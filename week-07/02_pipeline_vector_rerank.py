"""
Week 7 Day 3 — Pipeline B: Vector search + Voyage rerank.

Compare vs Week 6 baseline (vector-only, 93.3% hit@1).

Flow:
1. Query → Voyage embed (query mode)
2. pgvector top-20 CHUNKS (broader net for rerank)
3. Extract unique docs from chunks, keep best chunk per doc
4. Voyage rerank-2 on top-20 chunks
5. Deduplicate reranked chunks → top-5 docs
"""
from __future__ import annotations
import json
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import psycopg
import voyageai
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "week-06"))
from golden_dataset import GOLDEN_QUESTIONS
from rerank import rerank_candidates

load_dotenv()
vo = voyageai.Client()

DB_DSN = "postgresql://dev:dev@localhost:5432/ai_curriculum"
STRATEGY = "week6_fixed"  # Use best chunker from Week 6
VECTOR_TOP_K = 20         # Wider pool for rerank
FINAL_TOP_K = 5


@dataclass
class PipelineResult:
    question_id: str
    query: str
    vector_top5_docs: list[str]      # Doc IDs from vector-only ranking
    reranked_top5_docs: list[str]    # Doc IDs after rerank
    ground_truth: list[str]
    vector_hit_at_1: bool
    reranked_hit_at_1: bool
    vector_recall_at_5: bool
    reranked_recall_at_5: bool
    vector_mrr: float
    reranked_mrr: float
    latency_vector: float
    latency_rerank: float
    tokens_rerank: int
    cost_rerank: float


def vector_search_chunks(conn, query: str, top_k: int) -> list[dict]:
    """Return top-K CHUNKS (not docs) — pre-rerank pool."""
    start = time.time()
    r = vo.embed([query], model="voyage-3-large", input_type="query")
    q_emb = np.array(r.embeddings[0])
    
    sql = """
        SELECT
            id,
            metadata->>'doc_id' AS doc_id,
            content,
            1 - (embedding <=> %s) AS similarity
        FROM documents
        WHERE source = %s
        ORDER BY embedding <=> %s
        LIMIT %s
    """
    with conn.cursor() as cur:
        cur.execute(sql, (q_emb, STRATEGY, q_emb, top_k))
        rows = cur.fetchall()
    
    latency = time.time() - start
    
    chunks = [
        {"chunk_id": r[0], "doc_id": r[1], "content": r[2], "similarity": float(r[3])}
        for r in rows
    ]
    return chunks, latency


def dedupe_to_docs(items: list[dict], score_key: str, top_k: int) -> list[str]:
    """Collapse chunks → unique docs, keep best score per doc."""
    best: dict[str, float] = {}
    for item in items:
        d = item["doc_id"]
        s = item[score_key]
        if d not in best or s > best[d]:
            best[d] = s
    ranked = sorted(best.items(), key=lambda x: x[1], reverse=True)
    return [d for d, _ in ranked[:top_k]]


def calculate_metrics(retrieved_docs: list[str], ground_truth: list[str]) -> tuple[bool, bool, float]:
    """Return (hit@1, recall@5, MRR)."""
    truth = set(ground_truth)
    hit_1 = retrieved_docs[0] in truth if retrieved_docs else False
    recall_5 = any(d in truth for d in retrieved_docs)
    mrr = 0.0
    for rank, d in enumerate(retrieved_docs, 1):
        if d in truth:
            mrr = 1.0 / rank
            break
    return hit_1, recall_5, mrr


def evaluate_question(conn, question) -> PipelineResult:
    # 1. Vector search top-20 chunks
    chunks, latency_vec = vector_search_chunks(conn, question.query, VECTOR_TOP_K)
    
    # 2. Vector-only baseline: dedupe chunks → docs
    vector_docs = dedupe_to_docs(chunks, "similarity", FINAL_TOP_K)
    
    # 3. Rerank all 20 chunks
    candidates = [
        {"doc_id": c["doc_id"], "content": c["content"], "similarity": c["similarity"]}
        for c in chunks
    ]
    reranked, rerank_stats = rerank_candidates(
        query=question.query,
        candidates=candidates,
        top_k=VECTOR_TOP_K,  # Get all back to allow proper dedup
    )
    
    # 4. Dedupe reranked chunks → docs
    reranked_items = [
        {"doc_id": r.doc_id, "score": r.rerank_score}
        for r in reranked
    ]
    reranked_docs = dedupe_to_docs(reranked_items, "score", FINAL_TOP_K)
    
    # 5. Compute metrics for both
    v_hit, v_recall, v_mrr = calculate_metrics(vector_docs, question.ground_truth_doc_ids)
    r_hit, r_recall, r_mrr = calculate_metrics(reranked_docs, question.ground_truth_doc_ids)
    
    return PipelineResult(
        question_id=question.id,
        query=question.query,
        vector_top5_docs=vector_docs,
        reranked_top5_docs=reranked_docs,
        ground_truth=question.ground_truth_doc_ids,
        vector_hit_at_1=v_hit,
        reranked_hit_at_1=r_hit,
        vector_recall_at_5=v_recall,
        reranked_recall_at_5=r_recall,
        vector_mrr=v_mrr,
        reranked_mrr=r_mrr,
        latency_vector=latency_vec,
        latency_rerank=rerank_stats["latency"],
        tokens_rerank=rerank_stats["tokens"],
        cost_rerank=rerank_stats["cost_usd"],
    )


def main():
    results: list[PipelineResult] = []
    
    with psycopg.connect(DB_DSN) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SET hnsw.ef_search = 100")
        
        print(f"\n{'=' * 78}")
        print(f"  Pipeline B: Vector (top-{VECTOR_TOP_K}) + Voyage rerank-2 → top-{FINAL_TOP_K}")
        print('=' * 78)
        
        for q in GOLDEN_QUESTIONS:
            r = evaluate_question(conn, q)
            results.append(r)
            
            v_mark = "✓" if r.vector_hit_at_1 else "✗"
            rer_mark = "✓" if r.reranked_hit_at_1 else "✗"
            change = ""
            if r.reranked_hit_at_1 and not r.vector_hit_at_1:
                change = "  🔺 FIXED"
            elif not r.reranked_hit_at_1 and r.vector_hit_at_1:
                change = "  🔻 REGRESSION"
            
            print(f"  [{q.id}] vec={v_mark} rer={rer_mark}  {q.query[:50]}{change}")
    
    # === Aggregate ===
    n = len(results)
    v_hit = sum(r.vector_hit_at_1 for r in results) / n
    r_hit = sum(r.reranked_hit_at_1 for r in results) / n
    v_recall = sum(r.vector_recall_at_5 for r in results) / n
    r_recall = sum(r.reranked_recall_at_5 for r in results) / n
    v_mrr = sum(r.vector_mrr for r in results) / n
    r_mrr = sum(r.reranked_mrr for r in results) / n
    
    avg_lat_v = sum(r.latency_vector for r in results) / n
    avg_lat_r = sum(r.latency_rerank for r in results) / n
    total_cost = sum(r.cost_rerank for r in results)
    
    print(f"\n{'=' * 78}")
    print(f"  Aggregate metrics")
    print('=' * 78)
    print(f"{'Metric':<20} {'Vector-only':>14} {'+ Rerank':>14} {'Δ':>10}")
    print(f"{'hit@1':<20} {v_hit:>13.1%} {r_hit:>13.1%} {(r_hit-v_hit)*100:>+9.1f}pp")
    print(f"{'recall@5':<20} {v_recall:>13.1%} {r_recall:>13.1%} {(r_recall-v_recall)*100:>+9.1f}pp")
    print(f"{'MRR':<20} {v_mrr:>14.3f} {r_mrr:>14.3f} {r_mrr-v_mrr:>+10.3f}")
    print(f"\nLatency:  vector={avg_lat_v:.2f}s  rerank={avg_lat_r:.2f}s  total={avg_lat_v+avg_lat_r:.2f}s")
    print(f"Rerank total cost: ${total_cost:.4f} for {n} queries (${total_cost/n:.6f}/query)")
    
    # Save
    output = Path(__file__).parent / "pipeline_b_results.json"
    output.write_text(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
    print(f"\nResults saved → {output}")


if __name__ == "__main__":
    main()
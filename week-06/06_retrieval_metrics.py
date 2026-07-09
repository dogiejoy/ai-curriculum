"""
Week 6 Block 2 — Compare 4 chunking strategies via retrieval metrics.

Metrics:
- hit@1: correct doc appears in top-1 (strict)
- recall@5: correct doc appears in top-5 (typical RAG)
- MRR: 1 / rank of first correct doc (0 if not in top-K)
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
from golden_dataset import GOLDEN_QUESTIONS, GoldenQuestion

load_dotenv()
vo = voyageai.Client()

DB_DSN = "postgresql://dev:dev@localhost:5432/ai_curriculum"
TOP_K = 5
STRATEGIES = ["fixed", "recursive", "structural", "semantic"]


@dataclass
class RetrievalResult:
    question_id: str
    strategy: str
    retrieved_doc_ids: list[str]      # In rank order — top K unique docs
    ground_truth_doc_ids: list[str]
    hit_at_1: bool
    recall_at_5: bool
    reciprocal_rank: float             # 0 if not in top-K
    top_5_similarities: list[float]
    latency_seconds: float


def embed_query(text: str) -> np.ndarray:
    """Voyage query embedding (asymmetric input_type)."""
    r = vo.embed([text], model="voyage-3-large", input_type="query")
    return np.array(r.embeddings[0])


def search_strategy(
    conn: psycopg.Connection,
    query_emb: np.ndarray,
    strategy: str,
    top_k: int = TOP_K,
) -> list[tuple[str, float]]:
    """
    Return list of (doc_id, similarity) sorted by relevance.
    
    Fetches more raw chunks (top_k * 5) then deduplicates to top_k unique docs.
    Multiple chunks from same doc collapse to that doc's best chunk score.
    """
    source = f"week6_{strategy}"
    # Fetch 5× more to compensate for chunk-to-doc dedup
    raw_k = top_k * 5
    
    sql = """
        SELECT
            metadata->>'doc_id' AS doc_id,
            1 - (embedding <=> %s) AS similarity
        FROM documents
        WHERE source = %s
        ORDER BY embedding <=> %s
        LIMIT %s
    """
    
    with conn.cursor() as cur:
        cur.execute(sql, (query_emb, source, query_emb, raw_k))
        rows = cur.fetchall()
    
    # Dedupe: keep best similarity per doc
    doc_best: dict[str, float] = {}
    for doc_id, sim in rows:
        if doc_id not in doc_best or sim > doc_best[doc_id]:
            doc_best[doc_id] = float(sim)
    
    # Sort docs by best similarity, take top_k
    ranked = sorted(doc_best.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def evaluate_question(
    conn: psycopg.Connection,
    question: GoldenQuestion,
    strategy: str,
) -> RetrievalResult:
    start = time.time()
    query_emb = embed_query(question.query)
    ranked = search_strategy(conn, query_emb, strategy)
    latency = time.time() - start
    
    retrieved_ids = [d for d, _ in ranked]
    similarities = [s for _, s in ranked]
    
    truth = set(question.ground_truth_doc_ids)
    hit_at_1 = retrieved_ids[0] in truth if retrieved_ids else False
    recall_at_5 = any(d in truth for d in retrieved_ids)
    
    # Reciprocal rank: 1 / (position of first correct)
    reciprocal_rank = 0.0
    for i, d in enumerate(retrieved_ids, start=1):
        if d in truth:
            reciprocal_rank = 1.0 / i
            break
    
    return RetrievalResult(
        question_id=question.id,
        strategy=strategy,
        retrieved_doc_ids=retrieved_ids,
        ground_truth_doc_ids=question.ground_truth_doc_ids,
        hit_at_1=hit_at_1,
        recall_at_5=recall_at_5,
        reciprocal_rank=reciprocal_rank,
        top_5_similarities=similarities,
        latency_seconds=latency,
    )


def main():
    all_results: list[RetrievalResult] = []
    
    with psycopg.connect(DB_DSN) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SET hnsw.ef_search = 100")
        
        for strategy in STRATEGIES:
            print(f"\n{'─' * 70}")
            print(f"  Running strategy: {strategy}")
            print('─' * 70)
            for q in GOLDEN_QUESTIONS:
                r = evaluate_question(conn, q, strategy)
                all_results.append(r)
                mark = "✓" if r.hit_at_1 else ("○" if r.recall_at_5 else "✗")
                print(f"  {mark} [{q.id}] {q.query[:50]:<50} → {r.retrieved_doc_ids[0]:<11} (rr={r.reciprocal_rank:.2f})")
    
    # ===== Aggregate metrics =====
    print(f"\n{'=' * 70}")
    print("  Aggregate metrics per strategy")
    print('=' * 70)
    print(f"{'Strategy':<12} {'hit@1':>8} {'recall@5':>10} {'MRR':>8} {'avg_lat':>10}")
    
    by_strategy: dict[str, list[RetrievalResult]] = defaultdict(list)
    for r in all_results:
        by_strategy[r.strategy].append(r)
    
    for strategy in STRATEGIES:
        rs = by_strategy[strategy]
        hit_1 = sum(r.hit_at_1 for r in rs) / len(rs)
        recall = sum(r.recall_at_5 for r in rs) / len(rs)
        mrr = sum(r.reciprocal_rank for r in rs) / len(rs)
        avg_lat = sum(r.latency_seconds for r in rs) / len(rs)
        print(f"{strategy:<12} {hit_1:>8.1%} {recall:>10.1%} {mrr:>8.3f} {avg_lat:>9.2f}s")
    
    # ===== By difficulty =====
    print(f"\n{'=' * 70}")
    print("  hit@1 by difficulty")
    print('=' * 70)
    header = f"{'Strategy':<12}"
    for diff in ["easy", "medium", "hard"]:
        header += f" {diff:>8}"
    print(header)
    
    for strategy in STRATEGIES:
        line = f"{strategy:<12}"
        for diff in ["easy", "medium", "hard"]:
            filtered = [r for r in by_strategy[strategy]
                        if next(q for q in GOLDEN_QUESTIONS if q.id == r.question_id).difficulty == diff]
            if filtered:
                score = sum(r.hit_at_1 for r in filtered) / len(filtered)
                line += f" {score:>7.0%}"
            else:
                line += f" {'—':>8}"
        print(line)
    
    # ===== Save raw results =====
    output_path = Path(__file__).parent / "retrieval_results.json"
    output_path.write_text(
        json.dumps([asdict(r) for r in all_results], ensure_ascii=False, indent=2)
    )
    print(f"\n  Raw results saved → {output_path}")


if __name__ == "__main__":
    main()
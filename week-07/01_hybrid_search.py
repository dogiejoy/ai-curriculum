"""
Week 7 Day 1 — Hybrid Search: Vector + BM25 fused via RRF.

Language-aware: BM25 mostly helps English/codes/numbers.
Thai queries → BM25 contributes minimal but doesn't hurt (fusion neutral).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Literal

import numpy as np
import psycopg
import voyageai
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()
vo = voyageai.Client()

DB_DSN = "postgresql://dev:dev@localhost:5432/ai_curriculum"


# ===== Query language detection =====

def detect_query_type(query: str) -> Literal["thai_heavy", "english_heavy", "mixed"]:
    """Character-based heuristic. Thai unicode range U+0E00-U+0E7F."""
    thai_chars = sum(1 for c in query if '\u0e00' <= c <= '\u0e7f')
    non_ws = sum(1 for c in query if not c.isspace())
    if non_ws == 0:
        return "mixed"
    thai_ratio = thai_chars / non_ws
    if thai_ratio > 0.7:
        return "thai_heavy"
    if thai_ratio < 0.2:
        return "english_heavy"
    return "mixed"


# English stopwords (common words that dilute BM25 signal)
EN_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "how", "in", "is", "it", "of", "on", "or", "that",
    "the", "this", "to", "was", "were", "what", "when", "where",
    "which", "who", "why", "with", "will", "you", "your",
}

# Thai stopwords + short particles that split from morphology
TH_STOPWORDS = {
    "และ", "ของ", "ที่", "ใน", "จะ", "ให้", "ได้", "เป็น", "ไม่",
    "การ", "ต้อง", "หรือ", "เมื่อ", "กับ", "ยัง", "นี้", "นั้น",
}


def build_tsquery(query: str, operator: str = "&") -> str:
    """Extract keywords → tsquery with AND (default) or OR fusion.
    
    Args:
        operator: '&' (AND, precision) or '|' (OR, recall)
    """
    tokens = re.findall(r'[\w-]+', query)
    # Filter: min length 3, exclude stopwords (case-insensitive)
    tokens = [
        t for t in tokens
        if len(t) >= 3
        and t.lower() not in EN_STOPWORDS
        and t not in TH_STOPWORDS
    ]
    if not tokens:
        return ""
    return f" {operator} ".join(tokens)


def build_tsquery_hybrid_or_and(query: str) -> tuple[str, str]:
    """Return (or_query, and_query) — try both, pick best downstream."""
    return build_tsquery(query, "|"), build_tsquery(query, "&")

# ===== Individual searches =====

def vector_search(conn, query: str, source: str, top_k: int = 20) -> list[tuple[str, float]]:
    """Return [(doc_id, similarity)] ranked by cosine similarity."""
    r = vo.embed([query], model="voyage-3-large", input_type="query")
    query_emb = np.array(r.embeddings[0])
    
    sql = """
        SELECT metadata->>'doc_id' AS doc_id,
               1 - (embedding <=> %s) AS similarity
        FROM documents
        WHERE source = %s
        ORDER BY embedding <=> %s
        LIMIT %s
    """
    with conn.cursor() as cur:
        cur.execute(sql, (query_emb, source, query_emb, top_k * 5))  # chunk overhead
        rows = cur.fetchall()
    
    # Dedupe to best per doc
    best: dict[str, float] = {}
    for doc_id, sim in rows:
        if doc_id not in best or sim > best[doc_id]:
            best[doc_id] = float(sim)
    return sorted(best.items(), key=lambda x: x[1], reverse=True)[:top_k]


def bm25_search(conn, query: str, source: str, top_k: int = 20) -> list[tuple[str, float]]:
    """Return [(doc_id, bm25_score)] — try AND first (precision), OR fallback (recall)."""
    or_q, and_q = build_tsquery_hybrid_or_and(query)
    
    # Try AND first — strict, high precision
    for tsq in [and_q, or_q]:
        if not tsq:
            continue
        sql = """
            SELECT metadata->>'doc_id' AS doc_id,
                   ts_rank_cd(content_tsvector, q) AS score
            FROM documents,
                 to_tsquery('simple', %s) q
            WHERE content_tsvector @@ q AND source = %s
            ORDER BY score DESC
            LIMIT %s
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (tsq, source, top_k * 5))
                rows = cur.fetchall()
        except psycopg.errors.SyntaxError:
            continue
        
        if rows:
            best: dict[str, float] = {}
            for doc_id, score in rows:
                if doc_id not in best or score > best[doc_id]:
                    best[doc_id] = float(score)
            return sorted(best.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    return []

# ===== RRF Fusion =====

def reciprocal_rank_fusion(
    rank_lists: list[list[tuple[str, float]]],
    k: int = 60,
    top_k: int = 5,
) -> list[tuple[str, float]]:
    """Fuse multiple rank lists into single ranking.
    
    score(doc) = Σ 1 / (k + rank_in_list_i)
    """
    scores: dict[str, float] = {}
    for rank_list in rank_lists:
        for rank_1_indexed, (doc_id, _) in enumerate(rank_list, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank_1_indexed)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]


# ===== Hybrid search =====

BM25_MIN_SCORE = 0.2   # Filter noise below this threshold


def hybrid_search(conn, query: str, source: str, top_k: int = 5) -> dict:
    """Vector + BM25 (thresholded) → RRF fusion."""
    vec = vector_search(conn, query, source, top_k=20)
    bm25 = bm25_search(conn, query, source, top_k=20)
    
    # Filter BM25 by min score — skip noisy contributions
    bm25_filtered = [(d, s) for d, s in bm25 if s >= BM25_MIN_SCORE]
    
    fused = reciprocal_rank_fusion([vec, bm25_filtered], k=60, top_k=top_k)
    
    return {
        "query": query,
        "query_type": detect_query_type(query),
        "tsquery": build_tsquery(query, "&"),
        "vector_top5": vec[:5],
        "bm25_top5_raw": bm25[:5],
        "bm25_top5_filtered": bm25_filtered[:5],
        "fused_top5": fused,
    }

# ===== CLI test =====

def _print_ranking(label: str, ranking: list[tuple[str, float]]) -> None:
    print(f"  {label}:")
    if not ranking:
        print(f"    (empty)")
        return
    for i, (doc_id, score) in enumerate(ranking, 1):
        print(f"    {i}. [{score:.4f}] {doc_id}")


def main():
    test_queries = [
        "NexGard Spectra สำหรับสุนัขน้ำหนักเท่าไหร่",     # Q01 baseline
        "ยาแก้ปวดสำหรับสุนัข ไม่ใช่ steroid",              # Q06 canary — the hard one
        "SOP for temperature excursion incident reporting", # Q15 English SOP
    ]
    
    with psycopg.connect(DB_DSN) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SET hnsw.ef_search = 100")
        
        for q in test_queries:
            print(f"\n{'=' * 70}")
            print(f"Q: {q}")
            print('=' * 70)
            result = hybrid_search(conn, q, source="week6_fixed", top_k=5)
            print(f"  Query type: {result['query_type']}")
            print(f"  tsquery: {result['tsquery']!r}")
            print()
            #_print_ranking("Vector top-5", result['vector_top5'])
            #_print_ranking("BM25 top-5", result['bm25_top5'])
            #_print_ranking("Fused (RRF) top-5", result['fused_top5'])
            _print_ranking("BM25 raw", result['bm25_top5_raw'])
            _print_ranking("BM25 filtered (≥0.2)", result['bm25_top5_filtered'])
            _print_ranking("Fused (RRF)", result['fused_top5'])

if __name__ == "__main__":
    main()
"""
Voyage rerank-2 client wrapper + candidate handling.
"""
from __future__ import annotations
import time
from dataclasses import dataclass

import voyageai
from dotenv import load_dotenv

load_dotenv()
vo = voyageai.Client()


@dataclass
class RerankedCandidate:
    """A candidate after reranking."""
    doc_id: str
    content: str
    original_rank: int          # position in input list (0-indexed)
    rerank_score: float          # 0-1, higher is better
    original_similarity: float   # from vector search


def rerank_candidates(
    query: str,
    candidates: list[dict],       # [{doc_id, content, similarity}]
    top_k: int = 5,
    model: str = "rerank-2",
) -> tuple[list[RerankedCandidate], dict]:
    """
    Rerank candidates using Voyage cross-encoder.
    
    Returns (reranked_list, stats).
    stats = {tokens, latency, cost_usd}
    """
    if not candidates:
        return [], {"tokens": 0, "latency": 0.0, "cost_usd": 0.0}
    
    documents = [c["content"] for c in candidates]
    
    start = time.time()
    result = vo.rerank(
        query=query,
        documents=documents,
        model=model,
        top_k=top_k,
    )
    latency = time.time() - start
    
    reranked = []
    for r in result.results:
        original = candidates[r.index]
        reranked.append(RerankedCandidate(
            doc_id=original["doc_id"],
            content=original["content"],
            original_rank=r.index,
            rerank_score=float(r.relevance_score),
            original_similarity=original["similarity"],
        ))
    
    # Voyage cost: $0.05/1M tokens for rerank-2
    tokens = result.total_tokens
    cost = (tokens / 1_000_000) * 0.05
    
    return reranked, {
        "tokens": tokens,
        "latency": latency,
        "cost_usd": cost,
    }
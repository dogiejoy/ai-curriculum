"""
Week 5 Day 1 Block 3 — Compare embedding models on identical corpus.
Measure: quality (ranking), cost, latency.
"""
import time
import numpy as np
import openai
import voyageai
from dotenv import load_dotenv

load_dotenv()
vo = voyageai.Client()
oai = openai.OpenAI()


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Pricing (USD per 1M tokens) — verified June 2026
PRICING = {
    "voyage-3-large": 0.18,
    "voyage-3-lite":  0.02,
    "text-embedding-3-large": 0.13,
    "text-embedding-3-small": 0.02,
}


# Test corpus — vet warehouse domain (Depot RTB context)
DOCUMENTS = [
    "Frontline Plus ยาฆ่าเห็บหมัดสำหรับสุนัข ใช้แบบหยอดหลังคอ ป้องกัน 1 เดือน",
    "Bravecto chewable tablet สำหรับสุนัข กินครั้งเดียวป้องกันเห็บได้ 12 สัปดาห์",
    "Royal Canin Adult Cat อาหารแมวโตเต็มวัย รสไก่ ขนาด 4 กก.",
    "Drontal Plus ยาถ่ายพยาธิรวมในสุนัข ครอบคลุมพยาธิตัวกลม ตัวตืด พยาธิหัวใจ",
    "Otibact ยาหยอดหูสำหรับสุนัข แก้อักเสบและติดเชื้อแบคทีเรีย",
    "Frontline Spray สเปรย์ฆ่าเห็บหมัดและไรในสุนัข ใช้พ่นทั่วตัว",
    "Hill's Science Diet Puppy อาหารลูกสุนัข อายุต่ำกว่า 1 ปี",
    "Bravecto Plus combine flea tick and heartworm prevention",
]


QUERIES = [
    "ยาป้องกันเห็บหมัดสำหรับหมา",       # → expect: Frontline Plus, Bravecto, Frontline Spray
    "อาหารแมว",                          # → expect: Royal Canin
    "heartworm prevention",              # → expect: Drontal (mentions พยาธิหัวใจ), Bravecto Plus
    "ear infection treatment",           # → expect: Otibact
]


# ===== Embedding functions =====

def embed_voyage(texts: list[str], model: str, input_type: str) -> tuple[list[np.ndarray], int, float]:
    """Returns (embeddings, total_tokens, latency)."""
    start = time.time()
    r = vo.embed(texts, model=model, input_type=input_type)
    return [np.array(e) for e in r.embeddings], r.total_tokens, time.time() - start


def embed_openai(texts: list[str], model: str) -> tuple[list[np.ndarray], int, float]:
    """OpenAI doesn't have asymmetric input_type."""
    start = time.time()
    r = oai.embeddings.create(input=texts, model=model)
    embs = [np.array(d.embedding) for d in r.data]
    return embs, r.usage.total_tokens, time.time() - start


# ===== Evaluation =====

def evaluate_model(
    label: str,
    embed_docs_fn,
    embed_queries_fn,
    cost_per_million: float,
):
    print(f"\n{'=' * 75}")
    print(f"  {label}")
    print('=' * 75)

    # Embed corpus
    doc_embs, doc_tokens, doc_latency = embed_docs_fn(DOCUMENTS)
    
    # Embed queries
    query_embs, query_tokens, query_latency = embed_queries_fn(QUERIES)

    total_tokens = doc_tokens + query_tokens
    total_cost = (total_tokens / 1_000_000) * cost_per_million

    print(f"Tokens: docs={doc_tokens}, queries={query_tokens}, total={total_tokens}")
    print(f"Cost: ${total_cost:.6f}")
    print(f"Latency: docs={doc_latency:.2f}s, queries={query_latency:.2f}s")

    # For each query, rank all documents
    print(f"\n{'─' * 75}")
    print("Top-3 retrievals per query:")
    print('─' * 75)

    for q_idx, query in enumerate(QUERIES):
        sims = [
            (i, cosine_sim(query_embs[q_idx], doc_embs[i]))
            for i in range(len(DOCUMENTS))
        ]
        sims.sort(key=lambda x: x[1], reverse=True)

        print(f"\nQ: {query}")
        for rank, (doc_idx, sim) in enumerate(sims[:3], 1):
            doc_short = DOCUMENTS[doc_idx][:60] + "…" if len(DOCUMENTS[doc_idx]) > 60 else DOCUMENTS[doc_idx]
            print(f"  {rank}. [{sim:+.3f}] {doc_short}")


def main():
    # ===== Voyage 3 Large =====
    evaluate_model(
        "Voyage 3 Large (1024 dim, $0.18/1M)",
        embed_docs_fn=lambda t: embed_voyage(t, "voyage-3-large", "document"),
        embed_queries_fn=lambda t: embed_voyage(t, "voyage-3-large", "query"),
        cost_per_million=PRICING["voyage-3-large"],
    )

    # ===== Voyage 3 Lite =====
    evaluate_model(
        "Voyage 3 Lite (512 dim, $0.02/1M — 9x cheaper)",
        embed_docs_fn=lambda t: embed_voyage(t, "voyage-3-lite", "document"),
        embed_queries_fn=lambda t: embed_voyage(t, "voyage-3-lite", "query"),
        cost_per_million=PRICING["voyage-3-lite"],
    )

    # ===== OpenAI Large =====
    evaluate_model(
        "OpenAI text-embedding-3-large (3072 dim, $0.13/1M)",
        embed_docs_fn=lambda t: embed_openai(t, "text-embedding-3-large"),
        embed_queries_fn=lambda t: embed_openai(t, "text-embedding-3-large"),
        cost_per_million=PRICING["text-embedding-3-large"],
    )

    # ===== OpenAI Small =====
    evaluate_model(
        "OpenAI text-embedding-3-small (1536 dim, $0.02/1M)",
        embed_docs_fn=lambda t: embed_openai(t, "text-embedding-3-small"),
        embed_queries_fn=lambda t: embed_openai(t, "text-embedding-3-small"),
        cost_per_million=PRICING["text-embedding-3-small"],
    )


if __name__ == "__main__":
    main()
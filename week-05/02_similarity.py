"""
Week 5 Day 1 — Compute cosine similarity across multiple texts.
Shows how embeddings cluster semantically similar items.
"""
import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()
vo = voyageai.Client()


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity. Vectors don't need to be normalized — handled here."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Mix Thai + English + topical categories
TEXTS = [
    # Vet meds (Thai)
    "Frontline Plus เป็นยาฆ่าเห็บหมัดสำหรับสุนัข",
    "Bravecto กินครั้งเดียวป้องกันเห็บได้ 3 เดือน",
    "Royal Canin Adult Cat อาหารแมวพันธุ์โต",

    # Vet meds (English equivalents)
    "Frontline Plus is a flea and tick treatment for dogs",
    "Bravecto chewable tablet protects against ticks for 3 months",
    "Royal Canin Adult Cat food for adult cats",

    # Unrelated topics
    "Laravel เป็น PHP framework สำหรับสร้างเว็บแอป",
    "Bangkok weather is hot and humid today",
    "Photosynthesis converts sunlight into chemical energy",
]


def main():
    # Batch embed all texts in one API call (cheaper + faster)
    result = vo.embed(
        TEXTS,
        model="voyage-3-large",#voyage-multilingual-3
        input_type="document",
    )
    embeddings = [np.array(e) for e in result.embeddings]

    print(f"Embedded {len(TEXTS)} texts using {result.total_tokens} tokens\n")

    # Compute pairwise similarity matrix
    n = len(TEXTS)
    print(f"{'':<60}", end="")
    for j in range(n):
        print(f"  T{j}  ", end="")
    print()

    for i in range(n):
        short = TEXTS[i][:55] + "…" if len(TEXTS[i]) > 55 else TEXTS[i]
        print(f"T{i}: {short:<56}", end="")
        for j in range(n):
            sim = cosine_sim(embeddings[i], embeddings[j])
            print(f" {sim:+.2f}", end="")
        print()


if __name__ == "__main__":
    main()
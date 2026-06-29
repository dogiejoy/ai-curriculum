"""
Week 5 Day 1 — First embedding call + inspect vector.
"""
import os
import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()
vo = voyageai.Client()  # auto-reads VOYAGE_API_KEY


def main():
    text = "Frontline Plus เป็นยาฆ่าเห็บสำหรับสุนัข"

    result = vo.embed(
        [text],
        model="voyage-3-large",
        input_type="document",
    )

    embedding = np.array(result.embeddings[0])

    print(f"Input text: {text}")
    print(f"Embedding dim: {embedding.shape[0]}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Last 5 values: {embedding[-5:]}")
    print(f"Magnitude (L2 norm): {np.linalg.norm(embedding):.6f}")
    print(f"Total tokens used: {result.total_tokens}")


if __name__ == "__main__":
    main()
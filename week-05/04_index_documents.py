"""
Week 5 Day 2/3 combined — Index documents into pgvector.
"""
import os
from typing import Any

import numpy as np
import psycopg
import voyageai
from dotenv import load_dotenv
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector

load_dotenv()
vo = voyageai.Client()

DB_DSN = "postgresql://dev:dev@localhost:5432/ai_curriculum"

EMBEDDING_MODEL = "voyage-3-large"


# ===== Corpus (same as Block 3 comparison — reuse for consistency) =====

DOCUMENTS = [
    {"content": "Frontline Plus ยาฆ่าเห็บหมัดสำหรับสุนัข ใช้แบบหยอดหลังคอ ป้องกัน 1 เดือน",
     "metadata": {"category": "parasite_control", "species": "dog", "brand": "Frontline"}},
    {"content": "Bravecto chewable tablet สำหรับสุนัข กินครั้งเดียวป้องกันเห็บได้ 12 สัปดาห์",
     "metadata": {"category": "parasite_control", "species": "dog", "brand": "Bravecto"}},
    {"content": "Royal Canin Adult Cat อาหารแมวโตเต็มวัย รสไก่ ขนาด 4 กก.",
     "metadata": {"category": "food", "species": "cat", "brand": "Royal Canin"}},
    {"content": "Drontal Plus ยาถ่ายพยาธิรวมในสุนัข ครอบคลุมพยาธิตัวกลม ตัวตืด พยาธิหัวใจ",
     "metadata": {"category": "parasite_control", "species": "dog", "brand": "Drontal"}},
    {"content": "Otibact ยาหยอดหูสำหรับสุนัข แก้อักเสบและติดเชื้อแบคทีเรีย",
     "metadata": {"category": "medication", "species": "dog", "brand": "Otibact"}},
    {"content": "Frontline Spray สเปรย์ฆ่าเห็บหมัดและไรในสุนัข ใช้พ่นทั่วตัว",
     "metadata": {"category": "parasite_control", "species": "dog", "brand": "Frontline"}},
    {"content": "Hill's Science Diet Puppy อาหารลูกสุนัข อายุต่ำกว่า 1 ปี",
     "metadata": {"category": "food", "species": "dog", "brand": "Hill's"}},
    {"content": "Bravecto Plus combine flea tick and heartworm prevention",
     "metadata": {"category": "parasite_control", "species": "dog", "brand": "Bravecto"}},
]


def embed_documents(texts: list[str]) -> tuple[list[np.ndarray], int]:
    """Batch embed with input_type=document."""
    r = vo.embed(texts, model=EMBEDDING_MODEL, input_type="document")
    return [np.array(e) for e in r.embeddings], r.total_tokens


def clear_documents(conn: psycopg.Connection) -> None:
    """Wipe table before re-indexing (idempotent runs)."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE documents RESTART IDENTITY")
    conn.commit()


def insert_documents(
    conn: psycopg.Connection,
    docs: list[dict[str, Any]],
    embeddings: list[np.ndarray],
    source: str = "day1_corpus",
) -> None:
    """Bulk insert (production: use COPY for >1000 rows)."""
    with conn.cursor() as cur:
        for doc, emb in zip(docs, embeddings):
            cur.execute(
                """
                INSERT INTO documents (source, content, metadata, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (source, doc["content"], psycopg.types.json.Json(doc["metadata"]), emb),
            )
    conn.commit()


def main():
    print(f"Indexing {len(DOCUMENTS)} documents...")
    
    texts = [d["content"] for d in DOCUMENTS]
    embeddings, tokens = embed_documents(texts)
    print(f"Embeddings created: {len(embeddings)} × {embeddings[0].shape[0]} dim")
    print(f"Tokens used: {tokens}")
    
    with psycopg.connect(DB_DSN, row_factory=dict_row) as conn:
        register_vector(conn)  # register pgvector type adapter
        
        clear_documents(conn)
        insert_documents(conn, DOCUMENTS, embeddings)
        
        # Verify
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM documents")
            row = cur.fetchone()
            print(f"\n✓ Inserted {row['n']} documents into pgvector")


if __name__ == "__main__":
    main()
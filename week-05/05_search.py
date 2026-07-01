"""
Week 5 Day 2/3 — Similarity search over pgvector.
Uses HNSW index + cosine distance operator (<=>).
"""
from psycopg.types.json import Jsonb   # ← Jsonb ไม่ใช่ Json
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


def embed_query(text: str) -> np.ndarray:
    """Note: input_type='query' — asymmetric encoding matters."""
    r = vo.embed([text], model=EMBEDDING_MODEL, input_type="query")
    return np.array(r.embeddings[0])


def search(
    conn: psycopg.Connection,
    query_text: str,
    top_k: int = 3,
    filter_metadata: dict | None = None,
) -> list[dict]:
    """
    Similarity search with optional metadata filter.
    
    Returns rows sorted by cosine similarity (best first).
    Note: pgvector <=> returns cosine DISTANCE (0=same, 2=opposite)
          → similarity = 1 - distance
    """
    query_emb = embed_query(query_text)
    
    sql = """
        SELECT
            id,
            content,
            metadata,
            1 - (embedding <=> %s) AS similarity
        FROM documents
    """
    params: list = [query_emb]
    
    # Optional metadata filter (JSONB @>)
    if filter_metadata:
        sql += " WHERE metadata @> %s"
        params.append(Jsonb(filter_metadata))#params.append(psycopg.types.json.Json(filter_metadata))
    
    sql += " ORDER BY embedding <=> %s LIMIT %s"
    params.extend([query_emb, top_k])
    
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def main():
    with psycopg.connect(DB_DSN, row_factory=dict_row) as conn:
        register_vector(conn)
        
        # Optional: tune ef_search per query (higher = more accurate, slower)
        with conn.cursor() as cur:
            cur.execute("SET hnsw.ef_search = 100")
        
        # ===== Same queries as Day 1 Block 3 =====
        queries = [
            "ยาป้องกันเห็บหมัดสำหรับหมา",
            "อาหารแมว",
            "heartworm prevention",
            "ear infection treatment",
        ]
        
        for q in queries:
            print(f"\n{'=' * 75}")
            print(f"Q: {q}")
            print('=' * 75)
            results = search(conn, q, top_k=3)
            for i, r in enumerate(results, 1):
                content_short = r["content"][:65] + "…" if len(r["content"]) > 65 else r["content"]
                print(f"  {i}. [{r['similarity']:+.3f}] {content_short}")
                print(f"     metadata: {r['metadata']}")
        
        # ===== Bonus: metadata filter demo =====
        print(f"\n{'=' * 75}")
        print(f"BONUS: 'อาหาร' filtered to species=cat only")
        print('=' * 75)
        results = search(
            conn,
            "อาหาร",
            top_k=3,
            filter_metadata={"species": "cat"},
        )
        for i, r in enumerate(results, 1):
            content_short = r["content"][:65] + "…" if len(r["content"]) > 65 else r["content"]
            print(f"  {i}. [{r['similarity']:+.3f}] {content_short}")


if __name__ == "__main__":
    main()
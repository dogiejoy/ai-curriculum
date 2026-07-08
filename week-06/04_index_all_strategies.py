"""
Index the corpus × 4 strategies into pgvector.
Each strategy gets its own `source` label for query-time comparison.
"""
import json
import sys
import time
from pathlib import Path

import psycopg
import voyageai
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

sys.path.insert(0, str(Path(__file__).parent / "chunkers"))
from multi_doc import CHUNKERS

load_dotenv()
vo = voyageai.Client()

DB_DSN = "postgresql://dev:dev@localhost:5432/ai_curriculum"
CORPUS_PATH = Path(__file__).parent / "corpus" / "depot_corpus.json"


def embed_batch(texts: list[str]) -> tuple[list[list[float]], int]:
    """Batch embed — 128 max per Voyage API call."""
    all_embeddings = []
    total_tokens = 0
    for i in range(0, len(texts), 128):
        batch = texts[i:i + 128]
        r = vo.embed(batch, model="voyage-3-large", input_type="document")
        all_embeddings.extend(r.embeddings)
        total_tokens += r.total_tokens
    return all_embeddings, total_tokens


def index_strategy(conn, docs: list[dict], strategy_name: str, chunker_fn):
    """Chunk + embed + insert."""
    print(f"\n{'─' * 65}")
    print(f"  Indexing strategy: {strategy_name}")
    print('─' * 65)
    
    # Chunk
    start = time.time()
    chunks = chunker_fn(docs)
    chunk_time = time.time() - start
    
    if not chunks:
        print(f"  ⚠️  No chunks produced")
        return
    
    # Embed
    start = time.time()
    texts = [c.content for c in chunks]
    embeddings, tokens = embed_batch(texts)
    embed_time = time.time() - start
    
    # Insert
    start = time.time()
    source = f"week6_{strategy_name}"
    with conn.cursor() as cur:
        for chunk, emb in zip(chunks, embeddings):
            cur.execute(
                """
                INSERT INTO documents (source, content, metadata, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (source, chunk.content, psycopg.types.json.Jsonb(chunk.metadata), emb),
            )
    conn.commit()
    insert_time = time.time() - start
    
    # Report
    sizes = [c.size for c in chunks]
    print(f"  Chunks: {len(chunks)}")
    print(f"  Size min/mean/max: {min(sizes)}/{sum(sizes)//len(sizes)}/{max(sizes)}")
    print(f"  Total tokens: {tokens} (${(tokens/1_000_000)*0.18:.4f})")
    print(f"  Chunk: {chunk_time:.2f}s | Embed: {embed_time:.2f}s | Insert: {insert_time:.2f}s")


def main():
    docs = json.loads(CORPUS_PATH.read_text())
    print(f"Loaded {len(docs)} documents from corpus")
    total_chars = sum(len(d["content"]) for d in docs)
    print(f"Total content: {total_chars:,} chars")
    
    with psycopg.connect(DB_DSN) as conn:
        register_vector(conn)
        
        # Clear previous week 6 runs
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE source LIKE 'week6_%'")
            print(f"\n  Cleared previous week6_* rows")
        conn.commit()
        
        # Index each strategy
        for strategy_name, chunker_fn in CHUNKERS.items():
            index_strategy(conn, docs, strategy_name, chunker_fn)
        
        # Final summary
        print(f"\n{'=' * 65}")
        print("  Final index counts")
        print('=' * 65)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source, COUNT(*) as n, 
                       AVG(LENGTH(content))::int as avg_size
                FROM documents 
                WHERE source LIKE 'week6_%' 
                GROUP BY source 
                ORDER BY source
            """)
            for row in cur.fetchall():
                print(f"  {row[0]:<25} {row[1]:>4} chunks  avg {row[2]} chars")


if __name__ == "__main__":
    main()
"""
Week 6 Day 1 Block 3 — Run all 4 strategies on same doc, compare metrics.
"""
import sys
import time
from pathlib import Path

import numpy as np
import voyageai
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "chunkers"))
from basic import Chunk, fixed_size_chunker, recursive_chunker
from advanced import structural_chunker, semantic_chunker

load_dotenv()
vo = voyageai.Client()


VOYAGE_COST_PER_M = 0.18   # voyage-3-large


def embed_chunks(chunks: list[Chunk]) -> tuple[list[np.ndarray], int, float]:
    """Batch embed. Returns (embeddings, tokens, latency)."""
    texts = [c.content for c in chunks]
    start = time.time()
    r = vo.embed(texts, model="voyage-3-large", input_type="document")
    return [np.array(e) for e in r.embeddings], r.total_tokens, time.time() - start


def analyze(name: str, chunks: list[Chunk], embeddings, tokens: int, latency: float):
    sizes = [c.size for c in chunks]
    n = len(chunks)
    
    print(f"\n{'=' * 75}")
    print(f"  {name}")
    print('=' * 75)
    print(f"  Chunks:         {n}")
    print(f"  Size min/mean/max: {min(sizes)} / {sum(sizes)//n} / {max(sizes)}")
    print(f"  Size stddev:    {np.std(sizes):.1f}")
    print(f"  Total content:  {sum(sizes):,} chars")
    print(f"  Tokens:         {tokens}")
    print(f"  Cost (this run):${(tokens / 1_000_000) * VOYAGE_COST_PER_M:.6f}")
    print(f"  Embed latency:  {latency:.2f}s")
    print(f"  Storage:        {n * 1024 * 4:,} bytes ({n} × 1024 dims × 4 bytes)")


def main():
    text = Path(__file__).parent.joinpath("corpus/depot_faq.md").read_text()
    print(f"Source document: {len(text)} chars")
    
    strategies = [
        ("Fixed (400/50)",     lambda: fixed_size_chunker(text, chunk_size=400, overlap=50)),
        ("Recursive (400/50)", lambda: recursive_chunker(text, chunk_size=400, overlap=50)),
        ("Structural (800 max)", lambda: structural_chunker(text, max_chunk_size=800)),
        ("Semantic (800 max)",   lambda: semantic_chunker(text, max_chunk_size=800)),
    ]
    
    all_results = []
    for name, fn in strategies:
        chunks = fn()
        embeddings, tokens, latency = embed_chunks(chunks)
        analyze(name, chunks, embeddings, tokens, latency)
        all_results.append((name, chunks, tokens))
    
    # ===== Summary =====
    print(f"\n{'=' * 75}")
    print("  Summary — projected cost for 1000 similar docs")
    print('=' * 75)
    for name, chunks, tokens in all_results:
        projected = (tokens * 1000 / 1_000_000) * VOYAGE_COST_PER_M
        storage_gb = (len(chunks) * 1000 * 1024 * 4) / (1024**3)
        print(f"  {name:<25} {len(chunks):>3} chunks  {tokens:>5} tokens  ${projected:>7.2f}  {storage_gb*1024:>6.1f} MB storage")


if __name__ == "__main__":
    main()
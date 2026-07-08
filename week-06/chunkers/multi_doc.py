"""
Multi-document chunking wrappers.
Each doc = dict with 'content' and 'metadata'.
Chunker returns flat list of Chunk objects with source doc metadata attached.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic import Chunk, fixed_size_chunker, recursive_chunker
from advanced import structural_chunker, semantic_chunker


def _annotate(chunks: list[Chunk], doc_id: str, doc_metadata: dict) -> list[Chunk]:
    """Merge document-level metadata into chunk metadata."""
    for c in chunks:
        c.metadata = {**doc_metadata, "doc_id": doc_id, **c.metadata}
    return chunks


def chunk_documents_fixed(docs: list[dict], chunk_size: int = 400, overlap: int = 50) -> list[Chunk]:
    all_chunks = []
    for doc in docs:
        chunks = fixed_size_chunker(doc["content"], chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(_annotate(chunks, doc["id"], doc.get("metadata", {})))
    return all_chunks


def chunk_documents_recursive(docs: list[dict], chunk_size: int = 400, overlap: int = 50) -> list[Chunk]:
    all_chunks = []
    for doc in docs:
        chunks = recursive_chunker(doc["content"], chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(_annotate(chunks, doc["id"], doc.get("metadata", {})))
    return all_chunks


def chunk_documents_structural(docs: list[dict], max_chunk_size: int = 800) -> list[Chunk]:
    all_chunks = []
    for doc in docs:
        chunks = structural_chunker(doc["content"], max_chunk_size=max_chunk_size)
        all_chunks.extend(_annotate(chunks, doc["id"], doc.get("metadata", {})))
    return all_chunks


def chunk_documents_semantic(docs: list[dict], max_chunk_size: int = 800, threshold: float = 0.7) -> list[Chunk]:
    all_chunks = []
    for doc in docs:
        chunks = semantic_chunker(doc["content"], max_chunk_size=max_chunk_size, similarity_threshold=threshold)
        all_chunks.extend(_annotate(chunks, doc["id"], doc.get("metadata", {})))
    return all_chunks


CHUNKERS = {
    "fixed": chunk_documents_fixed,
    "recursive": chunk_documents_recursive,
    "structural": chunk_documents_structural,
    "semantic": chunk_documents_semantic,
}


if __name__ == "__main__":
    # Smoke test with existing doc
    text = Path(__file__).parent.parent.joinpath("corpus/depot_faq.md").read_text()
    docs = [{
        "id": "faq_001",
        "content": text,
        "metadata": {"doc_type": "faq", "language": "th"},
    }]
    
    for name, fn in CHUNKERS.items():
        chunks = fn(docs)
        print(f"{name}: {len(chunks)} chunks, first has metadata: {chunks[0].metadata}")
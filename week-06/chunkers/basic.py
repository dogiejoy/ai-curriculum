"""
Chunking strategies: Fixed-size and Recursive.
No external chunking libraries — pure Python for transparency.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A single chunk with metadata about its source."""
    content: str
    strategy: str
    chunk_index: int
    char_start: int
    char_end: int
    metadata: dict = field(default_factory=dict)

    @property
    def size(self) -> int:
        return len(self.content)


def fixed_size_chunker(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """Baseline: split every N chars, overlap M chars.
    
    Naive — cuts words/sentences mid-way but predictable.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must exceed overlap")
    
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        content = text[start:end]
        chunks.append(Chunk(
            content=content,
            strategy="fixed",
            chunk_index=idx,
            char_start=start,
            char_end=end,
            metadata={"chunk_size": chunk_size, "overlap": overlap},
        ))
        idx += 1
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def recursive_chunker(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    separators: list[str] | None = None,
) -> list[Chunk]:
    """LangChain-style recursive split.
    
    Tries separators in order (largest semantic unit first).
    Falls back to next separator if chunk still too big.
    """
    if separators is None:
        # Order: paragraph → line → sentence-ish → word → char
        separators = ["\n\n", "\n", "。", ".", " ", ""]
    
    def _split(txt: str, seps: list[str]) -> list[str]:
        """Recursively split until pieces fit chunk_size."""
        if len(txt) <= chunk_size:
            return [txt]
        
        # Try current separator
        sep = seps[0]
        rest_seps = seps[1:] if len(seps) > 1 else [""]
        
        if sep == "":
            # Last resort — hard split by chunk_size
            return [txt[i:i + chunk_size] for i in range(0, len(txt), chunk_size)]
        
        parts = txt.split(sep)
        result = []
        for part in parts:
            if len(part) <= chunk_size:
                result.append(part)
            else:
                # This part too big → recurse with smaller separator
                result.extend(_split(part, rest_seps))
        
        # Now merge small consecutive parts up to chunk_size
        merged = []
        current = ""
        for part in result:
            candidate = current + sep + part if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    merged.append(current)
                current = part
        if current:
            merged.append(current)
        return merged
    
    pieces = _split(text, separators)
    
    # Add overlap by prepending tail of previous chunk
    chunks = []
    running_pos = 0
    for i, piece in enumerate(pieces):
        # Overlap: prepend tail of previous chunk
        if i > 0 and overlap > 0:
            tail = pieces[i - 1][-overlap:]
            content = tail + piece
        else:
            content = piece
        
        start = text.find(piece, running_pos)
        if start < 0:
            start = running_pos
        end = start + len(piece)
        running_pos = end
        
        chunks.append(Chunk(
            content=content,
            strategy="recursive",
            chunk_index=i,
            char_start=start,
            char_end=end,
            metadata={"chunk_size": chunk_size, "overlap": overlap},
        ))
    return chunks


if __name__ == "__main__":
    from pathlib import Path
    text = Path(__file__).parent.parent.joinpath("corpus/depot_faq.md").read_text()
    
    for name, fn in [("Fixed", fixed_size_chunker), ("Recursive", recursive_chunker)]:
        chunks = fn(text, chunk_size=400, overlap=50)
        print(f"\n{'=' * 70}")
        print(f"{name}: {len(chunks)} chunks")
        print('=' * 70)
        for c in chunks[:3]:
            print(f"\n[{c.chunk_index}] ({c.size} chars) chars {c.char_start}-{c.char_end}")
            print(f"  {c.content[:150]}...")
"""
Structural (markdown-header aware) and Semantic chunking.
"""
from __future__ import annotations
import re
from pathlib import Path

import numpy as np
import voyageai
from dotenv import load_dotenv

import sys
sys.path.insert(0, str(Path(__file__).parent))
from basic import Chunk

load_dotenv()
vo = voyageai.Client()


def structural_chunker(
    text: str,
    max_chunk_size: int = 800,
) -> list[Chunk]:
    """Split by markdown headers, respect hierarchy.
    
    Each chunk = 1 heading section + its content.
    If section > max_chunk_size, split by sub-headings or paragraphs.
    """
    # Regex: match heading lines (# / ## / ### / etc)
    heading_re = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    # Find all headings + positions
    matches = list(heading_re.finditer(text))
    if not matches:
        # No headings — treat as single chunk
        return [Chunk(text, "structural", 0, 0, len(text), {"level": 0})]
    
    chunks = []
    heading_stack = []  # [(level, title), ...] for context
    idx = 0
    
    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()
        section_start = match.start()
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        
        # Update heading stack (pop deeper/equal levels)
        while heading_stack and heading_stack[-1][0] >= level:
            heading_stack.pop()
        heading_stack.append((level, title))
        
        section_text = text[section_start:section_end].strip()
        
        # Path breadcrumb: "H1 > H2 > H3"
        path = " > ".join(t for _, t in heading_stack)
        
        # If section too big, split by paragraphs
        if len(section_text) <= max_chunk_size:
            chunks.append(Chunk(
                content=section_text,
                strategy="structural",
                chunk_index=idx,
                char_start=section_start,
                char_end=section_end,
                metadata={"level": level, "path": path, "title": title},
            ))
            idx += 1
        else:
            # Split by paragraphs, keep header + path in each sub-chunk
            paragraphs = section_text.split("\n\n")
            current = ""
            for para in paragraphs:
                candidate = current + "\n\n" + para if current else para
                if len(candidate) <= max_chunk_size:
                    current = candidate
                else:
                    if current:
                        chunks.append(Chunk(
                            content=current,
                            strategy="structural",
                            chunk_index=idx,
                            char_start=section_start,
                            char_end=section_end,
                            metadata={"level": level, "path": path, "title": title, "sub_chunk": True},
                        ))
                        idx += 1
                    current = para
            if current:
                chunks.append(Chunk(
                    content=current,
                    strategy="structural",
                    chunk_index=idx,
                    char_start=section_start,
                    char_end=section_end,
                    metadata={"level": level, "path": path, "title": title, "sub_chunk": True},
                ))
                idx += 1
    # Post-process: merge tiny heading-only chunks with next chunk
    MIN_CHUNK_SIZE = 50
    merged = []
    i = 0
    while i < len(chunks):
        current = chunks[i]
        # If chunk is heading-only and small, merge with next
        while (i + 1 < len(chunks) 
            and current.size < MIN_CHUNK_SIZE 
            and chunks[i + 1].metadata.get("level", 0) > current.metadata.get("level", 0)):
            next_c = chunks[i + 1]
            current = Chunk(
                content=current.content + "\n\n" + next_c.content,
                strategy="structural",
                chunk_index=len(merged),
                char_start=current.char_start,
                char_end=next_c.char_end,
                metadata={**next_c.metadata, "path": current.metadata.get("path", next_c.metadata.get("path"))},
            )
            i += 1
        current.chunk_index = len(merged)
        merged.append(current)
        i += 1
    return merged
    #return chunks


def _split_sentences(text: str) -> list[str]:
    """Simple Thai + English sentence splitter.
    Thai doesn't use periods → split on newline, punctuation, or long spaces.
    """
    # Split on: paragraph breaks, single newlines, . ! ? followed by space, Thai clause ending
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in parts if s.strip()]


def semantic_chunker(
    text: str,
    max_chunk_size: int = 800,
    similarity_threshold: float = 0.7,
) -> list[Chunk]:
    """Chunk boundary = topical shift.
    
    1. Split into sentences
    2. Embed each sentence
    3. Compute similarity between adjacent sentences
    4. Break at sentences where similarity < threshold (topical shift)
    5. Merge to respect max_chunk_size
    """
    sentences = _split_sentences(text)
    if len(sentences) <= 1:
        return [Chunk(text, "semantic", 0, 0, len(text), {})]
    
    # Batch embed all sentences (1 API call)
    result = vo.embed(sentences, model="voyage-3-large", input_type="document")
    embeddings = [np.array(e) for e in result.embeddings]
    
    def cosine(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b))  # already normalized
    
    # Find break points where similarity drops below threshold
    breaks = [0]  # start of first chunk
    for i in range(1, len(sentences)):
        sim = cosine(embeddings[i], embeddings[i - 1])
        if sim < similarity_threshold:
            breaks.append(i)
    breaks.append(len(sentences))
    
    # Group sentences into chunks
    chunks = []
    running_pos = 0
    for chunk_idx, (start, end) in enumerate(zip(breaks[:-1], breaks[1:])):
        content = " ".join(sentences[start:end])
        
        # Enforce max size — split further if needed
        if len(content) > max_chunk_size:
            # Split at midpoint (naive fallback)
            mid = len(sentences[start:end]) // 2
            parts = [
                " ".join(sentences[start:start + mid]),
                " ".join(sentences[start + mid:end]),
            ]
        else:
            parts = [content]
        
        for part in parts:
            if not part.strip():
                continue
            char_start = text.find(part, running_pos)
            if char_start < 0:
                char_start = running_pos
            char_end = char_start + len(part)
            running_pos = char_end
            chunks.append(Chunk(
                content=part,
                strategy="semantic",
                chunk_index=len(chunks),
                char_start=char_start,
                char_end=char_end,
                metadata={"threshold": similarity_threshold, "sentences": end - start},
            ))
    # Merge chunks smaller than min_size with next
    MIN_CHUNK_SIZE = 100
    final = []
    i = 0
    while i < len(chunks):
        current = chunks[i]
        while i + 1 < len(chunks) and current.size < MIN_CHUNK_SIZE:
            next_c = chunks[i + 1]
            current = Chunk(
                content=current.content + " " + next_c.content,
                strategy="semantic",
                chunk_index=len(final),
                char_start=current.char_start,
                char_end=next_c.char_end,
                metadata=next_c.metadata,
            )
            i += 1
        current.chunk_index = len(final)
        final.append(current)
        i += 1
    return final
    #return chunks


if __name__ == "__main__":
    text = Path(__file__).parent.parent.joinpath("corpus/depot_faq.md").read_text()
    
    for name, fn in [("Structural", structural_chunker), ("Semantic", semantic_chunker)]:
        chunks = fn(text)
        print(f"\n{'=' * 70}")
        print(f"{name}: {len(chunks)} chunks")
        print('=' * 70)
        for c in chunks[:4]:
            print(f"\n[{c.chunk_index}] ({c.size} chars)")
            if 'path' in c.metadata:
                print(f"  path: {c.metadata['path']}")
            print(f"  {c.content[:180]}...")
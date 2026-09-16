# Week 16 — Corpus Indexing + HTTPS

## Day 1 (Mon 14 ก.ย.) — Indexing Architecture Design

### Delivered
docs/indexing-architecture.md (211 lines)

### Current pipeline analysed
week-06/04_index_all_strategies.py:
- Hardcoded corpus path and database DSN
- Indexes all 4 chunking strategies at once (research concern)
- DELETE WHERE source LIKE 'week6_%' then rebuild
- No retry on Voyage API failure — a timeout kills the whole run
- print() for progress

### Gap for clients
Client needs to load their own product docs, SOPs, and policies. Without a
command, every install requires us to run Python scripts manually.

### Decisions locked
| Decision | Choice |
|---|---|
| Input formats | JSON array + markdown folder |
| Chunking | Fixed 400/50 default, overridable |
| Re-index | Replace all for that source |
| Source label | --source flag, default 'default' |
| Embedding batch | 128 per call, 3 retries, exponential backoff |
| Dry run | Yes — chunk count + cost estimate |
| Markdown parsing | spatie/yaml-front-matter |
| Schema | Add doc_id column + index |
| Progress | Laravel progress bar |

### Tech debt closed by this design
chunk_index will be included in chunk metadata. The Week 6 Python chunker
omitted it, so chunk ordering depended on row id — fragile if rows are ever
reinserted or reordered.

### Transaction safety
Delete + insert wrapped in one transaction. The Python version deleted first,
then inserted; a failure partway left the corpus empty. Rollback now restores
the previous corpus.

### Verification plan
Re-index the existing Depot RTB corpus through the new command, then run
assistant:eval-retrieval. If it still reports 100% hit@1, the port preserved
chunking behaviour. Any drop means the PHP chunker diverged from the Python one.

### For Tue (Day 2)
- Migration: add doc_id column
- DTOs: Chunk, IndexingReport
- CorpusLoader: JSON and markdown paths, validation
- Verify in tinker before building the rest

### Time
2 hours (Block 1 requirements 45min, Block 2 design 45min, wrap 30min)

## Day 2 (Tue 15 ก.ย.) — Migration, DTOs, CorpusLoader

### Shipped
1. Migration: `doc_id` varchar(128) nullable + composite index (source, doc_id)
2. spatie/yaml-front-matter installed
3. DTOs: Chunk, IndexingReport, IndexingException
4. CorpusLoader — JSON and markdown directory support

### Corpus format surprise
The design doc assumed `doc_id` and `title` fields. The real Depot RTB corpus
uses `id` and has no `title` at all — titles live in the first H1 of content.
Also 13 documents, not the 6 I had assumed from earlier retrieval output
(retrieval only ever surfaced the top 5).

Fix: loader accepts either `doc_id` or `id`. Title resolution falls back
through three levels: explicit field, first H1, then doc_id.

Lesson: read the actual data before finalising a schema assumption.

### Postgres ignores AFTER clause
Migration used `->after('source')`. Postgres has no column reordering, so
Laravel silently drops it — `doc_id` landed at the end of the table. No
functional impact, but worth knowing the hint is MySQL-only.

### Verified
JSON path: 13 documents loaded, titles extracted from H1, metadata preserved
(products 5-6 keys, faq/guide 3 keys), zero skipped.

Markdown path: title resolution correct at all three levels — frontmatter
beats H1, H1 beats doc_id fallback. `doc_id` and `title` correctly excluded
from metadata. Empty file skipped with reason recorded.

Error paths, 5/5:
- Missing path
- Malformed JSON (reports parse error)
- JSON object instead of array
- Duplicate doc_id (names the duplicate)
- Directory with no markdown files

### For Wed (Day 3)
- FixedChunker (port from Week 6 Python, add chunk_index)
- EmbeddingBatcher (128 per call, 3 retries, exponential backoff)
- CorpusIndexer (orchestration + transaction)
- CorpusIndex CLI command (progress bar, dry run)

### Time
3 hours (Block 1 migration 45min, Block 2 DTOs+loader 75min, Block 3 testing 45min, wrap 15min)

## Day 3 (Wed 16 ก.ย.) — Chunker, Batcher, Indexer, CLI

### Shipped
1. FixedChunker — ported from week-06/chunkers/basic.py
2. EmbeddingBatcher — wraps VoyageService with batching and outer retry
3. CorpusIndexer — orchestration with transaction safety
4. corpus:index CLI command with dry-run and progress bar

### Reading the Python source changed the port
The design doc's chunking loop was wrong. The Python original has an explicit
early break:

    if end >= len(text):
        break
    start = end - overlap

My design doc used `position += chunkSize - overlap` and looped on the
condition alone. For a document whose length is an exact multiple of the
stride, that produces a trailing chunk of `overlap` characters — garbage
chunks on short documents, and a different retrieval surface.

Also found: chunk_index, char_start, char_end existed as fields on the Python
Chunk object but were never written to the database — only `chunk.metadata`
was inserted. That is the Week 6 tech debt, now closed by putting them in
metadata.

Lesson: port from the source, not from a description of the source.

### Parity verified against Python
| Metric | Python | PHP |
|---|---|---|
| Total chunks | 103 | 103 |
| min/avg/max | 104/378/400 | 104/378/400 |
| chunk 0 span | 0-400 | 0-400 |
| chunk 1 span | 350-750 | 350-750 |
| chunk 2 span | 700-1100 | 700-1100 |

mb_substr matches Python's code-point slicing on Thai text.

### EmbeddingBatcher
VoyageService already retries twice at 500ms, which covers transient network
failures. Added an outer retry with exponential backoff (2s, 4s) — that is
what a 429 actually needs. The Python indexer had neither and died mid-run
on a timeout.

Also added a count assertion: if the API returns fewer vectors than texts
sent, the run aborts rather than silently misaligning chunks to embeddings.

### Dry-run estimate is approximate
Estimate uses 2.5 chars per token for Thai. Measured against a real 3-chunk
embed: 608 actual tokens vs the estimator's implied ~490 — roughly 25% low.

Left as-is and labelled "(approximate)" in the output. Under-estimating is
the safer direction for a cost preview, and the real number appears after
an actual run.

### Transaction safety
Delete and insert are wrapped together. Rows insert in batches of 500.
A failure at any point rolls back and leaves the previous corpus intact.

### Verified
Dry run against the real Depot RTB corpus:
- 13 documents, 34,515 chars
- 103 chunks, min/avg/max 104/378/400
- Estimate 15,606 tokens, $0.0028
- No API call, no database writes

### For Thu (Day 4)
HTTPS/TLS setup documentation — the other Priority 1 gap for this week.

Real indexing run and retrieval verification is Friday, so any chunking
regression shows up against the 100% hit@1 baseline.

### Time
3 hours (Block 1 chunker 45min, Block 2 batcher 60min, Block 3 indexer+CLI 60min, wrap 15min)
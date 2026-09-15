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
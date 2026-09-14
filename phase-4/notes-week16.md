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
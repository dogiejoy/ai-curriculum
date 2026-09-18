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

## Day 4 (Thu 17 ก.ย.) — HTTPS/TLS

### Approach chosen: Caddy in front of nginx
Internet → Caddy :443 (TLS) → nginx :80 (SSE + rate limit) → php-fpm

Rejected alternatives:
- Caddy replacing nginx: would mean rewriting the rate limiting done in
  Week 15 (Caddy needs a plugin for it), and discarding the SSE tuning
  already verified
- certbot + nginx: renewal needs a cron job the client can forget. Expired
  certificates at 3am on a Saturday is the common failure mode.

Caddy handles certificates only. Everything application-level stays in nginx,
which means the Week 15 work stands untouched and a client with their own
load balancer can drop Caddy entirely.

### Shipped
1. docker/caddy/Caddyfile — production, Let's Encrypt via DEPOT_DOMAIN
2. docker/caddy/Caddyfile.local — `tls internal` for local testing
3. docker-compose.yml — caddy service + caddy_data/caddy_config volumes
4. docker-compose.tls-local.yml — port and Caddyfile override for testing
5. docs/https-setup.md — setup, renewal, CDN/load-balancer guidance,
   troubleshooting, security headers
6. .env.docker.example — DEPOT_DOMAIN, DEPOT_TLS_EMAIL

caddy_data must persist. Losing it forces a fresh certificate request, and
Let's Encrypt allows 5 per domain per week.

### Port 80 already taken on the dev machine
Local testing uses 8000/8443 via the override file. Compose merges `ports`
arrays rather than replacing them, so the override needs `!override` or the
container tries to bind both sets and fails again.

### Testing the wrong thing first
Initial SSE test piped curl into grep, which buffers at 4KB. Events appeared
to arrive all at once — a property of the pipeline, not the server.

Second attempt used `grep --line-buffered` with timestamps. That showed bursts
of roughly 64 events every 3 seconds. Suspicious, but running the same test
against nginx directly (bypassing Caddy) produced the same pattern: 57, 63,
63, 63, 62. Identical shape means Caddy adds no buffering — `flush_interval -1`
works.

The remaining burst pattern is the bash pipeline, not the server.

Browser confirmed it: text renders progressively over the full 20 seconds.

Lesson: when measuring streaming, the measuring tool is part of the system
under test.

### Gap found that wasn't on the list
assistant.html broke when authentication shipped in Week 15. Every request
returned 401, and the frontend's error handler — written in Week 10 when the
only failure mode was a safety block — reported it as "Guardrail: blocked".

Two bugs in one: no token, and an error handler that misattributes any
failure to guardrails.

Fixed the token side: prompt on first load, store in localStorage, send as
Bearer header. The misleading error message is still there — worth fixing
before a client sees it.

Also hit a subtlety putting the token code in: it was initially placed inside
`<script src="...marked.min.js">`. A script tag with a src attribute ignores
its inline content entirely, so the code never ran and apiToken stayed
undefined.

### Verified
- Caddy obtains a local certificate on start
- HTTPS reaches php-fpm: response carries `via: 1.1 Caddy`, `server: nginx`,
  `x-powered-by: PHP/8.3.33`
- Auth, prompt caching, and markdown rendering all work over TLS
- SSE streams progressively in the browser

### For Fri (Day 5)
- Run corpus:index for real, verify eval-retrieval still reports 100% hit@1
- Fix the frontend error handler to distinguish 401/403/429 from guardrails
- Update README with the HTTPS section
- Tag v0.3.2

### Time
3 hours

## Day 5 (Fri 18 ก.ย.) — Verification and v0.3.2

### The verification that mattered

Indexed the Depot RTB corpus through the Laravel pipeline into a new source
(`depot-v2`), leaving the Python-indexed `week6_fixed` untouched for comparison.

Run: 13 documents, 103 chunks, 19,769 tokens, $0.0036, 3.7 seconds.

Database comparison:

| | week6_fixed (Python) | depot-v2 (PHP) |
|---|---|---|
| chunks | 103 | 103 |
| docs | 0 (doc_id was NULL) | 13 |
| avg chars | 379 | 379 |

chunk_index and char_start/char_end present in metadata — the Week 6 tech
debt is closed. First three chunks of prod_001: spans 0-400, 350-750,
700-1100, matching the Python output exactly.

Retrieval eval on depot-v2:
- hit@1: 100% (15/15)
- recall@5: 100%
- MRR: 1.000
- avg latency: 418ms (Python baseline was 445ms)
- easy/medium/hard: 100/100/100

Every question returned rr=1.00. The PHP pipeline produces retrieval quality
identical to the Python one that has been in use for ten weeks.

### Frontend error handling

401, 403, and 429 now render distinct messages instead of "Guardrail:
blocked". Added a double-click on the header to change the stored token
without clearing site data.

### Forty minutes lost to a stale token

After testing the 401 path with a deliberately wrong token, `9|wrongtoken`
stayed in localStorage. Subsequent questions returned 500 and I went looking
for a backend bug that did not exist.

What made it confusing: nginx logged a genuine `500 44`, and curl with the
same invalid token returned 401. Backend tests confirmed 401 for all three
invalid-token shapes (wrong id, wrong hash, malformed). So the 500 is real
and browser-specific, but not caused by what I assumed.

Logged as a known issue for Week 17. Impact is limited to mistyped tokens,
but a client hitting it would be as lost as I was.

The lesson is about test hygiene: a test that writes state needs to clean up
after itself, or the next observation is contaminated.

### Documentation

README: corpus indexing step in the quickstart, HTTPS note above the endpoint
table, DEPOT_DOMAIN and DEPOT_TLS_EMAIL in config, full doc index.

Runbook: corpus management — re-index, inspect what is loaded, verify
retrieval after changes, estimate cost before a large run.

### Tagged v0.3.2

### Week 16 summary

Mon: indexing architecture design (2h)
Tue: migration, DTOs, CorpusLoader (3h)
Wed: chunker, batcher, indexer, CLI (3h)
Thu: HTTPS via Caddy (3h)
Fri: verification, docs, tag (3h)

Total: 14 hours.

Bugs and surprises this week:
- Corpus uses `id` not `doc_id`, has no title field, contains 13 documents
  rather than the 6 I assumed from retrieval output
- Postgres silently ignores `->after()` in migrations
- The design doc's chunking loop was wrong; reading the Python source caught it
- Python's chunk_index existed but was never persisted
- Testing SSE through a grep pipeline measured the pipeline, not the server
- assistant.html had been broken since Week 15 auth shipped, reporting 401 as
  a guardrail block
- A script tag with src ignores its inline content
- Compose merges `ports` arrays rather than replacing them
- Stale localStorage token cost 40 minutes of misdirected debugging

Priority 1 gaps: 4/4 closed.

### For Week 17
- Backup and restore automation
- Update and upgrade path
- Investigate the 401-becomes-500 browser discrepancy
- Full end-to-end rehearsal: fresh install simulating a client deployment
- Tag v0.4 — pilot ready
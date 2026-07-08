# Week 6 — Chunking Strategies Notes

## Day 1 (Mon 6 ก.ค.) — 4 strategies implemented + compared

### Strategies built (with post-process fixes)
1. Fixed-size (chunker=400, overlap=50) — baseline
2. Recursive (LangChain-style separator hierarchy)
3. Structural (markdown headers with breadcrumb path metadata)
4. Semantic (sentence embeddings, threshold=0.7 for break points)

### Bugs discovered + fixed
- Structural creates heading-only mini chunks → merge with next when size < 50
- Semantic mis-groups markdown headings as topic shifts → merge chunks < 100 chars
- Semantic cost under-reported — sentence-embed call not counted (fix Wed)

### Counter-intuitive findings
1. Overlap = double-embed cost. Fixed/Recursive tokens > Structural/Semantic on same doc
2. Structural + Semantic use fewer tokens because no overlap redundancy
3. Storage scales with chunk count, not chunk quality
4. Latency variance ~50% between strategies = mostly Voyage API jitter

### Production decision for Depot RTB Assistant
Structural chunking is default:
- Best chunk quality (aligned with document structure)
- Path breadcrumb metadata enables filtered search + citations
- Lowest cost per doc (no overlap redundancy)
- Great for FAQ + product catalog docs
Semantic reserved for: long marketing content, blog posts, unstructured guides

### For Wed
- Extend all 4 chunkers to accept multiple docs (not just single markdown)
- Index all 4 strategies into pgvector with different `source` labels
- Fix Semantic total-token accounting
- Prepare corpus of 10-15 diverse Depot RTB docs (products + FAQs + guides)

## Day 3 (Wed 8 ก.ค.) — Multi-doc setup + indexing

### Corpus generated
- 13 docs × ~2,700 chars = 34.5K total via Claude Sonnet 4.6
- 3 categories: 6 products, 4 FAQs, 3 guides
- All Thai with technical English terms mixed

### Indexing results (4 strategies × 13 docs)

| Strategy | Chunks | Avg Size | Tokens | Cost |
|---|---|---|---|---|
| Fixed | 103 | 378 | 19,769 | $0.0036 |
| Recursive | 115 | 342 | 19,863 | $0.0036 |
| Structural | 103 | 333 | 17,350 | $0.0031 |
| Semantic | 153 | 222 | 17,074 | $0.0031 |

### Findings at scale (13 docs vs Day 1 single doc)
1. Structural + Fixed converge on chunk count (103 same) but Structural saves 12% tokens
2. Semantic over-fragments on multi-doc corpus — sentence splitter bug amplified
3. Recursive under-utilizes chunk_size limit due to aggressive `\n\n` split
4. Storage per strategy = negligible (~2 MB for 474 chunks)

### Production tech debt logged
- Semantic sentence splitter regex weak on Thai punctuation → 12-char chunks
- Recursive should merge small consecutive chunks up to target size
- Both defer to Week 9 eval framework where quality gap will show

### For Thu
- Design golden dataset: 15 questions covering ~all doc topics
- Answer key = doc_id (which doc contains the answer)
- Run each question × 4 strategies → measure recall@5 + MRR
- Compare rankings + report which strategy wins for Depot RTB context
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

## Day 4-5 combined (Thu 9 ก.ค.) — Retrieval metrics

### Golden dataset built
- 15 questions covering 13 corpus docs
- Balance: easy 8 / medium 5 / hard 2
- 3 doc types: product 6, faq 5, guide 4
- Language: th 13, en 1, mixed 1
- Saved as JSON — reusable Week 7+ retrieval, Week 9 eval framework

### Retrieval results

| Strategy | hit@1 | recall@5 | MRR |
|---|---|---|---|
| Fixed (400/50) | 93.3% | 100% | 0.967 |
| Structural | 86.7% | 100% | 0.933 |
| Recursive | 80.0% | 93.3% | 0.867 |
| Semantic | 80.0% | 93.3% | 0.867 |

### Counter-intuitive finding
Fixed chunker beats Structural despite:
- No metadata awareness
- Boundary quality worse (mid-word cuts)

Hypothesis: overlap (50 chars) creates redundant "safety net" for queries that straddle chunk boundaries. Every retrievable keyword appears in 2+ chunks. → confirms Chroma Research: "semantic doesn't always win"

### Hard-query ceiling
Q06 "ยาแก้ปวด ไม่ใช่ steroid" → all 4 strategies fail
- Requires reasoning (NSAID = non-steroid) or hybrid search
- Q6-class questions define upper limit of embedding-only retrieval
- Week 7 hybrid + Week 8 RAG generation will address

### Production decision for Depot RTB
- Default: Fixed (400 chunk, 50 overlap) — highest accuracy
- Backup: Structural — 6.6% lower hit@1 but path metadata for citations
- Trade-off is UX vs accuracy, not technical

### Week 6 skills consolidated
- 4 chunking strategies implemented from scratch
- Multi-doc chunker with metadata merging
- Golden dataset methodology
- Retrieval metrics (hit@1, recall@5, MRR)
- pgvector search with strategy-labeled sources
- Learned: don't over-engineer — Fixed often wins

### Blog draft outline (skip full write, saved for later)
Title: "4 Chunking Strategies on Thai Vet Warehouse Data: Fixed Won"
Sections:
1. Setup: 13 docs, 15 golden questions, Voyage 3-large
2. 4 strategies described (Fixed/Recursive/Structural/Semantic)
3. Findings: Fixed 93.3% hit@1 vs Structural 86.7%
4. Why: overlap = redundancy safety net
5. When Structural still wins: citation UX
6. Q06 ceiling: what's next (hybrid + RAG)
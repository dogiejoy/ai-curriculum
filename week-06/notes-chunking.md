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
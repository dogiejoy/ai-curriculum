# Week 7 — Hybrid Search Notes

## Day 1 (Mon 13 ก.ค.) — BM25 + RRF fusion attempted

### Built
1. Added tsvector generated column + GIN index on documents
2. Hybrid search framework (Python):
   - Vector search via pgvector cosine
   - BM25 via Postgres ts_rank_cd
   - RRF fusion (k=60)
   - Language detection (Thai/English/mixed)
   - Stopword filter (EN + TH)
   - AND-first tsquery (fallback to OR if empty)
   - BM25 score threshold filter

### Verified working
- Q1 (mixed keywords) — hybrid neutral, vector already correct
- Q2 (Thai reasoning, Q6 canary) — vector alone got Metacam #1
  - Week 6 metrics under-estimated: bigger top_k * 5 fetch pool = better dedup
  - **Q6 was within vector reach, we under-searched previously**

### Not working — critical findings

**1. Postgres FTS is NOT true BM25**
- ts_rank_cd = weighted term frequency approximation
- Rare specific terms (e.g. "excursion") not weighted properly
- Common words (e.g. "temperature") dominate ranking
- Q3 SOP query → BM25 ranks faq_003 (wrong) > guide_003 (correct)

**2. Thai FTS = 0 tokens**
- `simple` config splits by whitespace only
- Thai has no spaces → whole phrase = single "token"
- Exact-match lookups fail
- BM25 useless for 87% of Depot RTB queries (Thai)

**3. RRF fusion can HURT when one signal misleads**
- Q3 vector alone: guide_003 rank #1 (correct)
- Q3 hybrid RRF: faq_003 rank #1 (wrong)
- BM25 misdirect > RRF's rank normalization

### Threshold experiment failed
BM25 min-score 0.2 filter didn't help — the wrong doc (faq_003) scored 0.3, above threshold.
Real issue: BM25 ranking wrong, not "noise below threshold".

### Real solution = Reranker
Cross-encoder (Voyage rerank-2) reads query + candidate together, understands context.
Deferred to Day 3 (Wed 15 ก.ค.).

### Day 1 verdict
Hybrid search implementation is **net-neutral to net-negative** vs pure vector for Depot RTB.
BM25 helps ONLY when:
- Query is English-heavy (rare in Thai corpus)
- Rare exact keywords (product codes, English brands)
- Vector already agrees (redundant confirmation)

BM25 hurts when:
- Common English words dominate rare specific ones
- Thai FTS returns empty
- Wrong doc has more common terms than correct doc has rare ones

### For Day 3 (Wed)
- Voyage rerank-2 API: send query + top 20 candidates → rerank
- Cross-encoder scoring > BM25 approximation
- Expected: fix Q3 without breaking Q1/Q2

### Tech debt logged
- Postgres FTS insufficient for Thai — future consideration: pg_bigm extension or ES/OpenSearch
- Not blocker: Vector alone hits 93% hit@1, reranker will lift further
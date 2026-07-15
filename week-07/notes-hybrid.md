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

## Day 2 (Tue 14 ก.ค.) — Reranker + HyDE concepts

### Cross-encoder = real leverage
Bi-encoder (Voyage embed): fast, encodes query + doc separately, loses fine-grained signal
Cross-encoder (Voyage rerank-2): reads query + doc together, understands context
- +5-15% recall@5, +10-25% MRR typical
- 100-300ms latency for 20 candidates
- Multilingual (Thai supported)
- Cost: $0.05/1M tokens

### Industry standard pattern
1. Vector search: top 20-50 (broad net, high recall)
2. Rerank: top 5-10 (precision filter)
3. LLM generation: uses top 5-10 as context

### Reranker limitations
- Only ranks candidates from initial pool (must include correct doc in top-20)
- Cannot transform query
- Adds 100-300ms latency (usually acceptable for chat)

### HyDE (Hypothetical Document Embeddings)
Instead of embedding query, embed LLM-generated fake answer.
Why: fake answer uses doc-like vocabulary → closer to real docs in vector space
When shines: abstract, reasoning, short queries
Cost: +1-3s latency, ~$0.001/query with Haiku
Risk: LLM hallucinates wrong direction

### Query Expansion alternative
LLM generates 2-3 query variants → search each → merge
Better for vocabulary variance, worse for question-doc gap

### Depot RTB architecture decision for Wed
Baseline: vector-only (93.3% hit@1)
Pipeline B: vector (top 20) + rerank-2 (top 5)
Pipeline C: HyDE + vector + rerank

Measure on golden dataset: hit@1, recall@5, MRR, latency, cost per query

## Day 3 (Wed 15 ก.ค.) — Rerank experiment + honest conclusion

### Pipeline B built
- rerank.py — Voyage rerank-2 wrapper (returns RerankedCandidate + stats)
- hyde.py — HyDE generator with Haiku 4.5 (tested but not measured full pipeline)
- 02_pipeline_vector_rerank.py — full evaluation over 15 golden questions

### HyDE quality (spot check)
Query: "ยาแก้ปวดสำหรับสุนัข ไม่ใช่ steroid"
Hypothetical answer generated correctly mentioned:
- Meloxicam (Metacam) — matches prod_005
- Carprofen (Rimadyl) — vocabulary overlap
- NSAID technical term
Cost: $0.0025/query, latency 5.71s (Haiku)
→ Quality good, latency too high for real-time chat

### Pipeline B measurement results

Vector-only baseline TODAY: 100% hit@1
- Week 6 reported 93.3% but under-measured (top_k*5=25 chunks fetched)
- Today's implementation: top-20 chunks → dedupe to docs → top-5
- Broader initial pool = correct doc's best chunk always surfaces

Rerank impact:
| Metric | Vector | +Rerank | Δ |
|---|---|---|---|
| hit@1 | 100.0% | 93.3% | -6.7pp |
| recall@5 | 100.0% | 100.0% | 0 |
| MRR | 1.000 | 0.967 | -0.033 |

Rerank cost: $0.0002/query, +0.5s latency

### Regression case (Q14 diagnosed)
Query: "สั่งด่วนหลังเลิกงานได้ไหม"
Ground truth: guide_001 (emergency stock)
- Vector: guide_001 rank #1 (understood urgent intent)
- Rerank: faq_002 rank #1 (over-weighted "สั่ง" keyword → general ordering doc)

Cross-encoder pathology: over-weights lexical overlap when semantic intent matters more.

### Week 7 verdict

For Depot RTB corpus at current scale (13 docs, 15 golden questions):
- Vector alone (top_k=20, dedupe → top-5) = **100% hit@1**
- Hybrid BM25 = **net-negative** (Postgres FTS limitation, Thai FTS unusable)
- Reranker = **net-negative** (over-weights keywords, hurts on colloquial queries)

**Depot RTB Assistant production decision**:
- KEEP: Vector-only retrieval, HNSW cosine, top-20 chunk fetch → dedupe → top-5 docs
- SKIP: BM25 hybrid, reranker
- DEFER: HyDE (measure when corpus grows to 100+ docs or query variance increases)

### Not rejecting reranker/HyDE — deferring

- Golden dataset is too clean (15 curated questions on 13 docs)
- Real Depot RTB production queries will be messier + more diverse
- Reranker + HyDE likely shine when:
  - Corpus size > 100 docs
  - Query complexity increases
  - Ambiguous/abstract queries appear
- Revisit these techniques post-launch when we have real usage data

### Cost of not adding complexity
- ✓ Simpler pipeline = easier client integration for Package A
- ✓ Lower latency (0.32s vs 0.82s)
- ✓ No extra API dependency (only Voyage embed)
- ✓ Cheaper per query
- ✓ Better production reliability (fewer failure modes)

**Business win**: knowing when NOT to add complexity is a mark of experienced AI engineer.
Package A pitch benefits: "we ship what proven works, defer what's speculative."
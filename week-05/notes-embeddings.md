# Week 5 — Embeddings Notes

## Day 1 (Mon 29 มิ.ย.) — Fundamentals + Model Comparison

### Concept established
- Embedding = vector representation in 1024-dim space (or 512/3072 depending on model)
- Voyage pre-normalizes L2=1 → cosine sim = dot product
- Asymmetric input_type ("document" vs "query") matters for Voyage
- Same product cross-language > different products same language (Voyage 3-Large)

### Cross-language verified ⭐
- Thai ↔ English same product: 0.88-0.94 similarity
- Same Thai but different product: 0.72
- → Production rule: RAG corpus can mix languages, semantic match dominates

### Voyage "high baseline" caveat
- Voyage similarities never go close to 0 even for unrelated text (0.50+)
- Unlike OpenAI which spreads wider (0.10-0.60 range)
- DO NOT use absolute threshold (sim > 0.5 = relevant)
- USE relative ranking (top-K most similar)

### Model selection — Depot RTB

| Model | Top-1 Acc | Latency | Cost/1M | Verdict |
|---|---|---|---|---|
| voyage-3-large | 4/4 | 0.80s | $0.18 | ✓ DEFAULT |
| voyage-3-lite | 2/4 | 0.37s | $0.02 | ❌ Fails on short Thai |
| OpenAI 3-large | 4/4 | 5.31s | $0.13 | Skip — slow + Thai token overhead |
| OpenAI 3-small | 3/4 | 0.74s | $0.02 | Backup option |

Decision: voyage-3-large primary, OpenAI 3-small fallback

### Production gotchas discovered
- voyage-multilingual-3 does NOT exist (use voyage-3-large for multilingual)
- OpenAI Thai tokens cost ~44% more than Voyage (verify before commit)
- Lite model lose semantic precision on short queries (4-char "อาหารแมว" misclassified)

## Day 2/3 combined (Wed 1 ก.ค.) — pgvector setup + integration

### pgvector concepts learned
- Extension adds vector(N) type + distance operators + index types
- Distance operators: <=> (cosine, our choice), <-> (L2), <#> (inner product)
- Two index types: HNSW vs IVFFlat

### HNSW vs IVFFlat decision tree
Choose HNSW when:
- < 10M vectors (our case — Depot RTB never hits this)
- Accuracy matters
- Data updates frequently

Choose IVFFlat when:
- > 10M vectors
- Build speed critical (batch ingesting)

HNSW knobs:
- Build: m=16 (edges), ef_construction=64 (build search width)
- Query: ef_search=40-100 (runtime tunable, no rebuild)
- Higher ef_search → better recall, slower query

### Critical: index operator must match query operator
- CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)
- SELECT ... ORDER BY embedding <=> query_vec
- If mismatch → index ignored → full table scan

### Production patterns established
- Docker Compose with named volume (data persists container recreation)
- Schema separates: source, content, metadata (jsonb), embedding
- Metadata GIN index for jsonb filter queries
- Source column index for corpus segmentation

### Python integration
- psycopg + pgvector.psycopg.register_vector() for type adapter
- input_type MUST differ: "document" for insert, "query" for search
- Cosine SIMILARITY = 1 - (embedding <=> query)  # pgvector returns distance

### Gotchas encountered
1. voyage-multilingual-3 doesn't exist (Day 1) → use voyage-3-large
2. Voyage free tier: 3 RPM / 10K TPM — hit limit at query 4 in test
   → Recommend adding payment method before Week 6 (golden dataset)
3. psycopg.types.json.Json vs Jsonb type mismatch → use Jsonb for jsonb columns

### Verified
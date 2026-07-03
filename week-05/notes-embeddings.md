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

## Day 4-5 combined (Fri 3 ก.ค.) — Laravel + pgvector integration

### Shipped
1. VoyageService (Laravel HTTP client wrapper) with retry
2. Document Eloquent model with Vector cast
3. Artisan command: docs:index (JSON → Voyage → pgvector)
4. Endpoint /api/search with:
   - Vector similarity (Distance::Cosine via nearestNeighbors)
   - JSONB metadata filter (@> operator)
   - Source column filter
   - Combined filters

### Cross-stack parity verified
Python-indexed docs (day1_corpus, 8 rows) + Laravel-indexed docs (depot_laravel_test, 5 rows) coexist in same table.
Search from Laravel gives identical similarity scores as Python (0.7585 exact match).
→ Template pattern for clients: any team stack can ingest, Laravel serves search API.

### pgvector-php composer package notes
- Auto-registered migration for CREATE EXTENSION vector (2022_08_03_000000)
- Provides Vector class + HasNeighbors trait + Distance enum
- nearestNeighbors('embedding', $vector, Distance::Cosine) → ORDER BY <=> distance
- Result has $doc->neighbor_distance attribute (cosine distance)
- similarity = 1 - neighbor_distance

### Production pattern discovered
- Semantic embedding sometimes weights KEYWORDS over CONTEXT
  - "ป้องกันเห็บ" on dog corpus → cat product with keyword rank #1
- ALWAYS combine metadata filter + semantic search for domain-specific queries
- Week 7 hybrid search will address this systematically

### Bugs encountered + fixes
- system PHP 7.0 vs Herd 8.3 PATH conflict — reactivate Herd terminal
- Migration table exists (from Python) → IF NOT EXISTS makes idempotent
- Json vs Jsonb type — Laravel Eloquent metadata cast handles automatically
- JSON_UNESCAPED_UNICODE missing in response → improvement for Week 6

### Skills consolidated (Week 5)
- Embedding fundamentals + cosine similarity math
- Voyage AI multilingual verified 4/4 Thai accuracy
- HNSW vs IVFFlat trade-offs, when to choose which
- Docker Compose stateful services + persistent volumes
- Laravel migrations for extension-based Postgres features
- Eloquent + pgvector cross-stack (Python ingest, Laravel search)
- Metadata jsonb filtering with @> containment operator
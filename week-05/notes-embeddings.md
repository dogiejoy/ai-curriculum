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
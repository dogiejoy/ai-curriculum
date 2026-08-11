# Week 11 — Cost Optimization + Caching

## Day 1 (Mon 10 ส.ค.) — Prompt Caching

### Plan revision
Original: Query classifier Day 1, caching Day 2
Revised: Caching Day 1 (safer + faster win), classifier Day 2-3

### Concepts learned
1. Anthropic prompt caching:
   - cache_control marker on system prompt blocks
   - 5-min TTL (free tier) or 1-hour (paid)
   - Cache write: 1.25x input price
   - Cache read: 0.1x input price (90% off)
   - Break-even: 2 queries within window
2. Minimum token requirement:
   - Sonnet: 1024 tokens
   - Others: 2048 tokens
   - Below minimum = silently ignored (no error!)
3. Cache-friendly prompt structure:
   - Stable base too small (673 chars ≈ 250 tokens) → can't cache
   - Sources larger (13,986 chars ≈ 5,200 tokens) → cachable
   - Cache hit requires exact text match

### Bug discovered
Anthropic PHP SDK uses camelCase (cacheControl), not snake_case
(cache_control). Silent failure — no error, just cache ignored.

### Shipped
1. Extended CompletionResult DTO — cacheCreationTokens, cacheReadTokens
2. Updated ClaudeService::calculateCost() — cache pricing tiers per model
3. AssistantContext DTO — split into stableSystemPrompt + sourcesText
4. ContextBuilder emits both parts for downstream caching

### Measured results (validation)
- 1st call: $0.0457 (25% premium — cache write overhead)
- 2nd call same query: $0.0067 (85% savings)
- Cache broke down: 11,065 tokens written first, read on second

### Business projections
Depot RTB expected cache hit rate:
- Realistic bursty pattern: 30-50% hit rate
- Best case (repeated identical queries): 85% savings
- Worst case (all unique queries): 25% overhead

Blended cost projection:
- No cache (baseline): $0.045/query
- With cache (30% hit): $0.032/query (-29%)
- With cache (50% hit): $0.026/query (-42%)

### Deferred to Day 2-3
- Query classifier (Haiku vs Sonnet routing)
- ContextBuilder default to emit cached format
- AssistantChatController to use cached system prompts
- Cache hit rate monitoring endpoint
- Full 30-question re-run to measure real hit rate

### Deferred to Week 12
- Semantic-aware cache key (use retrieval sig as cache key)
- Cache warming for hot queries

## Day 2 (Tue 11 ส.ค.) — Production Endpoint Caching

### Shipped
1. streamComplete() accepts string|array system (for cached blocks)
2. Streaming path captures cache tokens from message_start event
3. AssistantChatController passes 2-block cached system format:
   - Block 1: stableSystemPrompt (no cache — below 1024 min)
   - Block 2: sourcesText with cacheControl ephemeral
4. SSE 'done' event includes cache_creation_tokens, cache_read_tokens,
   cache_hit_ratio
5. Frontend assistant.html:
   - Status bar shows ⚡ cached (N tok) or 📝 cache write (N tok)
   - Session cost header displays cumulative savings + % reduction
   - Green ⚡ badge distinguishes cached from fresh queries

### Cache validation in production endpoint
- 1st call (cache miss): $0.057, 28s, cache_creation_tokens=11,731
- 2nd call (cache hit): $0.0074, 6.8s, cache_read_tokens=11,065
- 84% cost savings + 76% latency reduction on cache hits
- Cache TTL 5 min covers realistic clinic burst patterns

### 🚨 Critical bug discovered + fixed
Day 1 refactor of ContextBuilder left broken sourcesText loop:
- Placeholder variables ($marker, $title, $docId, $fullContent) never
  populated with actual logic
- Result: sources labeled with [doc_1] but content from doc_5
- Symptom: cold-chain query → refusal about Revolution Plus
         NSAID query → refusal about Hill's Science Diet
- Retrieval was correct; sourcesText assembly broken

Fix: proper loop with fetchFullDocs() call + variable assignment
Regression tested via tinker + curl — Metacam answer now correct

### Lesson learned
When refactoring existing working code (ContextBuilder Week 8 → Week 11):
- Should have run regression test IMMEDIATELY after refactor
- Placeholder comments ("// ... existing per-doc formatting ...") in code
  = time bomb waiting to explode
- Cache metrics working ≠ answers working
- Week 9 LLM-as-judge would have caught this on 1st query

Regression test principle:
"Every refactor to ContextBuilder must run assistant:eval-retrieval before
commit."

### Business framing
"We shipped prompt caching to production endpoint. Bursty clinic usage
patterns (5-10 queries per session) see 70-85% cost reduction on cache
hits. First-query overhead 25% amortized rapidly.

We also caught our own regression during rollout — hidden bug from
prior refactor that only surfaced when we retested end-to-end. This is
why measurement infrastructure matters."

### Deferred to Day 3-4
- Query complexity classifier (Haiku vs Sonnet routing)
- Full 30-question eval-judge with caching enabled
- Cache hit rate monitoring endpoint
- A/B quality comparison (cached vs non-cached, Haiku vs Sonnet)

### Business projections (updated)
Depot RTB blended cost per query (production):
- Baseline (Week 8 v0.1): $0.045
- With caching (v0.2, this week): $0.007 (cache hit) - $0.057 (cache write)
- Realistic 30-50% hit rate: ~$0.020-0.030 blended
- Target with routing (Week 12): $0.008
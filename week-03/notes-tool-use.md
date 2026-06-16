# Week 3 — Tool Use Notes

## Day 1 (Mon 15 มิ.ย.) — Tool Use Overview

### Core mental model
- Claude doesn't execute tools — just REQUESTS
- We dispatch + return tool_result
- Loop until stop_reason="end_turn"

### API mechanics
- `stop_reason`: "end_turn" vs "tool_use" (loop signal)
- Multi-turn: assistant content has tool_use blocks → user content has tool_result blocks
- Multiple tool_use in ONE turn = parallel execution
- tool_use_id must match (one-to-one)

### tool_choice modes
- `auto` (default): Claude decides — best for most use cases
- `any`: forces SOME tool — DANGEROUS without turn guard (infinite loop risk)
- `tool` specific: forces named tool — good for classifier/structured-output pattern
- `none`: ⚠️ Claude can still claim to use tools — better to OMIT tools param entirely

### Production patterns confirmed
1. **Self-correcting retry** — Claude retries failed tool with different params (Exp 1)
2. **Disambiguation** — Claude picks correct option from search results based on user intent
3. **Parallel execution** — independent tools called together in same turn (~50% latency saving)
4. **Default param inference** — Claude reads tool description for optional defaults
5. **Tool description = documentation for Claude** — invest time here

### Safety patterns
- Always bound loops with MAX_TURNS — never trust LLM stop condition alone
- Force tool_choice on FIRST turn only, then revert to auto
- Tool_choice="none" → omit tools instead (cleaner)

### Known quirks
- Character bleeding (Thai + Chinese chars mixed) — recurring issue, need system prompt fix
- Each turn = full API call = real latency (3-5s) — UX must show progress

## Day 2 (Tue 16 มิ.ย.) — Structured Outputs + Strict Tools

### Big news: Structured Outputs is GA
2 sub-features:
- JSON outputs (`output_config.format`): grammar-constrained response
- Strict tool use (`strict: True`): guaranteed tool input schema

### JSON outputs trade-offs (Block 1 data)
- Old way (prompt + parse): 2.49s, stochastic format
- NEW cold start: 16.78s ❌ (grammar compilation)
- NEW warm cache: 1.74s ✓ (better than old)
- Cache: 24 hr from last use

Production rule:
- Stable schema → NEW + pre-warm at deploy (best of both)
- Dynamic schema → OLD wins (no cache benefit)
- Latency-critical first call → OLD
- Batch processing → NEW (+ 50% batch discount)

### Strict tools trade-offs (Block 2 data)
- 95% of cases: smart model handles without strict (Test 1-3 identical)
- 5% edge cases break things: Test 4 - non-strict generated "<UNKNOWN>" string 
  in integer field → downstream TypeError

Decision rule:
- DB writes / side effects → strict required
- Read/search tools → skip strict (save latency)
- Limits: 20 strict tools per request, 24 optional params total

### Incompatibilities to remember
- ❌ Cannot combine output_config.format with:
  - Message prefilling
  - Citations
- ✓ Can combine with: tool use, streaming, batch, prompt caching

### SDK helpers
- Python: client.messages.parse(output_format=PydanticModel)
- Returns response.parsed_output as Pydantic instance
- Sync only currently (Anthropic SDK v0.60+)
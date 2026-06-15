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
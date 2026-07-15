# Week 8 — Depot RTB Assistant v0.1 Architecture

## High-level Flow
User query (Thai/English)
↓
[Laravel API endpoint: POST /api/assistant/chat]
↓

INTENT ROUTING
├── DB query intent → Tool use (Week 3 pattern, DB Query Agent)
└── Doc question → RAG pipeline (this Week 8)
↓
RETRIEVAL (from Week 5-7)
├── Voyage embed query (input_type=query)
├── pgvector top-20 chunks (HNSW cosine)
└── Dedupe → top-5 unique docs
↓
CONTEXT ASSEMBLY
├── Format retrieved chunks with citations markers
├── Add system prompt (role + guardrails)
└── Add user query
↓
LLM GENERATION (streaming)
├── Claude Sonnet 4.6 (default) or Haiku 4.5 (cost-critical)
├── SSE stream to client
└── Track: tokens, cost, latency
↓
RESPONSE
├── Streaming text + inline citations
└── Final metadata: sources, cost, tokens

## Boundary Decisions

**Unified endpoint for RAG + DB queries**
- Single entry point: `/api/assistant/chat`
- Intent routing via LLM function-calling (Sonnet decides tool)
- Alternative rejected: separate endpoints = frontend complexity

## Design Decisions

### 1. Citation Format
- **Primary**: Anthropic built-in citations API
- **Fallback**: Custom `[doc_N]` markers if quality issues

### 2. System Prompt Structure
role: You are Depot RTB Assistant for vet clinic staff.
behavior:

- Answer in Thai (natural, professional tone).
- Ground every claim in provided sources.
- If sources insufficient, say "ไม่มีข้อมูลนี้ในระบบ" — don't hallucinate.
- Use Thai vet terms + English when standard (Frontline, NSAID, mg/kg).
- Keep answers concise unless user asks detail.

context: [retrieved chunks with metadata]
user query: [Thai/English question]

### 3. Response Format (Streaming)
- Reuse `ClaudeService::streamComplete()` from Week 4
- SSE event sequence:
  1. `metadata` event first: `{sources: [doc_ids]}` — client shows source badges
  2. `text` deltas: normal streaming
  3. `done` event: `{tokens, cost, latency}` for cost tracking

### 4. Error Handling + Guardrails

| Scenario | Response |
|---|---|
| No relevant docs (top similarity < 0.4) | "ไม่มีข้อมูลนี้ในระบบ ลองถามใหม่หรือติดต่อทีมงาน" |
| Retrieval timeout (>10s) | "ระบบช้าผิดปกติ ลองใหม่อีกครั้ง" |
| LLM refused | Same as no docs |
| PII in query | Log warning, proceed (skip guardrails until Week 10) |

### 5. Model Selection

| Case | Model | Reasoning |
|---|---|---|
| Simple factual (Q1-Q5, Q8-Q11) | Haiku 4.5 | Fast + cheap |
| Reasoning (Q6, ambiguous) | Sonnet 4.6 | Handle nuance |
| Fallback if timeout | Haiku 4.5 | Guarantee response |

**Default for launch**: Sonnet 4.6. Later: intent-based routing to Haiku for savings.

## Week 8 Day-by-Day Plan

### Day 1 (Mon 20 ก.ค.) — Retrieval Service (3hr)
- Port `search_strategy()` from Week 6 Python → Laravel
- Class: `App\Services\RetrievalService`
- Method: `retrieveTopDocs(query: string, topK: int = 5): array`
- Return: `[{doc_id, content, similarity, metadata}, ...]`

### Day 2 (Tue 21 ก.ค.) — Context Builder (3hr)
- Class: `App\Services\ContextBuilder`
- Format chunks + metadata → prompt sections
- Test with Anthropic citations API

### Day 3 (Wed 22 ก.ค.) — Assistant Chat Endpoint (3hr)
- Controller: `AssistantChatController`
- Wire: retrieval → context → streamComplete
- Reuse SSE pattern from Week 4

### Day 4 (Thu 23 ก.ค.) — Frontend Integration (2hr)
- Extend `chat.html` from Week 4
- Add sources sidebar
- Show retrieval metadata

### Day 5 (Fri 24 ก.ค.) — End-to-end + Demo (3hr)
- Run all 15 golden questions through full pipeline
- Measure Claude generation quality (not just retrieval)
- Record demo video for portfolio

## Component Reuse Map

| Component | Source | Purpose |
|---|---|---|
| `ClaudeService::streamComplete` | Week 4 | LLM streaming |
| `VoyageService::embedOne` | Week 5 | Query embedding |
| `Document` Eloquent model | Week 5 | pgvector queries |
| SSE controller pattern | Week 4 | Response streaming |
| `chat.html` | Week 4 | Frontend base |
| Golden dataset | Week 6 | Testing |
| Retrieval logic (top-20 → dedupe → 5) | Week 6/7 | Production choice |

## Blockers to Investigate Mon Morning

1. **Anthropic citations API in PHP SDK?**
   - Check: `vendor/anthropic-ai/sdk/src` for citations type
   - Fallback: custom `[doc_N]` markers

2. **Streaming metadata BEFORE text**
   - SSE event for `{sources: [...]}` needs to emit before first text delta
   - Check `ChatStreamController` flow — insert new event type

3. **Chunk content vs full doc content for LLM context**
   - Chunks ~400 chars (Fixed strategy)
   - LLM needs enough context
   - Solution: retrieve top-5 chunks, fetch full docs from DB for LLM

4. **Context window size for 5 full docs**
   - Each ~2,700 chars = ~1,000 tokens
   - 5 docs = ~5,000 tokens
   - Sonnet 4.6 context: 200K → plenty of room

## Open Questions for Mon

- Anthropic citations vs custom markers — test which first?
- Full docs in context vs chunks only — measure both?
- Intent classifier: LLM-based OR keyword heuristic first?

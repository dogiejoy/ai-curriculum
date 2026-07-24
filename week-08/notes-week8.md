# Week 8 — Depot RTB Assistant v0.1

## Day 1 (Mon 20 ก.ค.) — Retrieval Service in Laravel

### Blockers investigated
1. Anthropic PHP SDK citations → beta namespace only
   - Decision: Use custom [doc_N] markers for v0.1
   - Migrate to native citations when stable
2. Docs data intact (474 chunks × 4 strategies × 13 docs)
3. Voyage API working from Laravel (1024 dim)

### Shipped
1. RetrievalService class
   - retrieveTopDocs(query, topK, source?, filter?)
   - Uses week6_fixed as default strategy
   - Fetch top-20 chunks → dedupe → top-5 docs
   - JSONB metadata filter support (species, category, etc.)
   - Returns [{doc_id, content, similarity, metadata, chunk_count}]
2. assistant:eval-retrieval artisan command
   - Runs golden dataset via RetrievalService
   - Reports hit@1, recall@5, MRR, per-difficulty
   - Saves JSON results for tracking over time

### Metrics achieved (Laravel)
| Metric | Value |
|---|---|
| hit@1 | 100% (15/15) |
| recall@5 | 100% |
| MRR | 1.000 |
| Avg latency | 402ms |

Cross-stack parity confirmed: identical similarity scores as Python
(e.g. Q1 NexGard = 0.6642 exact match).

### Production choices logged
- Default source: week6_fixed (Week 6 winner)
- Broader chunk pool (top_k * 4 = 20) enables perfect dedup
- Custom [doc_N] citations (beta risk avoided)
- Retrieval alone can be quality gate — no rerank/hybrid needed

### For Day 2
Build ContextBuilder:
- Retrieve top-5 docs via RetrievalService
- Fetch FULL doc content (not just chunk) for LLM context
- Format with [doc_1], [doc_2] markers + metadata
- System prompt structure (grounding + Thai + refuse-if-unknown)

## Day 2 (Wed 22 ก.ค. Session 1) — Context Builder + End-to-end

### Blocker 3 resolved
Full docs > chunks — measured on Q6 NSAID:
- Chunks (1,257 chars): Claude couldn't name product, no dosage
- Full docs (8,850 chars): Complete answer with active ingredient, dosage table
- Cost delta: $0.018/query (negligible at Package A scale)

Tech debt logged: chunk_index missing from metadata — using id-based ordering for now

### Shipped
1. RetrievalService::fetchFullDocs() — retrieve all chunks per doc_id
2. AssistantContext DTO (immutable, sources + system prompt + metadata)
3. ContextBuilder service:
   - build() orchestrates retrieval → dedupe → fetch full → format
   - Similarity threshold 0.4 for "no relevant docs" check
   - Extract markdown title from first heading
   - Format [doc_N] markers in system prompt
4. Empty-context path for irrelevant queries → refusal system prompt

### End-to-end verified (3 test cases)
Q6 NSAID: full production quality (dosage, ingredient, warnings, citations)
Q8 Cold-chain: multi-source structured answer with 3-zone temperature table
Irrelevant: clean refusal in Thai, $0.001 cost

### Metrics
Retrieval latency: ~700ms (from 400ms — fetchFullDocs adds ~350ms)
Generation latency: 12-17s (Sonnet 4.6 non-streaming)
Cost per real query: ~$0.045
Cost per refusal: ~$0.001

### Next (Session 2)
- AssistantChatController endpoint /api/assistant/chat
- SSE with metadata event (sources) BEFORE text stream
- Perceived latency < 3s (first token) via streaming

## Day 3 (Wed 22 ก.ค. Session 2) — Assistant Chat Endpoint

### Shipped
1. Route: POST /api/assistant/chat
2. AssistantChatController:
   - Validates request (message, top_k, source, filter, model, max_tokens)
   - SSE event sequence:
     * retrieval_start (timestamp)
     * sources (list + relevance + latency)
     * generation_start (model)
     * text (many, streamed deltas)
     * done (tokens, cost, total latency)
     * error (if exception)
   - Handles client disconnect via connection_aborted()
   - Reuses ContextBuilder + ClaudeService::streamComplete
   - Full audit logging per query

### End-to-end verified (3 test scenarios)

NSAID query:
- 5 sources retrieved (top sim 0.6571 = Metacam)
- Full markdown answer with dosage table
- 21.3s total (retrieval 490ms + generation 20.8s)
- Cost $0.0486

Irrelevant query:
- has_relevant_docs = false triggered
- Refusal "ไม่มีข้อมูลนี้ในระบบ Depot RTB..."
- 2.4s total, $0.001 cost
- Zero wasted tokens

Metadata filter (species=cat):
- Correctly narrowed to 3 cat products
- Answer focused on cat food (Royal Canin Renal SO)
- 16.9s total, $0.034 cost

### Business projection
- Blended cost per query ~$0.032 (Sonnet 4.6)
- 1000 queries/day = $960/month
- Optimization path: Haiku for simple queries → -80%, Prompt caching Week 12 → -90% input
- Package A infrastructure cost negligible vs value delivered

### Production notes
- artisan serve buffers response — verified Week 4
- nginx production stack streams properly with X-Accel-Buffering: no header
- Client disconnect detected via connection_aborted() → server stops early

### For Day 4 (Thu 23 ก.ค.)
Extend chat.html from Week 4 with:
- Sources sidebar showing badges (title + similarity + doc_id)
- Streaming text with markdown rendering
- Cost/latency display at end (from 'done' event)
- Optional: metadata filter UI (species/category)

## Day 4 (Thu 23 ก.ค.) — Frontend Integration

### Shipped: public/assistant.html
Single-file HTML with vanilla JS + marked.js for markdown rendering.

Features:
- 5 SSE event handlers (retrieval_start, sources, generation_start, text, done, error)
- Sources sidebar with badge cards (title, marker, doc_id, similarity, metadata pills)
- Assistant bubble with markdown rendering (tables, headings, lists, code)
- Status bar with per-query metrics
- Session cost accumulator (top right)
- Empty-state handling ("ยังไม่มีคำถาม", "ไม่พบเอกสารที่เกี่ยวข้อง")
- Apple-inspired clean UI
- Auto-scroll on new content
- Textarea auto-resize
- Enter to send (Shift+Enter for newline)

### Design decisions
- Right sidebar (not left) — sources are secondary reference, chat is primary
- Metadata pills for scannability (species, category, brand)
- Similarity as monospace number (not bar) — precision matters for engineers
- Session cost prominent — client sees value delivered
- Progressive indicator (🔍 → 💬) matches actual backend phases

### Client library choice
- marked.js from jsDelivr CDN
- 1 script tag, zero build step
- Alternative rejected: no bundler for v0.1, keep simple

### Verified end-to-end
NSAID query: full sources + rich markdown answer + $0.0485
Irrelevant query: empty sources + refusal + $0.0013
Session cost accumulated correctly
Layout responsive to content length

### v0.1 backend + frontend feature complete
Depot RTB Assistant ready for Friday demo + measurement
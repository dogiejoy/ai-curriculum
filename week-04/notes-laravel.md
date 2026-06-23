# Week 4 — Laravel Integration Notes

## Day 1 (Mon 22 มิ.ย.) — Setup + ClaudeService

### Stack pivoted (vs curriculum)
- Used official `anthropic-ai/sdk ^0.27` (released April 2026, beta)
- Skip rolling own HTTP client — SDK handles retry/streaming/types

### Laravel project bootstrapped
- Laravel 13.16.1 (latest)
- PHP 8.x via [Herd/Homebrew — note env manager]
- Composer packages: anthropic-ai/sdk, guzzlehttp/guzzle (auto via Laravel)

### ClaudeService design
- Singleton via service container
- Returns immutable CompletionResult DTO (text, tokens, cost, stop_reason)
- Auto-logs every completion (model, tokens, cost)
- Catches specific exceptions: BadRequestException (4xx user error) vs others (server)
- Configurable retry via env (timeout, maxRetries, backoff delays)

### SDK retry verified
- Default: 2 retries, 0.5s → 8s exponential backoff
- 600s default timeout (overridable to 60s for snappy UX)
- Auto-retries: connection errors, 408, 409, 429, 5xx

### Error handling tests (3/3 pass)
- Invalid model → APIStatusException, status 404 in message body
- max_tokens too high (999999) → BadRequestException with helpful message
  Found: Sonnet 4.6 max output = 128,000 tokens
- Empty messages → BadRequestException "at least one message is required"

### Pricing dict ported from Python
- Opus 4.7: $5/$25 per M
- Sonnet 4.6: $3/$15
- Haiku 4.5: $1/$5

### Production patterns established
- Service class + DTO for type safety
- env-driven config (no hardcoded retry/timeout)
- Structured logging per request (queryable for cost analysis later)
- Typed exception catching (BadRequestException vs APIConnectionException)

### Skip / saved for later
- Structured outputs (output_config.format) → Tue/Wed reading
- Tool use in Laravel → Wed hands-on
- Streaming SSE → Wed deep work
- Cost tracking middleware → Thu

### Things to remember
- $e->getCode() returns 0 (PHP exception code, NOT HTTP status) — actual status in $e->getMessage() body
- Always catch specific exception types (BadRequestException) over generic (APIStatusException)
- SDK is BETA — pin version in composer.json, watch for breaking changes

## Day 2 (Tue 23 มิ.ย.) — Streaming docs + Laravel SSE patterns

### Anthropic streaming event lifecycle
6 event types ใน proper order:
1. message_start         — message metadata (id, model, initial input_tokens)
2. content_block_start   — เริ่ม content block (text/tool_use/thinking)
3. content_block_delta   — incremental updates (text_delta/input_json_delta/thinking_delta)
4. content_block_stop    — block complete
5. message_delta         — final cumulative usage tokens
6. message_stop          — end of stream

Multiple content blocks per message possible (e.g. text + tool_use)
Ping events every ~15s (keepalive — ignore in UI)

### Empirical chunk size
- Anthropic batches small tokens into chunks ~20-25 chars
- ~2-3 deltas/second perceived rate — smooth UX
- For 300-char Thai response: 12 deltas in 5 seconds

### PHP SDK createStream() signature
- Same parameters as create()
- Returns BaseStream (implements Iterator)
- foreach ($stream as $event) — straightforward

### Laravel SSE patterns (3 options)
- response()->stream() with closure — DEFAULT CHOICE
- response()->eventStream() — Laravel 11+ helper (verify in Laravel 13)
- new StreamedResponse() — manual Symfony

### Critical SSE headers
- Content-Type: text/event-stream
- Cache-Control: no-cache, no-transform
- X-Accel-Buffering: no  (nginx buffer bypass)
- Connection: keep-alive

### Output buffering gotchas
- ob_end_clean() before loop to disable PHP buffer
- ob_flush() + flush() per event in loop
- nginx default buffers 8KB — header above bypasses
- DevTools Network tab to verify (chunks should arrive one-by-one)

### Frontend
- EventSource browser API for GET endpoints (simple)
- fetch() + ReadableStream for POST endpoints (Wed will need)
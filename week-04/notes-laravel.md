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
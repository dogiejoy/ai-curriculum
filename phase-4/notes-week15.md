# Week 15 — Path B Build Sprint (Auth + Rate Limiting)

## Context
Path B chosen Mon 7 ก.ย.: build pilot-ready features before selling.
Week 15-17 = 3-week sprint. Target: v0.4 pilot-ready by 25 ก.ย.

## Day 1 (Mon 7 ก.ย.) — Rest day
Extended recovery after 4-day break + Path B decision mental shift.

## Day 2 (Tue 8 ก.ย.) — Auth Architecture Design

### Delivered
docs/auth-architecture.md (214 lines) — complete design spec

### Decisions locked
| Decision | Choice |
|---|---|
| Auth package | Laravel Sanctum |
| Token pattern | Single-tenant (1 user, N tokens) |
| Abilities | chat:query, admin:stats |
| Rate limit key | Token ID (auth) / IP (anon) |
| Default limits | 60/hr chat, 120/hr admin, 10/hr anon |
| Health endpoints | No auth (Docker/LB access) |
| Token management | Artisan CLI (create/list/revoke) |
| Middleware order | Auth → RateLimit → Safety → Controller |

### Key architectural insight
Auth must come BEFORE safety middlewares in the chain.
Reason: unauthenticated requests shouldn't consume LLM budget on
PII/injection classification. Cheapest rejection first.

### Deferred (documented as non-goals)
- Multi-tenant isolation (pilot = single-tenant per install)
- OAuth/SSO (client adds if needed)
- Fine-grained per-user permissions

### Implementation plan
Wed 9 ก.ย.: Sanctum install + migrations + User seeder + 3 CLI commands
Thu 10 ก.ย.: Middleware wiring + rate limiters + config file
Fri 11 ก.ย.: E2E testing (10 scenarios) + docs + tag v0.3.1

### Time
2 hours (Block 1 requirements 45min, Block 2 design 45min, wrap 30min)

## Day 3 (Wed 9 ก.ย.) — Sanctum + Token CLI

### Shipped
1. Laravel Sanctum installed (composer require laravel/sanctum)
2. HasApiTokens trait added to User model
3. Org user created (single-tenant pattern): "Depot RTB" id=1
4. Three artisan commands built:
   - depot:token:create --name= --abilities= --user=
   - depot:token:list (table: ID, Name, Abilities, Last used, Created)
   - depot:token:revoke {id} (with confirmation prompt)
5. Two production tokens seeded:
   - warehouse-app (chat:query)
   - ops-dashboard (admin:stats)

### Surprises during install
- personal_access_tokens table already existed (Laravel 11+ ships it by default)
  → deleted the duplicate migration Sanctum published
- Original migration already marked "Ran" (2026_06_24_085529)

### Bug caught + fixed
config/depot.php was missing the opening <?php tag.
Symptom: every artisan command printed the config array as raw text before
its real output. Would have corrupted JSON/SSE responses in production.
Fix: added <?php as line 1.

### Verified in tinker
- Abilities isolation: chat token cannot do admin:stats, and vice versa
- findToken() resolves plaintext → token model → owner
- Revoked tokens are hard-deleted (not soft-deleted)

### For Thu (Day 4)
Wire middleware to routes:
- auth:sanctum + ability:chat:query + throttle:chat on /api/assistant/chat
- auth:sanctum + ability:admin:stats + throttle:admin on /api/admin/cost-stats
- Named rate limiters in AppServiceProvider (chat 60/hr, admin 120/hr, anon 10/hr)
- Keep /api/health and /api/ready open

### Time
3 hours (Block 1 install 45min, Block 2 CLI 60min, Block 3 verification 50min, wrap 15min)

## Day 4 (Thu 10 ก.ย.) — Middleware Wiring + Rate Limiters

### Shipped
1. routes/api.php cleaned + protected:
   - Removed duplicate unprotected /admin/cost-stats (Week 12 leftover
     was overriding the protected version — Laravel uses last registration)
   - Removed all commented-out legacy routes
   - Protected /search and /chat-stream with chat:query (they cost money too;
     flagged for removal review in Week 17)
2. Sanctum ability middleware aliases registered in bootstrap/app.php
3. Named rate limiters in AppServiceProvider::configureRateLimiting():
   - chat: 60/hr per token, 10/hr per IP for anonymous
   - admin: 120/hr per token
   - Keys prefixed token:/ip: to avoid collisions
4. Rate limit env vars added to .env.docker.example

### Bugs caught + fixed
Bug 1: 500 instead of 401 on unauthenticated request
- Cause: Laravel tried route('login') redirect for non-JSON requests;
  API-only app has no login route → RouteNotFoundException
- Fix: shouldRenderJsonWhen() in bootstrap/app.php forces JSON for api/*
- Lesson: server shouldn't depend on client sending Accept header correctly

Bug 2: HTTP 200 with correct 401 body
- Cause: `use Throwable;` import emitted a PHP warning (global namespace);
  warning echoed before headers → status stuck at 200
- Fix: removed the unnecessary import
- Lesson: any output before headers breaks status codes silently

### Smoke test — 6/6 passed
| Test | Result |
|---|---|
| No token → chat | 401 ✓ |
| Admin token → chat | 403 ✓ |
| Chat token → chat | 200 + full stream ✓ |
| Health/ready without token | 200 ✓ |
| Admin token → admin | 200 + stats ✓ |
| Chat token → admin | 403 ✓ |

Abilities isolation verified in both directions.

### Not yet tested
- Rate limiting 429 (needs 61 requests) — deferred to Fri
- APP_DEBUG=true still exposes full stack traces in error responses;
  production config review needed Fri

### For Fri (Day 5)
- Rate limit test (script 61 requests, expect 429 with retry_after)
- Anonymous rate limit test (11 requests without token)
- Revoked token test (401)
- APP_DEBUG production setting review
- Update README + runbook with auth section
- Write docs/authentication.md (client-facing guide)
- Tag v0.3.1

### Time
3 hours (Block 1 routes 60min, Block 2 limiters 60min, Block 3 smoke test 35min, wrap 15min)
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
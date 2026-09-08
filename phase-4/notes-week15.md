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
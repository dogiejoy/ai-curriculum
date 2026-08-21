# Week 12 — Production Deployment

## Day 1 (Mon 17 ส.ค.) — nginx + php-fpm streaming

### Shipped
1. docker/nginx/depot-rtb.conf — SSE-tuned nginx config:
   - proxy_buffering off on /api/assistant/chat only (not global)
   - proxy_read_timeout 3600s for streaming
   - fastcgi_buffering off + fastcgi_read_timeout 3600s
2. docker/php/Dockerfile — PHP 8.3-fpm-alpine:
   - Extensions: pdo, pdo_pgsql, pgsql, intl, zip, mbstring, bcmath
   - Composer bundled
3. docker-compose.yml — nginx + php-fpm services:
   - nginx :8080 (host) → :80 (container)
   - php-fpm :9000 (internal only)
   - Volumes: current directory mounted at /var/www/html
   - host.docker.internal for Postgres connection (existing container)

### Verified end-to-end
- curl streaming: events line-by-line over 15s ✓
- Cache write on first call: $0.059 for 11,731 tokens
- Cache read on second call: $0.019 (67% off)
- All Week 8-11 features working through new stack:
  * Retrieval (0.73 top similarity Metacam)
  * ContextBuilder with sources
  * Routing (multi_hop → Sonnet)
  * Cache metrics in SSE
  * Full markdown streaming in browser

### Bug fixed
- Frontend rendered markdown only at stream end → user perceived "batched"
- Fix: incremental marked.parse() per text chunk
- Scope issue: asstText lived in sendMessage(), fix rendered inside callback

### Design decisions
- Option C chosen: nginx + php-fpm in Docker, keep Postgres separate
- Reason: minimum reconfigure while learning production patterns
- Day 2 will consolidate into single Docker Compose (all 3 services)

### Deferred to Day 2
- Add Postgres to same docker-compose.yml
- Environment variable management (.env for secrets)
- Named volumes for Postgres persistence
- Full stack "docker compose up" bring-up

### Deferred to Day 3+
- Monitoring/observability (cost dashboard endpoint)
- HTTPS/TLS setup
- Log aggregation
- Health check endpoints

### Business framing
"Depot RTB Assistant v0.3 runs on standard nginx + php-fpm + Postgres stack.
No exotic infrastructure. Client ops teams already know this stack.
Ships as docker-compose.yml — one command to launch.
Streaming works production-grade (not just artisan serve buffering)."

## Day 2 (Tue 18 ส.ค.) — Full Docker Compose

### Shipped
1. docker-compose.yml consolidated to 3 services:
   - nginx :8080 (SSE-tuned)
   - php-fpm :9000 (Laravel + pgvector extensions)
   - postgres :5432 (external volume week-05_pgdata)
2. External volume reuse preserved Week 6 data:
   - 4 chunking strategies (fixed/recursive/semantic/structural)
   - 474 chunks total intact
3. Environment secrets pattern:
   - .env.docker (gitignored) for API keys + passwords
   - .env.docker.example checked into repo as template
   - php-fpm and postgres services read via env_file directive
4. Datasets moved into project:
   - storage/app/eval-datasets/v1.json (15 questions)
   - storage/app/eval-datasets/v2.json (30 questions)
   - Self-contained — no external filesystem dependency

### Verified end-to-end
- docker compose ps: 3 services running
- Data preservation: SELECT confirms 474 chunks intact after volume remount
- Full retrieval eval: 100% hit@1 preserved (matches Week 8/11 baseline)
- API endpoint: retrieval + routing + cache all functional
- Env secrets flow: ANTHROPIC_API_KEY + VOYAGE_API_KEY reach php-fpm

### Design decisions
- External volume (external: true, name: week-05_pgdata) = data survives
  container rebuilds + reuses Week 5 investment
- .env.docker not .env — separate from Laravel-native .env (host runtime)
- Overrides pattern: DB_HOST/PORT/DB fixed in compose, secrets from env_file
- Datasets in storage/app/eval-datasets = production-portable, no filesystem
  dependency on host layout

### Trade-offs
- Docker overhead: +43ms per query vs host-native (445ms vs 402ms)
- Acceptable: portable stack > tiny latency gain
- Client onboarding: 1 file (.env.docker) + docker compose up

### Bug fixed
Path assumption ai-curriculum was ~/side-projects/ but actual ~/ai-sp/
- Old default: base_path('../ai-curriculum/week-XX/golden_dataset.json')
- Broke inside container (mount only sees /var/www/html)
- Fix: storage_path('app/eval-datasets/vN.json') — Laravel-native path

### For Day 3 (Wed 19 ส.ค.)
Monitoring + observability:
- Cost dashboard endpoint (aggregate cache hit + routing distribution)
- Health check endpoints (/api/health, /api/ready)
- Structured JSON logs
- Consider Loki/Grafana OR just tail logs for v0.3

## Day 3 (Wed 19 ส.ค.) — Monitoring + Observability

### Shipped
1. HealthController with 2 endpoints:
   - GET /api/health — liveness (fast, no dependencies)
   - GET /api/ready — readiness (DB + corpus + API keys)
2. Docker healthcheck wired on nginx service (30s interval)
3. AssistantQueryLog model + migration:
   - Captures every query metric from Week 8/10/11 logging
   - Fields: query_redacted, sources, model, routing_rule, tokens
     (input/output/cache_creation/cache_read), cost_usd, latency,
     PII count + types, guardrail action + category
   - Indexes on created_at + (model, created_at) for stats queries
4. AdminStatsController::costStats endpoint:
   - GET /api/admin/cost-stats?hours=N
   - Aggregates: total cost, cache hit rate, model distribution,
     rule distribution, latency percentiles (p50/p95/p99), PII stats
5. artisan assistant:stats CLI command:
   - Ops-friendly terminal output
   - Same data as endpoint, no HTTP overhead

### Verified in production
5 queries in 1-hour window:
- Total cost: $0.1921 (avg $0.038/query — 15% below Week 11 projection)
- Cache hit rate: 41.4% (23,456 reads / 33,207 writes)
- Cache savings: $0.063 (33% off baseline)
- Latency p50: 20s, p95: 22.8s
- Routing: 100% Sonnet (multi_hop rule dominates as expected)

### Business framing
"Depot RTB Assistant v0.3 ships with per-client cost visibility. 
Admin endpoint returns 24hr cost + cache performance + latency 
percentiles. CLI available for ops (SSH-in stats). Client can audit 
every query cost themselves. This is production monitoring baseline —
Prometheus/Loki upgrade path exists if needed for scale."

### Design decisions
- DB table over log parsing — proper analytics, queryable, indexes
- Middleware bypass for guardrail_action=proceed only (v0.3 scope)
- Guardrail-triggered queries (blocked/redirected) NOT logged to DB yet
- p99 requires 100+ samples for meaningful measurement
- Cache savings calc: 2.70/1M savings per read token (Sonnet)

### Trade-offs
- APP_ENV=production in .env.docker means migrate needs confirmation
- Consider APP_ENV=staging in dev, production only for deploy
- Log middleware bypass = missing analytics for blocked queries
  (Week 12 Day 4 if time)

### For Day 4 (Thu 20 ส.ค.)
Deployment runbook + client onboarding docs:
- README section: quickstart (git clone → .env.docker → docker compose up)
- Runbook: common ops (restart, rebuild, backup, view stats)
- Failure scenarios: DB down, API key expired, disk full
- Client-onboarding checklist (secrets, domain, TLS notes)

## Day 4 (Thu 20 ส.ค.) — Documentation + Runbooks

### Shipped
1. README.md — full rewrite:
   - Feature list, quickstart (5-min setup)
   - Architecture diagram
   - Endpoints reference
   - Configuration table
   - Links to detailed docs
2. docs/runbook.md — 194 lines:
   - Daily ops (health, stats, logs)
   - Restart operations (graceful/full/rebuild)
   - Data management (backup, restore, truncate)
   - Secrets rotation (Anthropic, Voyage, DB)
   - Monitoring alert thresholds
   - Common ops FAQ
3. docs/failure-scenarios.md — 297 lines:
   - 6 primary failure modes with symptoms → diagnosis → fix
   - Ready check breakdowns
   - API errors (Anthropic/Voyage)
   - Streaming failures
   - Cost spikes with investigation SQL
   - Disk full recovery
   - Container restart loops
4. docs/client-onboarding.md — 100+ lines:
   - Pre-sales info gathering
   - Technical prep checklist
   - 5-step deployment
   - Handover to client
   - Package A tier guidance ($99/$299/$999)

### Business asset unlocked
Package A now has:
- Client-facing README (professional impression)
- Ops runbook (client can self-serve daily tasks)
- Failure playbook (reduces our support burden)
- Onboarding checklist (repeatable client rollouts)

### Deferred to Day 5
- Full end-to-end verification with fresh Docker rebuild
- Phase 3 retrospective (Weeks 9-12)
- Phase 4 (Package A launch prep) kickoff
- v0.3 = production ready milestone announcement

## Day 5 (Fri 21 ส.ค.) — Phase 3 Close + Phase 4 Kickoff

### Fresh rebuild verification
docker compose down + up = client onboarding simulation
- All 3 services healthy in ~30s
- /api/health OK, /api/ready 4/4 checks pass
- Real query streamed successfully
- Analytics logged: $0.058 first call (cache write)
- Total time from start to working query: ~1 min (README claim <10 min proven)

### Phase 3 Retrospective (Weeks 9-12)

Shipped 4 weeks:
- Week 9: Eval Framework (LLM-as-judge + v2 dataset + judge bug caught/fixed)
- Week 10: Guardrails (PII + injection + 5 portfolio screenshots)
- Week 11: Cost Optimization (Cache 85% savings + routing A/B validated)
- Week 12: Production Deployment (Docker + monitoring + full docs)

Key wins:
1. Empirical > opinion methodology compounded across all weeks
2. Transparency about bugs = strongest possible trust signal
3. Compression handling: skipped days absorbed without quality loss
4. Reuse from Phase 1-2: golden dataset, Voyage contract, SSE patterns
5. Conservative shipping (safety > aggressive optimization)

Tech debt logged (deferred to v0.4/Phase 5):
- Semantic chunker Thai splitter
- chunk_index metadata
- pg_bigm for Thai FTS
- Output PII scan
- Rate limiting infrastructure
- Multi-turn state
- Semantic-aware cache key

Business assets accumulated:
- Product: v0.3 feature-complete + safety-hardened + monitored + documented
- Docs: README + 3 operational docs
- Portfolio: 11 screenshots + architecture doc
- Economics: $0.038/query measured, 41% cache hit, 29% cost reduction
- Pricing: Package A tiers drafted ($99/$299/$999)

### 12-Week Curriculum Overall

Started: Mon 25 May 2026
Ended: Fri 21 Aug 2026
Duration: 12 weeks + 4 days (93% on-time delivery)

Phase 1 (1-4): Foundations
Phase 2 (5-8): RAG Deep Dive → Depot RTB Assistant v0.1
Phase 3 (9-12): Production Concerns → v0.3 client-deployable

Original 12-month business goal: 2-3 clients + recurring revenue by April 2027
Current status: Curriculum complete with 7+ months buffer for business execution

### Phase 4 Plan (Weeks 13-16, 24 Aug - 18 Sep)

Week 13: Landing page + positioning
Week 14: Case study + content marketing prep
Week 15: Sales outreach first wave (20-30 prospects)
Week 16: Demos + first pilot proposal

Critical success factors:
1. Positioning clarity: "RAG for Thai vet clinic warehouse management"
2. Proof over promises: real metrics not hypothetical
3. Niche depth > breadth (vet clinics first)
4. Support model realistic (runbook = self-service)
5. Cash flow: watch margins

### Phase 4 Immediate Next Steps
Weekend (optional): draft hero paragraph + brainstorm 5 target clinic types
Mon 24 Aug: landing page copy outline (no coding)
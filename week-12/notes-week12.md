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
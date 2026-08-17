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
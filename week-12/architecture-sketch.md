# Week 12 — Production Deployment Architecture

## Goals

1. Replace `php artisan serve` with production nginx + php-fpm stack
2. Package as Docker Compose for reproducible deploy
3. Verify streaming works end-to-end in browser (no buffering)
4. Establish monitoring baseline
5. Write deployment runbook

## Target Architecture

Single-server Docker Compose stack:
- nginx :80 (reverse proxy, static files, SSE-tuned config)
- php-fpm :9000 (Laravel Assistant backend)
- postgres :5432 (pgvector, existing corpus)

## Week 12 Day Plan

### Day 1 (Mon 17 ส.ค.) — nginx + php-fpm setup
Block 1: nginx config for SSE streaming (buffering off, timeouts up)
Block 2: php-fpm config tuning (workers, memory limits)
Block 3: Verify streaming works locally with real backend

### Day 2 (Tue 18 ส.ค.) — Docker Compose full stack
Block 1: PHP Dockerfile (base image + extensions)
Block 2: docker-compose.yml (3 services + volumes + env)
Block 3: Bring up stack + migrate + run eval

### Day 3 (Wed 19 ส.ค.) — Monitoring + observability
Block 1: Log format standardization (JSON structured logs)
Block 2: Cost tracking endpoint (aggregate from existing logs)
Block 3: Health check + readiness endpoints

### Day 4 (Thu 20 ส.ค.) — Deployment runbook
Block 1: Client onboarding checklist (env vars, secrets, TLS setup notes)
Block 2: Runbook for common ops (restart, rebuild, backup, restore)
Block 3: Failure scenarios + recovery steps

### Day 5 (Fri 21 ส.ค.) — Phase 3 close
Block 1: Full end-to-end verification (30 questions via production stack)
Block 2: Phase 3 retrospective (Weeks 9-12)
Block 3: Phase 4 prep (Package A launch tasks)

## Success Criteria for Week 12

- ✓ `docker compose up -d` brings up working stack
- ✓ Browser sees streaming word-by-word (not batched)
- ✓ 30-question eval passes at 100% hit@1 through production stack
- ✓ Cost tracking endpoint shows cache hit rate + routing distribution
- ✓ Deployment runbook <5 pages, actionable
- ✓ v0.3 declared production-ready for Package A pilot client

## Deferred to Phase 4

- HTTPS/TLS setup (needs domain per client)
- CI/CD pipeline
- Load testing at scale
- Multi-tenant architecture (if needed)
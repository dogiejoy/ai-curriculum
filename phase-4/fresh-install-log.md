# Fresh install rehearsal — 24 ก.ย. 2026

Clone: github.com/dogiejoy/laravel-ai-starter @ 4231711
Rule: follow README only. Anything it does not say is a gap.

## Blockers found

### B1 — docker compose up fails immediately
`docker-compose.yml` declares the pgdata volume as `external: true` pointing
at `week-05_pgdata`, a name carried over from the Week 5 research setup.
A fresh machine has no such volume, so Compose refuses to start.

### B2 — README claims a sample corpus that is not in the repo
`storage/app/.gitignore` contains `*`, so `storage/app/corpus/` never ships.
README step 5 says "the stack ships with the Depot RTB sample corpus".

### B3 — no user to own a token
Only DatabaseSeeder.php exists. The org user was created by hand in tinker
during Week 15. `depot:token:create --user=1` has nothing to attach to.

### Documentation errors found by reading
- Two sections numbered "### 5."
- Points at `docs/indexing.md — TODO Week 12 Day 5`; the real file is
  `docs/indexing-architecture.md`
- Expected health output says version 0.3.0
- Step 6 calls /api/admin/cost-stats without an Authorization header

### B4 — DB_PASSWORD missing from .env.docker.example
Compose warns and defaults it to an empty string. Postgres then initialises
with a blank password while php-fpm hardcodes `dev`, so the app cannot connect.

### B5 — container_name prevents two installs coexisting
Every service pins `container_name: laravel-ai-*`. A second install on the
same machine collides. Matters for anyone running staging alongside production.

### B1 confirmed differently than expected
The external volume did not fail here because `week-05_pgdata` exists on this
machine. Worse: the fresh install silently attached to the production
database. On a client machine it would fail outright.

### B6 — port 80 conflict has no documented fallback
Caddy binds 80 and 443. Anything already using them stops the install, and
the README offers no alternative.

### B7 — live API keys in .env.docker.example (CRITICAL)
See incident-2026-09-24-api-keys.md. Both revoked.

## Summary

Seven blockers from one rehearsal. One critical.

| # | Blocker | Status |
|---|---|---|
| B1 | pgdata is `external: true` pointing at week-05_pgdata | open |
| B2 | README claims a sample corpus the repo does not contain | open |
| B3 | No seeder creates the user that owns tokens | open |
| B4 | DB_PASSWORD absent from the template | fixed |
| B5 | container_name prevents two installs coexisting | open |
| B6 | Port 80/443 conflict has no documented fallback | open |
| B7 | Live API keys in the template | fixed, keys revoked |

Plus four README errors: duplicate "### 5." headings, a TODO pointing at a
file that does not exist, the expected version output is wrong, and the
analytics curl omits its auth header.

B1 behaved differently than predicted. The external volume did not fail —
it existed on this machine, so the fresh install silently attached to the
production database. On a client machine it would fail outright. The silent
version is worse.
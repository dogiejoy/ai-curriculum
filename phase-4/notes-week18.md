# Week 18 — Fresh Install Verification

## Day 1 (Mon 28 ก.ย.) — Rounds two and three

### Round two: three blockers

B9 — `.env.docker` invisible to Compose
Compose substitutes `${VAR}` in the compose file from `.env`, not from
`env_file`. `env_file` only injects into the container's environment.
Without `--env-file .env.docker`, `DB_PASSWORD` substituted as an empty
string and Postgres refused to start.

This machine has a Laravel `.env` carrying `DB_PASSWORD=dev`, which Compose
picked up by accident. Every previous "it works" was that coincidence.

B10 — no composer install step
`vendor/` is gitignored, correctly. A clean clone has no dependencies, so
every request dies on a missing `autoload.php`. The README went straight
from `cp .env.docker.example` to `docker compose up`.

Blocking for 100% of clients. Invisible to us because `vendor/` has sat on
this machine since Week 3 and the container mounts the host directory.

B11 — readiness pinned to a research label
The corpus check counted rows where `source = 'week6_fixed'` — a name from
our own Week 6 chunking experiments. No client will ever have it.

Every deployment would report `not_ready` forever: load balancers
withholding traffic, Docker healthchecks failing, monitoring alerting.
Written in Week 12 when that was the only corpus that existed, never
revisited.

### Round three: three more, all in the fix for round two

B12 — `make install` ignored its own fallback
The README documented running without Caddy when ports 80 and 443 are
taken. The Makefile written today to make setup easier started every
service and died on the port conflict.

Three days between writing the fallback and writing the thing that bypasses
it.

B13 — `key:generate` needs a file this deployment does not have
It writes `APP_KEY` into `.env`. This stack uses `.env.docker` via
`env_file`. The container has no `.env` at all, so the command threw.

Now generating the key directly into `.env.docker` with `openssl`-equivalent
PHP and recreating the containers, since `env_file` is read at container
creation.

B14 — nginx caches the upstream IP
Recreating php-fpm to pick up the new `APP_KEY` gave it a new container IP.
nginx resolves `php-fpm` once at startup, so it kept sending to the old
address: 502 on every request.

Restarting nginx fixed it immediately, confirming the cause. Recreating
nginx alongside php-fpm in the Makefile.

### What the three rounds show

| Round | Blockers |
|---|---|
| 1 (Thu) | 7 |
| 2 (today) | 3 |
| 3 (today) | 3 |

The count is not falling. Each round's fixes clear the path far enough to
reach the next problem — and round three's blockers were all created by
round two's fixes.

Two distinct failure modes:
- Things hidden by developer machine state (B9, B10 — a stray `.env`,
  a long-lived `vendor/`)
- Things assumed rather than tested (B11's hardcoded label, B12's Makefile
  bypassing a fallback documented three days earlier)

The second kind keeps appearing because writing a fix and verifying a fix
are different activities.

### v0.4 deferred again
Round four tomorrow from a clean clone. Tag only if it finds nothing.

Three rounds, three sets of blockers. Tagging now would be a guess.

### Time
3 hours
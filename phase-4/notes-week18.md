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

## Day 2 (Tue 29 ก.ย.) — Round four

### Install itself ran clean
`make install-nohttps` completed every step from a clean clone: composer
install, APP_KEY generated into `.env.docker`, services up, migrations,
org user seeded from `DEPOT_ORG_NAME`. No 502. B12, B13, B14 all hold.

First install sequence to run without intervention.

### B11 came back
Readiness still reported `source: week6_fixed`. Yesterday's fix went into
the throwaway test clone, not the repository. A clean clone brought the
original straight back.

The fix existed for a day in a directory that gets deleted every round.

### B16 — retrieval pinned to a research label
`RetrievalService::DEFAULT_SOURCE = 'week6_fixed'`, from the Week 6
chunking experiments.

A client indexes their corpus under any other name and retrieval returns
nothing. Readiness says ready. The corpus has rows. Every question comes
back with no relevant documents.

The most damaging blocker in five rounds, because everything looks correct
until the first question. Install succeeds, health checks pass, corpus
indexes, token works — and the assistant answers nothing.

Same class of bug as B11: a label from our own research baked into a path
a client depends on. B11 was in the health check, visible immediately.
B16 was in the retrieval path, visible only when someone asks something.

Source now comes from `config('depot.corpus.source')` via
`DEPOT_CORPUS_SOURCE`.

### Round four verdict
Install sequence: clean.
Application logic: two blockers, one a regression from fixing in the wrong
place.

Verified after the fix: retrieval_start, sources, routing,
generation_start, text — the full chain from a clean install.

But the verification ran on a clone that was `git pull`ed, not cloned
fresh. That is the same shortcut that let B11 survive a day. Round five
starts from nothing.

### Time
3 hours

## Day 3 (Wed 30 ก.ย.) — Round five, clean, v0.4.0 tagged

### Round five found nothing

Clean clone, no prior state. Every step passed on the first attempt:

- `make install-nohttps` — composer install, APP_KEY into `.env.docker`,
  services up, migrations, org user seeded
- `/api/health` — 200, correct version
- `corpus:index` — 13 documents, 103 chunks, $0.0036
- `/api/ready` — ready, `sources: ["sample"]`
- `depot:token:create` — token issued, owner correct
- Chat — retrieval, routing, generation, streaming text

Yesterday's fixes are in the repository, not just in a test clone that
gets deleted.

### Five rounds

| Round | Blockers |
|---|---|
| 1 | 7 |
| 2 | 3 |
| 3 | 3 |
| 4 | 2 |
| 5 | 0 |

Fifteen total. Three categories:

**Developer machine state a client would not have.** A stray Laravel `.env`
supplying `DB_PASSWORD`. A `vendor/` directory present since Week 3. A
Docker volume named for a Week 5 experiment. Each made something work here
that would fail everywhere else.

**Research labels in client-facing paths.** `week6_fixed` hardcoded in the
readiness check and in retrieval. The retrieval one was the worst blocker
of the five rounds: install succeeds, health checks pass, corpus indexes,
token works, and every question returns nothing.

**Bugs created by fixing earlier bugs.** A Makefile that bypassed the
port-conflict fallback documented three days before. Key generation writing
to a file this deployment does not use. nginx holding a stale upstream IP
after a container recreate.

The third category is the one worth remembering. Writing a fix and
verifying a fix are different activities, and skipping the second created
three blockers in a single afternoon.

### v0.4.0 tagged

First version verified the way a client would install it.

### What Path B bought

Chosen 7 September: build the gaps before selling.

Twenty-three days: auth, rate limiting, corpus indexing, HTTPS, backups,
upgrade tooling — and fifteen install blockers plus one security incident
that only surfaced because we installed it as a stranger would.

Under Path A the first client would have met all fifteen. B16 alone would
have had them looking at a system that installed cleanly, passed every
health check, and answered nothing.

### For Day 4
Outreach restart. Product is pilot-ready.

### Time
2.5 hours
# Week 17 — Backup, Upgrade Path, Pilot Rehearsal

## Day 1 (Mon 21 ก.ย.) — Rest day
Energy low. Dropped the 401→500 browser investigation from this week to
make room; impact is limited to mistyped tokens.

## Day 2 (Tue 22 ก.ย.) — Backup and Restore

### Before
Backup was a pg_dump command in the runbook. Never automated, never
restore-tested.

### Design
Database is ~4.5 MB, almost all of it vectors in `documents`. Small enough
for a full nightly dump.

Tables sorted by what losing them costs:
- Critical: users, personal_access_tokens (hashed — cannot be recreated),
  assistant_query_logs, migrations
- Recoverable but costly: documents (re-index needs source files + Voyage spend)
- Disposable: cache, sessions, jobs and friends — schema kept, data excluded

Outside the database and not covered by pg_dump: .env.docker, corpus source
files, caddy_data. Documented explicitly.

### Built
- postgresql16-client in the PHP image — pg_dump was absent; the version
  must match the server's major version
- depot:backup — custom format, excludes disposable table data, verifies
  every dump with pg_restore --list, prunes to the 14 most recent
- depot:restore — lists backups, refuses unreadable files, takes a
  pre-restore snapshot, restores in a single transaction
- scheduler container running schedule:work — without it, the nightly
  backup would be defined and never run
- Nightly schedule at 03:00 Asia/Bangkok

3.0 MB compressed from 4.4 MB. Vectors don't compress well.

### Restore test
Destroyed data three ways: deleted the warehouse-app token, deleted the
depot-v2 corpus, dropped assistant_query_logs entirely.

Confirmed broken: token 401, retrieval 0% hit@1, table gone.

After restore: token 403 (valid again, lacks admin ability), retrieval
100% hit@1 / MRR 1.000, query_logs table back with 16 rows, all 8
migrations Ran.

Retrieval at 100% is the meaningful check — it proves the vectors and
HNSW index came back usable, not just that row counts match.

Gap in the test: Step 1 counts weren't captured before destruction, so
query_logs=16 couldn't be compared against a pre-test figure. The table
coming back with data from a full DROP is still the property being tested.

### Scheduler gap found during design
The stack had no scheduler running. Any scheduled task would have been
silently inert. Found by asking "what actually triggers this at 3am".

### Time
3 hours + 15 min scheduler

## Day 3 (Wed 23 ก.ย.) — Upgrade Path

### The problem
A client on v0.3.2 has no way to know what upgrading to v0.4 requires.
Migration? Rebuild? New env keys? No answer means they stay on the old
version indefinitely.

### Change types found by reading the actual release history
1. Code only — pull and restart
2. Migration — needs `artisan migrate`
3. Dockerfile changed — needs `docker compose build`
4. New service or env key — manual, cannot be automated

Type 4 is what breaks upgrades silently. The operator does not know a key
is missing until something fails at runtime.

### Built
- `config/depot.version` as the single source of truth
- `CHANGELOG.md` with upgrade notes per version, written from the real
  git history of 0.3.0 through 0.4.0
- `depot:upgrade` — reports missing env keys, backs up, migrates, clears
  caches, verifies five dependencies

### The health endpoint had been lying
`/api/health` read `config('app.version')`, which does not exist, and fell
through to a hardcoded `'0.3.0'`. It reported 0.3.0 through both the 0.3.1
and 0.3.2 releases.

Anyone checking the deployed version — including us during a support call —
would have been told the wrong thing.

### The env check paid for itself immediately
First dry run found `APP_DEBUG` missing from `.env.docker`. It was added to
`.env.docker.example` in Week 15 when fixing the stack trace leak, but the
real file never got it.

The container had been running with debug on for eight days, leaking stack
traces in error responses — the exact bug we thought was fixed.

### Rollback is not what it looks like
Tested by rolling back the `doc_id` migration, then re-running it through
`depot:upgrade`.

The column came back. The data did not — `with_doc_id` was 0 across all 103
rows in both corpora.

Restoring the pre-upgrade backup brought all 103 back.

So `migrate:rollback` is not an undo for anything that drops a column.
Documented in CHANGELOG and runbook: roll back by restoring the backup.

### Found while preparing to test
`.env.docker` was untracked but not gitignored — one `git add -A` from
committing live API keys. Fixed.

### Time
3 hours

## Day 5 (Fri 25 ก.ย.) — Fixing what the rehearsal found

### Fixed
B1, B2, B3, B5, B6 plus four README errors. B4 and B7 were handled
yesterday during the incident response.

### The volume migration used the backup tooling for real
Switching pgdata from `external: week-05_pgdata` to a project-scoped
named volume meant starting with an empty database.

depot:backup before, migrate on the new volume, depot:restore after.
All 577 chunks across five sources came back.

The safety backup taken mid-restore was 25 KB — the new database held
only schema at that point. That number is a good sanity check that the
tooling captures what actually exists rather than what you expect.

First time backup and restore solved a real problem instead of a drill.

### README had accumulated contradictions
Beyond the four errors logged yesterday, editing it across several weeks
had left a duplicated feature bullet and, after moving the HTTPS section,
production guidance sitting above the prerequisites.

Rewriting the whole Quick Start rather than patching it was the right
call. Seven steps now, in the order a new operator would need them:
configure, start, migrate and seed, index, create a token, try the UI,
check cost.

### Architecture diagram was two services out of date
It still showed three services. Caddy arrived in Week 16, the scheduler
on Tuesday. Nobody reading the README would have known either existed.

### Still open
- 401→500 browser discrepancy (Week 18)
- Revoked keys remain in git history
- week-05_pgdata kept as a safety net; delete once the new volume has
  proven itself

### Time
3 hours

## Week 17 summary

Mon: rest
Tue: backup and restore, tested destructively (3.25h)
Wed: upgrade path, CHANGELOG, version fix (3h)
Thu: fresh install rehearsal, API key incident (3h)
Fri: fixing the blockers it found (3h)

Total: 12.25 hours

Both Priority 2 gaps closed. Seven install blockers found and six fixed.
One security incident found, contained, and documented.

The week's most valuable three hours were Thursday's — reading the
repository as a stranger. Eight weeks of working inside it had surfaced
none of what that found.

v0.4 tag moves to Monday, after a second fresh-install rehearsal confirms
the fixes work from a clean clone.
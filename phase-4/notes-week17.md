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
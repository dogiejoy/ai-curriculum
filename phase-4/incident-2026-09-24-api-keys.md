# API keys exposed in a public repository

**Date found**: 24 กันยายน 2026
**Exposure window**: 18 สิงหาคม (commit 9c7856d) – 24 กันยายน 2026, 37 days
**Severity**: high — working credentials, public repository
**Outcome**: no unauthorised use detected

## What happened

`.env.docker.example` was committed with live API keys rather than
placeholders:

- Anthropic: `sk-ant-api03-t0Ycq...`
- Voyage: `pa-HOFeFV...`

The file entered the repository in Week 12 Day 2, when the Docker Compose
stack and env pattern were set up. The intent was a template. The actual
keys were pasted in and never replaced.

`laravel-ai-starter` is public. Anyone could clone it and read both keys.

## How it was found

A fresh-install rehearsal — cloning the repository and following the README
as a new user would. The keys were visible in the first `cat` of the template.

Nothing in eight weeks of working on this repository surfaced it. Reading
your own file as its author is not the same as reading it as a stranger.

## Impact

Anthropic usage over the exposure window shows traffic only on 10, 16, and
18 September, matching days we were working, using the models our system
uses. 127,301 input tokens across 30 days — ordinary development volume,
no spike.

No evidence of unauthorised use.

Voyage carries lower financial risk (embeddings at $0.18 per million tokens)
and showed nothing unusual.

## Response

1. Revoked the Anthropic key
2. Revoked the Voyage key
3. Reviewed Anthropic usage across the window
4. Rewrote the template with placeholders
5. Issued new keys and updated `.env.docker`
6. Verified `/api/ready` with the new keys

## Still outstanding

Both keys remain in git history. Anyone who cloned before today can still
read them, though they no longer work. Rewriting history with `git filter-repo`
is possible but was not urgent once the keys were dead.

## What would have caught this earlier

- GitHub secret scanning alerts — worth checking whether one fired and was
  missed
- A pre-commit hook scanning for key patterns
- Reading files as a stranger would, which is what the rehearsal did

## Client implication

Every client install will copy this template. Shipping real keys in it would
have handed our credentials to every client. The template is now the thing
that must never contain a secret.
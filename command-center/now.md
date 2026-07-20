# Current Focus

## Active Objective

Publish the verified 4L sync-entry coordination repair through the separately authorized 4L-R durability and release block.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active.

## Current Work Block

Work block 4L-R Durability And Release — active under Ryan's direct instruction to commit and push to `main`.

## Current Task

Phase 4 Task 1K: locally complete for `P3-3H-02` through `P3-3H-07` plus the remaining `P3-3H-C01` coverage slice; durability and release are in progress.

## Owner

Codex Desktop owns exact-path publication, automatic deployment observation, safe credential-free production checks, and the sanitized closeout. Ryan authorized the direct-main release.

## Current Action

Re-run maintained verification; stage only the exact 4L source set; commit on `codex/sync-entry-coordination`; fast-forward local `main`; push `origin/main`; observe the exact automatic Fly run; verify credential-free `/health` and a missing-bearer `401` at `/plaid/sync-all` without following redirects; then publish one sanitized command-center-only `[skip actions]` closeout.

## Work Block 4L Result

- One stable mode-0600 `DATA_DIR` file provides non-blocking `fcntl.flock` coordination for manual, scheduled, and dashboard-triggered synchronization.
- Same-process separate opens, real two-process contention, normal release, and SIGKILL cleanup pass.
- `/plaid/sync-all` bypasses browser session authentication and normal entity setup, validates bearer first with constant-time comparison, then initializes each entity inside its own exception boundary.
- Unexpected scheduled entity failures are sanitized, structured, and contained so later entities continue and top-level partial/all failure remains truthful.
- Dashboard launch acquires the shared lease first, updates throttle only after successful start, transfers ownership to the worker, and releases without consuming throttle on start failure.
- Dashboard sync now reuses the maintained atomic non-vendor `_sync_entity` path; actual removed-event plus split cleanup, cursor advancement, vendor exclusion, item isolation, and one net Luxe Legacy bridge seam pass.
- The exact `claude-fable-5` max-effort review completed without fallback and its five required in-scope amendments were accepted.

## Release Boundaries

- No PR is required because Ryan explicitly requested a direct push to `main`; force push and recovery outside the exact fast-forward path remain prohibited.
- The safe missing-bearer check may verify the repaired `401` boundary without credentials or a Plaid call. It does not prove a real scheduled sync succeeds.
- Tasks 1L-1P, broader Task 2, Tasks 3-4, `/k/` authentication, shared durable throttle state, migrations, queues, new services, downstream contract changes, and unrelated repairs remain excluded.
- Real databases or financial/payroll/HR rows, uploads, credentials, authenticated production pages, live Plaid, manual workflow actions, non-automatic Fly changes, downstream access/writes, and other external actions remain closed.
- Untracked `scripts/sync_prod_to_local.sh` and unrelated `command-center/now 2.md` remain untouched and unstaged.

## Verification

- Re-run `.venv/bin/python scripts/smoke_test.py`, Python compilation, JSON validation, dashboard refresh, command-center health, `git diff --check`, staged-path review, and staged sensitive-addition scan before publication.
- Attribute the automatic Fly run to the exact source SHA and require success.
- Require production `/health` HTTP 200 and missing-bearer `/plaid/sync-all` HTTP 401 with redirects disabled.
- Require the `[skip actions]` closeout to produce no second Fly run and leave local `main` aligned with `origin/main`.

## Next Report Point

Return source and closeout commits, exact published paths, automatic workflow run and job result, credential-free health and missing-bearer proof, final `main` alignment, preserved exclusions, and the remaining natural scheduled-run observation boundary.

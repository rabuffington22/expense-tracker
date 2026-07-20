# Current Focus

## Active Objective

Run confirmed work block 4M after the first natural scheduled run proves the released 4L path under real schedule conditions.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active.

## Current Work Block

Work block 4M: Vendor Payment Matching Integrity — active and waiting at its natural scheduled-run activation gate before application implementation.

## Current Task

Phase 4 Task 1L.1: restore vendor-payment matching integrity. Ryan confirmed 4M; implementation remains behind the first successful natural scheduled run after source commit `2a12533`.

## Owner

Codex Desktop owns confirmed work block 4M, its local implementation, synthetic verification, and Runway OS closeout. The existing independent read-only monitor owns scheduled-run freshness and failure alerting; Ryan owns any new product, migration, live-action, publication, or recovery decision.

## Current Action

Do not manually dispatch or authenticate `/plaid/sync-all`. Recheck only sanitized public workflow metadata for the first natural schedule event after source commit `2a12533`. If it succeeds, create `codex/vendor-payment-matching-integrity` and begin the confirmed local-only Task 1L.1 implementation; otherwise stop at the exact gate.

## Work Block 4L Result

- One stable mode-0600 `DATA_DIR` file provides non-blocking `fcntl.flock` coordination for manual, scheduled, and dashboard-triggered synchronization.
- Same-process separate opens, real two-process contention, normal release, and SIGKILL cleanup pass.
- `/plaid/sync-all` bypasses browser session authentication and normal entity setup, validates bearer first with constant-time comparison, then initializes each entity inside its own exception boundary.
- Unexpected scheduled entity failures are sanitized, structured, and contained so later entities continue and top-level partial/all failure remains truthful.
- Dashboard launch acquires the shared lease first, updates throttle only after successful start, transfers ownership to the worker, and releases without consuming throttle on start failure.
- Dashboard sync now reuses the maintained atomic non-vendor `_sync_entity` path; actual removed-event plus split cleanup, cursor advancement, vendor exclusion, item isolation, and one net Luxe Legacy bridge seam pass.
- The exact `claude-fable-5` max-effort review completed without fallback and its five required in-scope amendments were accepted.

## Work Block 4L-R Result

- Exact fifteen-path source commit `2a12533` was fast-forwarded and pushed directly to `main` without force.
- Automatic Fly Deploy run `29711640510` and deploy job `88256335090` passed every reported step for exact source SHA `2a12533d637060ce2ea91ff205b30cde3cbbc99a`.
- Credential-free production `/health` returned HTTP 200.
- Missing-bearer `/plaid/sync-all` returned HTTP 401 with redirects disabled, confirming bearer-first behavior without entity initialization or a Plaid call.
- Both preserved untracked files remained untouched and unstaged; the high-confidence staged sensitive-addition scan returned zero.

## Verification

- Maintained synthetic smoke suite, Python compilation, JSON validation, dashboard refresh, command-center health, `git diff --check`, staged-path review, and sensitive-addition scan: pass before publication.
- Automatic Fly run/job attribution and every reported step: pass.
- Production `/health` HTTP 200 and missing-bearer `/plaid/sync-all` HTTP 401 with redirects disabled: pass.
- This command-center-only closeout must produce no second Fly run and must leave local `main` aligned with `origin/main`.

## Next Report Point

Return the first natural post-`2a12533` scheduled-run result without opening logs or response bodies. If green, continue through the confirmed 4M contract, focused and full synthetic verification, cleanup, and local Runway OS closeout. If missing or unsuccessful, stop and report the exact gate without application edits.

# Current Focus

## Active Objective

Publish completed work block 4N through the authorized 4N-R direct-main release path, then restore confirmed 4M at its natural scheduled-run gate.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active.

## Current Work Block

Work block 4N-R: Vendor Line-Item Persistence Durability And Release — active and authorized. Work block 4M remains confirmed and waiting at its natural scheduled-run activation gate.

## Current Task

Phase 4 Task 1L.2 release durability. The implementation is complete locally; exact-path commit, direct-main push, automatic Fly observation, credential-free health, and sanitized closeout are current.

## Owner

Codex Desktop owns authorized work block 4N-R publication, automatic release observation, credential-free health verification, and Runway OS closeout. The existing independent read-only monitor continues to own scheduled-run freshness and failure alerting; Ryan owns any recovery or scope expansion outside the exact release path.

## Current Action

Stage only the exact ten-path 4N set, rerun maintained verification, commit on `codex/vendor-line-item-persistence`, fast-forward and push `main`, observe the exact automatic Fly run, verify credential-free `/health`, and publish a command-center-only `[skip actions]` closeout. Stop on any unexpected path, sensitive addition, divergence, failed check, unattributable deploy, or failed health response.

## Work Block 4N Result

- New Amazon and Henry Schein imports persist each parent and every parser-provided child in one SQLite transaction.
- Parent reimport identity is exact vendor, order ID, and integer-cent total; exact reimports create no child duplicates and existing parents receive no implicit backfill.
- Decimal-to-cents normalization preserves Amazon and Henry item totals and Henry quantities; child or invalid-quantity failure rolls the new parent back.
- Raw vendor category metadata is preserved without inventing Ledger categories; Task 1L.3 still owns deterministic inference and entity-domain enforcement.
- Newly persisted children feed the maintained multi-category auto-split helper without `scripts/populate_line_items.py` once valid categories exist.
- Generated Amazon CSV and Henry Schein XLSX data-layer plus normal preview/save route checks pass across temporary Personal, BFM, and Luxe Legacy databases with denied networking, consumed temporary payloads, unchanged unrelated rows, and exact cleanup.
- Migration 53 was sufficient; no migration, backfill, protected data, retained user file, live action, commit, push, or deployment occurred.

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
- Work block 4N baseline and final full smoke suites, Python compilation, parent/child route handoff, exact reimport, rollback, cents, auto-split, all-entity isolation, denied networking, payload consumption, and cleanup: pass locally.
- Automatic Fly run/job attribution and every reported step: pass.
- Production `/health` HTTP 200 and missing-bearer `/plaid/sync-all` HTTP 401 with redirects disabled: pass.
- The 4N-R command-center-only closeout must produce no second Fly run and must leave local `main` aligned with `origin/main`.

## Next Report Point

Return the 4N source and closeout commits, exact published paths, automatic Fly run and job result, credential-free health, final main alignment, and preserved exclusions. Then restore the first natural post-`2a12533` scheduled-run observation as the unchanged 4M gate without manually dispatching or authenticating.

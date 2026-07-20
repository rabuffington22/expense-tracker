# Current Focus

## Active Objective

Begin confirmed work block 4M now that the first natural scheduled run has proved the released 4L path under real schedule conditions. Work block 4O is complete and verified locally.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active.

## Current Work Block

Work block 4M: Vendor Payment Matching Integrity — active and unblocked for its separately authorized local implementation. Work block 4O is complete and locally verified; work blocks 4N and 4N-R are complete, durable, deployed, and credential-free health verified.

## Current Task

Phase 4 Task 1L.1: restore vendor-payment matching integrity. Ryan confirmed 4M; the first successful natural scheduled run after source commit `2a12533` cleared its activation gate.

## Owner

Codex Desktop owns confirmed work block 4M, its local implementation, synthetic verification, and Runway OS closeout. The existing independent read-only monitor owns scheduled-run freshness and failure alerting; Ryan owns any new product, migration, live-action, publication, or recovery decision.

## Current Action

Create `codex/vendor-payment-matching-integrity` from updated `main` and begin the confirmed local-only Task 1L.1 implementation. Keep release, live actions, and production data access separately gated; do not manually dispatch or authenticate `/plaid/sync-all`.

## Work Block 4O Result

- `categories.md` is authoritative for new in-scope inference and acceptance writes in each entity.
- Vendor inference preserves valid candidates and falls back to `Needs Review` / `General`; empty and `Unknown` subcategories normalize to `General`.
- Henry Schein equal-frequency ties resolve by normalized alphabetical order across tested hash seeds.
- Transaction batches, vendor-order saves, and accepted order matches prevalidate before any transaction, order, note, match, or alias mutation.
- The vendor card no longer offers ad hoc subcategory creation, while the dedicated `Skipped` workflow sentinel remains intact.
- Baseline and final smoke, focused all-entity valid/invalid and zero-mutation cases, denied networking, exact cleanup, compilation, JSON, whitespace, dashboard, and health checks pass.
- No taxonomy, migration, historical-row action, protected data, live system, commit, push, or deployment occurred.

## Work Block 4N Result

- New Amazon and Henry Schein imports persist each parent and every parser-provided child in one SQLite transaction.
- Parent reimport identity is exact vendor, order ID, and integer-cent total; exact reimports create no child duplicates and existing parents receive no implicit backfill.
- Decimal-to-cents normalization preserves Amazon and Henry item totals and Henry quantities; child or invalid-quantity failure rolls the new parent back.
- Raw vendor category metadata is preserved without inventing Ledger categories; Task 1L.3 still owns deterministic inference and entity-domain enforcement.
- Newly persisted children feed the maintained multi-category auto-split helper without `scripts/populate_line_items.py` once valid categories exist.
- Generated Amazon CSV and Henry Schein XLSX data-layer plus normal preview/save route checks pass across temporary Personal, BFM, and Luxe Legacy databases with denied networking, consumed temporary payloads, unchanged unrelated rows, and exact cleanup.
- Migration 53 was sufficient; no migration, backfill, protected data, retained user file, live action, commit, push, or deployment occurred.

## Work Block 4N-R Result

- Exact ten-path source commit `89236a6` was fast-forwarded and pushed directly to `main` without force.
- Automatic Fly Deploy run `29714030248` and deploy job `88263334817` passed every reported step for exact source SHA `89236a62438c4c5063aedf6c276f0ae52fafcfbe`.
- Credential-free production `/health` returned HTTP 200.
- Both preserved untracked files remained untouched and unstaged; the high-confidence staged sensitive-addition scan returned zero.

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

## 4M Activation Gate Result

- The first natural post-`2a12533` scheduled run was `29740509073`, created at `2026-07-20T11:59:33Z`.
- Workflow `256886458` was `active`; the scheduled run completed with conclusion `success`.
- Freshness and incomplete-run thresholds passed using sanitized public metadata only.
- The 4M activation gate is cleared; no remediation, workflow action, Plaid call, or financial-system mutation was attempted.

## Verification

- Maintained synthetic smoke suite, Python compilation, JSON validation, dashboard refresh, command-center health, `git diff --check`, staged-path review, and sensitive-addition scan: pass before publication.
- Work block 4N baseline and final full smoke suites, Python compilation, parent/child route handoff, exact reimport, rollback, cents, auto-split, all-entity isolation, denied networking, payload consumption, and cleanup: pass locally.
- Automatic Fly run/job attribution and every reported step: pass.
- Production `/health` HTTP 200 and missing-bearer `/plaid/sync-all` HTTP 401 with redirects disabled: pass.
- This command-center-only closeout must produce no second Fly run and must leave local `main` aligned with `origin/main`.

## Next Report Point

Create the confirmed 4M implementation branch from updated `main`, then complete its focused and full synthetic verification, cleanup, and local Runway OS closeout. Keep publication and live actions as separate decisions. Work block 4O is complete locally, and its publication remains a separate decision.

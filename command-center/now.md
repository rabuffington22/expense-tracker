# Current Focus

## Active Objective

Publish the verified work block 4P source set directly to `main`, observe the resulting automatic Fly deployment, verify credential-free production health, and publish a sanitized skip-actions closeout. No 4Q implementation is authorized.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active.

## Current Work Block

Work block 4P-R: Payroll Import Integrity Durability And Release — active under Ryan's direct commit-and-push instruction. Work block 4P is complete and verified locally on `codex/payroll-import-integrity`.

## Current Task

Phase 4 Task 1M.4: validate employee roster writes atomically — held at its separate planning gate while 4P-R publishes the completed Tasks 1M.1-1M.3 work. Task 1M.5 remains planned, and no 4Q implementation is authorized.

## Owner

Codex Desktop owns the exact-path 4P-R commit, direct-main fast-forward push, automatic deployment observation, credential-free health verification, and sanitized closeout. Ryan owns any recovery, scope expansion, protected-data, or live-system decision and the later Task 1M.4 confirmation.

## Current Action

Re-run maintained verification, stage only the exact 4P set, commit on `codex/payroll-import-integrity`, fast-forward local `main`, push `origin/main`, observe the attributable automatic Fly run, verify credential-free `/health`, and publish a command-center-only `[skip actions]` closeout. Stop on any divergence or failed check.

## Work Block 4M-R Result

- Exact ten-path source commit `ffd42dd` was fast-forwarded and pushed directly to `main` without force.
- Automatic Fly Deploy run `29748373589` and deploy job `88372068257` passed every reported step for the exact source SHA.
- Credential-free production `/health` returned HTTP 200.
- Both preserved untracked files remained untouched and unstaged; the staged high-confidence sensitive-addition scan returned zero.
- No protected data, credential, authenticated production page, live vendor/Plaid call, manual workflow action, non-automatic Fly change, downstream access/write, migration, backfill, force push, or unrelated action occurred.
- This command-center-only closeout uses `[skip actions]` so it must not start a second Fly deployment.

## Work Block 4M Result

- `vendor_transactions.matched_transaction_id` is the canonical one-bank-to-one-vendor relationship; nonexistent `transactions.matched_order_id` is no longer queried or written.
- Matching and accepted applications serialize through SQLite `BEGIN IMMEDIATE`; stale, duplicate, missing, and already-claimed relationships reject without unrelated mutation.
- Exact matches still auto-apply, likely and loose candidates remain reviewable, and successful application changes only the selected bank merchant/notes plus the selected vendor relationship/confidence.
- Fresh Personal, BFM, and Luxe Legacy databases pass exact, review, unmatched, accepted, stale, duplicate, real two-thread claim, forced rollback, entity-isolation, denied-network, and exact-cleanup checks.
- Baseline and final maintained smoke suites and Python compilation pass. `core/db.py` is unchanged; no migration or backfill was needed.
- No real database, financial row, credential, application-integration request, live vendor/Plaid action, workflow action, Fly action, downstream access, commit, push, PR, merge, or deployment occurred.

## Work Block 4O Result

- `categories.md` is authoritative for new in-scope inference and acceptance writes in each entity.
- Vendor inference preserves valid candidates and falls back to `Needs Review` / `General`; empty and `Unknown` subcategories normalize to `General`.
- Henry Schein equal-frequency ties resolve by normalized alphabetical order across tested hash seeds.
- Transaction batches, vendor-order saves, and accepted order matches prevalidate before any transaction, order, note, match, or alias mutation.
- The vendor card no longer offers ad hoc subcategory creation, while the dedicated `Skipped` workflow sentinel remains intact.
- Baseline and final smoke, focused all-entity valid/invalid and zero-mutation cases, denied networking, exact cleanup, compilation, JSON, whitespace, dashboard, and health checks pass.
- No taxonomy, migration, historical-row action, protected data, or live vendor/Plaid action occurred.

## Work Block 4O-R Result

- Exact seventeen-path source commit `5529912` was fast-forwarded and pushed directly to `main` without force.
- Automatic Fly Deploy run `29745531202` and deploy job `88362414145` passed every reported step for exact source SHA `5529912b47003a931a33776f6ad24fe327257e25`.
- Credential-free production `/health` returned HTTP 200.
- Both preserved untracked files remained untouched and unstaged; the high-confidence staged sensitive-addition scan returned zero.
- The sanitized command-center-only closeout uses `[skip actions]` so it must not start a second deployment.

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
- Work block 4O source commit, automatic Fly run/job, and credential-free production `/health`: pass.
- Work block 4M baseline and final full smoke suites, Python compilation, all-entity vendor-payment matrix, two-thread contention, rollback, denied networking, and cleanup: pass locally.
- Final JSON validation, dashboard refresh, command-center health, `git diff --check`, dashboard inspection, and explicit worktree review: pass locally.

## Next Report Point

Report the completed 4P contract, exact changed paths, matching and creation behavior, payload and workbook matrix, full verification, cleanup, local-only branch state, preserved exclusions, and the recommended 4Q planning boundary.

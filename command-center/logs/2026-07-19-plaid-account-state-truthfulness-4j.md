# Work Block 4J — Plaid Reconciliation, Liability, And Freshness Truthfulness

Date: 2026-07-19

Status: complete and locally verified; release not authorized

## Scope

Completed Phase 4 Task 1I plus only the matching primary-Plaid slice of Task 2 for `P3-3G-02`, `P3-3G-03`, `P3-3G-04`, `P3-3G-05`, and focused `P3-3G-C01` coverage.

No real database, financial/payroll/HR row, upload, credential, authenticated production page, production/demo surface, live Plaid call, workflow, Fly action, downstream access/write, GitHub durability, deployment, Task 1J behavior, or other external action was used. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched and unstaged.

## Implemented Contract

- Added additive migration 58 with nullable `plaid_items.accounts_last_synced` and `plaid_items.liabilities_last_synced` markers.
- Replaced entity-wide balance freshness with independent per-item account freshness.
- Reconciled cached Plaid account rows only after that item's successful response.
- Preserved failed-item rows and markers while allowing successful siblings to reconcile.
- Removed authoritative disabled, investment, and removed accounts even when the successful item's keep set is empty.
- Preserved all manual rows during reconciliation.
- Removed the first-word institution/account-name deletion heuristic from Plaid Link; manual rows now require a future explicit stable placeholder identity or user-confirmed merge.
- Separated liability freshness from balance freshness, preserved last-known-good values and markers on failure, and advanced liability freshness after successful empty responses without clearing cached fields.
- Invalidated both item freshness markers when an account is enabled or disabled.

The sanitized source contract is `command-center/plaid-account-state-contract.md`.

## Maintained Verification

The baseline smoke suite passed before implementation. The final maintained suite passed after implementation with a new 4J section containing ten focused check groups, exercised once for the populated migration plus nine times across each of Personal, BFM, and Luxe Legacy for 28 focused assertions in total.

The maintained proof covers:

- populated schema-57 to schema-58 upgrade with the existing Plaid item preserved and both new markers null;
- per-item successful balance refresh and failed-sibling preservation;
- disabled, investment, removed, and all-disabled empty-keep-set cleanup;
- manual-row preservation and fresh-sibling cache isolation;
- normal liability application after balance refresh;
- liability failure preserving last-known-good values and the prior marker;
- successful empty liability response advancing its marker without clearing fields;
- account-toggle invalidation of both freshness markers;
- successful similar-name link preservation and rollback after a later failed account fetch;
- temporary Personal, BFM, and Luxe Legacy databases, fake tokens, mocked Plaid functions, denied outbound sockets, entity isolation, and exact synthetic cleanup.

The full suite also retained transaction identity, route, planning, payroll, downstream-selection, scheduled-result, transaction/cursor atomicity, export, recurring-report, saved-view, To Do, authentication, CSRF, and protected-cache coverage.

## Verification Result

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass.
- Python compilation for `core/db.py`, `web/routes/cashflow.py`, `web/routes/plaid.py`, and `scripts/smoke_test.py`: pass.
- Populated additive migration and exact temporary cleanup: pass.
- `jq empty command-center/state.json`: pass.
- `git diff --check`: pass.
- Dashboard refresh and command-center health check: required at final Runway OS closeout.

## Finding Disposition

- `P3-3G-02`: resolved locally; release pending.
- `P3-3G-03`: resolved locally; release pending.
- `P3-3G-04`: resolved locally; release pending.
- `P3-3G-05`: resolved locally; release pending.
- `P3-3G-C01`: account reconciliation, liability, freshness, toggle, link, all-entity, denied-network, migration, and cleanup slice complete; missing-modification observability, corrupt-token isolation, and remaining primary-Plaid coverage stay with Task 1J.

## Durability And Next Gate

The verified implementation remains local-only on `codex/plaid-account-truthfulness`. Commit, push, PR, merge, deployment, protected data, credentials, live Plaid, workflows, Fly, downstream access/write, and every other live action require separate authorization.

The next implementation candidate is a separately planned and confirmed 4K block for Task 1J Plaid item isolation and truthful observability. It is not authorized by this closeout.

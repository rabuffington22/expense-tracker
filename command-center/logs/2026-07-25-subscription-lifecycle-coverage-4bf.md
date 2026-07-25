# Work Block 4BF: Subscription Detection And Lifecycle Regression Coverage

Date: 2026-07-25

Status: complete and verified locally; uncommitted and not published

## Confirmed Scope

Phase 4 Task 1P.7.3 plus only its focused Task 2 / `P3-3C-C01` regression slice.

## Maintained Coverage

Section 8k of `scripts/smoke_test.py` now uses the existing temporary synthetic `DATA_DIR` to prove:

- all five supported cadence classes and the unsupported interval gap;
- regular versus irregular amount histories;
- route-level weekly, biweekly, monthly, quarterly, and annual suggestions in Personal, BFM, and Luxe Legacy;
- staleness, excluded merchant text, excluded categories, and positive-income filtering;
- empty watchlist rendering in all three entities;
- suggestion acceptance and removal from detection;
- manual watchlist addition;
- detail reconciliation for cadence, charge history, payment method, timeline, and deterministic local cancellation-tip metadata;
- status and notes updates with timeline persistence;
- account-information append ordering and deletion;
- share text with entity-local amount, payment method, account information, tips, notes, and recent charges;
- dismiss and restore;
- watchlist deletion with account-information and timeline cascades;
- reopened-connection persistence;
- entity-local output and write isolation;
- denied outbound networking; and
- exact restoration of synthetic transactions, four subscription tables, and every affected SQLite sequence.

## Verification

- Baseline full `.venv/bin/python scripts/smoke_test.py`: passed.
- Final full `.venv/bin/python scripts/smoke_test.py`: passed, including new section 8k.
- `.venv/bin/python -m py_compile scripts/smoke_test.py web/routes/subscriptions.py core/db.py`: passed.
- `git diff --check`: passed.
- Temporary database snapshot and SQLite-sequence restoration assertions: passed for Personal, BFM, and Luxe Legacy.
- Denied-network assertions: passed.

## Findings

The maintained subscription contract matched the original 3C audit evidence. No product defect, ambiguous entity contract, repair need, migration, dependency, browser/PWA change, or real AI requirement was found.

## Changed And Preserved Boundaries

Maintained coverage changed only in `scripts/smoke_test.py`. This sanitized log, Runway OS sources, and the generated dashboard changed for closeout. Product source, dependencies, migrations, authentication, browser/PWA behavior, workflows, and deployment files did not change.

No real database, financial row, upload, credential, protected data, OpenRouter/Plaid call, production/demo/Fly access, downstream system, GitHub action, commit, push, PR, merge, or deployment occurred.

The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log were not edited, staged, deleted, or absorbed.

## Next Gate

Work remains local-only and uncommitted on `codex/subscription-lifecycle-coverage`. Exact-scope 4BF-R durability requires separate authorization. If publication is parked, Task 1P.7.4 requires a separately proposed and confirmed 4BG Cash Flow coverage block.

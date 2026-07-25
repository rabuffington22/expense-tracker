# Work Block 4BE — Financial Read-Model Reconciliation And Export Coverage

Date: 2026-07-24

Status: complete and verified locally; uncommitted

Branch: `codex/financial-read-model-planning`

## Scope

Work block 4BE covered Tasks 1P.7.1-1P.7.2 and only their focused Task 2 regression slice:

- effective-transaction split replacement, centralized exclusions, signed totals, and dashboard reconciliation;
- dashboard date, account, transfer, review, empty, and entity-identity behavior;
- every non-recurring standard report through direct preparation and rendered view;
- CSV, PDF, supported transaction QBO, non-transaction QBO rejection, filenames, content types, and missing/empty inputs;
- Personal, BFM, and Luxe Legacy isolation, denied outbound networking, read-only preservation, and exact cleanup.

Tasks 1P.7.3-1P.7.4, CI, publication, product repair, migrations, dependencies, browser/PWA work, authentication, protected data, real databases, external/live actions, Plaid, downstream systems, GitHub, workflows, Fly, and deployment remained excluded.

## Result

The maintained smoke suite now creates one isolated two-month effective-ledger fixture for each entity. It proves that one split parent becomes exactly two effective pieces, excluded transfer and income categories remain out of spending summaries, signed direct and account totals reconcile, and dashboard counts, spend, income, net, review count, account filtering, and explicit transfer inclusion match the same fixture.

The same fixture covers Transactions, Category Summary, Merchant Summary, Month-over-Month, Income vs Expenses, Tax Summary, and Account Summary through raw helpers, prepared output, rendered views, CSV, and PDF. Transactions also pass QBO output while every unsupported report type rejects QBO. Stable columns, pivot months, entity-keyed filenames, content types, missing ranges, empty ranges, entity isolation, and response behavior are maintained. The separate 4H Recurring Charges matrix remains unchanged and passing.

The first focused run corrected an assertion that expected a merchant in a dashboard partial that now defers its detail panels. The second corrected cleanup to restore SQLite's synthetic split autoincrement counter. Both were test-harness assumptions; all product calculations and routes passed, and no product repair was needed.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: passed.
- Final `.venv/bin/python scripts/smoke_test.py`: passed end to end.
- `.venv/bin/python -m py_compile scripts/smoke_test.py`: passed.
- Focused all-entity split, signed-total, dashboard, report, rendered-view, CSV, PDF, QBO, input-boundary, isolation, denied-network, read-only, and cleanup assertions: passed inside section 8j.
- Synthetic Personal, BFM, and Luxe Legacy database snapshots were unchanged after read paths and exactly restored after cleanup.
- `git diff --check`: passed.
- JSON validation, dashboard refresh, command-center health, generated-state review, and rendered localhost inspection: passed after closeout.

## Changed And Preserved Boundaries

Maintained coverage changed only in `scripts/smoke_test.py`. This sanitized log, Runway OS sources, and the generated dashboard changed for closeout. Product source, dependencies, migrations, authentication, browser/PWA behavior, workflows, and deployment files did not change.

The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log were not edited, staged, deleted, or absorbed.

Work remains local-only and uncommitted. Exact-scope durability/publication requires a separately authorized 4BE-R block. If publication is parked, Task 1P.7.3 requires a separately confirmed 4BF planning and implementation block.

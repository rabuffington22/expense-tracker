# Work Block 4K — Plaid Item Isolation And Truthful Observability

Date: 2026-07-19

Scope: Phase 4 Task 1J, `P3-3G-06`, `P3-3G-07`, and only the matching item-isolation and observability slice of `P3-3G-C01`.

Status: complete and verified locally; release not authorized.

## Contract And Implementation

- Added `command-center/plaid-item-isolation-observability-contract.md` before implementation.
- Moved access-token decryption inside each primary Plaid item's exception boundary.
- A corrupt token now produces `access token unavailable` under the item's institution label, makes no Plaid request, and cannot abort healthy sibling items.
- All otherwise unexpected item exceptions return the stable sanitized `item sync failed` message; persistence failures retain the already-safe `transaction persistence failed; cursor unchanged` contract.
- Modified events now require exactly one affected stored transaction. A missing or ambiguous target fails and rolls back the complete item transaction, including any earlier additions, while preserving the starting cursor and `last_synced`.
- Modified and removed totals now use SQLite affected-row counts.
- Removal split cleanup now covers every matching transaction ID. Already-absent removals remain zero-count idempotent successes and may commit the new cursor.
- Primary items now run in a deterministic created-time/item-ID order so both before-and-after sibling cases are explicit and reproducible.

## Maintained Synthetic Proof

The expanded smoke suite runs 36 focused assertions across temporary Personal, BFM, and Luxe Legacy databases:

- corrupt token before a healthy sibling;
- corrupt token after a healthy sibling;
- no Plaid request for the corrupt token;
- sanitized errors without encrypted or decrypted token material;
- unchanged failed-item cursor and timestamp;
- healthy-sibling transaction and cursor commit;
- missing-modification rollback after an earlier addition;
- successful sibling continuation beside the missing modification;
- actual modified and removed row counts;
- split cleanup for a real removal;
- already-absent removal redelivery with zero count and cursor advancement; and
- exact cleanup of every synthetic item, account, transaction, split, and temporary database.

Outbound sockets were denied throughout the focused paths. Fake tokens and mocked Plaid results were used; no credential, protected database, financial row, production/demo surface, live Plaid call, workflow, Fly action, or downstream access occurred.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: passed before implementation.
- Post-implementation `.venv/bin/python scripts/smoke_test.py`: passed with the new 8g maintained section.
- `.venv/bin/python -m py_compile web/routes/plaid.py scripts/smoke_test.py`: passed.
- Temporary synthetic data and databases: cleaned by the maintained suite.
- `jq empty command-center/state.json`: passed before and after dashboard refresh.
- `node command-center/scripts/refresh-dashboard.js`: passed.
- `node command-center/scripts/health-check.js`: passed.
- `git diff --check`: passed; new-file whitespace and final explicit-path worktree checks also passed.
- Generated dashboard: visually inspected at localhost; Phase 4 shows 4K done, Task 1J current under Ryan for the release decision, and 4K-R as the next gated move.

## Preserved Boundaries

- No schema or migration change.
- No automatic retry or implicit reconstruction of a missing modification.
- No Task 1K scheduled/public coordination, `/k/`, cross-process lock, entity-level recovery, downstream, or unrelated repair work.
- No commit, push, PR, merge, deployment, protected-data access, credential use, live system, workflow, Fly, or downstream action.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated `command-center/now 2.md` remained untouched and unstaged.

## Result

`P3-3G-06` and `P3-3G-07` are resolved locally. Their focused `P3-3G-C01` coverage slice is maintained. Work block 4K is ready to close locally, while durability and release remain a separate Ryan decision.

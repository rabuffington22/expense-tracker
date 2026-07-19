# Work Block 4G — Scheduled Sync Result Truthfulness

Date: 2026-07-19

Status: complete and verified locally

## Scope

Implemented Phase 4 Task 1F and only the workflow-visible result slice of Task 2, limited to `P3-3H-01` and the matching slice of `P3-3H-C01`.

No workflow file, entity exception isolation, cross-process coordination, Plaid persistence, cursor behavior, public worker, authentication/setup ordering, migration, protected data, credential, real database, production/demo, external integration, GitHub durability, deployment, or live action was included.

## Result Contract

- Every entity result with an empty `errors` list, including an error-free skipped entity, returns HTTP 200 with top-level `ok: true` and `status: success`.
- One or more failed entities alongside at least one error-free entity returns HTTP 502 with `ok: false` and `status: partial_failure`.
- Errors in every entity result return HTTP 502 with `ok: false` and `status: failure`.
- The existing per-entity `results` payload is preserved without adding or widening error details.
- Existing missing/wrong bearer, missing configuration, contention, uncaught exception, lock-release, and configured entity-order behavior remains unchanged.

## Maintained Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass.
- Python compilation for `web/routes/plaid.py` and `scripts/smoke_test.py`: pass.
- Complete success, error-free skip, partial failure, all-entity failure, absent/wrong bearer, missing sync/Plaid configuration, contention, uncaught exception, lock release, entity order, per-entity result preservation, and secret-safe output: pass.
- Actual `curl --fail` against a localhost-only mocked partial-failure response: exit 22 as required.
- The tracked workflow still contains the existing `curl --fail` contract and was not edited or executed.
- Outbound sockets were denied during mocked route checks; Plaid and downstream seams were not invoked.
- Disposable smoke root removal, `git diff --check`, JSON validation, dashboard refresh, and command-center health: pass.

## Preserved Boundaries

Authorization-before-entity-setup remains `P3-3H-06`. Entity exception isolation, cross-process coordination, public `/k/` synchronization, cursor/removal behavior, vendor-item scope, failed-launch throttling, broader entry-point coverage, workflow mutation/execution, real data, credentials, Plaid, downstream access/writes, Fly, commit, push, PR, merge, and deployment remain separately gated.

Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched and unstaged.

## Learning

The scheduled route already had enough structured entity information to fix workflow truthfulness without changing sync execution. A narrow aggregation layer is sufficient: nested errors now become a failing HTTP result, while successful and intentionally skipped entities keep their existing meaning. The larger sync-entry family remains independent and can proceed after the planned primary-Plaid blocks without weakening daily failure visibility in the meantime.

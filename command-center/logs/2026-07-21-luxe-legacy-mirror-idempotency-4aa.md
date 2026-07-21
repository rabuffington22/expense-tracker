# Work Block 4AA — Luxe Legacy Mirror Key Validation And Explicit Idempotency

Date: 2026-07-21

Status: complete and verified locally; publication not authorized

## Scope

Implemented Tasks 1O.2-1O.4 only: malformed and duplicate mirror-key rejection, explicit `plaid_transaction_id` PostgREST conflict semantics, and the remaining maintained synthetic downstream-mirror coverage. No migration, downstream-repository change, deployed-schema inspection, live downstream request, protected-data access, credential access, GitHub durability, workflow, Fly action, or deployment occurred.

## Result

- The bridge keeps SQL `NULL` identifiers outside selection and rejects selected empty, whitespace-only, or whitespace-padded identifiers without rewriting Ledger rows.
- Exact repeated valid keys are counted deterministically and every row in the repeated group is withheld. Unrelated valid unique rows continue in stable key and Ledger-transaction order.
- Sanitized warnings contain only malformed-row, duplicate-row, and duplicate-key counts.
- An invalid-only selection returns zero without HTTP.
- Requests explicitly send `on_conflict=plaid_transaction_id` together with `Prefer: resolution=merge-duplicates` and the existing 15-second timeout.
- Success returns the number of valid unique rows sent. Downstream failure remains isolated, returns zero, and leaves all entity databases unchanged.
- README and the maintained contract now describe the local bridge behavior.

## Verification

- Baseline full `.venv/bin/python scripts/smoke_test.py`: passed before implementation.
- Final full `.venv/bin/python scripts/smoke_test.py`: passed after implementation and regression correction.
- Maintained section 8c covers absent/partial configuration, invalid-only no-request behavior, mixed null/malformed/duplicate/excluded/valid rows, deterministic repeat payloads, exact request path and headers, explicit conflict parameter and preference, timeout, sanitized warnings, failure isolation, Personal/BFM/Luxe Legacy preservation, scheduled/public LL-only invocation, denied sockets, and exact cleanup.
- `.venv/bin/python -m py_compile core/luxury_bridge.py scripts/smoke_test.py`: passed.
- `git diff --check`: passed.
- JSON validation, dashboard refresh, command-center health, rendered inspection, and final worktree review are part of the Runway OS closeout.

## Verification Finding

The first expanded request-header assertion exposed a local implementation regression before closeout: the initial validation loop reused the service-key variable name for a row identifier. That would have placed the last selected transaction ID in the synthetic authorization headers. The variables were separated into `service_key` and `plaid_key`, the assertion then passed, and the complete smoke suite was rerun successfully. No live request occurred.

## Preserved Boundaries

- Only synthetic temporary databases and fake configuration values were used.
- HTTP was mocked and outbound sockets were denied.
- No real row data, credential value, local production database, upload, backup, or external service was accessed.
- No source database row was changed by the bridge and all test data was cleaned exactly.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.
- The downstream repository was not accessed or changed in 4AA.
- No commit, push, PR, merge, workflow, Fly action, deployment, or other live action occurred.

## Next Gate

Work block 4AA-R may publish the exact verified local source set only if Ryan separately authorizes that durability and automatic-release scope. Otherwise the next planning pass begins Task 1P as a separate subsystem and risk class.

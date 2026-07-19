# Work Block 4I — Plaid Transaction Sync Atomicity

Date: 2026-07-19

Status: complete and locally verified; release not authorized

## Outcome

The primary Plaid sync applies each item's accepted additions, modifications, removals, final cursor, and `last_synced` in one SQLite transaction. Exact redelivery remains an explicit idempotent no-op. Genuine persistence errors now propagate to the existing item error path instead of being returned as duplicates, and caller-visible counters are added only after the item transaction commits.

Any add, categorization, modify, remove, split-delete, or cursor-write failure rolls back the complete item update. The stored cursor and timestamp remain unchanged, partial additions disappear, existing rows and splits remain intact, and the next attempt begins from the original stored cursor.

## Maintained Verification

- Baseline smoke suite: pass.
- Final smoke suite: pass.
- Mocked two-page Plaid aggregation and final cursor: pass.
- Successful add, modify, remove, cursor/timestamp commit, negative-debit sign, enabled-account filtering, and unrelated-row preservation across Personal, BFM, and Luxe Legacy: pass.
- Exact redelivery and cursor advancement without duplication across all three entities: pass.
- Forced add, modify, remove, and cursor-write failures across all three entities: twelve rollback paths passed.
- Retry after each forced failure from the original stored cursor: twelve paths passed.
- Removed-row split preservation on failure: pass.
- Outbound socket denial and temporary all-entity database isolation: pass.
- Exact synthetic item, account, transaction, split, upload, backup, WAL/SHM, and temporary-root cleanup: pass.
- Python compilation, `jq empty`, `git diff --check`, dashboard refresh, and command-center health: pass.

## Boundaries

No migration, real database, financial/payroll/HR row, upload, credential, production/demo access, live Plaid call, workflow action, Fly action, downstream access/write, automatic retry policy, reconciliation, liability, freshness, missing-modification observability, item isolation, scheduled/public coordination, commit, push, PR, merge, or deployment occurred. Untracked `scripts/sync_prod_to_local.sh` and unrelated `command-center/now 2.md` remained untouched and unstaged.

## Next Gate

Task 1H and `P3-3G-01` are complete locally, with only the atomicity slice of `P3-3G-C01` consumed. Publication requires a separate Ryan authorization. Task 1I is next for a separately planned Plaid reconciliation, liability, and freshness block.

## Learning

The cursor bug did not require a schema change or a new Plaid retry mechanism. The existing architecture already fetched every page before writing locally; the failure came from collapsing database errors into duplicate no-ops and incrementing counters before commit. Making the item transaction and its result boundary explicit closes the permanent-omission path while preserving the existing identity and pagination design.

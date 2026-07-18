# Work Block 3G — Mocked Primary Plaid Boundary Audit

Date: 2026-07-18

Status: complete with findings

## Scope

Audited Tasks 5A-5B using tracked source, the existing synthetic smoke suite, deterministic mocked Plaid responses, fake token values, outbound-socket denial, and temporary Personal, BFM, and Luxe Legacy databases.

No real database, balance, transaction, financial row, credential, Plaid token, production/demo surface, network call, workflow, Fly action, downstream write, authentication change, product repair, tracked-test change, or GitHub mutation was used. The temporary probe file and every audit-created database, WAL/SHM file, upload directory, and backup directory were removed.

## Verification Summary

- Existing tracked smoke suite: passed.
- Primary mocked probe: 44 passes, 12 controlled failures, zero unexpected failures, 56 total checks.
- Deterministic confirmation pass: reproduced the same 12 controlled failures and cleanup result.
- Temporary audit root removal: passed on both complete runs.
- Outbound network boundary: socket connection paths were blocked; all Plaid SDK, exchange, account, sync, disconnect, balance, and liability responses were mocked.

## Behavior Matrix

| Area | Result | Evidence |
| --- | --- | --- |
| Token encryption | Pass | Synthetic token persisted with `enc:` ciphertext and decrypted only with the synthetic Flask secret. |
| Client configuration | Pass | Missing credentials and invalid `PLAID_ENV` failed before network access. |
| SDK pagination | Pass | Two mocked transaction pages aggregated and returned the final cursor. |
| Link/exchange persistence | Pass with defect | Item and account rows were entity-local and encrypted, but the first-word cleanup removed an unrelated manual account. |
| Toggle and rename | Pass | Enabled state and display name changed only in the selected entity; linked cash-flow name followed the alias. |
| Disconnect | Pass | Mocked remote removal ran once; item, accounts, and linked balances were removed while transactions remained with the item link cleared. |
| Balance refresh | Pass with defects | Normal enabled-account refresh and manual-row preservation passed; disabled-only and partial-failure reconciliation plus mixed-freshness caching failed. |
| Liability propagation | Defect | A normal balance refresh wrote fresh timestamps before the liability staleness check, so liabilities and payment fields were not fetched or applied. |
| Incremental add/modify/remove | Pass | All three entities preserved sign, enabled-account filtering, normal modifications, removals, cursor movement, review categorization, and storage isolation. |
| Exact Plaid re-delivery | Pass | Re-delivery of the same Plaid transaction remained idempotent. |
| Distinct Plaid identity | Defect | Two different Plaid IDs with identical date, amount, and merchant collapsed to one transaction row. |
| Persistence failure handling | Defect | A forced SQLite insert failure was swallowed as a zero insert and the cursor advanced past the missing row. |
| Missing modified row | Defect | A modified event targeting no row was still counted as one update. |
| Corrupt token isolation | Defect | One corrupt encrypted item token aborted the entity before a valid sibling item could sync. |
| Tracked regression coverage | Gap | The maintained smoke suite renders `/plaid/` but does not guard connection, account, balance, liability, transaction-sync, cursor, or failure behavior. |

## Ranked Findings

### High — Persistence failures can advance the Plaid cursor past missing data

`_upsert_plaid_transaction()` catches every exception and returns `0`, the same result used for a duplicate. A synthetic SQLite trigger forced a write failure; `_sync_entity()` reported no error and committed the new cursor without the transaction. Acceptance requires distinguishing duplicates from persistence errors, rolling back or withholding the cursor on any write failure, and tracking the behavior synthetically.

### High — Distinct Plaid transactions can collapse under the generic identity hash

Two transactions with different Plaid IDs and accounts but identical date, amount, and merchant produced one primary key and one stored row. This confirms the Task 1 identity defect on the Plaid ingestion path. Acceptance requires preserving stable Plaid identity while retaining exact re-delivery idempotency and defining a safe migration for existing relationships.

### High — Partial balance refresh can delete the failed item's cached account rows

When one item refreshed successfully and a sibling item raised, the successful account IDs became the global keep-set and the failed item's existing Plaid balance row was deleted. When every account was disabled, the empty keep-set skipped deletion and retained the disabled row. Acceptance requires per-item reconciliation that never treats an API failure as authoritative absence and removes disabled/stale rows consistently.

### High — Normal cash-flow refresh skips liability details

`_load_entity_section()` refreshes account balances first. That writes a current `updated_at`; `_fetch_plaid_liabilities()` then uses the same timestamp as its staleness guard and returns without calling the liability client. The mocked normal path therefore never applied minimum payment or due date. Acceptance requires separate freshness state or one coordinated response so balance refresh cannot starve liability refresh.

### High — Link exchange can delete unrelated manual account state

The exchange route removes every manual balance whose first word matches the institution or a connected account. Linking synthetic Chase data deleted a distinct manual `Chase Emergency Reserve` balance. Acceptance requires explicit placeholder identity or exact user confirmation; unrelated manual rows must survive linking.

### Medium — Entity-wide maximum freshness hides stale accounts

The balance cache checks `MAX(updated_at)`. One fresh account suppressed the API refresh even while a sibling row was two hours old. Acceptance requires item/account-specific freshness or an entity refresh timestamp that can only be fresh after a complete successful reconciliation.

### Medium — Missing modified transactions are reported as updated

The modified counter increments without checking SQLite row count. A missing Plaid ID reported one update with no stored change, which can conceal the downstream effect of identity collisions. Acceptance requires zero-row updates to become an explicit error or recovery path rather than success.

### Medium — One corrupt token aborts the entire entity sync

All item tokens are decrypted before the per-item exception boundary. A corrupt synthetic ciphertext raised before the valid sibling item ran. Acceptance requires per-item decryption and sanitized error reporting so healthy items continue while the failed item is visible.

### Medium — Primary Plaid paths lack tracked regression coverage

The passing and failing evidence is ephemeral. Acceptance requires maintained synthetic tests for token/item persistence, account lifecycle, balance/liability reconciliation, incremental ingestion, pagination, deduplication, cursor safety, item failure isolation, and three-entity boundaries without credentials or network calls.

## Preserved Boundaries

- Tasks 5C-5D and 6-8 were not executed.
- The scheduled `/plaid/sync-all`, public `/k/` background-sync execution, and Luxe Legacy downstream request contract were not audited beyond the source seams necessary to exclude them.
- No repair, migration, tracked fixture/test/demo edit, or application source change occurred.
- No real secrets or row-level financial information entered the audit log or command center.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Next Readiness

Task 5C is ready for a separately confirmed work block 3H. Its audit should use mocked `_sync_entity` behavior to isolate bearer/CSRF handling, all-entity iteration, lock contention, partial failures, response reporting, and the public background-sync trigger without invoking Plaid or the downstream mirror. Task 5D remains separate because it introduces the mocked HTTP request and LL-only mirror contract.

## Durability

Ryan subsequently authorized publishing the exact seven-path 3G command-center closeout directly to `main` with `[skip actions]`. This log contains sanitized synthetic evidence only; the publish excludes product/test/workflow files, the pre-existing untracked sync script, deployment, live Plaid or downstream action, credentials, protected data, and production/demo access.

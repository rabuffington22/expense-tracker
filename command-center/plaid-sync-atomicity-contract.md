# Plaid Transaction Sync Atomicity Contract

Date: 2026-07-19

Scope: work block 4I, Phase 4 Task 1H, `P3-3G-01`, and only the cursor-safety and rollback slice of `P3-3G-C01`.

## Unit Of Work

One primary Plaid item is the local atomic unit. The stored cursor at the start of the item sync identifies the first update requested. The Plaid client fetches every available page into memory before local transaction persistence begins.

The following local changes form one SQLite transaction for that item:

- accepted added transactions;
- accepted modified transactions;
- accepted removed transactions and their splits;
- the final `next_cursor` returned after all fetched pages; and
- the matching `last_synced` timestamp.

The final cursor and timestamp may commit only after every accepted transaction mutation succeeds. Result counters become visible to the caller only after that transaction commits.

## Success And Idempotency

- Exact redelivery of an already-bound non-empty Plaid transaction ID is an idempotent no-op, not an error.
- Newly issued keys continue to use the source-aware authoritative Plaid identity established in work block 4C.
- A populated legacy row already bound to the Plaid transaction ID keeps its existing primary key.
- Enabled-account filtering, negative-debit semantics, categorization, splits, and entity isolation remain unchanged.
- A successful update with no accepted transaction events may still advance the item cursor and timestamp.

## Failure Behavior

An insert, categorization write, modification, split deletion, transaction deletion, or cursor/timestamp write failure aborts the complete item transaction. On failure:

- no partial added, modified, or removed state remains;
- removed-transaction splits remain intact;
- the stored cursor and `last_synced` remain at their starting values;
- successful counters from the rolled-back attempt are not reported; and
- the existing sanitized per-item error path receives the failure.

A transaction-ID conflict that is not an existing binding is a persistence error. It must not be converted to the same result as exact redelivery.

## Pagination And Retry Boundary

The client continues to fetch all available pages before persistence and returns only the final cursor. If page retrieval fails, no local transaction update begins and the stored cursor remains unchanged. Work block 4I does not add automatic Plaid retries; a later invocation therefore starts again from the original stored cursor.

This matches Plaid's documented sync shape: collect all pages, persist the accumulated updates with the final cursor, and restart a failed pagination loop from the original cursor rather than from an intermediate cursor.

## Explicit Exclusions

Work block 4I does not change reconciliation, account or balance preservation, liability refresh, freshness, link cleanup, missing-modification observability, corrupt-token isolation, scheduled/public coordination, public removed-event behavior, automatic retry policy, downstream mirroring, schema, or live operations.

## Maintained Acceptance Proof

`scripts/smoke_test.py` must use temporary Personal, BFM, and Luxe Legacy databases, fake tokens, mocked Plaid results, and denied outbound sockets to prove:

- successful aggregated updates commit accepted additions, modifications, removals, the final cursor, and the timestamp together;
- exact redelivery remains idempotent;
- disabled-account additions remain filtered;
- forced add, modify, remove, and cursor-write failures roll back all prior mutations and leave cursor/timestamp unchanged;
- a retry after failure starts from the original stored cursor and can complete successfully; and
- unrelated rows, signs, splits, and entity isolation remain intact.

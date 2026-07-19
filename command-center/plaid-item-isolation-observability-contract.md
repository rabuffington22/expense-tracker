# Plaid Item Isolation And Truthful Observability Contract

Date: 2026-07-19

Scope: work block 4K, Phase 4 Task 1J, `P3-3G-06`, `P3-3G-07`, and only the item-isolation and observability slice of `P3-3G-C01`.

## Item Failure Boundary

One primary Plaid item remains the local failure and cursor unit. Access-token decryption, enabled-account lookup, Plaid transaction retrieval, and atomic local application all run inside that item's exception boundary.

If any of those steps fails:

- the failed item returns one sanitized error identified by its institution name or item ID;
- error text contains no access token, encrypted token, ciphertext, credential, or financial row detail;
- the failed item makes no later Plaid request after decryption failure;
- the failed item's stored cursor and `last_synced` remain unchanged unless its atomic application already completed successfully; and
- healthy sibling items continue independently and retain their committed counters.

The block does not add automatic retries. A later invocation retries the failed item from its preserved stored cursor.

## Modified-Event Truthfulness

A modified event is successful only when its non-empty authoritative Plaid transaction ID matches one stored transaction row inside the selected entity. The update result must report the SQLite affected-row count rather than incrementing unconditionally.

If a modified event matches no stored row, the item transaction fails through the existing stable persistence-error path. All changes for that item roll back, its cursor and `last_synced` remain unchanged, and successful sibling items may still commit. Work block 4K does not implicitly insert or reconstruct the missing transaction because that would choose a recovery contract not established by the upstream event or current task.

## Removed-Event Truthfulness And Idempotency

Removal counts reflect actual deleted transaction rows. Split cleanup remains tied to the matching transaction. A removal for an already-absent transaction deletes zero rows, reports zero removals, and remains an idempotent success so exact re-delivery can advance the item cursor normally.

The public `/k/` worker's separate removed-event behavior remains outside this contract.

## Preserved Behavior

- Added, modified, and removed mutations plus the final cursor and `last_synced` remain atomic per item under the 4I contract.
- Existing source-aware transaction identity, legacy primary-key preservation, exact-redelivery behavior, enabled-account filtering, negative-debit semantics, categorization, splits, and three-entity isolation remain unchanged.
- Successful sibling item counts exclude all rolled-back work from failed items.
- Existing scheduled result truthfulness remains unchanged; broader entity and entry-point isolation belongs to Task 1K.

## Explicit Exclusions

Work block 4K does not change scheduled/public coordination, cross-process locking, public `/k/` authentication or worker behavior, entity-level entry-point recovery, automatic retries, account reconciliation, liabilities, freshness, downstream mirroring, schema, migrations, credentials, protected data, or live operations.

## Maintained Acceptance Proof

`scripts/smoke_test.py` must use temporary Personal, BFM, and Luxe Legacy databases, fake tokens, mocked Plaid responses, and denied outbound sockets to prove:

- corrupt-first and corrupt-last item order both isolate the failed token while healthy siblings commit;
- decryption failure makes no Plaid request and returned errors contain neither the fake encrypted token nor decrypted token material;
- a missing modified target rolls back that item, preserves its starting cursor and timestamp, reports no rolled-back counters, and leaves a healthy sibling successful;
- existing modified rows and removed rows report actual affected-row counts;
- already-absent removals remain zero-count idempotent successes;
- exact redelivery, enabled-account filtering, signs, splits, entity isolation, and prior atomicity behavior remain intact; and
- every synthetic item, account, transaction, split, and temporary database is cleaned exactly.

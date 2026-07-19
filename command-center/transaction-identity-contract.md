# Transaction Identity Contract

Status: active for work block 4C on 2026-07-19.

Scope: transaction primary-key computation for file imports and primary Plaid imports, plus preservation of pre-existing transaction keys and references. This contract does not change persistence ordering, Plaid cursors, reconciliation, concurrency, or any live data.

## Invariants

- `transactions.transaction_id` remains an opaque 24-character lowercase hexadecimal key. Callers must not infer date, amount, merchant, account, or source from it.
- Existing transaction IDs are immutable. Work block 4C adds no database migration and does not regenerate, backfill, or rewrite any populated row.
- Every identity is namespaced and versioned before hashing. File and Plaid identities therefore cannot alias one another even when their visible transaction fields match.
- Negative amounts remain debits. Identity computation does not alter amounts, `amount_cents`, categorization, edits, splits, order matches, aliases, or effective-reporting behavior.
- Entity isolation remains a database boundary. The same source identity may exist independently in Personal, BFM, and Luxe Legacy.

## File Imports

A normalized file row uses these identity components:

1. contract version and the `file` namespace;
2. a stable source/batch fingerprint derived from the caller-supplied source key, normally the normalized basename of `source_filename`;
3. the normalized row key: date, six-decimal signed amount, case-folded trimmed description, case-folded trimmed account, and uppercased currency;
4. the zero-based occurrence ordinal of that row key within the normalized payload, in source order.

The source key must be non-empty. This makes two otherwise identical rows from different source files or accounts distinct, preserves multiple legitimate identical rows within one payload, and makes an exact payload redelivery from the same source key produce the same IDs. A later payload from the same source key may add another identical occurrence without changing the earlier occurrence IDs.

Display renaming after preview does not change identity because IDs are computed from the original source key before confirmation. A materially different source key is a different import identity boundary; 4C does not attempt fuzzy cross-file reconciliation.

## Authoritative External IDs

For Plaid, a non-empty `plaid_transaction_id` is authoritative. A newly issued local primary key is the versioned hash of the `plaid` namespace plus that exact trimmed external ID. Date, amount, description, item, and account do not replace or weaken the authoritative identity.

If a populated pre-4C row already binds that authoritative ID to a legacy primary key, the existing binding wins and the issued key remains unchanged. Redelivery resolves to that row instead of inserting the new hash. This is an identity-resolution compatibility step, not a key rewrite or cursor-order change.

An empty or whitespace-only external ID is invalid and raises before an insert statement. It is never hashed as a shared key and never falls back to the legacy natural-key hash. Any broader invalid-record, cursor, retry, or reconciliation policy belongs to the later Plaid atomicity block.

## Legacy And Manual Rows

The prior date/amount/description hash remains recognized only as an already-issued opaque key and as a compatibility helper for callers outside the repaired import paths. Existing legacy and manually supplied keys are not rewritten. There is no current manual transaction-creation writer in the application; any future writer must choose an explicit namespace and stable source identity rather than reuse the natural-key fallback.

## Upgrade And Reference Safety

No schema change is required: the existing text primary key already stores the new opaque hashes. Re-running database initialization on a populated database must preserve transaction IDs and all references, including `transaction_splits.transaction_id` and `amazon_orders.matched_transaction_id`. New-identity imports append or skip by their computed keys; they do not mutate old keys.

## Verification Contract

Maintained synthetic checks cover all three entities and prove:

- deterministic, namespaced file and Plaid identities;
- distinct sources or accounts do not collide on the same date, amount, and description;
- same-source identical occurrences coexist;
- exact payload redelivery is fully idempotent;
- empty external IDs are rejected rather than aliased;
- populated legacy rows retain edits, negative-debit values, splits, order matches, and effective-reporting behavior after database re-entry and new imports;
- no real database, protected row, credential, network call, Plaid action, workflow, Fly action, downstream write, or GitHub durability occurs.

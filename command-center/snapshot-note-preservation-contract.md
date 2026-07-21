# Snapshot Note Preservation Contract

Date: 2026-07-20

Work block: 4T — Snapshot Note Preservation

Finding: `P3-3D-03`

## Snapshot Identity

- A goal has at most one snapshot for each `(goal_id, snapshot_date)` pair.
- Updating an existing same-day snapshot preserves its `id` and `created_at` values.
- A new date inserts a new snapshot row and does not alter an earlier row.

## Automatic Snapshot Behavior

- The Short-Term Planning page records the current absolute total of a goal's linked account balances.
- If today's snapshot already exists, automatic capture updates only `balance_cents`.
- Automatic capture never clears or replaces the existing manual `note`.

## Manual Review Behavior

- Manual review records the current linked-account balance and the normalized submitted note.
- If today's snapshot already exists, manual review updates `balance_cents` and intentionally replaces `note` while preserving row identity and creation time.
- Whitespace-only input normalizes to an empty note. An empty note does not satisfy the current-month review check.
- A non-empty note satisfies the current-month review check and survives later automatic page-load snapshots.

## Boundaries

- This contract does not add a migration, rewrite historical snapshots, seed demo records, or change the review form.
- Personal and BFM retain Short-Term Planning access. Luxe Legacy remains denied before the route handler.
- Verification uses only temporary synthetic databases with outbound networking denied and exact fixture cleanup.
- Task 1N.3, broader planning work, GitHub durability, deployment, production, credentials, protected data, and live systems remain separately gated.

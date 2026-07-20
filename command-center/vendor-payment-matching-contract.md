# Vendor Payment Matching Contract

Date: 2026-07-20
Work block: 4M — Vendor Payment Matching Integrity
Boundary: local source and temporary synthetic data only

## Canonical Relationship

- `vendor_transactions.matched_transaction_id` is the only vendor-payment-to-bank relationship.
- A bank transaction is available only when no vendor transaction points to its `transaction_id`.
- The nonexistent `transactions.matched_order_id` column is neither queried nor written.
- A bank transaction may be claimed by at most one vendor transaction through maintained application behavior.

## Matching Behavior

- Exact amount/date candidates retain automatic application.
- Likely and loose candidates remain review-only until accepted.
- Candidate selection and exact application run inside one SQLite `BEGIN IMMEDIATE` transaction.
- Accepted batches acquire the same immediate write boundary, validate every vendor and bank row before mutation, and then commit all matches together.

## Rejection And Atomicity

- A missing or already-matched vendor row is stale and rejected.
- A missing or already-claimed bank transaction is rejected.
- Duplicate vendor or bank identifiers within one accepted batch are rejected before any row changes.
- Concurrent claims serialize; one writer may commit and the later writer must reject the durable claim.
- Any error rolls back bank enrichment and vendor relationship updates for the whole batch.

## Enrichment Boundary

Successful application updates only the selected bank transaction's `merchant_canonical` and `notes`, then records the bank `transaction_id` and match confidence on the selected vendor transaction. It does not alter categories, splits, orders, aliases, another entity, or unrelated transactions.

## Explicit Exclusions

This contract adds no migration, unique index, backfill, historical duplicate detection or repair, real-data inspection, live vendor or Plaid action, workflow action, production access, downstream write, GitHub publication, or deployment.

## Verification Contract

- Fresh migration-built Personal, BFM, and Luxe Legacy databases with no `transactions.matched_order_id` column.
- Exact auto-application; likely review and acceptance; unmatched-vendor and unmatched-bank counts.
- Stale replay and duplicate batch rejection with zero unrelated mutation.
- Two-thread contention for one bank transaction with exactly one durable winner.
- Forced second-match failure with whole-batch rollback.
- Denied outbound networking, exact synthetic cleanup, baseline and final maintained smoke suites, Python compilation, JSON validation, dashboard refresh, command-center health, whitespace checks, dashboard inspection, and explicit worktree review.

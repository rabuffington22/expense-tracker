# Vendor Line-Item Persistence Contract

Work block: 4N
Task: Phase 4 Task 1L.2
Boundary: local source and synthetic data only

## Outcome

Normal Amazon and Henry Schein preview/save flows persist each newly inserted vendor-order parent and every parser-provided child item in the same SQLite transaction. The existing migration-53 `order_line_items` table is sufficient; 4N adds no migration, backfill, production script, or live-data action.

## Parent Identity And Reimport

- A parent duplicate is the same vendor, order ID, and exact integer-cent total.
- The first occurrence inserts its parent and children together.
- An exact reimport skips the existing parent and inserts no children.
- An existing parent with missing children is not repaired implicitly. Detection and remediation of historical rows remain separately gated.

## Item Normalization

- Amazon and Henry Schein parser shapes normalize into the existing shared columns: product name, quantity, unit-price cents, item-total cents, vendor item identifier, and raw vendor category metadata.
- Monetary values convert through decimal arithmetic to integer cents at persistence time.
- Henry Schein preserves its parsed extended item amount and quantity.
- Amazon preserves the parser's item amount plus its explicit tax and shipping components. Business-export item net totals already include those components.
- Invalid, non-finite, fractional, or non-positive quantities stop and roll back the import rather than being silently coerced.

## Category Boundary

- Import does not infer a Ledger category or subcategory.
- Raw Amazon or Henry Schein category metadata remains in `amazon_category` for later categorization.
- Optional Ledger category fields are persisted only when an upstream caller explicitly supplies them.
- Deterministic inference, entity-specific category validation, invalid-write rejection, and existing-row remediation remain Task 1L.3.

## Atomicity And Isolation

- Every parent and child in one `save_orders_to_db()` call commits together.
- Any parent or child failure rolls back all new rows in that call.
- The selected entity connection remains the only database touched.
- The persistence path performs no network request and retains no new upload after the existing preview/save handoff consumes its temporary payload.

## Auto-Split Boundary

New imports now create the line-item rows consumed by `auto_split_from_line_items()` without `scripts/populate_line_items.py`. Once those rows have valid Ledger categories, the maintained helper groups them, preserves the parent transaction sign, applies any parent-versus-child remainder to the largest group, and writes `vendor_line_item` splits whose cents reconcile exactly to the bank transaction.

4N proves that path with a newly imported synthetic multi-category order. It does not define how categories are inferred or accepted.

## Verification Contract

- Generated Amazon CSV and Henry Schein XLSX inputs.
- Normal preview/save HTTP handoff for both vendors.
- Fresh Personal, BFM, and Luxe Legacy databases.
- Exact parent and child counts, raw metadata, quantities, and integer cents.
- Exact reimport idempotency.
- Forced child failure with parent rollback.
- Multi-category auto-split with exact parent-cents reconciliation.
- Unchanged unrelated transactions, denied outbound networking, consumed temporary payloads, and exact synthetic cleanup.
- Baseline and final maintained smoke suite, Python compilation, JSON validation, dashboard refresh, command-center health, whitespace checks, dashboard inspection, and explicit worktree review.

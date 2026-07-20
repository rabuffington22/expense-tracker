# Work Block 4N — Vendor Line-Item Persistence

Date: 2026-07-19
Branch: `codex/vendor-line-item-persistence`
Durability: local-only; no commit, push, PR, merge, deployment, or live verification authorized

## Authorized Scope

Task 1L.2 plus only its focused Task 2 vendor line-item persistence and auto-split regression slice. Work block 4M remained confirmed and waiting at the natural post-`2a12533` scheduled-run gate.

Excluded throughout: Task 1L.1 implementation; Task 1L.3 category-domain enforcement; existing-row detection, backfill, or remediation; import UX changes; migration; real databases or financial rows; retained user uploads or original files; credentials; live vendor or Plaid access; authenticated production pages; workflow actions; Fly; downstream access or writes; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

## Implemented Contract

- `save_orders_to_db()` persists each new parent and its parser-provided children in one SQLite transaction.
- Parent reimport identity is exact vendor, order ID, and integer-cent total.
- Exact reimports skip the parent and create no child duplicates.
- Existing parents are not implicitly backfilled.
- Amazon and Henry Schein item shapes normalize into the existing migration-53 columns using decimal-to-cents conversion.
- Invalid, non-finite, fractional, or non-positive quantities fail rather than being silently coerced.
- Raw vendor category metadata is preserved, while normal import assigns no Ledger category or subcategory. Task 1L.3 remains the authority for inference and validation.
- Once valid categories exist, newly imported rows feed the maintained `auto_split_from_line_items()` path without `scripts/populate_line_items.py`.

## Synthetic Evidence

Generated inputs:

- one Amazon Business CSV payment with two child rows totaling 1,500 cents;
- one Henry Schein XLSX invoice with quantities 1 and 2, unit prices 400 and 550 cents, and extended children totaling 1,500 cents.

Across temporary Personal, BFM, and Luxe Legacy databases:

- each vendor inserted one parent and two children on first save;
- each exact reimport returned zero inserts and one skip with child counts unchanged;
- parent and child totals reconciled to 1,500 cents;
- Henry Schein preserved `(quantity, unit_price_cents, item_total_cents)` as `(1, 400, 400)` and `(2, 550, 1100)`;
- no import assigned a Ledger category or changed unrelated transactions;
- outbound sockets were denied and no network access occurred.

Additional controls:

- a forced child insert failure rolled its new parent back;
- an invalid zero quantity rolled its new parent back;
- a newly imported, synthetically categorized two-group order produced two `vendor_line_item` splits summing exactly to the negative 1,500-cent bank transaction;
- normal Amazon and Henry Schein HTTP preview/save flows retained both children through temporary JSON, consumed their session keys, deleted their exact temporary payloads, and wrote one parent plus two children in the selected entity;
- all synthetic parents, children, splits, and bank rows were removed before suite completion.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including the new 7c data-layer and route-handoff coverage.
- `.venv/bin/python -m py_compile core/amazon.py scripts/smoke_test.py`: pass.
- `git diff --check`: pass before closeout.
- No migration or backfill: confirmed.
- Latest sanitized Daily Plaid Sync metadata remained run `29683898125`, successful but predating source commit `2a12533`; 4M therefore remains at its scheduled gate.

Final dashboard refresh, command-center health, JSON validation, dashboard inspection, and explicit worktree review are recorded by the Runway OS closeout after source files and `state.json` are aligned.

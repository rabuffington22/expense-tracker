# Work Block 3B: Synthetic Import-to-Categorization Audit

Date: 2026-07-18

Status: done

## Confirmed Scope

Audit Phase 3 Task 2 as one synthetic-only vertical path from CSV/PDF statements and Amazon/Henry Schein orders through confirmation, matching, aliases, suggestions, and category/subcategory persistence across Personal, BFM, and Luxe Legacy.

## Exclusions

Task 1 and Tasks 3-8; product fixes; tracked fixture or regression-test expansion; real databases, statements, uploads, credentials, or row-level financial data; production/demo access; Plaid or live vendor-account actions; workflows, Fly, downstream writes, authentication/security changes; GitHub durability; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Evidence Contract

All inputs were generated inside an ephemeral temporary root. Findings record behavior and sanitized synthetic reproduction conditions only. Each area is classified as pass, defect, regression-coverage gap, or unverified boundary; no repair was implemented.

## Verification Result

The existing tracked smoke suite passed against its temporary `DATA_DIR`.

The ephemeral 3B probe completed 60 passing checks covering:

- CSV auto-detection, stored profile mapping, date formats, amount negation, split debit/credit columns, invalid-row handling, first import, and exact re-import deduplication;
- PDF text extraction, debit/credit signs, and year rollover;
- Amazon CSV and Henry Schein XLSX parsing, grouping, persistence, and duplicate handling;
- exact, review, and unmatched order-matching outcomes plus accepted-match persistence;
- alias suggestion precedence and database reapplication;
- upload preview, temporary payload, confirm, duplicate confirm, missing payload, checklist completion, and status undo;
- vendor-source preview/save, temporary-file cleanup, route persistence, and cross-entity isolation;
- independent Personal, BFM, and Luxe Legacy database state with no cross-entity leakage.

## Audit Matrix

| Area | Classification | Result |
| --- | --- | --- |
| CSV profiles and normalization | Pass | Auto-detection, explicit profiles, date formats, account propagation, debit/credit signs, amount negation, invalid input, and exact re-import behavior passed. |
| PDF statement parsing | Pass | Three generated rows preserved credit/debit signs and assigned the prior year correctly across a December-to-January statement boundary. |
| Upload preview and confirmation | Pass | Preview, temporary-file handoff, confirmation, duplicate handling, missing-payload handling, completion status, cleanup, and entity isolation passed. |
| Upload undo | Pass with operator ambiguity | Undo changes the monthly checklist status back to incomplete; it does not delete previously imported transactions, while the UI labels the action only as `Undo`. |
| Amazon and Henry Schein parsing | Pass | Generated Amazon and Henry Schein inputs grouped correctly, preserved totals, persisted independently in all entities, and deduplicated exact reimports. |
| Vendor-order line items and auto-split | Defect | Normal import persisted order summaries but zero line items, so matched-order auto-split returned `No categorized line items found`. |
| Order matching | Pass | Exact, review, and unmatched outcomes were produced in all three entities, and accepted exact matches linked only the target entity. |
| Vendor-payment matching | Defect | Every fresh migration-built entity failed before matching because the query references nonexistent `transactions.matched_order_id`. Exact/review/unmatched vendor-payment behavior remains blocked behind this defect. |
| Aliases and suggestions | Pass | Entity-local active aliases took precedence and reapplied to only their target databases. |
| Category/subcategory integrity | Defect | Amazon inference and accepted exact matching wrote `Household`, which is absent from all three current category definitions; equal-frequency Amazon categories also varied across hash seeds, and the accept endpoint persisted undefined category/subcategory values. |
| Temporary-file cleanup | Pass | Upload, vendor, and matching probe payloads left no files in the isolated temporary upload directory. |
| Tracked regression coverage | Gap | The tracked smoke suite covers generic CSV import and route availability but not the Task 2 parser, confirmation, matching, alias, vendor-order, or category-domain behaviors exercised here. |
| Live integrations and real-data occurrence | Unverified boundary | No real statement, database, credential, Plaid/vendor connection, production/demo surface, or downstream action was opened. |

## Ranked Findings

1. High functional correctness risk: vendor-payment matching cannot run on the migration-built schema because it queries and updates `transactions.matched_order_id`, a column not created by any migration.
2. High financial-classification integrity risk: vendor matching can write categories outside `categories.md`; mixed-category order inference is nondeterministic on ties; and category acceptance does not enforce defined category/subcategory pairs.
3. High vendor-detail completeness risk: ordinary Amazon and Henry Schein imports discard parsed line items, leaving the supported vendor auto-split path without the data it requires.
4. Medium regression-confidence risk: the 60 passing Task 2 behaviors are ephemeral and absent from the tracked smoke suite.
5. Low operator-clarity risk: upload `Undo` marks a checklist item incomplete but does not undo imported ledger rows, and the UI does not state that distinction.

All findings are recorded in `command-center/issues.md`. No product fix, migration, tracked fixture, or tracked test was added.

## Boundaries Preserved

No real database, statement, upload, credential, row-level financial data, production/demo endpoint, Plaid or live vendor-account action, workflow action, Fly action, downstream write, authentication change, product edit, tracked fixture/test edit, commit, push, PR, merge, or deployment occurred. The generated temporary inputs and databases were removed, and pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched.

## Conclusion

The basic statement parsers, vendor-order parsers, upload confirmation, order matching, alias behavior, cleanup, and three-entity isolation are sound under synthetic evidence. The path is not end-to-end trustworthy yet because vendor-payment matching is schema-broken, normal vendor imports lose split-level detail, and category writes are not constrained to the current domain source of truth. Task 2 is complete as an audit; repairs remain separately gated for Phase 4, and the next audit slice is Task 3.

## Post-Block Durability

After the audit and local verification were complete, Ryan separately authorized committing and pushing the exact seven-path command-center closeout directly to `main`. It is published with the established `[skip actions]` convention so the command-center-only push does not start the production Fly deployment workflow. No product, fixture, tracked test, workflow, protected-data, or pre-existing untracked-file change is included.

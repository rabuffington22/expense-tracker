# Work Block 3C: Synthetic Financial Read-Model Audit

Date: 2026-07-18

Status: done

## Confirmed Scope

Audit Phase 3 Task 3 as one synthetic-only financial read-model pass across dashboard metrics, report views and exports, subscription detection and lifecycle, and cash-flow balances and projections for Personal, BFM, and Luxe Legacy.

## Exclusions

Tasks 1-2 and 4-8; product fixes; tracked fixture or regression-test expansion; real databases, exports, balances, credentials, or row-level financial data; production/demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication/security changes; GitHub durability; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Evidence Contract

All rows, balances, subscriptions, and account details were synthetic and created inside an ephemeral `DATA_DIR`. Plaid, OpenRouter, authentication, downstream, and live-system configuration was absent. The temporary root was removed after every probe run. Findings contain only sanitized behavior and source references.

## Verification Result

The existing tracked smoke suite passed against its own temporary `DATA_DIR`.

The final ephemeral 3C probe ran 306 checks. It produced 297 passes, zero assertion failures, and nine controlled error reproductions. All nine errors were the same defect exercised at three layers in all three entities: direct recurring-report query, prepared report, and rendered report route.

Passing coverage included:

- effective-transaction replacement of split parents with signed split pieces;
- date-range, account, transfer-inclusion, category, merchant, month-over-month, income/expense, tax, and account-summary reconciliation;
- dashboard counts, spend, income, review count, account filters, transfer toggle, empty behavior, and route rendering;
- every non-recurring report type through prepared data, rendered HTMX view, CSV, and PDF; transaction QBO generation and non-transaction QBO rejection;
- filenames, response types, parseable PDF output, entity-specific content, empty ranges, and missing-date responses;
- subscription suggestion detection plus accept, detail, update, synthetic account-info add/delete, dismiss/restore, share-text, delete, and entity-local persistence;
- manual bank/card balance updates, manual recurring add/delete, automatic recurring projection, liabilities, and expected Personal-to-BFM shared cash-flow visibility with Luxe Legacy isolated;
- cross-entity output and write isolation for all three databases.

## Audit Matrix

| Area | Classification | Result |
| --- | --- | --- |
| Effective transactions and exclusions | Pass | Split parents were replaced by their signed pieces, category and merchant totals reconciled, and each entity's synthetic excluded category stayed out of spend totals. |
| Dashboard | Pass | Effective counts, spend, income, review count, account filters, transfer inclusion, routes, and entity-specific output matched the expected synthetic ledger. |
| Standard reports | Pass | Transactions, categories, merchants, month-over-month, income versus expenses, tax summary, and account summary prepared and rendered correctly across all entities. |
| CSV, PDF, and QBO exports | Pass | All supported non-recurring CSV/PDF paths returned expected response types and entity-specific content; transaction QBO was valid and QBO was rejected for unsupported report types. |
| Recurring Charges report | Defect | Direct query, prepared-report, and rendered-view paths failed in every entity because the SQL string contains the literal token `{exclude_sql('category')}`. |
| Subscription tracker | Pass | Detection, regularity and cadence, lifecycle routes, synthetic metadata, dismiss/restore, deletion, and entity-local persistence passed. |
| Cash flow | Pass | Manual balances, card liabilities, recurring projections, writes, deletes, expected Personal/BFM shared visibility, and LL isolation passed without external calls. |
| Empty and invalid input boundaries | Pass | Empty export ranges returned not found, missing dates returned bad request, and empty application surfaces remained renderable. |
| Tracked regression coverage | Gap | The maintained smoke suite checks route availability and basic monthly CSV exports but does not exercise the financial reconciliation, all report types, recurring query, subscription lifecycle, or cash-flow behavior covered here. |
| Live data and integrations | Unverified boundary | No production/demo data, Plaid/OpenRouter call, credential, real balance, workflow, Fly surface, or downstream system was opened. |

## Ranked Findings

1. Medium functional-availability risk: the Recurring Charges report is unusable in every migration-built entity because `get_recurring_charges()` executes an ordinary string containing an uninterpolated SQL helper expression.
2. Medium regression-confidence risk: the 297 passing Task 3 assertions and the recurring-report failure reproduction are ephemeral and absent from the tracked smoke suite.

Both findings are recorded in `command-center/issues.md`. No product fix or tracked test was implemented.

## Boundaries Preserved

No real database, export, balance, credential, row-level financial data, production/demo endpoint, Plaid/OpenRouter call, workflow action, Fly action, downstream write, authentication change, product edit, tracked fixture/test edit, PR, merge, or deployment occurred. Temporary databases were removed. Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched.

## Conclusion

The shared Task 3 financial read model is substantially coherent under synthetic evidence: dashboard figures, standard reports, exports, subscription behavior, cash-flow calculations, intended cross-entity visibility, and isolation reconciled across all three entities. The narrow exception is the Recurring Charges report, whose SQL construction prevents that report from running at all. Task 3 is complete as an audit, the repair remains separately gated for Phase 4, and Task 4 is the next planned audit slice.

## Durability

After the audit and local verification were complete, Ryan separately authorized committing and pushing the exact seven-path command-center closeout directly to `main`. It is published with the established `[skip actions]` convention so the command-center-only push does not start the production Fly deployment workflow. No product, fixture, tracked test, workflow, protected-data, or pre-existing untracked-file change is included.

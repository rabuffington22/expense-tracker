# Issues

These are known defects, risks, or rough edges. They are not active work unless promoted into a phase task and confirmed work block.

## Daily Plaid Sync Disabled For Inactivity

Status: monitored; work block 1C complete

Severity: high operational reliability

Captured: 2026-07-17

Where seen: GitHub Actions workflow metadata and run history

Revisit: Phase 1, Task 4 for recurrence prevention or detection

Summary:

The `Daily Plaid Sync` workflow was found `disabled_inactivity` after its last listed successful scheduled run on 2026-07-15. Work block 1A re-enabled it and verified controlled run `29627530457` successfully.

Impact:

Immediate sync scheduling is restored. Work block 1B found that the public repository's more-than-60-day commit gap closely matches GitHub's documented automatic-disable rule. Work block 1C added independent alert-only monitoring for disabled state, missing scheduled runs, unsuccessful runs, and runs incomplete beyond the delay window.

Why not fully closed:

The underlying GitHub inactivity behavior still exists, but active automation `expense-tracker-daily-plaid-sync-monitor` now detects recurrence without enabling or dispatching the workflow. Recovery remains Ryan-gated.

Promotion trigger:

The monitor reports a defined failure condition or Task 6 reveals a better control.

## Daily Plaid Sync Runs At The Start Of The Hour

Status: resolved

Severity: low operational reliability

Captured: 2026-07-18

Where seen: `.github/workflows/daily-plaid-sync.yml`

Revisit: Phase 1, Task 6

Resolution:

Work block 1D changed the workflow to `17 9 * * *` through ready PR `#83`, preserving the existing UTC hour and `workflow_dispatch`. Merge commit `96af7dc` triggered Fly Deploy run `29645346441`; the run and every job step succeeded. Daily Plaid Sync remained active, and production plus demo returned HTTP 200. No manual sync or sensitive log access occurred. The existing independent monitor owns the first natural minute-17 run observation.

## Project Documentation Contradicts Current Architecture

Status: resolved and released through PR #85

Severity: medium project reliability

Captured: 2026-07-17

Where seen: `README.md`, `PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, and `AGENTS.md`

Revisit: none unless active guidance diverges again

Summary:

Tracked root documentation mixes the retired Streamlit/manual-import architecture with the current Flask, HTMX, Plaid, Fly.io, and three-entity system. The most current instruction file is untracked.

Impact:

Agents and maintainers can begin from an incorrect architecture, execute obsolete commands, or mistake completed planning for future work.

Resolution:

Work block 2B added a concise tracked `AGENTS.md` as canonical, reduced `CLAUDE.md` to a compatibility pointer, and replaced `PROJECT_KNOWLEDGE.md` plus `plan.md` with historical notices backed by Git history. Work block 2B-R merged PR #85 as `216a992`, and the resulting production deployment plus HTTP health checks passed.

## Planning Foundations Lack Tracked Regression And Demo Goal Evidence

Status: confirmed by work block 3D; parked for Phase 4 regression coverage and Phase 5 demo review

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: retired `plan.md`, `scripts/smoke_test.py`, `scripts/seed_demo_data.py`, and work block 3D's 58-check temporary-database probe

Revisit: Phase 4 Task 2 for tracked coverage; Phase 5 for demo fidelity if still useful

Summary:

The legacy Short-Term Planning plan proposed dedicated goal CRUD, snapshot, budget, payoff, entity-isolation, and cross-entity smoke cases plus seeded goals and snapshots. Work block 3D confirmed that goal CRUD/status/delete, budget and subcategory persistence, effective split accounting, three-month averages, per-payroll budgets, action items, payoff engines when supplied correct rates, and entity-local Personal/BFM account choices work against temporary synthetic data. The tracked smoke suite still contains no dedicated long- or short-term planning cases, and demo seeding still omits goals and snapshots.

The audit treats goal CRUD, snapshot persistence, budget behavior, payoff correctness, and entity isolation as valid current expectations. It treats Short-Term Planning cross-entity account linking and the retired custom-allocation strategy as superseded: current repository rules require explicit cross-entity behavior, the live short-term UI is entity-local, and only avalanche and snowball are exposed. Personal/BFM sharing remains an explicit Long-Term Planning behavior and passed.

Impact:

The 3D evidence is current but ephemeral. Future changes can regress planning CRUD, projections, snapshots, budgets, payoff ordering, or entity boundaries without the maintained smoke suite detecting them. The public demo also cannot demonstrate goal progress history from its seeded state.

Acceptance checks:

- Tracked synthetic tests cover the passing 3D long- and short-term paths plus each separately repaired defect.
- Personal/BFM Long-Term Planning sharing and Luxe Legacy denial are explicit route and mutation assertions.
- Short-Term Planning goals and linked-account choices remain entity-local unless a new product decision explicitly widens them.
- Demo goal and snapshot seeding is either added with synthetic examples or explicitly declined as unnecessary.

Why not added now:

Tracked test and demo-seed expansion were explicitly excluded from audit work block 3D and require separate implementation scope.

## Locked Payoff Schedules Ignore Stored Account APRs

Status: open; discovered in work block 3D

Severity: high financial-planning correctness risk

Captured: 2026-07-18

Where seen: `web/routes/short_term_planning.py`, migrated `account_balances.apr_bps`, and deterministic lock-plan reproduction

Revisit: Phase 4 Task 1 for repair; Phase 4 Task 2 for tracked coverage

Summary:

The direct payoff engine correctly applies the APR values it receives, but `lock_plan()` does not select `apr_bps` from linked accounts and hard-codes every card to 20%. In a synthetic avalanche plan with a 9.99% card listed before a 29.99% card, the stored month-one schedule sent the extra payment to the low-APR card. The resulting rounded balances were $288 on the low-APR card and $1,195 on the high-APR card, the opposite of avalanche ordering.

Impact:

Locked plans can recommend and display the wrong payment sequence, interest accumulation, and payoff trajectory. A user could make a financial decision from a schedule that appears account-specific but ignores the account APR data already stored by the application.

Acceptance checks:

- Linked account details pass the stored `apr_bps` value into payoff computation.
- Avalanche targets the highest APR and snowball targets the smallest current balance regardless of linked-account order.
- Missing APR behavior is explicit and does not silently make different cards equivalent.
- The saved narrative and month-by-month schedule reconcile to the same inputs and have tracked synthetic coverage.

Why not fixed now:

Work block 3D is audit-only. Product repair and tracked tests require a separately confirmed Phase 4 block.

## Luxe Legacy Planning Denial Is Enforced Only On Page Entry

Status: open; discovered in work block 3D

Severity: high entity-boundary and hidden-data risk

Captured: 2026-07-18

Where seen: Long-Term and Short-Term Planning routes plus temporary Luxe Legacy and Personal databases

Revisit: Phase 4 Task 1 for route-boundary repair; Phase 4 Task 2 for direct-route coverage

Summary:

The two planning index routes redirect Luxe Legacy to the dashboard, but their supporting GET and POST routes do not enforce the same denial. With the LL entity selected, synthetic direct requests created a hidden LL planning item, goal, budget, and action item; exposed Personal cash-flow account names through the planning helper; and changed the Personal singleton planning inflation setting from 0 to 9.90%. The probe restored the synthetic setting afterward and removed its temporary data directory.

Impact:

The UI communicates that planning is unavailable to LL while direct routes can create unseen LL records and cross the intended boundary into Personal planning configuration and account-name metadata. This violates the explicit entity and LL planning boundary even though no real data or live system was accessed during the audit.

Acceptance checks:

- Every Long-Term and Short-Term Planning GET/POST helper applies the same LL denial as its index route.
- Denied requests leave all three entity databases unchanged and reveal no Personal/BFM account names.
- Personal/BFM Long-Term Planning sharing remains read-only for the secondary section and continues to work.
- Tracked tests exercise page and direct-route denial for item, settings, goal, snapshot, budget, action, and helper endpoints.

Why not fixed now:

Adding authorization guards changes route behavior and requires separate repair and regression scope.

## Automatic Goal Snapshots Erase Same-Day Review Notes

Status: open; discovered in work block 3D

Severity: medium planning-record persistence risk

Captured: 2026-07-18

Where seen: `web/routes/short_term_planning.py` and deterministic same-day snapshot reproduction

Revisit: Phase 4 Task 1 for snapshot upsert repair; Phase 4 Task 2 for tracked coverage

Summary:

A manual monthly review stores the note on the goal's current-day snapshot and initially satisfies the monthly-review check. The next Short-Term Planning page load runs `_auto_snapshot()` with `INSERT OR REPLACE` but no note value, replacing the row and clearing the note. The same synthetic goal immediately returned to `needs_review=True`.

Impact:

User-entered monthly review context is silently lost during an ordinary page reload, and the interface asks for a review that was already completed.

Acceptance checks:

- Repeated automatic snapshots update the current balance without deleting an existing note or changing the snapshot's identity unexpectedly.
- Manual review notes survive page loads and continue to satisfy the current-month review check.
- A later manual review can intentionally replace the note when requested.
- Tracked tests cover same-day auto/manual ordering and a month transition.

Why not fixed now:

Snapshot upsert behavior and tracked tests were excluded from audit work block 3D.

## Negative Asset Appreciation Is Treated As Zero Growth

Status: open; discovered in work block 3D

Severity: medium long-term projection correctness risk

Captured: 2026-07-18

Where seen: `web/routes/planning.py`, demo Equipment seed data, and deterministic projection reproduction

Revisit: Phase 4 Task 1 for projection repair; Phase 4 Task 2 for tracked coverage

Summary:

Long-Term Planning labels negative asset rates as depreciation, and demo Equipment is seeded at -15%, but `_compute_projections()` only compounds when the rate is greater than zero. A synthetic $10,000 asset at -10% remained $10,000 at the future milestone instead of declining.

Impact:

Depreciating assets are overstated in future asset and net-worth totals, making the combined long-term projection internally inconsistent with the rate shown to the user.

Acceptance checks:

- Negative rates compound downward while zero rates remain flat apart from contributions.
- Positive appreciation, inflation adjustment, contributions, and liability payoff behavior remain correct.
- Summary and combined net-worth totals reconcile to repaired item projections.
- Demo Equipment produces a declining projection and the behavior has tracked synthetic coverage.

Why not fixed now:

Projection logic and tracked tests require a separately confirmed Phase 4 repair block.

## Transaction Identity Can Collapse Distinct Transactions

Status: open; discovered in work block 3A

Severity: high financial-data completeness risk

Captured: 2026-07-18

Where seen: `core/imports.py`, `web/routes/plaid.py`, and synthetic temporary-database reproduction

Revisit: Phase 4 Task 1 for repair design; Phase 3 Task 5 for the bounded Plaid-path impact audit

Summary:

`compute_transaction_id()` hashes only date, amount, and normalized description. A synthetic pair with the same date, amount, and description but different accounts produced the same primary key; `commit_transactions()` inserted one row and silently counted the other as skipped. Legitimate repeated transactions with the same hash inputs can therefore be treated as duplicates. Source inspection also found that Plaid ingestion calls the same identity helper, but work block 3A did not perform Plaid or live-system testing.

Impact:

The importer can omit a legitimate transaction without surfacing an error, producing an incomplete ledger and understated or overstated downstream reporting. The audit did not inspect real data, so actual production occurrence is unknown.

Acceptance checks:

- Two legitimate transactions that differ by account or another stable source identity can coexist.
- Exact re-imports of the same source transaction remain deduplicated.
- Existing transaction relationships, including splits and vendor matches, have a safe preservation or migration path.
- Synthetic coverage proves CSV/import behavior and, in its separately authorized audit or repair scope, Plaid identity behavior.

Why not fixed now:

Work block 3A is audit-only. Changing the primary identity contract requires repair design, migration judgment, tracked regression coverage, and a separately confirmed Phase 4 work block.

## Transaction Edit, Split, And Effective-Reporting Paths Lack Tracked Regression Coverage

Status: parked for Phase 4 regression coverage

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py`, `web/routes/transactions.py`, and `core/reporting.py`

Revisit: Phase 4 Task 2, preferably alongside the transaction-identity repair block

Summary:

Work block 3A's ephemeral temporary-database probe confirmed current edit persistence, cross-entity edit and split denial, split sign and total validation, rejected-update preservation, and effective-reporting replacement of a split parent with signed split pieces. The tracked smoke suite does not exercise those behaviors, so the passing evidence is current but not a durable regression guard.

Impact:

Future changes to transaction editing, split validation, entity scoping, or reporting expansion could regress without the existing smoke suite detecting them.

Acceptance checks:

- Tracked synthetic tests cover successful edit and split operations.
- Cross-entity edit and split attempts return not found and leave every entity unchanged.
- Invalid split sign or total is rejected without replacing the prior valid split set.
- Effective reporting excludes the split parent, emits the split pieces, and preserves the signed total.

Why not added now:

Tracked test expansion was explicitly excluded from audit work block 3A and belongs in a separately confirmed Phase 4 regression-coverage block.

## Vendor-Payment Matching References A Missing Transaction Column

Status: open; discovered in work block 3B

Severity: high functional correctness risk

Captured: 2026-07-18

Where seen: `core/vendor_matching.py`, `core/db.py`, and fresh temporary databases for all three entities

Revisit: Phase 4 Task 1 for schema/query repair; Phase 4 Task 2 for regression coverage

Summary:

`match_vendor_to_bank()` selects and updates `transactions.matched_order_id`, but no ordered migration creates that column. The same `sqlite3.OperationalError` occurred in fresh Personal, BFM, and Luxe Legacy databases before any exact, review, or unmatched vendor-payment result could be produced.

Impact:

The Venmo/PayPal vendor-matching workflow cannot run against the canonical migration-built schema. Actual production state was not inspected, so whether a manually divergent live schema masks the defect is unknown and must not be assumed.

Acceptance checks:

- A fresh migration-built database can run vendor-payment matching without a schema error.
- Exact, review, unmatched-vendor, and unmatched-bank outcomes are covered synthetically.
- Accepted matches enrich only the target entity and cannot overwrite an unrelated transaction.
- Any schema change has an additive migration and a safe existing-data path.

Why not fixed now:

Work block 3B is audit-only. Schema/query repair and tracked tests require a separately confirmed Phase 4 block.

## Vendor-Order Imports Discard Parsed Line Items

Status: open; discovered in work block 3B

Severity: high vendor-detail completeness risk

Captured: 2026-07-18

Where seen: `core/amazon.py`, `core/henryschein.py`, `web/routes/data_sources.py`, `scripts/populate_line_items.py`, and synthetic all-entity reproduction

Revisit: Phase 4 Task 1 for import persistence repair; Phase 4 Task 2 for regression coverage

Summary:

Amazon and Henry Schein parsers produce grouped orders with individual item lists, but `save_orders_to_db()` persists only the order summary. Fresh imports therefore created zero `order_line_items` rows in every entity. The auto-split helper then returned `No categorized line items found`; the only existing population path is a separate file-specific script that reparses original files.

Impact:

New vendor imports cannot support the advertised line-item breakdown and category split path without a separate operational backfill that depends on retaining and locating the original files.

Acceptance checks:

- Normal Amazon and Henry Schein save flows persist their parsed line items transactionally with the parent order.
- Exact re-imports remain idempotent for both orders and line items.
- Item totals, quantity, tax/shipping treatment, category/subcategory, and parent totals reconcile in integer cents.
- A matched multi-category order can create valid vendor-line-item splits without a separate production script.

Why not fixed now:

Changing persistence and backfill behavior is implementation work with migration and regression implications, excluded from work block 3B.

## Vendor Categorization Can Escape The Category Source Of Truth

Status: open; discovered in work block 3B

Severity: high financial-classification integrity risk

Captured: 2026-07-18

Where seen: `core/amazon.py`, `web/routes/categorize.py`, `web/routes/categorize_vendors.py`, `categories.md`, and synthetic all-entity reproduction

Revisit: Phase 4 Task 1 for domain-enforcement repair; Phase 4 Task 2 for regression coverage

Summary:

Amazon category inference returned and accepted matching wrote `Household`, which is absent from the Personal, BFM, and Luxe Legacy definitions in `categories.md`. Equal-frequency item-category ties selected `CE` or `Home` under different hash seeds because the grouping logic uses an unordered set. A synthetic POST to the categorization accept route also persisted an undefined category and subcategory without validation.

Impact:

Automated or stale-client categorization can create nondeterministic classifications outside the maintained category domain, fragment reporting, and produce new orphan-cleanup work. Actual production occurrence was not inspected.

Acceptance checks:

- Every inference result is validated against the target entity's current category/subcategory definitions.
- Mixed-category tie handling is deterministic and documented.
- Transaction and vendor-order acceptance reject undefined categories and invalid category/subcategory pairs without changing stored data.
- Existing invalid classifications have a separately reviewed detection and remediation path.
- Synthetic tests cover Personal, BFM, and Luxe Legacy independently.

Why not fixed now:

Domain-enforcement behavior, existing-row remediation, and tracked tests require product and data-migration judgment outside the 3B audit.

## Task 2 Import And Categorization Paths Lack Tracked Regression Coverage

Status: parked for Phase 4 regression coverage

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and work block 3B's ephemeral 60-check probe

Revisit: Phase 4 Task 2, preferably alongside the related Task 2 repairs

Summary:

Work block 3B passed current synthetic behavior for CSV/PDF parsing, profiles, upload confirmation, Amazon/Henry parsing and deduplication, order matching, aliases, temporary-file cleanup, and entity isolation. The tracked smoke suite covers generic CSV import and route availability but does not guard these Task 2 paths.

Impact:

Passing behavior can regress without the maintained suite detecting it, and the three 3B correctness defects currently have no failing tracked reproductions.

Acceptance checks:

- Tracked synthetic fixtures cover CSV/PDF profiles and Amazon/Henry imports without real financial data.
- Route tests cover preview, confirm, duplicate, missing payload, completion status, and explicit undo semantics.
- Matching tests cover exact, review, unmatched, apply, line-item split, aliases, and all-entity isolation.
- Regression cases fail before and pass after each separately authorized repair.

Why not added now:

Tracked fixture and test expansion was explicitly excluded from audit work block 3B.

## Upload Undo Label Does Not Explain Its Status-Only Effect

Status: open; discovered in work block 3B

Severity: low operator-clarity risk

Captured: 2026-07-18

Where seen: `web/routes/upload.py`, `web/templates/upload.html`, and synthetic route reproduction

Revisit: Phase 5 Task 2 unless a related Phase 4 import repair makes the distinction urgent

Summary:

The upload page labels the completed-source action `Undo`. The route intentionally changes only `import_checklist_status.completed` and leaves imported transactions intact. The synthetic transaction count was unchanged after the checklist returned to incomplete.

Impact:

An operator can reasonably interpret `Undo` as reversing the import, then attempt another import or assume ledger rows were removed. Deduplication limits exact-repeat damage but does not make the action's meaning clear.

Acceptance checks:

- The UI states whether the action means `Mark incomplete` or truly reverses an import.
- If status-only, confirmation text explicitly says imported transactions remain.
- If true reversal is chosen later, it has an exact source/batch identity, preview, safety gate, and regression coverage.

Why not changed now:

User-facing wording or destructive reversal behavior is implementation and UX scope outside the 3B audit.

## Recurring Charges Report Executes An Uninterpolated SQL Helper

Status: open; discovered in work block 3C

Severity: medium functional-availability risk

Captured: 2026-07-18

Where seen: `core/reporting.py`, `web/routes/reports.py`, and synthetic direct, prepared-report, and rendered-route reproduction in all three entities

Revisit: Phase 4 Task 1 for query repair; Phase 4 Task 2 for regression coverage

Summary:

`get_recurring_charges()` builds its query with an ordinary triple-quoted string while embedding `{exclude_sql('category')}`. SQLite therefore receives the braces and helper call as literal SQL and raises `unrecognized token: "{"`. The same result occurred in fresh Personal, BFM, and Luxe Legacy databases at the direct helper, prepared-report, and rendered-report layers.

Impact:

The Reports page's Recurring Charges view and exports cannot produce a result when selected. Subscription detection and cash-flow recurring projections use separate implementations and passed, so the defect is currently isolated to the report path rather than all recurring behavior.

Acceptance checks:

- Recurring-report SQL is constructed safely and uses the target entity's current exclusion contract.
- Direct, prepared, rendered, CSV, and PDF recurring-report paths pass in fresh Personal, BFM, and Luxe Legacy databases.
- Repeated merchants are summarized correctly while transfers, payments, owner contributions, partner buyouts, and income follow the intended entity rules.
- Empty and out-of-range requests return an empty/not-found response rather than a server error.
- A tracked synthetic regression fails before and passes after the repair.

Why not fixed now:

Work block 3C is audit-only. Product repair and tracked regression coverage require a separately confirmed Phase 4 block.

## Task 3 Financial Read-Model Paths Lack Tracked Regression Coverage

Status: parked for Phase 4 regression coverage

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and work block 3C's ephemeral 306-check probe

Revisit: Phase 4 Task 2, preferably alongside the recurring-report repair and other prioritized reporting fixes

Summary:

Work block 3C produced 297 passing assertions across effective transactions, dashboard reconciliation, standard report views, CSV/PDF/QBO exports, subscription lifecycle, cash-flow behavior, and all-entity isolation. The tracked smoke suite covers route availability and basic monthly CSV exports but does not guard the complete Task 3 read model or reproduce the Recurring Charges report failure.

Impact:

Shared totals, split replacement, entity exclusions, export formats, subscription workflows, and cash-flow calculations can regress without the maintained suite detecting them. The known recurring-report failure also has no tracked failing reproduction.

Acceptance checks:

- Tracked synthetic tests reconcile dashboard and report totals against one deterministic all-entity dataset.
- Every supported report view and export format has happy-path, empty-range, and invalid-input coverage.
- Subscription detection/lifecycle and cash-flow balance/recurring behavior are tested without Plaid or OpenRouter access.
- Personal/BFM intended sharing and Luxe Legacy isolation are explicit assertions.
- The recurring-report regression is captured before its separately authorized repair.

Why not added now:

Tracked fixture and test expansion was explicitly excluded from audit work block 3C.

## Weekly Historical Views Mix Selected And Current Dates

Status: open; discovered in work block 3E

Severity: high financial-planning correctness risk

Captured: 2026-07-18

Where seen: `web/routes/weekly.py`, Short-Term Planning bill helpers, Cash Flow recurrence helpers, and deterministic current/historical/cross-month probes

Revisit: Phase 4 Task 1 for date-anchor repair; Phase 4 Task 2 for tracked coverage

Summary:

Weekly accepts an arbitrary ISO week, but only transaction queries and action-item due days consistently use that selected interval. Budget and category pace use `date.today()` for the divisor, recurring and credit-card bills compute their next occurrence from today, and the last-week burn-rate window can start in the previous month while ending in the viewed month. In the synthetic cross-month case, 42 days of spending were projected against a 30-day month and changed the conclusion from $3,216.67 over budget to $1,628.57 under budget.

Impact:

Navigating to a historical or boundary week can show the wrong pace, omit bills that belonged to that week, and reverse the budget-health conclusion. Current-week behavior passed, so the defect is specifically the incomplete propagation of the selected date.

Acceptance checks:

- Pace and category pace derive their day count from the viewed budget month.
- Manual, detected-recurring, and credit-card due items are projected into the selected week rather than always from today.
- Last-week scorecard, pace, MTD window, day count, and displayed month use one coherent calendar period across month/year boundaries.
- Current-week, historical, cross-month, cross-year, empty, and all-entity cases have tracked synthetic coverage.

Why not fixed now:

Work block 3E is audit-only. Date-anchor repair and tracked tests require separate Phase 4 implementation scope.

## Weekly Credit-Card Bills Use Full Balance Instead Of Scheduled Payment

Status: open; discovered in work block 3E

Severity: high cash-planning correctness risk

Captured: 2026-07-18

Where seen: `web/routes/short_term_planning.py`, `web/routes/weekly.py`, `web/templates/weekly.html`, and deterministic bill-total reproduction

Revisit: Phase 4 Task 1 for bill-amount repair; Phase 4 Task 2 for tracked coverage

Summary:

The credit-card due helper formats the title from `payment_amount_cents`, such as `Card Current — $50 due`, but Weekly copies `balance_cents` into the bill amount. The rendered row and weekly total therefore used $1,200 for the same synthetic card. With a $20 recurring charge and $50 manual charge, the displayed total was $1,270 instead of the scheduled $120.

Impact:

Weekly can materially overstate near-term bills and available cash even while the row title communicates the correct scheduled payment.

Acceptance checks:

- A credit-card bill row uses the scheduled payment amount when one exists.
- Missing scheduled-payment behavior is explicit and does not silently substitute the full balance unless the product deliberately labels it that way.
- Row title, amount column, total, and source helper reconcile in integer cents.
- Multiple cards, zero balances, missing amounts, and entity isolation have tracked tests.

Why not fixed now:

Bill semantics and regression tests were excluded from audit work block 3E.

## Waterfall Payoff Average Excludes Deficit Months

Status: open; discovered in work block 3E

Severity: high debt-planning correctness risk

Captured: 2026-07-18

Where seen: `web/routes/waterfall.py` and deterministic three-month surplus reproduction

Revisit: Phase 4 Task 1 for averaging repair; Phase 4 Task 2 for tracked coverage

Summary:

Waterfall labels its payoff input a three-month rolling average, but it first removes every non-positive month and averages only the remaining surpluses. Synthetic monthly results of $1,000, negative $2,000, and $2,500 produced a displayed average of $1,750 instead of the signed three-month average of $500.

Impact:

The debt-payoff estimate can substantially overstate recurring cash available for repayment precisely when recent deficits make the plan less reliable.

Acceptance checks:

- The rolling window and signed-surplus rule are explicit and use every included month.
- Deficit, zero, missing, and fewer-than-three-month histories have defined behavior.
- Displayed average, months-to-payoff, and payoff date reconcile to the same inputs.
- Tracked tests cover mixed surplus/deficit history and all-empty/non-positive history.

Why not fixed now:

Waterfall calculation changes and tracked tests require a separately confirmed Phase 4 block.

## Invalid Weekly Paydown Dates Persist And Break The Page

Status: open; discovered in work block 3E

Severity: medium functional-availability risk

Captured: 2026-07-18

Where seen: `web/routes/weekly.py` and a deterministic direct-route POST/read reproduction

Revisit: Phase 4 Task 1 for validation and defensive-read repair; Phase 4 Task 2 for tracked coverage

Summary:

The paydown-goal POST persists any non-empty target date. A synthetic direct request stored `not-a-date`, redirected successfully, and caused the next Weekly read to raise `ValueError` while parsing the saved goal.

Impact:

A malformed direct request or pre-existing bad value can make the Weekly page unavailable until the row is corrected.

Acceptance checks:

- Only valid ISO dates inside the accepted product range are persisted.
- Invalid POSTs preserve the prior valid goal and return a safe validation response.
- Malformed stored values cannot crash Weekly or Waterfall reads.
- Valid create/update behavior and Personal/BFM/LL boundaries remain intact.

Why not fixed now:

Route validation and defensive-read changes were excluded from audit work block 3E.

## Waterfall Can Report Zero Months While Debt Remains

Status: open; discovered in work block 3E

Severity: medium financial-display correctness risk

Captured: 2026-07-18

Where seen: `web/routes/waterfall.py` and direct payoff-estimate reproduction

Revisit: Phase 4 Task 1 for payoff rounding repair; Phase 4 Task 2 for tracked coverage

Summary:

The payoff helper rounds the fractional month to the nearest integer. When positive debt is smaller than half of one month's positive surplus, the result becomes `0 months` even though the balance is not zero.

Impact:

The summary can claim immediate payoff while debt remains, creating a visible contradiction between the card balance and payoff estimate.

Acceptance checks:

- Positive debt and positive surplus produce at least one payoff month.
- Zero debt and non-positive surplus retain explicit empty/no-estimate behavior.
- Displayed months and payoff date use a documented rounding rule and reconcile at boundary values.

Why not fixed now:

Payoff calculation changes and tracked tests were outside the 3E audit scope.

## Waterfall Tax Fallback Can Disagree With Display And Crash On Non-Finite Input

Status: open; discovered in work block 3E

Severity: medium scenario-integrity and availability risk

Captured: 2026-07-18

Where seen: `web/routes/waterfall.py`, `web/templates/waterfall.html`, and deterministic invalid-input route probes

Revisit: Phase 4 Task 1 for normalization repair; Phase 4 Task 2 for tracked coverage

Summary:

An out-of-range 100% tax input resets the calculation to the 22% default but leaves `tax_rate_pct` at 100 for rendering, so the page displays 100% next to a 22% result. A direct `tax_rate=nan` request reaches integer conversion of a non-finite float and raises `ValueError`.

Impact:

The scenario can display an input different from the rate actually applied, and malformed direct input can make the Waterfall page unavailable.

Acceptance checks:

- Tax input must be finite, normalized once, and range-checked before calculation or rendering.
- The displayed rate, owner take-home, target revenue, and actual continuation use the same normalized value.
- Invalid, empty, boundary, and non-finite inputs return a safe default or validation response without a server error.

Why not fixed now:

Input normalization and tracked tests require separately confirmed implementation scope.

## Weekly And Waterfall Paths Lack Tracked Regression Coverage

Status: parked for Phase 4 regression coverage

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py`, work block 3E's 58-check primary probe, and focused ten-check confirmation probe

Revisit: Phase 4 Task 2, preferably alongside the related 3E repairs

Summary:

Work block 3E confirmed current-period effective spending, valid budget/target math, bill-source assembly, paydown pace, empty states, actual/target waterfall reconciliation, intended Personal/BFM sharing, LL denial, and read-only preservation. The tracked smoke suite contains no dedicated Weekly or Waterfall cases and does not reproduce the six functional defects found at date and input edges.

Impact:

Derived financial views can regress or preserve known defects without the maintained suite detecting incorrect dates, totals, payoff estimates, invalid-input failures, or entity-boundary changes.

Acceptance checks:

- Tracked tests use one deterministic all-entity dataset for Weekly and Waterfall reconciliation.
- Current, historical, cross-month/year, empty, invalid-input, and intended cross-entity cases are explicit.
- Each repaired 3E defect has a failing-before and passing-after regression case.
- Tests remain synthetic and require no production data, credentials, Plaid, OpenRouter, or external access.

Why not added now:

Tracked test expansion was explicitly excluded from audit work block 3E.

# Issues

These are known defects, risks, or rough edges. They are not active work unless promoted into a phase task and confirmed work block.

Phase 3 Task 7 is consolidated in `command-center/phase-3-findings-consolidation.md`. That catalog assigns stable IDs, explicit confidence, affected boundaries, sanitized reproductions, observed-versus-expected behavior, impacts, evidence sources, and dependency tags to the 55 Phase 3-derived entries below. The detailed acceptance checks remain authoritative in each matching issue section here.

The Task 7 snapshot contains 42 unresolved behavioral or policy findings, 10 regression-coverage items, and three findings resolved and released through work blocks 4A-4B. The catalog's dependency tags support Task 8 sequencing but do not authorize or preselect a repair order.

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

Status: boundary slice covered by work block 4E; remaining coverage parked for Phase 4 and demo review for Phase 5

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: retired `plan.md`, `scripts/smoke_test.py`, `scripts/seed_demo_data.py`, and work block 3D's 58-check temporary-database probe

Revisit: Phase 4 Task 2 for remaining broad coverage; Phase 5 for demo fidelity if still useful

Summary:

The legacy Short-Term Planning plan proposed dedicated goal CRUD, snapshot, budget, payoff, entity-isolation, and cross-entity smoke cases plus seeded goals and snapshots. Work block 3D confirmed that goal CRUD/status/delete, budget and subcategory persistence, effective split accounting, three-month averages, per-payroll budgets, action items, payoff engines when supplied correct rates, and entity-local Personal/BFM account choices work against temporary synthetic data. Work block 4E added maintained all-route Luxe Legacy denial, unchanged-database, account-name non-disclosure, and Personal/BFM boundary coverage. The tracked smoke suite still lacks broad dedicated planning calculation and lifecycle cases, and demo seeding still omits goals and snapshots.

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

Status: resolved locally in work block 4S; release not authorized

Severity: high financial-planning correctness risk

Captured: 2026-07-18

Where seen: `web/routes/short_term_planning.py`, migrated `account_balances.apr_bps`, and deterministic lock-plan reproduction

Revisit: separate publication gate only

Summary:

The direct payoff engine correctly applies the APR values it receives, but `lock_plan()` does not select `apr_bps` from linked accounts and hard-codes every card to 20%. In a synthetic avalanche plan with a 9.99% card listed before a 29.99% card, the stored month-one schedule sent the extra payment to the low-APR card. The resulting rounded balances were $288 on the low-APR card and $1,195 on the high-APR card, the opposite of avalanche ordering.

Impact:

Locked plans can recommend and display the wrong payment sequence, interest accumulation, and payoff trajectory. A user could make a financial decision from a schedule that appears account-specific but ignores the account APR data already stored by the application.

Acceptance checks:

- Linked account details pass the stored `apr_bps` value into payoff computation.
- Avalanche targets the highest APR and snowball targets the smallest current balance regardless of linked-account order.
- Missing APR behavior is explicit and does not silently make different cards equivalent.
- The saved narrative and month-by-month schedule reconcile to the same inputs and have tracked synthetic coverage.

Resolution:

Work block 4S passes each linked credit card's stored `apr_bps` into the locked payoff timeline and removes the hard-coded 20% substitution. A known zero APR remains valid; absent or negative APR returns controlled Cash Flow guidance before the existing strategy, monthly amount, target date, narrative, or schedule can change. Maintained temporary Personal and BFM coverage proves exact reversed-order avalanche cents for 9.99% and 29.99% cards, balance-ordered snowball behavior, narrative and saved-schedule reconciliation, zero-APR persistence, missing/negative zero-mutation rejection, Luxe Legacy denial, denied networking, and exact cleanup. The baseline and final full smoke suites and Python compilation pass locally. No migration, template, protected data, external access, GitHub durability, deployment, or live action occurred.

## Luxe Legacy Planning Denial Is Enforced Only On Page Entry

Status: resolved and released through work block 4E-R

Severity: high entity-boundary and hidden-data risk

Captured: 2026-07-18

Where seen: Long-Term and Short-Term Planning routes plus temporary Luxe Legacy and Personal databases

Revisit: none unless the boundary contract changes

Summary:

The two planning index routes redirect Luxe Legacy to the dashboard, but their supporting GET and POST routes do not enforce the same denial. With the LL entity selected, synthetic direct requests created a hidden LL planning item, goal, budget, and action item; exposed Personal cash-flow account names through the planning helper; and changed the Personal singleton planning inflation setting from 0 to 9.90%. The probe restored the synthetic setting afterward and removed its temporary data directory.

Impact:

The UI communicates that planning is unavailable to LL while direct routes can create unseen LL records and cross the intended boundary into Personal planning configuration and account-name metadata. This violates the explicit entity and LL planning boundary even though no real data or live system was accessed during the audit.

Acceptance checks:

- Every Long-Term and Short-Term Planning GET/POST helper applies the same LL denial as its index route.
- Denied requests leave all three entity databases unchanged and reveal no Personal/BFM account names.
- Personal/BFM Long-Term Planning sharing remains read-only for the secondary section and continues to work.
- Tracked tests exercise page and direct-route denial for item, settings, goal, snapshot, budget, action, and helper endpoints.

Resolution:

Work block 4E added one early Luxe Legacy denial guard to each planning blueprint. Maintained coverage enumerates all 21 registered Long-Term and Short-Term Planning route rules, proves no denied request reaches its handler, leaves all three temporary entity databases logically unchanged, exposes no Personal/BFM account names, and preserves Personal/BFM Long-Term sharing plus ordinary planning availability. Baseline and final smoke suites, compilation, cleanup, whitespace, dashboard refresh, and health checks passed. Work block 4E-R published source commit `1a277b0` to `main`; automatic Fly run `29694423318` and deploy job `88212585378` passed, and credential-free production health returned HTTP 200.

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

Status: open; discovered in work block 3A and confirmed on the Plaid path in work block 3G

Severity: high financial-data completeness risk

Captured: 2026-07-18

Where seen: `core/imports.py`, `web/routes/plaid.py`, work block 3A's import reproduction, and work block 3G's mocked Plaid reproduction

Revisit: Phase 4 Task 1 for repair design and Phase 4 Task 2 for tracked import/Plaid coverage

Summary:

`compute_transaction_id()` hashes only date, amount, and normalized description. Work block 3A showed that two imported rows differing by account collapse to one primary key. Work block 3G confirmed the same behavior with mocked Plaid input: two different Plaid transaction IDs on different accounts but with the same date, amount, and merchant stored one row and reported one new transaction. Exact re-delivery of the same Plaid ID remained idempotent.

Impact:

The importer can omit a legitimate transaction without surfacing an error, producing an incomplete ledger and understated or overstated downstream reporting. The audit did not inspect real data, so actual production occurrence is unknown.

Acceptance checks:

- Two legitimate transactions that differ by account or another stable source identity can coexist.
- Exact re-imports of the same source transaction remain deduplicated.
- Existing transaction relationships, including splits and vendor matches, have a safe preservation or migration path.
- Synthetic coverage proves both CSV/import and Plaid identity behavior while preserving exact Plaid re-delivery idempotency.

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

Status: resolved and released through work blocks 4M-4M-R

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

Work block 4M removed the nonexistent bank-side column dependency without a migration, made `vendor_transactions.matched_transaction_id` canonical, and added maintained all-entity exact, review, unmatched, stale, duplicate, concurrent-claim, rollback, denied-network, and cleanup coverage. Work block 4M-R published source commit `ffd42dd`, automatic Fly run `29748373589` passed, and credential-free production health returned HTTP 200.

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
- Item totals, quantity, tax/shipping treatment, raw vendor metadata, and parent totals reconcile in integer cents without inventing Ledger categories.
- Once valid Ledger categories exist, a matched multi-category order can create valid vendor-line-item splits without the standalone population script.

Result:

Work block 4N now saves each new Amazon or Henry Schein parent and every parsed child in one SQLite transaction, deduplicates parents by exact vendor, order ID, and integer-cent total, skips existing parents without implicit backfill, and rolls the parent back when any child fails. Maintained synthetic coverage uses generated Amazon CSV and Henry Schein XLSX inputs across Personal, BFM, and Luxe Legacy; preserves raw category metadata without assigning a Ledger category; verifies quantity and cents, exact reimport, normal preview/save handoff, temporary-payload consumption, denied networking, unrelated-row preservation, auto-split consumption, and exact cleanup. Migration 53 already supplied the required table, so no migration, production script, existing-row repair, protected data, or live action was needed. Category inference and domain enforcement remain Task 1L.3.

## Vendor Categorization Can Escape The Category Source Of Truth

Status: resolved locally in work block 4O; release not authorized

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

Result:

Work block 4O makes `categories.md` authoritative for new in-scope inference and acceptance writes. Vendor inference is entity-aware and falls back to `Needs Review` / `General` rather than inventing a mapping; Henry Schein equal-frequency category ties are stable across hash seeds; transaction batches, vendor-order saves, and accepted order matches prevalidate before any transaction, order, match, note, or alias mutation; and the dedicated `Skipped` action remains a workflow sentinel rather than a financial category. Maintained synthetic coverage proves valid and invalid behavior independently in Personal, BFM, and Luxe Legacy with denied networking and exact cleanup. Existing invalid-row detection and remediation remain separately gated, and no taxonomy, migration, protected-data, or live-system change occurred.

## Task 2 Import And Categorization Paths Lack Tracked Regression Coverage

Status: partly addressed through work blocks 4N and 4O

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and work block 3B's ephemeral 60-check probe

Revisit: Phase 4 Task 2, preferably alongside the related Task 2 repairs

Summary:

Work block 3B passed current synthetic behavior for CSV/PDF parsing, profiles, upload confirmation, Amazon/Henry parsing and deduplication, order matching, aliases, temporary-file cleanup, and entity isolation. Work block 4N adds maintained Amazon and Henry Schein parent-plus-line-item, preview/save, exact-reimport, rollback, integer-cents, auto-split, all-entity isolation, denied-network, and cleanup coverage. Work block 4O adds maintained entity-specific inference, cross-hash-seed tie, transaction-batch, vendor-order, accepted-match, zero-mutation, alias-protection, skip-sentinel, denied-network, and cleanup coverage. Remaining CSV/PDF profile, broader matching, and explicit undo coverage stays paired with its related repair work.

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

Status: resolved and released through work blocks 4H-4H-R

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

Resolution:

Work block 4H constructs the SQL with the maintained entity-specific exclusion clause instead of sending a literal helper token to SQLite. It also corrects debit minimum/maximum ordering and adds maintained temporary all-entity coverage for the direct helper, prepared report, rendered view, CSV, PDF, entity exclusions, empty and out-of-range behavior, read-only execution, and exact synthetic cleanup. Work block 4H-R published source commit `166bbd9`; automatic Fly run `29696691569` and deploy job `88218551351` passed, and credential-free production health returned HTTP 200.

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

## Non-BFM Entities Can Directly Access And Mutate Payroll

Status: resolved locally in work block 4D; release not authorized

Severity: high payroll/HR boundary risk

Captured: 2026-07-18

Where seen: `web/routes/payroll.py`, `web/templates/components/sidebar.html`, `README.md`, and temporary all-entity route probes

Revisit: Phase 4 Task 1 for route-level BFM enforcement; Phase 4 Task 2 for tracked boundary coverage

Summary:

Work block 4D added one payroll-blueprint guard that redirects Personal and Luxe Legacy before any payroll handler reaches storage or upload parsing. Maintained synthetic coverage enumerates all eight registered payroll routes, verifies both denied entities, preserves employee/pay-change/payroll-entry and temporary-payload state, and confirms the BFM paths remain available.

Impact:

The visible product boundary is only a hidden navigation link. A direct request can create or expose payroll/HR state in entities where the feature is not intended, creating policy ambiguity and future disclosure risk even though the temporary audit confirmed database isolation.

Acceptance checks:

- Every payroll read and mutation denies non-BFM entities before opening payroll tables.
- Personal and Luxe Legacy direct requests leave employee, pay-change, and payroll-entry counts unchanged.
- BFM roster, import, detail, spending, and HTMX behavior remain intact.
- Tracked tests cover page and mutation denial for both non-BFM entities.

Resolution evidence:

`web/routes/payroll.py`, `scripts/smoke_test.py`, and `command-center/logs/2026-07-19-bfm-only-payroll-boundary-4d.md`. GitHub durability and release remain a separate gate.

## Payroll Preview Duplicates An Exact Existing Employee

Status: resolved locally in work block 4P; release not authorized

Severity: high payroll-history integrity risk

Captured: 2026-07-18

Where seen: `web/templates/payroll.html`, `web/routes/payroll.py`, and a generated-XLSX preview/save confirmation probe

Revisit: Phase 4 Task 1 for stable assignment rendering and duplicate prevention; Phase 4 Task 2 for regression coverage

Summary:

The route correctly matches parsed entries to an existing same-name employee, but the template's loop-local assignment does not survive outside the loop. The preview therefore defaults to `Create new employee`; submitting that rendered default created a duplicate same-name roster row and assigned the paycheck to it.

Impact:

A normal import can split one person's roster, pay history, and payroll entries across duplicate employee IDs, corrupting employee detail and role-spending interpretation.

Acceptance checks:

- Exact matches render one stable existing-employee assignment.
- The default save path cannot create a duplicate for an already-matched employee.
- Explicit reassignment and genuinely unmatched new-employee creation remain available.
- Re-import preserves both employee and payroll-entry counts.

Resolution:

Work block 4P moves normalized-name assignment into explicit route data, renders the single exact existing employee as the selected default, preserves selection of another existing employee, offers creation only for genuinely unmatched names, and repeats the same rule during save so a forged `new` submission cannot create a duplicate. Generated-XLSX maintained coverage proves exact match, explicit reassignment, new creation, stable reimport counts, BFM-only behavior, denied networking, and exact cleanup.

## Payroll Peer Averages Mix Hourly And Salary Units

Status: resolved locally in work block 4R; release not authorized

Severity: high compensation-comparison correctness risk

Captured: 2026-07-18

Where seen: `web/routes/payroll.py`, `web/templates/payroll.html`, and a mixed-pay-type synthetic roster

Revisit: Phase 4 Task 1 for comparison-unit design and repair; Phase 4 Task 2 for tracked coverage

Summary:

Peer averages group active employees by role but ignore pay type. One hourly provider and one annual-salary provider were averaged as raw cents, then the result was formatted as hourly for the hourly employee and annual for the salaried employee.

Impact:

The peer card can present a materially meaningless compensation comparison that may influence pay decisions.

Acceptance checks:

- Peer cohorts distinguish hourly and salary compensation or normalize both to one documented comparable unit.
- Display units match the calculation unit for every employee.
- Mixed, single-member, inactive, zero-rate, and empty cohorts have explicit behavior.
- Tracked tests reconcile the displayed comparison to deterministic source rates.

Resolution:

Work block 4R groups active employees by both maintained role and pay type, excludes the selected employee and inactive rows from contributing, and performs no annualization or hourly/salary conversion. Employee detail returns an integer-cent peer average plus peer count when another comparable employee exists, including a real zero average, and returns an explicit empty value when none exists. The modal states the same-role and same-pay-type basis, preserves `/hr` and `/yr`, and displays `No comparable peers` for an empty cohort. Maintained synthetic coverage verifies mixed units, multiple peers, self exclusion, inactive contributors and selected employees, zero-rate and empty cohorts, BFM-only denial, denied networking, rendered output, and exact cleanup.

## Payroll Employee Inputs Are Not Safely Normalized

Status: resolved locally in work block 4Q; release not authorized

Severity: medium data-integrity and availability risk

Captured: 2026-07-18

Where seen: `web/routes/payroll.py` and direct synthetic employee-create probes

Revisit: Phase 4 Task 1 for domain and numeric validation; Phase 4 Task 2 for regression coverage

Summary:

A direct request persisted a role outside the maintained payroll role domain. An invalid pay type reached SQLite's check constraint and raised `IntegrityError`, while a non-finite rate raised `OverflowError` during cents conversion.

Impact:

Malformed requests can create undefined role groupings or fail the route instead of preserving valid data and returning a controlled validation response.

Acceptance checks:

- Role, pay type, status, dates, and identifiers are checked against maintained domains before persistence.
- Pay rates must be finite, non-negative, and within a documented bound.
- Invalid requests leave prior data unchanged and return a controlled response.
- Valid create/update and rate-history behavior remains intact.

Resolution:

Work block 4Q adds one shared pre-mutation employee validator across manual create, manual update, and import-created roster rows. Maintained roles, pay types, statuses, exact optional dates, entity-local employee and assignment IDs, payload-linked imported names, duplicate normalized assignments, optional trimmed Phoenix codes, and decimal rates from zero through `$999,999,999.99` now have explicit contracts. Invalid, non-finite, negative, extreme, forged, duplicate, and missing values return controlled sanitized outcomes with exact zero mutation. Forced post-history and post-employee import failures prove rate history, employee changes, and payroll entries roll back together. Baseline and final full smoke suites, compilation, cleanup, denied networking, dashboard refresh, and health checks pass locally.

## Canceling Payroll Preview Retains The Parsed Payload

Status: resolved locally in work block 4P; release not authorized

Severity: medium payroll-data retention risk

Captured: 2026-07-18

Where seen: payroll temporary-payload helpers, preview Cancel behavior, and an isolated synthetic temp directory

Revisit: Phase 4 Task 1 for explicit cancel cleanup and payload lifecycle; Phase 4 Task 2 for tracked coverage

Summary:

Successful save consumes its temporary JSON payload, but navigating back through the preview's Cancel link leaves the parsed employee, paycheck, amount, and filename payload until the general age-based cleanup removes files older than four hours.

Impact:

Cancel does not end retention of an abandoned payroll payload, extending the lifetime of sensitive HR information beyond the user's apparent workflow.

Acceptance checks:

- Cancel invalidates and removes its exact payload immediately.
- Save, cancel, missing, reused, expired, and malformed keys have deterministic behavior.
- Cleanup never removes unrelated payloads and does not rely on Flask cookie storage.
- Tracked tests use an isolated temporary directory and leave it empty.

Resolution:

Work block 4P replaces preview's passive link with an explicit BFM-only POST cancel action, validates opaque keys without path reinterpretation, writes new payloads with mode `0600`, and consumes only the exact payload. Maintained isolated-directory coverage proves save, cancel, missing, reused, expired, malformed, unrelated-payload preservation, idempotency, and empty final cleanup.

## Malformed Payroll XLSX Raises Instead Of Returning An Import Error

Status: resolved locally in work block 4P; release not authorized

Severity: medium import-availability risk

Captured: 2026-07-18

Where seen: `core/payroll_parser.py`, `web/routes/payroll.py`, and a malformed synthetic upload

Revisit: Phase 4 Task 1 for parser error normalization; Phase 4 Task 2 for tracked coverage

Summary:

A structurally valid XLSX without a Phoenix header returns the intended controlled error state, but non-XLSX bytes carrying an `.xlsx` filename propagate a pandas/openpyxl `ValueError` from the upload route.

Impact:

A corrupt or mislabeled payroll export can produce a server error instead of an actionable import message.

Acceptance checks:

- Malformed, headerless, empty, unsupported, and valid multi-section files return explicit controlled outcomes.
- Parser exceptions are normalized without exposing file contents or internals.
- No temporary payload is retained when parsing fails.
- Valid import preview/save and duplicate behavior remain intact.

Resolution:

Work block 4P places one sanitized error boundary around workbook-engine loading, rejects unsupported filename types before parsing, and retains no payload for corrupt, mislabeled, empty, unsupported, or headerless outcomes. Generated valid multi-section coverage confirms normal preview behavior remains available.

## Payroll Lifecycle Paths Lack Tracked Regression Coverage

Status: resolved locally through work blocks 4D, 4P, 4Q, and 4R; 4R release not authorized

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py`, work block 3F's 40-check primary probe, and focused seven-check confirmation probe

Revisit: Phase 4 Task 2, preferably alongside the related payroll repairs

Summary:

Work block 4D added maintained coverage for the payroll routes, Personal/Luxe Legacy denial, unchanged denied-state snapshots, temporary-payload preservation, and normal BFM roster/detail/import/spending availability. Work block 4P extends that maintained matrix to exact preview/save matching, reassignment, new creation, reimport, payload permissions and lifecycle, malformed workbook outcomes, valid multi-section parsing, all-entity isolation, denied networking, and exact cleanup. Work block 4Q adds manual and import-created roster-domain validation, decimal-rate boundaries, controlled rejection, exact zero-mutation snapshots, valid rate-history behavior, and forced update/import rollback. Work block 4R completes the matrix with same-role/same-pay-type peer cohorts, self and inactive exclusion, zero-versus-empty behavior, display units and labels, BFM-only denial, denied networking, and exact cleanup.

Impact:

Payroll behavior can regress or retain known defects without maintained synthetic verification detecting incorrect employees, compensation comparisons, access boundaries, payload cleanup, or imports.

Acceptance checks:

- Tracked tests generate payroll workbooks at runtime and use temporary all-entity databases.
- Parser, roster/history, preview/save, duplicate import, aggregation, delete cascade, cleanup, and BFM-only boundaries are explicit.
- Every repaired 3F defect has a failing-before and passing-after regression case.
- Tests require no real payroll/HR data, credentials, production access, or external calls.

Resolution:

Every repaired 3F defect now has maintained synthetic coverage. The full suite requires no real payroll/HR data, retained uploads, credentials, production access, or external calls. The 4R compensation slice is locally verified but remains unpublished pending a separate release decision.

## Plaid Persistence Errors Can Advance The Cursor Past Missing Data

Status: resolved locally in work block 4I; release not authorized

Severity: high financial-data completeness risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py` and a deterministic forced-SQLite-failure probe

Revisit: Phase 4 Task 1 for transactional repair; Phase 4 Task 2 for tracked coverage

Summary:

`_upsert_plaid_transaction()` catches every exception and returns zero, the same result used for an exact duplicate. A synthetic trigger forced the insert to fail; `_sync_entity()` returned no error and committed the next cursor while the transaction remained absent.

Impact:

A transient schema, constraint, categorization, or write failure can move the incremental cursor beyond a transaction that never entered the ledger.

Acceptance checks:

- Exact duplicates and persistence errors have distinct outcomes.
- Any transaction persistence error rolls back or withholds the item cursor and returns a sanitized item error.
- A later retry can ingest the missed transaction without manual cursor repair.

Resolution:

Work block 4I now applies each item's accepted additions, modifications, removals, final cursor, and `last_synced` in one SQLite transaction. Exact redelivery remains an explicit no-op, while genuine persistence failures propagate to the existing item error path, roll back prior mutations, preserve the starting cursor and timestamp, and report no rolled-back counters. Maintained Personal, BFM, and Luxe Legacy checks cover multi-page aggregation, success, exact redelivery, enabled-account filtering, forced add/modify/remove/cursor-write failure, retry from the original cursor, split preservation, denied outbound sockets, and exact cleanup. Publication remains separately gated.

## Plaid Balance Reconciliation Is Unsafe On Disabled Or Partially Failed Items

Status: resolved locally in work block 4J; release not authorized

Severity: high account-state integrity risk

Captured: 2026-07-18

Where seen: `web/routes/cashflow.py` and mocked multi-item balance refreshes

Revisit: Phase 4 Task 1 for per-item reconciliation; Phase 4 Task 2 for tracked coverage

Summary:

When one item refreshed and a sibling raised, the successful account IDs became the global keep-set and the failed item's cached balance row was deleted. When every account was disabled, the empty keep-set skipped cleanup and retained the disabled row.

Impact:

A partial API failure can erase useful cached account state, while disabling every account can leave an unwanted balance visible indefinitely.

Acceptance checks:

- Reconciliation is scoped per successfully fetched item and preserves prior rows on failure.
- Disabled or removed accounts are consistently removed after an authoritative response.
- Manual accounts remain untouched in every success, empty, disabled, and failure case.

Resolution:

Work block 4J now records account freshness per Plaid item and reconciles cached rows only after that item's successful mocked response. Enabled non-investment accounts are retained, authoritative disabled, investment, and removed accounts are cleaned even when the keep set is empty, a failed sibling preserves its rows and marker, and manual rows are never candidates. Maintained Personal, BFM, and Luxe Legacy coverage proves partial failure, empty keep-set cleanup, fresh-sibling isolation, denied networking, and exact cleanup. Publication remains separately gated.

## Normal Cash Flow Refresh Skips Plaid Liabilities

Status: resolved locally in work block 4J; release not authorized

Severity: high cash-flow and payment accuracy risk

Captured: 2026-07-18

Where seen: `web/routes/cashflow.py` and a mocked first-load balance/liability probe

Revisit: Phase 4 Task 1 for freshness separation; Phase 4 Task 2 for tracked coverage

Summary:

Cash Flow refreshes balances first, which writes a current `updated_at`; the liability helper then uses that same timestamp as its cache guard. On the normal mocked path, liabilities were never fetched and minimum payment plus due date were not applied.

Impact:

Credit-card planning can display stale or missing payment obligations even after the page refreshes the balance.

Acceptance checks:

- Balance and liability freshness are separate or refreshed atomically.
- A normal stale load fetches and applies both data sets without unnecessary repeat calls.
- Liability unavailability and API errors remain distinguishable.

Resolution:

Work block 4J adds separate nullable per-item account and liability refresh markers through additive migration 58. A normal stale load now fetches and applies both data sets; an account refresh cannot suppress liabilities; successful empty liability responses advance only the liability marker without clearing last-known-good fields; and failures preserve both fields and the prior marker. Maintained all-entity coverage proves populated upgrade, normal application, failure preservation, successful empty response, and denied networking. Publication remains separately gated.

## Linking A Plaid Institution Can Delete Unrelated Manual Accounts

Status: resolved locally in work block 4J; release not authorized

Severity: high destructive account-state risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py` exchange-token route and a mocked connection probe

Revisit: Phase 4 Task 1 for explicit placeholder matching; Phase 4 Task 2 for tracked coverage

Summary:

The exchange route deletes every manual balance whose first word matches the institution or a connected account. Linking synthetic Chase data removed a distinct manual `Chase Emergency Reserve` row.

Impact:

Connecting one bank can silently delete manually maintained balance state for another similarly named account.

Acceptance checks:

- Manual rows are removed only through explicit stable placeholder identity or user confirmation.
- Similar names do not delete distinct state, and failed exchange paths leave every row unchanged.

Resolution:

Work block 4J removes the first-word institution/account-name deletion heuristic. Plaid Link now persists only stable Plaid item/account state and preserves every manual account until an explicit stable placeholder identity or user-confirmed merge exists. Maintained Personal, BFM, and Luxe Legacy route coverage proves a similar-name `Chase Emergency Reserve` row survives successful linking and a later failed account fetch rolls back the attempted item while preserving the manual row. Publication remains separately gated.

## Plaid Balance Freshness Uses An Entity-Wide Maximum

Status: resolved locally in work block 4J; release not authorized

Severity: medium account-freshness risk

Captured: 2026-07-18

Where seen: `web/routes/cashflow.py` and a mixed-freshness account probe

Revisit: Phase 4 Task 1 for item/account freshness; Phase 4 Task 2 for tracked coverage

Summary:

The cache guard checks `MAX(updated_at)` across all Plaid balance rows. One fresh synthetic account suppressed refresh while a sibling was two hours stale.

Impact:

An account can remain stale when another continues receiving recent timestamps, producing a mixed-age view that appears current.

Acceptance checks:

- Freshness is evaluated per item/account or by a complete successful refresh marker.
- One fresh row or a partial failure cannot mark stale siblings current.

Resolution:

Work block 4J replaces the entity-wide row maximum with separate successful-refresh markers on each Plaid item. One fresh item now skips only its own account or liability call, while stale siblings refresh independently and failed items remain stale. Account toggles invalidate both markers so newly disabled or re-enabled state cannot be hidden behind the prior cache window. Maintained all-entity coverage proves mixed freshness, marker invalidation, failure preservation, denied networking, and cleanup. Publication remains separately gated.

## Missing Plaid Modified Rows Are Reported As Updated

Status: resolved locally in work block 4K; release not authorized

Severity: medium sync-observability risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py` and a mocked modified-event probe

Revisit: Phase 4 Task 1 for row-count handling; Phase 4 Task 2 for tracked coverage

Summary:

The modified-event path increments `total_modified` without checking SQLite row count. A modification for an absent Plaid ID reported one update while changing no row.

Impact:

Sync summaries can claim reconciliation while records remain missing, including records lost to the confirmed identity collision.

Acceptance checks:

- Modified and removed counts reflect actual affected rows.
- A missing target becomes an explicit safe recovery/error path before cursor advancement.

Resolution:

Work block 4K uses the SQLite update row count and requires exactly one stored target for every modified Plaid event. A missing or ambiguous target now fails through the stable per-item persistence path, rolls back that item's earlier mutations, and preserves its cursor and `last_synced` for retry. Removal counts use actual deleted transaction rows, while already-absent removals remain zero-count idempotent successes. Maintained all-entity coverage proves truthful counters, missing-target rollback, healthy-sibling continuation, cursor preservation, split cleanup, absent-removal redelivery, denied networking, and exact cleanup. Publication remains separately gated.

## One Corrupt Plaid Token Aborts Valid Sibling Items

Status: resolved locally in work block 4K; release not authorized

Severity: medium item-isolation and reliability risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py` and a mixed valid/corrupt synthetic token probe

Revisit: Phase 4 Task 1 for per-item decryption isolation; Phase 4 Task 2 for tracked coverage

Summary:

`_sync_entity()` decrypts every item token before entering its per-item exception boundary. One corrupt synthetic ciphertext raised before a valid sibling item could sync.

Impact:

A single damaged token can block every connected institution in that entity instead of producing one sanitized item-level failure.

Acceptance checks:

- Decryption happens inside the per-item boundary, healthy siblings continue, and failed item reporting exposes no token material.

Resolution:

Work block 4K moves access-token decryption inside the per-item exception boundary and returns only stable sanitized item errors. A corrupt item makes no Plaid request, keeps its cursor and timestamp, and cannot prevent healthy siblings before or after it from committing. Maintained Personal, BFM, and Luxe Legacy cases cover corrupt-first and corrupt-last order, sanitized output without token or ciphertext material, successful sibling counters and persistence, denied networking, and exact cleanup. Publication remains separately gated.

## Primary Plaid Paths Lack Tracked Regression Coverage

Status: partially addressed through work block 4K; remaining broad primary Plaid coverage stays parked

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and work block 3G's 56-check mocked probe plus deterministic confirmation pass

Revisit: Phase 4 Task 2, preferably alongside the related Plaid repairs

Summary:

The tracked smoke suite renders Connected Accounts but does not exercise token/item persistence, account lifecycle, balance/liability refresh, incremental ingestion, pagination, cursor safety, deduplication, item failures, or three-entity sync isolation.

Impact:

Passing primary Plaid behavior can regress, and the eight confirmed defect clusters can persist or change, without maintained synthetic detection.

Acceptance checks:

- Tests use fake tokens, mocked SDK/HTTP entry points, blocked outbound calls, and temporary all-entity databases.
- Passing connection, account, balance, liability, transaction, pagination, deduplication, cursor, and isolation paths are explicit.
- Every repaired 3G defect has a failing-before and passing-after regression case.

Remaining gap:

Work block 4I adds the maintained transaction-pagination, cursor, rollback, exact-redelivery, enabled-account, three-entity, denied-network, and cleanup slice. Work block 4J adds populated freshness migration, per-item reconciliation, disabled/removed cleanup, manual-account preservation, normal and empty liability refresh, failure preservation, mixed freshness, account-toggle invalidation, similar-name link safety, denied-network, all-entity isolation, and cleanup coverage. Work block 4K adds corrupt-first and corrupt-last token isolation, sanitized errors, missing-modification rollback and cursor preservation, successful sibling continuation, actual modified/removed counts, absent-removal idempotency, denied networking, and exact cleanup. Broader connection and operator-path coverage not tied to these repaired defects remains parked for future paired work rather than widening Task 1J.

## Scheduled Plaid Sync Can Report Partial Failure As Success

Status: resolved locally in work block 4G; release not authorized

Severity: high operational reliability risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py`, `.github/workflows/daily-plaid-sync.yml`, and mocked entity-result probes

Revisit: Phase 4 Task 1 for response-contract repair; Phase 4 Task 2 for workflow-visible regression coverage

Result:

`/plaid/sync-all` now returns HTTP 200 with `ok: true` and `status: success` only when every entity result is error-free. One or more nested errors return HTTP 502 with `ok: false` and either `partial_failure` or `failure`; error-free skipped entities remain successful, and the existing per-entity results are preserved without wider error detail.

Impact:

The existing scheduled workflow's `curl --fail` contract now receives a failing HTTP result when any entity reports errors.

Acceptance checks:

- Top-level status and HTTP status reflect nested errors and distinguish complete success, partial success, contention, configuration failure, and total failure.
- Sanitized per-entity results remain available without secret or financial-row output.
- A mocked workflow-visible regression test proves `curl --fail` receives failure for partial sync errors.

Verification:

Maintained synthetic coverage uses fake secrets and mocked entity results to verify complete success, harmless skips, partial and total failure, bearer/configuration/contention behavior, unchanged exception and lock release semantics, entity order, preserved sanitized results, denied outbound networking, and an actual localhost-only `curl --fail` exit 22. Release remains separately gated.

## Scheduled And Public Sync Paths Lack Shared Cross-Process Coordination

Status: resolved locally in work block 4L; release not authorized

Severity: high cursor and financial-data consistency risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py`, `web/routes/kristine.py`, `Dockerfile`, and mocked lock-contention probes

Revisit: Phase 4 Task 1 for one canonical coordination design; Phase 4 Task 2 for concurrency coverage

Summary:

The scheduled and public paths use distinct `threading.Lock` objects, and each proceeded while the other's lock was held. Those locks and the public 15-minute throttle are process-local while production starts two Gunicorn workers.

Impact:

Scheduled, manual, or public-triggered syncs can overlap against the same SQLite rows and Plaid cursors, risking duplicate work, lock errors, stale cursor writes, or inconsistent results.

Acceptance checks:

- One coordination mechanism covers all sync entry points across production workers.
- Contention is explicit and cannot perform partial database work.
- Cursor writes remain monotonic and coupled to durable event application under concurrent attempts.
- Public throttling is atomic at the required deployment scope.

Resolution:

Work block 4L replaces the separate module-local sync locks with one non-blocking `fcntl.flock` lease on a stable mode-0600 file under `DATA_DIR`. Separate opens contend within one process and across the two Gunicorn workers; normal close and SIGKILL release are maintained-test proven; manual, scheduled, and dashboard-triggered entry points all use the same lease; and contention performs no partial sync work. The stable lock file is never unlinked and is not itself lock state. Release remains separately gated.

## Public Background Sync Advances Past Removed Plaid Events

Status: resolved locally in work block 4L; release not authorized

Severity: high financial-data correctness risk

Captured: 2026-07-18

Where seen: `web/routes/kristine.py` and a temporary-database removed-event reproduction

Revisit: Phase 4 Task 1 for canonical sync semantics; Phase 4 Task 2 for cursor/removal coverage

Summary:

The public worker processes added and modified events but ignores removed events before committing `next_cursor`. A synthetic removed transaction remained stored after the cursor advanced.

Impact:

Removed Plaid transactions can remain permanently in the ledger because ordinary incremental replay starts after the discarded event.

Acceptance checks:

- The public path uses the canonical removal and split-cleanup behavior.
- Cursor movement occurs only after every event is durably applied.
- Failure before removal completion withholds or rolls back the cursor.

Resolution:

The dashboard worker now calls the maintained `_sync_entity` core instead of a duplicate add/modify loop. Maintained dashboard-triggered synthetic coverage proves a removed transaction and its split are deleted in the same item transaction that advances the cursor, while the full primary Plaid suite continues to prove rollback and retry behavior. Release remains separately gated.

## Public Background Sync Includes Vendor Plaid Items

Status: resolved locally in work block 4L; release not authorized

Severity: high workflow and data-boundary risk

Captured: 2026-07-18

Where seen: `web/routes/kristine.py`, the `is_vendor` schema boundary, and a temporary all-entity probe

Revisit: Phase 4 Task 1 for item filtering or canonical sync consolidation; Phase 4 Task 2 for vendor-boundary coverage

Summary:

The public worker selects every `plaid_items` row rather than filtering `is_vendor = 0`. A synthetic vendor item was consumed through the normal spending-transaction and cursor path despite having a separate vendor-transactions workflow.

Impact:

Vendor payment-platform data can enter the wrong table and its cursor can be advanced outside the vendor import workflow.

Acceptance checks:

- Normal spending sync never reads or advances vendor items.
- Vendor items remain owned by the vendor workflow unless a new explicit architecture replaces both paths.
- Tracked all-entity tests prove table, cursor, and item-type isolation.

Resolution:

The dashboard worker now reuses `_sync_entity`, whose item query explicitly selects `is_vendor = 0`. Maintained synthetic coverage seeds spending and vendor items, proves only the spending item reaches mocked Plaid, and verifies the vendor cursor remains unchanged while the spending removal commits. Release remains separately gated.

## One Scheduled Entity Exception Aborts Healthy Later Entities

Status: resolved locally in work block 4L; release not authorized

Severity: medium all-entity reliability risk

Captured: 2026-07-18

Where seen: `web/routes/plaid.py` and a mocked BFM exception between Personal and Luxe Legacy

Revisit: Phase 4 Task 1 for explicit entity-failure semantics; Phase 4 Task 2 for fanout coverage

Summary:

An uncaught BFM exception returned a generic 500 and prevented Luxe Legacy from running. The lock released and the exception marker did not leak, but the response contained no structured record of completed and skipped entities.

Impact:

One entity can starve healthy later entities, and operators cannot distinguish completed, failed, and unattempted entities from the response.

Acceptance checks:

- Per-entity continuation or deliberate fail-fast behavior is explicit.
- Sanitized completion state identifies successful, failed, and unattempted entities.
- Retry semantics do not duplicate or skip cursor work.

Resolution:

The scheduled route now initializes and syncs each configured entity inside its own post-authorization exception boundary. Unexpected failures become the standard sanitized result shape with `errors: ["entity sync failed"]`; later entities continue; partial versus all-entity failure remains truthful; raw exception text is absent from JSON; and the shared lease releases after every disposition. Maintained coverage proves all three attempts occur after repeated synthetic exceptions. Release remains separately gated.

## Sync-All Runs Entity Setup Before Bearer Validation

Status: resolved locally in work block 4L; release not authorized

Severity: medium authorization-side-effect risk

Captured: 2026-07-18

Where seen: `web/__init__.py`, `web/routes/plaid.py`, and a missing-bearer temporary-directory probe

Revisit: Phase 4 Task 1 for request-hook boundary repair; Phase 4 Task 2 for unauthorized side-effect coverage

Summary:

The app's normal entity setup does not skip `/plaid/sync-all`, despite a nearby context comment. A missing-bearer request was rejected by the route only after the selected entity database was initialized and category synchronization ran.

Impact:

Unauthorized requests are not side-effect free and can trigger unnecessary database work before the endpoint's actual authorization check.

Acceptance checks:

- The cron endpoint bypasses browser entity setup and validates bearer authorization before database mutation.
- Missing and invalid bearer requests leave every entity database unchanged.
- Normal authorized all-entity iteration remains correct.

Resolution:

`/plaid/sync-all` is now explicitly exempt from browser session authentication and normal entity setup while retaining POST-only, CSRF-exempt, bearer-protected behavior. A fresh configured-auth app proves missing bearer returns 401 rather than a login redirect without entity initialization or category synchronization; correct bearer reaches the view and then initializes Personal, BFM, and Luxe Legacy in order. Bearer comparison is constant-time. Release remains separately gated, and the source-derived possibility that deployed scheduled requests currently stop at a green 302 remains unverified until a separately authorized release check.

## Failed Public Worker Launch Consumes Its Throttle Window

Status: resolved locally in work block 4L; release not authorized

Severity: medium background-sync availability risk

Captured: 2026-07-18

Where seen: `web/routes/kristine.py` and a mocked thread-start failure

Revisit: Phase 4 Task 1 for launch/throttle ordering; Phase 4 Task 2 for failure coverage

Summary:

The `/k/` route updates `_last_sync_time` before starting its daemon thread. A synthetic start failure returned 500 but suppressed another attempt in that worker for 15 minutes.

Impact:

A transient local launch failure delays recovery and turns a page view into an error without any sync beginning.

Acceptance checks:

- Throttle state advances only after successful worker launch or rolls back on failure.
- Launch failure produces a controlled response and remains immediately retryable under the chosen policy.

Resolution:

The dashboard route now serializes throttle and launch state inside one process, acquires the shared lease before thread creation, updates the throttle only after `Thread.start()` succeeds, transfers the lease to the worker on success, and releases it immediately while preserving the old timestamp on failure. Maintained deterministic coverage proves successful transfer, failed-start immediate retry, contention without throttle consumption, and throttled requests without lease churn. Release remains separately gated.

## Background Sync Entry Points Lack Tracked Regression Coverage

Status: resolved locally through work blocks 4G and 4L; release not authorized

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and work block 3H's repeated 32-check mocked probe

Revisit: Phase 4 Task 2, preferably alongside the related entry-point repairs

Summary:

Work block 4G adds maintained `/plaid/sync-all` coverage for bearer, configuration, configured entity order, complete success, harmless skip, partial and total error results, contention, exception/lock release, sanitized per-entity results, and workflow-visible `curl --fail` behavior. Public `_background_sync`, cross-path coordination, persistence/cursor, vendor scope, launch throttling, and remaining entry-point behavior stay parked.

Impact:

Bearer/CSRF behavior, workflow-visible partial errors, cross-path coordination, public throttling, item selection, removed events, cursor safety, and failure containment can regress without maintained detection.

Acceptance checks:

- Tests use fake environment values, mocked sync/downstream seams, denied outbound sockets, and temporary all-entity databases.
- Passing request, lock-release, entity-scope, and failure-containment behavior is explicit.
- Each repaired 3H defect has failing-before and passing-after regression coverage.

Resolution:

Work block 4G maintains workflow-visible result coverage. Work block 4L adds same-process separate-open contention, real two-process contention, normal release, SIGKILL cleanup, manual/scheduled/dashboard mutual exclusion, configured-auth bearer ordering, per-entity continuation and sanitization, successful and failed launch behavior, dashboard-triggered removal/cursor atomicity, vendor isolation, one net Luxe Legacy bridge invocation, mocked Plaid, denied sockets, temporary all-entity databases, and exact cleanup. The full maintained suite passes locally; release remains separately gated.

## Luxe Legacy Owner Draw Is Mirrored Despite The Exclusion Intent

Status: resolved locally in work block 4F; release not authorized

Severity: high downstream-data boundary risk

Captured: 2026-07-18

Where seen: `core/luxury_bridge.py`, `categories.md`, and the repeated mocked 3I payload probe

Revisit: a separately authorized release block if Ryan wants this local repair published

Summary:

The bridge comment says owner draws are not sale or purchase activity and should be excluded, but `EXCLUDE_CATS` uses `Owner Contribution`. LL defines `Owner Draw [Personal]` and does not define `Owner Contribution`, so a synthetic Owner Draw row entered the downstream payload.

Impact:

When the optional bridge is configured, a transaction type explicitly intended to remain outside the matching mirror can cross the downstream boundary and clutter or distort sale/purchase matching.

Acceptance checks:

- Bridge exclusions derive from or are explicitly reconciled with the maintained LL category contract.
- `Owner Draw` is omitted without suppressing valid LL sale or purchase categories.
- Scheduled and public bridge seams preserve the same corrected selection behavior.

Resolution:

Work block 4F replaced the nonexistent LL `Owner Contribution` mirror exclusion with the maintained `Owner Draw` category. Maintained synthetic coverage reproduced the original leak before the repair and now proves Owner Draw, Internal Transfer, and Credit Card Payment stay out while valid Cost of Goods and Income rows remain eligible. The direct bridge reads only Luxe Legacy and leaves all three temporary databases unchanged; scheduled and public sync seams invoke the mirror only for Luxe Legacy; fake configuration, mocked HTTP, and denied sockets prevent any live request. The repair remains local-only pending separate durability authorization.

## Luxe Legacy Mirror Idempotency Contract Permits Duplicate Conflict Keys

Status: open; discovered in work block 3I

Severity: high downstream correctness and availability risk

Captured: 2026-07-18

Where seen: `core/db.py`, `core/luxury_bridge.py`, and a repeated mocked duplicate-Plaid-ID probe

Revisit: Phase 4 Task 1 for local and downstream contract repair; Phase 4 Task 2 for duplicate-key coverage

Summary:

The local transaction schema creates a non-unique index on `plaid_transaction_id`. Two synthetic rows with the same Plaid ID were accepted and submitted in one bridge request. The request declares merge-duplicates but does not explicitly name `plaid_transaction_id` as its conflict target. The actual remote unique constraint and response were intentionally not inspected.

Impact:

One duplicate local key can make an all-eligible-row mirror batch ambiguous or fail as a unit, while the upstream Ledger sync still reports success because bridge failures are isolated and return zero.

Acceptance checks:

- The local schema or payload builder prevents duplicate downstream conflict keys in one request.
- The tracked downstream schema or request explicitly establishes `plaid_transaction_id` as the conflict key.
- Duplicate handling is deterministic, preserves the Ledger source of truth, and cannot silently drop an unrelated eligible row.
- Failure and recovery behavior has synthetic regression coverage without live downstream access.

Why not fixed now:

Schema, bridge, downstream-contract, and tracked-test changes were excluded from work block 3I.

## Luxe Legacy Mirror Accepts Empty Plaid Transaction IDs

Status: open; discovered in work block 3I

Severity: medium downstream validation risk

Captured: 2026-07-18

Where seen: `core/luxury_bridge.py` and the repeated mocked 3I eligibility probe

Revisit: Phase 4 Task 1 for selection validation; Phase 4 Task 2 for malformed-key coverage

Summary:

The bridge requires `plaid_transaction_id IS NOT NULL` but does not reject an empty string. A synthetic row with an empty Plaid ID entered the downstream payload as an idempotency key.

Impact:

Malformed local state can produce an invalid or colliding downstream request instead of being skipped or surfaced explicitly.

Acceptance checks:

- Only non-empty, normalized Plaid transaction IDs qualify for mirroring.
- Malformed identifiers are skipped or reported without affecting valid rows.
- Personal and BFM remain untouched and the Ledger source rows remain intact.

Why not fixed now:

Product repair and tracked coverage were excluded from work block 3I.

## Luxe Legacy Downstream Mirror Lacks Tracked Regression Coverage

Status: partly addressed by the focused work block 4F selection-boundary slice

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and work block 3I's repeated mocked bridge probe

Revisit: Phase 4 Task 2, preferably alongside mirror eligibility and idempotency repairs

Summary:

The maintained smoke suite now exercises the Owner Draw selection boundary, valid LL eligibility, LL-only storage access, unchanged entity databases, and scheduled/public LL-only invocation with fake configuration, mocked HTTP, and denied outbound sockets. Broader no-op, request-shape, failure-isolation, empty-ID, duplicate-key, and downstream-contract coverage remains for Task 1O or later separately gated work.

Impact:

Configuration no-ops, LL-only invocation, selection rules, authentication and payload shape, conflict-key behavior, timeout isolation, and Personal/BFM non-mutation can regress without maintained detection.

Acceptance checks:

- Tests use fake configuration, temporary all-entity databases, mocked HTTP and sync dependencies, and denied outbound sockets.
- Passing no-op, request-shape, failure-isolation, and entity-boundary behavior is explicit.
- Every repaired 3I finding has failing-before and passing-after coverage.

Remaining coverage:

Work block 4F intentionally added only the focused `P3-3I-01` selection slice. The remaining bridge contract and idempotency coverage stays parked with the corresponding unrepaired findings.

## Main Authentication Boundary Returns Protected HTML And Accepts A Client-Exposed Digest

Status: resolved and released through work blocks 4A-4B and PR #86

Severity: high authentication and financial-confidentiality risk

Captured: 2026-07-18

Where seen: `web/__init__.py`, `web/templates/base.html`, and the repeated fake-secret 3J request probe

Revisit: Phase 4 Task 1 before ordinary product repairs; Phase 4 Task 2 for request-class coverage

Summary:

Unauthenticated full-page requests receive complete protected server-rendered HTML behind a client overlay, while HTMX and JSON requests correctly receive 401. The rendered page publishes the digest used by the client gate, and a local app configured with that digest accepted the extracted value directly at `/auth/verify`.

Impact:

The overlay is not a confidentiality boundary. Protected financial HTML can be read without completing server authentication, and the published digest can act as a reusable credential when client and server configuration match.

Acceptance checks:

- Unauthenticated full-page, HTMX, and JSON requests cannot receive protected data.
- Password verification occurs server-side without publishing a reusable credential equivalent.
- Successful authentication establishes a secure session and failed authentication cannot dismiss the protection layer.
- Synthetic tests cover configured and unauthenticated request classes without real credentials.

Resolution:

Work block 4A redirected full-page requests to a standalone login before entity setup or protected rendering, kept unauthenticated HTMX/JSON at 401, moved password verification entirely server-side, removed the published digest and `/auth/verify`, and marked dynamic responses no-store. Work block 4B released the repair through PR #86; Fly Deploy and credential-free production redirect/login checks passed.

## PWA Cache Can Serve Protected Content Across Entity And Session State

Status: resolved and released through work blocks 4A-4B and PR #86

Severity: high cross-entity financial-confidentiality risk

Captured: 2026-07-18

Where seen: `web/static/sw.js` and the repeated isolated Chromium offline probe

Revisit: Phase 4 Task 1 before relying on installed/offline operation; Phase 4 Task 2 for browser coverage

Summary:

The service worker precaches `/` and caches arbitrary successful dynamic GET responses by URL. Entity cookies and authenticated sessions are not part of cache identity. After caching a BFM transactions page, an offline request with the Personal cookie received the BFM page.

Impact:

An installed or previously used browser can show stale protected content from the wrong entity or authentication state while offline.

Acceptance checks:

- Protected and entity-specific HTML/API responses are not stored under shared URL-only cache keys.
- Entity and authentication transitions clear or isolate sensitive cache entries.
- Offline fallback never exposes another entity's or prior session's financial content.
- Browser tests reproduce Personal/BFM/LL and authenticated/unauthenticated transitions with synthetic markers.

Resolution:

Work block 4A moved to service-worker cache v4, removed protected root and all dynamic responses from caching, retained only static assets and the data-free offline page, and deleted older caches on activation. A browser probe proved old-cache deletion and offline entity isolation. Work block 4B released v4 through PR #86; Fly Deploy passed and production `/sw.js` matched the static/offline-only contract.

## Public Dashboard Exposes Detailed Personal And Luxe Legacy Financial Information

Status: open product-policy decision; confirmed in work block 3J

Severity: high public financial-data exposure risk

Captured: 2026-07-18

Where seen: `web/routes/kristine.py`, `web/templates/kristine.html`, and the repeated synthetic public-route probe

Revisit: Phase 3 Task 8 for the intended public-data contract before any Phase 4 repair

Summary:

The deliberately unauthenticated `/k/` route correctly includes Personal and Luxe Legacy while excluding BFM, but it renders transaction names, dates, amounts, categories, budget progress, and selected balances.

Impact:

Anyone who can reach the URL can view detailed financial information. The existing documentation identifies the route as public but does not establish whether this exact row-level exposure is an accepted product decision.

Acceptance checks:

- Ryan explicitly selects the intended public data contract.
- The route authenticates, minimizes to approved aggregates, or documents and enforces the accepted exposure.
- BFM remains excluded and tests prove the exact allowed fields for Personal and Luxe Legacy.

Why not changed now:

Public-route behavior changes and product-direction decisions were excluded from work block 3J.

## Client And Server Authentication Modes Can Drift

Status: resolved and released through work blocks 4A-4B and PR #86

Severity: medium authentication-availability and configuration risk

Captured: 2026-07-18

Where seen: `web/__init__.py`, `web/templates/base.html`, and configured/no-password local probes

Revisit: Phase 4 Task 1 with the main authentication repair

Summary:

The client gate uses a hard-coded digest independent of `APP_PASSWORD_HASH`. Changing the server hash can make the client and server disagree, and no-password server mode still renders a blocking password overlay.

Impact:

Credential rotation or demo/unconfigured operation can lock out the browser UI or create inconsistent client/server authentication state.

Acceptance checks:

- Client and server behavior derive from one runtime configuration contract.
- Configured, invalid, changed, and no-password/demo modes behave deterministically.
- The client never unlocks before the server confirms the session.

Resolution:

Work block 4A removed independent client auth state. Configured legacy and Werkzeug hashes, invalid passwords, safe redirect targets, and unset/no-password mode derive from the server configuration and passed tracked synthetic plus browser checks. Work block 4B released the repair through PR #86 and verified the production login contains no legacy client state.

## Mobile Sidebar Lacks Complete Keyboard Focus And Scroll Handling

Status: open; discovered in work block 3J

Severity: medium navigation-accessibility risk

Captured: 2026-07-18

Where seen: `web/templates/base.html`, `web/static/style.css`, and the repeated 390px isolated Chromium probe

Revisit: Phase 4 Task 1 if paired with security work, otherwise Phase 5 Task 2

Summary:

The phone sidebar opens, updates `aria-expanded`, shows its scrim, and closes from the scrim. It does not move focus into navigation, lock background scrolling, or close on Escape.

Impact:

Keyboard and assistive-technology users can lose navigation context, and touch users can scroll the obscured page behind the open drawer.

Acceptance checks:

- Opening moves focus into navigation and closing restores focus to the hamburger.
- Escape and the scrim close the drawer.
- Background scrolling is locked only while open.
- Keyboard, touch, ARIA state, and route-click behavior remain consistent.

Why not fixed now:

Product changes were excluded from work block 3J.

## Session Cookie And Browser Security Policy Need Explicit Hardening

Status: open; discovered in work block 3J

Severity: medium defense-in-depth risk

Captured: 2026-07-18

Where seen: `web/__init__.py` and the repeated synthetic HTTPS response probe

Revisit: Phase 4 Task 1 with the authentication repair; verify before release

Summary:

The session cookie was HttpOnly but did not include explicit Secure or SameSite attributes, and protected HTML did not emit Content-Security-Policy. Existing MIME, frame, referrer, XSS, and HTTPS HSTS headers passed.

Impact:

The application relies on browser defaults and transport behavior for controls that should be explicit around an authenticated financial application.

Acceptance checks:

- Production session cookies have explicit Secure, HttpOnly, and SameSite policy.
- Local/test behavior remains usable without weakening production configuration.
- A tested CSP permits required HTMX and local assets while blocking unintended script/content sources.

Why not fixed now:

Authentication, cookie, and security-header changes were excluded from work block 3J.

## PWA Public Auth And Responsive Boundaries Lack Tracked Regression Coverage

Status: partly addressed in work block 4A; browser/public/navigation coverage remains

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: `scripts/smoke_test.py` and the repeated 3J request/browser probes

Revisit: Phase 4 Task 2 alongside the selected authentication, cache, public-route, and navigation repairs

Summary:

Work block 4A added maintained configured/no-password authentication, CSRF, safe redirect, exempt/public route, no-store, and service-worker source-contract coverage. Disposable isolated-browser probes also verified installation, old-cache deletion, offline cross-entity isolation, and public entity scope, but those browser, manifest, and responsive-navigation checks are not yet tracked.

Impact:

The highest-risk 3J boundaries can regress without repeatable detection; the audit evidence is deterministic but ephemeral.

Acceptance checks:

- Request tests use fake secrets and temporary all-entity databases.
- Browser tests use disposable storage, representative viewports, and denied outbound networking.
- Tests cover protected/public/exempt request classes, entity cache isolation, offline fallback, and keyboard navigation.

Remaining work:

Add a maintained isolated-browser layer for service-worker installation/offline isolation, exact public `/k/` fields after Ryan decides its contract, manifest/icons, and responsive keyboard/navigation state. Do not treat the new request-level coverage as closing those browser and product-policy boundaries.

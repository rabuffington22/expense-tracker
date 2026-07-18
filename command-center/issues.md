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

## Short-Term Planning Legacy Plan Exceeds Current Verification Evidence

Status: parked for Phase 3 audit

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: retired `plan.md`, `scripts/smoke_test.py`, and `scripts/seed_demo_data.py`

Revisit: Phase 3 functional audit and prioritization

Summary:

The legacy Short-Term Planning plan proposed dedicated goal CRUD, snapshot, budget, payoff, entity-isolation, and cross-entity smoke cases plus seeded goals and snapshots. The current feature is substantially implemented, but the synthetic smoke suite contains no dedicated Short-Term Planning cases, and demo seeding covers budgets and action items rather than the planned goal and snapshot examples.

Impact:

The historical plan cannot be treated as acceptance proof. Current behavior may be correct, but regression confidence and demo coverage need a fresh evidence-based audit rather than an assumption based on an obsolete checklist.

Why not now:

Work block 2B is documentation governance only. Adding product tests or demo data would widen scope into Phase 3 or Phase 4 and requires its own bounded work block.

Promotion trigger:

Phase 3 decomposes the functional audit and decides whether the missing dedicated cases are defects, useful regression additions, or superseded requirements.

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

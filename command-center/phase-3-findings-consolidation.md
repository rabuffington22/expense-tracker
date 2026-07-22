# Phase 3 Findings Consolidation

Date: 2026-07-18

Status: work block 3K decision-ready catalog

## Purpose And Scope

This is the sanitized Task 7 catalog for the 55 Phase 3-derived entries recorded by work blocks 3A-3J and updated by the 4A-4B authentication repair and release. It assigns stable IDs, status, severity, confidence, affected boundaries, sanitized reproductions, observed-versus-expected behavior, impacts, evidence, and dependency tags without selecting the Task 8 repair order.

The full acceptance checks remain under the matching titled sections in `command-center/issues.md`. Each row below maps one-to-one to that ledger heading unless it explicitly says it cross-validates another ID. Work-block logs are the evidence source; this catalog does not replace them.

No real database, financial row, payroll row, statement, upload, credential, password, browser session, production page, Plaid call, Fly action, workflow action, downstream request, or product mutation was used for this consolidation.

## Decision Snapshot

| Classification | High | Medium | Low | Total |
| --- | ---: | ---: | ---: | ---: |
| Unresolved behavior or policy | 23 | 18 | 1 | 42 |
| Regression-coverage item | 0 | 10 | 0 | 10 |
| Resolved and released | 2 | 1 | 0 | 3 |
| Total | 25 | 29 | 1 | 55 |

One unresolved high item, `P3-3J-03`, is a Ryan product-policy decision rather than an implementation-ready defect. Nine medium coverage items remain parked and `P3-3J-C01` is partly addressed. The three resolved items are retained for traceability but must not return to the repair candidate pool without new contrary evidence.

## Stable ID To Issue Ledger Map

The text after each ID is the exact heading in `command-center/issues.md`; that section owns the full impact narrative and acceptance checks.

- `P3-3A-01` — Transaction Identity Can Collapse Distinct Transactions
- `P3-3A-C01` — Transaction Edit, Split, And Effective-Reporting Paths Lack Tracked Regression Coverage
- `P3-3B-01` — Vendor-Payment Matching References A Missing Transaction Column
- `P3-3B-02` — Vendor-Order Imports Discard Parsed Line Items
- `P3-3B-03` — Vendor Categorization Can Escape The Category Source Of Truth
- `P3-3B-04` — Upload Undo Label Does Not Explain Its Status-Only Effect
- `P3-3B-C01` — Task 2 Import And Categorization Paths Lack Tracked Regression Coverage
- `P3-3C-01` — Recurring Charges Report Executes An Uninterpolated SQL Helper
- `P3-3C-C01` — Task 3 Financial Read-Model Paths Lack Tracked Regression Coverage
- `P3-3D-01` — Locked Payoff Schedules Ignore Stored Account APRs
- `P3-3D-02` — Luxe Legacy Planning Denial Is Enforced Only On Page Entry
- `P3-3D-03` — Automatic Goal Snapshots Erase Same-Day Review Notes
- `P3-3D-04` — Negative Asset Appreciation Is Treated As Zero Growth
- `P3-3D-C01` — Planning Foundations Lack Tracked Regression And Demo Goal Evidence
- `P3-3E-01` — Weekly Historical Views Mix Selected And Current Dates
- `P3-3E-02` — Weekly Credit-Card Bills Use Full Balance Instead Of Scheduled Payment
- `P3-3E-03` — Waterfall Payoff Average Excludes Deficit Months
- `P3-3E-04` — Invalid Weekly Paydown Dates Persist And Break The Page
- `P3-3E-05` — Waterfall Can Report Zero Months While Debt Remains
- `P3-3E-06` — Waterfall Tax Fallback Can Disagree With Display And Crash On Non-Finite Input
- `P3-3E-C01` — Weekly And Waterfall Paths Lack Tracked Regression Coverage
- `P3-3F-01` — Non-BFM Entities Can Directly Access And Mutate Payroll
- `P3-3F-02` — Payroll Preview Duplicates An Exact Existing Employee
- `P3-3F-03` — Payroll Peer Averages Mix Hourly And Salary Units
- `P3-3F-04` — Payroll Employee Inputs Are Not Safely Normalized
- `P3-3F-05` — Canceling Payroll Preview Retains The Parsed Payload
- `P3-3F-06` — Malformed Payroll XLSX Raises Instead Of Returning An Import Error
- `P3-3F-C01` — Payroll Lifecycle Paths Lack Tracked Regression Coverage
- `P3-3G-01` — Plaid Persistence Errors Can Advance The Cursor Past Missing Data
- `P3-3G-02` — Plaid Balance Reconciliation Is Unsafe On Disabled Or Partially Failed Items
- `P3-3G-03` — Normal Cash Flow Refresh Skips Plaid Liabilities
- `P3-3G-04` — Linking A Plaid Institution Can Delete Unrelated Manual Accounts
- `P3-3G-05` — Plaid Balance Freshness Uses An Entity-Wide Maximum
- `P3-3G-06` — Missing Plaid Modified Rows Are Reported As Updated
- `P3-3G-07` — One Corrupt Plaid Token Aborts Valid Sibling Items
- `P3-3G-C01` — Primary Plaid Paths Lack Tracked Regression Coverage
- `P3-3H-01` — Scheduled Plaid Sync Can Report Partial Failure As Success
- `P3-3H-02` — Scheduled And Public Sync Paths Lack Shared Cross-Process Coordination
- `P3-3H-03` — Public Background Sync Advances Past Removed Plaid Events
- `P3-3H-04` — Public Background Sync Includes Vendor Plaid Items
- `P3-3H-05` — One Scheduled Entity Exception Aborts Healthy Later Entities
- `P3-3H-06` — Sync-All Runs Entity Setup Before Bearer Validation
- `P3-3H-07` — Failed Public Worker Launch Consumes Its Throttle Window
- `P3-3H-C01` — Background Sync Entry Points Lack Tracked Regression Coverage
- `P3-3I-01` — Luxe Legacy Owner Draw Is Mirrored Despite The Exclusion Intent
- `P3-3I-02` — Luxe Legacy Mirror Idempotency Contract Permits Duplicate Conflict Keys
- `P3-3I-03` — Luxe Legacy Mirror Accepts Empty Plaid Transaction IDs
- `P3-3I-C01` — Luxe Legacy Downstream Mirror Lacks Tracked Regression Coverage
- `P3-3J-01` — Main Authentication Boundary Returns Protected HTML And Accepts A Client-Exposed Digest
- `P3-3J-02` — PWA Cache Can Serve Protected Content Across Entity And Session State
- `P3-3J-03` — Public Dashboard Exposes Detailed Personal And Luxe Legacy Financial Information
- `P3-3J-04` — Client And Server Authentication Modes Can Drift
- `P3-3J-05` — Mobile Sidebar Lacks Complete Keyboard Focus And Scroll Handling
- `P3-3J-06` — Session Cookie And Browser Security Policy Need Explicit Hardening
- `P3-3J-C01` — PWA Public Auth And Responsive Boundaries Lack Tracked Regression Coverage

## Status And Confidence Contract

- `open`: reproduced behavior differs from the maintained contract or creates a documented integrity, availability, boundary, retention, or usability risk.
- `decision-needed`: observed behavior is intentional or policy-dependent and needs Ryan to choose the desired contract before implementation.
- `coverage`: current behavior was verified or a defect reproduced, but the evidence is not protected by maintained tests.
- `resolved`: repaired, released, and verified through 4A-4B.
- Confidence `high`: deterministic synthetic, mocked, source, browser, or production-safe evidence reproduced the conclusion.
- Confidence `medium`: the local contract is proven but an external system or product-policy conclusion remains unverified.

## 3A — Transaction Foundation

Evidence: `command-center/logs/2026-07-18-synthetic-transaction-foundation-audit-3a.md`; identity was cross-validated by 3G.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3A-01 | High | open | High | Personal, BFM, LL; import and Plaid identity | Insert two temporary rows with the same date, amount, and description but different accounts; one was silently skipped, while legitimate source-distinct rows must coexist and exact redelivery must deduplicate. | Ledger completeness and every downstream total can be wrong. | identity-contract-before-migration-and-import-sync-repair |
| P3-3A-C01 | Medium | coverage | High | Transaction edit, split, isolation, and effective reporting | Ephemeral all-entity edit, split-sign, rejected-replacement, cross-entity denial, and split-parent replacement checks passed; maintained tests should preserve those contracts. | A future regression could corrupt edits, splits, isolation, or reports without detection. | pair-with-P3-3A-01-and-shared-transaction-tests |

## 3B — Import, Vendor Matching, And Categorization

Evidence: `command-center/logs/2026-07-18-synthetic-import-categorization-audit-3b.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3B-01 | High | open | High | Personal, BFM, LL vendor-payment matching and schema | Run matching against fresh migration-built temporary databases; every entity raised on missing `transactions.matched_order_id`, while the canonical schema must support exact, review, and unmatched results. | The supported vendor-payment workflow cannot run reliably. | schema-before-vendor-matching-and-coverage |
| P3-3B-02 | High | open | High | Amazon and Henry Schein order persistence | Import generated vendor files; parent orders persisted but zero line items did, while parsed items must persist transactionally and reimport idempotently. | Advertised line-item detail and automatic split behavior are unavailable. | line-item-contract-after-schema-review |
| P3-3B-03 | High | open | High | All-entity category and subcategory domain | Generated inference and acceptance wrote undefined `Household` values and tie output changed across hash seeds; writes must be deterministic and constrained to `categories.md`. | Reports fragment and invalid classifications accumulate. | category-contract-before-remediation |
| P3-3B-04 | Low | open | High | Upload checklist operator language | Invoke `Undo` after a synthetic confirmed import; only checklist status reset while ledger rows remained, whereas the UI must state that status-only effect. | Operators can reasonably misunderstand whether transactions were removed. | independent-copy-fix |
| P3-3B-C01 | Medium | coverage | High | Parsers, preview/confirm, matching, aliases, cleanup, isolation | Sixty synthetic checks passed but maintained smoke covers only generic CSV and route availability; tracked tests must preserve the verified paths and each repaired defect. | Broad import regressions can escape the current suite. | pair-with-3B-repairs |

## 3C — Financial Read Model

Evidence: `command-center/logs/2026-07-18-synthetic-financial-read-model-audit-3c.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3C-01 | Medium | open | High | Personal, BFM, LL Recurring Charges report | Execute direct query, prepared report, and rendered route against temporary data; all nine paths failed on literal `{exclude_sql('category')}`, while the report must execute the interpolated exclusion contract. | The Recurring Charges report is unavailable in every canonical entity. | isolated-report-repair |
| P3-3C-C01 | Medium | coverage | High | Dashboard, reports/exports, subscriptions, cash flow | 297 synthetic assertions passed across the shared read model, but maintained coverage is shallow; tracked tests must preserve reconciled totals, exports, lifecycle, visibility, and isolation. | High-value reporting behavior can regress silently. | pair-with-P3-3C-01-and-read-model-tests |

## 3D — Planning Foundations

Evidence: `command-center/logs/2026-07-18-synthetic-planning-foundations-audit-3d.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3D-01 | High | open | High | Short-Term Planning locked payoff schedules | Lock a synthetic avalanche plan with 9.99% and 29.99% cards; extra payment went to the low-rate card because 20% was hard-coded, while stored APR must drive avalanche order. | Saved payment guidance and interest projections can be materially wrong. | planning-input-contract-before-schedule-tests |
| P3-3D-02 | High | open | High | LL planning denial and Personal singleton settings | Direct LL helper routes created hidden LL records, revealed Personal account names, and mutated Personal inflation; every supporting route must enforce the index denial and preserve all databases. | Entity isolation and hidden planning data are violated. | route-guard-before-planning-feature-repairs |
| P3-3D-03 | Medium | open | High | Short-Term Planning snapshot persistence | Save a same-day manual review note, then load the page; auto-snapshot replacement cleared the note, while balance refresh must preserve manual review context. | User-entered planning history disappears during normal use. | snapshot-upsert-before-coverage |
| P3-3D-04 | Medium | open | High | Long-Term Planning asset projections | Project a temporary asset at a negative growth rate; value stayed flat, while negative rates must compound as depreciation. | Future assets and net worth are overstated. | projection-math-before-demo-fidelity |
| P3-3D-C01 | Medium | coverage | High | Long/short-term planning and demo evidence | Fifty-eight temporary checks established current CRUD, budget, payoff, visibility, and projection contracts, while maintained tests and seeded goal/snapshot evidence remain absent. | Planning regressions and demo gaps remain hard to detect. | pair-with-3D-repairs; demo-choice-later |

## 3E — Weekly And Waterfall

Evidence: `command-center/logs/2026-07-18-synthetic-weekly-waterfall-audit-3e.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3E-01 | High | open | High | Weekly historical date context | Render a selected historical week; some pace, bill, and burn calculations still used the current date, while every derived value must share the selected anchor. | Historical decisions are based on mixed periods. | shared-date-context-before-weekly-fixes |
| P3-3E-02 | High | open | High | Weekly credit-card bill assembly | Seed balance and scheduled-payment values; the full balance became the upcoming bill, while scheduled payment or an explicit fallback must drive cash planning. | Near-term required cash is overstated. | bill-source-contract-before-weekly-coverage |
| P3-3E-03 | High | open | High | Waterfall payoff averaging | Seed surplus and deficit months; the average ignored deficits, while the full defined period must contribute to the payoff rate. | Debt-payoff guidance is systematically optimistic. | waterfall-period-contract-before-projection-fixes |
| P3-3E-04 | Medium | open | High | Weekly paydown input validation | Persist an invalid target date; the bad value remained and later broke the page, while invalid input must be rejected without corrupting state. | One bad input can make the workflow unavailable. | validation-before-derived-view-tests |
| P3-3E-05 | Medium | open | High | Waterfall payoff display | Use a positive sub-month estimate with remaining debt; the UI reported zero months, while nonzero debt needs a meaningful minimum or finer unit. | Users receive a contradictory payoff estimate. | display-rule-after-average-contract |
| P3-3E-06 | Medium | open | High | Waterfall tax normalization | Supply fallback and non-finite tax inputs; display and calculation diverged or failed, while one finite normalized value must drive both. | Scenario totals can disagree or crash. | normalization-before-waterfall-coverage |
| P3-3E-C01 | Medium | coverage | High | Weekly and Waterfall derived workflows | Corrected temporary probes verified 58 primary and ten focused checks, but maintained coverage is absent; tracked tests must anchor dates, bills, payoff, tax, sharing, denial, and empty states. | Complex derived behavior can regress without detection. | pair-with-3E-repairs |

## 3F — Payroll Lifecycle

Evidence: `command-center/logs/2026-07-18-synthetic-payroll-lifecycle-audit-3f.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3F-01 | High | open | High | Personal/LL direct payroll routes; BFM-only policy | Call payroll helpers directly with Personal or LL selected; reads and mutations succeeded, while every route must enforce BFM-only access. | Payroll/HR data can cross the maintained entity boundary. | route-guard-before-payroll-repairs |
| P3-3F-02 | High | open | High | Payroll preview employee matching | Preview an exact existing synthetic employee; the default created a duplicate candidate, while exact matches must attach to the existing employee. | Payroll history fragments across duplicate employees. | matching-contract-before-import-save |
| P3-3F-03 | High | open | High | Payroll peer compensation comparison | Mix hourly and salary employees; raw values were averaged together, while comparisons must normalize or separate compensation units. | Compensation guidance is mathematically misleading. | compensation-unit-product-rule-before-implementation |
| P3-3F-04 | Medium | open | High | Payroll employee input normalization | Submit weak or malformed direct employee values; unsafe values persisted or raised, while input must normalize and reject without partial mutation. | Bad input can corrupt roster state or break requests. | validation-before-roster-coverage |
| P3-3F-05 | Medium | open | High | Payroll temporary-payload retention | Cancel a generated payroll preview; parsed payload remained until age cleanup, while cancel should remove it immediately. | Sensitive payroll intermediates live longer than necessary. | retention-cleanup-independent |
| P3-3F-06 | Medium | open | High | Phoenix/CyberPayroll XLSX error handling | Parse a malformed generated workbook; an exception escaped, while the import flow must return a controlled user-facing error and clean up. | A bad file makes the import path unavailable. | parser-error-before-import-coverage |
| P3-3F-C01 | Medium | coverage | High | Payroll parser, roster, import, history, isolation | Forty-seven temporary assertions established current behavior and defects, but dedicated maintained payroll coverage is absent. | Payroll regressions and boundary failures can escape detection. | pair-with-3F-repairs |

## 3G — Primary Plaid Boundary

Evidence: `command-center/logs/2026-07-18-mocked-primary-plaid-boundary-audit-3g.md`; `P3-3A-01` is the shared identity finding cross-validated here.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3G-01 | High | open | High | Plaid transaction persistence and cursor commit | Mock a persistence failure during incremental sync; the cursor advanced past missing data, while cursor commit must follow durable application of the page. | Transactions can be permanently omitted. | transaction-identity-and-atomicity-before-entry-points |
| P3-3G-02 | High | open | High | Plaid account/balance reconciliation | Mock disabled or partially failed items; cached rows were deleted too broadly, while reconciliation must preserve unrelated/manual and failed-item state. | Valid account state can disappear during refresh. | reconciliation-contract-before-cash-flow-tests |
| P3-3G-03 | High | open | High | Cash-flow Plaid liability refresh | Run the normal mocked refresh; liability details were skipped, while card liability fields must update with balances. | Cash-flow and payment guidance can be inaccurate. | liability-refresh-with-reconciliation |
| P3-3G-04 | High | open | High | Plaid link exchange and manual accounts | Link a mocked institution beside manual accounts; unrelated manual rows were deleted, while link reconciliation must affect only the target Plaid item. | User-maintained account state can be destructively lost. | link-reconciliation-before-live-use |
| P3-3G-05 | Medium | open | High | Plaid balance freshness | Seed one fresh and one stale account; entity-wide max freshness suppressed the stale refresh, while freshness must be evaluated per account/item. | Stale balances can appear current. | freshness-model-with-reconciliation |
| P3-3G-06 | Medium | open | High | Plaid modified-event observability | Send a modified event for a missing stored ID; the result reported an update, while counts must reflect affected rows. | Monitoring and operators receive false success. | observability-after-persistence-contract |
| P3-3G-07 | Medium | open | High | Plaid item failure isolation | Include one corrupt fake encrypted token and one healthy sibling; decryption aborted both, while item failures must be isolated. | One bad connection blocks valid sibling synchronization. | item-isolation-before-all-entity-entry-point |
| P3-3G-C01 | Medium | coverage | High | Link, account, balance, liability, sync, cursor, failure paths | Repeated mocked probes reproduced the same results with outbound sockets blocked, but maintained Plaid coverage is shallow. | High-risk integration regressions can escape the suite. | pair-with-3A-01-and-3G-repairs |

## 3H — Scheduled And Public Sync Entry Points

Evidence: `command-center/logs/2026-07-18-mocked-sync-entry-point-audit-3h.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3H-01 | High | open | High | Scheduled sync HTTP/workflow result | Return an entity result containing errors; route still returned 200 and `ok: true`, while partial failure must produce a machine-detectable unsuccessful result. | GitHub can stay green while financial sync is incomplete. | result-contract-before-workflow-coverage |
| P3-3H-02 | High | open | High | Scheduled/public concurrency under two Gunicorn workers | Exercise both mocked entry points; distinct process-local locks and throttle provided no shared coordination, while one cross-process contract must protect cursors and work. | Concurrent syncs can race and corrupt consistency. | coordination-after-3G-atomicity-before-live-concurrency |
| P3-3H-03 | High | open | High | Public background removed events and cursor | Feed a removed event; stored transaction remained while cursor advanced, whereas removal and cursor commit must be atomic. | Deleted upstream transactions remain while sync claims completion. | depends-on-P3-3G-01 |
| P3-3H-04 | High | open | High | Public background vendor-item scope | Seed a vendor Plaid item; public worker consumed it through the spending path, while vendor items must follow their explicit boundary. | The wrong workflow can mutate vendor-linked state. | item-scope-before-public-worker-coverage |
| P3-3H-05 | Medium | open | High | Scheduled all-entity failure isolation | Raise in BFM; later LL work was skipped and response lacked structured partial state, while healthy entities must continue or report explicit disposition. | One entity blocks healthy later synchronization. | depends-on-P3-3G-07-and-result-contract |
| P3-3H-06 | Medium | open | High | Sync bearer authorization side effects | Call without bearer; entity setup/category sync ran before rejection, while authorization must precede normal mutable setup. | Unauthorized traffic can trigger avoidable state work. | auth-order-independent |
| P3-3H-07 | Medium | open | High | Public worker launch and throttle | Mock thread-start failure; timestamp still consumed the throttle interval, while failed launch must remain immediately retryable. | A transient launch error suppresses recovery. | launch-state-before-public-worker-tests |
| P3-3H-C01 | Medium | coverage | High | Scheduled/public method, auth, coordination, result, cursor, scope | Repeated mocked probes produced identical findings with sockets denied, but maintained entry-point coverage is absent. | Operational regressions can remain invisible. | pair-with-3H-repairs |

## 3I — Luxe Legacy Downstream Mirror

Evidence: `command-center/logs/2026-07-18-mocked-luxe-legacy-downstream-mirror-audit-3i.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3I-01 | High | open | High | LL category exclusion and downstream selection | Seed maintained LL `Owner Draw`; it entered the mocked payload because code excludes nonexistent `Owner Contribution`, while the intended maintained category must be excluded. | Personal draw activity can cross the downstream business boundary. | category-contract-before-mirror-coverage |
| P3-3I-02 | High | open | Medium | Local/remote mirror idempotency | Seed duplicate Plaid IDs; local schema admitted both and one request carried both while conflict target stayed implicit, whereas local uniqueness and remote conflict behavior must be explicit. | A batch may duplicate, reject, or ambiguously merge downstream. | remote-contract-decision-before-implementation |
| P3-3I-03 | Medium | open | High | LL mirror identifier validation | Seed an empty Plaid ID; `IS NOT NULL` admitted it, while only non-empty stable IDs may qualify. | Invalid idempotency keys can reach the downstream request. | validation-with-P3-3I-02 |
| P3-3I-C01 | Medium | coverage | High | LL-only invocation, selection, request, failure, isolation | Forty-four mocked checks passed and findings reproduced with sockets denied, but maintained bridge coverage is absent. | Mirror regressions can escape without making real downstream calls. | pair-with-3I-repairs |

## 3J — PWA, Public, Authentication, And Responsive Boundaries

Evidence: `command-center/logs/2026-07-18-local-pwa-navigation-public-auth-audit-3j.md`, `command-center/logs/2026-07-18-server-auth-protected-cache-repair-4a.md`, and `command-center/logs/2026-07-18-auth-repair-release-4b.md`.

| ID | Severity | Status | Confidence | Affected boundary | Sanitized reproduction and observed versus expected | Impact | Dependency tag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P3-3J-01 | High | resolved | High | Main authentication and protected HTML | 3J returned full protected HTML and a reusable digest before auth; 4A moved verification server-side and 4B proved production redirects before rendering. | The confidentiality exposure is closed and retained only for regression traceability. | resolved-do-not-prioritize-without-new-evidence |
| P3-3J-02 | High | resolved | High | Service worker, entity/session cache | 3J replayed cached BFM HTML to offline Personal; 4A made dynamic requests network-only and 4B proved production cache v4 static/offline-only. | The cross-entity offline exposure is closed. | resolved-do-not-prioritize-without-new-evidence |
| P3-3J-03 | High | decision-needed | High | Public `/k/` Personal/LL financial-data contract | Repeated isolated requests rendered names, dates, amounts, categories, budgets, and selected balances without auth while excluding BFM; expected behavior depends on Ryan choosing authentication, minimization, or explicit acceptance. | Detailed Personal and LL financial information is intentionally public. | Ryan-policy-before-any-code |
| P3-3J-04 | Medium | resolved | High | Configured/unconfigured authentication modes | 3J showed independent client/server state and blocked no-password mode; 4A unified runtime behavior and 4B verified production login without a client digest. | Authentication availability/configuration drift is closed. | resolved-do-not-prioritize-without-new-evidence |
| P3-3J-05 | Medium | resolved-locally | High | Mobile sidebar accessibility | 4AD synchronizes drawer semantics, excludes closed navigation from keyboard and assistive use, places and contains focus, restores it on non-navigation close, handles Escape and scrim, locks scroll only while open, preserves navigation actions, and cleans breakpoint state. | The mobile navigation-accessibility defect is closed locally with maintained isolated-browser coverage; publication remains separate. | publish-only-if-separately-authorized |
| P3-3J-06 | Medium | partly-addressed | High | Session cookie and browser security policy | 4AC makes the session cookie explicit, 4AE freezes a strict core/narrow Plaid CSP contract, 4AF completes the shared execution foundation, 4AG-R makes dashboard/report fragments durable, and 4AH-R makes transaction/modal fragments durable and deployed; protected HTML still lacks CSP. | Cookie policy, planning, shared execution, and all directly returned fragment migrations are durable through 4AH-R; final HTMX disablement, page/style/header work, and final production proof remain separate. | confirm-final-htmx-disablement-after-4ah-r |
| P3-3J-C01 | Medium | partly-addressed | High | Auth, CSRF, redirect, cache, public fields, manifest, browser, responsive behavior | 4A added maintained request/cache contracts and 4AD adds maintained isolated-browser responsive-navigation coverage at phone, exact-mobile-breakpoint, and desktop-transition widths; manifest/icon, service-worker installation/offline isolation, and remaining configured-auth/exact-`/k/` browser slices remain. | Responsive navigation is now guarded locally, while broader installed-PWA and browser boundaries remain Task 1P.6. | pair-remaining-browser-coverage-with-1P6 |

## Dependency Clusters For Task 8

These are technical sequencing relationships, not a repair ranking.

1. Transaction identity and atomicity: `P3-3A-01` defines the source-identity contract used by import and Plaid; `P3-3G-01` then governs durable cursor application; `P3-3H-03` and `P3-3H-02` depend on those contracts for entry-point correctness.
2. Vendor data path: `P3-3B-01` establishes schema compatibility, `P3-3B-02` establishes line-item persistence, and `P3-3B-03` establishes category-domain enforcement before comprehensive `P3-3B-C01` coverage.
3. Planning and derived calculations: route denial and input contracts (`P3-3D-02`, `P3-3D-01`) should remain distinct from projection/snapshot fixes; Weekly/Waterfall items share date, bill, period, and normalization contracts and should gain `P3-3E-C01` coverage with their repairs.
4. Payroll boundary first: `P3-3F-01` is the access boundary for the remaining payroll integrity, validation, retention, and parser work; compensation-unit behavior in `P3-3F-03` may require Ryan to confirm the comparison contract.
5. Plaid core before entry points: reconciliation, liability, manual-account preservation, item isolation, and cursor correctness in 3G are prerequisites for trusting 3H scheduling/concurrency and 3I downstream behavior.
6. Public and browser policy: `P3-3J-03` requires Ryan's policy decision before code. Cookie/CSP work needs an explicit compatibility policy. Mobile accessibility is independent. Remaining browser coverage should accompany the selected repairs rather than become a detached broad test project.
7. Coverage items: the ten coverage entries are evidence requirements to pair with the related repair families; they are not ten standalone product priorities.

## Evidence Limits

- Actual production occurrence of most findings is unknown because real financial, payroll, upload, database, and authenticated production data remained closed.
- `P3-3I-02` proves the local duplicate-key and implicit-conflict contract but not the downstream service's actual uniqueness or merge behavior.
- `P3-3J-03` proves the public data contract but cannot decide whether that intentional contract is acceptable.
- Severity expresses potential impact under the demonstrated contract; it is not proof that a defect has already affected real rows.

## Task 8 Decision Gate

Task 7 is ready to close when this catalog reconciles one-to-one with the 55 Phase 3 issue entries and the command center passes verification. Task 8 remains Ryan-owned and must decide:

1. The intended public `/k/` contract.
2. Which dependency cluster should become the first broader Phase 4 repair block.
3. Whether the selected block includes its paired regression-coverage item.
4. Whether any medium product-contract question, especially payroll compensation units or cookie/CSP policy, needs a narrower decision before implementation.

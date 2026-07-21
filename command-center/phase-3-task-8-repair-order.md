# Phase 3 Task 8 — Provisional Repair Order

Date: 2026-07-18

Status: done; Ryan confirmed all four post-review decisions on 2026-07-19, Phase 3 Task 8 is complete, and this remains planning evidence rather than implementation authorization

## Purpose

Turn the verified 55-entry Phase 3 findings catalog into an evidence-backed repair sequence, explicit policy gates, and one bounded first Phase 4 proposal. This artifact deliberately does not change product behavior, infer production occurrence, or authorize migration, tests, live access, release, or GitHub durability.

## Second-Opinion Intake And Final 3L Recommendation

The full reviewer response is saved at `command-center/logs/second-opinion/2026-07-18-phase-3-task-8-fable-5-max.md`. Fable 5 returned high confidence, endorsed `P3-3A-01` plus `P3-3A-C01` as the first repair, and proposed changes to the middle of the sequence and the 4C acceptance contract.

This section supersedes conflicting ordering details in the original provisional sections below while preserving them as review traceability.

### Accepted Recommendations

1. Keep 4C Transaction Identity Foundation first.
2. Add a written per-source identity specification, populated pre-change synthetic upgrade coverage, empty/absent external-ID semantics, same-source duplicate semantics, and an explicit identity-only call-site boundary to 4C.
3. Pin 4C tracked coverage to `scripts/smoke_test.py` rather than leaving the test surface open-ended.
4. Move the small dependency-free boundary and truthfulness findings immediately after 4C: `P3-3D-02`, `P3-3F-01`, `P3-3I-01`, `P3-3H-01`, and `P3-3C-01`.
5. Treat that early tranche as several separately scoped work blocks unless later source inspection proves a shared implementation and verification seam; do not combine unrelated subsystems merely because each fix is small.
6. Pre-split the primary Plaid family into atomicity; reconciliation/preservation/liability/freshness; and isolation/observability blocks.
7. Decide `/k/` before the remaining scheduled/public sync-entry family.
8. Split `P3-3J-06`: schedule Secure/SameSite cookie policy as a narrow earlier browser-security block, and keep CSP behind compatibility design after the `/k/` decision.
9. Ship `P3-3C-01` with focused recurring-report coverage; do not pretend that this satisfies broad `P3-3C-C01`. Pull reconciled-total coverage forward where it protects transaction-identity and Plaid repairs, then park the remaining broad read-model coverage with its own explicit scope.
10. Correct the vendor-family rationale: its relationship to 4C is migration sequencing on the `transactions` table, not semantic dependence on the identity contract.

### Accepted With A Boundary Correction

The reviewer suggested pulling the core empty-ID behavior adjacent to `P3-3I-03` into 4C. The identity specification will define that an empty external ID is never a shared identity key, but 4C will not implement Luxe Legacy mirror filtering or broaden into Plaid cursor/persistence behavior. Those changes remain in their own findings and stop gates.

### Source-Level Missing Evidence Resolved

Current source inspection established:

- `core/imports.py` computes a 24-character SHA-256 key from only date, amount, and normalized description.
- Deduplication is a query-side comparison against existing `transaction_id` primary keys plus a same-dataframe duplicate drop; there is no separate unique index on the natural key.
- `transactions.transaction_id` is the primary key and is referenced by splits and order-matching behavior, so upgrade-path preservation is a real 4C constraint.
- Plaid transaction IDs are already carried by `core/plaid_client.py` and stored in `transactions.plaid_transaction_id`, but the Plaid insert path still uses the natural-key hash as the row primary key. The Plaid ID has a non-unique index, not a uniqueness constraint.
- Two identical rows within one imported dataframe currently share the same computed ID and the later occurrence is dropped.

These facts strengthen the recommendation to settle a written source-aware identity contract before changing call sites or migration behavior. They do not require protected or production data.

### Revised Repair Sequence

1. 4C Transaction Identity Foundation — `P3-3A-01`, `P3-3A-C01`.
2. Early boundary and truthfulness tranche, as separate blocks — `P3-3D-02`, `P3-3F-01`, `P3-3I-01`, `P3-3H-01`, `P3-3C-01` plus focused coverage.
3. Primary Plaid core, pre-split into three blocks — `P3-3G-01` through `P3-3G-07` with `P3-3G-C01` and the relevant early reconciled-total subset of `P3-3C-C01`.
4. Remaining scheduled/public sync entry points — `P3-3H-02` through `P3-3H-07` with `P3-3H-C01`; the `/k/` decision must be made before this family is planned.
5. Vendor import-to-categorization — `P3-3B-01` through `P3-3B-03` with `P3-3B-C01`.
6. Payroll integrity and retention — `P3-3F-02` through `P3-3F-06` with `P3-3F-C01`, after the BFM-only guard and compensation-unit decision.
7. Planning, Weekly, and Waterfall correctness — remaining `P3-3D` and `P3-3E` findings with paired coverage.
8. Luxe Legacy downstream mirror — `P3-3I-02`, `P3-3I-03`, and focused `P3-3I-C01` coverage are ready for a separately confirmed local block after 4Z verified the tracked downstream contract.
9. Public/browser security and UX — authenticated or minimized `/k/` contract, cookie flags, later CSP compatibility, mobile navigation, and paired `P3-3J-C01` coverage.
10. Remaining isolated availability, operator copy, and broad read-model coverage — `P3-3B-04` plus the unconsumed portion of `P3-3C-C01`.

All 55 catalog IDs remain accounted for, the three resolved findings remain outside the repair pool, and no critique recommendation authorizes implementation.

### Confirmed Task 8 Decisions

Ryan confirmed all four post-review recommendations on 2026-07-19:

1. 4C Transaction Identity Foundation is first, using the recommended source-aware duplicate and upgrade-preservation contract.
2. The revised sequence is accepted: separate early boundary/truthfulness blocks after 4C, then three pre-split primary Plaid blocks, then remaining sync-entry work.
3. The intended `/k/` contract is authenticated through the existing server-side gate; detailed-public behavior is not accepted as the future contract.
4. Regression coverage stays paired with each repair family; payroll comparisons default to separated hourly and salary cohorts; cookie flags are separated from later CSP compatibility work; and downstream idempotency stays parked pending an explicitly authorized read-only remote-contract check.

These decisions close Phase 3 Task 8 and work block 3L. They authorize the repair order and the creation of a separately confirmable 4C proposal, not implementation, GitHub durability, deployment, protected-data access, or live action.

### Revised 4C Identity Contract Default

Recommended Ryan default:

- A non-empty authoritative external transaction ID, such as a Plaid transaction ID, is the source identity and must not be replaced by the current natural-key hash.
- File imports use a documented stable source/batch fingerprint plus an occurrence ordinal among otherwise identical normalized rows, so legitimate duplicates within one payload coexist while exact re-import of that payload remains idempotent.
- Empty external IDs are never treated as shared identifiers. If safe handling would require Plaid persistence or cursor changes, 4C stops and leaves that behavior to the later Plaid atomicity block.
- Existing transaction primary keys and their split/order references must survive the populated synthetic upgrade path; no destructive regeneration is allowed.
- At import and Plaid call sites, only identity computation is in scope. Persistence ordering, cursor commits, reconciliation, and concurrency remain excluded.

Ryan must confirm or revise this source contract before 4C implementation can start.

## Evidence Base And Limits

- Source catalog: `command-center/phase-3-findings-consolidation.md`.
- Classification: 42 unresolved behavior or policy findings, ten coverage items, and three resolved findings.
- Severity: 25 high, 29 medium, and one low across the full catalog.
- Most findings were reproduced only with synthetic databases, generated files, mocked integrations, or isolated browsers. Their possible impact is proven; actual production occurrence is not.
- Work block 4Z later verified the tracked downstream uniqueness contract and explicit conflict target as `plaid_transaction_id`; deployed-schema and live merge behavior remain intentionally unverified.
- `P3-3J-03` proves the current detailed-public `/k/` behavior but cannot decide whether Ryan intends to retain it.

## Prioritization Rules

The provisional order uses five factors:

1. Prevent silent omission, destructive loss, or cross-entity exposure before improving derived views.
2. Repair prerequisite contracts before their dependents.
3. Prefer a narrow first block whose migration and verification risks can be isolated.
4. Pair maintained regression coverage with each repair family rather than creating a detached coverage project.
5. Stop at product-policy and remote-contract gates instead of silently choosing them in code.

## Provisional Ordered Families

### Order 1 — Transaction Identity Foundation

IDs: `P3-3A-01`, paired with `P3-3A-C01`.

Why first: the current identity contract can silently collapse legitimate source-distinct transactions and is shared by import and Plaid ingestion. It affects ledger completeness and every downstream total, while the first implementation can remain narrow enough to validate with temporary all-entity databases before touching cursor or concurrency behavior.

Boundary: do not include Plaid cursor atomicity, entry-point concurrency, real-data migration, production inspection, or release in the first block.

### Order 2 — Primary Plaid Preservation And Atomicity

IDs: `P3-3G-01`, `P3-3G-02`, `P3-3G-04`, `P3-3G-03`, `P3-3G-05`, `P3-3G-07`, `P3-3G-06`, paired with `P3-3G-C01`.

Internal dependency: durable page application and cursor commit first; reconciliation and manual-account preservation next; liability and freshness behavior after the reconciliation contract; item isolation before all-entity entry-point recovery; observability after persistence behavior is truthful.

Why second: this family contains the largest concentration of silent omission or destructive-state risks, but it depends on the transaction identity contract and has a broader mocked-integration verification path than the proposed first block.

### Order 3 — Scheduled And Public Sync Truthfulness

IDs: `P3-3H-03`, `P3-3H-02`, `P3-3H-01`, `P3-3H-05`, `P3-3H-04`, `P3-3H-06`, `P3-3H-07`, paired with `P3-3H-C01`.

Internal dependency: removed-event atomicity depends on Plaid cursor correctness; cross-process coordination follows the atomicity contract; result truthfulness and entity failure disposition follow the core sync result model. Vendor scope, bearer-before-setup, and failed-launch retry are narrower repairs but should ship with entry-point coverage.

Why third: entry-point fixes cannot make a fundamentally unsafe persistence core trustworthy. They become high leverage once Orders 1-2 establish source identity, durable cursor application, and item isolation.

### Order 4 — Entity And Sensitive-Workflow Boundaries

IDs: `P3-3D-02`, `P3-3F-01`, and `P3-3I-01`.

Disposition: implement as separate small blocks or as one shared route-guard pattern only if source inspection proves the same enforcement seam and verification path. Pair `P3-3D-C01`, `P3-3F-C01`, and `P3-3I-C01` only with their respective subsystem blocks, not with a generic boundary-only test project.

Why fourth: these are high-confidence isolation or sensitive-selection defects and should precede feature-level repairs. They do not share enough implementation surface to be assumed to form one block.

### Order 5 — Vendor Import-To-Categorization Integrity

IDs: `P3-3B-01`, `P3-3B-02`, `P3-3B-03`, paired with `P3-3B-C01`.

Internal dependency: canonical schema compatibility before line-item persistence; category-domain enforcement before remediation or broad import coverage.

Why fifth: all three are high-confidence correctness failures in an advertised workflow, but they are downstream of the foundational transaction identity contract and use a separate generated-file verification path.

### Order 6 — Payroll Integrity And Retention

IDs: `P3-3F-02`, `P3-3F-04`, `P3-3F-05`, `P3-3F-06`, paired with `P3-3F-C01`. `P3-3F-03` is included only after its compensation-unit policy gate is resolved.

Internal dependency: the BFM-only guard in Order 4 precedes these repairs. Exact employee matching precedes import-save coverage. Direct input validation, cancel cleanup, and malformed-workbook handling are independently testable.

Why sixth: the workflow handles sensitive payroll intermediates and contains high-impact integrity defects, but one high finding needs a Ryan product rule and the family is separate from ledger ingestion.

### Order 7 — Planning, Weekly, And Waterfall Correctness

Planning IDs: `P3-3D-01`, `P3-3D-03`, `P3-3D-04`, paired with `P3-3D-C01` after the `P3-3D-02` route guard.

Weekly/Waterfall IDs: `P3-3E-01`, `P3-3E-02`, `P3-3E-03`, `P3-3E-04`, `P3-3E-05`, `P3-3E-06`, paired with `P3-3E-C01`.

Internal dependency: selected-date, bill-source, full-period averaging, validation, and normalization contracts should precede display-only refinements. Planning APR order and snapshot persistence remain distinct from weekly/waterfall calculations even when both use planning data.

Why seventh: these findings can materially distort guidance, but they are derived-workflow defects rather than foundational ingestion, destructive-state, or sensitive-boundary failures.

### Order 8 — Luxe Legacy Downstream Mirror

IDs: `P3-3I-02`, `P3-3I-03`, and the relevant portion of `P3-3I-C01`. Work block 4Z satisfied the tracked-contract gate; `P3-3I-01` was handled earlier as a sensitive-selection boundary.

Why eighth: empty identifier validation and deterministic duplicate handling are locally provable, and 4Z established `plaid_transaction_id` as the tracked downstream primary key and explicit conflict target. Live schema inspection and downstream writes remain separately gated and unnecessary for the local repair block.

### Order 9 — Isolated Availability, UX, And Operator Clarity

IDs: `P3-3C-01` with `P3-3C-C01`; `P3-3J-05` with the relevant portion of `P3-3J-C01`; and `P3-3B-04` as an independent copy clarification.

Why ninth: the Recurring Charges report is unavailable, mobile navigation accessibility is incomplete, and `Undo` language is ambiguous, but these do not outrank silent omission, destructive reconciliation, isolation, or materially wrong financial guidance.

## Explicit Decision Gates

### Public `/k/` — `P3-3J-03`

Recommended default: do not accept the current detailed-public behavior unchanged. Prefer authentication using the existing server-side gate. If frictionless public access is a real product requirement, define a minimized data contract that excludes names, transaction detail, exact amounts, balances, and other sensitive fields before implementation.

Ryan choices: authenticate; minimize to a new explicitly public contract; or explicitly accept the current detailed-public contract.

### Payroll Compensation Units — `P3-3F-03`

Recommended default: compare like with like by separating hourly and salary cohorts. Do not invent an annualization rule until the available payroll fields and product intent support one.

### Cookie And CSP Policy — `P3-3J-06`

Recommended default: handle this in a dedicated browser-security block after documenting HTMX, inline script/style, asset, and local-development compatibility. Do not mix it into the first data-integrity repair.

### Downstream Idempotency — `P3-3I-02`

Recommended default: gate satisfied by 4Z. Plan one local-only block for deterministic malformed/duplicate key handling, explicit `plaid_transaction_id` request semantics, and the remaining maintained mirror coverage; keep live schema inspection and downstream writes separate.

## Coverage Disposition

All ten coverage entries are accounted for and remain paired with their repair family:

- `P3-3A-C01` — transaction identity block.
- `P3-3B-C01` — vendor import/categorization block.
- `P3-3C-C01` — recurring report and read-model block.
- `P3-3D-C01` — planning guard and calculation blocks.
- `P3-3E-C01` — weekly/waterfall block.
- `P3-3F-C01` — payroll boundary and integrity blocks.
- `P3-3G-C01` — primary Plaid blocks.
- `P3-3H-C01` — sync entry-point blocks.
- `P3-3I-C01` — downstream mirror blocks.
- `P3-3J-C01` — public/browser decision and mobile-accessibility blocks.

## Resolved Findings Outside The Repair Pool

`P3-3J-01`, `P3-3J-02`, and `P3-3J-04` remain resolved through work blocks 4A-4B and PR #86. They stay only as regression traceability unless new contrary evidence appears.

## Proposed First Phase 4 Block

Name: 4C — Transaction Identity Foundation

Parent phase and tasks: Phase 4 Tasks 1B and 2.

Included findings: `P3-3A-01` and `P3-3A-C01`.

Proposed outcome: define and implement a source-aware deterministic transaction identity contract that allows legitimate same-date, same-amount, same-description transactions from distinct accounts or sources to coexist while exact redelivery remains idempotent; preserve entity isolation, negative-debit semantics, split relationships, imports, and reporting behavior; add focused synthetic regression coverage.

Expected implementation surfaces: transaction identity helpers, additive migration logic in `core/db.py` if required, import and Plaid call sites that use the identity helper, and focused synthetic checks in `scripts/smoke_test.py` or the established tracked test surface.

Excluded from 4C: `P3-3G-01` and all other Plaid behavior; entry-point concurrency; vendor schema and line-item repairs; real databases or production collision inspection; destructive or irreversible ID rewrites; live Plaid, workflows, Fly, downstream actions; `/k/`; credentials; release; and GitHub durability.

Required stop conditions:

- The safe identity contract requires inspecting real transaction rows or credentials.
- An additive migration cannot preserve existing transaction references, splits, order matches, aliases, and exact-redelivery behavior in synthetic tests.
- The repair requires rewriting an applied migration or destructively regenerating existing IDs.
- Import and Plaid sources need incompatible identity semantics that cannot be resolved without a Ryan product/data decision.
- Verification expands into cursor atomicity, live sync, deployment, or another excluded subsystem.

Acceptance checks:

- Two synthetic transactions with identical date, amount, and description but different accounts or sources coexist in each entity.
- Exact redelivery from the same source still deduplicates deterministically.
- CSV/PDF and mocked Plaid paths use the explicit source-aware contract.
- Existing synthetic edit, split, isolation, negative-debit, effective-reporting, and import-deduplication behavior remains passing.
- Any schema change is additive and ordered; no applied migration is rewritten.
- Maintained synthetic suite, focused identity checks, dashboard refresh, health check, whitespace check, and disposable cleanup pass.

Durability: local-only implementation proposal. A later work-block confirmation would authorize code changes; release and GitHub durability would remain separate.

## Questions For Independent Review

1. Is transaction identity the correct first repair, or should payroll/planning route isolation, Plaid reconciliation, or vendor schema failure precede it?
2. Is proposed 4C narrow enough to finish safely while still proving the identity contract end to end?
3. Which dependency or risk relationships in Orders 1-9 are wrong, missing, or over-weighted?
4. Are the four decision-gate defaults defensible, and which need different Ryan choices before implementation planning?
5. What evidence, if any, is missing badly enough that 3L should stop rather than recommend a first block?

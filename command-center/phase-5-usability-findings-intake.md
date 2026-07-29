# Phase 5 Independent Usability Findings Intake

Date: 2026-07-26\
Work block: 5B Independent Usability Critique And Findings Intake\
Tasks: 1.3 (`P5-T13`) and 1.4 (`P5-T14`)\
Status: complete locally; critique preserved as opinion evidence

## Outcome

The independent critique agrees that The Ledger needs targeted polish rather than a broad redesign. It identifies one larger product-surface question—the purpose and structure of the recurring-charge page—and one common theme across the remaining findings: the interface often reports a state without explaining what it means or placing the next action beside it.

Codex adopts the low-risk demo-fidelity diagnosis and the general “explain and enable” principle. Product-direction, data-handling, broader information-architecture, and new detection-logic choices remain separately gated. No reviewer recommendation is treated as implementation authorization.

## Classification Rules

- `adopt`: retain as accepted direction for a separately confirmed Task 2 block.
- `ignore`: do not pursue because it is a weaker mitigation, conflicts with the maintained product contract, or is superseded by a stronger direction.
- `park`: potentially useful, but lower priority, broader than polish, dependent on earlier evidence, or unsupported by the current implementation.
- `Ryan-decision`: a material product, data-handling, or information-architecture choice that Codex will not make implicitly.

## Seven 5A Findings

| Finding | Reviewer position | Intake classification | Durable direction |
|---|---|---|---|
| F5A-01 demo category drift | Partly agree; P1 seed, P3 banner | `adopt` seed repair; `park` banner redesign | Align the synthetic Personal and BFM seed with the current `categories.md` domain before judging the banner. Preserve truthful production drift reporting. Reassess banner placement, consequence copy, action, and dismissal only after clean demo evidence exists. |
| F5A-02 absent demo goals | Agree; P1 | `adopt` two representative demo goals and colocated empty-state action; `ignore` repositioning the page away from goals | Make one synthetic Personal debt-payoff goal and one synthetic Personal savings goal part of the durable demo contract. Keep any empty-state CTA change in a later product block. |
| F5A-03 phone transaction overflow | Partly agree; P2 | `adopt` mobile-first rows; `ignore` scroll-cue-only closure | Below the tablet breakpoint, preserve all five current fields in a compact two-line row and preserve the current click-to-edit affordance. Keep the existing table at tablet/desktop widths and leave the already-good mobile filters unchanged. |
| F5A-04 LL empty and denied states | Agree and raise; P2 | `adopt` explanatory first-use and denied states; `Ryan-decision` exact first-run primary action | Reuse the Payroll empty-state pattern, preserve fail-closed routing, and show a plain-language notice that does not reveal another entity's capabilities. Decide whether “Connect a Bank” or “Import” is the primary LL action before implementation. |
| F5A-05 subscriptions versus recurring charges | Agree and raise; P1 product question | `Ryan-decision` page purpose; `adopt` tracked-first order, queue count, visible labels, and inline undo after that decision; `park` type grouping | The current detector recognizes cadence and amount regularity only and does not classify subscriptions, bills, payroll, rent, or other kinds. Do not add grouping or detection semantics inside a polish block. Decide whether this is a cancellation watchlist, a complete recurring-spend register, or both before revising the page as a unit. |
| F5A-06 Data Sources discoverability | Partly agree; P4 | `park` | Do not add another sidebar item now. Revisit Data Sources, Connected Accounts, To Do, and broader capability discovery as one information-architecture problem after higher-impact polish. |
| F5A-07 Ask Opus affordance | Agree and raise; P2 trust issue | `adopt` a visible purpose label in principle; `Ryan-decision` data-scope and retention contract; no implementation yet | The current route sends detailed entity/page financial context to OpenRouter and stores up to 40 clean user/assistant messages in temporary per-entity/page JSON files. Truthful privacy copy requires an explicit data-handling decision and verification of the intended production contract first. |

## Reviewer Findings Not Explicitly Named In 5A

| Finding | Classification | Durable direction |
|---|---|---|
| M-01 mobile entity context disappears | `adopt` | Add a read-only current-entity marker to the mobile header or page title area. Keep entity switching inside the drawer and preserve its semantics. |
| M-02 dashboard columns use different invisible inclusion rules | `park` | Reassess after the demo category repair. If zero-activity categories still dominate, collapse them by default while retaining a discoverable way to show them. |
| M-03 color conveys meaning without a legend or non-color redundancy | `park` | Audit the affected charts and repeated color semantics in a later focused accessibility block; do not widen the first polish slice. |
| M-04 no capability index or search | `park` | Treat as a broader information-architecture question, not a local polish fix. |
| M-05 offline screen lacks a data-safety statement and visible retry feedback | `resolved through 5P-R` | The separately confirmed recovery accepts the unchanged green 5P evidence while preserving 5P's historical stop. The exact controller is cached, Retry feedback is truthful and accessible, and the narrow generic-screen statement is supported. Do not extend it into a blanket device, storage, synchronization, encryption, retention, production-runtime, or application-wide privacy assurance. |

## Reviewer Priorities And Design Principles

The recommended priority order is accepted with one gate:

1. Repair demo category and goal fidelity first.
2. Resolve the recurring-charge product purpose before revising that surface.
3. Improve Luxe Legacy first-use and denied-state explanation.
4. Replace phone transaction overflow with mobile rows and restore visible entity context.
5. Clarify Ask Opus only after its data-scope and retention contract is explicitly decided.

The reviewer’s three design principles are adopted as Phase 5 evaluation heuristics:

1. Scope should be visible in the page title.
2. An absence or denial should explain itself, with the next action colocated.
3. Dense information must justify its cost; mobile views must always answer whose money is shown.

## Strengths To Preserve

Every later polish block must preserve:

- fail-closed entity boundaries and the narrower Luxe Legacy capability set;
- persistent desktop entity tabs and drawer-only mobile entity switching;
- mobile drawer focus placement, containment, Escape/scrim closure, scroll lock, and accessible control names;
- clean stacked mobile filters;
- tablet/desktop transaction scanning unless a later block explicitly changes it;
- Weekly Check-In's summary-to-detail hierarchy;
- Payroll's clear empty-state/import pattern;
- Data Sources' reached-state separation of vendor orders and payment-account matching;
- the restrained, data-free offline fallback;
- strict entity isolation and existing CSRF, authentication, PWA, and service-worker contracts;
- zero reviewed-page console warnings or errors.

## Open Questions Resolved By Source Inspection

| Reviewer question | Source-backed intake |
|---|---|
| Can recurring candidates be grouped by kind? | No current kind model exists. `_detect_subscriptions()` groups by merchant and checks cadence, amount regularity, recency, watchlist, dismissal, and exclusions. Grouping is parked unless a later confirmed block authorizes new product/detection logic. |
| Is category drift intentional? | The demo seed hard-codes a large legacy Personal/BFM category and budget vocabulary that diverges materially from `categories.md`. Treat it as accumulated seed drift, not an intentional teaching state. |
| Should demo goals be permanent? | Recommended yes: one Personal debt-payoff goal and one Personal savings goal, using existing synthetic accounts and no production effect. Confirmation of 5C accepts this exact default. |
| Are mobile transaction categories editable? | Yes. Each result row opens the existing transaction edit modal. A mobile-row implementation must preserve that route and affordance. |
| What does Ask Opus send and retain? | Page-specific context can include category, merchant, transaction, balance, planning, goal, budget, recurring-charge, and cross-entity Personal/BFM summary data. It is sent to OpenRouter using Claude Opus. Clean chat messages are retained in temporary per-entity/page JSON files, capped at 40 messages, until cleared or the temporary storage is removed. |

## Questions Reserved For Ryan

1. Should the recurring surface be a cancellation watchlist, a complete recurring-spend register, or a combined review-and-track workflow?
2. For Luxe Legacy first use, should “Connect a Bank” or “Import” be the primary action?
3. What production data-scope, cross-entity scope, retention, and user disclosure contract should govern Ask Opus?

The remaining reviewer questions are either answered above or parked with the broader information-architecture work.

## Task 2 Decomposition

- **Task 2.1 (`P5-T21`): Repair synthetic demo fidelity.** Align seeded Personal/BFM categories and budgets with `categories.md`; add one synthetic Personal debt-payoff goal and one savings goal; add focused all-temporary verification. Recommended first.
- **Task 2.2 (`P5-T22`): Improve first-use and denied-state explanation.** Colocate the Short-Term Planning empty-state action and improve Luxe Legacy empty/denied guidance after Ryan selects the LL primary action.
- **Task 2.3 (`P5-T23`): Repair phone transaction density and entity context.** Render compact phone rows that preserve the current fields and edit path; add a read-only entity marker; preserve filters, tablet/desktop table behavior, and drawer semantics.
- **Task 2.4 (`P5-T24`): Revise the recurring-charge surface.** After Ryan decides its purpose, revise naming, tracked/review order, queue progress, action labels, and undo without silently adding a new kind-classification model.
- **Task 2.5 (`P5-T25`): Clarify Ask Opus purpose and privacy.** First freeze and verify its data-scope/retention contract, then make the purpose and truthful boundary visible.
- **Task 2.6 (`P5-T26`): Reassess dashboard explanation and density.** After Task 2.1, reevaluate category-drift messaging, zero-activity category treatment, and non-color redundancy from fresh synthetic evidence.
- **Task 2.7 (`P5-T27`): Resolve connections and capability discovery.** Revisit Data Sources, Connected Accounts, To Do entry points, and capability discovery as one later information-architecture slice.
- **Task 2.8 (`P5-T28`): Verify and improve offline recovery feedback.** Done locally through 5P-R and feature-branch/draft-PR durable with candidate hosted verification through 5Q-R. The corrected exact non-token-boundary scan returned clean no-match once; candidate `3edccc0d4b097dfdbeccf2c7cc6837c0c2319684` is on open draft PR #92; automatic candidate Synthetic CI passed core before browser with zero annotations and zero deployment. Work block 5Q remains historically stopped before branch creation. The immutable 5Q-R closeout is valid only after its exact automatic final-head gate passes; production release remains a separate 5R decision. The recovery continues to accept the unchanged green smoke, installed-Chrome, direct-render, and cleanup evidence without rewriting either historical stop or making broader privacy claims.

## Recommended First Block

Work block 5C should include Task 2.1 only. The demo seed currently distorts every visual review and leaves the primary Short-Term Planning goal experience unreviewable. Repairing it is local, synthetic, independently verifiable, and does not require any unresolved product, privacy, live-data, or information-architecture decision.

## Preserved Boundaries

No application, test, dependency, authentication, financial, database, category-domain, workflow, runtime, or configuration source changed during 5B. No real financial data, credential, retained upload, database, production/demo/Plaid/Fly/downstream access, staging, commit, push, PR, merge, workflow action, deployment, or preserved untracked-file mutation occurred.

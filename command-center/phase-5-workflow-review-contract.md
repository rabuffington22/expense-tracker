# Phase 5 Workflow Review Contract

Date: 2026-07-26\
Work block: 5A Cross-Surface Usability Baseline\
Tasks: 1.1 (`P5-T11`) and 1.2 (`P5-T12`)\
Status: active, local-only

## Objective

Create a bounded, privacy-safe usability and qualitative accessibility baseline for representative desktop, mobile, exact-tablet, and installed-PWA workflows. The result is an evidence packet for later independent critique and Task 2 prioritization, not a product change or accessibility certification.

## Review Boundary

- Use only disposable synthetic data under a temporary `DATA_DIR`.
- Keep non-localhost browser traffic denied.
- Retain only screenshots and observations that contain synthetic demonstration content.
- Treat the current tracked application, README, categories, route/entity rules, smoke suite, and maintained isolated-browser suite as the comparison contract.
- Use maintained tests as technical guardrails. Do not reopen Phase 4 correctness findings without new contrary evidence.
- Do not change application, test, dependency, authentication, financial, database, category, workflow, runtime, or configuration sources.
- Do not use real financial rows, existing local databases, retained uploads, credentials, Plaid, Fly, production, demo hosting, downstream systems, GitHub actions, or publication.

## Representative Journey Matrix

| ID | Journey | Entity | Desktop 1200px | Phone 390px | Tablet 768px | Primary review questions |
|---|---|---|---|---|---|---|
| J1 | Daily orientation: Dashboard, To Do, Transactions, Reports | Personal | All four surfaces | Dashboard, drawer, To Do, Transactions | Transactions and Reports | Can a user understand current state, find work, filter/drill into rows, and recover from dense content? |
| J2 | Planning and reporting: Cash Flow, Short-Term Planning, Long-Term Planning, Weekly, Waterfall | Personal and BFM | All supported surfaces | Short-Term Planning, Weekly, Waterfall | Cash Flow and Long-Term Planning | Are planning concepts, goals, assumptions, chart/table controls, and cross-entity context understandable? Does demo data make the goal workflow credible? |
| J3 | Business operations: Dashboard, Transactions, Subscriptions, Payroll, Data Sources, Connected Accounts | BFM | All supported surfaces | Dashboard, drawer, Transactions, Subscriptions | Payroll and Data Sources | Are business-only capabilities discoverable, clearly labeled, and separated from Personal behavior without overwhelming the shell? |
| J4 | Supported and unsupported entity boundaries | Luxe Legacy | Dashboard, Transactions, Reports, Data Sources, supported empty states, and denied planning/payroll routes | Dashboard, drawer, Transactions | Reports and a denied route | Does the UI explain what is available, absent, empty, or denied without suggesting cross-entity access? |
| J5 | Installed-PWA continuity and recovery | Personal, BFM, Luxe Legacy | Standalone shell and entity continuity | Launch, drawer, entity switch, offline/error recovery | Breakpoint transition and standalone navigation | Does the app feel continuous and understandable when installed, offline, recovering, or changing entity/viewport? |

Desktop provides broad top-level coverage. Phone and exact-tablet checks focus on the highest-value navigation, interaction, dense-content, modal, table, error/recovery, and standalone paths rather than multiplying every route across every width.

## Heuristics

1. Orientation and information hierarchy.
2. Navigation clarity and current-location feedback.
3. Label, instruction, and financial-concept comprehensibility.
4. Entity identity and isolation cues.
5. Keyboard focus visibility, order, containment, Escape behavior, and landmark clarity.
6. Touch-target practicality and mobile drawer behavior.
7. Responsive overflow, wrapping, density, and control reachability.
8. Empty, loading, denied, offline, error, and recovery states.
9. Interaction feedback for filters, dialogs, drilldowns, and state changes.
10. Installed-PWA continuity across launch, entity switch, offline use, and breakpoint changes.
11. Demo-goal fidelity: whether synthetic demo content makes Short-Term Planning goals and their intended value understandable.

## Evidence Contract

Each retained screenshot must record journey ID, entity, route, viewport, state, and observation. Findings use sanitized identifiers and one of these evidence labels:

- `observed-friction`: a user-facing clarity, navigation, interaction, accessibility, or responsive concern.
- `observed-strength`: a behavior worth preserving during later polish.
- `technical-guardrail`: maintained automated proof, not a subjective usability conclusion.
- `unverified`: a matrix cell that could not be assessed safely.

5A records findings without accepting design direction or implementing a repair. Severity and Task 2 ordering remain provisional until the separately gated independent critique and Codex intake in Tasks 1.3-1.4.

## Stop Conditions

Stop and report rather than expand if protected or real data appears; credentials, external access, or a live action becomes necessary; evidence cannot be sanitized; a product, financial, security, or design decision is required; a product or maintained-test edit appears necessary; the representative matrix is insufficient; temporary cleanup cannot be proven; verification changes the plan; dashboard health fails; or a preserved untracked file would be touched.

## Completion Checks

- Full synthetic smoke passes.
- The maintained configured-auth/no-password installed-Chrome suite passes with denied non-localhost traffic and exact temporary cleanup.
- Every matrix row has retained sanitized evidence or an explicit `unverified` disposition.
- Every retained artifact is visually inspected.
- JSON, dashboard refresh/currentness/health, rendered closeout state, whitespace, exact changed paths, zero staging, and preserved-file hashes pass.

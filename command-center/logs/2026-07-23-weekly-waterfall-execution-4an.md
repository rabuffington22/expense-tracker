# Work Block 4AN: Weekly And Waterfall Execution

Date: 2026-07-23

Status: complete and locally verified on `codex/csp-weekly-waterfall`

## Scope

Included Task 1P.4.2c.4 plus only its focused Task 2 regression slice. Weekly AI entry moved to the maintained app-shell action. Waterfall's one executable inline script and the remaining native handlers moved into one template-free page-owned controller. The block preserved actual/target switching, nested breakdowns, revenue/take-home mode, target and tax Enter handling, tooltip toggling and outside-click closure, bar animations, URL semantics, AI entry, and Personal/BFM versus Luxe Legacy boundaries.

Excluded throughout: Tasks 1P.4.2c.5-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route calculations; financial logic; database queries; style migration; CSP headers, nonces, or enforcement; authentication; CSRF; Plaid; dependencies; credentials; protected data; real databases; retained uploads; external or live access; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

## Result

- `weekly.html` uses the existing app-shell AI action and contains zero executable inline scripts, native inline handlers, or `hx-on` attributes.
- `waterfall.html` loads page-owned `waterfall.js`, carries target mode through inert controller data, and contains zero executable inline scripts, native inline handlers, or `hx-on` attributes.
- `waterfall.js` uses delegated controls and remains free of server templating.
- The aggregate tracked-template inventory is 23 script elements: ten executable inline scripts, twelve external executable scripts, and one inert JSON carrier; native handlers are thirty-one and `hx-on` remains zero.
- No route, financial, database-query, style-policy, CSP-enforcement, authentication, Plaid, dependency, protected-data, credential, real-database, retained-upload, external/live, publication, deployment, or preserved-file mutation occurred.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed; maintained section 11i proves source and rendered zero-execution behavior, local assets, AI seams, and the exact residual inventory.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes with temporary synthetic Personal, BFM, and Luxe Legacy databases, denied non-localhost requests, zero unexpected console or page errors, and exact temporary cleanup.
- The browser matrix covered Weekly and Waterfall AI entry, initial and switched views, nested breakdowns, revenue/take-home mode, target and tax Enter navigation, tooltip toggle and outside-click closure, bar animation, Personal/BFM availability, and Luxe Legacy denial.
- Python compilation, JavaScript syntax, JSON validation, `git diff --check`, command-center refresh and health, generated-dashboard state, exact scope, and preserved-file checks passed.

## Durability

Local-only. No commit, push, PR, merge, publication, deployment, production inspection, protected access, credential use, real database, or live action occurred. Exact-scope 4AN-R durability/release and Task 1P.4.2c.5 remain separate Ryan gates.

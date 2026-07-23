# Work Block 4AM Evidence — Short-Term Planning Execution

Date: 2026-07-23

Status: complete and verified locally on `codex/csp-short-term-planning`

## Confirmed Scope

- Task 1P.4.2c.3c plus only its focused Task 2 regression slice.
- Migrate the Short-Term Planning executable inline script, template handlers, inert goal-data carrier, and same-route Python-rendered handlers into maintained local behavior.
- Preserve goal, plan, monthly-review, action-item, budget, subcategory, transaction-edit, fetch, AI, modal, keyboard, and Personal/BFM versus Luxe Legacy behavior.
- Keep publication, deployment, live access, protected data, financial logic, database queries, styles, CSP enforcement, dependencies, later route clusters, `scripts/sync_prod_to_local.sh`, and `command-center/now 2.md` outside scope.

## Corrected Source Inventory

- `short_term_planning.html` contained one executable inline script, twenty-two template-source native-handler occurrences, and one inert JSON script carrier.
- The Short-Term Planning budget transaction and subcategory response builders added two Python-rendered native handlers inside the same route family.
- The correction did not change the task, product behavior, risk class, or verification path.

## Result

- `short_term_planning.html` now loads one page-owned `short-term-planning.js`, carries goal data in a non-script inert template, and contains zero executable inline scripts, native inline handlers, or `hx-on` attributes.
- The page-owned controller uses delegated data actions and preserves goal popup/edit/plan/review behavior, goal-type switching, budget month navigation, subcategory expansion, transaction drill-down/edit/save/cancel, AI entry, money normalization, dialog closure, keyboard behavior, and idempotent initialization.
- Both Python response builders now emit handler-free declarative controls without changing their queries, calculations, mutation rules, or response boundary.
- The maintained aggregate template inventory is twenty-three script elements: eleven executable inline scripts, eleven external executable scripts, one inert JSON carrier, forty-four native handlers, and zero `hx-on` attributes. Both HTMX execution switches remain false.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: pass, including new section 11h source, rendered-page, rendered-response, inert-data, cleanup, and aggregate-inventory proof.
- Baseline and final `.venv/bin/python scripts/mobile_drawer_browser_test.py`: pass in configured-auth and no-password modes.
- The isolated browser proves goal popup/edit/plan/review, goal-type switching, fetched subcategory controls, handler-free transaction response markup, transaction save/cancel, AI entry, Personal/BFM isolation, Luxe Legacy denial, disabled HTMX switches, denied non-localhost requests, zero unexpected console/page errors, and exact temporary-data cleanup.
- Python and JavaScript syntax, command-center JSON, whitespace, dashboard refresh, command-center health, generated-state inspection, exact scope, and preserved-file checks: pass.

## Durability And Boundaries

- Local-only on `codex/csp-short-term-planning`.
- No commit, push, PR, merge, publication, deployment, workflow action, production/demo inspection, protected data, credential, real database, retained upload, downstream access/write, or live action occurred.
- `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` remain untouched and untracked.
- Exact-scope 4AM-R durability/release and Task 1P.4.2c.4 remain separate Ryan gates.

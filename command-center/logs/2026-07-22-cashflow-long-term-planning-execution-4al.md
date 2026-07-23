# Work Block 4AL Evidence — Cash Flow And Long-Term Planning Execution

Date: 2026-07-22

Status: complete and locally verified; not committed or published

## Confirmed Scope

- Completed Tasks 1P.4.2c.3a-1P.4.2c.3b plus only their focused Task 2 regression slices.
- Moved two executable inline scripts and twenty-five native handlers from `cashflow.html` and `planning.html` into separate page-owned maintained local controllers.
- Preserved the included Cash Flow and Long-Term Planning behavior and entity boundaries.
- Kept Short-Term Planning, route and financial logic, style/CSP enforcement, authentication, Plaid, dependencies, protected/live access, publication, deployment, downstream operations, and the two unrelated untracked files outside scope.

## Result

- `web/static/cashflow.js` owns delegated Cash Flow account/card opening, modal population, balance/limit/APR/payment sizing, due-day parsing, recurring-entry setup, scrim/Escape closure, and page AI entry.
- `web/static/planning.js` owns delegated Long-Term Planning item opening, add/edit/delete flows, source switching, birthday save, projection display, scrim/Escape closure, and page AI entry.
- Both included templates now contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes.
- The aggregate residual tracked-template inventory is twelve executable inline scripts, ten external executable assets, two inert JSON carriers, sixty-six native handlers, and zero `hx-on`; HTMX `allowEval` and `allowScriptTags` remain false.

## Verification

- `.venv/bin/python scripts/smoke_test.py` — pass, including focused source/rendered-response contracts and the exact residual inventory.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` — pass in configured-auth and no-password modes with temporary synthetic Personal/BFM/Luxe Legacy data, denied external requests, zero unexpected console/page errors, and exact cleanup.
- `.venv/bin/python -m py_compile scripts/smoke_test.py scripts/mobile_drawer_browser_test.py` — pass.
- `node --check web/static/cashflow.js` and `node --check web/static/planning.js` — pass.
- `jq empty command-center/state.json` and `git diff --check` — pass.
- Cash Flow, Long-Term Planning, and the generated command-center dashboard were rendered and visually inspected from synthetic/local-only state.
- Dashboard refresh and command-center health check — pass after closeout reconciliation.

## Boundaries And Durability

- No credential, protected data, real database, retained upload, external request, or live-system action was used.
- No route, financial-business-logic, Short-Term Planning, style, CSP-header/enforcement, Plaid, authentication, dependency, workflow, downstream, or deployment change occurred.
- `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` remain unmodified and untracked.
- The result remains local-only on `codex/csp-cashflow-long-term-planning`; no commit, push, PR, merge, publication, or deployment occurred.
- Exact-scope 4AL-R durability/release and Task 1P.4.2c.3c are separate Ryan gates.

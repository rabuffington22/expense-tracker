# Work Block 4AG — Dashboard And Report Fragment Execution

Date: 2026-07-22

Status: complete and verified locally

## Scope

Work block 4AG completed Task 1P.4.2b.1 only. It migrated the included dashboard, analysis, category-comparison, KPI, insight, and report fragment execution to maintained local JavaScript and inert declarative data. Transaction/editor/supporting-modal fragments, global HTMX execution switches, remaining pages, styles, CSP headers, Plaid, authentication, protected data, live systems, publication, and deployment remained outside scope.

## Result

- `web/static/dashboard-fragments.js` now owns delegated category, subcategory-popup, insight-modal, insight-dismissal, AI-detail, and report-expansion actions.
- The same asset builds the income/expense SVG chart from inert JSON and initializes KPI-dependent category, insight, compare, upcoming, and income-analysis requests through idempotent `htmx:load` handling.
- `web/templates/base.html` loads the maintained asset. The nine included fragment templates now contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes.
- The Python-rendered insight-detail response now uses the delegated dismissal contract instead of an inline handler.
- `allowEval=true` and `allowScriptTags=true` remain explicit. Deferred Task 1P.4.2b.2 retains one executable script, twenty-eight native handlers, and two `hx-on` attributes; final disablement remains Task 1P.4.2b.3.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed. The final suite includes focused migrated-source, static-controller, rendered-asset, Python-response, corrected residual-inventory, and deferred-HTMX-setting assertions.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes against temporary synthetic Personal, BFM, and Luxe Legacy databases.
- The browser matrix covered two repeated dashboard-body swaps in each auth mode; KPI-dependent detail/compare loads; category detail/compare expansion; insight request/modal behavior; AI-analysis response and delegated row toggles; chart recreation; merchant and tax-report swaps and expansion; denied non-localhost requests; zero console/page errors; and exact cleanup.
- Python compilation, JavaScript syntax, JSON validation, `git diff --check`, dashboard refresh, command-center health, and rendered-dashboard inspection passed.

## Inventory Correction

Focused proof distinguished executable code from inert JSON and corrected `txn_split_editor.html` from three executable scripts to one executable script plus two inert JSON blocks. Exact route-response enumeration also corrected the dashboard/report slice from fourteen to twelve template-native handlers: two sidebar handlers belong to a full-page include, not a directly returned fragment. The verified pre-4AG Task 1P.4.2b inventory was ten executable scripts, forty template handlers, one Python-rendered handler, and two `hx-on` attributes. Neither correction changed 4AG's confirmed path or behavior scope.

## Boundaries And Durability

All browser and application data was synthetic and temporary, non-localhost requests were denied, and cleanup passed. No credential, protected data, real database, retained upload, external request, production/demo inspection, GitHub mutation, deployment, or live action occurred. The result remains local-only on `codex/csp-dashboard-report-fragments`. The unrelated untracked `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` files were preserved.

## Next Gate

Proposed work block 4AH would cover Task 1P.4.2b.2 only: the remaining transaction/editor/supporting-modal fragment execution. It requires separate Ryan confirmation. Task 1P.4.2b.3 remains a separate final global HTMX disablement and cross-route proof gate.

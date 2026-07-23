# Work Block 4AP — Payroll Page Execution

Date: 2026-07-23

Status: complete and locally verified

## Scope

Task 1P.4.2c.6 plus only its focused Task 2 regression slice: migrate one executable inline script and nine native handlers from `payroll.html` into maintained page-owned behavior while preserving the BFM-only payroll boundary and the confirmed interaction matrix.

Tasks 1P.4.2c.7-1P.4.4, Tasks 1P.6-1P.7, the remainder of Task 2, Tasks 3-4, route/import/database-query/financial/product/style/CSP-enforcement/authentication/CSRF/Plaid/dependency/service-worker changes, credentials, protected data, real databases, retained uploads, external/live access, GitHub durability, publication, deployment, workflows, downstream access/writes, `scripts/sync_prod_to_local.sh`, and `command-center/now 2.md` remained excluded.

## Result

- `payroll.html` now loads page-owned template-free `payroll.js`, uses delegated `data-payroll-action` controls, and carries role-color data in a non-script inert template.
- The included page contains zero executable inline scripts, native handlers, or `hx-on` attributes.
- Add/show/cancel, mouse/Enter/Space employee detail, pay history and paycheck rendering, edit/delete form targets, deletion confirmation, close button, scrim, Escape, spending-period refresh, and import new-role switching remain available.
- The invalid nested edit/delete form structure was corrected into valid sibling forms with the Save button explicitly associated to the edit form. No route or product-policy change was required.
- Fetched employee names, notes, history, and paycheck values are rendered with DOM text nodes rather than concatenated detail HTML.
- The residual tracked-template inventory is eight executable inline scripts, fourteen external executable assets, zero inert JSON script carriers, seven native handlers, and zero `hx-on`; both HTMX execution switches remain false.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed. Section 11k proves the source template, rendered BFM route, page controller, inert data, valid form contract, and exact residual inventory.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes using temporary synthetic Personal, BFM, and Luxe Legacy databases, mocked payroll parsing, localhost-only traffic, zero unexpected console/page errors, and exact temporary database, upload-payload, and browser cleanup.
- The browser matrix covers BFM controller loading, add form focus, row mouse/Enter/Space detail, pay history/paychecks, edit/delete targets, dismissed confirmation, button/scrim/Escape closure, spending refresh, import new-role switching, exact preview cancellation cleanup, and Personal/LL denial before payroll execution.
- Python compilation, JavaScript syntax, JSON validation, whitespace, dashboard refresh/health, exact scope, and preserved-file checks pass.

## Verification Learning

The first final smoke run failed because the earlier peer-comparison regression expected controller code to remain inline in rendered HTML. The maintained assertion now checks the page-owned controller while retaining the rendered label check. The browser pass also confirmed that separating the previously nested delete form was necessary to make the intended edit and deletion targets valid and independently testable.

## Boundary

No commit, push, PR, merge, publication, deployment, production/demo inspection, credential, protected data, real database, retained upload, external request, live action, route/import/query/financial/product/style/CSP-enforcement/authentication/Plaid/dependency/downstream mutation, or preserved-file overlap occurred. Exact-scope 4AP-R durability and Task 1P.4.2c.7 remain separate Ryan gates.

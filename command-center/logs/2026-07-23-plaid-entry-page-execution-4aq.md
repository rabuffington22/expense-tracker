# Work Block 4AQ Evidence — Plaid Entry-Page Execution

Date: 2026-07-23

Status: complete and verified locally; publication remains separately gated.

## Result

- `data_sources.html` now loads page-owned, template-free `data-sources.js`; delegated controls preserve vendor selection, order-preview date counting, disconnect confirmation, Plaid Link launch, exit/error reset behavior, and form-encoded public-token exchange.
- `plaid.html` now loads page-owned, template-free `plaid.js`; delegated controls preserve both connect buttons, disconnect confirmation, Plaid Link launch, exit/error reset behavior, and JSON public-token exchange.
- Both exact `https://cdn.plaid.com/link/v2/stable/link-initialize.js` tags remain unchanged. No live Plaid or other external service was contacted.
- Order dates moved from executable inline JavaScript into a non-script inert template. Endpoint values are carried by declarative page-root attributes.
- The two pages now contain zero executable inline application scripts, zero native handlers, and zero `hx-on`. Aggregate tracked inventory is five executable inline scripts, sixteen external executable scripts, zero inert script carriers, one native handler, and zero `hx-on`.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed, including the focused two-page source/rendered, request, exchange-format, CSRF, entity-isolation, cleanup, initializer, and residual-inventory contract.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes with fake Plaid configuration, monkeypatched Plaid and crypto functions, exact initializer interception, denied non-localhost traffic, temporary synthetic Personal/BFM/Luxe Legacy data, and exact cleanup.
- Browser coverage exercised vendor-label switching, uploaded synthetic Amazon preview dates and count, both disconnect confirmations, Link open/success/exit/error states, form and JSON token exchanges, reloads, entity isolation, zero unexpected console/page errors, and removal of temporary browser, payload, and database state.
- Python compilation, JavaScript syntax, JSON parsing, whitespace, dashboard refresh, dashboard health, generated-state inspection, exact scope, protected-boundary review, and preserved-file checks passed.

## Boundary

No route, API, database-query, schema, financial, product, authentication, CSRF, dependency, service-worker, style, CSP header, nonce, exception-policy, enforcement, credential, protected-data, real-database, retained-upload, live-Plaid, external, GitHub, publication, deployment, workflow, downstream, or preserved-untracked-file mutation occurred.

## Learning

The isolated success path exposed a pre-existing vendor-account aggregation edge: a newly connected vendor item with no imported transactions can produce a `None` matched-total and make the existing account-list helper fall back to an empty list. The 4AQ proof uses a synthetic transaction fixture so it can test the migrated browser behavior without changing excluded route/query logic. Any repair belongs in a separately confirmed route-level block. The browser test also selects the exact seeded disconnect row because a successful mocked connection legitimately changes list ordering.

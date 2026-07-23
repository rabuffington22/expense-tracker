# Content Security Policy Compatibility Contract

Status: Task 1P.4.1, Task 1P.4.2a, both Task 1P.4.2b migration slices, final HTMX disablement, and all eight full-page execution clusters are durable, automatically deployed, and credential-free health verified through work block 4AR-R; style, header-enforcement, and final proof slices remain separately gated.

Parent: Phase 4 Task 1P.4 / finding `P3-3J-06`.

## Purpose And Boundary

This contract defines the target browser policy, the application surfaces that must be migrated before enforcement, and the maintained proof required to close the CSP half of `P3-3J-06`. Work block 4AE created the contract without product mutation. Work blocks 4AF-4AI migrated shared and swapped-fragment execution and disabled HTMX eval and swapped-script processing. Work blocks 4AJ-4AP migrated the first six full-page clusters. Work block 4AQ migrated Data Sources and Connected Accounts application execution into two page-owned controllers and non-script inert data while retaining both exact Plaid Link initializer tags. None added a CSP header, changed authentication, route or Plaid business behavior, or touched any live system.

Protected data, credentials, real databases, live Plaid Link, production/demo inspection, publication, deployment, and both preserved untracked files remain outside this planning artifact.

## Source-Grounded Constraints

- [HTMX security guidance](https://htmx.org/docs/#security) documents that `allowScriptTags=false` stops processing scripts in swapped content and `allowEval=false` disables event filters, `hx-on`, and `js:` forms of `hx-vals` and `hx-headers`. The same guidance recommends replacing those features through custom JavaScript and HTMX events.
- [HTMX configuration guidance](https://htmx.org/docs/#config) shows that `allowEval`, `allowScriptTags`, and `includeIndicatorStyles` default to `true`. The tracked local HTMX asset is version 2.0.4 and retains those defaults.
- [Plaid Link Web guidance](https://plaid.com/docs/link/web/#csp-directives) requires the Link initializer to load directly from its exact CDN URL and identifies Plaid frame and environment-specific connect origins. Plaid's nonce example still calls for `style-src-attr 'unsafe-inline'` on a Link document.
- [MDN CSP guidance](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) distinguishes nonces from source allowlists and recommends a restrictive default with explicit resource directives. [MDN `style-src-attr`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src-attr) confirms that this directive governs element `style` attributes independently of stylesheet and `<style>` sources.

## Inventory Summary

The tracked surface contains 46 HTML templates and seven standalone document roots: the shared `base.html` shell, login, three error documents, offline, and standalone `/k/`. After local work block 4AQ, the source inventory contains:

| Surface | Count | Contract consequence |
| --- | ---: | --- |
| All `<script>` elements | 21 | Separate the five remaining standalone-document inline scripts from sixteen external executable assets. |
| Executable inline scripts | 5 | Move to maintained local static JavaScript; a nonce is not a migration substitute. All authenticated application-page behavior now uses local assets. |
| External executable scripts | 16 | Local theme, HTMX, app-shell, page and fragment controllers, including `data-sources.js` and `plaid.js`, plus two exact Plaid Link initializer tags. |
| Inert `application/json` scripts | 0 | Swapped carriers, Short-Term Planning goals, and subscription suggestions now use non-script `<template>` data. |
| Native inline event-handler attributes | 1 | Replace the remaining offline retry handler before `script-src-attr 'none'`; all authenticated application-page handlers are removed. |
| `hx-on` attributes | 0 | All dependencies remain removed and 4AI proves the configured-auth/no-password cross-route matrix with HTMX eval and swapped-script processing disabled. |
| Inline `<style>` blocks | 7 | Move to local CSS before strict `style-src-elem`. |
| Element `style` attributes | 221 | Replace with classes, data-driven classes, custom-property classes, or stylesheet-backed state before strict application policy. |
| Runtime JavaScript style mutations | At least 33 call sites | Replace `element.style`, `cssText`, or equivalent attribute writes on strict application documents. |
| External browser runtime | Plaid Link only | Restrict to the exact documented initializer, CDN frame, and selected Plaid API environment. |

All application `fetch`, HTMX, XHR, service-worker, manifest, image, form, and upload behavior is otherwise same-origin. Tracked images are local; the stylesheet contains seven local `data:image/svg+xml` values. No tracked frame, object/embed, audio/video, remote font, or CSS import dependency was found outside Plaid Link.

## Document And Resource Policy Matrix

| Document family | Examples | Script/style migration | Network/resource policy |
| --- | --- | --- | --- |
| Shared authenticated shell | `base.html` and extending full pages | Remove base and page inline scripts, native handlers, `hx-on`, inline style blocks/attributes, and runtime style writes. Configure HTMX without inline config execution. | Self-only scripts, styles, images, fetch/HTMX, worker, manifest, and forms. No frames. |
| HTMX fragments | dashboard/report/category/transaction components returned directly by routes | Remove all executable fragment scripts and inline handlers. Initialize swapped content from static JS through delegated listeners or `htmx:load`. | Fragment response headers do not establish a new document policy; the owning full document policy controls execution. |
| Login | `auth/login.html` | Move its inline style block to local CSS. | Strict core policy; no Plaid, frame, worker, or manifest exception needed beyond harmless shared directives. |
| Offline and errors | `offline.html`, `errors/403.html`, `404.html`, `500.html` | Move theme bootstrap, retry handler, and inline styles to local assets while preserving data-free rendering. | Strict core policy; service worker may navigate to `/offline`, but the document makes no external connection. |
| Standalone `/k/` | `kristine.html` | Move its executable script and dynamic width styles to local behavior/classes while preserving the existing server-side authentication and self-managed entity contract. | Strict core policy; no Plaid exception. CSP does not change the established authentication boundary. |
| Plaid Link documents | `data_sources.html`, `plaid.html` | Move application scripts/handlers/styles to local assets. Add any request nonce only to the exact external initializer if implementation follows Plaid's nonce example. | Narrow Plaid variant: exact initializer URL, `frame-src https://cdn.plaid.com`, and only the selected `sandbox` or `production` connect origin. Plaid-only `style-src-attr 'unsafe-inline'` exception unless a maintained isolated proof shows Link works without the documented requirement. |
| Static/PWA resources | `/static/*`, `/sw.js`, manifest, icons | No executable inline dependency. Move HTMX indicator rules into local CSS and set `includeIndicatorStyles=false` so HTMX does not inject a `<style>` element. | `worker-src 'self'`, `manifest-src 'self'`, `img-src 'self' data:`. Service worker remains same-origin and static/offline-only. |

## Candidate Enforced Policies

The policy is an HTTP response header on HTML responses. Static assets do not need a separate HTML CSP. Response scoping must be explicit so the Plaid exception cannot leak to unrelated documents.

### Core application documents

```text
default-src 'self';
base-uri 'none';
object-src 'none';
frame-ancestors 'self';
form-action 'self';
script-src 'self';
script-src-attr 'none';
style-src 'self';
style-src-attr 'none';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
frame-src 'none';
worker-src 'self';
manifest-src 'self';
media-src 'none'
```

### Plaid Link document variant

Start with the core policy and change only these directives:

```text
script-src 'self' 'nonce-<per-response-random>' https://cdn.plaid.com/link/v2/stable/link-initialize.js;
style-src-attr 'unsafe-inline';
connect-src 'self' https://sandbox.plaid.com;
frame-src https://cdn.plaid.com
```

For `PLAID_ENV=production`, replace the sandbox connect origin with `https://production.plaid.com`; never allow both merely for convenience. A random per-response nonce is a defense-in-depth match for Plaid's documented nonce form, not authorization for application inline script. Do not add `strict-dynamic`, wildcard hosts, `unsafe-eval`, general script `unsafe-inline`, `data:` scripts, or `blob:` scripts.

`upgrade-insecure-requests` is excluded from the initial policy because an unconditional directive would rewrite ordinary local HTTP dependencies. It may be reconsidered only as an explicitly Fly-only rule with synthetic local/Fly coverage. No report endpoint exists, so `report-uri`/`report-to` is excluded rather than adding a live reporting service. Trusted Types is parked as later hardening: tracked code has numerous deliberate HTML insertion sinks, and `require-trusted-types-for 'script'` would be a separate compatibility program rather than a CSP-header closeout requirement.

## Required Migration Matrix

| Migration slice | Exact work | Completion gate | Suggested bounded task/block |
| --- | --- | --- | --- |
| Shared execution foundation | Move `base.html` executable blocks and five native handlers to local JS; replace two base `hx-on` handlers; move indicator CSS to the tracked stylesheet; set only `includeIndicatorStyles=false`; and establish the declarative HTMX configuration point. Keep `allowEval` and `allowScriptTags` at their current values until the remaining fragment dependencies are removed. | Complete locally through 4AF: maintained source assertions and configured-auth/no-password isolated Chrome prove shared navigation, themes, AI chat, service-worker registration, CSRF/HTMX behavior, repeated representative swaps, and responsive drawer behavior with no executable inline shell markup. | Task 1P.4.2a / work block 4AF complete locally. |
| Swapped-fragment execution | Remove executable scripts and inline handlers from all directly returned HTMX components; replace the remaining two fragment `hx-on` handlers; carry swapped server values through non-script inert data; initialize through local static JS and `htmx:load`/delegation; then set `allowEval=false` and `allowScriptTags=false`. | Durable and deployed through 4AI-R. Configured-auth/no-password isolated Chrome preserves repeated swaps, charts, KPI/category/insight/AI behavior, reports, transaction sorting/copy/edit/splits, popup/queue controls, and cleanup with both switches false and no directly returned script elements. | Tasks 1P.4.2b.1-1P.4.2b.3 / work blocks 4AG-4AI-R complete, durable, deployed, and credential-free health verified. |
| Full-page execution | Migrate the remaining 5 executable inline scripts and every source or rendered native handler in standalone/error documents; preserve page-specific initialization through local modules/data. | Every full-page route works with `script-src-attr 'none'` and no inline application script. | Tasks 1P.4.2c.1-1P.4.2c.8 are durable, automatically deployed, and credential-free health verified through 4AR-R. |
| Application style compatibility | Move seven inline style blocks, 221 attributes, and runtime style writes to static CSS/classes or explicitly bounded data-driven states. | Core pages run under `style-src-attr 'none'`; responsive and visualization behavior passes at maintained breakpoints. | Task 1P.4.3a; likely split into shell/components and page clusters. |
| Exceptional documents and Plaid | Reconcile login, offline/errors, `/k/`, local SVG data images, worker/manifest, and Plaid route-specific behavior; preserve Plaid's narrow documented style-attribute exception only on Link documents. | Strict families have no exception leakage; mocked Plaid document proves exact policy/header/tag wiring without live Plaid. | Task 1P.4.3b. |
| Header enforcement and proof | Add route-family header generation and optional Plaid nonce plumbing only after migration gates pass; add maintained request and isolated-browser contracts. | No CSP violations on the required matrix; exact prohibited source probes are blocked; no protected/live dependency. | Task 1P.4.4. |

Task 1P.4.2 and Task 1P.4.3 are too broad as single autonomous blocks and must use the sub-slices above. Work block 4AF completed the shared foundation, work block 4AG completed the dashboard/report fragment slice, work block 4AH completed the transaction/supporting-modal fragment slice, and work blocks 4AI and 4AI-R made global HTMX disablement and cross-route proof durable, automatically deployed, and credential-free health verified. The 2026-07-22 just-in-time source pass decomposed Task 1P.4.2c into the route clusters below before any work block could reference them.

| Task | Route cluster | Verified residual execution inventory | Boundary and sequencing reason |
| --- | --- | ---: | --- |
| 1P.4.2c.1 | Core review pages: shared sidebar, dashboard, reports, transactions, To Do | 0 inline scripts; 0 native handlers after 4AJ | Reuses the maintained shared, dashboard-fragment, and transaction-fragment asset seams plus one repeated-HTMX browser path; complete and verified locally through 4AJ. |
| 1P.4.2c.2 | Categorization and upload | 0 inline scripts; 0 native handlers after 4AK | Dedicated maintained controller preserves form, subcategory, navigation, confirmation, and status-only reset behavior; durable, automatically deployed, and credential-free health verified through 4AK-R. |
| 1P.4.2c.3a | Cash Flow | 0 inline scripts; 0 native handlers after 4AL | Page-owned `cashflow.js` preserves account/card modal population, input sizing, due-day parsing, recurring setup, AI entry, keyboard/scrim closure, and entity visibility; complete and verified locally through 4AL. |
| 1P.4.2c.3b | Long-Term Planning | 0 inline scripts; 0 native handlers after 4AL | Page-owned `planning.js` preserves item add/edit/delete, source switching, birthday save, projections, AI entry, keyboard/scrim closure, Personal/BFM sharing, and Luxe Legacy denial; complete and verified locally through 4AL. |
| 1P.4.2c.3c | Short-Term Planning | 0 inline scripts; 0 template or Python-rendered native handlers; 0 inert JSON carriers after 4AM | Page-owned `short-term-planning.js`, delegated controls, non-script goal data, and handler-free budget responses preserve goal, plan, review, action-item, budget, subcategory, transaction-edit, fetch, AI, modal, keyboard, and Personal/BFM versus Luxe Legacy behavior; complete and verified locally through 4AM. |
| 1P.4.2c.4 | Weekly and Waterfall | 0 inline scripts; 0 native handlers after 4AN | Existing app-shell AI behavior plus page-owned `waterfall.js` preserve view, breakdown, target, tax, tooltip, animation, keyboard, URL, and entity-boundary behavior; durable, deployed, and credential-free health verified through 4AN-R. |
| 1P.4.2c.5 | Subscriptions | 0 inline scripts; 0 native handlers; 0 inert JSON carriers after 4AO | Page-owned `subscriptions.js`, delegated controls, non-script suggestion data, and inert endpoint templates preserve AI, suggestion, watchlist, detail, account-info, tips, clipboard, modal, keyboard, and all-entity behavior; complete and verified locally through 4AO. |
| 1P.4.2c.6 | Payroll | 0 inline scripts; 0 native handlers; 0 inert JSON carriers after 4AP | Page-owned `payroll.js`, delegated controls, non-script role-color data, and valid sibling edit/delete forms preserve BFM-only add, detail, spending, import-role, confirmation, modal, and keyboard behavior; complete and verified locally through 4AP. |
| 1P.4.2c.7 | Data Sources and Connected Accounts | 0 inline application scripts; 0 native handlers; 2 page-owned local controllers; 2 retained external Plaid initializers after 4AQ | Page-owned `data-sources.js` and `plaid.js`, delegated controls, non-script order-date data, and inert endpoint attributes preserve vendor selection/counting, confirmations, both Link flows, button states, and distinct form-versus-JSON exchange contracts under exact mocked initializer interception; durable, automatically deployed, and credential-free health verified through 4AQ-R. |
| 1P.4.2c.8 | Offline, errors, and standalone `/k/` | 0 inline scripts; 0 source or rendered native handlers after 4AR | Blocking template-free `standalone-documents.js` preserves early theme and delegated retry across offline/errors; deferred template-free `kristine.js` preserves `/k/` drill-down behavior. Maintained request and configured-auth/no-password isolated-browser proof covers exact 403/404/500 status, no exception leakage, authentication/entity boundaries, denied networking, expected synthetic status console entries only, zero unexpected browser/page errors, and exact cleanup; durable and health verified through 4AR-R. |

The original eight-cluster inventory reconciled exactly to 22 executable inline scripts, 116 template-native handlers, and two full-page inert JSON carriers. The 4AM recheck additionally found and removed two Python-rendered Short-Term Planning handlers inside the same confirmed route family. The 4AR recheck found that the maintained one-handler source aggregate omitted a Jinja-adjacent conditional `/k/` `onclick` visible after rendering; 4AR removed and proved both handler seams. The final tracked-template execution inventory is 0 executable inline scripts, 21 external executable script occurrences, 0 inert JSON script carriers, 0 source-recognized native handlers, and 0 `hx-on`, with separate rendered assertions covering the formerly omitted `/k/` seam.

### Current Style-Migration Inventory

The 2026-07-23 just-in-time source pass reconciled the application-owned style surface after the execution migrations. The 4AE baseline of 221 template style attributes remains the historical contract count. Work block 4AS then removed the complete shared-shell and dashboard/report slice: 26 template style attributes, two style attributes emitted by maintained JavaScript markup, and ten application runtime style writes. The verified residual source now contains seven inline style blocks, 185 template style attributes, seven generated-markup style attributes, and 21 application runtime style writes.

| Task | Route cluster | Current residual inventory | Boundary and sequencing reason |
| --- | --- | ---: | --- |
| 1P.4.3a.1 | Shared shell and dashboard/report pages/fragments | 0 included style attributes or runtime writes after 4AS | Static classes, semantic hidden state, entity classes, body-lock state, and bounded percentage classes preserve the responsive, HTMX-swap, chart, tooltip, and shell behavior; complete and verified locally through 4AS. |
| 1P.4.3a.2 | Transactions, matching, vendor cards, and supporting fragments | 63 template attributes; 7 generated attributes; transaction runtime writes | Reuses the fragment controller and repeated-swap path but has a separate dense editing, matching, dynamic split-line, and total-state verification surface. |
| 1P.4.3a.3 | Categorization, orphan reassignment, upload, and upload dialog | 1 style block; 56 template attributes | Shares compact form/table/dialog layout and the categorization-upload controller; preserves the separately validated status-only Undo contract. |
| 1P.4.3a.4 | Cash Flow, Long-Term Planning, and Short-Term Planning | 13 template attributes; cash-flow/planning runtime writes | Shares modal-origin, progress, visibility, sizing, responsive, and planning-boundary behavior with one synthetic planning verification path. |
| 1P.4.3a.5 | Weekly and Waterfall | 13 template attributes; Waterfall runtime writes | Shares the validated calculation output and data-driven bar, timeline, tooltip, animation, and responsive visualization path. |
| 1P.4.3a.6 | Subscriptions and Payroll | 3 template attributes; subscription/payroll runtime writes | Small page-controller slice with clipboard, disclosure, role-color, conditional-control, dialog, keyboard, and BFM-only verification. |
| 1P.4.3a.7 | Data Sources and Connected Accounts | 1 style block; 34 template attributes | Keeps application-owned style cleanup with the exact mocked Plaid wiring while leaving the third-party Link exception and route-family policy to Task 1P.4.3b. |
| 1P.4.3a.8 | Login, offline/errors, and standalone `/k/` | 5 style blocks; 3 template attributes | Uses document-family local assets and exact auth/status/no-leakage/mobile proof; policy selection and exceptional-document reconciliation remain Task 1P.4.3b. |

After 4AS, the remaining seven clusters reconcile exactly to seven style blocks, 185 template attributes, seven generated attributes, and 21 runtime writes. The proven shell, semantic-state, bounded-percentage-class, and browser-proof patterns are available to the denser transaction and page-family clusters. Header generation, nonce plumbing, policy enforcement, the Plaid third-party exception, and live or publication work remain separate.

## Template Surface Inventory

Counts are source occurrences, not estimates. `Script` excludes inert JSON; `JSON` is `type="application/json"`; `Event` is a native inline event attribute; `Style` is an element style attribute.

| Template | Script | JSON | `<style>` | Event | Style | `hx-on` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `auth/login.html` | 0 | 0 | 1 | 0 | 0 | 0 |
| `base.html` | 6 | 0 | 0 | 0 | 1 | 0 |
| `cashflow.html` | 1 | 0 | 0 | 0 | 2 | 0 |
| `categorize.html` | 0 | 0 | 1 | 0 | 26 | 0 |
| `categorize_orphans.html` | 0 | 0 | 0 | 0 | 10 | 0 |
| `components/ai_analysis.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/categories_compare.html` | 0 | 0 | 0 | 0 | 4 | 0 |
| `components/dashboard_body.html` | 0 | 0 | 0 | 0 | 6 | 0 |
| `components/dashboard_detail_cats.html` | 0 | 0 | 0 | 0 | 1 | 0 |
| `components/dashboard_detail_insights.html` | 0 | 0 | 0 | 0 | 2 | 0 |
| `components/dashboard_ie_insights.html` | 0 | 0 | 0 | 0 | 1 | 0 |
| `components/ie_ai_analysis.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/insights_upcoming.html` | 0 | 0 | 0 | 0 | 2 | 0 |
| `components/kpi_panel.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/match_card.html` | 0 | 0 | 0 | 0 | 5 | 0 |
| `components/rpt_view.html` | 0 | 0 | 0 | 0 | 3 | 0 |
| `components/sidebar.html` | 0 | 0 | 0 | 0 | 1 | 0 |
| `components/subcat_txns_popup.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/todo_queue_detail.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/txn_results.html` | 0 | 0 | 0 | 0 | 6 | 0 |
| `components/txn_row.html` | 0 | 0 | 0 | 0 | 3 | 0 |
| `components/txn_row_edit.html` | 0 | 0 | 0 | 0 | 4 | 0 |
| `components/txn_split_editor.html` | 0 | 0 | 0 | 0 | 35 | 0 |
| `components/vendor_card.html` | 0 | 0 | 0 | 0 | 2 | 0 |
| `dashboard.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `data_sources.html` | 2 | 0 | 1 | 0 | 7 | 0 |
| `errors/403.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `errors/404.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `errors/500.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `kristine.html` | 1 | 0 | 0 | 0 | 3 | 0 |
| `match.html` | 0 | 0 | 0 | 0 | 1 | 0 |
| `offline.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `payroll.html` | 0 | 1 | 0 | 0 | 3 | 0 |
| `plaid.html` | 2 | 0 | 0 | 0 | 27 | 0 |
| `planning.html` | 1 | 0 | 0 | 0 | 1 | 0 |
| `reports.html` | 0 | 0 | 0 | 0 | 8 | 0 |
| `short_term_planning.html` | 1 | 0 | 0 | 0 | 10 | 0 |
| `subscriptions.html` | 1 | 0 | 0 | 0 | 0 | 0 |
| `todo.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `transactions.html` | 0 | 0 | 0 | 0 | 14 | 0 |
| `upload.html` | 0 | 0 | 0 | 0 | 9 | 0 |
| `upload_dialog.html` | 0 | 0 | 0 | 0 | 11 | 0 |
| `waterfall.html` | 1 | 0 | 0 | 0 | 9 | 0 |
| `weekly.html` | 0 | 0 | 0 | 0 | 4 | 0 |

The table records templates with source occurrences. Two additional templates have no listed CSP-sensitive source occurrences and still inherit their owning document policy.

## Maintained Verification Contract

Task 1P.4.4 must use temporary synthetic `DATA_DIR` databases and fake or absent integration configuration. It must not contact Plaid, production, demo, real databases, or any non-localhost service.

Request-level assertions:

- Core HTML documents emit exactly the strict core policy; Plaid documents emit only the narrow variant.
- Authenticated/no-password modes, login, all three errors, offline, exact `/k/`, and representative HTMX fragments retain existing authentication and cache behavior.
- Plaid sandbox/production selection emits one connect origin; invalid or absent configuration cannot broaden the allowlist.
- Static, service-worker, and manifest responses retain their existing content types/cache contracts and do not receive contradictory HTML-only policy assumptions.

Isolated Chrome assertions:

- Deny all non-localhost traffic and mock the exact Plaid initializer when exercising its document wiring.
- Capture `securitypolicyviolation`, console errors, page errors, failed requests, and unexpected dialogs.
- Exercise desktop, phone, and exact `768px` responsive boundaries; configured-auth and no-password modes; full-page loads; repeated HTMX swaps; transaction editing/splitting; dashboard/report/chart initialization; login; offline/errors; `/k/`; manifest and service-worker installation; and mocked Plaid open/exit wiring.
- Inject prohibited inline script, event attribute, style attribute on a core page, `eval`, cross-origin fetch, cross-origin frame, object, and form target probes and assert that the policy blocks them. Keep probes synthetic and isolated from production code paths.
- Preserve the existing mobile-drawer, CSRF, safe-redirect, entity isolation, no-store, and static/offline-only service-worker contracts.

Required repository checks after each implementation slice remain the focused test, full synthetic smoke suite when product code changes, isolated browser coverage, Python/JSON syntax as relevant, `git diff --check`, command-center refresh/health, rendered-dashboard inspection, and exact-path scope review.

## Decisions Frozen By This Contract

1. No general `unsafe-eval`, executable-script `unsafe-inline`, wildcard host, or data/blob script source.
2. Executable code moves to maintained local static JavaScript; application nonces do not excuse inline migration.
3. HTMX ends with eval and swapped-script execution disabled, and its injected indicator style disabled.
4. Core documents target `style-src-attr 'none'`; Plaid's documented style-attribute exception is route-family-specific and cannot leak to login, `/k/`, offline/errors, or ordinary authenticated pages.
5. Only one Plaid API environment is allowed per response, selected from validated tracked environment behavior.
6. Trusted Types, CSP reporting infrastructure, and Fly-only request upgrading are not bundled into Task 1P.4.
7. Task 1P.4.2 and Task 1P.4.3 require smaller execution blocks; 4AF-4AI completed shared and fragment execution, 4AJ-4AP completed the first six full-page clusters, 4AQ/4AQ-R completed and released Plaid entry-page execution while retaining the exact external initializer boundary, and 4AR/4AR-R completed and released the final standalone/error execution cluster. Every style or enforcement slice remains separately gated.

Any wish to allow broader inline behavior, both Plaid environments, another external origin, live Plaid testing, public-route redesign, or Trusted Types is a plan-changing decision and requires Ryan's explicit direction.

# Content Security Policy Compatibility Contract

Status: Task 1P.4.1, Task 1P.4.2a, and both Task 1P.4.2b migration slices are durable and automatically deployed through work block 4AH-R. Final HTMX disablement and cross-route proof are complete locally through 4AI; page, style/document, header enforcement, publication, and later proof remain separately gated.

Parent: Phase 4 Task 1P.4 / finding `P3-3J-06`.

## Purpose And Boundary

This contract defines the target browser policy, the application surfaces that must be migrated before enforcement, and the maintained proof required to close the CSP half of `P3-3J-06`. Work block 4AE created the contract without product mutation. Work block 4AF implemented the shared execution foundation, work block 4AG implemented the dashboard/report fragment slice, work block 4AH implemented the transaction and supporting-modal fragment slice, and work block 4AI disabled HTMX eval and swapped-script processing after replacing three swapped inert JSON script carriers with non-script template data. None added a CSP header, changed authentication or Plaid behavior, or touched any live system.

Protected data, credentials, real databases, live Plaid Link, production/demo inspection, publication, deployment, and both preserved untracked files remain outside this planning artifact.

## Source-Grounded Constraints

- [HTMX security guidance](https://htmx.org/docs/#security) documents that `allowScriptTags=false` stops processing scripts in swapped content and `allowEval=false` disables event filters, `hx-on`, and `js:` forms of `hx-vals` and `hx-headers`. The same guidance recommends replacing those features through custom JavaScript and HTMX events.
- [HTMX configuration guidance](https://htmx.org/docs/#config) shows that `allowEval`, `allowScriptTags`, and `includeIndicatorStyles` default to `true`. The tracked local HTMX asset is version 2.0.4 and retains those defaults.
- [Plaid Link Web guidance](https://plaid.com/docs/link/web/#csp-directives) requires the Link initializer to load directly from its exact CDN URL and identifies Plaid frame and environment-specific connect origins. Plaid's nonce example still calls for `style-src-attr 'unsafe-inline'` on a Link document.
- [MDN CSP guidance](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) distinguishes nonces from source allowlists and recommends a restrictive default with explicit resource directives. [MDN `style-src-attr`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src-attr) confirms that this directive governs element `style` attributes independently of stylesheet and `<style>` sources.

## Inventory Summary

The tracked surface contains 46 HTML templates and seven standalone document roots: the shared `base.html` shell, login, three error documents, offline, and standalone `/k/`. After 4AI, the source inventory contains:

| Surface | Count | Contract consequence |
| --- | ---: | --- |
| All `<script>` elements | 31 | Must distinguish local/external executable scripts from the two remaining full-page inert JSON blocks. |
| Executable inline scripts | 22 | Move to maintained local static JavaScript; a nonce is not a migration substitute. The former shared-shell, dashboard/report fragment, and transaction/modal fragment blocks are now local assets. |
| External executable scripts | 7 | Local theme, HTMX, app-shell, dashboard-fragment, and transaction-fragment assets plus two exact Plaid Link initializer tags. |
| Inert `application/json` scripts | 2 | The three directly swapped carriers moved to non-script `<template>` data in 4AI because HTMX removes every script when `allowScriptTags=false`; the two remaining full-page carriers belong to Task 1P.4.2c. |
| Native inline event-handler attributes | 116 | Replace with delegated or initialized listeners before `script-src-attr 'none'`; the former base, dashboard/report fragment, and transaction/modal fragment handlers are removed. |
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
| Standalone public `/k/` | `kristine.html` | Move its executable script and dynamic width styles to local behavior/classes while preserving the explicit public-route contract. | Strict core policy; no Plaid exception. CSP does not decide whether `/k/` remains public. |
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
| Swapped-fragment execution | Remove executable scripts and inline handlers from all directly returned HTMX components; replace the remaining two fragment `hx-on` handlers; carry swapped server values through non-script inert data; initialize through local static JS and `htmx:load`/delegation; then set `allowEval=false` and `allowScriptTags=false`. | Complete locally through 4AI. Configured-auth/no-password isolated Chrome preserves repeated swaps, charts, KPI/category/insight/AI behavior, reports, transaction sorting/copy/edit/splits, popup/queue controls, and cleanup with both switches false and no directly returned script elements. | Tasks 1P.4.2b.1-1P.4.2b.3 / work blocks 4AG-4AI complete locally; 4AI publication remains separate. |
| Full-page execution | Migrate remaining page-level executable inline scripts and native handlers, including both Plaid entry pages; preserve page-specific initialization through local modules/data. | Every full-page route works with `script-src-attr 'none'` and no inline application script. | Task 1P.4.2c after fragment foundation; split by route cluster if needed. |
| Application style compatibility | Move seven inline style blocks, 221 attributes, and runtime style writes to static CSS/classes or explicitly bounded data-driven states. | Core pages run under `style-src-attr 'none'`; responsive and visualization behavior passes at maintained breakpoints. | Task 1P.4.3a; likely split into shell/components and page clusters. |
| Exceptional documents and Plaid | Reconcile login, offline/errors, `/k/`, local SVG data images, worker/manifest, and Plaid route-specific behavior; preserve Plaid's narrow documented style-attribute exception only on Link documents. | Strict families have no exception leakage; mocked Plaid document proves exact policy/header/tag wiring without live Plaid. | Task 1P.4.3b. |
| Header enforcement and proof | Add route-family header generation and optional Plaid nonce plumbing only after migration gates pass; add maintained request and isolated-browser contracts. | No CSP violations on the required matrix; exact prohibited source probes are blocked; no protected/live dependency. | Task 1P.4.4. |

Task 1P.4.2 and Task 1P.4.3 are too broad as single autonomous blocks and must use the sub-slices above. Work block 4AF completed the shared foundation, work block 4AG completed the dashboard/report fragment slice, work block 4AH completed the transaction/supporting-modal fragment slice, and work block 4AI completed global HTMX disablement and cross-route proof locally. Task 1P.4.2c remains separately gated and requires just-in-time route-cluster decomposition.

## Template Surface Inventory

Counts are source occurrences, not estimates. `Script` excludes inert JSON; `JSON` is `type="application/json"`; `Event` is a native inline event attribute; `Style` is an element style attribute.

| Template | Script | JSON | `<style>` | Event | Style | `hx-on` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `auth/login.html` | 0 | 0 | 1 | 0 | 0 | 0 |
| `base.html` | 5 | 0 | 0 | 0 | 1 | 0 |
| `cashflow.html` | 1 | 0 | 0 | 15 | 2 | 0 |
| `categorize.html` | 2 | 0 | 1 | 3 | 26 | 0 |
| `categorize_orphans.html` | 1 | 0 | 0 | 1 | 10 | 0 |
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
| `components/sidebar.html` | 0 | 0 | 0 | 2 | 1 | 0 |
| `components/subcat_txns_popup.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/todo_queue_detail.html` | 0 | 0 | 0 | 0 | 0 | 0 |
| `components/txn_results.html` | 0 | 0 | 0 | 0 | 6 | 0 |
| `components/txn_row.html` | 0 | 0 | 0 | 0 | 3 | 0 |
| `components/txn_row_edit.html` | 0 | 0 | 0 | 0 | 4 | 0 |
| `components/txn_split_editor.html` | 0 | 0 | 0 | 0 | 35 | 0 |
| `components/vendor_card.html` | 0 | 0 | 0 | 0 | 2 | 0 |
| `dashboard.html` | 2 | 0 | 0 | 4 | 0 | 0 |
| `data_sources.html` | 3 | 0 | 1 | 3 | 7 | 0 |
| `errors/403.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `errors/404.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `errors/500.html` | 1 | 0 | 1 | 0 | 0 | 0 |
| `kristine.html` | 1 | 0 | 0 | 0 | 3 | 0 |
| `match.html` | 0 | 0 | 0 | 0 | 1 | 0 |
| `offline.html` | 1 | 0 | 1 | 1 | 0 | 0 |
| `payroll.html` | 1 | 0 | 0 | 9 | 3 | 0 |
| `plaid.html` | 2 | 0 | 0 | 3 | 27 | 0 |
| `planning.html` | 1 | 0 | 0 | 10 | 1 | 0 |
| `reports.html` | 1 | 0 | 0 | 5 | 8 | 0 |
| `short_term_planning.html` | 2 | 1 | 0 | 22 | 10 | 0 |
| `subscriptions.html` | 2 | 1 | 0 | 15 | 0 | 0 |
| `todo.html` | 1 | 0 | 0 | 5 | 0 | 0 |
| `transactions.html` | 1 | 0 | 0 | 2 | 14 | 0 |
| `upload.html` | 0 | 0 | 0 | 3 | 9 | 0 |
| `upload_dialog.html` | 0 | 0 | 0 | 0 | 11 | 0 |
| `waterfall.html` | 1 | 0 | 0 | 12 | 9 | 0 |
| `weekly.html` | 0 | 0 | 0 | 1 | 4 | 0 |

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
7. Task 1P.4.2 and 1P.4.3 require smaller execution blocks; 4AF completed the shared foundation, 4AG completed the dashboard/report fragment slice, and 4AH completed the transaction/supporting-modal slice locally. No later slice is authorized by those completions.

Any wish to allow broader inline behavior, both Plaid environments, another external origin, live Plaid testing, public-route redesign, or Trusted Types is a plan-changing decision and requires Ryan's explicit direction.

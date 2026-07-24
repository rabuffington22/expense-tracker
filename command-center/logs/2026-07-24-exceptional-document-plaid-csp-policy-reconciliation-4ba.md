# Work Block 4BA — Exceptional Documents and Plaid CSP Policy Reconciliation

Date: 2026-07-24
Status: Complete and locally verified after a read-only `claude-fable-5` / `max` second opinion and finding disposition.
Scope: Phase 4 Tasks 1P.4.3b.1 and 1P.4.3b.2.
Boundary: Local, sanitized command-center policy work only. No product, template, route, service-worker, header, nonce, credential, live Plaid, protected-data, publication, deployment, workflow, or GitHub durability action.

## Source Reconciliation

- Application-owned residual style inventory remains zero after 4AZ.
- `web/static/style.css` contains exactly seven `data:image/svg+xml` URLs; `img-src 'self' data:` remains necessary.
- Login uses same-origin CSS and icons, has no script, and submits same-origin.
- Offline and all three error documents use same-origin `standalone-documents.js` and `style.css` with no inline execution or style.
- Standalone `/k/` uses same-origin `kristine.js`, `style.css`, and icons with no inline execution or style.
- The service worker registers and fetches same-origin, caches only the generic offline document and local static assets, and never retains protected dynamic content.
- The service worker's last-resort synthetic HTML contains fixed text only. Task 1P.4.4 must add the strict core CSP header to that synthetic response without changing the 4BA source boundary.
- `data_sources.html` and `plaid.html` each contain one exact Plaid initializer occurrence.
- `plaid.index`, `data_sources.index`, and a successful `data_sources.parse` render Link documents. Redirects and error-handler responses from those endpoints do not.
- Tracked `PLAID_ENV` validation accepts exactly `sandbox` or `production`.

## Official Policy Inputs

- Plaid Link Web guidance: <https://plaid.com/docs/link/web/#csp-directives>
  - exact initializer: `https://cdn.plaid.com/link/v2/stable/link-initialize.js`;
  - response nonce in `script-src`, `style-src`, and `style-src-elem`;
  - `style-src-attr 'unsafe-inline'`;
  - `frame-src https://cdn.plaid.com/`;
  - one environment-specific `connect-src` origin.
- MDN CSP guidance: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP>
  - a nonce is unpredictable, unique per response, and matches the policy and permitted element.
- CSP Level 3: <https://www.w3.org/TR/CSP3/>
  - CSP is delivered and enforced from the resource response, including navigation responses involving a service worker.

## Frozen Policy Result

The strict core policy remains:

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

Rendered Plaid Link documents start with the strict core policy and change only:

```text
script-src 'self' 'nonce-<per-response-random>' https://cdn.plaid.com/link/v2/stable/link-initialize.js;
style-src 'self' 'nonce-<per-response-random>';
style-src-elem 'self' 'nonce-<per-response-random>';
style-src-attr 'unsafe-inline';
connect-src 'self' https://sandbox.plaid.com;
frame-src https://cdn.plaid.com
```

Production replaces the sandbox origin with `https://production.plaid.com`; both are never permitted together.

## Task 1P.4.4 Handoff

- Default every `text/html` response, including directly navigable HTMX fragments, to the strict core policy.
- Select the Plaid variant with an explicit render/response marker only when `plaid.html` or `data_sources.html` actually renders.
- Bind the marker only after successful rendering or directly to the successful response object; do not infer the exception from endpoint identity. Redirects, authentication responses, and mid-render errors stay strict.
- Generate one unpredictable base64 nonce from at least 128 bits of CSPRNG output per rendered Link-document response and apply it only to the exact initializer plus the matching policy directives.
- Keep application scripts and styles external and nonce-free.
- Give the service worker's last-resort synthetic HTML response the strict core CSP header.
- Ship the service-worker byte change with header enforcement so installation re-precaches `/offline` with the strict header; prove the updated cache-served document carries it.
- Do not add the HTML policy to static, manifest, worker, or API/JSON responses.
- Prove sandbox and production separately with synthetic configuration and denied non-localhost networking; do not use credentials or live Plaid.
- Before relying on released enforcement with real Link, require a separately authorized live checkpoint with CSP-violation, console, and request capture. Unexpected Plaid runtime or cross-origin fetch behavior triggers a new scoped decision.

## Read-Only Review And Disposition

Ryan selected Claude CLI model `claude-fable-5` with `max` effort. The bundled streaming review completed successfully after 858 seconds.

Verdict: approve with corrections; no critical findings and no policy-string change.

Accepted:

- protect every `text/html` response, including directly navigated fragments;
- bind the Plaid marker only to a successfully rendered response and explicitly test mid-render failure;
- make the separately authorized real-Link checkpoint explicit;
- couple service-worker cache refresh to the enforcement release and test cached `/offline`;
- specify at least 128 CSPRNG bits and base64 nonce encoding.

Parked outside 4BA:

- `frame-ancestors 'none'`/`X-Frame-Options: DENY`;
- worker-scoped CSP;
- converting local SVG data images to files;
- removing deprecated `X-XSS-Protection`;
- CSP reporting, request upgrading, and Trusted Types;
- the existing global fetch wrapper's cross-origin CSRF-header behavior. Task 1P.4.4 must not silently repair it; the separately gated live Link checkpoint will determine whether a new scoped decision is required.

Review artifacts:

- `command-center/handoffs/second-opinion/2026-07-24-4ba-exceptional-documents-plaid-csp-policy-review.md`
- `command-center/logs/second-opinion/2026-07-24-4ba-fable-5-max-response.md`

## Verification

- Source inventory was performed against tracked post-4AZ templates, routes, client configuration, stylesheet, manifest, and service worker.
- No `web/`, `core/`, `scripts/`, workflow, dependency, or runtime file was modified by 4BA.
- Full product smoke is intentionally skipped because this work block changes no product behavior.
- The review and disposition are complete. Remaining closeout checks are Runway OS alignment, dashboard refresh/health/rendered inspection, exact-path scope review, and preserved-file verification.

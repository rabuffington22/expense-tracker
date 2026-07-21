# Work Block 4AE Evidence — CSP Compatibility Contract

Date: 2026-07-21

Scope: confirmed local-only Task 1P.4.1 planning. No product, template, JavaScript, CSS, maintained-test, dependency, authentication, security-header, service-worker, manifest, Plaid behavior, protected-data, live-system, GitHub, publication, or deployment mutation was authorized or performed.

## Evidence Collected

- Read the canonical Phase 4 state, roadmap, decisions, operating rules, maintained README/categories guidance, finding `P3-3J-06`, tracked templates, Flask response headers, local HTMX 2.0.4 asset, service worker, manifest, CSS asset references, Plaid environment mapping, and existing synthetic/browser test surfaces.
- Counted 46 template script elements: 38 executable inline scripts, three external executable scripts, and five inert JSON data blocks.
- Counted 161 native inline event-handler attributes, four `hx-on` handlers, seven inline style blocks, and 221 element style attributes.
- Classified the shared shell, full-page templates, directly returned HTMX fragments, login, offline/errors, standalone `/k/`, static/PWA resources, and two Plaid Link documents.
- Confirmed that ordinary application browser requests and forms are same-origin; Plaid Link is the only tracked external browser runtime; images are local with seven CSS `data:image/svg+xml` values; no other tracked external frame, font, media, object/embed, or CSS import dependency was found.
- Confirmed from official HTMX guidance that `allowScriptTags=false`, `allowEval=false`, and the HTMX event model provide the intended migration boundary.
- Confirmed from official Plaid Link Web guidance that the initializer must load directly from its exact CDN URL and that Link documents need documented frame/connect sources plus a style-attribute allowance even under the nonce example.
- Confirmed that CSP style attributes are independently governed by `style-src-attr`, so Plaid's exception cannot be safely represented as a source-specific attribute allowlist.

## Result

Created `command-center/csp-compatibility-contract.md` with:

- strict core and narrow Plaid document policies;
- exact resource origins and environment selection;
- full template occurrence inventory;
- document/resource and rewrite-to-task matrices;
- a synthetic request and isolated-Chrome proof contract;
- explicit prohibited exceptions and parked follow-ups;
- bounded sub-slices for oversized Tasks 1P.4.2 and 1P.4.3; and
- proposed next work block 4AF for only the shared execution foundation.

The key compatibility finding is that HTMX fragment scripts cannot be made robust merely by issuing a fresh nonce on each fragment response: the owning document's already-established CSP controls the inserted content. Executable behavior therefore must move out of swapped fragments before `allowScriptTags=false` and enforcement. Separately, Plaid's documented `style-src-attr 'unsafe-inline'` requirement should be confined to the two Link document routes instead of weakening all application documents.

The closeout sequencing review also confirmed that proposed 4AF cannot yet set `allowEval=false` or `allowScriptTags=false`: two fragment `hx-on` handlers and executable fragment scripts remain outside its shared-shell scope. 4AF may migrate the shell and disable only HTMX's injected indicator style. Task 1P.4.2b owns the remaining fragment migration and both global HTMX execution switches.

## Verification

- `jq empty command-center/state.json` passed.
- `node command-center/scripts/refresh-dashboard.js` passed.
- `node command-center/scripts/health-check.js` passed.
- `git diff --check` passed.
- A localhost Chromium inspection of the generated dashboard showed the 4AE block complete, Task 1P.4.1 done, Task 1P.4.2a planned/current, proposed 4AF unconfirmed, Ryan as the next-decision owner, no horizontal overflow, and zero console errors.
- Final scoped worktree review found only command-center changes from this planning block plus the two preserved untracked files. No application, template, JavaScript, CSS, maintained-test, dependency, runtime configuration, authentication, header, worker, manifest, or Plaid behavior path changed.

The full application smoke suite was intentionally skipped because this work block changes no application behavior. `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` remained untouched and untracked.

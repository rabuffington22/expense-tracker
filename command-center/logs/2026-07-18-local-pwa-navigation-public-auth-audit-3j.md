# Work Block 3J — Local PWA, Navigation, And Public-Auth Boundary Audit

Date: 2026-07-18

Status: complete and verified locally

## Scope

Audited Phase 3 Task 6 through tracked source, the maintained synthetic smoke suite, a repeated temporary Flask request probe, and a repeated isolated Chromium probe against a localhost app using fake secrets, temporary Personal/BFM/Luxe Legacy databases, disposable browser storage, and zero external requests.

The audit covered the manifest and icon contract, root-scoped service-worker installation, protected and dynamic cache behavior, offline fallback, desktop/tablet/phone layout, mobile-sidebar behavior, the deliberately public `/k/` route, server and client authentication behavior, CSRF, exempt routes, session-cookie and security-header posture, entity boundaries, and tracked coverage.

Excluded throughout: Tasks 7-8; all repairs from 3A-3I; product, migration, tracked-test, fixture, workflow, authentication, CSRF, encryption, credential, public-route, and demo changes; real databases or financial rows; passwords or credentials; Ryan's browser state; production/demo access; external calls; Plaid, Fly, GitHub Actions, downstream writes; GitHub durability; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Verification Summary

- `.venv/bin/python scripts/smoke_test.py` passed every maintained synthetic check before and after the audit.
- The temporary request probe passed 31 expected controls and reproduced 12 controlled findings. A fresh confirmation pass reproduced the same 31/12 result.
- The isolated Chromium probe passed 23 expected controls and reproduced six controlled findings. A fresh browser context reproduced the result with zero external requests.
- Chromium reported zero manifest errors. The root service worker installed, activated, and controlled the isolated page.
- The manifest's declared 192px and 512px icons matched their actual dimensions; the 1024px and 180px Apple icons also matched.
- Desktop at 1440px, tablet at 820px, and phone at 390px rendered without horizontal overflow. The public dashboard stayed within its 480px layout boundary.
- The phone hamburger, `aria-expanded`, scrim, scrim-close behavior, desktop sidebar, public route layout, branded offline fallback, CSRF rejection/acceptance, HTMX/JSON denial, HSTS-on-HTTPS, and basic security headers passed.
- The public route showed only the intended synthetic Personal and Luxe Legacy slices and excluded the synthetic BFM marker, but it also proved that unauthenticated transaction-level details are part of the current public contract.
- Visual inspection covered the desktop dashboard, open phone sidebar, public dashboard, branded offline fallback, and the active/closed command-center state.

## Behavior Matrix

| Boundary | Result | Evidence |
| --- | --- | --- |
| Manifest and icons | Pass | Standalone root start URL, expected icon sizes, correct image dimensions, and zero Chromium manifest errors. |
| Service-worker registration | Pass | `/sw.js` registered at root scope, installed, activated, and controlled the isolated page. |
| Offline fallback | Pass | A never-visited offline navigation rendered the branded offline page. |
| Protected and entity-specific offline cache | High defect | The worker precaches `/`, caches arbitrary successful dynamic GET responses, and keys them by URL rather than entity or authenticated session. An offline Personal request received the last cached BFM transaction page. |
| Desktop/tablet/phone layout | Pass | No horizontal overflow at 1440px, 820px, or 390px; desktop sidebar and phone header modes matched the CSS breakpoint. |
| Phone sidebar basics | Pass | Hamburger opening, `aria-expanded`, scrim visibility, and scrim close behavior worked. |
| Phone sidebar keyboard/focus | Medium defect | Opening retained focus on the hamburger, did not lock background scrolling, and Escape did not close the sidebar. |
| HTMX and JSON authentication | Pass | Unauthenticated HTMX and JSON-classified requests returned 401. |
| Full-page authentication | High defect | Unauthenticated full-page requests returned complete protected HTML, including the synthetic transaction marker, behind only a client-side overlay. |
| Client/server credential boundary | High defect | The rendered page publishes a reusable digest, and a second local app configured with that digest accepted the extracted value directly at `/auth/verify`. No password or real credential was used. |
| Auth configuration coherence | Medium defect | The client digest is hard-coded independently from `APP_PASSWORD_HASH`; no-password server mode still rendered a blocking overlay. |
| CSRF | Pass | Missing token returned 403; the session token permitted the same mutation; approved bearer/public exemptions remained reachable. |
| Session/browser hardening | Medium gap | Session cookies were HttpOnly but lacked explicit Secure and SameSite attributes; protected HTML lacked Content-Security-Policy. |
| Public `/k/` entity scope | Pass with high policy risk | Personal and Luxe Legacy synthetic details rendered without auth, BFM stayed excluded, and the main overlay/sidebar stayed absent. The intentionally public route includes transaction names, dates, amounts, categories, and selected balances. |
| Tracked coverage | Gap | The maintained smoke suite does not exercise configured auth, the public route, manifest/service-worker/offline behavior, entity-specific cache behavior, or responsive navigation. |
| Cleanup and outbound boundary | Pass | Both request runs removed their temporary roots; browser storage and screenshots were disposable; the browser made zero external requests; the local server and temporary data were removed. |

## Ranked Findings

### High — The main authentication boundary is client-bypassable and returns protected HTML before authentication

The server denies unauthenticated HTMX and JSON requests but deliberately allows full-page protected requests so the overlay can render. Those responses contain the complete server-rendered financial page. The same page publishes the digest used by the client gate, and `/auth/verify` accepts the digest itself as the server credential when configured to match.

Acceptance requires server-side denial or a credential-safe login response before protected HTML is rendered, server-side password verification that does not publish a reusable credential equivalent, and synthetic proof across full-page, HTMX, JSON, and session transitions.

### High — The PWA cache can serve protected content across entity and authentication state

The service worker precaches the protected root and caches every successful dynamic GET by URL. Cache keys do not include the entity cookie or authenticated session. The isolated confirmation loaded a BFM transactions response online, switched the cookie to Personal, went offline, and received the cached BFM page.

Acceptance requires a deliberate sensitive-data caching policy: protected/entity-specific HTML and API responses must not be cached under a shared URL key, auth/entity transitions must invalidate relevant entries, and offline behavior must never cross entity or session boundaries.

### High — The public dashboard exposes detailed Personal and Luxe Legacy financial information without authentication

The route is intentionally public and correctly excludes BFM, but current output includes transaction names, dates, amounts, categories, budget progress, and selected account balances for Personal and Luxe Legacy. Task 8 needs an explicit product decision on whether that exact unauthenticated data contract is acceptable.

Acceptance requires Ryan to choose the public data contract, then enforce and test the selected minimum: authenticate it, reduce it to non-sensitive aggregates, or explicitly accept the documented exposure with appropriate controls.

### Medium — Client and server authentication modes can drift or block no-password mode

The client digest is hard-coded independently of `APP_PASSWORD_HASH`. A different server hash makes the client and server disagree, while an empty server hash still leaves the browser overlay visible and blocking.

Acceptance requires one runtime source of truth and deterministic configured, unconfigured/demo, invalid, and changed-credential behavior.

### Medium — Mobile navigation lacks complete overlay accessibility behavior

The phone sidebar opens visually and updates `aria-expanded`, but focus remains on the hamburger, background scrolling remains available, and Escape does not close it.

Acceptance requires focus placement and restoration, Escape close, background scroll lock, and keyboard/screen-reader checks without regressing scrim or route navigation.

### Medium — Session and browser defense-in-depth controls are incomplete

The synthetic HTTPS response set an HttpOnly session cookie without explicit Secure or SameSite attributes, and protected HTML had no Content-Security-Policy. Existing frame, MIME, referrer, XSS, and HTTPS HSTS controls passed.

Acceptance requires an explicit production cookie policy and a tested CSP compatible with HTMX, local scripts, and required assets.

### Medium — PWA, public, configured-auth, cache, and responsive boundaries lack tracked regression coverage

All 3J evidence is deterministic but ephemeral. The maintained smoke suite does not cover the audited request classes, configured/no-password auth modes, public entity slice, manifest/icons, service worker, offline cross-entity behavior, or mobile navigation state.

Acceptance requires focused synthetic request tests plus an isolated browser suite that blocks outbound networking and uses temporary data and browser state.

## Preserved Boundaries

- No application, fixture, tracked-test, workflow, authentication, CSRF, encryption, credential, public-route, or deployment file changed.
- No real password, credential, protected database, financial row, browser profile, production/demo surface, external call, Plaid action, Fly action, GitHub Action, or downstream write was used.
- No repair was implemented; every finding is parked for Task 7 consolidation and Task 8 prioritization.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Next Readiness

Task 6 and work block 3J are complete as an audit. Task 7 can now consolidate all Phase 3 findings into a single severity and dependency order. The main authentication boundary and cross-entity PWA cache are the strongest candidates for the front of that consolidation, while the exact `/k/` public-data contract requires Ryan's Task 8 decision before repair scope is selected.

## Durability

Local-only. No commit, push, PR, merge, workflow, or deployment action is part of work block 3J.

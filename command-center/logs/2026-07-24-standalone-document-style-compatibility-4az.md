# Work Block 4AZ — Standalone Document Style Compatibility

Date: 2026-07-24
Status: complete, verified, local-only, and uncommitted
Branch: `codex/csp-standalone-styles`

## Scope

Task 1P.4.3a.8 plus only its focused Task 2 regression slice. The block covered login, offline, 403/404/500, and standalone `/k/` style compatibility. Service-worker and manifest behavior, routes, authentication, CSRF, CSP policy/enforcement, protected data, credentials, live systems, GitHub durability, publication, deployment, workflows, downstream systems, and unrelated untracked files remained excluded.

## Result

- Moved the login document styling to scoped `standalone-login-*` classes in maintained `web/static/style.css`.
- Moved the shared offline/error document styling to scoped `standalone-message-*` classes in the same already precached stylesheet.
- Replaced the three standalone `/k/` percentage style attributes with the existing bounded `u-pct-*` class contract.
- Preserved the blocking early-theme controller, offline retry controller, standalone `/k/` controller, service-worker source, routes, authentication, and CSRF behavior without modification.
- Reconciled exact application-owned style inventory from 5 style blocks / 3 template style attributes / 0 generated attributes / 0 runtime writes to 0 / 0 / 0 / 0.

## Verification

- Baseline and final full synthetic smoke passed.
- Focused source, rendered-response, request-status, authentication/entity-boundary, offline-asset, and final inventory assertions passed.
- Configured-auth and no-password isolated-browser coverage passed.
- Phone, exact 768px, and desktop checks passed without responsive overflow.
- Rendered login, offline, 403, 500, and `/k/` documents were visually inspected; the intended centered card/message layouts and bounded bars remained intact.
- Exact 403/404/500 statuses and no exception leakage remained intact.
- The existing service-worker precache still contains the stylesheet needed by the offline fallback; no service-worker edit was required.
- Denied non-localhost traffic, zero unexpected browser/page errors, and exact disposable-state cleanup passed.
- Python and JavaScript syntax, JSON, whitespace, command-center refresh/health, exact scope, and all preserved-file checks passed.

## Boundaries

No commit, push, PR, publication, deployment, workflow action, service-worker or manifest mutation, route, authentication, CSRF, CSP policy/enforcement, protected-data access, credential use, external/live action, downstream access, or preserved-file mutation occurred.

## Next Gate

Exact 4AZ-R durability and release require separate planning and confirmation. If publication is not desired, Task 1P.4.3b remains a separate planning decision.

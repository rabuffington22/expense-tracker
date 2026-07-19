# Work Block 4A — Server-Side Auth And Protected-Cache Repair

Date: 2026-07-18

Status: complete and verified locally; release not authorized

## Scope

Ryan directly prioritized the two leading 3J findings: protected financial HTML must not be returned before authentication, and protected or entity-specific responses must not be retained by the service worker. This local block included the Flask auth boundary, a standalone login, removal of client digest replay, legacy and modern password-hash compatibility, coherent no-password mode, static/offline-only caching, focused synthetic coverage, isolated-browser verification, documentation, cleanup, and Runway OS closeout.

The public `/k/` data contract, mobile navigation, cookie/CSP hardening, real credentials and data, production/demo, external calls, live actions, and all GitHub durability remained excluded.

## Implemented Boundary

- Configured full-page requests now redirect to `/auth/login` before entity setup or protected template rendering.
- HTMX and JSON requests continue to receive 401 when unauthenticated.
- The standalone login posts the plaintext password under CSRF protection and verifies it only on the server.
- Successful login clears prior session state and establishes the authenticated session; failed login returns a controlled error.
- Existing raw SHA-256 `APP_PASSWORD_HASH` values remain compatible through constant-time comparison, while Werkzeug password hashes are also accepted as a migration path.
- The hard-coded client digest, `localStorage` unlock state, overlay, and `/auth/verify` replay endpoint were removed.
- Unset `APP_PASSWORD_HASH` now renders the app directly without a contradictory client overlay.
- Dynamic responses use `Cache-Control: no-store`.
- Service-worker cache v4 removes `/` from precache, caches only `/static/` assets and the data-free `/offline` page, uses network-only dynamic requests, and deletes all older caches on activation.
- `/k/` remains deliberately public and retains its existing Personal/LL versus BFM behavior; its product-policy decision remains open.

## Verification

- Maintained synthetic smoke suite: passed, including all existing initialization, import, entity-isolation, route, export, saved-view, and To Do checks.
- New tracked auth/cache checks: passed configured legacy hash, Werkzeug hash, wrong password, correct password, CSRF rejection, safe next-path handling, HTMX 401, no protected redirect body, no-store responses, digest-route removal, no-password mode, public/exempt routes, cache version, and static-only runtime cache contracts.
- Isolated configured-auth Chromium probe: 19 of 19 checks passed with zero external requests.
- Isolated no-password Chromium probe: 2 of 2 checks passed with zero external requests.
- The configured-auth browser seeded an old v3 protected cache before activation; v4 deleted it, retained only static/offline URLs, and never cached authenticated transaction or public `/k/` pages.
- An online synthetic BFM transaction page followed by an offline Personal request returned the generic offline page and no BFM marker.
- Login and offline-fallback screenshots were visually inspected and rendered cleanly at phone size.
- Python compile, service-worker syntax, `git diff --check`, dashboard refresh, command-center health, generated-dashboard inspection, and final worktree review passed.

## Protected Boundaries And Cleanup

Only fake secrets, synthetic marker rows, temporary all-entity databases, disposable browser state, and localhost were used. No real password, credential, database, financial row, existing browser session, production/demo surface, external network call, Plaid action, Fly action, workflow, downstream write, commit, push, PR, merge, or deployment occurred. Both localhost servers stopped normally, and all 3J/4A temporary scripts, databases, browser profiles, caches, and screenshots were removed. The pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched.

## Remaining Gate

The repair exists only in the local worktree on `codex/server-side-auth-boundary`. Production behavior is unchanged until Ryan separately authorizes exact GitHub durability and release actions. Phase 3 Task 7 resumes after the repair is released or Ryan explicitly defers release.

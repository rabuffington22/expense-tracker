# Work Block 4AC — Explicit Session-Cookie Policy

Date: 2026-07-21

Status: complete and verified locally

## Result

The Flask factory now declares the session-cookie policy directly. HttpOnly and SameSite Lax apply everywhere; a non-empty Fly-provided `FLY_APP_NAME` adds Secure; and ordinary local HTTP remains usable. The cookie remains host-only, application-root scoped, named `session`, and non-permanent.

## Verification

- Baseline maintained synthetic smoke suite: pass.
- Final maintained synthetic smoke suite: pass.
- Local cookie attributes: `HttpOnly`, `SameSite=Lax`, `Path=/`, no `Secure`, no `Domain`, no `Expires`, and no `Max-Age`.
- Fly-simulated HTTPS cookie attributes: `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`, no `Domain`, no `Expires`, and no `Max-Age`.
- Fly-simulated authenticated root and `/k/` continuity: pass.
- Existing configured-auth, no-password, CSRF, exempt-route, and protected-cache contracts: pass.
- Python compilation: pass.
- Environment restoration and temporary-data cleanup: pass.

## Boundaries

No CSP, entity-cookie, mobile/PWA, broad browser, session lifetime/name/domain/path, migration, credential, protected-data, real-database, retained-upload, production, Fly, GitHub, publication, deployment, or live action occurred. `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` remained untouched and unstaged.

## Next Gate

Publication remains separate. If Ryan authorizes exact-scope durability and release, plan 4AC-R; otherwise Task 1P.3 is the next just-in-time planning gate.

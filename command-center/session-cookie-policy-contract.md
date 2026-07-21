# Session-Cookie Policy Contract

Date: 2026-07-21

Work block: 4AC — Explicit Session-Cookie Policy

## Scope

This contract resolves the cookie half of `P3-3J-06` for the Flask session cookie only. Content Security Policy, the separate entity preference cookie, mobile/PWA behavior, session lifetime or naming, live verification, and publication remain outside 4AC.

## Runtime Contract

- `SESSION_COOKIE_HTTPONLY` is explicitly `True` in every environment.
- `SESSION_COOKIE_SAMESITE` is explicitly `Lax` in every environment.
- `SESSION_COOKIE_SECURE` is `True` when Fly provides a non-empty `FLY_APP_NAME`; ordinary local HTTP remains `False`.
- The session cookie remains host-only, application-root scoped, named `session`, and non-permanent.
- No new secret, Fly configuration value, proxy trust, or operator setting is required.

## Preserved Behavior

- Configured server-side authentication and Werkzeug and legacy password-hash support.
- CSRF-backed login and safe local return paths.
- The authenticated root and `/k/` session boundary.
- No-password mode and the existing system-route exemptions.
- Temporary synthetic data, entity isolation, and protected-data boundaries.

## Maintained Proof

The authentication section of `scripts/smoke_test.py` proves:

- local responses set `HttpOnly; SameSite=Lax; Path=/` without `Secure`, `Domain`, `Expires`, or `Max-Age`;
- Fly-simulated HTTPS responses add `Secure` while preserving those other attributes;
- the secure Fly-simulated session authorizes the protected root and `/k/`;
- configured-auth, no-password, CSRF, cache, and exemption contracts continue to pass;
- the original `FLY_APP_NAME` environment state is restored.

## Boundaries

No credential, protected data, real database, retained upload, external request, Fly mutation, GitHub action, commit, push, PR, merge, deployment, or production inspection is part of 4AC.

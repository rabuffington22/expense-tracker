# Focused Dashboard Authentication Contract

Date: 2026-07-21

Status: implemented and verified locally through work block 4AB; publication remains separately gated

## Boundary

`/k` and `/k/` are standalone Personal and Luxe Legacy views, not public data surfaces. When `APP_PASSWORD_HASH` is configured, they use the same server-side session gate as the main application.

Authentication and entity setup are distinct decisions:

- `/k` is not authentication-exempt.
- `/k` remains global entity-setup-exempt because its route deliberately initializes and reads Personal and Luxe Legacy itself.
- BFM remains excluded from the route.

## Request Contract

- A configured unauthenticated full-page request redirects to `/auth/login` with a safe local return path.
- A configured unauthenticated HTMX or JSON request returns HTTP 401.
- Authentication completes before global entity setup, route-specific database initialization, background-sync launch, or protected rendering.
- An authenticated request preserves the existing standalone template, Personal and Luxe Legacy fields, BFM exclusion, and background-sync seam.
- When `APP_PASSWORD_HASH` is unset, `/k/` remains available under the application's established no-password/demo contract.

## Unchanged Exemptions

Static assets, `/health`, `/sw.js`, `/offline`, `/auth/login`, and bearer-protected `/plaid/sync-all` retain their established authentication and setup behavior.

Cookie flags, Content Security Policy, mobile navigation, generalized browser-test infrastructure, and publication are outside 4AB.

## Verification Contract

Maintained synthetic coverage must prove:

- both `/k` and `/k/` authenticate before routing or rendering;
- safe return-path preservation;
- HTMX and JSON 401 behavior;
- zero database initialization and zero background-sync launch before authentication;
- logical preservation of all three temporary entity databases on denial;
- authenticated Personal and Luxe Legacy rendering with BFM exclusion;
- no-password availability;
- unchanged system exemptions;
- denied networking and exact marker cleanup.

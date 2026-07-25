# Work Block 4BD — Installed-PWA And Browser-Boundary Coverage Convergence

Date: 2026-07-24

Status: complete and verified locally; uncommitted

Branch: `codex/pwa-browser-boundary-coverage`

## Scope

Work block 4BD covered Tasks 1P.6.1-1P.6.4 only:

- manifest, icon, and installability inputs;
- root-scoped service-worker installation and real offline entity isolation;
- configured-auth browser request, redirect, exemption, and sign-in boundaries;
- exact authenticated and no-password `/k/` Personal/Luxe Legacy fields with BFM exclusion.

Task 1P.7, CI, publication, product or asset repair, authentication/cache/public-route changes, protected data, real databases, production/demo, non-localhost access, GitHub actions, deployment, Fly, and downstream systems remained excluded.

## Result

The existing maintained browser runner already covered same-origin worker registration, cache-version refresh, generic standalone documents, configured-auth sign-in, responsive `/k/`, denied external networking, browser-error detection, and disposable cleanup. Work block 4BD extended that runner with the remaining explicit acceptance boundaries:

1. The root document links the exact `The Ledger` manifest; declared 192, 512, maskable, and 180-pixel icons load at their natural dimensions; the page is a secure localhost context; and the active worker script and scope are exactly `/sw.js` and `/`.
2. After representative Personal, BFM, and Luxe Legacy online visits, browser-controlled offline navigation returns one identical generic data-free document for every entity. The current cache contains only the generic offline route and static assets, cached CSS remains available, and a dynamic JSON request fails network-only.
3. Configured authentication redirects a full-page request to the standalone server login, returns 401 to HTMX and JSON requests, keeps manifest/worker/offline/health exempt, rejects an external return target, performs a synthetic local sign-in, and exposes no password, hash, client digest, or former overlay.
4. `/k/` ignores a BFM entity cookie, excludes both BFM fixture markers, and preserves the exact synthetic Personal budget fields plus Luxe Legacy account and KPI fields. The same maintained matrix continues to cover no-password mode, configured-auth mode, representative responsive widths, route-owned context, protected-cache behavior, and cleanup.

No product mismatch or repair need was found. `P3-3J-C01` and Task 1P.6 are complete locally through 4BD.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: passed.
- Baseline and final `.venv/bin/python scripts/mobile_drawer_browser_test.py`: passed.
- `.venv/bin/python -m py_compile scripts/mobile_drawer_browser_test.py`: passed.
- Browser requests remained localhost-only with expected deliberate offline and 401 errors scoped out of the unexpected-error ledger.
- Temporary browser profile, synthetic databases, server process, fake configuration, and environment restoration: passed through the maintained runner.
- `jq empty command-center/state.json`: passed after closeout.
- `git diff --check`: passed.
- Dashboard refresh, command-center health check, generated-state review, and rendered localhost inspection: passed after closeout.

The first focused iterations corrected test expectations only: Luxe Legacy online presence was asserted through its stable sidebar class; the complete synthetic fixture's expense and total fields were aligned to `$363` and `$637`; and deliberate offline/401 console entries were isolated from the unexpected-error check. Product source did not change.

## Changed And Preserved Boundaries

Maintained coverage changed in `scripts/mobile_drawer_browser_test.py`. This sanitized log, the issue/finding disposition, Runway OS sources, and generated dashboard changed for closeout. No product, dependency, workflow, configuration, or deployment file changed.

The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log were not edited, staged, deleted, or absorbed.

Work remains local-only and uncommitted. Exact-scope durability/publication requires a separately authorized 4BD-R block; if publication is parked, Task 1P.7 requires a separately confirmed 4BE block.

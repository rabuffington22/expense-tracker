# Work Block 4AF — Shared CSP Execution Foundation

Date: 2026-07-21

Status: complete and verified locally

## Scope

Work block 4AF completed Task 1P.4.2a only. It migrated the shared `base.html` execution surface to maintained local assets, moved HTMX indicator rules to local CSS, and added focused synthetic and isolated-browser proof. Fragment, remaining-page, style, policy-header, Plaid, publication, deployment, and live work remained outside scope.

## Result

- `web/static/theme-init.js` now applies the stored theme before rendering and keeps the browser theme color aligned.
- `web/static/app-shell.js` now owns shared theme controls, accessible drawer behavior, AI modal lifecycle, keyboard shortcuts, CSRF form and HTMX header wiring, and same-origin service-worker registration.
- `web/templates/base.html` contains no executable inline application blocks, native inline event handlers, or `hx-on` handlers. Shared server values remain declarative, and HTMX loads from the maintained local asset.
- `web/static/style.css` now owns the HTMX indicator rules, while declarative HTMX configuration disables only injected indicator styles.
- `allowEval` and `allowScriptTags` remain explicitly enabled as a temporary compatibility dependency. Task 1P.4.2b owns removing the remaining fragment dependencies before either setting changes.

## Verified Inventory

The tracked template inventory now contains 42 script elements: 32 executable inline scripts, five external scripts, and five inert JSON scripts. It also contains 156 native inline event-handler attributes and two `hx-on` attributes. The shared base template contributes three external scripts, one inert configuration element, and zero executable inline blocks or inline handlers.

## Verification

- Python compilation passed for `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py`.
- JavaScript syntax passed for both new maintained local assets.
- The full synthetic smoke suite passed, including the new shared CSP execution foundation assertions.
- The maintained isolated-browser matrix passed in configured-auth and no-password modes, covering local assets, early theme application, HTMX configuration and indicators, AI lifecycle, CSRF, service-worker registration, accessible drawer behavior, responsive boundaries, repeated transaction-fragment swaps, keyboard behavior, denied external requests, console/page errors, and cleanup.
- JSON validation and `git diff --check` passed before closeout.

## Boundaries And Durability

All test data was synthetic and temporary, non-localhost requests were denied, and cleanup passed. No protected data, credential, real database, retained upload, external request, production or demo inspection, GitHub publication, deployment, or live action occurred. The result remains local-only on `codex/csp-shared-execution-foundation`. The unrelated untracked `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` files were preserved.

## Next Gate

Run a separate just-in-time sizing pass over Task 1P.4.2b using the verified fragment inventory. No fragment migration or HTMX eval/script disablement is authorized by this closeout.

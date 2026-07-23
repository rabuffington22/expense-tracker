# Work Block 4AR — Standalone And Error-Document Execution

Date: 2026-07-23

Status: complete and verified locally on `codex/csp-standalone-documents`; durability and release remain separate.

## Scope

- Included Task 1P.4.2c.8 plus only its focused Task 2 regression slice.
- Migrated execution in `offline.html`, `errors/403.html`, `errors/404.html`, `errors/500.html`, and `kristine.html`.
- Preserved data-free error/offline rendering, early stored-theme initialization, retry behavior, exact error status codes, `/k/` authentication/entity boundaries, drill-down interaction, and no exception leakage.
- Excluded style and runtime-style migration, CSP headers/nonces/enforcement, routes, authentication, cache, CSRF, service worker, manifest, financial/database/product behavior, dependencies, protected data, credentials, real databases, retained uploads, external/live access, GitHub durability, publication, deployment, workflows, downstream access/writes, and both preserved untracked files.

## Result

- New blocking template-free `web/static/standalone-documents.js` applies the stored theme before error/offline styles paint and owns delegated offline retry behavior.
- New deferred template-free `web/static/kristine.js` owns delegated `/k/` category drill-down behavior.
- All five included source templates and rendered responses contain zero executable inline scripts, zero native handlers, and zero `hx-on`.
- The final tracked-template execution inventory is 0 executable inline scripts, 21 external executable script occurrences, 0 inert JSON script carriers, 0 source-recognized native handlers, and 0 `hx-on`.
- The prior maintained aggregate reported one native handler because its source regex counted the offline handler but missed the Jinja-adjacent conditional `/k/` `onclick`; focused rendered proof now covers that formerly omitted seam explicitly.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed; final section 11m proves five source templates, local assets, rendered responses, exact 200/403/404/500 status behavior, no exception leakage, and the final aggregate inventory.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes with early light-theme behavior, offline retry, exact 403/404/500 documents, expected synthetic status console entries only, zero unexpected console/page errors, `/k/` local-controller and drill-down behavior, Personal/Luxe Legacy scope without BFM leakage, denied non-localhost traffic, and exact temporary all-entity/browser cleanup.
- The maintained HTMX indicator assertion now observes its existing 200 ms CSS transition after 400 ms instead of 250 ms; a concurrent final run exposed the prior timing race, and the isolated rerun passed without changing product CSS or behavior.
- Relevant Python compilation and JavaScript syntax checks passed.
- JSON validation, `git diff --check`, exact-scope review, dashboard refresh, command-center health, generated-state assertions, and both preserved-file checks passed at closeout.

## Boundaries

- No route, authentication, cache, CSRF, service-worker, manifest, style, CSP policy/header/enforcement, financial, database, product, dependency, credential, protected-data, real-database, retained-upload, external/live, GitHub, publication, deployment, workflow, downstream, or destructive mutation occurred.
- `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` remain unmodified and untracked.
- Exact-scope 4AR-R durability/release and Task 1P.4.3a just-in-time decomposition remain separate Ryan gates.

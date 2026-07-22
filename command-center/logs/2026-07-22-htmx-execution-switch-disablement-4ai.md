# Work Block 4AI — Final HTMX Execution-Switch Disablement

Date: 2026-07-22

Status: complete and verified locally on `codex/csp-htmx-disablement`; publication is not authorized.

## Scope

Task 1P.4.2b.3 only: disable HTMX eval and swapped-script processing, prove the tracked template surface has no eval-backed HTMX attributes, prove directly returned fragment behavior without script elements, and preserve the maintained shared-shell, dashboard/report, and transaction/modal matrix across configured-auth and no-password modes.

Task 1P.4.2c and later work, full-page execution, style migration, CSP headers/nonces/enforcement, Plaid, authentication, cookies, CSRF, service-worker/manifest changes, financial behavior, vendored HTMX changes, new dependencies, credentials, protected data, real databases, external networking, production/demo, GitHub durability, publication, deployment, workflows, downstream access/writes, `scripts/sync_prod_to_local.sh`, and `command-center/now 2.md` remained excluded.

## Result

- `base.html` now declares `allowEval=false` and `allowScriptTags=false` while retaining `includeIndicatorStyles=false`.
- Maintained source proof finds zero `hx-on`, `hx-vars`, JavaScript-valued `hx-vals`/`hx-headers`, and HTMX trigger-filter attributes across tracked templates.
- Directly returned dashboard/report and transaction/supporting-modal fragments contain zero script elements and zero native inline handlers.
- The aggregate tracked inventory is 31 script elements: 22 executable inline scripts, seven external executable scripts, and two full-page inert JSON scripts. Native inline handlers remain 116 and `hx-on` remains zero; these residual full-page surfaces belong to Task 1P.4.2c.
- Shared shell, dashboard/report charts and controls, transaction filtering/sorting/copy/edit/suggestions/rules/splits, popup/queue/modal behavior, AI, CSRF, service-worker registration, drawer behavior, keyboard behavior, and exact cleanup remain intact under both authentication modes.

## Compatibility Finding And Correction

The first no-password browser run timed out waiting for the income/expense chart after both switches were disabled. HTMX 2.0.4 removes every `<script>` element from swapped content when `allowScriptTags=false`, including inert `type="application/json"` elements. The dashboard chart payload and two transaction split-editor payloads were therefore removed before their maintained controllers could initialize.

The three directly swapped JSON carriers moved to non-script `<template data-json>` elements, and the existing dashboard and transaction fragment readers now read template content. This was the smallest compatibility correction inside the confirmed Task 1P.4.2b.3 route family and verification path. A follow-up browser assertion initially looked for the split templates inside the editor root even though they are siblings within the modal; correcting the assertion target required no product change.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: passed before product edits.
- Final `.venv/bin/python scripts/smoke_test.py`: passed after the switch and inert-data changes, including sections 11b-11d.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py`: passed in configured-auth and no-password modes after the compatibility correction.
- Browser coverage included repeated dashboard/report and transaction swaps, charts, drilldowns, modals, split add/remove/auto/save/delete, popup/queue controls, shared shell, AI, CSRF, service worker, drawer, keyboard behavior, both runtime switches false, zero unexpected console/page errors, denied non-localhost requests, and exact cleanup.
- Python compilation and JavaScript syntax checks passed for the changed maintained test and controller files.
- Final JSON, whitespace, dashboard refresh/health/rendered-state, exact-scope, worktree, and preserved-file checks are recorded in the Runway OS closeout.

## Boundaries

No commit, push, PR, merge, publication, deployment, workflow action, production/demo inspection, credential, protected data, real database, retained upload, external request, downstream access/write, vendored HTMX change, or preserved-file mutation occurred.

Task 1P.4.2c remains the next planning gate. Exact-scope 4AI publication and every live action require separate Ryan authorization.

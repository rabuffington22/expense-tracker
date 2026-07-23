# Work Block 4AQ-R Evidence — Plaid Entry-Page Execution Release

Date: 2026-07-23

Status: complete, durable, automatically deployed, and credential-free health verified.

## Durability

- Exact thirteen-path source commit: `993506b25d37c452471ea9ea413e734efe25d122`.
- Local `main`, `origin/main`, and `codex/csp-plaid-entry` aligned to the exact source commit before closeout.
- The source commit was created from explicit-path staging and reached `main` by clean fast-forward followed by a non-force direct push. No PR was created.

## Automatic Release

- Automatic workflow: Fly Deploy run `30027699965`.
- Exact workflow source SHA: `993506b25d37c452471ea9ea413e734efe25d122`.
- Deploy job: `89276216665`.
- Every reported deploy step completed successfully, including `flyctl deploy --remote-only`.
- Credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200 with JSON `{"status":"ok"}` after deployment.

## Verification

- Full `.venv/bin/python scripts/smoke_test.py` passed, including focused Plaid entry-page source, rendered, request, exchange-format, entity-isolation, cleanup, and residual-inventory coverage.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes with exact Plaid initializer interception, mocked Plaid, denied non-localhost traffic, temporary synthetic all-entity data, zero unexpected browser errors, and exact cleanup.
- Python compilation, JavaScript syntax, JSON parsing, whitespace, dashboard refresh, dashboard health, generated-state inspection, exact staged paths, commit contents, ancestry, exact remote SHA, sensitive-addition review, protected-boundary review, and preserved-file checks passed.

## Boundary

No PR, force push, credential, protected data, real database, retained upload, authenticated production page, live Plaid, manual workflow action, workflow edit, non-automatic Fly mutation, downstream access/write, empty-vendor route repair, broader recovery, or mutation of `scripts/sync_prod_to_local.sh` or `command-center/now 2.md` occurred. Task 1P.4.2c.8 and every later policy or product mutation remain separately gated.

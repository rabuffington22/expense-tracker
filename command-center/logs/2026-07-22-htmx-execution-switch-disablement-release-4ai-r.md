# Work Block 4AI-R — Final HTMX Execution-Switch Durability And Release

Date: 2026-07-22

Status: complete, durable, automatically deployed, and credential-free production health verified

## Published Source

- Source commit: `3fb0d74966bed7806e13efa65e15609ff173e817`
- Branch path: `codex/csp-htmx-disablement` fast-forwarded to local `main`
- Remote target: `origin/main`
- Published set: the exact sixteen verified 4AI application, static-asset, maintained-test, CSP contract, issue, findings, evidence, and Runway OS paths
- Pull request: none, per Ryan's direct-main instruction
- Force push: none

## Automatic Release Evidence

- GitHub Actions workflow: `Fly Deploy`
- Run: `29954953878`
- Deploy job: `89041537857`
- Exact workflow head SHA: `3fb0d74966bed7806e13efa65e15609ff173e817`
- Result: completed successfully; every reported deploy step passed
- Non-blocking annotation: the existing `actions/checkout@v4` Node 20 deprecation notice, forced onto Node 24
- Credential-free production check: `https://ledger-oak.fly.dev/health`
- Production result: HTTP 200 with `{"status":"ok"}`

## Verification

- Local `main`, `origin/main`, and the workflow head matched the exact source SHA before closeout.
- Full synthetic smoke passed.
- Configured-auth and no-password isolated Chrome passed the shared-shell, dashboard/report, transaction/modal, false-switch, denied-network, zero-error, and exact-cleanup matrix.
- Relevant Python and JavaScript syntax, JSON, whitespace, dashboard refresh, command-center health, rendered dashboard, exact-path, staged-set, commit-content, protected-path, and high-confidence sensitive-addition checks passed.
- `command-center/now 2.md` and `scripts/sync_prod_to_local.sh` remained untracked and excluded.

## Boundaries Preserved

- No PR, force push, manual workflow dispatch or rerun, workflow edit, non-automatic Fly mutation, credential, protected data, real database, retained upload, authenticated production page, or downstream access/write occurred.
- Task 1P.4.2c and every later CSP slice remain separately gated.
- This release closeout changes sanitized command-center artifacts only and uses `[skip actions]` to avoid a second automatic deployment.

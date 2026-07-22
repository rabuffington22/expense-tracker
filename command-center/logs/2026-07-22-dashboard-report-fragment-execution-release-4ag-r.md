# Work Block 4AG-R — Dashboard And Report Fragment Durability And Release

Date: 2026-07-22

Status: complete, durable, automatically deployed, and credential-free production health verified

## Published Source

- Source commit: `2ea23d1a6399be5e37d96275e84d45519105846c`
- Branch path: source committed on `codex/csp-dashboard-report-fragments`, then local `main` fast-forwarded cleanly.
- Remote: `origin/main` matched the exact source SHA after a non-force direct push.
- Scope: exactly twenty-three verified 4AG paths; no PR.

## Release Proof

- Automatic workflow: Fly Deploy run `29895902768`.
- Deploy job: `88845905269`.
- Result: every reported step passed for exact source SHA `2ea23d1a6399be5e37d96275e84d45519105846c`.
- Production health: credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200 with `{"status":"ok"}`.
- GitHub annotation: the existing non-blocking Node 20 deprecation notice for `actions/checkout@v4`, forced onto Node 24; deployment succeeded.

## Verification

Exact source/staged paths, protected paths, high-confidence sensitive additions, full synthetic smoke, configured-auth/no-password isolated Chrome, Python/JavaScript syntax, JSON, whitespace, dashboard refresh/health/rendered state, commit contents, ancestry, exact remote SHA, automatic run/job result, production health, and preserved exclusions passed.

## Boundaries

No PR, force push, credential, protected data, real database, retained upload, authenticated production page, manual workflow action, workflow edit, non-automatic Fly mutation, downstream access or write, Task 1P.4.2b.2 implementation, broader recovery, or preserved-file mutation occurred. The unrelated untracked `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` files remained excluded.

## Closeout

This sanitized command-center-only closeout uses `[skip actions]` so it does not trigger another deployment. Proposed work block 4AH remains a separate Ryan confirmation gate for Task 1P.4.2b.2 only.

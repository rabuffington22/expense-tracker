# Work Block 4AT-R — Transaction And Matching Style Compatibility Release

Date: 2026-07-23
Durability: committed and pushed to `main`

## Published source

- Source commit: `30236a7def65d190fffc8ba89ce70cfab8ad5a09`
- Published set: the exact 19 verified 4AT application, controller, template, maintained-test, CSP contract, evidence, and Runway OS paths.
- Local `main`, remote `main`, and the feature base matched before a clean fast-forward and direct push without force or PR.

## Automatic release

- Workflow: `Fly Deploy`
- Run: `30045444363`
- Deploy job: `89335369654`
- Workflow head SHA: `30236a7def65d190fffc8ba89ce70cfab8ad5a09`
- Result: every reported deployment step passed.
- Annotation: the existing non-blocking Node deprecation notice for `actions/checkout@v4`, forced onto Node 24.

## Production verification

- Credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200.
- Sanitized response: `{"status":"ok"}`.
- Local `HEAD`, local `main`, and `origin/main` matched the source commit after deployment.

## Boundaries

- Exact-path, staged-set, protected-boundary, high-confidence sensitive-addition, maintained smoke, configured-auth/no-password isolated-browser, syntax, JSON, whitespace, dashboard, generated-state, commit-content, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed.
- No PR, force push, manual workflow action, workflow edit, non-automatic Fly mutation, credential, protected data, real database, retained upload, authenticated production page, downstream action, Task 1P.4.3a.3 work, broader recovery, destructive action, or preserved-file mutation occurred.
- `command-center/now 2.md` and `scripts/sync_prod_to_local.sh` remained untouched and untracked.
- Task 1P.4.3a.3 remains a separate Ryan planning and authorization gate.

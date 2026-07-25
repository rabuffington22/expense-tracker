# Work Block 4BJ-R — Safe Synthetic CI Durability Without Deployment

Date: 2026-07-25

Status: complete and durable on `main` without deployment.

## Authorization and route

Ryan directly instructed Codex to commit and push the verified 4BJ package to `main`. The direct-main route replaced the earlier draft-PR proposal but did not authorize a PR, workflow execution, deployment, browser CI, product change, protected access, or broader recovery.

Codex used two `[skip actions]` commits so publication could not trigger the existing push-to-`main` Fly deployment workflow. Staging was explicit and non-force publication was used throughout.

## Published source

- Source commit: `30b4cd97d749e244727a03400cdfa869c34c702b`
- Expected parent: `2babc9403f808ab65549751d11f5e3c429d8bf9d`
- Exact 13 paths:
  - `.github/workflows/synthetic-ci.yml`
  - `README.md`
  - `scripts/ci_safety_check.py`
  - `command-center/synthetic-ci-safety-contract.md`
  - `command-center/scripts/health-check.js`
  - `command-center/scripts/refresh-dashboard.js`
  - `command-center/logs/2026-07-25-safe-pr-synthetic-ci-foundation-4bj.md`
  - `command-center/decisions.md`
  - `command-center/index.html`
  - `command-center/issues.md`
  - `command-center/now.md`
  - `command-center/roadmap.md`
  - `command-center/state.json`

The containing `[skip actions]` commit publishes this sanitized closeout separately.

## Verification

- Full synthetic smoke: pass.
- Maintained CI safety checker under the project environment and bare Python 3.12: pass.
- Workflow YAML, Python 3.12 compilation, tracked JavaScript syntax, and command-center JSON: pass.
- Generated dashboard currentness, normal health, CI health, and rendered active-state inspection: pass.
- Whitespace, trailing-whitespace, high-confidence secret-pattern, operational-workflow no-diff, exact changed/staged/committed paths, expected ancestry, and preserved-file checks: pass.
- Local `HEAD`, local `main`, tracking `origin/main`, live remote `main`, and the GitHub commit API aligned to the source SHA after the non-force push.
- GitHub reported zero workflow runs for the source SHA.

## Boundaries preserved

- No PR, workflow enablement/execution/dispatch/rerun, deployment, Fly action, production/demo access, Plaid action, protected-data access, product/runtime/dependency/migration/authentication/CSRF/CSP change, operational-workflow edit, force push, conflict resolution, rebase, delegation, or second opinion occurred.
- `.github/workflows/fly-deploy.yml` and `.github/workflows/daily-plaid-sync.yml` remained unchanged.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and `command-center/logs/2026-07-23-categorization-upload-style-compatibility-4au 2.md` remained untracked, untouched, and excluded.

## Result and next gate

Tasks 3.1-3.2 and their safe core synthetic CI foundation are durable on `main` without deployment. The workflow has not executed because it is pull-request-only and both release commits skip Actions. A separately confirmed synthetic test PR is the recommended observation gate before any Task 3.3 browser-CI planning or implementation.

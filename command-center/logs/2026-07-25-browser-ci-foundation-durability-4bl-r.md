# Work Block 4BL-R — Browser CI Foundation Durability Without Deployment

Date: 2026-07-25

Status: complete and durable on `main` without deployment.

## Authorization and route

Ryan confirmed exact-path 4BL-R for the verified browser-CI foundation. Codex used direct, non-force `main` publication with two `[skip actions]` commits. No PR or remote feature branch was created because either would enter the separately gated hosted-observation path.

## Published source

- Source commit: `be14f5aa1e0733d6d12f57a221560eb96f95df5c`
- Expected parent: `7a5e21d9ba1363647c32cda23606fbdb9fa94827`
- Exact ten paths:
  - `.github/workflows/synthetic-ci.yml`
  - `README.md`
  - `scripts/ci_safety_check.py`
  - `command-center/synthetic-ci-safety-contract.md`
  - `command-center/logs/2026-07-25-pr-only-isolated-browser-ci-foundation-4bl.md`
  - `command-center/decisions.md`
  - `command-center/index.html`
  - `command-center/now.md`
  - `command-center/roadmap.md`
  - `command-center/state.json`

The containing `[skip actions]` commit publishes this sanitized closeout separately.

## Verification

- Full temporary-data synthetic smoke: pass in 9.74 seconds.
- Full configured-auth/no-password isolated-browser suite: pass in 287.69 seconds.
- Maintained CI safety, workflow YAML, Python compilation, tracked JavaScript syntax, and command-center JSON: pass.
- Generated dashboard currentness, normal/CI health, and rendered active-state inspection: pass.
- Whitespace, sensitive additions, operational-workflow exclusion, exact changed/staged/committed paths, expected ancestry, and preserved-file checks: pass.
- The first staged whitespace audit found three trailing spaces used as Markdown hard breaks in the new sanitized 4BL evidence header. They were removed and the exact-path audit passed before commit.
- Local `HEAD`, local `main`, tracking `origin/main`, live remote `main`, and the GitHub commit API aligned to the source SHA after the non-force push.
- GitHub reported zero workflow runs for the source SHA.

## Boundaries preserved

- No PR, remote feature-branch publication, workflow enablement/execution/dispatch/rerun/cancellation, deployment, Fly action, production/demo access, Plaid action, protected-data access, product/dependency/browser-test/runtime/migration/authentication/CSRF/CSP change, operational-workflow edit, force push, rebase, conflict resolution, branch deletion, delegation, or second opinion occurred.
- `.github/workflows/fly-deploy.yml` and `.github/workflows/daily-plaid-sync.yml` remained unchanged.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and `command-center/logs/2026-07-23-categorization-upload-style-compatibility-4au 2.md` remained untracked, untouched, and excluded.

## Result and next gate

Tasks 3.3.1-3.3.2 and the PR-only browser-CI foundation are durable on `main` without deployment. Neither the source publication nor this closeout executes the workflow. Task 3.3.3 and proposed 4BM remain a separate confirmation gate for one hosted core-then-browser observation through a no-merge draft PR.

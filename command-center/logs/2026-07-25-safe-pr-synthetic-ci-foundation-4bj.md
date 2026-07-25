# Work Block 4BJ — Safe PR-Only Synthetic CI Foundation

Date: 2026-07-25

Status: complete, locally verified, unpublished, uncommitted, and unstaged.

## Scope completed

- Froze the exact trigger, permission, checkout, immutable-action, Python 3.12, dependency, logging, network, timeout, command, and protected-data contract.
- Added one new workflow for pull requests targeting `main` only.
- Added one standard-library fail-closed workflow safety checker.
- Added deterministic read-only dashboard currentness and CI-health modes.
- Updated maintained README guidance and Runway OS state.

## Exact workflow contract

- Trigger: `pull_request` targeting `main` only.
- Permission: `contents: read` only.
- Checkout: full history for PR whitespace comparison; credentials are not persisted.
- Immutable official actions:
  - checkout `11d5960a326750d5838078e36cf38b85af677262`, verified against the official `v4` tag.
  - setup-python `a26af69be951a213d495a4c3e4e4022e16d87065`, verified against the official `v5` tag.
- Runner: `ubuntu-latest`, Python 3.12, 20-minute timeout.
- Dependencies: `requirements.txt` only; no development/browser dependency, cache, or artifact action.
- Commands: safety checker, full synthetic smoke, Python/JavaScript syntax, JSON, generated dashboard currentness, command-center CI health, and pull-request whitespace.
- No secrets, write permission, operational workflow edit, deploy, sync, Plaid, Fly, production/demo/downstream, browser suite, protected data, or real financial input.

## Network and logging boundary

The GitHub-hosted runner is not an egress firewall. GitHub retrieves the two pinned actions and `pip` retrieves tracked runtime dependencies from its normal public index. The reviewed workflow contains no other network command, passes no secrets or protected data, and invokes the maintained synthetic suite with its focused non-localhost denial checks. Logs are limited to ordinary setup, dependency installation, maintained checks, and synthetic diagnostics; there is no shell tracing, environment dump, or artifact upload.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: pass.
- Disposable Python 3.12 environment installed only `requirements.txt`, then ran the safety checker, full synthetic smoke, and compilation: pass; the environment was removed.
- The bare system Python 3.12 initially lacked installed packages and stopped at `pandas`; this was an environment precondition, not a product incompatibility.
- `.venv/bin/python scripts/ci_safety_check.py` and `python3.12 scripts/ci_safety_check.py`: pass.
- Workflow YAML syntax: pass.
- Python 3.12 compilation and tracked JavaScript syntax: pass.
- JSON validation, `refresh-dashboard.js --check`, `health-check.js --ci`, normal command-center health, and generated-state equality: pass.
- Whitespace, trailing-whitespace, high-confidence secret-pattern, exact operational-workflow no-diff, zero-staged, preserved-file, branch/base-SHA, and exact-scope checks: pass.
- Rendered active dashboard inspection before implementation: pass.

## Boundaries preserved

- No staging, commit, push, PR, merge, workflow enablement/execution/dispatch/rerun, deployment, production access, protected-data access, delegation, or second opinion occurred.
- `.github/workflows/fly-deploy.yml` and `.github/workflows/daily-plaid-sync.yml` are unchanged.
- Product source, migrations, dependencies, authentication, CSRF, CSP, Plaid, Fly, production/demo, downstream, real databases/uploads, and financial rows are unchanged and unaccessed.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and `command-center/logs/2026-07-23-categorization-upload-style-compatibility-4au 2.md` remain preserved and unrelated.

## Result and next gate

Tasks 3.1-3.2 and 4BJ are complete locally on `codex/safe-synthetic-ci`. Task 3 remains active. Proposed 4BJ-R may publish the exact verified source through the feature branch and a draft PR and observe the core synthetic run without merge or deployment. Task 3.3 browser CI remains planned only after the live core workflow proves stable.

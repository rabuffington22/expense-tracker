# Work Block 4BL — PR-Only Isolated-Browser CI Foundation

Date: 2026-07-25
Status: complete locally; unpublished, uncommitted, and unstaged
Branch: `codex/isolated-browser-ci`
Base: `main` at `7a5e21d9ba1363647c32cda23606fbdb9fa94827`

## Scope completed

- Froze Task 3.3.1's exact browser-CI and Node 24 action-runtime contract.
- Upgraded both jobs to the verified immutable official checkout v7.0.1 and setup-python v7.0.0 commits.
- Preserved the pull-request-to-`main`, `contents: read`, no-secret, and non-persistent-checkout boundary.
- Preserved the existing `core-synthetic` command surface on `ubuntu-latest` with a 20-minute timeout.
- Added `browser-synthetic` after core success on explicit `ubuntu-24.04`, Python 3.12, the installed Google Chrome channel, tracked `requirements-dev.txt`, and a 15-minute timeout.
- Added no browser download, dependency cache, artifact, service, container, environment, deploy, sync, or live-system surface.
- Expanded the standard-library safety checker to freeze the exact jobs, order, runners, timeouts, action SHAs, checkout behavior, reviewed commands, development dependency lines, and installed-Chrome/non-localhost-denial/temporary-data/exact-cleanup browser anchors.
- Updated compact maintained guidance and Runway OS.

## Exact workflow contract

- Trigger: `pull_request` targeting `main` only.
- Permission: top-level `contents: read` only.
- Checkout: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` in both jobs with `persist-credentials: false`.
- Python: `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` and Python 3.12 in both jobs.
- Core: `ubuntu-latest`, 20 minutes, existing runtime-only commands unchanged apart from the action pin upgrade.
- Browser: depends only on core, `ubuntu-24.04`, 15 minutes, reports installed Chrome, installs `requirements-dev.txt`, and runs `scripts/mobile_drawer_browser_test.py`.
- Network: action and public dependency retrieval are the only reviewed runner commands with network potential; browser requests outside the ephemeral localhost application are aborted by the maintained suite.
- Data/logging: synthetic temporary all-entity fixtures, mocked external seams, no secrets or protected inputs, no shell tracing/environment dump, no screenshots/videos/artifacts, and exact cleanup.

## Verification

- Maintained CI safety checker: pass.
- Workflow YAML parse: pass.
- Full synthetic smoke suite: pass in 8.86 seconds.
- Full configured-auth/no-password isolated-browser suite: pass in 287.25 seconds.
- Browser proof includes installed Chrome use, temporary Personal/BFM/Luxe Legacy databases, mocked external seams, non-localhost request denial, entity isolation, CSP/authentication/PWA/application-surface coverage, and exact cleanup.
- Python compilation and tracked JavaScript syntax: pass.
- `command-center/state.json` validation: pass.
- Dashboard refresh/currentness and normal/CI health: pass.
- Whitespace, reviewed sensitive-addition patterns, branch/base, zero-staged, exact-path, and preserved-file checks: pass.

## Boundaries preserved

- No product, dependency, browser-test, operational-workflow, runtime, migration, authentication, CSRF, or CSP change.
- No staging, commit, push, PR, workflow execution, rerun, merge, deployment, Fly/Plaid/production/demo/downstream, credential, protected-data, or real-data action.
- The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log remain untouched.
- The prior hosted Node 20 annotation is remediated only in the local source contract. Hosted confirmation remains unproven.

## Next separate gate

Proposed work block 4BL-R may publish the exact verified source package without deployment. Task 3.3.3 hosted browser observation remains a later, separate confirmation.

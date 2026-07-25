# Synthetic CI Safety Contract

Work block 4BJ established one locally verified GitHub Actions workflow for core synthetic verification. Work block 4BJ-R governs source publication without execution or deployment; an observed test PR remains a separate gate.

## Trigger and authority

- Trigger only on `pull_request` events targeting `main`.
- Grant only `contents: read`.
- Use no repository, environment, or organization secrets.
- Persist no checkout credentials.
- Do not expose `push`, `pull_request_target`, `workflow_dispatch`, `schedule`, deployment, synchronization, or production paths.

## Runner and dependencies

- Run one `core-synthetic` job on `ubuntu-latest` with a 20-minute timeout.
- Use Python 3.12 to match the production container.
- Pin official actions to the full commit SHAs verified from the official repositories on 2026-07-25:
  - `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (`v4`)
  - `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065` (`v5`)
- Install only `requirements.txt` from public Python package indexes. Do not install `requirements-dev.txt`, browser automation, caches, or artifact actions.

## Commands and data boundaries

The job may run only the reviewed commands in `.github/workflows/synthetic-ci.yml`:

- install tracked runtime dependencies;
- run the maintained workflow safety checker;
- run the temporary-data synthetic smoke suite;
- compile tracked Python and syntax-check tracked JavaScript;
- validate `command-center/state.json`;
- verify generated dashboard currentness without writing files;
- run command-center health in CI mode, where embedded-state equality replaces unreliable checkout mtimes;
- check whitespace across the pull-request diff.

The workflow may not read `.env`, `local_state/`, databases, uploads, statements, exports, payroll rows, Plaid tokens, financial rows, production, demo, Fly, or downstream systems. It may not invoke the browser suite, any sync, deploy, workflow mutation, or external application endpoint.

Network access is bounded but not sandboxed: GitHub retrieves the two pinned actions, and `pip` retrieves `requirements.txt` dependencies from its normal public package index. The reviewed workflow contains no other network command, and the maintained smoke suite uses synthetic temporary data with focused non-localhost denial checks. GitHub-hosted runners do not provide a general egress firewall here, so safety depends on passing no secrets or protected data, keeping token authority read-only, and reviewing changes to the workflow, checker, and invoked scripts before publication.

Logs are limited to ordinary action setup, dependency installation, maintained-check output, and synthetic failure diagnostics. The workflow contains no shell tracing, environment dump, secret expression, artifact upload, or real-data input.

## Maintained enforcement

`scripts/ci_safety_check.py` fails unless the workflow preserves the exact trigger, permissions, immutable actions, runtime, dependency, command, and forbidden-surface contract. The checker uses only the Python standard library and runs before the smoke suite.

The read-only dashboard checks are:

```bash
node command-center/scripts/refresh-dashboard.js --check
node command-center/scripts/health-check.js --ci
```

`--check` performs the normal structural and generated-state derivation while retaining the committed timestamp, then fails instead of writing if `state.json` or the embedded dashboard state would change. `--ci` retains the full health contract and exact embedded-state comparison while skipping only filesystem-mtime freshness, which is not stable across clean checkouts.

## Separate gates

The following remain unauthorized until Ryan confirms a later block: PR creation, workflow execution or rerun, merge, deployment, Task 3.3 browser CI, protected access, and any product or operational-workflow change.

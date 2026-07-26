# Synthetic CI Safety Contract

Work block 4BJ established the core synthetic workflow, 4BK observed one successful hosted core run, and local-only work block 4BL adds the isolated-browser job and remediates the prior Node 20 action-runtime annotation in source. Publication and hosted browser observation remain separate gates.

## Trigger and authority

- Trigger only on `pull_request` events targeting `main`.
- Grant only `contents: read`.
- Use no repository, environment, or organization secrets.
- Persist no checkout credentials.
- Do not expose `push`, `pull_request_target`, `workflow_dispatch`, `schedule`, deployment, synchronization, or production paths.

## Jobs, runners, and dependencies

- Run `core-synthetic` on `ubuntu-latest` with a 20-minute timeout.
- Run `browser-synthetic` only after core success, on explicit `ubuntu-24.04` with a 15-minute timeout.
- Use Python 3.12 in both jobs.
- Pin both jobs to the full official action commits verified on 2026-07-25:
  - `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (`v7.0.1`, Node 24)
  - `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` (`v7.0.0`, Node 24)
- Install only tracked `requirements.txt` in core and tracked `requirements-dev.txt` in browser. The latter includes the runtime requirements and the bounded Playwright dependency.
- Use the Google Chrome channel already present on the official Ubuntu 24.04 runner image. Do not run `playwright install`, download another browser, cache dependencies, upload or download artifacts, or add services, containers, or environments.

## Commands and data boundaries

The jobs may run only the reviewed commands in `.github/workflows/synthetic-ci.yml`.

Core may:

- install tracked runtime dependencies;
- run the maintained workflow safety checker;
- run the temporary-data synthetic smoke suite;
- compile tracked Python and syntax-check tracked JavaScript;
- validate `command-center/state.json`;
- verify generated dashboard currentness without writing files;
- run command-center health in CI mode, where embedded-state equality replaces unreliable checkout mtimes;
- check whitespace across the pull-request diff.

Browser may:

- report the installed `google-chrome` version;
- install tracked development requirements; and
- run `scripts/mobile_drawer_browser_test.py`.

The browser suite uses the installed Chrome channel in both authentication modes, an ephemeral localhost server, temporary synthetic Personal/BFM/Luxe Legacy databases, mocked external seams, denied non-localhost browser requests, and exact temporary-directory cleanup.

The workflow may not read `.env`, `local_state/`, real databases, uploads, statements, exports, payroll rows, Plaid tokens, financial rows, production, demo, Fly, or downstream systems. It may not invoke sync, deploy, workflow mutation, or an external application endpoint.

Network access is bounded but not runner-firewalled: GitHub retrieves the pinned actions, and `pip` retrieves the two tracked requirement sets from its normal public package index. The reviewed workflow contains no other network command. The browser itself aborts requests outside its ephemeral localhost application, including its mocked Plaid initializer seam. Safety therefore depends on passing no secrets or protected data, keeping token authority read-only, and reviewing changes to the workflow, checker, requirements, and invoked scripts before publication.

Logs are limited to ordinary action setup, installed-Chrome version, dependency installation, maintained-check output, and synthetic failure diagnostics. The workflow contains no shell tracing, environment dump, secret expression, artifact upload, screenshot/video capture, or real-data input.

## Maintained enforcement

`scripts/ci_safety_check.py` fails unless the workflow preserves the exact trigger, permissions, job order, runners, timeouts, immutable actions, runtime, checkout behavior, dependency commands, reviewed command order, and forbidden-surface contract. It also freezes the two-line tracked development dependency contract and checks maintained browser anchors for installed-Chrome use in both auth modes, two non-localhost denial paths, temporary synthetic data, and exact cleanup. The checker uses only the Python standard library and runs before the core smoke suite.

The read-only dashboard checks are:

```bash
node command-center/scripts/refresh-dashboard.js --check
node command-center/scripts/health-check.js --ci
```

`--check` performs the normal structural and generated-state derivation while retaining the committed timestamp, then fails instead of writing if `state.json` or the embedded dashboard state would change. `--ci` retains the full health contract and exact embedded-state comparison while skipping only filesystem-mtime freshness, which is not stable across clean checkouts.

## Separate gates

The following remain unauthorized until Ryan confirms a later block: staging, commit, push, PR creation, workflow execution or rerun, hosted browser observation, merge, deployment, protected access, and any product, dependency, browser-test, or operational-workflow change.

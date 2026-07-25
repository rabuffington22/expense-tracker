# Core Synthetic CI Observation — Work Block 4BK

Date: 2026-07-25

## Scope

Observe the durable pull-request-only `Synthetic CI` workflow through one marker-only draft PR, verify the exact hosted run and absence of deployment, close the PR without merge after success, and record a sanitized Runway OS closeout.

## Repository And GitHub Inputs

- Verified base `main`: `65b6b7aa37fcd1f9ff88a82b161a4afa54960006`.
- Feature branch: `codex/synthetic-ci-observation`.
- Marker-only feature commit: `cde1360e0e9f2041ebace7cd6555e2a021bf6400`.
- Draft PR: [#87](https://github.com/rabuffington22/expense-tracker/pull/87).
- Workflow run: [30175620834](https://github.com/rabuffington22/expense-tracker/actions/runs/30175620834).
- Core job: [89723824615](https://github.com/rabuffington22/expense-tracker/actions/runs/30175620834/job/89723824615).

## Result

- The run event was `pull_request`.
- The run head SHA exactly matched the marker-only feature commit.
- `Core synthetic checks` completed successfully in 52 seconds.
- Checkout, Python setup, runtime dependency installation, maintained workflow safety, full synthetic smoke, Python syntax, JavaScript syntax, command-center JSON, generated-dashboard currentness, command-center health, pull-request whitespace, and cleanup steps all passed.
- GitHub emitted one non-failing Node.js 20 deprecation annotation for the pinned checkout and setup-python action versions because the runner forced them onto Node.js 24. No workflow edit or repair was authorized or performed.
- No Fly Deploy run or other workflow run existed for the feature SHA.
- PR #87 was closed while still a draft; `mergedAt` remained null.
- Remote `main` remained at the verified base throughout the PR observation.
- The remote feature branch was retained at the feature SHA; branch deletion remained outside scope.

## Boundaries Preserved

- No product, workflow, dependency, configuration, migration, authentication, CSRF, CSP, database, upload, or category source changed.
- No merge, deployment, Fly, Plaid, production, demo, downstream, credential, protected-data, financial-row, manual dispatch, rerun, cancellation, branch deletion, force push, or broader recovery occurred.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log remained untouched and excluded.

## Local Verification

- `.venv/bin/python scripts/smoke_test.py`
- `.venv/bin/python scripts/ci_safety_check.py`
- `.venv/bin/python -m json.tool command-center/state.json`
- `node command-center/scripts/refresh-dashboard.js`
- `node command-center/scripts/health-check.js`
- `node command-center/scripts/refresh-dashboard.js --check`
- rendered dashboard inspection
- `git diff --check`

Task 3.2.1 is complete. Task 3.3 isolated-browser CI remains a separate just-in-time planning and confirmation gate; the non-failing action-runtime deprecation annotation should be considered during that later planning pass.

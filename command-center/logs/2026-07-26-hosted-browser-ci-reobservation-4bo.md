# Hosted Browser CI Reobservation And Safe Closure — Work Block 4BO

Date: 2026-07-26

Status: complete. The verified portability repair passed one clean hosted reobservation, draft PR #88 closed without merge, and the remote observation branch remains retained.

## Scope And Publication

- Verified base `main`: `4e9c285dd0237a3c576143fd85587fbda60dfc47`.
- Existing feature branch: `codex/browser-ci-observation`.
- Prior marker commit: `68959de40ca7de52cd20a0465d002ae4929c92ce`.
- Exact two-file repair commit: `bb6d14e7163e40976ffc2f0671509fd4b70f6a28`.
- Commit contents: `web/static/style.css` and `scripts/mobile_drawer_browser_test.py` only.
- Draft PR: [#88](https://github.com/rabuffington22/expense-tracker/pull/88).
- Pull-request workflow run: [30202164293](https://github.com/rabuffington22/expense-tracker/actions/runs/30202164293).
- Core job: [89793869350](https://github.com/rabuffington22/expense-tracker/actions/runs/30202164293/job/89793869350).
- Browser job: [89793962387](https://github.com/rabuffington22/expense-tracker/actions/runs/30202164293/job/89793962387).

## Local Preflight

- Active 4BO Runway OS JSON, refresh/currentness, health, rendered dashboard, and whitespace checks passed before staging.
- The complete synthetic smoke suite passed.
- The complete configured-auth/no-password installed-Chrome browser suite passed sequentially with all-entity, responsive, denied-network, and exact-cleanup contracts intact.
- Maintained CI safety and Python compilation passed.
- High-confidence sensitive-addition, exact-path, zero-preexisting-stage, branch, PR, remote, and preserved-file checks passed.
- Only the two approved repair paths were staged and committed. The five Runway OS paths and every untracked evidence or preserved file remained unstaged.

## Hosted Result

- The feature push produced exactly one workflow for the repair SHA: `Synthetic CI`, event `pull_request`, run `30202164293`.
- Core job `89793869350` ran first and passed every setup, dependency, safety, smoke, syntax, JSON, dashboard, whitespace, post-job cleanup, and completion step in 55 seconds.
- Browser job `89793962387` started only after core success and passed every setup, checkout, Python, installed-Chrome, dependency, complete browser-suite, post-job cleanup, and completion step in 5 minutes 23 seconds.
- The browser environment was Ubuntu 24.04 runner image `20260720.247.2`, Python 3.12.13, Google Chrome 150.0.7871.128, and Playwright 1.61.0.
- The maintained browser suite passed its complete matrix, including the transaction date-filter contract that stopped 4BM.
- Both jobs reported zero annotations.
- The repair SHA had exactly one workflow run and no Fly Deploy or other workflow.

## PR And Branch Disposition

- PR #88 closed without merge only after the completely clean hosted result.
- `mergedAt` remains null.
- Remote `codex/browser-ci-observation` remains retained at repair commit `bb6d14e7163e40976ffc2f0671509fd4b70f6a28`.
- Remote `main` remained unchanged at `4e9c285dd0237a3c576143fd85587fbda60dfc47` throughout feature publication and PR closure.

## Boundaries Preserved

- No merge, repair durability on `main`, production deployment, manual dispatch, rerun, cancellation, workflow edit, action/runner/browser-version/dependency change, further repair, Fly, Plaid, production/demo/downstream, credential, protected-data, or real-financial-data action occurred.
- No branch deletion, force push, rebase, conflict resolution, delegation, second opinion, or broader recovery occurred.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log remained untouched and excluded.

## Next Gate

The two-file repair is verified on the retained feature branch but is not durable on `main`. Proposed work block 4BP remains a separate Ryan decision for the exact durability path. Merge, deployment, and Phase 4 completion reconciliation are not inferred from 4BO.

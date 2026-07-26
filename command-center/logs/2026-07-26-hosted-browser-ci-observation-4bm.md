# Hosted Browser CI Observation — Work Block 4BM

Date: 2026-07-26

Status: stopped at the confirmed hosted-run failure boundary. Draft PR #88 remains open and unmerged for read-only diagnosis.

## Scope And Inputs

- Verified base `main`: `4e9c285dd0237a3c576143fd85587fbda60dfc47`.
- Feature branch: `codex/browser-ci-observation`.
- Marker-only feature commit: `68959de40ca7de52cd20a0465d002ae4929c92ce`.
- Draft PR: [#88](https://github.com/rabuffington22/expense-tracker/pull/88).
- Pull-request workflow run: [30191944724](https://github.com/rabuffington22/expense-tracker/actions/runs/30191944724).
- Core job: [89766609536](https://github.com/rabuffington22/expense-tracker/actions/runs/30191944724/job/89766609536).
- Browser job: [89766677978](https://github.com/rabuffington22/expense-tracker/actions/runs/30191944724/job/89766677978).

## Verified Hosted Result

- The run event was `pull_request` and its head SHA exactly matched the marker commit.
- `Core synthetic checks` ran first and passed every setup, dependency, maintained safety, full-smoke, syntax, JSON, dashboard-currentness/health, whitespace, post-job cleanup, and completion step in 48 seconds.
- Only after core success did `Isolated browser checks` start.
- The browser runner used Ubuntu 24.04, Python 3.12.13, Google Chrome 150.0.7871.128, and Playwright 1.61.0.
- Browser setup, checkout, Python setup, installed-Chrome verification, and tracked browser-dependency installation passed.
- The maintained browser suite failed after 27 seconds at its first reported mismatch: `no-password transaction/matching styles: Personal desktop date filters must preserve their fixed width`.
- The browser job concluded failure in 1 minute 5 seconds. GitHub reported exactly one failure annotation: `Process completed with exit code 1.`
- Post-checkout cleanup and job completion passed. The reported `Post Set up Python` step was skipped after the browser-suite failure.
- The prior Node.js 20 deprecation annotation did not recur; the only annotation was the browser-suite exit failure.
- No Fly Deploy or other workflow run existed for the marker SHA. Remote `main` remained at the verified base.
- Draft PR #88 remains open and draft with `mergedAt` null. The remote feature branch remains at the marker SHA.

## Local Versus Hosted Evidence

- Immediately before PR creation, the complete temporary-data smoke suite, full configured-auth/no-password installed-Chrome browser suite, maintained CI safety, JSON, generated-dashboard currentness, command-center health, and whitespace checks passed locally.
- Read-only source inspection found `.txn-filter-date { flex: 0 0 130px; }` with no explicit flex-item minimum-size override around an `input[type=date]`. A Linux Chrome intrinsic date-control minimum wider than the flex basis is a plausible cause of the hosted-only width mismatch.
- The failed assertion did not print the measured date-filter and filter-bar widths. The intrinsic-sizing explanation is therefore an inference, not a confirmed diagnosis or authorized repair.

## Stop And Boundaries Preserved

- 4BM stopped exactly as confirmed. No repair, workflow edit, product edit, dependency edit, rerun, manual dispatch, cancellation, PR closure, merge, deployment, branch deletion, force push, rebase, conflict resolution, or broader recovery occurred.
- No Fly, Plaid, production/demo/downstream, credential, protected-data, or real-financial-data access occurred.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log remained untouched and excluded.
- This stopped evidence and Runway OS state remain local and uncommitted. Publication while the failed PR remains open is not inferred.

## Next Gate

Ryan must separately confirm or revise a bounded remediation-and-reobservation block. A safe default would first add diagnostic width evidence and a narrow Linux-portable transaction date-filter sizing repair with local regression proof, then use a new feature commit to trigger a separately authorized hosted reobservation. No such work is authorized by stopped 4BM.

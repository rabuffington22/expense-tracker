# 2026-07-18 — Work Block 1B Recurring Sync Safeguards

## Authorization And Scope

Ryan confirmed work block 1B on 2026-07-18. The block authorized sanitized platform research, option comparison, a recommendation, and an implementation-ready follow-up. It did not authorize a monitor, automation, workflow edit, sync, credential access, production-data access, deploy, commit, push, PR, or merge.

## Current Evidence

- The repository is public and its default branch is `main`.
- Daily Plaid Sync is workflow ID `256886458`, path `.github/workflows/daily-plaid-sync.yml`, and currently reports state `active`.
- The workflow schedules `0 9 * * *`, exactly at the start of an hour.
- The last listed scheduled run before recovery succeeded on 2026-07-15. Controlled manual run `29627530457` succeeded on 2026-07-18.
- The last repository commit before the recovery work was 2026-05-15. New project activity resumed on 2026-07-17, more than 60 days later.
- During the confirmed-block preflight, the previously prepared Runway OS branch was found already merged and pushed to `main`; `main` and `origin/main` both pointed to `0b9d60d`. This was recorded as current truth rather than treated as pending work.

No response bodies, financial rows, credentials, secrets, Fly state, or database contents were opened.

## Authoritative Platform Behavior

GitHub documents that scheduled workflows in public repositories are automatically disabled after 60 days with no repository activity. GitHub also documents that scheduled workflows run only from the default branch and may be delayed or even dropped during high load, especially at the start of an hour.

Sources:

- [Disabling and enabling a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows?tool=cli)
- [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [REST API endpoints for workflows](https://docs.github.com/en/rest/actions/workflows)
- [REST API endpoints for workflow runs](https://docs.github.com/en/rest/actions/workflow-runs)
- [Notifications for workflow runs](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs)

The repository's public visibility, the more-than-60-day commit gap, the `disabled_inactivity` state found on 2026-07-17, and successful scheduled runs through 2026-07-15 strongly support GitHub's inactivity rule as the cause. This is an evidence-backed inference; GitHub did not provide a repository-specific cause event beyond the workflow state.

The successful scheduled runs did not themselves keep the workflow active. GitHub's normal run notifications are also insufficient as an absence detector: they report completed runs, but a disabled scheduler produces no run to notify about.

## Options Compared

| Option | What it catches | Main advantage | Main weakness | Disposition |
| --- | --- | --- | --- | --- |
| Manual monthly check | Disabled state visible when checked | No new system | Depends on memory and does not promptly detect missed runs | Fallback only |
| Same-repo keepalive commit | Can prevent the 60-day inactivity condition | GitHub-native | Mutates Git history, may trigger production deployment on `main`, and relies on the scheduler it is protecting | Reject |
| GitHub run-failure notifications | Failed runs that actually start | Built in | Cannot detect a missing run or an automatically disabled scheduler | Keep as secondary signal only |
| Independent read-only Codex monitor | Disabled state, stale scheduled run, or non-successful latest scheduled run | No workflow write, no financial data, no new paid service; independent of this repository's scheduler | Depends on the local Codex automation environment being available | Recommend |
| External cloud heartbeat monitor | Missing heartbeat or failed delivery | Strongest infrastructure independence | Adds an external account/integration and possibly recurring cost; requires workflow mutation | Park unless the local monitor proves insufficient |

## Recommendation

Create a local Codex recurring monitor attached to this project, scheduled after the expected daily run window. It should read only public GitHub metadata and alert Ryan when any of these conditions are true:

1. Daily Plaid Sync state is not `active`.
2. No `schedule` event has appeared within the preceding 36 hours.
3. The newest scheduled run is completed with a conclusion other than `success`, or remains incomplete beyond a conservative delay window.

The monitor must not enable, dispatch, rerun, or edit the workflow. Recovery remains a Ryan-confirmed action because an automatic re-enable could revive an intentionally disabled workflow and a dispatch can write new financial transactions.

The current `0 9 * * *` trigger should be moved away from minute zero in a separate source-and-release block. GitHub explicitly identifies the start of the hour as a high-load period where scheduled jobs can be delayed or dropped. That change has a different verification and deployment path from the monitor.

## Proposed Work Block 1C

Name: Independent Daily Sync Monitor.

Included: Phase 1 Task 5.

Excluded: Task 6; workflow changes; automatic enable, dispatch, or rerun; Plaid, Fly, application, secret, database, or financial-data access; paid external services; commit, push, PR, merge, or deploy.

Owner and recommended agent: Codex Desktop, because the block is a project-local automation setup with Runway OS stewardship and explicit sensitive-action boundaries.

Expected live effect: create one local recurring Codex automation that performs public, read-only GitHub checks and notifies Ryan only when the defined health conditions fail.

Stop conditions:

- The automation cannot run without credentials or private data.
- The available automation surface cannot reliably query current public workflow state and run metadata.
- The setup would enable, dispatch, rerun, or edit the workflow.
- The monitor requires an external paid service or broader system access.
- A test cannot distinguish scheduled runs from manual dispatches.

Verification:

- inspect the automation definition before activation;
- run one read-only test against current workflow metadata;
- prove the test reports `active` and identifies the latest scheduled run without opening logs;
- verify no workflow, application, or production state changed;
- update Runway OS, refresh the dashboard, and pass health check.

Report point: return the automation identity, cadence, exact alert thresholds, read-only test result, limitations, and separate Task 6 boundary.

## Result

Work block 1B completed without a stop condition. The recurrence cause is sufficiently explained, five safeguard approaches were compared, the independent alert-only monitor is the recommended next step, and the top-of-hour cron adjustment remains a separate later task.

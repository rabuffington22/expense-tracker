# Current Focus

## Active Objective

Execute confirmed work block 2A to restore a trustworthy root project entry point without changing application or production behavior.

## Current Phase

Phase 2: Project Truth And Documentation Recovery — active.

## Active Work Block

2A: Restore the Root Project Entry Point — confirmed and active.

## Current Task

Phase 2 Tasks 1 and 4: rebuild the root README for the current architecture and document sanitized deployment, data, and side-effect boundaries.

## Owner

Codex Desktop owns implementation, verification, command-center stewardship, branch durability, and draft-PR publication. Ryan owns review of the draft PR and the later Task 2 and Task 3 governance decisions.

## Status

Daily Plaid Sync changed from `disabled_inactivity` to `active`. Controlled workflow-dispatch run `29627530457` completed successfully; its sync job and all three job steps passed. The workflow remained active afterward. Production and demo roots both returned HTTP 200.

No workflow logs containing response bodies, financial rows, or credentials were opened. No source-code, secret, Fly, database-transfer, authentication, documentation, PR, merge, or parent-repo change occurred.

GitHub's documented 60-day inactivity rule matches the public repository's more-than-60-day commit gap before `disabled_inactivity`; this is an evidence-backed cause inference. Five safeguard options were compared. Work block 1C created active automation `expense-tracker-daily-plaid-sync-monitor`, which checks only public workflow metadata and alerts on disabled state, a missing scheduled run, a non-successful latest scheduled run, or a run that remains incomplete beyond the delay window. It must never enable or dispatch the workflow.

The stored automation is active on a daily 7:00 AM local schedule with a 36-hour freshness threshold and a three-hour incomplete-run threshold. The read-only test returned healthy: workflow state `active`, latest scheduled run `29640666471`, event `schedule`, status `completed`, conclusion `success`, and no alert conditions. Manual dispatch `29627530457` was separately visible as `workflow_dispatch` and did not satisfy freshness.

The automation create surface normalized the new cron to `ACTIVE` immediately even though the initial request used `PAUSED`. Codex inspected the stored definition before its first scheduled execution. The prompt requests no separate healthy notification, but the app may still retain normal automation run history; the first scheduled run will reveal the exact quiet-success presentation.

Work block 1D changed the default-branch cron from `0 9 * * *` to `17 9 * * *` without changing the UTC hour or `workflow_dispatch`. PR `#83` merged as `96af7dc`. Fly Deploy run `29645346441` completed successfully, including every job step. Daily Plaid Sync workflow `256886458` remained `active`, and production plus demo roots both returned HTTP 200.

No manual sync, workflow enable/disable/dispatch/rerun, application change, financial-data access, credential access, deployment-log read, monitor change, or parent-repo change occurred. The first natural minute-17 scheduled execution is intentionally not a closeout gate; the existing independent monitor will continue checking scheduled-run freshness and success after the normal run window.

## Durability

The 1D source change is committed as `e34c239` and merged to `main` as `96af7dc` through PR `#83`. This verified command-center closeout is published directly to `main` with `[skip actions]` so it does not trigger a second Fly deploy. Pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh` remain excluded and untouched.

## Current Action

Rebuild `README.md` from verified repository truth, add the confirmed sanitized operating boundaries, run the synthetic and Runway OS checks, and publish a draft PR from `codex/phase-2-root-docs` without merging or deploying.

## Locked Boundaries During Work Block 2A

- No `PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, or `AGENTS.md` edit, archive, deletion, or tracking change.
- No edit, staging, or tracking change to pre-existing untracked `scripts/sync_prod_to_local.sh`.
- No application, workflow, monitor, credential, ignored-data, database, Fly, authentication, deploy, merge, or parent-repo action.
- Draft-PR creation is authorized; merge and deployment remain excluded.
- The active monitor remains read-only and never performs recovery automatically.

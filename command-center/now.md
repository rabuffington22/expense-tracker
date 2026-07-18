# Current Focus

## Active Objective

Review the verified work block 2A draft PR, then define the separate Phase 2 governance block for the preserved legacy and instruction files.

## Current Phase

Phase 2: Project Truth And Documentation Recovery — active.

## Completed Work Block

2A: Restore the Root Project Entry Point — complete and verified on draft PR #84.

## Current Task

Phase 2 Task 2: decide the future of `PROJECT_KNOWLEDGE.md` and `plan.md`, awaiting review of draft PR #84 and a separately confirmed work block.

## Owner

Ryan owns review of draft PR #84 and confirmation or revision of the next Phase 2 governance block. Codex Desktop owns the verified 2A evidence, branch closeout, and the next just-in-time planning pass.

## Status

Work block 2A replaced the retired Streamlit/manual-import/two-entity README with a current Flask, HTMX, Plaid, Fly.io, and three-entity project entry point. The README now records local synthetic setup, application surfaces, entity/data isolation, environment-variable names without values, deploy mechanics, and explicit authorization gates for live or sensitive actions. `PROJECT_STRUCTURE.md` now classifies the README as current.

The full synthetic smoke suite passed, documentation claims were cross-checked against tracked runtime and deployment sources, stale architecture instructions were absent, excluded tracked files had no diff, and Runway OS refresh and health checks passed. Source commit `c249c9b` is pushed on `origin/codex/phase-2-root-docs`, and draft PR #84 is open without merge or deployment.

`PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, untracked `AGENTS.md`, and untracked `scripts/sync_prod_to_local.sh` remain preserved and unchanged. Their future is intentionally outside 2A.

Daily Plaid Sync changed from `disabled_inactivity` to `active`. Controlled workflow-dispatch run `29627530457` completed successfully; its sync job and all three job steps passed. The workflow remained active afterward. Production and demo roots both returned HTTP 200.

No workflow logs containing response bodies, financial rows, or credentials were opened. No source-code, secret, Fly, database-transfer, authentication, documentation, PR, merge, or parent-repo change occurred.

GitHub's documented 60-day inactivity rule matches the public repository's more-than-60-day commit gap before `disabled_inactivity`; this is an evidence-backed cause inference. Five safeguard options were compared. Work block 1C created active automation `expense-tracker-daily-plaid-sync-monitor`, which checks only public workflow metadata and alerts on disabled state, a missing scheduled run, a non-successful latest scheduled run, or a run that remains incomplete beyond the delay window. It must never enable or dispatch the workflow.

The stored automation is active on a daily 7:00 AM local schedule with a 36-hour freshness threshold and a three-hour incomplete-run threshold. The read-only test returned healthy: workflow state `active`, latest scheduled run `29640666471`, event `schedule`, status `completed`, conclusion `success`, and no alert conditions. Manual dispatch `29627530457` was separately visible as `workflow_dispatch` and did not satisfy freshness.

The automation create surface normalized the new cron to `ACTIVE` immediately even though the initial request used `PAUSED`. Codex inspected the stored definition before its first scheduled execution. The prompt requests no separate healthy notification, but the app may still retain normal automation run history; the first scheduled run will reveal the exact quiet-success presentation.

Work block 1D changed the default-branch cron from `0 9 * * *` to `17 9 * * *` without changing the UTC hour or `workflow_dispatch`. PR `#83` merged as `96af7dc`. Fly Deploy run `29645346441` completed successfully, including every job step. Daily Plaid Sync workflow `256886458` remained `active`, and production plus demo roots both returned HTTP 200.

No manual sync, workflow enable/disable/dispatch/rerun, application change, financial-data access, credential access, deployment-log read, monitor change, or parent-repo change occurred. The first natural minute-17 scheduled execution is intentionally not a closeout gate; the existing independent monitor will continue checking scheduled-run freshness and success after the normal run window.

## Durability

The 2A source implementation commit is `c249c9b` on pushed branch `codex/phase-2-root-docs` and draft PR #84. The verified closeout is being added to that same branch. Nothing is merged to `main`, and no Fly deployment is triggered. Pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh` remain excluded and untouched.

## Current Action

Review draft PR #84, then run a just-in-time planning pass for a possible 2B governance block covering Tasks 2 and 3. No legacy-document or instruction-source mutation is authorized yet.

## Locked Boundaries After Work Block 2A

- No `PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, or `AGENTS.md` edit, archive, deletion, or tracking change.
- No edit, staging, or tracking change to pre-existing untracked `scripts/sync_prod_to_local.sh`.
- No application, workflow, monitor, credential, ignored-data, database, Fly, authentication, deploy, merge, or parent-repo action.
- Draft PR #84 may be reviewed; merge and deployment require separate Ryan direction.
- The active monitor remains read-only and never performs recovery automatically.

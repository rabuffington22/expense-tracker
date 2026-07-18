# 2026-07-17 — Work Block 1A Operational Reliability Recovery

## Authorization

Ryan accepted Phases 1-5, authorized target-branch commit/push durability, and confirmed work block 1A with its documented live effects. The controlled run could insert newly available transactions and invoke the existing Luxe Legacy bridge.

## Scope

Included:

- Phase 1 Task 1: re-enable Daily Plaid Sync;
- Phase 1 Task 2: verify one controlled run;
- Phase 1 Task 3: establish production/demo health baselines;
- sanitized Runway OS closeout and target-branch durability.

Excluded:

- Task 4 safeguard design;
- source-code, workflow-file, secret, Fly, database-transfer, authentication, CSRF, encryption, documentation, PR, merge, or parent-repo changes;
- row-level financial or credential output.

## Before State

- Workflow ID: `256886458`
- Workflow path: `.github/workflows/daily-plaid-sync.yml`
- State: `disabled_inactivity`
- Last listed scheduled success: run `29408903430` on 2026-07-15
- Remote `main` workflow SHA-256 matched the local reviewed file.
- Reviewed target: `POST https://ledger-oak.fly.dev/plaid/sync-all` using the existing GitHub `SYNC_SECRET` reference.

## Actions And Evidence

1. Enabled `daily-plaid-sync.yml` through the authenticated GitHub CLI.
2. Verified workflow state changed to `active`.
3. Dispatched one controlled `workflow_dispatch` run. The dispatch command returned run `29627530457` directly.
4. Rejected a stale filtered-run lookup that returned an older May run and anchored all verification to the dispatch-returned run ID.
5. Waited for run `29627530457`; it completed successfully.
6. Verified the `sync` job and all three job steps completed successfully without opening response-body logs.
7. Verified the workflow remained `active`.
8. Verified production root HTTP 200 and demo root HTTP 200.

Run: `https://github.com/rabuffington22/expense-tracker/actions/runs/29627530457`

## Result

Work block 1A completed successfully without a stop condition. Daily sync scheduling is restored and the controlled end-to-end GitHub job passed. The remaining Phase 1 concern is recurrence: Task 4 must decide how to prevent or detect a future silent inactivity disablement.

## Durability

Baseline Runway OS commits `e9a8e5e` and `8ab8745` were already pushed on `origin/codex/runway-os-full-install`. This closeout will be committed and pushed on the same branch. No parent-repo change is authorized.

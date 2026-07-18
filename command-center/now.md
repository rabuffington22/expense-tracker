# Current Focus

## Active Objective

Review verified work block 2B and decide whether to publish the documentation-governance change through a separately confirmed release block.

## Current Phase

Phase 2: Project Truth And Documentation Recovery — active.

## Completed Work Block

2B: Retire Legacy Guidance And Establish Canonical Agent Instructions — verified on draft PR #85; not merged or deployed.

## Current Task

Phase 2 Task 3: reconcile `CLAUDE.md` and `AGENTS.md` — implementation is verified on draft PR #85 and current at the release-approval gate.

## Owner

Ryan owns review and confirmation or revision of a future 2B-R release block. Codex Desktop owns the verified branch, closeout evidence, exact restart point, and any later release execution after confirmation.

## Result

Work block 2B established `AGENTS.md` as the concise tracked canonical agent and contributor instruction source and reduced `CLAUDE.md` from a duplicated 1,150-line project encyclopedia to a compatibility entry point. It replaced `PROJECT_KNOWLEDGE.md` and `plan.md` with short historical notices that point to current sources and include exact Git-history recovery commands.

The source review found that Short-Term Planning is substantially implemented, but the legacy plan's proposed dedicated smoke cases and seeded goal/snapshot examples are not present as written. That discrepancy is now parked in `command-center/issues.md` for a fresh Phase 3 audit rather than being hidden, implemented out of scope, or left as a stale active plan.

Synthetic smoke tests passed. Documentation authority, stale-guidance, model-name, path, sensitive-content, Git-object, exact-scope, whitespace, dashboard-refresh, and command-center health checks passed. The original pre-block untracked `AGENTS.md` remains recoverable as Git blob `f8c8b792f29e91e3faf8cf8b253cfcb7e5ecb313`.

Source commit `912c9bb` is pushed on `origin/codex/phase-2-document-governance`. Draft PR #85 targets `main` and contains only the twelve authorized documentation and command-center paths. The GitHub connector lacked PR-write access, so the authenticated `gh` fallback created the draft PR as allowed by the publication workflow.

## Durability

- Branch: `codex/phase-2-document-governance`
- Source commit: `912c9bb`
- Draft PR: https://github.com/rabuffington22/expense-tracker/pull/85
- Status: committed and pushed on the feature branch; not merged; no deployment
- Preserved user file: untracked `scripts/sync_prod_to_local.sh`, untouched and unstaged

## Current Action

Ryan reviews draft PR #85 and confirms or revises a separately proposed 2B-R release block before any merge or production deployment.

## Release Boundary

- No merge, ready-for-review transition, deployment, workflow action, production health check, or closeout push is authorized yet.
- No application, workflow, authentication, database, Plaid, Fly configuration, credential, financial-data, parent-repo, or excluded-file change is authorized.
- A future 2B-R block should recheck the exact PR diff and mergeability, rerun safe verification, merge only after confirmation, observe the single automatic Fly deploy using sanitized status, verify production health, and close Phase 2 without triggering a second deploy.

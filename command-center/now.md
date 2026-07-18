# Current Focus

## Active Objective

Execute confirmed work block 2B to retire obsolete project guidance and establish one maintained agent-instruction source without changing application or production behavior.

## Current Phase

Phase 2: Project Truth And Documentation Recovery — active.

## Active Work Block

2B: Retire Legacy Guidance And Establish Canonical Agent Instructions — active and authorized.

Included: Phase 2 Tasks 2 and 3.

Excluded: completed Tasks 1 and 4; Phase 3; application code; tests; workflows; authentication; databases; Plaid; Fly configuration; credentials; financial data; production operations; untracked `scripts/sync_prod_to_local.sh`; parent-repo changes; merge; and deployment.

## Current Task

Phase 2 Task 2: replace `PROJECT_KNOWLEDGE.md` and `plan.md` with concise historical notices after confirming their useful current substance already has a canonical home.

## Owner

Codex Desktop owns implementation, source reconciliation, exact-scope verification, dashboard currency, branch publication, and final intake. Ryan owns review of the resulting draft PR and any later release authorization.

## Current State

Ryan confirmed work block 2B on 2026-07-18. The original untracked `AGENTS.md` was inspected before implementation and preserved as Git blob `f8c8b792f29e91e3faf8cf8b253cfcb7e5ecb313` so its exact pre-block contents remain recoverable while the confirmed tracked replacement is prepared.

The current root README and Runway OS already own architecture, setup, project direction, safety boundaries, and deployment controls. `PROJECT_KNOWLEDGE.md` still describes the retired Streamlit, Atlas-hosted, two-entity system. `plan.md` describes a Short-Term Planning direction that is substantially present in tracked migrations, routes, templates, navigation, AI context, budgets, goals, snapshots, and action items. Its promised dedicated smoke cases and seeded goal/snapshot examples are not present as written, so that discrepancy is parked for a fresh Phase 3 audit instead of being hidden or treated as a current plan. `CLAUDE.md` and the untracked `AGENTS.md` are near-duplicate 1,150-line references whose small differences include incorrect model-name substitutions in the untracked copy.

Work block 2A-R remains the last released block: PR #84 merged to `main` as `6270304`, automatic Fly Deploy run `29646390675` passed, production health and root returned HTTP 200, and the sanitized closeout is published on `main` as `3807792`.

## Current Action

Write the confirmed 2B active state into Runway OS, refresh and health-check the dashboard, then implement only the four authorized governance documents and supporting documentation links.

## Stop Conditions

- A legacy document contains unique current guidance without a safe canonical destination.
- The inspected untracked `AGENTS.md` cannot be reconciled without losing unique instructions.
- A proposed instruction would broaden live or sensitive authority beyond current operating rules.
- Application, workflow, database, credential, financial-data, production, parent-repo, or excluded-file changes become necessary.
- The diff expands beyond confirmed documentation and command-center scope.
- Verification fails in a plan-changing way.
- Branch publication includes unexpected paths.

## Verification And Report Point

Cross-check retained guidance against tracked source and canonical documentation; confirm the Short-Term Planning plan is implemented; scan for stale authority, architecture, model identifiers, live recipes, and financial history; run the synthetic smoke suite and `git diff --check`; refresh and health-check Runway OS; inspect the generated dashboard and exact staged paths; then push the verified branch and open a draft PR without merge or deployment.

## Durability

Active work is on `codex/phase-2-document-governance`. The verified implementation will be committed and pushed on that branch and opened as a draft PR. `main`, production, and the parent repo remain unchanged.

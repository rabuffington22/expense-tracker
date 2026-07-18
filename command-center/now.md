# Current Focus

## Active Objective

Publish verified documentation-governance work through confirmed release block 2B-R and close Phase 2 without widening content or operational scope.

## Current Phase

Phase 2: Project Truth And Documentation Recovery — active.

## Active Work Block

2B-R: Publish Canonical Project Guidance — active and authorized.

Included: Phase 2 Tasks 2 and 3 publication only.

Excluded: content changes beyond verified PR #85; application code; workflows or monitor changes; authentication; databases; Plaid; Fly configuration or secrets; credentials; financial data; parent-repo changes; pre-existing untracked `scripts/sync_prod_to_local.sh`; manual workflow actions; and out-of-plan recovery.

## Current Task

Phase 2 Task 3: publish the verified `AGENTS.md` and `CLAUDE.md` governance decision with the related legacy-document retirement through PR #85.

## Owner

Codex Desktop owns exact-scope release execution, sanitized deploy observation, stop judgment, command-center closeout, and final report. Ryan authorized the `main` publication and resulting automatic production deployment.

## Current State

PR #85 is open, draft, mergeable, targets `main`, and contains the expected thirteen documentation and Runway OS paths. Source and closeout commits are pushed on `origin/codex/phase-2-document-governance`; the feature branch is aligned with its remote. The only unrelated working-tree item is pre-existing untracked `scripts/sync_prod_to_local.sh`, which remains untouched and unstaged.

## Current Action

Commit and push the active 2B-R record to the feature branch, rerun safe pre-release verification, mark PR #85 ready, merge without force, observe the single automatic Fly Deploy using sanitized status only, and verify production root plus `/health` return HTTP 200.

## Stop Conditions

- PR #85 changes scope, loses clean mergeability, or no longer targets `main` from the expected branch.
- `main` diverges or branch protection changes the release path.
- Safe verification regresses.
- Fly Deploy fails or production root or `/health` does not return HTTP 200.
- Verification would require logs, credentials, secrets, financial data, Plaid, databases, or manual workflow action.
- Recovery requires application, authentication, infrastructure, credential, or financial-system mutation.
- The command-center closeout push would trigger a second deploy.

## Report Point

Return the merge commit, automatic deploy run and sanitized result, HTTP health, final branch durability, protected boundaries, closeout commit, and the Phase 3 just-in-time planning boundary.

## Durability

The active 2B-R record will be committed and pushed on `codex/phase-2-document-governance` before the PR is released. After verified deployment, a command-center-only closeout may be committed directly to `main` with `[skip actions]` so it does not trigger another deployment.

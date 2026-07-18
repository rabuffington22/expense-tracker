# 2026-07-18 — Work Block 2A-R Root Project Entry Point Release

## Authorization And Scope

Ryan explicitly instructed Codex to commit and push the verified work block 2A documentation to `main`. The release block authorized marking PR #84 ready, merging its exact verified diff, observing the one automatic production Fly deploy, checking sanitized workflow/job/step status and production HTTP health, and publishing a command-center-only closeout with `[skip actions]`.

Tasks 2 and 3, content expansion, application code, workflows, monitor changes, databases, Plaid, credentials, row-level financial data, Fly configuration or secrets, authentication, legacy files, pre-existing untracked files, parent-repo changes, manual workflow actions, and out-of-plan recovery remained excluded.

## Pre-Release Verification

- PR #84 was open, draft, cleanly mergeable, and limited to the expected eight documentation and Runway OS paths.
- The synthetic smoke suite passed all database, import, deduplication, entity-isolation, route, export, saved-view, and To Do checks using a temporary synthetic `DATA_DIR`.
- Runway OS dashboard refresh and health check passed.
- The active release dashboard was visually inspected, and its task-level next action was corrected before publication.
- `git diff --check` passed.

## Release And Verification

- PR #84 was marked ready and merged without force.
- Main merge commit: `6270304`.
- Fly Deploy run: `29646390675`.
- Deploy job and every listed step completed successfully.
- Production `/health`: HTTP 200.
- Production root: HTTP 200.
- No deployment logs or HTTP response bodies were opened.
- No manual workflow dispatch, rerun, Fly action, Plaid action, database access, credential access, financial-data access, application change, authentication change, legacy-file change, or recovery action occurred.

GitHub emitted a non-blocking annotation that `actions/checkout@v4` targets deprecated Node 20 and is currently forced to Node 24. The annotation did not affect the release and no workflow change was made in this block.

## Durability

- PR #84: merged.
- Main release commit: `6270304`.
- Verified release closeout: published directly to `main` with `[skip actions]`.
- Second Fly deploy: intentionally suppressed.

## Result

Work block 2A-R completed without a safety stop. The restored root project entry point and sanitized operating boundaries are now on `main`, production is healthy, and Phase 2 returns to the separately gated legacy-document and instruction-governance decision.

## Learning

Even a documentation-only merge deploys the production app because every push to `main` uses the same Fly workflow. The release path is healthy and predictable, but GitHub now warns that `actions/checkout@v4` relies on deprecated Node 20 compatibility. That warning is not urgent for this release, yet it is a concrete maintenance signal to consider in a future workflow-specific block rather than mixing it into documentation governance.

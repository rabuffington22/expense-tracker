# Expense Tracker Runway OS Roadmap

Runway OS is the operating system for the existing Expense Tracker application, also branded in-product as The Ledger. The application already exists and runs in production; this roadmap is about restoring reliable operations, trustworthy project state, and an ordered path for repairs and improvement.

Ryan confirmed Phases 1-5 as the baseline roadmap on 2026-07-17. Work still runs through separately confirmed, bounded work blocks.

## Phase 0: Full Runway OS Installation And Baseline

Status: complete

Goal: install the complete in-repo command center, migrate current planning truth into its canonical surfaces, and establish a safe verified baseline without changing application or production behavior.

- **Task 1: Inventory the existing repo and preserve pre-existing state.** Record branch, HEAD, remote, dirty files, current planning surfaces, sensitive boundaries, and safe verification commands. Status: done.
- **Task 2: Install the full Runway OS scaffold on a dedicated branch.** Add the command center and standard helper surfaces without overwriting existing repo files. Status: done.
- **Task 3: Migrate current project-control truth.** Replace scaffold placeholders with Expense Tracker's current focus, decisions, operating rules, architecture, issues, source migration map, and proposed roadmap. Status: done.
- **Task 4: Adapt the verification contract to the existing repo shape.** Recognize `web/`, `core/`, `scripts/`, and root entry points instead of requiring scratch-only `app/` and `scratch/` folders. Status: done.
- **Task 5: Verify and close the bootstrap.** Refresh the dashboard, run Runway OS health checks, run the synthetic smoke suite, inspect the generated dashboard, and run git consistency checks. Status: done.
- **Task 6: Review the proposed roadmap and authorize the first operational block.** Ryan confirms or changes the proposed phase plan and the Phase 1 work block before any workflow, production, or application mutation. Status: done; Ryan accepted Phases 1-5 and confirmed 1A.
- **Task 7: Commit and push the verified Runway OS baseline.** Stage only `PROJECT_STRUCTURE.md` and `command-center/`, preserve the pre-existing untracked files, commit the install branch, and push it to `origin`. Status: done; baseline commit `e9a8e5e` is pushed on `origin/codex/runway-os-full-install`.

### Confirmed Work Block 0A: Full Runway OS Install

Status: done

Included: Tasks 1-5.

Excluded: Task 6; re-enabling or manually triggering GitHub Actions; Plaid syncs; Fly deploys; production data access; `.env` or `local_state/` access; application fixes; legacy-document rewrites; changes to pre-existing untracked files; commit, push, PR, or merge.

Owner: Codex.

Stop conditions:

- An existing tracked or untracked project file would be overwritten.
- Verification requires credentials, production data, a live financial mutation, or an external side effect.
- The full scaffold cannot be adapted to the existing repo shape without weakening meaningful checks.
- The scope expands into application implementation or production operations.

Verification:

- `node command-center/scripts/refresh-dashboard.js`
- `node command-center/scripts/health-check.js`
- `.venv/bin/python scripts/smoke_test.py`
- `git diff --check`
- generated dashboard inspection
- final `git status --short --branch`

### Confirmed Work Block 0B: Target Durability Closeout

Status: done

Included: Task 7.

Excluded: Phase 1 live workflow actions; application code; credentials; ignored data; production, Plaid, Fly, or downstream actions; `AGENTS.md`; `scripts/sync_prod_to_local.sh`; PR or merge; parent-repo changes.

Owner and recommended agent: Codex Desktop.

Stop conditions:

- Staging includes any path outside `PROJECT_STRUCTURE.md` and `command-center/`.
- Refresh, health, smoke, JSON, or whitespace verification no longer passes.
- The branch cannot be pushed without force or unexpected remote changes appear.

Verification:

- inspect the staged path list;
- inspect the staged diff summary;
- commit without modifying existing app files;
- push `codex/runway-os-full-install` without force;
- verify upstream branch and remote commit.

## Phase 1: Operational Reliability Recovery

Status: complete

Goal: restore and prove the automated financial-data pipeline before broader feature work.

- **Task 1: Re-enable the disabled Daily Plaid Sync workflow with Ryan authorization.** Treat this as an external GitHub mutation and preserve the exact before/after state. Status: done; workflow is active.
- **Task 2: Verify one controlled sync execution.** Confirm authentication, all-entity results, downstream Luxe Legacy isolation, and failure reporting without exposing financial row data. Status: done; controlled run `29627530457` completed successfully.
- **Task 3: Establish production and demo health baselines.** Capture safe HTTP health, latest deploy status, workflow state, and restartable checks in Runway OS. Status: done; both roots returned HTTP 200 and both workflows are active.
- **Task 4: Define recurring operational checks.** Decide what belongs in manual re-entry, dashboard status, GitHub Actions, or a later monitored automation. Status: done; work block 1B recommended an independent alert-only Codex monitor.
- **Task 5: Add an independent read-only Daily Plaid Sync monitor.** Create a project-local recurring Codex automation that checks public workflow state and scheduled-run freshness, alerts Ryan on failure, and never enables or dispatches the workflow. Status: done; automation `expense-tracker-daily-plaid-sync-monitor` is active and its read-only test passed.
- **Task 6: Move the daily trigger away from the start of the hour.** Change the schedule from minute zero through a separate source-and-release block because GitHub documents higher delay/drop risk at the start of an hour. Status: done; PR `#83` moved the schedule to `17 9 * * *`, Fly Deploy run `29645346441` passed, and both HTTP health checks returned 200.

### Proposed Work Block 1A: Restore Daily Sync And Operational Baseline

Status: done

Included: Tasks 1-3.

Excluded: Task 4; source-code changes; secrets or financial-row access; Fly deployment; database transfer or cleanup; authentication, CSRF, or encryption changes; documentation recovery; PR, merge, or parent-repo changes. Ryan explicitly added target-branch commit/push durability for Runway OS state and closeout artifacts.

Why these tasks belong together: enabling the disabled schedule, observing one controlled run, and confirming safe production/demo health form one coherent operational-recovery outcome with the same GitHub/runtime verification path. Task 4 depends on what this block reveals and remains separate.

Owner and recommended agent: Codex Desktop. It can coordinate the exact GitHub mutation, preserve before/after state, inspect sanitized run results, update Runway OS, and stop at any live-system anomaly.

Expected live effect: enabling the workflow restores its schedule. One controlled workflow dispatch calls `/plaid/sync-all`, may insert newly available transactions for the configured entities, and may invoke the existing downstream Luxe Legacy bridge for qualifying synced transactions.

Stop conditions:

- GitHub authorization or workflow access is unavailable.
- The workflow definition differs from the reviewed local file or targets an unexpected endpoint.
- The controlled run exposes credential, financial-row, or other sensitive output.
- Any entity sync, downstream bridge, production HTTP check, or workflow job fails.
- Recovery would require source-code, secret, Fly, database, or authentication changes.

Verification:

- record workflow state before and after enable;
- confirm one manual dispatch is accepted;
- wait for the dispatched run to complete;
- record only sanitized per-entity success/failure summary;
- confirm the workflow remains active after the run;
- verify production and demo root HTTP status;
- update Runway OS sources and state;
- refresh and health-check the dashboard;
- report target durability separately.

Result: the remote workflow definition matched the reviewed local file, the workflow changed from `disabled_inactivity` to `active`, controlled workflow-dispatch run `29627530457` completed successfully in about 20 seconds, all job steps passed, the workflow remained active, and production/demo roots returned HTTP 200. Row-level logs were not opened.

### Confirmed Work Block 1B: Define Recurring Sync Safeguards

Status: done; confirmed and completed on 2026-07-18

Included: Task 4.

Excluded: implementation of a monitor or automation; workflow enable/disable/dispatch; additional Plaid sync; application, workflow, secret, Fly, database, authentication, documentation, PR, merge, or parent-repo changes.

Outcome: compare the safe options for detecting or preventing future scheduled-workflow inactivity, recommend one with explicit tradeoffs, and write an implementation-ready follow-up task without changing live state.

Owner and recommended agent: Codex Desktop. The block is project-control research and recommendation work using sanitized GitHub metadata and official platform behavior.

Stop conditions:

- The recommendation requires credential, financial, production, or row-level data access.
- The right mechanism would create a new external service, recurring cost, or write-capable automation without Ryan direction.
- Platform behavior cannot be verified from authoritative documentation or current repo metadata.

Verification:

- authoritative platform behavior cited in the project log;
- at least two viable safeguard options compared;
- one recommended path with implementation and stop boundaries;
- roadmap/state updated without live mutation;
- dashboard refresh and health check pass.

Result: the repository is public and had a more-than-60-day commit gap before GitHub reported `disabled_inactivity`, matching GitHub's documented inactivity rule. Five options were compared. An independent, alert-only Codex monitor is recommended because it can detect disabled state, missing scheduled runs, and non-successful runs without workflow writes or financial-data access. The current top-of-hour cron timing was recorded as a separate hardening task because GitHub documents delay/drop risk at the start of an hour.

### Confirmed Work Block 1C: Independent Daily Sync Monitor

Status: done; confirmed and completed on 2026-07-18

Included: Task 5.

Excluded: Task 6; workflow edits; automatic enable, dispatch, or rerun; Plaid, Fly, application, secret, database, or financial-data access; paid external services; commit, push, PR, merge, or deploy.

Outcome: create one project-local recurring Codex automation that checks public GitHub workflow state and scheduled-run freshness after the expected daily run window, then alerts Ryan only when a defined health condition fails.

Confirmed defaults: run daily at 7:00 AM America/Chicago; query unauthenticated public GitHub REST metadata; consider only `schedule` events; alert when the workflow is not `active`, no scheduled run exists within 36 hours, the latest scheduled run completed unsuccessfully, or it remains incomplete beyond the delay window. A manual dispatch never satisfies freshness. Healthy runs should remain quiet if the automation surface supports quiet success.

Owner and recommended agent: Codex Desktop. The block requires project-local automation setup, exact sensitive-action boundaries, read-only validation, and Runway OS closeout.

Expected live effect: one local recurring automation is created and activated. It reads public GitHub metadata and may notify Ryan; it cannot mutate the workflow or financial system.

Stop conditions:

- The automation requires credentials, private data, or a paid external service.
- It cannot distinguish scheduled runs from manual dispatches.
- Healthy checks would create unavoidable noisy daily alerts.
- It would enable, dispatch, rerun, or edit the workflow.
- A read-only test cannot verify current workflow state and scheduled-run freshness.

Verification:

- inspect the automation definition before activation;
- run one read-only test against current public workflow metadata;
- confirm it reports the workflow as active and identifies the latest scheduled run without opening logs;
- verify no workflow, application, or production state changed;
- refresh and health-check Runway OS.

Suggested later block: 1D for Task 6, using a separate branch and release boundary because a merge to `main` may trigger the existing Fly deployment workflow.

Result: created active project-local automation `expense-tracker-daily-plaid-sync-monitor` on a daily 7:00 AM local schedule. Its prompt uses unauthenticated public GitHub REST metadata, filters to `schedule` events, applies the confirmed 36-hour and three-hour thresholds, and forbids all workflow or financial-system mutation. The read-only test identified active workflow ID `256886458` and successful scheduled run `29640666471` with no alert conditions; manual dispatch `29627530457` remained excluded. The app normalized creation to active immediately, but the stored definition was inspected before its first scheduled execution.

Target durability: the 1C closeout was committed as `b1742cf` and pushed directly to `main`; the follow-up dashboard durability record is also tracked on `main`.

### Confirmed Work Block 1D: Harden Daily Sync Schedule

Status: done; confirmed and completed on 2026-07-18

Included: Task 6.

Excluded: Tasks 1-5 reruns; workflow enable/disable/dispatch/rerun; manual Plaid sync; Phase 2 Tasks 1-4; application, Fly configuration, secret, credential, ignored-data, database, authentication, monitor, or parent-repo changes; pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh`.

Outcome: change the Daily Plaid Sync cron from `0 9 * * *` to `17 9 * * *`, preserving the existing UTC hour and `workflow_dispatch`, then release through `codex/daily-sync-cron-hardening` and a ready PR.

Owner and recommended agent: Codex Desktop. The block is a small sensitive-repo edit coupled to GitHub release handling, production-deploy observation, and Runway OS closeout; no delegation or second opinion is needed.

Expected live effect: merging the ready PR to `main` triggers one production Fly deploy. No manual Plaid sync is authorized. A naturally scheduled run may occur only through the existing schedule.

Stop conditions:

- The diff expands beyond the confirmed workflow and command-center paths.
- Remote divergence, branch protection, or PR state changes the release plan.
- Local verification, the ready PR, Fly Deploy, production HTTP health, dashboard refresh, or health check fails.
- Verification would require secrets, financial data, workflow response-body logs, or manual Plaid execution.
- The `[skip actions]` closeout push unexpectedly starts another Fly deploy.
- Recovery would require a new production or financial-system mutation.

Verification:

- confirm the cron and explanatory comment are the only workflow behavior changes;
- run the synthetic smoke suite and `git diff --check`;
- refresh and health-check Runway OS before release;
- merge the ready PR and verify the default-branch source contains `17 9 * * *`;
- confirm Daily Plaid Sync remains active and the independent monitor is unchanged;
- confirm the resulting Fly Deploy succeeds and production plus demo roots return HTTP 200;
- close Task 6 and Phase 1, refresh and health-check Runway OS, and push the sanitized closeout with `[skip actions]` without starting a second deploy.

Report point: return the exact cron change, branch, PR, commit and deploy evidence, HTTP health, workflow state, protected boundaries, dashboard verification, and the pending natural-run observation handled by the existing monitor.

Result: commit `e34c239` changed only the cron and explanatory comment in the workflow plus the active Runway OS record. Ready PR `#83` was mergeable and merged to `main` as `96af7dc`. Fly Deploy run `29645346441` and every job step completed successfully. Default-branch source contains `17 9 * * *`, Daily Plaid Sync workflow `256886458` remains active, and production plus demo roots returned HTTP 200. No manual sync or sensitive log access occurred. The existing independent monitor owns the first natural minute-17 scheduled-run observation.

Target durability: source and active-state changes are merged on `main`; the verified command-center closeout is published directly to `main` with `[skip actions]` to avoid a second production deployment.

## Phase 2: Project Truth And Documentation Recovery

Status: complete; all four tasks are merged to `main`, deployed, and verified through work blocks 2A, 2A-R, 2B, and 2B-R

Goal: remove contradictory project guidance while retaining useful domain history.

- **Task 1: Rebuild the root README for the current Flask, HTMX, Fly.io, Plaid, and three-entity architecture.** Status: done, merged to `main`, deployed, and verified through work blocks 2A and 2A-R.
- **Task 2: Decide the future of `PROJECT_KNOWLEDGE.md` and `plan.md`.** Archive, replace, or clearly mark their historical status after useful content is migrated. Status: done, merged to `main`, deployed, and verified through work blocks 2B and 2B-R.
- **Task 3: Reconcile `CLAUDE.md` and the untracked `AGENTS.md`.** Define one maintained instruction source and explicitly decide whether `AGENTS.md` becomes tracked. Status: done, merged to `main`, deployed, and verified through work blocks 2B and 2B-R.
- **Task 4: Document deployment, data, and side-effect boundaries without credentials or financial detail.** Status: done, merged to `main`, deployed, and verified through work blocks 2A and 2A-R.

### Work Block 2A — Restore the Root Project Entry Point

Status: done, released, and verified through work block 2A-R

Included: Task 1 and Task 4.

Excluded: Task 2; Task 3; application code; workflows; databases; production, Plaid, Fly, credential, or financial-data access; `PROJECT_KNOWLEDGE.md`; `plan.md`; `CLAUDE.md`; untracked `AGENTS.md`; untracked `scripts/sync_prod_to_local.sh`; parent-repo changes; merge or deployment.

Why this grouping: the root README and sanitized operating boundaries form one trustworthy project entry point, use the same verified repository sources, and share one documentation verification path. Legacy-document disposition and agent-instruction governance remain separate Ryan decisions after the replacement README can be reviewed.

Owner: Codex Desktop.

Recommended agent: Codex manager in the current thread. This small cross-cutting documentation block requires source-of-truth reconciliation, sensitive-project boundaries, local verification, and command-center stewardship. No external worker or second opinion is needed.

Expected files: `README.md`; `PROJECT_STRUCTURE.md` if its README classification needs updating; `command-center/roadmap.md`; `command-center/now.md`; `command-center/decisions.md`; `command-center/state.json`; `command-center/index.html`; and one sanitized closeout log.

Stop conditions:

- a claim cannot be verified without credentials, ignored files, or row-level financial data;
- implementation requires application code, workflow, legacy-document, or pre-existing untracked-file changes;
- a Ryan decision about archiving legacy documents or tracking `AGENTS.md` becomes necessary;
- scope expands beyond Tasks 1 and 4;
- smoke, documentation, dashboard, health, or exact-scope verification fails in a plan-changing way;
- branch or draft-PR publication would include paths outside the confirmed scope.

Verification:

- cross-check README claims against the runtime, Flask factory, Fly configurations, workflows, `.env.example`, requirements, and current repository structure;
- confirm stale Streamlit, no-bank-linking, and two-entity instructions are removed;
- validate referenced paths and commands;
- run `.venv/bin/python scripts/smoke_test.py`;
- run `git diff --check`;
- refresh and health-check Runway OS;
- inspect the generated dashboard and exact staged paths;
- confirm the pushed branch and draft PR contain no application, ignored-data, legacy-document, or untracked-file changes.

Durability: work on `codex/phase-2-root-docs`, commit and push the verified branch, and open a draft PR for Ryan review. Do not merge or deploy.

Report point: return the new README structure, important truth corrections, verification results, branch/commit/draft-PR status, preserved boundaries, and any documentation uncertainty discovered.

Result: replaced the retired Streamlit/manual-import/two-entity README with a tracked-source-verified Flask, HTMX, Plaid, Fly.io, and three-entity entry point. Added local setup, entity/data isolation, application surfaces, imports and synchronization, configuration names without values, deploy mechanics, and explicit side-effect gates. Updated `PROJECT_STRUCTURE.md`, preserved every excluded legacy and untracked file, passed the full synthetic smoke suite plus documentation and Runway OS checks, and opened draft PR #84 from pushed branch `codex/phase-2-root-docs` without merge or deployment.

Target durability: source implementation commit `c249c9b` and the verified 2A closeout are merged to `main` through PR #84 as `6270304`; release verification is recorded by 2A-R.

### Work Block 2A-R — Publish the Root Project Entry Point

Status: done and verified

Included: Task 1 and Task 4 publication only.

Excluded: Task 2; Task 3; content changes beyond the verified PR #84 diff; application code; workflows; monitor changes; databases; Plaid; credentials; row-level financial data; Fly configuration or secrets; legacy or untracked files; parent-repo changes; and any recovery action outside the release plan.

Why this grouping: Ryan explicitly authorized committing and pushing the verified 2A documentation to `main`. The source, review surface, production-deploy observation, HTTP health check, and skip-actions closeout form one release path. The deferred governance tasks do not affect whether the already-verified documentation can be published.

Owner and agent: Codex Desktop in the current thread. This release requires exact-scope GitHub mutation, production-deploy observation, stop judgment, and Runway OS closeout; no delegation or second opinion is needed.

Expected live effect: mark draft PR #84 ready, merge it to `main`, trigger one automatic production Fly deploy, and then publish a command-center-only closeout to `main` with `[skip actions]` so no second deploy starts.

Stop conditions:

- PR #84 is no longer open, clean, or limited to the verified eight documentation and Runway OS paths;
- `main` diverges or branch protection changes the release path;
- synthetic smoke, dashboard, health, or exact-diff verification regresses;
- Fly Deploy fails or production root/health does not return HTTP 200;
- verification would require deployment logs, secrets, financial data, Plaid access, database access, or manual workflow dispatch;
- recovery requires application, authentication, infrastructure, credential, or financial-system mutation;
- the closeout push would unexpectedly trigger a second Fly deployment.

Verification:

- recheck the exact PR file list, draft/open state, and clean mergeability;
- rerun the synthetic smoke suite, Runway OS refresh/health, and `git diff --check` before release;
- mark PR #84 ready and merge it without force;
- identify the resulting `main` merge commit and Fly Deploy run;
- inspect only sanitized workflow, job, and step status without opening logs;
- confirm production `/health` and root return HTTP 200;
- return Task 2 to current, close 2A-R, refresh and health-check Runway OS, and push the closeout with `[skip actions]`.

Report point: return the merge commit, deploy run and result, production HTTP health, final `main`/`origin/main` state, protected boundaries, closeout commit, and remaining Phase 2 decision.

Result: marked PR #84 ready and merged its exact verified eight-file diff to `main` as `6270304`. Automatic Fly Deploy run `29646390675` and every job step passed without opening logs. Production `/health` and the root returned HTTP 200. No manual workflow, Fly, Plaid, database, credential, financial-data, application, authentication, legacy-file, or untracked-file action occurred. GitHub emitted a non-blocking annotation that `actions/checkout@v4` targets deprecated Node 20 and is currently forced to Node 24.

Target durability: PR #84 is merged on `main`; the sanitized release closeout is published directly to `main` with `[skip actions]` so no second Fly deploy starts.

### Work Block 2B — Retire Legacy Guidance And Establish Canonical Agent Instructions

Status: done and verified on draft PR #85; release not authorized

Included: Task 2 and Task 3.

Excluded: Tasks 1 and 4, which are already done; Phase 3 Tasks 1-4; application code; tests; workflows; authentication; databases; Plaid; Fly configuration; credentials; financial data; production operations; untracked `scripts/sync_prod_to_local.sh`; parent-repo changes; merge; and deployment.

Governance decisions accepted by confirmation:

- replace `PROJECT_KNOWLEDGE.md` with a concise historical notice pointing to the current README, command center, and Git history;
- replace `plan.md` with a concise completed-plan notice pointing to the implemented Short-Term Planning surfaces and Git history;
- make a concise tracked `AGENTS.md` the canonical agent instruction source;
- reduce `CLAUDE.md` to a compatibility entry point directing Claude-based tools to `AGENTS.md`, the README, and command-center sources;
- remove duplicated change logs, stale architecture, obsolete live commands, and row-level financial history from active agent context.

Why this grouping: the four documents currently compete for project or agent truth. They share the same source-of-truth analysis, documentation-only change path, exact-scope review, and verification contract. Phase 3 audit work and publication to `main` use different risk and verification paths and remain separate.

Owner and recommended agent: Codex Desktop in the current thread. This sensitive-retrofit governance block requires repo-wide source reconciliation, preservation of user-owned untracked content, command-center stewardship, exact-scope verification, and final intake. No delegation or second opinion is needed.

Expected files: `PROJECT_KNOWLEDGE.md`; `plan.md`; `AGENTS.md`; `CLAUDE.md`; `README.md` and `PROJECT_STRUCTURE.md` only if governance links need correction; `command-center/roadmap.md`; `command-center/now.md`; `command-center/decisions.md`; `command-center/state.json`; `command-center/index.html`; and one sanitized closeout log.

Stop conditions:

- any supposedly obsolete document contains unique current guidance without a safe canonical destination;
- the untracked `AGENTS.md` changes from the inspected copy or contains unique instructions that cannot be safely reconciled;
- a proposed instruction would authorize live or sensitive actions more broadly than current operating rules;
- application, workflow, database, credential, financial-data, production, parent-repo, or excluded-file changes become necessary;
- the diff expands beyond the confirmed documentation and command-center scope;
- smoke, dashboard, health, link, stale-guidance, or exact-scope verification fails in a plan-changing way;
- branch publication includes unexpected paths.

Verification:

- cross-check retained guidance against `README.md`, tracked source, and command-center operating rules;
- confirm the Short-Term Planning plan is substantially implemented before retiring it;
- confirm `AGENTS.md` contains no stale model identifiers, obsolete architecture, destructive operational recipes, or duplicated financial history;
- scan active documentation for contradictory authority and stale Streamlit or manual-deploy guidance;
- validate referenced paths and commands;
- run `.venv/bin/python scripts/smoke_test.py`;
- run `git diff --check`;
- refresh and health-check Runway OS;
- inspect the generated dashboard and exact diff and staged paths;
- confirm `scripts/sync_prod_to_local.sh` and all application files remain untouched.

Durability: work on `codex/phase-2-document-governance`, commit and push the verified branch, and open a draft PR. Do not merge or deploy.

Report point: return the exact governance outcomes, useful content retained or migrated, stale or risky material removed from active context, verification results, branch and commit, draft PR, preserved boundaries, and the proposed 2B-R release gate.

Result: added a concise tracked `AGENTS.md` as the canonical agent and contributor instruction source; reduced `CLAUDE.md` to a compatibility entry point; replaced `PROJECT_KNOWLEDGE.md` and `plan.md` with concise historical notices backed by Git-history recovery commands; updated the README, project structure, and Runway OS authority map; and parked the legacy Short-Term Planning plan's missing dedicated smoke and demo-goal coverage for a fresh Phase 3 audit. The synthetic smoke suite, documentation scans, path and Git-object checks, exact-scope checks, dashboard refresh, health check, and whitespace checks passed. Source commit `912c9bb` is pushed on `origin/codex/phase-2-document-governance`, and draft PR #85 is open without merge or deployment.

Target durability: the verified implementation is merged to `main` through PR #85 as `216a992`; release verification is recorded by 2B-R.

### Work Block 2B-R — Publish Canonical Project Guidance

Status: done and verified

Included: Task 2 and Task 3 publication only.

Excluded: content changes beyond the verified PR #85 diff; application code; workflows or monitor changes; authentication; databases; Plaid; Fly configuration or secrets; credentials; financial data; parent-repo changes; pre-existing untracked `scripts/sync_prod_to_local.sh`; manual workflow dispatch; and any recovery action outside this release plan.

Why this grouping: Ryan explicitly authorized committing and pushing the verified 2B work to `main`. The exact PR review, ready transition, merge, single automatic Fly deploy, sanitized health verification, and skip-actions closeout form one bounded release path.

Owner and agent: Codex Desktop in the current thread. The block requires exact-scope GitHub mutation, production-deploy observation, stop judgment, and Runway OS closeout. No delegation or second opinion is needed.

Expected live effect: mark draft PR #85 ready, merge it to `main`, trigger one automatic production Fly deploy, then publish a command-center-only closeout directly to `main` with `[skip actions]` so no second deploy starts.

Stop conditions:

- PR #85 is no longer open, clean, mergeable, or limited to the verified thirteen documentation and Runway OS paths;
- `main` diverges or branch protection changes the release path;
- synthetic smoke, dashboard, health, or exact-diff verification regresses;
- Fly Deploy fails or production root or `/health` does not return HTTP 200;
- verification would require deployment logs, secrets, credentials, financial data, Plaid, databases, or manual workflow dispatch;
- recovery requires application, authentication, infrastructure, credential, or financial-system mutation;
- the closeout push would unexpectedly trigger a second Fly deployment.

Verification:

- recheck the exact PR file list, draft/open state, clean mergeability, and branch/base identity;
- rerun the synthetic smoke suite, Runway OS refresh and health, and `git diff --check` before release;
- mark PR #85 ready and merge it without force;
- identify the resulting `main` merge commit and automatic Fly Deploy run;
- inspect only sanitized workflow, job, and step status without opening logs;
- confirm production `/health` and root return HTTP 200;
- close Tasks 2 and 3 plus Phase 2, activate Phase 3 for just-in-time audit planning, refresh and health-check Runway OS, and push the command-center-only closeout with `[skip actions]`.

Report point: return the merge commit, deploy run and result, production HTTP health, final `main` and `origin/main` state, protected boundaries, closeout commit, and the Phase 3 planning boundary.

Result: marked PR #85 ready and merged its verified thirteen-path documentation and Runway OS diff to `main` as `216a992`. Automatic Fly Deploy run `29647452643` and every job step passed without opening logs. Production root and `/health` returned HTTP 200. No manual workflow, Fly, Plaid, database, credential, financial-data, application, authentication, parent-repo, or pre-existing untracked-file action occurred.

Target durability: PR #85 is merged on `main`; the sanitized 2B-R closeout is published directly to `main` with `[skip actions]` so no second Fly deploy starts.

## Phase 3: Functional Audit And Prioritization

Status: complete; Tasks 1-8 and work blocks 3A-3L are done

Goal: determine what “working properly” means across the live product, then rank evidence-backed defects and gaps.

- **Task 1: Audit the transaction foundation and three-entity isolation with synthetic data.** Status: done through work block 3A. The audit passed initialization, isolation, debit-sign, edit, split, and effective-reporting probes; it found a high-severity identity collision risk and a medium tracked-regression-coverage gap without implementing fixes.
- **Task 2: Audit statement and vendor-order import, matching, and categorization workflows.** Status: done through work block 3B. The audit passed 60 synthetic checks and found three high-risk correctness defects in vendor-payment schema compatibility, vendor line-item persistence, and category-domain enforcement, plus a medium coverage gap and low `Undo` ambiguity.
- **Task 3: Audit dashboard, reporting, exports, subscriptions, and cash-flow behavior.** Status: done through work block 3C. The tracked smoke suite passed; 297 of 306 ephemeral assertions passed, and the remaining nine controlled errors reproduced one medium Recurring Charges report SQL defect at three layers in all three entities. A medium tracked-coverage gap was also recorded without implementation.
- **Task 4A: Audit long-term planning projections and cross-entity visibility.** Status: done through work block 3D. Positive projections, linked balances, CRUD, summaries, and Personal/BFM visibility passed; negative depreciation and LL direct-route denial defects were recorded without repair.
- **Task 4B: Audit short-term goals, snapshots, budgets, actions, and payoff planning.** Status: done through work block 3D. CRUD, entity-local choices, budgets, effective splits, averages, per-payroll math, actions, and direct payoff engines passed; APR-blind locked plans, snapshot-note loss, LL direct-route denial, and tracked-coverage gaps were recorded without repair.
- **Task 4C: Audit weekly and waterfall derived workflows.** Status: done through work block 3E. Current-period calculations, effective spending, valid target modes, empty states, intended Personal/BFM sharing, LL denial, and read-only preservation passed; six functional defects and one tracked-coverage gap were recorded without repair.
- **Task 4D: Audit payroll roster, Phoenix/CyberPayroll import, and role spending.** Status: done through work block 3F. Parser, roster lifecycle, explicit import persistence, re-import deduplication, role-spending totals, delete cascades, storage isolation, and successful-save cleanup passed; three high payroll-integrity/boundary defects, three medium validation/retention/import defects, and one medium tracked-coverage gap were recorded without repair.
- **Task 5A: Audit Plaid connection, account, balance, and liability boundaries.** Status: done through work block 3G. Encryption, entity-local exchange, account toggle/rename/disconnect, normal balance refresh, and manual-row preservation passed; overbroad manual cleanup, unsafe disabled/partial reconciliation, global freshness, liability starvation, and tracked-coverage defects were recorded without repair.
- **Task 5B: Audit incremental Plaid transaction-sync semantics.** Status: done through work block 3G. Pagination, normal all-entity add/modify/remove, sign, enabled-account filtering, cursor success, categorization, exact re-delivery, and isolation passed; Plaid identity collision, swallowed persistence failure with cursor advance, false modified counts, corrupt-token fanout, and tracked-coverage defects were recorded without repair.
- **Task 5C: Audit scheduled and public background-sync entry points.** Status: done through work block 3H. Method/bearer/CSRF separation, normal all-entity iteration, same-process lock release/contention, public reachability/throttle, Personal/LL scope, cursor success, item failure containment, and cleanup passed; seven functional/boundary defects plus one tracked-coverage gap were recorded without repair.
- **Task 5D: Audit the Luxe Legacy downstream-mirror boundary.** Status: done through work block 3I. Configuration/no-op, LL-only scheduled/public invocation and storage, request/auth/payload/timeout shape, standard exclusions, repeat stability, failure isolation, entity non-mutation, and cleanup passed; Owner Draw eligibility, empty Plaid IDs, duplicate/implicit conflict keys, tracked coverage, and remote-idempotency proof were recorded without repair or live access.
- **Task 6: Audit PWA, responsive navigation, public dashboard, and authentication boundaries.** Status: done through work block 3J. Manifest/installability, icons, desktop/tablet/phone layout, basic mobile drawer state, CSRF, exempt routes, security headers, and branded offline fallback passed; seven finding clusters were recorded across the main authentication boundary, cross-entity PWA caching, public financial-detail exposure, auth-mode coherence, mobile accessibility, browser/session hardening, and tracked coverage.
- **Task 7: Consolidate audit findings into severity-ranked issues.** Status: done through work block 3K. The 55 Phase 3-derived entries now have stable IDs, explicit status, severity, confidence, affected boundaries, sanitized reproductions, observed-versus-expected behavior, impact, acceptance-check ownership, evidence, and dependency tags in one verified catalog.
- **Task 8: Confirm the repair order and bounded Phase 4 implementation work blocks with Ryan.** Status: done through work block 3L. Ryan confirmed 4C first, the revised early-boundary and pre-split Plaid sequence, authenticated `/k/`, paired coverage, and the deferred payroll, cookie/CSP, and downstream-idempotency defaults.

### Confirmed Work Block 3A: Synthetic Transaction Foundation Audit

Status: done; confirmed and completed on 2026-07-18

Included: Task 1.

Excluded: Tasks 2-8; product fixes; tracked test expansion; real databases, uploads, credentials, or row-level financial data; production or demo access; Plaid, workflow, Fly, or downstream actions; authentication, encryption, CSRF, credential, or public-route changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether the tracked transaction foundation behaves consistently across Personal, BFM, and Luxe Legacy using source inspection, the existing synthetic smoke suite, and ephemeral probes against temporary databases. Classify each audited behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit block couples source inspection, synthetic verification, finding classification, and command-center stewardship; no external worker or second opinion is needed.

Expected surfaces: read `core/db.py`, `core/imports.py`, `core/reporting.py`, `web/__init__.py`, transaction routes/templates, tracked fixtures, and `scripts/smoke_test.py`; write a sanitized 3A audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application or tracked test file should change.

Stop conditions:

- Verification would require real databases, uploads, financial rows, credentials, production/demo access, Plaid, or another live action.
- A finding requires a product fix or tracked regression test; record it and stop short of implementation.
- Entity isolation appears violated or ambiguous, or a security/authentication/destructive-data condition appears.
- Scope expands beyond Task 1 or a verification failure changes the audit plan.
- The command center cannot be refreshed or health check cannot pass.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- ephemeral temporary-`DATA_DIR` checks for all three entities, deterministic transaction IDs, re-import deduplication, negative-debit convention, edit/split behavior, effective-reporting split replacement, and cross-entity denial/isolation
- `git diff --check`
- Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: after 3A completed locally, Ryan separately authorized publishing the exact command-center closeout directly to `main` with `[skip actions]`; no PR, merge, or deploy is part of that durability step.

Report point: return a sanitized pass/gap/unverified matrix, ranked findings with acceptance checks, exact synthetic checks, preserved boundaries, and a recommendation for work block 3B covering Task 2.

Result: the existing smoke suite and the ephemeral all-entity probe passed initialization, schema alignment, isolation, signed-cents, edit, split-validation, and effective-reporting checks. One high-severity financial-data completeness defect was reproduced: identity hashes only date, amount, and description, so otherwise identical rows from different accounts collide and one is silently skipped. Edit/split/reporting behavior passed but lacks tracked regression coverage, recorded as a medium risk. Plaid uses the same identity helper in source, but its impact remains an unverified Task 5 boundary. No repair, tracked test, live access, protected-data read, or durability action occurred.

### Confirmed Work Block 3B: Synthetic Import-to-Categorization Audit

Status: done; confirmed and completed on 2026-07-18

Included: Task 2.

Excluded: Task 1 and Tasks 3-8; product fixes; tracked fixture or regression-test expansion; real databases, statements, uploads, credentials, or row-level financial data; production or demo access; Plaid or vendor-account link, sync, or disconnect actions; workflows, Fly, downstream writes, authentication or security changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether the complete synthetic path from CSV/PDF statements and Amazon/Henry Schein orders through confirmation, matching, aliases, suggestions, and category/subcategory persistence behaves consistently across Personal, BFM, and Luxe Legacy. Classify each audited behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples source inspection, generated fixture design, ephemeral all-entity verification, finding classification, and command-center stewardship; no delegation or second opinion is needed.

Expected surfaces: read `core/imports.py`, `core/amazon.py`, `core/henryschein.py`, `core/vendor_matching.py`, `core/categorize.py`, database schema, categories, tracked fixtures, smoke coverage, and upload/data-source/match/categorization routes and templates. Write a sanitized 3B audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, fixture, or tracked test file should change.

Stop conditions:

- Verification would require real databases, statements, uploads, financial rows, credentials, production/demo access, Plaid, a live vendor connection, or another live action.
- Entity isolation or security behavior appears violated or unsafe.
- A finding requires product repair, migration design, or tracked regression coverage; record it without implementing it.
- The known transaction-identity defect prevents a trustworthy Task 2 conclusion.
- Scope expands beyond Task 2, a verification failure changes the audit plan, or the command center cannot be refreshed and health-checked.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- generated temporary CSV, PDF, and XLSX parser inputs plus route/file-flow probes against an ephemeral `DATA_DIR`
- all-entity checks for import profiles, preview/confirm/duplicate/undo boundaries, Amazon and Henry Schein persistence, exact/review/unmatched matching, aliases, suggestions, category/subcategory consistency, and cross-entity isolation
- temporary-file cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: after 3B completed locally, Ryan separately authorized publishing the exact seven-path command-center closeout directly to `main` with `[skip actions]`; no PR, merge, or production deployment is part of that durability step.

Report point: return a sanitized pass/gap/unverified matrix, ranked findings with acceptance checks, exact synthetic checks, preserved boundaries, and a recommendation for work block 3C covering Task 3.

Result: the tracked smoke suite and 60 ephemeral checks passed the CSV/PDF, upload confirmation, Amazon/Henry parsing and deduplication, order-matching, alias, cleanup, and three-entity-isolation behaviors. Vendor-payment matching failed against every fresh migration-built entity because it references nonexistent `transactions.matched_order_id`; normal vendor imports persisted no line items for auto-split; and category inference/acceptance wrote undefined or nondeterministic values outside `categories.md`. A medium tracked-coverage gap and low status-only `Undo` ambiguity were also recorded. No repair, product/test change, protected-data access, live action, or GitHub durability occurred.

### Confirmed Work Block 3C: Synthetic Financial Read-Model Audit

Status: done; confirmed and completed on 2026-07-18

Included: Task 3.

Excluded: Tasks 1-2 and 4-8; product fixes; tracked fixture or regression-test expansion; real databases, exports, balances, credentials, or row-level financial data; production or demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication or security changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether dashboard metrics, report views and exports, subscription detection, and cash-flow projections produce a consistent financial read from the same deterministic synthetic transaction and account timeline across Personal, BFM, and Luxe Legacy. Classify each audited behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Why this grouping: every included surface consumes the same dates, accounts, entity-specific exclusions, split semantics, recurring-charge patterns, and balance inputs. One synthetic read model provides a coherent reconciliation path. Task 4 changes to planning, weekly, waterfall, and payroll state and remains a separate work block.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples source inspection, temporary-database probes, cross-surface reconciliation, finding classification, and command-center stewardship; no delegation or second opinion is needed.

Expected surfaces: read `core/reporting.py`, reporting-related database migrations, `web/routes/dashboard.py`, `web/routes/reports.py`, `web/routes/subscriptions.py`, `web/routes/cashflow.py`, `web/export_helpers.py`, related templates, and `scripts/smoke_test.py`. Write a sanitized 3C audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, fixture, or tracked test file should change.

Stop conditions:

- Verification would require real financial data, credentials, production/demo access, Plaid, OpenRouter, or another external API call.
- Entity isolation, authentication, or destructive-data behavior appears unsafe.
- A finding requires implementation, migration design, or tracked regression coverage; record it without implementing it.
- An earlier defect prevents a trustworthy Task 3 conclusion.
- Scope expands beyond Task 3, verification changes the audit plan, or command-center checks fail.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- deterministic multi-month temporary data across all three entities covering ordinary spending, entity-specific exclusions, income, uncategorized rows, split replacement, repeated and irregular merchants, multiple accounts, balances, liabilities, and manual recurring charges
- dashboard, HTMX, report-builder, CSV, PDF, QBO, subscription, and cash-flow probes reconciled to expected totals, dates, filenames, empty states, and entity isolation
- temporary-data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: published directly to `main` under Ryan's separate post-block authorization with `[skip actions]`; no PR, merge, or deployment is part of this command-center-only closeout.

Report point: return a sanitized cross-surface pass, defect, gap, and unverified matrix; ranked findings with acceptance checks; exact synthetic checks; preserved boundaries; and whether work block 3D should proceed with Task 4 as currently sequenced.

Result: the tracked smoke suite passed, and the final ephemeral probe ran 306 checks with 297 passes, zero assertion failures, and nine controlled reproductions of one defect across direct query, prepared-report, and rendered-route layers in Personal, BFM, and Luxe Legacy. Dashboard reconciliation, effective split replacement, exclusions, account/date filters, every non-recurring report view, CSV/PDF/QBO exports, subscription lifecycle, cash-flow balances and projections, intended Personal/BFM visibility, LL isolation, and cleanup passed. The Recurring Charges report cannot run because its SQL contains a literal uninterpolated exclusion helper; the broader Task 3 paths also lack tracked regression coverage. No repair, product/test change, protected-data access, external call, live action, or GitHub durability occurred.

### Confirmed Work Block 3D: Synthetic Planning Foundations Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Tasks 4A and 4B.

Excluded: Tasks 4C-4D and 5-8; product repairs or migrations; tracked test, fixture, or demo-seed expansion; real databases, financial rows, payroll/HR data, credentials, production or demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication or security changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether long-term projections and cross-entity visibility plus short-term goals, snapshots, budgets, actions, and payoff planning behave consistently against deterministic synthetic account and transaction state. Classify behavior as pass, defect, regression-coverage gap, superseded historical expectation, or unverified boundary without implementing repairs.

Why this grouping: Tasks 4A-4B share the planning schema, account balances, budget state, entity rules, route family, and temporary-database verification path. Task 4C consumes these outputs through a separate calendar and cross-surface reconciliation path; Task 4D introduces a separate XLSX, temporary-upload, employee-lifecycle, and payroll/HR boundary.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples source inspection, deterministic temporary state, cross-entity verification, historical-expectation classification, command-center stewardship, and final intake; no delegation or second opinion is needed.

Expected surfaces: read `core/db.py`, `web/routes/planning.py`, `web/routes/short_term_planning.py`, relevant `web/routes/ai.py` context code without making an API call, related templates, `scripts/seed_demo_data.py`, `scripts/smoke_test.py`, and the parked planning issue. Write a sanitized 3D audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, fixture, tracked test, or demo-seed file should change.

Stop conditions:

- Verification would require real financial or payroll data, credentials, production/demo access, Plaid, OpenRouter, or another external action.
- Entity isolation, authentication, destructive behavior, or sensitive-data handling appears unsafe.
- A finding requires a product repair, migration, tracked test, or demo-data change; record it without implementation.
- An earlier defect prevents a trustworthy planning conclusion.
- Scope expands into Tasks 4C-4D or 5-8, verification changes the audit plan, or command-center checks fail.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- deterministic temporary-`DATA_DIR` checks for long-term settings, asset/liability CRUD and projections, cash-flow-linked balances, Personal/BFM shared visibility, and Luxe Legacy denial
- all-entity short-term checks for goal CRUD and status, automatic/manual snapshots, plan locking, payoff strategies and schedules, budgets and subcategories, per-payroll computation, action items, date and empty states, entity isolation, and the parked legacy expectations
- temporary-data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: published directly to `main` under Ryan's separate post-block authorization with `[skip actions]`; no PR, merge, or deployment is part of this command-center-only closeout.

Report point: return a sanitized pass, defect, gap, superseded, and unverified matrix; a verdict on the parked legacy expectations; ranked findings with acceptance checks; exact synthetic checks; preserved boundaries; and whether work block 3E should proceed with Task 4C.

Result: the tracked synthetic smoke suite passed. The final ephemeral 3D probe ran 58 checks with 48 passes, zero runtime errors, and ten controlled assertion failures that cluster into four defects: locked avalanche schedules ignore stored APRs, LL denial is absent from direct planning routes, automatic same-day snapshots erase manual review notes, and negative asset appreciation is treated as zero growth. Goal CRUD/status/delete, budgets and subcategories, effective split replacement, three-month averages, per-payroll math, actions, direct payoff engines, positive projections, linked balances, summaries, and Personal/BFM visibility passed. The legacy goal/snapshot/budget/payoff/isolation expectations remain valid; short-term cross-entity linking and custom allocation are superseded. Planning paths still lack tracked coverage, and demo goals/snapshots remain unseeded. No repair, tracked product/test/demo change, protected-data access, external call, live action, or GitHub durability occurred.

### Confirmed Work Block 3E: Synthetic Weekly and Waterfall Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Task 4C.

Excluded: completed Tasks 1-3 and 4A-4B; Tasks 4D and 5-8; product repairs or migrations; tracked test, fixture, or demo-seed expansion; real financial or payroll data, credentials, production or demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication or security changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether weekly pace, bills, burn rate, warnings, and paydown tracking plus the BFM-to-Personal actual and target waterfall produce internally consistent results from the same deterministic synthetic budgets, effective transactions, balances, recurring-charge state, paydown goal, and payroll schedule. Classify behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Why this grouping: Weekly and Waterfall are coupled derived consumers of the same validated Task 4A-4B planning inputs and Task 3 financial read model. One deterministic multi-month state can reconcile their dates, budget sections, spending totals, balances, paydown pace, and intended Personal/BFM/LL boundaries. Task 4D introduces generated XLSX, temporary-upload, employee-lifecycle, and payroll/HR verification and remains separate.

Owner and recommended agent: Codex Desktop in the current task. This sensitive-retrofit audit couples source inspection, synthetic cross-entity verification, finding classification, command-center stewardship, and final intake; no delegation or second opinion is needed.

Expected surfaces: read `web/routes/weekly.py`, `web/routes/waterfall.py`, relevant short-term-planning and cash-flow helpers, `core/reporting.py`, `core/db.py`, related templates, `scripts/seed_demo_data.py`, and `scripts/smoke_test.py`. Write a sanitized 3E audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, fixture, tracked test, or demo-seed file should change.

Stop conditions:

- Verification would require protected financial or payroll data, credentials, production/demo access, Plaid, OpenRouter, or another external action.
- Entity isolation, authentication, destructive behavior, or sensitive-data handling appears unsafe.
- A finding requires a product repair, migration, tracked test, fixture, or demo-data change; record it without implementation.
- An earlier defect prevents a trustworthy Task 4C conclusion rather than being isolated.
- Scope expands into Task 4D or Tasks 5-8, verification changes the plan, or command-center checks fail.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- deterministic temporary-`DATA_DIR` checks for ISO-week navigation, cross-month/year dates, budget and category pace, effective split spending, exclusions, burn rate, warnings, action/recurring/card/payroll bills, balances, paydown-goal persistence, and empty states
- multi-month BFM-to-Personal checks for actual income/expense/surplus, budget-section grouping, revenue and take-home target modes, tax handling, historical trend, payoff estimate, invalid inputs, rendered routes, intended cross-entity visibility, Luxe Legacy denial, and absence of cross-entity mutation
- temporary-data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: published directly to `main` under Ryan's separate post-block authorization with `[skip actions]`; no PR, merge, or deployment is part of this command-center-only closeout.

Report point: return a sanitized weekly/waterfall pass, defect, gap, and unverified matrix; ranked findings with acceptance checks; exact synthetic checks; preserved boundaries; tracked-coverage assessment; and whether work block 3F should proceed with Task 4D.

Result: the tracked synthetic smoke suite passed. The final 58-check primary audit, corrected for three harness expectations and supported by a focused ten-check confirmation probe, found six functional defect clusters and one medium tracked-coverage gap without unexpected runtime errors. Current-period effective spending, exclusions, valid pace and target math, bill-source assembly, paydown pace, BFM payroll date, empty states, actual and target waterfall reconciliation, historical series, intended Personal/BFM sharing, LL denial, read-only preservation, and temporary cleanup passed. Weekly historical navigation mixes selected and current dates; card bills use full balances rather than scheduled payments; Waterfall excludes deficit months from its payoff average; invalid paydown dates persist and break Weekly; sub-month payoff estimates can show zero months; and tax fallback/display plus non-finite input handling are inconsistent. No repair, tracked product/test/demo change, protected-data access, external call, live action, or GitHub durability occurred.

### Confirmed Work Block 3F: Synthetic Payroll Lifecycle Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Task 4D.

Excluded: completed Tasks 1-3 and 4A-4C; Tasks 5-8; all repairs from work blocks 3A-3E; product repairs or migrations; tracked test, fixture, or demo-seed changes; real payroll, HR, financial, upload, or credential data; production or demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication or security changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether employee roster and pay-history behavior, Phoenix/CyberPayroll parsing and preview/save flow, re-import deduplication, temporary-payload lifecycle, role mapping, pay-period aggregation, and the intended BFM-only access boundary behave consistently against generated XLSX files and temporary synthetic entity databases. Classify behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Why this grouping: employee lifecycle, payroll parsing, import persistence, duplicate handling, and role-spending output share the same payroll schema, generated-XLSX input, temporary-payload lifecycle, entity boundary, and synthetic verification path. Task 5 introduces mocked integration and credential boundaries, Task 6 introduces authentication and public-route risk, and Task 7 depends on the remaining audit slices.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples source inspection, generated fixtures, temporary databases, cross-entity verification, finding classification, command-center stewardship, and final intake; no delegation or second opinion is needed.

Expected surfaces: read `core/payroll_parser.py`, payroll migrations in `core/db.py`, `web/routes/payroll.py`, `web/templates/payroll.html`, entity and navigation rules, `scripts/smoke_test.py`, `README.md`, and `categories.md`. Write a sanitized 3F audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, fixture, tracked-test, demo, workflow, or deployment file should change.

Stop conditions:

- Verification would require real payroll, HR, financial, credential, upload, production, or demo data.
- An entity-isolation, authentication, destructive-data, or sensitive-payload condition appears unsafe.
- A finding requires repair, migration, or tracked regression coverage; record it without implementation.
- The maintained BFM-only product boundary becomes genuinely ambiguous rather than merely violated by current behavior.
- Scope expands beyond Task 4D, verification changes the audit plan, or Runway OS cannot refresh and pass health checks.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- generated Phoenix-style XLSX parser and route probes covering dates, sections, job codes, matched and unmatched employees, malformed inputs, preview, save, duplicate import, and temporary-payload lifecycle
- temporary all-entity database checks for employee CRUD, status, pay-change history, detail, delete cascades, paycheck history, pay-period selection, role totals, employee totals, percentages, HTMX output, BFM access, Personal and Luxe Legacy denial, and absence of cross-entity mutation
- tracked regression-coverage assessment, temporary-data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: published directly to `main` under Ryan's separate post-block authorization with `[skip actions]`; no PR, merge, or deployment is part of this command-center-only closeout.

Report point: return a sanitized payroll pass, defect, gap, and unverified matrix; ranked findings with acceptance checks; exact synthetic verification performed; temporary-payload cleanup result; protected boundaries; tracked-coverage assessment; and whether Task 5 is ready for just-in-time work-block planning.

Result: the tracked synthetic smoke suite passed. Across a 40-check primary payroll probe and focused seven-check confirmation probe, 36 of 47 assertions passed and eleven controlled failures collapsed into six defect clusters plus one tracked-coverage gap. Multi-section parsing, date and amount normalization, known/unknown role mapping, parser deduplication, headerless-file handling, BFM roster CRUD and pay history, delete cascades, explicit import persistence, re-import row stability, role and employee totals, successful-save cleanup, three-entity storage isolation, and complete audit cleanup passed. Personal and Luxe Legacy direct routes violated the maintained BFM-only boundary; the default preview duplicated an exact existing employee; peer averages mixed hourly and salary units; employee direct inputs were weakly normalized; cancel retained its parsed payload; and malformed XLSX bytes raised instead of returning a controlled error. No repair, tracked product/test/demo change, protected-data access, external call, live action, or GitHub durability occurred.

### Confirmed Work Block 3G: Mocked Primary Plaid Boundary Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Tasks 5A-5B.

Excluded: Tasks 5C-5D and 6-8; all repairs from work blocks 3A-3F; product repairs or migrations; tracked test, fixture, or demo-seed changes; real databases, balances, transactions, financial rows, credentials, or Plaid tokens; production or demo access; network calls; live Plaid, workflow, Fly, or downstream actions; authentication, CSRF, encryption, credential, or public-route changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether Plaid connection and account state, cached balances and liabilities, and incremental transaction ingestion preserve token, entity, account, cursor, deduplication, sign, categorization, removal, and failure boundaries against mocked SDK responses and temporary all-entity databases. Classify behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Why this grouping: connection/account state and incremental ingestion share `core/plaid_client.py`, `web/routes/plaid.py`, the Plaid schema, encrypted item storage, temporary entity databases, and one deterministic mocked verification harness. Task 5C adds protected/public entry-point and concurrency behavior; Task 5D adds a separate downstream HTTP/write boundary. Both depend on the primary Plaid result and remain separate.

Owner and recommended agent: Codex Desktop in the current task. This sensitive-retrofit audit couples source inspection, mocked integration behavior, temporary three-entity state, finding classification, command-center stewardship, and final intake; no delegation or second opinion is needed.

Expected surfaces: read `core/plaid_client.py`, `core/crypto.py`, Plaid migrations in `core/db.py`, `web/routes/plaid.py`, Plaid account and liability helpers in `web/routes/cashflow.py`, relevant app initialization and templates, and `scripts/smoke_test.py`. Write a sanitized 3G audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, fixture, tracked-test, workflow, or deployment file should change.

Stop conditions:

- Verification would require real credentials, Plaid tokens, databases, balances, transactions, financial rows, production/demo access, a network call, or another live action.
- Entity isolation, token handling, authentication, destructive behavior, or sensitive-data handling appears unsafe.
- A finding requires repair, migration, or tracked regression coverage; record it without implementation.
- The known Task 1 transaction-identity defect prevents a trustworthy Tasks 5A-5B conclusion rather than being isolated.
- Scope expands into Tasks 5C-5D or 6-8, verification changes the audit plan, or Runway OS cannot refresh and pass health checks.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- mocked connection/exchange, encrypted persistence, account enable/rename/disconnect, manual-account preservation, balance-cache, and liability checks against temporary all-entity databases
- deterministic mocked added, modified, removed, paginated, duplicate, disabled-account, cursor, sign, categorization, failure-isolation, and transaction-identity checks across Personal, BFM, and Luxe Legacy
- no-outbound-call confirmation, tracked regression-coverage assessment, temporary-data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: Ryan separately authorized publishing the exact seven-path 3G command-center closeout directly to `main` with `[skip actions]`. This commit is the durability record; no PR, merge, deployment, live Plaid action, workflow action, or downstream write is included.

Report point: return a sanitized Tasks 5A-5B pass, defect, gap, and unverified matrix; ranked findings with acceptance checks; exact mocked verification; protected boundaries; temporary cleanup; tracked-coverage assessment; and Task 5C readiness.

Result: the tracked smoke suite passed. A deterministic 56-check mocked probe produced 44 passes, twelve controlled failures, and zero unexpected failures; a confirmation pass reproduced the same failures and cleanup. Encryption, configuration rejection, pagination, entity-local exchange, account toggle/rename/disconnect, normal balance refresh, manual-row preservation, all-entity add/modify/remove, sign, enabled-account filtering, successful cursor movement, review categorization, exact re-delivery, and isolation passed. Eight defect clusters were recorded: first-word link cleanup can delete unrelated manual balances; balance reconciliation can retain disabled-only rows or delete failed-item rows; entity-wide maximum freshness can hide stale accounts; normal balance refresh starves liability refresh; distinct Plaid IDs can collide; persistence errors can be swallowed while the cursor advances; absent modified rows are reported successful; and one corrupt token aborts healthy sibling items. Primary Plaid paths also lack tracked regression coverage. No product/test change, protected-data access, network call, live action, or GitHub durability occurred.

### Confirmed Work Block 3H: Mocked Sync Entry-Point Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Task 5C.

Excluded: Task 5D and Tasks 6-8; all repairs from work blocks 3A-3G; product repairs or migrations; tracked test, fixture, workflow, or demo-seed changes; real databases, balances, transactions, financial rows, credentials, or Plaid tokens; production or demo access; network calls; live Plaid, workflow, Fly, or downstream actions; authentication, CSRF, encryption, credential, or public-route changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether `/plaid/sync-all` and the public `/k/` background-sync path preserve their authorization, CSRF, method, entity-selection, throttling, locking, concurrency, failure-containment, cursor, and response/reporting boundaries with mocked internals only. Classify behavior as pass, defect, regression-coverage gap, or unverified boundary without implementing repairs.

Why this grouping: both entry points orchestrate background Plaid synchronization and share one mocked verification model around request boundaries, locks, entity selection, failure containment, and observable results. Task 5D introduces a separate mocked outbound-HTTP contract, and Task 6 requires broader public-route and authentication-policy judgment.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples local source inspection, mocked request and concurrency behavior, protected-data boundaries, finding classification, command-center stewardship, and final intake; no delegation or second opinion is needed.

Expected surfaces: read `web/routes/plaid.py`, `web/routes/kristine.py`, `web/__init__.py`, `.github/workflows/daily-plaid-sync.yml`, relevant database helpers, and `scripts/smoke_test.py`. Use an untracked disposable probe with fake environment values, temporary synthetic databases, mocked synchronization/thread dependencies, and outbound-socket denial. Write a sanitized 3H audit log and update `command-center/issues.md` only when findings require it; close out through Runway OS sources, state, and dashboard. No application, workflow, fixture, or tracked-test file should change.

Stop conditions:

- Verification would require protected data, real credentials or tokens, an external call, production/demo access, or another live action.
- Authentication, concurrency, entity-isolation, destructive-data, or sensitive-output behavior appears unsafe to probe beyond the local mocked boundary.
- A finding requires repair, migration, or tracked regression coverage; record it without implementation.
- Scope expands into Task 5D's downstream request contract or Task 6's broader authentication/public-dashboard policy.
- Verification changes the audit plan materially, or Runway OS cannot refresh and pass health checks.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- deterministic mocked `/plaid/sync-all` checks for method, missing/wrong/correct bearer, CSRF exemption, all-entity iteration, lock contention and release, partial failure, response truthfulness, and secret-safe output
- deterministic mocked `/k/` checks for public trigger, interval throttle, daemon-thread launch, Personal/Luxe Legacy scope, item selection, per-item failure handling, cursor/results, and interaction with the scheduled-sync lock
- outbound-socket denial, repeat confirmation pass, tracked regression-coverage assessment, temporary-data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: Ryan subsequently authorized and published the exact seven-path 3H command-center closeout directly to `main` as commit `c3130ea` with `[skip actions]`. No PR, merge, deployment, live integration action, or workflow action occurred.

Report point: return a sanitized Task 5C pass, defect, gap, and unverified matrix; ranked findings with acceptance checks; exact mocked verification; protected boundaries; temporary cleanup; tracked-coverage assessment; and Task 5D readiness.

Result: the tracked smoke suite passed. A deterministic 32-check mocked probe produced 22 passes, ten controlled failures, and zero unexpected failures; a confirmation pass reproduced the same results and complete cleanup. Method/bearer rejection, secret-safe responses, CSRF separation, normal all-entity iteration, scheduled same-process lock behavior, public reachability and one-process throttle, Personal/LL scope, normal cursor movement, per-item failure containment, and lock release passed. Seven defect clusters were recorded: scheduled nested errors return HTTP 200 and top-level success; scheduled/public coordination is separate and process-local under two Gunicorn workers; the public worker ignores removed events while advancing the cursor; it selects vendor items; one scheduled entity exception aborts later entities without structured partial state; missing bearer is rejected only after normal entity setup; and thread-start failure consumes the throttle window. The entry points also lack tracked regression coverage. No repair, tracked product/test/workflow change, protected-data access, network call, live action, or GitHub durability occurred.

### Confirmed Work Block 3I: Mocked Luxe Legacy Downstream-Mirror Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Task 5D.

Excluded: Tasks 6-8 and all repairs from work blocks 3A-3H; product repairs or migrations; tracked test, fixture, workflow, or demo-seed changes; real databases, transactions, balances, financial rows, credentials, or downstream schema contents; production or demo access; network calls; live Plaid, workflow, Fly, Supabase, or downstream actions; authentication, CSRF, encryption, credential, or public-route changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether the optional Luxe Legacy mirror preserves LL-only invocation, true no-op behavior when configuration or eligible rows are absent, eligible-row and category exclusions, request URL/authentication/payload/timeout shape, stable repeat-request and upsert signaling, upstream failure isolation, and absence of Personal or BFM mutation with mocked HTTP only. Classify behavior as pass, defect, tracked-regression-coverage gap, or unverified remote boundary without implementing repairs.

Why this grouping: row selection, payload construction, authentication headers, idempotency signaling, and failure handling share `core/luxury_bridge.py`, its scheduled and public sync invocation seams, one temporary all-entity data model, and one deterministic mocked-HTTP verification path. Task 6 introduces broader PWA, public-route, and authentication-policy judgment; Tasks 7-8 depend on completing the remaining audit slices.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples local orchestration, synthetic all-entity verification, protected no-network boundaries, finding classification, command-center stewardship, and final intake; no delegation or second opinion is needed.

Expected surfaces: read `core/luxury_bridge.py`, its call sites in `web/routes/plaid.py` and `web/routes/kristine.py`, relevant transaction migrations in `core/db.py`, `categories.md`, and `scripts/smoke_test.py`. Use a disposable untracked probe with fake URL/key values, temporary Personal/BFM/Luxe Legacy databases, mocked `requests.post`, and outbound-socket denial. Write a sanitized 3I audit log and update `command-center/issues.md` only when findings require it; close through Runway OS sources, state, and dashboard. No application, fixture, tracked-test, workflow, or deployment file should change.

Stop conditions:

- Verification requires a real credential, protected database or financial row, network call, Supabase access, downstream schema inspection, production/demo access, or another live action.
- Actual downstream uniqueness or idempotency cannot be established from the local request contract; classify it as an unverified remote boundary rather than broadening access.
- Entity isolation, credential handling, destructive behavior, or sensitive output appears unsafe to probe beyond local mocks.
- A finding requires repair, migration, tracked regression coverage, or broader Task 6 product/security judgment.
- Verification changes the audit plan materially, or Runway OS cannot refresh and pass health checks.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- deterministic mocked configuration/no-op, LL-only invocation, eligible-row and exclusion, category-contract, URL/header/payload/type/timeout, repeat-request/upsert-signal, return-count, HTTP-error, timeout, exception, and upstream-isolation checks
- explicit Personal/BFM non-mutation, outbound-socket denial, deterministic confirmation pass, tracked regression-coverage assessment, and complete temporary cleanup
- `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: Ryan separately authorized publishing the exact eight-path 3I command-center closeout directly to `main` with `[skip actions]`. This commit is the durability record; no PR, merge, deployment, live integration action, workflow action, downstream write, product change, or pre-existing untracked-file change is included.

Report point: return a sanitized Task 5D pass, defect, gap, and unverified matrix; ranked findings with acceptance checks; local idempotency-contract versus remote-unverified conclusions; exact mocked verification; protected boundaries; cleanup; tracked-coverage assessment; and Task 6 readiness.

Result: the tracked smoke suite passed. A deterministic mocked probe produced 44 passes, three controlled failures, two contract/coverage gaps, one intentionally unverified remote boundary, and complete cleanup; a confirmation pass reproduced the same classifications. Configuration and empty-row no-ops, LL-only scheduled/public invocation and storage, normalized request and fake-auth shape, payload fields/types, stable repeats, standard exclusions, HTTP-error and timeout isolation, upstream sync preservation, Personal/BFM non-mutation, outbound-socket denial, and cleanup passed. LL `Owner Draw` was submitted because the bridge excludes nonexistent LL category `Owner Contribution`; empty Plaid IDs qualified; duplicate Plaid IDs entered one request while the conflict target remained implicit; and no tracked bridge coverage exists. Actual remote uniqueness and merge behavior remains unverified. No repair, product/test change, protected-data access, network call, downstream write, live action, or GitHub durability occurred.

### Confirmed Work Block 3J: Local PWA, Navigation, And Public-Auth Boundary Audit

Status: done; confirmed and completed locally on 2026-07-18

Included: Task 6.

Excluded: Tasks 7-8 and all repairs from work blocks 3A-3I; product repairs or migrations; tracked test, fixture, workflow, or demo-seed changes; real databases, financial rows, credentials, passwords, or existing browser authentication; production/demo access, external network calls, Plaid, Fly, GitHub Actions, or downstream writes; authentication, CSRF, encryption, credential, or public-route behavior changes; commit, push, PR, merge, and deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: determine whether the PWA installation/offline contract, desktop/tablet/phone navigation, deliberately public `/k/` dashboard, server-side authentication gate, client overlay, CSRF boundaries, exempt routes, and security headers behave consistently using only tracked source, temporary synthetic state, fake secrets, isolated localhost requests, disposable browser state, and blocked outbound networking. Classify behavior as pass, defect, tracked-regression-coverage gap, or unverified boundary without implementing repairs.

Why this grouping: PWA installation, offline behavior, responsive navigation, the public dashboard, and the main authentication gate share the app factory, base layout, browser state, service worker, and local browser verification path. Task 7 depends on the completed Task 6 evidence, while Task 8 is Ryan's later repair-prioritization decision.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit audit couples security judgment, synthetic verification, isolated browser behavior, finding classification, cleanup, and command-center stewardship. No delegation or second opinion is needed before evidence exists.

Expected surfaces: read `web/__init__.py`, `web/routes/kristine.py`, `web/templates/base.html`, sidebar/public/offline templates, `web/static/sw.js`, `web/static/manifest.json`, responsive CSS, and `scripts/smoke_test.py`. Exercise an isolated localhost app with temporary synthetic databases, fake `FLASK_SECRET` and `APP_PASSWORD_HASH` values, disposable browser state, and denied outbound networking. Write a sanitized 3J audit log and update `command-center/issues.md` only when findings require it; close through Runway OS sources, state, and dashboard. No application, fixture, tracked-test, workflow, authentication, public-route, or deployment file should change.

Stop conditions:

- Verification requires a real password, credential, financial row, production/demo access, external call, or Ryan's browser profile, local storage, or authenticated session.
- Public or authentication behavior cannot be assessed safely using temporary synthetic state and isolated local behavior.
- A serious exposure appears with synthetic data; record it and stop short of live confirmation or repair.
- A finding requires repair, migration, tracked regression coverage, or a product-direction decision.
- Scope expands beyond Task 6, cleanup cannot be proven, or Runway OS cannot refresh and pass health checks.

Verification:

- `.venv/bin/python scripts/smoke_test.py`
- temporary Flask test-client matrix for protected, public, exempt, authenticated, HTMX/JSON, and CSRF cases using fake secrets and temporary all-entity databases
- manifest, root-scoped service worker, cache, offline, update, and security-header contract checks
- isolated localhost browser checks at representative phone, tablet, and desktop viewports covering navigation, scrim, Escape, focus, ARIA state, route preservation, public rendering, and offline fallback
- outbound-network denial, disposable browser/data cleanup, `git diff --check`, Runway OS refresh, health check, generated-dashboard inspection, and final worktree review

Durability: local-only. No commit, push, PR, merge, workflow, or deployment action is part of work block 3J.

Report point: returned a sanitized PWA/navigation/public/auth matrix, seven ranked finding clusters with acceptance checks, repeated synthetic and viewport verification, cleanup, preserved boundaries, and Task 7 readiness.

Result: the maintained smoke suite passed. A repeated temporary request probe produced 31 expected passes and 12 controlled findings; a repeated isolated Chromium probe produced 23 expected passes and six controlled findings with zero external requests. Manifest and icon validation, root service-worker installation, desktop/tablet/phone overflow, basic mobile drawer state, public Personal/LL versus BFM isolation, CSRF, exempt routes, branded offline fallback, HSTS-on-HTTPS, and basic security headers passed. Seven finding clusters were recorded: protected full-page HTML and a reusable client digest bypass the intended authentication boundary; URL-only offline caching crossed BFM content into a Personal request; `/k/` publicly exposes detailed Personal and LL financial information by design; client/server/no-password auth modes drift; the mobile drawer lacks focus transfer, scroll lock, and Escape close; cookie/CSP hardening is incomplete; and no tracked PWA/public/auth/responsive coverage exists. No repair, product/test change, credential use, protected-data access, existing browser state, external call, live action, or GitHub durability occurred.

### Confirmed Work Block 3K: Findings Consolidation And Decision Readiness

Status: done; confirmed and completed on 2026-07-18

Included: Task 7 only. Consolidate the 55 Phase 3-derived entries from work blocks 3A-3J and the 4A-4B resolution evidence into one sanitized, decision-ready catalog with stable IDs, evidence sources, status, severity, confidence, affected entity or boundary, observed versus expected behavior, sanitized reproduction, impact, acceptance checks, dependency tags, and Ryan-decision tags.

Excluded: completed Tasks 1-6; Task 8 repair ordering; Phase 4 Tasks 1B-4; product repairs, migrations, tracked test implementation, `/k/` policy or behavior changes, credentials, protected data, real databases, production/demo access, Plaid, Fly, workflows, downstream writes, GitHub durability, and pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: make the completed audit evidence complete, cross-linked, deduplicated, and ready for Ryan's Task 8 prioritization without selecting the repair order or changing product behavior.

Why this grouping: every included action uses the same sanitized audit logs, issue ledger, evidence-classification rules, and command-center verification path. Task 8 is a separate Ryan-owned product and priority decision, while implementation requires subsystem-specific Phase 4 blocks.

Owner and recommended agent: Codex Desktop in the current task. The central policy assigns command-center stewardship, cross-file reconciliation, dashboard currency, and final intake to Codex; no external worker or second opinion is needed.

Blocking questions: none.

Non-blocking defaults: preserve current severity unless the recorded evidence supports a correction; distinguish functional defects, product-policy decisions, resolved findings, regression-coverage gaps, and remote-unverified boundaries; cross-link shared findings rather than duplicating them; keep historical operational/documentation issues outside the Phase 3 catalog; remain local-only.

Expected surfaces: read `command-center/issues.md`, work-block logs 3A-3J, and 4A-4B repair/release evidence; create `command-center/phase-3-findings-consolidation.md`; update the issue ledger and Runway OS source/state/dashboard surfaces. No product or tracked test file should change.

Stop conditions:

- Evidence conflicts enough to change severity or issue identity without a defensible source-backed answer.
- Consolidation requires protected data, credentials, production inspection, or another live action.
- A product-policy decision, repair-order choice, or implementation change is needed.
- Scope expands beyond Task 7, or the dashboard refresh or health check cannot pass.

Verification:

- cross-reference every Phase 3 finding and 4A-4B resolution against the consolidated catalog
- completeness checks for IDs, evidence, confidence, affected boundary, observed/expected behavior, sanitized reproduction, impact, acceptance checks, dependencies, status, duplicates, and orphaned entries
- `jq empty command-center/state.json`
- `node command-center/scripts/refresh-dashboard.js`
- `node command-center/scripts/health-check.js`
- `git diff --check`, generated-dashboard inspection, and final worktree review

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is part of work block 3K.

Report point: return the severity/status counts, stable issue catalog, resolved and decision-needed findings, dependency clusters, evidence limits, preserved boundaries, and the exact choices Ryan must make in Task 8.

Result: all 55 Phase 3-derived issue headings reconcile one-to-one to stable IDs in `command-center/phase-3-findings-consolidation.md`. The catalog contains 42 unresolved behavioral or policy findings, ten regression-coverage items, and three resolved findings; severity totals are 25 high, 29 medium, and one low. It preserves the public `/k/` contract as a Ryan decision, the downstream idempotency behavior as remotely unverified, the 4A-4B findings as resolved, and technical dependencies as sequencing evidence rather than a repair ranking. No product, test, migration, protected-data, credential, live-system, or GitHub action occurred. Task 7 and work block 3K are complete; Task 8 becomes current for a separately confirmed decision block.

### Confirmed Work Block 3L: Repair Order Decision And Phase 4 Sequencing

Status: done; the direct `claude-fable-5` / `max` review completed successfully, Codex intaked it, and Ryan confirmed all four post-review decisions on 2026-07-19

Included: Task 8 only. Assign every unresolved 3K finding to an ordered repair tier, explicit Ryan decision gate, or parked category; recommend the public `/k/` contract, first dependency cluster, paired regression coverage, and disposition of payroll compensation-unit and cookie/CSP questions; pressure-test the proposed order through one sanitized read-only Claude CLI run using `claude-fable-5` at `max` effort; and return one bounded first Phase 4 implementation block for Ryan confirmation.

Excluded: completed Tasks 1-7; completed Phase 4 Task 1A; Phase 4 Tasks 1B-4 implementation; product, migration, tracked-test, fixture, workflow, authentication, security-header, credential, or public-route changes; real databases, financial or payroll rows, uploads, credentials, production or demo access, Plaid, Fly, workflows, downstream writes, or other live actions; commit, push, PR, merge, deployment; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: give Ryan an evidence-backed repair order, explicit policy choices, and a coherent first Phase 4 block without pre-authorizing implementation or inferring production occurrence from synthetic and mocked evidence.

Why this grouping: the public `/k/` policy, first technical dependency cluster, paired coverage, and deferred product-contract questions jointly determine which repair family is safe to implement first. Code scope cannot be trustworthy until these decisions are reconciled against the same 55-entry catalog.

Owner and recommended agent: Ryan is the final decision owner. Codex Desktop is the autonomous packet owner and command-center steward. The central policy keeps orchestration, cross-file prioritization, dashboard currency, critique intake, and final recommendation with Codex.

Reviewer route: one direct sanitized Claude CLI run using model `claude-fable-5` at effort `max`. Ryan explicitly selected this one-off route after initially confirming a manual handoff. Codex must use read-only tools, plan permission mode, and no session persistence; save the response under `command-center/logs/second-opinion/`; and stop rather than substitute a different model or effort if the requested run fails.

Provisional defaults: prioritize data integrity and entity isolation before UX polish; pressure-test transaction identity and ingestion atomicity as the first cluster; pair regression coverage with every selected repair; do not accept the current detailed-public `/k/` exposure unchanged; keep payroll compensation units and cookie/CSP policy out of the first implementation block unless their cluster is selected; preserve resolved 4A-4B findings outside the repair pool; and remain local-only.

Blocking questions: none before preparing the decision and review packet. Ryan must later decide the public `/k/` contract, first dependency cluster, paired-coverage rule, and any medium product-contract gate before Task 8 closes.

Expected surfaces: read `command-center/phase-3-findings-consolidation.md`, supporting audit logs, `command-center/issues.md`, current source and synthetic tests as needed for dependency truth, and the agent-selection policy; create a sanitized Task 8 repair-order artifact and Claude CLI prompt; save the returned critique under `command-center/logs/second-opinion/`; update `command-center/roadmap.md`, `now.md`, `decisions.md`, `state.json`, and generated `index.html`. No product or tracked-test file should change.

Stop conditions:

- Prioritization requires real data, credentials, production inspection, or another live action.
- A migration, `/k/`, payroll compensation-unit, cookie/CSP, or other product contract cannot be safely recommended from verified evidence.
- Scope crosses into product implementation, GitHub durability, or a live-system mutation.
- Review reveals an evidence conflict that changes issue identity, severity, or the 3K catalog contract.
- Dashboard refresh or command-center health check cannot pass.

Verification:

- assign every unresolved finding to an ordered tier, decision gate, or explicit parked category;
- keep all three resolved findings outside the repair pool;
- reconcile dependency order to all seven Task 8 clusters and pair or explicitly park every coverage item;
- record reviewer agreements, disagreements, alternatives, confidence, and missing information without silently adopting product decisions;
- `jq empty command-center/state.json`;
- `node command-center/scripts/refresh-dashboard.js`;
- `node command-center/scripts/health-check.js`;
- `git diff --check`, generated-dashboard inspection, and final worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, product, or live action is part of work block 3L.

Report point: after the direct Claude CLI critique is saved and intaken, report the ordered repair queue, accepted and rejected reviewer recommendations, exact Ryan decisions, and one fully bounded first Phase 4 implementation block. Task 8 remains current and no implementation begins until Ryan separately confirms those decisions and the later block.

Second-opinion result: Fable 5 endorsed `P3-3A-01` plus `P3-3A-C01` as the first block with high confidence. Codex accepted the requested written per-source identity specification, populated synthetic upgrade path, same-source duplicate and empty-ID semantics, identity-only call-site boundary, early boundary/truthfulness tranche, pre-split Plaid family, `/k/` decide-by point, cookie/CSP split, focused-versus-broad read-model coverage split, and corrected vendor migration rationale. The early tranche remains several separately scoped blocks rather than one cross-subsystem implementation block. Source inspection confirmed query-side primary-key deduplication, same-dataframe duplicate dropping, stored but non-unique Plaid IDs, and the current natural-key hash at both import and Plaid call sites. The review intake moved 3L to awaiting confirmation; Ryan then confirmed all four decisions, while implementation remained unauthorized.

Result: Ryan confirmed all four post-review decisions. Transaction identity and paired coverage are first through proposed work block 4C; the next tranche uses separate boundary/truthfulness blocks before three pre-split Plaid blocks and remaining sync-entry work; `/k/` is intended to use the existing server-side authentication gate; coverage remains paired; hourly and salary payroll comparisons remain separate; cookie flags stay separate from later CSP compatibility; and downstream idempotency remains parked pending an explicitly authorized read-only remote-contract check. Task 8, work block 3L, and Phase 3 are complete without product, test, migration, protected-data, live-system, or GitHub action.

## Phase 4: Core Repairs And Regression Coverage

Status: active; work block 4AF completed Task 1P.4.2a locally and Task 1P.4.2b remains separately gated

Goal: implement the highest-value fixes while strengthening repeatable verification.

- **Task 1A: Repair the confirmed server-authentication and protected-cache boundaries.** Status: done, released, and credential-free production verified through work blocks 4A-4B and PR #86.
- **Task 1B: Establish source-aware transaction identity.** Status: done, released, and credential-free production health verified through work blocks 4C-4C-R for `P3-3A-01`.
- **Task 1C: Enforce the BFM-only payroll route boundary.** Status: done, released, and credential-free production health verified through work blocks 4D-4D-R for `P3-3F-01` plus the boundary slice of `P3-3F-C01`.
- **Task 1D: Enforce the Luxe Legacy denial boundary across planning routes.** Status: done, released, and credential-free production health verified through work blocks 4E-4E-R for `P3-3D-02` plus the boundary slice of `P3-3D-C01`.
- **Task 1E: Enforce Luxe Legacy-only downstream source selection.** Status: done, released, and credential-free production health verified through work blocks 4F-4F-R for `P3-3I-01` plus the focused selection slice of `P3-3I-C01`; remote idempotency remains parked.
- **Task 1F: Report scheduled sync partial failures truthfully.** Status: done, released, and credential-free production health verified through work blocks 4G-4G-R for `P3-3H-01` plus the workflow-visible result slice of `P3-3H-C01`; authorization-before-entity-setup (`P3-3H-06`) remains later.
- **Task 1G: Restore the Recurring Charges report query.** Status: done, released, and credential-free production health verified through work blocks 4H-4H-R for `P3-3C-01` plus the recurring-report slice of `P3-3C-C01`.
- **Task 1H: Make Plaid page application and cursor advancement atomic.** Status: done, released, and credential-free production health verified through work blocks 4I-4I-R for `P3-3G-01` plus the focused atomicity slice of `P3-3G-C01`.
- **Task 1I: Repair Plaid reconciliation, liabilities, and freshness truthfulness.** Status: done, released, and credential-free production health verified through work blocks 4J-4J-R for `P3-3G-02` through `P3-3G-05` plus the matching focused `P3-3G-C01` coverage slice.
- **Task 1J: Isolate Plaid item failures and add truthful observability.** Status: done, released, and credential-free production health verified through work blocks 4K-4K-R for `P3-3G-06`, `P3-3G-07`, and the matching focused `P3-3G-C01` slice.
- **Task 1K: Repair scheduled and public sync-entry coordination and result truthfulness.** Status: done, released, automatically deployed, and safely credential-free production verified through work blocks 4L-4L-R for `P3-3H-02` through `P3-3H-07` plus the remaining `P3-3H-C01` slice; the next natural scheduled run remains the real-sync truth point.
- **Task 1L: Repair vendor import-to-categorization integrity.** Status: done and released across Tasks 1L.1-1L.3 through work blocks 4M/4M-R, 4N/4N-R, and 4O/4O-R.
  - **Task 1L.1: Restore vendor-payment matching integrity.** Replace the nonexistent `transactions.matched_order_id` dependency with one explicit, race-safe vendor-to-bank match contract, preserve target-entity isolation, and add focused exact/review/unmatched/apply regression coverage. Status: done, released, automatically deployed, and credential-free production health verified through work blocks 4M-4M-R.
  - **Task 1L.2: Persist vendor-order line items end to end.** Save Amazon and Henry Schein line items transactionally with their parent orders, preserve exact-reimport idempotency, reconcile integer cents, and prove the maintained auto-split path no longer needs the standalone population script for new imports. Status: done and verified locally through work block 4N; release remains separate.
  - **Task 1L.3: Enforce the category source of truth deterministically.** Validate inferred and accepted transaction/vendor-order category pairs against the current entity definition, make mixed-category ties deterministic, and reject invalid writes without changing stored data. Status: done and verified locally through work block 4O; release and existing-row detection or remediation remain separate decisions.
- **Task 1M: Repair remaining payroll integrity, validation, and temporary-payload retention.** Status: done locally across Tasks 1M.1-1M.5 through work blocks 4P, 4Q, and 4R; 4R release remains separate.
  - **Task 1M.1: Prevent duplicate employees during payroll import.** Stabilize exact existing-employee assignment across preview and save, preserve explicit reassignment and genuinely unmatched creation, and pair `P3-3F-02` with its focused `P3-3F-C01` coverage slice. Status: done and verified locally through work block 4P; release remains separate.
  - **Task 1M.2: End abandoned payroll-preview payload retention.** Add an explicit cancel path that consumes only its exact temporary payload and prove save, cancel, missing, reused, expired, malformed, unrelated-payload, and cleanup behavior for `P3-3F-05` with focused coverage. Status: done and verified locally through work block 4P; release remains separate.
  - **Task 1M.3: Normalize malformed payroll-workbook failures.** Convert corrupt, mislabeled, empty, unsupported, and headerless upload failures into sanitized controlled outcomes without retaining a payload, while preserving valid multi-section preview/save behavior for `P3-3F-06` with focused coverage. Status: done and verified locally through work block 4P; release remains separate.
  - **Task 1M.4: Validate employee roster writes atomically.** Enforce maintained role, pay-type, status, date, identifier, and finite non-negative rate rules before create/update mutation; preserve valid rate-history behavior and pair `P3-3F-04` with focused coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4Q and 4Q-R.
  - **Task 1M.5: Separate payroll peer comparisons by compensation unit.** Compute and display like-for-like hourly and salary cohorts, including mixed, single-member, inactive, zero-rate, and empty cases, for `P3-3F-03` with focused coverage. Status: done and verified locally through work block 4R; release remains separate.
- **Task 1N: Repair planning, Weekly, and Waterfall calculation truthfulness.** Status: complete, released, automatically deployed, and credential-free production health verified across Tasks 1N.1-1N.8 through work blocks 4S-4Y and their release blocks.
  - **Task 1N.1: Use stored APRs in locked payoff schedules.** Pass each linked card's maintained `apr_bps` value into payoff calculation, define missing or invalid APR behavior explicitly, and reconcile avalanche/snowball order, narrative, and saved schedule for `P3-3D-01`. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4S and 4S-R.
  - **Task 1N.2: Preserve manual goal-review notes during automatic snapshots.** Update same-day balances without replacing the snapshot identity or erasing a manual note, while preserving intentional later manual-note replacement for `P3-3D-03`. Status: done, durable, automatically deployed, and credential-free production health verified through 4T and 4T-R.
  - **Task 1N.3: Compound negative asset appreciation as depreciation.** Preserve negative projection rates instead of clamping them to zero and reconcile future asset and net-worth results for `P3-3D-04`. Status: complete, durable, automatically deployed, and health verified through 4U-R.
  - **Task 1N.4: Unify Weekly date context and scheduled card-bill amounts.** Anchor pace, MTD, burn, recurring/manual/card bills, and display periods to the viewed week; use the scheduled payment rather than the full card balance for `P3-3E-01` and `P3-3E-02`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4V and 4V-R.
  - **Task 1N.5: Validate Weekly paydown dates and read stored goals defensively.** Reject invalid target dates without changing the prior goal and prevent malformed stored values from breaking Weekly or Waterfall for `P3-3E-04`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4W and 4W-R.
  - **Task 1N.6: Include deficit months in Waterfall payoff inputs.** Define the rolling period and signed-surplus rule so every included month contributes to the displayed average and payoff estimate for `P3-3E-03`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4X and 4X-R.
  - **Task 1N.7: Keep Waterfall payoff duration truthful while debt remains.** Apply a documented rounding rule so positive debt with positive surplus cannot render as zero payoff months for `P3-3E-05`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4X and 4X-R.
  - **Task 1N.8: Normalize Waterfall tax input once.** Require one finite, range-checked value to drive calculation and rendering without direct-input crashes for `P3-3E-06`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4Y and 4Y-R.
- **Task 1O: Repair the locally provable Luxe Legacy downstream-mirror contract.** Status: done and verified locally across Tasks 1O.1-1O.4 through work blocks 4Z and 4AA; publication and live downstream verification remain separate gates.
  - **Task 1O.1: Verify the tracked downstream conflict contract read-only.** Inspect only tracked schema, migration, and request-contract sources in the local downstream repository to determine whether `ledger_transactions.plaid_transaction_id` is uniquely constrained and which explicit PostgREST conflict target the mirror must use. Do not open credentials, databases, row data, network surfaces, or make changes. Status: done through 4Z; tracked schema and importer establish `plaid_transaction_id` as the primary key and explicit conflict target.
  - **Task 1O.2: Reject malformed and duplicate mirror keys deterministically.** After Task 1O.1, define and implement a local payload-selection rule for empty, whitespace-only, whitespace-padded, and repeated Plaid transaction IDs without changing Ledger source rows or dropping unrelated eligible rows. Status: done and verified locally through work block 4AA; publication remains separate.
  - **Task 1O.3: Make the mirror conflict target explicit in tracked contracts.** After Task 1O.1, align the Ledger request with `plaid_transaction_id` as the explicit PostgREST conflict target. Status: done and verified locally through work block 4AA without a downstream schema change; downstream writes, production inspection, and deployment remain separately gated.
  - **Task 1O.4: Complete maintained synthetic downstream-mirror coverage.** Pair Tasks 1O.2-1O.3 with the remaining `P3-3I-C01` no-op, request-shape, malformed-key, duplicate-key, failure-isolation, and entity-preservation checks using temporary databases, mocked HTTP, and denied outbound sockets. Status: done and verified locally through work block 4AA; publication remains separate.
- **Task 1P: Resolve the remaining public, mobile, browser-hardening, availability, and operator-clarity findings.** Status: active and decomposed into the execution-sized tasks below; the first full-page route cluster is durable through 4AJ-R, while Task 1P.4.2c.2 and Task 1P.5 are complete and verified locally through 4AK.
  - **Task 1P.1: Authenticate `/k/` through the existing server-side gate.** Resolve `P3-3J-03` and its exact request/public-field slice of `P3-3J-C01` by requiring the configured application session before route execution while preserving no-password mode, Personal/Luxe Legacy scope, BFM exclusion, and the route's self-managed database context. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4AB and 4AB-R.
  - **Task 1P.2: Make the session-cookie policy explicit.** Resolve the cookie half of `P3-3J-06` with a production-safe Secure, HttpOnly, and SameSite contract that preserves local and synthetic-test usability. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4AC and 4AC-R.
  - **Task 1P.3: Complete mobile-drawer accessibility.** Resolve `P3-3J-05` and its responsive-navigation slice of `P3-3J-C01` with focus placement and restoration, Escape and scrim closing, open-only scroll lock, route-click consistency, and maintained browser coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4AD and 4AD-R.
  - **Task 1P.4: Design and enforce a compatible Content Security Policy.** Resolve the CSP half of `P3-3J-06` without weakening the policy merely to avoid template work. Work block 4AE found 46 script elements, 161 inline event-handler attributes, 221 inline style attributes, four `hx-on` attributes, HTMX 2.0.4 fragment behavior, two Plaid Link entry templates, and separate base, login, offline/error, and `/k/` document families. Status: active; compatibility planning, shared execution, both fragment migration slices, final HTMX disablement, and the first full-page route cluster are durable through 4AJ-R; Task 1P.4.2c.2 is complete and verified locally through 4AK.
    - **Task 1P.4.1: Freeze the CSP compatibility contract and migration matrix.** Inventory every executable-script, HTMX fragment, inline-style, local-asset, worker/manifest, login, offline/error, standalone `/k/`, and Plaid Link dependency; define exact candidate directives and allowed origins; classify every required rewrite; and specify a synthetic header/browser verification matrix without changing product behavior. Status: complete and verified locally through work block 4AE; durability is active through Task 1P.4.1-R and implementation remains separate.
      - **Task 1P.4.1-R: Publish the CSP contract and planning closeout.** Make the exact nine-path 4AE command-center artifact set durable on `main` through native `[skip actions]` commits, exact remote-SHA verification, and a sanitized closeout without triggering deployment. Status: active through confirmed work block 4AE-R.
    - **Task 1P.4.2: Remove inline executable markup and HTMX eval dependencies.** Move executable inline script blocks, native event-handler attributes, and `hx-on` behavior into maintained local static JavaScript and delegated listeners; carry server-rendered values through inert JSON or data attributes; and disable HTMX eval and swapped-script execution only after focused synthetic coverage proves compatibility. Status: active and decomposed by the 4AE matrix; Tasks 1P.4.2a, 1P.4.2b.1, and 1P.4.2b.2 are complete at their recorded durability levels.
      - **Task 1P.4.2a: Migrate the shared execution foundation.** Move shared-shell executable blocks and native/HTMX handlers to maintained local JavaScript; move HTMX indicator rules to local CSS; disable only injected indicator styles; and prove the shell while explicitly retaining eval and swapped-script processing until their remaining fragment dependencies are removed. Status: complete and verified locally through work block 4AF.
      - **Task 1P.4.2b: Migrate HTMX-swapped fragment execution.** Remove executable scripts and inline handlers from directly returned fragments; replace the remaining fragment `hx-on` behavior; carry server state through inert data; initialize repeated swaps through delegated listeners or `htmx:load`; then disable HTMX eval and swapped-script processing. The verified pre-4AG fragment surface contained ten executable template scripts, 40 template-native inline handlers, one Python-rendered inline handler, and two `hx-on` handlers, so it is decomposed into the execution-sized tasks below. Status: complete, durable, automatically deployed, and credential-free health verified through 4AI-R.
        - **Task 1P.4.2b.1: Migrate dashboard and report fragment execution.** Move the nine executable template scripts, twelve template-native inline handlers, and one Python-rendered insight-detail inline handler in the included dashboard, analysis, category-comparison, KPI, insight, and report fragment responses into maintained local JavaScript; carry chart and server-rendered values inertly; and prove repeated swaps, chart redraws, drilldowns, modals, and report expansion without fragment script execution. Status: complete, durable, automatically deployed, and credential-free health verified through work blocks 4AG and 4AG-R.
        - **Task 1P.4.2b.2: Migrate transaction and supporting modal fragment execution.** Move the one executable script, remaining twenty-eight native inline handlers, and two `hx-on` handlers in transaction results, row editing, split editing, and supporting popup/queue fragments into maintained local JavaScript and declarative data; preserve sorting, copy, edit, suggest, rule, split, modal, and cleanup behavior across repeated swaps. Status: complete, durable, automatically deployed, and credential-free health verified through work blocks 4AH and 4AH-R.
        - **Task 1P.4.2b.3: Disable and prove HTMX eval and swapped-script processing.** After Tasks 1P.4.2b.1-1P.4.2b.2 leave no directly returned executable fragment or eval-backed attribute, set `allowEval=false` and `allowScriptTags=false`; assert the residual inventory is zero; and run the cross-route repeated-swap synthetic and isolated-browser matrix. Status: complete, durable, automatically deployed, and credential-free health verified through work blocks 4AI and 4AI-R.
      - **Task 1P.4.2c: Migrate remaining full-page execution.** Move the remaining 22 executable inline scripts, 116 template-native handlers, two Python-rendered handlers, and two full-page inert JSON carriers to maintained local behavior and inert server data. The verified source inventory is decomposed into the eight route clusters below. Status: active and decomposed; Task 1P.4.2c.1 is durable through 4AJ-R, Task 1P.4.2c.2 is durable through 4AK-R, Tasks 1P.4.2c.3a-1P.4.2c.3b are durable through 4AL-R, and Task 1P.4.2c.3c is complete locally with publication active through 4AM-R.
        - **Task 1P.4.2c.1: Migrate core review-page execution.** Move the five executable inline scripts and eighteen native handlers in `components/sidebar.html`, `dashboard.html`, `reports.html`, `transactions.html`, and `todo.html` into the existing shared, dashboard-fragment, and transaction-fragment asset seams; preserve view switching, report export state, transaction filtering/suggestions, To Do modal behavior, sidebar controls, and repeated HTMX behavior. Status: complete, durable, automatically deployed, and credential-free health verified through 4AJ-R.
        - **Task 1P.4.2c.2: Migrate categorization and upload execution.** Move the three executable inline scripts and seven native handlers in `categorize.html`, `categorize_orphans.html`, and `upload.html` into maintained local behavior while preserving alias prefill, category/subcategory loading, month selection, and destructive-action confirmations. Status: complete, durable, automatically deployed, and credential-free health verified through 4AK-R with Task 1P.5 and only the focused Task 2 regression slices.
        - **Task 1P.4.2c.3: Migrate cash-flow and planning execution.** Umbrella task for the three execution-sized route slices below. The verified source contained three executable inline scripts, forty-seven template-native handlers, one inert JSON carrier, and two Python-rendered Short-Term Planning handlers across `cashflow.html`, `planning.html`, `short_term_planning.html`, and the same-route budget response builders. Status: complete locally; Tasks 1P.4.2c.3a-1P.4.2c.3b are durable through 4AL-R and Task 1P.4.2c.3c publication is active through 4AM-R.
          - **Task 1P.4.2c.3a: Migrate Cash Flow execution.** Move the one executable inline script and fifteen native handlers in `cashflow.html` into a maintained page-owned local controller while preserving account/card opening, modal population, balance/limit/APR/payment sizing, due-day parsing, recurring-entry setup, scrim/Escape closure, AI entry, and Personal/BFM/LL visibility. Status: complete and locally verified through 4AL; durability/release remains separate.
          - **Task 1P.4.2c.3b: Migrate Long-Term Planning execution.** Move the one executable inline script and ten native handlers in `planning.html` into a maintained page-owned local controller while preserving asset/liability add, edit, source switching, delete confirmation, birthday editing, projection display, modal/scrim/Escape behavior, AI entry, Personal/BFM sharing, and Luxe Legacy denial. Status: complete and locally verified through 4AL; durability/release remains separate.
          - **Task 1P.4.2c.3c: Migrate Short-Term Planning execution.** Move the one executable inline script, twenty-two template-source native-handler occurrences, one inert JSON carrier in `short_term_planning.html`, and two Python-rendered native handlers in the same budget drill-down route family into maintained local behavior and non-script inert data while preserving goal and plan dialogs, progress, budgets, action items, category drill-downs, dynamic transaction editing, fetch behavior, and keyboard/modal behavior. Status: complete and locally verified through work block 4AM with only its focused Task 2 regression slice; exact-scope durability/release is active through 4AM-R.
        - **Task 1P.4.2c.4: Migrate Weekly and Waterfall execution.** Move the one executable inline script and thirteen native handlers in `weekly.html` and `waterfall.html` into maintained local behavior while preserving weekly AI entry, waterfall mode, breakdown, target, tax, tooltip, and keyboard behavior. Status: planned.
        - **Task 1P.4.2c.5: Migrate subscription-page execution.** Move the one executable inline script, fifteen native handlers, and one inert JSON carrier in `subscriptions.html` into maintained local behavior and non-script inert data while preserving suggestion, watchlist, detail, account-info, copy, tips, modal, and keyboard workflows. Status: planned as a standalone high-interaction page cluster.
        - **Task 1P.4.2c.6: Migrate payroll-page execution.** Move the one executable inline script and nine native handlers in `payroll.html` into maintained local behavior while preserving add/edit/detail, spending-period, new-role, deletion-confirmation, modal, and keyboard workflows. Status: planned as a separate BFM-only payroll boundary.
        - **Task 1P.4.2c.7: Migrate Plaid entry-page execution.** Move the three executable inline application scripts and six native handlers in `data_sources.html` and `plaid.html` into maintained local behavior and inert server data while retaining the two exact external Plaid initializer tags for the later narrow policy; prove Link wiring only with fake configuration, mocked Plaid, denied outbound networking, and temporary synthetic data. Status: planned as a separate integration and CSP-exception boundary.
        - **Task 1P.4.2c.8: Migrate standalone and error-document execution.** Move the five executable inline scripts and one native handler in `offline.html`, `errors/403.html`, `errors/404.html`, `errors/500.html`, and `kristine.html` into document-family-specific local behavior while preserving data-free error/offline rendering, retry behavior, `/k/` interaction, authentication boundaries, and no exception leakage. Status: planned as a separate standalone-document verification family.
    - **Task 1P.4.3: Make styling and exceptional document surfaces policy-compatible.** Apply the strict core style-attribute contract while confining Plaid's documented exception to Link documents. Status: planned and decomposed by the 4AE matrix.
      - **Task 1P.4.3a: Make application styles strict-policy compatible.** Move seven inline style blocks, 221 style attributes, and runtime style mutations to static CSS/classes or bounded data-driven states so core documents can enforce `style-src-attr 'none'`. Status: planned; split into bounded route clusters before execution.
      - **Task 1P.4.3b: Reconcile exceptional documents and Plaid.** Cover login, offline/errors, standalone `/k/`, local data images, worker/manifest, and the narrow Plaid document policy with exact initializer, frame, environment-specific connect, and Plaid-only style-attribute allowances. Status: planned after relevant execution/style prerequisites.
    - **Task 1P.4.4: Enforce and prove the final Content Security Policy.** Add the exact Flask response policy and any request-scoped nonce plumbing selected by the contract; prove full-page and HTMX-fragment behavior, configured-auth and no-password modes, standalone `/k/`, offline/error, service-worker/manifest, and mocked Plaid boundaries with maintained synthetic header and isolated-browser coverage; then close `P3-3J-06` only if no prohibited source remains. Status: planned after Tasks 1P.4.1-1P.4.3.
  - **Task 1P.5: Clarify Upload `Undo` as status-only.** Resolve `P3-3B-04` with explicit operator language that resetting checklist state does not remove imported ledger rows, plus focused rendered/request coverage. Status: complete and verified locally through 4AK; durability remains separate.
  - **Task 1P.6: Finish installed-PWA and browser-boundary regression coverage.** Complete the unconsumed manifest/icon, service-worker installation and offline-isolation, configured-auth, and exact post-decision `/k/` slices of `P3-3J-C01` without reopening resolved 4A-4B behavior absent contrary evidence. Status: planned and paired with the relevant preceding repairs where practical.
  - **Task 1P.7: Finish the remaining broad financial read-model regression coverage.** Consume the unpaired remainder of `P3-3C-C01` through one separately scoped synthetic verification block; do not mix it into public-route, mobile, or browser-policy implementation. Status: planned after the higher-risk Task 1P boundary work.
- **Task 2: Expand regression tests around repaired workflows and entity isolation.** Status: active as paired work only; 4C completed `P3-3A-C01`, 4D completed the payroll-boundary slice of `P3-3F-C01`, 4E completed the planning-boundary slice of `P3-3D-C01`, 4F completed the Owner Draw/source-selection slice of `P3-3I-C01`, 4G completed the workflow-visible result slice of `P3-3H-C01`, 4H completed the recurring-report slice of `P3-3C-C01`, 4I completed the transaction/cursor atomicity slice, 4J completed its reconciliation, link, liability, and freshness slice, 4K completed its item-isolation and observability slice, 4M completed its vendor-payment matching slice, 4P completed its payroll import and payload slice, 4Q completed its roster-validation slice, 4S completed the locked-payoff APR slice, 4T completed the snapshot-persistence slice of `P3-3D-C01`, 4V completed the `P3-3E-01`/`P3-3E-02` Weekly slice, 4W completed the `P3-3E-04` Weekly/Waterfall validation slice, and 4AD completed the responsive-navigation slice of `P3-3J-C01`.
- **Task 3: Add CI checks that are safe for a private financial application and use only synthetic data.**
- **Task 4: Publish and verify only explicitly approved repairs.** Status: done through 4AD-R for every explicitly released repair to date; future publication remains separately gated.

### Confirmed Work Block 4AE-R: CSP Contract Durability

Status: complete and durable on `main` without deployment

Parent task: Phase 4 Task 1P.4.1-R only.

Included: exact-path and sensitive-addition review; validate local and remote `main` alignment; explicitly stage only the nine verified 4AE command-center paths; create `Publish 4AE CSP compatibility contract [skip actions]`; push directly to `origin/main` without force or PR; verify the exact remote SHA and that GitHub natively skipped Actions; record the sanitized durable result in existing Runway OS sources; create one command-center-only closeout commit with `[skip actions]`; push it; and verify final local/remote alignment, skipped Actions, and preserved exclusions.

Exact publish paths: `command-center/csp-compatibility-contract.md`; `command-center/logs/2026-07-21-csp-compatibility-contract-4ae.md`; `command-center/decisions.md`; `command-center/index.html`; `command-center/issues.md`; `command-center/now.md`; `command-center/phase-3-findings-consolidation.md`; `command-center/roadmap.md`; and `command-center/state.json`.

Excluded: proposed Tasks 1P.4.2a-1P.7 and work block 4AF; the remainder of Task 2; Tasks 3-4; all product, template, JavaScript, CSS, maintained-test, dependency, runtime configuration, authentication, cookie, CSRF, security-header, public-route, service-worker, manifest, or Plaid behavior changes; credentials; protected data; real databases; retained uploads; production or demo inspection; workflow edits, dispatches, or reruns; Fly actions; external calls beyond GitHub fetch/push/read-only commit and workflow metadata; PR creation; force push; recovery beyond a normal fast-forward decision; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: all included paths are one sanitized, verified Task 1P.4.1 planning outcome with one Git durability path and no application-release value. Publishing them together makes the CSP contract durable while a native `[skip actions]` commit prevents an unnecessary Fly deployment.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns scope control, Git safety, sensitive-addition checks, direct-main durability, skipped-workflow verification, and final Runway OS closeout. Ryan owns every product, reviewer, 4AF, live, deployment, and recovery decision.

Defaults: no PR, branch, force push, product change, deployment, or production health check; explicit path staging only; both commits contain `[skip actions]`; verify native workflow skipping rather than assuming it; preserve both unrelated untracked files; keep proposed 4AF unconfirmed after closeout.

Stop conditions: unexpected path; sensitive addition; protected data; unrelated change; failed maintained command-center verification; local or remote `main` divergence; excluded staging; push rejection; a workflow run despite `[skip actions]`; or any recovery beyond a normal fetch-and-fast-forward decision.

Verification: exact nine-path scope; no application/product/test/dependency diff; protected-path and high-confidence secret scans; `jq empty command-center/state.json`; dashboard refresh and health; whitespace including new files; rendered-dashboard inspection; staged-set and commit-content review; local/remote ancestry and exact SHA after each push; read-only workflow metadata showing no run for either commit; final clean tracked worktree with both excluded untracked files preserved.

Dashboard closeout: after the first push, update human-readable sources with the durable source commit, align `state.json`, refresh and health-check, inspect the rendered closeout, commit only existing command-center paths with `[skip actions]`, push, and verify final alignment.

Report point: return source and closeout SHAs, exact published paths, GitHub Actions skip result, final branch alignment, preserved exclusions, no deployment, and proposed 4AF as the separately confirmable next block.

Result: exact nine-path source commit `d749700` is durable on `main`; local and remote SHA matched; GitHub Actions returned zero runs for the source SHA because `[skip actions]` was honored; no Fly deployment occurred; exact-scope, sensitive-addition, protected-path, JSON, dashboard, health, whitespace, rendered inspection, staged-set, commit-content, ancestry, remote-alignment, and exclusion checks passed. This sanitized command-center-only closeout also uses `[skip actions]`.

Suggested next work block: proposed 4AF remains unchanged and unconfirmed after 4AE-R.

### Confirmed Work Block 4AG: Dashboard And Report Fragment Execution

Parent task: Phase 4 Task 1P.4.2b.1 only.

Status: complete and verified locally.

Included: move nine executable template scripts, twelve template-native inline handlers, and one Python-rendered insight-detail inline handler from the included dashboard, analysis, category-comparison, KPI, insight, and report fragment responses into maintained local JavaScript; carry chart and server-rendered values inertly; preserve chart, drilldown, modal, AI-panel, and report behavior across repeated swaps; add focused synthetic and isolated-browser coverage; reconcile the CSP contract, findings/issues, evidence, and Runway OS; and close locally.

Excluded: Tasks 1P.4.2b.2-1P.7; the remainder of Task 2; Tasks 3-4; transaction results/edit/split and supporting popup/queue migration; global HTMX eval or swapped-script disablement; remaining page scripts or native handlers; inline-style migration; CSP headers, nonces, or enforcement; Plaid; login; offline/errors; standalone `/k/`; worker/manifest; authentication, cookie, CSRF, responsive redesign, or financial behavior; new dependencies; credentials; protected data; real databases; retained uploads; external networking; production/demo inspection; GitHub durability; publication; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the included nine templates share the analytics/report fragment lifecycle, repeated-swap initialization model, chart and modal behavior, objective source inventory, and one isolated-browser verification path. The transaction/editor fragments use a separate mutation and cleanup model, while global HTMX disablement must wait until both migration slices are complete.

Owner and agent: Codex Desktop in the current task without delegation or second opinion. The sensitive retrofit policy prefers Codex when implementation, verification, scope control, and final dashboard stewardship are tightly coupled.

Runner path: create and work on `codex/csp-dashboard-report-fragments`; keep durability local-only.

Expected surfaces: `web/templates/components/ai_analysis.html`, `categories_compare.html`, `dashboard_body.html`, `dashboard_detail_cats.html`, `dashboard_detail_insights.html`, `ie_ai_analysis.html`, `insights_upcoming.html`, `kpi_panel.html`, and `rpt_view.html`; the exact insight-detail response builder in `web/routes/dashboard.py`; maintained local JavaScript and its loading point as needed; `scripts/smoke_test.py`; focused isolated-browser coverage; CSP contract, findings/issues, evidence log, Runway OS sources, and generated dashboard.

Defaults: preserve visual and behavioral parity; use inert declarative data, delegated listeners, and `htmx:load` or equivalent idempotent initialization; add no runtime dependency; keep `allowEval=true` and `allowScriptTags=true` with explicit assertions for later Tasks 1P.4.2b.2-1P.4.2b.3; use temporary synthetic all-entity databases, localhost only, denied non-localhost requests, disposable browser state, and exact cleanup; preserve both unrelated untracked files.

Stop conditions: parity requires transaction/editor/supporting-modal work or another excluded route family; this slice requires disabling global HTMX compatibility settings; a CSP-header, style-policy, Plaid, authentication, product/design, or new-dependency decision appears; protected data, credentials, real databases, external/live access, another task, plan-changing verification failure, cleanup failure, command-center failure, or preserved-file overlap appears.

Verification: baseline and final full synthetic smoke; focused request/source assertions proving the nine included fragments contain zero executable inline scripts and zero native inline handlers; configured-auth and no-password isolated Chrome covering repeated dashboard body, KPI, category comparison/detail, insights, AI analysis, chart, and report swaps; denied external requests, console/page errors, exact cleanup; relevant Python/JavaScript/JSON syntax; `git diff --check`; dashboard refresh and health; rendered-dashboard inspection; exact product boundary; both preserved untracked files.

Durability: local-only. No commit, push, PR, merge, workflow action, deployment, production/demo inspection, credential, protected-data, real-database, or live action is included.

Result: the nine included templates now contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes. `dashboard-fragments.js` owns idempotent chart/KPI initialization and delegated category, insight, AI, and report actions. Full synthetic smoke and configured-auth/no-password isolated Chrome pass repeated dashboard, KPI, category, insight, AI, chart, and report swaps with denied external requests, zero console/page errors, and exact synthetic cleanup. Relevant syntax, JSON, whitespace, dashboard refresh/health, rendered inspection, exact scope, and preserved-file checks pass. `allowEval` and `allowScriptTags` remain true; Task 1P.4.2b.2 retains one executable script, twenty-eight handlers, and two `hx-on` attributes. The result is local-only on `codex/csp-dashboard-report-fragments`.

Report point: return exact migrated behavior and local asset structure, residual fragment counts, continued temporary HTMX dependency status, focused and full verification, changed paths, cleanup, local-only branch status, and a separately confirmable Task 1P.4.2b.2 block.

Suggested next work block: 4AH for Task 1P.4.2b.2 only after 4AG closes cleanly; keep Task 1P.4.2b.3 separate until both migration slices are complete.

### Confirmed Work Block 4AG-R: Dashboard And Report Fragment Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified.

Parent task: Phase 4 Task 1P.4.2b.1-R only.

Included: exact-path staging of the twenty-three verified 4AG application, static-asset, maintained-test, CSP contract, issue, findings, evidence, and Runway OS paths; one intentional source commit on `codex/csp-dashboard-report-fragments`; fast-forward local `main`; direct push to `origin/main` without force or PR; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; exact source-SHA verification; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source paths: `command-center/csp-compatibility-contract.md`; `command-center/decisions.md`; `command-center/index.html`; `command-center/issues.md`; `command-center/logs/2026-07-22-dashboard-report-fragment-execution-4ag.md`; `command-center/now.md`; `command-center/phase-3-findings-consolidation.md`; `command-center/roadmap.md`; `command-center/state.json`; `scripts/mobile_drawer_browser_test.py`; `scripts/smoke_test.py`; `web/routes/dashboard.py`; `web/static/dashboard-fragments.js`; `web/templates/base.html`; `web/templates/components/ai_analysis.html`; `categories_compare.html`; `dashboard_body.html`; `dashboard_detail_cats.html`; `dashboard_detail_insights.html`; `ie_ai_analysis.html`; `insights_upcoming.html`; `kpi_panel.html`; and `rpt_view.html`.

Excluded: Tasks 1P.4.2b.2-1P.7; proposed work block 4AH implementation; any new product, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, or Plaid mutation; credentials; protected data; real databases; retained uploads; authenticated production pages; workflow edits, manual dispatches, or reruns; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and agent: Codex Desktop in the current task without delegation. Ryan explicitly authorized commit and direct push to `main`; no PR is used.

Defaults: explicit path staging only; preserve the verified source and temporary HTMX compatibility state; observe only the automatic deployment and credential-free health; use `[skip actions]` only for the sanitized command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition; protected-boundary risk; failed maintained verification; excluded staging; local or remote `main` divergence; push rejection; automatic deployment or credential-free health failure requiring mutation; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact path and staged sets; high-confidence sensitive-addition and protected-path scans; full smoke; isolated-browser matrix; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and rendered inspection; commit content; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production health; final worktree and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with the exact commit/run/health result, align `state.json`, refresh and health-check, inspect the rendered closeout, commit only the sanitized existing command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and proposed 4AH still separately gated.

Result: exact twenty-three-path source commit `2ea23d1a6399be5e37d96275e84d45519105846c` is durable on `main` and `origin/main`; automatic Fly Deploy run `29895902768` and job `88845905269` passed for that exact SHA; credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-path, high-confidence sensitive-addition, maintained smoke, isolated-browser, syntax, JSON, whitespace, dashboard refresh/health/rendered-state, ancestry, remote-alignment, and preserved-exclusion checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, credential, protected data, real database, authenticated production page, downstream access/write, future fragment implementation, or preserved-file mutation occurred. This sanitized command-center-only closeout uses `[skip actions]`; proposed 4AH remains separately gated.

### Confirmed Work Block 4AH-R: Transaction And Supporting Modal Fragment Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified

Parent task: Phase 4 Task 1P.4.2b.2-R only.

Included: exact-path staging of the eighteen verified 4AH application, static-asset, maintained-test, CSP contract, issue, findings, evidence, and Runway OS paths; one intentional source commit on `codex/csp-transaction-modal-fragments`; fast-forward local `main`; direct push to `origin/main` without force or PR; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; exact source-SHA verification; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source paths: `command-center/csp-compatibility-contract.md`; `command-center/decisions.md`; `command-center/index.html`; `command-center/issues.md`; `command-center/logs/2026-07-22-transaction-modal-fragment-execution-4ah.md`; `command-center/now.md`; `command-center/phase-3-findings-consolidation.md`; `command-center/roadmap.md`; `command-center/state.json`; `scripts/mobile_drawer_browser_test.py`; `scripts/smoke_test.py`; `web/static/transaction-fragments.js`; `web/templates/base.html`; `web/templates/components/subcat_txns_popup.html`; `todo_queue_detail.html`; `txn_results.html`; `txn_row_edit.html`; and `txn_split_editor.html`.

Excluded: Task 1P.4.2b.3 and later tasks; proposed 4AI implementation; any new product, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, or Plaid mutation beyond the verified 4AH set; credentials; protected data; real databases; retained uploads; authenticated production pages; workflow edits, manual dispatches, or reruns; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and agent: Codex Desktop in the current task without delegation. Ryan explicitly authorized commit and direct push to `main`; no PR is used.

Defaults: explicit path staging only; preserve the verified source and temporary HTMX compatibility state; observe only the automatic deployment and credential-free health; use `[skip actions]` only for the sanitized command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition; protected-boundary risk; failed maintained verification; excluded staging; local or remote `main` divergence; push rejection; automatic deployment or credential-free health failure requiring mutation; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact path and staged sets; high-confidence sensitive-addition and protected-path scans; full smoke; isolated-browser matrix; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and rendered inspection; commit content; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production health; final worktree and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with the exact commit/run/health result, align `state.json`, refresh and health-check, inspect the rendered closeout, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and proposed 4AI still separately gated.

Result: exact eighteen-path source commit `ec27736b50a79ab24d3f0d5c2fa115a60e7c44da` is durable on `main` and `origin/main`; automatic Fly Deploy run `29926538588` and deploy job `88945038809` passed for that exact SHA; credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-path, high-confidence sensitive-addition, maintained smoke, isolated-browser, syntax, JSON, whitespace, dashboard refresh/health/rendered-state, ancestry, remote-alignment, and preserved-exclusion checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, credential, protected data, real database, authenticated production page, downstream access/write, Task 1P.4.2b.3 implementation, or preserved-file mutation occurred. This sanitized command-center-only closeout uses `[skip actions]`; proposed 4AI remains separately gated. Evidence: `command-center/logs/2026-07-22-transaction-modal-fragment-execution-release-4ah-r.md`.

### Confirmed Work Block 4AH: Transaction And Supporting Modal Fragment Execution

Status: complete and verified locally; not published

Parent task: Phase 4 Task 1P.4.2b.2 only.

Included: record 4AH as active before product work; create `codex/csp-transaction-modal-fragments`; move the one executable script, twenty-eight native inline handlers, and two `hx-on` handlers from `components/txn_results.html`, `txn_row_edit.html`, `txn_split_editor.html`, `subcat_txns_popup.html`, and `todo_queue_detail.html` into maintained local JavaScript and declarative data; preserve sorting, copy, edit, suggest, rule, split, popup, queue, modal, and cleanup behavior across repeated swaps; add focused maintained synthetic and isolated-browser proof; reconcile the CSP contract, findings/issues, evidence, and Runway OS; and close locally after full verification.

Excluded: Task 1P.4.2b.3; Task 1P.4.2c; Tasks 1P.4.3-1P.7; the remainder of Task 2; Tasks 3-4; global HTMX eval or swapped-script disablement; remaining full-page execution; style migration; CSP headers, nonces, or enforcement; Plaid; login; offline/errors; standalone `/k/`; worker/manifest; authentication, cookie, CSRF, responsive, or financial behavior; new dependencies; credentials; protected data; real databases; retained uploads; external networking; production/demo inspection; GitHub durability; publication; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the five remaining directly returned fragments share one execution-removal contract, one maintained delegated-listener pattern, and one synthetic repeated-swap verification path. Task 1P.4.2b.3 changes global compatibility switches and therefore remains a separate gate after this migration proves the residual fragment inventory is zero.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. The sensitive retrofit policy favors Codex because cross-template implementation, local browser verification, exact cleanup, and final Runway OS stewardship are tightly coupled. Ryan owns every scope expansion, publication, deployment, live action, and Task 1P.4.2b.3 decision.

Expected surfaces: the five included component templates; a maintained local fragment controller and shared asset-loading point only as needed; focused `scripts/smoke_test.py` and isolated-browser coverage; the CSP contract, findings/issues, sanitized evidence, Runway OS sources, and generated dashboard. Full-page inline execution remains outside scope even when an included fragment calls an existing page-level helper.

Defaults: preserve visual and behavioral parity; use inert data, delegated listeners, and idempotent HTMX initialization; add no runtime dependency; retain `allowEval=true` and `allowScriptTags=true` with explicit assertions for Task 1P.4.2b.3; use temporary synthetic all-entity databases, fake or empty integration configuration, localhost only, denied non-localhost requests, disposable browser state, and exact cleanup; keep durability local-only; preserve both unrelated untracked files.

Stop conditions: parity requires migrating full-page execution or disabling global HTMX compatibility; a broader product, design, authentication, CSP-header, style-policy, Plaid, financial-behavior, or new-dependency decision appears; protected data, credentials, real databases, external/live access, another task, plan-changing verification failure, cleanup failure, command-center failure, or preserved-file overlap appears.

Verification: baseline and final full synthetic smoke; focused source and rendered-response assertions proving the five included fragments contain zero executable scripts, zero native inline handlers, and zero `hx-on` attributes; configured-auth and no-password isolated Chrome covering repeated transaction results, sorting, copy, edit/cancel/save, suggestion/rule, split add/remove/auto/save/delete, subcategory popup, To Do queue, modal-close, backdrop, after-request, and cleanup behavior; denied external requests; zero console/page errors; entity isolation; exact temporary-data cleanup; relevant Python/JavaScript/JSON syntax; `git diff --check`; dashboard refresh and health; rendered-dashboard inspection; exact product boundary; both preserved untracked files.

Dashboard closeout: when implementation and verification finish, mark 4AH done and local-only, preserve Task 1P.4.2b.3 as awaiting separate confirmation, align human-readable sources and `state.json`, refresh and health-check, inspect the rendered closeout, and do not commit or publish.

Report point: return exact migrated behavior, local asset structure, zeroed fragment inventory, continued temporary HTMX settings, focused and full verification, changed paths, cleanup, preserved boundaries, local-only branch state, and a separately confirmable 4AI block for Task 1P.4.2b.3.

Suggested next work block: 4AI for Task 1P.4.2b.3 only after 4AH closes cleanly; publication remains separately gated.

### Confirmed Work Block 4AI: Final HTMX Execution-Switch Disablement

Status: complete and verified locally on `codex/csp-htmx-disablement`; publication remains separate.

Parent task: Phase 4 Task 1P.4.2b.3 only.

Included: set the declarative HTMX `allowEval` and `allowScriptTags` settings to `false`; prove the tracked template surface contains no `hx-on`, `hx-vars`, JavaScript-valued `hx-vals` or `hx-headers`, or trigger-filter dependencies; prove directly returned dashboard/report and transaction/supporting-modal fragments contain no executable scripts or native inline handlers; preserve shared-shell, dashboard/report, and transaction/modal behavior across repeated swaps; add or revise maintained synthetic and configured-auth/no-password isolated-browser coverage; and close Runway OS locally.

Excluded: Task 1P.4.2c; Tasks 1P.4.3-1P.7; the remainder of Task 2; Tasks 3-4; remaining full-page scripts and native handlers; style migration; CSP headers, nonces, or enforcement; Plaid; authentication; cookies; CSRF; service-worker or manifest changes; product, responsive, or financial behavior; vendored HTMX edits; new dependencies; credentials; protected data; real databases; retained uploads; external networking; production/demo inspection; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: both global switches govern the same HTMX execution boundary and share one zero-dependency inventory plus one cross-route repeated-swap verification path. Tasks 1P.4.2b.1 and 1P.4.2b.2 are durable prerequisites. Remaining full-page execution and CSP/style enforcement use broader surfaces and separate verification paths, so they remain later blocks.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. The change is mechanically small but couples global browser behavior, maintained synthetic and isolated-browser proof, cleanup, and Runway OS stewardship; deterministic acceptance checks make independent critique unnecessary. Ryan owns every expansion, publication, deployment, and live action.

Runner path: current Codex task on local branch `codex/csp-htmx-disablement`.

Expected surfaces: `web/templates/base.html`; the three inert JSON carriers in `web/templates/components/dashboard_body.html` and `txn_split_editor.html`; their existing `web/static/dashboard-fragments.js` and `transaction-fragments.js` readers; focused `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py` coverage; `command-center/csp-compatibility-contract.md`; sanitized 4AI evidence; and Runway OS roadmap, now, decisions, state, and generated dashboard. Other application templates or JavaScript remain excluded.

Defaults: preserve all user-visible behavior; edit no vendored HTMX library; use the existing declarative meta configuration; use temporary synthetic Personal, BFM, and Luxe Legacy data plus disposable localhost browser state; deny non-localhost requests; require zero unexpected console/page errors and exact cleanup; keep durability local-only; preserve both unrelated untracked files.

Blocking questions: none. Ryan confirmed the proposed base scope without expansion.

Stop conditions: an eval-backed HTMX dependency appears; parity requires Task 1P.4.2c, product behavior, CSP-header, style-policy, Plaid, authentication, service-worker, manifest, financial, or dependency changes; protected data, credentials, real databases, retained uploads, external/live access, another task, plan-changing verification failure, cleanup failure, command-center failure, or either preserved-file overlap appears.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions for zero eval-backed HTMX attributes and zero directly returned fragment execution; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` across shared-shell behavior, repeated dashboard/report swaps, and repeated transaction/modal workflows with both runtime switches false; denied non-localhost requests; zero unexpected console/page errors; exact temporary all-entity cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; rendered-dashboard inspection; explicit-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AI and Task 1P.4.2b.3 done and local-only; make Task 1P.4.2c the next decision gate; align human-readable sources with `state.json`; refresh and health-check; inspect the rendered closeout; and do not commit or publish.

Report point: return the exact HTMX switch contract, zero-dependency inventory, cross-route synthetic and browser proof, changed paths, cleanup, preserved boundaries, local branch state, and separate publication plus Task 1P.4.2c gates.

Suggested next work block: after 4AI closes cleanly, run just-in-time decomposition for broad Task 1P.4.2c and propose 4AJ for its first coherent full-page route cluster; publication remains separately gated.

Result: `base.html` now sets `allowEval=false` and `allowScriptTags=false`. Maintained source proof finds zero eval-backed HTMX attributes, and all directly returned dashboard/report plus transaction/supporting-modal fragments contain zero script elements and zero native inline handlers. The first disabled-switch browser run revealed that HTMX removes inert `application/json` script carriers from swapped content; the one dashboard chart payload and two transaction split-editor payloads therefore moved to non-script template data read by their existing maintained controllers. The aggregate tracked inventory is now 31 script elements: 22 executable inline scripts, seven external scripts, and two full-page inert JSON scripts, with 116 native handlers and zero `hx-on` attributes. Baseline and final full smoke pass; configured-auth and no-password isolated Chrome preserve shared shell, repeated dashboard/report and transaction/modal workflows, AI, CSRF, service worker, drawer and keyboard behavior with both runtime switches false, denied external requests, zero unexpected console/page errors, and exact all-entity cleanup. Python/JavaScript syntax, JSON, whitespace, dashboard refresh/health/rendered inspection, exact scope, and preserved-file checks pass locally. No commit, push, PR, merge, publication, deployment, protected data, credential, real database, external request, live action, vendored HTMX change, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-22-htmx-execution-switch-disablement-4ai.md`.

### Confirmed Work Block 4AI-R: Final HTMX Execution-Switch Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified.

Parent task: Phase 4 Task 1P.4.2b.3-R only.

Included: exact-path staging of the sixteen verified 4AI application, static-asset, maintained-test, CSP contract, issue, findings, evidence, and Runway OS paths; one intentional source commit on `codex/csp-htmx-disablement`; fast-forward local `main`; direct push to `origin/main` without force or PR; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; exact source-SHA verification; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source paths: `command-center/csp-compatibility-contract.md`; `command-center/decisions.md`; `command-center/index.html`; `command-center/issues.md`; `command-center/logs/2026-07-22-htmx-execution-switch-disablement-4ai.md`; `command-center/now.md`; `command-center/phase-3-findings-consolidation.md`; `command-center/roadmap.md`; `command-center/state.json`; `scripts/mobile_drawer_browser_test.py`; `scripts/smoke_test.py`; `web/static/dashboard-fragments.js`; `web/static/transaction-fragments.js`; `web/templates/base.html`; `web/templates/components/dashboard_body.html`; and `web/templates/components/txn_split_editor.html`.

Excluded: Task 1P.4.2c and later tasks; any new product, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, or Plaid mutation beyond the verified 4AI set; credentials; protected data; real databases; retained uploads; authenticated production pages; workflow edits, manual dispatches, or reruns; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and agent: Codex Desktop in the current task without delegation. Ryan explicitly authorized commit and direct push to `main`; no PR is used.

Defaults: explicit path staging only; preserve the verified false-switch result; observe only the automatic deployment and credential-free health; use `[skip actions]` only for the sanitized command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition; protected-boundary risk; failed maintained verification; excluded staging; local or remote `main` divergence; push rejection; automatic deployment or credential-free health failure requiring mutation; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact path and staged sets; high-confidence sensitive-addition and protected-path scans; full smoke; isolated-browser matrix; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and rendered inspection; commit content; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production health; final worktree and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with the exact commit/run/health result, align `state.json`, refresh and health-check, inspect the rendered closeout, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c still separately gated.

Result: exact sixteen-path source commit `3fb0d74966bed7806e13efa65e15609ff173e817` is durable on `main` and `origin/main`; automatic Fly Deploy run `29954953878` and deploy job `89041537857` passed for that exact SHA; credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-path, high-confidence sensitive-addition, maintained smoke, isolated-browser, syntax, JSON, whitespace, dashboard refresh/health/rendered-state, ancestry, remote-alignment, and preserved-exclusion checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, credential, protected data, real database, authenticated production page, downstream access/write, Task 1P.4.2c implementation, or preserved-file mutation occurred. This sanitized command-center-only closeout uses `[skip actions]`. Evidence: `command-center/logs/2026-07-22-htmx-execution-switch-disablement-release-4ai-r.md`.

### Confirmed Work Block 4AJ: Core Review-Page Execution

Status: complete and verified locally on `codex/csp-core-review-pages`; durability remains separate.

Parent tasks: Phase 4 Task 1P.4.2c.1 plus only its focused Task 2 regression slice.

Included: migrate the five executable inline scripts and eighteen native handlers in `components/sidebar.html`, `dashboard.html`, `reports.html`, `transactions.html`, and `todo.html` into the already-loaded shared, dashboard-fragment, and transaction-fragment static controllers; preserve sidebar controls, dashboard view switching and category popup, report export state, transaction sorting/filtering/copy/suggestion behavior, To Do modal behavior, repeated HTMX behavior, and the false HTMX execution-switch contract; add focused maintained synthetic and configured-auth/no-password isolated-browser coverage; and close Runway OS locally.

Excluded: Tasks 1P.4.2c.2-1P.4.2c.8; Tasks 1P.4.3-1P.7; the remainder of Task 2; Tasks 3-4; inline-style or runtime-style migration; CSP headers, nonces, or enforcement; Plaid; authentication; cookies; CSRF; service-worker or manifest changes; product, responsive, or financial behavior; new dependencies; credentials; protected data; real databases; retained uploads; external networking; production/demo inspection; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: all five surfaces are ordinary authenticated-shell review pages, reuse the three maintained static controller seams already loaded by `base.html`, and share one configured-auth/no-password browser matrix. Categorization/upload, planning, payroll, Plaid, subscriptions, and standalone documents have distinct mutation, risk, or verification paths and remain separate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. The deterministic migration couples shared controller behavior, local synthetic and isolated-browser proof, exact cleanup, scope control, and Runway OS stewardship. Ryan owns every scope expansion, publication, deployment, and live action.

Runner path: current Codex task on local branch `codex/csp-core-review-pages`.

Expected surfaces: the five included templates; `web/static/app-shell.js`, `web/static/dashboard-fragments.js`, and `web/static/transaction-fragments.js`; focused `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py` coverage; the CSP compatibility contract, sanitized evidence, issue/findings disposition only if affected, Runway OS source files, and generated dashboard. `base.html` remains unchanged unless the existing globally loaded asset contract is unexpectedly insufficient, which triggers a stop before widening scope.

Defaults: preserve visual and behavioral parity; reuse existing static assets and introduce no runtime dependency; keep `allowEval=false`, `allowScriptTags=false`, and `hx-on` at zero; use temporary synthetic Personal, BFM, and Luxe Legacy data, fake or empty integration configuration, localhost-only disposable browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; keep implementation local-only; preserve both unrelated untracked files.

Blocking questions: none. Ryan confirmed the base block without expansion.

Stop conditions: parity requires another Task 1P.4.2c route cluster, Task 1P.4.3 style work, CSP enforcement, authentication, Plaid, financial behavior, or a new dependency; an existing helper dependency requires cross-route migration beyond the five included surfaces; protected data, credentials, real databases, retained uploads, external/live access, another task, plan-changing verification failure, cleanup failure, command-center failure, or either preserved-file overlap appears.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused source and rendered-response assertions proving the five included surfaces contain zero executable inline scripts and zero native inline handlers while the aggregate residual inventory is exactly seventeen executable inline scripts, ninety-eight native handlers, two inert JSON carriers, and zero `hx-on`; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage for shared sidebar, dashboard, reports, transactions, To Do, repeated representative HTMX behavior, AI entry points, CSRF preservation, drawer/keyboard behavior, denied non-localhost requests, zero unexpected console/page errors, and exact all-entity cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AJ and Task 1P.4.2c.1 done and local-only; make Task 1P.4.2c.2 the next separate confirmation gate; align human-readable sources with `state.json`; refresh and health-check; inspect the generated state; and do not commit or publish.

Report point: return the exact behavior migrated, static-controller organization, zeroed included inventory and exact residual inventory, focused and full verification, changed paths, cleanup, preserved boundaries, local branch state, and separate publication plus Task 1P.4.2c.2 gates.

Suggested next work block: only after 4AJ closes cleanly, separately decide between 4AJ-R exact-scope durability/release and proposed 4AK for Task 1P.4.2c.2; neither is pre-authorized.

Result: the five included source templates now contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes. Existing static controllers own shared theme/brand/AI entry, dashboard view and popup, report type/export state, transaction filter/sort/copy/edit/suggestion behavior, and To Do modal/keyboard behavior; server-rendered URLs cross through inert `data-*` values. The maintained residual inventory is seventeen executable inline scripts, seven external scripts, two inert JSON carriers, ninety-eight native handlers, and zero `hx-on` attributes, while `allowEval=false` and `allowScriptTags=false` remain unchanged. Baseline and final full smoke plus configured-auth/no-password isolated Chrome pass representative included workflows, repeated HTMX behavior, denied external requests, zero unexpected console/page errors, and exact synthetic all-entity cleanup. JavaScript syntax, JSON, whitespace, dashboard refresh/health/generated-state inspection, exact scope, and preserved-file checks pass locally. No commit, push, PR, merge, publication, deployment, production/demo inspection, protected data, credential, real database, live action, dependency change, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-22-core-review-page-execution-4aj.md`.

### Confirmed Work Block 4AJ-R: Core Review-Page Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified.

Parent task: Phase 4 Task 1P.4.2c.1-R only.

Included: explicitly stage the exact verified 4AJ application, static-controller, maintained-test, CSP contract, evidence, and Runway OS paths; create one intentional source commit on `codex/csp-core-review-pages`; fast-forward local `main`; push directly to `origin/main` without force or PR; observe the resulting automatic Fly deployment read-only; verify credential-free production `/health`; verify exact source-SHA durability; and create and push one sanitized command-center-only `[skip actions]` closeout commit.

Excluded: Task 1P.4.2c.2 and later tasks; new product, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, or Plaid mutation beyond the verified 4AJ set; credentials; protected data; real databases; retained uploads; authenticated production pages; workflow edits, manual dispatches, or reruns; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and agent: Codex Desktop in the current task without delegation. Ryan explicitly authorized commit and direct push to `main`; no PR is used.

Defaults: explicit path staging only; preserve the verified false-switch behavior; observe only the automatic deployment and credential-free health; use `[skip actions]` only for the sanitized closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition; protected-boundary risk; failed maintained verification; excluded staging; local or remote `main` divergence; push rejection; automatic deployment or credential-free health failure requiring mutation; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; high-confidence sensitive-addition and protected-path scans; full smoke; isolated-browser matrix; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and generated state; commit content; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production health; final tracked cleanliness; and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with exact commit/run/health results, align `state.json`, refresh and health-check, inspect generated state, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.2 still separately gated.

Result: exact seventeen-path source commit `f8dfa803d0f7162240a8438fd53d8e0038966ee0` is durable on local and remote `main`; automatic Fly Deploy run `29959060928` and deploy job `89055358673` passed every reported step for that exact SHA; credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact changed and staged sets, protected-path and sensitive-addition scans, maintained smoke and isolated-browser suites, syntax, JSON, whitespace, dashboard refresh/health/generated state, commit contents, fast-forward, ancestry, remote alignment, automatic release, production health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, Task 1P.4.2c.2 implementation, broader recovery, or preserved-file mutation occurred. This sanitized command-center-only closeout uses `[skip actions]`. Evidence: `command-center/logs/2026-07-22-core-review-page-execution-release-4aj-r.md`.

### Confirmed Work Block 4AK: Categorization And Upload Execution

Status: complete and verified locally on `codex/csp-categorization-upload`; durability remains separate.

Parent tasks: Phase 4 Task 1P.4.2c.2, Task 1P.5, and only their focused Task 2 regression slices.

Included: move three executable inline scripts and seven native handlers from `categorize.html`, `categorize_orphans.html`, and `upload.html` into one maintained local static controller; preserve alias prefill, category/subcategory loading, orphan reassignment controls, upload month navigation, and destructive confirmations; relabel status-only Upload `Undo` as `Mark incomplete` with explicit confirmation that imported transactions remain; add focused maintained synthetic and configured-auth/no-password isolated-browser coverage; reconcile the CSP inventory, issue state, sanitized evidence, and Runway OS; and close locally.

Excluded: Tasks 1P.4.2c.3-1P.4.2c.8; Tasks 1P.4.3-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; inline-style or runtime-style migration; CSP headers, nonces, or enforcement; Plaid; authentication; cookies; CSRF changes; service-worker or manifest changes; categorization, import, deletion, product, responsive, or financial-logic changes beyond the confirmed status-only wording; new dependencies; credentials; protected data; real databases; retained uploads; external networking; production/demo inspection; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: all included execution lives on the categorization and upload route family, shares one ordinary authenticated-shell lifecycle, and can use one focused synthetic and isolated-browser verification matrix. Task 1P.5 touches the same Upload control and has an already-settled status-only contract. Cash-flow/planning contains forty-seven handlers and an inert JSON carrier, and later clusters have separate payroll, Plaid, subscription, or standalone-document boundaries.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns the deterministic static-controller migration, exact browser behavior, synthetic data isolation, cleanup, issue disposition, inventory reconciliation, and Runway OS stewardship. Ryan owns expansion, publication, deployment, and live actions.

Runner path: current Codex task on local branch `codex/csp-categorization-upload`.

Expected surfaces: `web/templates/categorize.html`, `web/templates/categorize_orphans.html`, `web/templates/upload.html`, `web/templates/base.html`, a dedicated `web/static/categorization-upload.js`, focused `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py` coverage, the CSP compatibility contract, `command-center/issues.md`, sanitized evidence, Runway OS sources, and generated dashboard.

Defaults: preserve visual and behavioral parity; use delegated listeners and inert `data-*` route values in a template-free static controller; introduce no runtime dependency; keep `allowEval=false`, `allowScriptTags=false`, and `hx-on` at zero; use `Mark incomplete` plus confirmation that imported transactions remain for Task 1P.5; use temporary synthetic Personal, BFM, and Luxe Legacy data, both authentication modes, localhost-only disposable browser state, denied external requests, zero unexpected console/page errors, and exact cleanup; keep implementation local-only; preserve both unrelated untracked files.

Blocking questions: none. Ryan confirmed the expanded block and its recommended wording defaults.

Stop conditions: parity requires categorization, import, deletion, or true-reversal business-logic changes; another Task 1P.4.2c route cluster, style work, CSP enforcement, authentication, Plaid, product/financial behavior, or a new dependency is required; protected data, credentials, real databases, retained uploads, external/live access, another task, plan-changing verification failure, cleanup failure, command-center failure, or either preserved-file overlap appears.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused source and rendered-response assertions proving the three included templates contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` while the aggregate residual inventory is exactly fourteen executable inline scripts, eight external scripts including the new maintained controller, two inert JSON carriers, ninety-one native handlers, and zero `hx-on`; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage for alias prefill, category/subcategory loading, orphan reassignment controls, upload month navigation, deletion confirmations, status-only `Mark incomplete`, denied non-localhost requests, zero unexpected console/page errors, and exact all-entity cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AK, Task 1P.4.2c.2, Task 1P.5, and their focused Task 2 slices done locally; make separate 4AK-R durability/release versus Task 1P.4.2c.3 re-sizing the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated behavior, controller organization, Task 1P.5 wording, included and residual inventories, focused and full verification, cleanup, changed paths, local branch state, preserved exclusions, and separate 4AK-R plus Task 1P.4.2c.3 gates.

Suggested next work block: separately decide whether to authorize 4AK-R exact-scope durability/release; after durability, re-size Task 1P.4.2c.3 before proposing 4AL. Neither is pre-authorized.

Result: the three included templates now contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes. The dedicated template-free controller owns category/subcategory loading, orphan reassignment controls, alias prefill, upload month navigation, and included confirmations. `Undo` is now `Mark incomplete`; the confirmation says imported transactions remain, and maintained request proof resets checklist status without changing the transaction count. The aggregate inventory is fourteen executable inline scripts, eight external executable scripts, two inert JSON carriers, ninety-one native handlers, and zero `hx-on`, while both HTMX execution switches remain false. Baseline and final full smoke plus configured-auth/no-password isolated Chrome pass with denied external requests, zero unexpected console/page errors, and exact synthetic cleanup. Syntax, JSON, whitespace, dashboard refresh/health/generated state, exact scope, and preserved-file checks pass. No commit, push, PR, publication, deployment, protected data, credential, real database, external/live action, later route-cluster work, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-22-categorization-upload-execution-4ak.md`.

### Confirmed Work Block 4AK-R: Categorization And Upload Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified.

Parent task: Phase 4 Task 1P.4.2c.2-R for the exact verified 4AK source set only.

Included: explicitly stage the exact fifteen verified 4AK application, static-controller, maintained-test, CSP contract, issue, evidence, and Runway OS paths; create one intentional source commit on `codex/csp-categorization-upload`; fast-forward local `main`; push directly to `origin/main` without force or PR; observe the resulting automatic Fly deployment read-only; verify credential-free production `/health`; verify exact source-SHA durability; and create and push one sanitized command-center-only `[skip actions]` closeout commit.

Excluded: Task 1P.4.2c.3 and later tasks; any new product, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, or Plaid mutation beyond the verified 4AK set; credentials; protected data; real databases; retained uploads; authenticated production pages; workflow edits, manual dispatches, or reruns; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly requested commit and push to `main`. The complete 4AK source is already locally verified, so exact durability, automatic release observation, credential-free health, and sanitized closeout form one bounded release path without reopening implementation.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only automatic deployment observation, credential-free health, and Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and Task 1P.4.2c.3 decision.

Defaults: no PR or force push; exact-path staging only; preserve the verified controller, status-only wording, false HTMX execution switches, maintained proof, and both unrelated untracked files; use only the automatic `main` deployment; inspect no authenticated production page; make no manual workflow or Fly mutation; use `[skip actions]` only for the final sanitized closeout.

Stop conditions: unexpected or excluded path; sensitive addition or protected-data risk; failed maintained verification; local or remote `main` divergence; excluded staging; push rejection; automatic deployment failure requiring mutation; credential-free health failure; workflow behavior inconsistent with the expected automatic release; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; high-confidence sensitive-addition and protected-path checks; full smoke; configured-auth/no-password isolated-browser matrix; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and rendered state; commit content; clean fast-forward; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production `/health`; final tracked cleanliness; and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with exact commit/run/health results, align `state.json`, refresh and health-check, inspect generated state, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.3 still separately gated.

Result: exact fifteen-path source commit `85a42ec8abe3f5abbbc5fb783658ca2e1bc7129e` is durable on local and remote `main`. Automatic Fly Deploy run `29974641835` and deploy job `89103727566` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, rendered-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, later route-cluster work, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.3 remains separately gated. Evidence: `command-center/logs/2026-07-22-categorization-upload-execution-release-4ak-r.md`.

### Confirmed Work Block 4AL: Cash Flow And Long-Term Planning Execution

Status: complete and locally verified; not committed or published

Parent tasks: Phase 4 Tasks 1P.4.2c.3a-1P.4.2c.3b plus only their focused Task 2 regression slices.

Included: move the one executable inline script and fifteen native handlers from `cashflow.html` plus the one executable inline script and ten native handlers from `planning.html` into maintained page-owned local controllers; preserve account/card opening, modal population, input sizing, due-day parsing, recurring-entry setup, asset/liability add/edit/delete, source switching, birthday editing, projections, confirmations, scrim/Escape closure, AI entry, Personal/BFM sharing, Luxe Legacy boundaries, and existing product behavior; add focused maintained synthetic and configured-auth/no-password isolated-browser proof; reconcile the CSP inventory, sanitized evidence, and Runway OS; and close locally after verification.

Excluded: Task 1P.4.2c.3c; Tasks 1P.4.2c.4-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route or financial-business-logic changes; style migration; CSP headers, nonces, or enforcement; Plaid; authentication; dependencies; credentials; protected data; real databases; retained uploads; external or live access; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Cash Flow and Long-Term Planning share the cash-flow-account linkage, Personal/BFM planning model, card/modal interaction risk, static-controller migration pattern, and one synthetic/browser verification path. Short-Term Planning carries a distinct inert-data, goal, budget, action-item, fetch, and dynamic transaction-edit surface and remains separate.

Expansion candidates: none. Short-Term Planning and Weekly/Waterfall introduce different verification paths and remain separately gated.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, exact-scope verification, synthetic cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every scope expansion, publication, deployment, protected-access, and live-action decision.

Runner path: create local branch `codex/csp-cashflow-long-term-planning`; keep the result local-only with no commit, push, PR, merge, publication, deployment, or production inspection.

Expected surfaces: `web/templates/cashflow.html`, `web/templates/planning.html`, dedicated page-owned static controllers such as `web/static/cashflow.js` and `web/static/planning.js`, focused `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py` coverage, `command-center/csp-compatibility-contract.md`, one sanitized 4AL evidence log, Runway OS sources, and the generated dashboard. Route files are inspection-only unless an unexpected requirement triggers a stop.

Defaults: use delegated listeners and inert `data-*` values; keep the two controllers page-owned rather than creating a cross-page abstraction absent a clear source need; keep `allowEval=false`, `allowScriptTags=false`, and `hx-on` at zero; preserve runtime style behavior for the separately gated style task; use temporary synthetic Personal, BFM, and Luxe Legacy data; deny non-localhost browser traffic; require zero unexpected browser errors and exact cleanup; and preserve both unrelated untracked files.

Stop conditions: parity requires route or financial-business-logic changes, Short-Term Planning, another route cluster, style or CSP enforcement, Plaid, authentication, a dependency, credentials, protected data, real databases, retained uploads, external/live access, or a product decision; verification changes the plan; exact cleanup fails; command-center refresh or health fails; scope expands; or either preserved file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving both included templates contain zero executable inline scripts, zero native inline handlers, and zero `hx-on`; aggregate residual inventory of twelve executable inline scripts, ten external executable assets, two inert JSON carriers, sixty-six native handlers, and zero `hx-on`; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` covering account/card modals, balance/card fields, due-day handling, item add/edit/delete confirmation, source switching, birthday save, Escape/scrim closure, projections, AI entry, entity boundaries, denied external requests, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON; `git diff --check`; dashboard refresh, health, and rendered-state inspection; exact scope; and both preserved untracked files.

Dashboard closeout: mark Tasks 1P.4.2c.3a-1P.4.2c.3b and 4AL complete locally; make separate 4AL-R durability/release and Task 1P.4.2c.3c recheck the next Ryan gates; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated behavior, controller organization, included and residual inventories, focused and full verification, cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AL-R publication plus Task 1P.4.2c.3c gates.

Suggested next block: separately decide whether to authorize 4AL-R exact-scope durability/release; after durability, recheck Task 1P.4.2c.3c before proposing 4AM. Neither is pre-authorized.

Result: the two included templates contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes. Separate page-owned `cashflow.js` and `planning.js` controllers preserve the included workflows through delegated listeners and inert `data-*` values. The residual inventory is twelve executable inline scripts, ten external executable assets, two inert JSON carriers, sixty-six native handlers, and zero `hx-on`; both HTMX execution switches remain false. Full synthetic smoke and configured-auth/no-password isolated Chrome pass with denied external requests, zero unexpected console/page errors, and exact temporary all-entity cleanup. Focused source/rendered assertions, Python and JavaScript syntax, JSON, whitespace, dashboard refresh/health, rendered application/dashboard inspection, exact scope, and preserved-file checks pass. No route, financial, Short-Term Planning, style, CSP-header, Plaid, authentication, dependency, protected-data, real-database, external/live, GitHub, publication, deployment, downstream, or preserved-file mutation occurred. The result remains uncommitted on `codex/csp-cashflow-long-term-planning`; 4AL-R and Task 1P.4.2c.3c remain separate Ryan gates. Evidence: `command-center/logs/2026-07-22-cashflow-long-term-planning-execution-4al.md`.

### Confirmed Work Block 4AL-R: Cash Flow And Long-Term Planning Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified

Parent task: Phase 4 Task 1P.4.2c.3-R only.

Included: stage the exact thirteen verified 4AL application, controller, maintained-test, CSP contract, evidence, and Runway OS source paths; create one intentional source commit on `codex/csp-cashflow-long-term-planning`; fast-forward local `main`; push directly to `origin/main` without force or PR; observe the resulting automatic Fly deployment read-only; verify credential-free production `/health`; verify the exact source SHA is durable; create one sanitized command-center-only `[skip actions]` closeout commit; push it to `main`; and prove final local/remote alignment.

Excluded: Task 1P.4.2c.3c and every later task; every new application, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, Plaid, route, or financial mutation beyond the verified 4AL set; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly requested commit and push to `main`. The complete 4AL set is already locally verified, so exact durability, automatic release observation, credential-free health, and sanitized closeout form one bounded publication block without reopening implementation.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only automatic-deployment observation, credential-free health, and Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and Task 1P.4.2c.3c decision.

Runner path: source commit on `codex/csp-cashflow-long-term-planning`; clean fast-forward of local `main`; direct push to `origin/main`; automatic-deployment observation; credential-free health; sanitized `[skip actions]` closeout on `main`.

Expected surfaces: the exact thirteen verified 4AL paths for the source commit; then only `command-center/now.md`, `command-center/roadmap.md`, `command-center/decisions.md`, `command-center/state.json`, generated `command-center/index.html`, and one sanitized 4AL-R evidence log for closeout.

Defaults: explicit-path staging only; no PR or force push; no new application mutation; preserve the verified controllers, tests, inventory, and false HTMX execution switches; observe only the automatic `main` deployment and credential-free health; use `[skip actions]` only for the final command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition or protected-data risk; failed verification; local or remote `main` divergence; excluded staging; push rejection; automatic deployment or health failure that requires mutation or broader diagnosis; workflow behavior inconsistent with the expected automatic release; preserved-file overlap; or recovery beyond clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-path and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and rendered state; commit content; clean fast-forward; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production `/health`; final tracked cleanliness; and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with exact commit/run/health results, align `state.json`, refresh and health-check, inspect generated state, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.3c still separately gated.

Suggested next work block: after 4AL-R closes, recheck Task 1P.4.2c.3c before proposing a separate high-interaction block; do not infer implementation authorization.

Result: exact thirteen-path source commit `62fab2655856e8a076aaff1eacd8a43bb7421132` is durable on local and remote `main`. Automatic Fly Deploy run `29991146113` and deploy job `89154057052` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, rendered-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, Short-Term Planning work, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.3c remains separately gated. Evidence: `command-center/logs/2026-07-23-cashflow-long-term-planning-execution-release-4al-r.md`.

### Confirmed Work Block 4AM-R: Short-Term Planning Durability And Release

Status: active.

Parent task: Phase 4 Task 1P.4.2c.3c-R for the exact verified 4AM source set only.

Included: stage the exact twelve verified 4AM application, controller, maintained-test, CSP contract, evidence, and Runway OS source paths; create one intentional source commit on `codex/csp-short-term-planning`; fast-forward local `main`; push directly to `origin/main` without force or PR; observe the resulting automatic Fly deployment read-only; verify credential-free production `/health`; verify the exact source SHA is durable; create one sanitized command-center-only `[skip actions]` closeout commit; push it to `main`; and prove final local/remote alignment.

Excluded: Task 1P.4.2c.4 and every later task; every new application, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, Plaid, route, database-query, or financial mutation beyond the verified 4AM set; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly requested commit and push to `main`. The complete 4AM set is already locally verified, so exact durability, automatic release observation, credential-free health, and sanitized closeout form one bounded publication block without reopening implementation.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only automatic-deployment observation, credential-free health, and Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and Task 1P.4.2c.4 decision.

Runner path: source commit on `codex/csp-short-term-planning`; clean fast-forward of local `main`; direct push to `origin/main`; automatic-deployment observation; credential-free health; sanitized `[skip actions]` closeout on `main`.

Expected surfaces: the exact twelve verified 4AM paths for the source commit; then only `command-center/now.md`, `command-center/roadmap.md`, `command-center/decisions.md`, `command-center/state.json`, generated `command-center/index.html`, and one sanitized 4AM-R evidence log for closeout.

Defaults: explicit-path staging only; no PR or force push; no new application mutation; preserve the verified controller, response markup, tests, inventory, and false HTMX execution switches; observe only the automatic `main` deployment and credential-free health; use `[skip actions]` only for the final command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition or protected-data risk; failed verification; local or remote `main` divergence; excluded staging; push rejection; automatic deployment or health failure that requires mutation or broader diagnosis; workflow behavior inconsistent with the expected automatic release; preserved-file overlap; or recovery beyond clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-path and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python and JavaScript syntax; JSON; whitespace; dashboard refresh, health, and rendered state; commit content; clean fast-forward; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production `/health`; final tracked cleanliness; and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with exact commit/run/health results, align `state.json`, refresh and health-check, inspect generated state, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.4 still separately gated.

Suggested next work block: after 4AM-R closes, recheck Task 1P.4.2c.4 before proposing a separate Weekly/Waterfall block; do not infer implementation authorization.

### Confirmed Work Block 4AF-R: Shared CSP Execution Foundation Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified

Parent task: Phase 4 Task 1P.4.2a-R only.

Included: stage the exact fifteen verified 4AF application, static-asset, maintained-test, CSP contract, issue, findings, evidence, and Runway OS paths; create one intentional source commit on `codex/csp-shared-execution-foundation`; fast-forward local `main`; push directly to `origin/main` without force or PR; observe the resulting automatic Fly deployment read-only; verify credential-free production `/health`; verify the exact source SHA is durable; create one sanitized command-center-only `[skip actions]` closeout commit; push it to `main`; and prove final local/remote alignment.

Excluded: Task 1P.4.2b and later Task 1P work; all new application, template, JavaScript, CSS, test, dependency, runtime, authentication, cookie, CSRF, header, Plaid, service-worker, manifest, worker, responsive, or financial behavior changes; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow dispatches or reruns; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly requested commit and push to `main`. The complete 4AF set is already locally verified, so durability, automatic release observation, credential-free health, and sanitized closeout form one bounded publication block without reopening implementation.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only deployment observation, credential-free health, and Runway OS closeout. Ryan owns every scope expansion, live mutation, failure recovery, and Task 1P.4.2b decision.

Defaults: no PR or force push; exact-path staging only; preserve the verified temporary HTMX compatibility settings; use the automatic `main` deployment only; inspect no authenticated production page; make no manual workflow or Fly mutation; use `[skip actions]` only for the final command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition or protected-data risk; failed verification; local or remote `main` divergence; excluded staging; push rejection; automatic deployment failure that would require mutation; credential-free health failure; workflow behavior inconsistent with the expected automatic release; preserved-file overlap; or recovery beyond clean fast-forward and read-only diagnosis.

Verification: exact path and staged sets; high-confidence sensitive-addition and protected-path checks; maintained full synthetic smoke and isolated-browser shared-shell suites; Python and JavaScript syntax; JSON; whitespace; dashboard refresh, health, and rendered state; commit content; clean fast-forward; main ancestry; exact remote SHA; automatic deployment run and job result; credential-free production `/health`; final tracked cleanliness; and preserved untracked files.

Report point: return source and closeout SHAs, exact published paths, deployment run and job result, production-health result, final local/remote alignment, preserved exclusions, and Task 1P.4.2b still separately gated.

Suggested next work block: after 4AF-R closes, run the separate just-in-time sizing pass for Task 1P.4.2b; do not infer implementation authorization.

Result: exact fifteen-path source commit `80dd7761c13cc9da94e9a26a8326871622734be6` is durable on `main`; automatic Fly Deploy run `29873831453` and deploy job `88779843248` passed for that exact SHA; and credential-free production `/health` returned HTTP 200. Exact-path, protected-path, high-confidence sensitive-addition, maintained smoke, isolated-browser, syntax, JSON, whitespace, dashboard, health, rendered-state, ancestry, and remote-alignment checks passed. No PR, force push, protected data, credential, authenticated production page, manual workflow, non-automatic Fly mutation, Task 1P.4.2b implementation, or preserved untracked-file change occurred. Evidence is recorded in `command-center/logs/2026-07-21-shared-csp-execution-foundation-release-4af-r.md`.

### Confirmed Work Block 4AF: Shared CSP Execution Foundation

Status: complete and verified locally

Parent task: Phase 4 Task 1P.4.2a only.

Included: record 4AF as active before product work; create `codex/csp-shared-execution-foundation`; move the six executable inline application blocks, five native inline event handlers, and two `hx-on` handlers in `web/templates/base.html` into maintained local static JavaScript and delegated/HTMX event listeners; carry shared server-rendered values through inert data or attributes; move HTMX indicator rules into tracked local CSS; establish declarative HTMX configuration and set only `includeIndicatorStyles=false`; preserve current `allowEval` and `allowScriptTags` values until Task 1P.4.2b removes their remaining fragment dependencies; add focused maintained synthetic and isolated-browser coverage for shared-shell behavior; reconcile the 4AE contract, findings, issue state, README only if the maintained application surface changes, and Runway OS; and close locally after full verification.

Excluded: Tasks 1P.4.2b-1P.7; remaining page and fragment executable scripts or handlers; global `allowEval=false` or `allowScriptTags=false`; inline style attributes or blocks outside the exact HTMX indicator extraction; Flask CSP or nonce headers; route-family policy enforcement; Plaid entry-page behavior; login, offline/error, standalone `/k/`, service-worker, manifest, public-route, authentication, cookie, CSRF, or responsive-design contract changes; new runtime dependencies; credentials; protected data; real databases; retained uploads; external networking; production/demo inspection; GitHub durability; publication; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the shared shell is the dependency-first execution surface for every inherited page and provides the local initializer/event/configuration foundation later fragment and page migrations will reuse. Keeping HTMX eval and swapped scripts temporarily enabled avoids breaking known fragment dependencies before Task 1P.4.2b can remove and prove them.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns implementation, synthetic/browser verification, scope review, and Runway OS closeout. Ryan owns scope changes, reviewer choice, publication, and live actions.

Defaults: preserve visual and behavioral parity; use maintained local static JavaScript with event delegation and `htmx:load` where shared behavior must survive swaps; use inert data rather than executable templating; add no framework or runtime dependency; set only HTMX `includeIndicatorStyles=false`; maintain explicit focused assertions that `allowEval` and `allowScriptTags` remain temporarily enabled because Task 1P.4.2b still owns their removal; use temporary synthetic all-entity databases, fake/empty integration configuration, localhost only, denied non-localhost requests, disposable browser state, and exact cleanup; keep durability local-only.

Stop conditions: shared-shell behavior cannot be preserved without reaching a fragment or page outside Task 1P.4.2a; disabling eval or swapped-script processing becomes necessary before remaining dependencies migrate; a broader style or design change is required; a new runtime dependency, authentication/security policy change, protected/live access, another Task 1P item, external request, plan-changing verification failure, cleanup failure, command-center failure, or preserved-file overlap appears.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused maintained shared-shell request/source assertions; maintained isolated-Chrome coverage for configured-auth and no-password modes, desktop, phone, and exact responsive boundary behavior, repeated representative HTMX swaps, theme, navigation/drawer, AI chat, service-worker registration contract, CSRF/HTMX headers, denied external requests, console/page errors, and cleanup; explicit remaining-dependency assertion for temporary HTMX eval/script settings; relevant Python/JavaScript syntax; `jq empty command-center/state.json`; dashboard refresh and health; `git diff --check`; rendered-dashboard inspection; exact-path/product-boundary review; and preserved untracked-file confirmation.

Dashboard closeout: update maintained human-readable sources first, align `state.json`, refresh and health-check, inspect the rendered current task/work block/owner/next action, and leave fragment/page/style/header, publication, and live work separately gated.

Report point: return the exact shared behaviors migrated, local asset/config structure, temporary HTMX dependency assertion, focused and full verification results, changed paths, residual 1P.4.2b dependencies, local-only durability, and a separately confirmable next block.

Suggested next work block: only after 4AF closes, size Task 1P.4.2b from the verified fragment inventory; do not pre-authorize it.

Result: `base.html` no longer contains executable inline application blocks, native inline event handlers, or `hx-on` handlers. Maintained local theme and application-shell assets preserve the shared behavior, HTMX indicator CSS is local with only injected indicators disabled, and explicit compatibility settings retain eval and swapped scripts until Task 1P.4.2b. Full synthetic and isolated-browser verification passed. The remaining tracked-template inventory is 32 executable inline scripts, 156 native inline handlers, and two fragment `hx-on` attributes. Evidence is recorded in `command-center/logs/2026-07-21-shared-csp-execution-foundation-4af.md`; durability remains local-only.

### Confirmed Work Block 4AE: CSP Compatibility Contract And Migration Matrix

Status: complete and verified locally

Parent task: Phase 4 Task 1P.4.1 only.

Included: inventory every executable-script, HTMX fragment, inline-style, local-asset, worker/manifest, login, offline/error, standalone `/k/`, and Plaid Link dependency; define exact candidate CSP directives and allowed origins; classify every required rewrite; specify the synthetic header and isolated-browser verification matrix; write one sanitized repo-backed compatibility contract and evidence log; and close Runway OS locally.

Excluded: Tasks 1P.4.2-1P.7; the remainder of Task 2; Tasks 3-4; all product, template, JavaScript, CSS, maintained-test, dependency, authentication, cookie, CSRF, security-header, public-route, manifest, service-worker, or Plaid behavior changes; credentials; protected data; real databases; retained uploads; production or demo inspection; live traffic; external actions beyond read-only official public documentation; GitHub durability; publication; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the block has one planning-and-evidence outcome, one read-only source model, one sanitized artifact set, and one Runway OS verification path. Executable-markup migration, style/document refactoring, and CSP enforcement depend on this contract and require separate mutation and verification blocks.

Owner and recommended agent: Codex Desktop in the current task without delegation. The block requires cross-template inspection, security-policy synthesis, task sizing, and command-center stewardship. Codex owns the contract, matrix, verification, dashboard currency, and final intake; Ryan owns all product-policy, reviewer, implementation, publication, and live-action decisions.

Defaults: target no `unsafe-eval` and no executable inline event attributes; prefer local scripts and request-scoped nonces over broad script exceptions; treat inline-style policy as an explicit decision rather than an automatic blanket allowance; use exact Plaid origins and tracked environment behavior without opening Link live; carry server-rendered values through inert JSON or data attributes in later work; split Tasks 1P.4.2 or 1P.4.3 further if the matrix shows either remains too broad; keep durability local-only; and make no product or maintained-test change.

Stop conditions: a product or UX decision is required before the candidate contract can be stated; exact compatibility cannot be established without credentials, protected data, real databases, or live traffic; product or test changes become necessary; official public requirements conflict with tracked behavior; scope reaches another task or subsystem; either preserved untracked file would be touched; or dashboard refresh or health check cannot pass.

Verification: complete file-to-directive and rewrite-to-task matrices; explicit candidate directives, origins, compatibility blockers, and Ryan decisions; no product, test, dependency, configuration, or runtime diff; `jq empty command-center/state.json`; `node command-center/scripts/refresh-dashboard.js`; `node command-center/scripts/health-check.js`; `git diff --check`; rendered-dashboard inspection; and final scoped worktree review. The full application smoke suite is intentionally skipped because 4AE changes no application behavior.

Dashboard closeout: update human-readable sources first, align `state.json`, add the contract and evidence, refresh and health-check the dashboard, inspect the rendered current phase/task/work block/owner/next action, and leave every implementation and durability step separately gated.

Report point: return the candidate CSP, exact allowances, compatibility blockers, migration counts and proposed implementation slices, reviewer recommendation, unresolved Ryan decisions, changed command-center paths, verification results, local-only durability, and one separately confirmable next block.

Result: `command-center/csp-compatibility-contract.md` now freezes strict core and narrow Plaid policies, exact origins, the template/resource inventory, rewrite-to-task slices, prohibited exceptions, and a maintained synthetic request/isolated-browser proof contract. HTMX fragment execution and Plaid's document-specific style exception are explicit sequencing constraints. Tasks 1P.4.2 and 1P.4.3 are decomposed into bounded sub-slices. No product or maintained-test change occurred.

Suggested next work block: 4AF for Task 1P.4.2a only after Ryan approves the contract or requests an independent review. Do not infer implementation authorization from completed 4AE planning.

### Confirmed Work Block 4AD: Mobile Drawer Accessibility And Responsive Coverage

Status: complete and verified locally

Parent tasks: Phase 4 Task 1P.3 and only the responsive-navigation slice of Task 2 finding `P3-3J-C01`.

Included: keep closed mobile drawer content out of normal keyboard and assistive navigation; synchronize hamburger, drawer, and scrim state; move focus into the opened drawer; contain focus while open; restore focus on non-navigation close; close on Escape and scrim; lock background scrolling only while open; preserve route and entity-submit navigation; clean up state across breakpoint changes; add focused maintained isolated-browser coverage; reconcile maintained documentation and issue state; and close Runway OS locally after verification.

Excluded: Tasks 1P.4-1P.7; the remainder of Task 2; Tasks 3-4; CSP; Upload copy; manifest, icon, service-worker, offline, configured-auth, exact `/k/`, and generalized browser/PWA coverage; broad financial read-model coverage; migrations; credentials; protected data; real databases; production inspection; external networking; live actions; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the drawer repair and its responsive coverage share one template, CSS, JavaScript, accessibility contract, isolated-browser setup, risk class, and verification path. CSP, broader PWA coverage, Upload copy, and financial read models require separate decisions or subsystems.

Owner and runner: Codex Desktop in the current task on `codex/mobile-drawer-accessibility`; no delegation or second opinion. Codex owns implementation, focused browser-test setup, verification, cleanup, issue disposition, dashboard currency, and final intake. Prefer a development-only browser dependency surface if required and do not expand production dependencies by default.

Defaults: mobile means the maintained `max-width: 768px` breakpoint; focus the first usable primary navigation link on open; contain Tab focus while open; restore focus for Escape, scrim, or toggle closure but not during route or form navigation; clear transient drawer state at the desktop transition while preserving the now-persistent sidebar; use explicit ARIA/control and closed-state semantics; lock body scrolling only while open; leave desktop behavior and visual design unchanged except focused accessibility styling; use synthetic temporary data, disposable browser state, localhost, and denied outbound networking; and keep durability local-only.

Stop conditions: a broader navigation redesign, CSP or authentication change, generalized PWA/browser infrastructure, new production dependency, protected data, credentials, external or live access, another Task 1P item, plan-changing verification failure, failed cleanup, command-center failure, or overlap with either preserved untracked file.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused maintained isolated-browser checks at phone and breakpoint-adjacent widths covering closed/open semantics, focus placement and containment, restoration, Escape, scrim, body scroll lock, route/entity actions, and resize cleanup; temporary synthetic all-entity data; disposable browser state; denied outbound networking; exact cleanup; Python and relevant test-script validation; JSON validation; `git diff --check`; dashboard refresh and health; rendered-dashboard inspection; and final scoped worktree review.

Dashboard closeout: update human-readable sources first, align `state.json`, refresh the dashboard, run health check, inspect the generated dashboard and relevant diff, and leave publication separately gated.

Report point: return the exact drawer contract, focused and full test results, browser/runtime setup, changed paths, cleanup proof, issue disposition, preserved exclusions, local branch state, and readiness or blocker for a separately confirmed release block.

Suggested next work block: 4AD-R exact-scope durability and automatic release only if separately authorized; otherwise plan 4AE for Task 1P.4 CSP compatibility.

### Confirmed Work Block 4AD-R: Mobile Drawer Accessibility Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified

Parent task: Phase 4 Task 4 for the exact verified 4AD source set only.

Included: the exact verified fifteen-path 4AD application, template, CSS, maintained browser test, development-only dependency surface, README, contract, issue, findings, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/mobile-drawer-accessibility`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; protected data; real financial rows or databases; retained uploads; credentials; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly changes; external calls other than GitHub/Fly status and credential-free health; downstream access or writes; migrations; Tasks 1P.4-1P.7; broader Task 2; unrelated repairs; PR creation; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop in the current task without delegation or PR. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly attribution, credential-free health verification, and final Runway OS closeout.

Defaults: preserve the verified 4AD drawer and browser-test contract; no PR because Ryan directly instructed commit and push to `main`; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1P.4 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic smoke and focused isolated-browser coverage; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1P.4 planning gate.

Result: the exact fifteen-path 4AD source set was committed as `0459372`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force or PR. Automatic Fly Deploy run `29855162229` and deploy job `88717551145` passed for exact source SHA `0459372abdc8bbc7ce29f4288430446aa5661b21`, and credential-free production `/health` returned HTTP 200. Exact-path, protected-path, high-confidence sensitive-pattern, staged-set, ancestry, remote-alignment, maintained smoke, isolated-browser, compilation, JSON, whitespace, dashboard refresh, and health checks passed. Both preserved untracked files remained excluded; GitHub's non-blocking Node 20 deprecation annotation did not affect deployment; and this sanitized command-center-only closeout uses `[skip actions]` to prevent a second deployment. Task 1P.4 returns as the separate planning gate. Evidence: `command-center/logs/2026-07-21-mobile-drawer-accessibility-release-4ad-r.md`.

Result: the hamburger now explicitly controls `sidebar-nav`; closed mobile navigation is assistive-hidden and inert; opening synchronizes state, focuses Dashboard, contains Tab focus, shows the scrim, and locks body scroll; Escape, scrim, and toggle closure restore the hamburger; route and entity-submit navigation close without stale focus restoration; and the exact `768px` to `769px` transition clears transient state while preserving desktop navigation. A maintained Playwright check uses the installed Chrome channel, temporary synthetic all-entity databases, fake or empty integration configuration, localhost only, denied non-localhost requests, disposable browser state, console-error detection, and exact cleanup. Baseline and final full smoke suites, the focused browser matrix, compilation, JSON, whitespace, dashboard refresh, health, rendered inspection, and scope review pass locally. The first browser run caught a missing visual scrim display after semantic refactoring; explicit visible-scrim CSS fixed it before the full matrix passed. No excluded or live action occurred, both preserved untracked files remain untouched, and publication is not authorized. Evidence: `command-center/mobile-drawer-accessibility-contract.md` and `command-center/logs/2026-07-21-mobile-drawer-accessibility-4ad.md`.

### Confirmed Work Block 4AC-R: Session-Cookie Policy Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified

Parent task: Phase 4 Task 4 for the exact verified 4AC source set.

Included: the exact verified twelve-path 4AC application, maintained-test, README, contract, issue, findings, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/session-cookie-policy`; fast-forward local `main`; direct push to `origin/main` without force; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; protected data; real databases; retained uploads; credentials; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Tasks 1P.3-1P.7; broader Task 2; unrelated work; PR creation; force push; and recovery beyond the exact fast-forward path.

Owner and runner: Codex Desktop in the current task. No PR because Ryan directly instructed commit and push to `main`; no delegation or second opinion.

Stop conditions: unexpected paths, sensitive additions, protected data, unrelated changes, local or remote `main` divergence, failed maintained verification, excluded staging, unattributable or failed automatic deployment, failed credential-free health, a second closeout deployment, or recovery beyond the authorized fast-forward path.

Verification: exact path and staged-set review; high-confidence sensitive-addition scan; branch ancestry and remote alignment; maintained synthetic smoke; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; source commit; direct-main fast-forward push; exact automatic Fly run and job attribution; credential-free production `/health`; final `main` alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and separate Task 1P.3 planning gate.

Result: exact twelve-path source commit `07c2026` was fast-forwarded and pushed directly to `main` without force or PR. Automatic Fly Deploy run `29851220888` and deploy job `88704299424` passed for exact source SHA `07c20265b359f52262ecba6447a24b71a6290eea`, and credential-free production `/health` returned HTTP 200. The staged high-confidence sensitive-addition and protected-path scans returned zero; both preserved untracked files remained excluded; GitHub's non-blocking Node 20 deprecation annotation did not affect deployment; and this sanitized command-center-only closeout uses `[skip actions]` to prevent a second deployment. Task 1P.3 returns as the separate planning gate.

### Confirmed Work Block 4AC: Explicit Session-Cookie Policy

Status: complete and verified locally

Parent tasks: Phase 4 Task 1P.2 and only the focused Task 2 coverage for the cookie half of `P3-3J-06`.

Included: make the Flask session cookie explicitly `HttpOnly` and `SameSite=Lax` everywhere; make it `Secure` on Fly through the infrastructure-provided `FLY_APP_NAME` signal while preserving ordinary local HTTP and controlled synthetic-test usability; preserve the host-only, application-root, non-permanent session, cookie name, configured-auth, no-password, CSRF, and `/k/` authentication contracts; add focused maintained synthetic coverage; reconcile maintained documentation and issue state; and close Runway OS locally after verification.

Excluded: Tasks 1P.3-1P.7; the remainder of Task 2; Tasks 3-4; CSP; entity-cookie changes; mobile, installed-PWA, and generalized browser work; session lifetime, name, domain, or path changes; migrations; credentials; protected data; real databases; production inspection; Fly mutation; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and runner: Codex Desktop in the current task on `codex/session-cookie-policy`; no delegation or second opinion.

Stop conditions: a secret, Fly configuration mutation, live inspection, proxy-trust redesign, authentication-flow change, entity-cookie or CSP work, another Task 1P item, protected/live access, scope expansion, plan-changing verification failure, failed cleanup, command-center failure, or overlap with either preserved untracked file.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; local and Fly-simulated cookie attributes; authenticated HTTPS session continuity for the root and `/k/`; configured-auth, no-password, CSRF, and non-permanent-session preservation; environment restoration; no external networking; Python compilation; JSON validation; `git diff --check`; dashboard refresh and health; rendered-dashboard inspection; and final worktree review.

Durability: local-only. Commit, push, PR, merge, publication, deployment, production inspection, and live actions remain unauthorized.

Report point: return the exact cookie contract, focused and full synthetic proof, changed paths, cleanup, preserved boundaries, local branch state, and separate publication gate.

Suggested next work block: 4AC-R exact-scope durability and release only if separately authorized; otherwise plan 4AD for Task 1P.3.

Result: the Flask factory now explicitly uses HttpOnly and SameSite Lax in every environment and adds Secure when Fly supplies a non-empty `FLY_APP_NAME`, while ordinary local HTTP remains usable. The host-only, application-root, non-permanent `session` cookie; configured-auth and no-password modes; CSRF; exemptions; protected root; and `/k/` all remain intact. Baseline and final maintained smoke suites pass with exact local and Fly-simulated cookie attributes, secure HTTPS session continuity, environment restoration, and cleanup. Python compilation, JSON, whitespace, dashboard refresh, health, rendered inspection, and scope checks pass locally. No CSP, entity-cookie, session-lifetime, mobile/PWA, broad browser, protected/live, GitHub, publication, deployment, or other excluded action occurred.

### Confirmed Work Block 4AB: `/k/` Authentication Boundary

Status: complete, durable, automatically deployed, and credential-free production health verified through 4AB-R

Parent tasks: Phase 4 Task 1P.1 and only the focused Task 2 coverage for `P3-3J-03` and its request/public-field slice of `P3-3J-C01`.

Included: require `/k` and `/k/` to pass the existing configured server-side session gate before route execution; separate authentication exemptions from global entity-setup exemptions so the route can continue managing Personal and Luxe Legacy itself; preserve authenticated and no-password behavior, BFM exclusion, current post-auth fields, and existing non-`/k/` exemptions; add focused maintained synthetic coverage and sanitized Runway OS closeout.

Excluded: Tasks 1P.2-1P.7; the remainder of Task 2; Tasks 3-4; cookie flags; CSP; mobile navigation; generalized browser-test infrastructure; Upload copy; broad read-model coverage; migrations; credential or secret changes; real data or databases; production inspection; Plaid, Fly, workflows, downstream systems, GitHub publication, deployment, and other live actions; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: the route exemption, authentication order, no-side-effect pre-auth boundary, exact post-auth entity/field contract, and focused regression checks share one Flask application seam and one synthetic verification path. The excluded tasks require separate browser-security, UX, operator-copy, or broad read-model contracts.

Owner and recommended agent: Codex Desktop in the current task. The sensitive-retrofit policy keeps authentication implementation, synthetic financial-boundary verification, cleanup, documentation, issue disposition, and Runway OS stewardship with Codex; no delegation or second opinion is needed.

Runner path: current Codex task on local branch `codex/k-dashboard-auth-boundary`. Codex owns implementation, review, verification, cleanup, exact-scope intake, and dashboard closeout.

Expected surfaces: `web/__init__.py`; `web/routes/kristine.py`; focused `scripts/smoke_test.py` coverage; `README.md`; a compact authenticated-dashboard contract; sanitized 4AB evidence; `command-center/issues.md`; and Runway OS roadmap, now, decisions, state, and generated dashboard. `web/templates/kristine.html` should remain unchanged unless source verification reveals a real compatibility dependency.

Defaults: keep `/k/` global entity-setup-exempt but not authentication-exempt; configured-auth full-page requests redirect safely to login with the return path preserved; unauthenticated HTMX and JSON requests return 401; authentication runs before database initialization or background-sync launch; authenticated output preserves Personal and Luxe Legacy scope, BFM exclusion, and current fields; no-password/demo mode stays coherent with the rest of the application; health, static, service-worker, offline, login, and bearer-protected scheduled-sync exemptions remain unchanged; durability is local-only.

Blocking questions: none. Ryan already selected the existing server-side authentication gate as the intended `/k/` contract.

Stop conditions: correct behavior requires real credentials, protected data, a secret change, production inspection, a changed configured/no-password policy, or a wider entity-context architecture; scope reaches cookie, CSP, mobile, PWA-harness, Upload, broad read-model, migration, Plaid, deployment, or another task; focused or full verification materially changes the plan; exact cleanup cannot be proven; command-center checks fail; or either preserved untracked file would be touched.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; configured-auth `/k` and `/k/` redirect, safe-return, HTMX/JSON 401, authenticated-rendering, and pre-auth-body checks; fail-fast proof that unauthorized requests initialize no route database and launch no background sync; authenticated Personal/Luxe Legacy scope and BFM exclusion; no-password availability; unchanged exempt surfaces; denied networking; unchanged temporary all-entity data; exact cleanup; targeted Python compilation; JSON validation; `git diff --check`; dashboard refresh; command-center health; generated-dashboard inspection; and explicit-path worktree review.

Dashboard closeout: 4AB and 4AB-R are complete; human-readable sources and `state.json` are aligned; the generated dashboard is refreshed and health checked; Task 1P.2 is the next separate planning gate.

Report point: return the exact authentication/exemption contract, pre-route no-side-effect proof, configured/no-password results, authenticated field/entity behavior, changed paths, cleanup proof, preserved exclusions, local branch state, and separate publication gate.

Suggested next work block: plan 4AC for Task 1P.2 session-cookie hardening; implementation remains unconfirmed.

Result: authentication exemptions and entity-setup exemptions are now separate. Configured unauthenticated `/k` and `/k/` full-page requests redirect safely to login, HTMX and JSON receive 401, and maintained fail-fast checks prove no global or route-specific database initialization or background-sync launch occurs first. Authenticated and no-password requests preserve the standalone route, Personal/Luxe Legacy fields, BFM exclusion, and its own sync seam. Baseline and final full smoke suites, compilation, logical database preservation, denied networking, exact synthetic cleanup, JSON, whitespace, dashboard refresh, health, generated inspection, and worktree review pass locally. One initial test assertion assumed cent rendering; the existing template intentionally uses whole dollars, so the assertion was corrected without changing product behavior. No credential, protected data, real database, external request, live action, GitHub durability, or deployment occurred. Evidence: `command-center/focused-dashboard-auth-contract.md` and `command-center/logs/2026-07-21-focused-dashboard-auth-boundary-4ab.md`.

### Confirmed Work Block 4AB-R: Focused Dashboard Authentication Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-21

Parent task: Phase 4 Task 4 for the exact verified 4AB source set only.

Included: the exact verified twelve-path 4AB application, route documentation, maintained-test, README, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/k-dashboard-auth-boundary`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Tasks 1P.2-1P.7; broader Task 2; unrelated repairs; PR creation; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4AB contract and implementation; create one source commit on the existing feature branch; fast-forward local `main`; push without force; observe only the automatic deployment caused by the source push; verify only credential-free `/health`; publish the closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1P.2 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic smoke suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job attribution; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and separate Task 1P.2 planning gate.

Result: exact twelve-path source commit `e20555d` was fast-forwarded and pushed directly to `main` without force or PR. Automatic Fly Deploy run `29849025459` and deploy job `88696866487` passed for exact source SHA `e20555d7785e3becbf2eabede548007284d2d765`, and credential-free production `/health` returned HTTP 200. Local `main` matched `origin/main`; the staged high-confidence sensitive-addition scan returned zero; both preserved untracked files remained excluded; and this command-center-only closeout uses `[skip actions]` to prevent a second deployment. Task 1P.2 is now the separate planning gate.

### Confirmed Work Block 4V: Weekly Date And Bill Truthfulness

Status: complete and verified locally on 2026-07-21; release not authorized

Included: Task 1N.4 plus only the focused Task 2 regression slice for `P3-3E-01`, `P3-3E-02`, and the matching `P3-3E-C01` coverage. Use the selected ISO week's Monday as the budget-month anchor; make pace, category pace, MTD, burn, recurring/manual/card bill projection, and displayed period share that viewed-week context; prevent cross-month windows from exceeding the anchored month; use positive scheduled card payments for bill rows and totals; and render missing or zero scheduled amounts as unavailable without substituting the full balance.

Excluded: Tasks 1N.5-1N.8; Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; migrations; historical remediation; demo redesign; broad UI work; authentication or CSRF changes; real financial data; retained uploads; credentials; production/demo access; Plaid; external calls; workflows; Fly; downstream writes; commit, push, PR, merge, or deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Outcome: one deterministic viewed-week contract drives Weekly pace, category pace, MTD, burn, bill recurrence, and displayed period across current, historical, cross-month, and cross-year weeks; card reminders, displayed amounts, and totals reconcile to scheduled payments in integer cents; missing or zero scheduled amounts remain explicit and never silently become full balances; existing Cash Flow and Short-Term Planning defaults, entity isolation, and unrelated rows remain unchanged.

Owner and recommended agent: Codex Desktop in the current task on `codex/weekly-date-bill-truthfulness`. The repair couples Weekly route orchestration, date-aware shared helpers, maintained synthetic coverage, issue disposition, and Runway OS stewardship. No delegation or second opinion is needed, and Codex owns implementation, verification, cleanup, dashboard currency, and final intake.

Stop conditions:

- Correct behavior requires a different week/month anchor or scheduled-payment fallback policy.
- Shared-helper changes would alter unrelated Cash Flow or Short-Term Planning behavior.
- The repair requires a migration, historical remediation, Task 1N.5, Waterfall work, broader UI design, authentication, or another Phase 4 task.
- Verification requires protected financial data, retained uploads, credentials, production/demo access, Plaid, networking, a workflow, Fly, downstream access, or another live action.
- Maintained or focused verification changes the plan, exact cleanup cannot be proven, command-center refresh or health fails, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py` using only its temporary synthetic `DATA_DIR`.
- Focused current, historical, cross-month, cross-year, empty, and invalid-week Weekly navigation; budget/category pace, MTD, burn, display, drill-through, recurrence, bill ordering, multiple-card, positive/missing/zero scheduled-payment, zero-balance, row, and total reconciliation checks.
- Personal and BFM behavior, Luxe Legacy denial, denied networking, unrelated-row preservation, and exact temporary cleanup.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, production/demo, Plaid, downstream, or other live action is part of work block 4V.

Report point: return the exact viewed-week contract, recurrence-anchor behavior, missing-payment behavior, focused and full synthetic results, changed paths, cleanup proof, preserved boundaries, local branch state, and the separate publication gate. If 4V closes cleanly, 4V-R is publication-only if separately authorized; otherwise Task 1N.5 is the next planning gate.

Result: Weekly now uses the selected ISO week's Monday as the single budget-month anchor for total/category pace, last-week comparison, warnings, MTD, burn, and display. Detected recurring, manual recurring, and card-due helpers accept an optional reference date so historical and boundary weeks project from their viewed Monday while existing Cash Flow and Short-Term Planning callers retain today-based defaults. Positive scheduled card payments drive row amounts and totals; missing or zero scheduled amounts remain unavailable and never fall back to full balances. Baseline and final full smoke, maintained section 8a5, compilation, JSON, whitespace, dashboard refresh, health, rendered inspection, Personal/BFM isolation, Luxe Legacy denial, denied networking, unrelated-row preservation, and exact cleanup pass locally. No migration, template, protected-data, external, GitHub durability, deployment, or live action occurred.

### Confirmed Work Block 4V-R: Weekly Date And Bill Truthfulness Durability And Release

Status: complete on 2026-07-21

Included: the exact verified twelve-path 4V application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/weekly-date-bill-truthfulness`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N.5; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4V contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N.5 planning separate.

Stop conditions: an unexpected path, sensitive addition, protected data, unrelated user change, local or remote `main` divergence, failed maintained verification, excluded staging, unattributable or failed automatic deployment, failed credential-free health, a second closeout deployment, or recovery beyond the authorized fast-forward path.

Verification: exact path and staged-set review; branch ancestry and remote alignment; staged high-confidence sensitive-addition scan; maintained smoke, Python compilation, JSON validation, dashboard refresh, health check, and whitespace check; direct-main fast-forward push; exact automatic Fly run and job attribution; credential-free production health; final `main` alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1N.5 planning gate.

Result: the exact twelve-path 4V source set was committed as `9b3e517`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29826028617` and deploy job `88619460588` passed for exact source SHA `9b3e517fc7edf36dd681c6ff5ffe6fd33ddc3263`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, the staged high-confidence sensitive-addition scan returned zero, and no PR or unauthorized live action occurred. This command-center-only closeout uses `[skip actions]` to prevent a second deployment. Evidence: `command-center/logs/2026-07-21-weekly-date-bill-truthfulness-release-4v-r.md`.

### Confirmed Work Block 4W: Weekly Paydown Goal Validation

Status: complete and verified locally on 2026-07-21; publication not authorized

Included: Task 1N.5 plus only the focused Task 2 regression slice for `P3-3E-04` and matching `P3-3E-C01` coverage. Accept only a real ISO target date strictly later than the current local date; reject malformed, nonexistent, empty, today, and past submissions without mutating the prior goal; preserve valid start metadata on update; make malformed stored goals safe for Weekly and Waterfall reads; allow a later valid target to recover a row whose target date alone is malformed; and align browser guidance with the server rule.

Excluded: Tasks 1N.6-1N.8; Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; Waterfall averaging, rounding, or tax repairs; migrations; historical remediation; broader UI work; authentication or CSRF changes; real financial data; retained uploads; credentials; production/demo access; external calls; workflows; Fly; downstream writes; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: the unsafe POST, singleton stored-goal parser, Weekly rendering, Waterfall's shared paydown helper, and focused regression coverage use the same goal contract and synthetic verification path. The next Waterfall tasks change separate financial-calculation contracts and remain independently gated.

Defaults confirmed by Ryan with the block: require a target strictly later than the server's current local date; preserve valid stored start date and balance on target update; perform no read-time mutation; treat malformed stored goal metadata as unavailable for pace rendering; return sanitized controlled guidance without echoing input; keep the block local-only; and gate every commit, push, release, or live action separately.

Expansion candidates and questions: none. Task 1N.6 introduces a separate signed-surplus period and payoff-input contract.

Owner and recommended agent: Codex Desktop in the current task on local branch `codex/weekly-paydown-goal-validation`. The small sensitive-repo repair couples route validation, a shared defensive read seam, maintained synthetic coverage, issue disposition, and Runway OS stewardship; no delegation or second opinion is needed. Codex owns implementation, verification, exact cleanup, and dashboard closeout.

Expected surfaces: `web/routes/weekly.py`; `web/templates/weekly.html` if needed to align browser guidance; `web/routes/waterfall.py` only if the shared defensive seam requires a focused change; `scripts/smoke_test.py`; a compact paydown-goal contract; sanitized 4W evidence; issue disposition; and Runway OS sources/dashboard. No migration or `core/db.py` change is expected.

Stop conditions:

- The confirmed date-range rule needs to change, or safe recovery requires a migration, deletion, or historical remediation.
- Correct behavior requires Waterfall averaging, payoff rounding, tax normalization, another Phase 4 task, authentication, or CSRF changes.
- Protected data, retained uploads, credentials, production/demo, external access, workflows, Fly, downstream writes, or another live action becomes necessary.
- Focused or full verification materially changes the plan, exact cleanup cannot be proven, command-center checks fail, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py`.
- Personal/BFM valid create and update, preserved start metadata, and valid target recovery from a malformed stored target.
- Malformed, nonexistent, empty, today, and past submissions with exact zero-mutation proof.
- Malformed stored target date, start date, or unusable start-balance metadata cannot break Weekly or Waterfall reads and causes no read-time mutation.
- Luxe Legacy denial, denied networking, unrelated-row preservation, and exact temporary cleanup.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered dashboard inspection, and final explicit-path worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is authorized.

Report point: return the accepted date contract, rejected-input behavior, Weekly and Waterfall defensive-read behavior, recovery result, focused and full synthetic results, changed paths, cleanup proof, preserved boundaries, local branch state, and the separate publication gate.

Suggested next work block: 4W-R durability and automatic release only if separately authorized; otherwise separately plan Task 1N.6 as 4X.

Result: Weekly now accepts only canonical real targets strictly later than the current local date and rejects empty, malformed, nonexistent, loose-format, today, and past targets before database access with exact prior-state preservation. Valid updates retain row identity, creation time, start date, and start balance; a valid target can recover a malformed target-only row when its start metadata remains usable. Weekly and Waterfall now ignore malformed stored target dates, start dates, or start balances without read-time mutation, and the browser minimum matches the server rule. Baseline and final full smoke suites, maintained section 8a6, compilation, JSON, whitespace, dashboard refresh, health, Personal/BFM isolation, Luxe Legacy denial, denied networking, unrelated-row preservation, and exact cleanup pass locally. No migration, historical remediation, Waterfall calculation repair, protected data, external access, GitHub durability, deployment, or live action occurred. Evidence: `command-center/paydown-goal-validation-contract.md` and `command-center/logs/2026-07-21-weekly-paydown-goal-validation-4w.md`.

### Confirmed Work Block 4W-R: Weekly Paydown Goal Validation Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-21

Parent task: Phase 4 Task 4 for the exact verified 4W source set only.

Included: the exact verified eleven-path 4W application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/weekly-paydown-goal-validation`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N.6; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4W contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N.6 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1N.6 planning gate.

Result: the exact eleven-path 4W source set was committed as `404e3d3`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29828286559` and deploy job `88626630654` passed for exact source SHA `404e3d3d5271e35ca25b857b88fa3d3df683aaf5`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, the staged high-confidence sensitive-addition scan returned zero, and no PR or unauthorized live action occurred. This command-center-only closeout uses `[skip actions]` to prevent a second deployment. Evidence: `command-center/logs/2026-07-21-weekly-paydown-goal-validation-release-4w-r.md`.

### Confirmed Work Block 4Y: Waterfall Tax Input Truthfulness

Status: complete and verified locally on 2026-07-21; publication not authorized

Included: Task 1N.8 and only the focused Task 2 regression slice for `P3-3E-06` and matching `P3-3E-C01` Waterfall coverage. Parse the tax query once as a finite decimal, round once to basis-point precision, accept normalized values from 0 through 9,999 basis points, use the existing 2,200-basis-point default for omitted or invalid input, and derive both rendering and every actual/target calculation from the same normalized value.

Excluded: Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; Waterfall payoff-window or duration changes; migrations; historical remediation; broader UI work; authentication or CSRF changes; real financial data; retained uploads; credentials; production/demo access; Plaid; networking; workflows; Fly; downstream writes; GitHub publication; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: the final known Weekly/Waterfall audit defect and its regression slice share one route/template calculation chain, one input contract, and one synthetic verification path. Neighboring tasks concern downstream integration, security and UX policy, CI, or publication and therefore have different dependencies or risk classes.

Owner and recommended agent: Codex Desktop in the current task on `codex/waterfall-tax-input-truthfulness`. The block couples financial-input normalization, route/template reconciliation, maintained synthetic coverage, issue disposition, exact cleanup, and Runway OS stewardship. No delegation or second opinion is needed.

Defaults: parse with finite decimal handling; round once to the nearest basis point; accept normalized 0.00% through 99.99%; fall back to the existing 22.00% for omitted, blank, malformed, non-finite, negative, 100%-or-greater, or normalization-overflow input; derive the display value from the accepted basis points; preserve existing calculation behavior otherwise; return a safe rendered page rather than a new validation response; and keep the block local-only.

Stop conditions:

- Correct behavior requires rejecting input with a new user-facing error or a different range or precision policy.
- The repair expands into payoff calculations, migration, historical remediation, broader UI work, authentication, or another Phase 4 task.
- Verification requires protected financial data, retained uploads, credentials, production/demo, Plaid, networking, workflows, Fly, downstream access, GitHub publication, deployment, or another live action.
- Maintained or focused verification changes the plan, exact cleanup cannot be proven, command-center refresh or health fails, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py` using only its temporary synthetic `DATA_DIR`.
- Focused omitted, valid integer and decimal, zero, 99.99, 100, negative, blank, malformed, `NaN`, positive/negative infinity, and extreme-value route cases.
- Reconcile the rendered rate, actual take-home, target take-home, take-home-mode revenue, and safe fallback to the same normalized basis-point value.
- Personal/BFM intended behavior, Luxe Legacy denial, denied networking, unrelated-row preservation, exact temporary cleanup, Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is part of work block 4Y.

Report point: return the exact normalized input and fallback contract, calculation/display reconciliation, focused and full synthetic results, changed paths, cleanup proof, preserved boundaries, local branch state, and separate publication gate. If 4Y closes cleanly, 4Y-R is publication-only if separately authorized; otherwise stop at the exact blocker.

Result: Waterfall now parses the optional tax query once with finite decimal semantics, rounds half-up once to basis-point precision, accepts normalized 0.00% through 99.99%, and uses the existing 22.00% default for omitted, blank, malformed, non-finite, negative, 100%-or-greater, or normalization-overflow input. One integer basis-point value drives both tax controls, actual take-home, revenue-mode take-home, and take-home-mode gross and required revenue. Browser input reaches the server without sign-stripping reinterpretation. Baseline and final full smoke suites pass; maintained section 8a8 covers the normalization matrix, rendering and calculation reconciliation, Personal/BFM behavior, Luxe Legacy denial, denied networking, database preservation, and exact cleanup. Compilation, JSON, whitespace, dashboard refresh, health, rendered inspection, and scope review pass locally. No migration, protected data, external access, GitHub durability, deployment, or live action occurred. Evidence: `command-center/waterfall-tax-input-contract.md` and `command-center/logs/2026-07-21-waterfall-tax-input-truthfulness-4y.md`.

### Confirmed Work Block 4Y-R: Waterfall Tax Input Truthfulness Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-21

Parent task: Phase 4 Task 4 for the exact verified 4Y source set only.

Included: the exact verified eleven-path 4Y application, template, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/waterfall-tax-input-truthfulness`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1O; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4Y contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1O planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1O planning gate.

Result: the exact eleven-path 4Y source set was committed as `b5c862b`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29833970537` and deploy job `88645453012` passed for exact source SHA `b5c862b002dbb5d2831a8cebf4cbf71705008c1d`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, the staged high-confidence sensitive-addition scan returned zero, and no PR or unauthorized live action occurred. This command-center-only closeout uses `[skip actions]` to prevent a second deployment. Evidence: `command-center/logs/2026-07-21-waterfall-tax-input-truthfulness-release-4y-r.md`.

### Confirmed Work Block 4Z: Downstream Idempotency Contract Discovery

Status: complete on 2026-07-21

Included: Task 1O.1 only. Verify from tracked local sources whether the intended downstream `ledger_transactions.plaid_transaction_id` column is uniquely constrained and which explicit PostgREST conflict target the Ledger mirror must use. Read the downstream repository's agent instructions first, confirm repository identity, and compare exact tracked schema, migration, test, and request-contract evidence with `core/luxury_bridge.py` and the existing 3I findings.

Excluded: Tasks 1O.2-1O.4; Task 1P; Tasks 2-4; application, test, schema, or migration implementation; downstream-repository changes; credentials; protected or row-level data; databases; untracked payloads; network or Supabase access; live requests or downstream writes; Plaid; workflows; Fly; GitHub publication; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: Task 1O.1 is the read-only prerequisite for every remaining downstream-mirror repair. Tasks 1O.2-1O.4 depend on the discovered uniqueness and conflict contract, so including them now would require guessing behavior that the audit explicitly left unverified.

Owner and recommended agent: Codex Desktop in the current task. The block couples sensitive cross-repository boundary control, exact tracked-source reconciliation, sanitized evidence, and Runway OS stewardship. No delegation or second opinion is needed.

Defaults: treat `/Users/ryanbuffington/Documents/GitHub/luxurious luxury` as the intended target only if tracked Ledger and downstream sources establish that identity; inspect tracked files only without fetch or pull; do not open secret files, databases, row data, or untracked payloads; write only a sanitized Expense Tracker command-center verdict and state closeout; and keep all implementation separately gated.

Stop conditions:

- Tracked evidence cannot establish the intended downstream repository.
- The uniqueness or PostgREST conflict contract is absent, stale, or contradictory.
- Proof requires credentials, protected data, row data, a database, networking, Supabase, or a live request.
- A downstream migration, product decision, implementation, or another Phase 4 task becomes necessary.
- Scope reaches Tasks 1O.2-1O.4, verification changes the plan, command-center checks fail, or either preserved untracked file would be touched.

Verification:

- Record the downstream repository identity, branch, commit, worktree status, and exact tracked-file scope without mutation or remote fetch.
- Cite exact tracked schema, migration, test, and request-contract sources supporting or contradicting uniqueness and conflict behavior.
- Confirm no secret, database, row-data, untracked-payload, network, Supabase, live-request, or downstream-write access occurred.
- Validate `command-center/state.json`, run dashboard refresh and health check, run `git diff --check`, inspect the rendered dashboard, and review the final worktree with both preserved untracked files untouched.
- Do not run the application smoke suite because this block changes no application or maintained test code.

Durability: exact eight-path closeout commit `88a8c52` is durable on local `main` and `origin/main`. GitHub reported no workflow run for the `[skip actions]` commit, so no Fly deployment started. Both preserved untracked files remain untouched; no PR, force push, credential, protected data, product implementation, live downstream action, or unrelated mutation occurred.

Report point: return the proven conflict key and request semantics, exact tracked evidence, compatibility verdict, remaining uncertainty, preserved boundaries, and the recommended readiness or blocker for a separately confirmed Task 1O.2-1O.4 implementation block.

Result: tracked downstream sources identify `/Users/ryanbuffington/Documents/GitHub/luxurious luxury` as the intended Supabase consumer, direct operators to `src/lib/db/schema.sql`, define `ledger_transactions.plaid_transaction_id` as the table primary key, and explicitly upsert the tracked Apple Card importer on that column. The Ledger bridge names the same intended key but its local index is non-unique, its eligibility predicate admits empty strings, its payload builder does not handle repeated keys, and its REST request leaves the conflict target implicit. No downstream schema change is indicated. Tasks 1O.2-1O.4 are ready for separate local-only planning; deployed-schema and live behavior remain intentionally unverified. The initial broad tracked-source search returned credential-related history from a tracked memory file; no value is reproduced, the search was narrowed immediately, and no environment file, keychain, database, row data, untracked payload, network, Supabase surface, downstream mutation, or live action occurred. Evidence: `command-center/luxe-legacy-downstream-contract-discovery.md`.

### Confirmed Work Block 4AA: Mirror Key Validation And Explicit Idempotency

Status: complete and verified locally on 2026-07-21; publication not authorized

Included: Tasks 1O.2-1O.4. Treat Plaid transaction IDs as opaque; reject null, empty, whitespace-only, or whitespace-padded identifiers without rewriting them; reject every row in a repeated valid-key group while continuing with unrelated valid rows; record only sanitized invalid and duplicate counts; explicitly send `on_conflict=plaid_transaction_id` with merge-duplicate semantics; and complete the remaining maintained `P3-3I-C01` configuration no-op, request-shape, malformed-key, duplicate-key, failure-isolation, repeatability, and entity-preservation coverage using temporary all-entity databases, mocked HTTP, and denied sockets.

Excluded: Task 1P; unrelated Task 2 coverage; Tasks 3-4; database migrations; downstream-repository changes; production or deployed-schema inspection; live Supabase requests or writes; protected data; credentials; Plaid, Fly, workflows, deployment, commit, push, PR, or merge actions; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: the three tasks share one bridge function, one established downstream key contract, one maintained smoke-test section, one synthetic verification path, and one downstream-correctness risk. Work block 4Z removed the only schema-choice dependency by proving the tracked downstream primary key and explicit conflict target are both `plaid_transaction_id` and that no downstream schema change is indicated. Task 1P starts a separate authentication, mobile, browser-hardening, and UX decision family.

Owner and recommended agent: Codex Desktop in the current task on local branch `codex/luxe-legacy-mirror-idempotency`. The block is a small integrated repair coupling implementation, synthetic financial-boundary verification, issue disposition, and Runway OS stewardship. No delegation or second opinion is needed. Codex owns implementation, verification, cleanup, dashboard currency, and final intake.

Defaults confirmed by Ryan: treat keys as opaque and require a non-empty identifier equal to its stripped form; do not repair or rewrite malformed source values; reject every row in an exact duplicate valid-key group rather than choosing a winner; continue with unrelated valid rows; log only sanitized counts, never identifiers or row data; retain the existing successful-row count and failure-isolation return contract; use the explicit PostgREST `on_conflict=plaid_transaction_id` request parameter; make no migration or downstream-repository change; and keep durability local-only.

Stop conditions:

- Correct behavior requires choosing a duplicate winner, rewriting source identifiers, or changing the confirmed malformed-key policy.
- A local or downstream schema migration, deployed-schema inspection, production verification, or downstream-repository change becomes necessary.
- Verification requires credentials, protected or row-level financial data, networking, Supabase, Plaid, Fly, workflows, or another live system.
- Work expands into sync orchestration, broader failure semantics, Task 1P, another repair family, or unrelated Task 2 coverage.
- Focused or full verification changes the plan, exact cleanup cannot be proven, command-center refresh or health fails, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py` using only its temporary synthetic `DATA_DIR`.
- Focused missing and partial configuration no-op, explicit request path/headers/conflict target/timeout/payload, success, failure-isolation, and repeatability checks.
- Null, empty, whitespace-only, whitespace-padded, exact duplicate-group, mixed malformed/duplicate/valid, and unrelated-valid-row behavior.
- Temporary Personal, BFM, and Luxe Legacy databases; mocked HTTP; denied outbound sockets; exact source-row and all-entity preservation; and exact cleanup.
- Targeted Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final worktree review.

Dashboard closeout: update human-readable sources first; align `state.json`; refresh and health-check the dashboard; and record Tasks 1O.2-1O.4 and 4AA as done only if every required check passes.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, production, Plaid, Supabase, downstream-write, or other live action is included.

Report point: return the exact malformed and duplicate-key policy, explicit request contract, focused and full synthetic results, changed paths, cleanup proof, preserved boundaries, local branch state, and separate 4AA-R publication gate.

Suggested next work block: 4AA-R for exact-scope durability and automatic release only if Ryan separately authorizes publication after local verification.

Result: the bridge now keeps SQL `NULL` identifiers outside selection; rejects empty, whitespace-only, and whitespace-padded identifiers without rewriting source rows; withholds every row in an exact duplicate valid-key group; continues unrelated valid rows in deterministic order; logs sanitized counts only; returns zero without HTTP when nothing valid remains; and explicitly sends `on_conflict=plaid_transaction_id` with merge-duplicate semantics. Maintained section 8c proves missing and partial configuration no-ops, invalid-only behavior, mixed malformed/duplicate/excluded/valid selection, repeatability, exact request headers and conflict semantics, timeout, failure isolation, all-entity preservation, scheduled/public Luxe Legacy-only invocation, denied networking, and exact cleanup. Baseline and final full smoke suites, Python compilation, JSON, whitespace, dashboard refresh, health, rendered inspection, and final scope review pass locally. The request-header assertion caught a service-key/row-key variable shadowing regression before closeout; the variables were separated and the entire suite passed again. No migration, downstream-repository change, protected data, credential, production or Supabase access, external request, GitHub durability, deployment, or live action occurred. Evidence: `command-center/luxe-legacy-mirror-idempotency-contract.md` and `command-center/logs/2026-07-21-luxe-legacy-mirror-idempotency-4aa.md`.

### Confirmed Work Block 4AA-R: Mirror Idempotency Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-21

Included: the exact verified eleven-path 4AA application, maintained-test, README, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/luxe-legacy-mirror-idempotency`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1P; broader Task 2; unrelated repairs; PR creation; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4AA contract and implementation; create one source commit on the existing feature branch; fast-forward local `main`; push `main` without force; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1P planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and high-confidence sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; exact automatic Fly run/job attribution; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and separate Task 1P planning gate.

Result: the exact eleven-path 4AA source set was committed as `9d10e25`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29839016474` and deploy job `88662740219` passed every reported step for exact source SHA `9d10e25809ef7e39f580705c9b7290cb3889ddc3`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, the staged high-confidence sensitive-addition scan returned zero, and no PR, protected data, retained upload, credential, authenticated production page, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1P implementation, force push, or unrelated action occurred. GitHub reported the non-blocking Node 20 deprecation annotation for `actions/checkout@v4`, forced onto Node 24. This command-center-only closeout uses `[skip actions]` to prevent a second deployment. Evidence: `command-center/logs/2026-07-21-luxe-legacy-mirror-idempotency-release-4aa-r.md`.

### Confirmed Work Block 4X: Waterfall Payoff Truthfulness

Status: complete and verified locally on 2026-07-21; publication not authorized

Included: Task 1N.6, Task 1N.7, and only the focused Task 2 regression slices for `P3-3E-03`, `P3-3E-05`, and `P3-3E-C01`. Use the selected Waterfall month and the two immediately preceding calendar months; include every signed monthly BFM surplus, with a no-row month contributing zero; drive display and payoff from the same three-month average; return no estimate for a non-positive average; and use ceiling-to-whole-month display plus the same exact ratio rounded upward to a whole day for payoff date.

Excluded: Task 1N.8; Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; migrations; historical remediation; broader UI work; authentication; real financial data; retained uploads; credentials; production/demo access; Plaid; external calls; workflows; Fly; downstream writes; GitHub publication; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: the rolling-average and payoff-duration defects share the same Waterfall route helper, displayed output, synthetic history, reconciliation path, and financial-truthfulness risk. Task 1N.8 starts a separate direct-input and tax-normalization contract.

Owner and recommended agent: Codex Desktop in the current task on `codex/waterfall-payoff-truthfulness`. The block couples financial-contract definition, route/helper implementation, focused maintained coverage, issue reconciliation, exact cleanup, and Runway OS stewardship. No delegation or second opinion is needed.

Defaults: use a fixed three-calendar-month window ending at the selected month; include positive, zero, and negative signed surplus; treat a no-row calendar month as zero because no separate completeness signal exists; use the same average for display and calculation; return no payoff estimate for non-positive average; use whole-month ceiling for display; derive payoff date from the same exact ratio rounded upward to a whole day; preserve Personal/BFM sharing, Luxe Legacy denial, and read-only route behavior; and keep the block local-only.

Stop conditions:

- Correct behavior requires a separate completeness signal or a different rolling-period or missing-month policy.
- The repair requires Task 1N.8, migration, historical remediation, broader UI work, authentication, or another Phase 4 task.
- Verification requires protected financial data, retained uploads, credentials, production/demo, Plaid, networking, workflows, Fly, downstream access, GitHub publication, deployment, or another live action.
- Maintained or focused verification changes the plan, exact cleanup cannot be proven, command-center refresh or health fails, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py` using only its temporary synthetic `DATA_DIR`.
- Focused mixed, positive, zero, non-positive, missing-month, historical, and cross-year signed-window checks, including the `$1,000 - $2,000 + $2,500 = $500/month` reproduction.
- Sub-month, fractional, exact-multiple, zero-debt, and non-positive-surplus payoff checks; displayed average, whole-month duration, and payoff date must reconcile to the same exact ratio.
- Personal/BFM intended behavior, Luxe Legacy denial, denied networking, unrelated-row preservation, exact temporary cleanup, Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is part of work block 4X.

Report point: return the exact rolling-window and signed-average contract, payoff-rounding behavior, focused and full synthetic results, changed paths, cleanup proof, preserved boundaries, local branch state, and separate publication gate. If 4X closes cleanly, 4X-R is publication-only if separately authorized; otherwise Task 1N.8 becomes the next planning gate.

Result: Waterfall now uses a fixed three-calendar-month payoff window ending at the selected month and averages every signed monthly result, including deficits, zeros, and no-row months. The audit history of `$1,000`, `-$2,000`, and `$2,500` now displays and calculates from `$500/month`. Positive debt and surplus use ceiling-to-whole-month duration and a payoff date derived from the same exact ratio rounded upward to a whole day, so sub-month debt cannot report zero months. The template labels the signed average and handles singular month wording. Baseline and final full smoke suites, maintained section 8a7, compilation, JSON, whitespace, dashboard refresh, health, rendered inspection, all-entity boundaries, denied networking, read-only preservation, and exact cleanup pass locally. No Task 1N.8, migration, protected data, external access, GitHub durability, deployment, or live action occurred. Evidence: `command-center/waterfall-payoff-contract.md` and `command-center/logs/2026-07-21-waterfall-payoff-truthfulness-4x.md`.

### Confirmed Work Block 4X-R: Waterfall Payoff Truthfulness Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-21

Parent task: Phase 4 Task 4 for the exact verified 4X source set only.

Included: the exact verified eleven-path 4X application, template, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/waterfall-payoff-truthfulness`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N.8; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout. No delegation or second opinion is needed.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4X contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N.8 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1N.8 planning gate.

Result: the exact eleven-path 4X source set was committed as `dc12890`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29830719921` and deploy job `88634537268` passed for exact source SHA `dc128903bb7dd21cc3516a6742ce9d083f66bbc1`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, the staged high-confidence sensitive-addition scan returned zero, and no PR or unauthorized live action occurred. This command-center-only closeout uses `[skip actions]` to prevent a second deployment. Evidence: `command-center/logs/2026-07-21-waterfall-payoff-truthfulness-release-4x-r.md`.

### Confirmed Work Block 4A: Server-Side Auth And Protected-Cache Repair

Status: complete and verified locally on 2026-07-18; release not authorized

Included: Phase 4 Task 1A only. Enforce configured authentication before protected HTML is returned; replace the client-exposed digest flow with a server-verified login that preserves legacy `APP_PASSWORD_HASH` compatibility and supports Werkzeug password hashes; make no-password mode coherent; restrict the service worker to static/offline assets and purge older dynamic caches; add focused synthetic request and isolated-browser regression coverage.

Excluded: `/k/` access or content changes; mobile drawer behavior; session-cookie or CSP hardening; credential rotation or real secret inspection; real databases, uploads, financial rows, existing browser state, production or demo access, and external calls; Plaid, Fly, workflows, downstream writes; commit, push, PR, merge, deployment; unrelated Phase 3 findings; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: unauthenticated protected requests receive no protected financial HTML; correct plaintext login establishes only a server session; the old digest replay route no longer works; configured and no-password modes agree between client and server; protected/entity-specific pages cannot be served from service-worker caches across sessions or entities; `/k/` remains behaviorally unchanged.

Owner and recommended agent: Codex Desktop in the current task. The change couples the Flask request boundary, session flow, base template, service worker, synthetic coverage, browser verification, and Runway OS stewardship; no external worker or second opinion is needed.

Stop conditions:

- Compatibility cannot be preserved without reading or changing a real password or credential.
- Verification requires a real database, financial row, existing browser profile, production/demo access, external call, or live action.
- The repair requires changing `/k/`, unrelated navigation or browser hardening, a database schema, Plaid, workflows, or deployment behavior.
- The maintained smoke suite fails for an unrelated reason, focused acceptance checks cannot pass, cleanup cannot be proven, or the dashboard health check fails.

Verification:

- `.venv/bin/python scripts/smoke_test.py` plus focused tracked configured-auth, no-password, CSRF, exempt-route, and legacy/modern password-hash checks.
- Isolated localhost browser checks proving no protected pre-auth HTML or client digest, correct/wrong login behavior, old-route denial, no-password coherence, static/offline-only caching, old-cache cleanup, cross-entity offline isolation, unchanged `/k/`, zero external requests, and disposable cleanup.
- `git diff --check`, dashboard refresh, health check, visual dashboard inspection, and final explicit-path worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is part of work block 4A.

Report point: return the exact auth and caching behavior changed, compatibility path, tracked and browser verification, unchanged `/k/` boundary, cleanup, remaining release gate, and what the fix means for the next Phase 3 step.

Result: configured full-page requests now redirect to a standalone CSRF-protected login before entity setup or protected rendering; HTMX/JSON remain 401; password verification is server-only; the digest, client storage gate, overlay, and `/auth/verify` are gone; legacy SHA-256 and Werkzeug hashes work; no-password mode renders directly; dynamic responses are no-store; cache v4 retains only static assets and the data-free offline page while purging older caches. The maintained suite and focused tracked checks passed, configured-auth Chromium passed 19/19, no-password Chromium passed 2/2, both with zero external requests, and visual/cleanup/whitespace checks passed. `/k/` remains unchanged. Production is unchanged pending separate release authorization.

### Confirmed Work Block 4B: Publish And Verify Auth Repair

Status: done, released, and verified on 2026-07-18

Included: Task 1A release durability and Task 4. Re-review the exact verified 4A diff and sensitive boundaries; stage and commit only intended application, tracked-test, documentation, and command-center paths; preserve the pre-existing untracked sync script; push `codex/server-side-auth-boundary`; open a PR; wait for required checks; merge to `main`; monitor the automatic Fly deployment; verify public and pre-auth production behavior without signing in; and publish the sanitized command-center-only closeout with `[skip actions]`.

Excluded: Task 1B and Tasks 2-3; credential inspection, rotation, or Fly secret changes; authenticated production financial-page verification; real databases, rows, uploads, or browser state; `/k/` access/content changes; mobile navigation; cookie/CSP hardening; Plaid actions, manual workflow dispatch, downstream writes; unrelated repairs; recovery outside the exact branch/PR/deploy path; pre-existing untracked `scripts/sync_prod_to_local.sh`.

Outcome: the verified repair is durable on `main`, the merge-triggered Fly deployment passes, production returns health successfully, protected full-page requests redirect to the standalone login before protected rendering, the public login contains no reusable digest or financial HTML, service-worker v4 exposes the static/offline-only contract, and project state records the release without a second deployment.

Owner and recommended agent: Codex Desktop in the current task. The release requires exact-path Git review, GitHub PR/check/merge handling, Fly workflow observation, credential-free HTTP verification, and Runway OS closeout; a second opinion adds no value after the deterministic 4A verification.

Blocking questions: none.

Non-blocking defaults: use a PR rather than direct product push to `main`; merge only after required checks pass; do not use the real password; do not rotate credentials; verify only health, redirect/login content, and service-worker source; use a direct-main `[skip actions]` commit only for the post-release command-center closeout.

Stop conditions:

- The exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change.
- The branch is conflicted or cannot be safely synchronized without rewriting history.
- A required PR check or the Fly deployment fails, is cancelled, or cannot be attributed to the merge.
- Production returns protected financial HTML before authentication, exposes a reusable digest, or does not serve service-worker v4.
- Verification requires a real password, authenticated financial page, database, protected data, secret change, manual workflow dispatch, or recovery beyond the approved release path.
- The final dashboard refresh, health check, whitespace check, or main/origin alignment cannot pass.

Verification:

- Exact status/diff/path review, sensitive-string scan, `.venv/bin/python scripts/smoke_test.py`, Python/service-worker syntax, `git diff --check`, dashboard refresh, health check, and dashboard inspection before commit.
- Required PR checks and merge commit; automatic Fly deployment run and job result without opening protected logs unless failure diagnosis is necessary.
- Credential-free production HTTP: `/health` 200; protected `/` redirects to `/auth/login`; login body contains no protected markers, client digest, `atlas-auth`, or `/auth/verify`; `/sw.js` contains `the-ledger-v4`, excludes protected root precache, and retains no dynamic-cache fallback.
- Final `main` and `origin/main` alignment, clean intended tracked state, preserved untracked sync script, sanitized closeout, dashboard refresh/health, and `[skip actions]` closeout publication.

Durability: source/test/docs/4A evidence through a reviewed PR merged to `main`, followed only by a command-center closeout commit with `[skip actions]`. No force push, credential mutation, manual workflow action, or second deployment is included.

Report point: return source commit, PR and merge, required checks, Fly deployment run/result, credential-free production verification, final `main`/`origin/main` state, closeout commit, preserved boundaries, and the next Phase 3 Task 7 planning point.

Result: source commit `fe1ec2e` was published through PR #86 and merged as `f4cd686`. GitHub reported no PR checks configured and a clean merge state. Automatic Fly Deploy run `29670793359` passed every step for the merge commit. Production `/health` returned 200; protected root returned a no-store 302 to `/auth/login?next=/`; the standalone login contained no protected shell or reusable digest client; and `/sw.js` served cache v4 with the static/offline-only contract. No password, protected data, authenticated financial page, credential/secret change, `/k/` access, manual workflow dispatch, or unrelated repair occurred. The exact command-center closeout is published separately with `[skip actions]` to avoid a second deployment.

### Work Block 4C: Transaction Identity Foundation

Status: done; confirmed and completed locally on 2026-07-19

Parent tasks: Phase 4 Tasks 1B and 2.

Included findings: `P3-3A-01` and paired coverage item `P3-3A-C01` only.

Outcome: document and implement a source-aware deterministic transaction-identity contract that lets legitimate source-distinct and same-source duplicate transactions coexist while exact source-payload redelivery remains idempotent; preserve entity isolation, existing transaction primary keys and references, negative-debit semantics, edits, splits, order matches, imports, and effective reporting; and add focused maintained synthetic coverage.

Why this grouping: identity computation, additive upgrade safety, import/Plaid identity call sites, and focused regression coverage share one foundational contract and one temporary all-entity verification path. Plaid cursor atomicity and every downstream repair consume this contract but introduce different persistence, coordination, and risk boundaries, so they remain later blocks.

Excluded: completed Task 1A; Tasks 3-4; every finding except `P3-3A-01` and `P3-3A-C01`; Plaid cursor atomicity, reconciliation, liability, freshness, failure isolation, observability, entry-point behavior, and live sync; vendor, payroll, planning, reporting, downstream, `/k/`, cookie/CSP, mobile, and unrelated repairs; real databases, financial or payroll rows, uploads, credentials, production/demo access, Plaid, Fly, workflows, downstream writes, or other live actions; commit, push, PR, merge, deployment; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

Identity defaults confirmed by Ryan:

- A non-empty authoritative external transaction ID, such as a Plaid transaction ID, is the source identity and is not replaced by the current date/amount/description hash.
- File imports use a documented stable source/batch fingerprint plus occurrence ordinal among otherwise identical normalized rows, so legitimate duplicates within one payload coexist and exact payload re-import remains idempotent.
- Empty external IDs are never shared identity keys. If safe behavior requires Plaid persistence or cursor changes, stop and leave that work to the later Plaid atomicity block.
- Existing transaction primary keys and their split/order references must survive the populated synthetic upgrade path; no destructive regeneration is allowed.
- Import and Plaid call-site scope is identity computation only. Persistence ordering, cursor commits, reconciliation, and concurrency remain excluded.

Autonomous owner and recommended agent: Codex Desktop in the current task. The block tightly couples source-contract documentation, additive migration judgment, import and Plaid call-site integration, synthetic upgrade verification, cleanup, Runway OS stewardship, and final intake. The independent Fable 5 review already endorsed this block with high confidence, so another second opinion is not recommended before implementation.

Runner path: completed in the current Codex task on `codex/transaction-identity-foundation` without delegation.

Blocking questions: none. Ryan confirmed the source-aware duplicate, authoritative-ID, upgrade-preservation, and empty-ID boundaries through Task 8.

Non-blocking defaults: write `command-center/transaction-identity-contract.md` before code changes; use an additive ordered migration only if needed; pin maintained coverage to `scripts/smoke_test.py`; run all verification with temporary synthetic Personal, BFM, and Luxe Legacy databases; deny outbound networking; remain local-only.

Expected surfaces: `command-center/transaction-identity-contract.md`; `core/imports.py`; additive migration logic in `core/db.py` only if required; the identity-computation call site in `web/routes/plaid.py`; focused checks in `scripts/smoke_test.py`; and Runway OS source/state/dashboard/closeout artifacts. Other product surfaces are read-only unless an unexpected dependency triggers a stop.

Stop conditions:

- The identity contract requires real transaction rows, credentials, production inspection, or another live action.
- An additive upgrade cannot preserve existing primary keys, splits, order matches, aliases, and exact-redelivery behavior in populated synthetic tests.
- The repair would rewrite an applied migration or destructively regenerate existing transaction IDs.
- Manual, file-import, and Plaid identity semantics cannot share a safe explicit contract without another Ryan decision.
- Empty external-ID handling requires changing Plaid persistence, cursor behavior, reconciliation, or entry-point semantics.
- Import or Plaid call-site changes expand beyond identity computation.
- Baseline or focused verification fails in a way that changes the plan, disposable cleanup cannot be proven, or the command center cannot refresh and pass health checks.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- focused all-entity checks for same-natural-key transactions from distinct accounts or sources, legitimate same-source duplicates, exact payload re-import, non-empty authoritative external IDs, empty-ID non-aliasing, and deterministic behavior;
- populated pre-change synthetic migration coverage preserving transaction IDs, splits, order matches, aliases, edits, negative-debit convention, and effective reporting;
- import and mocked Plaid identity call-site checks with outbound networking denied;
- disposable cleanup, `jq empty command-center/state.json`, dashboard refresh, command-center health check, `git diff --check`, generated-dashboard inspection, and final worktree review.

Dashboard closeout: update source files first; align `state.json`; refresh and health-check the dashboard; record 4C as done only if every required check passes. If a stop condition is hit, record the exact restart point and leave Phase 4 current.

Durability: local-only. No commit, push, PR, merge, deployment, workflow, credential, protected-data, or live action occurred.

Report point: return the written identity contract, exact source/migration/test changes, focused and full synthetic results, populated-upgrade evidence, disposable cleanup, preserved boundaries, branch/worktree state, remaining release gate, and the recommended first separate boundary/truthfulness block.

Suggested next block after completion: a separately planned 4D boundary/truthfulness repair, provisionally starting with `P3-3F-01` BFM-only payroll route enforcement plus focused payroll boundary coverage. Final 4D sizing waits for 4C closeout evidence.

Result: the written contract and implementation replace new file natural-key collisions with versioned source/account/occurrence identity, make non-empty Plaid transaction IDs authoritative for newly issued keys, preserve populated legacy Plaid bindings, and require no schema migration. The maintained suite passes across all entities, including exact redelivery, same-source duplicates, populated legacy IDs, edits, negative debits, splits, order matches, aliases, effective reporting, empty-ID rejection, and a socket-denied Plaid seam. The disposable test root was removed and all command-center checks passed.

Evidence: `command-center/transaction-identity-contract.md`, `command-center/logs/2026-07-19-transaction-identity-foundation-4c.md`, `core/imports.py`, `web/routes/plaid.py`, and `scripts/smoke_test.py`.

### Work Block 4C-R: Durability And Release

Status: done under Ryan's 2026-07-19 direct instruction to commit and push the completed work to `main`.

Included: exact intended Task 8/4C source, maintained test, contract, second-opinion, closeout, and command-center artifacts; explicit staging; one source commit; fast-forward local `main`; direct push to `origin/main`; read-only observation of the automatic Fly workflow; credential-free `/health`; and one command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; real databases or financial/payroll rows; credentials; authenticated production pages; Plaid calls or cursor changes; workflow dispatch; Fly mutation outside the automatic main-push workflow; downstream writes; `/k/`; 4D or unrelated repairs; force push; and recovery beyond the exact path.

Stop conditions: unexpected publish paths or sensitive content; remote divergence; failed verification or deployment; credential/protected-data requirements; or any recovery outside the authorized path.

Report point: return both commits, automatic workflow result, credential-free health, final main alignment, preserved exclusions, and the next separately planned 4D gate.

Result: source commit `4a84f49` was pushed directly to `main`. Automatic Fly Deploy run `29689659579` and deploy job `88200026060` passed every reported step for that exact SHA. Production `/health` returned HTTP 200 without credentials. The pre-existing untracked sync script remained excluded, and this command-center-only closeout uses `[skip actions]` so it does not trigger a second deployment.

Evidence: `command-center/logs/2026-07-19-transaction-identity-release-4c-r.md`, source commit `4a84f49`, and GitHub Actions run `29689659579`.

### Confirmed Work Block 4D: BFM-Only Payroll Boundary

Status: done and locally verified on 2026-07-19; release not authorized

Parent tasks: Phase 4 Task 1C and the focused payroll-boundary slice of Task 2.

Included findings: `P3-3F-01` and only the boundary-focused portion of `P3-3F-C01`.

Outcome: every `/payroll/` read and mutation enforces the maintained BFM-only boundary before a payroll route parses an upload, opens payroll tables, or changes data. Personal and Luxe Legacy direct requests leave payroll rows and temporary import payloads unchanged, while normal BFM behavior remains intact.

Why this grouping: the route guard and focused regression coverage share the payroll blueprint, entity boundary, temporary all-entity databases, and request-level verification. The remaining payroll findings use broader employee-matching, compensation, validation, XLSX-parser, and temporary-retention contracts and stay in Task 1M.

Excluded: completed Tasks 1A-1B and 4; Tasks 1D-1P and 3; every finding except `P3-3F-01` and the focused `P3-3F-C01` slice; remaining payroll matching, compensation, validation, malformed-workbook, and temporary-payload repairs; migrations and template changes unless a verified boundary dependency requires stopping for Ryan; real databases, payroll/HR/financial rows, uploads, credentials, production/demo access, Plaid, Fly, workflows, downstream writes, or other live actions; commit, push, PR, merge, deployment; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

Owner and recommended agent: Codex Desktop in the current task. This small sensitive-boundary repair couples Flask blueprint behavior, synthetic all-route verification, cleanup, Runway OS stewardship, and final intake; no delegation or second opinion is needed.

Runner path: current Codex task on local branch `codex/bfm-payroll-boundary` after this active block is durable and dashboard-verified.

Non-blocking defaults: use one payroll-blueprint guard before route handlers; redirect non-BFM payroll requests to the dashboard, matching existing entity-denial conventions; preserve all eight payroll route behaviors for BFM; use temporary synthetic Personal, BFM, and Luxe Legacy databases only; make no migration, template, network, or real-upload change.

Stop conditions:

- Enforcement cannot occur before payroll table or upload access without expanding beyond the payroll blueprint.
- A conflicting route type requires a new user-facing denial contract or other Ryan decision.
- Work expands into Task 1M or another subsystem.
- Verification requires real payroll/financial data, credentials, production/demo access, or another live action.
- Baseline or focused verification fails in a way that changes the plan, disposable cleanup cannot be proven, or command-center refresh/health fails.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- focused Personal, BFM, and Luxe Legacy coverage for all payroll GET/POST routes;
- prove denied requests create no employees, pay changes, payroll entries, or temporary import payloads;
- confirm normal BFM roster, detail, import, and spending behavior remains intact;
- Python compilation, disposable cleanup, `jq empty command-center/state.json`, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update source files first, align `state.json`, refresh and health-check the dashboard, and mark 4D done only after every required check passes.

Durability: local-only. No commit, push, PR, merge, deployment, workflow, credential, protected-data, or live action is included.

Report point: return the exact guard behavior, all-route and all-entity evidence, unchanged-data and temporary-payload evidence, full and focused test results, files changed, cleanup, preserved exclusions, branch state, and the separate release gate.

Suggested next block: separately plan 4E for Task 1D, the Luxe Legacy planning-route boundary with its focused `P3-3D-C01` coverage slice.

Result: one payroll-blueprint `before_request` guard now redirects every non-BFM payroll request to the dashboard before any payroll handler reaches storage or upload parsing. The maintained smoke suite enumerates all eight registered payroll routes, verifies sixteen Personal/Luxe Legacy denial outcomes with unchanged employee, pay-change, payroll-entry, and temporary-payload state, and confirms all eight BFM route paths remain available. Baseline and final smoke runs, Python compilation, exact temporary-payload cleanup, whitespace checks, dashboard refresh, and command-center health passed. No migration, template, real data, credential, external call, live action, or GitHub durability occurred.

Evidence: `web/routes/payroll.py`, `scripts/smoke_test.py`, and `command-center/logs/2026-07-19-bfm-only-payroll-boundary-4d.md`.

### Work Block 4D-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: exact intended 4D application, maintained-test, evidence, and command-center paths; explicit staging; one source commit on `codex/bfm-payroll-boundary`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly workflow; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; real databases or payroll/HR/financial rows; uploads; credentials; authenticated production pages; Plaid calls; workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream writes; 4E and unrelated repairs; force push; and recovery beyond the exact fast-forward publish path.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; or recovery would exceed the authorized path.

Verification: exact path and sensitive-string review; baseline/final maintained synthetic suite; Python compilation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; and sanitized `[skip actions]` closeout publication.

Report point: return both commits, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separately planned 4E gate.

Result: the exact nine-path 4D source set was committed as `7f7f71e`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29691622134` and job `88205268889` passed every reported step for that exact source SHA. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The untracked sync script remained excluded, no protected data or credentials were used, and no manual workflow or Fly action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-bfm-only-payroll-boundary-release-4d-r.md`, source commit `7f7f71e`, and GitHub Actions run `29691622134`.

### Confirmed Work Block 4E: Luxe Legacy Planning Boundary

Status: done and locally verified on 2026-07-19; release not authorized

Parent tasks: Phase 4 Task 1D and the focused planning-boundary slice of Task 2.

Included findings: `P3-3D-02` and only the boundary-focused portion of `P3-3D-C01`.

Outcome: every Long-Term and Short-Term Planning request denies Luxe Legacy at the blueprint boundary before a route handler can read account names or mutate planning, transaction, budget, goal, snapshot, action, or Personal singleton state. Personal and BFM planning behavior, including read-only Long-Term Planning sharing, remains intact.

Why this grouping: both planning blueprints need the same early entity guard and can be verified through one temporary three-entity database harness. The route repair and focused coverage share one outcome, implementation seam, verification path, and risk class.

Excluded: completed Tasks 1A-1C and 4; Tasks 1E-1P and 3; every finding except `P3-3D-02` and the focused `P3-3D-C01` boundary slice; remaining broad planning coverage and demo goal/snapshot seeding; APR, snapshot, depreciation, Weekly, and Waterfall calculation repairs; templates and migrations unless an unexpected boundary dependency triggers a stop; real databases, financial/payroll/HR rows, uploads, credentials, production/demo access, Plaid, Fly, workflows, downstream writes, or other live actions; commit, push, PR, merge, deployment; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

Owner and recommended agent: Codex Desktop in the current task. This deterministic boundary repair couples two Flask blueprints, all-route synthetic verification, cleanup, Runway OS stewardship, and final intake; no delegation or second opinion is needed.

Runner path: current Codex task on local branch `codex/luxe-legacy-planning-boundary` after this active block is dashboard-verified.

Blocking questions: none.

Non-blocking defaults: add one `before_request` Luxe Legacy guard to each planning blueprint; redirect denied requests to the dashboard; remove redundant index-only checks if safely superseded; enumerate all 21 registered route rules; use temporary synthetic Personal, BFM, and Luxe Legacy databases only; preserve Personal/BFM planning and Long-Term read-only sharing; remain local-only.

Stop conditions:

- Enforcement cannot occur before every planning handler without changing another subsystem.
- An endpoint requires a new user-facing denial contract or Ryan product decision.
- Personal/BFM sharing or ordinary planning behavior cannot be preserved.
- Work expands into calculation repairs, demo seeding, templates, migrations, Task 1E-1P, Task 3, or another subsystem.
- Verification requires protected data, credentials, external access, or another live action.
- Baseline or focused verification fails in a way that changes the plan, cleanup cannot be proven, or command-center refresh/health fails.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py`.
- Maintained Luxe Legacy denial coverage across all 21 registered Long-Term and Short-Term Planning route rules.
- Before/after snapshots proving denied requests leave all three entity databases unchanged and reveal no Personal/BFM account names.
- Personal/BFM Long-Term sharing and ordinary planning route behavior remain available.
- Python compilation, disposable cleanup, `jq empty command-center/state.json`, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update source files first, align `state.json`, refresh and health-check the dashboard, and mark 4E done only after every required check passes.

Durability: local-only. No commit, push, PR, merge, deployment, workflow, credential, protected-data, or live action is included.

Report point: return exact guard behavior, all-route denial evidence, unchanged-database and no-account-name evidence, preserved Personal/BFM behavior, full and focused test results, cleanup, changed files, branch state, and the separate release gate.

Suggested next block: separately propose 4E-R for durability, automatic deployment observation, credential-free production health, and sanitized closeout. Task 1E remains the next implementation block after any separately authorized release decision.

Result: one `before_request` guard on each planning blueprint now redirects Luxe Legacy to the dashboard before any of the 21 registered Long-Term or Short-Term Planning route handlers can run. Maintained coverage enumerates every route rule, replaces every planning view with a fail-fast sentinel during denied requests, proves all three temporary entity databases remain logically unchanged, verifies denied responses expose neither Personal nor BFM account names, and confirms Personal/BFM Long-Term sharing, account helpers, and Short-Term page availability remain intact. Baseline and final smoke runs, Python compilation, temporary-directory cleanup, `git diff --check`, dashboard refresh, and command-center health passed. No template, migration, real data, credential, external call, live action, or GitHub durability occurred.

Evidence: `web/routes/planning.py`, `web/routes/short_term_planning.py`, `scripts/smoke_test.py`, and `command-center/logs/2026-07-19-luxe-legacy-planning-boundary-4e.md`.

### Work Block 4E-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: exact intended 4E application, maintained-test, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/luxe-legacy-planning-boundary`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly workflow; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; Plaid calls; workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream writes; Task 1E or unrelated repairs; force push; and recovery beyond the exact fast-forward publish path.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; or recovery would exceed the authorized path.

Verification: exact path and sensitive-string review; baseline/final maintained synthetic suite; Python compilation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separately planned Task 1E gate.

Result: the exact ten-path 4E source set was committed as `1a277b0`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29694423318` and deploy job `88212585378` passed every reported step for that exact source SHA. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The untracked sync script and unrelated `command-center/now 2.md` remained excluded, no protected data or credentials were used, and no manual workflow or Fly action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-luxe-legacy-planning-boundary-release-4e-r.md`, source commit `1a277b0`, and GitHub Actions run `29694423318`.

### Confirmed Work Block 4F: Luxe Legacy Downstream Selection Boundary

Status: done and locally verified on 2026-07-19; release not authorized

Parent tasks: Phase 4 Task 1E and only the Owner Draw/source-selection slice of Task 2.

Included findings: `P3-3I-01` and the focused selection-boundary portion of `P3-3I-C01`.

Outcome: reconcile the optional Luxe Legacy mirror with the maintained LL category contract so `Owner Draw` cannot cross the downstream selection boundary, while valid LL sale and purchase categories remain eligible and scheduled/public sync seams retain LL-only invocation.

Why this grouping: the incorrect category exclusion and focused regression coverage share one selection function, one mocked HTTP boundary, and one temporary all-entity verification path.

Excluded: Tasks 1F-1P and Tasks 3-4 except the focused Task 2 slice; every finding except `P3-3I-01` and the selected `P3-3I-C01` slice; empty Plaid-ID handling; duplicate conflict keys; local or remote idempotency changes; downstream schema inspection or writes; broader request/failure coverage; real databases or financial rows; credentials; production/demo access; Plaid calls; workflows; Fly; other live actions; commit, push, PR, merge, deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop in the current task. This deterministic repair couples the mirror selection contract, maintained synthetic coverage, strict downstream boundaries, cleanup, Runway OS stewardship, and final intake; no delegation or second opinion is needed.

Runner path: current Codex task on local branch `codex/luxe-legacy-downstream-selection` after this active block is dashboard-verified.

Blocking questions: none.

Non-blocking defaults: keep a mirror-specific explicit exclusion contract reconciled with `categories.md`; preserve `Internal Transfer` and `Credit Card Payment`; replace nonexistent LL `Owner Contribution` with `Owner Draw`; use fake configuration, mocked HTTP, denied outbound sockets, and temporary all-entity databases; make no request-shape, timeout, failure-isolation, empty-ID, duplicate-key, schema, or downstream-contract change; remain local-only.

Stop conditions:

- Correct selection requires changing the category model, downstream schema, idempotency behavior, or another subsystem.
- Valid LL sale or purchase categories cannot remain eligible, or scheduled/public LL-only invocation cannot be preserved.
- Verification requires real data, credentials, external networking, downstream access, or another live action.
- Scope reaches empty identifiers, duplicate keys, production, deployment, GitHub durability, or another Phase 4 task.
- Baseline or final verification changes the plan, disposable cleanup cannot be proven, or command-center refresh/health fails.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- maintained failing-before/passing-after coverage proving `Owner Draw` is omitted and valid LL categories remain eligible;
- focused coverage proving Personal and BFM never become bridge sources and both scheduled/public seams invoke the bridge only for Luxe Legacy;
- before/after snapshots proving all three temporary entity databases remain unchanged and mocked HTTP proving no real request occurs;
- Python compilation, disposable cleanup, `jq empty command-center/state.json`, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update source files first, align `state.json`, refresh and health-check the dashboard, and mark 4F done only after every required check passes.

Durability: local-only. No commit, push, PR, merge, deployment, workflow, credential, protected-data, downstream write, or other live action is included.

Report point: return the exact selection behavior changed; focused and full synthetic results; preserved valid categories and LL-only invocation; unchanged-database and no-network evidence; cleanup; changed paths; branch state; remaining idempotency and release gates; and the separately planned Task 1F point.

Suggested next block: separately plan 4G for Task 1F, making partial sync failures machine-detectable to the scheduled workflow.

Result: the mirror-specific exclusion set now uses the maintained Luxe Legacy `Owner Draw` category while preserving `Internal Transfer` and `Credit Card Payment`. Maintained synthetic coverage reproduced the original leak before the repair and now proves Owner Draw stays local, valid Cost of Goods and Income rows remain eligible, direct bridge execution reads only Luxe Legacy without changing any entity database, and scheduled/public sync seams invoke the mirror only for Luxe Legacy. Fake configuration, mocked HTTP, and denied sockets prevented external calls. Baseline and final smoke, Python compilation, disposable cleanup, JSON validation, dashboard refresh, health check, and whitespace checks passed. Empty-ID handling, duplicate conflict keys, downstream idempotency, live access, GitHub durability, and deployment remained excluded.

Evidence: `core/luxury_bridge.py`, `scripts/smoke_test.py`, `command-center/issues.md`, and `command-center/logs/2026-07-19-luxe-legacy-downstream-selection-4f.md`.

### Work Block 4F-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: exact intended 4F application, maintained-test, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/luxe-legacy-downstream-selection`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; empty-ID or idempotency repairs; Task 1F or unrelated work; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; or recovery would exceed the authorized path.

Verification: exact path and sensitive-string review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separately planned Task 1F gate.

Result: the exact nine-path 4F source set was committed as `ce0c1b6`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29695007172` and job `88214137931` passed every reported step for that exact source SHA. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The untracked sync script and unrelated `command-center/now 2.md` remained excluded, no protected data or credentials were used, and no manual workflow, non-automatic Fly, Plaid, or downstream action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-luxe-legacy-downstream-selection-release-4f-r.md`, source commit `ce0c1b6`, and GitHub Actions run `29695007172`.

### Work Block 4G: Scheduled Sync Result Truthfulness

Status: done; confirmed and completed locally on 2026-07-19

Parent tasks: Phase 4 Task 1F and only the scheduled-result slice of Task 2.

Included findings: `P3-3H-01` and the matching workflow-visible result slice of `P3-3H-C01` only.

Outcome: make `/plaid/sync-all` return HTTP 200 and top-level success only when every entity result is error-free; make any nested entity error machine-detectable to the existing `curl --fail` workflow while preserving a sanitized per-entity result; distinguish partial from all-entity failure; treat an error-free skipped entity as successful; and add focused maintained synthetic coverage.

Why this grouping: route-level result aggregation and the exact workflow-visible regression proof share one HTTP contract, one mocked entity-result seam, and one temporary synthetic verification path. Authorization-before-entity-setup, exception isolation, coordination, persistence, public-worker behavior, and workflow release use different risk and verification paths and remain later.

Excluded: completed Tasks 1A-1E; Tasks 1G-1P and Tasks 3-4 except the focused Task 2 slice; `P3-3H-02` through `P3-3H-07`, including authorization-before-entity-setup (`P3-3H-06`); entity exception isolation, cross-process coordination, public `/k/` synchronization, cursor/removal behavior, vendor-item scope, thread-launch throttling, Plaid persistence, and workflow edits; real databases or financial rows, uploads, credentials, production/demo access, Plaid calls, workflow dispatch/rerun, Fly, downstream access/writes, or other live actions; commit, push, PR, merge, deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop in the current task. The deterministic repair couples route behavior, workflow-visible status semantics, maintained synthetic coverage, protected-data boundaries, cleanup, Runway OS stewardship, and final intake. The independent Fable 5 review already recommended this exact early micro-fix, so no additional second opinion or delegation is needed.

Runner path: current Codex task on local branch `codex/scheduled-sync-result-truthfulness` after this active block is dashboard-verified.

Blocking questions: none.

Non-blocking defaults: preserve the existing per-entity result shape without widening error detail; return `ok: true` only when every `errors` list is empty; keep error-free `skipped: true` results successful; return `ok: false` and a failure-class HTTP status for any nested error; distinguish partial from all-entity failure in a top-level status; preserve current missing/wrong bearer, missing configuration, contention, uncaught-exception, lock-release, and entity-order behavior; leave `.github/workflows/daily-plaid-sync.yml` unchanged; use fake secrets, mocked entity results, temporary all-entity databases, and denied outbound networking; remain local-only.

Expected surfaces: `web/routes/plaid.py`; focused maintained checks in `scripts/smoke_test.py`; read-only reference to `.github/workflows/daily-plaid-sync.yml`; `command-center/issues.md`; one sanitized 4G closeout log; and Runway OS roadmap, now, decisions, state, and dashboard files. No migration, workflow edit, or live-system surface is expected.

Stop conditions:

- Correct behavior requires changing entity failure isolation, Plaid persistence, cursor handling, coordination, workflow configuration, authentication/setup ordering, or another task.
- A response would expose a credential, secret, financial row, or newly widened error detail.
- Verification requires real data, credentials, Plaid, downstream networking, workflow execution, production/demo access, or another live action.
- Existing consumers require a product decision about a materially different response contract.
- Baseline or focused verification fails in a plan-changing way, disposable cleanup cannot be proven, or command-center refresh/health fails.
- Scope reaches GitHub durability, deployment, `P3-3H-06`, or another Phase 4 task.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- focused complete-success, harmless-skip, one-entity partial-failure, all-entity failure, absent/wrong bearer, missing configuration, contention, unchanged exception, lock-release, entity-order, and secret-safe response checks;
- deterministic localhost-only or equivalent proof that the partial-failure HTTP response is rejected by the existing `curl --fail` contract;
- mocked entity results, denied outbound networking, temporary all-entity databases, and disposable cleanup;
- Python compilation, `jq empty command-center/state.json`, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update source files first, align `state.json`, refresh and health-check the dashboard, and mark 4G done only after every required check passes.

Durability: local-only. Commit, push, PR, merge, deployment, workflow mutation/execution, credential access, protected data, Plaid, downstream access/write, and other live actions remain excluded.

Report point: return the exact top-level and HTTP result contract; focused and full synthetic results; workflow-visible failure proof; preserved bearer, contention, exception, entity-order, and error-detail behavior; no-network and cleanup evidence; changed paths; branch state; and the separate release gate.

Suggested next block: separately plan 4H for Task 1G, restoring the Recurring Charges report query with focused reporting coverage.

Result: `/plaid/sync-all` now returns HTTP 200 with `ok: true` and `status: success` only when every entity result is error-free. One or more nested errors return HTTP 502 with `ok: false` and `status: partial_failure`, while errors in every entity return `status: failure`; error-free skipped entities remain successful and the existing per-entity results are preserved without wider error detail. Maintained synthetic coverage proves success, skips, partial and total errors, bearer/configuration/contention behavior, unchanged exception and lock release semantics, entity order, secret-safe output, and an actual localhost-only `curl --fail` exit 22. Baseline and final smoke suites, Python compilation, disposable cleanup, JSON validation, dashboard refresh, health check, and whitespace checks passed. No workflow edit/execution, real data, credential, Plaid, downstream, production/demo, GitHub durability, deployment, or other live action occurred.

Evidence: `web/routes/plaid.py`, `scripts/smoke_test.py`, `command-center/issues.md`, and `command-center/logs/2026-07-19-scheduled-sync-result-truthfulness-4g.md`.

### Work Block 4G-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: exact intended 4G application, maintained-test, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/scheduled-sync-result-truthfulness`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; `P3-3H-06`; broader sync-entry repairs; Task 1G or unrelated work; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-string review, direct-main durability, attributable automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Blocking questions: none. Ryan directly authorized commit and push to `main` for the completed 4G scope.

Non-blocking defaults: use explicit intended paths; preserve both unrelated untracked files; commit first on the feature branch; require local `main`, `origin/main`, and the feature-branch base to align before fast-forwarding; push without force; inspect the automatic deploy result without opening protected logs unless failure diagnosis is necessary; verify only credential-free `/health`; publish the post-release command-center closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; staging includes either excluded untracked file; maintained verification fails; the source commit cannot be fast-forwarded safely; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; the closeout push starts another deploy; or recovery would exceed the authorized path.

Verification: exact path, staged-set, sensitive-pattern, branch ancestry, and remote-alignment review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; source commit and direct-main fast-forward push; automatic Fly run/job result for the exact source SHA; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separately planned Task 1G point.

Result: the exact nine-path 4G source set was committed as `d206737`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29695920703` and deploy job `88216548891` passed every reported step for that exact source SHA. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The untracked sync script and unrelated `command-center/now 2.md` remained excluded; the staged sensitive-addition scan returned zero; and no protected data, credentials, authenticated production page, manual workflow, non-automatic Fly, Plaid, downstream, workflow-edit, broader repair, or unrelated action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-scheduled-sync-result-truthfulness-release-4g-r.md`, source commit `d206737`, GitHub Actions run `29695920703`, and Fly deploy job `88216548891`.

### Work Block 4H: Recurring Charges Report Repair

Status: done; confirmed and completed locally on 2026-07-19

Parent tasks: Phase 4 Task 1G and only the recurring-report slice of Task 2.

Included findings: `P3-3C-01` and the matching recurring-report slice of `P3-3C-C01` only.

Outcome: construct the Recurring Charges query with the maintained entity-specific exclusion contract; preserve raw bank-level grouping and existing merchant, amount, date, presentation, and filename semantics; restore direct, prepared, rendered, CSV, and PDF paths in Personal, BFM, and Luxe Legacy; return normal empty or not-found responses for empty and out-of-range requests; and add focused maintained synthetic regression coverage.

Why this grouping: the query correction and focused regression proof share one reporting helper, the same recurring-only route and export surfaces, one temporary all-entity dataset, and one verification path. Broader financial read-model coverage and the primary-Plaid sequence use materially different scope, risk, and verification paths.

Excluded: completed Tasks 1A-1F; Tasks 1H-1P; Tasks 3-4; the remainder of Task 2 and `P3-3C-C01`; changes to the broad reporting model, split-transaction behavior, category definitions, templates, database schema, subscription detection, or cash-flow recurrence; real databases or financial/payroll/HR rows, uploads, credentials, production/demo, Plaid, workflows, Fly, downstream access/writes, or other live actions; commit, push, PR, merge, deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop in the current task. This is a small, acceptance-check-driven repair tightly coupled to synthetic verification and command-center closeout, so the current central policy favors Codex and no delegation or second opinion is needed.

Runner path: current Codex task on local branch `codex/recurring-charges-report-repair` after the active-block dashboard is verified.

Blocking questions: none.

Non-blocking defaults: keep recurring detection on raw bank transactions rather than split allocations; use the current entity-specific `categories.md` exclusion contract; preserve grouping, statistics, dates, UI shape, and filenames; keep Luxe Legacy `Owner Draw` eligible because it is not marked excluded while BFM `Owner Contribution` and `Partner Buyout` remain excluded; use temporary synthetic all-entity databases only; and remain local-only.

Expected surfaces: `core/reporting.py`; focused maintained checks in `scripts/smoke_test.py`; conditional recurring-only handling in `web/routes/reports.py` if required; read-only reference to `categories.md` and the recurring report template; `command-center/issues.md`; one sanitized 4H closeout log; and Runway OS roadmap, now, decisions, state, and dashboard files. No migration or template change is expected.

Stop conditions:

- Correct behavior requires changing the broader reporting model, transaction splits, category definitions, templates, schema, subscription detection, cash-flow recurrence, or another Phase 4 task.
- A product decision is needed about recurring grouping, category eligibility, presentation, or the definition of done.
- Verification requires real data, credentials, external access, production/demo, Plaid, workflow execution, Fly, downstream access/write, or another live action.
- Baseline or focused verification fails in a plan-changing way, disposable cleanup cannot be proven, or command-center refresh/health fails.
- Scope reaches GitHub durability, deployment, either preserved untracked file, or another excluded task.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- focused direct helper, prepared report, rendered HTMX view, CSV, and PDF checks across temporary Personal, BFM, and Luxe Legacy databases;
- repeated-merchant count, average, minimum, maximum, first-date, last-date, category, entity-specific exclusion, empty-range, out-of-range, missing-input, and unchanged-database assertions;
- Python compilation, `jq empty command-center/state.json`, disposable cleanup, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update source files first, align `state.json`, refresh and health-check the dashboard, and mark 4H done only after every required check passes.

Durability: local-only. Commit, push, PR, merge, deployment, protected data, credentials, real databases, live systems, Plaid, workflows, Fly, downstream access/write, and other live actions remain excluded.

Report point: return the exact query contract; all-entity direct, view, CSV, and PDF results; exclusion and empty-range behavior; full smoke result; cleanup evidence; changed paths; local branch state; preserved exclusions; and the separate release gate.

Suggested next block: separately plan 4H-R Durability And Release if Ryan wants the verified repair published; otherwise stop locally before planning Task 1H.

Result: the Recurring Charges query now interpolates the maintained entity-specific exclusion clause instead of sending a literal helper token to SQLite. Negative debit summaries now report the smaller absolute charge as minimum and the larger as maximum. Maintained synthetic coverage reproduced the failing-before error and now passes direct, prepared, rendered, CSV, PDF, summary, exclusion, empty, out-of-range, missing-input, unchanged-database, and exact-cleanup checks across Personal, BFM, and Luxe Legacy. The baseline and final smoke suites, Python compilation, JSON validation, disposable cleanup, whitespace checks, dashboard refresh, and health check pass. No real data, credentials, external access, live action, migration, category/template change, GitHub durability, or deployment occurred.

Evidence: `core/reporting.py`, `scripts/smoke_test.py`, `command-center/issues.md`, and `command-center/logs/2026-07-19-recurring-charges-report-repair-4h.md`.

### Work Block 4H-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: explicit staging of the exact intended 4H application, maintained-test, issue, evidence, and command-center paths; one source commit on `codex/recurring-charges-report-repair`; fast-forward alignment of local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; broader reporting, Task 1H, and unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, attributable automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Blocking questions: none. Ryan directly instructed Codex to commit and push the completed 4H work to `main`.

Non-blocking defaults: use the exact nine intended paths; preserve both unrelated untracked files; commit first on the feature branch; require local `main`, `origin/main`, and the feature-branch base to align before fast-forwarding; push without force; inspect the automatic deploy result without opening protected logs unless failure diagnosis is necessary; verify only credential-free `/health`; and publish the post-release command-center closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; staging includes either excluded untracked file; maintained verification fails; the source commit cannot be fast-forwarded safely; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; the closeout push starts another deploy; or recovery would exceed the authorized path.

Verification: exact path, staged-set, sensitive-pattern, branch-ancestry, GitHub-authentication, and remote-alignment review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; source commit and direct-main fast-forward push; automatic Fly run/job result for the exact source SHA; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separate Task 1H planning gate.

Result: the exact nine-path 4H source set was committed as `166bbd9`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29696691569` and deploy job `88218551351` passed every reported step for that exact source SHA. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The untracked sync script and unrelated `command-center/now 2.md` remained excluded; the staged high-confidence sensitive-addition scan returned zero; and no protected data, credentials, authenticated production page, manual workflow, non-automatic Fly, Plaid, downstream, workflow-edit, broader repair, or unrelated action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-recurring-charges-report-release-4h-r.md`, source commit `166bbd9`, GitHub Actions run `29696691569`, and Fly deploy job `88218551351`.

### Work Block 4I: Plaid Transaction Sync Atomicity

Status: done and locally verified on 2026-07-19; release not authorized

Parent tasks: Phase 4 Task 1H and only the cursor-safety and rollback slice of Task 2.

Included findings: `P3-3G-01` and the matching focused slice of `P3-3G-C01` only.

Outcome: apply every fetched addition, modification, removal, final cursor, and `last_synced` update atomically for each Plaid item; distinguish exact-redelivery no-ops from genuine persistence errors; roll back all item mutations and preserve the stored cursor and timestamp when any persistence or cursor write fails; and add focused maintained synthetic coverage across Personal, BFM, and Luxe Legacy with mocked Plaid responses and denied outbound networking.

Why this grouping: transaction mutations and final cursor advancement share one per-item SQLite transaction, one failure boundary, and one all-entity mocked verification path. Reconciliation, liabilities, freshness, missing-modification observability, item isolation, and scheduled/public coordination use different contracts and remain later tasks.

Excluded: completed Tasks 1A-1G; Tasks 1I-1P and 3-4; the remainder of Task 2 and `P3-3G-C01`; `P3-3G-02` through `P3-3G-07`; `P3-3H-02` through `P3-3H-07`; reconciliation, cached-balance preservation, liabilities, freshness, link cleanup, missing-modification observability, item failure isolation, scheduled/public concurrency, public removed-event behavior, automatic Plaid retries, and downstream behavior; migrations unless an unexpected dependency triggers a stop; real databases or financial/payroll/HR rows, uploads, credentials, production/demo, live Plaid, workflows, Fly, downstream access/writes, or other live actions; commit, push, PR, merge, deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Atomicity defaults:

- Fetch every available page from the stored starting cursor before local persistence, then apply the accepted transaction events and the final cursor in one per-item SQLite transaction.
- Treat exact redelivery as an explicit idempotent no-op, but allow genuine insert, update, delete, or cursor-write errors to abort the transaction.
- On any persistence failure, roll back all mutations from that item and leave both its stored cursor and `last_synced` unchanged.
- Do not add automatic network retries. A pagination failure remains visible; because no local cursor moves, a later attempt begins from the original stored cursor as required by the Plaid pagination contract.
- Preserve enabled-account filtering, source-aware transaction identity, negative-debit semantics, splits, exact redelivery, entity isolation, and current successful result counts.

Autonomous owner and recommended agent: Codex Desktop in the current task. This block couples financial-integrity semantics, mocked integration behavior, cross-file implementation, synthetic verification, protected-data boundaries, and Runway OS stewardship. The previous independent review already pre-split the Plaid family into atomicity, reconciliation, and isolation/observability, so no additional delegation or second opinion is needed.

Runner path: current Codex task on local branch `codex/plaid-sync-atomicity` without delegation.

Blocking questions: none.

Non-blocking defaults: write a concise Plaid sync atomicity contract before code changes; keep the existing aggregate-pages-before-persist architecture unless source verification proves a smaller safe seam; pin maintained coverage to `scripts/smoke_test.py`; use temporary synthetic all-entity databases, fake tokens, mocked Plaid responses, and denied outbound sockets; and remain local-only.

Expected surfaces: `command-center/plaid-sync-atomicity-contract.md`; `web/routes/plaid.py`; `core/plaid_client.py` only if the pagination seam requires adjustment; focused checks in `scripts/smoke_test.py`; `command-center/issues.md`; one sanitized 4I closeout log; and Runway OS roadmap, now, decisions, state, and dashboard files. No migration is expected.

Stop conditions:

- Correctness requires a migration, real transaction inspection, credentials, a live Plaid call, or another external action.
- The repair expands into reconciliation, liabilities, freshness, link cleanup, missing-modification observability, item isolation, entry-point coordination, public-worker behavior, downstream behavior, or another Phase 4 task.
- Existing transaction identities, splits, exact-redelivery behavior, enabled-account filtering, or entity isolation cannot be preserved.
- Plaid pagination cannot be handled safely without a new automatic retry or product-contract decision.
- Baseline or focused verification fails in a plan-changing way, disposable cleanup cannot be proven, or command-center refresh/health fails.
- Scope reaches GitHub durability, deployment, either preserved untracked file, or another excluded action.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- maintained all-entity success and multi-page final-cursor checks;
- forced failures during additions, modifications, removals, and cursor update proving full rollback, unchanged starting cursor and timestamp, and unchanged unrelated rows;
- exact-redelivery idempotency, successful retry from the preserved starting cursor, enabled-account filtering, signed-amount and split preservation, mocked Plaid responses, and denied outbound sockets;
- Python compilation, `jq empty command-center/state.json`, disposable cleanup, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update source files first, align `state.json`, refresh and health-check the dashboard, and mark 4I done only after every required check passes.

Durability: complete and verified locally on `codex/plaid-sync-atomicity`. Commit, push, PR, merge, deployment, protected data, credentials, real databases, live systems, Plaid, workflows, Fly, downstream access/write, and other live actions remain excluded.

Report point: return the exact transaction/cursor contract, changed paths, focused and full synthetic results, rollback and cleanup evidence, local branch state, preserved exclusions, and the separate release gate.

Suggested next block: separately plan 4J Plaid Reconciliation, Liability, And Freshness Truthfulness for Task 1I after 4I evidence is complete.

Result: the sync path now applies each item's accepted additions, modifications, removals, final cursor, and `last_synced` inside one explicit SQLite transaction. Exact Plaid redelivery remains an idempotent no-op; genuine persistence errors propagate to the existing item error path; rolled-back counters are not reported; and a failed attempt leaves the starting cursor, timestamp, prior rows, and splits intact. Maintained coverage passes two-page aggregation, success, redelivery, enabled-account filtering, signed amounts, removal, twelve forced all-entity add/modify/remove/cursor failures, retry from the original cursor, denied outbound sockets, and exact cleanup. Baseline and final smoke suites, Python compilation, JSON validation, whitespace checks, dashboard refresh, and health check pass with no migration or live action.

Evidence: `command-center/plaid-sync-atomicity-contract.md`, `web/routes/plaid.py`, `scripts/smoke_test.py`, `command-center/issues.md`, and `command-center/logs/2026-07-19-plaid-sync-atomicity-4i.md`.

### Work Block 4I-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: the exact ten intended 4I application, maintained-test, contract, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/plaid-sync-atomicity`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `web/routes/plaid.py`; `scripts/smoke_test.py`; `command-center/plaid-sync-atomicity-contract.md`; `command-center/logs/2026-07-19-plaid-sync-atomicity-4i.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; live Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; reconciliation, liabilities, freshness, Task 1I, broader Plaid work, and unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the prior 4I test and contract; use only credential-free production `/health`; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-string review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separate Task 1I planning gate.

Result: the exact ten-path 4I source set was committed as `46f8286`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29697681136` and deploy job `88221144959` passed every reported step for exact source SHA `46f82863d5f15cc4a68f06cbc98f443a65dbf4b7`. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The staged high-confidence sensitive-addition scan returned zero; the untracked sync script and unrelated `command-center/now 2.md` remained excluded; and no protected data, credentials, authenticated production page, manual workflow, non-automatic Fly, live Plaid, downstream, workflow-edit, Task 1I, force-push, or unrelated action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-plaid-sync-atomicity-release-4i-r.md`, source commit `46f8286`, GitHub Actions run `29697681136`, and Fly deploy job `88221144959`.

### Confirmed Work Block 4J: Plaid Reconciliation, Liability, And Freshness Truthfulness

Status: done and locally verified on 2026-07-19; release not authorized

Parent tasks: Phase 4 Task 1I and only the matching primary-Plaid slice of Task 2.

Included findings: `P3-3G-02`, `P3-3G-03`, `P3-3G-04`, `P3-3G-05`, and the matching focused slice of `P3-3G-C01`.

Outcome: make Plaid account-state refresh truthful and preservation-safe by reconciling cached Plaid balances only within each successfully fetched item, preserving failed-item and manual account state, removing the unsafe first-word manual-account deletion heuristic from link exchange, fetching and caching liabilities independently from balance freshness, and preventing one fresh account or partial failure from making stale siblings appear current.

Why this grouping: per-item reconciliation, manual-account preservation, liability refresh, and freshness share the Plaid account lifecycle, `plaid_items` / `plaid_accounts` / `account_balances` state, Cash Flow refresh path, state-preservation risk, and one mocked all-entity verification model. Task 1J changes transaction-update observability and corrupt-token isolation inside the sync worker, while Task 1K changes scheduled/public entry points; both use different contracts and remain later.

Included: Task 1I and only the matching `P3-3G-C01` portion of Task 2.

Excluded: completed Tasks 1A-1H; Tasks 1J-1P and Tasks 3-4; the remainder of Task 2 and `P3-3G-C01`; `P3-3G-06`, `P3-3G-07`, and every remaining `P3-3H` finding; missing-modification observability, corrupt-token isolation, scheduled/public coordination, downstream behavior, and unrelated repairs; destructive migration or rewriting an applied migration; real databases or financial/payroll/HR rows, uploads, credentials, authenticated production pages, production/demo access, live Plaid, workflows, Fly, downstream access/writes, or external actions; commit, push, PR, merge, deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Autonomous owner and recommended agent: Codex Desktop in the current task. This sensitive financial-integrity block couples contract design, cross-file implementation, additive-schema judgment, synthetic all-entity verification, protected-data boundaries, Runway OS stewardship, and final intake. The prior independent review already endorsed this second primary-Plaid sub-block, so no delegation or additional second opinion is needed.

Runner path: current Codex task on local branch `codex/plaid-account-truthfulness` without delegation.

Blocking questions: none.

Non-blocking defaults:

- Preserve every manual account during Plaid linking unless an explicit stable placeholder identity exists; remove the first-word name deletion heuristic rather than inventing a new match.
- Reconcile cached Plaid accounts per successfully fetched item. An item failure is not authoritative evidence that its prior rows disappeared.
- Keep balance freshness distinct from liability freshness so one successful fetch cannot suppress the other.
- Use an additive, ordered migration only if source inspection proves separate freshness state requires it; never rewrite an applied migration.
- Preserve last-known-good account and liability values when the relevant Plaid call fails.
- Use temporary all-entity databases, fake tokens, mocked Plaid responses, denied outbound sockets, and exact cleanup; remain local-only.

Expected surfaces: a sanitized Plaid account-state contract under `command-center/`; `web/routes/cashflow.py`; `web/routes/plaid.py`; `core/db.py` only if an additive freshness migration is necessary; focused checks in `scripts/smoke_test.py`; `command-center/issues.md`; one sanitized 4J closeout log; and Runway OS roadmap, now, decisions, state, and dashboard files.

Stop conditions:

- Correctness requires protected data, credentials, live Plaid, production inspection, or another external action.
- A safe design requires destructive migration, rewriting an applied migration, or guessing existing production state.
- Manual-account cleanup needs a product rule beyond preserving all unmatched manual rows.
- Work expands into Task 1J, sync-entry coordination, downstream behavior, or another repair family.
- Entity isolation, last-known-good account state, or failure preservation cannot be maintained.
- Baseline or focused verification changes the plan, cleanup cannot be proven, command-center checks fail, or scope reaches GitHub durability, deployment, or either preserved untracked file.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- maintained Personal, BFM, and Luxe Legacy cases proving per-item reconciliation, partial-item failure preservation, authoritative disabled/removed-account cleanup, and manual-row preservation;
- normal stale loads fetching both balances and liabilities, mixed freshness not hiding stale siblings, liability failure remaining distinguishable while preserving last-known-good values, and similar-name manual accounts surviving link exchange;
- mocked Plaid responses, fake tokens, denied outbound sockets, populated synthetic upgrade-path coverage if a migration is required, unchanged failure snapshots, and exact disposable cleanup;
- Python compilation, `jq empty command-center/state.json`, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update human-readable sources first, align `state.json`, refresh and health-check the dashboard, and mark 4J done only after every required check passes.

Durability: complete and verified locally on `codex/plaid-account-truthfulness`. Commit, push, PR, merge, deployment, protected data, credentials, real databases, live systems, Plaid, workflows, Fly, downstream access/write, and other external actions remain excluded.

Report point: return the exact account-state contract, changed paths, whether a migration was needed, focused and full synthetic results, failure-preservation and cleanup evidence, local branch state, preserved exclusions, and the separate release gate.

Suggested next block: separately plan 4K Plaid Item Isolation And Truthful Observability for Task 1J plus only its matching Task 2 slice after 4J evidence is complete.

Result: additive migration 58 now stores separate nullable per-item account and liability freshness markers. Cash Flow reconciles only successfully fetched items, preserves failed siblings and every manual row, removes authoritative disabled/investment/removed rows even with an empty keep set, fetches liabilities independently from balances, preserves last-known-good fields and markers on failure, distinguishes successful empty liability responses, and invalidates both markers on account toggle. Plaid Link no longer deletes manual rows by first-word name matching. The baseline and final smoke suites, Python compilation, populated upgrade path, 28 focused all-entity assertions, denied networking, exact cleanup, JSON validation, whitespace checks, dashboard refresh, and health check pass without protected data or live action.

Evidence: `command-center/plaid-account-state-contract.md`, `core/db.py`, `web/routes/cashflow.py`, `web/routes/plaid.py`, `scripts/smoke_test.py`, `command-center/issues.md`, and `command-center/logs/2026-07-19-plaid-account-state-truthfulness-4j.md`.

### Work Block 4J-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: the exact twelve intended 4J application, additive migration, maintained-test, contract, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/plaid-account-truthfulness`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `core/db.py`; `web/routes/cashflow.py`; `web/routes/plaid.py`; `scripts/smoke_test.py`; `command-center/plaid-account-state-contract.md`; `command-center/logs/2026-07-19-plaid-account-state-truthfulness-4j.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; live Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; Task 1J, broader Plaid work, and unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the verified 4J contract, migration, implementation, and tests; use only credential-free production `/health`; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-string review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separate Task 1J / 4K planning gate.

Result: the exact twelve-path 4J source set was committed as `74ad56d`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29699120063` and deploy job `88225014833` passed every reported step for exact source SHA `74ad56d1caf7e5c03b9863354ee61a9f11421604`. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main`. The staged high-confidence sensitive-addition scan returned zero; the untracked sync script and unrelated `command-center/now 2.md` remained excluded; and no protected data, credentials, authenticated production page, manual workflow, non-automatic Fly, live Plaid, downstream, workflow-edit, Task 1J implementation, force-push, or unrelated action occurred. This command-center-only closeout is published separately with `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-plaid-account-state-truthfulness-release-4j-r.md`, source commit `74ad56d`, GitHub Actions run `29699120063`, and Fly deploy job `88225014833`.

### Confirmed Work Block 4K: Plaid Item Isolation And Truthful Observability

Status: done and locally verified on 2026-07-19; release not authorized

Parent tasks: Phase 4 Task 1J and only the matching primary-Plaid slice of Task 2.

Included findings: `P3-3G-06`, `P3-3G-07`, and the matching item-isolation and observability slice of `P3-3G-C01`.

Outcome: isolate access-token decryption and transaction-update failures per Plaid item so healthy sibling items continue; make modified and removed counts reflect actual affected rows; treat a missing modified target as a safe item failure that rolls back the item and preserves its cursor and `last_synced`; preserve already-absent removals as idempotent zero-row events; return only sanitized item-level errors; and add focused maintained all-entity synthetic coverage.

Why this grouping: token isolation, missing-modification truthfulness, affected-row counts, item-level error reporting, cursor preservation, and focused coverage all share the primary `_sync_entity()` item loop, `_apply_plaid_transaction_updates()` transaction boundary, one result contract, and one mocked all-entity verification model. Task 1K changes scheduled/public orchestration and cross-process coordination and therefore remains separate.

Included: Task 1J and only the matching `P3-3G-C01` portion of Task 2.

Excluded: completed Tasks 1A-1I; Tasks 1K-1P and Tasks 3-4; the remainder of Task 2 and `P3-3G-C01`; every remaining `P3-3H` finding; scheduled/public sync coordination, `/k/`, cross-process locking, entity-level entry-point recovery, automatic retries, downstream behavior, and unrelated repairs; schema migration or rewriting an applied migration; real databases or financial/payroll/HR rows, uploads, credentials, authenticated production pages, production/demo access, live Plaid, workflows, Fly, downstream access/writes, or other external actions; commit, push, PR, merge, deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Autonomous owner and recommended agent: Codex Desktop in the current task. This sensitive financial-integrity block couples contract design, primary sync implementation, maintained all-entity verification, protected-data boundaries, exact cleanup, Runway OS stewardship, and final intake. The prior independent Task 8 review already endorsed a separate isolation/observability block, so no delegation or additional second opinion is needed.

Runner path: current Codex task on local branch `codex/plaid-item-isolation-observability` without delegation.

Blocking questions: none.

Non-blocking defaults:

- Decrypt each token inside its item-level exception boundary. A corrupt item produces one sanitized error and no Plaid request, while healthy sibling items continue.
- A missing modified target raises the existing stable item persistence failure, rolls back all work for that item, and preserves its cursor and timestamp for retry. Do not implicitly reconstruct or upsert a missing modified row.
- Modified and removed counts use actual affected transaction rows. An already-absent removal is an idempotent zero-row event and does not fail the item.
- Preserve existing transaction identity, cursor atomicity, exact-redelivery behavior, enabled-account filtering, signs, splits, entity isolation, and successful sibling counts.
- Use temporary Personal, BFM, and Luxe Legacy databases, fake tokens, mocked Plaid responses, denied outbound sockets, and exact cleanup; remain local-only.

Expected surfaces: a sanitized Plaid item-isolation and observability contract under `command-center/`; `web/routes/plaid.py`; focused checks in `scripts/smoke_test.py`; `command-center/issues.md`; one sanitized 4K closeout log; and Runway OS roadmap, now, decisions, state, and dashboard files. `core/crypto.py` and prior Plaid contracts are read-only unless an unexpected dependency triggers a stop. No migration is expected.

Stop conditions:

- Correctness requires protected data, credentials, live Plaid, production inspection, a migration, or another external action.
- Safe missing-modification behavior requires implicit recovery or upsert semantics beyond the confirmed conservative error-and-retry default.
- Sanitized reporting cannot avoid exposing token, ciphertext, financial, or protected detail.
- Work expands into Task 1K, scheduled/public coordination, downstream behavior, or another repair family.
- Entity isolation, per-item cursor preservation, healthy-sibling continuation, exact redelivery, or cleanup cannot be maintained.
- Baseline or focused verification changes the plan, Runway OS cannot refresh and pass health checks, or scope reaches GitHub durability, deployment, or either preserved untracked file.

Verification:

- baseline and final `.venv/bin/python scripts/smoke_test.py`;
- maintained Personal, BFM, and Luxe Legacy cases with corrupt-first and corrupt-last sibling items proving only the failed item errors, no Plaid request occurs for its bad token, healthy siblings commit, and error text contains no token or ciphertext;
- missing-modification cases proving the item rolls back, its starting cursor and `last_synced` remain unchanged, successful siblings still commit, and retry remains available;
- modified and removed counts based on actual affected rows, including idempotent already-absent removals, plus unchanged exact-redelivery, enabled-account filtering, signed amounts, splits, and entity isolation;
- mocked Plaid responses, fake tokens, denied outbound sockets, exact disposable cleanup, Python compilation, `jq empty command-center/state.json`, dashboard refresh, health check, `git diff --check`, generated-dashboard inspection, and final explicit-path worktree review.

Dashboard closeout: update human-readable sources first, align `state.json`, refresh and health-check the dashboard, and mark 4K done only after every required check passes.

Durability: local-only. Commit, push, PR, merge, deployment, protected data, credentials, real databases, live systems, Plaid, workflows, Fly, downstream access/write, and other external actions remain excluded.

Report point: return the exact item-isolation and observability contract, changed paths, focused and full synthetic results, cursor-preservation and healthy-sibling evidence, sanitized-error proof, cleanup, local branch state, preserved exclusions, and the separate release gate.

Suggested next block: separately decide 4K-R Durability And Release. After any authorized release, separately plan Task 1K.

Result: access-token decryption now runs inside each primary Plaid item's exception boundary, corrupt items return stable sanitized errors without making a Plaid request, and healthy siblings continue regardless of whether the failed item is ordered before or after them. Missing modified targets now fail atomically, roll back any earlier item mutations, preserve the starting cursor and `last_synced`, and report no rolled-back counters. Modified and removed totals use actual SQLite affected rows; removal split cleanup covers all matching transactions; and already-absent removals remain zero-count idempotent successes. The baseline and final smoke suites, Python compilation, 36 focused all-entity assertions, denied networking, exact cleanup, JSON validation, whitespace checks, dashboard refresh, and health check pass without a migration, protected data, credential, live action, GitHub durability, or deployment.

Evidence: `command-center/plaid-item-isolation-observability-contract.md`, `web/routes/plaid.py`, `scripts/smoke_test.py`, `command-center/issues.md`, and `command-center/logs/2026-07-19-plaid-item-isolation-observability-4k.md`.

### Work Block 4K-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free health verified on 2026-07-19

Included: the exact ten intended 4K application, maintained-test, contract, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/plaid-item-isolation-observability`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `web/routes/plaid.py`; `scripts/smoke_test.py`; `command-center/plaid-item-isolation-observability-contract.md`; `command-center/logs/2026-07-19-plaid-item-isolation-observability-4k.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; live Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; Task 1K, broader sync-entry work, and unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the verified 4K contract, implementation, tests, and evidence; use only credential-free production `/health`; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separate Task 1K planning gate.

Result: the exact ten-path 4K source set was committed as `72d2bba`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29700530131` and deploy job `88228726512` passed every reported step for exact source SHA `72d2bbaed19bee431ce8bee12e41ef891c0fedd2`. Production `/health` returned HTTP 200 without credentials, and local `main` matched `origin/main` before closeout. The staged high-confidence sensitive-addition scan returned zero; the untracked sync script and unrelated `command-center/now 2.md` remained excluded; and no protected data, credentials, authenticated production page, manual workflow, non-automatic Fly, live Plaid, downstream, workflow-edit, Task 1K implementation, force-push, or unrelated action occurred. This command-center-only closeout uses `[skip actions]` to avoid a second deployment.

Evidence: `command-center/logs/2026-07-19-plaid-item-isolation-observability-release-4k-r.md`, source commit `72d2bba`, GitHub Actions run `29700530131`, and Fly deploy job `88228726512`.

### Confirmed Work Block 4L: Sync Entry Coordination And Truthful Recovery

Status: done and verified locally on 2026-07-19; release not authorized

Included: Task 1K for `P3-3H-02` through `P3-3H-07`, plus only the matching `P3-3H-C01` Task 2 regression-coverage slice. Establish one process-safe coordination contract across manual, scheduled, and dashboard-triggered Plaid sync; preserve the current `/k/` refresh-on-view trigger while routing it through the maintained primary sync core; apply removed events atomically; exclude vendor items; continue healthy later scheduled entities after one entity exception with structured sanitized partial results; put bearer authorization before normal entity setup; and consume the dashboard-trigger throttle only after successful worker launch.

Excluded: Tasks 1L-1P; the remainder of Task 2; Tasks 3-4; `/k/` authentication or other public-route policy changes; automatic retry queues or new services; database migrations unless a changed plan is separately confirmed; workflow edits or execution; real databases or financial, payroll, or HR rows; uploads; credentials; authenticated production pages; live Plaid; production/demo access; Fly; downstream contract changes or writes; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop. The block couples a process-level coordination contract, sensitive financial-integrity boundaries, cross-file integration, true multiprocess synthetic proof, and Runway OS stewardship.

Reviewer route: direct Claude CLI using `claude-fable-5` at `max` effort in read-only plan mode with no session persistence. Codex will write a sanitized repo-backed review packet, intake the critique, and either move 4L to active when the confirmed scope remains intact or stop in awaiting-confirmation if the critique materially changes scope. The exact route must not silently fall back.

Review result: completed successfully with no fallback. The reviewer endorsed the scope unchanged and required per-entity initialization after authorization, configured-auth endpoint coverage, three deliberate maintained-check updates, deletion of the duplicate dashboard bridge call, and explicit `flock`-only/never-unlink invariants. Codex accepted all five and activated local implementation. The review inferred that configured server auth may currently redirect scheduled workflow requests before bearer validation while `curl --fail` remains green; this is source-derived urgency evidence, not live verification or release authority.

Expected surfaces: a small shared coordinator under `core/` or an equivalent reviewed location; `web/routes/plaid.py`; `web/routes/kristine.py`; `web/__init__.py`; `scripts/smoke_test.py`; a sanitized sync-entry coordination contract and 4L closeout log; `command-center/issues.md`; and the Runway OS roadmap, now, decisions, state, and dashboard.

Defaults: keep `/k/` access behavior unchanged for later Task 1P; preserve refresh-on-view but remove its duplicate transaction-application logic; coordinate manual, scheduled, and dashboard-triggered entry points; prefer a non-blocking volume-backed process-safe lock under the configured or temporary `DATA_DIR`, with automatic release on process exit and no migration; keep contention non-queued; preserve the existing downstream invocation contract; continue later scheduled entities after one exception; keep errors sanitized; exclude vendor items; and make failed worker launch immediately retryable.

Stop conditions: coordination requires cross-machine infrastructure beyond the current mounted-volume runtime; the lock cannot prove process-exit cleanup or mutual exclusion across existing entry points; correctness requires a `/k/` access-policy change, protected data, credentials, live Plaid, production inspection, a migration, or a downstream contract change; the current refresh-on-view behavior needs a new product decision; verification reveals a materially different architecture or scope; command-center checks fail; or work overlaps either preserved untracked file.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; true two-process contention using temporary synthetic `DATA_DIR`; manual/scheduled/dashboard mutual exclusion; removed-event atomicity; vendor-item exclusion; scheduled entity-exception continuation and truthful partial results; unauthorized bearer rejection before entity initialization or category sync; failed-launch immediate retry; fake tokens, mocked Plaid, denied outbound sockets, all-entity isolation, and exact cleanup; Python compilation; JSON validation; dashboard refresh; command-center health; `git diff --check`; dashboard inspection; and explicit worktree review.

Report point: return the exact reviewed coordination contract, reviewer disposition, changed paths, multiprocess proof, scheduled/manual/dashboard behavior, focused and full synthetic results, cleanup evidence, local branch state, preserved exclusions, and the separate 4L-R release gate.

Result: added one stable mode-0600 `DATA_DIR` `fcntl.flock` lease shared by manual, scheduled, and dashboard-triggered Plaid entry points; proved same-process separate-open and real two-process contention plus normal and SIGKILL cleanup; exempted `/plaid/sync-all` from browser session/entity setup so constant-time bearer validation precedes mutation; initialized and contained each authorized scheduled entity with structured sanitized continuation; rewrote dashboard launch ownership and throttle ordering; reused the maintained atomic non-vendor `_sync_entity` core; and removed the duplicate bridge call. Baseline and final full smoke, Python compilation, configured-auth, actual dashboard removal/vendor, denied-network, exact-cleanup, JSON, whitespace, dashboard, and health checks pass without protected data, live systems, migration, release, or either preserved untracked file.

Evidence: `core/sync_coordination.py`; `web/routes/plaid.py`; `web/routes/kristine.py`; `web/__init__.py`; `scripts/smoke_test.py`; `command-center/sync-entry-coordination-contract.md`; `command-center/logs/second-opinion/2026-07-19-phase-4-4l-fable-5-max.md`; and `command-center/logs/2026-07-19-sync-entry-coordination-4l.md`.

### Work Block 4L-R: Durability And Release

Status: done, durable, automatically deployed, and safely credential-free production verified on 2026-07-19

Included: the exact fifteen intended 4L application, maintained-test, contract, review, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/sync-entry-coordination`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; one missing-bearer `/plaid/sync-all` request with redirects disabled; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `core/sync_coordination.py`; `web/routes/plaid.py`; `web/routes/kristine.py`; `web/__init__.py`; `scripts/smoke_test.py`; `command-center/sync-entry-coordination-contract.md`; `command-center/handoffs/second-opinion/2026-07-19-phase-4-4l-sync-entry-coordination.md`; `command-center/logs/second-opinion/2026-07-19-phase-4-4l-fable-5-max.md`; `command-center/logs/2026-07-19-sync-entry-coordination-4l.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; an authorized bearer or live Plaid call; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; Tasks 1L-1P; broader Task 2; Tasks 3-4; unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, safe credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the verified 4L contract, implementation, tests, review, and evidence; use only credential-free production `/health` plus a missing-bearer request that cannot enter synchronization; do not supply `SYNC_SECRET`, inspect authenticated pages, or trigger Plaid; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health or the missing-bearer `401` boundary fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; missing-bearer `/plaid/sync-all` HTTP 401 with redirects disabled; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free health and missing-bearer proof, final main alignment, preserved exclusions, and the remaining natural scheduled-run observation boundary.

Result: the exact fifteen-path 4L source set was committed as `2a12533`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29711640510` and deploy job `88256335090` passed every reported step for exact source SHA `2a12533d637060ce2ea91ff205b30cde3cbbc99a`. Production `/health` returned HTTP 200, and a credential-free missing-bearer `/plaid/sync-all` request returned HTTP 401 with redirects disabled, proving the repaired boundary without entering Plaid synchronization. Local `main` matched `origin/main` before closeout; the staged high-confidence sensitive-addition scan returned zero; both preserved untracked files remained excluded; and no protected data, credential, authenticated production page, authorized bearer, manual workflow, non-automatic Fly, live Plaid, downstream, workflow edit, Task 1L implementation, force push, or unrelated action occurred. This command-center-only closeout uses `[skip actions]` to avoid a second deployment. The next natural scheduled run remains the safe proof of real scheduled synchronization.

Evidence: `command-center/logs/2026-07-19-sync-entry-coordination-release-4l-r.md`, source commit `2a12533`, GitHub Actions run `29711640510`, and Fly deploy job `88256335090`.

### Confirmed Work Block 4M: Vendor Payment Matching Integrity

Status: complete and verified locally on 2026-07-20; release not authorized

Included: Task 1L.1 plus only the focused vendor-payment matching slice of Task 2. Replace the nonexistent `transactions.matched_order_id` dependency with one explicit vendor-to-bank relationship contract; preserve exact-match auto-application and likely/loose review; prevent stale or duplicate application from overwriting an unrelated transaction; preserve target-entity isolation; and add maintained exact, review, unmatched, apply, rollback, and isolation coverage using temporary synthetic databases.

Excluded: Tasks 1L.2-1P; the remainder of Task 2; Tasks 3-4; existing-invalid-row detection or remediation; the low-priority import `Undo` wording issue; vendor line-item persistence; category-domain enforcement; real databases or financial rows; uploads; credentials; live Plaid or vendor access; authenticated production pages; manual workflow dispatch, rerun, or authentication; Fly operations; downstream access or writes; migration or backfill unless Ryan separately approves a changed plan; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: Task 1L.1 and its focused regression slice restore one currently broken payment-matching workflow through one relationship contract and one all-entity synthetic verification path. Tasks 1L.2 and 1L.3 use different parser, persistence, auto-split, category-domain, and remediation contracts and remain separate.

Owner and recommended agent: Codex Desktop in the current task. This sensitive-retrofit block tightly couples financial-integrity behavior, local source changes, temporary all-entity verification, and final Runway OS stewardship. No delegation or second opinion is needed for the deterministic missing-column defect.

Expected surfaces: `core/vendor_matching.py`; focused additions to `scripts/smoke_test.py`; a concise vendor-payment matching contract; a sanitized 4M closeout log; relevant `command-center/issues.md` disposition; and the Runway OS roadmap, now, decisions, state, and dashboard. `core/db.py` is expected to remain unchanged; evidence that a migration is required triggers a stop.

Defaults: treat `vendor_transactions.matched_transaction_id` as the canonical relationship; permit at most one vendor match per bank transaction; keep exact-match auto-application and likely/loose review behavior; reject stale or duplicate application without unrelated mutation; make no historical repair or schema change; use local branch `codex/vendor-payment-matching-integrity`; and keep commit, push, PR, merge, release, and live verification separately gated.

Activation gate: passed on 2026-07-20. Using sanitized unauthenticated public GitHub REST metadata filtered to `event=schedule`, workflow `256886458` was `active` and run `29740509073` was created at `2026-07-20T11:59:33Z`, completed with conclusion `success`, and satisfied freshness and incomplete-run thresholds. No logs, response bodies, manual dispatch, authentication, or acceleration action occurred.

Stop conditions: the activation run is missing or unsuccessful; repair requires real data, credentials, production inspection, live vendor/Plaid activity, a schema migration, backfill, or historical duplicate decision; one-bank-to-one-vendor semantics conflict with tracked source; work expands into another task; focused or full verification changes the plan; command-center refresh or health fails; or either preserved untracked file would be touched.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; fresh temporary Personal, BFM, and Luxe Legacy databases; exact, review, unmatched-vendor, unmatched-bank, accepted, stale, duplicate, rollback, and cross-entity cases; proof that only the intended bank transaction is enriched; denied outbound networking and exact cleanup; Python compilation; JSON validation; dashboard refresh; command-center health; `git diff --check`; dashboard inspection; and explicit worktree review.

Report point: return the natural post-release run evidence, exact matching contract, changed paths, focused and full synthetic results, confirmation that no migration was needed or the precise stop reason, cleanup evidence, local branch state, preserved exclusions, and the separate release gate.

Suggested next action: work block 4M-R is complete; define and confirm the next bounded Task 1M work block separately before implementation.

Activation result: the first natural post-`2a12533` scheduled run `29740509073` completed successfully, clearing the 4M gate. Evidence: `command-center/logs/2026-07-20-natural-scheduled-run-4m-gate.md`.

Result: matching now uses `vendor_transactions.matched_transaction_id` as the canonical relationship and never queries or writes nonexistent `transactions.matched_order_id`. Candidate selection, exact application, and accepted batches use immediate SQLite write transactions; stale, duplicate, missing, and already-claimed relationships reject without unrelated mutation; and successful application enriches only the selected bank transaction. Baseline and final maintained smoke suites, Python compilation, fresh all-entity exact/review/unmatched/accepted/stale/duplicate/two-writer/rollback/isolation cases, denied networking, exact cleanup, JSON, whitespace, dashboard, and health checks pass. No migration, backfill, historical-row action, protected data, application-integration request, live system, GitHub durability, or deployment occurred. Evidence: `command-center/vendor-payment-matching-contract.md` and `command-center/logs/2026-07-20-vendor-payment-matching-4m.md`.

### Confirmed Work Block 4M-R: Vendor Payment Matching Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-20

Included: the exact verified 4M application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/vendor-payment-matching-integrity`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial rows; uploads; credentials; authenticated production pages; live vendor or Plaid calls; manual workflow dispatch or rerun; workflow edits; non-automatic Fly changes; downstream access or writes; migrations, backfills, or historical remediation; Tasks 1M-1P; broader Task 2; Tasks 3-4 except this exact 4M durability action; unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4M contract and implementation; observe only the automatic Fly deployment caused by the main push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1M planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final main alignment, preserved exclusions, and the Task 1M planning gate.

Result: the exact ten-path 4M source set was committed as `ffd42dd`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29748373589` and deploy job `88372068257` passed every reported step for exact source SHA `ffd42dd34160a860bf12998cf3cb22e73b5b3c63`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, credential, authenticated production page, live vendor/Plaid action, manual workflow action, non-automatic Fly change, downstream access/write, migration, backfill, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-vendor-payment-matching-release-4m-r.md`.

### Confirmed Work Block 4N: Vendor Line-Item Persistence

Status: complete and verified locally on 2026-07-19; release not authorized; work block 4M is now unblocked after its scheduled-run gate passed

Included: Task 1L.2 plus only the focused vendor line-item persistence and auto-split slice of Task 2. Persist Amazon and Henry Schein parsed line items transactionally with newly inserted parent orders; preserve exact reimport idempotency; reconcile quantity, item, and parent totals in integer cents; and prove a matched multi-category new import can use the maintained auto-split path without the standalone population script.

Excluded: waiting Task 1L.1 implementation and its 4M contract; Task 1L.3 and the remainder of Task 2; Tasks 1M-1P and Tasks 3-4; existing-order detection, backfill, or remediation; category-domain redesign or enforcement; changes to import UX; real databases, financial rows, retained uploads, or original user files; credentials; live vendor or Plaid access; authenticated production pages; workflow dispatch, rerun, or authentication; Fly operations; downstream access or writes; migration; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: both parsers already produce per-order item lists, while the shared save path currently persists only parent summaries. Parent and line-item insertion, exact reimport handling, integer-cents reconciliation, and maintained auto-split proof share one import transaction, one schema already created by migration 53, and one temporary all-entity verification path. Vendor-payment matching and category-domain enforcement use different contracts and remain separate.

Owner and recommended agent: Codex Desktop in the current task. The block requires cross-file persistence design, sensitive financial-data boundaries, temporary all-entity verification, exact cleanup, and Runway OS stewardship; no delegation or second opinion is needed for this deterministic local repair.

Runner path: current Codex task on local branch `codex/vendor-line-item-persistence`. Codex owns implementation, verification, final intake, dashboard currency, and the decision whether the returned work satisfies the confirmed block.

Expected surfaces: `core/amazon.py`; narrowly scoped parser normalization only if required to preserve a shared item contract; focused additions to `scripts/smoke_test.py`; a concise vendor line-item persistence contract; a sanitized 4N closeout log; the relevant `command-center/issues.md` disposition; and Runway OS roadmap, now, decisions, state, and dashboard. `core/db.py`, production scripts, and import templates are expected to remain unchanged.

Defaults: apply only to new parent orders; skip an existing duplicate parent and do not backfill missing children; insert each import batch's parents and children in one transaction; preserve current preview, date-filter, and save UX; normalize monetary values to integer cents at persistence time; preserve existing line-item category output needed by the maintained auto-split path without widening into Task 1L.3 validation; and keep commit, push, PR, merge, release, and live verification separately gated.

Stop conditions: the natural post-`2a12533` scheduled run fails; correct persistence requires a migration, existing-row backfill, retained user files, protected data, credentials, external access, or a category-domain decision; parser money or quantity semantics cannot reconcile without changing product behavior; one import cannot remain atomic; work expands into Task 1L.1, Task 1L.3, or another repair family; focused or full verification changes the plan; command-center refresh or health fails; or either preserved untracked file would be touched.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; fresh temporary Personal, BFM, and Luxe Legacy databases; generated Amazon and Henry Schein inputs; parent-plus-child persistence, exact reimport idempotency, quantity and integer-cents reconciliation, multi-category matched auto-split, forced rollback, unchanged unrelated rows, cross-entity isolation, denied outbound networking, and exact cleanup; Python compilation; JSON validation; dashboard refresh; command-center health; `git diff --check`; dashboard inspection; and explicit worktree review.

Dashboard closeout: update human-readable sources first; align `state.json`; refresh and health-check the dashboard; record 4N as done only if every required check passes; then restore 4M as current. The scheduled gate has since cleared on 2026-07-20.

Report point: return the exact persistence contract, changed paths, Amazon and Henry Schein parent/item outcomes, cents and auto-split proof, focused and full synthetic results, confirmation that no migration or backfill was needed or the precise stop reason, cleanup evidence, local branch state, preserved exclusions, and current 4M gate status.

Suggested next work block: resume confirmed 4M immediately after the first successful natural post-`2a12533` scheduled run; otherwise stop for Ryan if that run fails.

Result: new Amazon and Henry Schein imports now persist each parent and all parser-provided children in one SQLite transaction using exact vendor, order ID, and integer-cent parent identity. Exact reimports skip parents without duplicating children; existing parents remain untouched; forced child and invalid-quantity failures roll back their new parents; raw vendor category metadata is preserved without inventing Ledger classifications; and newly persisted categorized children feed the maintained auto-split helper without the standalone population script. Generated Amazon CSV and Henry Schein XLSX inputs passed data-layer and normal HTTP preview/save coverage across temporary Personal, BFM, and Luxe Legacy databases, including quantity and cents, two-group split reconciliation, unchanged unrelated rows, denied networking, temporary-payload consumption, and exact cleanup. Baseline and final full smoke suites plus Python compilation passed. Migration 53 was sufficient, so no migration, backfill, protected data, retained user file, live action, or GitHub durability occurred. Task 1L.2 and its focused Task 2 slice are resolved locally; Task 1L.3 category-domain enforcement and 4N release remain separate.

### Work Block 4N-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free production health verified on 2026-07-19

Included: the exact ten intended 4N application, maintained-test, contract, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/vendor-line-item-persistence`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `core/amazon.py`; `scripts/smoke_test.py`; `command-center/vendor-line-item-persistence-contract.md`; `command-center/logs/2026-07-19-vendor-line-item-persistence-4n.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial rows; retained uploads or original user files; credentials; authenticated production pages; live vendor or Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; Task 1L.1 implementation; Task 1L.3; broader Task 2; Tasks 1M-1P and 3-4; unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the verified 4N contract, implementation, tests, and evidence; use only credential-free production `/health`; do not authenticate, inspect protected pages, or trigger live vendor or Plaid activity; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free health, final main alignment, preserved exclusions, and the unchanged 4M scheduled-run gate.

Result: the exact ten-path 4N source set was committed as `89236a6`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29714030248` and deploy job `88263334817` passed every reported step for exact source SHA `89236a62438c4c5063aedf6c276f0ae52fafcfbe`. Production `/health` returned HTTP 200 without credentials. Local `main` matched `origin/main` before closeout; the staged high-confidence sensitive-addition scan returned zero; both preserved untracked files remained excluded; and no protected data, credential, authenticated production page, manual workflow action, non-automatic Fly mutation, live vendor or Plaid call, downstream access or write, workflow edit, Task 1L.1 implementation, Task 1L.3 work, force push, or unrelated action occurred. This command-center-only closeout uses `[skip actions]` to avoid a second deployment. Confirmed 4M is current again at its unchanged natural scheduled-run gate.

Evidence: `command-center/logs/2026-07-19-vendor-line-item-persistence-release-4n-r.md`, source commit `89236a6`, GitHub Actions run `29714030248`, and Fly deploy job `88263334817`.

### Confirmed Work Block 4O: Deterministic Category-Domain Enforcement

Status: done and verified locally on 2026-07-19; direct-main release authorized on 2026-07-20; confirmed work block 4M is current and unblocked

Included: Task 1L.3 plus only the focused category-domain enforcement slice of Task 2. Treat each entity's current `categories.md` definition as authoritative; validate every in-scope inferred and accepted category/subcategory pair; make mixed-category vendor ties deterministic; reject invalid transaction, vendor-order, and match-application writes without changing stored data; preserve the dedicated vendor-queue `Skipped` sentinel without treating it as a financial category; and add maintained Personal, BFM, and Luxe Legacy regression coverage.

Excluded: waiting Task 1L.1 implementation and its 4M contract; completed Task 1L.2; Tasks 1M-1P; the remainder of Task 2; Tasks 3-4; existing-invalid-row detection, reporting, backfill, or remediation; the low-priority import `Undo` wording issue; category-taxonomy additions, renames, or removals; general category-management redesign; real databases or financial rows; retained uploads or original user files; credentials; live vendor or Plaid access; authenticated production pages; workflow dispatch, rerun, or authentication; Fly operations; downstream access or writes; migrations; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: entity-specific inference, deterministic vendor-category selection, acceptance validation, and focused regression coverage share one category-domain contract and one temporary all-entity verification path. Task 1L.2 is already released and supplies the persisted line-item foundation. Work block 4M uses a different vendor-payment relationship contract and remains safely waiting on an independent scheduled-run gate.

Owner and recommended agent: Codex Desktop in the current task. The block couples financial-classification behavior, several related write paths, temporary all-entity verification, and final Runway OS stewardship. No delegation or additional second opinion is needed because the safest behavior is constrained by the maintained entity definitions and explicit rejection checks.

Runner path: current Codex task on local branch `codex/category-domain-enforcement`. Codex owns implementation, verification, final intake, dashboard currency, and the decision whether the returned work satisfies the confirmed block.

Expected surfaces: `core/categories.py`; `core/amazon.py`; `core/henryschein.py`; `web/routes/categorize.py`; `web/routes/categorize_vendors.py`; the vendor-card template only if required for consistent validation UX; focused additions to `scripts/smoke_test.py`; a concise category-domain contract; a sanitized 4O closeout log; relevant `command-center/issues.md` disposition; and Runway OS roadmap, now, decisions, state, and dashboard. `categories.md`, `core/db.py`, production scripts, and unrelated categorization surfaces are expected to remain unchanged.

Defaults: use `categories.md` through the maintained entity-aware loader rather than database leftovers; fall back to `Needs Review` / `General` when an inferred pair is invalid instead of inventing an entity mapping; rank mixed-category candidates by frequency and break ties by normalized alphabetical order; prevalidate a submitted batch before any transaction, order, match, or alias mutation; show a clear error without advancing the vendor queue on invalid input; preserve `Skipped` only through the dedicated skip action; do not change the taxonomy or historical rows; and keep commit, push, PR, merge, release, and live verification separately gated.

Blocking questions: none.

Stop conditions: the natural 4M activation run completes unsuccessfully; safe enforcement requires a category-taxonomy decision, schema migration, historical-row access, detection, backfill, or remediation; dedicated `Skipped` behavior cannot be preserved without weakening the domain contract; implementation expands into general category management, Task 1L.1, or another repair family; focused or full verification materially changes the plan; command-center refresh or health fails; or either preserved untracked file would be touched.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; fresh temporary Personal, BFM, and Luxe Legacy databases; valid and invalid entity-specific inference; stable mixed-category tie results across hash seeds; valid transaction and vendor-order acceptance; invalid single and multi-row submissions with zero transaction, order, match, or alias mutation; invalid match application leaving transaction and order state unchanged; preserved dedicated `Skipped` behavior; denied outbound networking and exact cleanup; Python compilation; JSON validation; dashboard refresh; command-center health; `git diff --check`; dashboard inspection; and explicit worktree review.

Dashboard closeout: update human-readable sources first; align `state.json`; refresh and health-check the dashboard; record 4O as done only if every required check passes; then restore 4M as current. The natural scheduled gate cleared on 2026-07-20 through sanitized public evidence, so 4M is ready to resume after 4O closeout.

Report point: return the exact category-domain contract, fallback and tie behavior, changed paths, focused and full all-entity results, zero-mutation rejection proof, cleanup evidence, local branch state, preserved exclusions, and current 4M gate status.

Suggested next work block: resume already-confirmed 4M. Publication of 4O remains a separate authorization.

Result: `categories.md` is now authoritative for new in-scope category writes. Vendor inference is explicitly entity-aware, preserves valid candidates, and safely falls back to `Needs Review` / `General`; empty and `Unknown` subcategories normalize to `General`; Henry Schein equal-frequency ties resolve by frequency then normalized alphabetical order across hash seeds; and transaction batches, vendor-order saves, and accepted order matches prevalidate before any transaction, order, note, match, or alias mutation. The vendor categorization card no longer offers ad hoc subcategory creation, while the dedicated `Skipped` workflow sentinel remains intact. Baseline and final full smoke suites, focused all-entity valid/invalid and zero-mutation cases, denied networking, exact cleanup, Python compilation, JSON validation, whitespace, dashboard refresh, health, and dashboard inspection pass. No taxonomy, migration, historical-row action, protected data, live system, or GitHub durability occurred during local implementation. The natural scheduled-run gate has since cleared, so confirmed 4M is unblocked and remains separate from the authorized 4O release.

Evidence: `command-center/category-domain-contract.md` and `command-center/logs/2026-07-19-category-domain-enforcement-4o.md`.

### Work Block 4O-R: Durability And Release

Status: done, durable, automatically deployed, and credential-free production health verified on 2026-07-20

Included: the exact seventeen intended 4O application, maintained-test, contract, issue, evidence, and command-center paths, including the sanitized 4M activation-gate evidence needed to keep shared Runway OS state coherent; explicit staging; one source commit on `codex/category-domain-enforcement`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `core/amazon.py`; `core/categories.py`; `core/henryschein.py`; `scripts/smoke_test.py`; `web/routes/categorize.py`; `web/routes/categorize_vendors.py`; `web/routes/match.py`; `web/templates/components/vendor_card.html`; `command-center/category-domain-contract.md`; `command-center/logs/2026-07-19-category-domain-enforcement-4o.md`; `command-center/logs/2026-07-20-natural-scheduled-run-4m-gate.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial rows; retained uploads or original user files; credentials; authenticated production pages; live vendor or Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; 4M implementation; Tasks 1M-1P; broader Task 2; Tasks 3-4; unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release required exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the verified 4O contract, implementation, tests, and evidence; use only credential-free production `/health`; do not authenticate, inspect protected pages, or trigger live vendor or Plaid activity; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free health, final main alignment, preserved exclusions, and current unblocked 4M status.

Result: the exact seventeen-path 4O source set was committed as `5529912`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29745531202` and deploy job `88362414145` passed every reported step for exact source SHA `5529912b47003a931a33776f6ad24fe327257e25`. Production `/health` returned HTTP 200 without credentials. Local `main` matched `origin/main` before closeout; the staged high-confidence sensitive-addition scan returned zero; both preserved untracked files remained excluded; and no protected data, credential, authenticated production page, manual workflow action, non-automatic Fly mutation, live vendor or Plaid call, downstream access or write, workflow edit, 4M implementation, force push, or unrelated action occurred. This command-center-only closeout uses `[skip actions]` to avoid a second deployment. Confirmed 4M remains current and unblocked.

Evidence: `command-center/logs/2026-07-20-category-domain-enforcement-release-4o-r.md`, source commit `5529912`, GitHub Actions run `29745531202`, and Fly deploy job `88362414145`.

### Confirmed Work Block 4P: Payroll Import Integrity And Payload Lifecycle

Status: done and verified locally on 2026-07-20; release not authorized

Included: Tasks 1M.1-1M.3 plus only the focused Task 2 coverage for `P3-3F-02`, `P3-3F-05`, `P3-3F-06`, and their matching `P3-3F-C01` slice. Stabilize exact existing-employee assignment across preview and save; preserve explicit reassignment and genuinely unmatched employee creation; add an explicit BFM-only cancel action that consumes only its exact temporary payload; normalize malformed payroll workbooks into sanitized controlled outcomes without retaining a payload; and add maintained generated-workbook, temporary all-entity, isolated-payload, denied-network, and cleanup coverage.

Excluded: Tasks 1M.4-1M.5; Tasks 1N-1P; the remainder of Task 2; Tasks 3-4; roster-domain validation; compensation calculations; real payroll/HR or financial rows; retained user uploads; credentials; migrations; authentication, CSRF, encryption, or public-route policy changes; production/demo; external calls; live systems; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: exact matching, preview assignment, save, cancel, parser errors, and temporary-payload lifecycle share `core/payroll_parser.py`, the payroll routes and template, one generated-XLSX path, one isolated temporary-payload contract, and one maintained request-level verification matrix. Roster validation and compensation comparison use different mutation and calculation contracts and remain separate.

Owner and recommended agent: Codex Desktop in the current task. This sensitive-retrofit block couples payroll handling, templates, maintained synthetic tests, exact temporary cleanup, and Runway OS stewardship. External workers remain inactive for this project boundary, and no second opinion is needed because the accepted behavior has explicit checks.

Runner path: current Codex task on local branch `codex/payroll-import-integrity`. Codex owns implementation, review, verification, cleanup, final intake, dashboard currency, and the decision whether 4P satisfies the confirmed block.

Expected surfaces: `core/payroll_parser.py`; `web/routes/payroll.py`; `web/templates/payroll.html`; focused additions to `scripts/smoke_test.py`; a concise payroll-import contract; a sanitized 4P closeout log; the matching issue dispositions; and Runway OS roadmap, now, decisions, state, and dashboard. `core/db.py` is expected to remain unchanged.

Defaults: an exact normalized-name match uses the existing employee by default and ordinary save cannot create a duplicate; explicit reassignment may select another existing employee; genuinely unmatched employees may be created; ambiguous duplicate existing identities stop for Ryan; cancel uses an explicit BFM-only POST that consumes only its supplied preview payload; parser failures are sanitized without exposing file contents or internals; tests generate every workbook at runtime, isolate the temporary directory, deny networking, and use temporary all-entity databases; and commit, push, release, and live verification remain separately gated.

Blocking questions: none.

Stop conditions: implementation needs real payroll/HR data, a retained user upload, credentials, migration, authentication or CSRF policy change, production/demo, external access, or another live action; multiple existing employees share one normalized identity; safe cancellation cannot avoid unrelated-payload deletion; scope expands into Tasks 1M.4-1M.5 or another repair family; focused or full verification materially changes the plan; command-center refresh or health fails; or either preserved untracked file would be touched.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; generated exact-match, reassignment, unmatched-creation, duplicate-prevention, and reimport checks; save, cancel, missing, reused, expired, malformed, unrelated-payload, and exact-cleanup checks; corrupt, mislabeled, empty, unsupported, headerless, and valid multi-section workbook outcomes; BFM-only behavior and unchanged Personal/Luxe Legacy state; denied outbound networking; Python compilation; JSON validation; dashboard refresh; command-center health; `git diff --check`; dashboard inspection; and explicit worktree review.

Dashboard closeout: update human-readable sources first; align `state.json`; refresh and health-check the dashboard; record 4P as done only if every required check passes; and make Task 1M.4 current for the next separately confirmed block.

Report point: return the payroll-import contract, exact changed paths, matching and creation behavior, payload cleanup and malformed-workbook matrix, focused and full synthetic results, cleanup proof, local branch state, preserved exclusions, and the recommended next block.

Suggested next work block: 4Q Atomic Payroll Roster Validation for Task 1M.4 plus only its focused Task 2 coverage. Publication of 4P remains separately gated.

Result: exact normalized-name matches now select the existing employee in preview and are re-enforced during save, explicit reassignment and genuinely unmatched creation remain available, and exact reimport preserves employee and payroll-entry counts. Preview Cancel is a BFM-only exact-key POST; mode-0600 payloads handle save, cancel, missing, reused, expired, malformed, unrelated, and invalid-key cases deterministically. Unsupported filename types and workbook-engine failures return sanitized controlled outcomes without retaining payloads, while headerless and valid multi-section behavior remains explicit. Baseline and final maintained smoke suites, generated-XLSX matching and workbook cases, isolated payload lifecycle, temporary all-entity isolation, denied networking, exact cleanup, Python compilation, JSON, whitespace, dashboard, health, and rendered inspection pass. No migration, protected data, retained user upload, live system, external call, GitHub durability, or deployment occurred.

Evidence: `command-center/payroll-import-integrity-contract.md`, `command-center/logs/2026-07-20-payroll-import-integrity-4p.md`, `core/payroll_parser.py`, `web/routes/payroll.py`, `web/templates/payroll.html`, and `scripts/smoke_test.py`.

### Confirmed Work Block 4P-R: Payroll Import Integrity Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-20

Included: the exact verified twelve-path 4P application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/payroll-import-integrity`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real payroll/HR or financial rows; retained uploads; credentials; authenticated production pages; external calls; manual workflow dispatch or rerun; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Tasks 1M.4-1M.5; broader Task 2; Tasks 3-4 except this exact 4P durability action; unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4P contract and implementation; observe only the automatic Fly deployment caused by the main push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1M.4 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final main alignment, preserved exclusions, and the Task 1M.4 planning gate.

Result: the exact twelve-path 4P source set was committed as `4b2775c`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29753360363` and deploy job `88389339278` passed every reported step for exact source SHA `4b2775c403a631512d49d0fc0b8720a8495b5183`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, retained upload, credential, authenticated production page, external call, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1M.4 implementation, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-payroll-import-integrity-release-4p-r.md`.

### Confirmed Work Block 4Q: Atomic Payroll Roster Validation

Status: done and verified locally on 2026-07-20; release not authorized

Included: Task 1M.4 plus only the focused Task 2 coverage for `P3-3F-04` and its matching `P3-3F-C01` slice. Validate every manual-create, manual-update, and import-created employee row before mutation; preserve valid employee and rate-history behavior; return controlled sanitized rejection outcomes; and prove invalid or failed requests leave employees, pay changes, and payroll entries unchanged.

Excluded: Task 1M.5; Tasks 1N-1P; the remainder of Task 2; Tasks 3-4; employee deletion; duplicate-identity or roster-deduplication policy changes; compensation calculations; migrations or historical cleanup; real payroll/HR or financial rows; retained uploads; credentials; authentication or CSRF changes; production/demo; external calls; live systems; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Why this grouping: manual create, manual update, and import-created roster rows share one employee-domain contract, one BFM-only mutation boundary, and one temporary-database verification path. Their focused regression coverage is required to prove validation and rate-history behavior are atomic. Task 1M.5 changes compensation calculations and display semantics through a different verification path and remains separate.

Owner and recommended agent: Codex Desktop in the current task. This sensitive payroll block couples route behavior, transactional integrity, maintained synthetic verification, cleanup, and Runway OS stewardship. External workers remain inactive, and no second opinion is needed because the accepted contract is deterministic with explicit checks.

Runner path: current Codex task on local branch `codex/atomic-payroll-roster-validation`. Codex owns implementation, verification, cleanup, final intake, dashboard currency, and the decision whether 4Q satisfies the confirmed block.

Expected surfaces: `web/routes/payroll.py`; focused additions to `scripts/smoke_test.py`; a concise payroll-roster validation contract; a sanitized 4Q closeout log; matching issue dispositions; and Runway OS roadmap, now, decisions, state, and dashboard. Templates change only if the existing flash surface cannot return accessible controlled feedback. `core/db.py` is expected to remain unchanged.

Defaults: require a non-empty normalized name; use the maintained `ROLE_ORDER` role domain, `hourly`/`salary` pay types, and `active`/`inactive`/`terminated` statuses; accept an empty or real ISO `YYYY-MM-DD` hire date without forbidding future dates; require employee and assignment IDs to resolve inside BFM; keep Phoenix codes optional, trimmed, and nullable without a new whitelist; preserve empty-rate-as-zero; parse currency through decimal cents and reject non-numeric, non-finite, negative, or greater-than-`$999,999,999.99` rates; preserve the one-use import-payload lifecycle; and keep commit, push, release, and live verification separately gated.

Blocking questions: none.

Stop conditions: implementation needs real payroll/HR data, a retained upload, credentials, migration, identity-policy decision, authentication or CSRF change, production/demo, external access, or another live action; validation cannot preserve valid import or rate-history behavior; work expands into Task 1M.5 or another repair family; focused or full verification materially changes the plan; cleanup cannot be proven; command-center refresh or health fails; or either preserved untracked file would be touched.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused valid and invalid manual-create, manual-update, and import-created employee cases; role, pay-type, status, date, employee/assignment-ID, name, and empty/finite/negative/overflow rate matrices; before/after row snapshots proving rejected requests create no employee, pay-change, or payroll-entry mutation; forced failure proving employee update and rate-history insertion roll back together; valid zero-to-positive and positive-to-positive history behavior; BFM-only isolation; denied networking; exact temporary cleanup; Python compilation; JSON validation; dashboard refresh; command-center health; `git diff --check`; dashboard inspection; and explicit worktree review.

Dashboard closeout: update human-readable sources first; align `state.json`; refresh and health-check the dashboard; and record 4Q as done only if every required check passes.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is included.

Report point: return the exact validation contract, changed paths, rejection and rollback matrix, preserved valid behavior, focused and full synthetic results, cleanup evidence, local branch state, preserved exclusions, and the separate publication gate.

Suggested next work block: 4Q-R for exact-scope durability and automatic release if separately authorized; after that gate, separately propose 4R for Task 1M.5 like-for-like payroll peer comparisons.

Result: one shared pre-mutation validator now governs manual create, manual update, and import-created employee rows. Maintained role, pay-type, status, exact optional-date, entity-local assignment, payload-linked name, optional Phoenix-code, and bounded decimal-rate rules return controlled sanitized outcomes; empty rates, future dates, and valid rate-history behavior remain intact. Maintained coverage proves invalid create/update/import requests leave complete payroll snapshots unchanged, positive-to-positive and zero-to-positive history rules remain explicit, forged assignment names and missing IDs reject, rejected payloads are consumed exactly once, and forced post-history plus post-employee persistence failures roll back whole transactions. Baseline and final smoke suites, Python compilation, BFM-only isolation, denied networking, exact cleanup, JSON, whitespace, dashboard refresh, health, and rendered inspection pass. No migration, template, protected data, retained upload, external call, GitHub durability, deployment, or live action occurred. Evidence: `command-center/payroll-roster-validation-contract.md`, `command-center/logs/2026-07-20-atomic-payroll-roster-validation-4q.md`, `web/routes/payroll.py`, and `scripts/smoke_test.py`.

### Confirmed Work Block 4Q-R: Atomic Payroll Roster Validation Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-20

Included: the exact verified ten-path 4Q application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/atomic-payroll-roster-validation`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real payroll/HR or financial rows; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow dispatch or rerun; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1M.5; broader Task 2; Tasks 3-4 except this exact 4Q durability action; unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4Q contract and implementation; observe only the automatic Fly deployment caused by the main push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1M.5 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final main alignment, preserved exclusions, and the separate Task 1M.5 planning gate.

Result: the exact ten-path 4Q source set was committed as `3f3ffb2`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29761239024` and deploy job `88416099000` passed every reported step for exact source SHA `3f3ffb2b9d487d99afd2daacb956c69c3921e1c2`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, retained upload, credential, authenticated production page, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1M.5 implementation, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-atomic-payroll-roster-validation-release-4q-r.md`.

### Confirmed Work Block 4R: Like-For-Like Payroll Peer Comparisons

Status: done and verified locally on 2026-07-20; release not authorized

Parent tasks: Phase 4 Task 1M.5 and only its focused Task 2 regression slice.

Included findings: `P3-3F-03` and the matching compensation-comparison slice of `P3-3F-C01` only.

Outcome: compute and display peer compensation from other active employees with the same role and pay type; keep hourly and salary values separate without annualization; distinguish a real zero-rate average from an empty cohort; and cover mixed, multiple-peer, single-member, inactive, zero-rate, and empty cases with maintained synthetic checks.

Why this grouping: the compensation helper, employee-detail JSON, modal presentation, and focused regression coverage form one small payroll vertical slice with one temporary-BFM verification path. Task 1N begins a different calculation family, Task 3 changes CI, and Task 4 introduces a separately gated publication and live-deployment path.

Excluded: Tasks 1M.1-1M.4; Tasks 1N-1P; the remainder of Task 2; Tasks 3-4; employee import, identity, deletion, validation, or pay-history changes; migrations or historical cleanup; real payroll/HR or financial rows; retained uploads; credentials; authentication or CSRF changes; production/demo; external calls; live systems; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Defaults confirmed by Ryan with the block: a peer is another active employee with the same role and `pay_type`; the selected employee is excluded from their own average; inactive rows never contribute, while an inactive selected employee may compare against active peers; zero is a real comparable value and must not be confused with no peers; no hourly/salary conversion or annualization occurs; and the UI states the matching role/pay-type basis with `/hr` or `/yr` units.

Expansion candidates and questions: none. The nearest tasks require different product contracts, files, verification paths, or risk classes.

Owner and recommended agent: Codex Desktop in the current task on local branch `codex/payroll-compensation-cohorts`. The block is a small, tightly coupled Flask/Jinja/test change with sensitive-project boundaries and Runway OS stewardship; no delegation or second opinion is needed. Codex owns implementation, verification, exact-scope intake, and dashboard closeout.

Expected surfaces: `web/routes/payroll.py`, `web/templates/payroll.html`, focused additions to `scripts/smoke_test.py`, a compact compensation-comparison contract, sanitized 4R evidence, issue disposition, and Runway OS sources/dashboard.

Stop conditions:

- Correct behavior requires annualization, compensation-policy invention, or real payroll/HR data.
- A migration, historical-row cleanup, authentication or CSRF change, external access, production/demo, or another live action becomes necessary.
- Work expands into another payroll or calculation task, or alters roster, import, validation, deletion, identity, or pay-history behavior.
- Existing BFM-only behavior regresses, focused/full verification materially changes the plan, cleanup cannot be proven, command-center checks fail, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py`.
- Focused temporary-BFM checks for mixed hourly/salary, multiple peers, single-member, inactive, zero-rate, and empty cohorts.
- Employee-detail JSON and rendered-display assertions for values, units, labels, and explicit empty states.
- Personal and Luxe Legacy denial and unchanged-state checks, denied outbound networking, and exact temporary cleanup.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final explicit-path worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is authorized.

Report point: return the exact peer-cohort contract, visible behavior, focused and full synthetic results, changed paths, cleanup, preserved boundaries, local branch state, and the separate 4R-R publication gate.

Suggested next work block: 4R-R for exact-scope durability and automatic release only if Ryan separately authorizes publication; otherwise begin a new just-in-time planning pass for Task 1N.

Result: peer compensation now uses only other active employees with the same role and pay type. Employee detail exposes `peer_avg_cents` plus `peer_count`; a real zero remains numeric while no comparable peers returns `null`. The modal names the matching basis, preserves `/hr` and `/yr`, and shows `No comparable peers` for an empty cohort. Baseline and final full smoke suites passed; focused maintained coverage passed mixed, multiple, self-exclusion, inactive, zero-rate, empty, BFM-only, denied-network, and exact-cleanup checks; disposable-browser verification rendered `$30.00/hr`, `$120,000/yr`, and the explicit empty state. Python compilation, JSON, whitespace, dashboard refresh, health, and final scope checks pass locally. No migration, protected data, retained upload, external call, GitHub durability, deployment, or live action occurred. Evidence: `command-center/payroll-peer-comparison-contract.md` and `command-center/logs/2026-07-20-payroll-peer-comparisons-4r.md`.

### Confirmed Work Block 4R-R: Like-For-Like Payroll Peer Comparisons Durability And Release

Status: done, deployed, and credential-free health verified on 2026-07-20

Parent task: Phase 4 Task 4 for the exact verified 4R source set only.

Included: explicit staging of the exact eleven-path 4R application, maintained-test, contract, issue, evidence, and command-center source set; one source commit on `codex/payroll-compensation-cohorts`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real payroll/HR or financial rows; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4R contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final main alignment, preserved exclusions, and the separate Task 1N planning gate.

Result: the exact eleven-path 4R source set was committed as `edaa853`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29778504012` and deploy job `88473691178` passed every reported step for exact source SHA `edaa853d2177adb1a5a9c31d2c56e6df42a6df88`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, retained upload, credential, authenticated production page, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1N implementation, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-payroll-peer-comparisons-release-4r-r.md`.

### Confirmed Work Block 4S: Locked Payoff APR Truthfulness

Status: done and verified locally on 2026-07-20; release not authorized

Parent tasks: Phase 4 Task 1N.1 and only its focused Task 2 regression slice.

Included findings: `P3-3D-01` and the matching locked-payoff slice of `P3-3D-C01` only.

Outcome: replace the hard-coded locked-plan rate with each linked card's stored APR; make missing or invalid APR behavior explicit; preserve truthful avalanche and snowball ordering; reconcile the narrative and saved month-by-month schedule to the same inputs; and add focused maintained synthetic coverage.

Why this grouping: the linked-account query, payoff engine input, locked narrative, saved schedule, and focused regression coverage form one Short-Term Planning vertical slice with one temporary-database verification path. Snapshot persistence, long-term projections, Weekly, and Waterfall have separate calculation contracts and remain later tasks.

Excluded: Tasks 1N.2-1N.8; Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; Cash Flow APR-entry redesign; migrations; historical cleanup or existing-data remediation; real financial data or databases; retained uploads; credentials; production/demo; external calls; Plaid; workflows; Fly; downstream systems; commit, push, PR, merge, or deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Defaults confirmed by Ryan with the block: use stored `apr_bps`; allow a known 0% APR; treat `NULL` or negative APR as unavailable; when any linked card lacks a valid APR, do not create or overwrite the locked schedule and return controlled guidance to set APR in Cash Flow; avalanche orders by APR; snowball orders by current balance independently of account insertion order; and every durability or release action remains separately gated.

Expansion candidates and questions: none. Task 1N.2 shares a route file but has a separate snapshot-persistence contract and verification path.

Owner and recommended agent: Codex Desktop in the current task on local branch `codex/locked-payoff-apr-truthfulness`. This is a small sensitive-repo repair tightly coupled to synthetic verification and Runway OS stewardship; no delegation or second opinion is needed. Codex owns implementation, verification, exact-scope intake, and dashboard closeout.

Expected surfaces: `web/routes/short_term_planning.py`; focused additions to `scripts/smoke_test.py`; `web/templates/short_term_planning.html` only if existing feedback cannot communicate controlled rejection; a compact APR contract; sanitized 4S evidence; issue disposition; and Runway OS sources/dashboard.

Stop conditions:

- Correct behavior requires a new APR-entry policy, schema migration, historical remediation, or broader payoff-engine redesign.
- Protected data, credentials, external access, production/demo, or another live action becomes necessary.
- Work expands into Tasks 1N.2-1N.8 or broad planning coverage.
- Focused or full verification materially changes the plan, exact cleanup cannot be proven, command-center checks fail, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py`.
- Reversed-order 9.99% and 29.99% linked cards proving avalanche uses the higher stored APR; balance-order cases proving snowball remains independent of APR and insertion order.
- Saved narrative and month-by-month schedule reconciliation to the same inputs.
- Missing, negative, and known-zero APR cases, including exact zero mutation on controlled rejection.
- Personal/BFM behavior, Luxe Legacy denial, denied networking, and exact temporary cleanup.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered inspection if feedback changes, and final explicit-path worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is authorized.

Report point: return the exact APR contract, missing-APR behavior, avalanche and snowball results, narrative and schedule reconciliation, focused and full synthetic results, changed paths, cleanup, preserved boundaries, local branch state, and the separate publication gate.

Suggested next work block: 4T Snapshot Note Preservation for Task 1N.2 plus only its focused Task 2 regression slice after 4S evidence is complete.

Result: locked payoff schedules now use each linked card's stored APR instead of a hard-coded rate. Known zero APR remains valid; missing or negative APR returns controlled Cash Flow guidance before any prior locked-plan field changes. Maintained synthetic coverage proves exact reversed-order avalanche cents, balance-ordered snowball behavior, narrative and schedule reconciliation, missing/negative zero mutation, Personal/BFM behavior, Luxe Legacy denial, denied networking, and exact cleanup. Baseline and final full smoke suites, Python compilation, JSON, whitespace, dashboard refresh, health, and final scope checks pass locally. No template, migration, protected data, external call, GitHub durability, deployment, or live action occurred. Evidence: `command-center/locked-payoff-apr-contract.md` and `command-center/logs/2026-07-20-locked-payoff-apr-truthfulness-4s.md`.

### Confirmed Work Block 4S-R: Locked Payoff APR Truthfulness Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-20

Parent task: Phase 4 Task 4 for the exact verified 4S source set only.

Included: the exact verified ten-path 4S application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/locked-payoff-apr-truthfulness`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N.2; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4S contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N.2 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1N.2 planning gate.

Result: the exact ten-path 4S source set was committed as `91646a5`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29797187213` and deploy job `88530786726` passed every reported step for exact source SHA `91646a50e02d147ef21d4452c415fecaf3e82274`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, retained upload, credential, authenticated production page, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1N.2 implementation, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-locked-payoff-apr-truthfulness-release-4s-r.md`.

### Confirmed Work Block 4T: Snapshot Note Preservation

Status: done and verified locally on 2026-07-20; release not authorized

Parent tasks: Phase 4 Task 1N.2 and only its focused Task 2 regression slice.

Included findings: `P3-3D-03` and the matching snapshot-persistence slice of `P3-3D-C01` only.

Outcome: make same-day automatic snapshots update balances without replacing snapshot identity, creation time, or an existing manual note; keep manual review submission authoritative for intentional note replacement; create a new row on a new date; and add focused maintained synthetic coverage.

Why this grouping: automatic and manual snapshots share the same Short-Term Planning route, unique date key, persistence contract, and temporary-database verification path. Task 1N.3 uses a separate Long-Term Planning projection contract and remains later.

Excluded: Tasks 1N.3-1N.8; Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; migrations; historical snapshot cleanup; demo seeding; UI redesign; real financial data or databases; retained uploads; credentials; production/demo; external calls; Plaid; workflows; Fly; downstream systems; commit, push, PR, merge, or deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Defaults confirmed by Ryan with the block: same-day automatic conflict updates only `balance_cents`; same-day manual conflict updates `balance_cents` and the normalized note; both paths preserve snapshot `id` and `created_at`; an empty manual note remains empty and does not satisfy monthly review; a new date inserts a new row without changing earlier notes; no schema or template change is expected; every durability or release action remains separately gated.

Expansion candidates and questions: none. Task 1N.3 has a different persistence and verification contract.

Owner and recommended agent: Codex Desktop in the current task on local branch `codex/snapshot-note-preservation`. This small sensitive-repo repair couples Flask persistence behavior, maintained synthetic verification, cleanup, issue disposition, and Runway OS stewardship; no delegation or second opinion is needed. Codex owns implementation, verification, exact-scope intake, and dashboard closeout.

Expected surfaces: `web/routes/short_term_planning.py`; focused additions to `scripts/smoke_test.py`; a compact snapshot-note preservation contract; sanitized 4T evidence; issue disposition; and Runway OS sources/dashboard. A template change is excluded unless current-source evidence reveals a new UX decision, which triggers a stop.

Stop conditions:

- Correct behavior requires a migration, historical remediation, or a new review-note or UX policy.
- Protected data, credentials, authentication changes, external access, production/demo, or another live action becomes necessary.
- Work expands into Task 1N.3 or broader planning coverage.
- Focused or full verification materially changes the plan, exact cleanup cannot be proven, command-center checks fail, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py`.
- Same-day automatic-to-manual-to-automatic, manual-to-automatic, and repeated-automatic ordering.
- Intentional later manual note replacement and explicit empty-note behavior.
- Snapshot `id` and `created_at` stability across same-day automatic and manual updates.
- A month transition creates a new row while preserving the earlier note.
- Personal/BFM behavior, Luxe Legacy denial, denied networking, and exact temporary cleanup.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered dashboard inspection, and final explicit-path worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is authorized.

Report point: return the exact persistence contract, ordering and identity matrix, focused and full synthetic results, changed paths, cleanup, preserved boundaries, local branch state, and the separate publication gate.

Suggested next work block: 4T-R durability and automatic release only if separately authorized; otherwise plan Task 1N.3 as 4U.

Result: automatic same-day snapshots now update only the current balance while preserving the snapshot ID, creation time, and manual note. Manual reviews intentionally replace the normalized note without replacing identity; empty notes remain review-incomplete; and a new month creates a new row without altering the earlier review. Maintained Personal and BFM coverage proves automatic/manual/repeated-auto ordering, intentional replacement, empty-note behavior, month transition, Luxe Legacy denial, denied networking, and exact cleanup. Baseline and final full smoke suites, Python compilation, JSON, whitespace, dashboard refresh, health, and final scope checks pass locally. No migration, template, protected data, external call, GitHub durability, deployment, or live action occurred. Evidence: `command-center/snapshot-note-preservation-contract.md` and `command-center/logs/2026-07-20-snapshot-note-preservation-4t.md`.

### Confirmed Work Block 4T-R: Snapshot Note Preservation Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified on 2026-07-20

Parent task: Phase 4 Task 4 for the exact verified 4T source set only.

Included: the exact verified ten-path 4T application, maintained-test, contract, issue, evidence, and Runway OS source set; explicit-path staging; one source commit on `codex/snapshot-note-preservation`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N.3; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4T contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N.3 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1N.3 planning gate.

Result: the exact ten-path 4T source set was committed as `7b473bb`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29799554597` and deploy job `88537736941` passed every reported step for exact source SHA `7b473bbb6022feeafd69c61c1c7349dde726296d`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, retained upload, credential, authenticated production page, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1N.3 implementation, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-snapshot-note-preservation-release-4t-r.md`.

### Confirmed Work Block 4U: Negative Appreciation Truthfulness

Status: done and verified locally on 2026-07-20; release not authorized

Parent tasks: Phase 4 Task 1N.3 and only its focused Task 2 regression slice.

Included findings: `P3-3D-04` and the matching negative-appreciation slice of `P3-3D-C01` only.

Outcome: make negative asset rates compound as depreciation, preserve the zero-rate contribution path and existing positive-rate behavior, and reconcile item projections, entity summaries, and combined net worth with focused maintained synthetic coverage.

Why this grouping: the defect, asset projection formula, entity summaries, combined totals, existing demo Equipment case, and focused coverage share the same Long-Term Planning calculation path. Task 1N.4 begins a separate Weekly date-context and bill-source contract.

Excluded: Tasks 1N.4-1N.8; Tasks 1O-1P; the remainder of Task 2; Tasks 3-4; migrations; historical remediation; demo redesign; rate-input policy changes; Weekly/Waterfall work; UI redesign; real financial data or databases; retained uploads; credentials; production/demo access; external calls; live systems; GitHub durability; deployment; pre-existing untracked `scripts/sync_prod_to_local.sh`; and unrelated untracked `command-center/now 2.md`.

Defaults confirmed by Ryan with the block: use the existing compound-growth formula for positive and negative nonzero rates; retain the zero-rate linear-contribution path, current inflation adjustment, and contribution timing; verify ordinary negative rates including -10% and the existing -15% demo Equipment rate; stop for a new policy decision if rates at or below -100% become material; expect no schema, template, or demo-seed edit; and keep every durability or release action separately gated.

Expansion candidates and questions: none. Task 1N.4 uses a different route, calculation contract, and verification path.

Owner and recommended agent: Codex Desktop in the current task on local branch `codex/negative-asset-depreciation`. This small sensitive-repo repair couples one Flask calculation seam, maintained synthetic verification, cleanup, issue disposition, and Runway OS stewardship; no delegation or second opinion is needed. Codex owns implementation, verification, exact-scope intake, and dashboard closeout.

Expected surfaces: `web/routes/planning.py`; focused additions to `scripts/smoke_test.py`; a compact negative-appreciation projection contract; sanitized 4U evidence; issue disposition; and Runway OS sources/dashboard. `scripts/seed_demo_data.py` is verification input only; no template, migration, or seed edit is expected.

Stop conditions:

- Correct behavior requires a new rate-domain policy, especially for rates at or below -100%, a migration, historical remediation, or a template/UX decision.
- Protected data, credentials, authentication changes, external access, production/demo, or another live action becomes necessary.
- Work expands into Task 1N.4 or broader planning coverage.
- Focused or full verification materially changes the plan, exact cleanup cannot be proven, command-center checks fail, or either preserved untracked file would be touched.

Verification:

- Baseline and final `.venv/bin/python scripts/smoke_test.py`.
- Exact ordinary negative-rate depreciation, zero-rate contributions, positive appreciation, contribution timing, and inflation adjustment.
- Item projections, entity asset totals, and combined net worth reconcile; existing demo Equipment produces a declining projection.
- Personal/BFM behavior, Luxe Legacy denial, denied networking, and exact temporary cleanup.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, health check, rendered dashboard inspection, and final explicit-path worktree review.

Durability: local-only. No commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action is authorized.

Report point: return the exact projection contract, item/entity/combined reconciliation, focused and full synthetic results, changed paths, cleanup, preserved boundaries, local branch state, and the separate publication gate.

Suggested next work block: 4U-R durability and automatic release only if separately authorized; otherwise separately plan Task 1N.4.

Result: positive and negative nonzero asset rates now use the same existing compound-growth and end-of-year contribution formula, while zero rates retain the explicit linear path and inflation adjustment remains unchanged. Exact five-year checks project a $10,000 asset at -10% to $5,904.90 nominally and the demo-equivalent $85,000 Equipment asset at -15% to $37,714.95. Maintained coverage proves negative, zero, positive, contribution, inflation, item-summary, Personal/BFM entity-summary, combined-net-worth, rendered-label, Luxe Legacy denial, denied-network, unrelated-row preservation, and exact-cleanup behavior. Baseline and final full smoke suites, Python compilation, JSON, whitespace, dashboard refresh, health, and rendered inspection pass locally. No migration, template, seed, protected data, external access, GitHub durability, deployment, or live action occurred. Evidence: `command-center/negative-appreciation-projection-contract.md` and `command-center/logs/2026-07-20-negative-appreciation-truthfulness-4u.md`.

### Confirmed Work Block 4U-R: Negative Appreciation Truthfulness Durability And Release

Status: active under Ryan's direct instruction to commit and push to `main`

Parent task: Phase 4 Task 4 for the exact verified 4U source set only.

Included: the exact verified ten-path 4U application, maintained-test, contract, issue, evidence, and command-center source set; explicit-path staging; one source commit on `codex/negative-asset-depreciation`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real financial rows or databases; retained uploads; credentials; authenticated production pages; external calls other than GitHub/Fly status and credential-free health; manual workflow actions; workflow edits; non-automatic Fly changes; downstream access or writes; migrations; Task 1N.4; broader Task 2; unrelated repairs; force push; and recovery beyond the exact fast-forward path.

Owner and recommended agent: Codex Desktop. This release requires exact-path Git stewardship, sensitive-addition review, direct-main fast-forward safety, automatic Fly observation, credential-free health verification, and final Runway OS closeout.

Defaults: no PR because Ryan directly instructed commit and push to `main`; preserve the verified 4U contract and implementation; observe only the automatic Fly deployment caused by the source push; verify only credential-free `/health`; publish the release closeout with `[skip actions]` so it cannot trigger a second deployment; and leave Task 1N.4 planning separate.

Stop conditions: the intended diff contains an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the exact authorized fast-forward path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staged-set review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final local-main/origin-main alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return the source and closeout commits, exact published paths, automatic Fly result, credential-free health, final `main` alignment, preserved exclusions, and the separate Task 1N.4 planning gate.

Result: the exact ten-path 4U source set was committed as `0222d30`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force. Automatic Fly Deploy run `29802647208` and deploy job `88546571143` passed for exact source SHA `0222d301f4e952e755ad6321666ce2f4c93e96e6`; credential-free production `/health` returned HTTP 200. Both preserved untracked files remained excluded, and no protected data, retained upload, credential, authenticated production page, manual workflow action, non-automatic Fly change, downstream access/write, migration, Task 1N.4 implementation, force push, or unrelated action occurred. Evidence: `command-center/logs/2026-07-20-negative-appreciation-truthfulness-release-4u-r.md`.

## Phase 5: UX Polish, Operations, And Durable Handoff

Status: planned

Goal: make the product understandable, maintainable, and easy to re-enter after the critical repairs are complete.

- **Task 1: Review desktop, mobile, and installed-PWA workflows for usability and accessibility.**
- **Task 2: Polish high-friction journeys without widening financial or authentication risk.**
- **Task 3: Finalize operator runbooks, current documentation, monitoring decisions, and release evidence.**
- **Task 4: Close the roadmap with target-repo commit/push durability and a compact parent-project pointer.**

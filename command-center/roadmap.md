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

Status: active after durable release and credential-free production verification of work block 4J-R; Task 1J is next for separate planning

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
- **Task 1J: Isolate Plaid item failures and add truthful observability.** Status: current for separate planning as the third primary-Plaid block.
- **Task 1K: Repair scheduled and public sync-entry coordination and result truthfulness.** Status: planned after Tasks 1H-1J.
- **Task 1L: Repair vendor import-to-categorization integrity.** Status: planned after the Plaid and sync-entry foundations.
- **Task 1M: Repair remaining payroll integrity, validation, and temporary-payload retention.** Status: planned after Task 1C; separate hourly and salary cohorts per Ryan's confirmed default.
- **Task 1N: Repair planning, Weekly, and Waterfall calculation truthfulness.** Status: planned after the planning route guard.
- **Task 1O: Repair the locally provable Luxe Legacy downstream-mirror contract.** Status: planned after Task 1E; downstream idempotency remains parked pending an authorized read-only contract check.
- **Task 1P: Resolve the remaining public, mobile, browser-hardening, availability, and operator-clarity findings.** Status: planned; authenticate `/k/`, keep cookie flags separate from later CSP compatibility, and preserve separately scoped UX decisions.
- **Task 2: Expand regression tests around repaired workflows and entity isolation.** Status: active as paired work only; 4C completed `P3-3A-C01`, 4D completed the payroll-boundary slice of `P3-3F-C01`, 4E completed the planning-boundary slice of `P3-3D-C01`, 4F completed the Owner Draw/source-selection slice of `P3-3I-C01`, 4G completed the workflow-visible result slice of `P3-3H-C01`, 4H completed the recurring-report slice of `P3-3C-C01`, 4I completed the transaction/cursor atomicity slice of `P3-3G-C01`, and 4J completed its reconciliation, link, liability, and freshness slice.
- **Task 3: Add CI checks that are safe for a private financial application and use only synthetic data.**
- **Task 4: Publish and verify only explicitly approved repairs.** Status: done through 4B and 4C-R through 4J-R; every future release remains separately gated.

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

Status: active; directly authorized by Ryan on 2026-07-19

Included: the exact ten intended 4K application, maintained-test, contract, issue, evidence, and command-center paths; explicit staging; one source commit on `codex/plaid-item-isolation-observability`; fast-forward local `main`; direct push to `origin/main`; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Exact source set: `web/routes/plaid.py`; `scripts/smoke_test.py`; `command-center/plaid-item-isolation-observability-contract.md`; `command-center/logs/2026-07-19-plaid-item-isolation-observability-4k.md`; `command-center/issues.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/index.html`.

Excluded: pre-existing untracked `scripts/sync_prod_to_local.sh`; unrelated untracked `command-center/now 2.md`; real databases or financial/payroll/HR rows; uploads; credentials; authenticated production pages; live Plaid calls; manual workflow dispatch or rerun; Fly mutation outside the automatic main-push workflow; downstream access or writes; workflow-file changes; Task 1K, broader sync-entry work, and unrelated repairs; force push; and recovery outside the exact fast-forward publish path.

Owner and recommended agent: Codex Desktop. The release requires exact-path Git and sensitive-addition review, direct-main durability, automatic Fly observation, credential-free HTTP verification, and Runway OS closeout.

Defaults: no PR because Ryan directly requested commit and push to `main`; preserve the verified 4K contract, implementation, tests, and evidence; use only credential-free production `/health`; inspect workflow metadata and open logs only if failure requires diagnosis; publish the post-deploy closeout with `[skip actions]` to prevent a second deployment.

Stop conditions: the exact diff includes an unexpected path, sensitive value, protected data, or unrelated user change; local or remote `main` diverges; maintained verification fails; staging includes an excluded path; the automatic deployment fails or cannot be attributed to the source SHA; credential-free health fails; a second deployment starts for the closeout; or recovery would exceed the authorized path.

Verification: exact path and sensitive-addition review; maintained synthetic suite; Python compilation; JSON validation; dashboard refresh and health; `git diff --check`; explicit staging review; source commit and direct-main fast-forward push; automatic Fly run/job result; credential-free production `/health`; final main/origin alignment; preserved exclusions; and sanitized `[skip actions]` closeout publication.

Report point: return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separate Task 1K planning gate.

## Phase 5: UX Polish, Operations, And Durable Handoff

Status: planned

Goal: make the product understandable, maintainable, and easy to re-enter after the critical repairs are complete.

- **Task 1: Review desktop, mobile, and installed-PWA workflows for usability and accessibility.**
- **Task 2: Polish high-friction journeys without widening financial or authentication risk.**
- **Task 3: Finalize operator runbooks, current documentation, monitoring decisions, and release evidence.**
- **Task 4: Close the roadmap with target-repo commit/push durability and a compact parent-project pointer.**

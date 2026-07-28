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

Status: complete through work block 4BR-R; the exact 4BR reconciliation is durable on `main`, both publication commits use `[skip actions]`, and Phase 5 is active without beginning product review or implementation

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
  - **Task 1L.2: Persist vendor-order line items end to end.** Save Amazon and Henry Schein line items transactionally with their parent orders, preserve exact-reimport idempotency, reconcile integer cents, and prove the maintained auto-split path no longer needs the standalone population script for new imports. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4N and 4N-R.
  - **Task 1L.3: Enforce the category source of truth deterministically.** Validate inferred and accepted transaction/vendor-order category pairs against the current entity definition, make mixed-category ties deterministic, and reject invalid writes without changing stored data. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4O and 4O-R; existing-row detection or remediation remains outside Phase 4.
- **Task 1M: Repair remaining payroll integrity, validation, and temporary-payload retention.** Status: complete, durable, automatically deployed, and credential-free production health verified across Tasks 1M.1-1M.5 through 4P-R, 4Q-R, and 4R-R.
  - **Task 1M.1: Prevent duplicate employees during payroll import.** Stabilize exact existing-employee assignment across preview and save, preserve explicit reassignment and genuinely unmatched creation, and pair `P3-3F-02` with its focused `P3-3F-C01` coverage slice. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4P and 4P-R.
  - **Task 1M.2: End abandoned payroll-preview payload retention.** Add an explicit cancel path that consumes only its exact temporary payload and prove save, cancel, missing, reused, expired, malformed, unrelated-payload, and cleanup behavior for `P3-3F-05` with focused coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4P and 4P-R.
  - **Task 1M.3: Normalize malformed payroll-workbook failures.** Convert corrupt, mislabeled, empty, unsupported, and headerless upload failures into sanitized controlled outcomes without retaining a payload, while preserving valid multi-section preview/save behavior for `P3-3F-06` with focused coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4P and 4P-R.
  - **Task 1M.4: Validate employee roster writes atomically.** Enforce maintained role, pay-type, status, date, identifier, and finite non-negative rate rules before create/update mutation; preserve valid rate-history behavior and pair `P3-3F-04` with focused coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4Q and 4Q-R.
  - **Task 1M.5: Separate payroll peer comparisons by compensation unit.** Compute and display like-for-like hourly and salary cohorts, including mixed, single-member, inactive, zero-rate, and empty cases, for `P3-3F-03` with focused coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4R and 4R-R.
- **Task 1N: Repair planning, Weekly, and Waterfall calculation truthfulness.** Status: complete, released, automatically deployed, and credential-free production health verified across Tasks 1N.1-1N.8 through work blocks 4S-4Y and their release blocks.
  - **Task 1N.1: Use stored APRs in locked payoff schedules.** Pass each linked card's maintained `apr_bps` value into payoff calculation, define missing or invalid APR behavior explicitly, and reconcile avalanche/snowball order, narrative, and saved schedule for `P3-3D-01`. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4S and 4S-R.
  - **Task 1N.2: Preserve manual goal-review notes during automatic snapshots.** Update same-day balances without replacing the snapshot identity or erasing a manual note, while preserving intentional later manual-note replacement for `P3-3D-03`. Status: done, durable, automatically deployed, and credential-free production health verified through 4T and 4T-R.
  - **Task 1N.3: Compound negative asset appreciation as depreciation.** Preserve negative projection rates instead of clamping them to zero and reconcile future asset and net-worth results for `P3-3D-04`. Status: complete, durable, automatically deployed, and health verified through 4U-R.
  - **Task 1N.4: Unify Weekly date context and scheduled card-bill amounts.** Anchor pace, MTD, burn, recurring/manual/card bills, and display periods to the viewed week; use the scheduled payment rather than the full card balance for `P3-3E-01` and `P3-3E-02`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4V and 4V-R.
  - **Task 1N.5: Validate Weekly paydown dates and read stored goals defensively.** Reject invalid target dates without changing the prior goal and prevent malformed stored values from breaking Weekly or Waterfall for `P3-3E-04`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4W and 4W-R.
  - **Task 1N.6: Include deficit months in Waterfall payoff inputs.** Define the rolling period and signed-surplus rule so every included month contributes to the displayed average and payoff estimate for `P3-3E-03`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4X and 4X-R.
  - **Task 1N.7: Keep Waterfall payoff duration truthful while debt remains.** Apply a documented rounding rule so positive debt with positive surplus cannot render as zero payoff months for `P3-3E-05`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4X and 4X-R.
  - **Task 1N.8: Normalize Waterfall tax input once.** Require one finite, range-checked value to drive calculation and rendering without direct-input crashes for `P3-3E-06`. Status: complete, durable, automatically deployed, and credential-free production health verified through 4Y and 4Y-R.
- **Task 1O: Repair the locally provable Luxe Legacy downstream-mirror contract.** Status: complete, durable, automatically deployed, and credential-free production health verified across Tasks 1O.1-1O.4 through 4AA-R; live downstream writes and protected verification remain outside Phase 4.
  - **Task 1O.1: Verify the tracked downstream conflict contract read-only.** Inspect only tracked schema, migration, and request-contract sources in the local downstream repository to determine whether `ledger_transactions.plaid_transaction_id` is uniquely constrained and which explicit PostgREST conflict target the mirror must use. Do not open credentials, databases, row data, network surfaces, or make changes. Status: done through 4Z; tracked schema and importer establish `plaid_transaction_id` as the primary key and explicit conflict target.
  - **Task 1O.2: Reject malformed and duplicate mirror keys deterministically.** After Task 1O.1, define and implement a local payload-selection rule for empty, whitespace-only, whitespace-padded, and repeated Plaid transaction IDs without changing Ledger source rows or dropping unrelated eligible rows. Status: done, durable, automatically deployed, and credential-free production health verified through 4AA-R.
  - **Task 1O.3: Make the mirror conflict target explicit in tracked contracts.** After Task 1O.1, align the Ledger request with `plaid_transaction_id` as the explicit PostgREST conflict target. Status: done and durable through 4AA-R without a downstream schema change; downstream writes and production inspection remain separately gated.
  - **Task 1O.4: Complete maintained synthetic downstream-mirror coverage.** Pair Tasks 1O.2-1O.3 with the remaining `P3-3I-C01` no-op, request-shape, malformed-key, duplicate-key, failure-isolation, and entity-preservation checks using temporary databases, mocked HTTP, and denied outbound sockets. Status: done and durable through 4AA-R.
- **Task 1P: Resolve the remaining public, mobile, browser-hardening, availability, and operator-clarity findings.** Status: complete and durable through the full execution, strict-CSP, browser-boundary, and financial read-model sequence ending at 4BI-R.
  - **Task 1P.1: Authenticate `/k/` through the existing server-side gate.** Resolve `P3-3J-03` and its exact request/public-field slice of `P3-3J-C01` by requiring the configured application session before route execution while preserving no-password mode, Personal/Luxe Legacy scope, BFM exclusion, and the route's self-managed database context. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4AB and 4AB-R.
  - **Task 1P.2: Make the session-cookie policy explicit.** Resolve the cookie half of `P3-3J-06` with a production-safe Secure, HttpOnly, and SameSite contract that preserves local and synthetic-test usability. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4AC and 4AC-R.
  - **Task 1P.3: Complete mobile-drawer accessibility.** Resolve `P3-3J-05` and its responsive-navigation slice of `P3-3J-C01` with focus placement and restoration, Escape and scrim closing, open-only scroll lock, route-click consistency, and maintained browser coverage. Status: done, durable, automatically deployed, and credential-free production health verified through work blocks 4AD and 4AD-R.
  - **Task 1P.4: Design and enforce a compatible Content Security Policy.** Resolve the CSP half of `P3-3J-06` without weakening the policy merely to avoid template work. Work block 4AE found 46 script elements, 161 inline event-handler attributes, 221 inline style attributes, four `hx-on` attributes, HTMX 2.0.4 fragment behavior, two Plaid Link entry templates, and separate base, login, offline/error, and `/k/` document families. Status: complete through the durable 4BB-R enforcement release and the passed two-entry-path real Plaid runtime checkpoint in 4BC.
    - **Task 1P.4.1: Freeze the CSP compatibility contract and migration matrix.** Inventory every executable-script, HTMX fragment, inline-style, local-asset, worker/manifest, login, offline/error, standalone `/k/`, and Plaid Link dependency; define exact candidate directives and allowed origins; classify every required rewrite; and specify a synthetic header/browser verification matrix without changing product behavior. Status: complete and durable through work blocks 4AE and 4AE-R; implementation completed separately through 4BB-R.
      - **Task 1P.4.1-R: Publish the CSP contract and planning closeout.** Make the exact nine-path 4AE command-center artifact set durable on `main` through native `[skip actions]` commits, exact remote-SHA verification, and a sanitized closeout without triggering deployment. Status: complete and durable on `main` through 4AE-R with Actions skipped.
    - **Task 1P.4.2: Remove inline executable markup and HTMX eval dependencies.** Move executable inline script blocks, native event-handler attributes, and `hx-on` behavior into maintained local static JavaScript and delegated listeners; carry server-rendered values through inert JSON or data attributes; and disable HTMX eval and swapped-script execution only after focused synthetic coverage proves compatibility. Status: complete, durable, automatically deployed, and credential-free health verified through 4AR-R.
      - **Task 1P.4.2a: Migrate the shared execution foundation.** Move shared-shell executable blocks and native/HTMX handlers to maintained local JavaScript; move HTMX indicator rules to local CSS; disable only injected indicator styles; and prove the shell while explicitly retaining eval and swapped-script processing until their remaining fragment dependencies are removed. Status: complete and verified locally through work block 4AF.
      - **Task 1P.4.2b: Migrate HTMX-swapped fragment execution.** Remove executable scripts and inline handlers from directly returned fragments; replace the remaining fragment `hx-on` behavior; carry server state through inert data; initialize repeated swaps through delegated listeners or `htmx:load`; then disable HTMX eval and swapped-script processing. The verified pre-4AG fragment surface contained ten executable template scripts, 40 template-native inline handlers, one Python-rendered inline handler, and two `hx-on` handlers, so it is decomposed into the execution-sized tasks below. Status: complete, durable, automatically deployed, and credential-free health verified through 4AI-R.
        - **Task 1P.4.2b.1: Migrate dashboard and report fragment execution.** Move the nine executable template scripts, twelve template-native inline handlers, and one Python-rendered insight-detail inline handler in the included dashboard, analysis, category-comparison, KPI, insight, and report fragment responses into maintained local JavaScript; carry chart and server-rendered values inertly; and prove repeated swaps, chart redraws, drilldowns, modals, and report expansion without fragment script execution. Status: complete, durable, automatically deployed, and credential-free health verified through work blocks 4AG and 4AG-R.
        - **Task 1P.4.2b.2: Migrate transaction and supporting modal fragment execution.** Move the one executable script, remaining twenty-eight native inline handlers, and two `hx-on` handlers in transaction results, row editing, split editing, and supporting popup/queue fragments into maintained local JavaScript and declarative data; preserve sorting, copy, edit, suggest, rule, split, modal, and cleanup behavior across repeated swaps. Status: complete, durable, automatically deployed, and credential-free health verified through work blocks 4AH and 4AH-R.
        - **Task 1P.4.2b.3: Disable and prove HTMX eval and swapped-script processing.** After Tasks 1P.4.2b.1-1P.4.2b.2 leave no directly returned executable fragment or eval-backed attribute, set `allowEval=false` and `allowScriptTags=false`; assert the residual inventory is zero; and run the cross-route repeated-swap synthetic and isolated-browser matrix. Status: complete, durable, automatically deployed, and credential-free health verified through work blocks 4AI and 4AI-R.
      - **Task 1P.4.2c: Migrate remaining full-page execution.** Move the remaining 22 executable inline scripts, 116 template-native handlers, two Python-rendered handlers, and two full-page inert JSON carriers to maintained local behavior and inert server data. The verified source inventory is decomposed into the eight route clusters below. Status: complete, durable, automatically deployed, and credential-free health verified through 4AR-R.
        - **Task 1P.4.2c.1: Migrate core review-page execution.** Move the five executable inline scripts and eighteen native handlers in `components/sidebar.html`, `dashboard.html`, `reports.html`, `transactions.html`, and `todo.html` into the existing shared, dashboard-fragment, and transaction-fragment asset seams; preserve view switching, report export state, transaction filtering/suggestions, To Do modal behavior, sidebar controls, and repeated HTMX behavior. Status: complete, durable, automatically deployed, and credential-free health verified through 4AJ-R.
        - **Task 1P.4.2c.2: Migrate categorization and upload execution.** Move the three executable inline scripts and seven native handlers in `categorize.html`, `categorize_orphans.html`, and `upload.html` into maintained local behavior while preserving alias prefill, category/subcategory loading, month selection, and destructive-action confirmations. Status: complete, durable, automatically deployed, and credential-free health verified through 4AK-R with Task 1P.5 and only the focused Task 2 regression slices.
        - **Task 1P.4.2c.3: Migrate cash-flow and planning execution.** Umbrella task for the three execution-sized route slices below. The verified source contained three executable inline scripts, forty-seven template-native handlers, one inert JSON carrier, and two Python-rendered Short-Term Planning handlers across `cashflow.html`, `planning.html`, `short_term_planning.html`, and the same-route budget response builders. Status: done and durable; Tasks 1P.4.2c.3a-1P.4.2c.3b are durable through 4AL-R and Task 1P.4.2c.3c is durable through 4AM-R.
          - **Task 1P.4.2c.3a: Migrate Cash Flow execution.** Move the one executable inline script and fifteen native handlers in `cashflow.html` into a maintained page-owned local controller while preserving account/card opening, modal population, balance/limit/APR/payment sizing, due-day parsing, recurring-entry setup, scrim/Escape closure, AI entry, and Personal/BFM/LL visibility. Status: complete, durable, automatically deployed, and credential-free production health verified through 4AL-R.
          - **Task 1P.4.2c.3b: Migrate Long-Term Planning execution.** Move the one executable inline script and ten native handlers in `planning.html` into a maintained page-owned local controller while preserving asset/liability add, edit, source switching, delete confirmation, birthday editing, projection display, modal/scrim/Escape behavior, AI entry, Personal/BFM sharing, and Luxe Legacy denial. Status: complete, durable, automatically deployed, and credential-free production health verified through 4AL-R.
          - **Task 1P.4.2c.3c: Migrate Short-Term Planning execution.** Move the one executable inline script, twenty-two template-source native-handler occurrences, one inert JSON carrier in `short_term_planning.html`, and two Python-rendered native handlers in the same budget drill-down route family into maintained local behavior and non-script inert data while preserving goal and plan dialogs, progress, budgets, action items, category drill-downs, dynamic transaction editing, fetch behavior, and keyboard/modal behavior. Status: done, durable, automatically deployed, and credential-free health verified through work blocks 4AM and 4AM-R with only its focused Task 2 regression slice.
        - **Task 1P.4.2c.4: Migrate Weekly and Waterfall execution.** Move the one executable inline script and thirteen native handlers in `weekly.html` and `waterfall.html` into maintained local behavior while preserving weekly AI entry, waterfall mode, breakdown, target, tax, tooltip, and keyboard behavior. Status: complete, durable, automatically deployed, and credential-free health verified through 4AN-R.
        - **Task 1P.4.2c.5: Migrate subscription-page execution.** Move the one executable inline script, fifteen native handlers, one runtime `onclick` assignment, and one inert JSON carrier in `subscriptions.html` into maintained local behavior and non-script inert data while preserving suggestion, watchlist, detail, account-info, copy, tips, modal, and keyboard workflows. Status: complete, durable, automatically deployed, and credential-free health verified through 4AO-R with only its focused Task 2 regression slice.
        - **Task 1P.4.2c.5-R: Publish and verify subscription-page execution.** Make only the exact verified 4AO source set durable, then observe the automatic deployment and verify credential-free production health under a separately confirmed release contract. Status: complete through work block 4AO-R.
        - **Task 1P.4.2c.6: Migrate payroll-page execution.** Move the one executable inline script and nine native handlers in `payroll.html` into maintained local behavior while preserving add/edit/detail, spending-period, new-role, deletion-confirmation, modal, and keyboard workflows. Status: complete, durable, automatically deployed, and credential-free health verified through 4AP-R with only its focused Task 2 regression slice.
        - **Task 1P.4.2c.6-R: Publish and verify payroll-page execution.** Make only the exact verified 4AP source set durable, then observe the automatic deployment and verify credential-free production health under confirmed release work block 4AP-R. Status: complete through work block 4AP-R.
        - **Task 1P.4.2c.7: Migrate Plaid entry-page execution.** Move the three executable inline application scripts and six native handlers in `data_sources.html` and `plaid.html` into maintained local behavior and inert server data while retaining the two exact external Plaid initializer tags for the later narrow policy; prove Link wiring only with fake configuration, mocked Plaid, denied outbound networking, and temporary synthetic data. Status: complete, durable, automatically deployed, and credential-free health verified through 4AQ-R.
        - **Task 1P.4.2c.7-R: Publish and verify Plaid entry-page execution.** Make only the exact locally verified 4AQ source set durable, then observe the automatic deployment and verify credential-free production health under a separately confirmed release block. Status: complete through work block 4AQ-R.
        - **Task 1P.4.2c.8: Migrate standalone and error-document execution.** Move the five executable inline scripts and all source or rendered native handlers in `offline.html`, `errors/403.html`, `errors/404.html`, `errors/500.html`, and `kristine.html` into document-family-specific local behavior while preserving data-free error/offline rendering, retry behavior, `/k/` interaction, authentication boundaries, and no exception leakage. The maintained one-handler aggregate omitted a Jinja-adjacent conditional `/k/` `onclick` that appeared in rendered output, so 4AR explicitly proved both handler seams. Status: complete, durable, automatically deployed, and credential-free health verified through 4AR-R.
        - **Task 1P.4.2c.8-R: Publish and verify standalone and error-document execution.** Make only the exact locally verified 4AR source set durable, then observe the automatic deployment and verify credential-free production health under confirmed work block 4AR-R. Status: complete through work block 4AR-R.
    - **Task 1P.4.3: Make styling and exceptional document surfaces policy-compatible.** Apply the strict core style-attribute contract while confining Plaid's documented exception to Link documents. Status: complete and durable through 4AZ-R and 4BA-R.
      - **Task 1P.4.3a: Make application styles strict-policy compatible.** The 4AE baseline found seven inline style blocks and 221 template style attributes. The 2026-07-23 just-in-time source pass found seven inline style blocks, 211 template style attributes, nine generated-markup style attributes, and 31 application runtime style writes. Work blocks 4AS through 4AZ completed all eight route clusters and reduced the verified application-owned inventory to zero inline style blocks, zero template style attributes, zero generated attributes, and zero application runtime style writes. Status: complete, durable, automatically deployed, and credential-free health verified through 4AS-R, 4AT-R, 4AU-R, 4AV-R, 4AW-R, 4AX-R, 4AY-R, and 4AZ-R.
        - **Task 1P.4.3a.1: Make shared-shell and dashboard/report styles strict-policy compatible.** Remove 26 template style attributes, two generated-markup style attributes, and the ten application runtime style writes in the shared shell, sidebar, dashboard/report pages and fragments. Preserve responsive navigation, AI-chat scroll locking, report controls, repeated HTMX swaps, charts, drilldowns, tooltip positioning, visibility state, and entity accents through static classes, bounded state attributes, or validated data-driven values. Status: complete, durable, automatically deployed, and credential-free health verified through work block 4AS-R.
        - **Task 1P.4.3a.1-R: Publish and verify shared-shell and dashboard/report style compatibility.** Make only the exact locally verified 4AS source set durable, then observe the automatic deployment and verify credential-free production health under confirmed work block 4AS-R. Status: complete through work block 4AS-R.
        - **Task 1P.4.3a.2: Make transaction and matching-fragment styles strict-policy compatible.** Remove 63 template style attributes, seven generated-markup style attributes, and four transaction-fragment runtime style writes across Transactions, matching/vendor cards, row editing, and split editing while preserving repeated swaps, sorting, editing, matching, split totals, dynamic line creation, modal behavior, and responsive layout. Status: complete, durable, automatically deployed, and credential-free health verified through 4AT-R.
        - **Task 1P.4.3a.2-R: Publish and verify transaction and matching-fragment style compatibility.** Make only the exact locally verified 4AT source set durable, then observe the automatic deployment and verify credential-free production health under a separately confirmed release block. Status: complete through work block 4AT-R.
        - **Task 1P.4.3a.3: Make categorization and upload styles strict-policy compatible.** Move one inline style block and 56 template style attributes from categorization, orphan reassignment, upload, and upload-dialog surfaces into maintained CSS/classes while preserving compact tables, form layout, alias states, confidence badges, pagination, dialog behavior, mobile layout, and status-only Upload Undo wording. Status: complete, durable, automatically deployed, and credential-free health verified through work block 4AU-R.
        - **Task 1P.4.3a.3-R: Publish and verify categorization and upload style compatibility.** Make only the exact locally verified 4AU source set durable, then observe the automatic deployment and verify credential-free production health under confirmed work block 4AU-R. Status: complete through work block 4AU-R.
        - **Task 1P.4.3a.4: Make Cash Flow and planning styles strict-policy compatible.** Remove 13 template style attributes and the runtime style writes in Cash Flow, Long-Term Planning, and Short-Term Planning while preserving data-driven progress, modal origins, input sizing, visibility/disabled states, transaction drilldowns, responsive behavior, and Personal/BFM versus Luxe Legacy boundaries. Status: complete and verified locally through work block 4AV.
        - **Task 1P.4.3a.4-R: Publish and verify Cash Flow and planning style compatibility.** Make only the exact locally verified 4AV source set durable, then observe the authorized automatic deployment and verify credential-free production health under exact work block 4AV-R. Status: complete through work block 4AV-R.
        - **Task 1P.4.3a.5: Make Weekly and Waterfall styles strict-policy compatible.** Remove 13 template style attributes and Waterfall runtime style writes while preserving data-driven bars, timelines, tax/target views, tooltip placement, animation staggering, exact responsive behavior, and the validated Weekly/Waterfall calculations. Status: complete, durable, automatically deployed, and credential-free health verified through work block 4AW-R.
        - **Task 1P.4.3a.5-R: Publish and verify Weekly and Waterfall style compatibility.** Make only the exact locally verified 4AW source set durable, then observe the authorized automatic deployment and verify credential-free production health under a separately confirmed release block. Status: complete through work block 4AW-R.
        - **Task 1P.4.3a.6: Make Subscriptions and Payroll styles strict-policy compatible.** Remove the three baseline-counted Payroll template style attributes, the conditional new-role rendered style attribute that the baseline regex does not count, the two route-generated style attributes in the Payroll spending partial, and all five runtime style writes in the page-owned Subscriptions and Payroll controllers while preserving clipboard fallback, disclosure state, role colors, bounded spending bars, repeated period swaps, new-role visibility, dialogs, keyboard behavior, and BFM-only payroll boundaries. Status: complete, durable, automatically deployed, and credential-free health verified through 4AX-R.
        - **Task 1P.4.3a.6-R: Publish and verify Subscriptions and Payroll style compatibility.** Make only the exact locally verified 4AX source set durable, then observe the authorized automatic deployment and verify credential-free production health under confirmed release work block 4AX-R. Status: complete through work block 4AX-R.
        - **Task 1P.4.3a.7: Make Data Sources and Plaid entry-page styles strict-policy compatible.** Move one inline style block and 34 template style attributes to maintained CSS/classes while preserving vendor controls, account tables, both exact Plaid initializer tags, form-versus-JSON exchange contracts, responsive layout, and the separately gated narrow third-party Plaid style exception. Status: complete, durable, automatically deployed, and credential-free production health verified through 4AY-R.
        - **Task 1P.4.3a.7-R: Publish and verify Data Sources and Connected Accounts style compatibility.** Make only the exact locally verified 4AY source set durable, then observe the authorized automatic deployment and verify credential-free production health under a separately confirmed release block. Status: complete through work block 4AY-R.
        - **Task 1P.4.3a.8: Make login, offline/error, and standalone `/k/` styles strict-policy compatible.** Move five inline style blocks and three template style attributes from login, offline, 403/404/500, and `/k/` documents to family-specific local CSS/classes while preserving early theme, data-free error/offline rendering, retry, exact status/no-leakage behavior, authentication, entity boundaries, and mobile layout. Status: complete and verified locally through work block 4AZ.
        - **Task 1P.4.3a.8-R: Publish and verify standalone document style compatibility.** Make only the exact locally verified 4AZ source set durable, then observe the authorized automatic deployment and verify credential-free production health under a separately confirmed release block. Status: complete through work block 4AZ-R.
      - **Task 1P.4.3b: Reconcile exceptional documents and Plaid.** Umbrella policy-reconciliation task for the two execution-sized slices below. The post-4AZ source pass confirmed that strict core/PWA inputs and the Plaid-only third-party exception have different policy questions but one shared contract handoff to Task 1P.4.4. Status: complete and locally verified through 4BA.
        - **Task 1P.4.3b.1: Freeze strict exceptional-document and PWA policy inputs.** Reconcile login, offline/errors, standalone `/k/`, the seven maintained local `data:image/svg+xml` stylesheet resources, root-scoped `/sw.js`, the same-origin manifest/icons, data-free offline caching, and the HTML-versus-static response boundary into exact directive and route-family inputs for Task 1P.4.4. Preserve existing authentication, cache, CSRF, service-worker, manifest, entity, and offline behavior; do not add headers or mutate product code. Status: complete and locally verified through 4BA.
        - **Task 1P.4.3b.2: Freeze the Plaid-only CSP exception and environment contract.** Reconcile both exact Link initializer tags, the CDN frame origin, validated sandbox-or-production connect selection, request-scoped initializer and Plaid-injected-style nonce requirements, and the rendered-Link-document-only `style-src-attr 'unsafe-inline'` exception against current official Plaid guidance. Prohibit exception leakage, both-environment allowlisting, live Link use, credentials, and application inline-code allowances; hand the final exact policy to Task 1P.4.4 without adding a header or nonce plumbing here. Status: complete and locally verified through 4BA.
    - **Task 1P.4.4: Enforce and prove the final Content Security Policy.** Add the exact Flask response policy and request-scoped nonce plumbing selected by the contract; protect every `text/html` response; bind the Plaid variant only to a successfully rendered Link response; refresh and prove cached `/offline`; prove full-page and HTMX-fragment behavior, configured-auth and no-password modes, standalone `/k/`, offline/error, service-worker/manifest, forced Link-render errors, and mocked Plaid boundaries with maintained synthetic header and isolated-browser coverage; then close `P3-3J-06` locally only if no prohibited source remains. Status: complete, durable, automatically deployed, credential-free health verified through 4BB-R, and real Plaid runtime verified on both production entry paths through 4BC.
  - **Task 1P.5: Clarify Upload `Undo` as status-only.** Resolve `P3-3B-04` with explicit operator language that resetting checklist state does not remove imported ledger rows, plus focused rendered/request coverage. Status: complete and verified locally through 4AK; durability remains separate.
  - **Task 1P.6: Finish installed-PWA and browser-boundary regression coverage.** Complete the unconsumed `P3-3J-C01` browser proof without reopening resolved 4A-4B behavior absent contrary evidence. The just-in-time 4BD planning pass found four remaining execution-sized coverage slices that share one isolated-browser harness and verification boundary. Status: complete, durable on `origin/main`, and verified without deployment through work block 4BD-R.
    - **Task 1P.6.1: Prove the manifest, icons, and installability contract.** Add maintained isolated-browser proof for the linked manifest, exact app identity/start/display fields, declared icon purposes and dimensions, same-origin asset availability, and root installability inputs without changing product assets by default. Status: done and durable through 4BD-R.
    - **Task 1P.6.2: Prove service-worker installation and offline entity isolation.** Exercise root-scoped installation and activation, current precache contents, static-only caching, protected/dynamic network-only behavior, and a real offline navigation fallback that remains generic and free of Personal, BFM, or Luxe Legacy content after representative online entity visits. Status: done and durable through 4BD-R.
    - **Task 1P.6.3: Prove configured-auth browser boundaries before and after sign-in.** Add maintained browser checks for full-page redirect, HTMX/JSON denial, safe local return handling, exempt static/manifest/worker/offline availability, successful synthetic sign-in, and authenticated shell continuity without exposing a client-side digest. Status: done and durable through 4BD-R.
    - **Task 1P.6.4: Prove the exact authenticated `/k/` field and entity contract.** Verify the post-decision authenticated browser surface with explicit synthetic Personal and Luxe Legacy fields, BFM exclusion, route-owned context, no-password preservation, responsive behavior, and no protected cache reuse. Status: done and durable through 4BD-R.
  - **Task 1P.7: Finish the remaining broad financial read-model regression coverage.** Consume the unpaired remainder of `P3-3C-C01` without mixing it into public-route, mobile, or browser-policy implementation. The 2026-07-24 just-in-time pass reconciled the original 297 passing audit assertions against the maintained suite and split the remaining work into four execution-sized tasks. The 2026-07-25 4BG stop then decomposed Task 1P.7.4 into a repair prerequisite and the deferred coverage remainder. Status: complete and durable without deployment through 4BI-R.
    - **Task 1P.7.1: Reconcile effective-transaction and dashboard totals.** Add maintained all-entity synthetic proof that split pieces replace split parents, maintained exclusions remain centralized, signed income and spend reconcile, and dashboard counts, spend, income, review count, date/account/transfer filters, empty states, and entity-specific output agree with the same ledger fixture. Status: done and durable through 4BE-R.
    - **Task 1P.7.2: Complete the standard-report and export matrix.** Preserve every non-recurring report type through direct data preparation, rendered view, CSV, PDF, and supported QBO behavior, including range handling, filenames, response types, empty/missing inputs, reconciled totals, and Personal/BFM/Luxe Legacy isolation. The separately repaired Recurring Charges matrix remains covered by 4H. Status: done and durable through 4BE-R.
    - **Task 1P.7.3: Preserve subscription detection and lifecycle behavior.** Add maintained all-entity synthetic proof for suggestion cadence and regularity, accept/add/detail/update, account-information add/delete, dismiss/restore, share text, delete, persistence, empty states, denied networking, and entity-local isolation. Status: done and durable without deployment through 4BF-R.
    - **Task 1P.7.4: Preserve Cash Flow balances, liabilities, recurrence, and visibility.** Umbrella for the repair prerequisite exposed by 4BG and the remaining maintained financial-behavior matrix. Status: complete and durable without deployment through 4BI-R.
      - **Task 1P.7.4a: Repair the Cash Flow shared-entity mutation boundary.** Make Personal/BFM sibling sections genuinely read-only, require every account/card/recurring mutation target to match the active cookie entity, preserve valid active-entity mutations, and add focused maintained colliding-ID, no-mutation, entity-isolation, denied-network, and exact-cleanup proof. Status: complete and durable without deployment through 4BI-R.
      - **Task 1P.7.4b: Complete Cash Flow financial-behavior coverage.** Resume the stopped 4BG matrix for manual bank/card persistence, stored liabilities, manual recurring add/projection/delete, representative automatic recurrence and date boundaries, empty states, Personal/BFM shared visibility, Luxe Legacy isolation, denied networking, and exact cleanup after Task 1P.7.4a passes. Status: complete and durable without deployment through 4BI-R.
- **Task 2: Expand regression tests around repaired workflows and entity isolation.** Status: complete for every selected Phase 4 repair-linked and browser/read-model slice through 4BI-R; broad import/operator-path coverage `P3-3B-C01` and broad Plaid connection/operator-path coverage `P3-3G-C01` are explicitly parked as non-exit-critical future paired work, while planning demo-goal fidelity from `P3-3D-C01` is carried to Phase 5.
- **Task 3: Add CI checks that are safe for a private financial application and use only synthetic data.** The core and isolated-browser contracts, implementations, hosted observations, portability repair, and deterministic Fly deployment runtime are complete through 4BQ. Status: complete and durable.
  - **Task 3.1: Freeze the safe synthetic CI contract.** Define the exact pull-request trigger, least-privilege token, immutable action references, Python/runtime alignment, dependency installation, logging, network, timeout, command, and protected-data boundaries before adding a workflow. Status: complete and durable without deployment through 4BJ-R.
  - **Task 3.2: Implement the PR-only core synthetic CI foundation.** Add one GitHub Actions workflow that runs only on pull requests targeting `main`, persists no checkout credentials, receives no secrets, performs no deploy or sync action, installs tracked runtime dependencies under Python 3.12, and runs the maintained synthetic smoke, relevant Python/JavaScript syntax, JSON, dashboard refresh/health/currentness, and whitespace checks. Status: complete and durable without deployment through 4BJ-R; the workflow has zero runs.
  - **Task 3.2.1: Observe the core synthetic workflow through a minimal no-merge test PR.** Create a feature branch containing only one sanitized branch-only observation marker; open a draft PR to `main`; verify the exact pull-request event, head SHA, core job, steps, and absence of Fly deployment; close the PR without merge after success; and record only sanitized identifiers and status. Status: complete through work block 4BK with successful run `30175620834`, closed-unmerged draft PR #87, and no deployment.
  - **Task 3.3: Add isolated-browser CI coverage.** Umbrella for the execution-sized action/runtime contract, local job implementation, and hosted observation below. The 4BK follow-up pass confirmed the maintained browser matrix passes locally in 286.89 seconds with temporary all-entity data, denied non-localhost browser requests, mocked external seams, both auth modes, and exact cleanup. Status: complete; the hosted matrix passed through 4BO, the portability repair is durable and deployed through 4BP, and the deterministic Fly deployment runtime passed through 4BQ.
    - **Task 3.3.1: Freeze the isolated-browser CI and Node 24 action-runtime contract.** Replace the warned Node 20 action versions with the current official checkout v7.0.1 and setup-python v7.0.0 immutable commits; select explicit `ubuntu-24.04`, whose current official image includes Google Chrome; preserve Python 3.12 and `contents: read`; install only tracked `requirements-dev.txt`; run browser coverage as a separate job after core success with a 15-minute timeout; and freeze no-secret, no-cache, no-artifact, no-browser-download, network, logging, protected-data, and exact-cleanup boundaries. Status: complete and durable without deployment through 4BL-R.
    - **Task 3.3.2: Implement the PR-only isolated-browser CI job and maintained safety assertions.** Upgrade both existing official action pins to the selected Node 24-compatible immutable SHAs; add a separate browser job that depends on the core job, verifies installed Chrome, installs `requirements-dev.txt`, and runs `scripts/mobile_drawer_browser_test.py`; expand the fail-closed workflow checker, safety contract, maintained README, sanitized evidence, and Runway OS integration without changing product behavior or the pull-request-only/read-only authority boundary. Status: complete and durable without deployment through 4BL-R.
    - **Task 3.3.3: Observe the hosted browser CI job through a no-merge test PR.** Umbrella for the stopped first observation, local portability diagnosis/repair, and successful hosted reobservation. The first 4BM run proved exact core-before-browser order and setup but failed the Personal desktop transaction date-filter fixed-width assertion; 4BN repaired the intrinsic flex-item minimum sizing locally; and 4BO passed one clean hosted run. Status: complete through 4BO; PR #88 is closed unmerged and the branch is retained.
      - **Task 3.3.3a: Diagnose and repair hosted transaction date-filter sizing portability.** Use the exact 4BM evidence and read-only source inspection to identify the actual layout contract; add sanitized measured-state detail to the maintained failure message; apply at most the narrow Linux-portable CSS/browser-test change justified by the diagnosis; preserve phone, exact-768, and desktop transaction-filter behavior across Personal, BFM, and Luxe Legacy; run focused and full local verification; and close locally without staging, commit, push, PR mutation, workflow execution, or other external action. Status: complete locally through 4BN.
      - **Task 3.3.3b: Publish the verified portability repair and reobserve hosted browser CI.** After Task 3.3.3a passes and separate authorization, commit only the verified repair on the existing `codex/browser-ci-observation` branch; push once so the open draft PR automatically runs; verify exact event, SHA, core-then-browser order, environment, steps, diagnostics, cleanup, annotations, and no deployment; close PR #88 without merge only after a completely clean success; retain the branch; and perform the separately approved sanitized Runway OS closeout. Status: complete through 4BO with clean run `30202164293`, closed-unmerged PR #88, retained branch, and no deployment.
- **Task 4: Publish and verify only explicitly approved repairs.** Status: done through 4BR-R; the exact command-center reconciliation is durable, the transition closeout is the containing `[skip actions]` commit, and Phase 5 is active.

### Confirmed Work Block 4BR-R: Command-Center Durability And Phase Transition

Status: complete; confirmed and completed on 2026-07-26.

Parent task: Phase 4 Task 4 (`P4-T4`) only. Phase 5 Task 1 (`P5-T1`) may become the sole current planning gate at closeout, but no Phase 5 review or implementation is included.

Included: write and verify active 4BR-R state; reverify the exact eight-path 4BR package; explicitly stage and commit those eight paths as `Preserve Phase 4 completion reconciliation [skip actions]`; cleanly fast-forward local `main`; non-force push `main`; verify the exact remote SHA and zero workflow activity; create a sanitized six-path 4BR-R closeout; mark Phase 4 done and Phase 5 active at zero percent; make Phase 5 Task 1 the sole current Ryan-owned planning gate; commit the exact closeout as `Close Phase 4 and activate Phase 5 [skip actions]`; push it; and verify final local, tracking, and live alignment plus zero workflows.

Excluded: Phase 5 Tasks 1-4 implementation; product, test, workflow, dependency, runtime, configuration, README, category, design, or policy changes; PR creation; GitHub merge; workflow dispatch, rerun, cancellation, or repair; deployment; Plaid or Fly mutation; production, demo, or downstream access; credentials; protected or real financial, payroll, upload, or database data; force push; rebase; conflict resolution; branch deletion; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the verified reconciliation, its durable publication, and the control-only phase transition are one command-center outcome with the same exact-path Git, zero-workflow, dashboard, and rendered-state verification path. Phase 5 review and implementation use a separate subjective and product-facing definition of done.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact-path Git handling, Runway OS stewardship, verification, zero-workflow proof, rendered inspection, stop enforcement, and final intake. Ryan owns any scope expansion, recovery, product decision, protected action, or later Phase 5 work block.

Runner path: reverify the aligned baseline and preserved hashes; make 4BR-R active; run the complete local safety bundle; stage only the exact eight paths; create the first `[skip actions]` commit; cleanly fast-forward and non-force push `main`; verify the exact SHA and zero workflows; write and verify the exact six-path closeout; create and push the second `[skip actions]` commit; verify zero workflows and final alignment; inspect the rendered dashboard; and stop for any deviation.

Expected first commit paths: `command-center/roadmap.md`, `command-center/now.md`, `command-center/decisions.md`, `command-center/issues.md`, `command-center/phase-3-findings-consolidation.md`, `command-center/state.json`, generated `command-center/index.html`, and `command-center/logs/2026-07-26-phase-4-completion-reconciliation-4br.md`.

Expected closeout paths: `command-center/roadmap.md`, `command-center/now.md`, `command-center/decisions.md`, `command-center/state.json`, generated `command-center/index.html`, and `command-center/logs/2026-07-26-phase-4-completion-reconciliation-durability-4br-r.md`.

Defaults: use the existing `codex/phase-4-completion-reconciliation` branch and retain it; use two direct-main `[skip actions]` commits with no PR; rerun full smoke and maintained CI safety; reuse the recent full browser matrix only if product and browser-test ancestry remains unchanged; make Phase 5 Task 1 current as planning metadata only and Ryan-owned until 5A is separately confirmed; and preserve all three unrelated untracked files exactly.

Blocking questions: none.

Expansion candidates and questions: none. Phase 5 Task 1 review, task refinement, design critique, and every implementation action remain later gates.

Stop conditions: local, tracking, or live `main` drift; an unexpected changed, staged, or committed path; a preserved-file change; verification, dashboard, rendered-state, whitespace, or sensitive-addition failure; conflict, rebase, force push, non-fast-forward, rejected push, or broader recovery; any workflow for either `[skip actions]` SHA; inability to preserve exactly one active phase and one current task; or any need for Phase 5 execution, product judgment, protected access, or another excluded action.

Verification: exact local, tracking, and live SHAs; preserved hashes; full synthetic smoke; maintained CI safety; JSON; dashboard refresh/currentness/health and rendered state; exactly one active phase and current task before and after transition; exact changed, staged, and committed paths; whitespace and high-confidence sensitive additions; both remote commit SHAs and zero workflows; final local/tracking/live alignment; retained local branch; and a final worktree containing only the three preserved untracked files.

Dashboard closeout: while active, show 4BR-R as the current work block under Phase 4 Task 4. On success, show 4BR-R done, Phase 4 done, Phase 5 active at zero percent, Phase 5 Task 1 as the sole current Ryan-owned planning gate, and proposed 5A as the recommended next decision. Do not begin 5A.

Report point: return both commit SHAs, exact files, zero-workflow proof, final phase and task state, rendered-dashboard result, final branch and worktree state, preserved hashes, and any stop.

Suggested next work block: 5A just-in-time Phase 5 Task 1 workflow-review decomposition and evidence baseline, with any design second opinion decided before polish implementation.

Result: exact eight-path source commit `b6c7a05d2c7bce46fbfbe05b9cf2470a92460bc3` is durable on local, tracking, and live `main` with zero workflows and zero check runs. The containing exact six-path closeout commit marks 4BR-R and Phase 4 done, activates Phase 5 at zero percent, and makes Phase 5 Task 1 the sole current Ryan-owned planning gate without beginning review or implementation. Final intake verifies the containing closeout SHA, zero workflows, rendered state, preserved files, and final alignment.

### Confirmed Work Block 4BR: Phase 4 Completion Reconciliation

Status: complete and locally verified on 2026-07-26; unstaged, uncommitted, and unpushed pending separately confirmed 4BR-R.

Parent tasks: Phase 4 Tasks 1P (`P4-T1P`), 2 (`P4-T2`), 3 (`P4-T3`), 3.3 (`P4-T33`), and 4 (`P4-T4`) only for evidence-backed completion reconciliation.

Included: write and verify active 4BR state; create local `codex/phase-4-completion-reconciliation` from exact aligned `main`; crosswalk every Phase 4 task and issue against current source, Git ancestry, retained sanitized evidence, workflow results, and durability status; correct stale umbrella-task, blocker, owner, next-action, issue, and finding statuses only when evidence is sufficient; classify each item as durable/resolved, parked with rationale, monitored/accepted, decision-gated, or genuinely residual; and close locally as completion-ready only if every Phase 4 exit-critical item is supported.

Excluded: Phase 5 Tasks 1-4; application, test, workflow, dependency, runtime, configuration, README, category, product, design, or policy changes; new repairs; staging; commit; push; PR; workflow execution, dispatch, rerun, or cancellation; deployment; Plaid or Fly mutation; production/demo/downstream; credentials; protected or real financial/payroll/upload data; branch deletion or cleanup; force push; rebase; conflict resolution; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: Tasks 1P, 2, 3, 3.3, and 4 are the only Phase 4 umbrella tasks still displayed as non-final even though their child implementation, coverage, publication, hosted-CI, repair-durability, and deployment-runtime work has completed through 4BQ. Their remaining work is one shared evidence and state-consistency problem across the same command-center sources.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns the evidence crosswalk, Runway OS stewardship, exact-path local edits, verification, rendered inspection, stop enforcement, and final intake. Ryan owns every ambiguous policy, product, publication, Phase 5, protected-access, and broader-scope decision.

Runner path: verify active state and exact baseline; build the complete task/issue/evidence crosswalk; compare source and current Git with retained evidence; update only supported stale statuses; prove command-center consistency and current rendered output; then close locally as completion-ready or stop with an exact residual list.

Defaults: current Git and source override stale prose; do not reopen resolved findings without contrary evidence; keep parked, monitored, accepted, and decision-gated items explicit; run full smoke and maintained CI safety; reuse the exact recent full-browser evidence unless product or browser-test ancestry changed; keep Phase 4 active and Phase 5 planned pending 4BR-R; make no staged, committed, pushed, workflow, deployment, branch-cleanup, or protected action; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Phase 5 task refinement and publication depend on the completed reconciliation and remain separate gates.

Stop conditions: insufficient or contradictory evidence for any proposed disposition; an exit-critical residual; a product, policy, design, or publication decision; current source contradicting retained evidence; any need for product/test/workflow/configuration/domain changes or another excluded path/action; exact-path, sensitive-addition, JSON, dashboard, health, rendered-state, whitespace, Git, or preserved-file failure; or inability to keep exactly one current task and one active phase. Stop without forced completion, repair, expansion, staging, or publication.

Verification: exact local/tracking/remote baseline and preserved hashes; complete Phase 4 task/issue/evidence crosswalk; source and ancestry checks; current referenced GitHub evidence where needed; full synthetic smoke; maintained CI safety; relevant JSON; dashboard refresh/currentness/health and rendered state; exactly one current task; whitespace and sensitive additions; exact changed paths; zero staged files; and all preserved-file checks.

Dashboard closeout: on success, mark 4BR locally done, remove supported stale task/blocker/action and issue/finding states, record Phase 4 as completion-ready while still active, keep Phase 5 planned, make 4BR-R exact command-center durability and phase transition the sole next Ryan decision, refresh and health-check Runway OS, and inspect the rendered dashboard. On a stop, keep Phase 4 active and name the exact residual task or decision.

Report point: return reconciled task and issue counts, corrected stale fields, durable versus carried-forward findings, any residual gates, exact changed paths, verification, branch/worktree state, preserved exclusions, and whether 4BR-R is ready.

Suggested next work block: 4BR-R exact command-center durability and Phase 4-to-Phase 5 transition, separately planned and confirmed.

Result: the crosswalk reconciled 121 Phase 4 task records and all 59 issue records. The 55 Phase 3-derived entries are 52 resolved/durable, two explicitly parked broad coverage residuals, and one Phase 5 carry-forward; the four additional project issues are three resolved and one monitored. No exit-critical Phase 4 product defect remains. Phase 4 is completion-ready but remains active, Task 4 remains the sole current task, Phase 5 remains planned, and 4BR-R is the sole next Ryan decision.

### Confirmed Work Block 4BQ: Fly Deploy Action Runtime And Toolchain Durability

Status: complete; confirmed and completed on 2026-07-26.

Parent task: Phase 4 Task 4 (`P4-T4`) only for the exact authorized Fly deployment workflow durability package, automatic release observation, credential-free health verification, and sanitized closeout.

Included: write and verify active 4BQ state; verify local, tracking, remote, and GitHub `main` at the exact current baseline; verify official checkout v7.0.1 commit `3d3c42e5aac5ba805825da76410c181273ba90b1`, Fly setup action commit `ed8efb33836e8b2096c7fd3ba1c8afe303ebbff1`, Fly CLI `0.4.74`, the successful 4BP inputs, inactive deployment lane, production health, and preserved hashes; create local `codex/fly-deploy-runtime-durability`; preserve the current push-to-`main` and `workflow_dispatch` triggers without invoking manual dispatch, the sole deploy job, `deploy-group`, `flyctl deploy --remote-only`, and the literal `FLY_API_TOKEN` reference without reading it; set `permissions: contents: read`, explicit `ubuntu-24.04`, a 20-minute timeout, checkout `persist-credentials: false`, both immutable action SHAs, and Fly CLI `0.4.74`; extend `scripts/ci_safety_check.py` to fail closed on the exact Fly contract; add `command-center/fly-deploy-safety-contract.md`; update README guidance; run the complete local safety bundle; explicitly stage and commit only those four source/contract paths without a skip token; cleanly fast-forward local `main`; non-force push `main`; observe only the resulting exact-SHA automatic Fly deployment; require exact pinned inputs, successful steps, zero annotations, and credential-free HTTP 200 health; then write one sanitized 4BQ evidence log, explicitly stage only it plus `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`, create and push one `[skip actions]` closeout, and verify zero closeout workflow activity.

Excluded: Daily Plaid Sync, `SYNC_SECRET`, Synthetic CI behavior, application code, Dockerfile, `fly.toml`, Fly secrets or configuration, manual workflow dispatch/rerun/cancellation, non-automatic Fly mutation, production databases or authenticated pages, Plaid, demo/downstream, credentials, protected or real data, Phase 4 completion reconciliation, Phase 5, PR creation, remote feature-branch publication, force push, rebase, conflict resolution, branch deletion, broader recovery, delegation, second opinion, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: checkout runtime, mutable Fly setup action, floating Fly CLI, floating runner, token permissions, persisted checkout credentials, timeout, maintained checker, and hosted evidence are inputs or safeguards for the same production deployment job. The successful 4BP run already proved Ubuntu 24.04, Fly setup commit `ed8efb3`, and Fly CLI `0.4.74`, so freezing them together removes drift without changing the deployment command or application.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns active-state stewardship, workflow-contract implementation, maintained safety assertions, complete local verification, exact-path Git handling, automatic deployment observation, credential-free health proof, stop enforcement, sanitized closeout, dashboard currency, and final intake.

Runner path: verify active state and exact live inputs; create the clean local branch; implement only the four-path durability package; run full local proof; commit exact paths; cleanly fast-forward and non-force push `main`; observe only the exact automatic deployment; require pinned inputs, clean success, zero annotations, and HTTP 200 health; then publish and verify the exact sanitized `[skip actions]` closeout.

Defaults: preserve both triggers but do not invoke `workflow_dispatch`; preserve the existing deploy command, concurrency, and sole secret reference; use explicit Ubuntu 24.04, `contents: read`, a 20-minute timeout, non-persistent checkout credentials, both full immutable action SHAs, and Fly CLI `0.4.74`; use no PR or remote feature branch; retain the local branch; use one four-path source commit without a skip token; accept only clean fast-forward ancestry and a non-force push; use `[skip actions]` only for the sanitized closeout; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Daily Plaid Sync and Phase 4 completion reconciliation use different risk and verification paths.

Stop conditions: official metadata, successful-run input, live-main, workflow, expected-path, sensitive-addition, preserved-file, verification, dashboard, cleanup, ancestry, or remote drift; inability to preserve the existing trigger, command, concurrency, or secret reference; any need for credential values, protected access, conflict resolution, rebase, force push, non-fast-forward, rejected push, broader recovery, manual workflow action, or excluded work; a missing, duplicated, wrong-SHA, failed, wrongly pinned, or annotated automatic deployment; credential-free health failure; or any closeout workflow. Stop and report without dispatch, rerun, cancellation, repair, or expansion.

Verification: official action and Fly release metadata; exact baseline and preserved hashes; full smoke; full configured-auth/no-password installed-Chrome suite; extended CI safety; Python compilation; JSON; dashboard refresh/currentness/health and rendered state; whitespace and sensitive additions; exact changed/staged/committed paths; cleanup; ancestry; exact automatic event, SHA, runner, action commits, Fly CLI, steps, conclusion, duration, zero annotations, and credential-free HTTP 200 health; exact six-path `[skip actions]` closeout; zero closeout workflows; final alignment; and preserved files.

Dashboard closeout: on success, mark 4BQ done, make 4BR Phase 4 Completion Reconciliation the next separate Ryan decision, refresh and health-check Runway OS, inspect the rendered dashboard, publish the sanitized closeout, and verify zero closeout workflows. On a stop, record exact safe evidence and leave 4BQ blocked without recovery.

Report point: return source and closeout SHAs, exact paths, runner/action/tool versions, workflow and job identifiers, steps and runtime, annotations, health, final alignment, preserved exclusions, and Phase 4 reconciliation readiness.

Result: exact source commit `b94009334cd129ccdb2f963a2e3d86045e0934d3` with sole parent `d1c1a297e13ed30baa8afc0c3ffe54e69888e749` contains only `.github/workflows/fly-deploy.yml`, `README.md`, `command-center/fly-deploy-safety-contract.md`, and `scripts/ci_safety_check.py`. Full smoke, full configured-auth/no-password installed-Chrome coverage, positive and negative dual-workflow safety checks, compilation, JSON, dashboard, whitespace, sensitive-addition, exact-path, cleanup, ancestry, live-lane, remote, and preserved-file checks passed. Exactly one workflow exists for the source SHA: automatic push-triggered run `30207408610`; deploy job `89807770887` passed every step in 44 seconds on Ubuntu 24.04 with `contents: read`, checkout SHA `3d3c42e`, non-persistent credentials, Fly setup SHA `ed8efb3`, and Fly CLI `0.4.74`. The annotation API returned an empty list, the 4BP warning did not recur, and credential-free production health returned HTTP 200. No manual workflow action, Daily Plaid Sync, protected access, broader Fly or application change, recovery, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-26-fly-deploy-runtime-toolchain-durability-4bq.md`.

Suggested next work block: 4BR Phase 4 Completion Reconciliation.

### Confirmed Work Block 4BP: Browser CI Portability Repair Durability And Release

Status: blocked at the confirmed unexpected-deployment-annotation stop on 2026-07-26.

Parent task: Phase 4 Task 4 (`P4-T4`) only for the exact authorized repair durability, automatic release observation, credential-free health verification, and sanitized closeout.

Included: write and verify active 4BP state; verify local, tracking, live GitHub `main` at `a577d14e53aa1b47feffb6617733f67e518cc46c` and the retained repair commit at `bb6d14e7163e40976ffc2f0671509fd4b70f6a28`; preserve and hash the three unrelated untracked files; create local `codex/browser-ci-portability-release` from verified `main`; apply only `web/static/style.css` and `scripts/mobile_drawer_browser_test.py` from the retained repair without its marker or branch history; run the complete local safety bundle; explicitly stage and commit exactly those two files without a skip token; cleanly fast-forward local `main`; non-force push `main`; observe only the resulting automatic `Fly Deploy` for the exact source SHA; verify credential-free `https://ledger-oak.fly.dev/health` returns HTTP 200; write one sanitized 4BP evidence log; explicitly stage only that log plus `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create and non-force push one `[skip actions]` closeout; and verify zero workflow activity for the closeout SHA.

Excluded: reopening or merging PR #88; its marker commit or branch history; remote publication of the new local release branch; Phase 4 completion reconciliation; Phase 5; broader Task 2 or Task 4 work; any additional product, test, dependency, workflow, runner, browser-version, runtime, migration, authentication, CSRF, or CSP change; manual workflow dispatch, rerun, cancellation, or repair; non-automatic Fly mutation; Plaid; production databases or authenticated pages; demo; downstream access or writes; credentials; protected or real data; force push; rebase; conflict resolution; branch deletion; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the exact host-verified two-file repair, its one automatic deployment, credential-free health proof, and sanitized closeout form one coherent durability outcome. PR history, broader repair work, Phase 4 reconciliation, and Phase 5 use different authority and verification paths.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns active-state stewardship, exact-path source transfer, complete local verification, explicit staging, clean Git ancestry, automatic deployment observation, credential-free health verification, stop enforcement, sanitized closeout, dashboard currency, and final intake.

Runner path: verify active Runway OS and exact live state; create the clean local release branch; transfer only the two repair paths; run the full safety bundle; commit exact paths; cleanly fast-forward and non-force push `main`; observe only the exact automatic Fly run; verify credential-free production health; then publish and verify the exact sanitized `[skip actions]` closeout.

Defaults: use no PR; do not push the release branch; preserve the retained observation branch; use one two-path source commit without a skip token; accept only clean fast-forward ancestry and a non-force push; observe rather than mutate the automatic Fly deployment; use `[skip actions]` only for the sanitized six-path closeout; distinguish independently scheduled workflows by event and SHA; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Phase 4 completion reconciliation remains a later gate because its disposition depends on this release result.

Stop conditions: live-main, repair-commit, workflow, expected-path, sensitive-addition, preserved-file, verification, dashboard, cleanup, ancestry, or remote drift; any conflict, rebase, force-push, non-fast-forward, rejected push, or broader recovery need; a missing, failed, wrong-SHA, or unexpectedly annotated deployment; credential-free health failure; any second closeout workflow; or any protected, manual, or excluded action. Stop and report without dispatching, rerunning, cancelling, or repairing.

Verification: exact local, tracking, live GitHub, and retained repair SHAs; preserved-file hashes; full synthetic smoke; full configured-auth/no-password installed-Chrome suite; maintained CI safety; relevant Python compilation and JSON; dashboard refresh/currentness/health and rendered state; whitespace and sensitive additions; exact changed, staged, and committed paths; cleanup; clean ancestry; exact automatic Fly workflow, source SHA, job, steps, conclusion, and annotations; credential-free HTTP 200 health; exact six-path `[skip actions]` closeout; zero closeout workflows; and final local/tracking/live alignment.

Dashboard closeout: on success, mark 4BP done, retain Phase 4 completion reconciliation as a separate Ryan decision, refresh and health-check Runway OS, inspect the rendered dashboard, publish the sanitized closeout, and verify zero closeout workflow activity. On a stop, record the exact safe evidence without claiming completion or taking recovery action.

Report point: return the source and closeout SHAs, exact published paths, automatic Fly run and job identifiers and conclusions, annotations, credential-free health result, final branch/worktree state, preserved exclusions, and the next separate Phase 4 reconciliation decision.

Result: exact source commit `9b26030419b318af100bdc7d871d6c976fd02709` with sole parent `a577d14e53aa1b47feffb6617733f67e518cc46c` contains only `web/static/style.css` and `scripts/mobile_drawer_browser_test.py`, matches retained hosted repair content, and is durable on local, tracking, remote, and GitHub `main`. Full smoke, full configured-auth/no-password installed-Chrome coverage, CI safety, compilation, JSON, dashboard, whitespace, sensitive-addition, cleanup, exact-path, ancestry, remote, and preserved-file checks passed. Exactly one workflow exists for the source SHA: automatic push-triggered `Fly Deploy` run `30203353270`; deploy job `89797056689` passed every step in 2 minutes 7 seconds, and credential-free production health returned HTTP 200. GitHub emitted one warning because operational workflow `actions/checkout@v4` targets Node.js 20 and was forced onto Node.js 24. The annotation is an explicit 4BP stop, so no workflow edit, action-pin change, rerun, dispatch, cancellation, further repair, broader recovery, or Phase 4 reconciliation occurred. Evidence: `command-center/logs/2026-07-26-browser-ci-portability-repair-release-4bp.md`.

Suggested next work block: separately plan and confirm 4BQ Fly Deploy Action Runtime Remediation before Phase 4 Completion Reconciliation.

### Confirmed Work Block 4BO: Hosted Browser CI Reobservation And Safe Closure

Status: complete; confirmed and completed on 2026-07-26.

Parent tasks: Phase 4 Task 3.3.3b (`P4-T333B`) plus Task 4 (`P4-T4`) only for the exact authorized publication and sanitized post-observation closeout.

Included: write and verify the active contract; revalidate the complete 4BN local proof; explicitly stage only `web/static/style.css` and `scripts/mobile_drawer_browser_test.py`; create one feature commit without a skip token on the existing `codex/browser-ci-observation` branch; push once so open draft PR #88 automatically runs `Synthetic CI`; verify the exact pull-request event, head SHA, core-before-browser job order, environment, every step, diagnostics, cleanup, annotations, and absence of deployment; close PR #88 without merge only after a completely clean success; retain the remote branch; return to `main`; write sanitized 4BO evidence and reconcile the retained 4BM and 4BN evidence; explicitly stage only those evidence logs plus `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create one `[skip actions]` closeout commit; non-force push `main`; and verify exact remote alignment with zero closeout workflow or deployment activity.

Excluded: Task 3.3.3a beyond publishing its already-verified two-file result; broader Task 2 or Task 4; Phase 4 completion reconciliation; Phase 5; merge; repair durability on `main`; deployment; manual workflow dispatch, rerun, or cancellation; workflow, action, runner, browser-version, dependency, product, runtime, migration, authentication, CSRF, or CSP changes; further repair; Fly; Plaid; production/demo/downstream; credentials; protected or real data; branch deletion; force push; rebase; conflict resolution; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the exact two-file repair publication, one automatic hosted reobservation, no-deployment proof, conditional safe PR closure, and sanitized evidence form one verification outcome. Merge, source durability on `main`, deployment, Phase 4 reconciliation, and Phase 5 use different risk and verification paths and depend on this result.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns active-state stewardship, full local preflight, exact-path staging, branch commit and push, bounded hosted-run observation, stop enforcement, no-deployment proof, conditional PR closure, sanitized closeout, remote verification, dashboard currency, and final intake.

Runner path: verify active Runway OS and exact live branch, PR, and `main` state; run fresh full synthetic, browser, and CI-safety preflight; stage and commit only the two verified repair files; push the existing feature branch once; observe only the automatic core-then-browser run; close unmerged only after a clean pass; return to `main`; write the sanitized evidence and five-path Runway OS closeout; verify, commit exact paths with `[skip actions]`, push non-force, and verify final state.

Defaults: one explicit two-path feature commit without a skip token; one non-force feature-branch push; no merge; close only after both hosted jobs succeed cleanly and in order with no unexpected annotation or deployment; retain the remote branch; leave a failed, missing, delayed, out-of-order, or unexpectedly annotated draft PR open without repair, rerun, cancellation, or scope expansion; use `[skip actions]` only for the sanitized closeout; distinguish any independently scheduled Daily Plaid Sync by event and SHA; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Merge, repair durability on `main`, deployment, Phase 4 reconciliation, and Phase 5 remain later gates.

Stop conditions: branch, PR, `main`, workflow, or expected-path drift; local verification, dashboard, sensitive-addition, cleanup, exact-stage, or preserved-file failure; a missing, failed, delayed, out-of-order, or unexpectedly annotated hosted job; any Fly deployment or unexpected workflow; or any need for repair, rerun, cancellation, workflow change, merge, branch deletion, force push, rebase, conflict resolution, protected access, or broader recovery. On a hosted stop, leave PR #88 open and perform read-only diagnosis only.

Verification: fresh full synthetic smoke; full configured-auth/no-password installed-Chrome suite; maintained CI safety; relevant Python and JSON syntax; dashboard refresh/currentness/health and rendered state; whitespace and sensitive additions; exact changed and staged paths, commit contents, ancestry, push, PR base/head/event; every core and browser step; core-before-browser order; environment and installed Chrome version; runtimes, cleanup, annotations, diagnostics, and conclusions; no feature-SHA Fly deployment; conditional closed-unmerged status with `mergedAt` null; retained remote branch; sanitized exact-path `[skip actions]` closeout; live `main` SHA; zero closeout workflows; final local/tracking/live alignment; and all preserved-file checks.

Dashboard closeout: on success, mark 4BO and Task 3.3.3b done, retain repair durability on `main` as the next separate Ryan decision, refresh and health-check Runway OS, inspect the rendered dashboard, and publish the sanitized closeout. On a stop, record the exact evidence and leave 4BO blocked without claiming completion.

Report point: return the feature SHA, PR URL and number, workflow and job identifiers, step order, conclusions and runtimes, environment, measured diagnostic result, annotations, cleanup and no-deployment result, PR disposition, closeout SHA, final repository alignment, preserved exclusions, and the next separate repair-durability decision.

Suggested next work block: 4BP Exact Repair Durability Decision after a successful 4BO reobservation; Phase 4 completion reconciliation remains later.

Result: active Runway OS and the complete local safety bundle passed before publication. Exact two-file commit `bb6d14e7163e40976ffc2f0671509fd4b70f6a28` produced exactly one `pull_request` workflow, run `30202164293`. Core job `89793869350` passed every step in 55 seconds, then browser job `89793962387` passed every step and cleanup in 5 minutes 23 seconds on Ubuntu 24.04 with Python 3.12.13, Google Chrome 150.0.7871.128, and Playwright 1.61.0. Both jobs had zero annotations; the complete hosted matrix passed the date-filter contract that stopped 4BM; and no Fly Deploy or other workflow existed for the feature SHA. PR #88 closed without merge with `mergedAt` null, the remote branch remains retained at `bb6d14e`, and remote `main` remained at `4e9c285`. No merge, repair durability on `main`, deployment, further repair, manual workflow action, protected access, broader recovery, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-26-hosted-browser-ci-reobservation-4bo.md`.

### Confirmed Work Block 4BM: Hosted Browser CI Observation Through A No-Merge Test PR

Status: blocked locally at the confirmed hosted-run failure boundary; confirmed and stopped on 2026-07-26.

Parent tasks: Phase 4 Task 3.3.3 (`P4-T333`) plus Task 4 only for the sanitized post-observation Runway OS closeout.

Included: write and verify the active contract; create `codex/browser-ci-observation` from verified `main`; add and explicitly stage one branch-only sanitized observation marker; commit it without a skip token; push the feature branch; open one draft PR targeting `main`; observe the automatically triggered `Synthetic CI` pull-request run; verify the exact event, head SHA, core-then-browser job order, every step, installed Google Chrome, dependency installation, runtime, cleanup, annotations, and absence of Fly deployment; close the PR without merge only after a completely successful clean run; retain the remote branch; return to `main`; write sanitized evidence and closeout state; explicitly stage only that evidence plus `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create one `[skip actions]` closeout commit; non-force push `main`; and verify exact remote alignment with zero workflow or deployment activity for the closeout.

Excluded: broader Task 2 or Task 4; Phase 5; workflow, product, runtime, dependency, browser-test, migration, authentication, CSRF, or CSP changes; repair; manual workflow dispatch, rerun, or cancellation; merge; deployment; Fly; Plaid; production/demo/downstream; credentials; protected or real data; branch deletion; force push; conflict resolution; rebase; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the marker-only PR is the smallest safe way to observe the already-durable post-core hosted browser job. Exact hosted evidence, no-deployment proof, safe PR closure, and sanitized Runway OS closeout form one verification outcome; repair, rerun, merge, deployment, Phase 4 reconciliation, and Phase 5 use different risk and verification paths.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns active-state stewardship, local preflight, exact-path staging, branch/commit/PR handling, bounded run observation, stop enforcement, no-deployment proof, successful-run PR closure, sanitized closeout, remote verification, dashboard currency, and final intake.

Runner path: verify active Runway OS and exact live `main`; run fresh full synthetic and browser preflight; create `codex/browser-ci-observation`; commit only `command-center/logs/2026-07-26-browser-ci-observation-trigger-4bm.md`; push and open a draft PR; observe only its automatic core-then-browser run; close unmerged only after a clean pass; return to `main`; write `command-center/logs/2026-07-26-hosted-browser-ci-observation-4bm.md` and the five-path Runway OS closeout; verify, commit exact paths with `[skip actions]`, push non-force, and verify final state.

Defaults: one draft PR; one marker-only feature commit without a skip token; no merge; close only after both jobs succeed cleanly with no unexpected annotation or deployment; retain the remote branch; leave a failed, missing, over-time, out-of-order, or unexpectedly annotated draft PR open for read-only diagnosis; do not repair, rerun, cancel, or broaden scope; use `[skip actions]` only for the sanitized closeout; treat an independently scheduled Daily Plaid Sync as unrelated by event and SHA; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Repair, rerun, merge, deployment, Phase 4 reconciliation, and Phase 5 remain later gates.

Stop conditions: main or workflow drift; a missing, failed, over-time, or out-of-order job; any unexpected action/runtime annotation or Fly deployment; need for repair, rerun, cancellation, merge, workflow edit, protected action, branch deletion, rebase, force push, conflict resolution, or broader recovery; verification, dashboard, scope, cleanup, sensitive-addition, exact-path, or preserved-file failure.

Verification: fresh full synthetic smoke; full configured-auth/no-password isolated-browser suite; maintained CI safety; JSON, dashboard refresh/currentness/health and rendered state; whitespace and sensitive additions; exact branch, marker diff, stage, commit, ancestry, push, PR base/head/event; every core and browser job step; core-before-browser order; installed Chrome version; runtimes, cleanup, annotations, and conclusions; no feature-SHA Fly deployment; closed-unmerged status with `mergedAt` null; sanitized exact-path closeout and `[skip actions]` commit; live main SHA; zero closeout workflows; final local/tracking/live alignment; and all preserved-file checks.

Dashboard closeout: on success, mark 4BM and Task 3.3.3 done, make 4BN Phase 4 Completion Reconciliation the next planning gate, refresh and health-check Runway OS, inspect the rendered dashboard, and publish the sanitized closeout. On a stop, record the exact evidence and leave the task blocked without claiming completion.

Report point: return feature SHA, PR URL and number, workflow and job identifiers, step conclusions and runtimes, Chrome version, annotations, cleanup and no-deployment result, closed-unmerged status, closeout SHA, final repository alignment, preserved exclusions, and the next separate 4BN planning gate.

Suggested next work block: 4BN Phase 4 Completion Reconciliation after a successful 4BM observation.

Result: local full smoke and browser preflight passed. Marker-only commit `68959de40ca7de52cd20a0465d002ae4929c92ce` produced draft PR #88 and exact pull-request run `30191944724`. Core job `89766609536` passed every step in 48 seconds. Browser job `89766677978` started afterward on Ubuntu 24.04 with Python 3.12.13, Chrome 150.0.7871.128, and Playwright 1.61.0; setup and dependency installation passed, but the maintained suite failed after 27 seconds at the Personal desktop transaction date-filter fixed-width assertion, producing one exit-code annotation and a 1-minute-5-second failed job. The prior Node.js 20 annotation did not recur. No Fly deployment or other feature-SHA workflow occurred, and `main` remained unchanged. PR #88 remains open, draft, and unmerged; no repair, rerun, cancellation, closure, merge, workflow/product/dependency edit, deployment, protected access, or preserved-file action occurred. Read-only inspection makes Linux Chrome intrinsic date-input minimum sizing a plausible cause, but the failed assertion did not record actual widths, so that inference requires a separately confirmed diagnostic and repair block. Evidence: `command-center/logs/2026-07-26-hosted-browser-ci-observation-4bm.md`.

Suggested next work block after the stop: 4BN Browser CI Portability Diagnosis And Local Repair for Task 3.3.3a only, followed by separately gated 4BO Hosted Browser CI Reobservation And Safe Closure for Task 3.3.3b after local verification passes.

### Confirmed Work Block 4BN: Browser CI Portability Diagnosis And Local Repair

Status: complete locally; confirmed and completed on 2026-07-26.

Parent task: Phase 4 Task 3.3.3a (`P4-T333A`) only.

Included: write and verify the active contract; continue on the existing local `codex/browser-ci-observation` branch while leaving its remote head and draft PR #88 unchanged; use the exact 4BM evidence and tracked source to diagnose the hosted-only Personal desktop transaction date-filter width mismatch; add sanitized measured date-group and filter-bar values to the maintained failure output; apply at most the narrow flex-item/CSS sizing correction justified by the diagnosis; preserve the existing 130px desktop, exact-768 two-column, phone stacking, no-overflow, no-style-attribute, all-entity, both-auth, denied-network, and exact-cleanup contracts; run focused and complete local verification; write sanitized evidence; and close Runway OS locally without staging or external action.

Excluded: Task 3.3.3b; 4BO hosted reobservation; Task 4; staging; commit; push; PR #88 mutation or closure; workflow execution, rerun, or cancellation; merge; branch deletion; publication; deployment; workflow, action, runner, browser-version, dependency, authentication, CSRF, CSP, or migration changes; relaxed acceptance ranges; broader product or design work; Fly; Plaid; production/demo/downstream; credentials; protected or real data; Phase 4 reconciliation; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: measured failure evidence, the narrow sizing correction, responsive assertions, and local regression proof share one layout seam and one local definition of done. Hosted reobservation requires a branch push and automatic workflow run, so it remains a separate risk and authorization gate.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns diagnosis, narrow implementation, visual and synthetic verification, exact cleanup, dashboard currency, scope enforcement, and final intake.

Runner path: activate 4BN on local `main`; switch to the existing local `codex/browser-ci-observation` branch while preserving the uncommitted Runway OS state; establish measured local layout evidence; diagnose before changing CSS; add only the justified diagnostic and sizing repair; run focused and complete verification; then close locally as passed or stopped with zero staged and external changes.

Defaults: preserve the 130px desktop date-filter contract and current appearance; do not weaken the acceptance range; prefer a narrow flex-item minimum-size correction only if supported; include only sanitized numeric dimensions in failure messages; preserve phone and exact-768 behavior; use temporary synthetic all-entity data, both auth modes, installed local Chrome, denied non-localhost traffic, and exact cleanup; leave PR #88 open, draft, unmerged, and untouched; keep all work local, unstaged, and uncommitted.

Blocking questions: none.

Expansion candidates and questions: none. Task 3.3.3b changes the risk class to hosted execution and depends on the verified 4BN patch.

Stop conditions: the narrow hypothesis is disproved; a broader layout/design or acceptance decision is needed; the fix changes supported responsive behavior or causes overflow; any entity/auth/style/network/cleanup regression appears; a dependency/workflow/external action becomes necessary; scope expands; verification or dashboard health fails in a plan-changing way; sensitive or unexpected paths appear; or a preserved file overlaps.

Verification: focused computed layout and measured failure detail across all three entities at phone, exact-768, and desktop; full synthetic smoke; full configured-auth/no-password installed-Chrome browser suite; maintained CI safety; relevant Python and JavaScript syntax; JSON; dashboard refresh/currentness/health and rendered inspection; whitespace and sensitive additions; exact changed paths; zero staged changes; zero external actions; and all preserved files.

Dashboard closeout: on pass, mark 4BN and Task 3.3.3a complete locally and make Task 3.3.3b the sole current gate for separately proposed 4BO. On a stop, keep Task 3.3.3a current and record the exact blocker. Refresh, health-check, and inspect the rendered dashboard either way.

Report point: return the exact diagnosis, measured evidence, repair contract, changed paths, responsive/all-entity result, complete verification, cleanup, branch/worktree state, preserved exclusions, and separate 4BO gate.

Suggested next work block: 4BO Hosted Browser CI Reobservation And Safe Closure for Task 3.3.3b after 4BN passes locally.

Result: the desktop date-filter flex item used a `130px` basis with `min-width: auto`; a temporary synthetic all-entity Chrome probe measured `132.44px`, confirming intrinsic minimum sizing could enlarge it. The narrow repair adds `min-width: 0` without changing the basis or acceptance range, and maintained assertion failures now include only sanitized `dateWidth` and `filterWidth` measurements. Post-repair Personal, BFM, and Luxe Legacy each measured exactly `130.00px` on desktop while phone and exact-768 geometry remained unchanged with no overflow or blocked-network attempt. Full smoke and a clean complete both-auth installed-Chrome rerun passed. The first concurrent browser attempt had stopped earlier at an unrelated dashboard partial-response timeout, cleaned up exactly, and was not treated as repair evidence. JSON, dashboard currentness/health, syntax, whitespace, exact-path, zero-stage, and preserved-file checks pass; the in-app browser blocked localhost dashboard reinspection after server restart, so that UI-inspection limitation is explicit and no workaround was attempted. All work remains local, unstaged, uncommitted, and unpushed; PR #88 and its remote branch remain untouched, and no workflow or deployment occurred. Evidence: `command-center/logs/2026-07-26-browser-ci-portability-local-repair-4bn.md`.

### Confirmed Work Block 4BL-R: Browser CI Foundation Durability Without Deployment

- Include Task 4 (`P4-T4`) only for the exact verified 4BL package: explicitly stage the ten approved source paths; create one `[skip actions]` source commit on `codex/isolated-browser-ci`; cleanly fast-forward local `main`; non-force push it; verify exact remote/GitHub SHA and zero workflows; then write, verify, commit, and push one sanitized six-path `[skip actions]` closeout.
- Exclude Task 3.3.3 hosted observation, broader Task 2 or Task 4, Phase 5, PR creation, remote feature-branch publication, workflow execution/dispatch/rerun/cancellation, merge-triggered deployment, Fly, Plaid, production/demo/downstream, credentials, protected or real data, product/dependency/browser-test/runtime/migration/authentication/CSRF/CSP/operational-workflow changes, force push, rebase, conflict resolution, branch deletion, broader recovery, delegation, second opinion, and the three preserved untracked files.
- Use direct non-force `main` publication with two explicit-path `[skip actions]` commits. Do not create a PR because that would deliberately enter Task 3.3.3 and execute the new hosted jobs.
- Stop for live-`main` drift from `7a5e21d9ba1363647c32cda23606fbdb9fa94827`; any unexpected, sensitive, or preserved path; verification/dashboard/scope/cleanup failure; non-fast-forward, conflict, rebase, force-push, push rejection, or broader recovery need; GitHub verification failure; or any workflow/deployment activity despite `[skip actions]`.
- Verify full smoke and full isolated-browser coverage; maintained CI safety; workflow YAML and relevant syntax; JSON, dashboard refresh/currentness/health and rendered state; whitespace and sensitive additions; exact changed/staged/committed paths; ancestry; live GitHub SHA and zero workflows after both pushes; final local/tracking/live alignment; and preservation of all three unrelated untracked files.
- Report source and closeout SHAs, exact published paths, ancestry, zero-workflow/no-deployment result, final alignment/worktree, preserved exclusions, and the still-separate Task 3.3.3 gate.
- Result: exact ten-path source commit `be14f5aa1e0733d6d12f57a221560eb96f95df5c` is durable on `main` with expected parent `7a5e21d9ba1363647c32cda23606fbdb9fa94827`, full verification passed, GitHub reported zero workflow runs, and no deployment occurred. The sanitized closeout is published separately with `[skip actions]`. Evidence: `command-center/logs/2026-07-25-browser-ci-foundation-durability-4bl-r.md`.

### Confirmed Work Block 4BL: PR-Only Isolated-Browser CI Foundation

- Include Task 3.3.1 (`P4-T331`) and Task 3.3.2 (`P4-T332`) only: freeze the exact browser-CI action/runtime boundary and implement the separate PR-only browser job, maintained safety assertions, compact documentation, sanitized evidence, and Runway OS integration locally.
- Exclude Task 3.3.3 hosted observation, broader Task 2 or Task 4, Phase 5, product/runtime/dependency/migration/authentication/CSRF/CSP or browser-test changes, staging, commit, push, PR, workflow action, merge, deployment, Fly, Plaid, production/demo/downstream, credentials, protected or real data, delegation/second opinion, and the three preserved untracked files.
- Use checkout v7.0.1 commit `3d3c42e5aac5ba805825da76410c181273ba90b1` and setup-python v7.0.0 commit `5fda3b95a4ea91299a34e894583c3862153e4b97`; preserve the PR-to-`main`, `contents: read`, and non-persistent-checkout boundary; keep core on `ubuntu-latest`; add a post-core `ubuntu-24.04` browser job with Python 3.12, installed Google Chrome, tracked `requirements-dev.txt`, a 15-minute timeout, and no browser download/cache/artifact/service/container/environment.
- Stop if Linux portability requires product, dependency, or browser-test repair; if any secret, write permission, persistent credential, mutable action, protected/live path, publication, hosted execution, or broader recovery is needed; or if verification, dashboard, scope, or preserved-file checks fail.
- Verify full synthetic smoke, maintained CI safety, full isolated-browser coverage, workflow/YAML and relevant syntax, JSON, dashboard refresh/currentness/health and rendered state, whitespace, exact paths, zero staged changes, zero external actions, and preservation of all three unrelated untracked files.
- Report the exact local workflow contract, checker coverage, action-runtime remediation, verification/runtime, branch/worktree, protected exclusions, and the separately gated 4BL-R durability proposal.
- Result: complete locally on `codex/isolated-browser-ci`; full smoke passed in 8.86 seconds, full isolated-browser coverage passed in 287.25 seconds, every static/dashboard/scope boundary passed, and no staging or external action occurred. Evidence: `command-center/logs/2026-07-25-pr-only-isolated-browser-ci-foundation-4bl.md`.

### Confirmed Work Block 4BK: Core Synthetic CI Observation Through A No-Merge Test PR

Status: done; confirmed and completed on 2026-07-25.

Parent tasks: Phase 4 Task 3.2.1 (`P4-T321`) plus Task 4 only for the sanitized post-observation Runway OS closeout.

Included: write and verify the active contract; create `codex/synthetic-ci-observation` from verified `main`; add and explicitly stage one branch-only sanitized observation marker; commit it without a skip token; push the feature branch; open one draft PR targeting `main`; observe the automatically triggered `Synthetic CI` pull-request run; verify the exact event, head SHA, core job, every step, and absence of Fly deployment; close the PR without merge after success; return to `main`; write sanitized evidence and closeout state; explicitly stage only that evidence plus `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create one `[skip actions]` closeout commit; non-force push `main`; and verify exact remote alignment with zero workflow or deployment activity for the closeout.

Excluded: Task 3.3 browser CI; broader Task 2 or Task 4; Phase 5; workflow, product, runtime, dependency, migration, authentication, CSRF, or CSP changes; merge; deployment; Fly; Plaid; production/demo/downstream; credentials; protected or real data; manual workflow dispatch, rerun, or cancellation; branch deletion; force push; conflict resolution; rebase; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the marker-only PR is the smallest safe way to produce the first hosted evidence for the durable PR-only workflow. Its sanitized Runway OS closeout records the same observation without merging the marker or triggering deployment, while Task 3.3 has a different dependency, runner, runtime, and failure profile.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns active-state stewardship, exact-path staging, branch/commit/PR handling, bounded run observation, no-deployment proof, PR closure after success, sanitized closeout, remote verification, and final intake.

Runner path: preserve the five local planning changes while creating `codex/synthetic-ci-observation` from `65b6b7aa37fcd1f9ff88a82b161a4afa54960006`; commit only `command-center/logs/2026-07-25-core-synthetic-ci-observation-trigger-4bk.md`; push and open a draft PR; observe only the automatically created core run; close unmerged after success; switch back to `main` while preserving the planning changes; write the separate durable evidence log and closeout; verify, commit exact paths with `[skip actions]`, push non-force, and verify final state.

Defaults: one draft PR; one marker-only feature commit with no skip token; no merge; close the draft PR after success; retain the remote branch; leave a failed draft PR open for read-only diagnosis; `[skip actions]` only for the sanitized closeout; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Browser CI, workflow repair or rerun, merge, deployment, production, and protected access have different definitions of done.

Stop conditions: workflow or remote-main drift; unexpected workflow or Fly deployment; the core run missing, failing, or exceeding the bounded observation window; any need for repair, rerun, workflow edit, merge, deployment, protected access, branch deletion, or broader recovery; verification, dashboard, scope, or preserved-file failure. If the hosted run fails, leave the draft PR open and stop after read-only diagnosis.

Verification: local full smoke and maintained CI safety preflight; JSON, dashboard refresh/currentness/health and rendered active state; exact marker-only diff, stage, commit, ancestry, and remote branch SHA; draft PR base/head/event; exact workflow/run/job/step conclusions; zero Fly deployment; closed-unmerged status; sanitized evidence; final JSON, dashboard, whitespace, exact closeout paths and commit; live-main SHA; zero workflow activity for the `[skip actions]` closeout; final local/remote alignment; and all three preserved files.

Dashboard closeout: show 4BK active with Task 3.2.1 current before branch work. After a successful closed-unmerged run and durable closeout, mark 4BK and Task 3.2.1 done, keep Task 3 active, make a just-in-time Task 3.3 planning pass the next Ryan gate, and refresh, health-check, and inspect the rendered dashboard.

Report point: return the feature SHA, PR URL and number, run/job identifiers, step conclusions, closed-unmerged/no-deployment result, main closeout SHA, final worktree, preserved exclusions, and the separately gated Task 3.3 decision.

Suggested next work block: run a just-in-time Task 3.3 browser-CI planning pass only after the first hosted core run is successful and 4BK is closed.

Result: local full smoke, maintained CI safety, JSON, dashboard, whitespace, exact-path, and preserved-file preflight passed. Marker-only feature commit `cde1360e0e9f2041ebace7cd6555e2a021bf6400` was pushed on retained branch `codex/synthetic-ci-observation`. Draft PR [#87](https://github.com/rabuffington22/expense-tracker/pull/87) triggered exact `pull_request` run [30175620834](https://github.com/rabuffington22/expense-tracker/actions/runs/30175620834) and core job [89723824615](https://github.com/rabuffington22/expense-tracker/actions/runs/30175620834/job/89723824615); every reported step passed in 52 seconds. GitHub emitted one non-failing Node.js 20 deprecation annotation for the pinned official actions because the runner forced them onto Node.js 24. No Fly Deploy or other workflow run existed for the feature SHA; remote `main` never moved. PR #87 was closed while still a draft with no merge, and the remote branch was retained. No workflow edit, product change, deployment, production access, protected-data access, rerun, cancellation, branch deletion, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-25-core-synthetic-ci-observation-4bk.md`.

### Confirmed Work Block 4BJ-R: Safe Synthetic CI Durability Without Deployment

Status: done and durable without deployment; directly authorized and completed on 2026-07-25.

Parent task: Phase 4 Task 4, limited to the exact verified 4BJ source package.

Included: record 4BJ-R active; re-run the approved source-package checks; explicitly stage only `.github/workflows/synthetic-ci.yml`, `README.md`, `scripts/ci_safety_check.py`, `command-center/synthetic-ci-safety-contract.md`, `command-center/scripts/health-check.js`, `command-center/scripts/refresh-dashboard.js`, `command-center/logs/2026-07-25-safe-pr-synthetic-ci-foundation-4bj.md`, `command-center/decisions.md`, `command-center/index.html`, `command-center/issues.md`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create one `[skip actions]` source commit on `codex/safe-synthetic-ci`; cleanly fast-forward local `main`; non-force push `origin/main`; verify exact live remote/GitHub SHA and zero workflow activity; then publish one sanitized `[skip actions]` closeout commit.

Excluded: Task 3.3 browser CI; broader Task 2; further Task 4; Phase 5; product, runtime, dependency, migration, authentication, CSRF, or CSP changes; edits to `.github/workflows/fly-deploy.yml` or `.github/workflows/daily-plaid-sync.yml`; PR creation; workflow execution, dispatch, or rerun; deployment; Fly; Plaid; production/demo/downstream; credentials; protected or real data; force push; conflict resolution; rebase; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the workflow, fail-closed checker, safety contract, deterministic dashboard checks, maintained guidance, evidence, and Runway OS state form one auditable synthetic CI foundation. The direct-main request changes the publication route but does not expand implementation or live-operation scope.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact-path verification, sensitive-addition review, staging, commits, ancestry, clean local-main fast-forward, non-force pushes, remote/no-workflow verification, dashboard stewardship, and final intake.

Runner path: continue on `codex/safe-synthetic-ci`; verify active Runway OS and GitHub prerequisites; re-run the complete source-package checks; stage the 13 approved paths only; create and inspect the source commit; cleanly fast-forward and push `main`; verify exact SHA and zero workflow activity; then write, verify, commit, and push the sanitized closeout.

Defaults: explicit-path staging; two `[skip actions]` commits; direct non-force main publication without PR, workflow action, deployment, Fly, or production access; preserve all three unrelated untracked files; expected source parent `2babc9403f808ab65549751d11f5e3c429d8bf9d`, subject to immediate pre-stage revalidation.

Blocking questions: none. Ryan's direct-main instruction resolves the publication route; `[skip actions]` preserves the separate deployment gate.

Expansion candidates and questions: none. Browser CI, observed PR execution, deployment, and product work have different definitions of done.

Stop conditions: any unexpected or sensitive path; preserved-file overlap; failed verification, dashboard, or scope check; live remote divergence; non-fast-forward requirement; push rejection; inability to verify GitHub; any workflow run or deployment despite `[skip actions]`; or recovery beyond read-only diagnosis.

Verification: full `.venv/bin/python scripts/smoke_test.py`; `.venv/bin/python scripts/ci_safety_check.py`; workflow YAML, relevant Python and JavaScript syntax, JSON, dashboard refresh/currentness/health/generated/rendered state, whitespace, high-confidence sensitive-addition review, exact changed/staged/committed paths, ancestry, exact live remote/GitHub SHA, zero workflow activity for both commits, final local/remote alignment, and all three preserved files.

Dashboard closeout: show 4BJ-R active with Task 4 current before staging. After remote verification, mark 4BJ-R and Tasks 3.1-3.2 durable without deployment, return Task 3 to the next just-in-time gate for Task 3.3, and refresh, health-check, and inspect the rendered dashboard.

Report point: return source and closeout SHAs, exact published paths, ancestry and remote alignment, zero-workflow/no-deployment result, verification, final worktree, preserved exclusions, and the separate Task 3.3 gate.

Suggested next work block: perform a just-in-time Task 3.3 browser-CI planning pass only after Ryan chooses whether the core PR workflow should first be exercised through a separately confirmed test PR.

Result: full synthetic smoke, the maintained CI safety checker under the project environment and Python 3.12, workflow YAML, relevant Python and JavaScript syntax, JSON, dashboard refresh/currentness/normal and CI health/generated/rendered state, whitespace, high-confidence secret-pattern review, exact changed/staged/committed paths, clean fast-forward ancestry, non-force push, live remote and GitHub SHA alignment, and all preserved-file checks passed. Exact 13-path source commit `30b4cd97d749e244727a03400cdfa869c34c702b`, with parent `2babc9403f808ab65549751d11f5e3c429d8bf9d`, was fast-forwarded and pushed non-force to `main`. GitHub reported zero workflow runs because the commit used `[skip actions]`; no PR, workflow action, Fly deployment, production access, protected-data access, or production health check occurred. Evidence: `command-center/logs/2026-07-25-safe-synthetic-ci-durability-4bj-r.md`.

### Confirmed Work Block 4BJ: Safe PR-Only Synthetic CI Foundation

Status: complete and locally verified; confirmed and completed on 2026-07-25; unpublished, uncommitted, and unstaged.

Parent tasks: Phase 4 Task 3.1 (`P4-T31`) and Task 3.2 (`P4-T32`) only.

Included: freeze the exact pull-request trigger, least-privilege token, immutable action references, Python/runtime alignment, dependency installation, logging, network, timeout, command, and protected-data boundaries; create local branch `codex/safe-synthetic-ci`; add one new PR-only core synthetic workflow targeting `main`; add maintained static safety assertions; update compact maintained CI guidance; write one sanitized evidence log; integrate and close the block in Runway OS.

Excluded: Task 3.3 browser CI; broader Task 2; Task 4 publication; Phase 5; edits to `.github/workflows/fly-deploy.yml` or `.github/workflows/daily-plaid-sync.yml`; workflow enablement, execution, dispatch, or rerun; staging, commit, push, PR, merge, or deployment; product behavior; migrations; authentication, CSRF, or CSP; Plaid, Fly, production, demo, downstream, credentials, real databases, uploads, or financial rows; delegation or second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: Tasks 3.1-3.2 share one safety contract, workflow file, and deterministic local verification path. Task 3.3 requires a separate browser dependency, installed-Chrome runner, longer runtime, and different failure diagnosis, so its right design depends on observing the core foundation first.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns the contract, local source, maintained safety assertions, verification, dashboard stewardship, and final intake.

Runner path: write and verify this active contract first; create `codex/safe-synthetic-ci`; re-run baseline smoke; resolve immutable official-action SHAs from their official repositories; implement only the approved workflow, safety check, documentation, evidence, and command-center paths; run complete local verification; then close 4BJ locally and uncommitted.

Expected paths: new `.github/workflows/synthetic-ci.yml`; new `command-center/synthetic-ci-safety-contract.md`; one maintained standard-library workflow safety checker, expected at `scripts/ci_safety_check.py`; `README.md`; one sanitized 4BJ evidence log; and the Runway OS source/generated dashboard paths.

Defaults: `pull_request` targeting `main` only; `permissions: contents: read`; checkout `persist-credentials: false`; official actions pinned to verified full commit SHAs; Python 3.12; install only `requirements.txt`; no dependency cache or artifact upload; no delegation or second opinion.

Blocking questions: none.

Expansion candidates and questions: none. Browser CI and publication introduce different risk and verification classes.

Stop conditions: any secret or write permission; protected or live data/service requirement; push, `workflow_dispatch`, deployment, sync, or operational-workflow edit; inability to keep checkout non-persistent or action references immutable; Linux/Python 3.12 compatibility requiring product change; need for Task 3.3; failed verification, dashboard, scope, or preserved-file checks.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; maintained static safety check; YAML syntax; relevant Python compilation and JavaScript syntax; JSON validation; dashboard refresh, health, generated currentness and rendered inspection; `git diff --check`; exact changed and staged paths; zero external actions; and all three preserved untracked files.

Dashboard closeout: show 4BJ active with Task 3.1 current before branch/workflow work. At completion, mark Tasks 3.1-3.2 and 4BJ complete locally, keep Task 3 active, and make 4BJ-R publication/observation the next separate gate while Task 3.3 remains planned behind a stable live core run.

Report point: return the exact local workflow contract, maintained safety guarantees, verification, changed paths, branch and zero-staged state, protected exclusions, and the separately gated 4BJ-R proposal.

Suggested next work block: 4BJ-R to publish the exact verified source through a feature branch and draft PR and observe the core synthetic run without merge or deployment. Consider Task 3.3 only after the live core run is stable.

Result: the new PR-to-`main` workflow grants `contents: read` only, persists no checkout credentials, pins the official checkout and setup-python actions to verified full commit SHAs, uses Python 3.12 and `requirements.txt` only, and runs the maintained safety, full synthetic smoke, syntax, JSON, generated-dashboard currentness, CI-health, and pull-request whitespace checks. Baseline and final local smoke plus a disposable Python 3.12 install and full smoke, YAML, Python/JavaScript syntax, JSON, dashboard, whitespace, secret-pattern, exact-scope, zero-staged, and preserved-file checks pass. GitHub-runner egress is explicitly bounded but not sandboxed: pinned actions and public dependency installation use normal network access, while the reviewed workflow contains no other network command and receives no secrets, write authority, protected data, or real input. No staging, commit, push, PR, workflow action, deployment, production/protected access, product change, operational-workflow edit, delegation, second opinion, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-25-safe-pr-synthetic-ci-foundation-4bj.md`.

### Confirmed Work Block 4BI-R: Cash Flow Boundary Repair And Financial-Coverage Durability Without Deployment

Status: done and durable without deployment; confirmed and completed on 2026-07-25.

Parent task: Phase 4 Task 4, limited to the exact verified combined 4BG/4BH/4BI durability slice.

Included: record 4BI-R active; re-run the approved source-package checks; explicitly stage only `web/routes/cashflow.py`, `web/templates/cashflow.html`, `web/static/cashflow.js`, `scripts/mobile_drawer_browser_test.py`, `scripts/smoke_test.py`, `command-center/decisions.md`, `command-center/index.html`, `command-center/issues.md`, `command-center/now.md`, `command-center/roadmap.md`, `command-center/state.json`, `command-center/logs/2026-07-25-cashflow-financial-behavior-coverage-4bg.md`, `command-center/logs/2026-07-25-cashflow-entity-boundary-repair-4bh.md`, and `command-center/logs/2026-07-25-cashflow-financial-behavior-coverage-4bi.md`; create one `[skip actions]` source commit on `codex/cashflow-read-model-coverage`; cleanly fast-forward local `main`; non-force push `origin/main`; verify exact live remote SHA and zero workflow activity; then publish one sanitized `[skip actions]` closeout commit.

Excluded: broader Task 2; Task 3 CI; further Task 4 scope; Phase 5; product/test/documentation expansion or repair; migrations; dependencies; authentication; CSP; PWA; Plaid; PR creation; workflow dispatch, rerun, cancellation, or edits; deployment; production/demo/Fly access; credentials; protected data; real databases/uploads; downstream systems; force push; conflict resolution; rebase; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the 4BG stop evidence, resolved issue, 4BH safety repair, 4BI financial-behavior matrix, maintained browser proof, and Runway OS closeout form one auditable Cash Flow result. Omitting any part would separate the repair from either its root-cause evidence or its maintained acceptance proof.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact-path verification, sensitive-addition review, staging, commits, ancestry, clean main fast-forward, non-force pushes, remote/no-workflow verification, dashboard stewardship, and final intake.

Runner path: continue in the current task on `codex/cashflow-read-model-coverage`; verify active Runway OS and GitHub prerequisites; re-run the complete source-package checks; resolve local and live `main`; stage the fourteen approved paths only; create and inspect the source commit; cleanly fast-forward and push `main`; verify exact SHA and zero workflow activity; then write, verify, commit, and push the sanitized closeout.

Expected paths: the exact fourteen source-package paths listed above. Closeout may change only `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, `command-center/state.json`, and one new sanitized 4BI-R release log.

Defaults: explicit-path staging; two `[skip actions]` commits; direct non-force main publication without a PR; no workflow action, deployment, Fly access, production access, or production health check; preserve all three unrelated untracked files; expected source parent `e9ce4d002b1527516f1fbe8bdefa513e4bb41497`, subject to immediate pre-stage revalidation.

Blocking questions: none.

Expansion candidates and questions: none. Task 3 CI and Phase 5 use different definitions of done.

Stop conditions: an unexpected or sensitive path; preserved-file overlap; verification, cleanup, dashboard, or scope failure; live remote divergence; non-fast-forward requirement; push rejection; inability to verify GitHub; any workflow run or deployment despite `[skip actions]`; or recovery beyond read-only diagnosis. If a workflow unexpectedly starts, stop and report rather than cancel it.

Verification: full `.venv/bin/python scripts/smoke_test.py`; full `.venv/bin/python scripts/mobile_drawer_browser_test.py`; relevant Python compilation; JavaScript syntax; maintained sections 8l-8m denied-network/exact-cleanup proof; high-confidence sensitive-addition review; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed/staged/committed path checks; commit ancestry; exact live remote and GitHub SHA; zero workflow activity for both commits; final local/remote alignment; and all three preserved files.

Dashboard closeout: show 4BI-R active with Task 4 current before staging. After remote verification, mark 4BI-R, Tasks 1P.7.4a-1P.7.4b, and the Task 1P.7.4 umbrella durable without deployment; make Task 3 the sole current planning gate for a just-in-time decomposition; refresh, health-check, and inspect the rendered dashboard.

Report point: return source and closeout SHAs, exact published paths, ancestry and remote alignment, zero-workflow/no-deployment result, verification, final worktree state, preserved exclusions, and the separate Task 3 planning gate.

Suggested next work block: run a just-in-time Task 3 decomposition, then separately propose a 4BJ safe synthetic CI block.

Result: full smoke, maintained configured-auth/no-password browser coverage, relevant Python and JavaScript syntax, sections 8l-8m denied-network/exact-cleanup proof, high-confidence sensitive-addition review, JSON, whitespace, dashboard, exact-path, ancestry, remote, and preserved-file checks passed. Exact fourteen-path source commit `e0b7ec1eda9b39d365062c5511bd1d93868f44c4`, with parent `e9ce4d002b1527516f1fbe8bdefa513e4bb41497`, was fast-forwarded and pushed non-force to `main`. Local, tracking, live remote, and GitHub SHA checks aligned; GitHub reported zero workflow runs. No PR, workflow action, deployment, Fly action, production access, protected-data access, or production health check occurred. Evidence: `command-center/logs/2026-07-25-cashflow-boundary-financial-coverage-release-4bi-r.md`.

### Confirmed Work Block 4BI: Cash Flow Financial-Behavior Coverage Completion

Status: complete and locally verified; confirmed and completed on 2026-07-25; uncommitted.

Parent tasks: Phase 4 Task 1P.7.4b plus only its focused Task 2 / `P3-3C-C01` regression slice.

Included: add maintained temporary Personal, BFM, and Luxe Legacy proof for bank and card persistence; due-day and derived-date behavior; stored liability rendering without Plaid retrieval; manual recurring add, projection, and delete; cadence classification and representative automatic projections; stale, irregular, and horizon exclusions; month-end and year-boundary behavior; empty states; reciprocal read-only Personal/BFM visibility; Luxe Legacy isolation; valid active-entity writes; denied networking; exact row and sequence cleanup; and local Runway OS closeout.

Excluded: broader Task 2; Tasks 3-4; further product repair or redesign; migrations; dependencies; categories; authentication; CSRF; CSP; PWA; unrelated UI; Plaid fetching, linking, or synchronization; protected data; real databases/uploads; credentials; production/demo; external or downstream systems; GitHub durability; workflows; Fly; deployment; publication; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the included behavior shares the Cash Flow read model, `account_balances` and `manual_recurring` persistence, recurrence helpers, one temporary all-entity fixture, the verified 4BH visibility contract, denied networking, and exact cleanup. Product repair, browser-policy work, CI, durability, and publication use different definitions of done.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The block requires deterministic maintained-test integration, temporary financial-fixture cleanup, all-entity verification, and Runway OS stewardship.

Runner path: continue on `codex/cashflow-read-model-coverage`; verify active Runway OS; run baseline full smoke; add one focused maintained Cash Flow section while keeping product source read-only; run the complete verification bundle; then close locally as passed or stopped without commit or publication.

Expected paths: `scripts/smoke_test.py`; one sanitized 4BI evidence log; `command-center/decisions.md`; `command-center/index.html`; `command-center/now.md`; `command-center/roadmap.md`; and `command-center/state.json`. `command-center/issues.md` may change only if a confirmed mismatch requires a durable finding. No product path is expected.

Defaults: use fixed reference dates; temporary Personal, BFM, and Luxe Legacy databases; stored-field liability proof rather than duplicate Plaid-fetch coverage; cadence-band classification plus representative weekly, biweekly, and monthly projection behavior; deterministic stale, irregular, horizon, month-end, and year-boundary cases; denied outbound networking; before/after row and sequence snapshots; local-only uncommitted closeout; and preservation of all three unrelated untracked files.

Blocking questions: none. Ryan confirmed the recommended 4BI proposal and existing 4BH read-only sibling contract.

Expansion candidates and questions: none. Broader Task 2, product repair, CI, durability, publication, protected access, and live action remain later gates.

Stop conditions: any product mismatch or need for product repair; need for migration, dependency, authentication, Plaid, protected-data, external, live, publication, deployment, or other excluded work; scope expansion; plan-changing verification failure; failed cleanup or command-center health; or preserved-file overlap.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused bank/card, stored-liability, manual/automatic recurrence, date-boundary, empty, reciprocal read-only visibility, Luxe Legacy, current-entity write, denied-network, and exact-cleanup proof; relevant Python compilation; maintained configured-auth and no-password isolated-browser regression; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed-path review; and all three preserved files.

Dashboard closeout: after a pass, mark 4BI, Task 1P.7.4b, and the Task 1P.7.4 umbrella complete locally; make exact-scope 4BI-R durability without deployment the sole current planning gate; refresh, health-check, and inspect the rendered dashboard. Record the exact stop instead if any stop condition fires.

Report point: return the exact maintained matrix, confirmed behavior or stopped mismatch, cleanup proof, verification, changed paths, branch/worktree state, preserved exclusions, and the separate 4BI-R durability gate.

Suggested next work block: 4BI-R Cash Flow Boundary Repair And Financial-Coverage Durability Without Deployment for the exact verified combined 4BH/4BI set.

Result: maintained section 8m proves primary empty states in separate disposable databases; all-entity bank/card persistence; stored liability rendering without Plaid retrieval; stored and derived due dates; manual add/projection/delete with month-end and year rollover; all cadence classification bands; representative weekly, biweekly, and monthly projections; irregular, stale, and horizon exclusions; reciprocal read-only Personal/BFM financial visibility; Luxe Legacy isolation; valid active-entity writes; denied networking; and exact row/sequence cleanup. The first new iteration corrected only a whole-dollar display expectation. Product source remained read-only. Baseline and final full smoke, maintained configured-auth/no-password isolated browser, Python and JavaScript syntax, JSON, whitespace, dashboard, exact-scope, and preserved-file checks pass. Task 1P.7.4b and the Task 1P.7.4 umbrella are complete locally. Evidence: `command-center/logs/2026-07-25-cashflow-financial-behavior-coverage-4bi.md`.

### Confirmed Work Block 4BH: Cash Flow Shared-Entity Mutation Boundary Repair

Status: complete and locally verified; confirmed and completed on 2026-07-25; uncommitted.

Parent tasks: Phase 4 Task 1P.7.4a plus only its focused Task 2 regression slice.

Included: preserve Personal/BFM sibling Cash Flow balances, liabilities, and upcoming information while removing sibling edit, delete, recurring-entry, mutation action, and mutation-target data; require submitted entity targets to match the active cookie entity for account, card, and recurring mutations; preserve valid active-entity writes; add maintained temporary all-entity colliding-ID, missing/mismatched-target no-mutation, valid-mutation, Luxe Legacy isolation, denied-network, exact-cleanup, rendered, and focused isolated-browser proof; and close Runway OS locally after verification.

Excluded: Task 1P.7.4b; broader Task 2; Tasks 3-4; migrations; dependencies; categories; authentication; CSRF; CSP; PWA; unrelated UI work; Plaid; protected data; real databases/uploads; credentials; external systems; production/demo; GitHub durability; workflows; Fly; deployment; publication; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: sibling presentation, server target validation, and colliding-ID proof are one coherent safety repair across the same Cash Flow route/template/controller seam. The broader balance, liability, recurrence, and projection matrix depends on this boundary passing first and remains Task 1P.7.4b.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The block requires cross-file route/template/test integration, synthetic cleanup, rendered inspection, and Runway OS stewardship under a deterministic product contract.

Runner path: continue on `codex/cashflow-read-model-coverage`; verify active Runway OS; run the baseline full smoke suite; implement only the boundary repair and focused maintained coverage; run the complete verification bundle; then close locally as passed or stopped without commit or publication.

Expected paths: `web/routes/cashflow.py`; `web/templates/cashflow.html`; `web/static/cashflow.js`; `scripts/smoke_test.py`; `scripts/mobile_drawer_browser_test.py`; one sanitized 4BH evidence log; `command-center/decisions.md`; `command-center/index.html`; `command-center/issues.md`; `command-center/now.md`; `command-center/roadmap.md`; and `command-center/state.json`.

Defaults: Personal/BFM sibling sections remain visible but read-only; missing or mismatched submitted entity targets receive controlled HTTP 404 with zero mutation; valid active-entity forms remain supported; temporary Personal, BFM, and Luxe Legacy databases use colliding local IDs, denied outbound networking, and exact row/sequence cleanup; preserve all three unrelated untracked files.

Blocking questions: none. Ryan confirmed the recommended read-only sibling and strict active-entity mutation contract.

Expansion candidates and questions: none. Task 1P.7.4b, CI, durability, publication, and live actions use separate definitions of done and remain later gates.

Stop conditions: a requested cross-entity editing contract; need for migration, dependency, authentication, CSRF, CSP, PWA, protected, credential, Plaid, external, live, publication, or deployment work; scope expansion; plan-changing verification failure; failed cleanup or command-center health; or preserved-file overlap.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused source/rendered/isolated-browser sibling-read-only and active-edit proof; colliding-ID missing/mismatched-target no-mutation checks for every included route; valid current-entity bank/card/recurring writes; Luxe Legacy isolation; denied networking; exact cleanup; relevant Python and JavaScript compilation; JSON; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed-path review; and all three preserved files.

Dashboard closeout: after a pass, mark 4BH and Task 1P.7.4a done locally, make Task 1P.7.4b the sole current planning gate, refresh, health-check, and inspect the rendered dashboard. Record the exact stop instead if any stop condition fires.

Report point: return exact repaired behavior, maintained proof, verification and cleanup, changed paths, branch/worktree state, preserved exclusions, and the separate Task 1P.7.4b or durability gate.

Suggested next work block: 4BI Cash Flow Financial-Behavior Coverage Completion for Task 1P.7.4b after 4BH passes.

Result: Personal/BFM sibling cards retain balances, liability detail, and upcoming information through a view-only flip but contain no account ID, entity target, edit modal, recurring form, or mutation-target data. Account, card, recurring-add, and recurring-delete routes require the submitted entity to equal the active cookie entity and return controlled HTTP 404 before database access for missing or mismatched targets. Maintained temporary all-entity colliding-ID proof covers every rejection path, zero mutation, valid active-entity writes, read-only rendered controls, Luxe Legacy isolation, denied networking, and exact row/sequence cleanup. Baseline and final full smoke, the maintained isolated-browser suite in both authentication modes, focused rendered inspection, Python and JavaScript syntax, JSON, whitespace, dashboard, exact-scope, and preserved-file checks pass. The first new smoke iteration corrected only an over-narrow exact sibling-card count. No migration, dependency, authentication, CSRF, CSP, PWA, Plaid, protected data, real database, credential, external/live, GitHub, workflow, Fly, deployment, publication, or preserved-file action occurred. Evidence: `command-center/logs/2026-07-25-cashflow-entity-boundary-repair-4bh.md`.

### Confirmed Work Block 4BG: Cash Flow Financial-Behavior Coverage

Status: stopped locally at a confirmed product-boundary mismatch; confirmed and stopped on 2026-07-25.

Parent tasks: Phase 4 Task 1P.7.4 and only its focused Task 2 / `P3-3C-C01` regression slice.

Included: add maintained temporary Personal, BFM, and Luxe Legacy proof for manual bank balance updates; credit-card balance, limit, APR, payment, and due-date persistence; existing cached/manual liability rendering; manual recurring add, projection, and delete; representative automatic recurring projections and date boundaries; empty states; Personal/BFM shared visibility; Luxe Legacy isolation; cookie-owned write isolation; denied networking; and exact cleanup.

Shared-visibility decision: Personal and BFM may see each other's Cash Flow sections, but those sibling sections are read-only. Active-entity mutations remain cookie-owned. If the current rendered or route contract exposes or misroutes a foreign-entity mutation, 4BG stops and records the mismatch without changing product source.

Excluded: Tasks 1P.7.1-1P.7.3; broader Task 2; Task 3 CI; Task 4 publication; product repair or redesign; migrations; dependencies; categories; authentication; CSRF; CSP; browser/PWA behavior; Plaid fetching or synchronization; protected data; real databases/uploads; credentials; production/demo; external networking; downstream systems; GitHub durability; workflows; Fly; deployment; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the included behavior shares the Cash Flow route module, `account_balances` and `manual_recurring` persistence, one temporary all-entity fixture, the same entity-visibility contract, a denied-network boundary, and exact row/sequence cleanup. Upstream Plaid account/liability refresh is already covered through 4J; browser behavior, CI, repair, and publication use different contracts and remain separate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns maintained-test integration, exact synthetic verification, dashboard stewardship, and final intake.

Runner path: write and verify active Runway OS, create `codex/cashflow-read-model-coverage`, run the baseline full smoke suite, add one focused maintained Cash Flow section without product changes, run the complete verification bundle, then close locally as passed or stopped.

Expected paths: `scripts/smoke_test.py`; one sanitized 4BG evidence log; `command-center/decisions.md`; `command-center/index.html`; `command-center/now.md`; `command-center/roadmap.md`; and `command-center/state.json`. `command-center/issues.md` may change only if a confirmed mismatch requires a durable finding. No product path is expected.

Defaults: fixed synthetic dates; temporary Personal, BFM, and Luxe Legacy databases; stored-field liability proof rather than duplicate Plaid-fetch coverage; denied outbound networking; before/after row and sequence snapshots; local-only and uncommitted result; preserve all three unrelated untracked files.

Blocking question resolved: Ryan accepted read-only Personal/BFM shared visibility by confirming the recommended 4BG proposal.

Expansion candidates and questions: none. Broader Task 2, CI, repair, and publication use different risk and verification paths.

Stop conditions: an ambiguous or violated shared-visibility/write contract; any product defect or need for product repair; need for migration, dependency, browser, authentication, protected-data, Plaid, external, live, publication, or deployment work; scope expansion; plan-changing verification failure; failed cleanup or command-center health; or preserved-file overlap.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused current-entity bank/card writes, stored liabilities, manual/automatic recurrence, empty, read-only shared visibility, Luxe Legacy isolation, denied-network, and exact-cleanup proof; relevant Python compilation; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed-path review; and all three preserved files.

Dashboard closeout: show 4BG active with Task 1P.7.4 current, Codex owner, the read-only shared-visibility decision, stop conditions, verification, and report point before maintained-test work. At closeout, mark 4BG and Task 1P.7.4 done locally or record the exact stop, refresh, health-check, and inspect the rendered dashboard.

Report point: return exact maintained coverage, confirmed behavior or stopped mismatch, cleanup proof, verification, changed paths, branch state, preserved exclusions, and the next separate durability or repair gate.

Suggested next work block: 4BG-R exact-scope durability if 4BG passes without product changes; otherwise separately plan a Cash Flow entity-boundary repair.

Stop result: active-state JSON, dashboard refresh/health/generated/rendered inspection, branch creation, and the baseline full synthetic smoke suite passed. A disposable denied-network probe then created colliding synthetic account IDs in Personal, BFM, and Luxe Legacy. The Personal Cash Flow response exposed the BFM sibling card through the editable action; submitting that sibling card's ID and hidden BFM entity value returned the normal redirect, changed the same-ID Personal row, and left the intended BFM row plus Luxe Legacy unchanged. The temporary root was removed exactly. 4BG stopped before maintained-test expansion because this violates the confirmed read-only shared-visibility contract. No product or test repair, migration, protected access, external call, GitHub action, workflow, Fly action, deployment, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-25-cashflow-financial-behavior-coverage-4bg.md`.

Revised next block: separately propose a Cash Flow entity-boundary repair that makes sibling sections truly read-only or adopts another explicit Ryan-approved mutation contract, then resumes the maintained 4BG matrix.

### Confirmed Work Block 4BF-R: Subscription Lifecycle Coverage Durability Without Deployment

Status: done and durable on `origin/main`; confirmed and completed on 2026-07-25 with zero workflow runs and no deployment.

Parent task: Phase 4 Task 4, limited to the exact verified 4BF durability slice.

Included: record 4BF-R active; re-run the approved 4BF release checks; explicitly stage only `scripts/smoke_test.py`, `command-center/logs/2026-07-25-subscription-lifecycle-coverage-4bf.md`, `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create one `[skip actions]` source commit on `codex/subscription-lifecycle-coverage`; cleanly fast-forward local `main`; non-force push `origin/main`; verify the exact live remote SHA and zero workflow activity; then publish one sanitized `[skip actions]` closeout commit.

Excluded: Task 1P.7.4; broader Task 2; Task 3 CI; product or maintained-test expansion or repair; dependencies; migrations; browser/PWA/authentication behavior; PR creation; workflow dispatch, rerun, cancellation, or edits; deployment; production/demo/Fly access; credentials; protected data; real databases/uploads; Plaid; downstream systems; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: 4BF produced one coherent seven-path maintained-test and sanitized command-center package with no product/runtime change. One exact-path `[skip actions]` durability sequence makes that verified result durable without triggering an unnecessary Fly deployment. Cash Flow uses different fixtures, persistence mutations, visibility rules, calculations, and verification and remains a later gate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path verification, sensitive-addition review, staging, commits, ancestry, clean main fast-forward, non-force pushes, remote/no-workflow verification, dashboard stewardship, and final intake.

Runner path: continue in the current task on `codex/subscription-lifecycle-coverage`; verify active Runway OS; re-run the complete source-package checks; resolve live remote `main`; stage the seven approved paths only; create the source commit; verify its contents and parent; cleanly fast-forward and push `main`; verify the exact SHA and zero workflow activity; then write, verify, commit, and push the sanitized closeout.

Expected paths: the exact seven source-package paths listed above. Closeout may change only `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, `command-center/state.json`, and one new sanitized 4BF-R release log.

Defaults: explicit-path staging; two `[skip actions]` commits; direct non-force main publication without a PR; no workflow action, deployment, production access, or production health check; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Task 1P.7.4 and CI have different scopes and remain separate.

Stop conditions: an unexpected or sensitive path; verification, cleanup, dashboard, scope, or preserved-file failure; live remote divergence; non-fast-forward requirement; push rejection; any workflow run or deployment despite `[skip actions]`; or recovery beyond clean fast-forward and read-only diagnosis. If a workflow unexpectedly starts, stop and report rather than cancel it.

Verification: full `.venv/bin/python scripts/smoke_test.py`; `.venv/bin/python -m py_compile scripts/smoke_test.py`; denied networking and exact cleanup through maintained section 8k; high-confidence sensitive-addition review; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed/staged/committed path checks; commit ancestry; exact live remote SHA; zero workflow activity for both commits; final local/remote alignment; and all three preserved files.

Dashboard closeout: show 4BF-R active with Task 4 current before staging. After remote verification, mark 4BF-R and Task 1P.7.3 durable, restore Task 1P.7.4 as the sole current planning gate, refresh, health-check, and inspect the rendered dashboard.

Report point: return source and closeout SHAs, exact published paths, remote alignment, zero-workflow/no-deployment result, verification, final worktree state, preserved exclusions, and the separate 4BG planning gate.

Suggested next work block: 4BG for Task 1P.7.4 Cash Flow coverage after a separate proposal and confirmation.

Closeout result: full smoke, Python compilation, section 8k denied-network/exact-cleanup coverage, sensitive-addition review, JSON, whitespace, dashboard refresh/health/generated/rendered state, exact changed/staged/committed paths, commit ancestry, live remote resolution, and all three preserved-file checks passed. Exact seven-path source commit `a2ed513c3095f9df1f43039ab674e6894b12214a` is durable on `origin/main`; local `HEAD`, local `main`, tracking `origin/main`, live remote `main`, and GitHub all resolved to that SHA after the non-force push. GitHub reported zero workflow runs, so no Fly deployment or production access occurred. This sanitized closeout uses `[skip actions]`. Evidence: `command-center/logs/2026-07-25-subscription-lifecycle-coverage-release-4bf-r.md`.

### Confirmed Work Block 4BF: Subscription Detection And Lifecycle Regression Coverage

Status: done and locally verified on `codex/subscription-lifecycle-coverage`; confirmed and completed on 2026-07-25; uncommitted and not published.

Parent tasks: Phase 4 Task 1P.7.3 and only its focused Task 2 / `P3-3C-C01` regression slice.

Included: add maintained temporary all-entity synthetic proof for all five detection cadences, amount regularity, staleness and exclusions, empty rendering, suggestion acceptance, manual watchlist addition, detail, status/notes/timeline/payment-method persistence, stored synthetic cancellation-tip metadata, account-information add/delete, dismiss/restore, share text, watchlist deletion and related-row cleanup, reopened-connection persistence, denied networking, and entity-local output and writes.

Excluded: Task 1P.7.4; broader Task 2; Task 3 CI; Task 4 publication; product repair or redesign; migrations; dependencies; categories; authentication; CSRF; CSP; browser/PWA behavior; real AI/OpenRouter generation; protected data; real databases/uploads; credentials; production/demo; external networking; Plaid; downstream systems; GitHub durability; workflows; Fly; deployment; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: detection, watchlist lifecycle, metadata, and persistence share one subscription route module, four related tables, one temporary all-entity harness, one denied-network boundary, and one exact-cleanup contract. Cash Flow uses different persistence, visibility, calculations, and acceptance checks and remains separate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns maintained-test integration, product-contract intake, cleanup, Runway OS stewardship, and final verification.

Runner path: activate 4BF in Runway OS; create `codex/subscription-lifecycle-coverage`; run the baseline full smoke suite; add one focused maintained smoke section using only temporary Personal, BFM, and Luxe Legacy databases; keep product source read-only; run focused and final verification; then close locally and uncommitted.

Expected paths: primarily `scripts/smoke_test.py`; one sanitized 4BF evidence log; `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`. Product source is inspection-only.

Defaults: use stored or deterministically mocked synthetic cancellation tips only; deny all outbound networking; prove each entity independently; reopen connections for persistence checks; snapshot before seeding; restore all affected rows and SQLite sequences exactly; do not rerun the browser suite because product/browser code does not change; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Task 1P.7.4, CI, publication, and any repair use different contracts.

Stop conditions: a product defect or ambiguous lifecycle/entity contract; need for excluded product, migration, dependency, protected, credential, real-data, external, live, or publication work; scope expansion; plan-changing verification failure; cleanup or command-center health failure; or preserved-file overlap.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused detection, cadence, regularity, lifecycle, persistence, empty, isolation, denied-network, and cleanup assertions; relevant Python compilation; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered-dashboard inspection; exact changed-path scope; and all three preserved files.

Dashboard closeout: show 4BF active with Task 1P.7.3 current, Codex owner, exact exclusions, stop conditions, verification, and report point before implementation. After passing verification, mark 4BF and Task 1P.7.3 done locally, make Task 1P.7.4 the sole current planning gate, refresh, health-check, and inspect the rendered dashboard.

Report point: return exact maintained coverage, confirmed behavior, any stopped product mismatch, verification and cleanup, changed paths, branch state, preserved exclusions, and the separate 4BF-R durability or 4BG Task 1P.7.4 planning gate.

Suggested next work block: 4BF-R exact-scope durability if separately authorized; otherwise propose 4BG for Task 1P.7.4 Cash Flow coverage.

Closeout result: section 8k of the maintained smoke suite now proves all five cadence classes, amount regularity, staleness and exclusions, all-entity empty rendering, suggestion acceptance, manual add, detail, status/notes/timeline/payment-method persistence, stored deterministic cancellation-tip metadata, account-information add/delete, dismiss/restore, share text, delete cascades, reopened persistence, entity-local output and writes, denied networking, and exact restoration of rows and four subscription SQLite sequences. Baseline and final full smoke, Python compilation, JSON, whitespace, dashboard refresh/health/generated/rendered state, exact scope, and all three preserved-file checks pass. No product mismatch or repair need was found and product source did not change. Evidence: `command-center/logs/2026-07-25-subscription-lifecycle-coverage-4bf.md`.

### Confirmed Work Block 4BE-R: Financial Read-Model Coverage Durability Without Deployment

Status: done and durable on `origin/main`; confirmed and completed on 2026-07-25 with zero workflow runs and no deployment.

Parent task: Phase 4 Task 4, limited to the exact verified 4BE durability slice.

Included: record 4BE-R active; re-run the approved 4BE release checks; explicitly stage only `scripts/smoke_test.py`, `command-center/logs/2026-07-24-financial-read-model-export-coverage-4be.md`, `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`; create one `[skip actions]` source commit on `codex/financial-read-model-planning`; cleanly fast-forward local `main`; non-force push `origin/main`; verify the exact live remote SHA and zero workflow activity; then publish one sanitized `[skip actions]` closeout commit.

Excluded: Tasks 1P.7.3-1P.7.4; broader Task 2; Task 3 CI; product or maintained-test expansion or repair; dependencies; migrations; browser/PWA/authentication behavior; PR creation; workflow dispatch, rerun, cancellation, or edits; deployment; production/demo/Fly access; credentials; protected data; real databases/uploads; Plaid; downstream systems; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: 4BE produced one coherent seven-path maintained-test and sanitized command-center package with no product/runtime change. One exact-path `[skip actions]` durability sequence makes that verified result durable without triggering an unnecessary Fly deployment. Subscription and Cash Flow lifecycle coverage use different fixtures, persistence mutations, route contracts, and verification and remain later gates.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path verification, sensitive-addition review, staging, commits, ancestry, clean main fast-forward, non-force pushes, remote/no-workflow verification, dashboard stewardship, and final intake.

Runner path: continue in the current thread on `codex/financial-read-model-planning`; verify active Runway OS; re-run the complete source-package checks; resolve live remote `main`; stage the seven approved paths only; create the source commit; verify its contents and parent; cleanly fast-forward and push `main`; verify the exact SHA and zero workflow activity; then write, verify, commit, and push the sanitized closeout.

Expected paths: the exact seven source-package paths listed above. Closeout may change only `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, `command-center/state.json`, and one new sanitized 4BE-R release log.

Defaults: explicit-path staging; two `[skip actions]` commits; direct non-force main publication without a PR; no workflow action, deployment, production access, or production health check; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Tasks 1P.7.3-1P.7.4 and CI have different scopes and remain separate.

Stop conditions: an unexpected or sensitive path; verification, cleanup, dashboard, scope, or preserved-file failure; live remote divergence; non-fast-forward requirement; push rejection; any workflow run despite `[skip actions]`; any deployment activity; or recovery beyond clean fast-forward and read-only diagnosis.

Verification: full `.venv/bin/python scripts/smoke_test.py`; `.venv/bin/python -m py_compile scripts/smoke_test.py`; denied networking, read-only preservation, and exact cleanup through maintained section 8j; high-confidence sensitive-addition review; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed/staged/committed path checks; commit ancestry; exact live remote SHA; zero workflow activity for both commits; final local/remote alignment; and all three preserved files.

Dashboard closeout: show 4BE-R active with Task 4 current before staging. After remote verification, mark 4BE-R and Tasks 1P.7.1-1P.7.2 durable, restore Task 1P.7.3 as the sole current planning gate, refresh, health-check, and inspect the rendered dashboard.

Report point: return source and closeout SHAs, exact published paths, remote alignment, zero-workflow/no-deployment result, verification, final worktree state, preserved exclusions, and the separate 4BF planning gate.

Suggested next work block: 4BF for Task 1P.7.3 subscription detection and lifecycle coverage after a separate proposal and confirmation.

Closeout result: full smoke, Python compilation, section 8j denied-network/read-only/exact-cleanup coverage, high-confidence sensitive-addition review, JSON, whitespace, dashboard refresh/health/generated/rendered state, exact changed/staged/committed paths, commit ancestry, live remote resolution, and all three preserved-file checks passed. Exact seven-path source commit `36007de4100b3ded048d9020403ac7d94fdbb706` is durable on `origin/main`; local `HEAD`, local `main`, tracking `origin/main`, live remote `main`, and GitHub all resolved to that SHA after the non-force push. GitHub reported zero workflow runs, so no Fly deployment or production access occurred. This sanitized closeout uses `[skip actions]`. Evidence: `command-center/logs/2026-07-25-financial-read-model-coverage-release-4be-r.md`.

### Confirmed Work Block 4BE: Financial Read-Model Reconciliation And Export Coverage

Status: done and locally verified on 2026-07-24; uncommitted and not published.

Parent tasks: Phase 4 Tasks 1P.7.1-1P.7.2 and only their focused Task 2 regression slice.

Included: add maintained all-entity synthetic coverage for effective-transaction split replacement, centralized exclusions, signed income/spend reconciliation, dashboard counts and filters, empty and entity-specific output, every non-recurring standard report through direct preparation and rendered view, CSV/PDF exports, supported transaction QBO, filenames, response types, empty/missing inputs, reconciled totals, denied networking, entity isolation, and exact cleanup. Preserve the separately maintained 4H Recurring Charges matrix.

Excluded: Tasks 1P.7.3-1P.7.4; Task 3 CI; Task 4 publication; product or financial-business-logic repair; browser/PWA work; dependencies; migrations; authentication, CSRF, CSP, cache, or public-route changes; credentials; protected data; real financial rows or databases; retained uploads; production/demo; external networking; Plaid; downstream systems; GitHub durability; workflows; Fly; deployment; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: Tasks 1P.7.1-1P.7.2 share one synthetic effective-ledger fixture, reporting helpers, route layer, export matrix, risk class, and verification path. Subscription and Cash Flow coverage introduce distinct persistence tables, mutation lifecycles, route contracts, and definitions of done.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns fixture design, maintained-test implementation, source-contract intake, local verification, cleanup, Runway OS stewardship, and final scope review.

Runner path: continue on `codex/financial-read-model-planning`; record 4BE active; run baseline full smoke; add only maintained synthetic coverage in the existing smoke harness; treat current behavior and the original 3C expected contract as authoritative unless a mismatch triggers a stop; run focused and full verification; reconcile sanitized evidence and Runway OS; close locally and uncommitted.

Expected paths: primarily `scripts/smoke_test.py`; read-only inspection of `core/reporting.py`, `web/routes/dashboard.py`, and `web/routes/reports.py`; one sanitized 4BE evidence log; and Runway OS sources plus generated dashboard. Product source should remain unchanged unless the block stops for a separately proposed repair.

Defaults: temporary Personal, BFM, and Luxe Legacy databases only; one shared effective-ledger fixture; denied outbound networking; exact cleanup; preserve existing 4H recurring-report proof; no browser run unless route-level evidence proves insufficient; local-only durability; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Tasks 1P.7.3-1P.7.4 require separate persistence and lifecycle work.

Stop conditions: a product defect or ambiguous financial contract; need for product repair, migration, dependency, real data, credential, protected access, external system, or live action; scope expansion; plan-changing verification failure; exact-cleanup failure; command-center refresh or health failure; or overlap with a preserved untracked file.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused effective-ledger, dashboard, report-preparation, rendered-view, CSV, PDF, QBO, empty/missing-input, all-entity, isolation, denied-network, and cleanup checks; Python compilation; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed-path review; and preservation of all three unrelated untracked files.

Dashboard closeout: while active show 4BE, Task 1P.7.1 current, Codex owner, exact exclusions, stop conditions, verification, and report point. After passing verification, mark Tasks 1P.7.1-1P.7.2 and 4BE done locally, make Task 1P.7.3 current at its next planning gate, refresh, health-check, and inspect the dashboard.

Report point: return the exact coverage added, reconciled behavior, any stopped defect, focused and full verification, cleanup, changed paths, local branch and durability state, preserved exclusions, and the next separately gated work block.

Suggested next work block: 4BE-R for exact-scope durability only if separately authorized; otherwise plan 4BF for Task 1P.7.3 subscription lifecycle coverage.

Closeout result: the maintained smoke suite now uses one isolated two-month effective-ledger fixture per entity to prove exact split replacement, centralized exclusions, signed totals, dashboard KPIs and account/transfer behavior, all seven non-recurring report families through direct preparation and rendered view, CSV/PDF, transaction-only QBO, stable filenames and response types, missing/empty ranges, all-entity isolation, denied networking, read-only preservation, and exact cleanup. Baseline and final full smoke, Python compilation, JSON, whitespace, dashboard refresh/health/generated/rendered state, exact scope, and all three preserved-file checks pass. No product defect or repair need was found; product source did not change. Evidence: `command-center/logs/2026-07-24-financial-read-model-export-coverage-4be.md`.

### Confirmed Work Block 4BD-R: Installed-PWA Browser-Coverage Durability

Status: done and durable on `origin/main`; confirmed and completed on 2026-07-24.

Parent task: Phase 4 Task 4, limited to the exact verified 4BD durability slice.

Included: record 4BD-R as active; re-run the approved 4BD release checks; explicitly stage only the nine intended maintained-test and sanitized command-center paths; create one `[skip actions]` source commit on `codex/pwa-browser-boundary-coverage`; cleanly fast-forward local `main`; non-force push `origin/main`; verify the exact remote SHA and absence of workflow activity; then add, commit, and push one sanitized `[skip actions]` closeout.

Excluded: Task 1P.7; broader Task 2; Task 3 CI; product, asset, application-runtime, dependency, workflow, or configuration changes beyond the already verified 4BD maintained test; PR creation; deployment; production/demo/Fly access; credentials; protected data; real databases/uploads; Plaid; downstream systems; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: 4BD produced one coherent maintained-test and sanitized command-center package with no product/runtime change. One exact-path `[skip actions]` durability sequence makes that verified result durable without triggering an unnecessary Fly deployment. Task 1P.7 and CI require different planning, risk, and verification paths.

Owner and recommended agent: Codex Desktop in the current task. No delegation or second opinion. Codex owns scope review, verification, explicit staging, commits, clean ancestry, non-force push, no-workflow proof, dashboard currency, and final intake; Ryan owns every expansion, live action, deployment, protected-access, and later-task decision.

Runner path: verify active Runway OS; run full smoke, isolated Chrome, compilation, cleanup, sensitive-addition, JSON, whitespace, dashboard, and exact-scope checks; create the `[skip actions]` source commit; cleanly fast-forward and push `main`; verify exact remote/no-workflow state; then publish the sanitized `[skip actions]` closeout and verify final alignment.

Expected source paths: `scripts/mobile_drawer_browser_test.py`; `command-center/decisions.md`; `command-center/index.html`; `command-center/issues.md`; `command-center/now.md`; `command-center/phase-3-findings-consolidation.md`; `command-center/roadmap.md`; `command-center/state.json`; and `command-center/logs/2026-07-24-installed-pwa-browser-boundary-coverage-4bd.md`. Closeout may add one sanitized 4BD-R log and update only the command-center state sources and generated dashboard.

Defaults: exact-path staging; two `[skip actions]` commits; direct non-force `main` publication; no PR, workflow action, deployment, production health check, or live access; preserve all three unrelated untracked files.

Blocking questions: none.

Expansion candidates and questions: none. Task 1P.7 and Task 3 introduce different scope and remain separate.

Stop conditions: an unexpected or sensitive path; failed smoke, browser, compilation, cleanup, JSON, whitespace, dashboard, scope, or preserved-file check; local/remote `main` divergence; non-fast-forward requirement; push rejection; any workflow run despite `[skip actions]`; or recovery beyond clean fast-forward and read-only diagnosis.

Verification: full `.venv/bin/python scripts/smoke_test.py`; full `.venv/bin/python scripts/mobile_drawer_browser_test.py`; Python compilation; denied networking and exact cleanup through the maintained runner; high-confidence sensitive-addition review; JSON; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; exact changed/staged/committed paths; commit ancestry; exact remote SHA; absence of workflow activity; final local/remote alignment; and all three preserved untracked files.

Dashboard closeout: show 4BD-R active with Task 4 current, Codex owner, exact exclusions, stop conditions, verification, and next report point before staging. After remote verification, mark it done and restore Task 1P.7 to the next planning gate; refresh, health-check, and inspect the rendered dashboard.

Report point: return source and closeout commit SHAs, exact published paths, remote alignment, `[skip actions]` and no-deployment result, final worktree state, preserved exclusions, and the separate Task 1P.7 planning gate.

Suggested next work block: a 4BE just-in-time planning pass that first decomposes Task 1P.7 into visible financial read-model subtasks before any implementation proposal.

Result: exact nine-path source commit `1d9f4904d0e84cc1696f7e4d89a536668a161c1e` is durable on `origin/main`. Full smoke, isolated Chrome, compilation, cleanup, sensitive-addition, JSON, whitespace, dashboard, exact staging/commit, ancestry, non-force push, remote-SHA, and preserved-file checks passed. GitHub reports zero workflow runs for the source SHA, so no Fly deployment or production access occurred. This sanitized closeout uses `[skip actions]`. Evidence: `command-center/logs/2026-07-24-installed-pwa-browser-boundary-coverage-release-4bd-r.md`.

### Confirmed Work Block 4BD: Installed-PWA And Browser-Boundary Coverage Convergence

Status: done locally and uncommitted; confirmed and completed on 2026-07-24.

Parent tasks: Phase 4 Tasks 1P.6.1-1P.6.4 and only the remaining `P3-3J-C01` browser-coverage slice.

Included: converge maintained isolated-browser proof for the linked manifest and exact installability inputs; declared icon purposes, dimensions, and same-origin availability; root-scoped service-worker installation/activation, current precache, static-only caching, protected/dynamic network-only behavior, and real generic offline navigation after representative entity visits; configured-auth full-page redirect, HTMX/JSON denial, safe local return, exempt surfaces, synthetic sign-in, and shell continuity; and exact authenticated/no-password `/k/` Personal/Luxe Legacy fields, BFM exclusion, route-owned context, responsive behavior, and no protected cache reuse.

Excluded: Task 1P.7; Task 3 CI; Task 4 publication; product, asset, authentication, cache, route, service-worker, manifest, financial, database, category, dependency, or UX repair; credentials; protected data; real databases/uploads; production/demo; non-localhost access; GitHub durability; commit, push, PR, merge, deployment, workflows, Fly, downstream systems, broader recovery, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: all four tasks consume one existing isolated-browser harness, temporary synthetic all-entity setup, configured-auth/no-password matrix, denied-network boundary, and exact cleanup path. They produce one coherent result: whether the original 3J browser boundaries are now durably guarded. Financial read models, CI, publication, and any repair require different risk or verification classes.

Owner and recommended agent: Codex Desktop in the current task. No delegation or second opinion. Codex owns maintained-test edits, verification, cleanup, issue disposition, dashboard currency, and final intake; Ryan owns every repair, product, protected/live, publication, and expansion decision.

Runner path: activate 4BD and verify Runway OS; create local branch `codex/pwa-browser-boundary-coverage`; establish baseline smoke and browser results; extend the existing maintained browser suite only where original acceptance boundaries remain implicit; run the full local closeout; then record pass or safe stop.

Expected surfaces: primarily `scripts/mobile_drawer_browser_test.py`; `scripts/smoke_test.py` only for focused source/request support if required; `command-center/issues.md`; `command-center/phase-3-findings-consolidation.md`; one sanitized 4BD evidence log; Runway OS sources; and generated `command-center/index.html`. Product files remain unchanged by default.

Defaults: use installed Chrome, temporary synthetic Personal/BFM/Luxe Legacy databases, fake configured authentication, no-password mode, localhost only, denied non-localhost traffic, disposable browser state, and exact cleanup; extend the existing runner rather than create another; preserve current product behavior; stop rather than repair any mismatch; keep local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.7, CI, publication, and any repair use different contracts.

Stop conditions: evidence reveals a product, authentication, cache, entity-isolation, or PWA defect requiring repair; a product or UX decision is needed; protected data, credentials, real databases, production/demo, or external networking becomes necessary; scope expands; verification changes the plan; cleanup or command-center health fails; or a preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; full `.venv/bin/python scripts/mobile_drawer_browser_test.py`; exact assertions for Tasks 1P.6.1-1P.6.4; denied non-localhost traffic; zero unexpected browser/page errors; exact temporary cleanup; relevant Python compilation; JSON validation; `git diff --check`; dashboard refresh, health, generated-state and rendered-dashboard inspection; exact worktree scope; and all preserved files.

Dashboard closeout: show 4BD active with Task 1P.6.1 current, Codex owner, exact boundaries, verification, and next report point before implementation. After verification, mark each included task and 4BD done only if all checks pass; otherwise record a safe stop without repairing. Refresh, health-check, and inspect the rendered dashboard.

Report point: return existing versus newly added coverage, exact findings, changed paths, verification and cleanup, local durability, preserved exclusions, whether `P3-3J-C01` and Task 1P.6 can close, and the separately gated repair or 4BD-R publication decision.

Suggested next work block: 4BD-R exact-scope durability/publication if separately authorized; if publication is parked, propose 4BE for Task 1P.7.

Result: the maintained isolated-browser runner now explicitly proves the exact manifest and icon contract, root worker scope and static-only cache, identical generic cross-entity offline navigation after Personal/BFM/Luxe Legacy visits, configured-auth full-page/HTMX/JSON/exempt/safe-return/sign-in boundaries, absence of a client-side digest, and exact authenticated/no-password `/k/` Personal/Luxe Legacy fields with BFM exclusion. Baseline and final full smoke and browser suites, compilation, denied networking, expected-error scoping, exact cleanup, JSON, whitespace, dashboard refresh/health/rendered inspection, exact worktree scope, and preserved-file checks pass. No product mismatch was found and product source did not change. Tasks 1P.6.1-1P.6.4, Task 1P.6, and `P3-3J-C01` are complete locally. Evidence: `command-center/logs/2026-07-24-installed-pwa-browser-boundary-coverage-4bd.md`.

### Confirmed Work Block 4BC: Real Plaid CSP Runtime Checkpoint

Status: done locally and uncommitted; confirmed and completed on 2026-07-24.

Parent task: Phase 4 Task 1P.4.4, limited to its separately gated real Plaid Link validation slice.

Included: record 4BC as active; verify exact deployed 4BB source and credential-free production health; use the existing authenticated Chrome session and currently selected entity without switching; inspect only the CSP, initializer, console, and network state of production `/data-sources/` and `/plaid/`; create exactly one real Link token from each entry path; open and close each Plaid Link surface before institution selection; verify one configured Plaid environment, fresh nonce-bearing policies, and no unexpected violation; and close Runway OS with sanitized evidence.

Excluded: Tasks 1P.6-1P.7; broader Task 2 regression; Task 3 CI; Task 4 publication; application, maintained-test, dependency, configuration, policy, authentication, CSRF, financial, database, category, PWA, workflow, or Fly changes; credentials, password or OTP handling, institution selection, account login, public-token exchange, account connection, sync, disconnect, toggle, rename, or other account mutation; protected detail; screenshots; response bodies; real database or upload mutation; downstream access or writes; commit, push, PR, merge, deployment, workflow action, non-automatic Fly action, broader recovery, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: both released entry paths exercise the same production CSP exception, exact Plaid initializer, Link frame, selected-environment origin, sanitized browser evidence, and stop boundary. They produce one coherent result: whether the real third-party runtime starts under the released policy without reaching account connection.

Owner and recommended agent: Codex Desktop in the current task after Ryan's explicit protected/live authorization. Codex owns exact browser instrumentation, evidence minimization, stop decisions, Runway OS currency, and final intake. Ryan owns manual authentication if required and every institution-selection, account, policy, repair, protected-data, or expansion decision.

Runner path: make the confirmed block active in Runway OS; refresh, health-check, and inspect the rendered dashboard; verify exact deployed source and credential-free health; use the existing authenticated Chrome session; inspect each entry document without recording page content; create one Link token, open Link, verify the frame and browser policy state, and close before institution selection; prove no exchange or mutation endpoint occurred; then save sanitized evidence and close locally.

Expected surfaces: `command-center/now.md`; `command-center/roadmap.md`; `command-center/decisions.md`; `command-center/state.json`; generated `command-center/index.html`; `command-center/csp-compatibility-contract.md` if the checkpoint changes its status note; and one sanitized 4BC evidence log. Production `/data-sources/`, `/plaid/`, `/health`, the exact Plaid initializer, and browser console/network state are read or narrowly exercised without product-source edits.

Defaults: use the current entity without switching; use the existing Chrome authentication state; pause for Ryan to authenticate manually if needed; do not request, read, type, or retain credentials; do not inspect or report institution, account, transaction, payroll, balance, or row-level detail; do not take screenshots or retain response bodies; record only route, status, policy shape, nonce presence/freshness, permitted hostnames, expected Link-token calls, Link open/close, and sanitized errors; keep local-only and uncommitted; stop rather than repair on failure.

Blocking questions: none. Ryan's confirmation authorizes the exact authenticated production reads, two Link-token requests, and two open-then-close Link checks above.

Expansion candidates: none. Tasks 1P.6-1P.7, broader regression, CI, policy repair, and publication use different risk and verification paths.

Stop conditions: authentication is missing or requires Codex to handle a password, OTP, or credential; Link reaches institution selection or account login; any exchange-token, sync, disconnect, account, database, downstream, workflow, or Fly mutation appears; a CSP violation, initializer/frame failure, unexpected external origin, sensitive browser output, or protected-detail capture becomes necessary; repair requires policy or product change; deployed source differs from the verified release; command-center, scope, or preserved-file verification fails; or the work expands beyond 4BC.

Verification: exact deployed 4BB source and credential-free `/health`; fresh nonce-bearing Plaid policy on both production entry documents with only one configured environment; Link frame opens and closes on each path without unexpected CSP violations or browser errors; exactly two Link-token POSTs and no exchange, sync, disconnect, or mutation endpoint; JSON validation; `git diff --check`; dashboard refresh, health, generated-state inspection, and rendered-dashboard inspection; exact worktree scope; and all three preserved untracked files.

Dashboard closeout: first show 4BC active with Task 1P.4.4 current, Codex owner, exact stop conditions, verification, and next report point. After the live checkpoint, record pass or safe stop, save sanitized evidence, make the next separate gate explicit, align human-readable sources and `state.json`, refresh, health-check, and inspect the rendered dashboard.

Report point: return pass or stop by entry path; sanitized policy, initializer, console, and network findings; exact expected live requests; confirmation that no token exchange or account mutation occurred; changed command-center paths; local durability and preserved exclusions; and the next separate decision.

Suggested next work block: if 4BC passes, propose 4BD for Task 1P.6 installed-PWA and browser-boundary regression coverage. If 4BC stops or fails, propose a separate local-only diagnosis block rather than widening policy during 4BC.

Result: exact Fly Deploy run `30116007970` remained successful for source SHA `6c2a2800ec887ea3c2bf8fb254214dbd0630f55f`, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. After Ryan authenticated manually, both production entry documents returned HTTP 200 with exactly one initializer, fresh nonces matched by the three intended policy directives, the Plaid frame origin, and only the configured production API origin. Each real Link opened to its pre-institution consent surface and closed successfully before institution selection. The complete session contained exactly the two authorized Link-token POSTs, no exchange or mutation endpoint, no failed response, and zero product or CSP errors. Three identical Chrome extension message-channel entries were classified as control noise. No screenshot, response body, protected detail, institution selection, account login, token exchange, account/financial mutation, product repair, or policy widening occurred. Evidence: `command-center/logs/2026-07-24-real-plaid-csp-runtime-checkpoint-4bc.md`.

Next separate decision: propose 4BD for Task 1P.6 installed-PWA and browser-boundary regression coverage. It is not authorized by 4BC.

### Confirmed Work Block 4BB-R: Final CSP Enforcement Durability And Release

Status: done; directly authorized and completed on 2026-07-24

Parent task: Phase 4 Task 4 only for the exact Task 1P.4.4 / 4BB durability and automatic-release slice.

Included: record 4BB-R as active; rerun full smoke and configured-auth/no-password isolated-browser coverage; validate syntax, JSON, whitespace, dashboard health/generated/rendered state, exact worktree scope, and all preserved files; stage explicitly only the intended verified 4BB source, maintained tests, documentation, evidence, and Runway OS paths; create one source commit on `codex/csp-header-enforcement`; cleanly fast-forward local `main`; push `main` directly and without force; observe only the resulting automatic Fly deployment; verify its exact source SHA and credential-free production `/health`; then commit and push only the sanitized Runway OS release closeout with `[skip actions]`.

Excluded: proposed 4BC real Plaid Link checkpoint; credentials; Plaid link, sync, disconnect, or account mutation; protected data; real databases/uploads; authenticated production/demo pages; manual workflow actions; workflow edits; non-automatic Fly mutation; downstream access or writes; PR creation; force push; product changes beyond the verified 4BB set; broader Task 1P.6-1P.7, Task 2, Task 3, or Task 4 work; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: 4BB is one fully verified security-header release unit. Ryan's direct publication instruction authorizes its source durability and the automatic deployment that a `main` push triggers. Real Plaid remains a different protected checkpoint and is not inferred from publication authority.

Owner and runner: Codex Desktop owns explicit-path staging, commit, clean main fast-forward, non-force push, automatic-run observation, credential-free health, exact-SHA proof, sanitized closeout, dashboard currency, and preserved-file control. Ryan owns real Plaid, credentials, protected access, policy expansion, broader recovery, and every new mutation.

Stop conditions: any unexpected or sensitive path; changed source after verification; failed smoke/browser/syntax/JSON/whitespace/dashboard health; preserved-file overlap; local or remote `main` divergence; a non-fast-forward requirement; push rejection; deployment failure requiring mutation; credential-free health failure; exact source-SHA mismatch; or recovery beyond clean fast-forward and read-only diagnosis.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment run/job and exact-SHA result, credential-free health, local/remote alignment, real-Plaid omission, preserved exclusions, and the next separately gated action.

Result: exact 20-path source commit `6c2a2800ec887ea3c2bf8fb254214dbd0630f55f` is durable on `origin/main`. Automatic Fly Deploy run `30116007970` and deploy job `89556739589` passed every reported step for that exact SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Full release verification, exact staging and ancestry, non-force push, remote alignment, and preserved-file checks passed. No real Plaid, credential, protected data, authenticated production page, manual workflow, non-automatic Fly, downstream, PR, force push, broader recovery, or preserved-file action occurred. Evidence: `command-center/logs/2026-07-24-final-csp-enforcement-release-4bb-r.md`.

### Confirmed Work Block 4BB: Final CSP Enforcement And Local Proof

Status: done and locally verified on 2026-07-24; publication and real Plaid remain unauthorized

Parent tasks: Phase 4 Task 1P.4.4 plus only its focused Task 2 CSP regression slice.

Included: record 4BB as active before product work; create `codex/csp-header-enforcement` from current `origin/main`; attach the exact strict policy to every `text/html` response including directly navigable fragments; select the narrow Plaid variant only for a successfully rendered `plaid.html` or `data_sources.html` Link response; generate one unpredictable base64 nonce from at least 128 CSPRNG bits per successful Link response; apply it only to both exact initializer tags and the matching `script-src`, `style-src`, and `style-src-elem` directives; retain the rendered-Link-only `style-src-attr 'unsafe-inline'`, exact CDN frame, and one validated sandbox-or-production connect origin; refresh the service-worker cache and attach strict CSP to its last-resort synthetic HTML; add maintained request and isolated-browser enforcement proof; reconcile the contract, issue, README if maintained behavior changes, evidence, and Runway OS; and close `P3-3J-06` locally only if every required check passes.

Excluded: Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; real Plaid Link; credentials; protected data; real databases; retained uploads; production/demo inspection; non-localhost product access; GitHub durability; commit, push, PR, merge, publication, deployment, workflows, Fly, downstream access or writes; authentication, CSRF, financial, category, database, dependency, or broader PWA redesign; CSP reporting, Trusted Types, request upgrading, broader origins, both Plaid environments, or relaxed inline-code policy; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the response header, successful-render Plaid marker, request-scoped nonce, exact initializer attributes, service-worker cache refresh, and request/browser proof form one atomic security boundary. Splitting enforcement from proof would create an incompletely verified policy. Real Plaid, publication, broader installed-PWA coverage, CI, and financial read-model coverage introduce different risk or verification classes and depend on the local enforcement result.

Expansion candidates and questions: none. Task 1P.6's exact service-worker/offline overlap is already included where Task 1P.4.4 requires it; its remaining broader browser-boundary coverage, Task 1P.7, Task 3, and Task 4 stay separate.

Owner and recommended agent: Codex Desktop in the current task without delegation or another second opinion. The sensitive retrofit couples Flask response behavior, template nonce plumbing, service-worker semantics, a maintained isolated-browser matrix, exact cleanup, evidence, and Runway OS stewardship. The exact policy already received an independent `claude-fable-5` maximum-effort review. Ryan owns every scope or policy change, real-Plaid checkpoint, publication, protected, and live decision.

Runner path: current Codex task on `codex/csp-header-enforcement`; make 4BB active in Runway OS; run baseline full synthetic and isolated-browser verification; implement the frozen policy, nonce, successful-response marker, and service-worker refresh; add focused maintained proof; run the complete final matrix; inspect rendered behavior and dashboard state; then close locally without commit or publication.

Expected surfaces: CSP/header support in `web/__init__.py` and possibly one focused `web/` helper; successful-Link response marking in `web/routes/plaid.py` and `web/routes/data_sources.py`; nonce attributes in `web/templates/plaid.html` and `web/templates/data_sources.html`; `web/static/sw.js`; focused additions to `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py`; README only if the maintained security surface changes; `command-center/csp-compatibility-contract.md`; issue disposition; one sanitized 4BB evidence log; `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`.

Defaults: preserve the exact frozen core and Plaid policies; apply strict CSP to every `text/html` response but not static, worker, manifest, or JSON responses; mark the Plaid variant only after successful rendering; keep redirects, authentication responses, and error documents strict; generate a fresh nonce once per successful Link response; preserve the existing absent-`PLAID_ENV` sandbox default; make invalid configuration fail closed without broadening and stop if that requires a new product decision; mock the exact Plaid initializer; deny non-localhost traffic; use temporary synthetic all-entity databases and disposable browser state; preserve authentication, CSRF, no-store, entity, responsive, and static/offline-only worker behavior; keep durability local-only and uncommitted; preserve all three unrelated untracked files.

Stop conditions: compatibility requires widening the frozen policy, allowing both Plaid environments or another origin, changing authentication/CSRF/product/financial/database/dependency behavior, or broader service-worker/PWA redesign; a nonce or Plaid exception could leak to an error, redirect, or authentication response; real Plaid, credentials, protected data, real databases, retained uploads, production/demo, or non-localhost access becomes necessary; baseline or final verification materially changes the plan; exact cleanup, dashboard refresh, health, or preserved-file checks fail; or scope expands.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; baseline and final `.venv/bin/python scripts/mobile_drawer_browser_test.py`; focused exact-header and response-classification assertions for full pages, fragments, login/errors/offline/`/k/`, static, worker, manifest, and JSON; both Link templates, successful render, forced mid-render error, sandbox, production, absent, and invalid configuration; configured-auth and no-password isolated Chrome at desktop, phone, and exact 768px; representative full pages and repeated HTMX swaps; mocked Plaid open/exit; manifest and service-worker installation; upgrade from a cached headerless `/offline` response and cache-served strict-header proof; prohibited inline script, native handler, style attribute, eval, cross-origin fetch, frame, object, and form-target probes; denied networking; zero unexpected CSP violations, console/page errors, failed requests, dialogs, or temporary state; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh, health, generated-state inspection, and rendered-dashboard inspection; exact-path worktree review; and all preserved untracked files.

Dashboard closeout: before implementation, make 4BB current in `now.md`, `roadmap.md`, `decisions.md`, and `state.json`, refresh and health-check, and inspect the rendered dashboard. After complete verification, mark 4BB and Task 1P.4.4 done locally and close `P3-3J-06` only if every enforcement check passes; keep real Plaid, publication, and broader Task 1P.6 work separately gated; refresh, health-check, and inspect the final rendered dashboard; do not commit or publish.

Report point: return the exact strict and Plaid policies, response-classification and nonce design, service-worker/offline result, prohibited-probe results, changed paths, complete verification and cleanup, local branch/durability state, preserved exclusions, and separate real-Plaid and publication gates.

Suggested next work block: after 4BB closes cleanly, propose 4BC for a narrowly authorized real Plaid enforcement checkpoint. Only after that checkpoint passes should exact-scope 4BB-R durability and release be considered.

Result: the frozen strict policy now protects every HTML response; only successfully rendered Link documents receive a fresh response-scoped nonce and narrow environment-specific Plaid variant; service-worker v5 refreshes the offline cache and protects emergency HTML; maintained request and configured-auth/no-password isolated-browser proof passes with mocked Plaid, denied non-localhost traffic, prohibited-source enforcement, and exact cleanup. Enforcement also found and removed the last generated Short-Term Planning style seams without widening policy. `P3-3J-06` is locally resolved. Evidence: `command-center/logs/2026-07-24-final-csp-enforcement-4bb.md`.

### Confirmed Work Block 4BA-R: Exceptional Documents And Plaid CSP Policy Reconciliation Durability

Status: done; directly authorized and completed on 2026-07-24.

Result: exact nine-path source commit `8dfbc0f4c32d9b011db0e8f0eeb4b9bfa4081b09` is durable on `origin/main`. Exact scope, sensitive-addition, JSON, whitespace, dashboard, commit-parent, clean fast-forward, non-force push, remote-SHA, no-workflow-run, and preserved-file checks passed. `[skip actions]` produced no GitHub workflow run and no Fly deployment or production access occurred. No product, workflow, protected, credential, database, live Plaid, downstream, proposed 4BB, broader recovery, or preserved-file mutation occurred.

Parent task: Phase 4 Task 1P.4.3b-R plus only the authorized command-center durability slice.

Included: explicit staging of only the nine intended sanitized 4BA command-center paths; one `[skip actions]` source commit on `codex/csp-policy-reconciliation`; a clean fast-forward of local `main`; direct non-force push to `origin/main`; exact remote-SHA verification; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.4 implementation and proposed 4BB; Tasks 1P.6-1P.7; broader Task 2; Tasks 3-4 except this exact durability action; application/template/route/test/dependency/workflow/configuration changes; CSP headers, nonce plumbing, service-worker/manifest, authentication, credentials, protected data, real databases, retained uploads, live Plaid, production/demo/Fly access, downstream systems, PR creation, force push, broader recovery, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: 4BA produced only sanitized command-center policy, evidence, review, and Runway OS artifacts. One exact-path `[skip actions]` durability sequence makes them durable without triggering an unnecessary Fly deployment or crossing into Task 1P.4.4.

Owner and runner: Codex Desktop on `codex/csp-policy-reconciliation`, using explicit-path staging, clean local-main fast-forward, non-force direct push, remote verification, and a sanitized closeout.

Expected source paths: `command-center/csp-compatibility-contract.md`; `command-center/handoffs/second-opinion/2026-07-24-4ba-exceptional-documents-plaid-csp-policy-review.md`; `command-center/logs/2026-07-24-exceptional-document-plaid-csp-policy-reconciliation-4ba.md`; `command-center/logs/second-opinion/2026-07-24-4ba-fable-5-max-response.md`; `command-center/decisions.md`; `command-center/now.md`; `command-center/roadmap.md`; `command-center/state.json`; and generated `command-center/index.html`.

Stop conditions: an unexpected or sensitive path; failed JSON, whitespace, dashboard, scope, or preserved-file check; local/remote `main` divergence; push rejection; any workflow run despite `[skip actions]`; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed/staged/committed paths; high-confidence sensitive-addition scan; JSON; `git diff --check`; dashboard refresh, health, generated-state and rendered inspection; commit contents; clean ancestry; exact `origin/main` SHA; absence of a deploy-triggering workflow run; final tracked alignment; and all three preserved untracked files. Full product smoke remains intentionally skipped because the release contains no product/runtime change.

Report point: return the source and closeout commit SHAs, nine published source paths, exact remote alignment, `[skip actions]`/no-deployment result, final worktree state, preserved exclusions, and separately gated proposed 4BB.

Suggested next work block: 4BB for Task 1P.4.4 only after separate Ryan confirmation.

### Confirmed Work Block 4BA: Exceptional Documents And Plaid CSP Policy Reconciliation

Status: done; confirmed and completed locally on 2026-07-24.

Result: tracked-source and official-documentation reconciliation is complete in the CSP contract and sanitized 4BA evidence log. Claude CLI `claude-fable-5` at `max` effort completed the read-only review in 858 seconds with “approve with corrections,” no critical finding, and no policy-string change. Accepted corrections protect every `text/html` response including direct fragment navigation; bind the Plaid marker only to successful Link responses and test mid-render failure; require at least 128 CSPRNG bits/base64 nonce encoding; couple the service-worker update to cached `/offline` refresh; and retain real Link as a separately authorized live checkpoint. Optional header, worker, SVG, reporting, deprecated-header, Trusted Types, and cross-origin fetch-wrapper observations are parked. Contract/evidence, JSON, whitespace, dashboard, scope, and preserved-file checks pass; no product/runtime or external mutation occurred.

Parent tasks: Phase 4 Tasks 1P.4.3b.1-1P.4.3b.2 only.

Included: reconcile strict login, offline/error, standalone `/k/`, seven maintained local data-image, root service-worker, same-origin manifest/icon, data-free offline-cache, and HTML-versus-static response inputs; reconcile both exact Plaid Link initializer tags, the CDN frame, one validated sandbox-or-production connect origin, request-scoped initializer and Plaid-injected-style nonce requirements, and the Plaid-route-only `style-src-attr 'unsafe-inline'` exception; update the repo-backed CSP contract and one sanitized evidence log; obtain a read-only second opinion on the finished artifact when the explicitly selected Claude CLI model and effort are available; disposition the critique; and close Runway OS locally.

Excluded: Task 1P.4.4, Tasks 1P.6-1P.7, the remainder of Task 2, Tasks 3-4, application/template/route/maintained-test/dependency/configuration changes, CSP headers or nonce plumbing, service-worker or manifest behavior changes, authentication, CSRF, product behavior, credentials, protected data, real databases, retained uploads, live Plaid or non-public documentation, production/demo inspection, GitHub durability, publication, deployment, workflows, downstream access or writes, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: both tasks produce one exact policy contract, one official-documentation and tracked-source model, one sanitized evidence packet, one independent critique, and one handoff to Task 1P.4.4. Header enforcement, installed-PWA regression, publication, and live action have different risk and verification classes.

Owner and recommended agent: Codex Desktop in the current task, with a read-only Claude CLI second opinion after the repo-backed policy artifact is complete. Codex owns source and documentation reconciliation, contract and evidence changes, review intake, dashboard currency, scope control, and final disposition. Ryan owns the Claude model/effort selection, every policy or scope expansion, Task 1P.4.4 authorization, publication, and live action.

Runner path: work locally on `codex/csp-policy-reconciliation`; make the confirmed block active in Runway OS; reconcile the policy contract and evidence; create the review packet only after the Claude CLI model and effort are explicitly selected; run the bundled read-only review; adopt, reject, or park findings without expanding scope; then close locally and leave Task 1P.4.4 separately gated.

Expected surfaces: `command-center/csp-compatibility-contract.md`; one sanitized 4BA evidence log; a second-opinion prompt and response under `command-center/handoffs/second-opinion/` and `command-center/logs/second-opinion/` after reviewer settings are selected; `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`. No `web/`, `core/`, `scripts/`, workflow, dependency, or runtime file should change.

Defaults: preserve the strict core policy and verified zero application-owned inline execution/style inventory; retain `img-src 'self' data:` for seven maintained local SVG data images; retain same-origin worker and manifest inputs; preserve both exact Plaid initializer tags; allow exactly one validated sandbox-or-production connect origin per response; confine Plaid nonce and style-attribute requirements to Link documents; use only public official documentation and tracked source; keep durability local-only and uncommitted; and skip full smoke because no application behavior should change.

Blocking question before the second-opinion step: select the Claude CLI model and effort. The recommended setting is `--model opus --effort max`; no review prompt may be created or run until Ryan explicitly selects both values.

Expansion candidates: none. Task 1P.4.4 changes security headers and nonce plumbing; Task 1P.6 consumes broader installed-PWA/browser regression; both require separate work blocks.

Stop conditions: the exact policy requires a product or UX decision; official requirements cannot be reconciled without a broader Plaid or inline-code exception; both Plaid environments would need allowlisting; live Plaid, credentials, protected data, non-public sources, or non-localhost product access becomes necessary; work crosses into product code, headers, nonce plumbing, service-worker/manifest behavior, authentication, Task 1P.4.4, or later tasks; independent review materially changes scope or definition of done; verification or dashboard health fails; scope expands; or a preserved untracked file overlaps.

Verification: exact strict-document, PWA-resource, and HTML/static response-family matrix; seven local data images; root service worker; manifest/icons; offline caching; both exact Plaid initializer tags; tracked sandbox/production validation; exact core and Plaid policy variants plus Task 1P.4.4 handoff; no product, maintained-test, dependency, configuration, or runtime diff; JSON validation; `git diff --check`; dashboard refresh, health, generated-state inspection, and rendered-dashboard inspection; exact-path worktree review; and preserved untracked files. Full application smoke is intentionally skipped because 4BA must not change application behavior.

Dashboard closeout: after policy reconciliation and review intake, mark 4BA and Tasks 1P.4.3b.1-1P.4.3b.2 done; make Task 1P.4.4 the next separate Ryan decision; align human-readable sources and `state.json`; refresh, health-check, and inspect the rendered dashboard; and keep every durability, publication, protected, and live step separately gated.

Report point: return the exact core and Plaid policy variants, resolved contract drift, route/environment/nonce decisions, reviewer findings and dispositions, changed command-center paths, verification results, local branch and durability status, preserved exclusions, and the separate Task 1P.4.4 gate.

Suggested next work block: 4BB for Task 1P.4.4 final CSP header enforcement and maintained synthetic/isolated-browser proof, only after separate Ryan confirmation.

### Confirmed Work Block 4AZ-R: Standalone Document Style Compatibility Release

Status: done; confirmed and completed on 2026-07-24.

Parent tasks: Phase 4 Task 1P.4.3a.8-R plus only the authorized Task 4 release slice.

Included: explicit-path staging and commit of the exact verified 4AZ application templates, maintained CSS, smoke/browser tests, CSP contract, evidence, and Runway OS paths on `codex/csp-standalone-styles`; direct non-force push of that exact source commit to `origin/main`; read-only observation of the resulting automatic Fly deployment; exact source-SHA verification; credential-free production `/health`; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.3b, Task 1P.4.4, Tasks 1P.6-1P.7, the remainder of Task 2, Tasks 3 and every unapproved Task 4 action; new application, runtime, style, route, authentication, CSRF, service-worker, manifest, CSP-header/nonce/exception/enforcement, Plaid-policy, financial, database, product, or dependency changes; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the verified 4AZ source set, direct-main durability, automatic release observation, credential-free health, and sanitized Runway OS closeout form one controlled release boundary. Task 1P.4.3b and final CSP enforcement require different policy and verification decisions.

Owner and recommended agent: Codex Desktop in the current task. Codex owns exact-path staging, source commit, direct non-force push, read-only automatic-deployment observation, credential-free health, sanitized closeout, dashboard currency, and final intake. Ryan owns every expansion, manual workflow or Fly action, protected access, broader recovery, and later task.

Runner path: reverify the exact local result; stage only authorized paths; create one source commit on `codex/csp-standalone-styles`; push directly to `origin/main`; observe only the automatic Fly deployment; verify exact SHA and credential-free `/health`; then commit and push only the sanitized `[skip actions]` closeout.

Expected surfaces: the exact 16-path 4AZ application/template, maintained CSS/test, CSP-contract, evidence, and Runway OS source set for the source commit; then only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, and one sanitized 4AZ-R release evidence log for closeout.

Defaults: preserve exact 0/0/0/0 style inventory, the full synthetic and configured-auth/no-password browser proof, offline asset behavior, and all three unrelated untracked files; use explicit-path staging; no PR, force push, manual workflow action, workflow edit, non-automatic Fly mutation, or authenticated production access; use `[skip actions]` only for the sanitized command-center closeout.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3b and final CSP enforcement have separate policy and risk boundaries.

Stop conditions: an unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, broader recovery, or any scope expansion.

Verification: exact changed and staged paths; full smoke and configured-auth/no-password isolated browser; relevant Python and JavaScript syntax; JSON; whitespace; dashboard refresh/health/generated-state inspection; commit contents and ancestry; exact remote SHA; automatic workflow and deploy-job result; credential-free production health; final branch/remote alignment; and all preserved untracked files.

Dashboard closeout: after release verification, mark 4AZ-R and Task 1P.4.3a.8-R complete; preserve Task 1P.4.3b as the next separately gated planning decision; align source files and `state.json`; refresh and health-check; inspect generated state; commit only the sanitized closeout with `[skip actions]`; push directly to `main`; and verify no second workflow run exists for the closeout.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and separately gated Task 1P.4.3b.

Result: exact 16-path source commit `6017d2262d303f93fd70f4c790f32455d5022df1` is durable on `origin/main`. Automatic Fly Deploy run `30105710374` and deploy job `89522491511` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact changed and staged sets, maintained smoke, configured-auth/no-password isolated browser, Python and JavaScript syntax, JSON, whitespace, dashboard health, commit contents, ancestry, remote alignment, automatic release, production health, and all preserved-file checks passed. GitHub emitted a non-failing Node 20 deprecation annotation for `actions/checkout@v4`; workflow maintenance remains outside scope. No PR, force push, credential, protected data, real database, retained upload, authenticated production page, manual workflow action, workflow edit, non-automatic Fly mutation, downstream access/write, Task 1P.4.3b work, broader recovery, or preserved-file mutation occurred.

Target durability: source and active-state changes are on `main`; the verified command-center closeout is published separately with `[skip actions]` to avoid a second automatic deployment.

Suggested next work block: separately plan Task 1P.4.3b exceptional-document and Plaid policy reconciliation.

### Confirmed Work Block 4AZ: Standalone Document Style Compatibility

Status: complete, verified, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.8 plus only its focused Task 2 regression slice.

Included: remove the five inline style blocks in `auth/login.html`, `offline.html`, and `errors/403.html`, `errors/404.html`, and `errors/500.html`; remove the three bounded percentage style attributes in `kristine.html`; preserve login, CSRF, safe-return, early theme, data-free error/offline rendering, retry, exact statuses and no exception leakage, configured-auth and no-password behavior, Personal/Luxe Legacy scope, BFM exclusion, and responsive layout; add focused source, rendered, request, isolated-browser, offline-asset, and visual proof; reconcile the final application-owned style inventory from 5/3/0/0 to 0/0/0/0; and close Runway OS locally after verification.

Excluded: Task 1P.4.3b, Task 1P.4.4, Tasks 1P.6-1P.7, the remainder of Task 2, Tasks 3-4, CSP headers/nonces/exception policy/enforcement, Plaid policy, service-worker or manifest behavior, route, authentication, CSRF, product, financial, database, dependency, protected-data, credential, external/live, GitHub durability, publication, deployment, workflow, or downstream changes; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: login, offline/errors, and standalone `/k/` are the final application-owned style family, share the exact standalone execution foundation completed through 4AR-R, and use one source, rendered, authentication, error-status, offline-safe, responsive, and visual verification path. Plaid exception policy and final CSP enforcement depend on this block reaching zero and remain separate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns the exact local implementation, synthetic/request/browser proof, rendered visual inspection, cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, service-worker or CSP-policy decision, protected action, publication, deployment, and live action.

Runner path: write and verify active command-center state, create `codex/csp-standalone-styles` from current `origin/main`, implement the exact local slice, run focused and full proof, inspect rendered login/offline/error/`/k/` documents, and close locally before any durability decision.

Expected surfaces: `web/templates/auth/login.html`; `web/templates/offline.html`; `web/templates/errors/403.html`; `web/templates/errors/404.html`; `web/templates/errors/500.html`; `web/templates/kristine.html`; `web/static/style.css`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. `web/static/standalone-documents.js`, `web/static/kristine.js`, `web/static/sw.js`, routes, and authentication code are verification surfaces with no planned edits.

Defaults: preserve appearance rather than redesigning; use scoped document-family classes in the already precached `style.css` so the cached offline fallback stays styled without a service-worker mutation; retain the blocking standalone theme initializer and deferred `/k/` controller unchanged; use the existing bounded percentage classes for integer bars; use temporary synthetic all-entity data, both authentication modes, localhost-only disposable browser state, denied non-localhost traffic, zero unexpected errors, and exact cleanup; preserve all three unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3b introduces third-party and exceptional-document policy, Task 1P.4.4 introduces header enforcement, and publication has a different risk and verification class.

Stop conditions: preserving offline styling requires a service-worker change; parity requires a product/design decision or inline-style exception; work crosses into authentication, CSRF, routes, CSP policy/enforcement, Plaid, service worker/manifest, financial, database, protected/live, or later-task behavior; phone, exact 768px, or desktop behavior is ambiguous; verification changes the plan; cleanup or command-center health fails; scope expands; or a preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered zero-style proof with exact final 0/0/0/0 inventory; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across login, offline/retry, exact 403/404/500 status and non-leakage, `/k/` authentication/entity/drilldown behavior, phone/exact-768/desktop layout, denied networking, zero unexpected errors, and cleanup; actual rendered visual inspection; existing service-worker precache retention of `style.css`; relevant Python/JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh/health/generated-state inspection; exact scope; and all preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AZ, Task 1P.4.3a.8, and its focused Task 2 slice complete locally; make separate 4AZ-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated seams and replacement classes, final inventory, authentication/error/offline/browser and visual proof, cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AZ-R gate.

Result: 4AZ moved the login document and offline/403/404/500 message-family styling into scoped maintained classes in the already precached `web/static/style.css`, replaced all three standalone `/k/` percentage attributes with the existing bounded percentage-class contract, and reconciled the exact application-owned style inventory to 0/0/0/0. Baseline and final full smoke, focused source/rendered/request/offline-asset assertions, Python and JavaScript syntax, JSON, whitespace, and configured-auth/no-password isolated Chrome passed. Rendered phone, exact-768, and desktop inspection covered login, offline, 403, 500, and `/k/` with preserved layout, exact status/no leakage, authentication/entity boundaries, no product inline styles, no overflow, denied non-localhost traffic, zero unexpected errors, and exact disposable-state cleanup. No service-worker, manifest, route, authentication, CSRF, CSP policy/enforcement, protected/live, GitHub, publication, deployment, downstream, or preserved-file mutation occurred.

Target durability: complete locally on `codex/csp-standalone-styles` and intentionally uncommitted; 4AZ-R requires separate planning and confirmation.

Suggested next work block: separately decide whether to authorize exact-scope 4AZ-R durability and release. If publication is not desired, Task 1P.4.3b remains the next planning decision.

### Confirmed Work Block 4AY: Data Sources And Connected Accounts Style Compatibility

Status: complete, verified, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.7 plus only its focused Task 2 regression slice.

Included: remove one inline style block and 34 template style attributes from `data_sources.html` and `plaid.html`; preserve vendor workflows, conditional account states and tables, both exact Plaid initializer tags, form-versus-JSON exchange contracts, entity isolation, and responsive behavior; add focused maintained source, conditional-rendered, and configured-auth/no-password isolated-browser proof; reconcile the exact residual CSP style inventory from 6/37/0/0 to 5/3/0/0; and close Runway OS locally after verification.

Excluded: Task 1P.4.3a.8, Task 1P.4.3b, Task 1P.4.4, Tasks 1P.6-1P.7, the remainder of Task 2, Tasks 3-4, the known empty-vendor aggregation issue, route/query, financial, database, product, authentication, CSRF, dependency, CSP-header/nonce/exception/enforcement, real Plaid, protected data, credentials, external/live access, GitHub durability, publication, deployment, workflow, downstream, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: Data Sources and Connected Accounts form one Plaid-entry presentation surface, share the existing local-controller and mocked-Link harness, and use one source, rendered-state, and browser verification path. Standalone documents have authentication and offline/error behavior; Plaid exception policy and CSP enforcement require different decisions and proof; publication remains a separate side-effect gate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns the exact local implementation, synthetic and browser proof, cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, Plaid-policy decision, protected action, publication, and live action.

Runner path: write and verify active command-center state, create `codex/csp-plaid-entry-styles` from the current `origin/main` state, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/data_sources.html`; `web/templates/plaid.html`; `web/static/style.css`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. `web/static/data-sources.js` and `web/static/plaid.js` are verification surfaces with no planned edits. No route change is expected.

Defaults: preserve appearance and behavior rather than redesigning; use page-specific semantic classes and existing utilities where suitable; retain both exact Plaid initializer tags unchanged; use fake Plaid configuration, mocked Plaid functions, temporary synthetic all-entity data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost traffic, zero unexpected browser/page errors, and exact cleanup; preserve all three unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.8 introduces authentication and offline/error document behavior; Task 1P.4.3b introduces third-party policy; every later task has a different risk or verification class.

Stop conditions: parity requires a product/design decision or inline-style exception; work would cross into Plaid policy, CSP enforcement, route/query, database, authentication, CSRF, financial, product, or later-task behavior; real Plaid, credentials, protected data, or non-localhost access becomes necessary; desktop, phone, or exact 768px behavior becomes ambiguous; verification changes the plan; cleanup or command-center health fails; scope expands; or a preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered zero-style proof across relevant conditional states; exact retention of both Plaid initializer tags and both exchange formats; final aggregate inventory of five style blocks, three template style attributes, zero generated attributes, and zero runtime writes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage at desktop, phone, and exact 768px for vendor selection/counting, confirmations, account states/tables, Link open/success/exit/error wiring, responsive overflow, entity isolation, denied networking, zero unexpected browser/page errors, and cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and all preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AY, Task 1P.4.3a.7, and its focused Task 2 slice done locally; make separate 4AY-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated seams and replacement classes, final 5/3/0/0 inventory, conditional/rendered/browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AY-R gate.

Suggested next work block: separately decide whether to authorize exact-scope 4AY-R durability and release. If publication is not desired, Task 1P.4.3a.8 remains the next planning decision.

Result: the one Data Sources inline style block and all 34 Data Sources/Connected Accounts template style attributes are removed through maintained page-specific semantic classes and existing utilities. Both exact Plaid initializer tags, page-owned controllers, vendor behavior, conditional account states and tables, mocked Link behavior, form-versus-JSON exchange contracts, entity isolation, and responsive layout remain intact. Baseline and final full smoke plus configured-auth/no-password isolated Chrome across all entities at phone, exact 768px, and desktop passed with denied networking, zero unexpected browser/page errors, and exact cleanup. The residual inventory is exactly 5/3/0/0. No commit, push, publication, deployment, route/query repair, CSP policy/enforcement, real Plaid, protected/live access, downstream, destructive, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-24-data-sources-connected-accounts-style-compatibility-4ay.md`.

### Confirmed Work Block 4AY-R: Data Sources And Connected Accounts Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.7-R plus the authorized Task 4 publication slice.

Included: explicitly stage and commit the exact verified 4AY application templates, maintained CSS, smoke/browser tests, CSP contract, evidence, and Runway OS paths on `codex/csp-plaid-entry-styles`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify its exact source SHA and credential-free production `/health`; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.3a.8 and every later task; any new mutation beyond verified 4AY; route/query repair; credentials; protected data; real databases; retained uploads; authenticated production pages; real Plaid; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the verified 4AY source set, direct-main push, automatic release observation, credential-free health verification, and sanitized Runway OS closeout form one controlled durability boundary. Task 1P.4.3a.8, Plaid policy, CSP enforcement, and route repair remain separate implementation and decision surfaces.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path staging, commit and ancestry verification, direct-main push, read-only automatic-deployment observation, credential-free health, sanitized closeout, and final intake. Ryan owns every expansion, manual live action, and broader recovery.

Runner path: current Codex task on `codex/csp-plaid-entry-styles`; exact source commit; clean fast-forward of local `main`; direct non-force `origin/main` push; automatic Fly observation; credential-free health; then one command-center-only `[skip actions]` closeout.

Expected surfaces: exact twelve-path 4AY source set for the source commit; then only `command-center/now.md`, `command-center/roadmap.md`, `command-center/decisions.md`, `command-center/state.json`, generated `command-center/index.html`, and one sanitized 4AY-R release evidence log for closeout.

Defaults: explicit-path staging only; no PR, force push, manual workflow action, or non-automatic Fly mutation; preserve exact 5/3/0/0 inventory, both Plaid initializer tags, dual-auth all-entity responsive proof, and all three unrelated untracked files; observe only automatic deployment and credential-free health; use `[skip actions]` only for sanitized closeout.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.8, Plaid policy, CSP enforcement, and the known route defect have different implementation and risk boundaries.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, recovery beyond clean fast-forward/read-only diagnosis, or scope expansion.

Verification: exact changed and staged paths; full smoke and configured-auth/no-password isolated Chrome evidence; relevant Python, JavaScript, and JSON syntax; whitespace; dashboard refresh, health, and generated-state inspection; commit contents; clean fast-forward; ancestry; exact remote SHA; automatic Fly workflow and deploy-job result; credential-free production health; final local/remote alignment; and all preserved untracked files.

Dashboard closeout: mark 4AY-R and Task 1P.4.3a.7-R complete; preserve Task 1P.4.3a.8 as the next separately gated planning decision; align human-readable sources and `state.json`; refresh and health-check; inspect generated state; commit only the sanitized command-center closeout with `[skip actions]`; push directly to `main`; and verify no second workflow run exists for the skip-actions commit.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health result, final local/remote alignment, preserved exclusions, and separately gated Task 1P.4.3a.8.

Suggested next work block: separately decide whether to plan and confirm Task 1P.4.3a.8 for login, offline/error, and standalone `/k/` style compatibility.

Result: exact 12-path source commit `9daeb8f4508a3fab2b63ea7304903d4cc10adcbb` is durable on `origin/main`. Automatic Fly Deploy run `30101833858` and deploy job `89509540237` passed for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Full maintained synthetic and dual-auth responsive browser proof, syntax, JSON, whitespace, command-center health, exact scope, ancestry, remote alignment, and preserved-file checks passed. No PR, force push, manual workflow action, workflow edit, non-automatic Fly mutation, protected access, real Plaid, later-task implementation, broader recovery, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-24-data-sources-connected-accounts-style-compatibility-release-4ay-r.md`.

### Confirmed Work Block 4AX: Subscriptions And Payroll Style Compatibility

Status: complete, verified, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.6 plus only its focused Task 2 regression slice.

Included: remove the three baseline-counted Payroll template style attributes, one conditional new-role rendered style attribute, two route-generated Payroll spending-partial style attributes, and all five runtime style writes in the page-owned Subscriptions and Payroll controllers; preserve clipboard fallback, disclosure state, role colors, bounded spending bars, repeated period swaps, new-role visibility, dialogs, keyboard behavior, entity isolation, and the BFM-only Payroll boundary; reconcile the exact residual CSP style inventory; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.3a.7-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route contracts or queries beyond the included Payroll partial markup; financial calculations, databases, product behavior, authentication, CSRF, dependencies, CSP-header/nonce/exception/enforcement, Plaid, protected data, credentials, downstream systems, external/live access, GitHub, publication, deployment, workflows, `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log.

Why this grouping: the remaining Subscriptions and Payroll style seams share the existing extracted controllers, semantic state patterns, bounded percentage utilities, synthetic fixtures, and responsive browser harness. Data Sources/Plaid introduces third-party policy and exchange-contract boundaries; standalone documents introduce authentication and offline/error behavior; final CSP enforcement depends on every style cluster being complete.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and isolated-browser proof, exact cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product or policy decision, publication, protected access, live action, and broader recovery.

Runner path: write and verify active command-center state, create `codex/csp-subscriptions-payroll-styles`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/payroll.html`; `web/routes/payroll.py`; `web/static/subscriptions.js`; `web/static/payroll.js`; `web/static/style.css`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard.

Defaults: preserve appearance and behavior rather than redesigning; use a maintained off-screen class for the clipboard proxy, semantic state and ARIA plus `hidden` for disclosure and new-role visibility, finite existing role-color classes with the current fallback, and the existing bounded `u-pct-0` through `u-pct-100` contract for integer spending bars; use temporary synthetic all-entity data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost traffic, zero unexpected console/page errors, and exact cleanup; preserve all three unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.7 introduces Plaid and vendor exchange-contract boundaries; every later cluster has a different policy or verification boundary.

Stop conditions: parity requires a product/design decision, an inline-style exception, unbounded dynamic styling, a new role-color policy, or excluded route/query, financial, database, authentication, CSP-enforcement, Plaid, or later-task work; desktop, phone, or exact 768px behavior becomes ambiguous; protected/live/destructive access appears; verification changes the plan; cleanup fails; command-center checks fail; scope expands; or a preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered zero-style proof for Payroll including both conditional branches and `/payroll/spending`; zero `.style.*` writes in both included controllers; exact residual tracked inventory of six style blocks, 37 template style attributes, zero JavaScript-generated attributes, and zero runtime writes plus zero Payroll route-generated style attributes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across Subscriptions in Personal/BFM/Luxe Legacy plus BFM Payroll and Personal/Luxe Legacy denial at desktop, phone, and exact 768px for clipboard fallback, disclosure, dialogs, mouse/Enter/Space/Escape behavior, role colors, spending refresh, conditional new-role controls, responsive overflow, denied networking, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and all preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AX, Task 1P.4.3a.6, and its focused Task 2 slice done locally; make separate 4AX-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated seams and replacement patterns, final inventory, behavior/responsive/browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AX-R gate.

Result: all three baseline-counted Payroll template attributes, one conditional rendered attribute, two route-generated Payroll spending-partial attributes, and all five Subscriptions/Payroll runtime style writes are removed through a maintained clipboard-proxy class, semantic disclosure and conditional-control state, finite role classes, and bounded percentage classes. Baseline and final full smoke, focused source/rendered/repeated-partial proof, configured-auth/no-password isolated Chrome over all-entity Subscriptions and the BFM-only Payroll boundary at phone, exact 768px, and desktop, denied networking, zero unexpected browser/page errors, syntax, exact cleanup, and inventory reconciliation passed. Clipboard success and rejection fallback, dialogs, keyboard behavior, role colors, employee detail, repeated spending swaps, bounded bars, import new-role visibility, and responsive layout remain intact. The residual tracked inventory is exactly 6/37/0/0, and the Payroll route emits zero style attributes. No commit, push, PR, publication, deployment, live/protected access, route-query, financial, database, authentication, CSP enforcement, Plaid, later-cluster, destructive, downstream, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-24-subscriptions-payroll-style-compatibility-4ax.md`. Exact 4AX-R durability remains a separate Ryan gate.

Suggested next work block: 4AX-R is now confirmed by Ryan's direct instruction to commit and push the verified result to `main`.

### Confirmed Work Block 4AX-R: Subscriptions And Payroll Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.6-R plus the authorized Task 4 publication slice.

Included: explicitly stage and commit the exact verified 4AX application, controller, templates, maintained tests, CSP contract, evidence, and Runway OS paths on `codex/csp-subscriptions-payroll-styles`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify its exact source SHA and credential-free production `/health`; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.3a.7 and every later task; any new mutation beyond verified 4AX; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the verified 4AX source set, direct-main push, automatic release observation, health verification, and sanitized Runway OS closeout form one controlled durability boundary. Task 1P.4.3a.7 is a separate implementation and third-party Plaid policy surface.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path staging, commit and ancestry verification, direct-main push, read-only automatic-deployment observation, credential-free health, sanitized closeout, and final intake. Ryan owns every expansion, manual live action, and broader recovery.

Expected surfaces: the exact verified 4AX paths for the source commit; `origin/main`; the automatic `Fly Deploy` workflow and deploy job; credential-free production `/health`; then only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, and a sanitized 4AX-R evidence log for closeout.

Defaults: use explicit-path staging only; preserve the verified template, conditional-rendered, route-generated, and runtime migration, residual 6/37/0/0 inventory, zero Payroll route-generated attributes, dual-auth responsive browser proof, and all three unrelated untracked files; use no PR, force push, manual workflow action, or non-automatic Fly mutation; observe only automatic deployment and credential-free health; use `[skip actions]` only for the sanitized closeout.

Blocking questions: none. Ryan's direct instruction to commit and push the verified result to `main` authorizes the exact release boundary.

Expansion candidates: none. Task 1P.4.3a.7 remains a separate implementation block.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, commit mismatch, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, recovery beyond a clean fast-forward and read-only diagnosis, or scope expansion.

Verification: exact changed and staged sets; full smoke; configured-auth/no-password isolated Chrome; Python, JavaScript, and JSON syntax; whitespace; dashboard refresh/health/generated state; commit content and ancestry; exact remote SHA; automatic Fly workflow and deploy-job result for the source commit; credential-free production `/health`; final local/remote alignment; and all preserved untracked files.

Dashboard closeout: mark 4AX-R and Task 1P.4.3a.6-R complete; preserve Task 1P.4.3a.7 as the next separately gated planning decision; align human-readable sources and `state.json`; refresh and health-check; inspect generated state; commit only the sanitized command-center closeout with `[skip actions]`; push directly to `main`; and verify no second workflow run exists for the skip-actions commit.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health result, final local/remote alignment, preserved exclusions, and separately gated Task 1P.4.3a.7.

Result: exact 15-path source commit `fd16a004d81cf378948c6b6b3158e667c4a3905f` is durable on `origin/main`. Automatic Fly Deploy run `30069896710` and deploy job `89408388148` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact changed and staged sets, full smoke, configured-auth/no-password isolated Chrome, Python and JavaScript syntax, JSON, whitespace, command-center health, commit contents, ancestry, remote alignment, automatic release, production health, and all preserved-file checks passed. No PR, force push, manual workflow action, workflow edit, non-automatic Fly mutation, credential, protected data, real database, retained upload, authenticated production page, downstream access/write, Task 1P.4.3a.7 work, broader recovery, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-24-subscriptions-payroll-style-compatibility-release-4ax-r.md`.

Suggested next work block: separately decide whether to plan and confirm Task 1P.4.3a.7 for Data Sources and Plaid entry-page style compatibility.

### Confirmed Work Block 4AW: Weekly And Waterfall Style Compatibility

Status: complete, verified, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.5 plus only its focused Task 2 regression slice.

Included: remove four Weekly and nine Waterfall template style attributes plus four `waterfall.js` runtime style writes; preserve validated calculations, credit-card and paydown bars, category pace, Waterfall fractional geometry, actual/target views, tooltips, animation staggering, tax/target behavior, exact responsive layout, and Personal/BFM versus Luxe Legacy boundaries; add focused maintained source, rendered-response, and configured-auth/no-password isolated-browser proof; reconcile the exact residual CSP style inventory; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.3a.6-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route, financial-calculation, database-query, product, authentication, CSRF, dependency, CSP-header/nonce/exception/enforcement, Plaid, protected-data, credential, external/live, GitHub, publication, deployment, workflow, or downstream changes; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: Weekly and Waterfall share credit-card/paydown bars, calculation-backed percentages, responsive visualization, and the maintained synthetic browser harness. Subscriptions/Payroll introduce clipboard, disclosure, dynamic role-color, and BFM-only payroll behavior; Plaid and standalone documents have separate policy and authentication boundaries; final CSP enforcement depends on every style cluster.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product/design decision, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-weekly-waterfall-styles`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/weekly.html`; `web/templates/waterfall.html`; `web/static/waterfall.js`; `web/static/style.css`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. No route file change is expected.

Defaults: preserve appearance and calculations rather than redesigning; use maintained semantic and bounded percentage classes for integer Weekly, paydown, and trend values; use inert data plus measured Web Animations API effects for exact fractional Waterfall geometry, tooltip coordinates, and staggered motion without runtime style mutation; use temporary synthetic Personal/BFM/Luxe Legacy data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost traffic, zero unexpected console/page errors, and exact cleanup; preserve all three unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.6 introduces a different controller, clipboard/disclosure behavior, dynamic role colors, and the BFM-only payroll boundary; every later cluster has a different policy or verification boundary.

Stop conditions: parity requires a product/design choice, calculation or route change, inline-style exception, visual drift, or excluded financial, database, authentication, CSP-enforcement, Plaid, or later-task work; desktop, phone, or exact 768px behavior becomes ambiguous; protected/live/destructive access appears; verification changes the plan; cleanup fails; command-center checks fail; scope expands; or any preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving both included templates contain zero style attributes; zero `.style.*` writes in `waterfall.js`; exact residual inventory of six style blocks, 40 template style attributes, zero generated attributes, and five runtime writes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across Personal/BFM supported routes and Luxe Legacy denial at desktop, phone, and exact 768px for bars, fractional geometry, actual/target views, tooltip edge placement, animation staggering, tax/target inputs, responsive overflow, denied networking, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and all preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AW, Task 1P.4.3a.5, and its focused Task 2 slice done locally; make separate 4AW-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated surfaces and patterns, final 6/40/0/5 inventory, calculation/visual/responsive/browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AW-R gate.

Result: all four Weekly and nine Waterfall template style attributes plus all four Waterfall runtime style writes are removed through semantic and bounded percentage classes, inert fractional geometry, and measured Web Animations API effects. Baseline and final full smoke, focused source/rendered proof, configured-auth/no-password isolated Chrome over Personal/BFM supported routes and the Luxe Legacy denial boundary at phone, exact 768px, and desktop, denied networking, zero unexpected browser/page errors, syntax, exact cleanup, and inventory reconciliation passed. Validated calculations, integer and fractional bars, actual/target views, tooltip placement, animation staggering, inputs, navigation, and responsive layout remain intact. The residual tracked inventory is exactly 6/40/0/5. No commit, push, PR, publication, deployment, live/protected access, route, calculation, database, authentication, CSP enforcement, later-cluster work, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-weekly-waterfall-style-compatibility-4aw.md`. Exact 4AW-R durability remains a separate Ryan gate.

Suggested next work block: separately decide whether to plan and confirm Task 1P.4.3a.6 for Subscriptions and Payroll style compatibility.

### Confirmed Work Block 4AW-R: Weekly And Waterfall Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.5-R plus the authorized Task 4 publication slice.

Included: explicitly stage and commit the exact verified 4AW application, controller, templates, maintained tests, CSP contract, evidence, and Runway OS paths on `codex/csp-weekly-waterfall-styles`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify its exact source SHA and credential-free production `/health`; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.3a.6 and every later task; any new mutation beyond verified 4AW; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the verified 4AW source set, direct-main push, automatic release observation, health verification, and sanitized Runway OS closeout form one controlled durability boundary. Task 1P.4.3a.6 is a separate implementation and verification surface.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path staging, commit and ancestry verification, direct-main push, read-only automatic-deployment observation, credential-free health, sanitized closeout, and final intake. Ryan owns every expansion, manual live action, and broader recovery.

Expected surfaces: the exact verified 4AW paths for the source commit; `origin/main`; the automatic `Fly Deploy` workflow and deploy job; credential-free production `/health`; then only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, and a sanitized 4AW-R evidence log for closeout.

Defaults: use explicit-path staging only; preserve the verified 13-attribute/four-runtime-write migration, residual 6/40/0/5 inventory, dual-auth responsive browser proof, and all three unrelated untracked files; use no PR, force push, manual workflow action, or non-automatic Fly mutation; observe only automatic deployment and credential-free health; use `[skip actions]` only for the sanitized closeout.

Blocking questions: none. Ryan's direct instruction to commit and push the verified result to `main` authorizes the exact release boundary.

Expansion candidates: none. Task 1P.4.3a.6 remains a separate implementation block.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, commit mismatch, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, recovery beyond a clean fast-forward and read-only diagnosis, or scope expansion.

Verification: exact changed and staged sets; full smoke; configured-auth/no-password isolated Chrome; Python, JavaScript, and JSON syntax; whitespace; dashboard refresh/health/generated state; commit content and ancestry; exact remote SHA; automatic Fly workflow and deploy-job result for the source commit; credential-free production `/health`; final local/remote alignment; and all preserved untracked files.

Dashboard closeout: mark 4AW-R and Task 1P.4.3a.5-R complete; preserve Task 1P.4.3a.6 as the next separately gated planning decision; align human-readable sources and `state.json`; refresh and health-check; inspect generated state; commit only the sanitized command-center closeout with `[skip actions]`; push directly to `main`; and verify no second workflow run exists for the skip-actions commit.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health result, final local/remote alignment, preserved exclusions, and separately gated Task 1P.4.3a.6.

Result: exact 13-path source commit `dec8b0731b346c19b631b0f6c405bfc4c19ede4a` is durable on `origin/main`. Automatic Fly Deploy run `30067582194` and deploy job `89401458560` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact changed and staged sets, full smoke, configured-auth/no-password isolated Chrome, Python and JavaScript syntax, JSON, whitespace, command-center health, commit contents, ancestry, remote alignment, automatic release, production health, and all preserved-file checks passed. No PR, force push, manual workflow action, workflow edit, non-automatic Fly mutation, broader recovery, Task 1P.4.3a.6 work, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-weekly-waterfall-style-compatibility-release-4aw-r.md`.

Suggested next work block: separately decide whether to plan and confirm Task 1P.4.3a.6 for Subscriptions and Payroll style compatibility.

### Confirmed Work Block 4AV: Cash Flow And Planning Style Compatibility

Status: complete, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.4 plus only its focused Task 2 regression slice.

Included: remove two Cash Flow, one Long-Term Planning, and ten Short-Term Planning template style attributes plus three `cashflow.js`, three `planning.js`, and two `short-term-planning.js` runtime style writes; preserve data-driven progress, precise modal origins, input sizing, disabled and visibility state, transaction drilldowns, responsive behavior, and Personal/BFM versus Luxe Legacy boundaries; add focused maintained source, rendered-response, and configured-auth/no-password isolated-browser proof; reconcile the exact residual CSP style inventory; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.3a.5-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route, financial-calculation, database, category-domain, product, authentication, CSRF, dependency, CSP-header/nonce/exception/enforcement, protected-data, credential, external/live, GitHub, publication, deployment, workflow, or downstream changes; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the three pages share page-owned controllers, modal-origin behavior, bounded progress, form-state behavior, entity-boundary tests, and one synthetic browser harness. Weekly/Waterfall, Subscriptions/Payroll, Plaid, standalone documents, and final CSP enforcement each introduce a different verification or risk boundary.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-cashflow-planning-styles`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/static/style.css`; `web/static/cashflow.js`; `web/static/planning.js`; `web/static/short-term-planning.js`; `web/templates/cashflow.html`; `web/templates/planning.html`; `web/templates/short_term_planning.html`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. No route file change is expected.

Defaults: preserve appearance and behavior rather than redesigning; use semantic static classes and the existing `u-pct-0` through `u-pct-100` contract without changing displayed calculations; use HTML sizing and state attributes plus CSS state selectors instead of runtime style writes; use measured Web Animations API motion only when it preserves precise modal origins without inline style mutation; use temporary synthetic Personal/BFM/Luxe Legacy data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost traffic, zero unexpected console/page errors, and exact cleanup; preserve all three unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.5 introduces calculation-backed visualization and animation sequencing, and every later cluster has a different policy or verification boundary.

Stop conditions: parity requires a product/design choice, inline-style exception, unbounded dynamic styling, or excluded route, financial, database, authentication, CSP-enforcement, or later-task work; desktop, phone, or exact 768px behavior becomes ambiguous; protected/live/destructive access appears; verification changes the plan; cleanup fails; command-center checks fail; scope expands; or any preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving all three included templates contain zero style attributes; zero `.style.*` writes in `cashflow.js`, `planning.js`, and `short-term-planning.js`; exact residual inventory of six style blocks, 53 template style attributes, zero generated attributes, and nine runtime writes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across supported Personal/BFM/Luxe Legacy boundaries at desktop, phone, and exact 768px for progress, modal origin, input sizing, disabled/hidden state, drilldowns, responsive overflow, denied networking, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and all preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AV, Task 1P.4.3a.4, and its focused Task 2 slice done locally; make separate 4AV-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated surfaces and patterns, final 6/53/0/9 inventory, focused/full/auth/entity/responsive browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AV-R gate.

Result: all 13 included template style attributes and eight included runtime style writes are removed through semantic classes, bounded percentage classes, HTML state/sizing attributes, CSS state selectors, and measured Web Animations API card-origin motion. Baseline and final full smoke, focused source/rendered proof, configured-auth/no-password isolated Chrome over Personal/BFM supported routes and the Luxe Legacy denial boundary at phone, exact 768px, and desktop, denied networking, zero unexpected browser/page errors, syntax, exact cleanup, and inventory reconciliation passed. The residual tracked inventory is exactly 6/53/0/9. No commit, push, PR, publication, deployment, live/protected access, later-cluster work, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-cashflow-planning-style-compatibility-4av.md`. Exact 4AV-R durability remains a separate Ryan gate.

### Confirmed Work Block 4AV-R: Cash Flow And Planning Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.4-R plus the authorized Task 4 publication slice.

Included: explicitly stage and commit the exact verified 4AV application, controller, template, maintained-test, CSP contract, evidence, and Runway OS paths on `codex/csp-cashflow-planning-styles`; cleanly fast-forward local `main`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify its exact source SHA and credential-free production `/health`; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.3a.5 and every later task; any new mutation beyond verified 4AV; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the verified 4AV source set, branch-to-main fast-forward, automatic release observation, health verification, and sanitized Runway OS closeout form one controlled durability boundary. Task 1P.4.3a.5 is a separate implementation and verification surface.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path staging, commit and ancestry verification, direct-main push, read-only automatic-deployment observation, credential-free health, sanitized closeout, and final intake. Ryan owns every expansion, manual live action, and broader recovery.

Expected surfaces: the exact verified 4AV paths for the source commit; local and remote `main`; the automatic `Fly Deploy` workflow and deploy job; credential-free production `/health`; then only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, and a sanitized 4AV-R evidence log for closeout.

Defaults: use explicit-path staging only; preserve the verified 13-attribute/eight-runtime-write migration, residual 6/53/0/9 inventory, dual-auth responsive browser proof, and all three unrelated untracked files; use no PR, force push, manual workflow action, or non-automatic Fly mutation; observe only automatic deployment and credential-free health; use `[skip actions]` only for the sanitized closeout.

Blocking questions: none. Ryan's direct instruction to commit and push the verified result to `main` authorizes the exact release boundary.

Expansion candidates: none. Task 1P.4.3a.5 remains a separate implementation block.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, commit mismatch, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, recovery beyond a clean fast-forward and read-only diagnosis, or scope expansion.

Verification: exact changed and staged sets; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python, JavaScript, and JSON syntax; whitespace; dashboard refresh/health/generated state; commit content and ancestry; exact remote SHA; automatic Fly workflow and deploy-job result for the source commit; credential-free production `/health`; final local/remote alignment; and all preserved untracked files.

Dashboard closeout: after source durability, automatic deployment, and health verification, mark 4AV-R and Task 1P.4.3a.4-R complete; preserve Task 1P.4.3a.5 as the next separately gated planning decision; align human-readable sources and `state.json`; refresh and health-check; inspect generated state; commit only the sanitized command-center closeout with `[skip actions]`; push directly to `main`; and verify no second workflow run exists for the skip-actions commit.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health result, final local/remote alignment, preserved exclusions, and separately gated Task 1P.4.3a.5.

Result: exact 16-path source commit `7fa732bda18f0aeb735492d1d23cfaf22d2d42e5` is durable on local and remote `main`. Automatic Fly Deploy run `30055663641` and deploy job `89366650549` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact changed and staged sets, protected-boundary and high-confidence sensitive-addition scans, full smoke, configured-auth/no-password isolated Chrome, Python and JavaScript syntax, JSON, whitespace, dashboard refresh/health/generated-state inspection, commit contents, clean fast-forward, ancestry, remote alignment, automatic release, production health, and all preserved-file checks passed. No PR, force push, manual workflow action, workflow edit, non-automatic Fly mutation, broader recovery, Task 1P.4.3a.5 work, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-cashflow-planning-style-compatibility-release-4av-r.md`.

Suggested next work block: separately decide whether to authorize exact-scope 4AV-R durability and release after reviewing the local result. Task 1P.4.3a.5 remains separately gated.

### Confirmed Work Block 4AU: Categorization And Upload Style Compatibility

Status: complete, verified, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.3 plus only its focused Task 2 regression slice.

Included: remove one inline style block and 56 template style attributes from `categorize.html`, `categorize_orphans.html`, `upload.html`, and `upload_dialog.html`; move the included styling into maintained semantic classes in `web/static/style.css`; preserve compact tables and forms, alias visibility and prefill, confidence badges, pagination, orphan reassignment, upload month/settings controls, upload preview dialogs, mobile layout, and the status-only `Mark incomplete` wording and request contract; add focused maintained source/rendered and configured-auth/no-password isolated-browser proof; reconcile the exact residual CSP style inventory; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.3a.4-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route, controller, financial, database, category-domain, product, authentication, CSRF, dependency, CSP-header/nonce/exception/enforcement, protected-data, credential, external/live, GitHub, publication, deployment, workflow, or downstream changes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: all 56 attributes and the one style block share the maintained categorization/upload controller, compact form/table vocabulary, dialog and pagination behavior, and one temporary all-entity responsive browser path. Task 1P.4.3a.4 introduces planning controllers, runtime style writes, progress state, and entity-boundary verification, while publication carries a distinct live-side-effect gate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product/design decision, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-categorization-upload-styles`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/static/style.css`; `web/templates/categorize.html`; `categorize_orphans.html`; `upload.html`; `upload_dialog.html`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. `web/static/categorization-upload.js` remains the behavior reference and is expected to remain unchanged.

Defaults: preserve appearance and behavior rather than redesigning; use static semantic classes and existing shared utilities; add no dependency or runtime style-writing mechanism; use temporary synthetic Personal/BFM/Luxe Legacy data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.4 has a different controller, runtime-state, entity-boundary, and verification path.

Stop conditions: parity requires a product/design choice or excluded route, controller, database, financial, category-domain, authentication, CSP-enforcement, unbounded dynamic styling, or later-task work; desktop, phone, or exact 768px behavior becomes ambiguous; protected/live/destructive access appears; verification changes the plan; exact cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving all four included templates contain zero inline style blocks and zero style attributes; exact residual inventory of six style blocks, 66 template style attributes, zero generated attributes, and 17 runtime writes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across Personal/BFM/Luxe Legacy at desktop, phone, and exact 768px for compact categorization tables and forms, alias/confidence states, pagination, orphan reassignment, upload controls, preview/dialog layout, status-only wording, responsive overflow, denied networking, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AU, Task 1P.4.3a.3, and its focused Task 2 slice done locally; make separate 4AU-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated surfaces and patterns, final inventory, source/rendered/browser results, responsive and all-entity parity, cleanup evidence, changed paths, local branch state, preserved exclusions, and the separate 4AU-R gate.

Suggested next work block: separately decide whether to authorize exact-scope 4AU-R durability and release after reviewing the local result. Task 1P.4.3a.4 remains separately gated.

Result: all one included inline style block and 56 template style attributes are removed through maintained semantic classes and the existing bounded percentage contract without changing `categorization-upload.js`. The exact residual tracked inventory is six inline style blocks, 66 template style attributes, zero generated-markup style attributes, and 17 application runtime style writes. Baseline and final full smoke, focused source/rendered assertions, configured-auth/no-password isolated Chrome across Personal, BFM, and Luxe Legacy at phone, exact 768px, and desktop, relevant syntax, JSON, whitespace, exact-scope, denied-networking, zero-unexpected-error, cleanup, and preserved-file checks passed. No commit, push, PR, publication, deployment, live/protected access, route, controller, financial, database, category-domain, product, authentication, CSP enforcement, later-cluster, destructive, downstream, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-categorization-upload-style-compatibility-4au.md`.

### Confirmed Work Block 4AU-R: Categorization And Upload Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.3-R plus the authorized Task 4 publication slice.

Included: explicitly stage and commit the exact verified 4AU application, template, maintained-test, CSP contract, evidence, and Runway OS paths on `codex/csp-categorization-upload-styles`; cleanly fast-forward local `main`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify its exact source SHA and credential-free production `/health`; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.3a.4 and every later task; any new mutation beyond verified 4AU; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the verified 4AU source set, branch-to-main fast-forward, automatic release observation, health verification, and sanitized Runway OS closeout form one controlled durability boundary. Task 1P.4.3a.4 is a separate implementation and verification surface.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns exact-path staging, commit and ancestry verification, direct-main push, read-only automatic-deployment observation, credential-free health, sanitized closeout, and final intake. Ryan owns every expansion, manual live action, and broader recovery.

Expected surfaces: the exact verified 4AU paths for the source commit; local and remote `main`; the automatic `Fly Deploy` workflow and deploy job; credential-free production `/health`; then only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, and a sanitized 4AU-R evidence log for closeout.

Defaults: use explicit-path staging only; preserve the verified one-block/56-attribute migration, residual 6/66/0/17 inventory, browser proof, and both unrelated untracked files; use no PR, force push, manual workflow action, or non-automatic Fly mutation; observe only automatic deployment and credential-free health; use `[skip actions]` only for the sanitized closeout.

Blocking questions: none. Ryan's direct instruction to commit and push the verified result to `main` authorizes the exact release boundary.

Expansion candidates: none. Task 1P.4.3a.4 remains a separate implementation block.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, preserved-file overlap, local or remote `main` divergence, push rejection, commit mismatch, recovery beyond a clean fast-forward, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, or scope expansion.

Verification: exact changed and staged sets; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python, JavaScript, and JSON syntax; whitespace; dashboard refresh/health/generated state; commit content and ancestry; exact remote SHA; automatic workflow and deploy-job result for the source SHA; credential-free production health; final local/remote alignment; and both preserved untracked files.

Dashboard closeout: after release verification, mark 4AU-R and Task 1P.4.3a.3-R done; make Task 1P.4.3a.4 the next separate planning gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; then publish one command-center-only `[skip actions]` closeout commit.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and separately gated Task 1P.4.3a.4.

Suggested next work block: plan Task 1P.4.3a.4 separately after 4AU-R closes; do not infer implementation authorization.

Result: exact 14-path source commit `058016623d55723b13b32972403db792f245ef43` was cleanly fast-forwarded and pushed to local and remote `main` without PR or force. Automatic Fly Deploy run `30049142292` and deploy job `89347105219` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact changed and staged sets, sensitive-addition and protected-boundary scans, maintained full smoke, configured-auth/no-password isolated Chrome, syntax, JSON, whitespace, dashboard, commit-content, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No manual workflow action, workflow edit, non-automatic Fly mutation, credential, protected data, real database, retained upload, authenticated production page, downstream action, Task 1P.4.3a.4 work, broader recovery, destructive action, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-categorization-upload-style-compatibility-release-4au-r.md`.

### Confirmed Work Block 4AT: Transaction And Matching Style Compatibility

Status: complete, verified, local-only, and uncommitted.

Parent tasks: Phase 4 Task 1P.4.3a.2 plus only its focused Task 2 regression slice.

Included: remove 63 template style attributes, seven JavaScript-generated split-line style attributes, and four transaction runtime style writes from `transactions.html`, `match.html`, `match_card.html`, `vendor_card.html`, transaction results, row, row-edit, and split-editor fragments plus `transaction-fragments.js`; preserve transaction filtering, sorting, copying, editing, category/subcategory changes, matching/vendor-card progress, repeated HTMX swaps, dynamic split-line creation, total-state feedback, auto/manual split lifecycle, modals, and responsive layout; add focused maintained source/rendered and configured-auth/no-password isolated-browser proof; reconcile the exact residual CSP style inventory; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.3a.3-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route, financial, database, matching-policy, product, authentication, CSRF, dependency, CSP-header/nonce/exception/enforcement, category-domain, protected-data, credential, external/live, GitHub, publication, deployment, workflow, or downstream changes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: all included occurrences share `style.css`, the transaction/matching fragment family, `transaction-fragments.js`, repeated HTMX initialization, bounded percentage state, split-total state, and one responsive isolated-browser path. The categorization/upload cluster has a distinct controller and dialog, pagination, confidence-state, and Upload Undo regression contract.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-transaction-matching-styles`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/static/style.css`; `web/static/transaction-fragments.js`; `web/templates/transactions.html`; `web/templates/match.html`; `web/templates/components/match_card.html`; `vendor_card.html`; `txn_results.html`; `txn_row.html`; `txn_row_edit.html`; `txn_split_editor.html`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard.

Defaults: preserve appearance and behavior rather than redesigning; reuse static semantic classes and the bounded `u-pct-0` through `u-pct-100` contract; replace split-total runtime colors with explicit balanced/unbalanced state classes; use temporary synthetic Personal/BFM/Luxe Legacy data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.3 has a different controller and verification boundary.

Stop conditions: parity requires route, database, financial, matching-policy, product, authentication, CSP-enforcement, unbounded dynamic styling, protected/live/destructive, or later-task work; desktop, phone, or exact 768px behavior becomes ambiguous; verification changes the plan; exact cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving all included templates/fragments contain zero style attributes; zero generated `style=` markup and zero runtime `.style.*` writes in `transaction-fragments.js`; exact residual inventory of seven style blocks, 122 template attributes, zero generated attributes, and 17 runtime writes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across Personal/BFM/Luxe Legacy at desktop, phone, and exact 768px for transaction filters, repeated swaps, sorting, copy, editing, matching/vendor cards, split totals, dynamic lines, auto/manual split lifecycle, modal behavior, denied networking, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AT, Task 1P.4.3a.2, and its focused Task 2 slice done locally; make separate 4AT-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated surfaces and patterns, final inventory, focused/full/auth/entity/responsive browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AT-R gate.

Suggested next work block: separately decide whether to authorize exact-scope 4AT-R durability and release. Task 1P.4.3a.3 remains separately gated.

Result: all 63 included template style attributes, seven generated split-line style attributes, and four transaction runtime style writes are removed through maintained semantic classes, bounded `u-pct-*` classes, and explicit balanced/unbalanced split-total state. The exact residual tracked inventory is seven inline style blocks, 122 template style attributes, zero generated-markup style attributes, and 17 application runtime style writes. Baseline and final full smoke, source/rendered assertions, configured-auth/no-password isolated Chrome across Personal, BFM, and Luxe Legacy at desktop, phone, and exact 768px, relevant syntax, JSON, whitespace, dashboard, exact-scope, denied-networking, zero-unexpected-error, cleanup, and preserved-file checks passed. No commit, push, PR, publication, deployment, live/protected access, route, financial, database, matching-policy, product, authentication, CSP enforcement, later-cluster, destructive, downstream, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-transaction-matching-style-compatibility-4at.md`.

### Confirmed Work Block 4AT-R: Transaction And Matching Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.2-R plus the publication portion of Task 4.

Included: explicitly stage the exact 19 verified 4AT application, controller, template, maintained-test, CSP contract, evidence, and Runway OS paths; create one source commit on `codex/csp-transaction-matching-styles`; require local `main`, remote `main`, and the feature base to match before a clean fast-forward; push `main` directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment for the exact source SHA; verify credential-free production `/health`; then write, verify, commit with `[skip actions]`, and push one sanitized command-center-only closeout.

Excluded: Task 1P.4.3a.3 and every later task; any new application, runtime, style, route, authentication, financial, database, matching-policy, product, dependency, CSP-header/nonce/exception/enforcement, or policy mutation beyond verified 4AT; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly authorized commit and direct push to `main`. The exact 4AT set is already locally verified, and this block adds only established durability, automatic-release observation, credential-free health verification, and sanitized closeout.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, maintained verification, direct-main durability, read-only automatic-deployment observation, credential-free health, and sanitized Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and later-task decision.

Runner path: refresh active release state; rerun exact release verification; explicitly stage and commit the verified 4AT paths on `codex/csp-transaction-matching-styles`; require local and remote `main` to equal the known base; fast-forward local `main`; push directly without force; inspect the automatic Fly run for the exact source SHA; request only credential-free production `/health`; then write, verify, commit with `[skip actions]`, and push the sanitized command-center closeout.

Expected surfaces: the exact 19 verified 4AT paths for the source commit; local and remote `main`; the automatic `Fly Deploy` workflow and deploy job; credential-free production `/health`; then only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, and a sanitized 4AT-R evidence log for closeout.

Defaults: explicit-path staging only; no PR; no force push; no manual workflow dispatch or rerun; no non-automatic Fly mutation; preserve the verified 63/7/4 migration, residual 7/122/0/17 inventory, both-auth all-entity responsive browser proof, and both unrelated untracked files; use `[skip actions]` only for the closeout commit.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.3 requires a separate implementation and browser-proof boundary.

Stop conditions: changed or staged paths differ from the exact contract; a protected path or high-confidence sensitive addition appears; maintained verification fails; either preserved file overlaps; local or remote `main` diverges from the known base; fast-forward is not clean; push is rejected; the automatic deployment fails or requires mutation; the workflow head SHA differs; credential-free production health is not HTTP 200 with the expected sanitized response; or recovery exceeds clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python and JavaScript syntax; JSON; `git diff --check`; dashboard refresh/health/generated state; commit contents; clean fast-forward; ancestry; exact remote SHA; automatic workflow and deploy-job result for the exact source SHA; credential-free production health; final local/remote alignment; and both preserved untracked files.

Dashboard closeout: after release verification, mark 4AT-R and Task 1P.4.3a.2-R done; make Task 1P.4.3a.3 the next separate planning gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; then publish one command-center-only `[skip actions]` closeout commit.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health results, final local/remote alignment, preserved exclusions, and the separate Task 1P.4.3a.3 gate.

Suggested next work block: plan Task 1P.4.3a.3 separately after 4AT-R closes; do not infer implementation authorization.

Result: exact 19-path source commit `30236a7def65d190fffc8ba89ce70cfab8ad5a09` is durable on local and remote `main`. Automatic Fly Deploy run `30045444363` and deploy job `89335369654` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained smoke, configured-auth/no-password isolated Chrome, syntax, JSON, whitespace, dashboard, generated-state, commit-content, clean-fast-forward, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. GitHub reported only the existing non-blocking Node deprecation annotation for `actions/checkout@v4`, forced onto Node 24. No PR, force push, manual workflow action, non-automatic Fly mutation, Task 1P.4.3a.3 work, broader recovery, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-transaction-matching-style-compatibility-release-4at-r.md`.

### Confirmed Work Block 4AS-R: Shared Shell And Dashboard/Report Style Compatibility Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.3a.1-R.

Included: explicitly stage the exact verified 4AS application, controllers, templates, maintained tests, CSP contract, evidence, and Runway OS paths; create one source commit on `codex/csp-shared-dashboard-styles`; cleanly fast-forward local `main`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify the exact source SHA and credential-free production `/health`; then create and push one sanitized command-center-only `[skip actions]` closeout commit so no second deployment runs.

Excluded: Task 1P.4.3a.2 and every later task; any new application, runtime, style, route, authentication, financial, database, product, dependency, CSP-header/nonce/exception/enforcement, or policy mutation beyond verified 4AS; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop in the current task. Ryan owns every scope expansion and recovery beyond a clean fast-forward plus read-only diagnosis.

Defaults: use explicit-path staging only; preserve the verified 26 template, two generated, and ten runtime style migration plus the exact residual 7/185/7/21 inventory; preserve configured-auth/no-password all-entity responsive proof and both unrelated untracked files; observe only the automatic deployment and credential-free health; use `[skip actions]` only for the sanitized closeout.

Stop conditions: an unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, scope expansion, or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed and staged sets; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python, JavaScript, and JSON syntax; whitespace; dashboard refresh/health/generated state; commit contents; ancestry; exact remote SHA; automatic workflow and deploy-job result; credential-free production health; final local/remote alignment; and both preserved untracked files.

Report point: return source and closeout commit SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and the separately gated Task 1P.4.3a.2.

Result: exact 22-path source commit `8b85c38845c2c9389ff3d17d5cbf1436540d23f9` is durable on local and remote `main`. Automatic Fly Deploy run `30040196919` and deploy job `89317958328` passed every reported step for that exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact staging, protected-boundary and sensitive-addition scans, maintained verification, clean fast-forward, remote alignment, automatic deployment, health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, broader recovery, Task 1P.4.3a.2 work, or excluded mutation occurred.

Evidence: `command-center/logs/2026-07-23-shared-dashboard-style-compatibility-release-4as-r.md`.

### Confirmed Work Block 4AS: Shared Shell And Dashboard/Report Style Compatibility

Status: complete and verified locally on `codex/csp-shared-dashboard-styles`; durability remains separate.

Parent tasks: Phase 4 Task 1P.4.3a.1 plus only its focused Task 2 regression slice.

Included: remove 26 template style attributes, two JavaScript-generated markup style attributes, and ten application runtime style writes from `base.html`, `reports.html`, the shared sidebar and dashboard/report fragments, `app-shell.js`, and `dashboard-fragments.js`; preserve responsive navigation, AI-chat scroll locking, report selection/export controls, repeated HTMX swaps, charts, category and insight drilldowns, tooltip positioning, visibility state, loading state, entity accents, and responsive layout; add focused maintained source/rendered and isolated-browser proof; reconcile the exact residual CSP style inventory; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.3a.2-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; styling outside the included shell/dashboard/report family; CSP headers, nonces, route-family exception policy, or enforcement; route, authentication, cache, CSRF, service-worker, manifest, financial, database, product, or dependency changes; credentials; protected data; real databases; retained uploads; external/live access; GitHub durability; publication; deployment; workflows; downstream access/writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: every included occurrence shares `style.css`, the shared shell or dashboard/report fragment controller seams, repeated HTMX initialization, responsive rendering, and one configured-auth/no-password isolated-browser path. The denser transaction/matching slice and every later page family have distinct interaction and verification surfaces and remain separate.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product choice, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-shared-dashboard-styles`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/static/style.css`; `web/static/app-shell.js`; `web/static/dashboard-fragments.js`; `web/templates/base.html`; `web/templates/reports.html`; the included sidebar and dashboard/report component templates; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard.

Defaults: preserve appearance and behavior rather than redesigning; use static CSS classes, semantic `hidden`/ARIA/state attributes, and bounded validated numeric classes; do not add CSP headers, nonces, enforcement, or an application style exception; use temporary synthetic Personal/BFM/Luxe Legacy data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Task 1P.4.3a.2 depends on the reusable state, numeric-class, and browser-proof patterns established here but has a separate dense transaction/matching verification surface.

Stop conditions: parity requires route, authentication, cache, financial, database, product, dependency, CSP enforcement, unbounded dynamic styling, application style exceptions, protected/live, destructive, or later-task work; desktop, phone, or exact 768px behavior becomes ambiguous; verification changes the plan; exact cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving the included templates contain zero style attributes; zero generated markup style attributes and runtime style writes in the included controllers; exact residual inventory of seven style blocks, 185 template attributes, seven generated attributes, and 21 runtime style writes; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage across Personal/BFM/Luxe Legacy at desktop, phone, and exact 768px for repeated swaps, reports, charts, drilldowns, tooltips, responsive navigation, AI overlay, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AS, Task 1P.4.3a.1, and its focused Task 2 slice done locally; make separate 4AS-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated surfaces and patterns, final inventory, focused/full/auth/entity/responsive browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AS-R gate.

Suggested next work block: separately decide whether to authorize exact-scope 4AS-R durability and release. Task 1P.4.3a.2 remains separately gated.

Result: all 26 included template style attributes, both included generated-markup style attributes, and all ten included runtime style writes are removed through static classes, semantic hidden/body state, entity classes, and bounded percentage classes. Responsive navigation, exact 768px behavior, repeated swaps, report controls, charts, drilldowns, tooltip placement, AI-chat body locking, visibility/loading state, and all three entity accents passed maintained configured-auth and no-password isolated-browser proof. The exact residual inventory is seven style blocks, 185 template attributes, seven generated attributes, and 21 runtime writes. Full smoke, relevant syntax, JSON, whitespace, dashboard refresh/health/generated state, cleanup, exact scope, and both preserved-file checks passed. No commit, push, publication, deployment, live, or excluded mutation occurred.

Evidence: `command-center/logs/2026-07-23-shared-dashboard-style-compatibility-4as.md`.

### Confirmed Work Block 4AR: Standalone And Error-Document Execution

Status: complete and verified locally on `codex/csp-standalone-documents`; durability remains separate.

Parent tasks: Phase 4 Task 1P.4.2c.8 plus only its focused Task 2 regression slice.

Included: move the five executable inline scripts and all source or rendered native handlers from `offline.html`, `errors/403.html`, `errors/404.html`, `errors/500.html`, and `kristine.html` into document-family-specific maintained local JavaScript; preserve data-free error/offline rendering, early theme initialization, retry behavior, `/k/` drill-down interaction, configured-auth and no-password boundaries, Personal/Luxe Legacy scope, BFM exclusion, status codes, and no exception leakage; add focused maintained source/rendered, request, and isolated-browser proof; reconcile the CSP inventory and sanitized evidence; and close Runway OS locally after verification.

Inventory correction: the maintained aggregate reports five inline scripts and one native handler because its source regex sees the offline retry handler but misses the Jinja-adjacent conditional `/k/` `onclick`. Work block 4AR treats the rendered `/k/` handler as included acceptance surface and requires both handler seams to reach zero without changing the durable task number.

Excluded: Tasks 1P.4.3a-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; style or runtime-style migration; CSP headers, nonces, route-family policy, or enforcement; route, authentication, cache, CSRF, service-worker, manifest, financial, database, product, or dependency changes; credentials; protected data; real databases; retained uploads; external/live access; GitHub durability; publication; deployment; workflows; downstream access/writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the five documents are the final execution-bearing family outside the ordinary authenticated shell and share one local-controller, request/status, auth-boundary, no-exception-leakage, and isolated-browser verification path. Style compatibility, policy enforcement, broader PWA proof, broad read-model coverage, and publication have different inventories, dependencies, or risk classes.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, protected-boundary review, CSP inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product choice, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-standalone-documents`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/offline.html`; `web/templates/errors/403.html`; `web/templates/errors/404.html`; `web/templates/errors/500.html`; `web/templates/kristine.html`; local standalone/error and `/k/` controllers under `web/static/`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. No route, CSS, database, dependency, service-worker, manifest, or deployment file is expected to change.

Defaults: use a blocking template-free local initializer for error/offline theme behavior and delegated retry plus a deferred template-free page-owned `/k/` controller; preserve existing copy, styles, status codes, URLs, cache/auth boundaries, entity behavior, and both false HTMX execution switches; use temporary synthetic Personal/BFM/Luxe Legacy data, configured-auth and no-password modes, localhost-only disposable browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; keep durability local-only and uncommitted.

Blocking questions: none.

Expansion candidates: none. Tasks 1P.4.3a-1P.4.4 and Task 1P.6 stay separate because their style-policy, header-enforcement, and installed-PWA verification paths depend on this block's result.

Stop conditions: parity requires route, authentication, cache, CSRF, service-worker, manifest, financial, database, product, dependency, style-policy, CSP-enforcement, protected/live, destructive, or later-task work; error behavior leaks exception details; a pre-existing defect makes parity ambiguous; verification changes the plan; exact cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; source and rendered-response assertions proving all five included templates contain zero executable inline scripts, zero native inline handlers including the conditional `/k/` seam, and zero `hx-on`; exact post-4AR aggregate execution inventory; configured-auth and no-password `.venv/bin/python scripts/mobile_drawer_browser_test.py` coverage for error/offline theme, offline retry, 403/404/500 rendering and status, no exception leakage, `/k/` authentication and entity boundaries, drill-down interaction, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; relevant Python and JavaScript syntax; JSON validation; `git diff --check`; dashboard refresh and health; generated-state inspection; exact-path scope review; and both preserved untracked files.

Dashboard closeout: after implementation and verification, mark 4AR, Task 1P.4.2c.8, and its focused Task 2 slice done locally; make separate 4AR-R durability/release the next Ryan gate; align human-readable sources with `state.json`; refresh and health-check; inspect generated state; and do not commit or publish.

Report point: return exact migrated behavior, corrected and final inventory, controller organization, focused/full/auth/error/offline browser proof, exact cleanup, changed paths, local branch state, preserved exclusions, and the separate 4AR-R gate.

Suggested next work block: separately decide whether to authorize exact-scope 4AR-R durability and release. Task 1P.4.3a still requires a fresh just-in-time decomposition and is not pre-authorized.

Result: `offline.html` and all three error templates now load blocking template-free `standalone-documents.js`, which preserves stored-theme initialization before paint and owns delegated retry behavior. `kristine.html` loads deferred template-free `kristine.js`, and its conditional category drill-down uses delegated data behavior. All five source templates and rendered responses contain zero executable inline scripts, zero native handlers, and zero `hx-on`; the final tracked-template execution inventory is 0 inline scripts, 21 external script occurrences, 0 inert JSON carriers, 0 source-recognized native handlers, and 0 `hx-on`. Baseline and final full smoke plus configured-auth/no-password isolated Chrome pass with exact error statuses, no exception leakage, early theme, retry, `/k/` auth/entity/drill-down behavior, denied networking, expected synthetic status console entries only, zero unexpected browser/page errors, and exact cleanup. Syntax, JSON, whitespace, dashboard refresh/health/generated state, exact scope, and preserved-file checks pass locally. No route, authentication, cache, CSRF, service-worker, manifest, style, CSP policy/header/enforcement, financial, database, product, dependency, protected/live, GitHub, publication, deployment, downstream, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-standalone-error-document-execution-4ar.md`.

### Confirmed Work Block 4AR-R: Standalone And Error-Document Execution Release

Status: complete, durable, automatically deployed, and credential-free health verified.

Parent task: Phase 4 Task 1P.4.2c.8-R plus the exact verified 4AR source set.

Included: explicitly stage the exact verified 4AR application, controllers, maintained tests, CSP contract, evidence, and Runway OS paths; create one source commit on `codex/csp-standalone-documents`; cleanly fast-forward local `main`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify credential-free production `/health` and the exact deployed source SHA; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Tasks 1P.4.3a-1P.4.4 and every later task; any new application/runtime/style/CSP-policy mutation beyond verified 4AR; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, maintained verification, direct-main durability, read-only automatic-deployment observation, credential-free health, and sanitized Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and later-task decision.

Runner path: verify local/remote alignment and the exact source set; refresh and health-check active state; run the full maintained synthetic and isolated-browser release matrix; stage explicit paths only; review the exact staged set and sensitive/protected boundaries; commit on `codex/csp-standalone-documents`; cleanly fast-forward local `main`; push without force; observe the automatic deployment read-only; verify credential-free production health; then publish a command-center-only `[skip actions]` closeout.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python and JavaScript syntax; JSON; whitespace; dashboard refresh, health, and generated-state inspection; commit contents; ancestry; exact remote SHA; automatic workflow result; credential-free production health; final local/remote alignment; and both preserved untracked files.

Dashboard closeout: record source commit, automatic workflow run and deploy job, health result, exact boundaries, and the separate Task 1P.4.3a just-in-time decomposition gate; align `state.json`; refresh and health-check; then publish one command-center-only `[skip actions]` closeout commit.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and the separate Task 1P.4.3a planning gate.

Suggested next work block: after 4AR-R closes, run fresh just-in-time decomposition for Task 1P.4.3a before proposing any style-policy implementation; do not infer implementation authorization.

Result: exact sixteen-path source commit `9e45ee6a653ff5053574785b7c5903c2bb1264c6` is durable on local and remote `main`. Automatic Fly Deploy run `30036622567` and deploy job `89306074345` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, generated-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. GitHub reported only the existing non-blocking Node deprecation annotation. No PR, force push, manual workflow action, non-automatic Fly mutation, protected-data access, Task 1P.4.3a implementation, broader recovery, or preserved-file mutation occurred. Task 1P.4.3a remains separately gated for fresh just-in-time decomposition. Evidence: `command-center/logs/2026-07-23-standalone-error-document-execution-release-4ar-r.md`.

### Confirmed Work Block 4AQ-R: Plaid Entry-Page Execution Release

Status: complete.

Parent task: Phase 4 Task 1P.4.2c.7-R plus the exact verified 4AQ source set.

Included: explicitly stage the exact verified 4AQ application, controllers, maintained tests, CSP contract, evidence, and Runway OS paths; create one source commit on `codex/csp-plaid-entry`; cleanly fast-forward local `main`; push directly to `origin/main` without force or PR; observe only the resulting automatic Fly deployment; verify credential-free production `/health` and the exact deployed source SHA; then publish one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.2c.8 and every later task; any new application/runtime mutation beyond verified 4AQ; the pre-existing empty-vendor aggregation edge; credentials; protected data; real databases; retained uploads; authenticated production pages; live Plaid; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, maintained verification, direct-main durability, read-only automatic-deployment observation, credential-free health, and sanitized Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and later-task decision.

Runner path: verify local/remote alignment and the exact source set; refresh and health-check active state; run the full maintained synthetic and isolated-browser release matrix; stage explicit paths only; review the exact staged set and sensitive/protected boundaries; commit on `codex/csp-plaid-entry`; cleanly fast-forward local `main`; push without force; observe the automatic deployment read-only; verify credential-free production health; then publish a command-center-only `[skip actions]` closeout.

Stop conditions: unexpected path, sensitive addition, protected-boundary risk, failed maintained verification, excluded staging, local or remote `main` divergence, push rejection, automatic deployment failure requiring mutation, credential-free health failure, exact source-SHA mismatch, preserved-file overlap, or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python and JavaScript syntax; JSON; whitespace; dashboard refresh, health, and generated-state inspection; commit contents; ancestry; exact remote SHA; automatic workflow result; credential-free production health; final local/remote alignment; and both preserved untracked files.

Dashboard closeout: record source commit, automatic workflow run and deploy job, health result, exact boundaries, and next separate Task 1P.4.2c.8 gate; align `state.json`; refresh and health-check; then publish one command-center-only `[skip actions]` closeout commit.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, the separately gated empty-vendor route edge, and Task 1P.4.2c.8.

Suggested next work block: after 4AQ-R closes, recheck Task 1P.4.2c.8 before proposing standalone/error-document execution; do not infer implementation authorization.

Result: exact thirteen-path source commit `993506b25d37c452471ea9ea413e734efe25d122` is durable on local and remote `main`. Automatic Fly Deploy run `30027699965` and deploy job `89276216665` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, generated-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, live Plaid, manual workflow action, non-automatic Fly mutation, protected-data access, empty-vendor route repair, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.8 remains separately gated. Evidence: `command-center/logs/2026-07-23-plaid-entry-page-execution-release-4aq-r.md`.

### Confirmed Work Block 4AQ: Plaid Entry-Page Execution

Status: complete and locally verified.

Parent task: Phase 4 Task 1P.4.2c.7 plus only its focused Task 2 regression slice.

Included: move the three executable inline application scripts and six native handlers from `data_sources.html` and `plaid.html` into page-owned template-free `data-sources.js` and `plaid.js`, delegated declarative controls, and non-script inert order-date and endpoint data; preserve vendor-label switching, preview-date counting, disconnect confirmations, both Plaid Link launch/exchange flows, button reset/error behavior, and the existing JSON-versus-form payload contracts; retain the two exact Plaid initializer tags for the later policy task; add focused source/rendered, synthetic request, and configured-auth/no-password isolated-browser proof with fake configuration, monkeypatched Plaid functions, exact initializer interception, denied outbound networking, and temporary synthetic all-entity data; reconcile the CSP inventory and sanitized evidence; and close Runway OS locally after verification.

Excluded: Task 1P.4.2c.8; Tasks 1P.4.3a-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; inline-style migration; CSP headers, nonces, exception policy, or enforcement; route, API, database-query, financial, product, authentication, CSRF, dependency, or service-worker changes; credentials; protected data; real databases; retained uploads; live Plaid or other external access; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Data Sources and Connected Accounts form one Plaid Link entry boundary with the same local-controller pattern, fake-config mocked-Link test seam, denied-network requirement, synthetic all-entity fixture family, and residual-inventory closeout. Standalone documents, style compatibility, policy enforcement, and publication have different verification and risk classes.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, protected-boundary review, CSP inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product choice, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify active command-center state, create `codex/csp-plaid-entry`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/data_sources.html`; `web/templates/plaid.html`; new `web/static/data-sources.js`; new `web/static/plaid.js`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. No route, CSS, database, dependency, or deployment file is expected to change.

Defaults: use two page-owned template-free controllers with delegated `data-*` actions; carry order dates and endpoint/configuration values through non-script inert data or ordinary data attributes; preserve endpoint paths, exchange encodings, confirmation language, current runtime-style behavior, both false HTMX execution switches, and both exact initializer tags; intercept only the exact Plaid initializer URL with a synthetic browser stub and abort every other non-localhost request; use fake configuration, monkeypatched Plaid functions, temporary synthetic all-entity data, both auth modes, zero unexpected browser errors, and exact cleanup; preserve both unrelated untracked files; and keep durability local-only.

Stop conditions: parity requires route, payload, database, financial, product, authentication, CSRF, dependency, style-policy, CSP-enforcement, service-worker, protected/live, destructive, or later-task work; a pre-existing page defect makes parity ambiguous; the exact initializer cannot be mocked without weakening denied networking; verification changes the plan; exact cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final full smoke; source and rendered zero-application-execution assertions for Data Sources and Connected Accounts; exact retained initializer tags; exact residual aggregate inventory of five executable inline scripts, sixteen external scripts, zero inert script carriers, one native handler, and zero `hx-on`; configured-auth and no-password isolated Chrome covering vendor label/count behavior, confirmations, Plaid open/success/exit/error behavior, both exchange formats, all-entity isolation, denied external traffic, zero unexpected browser errors, and exact cleanup; relevant Python, JavaScript, and JSON syntax; whitespace; dashboard refresh, health, and rendered-state inspection; exact worktree scope; and both preserved files.

Dashboard closeout: record exact implementation and proof, align `state.json`, refresh and health-check, inspect generated state, and keep 4AQ-R durability plus Task 1P.4.2c.8 as separate Ryan gates.

Report point: return exact migrated behavior and residual inventory, controller/data organization, mocked Link proof, focused and full verification, entity and cleanup results, changed paths, local branch state, preserved exclusions, and separate 4AQ-R plus Task 1P.4.2c.8 gates.

Suggested next work block: decide separately whether to authorize exact-scope 4AQ-R durability and release; Task 1P.4.2c.8 remains a later document-family gate.

Result: `data_sources.html` and `plaid.html` now use page-owned template-free `data-sources.js` and `plaid.js`, delegated controls, non-script order-date data, and inert endpoint attributes while retaining both exact Plaid initializer tags. Vendor switching, preview counting, confirmations, both Link flows, exit/error reset behavior, and distinct form-versus-JSON exchange payloads passed focused request/rendered proof plus configured-auth/no-password isolated Chrome with fake configuration, monkeypatched Plaid functions, exact initializer interception, denied external traffic, temporary synthetic all-entity data, zero unexpected browser errors, and exact cleanup. Residual tracked inventory is five executable inline scripts, sixteen external executable scripts, zero inert script carriers, one native handler, and zero `hx-on`. A pre-existing empty-vendor aggregation edge was isolated in the synthetic fixture without changing excluded route/query logic. No style, CSP policy/header/enforcement, live, GitHub, deployment, downstream, protected-data, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-23-plaid-entry-page-execution-4aq.md`.

### Confirmed Work Block 4AP: Payroll Page Execution

Status: complete and locally verified.

Parent task: Phase 4 Task 1P.4.2c.6 plus only its focused Task 2 regression slice.

Included: move the one executable inline script and nine native handlers from `payroll.html` into page-owned template-free `payroll.js`, delegated declarative controls, and non-script inert role-color data; preserve BFM-only access, add/edit/detail, spending-period, new-role, deletion-confirmation, modal, scrim, Escape, Enter, and Space workflows; add focused source/rendered and configured-auth/no-password isolated-browser proof; reconcile the CSP inventory and sanitized evidence; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.2c.7-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route, import, database-query, financial, product, style, CSP-header/nonce/enforcement, authentication, CSRF, Plaid, dependency, or service-worker changes; credentials; protected data; real databases; retained uploads; external or live access; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Payroll is one BFM-only page/controller and synthetic fixture family with a single source, interaction matrix, protected-boundary review, and verification path. Plaid and standalone/error documents require different integration, authentication, and CSP-exception proof.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, CSP inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion, product choice, publication, live action, and recovery beyond the confirmed boundary.

Runner path: write and verify the active command-center state, create `codex/csp-payroll`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/payroll.html`; new `web/static/payroll.js`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. No route, CSS, database, dependency, or deployment file is expected to change.

Defaults: use a page-owned template-free controller with delegated `data-*` actions; carry role colors through non-script inert markup; preserve current runtime-style behavior for Task 1P.4.3a; keep both HTMX execution switches false; use temporary synthetic all-entity data in both auth modes with localhost-only browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; and keep durability local-only.

Stop conditions: parity requires route, import, database-query, financial, product, style-policy, CSP-enforcement, authentication, Plaid, dependency, protected/live, destructive, or later-task work; a pre-existing payroll defect makes parity ambiguous; verification changes the plan; exact cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final full smoke; source and rendered payroll zero-execution assertions; exact residual aggregate inventory of eight executable inline scripts, fourteen external scripts, zero inert script carriers, seven native handlers, and zero `hx-on`; configured-auth and no-password isolated Chrome covering BFM-only access, add/show/cancel, row mouse/keyboard detail, detail rendering/edit target, modal/scrim/Escape closure, spending-period refresh, new-role visibility, deletion confirmation, Personal/LL denial, denied external traffic, zero unexpected browser errors, and exact cleanup; relevant Python, JavaScript, and JSON syntax; whitespace; dashboard refresh, health, and rendered-state inspection; exact worktree scope; and both preserved files.

Dashboard closeout: record exact implementation and proof, align `state.json`, refresh and health-check, inspect generated state, and keep 4AP-R durability plus Task 1P.4.2c.7 as separate Ryan gates.

Report point: return exact migrated behavior and residual inventory, controller/data organization, focused and full verification, entity-boundary and cleanup results, changed paths, local branch state, preserved exclusions, and separate 4AP-R plus Task 1P.4.2c.7 gates.

Suggested next work block: decide separately whether to authorize exact-scope 4AP-R durability and release; Task 1P.4.2c.7 still requires its own fresh proposal.

Result: `payroll.html` loads page-owned template-free `payroll.js`, uses delegated declarative controls, carries role colors in a non-script inert template, and contains zero executable inline scripts, native handlers, or `hx-on`. The BFM-only add/detail/edit/delete-target, pay-history/paycheck, spending-period, import-role, confirmation, modal/scrim/Escape, Enter, and Space matrix passes; Personal and LL remain denied before payroll execution. The previously nested edit/delete forms are valid sibling forms, and fetched detail values use DOM text nodes without route or product-policy changes. Residual inventory is eight inline executable scripts, fourteen external assets, zero inert script carriers, seven native handlers, and zero `hx-on`; both HTMX execution switches remain false. Baseline and final full smoke, configured-auth/no-password isolated Chrome, exact temporary database/upload/browser cleanup, syntax, JSON, whitespace, dashboard, scope, and preserved-file checks pass. No commit, push, PR, merge, publication, deployment, protected/live access, route/import/query/financial/product/style/CSP-enforcement/authentication/Plaid/dependency mutation, or preserved-file overlap occurred. Evidence: `command-center/logs/2026-07-23-payroll-page-execution-4ap.md`.

### Confirmed Work Block 4AP-R: Payroll Page Durability And Release

Status: complete.

Parent task: Phase 4 Task 1P.4.2c.6-R for the exact verified 4AP source set only.

Included: explicit staging of the exact verified 4AP application, controller, maintained-test, CSP contract, evidence, and Runway OS paths; one source commit on `codex/csp-payroll`; a clean fast-forward of local `main`; direct push to `origin/main` without force or PR; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; exact source-SHA verification; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.2c.7 and every later task; every new application, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, Plaid, route, database-query, or financial mutation beyond the verified 4AP set; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: 4AP is already bounded and fully verified. One source commit, one automatic deployment observation, one credential-free health check, and one non-deploying sanitized closeout make durability and live consequence explicit without reopening implementation.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only automatic-deployment observation, credential-free health, and Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and Task 1P.4.2c.7 decision.

Runner path: refresh active release state; rerun exact release verification; explicitly stage and commit the verified 4AP paths on `codex/csp-payroll`; require local and remote `main` to equal the known base; fast-forward local `main`; push directly without force; inspect the automatic Fly run for the exact source SHA; request only credential-free production `/health`; then write, verify, commit with `[skip actions]`, and push the sanitized command-center closeout.

Expected surfaces: the exact verified 4AP source set only for the source commit; then `command-center/decisions.md`, `command-center/now.md`, `command-center/roadmap.md`, `command-center/state.json`, generated `command-center/index.html`, and a new sanitized 4AP-R evidence log for closeout.

Defaults: explicit-path staging; no PR; no force; no stash/reset; preserve both untracked files; one automatic Fly deployment only; no manual workflow dispatch, retry, Fly command, authenticated production route, credential use, protected data, real database, or downstream action; `[skip actions]` on the command-center-only closeout.

Stop conditions: changed or staged paths differ from the exact contract; a protected-path or high-confidence sensitive addition appears; maintained verification fails; either preserved file overlaps; local or remote `main` diverges from the known base; fast-forward is not clean; push is rejected; the automatic deployment fails or requires mutation; the workflow head SHA differs; credential-free production health is not HTTP 200 with the expected sanitized response; or recovery exceeds clean fast-forward and read-only diagnosis.

Verification: exact changed and staged sets; protected-boundary and high-confidence sensitive-addition scans; full synthetic smoke; configured-auth and no-password isolated Chrome; Python and JavaScript syntax; JSON; whitespace; dashboard refresh/health/generated state; commit contents; clean fast-forward and ancestry; exact local/remote/source SHA; automatic Fly workflow and deploy-job result for that SHA; credential-free production `/health`; final local/remote alignment; and both preserved untracked files.

Dashboard closeout: record source commit, automatic workflow run and deploy job, health result, exact boundaries, and next separate Task 1P.4.2c.7 gate; align `state.json`; refresh and health-check; then publish one command-center-only `[skip actions]` closeout commit.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.7 still separately gated.

Suggested next work block: after 4AP-R closes, recheck Task 1P.4.2c.7 before proposing Plaid entry-page work; do not infer implementation authorization.

Result: exact twelve-path source commit `5d331cf2c4a39a71fc8338c0396d85f8b6d449de` is durable on local and remote `main`. Automatic Fly Deploy run `30018319510` and deploy job `89244106601` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with JSON `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, generated-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, Plaid entry-page work, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.7 remains separately gated. Evidence: `command-center/logs/2026-07-23-payroll-page-execution-release-4ap-r.md`.

### Confirmed Work Block 4AO: Subscription Page Execution

Status: complete and locally verified.

Parent task: Phase 4 Task 1P.4.2c.5 plus only its focused Task 2 regression slice.

Included: move the one executable inline script, fifteen native handlers, one runtime `onclick` assignment, and one inert JSON carrier from `subscriptions.html` into a page-owned template-free local controller, delegated declarative controls, and non-script inert data; preserve suggestion, watchlist, detail, charge/payment, timeline, account-info, tips, clipboard, add/dismiss, confirmation, modal, scrim, Escape, Enter, Space, AI-entry, and entity-isolation behavior; add focused source/rendered and configured-auth/no-password isolated-browser proof; reconcile the CSP inventory and sanitized evidence; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.2c.6-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route, database-query, financial, product, or account-information policy changes; style migration; CSP headers, nonces, or enforcement; authentication; CSRF; Plaid; dependencies; service-worker behavior; credentials; protected data; real databases; retained uploads; external or live access; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: the subscription page is one high-interaction controller and inert-data boundary with one synthetic fixture family and one configured-auth/no-password browser matrix. Payroll is BFM-only, Plaid has an integration and CSP-exception boundary, and standalone documents require a different verification family.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, CSP inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion and publication decision.

Runner path: write and verify the active command-center state, create `codex/csp-subscriptions`, implement the exact local slice, run focused and full proof, and close locally before any durability decision.

Expected surfaces: `web/templates/subscriptions.html`; new `web/static/subscriptions.js`; focused maintained smoke and isolated-browser coverage; `command-center/csp-compatibility-contract.md`; sanitized evidence; Runway OS sources; and the generated dashboard. No route, CSS, database, dependency, or deployment file is expected to change.

Defaults: reuse the app-shell AI action; use a page-owned template-free controller with delegated `data-*` actions; carry suggestion data and server-generated endpoints through non-script inert markup; preserve existing runtime-style behavior for the later style task; keep both HTMX execution switches false; use temporary synthetic all-entity data with deterministic local AI and clipboard behavior, localhost-only browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; and keep durability local-only.

Stop conditions: parity requires route, query, financial, product, account-information policy, style-policy, CSP-enforcement, authentication, Plaid, dependency, protected/live, destructive, or later-task work; verification changes the plan; exact temporary cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final full smoke; source and rendered subscriptions zero-execution assertions; exact residual aggregate inventory of nine executable inline scripts, thirteen external scripts, zero inert script carriers, sixteen native handlers, and zero `hx-on`; configured-auth and no-password isolated Chrome covering AI entry, suggestion/watchlist detail, mouse and keyboard operation, charge/payment/timeline/tips rendering, account-info add/delete, clipboard copy, add/dismiss controls, confirmation, modal closure, all-entity isolation, denied external traffic, zero unexpected browser errors, and exact cleanup; relevant Python, JavaScript, and JSON syntax; whitespace; dashboard refresh, health, and rendered-state inspection; exact worktree scope; and both preserved files.

Dashboard closeout: record the exact implementation and proof, align `state.json`, refresh and health-check, inspect generated state, and keep 4AO-R durability plus Task 1P.4.2c.6 as separate Ryan gates.

Report point: return exact migrated behavior and residual inventory, controller/data organization, focused and full verification, browser and cleanup results, changed paths, local branch state, preserved exclusions, and the separate 4AO-R publication plus Task 1P.4.2c.6 gates.

Suggested next work block: decide separately whether to authorize exact-scope 4AO-R durability and release; Task 1P.4.2c.6 still requires its own fresh proposal.

Result: `subscriptions.html` loads page-owned template-free `subscriptions.js`, carries suggestion data in a non-script inert template, reuses the app-shell AI action, and contains zero executable inline scripts, native handlers, runtime `onclick` assignments, inert script carriers, or `hx-on`. Delegated behavior preserves suggestion/watchlist detail, charges, payment, timeline, account-info add/delete, deterministic tips, clipboard, add/dismiss controls, confirmation, modal/scrim/Escape, Enter/Space, and Personal/BFM/Luxe Legacy isolation. The residual tracked-template inventory is nine inline executable scripts, thirteen external assets, zero inert script carriers, sixteen native handlers, and zero `hx-on`; both HTMX execution switches remain false. Baseline and final full smoke, focused source/rendered proof, configured-auth/no-password isolated Chrome, syntax, JSON, whitespace, dashboard, scope, browser-error/network, exact-cleanup, and preserved-file checks pass. No commit, push, PR, merge, publication, deployment, protected/live access, route/query/financial/product/style/CSP-enforcement/authentication/Plaid/dependency mutation, or preserved-file overlap occurred. Evidence: `command-center/logs/2026-07-23-subscription-page-execution-4ao.md`.

### Confirmed Work Block 4AO-R: Subscription Page Durability And Release

Status: complete.

Parent task: Phase 4 Task 1P.4.2c.5-R for the exact verified 4AO source set only.

Included: explicit staging of the exact verified 4AO application, controller, maintained-test, CSP contract, evidence, and Runway OS paths; one source commit on `codex/csp-subscriptions`; a clean fast-forward of local `main`; direct push to `origin/main` without force or PR; read-only observation of the resulting automatic Fly deployment; credential-free production `/health`; exact source-SHA verification; and one sanitized command-center-only `[skip actions]` closeout commit and push.

Excluded: Task 1P.4.2c.6 and every later task; every new application, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, Plaid, route, database-query, or financial mutation beyond the verified 4AO set; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly authorized commit and direct push to `main`. The exact 4AO source set is already locally verified, and this block adds only the established durability, automatic-release observation, health verification, and sanitized closeout path.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only automatic-deployment observation, credential-free health, and Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and Task 1P.4.2c.6 decision.

Runner path: refresh and verify the active release state; stage only the exact 4AO path set; commit once on `codex/csp-subscriptions`; fetch and require clean local/remote alignment; fast-forward local `main`; push directly without force; observe only the automatic workflow; verify credential-free health and exact deployed source SHA; write one sanitized closeout; refresh and health-check; commit `[skip actions]`; and push the closeout.

Expected surfaces: the exact eleven-path verified 4AO set for the source commit; then only `command-center/decisions.md`, `command-center/index.html`, `command-center/logs/2026-07-23-subscription-page-execution-release-4ao-r.md`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json` for the sanitized closeout. The two preserved untracked files remain untouched.

Defaults: explicit-path staging; no PR; no force push; no manual workflow action; no credential use; no authenticated production page; no non-automatic Fly mutation; no new product change; no protected data; preserve exact 4AO behavior, inventory, tests, and both untracked files.

Stop conditions: any unexpected path or sensitive addition; protected-boundary risk; failed maintained verification; excluded staging; local or remote `main` divergence; push rejection; automatic deployment failure requiring mutation; credential-free health failure; source-SHA mismatch; preserved-file overlap; or recovery beyond a clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-boundary and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python and JavaScript syntax; JSON; whitespace; dashboard refresh, health, and generated-state inspection; commit contents; ancestry; exact remote SHA; automatic workflow result; credential-free production `/health`; final local/remote alignment; and both preserved untracked files.

Dashboard closeout: record the source commit, automatic workflow run and deploy job, health result, exact boundaries, and next separate Task 1P.4.2c.6 gate; align `state.json`; refresh and health-check; then publish one command-center-only `[skip actions]` closeout commit.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.6 still separately gated.

Suggested next work block: after 4AO-R closes, recheck Task 1P.4.2c.6 before proposing payroll-page work; do not infer implementation authorization.

Result: exact eleven-path source commit `55ec28abaeee8abfe300bcd1ab2489fb393aee54` is durable on local and remote `main`. Automatic Fly Deploy run `30015264505` and deploy job `89233474666` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, generated-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, payroll-page work, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.6 remains separately gated. Evidence: `command-center/logs/2026-07-23-subscription-page-execution-release-4ao-r.md`.

### Confirmed Work Block 4AN: Weekly And Waterfall Execution

Status: complete and locally verified

Parent task: Phase 4 Task 1P.4.2c.4 plus only its focused Task 2 regression slice.

Included: move Weekly AI entry to the existing maintained app-shell action; move Waterfall's one executable inline script and remaining native handlers into a page-owned local controller; preserve actual/target switching, breakdown controls, revenue/take-home modes, target and tax Enter-key handling, tooltips, click-away closure, bar animations, URL semantics, AI entry, and entity boundaries; add focused source/rendered and configured-auth/no-password isolated-browser proof; reconcile the CSP inventory and sanitized evidence; and close Runway OS locally after verification.

Excluded: Tasks 1P.4.2c.5-1P.4.4; Tasks 1P.6-1P.7; the remainder of Task 2; Tasks 3-4; route calculations; financial logic; database queries; style migration; CSP headers, nonces, or enforcement; authentication; CSRF; Plaid; dependencies; credentials; protected data; real databases; retained uploads; external or live access; GitHub durability; publication; deployment; workflows; downstream access or writes; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Weekly and Waterfall are the existing planning-consumer route cluster, share the same entity and synthetic-fixture boundaries, and can be proven in one browser matrix. Weekly needs only the maintained app-shell AI seam, while Waterfall needs one page-owned controller. Subscriptions has a separate high-interaction modal, suggestion, clipboard, and inert-data boundary and remains later.

Owner and recommended agent: Codex Desktop in the current task without delegation or second opinion. Codex owns implementation, synthetic and browser proof, exact cleanup, CSP inventory reconciliation, dashboard currency, and final intake. Ryan owns every expansion and publication decision.

Defaults: reuse `app-shell.js` for both AI buttons without creating `weekly.js`; create template-free `waterfall.js` with delegated `data-*` actions and inert controller state; preserve current URL, keyboard, tooltip, animation, and runtime-style behavior exactly; keep both HTMX execution switches false; use temporary synthetic Personal, BFM, and Luxe Legacy data with localhost-only browser state, denied non-localhost requests, zero unexpected console/page errors, and exact cleanup; preserve both unrelated untracked files; keep durability local-only.

Stop conditions: parity requires route, database-query, financial, product-direction, style-policy, CSP-enforcement, authentication, Plaid, dependency, protected/live, destructive, or later-task work; verification changes the plan; exact temporary cleanup fails; command-center checks fail; scope expands; or either preserved untracked file overlaps.

Verification: baseline and final full smoke; source and rendered Weekly/Waterfall zero-execution assertions; exact residual aggregate inventory of ten executable inline scripts, twelve external scripts, one inert JSON carrier, thirty-one native handlers, and zero `hx-on`; configured-auth and no-password isolated Chrome covering AI entry, actual/target switching, breakdowns, mode, target and tax Enter behavior, tooltips, outside-click closure, animation, entity boundaries, denied external traffic, zero unexpected browser errors, and exact cleanup; relevant Python, JavaScript, and JSON syntax; whitespace; dashboard refresh, health, and rendered-state inspection; exact worktree scope; and preserved files.

Report point: return exact migrated behavior and inventory, controller organization, focused and full verification, browser and cleanup results, changed paths, local branch state, preserved exclusions, and the separate 4AN-R publication plus Task 1P.4.2c.5 gates.

Suggested next work block: after 4AN closes locally, decide separately whether to authorize exact-scope 4AN-R durability and release; Task 1P.4.2c.5 still requires its own fresh proposal.

Result: Weekly and Waterfall AI entry now uses the maintained app-shell action, and page-owned template-free `waterfall.js` preserves actual/target switching, nested breakdowns, revenue/take-home mode, target and tax Enter handling, tooltips, click-away closure, bar animation, URL semantics, and Personal/BFM versus Luxe Legacy boundaries. Both included templates contain zero executable inline scripts, native handlers, or `hx-on`; the residual tracked-template inventory is ten executable inline scripts, twelve external scripts, one inert JSON carrier, thirty-one native handlers, and zero `hx-on`. Baseline and final full smoke plus configured-auth/no-password isolated Chrome, focused source/rendered coverage, syntax, JSON, whitespace, dashboard, scope, and exact-cleanup checks pass. The result remains local-only on `codex/csp-weekly-waterfall`; no commit, push, PR, merge, publication, deployment, protected access, credential use, real database, or live action occurred. Evidence: `command-center/logs/2026-07-23-weekly-waterfall-execution-4an.md`.

### Confirmed Work Block 4AN-R: Weekly And Waterfall Durability And Release

Status: complete, durable, automatically deployed, and credential-free production health verified.

Parent task: Phase 4 Task 1P.4.2c.4-R for the exact verified 4AN source set only.

Included: stage the exact verified 4AN application, controller, maintained-test, CSP contract, evidence, and Runway OS source paths; create one intentional source commit on `codex/csp-weekly-waterfall`; fast-forward local `main`; push directly to `origin/main` without force or PR; observe the resulting automatic Fly deployment read-only; verify credential-free production `/health`; verify the exact source SHA is durable; create one sanitized command-center-only `[skip actions]` closeout commit; push it to `main`; and prove final local/remote alignment.

Excluded: Task 1P.4.2c.5 and every later task; every new application, template, JavaScript, CSS, test, dependency, runtime, authentication, header, worker, manifest, Plaid, route, database-query, or financial mutation beyond the verified 4AN set; credentials; protected data; real databases; retained uploads; authenticated production pages; manual workflow actions; workflow edits; non-automatic Fly mutations; downstream access or writes; PR creation; force push; broader recovery; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

Why this grouping: Ryan explicitly requested commit and push to `main`. The complete 4AN set is already locally verified, so exact durability, automatic release observation, credential-free health, and sanitized closeout form one bounded publication block without reopening implementation.

Owner and recommended agent: Codex Desktop in the current task without delegation. Codex owns exact staging, Git safety, sensitive-addition and protected-boundary review, direct-main durability, read-only automatic-deployment observation, credential-free health, and Runway OS closeout. Ryan owns every expansion, live mutation, failure recovery, and Task 1P.4.2c.5 decision.

Runner path: source commit on `codex/csp-weekly-waterfall`; clean fast-forward of local `main`; direct push to `origin/main`; automatic-deployment observation; credential-free health; sanitized `[skip actions]` closeout on `main`.

Expected surfaces: the exact verified 4AN paths for the source commit; then only `command-center/now.md`, `command-center/roadmap.md`, `command-center/decisions.md`, `command-center/state.json`, generated `command-center/index.html`, and one sanitized 4AN-R evidence log for closeout.

Defaults: explicit-path staging only; no PR or force push; no new application mutation; preserve the verified controller, templates, tests, inventory, and false HTMX execution switches; observe only the automatic `main` deployment and credential-free health; use `[skip actions]` only for the final command-center closeout; preserve both unrelated untracked files.

Stop conditions: unexpected or excluded path; sensitive addition or protected-data risk; failed verification; local or remote `main` divergence; excluded staging; push rejection; automatic deployment or health failure that requires mutation or broader diagnosis; workflow behavior inconsistent with the expected automatic release; preserved-file overlap; or recovery beyond clean fast-forward and read-only diagnosis.

Verification: exact changed and staged paths; protected-path and high-confidence sensitive-addition scans; full smoke; configured-auth/no-password isolated Chrome; Python/JavaScript/JSON syntax; whitespace; dashboard refresh, health, and rendered state; commit content; clean fast-forward; `main` ancestry; exact remote SHA; automatic deployment run/job result; credential-free production `/health`; final tracked cleanliness; and both preserved untracked files.

Dashboard closeout: after source durability and release proof, update human-readable sources with exact commit/run/health results, align `state.json`, refresh and health-check, inspect generated state, commit only sanitized command-center paths with `[skip actions]`, push, and verify final local/remote alignment without triggering another deployment.

Report point: return source and closeout SHAs, exact published paths, automatic deployment and health results, final alignment, preserved exclusions, and Task 1P.4.2c.5 still separately gated.

Suggested next work block: after 4AN-R closes, recheck Task 1P.4.2c.5 before proposing a separate subscription-page block; do not infer implementation authorization.

Result: exact thirteen-path source commit `4fc47359de1f02a78dde95d90b34292fa4ea1542` is durable on local and remote `main`. Automatic Fly Deploy run `30011582629` and deploy job `89220774553` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, rendered-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, subscription-page work, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.5 remains separately gated. Evidence: `command-center/logs/2026-07-23-weekly-waterfall-execution-release-4an-r.md`.

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

Status: complete, durable, automatically deployed, and credential-free production health verified.

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

Result: exact twelve-path source commit `f6505aa1860ad3219231effb26c53e23fa7ffe0b` is durable on local and remote `main`. Automatic Fly Deploy run `29994452861` and deploy job `89164689293` passed every reported step for the exact source SHA, and credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`. Exact-path, staged-set, protected-boundary, sensitive-addition, maintained verification, syntax, dashboard, rendered-state, ancestry, remote-alignment, automatic-release, production-health, and preserved-file checks passed. No PR, force push, manual workflow action, non-automatic Fly mutation, authenticated production page, credential, protected data, real database, downstream action, Weekly/Waterfall work, broader recovery, or preserved-file mutation occurred. Task 1P.4.2c.4 remains separately gated. Evidence: `command-center/logs/2026-07-23-short-term-planning-execution-release-4am-r.md`.

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

Status: active at 50%; Task 4.1 and 5G-R2 are complete; Task 4.2 and confirmed 5H-R are active for exact Ask and operator package branch durability plus hosted draft-PR review while provider verification, merge, deployment, production, final closeout, and parked Task 2 work remain separate

Goal: make the product understandable, maintainable, and easy to re-enter after the critical repairs are complete.

- **Task 1: Review desktop, mobile, and installed-PWA workflows for usability and accessibility.** Status: done locally through 5A and 5B.
  - **Task 1.1: Freeze the workflow-review contract and representative journey matrix.** Status: done locally in 5A; the bounded J1-J5 matrix, heuristics, evidence labels, privacy boundary, and stop conditions are recorded in `command-center/phase-5-workflow-review-contract.md`.
  - **Task 1.2: Capture the synthetic desktop, mobile, and installed-PWA usability baseline.** Status: done locally in 5A. Full synthetic smoke and the complete maintained installed-Chrome suite passed; the J1-J5 matrix, seven provisional friction clusters, strengths, limitations, sanitized artifacts, and exact cleanup are recorded in `command-center/phase-5-usability-baseline.md`.
  - **Task 1.3: Obtain an independent design and usability critique of the focused evidence packet.** Status: done locally in 5B. The verified return is preserved unchanged with its original ZIP, complete Markdown critique, manifest, three inspected synthetic annotations, and exact hashes.
  - **Task 1.4: Reconcile findings and recommend the first Task 2 polish block.** Status: done locally in 5B. Every 5A and reviewer finding is classified in `command-center/phase-5-usability-findings-intake.md`; material product and data-handling choices remain Ryan decisions.
- **Task 2: Polish high-friction journeys without widening financial or authentication risk.** Status: active umbrella; decomposed into Tasks 2.1-2.8 after 5B intake.
  - **Task 2.1: Repair synthetic demo fidelity.** Status: done locally through 5C. Personal/BFM use the exact maintained category domains, Personal has one debt-payoff and one savings goal, repeated seeds match, focused coverage passes, and rendered review no longer opens on orphan drift or missing goals.
  - **Task 2.2: Improve first-use and denied-state explanation.** Status: parked by Ryan until further notice together with Luxe Legacy setup and the associated 5D path. The combined Short-Term Planning empty-state action and Luxe Legacy empty/denied guidance remain unimplemented; existing Luxe Legacy isolation and fail-closed behavior stay unchanged.
  - **Task 2.3: Repair phone transaction density and entity context.** Status: done locally through 5E. Personal, BFM, and LL now use complete non-scrolling phone rows and a read-only shared mobile entity marker while preserving current fields, sort, copy, pagination, filters, HTMX, edit, exact-768/desktop table, drawer, and entity behavior.
  - **Task 2.4: Revise the recurring-charge surface.** Status: done through 5G/5G-RS and branch-durable plus hosted-verified through 5G-R on open draft PR #90 after successful recovery, application-readiness proof, complete synthetic and rendered verification with no correction, Ryan's exact closeout-dashboard attestation, and two clean automatic PR heads. Merge and production release remain separate.
  - **Task 2.5: Clarify Ask Opus purpose and privacy.** Status: done locally through 5H-A/5H-B. Seven exact page contexts are active-entity and summary-first; unknown/General/Weekly/Waterfall fail before data or provider work; server transcript behavior is removed; Clear is browser-local; Ask-specific provider controls require ZDR and deny data-collecting providers; truthful disclosure and complete synthetic/browser verification pass. Durability, provider-account verification, publication, and production remain separate.
  - **Task 2.6: Reassess dashboard explanation and density.** Status: done locally through 5F. Categories with spending or budgets remain primary, only zero-spend/no-budget categories begin behind an exact-count accessible disclosure, budget context is textual, and the orphan notice is user-facing without changing financial or category semantics.
  - **Task 2.7: Resolve connections and capability discovery.** Status: parked. Revisit Data Sources, Connected Accounts, To Do entry points, and capability discovery as one later information-architecture slice.
  - **Task 2.8: Verify and improve offline recovery feedback.** Status: parked. Verify cache truth and retry feedback before making any data-safety claim.
- **Task 3: Finalize operator runbooks, current documentation, monitoring decisions, and release evidence.** Status: done locally through 5I-5L; operator re-entry, synthetic validation, release evidence, maintained documentation, monitoring decisions, and the compact handoff are complete without granting release or protected authority.
  - **Task 3.1: Inventory safe operator re-entry paths and protected boundaries.** Status: done locally through completed 5I; the source-linked inventory covers authority, setup, verification, deployment, synchronization, recovery, AI, data, durability, destructive utilities, and stop boundaries.
  - **Task 3.2: Draft the consolidated operator runbook and monitoring/maintenance matrix.** Status: done locally through completed 5I; the runbook and matrix distinguish source-verified, externally unverified, protected, and separately authorized state.
  - **Task 3.3: Prove the runbook with a local synthetic re-entry drill.** Status: done locally through completed 5J after first-pass workflow-safety, full smoke, complete both-auth installed-browser, denied-network, preservation, exact-cleanup, and automated dashboard-closeout verification.
  - **Task 3.4: Reconcile Phase 5 release evidence, durability, and unresolved gates.** Status: done locally through 5K. The exact map distinguishes PR #89's merged/deployed historical production evidence, PR #90's open-draft hosted verification, local-only Ask/operator work, current-runtime unknowns, protected provider settings, and every pending gate.
  - **Task 3.5: Finalize maintained documentation and the release handoff.** Status: done locally through completed 5L with source-linked startup/configuration/sync-contract/time-label corrections, reconciled runbook/matrix, and one compact operator/release handoff.
- **Task 4: Close the roadmap with target-repo and parent-project durability.** Status: active umbrella; execution remains split across Tasks 4.1-4.5.
  - **Task 4.1 (`P5-T41`): Release Recurring Review from verified draft PR #90.** Status: done through 5G-R2; merged as `d81ed7078e741a0c7613e7898312ce01cd359f45`, automatically deployed once, and health-verified.
  - **Task 4.2 (`P5-T42`): Preserve Ask Opus and Task 3 artifacts durably.** Status: active through confirmed 5H-R; preserve the accepted dirty-worktree boundaries and publish only the exact verified package to a retained draft PR.
  - **Task 4.3 (`P5-T43`): Verify protected OpenRouter account controls.** Status: planned and protected; requires a separate target-specific authorization.
  - **Task 4.4 (`P5-T44`): Release Ask Opus and its operator handoff package.** Status: planned; durability, hosted review, merge, deployment, and health evidence must be bounded from provider verification.
  - **Task 4.5 (`P5-T45`): Complete final target-repo and parent-project durability closeout.** Status: planned; only after prior Task 4 release and evidence gates are resolved.

### Confirmed Work Block 5H-R: Ask and Operator Package Branch Durability and Hosted Review

Status: closeout publication in progress after a clean candidate draft-PR pass; exact final-head CI remains required.

Included: Task 4.2 (`P5-T42`) only. Preserve the accepted dirty worktree, empty real index, and three unrelated files; revalidate remote `main` at `d81ed7078e741a0c7613e7898312ce01cd359f45`; fetch only that exact ref; prove it is a tree-identical descendant of local head `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`; fast-forward `codex/ask-opus-privacy` without changing working files; revalidate the exact 31-path candidate consisting of 19 tracked modifications and 12 intended untracked Ask, operator, monitoring, handoff, and evidence artifacts; run the complete local verification contract; explicitly stage only those paths; commit and non-force push the new branch; open one draft PR targeting `main`; observe automatic core-then-browser Synthetic CI; publish one exact eight-path sanitized closeout commit; require final-head CI; prove zero Fly deployment; retain the branch; leave the PR open, draft, and unmerged; close Task 4.2 locally; and stop.

Excluded: Tasks 4.3-4.5; OpenRouter or provider-account access; further product, design, test, workflow, dependency, runtime, configuration, authentication, financial, category, reporting, database, or defect work; PR ready transition; merge; deployment; production or health request; manual workflow dispatch, rerun, cancellation, or repair; push to `main`; rebase; stash; cherry-pick; force push; conflict resolution; branch deletion; Plaid; Fly administration; credentials; protected or real data; parked Tasks 2.2, 2.7, and 2.8; parent-project updates; delegation; second opinion; the duplicate 4AU log; `command-center/now 2.md`; and `scripts/sync_prod_to_local.sh`.

Why this grouping: the Ask implementation, maintained tests, privacy contract, operator runbook, monitoring matrix, release evidence, handoff, and Runway OS closeout are one already-verified local package with one durability outcome, one branch, one risk class, and one hosted verification path. Provider verification and production release use different protected and live-action evidence and remain later tasks.

Owner and recommended agent: Codex Desktop without delegation or second opinion. This block is exact Git history orchestration, path-controlled publication, hosted verification, dirty-worktree preservation, and Runway OS stewardship rather than subjective design work.

Runner path: record and verify active state; capture exact branch/head/status/index and preservation hashes; revalidate and fetch exact remote main; prove ancestry and identical trees; fast-forward without changing the worktree; run complete local verification; stage only the exact 31 paths; commit and push; open a draft PR; verify candidate-head CI and zero deployment; publish only the exact eight-path sanitized closeout; verify final-head CI and zero deployment; close locally; and stop.

Expected surfaces: the exact 31-path local candidate; `codex/ask-opus-privacy`; one new draft PR targeting `main`; automatic Synthetic CI only; and an exact eight-path closeout consisting of `now.md`, `roadmap.md`, `decisions.md`, `state.json`, generated `index.html`, the release-evidence map, the release handoff, and one new sanitized 5H-R log.

Defaults: two commits, candidate then closeout; normal non-force push; draft PR retained and unmerged; no CI rerun; no human dashboard checkpoint; stop rather than repair any conflict or unexpected failure.

Stop conditions: remote `main` drift; ancestry or tree-identity mismatch; any worktree/index/preserved-hash change from the guarded fast-forward; candidate path-count or content drift; failed local verification; excluded or sensitive staged content; non-fast-forward push; unexpected existing branch or PR; PR base/head/diff/mergeability drift; failed, missing, delayed, reordered, or annotated hosted check; any Fly deployment; cleanup residue; command-center failure; or need for repair, rerun, protected access, or expansion.

Verification and report point: exact local and hosted refs; identical-tree fast-forward; exact 31 paths and three exclusions; workflow safety, smoke, browser, syntax, JSON, dashboard, whitespace, sensitive, cleanup, index, and preservation checks; commit ancestry; draft PR base/head/diff; candidate and final CI jobs/steps/annotations; zero deployment; retained branch; empty index; automated dashboard closeout; and the separately gated Task 4.3 decision.

Candidate result: guarded fast-forward to exact post-PR-#90 `main` preserved all working files and exclusions; the complete local verification contract passed; exact 31-path candidate commit `f7482a95e754160905a79ec0130ef8faf0a48784` was pushed normally; draft PR #91 targets `main`; Synthetic CI run `30329875129` passed core job `90182588590` then browser job `90182722250` with every step successful and zero annotations; and the candidate caused zero Fly deployments. The exact eight-path closeout and final-head hosted gate remain.

### Confirmed Work Block 5G-R2: Recurring Review Exact-Head Production Release

Status: done; exact merge, one automatic deployment, credential-free health, branch retention, and local preservation verified.

Included: Task 4.1 (`P5-T41`) only. Preserve the accepted dirty local worktree, `codex/ask-opus-privacy` at `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`, the empty real index, and the three unrelated untracked files. Revalidate remote `main` at `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`; PR #90 open, draft, mergeable, based on `main`, and headed by the exact verified SHA; require exact-head Synthetic CI success with zero annotations; mark the PR ready; merge with a normal merge commit without bypass or branch deletion; verify exact merge parents; observe only the resulting automatic exact-merge-SHA Fly Deploy; require every job and step successful with zero annotations; make one credential-free production `/health` request; record sanitized local evidence; close Task 4.1; make Task 4.2 the next Ryan-owned planning task; and stop.

Excluded: Tasks 4.2-4.5; Ask Opus durability, protected provider verification, or release; parked Tasks 2.2, 2.7, and 2.8; local fetch, checkout, rebase, staging, commit, or push; publication of the accepted dirty worktree; manual workflow dispatch, rerun, cancellation, repair, or deployment; Fly CLI, SSH, console, secrets, logs, restart, rollback, or database operations; Plaid; authenticated production pages; protected or real financial data; force push; conflict resolution; feature-branch deletion; parent-project updates; delegation; and second opinion.

Defaults: use the successful exact-head CI unless an automatic ready-for-review check appears; never rerun manually; retain the feature branch; stop on drift rather than adapt; permit exactly one automatic deployment and one minimal credential-free health request; leave all local closeout changes unstaged and uncommitted; and verify the dashboard automatically without Ryan visual attestation.

Stop conditions: any unexpected local branch/head/index/preserved-file change; remote-main, PR number/base/head/state/draft/mergeability, exact-check, job, step, or annotation mismatch; merge SHA or parent mismatch; missing, duplicated, failed, cancelled, or unrelated deployment; non-successful health response; need for credentials, protected data, manual action, rollback, logs, repair, or expansion; or failed JSON, dashboard, health, currentness, whitespace, sensitive-value, preservation, or scope verification.

Verification and report point: return the exact preflight refs and PR state, exact-head check run/jobs/annotations, ready transition, merge SHA and parents, exact automatic deployment run/jobs/steps/annotations, one health result, proof of no second deployment, retained feature branch, unchanged local baseline/index/preserved files, sanitized local evidence paths, automated dashboard closeout, and the separately gated Task 4.2 next decision.

Result: remote `main` and PR #90 matched the frozen contract; exact-head Synthetic CI run `30279361029` passed both jobs and all steps with zero annotations; PR #90 was marked ready and merged normally as `d81ed7078e741a0c7613e7898312ce01cd359f45` with the exact expected parents; automatic Fly Deploy run `30327566484` and job `90176026100` passed every step with zero annotations; exactly one deploy exists for the merge; one credential-free `/health` request returned HTTP 200 and `status: ok`; the feature branch remains retained; and the accepted local dirty worktree, empty index, and preserved unrelated files remained unchanged. Task 4.1 is complete and Task 4.2 is the next planning gate. Evidence: `command-center/logs/2026-07-27-recurring-review-production-release-5g-r2.md`.

### Confirmed Work Block 5L: Maintained Documentation and Compact Release Handoff

Status: done locally; Task 4 and every release/provider gate remain separate.

Included: Task 3.5 (`P5-T35`) only. Preserve the exact dirty-worktree baseline; add a prominent README warning that ordinary local startup resolves `DATA_DIR` to `./local_state` by default and can initialize databases, create sidecars, apply migrations, and synchronize categories; align `.env.example` with operator-configurable variables documented in README using placeholders only; correct the stale “proposed” lifecycle label in `sync-entry-coordination-contract.md` to reflect verified 4L/4L-R implementation and release without rewriting its historical body; replace the dashboard timestamp formatter's year-round `CST` label with seasonally accurate Central Time and prove winter/summer behavior; reconcile the operator runbook and monitoring matrix; create one compact source-linked Phase 5 release handoff and one sanitized 5L log; close Runway OS automatically; and stop.

Excluded: Task 4 (`P5-T4`); 5G-R2; 5H-R; provider-account verification; Tasks 2.2, 2.7, and 2.8; application behavior; maintained product tests; workflows; dependencies; database migrations; authentication; Plaid, Fly, OpenRouter, demo, production, or protected-data access; external-currentness queries; monitoring automation or invented cadences; staging, commit, push, PR mutation, workflow action, merge, deployment, rollback, parent updates, delegation, second opinion, and the three preserved unrelated files.

Why this grouping: the README, configuration example, historical sync-contract label, command-center time label, operator runbook, monitoring matrix, and compact handoff are all local source-linked corrections discovered by Tasks 3.1-3.4. They share one factual documentation outcome, one low-risk local boundary, and one verification path. Provider verification, publication, release, and Task 4 require different authority and evidence.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The work requires cross-file factual reconciliation, safe configuration examples, a small command-center formatter correction, preservation of the accepted dirty worktree, and Runway OS stewardship.

Runner path: record and refresh active 5L; preserve branch/head, empty index, accepted dirty paths, product/test hashes, documentation-input hashes, PR #90 boundary, and unrelated files; apply only the listed corrections; create the handoff and log; verify source links, configuration coverage, winter/summer timestamp behavior, evidence labels, exact paths, and Runway OS; close Task 3.5 locally; and stop.

Expected paths: `README.md`; `.env.example`; `command-center/sync-entry-coordination-contract.md`; `command-center/scripts/refresh-dashboard.js`; `command-center/operator-runbook.md`; `command-center/operations-monitoring-matrix.md`; new `command-center/phase-5-release-handoff.md`; new `command-center/logs/2026-07-27-maintained-documentation-release-handoff-5l.md`; `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`. The 5K evidence map and tracked implementation are read-only inputs unless one narrow handoff cross-link is necessary.

Defaults: `.env.example` lists operator-configurable variables documented by README but not internal `TESTING` or infrastructure-provided `FLY_APP_NAME`; all example values remain blank or safe development placeholders; the sync contract's historical body remains intact; Central timestamps use `CST` in winter and `CDT` in summer; missing monitor cadences remain explicit decisions and are not invented; no external currentness is queried; product suites are not rerun unless an unexpected product/test overlap appears; PR #90 remains untouched; and routine dashboard closeout is automated.

Stop conditions: a correction requires application, maintained-test, workflow, dependency, database, authentication, provider, or product behavior changes; configuration meaning cannot be resolved from tracked source without credentials or live access; a statement would promote historical evidence into a current external claim; release sequencing requires a new Ryan decision; an unexpected file, protected value, baseline drift, staging change, or unrelated-file change appears; or configuration-inventory, timestamp, link, JSON, dashboard, health, currentness, whitespace, sensitive-value, preservation, or exact-scope verification fails.

Verification: exact branch/head/status/empty-index and captured hashes; README/source/configuration-name consistency; placeholder-only `.env.example`; source-linked 4L/4L-R lifecycle correction; deterministic winter/summer Central timestamp proof; complete local-link and handoff-gate review; high-confidence sensitive-value scan; JSON; automated dashboard refresh/generated-state equality/health; exactly one current task; generated markers; relevant diff; `git diff --check`; and exact changed paths.

Dashboard closeout: on a supported result, mark Task 3.5 and 5L complete locally, keep Phase 5 active at 50%, make Task 4 the sole current Ryan-owned planning gate, retain every release/provider/live boundary, and use automated dashboard closeout without Ryan visual attestation.

Report point: return the exact documentation corrections, configuration inventory, timestamp proof, handoff contents, remaining monitoring decisions, release-package boundaries, changed paths, preservation, verification, and the next separately authorized release decision.

Suggested next work block: 5G-R2 for exact-head Recurring Review merge and production release only after a fresh proposal and confirmation. Ask Opus durability and protected provider verification remain a separate path.

Result: README now prominently states that ordinary startup can use and initialize or migrate the resolved `DATA_DIR`; `.env.example` exactly covers the twelve operator-configurable variables documented in README without real values; the sync-entry contract lifecycle label matches verified 4L-4L-R evidence while its historical body remains unchanged; and the dashboard formatter passes deterministic winter `CST` and summer `CDT` fixtures. The operator runbook and monitoring matrix now distinguish corrected documentation from unresolved monitoring and protected-currentness decisions. `command-center/phase-5-release-handoff.md` separates released PR #89 work, hosted-only PR #90 work, local-only Ask/operator work, protected provider verification, monitoring decisions, recommended release order, and every remaining gate. Local links, configuration inventory, timestamp behavior, sensitive-value, JSON, dashboard, health, currentness, whitespace, scope, branch/head, empty-index, product/test hash, and preserved-file checks passed. No product/test/workflow/database/provider/external/publication/merge/deployment/production/Task 4 action or invented cadence occurred. Task 3 and Task 3.5 are complete locally; Task 4 becomes the sole current Ryan-owned planning gate.

### Confirmed Work Block 5K: Phase 5 Release-Evidence and Unresolved-Gates Reconciliation

Status: done locally; Task 3.5 remains separately gated.

Included: Task 3.4 (`P5-T34`) only. Preserve the exact dirty-worktree baseline; inventory Phase 5 blocks 5A-5J from current Runway OS and sanitized evidence; reconcile local commits, ancestry, branches, and uncommitted paths without fetching or changing refs; query read-only GitHub metadata for current remote `main`, PR #89, PR #90, and exact relevant Synthetic CI and Fly Deploy runs; classify every result as local-only, durable, hosted-verified, merged, deployed, historical production-verified, externally unverified-current, protected, or pending; identify the exact evidence needed to clear each unresolved gate; create one release-evidence map and one sanitized log; update the monitoring matrix evidence row; close Runway OS automatically; and stop.

Excluded: Task 3.5; Tasks 2.2, 2.7, and 2.8; Task 4; product, test, README, workflow, dependency, runtime, configuration, database, or migration changes; provider-account access; OpenRouter, Fly, Plaid, deployed application, demo, production, or health-endpoint access; fetch, checkout, rebase, staging, commit, push, PR mutation, workflow dispatch/rerun/cancellation, merge, deployment, rollback, parent updates, delegation, and second opinion.

Why this grouping: local Git provenance, sanitized evidence, GitHub refs, PRs, and exact workflow metadata all support one factual Phase 5 release-status map. Task 3.5 applies corrections based on this map and remains separate.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The block requires cross-file provenance analysis, exact-SHA hosted metadata reconciliation, conservative evidence labels, sanitized reporting, and Runway OS stewardship.

Runner path: record and refresh active 5K; preserve branch/head, dirty worktree, empty index, product/test hashes, and unrelated files; inventory local evidence; inspect local Git without ref mutation; query each exact hosted surface once; reconcile exact SHAs, PR state, job order, conclusions, annotations, merges, and deploy evidence; create the evidence map and log; close Task 3.4 locally; verify Runway OS automatically; and stop.

Expected paths: create `command-center/phase-5-release-evidence-map.md` and `command-center/logs/2026-07-27-phase-5-release-evidence-reconciliation-5k.md`; narrowly update `command-center/operations-monitoring-matrix.md`; update `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`. No product, test, README, workflow, provider, Fly, database, production, or unrelated path may change.

Defaults: current Git and exact hosted metadata override stale prose; historical evidence remains historical; no provider, Fly, application, or health query; no fetch or local ref mutation; one query per necessary hosted surface; missing or ambiguous evidence remains pending; and no local-only result is promoted by inference.

Stop conditions: local/hosted ref contradiction prevents classification; metadata is unavailable, private, sensitive, or requires write authority; a result lacks an exact SHA; evidence requires provider, Fly, application, production, database, or protected access; urgent repair or excluded correction is needed; baseline or intended-path drift occurs; or link, JSON, dashboard, health, currentness, whitespace, sensitive-value, or scope verification fails.

Verification: exact local branch/head/status/empty-index/ancestry/path inventory; unchanged product/test and preserved-file hashes; exact read-only GitHub ref, PR, run, job, conclusion, annotation, and SHA reconciliation; source-linked evidence statements; strict evidence-label boundaries; local links; JSON; automated dashboard refresh/generated-state equality/health; exactly one current task; generated markers; relevant diff; whitespace; sensitive-value scan; and exact changed paths.

Dashboard closeout: on a supported result, mark Task 3.4 and 5K complete locally, make Task 3.5 the sole current Ryan-owned planning task, retain every release and protected gate, and use automated dashboard closeout without Ryan visual attestation.

Report point: return the exact evidence map, current refs and PR states, CI/deployment evidence, local-only versus durable boundaries, unresolved gates, contradictions, changed paths, preservation, and decisions required before release or documentation work.

Suggested next work block: 5L — Task 3.5 Maintained Documentation and Compact Release Handoff.

Result: current remote `main` is `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb` and contains PR #89 merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce` plus three later `[skip actions]` command-center commits. PR #89 activation head `13d2f16a9cca8b8d4fb4900006dfaa9655824474` passed exact ordered Synthetic CI run `30262719321` with zero annotations; the merge passed Fly Deploy run `30263216876` with zero annotations and has dated authorized `status: ok` health evidence. PR #90 remains open, clean, draft, and unmerged at `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`; exact-head Synthetic CI run `30279361029` passed both jobs with zero annotations, but no merge, deployment, or production claim exists. Ask Opus and operator/handoff artifacts are local-only; current runtime health is externally unverified and provider settings remain protected. The source-linked map is `command-center/phase-5-release-evidence-map.md`. No contradiction, external mutation, protected access, or excluded action occurred. Task 3.4 and 5K are complete locally; Task 3.5 is the sole current Ryan-owned planning task.

### Confirmed Work Block 5J: Local Synthetic Operator Re-entry Drill

Status: done locally under the automated dashboard-closeout rule.

Included: Task 3.3 (`P5-T33`) only. Follow the 5I authority, risk-classification, worktree-preservation, synthetic-verification, failure, cleanup, and dashboard sequence; run the maintained workflow-safety checker, full smoke suite, and complete installed-Chrome suite once; allow the smoke suite's internal demo-seeder subprocess only within its source-defined disposable temporary directory; annotate the runbook and matrix with accurate validation status/evidence; write one sanitized 5J log; close Runway OS locally; and stop.

Excluded: Tasks 3.4-3.5; Tasks 2.2, 2.7, and 2.8; Task 4; defect repair; product, test, workflow, dependency, runtime, configuration, migration, or substantive README changes; external-currentness, GitHub, PR, workflow, provider-account, or production observations; `.env`, credentials, real databases, uploads, backups, statements, exports, financial or payroll rows; direct application startup against `local_state`; direct seed, sync, transfer, recovery, Plaid, Fly, OpenRouter, or other operational command execution; staging, commit, push, PR mutation, workflow action, merge, deployment, production, parent changes, delegation, and second opinion.

Why this grouping: Task 3.3 is one source-defined credential-free validation path for the runbook and matrix produced by Tasks 3.1-3.2. Task 3.4 uses different local/durable/hosted/currentness evidence, while Task 3.5 depends on both results.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The local policy assigns orchestration, local verification, exact cleanup, evidence intake, and Runway OS stewardship to Codex.

Runner path: record active 5J; preserve the exact dirty-worktree baseline, branch/head, empty index, and unrelated files; run `scripts/ci_safety_check.py`, `scripts/smoke_test.py`, and `scripts/mobile_drawer_browser_test.py` once; accept only temporary synthetic data, ephemeral localhost, both authentication modes, denied non-localhost browser requests, sanitized diagnostics, and exact cleanup; record pass or stop evidence; update only validation status/evidence and Runway OS; and stop.

Expected paths: narrow updates to `command-center/operator-runbook.md` and `command-center/operations-monitoring-matrix.md`; one new `command-center/logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md`; and `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`. No maintained product, test, workflow, README, configuration, dependency, database, protected, or unrelated path may change.

Defaults: accept the current dirty worktree as the preserved baseline; run each complete suite once; do not retry blindly; do not open `.env`; log only sanitized pass/fail evidence; do not query PR #90 or any external surface; never invoke the demo seeder directly; and make no product or test correction.

Stop conditions: unresolved or non-temporary data path; credential, protected content, external request, or live configuration need; direct operational action; failing suite requiring correction; temporary-data, browser-server, process, or artifact residue; unexpected changed path; branch/head/index/preserved-file drift; or failed JSON, dashboard, health, currentness, whitespace, sensitive-pattern, or exact-scope verification.

Verification: exact baseline and final hashes; empty index; unchanged branch/head; local workflow safety checker; complete smoke suite; complete both-auth installed-Chrome suite; denied-network and exact-cleanup assertions; narrow runbook/matrix evidence; JSON; dashboard refresh/currentness/health; generated markers; whitespace; sensitive-pattern scan; and exact changed paths.

Dashboard closeout: on a clean pass, mark Task 3.3 and 5J complete locally, make Task 3.4 the sole current Ryan-owned planning task, and keep Task 3.5 plus every external, protected, durability, publication, merge, deployment, and production gate separate. Wait for Ryan's exact `5J dashboard verified` attestation before final declaration.

Report point: return every re-entry stage exercised, exact commands, sanitized outcomes, cleanup proof, any runbook gap, changed paths, preservation, dashboard status, and the separate Task 3.4 planning gate.

Suggested next work block: 5K — Task 3.4 Phase 5 Release-Evidence and Unresolved-Gates Reconciliation.

Result: the workflow safety checker passed the Synthetic CI and Fly Deploy contracts; the full smoke suite passed once with temporary synthetic entity data, maintained denied-network seams, its internally guarded disposable demo-seeder proof, and exact cleanup; and the complete installed-Chrome suite passed once in both authentication modes with ephemeral localhost, blocked non-localhost requests, mocked external seams, console/page-error checks, and exact cleanup. Product and test hashes, branch/head, empty index, and preserved unrelated files were unchanged. The runbook and monitoring matrix now accurately mark the local synthetic path as verified through 5J. Automated JSON, dashboard refresh/generated-state equality/health, current-task invariant, generated-marker, relevant-diff, whitespace, sensitive-value, scope, and preservation checks passed. Ryan directed that routine dashboard closeouts no longer require his visual attestation. No repair, credential, real/protected data, external-currentness, GitHub/PR/workflow observation, product/test/workflow/dependency/configuration/README change, publication, merge, deployment, or production action occurred. Task 3.4 remains planning-only. Evidence: `command-center/logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md`.

### Confirmed Work Block 5I: Operator Re-entry and Monitoring Contract

Status: done locally after Ryan's rendered closeout-dashboard attestation.

Included: Tasks 3.1-3.2 (`P5-T31`-`P5-T32`) only. Inventory tracked setup, verification, deployment, synchronization, recovery, AI, data, durability, workflow, safety-contract, and sanitized evidence sources; draft one source-linked operator runbook plus one monitoring/maintenance matrix; distinguish source-verified, externally unverified, protected, and separately authorized state; add one sanitized evidence log; close Runway OS locally; and stop.

Excluded: Tasks 3.3-3.5; Tasks 2.2, 2.7, and 2.8; Task 4; README, product, test, workflow, runtime, database, dependency, or configuration changes; external-currentness queries; provider-account verification; `.env`, credentials, real databases, uploads, backups, statements, exports, financial or payroll rows; invoking seed, sync, transfer, recovery, deployment, Plaid, Fly, OpenRouter, or other operational commands; staging, commit, push, PR #90 mutation, workflow action, merge, deployment, production, parent-project changes, delegation, and second opinion.

Why this grouping: Tasks 3.1-3.2 share one factual source-audit and documentation outcome, the same local-only safety boundary, and the same verification path. Task 3.3 exercises the result and therefore stays separate.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns cross-file reconciliation, conservative safety language, Runway OS stewardship, and final intake.

Runner path: record and refresh active 5I; preserve the exact branch, head, dirty worktree, empty index, PR #90, and unrelated files; read tracked source plus sanitized evidence only; create the runbook, monitoring matrix, and evidence log; verify links, scope, safety, generated state, and preservation; close locally; and stop.

Expected paths: create `command-center/operator-runbook.md`, `command-center/operations-monitoring-matrix.md`, and one sanitized 5I evidence log; update only `command-center/now.md`, `roadmap.md`, `decisions.md`, `state.json`, and generated `index.html`. All product, test, README, workflow, configuration, database, protected, and unrelated paths remain unchanged.

Defaults: label mutable external facts as unverified-current; record currentness gaps without querying them; never infer remediation authority; do not invoke a script merely to learn its CLI; defer maintained README changes to Task 3.5; preserve PR #90 and the existing worktree.

Stop conditions: a material source contradiction needs Ryan; accurate guidance requires external/protected/live access; an operational command or product change is needed; scope expands; an unexpected or sensitive path appears; preservation, index, branch, or PR state drifts; or JSON, dashboard, health, generated-state, whitespace, or source-link verification fails.

Verification: every instruction is source-linked; the runbook covers normal, failure, escalation, recovery, and re-entry boundaries; the matrix records owner, signal, cadence, threshold, allowed observation, evidence, status, and remediation gate; unsupported currentness claims are absent; JSON, dashboard refresh/currentness/health, generated markers, whitespace, sensitive-pattern, exact-path, empty-index, preserved-hash, branch, and unchanged-PR checks pass.

Dashboard closeout: on success, mark Tasks 3.1-3.2 and 5I done locally, make Task 3.3 the sole current Ryan-owned planning task, and keep Tasks 3.4-3.5 plus every external, protected, durability, publication, merge, deployment, and production gate separate. If browser policy still blocks the local `file:` page, wait for Ryan's `5I dashboard verified` attestation before declaring completion.

Report point: return the source inventory, runbook, monitoring matrix, contradictions, unresolved currentness, exact paths, verification, preservation, dashboard status, and the proposed Task 3.3 drill.

Suggested next work block: 5J — Task 3.3 Local Synthetic Operator Re-entry Drill.

Result: `command-center/operator-runbook.md` and `command-center/operations-monitoring-matrix.md` now define the source-linked re-entry, risk, verification, monitoring, recovery, and escalation contract. The audit confirmed the `run.py` default-data/migration boundary and the demo seeder's no-help destructive behavior; recorded the stale sync-contract header, configuration/example gaps, absent continuous health/backup/runtime-maintenance cadences, externally unverified monitor/provider state, and hard-coded dashboard `CST` label; and deferred runtime validation, release evidence, and maintained-documentation corrections to Tasks 3.3-3.5. Local-link, field, currentness-language, sensitive-pattern, protected-value, JSON, dashboard, health, whitespace, scope, empty-index, preserved-file, branch/head, and unchanged PR #90 checks passed. Ryan returned the exact `5I dashboard verified` attestation after inspecting the sanitized rendered closeout dashboard. Tasks 3.1-3.2 and 5I are complete locally; Task 3.3 execution and every external, protected, operational, product, test, README, workflow, publication, merge, deployment, and production action remain separately gated. Evidence: `command-center/logs/2026-07-27-operator-reentry-monitoring-contract-5i.md`.

### Confirmed Work Block 5H-B: Ask Opus Privacy Contract Implementation

Status: done locally; verified, unstaged, uncommitted, and unpublished.

Included: Task 2.5 (`P5-T25`) only. Adopt the recommended 5H contract; preserve explicit-submit-only behavior; make every supported context active-entity and summary-first; reject unknown page identifiers before data gathering; remove Weekly and Waterfall Ask triggers until dedicated contexts exist; eliminate server-side conversation persistence; make Clear browser-local; require OpenRouter per-request ZDR and denial of data-collecting providers; replace advisor and full-access language with truthful purpose, provider-path, page-data, entity, metadata, retention, and fallibility disclosure; add exact temporary-synthetic payload, entity-isolation, provider-policy, lifecycle, error, modal, accessibility, responsive, both-auth, and denied-network coverage; update maintained documentation; close Runway OS locally; and stop.

Excluded: Tasks 2.2, 2.7, 2.8, 3, and 4; Personal/BFM combination or opt-in; account, asset, or liability labels; exact transaction dates; free-form goal strategies; unrelated OpenRouter features including cancellation tips and categorization; existing chat-history files; `.env`; credentials; real databases, uploads, or financial rows; live OpenRouter, Anthropic, Plaid, Fly, production, demo, downstream, or another API call; authentication, database, migration, category, reporting, CSP, PWA, workflow, or dependency change beyond required regression preservation; PR #90 mutation; staging, commit, push, PR creation, merge, deployment, provider-account verification, delegation, second opinion; and the duplicate 4AU log, `command-center/now 2.md`, or `scripts/sync_prod_to_local.sh`.

Why this grouping: exact page validation, context minimization, transcript removal, provider routing, disclosure, and their synthetic/browser tests form one enforceable privacy contract. Leaving any of them for a different implementation block would make the UI or transport boundary incomplete.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The block requires integrated Flask, client, template, privacy-boundary, synthetic-test, rendered-browser, and Runway OS stewardship; 5H-A already completed the relevant independent factual audit.

Runner path: write and verify active 5H-B state; preserve the exact dirty worktree, three unrelated files, current head, and PR #90; create local `codex/ask-opus-privacy` from exact head `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a` without pushing; establish synthetic baselines; implement only the accepted contract; run focused and complete verification with denied external networking; inspect sanitized rendered behavior; close Task 2.5 locally; and stop.

Expected paths and surfaces: `core/ai_client.py`, `web/routes/ai.py`, `web/templates/base.html`, `web/templates/weekly.html`, `web/templates/waterfall.html`, `web/static/app-shell.js`, `web/static/style.css`, `scripts/smoke_test.py`, `scripts/mobile_drawer_browser_test.py`, `README.md`, `command-center/ask-opus-data-handling-contract.md`, one new sanitized 5H-B evidence log, five Runway OS sources, and generated dashboard. Other supported Ask-trigger templates are inspection-only unless exact tested disclosure metadata requires a narrowly necessary change.

Defaults: no cross-entity or opt-in mode; exclude account, asset, and liability labels, exact transaction dates, and free-form strategies; permit merchant names only for aggregated merchant analysis and recurring-charge review; send no prior question or answer; keep visible responses only in the current browser DOM; make Clear local; preserve the Opus model; enforce privacy controls only on Ask Opus without changing other AI features; use AI-explainer and verify-before-financial-decision language; make no account-setting claim; keep work local.

Stop conditions: any need for protected data, credential, existing chat file, real provider request, broader entity scope, excluded identifier, unrelated AI behavior change, provider-policy fallback, unexpected path, PR #90 or branch drift, preserved-file overlap, external network request, cleanup failure, or plan-changing focused/full/browser/dashboard/scope/whitespace/index verification failure.

Verification: baseline and final full smoke; exact temporary-synthetic serialized-context allowlists for every supported page and all three entities; unknown-page rejection before data access; provider request capture proving ZDR and data-collection denial; no transcript path or filesystem behavior; browser-only Clear; no request on modal open; truthful disclosure; Weekly/Waterfall absence; authentication, CSRF, CSP, HTMX, keyboard, accessibility, desktop, phone, exact-768, PWA, console, denied-network, and cleanup preservation; relevant Python and JavaScript syntax; JSON; dashboard refresh/currentness/health and rendered state; whitespace; high-confidence sensitive additions; exact changed paths; empty real index; preserved hashes; and unchanged open draft PR #90.

Dashboard closeout: on success, mark 5H-B and Task 2.5 complete locally, keep Phase 5 active, make Task 3 the sole current Ryan-owned planning task, retain Tasks 2.2, 2.7, and 2.8 as parked, and preserve 5G-R2, 5H-R, provider-account verification, publication, merge, deployment, and production as separate gates.

Report point: return the accepted page-by-page data boundary, exact provider payload, transcript and Clear behavior, disclosure, disabled triggers, changed paths, complete synthetic and rendered verification, branch/index/preservation state, and any discovered constraint.

Expansion candidates and questions: none. Confirmation accepts the recommended contract and this local implementation only.

Suggested next work block: 5H-R exact-path branch durability and hosted review only after Ryan separately resolves the PR #90/5G-R2 branch base. Protected OpenRouter account-setting verification remains a separate pre-production gate.

Result: Ask Opus now accepts only Dashboard, Transactions, Long-Term Planning, Short-Term Planning, Recurring Review, Cash Flow, and Reports; missing, General, Weekly, Waterfall, and crafted pages return 400 before context or provider work. Every context is active-entity and summary-first, with the selected account/item/date/strategy/note/merchant exclusions. The server transcript directory, history helpers, and Clear endpoint are removed; one fresh question is sent per submission and Clear affects only the browser DOM. Ask-specific requests serialize `provider: {"zdr": true, "data_collection": "deny"}`. The modal truthfully discloses purpose, entity, page data, provider path, request metadata, no Ledger transcript, and fallibility. Focused coverage also corrected the prior Ask-only SQLite `%%Y-%%m` defect that silently omitted current-month categories and merchants. Baseline and final smoke/browser suites, exact Personal/BFM/LL allowlists, provider capture, invalid-page pre-data stop, transcript absence, 390/768/1440 layout, direct sterile desktop/phone inspection, denied networking, console health, cleanup, dashboard, scope, index, preserved-file, and unchanged PR #90 checks passed. No protected, provider-account, live API, GitHub, workflow, merge, deployment, or production action occurred. Evidence: `command-center/logs/2026-07-27-ask-opus-privacy-contract-implementation-5h-b.md`.

### Confirmed Work Block 5H-A: Ask Opus Data-Handling Contract Audit

Status: done locally; recommended contract returned to Ryan and implementation remains separate.

Included: Task 2.5 (`P5-T25`) only for its contract prerequisite. Inspect tracked Ask Opus source and maintained tests plus current public official OpenRouter and Anthropic documentation; map every visible trigger to accepted route page, transmitted data categories, entity and cross-entity scope, fallback behavior, history persistence and clearing, disclosure, authentication, CSRF, error, and logging boundaries; create one sanitized decision packet and evidence log; recommend a production contract and alternatives; define exact Ryan decisions and acceptance criteria for a later implementation block; update and refresh Runway OS; and stop.

Excluded: Task 2.5 implementation or product, route, template, style, JavaScript, test, dependency, workflow, configuration, authentication, database, AI, CSP, or PWA behavior change; Tasks 2.2, 2.7-2.8, 3, and 4; reading existing temporary chat-history files, `.env`, credentials, real databases, uploads, or financial rows; OpenRouter, Anthropic, Plaid, Fly, production, demo, downstream, or another live API call; staging, commit, push, PR #90 mutation, merge, deployment, production health, delegation, second opinion, or action on the duplicate 4AU log, `command-center/now 2.md`, or `scripts/sync_prod_to_local.sh`.

Why this grouping: source behavior, provider policy, retention semantics, truthful disclosure, and implementation acceptance criteria form one decision prerequisite. UI implementation depends on Ryan selecting that contract, while release and adjacent phase tasks have different risk and verification paths.

Owner and recommended agent: Codex Desktop without delegation or second opinion. The work requires cross-file source audit, current public-policy research, privacy-boundary analysis, and Runway OS stewardship. The earlier independent design review already identified the trust problem; this block resolves factual scope before another critique could help.

Defaults: treat transmission as permitted only after explicit question submission; recommend entity-local context by default, no silent page fallback or cross-entity inclusion, minimum page-relevant data, no invisible indefinite on-disk transcript, and truthful provider/data/scope/retention disclosure; make no provider retention, training, or deletion claim without current official support; recommend rather than adopt the final contract; keep all work local and leave PR #90 unchanged.

Stop conditions: any need to inspect protected data, credentials, live configuration, existing chat files, or call an AI/API; provider documentation cannot support a disclosure-critical claim; an urgent security correction or product change becomes necessary; scope expands beyond the Task 2.5 contract prerequisite; or exact-path, sensitive-data, JSON, dashboard, health, or whitespace verification fails.

Verification: complete trigger/context/entity/retention/control matrix with tracked-source citations; current official provider-policy citations; explicit unknowns; no protected/live access; exact changed paths; sensitive-addition review; JSON parsing; dashboard refresh/currentness and health; and `git diff --check`.

Dashboard closeout: mark 5H-A done; leave Task 2.5 Ryan-owned and `decision-needed`; show the exact contract choices; keep Phase 5 at 44%; leave PR #90 open, draft, and unchanged; and do not imply implementation, release, or deployment authority.

Report point: return the current behavior matrix, important mismatches and risks, provider-policy findings, recommended contract, alternatives and tradeoffs, exact Ryan decision prompt, changed artifacts, verification result, and separately confirmed 5H-B implementation gate.

Expansion candidates and questions: none. Implementation, Task 2.7 information architecture, 5G-R2 release, and every live or protected action remain separate.

Suggested next work block: 5H-B for Ask Opus purpose and privacy implementation only after Ryan selects and separately confirms the contract.

Result: tracked source established that six effective contexts silently combine Personal and BFM; Weekly and Waterfall normalize to shared `general` context and history while their Clear actions target different files; temporary question/answer history has a 40-message cap but no TTL or visible restoration; and the current OpenRouter request enforces no provider privacy controls. Current official documentation establishes that OpenRouter prompt/response logging is opt-in, metadata is retained, provider routing and retention vary, and per-request ZDR is available; first-party Anthropic commercial content is not used for training by default and is ordinarily deleted within 30 days, but OpenRouter may select another endpoint. The recommended contract is explicit-submit-only, active-entity, summary-first, no broad fallback, no server transcript by default, per-request ZDR plus denial of data-collecting providers, separately verified OpenRouter account settings, truthful disclosure, and fail-closed behavior. Weekly and Waterfall remain unavailable until dedicated contexts exist. No protected data, existing chat file, credential, live API, product/test/configuration source, GitHub, workflow, merge, deployment, or production state was accessed or changed. Task 2.5 remains incomplete and returns to Ryan as `decision-needed`; evidence is in `command-center/ask-opus-data-handling-contract.md` and `command-center/logs/2026-07-27-ask-opus-data-handling-contract-audit-5h-a.md`.

### Confirmed Work Block 5G-R: Recurring Review Branch Durability And Hosted Review

Status: done on open draft PR #90, conditional on the exact six-path closeout head satisfying the recorded automatic hosted verification contract.

Included: Task 4 (`P5-T4`) only for exact feature-branch durability and hosted PR-only review of completed Task 2.4 and 5G/5G-RS. Revalidate the exact sixteen-path initial package; explicitly stage only those paths; create one release-candidate commit without a skip token; non-force push `codex/recurring-review-surface`; open one draft PR targeting `main`; observe automatic core-then-browser Synthetic CI; after a clean first pass publish one sanitized six-path closeout commit without a skip token; require the final PR head to pass the same workflow; prove zero Fly deployment; retain the branch; leave the PR open, draft, and unmerged; and stop.

Initial package: `README.md`, `scripts/smoke_test.py`, `web/routes/subscriptions.py`, `web/static/style.css`, `web/static/subscriptions.js`, `web/templates/subscriptions.html`, `web/templates/todo.html`, `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, `command-center/state.json`, `command-center/logs/2026-07-27-recovered-database-application-verification-5g-av.md`, `command-center/logs/2026-07-27-human-verified-dashboard-reentry-5g-av-r.md`, `command-center/logs/2026-07-27-recurring-review-safe-resume-5g-rs.md`, and `command-center/logs/2026-07-27-recurring-review-branch-durability-5g-r.md`.

Excluded: merge; push to `main`; ready-for-review transition; production release or health access; Fly deployment, CLI, console, secrets, restart, or rollback; manual workflow dispatch, rerun, cancellation, or repair; Plaid; protected or real data; Task 2.5 and every other product or privacy change; source correction; dependency, workflow, runtime, configuration, category, database, authentication, CSP, or PWA change; delegation; second opinion; force push; rebase; conflict resolution; branch deletion; the duplicate 4AU log; `command-center/now 2.md`; and `scripts/sync_prod_to_local.sh`.

Why this grouping: exact-path commit, feature-branch push, draft PR creation, two automatic hosted verification heads, and zero-deployment proof form one durability outcome. Merge and production release have a higher risk class and depend on the hosted result.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact-path Git/GitHub handling, local and hosted verification, zero-deployment proof, and Runway OS intake.

Defaults: retain the existing feature branch; use two commits; omit skip tokens because both PR heads must receive Synthetic CI; use no manual workflow action; leave the PR draft and unmerged; retain the branch; perform no production health request because no deployment is authorized.

Stop conditions: local/main/origin/head or path drift; original or preserved-file drift; owner/sidecar or unsafe-data condition; sensitive addition; exact-stage, smoke, browser, safety, syntax, JSON, dashboard, whitespace, cleanup, or index failure; push conflict; unexpected PR state; failed, missing, delayed, out-of-order, or annotated hosted job; any Fly deployment; or any need for repair, rerun, cancellation, merge, protected access, force, rebase, conflict resolution, or expansion.

Verification: exact branch and base refs; original and preserved hashes without SQLite; exact sixteen-path initial stage; full smoke; complete both-auth installed-Chrome suite; Synthetic CI and Fly safety; Python/JavaScript syntax; JSON; dashboard refresh/currentness/health; whitespace; sensitive additions; cleanup; source and closeout commit ancestry; non-force remote branch equality; draft PR base/head/state; automatic core-before-browser success with zero annotations on both heads; and zero Fly Deploy runs for both heads.

Dashboard closeout: on success, record 5G-R as branch-durable and hosted-verified, keep Task 2.4 done, keep Phase 5 at 44%, return Task 2.5 to Ryan as the sole current planning decision, and preserve merge and production release as separately confirmed 5G-R2.

Report point: return exact staged paths, commits, branch, draft PR, both hosted run/job results, annotations, zero-deployment proof, preserved exclusions, final dashboard state, and the separate 5G-R2 gate.

Expansion candidates and questions: none.

Suggested next work block: 5G-R2 for merge and production release only after clean hosted review and separate Ryan confirmation.

Result: exact sixteen-path source commit `182cabd73640bfd6f8ce754740b5b20bbfc045dd` is durable on `codex/recurring-review-surface` and open draft PR [#90](https://github.com/rabuffington22/expense-tracker/pull/90), targeting unchanged `main` at `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`. Automatic pull-request Synthetic CI run `30278240194` passed core job `90017670024` before browser job `90017941876`; every step succeeded, both jobs returned zero annotations, and no Fly Deploy run existed for the candidate SHA. The authorized six-path closeout commit is valid only after its own exact SHA passes the same automatic core-then-browser, zero-annotation, zero-deployment contract with PR #90 still open, draft, unmerged, and aligned to the retained branch. Task 2.5 returns to Ryan as the sole current planning decision; merge and production release remain separately gated as 5G-R2.

### Confirmed Work Block 5G-RS: Recurring Review Safe Resume And Local Closeout

Status: done locally; synthetic and rendered checks passed with no correction, Ryan's rendered closeout-dashboard attestation passed, and publication remains separate.

Included: Task 2.4 (`P5-T24`) only. Resume the preserved seven-file Recurring Review implementation after completed 5G-AV-R; verify its combined review-and-track purpose, existing `/subscriptions/` route, visible name, truthful scope copy, tracked-first order, exact review count, visible Track and Dismiss actions, immediate accessible undo, durable restoration, existing lifecycle/manual-add/detail/history/notes/account-information/tips/delete behavior, entity isolation, authentication modes, CSP/PWA preservation, and responsive behavior. Make only narrowly necessary corrections inside the expected seven product/documentation/test paths when required to satisfy that frozen contract.

Excluded: Task 2.2 (`P5-T22`); Task 2.5 (`P5-T25`); Tasks 2.7-2.8 (`P5-T27`-`P5-T28`); Tasks 3-4 (`P5-T3`-`P5-T4`); kind/classification models; detector thresholds, cadence, query, financial, category, reporting, migration, authentication, session, CSRF, CSP, PWA, service-worker, Ask Opus, AI-data, or URL changes; protected row data; Luxe Legacy setup; Plaid; staging, commit, push, PR, workflow, Fly, publication, deployment, production; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the implementation, focused synthetic coverage, complete browser suite, responsive rendering, and local closeout are the remaining parts of one already-frozen Task 2.4 contract. Every adjacent task or durability action has a different decision and risk path.

Owner and recommended agent: Codex Desktop without delegation or another second opinion. The block requires integrated Flask, Jinja, JavaScript, CSS, test, browser, protected-boundary, and Runway OS stewardship; the completed 5B critique already supplies independent design review.

Runner path: write and refresh active 5G-RS state; verify accepted original hashes and metadata plus owner/sidecar absence without SQLite or application access; verify the seven preserved product files, three preserved unrelated files, and empty real index; run only temporary synthetic smoke/browser/rendered checks; make only narrow in-scope corrections when necessary; prove exact cleanup and preservation; write and refresh local closeout; wait for Ryan's `5G-RS closeout dashboard verified`; then declare completion and stop before every sequel.

Expected paths: `README.md`, `scripts/smoke_test.py`, `web/routes/subscriptions.py`, `web/static/style.css`, `web/static/subscriptions.js`, `web/templates/subscriptions.html`, `web/templates/todo.html`, read/run-only `scripts/mobile_drawer_browser_test.py`, five command-center sources, generated dashboard, and `command-center/logs/2026-07-27-recurring-review-safe-resume-5g-rs.md`. No database, migration, dependency, configuration, workflow, or new product path is expected.

Defaults: use only fresh temporary synthetic Personal, BFM, and Luxe Legacy data; never invoke `scripts/seed_demo_data.py`; never resolve `DATA_DIR` to `local_state`; never load `.env` or live credentials; never open recovered originals through SQLite or Flask; allow only narrowly necessary corrections within the expected seven product paths; keep everything local, unstaged, uncommitted, and unpublished.

Stop conditions: original or preserved-file drift; unexpected owner or WAL/SHM sidecar; unsafe `DATA_DIR`, `.env`, credential, or external-network condition; unexpected source path; need for a model, semantic, migration, authentication, CSP/PWA, URL, protected/live, publication, or other excluded change; lifecycle, entity, accessibility, keyboard, modal, responsive, or cleanup regression; plan-changing test or rendered failure; dashboard/currentness/health/whitespace/index failure.

Verification: accepted original hashes/metadata and owner/sidecar absence without SQLite; preserved product and unrelated-file hashes; `.venv/bin/python scripts/smoke_test.py`; `.venv/bin/python scripts/mobile_drawer_browser_test.py`; temporary synthetic desktop, 390px phone, and exact-768 installed-Chrome inspection with denied non-localhost networking; focused all-entity Track/Dismiss/decrement/undo/restore/empty/manual-add/lifecycle/detail/account/tips/delete coverage; Python/JavaScript syntax; CI safety; JSON; dashboard refresh/currentness/health; whitespace; exact paths; cleanup; empty real index.

Dashboard closeout: on pass, show 5G-RS, 5G, and Task 2.4 done locally; keep Phase 5 active and publication absent; identify 5G-R as a separately gated durability/release decision; wait for `5G-RS closeout dashboard verified` before declaring completion.

Report point: return exact behavior, changed paths, synthetic and rendered results, correction details if any, original/worktree preservation, cleanup, branch/index state, and the remaining durability/publication gate.

Expansion candidates and questions: none.

Suggested next work block: after a clean local result, separately plan 5G-R for exact branch durability and any hosted/release decision. Do not begin it inside 5G-RS.

Result: the preserved seven-file implementation required no correction. Original database hashes/metadata and owner/sidecar absence, product and unrelated preserved hashes, syntax, Synthetic CI/Fly safety, full smoke, complete both-auth installed-Chrome coverage, denied-network behavior, exact cleanup, whitespace, and empty-index checks passed. Fresh installed-Chrome rendering passed for synthetic Personal desktop 1440x1000 with immediate undo, BFM exact-768, and Luxe Legacy 390px phone with HTTP 200, tracked-first order, truthful one-tracked/one-to-review counts, visible Track and Dismiss actions, readable wrapping, zero horizontal overflow, zero console/page errors, and zero denied requests. The synthetic data, runner, and three temporary screenshots were removed exactly with no process owner. Ryan returned the exact `5G-RS closeout dashboard verified` attestation after inspecting the sanitized closeout state. Task 2.4 and 5G/5G-RS are complete locally. No product correction, original SQLite/Flask access, staging, commit, publication, GitHub, workflow, Fly, Plaid, deployment, production, or successor action occurred; 5G-R remains a separate gate.

### Confirmed Work Block 5G-AV-R: Human-Verified Dashboard Re-entry And Application Check

Status: done; protected-copy application check and both Ryan-rendered dashboard checkpoints passed.

Included: Task 2.4 (`P5-T24`) only for exact recovered-data application-readiness re-entry. Codex writes and refreshes active 5G-AV-R state, runs JSON, dashboard generation/currentness, health, whitespace, exact-diff, and empty-index checks, and stops before every protected-data action. Ryan opens the generated dashboard and confirms that it visibly shows Phase 5, active 5G-AV-R, Task 2.4, Ryan at the checkpoint, the protected-copy stop conditions, and the next report point. Ryan's safe `active dashboard verified` handoff unlocks the already-authorized exact 5G-AV disposable-copy verification. Codex then reuses the confirmed mode-700 byte-identical Personal/BFM copy, sterile Flask/installed-Chrome, denied-network, eight-route, sanitized-evidence, integrity/schema/aggregate, original/worktree-preservation, and exact-cleanup contract unchanged. After pass or stop, Codex writes and refreshes the sanitized closeout and waits for Ryan's `closeout dashboard verified` handoff before declaring the block complete.

Excluded: Task 2.2 (`P5-T22`); Task 2.5 (`P5-T25`); Tasks 2.7-2.8 (`P5-T27`-`P5-T28`); Tasks 3-4 (`P5-T3`-`P5-T4`); 5G implementation resume or completion; product/test edits; opening recovered originals through Flask; mutation of originals or protected recovery copies; screenshots, traces, videos, downloads, response/HTML/body dumps, console message text, row-level or financial output; Luxe Legacy; Plaid; OpenRouter; credentials; staging, commit, push, PR, workflow, Fly, deployment, production, publication, delegation, second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the two manual rendered-dashboard attestations are the missing control-surface proof around the already coherent protected-copy application verification. Keeping them inside one block prevents either handoff from silently authorizing 5G implementation or publication.

Owner and recommended agent: Codex Desktop, with Ryan owning only the two rendered-dashboard checkpoints. No delegation or second opinion. Codex remains responsible for protected-data boundary control, application/browser orchestration, exact cleanup, evidence, and Runway OS closeout.

Runner path: record and refresh active state; pause for `active dashboard verified`; after that exact handoff, execute only the confirmed 5G-AV protected-copy verification; write and refresh sanitized pass/stop closeout; pause for `closeout dashboard verified`; then report and stop before every sequel.

Expected paths and surfaces: the five command-center sources, generated dashboard, `command-center/logs/2026-07-27-human-verified-dashboard-reentry-5g-av-r.md`, the existing 5G-AV log, exact recovered Personal/BFM files only after the first handoff for owner/sidecar/hash/copy checks, one mode-700 disposable directory outside the repository, and Dashboard/Transactions/To Do/Recurring Review for both entities. No tracked product or test change is expected.

Defaults: Ryan reports only the exact safe checkpoint phrases and provides no screenshot or financial detail; Codex reuses the prior 5G-AV contract without expansion; the first checkpoint unlocks only protected-copy verification; the second checkpoint closes only 5G-AV-R; even a clean result returns 5G resume to Ryan as a separate decision.

Stop conditions: either rendered dashboard does not match the expected phase, block, task, checkpoint owner, stop conditions, or report point; original drift, unexpected owner or sidecar, copy mismatch, original-path access, external network, credential/live dependency, integrity failure, unexpected financial/workflow aggregate mutation, route/browser/privacy failure, cleanup or preserved-file drift, JSON/dashboard/health/whitespace/index failure, scope expansion, or need for any excluded action.

Verification: exact active and closeout Ryan-rendered-dashboard attestations; JSON; dashboard generation/currentness and health; exact command-center diff; whitespace and empty index; then the unchanged 5G-AV source/copy hash, owner/sidecar, sterile-environment, denied-network, eight-route, integrity/schema/aggregate, cleanup, original, product, and preserved-file checks.

Dashboard closeout: show active 5G-AV-R and Ryan at the first checkpoint before protected access. After pass or stop, show the exact sanitized result and Ryan at the closeout checkpoint. Do not declare completion until `closeout dashboard verified`.

Report point: after the first checkpoint, begin the already-authorized protected-copy check. After the second checkpoint, return application readiness, preservation and cleanup proof, and the separate 5G-resume recommendation.

Expansion candidates and questions: none. Both human replies are verification handoffs inside 5G-AV-R, not authority for any excluded sequel.

Suggested next work block: after a clean verified closeout, separately propose 5G-RS for Recurring Review resume and local closeout. If verification stops, propose a sanitized diagnostic block instead.

Result: Ryan returned both `active dashboard verified` and `closeout dashboard verified`, and the protected-copy application check passed. Both recovered originals matched their accepted hashes and metadata before and after with no owners or sidecars. Exact byte-identical copies ran only in a mode-700 disposable directory through sterile local Flask and fresh installed Chrome with live credentials absent and non-localhost networking denied. Dashboard, Transactions, To Do, and Recurring Review passed for Personal and BFM: eight of eight HTTP 200 responses with expected titles/headings, zero console errors, zero page errors, and zero denied requests. Both copies passed integrity before and after; tracked additive schema 57 advanced to 58; category/subcategory deltas were Personal `0/+16` and BFM `-2/+22`; import-profile counts and every protected financial/workflow aggregate remained unchanged. The exact directory and four derived temporary files were removed after all processes closed. The originals, seven existing modified 5G product/test/documentation files, three preserved unrelated untracked files, and empty real Git index remained unchanged. 5G-AV-R is complete locally. This is an application-readiness result only; 5G resume remains separately gated.

### Confirmed Work Block 5G-AV: Recovered-Database Application Verification

Status: stopped safely before protected copying because the required rendered dashboard inspection was unavailable; verification did not begin and 5G implementation resume remains excluded.

Included: Task 2.4 (`P5-T24`) only for recovered-data application readiness. Require no application process to own either recovered Personal or BFM database and no unexpected matching WAL/SHM sidecar; capture sanitized source hashes and metadata; create mode-700 byte-identical disposable working copies outside the repository; verify copy/source equality; run the Flask application and fresh installed-Chrome checks against only those copies in a sterile child environment with a synthetic Flask secret, no authentication hash, no `.env` loading, no Plaid/OpenRouter/downstream credentials, and denied non-localhost networking; verify Dashboard, Transactions, To Do, and Recurring Review for both Personal and BFM using only route status, expected title/landmark presence, and error counts; permit normal initialization, migration, WAL, and category synchronization only on the disposable copies; compare copy integrity, schema version, and aggregate table-count deltas without retaining row values; close all processes; remove the exact disposable directory; prove the recovered originals and existing dirty worktree remained unchanged; write one sanitized evidence log and Runway OS closeout; and stop.

Excluded: Task 2.2 (`P5-T22`); Task 2.5 (`P5-T25`); Tasks 2.7-2.8 (`P5-T27`-`P5-T28`); Tasks 3-4 (`P5-T3`-`P5-T4`); opening the original recovered databases through Flask; mutation of originals or protected recovery copies; screenshots, traces, videos, downloads, response or HTML/body dumps, console message text, merchant/account/transaction/financial values, or row-level reporting; 5G implementation resume or completion; product/test edits; authentication, migration, database, detector, category-domain, financial, or application behavior changes; Luxe Legacy; Plaid; OpenRouter; credentials; staging, commit, push, PR, workflow, Fly, deployment, production, delegation, second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: both recovered entities need the same protected-copy lifecycle, sterile application environment, route matrix, integrity and aggregate checks, original-preservation proof, and exact cleanup before Ryan can decide whether 5G may resume. Product implementation and every later Phase 5 task depend on this result and use different authority and verification paths.

Owner and recommended agent: Codex Desktop without delegation. The block requires protected-data boundary control, application/browser orchestration, mixed-worktree preservation, sanitized evidence, and Runway OS stewardship. No independent second opinion is needed for this mechanical verification.

Runner path: record and render active 5G-AV state; hash and inventory the exact originals without SQLite application access; require no owner or unexpected sidecar; create and verify exact protected disposable copies; run the application in a fresh sterile child environment on an ephemeral localhost port; verify the bounded Personal/BFM route matrix with fresh installed Chrome and denied external networking; record only sanitized pass/fail and aggregate metadata; close every process; remove the validated disposable directory; prove original and worktree preservation; close Runway OS locally; and stop.

Expected paths and surfaces: no tracked product or test changes; exact recovered `local_state/personal.sqlite` and `company.sqlite` only for read-only metadata, hashing, and copying; one validated mode-700 temporary directory outside the repository; Dashboard, Transactions, To Do, and Recurring Review for Personal and BFM; one sanitized `command-center/logs/2026-07-27-recovered-database-application-verification-5g-av.md`; and `command-center/decisions.md`, `now.md`, `roadmap.md`, `state.json`, and generated `index.html`.

Defaults: verify Personal then BFM; use byte-identical disposable copies rather than opening originals through Flask; set a synthetic Flask secret and no authentication hash; omit every live-integration credential; deny non-localhost networking; retain only route/status/landmark/error-count, integrity, schema-version, and aggregate-delta evidence; produce no screenshot, trace, video, response body, HTML dump, console text, protected label, or financial value; remove the exact temporary copies after all processes close; leave the result local, unstaged, uncommitted, and unpublished; and return even a clean pass to Ryan before any 5G resume.

Stop conditions: source hash or metadata drift from the accepted recovery state; unexpected Personal/BFM WAL/SHM sidecar or database owner; copy mismatch; inability to constrain `DATA_DIR` to the disposable directory; any original-path application access; external network request, credential, or live dependency; integrity result other than `ok`; unexpected financial/workflow aggregate mutation; route status, required title/landmark, page-error, console-error, or browser failure; need to retain or disclose protected details; product or preserved-file drift; temporary cleanup, JSON, dashboard, rendered-state, whitespace, real-index, or health failure; or need for any excluded action.

Verification: source file inventory, hash, owner, and sidecar checks; copy/source hash equality; sterile environment and denied-network proof; bounded eight-route Personal/BFM status and landmark matrix; copy integrity and schema version before and after; aggregate table-count deltas that distinguish allowed schema/category initialization from forbidden financial/workflow mutation; no screenshots/traces/body or console-text retention; exact browser/server/database cleanup; removed disposable directory; unchanged original hashes and metadata; unchanged existing product and preserved-file hashes; empty real Git index; JSON; dashboard refresh/currentness/health and rendered state; and `git diff --check`.

Dashboard closeout: while active, show 5G-AV, Task 2.4, Codex ownership, stop conditions, verification, and sanitized closeout as the next report point. On pass or stop, record the exact sanitized stage, return control to Ryan, keep Task 2.4 blocked and 5G stopped, and do not claim product completion, durability, publication, deployment, or production verification.

Report point: return application readiness per entity and route, any schema/category-only aggregate delta, proof that originals and existing worktree were preserved, exact temporary cleanup, and a recommendation on whether Ryan should consider separately confirming 5G resume.

Expansion candidates and questions: none. A clean 5G-AV result does not activate 5G implementation, publication, or any later Phase 5 task.

Suggested next work block: after a clean 5G-AV pass, separately propose 5G-RS for Recurring Review resume and local closeout. If 5G-AV stops, plan a separate sanitized diagnosis instead. Do not begin either sequel inside 5G-AV.

Stop result: the confirmed proposal was written into Runway OS; `state.json` parsed; dashboard generation, generated-state currentness, health, whitespace, and empty-index checks passed; and the existing dirty-file set was inventoried and hashed. The required rendered dashboard inspection could not proceed because the selected in-app browser rejected the local `file:` URL under its security policy and explicitly prohibited browser workarounds or alternate browser surfaces. 5G-AV stopped before process-owner, sidecar, database hash, metadata, copy, SQLite, Flask, Chrome application-route, or aggregate-table access. Neither recovered original nor any protected recovery copy was touched, no disposable directory was created, and no protected output, product change, Git, GitHub, workflow, Fly, Plaid, deployment, production, delegation, or second-opinion action occurred. Ryan may visually verify the generated dashboard and separately authorize re-entry from the exact pre-copy boundary. Evidence: `command-center/logs/2026-07-27-recovered-database-application-verification-5g-av.md`.

### Confirmed Work Block 5G-RC-R: Recovery Record Direct-Main Durability

Status: complete; recovery record durable on `main` without workflow or deployment.

Included: from exact aligned base `3ffd94bafc2eba375a795ed3e5df26e3615e79c4`, explicitly stage the five command-center sources plus the 5G stop, 5G-RA, and 5G-RC logs; require exact diff and sensitive-data review; commit with `[skip actions]`; push the fast-forward commit directly to `origin/main`; prove GitHub recorded no workflow or deployment for that SHA; then write one sanitized 5G-RC-R closeout log, update only the five command-center sources, commit those six paths with `[skip actions]`, push directly to `origin/main`, and verify no workflow plus final local branch, local `main`, and remote `main` alignment.

Excluded: README; `scripts/smoke_test.py`; all subscription route/template/controller/style product changes; databases, `local_state`, and protected recovery copies; application access, migrations, 5G resume, product durability or release, PR creation, workflow dispatch/rerun/cancellation, deployment, production, Fly, Plaid, force push, rebase, conflict resolution, branch deletion, delegation, second opinion, and the three preserved unrelated files.

Stop conditions: local or remote `main` drift; unexpected staged path, diff, or sensitive content; JSON, dashboard, rendered-state, whitespace, exact-path, preserved-file, Git, push, or zero-workflow failure; non-fast-forward or need for force/rebase/conflict resolution; any workflow or deployment; or need for an excluded action.

Verification: GitHub authentication; exact refs and ancestry; explicit paths; JSON; dashboard refresh, health, and rendered state; whitespace; sensitive additions; exact staged diff; `[skip actions]` commit messages; fast-forward direct-main pushes; exact remote SHA; zero workflows/check runs/deployment for both commits; empty final index; preserved hashes; and retained incomplete product changes only in the local worktree.

Report point: return both commit SHAs, exact published paths, zero-workflow/deployment proof, final refs, retained local product work, preserved exclusions, and the still-separate application-verification and 5G-resume gates.

Result: exact eight-path recovery-record source commit `77236737c7e8218e8570bb3a358e2d83db054945`, with expected parent `3ffd94bafc2eba375a795ed3e5df26e3615e79c4`, is durable on `origin/main`. Exact-path, staged-diff, whitespace, and high-confidence sensitive-addition checks passed, and GitHub reported zero workflow runs and zero check runs for the source commit. The containing exact six-path command-center-only closeout uses `[skip actions]`, records the completed recovery as durable, and requires final exact-ref and zero-workflow confirmation. The incomplete README and 5G product/test changes remain local; no application access, 5G resume, product publication, PR, workflow action, deployment, production, database, protected recovery-copy, or preserved unrelated-file action occurred. Evidence: `command-center/logs/2026-07-27-recovery-record-direct-main-durability-5g-rc-r.md`.

### Confirmed Work Block 5G-RC: Immediate Personal/BFM Snapshot Recovery

Status: complete and verified locally; application access and 5G resume remain separate.

Included: freeze exact current Personal/BFM SQLite file sets; prove no application process owns them; create and verify an exact protected post-incident safety copy under `local_state/backups/`; mount exact snapshot `com.apple.TimeMachine.2026-07-27-071321.local` read-only using a direct macOS administrator prompt if required; inspect only the exact Personal/BFM SQLite file sets; require both base databases and successful SQLite integrity checks; preserve ownership and modes; replace only the current exact Personal/BFM SQLite sets with the snapshot sets; prove restored hashes equal source hashes and integrity passes; unmount and clean temporary access.

Excluded: row-value reporting, application access, migrations, demo seed, sync, backup utilities outside the exact safety copy, Luxe Legacy, product/test work, 5G resume, staging, commit, push, PR, workflow, Fly, Plaid, deployment, production, delegation, second opinion, and all unrelated files.

Stop conditions: snapshot, path, or file-set ambiguity; absent Personal or BFM base database; writable snapshot mount; integrity failure; unexpected active database owner; safety-copy creation or verification failure; replacement, equality, ownership, mode, or integrity failure; unexpected path; cleanup failure; or need for an excluded action.

Verification: exact snapshot identity and read-only mount; source/current/safety-copy file-set inventories and SHA-256 values without row output; SQLite integrity before and after; exact source-to-restored equality; unchanged unrelated files; unmounted snapshot; removed temporary access; empty Git index; JSON, dashboard refresh and health, and rendered dashboard.

Report point: return restored Personal/BFM status, exact snapshot, safety-copy location, equality and integrity proof, cleanup, and the separate application-verification and 5G-resume gates.

Result: exact post-incident Personal and BFM files were preserved byte-for-byte under protected `local_state/backups/5g-recovery-20260727-0753-post-seed/`. Time Machine exposed exact snapshot `com.apple.TimeMachine.2026-07-27-071321.local` as protected read-only `Data@snap-79315582`. Its exact Personal and BFM base databases, with no matching WAL/SHM sidecars, were copied by Finder into protected snapshot staging; both differed from the post-seed copies and passed SQLite integrity. Exact same-directory temporary replacements were verified and atomically renamed over only the two live targets. Restored live hashes equal their staged snapshot sources, integrity passes, ownership and modes are preserved, and aggregate checks restore 691 Personal and 1,303 BFM transactions—the exact pre-seed counts—plus associated affected-table aggregates. The exact recovery snapshot was unmounted without force. Four unrelated older system-managed read-only mounts remained busy and were left to macOS rather than force-unmounted. No application access, migration, seed, sync, Luxe Legacy, 5G resume, Git publication, deployment, production, or live action occurred. Evidence: `command-center/logs/2026-07-27-immediate-personal-bfm-snapshot-recovery-5g-rc.md`.

### Confirmed Work Block 5G-RA: Personal/BFM Local-Database Recovery Assessment

Status: stopped safely at the non-privileged read-only mount boundary; assessment incomplete and no restore authority consumed.

Included: resolve the exact pre-incident local Time Machine snapshot `com.apple.TimeMachine.2026-07-27-071321.local` through read-only metadata; mount that exact snapshot at a disposable exact path only if necessary, only read-only, and only if possible without a privilege prompt; locate only snapshot copies of `/Users/ryanbuffington/Documents/GitHub/expense-tracker/local_state/personal.sqlite` and `company.sqlite`; collect only existence, size, and modification time; run SQLite `PRAGMA integrity_check` against each snapshot file; report only sanitized file metadata and aggregate integrity results; unmount and remove the empty temporary mount path if one was created.

Excluded: SQLite row queries, schema/content browsing beyond `PRAGMA integrity_check`, row counts, financial values, copies, exports, restore, replacement, recovery writes, current-database reads beyond file metadata, application access, seed/migration/sync/backup commands, Luxe Legacy, 5G implementation or resume, product/test work, staging, commit, push, PR, workflows, Fly, Plaid, deployment, production, credentials, protected-data disclosure, delegation, second opinion, and all three preserved unrelated files.

Why this grouping: snapshot resolution, exact-path metadata, file presence, integrity, and read-only cleanup answer one question—whether an apparently intact pre-incident recovery source exists—without consuming the separate authority required to copy or restore it.

Owner and recommended agent: Codex Desktop without delegation. Ryan retains every recovery selection, copy, restore, replacement, row inspection, application access, resume, durability, publication, and live-action decision.

Runner path: record and verify active 5G-RA state; capture current Personal/BFM file metadata; resolve the exact snapshot and volume using read-only system metadata; if direct access is unavailable, inspect the local mount utility contract and attempt only an exact read-only mount without `sudo`; prove the mount is read-only; check exact snapshot paths, metadata, and `PRAGMA integrity_check`; unmount and clean the temporary path; prove current database metadata, real index, and preserved hashes are unchanged; write a sanitized assessment closeout; and stop.

Stop conditions: snapshot identifier, volume, mount, or path ambiguity; missing Personal or BFM snapshot database; any need for writable access, `sudo`, administrator authentication, a privilege prompt, copying, restoration, current-database content access, or another excluded action; mount not proven read-only; SQLite integrity output other than `ok`; current database metadata drift; temporary cleanup failure; unexpected path; dashboard, JSON, scope, index, or preserved-file failure.

Verification: exact snapshot identifier and timestamp; exact Data-volume identity; current Personal/BFM size and modification time before and after; snapshot file existence, size, and modification time; explicit read-only mount evidence if mounted; `PRAGMA integrity_check` aggregate output only; exact unmount and empty temporary cleanup; JSON, dashboard refresh and health, `git diff --check`, empty real index, and preserved hashes.

Dashboard closeout: while active, show 5G-RA as current, keep Task 2.4 blocked and 5G stopped, and identify Codex as assessment owner. On completion or stop, record only the recoverability finding, return control to Ryan for a separately confirmed restore decision, and do not restore or resume 5G.

Report point: return whether both exact pre-incident database files exist and pass integrity, sanitized metadata, any assessment limitation, proof that current databases remained frozen and temporary access was removed, and the exact separate restore gate.

Stop result: read-only `tmutil` and APFS metadata confirmed exact snapshot `com.apple.TimeMachine.2026-07-27-071321.local` on Data volume `/dev/disk3s5`, with UUID `B0AB8CCC-80CA-4A76-970F-DB1279B16571` and XID `79315582`. One exact non-privileged `mount_apfs` attempt specified `rdonly,nobrowse`, the exact snapshot, exact device, and a disposable `mktemp` directory. macOS returned `Operation not permitted` with exit code 77. The directory was removed; no snapshot mounted; no snapshot database path, row, or content was accessed; no file presence or integrity result was obtained; current Personal/BFM file size and modification time remained unchanged; preserved hashes remained unchanged; and the real Git index remained empty. A separately confirmed privileged read-only assessment or another exact recovery path is required before any copy or restore decision. Evidence: `command-center/logs/2026-07-27-personal-bfm-local-database-recovery-assessment-5g-ra.md`.

### Confirmed Work Block 5G: Recurring Review And Cancellation Clarity

Status: done locally through the recovery, application-readiness, safe-resume, and rendered-closeout sequence; unstaged, uncommitted, and unpublished.

Included: Task 2.4 (`P5-T24`) only. Treat `/subscriptions/` as a combined workflow for reviewing detected recurring charges and tracking selected charges for watching or cancellation without claiming complete recurring-spend coverage. Keep the existing route. Rename the visible surface to `Recurring Review`; add concise purpose copy; place tracked charges before the detected-review queue; show an exact remaining-review count; replace icon-only queue actions with visible Track and Dismiss controls; provide an immediate accessible undo path after dismissal; preserve existing dismissal restoration; and keep existing watching, cancelling, cancelled, manual-add, detail, charge-history, notes, account-information, cancellation-tip, entity-isolation, authentication, CSP, PWA, and responsive behavior.

Excluded: Task 2.2 (`P5-T22`) and 5D; Task 2.5 (`P5-T25`); Tasks 2.7-2.8 (`P5-T27`-`P5-T28`); Tasks 3-4 (`P5-T3`-`P5-T4`); recurring kind or classification models; detector thresholds, cadence logic, query semantics, or completeness claims; database migrations; financial/category/reporting behavior; authentication, session, CSRF, CSP, PWA, service-worker, Ask Opus, AI-data, or URL changes; Luxe Legacy setup or downstream writes; real or protected financial, payroll, database, upload, or credential data; Plaid, Fly, production, demo, workflow, GitHub, staging, commit, push, PR, merge, deployment, or publication action; delegation, second opinion, broader recovery; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: page purpose, naming, section order, queue progress, visible actions, and dismissal undo form one coherent usability contract on the existing subscriptions surface. The nearest remaining tasks introduce separate privacy, information-architecture, offline, runbook, publication, or phase-closeout decisions.

Owner and recommended agent: Codex Desktop without delegation or another second opinion. The block requires integrated Flask, Jinja, JavaScript, CSS, synthetic-test, rendered-browser, and Runway OS stewardship. The completed 5B independent critique already provides the relevant external review.

Runner path: record and render active 5G state; create local `codex/recurring-review-surface`; establish the synthetic baseline; implement only the confirmed combined review-and-track presentation and safe undo behavior; add focused all-entity temporary-data coverage; run focused and complete verification; inspect sanitized rendered desktop, phone, and exact-tablet results; write one local evidence and Runway OS closeout; leave the real index empty; and stop.

Expected paths and surfaces: `web/routes/subscriptions.py` only if required for count or undo presentation; `web/templates/subscriptions.html`; `web/templates/todo.html`; `web/static/subscriptions.js`; `web/static/style.css`; `scripts/smoke_test.py`; `README.md`; one sanitized 5G evidence log; and the source/generated Runway OS paths. No database, migration, workflow, configuration, dependency, category, authentication, PWA, protected-data, or production path is expected.

Defaults: use `Recurring Review` as the page and To Do label; keep `/subscriptions/`; explain that the page reviews detected recurring charges and tracks selected charges for watching or cancellation; show tracked charges first and detected charges second with an exact `{N} to review` count; use visible Track and Dismiss labels while retaining or improving accessible names; provide an immediate safe undo after dismissal and keep the durable dismissed list; do not change internal lifecycle values, detector logic, category grouping, tips behavior, or Ask Opus; use temporary synthetic data only; keep the result local, unstaged, uncommitted, and unpublished.

Stop conditions: the work requires a new kind model, migration, detector or query change, persistent classification, financial or category semantic change, authentication/session/CSRF/CSP/PWA contract change, URL migration, protected or live access, unexpected paths, or preserved-file overlap; immediate undo cannot be implemented without widening data handling; lifecycle, entity isolation, modal, keyboard, responsive, or route behavior regresses; scope expands into another Task 2 slice or GitHub/production action; or focused/full verification, cleanup, dashboard, rendered-state, whitespace, empty-index, or preserved-hash checks fail in a plan-changing way.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused temporary Personal, BFM, and Luxe Legacy order/count/Track/Dismiss/decrement/undo/restore/empty/manual-add/status/notes/detail/account-info/tips/delete and exact-cleanup coverage; unchanged detector fixture outputs; complete configured-auth/no-password installed-Chrome suite; desktop, 390px phone, exact-768, keyboard, modal, responsive, console, denied-network, and rendered inspection; Python and tracked-JavaScript syntax; maintained CI/Fly safety; JSON; dashboard refresh/currentness/health and rendered state; whitespace; sensitive additions; exact paths; zero staging; and preserved-file hashes.

Dashboard closeout: while active, show 5G, Task 2.4, Codex ownership, stop conditions, verification, and local closeout as the next report point. On success, mark 5G and Task 2.4 complete locally, keep Phase 5 active, leave Task 2.5 and every later decision separate, and do not claim GitHub durability, production release, Task 3, or final Phase 5 completion.

Report point: return the frozen purpose contract, exact labels/order/count/undo behavior, changed paths, lifecycle and detector-preservation proof, complete synthetic and rendered verification, cleanup, branch/index state, preserved exclusions, and any discovered constraint.

Expansion candidates and questions: none. Confirmation accepts the combined review-and-track purpose; cancellation-only, complete-register, kind-model, Ask Opus, information-architecture, offline, runbook, publication, and production alternatives remain outside 5G.

Suggested next work block: after a clean local 5G result, separately decide whether to authorize 5G-R for exact branch durability, hosted review, and any release path. Do not begin 5G-R inside 5G.

Final result: 5G initially stopped at the protected local-data boundary after the seed utility unexpectedly executed. The separately confirmed 5G-RC and 5G-RC-R sequence restored the exact pre-incident Personal and BFM files and made the sanitized recovery record durable without deployment; 5G-AV-R then proved both recovered databases application-ready through disposable-copy checks and two Ryan-rendered checkpoints. Confirmed 5G-RS resumed only the preserved seven-file implementation, required no correction, and passed the full synthetic, both-auth installed-Chrome, desktop, exact-768, phone, denied-network, preservation, and cleanup contract. Ryan returned the exact `5G-RS closeout dashboard verified` attestation. Task 2.4 and 5G/5G-RS are complete locally, unstaged, uncommitted, and unpublished. Evidence: `command-center/logs/2026-07-27-recurring-review-cancellation-clarity-5g-stop.md`, `command-center/logs/2026-07-27-immediate-personal-bfm-snapshot-recovery-5g-rc.md`, `command-center/logs/2026-07-27-human-verified-dashboard-reentry-5g-av-r.md`, and `command-center/logs/2026-07-27-recurring-review-safe-resume-5g-rs.md`.

### Confirmed Work Block 5F-R2: Verified Draft PR Production Release

Status: done, durable on `main`, automatically deployed once, zero-annotation checked, credential-free health verified, and closed with one command-center-only `[skip actions]` commit.

Included: Task 4 (`P5-T4`) only for the release checkpoint of the verified 5A-5F set on draft PR [#89](https://github.com/rabuffington22/expense-tracker/pull/89). Record active 5F-R2 state; publish one exact five-path command-center activation commit without a skip token to the feature branch; require the resulting exact PR head to pass automatic core-then-browser Synthetic CI with zero annotations; reverify unchanged `main`, exact PR base/head/state, mergeability, and checks; mark PR #89 ready for review; merge it with a merge commit preserving the verified history; observe only the resulting automatic exact-SHA push-triggered Fly Deploy; require every deployment step to succeed with zero annotations; verify bounded credential-free `https://ledger-oak.fly.dev/health`; publish one sanitized six-path `[skip actions]` command-center release closeout directly to `main`; prove the closeout caused no second deployment; retain the feature branch; and stop.

Excluded: Task 2.2 (`P5-T22`) and 5D; Tasks 2.4-2.8 (`P5-T24`-`P5-T28`); Task 3 (`P5-T3`); final Phase 5 closeout or parent-project pointer; any further product, maintained-test, workflow, dependency, runtime, configuration, category, database, authentication, PWA, Ask Opus, recurring-surface, connection, offline, or design change; Luxe Legacy setup or downstream writes; Plaid link, sync, disconnect, or account action; Fly CLI, console, SSH, secrets, restart, rollback, or manual deployment; authenticated production pages; real or protected financial, payroll, database, upload, or credential data; manual workflow dispatch, rerun, cancellation, or repair; force push, rebase, conflict resolution, branch deletion, broader recovery, delegation, second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the activation head, final PR CI, ready transition, merge, exact automatic deployment, credential-free health check, and no-second-deployment closeout form one production-release chain with one authority and evidence path. Task 3 and the remaining Task 2 choices depend on the release result and use different product or documentation decisions.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact-path Git and PR handling, automatic-workflow observation, bounded public health verification, command-center stewardship, stop enforcement, and final intake. Ryan retains every expansion, rollback, repair, protected action, and subsequent product or phase decision.

Runner path: verify refs, PR state, GitHub authentication, safety contracts, preserved hashes, and a clean intended worktree; record and render active 5F-R2 state; run the local release preflight; explicitly stage, commit, and push only the five activation paths; require a fresh exact-head PR-only core-then-browser pass with zero annotations; reverify all merge preconditions; mark PR #89 ready and merge it with a merge commit; verify the exact merge SHA and parents; observe the one automatic push-triggered Fly Deploy and every step; require zero annotations; make at most three credential-free `/health` requests over two minutes after the successful deployment; write and verify one sanitized six-path release closeout; commit it directly to `main` with `[skip actions]`; non-force push; prove no second deployment; retain the feature branch; and stop.

Expected paths and surfaces: activation changes only `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json`. Closeout changes those same five paths plus one new sanitized 5F-R2 log. External surfaces are PR #89, its automatic Synthetic CI, the automatic Fly Deploy, and the credential-free production `/health` endpoint. No application, test, workflow, Fly configuration, or protected-data file changes are expected.

Defaults: use a merge commit rather than squash or rebase; preserve the verified commit history; prefer the GitHub connector for ready and merge, with authenticated `gh` limited to the exact same operations only if the known integration permission limitation recurs; require a fresh PR CI pass after activation; allow at most three credential-free health requests over two minutes after successful deployment; use `[skip actions]` on the command-center-only closeout; retain the feature branch; treat an independently scheduled Daily Plaid Sync as unrelated and do not inspect or operate it.

Stop conditions: local, remote, live `main`, feature head, PR base/head/state, mergeability, checks, annotations, paths, sensitive-data, preserved-file, dashboard, or cleanup drift; any failed, missing, delayed, out-of-order, or annotated PR job; a review requirement, conflict, force operation, or different merge method; unexpected merge SHA or parents; a missing, non-push, wrong-SHA, failed, delayed, duplicated, or annotated Fly deployment; production health outside the bounded successful contract; any workflow on the `[skip actions]` closeout SHA; push rejection; or any need for rollback, repair, rerun, cancellation, Fly administration, protected access, broader recovery, or excluded work. On a hosted or production stop, perform sanitized read-only diagnosis only.

Verification: current refs, ancestry, GitHub authentication, PR metadata, exact paths, preserved hashes, full synthetic smoke, maintained Synthetic CI and Fly safety, Python and tracked-JavaScript syntax, JSON, dashboard refresh/currentness/health and rendered state, whitespace, sensitive additions, cleanup, activation commit and remote SHA, fresh exact-head PR event and SHA, core-before-browser order, every step and annotations, ready/merge state, merge commit parents and remote `main`, exact automatic Fly Deploy event/SHA/job/steps and zero annotations, bounded credential-free `{"status":"ok"}`, exact six-path `[skip actions]` closeout, no second deployment, final refs, clean index, and only the three preserved untracked files.

Dashboard closeout: while active, show 5F-R2 with Task 4 and Codex as owner. On success, mark 5F-R2 done, keep Phase 5 active at 38%, do not claim Task 3 or final Phase 5 completion, record Task 4's verified production-release checkpoint while keeping its final parent-pointer work later, and return the next Task 2 direction choice to Ryan.

Report point: return the activation SHA and PR CI run/job IDs; final PR state; merge SHA and parents; deployment run/job IDs, step results, and annotations; production-health result; closeout SHA and no-second-deployment proof; final refs, branch retention, preserved hashes, exclusions, and the next separately gated direction.

Expansion candidates and questions: none. Task 3 and the remaining Task 2 work depend on the release result and remain separate.

Suggested next work block: after successful 5F-R2, separately plan a Ryan-owned Task 2.4 (`P5-T24`) recurring-surface purpose decision unless Ryan chooses another remaining Phase 5 direction. Do not begin Task 3 or final Phase 5 closeout in 5F-R2.

Result: the exact five-path activation commit `13d2f16a9cca8b8d4fb4900006dfaa9655824474` passed fresh pull-request Synthetic CI run `30262719321`; core job `89966154249` and later browser job `89966350270` passed every step with zero annotations. PR #89 was marked ready and merged with merge commit `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce`, whose parents are the accepted prior `main` baseline and exact activation head. Exactly one automatic push-triggered Fly Deploy run, `30263216876`, ran for the merge SHA; deploy job `89967738107` passed every step with zero annotations. One credential-free production-health request returned sanitized `{"status":"ok"}`. The GitHub integration's known write-permission boundary required only the confirmed authenticated CLI fallback for ready and merge. The one sanitized six-path closeout uses `[skip actions]` and must have no workflow on its SHA. No excluded action occurred. Evidence: `command-center/logs/2026-07-27-verified-draft-pr-production-release-5f-r2.md`.

### Confirmed Work Block 5F-RR: Verified Set Branch Publication Retry

Status: verified on open draft PR [#89](https://github.com/rabuffington22/expense-tracker/pull/89); the exact six-path closeout head must satisfy its automatic final-head Synthetic CI contract before the result is final.

Included: Task 4 (`P5-T4`) only for exact feature-branch durability and hosted PR-only review of the verified 5A-5F outputs from Tasks 1.1-1.4 (`P5-T11`-`P5-T14`), Task 2.1 (`P5-T21`), Task 2.3 (`P5-T23`), and Task 2.6 (`P5-T26`). Revalidate the exact 76-path candidate; explicitly stage only its 17 tracked modifications and 59 intended untracked Phase 5 artifacts, logs, handoff files, contracts, and evidence; create one release-candidate commit without a skip token; non-force push the current feature branch; open one draft PR targeting `main`; observe automatic PR-only core-then-browser Synthetic CI; after a clean first pass create one sanitized six-path closeout commit without a skip token; require final-head CI; retain the remote branch; leave the PR open, draft, and unmerged; and verify zero Fly deployment.

Excluded: Tasks 2.2, 2.4-2.5, 2.7-2.8, and 3; any further product, maintained-test, dependency, workflow, runtime, configuration, category, database, authentication, PWA, Ask Opus, recurring-surface, connection, offline, or design change; Luxe Legacy setup or downstream writes; merge or push to `main`; production deployment or health access; ready-for-review transition; manual workflow dispatch, rerun, cancellation, or repair; Fly, Plaid, demo, production, downstream, credential, protected, database, upload, payroll, or real financial-data access; branch deletion; force push; rebase; conflict resolution; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the 76 paths are one verified release candidate with one exact-path Git publication and hosted-review path. The sanitized closeout belongs in the same block because it records the first hosted result and requires the final durable PR head to pass the identical checks. Merge and production have a different risk class and remain later.

Owner and recommended agent: Codex Desktop using the GitHub publishing workflow, without delegation or second opinion. Codex owns exact-path Git handling, Runway OS stewardship, draft-PR publication, hosted-run observation, zero-deployment proof, stop enforcement, and final intake. Ryan retains merge, production, and every broader decision.

Runner path: verify local and remote `main`, the absent remote feature branch and matching PR, GitHub authentication, exact candidate and preserved hashes; record and render active state; run the complete local publication preflight; explicitly stage and commit only the 76 approved paths; push the branch with tracking; open one draft PR to `main`; observe first-head Synthetic CI; on clean success write and publish one sanitized six-path closeout; observe final-head Synthetic CI; and stop unmerged.

Expected paths: the existing 76-path candidate; active Runway OS changes within the same tracked command-center files; then one new sanitized 5F-RR evidence log plus `command-center/decisions.md`, `command-center/index.html`, `command-center/now.md`, `command-center/roadmap.md`, and `command-center/state.json` in the closeout commit.

Defaults: use one candidate commit and one sanitized closeout commit, both without skip tokens; reuse the completed local browser pass only if every product and browser-test hash remains unchanged; require hosted browser CI on both PR heads; keep the PR draft and open; retain the remote branch; treat an unrelated scheduled Daily Plaid Sync as outside the block unless it contradicts the candidate SHA or workflow boundary; perform no production health check because this block must produce zero deployment.

Stop conditions: local, remote, or live `main` drift; candidate, sensitive-data, preserved-file, stage, commit, ancestry, push, PR, workflow, hosted-order, annotation, zero-deployment, cleanup, dashboard, or verification drift; push rejection or need for force, rebase, conflict resolution, or broader recovery; missing, failed, delayed, out-of-order, or unexpectedly annotated hosted jobs; any Fly deployment or unexpected workflow; or any need for repair, rerun, cancellation, merge, protected access, or excluded action. On a hosted stop, leave the draft PR open and perform read-only diagnosis only.

Verification: full synthetic smoke; maintained Synthetic CI and Fly safety; Python and tracked-JavaScript syntax; JSON; dashboard refresh/currentness/health and rendered inspection; whitespace; high-confidence sensitive additions; exact changed, staged, committed, and remote paths; preserved hashes; branch ancestry; draft PR base/head/draft state; both exact-head pull-request events and SHAs; core-before-browser order and every hosted step; annotations; cleanup; zero Fly deployment; and final branch/PR alignment.

Dashboard closeout: while active, show 5F-RR with Task 4 and Codex as owner. On success, mark 5F-RR done on the verified open draft PR, keep Phase 5 at 38%, keep Task 3 planned, return Task 4 to Ryan for a separately confirmed 5F-R2 production-release decision, and do not claim merge, deployment, or final Phase 5 closeout.

Report point: return exact candidate and closeout SHAs, draft PR URL and base/head/state, local verification, hosted run/job IDs and steps, annotations, zero-deployment evidence, preserved exclusions, final branch/PR state, and the separately gated 5F-R2 decision.

Expansion candidates and questions: none. Merge and production introduce a higher-risk automatic deployment and remain excluded. No clarification is required inside 5F-RR.

Suggested next work block: 5F-R2 to separately authorize merge to `main`, observe only the resulting automatic Fly deployment, verify credential-free production health, and record the release closeout without beginning Task 3 or final Phase 5 closeout.

Result: the exact 76-path candidate was committed as `a87676235c5d79b4347517962cd3ce8a3134b482`, non-force pushed to `codex/phase-5-usability-baseline`, and opened as draft PR [#89](https://github.com/rabuffington22/expense-tracker/pull/89) targeting `main`. Candidate pull-request Synthetic CI run `30239840256` passed every core step in job `89894583340` and every later browser step in job `89894693185`; both jobs had zero annotations, and the candidate SHA had no Fly Deploy run. Local preflight, exact-path, provenance, preserved-file, cleanup, and zero-deployment checks passed. The one authorized sanitized six-path closeout commit carries this result and must itself pass the same exact-head PR-only contract before completion may be claimed. The PR remains open, draft, and unmerged; production and 5F-R2 remain separately gated. Evidence: `command-center/logs/2026-07-27-verified-set-branch-publication-retry-5f-rr.md`.

### Confirmed Work Block 5F-R: Phase 5 Verified Set Branch Durability And Hosted Review

Status: stopped locally on `codex/phase-5-usability-baseline` at the confirmed staged-whitespace gate before commit, push, PR, workflow, merge, or deployment.

Included: Task 4 (`P5-T4`) only for branch durability and hosted CI review of the already-complete outputs from Tasks 1.1-1.4 (`P5-T11`-`P5-T14`), Task 2.1 (`P5-T21`), Task 2.3 (`P5-T23`), and Task 2.6 (`P5-T26`). Revalidate the accumulated verified 5A-5F candidate; explicitly stage only the approved tracked source, maintained tests, sanitized artifacts, Claude Design handoff and returned-review evidence, logs, Phase 5 artifacts, and Runway OS paths; commit the exact candidate; non-force push the current feature branch; open one draft PR targeting `main`; observe the automatic PR-only `Synthetic CI` core-then-browser jobs; publish one sanitized branch closeout commit; require the final PR head to pass the same hosted workflow; leave the PR open, draft, and unmerged; and verify zero Fly deployment.

Excluded: Tasks 2.2, 2.4-2.5, 2.7-2.8, and 3; any further product, test, dependency, workflow, runtime, configuration, category, migration, authentication, CSRF, CSP, PWA, Ask Opus, recurring-surface, connection-discovery, offline-recovery, or design change; Luxe Legacy setup or downstream writes; merge or push to `main`; ready-for-review transition; production deployment or health access; manual workflow dispatch, rerun, cancellation, or repair; Fly, Plaid, demo, production, downstream, credential, protected, database, upload, payroll, or real financial-data access; branch deletion; force push; rebase; conflict resolution; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the accumulated 5A-5F source, tests, sanitized evidence, design-review packet, and Runway OS record are one release candidate with the same exact-path staging, local verification, branch publication, PR-only hosted verification, and no-deployment proof. Later product choices, final documentation, merge, and production release use different authority, risk, and verification paths.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact-path Git handling, command-center stewardship, GitHub draft-PR publication, hosted-run observation, no-deployment proof, stop enforcement, and final intake. Ryan owns any scope expansion, merge, production release, protected action, or later Phase 5 decision.

Runner path: keep the existing `codex/phase-5-usability-baseline` branch; record and verify active 5F-R state; confirm local and remote `main` remain at the accepted Phase 5 baseline; preserve the three unrelated untracked files; run the complete local safety bundle; create one exact release-candidate commit without a skip token; push the branch with tracking; open one draft PR to `main`; observe the exact automatic core-then-browser `Synthetic CI` run; on clean success, write one sanitized 5F-R evidence and Runway OS closeout commit without a skip token; push it; observe the final-head core-then-browser run; and stop with the draft PR open and unmerged.

Expected paths: the seventeen tracked Phase 5 paths already changed on the branch; the fifty-seven intended untracked Phase 5 files under `command-center/artifacts/phase-5/`, `command-center/handoffs/claude-design/2026-07-26-ledger-usability-5b/`, the five 2026-07-26 5A/5B/5C/5E/5F logs, and the three Phase 5 contract/baseline/intake artifacts; one sanitized 5F-R evidence log; and the active/closeout Runway OS source and generated-dashboard paths. No unrelated untracked file may enter either commit.

Defaults: use one release-candidate commit followed by one sanitized closeout commit; require hosted CI on the final PR head; keep the PR draft and open; retain the remote feature branch; do not use a skip token on either PR commit; treat an independently scheduled Daily Plaid Sync as unrelated unless its event or SHA contradicts the block; make no product edit during durability; keep Luxe Legacy setup parked; and reserve merge-to-`main` plus automatic Fly deployment for separately confirmed 5F-R2.

Stop conditions: local, remote, or live `main` drift; unexpected, sensitive, or preserved-file scope; failed full smoke, complete browser coverage, CI/Fly safety, syntax, JSON, dashboard, rendered, whitespace, sensitive-addition, cleanup, exact-stage, ancestry, or preservation check; push rejection or need for force, rebase, conflict resolution, or broader recovery; PR base/head mismatch; a missing, failed, over-window, out-of-order, or unexpectedly annotated hosted job; any Fly deployment or unexpected workflow for either feature SHA; or any need for repair, rerun, cancellation, merge, protected access, or an excluded action. On a hosted stop, leave the draft PR open and perform read-only diagnosis only.

Verification: `.venv/bin/python scripts/smoke_test.py`; complete configured-auth and no-password `scripts/mobile_drawer_browser_test.py`; `scripts/ci_safety_check.py`; Python and tracked-JavaScript syntax; JSON; dashboard refresh/currentness/health and rendered inspection; `git diff --check`; high-confidence sensitive-addition review; exact changed, staged, committed, and remote paths; preserved-file hashes; branch ancestry; draft PR base/head/draft state; exact final-head pull-request event and SHA; core-before-browser order and every hosted step; annotations; cleanup; zero Fly deployment; and final branch/PR alignment.

Dashboard closeout: while active, show 5F-R as the current Phase 5 work block with Task 4 current and Codex as owner. After both hosted runs pass, mark 5F-R verified on the open draft PR, keep Phase 5 active, keep Task 4 current as the Ryan-owned 5F-R2 production-release decision, keep Task 3 planned, and do not claim final Phase 5 closeout.

Report point: return the exact candidate and closeout commits, draft PR URL and base/head, local and hosted verification results, hosted run/job IDs and annotations, zero-deployment evidence, preserved exclusions, branch state, and the separately gated production-release decision.

Expansion candidates and questions: the Task 4 production-release sequel is the nearest candidate but is intentionally excluded because merge-to-`main` triggers a higher-risk automatic Fly deployment. No clarification is required inside 5F-R.

Suggested next work block: 5F-R2 to review and separately authorize merge of the verified draft PR to `main`, observe only the resulting automatic Fly deployment, verify credential-free production health, and publish the release closeout without beginning another product slice or final Phase 5 closeout.

Result: all active-state, branch, remote-main, GitHub-authentication, preserved-file, CI/Fly safety, full smoke, complete both-auth installed-Chrome, syntax, JSON, dashboard currentness/health/rendered, high-confidence secret-pattern, and cleanup checks passed. Codex explicitly staged the exact seventy-four-path candidate, with only the three preserved files remaining untracked. The required staged `git diff --check` then found Markdown trailing-space hard breaks and extra blank EOF lines across Phase 5 evidence, handoff copies, logs, and intake files. Some affected handoff artifacts are tied to packet manifests and prior provenance claims, so normalization would require a separately authorized evidence-package repair. Codex removed only the staged state, preserved every working-tree file, and stopped. No commit, push, PR, workflow, merge, deployment, production action, protected access, Luxe Legacy setup, downstream write, or preserved-file mutation occurred. Evidence: `command-center/logs/2026-07-26-phase-5-verified-set-branch-durability-hosted-review-5f-r.md`.

### Confirmed Work Block 5F-W: Evidence Whitespace And Provenance Normalization

Status: done locally on `codex/phase-5-usability-baseline`; real Git index empty, uncommitted, and unpublished.

Included: Task 4 (`P5-T4`) only for the exact evidence-package prerequisite exposed by 5F-R. Replace intentional terminal two-space Markdown hard breaks with terminal backslashes in the eleven identified Phase 5 evidence, log, handoff-copy, and intake Markdown files; remove only extra blank EOF lines so each affected file ends in exactly one newline; keep the canonical Phase 5 baseline and workflow-review contract byte-identical to their handoff copies; recompute only the two affected entries in the Claude Design packet manifest; preserve the original response ZIP and all five returned Claude artifacts byte-for-byte; preserve the recorded hashes in the local response intake manifest; and prove only the allowed transformations occurred.

Excluded: Tasks 2.2, 2.4-2.5, 2.7-2.8, and 3; every product, maintained-test, workflow, dependency, runtime, configuration, category, database, financial/query/reporting, authentication, CSRF, CSP, PWA, Ask Opus, recurring-surface, connection, offline, or design change; Luxe Legacy setup or downstream writes; protected or real data; credentials; production, demo, Plaid, Fly, or downstream access; real Git staging; commit, push, PR, merge, workflow action, deployment, production health; branch cleanup; force push; rebase; conflict resolution; broader recovery; delegation; second opinion; `scripts/sync_prod_to_local.sh`; `command-center/now 2.md`; and the unrelated duplicate 4AU log.

Why this grouping: the eleven whitespace/EOF repairs and the two directly dependent packet-manifest entries form one mechanical, locally provable provenance repair with a single verification path. Product behavior, publication, merge, deployment, and later Phase 5 work have different risks and remain separate gates.

Owner and recommended agent: Codex Desktop without delegation or second opinion. Codex owns exact evidence edits, manifest reconciliation, command-center stewardship, disposable-index proof, stop enforcement, and final intake. Ryan retains all publication and live-action authority.

Runner path: record and verify active 5F-W state; preserve preimages in a temporary directory; apply only the reviewed line-break and EOF transformations; keep canonical/copy pairs identical; calculate and update only the two dependent packet-manifest hashes; prove the original ZIP, five returned artifacts, response intake recorded hashes, product files, browser-test file, and preserved unrelated files are unchanged; run the complete local verification; use a disposable alternate index for the full intended candidate whitespace gate; keep the real index empty; close locally and return Task 4 to Ryan.

Expected paths: the eleven identified Markdown files; `command-center/handoffs/claude-design/2026-07-26-ledger-usability-5b/context/packet-manifest.sha256`; active and closeout Runway OS sources; generated dashboard; and one sanitized 5F-W evidence log at closeout. No product or maintained-test path may change during this block.

Defaults: use terminal backslashes to preserve CommonMark hard-break semantics without trailing whitespace; remove only surplus terminal blank lines while retaining exactly one final newline; normalize each canonical/handoff pair identically; update only the two directly affected manifest entries; leave the response intake manifest's recorded returned-artifact hashes unchanged; reuse 5F-R's complete browser result only if product and browser-test hashes remain unchanged; use no real Git staging; keep Luxe Legacy setup parked.

Stop conditions: semantic-content drift beyond line-break encoding and terminal blank-line cleanup; canonical/copy mismatch; any returned ZIP or returned-artifact mutation; unexpected manifest change; product/test or preserved-file drift; protected/sensitive content; failed smoke, safety, syntax, JSON, dashboard, rendered, whitespace, sensitive-addition, cleanup, alternate-index, or provenance verification; real-index staging; or any need for publication, external access, broader repair, or an excluded action.

Verification: exact before/after path inventory and transformation proof; canonical/copy byte equality; recomputed packet-manifest verification; original ZIP and five returned-artifact SHA-256 checks; response intake recorded-hash preservation; full synthetic smoke; maintained Synthetic CI and Fly safety; Python and tracked-JavaScript syntax; JSON; dashboard refresh/currentness/health and rendered inspection; high-confidence sensitive-addition review; cleanup; disposable alternate-index full-candidate `git diff --cached --check`; zero real staging; exact changed paths; and preserved-file hashes.

Dashboard closeout: while active, show 5F-W as current with Task 4 and Codex as owner. On success, mark 5F-W done locally, keep Phase 5 active at 38%, keep 5F-R recorded as stopped, return Task 4 to Ryan, and make 5F-RR branch-publication retry the separately gated recommended next move.

Report point: return the exact normalized files and transformation counts, updated manifest entries, unchanged ZIP/returned-artifact and product/test proof, full local and alternate-index verification, zero-staging and preserved-file proof, and the separately gated 5F-RR decision.

Expansion candidates and questions: renewed branch publication is the nearest candidate but remains excluded because it introduces GitHub writes and hosted workflow execution. No clarification is required inside 5F-W.

Result: eleven reviewed Markdown files received only the approved deterministic transform: forty-one intentional two-space hard breaks became terminal backslashes and four surplus EOF blank lines were removed. The two canonical 5A artifacts remain byte-identical to their handoff copies; only two packet-manifest entries changed; all 27 packet entries verify; the original ZIP, five returned Claude artifacts, product/test sources, README, response-intake recorded hashes, and preserved files remain byte-identical. Full smoke, CI/Fly safety, syntax, JSON, dashboard, rendered, whitespace, sensitive-addition, cleanup, exact-transform, and disposable alternate-index checks passed with the real Git index empty. No external or excluded action occurred. Evidence: `command-center/logs/2026-07-27-evidence-whitespace-provenance-normalization-5f-w.md`.

Suggested next work block: 5F-RR to retry exact branch publication and hosted review after the clean 5F-W closeout; production remains the later 5F-R2 gate.

### Confirmed Work Block 5A: Cross-Surface Usability Baseline

Status: done locally on `codex/phase-5-usability-baseline`; unstaged, uncommitted, and unpublished.

Included: Task 1.1 (`P5-T11`) to freeze the representative workflow-review contract and journey matrix, plus Task 1.2 (`P5-T12`) to capture a sanitized desktop, mobile, exact-768, and installed-PWA usability baseline using only disposable synthetic local data.

Excluded: Tasks 1.3-1.4 (`P5-T13`-`P5-T14`), Tasks 2-4, Claude Design handoff or critique intake, application/test/dependency/authentication/financial/database/category/workflow/runtime/configuration changes, real financial data or databases, credentials, retained uploads, production/demo/Plaid/Fly/downstream access, external calls, staging, commit, push, PR, merge, workflow action, deployment, and all three preserved untracked files.

Review matrix: inspect representative Personal daily-work, planning/reporting, BFM operations, Luxe Legacy supported/unsupported-boundary, and installed-PWA continuity journeys. Use desktop 1200px for broad top-level coverage and phone 390px plus exact tablet 768px for the highest-value navigation, content, modal, form, table, error/recovery, and standalone paths. Evaluate navigation clarity, information hierarchy, labels, focus and keyboard behavior, touch targets, responsive overflow, empty/error states, cross-entity clarity, installed-PWA continuity, and the carried-forward planning demo-goal fidelity question. This is a qualitative usability and accessibility baseline, not accessibility certification or a repeat of Phase 4 correctness auditing.

Owner and recommended agent: Codex Desktop. The block couples controlled synthetic browser evidence, privacy-safe artifact creation, cross-surface judgment, exact cleanup, and Runway OS stewardship. No delegation or second opinion occurs in 5A.

Expected surfaces: `command-center/phase-5-workflow-review-contract.md`; sanitized synthetic screenshots under `command-center/artifacts/phase-5/5a/`; `command-center/phase-5-usability-baseline.md`; a sanitized 5A closeout log; Runway OS sources and generated dashboard; temporary synthetic runtime state that must be removed exactly. No product source or maintained test change is expected.

Defaults: use current maintained synthetic fixtures and installed-Chrome browser infrastructure; use existing tests as technical guardrails rather than reopening resolved Phase 4 correctness work; retain only sanitized synthetic evidence; record findings without implementing or accepting a redesign; use the current route/entity rules as the comparison contract; preserve all three unrelated untracked files exactly; and keep the result local, unstaged, uncommitted, and unpublished.

Stop conditions: protected or real data appears; credentials, authentication changes, external access, or a live action becomes necessary; a finding requires a product, financial, security, or design decision; scope leaves the representative matrix; evidence cannot be sanitized; synthetic setup or cleanup cannot be proven; maintained verification changes the plan; a product/test change appears necessary; the command center cannot refresh cleanly; or a preserved file would be touched.

Verification: baseline synthetic smoke; maintained configured-auth/no-password isolated-browser guardrails with denied non-localhost networking and exact temporary cleanup; complete review-matrix evidence coverage; direct visual inspection of retained synthetic artifacts; JSON; dashboard refresh/currentness/health and rendered active/closeout state; `git diff --check`; exact changed and staged paths; zero staged files; and preserved-file hashes.

Dashboard closeout: while active, show 5A as the current Phase 5 work block with Task 1.1 current. On success, mark Tasks 1.1-1.2 and 5A done, keep Phase 5 and Task 1 active, and make Task 1.3 the sole Ryan-owned planning gate for separately confirmed 5B.

Report point: return the exact journey matrix, sanitized artifacts, observed friction and strengths, planning demo-goal conclusion, technical guardrails, cleanup, changed paths, preserved boundaries, branch state, and the separate 5B decision.

Suggested next work block: 5B Independent Usability Critique And Findings Intake for Tasks 1.3-1.4, using a narrow Ryan-assisted Claude Design handoff followed by Codex adopt/ignore/park/Ryan-decision intake before any Task 2 polish.

Result: the J1-J5 contract and usability baseline are complete. Full synthetic smoke passed in 8.56 seconds, and the complete maintained configured-auth/no-password installed-Chrome suite passed all three entities, installed/standalone/offline behavior, responsive and interaction contracts, strict CSP, denied non-localhost networking, zero unexpected errors, and exact cleanup. A separate explicit-synthetic local session retained eleven visually inspected screenshots, produced zero browser console warnings/errors, and removed its managed `expense_5a_review_*` root. The packet records seven provisional friction clusters: stale demo categories, absent demo goals, undisclosed mobile-table overflow, weak Luxe Legacy empty/denied explanation, subscription-versus-recurring scope ambiguity, indirect Data Sources discovery, and the unexplained visible AI affordance. No product/test/configuration change, protected/live access, second opinion, staging, commit, push, PR, workflow, deployment, or preserved-file mutation occurred. Evidence: `command-center/phase-5-workflow-review-contract.md`, `command-center/phase-5-usability-baseline.md`, `command-center/artifacts/phase-5/5a/`, and `command-center/logs/2026-07-26-cross-surface-usability-baseline-5a.md`.

### Confirmed Work Block 5B: Independent Usability Critique And Findings Intake

Status: done locally on 2026-07-26; unstaged, uncommitted, and unpublished. The verified return is preserved unchanged, the complete critique is classified, and no Task 2 implementation is authorized.

Included: Task 1.3 (`P5-T13`) to obtain a narrow critique-only Claude Design second opinion from the exact sanitized 5A packet, plus Task 1.4 (`P5-T14`) to preserve and reconcile the returned opinion, classify every finding, surface Ryan decisions, and recommend the first bounded Task 2 work block without implementing it.

Excluded: Tasks 2-4 implementation, product/test/dependency/authentication/financial/database/category/workflow/runtime/configuration changes, real financial data or databases, credentials, retained uploads, production/demo/Plaid/Fly/downstream access, external or live actions other than opening Claude Design for the manual handoff, staging, commit, push, PR, merge, workflow action, deployment, and all three preserved untracked files.

Review focus: cross-surface explanation, discoverability, information hierarchy, and mobile density across all seven provisional 5A findings. The reviewer must also name strengths that later polish should preserve. The request is critique plus prioritized revised-direction advice only; lightweight annotations or mockups are allowed for at most three high-leverage recommendations, but code, implementation, unrestricted redesign, and work-block selection are prohibited.

Owner and recommended agents: Codex Desktop owns the repo-backed packet, sanitization, Downloads copy, Runway OS state, returned-response preservation, findings crosswalk, and final recommendation. Claude Design is the independent critique specialist. Ryan owns the required manual upload, prompt paste, and returned-folder save plus any material product-direction decision.

Runner and handoff path: write and verify the confirmed `second-opinion` block; create `command-center/handoffs/claude-design/2026-07-26-ledger-usability-5b/`; copy the exact final packet to `~/Downloads/claude-design-ledger-usability-5b-2026-07-26`; open `https://claude.ai/design`; stop for Ryan to drag/drop the packet and paste its prompt; expect `~/Downloads/claude-design-ledger-usability-5b-response-2026-07-26`; then preserve the response unchanged, inventory returned files, and perform Task 1.4 intake.

Expected surfaces: the repo and Downloads handoff folders; the existing 5A contract, baseline, eleven screenshots, and bounded read-only source references; Claude Design; the returned Downloads folder; a later sanitized 5B intake artifact; Runway OS sources and generated dashboard. No application source modification is expected.

Defaults: ask Claude for prioritized findings, explicit agreement or disagreement with each 5A finding, preservation constraints, and an `Implementation Notes For Codex` section; treat every reviewer statement as opinion until Codex classifies it as adopt, ignore, park, or Ryan-decision; preserve the 5A packet and returned response unchanged; keep the block local, unstaged, uncommitted, and unpublished.

Stop conditions: protected or real data, credentials, databases, retained uploads, or unsanitized evidence appears; the review target expands; Claude requests or returns implementation code, live action, or materially broader planning; Claude Design or the returned folder is unavailable; packet or response provenance cannot be verified; a recommendation requires a material Ryan product decision; sanitization, exact-path, dashboard, verification, or preserved-file checks fail.

Verification: exact manifest and hashes for the eleven input screenshots and both packet copies; protected-boundary and sanitization scans of every packet and response artifact; unchanged response preservation and complete returned-file inventory; crosswalk of all seven 5A findings, strengths, and every reviewer recommendation with no unclassified item; JSON; dashboard refresh/currentness/health and rendered-state inspection; `git diff --check`; zero staged files; exact changed paths; and unchanged preserved-file hashes.

Dashboard flow: show 5B as `second-opinion` with Task 1.3 current during packet preparation and Ryan's manual handoff. After a verified response returns, make Task 1.4 current for Codex intake. On success, mark 5B and Task 1 done and make Task 2.1 the sole Ryan-owned planning gate.

Report points: first return the verified repo and Downloads packet paths, review focus, prompt contract, and exact manual Ryan action. After the response returns, report the preserved artifacts, complete finding crosswalk, adopt/ignore/park/Ryan-decision classifications, prioritized friction, and recommended first Task 2 block.

Suggested next work block: a separately planned and confirmed 5C for the highest-value Task 2 polish slice selected only after 5B intake.

Result: the original returned ZIP and its five-file extracted response are preserved with exact SHA-256 hashes. The complete critique and all three synthetic annotations were inspected. All seven 5A findings, five additional reviewer findings, priorities, strengths, principles, questions, parked ideas, and implementation notes are classified in `command-center/phase-5-usability-findings-intake.md`. Source inspection confirmed that recurring detection has no kind model, mobile transaction rows retain an edit route, the demo taxonomy is hard-coded and stale, and Ask Opus sends detailed financial context to OpenRouter while retaining capped temporary chat history. Task 2 is decomposed into eight bounded units, and Task 2.1 is recommended for proposed 5C. No product/test/configuration change, protected/live access, staging, commit, push, PR, workflow, deployment, or preserved-file mutation occurred. Evidence: `command-center/handoffs/claude-design/2026-07-26-ledger-usability-5b/response/`, `command-center/phase-5-usability-findings-intake.md`, and `command-center/logs/2026-07-26-independent-usability-critique-findings-intake-5b.md`.

### Confirmed Work Block 5C: Demo Fidelity Repair

Status: done locally on 2026-07-26 for Task 2.1 only; unstaged, uncommitted, and unpublished.

Objective: remove the two synthetic-data defects that distort every usability review and make the existing Short-Term Planning goal experience reviewable, without changing product UI, production behavior, category definitions, or any live environment.

Included: Task 2.1 (`P5-T21`) only. Align the demo seed's Personal and BFM transaction/category/subcategory and budget vocabulary with the current entity-specific `categories.md` definitions; remove seeded legacy-category drift rather than suppressing the truthful runtime warning; add one representative synthetic Personal debt-payoff goal and one representative synthetic Personal savings goal using existing synthetic accounts; make reseeding deterministic and idempotent for the affected goal records; add focused maintained temporary-data coverage for category-domain alignment, both goal types, linked-account validity, rerun behavior, and entity isolation; update compact demo documentation only if the maintained contract needs it; and close Runway OS locally after verification.

Excluded: Tasks 2.2-2.8 and Tasks 3-4; templates, styles, JavaScript, route behavior, the production category domain, migrations, authentication, CSRF, CSP, PWA/service worker, recurring detection, Ask Opus, Luxe Legacy product design, mobile transaction design, dashboard banner design, real financial data or databases, retained uploads, credentials, production/demo/Plaid/Fly/downstream access, deploying or reseeding the live demo, staging, commit, push, PR, merge, workflow action, deployment, and all three preserved untracked files.

Owner and recommended agent: Codex Desktop. The work is a local repo-only synthetic-data and verification slice with no independent critique, protected access, delegation, or external action.

Expected files: `scripts/seed_demo_data.py`; focused maintained synthetic coverage, expected in `scripts/smoke_test.py` unless a smaller established test seam is clearly safer; `README.md` only if the durable demo contract is otherwise undocumented; a sanitized 5C evidence log; `command-center/now.md`, `command-center/roadmap.md`, `command-center/decisions.md`, `command-center/state.json`, and generated `command-center/index.html`. No product template, route, stylesheet, runtime configuration, workflow, migration, or category-domain file should change.

Defaults: treat `categories.md` as authoritative and do not change it; seed both goals only for the Personal synthetic demo; use existing synthetic accounts and plausible but clearly synthetic values; preserve deterministic transaction IDs and entity isolation; run every data check under a disposable `DATA_DIR`; preserve the truthful drift warning in product code; keep the result local, unstaged, uncommitted, and unpublished.

Stop conditions: category alignment requires changing `categories.md`, product categorization semantics, or a migration; goal seeding requires product behavior, production data, or a live/demo host; a seeded category or subcategory cannot map unambiguously without a product decision; rerun behavior cannot remain deterministic and isolated; a protected boundary or unrelated path appears; focused or full verification changes the plan; rendered dashboard or Short-Term Planning evidence still shows category drift or missing goals; command-center refresh or health fails; or any preserved untracked file changes.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused disposable-data seed assertions across Personal, BFM, and untouched Luxe Legacy; exact category/subcategory membership against `categories.md`; exactly one active Personal debt-payoff and one active Personal savings goal with valid linked synthetic accounts after repeated seeding; no cross-entity goal leakage; localhost rendered inspection of the Personal dashboard and Short-Term Planning at representative desktop width using disposable synthetic data; zero browser console warnings/errors; exact temporary cleanup; JSON; dashboard refresh/currentness/health and rendered Runway OS inspection; `git diff --check`; exact changed and staged paths; zero staged files; and unchanged preserved-file hashes.

Completion report: return the exact seed changes, category and goal assertions, before/after rendered conclusion, smoke and focused results, cleanup, changed paths, preserved exclusions, branch/worktree state, and the separate next Task 2 decision. Do not begin Task 2.2 or another sequel.

Result: `scripts/seed_demo_data.py` now loads the exact Personal/BFM category and subcategory domains from `categories.md`, uses only valid merchant and budget categories, produces deterministic same-day reseeds, adds one linked Personal debt-payoff goal and one linked savings goal, gives BFM no goals, and continues not to touch Luxe Legacy. `scripts/smoke_test.py` proves exact category/subcategory equality, valid transaction/budget membership, goal types and links, identical repeated output, no cross-entity leakage, and byte-for-byte Luxe Legacy preservation. Baseline and final full smoke passed. Disposable rendered inspection showed no orphan-category warning on the Personal Dashboard and both goals on Short-Term Planning with zero console warnings/errors. The exact managed root is absent after recoverable cleanup to Trash. No product UI, category-domain, migration, live/demo, protected, GitHub, deployment, sequel, or preserved-file action occurred. Evidence: `command-center/logs/2026-07-26-demo-fidelity-repair-5c.md`.

Suggested next work block: Luxe Legacy setup and the Task 2.2 / 5D path are parked until Ryan explicitly reopens them. When Ryan is ready, separately plan and confirm a bounded Task 2.3 phone transaction density and entity-context block; no Task 2.3 implementation is authorized by this roadmap update.

### Confirmed Work Block 5E: Phone Transaction Clarity And Entity Context

Status: done locally on 2026-07-26 for Task 2.3 only; unstaged, uncommitted, and unpublished. The 5D label remains parked with Task 2.2.

Included: Task 2.3 (`P5-T23`) only. Replace the phone-only 560px horizontally scrolling transaction presentation with compact rows that keep the current date, description, amount, category, and subcategory fields readable; preserve the existing row-to-edit-modal affordance, sorting, copy, pagination, badges, empty state, filters, and repeated HTMX swaps; keep the table at exact-768 and desktop widths; add a concise read-only current-entity marker to the shared mobile header using existing Personal, BFM, and LL labels; add focused maintained synthetic browser coverage; retain sanitized rendered evidence; and close Runway OS locally after verification.

Excluded: Task 2.2 (`P5-T22`) and 5D; Tasks 2.4-2.8 and Tasks 3-4; new financial fields, inline transaction editing, financial/query/route/database/category behavior, transaction identity or mutation semantics, new sorting/filtering semantics, drawer markup, entity switching, authentication, CSRF, CSP, PWA/service worker, Ask Opus, recurring detection, dashboard redesign, Luxe Legacy setup, real financial data or databases, retained uploads, credentials, production/demo/Plaid/Fly/downstream access, staging, commit, push, PR, merge, workflow action, deployment, and all preserved untracked files.

Why this grouping: the completed 5B review explicitly bundled phone transaction hierarchy and mobile entity context because both are responsive-shell changes with one synthetic browser and visual-verification path. The source-backed intake confirms that the current edit modal is the required row affordance. Task 2.6 remains separate because it concerns dashboard information design; Tasks 2.4-2.5 require product/data-handling decisions; Task 2.2 remains paused.

Owner and recommended agent: Codex Desktop. The block needs coordinated Jinja/CSS changes, browser regression coverage, direct rendered judgment, and Runway OS stewardship. No additional second opinion or delegation is included because Claude Design already critiqued this exact slice.

Expected files: `web/templates/base.html`, `web/templates/components/txn_results.html`, `web/templates/components/txn_row.html`, `web/static/style.css`, focused coverage in `scripts/mobile_drawer_browser_test.py`, sanitized synthetic evidence under `command-center/artifacts/phase-5/5e/`, a sanitized 5E closeout log, Runway OS sources, and generated dashboard. No JavaScript, route, database, financial-logic, README, category-domain, workflow, dependency, or runtime configuration change is expected.

Defaults: activate compact rows only at the existing phone breakpoint up to 480px; show the read-only entity marker wherever the shared mobile header appears; use existing Personal, BFM, and LL display labels; preserve the logo, hamburger, drawer, all five current transaction fields, current server-rendered text, sort access, copy, pagination, badges, empty state, filters, repeated HTMX behavior, and edit modal; keep one semantic transaction row rather than duplicating financial content; keep the result local, unstaged, uncommitted, and unpublished.

Stop conditions: implementation requires new financial fields, queries, routes, migrations, sorting/filtering semantics, inline editing, drawer markup, entity switching, authentication, PWA behavior, a wider-than-phone row change, protected or live access, an unexpected path, or a material product decision; accessibility, HTMX, edit, filter, sort, exact-768, desktop, drawer, entity-isolation, console, cleanup, dashboard, scope, or preserved-file verification fails in a plan-changing way.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused disposable Personal, BFM, and LL 390px assertions for no transaction horizontal movement, five readable fields, correct read-only marker, preserved sort, copy, pagination, repeated HTMX swaps, row-to-edit-modal behavior, document non-overflow, and zero console errors; exact-768 and desktop table preservation; complete maintained configured-auth/no-password `scripts/mobile_drawer_browser_test.py` with denied non-localhost networking and exact cleanup; direct inspection of sanitized rendered evidence; relevant Python syntax; JSON; dashboard refresh/currentness/health and rendered state; `git diff --check`; exact changed paths; zero staging; and unchanged preserved files.

Completion report: return exact templates/styles/coverage changes, before-and-after phone measurements and visual conclusion, entity-marker behavior, preserved edit/filter/sort/table/drawer results, smoke and browser results, console and cleanup state, evidence paths, exact changes and exclusions, and branch/worktree durability. Do not begin Task 2.6 or reopen Task 2.2.

Suggested next work block: after verified 5E closeout, separately plan Task 2.6 (`P5-T26`) dashboard explanation and density unless Ryan first chooses to resolve one of the Task 2.4 or Task 2.5 decisions. Task 2.2 and 5D remain parked.

Result: `base.html` now exposes the active Personal, BFM, or LL value in the shared mobile header with an explicit screen-reader-only `Current entity:` prefix. The existing transaction table remains one semantic server-rendered structure; at the phone breakpoint, template classes and bounded CSS render each row as a compact two-line grid with all five fields while retaining all five sort controls, copy, pagination, badges, empty state, filters, repeated HTMX swaps, and the row-to-edit-modal path. Personal, BFM, and LL each measure a 390px document with a 368px wrapper client and scroll width and five visible fields; exact-768 and desktop remain `table` / `table-row`. Baseline and final full smoke, relevant compilation, the complete maintained configured-auth/no-password browser suite, direct inspection of four sanitized screenshots, JSON, dashboard, whitespace, exact-scope, zero-staging, cleanup, and preserved-file checks pass. No excluded financial, route, query, database, category, drawer, entity-switching, authentication, PWA, live, GitHub, deployment, sequel, or preserved-file action occurred. Evidence: `command-center/logs/2026-07-26-phone-transaction-clarity-5e.md` and `command-center/artifacts/phase-5/5e/`.

### Confirmed Work Block 5F: Dashboard Category Signal And Density

Status: done locally on 2026-07-26 for Task 2.6 only; verified, unstaged, uncommitted, and unpublished. Ryan confirmed the exact recommended block after a disposable clean-demo measurement found that 15 of 32 rendered Personal categories and 12 of 29 BFM categories had zero current activity; 15 Personal and 10 BFM categories also had no configured budget.

Included: Task 2.6 (`P5-T26`) only. Keep categories with spending or a configured budget visible; collapse only zero-spend, no-budget categories behind a clearly labeled keyboard-accessible exact-count disclosure for the selected period; add visible textual budget context using existing computed amounts and percentages; replace internal-facing orphan-category wording with concise user-facing language while preserving the truthful count, reassignment link, and once-per-session behavior; preserve current totals, calculations, thresholds, data inclusion, category definitions, drill-downs, subcategory modal, Details/Compare views, repeated HTMX swaps, responsiveness, and entity isolation; add focused maintained synthetic coverage; inspect sanitized Personal/BFM evidence; verify supported Luxe Legacy behavior for regression only; and close Runway OS locally.

Excluded: Task 2.2 (`P5-T22`) and 5D; Tasks 2.4-2.5 and 2.7-2.8; Tasks 3-4; Luxe Legacy setup, onboarding, or first-use direction; application-wide color or chart redesign; new financial calculations, reporting/category inclusion semantics, category definitions, query results, migrations, database behavior, authentication, CSRF, CSP, PWA/service worker, Ask Opus, recurring detection, connection discovery, offline copy, real financial data or databases, retained uploads, credentials, production/demo/Plaid/Fly/downstream access, staging, commit, push, PR, merge, workflow action, deployment, and all preserved untracked files.

Why this grouping: category density, category-drift explanation, and color-independent budget meaning share one dashboard category presentation, controller, styling, focused browser, and rendered-verification path. The completed Claude Design critique already covers the direction, and the post-5C synthetic measurement resolves the conditional density question. The nearest excluded tasks require different product decisions, subsystems, or risk classes.

Owner and recommended agent: Codex Desktop. The block needs integrated route/template/controller work, accessibility judgment, direct rendered inspection, maintained synthetic browser coverage, exact cleanup, and Runway OS stewardship. No delegation or additional second opinion is included.

Expected files: `web/routes/dashboard.py`, `web/templates/components/dashboard_detail_cats.html`, `web/static/dashboard-fragments.js`, `web/static/style.css`, possibly `web/__init__.py` for orphan-warning wording, focused coverage in `scripts/smoke_test.py` and `scripts/mobile_drawer_browser_test.py`, sanitized evidence under `command-center/artifacts/phase-5/5f/`, a sanitized 5F closeout log, Runway OS sources, and generated dashboard.

Defaults: inactive means both zero spending and no configured budget in the selected period; zero-spend budgeted categories remain visible; the exact-count disclosure applies to the current fragment and naturally resets when the selected period rerenders; textual context reuses existing computed values and thresholds; no hidden category becomes unavailable; Personal/BFM receive focused visual review; Luxe Legacy receives regression verification only; preserve every existing financial, category, interaction, security, responsive, and entity boundary; keep the result local, unstaged, uncommitted, and unpublished.

Stop conditions: the implementation needs new financial or category semantics, changes report/query totals or inclusion, makes inactive data undiscoverable, breaks keyboard access, drill-down, subcategory, Details/Compare, HTMX, responsive, authentication, CSP, PWA, or entity behavior, widens into a full chart redesign or another Task 2 slice, touches Luxe Legacy setup, requires protected/live access, overlaps an unexpected path, or produces a plan-changing verification, rendered, cleanup, dashboard, scope, or preserved-file failure.

Verification: baseline and final `.venv/bin/python scripts/smoke_test.py`; focused disposable Personal/BFM assertions for visible and inactive classification, exact disclosure count and state, keyboard and pointer toggling, visible budget text, truthful orphan warning and reassignment link, drill-down and subcategory behavior, repeated HTMX swaps, no hidden-data loss, and unchanged totals; complete maintained configured-auth/no-password `scripts/mobile_drawer_browser_test.py`; Personal/BFM at 390px, exact 768px, and desktop plus Luxe Legacy regression; sanitized rendered evidence and direct inspection; denied non-localhost networking; zero unexpected console/page errors; exact temporary cleanup; relevant syntax; JSON; dashboard refresh/currentness/health and rendered state; `git diff --check`; exact changed paths; zero staging; and unchanged preserved files.

Completion report: return exact visible/collapsed before-and-after counts, wording and budget-context changes, accessibility and responsive conclusions, preserved totals/drill/HTMX/entity behavior, smoke and browser results, console and cleanup state, evidence paths, exact changes and exclusions, branch/worktree durability, and the separate next gate without beginning a sequel.

Result: Personal now keeps 17 spending-or-budgeted category rows primary and starts 15 zero-spend/no-budget rows behind an exact-count disclosure, reducing the measured category fragment from 1,018.46px to 668.63px. BFM keeps 19 rows primary and starts 10 inactive rows collapsed while its two zero-spend budgeted categories remain visible with explicit `0% of` budget text. Every primary row now exposes percentage-and-budget or `No budget` text; the existing totals, percentages, thresholds, inclusion, category definitions, drill, subcategory, Details/Compare, HTMX, authentication, CSP, PWA, responsive, and entity behavior remain unchanged. The orphan notice now uses user-facing category-list wording and a `Review and reassign` link while preserving count and once-per-session behavior. Baseline and final full smoke, complete maintained both-auth browser coverage including Enter/Space, direct disposable Personal/BFM visual inspection, Luxe Legacy regression-only rendering, syntax, JSON, dashboard, whitespace, cleanup, zero-staging, exact-scope, and preserved-file checks passed. Evidence: `command-center/logs/2026-07-26-dashboard-category-signal-density-5f.md`.

Suggested next work block: after verified 5F closeout, separately decide whether to run a 5F-R durability/publication block for the accumulated verified Phase 5 product changes. Task 2.2 and 5D remain parked; Tasks 2.4-2.5 remain decision-gated; Tasks 2.7-2.8 remain separate.

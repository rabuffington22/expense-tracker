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

Status: active; Tasks 1-3 and 4A-4B plus work blocks 3A-3D are done, and Task 4C is current awaiting a separately confirmed weekly/waterfall audit block

Goal: determine what “working properly” means across the live product, then rank evidence-backed defects and gaps.

- **Task 1: Audit the transaction foundation and three-entity isolation with synthetic data.** Status: done through work block 3A. The audit passed initialization, isolation, debit-sign, edit, split, and effective-reporting probes; it found a high-severity identity collision risk and a medium tracked-regression-coverage gap without implementing fixes.
- **Task 2: Audit statement and vendor-order import, matching, and categorization workflows.** Status: done through work block 3B. The audit passed 60 synthetic checks and found three high-risk correctness defects in vendor-payment schema compatibility, vendor line-item persistence, and category-domain enforcement, plus a medium coverage gap and low `Undo` ambiguity.
- **Task 3: Audit dashboard, reporting, exports, subscriptions, and cash-flow behavior.** Status: done through work block 3C. The tracked smoke suite passed; 297 of 306 ephemeral assertions passed, and the remaining nine controlled errors reproduced one medium Recurring Charges report SQL defect at three layers in all three entities. A medium tracked-coverage gap was also recorded without implementation.
- **Task 4A: Audit long-term planning projections and cross-entity visibility.** Status: done through work block 3D. Positive projections, linked balances, CRUD, summaries, and Personal/BFM visibility passed; negative depreciation and LL direct-route denial defects were recorded without repair.
- **Task 4B: Audit short-term goals, snapshots, budgets, actions, and payoff planning.** Status: done through work block 3D. CRUD, entity-local choices, budgets, effective splits, averages, per-payroll math, actions, and direct payoff engines passed; APR-blind locked plans, snapshot-note loss, LL direct-route denial, and tracked-coverage gaps were recorded without repair.
- **Task 4C: Audit weekly and waterfall derived workflows.** Status: current; awaiting a separately confirmed work block 3E. Reuse validated synthetic planning, budget, transaction, balance, paydown-goal, and payroll-schedule inputs to reconcile weekly pace/bills and BFM-to-Personal waterfall calculations, dates, empty states, and entity boundaries.
- **Task 4D: Audit payroll roster, Phoenix/CyberPayroll import, and role spending.** Status: planned after Task 4C. Use generated synthetic XLSX/payroll records to check employee CRUD and pay history, parse-preview-save and duplicate behavior, role mapping and aggregation, temporary-payload cleanup, and intended entity/access boundaries without real payroll or HR data.
- **Task 5: Audit Plaid and downstream-sync integration boundaries.** Status: planned. Begin with source and synthetic/mocked behavior; any production account access, Plaid action, workflow action, credential use, or downstream write requires a separate target-specific authorization.
- **Task 6: Audit PWA, responsive navigation, public dashboard, and authentication boundaries.** Status: planned. Use tracked source and synthetic/local behavior first; do not change authentication, CSRF, credential, encryption, or public-route behavior during the audit.
- **Task 7: Consolidate audit findings into severity-ranked issues.** Status: planned. Record sanitized reproduction steps, observed versus expected behavior, impact, confidence, acceptance checks, and the affected entity or boundary.
- **Task 8: Confirm the repair order and bounded Phase 4 implementation work blocks with Ryan.** Status: planned. Prioritize only evidence-backed findings after the relevant audit slices are complete.

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

## Phase 4: Core Repairs And Regression Coverage

Status: planned

Goal: implement the highest-value fixes while strengthening repeatable verification.

- **Task 1: Repair confirmed reliability and correctness defects in prioritized work blocks.**
- **Task 2: Expand regression tests around repaired workflows and entity isolation.**
- **Task 3: Add CI checks that are safe for a private financial application and use only synthetic data.**
- **Task 4: Deploy only after a verified, explicitly approved release block.**

## Phase 5: UX Polish, Operations, And Durable Handoff

Status: planned

Goal: make the product understandable, maintainable, and easy to re-enter after the critical repairs are complete.

- **Task 1: Review desktop, mobile, and installed-PWA workflows for usability and accessibility.**
- **Task 2: Polish high-friction journeys without widening financial or authentication risk.**
- **Task 3: Finalize operator runbooks, current documentation, monitoring decisions, and release evidence.**
- **Task 4: Close the roadmap with target-repo commit/push durability and a compact parent-project pointer.**

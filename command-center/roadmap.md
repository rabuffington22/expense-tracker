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

Status: paused after Tasks 1-6 and work blocks 3A-3J while Ryan decides the verified 4A release path; Task 7 resumes after release or explicit deferral

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
- **Task 7: Consolidate audit findings into severity-ranked issues.** Status: paused during the 4A release decision; then return to just-in-time planning after release or explicit deferral. Record sanitized reproduction steps, observed versus expected behavior, impact, confidence, acceptance checks, and the affected entity or boundary.
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

## Phase 4: Core Repairs And Regression Coverage

Status: active for confirmed work block 4B release

Goal: implement the highest-value fixes while strengthening repeatable verification.

- **Task 1A: Repair the confirmed server-authentication and protected-cache boundaries.** Status: complete and verified locally through work block 4A; release authorized through work block 4B.
- **Task 1B: Repair remaining confirmed reliability and correctness defects in prioritized work blocks.** Status: planned after Phase 3 Tasks 7-8 establish the broader order.
- **Task 2: Expand regression tests around repaired workflows and entity isolation.**
- **Task 3: Add CI checks that are safe for a private financial application and use only synthetic data.**
- **Task 4: Deploy only after a verified, explicitly approved release block.** Status: current through confirmed work block 4B.

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

Status: active; confirmed by Ryan on 2026-07-18

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

## Phase 5: UX Polish, Operations, And Durable Handoff

Status: planned

Goal: make the product understandable, maintainable, and easy to re-enter after the critical repairs are complete.

- **Task 1: Review desktop, mobile, and installed-PWA workflows for usability and accessibility.**
- **Task 2: Polish high-friction journeys without widening financial or authentication risk.**
- **Task 3: Finalize operator runbooks, current documentation, monitoring decisions, and release evidence.**
- **Task 4: Close the roadmap with target-repo commit/push durability and a compact parent-project pointer.**

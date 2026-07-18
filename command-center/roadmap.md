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

Status: active

Goal: restore and prove the automated financial-data pipeline before broader feature work.

- **Task 1: Re-enable the disabled Daily Plaid Sync workflow with Ryan authorization.** Treat this as an external GitHub mutation and preserve the exact before/after state. Status: done; workflow is active.
- **Task 2: Verify one controlled sync execution.** Confirm authentication, all-entity results, downstream Luxe Legacy isolation, and failure reporting without exposing financial row data. Status: done; controlled run `29627530457` completed successfully.
- **Task 3: Establish production and demo health baselines.** Capture safe HTTP health, latest deploy status, workflow state, and restartable checks in Runway OS. Status: done; both roots returned HTTP 200 and both workflows are active.
- **Task 4: Define recurring operational checks.** Decide what belongs in manual re-entry, dashboard status, GitHub Actions, or a later monitored automation. Status: done; work block 1B recommended an independent alert-only Codex monitor.
- **Task 5: Add an independent read-only Daily Plaid Sync monitor.** Create a project-local recurring Codex automation that checks public workflow state and scheduled-run freshness, alerts Ryan on failure, and never enables or dispatches the workflow. Status: done; automation `expense-tracker-daily-plaid-sync-monitor` is active and its read-only test passed.
- **Task 6: Move the daily trigger away from the start of the hour.** Change the schedule from minute zero through a separate source-and-release block because GitHub documents higher delay/drop risk at the start of an hour. Status: current; awaiting a separate work block 1D proposal and confirmation.

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

## Phase 2: Project Truth And Documentation Recovery

Status: planned

Goal: remove contradictory project guidance while retaining useful domain history.

- **Task 1: Rebuild the root README for the current Flask, HTMX, Fly.io, Plaid, and three-entity architecture.**
- **Task 2: Decide the future of `PROJECT_KNOWLEDGE.md` and `plan.md`.** Archive, replace, or clearly mark their historical status after useful content is migrated.
- **Task 3: Reconcile `CLAUDE.md` and the untracked `AGENTS.md`.** Define one maintained instruction source and explicitly decide whether `AGENTS.md` becomes tracked.
- **Task 4: Document deployment, data, and side-effect boundaries without credentials or financial detail.**

## Phase 3: Functional Audit And Prioritization

Status: planned

Goal: determine what “working properly” means across the live product, then rank evidence-backed defects and gaps.

- **Task 1: Audit core workflows for Personal, BFM, and Luxe Legacy with safe data-handling rules.**
- **Task 2: Audit Plaid, vendor import/matching, categorization, reporting, planning, payroll, weekly, waterfall, PWA, and public dashboard behavior.**
- **Task 3: Convert findings into severity-ranked issues with reproduction and acceptance checks.**
- **Task 4: Confirm the repair order and bounded implementation work blocks with Ryan.**

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

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

- **Task 1: Re-enable the disabled Daily Plaid Sync workflow with Ryan authorization.** Treat this as an external GitHub mutation and preserve the exact before/after state.
- **Task 2: Verify one controlled sync execution.** Confirm authentication, all-entity results, downstream Luxe Legacy isolation, and failure reporting without exposing financial row data.
- **Task 3: Establish production and demo health baselines.** Capture safe HTTP health, latest deploy status, workflow state, and restartable checks in Runway OS.
- **Task 4: Define recurring operational checks.** Decide what belongs in manual re-entry, dashboard status, GitHub Actions, or a later monitored automation.

### Proposed Work Block 1A: Restore Daily Sync And Operational Baseline

Status: active

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

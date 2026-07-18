# Decision Log

## Accepted

### 2026-07-17 — Install the full Runway OS in Expense Tracker

Ryan rejected a thin overlay and confirmed a full in-repo Runway OS install. The target repo will own its roadmap, current state, decisions, operating rules, dashboard, logs, handoffs, and verification history in `command-center/`.

### 2026-07-17 — Keep the financial-data protection profile without reducing the OS

The scaffold records the `sensitive-retrofit` profile because the project handles financial, payroll, credentialed, and production operations. This affects default worker automation and reporting boundaries only. It does not remove any core Runway OS planning, dashboard, state, handoff, or verification surface.

### 2026-07-17 — Preserve existing project files during bootstrap

The installer is staged separately and only new Runway OS surfaces are transplanted. Existing `README.md`, `.gitignore`, application directories, documentation, ignored data, and the two pre-existing untracked files are not overwritten or staged by default.

### 2026-07-17 — Use the existing repo shape

Expense Tracker's product source remains in `web/`, `core/`, `scripts/`, and root entry/configuration files. Scratch-only `app/` and `scratch/` directories will not be added merely to satisfy a generic scaffold check.

### 2026-07-17 — Make Runway OS canonical for project control

Legacy documentation remains supporting domain material or migration input. It does not compete with `command-center/roadmap.md`, `now.md`, `decisions.md`, `operating-rules.md`, and `state.json` for current project direction.

### 2026-07-17 — Keep bootstrap read-only toward application and production behavior

Work block 0A installs and verifies the operating system only. It does not re-enable GitHub workflows, trigger Plaid, deploy Fly apps, access ignored financial data, modify application code, or rewrite legacy documentation.

### 2026-07-17 — Accept Phases 1-5 as the baseline roadmap

Ryan confirmed the proposed operational reliability, documentation recovery, functional audit, repair/testing, and UX/operations phases. Each phase still requires just-in-time work-block confirmation before execution.

### 2026-07-17 — Make the Runway OS branch durable before live recovery

Ryan authorized staging only `PROJECT_STRUCTURE.md` and `command-center/`, committing the verified full install, and pushing `codex/runway-os-full-install` to the existing GitHub remote. Pre-existing untracked files remain excluded.

### 2026-07-17 — Confirm work block 1A and its live effects

Ryan authorized enabling Daily Plaid Sync and dispatching one controlled workflow run after target durability. The run may insert newly available transactions into the configured production entities and invoke the existing Luxe Legacy bridge for qualifying data. Source-code, secret, Fly, database-transfer, authentication, PR, merge, and parent-repo changes remain excluded.

### 2026-07-17 — Accept work block 1A as successfully verified

The workflow changed from `disabled_inactivity` to `active`. Controlled run `29627530457` completed successfully with every job step passing, the workflow remained active, and production/demo roots returned HTTP 200. Only job/step status was inspected; no response-body, financial-row, or credential output was opened.

### 2026-07-18 — Confirm work block 1B as a read-only safeguard-definition block

Ryan authorized sanitized GitHub platform research, option comparison, a recommendation, and an implementation-ready follow-up. The block did not authorize a monitor, automation, workflow mutation, sync, credential or financial-data access, deploy, commit, push, PR, or merge.

### 2026-07-18 — Record Runway OS as merged and pushed on main

Before 1B research began, repository state showed `codex/runway-os-full-install` had already been fast-forward merged and `main` plus `origin/main` pointed to `0b9d60d`. The command center now treats `main` as the durable current branch rather than describing the earlier branch push or merge as pending.

### 2026-07-18 — Publish the 1B closeout directly to main

Ryan authorized committing and pushing the completed work block 1B command-center changes directly to `main`. The pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh` remain excluded.

### 2026-07-18 — Confirm work block 1C for an independent read-only monitor

Ryan authorized one project-local recurring Codex automation that checks unauthenticated public GitHub workflow metadata daily at 7:00 AM America/Chicago. It may alert on a non-active workflow, no scheduled run within 36 hours, an unsuccessful latest scheduled run, or a scheduled run that remains incomplete beyond the delay window. Manual dispatches do not satisfy freshness. The automation must never enable, dispatch, rerun, or edit the workflow and must not access credentials, financial data, Plaid, Fly, databases, application state, or paid external services.

### 2026-07-18 — Publish the 1C closeout directly to main

Ryan authorized committing and pushing the completed work block 1C command-center changes directly to `main`. Publication remains limited to the 1C Runway OS sources, generated dashboard, and closeout log. Pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh` remain excluded.

### 2026-07-18 — Confirm work block 1D for minute-zero cron hardening

Ryan authorized changing Daily Plaid Sync from `0 9 * * *` to `17 9 * * *` on `codex/daily-sync-cron-hardening`, publishing a ready PR, merging it to `main`, and observing the single production Fly deploy triggered by that merge. The block preserves `workflow_dispatch`, does not manually dispatch or rerun the sync, and excludes application, Fly configuration, secret, credential, financial-data, database, authentication, monitor, parent-repo, and pre-existing untracked-file changes. After verified deployment, Codex may push the command-center-only closeout directly to `main` with `[skip actions]` to prevent a second deploy.

### 2026-07-18 — Accept work block 1D and Phase 1 as verified complete

Ready PR `#83` merged the minute-17 schedule as `96af7dc`. Fly Deploy run `29645346441` and every job step passed, default-branch source contains `17 9 * * *`, Daily Plaid Sync remains active, and production plus demo returned HTTP 200. The first natural scheduled execution is left to the existing independent monitor rather than a manual dispatch. Phase 1 is complete, and Phase 2 becomes active for just-in-time work-block planning without authorizing documentation edits.

### 2026-07-18 — Confirm work block 2A for the root project entry point

Ryan authorized rebuilding `README.md` for the current Flask, HTMX, Fly.io, Plaid, and three-entity architecture and documenting sanitized deployment, data, and side-effect boundaries. Codex may work on `codex/phase-2-root-docs`, update the supporting project-structure and Runway OS surfaces, commit and push the verified branch, and open a draft PR. The block excludes application code, workflows, databases, production/Plaid/Fly/credential/financial-data access, legacy-document edits or archival, `CLAUDE.md`, pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh`, merge, and deployment.

### 2026-07-18 — Accept work block 2A as verified on draft PR #84

The root README now reflects the tracked Flask, HTMX, Plaid, Fly.io, and three-entity implementation and records sanitized deployment, data, and side-effect boundaries. The synthetic smoke suite, documentation truth checks, exact-scope checks, dashboard refresh, and Runway OS health check passed. Source commit `c249c9b` is pushed on `codex/phase-2-root-docs`, and draft PR #84 is open without merge or deployment. Tasks 2 and 3 remain separate governance work requiring a new confirmation.

### 2026-07-18 — Authorize work block 2A-R to publish PR #84 to main

Ryan explicitly instructed Codex to commit and push the verified work to `main`. This authorizes marking PR #84 ready, merging it without force, observing the one production Fly deploy automatically triggered by the `main` update, and checking sanitized workflow status plus production root/health HTTP status. It also authorizes a command-center-only closeout commit pushed directly to `main` with `[skip actions]` to prevent a second deployment. Tasks 2 and 3, content expansion, manual workflow actions, Fly mutations, credentials, financial data, databases, application/authentication changes, and pre-existing untracked files remain excluded.

## Pending Ryan Direction

- Review draft PR #84 and decide whether it should later be merged.
- Confirm or revise a future Phase 2 governance block deciding whether `AGENTS.md` becomes tracked and which legacy documentation is archived, replaced, or labeled historical.

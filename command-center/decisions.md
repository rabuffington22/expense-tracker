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

### 2026-07-18 — Accept work block 2A-R as successfully released

PR #84 was marked ready and merged to `main` as `6270304`. Automatic Fly Deploy run `29646390675` and every job step passed, and production `/health` plus the root returned HTTP 200. GitHub emitted a non-blocking annotation that `actions/checkout@v4` targets deprecated Node 20 and is currently forced to Node 24; it did not affect the release. No logs, response bodies, credentials, financial data, manual workflow action, or recovery mutation occurred. The sanitized closeout is published to `main` with `[skip actions]` so it does not deploy again.

### 2026-07-18 — Confirm work block 2B for legacy and agent-instruction governance

Ryan authorized replacing `PROJECT_KNOWLEDGE.md` and `plan.md` with concise in-place historical notices, making a concise tracked `AGENTS.md` the canonical agent instruction source, and reducing `CLAUDE.md` to a compatibility entry point. The block may update supporting README, project-structure, and Runway OS surfaces when needed, work on `codex/phase-2-document-governance`, commit and push the verified branch, and open a draft PR. It excludes application code, workflows, authentication, databases, Plaid, Fly configuration, credentials, financial data, production operations, untracked `scripts/sync_prod_to_local.sh`, parent-repo changes, merge, and deployment.

### 2026-07-18 — Accept work block 2B as verified on draft PR #85

The repository now has one concise tracked canonical instruction source in `AGENTS.md`; `CLAUDE.md` is a compatibility entry point; and `PROJECT_KNOWLEDGE.md` plus `plan.md` are historical notices with Git recovery commands rather than competing guidance. The legacy Short-Term Planning plan's missing dedicated smoke and seeded goal/snapshot coverage is parked for Phase 3 rather than hidden. All documentation, synthetic, exact-scope, dashboard, and health checks passed. Commit `912c9bb` is pushed on `codex/phase-2-document-governance`, and draft PR #85 is open without merge or deployment.

### 2026-07-18 — Authorize work block 2B-R to publish PR #85 to main

Ryan explicitly instructed Codex to commit and push the verified documentation-governance work to `main`. This authorizes recording 2B-R on the feature branch, marking draft PR #85 ready, merging it without force, observing the single automatic Fly Deploy triggered by the merge, and checking sanitized workflow status plus production root and `/health` HTTP status. It also authorizes a command-center-only closeout pushed directly to `main` with `[skip actions]` to prevent a second deployment. Content changes beyond the verified PR, application and workflow edits, manual workflow actions, Fly mutations, credentials, financial data, databases, Plaid, authentication, parent-repo changes, and pre-existing untracked files remain excluded.

### 2026-07-18 — Accept work block 2B-R and Phase 2 as verified complete

Ready PR #85 merged the verified canonical-guidance and legacy-document governance work to `main` as `216a992`. Automatic Fly Deploy run `29647452643` and every job step passed, and production root plus `/health` returned HTTP 200. Only sanitized workflow, job, step, and HTTP status was inspected. Phase 2 is complete, and Phase 3 becomes active for just-in-time audit decomposition without authorizing functional-audit execution.

### 2026-07-18 — Confirm work block 3A for the synthetic transaction foundation audit

Ryan confirmed Task 1 as a synthetic-only audit of the transaction foundation and Personal, BFM, and Luxe Legacy isolation. Codex may inspect tracked source, run the existing smoke suite, execute ephemeral probes against temporary databases, create a sanitized audit log, record ranked findings, and close Runway OS state. Tasks 2-8, product fixes, tracked test expansion, real databases, uploads, credentials, row-level financial data, production/demo access, Plaid or workflow actions, authentication/security changes, pre-existing `scripts/sync_prod_to_local.sh`, and all commit, push, PR, merge, and deployment actions remain excluded.

### 2026-07-18 — Accept work block 3A as verified with one correctness defect and one coverage gap

The existing smoke suite passed, and ephemeral temporary-database probes passed all-entity initialization, schema alignment, isolation, signed-cents, edit, split-validation, rejected-update preservation, and effective-reporting checks. A high financial-data completeness defect was reproduced: identity hashes only date, amount, and description, so distinct transactions with different accounts can collide and one is silently skipped. The same helper is used by Plaid source, but Plaid impact remains unverified under Task 5. Edit, split, and effective-reporting behavior passed but lacks tracked regression coverage. Both findings are recorded without repair or test expansion, Task 1 is done, and Task 2 becomes current for a separately confirmed audit block.

### 2026-07-18 — Authorize direct-main durability for the 3A audit closeout

Ryan explicitly instructed Codex to commit and push the verified 3A command-center closeout to `main`. This authorizes staging only the seven 3A command-center paths, committing with the established `[skip actions]` convention, and pushing `main` without force. Product and tracked test files, pre-existing untracked `scripts/sync_prod_to_local.sh`, application/workflow changes, production deployment, live access, protected data, credentials, Plaid, Fly, and all recovery outside the exact closeout remain excluded.

## Pending Ryan Direction

### 2026-07-18 — Confirm work block 3B for the synthetic import-to-categorization audit

Ryan confirmed Task 2 as one synthetic-only vertical audit from statement and vendor-order ingestion through matching, aliases, suggestions, and category/subcategory handling across Personal, BFM, and Luxe Legacy. Codex may inspect tracked source, generate ephemeral CSV/PDF/XLSX inputs, run route and core probes against temporary databases, create a sanitized audit log, record ranked findings, and close Runway OS state. Tasks 1 and 3-8, product fixes, tracked test or fixture expansion, real databases/statements/uploads, credentials, row-level financial data, production/demo access, Plaid or vendor-account actions, workflows, Fly, downstream writes, authentication/security changes, pre-existing `scripts/sync_prod_to_local.sh`, and all commit, push, PR, merge, and deployment actions remain excluded.

### 2026-07-18 — Accept work block 3B as verified with three high-risk correctness findings

The tracked smoke suite passed, and 60 ephemeral all-entity checks passed the CSV/PDF parser, profile, sign, invalid-row, exact-reimport, upload confirmation, Amazon/Henry parsing and deduplication, exact/review/unmatched order-matching, alias, cleanup, and isolation behaviors. Vendor-payment matching failed on every fresh entity because it references nonexistent `transactions.matched_order_id`; normal vendor imports persisted no line items for auto-split; and Amazon/category acceptance wrote undefined or nondeterministic category values outside `categories.md`. Task 2 is complete as an audit with these three high-risk findings, a medium tracked-coverage gap, and a low status-only `Undo` ambiguity recorded. No repair, product/test change, protected-data access, live action, or GitHub durability occurred, and Task 3 becomes current for a separately confirmed work block.

### 2026-07-18 — Authorize direct-main durability for the 3B audit closeout

Ryan explicitly instructed Codex to commit and push the verified 3B command-center closeout to `main`. This authorizes staging only the seven 3B command-center paths, committing with the established `[skip actions]` convention, and pushing `main` without force. Product, fixture, and tracked test files; pre-existing untracked `scripts/sync_prod_to_local.sh`; application/workflow changes; production deployment; live access; protected data; credentials; Plaid or vendor-account actions; Fly; and all recovery outside the exact closeout remain excluded.

### 2026-07-18 — Confirm work block 3C for the synthetic financial read-model audit

Ryan confirmed Task 3 as one synthetic-only audit of dashboard metrics, report views and exports, subscription detection, and cash-flow projections against the same deterministic multi-month transaction and account timeline across Personal, BFM, and Luxe Legacy. Codex may inspect tracked source, run the existing smoke suite, exercise ephemeral route and core probes against temporary databases, create a sanitized audit log, record ranked findings, and close Runway OS state. Tasks 1-2 and 4-8, product fixes, tracked fixture or test expansion, real databases, exports, balances, credentials, row-level financial data, production/demo access, Plaid or OpenRouter calls, workflows, Fly, downstream writes, authentication/security changes, pre-existing `scripts/sync_prod_to_local.sh`, and all commit, push, PR, merge, and deployment actions remain excluded.

### 2026-07-18 — Accept work block 3C as verified with one report defect and one coverage gap

The tracked smoke suite passed. The final ephemeral all-entity probe ran 306 checks with 297 passes, zero assertion failures, and nine controlled error reproductions representing one defect at the direct-query, prepared-report, and rendered-route layers in Personal, BFM, and Luxe Legacy. Dashboard totals, effective split replacement, exclusions, filters, all non-recurring report views and exports, subscriptions, cash flow, intended Personal/BFM visibility, LL isolation, and cleanup passed. The Recurring Charges report executes a literal `{exclude_sql('category')}` token and cannot run; the Task 3 paths also lack tracked regression coverage. Both findings are recorded without repair, product/test change, protected-data access, external call, live action, or GitHub durability. Task 3 is complete as an audit, and Task 4 becomes current for a separately confirmed work block.

### 2026-07-18 — Authorize direct-main durability for the 3C audit closeout

Ryan explicitly instructed Codex to commit and push the verified 3C command-center closeout to `main`. This authorizes staging only the seven 3C command-center paths, committing with the established `[skip actions]` convention, and pushing `main` without force. Product, fixture, and tracked test files; pre-existing untracked `scripts/sync_prod_to_local.sh`; application/workflow changes; production deployment; live access; protected data; credentials; Plaid or OpenRouter calls; Fly; and all recovery outside the exact closeout remain excluded.

### 2026-07-18 — Confirm work block 3D for the synthetic planning foundations audit

Ryan confirmed Tasks 4A-4B as one synthetic-only audit of long-term projections and cross-entity visibility plus short-term goals, snapshots, budgets, actions, and payoff planning. Codex may inspect tracked source, run the existing smoke suite, execute deterministic ephemeral probes against temporary entity databases, reconcile the parked legacy expectations, create a sanitized audit log, record ranked findings, and close Runway OS state. Tasks 4C-4D and 5-8, product repairs or migrations, tracked test/fixture/demo expansion, real financial or payroll data, credentials, production/demo access, Plaid or OpenRouter calls, workflows, Fly, downstream writes, authentication/security changes, pre-existing `scripts/sync_prod_to_local.sh`, and all commit, push, PR, merge, and deployment actions remain excluded.

### 2026-07-18 — Accept work block 3D as verified with four planning defects and one coverage gap

The tracked smoke suite passed, and the final ephemeral all-entity planning probe ran 58 checks with 48 passes, zero runtime errors, and ten controlled failures representing four distinct defects: locked payoff schedules hard-code APRs, LL denial is missing from direct planning routes, automatic snapshots erase same-day review notes, and negative appreciation does not depreciate assets. Goal CRUD, budgets, effective splits, averages, per-payroll math, actions, direct payoff engines, positive projections, linked balances, summaries, and intended Personal/BFM visibility passed. The core legacy goal/snapshot/budget/payoff/isolation expectations remain valid; short-term cross-entity linking and custom allocation are superseded. Planning paths still lack tracked regression coverage, demo goals/snapshots remain unseeded, Tasks 4A-4B and work block 3D are complete, and Task 4C becomes current for a separately confirmed 3E audit. No repair, tracked product/test/demo change, protected-data access, external call, live action, or GitHub durability occurred.

### 2026-07-18 — Authorize direct-main durability for the 3D audit closeout

Ryan explicitly instructed Codex to commit and push the verified 3D command-center closeout to `main`. This authorizes staging only the seven 3D command-center paths, committing with the established `[skip actions]` convention, and pushing `main` without force. Product, fixture, tracked test, and demo-seed files; pre-existing untracked `scripts/sync_prod_to_local.sh`; application/workflow changes; production deployment; live access; protected data; credentials; Plaid or OpenRouter calls; Fly; and all recovery outside the exact closeout remain excluded.

## Pending Ryan Direction

- Confirm or revise work block 3E for the synthetic weekly and waterfall audit in Task 4C. Any 3D repair, tracked regression coverage, protected-data access, live action, or further durability step requires a separate decision.

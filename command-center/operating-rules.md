# Expense Tracker Operating Rules

## Source Of Truth

- `command-center/roadmap.md` owns project direction, phases, and numbered tasks.
- `command-center/now.md` owns the current phase, work block, task, owner, blockers, and next action.
- `command-center/decisions.md` owns accepted and pending direction choices.
- `command-center/operating-rules.md` owns standing process, privacy, and side-effect boundaries.
- `command-center/state.json` mirrors the dashboard-visible project state.
- `command-center/index.html` is generated display output and never source truth.
- `command-center/logs/` holds dated execution and verification evidence.
- `command-center/handoffs/` holds scoped packets for another agent or a restart.
- `command-center/ideas.md` and `issues.md` hold parked, non-active items.

## Existing-Repo Shape

Expense Tracker is an existing Flask application. Product source stays in `web/`, `core/`, `scripts/`, `fixtures/`, and root runtime/configuration files. Do not add scratch-project `app/` or `scratch/` roots merely to satisfy a generic scaffold expectation.

`categories.md` remains the domain source of truth for category and subcategory definitions. Runway OS governs project control; it does not replace product-domain contracts.

## Full Install And Profile Semantics

This repo has the complete Runway OS command-center surface. Its `sensitive-retrofit` scaffold profile records stricter defaults for financial, payroll, credentialed, and production work; it does not make the OS partial.

External worker runners and write-capable agent-router automation are not installed by default. Add them only through a separately confirmed project-local routing-policy block.

## Financial, Credential, And Data Boundaries

Closed by default:

- `.env` and all credential values;
- `local_state/`, SQLite files, WAL/SHM files, and row-level financial data;
- uploads, backups, statements, raw exports, screenshots, and temporary financial payloads;
- Plaid access tokens and account/transaction detail;
- payroll/HR row detail;
- production or downstream database contents.

Runway OS artifacts, logs, dashboards, handoffs, parent pointers, and chat reports must stay at a sanitized project-control level unless Ryan explicitly approves a narrower local task.

## Live Side-Effect Gate

These require a separately confirmed work block with exact targets, stop conditions, and verification:

- enabling, disabling, dispatching, or rerunning GitHub Actions;
- Plaid link, sync, disconnect, or account changes;
- Fly deploy, secret, SSH, SFTP, console, restart, or production database operations;
- local/production database transfer scripts;
- downstream Luxe Legacy/Supabase writes;
- changes to authentication, CSRF, encryption, credential, or public-route behavior;
- destructive data cleanup or migration.

Read-only GitHub metadata, safe HTTP health checks, synthetic tests, and local source inspection are allowed when they stay inside the confirmed work block.

## Pre-Existing Worktree Rule

`AGENTS.md` and `scripts/sync_prod_to_local.sh` were untracked before Runway OS installation. Preserve them and never stage, edit, delete, or absorb them into another change unless Ryan explicitly approves those paths.

Ignored local files belong to the user and are not retrofit inputs by default.

## Legacy Documentation Migration

Legacy project plans, architecture references, status notes, and operator instructions are migration inputs or supporting domain docs, not competing project-control authorities.

Do not delete, archive, replace, or demote them without Ryan approval. First record their classification and migrate useful current project-control substance into Runway OS.

## Work Blocks

Phase tasks hold normal planned work. Confirmed work blocks authorize bounded autonomous execution.

Every work block records:

- included and excluded task numbers;
- owner and recommended agent;
- expected files and systems touched;
- stop conditions;
- verification checks;
- dashboard/state closeout;
- target and parent durability status;
- next report point.

After Ryan confirms a work block, write it into the command center before implementation, delegation, or second opinion. Stay inside the block until complete or a stop condition is reached.

## Agent Selection

Codex is the default owner for Runway OS stewardship, cross-file integration, local verification, and final intake. Use the current parent agent-selection policy when recommending another worker.

No external worker receives financial data, credentials, production outputs, or write authority without an explicit project-local policy and Ryan approval.

## Verification

Safe baseline checks are:

- `.venv/bin/python scripts/smoke_test.py` using its temporary synthetic `DATA_DIR`;
- `node command-center/scripts/refresh-dashboard.js`;
- `node command-center/scripts/health-check.js`;
- `git diff --check`;
- generated dashboard inspection;
- read-only GitHub status and HTTP checks when relevant.

Skipped checks must state why: unsafe, unavailable, credential-dependent, side-effect-heavy, out of scope, or blocked.

## Dashboard Currency

After meaningful changes to phase, task, work block, owner, blocker, next action, decisions, waiting state, artifacts, verification, or closeout:

1. Update human-readable sources first.
2. Update `command-center/state.json` to match.
3. Run `node command-center/scripts/refresh-dashboard.js`.
4. Run `node command-center/scripts/health-check.js`.
5. Inspect the generated dashboard and relevant diff.

Do not call Runway OS current if refresh or health check fails.

## Git And Durability

- Use `codex/` branches for Runway OS or implementation work unless Ryan specifies otherwise.
- Do not stage pre-existing dirty or untracked files outside the confirmed paths.
- Do not commit or push unless Ryan asks or the confirmed work block includes GitHub durability.
- Dashboard freshness and GitHub durability are separate. Report branch, status, commit, push, and `committed-and-pushed`, `committed-local-only`, `local-only`, `waiting`, or `blocked` explicitly.
- Production deploys from `main` are never implied by a local Runway OS change.

## Parent Boundary

The Expense Tracker repo owns detailed project state and implementation history. The parent Projects Project repo may later receive a compact sanitized pointer and reusable lesson after Ryan authorizes parent durability. It must not copy financial detail or the target backlog wholesale.

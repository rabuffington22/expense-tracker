# Existing-Project Retrofit Intake

Date: 2026-07-17

Status: read-only intake complete; full Runway OS bootstrap confirmed

## Target Identity

- Project: Expense Tracker / The Ledger
- Local path: `/Users/ryanbuffington/Documents/GitHub/expense-tracker`
- Type: existing private Git repository and production Flask application
- Remote: `https://github.com/rabuffington22/expense-tracker.git`
- Baseline branch: `main`
- Baseline HEAD: `a27f790879657ff1a55e73b158f176c15a068fec`
- Install branch: `codex/runway-os-full-install`
- Baseline GitHub durability: local `main` matched `origin/main`

## Pre-Existing Worktree State

- Status: tracked tree clean at intake; two pre-existing untracked files
- Preserve and never stage by default: `AGENTS.md`, `scripts/sync_prod_to_local.sh`
- Ignored local surfaces present: `.env`, `.venv/`, `local_state/`, caches, and local Claude settings
- No pre-existing `command-center/`

## Safe Source Inventory

Reviewed:

- Git status, branches, remotes, recent commits, tracked-file inventory, and ignore rules
- `README.md`, `PROJECT_KNOWLEDGE.md`, `CLAUDE.md`, `plan.md`, `categories.md`, and `AGENTS.md`
- Application directory shape, route inventory, migration list, requirements, test entry point, GitHub workflows, and deployment configuration
- GitHub open issues, open pull requests, recent commits, workflow state, and recent workflow runs
- Production and demo root HTTP availability

Intentionally not opened:

- `.env`
- `local_state/` and SQLite contents
- uploads, backups, statements, raw exports, production data, or credential values
- live Plaid account or transaction detail
- Fly logs or production database contents

Safe checks discovered:

- `.venv/bin/python scripts/smoke_test.py` uses a temporary synthetic `DATA_DIR`
- `node command-center/scripts/refresh-dashboard.js`
- `node command-center/scripts/health-check.js`
- `git diff --check`
- read-only GitHub workflow/status queries
- unauthenticated production and demo root HTTP checks

## Sensitive And Side-Effect Boundaries

Possible data classes include personal and business financial transactions, account information, payroll/HR information, Plaid access tokens, production credentials, and downstream Luxe Legacy transaction data.

Side-effect-heavy actions include:

- re-enabling or triggering GitHub Actions workflows;
- Plaid link, sync, disconnect, or account mutations;
- Fly deploys, secrets, SSH, SFTP, or production database work;
- local-to-production or production-to-local database synchronization;
- downstream Supabase writes;
- any operation that exposes row-level financial or credential data.

These actions require a separately confirmed project-local work block.

## Source-Of-Truth Migration Map

| Existing surface | Classification | Runway OS treatment |
|---|---|---|
| `README.md` | replacement candidate | Preserve now; rebuild from current architecture in proposed Phase 2. |
| `PROJECT_KNOWLEDGE.md` | historical source input | Preserve now; extract any unique history, then archive or replace with Ryan approval. |
| `plan.md` | implemented-plan history | Preserve now; mark historical or archive after verifying no open commitments remain. |
| `CLAUDE.md` | supporting domain library and current source input | Keep as supporting reference; migrate project-control rules into command-center files. |
| `AGENTS.md` | pre-existing untracked supporting artifact | Leave untouched and untracked until Ryan decides its future. |
| `categories.md` | domain source of truth | Keep as-is; link from architecture and project structure. |
| `.github/workflows/` | live operational surface | Keep as-is; promote the disabled Daily Plaid Sync workflow into proposed Phase 1. |
| Git history and successful deploy/sync runs | evidence/history | Use as safe project-control evidence without copying financial details. |

## Intake Findings

- The synthetic smoke suite passed.
- Production and demo roots returned HTTP 200 during intake.
- There were no open GitHub issues or pull requests.
- The last code commit and successful deploy were on 2026-05-15.
- The Daily Plaid Sync workflow is currently `disabled_inactivity`; its last listed successful scheduled run was 2026-07-15.
- Documentation and project-control truth have materially drifted from the current Flask, Plaid, Fly.io, three-entity implementation.

## Recommended Next Work

Complete work block 0A, ask Ryan to confirm the proposed roadmap, then run a bounded Phase 1 operational-reliability block. The first live action should be an explicitly approved re-enable-and-verify pass for Daily Plaid Sync; it should not be hidden inside the Runway OS install.

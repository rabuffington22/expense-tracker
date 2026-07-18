# The Ledger — Agent Instructions

## Authority And Re-entry

Read these sources before acting:

1. `command-center/now.md` for the active phase, task, work block, owner, blockers, and next action.
2. `command-center/roadmap.md` for numbered tasks and confirmed work-block scope.
3. `command-center/decisions.md` and `command-center/operating-rules.md` for accepted direction and durable safety rules.
4. `README.md` for current architecture, setup, application surfaces, deployment mechanics, and sanitized operating boundaries.
5. `categories.md` for category and subcategory definitions.
6. Tracked source and synthetic tests for implementation truth.

Runway OS in `command-center/` is canonical for project control. `PROJECT_KNOWLEDGE.md` and `plan.md` are historical notices. `CLAUDE.md` is only a compatibility entry point to this file.

Do not infer implementation authorization from roadmap placement alone. Product, documentation, live, or GitHub mutations require the exact scope of a confirmed work block or a direct Ryan request.

## Current Product Shape

The Ledger is a Flask, Jinja, HTMX, and SQLite expense tracker hosted on Fly.io. Plaid is the primary connected-account integration when configured; CSV/PDF statement import remains a fallback. Vendor order imports support Amazon CSV and Henry Schein XLSX data.

Production entities are fully isolated:

- Personal → `personal.sqlite`
- BFM → `company.sqlite`
- LL → `luxelegacy.sqlite`

`DATA_DIR` selects the database and upload root. The demo uses a separate Fly app, volume, synthetic data, and entity override.

## Repository Map

- `web/` — Flask factory, route blueprints, templates, static assets, PWA, and HTTP/UI behavior.
- `core/` — migrations, imports, categorization, reporting, Plaid, AI, and financial business logic.
- `scripts/` — synthetic smoke tests, demo seeding, and controlled utilities.
- `fixtures/` — synthetic import fixtures.
- `.github/workflows/` — production deployment and scheduled Plaid synchronization.
- `command-center/` — current direction, decisions, state, logs, handoffs, and generated dashboard.
- `README.md` — maintained project entry point.
- `categories.md` — category/subcategory domain source of truth.

Do not add obsolete Streamlit `app/` or `scratch/` roots. The current application entry point is `run.py` and product code stays in the existing Flask structure.

## Protected Data Boundary

Closed by default:

- `.env` and credential values;
- `local_state/`, SQLite files, WAL/SHM files, and row-level financial data;
- uploads, backups, statements, exports, screenshots, and temporary financial payloads;
- Plaid access tokens and account/transaction detail;
- payroll or HR row detail;
- production or downstream database contents.

Never place real secret values or row-level financial information in tracked files, command-center artifacts, logs, handoffs, PR text, or chat reports. Use synthetic fixtures and sanitized project-control metadata.

## Live Side-Effect Gate

These require separate target-specific authorization:

- enable, disable, dispatch, or rerun GitHub Actions;
- Plaid link, sync, disconnect, or account changes;
- Fly deploy, secret, SSH, console, restart, or production database operations;
- local/production database transfers or destructive cleanup;
- downstream Luxe Legacy writes;
- authentication, encryption, CSRF, credential, or public-route changes;
- merge to `main`, which triggers the production Fly deployment workflow.

Stop at the exact gate when authorization, credentials, or safe verification are missing. Do not improvise around it.

## Working-Tree And Git Rules

- Preserve user changes and inspect `git status --short --branch` before editing or staging.
- `scripts/sync_prod_to_local.sh` is a pre-existing untracked user file. Do not edit, stage, delete, or absorb it without explicit authorization.
- Use `codex/` branches unless Ryan requests another name.
- Stage explicit paths in mixed worktrees; do not default to `git add -A`.
- Do not commit, push, open a PR, merge, or deploy unless the confirmed block includes that action.
- Feature-branch pushes and draft PRs do not deploy production. A merge or push to `main` does.

## Implementation Conventions

- Keep entity databases, categories, aliases, imports, and reporting isolated. Any cross-entity behavior must be explicit and tested.
- Database migrations are additive and ordered in `core/db.py`; do not rewrite an applied migration.
- Transaction IDs are deterministic. Preserve deduplication behavior.
- Negative transaction amounts represent debits.
- Reporting exclusions are centralized in `core/reporting.py`; reuse those helpers rather than creating competing lists.
- Reporting uses split transactions in place of split parents. Reuse the established effective-transaction query path.
- Flask's cookie session is size-limited. Large upload or matching payloads belong in temporary files, not the session.
- Prefer server-rendered Flask/HTMX patterns already used by the surrounding page. Keep swaps and targets narrowly scoped.
- Preserve the entity cookie, CSRF/authentication behavior, PWA/service-worker routes, accessibility landmarks, keyboard behavior, and mobile navigation unless the confirmed block explicitly changes them.
- Never test product behavior against real financial databases when synthetic temporary data can answer the question.

## Safe Verification

Preferred checks:

```bash
.venv/bin/python scripts/smoke_test.py
node command-center/scripts/refresh-dashboard.js
node command-center/scripts/health-check.js
git diff --check
git status --short --branch
```

The smoke suite uses a temporary synthetic `DATA_DIR` and requires no live server or production credentials. Add focused synthetic coverage for changed behavior when appropriate.

After meaningful command-center state changes:

1. update human-readable source files;
2. align `command-center/state.json`;
3. run the dashboard refresh;
4. run the command-center health check;
5. inspect the generated dashboard and relevant diff.

Do not call a work block complete while required verification is failing or the dashboard communicates stale state.

## Documentation Maintenance

Keep maintained guidance compact and source-linked:

- update `README.md` when architecture, setup, product surfaces, or deployment mechanics change;
- update this file when repository-wide agent rules or safety boundaries change;
- update `categories.md` for category-domain changes;
- update Runway OS for current direction, decisions, task state, and closeouts;
- prefer Git history and dated command-center logs over a growing duplicated change log.

If documentation and code disagree, verify the code and tests, correct the maintained documentation within scope, and record plan-changing uncertainty rather than guessing.

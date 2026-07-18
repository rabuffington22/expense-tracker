# Expense Tracker Project Structure

## Existing Product Surfaces

- `web/`: Flask application factory, routes, templates, static assets, PWA, and HTTP/UI behavior.
- `core/`: database migrations, financial business logic, categorization, import, Plaid, reporting, cryptography, and cross-app integration.
- `scripts/`: synthetic smoke tests, safe demo seeding, controlled maintenance utilities, and production-oriented operator scripts.
- `fixtures/`: synthetic import fixtures used by tests.
- `.github/workflows/`: Fly deployment and scheduled Plaid synchronization.
- `run.py`, `Dockerfile`, `fly.toml`, `fly.demo.toml`, and `requirements.txt`: runtime and deployment configuration.
- `categories.md`: domain source of truth for categories and subcategories.

## Runway OS

- `command-center/`: canonical project direction, current state, decisions, operating rules, structured dashboard state, generated dashboard, logs, handoffs, templates, and safe helper surfaces.
- `command-center/state.json`: machine-readable dashboard state.
- `command-center/roadmap.md`: phase plan and numbered task inventory.
- `command-center/now.md`: current phase, work block, task, owner, blockers, and next action.
- `command-center/decisions.md`: accepted and pending direction choices.
- `command-center/operating-rules.md`: durable process, privacy, and side-effect boundaries.
- `command-center/index.html`: generated dashboard view; never the source of truth.

## Existing Documentation And Migration Status

- `CLAUDE.md`: current but very large domain and operating reference; supporting source input, not the project-control authority.
- `README.md`: current root entry point for architecture, local setup, application surfaces, deployment mechanics, data handling, and sanitized operating boundaries.
- `PROJECT_KNOWLEDGE.md`: tracked historical architecture reference; archive or replacement candidate in proposed Phase 2.
- `plan.md`: tracked implementation plan whose major feature already exists; historical/archive candidate after review.
- `AGENTS.md`: pre-existing untracked local instruction file; preserve untouched until Ryan explicitly decides its tracked status.

## Data And Credential Boundary

Ignored `.env`, `local_state/`, SQLite files, uploads, backups, statements, and local caches are outside normal Runway OS inspection and reporting. They are never copied into command-center artifacts.

## Retrofit Rule

This is an existing application, not a scratch project. Product work stays in the established product folders. Do not introduce `app/` or `scratch/` as competing product roots.

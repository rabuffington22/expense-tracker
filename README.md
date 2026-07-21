# The Ledger

The Ledger is a Flask, HTMX, and SQLite expense tracker for personal and business finances. It combines Plaid transaction sync, CSV/PDF statement import, vendor-order matching, categorization, reporting, cash-flow planning, and installable PWA behavior in one server-rendered application.

- Production: [ledger-oak.fly.dev](https://ledger-oak.fly.dev)
- Demo: [ledger-oak-demo.fly.dev](https://ledger-oak-demo.fly.dev)
- Runtime: Flask + Gunicorn on Fly.io
- UI: Jinja templates + HTMX, with responsive desktop/mobile layouts
- Storage: one SQLite database per entity on the configured `DATA_DIR`

## Entity isolation

Production has three entities. The selected entity is stored in a browser cookie, and each entity uses its own database and category configuration.

| Display name | Database | Notes |
| --- | --- | --- |
| Personal | `personal.sqlite` | Personal spending, cash flow, planning, and debt tracking |
| BFM | `company.sqlite` | Company expenses, payroll, budgets, and surplus waterfall inputs |
| LL | `luxelegacy.sqlite` | Luxe Legacy business transactions and reporting |

The demo overrides this map with `ENTITIES=Personal:personal,Business:company` and uses a separate Fly app and volume.

## Core capabilities

- Plaid account connection, transaction sync, account balances, and credit-card liabilities
- CSV and PDF bank-statement import with reusable source profiles and deterministic deduplication
- Amazon CSV and Henry Schein XLSX order import, transaction matching, line-item breakdown, and categorization
- Merchant aliases, keyword suggestions, category/subcategory budgets, transaction splits, and review queues
- Dashboard analysis, transaction filtering, saved views, subscriptions, cash flow, and monthly reports
- Long-term planning, short-term goals and budgets, weekly check-ins, and BFM-to-Personal waterfall planning
- BFM employee roster and Phoenix/CyberPayroll import
- Optional OpenRouter-powered chat, category suggestions, subscription tips, and dashboard analysis
- PWA manifest, static/offline-only service-worker caching, data-free offline fallback, mobile navigation, and dark/light themes
- Standalone mobile-oriented dashboard at `/k/`; it uses the main session gate when authentication is configured

## Architecture

```text
Browser / installed PWA
        |
        v
Flask routes + Jinja templates + HTMX
        |
        v
Core import, categorization, reporting, planning, and sync modules
        |
        +--> personal.sqlite
        +--> company.sqlite
        +--> luxelegacy.sqlite
        |
        +--> Plaid API (optional)
        +--> OpenRouter API (optional)
        +--> Luxe Legacy downstream mirror (optional, LL sync only)
```

`web/` owns HTTP and UI behavior. `core/` owns database migrations and business logic. SQLite databases use WAL mode and are initialized or migrated when an entity is accessed. `categories.md` is the domain source of truth for category and subcategory definitions.

## Local development

Use Python 3.12 when possible to match the production container.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Generate a local Flask secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace the placeholder `FLASK_SECRET` in `.env` with the generated value, then start the app:

```bash
python run.py
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501). `run.py` loads the project-root `.env` file and starts Flask on port 8501. Local data defaults to `./local_state/`.

### Synthetic smoke test

```bash
.venv/bin/python scripts/smoke_test.py
```

The smoke suite creates a temporary `DATA_DIR` and uses synthetic fixtures. It does not need a live server, production credentials, or real financial data.

## Configuration

Never place real secret values in tracked files, documentation, test fixtures, command-center artifacts, or issue/PR text.

| Variable | Required | Purpose |
| --- | --- | --- |
| `FLASK_SECRET` | Yes | Flask session signing and the key source for encrypted Plaid access tokens |
| `DATA_DIR` | No | Database, upload, and backup root; defaults to `./local_state` and is `/data` on Fly |
| `FLASK_DEBUG` | No | Enables local Flask debug mode when truthy |
| `ENTITIES` | No | Overrides the display-name/database map, primarily for the demo app |
| `APP_PASSWORD_HASH` | Production gate | Enables the server-rendered login and authenticated session; accepts the legacy raw SHA-256 digest or a Werkzeug password hash, while unset disables the gate |
| `PLAID_CLIENT_ID` | Plaid only | Plaid application identifier |
| `PLAID_SECRET` | Plaid only | Plaid environment secret |
| `PLAID_ENV` | Plaid only | `sandbox` or `production`; defaults to `sandbox` |
| `SYNC_SECRET` | Scheduled sync only | Bearer secret protecting `/plaid/sync-all` |
| `OPENROUTER_API_KEY` | AI only | Enables optional AI features |
| `LUXURY_SUPABASE_URL` | LL mirror only | Optional downstream Luxe Legacy endpoint |
| `LUXURY_SUPABASE_SERVICE_KEY` | LL mirror only | Optional downstream Luxe Legacy service credential |

When `APP_PASSWORD_HASH` is configured, Flask redirects unauthenticated full-page requests to a standalone login before entity setup or protected-page rendering. Password verification occurs only on the server; the browser receives an authenticated session, not the configured digest. The session cookie is explicitly HttpOnly and SameSite Lax in every environment; Fly runtimes are detected through the infrastructure-provided `FLY_APP_NAME` value and additionally require the Secure attribute, while ordinary local HTTP remains usable. The cookie remains host-only, application-root scoped, and non-permanent. The standalone `/k/` dashboard uses this same session gate but remains outside global entity setup because it manages Personal and Luxe Legacy contexts itself. Static assets, health/offline surfaces, login, and the bearer-protected scheduled-sync endpoint follow explicit exemptions in `web/__init__.py`. The service worker caches only static assets and the data-free offline page, never protected or entity-specific responses. Authentication changes remain controlled work and should not be treated as a routine documentation or deployment edit.

## Data layout and handling

With the default local configuration:

```text
local_state/
├── personal.sqlite
├── company.sqlite
├── luxelegacy.sqlite
├── uploads/
└── backups/
```

Real databases, WAL/SHM files, `.env`, uploads, backups, statements, exports, and temporary financial payloads are ignored and must remain outside Git history. Parsed upload and AI-chat intermediates use temporary directories so Flask's cookie session stays below its size limit.

Transaction IDs are deterministic, so importing the same normalized bank transaction again does not create a duplicate. Reporting uses centralized exclusion rules and replaces a split parent transaction with its categorized split pieces when splits exist.

## Main application surfaces

| Surface | Route | Purpose |
| --- | --- | --- |
| Dashboard | `/` | KPI comparisons, trends, insights, recurring items, and review status |
| To Do | `/todo/` | Review queues, recurring work, tasks, cut list, and workflow entry points |
| Transactions | `/transactions/` | Filtering, saved views, inline edits, rules, suggestions, and splits |
| Subscriptions | `/subscriptions/` | Recurring-subscription detection, tracking, account notes, and cancellation tips |
| Cash Flow | `/cashflow/` | Manual/Plaid balances, liabilities, and upcoming recurring charges |
| Short-Term Planning | `/planning/short-term` | Goals, budgets, action items, progress, and plan locking |
| Long-Term Planning | `/planning/` | Asset/liability projections and milestone planning |
| Payroll | `/payroll/` | BFM employee roster, pay history, and Phoenix/CyberPayroll imports |
| Weekly | `/weekly/` | Weekly scorecard, bills, pace, and credit-card paydown tracking |
| Waterfall | `/waterfall/` | BFM surplus and Personal debt-paydown scenarios |
| Reports | `/reports/` | Monthly detail, category drill-downs, exports, and CSS spending trends |
| Connected Accounts | `/plaid/` | Plaid Link, per-item sync, account visibility, rename, and disconnect |
| Data Sources | `/data-sources/` | Vendor-order imports and supported vendor-account connections |
| Import | `/upload/` | CSV/PDF statement sources, profiles, preview, confirmation, and undo |
| Match/Categorize | `/match/`, `/categorize-vendors/`, `/categorize/` | Vendor matching and remaining categorization workflow |
| Focused dashboard | `/k/` | Standalone mobile-oriented Personal and Luxe Legacy view using the configured session gate |

## Imports and synchronization

Plaid is the primary bank-transaction integration when configured. Users can connect and sync accounts from `/plaid/`. GitHub Actions also calls the bearer-protected `/plaid/sync-all` endpoint on the configured daily schedule. The application does not perform a Plaid sync merely because the server starts.

CSV/PDF bank statements remain available as a fallback. Vendor imports support Amazon order CSVs and Henry Schein XLSX exports. Vendor data can be matched to bank transactions to replace generic charge descriptions with actual product/order context and to create categorized transaction splits.

After a successful LL Plaid sync, an optional bridge can upsert eligible transactions to the configured Luxe Legacy downstream service. The bridge is a no-op when either environment variable is absent. It accepts only non-empty Plaid transaction IDs that are already free of surrounding whitespace, withholds every row in an ambiguous duplicate-key group while continuing unrelated valid rows, and explicitly uses `plaid_transaction_id` as the downstream conflict target. It never changes the Ledger databases' source-of-truth role.

## Deployment and operations

Production uses `fly.toml`, a persistent `/data` volume, and Gunicorn on internal port 8080. The demo uses `fly.demo.toml`, its own app and volume, a separate entity override, and synthetic seed data.

GitHub Actions currently owns two operational workflows:

- `Fly Deploy`: a push to `main` deploys the production Fly app. It can also be dispatched manually.
- `Daily Plaid Sync`: runs at 09:17 UTC and calls the protected all-entity sync endpoint. It can also be dispatched manually.

Feature-branch pushes and draft PRs do not match the production deploy trigger. Merging to `main`, manually dispatching either workflow, changing Fly secrets, and invoking a Plaid sync are live side effects and require an explicitly approved work block.

The application exposes `/health` for a minimal health check. The production and demo roots may also be checked by HTTP status when a confirmed verification block allows external reads.

## Operating boundaries

Safe default development and verification work uses only source code, synthetic fixtures, temporary test databases, and sanitized project-control metadata.

The following actions require explicit target-specific authorization before execution:

- Plaid link, sync, disconnect, or account changes
- GitHub Actions enable, disable, dispatch, or rerun
- Fly deploy, secret, SSH, console, restart, or production database operations
- Local/production database transfers, data cleanup, migration, or destructive demo reseeding
- Downstream Luxe Legacy writes
- Authentication, encryption, CSRF, credential, or public-route behavior changes
- Inspection or disclosure of row-level financial, payroll, credential, or upload data

When one of these boundaries is reached, stop at the exact gate and request direction. Do not work around missing credentials or broaden a documentation/testing task into a live operational action.

## Repository map

```text
web/                    Flask application, routes, templates, static assets, PWA
core/                   Database migrations and financial business logic
scripts/                Synthetic tests, demo seeding, and controlled utilities
fixtures/               Synthetic import fixtures
.github/workflows/      Production deploy and scheduled Plaid sync
command-center/         Canonical project direction, state, decisions, and dashboard
categories.md           Category/subcategory domain source of truth
run.py                  Local Flask entry point
Dockerfile              Production Gunicorn image
fly.toml                Production Fly configuration
fly.demo.toml           Demo Fly configuration
requirements.txt        Python dependencies
```

## Project control and documentation

Runway OS in `command-center/` is the source of truth for active phases, tasks, decisions, safety rules, and verified closeouts:

- `command-center/now.md` — current phase, work block, owner, blocker, and next action
- `command-center/roadmap.md` — phases and numbered task inventory
- `command-center/decisions.md` — accepted and pending direction choices
- `command-center/operating-rules.md` — durable privacy and side-effect boundaries
- `command-center/state.json` — machine-readable dashboard state
- `command-center/index.html` — generated dashboard view, not a source file

`AGENTS.md` is the canonical agent and contributor instruction source. `CLAUDE.md` is a compatibility entry point that directs Claude-based tools to the same maintained guidance. `PROJECT_KNOWLEDGE.md` and `plan.md` are concise historical notices whose full former contents remain available through Git history.

After changing command-center state, refresh and verify it with:

```bash
node command-center/scripts/refresh-dashboard.js
node command-center/scripts/health-check.js
```

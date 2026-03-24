# The Ledger

## What This Is
Flask + HTMX + SQLite personal/business expense tracker. Hosted on Fly.io. Bank and credit card transactions sync automatically via Plaid API (connected accounts). CSV/PDF bank statement import retained as fallback. Vendor order data (Amazon CSV, Henry Schein XLSX) matched to bank transactions for real product names.

Previously built on Streamlit — migrated to Flask + HTMX to eliminate WebSocket disconnect issues during interactive workflows.

## Three Entities (Fully Isolated)
- **Personal** -> `personal.sqlite`
- **BFM** (company) -> `company.sqlite`
- **LL** (Luxe Legacy) -> `luxelegacy.sqlite`

Each has its own DB, categories, aliases, import checklists. Entity selected via sidebar toggle.

## Key Paths
- **Repo (Home Mac):** `/Users/ryanbuffington/expense-tracker`
- **App URL:** `https://ledger-oak.fly.dev`
- **Demo URL:** `https://ledger-oak-demo.fly.dev` (no auth, seed data, 2 entities)

## Plaid Integration
- **Status:** Production approved and running (`PLAID_ENV=production`)
- **Plaid app name:** BFM Expense Tracker (Plaid dashboard)
- **Client ID:** `69a02460632219000ea2ea03`
- **Env vars required:** `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV` (sandbox|production)
- **Current deploy:** Running in production mode (`PLAID_ENV=production`)
- **Sandbox test creds:** username `user_good`, password `pass_good`
- **Connected Accounts page:** `/plaid/` — connect banks, sync, disconnect
- **Sync:** Manual only (no auto-sync on startup) — POST `/plaid/sync`
- **Migration 18:** Added `plaid_items`, `plaid_accounts` tables + `plaid_item_id` on transactions
- **Plaid products:** `transactions` (required) + `liabilities` (optional). Link token uses `optional_products=[Products("liabilities")]` — silently included without separate consent screen.
- **Liabilities integration:** `get_liabilities()` in `plaid_client.py` fetches credit card balance, credit limit, next payment due date, minimum payment. Cash Flow page auto-populates from Plaid when `plaid_account_id` is linked. Falls back to manual entry if Plaid unavailable. Payment section hidden when no data from either source.
- **SDK note:** plaid-python v38.3.0 only has `Sandbox` and `Production` environments (no `Development`)

## Deploy
Push to `main` — GitHub Actions automatically deploys to Fly.io via `.github/workflows/fly-deploy.yml`.

```bash
git push origin main
```

That's it. No SSH, no manual restart needed.

### Demo Instance
Separate Fly app (`ledger-oak-demo`) with fake seed data, no auth, 2 entities (Personal + Business).

```bash
# Deploy demo
fly deploy --config fly.demo.toml --remote-only

# Re-seed demo data (wipe + recreate)
fly ssh console -a ledger-oak-demo -C 'python3 /app/scripts/seed_demo_data.py'
```

- **Config:** `fly.demo.toml` — separate volume (`ledger_oak_demo_data`), `ENTITIES=Personal:personal,Business:company`
- **Auth:** Disabled (no `APP_USERNAME`/`APP_PASSWORD` env vars)
- **Entity override:** `ENTITIES` env var in `web/__init__.py` — format `"Display:key,Display:key"`
- **Seed script:** `scripts/seed_demo_data.py` — ~1010 personal (26 categories) + ~688 business (22 categories) transactions, accounts, recurring. Wipes and re-seeds on each run.

## Directory Structure
```
web/                               # Flask app (replaced old app/ Streamlit code)
  __init__.py                      # Flask app factory, entity cookie, before_request hook
  routes/                          # Route blueprints (one per page)
    dashboard.py                   # GET / (KPI panels, categories, insights, AI analysis)
    transactions.py                # GET/POST /transactions (filterable list, inline edit, AI suggest)
    todo.py                        # GET/POST /todo (review queues, statement reminders)
    subscriptions.py               # GET/POST /subscriptions (watchlist, tracking, AI tips)
    cashflow.py                    # GET /cashflow (account balances, upcoming bills)
    planning.py                    # GET/POST /planning (net worth projections)
    payroll.py                     # GET/POST /payroll (employee roster, Phoenix import, role spending)
    short_term_planning.py         # GET/POST /planning/short-term (budgets, action items, goals)
    weekly.py                      # GET/POST /weekly (weekly check-in, bills, CC paydown)
    waterfall.py                   # GET /waterfall (BFM surplus to personal debt paydown)
    reports.py                     # GET /reports (monthly detail + spending trend)
    ai.py                          # POST /ai/ask, /ai/clear (global Ask Opus chat, per-page context)
    plaid.py                       # GET/POST /plaid (connect, sync, disconnect)
    saved_views.py                 # POST /saved-views (CRUD for filter presets)
    upload.py                      # GET/POST /upload (bank statement import)
    vendors.py                     # GET/POST /vendors (Amazon CSV, Henry Schein XLSX)
    match.py                       # GET/POST /match (link orders to bank txns)
    categorize_vendors.py          # GET/POST /categorize-vendors (label vendor orders)
    categorize.py                  # GET/POST /categorize (remaining txns + settings)
    kristine.py                    # GET /k/ (Kristine's public dashboard, no auth)
  templates/
    base.html                      # Layout: sidebar + main content, mobile header/hamburger
    components/
      sidebar.html                 # Entity toggle + primary nav (ARIA nav landmark)
      dashboard_body.html          # Dashboard main content (HTMX swap target)
      kpi_panel.html               # KPI compare panel (left/right)
      categories_compare.html      # Categories comparison bar chart
      insights_upcoming.html       # Expense Insights + Upcoming recurring side-by-side (Compare view)
      dashboard_detail_insights.html # Expense Insights + Upcoming (Details view)
      dashboard_detail_cats.html   # Detail categories bar chart (Details view)
      dashboard_ie_insights.html   # Income vs Expenses Insights (below IE chart)
      ai_analysis.html             # AI analysis results partial
      txn_results.html             # Transaction list results (HTMX swap target)
      txn_row.html                 # Single transaction row (includes split badge)
      txn_row_edit.html            # Inline-edit transaction row
      txn_split_editor.html        # Split transaction modal (balance validation, auto-split)
      todo_queue_detail.html       # To Do queue popup detail
      vendor_card.html             # Vendor order card (HTMX swap target)
      match_card.html              # Match review card (HTMX swap target)
      flash.html                   # Success/error flash messages
    dashboard.html
    transactions.html
    todo.html
    subscriptions.html             # Subscription watchlist + detail modals
    cashflow.html                  # Per-account balance cards + edit modals
    planning.html                  # Net worth projections + add/edit modals
    payroll.html                   # Employee roster, role spending, Phoenix import
    reports.html                   # Two-section layout: monthly detail + spending trend
    weekly.html                    # Weekly check-in: KPI, CC paydown, bills, scorecard
    waterfall.html                 # BFM surplus waterfall to personal debt
    plaid.html                     # Connected Accounts (Plaid Link)
    upload.html                    # Import tab + Settings tab
    upload_dialog.html             # File upload + preview/confirm
    vendors.html                   # Upload + date filter + save
    match.html
    categorize_vendors.html
    categorize.html                # Review tab + Settings tab
    kristine.html                  # Kristine's dashboard (standalone, no base.html)
  static/
    style.css                      # Apple-style dual theme (dark default + light), CSS custom properties on data-theme, SF Pro fonts
    htmx.min.js                    # HTMX library (~14KB)
    ledger-ai-icon.png             # Sidebar brand icon (176×176 display, vertical stacked layout)
    joker-button.png               # Ask Opus button icon (66×66 display, purple ? with glow)
    sw.js                          # Service worker (PWA: cache-first static, network-first navigation)
    manifest.json                  # PWA manifest (installable, standalone display)
    icon-192x192.png               # PWA icon 192px (gold L monogram on dark rounded-rect)
    icon-512x512.png               # PWA icon 512px (gold L monogram)
    icon-1024x1024.png             # PWA icon 1024px (gold L monogram, master size)
    the-ledger-logo-lockup.png     # Full logo lockup (header/mobile-header use)
    the-ledger-seal.png            # Wax seal artwork (sidebar brand icon)
  templates/
    offline.html                   # PWA offline fallback page (standalone, no base.html)
core/                              # Business logic
  db.py                            # Schema migrations (56 so far), DB init, connections
  ai_client.py                     # OpenRouter API client (Claude via OpenRouter for AI features)
  imports.py                       # CSV/PDF parsing, normalization, dedup
  categorize.py                    # Alias matching, keyword heuristics
  amazon.py                        # Amazon order CSV parsing + vendor order matching
  henryschein.py                   # Henry Schein XLSX parsing
  payroll_parser.py                # Phoenix/Greenpage CyberPayroll report parser
  plaid_client.py                  # Plaid API client (link, sync, liabilities)
  reporting.py                     # Query helpers for Reports page + centralized exclusion lists
  coverage.py                      # Test coverage utilities
scripts/
  seed_demo_data.py                # Seed fake data for demo instance (2 entities)
run.py                             # Entry point: python run.py (dev mode)
fly.demo.toml                      # Fly.io config for demo instance (no auth, 2 entities)
requirements.txt                   # flask, gunicorn, pandas, pdfplumber, plaid-python, etc.
```

## HTMX Interactions
- **Dashboard filters:** Filter form uses `hx-get` to `/dashboard/partial`, swaps `#dashboard-body` with `hx-push-url="true"`. Loading state via JS event listeners (not `hx-indicator`).
- **Card queue (Categorize Vendors):** Save/Skip buttons use `hx-post` + `hx-target` to swap just the card div
- **Match review:** Accept/Skip swap the match card via HTMX partial
- **Category dropdowns:** `hx-get` to fetch subcategories when category changes
- **File uploads:** Standard form POST, returns full page with results
- **Reports chart:** Pure CSS bar chart (no JavaScript charting library)

## Session & Temp Files
Flask's cookie-based session has a 4KB limit. Parsed data from file uploads and match results is stored in temp files on disk (`/tmp/expense-tracker-uploads/`), with only a small key stored in the session or passed as a hidden form field.

Pattern used across routes:
- `_save_temp(key, data)` -- writes JSON to `/tmp/expense-tracker-uploads/{key}.json`
- `_load_temp(key)` -- reads + deletes the temp file
- `_TEMP_DIR` created on module import

## Pages
- **Dashboard** -- KPI compare panels, categories chart, income vs expenses chart, insights + upcoming recurring, on-demand AI analysis
- **To Do** -- Review queues (uncategorized, vendor breakdown, transfers, large txns, new merchants, orders) + Workflow links
- **Transactions** -- Filterable transaction list with inline editing, saved views, AI category suggestion
- **Subscriptions** -- Subscription watchlist with auto-detection, tracking timeline, AI cancellation tips, account info
- **Cash Flow** -- Per-account balances, upcoming recurring charges, Plaid liabilities
- **Planning** -- Long-term net worth projections (assets + liabilities at milestone ages, inflation-adjusted)
- **Payroll** -- Employee roster, Phoenix/CyberPayroll import, role-based spending (BFM only)
- **Weekly** -- Weekly check-in: KPI band (spent/pace/remaining), credit card paydown tracker with per-card utilization bars and target-date pace indicator, this week's bills (from 5 data sources), last week scorecard (top categories, burn rate, warnings). ISO week navigation (Mon–Sun). Hidden for LL entity.
- **Waterfall** -- BFM surplus to personal debt paydown. Two tabs: **Actual** (monthly actuals: revenue → fixed costs → operating costs → surplus) and **Target** (budget-based scenario modeling). Target has two-mode toggle: **Revenue Target** (set revenue, see resulting take-home) or **Desired Take-Home** (set after-tax take-home, back-calculates gross at 22% tax and required revenue). Hover tooltips on bars show per-category breakdown (actuals show spending, target shows budgets). Personal CC debt with utilization bars and payoff estimate. Other liabilities (mortgages/loans). 6-month surplus trend chart. Cross-entity (always queries BFM + Personal). Hidden for LL entity.
- **Reports** -- Monthly detail + spending trend (pure CSS bar chart)
- **Connected Accounts** -- Plaid Link, sync, disconnect
- **Kristine's Dashboard** (`/k/`) -- Public (no auth), mobile-first page for Kristine. Shows Personal Focus budget status (categories, subcategories, transaction drill-down), Luxe Legacy business summary, account balances (BOA Primary, LL, Apple Card), and praise/gamification. Light blue and pink theme. Standalone template (no sidebar/base.html).

### 5-Step Workflow (linked from To Do page)
1. **Upload from Bank/CC** -- Import CSV/PDF bank statements
2. **Upload from Vendors** -- Upload Amazon/Henry Schein order data
3. **Match** -- Link vendor orders to bank transactions
4. **Categorize Vendors** -- Label each vendor order with category/subcategory
5. **Categorize Remaining** -- Review + categorize remaining bank transactions

Workflow pages removed from sidebar in PR #23 redesign; now accessible via To Do page Workflows section.

## Database (56 Migrations)
Key tables:
- **`transactions`** -- Main ledger. PK = SHA-256(date, amount, description)[:24]. Negative amount = debit.
- **`categories`** -- Per-entity categories. Personal: 35 categories. BFM: 32 categories. Every category has a "General" subcategory.
- **`subcategories`** -- Two-level categorization (Migration 15). Each subcategory belongs to a parent category. No "Unknown" subcategories — unknowns go to "Needs Review" category.
- **`merchant_aliases`** -- Pattern-based auto-categorization (contains/regex -> merchant + category)
- **`import_profiles`** -- Saved CSV column mappings per bank (Amex, Chase, Capital One, Citi, BofA)
- **`import_checklist` / `import_checklist_status`** -- Monthly source tracking
- **`amazon_orders`** -- Vendor orders for deferred matching. `matched_transaction_id` tracks matches. Has `category`/`subcategory` (Migration 16) and `vendor` (Migration 17, default `'amazon'`). Stores both Amazon and Henry Schein orders.
- **`account_balances`** -- Cash Flow account tracking (Migration 26+27). Fields: account_name, balance_cents, balance_source (manual/plaid), account_type (bank/credit_card), credit_limit_cents, payment_due_day, payment_due_date, payment_amount_cents, sort_order, plaid_account_id.
- **`manual_recurring`** -- Manually-added recurring charges per account (Migration 28). Fields: account_id (FK → account_balances), merchant, amount_cents, day_of_month (1–31), created_at. Merged with auto-detected recurring on Cash Flow page.
- **`subscriptions`** -- Subscription watchlist (Migration 32). Fields: merchant, amount_cents, cadence, status (active/cancelled/paused), category, notes, linked_account_name, first_seen, last_charged, created_at. Tracks recurring subscriptions with cost tracking and AI cancellation tips.
- **`subscription_dismissals`** -- Dismissed subscription suggestions (Migration 33). Fields: merchant_canonical (UNIQUE), dismissed_at. Prevents re-suggesting dismissed subscriptions.
- **`subscription_tracking`** -- Subscription timeline tracking (Migration 34). Fields: subscription_id (FK), event_type (created/price_change/cancelled/resumed/note), old_value, new_value, notes, created_at.
- **`subscription_account_info`** -- Subscription account details (Migration 37). Fields: subscription_id (FK UNIQUE), account_email, account_phone, phone_a_friend_name, phone_a_friend_number, notes.
- **`planning_settings`** -- Planning page settings (Migration 35). Fields: inflation_rate (bps), current_age, custom_milestone, birth_date (Migration 38). Singleton row (id=1), stored in personal.sqlite.
- **`planning_items`** -- Planning assets/liabilities (Migration 36). Fields: item_type (asset/liability), name, current_value_cents, annual_rate_bps, monthly_contrib_cents, monthly_payment_cents, source (manual/cashflow), cashflow_account_name, sort_order.
- **`budget_items`** -- Monthly budget targets per category (Migration 48). Fields: category (UNIQUE), monthly_budget_cents, budget_section (fixed/focus/other), is_per_payroll (Migration 50), per_payroll_cents (Migration 50). Section groups categories into Fixed (housing, ranch, insurance, retirement, student loans), Focus (discretionary to optimize), and Everything Else. Per-payroll categories (Payroll, Taxes) store per-payroll amount and dynamically multiply by pay periods per month.
- **`employees`** -- Employee roster (Migration 51). Fields: name, role (free-text), phoenix_job_code, pay_type (hourly/salary), pay_rate_cents, hire_date, status (active/inactive/terminated), notes. BFM only.
- **`employee_pay_changes`** -- Pay rate change history (Migration 51). Fields: employee_id (FK CASCADE), effective_date, old_rate_cents, new_rate_cents, change_type, notes.
- **`payroll_entries`** -- Per-employee paycheck data from Phoenix import (Migration 51). Fields: employee_id (FK CASCADE), paycheck_date, amount_cents (total employer cost = Gross + ER Tax + Benefits), source_filename. UNIQUE(employee_id, paycheck_date).
- **`budget_subcategories`** -- Optional subcategory-level budget targets (Migration 49). Fields: category, subcategory, monthly_budget_cents, created_at. UNIQUE(category, subcategory). Separate from budget_items. When set, subcategory rows show remaining amount and progress bar.
- **`payroll_schedule`** -- Biweekly payroll cadence (Migration 50). Singleton table (CHECK id=1). Fields: anchor_date (known payday YYYY-MM-DD), cadence_days (14), pay_dow (day-of-week payment hits bank, 0=Mon, 2=Wed). Used by `_count_pay_periods()` to compute how many paydays fall in a given month (typically 2, sometimes 3). Only BFM uses this; Personal/LL have no row.
- **`order_line_items`** -- Individual products within multi-item vendor orders (Migration 53). Fields: amazon_order_id (FK → amazon_orders), item_description, qty, unit_price_cents, category, subcategory, line_number. Breaks down aggregate orders into per-item categorization.
- **`transaction_splits`** -- Split a single bank transaction across multiple budget categories (Migration 54). Fields: transaction_id (FK → transactions), description, amount_cents, category, subcategory, sort_order, source (manual/vendor_line_item), line_item_id (FK → order_line_items), created_at. When splits exist, `effective_txns_cte()` replaces parent with split pieces in all reporting queries.
- **`cc_paydown_goal`** -- Credit card paydown target date goal (Migration 56). Singleton per entity (CHECK id=1). Fields: target_date, start_date, start_balance_cents, created_at. Used by Weekly page to compute linear pace toward $0 balance.

## Vendor Workflow (Three-Phase)

**Phase 1 -- Upload (Vendors page):**
Select vendor from dropdown (Amazon or Henry Schein) -> upload file -> preview order count/date range/total -> filter by date range -> save to `amazon_orders` table with `vendor` tag.

**Phase 2 -- Match (Match page):**
Run matching algorithm to link vendor orders to bank transactions. Exact matches auto-applied. Uncertain matches shown in card review queue (Accept/Skip). Cards show amount diff and date gap with red highlighting when values are outside tolerance.

**Phase 3 -- Categorize (Categorize Vendors page):**
Card queue shows uncategorized orders across all vendors. Product name, date, amount displayed; pick category + subcategory. Uses `infer_category()` for smart defaults.

### Amazon CSV Formats
Two formats: **Business** (groups by `payment_ref_id`) and **Privacy Central** (groups by `order_id`).

### Henry Schein XLSX Format
"Items Purchased" export. Groups by Invoice No (one invoice = one bank charge). Key columns: Short Description, Invoice No, Invoice Date, Amount, Category/Sub Category1, Manufacturer.

### Matching Algorithm (Amazon only for now)
1. **Exact** (amount within 8% + date within 5 days) -> auto-applied, confidence 0.95
2. **Likely** (amount within 8% + date within 10 days) -> shown for review, confidence 0.80
3. **Multi-order** (Business format only -- 2-3 orders summing to txn) -> confidence 0.75
4. **Date-only fallback** -> confidence 0.50

Match review cards show:
- Amount diff with red highlighting when >3%
- Date gap (days between bank charge and order date) with red when >5 days or negative

Subscription charges (Audible, Kindle Unlimited, Amazon Music, etc.) excluded via `_AMAZON_EXCLUDE_PATTERNS`.

## Categorization
1. **Alias rules** (confidence 0.95) -- `merchant_aliases` table
2. **Keyword heuristics** (confidence 0.5-0.8) -- fallback for common merchants
3. **Subcategories** -- Two-level system. `infer_category()` returns `(category, subcategory)` tuple.
4. **Exclusion lists** -- Centralized in `core/reporting.py`: `EXCLUDE_CATS` (Internal Transfer, Credit Card Payment, Income, Owner Contribution, Partner Buyout) and `EXCLUDE_CATS_NO_INCOME` (same minus Income). `exclude_sql()` helper generates SQL NOT IN clause. Imported by `dashboard.py`, `short_term_planning.py`, `kristine.py`.

## Important Patterns
- `DATA_DIR` env var controls where DBs and uploads go (default: `./local_state`)
- Transaction IDs are deterministic -- reimporting the same CSV won't create duplicates
- Entity stored in cookie (survives page refreshes, no WebSocket dependency)
- Dual theme (dark default + light) via `data-theme` attribute on `<html>`, persisted in `localStorage`. Toggle in sidebar. Inline `<script>` in `<head>` prevents flash of wrong theme.
- CSS custom properties for all colors/shadows/borders — ~30 variables per theme in `:root[data-theme="dark"]` and `:root[data-theme="light"]`
- Light-theme scoped overrides (`:root[data-theme="light"] .selector`) for dashboard-specific polish (charts, chips, filter bar, KPI cards)
- Mobile responsive: hamburger menu at ≤768px, sidebar slides in/out with scrim overlay
- Accessibility: skip-to-content link, ARIA labels on sidebar nav, focus-visible rings on all interactive elements
- Open redirect prevention on `/set-entity` — only relative paths allowed

## Reports Page Architecture
Two independent sections, no JavaScript charting library (pure CSS bars).

**Top Section — Monthly Detail:**
- Month navigator: ‹ February › (prev/next arrows, full month name)
- Stat cards: Spending | Income | Net (for selected month)
- Category breakdown: colored dots, horizontal fill bars, drill-down chevrons
- Drill-down: transaction list when category clicked, CSV export

**Bottom Section — Spending Trend:**
- Period toggle: segmented control [ 3M | 6M | 1Y | 2Y ]
- Pure CSS bar chart: variable bar count (3/6/12/24), always ends at most recent month
- Selected month's bar highlighted (brighter gradient + blue label)

**URL params:** `?month=YYYY-MM` (default: latest), `?period=6` (3/6/12/24), `?drill=CategoryName`

**Date formatting (never show YYYY-MM anywhere):**
- `fmt_month_full()`: "February" (current year) or "February 2025"
- `fmt_month_short()`: "Feb" (current year) or "Feb 25"
- `fmt_date()`: "Feb 15" (current year) or "Feb 15, 2025"
- All defined in `web/routes/reports.py`, passed to template as callables

**Chart scaling by period:**
- 3M: wide bars (20% track padding, 16px gap)
- 6M: default (12% padding, 6px gap)
- 12M: narrow (8% padding, 3px gap, smaller labels)
- 24M: very narrow (4% padding, 2px gap, value labels hidden)
- Mobile: 12M+ hides value labels, 24M alternates x-axis labels

**Query functions used (all in `core/reporting.py`):**
- `get_available_months(entity)` — month list for navigation bounds
- `get_monthly_totals(entity, start, end)` — bar chart data
- `get_category_totals(entity, month)` — category breakdown
- `get_income_total(entity, month)` — income stat card
- `get_transactions(entity, month, category)` — drill-down list

## Delete Amazon Data (for re-import)
```python
# Run via SSH on Atlas
ssh Atlas@192.168.3.10 "cd ~/expense-tracker && .venv/bin/python -c \"
import sqlite3
conn = sqlite3.connect('local_state/personal.sqlite')
c = conn.cursor()
c.execute('UPDATE transactions SET product_summary=NULL, description_override=NULL, matched_order_id=NULL WHERE matched_order_id IS NOT NULL AND matched_order_id IN (SELECT order_id FROM amazon_orders WHERE vendor=\\\"amazon\\\")')
c.execute('DELETE FROM amazon_orders WHERE vendor=\\\"amazon\\\"')
conn.commit()
print(f'Deleted {c.rowcount} orders')
conn.close()
\""
```

## Testing
```bash
python scripts/smoke_test.py  # No server needed
```

## Gitignored (never commit)
`local_state/`, `*.sqlite`, `uploads/`, `backups/`, `.venv/`, `statements/`

## Dependencies
flask, gunicorn, pandas, pdfplumber, python-dateutil, openpyxl, plaid-python, requests (for OpenRouter AI client)

> Note: `plotly` is still in requirements.txt but no longer used on the reports page (replaced by pure CSS bars). Can be removed once confirmed not used elsewhere.

## Dashboard Architecture

**KPI Strip:** Spend, Income, Net, Needs Review count, Latest Transaction date. Spend/Income are clickable drill links to `/transactions`.

**Sync Health:** Plaid connection status per institution (only shown when Plaid items exist).

**Expense Insights Card:** Up to 3 auto-generated expense insights computed by `_compute_insights()`:
- Category spend increase vs prior period (>$50, ≥2 txns)
- New merchants this period (not seen in prior 90 days)
- Large transactions over $500
Each insight links to a drill-down in `/transactions`. Compare view adds cross-period insights via `_compute_compare_insights()` (spending change, category shifts). Income insights separated out (see below).

**Income vs Expenses Insights:** Below the IE line chart. Computed by `_compute_income_insights()` via HTMX endpoint `GET /dashboard/ie-insights`. Shows income change between periods, top income source, and expense-to-income ratio (90–200% range only). Triggered by KPI panel scripts after load.

**Upcoming Recurring:** Detects recurring merchants via `_detect_recurring()` + `_build_upcoming()`:
- 90-day lookback, ≥2 occurrences per merchant
- Cadence classification: Weekly (5–9d), Monthly (25–35d), Annual (340–390d)
- Amount regularity: ≥2 of last 3 within max($3, 5% of median)
- Staleness filter: skips if last charge >2× cadence ago
- Up to 6 items within next 30 days, sorted soonest first
- Drill links include merchant + ±7 day window around expected date
- Respects account filter from dashboard params

**Cash Flow Chart:** 6-month spend trend bar chart (pure CSS, no charting library).

**Top Categories / Top Merchants:** Ranked lists with horizontal bar visualization and drill-down links.

**Review Inbox:** Uncategorized, Vendor Breakdown Needed, Possible Transfers counts with drill links.

**Vendor Orders:** Total/unmatched order count linking to Match page (shown only when orders exist).

**HTMX Partial Updates:** Filter form submits via `hx-get` to `/dashboard/partial`, swaps `#dashboard-body`. Loading state managed via `htmx:beforeRequest`/`htmx:afterRequest`/`htmx:responseError` event listeners that toggle `.dash-loading` class (opacity fade + pointer-events disabled).

**Saved Views:** Dashboard and transactions pages support saved filter presets via the saved views system. Row shows select + Save As + Update visible; Rename, Make Default, Clear Default, Delete in a "⋯" overflow menu (keyboard accessible, closes on outside click/Escape).

## AI Features
Four AI-powered features using Claude via OpenRouter (`core/ai_client.py`). Requires `OPENROUTER_API_KEY` env var.

- **Ask Opus** (global chat modal) — Available on every page via "Ask Opus" button. Uses `anthropic/claude-opus-4.6` via `web/routes/ai.py`. Each page sends page-specific financial context (planning data, spending trends, transaction patterns, subscription costs, account balances, etc.). Conversation persists per entity+page in `/tmp/expense-tracker-ai/`. System prompt adapts per page (financial advisor on Planning, spending analyst on Dashboard, etc.). Modal lives in `base.html`, JS function `aiChatOpen('pagename')` sets context. Button is a joker `?` image (`web/static/joker-button.png`, 66×66px) with purple glow (`drop-shadow`), hover scale+brightness effect. CSS classes: `.joker-btn`, `.joker-btn-img`.
- **AI Suggest** (transactions edit modal) — Uses `anthropic/claude-sonnet-4.6`. Sends merchant + amount, returns category/subcategory suggestion. Button labeled "AI Suggest", shows error feedback on failure.
- **AI Cancellation Tips** (subscriptions detail modal) — Uses `anthropic/claude-sonnet-4.6`. Generates step-by-step cancellation instructions for a subscription. On-demand button on watchlist items.
- **AI Analysis** (dashboard insights) — Uses `anthropic/claude-sonnet-4.6`. Gathers spending summary (categories, merchants, trends), returns 3-5 narrative insights. Cached in-memory 1 hour per entity+period. Button in Insights section with blue accent.

## Subscriptions Page Architecture
Subscription watchlist at `/subscriptions` for tracking recurring charges.

- **Auto-detection** — Identifies recurring merchants from transaction patterns. Suggestions shown with Accept/Dismiss. Dismissed tracked in `subscription_dismissals`.
- **Watchlist** — Active subscriptions with merchant, amount, cadence, category, status (active/cancelled/paused). Links to filtered transactions.
- **Detail modal** — Popup with tracking timeline (price changes, notes, status changes), account info (email, phone), "Phone a Friend" share button.
- **Tracking timeline** — `subscription_tracking` table logs events (created, price_change, cancelled, resumed, note). Displayed chronologically in modal.
- **Account info** — `subscription_account_info` table stores per-subscription email, phone, notes, Phone a Friend contact.
- **Interest/fee exclusion** — Subscription detection skips interest charges and bank fees.

## Planning Page Architecture
Long-term net worth projections at `/planning`. Settings stored in `personal.sqlite` (global singleton), items per entity.

- **Settings** — Inflation rate (bps), birth date (auto-computes age), custom milestone age. Click age to change birthday.
- **Assets** — Name, current value, annual appreciation rate (bps), monthly contribution. Projected forward with compound growth: `FV = V*(1+r)^n + C*((1+r)^n - 1)/r`.
- **Liabilities** — Name, current balance, annual interest rate (bps), monthly payment. Amortized forward: `Balance = B0*(1+r)^t - P*((1+r)^t - 1)/r`. Shows "Paid off" when balance reaches 0.
- **Milestones** — Default ages 60, 65, 70 + optional custom milestone. All projections inflation-adjusted to today's dollars.
- **Cross-entity visibility** — Personal ↔ BFM share view (each sees other's items). LL excluded. Combined net worth row across all visible entities.
- **Cashflow linking** — Items can pull live balance from `account_balances` (source="cashflow") instead of manual entry.
- **Add/Edit modal** — Shared modal for both add and edit. Borderless input fields (transparent bg, no border/outline/shadow/focus ring — editable text feel). Delete button appears in modal when editing (red outline, bottom-left). Separate `<form>` for delete to avoid nested form issues.
- **Input formatting** — Current value and monthly contribution/payment display with commas, no cents (`1,429,303`). Rate shows `%` suffix tight to value (`4.75 %`). JS strips commas from money fields on form submit before POST.
- **Summary band** — Header row (TODAY, @60, etc.) at 0.88rem matching net worth values. Assets/liabilities rows slightly smaller at 0.78rem. Faint divider lines (`rgba(255,255,255,0.06)`) below header row and below liabilities row to visually separate Net Worth.
- **Combined Net Worth** — Centered card (`max-width: 480px`), glass bg. Label at 0.82rem, item text at 0.72rem, values at 0.88rem.
- **Settings bar** — No Update button; inflation rate and custom milestone submit via Enter key.
- **HTMX** — Cashflow account dropdown populated via `GET /planning/cashflow-accounts/<entity_key>`.

## PWA (Progressive Web App)
- **Installable** — Meets all PWA installability requirements (manifest + service worker + HTTPS + icons).
- **Service worker** — `web/static/sw.js`, served from `/sw.js` (root scope). Registered in `base.html` on page load.
- **Caching strategy:**
  - Static assets (`/static/*`): cache-first, fall back to network
  - HTML navigation: network-first, fall back to cache, then offline page
  - Other requests (HTMX partials, API): network-first, fall back to cache
- **Pre-cached on install:** App shell (`/`), offline page, CSS, JS, all icons/logos, manifest (15 assets).
- **Cache versioning** — `CACHE_NAME = 'the-ledger-v2'`. Bump version when changing static assets to force SW update. Old caches auto-deleted on activate.
- **Offline fallback** — `/offline` route renders `offline.html` (standalone template, branded, retry button). Auth bypassed.
- **Manifest** — `web/static/manifest.json`: name, short_name, start_url, id, display=standalone, 3 icons (192 any, 512 any, 512 maskable).
- **Icons** — Gold "L" monogram on dark rounded-rect background. Clean at all dock/home-screen sizes. Wax seal artwork (`the-ledger-seal.png`) retained for in-app sidebar use only.
- **Mobile meta tags** — `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style` (black-translucent), `apple-mobile-web-app-title`, `mobile-web-app-capable`.
- **Auth bypass** — `/sw.js` and `/offline` routes bypass basic auth and entity setup in `web/__init__.py`.
- **Updating icons** — Replace PNGs in `web/static/`, bump `CACHE_NAME` version in `sw.js`, deploy. Users must remove and re-add the app to dock/home-screen to see new icon (OS caches icon at install time).

## Change Log

### 2026-03-24 — PWA: service worker, installability, offline fallback + monogram icons
Made the app a proper installable Progressive Web App with service worker caching and offline support. Replaced wax seal PWA icons with clean L monogram for better dock/home-screen appearance.

1. **Service worker (`web/static/sw.js`)** — Cache-first for static assets, network-first with offline fallback for navigation. Pre-caches 15 app shell assets on install. Served from `/sw.js` (root scope) via Flask route in `web/__init__.py`. `max_age=0` ensures browsers always check for SW updates.
2. **Offline fallback (`web/templates/offline.html`)** — Standalone branded page with theme support (dark/light via localStorage), plug icon, "You're Offline" message, and Retry button. No dependency on base.html or entity context.
3. **Manifest updates (`web/static/manifest.json`)** — Added `id`, `description`, `orientation` fields. Added maskable icon entry (512px). All required installability fields present.
4. **SW registration (`web/templates/base.html`)** — Registration script added before `</body>` with `'serviceWorker' in navigator` guard. Auto-detects and activates new SW versions via `updatefound` listener.
5. **Mobile meta tags** — Added `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style`, `apple-mobile-web-app-title`, `mobile-web-app-capable` to `base.html` `<head>`.
6. **Auth bypass** — `/sw.js` and `/offline` routes skip basic auth, entity setup, and context processor in `web/__init__.py`.
7. **Monogram icons** — Replaced wax seal PWA icons (busy/illegible at small sizes) with clean gold L monogram on dark rounded-rect background. Files: `icon-192x192.png`, `icon-512x512.png`, `icon-1024x1024.png`, `apple-touch-icon.png`. Header logo (`the-ledger-logo-lockup.png`) and sidebar seal (`the-ledger-seal.png`) unchanged.
8. **Cache version v2** — Bumped `CACHE_NAME` from `the-ledger-v1` to `the-ledger-v2` to force re-cache of new monogram icons.

### 2026-03-12 — Personal budget review + dashboard category bar redesign + Joker palette
Complete Personal budget review (30 categories), dashboard UX overhaul for category rows, and Joker-themed color palette.

1. **Personal budget review** — Reviewed all spending categories using Dec/Jan/Feb 3-month averages. Set budgets for 30 categories totaling ~$33,579/mo. New budgets created: Cleaning ($600 fixed), Laundry Service ($500 fixed), Self Storage ($200 fixed), Security ($122 fixed), Streaming ($140 fixed), Gifts ($200 other), Toys ($200 other), ATM Withdrawals ($100 other), Home Improvement ($100 other). Existing budgets adjusted: Abuelitos $533→$700, Childcare $513→$500, Shopping $901→$450, Entertainment $943→$230, Clothing $686→$350, Transportation $356→$250, LL Expense $232→$200, Health & Beauty $306→$200, Healthcare $306→$100, Insurance $1,533→$1,500, Pets $47→$50. Stale entries deleted: Electronics, Storage (no transactions).
2. **CCI → Care Credit identification** — Two CCI charges ($161 each) on BankAmericard identified as Care Credit dental payments for abuelitos. Recategorized to Abuelitos/Healthcare. Merchant alias created: pattern='CCI', pattern_type='contains', merchant_canonical='Care Credit', default_category='Abuelitos', default_subcategory='Healthcare'. Abuelitos budget bumped $600→$700 to accommodate.
3. **Production sync** — Comprehensive sync script replaced all 30 budget_items, added Care Credit alias, and updated 477 Dec–Mar transaction categories on production. All successful (477 updated, 0 not found).
4. **Dashboard category bar redesign** — Multiple iterations redesigning category rows. Final design: spent amount rendered inside the colored progress bar (white text with text-shadow, right-aligned via `position: absolute; right: 0.4rem`). Small bars (<15% width) get `dcat-fill--narrow` class that flips label to the right of the bar in normal text color. $0 categories hide the label entirely. Budget shown in fixed-width gray column (60px) at far right. Chevrons hidden (`display: none`) to give bars more room. Category name column narrowed from 150px to 120px.
5. **Joker color palette** — Bar colors changed to dark, rich tones for better white text contrast: emerald green (`#1a7a4a→#145e39`) for under-budget, dark gold (`#b8860b→#8b6508`) for warning, deep berry/crimson (`#8b1a4a→#6b1038`) for over-budget, deep purple (`#4b2d8e→#3a1f75`) for no-budget default.

### 2026-03-11 — Waterfall Target: two-mode toggle, hover tooltips, take-home mode + BFM recalibration
Major Waterfall Target tab improvements: two-mode scenario modeling, per-category hover tooltips, and Desired Take-Home mode. Plus BFM budget recalibration and production sync.

1. **Two-mode scenario toggle** — Target tab now has segmented control: **Revenue Target** (set revenue, see resulting take-home) or **Desired Take-Home** (set after-tax take-home, back-calculates gross and required revenue). Single input field + summary line adapts per mode. JS `wfSetMode()` toggles active state and clears input.
2. **Desired Take-Home mode** — Enter desired after-tax take-home pay. Back-calculates gross salary: `gross = take_home / (1 - tax_rate)`. Then `required_revenue = gross + bfm_costs`. Summary shows "Gross $X → Revenue needed $Y". URL param: `?mode=takehome&take_home=40000`.
3. **Hover tooltips on waterfall bars** — Hovering Fixed Costs, Operating, BFM Fixed, BFM Operating, Personal Fixed, or Personal Variable shows per-category breakdown. Target view shows budget amounts; Actual view shows actual spending. Smart positioning flips tooltip above the row when near viewport bottom. `data-tip` JSON attributes parsed by JS on mouseenter. Light mode supported.
4. **Owner salary defaults to BFM surplus** — Revenue mode: `owner_gross = max(target_bfm_surplus, 0)`.
5. **Effective tax rate 26.5% → 22%** — `_EFFECTIVE_TAX_RATE_BPS` updated from 2650 to 2200.
6. **Deficit display fix** — Remaining row in personal waterfall now shows minus sign for deficits (e.g., "−$2,691" in red). Previously showed unsigned amount which was confusing.
7. **BFM budget recalibration** — Rebuilt all 27 BFM budget items using Dec 2025–Feb 2026 3-month spending averages. Key changes: Payroll $24,500/payroll (was $25,773), Insurance $4,700 (was $6,000), Office Supplies $650 (was $1,550), new Accounting $700, new Storage $470. Total: $127,949/mo.
8. **BFM category cleanup** — Added missing Accounting category. Fixed 34 Rent and 12 IT transactions with NULL subcategories → General. Merged IT Services ($3,000) + IT ($400) budgets → IT $3,400. Removed duplicate aliases (Chansen Media, providential).
9. **Production database full sync** — Synced all BFM category changes to production via transaction_id matching. 193 transactions recategorized (Insurance 83, Taxes 39, Rent 34, Medical Billing 15, Accounting 13, etc.). Budget items and merchant aliases fully replaced. Remaining 4-transaction gap (Income/Fees) confirmed as newer Plaid transactions on production only.

### 2026-03-10 — Waterfall page: BFM surplus to personal debt paydown
New `/waterfall` page showing monthly business cash flow waterfall and personal debt targets.

1. **Waterfall route (`web/routes/waterfall.py`)** — New blueprint at `/waterfall`. Cross-entity page that always queries both `company.sqlite` (BFM income/expenses) and `personal.sqlite` (CC balances, mortgages). Month navigation via `?month=YYYY-MM`. LL entity redirects to dashboard.
2. **KPI band** — Three cells: BFM Revenue, Total Expenses, Surplus (green when positive, red when negative).
3. **Business Waterfall breakdown** — Stacked flow rows: Gross Revenue → Fixed Costs (collapsible, shows Payroll, Facilities, EIDL Loan, etc.) → Operating Costs (collapsible, shows IT, Medical Supplies, Software, etc.) → divider → Available for Personal. Expense grouping from `_get_budget_status()` budget_section field (fixed vs focus/other/none).
4. **Personal CC Debt section** — Reuses `.wk-cc-*` CSS classes from Weekly page. Per-card utilization bars, total debt, payoff estimate ("At $X/mo surplus → CCs paid off in N months"), and pace indicator from existing `cc_paydown_goal`.
5. **Other Liabilities** — Personal mortgages/loans from `planning_items` table with balance, rate, and monthly payment.
6. **Surplus Trend chart** — Last 6 months of BFM surplus as pure CSS bar chart (reuses `.chart-*` classes from Reports). Selected month highlighted. Negative surplus months shown in red bars.
7. **Data reuse** — No new database tables. Imports: `_get_budget_status()` from STP, `_get_cc_balances()`/`_get_paydown_goal()`/`_compute_paydown_pace()` from weekly.py, `_get_items()` from planning.py, `get_available_months()`/`effective_txns_cte()`/`exclude_sql()` from reporting.py.
8. **CSS** — ~170 lines of `.wf-*` styles (nav, KPI band, flow rows, chevron toggle, detail rows, divider, payoff estimate, liability rows, trend chart overrides). Light mode overrides. Responsive at 600px.
9. **Sidebar link** — "Waterfall" between Weekly and Cash Flow, gated for non-LL entities.

### 2026-03-10 — Weekly Check-In page + CC Paydown tracker (Migration 56)
New `/weekly` page with ISO week navigation, spending pace tracking, credit card paydown goals, and bill aggregation from 5 data sources.

1. **Weekly page (`web/routes/weekly.py`)** — New blueprint at `/weekly`. ISO week navigation (Mon–Sun boundaries) with prev/next arrows. KPI band shows Spent This Week, Weekly Pace (monthly budget × 7 / days_in_month), and Remaining (green when on pace, red when over). Hidden for LL entity (redirects to dashboard).
2. **This Week's Bills** — Aggregates bills from 5 sources: action items (manual-pay due dates), auto-detected recurring merchants, manual recurring charges, credit card payment due dates, and BFM payroll schedule. Filters to current week's Mon–Sun window. Shows merchant, amount, day of week, and source tag. Bills vary correctly across weeks based on actual due dates.
3. **Last Week Scorecard** — Previous week's spending total, burn rate vs monthly budget (over/under with color), top 5 categories with pace bars (green ≤100%, orange 100–115%, red >115%), and up to 3 warnings (categories >115% of weekly pace).
4. **Credit Card Paydown (Migration 56)** — New `cc_paydown_goal` singleton table per entity (target_date, start_date, start_balance_cents). Per-card utilization bars (green <50%, orange 50–80%, red >80%) with balance and limit. Total CC Debt row. Inline target date form saves goal via `POST /weekly/paydown-goal`. Progress bar with linear pace calculation: `expected = start_balance × (1 - days_elapsed / total_days)`. Shows "On pace" (green) or "Behind" (red) with percentage complete and days remaining. Preserves start_date/start_balance on target date updates, snapshots current total on first set.
5. **Week navigation** — ISO week format (`2026-W11`). URL param `?w=2026-W11`. Prev/next arrows. Current week shows "This Week (Mar 9–15)", other weeks show "Week of Mar 2–8". `_week_bounds()` computes Monday–Sunday from ISO week string.
6. **Blueprint registration** — `weekly_bp` registered in `web/__init__.py`. Sidebar link between "To Do" and "Cash Flow", gated for non-LL entities (`entity_key != 'luxelegacy'`).
7. **CSS** — ~360 lines of `.wk-*` styles: nav strip, KPI band, bills table, category bars, warnings, CC paydown section (`.wk-cc-*` for rows, utilization bars, pace indicator, progress bar, target form). Responsive at 600px breakpoint.

### 2026-03-10 — Category audit + centralized exclusions + Migration 55 + data fixes
Comprehensive category audit after Personal expanded to 35 categories and BFM to 32. Centralized exclusion lists, fixed stale references, and resolved two production data issues.

1. **Centralized exclusion lists** — `core/reporting.py` now exports `EXCLUDE_CATS`, `EXCLUDE_CATS_NO_INCOME`, and `exclude_sql()` helper. `dashboard.py`, `short_term_planning.py`, and `kristine.py` import from reporting instead of maintaining their own copies. Backward-compat aliases kept for internal use.
2. **Fixed kristine.py "Owner Draw" bug** — 4 inline SQL strings referenced stale `'Owner Draw'` category (renamed to `'Owner Contribution'` months ago). Fixed all occurrences in `_get_personal_summary()`.
3. **Updated keyword rules** — `core/categorize.py` `_KEYWORD_RULES` updated for current categories: `Household/Cleaning` → `Cleaning/Cleaning Service`, `Home` split into `Home Improvement` + `Home Services`, `Housing` → `Mortgage` + `Facilities`, `Supplies` → `Office Supplies`, `Storage` → `Self Storage`, `HR` separated from `Payroll`.
4. **Updated default categories** — `core/db.py` `_DEFAULT_CATEGORIES` and `_DEFAULT_SUBCATEGORIES` fully rebuilt to match current 35 Personal + 32 BFM categories. Removed stale: Housing, Household, Travel, Transfers, Fitness, Office Maintenance, Supplies.
5. **Migration 55** — Fixes stale alias/budget categories on existing databases: `Transfers` → `Credit Card Payment`, `Subscriptions` → `Entertainment`, `Dining`/`Groceries` → `Food`, `Housing` → `Mortgage` in budget_items. Also fixed M12 and M48 in-place for new databases.
6. **BFM budget_items populated** — Production had 0 budget_items. Computed 3-month spending averages (Dec 2025–Feb 2026) and inserted 23 validated budget items: Fixed ($128k/mo total), Focus (Medical Supplies, Office Supplies, Food, Software, Marketing, IT), Other (Fees, Electronics, HR, etc.). Payroll marked per-payroll ($40,500/payroll). payroll_schedule inserted (anchor 2026-02-25, biweekly, Wednesday).
7. **Personal amazon_orders orphans fixed** — 445 of 529 orders had `matched_transaction_id` pointing to non-existent transactions (IDs same format but no match). Cleared all orphaned matches so orders can be re-matched via Match page. 714 line items preserved (linked to orders, not transactions).
8. **Transaction edit modal: order items** — Read-only "Order Items" section added to transaction edit modal showing matched vendor order line items (product name, quantity, amount, category/subcategory). Falls back to `product_summary` when no line items exist.

### 2026-03-10 — Dashboard/STP alignment: all categories visible + budget progress on dashboard + Heath Easter egg
Dashboard now uses STP as single source of truth. Both pages show identical category/subcategory lists. Budget progress indicators added to dashboard. Heath Joker Easter egg on sidebar icon.

1. **Dashboard uses STP as source of truth** — `detail_categories()` calls `_get_budget_status()` from `short_term_planning.py` directly instead of independently querying budget_items and transactions. Deleted `_get_budget_map()` (40 lines of duplicate logic). Dashboard is read-only scoreboard; STP is the editing cockpit.
2. **All categories visible on both pages** — `_get_budget_status()` rewritten to return ALL categories from the `categories` table, not just budgeted ones. Unbudgeted categories get `budget_cents=0` and `budget_section=None`. New "NO BUDGET" section on STP for categories without budgets.
3. **All subcategories visible on STP** — `budget_subcategories()` endpoint rewritten to query ALL defined subcategories from the `subcategories` table (even at $0 spending), matching the dashboard's `_query_subcategory_rollups()` approach.
4. **Budget-colored bars on dashboard** — Category spending bars color-coded by budget health: green (≤100%), orange (100–115%), red (>115%). Categories without budgets show no bar. Thresholds aligned with STP (both use 115% for red).
5. **Uncategorized row on dashboard** — Bottom row showing uncategorized spending total (Needs Review + null/empty category) with drill-through link to transactions.
6. **Removed unbudgeted section from STP** — Old collapsible "UNBUDGETED SPENDING" section removed; unbudgeted categories now appear in the main budget table under "NO BUDGET" section with empty budget input placeholder.
7. **Plaid duplicate cleanup** — Removed 4 duplicate transactions from March Plaid sync: Barco Well Service ($5,400.63), DFW Security ($122.44), Venmo ($120), Adobe ($21.64). All were same-amount/same-description charges 1 day apart with different Plaid IDs. Prior months clean.
8. **Barco Well Service recategorized** — Moved from Ranch/General to Home/Plumbing (matching prior Barco transactions).
9. **Heath Easter egg** — Clicking the sidebar icon triggers a 3D card flip animation revealing a watercolor Joker painting (Heath) on the back. Uses CSS `perspective`, `transform-style: preserve-3d`, `rotateY(180deg)`, and `backface-visibility: hidden`. Click again to flip back. Source image background removed with `rembg` AI library for transparent PNG (`web/static/heath-standing.png`). Sidebar icon centered between top edge and first divider with equal padding (`1.6rem`). Heath offset `top: -20px` so full head is visible when flipped. Fits the app's playing card/Joker theme.
10. **Card flip + genie animation on Cash Flow, Planning, and STP goals** — Clicking any playing card triggers a 3D flip revealing the suit back (♦ green for bank/asset/savings, ♠ purple for credit/liability/debt), then the modal genie-stretches from the card's exact screen position to center (like macOS dock genie effect). Closing reverses the genie back to the card, then flips it back. Shared `.card-flip-inner`/`.card-flip-front`/`.card-flip-back` CSS structure across all three pages. `modalGenieIn`/`modalGenieOut` keyframes use `translate3d` with `--genie-x`/`--genie-y` CSS custom properties set dynamically by JS from `getBoundingClientRect()`. Performance optimizations: `will-change: transform, opacity` on modals, `backdrop-filter: blur` reduced from 8px to 4px, scrim appears instantly (no fade — blur recomputation was main stutter cause), card flip shortened from 0.5s to 0.3s, flip-to-modal delay 250ms, close animation 300ms. Applied to: Cash Flow (`cfFlipAndOpen`), Long-Term Planning (`plFlipAndOpen`), Short-Term Planning goals (`stpFlipAndOpen`).

### 2026-03-09 — Split transactions + LL Venmo dedup + Spend Trend chart restored
Transaction splitting for multi-category bank charges, Luxe Legacy data import with Venmo deduplication, Plaid sync across all entities, and restored missing dashboard bar chart.

1. **Split transactions (Migration 54)** — New `transaction_splits` table enables splitting a single bank transaction across multiple budget categories. `effective_txns_cte()` CTE in `core/reporting.py` transparently replaces parent transactions with split pieces in all reporting queries. Updated 16+ query functions across `reporting.py`, `dashboard.py`, `kristine.py`, `short_term_planning.py`, and `transactions.py`. New endpoints: `GET/POST/DELETE /transactions/splits/<txn_id>` for split CRUD, `POST /transactions/splits/<txn_id>/auto` to auto-generate from vendor line items. Split editor modal with balance validation, running total, and "Auto-split from Line Items" button. Split badge on transaction rows. `auto_split_from_line_items()` in `core/amazon.py` generates splits from `order_line_items`.
2. **LL Venmo deduplication** — Imported 231 LL transactions from production. Identified that every Venmo sale creates 3 transactions (Venmo IN from customer, Venmo transfer OUT to bank, BOA deposit IN from Venmo). Recategorized 51 duplicate transfers to Internal Transfer (27 Venmo Standard/Instant Transfers + 24 BOA Venmo deposits). 11 BOA bank-to-bank transfers also recategorized. LL income corrected from $25k → $15.5k. Cesar Mauro ($275 house cleaning) moved to Owner Draw/Personal.
3. **Plaid sync + data pull** — Synced all 3 entities via production Plaid. BFM +5 new transactions (Kroger, Adobe, Starbucks, Zapier, Uber Eats — all auto-categorized via aliases). Personal +15, LL +0. All corrections pushed to production.
4. **Spend Trend bar chart restored** — Dashboard bar chart was accidentally removed: template section in `dashboard_body.html` deleted in commit f3450f6 (Activity band removal), CSS deleted in commit 0f31fd3 (dead CSS cleanup). Restored both template HTML and ~90 lines of chart CSS.

### 2026-03-09 — Joker button for Ask Opus + vendor order categorization
Replaced "Ask Opus" text buttons with joker `?` image button across all pages. Bulk-categorized all vendor orders and added line item breakdown.

1. **Joker button** — Replaced navy "Ask Opus" text button with joker `?` image button (`web/static/joker-button.png`) on all 7 pages: Dashboard, Cash Flow, Transactions, Reports, Subscriptions, Short-Term Planning, Long-Term Planning. 66×66px with subtle purple glow (`drop-shadow`), hover scale (1.12×) + brightness, active press (0.95×). CSS classes `.joker-btn` + `.joker-btn-img` in `style.css`.
2. **Vendor order bulk categorization** — `scripts/categorize_vendor_orders.py` categorized all 745 Amazon/Henry Schein orders (529 Personal, 210 BFM Amazon, 6 BFM Henry Schein) using keyword-based rules with entity-specific category mappings. 100% categorized.
3. **Order line items (Migration 53)** — New `order_line_items` table breaks multi-item orders into individual products with per-item categorization. 382 line items populated for BFM (324 Amazon + 58 Henry Schein) via `scripts/populate_line_items.py`.
4. **Production sync** — All vendor order data (745 amazon_orders + 382 line items) pushed to production via SQL INSERT exports.

### 2026-03-08 — Rebrand to "The Ledger" + Joker theme + playing card UI
Major visual overhaul with Joker/playing card motif across the app.

1. **Rebrand** — "Ledger AI" → "The Ledger" across all page titles, sidebar wordmark, and references. New watercolor Joker icon replaces old icon.
2. **Color overhaul** — Dashboard primary accent changed from blue to royal purple (`--series-left: #7C3AED`). Compare bars changed to sea green (`--series-right: #2e8b57`). Income accent changed to sea green. AI Analysis boxes styled purple.
3. **Playing card Cash Flow** — Account cards use 5:7 aspect ratio with suit pips (♠ spade for bank accounts in green, ♦ diamond for credit cards in purple). Fixed 105px grid columns. Names at ~25% from top, balances dead center. Two-line names: "Apple Card" + "Ryan"/"Kristine", "First Horizon" + "Mortgage". All detail (credit limit, APR, payment due, upcoming charges) moved to popup modal only.
4. **Playing card Planning** — Long-Term Planning items use same card treatment. Assets get green spade pips, liabilities get purple diamond pips.
5. **Sidebar** — Active indicator changed from blue to purple (`--series-left`).
6. **Cash Flow sync fix** — `_sync_plaid_accounts()` was deleting all manually-added accounts (`plaid_account_id IS NULL`). Fixed to preserve manual accounts like Prosperity Bank.
7. **BFM Prosperity Bank** — Added to Cash Flow as manual bank account ($79,641). 881 transactions intact from PDF imports.

### 2026-03-08 — Kristine's Dashboard: mobile-first public page with praise engine
New `/k/` page for Kristine — a password-free, mobile-optimized dashboard showing Personal Focus budget and Luxe Legacy business data.

1. **Route (`web/routes/kristine.py`)** — Blueprint at `/k` with auth bypass. Queries both `personal.sqlite` (Focus budget categories from `budget_items WHERE budget_section = 'focus'`) and `luxelegacy.sqlite` (LL income, expenses, transactions). Standalone template (no `base.html`).
2. **Auth bypass (`web/__init__.py`)** — `_basic_auth()`, `_setup_entity()`, and `_inject_globals()` all skip for `/k` paths. Kristine's page manages its own DB connections directly.
3. **Focus budget section** — Per-category rows with budget vs spent, progress bars, subcategory breakdown (shown when >1 subcategory). Tappable categories expand to show individual transactions with JS toggle (`kdToggle()`). Categories sorted by spending descending.
4. **Account balances** — Three-card grid showing BOA Primary (checking), Luxe Legacy (LL business checking), and Apple Card (credit card with utilization bar). Queries `account_balances` from both personal and LL databases.
5. **Praise engine (`_compute_praise()`)** — Dynamic motivational messages based on budget performance. Analyzes: zero-spend categories, under-30% categories, month-over-month improvement, overall budget percentage. Generates headline + up to 3 "wins" with star bullets. Always finds something positive even when budget is tight.
6. **Month navigation** — Prev/next arrows with `?m=YYYY-MM` query parameter. Right arrow disabled for current month. `_month_offset()` handles year rollover.
7. **Luxe Legacy section** — Revenue/Expenses/Profit KPIs, category spending breakdown, recent 15 transactions. Shows "No transactions yet" empty state when LL has no data.
8. **Light blue and pink theme** — Custom `.kd-*` CSS classes (not using app's dark theme). Background: blue-to-pink gradient (`#e8f4fd` → `#fce4ec`). Progress bars: blue gradient. Section labels/chevrons: pink (`#ec407a`). Praise banner: blue→lavender→pink gradient with purple headline and pink stars. All text in harmonized blue-gray tones. Credit card utilization bar in bright pink (not red).
9. **Mobile-first** — `max-width: 480px`, touch-friendly tap targets, `apple-mobile-web-app-capable` meta tag, `viewport-fit=cover`. No JavaScript dependencies (vanilla JS only).

### 2026-03-08 — Payroll page: employee roster, Phoenix import, role-based spending
New `/payroll` page for BFM with employee roster management, Phoenix/CyberPayroll report import, and role-based spending analysis.

1. **Migration 51** — Three new tables: `employees` (roster with role, pay rate, hire date, status), `employee_pay_changes` (raise history), `payroll_entries` (per-employee paycheck data from Phoenix). Payroll subcategories seeded: Providers, Nurses, Scribes, Front Office, Office Manager, HR, Owner.
2. **Phoenix parser (`core/payroll_parser.py`)** — Parses "Per Payroll Costs" pivoted Excel export. Finds year-section headers ("Paycheck Dates"), extracts employee rows with amounts per date column. Amounts = Gross + ER Tax + Benefits (total employer cost). `PHOENIX_JOB_CODE_MAP` maps job codes to roles. `match_to_employees()` matches parsed entries to DB employees by name.
3. **Payroll route (`web/routes/payroll.py`)** — Blueprint at `/payroll` with CRUD for employees, Phoenix import (parse → preview → save), and role-based spending analysis. Detail modal shows compensation stats (days since raise, peer comparison), pay history timeline, recent paychecks, and edit form. Role badges with per-role colors.
4. **Payroll template (`web/templates/payroll.html`)** — Three sections: Team Roster (table with role badges, status, raise flags), Spending by Role (colored horizontal bars with month selector), Import Payroll (file upload with preview and role assignment for unmatched employees).
5. **Short-Term Planning integration** — `budget_subcategories()` special-cases Payroll category to query `payroll_entries JOIN employees GROUP BY role` instead of transactions. Falls back to standard query if no payroll data exists.
6. **Sidebar link** — "Payroll" appears in sidebar only for BFM entity (`entity_key == 'company'`).
7. **Initial data import** — Parsed Phoenix PerPayrollCosts.xlsx: 24 employees, 457 payroll entries across 2025-2026 ($1.14M in 2025, $184k YTD 2026). All employees matched and roles assigned.
8. **Employee roster** — 15 active, 9 terminated. Roles: Providers (Joseph Talley, Michelle Guilbeault), Nurses (Amber, Melissa, Heidi Maldonado), Scribes (Andrea Rodriguez Favela, Allison Ballard), Front Office (Kimberly, Desiree, Darlene, Cressie, Alexandria Aparicio), Office Manager (Sarah Gaiser), HR (Kristine Buffington), Owner (Ryan Buffington).

### 2026-03-08 — Pay-period-aware budgets + Henry Schein upload + Medical Supplies subcategories
Biweekly payroll budget multiplier, Henry Schein XLSX import with matching, and Medical Supplies subcategory breakdown for BFM.

1. **Pay-period-aware budgets (Migration 50)** — New `payroll_schedule` singleton table stores biweekly cadence (anchor date 2026-02-25, every 14 days, Wednesday). New `is_per_payroll` and `per_payroll_cents` columns on `budget_items`. `_get_budget_status()` dynamically computes effective monthly budget as `per_payroll_cents × pay_periods`. Budget input shows per-payroll amount with `×2 = $51,546` or `×3 = $77,319` annotation. `save_budget()` updates `per_payroll_cents` and syncs `monthly_budget_cents = per_payroll * 2` for backward compatibility. Payroll ($25,773/payroll) and Taxes ($9,750/payroll) marked as per-payroll categories.
2. **Henry Schein XLSX upload** — Imported 6 invoices (58 line items, $9,516 total, Oct 2025–Feb 2026) from Items Purchased export. 3 invoices matched to bank transactions (Dec $2,253, Jan $2,136, Feb $2,037) — all exact matches with $0 amount diff.
3. **Henry Schein parser fix** — Amount column in XLSX shows invoice total on every row (not per-item). Parser was summing these, inflating totals (e.g., $2,037 × 11 rows = $22,408). Fixed `inv_total` to take Amount once per invoice: `_parse_amount(group.iloc[0].get(amount_col))`. Item amounts now use `unit_price * qty`.
4. **Python 3.9 compat** — Added `from __future__ import annotations` to `core/henryschein.py` to fix `str | None` type hint error.
5. **Henry Schein merchant alias** — Created `henry schein` (contains) → Medical Supplies alias for auto-categorization of future transactions.
6. **Henry Schein transactions recategorized** — 3 matched bank transactions moved from Household/Supplies → Medical Supplies / General. Merchant canonical set to "Henry Schein".
7. **Medical Supplies subcategories** — Created 8 subcategories: Diagnostics (76% of HS spend — Cepheid COVID/Flu/RSV test kits $680/ea, Strep A, HemoCue glucose, EKG electrodes), Rx (8% — injectable meds), Exam Supplies (8% — table paper, thermometer covers, pulse ox, ear curettes), PPE (4% — gloves, Sani-Cloth wipes, sharps containers, masks), Needles & Syringes (4% — safety needles, luer lock syringes), Wound Care (<1% — adhesive bandages), Liquid Nitrogen (Air Supply deliveries), General (mixed Henry Schein orders).
8. **Medical Supplies moved to FOCUS** — Budget section changed from "other" to "focus" ($2,300/mo budget).

### 2026-03-08 — Amazon Business upload + BFM category overhaul + budget polish
Amazon Business CSV import with order matching, major BFM category restructuring, subcategory budgets, and Personal transaction recategorization.

1. **Amazon Business CSV upload** — Uploaded 1 year of Amazon Business order history (327 line items, 211 payment groups, $18.4k total). 69 of 71 Amazon bank transactions matched to product details via `parse_amazon_csv()` + `group_orders()` + matching algorithm. Auto-applied 64 exact matches, 5 likely/date-only matches.
2. **New BFM categories** — Kitchen (Disposables/Paper Products/Paper Towels), Bathroom (Toilet Paper), Rent, Compliance (Document Shredding/Credentialing), Accounting, Retirement (Simple IRA).
3. **New BFM subcategories** — IT/Hardware, IT/Services, Supplies/Printer Paper, Supplies/Printer, Electronics/Tools, Medical Supplies/Liquid Nitrogen, Patient Services/Communication, Utilities/Landlord Pass-Through.
4. **IT Services renamed to IT** — Category renamed, On Site PC Services → IT/Services, Apple computer + peripherals → IT/Hardware, Amazon IT purchases (cables, mounts, adapters, PC parts) → IT/Hardware.
5. **Rent category** — 40 Providential/Provcom charges moved from Facilities. 10 utility pass-throughs (BuffUtil/Buff111) separated to Utilities/Landlord Pass-Through. 30 actual rent charges remain (~$10,625/month).
6. **Compliance category** — Iron Mountain document shredding (3 txns) + Texas Health Resources credentialing (1 txn) moved from Facilities and Fees.
7. **Accounting category** — Bryan L. Parker CPA charges (13 txns, $700/month) moved from Facilities.
8. **Patient Services/Communication** — Modernizing Medicine/Klara (15 txns, $1,343/month) moved from Subscriptions/Software.
9. **Retirement/Simple IRA** — Edward Jones checks (#10070, #10065, #10058) moved from Needs Review.
10. **Utilities/Internet** — 21 Frontier Communications charges moved from Utilities/General.
11. **Adobe → Software/Productivity** — 13 Adobe charges fixed (12 were already correct, 1 had null subcategory).
12. **Food/Coffee** — Amazon coffee pods and creamer moved from Food/General.
13. **Amazon Supplies recategorization** — Purell → Bathroom, Brother toner/labels → Supplies/Printer, PC fans/cables/adapters → IT/Hardware, screws/WD-40/workbench mat → Office Maintenance.
14. **Deposit Item Returns** — Two $9,900 bounced transfers moved from Fees to Internal Transfer.
15. **Eliminated non-business categories** — Home (13 txns), Household (6 txns), Health & Beauty (8 txns), Entertainment (2 txns) all emptied. Items redistributed: LED lighting/mounts/cables → IT/Hardware, tools → Electronics/Tools, paper towels → Kitchen/Paper Products, toilet paper → Bathroom/Toilet Paper, Lysol/tissue → Bathroom, dish soap/trash bags/trash can → Kitchen, storage boxes/batteries → Supplies, tech wipes → IT/Hardware.
16. **BFM budgets rebuilt** — Cleared stale budgets (IT Services, Subscriptions, Partner Buyout) and rebuilt 27 category budgets based on 3-month averages. Fixed ($114,559/mo): Payroll $61k, Taxes $19.5k, Rent $10,625, Loan $9,884, Retirement $7,500, Utilities $3,600, Patient Services $1,750, Accounting $700. Focus ($11,200/mo): IT $2,700, Facilities $2,600, Medical Supplies $2,300, Software $1,400, Food $1,300, Marketing $500, Compliance $400. Everything Else ($3,265/mo): Fees, HR, Electronics, Staff Gifts, Storage, Supplies, Office Environment, Collections, Office Maintenance, Professional Development, Shipping, Training. Grand total: $129,024/mo.
17. **Check categorization** — Check #10070/$10065/$10058 → Retirement/Simple IRA (Edward Jones). Check #3697 → HR (provider license reimbursement). Check #3687 remains Needs Review.
18. **SERVICE charge** — $1 bank service charge moved from Needs Review to Fees.

### 2026-03-08 — Subcategory budgets + budget layout polish + transaction recategorization
Optional subcategory-level budgets, budget KPI layout improvements, and bulk transaction recategorization across November–December.

1. **Subcategory budgets (Migration 49)** — New `budget_subcategories` table enables per-subcategory budget targets. Subcategory rows show `$` input field; when budget is set, remaining amount and progress bar appear. Empty inputs show `$—` placeholder. `save_budget()` handles `subbudget_{category}__{subcategory}` form fields. Category-level save changed from `INSERT OR REPLACE` to `UPDATE + INSERT` to preserve `budget_section`.
2. **Budget KPI layout** — Month dropdown pulled out of KPI box, placed left-aligned on same row. KPI box (Budgeted/Spent/Remaining) centered via `position: absolute` on dropdown so it doesn't affect centering. Dropdown enlarged (1.05rem font).
3. **Section order** — Focus section moved above Fixed in budget table (`_BUDGET_SECTIONS` order swapped).
4. **Green threshold** — Remaining amounts within $1 of zero show green instead of flipping to red (applies to category rows, subcategory rows, and KPI summary).
5. **Subcategory budgets set** — Home/Landscaping ($1,321), Home/Security ($122), Home/Cleaning ($275), Home/Laundry ($500), Ranch/Mortgage ($3,945), Health & Beauty/Fitness ($64), Storage/General ($266). Applied to both local and production.
6. **December recategorization** — 14 Amazon purchases recategorized from Home/General: diapers/baby gate/trampoline → Childcare, LED lights/beam clamps → Home/Improvement, ceiling mount → Home/Security, leather cleaner → LL Expense, snacks → Food/Groceries, grab bar → Abuelitos. 9 Entertainment/General Amazon items → Shopping/Gifts (Christmas gifts). DashPass → Food/Delivery. Clothing/General kids clothes → Clothing/Kids. TJ Maxx → Shopping/Kids (all locations). Shopping/Amazon December items → Shopping/Gifts.
7. **November recategorization** — Kids clothes → Clothing/Kids (Disney, Children's Place, Crocs). Mickey Mouse hoodie moved from Electronics → Clothing/Kids. Party supplies (balloon stands, tablecloths, plates) → Shopping/Gifts. JBL kids headphones → Shopping/Gifts. Sea shell painting kits → Shopping/Kids. Baby wipes → Childcare. Cradle cap treatment → Childcare. Beam clamps/LED lights → Home/Improvement. Sonic drink mix moved from Pets → Food/Groceries.

### 2026-03-07 — Short-Term Planning: recurring action items + subcategory fixes + duplicate cleanup
Recurring monthly action items, subcategory drill-down fixes, and comprehensive duplicate transaction scan.

1. **Recurring action items** — Migration 46-47: added `is_recurring INTEGER DEFAULT 0` and `completed_month TEXT` columns to `action_items`. Three manual-pay items (house mortgage 1st, Kubota tractor 3rd, ranch mortgage 19th) marked `is_recurring = 1`. When a recurring item is completed, `completed_month` stores `YYYY-MM`. At page load, `_get_action_items()` auto-resets recurring items completed in a prior month back to pending. Delete button hidden for recurring items. Small ↻ icon shown next to recurring item titles.
2. **Subcategory column alignment** — `budget_subcategories()` endpoint had subcategory dollar amounts appearing under the Budget column instead of Spent. Fixed by moving `${amt:,.0f}` from the 3rd `<td>` to the 2nd.
3. **Subcategory readability** — `.stp-subcat-row td` bumped from `var(--ui-font-xs)` (0.68rem) to 0.92rem/weight 600 with increased padding.
4. **Section spacing** — `.stp-section` margin-bottom increased to 2.5rem. `.stp-section--border-label` margin-top increased to 2.5rem. Section labels ("ACTION ITEMS", "GOALS", "MONTHLY BUDGET") bumped from `var(--ui-font-xs)` to 0.88rem.
5. **Manual Pay indent** — Added `padding-left: 0.5rem` to `.stp-actions-grid` so "MANUAL PAY" starts to the right of "ACTION ITEMS".
6. **Duplicate transaction cleanup** — Comprehensive scan found and removed 7 duplicates total: Student Loan THECB ($416.73), Folds of Grace ($114.17), Denton County ($76.25), Whatnot ($107.40), Living Spaces ($745.84) on both local and production; Amazon Oct 6 ($29.22) and Amazon Jul 10 ($113.65) local only.

### 2026-03-07 — Short-Term Planning: action items polish + budget table readability
UX improvements to the Short-Term Planning page across action items and monthly budget sections.

1. **Action items readability** — Bumped action item text from `var(--ui-font-base)` (0.82rem) to `1.0rem` / weight 600, matching the budget table. Column headers ("MANUAL PAY", "AUTOPAY") bumped from 0.62rem to 0.78rem. Add-item input also 1.0rem/600.
2. **Due date ordinals** — Action item `due_date` values (day-of-month integers like "3") now display with ordinal suffixes: 1st, 3rd, 19th. New `_ordinal()` helper in `short_term_planning.py`. `_get_action_items()` computes `due_display` field.
3. **Ask Opus button fix** — Short-Term Planning page button was missing `btn btn-primary btn-sm` classes (had only `pl-btn-ask`). Now matches Dashboard and Cash Flow button styling.
4. **Budget table: 3-Mo Avg readability** — `.stp-avg` font bumped from `var(--ui-font-xs)` (0.68rem) to `1.0rem` to match table body.
5. **Budget table: uniform column spacing** — Removed all custom `nth-child` padding overrides that created uneven gaps. Budget input uses HTML `size` attribute (sized to value length) instead of fixed CSS `width`, preventing the Budget column from inflating with empty space.
6. **Budget table: progress bar + percentage** — Bar widened from 80px to 100px. Percentage label shown permanently next to bar (e.g., "40%", "180%") via `.stp-budget-pct` span. Wrapped in `.stp-budget-progress-wrap` flex container.
7. **Title spacing** — Added `margin-top: 1.5rem` to `.stp-section--border-label` for more breathing room between page title and Action Items box.
8. **Review banner text** — Goal card review banner shortened from "Monthly check-in: Review your progress" to just "Monthly check-in".
9. **Goal card alignment** — Added `min-height: 2.6rem` to `.stp-goal-header` and `align-items: flex-start` so dollar amounts and progress bars align vertically across all 3 goal cards even when titles wrap.
10. **Lock In Plan button fix** — `{{ goal|tojson|e }}` in onclick attributes produced broken HTML for complex nested goal objects. Fixed by storing goal data in `<script type="application/json" id="stp-goals-data">` block and looking up by ID.
11. **fmt_dollars() rounding fix** — `fmt_dollars()` in `web/__init__.py` now rounds before checking sign, preventing `-50 cents` from displaying as `−$0` in red.
12. **Budget column order** — Swapped Spent and Budget columns (Spent now first).
13. **Budget $ prefix** — Budget input wrapped in `<span class="stp-budget-input-wrap">$<input ...></span>` for dollar sign prefix.
14. **Duplicate transaction cleanup** — Removed duplicate Cesar Mauro ($275) and Complete Landsculpture ($1,321.24) transactions caused by same payment visible from two Plaid-connected accounts. Cleaned on both local and production.

### 2026-03-07 — Rebrand: Ledger Oak → Ledger AI + icon update + unified accent color
App renamed from "Ledger Oak" to "Ledger AI" across all source files and templates.

1. **App name** — All references updated: page titles (12 templates), `base.html` default title + mobile header, sidebar wordmark, AI system prompt (`ai.py`), Plaid client name, PDF export footer, auth realm, docstrings (`run.py`, `__init__.py`), smoke test header.
2. **Sidebar icon** — New `ledger-ai-icon.png` (from "Ledger AI icon v2.png"). Displayed at 176×176px in vertical stacked layout. `object-fit: contain`, no border-radius. Negative margins (`margin-top: -1.8rem` on `.sb-brand`, `margin-bottom: -2rem` on icon, `margin-top: -1rem` on `.sb-brand-text`) compensate for PNG whitespace.
3. **Subtitle removed** — "EXPENSE TRACKER" subtitle below wordmark removed. Sidebar now shows just icon + "LEDGER AI".
4. **All entity accents unified** — Personal changed from `#14a9f8` to `#003eb6`, LL changed from `#a78bfa` (purple) to `#003eb6`. All three entities now use the same blue accent.
5. **Wordmark color** — "LEDGER AI" text changed from entity accent to `var(--blue)` (`#0a84ff`) so it's consistent regardless of entity.
6. **Fly infrastructure unchanged** — Fly app names (`ledger-oak`, `ledger-oak-demo`), volume names, and URLs kept as-is (infrastructure references).

### 2026-03-07 — Dashboard redesign: Details/Compare tabs, split insights, KPI sizing
Major dashboard restructuring with two view modes and separated insight sections.

1. **Details/Compare tabs** — New segmented control toggles between Details (single-period) and Compare (two-period side-by-side) views. Details tab shows single KPI panel + categories + insights. Compare tab shows left/right KPI panels + categories comparison + insights.
2. **KPI box sizing** — KPI panels increased to 40% width (up from 30%) on both tabs for better readability.
3. **Expense Insights split** — Insights box renamed to "Expense Insights" and now shows only expense-related insights (category increases, new merchants, large transactions). Income insight removed from `_compute_compare_insights()`.
4. **Income vs Expenses Insights** — New "Income vs Expenses Insights" section below the IE line chart. New `_compute_income_insights()` function generates income change, top income source, and expense-to-income ratio insights. New HTMX endpoint `GET /dashboard/ie-insights`. Spending ratio capped to 90–200% range to avoid absurd values.
5. **Subcategory bar width** — Subcategory bars 20% narrower than category bars (`flex: 0.8`) for visual hierarchy.
6. **Insights box height** — Removed `min-height: 200px` from `.iu-insights-box` and `.iu-upcoming-box`. Upcoming box matches insights box height via `align-items: stretch`.
7. **HTMX race condition fix** — Compare tab staggered HTMX calls with `setTimeout` (0ms categories, 50ms insights-upcoming, 100ms ie-insights) to prevent simultaneous requests to same target.
8. **Insights readability** — `.iu-text`/`.iu-merchant` bumped from 0.74rem/500 to 0.82rem/600. Section labels (`.iu-half-label`) from 0.58rem to 0.64rem. Date/amount from 0.68rem to 0.74rem. Row padding increased.
9. **New templates** — `dashboard_detail_insights.html` (Details view insights + upcoming), `dashboard_detail_cats.html` (Details view categories), `dashboard_ie_insights.html` (income vs expenses insights below IE chart).

### 2026-03-05 — BFM transaction categorization + Planning card polish + dashboard fix
Production database updates and UI fixes.

1. **Partner Buyout category (BFM)** — New category for Allison Flesher buyout transactions (4% practice ownership, $350/mo checks). 16 transactions recategorized (9 debits, 7 credits). Added to all NOT IN exclusion lists in `core/reporting.py` and `web/routes/dashboard.py` (`_TRANSFER_CATS`, `_exclude_transfers_clause()`, and 8+ hardcoded strings). Fixed `get_income_vs_expenses_daterange()` which was also missing `Owner Contribution` from its CASE WHEN exclusions.
2. **Insurance Incentive subcategory (BFM)** — New subcategory under Income for 3 large quarterly deposits ($29.9k, $31.3k, $32.4k) that just said "Deposit".
3. **Athena Health subcategory (BFM)** — New subcategory under Income for 310 daily ACH deposits ($2.3M total) from Athena Health medical billing service. All "BUFFINGTON ACH ITEMS" deposits recategorized from Income/NULL or Income/Patient Payments to Income/Athena Health.
4. **Planning card title font** — `.pl-box-name` font bumped from 0.62rem to 0.78rem for better readability.
5. **Planning item renames** — "Edward Jones Retirement" → "Edward Jones", "Tractor & Implements" → "Tractor", "Skid Steer & Implements" → "Skid Steer".
6. **Insights "All caught up" fix** — `.iu-empty-sm` had `display: flex` which overrode the HTML `hidden` attribute, causing "All caught up" to show even when insights were visible. Added `.iu-empty-sm[hidden] { display: none; }`.
7. **Summary band dividers committed** — Faint divider lines below header and below liabilities row were in local CSS but had never been committed to production.

### 2026-03-05 — Planning page: ranch equipment assets + Kubota loan
Added ranch equipment to Planning page net worth projections.

1. **Ranch value updated** — Ranch asset changed from $608k to $650k (purchase price as of 2025).
2. **Skid Steer & Implements** — New asset: $48,000 (50% of ~$96k). JD 333G compact track loader (2021, ~1000 hrs) + 6 attachments (AB32 auger, AT321181, DB96 blade, GR84B grapple, RC78B rotary cutter, TR48B trencher). JD equipment paid off. Depreciation rate: -5%/yr.
3. **Tractor & Implements** — New asset: $175,000 (100% ownership). Kubota M6-141DTC-F-1 (2025, 30 hrs) + LA2255 loader + BB2596 box blade + PFL4648 pallet forks + RC5715 rotary cutter. Depreciation rate: -5%/yr.
4. **Kubota Loan** — New liability: $167,707 @ 0% interest, $3,164/mo, 60-month term maturing 07/2030.
5. **Sort order** — Assets sorted highest-to-lowest value. Liabilities sorted biggest-to-smallest balance.

### 2026-03-05 — Planning page: modal UX polish + borderless inputs + formatting
Planning page modal and summary band refinements.

1. **Removed Update button** — Settings bar (inflation rate, custom milestone) now submits via Enter key only. Removed `.pl-btn-update` button and CSS.
2. **Borderless modal inputs** — `.pl-modal-input` changed to `background: transparent !important; border: none !important; outline: none !important; box-shadow: none !important; -webkit-appearance: none`. Uses `!important` to override global `input:focus` rule that adds blue border + box-shadow. Inputs look like plain editable text.
3. **Comma formatting** — Current value, monthly contribution, and monthly payment display with commas and no cents (`'{:,.0f}'.format()`). Rate keeps decimal (`'{:.2f}'.format()`). JS `submit` event listener strips commas from money fields before POST.
4. **Tight % suffix** — Rate input uses `size="4"`, `width: auto`, `text-align: right` via `.pl-modal-input--pct`. Wrapper `.pl-input-wrap--tight` with `gap: 0`. Suffix `.pl-input-suffix` with `margin-left: 0.1rem` for minimal breathing room.
5. **Summary band font hierarchy** — Header row (TODAY, @60, @65, @70) bumped to `0.88rem` (matching net worth values). Assets/liabilities rows at `0.78rem` (slightly smaller).
6. **Combined Net Worth label** — `.pl-combined-label` increased from `0.58rem` to `0.82rem`. Item text bumped to `0.72rem`, values to `0.88rem`.
7. **Summary band dividers** — Faint `1px solid rgba(255,255,255,0.06)` border below header row (`.pl-summary-header`) and below liabilities row (`.pl-summary-row--liability`). Light-mode uses `rgba(0,0,0,0.06)`.
8. **Combined Net Worth box** — `max-width: 480px` (down from 520px), centered via `margin: auto`.

### 2026-03-05 — Global Ask Opus: AI chat on every page
Moved AI chat from Planning-only to a global modal available on Dashboard, Transactions, Subscriptions, Cash Flow, Planning, and Reports.

1. **New `web/routes/ai.py` blueprint** — Global AI chat with `POST /ai/ask` and `POST /ai/clear` endpoints. Page-specific context builders gather relevant financial data per page (planning projections, spending trends, transaction patterns, subscription costs, account balances). System prompt adapts per page role. Conversation persistence per entity+page in `/tmp/expense-tracker-ai/`.
2. **Global modal in `base.html`** — Single chat modal shared across all pages. JS function `aiChatOpen('pagename')` sets page context and opens modal. Page switching clears thread. Escape/click-outside closes. HTMX form posts to `/ai/ask`.
3. **Ask Opus button on 6 pages** — `.page-title-row` flex container with `h1` title + button. Button styled as deep navy fill (`#001a3a`) with light blue ring (`#14a9f8`), no glow. Hover brightens fill slightly.
4. **Planning cleanup** — Removed ~420 lines of AI chat code from `planning.py` (context gatherer, conversation persistence, system prompt, endpoints, markdown formatter). All moved to `ai.py`. Planning page button changed from `plChatOpen()` to `aiChatOpen('planning')`.
5. **CSS rename** — All `.pl-chat-*` classes renamed to `.ai-chat-*` for global scope. `.pl-btn-ask` button class with `margin-left: auto` pushes button right. `.pl-btn-update` gray style for Planning's Update button.
6. **Context builders per page** — Planning: assets, liabilities, projections, spending, account balances. Dashboard: KPIs, top categories, top merchants, 6-month trends. Transactions: 90-day patterns, category distribution, large txns. Subscriptions: watchlist items, costs, statuses. Cash Flow: account balances, credit utilization, manual recurring. Reports: 12-month trends, month comparisons. General: fallback with spending totals + accounts.

### 2026-03-04 — Planning page: auto-age from birthday + delete in modal + tighter milestones
Planning page UX improvements for managing net worth projections.

1. **Migration 38: birth_date column** — Added `birth_date TEXT` to `planning_settings`. Pre-populated with `1977-06-21`. Age auto-computed from birth date via `_compute_age()`.
2. **Click-to-edit age** — Age displays as clickable number with dashed underline. Clicking reveals date picker for birthday. Submitting auto-saves and recomputes age. Supports different users (e.g. spouse) entering their own birthday.
3. **Delete moved to modal** — Removed `×` delete button from table rows. Delete button now appears inside the edit modal (red outline, bottom-left). Uses separate `<form>` outside the main edit form to avoid nested form issues.
4. **Tighter milestone columns** — `@60`, `@65`, `@70` columns squeezed with reduced padding (0.25rem). Name column gets `width: 100%` to push milestones right.
5. **Python 3.9 compat** — Added `from __future__ import annotations` to fix `str | None` type hint syntax.

### 2026-03-04 — AI features: suggest, cancellation tips, dashboard analysis
Three AI-powered features using Claude via OpenRouter API.

1. **AI client (`core/ai_client.py`)** — OpenRouter API client using `anthropic/claude-sonnet-4.6`. Shared by all AI features. Requires `OPENROUTER_API_KEY` env var. 20s timeout, graceful fallback when unavailable.
2. **AI Suggest (transactions)** — Button in transaction edit modal sends merchant name + amount to Claude, returns suggested category/subcategory. Shows error feedback when AI cannot categorize.
3. **AI Cancellation Tips (subscriptions)** — On-demand button on watchlist items fetches personalized cancellation instructions from Claude. Displayed in subscription detail modal.
4. **AI Analysis (dashboard)** — "AI Analysis" button in Insights section. Gathers spending summary (category totals, top merchants, period comparisons), sends to Claude, displays 3-5 narrative insights. Results cached in-memory for 1 hour per entity+period combo. Blue accent styling matching insights aesthetic.

### 2026-03-04 — Subscriptions page: watchlist + tracking + detail modals
New `/subscriptions` page for managing recurring subscription charges.

1. **Migrations 32-34, 37** — `subscriptions` table (watchlist), `subscription_dismissals` (suggestions), `subscription_tracking` (timeline), `subscription_account_info` (account details).
2. **Auto-detection** — Suggests subscriptions from transaction patterns. Dismiss/undo for unwanted suggestions.
3. **Detail modal** — Tracking timeline (price changes, notes), account info fields (email, phone), "Phone a Friend" share button for cancellation calls.
4. **Cancellation tips** — AI-generated cancellation instructions via OpenRouter.
5. **Account info** — Email, phone, notes fields per subscription. Phone a Friend name/number for calling to cancel.

### 2026-03-04 — Transactions page polish + Connected Accounts cleanup
UI improvements across transactions and Plaid pages.

1. **Subcategory column** — Added as its own column on transactions page (previously combined with category).
2. **Column spacing** — Widened Amount, Category, and Subcategory columns for readability.
3. **Connected Accounts** — Fixed column alignment across institution tables. Connect a Bank + Sync All buttons side by side. Disconnect button styled as red text only. Last synced text shrunk.
4. **Global table fix** — Removed bottom border on last table row.
5. **Subscription filter** — Excluded interest charges and fees from subscription detection.
6. **Color tuning** — Toned down green/red to match blue/purple intensity across app.

### 2026-03-04 — Planning page: net worth projections (initial build)
New `/planning` page for long-term financial planning.

1. **Migrations 35-36** — `planning_settings` (inflation rate, age, custom milestone) and `planning_items` (assets + liabilities with growth rates, contributions, payments).
2. **Projection engine** — Assets: compound growth formula `FV = V*(1+r)^n + C*((1+r)^n - 1)/r`. Liabilities: amortization with monthly payment. All inflation-adjusted to today's dollars.
3. **Cross-entity visibility** — Personal and BFM share view (each sees other's items). LL excluded.
4. **Cashflow linking** — Items can pull live balances from `account_balances` table instead of manual entry.
5. **Combined net worth** — Summary row shows total across all visible entities at each milestone age.
6. **Initial data** — Home Mortgage ($1.43M @ 4.75%), Edward Jones Retirement ($275.7k @ 7%), Home ($2M asset @ 3.5% appreciation).

### 2026-03-04 — Plaid production + liabilities + category overhaul (BFM & Personal)
Plaid upgraded to production. Liabilities product enabled. Major category reorganization for both BFM and Personal entities via direct SQL on live Fly databases.

1. **Plaid production** — Set `PLAID_ENV=production` and `PLAID_SECRET` via Fly secrets. Added `optional_products=[Products("liabilities")]` to Link token in `plaid_client.py`. Removed non-existent `plaid.Environment.Development` (SDK only has Sandbox + Production). Liabilities data confirmed flowing on Cash Flow page.
2. **Plaid account cleanup** — Removed American Express from Personal (business card, 0 txns). Removed Quicksilver from BFM plaid_accounts (personal card). Kept First Horizon Bank.
3. **BFM category overhaul (29 categories)** — Removed personal categories (Office, Household, Entertainment, Groceries, etc.). Created business categories: IT Services, Facilities, HR, Patient Services, Collections, Medical Supplies, Staff Gifts, Office Environment, Office Maintenance, Training. Broke down Subscriptions into Software (AI/Productivity/Accounting/Automation/Collaboration/Communication/Financial Monitoring/HR/Marketing), Office Environment (Media), Professional Development (Membership), Patient Services (Telehealth). Subcategorized Utilities (Electric/Internet/Phone/Water). Merged Dining + Snacks into Food (Coffee/Delivery/Restaurants/Snacks/Water Delivery). Removed Shopping (merchants distributed). 60+ alias rules created/updated.
4. **Personal category overhaul (24 categories, down from 34)** — Removed 10 categories: Unknown, Other, Gas & Auto, Personal Care, Education, Travel, Electronics, Shopping, Kids, Subscriptions, Office. Merged Dining + Groceries into Food (Coffee/Delivery/Fast Food/Groceries/Restaurant). Broke out Subscriptions: streaming → Entertainment (Streaming Video/Streaming Music), software → Entertainment/Software, Tonal → Fitness, DoorDash → Food/Delivery. Renamed: Home Improvement → Home (added Landscaping/Security/Pest Control/Plumbing/Laundry), Pet Supplies → Pets, Ask Kristine → Needs Review, Kristine Business → LL Expense. Subcategorized: Ranch (Equipment/Mortgage/Supplies/Utilities), Utilities (Electric/Gas/Trash), Fees (Interest/Wire Fees/Bank Fees). Moved Cotton Electric to Ranch/Utilities, Folds of Grace to Home/Laundry.
5. **Category standards** — Every category has "General" subcategory. No "Unknown" subcategories. Unknowns go to "Needs Review" category. Applied across all 3 entities.

### 2026-03-03 — Demo instance + configurable entities + Cash Flow tweaks
Public demo at `ledger-oak-demo.fly.dev` with fake seed data, no auth, 2 entities. Made entity map configurable via env var.

1. **`ENTITIES` env var** — `web/__init__.py` parses `ENTITIES=Personal:personal,Business:company` to override the default 3-entity map. Colors and labels fall back gracefully for unknown display names (e.g. "Business" gets blue accent + business labels).
2. **`fly.demo.toml`** — Separate Fly config: `app=ledger-oak-demo`, own volume (`ledger_oak_demo_data`), `ENTITIES` override, no `APP_USERNAME`/`APP_PASSWORD` (auth disabled).
3. **`scripts/seed_demo_data.py`** — Generates realistic fake data for 2 entities. Wipes and re-seeds on each run. Personal: ~1010 transactions, 5 accounts (2 bank + 3 credit), 2 manual recurring, 26 categories with 154 subcategories. Business: ~688 transactions, 4 accounts (3 bank + 1 credit), 2 manual recurring, 22 categories with 108 subcategories. Business merchants: Staples, Adobe, Zoom, Delta, ADP, Google Ads, McKinsey, UnitedHealthcare, etc.
4. **Dynamic `_ENTITY_DISPLAY`** — `cashflow.py` replaced hardcoded entity display map with `_build_entity_display()` that derives from `_ENTITY_MAP` at runtime. Cross-entity sections show correct names for both prod and demo.
5. **Upcoming charges capped at 3** — `cashflow.py` `_load_entity_section()` slices `combined[:3]` to limit upcoming charges per account card.
6. **Credit card balances positive** — Seed data uses positive balances (amount owed) matching Plaid convention.

### 2026-03-03 — Cash Flow visual polish + Plaid-driven accounts + modal redesign
Replaced hardcoded `_ACCOUNT_DEFS` with Plaid-driven `_sync_plaid_accounts()`. Card and modal visual polish pass.

1. **Plaid-driven accounts** — `_sync_plaid_accounts()` dynamically creates/updates `account_balances` rows from connected Plaid accounts with live balances. Replaces hardcoded `_ACCOUNT_DEFS` and `_ensure_accounts()`. Handles duplicate account name disambiguation (appends institution + mask). Empty `match_names` guard prevents invalid SQL. Orphaned `account_balances` rows cleaned up on Plaid disconnect.
2. **Credit limit preservation** — When Plaid returns null for credit limit (Capital One), the UPDATE skips `credit_limit_cents` to preserve manually-entered values.
3. **Card color tints** — Bank cards: Personal accent blue `rgba(20,169,248,0.10)`. Credit cards: LL accent purple `rgba(191,90,242,0.10)`. Both with `backdrop-filter: blur(16px)` and color-matched borders. Light-mode at slightly lower opacity.
4. **Balance font specificity fix** — `.cf-box-value.cf-box-value--inline` (two-class selector) overrides `.cf-box-value` which appeared later in CSS. Balance font tuned to 0.94rem.
5. **Bank grid 5-column** — `.cf-grid--banks` changed to `repeat(5, 1fr)` to fit all 5 personal bank accounts on one row.
6. **Empty state on cards** — When no upcoming charges, "UPCOMING" label hidden and "No upcoming charges" centered on card. Not italicized.
7. **Modal header** — Balance moved to same line as account name. Modal name font increased to 0.80rem.
8. **Modal credit limit** — Hidden for bank accounts, shown for credit cards. `cf-card-subline[hidden]` rule fixes `display: flex` overriding `hidden` attribute.
9. **Modal background** — Darker `#111` (light: `#f0f0f0`). Header gets 0.5rem bottom margin for spacing.
10. **Modal empty state** — "UPCOMING" label hidden, "No upcoming charges" left-justified, not italicized.
11. **Modal payment line** — Left-justified (`justify-content: flex-start`). Due date placeholder changed from "15" to "Day".
12. **Add Manual Recurring** — Reuses payment line classes (`cf-modal-input`, `cf-modal-input--small`, `cf-modal-input--inline`) for consistent look. No underlines, left-justified compact layout. Section label and inputs at 0.55rem, 50% opacity for subtle appearance. Tight spacing between label and input row.
13. **Modal section alignment** — Credit limit right-aligned (matches card). Payment line, upcoming, and add recurring all left-justified.

### 2026-03-02 — Workflow links on To Do page + compact font fix
Restored access to the 5 workflow pages (Upload from Bank/CC, Upload from Vendors, Match, Categorize Vendors, Categorize Remaining) which were removed from the sidebar in PR #23.

1. **Workflows section on To Do page** — New "Workflows" panel below the "Review" queues panel with links to all 5 workflow pages. Always visible (not count-driven) since these are proactive tools.
2. **Section labels** — `.todo-section-label` CSS class added for "REVIEW" and "WORKFLOWS" uppercase tracked headers above each panel.
3. **Compact font fix** — Added `font-size: var(--ui-font-base)` to `.main` content container. Workflow pages (Upload, Vendors, Match, Categorize) were using the default 15px body font for `<p>`, `<strong>`, etc., making them look oversized vs. the redesigned pages. All `rem`-based explicit sizes (KPI values, page titles, charts) unaffected.
4. **Plaid Link token fix** — Removed `liabilities` from Plaid Link token products (was causing errors). Cash Flow liabilities integration still works via separate `get_liabilities()` call.
5. **Bulk categorization** — All Personal (142) and Business (68) uncategorized transactions categorized via merchant alias rules. 55 Personal + 32 Business alias rules created. New "Needs Review" category added to Business entity.
6. **Data cleanup** — Removed 364 business transactions (Amex Amazon Business + Capital One Spark Cash Select) accidentally synced into Personal entity. Plaid accounts/items cleaned.
7. **Stale PR closed** — PR #76 (To Do v2 polish) closed as superseded.

### 2026-03-02 — To Do queue detail popups + per-item dismiss
Inline HTMX-powered modal popups for "Large transactions" and "New merchants" review queues on the To Do page. Per-item and bulk dismiss with date-based cutoff tracking.

1. **Migration 30** — `queue_dismissals` table: queue_type (UNIQUE), dismissed_at, dismissed_before. Stores bulk dismiss date cutoff per queue type.
2. **Migration 31** — `queue_item_dismissals` table: queue_type, item_key (UNIQUE together), dismissed_at. Tracks individually dismissed transactions/merchants.
3. **Queue detail endpoints** — `GET /todo/queue/large-txns` and `GET /todo/queue/new-merchants` return HTML partials. Large txns: table with Date, Merchant, Amount, Category. New merchants: compact rows with first seen date, txn count, total spent.
4. **Modal popup** — `.tq-modal-scrim` + `.tq-modal-card` (520px, 80vh max). Same pattern as Cash Flow edit modal: fixed overlay, click-outside-to-close, Escape key, × button.
5. **HTMX lazy loading** — Queue rows changed from `<a>` to `<div>` with `hx-get` + `hx-target="#tq-modal-body"`. `onclick="tqOpenModal()"` shows loading state immediately.
6. **Per-item dismiss** — × button on each row uses `hx-post` to `/todo/queue/dismiss-item` with `hx-target="closest tr"` (or `.tq-merchant-row`) + `hx-swap="outerHTML"`. Returns empty response to remove the row inline. Item key: `transaction_id` for large txns, `merchant_canonical` for new merchants.
7. **Bulk dismiss** — "Dismiss All" button upserts `queue_dismissals` with today's date. Also clears per-item dismissals for that queue type.
8. **Count queries updated** — Both `_get_queue_counts()` and detail query functions exclude items in `queue_item_dismissals` via Python-side set filtering after SQL fetch.
9. **Footer layout** — "View all in Transactions ›" on bottom-left, "Come Back Later" + "Dismiss All" buttons on bottom-right. Flexbox `space-between`.
10. **Popup title typography** — Uppercase tracked Apple style (`.tq-detail-title`: `text-transform: uppercase`, `letter-spacing: var(--label-tracking)`, centered).
11. **To Do page layout** — Review Queues panel header removed. Panel capped at `max-width: 420px`. Badge counts right-aligned with `margin-left: auto`.
12. **Transaction filters** — Added `large_txns` and `new_merchants` filter params to `transactions.py` `_get_filter_params()` and `_build_base_cte()` for "View all in Transactions" drill-through links.

### 2026-03-02 — Cash Flow page + color palette refresh + edit modal redesign
New `/cashflow` page showing per-account balances and upcoming recurring charges. Plus sidebar and dashboard color updates. Edit modal redesigned as card clone with inline-editable fields and manual recurring charge support. Plaid liabilities integration for auto-populating credit card data. **Note:** Hardcoded `_ACCOUNT_DEFS` replaced by Plaid-driven `_sync_plaid_accounts()` in 2026-03-03 update. Card colors and modal layout also updated — see 2026-03-03 entry.

1. **Migration 26+27** — `account_balances` table with fields for balance, source (manual/plaid), account type (bank/credit_card), credit limit, payment due day/date/amount, sort order. Plaid linking via `plaid_account_id`.
2. **Migration 28** — `manual_recurring` table: account_id (FK → account_balances, CASCADE), merchant, amount_cents, day_of_month (1–31), created_at. Monthly cadence only.
3. **Cross-entity visibility** — Personal and BFM share view (each sees the other's accounts below). LL is isolated.
4. **Per-account recurring detection** — `_detect_upcoming_for_account()` filters transactions by account name(s), detects recurring merchants (90-day lookback, cadence classification), shows next expected charge date and amount. Auto-detected + manual recurring merged and sorted by date.
5. **Plaid liabilities integration** — `_fetch_plaid_liabilities()` calls `get_liabilities()` for all connected Plaid items. `_apply_plaid_liabilities()` updates balance, credit limit, payment due date/amount, and sets `balance_source='plaid'`. Persists to DB as cache. Early env var check prevents hanging when Plaid credentials aren't configured.
6. **Due date formatting** — Hidden field + display field pattern: hidden `payment_due_day` stores integer for backend, visible field shows formatted date ("Mar 20"). JS `cfFormatDate()` converts YYYY-MM-DD to "Mon D". `cfParseDueDay()` extracts day number from user edits.
7. **Manual recurring charges** — "Add Manual Recurring" section inside edit modal. POST `/cashflow/recurring/add`. Delete via POST `/cashflow/recurring/delete/<id>`. `_get_manual_recurring()` calculates next occurrence date (handles month rollover + day clamping).
8. **Sidebar refinements** — Width shrunk to 210px. Entity toggle `max-width: 181px` to align with LEDGER OAK text.
9. **Color palette refresh** — LL accent: gold → dusty mauve (`#c4909a`). Dashboard series: blue `#14a9f8` (Personal blue) + violet `#a78bfa`. Green/red harmonized: `#4ade80`/`#f87171` (dark), `#22c55e`/`#ef4444` (light).
10. **Deploy** — Two gunicorn workers (`-w 2`) to prevent single-worker blocking. `--graceful-timeout 5` added.

### 2026-03-01 — PR #73: Per-entity To Do page (statement reminders + review queues)
New `/todo` page combining ops checklist functionality with data-driven review queues.

1. **Migration 24** — Two new tables: `statement_schedules` (id, name, statement_day 1–31, notes, is_active, created_at) and `statement_completions` (id, schedule_id FK CASCADE, period_key YYYY-MM, completed_at, UNIQUE(schedule_id, period_key)).
2. **Statement Reminders section** — Inline add form (name + day + notes + Add button). Active schedules sorted by due date ascending. Status logic: "Done" if completion exists for current YYYY-MM period, "Due" if today >= clamped statement day and not done, "Upcoming" otherwise. Clamped day handles months with fewer days (e.g. day 31 in Feb → Feb 28). Mark Done button (UPSERT ignore on conflict). Delete with confirm.
3. **Review Queues section** — Count-driven links to existing filtered pages: Uncategorized transactions (`/transactions/?uncategorized=1`), Vendor breakdown needed (`/transactions/?vendor_breakdown=1`), Possible transfers (`/transactions/?possible_transfer=1`), Orders to match (`/match/`), Orders to categorize (`/categorize-vendors/`). "All caught up" empty state when all counts are zero.
4. **Route** — `web/routes/todo.py` blueprint (url_prefix `/todo`). Endpoints: GET `/todo/`, POST `schedules/create`, POST `schedules/complete/<id>`, POST `schedules/toggle/<id>`, POST `schedules/delete/<id>`.
5. **Sidebar** — "To Do" link added to primary nav between Dashboard and Transactions.
6. **Smoke tests** — Section 10: CRUD, entity isolation (BFM can't see Personal schedules), cascade delete (completions removed when schedule deleted).

### 2026-03-01 — PR #72: UI density pass + page unification
Two combined changes: (1) unify non-dashboard pages to flat + outlined design language, (2) reduce vertical whitespace ~25% across all pages. CSS-first approach. Also folds in PR #70 equal-height fix. All 16 stale PRs closed.

1. **Page-chrome primitives** — New shared CSS classes: `.section-title` (1rem/700), `.outline-panel` (transparent bg + hairline border, 14px radius), `.panel-header` (tracked uppercase), `.table-wrap` (overflow-x), `.empty-state`, `.form-narrow` (500px max), `.toggle-btn`.
2. **Template unification** — Transactions, Reports, Upload, Vendors, Categorize, Connected Accounts pages all switched from `.card` to `.outline-panel`. Inline styles replaced with shared classes. Plaid scoped `<style>` block removed.
3. **Density tokens** — New `:root` tokens: `--ui-font-xs` (0.68rem), `--ui-font-sm` (0.78rem), `--ui-font-base` (0.82rem), `--ui-pad-xs` (0.22rem), `--ui-pad-sm` (0.4rem), `--ui-pad-md` (0.75rem), `--ui-gap` (0.75rem), `--ui-radius` (10px).
4. **Radius tightened** — `--radius` 12→10px, `--radius-lg` 16→14px, `--radius-xl` 18→14px.
5. **Controls tighter** — Buttons: padding 0.52→0.4rem, font 0.88→0.82rem. Inputs: padding 0.55→0.38rem, font 0.88→0.82rem. Labels: font 0.78→0.68rem. Form-group margin 0.85→0.55rem.
6. **Tables tighter** — th/td padding 0.55→0.35rem. Font 0.85→0.82rem.
7. **Panels/headings tighter** — Page title 2→1.6rem (margin 1.4→0.9rem). Section title 1.15→1rem. Outline-panel padding 1rem→0.75rem. Card padding 1.2→0.85rem.
8. **Reports tighter** — Stat cards padding 1.2→0.8rem, value font 1.8→1.5rem. Category rows 0.75→0.5rem. Chart card 1.6→1.1rem. Month nav arrows 36→32px, name 1.5→1.3rem.
9. **Filter bar tighter** — Padding 0.75→0.55rem. Input-sm padding 0.35→0.28rem, height 34→30px (light mode).
10. **Main content padding** — Desktop 2rem→1.5rem, tablet 1.5→1.2rem, mobile 68px→60px top.
11. **Equal-height fix** — `.iu-row-grid` `align-items: start` → `stretch` (PR #70 folded in).
12. **Stale PR cleanup** — Closed PRs #29, #32, #34, #46, #47, #49, #50, #56, #57, #58, #62, #64, #66, #67, #70, #71 (all superseded).

### 2026-03-01 — PR #70: Insights + Upcoming equal height on desktop
Single CSS fix: `.iu-row-grid` `align-items: start` → `align-items: stretch`. Both cards now fill identical height regardless of content length. Empty states remain vertically centered via existing flex layout.

### 2026-03-01 — PR #68: Insights + Upcoming half-width side-by-side, no emojis
New Insights + Upcoming section below the Income vs Expenses chart.

1. **Side-by-side layout** — Insights box (left) and Upcoming box (right) sit 50/50 in a `.iu-row-grid` 2-column grid. Both use `outline-band` styling. Stacks vertically at ≤900px.
2. **No emojis** — Insight rows are text-only (no 📈/🆕/💰 icons). Clean rows with just text + chevron.
3. **Insights internal layout** — Top section split into two columns with "THIS MONTH" / "LAST MONTH" uppercase tracked headers. Vertical hairline divider. Bottom "COMPARE" section with cross-period insights (spending change, biggest category shift, income change).
4. **Unified compare header** — "COMPARE THIS MONTH VS LAST MONTH" all on one line, same uppercase/tracked/muted typography as the period half-labels.
5. **Tighter row density** — Row padding 0.32rem (Apple-ish list density). Hairline dividers at 0.06 alpha.
6. **HTMX endpoint** — `/dashboard/insights-upcoming` receives both `left_period` and `right_period`, computes per-period insights via `_compute_insights()`, cross-period compare via `_compute_compare_insights()`, and upcoming recurring via `_detect_recurring()` + `_build_upcoming()`.
7. **KPI panel wiring** — `kpi_panel.html` script triggers insights/upcoming fetch after both panels load (same pattern as categories comparison).

### 2026-02-28 — PR #47: Single-line header strip (no chips, segmented-track container)
Removed chips row, flattened header panel, added strip container matching entity switcher.

1. **Chips removed** — Entire `dhdr-chips` row (Uncategorized, Vendor Needed, Transfers, Include Transfers) removed from template. Backend URL params still accepted for saved view compatibility.
2. **Panel removed** — Wrapper changed from `class="card txn-filter-bar dhdr-bar"` to just `class="dhdr-bar"`. Background transparent, no shadow/border/radius.
3. **Header strip** — New `.dhdr-strip` wraps `.dhdr-row`: `background: var(--seg-bg)`, `border: 1px solid var(--seg-border)`, `border-radius: 12px`, `padding: 10px 12px`. Matches entity switcher track exactly (same tokens, same radius).
4. **Single-line layout** — `.dhdr-row` set to `flex-wrap: nowrap`. Pill widths reduced: account 200→150px, saved views 170→130px. All controls fit on one line at desktop width.
5. **Responsive** — Wraps at ≤900px, stacks at ≤480px. Strip tightens to `padding: 8px 10px`, `border-radius: 10px` on mobile.
6. **Dark mode** — Strip reads near-black (`rgba(255,255,255,0.05)`), not gray. Light mode uses `rgba(0,0,0,0.03)`.

### 2026-02-28 — PR #46: Flat/outlined date picker (match band aesthetic)
Cleaner CSS for the date button and popover to match outline-band look.

1. **Date button** — `.dhdr-datebtn.dhdr-pill` compound selector: transparent bg, no arrow image, `border: 1px solid rgba(255,255,255,0.12)`, no shadow/blur. Higher specificity than `.dhdr-pill` without `!important`.
2. **Border bump** — Popover, divider, and date input borders bumped from 0.10→0.12 alpha for consistency.
3. **Light-mode borders** — Bumped from 0.08→0.10 alpha across popover, divider, date inputs.
4. **Hover/focus** — Dark hover `rgba(255,255,255,0.04)`, light hover `rgba(0,0,0,0.03)`. Focus ring via `var(--focus-ring)`.
5. **Cleanup** — Removed `button#dhdr-datebtn` from PR #45 `!important` block since compound selector handles specificity cleanly.

### 2026-02-28 — PR #45: Premium-flat Spend Trend bars + flat header date picker
Completed the flat-outline design language across the remaining glass/blur elements.

1. **Trend chart container** — `.trend-chart` scoped overrides: transparent background + `1px solid rgba(255,255,255,0.10)` border (matches `.outline-band`). Light mode uses `rgba(0,0,0,0.08)`.
2. **Premium-flat bars** — Subtle gradient fill (`rgba(10,132,255,0.85)` to `0.55`). `::after` pseudo-element adds a 35%-height top highlight (`rgba(255,255,255,0.22)` at `opacity: 0.65`) — no glow or neon.
3. **Selected bar** — `filter: none`, `box-shadow: none`, `opacity: 1` + bold value label. Clean emphasis without bloom.
4. **Header controls flattened** — Date button, account select, saved views select, and SV buttons all get `background: transparent`, `backdrop-filter: none`, `border: 1px solid rgba(255,255,255,0.10)`. Replaced ghost-glass from PR #40.
5. **Popover no glass** — `.dhdr-popover` uses solid `var(--bg)` background, no `backdrop-filter`, no `box-shadow`. Hover items use subtle rgba fill.
6. **Custom date inputs** — Transparent background + hairline border. Light-mode override updated from `var(--input-sm-border)` to `rgba(0,0,0,0.08)`.

### 2026-02-28 — PR #44: Outline-only bands + true 3D donut (extruded depth)
Flattened the three remaining dashboard bands and added real 3D thickness to the donut.

1. **Outline bands** — Activity, Spending, Recurring sections changed from `class="band"` to `class="outline-band"`: transparent background, hairline border, no box-shadow. Band labels use `var(--bg)` background to sit seamlessly on the outline.
2. **Inside-band overrides** — `.outline-band .rpt-cat-list` gets transparent bg/no border. `.outline-band .rpt-cat-row` uses subtle `border-bottom` dividers (last child none).
3. **True 3D extrusion** — New `<g class="donut-extrude" transform="translate(0, 5)">` group renders duplicate arcs shifted down 5px below the main ring. Creates visible "thickness" like a coin edge.
4. **Extrusion styling** — `.donut-slice--extrude`: `pointer-events: none`, `opacity: 0.35` dark / `0.22` light. Non-interactive, subtler than main slices.
5. **Softened ring shadow** — `feDropShadow` reduced to `dy:1, stdDeviation:1.5, flood-opacity:0.12` since extrusion provides real depth cues.

### 2026-02-28 — PR #43: Subtle 3D donut ring — SVG shadow + highlight overlays
Added depth to the donut chart using SVG filters and gradient overlays (no CSS hacks).

1. **SVG defs** — Three new defs: `feDropShadow` filter (`donutRingShadow`), `radialGradient` specular highlight (`donutHighlight`, top-left light source), `radialGradient` inner shade (`donutInnerShade`, edge darkening).
2. **Ring group** — Track + slices wrapped in `<g class="donut-ring" filter="url(#donutRingShadow)">` so shadow applies to the whole ring, not per-slice.
3. **Overlay rings** — Two `<circle class="donut-overlay">` elements above slices: `--highlight` uses `donutHighlight` gradient, `--shade` uses `donutInnerShade`. Both `pointer-events: none`.
4. **Theme-aware opacity** — Dark: highlight 0.22 / shade 0.28. Light: highlight 0.18 / shade 0.16.
5. **Cleanup** — Old CSS `::after` pseudo-element highlight disabled (`display: none`). Slice base opacity bumped from 0.92 to 0.95.

### 2026-02-28 — PR #42: Flatten dashboard — band sections replace nested cards
Removed all nested card surfaces from dashboard sections, replacing with flat band layouts.

1. **Activity band** — Spend Trend (left) + Review Inbox/Insights (right) in `band-grid--2` layout. Chart wrapped in subtle `plot-area` surface.
2. **Spending band** — Donut + legend sit directly inside band with `band-head` title. Removed `chart-card`, `chart-well`, and extra wrapper divs.
3. **Recurring band** — Top Merchants + Upcoming side-by-side in `band-grid--2`. Removed `list-card` wrappers.
4. **New CSS components** — `band-head`, `band-body`, `band-grid`, `band-grid--2`, `band-panel`, `band-stack`, `panel-title`, `band-divider`, `plot-area`. Inside-band overrides flatten `rpt-cat-list` and `donut-legend-list` backgrounds.
5. **Jinja guard fix** — Added missing `{% endif %}` for the `{% if review_count > 0 or ... %}` conditional wrapping Review Inbox + Insights inside `band-stack`.

### 2026-02-28 — PR #31: KPI band — remove cents + center-align (Provider-style)
Cleaner KPI values: whole dollars only, center-aligned cells.

1. **Whole dollars** — KPI values drop cents (e.g. `$7,486` not `$7,486.45`). Uses `"{:,.0f}".format(cents/100)` in Jinja. Net uses `\u2212` minus sign.
2. **Center alignment** — `.kpi-band--centered` modifier centers label, value, and sub-text in each cell via `text-align: center` + flex column `align-items: center`.

### 2026-02-28 — PR #30: KPI band Provider parity (typography + outlined band)
Matched KPI band to Provider dashboard: lighter values, outlined band, period label.

1. **Lighter values** — `font-weight: 500` (was `800`), `font-size: 1.65rem` (was `2.55rem`). Calm, readable numerals matching Provider's thin typography.
2. **Outlined band** — Kept `.band` class for subtle border outline + floating period label badge. Overrode `.band` background to transparent.
3. **Period label** — Dynamic date range label replaces static "Overview" badge (e.g. "Feb 1 – 28"). Computed by `_format_period_label()` in `dashboard.py`.
4. **Tighter spacing** — Cell padding `1.0rem 1.1rem 0.9rem` (was `1.35rem 1.45rem 1.25rem`), label gap `0.55rem` (was `0.75rem`), sub gap `0.45rem` (was `0.70rem`).
5. **Responsive** — Scaled down: 900px `1.50rem`, 480px `1.35rem`.

### 2026-02-28 — PR #28: KPI band typography + remove dividers
Fixed value collision and removed hard vertical dividers.

1. **Smaller values** — `2.55rem` (was `2.85rem`), Latest `2.25rem` (was `2.35rem`). `white-space: nowrap` prevents wrapping.
2. **No dividers** — Removed `border-right` entirely from `.kpi-cell`. Provider KPI bands have no visible dividers between metrics.
3. **Subtle gradient** — Row gets a faint top-to-transparent gradient for soft visual cohesion instead of hard lines.
4. **Tighter padding** — `1.35rem 1.45rem 1.25rem` (was `1.45rem 1.60rem 1.35rem`).
5. **Responsive** — Scaled down font sizes at 900px (`2.25rem`) and 480px (`2.00rem`).

### 2026-02-28 — PR #27: Provider KPI parity (tall, airy, tracked labels)
Tuned KPI band to match Provider dashboard vertical rhythm and typography.

1. **Provider modifier** — `.kpi-band--provider` scoped overrides keep base `.kpi-band` intact.
2. **Taller cells** — Padding `1.45rem 1.60rem 1.35rem` (was `1.15rem 1.25rem`).
3. **Tiny tracked labels** — `0.58rem`, `letter-spacing: 0.18em`, `opacity: 0.70`.
4. **Bigger airy values** — `2.85rem` weight 800 (was `2.25rem`). Latest cell smaller at `2.35rem`.
5. **Softer subtext** — `opacity: 0.60`, `margin-top: 0.70rem`.
6. **Ultra-subtle dividers** — `rgba(…,0.055)` dark / `rgba(…,0.045)` light.
7. **Nearly invisible hover** — `rgba(…,0.02)` dark / `rgba(…,0.015)` light.
8. **Responsive** — Provider-specific padding/font reductions at 900px and 480px.

### 2026-02-28 — PR #26: KPI band flatten (remove card surface)
Removed heavy card surface from KPI band to match Provider flat-band feel.

1. **Flat band** — `.kpi-band` overrides: `background: transparent`, `box-shadow: none`, `padding: 0` (only `padding-top: 0.9rem` for label clearance). Band outline remains from `.band` parent.
2. **Flat row** — `.kpi-band-row` now `border-radius: 0`, `overflow: visible` — no tile feel.
3. **Subtle dividers** — Explicit `rgba(255,255,255,0.08)` dark / `rgba(0,0,0,0.06)` light borders instead of `var(--band-border)`.
4. **Subtle hover** — `rgba(255,255,255,0.03)` dark / `rgba(0,0,0,0.02)` light — barely visible, not button-group-like.
5. **Light-mode parity** — Per-theme overrides for cell borders, hover, and responsive border-top.

### 2026-02-28 — PR #25: Dashboard KPI band (Provider-style)
Replaced 5 separate KPI tiles with a single Provider-style band row.

1. **KPI band row** — `.kpi-band` + `.kpi-band-row` 5-column grid replaces `.metrics-row` of individual `.metric` cards. One calm container, equal columns, vertical dividers via `border-right`.
2. **Cell anatomy** — `.kpi-cell-label` (tiny uppercase), `.kpi-cell-value` (2.25rem/800 weight), `.kpi-cell-sub` (muted subtext). Color classes: `.kpi-pos`, `.kpi-neg`, `.kpi-warn`.
3. **Drill links preserved** — Spend → expense, Income → income, Needs Review → uncategorized. Net and Latest remain static (no link).
4. **Subtext line** — Spend shows txn count, Net shows "period net", Needs Review shows "uncategorized", Latest shows "last activity".
5. **Responsive** — 5 cols → 2 cols at ≤900px → 1 col at ≤480px with border-top dividers.
6. **Old styles untouched** — `.metric`, `.metrics-row` CSS kept for other pages; just stopped using them in dashboard.

### 2026-02-28 — PR #24: Design language shift — Provider Performance style
Banded groups, segmented controls, chart wells, and Provider-style typography across the dashboard.

1. **CSS tokens** — Added `--band-bg`, `--band-border`, `--band-shadow`, `--chart-well-bg`, `--seg-bg`, `--seg-border`, `--seg-active-bg`, `--seg-active-text` per theme. Plus `--radius-xl` (18px), `--label-tracking` (0.08em).
2. **Band component** — `.band` wrapper with subtle border/bg/shadow and `.band-label` floating pill (absolute positioned, uppercase, 0.68rem). Dashboard sections wrapped in 4 bands: Overview, Activity, Spending, Recurring.
3. **Chart well** — `.chart-well` inner surface with `--chart-well-bg` background, applied around donut chart SVG.
4. **Segmented controls** — Unified `.segmented` component (inline-flex, 12px radius, 30px items). Dashboard filter chips, sidebar entity toggle, and reports period toggle all use segmented tokens (`--seg-bg`, `--seg-active-bg`).
5. **Typography** — KPI labels: 0.68rem weight 700 with `--label-tracking`. KPI values: 1.7rem weight 800. Section titles: 0.88rem weight 800.
6. **Interaction polish** — Softened `--shadow-hover` (dark: 0.18 alpha vs 0.3). Increased `.dash-grid` gap to 1.2rem for band label clearance.
7. **Light-mode parity** — Segmented chip overrides for both themes. Light-mode band/well tokens use subtle `rgba(0,0,0,...)` values.

### 2026-02-28 — PR #23: Sidebar redesign (Apple-ish) + Workflows collapsed by default
Calmer sidebar with clear hierarchy, collapsible workflows, Apple-ish styling.

1. **Section grouping** — Sidebar split into Brand, Entity toggle, Primary nav (4 links), collapsible Workflows (5 steps), Theme toggle. New `.sb-*` class prefix.
2. **Segmented control polish** — Taller (34px), larger radius (12px), CSS-only form styling (no inline styles).
3. **Active indicator** — Primary nav active state uses 3px blue left bar (`::before` pseudo-element) + soft background.
4. **Collapsible Workflows** — "Workflows" header with rotating chevron, collapsed by default, state persisted via `localStorage("sidebar_workflows_open")`.
5. **Calmer brand** — Smaller title (1.3rem vs 1.55rem), subtle `.sb-divider` elements replace `<hr>` tags.
6. **Accessibility** — `aria-expanded` + `aria-controls` on toggle button, focus-visible rings on all elements.

### 2026-02-28 — PR #21: Donut layout sizing + Apple-ish polish
Bigger donut, tighter legend, softer slices, bidirectional hover linking.

1. **Larger donut** — Increased from 200×200 to 300×300px desktop (220px tablet, 180px mobile) via `.donut-chart-wrap--lg` modifier. Center text bumped to 1.35rem.
2. **Compact legend** — `.donut-legend-list` scoped overrides reduce row padding (0.55rem vs 0.75rem), font sizes (0.85rem), and radius (14px) for tighter scannable rows.
3. **Softer slices** — `stroke-linecap: round` for smooth edges, base opacity 0.92, wider gap (0.8% vs 0.5%). Track ring uses subtle rgba stroke instead of 50% opacity.
4. **Hover pop** — Slices brighten to full opacity, expand stroke-width to 34, and add `drop-shadow` on hover. 120ms transition for smooth feel.
5. **Slice ↔ legend linking** — `data-donut-key` attributes on slices and legend rows. Tiny JS wires mouseenter/mouseleave to add `.is-hover` class on matching elements. Hovering a slice highlights the legend row; hovering a legend row highlights the slice.
6. **Light theme** — Track ring uses `rgba(0,0,0,0.05)` in light mode.

### 2026-02-28 — PR #20: Dashboard single date pill (presets)
Replaced two native date inputs with a compact pill + popover.

1. **Date pill** — Single button showing "Feb 1–28" replaces two `<input type="date">` pickers. Reuses `.dhdr-pill` class.
2. **Preset popover** — Last 7 days, Last 30 days, This month, Last month computed in JS. Selection writes hidden `start`/`end` inputs and triggers `form.requestSubmit()` for HTMX update.
3. **Custom dates** — "Custom…" reveals inline date inputs + Apply button inside the popover.
4. **Label formatting** — `fmtRange()` shows "Feb 1–28" (same month) or "Feb 1 – Mar 15" (cross-month) with thin-space en-dash.
5. **Coexistence** — Popover uses `hidden` attribute (not `.open` class), so saved views Escape/click-outside handlers don't conflict.
6. **Responsive** — Pill takes full width on mobile ≤480px.

### 2026-02-28 — PR #16: Saved Views overflow menu
Collapsed 6 flat saved-views buttons into a compact layout.

1. **Overflow menu** — Rename, Make Default, Clear Default, and Delete moved into a "⋯" popover menu. Select, Save As, and Update remain visible.
2. **Keyboard accessible** — `aria-haspopup`, `role="menu"`/`role="menuitem"`, closes on Escape.
3. **Outside click close** — Document-level click listener closes open menus when clicking outside `.sv-menu-wrap`.
4. **Danger styling** — Delete menu item uses `--red` color with red-tinted hover background.
5. **Simplified enable/disable** — `_svEnableActions()` now only toggles Update and "⋯" trigger (menu items don't need individual disable since the trigger gates access).
6. **Both pages** — Applied identically to dashboard and transactions saved views rows.

### 2026-02-28 — PR #15: Filter bar + saved views light-mode polish
CSS-only light-theme refinements for the filter bar area.

1. **Control height alignment** — Standardized inputs and buttons to 34px in the filter bar (scoped to `.txn-filter-bar` and `.txn-chips` to avoid affecting pagination/inline-edit buttons).
2. **Tighter spacing** — Filter bar padding reduced to 0.6rem, form-row gap to 0.35rem.
3. **Lighter inactive chips** — Softer border/fill/text for iOS pill feel; subtle hover state.
4. **Softer secondary buttons** — Filter bar `.btn-secondary` uses gray text (not blue) so Apply stays the clear primary action.
5. **Saved views row separator** — Subtle top border between chips row and saved views row.
6. **Airy sticky shadow** — Replaced heavy `--shadow-card` with lighter shadow on the sticky filter bar.

### 2026-02-28 — PR #14: Light-theme parity pass (dashboard-specific)
CSS-only dashboard fixes for light mode.

1. **Active chip text fix** — Changed `.txn-chip.active` from `color: #fff` (invisible on light blue) to `color: var(--blue)` + `font-weight: 600`.
2. **`--shadow-hover` variable** — Added to both theme blocks for theme-aware hover shadows. Dark: heavy (0.3 alpha), Light: subtle (0.08 alpha).
3. **Metric hover shadow** — `a.metric-link:hover` now uses `var(--shadow-hover)` instead of hardcoded value.
4. **Softer chart gradients** — Light-mode chart bars use `#5eaeff → #007aff` (less neon than dark mode's `#4da8ff → #0a84ff`).
5. **KPI card borders** — Light-mode metrics get `1px solid var(--border)` for definition on white background.
6. **Section titles** — Bolder weight (700) and `--text-secondary` color in light mode.
7. **Filter bar/input borders** — Visible 1px borders on inputs and filter bar in light mode.
8. **Select arrow contrast** — Arrow stroke darkened from `#999` to `#666` in light mode.

### 2026-02-28 — PR #13: Theme toggle (Light/Dark) + light-theme mockup parity
Major CSS refactoring to add persistent Light/Dark theme toggle. Dark remains default.

1. **CSS variable architecture** — Refactored `:root` into theme-invariant tokens + `:root[data-theme="dark"]` + `:root[data-theme="light"]`. ~30 intermediate variables per theme (hover-bg, control-bg, chip-bg, chart-text, chevron-color, scrollbar-thumb, toggle-shadow, input-sm-bg, btn-icon-bg, editing-bg, etc.).
2. **Replaced all hardcoded rgba** — Every hardcoded `rgba(255,255,255,...)` and `rgba(0,0,0,...)` throughout the CSS replaced with theme-aware variables.
3. **Flash prevention** — Inline `<script>` in `<head>` before CSS link reads `localStorage` and sets `data-theme` attribute before any styles load.
4. **Toggle UI** — Moon/sun button at bottom of sidebar, `toggleTheme()` function, `_syncThemeUI()` single source of truth for icon/label sync.
5. **Light theme tokens** — `--bg: #f4f6f9`, `--bg-card: #ffffff`, `--text: #1d1d1f`, `--shadow-card` with subtle values, `color-scheme: light`, `--date-icon-filter: none`.
6. **meta theme-color** — Dynamically updated on toggle (`#f4f6f9` light, `#000000` dark).

### 2026-02-27 — PR #9: Upcoming Recurring alignment
Tweaked existing recurring detection to match target spec.

1. **Lookback 365→90 days** — `_detect_recurring()` now queries last 90 days instead of 365 for faster, more relevant pattern detection.
2. **Min occurrences 3→2** — Lowered threshold so bimonthly or new recurring charges surface sooner.
3. **Max items 10→6** — Caps the Upcoming card to 6 items for a cleaner dashboard.
4. **Account filter** — Recurring queries now respect the dashboard account filter (`params.account`), so switching accounts shows only that account's patterns.
5. **Date-windowed drill links** — Each upcoming item links to `/transactions` filtered by merchant + ±7 day window around expected date (via `drill_start`/`drill_end` fields).
6. **Heuristic docstring** — Added summary comment block above `_detect_recurring()` documenting the full algorithm.

### 2026-02-27 — PR #8: Dashboard UX polish
Loading state, Insights card, section cleanup.

1. **HTMX loading indicator** — `htmx:beforeRequest`/`afterRequest`/`responseError` event listeners toggle `.dash-loading` class on `#dashboard-body` (opacity fade + pointer-events disabled during filter changes).
2. **Insights card** — `_compute_insights()` generates up to 3 contextual insights: largest category increase vs prior period, new merchants, large transactions (>$500). Each links to a `/transactions` drill-down.
3. **Section title cleanup** — Replaced 5 inline `<h2 style="...">` with `.dash-section-title` CSS class for consistency.
4. **Empty state improvement** — Added emoji icon + descriptive text + CTA button linking to transactions with current filter params.
5. **Wrapper div cleanup** — Removed 4 unnecessary `<div style="margin-top:...">` wrappers from dashboard body template.
6. **Empty entity smoke test** — Added BFM entity test to catch crashes when an entity has zero data.

### 2026-02-27 — Reports page redesign
Complete rewrite of the reports page from a single-section Plotly-based layout to a two-section pure CSS layout.

1. **Removed Plotly** — Replaced Plotly.js bar chart with pure HTML/CSS bars. `border-radius: 7px` pill-shaped bars, blue gradient fill, spring animation. Plotly 2.27.0 didn't support `cornerradius`, so bars were always square.
2. **Two-section layout** — Top: monthly detail (month navigator + stat cards + category breakdown + drill-down). Bottom: spending trend (period toggle + bar chart).
3. **Month navigator** — Prev/next arrows flanking full month name ("February"). Replaces the confusing start/end range picker + detail month dropdown.
4. **Period segmented control** — Apple-style [ 3M | 6M | 1Y | 2Y ] toggle. Chart scales bar width/spacing per period. Value labels hidden at 24M. Responsive label thinning on mobile.
5. **Date formatting** — All `YYYY-MM` and `YYYY-MM-DD` formats replaced with human-friendly: "February", "Feb 25", "Feb 15". Year omitted when current year. Helper functions in `reports.py`.
6. **Selected month highlight** — The month selected in the top section gets a brighter blue bar + blue label in the trend chart, visually connecting the two sections.
7. **URL simplification** — Replaced `?start=&end=&detail=` with `?month=&period=`. Cleaner, bookmarkable, no confusing overlap.

### 2026-02-26 — Apple-style UI overhaul
Complete visual redesign targeting Apple iOS/macOS dark mode aesthetic. Branch: `claude/review-code-testing-w9VVE`.

1. **style.css rewrite** — True black `#000` background, SF Pro font stack (`-apple-system, BlinkMacSystemFont, "SF Pro Display"`), 0.5px hairline borders, `border-radius: 16px` cards, segmented entity toggle control, `backdrop-filter` vibrancy effects, `cubic-bezier(0.32, 0.72, 0, 1)` spring animations.
2. **Responsive mobile layout** — CSS Grid metrics row, hamburger menu at ≤768px, sidebar slides in from left with scrim overlay, three breakpoints (1024px, 768px, 400px).
3. **Accessibility** — Skip-to-content link, `aria-label="Main navigation"` on sidebar, `aria-expanded` on hamburger, `:focus-visible` blue rings on all interactive elements, `role="alert"` on flash messages.
4. **base.html restructure** — Added `<meta name="theme-color" content="#000000">`, `<meta name="color-scheme" content="dark">`, mobile header with hamburger SVG, scrim div, `toggleSidebar()`/`closeSidebar()` JS, auto-close sidebar on mobile nav click.

### 2026-02-26 — Second code review pass (6 more bugs)
Continued review after initial fixes. All routes tested via Flask test client with populated databases.

1. **Bug: `pd.read_json()` crashes on pandas 2.x** — `upload.py` passed raw JSON strings to `pd.read_json()`, which in pandas 2.x interprets strings as file paths, causing `OSError: File name too long`. Fixed by wrapping with `io.StringIO()`. Also added Timestamp-to-string conversion for `date`/`imported_at` columns that `read_json` auto-parses.
2. **Bug: Dashboard income always $0** — `dashboard.py` income query used `strftime('%%Y-%%m', date)` which produces literal `%Y-%m` text in SQLite instead of formatting the date. Fixed to `strftime('%Y-%m', date)`.
3. **XSS: categorize.html JS subcategory builder** — `_buildOptions()` injected subcategory names directly into innerHTML without escaping. Added `_escapeHtml()` helper using DOM text node.
4. **XSS: plaid.html disconnect confirm** — Institution name injected directly into `onsubmit="return confirm('...')"` attribute. Fixed with `|tojson` filter.
5. **Security: open redirect in `/set-entity`** — `redirect` form field accepted arbitrary URLs. Added validation to only allow relative paths (blocks `//evil.com`).
6. **Missing dependency: openpyxl** — `core/henryschein.py` uses `pd.read_excel()` which requires openpyxl, but it wasn't in `requirements.txt`. Added `openpyxl>=3.1.0`.

### 2026-02-26 — End-to-end code review fixes
Full review of all routes, templates, and core modules. Smoke test passing. Fixes:

1. **Bug: `add_alias` active checkbox ignored** — `categorize.py:349` had `1 if ... else 1`, always setting `active=1` regardless of checkbox state. Fixed to `1 if ... else 0`.
2. **Bug: `rename_category` orphaned subcategories and vendor orders** — Renaming a category updated `categories`, `transactions`, and `merchant_aliases` but not `subcategories.category_name` or `amazon_orders.category`. Added both UPDATE statements.
3. **Bug: `delete_category` orphaned subcategories** — Deleting a category left orphan rows in `subcategories`. Added `DELETE FROM subcategories WHERE category_name=?`.
4. **XSS: unescaped HTML in subcategory option endpoints** — Both `/categorize/subcategories` and `/categorize-vendors/subcategories` rendered user-provided names directly into `<option>` tags without escaping. Added `markupsafe.escape()`.
5. **XSS: unescaped values in JS contexts** — `categorize.html` delete confirm and alias prefill injected category/description into JS strings without proper escaping. Fixed with `|tojson` filter.
6. **Bug: CSV export Content-Disposition header** — Filename not quoted, causing download issues when category names contain spaces. Added quotes around filename.

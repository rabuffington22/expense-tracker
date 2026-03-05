# Expense Tracker

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
- **Seed script:** `scripts/seed_demo_data.py` — ~800 personal + ~570 business transactions, accounts, recurring, categories

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
    reports.py                     # GET /reports (monthly detail + spending trend)
    ai.py                          # POST /ai/ask, /ai/clear (global Ask Opus chat, per-page context)
    plaid.py                       # GET/POST /plaid (connect, sync, disconnect)
    saved_views.py                 # POST /saved-views (CRUD for filter presets)
    upload.py                      # GET/POST /upload (bank statement import)
    vendors.py                     # GET/POST /vendors (Amazon CSV, Henry Schein XLSX)
    match.py                       # GET/POST /match (link orders to bank txns)
    categorize_vendors.py          # GET/POST /categorize-vendors (label vendor orders)
    categorize.py                  # GET/POST /categorize (remaining txns + settings)
  templates/
    base.html                      # Layout: sidebar + main content, mobile header/hamburger
    components/
      sidebar.html                 # Entity toggle + primary nav (ARIA nav landmark)
      dashboard_body.html          # Dashboard main content (HTMX swap target)
      kpi_panel.html               # KPI compare panel (left/right)
      categories_compare.html      # Categories comparison bar chart
      insights_upcoming.html       # Insights + Upcoming recurring side-by-side
      ai_analysis.html             # AI analysis results partial
      txn_results.html             # Transaction list results (HTMX swap target)
      txn_row.html                 # Single transaction row
      txn_row_edit.html            # Inline-edit transaction row
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
    reports.html                   # Two-section layout: monthly detail + spending trend
    plaid.html                     # Connected Accounts (Plaid Link)
    upload.html                    # Import tab + Settings tab
    upload_dialog.html             # File upload + preview/confirm
    vendors.html                   # Upload + date filter + save
    match.html
    categorize_vendors.html
    categorize.html                # Review tab + Settings tab
  static/
    style.css                      # Apple-style dual theme (dark default + light), CSS custom properties on data-theme, SF Pro fonts
    htmx.min.js                    # HTMX library (~14KB)
core/                              # Business logic
  db.py                            # Schema migrations (38 so far), DB init, connections
  ai_client.py                     # OpenRouter API client (Claude via OpenRouter for AI features)
  imports.py                       # CSV/PDF parsing, normalization, dedup
  categorize.py                    # Alias matching, keyword heuristics
  amazon.py                        # Amazon order CSV parsing + vendor order matching
  henryschein.py                   # Henry Schein XLSX parsing
  plaid_client.py                  # Plaid API client (link, sync, liabilities)
  reporting.py                     # Query helpers for Reports page
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
- **Reports** -- Monthly detail + spending trend (pure CSS bar chart)
- **Connected Accounts** -- Plaid Link, sync, disconnect

### 5-Step Workflow (linked from To Do page)
1. **Upload from Bank/CC** -- Import CSV/PDF bank statements
2. **Upload from Vendors** -- Upload Amazon/Henry Schein order data
3. **Match** -- Link vendor orders to bank transactions
4. **Categorize Vendors** -- Label each vendor order with category/subcategory
5. **Categorize Remaining** -- Review + categorize remaining bank transactions

Workflow pages removed from sidebar in PR #23 redesign; now accessible via To Do page Workflows section.

## Database (38 Migrations)
Key tables:
- **`transactions`** -- Main ledger. PK = SHA-256(date, amount, description)[:24]. Negative amount = debit.
- **`categories`** -- Per-entity categories. Personal: 24 categories. BFM: 29 categories. Every category has a "General" subcategory.
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

**Insights Card:** Up to 3 auto-generated insights computed by `_compute_insights()`:
- Category spend increase vs prior period (>$50, ≥2 txns)
- New merchants this period (not seen in prior 90 days)
- Large transactions over $500
Each insight links to a drill-down in `/transactions`.

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

- **Ask Opus** (global chat modal) — Available on every page via "Ask Opus" button. Uses `anthropic/claude-opus-4.6` via `web/routes/ai.py`. Each page sends page-specific financial context (planning data, spending trends, transaction patterns, subscription costs, account balances, etc.). Conversation persists per entity+page in `/tmp/expense-tracker-ai/`. System prompt adapts per page (financial advisor on Planning, spending analyst on Dashboard, etc.). Modal lives in `base.html`, JS function `aiChatOpen('pagename')` sets context. Button styled as deep navy (`#001a3a`) with light blue (`#14a9f8`) ring.
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

## Change Log

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
3. **`scripts/seed_demo_data.py`** — Generates realistic fake data for 2 entities. Personal: ~800 transactions, 5 accounts (2 bank + 3 credit), 2 manual recurring, 19 categories with 125 subcategories. Business: ~570 transactions, 4 accounts (3 bank + 1 credit), 2 manual recurring, 14 categories with 76 subcategories. Business merchants: Staples, Adobe, Zoom, Delta, ADP, Google Ads, etc.
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

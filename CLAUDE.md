# Expense Tracker

## What This Is
Flask + HTMX + SQLite personal/business expense tracker. Runs locally on Atlas Mac Mini. Bank and credit card transactions sync automatically via Plaid API (connected accounts). CSV/PDF bank statement import retained as fallback. Vendor order data (Amazon CSV, Henry Schein XLSX) matched to bank transactions for real product names.

Previously built on Streamlit — migrated to Flask + HTMX to eliminate WebSocket disconnect issues during interactive workflows.

## Three Entities (Fully Isolated)
- **Personal** -> `personal.sqlite`
- **BFM** (company) -> `company.sqlite`
- **LL** (Luxe Legacy) -> `luxelegacy.sqlite`

Each has its own DB, categories, aliases, import checklists. Entity selected via sidebar toggle.

## Key Paths
- **Repo (Home Mac):** `/Users/ryanbuffington/expense-tracker`
- **Repo (Atlas):** `~/expense-tracker`
- **DB location (Atlas):** `~/expense-tracker/local_state/` (default -- no `DATA_DIR` set)
- **Python (Atlas):** Homebrew, venv at `~/expense-tracker/.venv`
- **App URL:** `http://192.168.3.10:8501` (LAN) or `http://100.79.127.29:8501` (Tailscale)

## Plaid Integration
- **Status:** Production access submitted 2026-02-26, in review. Sandbox available now.
- **Plaid app name:** BFM Expense Tracker (Plaid dashboard)
- **Client ID:** `69a02460632219000ea2ea03`
- **Env vars required:** `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV` (sandbox|development|production)
- **Current deploy:** Running in sandbox mode (`PLAID_ENV=sandbox`)
- **Sandbox test creds:** username `user_good`, password `pass_good`
- **Connected Accounts page:** `/plaid/` — connect banks, sync, disconnect
- **Sync:** Manual only (no auto-sync on startup) — POST `/plaid/sync`
- **Migration 18:** Added `plaid_items`, `plaid_accounts` tables + `plaid_item_id` on transactions
- **To switch to production:** Update `PLAID_SECRET` to production secret and set `PLAID_ENV=production`, then restart gunicorn

## Deploy with Plaid (Full Restart)
```bash
ssh Atlas@192.168.3.10 "cd ~/expense-tracker && git pull origin main && .venv/bin/pip install plaid-python -q && pkill -9 -f gunicorn; sleep 2 && PLAID_CLIENT_ID=69a02460632219000ea2ea03 PLAID_SECRET=<secret> PLAID_ENV=sandbox OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES nohup .venv/bin/gunicorn -w 1 -b 0.0.0.0:8501 --timeout 120 --access-logfile - 'web:create_app()' > /tmp/flask.log 2>&1 &"
```

> **DATA_DIR pitfall:** Do NOT pass `DATA_DIR` to deploy commands -- keep everything on `local_state/`.

## Deploy to Atlas
```bash
# Full restart (use after requirements.txt changes or if gunicorn is dead)
ssh Atlas@192.168.3.10 "cd ~/expense-tracker && git pull origin main && pkill -9 -f gunicorn; sleep 2 && OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES nohup .venv/bin/gunicorn -w 1 -b 0.0.0.0:8501 --timeout 120 --access-logfile - 'web:create_app()' > /tmp/flask.log 2>&1 &"
```

```bash
# Graceful reload (use for code-only changes -- workers restart without downtime)
ssh Atlas@192.168.3.10 "cd ~/expense-tracker && git pull origin main && pkill -HUP -f gunicorn"
```

Notes:
- `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` required on macOS for gunicorn fork()
- `--timeout 120` needed because matching algorithm can take >30s
- Single worker (`-w 1`) because SQLite doesn't support concurrent writers
- If LAN times out, try Tailscale IP `100.79.127.29`

## Directory Structure
```
web/                               # Flask app (replaced old app/ Streamlit code)
  __init__.py                      # Flask app factory, entity cookie, before_request hook
  routes/                          # Route blueprints (one per page)
    dashboard.py                   # GET /
    upload.py                      # GET/POST /upload  (bank statement import)
    vendors.py                     # GET/POST /vendors (Amazon CSV, Henry Schein XLSX)
    match.py                       # GET/POST /match   (link orders to bank txns)
    categorize_vendors.py          # GET/POST /categorize-vendors (label vendor orders)
    categorize.py                  # GET/POST /categorize (remaining txns + settings)
    reports.py                     # GET /reports (monthly detail + spending trend)
  templates/
    base.html                      # Layout: sidebar + main content, mobile header/hamburger, skip-link, scrim overlay
    components/
      sidebar.html                 # Entity toggle + numbered nav steps (ARIA nav landmark)
      card.html                    # Vendor order card (HTMX swap target)
      match_card.html              # Match review card (HTMX swap target)
      flash.html                   # Success/error flash messages
    dashboard.html
    upload.html                    # Import tab + Settings tab
    upload_dialog.html             # File upload + preview/confirm
    vendors.html                   # Upload + date filter + save
    match.html
    categorize_vendors.html
    categorize.html                # Review tab + Settings tab
    reports.html                   # Two-section layout: monthly detail + spending trend
  static/
    style.css                      # Apple-style dual theme (dark default + light), CSS custom properties on data-theme, SF Pro fonts
    htmx.min.js                    # HTMX library (~14KB)
core/                              # Business logic (unchanged from Streamlit era)
  db.py                            # Schema migrations (20 so far), DB init, connections
  imports.py                       # CSV/PDF parsing, normalization, dedup
  categorize.py                    # Alias matching, keyword heuristics
  amazon.py                        # Amazon order CSV parsing + vendor order matching
  henryschein.py                   # Henry Schein XLSX parsing
  reporting.py                     # Query helpers for Reports page
run.py                             # Entry point: python run.py (dev mode)
requirements.txt                   # flask, gunicorn, pandas, plotly, pdfplumber, etc.
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

## 5-Page Workflow (sidebar order)
1. **Upload from Bank/CC** -- Import CSV/PDF bank statements
2. **Upload from Vendors** -- Upload Amazon/Henry Schein order data
3. **Match** -- Link vendor orders to bank transactions
4. **Categorize Vendors** -- Label each vendor order with category/subcategory
5. **Categorize Remaining** -- Review + categorize remaining bank transactions

Plus **Dashboard** and **Reports** pages.

## Database (20 Migrations)
Key tables:
- **`transactions`** -- Main ledger. PK = SHA-256(date, amount, description)[:24]. Negative amount = debit.
- **`categories`** -- Seeded defaults (Kids, Household, Health & Beauty, Clothing, Pet Supplies, Office, Kristine Business, etc.)
- **`subcategories`** -- Two-level categorization (Migration 15). Each subcategory belongs to a parent category. "Unknown" always available.
- **`merchant_aliases`** -- Pattern-based auto-categorization (contains/regex -> merchant + category)
- **`import_profiles`** -- Saved CSV column mappings per bank (Amex, Chase, Capital One, Citi, BofA)
- **`import_checklist` / `import_checklist_status`** -- Monthly source tracking
- **`amazon_orders`** -- Vendor orders for deferred matching. `matched_transaction_id` tracks matches. Has `category`/`subcategory` (Migration 16) and `vendor` (Migration 17, default `'amazon'`). Stores both Amazon and Henry Schein orders.

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
flask, gunicorn, pandas, pdfplumber, python-dateutil, openpyxl, plaid-python

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

## Change Log

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

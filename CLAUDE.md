# Expense Tracker

## What This Is
Flask + HTMX + SQLite personal/business expense tracker. Runs locally on Atlas Mac Mini. No cloud sync, no bank linking — CSV/PDF bank statements uploaded manually, categorized via alias rules and keyword heuristics. Vendor order data (Amazon CSV, Henry Schein XLSX) matched to bank transactions for real product names.

Previously built on Streamlit — migrated to Flask + HTMX to eliminate WebSocket disconnect issues during interactive workflows.

## Two Entities (Fully Isolated)
- **Personal** -> `personal.sqlite`
- **BFM** (company) -> `company.sqlite`

Each has its own DB, categories, aliases, import checklists. Entity selected via sidebar toggle.

## Key Paths
- **Repo (Home Mac):** `/Users/ryanbuffington/expense-tracker`
- **Repo (Atlas):** `~/expense-tracker`
- **DB location (Atlas):** `~/expense-tracker/local_state/` (default -- no `DATA_DIR` set)
- **Python (Atlas):** Homebrew, venv at `~/expense-tracker/.venv`
- **App URL:** `http://192.168.3.10:8501` (LAN) or `http://100.79.127.29:8501` (Tailscale)

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
    reports.py                     # GET /reports (charts, drill-down, CSV export)
  templates/
    base.html                      # Layout: sidebar + main content, dark theme
    components/
      sidebar.html                 # Entity toggle + numbered nav steps
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
    reports.html                   # Plotly charts + drill-down tables
  static/
    style.css                      # Dark theme (#1c1c1e bg, white text)
    htmx.min.js                    # HTMX library (~14KB)
core/                              # Business logic (unchanged from Streamlit era)
  db.py                            # Schema migrations (17 so far), DB init, connections
  imports.py                       # CSV/PDF parsing, normalization, dedup
  categorize.py                    # Alias matching, keyword heuristics
  amazon.py                        # Amazon order CSV parsing + vendor order matching
  henryschein.py                   # Henry Schein XLSX parsing
  reporting.py                     # Query helpers for Reports page
run.py                             # Entry point: python run.py (dev mode)
requirements.txt                   # flask, gunicorn, pandas, plotly, pdfplumber, etc.
```

## HTMX Interactions
- **Card queue (Categorize Vendors):** Save/Skip buttons use `hx-post` + `hx-target` to swap just the card div
- **Match review:** Accept/Skip swap the match card via HTMX partial
- **Category dropdowns:** `hx-get` to fetch subcategories when category changes
- **File uploads:** Standard form POST, returns full page with results
- **Reports chart:** Plotly JSON rendered client-side via `plotly-2.27.0.min.js`

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

## Database (17 Migrations)
Key tables:
- **`transactions`** -- Main ledger. PK = SHA-256(date, amount, description)[:24]. Negative amount = debit.
- **`categories`** -- Seeded defaults (Baby & Kids, Household, Health & Beauty, Clothing, Pet Supplies, Office, Kristine Business, etc.)
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
- Dark theme with `color-scheme: dark` on date inputs for calendar picker visibility

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
flask, gunicorn, pandas, plotly, pdfplumber, python-dateutil, openpyxl

## Change Log

### 2026-02-26 — End-to-end code review fixes
Full review of all routes, templates, and core modules. Smoke test passing. Fixes:

1. **Bug: `add_alias` active checkbox ignored** — `categorize.py:349` had `1 if ... else 1`, always setting `active=1` regardless of checkbox state. Fixed to `1 if ... else 0`.
2. **Bug: `rename_category` orphaned subcategories and vendor orders** — Renaming a category updated `categories`, `transactions`, and `merchant_aliases` but not `subcategories.category_name` or `amazon_orders.category`. Added both UPDATE statements.
3. **Bug: `delete_category` orphaned subcategories** — Deleting a category left orphan rows in `subcategories`. Added `DELETE FROM subcategories WHERE category_name=?`.
4. **XSS: unescaped HTML in subcategory option endpoints** — Both `/categorize/subcategories` and `/categorize-vendors/subcategories` rendered user-provided names directly into `<option>` tags without escaping. Added `markupsafe.escape()`.
5. **XSS: unescaped values in JS contexts** — `categorize.html` delete confirm and alias prefill injected category/description into JS strings without proper escaping. Fixed with `|tojson` filter.
6. **Bug: CSV export Content-Disposition header** — Filename not quoted, causing download issues when category names contain spaces. Added quotes around filename.

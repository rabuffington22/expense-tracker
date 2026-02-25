# Expense Tracker — Project Knowledge

> Comprehensive reference for Claude project context. Last updated: 2026-02-25.

---

## Overview

A **Streamlit + SQLite** personal/business expense tracker that runs locally on Atlas Mac Mini. No cloud sync, no bank linking — CSV and PDF bank statements are uploaded manually, categorized via alias rules and keyword heuristics, and analyzed with monthly reports. Amazon order CSVs can be uploaded separately and matched to bank transactions to get real product names.

**Two fully separate entities** with isolated SQLite databases:
- **Personal** → `personal.sqlite`
- **BFM** (company) → `company.sqlite`

---

## Infrastructure

| Item | Value |
|------|-------|
| **GitHub repo** | `rabuffington22/atlas-dashboard` ... no, `rabuffington22/expense-tracker` (private) |
| **Host** | Atlas Mac Mini (`Atlas@100.79.127.29` via Tailscale) |
| **App URL (LAN)** | `http://192.168.3.10:8501` |
| **App URL (Tailscale)** | `http://100.79.127.29:8501` |
| **Repo on Atlas** | `~/expense-tracker` |
| **Data on Atlas** | `~/expense-data` (set via `DATA_DIR` env var) |
| **Python** | Homebrew `/opt/homebrew/bin/python3`, venv at `~/expense-tracker/.venv` |
| **Repo on Home Mac** | `/Users/ryanbuffington/expense-tracker` |
| **Streamlit theme** | Dark, Apple-style (`#1c1c1e` bg, `#0a84ff` primary) |

### Deploy Command

```bash
ssh Atlas@100.79.127.29 "cd ~/expense-tracker && git pull origin main && pkill -9 -f 'streamlit run' ; sleep 3 && cd ~/expense-tracker && nohup /Users/atlas/expense-tracker/.venv/bin/streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501 > /tmp/streamlit.log 2>&1 & sleep 3 && tail -5 /tmp/streamlit.log"
```

Just push to `main` and run the above. There's also a launchd service (`com.expense-tracker.streamlit`) for auto-start on boot.

---

## Directory Structure

```
expense-tracker/
├── app/
│   ├── main.py              # Streamlit multi-page router
│   ├── shared.py            # Entity selector, helpers
│   └── pages/
│       ├── 0_Dashboard.py   # Quick stats, import progress
│       ├── 1_Upload.py      # Source-by-source CSV/PDF import
│       ├── 2_Categorize.py  # Review suggestions, Amazon match, settings
│       └── 3_Reports.py     # Monthly charts, drill-down, CSV export
├── core/
│   ├── db.py                # Schema migrations, DB init, connections
│   ├── imports.py           # CSV/PDF parsing, normalization, dedup
│   ├── categorize.py        # Alias matching, keyword heuristics
│   ├── amazon.py            # Amazon order CSV parsing + matching
│   └── reporting.py         # Query helpers for Reports page
├── fixtures/                # Test CSVs for smoke test
├── scripts/
│   ├── setup-atlas.sh       # One-time Atlas setup (venv, launchd)
│   ├── smoke_test.py        # Automated verification
│   └── com.expense-tracker.streamlit.plist
├── .streamlit/config.toml
├── requirements.txt         # streamlit, pandas, plotly, pdfplumber, python-dateutil
└── .gitignore
```

**Not in repo (gitignored):** `local_state/`, `*.sqlite`, `uploads/`, `backups/`, `statements/`, `.venv/`

---

## Database Schema (13 Migrations)

All migrations are additive, tracked via `schema_version` table, applied by `init_db(entity)`.

### Core Tables

**`transactions`** — The main ledger
| Column | Type | Notes |
|--------|------|-------|
| transaction_id | TEXT PK | SHA-256(date, amount, description)[:24] |
| date | TEXT | ISO-8601 (YYYY-MM-DD) |
| description_raw | TEXT | Original bank description |
| merchant_raw | TEXT | |
| merchant_canonical | TEXT | Cleaned merchant name |
| amount | REAL | Signed (negative = debit) |
| currency | TEXT | Default 'USD' |
| account | TEXT | |
| category | TEXT | FK to categories.name |
| confidence | REAL | 0.0–1.0 (1.0 = user-confirmed) |
| notes | TEXT | Free text; Amazon product name goes here |
| source_filename | TEXT | Which file it came from |
| imported_at | TEXT | ISO timestamp |

**`categories`** — Category list (defaults seeded on init)
- Groceries, Dining, Transportation, Utilities, Healthcare, Entertainment, Shopping, Travel, Housing, Income, Transfers, Fees, Subscriptions, Home Improvement, Pet Supplies, Personal Care, Other

**`merchant_aliases`** — Pattern-based categorization rules
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| pattern_type | TEXT | 'contains' or 'regex' |
| pattern | TEXT | Match string |
| merchant_canonical | TEXT | Cleaned name to assign |
| default_category | TEXT | Category to assign |
| active | INTEGER | 1 = enabled |

**`import_profiles`** — Saved CSV column mappings per bank/issuer
- date_col, description_col, amount_col, merchant_col, account_col, currency_col
- amount_negate (boolean), date_format (e.g. 'MM/DD/YYYY')
- Defaults: Amex CC, Bank Checking, Capital One, Citi CC, BofA CC, BofA Checking

**`import_checklist`** — Monthly sources to import per entity
- label, filename_pattern, profile_name, url, notes, sort_order, entity

**`import_checklist_status`** — Tracks which source/month combos are imported
- checklist_item_id, month (YYYY-MM), status, imported_at

**`amazon_orders`** — Persisted Amazon order data for deferred matching
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| order_id | TEXT | Amazon order ID |
| payment_ref_id | TEXT | Business CSV grouping key |
| order_date | TEXT | |
| charge_date | TEXT | Payment date from Business CSV |
| product_summary | TEXT | Concatenated product names |
| amazon_category | TEXT | Amazon's internal category |
| order_total | REAL | Charge amount |
| matched_transaction_id | TEXT | NULL = unmatched |
| imported_at | TEXT | |

---

## Core Modules

### `core/imports.py` — Parsing & Import

- **`parse_csv(path, profile)`** — Handles header detection, column mapping, auto-detection, Debit/Credit merging. Auto-skips bank summary headers.
- **`parse_pdf(path)`** — Best-effort extraction via pdfplumber. Strategy 1: table extraction; Strategy 2: text-based line parsing. Supports many date formats including short dates (MM/DD) with year inference.
- **`normalize_transactions(df, source_filename, profile)`** — Canonical schema, date parsing, amount conversion, stable transaction_id generation.
- **`deduplicate(df, entity)`** / **`commit_transactions(df, entity)`** — Dedup by transaction_id, batch insert.
- **`save_upload(file_bytes, filename)`** — Saves file to `DATA_DIR/uploads/`.

### `core/categorize.py` — Auto-Categorization

Two tiers:
1. **Alias rules** (confidence 0.95) — Checks `merchant_aliases` table for contains/regex matches.
2. **Keyword heuristics** (confidence 0.5–0.8) — Fallback rules for common merchants. Strips platform prefixes (PAYPAL *, VENMO *).

Key functions: `suggest_categories(df, entity)`, `apply_aliases_to_db(entity)`.

36 default alias rules cover: payments, fees, subscriptions (Netflix, Spotify, etc.), dining (Uber Eats, DoorDash, etc.), groceries (Kroger, Whole Foods, etc.), transportation, utilities.

### `core/amazon.py` — Amazon Order Matching

Supports two CSV formats:
- **Amazon Business** — groups by `payment_ref_id` (matches bank charges exactly, handles split shipments)
- **Amazon Privacy Central** — groups by `order_id`

**Multi-pass matching algorithm:**
1. Exact: amount + date within window (confidence 0.95)
2. Amount-only: amount match, any date (confidence 0.80)
3. Multi-order: 2–3 orders summing to transaction amount (confidence 0.75)
4. Date-only: date match, closest amount (confidence 0.50)

**Deferred matching flow:** Upload Amazon CSV → save orders to DB → import bank statements later → run matching against stored orders.

### `core/reporting.py` — Report Queries

`get_monthly_totals()`, `get_category_totals()`, `get_transactions()`, `get_uncategorized()`, `get_available_months()`.

---

## Streamlit Pages

### 0_Dashboard
- "Need Review" count (uncategorized / low-confidence transactions)
- Latest transaction date
- Import progress: last 3 months, source-by-source completion

### 1_Upload (2 tabs)
- **Import tab:** Month selector → source checklist → per-source file upload → preview (count, date range, credits/debits) → auto-rename files → import to DB
- **Settings tab:** Manage monthly sources (add/delete checklist items) + import profiles (add/delete column mappings)

### 2_Categorize (3 tabs)
- **Review tab:** Uncategorized transactions → "Suggest Categories" → editable table → "Accept Changes" (auto-creates aliases for future matching)
- **Amazon Match tab:** Section A uploads Amazon CSV to DB; Section B matches stored orders to bank transactions with editable results
- **Settings tab:** Manage categories (add/delete/rename) + merchant aliases (add/delete, reapply all)

### 3_Reports
- Month range picker → stacked bar chart (spend by category) → category drill-down table → transaction detail → CSV export

---

## Key Design Decisions

1. **Entity isolation** — Personal and BFM have completely separate SQLite DBs, categories, aliases, and import checklists.
2. **Deterministic categorization** — No LLM calls; alias rules + keyword heuristics are fast and predictable. LLM stub is ready but unused.
3. **Stable transaction_id** — SHA-256(date, amount, description_raw)[:24] prevents duplicate imports.
4. **Flexible parsing** — Multiple date formats, auto-header detection, Debit/Credit column merging, PDF text-based fallback.
5. **Amazon deferred matching** — Orders persist in DB independently of bank statements, enabling upload-now/match-later workflow.
6. **WAL mode SQLite** — Concurrent read/write, crash recovery.
7. **All local** — No cloud sync, no bank APIs, no external services. Privacy by design.

---

## Default Import Profiles

| Profile Name | Date Col | Description Col | Amount Col | Notes |
|-------------|----------|-----------------|------------|-------|
| Amex Credit Card | Date | Merchant | Amount | amount_negate=true |
| Bank Checking | Transaction Date | Details | Debit | auto-merge Debit/Credit |
| Capital One | Transaction Date | Description | Debit | auto-merge Debit/Credit |
| Citi Credit Card | Date | Description | Debit | auto-merge, MM/DD/YYYY |
| BofA Credit Card | Posted Date | Payee | Amount | MM/DD/YYYY |
| BofA Checking | Date | Description | Amount | MM/DD/YYYY |

---

## Testing

```bash
# Smoke test (no server needed)
python scripts/smoke_test.py

# Manual: run locally
streamlit run app/main.py
```

The smoke test verifies: DB init, CSV parsing, normalization, import, deduplication, and entity isolation.

---

## Commit History (recent)

```
13c3a30 Persist Amazon orders in DB for deferred matching
78c80ed Support Amazon Business CSV format in order matching
c42180f Add Amazon order CSV matching to Categorize page
4f9c8e1 Auto-generate filename from source label and month on upload
72c2cff Save uploaded files to uploads/ with optional rename
12a6099 Rename DIY category to Home Improvement
ef5ac6d Improve categorization: smarter keywords, prefix stripping, auto-aliases
fbc6c06 Fix parse_pdf to accept file-like objects from Streamlit uploads
```

---

## Pending / Backlog

- **Test Amazon matching end-to-end** with real BFM Amazon Business CSV + bank statements
- **Personal Amazon orders** — waiting for Privacy Central export (can take days)
- **LLM-assisted categorization** — stub exists but not wired up
- **Receipt image parsing** — not started
- **Multi-user support** — not planned (single-user tool)

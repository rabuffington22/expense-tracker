# Expense Tracker

## What This Is
Streamlit + SQLite personal/business expense tracker. Runs locally on Atlas Mac Mini. No cloud sync, no bank linking — CSV/PDF bank statements uploaded manually, categorized via alias rules and keyword heuristics. Amazon order CSVs matched to bank transactions for real product names.

## Two Entities (Fully Isolated)
- **Personal** → `personal.sqlite`
- **BFM** (company) → `company.sqlite`

Each has its own DB, categories, aliases, import checklists. Entity selected via sidebar.

## Key Paths
- **Repo (Home Mac):** `/Users/ryanbuffington/expense-tracker`
- **Repo (Atlas):** `~/expense-tracker`
- **DB location (Atlas):** `~/expense-tracker/local_state/` (default — no `DATA_DIR` set)
- **Python (Atlas):** Homebrew, venv at `~/expense-tracker/.venv`
- **App URL:** `http://192.168.3.10:8501` (LAN) or `http://100.79.127.29:8501` (Tailscale)

> **⚠️ DATA_DIR pitfall:** The launchd plist sets `DATA_DIR=~/expense-data` but manual `nohup` restarts do NOT. Streamlit has been using `local_state/` in practice. Do NOT pass `DATA_DIR` to the reset script or deploy command — keep everything on `local_state/`.

## Deploy to Atlas
```bash
ssh Atlas@192.168.3.10 "cd ~/expense-tracker && git pull origin main && pkill -9 -f 'streamlit run' ; sleep 3 && cd ~/expense-tracker && nohup /Users/atlas/expense-tracker/.venv/bin/streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501 > /tmp/streamlit.log 2>&1 & sleep 3 && tail -5 /tmp/streamlit.log"
```
If LAN times out, try Tailscale IP `100.79.127.29` instead. Just push to `main` and run the above.

## Directory Structure
```
app/
  main.py              # Streamlit multi-page router
  shared.py            # Entity selector, helpers
  pages/
    0_Dashboard.py     # Quick stats, import progress
    1_Upload.py        # Source-by-source CSV/PDF import (modal dialog)
    2_Categorize.py    # Review suggestions, Amazon order upload + categorize, alias settings
    3_Match.py         # Match pre-categorized Amazon orders to bank transactions
    4_Reports.py       # Monthly charts, drill-down, CSV export
core/
  db.py                # Schema migrations (16 so far), DB init, connections
  imports.py           # CSV/PDF parsing, normalization, dedup
  categorize.py        # Alias matching, keyword heuristics
  amazon.py            # Amazon order CSV parsing + matching
  reporting.py         # Query helpers for Reports page
scripts/
  setup-atlas.sh       # One-time Atlas setup
  smoke_test.py        # Automated verification
```

## Database (16 Migrations)
Key tables:
- **`transactions`** — Main ledger. PK = SHA-256(date, amount, description)[:24]. Negative amount = debit.
- **`categories`** — Seeded defaults (Baby & Kids, Household, Health & Beauty, Clothing, Pet Supplies, Office, Kristine Business, etc.)
- **`subcategories`** — Two-level categorization (Migration 15). Each subcategory belongs to a parent category. "Unknown" always available.
- **`merchant_aliases`** — Pattern-based auto-categorization (contains/regex → merchant + category)
- **`import_profiles`** — Saved CSV column mappings per bank (Amex, Chase, Capital One, Citi, BofA)
- **`import_checklist` / `import_checklist_status`** — Monthly source tracking
- **`amazon_orders`** — Persisted Amazon orders for deferred matching. `matched_transaction_id` tracks matches. Has `category`/`subcategory` columns (Migration 16) for pre-categorization before matching.

## Amazon Workflow (Two-Phase)
**Phase 1 — Categorize (on Categorize page, Amazon tab):**
Upload Amazon order CSV → categorize each order one-by-one in a card queue (product name, date, amount shown; pick category + subcategory). Uses `infer_category()` for smart defaults. Categories saved to `amazon_orders` table.

**Phase 2 — Match (on Match page):**
Link pre-categorized Amazon orders to bank transactions. Matching uses the order's saved category (via `_get_order_category()`).

Two CSV formats: **Business** (groups by `payment_ref_id`) and **Privacy Central** (groups by `order_id`).

Multi-pass algorithm:
1. **Exact** (amount within 8% + date within 5 days) → auto-applied, confidence 0.95
2. **Likely** (amount within 8% + date within 10 days) → shown for review, confidence 0.80
3. **Multi-order** (Business format only — 2-3 orders summing to txn) → confidence 0.75
4. **Date-only fallback** → confidence 0.50

Exact matches auto-apply. Uncertain matches shown in single-card review queue (Accept/Skip).

Subscription charges (Audible, Kindle Unlimited, Amazon Music, etc.) excluded via `_AMAZON_EXCLUDE_PATTERNS`.

## Categorization
1. **Alias rules** (confidence 0.95) — `merchant_aliases` table
2. **Keyword heuristics** (confidence 0.5–0.8) — fallback for common merchants
3. **Subcategories** — Two-level system. `infer_category()` returns `(category, subcategory)` tuple. Users can create new subcategories inline during review. Cached with `@st.cache_data(ttl=120)`.

## Important Patterns
- `DATA_DIR` env var controls where DBs and uploads go (default: `./local_state`)
- Transaction IDs are deterministic — reimporting the same CSV won't create duplicates
- Upload dialog uses `@st.dialog` with custom CSS for 50vw width
- File auto-rename detects month from actual transaction dates, not the selected dropdown
- Imported sources show green checkmark (not strikethrough)

## Reset Amazon Data (for re-testing)
Script at `/tmp/reset_amazon.py` on Atlas. Do NOT set `DATA_DIR`:
```bash
ssh Atlas@192.168.3.10 "cd ~/expense-tracker && /Users/atlas/expense-tracker/.venv/bin/python /tmp/reset_amazon.py"
```

## Testing
```bash
python scripts/smoke_test.py  # No server needed
```

## Gitignored (never commit)
`local_state/`, `*.sqlite`, `uploads/`, `backups/`, `.venv/`, `statements/`

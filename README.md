# Expense Tracker

A lightweight, privacy-first expense tracker built with **Streamlit + SQLite**.
No bank linking. All data stays local. Ingest via CSV or PDF statements.

---

## Features

- **Two fully separate entities** — Personal and Company, each with its own SQLite database
- **CSV & PDF import** with reusable import profiles per issuer
- **Auto-categorization** via merchant alias rules and keyword heuristics (OpenClaw LLM stub)
- **Reports** — monthly stacked bar chart, category totals, transaction drill-down, CSV export
- **Category & Alias management** — add, rename, delete categories; manage merchant alias rules
- **Deduplication** — same transaction imported twice is safely skipped

---

## Local dev setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/rabuffington22/expense-tracker.git
cd expense-tracker

python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app/main.py --server.address 127.0.0.1 --server.port 8501
```

Or simply `streamlit run app/main.py` — the `.streamlit/config.toml` already sets
`address = "127.0.0.1"` and `port = 8501`.

Open http://127.0.0.1:8501 in your browser.

---

## DATA_DIR

All SQLite databases, uploaded files, and backups are stored in a single directory
controlled by the `DATA_DIR` environment variable.

| Scenario | Path |
|----------|------|
| Local dev (default) | `./local_state/` (relative to cwd) |
| Custom | Set `DATA_DIR=/your/path` |

**Directory layout created automatically:**

```
$DATA_DIR/
├── personal.sqlite
├── company.sqlite
├── uploads/
└── backups/
```

### Setting DATA_DIR

**Session (macOS/Linux):**
```bash
export DATA_DIR=/Users/you/Documents/expense-data
streamlit run app/main.py
```

**Persistent (add to `~/.zshrc` or `~/.bash_profile`):**
```bash
export DATA_DIR=/Users/you/Documents/expense-data
```

**On Atlas (launchd / cron):**
Add `DATA_DIR=/path/to/data` to the environment for the cron job or launchd plist.

---

## Tailscale / remote access

The app binds to `127.0.0.1` by default and is **not** exposed on the LAN.

To access it from another device on your Tailscale network, run it on a machine
that is already a Tailscale node and bind to its Tailscale IP:

```bash
streamlit run app/main.py --server.address 100.x.x.x --server.port 8501
```

Or add to `.streamlit/config.toml`:
```toml
[server]
address = "100.x.x.x"   # your Tailscale IP
port = 8501
```

**Do not bind to `0.0.0.0`** unless you have additional network-level access control.

---

## Smoke test

Verifies DB init, CSV parsing, normalization, import, and deduplication using
synthetic fixtures — no real financial data.

```bash
python scripts/smoke_test.py
```

---

## Project structure

```
expense-tracker/
├── app/
│   ├── main.py                     # Home page (Streamlit entry point)
│   ├── shared.py                   # Shared helpers (entity selector, page config)
│   └── pages/
│       ├── 1_Upload_Import.py      # CSV/PDF upload and import
│       ├── 2_Categorize.py         # Review and accept category suggestions
│       ├── 3_Reports.py            # Monthly charts and drill-downs
│       └── 4_Categories_Aliases.py # Manage categories and merchant rules
├── core/
│   ├── db.py           # DB init, migrations, connections
│   ├── imports.py      # CSV/PDF parsing, normalization, dedup, commit
│   ├── categorize.py   # Alias matching + keyword heuristic stub
│   └── reporting.py    # Query helpers for reports
├── fixtures/
│   └── sample.csv      # Synthetic test data (no real financial data)
├── scripts/
│   └── smoke_test.py   # Automated smoke test
├── .streamlit/
│   └── config.toml     # Streamlit server/theme config
├── requirements.txt
└── .gitignore
```

---

## Schema

Each entity DB has these tables:

| Table | Purpose |
|-------|---------|
| `transactions` | Canonical transaction ledger |
| `categories` | Category list (seeded with defaults) |
| `merchant_aliases` | Pattern → canonical merchant + category rules |
| `import_profiles` | Saved column mappings per bank/issuer |
| `schema_version` | Migration tracking |

Schema migrations are additive and safe to run on existing databases.

---

## OpenClaw integration (future)

`core/categorize.py::suggest_categories()` currently runs a deterministic stub
(alias rules + keyword heuristics).  To swap in an OpenClaw LLM call, replace
the body of that function — the interface is:

```python
def suggest_categories(df: pd.DataFrame, entity: str) -> pd.DataFrame:
    # Input:  DataFrame of transactions
    # Output: same DataFrame with category + confidence filled in
```

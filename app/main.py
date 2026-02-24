"""
Expense Tracker — Home

Run with:
    streamlit run app/main.py --server.address 127.0.0.1 --server.port 8501
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.shared import page_config, entity_selector  # noqa: E402

page_config("Expense Tracker — Home")

import streamlit as st  # noqa: E402

from core.db import get_connection  # noqa: E402

# ── Sidebar ───────────────────────────────────────────────────────────────────
entity = entity_selector()
entity_lower = entity.lower()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("💰 Expense Tracker")
st.caption(f"Entity: **{entity}**  ·  Use the sidebar to navigate pages")

st.markdown("---")

# ── Quick stats ───────────────────────────────────────────────────────────────
conn = get_connection(entity_lower)
try:
    total_txn   = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    uncat_count = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE category IS NULL OR category = '' OR confidence < 0.6"
    ).fetchone()[0]
    latest_date = conn.execute(
        "SELECT MAX(date) FROM transactions"
    ).fetchone()[0] or "—"
finally:
    conn.close()

c1, c2, c3 = st.columns(3)
c1.metric("Total transactions", f"{total_txn:,}")
c2.metric("Need review", f"{uncat_count:,}", help="Uncategorized or low-confidence")
c3.metric("Latest transaction", latest_date)

st.markdown("---")

st.markdown(
    """
**Pages**

| Page | Purpose |
|------|---------|
| **Upload & Import** | Import CSV and PDF bank statements |
| **Categorize** | Review and accept category suggestions |
| **Reports** | Monthly spend charts and drill-downs |
| **Categories & Aliases** | Manage categories and merchant rules |
"""
)

"""Dashboard — quick stats and overview."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime

import streamlit as st

from core.db import get_connection, init_db
from app.shared import get_entity, entity_display

entity, entity_lower = get_entity()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Dashboard")

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

    # Current month spend
    cur_month = datetime.now().strftime("%Y-%m")
    month_spend = conn.execute(
        "SELECT COALESCE(ABS(SUM(amount)), 0) FROM transactions "
        "WHERE strftime('%Y-%m', date) = ? AND amount < 0",
        (cur_month,),
    ).fetchone()[0]
    month_income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions "
        "WHERE strftime('%Y-%m', date) = ? AND amount > 0",
        (cur_month,),
    ).fetchone()[0]

    # Alias count
    alias_count = conn.execute("SELECT COUNT(*) FROM merchant_aliases WHERE active=1").fetchone()[0]
finally:
    conn.close()

c1, c2, c3 = st.columns(3)
c1.metric("Total Transactions", f"{total_txn:,}")
c2.metric("Need Review", f"{uncat_count:,}", help="Uncategorized or low-confidence")
c3.metric("Latest Transaction", latest_date)

c4, c5, c6 = st.columns(3)
c4.metric(f"{datetime.now().strftime('%b %Y')} Spend", f"${month_spend:,.2f}")
c5.metric(f"{datetime.now().strftime('%b %Y')} Income", f"${month_income:,.2f}")
c6.metric("Active Aliases", f"{alias_count}")

# ── Import progress ──────────────────────────────────────────────────────────
st.markdown("---")

# Check import progress across both entities
other_entity = "company" if entity_lower == "personal" else "personal"
init_db(other_entity)

month = datetime.now().strftime("%Y-%m")
progress_parts = []
for ent in ["personal", "company"]:
    ent_conn = get_connection(ent)
    try:
        ent_items = ent_conn.execute(
            "SELECT id FROM import_checklist WHERE entity=?", (ent,)
        ).fetchall()
        if not ent_items:
            continue
        item_ids = [r[0] for r in ent_items]
        placeholders = ",".join("?" * len(item_ids))
        done = ent_conn.execute(
            f"SELECT COUNT(*) FROM import_checklist_status "
            f"WHERE month=? AND completed=1 AND checklist_item_id IN ({placeholders})",
            [month] + item_ids,
        ).fetchone()[0]
        total = len(ent_items)
        icon = "Done" if done == total else "-"
        progress_parts.append(f"{icon} {entity_display(ent)}: {done}/{total}")
    finally:
        ent_conn.close()

if progress_parts:
    st.subheader(f"Import Progress — {month}")
    st.write(" · ".join(progress_parts))

# ── Top spending categories this month ────────────────────────────────────────
conn = get_connection(entity_lower)
try:
    top_cats = conn.execute(
        "SELECT COALESCE(NULLIF(category,''), 'Uncategorized') AS cat, "
        "ABS(SUM(amount)) AS total "
        "FROM transactions "
        "WHERE strftime('%Y-%m', date) = ? AND amount < 0 "
        "GROUP BY cat ORDER BY total DESC LIMIT 5",
        (cur_month,),
    ).fetchall()
finally:
    conn.close()

if top_cats:
    st.subheader(f"Top Categories — {datetime.now().strftime('%b %Y')}")
    for row in top_cats:
        col_name, col_amt = st.columns([3, 1])
        col_name.write(row["cat"])
        col_amt.write(f"${row['total']:,.2f}")

"""Dashboard — quick stats and import status overview."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime

import streamlit as st

from core.db import get_connection
from app.shared import get_entity

entity, entity_lower = get_entity()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stMainBlockContainer { padding-top: 1rem !important; }
    [data-testid='stAppViewBlockContainer'] { padding-top: 1rem !important; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="stMetric"] { padding-bottom: 0 !important; margin-bottom: -1rem !important; }
</style>
""", unsafe_allow_html=True)
st.title(f"{entity} Dashboard")
st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# ── Top row: Need Review + Latest Transaction ─────────────────────────────────
conn = get_connection(entity_lower)
try:
    uncat_count = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE category IS NULL OR category = '' OR confidence < 0.6"
    ).fetchone()[0]
    latest_raw = conn.execute(
        "SELECT MAX(date) FROM transactions"
    ).fetchone()[0]
    if latest_raw:
        latest_date = datetime.strptime(latest_raw, "%Y-%m-%d").strftime("%b %-d, %Y")
    else:
        latest_date = "—"
finally:
    conn.close()

c1, c2 = st.columns(2)
c1.metric("Need Review", f"{uncat_count:,}", help="Uncategorized or low-confidence")
c2.metric("Latest Transaction", latest_date)

st.markdown("---")

# ── Import progress — last 3 months ──────────────────────────────────────────
now = datetime.now()
y, m = now.year, now.month
months = []
for _ in range(3):
    months.append(f"{y:04d}-{m:02d}")
    m -= 1
    if m == 0:
        m = 12
        y -= 1


def format_month(ym: str) -> str:
    return datetime.strptime(ym, "%Y-%m").strftime("%b %Y")


conn = get_connection(entity_lower)
try:
    all_sources = conn.execute(
        "SELECT id FROM import_checklist WHERE entity=? ORDER BY sort_order, id",
        (entity_lower,),
    ).fetchall()
    all_sources = [dict(r) for r in all_sources]

    if all_sources:
        item_ids = [s["id"] for s in all_sources]
        placeholders = ",".join("?" * len(item_ids))
        total = len(all_sources)

        for mo in months:
            status_rows = conn.execute(
                f"SELECT checklist_item_id, completed FROM import_checklist_status "
                f"WHERE month=? AND checklist_item_id IN ({placeholders})",
                [mo] + item_ids,
            ).fetchall()
            done = sum(1 for r in status_rows if bool(r["completed"]))
            st.write(f"**{format_month(mo)}** — {done}/{total} sources imported")
    else:
        st.info("No import sources defined. Go to Upload > Settings to add your bank/card sources.")
finally:
    conn.close()

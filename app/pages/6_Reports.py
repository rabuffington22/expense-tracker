"""Reports page — stacked bar chart, category totals, drill-down, CSV export."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import io

import plotly.express as px
import streamlit as st

from core.reporting import (
    get_available_months,
    get_category_totals,
    get_monthly_totals,
    get_transactions,
)
from app.shared import get_entity

entity, entity_lower = get_entity()

st.title("Reports")

# ── Month range picker ────────────────────────────────────────────────────────
months = get_available_months(entity_lower)
if not months:
    st.info("No transactions imported yet.")
    st.stop()

col_start, col_end = st.columns(2)
start_month = col_start.selectbox("From month", months, index=0, key="rpt_start")
end_month   = col_end.selectbox("To month",   months, index=len(months)-1, key="rpt_end")

if start_month > end_month:
    st.error("'From' month must be on or before 'To' month.")
    st.stop()

# ── Stacked bar chart ─────────────────────────────────────────────────────────
monthly_df = get_monthly_totals(entity_lower, start_month, end_month)

if monthly_df.empty:
    st.info("No expense transactions found for the selected range.")
else:
    fig = px.bar(
        monthly_df,
        x="month",
        y="total_amount",
        color="category",
        barmode="stack",
        labels={"month": "Month", "total_amount": "Spend ($)", "category": "Category"},
        title=f"Monthly Spend by Category  ({start_month} – {end_month})",
        height=420,
    )
    fig.update_layout(
        xaxis_tickangle=-30,
        legend_title_text="Category",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Category totals for selected month ───────────────────────────────────────
selected_month = st.selectbox(
    "Detail month",
    [m for m in months if start_month <= m <= end_month],
    index=0,
    key="detail_month",
)

cat_df = get_category_totals(entity_lower, selected_month)
if cat_df.empty:
    st.info(f"No expense transactions in {selected_month}.")
    st.stop()

cat_display = cat_df.copy()
cat_display["total_amount"] = cat_display["total_amount"].map("${:,.2f}".format)
st.subheader(f"Category totals — {selected_month}")
st.dataframe(
    cat_display.rename(columns={"category": "Category", "count": "Txns", "total_amount": "Total Spend"}),
    use_container_width=True,
    hide_index=True,
)

# ── Category drill-down ───────────────────────────────────────────────────────
st.markdown("---")
all_categories = cat_df["category"].tolist()
drill_cat = st.selectbox("Drill into category", ["(select)"] + all_categories, key="drill_cat")

if drill_cat != "(select)":
    txns = get_transactions(entity_lower, month=selected_month, category=drill_cat)
    st.subheader(f"{drill_cat} — {selected_month}  ({len(txns)} transactions)")

    if txns.empty:
        st.info("No transactions found.")
    else:
        # Format for display
        disp = txns[["date", "description_raw", "merchant_canonical", "amount", "account", "notes"]].copy()
        disp["amount"] = disp["amount"].map("${:,.2f}".format)
        st.dataframe(
            disp.rename(columns={
                "date": "Date", "description_raw": "Description",
                "merchant_canonical": "Merchant", "amount": "Amount",
                "account": "Account", "notes": "Notes",
            }),
            use_container_width=True,
            hide_index=True,
        )

        # ── Export ────────────────────────────────────────────────────────────
        csv_bytes = txns.to_csv(index=False).encode()
        st.download_button(
            label="Export as CSV",
            data=csv_bytes,
            file_name=f"{entity_lower}_{selected_month}_{drill_cat.lower().replace(' ','_')}.csv",
            mime="text/csv",
        )

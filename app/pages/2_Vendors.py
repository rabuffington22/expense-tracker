"""Vendors page — upload vendor order data (Amazon CSV, Henry Schein XLSX)."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import date as _date

import pandas as pd
import streamlit as st

from core.amazon import (
    parse_amazon_csv,
    group_orders,
    save_orders_to_db,
    get_order_counts,
)
from core.henryschein import parse_henryschein_xlsx
from app.shared import get_entity

entity, entity_lower = get_entity()

st.title("Upload from Vendors")
st.caption(
    "Upload vendor order data. Orders are saved here, categorized on the next page, "
    "then matched to bank transactions on the Match page."
)

# ── Vendor selector ──────────────────────────────────────────────────────────
vendor = st.selectbox("Vendor", ["Amazon", "Henry Schein"], key="vendor_select")

# ── File uploader (adapts to vendor) ─────────────────────────────────────────
if vendor == "Amazon":
    uploaded = st.file_uploader(
        "Amazon Order History CSV",
        type=["csv"],
        key="vendor_file_upload",
        label_visibility="collapsed",
    )
else:
    uploaded = st.file_uploader(
        "Henry Schein Items Purchased XLSX",
        type=["xlsx"],
        key="vendor_file_upload",
        label_visibility="collapsed",
    )

# ── Parse + preview ──────────────────────────────────────────────────────────
if uploaded:
    if vendor == "Amazon":
        df_amazon, parse_warnings = parse_amazon_csv(uploaded)
        if parse_warnings:
            for w in parse_warnings:
                st.warning(w)
        if df_amazon.empty:
            st.error("Could not parse any orders from the CSV.")
        else:
            orders = group_orders(df_amazon)
            dates = df_amazon["order_date"].dropna()
            min_d = dates.min() if not dates.empty else "?"
            max_d = dates.max() if not dates.empty else "?"
            total_spent = sum(o["order_total"] for o in orders)
            st.write(
                f"**{len(orders)} orders** parsed "
                f"({min_d} to {max_d}) "
                f"totaling **${total_spent:,.2f}**"
            )

            # Date range filter
            st.markdown("---")
            st.write("**Filter by date range**")
            _parsed_dates = pd.to_datetime(dates, errors="coerce").dropna()
            _d_min = _parsed_dates.min().date() if not _parsed_dates.empty else _date.today()
            _d_max = _parsed_dates.max().date() if not _parsed_dates.empty else _date.today()
            _default_start = _date(_d_max.year - 1, _d_max.month, _d_max.day) if _d_max.year > _d_min.year or _d_max.month > _d_min.month else _d_min
            if _default_start < _d_min:
                _default_start = _d_min
            c_from, c_to = st.columns(2)
            filter_from = c_from.date_input("From", value=_default_start, min_value=_d_min, max_value=_d_max)
            filter_to = c_to.date_input("To", value=_d_max, min_value=_d_min, max_value=_d_max)

            filtered_orders = [
                o for o in orders
                if o.get("order_date") and filter_from <= pd.to_datetime(o["order_date"]).date() <= filter_to
            ]
            filtered_total = sum(o["order_total"] for o in filtered_orders)
            st.write(
                f"**{len(filtered_orders)}** of {len(orders)} orders in range, "
                f"totaling **${filtered_total:,.2f}**"
            )

            if st.button(f"Save {len(filtered_orders)} orders", type="primary", disabled=len(filtered_orders) == 0):
                inserted, skipped = save_orders_to_db(entity_lower, filtered_orders, vendor="amazon")
                msg = f"Saved **{inserted}** orders."
                if skipped:
                    msg += f" Skipped **{skipped}** duplicates."
                st.success(msg)
                st.rerun()

    else:  # Henry Schein
        orders, parse_warnings = parse_henryschein_xlsx(uploaded)
        if parse_warnings:
            for w in parse_warnings:
                st.warning(w)
        if not orders:
            st.error("Could not parse any invoices from the XLSX.")
        else:
            dates = [o["order_date"] for o in orders]
            min_d = min(dates)
            max_d = max(dates)
            total_spent = sum(o["order_total"] for o in orders)
            st.write(
                f"**{len(orders)} invoices** parsed "
                f"({min_d} to {max_d}) "
                f"totaling **${total_spent:,.2f}**"
            )

            # Date range filter
            st.markdown("---")
            st.write("**Filter by date range**")
            _parsed_dates = pd.to_datetime(dates, errors="coerce").dropna()
            _d_min = _parsed_dates.min().date() if not _parsed_dates.empty else _date.today()
            _d_max = _parsed_dates.max().date() if not _parsed_dates.empty else _date.today()
            _default_start = _date(_d_max.year - 1, _d_max.month, _d_max.day) if _d_max.year > _d_min.year or _d_max.month > _d_min.month else _d_min
            if _default_start < _d_min:
                _default_start = _d_min
            c_from, c_to = st.columns(2)
            filter_from = c_from.date_input("From", value=_default_start, min_value=_d_min, max_value=_d_max)
            filter_to = c_to.date_input("To", value=_d_max, min_value=_d_min, max_value=_d_max)

            filtered_orders = [
                o for o in orders
                if o.get("order_date") and filter_from <= pd.to_datetime(o["order_date"]).date() <= filter_to
            ]
            filtered_total = sum(o["order_total"] for o in filtered_orders)
            st.write(
                f"**{len(filtered_orders)}** of {len(orders)} invoices in range, "
                f"totaling **${filtered_total:,.2f}**"
            )

            if st.button(f"Save {len(filtered_orders)} invoices", type="primary", disabled=len(filtered_orders) == 0):
                inserted, skipped = save_orders_to_db(entity_lower, filtered_orders, vendor="henryschein")
                msg = f"Saved **{inserted}** invoices."
                if skipped:
                    msg += f" Skipped **{skipped}** duplicates."
                st.success(msg)
                st.rerun()

# ── Stored order summary ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Saved Orders")

total_orders, unmatched_orders = get_order_counts(entity_lower)
if total_orders:
    matched = total_orders - unmatched_orders
    st.write(
        f"**{total_orders}** vendor orders on file — "
        f"**{matched}** matched, **{unmatched_orders}** unmatched"
    )
else:
    st.caption("No vendor orders saved yet.")

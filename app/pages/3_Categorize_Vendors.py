"""Categorize Vendors page — card queue to label each vendor order."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime, timezone

import streamlit as st

from core.db import get_connection
from core.amazon import (
    get_uncategorized_orders,
    get_order_counts,
    categorize_order,
    infer_category,
)
from app.shared import get_entity, get_categories, get_subcategories

entity, entity_lower = get_entity()

st.title("Categorize Vendors")

# ── Order counts ─────────────────────────────────────────────────────────────
total_orders, _ = get_order_counts(entity_lower)
uncategorized = get_uncategorized_orders(entity_lower)

if not uncategorized and total_orders > 0:
    st.success("All orders are categorized! Head to the **Match** page to link them to bank charges.")
    st.stop()
elif not uncategorized:
    st.info("Upload vendor orders on the **Vendors** page to get started.")
    st.stop()

st.write(f"**{len(uncategorized)} orders** need categorization.")

# ── Card queue ───────────────────────────────────────────────────────────────
if "vendor_cat_idx" not in st.session_state:
    st.session_state.vendor_cat_idx = 0
idx = st.session_state.vendor_cat_idx

categories = get_categories(entity_lower)
if "Shopping" not in categories:
    categories = categories + ["Shopping"]

if idx >= len(uncategorized):
    st.success(f"Done! Categorized all **{len(uncategorized)}** orders.")
    if st.button("Finish"):
        st.session_state.pop("vendor_cat_idx", None)
        st.rerun()
else:
    order = uncategorized[idx]

    # Progress counter
    st.write(f"**Order {idx + 1} of {len(uncategorized)}**")
    st.progress(idx / len(uncategorized))

    # Product name — prominent
    st.markdown(f"### {order['product_summary'][:120]}")
    st.write(f"Date: {order['order_date']}  ·  Amount: **${order['order_total']:,.2f}**")

    # Infer a default
    inferred_cat, inferred_sub = infer_category(
        order.get("product_summary", ""),
        order.get("amazon_category", ""),
    )

    # Category + Subcategory
    c_cat, c_sub = st.columns(2)
    category = c_cat.selectbox(
        "Category",
        categories,
        index=categories.index(inferred_cat) if inferred_cat in categories else 0,
        key=f"vcat_{idx}",
    )
    subs = get_subcategories(entity_lower, category)
    subcategory = c_sub.selectbox(
        "Subcategory",
        subs,
        index=subs.index(inferred_sub) if inferred_sub in subs else (subs.index("Unknown") if "Unknown" in subs else 0),
        key=f"vsub_{idx}",
    )
    custom_sub = c_sub.text_input(
        "Or new subcategory",
        key=f"vnewsub_{idx}",
        placeholder="Type to create new...",
    )
    final_sub = custom_sub.strip() if custom_sub.strip() else subcategory

    # Helper to persist a custom subcategory
    def _save_subcategory(cat, sub):
        if cat and sub and sub != "Unknown":
            conn = get_connection(entity_lower)
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) "
                    "VALUES (?,?,?)",
                    (cat, sub, datetime.now(timezone.utc).isoformat()),
                )
                conn.commit()
            finally:
                conn.close()
            get_subcategories.clear()

    c1, c2 = st.columns(2)

    if c1.button("Save", type="primary", use_container_width=True):
        _save_subcategory(category, final_sub)
        categorize_order(entity_lower, order["id"], category, final_sub)
        st.session_state.vendor_cat_idx = idx + 1
        st.rerun()

    if c2.button("Skip", use_container_width=True):
        st.session_state.vendor_cat_idx = idx + 1
        st.rerun()

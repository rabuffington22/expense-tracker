"""Match page — link bank transactions to pre-categorized vendor orders."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime

import streamlit as st

from core.amazon import (
    find_amazon_transactions,
    load_orders_from_db,
    match_orders_to_transactions,
    apply_matches,
    get_order_counts,
)
from app.shared import get_entity

entity, entity_lower = get_entity()

st.title("Match")

# ── Order counts ─────────────────────────────────────────────────────────────
total_orders, unmatched_orders = get_order_counts(entity_lower)
matched_orders = total_orders - unmatched_orders

if total_orders:
    st.write(
        f"**{total_orders}** vendor orders on file — "
        f"**{matched_orders}** matched, **{unmatched_orders}** unmatched"
    )
else:
    st.info(
        "No vendor orders saved yet. Upload orders on the "
        "**Vendors** page first."
    )
    st.stop()

if unmatched_orders == 0:
    st.success("All vendor orders have been matched to bank transactions!")
    st.stop()

# ── Find Amazon bank transactions ────────────────────────────────────────────
amazon_txns = find_amazon_transactions(entity_lower)

if amazon_txns.empty:
    st.info(
        "No Amazon transactions found in your imported bank data. "
        "Import your bank statements on the **Upload** page first, then come back here."
    )
    st.stop()

st.write(f"Found **{len(amazon_txns)} Amazon transactions** in your bank data.")

# ── Run Matching ─────────────────────────────────────────────────────────────
if st.button("Run Matching", type="primary"):
    db_orders = load_orders_from_db(entity_lower, unmatched_only=True)
    matches = match_orders_to_transactions(db_orders, amazon_txns)

    # Auto-apply exact matches immediately
    exact = [m for m in matches if m["match_type"] == "exact"]
    if exact:
        auto_apply = []
        for m in exact:
            auto_apply.append({
                "transaction_id": m["transaction_id"],
                "product_summary": m["product_summary"],
                "suggested_category": m["suggested_category"],
                "suggested_subcategory": m.get("suggested_subcategory", "Unknown"),
                "order_id": m["order_id"],
                "order_total": m["matched_order"]["order_total"],
                "confidence": m["confidence"],
            })
        auto_count = apply_matches(entity_lower, auto_apply)
        st.success(f"Auto-applied **{auto_count}** exact matches.")

    # Keep non-exact matches for review
    review = [m for m in matches if m["match_type"] not in ("exact", "skip", "none")]
    no_match = [m for m in matches if m["match_type"] == "none"]
    st.session_state.match_review = review
    st.session_state.match_no_match = no_match
    st.session_state.match_review_idx = 0

# ── Review Queue ─────────────────────────────────────────────────────────────
review = st.session_state.get("match_review")
no_match = st.session_state.get("match_no_match", [])

if review:
    st.markdown("---")

    if "match_review_idx" not in st.session_state:
        st.session_state.match_review_idx = 0
    idx = st.session_state.match_review_idx

    if idx >= len(review):
        st.success(f"Done! Reviewed all **{len(review)}** matches.")
        if st.button("Finish"):
            st.session_state.pop("match_review", None)
            st.session_state.pop("match_no_match", None)
            st.session_state.pop("match_review_idx", None)
            st.rerun()
    else:
        m = review[idx]
        tid = m["transaction_id"]
        order = m.get("matched_order", {})
        txn_amt = abs(m["txn_amount"])
        order_amt = order.get("order_total", 0)
        amt_diff = abs(txn_amt - order_amt)
        amt_pct = (amt_diff / txn_amt * 100) if txn_amt else 0

        try:
            txn_d = datetime.strptime(m["txn_date"], "%Y-%m-%d")
            ord_d = datetime.strptime(order.get("order_date", m["txn_date"]), "%Y-%m-%d")
            days_apart = abs((txn_d - ord_d).days)
        except (ValueError, TypeError):
            days_apart = 0

        # Progress
        st.write(f"**Match {idx + 1} of {len(review)}**")
        st.progress(idx / len(review))

        # Side-by-side comparison
        col_bank, col_order = st.columns(2)
        with col_bank:
            st.write("**Bank Charge**")
            st.write(f"Date: {m['txn_date']}")
            st.write(f"Amount: **${txn_amt:,.2f}**")
            st.write(f"Description: {m['txn_description'][:60]}")
        with col_order:
            st.write("**Vendor Order**")
            st.write(f"Date: {order.get('order_date', '?')}")
            st.write(f"Amount: **${order_amt:,.2f}**")
            st.write(f"Product: {m['product_summary'][:80]}")
            # Show category from pre-categorized order
            cat_display = m.get("suggested_category", "")
            sub_display = m.get("suggested_subcategory", "")
            if cat_display:
                cat_label = cat_display
                if sub_display and sub_display != "Unknown":
                    cat_label += f" → {sub_display}"
                st.write(f"Category: **{cat_label}**")

        # Comparison stats — highlight problem values in red
        pct_color = "red" if amt_pct > 3 else "inherit"
        days_color = "red" if days_apart > 3 else "inherit"
        st.markdown(
            f"<span style='font-size:0.95rem'>"
            f"Amount diff: <span style='color:{pct_color};font-size:1.1rem;font-weight:600'>"
            f"${amt_diff:.2f} ({amt_pct:.1f}%)</span> · "
            f"Days apart: <span style='color:{days_color};font-size:1.1rem;font-weight:600'>"
            f"{days_apart}</span>"
            f"</span>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)

        if c1.button("✅ Accept", type="primary", use_container_width=True):
            apply_matches(entity_lower, [{
                "transaction_id": tid,
                "product_summary": m["product_summary"],
                "suggested_category": m["suggested_category"],
                "suggested_subcategory": m.get("suggested_subcategory", "Unknown"),
                "order_id": m["order_id"],
                "order_total": order.get("order_total", 0),
                "confidence": m["confidence"],
            }])
            st.session_state.match_review_idx = idx + 1
            st.rerun()

        if c2.button("⏭️ Skip", use_container_width=True):
            st.session_state.match_review_idx = idx + 1
            st.rerun()

if no_match:
    with st.expander(f"{len(no_match)} unmatched bank transactions"):
        for m in no_match:
            st.write(
                f"**{m['txn_date']}** — {m['txn_description']} — "
                f"${abs(m['txn_amount']):,.2f}"
            )

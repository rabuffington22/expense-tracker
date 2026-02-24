"""Categorize page — review, suggest, and accept transaction categories."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.shared import page_config, entity_selector, get_categories  # noqa: E402

page_config("Categorize")

import streamlit as st  # noqa: E402
import pandas as pd  # noqa: E402

from core.db import get_connection  # noqa: E402
from core.categorize import suggest_categories  # noqa: E402
from core.reporting import get_uncategorized  # noqa: E402

# ── Sidebar ───────────────────────────────────────────────────────────────────
entity = entity_selector()
entity_lower = entity.lower()

st.title("Categorize")
st.caption(f"Entity: **{entity}**")

# ── Load data ─────────────────────────────────────────────────────────────────
raw = get_uncategorized(entity_lower)

if raw.empty:
    st.success("✅ All transactions are categorized.")
    st.stop()

st.write(f"**{len(raw)} transactions** need review (uncategorized or low confidence)")

# ── Suggest button ────────────────────────────────────────────────────────────
if "categorize_df" not in st.session_state or st.session_state.get("categorize_entity") != entity_lower:
    st.session_state.categorize_df = raw.copy()
    st.session_state.categorize_entity = entity_lower

if st.button("✨ Suggest Categories", type="primary"):
    with st.spinner("Applying alias rules and keyword heuristics…"):
        st.session_state.categorize_df = suggest_categories(raw.copy(), entity_lower)
    st.success("Suggestions applied — review and accept below.")

# ── Editable table ────────────────────────────────────────────────────────────
categories = get_categories(entity_lower) + ["Uncategorized"]
df_edit = st.session_state.categorize_df

DISPLAY_COLS = ["transaction_id", "date", "description_raw", "amount", "category", "confidence", "notes"]
df_show = df_edit[[c for c in DISPLAY_COLS if c in df_edit.columns]].copy()

edited = st.data_editor(
    df_show,
    column_config={
        "transaction_id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "date":           st.column_config.TextColumn("Date", disabled=True, width="small"),
        "description_raw": st.column_config.TextColumn("Description", disabled=True, width="large"),
        "amount":         st.column_config.NumberColumn("Amount", format="$%.2f", disabled=True, width="small"),
        "category":       st.column_config.SelectboxColumn("Category", options=categories, width="medium"),
        "confidence":     st.column_config.NumberColumn("Conf.", format="%.0%%", disabled=True, width="small"),
        "notes":          st.column_config.TextColumn("Notes", width="medium"),
    },
    use_container_width=True,
    hide_index=True,
    height=520,
    key="cat_editor",
)

# ── Accept changes ────────────────────────────────────────────────────────────
st.markdown("---")
col_accept, col_reset = st.columns([2, 1])

with col_accept:
    if st.button("✅ Accept Changes", type="primary"):
        if edited.empty:
            st.warning("Nothing to save.")
        else:
            conn = get_connection(entity_lower)
            try:
                for _, row in edited.iterrows():
                    cat = row.get("category") or ""
                    if cat == "Uncategorized":
                        cat = ""
                    conn.execute(
                        "UPDATE transactions SET category=?, confidence=1.0, notes=? "
                        "WHERE transaction_id=?",
                        (cat, row.get("notes") or "", row["transaction_id"]),
                    )
                conn.commit()
            finally:
                conn.close()

            st.success(f"Saved {len(edited)} transaction(s).")
            # Clear session state so page reloads fresh
            del st.session_state["categorize_df"]
            st.rerun()

with col_reset:
    if st.button("Reset"):
        del st.session_state["categorize_df"]
        st.rerun()

# ── Create alias expander ─────────────────────────────────────────────────────
with st.expander("➕ Create merchant alias from a transaction"):
    st.caption("Aliases auto-categorize future transactions from the same merchant.")
    with st.form("add_alias_from_cat"):
        desc_input = st.text_input(
            "Merchant pattern (will match as 'contains')",
            placeholder="e.g. STARBUCKS",
        )
        canonical  = st.text_input("Canonical merchant name", placeholder="e.g. Starbucks")
        def_cat    = st.selectbox("Default category", ["(none)"] + get_categories(entity_lower))
        submitted  = st.form_submit_button("Save Alias")
        if submitted:
            if not desc_input or not canonical:
                st.error("Pattern and canonical name are required.")
            else:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                conn = get_connection(entity_lower)
                try:
                    conn.execute(
                        "INSERT INTO merchant_aliases "
                        "(pattern_type, pattern, merchant_canonical, default_category, active, created_at) "
                        "VALUES ('contains',?,?,?,1,?)",
                        (desc_input, canonical,
                         None if def_cat == "(none)" else def_cat,
                         now),
                    )
                    conn.commit()
                finally:
                    conn.close()
                st.success(f"Alias saved: '{desc_input}' → {canonical}")

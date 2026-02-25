"""Categorize page — review/suggest/accept categories + manage categories & aliases."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime, timezone

import streamlit as st
import pandas as pd

from core.db import get_connection
from core.categorize import suggest_categories, apply_aliases_to_db
from core.reporting import get_uncategorized
from app.shared import get_entity, get_categories

entity, entity_lower = get_entity()

st.title("Categorize")

tab_review, tab_settings = st.tabs(["Review", "Settings"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Review (suggest and accept categories)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_review:
    raw = get_uncategorized(entity_lower)

    if raw.empty:
        st.success("All transactions are categorized.")
    else:
        st.write(f"**{len(raw)} transactions** need review (uncategorized or low confidence)")

        # ── Suggest button ────────────────────────────────────────────────────
        if "categorize_df" not in st.session_state or st.session_state.get("categorize_entity") != entity_lower:
            st.session_state.categorize_df = raw.copy()
            st.session_state.categorize_entity = entity_lower

        if st.button("Suggest Categories", type="primary"):
            with st.spinner("Applying alias rules and keyword heuristics…"):
                st.session_state.categorize_df = suggest_categories(raw.copy(), entity_lower)
            st.success("Suggestions applied — review and accept below.")

        # ── Editable table ────────────────────────────────────────────────────
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

        # ── Accept changes ────────────────────────────────────────────────────
        st.markdown("---")
        col_accept, col_reset = st.columns([2, 1])

        with col_accept:
            if st.button("Accept Changes", type="primary"):
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
                    del st.session_state["categorize_df"]
                    st.rerun()

        with col_reset:
            if st.button("Reset"):
                del st.session_state["categorize_df"]
                st.rerun()

        # ── Quick alias from transaction ──────────────────────────────────────
        with st.expander("Create merchant alias from a transaction"):
            st.caption("Aliases auto-categorize future transactions from the same merchant.")
            with st.form("add_alias_from_cat"):
                desc_input = st.text_input(
                    "Merchant pattern (will match as 'contains')",
                    placeholder="e.g. STARBUCKS",
                )
                canonical = st.text_input("Canonical merchant name", placeholder="e.g. Starbucks")
                def_cat = st.selectbox("Default category", ["(none)"] + get_categories(entity_lower))
                submitted = st.form_submit_button("Save Alias")
                if submitted:
                    if not desc_input or not canonical:
                        st.error("Pattern and canonical name are required.")
                    else:
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


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Settings (categories + merchant aliases)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_settings:

    # ── Categories section ────────────────────────────────────────────────────
    st.subheader("Categories")

    cats = get_categories(entity_lower)
    if cats:
        for cat in cats:
            c1, c2 = st.columns([4, 1])
            c1.write(cat)
            if c2.button("Delete", key=f"delcat_{cat}"):
                conn = get_connection(entity_lower)
                try:
                    conn.execute("DELETE FROM categories WHERE name=?", (cat,))
                    conn.commit()
                finally:
                    conn.close()
                st.rerun()
    else:
        st.info("No categories defined.")

    with st.form("add_cat"):
        new_name = st.text_input("New category name")
        submitted = st.form_submit_button("Add Category")
        if submitted:
            if not new_name.strip():
                st.error("Name cannot be blank.")
            elif new_name.strip() in cats:
                st.error(f"'{new_name}' already exists.")
            else:
                now = datetime.now(timezone.utc).isoformat()
                conn = get_connection(entity_lower)
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO categories (name, created_at) VALUES (?,?)",
                        (new_name.strip(), now),
                    )
                    conn.commit()
                finally:
                    conn.close()
                st.success(f"Category '{new_name.strip()}' added.")
                st.rerun()

    with st.expander("Rename a category"):
        with st.form("rename_cat"):
            st.caption("Also updates all matching transactions and aliases")
            col_old, col_new = st.columns(2)
            old_name = col_old.selectbox("Existing category", cats or ["(none)"])
            new_rename = col_new.text_input("New name")
            if st.form_submit_button("Rename"):
                if not new_rename.strip():
                    st.error("New name cannot be blank.")
                else:
                    conn = get_connection(entity_lower)
                    try:
                        conn.execute("UPDATE categories SET name=? WHERE name=?", (new_rename.strip(), old_name))
                        conn.execute("UPDATE transactions SET category=? WHERE category=?", (new_rename.strip(), old_name))
                        conn.execute("UPDATE merchant_aliases SET default_category=? WHERE default_category=?",
                                     (new_rename.strip(), old_name))
                        conn.commit()
                    finally:
                        conn.close()
                    st.success(f"Renamed '{old_name}' → '{new_rename.strip()}'.")
                    st.rerun()

    st.markdown("---")

    # ── Merchant Aliases section ──────────────────────────────────────────────
    st.subheader("Merchant Aliases")
    st.caption(
        "Rules are checked in order. First match wins.  "
        "`contains` = case-insensitive substring; `regex` = Python regex."
    )

    def load_aliases() -> list[dict]:
        conn = get_connection(entity_lower)
        try:
            rows = conn.execute(
                "SELECT id, pattern_type, pattern, merchant_canonical, "
                "default_category, active FROM merchant_aliases ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    aliases = load_aliases()
    if aliases:
        header = st.columns([1, 2, 2, 2, 1, 1])
        for h, t in zip(header, ["Type", "Pattern", "Canonical", "Category", "Active", ""]):
            h.markdown(f"**{t}**")

        for a in aliases:
            c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 1, 1])
            c1.write(a["pattern_type"])
            c2.write(a["pattern"])
            c3.write(a["merchant_canonical"])
            c4.write(a["default_category"] or "—")
            c5.write("Yes" if a["active"] else "No")
            toggle_label = "Pause" if a["active"] else "Enable"
            if c6.button(toggle_label, key=f"tog_{a['id']}"):
                conn = get_connection(entity_lower)
                try:
                    conn.execute("UPDATE merchant_aliases SET active=? WHERE id=?",
                                 (0 if a["active"] else 1, a["id"]))
                    conn.commit()
                finally:
                    conn.close()
                st.rerun()

        # Delete by ID
        with st.expander("Delete alias"):
            alias_ids = {f"[{a['id']}] {a['pattern']}": a["id"] for a in aliases}
            to_delete = st.selectbox("Select alias", list(alias_ids.keys()), key="del_alias_sel")
            if st.button("Delete selected alias", type="secondary"):
                conn = get_connection(entity_lower)
                try:
                    conn.execute("DELETE FROM merchant_aliases WHERE id=?", (alias_ids[to_delete],))
                    conn.commit()
                finally:
                    conn.close()
                st.rerun()
    else:
        st.info("No aliases defined yet.")

    # ── Add alias ─────────────────────────────────────────────────────────────
    st.markdown("---")
    with st.form("add_alias"):
        st.markdown("**Add Alias**")
        col1, col2 = st.columns(2)
        ptype     = col1.selectbox("Pattern type", ["contains", "regex"])
        pattern   = col1.text_input("Pattern",   placeholder="e.g. STARBUCKS")
        canonical = col1.text_input("Canonical merchant name", placeholder="e.g. Starbucks")
        def_cat   = col2.selectbox("Default category (optional)", ["(none)"] + get_categories(entity_lower))
        active    = col2.checkbox("Active", value=True)

        if st.form_submit_button("Save Alias"):
            if not pattern.strip() or not canonical.strip():
                st.error("Pattern and canonical name are required.")
            else:
                now = datetime.now(timezone.utc).isoformat()
                conn = get_connection(entity_lower)
                try:
                    conn.execute(
                        "INSERT INTO merchant_aliases "
                        "(pattern_type, pattern, merchant_canonical, default_category, active, created_at) "
                        "VALUES (?,?,?,?,?,?)",
                        (ptype, pattern.strip(), canonical.strip(),
                         None if def_cat == "(none)" else def_cat,
                         int(active), now),
                    )
                    conn.commit()
                finally:
                    conn.close()
                st.success(f"Alias saved: '{pattern.strip()}' → {canonical.strip()}")
                st.rerun()

    # ── Reapply all rules ─────────────────────────────────────────────────────
    st.markdown("---")
    st.caption("Re-run all active alias rules against every transaction in the database.")
    if st.button("Reapply All Alias Rules", type="primary"):
        with st.spinner("Reapplying…"):
            updated = apply_aliases_to_db(entity_lower)
        st.success(f"Updated {updated} transaction(s).")

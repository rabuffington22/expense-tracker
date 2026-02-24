"""Categories & Aliases page — manage category list and merchant alias rules."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.shared import page_config, entity_selector, get_categories  # noqa: E402

page_config("Categories & Aliases")

from datetime import datetime, timezone  # noqa: E402

import streamlit as st  # noqa: E402

from core.db import get_connection  # noqa: E402
from core.categorize import apply_aliases_to_db  # noqa: E402

# ── Sidebar ───────────────────────────────────────────────────────────────────
entity = entity_selector()
entity_lower = entity.lower()

st.title("Categories & Aliases")
st.caption(f"Entity: **{entity}**")

tab_cats, tab_aliases = st.tabs(["Categories", "Merchant Aliases"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Categories
# ═══════════════════════════════════════════════════════════════════════════════
with tab_cats:
    st.subheader("Category List")

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

    st.markdown("---")
    st.subheader("Add / Rename")

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

    with st.form("rename_cat"):
        st.caption("Rename a category (also updates all matching transactions)")
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


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Merchant Aliases
# ═══════════════════════════════════════════════════════════════════════════════
with tab_aliases:
    st.subheader("Merchant Alias Rules")
    st.caption(
        "Rules are checked in order. First match wins.  "
        "`contains` = case-insensitive substring match; `regex` = Python regex."
    )

    # ── List existing aliases ─────────────────────────────────────────────────
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
            c5.write("✅" if a["active"] else "⏸")
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
    st.subheader("Add Alias")
    with st.form("add_alias"):
        col1, col2 = st.columns(2)
        ptype      = col1.selectbox("Pattern type", ["contains", "regex"])
        pattern    = col1.text_input("Pattern",   placeholder="e.g. STARBUCKS")
        canonical  = col1.text_input("Canonical merchant name", placeholder="e.g. Starbucks")
        def_cat    = col2.selectbox("Default category (optional)", ["(none)"] + get_categories(entity_lower))
        active     = col2.checkbox("Active", value=True)

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
    st.subheader("Reapply Rules to History")
    st.caption("Re-runs all active alias rules against every transaction in the database.")
    if st.button("Reapply All Alias Rules", type="primary"):
        with st.spinner("Reapplying…"):
            updated = apply_aliases_to_db(entity_lower)
        st.success(f"Updated {updated} transaction(s).")

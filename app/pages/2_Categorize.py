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
from core.amazon import (
    parse_amazon_csv,
    group_orders,
    save_orders_to_db,
    get_order_counts,
    get_uncategorized_orders,
    categorize_order,
    infer_category,
)
from app.shared import get_entity, get_categories, get_subcategories

entity, entity_lower = get_entity()

st.title("Categorize")

tab_review, tab_amazon, tab_settings = st.tabs(["Review", "Amazon Match", "Settings"])


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
                    aliases_created = 0
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

                            # Auto-create merchant alias so future imports learn
                            if cat:
                                desc = str(row.get("description_raw") or "").strip()
                                if desc:
                                    # Strip platform prefixes for cleaner patterns
                                    import re
                                    pattern = re.sub(
                                        r"^(paypal\s*\*|venmo\s*\*|zelle\s*\*|sq\s*\*|tst\s*\*|sp\s*\*)\s*",
                                        "", desc, flags=re.IGNORECASE,
                                    ).strip()
                                    if len(pattern) >= 4:
                                        # Check if alias already exists
                                        existing = conn.execute(
                                            "SELECT id FROM merchant_aliases "
                                            "WHERE pattern_type='contains' AND LOWER(pattern)=LOWER(?)",
                                            (pattern,),
                                        ).fetchone()
                                        if not existing:
                                            now_ts = datetime.now(timezone.utc).isoformat()
                                            conn.execute(
                                                "INSERT INTO merchant_aliases "
                                                "(pattern_type, pattern, merchant_canonical, "
                                                " default_category, active, created_at) "
                                                "VALUES (?, ?, ?, ?, 1, ?)",
                                                ("contains", pattern, pattern, cat, now_ts),
                                            )
                                            aliases_created += 1
                        conn.commit()
                    finally:
                        conn.close()

                    msg = f"Saved {len(edited)} transaction(s)."
                    if aliases_created:
                        msg += f" Created {aliases_created} merchant alias(es) for future matching."
                    st.success(msg)
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
# TAB 2 — Amazon Orders (upload + categorize)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_amazon:

    # ── Section A: Upload Amazon Orders ────────────────────────────────────
    st.subheader("Upload Amazon Orders")
    st.caption(
        "Upload your Amazon order history CSV. Orders are saved and "
        "categorized here, then matched to bank transactions on the Match page."
    )

    amazon_file = st.file_uploader(
        "Amazon Order History CSV",
        type=["csv"],
        key="amazon_csv_upload",
        label_visibility="collapsed",
    )

    if amazon_file:
        df_amazon, parse_warnings = parse_amazon_csv(amazon_file)
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
            from datetime import date as _date
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
                inserted, skipped = save_orders_to_db(entity_lower, filtered_orders)
                msg = f"Saved **{inserted}** orders."
                if skipped:
                    msg += f" Skipped **{skipped}** duplicates."
                st.success(msg)
                st.rerun()

    # Show stored order summary
    total_orders, unmatched_orders = get_order_counts(entity_lower)
    if total_orders:
        matched = total_orders - unmatched_orders
        st.write(
            f"**{total_orders}** Amazon orders on file — "
            f"**{matched}** matched, **{unmatched_orders}** unmatched"
        )
    else:
        st.caption("No Amazon orders saved yet.")

    st.markdown("---")

    # ── Section B: Categorize Orders (card queue) ──────────────────────────
    st.subheader("Categorize Orders")

    uncategorized = get_uncategorized_orders(entity_lower)

    if not uncategorized and total_orders > 0:
        st.success("All orders are categorized! Head to the **Match** page to link them to bank charges.")
    elif not uncategorized:
        st.info("Upload an Amazon order CSV above to get started.")
    else:
        st.write(f"**{len(uncategorized)} orders** need categorization.")

        # Track progress through the queue
        if "amazon_cat_idx" not in st.session_state:
            st.session_state.amazon_cat_idx = 0
        idx = st.session_state.amazon_cat_idx

        categories = get_categories(entity_lower)
        if "Shopping" not in categories:
            categories = categories + ["Shopping"]

        if idx >= len(uncategorized):
            st.success(f"Done! Categorized all **{len(uncategorized)}** orders.")
            if st.button("Finish"):
                st.session_state.pop("amazon_cat_idx", None)
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
                key=f"ocat_{idx}",
            )
            subs = get_subcategories(entity_lower, category)
            subcategory = c_sub.selectbox(
                "Subcategory",
                subs,
                index=subs.index(inferred_sub) if inferred_sub in subs else (subs.index("Unknown") if "Unknown" in subs else 0),
                key=f"osub_{idx}",
            )
            custom_sub = c_sub.text_input(
                "Or new subcategory",
                key=f"onewsub_{idx}",
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

            if c1.button("💾 Save", type="primary", use_container_width=True):
                _save_subcategory(category, final_sub)
                categorize_order(entity_lower, order["id"], category, final_sub)
                st.session_state.amazon_cat_idx = idx + 1
                st.rerun()

            if c2.button("⏭️ Skip", use_container_width=True):
                st.session_state.amazon_cat_idx = idx + 1
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Settings (categories + merchant aliases)
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
                get_categories.clear()
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
                get_categories.clear()
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
                    get_categories.clear()
                    st.rerun()

    st.markdown("---")

    # ── Subcategories section ──────────────────────────────────────────────────
    st.subheader("Subcategories")

    sub_cat_filter = st.selectbox(
        "Show subcategories for:",
        cats or ["(none)"],
        key="sub_cat_filter",
    )

    if sub_cat_filter and sub_cat_filter != "(none)":
        subs = get_subcategories(entity_lower, sub_cat_filter)
        # Filter out the auto-added "Unknown" for display — only show DB entries
        conn = get_connection(entity_lower)
        try:
            db_subs = conn.execute(
                "SELECT id, name FROM subcategories WHERE category_name = ? ORDER BY name",
                (sub_cat_filter,),
            ).fetchall()
        finally:
            conn.close()

        if db_subs:
            for sub_row in db_subs:
                sc1, sc2 = st.columns([4, 1])
                sc1.write(sub_row[1])
                if sc2.button("Delete", key=f"delsub_{sub_row[0]}"):
                    conn = get_connection(entity_lower)
                    try:
                        conn.execute("DELETE FROM subcategories WHERE id=?", (sub_row[0],))
                        conn.commit()
                    finally:
                        conn.close()
                    get_subcategories.clear()
                    st.rerun()
        else:
            st.caption("No subcategories defined yet. 'Unknown' is always available.")

        with st.form("add_sub"):
            new_sub = st.text_input("New subcategory name")
            if st.form_submit_button("Add Subcategory"):
                if not new_sub.strip():
                    st.error("Name cannot be blank.")
                else:
                    now = datetime.now(timezone.utc).isoformat()
                    conn = get_connection(entity_lower)
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) VALUES (?,?,?)",
                            (sub_cat_filter, new_sub.strip(), now),
                        )
                        conn.commit()
                    finally:
                        conn.close()
                    st.success(f"Subcategory '{new_sub.strip()}' added to {sub_cat_filter}.")
                    get_subcategories.clear()
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

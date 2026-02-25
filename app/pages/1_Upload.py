"""Upload page — source-by-source import of CSV and PDF bank statements."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from core.db import get_connection
from core.imports import (
    commit_transactions,
    normalize_transactions,
    parse_csv,
    parse_pdf,
)
from app.shared import get_entity

entity, entity_lower = get_entity()

st.title("Upload")


# ── Profile helpers ───────────────────────────────────────────────────────────

def load_profiles() -> list[dict]:
    conn = get_connection(entity_lower)
    try:
        rows = conn.execute("SELECT * FROM import_profiles ORDER BY name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def save_profile(p: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(entity_lower)
    try:
        conn.execute(
            """INSERT OR REPLACE INTO import_profiles
               (name, date_col, description_col, amount_col, merchant_col,
                account_col, currency_col, amount_negate, date_format, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (p["name"], p["date_col"], p["description_col"], p["amount_col"],
             p.get("merchant_col"), p.get("account_col"), p.get("currency_col"),
             int(p.get("amount_negate", 0)), p.get("date_format"), now),
        )
        conn.commit()
    finally:
        conn.close()


def delete_profile(name: str) -> None:
    conn = get_connection(entity_lower)
    try:
        conn.execute("DELETE FROM import_profiles WHERE name=?", (name,))
        conn.commit()
    finally:
        conn.close()


# ── Checklist helpers ─────────────────────────────────────────────────────────

def current_month() -> str:
    return datetime.now().strftime("%Y-%m")


def load_checklist_all() -> list[dict]:
    """Load ALL checklist items (both entities) from current DB."""
    conn = get_connection(entity_lower)
    try:
        rows = conn.execute(
            "SELECT * FROM import_checklist ORDER BY sort_order, id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def load_checklist_status(month: str) -> dict:
    """Return {checklist_item_id: status_row} for the given month."""
    conn = get_connection(entity_lower)
    try:
        rows = conn.execute(
            "SELECT * FROM import_checklist_status WHERE month=?", (month,)
        ).fetchall()
        return {r["checklist_item_id"]: dict(r) for r in rows}
    finally:
        conn.close()


def set_checklist_status(item_id: int, month: str, completed: bool, filename: str = "") -> None:
    now = datetime.now(timezone.utc).isoformat() if completed else None
    conn = get_connection(entity_lower)
    try:
        conn.execute(
            """INSERT INTO import_checklist_status
               (checklist_item_id, month, completed, completed_at, source_filename)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(checklist_item_id, month)
               DO UPDATE SET completed=?, completed_at=?, source_filename=?""",
            (item_id, month, int(completed), now, filename,
             int(completed), now, filename),
        )
        conn.commit()
    finally:
        conn.close()


def save_checklist_item(label: str, filename_pattern: str = "", profile_name: str = "",
                        url: str = "", notes: str = "", item_entity: str = "personal") -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(entity_lower)
    try:
        max_order = conn.execute("SELECT COALESCE(MAX(sort_order),0) FROM import_checklist").fetchone()[0]
        conn.execute(
            """INSERT INTO import_checklist
               (label, filename_pattern, profile_name, url, notes, sort_order, entity, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (label, filename_pattern or None, profile_name or None,
             url or None, notes or None, max_order + 1, item_entity, now),
        )
        conn.commit()
    finally:
        conn.close()


def delete_checklist_item(item_id: int) -> None:
    conn = get_connection(entity_lower)
    try:
        conn.execute("DELETE FROM import_checklist WHERE id=?", (item_id,))
        conn.execute("DELETE FROM import_checklist_status WHERE checklist_item_id=?", (item_id,))
        conn.commit()
    finally:
        conn.close()


# ── Month list helper ─────────────────────────────────────────────────────────

def month_options(count: int = 12) -> list[str]:
    """Return last `count` months as YYYY-MM strings, most recent first."""
    now = datetime.now()
    y, m = now.year, now.month
    months = []
    for _ in range(count):
        months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return months


def format_month(ym: str) -> str:
    """Convert 'YYYY-MM' to 'Feb 2026'."""
    return datetime.strptime(ym, "%Y-%m").strftime("%b %Y")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_import, tab_settings = st.tabs(["Import", "Settings"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Import (source-by-source)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_import:

    # ── Month selector ────────────────────────────────────────────────────────
    months = month_options()
    col_month, _ = st.columns([1, 7])
    with col_month:
        selected_month = st.selectbox(
            "Month",
            months,
            index=0,
            format_func=format_month,
            key="import_month",
            label_visibility="collapsed",
        )

    # ── Load data ─────────────────────────────────────────────────────────────
    all_items = load_checklist_all()
    items = [i for i in all_items if i.get("entity", "personal") == entity_lower]
    status = load_checklist_status(selected_month)
    profiles = load_profiles()
    profile_map = {p["name"]: p for p in profiles}

    # ── Progress summary ──────────────────────────────────────────────────────
    if not items:
        st.info("No sources defined. Go to the Settings tab to add your bank/card sources.")
    else:
        done_count = sum(
            1 for i in items if status.get(i["id"], {}).get("completed", 0)
        )
        total_count = len(items)

        st.write(f"{done_count}/{total_count} sources imported")

        st.markdown("---")

        # ── Look up last transaction date per source ─────────────────────────
        conn = get_connection(entity_lower)
        try:
            source_last_dates = {}
            for item in items:
                pattern = (item.get("filename_pattern") or "").strip()
                if pattern:
                    row = conn.execute(
                        "SELECT MAX(date) FROM transactions "
                        "WHERE LOWER(source_filename) LIKE ?",
                        (f"%{pattern.lower()}%",),
                    ).fetchone()
                    if row and row[0]:
                        source_last_dates[item["id"]] = row[0]
        finally:
            conn.close()

        # ── Source list ───────────────────────────────────────────────────────
        # Clear active upload if entity or month changed
        if st.session_state.get("_upload_entity") != entity_lower:
            st.session_state.pop("active_upload_source", None)
            st.session_state["_upload_entity"] = entity_lower
        if st.session_state.get("_upload_month") != selected_month:
            st.session_state.pop("active_upload_source", None)
            st.session_state["_upload_month"] = selected_month

        for item in items:
            item_status = status.get(item["id"], {})
            is_done = bool(item_status.get("completed", 0))

            col_label, col_action = st.columns([4, 1.5])

            with col_label:
                if is_done:
                    st.markdown(f"~~{item['label']}~~")
                    fname = item_status.get("source_filename", "")
                    if fname:
                        st.caption(fname)
                else:
                    st.markdown(f"**{item['label']}**")
                    last_date = source_last_dates.get(item["id"])
                    hint = f"Last: {last_date}" if last_date else "No data yet"
                    if item.get("url"):
                        hint += f" · [Download]({item['url']})"
                    st.markdown(hint)

            with col_action:
                if is_done:
                    if st.button("Undo", key=f"undo_{item['id']}"):
                        set_checklist_status(item["id"], selected_month, False)
                        st.rerun()
                else:
                    if st.button("Upload", key=f"upload_{item['id']}", type="primary"):
                        st.session_state.active_upload_source = item["id"]

        # ── Upload panel for active source ────────────────────────────────────
        active_source_id = st.session_state.get("active_upload_source")

        if active_source_id:
            active_item = next((i for i in items if i["id"] == active_source_id), None)

            if active_item is None:
                st.session_state.pop("active_upload_source", None)
                st.rerun()
            else:
                st.markdown("---")
                col_hdr, col_cancel = st.columns([4, 1])
                with col_hdr:
                    st.subheader(f"Import: {active_item['label']}")
                with col_cancel:
                    if st.button("Cancel"):
                        st.session_state.pop("active_upload_source", None)
                        st.session_state.pop("source_parsed", None)
                        st.rerun()

                # Resolve profile for this source
                profile_name = active_item.get("profile_name")
                profile = profile_map.get(profile_name) if profile_name else None

                # Multi-file uploader
                uploaded_files = st.file_uploader(
                    f"Drop files for {active_item['label']}",
                    type=["csv", "pdf"],
                    accept_multiple_files=True,
                    key=f"fu_{active_source_id}",
                    label_visibility="collapsed",
                )

                if uploaded_files:
                    # Parse each file
                    all_parsed = {}
                    for f in uploaded_files:
                        is_pdf = f.name.lower().endswith(".pdf")
                        try:
                            if is_pdf:
                                raw, errors = parse_pdf(f)
                                if raw.empty:
                                    all_parsed[f.name] = (None, "; ".join(errors))
                                else:
                                    norm = normalize_transactions(raw, source_filename=f.name, profile=None)
                                    all_parsed[f.name] = (norm, "; ".join(errors) if errors else None)
                            else:
                                raw = parse_csv(f, profile=profile)
                                norm = normalize_transactions(raw, source_filename=f.name, profile=profile)
                                all_parsed[f.name] = (norm, None)
                        except Exception as exc:
                            all_parsed[f.name] = (None, str(exc))

                    # Show per-file previews
                    good_dfs = {}
                    for fname, (df, err) in all_parsed.items():
                        with st.expander(fname, expanded=True):
                            if err:
                                st.warning(f"Extraction notes: {err}")
                            if df is None or df.empty:
                                st.error("Could not extract any transactions.")
                                continue

                            # Summary
                            stat_parts = [f"**{len(df)} transactions**"]
                            if "date" in df.columns:
                                dates = pd.to_datetime(df["date"], errors="coerce").dropna()
                                if not dates.empty:
                                    min_d = dates.min().strftime("%b %d")
                                    max_d = dates.max().strftime("%b %d, %Y")
                                    stat_parts.append(f"{min_d} – {max_d}")
                            st.write(" · ".join(stat_parts))

                            # Credits / debits
                            if "amount" in df.columns:
                                amounts = pd.to_numeric(df["amount"], errors="coerce").dropna()
                                credits = amounts[amounts > 0].sum()
                                debits = abs(amounts[amounts < 0].sum())
                                net = credits - debits
                                mc1, mc2, mc3 = st.columns(3)
                                mc1.metric("Credits", f"${credits:,.2f}")
                                mc2.metric("Debits", f"${debits:,.2f}")
                                net_label = f"${net:,.2f}" if net >= 0 else f"-${abs(net):,.2f}"
                                mc3.metric("Net", net_label)

                            # Data table
                            display_cols = ["date", "description_raw", "amount", "account", "currency"]
                            st.dataframe(
                                df[[c for c in display_cols if c in df.columns]],
                                use_container_width=True,
                                height=220,
                            )
                            good_dfs[fname] = df

                    # Import button
                    if good_dfs:
                        total_txns = sum(len(d) for d in good_dfs.values())
                        file_count = len(good_dfs)
                        st.markdown("---")
                        st.write(
                            f"Ready to import **{total_txns} transactions** "
                            f"from **{file_count} file{'s' if file_count > 1 else ''}**"
                        )

                        if st.button(f"Import {total_txns} transactions", type="primary"):
                            total_new = total_skip = 0
                            for fname, df in good_dfs.items():
                                inserted, skipped = commit_transactions(df, entity_lower)
                                total_new += inserted
                                total_skip += skipped

                            # Mark source complete
                            all_filenames = ", ".join(good_dfs.keys())
                            set_checklist_status(
                                active_item["id"],
                                selected_month,
                                True,
                                all_filenames,
                            )

                            st.success(
                                f"Imported **{total_new} new** / "
                                f"skipped **{total_skip} duplicates**"
                            )
                            st.session_state.pop("active_upload_source", None)
                            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Settings (Sources + Profiles)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_settings:

    # ── Sources section ───────────────────────────────────────────────────────
    st.subheader("Monthly Import Sources")
    st.caption(
        "Define which statements you expect to import each month."
    )

    profiles = load_profiles()
    profile_options = ["(none)"] + [p["name"] for p in profiles]
    all_items_tab = load_checklist_all()
    entity_items = [i for i in all_items_tab if i.get("entity", "personal") == entity_lower]

    if entity_items:
        for item in entity_items:
            with st.expander(item["label"]):
                st.write(f"**Filename pattern:** {item.get('filename_pattern') or '—'}")
                st.write(f"**Linked profile:** {item.get('profile_name') or '—'}")
                st.write(f"**URL:** {item.get('url') or '—'}")
                st.write(f"**Notes:** {item.get('notes') or '—'}")
                if st.button("Delete", key=f"delcl_{item['id']}"):
                    delete_checklist_item(item["id"])
                    st.rerun()
    else:
        st.info("No sources defined yet. Add your recurring bank/card statements below.")

    st.markdown("---")
    st.subheader("Add Source")
    with st.form("add_checklist"):
        cl_label    = st.text_input("Source name *", placeholder="e.g. Chase Checking")
        c1, c2 = st.columns(2)
        cl_pattern  = c1.text_input(
            "Filename pattern",
            placeholder="e.g. chase",
            help="Case-insensitive substring to match uploaded filenames",
        )
        cl_profile  = c1.selectbox("Linked profile", profile_options)
        cl_url      = c2.text_input("Download URL", placeholder="e.g. https://chase.com/statements")
        cl_notes    = c2.text_input("Notes", placeholder="e.g. Export last 30 days as CSV")

        if st.form_submit_button("Add Source"):
            if not cl_label.strip():
                st.error("Source name is required.")
            else:
                save_checklist_item(
                    label=cl_label.strip(),
                    filename_pattern=cl_pattern.strip(),
                    profile_name="" if cl_profile == "(none)" else cl_profile,
                    url=cl_url.strip(),
                    notes=cl_notes.strip(),
                    item_entity=entity_lower,
                )
                st.success(f"Source '{cl_label.strip()}' added.")
                st.rerun()

    st.markdown("---")

    # ── Profiles section ──────────────────────────────────────────────────────
    st.subheader("Import Profiles")
    st.caption(
        "Profiles map column names from your bank's CSV to the standard format."
    )

    profiles = load_profiles()
    if profiles:
        for p in profiles:
            with st.expander(p["name"]):
                c1, c2 = st.columns(2)
                c1.write(f"**Date column:** {p['date_col']}")
                c1.write(f"**Description column:** {p['description_col']}")
                c1.write(f"**Amount column:** {p['amount_col']}")
                c2.write(f"**Merchant column:** {p.get('merchant_col') or '—'}")
                c2.write(f"**Account column:** {p.get('account_col') or '—'}")
                c2.write(f"**Negate amounts:** {'Yes' if p['amount_negate'] else 'No'}")
                c2.write(f"**Date format:** {p.get('date_format') or 'auto'}")
                if st.button("Delete", key=f"del_{p['name']}"):
                    delete_profile(p["name"])
                    st.rerun()
    else:
        st.info("No profiles yet.")

    st.markdown("---")
    st.subheader("Add Profile")
    with st.form("add_profile"):
        name     = st.text_input("Profile name", placeholder="e.g. Chase Checking")
        col1, col2 = st.columns(2)
        date_col = col1.text_input("Date column *",        placeholder="Date")
        desc_col = col1.text_input("Description column *", placeholder="Description")
        amt_col  = col1.text_input("Amount column *",      placeholder="Amount")
        mer_col  = col2.text_input("Merchant column",      placeholder="(optional)")
        acc_col  = col2.text_input("Account column",       placeholder="(optional)")
        cur_col  = col2.text_input("Currency column",      placeholder="(optional)")
        negate   = col2.checkbox("Negate amounts", help="Check if debits are positive in this CSV")
        date_fmt = st.text_input("Date format", placeholder="e.g. %m/%d/%Y (leave blank for auto)")

        submitted = st.form_submit_button("Save Profile")
        if submitted:
            if not all([name, date_col, desc_col, amt_col]):
                st.error("Name, Date, Description, and Amount columns are required.")
            else:
                save_profile({
                    "name": name, "date_col": date_col, "description_col": desc_col,
                    "amount_col": amt_col, "merchant_col": mer_col or None,
                    "account_col": acc_col or None, "currency_col": cur_col or None,
                    "amount_negate": negate,
                    "date_format": date_fmt.strip() or None,
                })
                st.success(f"Profile '{name}' saved.")
                st.rerun()

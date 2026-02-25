"""Upload & Import page — ingest CSV and PDF bank statements."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.shared import page_config, entity_selector  # noqa: E402

page_config("Upload & Import")

from datetime import datetime, timezone  # noqa: E402

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from core.db import get_connection, init_db  # noqa: E402
from core.imports import (  # noqa: E402
    commit_transactions,
    normalize_transactions,
    parse_csv,
    parse_pdf,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
entity = entity_selector()
entity_lower = entity.lower()
other_entity = "company" if entity_lower == "personal" else "personal"

# Ensure other entity DB is initialized too (for cross-entity progress)
init_db(other_entity)

st.title("Upload & Import")
st.caption(f"Entity: **{entity}**")


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


def get_checklist_progress(month: str, all_items: list[dict]) -> dict:
    """Get import progress for both entities by querying each entity's DB."""
    result = {}
    for ent in ["personal", "company"]:
        ent_items = [i for i in all_items if i.get("entity", "personal") == ent]
        if not ent_items:
            result[ent] = (0, 0)
            continue
        conn = get_connection(ent)
        try:
            item_ids = [i["id"] for i in ent_items]
            placeholders = ",".join("?" * len(item_ids))
            done = conn.execute(
                f"SELECT COUNT(*) FROM import_checklist_status "
                f"WHERE month=? AND completed=1 AND checklist_item_id IN ({placeholders})",
                [month] + item_ids,
            ).fetchone()[0]
            result[ent] = (done, len(ent_items))
        finally:
            conn.close()
    return result


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


def auto_check_by_filename(filenames: list, month: str) -> list:
    """Auto-check items whose filename_pattern matches any imported file.

    Only checks items belonging to the current entity.
    """
    all_items = load_checklist_all()
    matched = []
    for item in all_items:
        # Only auto-check items for the current entity
        if item.get("entity", "personal") != entity_lower:
            continue
        pattern = (item.get("filename_pattern") or "").strip().lower()
        if not pattern:
            continue
        for fname in filenames:
            if pattern in fname.lower():
                set_checklist_status(item["id"], month, True, fname)
                matched.append(item["label"])
                break
    return matched


def suggest_entity_for_file(filename: str, all_items: list[dict]):
    """Return (entity, checklist_label) if filename matches a checklist pattern."""
    for item in all_items:
        pattern = (item.get("filename_pattern") or "").strip().lower()
        if pattern and pattern in filename.lower():
            return item.get("entity", "personal"), item["label"]
    return None, None


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


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_upload, tab_profiles, tab_checklist = st.tabs(["Upload Files", "Manage Profiles", "Monthly Sources"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Upload Files
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    # ── Cross-entity import progress ──────────────────────────────────────────
    month = current_month()
    all_items = load_checklist_all()

    if all_items:
        progress = get_checklist_progress(month, all_items)
        p_done, p_total = progress.get("personal", (0, 0))
        c_done, c_total = progress.get("company", (0, 0))
        total_done = p_done + c_done
        total_all = p_total + c_total

        if total_all > 0 and total_done == total_all:
            st.success(f"All {total_all} sources imported for **{month}**")
        else:
            parts = []
            if p_total > 0:
                icon = "✅" if p_done == p_total else "📋"
                parts.append(f"{icon} Personal: {p_done}/{p_total}")
            if c_total > 0:
                icon = "✅" if c_done == c_total else "📋"
                parts.append(f"{icon} Company: {c_done}/{c_total}")
            st.info(f"**{month}** — {' · '.join(parts)}")

        # Show only current entity's items
        items = [i for i in all_items if i.get("entity", "personal") == entity_lower]
        status = load_checklist_status(month)

        for item in items:
            item_status = status.get(item["id"], {})
            is_done = bool(item_status.get("completed", 0))

            col_check, col_label, col_info = st.columns([0.5, 3, 3])
            with col_check:
                new_val = st.checkbox(
                    "done", value=is_done, key=f"ck_{item['id']}_{month}",
                    label_visibility="collapsed",
                )
                if new_val != is_done:
                    set_checklist_status(item["id"], month, new_val)
                    st.rerun()

            with col_label:
                label_text = f"~~{item['label']}~~" if is_done else f"**{item['label']}**"
                st.markdown(label_text)

            with col_info:
                hints = []
                if item.get("profile_name"):
                    hints.append(f"Profile: {item['profile_name']}")
                if item.get("url"):
                    hints.append(f"[Download]({item['url']})")
                if item.get("notes"):
                    hints.append(item["notes"])
                if item_status.get("source_filename"):
                    hints.append(f"_{item_status['source_filename']}_")
                st.caption(" · ".join(hints) if hints else "")

        st.markdown("---")

    # ── File upload ───────────────────────────────────────────────────────────
    profiles = load_profiles()
    profile_names = ["(auto-detect)"] + [p["name"] for p in profiles]

    col_csv, col_pdf = st.columns(2)
    with col_csv:
        csv_files = st.file_uploader(
            "Upload CSV files", type=["csv"], accept_multiple_files=True, key="csv_up"
        )
    with col_pdf:
        pdf_files = st.file_uploader(
            "Upload PDF statements", type=["pdf"], accept_multiple_files=True, key="pdf_up"
        )

    all_files = list(csv_files or []) + list(pdf_files or [])

    if not all_files:
        st.info("Upload one or more CSV or PDF files to get started.")
        st.stop()

    # ── Entity mismatch warnings ──────────────────────────────────────────────
    for f in all_files:
        suggested_entity, match_label = suggest_entity_for_file(f.name, all_items)
        if suggested_entity and suggested_entity != entity_lower:
            st.warning(
                f"**{f.name}** matches **{match_label}** "
                f"({suggested_entity.title()} entity). "
                f"Switch to {suggested_entity.title()} to import correctly."
            )

    # ── Per-file profile selectors ────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Assign profiles")
    st.caption("Choose an import profile for each file.")

    file_profiles = {}
    for f in all_files:
        # Auto-suggest profile based on checklist filename_pattern
        default_idx = 0
        for item in all_items:
            pattern = (item.get("filename_pattern") or "").strip().lower()
            if pattern and pattern in f.name.lower() and item.get("profile_name"):
                try:
                    default_idx = profile_names.index(item["profile_name"])
                except ValueError:
                    pass
                break

        selected = st.selectbox(
            f"**{f.name}**",
            profile_names,
            index=default_idx,
            key=f"profile_{f.name}",
        )
        file_profiles[f.name] = next(
            (p for p in profiles if p["name"] == selected), None
        )

    # ── Parse & preview ───────────────────────────────────────────────────────
    if "parsed_dfs" not in st.session_state:
        st.session_state.parsed_dfs = {}

    st.markdown("---")
    if st.button("Parse & Preview", type="primary"):
        st.session_state.parsed_dfs = {}

        for f in all_files:
            prof = file_profiles.get(f.name)
            is_pdf = f.name.lower().endswith(".pdf")

            if is_pdf:
                raw, errors = parse_pdf(f)
                if raw.empty:
                    st.session_state.parsed_dfs[f.name] = ("pdf", None, "; ".join(errors))
                else:
                    try:
                        norm = normalize_transactions(raw, source_filename=f.name, profile=prof)
                        st.session_state.parsed_dfs[f.name] = (
                            "pdf", norm, "; ".join(errors) if errors else None
                        )
                    except Exception as exc:
                        st.session_state.parsed_dfs[f.name] = ("pdf", None, str(exc))
            else:
                try:
                    raw = parse_csv(f, profile=prof)
                    norm = normalize_transactions(raw, source_filename=f.name, profile=prof)
                    st.session_state.parsed_dfs[f.name] = ("csv", norm, None)
                except Exception as exc:
                    st.session_state.parsed_dfs[f.name] = ("csv", None, str(exc))

    # ── Show previews ──────────────────────────────────────────────────────────
    parsed = st.session_state.get("parsed_dfs", {})
    if not parsed:
        st.stop()

    all_ok = {}
    for fname, (ftype, df, err) in parsed.items():
        with st.expander(f"📄 {fname}", expanded=True):
            if err:
                st.warning(f"Extraction warnings: {err}")
            if df is None or df.empty:
                st.error("Could not extract any transactions from this file.")
                continue

            # ── Summary stats ─────────────────────────────────────────────
            stat_parts = [f"**{len(df)} transactions**"]

            if "date" in df.columns:
                dates = pd.to_datetime(df["date"], errors="coerce").dropna()
                if not dates.empty:
                    min_d = dates.min().strftime("%b %d")
                    max_d = dates.max().strftime("%b %d, %Y")
                    stat_parts.append(f"{min_d} – {max_d}")

            st.write(" · ".join(stat_parts))

            # Credits / debits summary
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

            # ── Data table ────────────────────────────────────────────────
            display_cols = ["date", "description_raw", "amount", "account", "currency"]
            st.dataframe(
                df[[c for c in display_cols if c in df.columns]],
                use_container_width=True,
                height=220,
            )
            all_ok[fname] = df

    if not all_ok:
        st.stop()

    # ── Import button ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.write(f"Ready to import **{sum(len(d) for d in all_ok.values())} total transactions**")
    if st.button("Import All", type="primary"):
        total_new = total_skip = 0
        for fname, df in all_ok.items():
            inserted, skipped = commit_transactions(df, entity_lower)
            total_new  += inserted
            total_skip += skipped

        # Auto-check matching checklist items
        imported_names = list(all_ok.keys())
        matched = auto_check_by_filename(imported_names, month)

        msg = f"Imported **{total_new} new** / skipped **{total_skip} duplicates**"
        if matched:
            msg += f"  \nAuto-checked: {', '.join(matched)}"
        st.success(msg)
        st.session_state.parsed_dfs = {}
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Manage Profiles
# ═══════════════════════════════════════════════════════════════════════════════
with tab_profiles:
    st.subheader("Import Profiles")
    st.caption(
        "Profiles let you map column names once per bank/issuer and reuse them on future imports."
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


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Monthly Sources
# ═══════════════════════════════════════════════════════════════════════════════
with tab_checklist:
    st.subheader("Monthly Import Sources")
    st.caption(
        "Define which statements you expect to import each month. "
        "Items auto-check when an uploaded filename matches the pattern."
    )

    profiles = load_profiles()
    profile_options = ["(none)"] + [p["name"] for p in profiles]
    all_items_tab = load_checklist_all()

    if all_items_tab:
        for item in all_items_tab:
            item_ent = item.get("entity", "personal").title()
            with st.expander(f"{item['label']}  ({item_ent})"):
                st.write(f"**Entity:** {item_ent}")
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
            help="Case-insensitive substring to match uploaded filenames for auto-check",
        )
        cl_profile  = c1.selectbox("Auto-select profile", profile_options)
        cl_entity   = c1.selectbox("Entity", ["Personal", "Company"],
                                   index=0 if entity_lower == "personal" else 1)
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
                    item_entity=cl_entity.lower(),
                )
                st.success(f"Source '{cl_label.strip()}' added.")
                st.rerun()

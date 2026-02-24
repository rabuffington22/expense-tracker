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

from core.db import get_connection  # noqa: E402
from core.imports import (  # noqa: E402
    commit_transactions,
    normalize_transactions,
    parse_csv,
    parse_pdf,
    save_upload,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
entity = entity_selector()
entity_lower = entity.lower()

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


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_upload, tab_profiles = st.tabs(["Upload Files", "Manage Profiles"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Upload Files
# ═══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    profiles = load_profiles()
    profile_names = ["(auto-detect)"] + [p["name"] for p in profiles]
    selected_profile_name = st.selectbox("Import profile", profile_names)
    selected_profile = next(
        (p for p in profiles if p["name"] == selected_profile_name), None
    )

    col_csv, col_pdf = st.columns(2)
    with col_csv:
        csv_files = st.file_uploader(
            "Upload CSV files", type=["csv"], accept_multiple_files=True, key="csv_up"
        )
    with col_pdf:
        pdf_files = st.file_uploader(
            "Upload PDF statements", type=["pdf"], accept_multiple_files=True, key="pdf_up"
        )

    if not csv_files and not pdf_files:
        st.info("Upload one or more CSV or PDF files to get started.")
        st.stop()

    # ── Parse & preview ───────────────────────────────────────────────────────
    if "parsed_dfs" not in st.session_state:
        st.session_state.parsed_dfs = {}

    if st.button("Parse & Preview", type="primary"):
        st.session_state.parsed_dfs = {}

        # CSV
        for f in csv_files or []:
            try:
                raw = parse_csv(f, profile=selected_profile)
                norm = normalize_transactions(raw, source_filename=f.name, profile=selected_profile)
                st.session_state.parsed_dfs[f.name] = ("csv", norm, None)
            except Exception as exc:
                st.session_state.parsed_dfs[f.name] = ("csv", None, str(exc))

        # PDF
        for f in pdf_files or []:
            raw, errors = parse_pdf(f)
            if raw.empty:
                st.session_state.parsed_dfs[f.name] = ("pdf", None, "; ".join(errors))
            else:
                try:
                    norm = normalize_transactions(raw, source_filename=f.name, profile=selected_profile)
                    st.session_state.parsed_dfs[f.name] = ("pdf", norm, "; ".join(errors) if errors else None)
                except Exception as exc:
                    st.session_state.parsed_dfs[f.name] = ("pdf", None, str(exc))

    # ── Show previews ──────────────────────────────────────────────────────────
    parsed = st.session_state.get("parsed_dfs", {})
    if not parsed:
        st.stop()

    all_ok: dict[str, pd.DataFrame] = {}
    for fname, (ftype, df, err) in parsed.items():
        with st.expander(f"📄 {fname}", expanded=True):
            if err:
                st.warning(f"Extraction warnings: {err}")
            if df is None or df.empty:
                st.error("Could not extract any transactions from this file.")
                continue
            st.write(f"**{len(df)} transactions** found")
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
            path = save_upload(
                b"",  # bytes already parsed; just record filename
                fname,
            ) if False else None  # save_upload only for actual file objects
            inserted, skipped = commit_transactions(df, entity_lower)
            total_new  += inserted
            total_skip += skipped
        st.success(f"✅ Imported **{total_new} new** / skipped **{total_skip} duplicates**")
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

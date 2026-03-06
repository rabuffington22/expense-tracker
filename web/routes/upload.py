"""Upload route — bank/CC statement import."""

import io
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, session

from core.db import get_connection
from core.imports import parse_csv, parse_pdf, normalize_transactions, commit_transactions

# Temp directory for storing parsed data between upload and confirm steps
_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-uploads")
os.makedirs(_TEMP_DIR, exist_ok=True)

bp = Blueprint("upload", __name__, url_prefix="/upload")

_ROOT = Path(__file__).parent.parent.parent


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_profiles(entity_key):
    conn = get_connection(entity_key)
    try:
        rows = conn.execute("SELECT * FROM import_profiles ORDER BY name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _load_checklist(entity_key):
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT * FROM import_checklist WHERE entity=? ORDER BY sort_order, id",
            (entity_key,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _load_checklist_status(entity_key, month):
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT * FROM import_checklist_status WHERE month=?", (month,)
        ).fetchall()
        return {r["checklist_item_id"]: dict(r) for r in rows}
    finally:
        conn.close()


def _month_options(count=12):
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


def _format_month(ym):
    return datetime.strptime(ym, "%Y-%m").strftime("%b %Y")


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    tab = request.args.get("tab", "import")
    month = request.args.get("month") or _month_options()[0]
    items = _load_checklist(g.entity_key)
    status = _load_checklist_status(g.entity_key, month)
    profiles = _load_profiles(g.entity_key)
    profile_map = {p["name"]: p for p in profiles}

    # Last transaction dates per source
    conn = get_connection(g.entity_key)
    try:
        source_last_dates = {}
        for item in items:
            pattern = (item.get("filename_pattern") or "").strip()
            if pattern:
                row = conn.execute(
                    "SELECT MAX(date) FROM transactions WHERE LOWER(source_filename) LIKE ?",
                    (f"%{pattern.lower()}%",),
                ).fetchone()
                if row and row[0]:
                    source_last_dates[item["id"]] = row[0]
    finally:
        conn.close()

    done_count = sum(1 for i in items if status.get(i["id"], {}).get("completed", 0))

    return render_template(
        "upload.html",
        tab=tab,
        months=_month_options(),
        selected_month=month,
        format_month=_format_month,
        items=items,
        status=status,
        profiles=profiles,
        profile_map=profile_map,
        source_last_dates=source_last_dates,
        done_count=done_count,
        total_count=len(items),
    )


@bp.route("/import-file/<int:item_id>", methods=["GET", "POST"])
def import_file(item_id):
    """Upload dialog for a specific source."""
    month = request.args.get("month") or _month_options()[0]

    # Load checklist item
    conn = get_connection(g.entity_key)
    try:
        item = conn.execute("SELECT * FROM import_checklist WHERE id=?", (item_id,)).fetchone()
        if not item:
            flash("Source not found.", "danger")
            return redirect(url_for("upload.index", month=month))
        item = dict(item)
    finally:
        conn.close()

    profiles = _load_profiles(g.entity_key)
    profile_map = {p["name"]: p for p in profiles}
    prof_name = item.get("profile_name")
    prof = profile_map.get(prof_name) if prof_name else None

    if request.method == "GET":
        return render_template(
            "upload_dialog.html",
            item=item,
            month=month,
            format_month=_format_month,
        )

    # POST — process uploaded files
    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        flash("No files selected.", "warning")
        return redirect(url_for("upload.import_file", item_id=item_id, month=month))

    parsed_files = []
    for f in files:
        is_pdf = f.filename.lower().endswith(".pdf")
        try:
            if is_pdf:
                raw, errors = parse_pdf(f)
                if raw.empty:
                    parsed_files.append({"name": f.filename, "df": None, "error": "; ".join(errors)})
                else:
                    norm = normalize_transactions(raw, source_filename=f.filename, profile=None)
                    parsed_files.append({"name": f.filename, "df": norm, "error": "; ".join(errors) if errors else None})
            else:
                raw = parse_csv(f, profile=prof)
                norm = normalize_transactions(raw, source_filename=f.filename, profile=prof)
                parsed_files.append({"name": f.filename, "df": norm, "error": None})
        except Exception as exc:
            parsed_files.append({"name": f.filename, "df": None, "error": str(exc)})

    # Build preview data
    previews = []
    for pf in parsed_files:
        preview = {"name": pf["name"], "error": pf["error"]}
        if pf["df"] is not None and not pf["df"].empty:
            df = pf["df"]
            preview["count"] = len(df)
            dates = pd.to_datetime(df["date"], errors="coerce").dropna()
            if not dates.empty:
                preview["min_date"] = dates.min().strftime("%b %d")
                preview["max_date"] = dates.max().strftime("%b %d, %Y")
            amounts = pd.to_numeric(df["amount"], errors="coerce").dropna()
            preview["credits"] = float(amounts[amounts > 0].sum())
            preview["debits"] = float(abs(amounts[amounts < 0].sum()))
            preview["net"] = preview["credits"] - preview["debits"]

            # Auto-detect month for filename
            months_series = dates.dt.to_period("M")
            mode_months = months_series.mode()
            if len(mode_months):
                preview["detected_month"] = mode_months[0].strftime("%b %Y")
            else:
                preview["detected_month"] = _format_month(month)

            ext = Path(pf["name"]).suffix
            preview["suggested_name"] = f"{item['label']} - {preview['detected_month']}{ext}"
        previews.append(preview)

    # Store parsed data in temp file (too large for cookie session)
    temp_key = f"upload_{uuid.uuid4().hex[:12]}"
    temp_data = {
        fname: pf["df"].to_json()
        for pf in parsed_files
        if pf["df"] is not None and not pf["df"].empty
        for fname in [pf["name"]]
    }
    temp_path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
    with open(temp_path, "w") as f:
        json.dump(temp_data, f)
    session["upload_temp_key"] = temp_key

    good_count = sum(1 for p in previews if p.get("count"))
    total_txns = sum(p.get("count", 0) for p in previews)

    return render_template(
        "upload_dialog.html",
        item=item,
        month=month,
        format_month=_format_month,
        previews=previews,
        good_count=good_count,
        total_txns=total_txns,
        show_preview=True,
    )


@bp.route("/confirm/<int:item_id>", methods=["POST"])
def confirm(item_id):
    """Confirm import — commit transactions to DB."""
    month = request.form.get("month") or _month_options()[0]

    # Load parsed data from temp file
    temp_key = session.pop("upload_temp_key", None)
    upload_dfs = {}
    if temp_key:
        temp_key = os.path.basename(temp_key)  # prevent path traversal
        temp_path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
        if os.path.exists(temp_path):
            with open(temp_path) as f:
                upload_dfs = json.load(f)
            os.remove(temp_path)

    if not upload_dfs:
        flash("No data to import. Please upload files again.", "warning")
        return redirect(url_for("upload.index", month=month))

    total_new = 0
    total_skip = 0
    saved_names = []

    for fname, json_data in upload_dfs.items():
        df = pd.read_json(io.StringIO(json_data))
        # read_json auto-parses date-like columns to Timestamp — convert back
        # to strings so they can be bound to SQLite TEXT columns.
        for col in ("date", "imported_at"):
            if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime("%Y-%m-%d" if col == "date" else "%Y-%m-%dT%H:%M:%S%z")
        inserted, skipped = commit_transactions(df, g.entity_key)
        total_new += inserted
        total_skip += skipped

        # Get renamed filename from form
        save_name = request.form.get(f"rename_{fname}", fname).strip()
        if not save_name:
            save_name = fname
        if not Path(save_name).suffix:
            save_name += Path(fname).suffix
        saved_names.append(save_name)

    # Mark source complete
    conn = get_connection(g.entity_key)
    try:
        now = datetime.now(timezone.utc).isoformat()
        all_filenames = ", ".join(saved_names)
        conn.execute(
            """INSERT INTO import_checklist_status
               (checklist_item_id, month, completed, completed_at, source_filename)
               VALUES (?, ?, 1, ?, ?)
               ON CONFLICT(checklist_item_id, month)
               DO UPDATE SET completed=1, completed_at=?, source_filename=?""",
            (item_id, month, now, all_filenames, now, all_filenames),
        )
        conn.commit()
    finally:
        conn.close()

    flash(f"Imported {total_new} new / skipped {total_skip} duplicates.", "success")
    return redirect(url_for("upload.index", month=month))


@bp.route("/undo/<int:item_id>", methods=["POST"])
def undo(item_id):
    """Undo import completion for a source."""
    month = request.form.get("month") or _month_options()[0]
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            """INSERT INTO import_checklist_status
               (checklist_item_id, month, completed, completed_at, source_filename)
               VALUES (?, ?, 0, NULL, '')
               ON CONFLICT(checklist_item_id, month)
               DO UPDATE SET completed=0, completed_at=NULL, source_filename=''""",
            (item_id, month),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("upload.index", month=month))


# ── Settings routes ──────────────────────────────────────────────────────────

@bp.route("/add-source", methods=["POST"])
def add_source():
    label = request.form.get("label", "").strip()
    if not label:
        flash("Source name is required.", "danger")
        return redirect(url_for("upload.index", tab="settings"))

    pattern = request.form.get("pattern", "").strip()
    profile = request.form.get("profile", "")
    if profile == "(none)":
        profile = ""
    url_val = request.form.get("url", "").strip()
    notes = request.form.get("notes", "").strip()

    conn = get_connection(g.entity_key)
    try:
        max_order = conn.execute("SELECT COALESCE(MAX(sort_order),0) FROM import_checklist").fetchone()[0]
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO import_checklist
               (label, filename_pattern, profile_name, url, notes, sort_order, entity, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (label, pattern or None, profile or None, url_val or None,
             notes or None, max_order + 1, g.entity_key, now),
        )
        conn.commit()
    finally:
        conn.close()
    flash(f"Source '{label}' added.", "success")
    return redirect(url_for("upload.index", tab="settings"))


@bp.route("/delete-source/<int:item_id>", methods=["POST"])
def delete_source(item_id):
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM import_checklist WHERE id=?", (item_id,))
        conn.execute("DELETE FROM import_checklist_status WHERE checklist_item_id=?", (item_id,))
        conn.commit()
    finally:
        conn.close()
    flash("Source deleted.", "success")
    return redirect(url_for("upload.index", tab="settings"))


@bp.route("/add-profile", methods=["POST"])
def add_profile():
    name = request.form.get("name", "").strip()
    date_col = request.form.get("date_col", "").strip()
    desc_col = request.form.get("desc_col", "").strip()
    amt_col = request.form.get("amt_col", "").strip()

    if not all([name, date_col, desc_col, amt_col]):
        flash("Name, Date, Description, and Amount columns are required.", "danger")
        return redirect(url_for("upload.index", tab="settings"))

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            """INSERT OR REPLACE INTO import_profiles
               (name, date_col, description_col, amount_col, merchant_col,
                account_col, currency_col, amount_negate, date_format, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (name, date_col, desc_col, amt_col,
             request.form.get("merchant_col", "").strip() or None,
             request.form.get("account_col", "").strip() or None,
             request.form.get("currency_col", "").strip() or None,
             1 if request.form.get("negate") else 0,
             request.form.get("date_format", "").strip() or None,
             now),
        )
        conn.commit()
    finally:
        conn.close()
    flash(f"Profile '{name}' saved.", "success")
    return redirect(url_for("upload.index", tab="settings"))


@bp.route("/delete-profile/<name>", methods=["POST"])
def delete_profile(name):
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM import_profiles WHERE name=?", (name,))
        conn.commit()
    finally:
        conn.close()
    flash(f"Profile '{name}' deleted.", "success")
    return redirect(url_for("upload.index", tab="settings"))

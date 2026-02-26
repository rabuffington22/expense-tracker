"""Categorize route — review/suggest/accept categories + manage categories & aliases."""

import re
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, session

from core.db import get_connection
from core.categorize import suggest_categories, apply_aliases_to_db
from core.reporting import get_uncategorized

bp = Blueprint("categorize", __name__, url_prefix="/categorize")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_categories(entity_key):
    conn = get_connection(entity_key)
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def _get_subcategories(entity_key, category):
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT id, name FROM subcategories WHERE category_name = ? ORDER BY name",
            (category,),
        ).fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]
    finally:
        conn.close()


def _load_aliases(entity_key):
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT id, pattern_type, pattern, merchant_canonical, "
            "default_category, active FROM merchant_aliases ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    tab = request.args.get("tab", "review")
    raw = get_uncategorized(g.entity_key)
    categories = _get_categories(g.entity_key) + ["Uncategorized"]

    # Check if we have suggested data in session
    suggested = session.get("categorize_suggested")
    txns = []
    if not raw.empty:
        for _, row in raw.iterrows():
            txn = row.to_dict()
            # If we have suggestions, overlay them
            if suggested and txn.get("transaction_id") in suggested:
                s = suggested[txn["transaction_id"]]
                txn["category"] = s.get("category", txn.get("category", ""))
                txn["confidence"] = s.get("confidence", txn.get("confidence", 0))
            txns.append(txn)

    # Settings tab data
    cats = _get_categories(g.entity_key)
    aliases = _load_aliases(g.entity_key)

    return render_template(
        "categorize.html",
        tab=tab,
        txns=txns,
        txn_count=len(txns),
        categories=categories,
        cats=cats,
        aliases=aliases,
        has_suggestions=bool(suggested),
    )


@bp.route("/suggest", methods=["POST"])
def suggest():
    """Run suggestion engine and store results in session."""
    raw = get_uncategorized(g.entity_key)
    if raw.empty:
        flash("No transactions to suggest categories for.", "info")
        return redirect(url_for("categorize.index"))

    result = suggest_categories(raw.copy(), g.entity_key)

    # Store suggestions in session keyed by transaction_id
    suggestions = {}
    for _, row in result.iterrows():
        tid = row.get("transaction_id")
        if tid:
            suggestions[tid] = {
                "category": row.get("category", ""),
                "confidence": float(row.get("confidence", 0)),
            }

    session["categorize_suggested"] = suggestions
    flash(f"Suggestions applied to {len(suggestions)} transactions. Review and accept below.", "success")
    return redirect(url_for("categorize.index"))


@bp.route("/accept", methods=["POST"])
def accept():
    """Accept category assignments from the review table."""
    txn_ids = request.form.getlist("txn_id")
    if not txn_ids:
        flash("Nothing to save.", "warning")
        return redirect(url_for("categorize.index"))

    conn = get_connection(g.entity_key)
    aliases_created = 0
    saved_count = 0
    try:
        for tid in txn_ids:
            cat = request.form.get(f"cat_{tid}", "").strip()
            notes = request.form.get(f"notes_{tid}", "").strip()

            if cat == "Uncategorized":
                cat = ""

            conn.execute(
                "UPDATE transactions SET category=?, confidence=1.0, notes=? "
                "WHERE transaction_id=?",
                (cat, notes, tid),
            )
            saved_count += 1

            # Auto-create merchant alias for future matching
            if cat:
                desc = request.form.get(f"desc_{tid}", "").strip()
                if desc:
                    pattern = re.sub(
                        r"^(paypal\s*\*|venmo\s*\*|zelle\s*\*|sq\s*\*|tst\s*\*|sp\s*\*)\s*",
                        "", desc, flags=re.IGNORECASE,
                    ).strip()
                    if len(pattern) >= 4:
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

    session.pop("categorize_suggested", None)
    msg = f"Saved {saved_count} transaction(s)."
    if aliases_created:
        msg += f" Created {aliases_created} merchant alias(es) for future matching."
    flash(msg, "success")
    return redirect(url_for("categorize.index"))


@bp.route("/reapply-aliases", methods=["POST"])
def reapply_aliases():
    """Re-run all active alias rules against every transaction."""
    updated = apply_aliases_to_db(g.entity_key)
    flash(f"Updated {updated} transaction(s).", "success")
    return redirect(url_for("categorize.index", tab="settings"))


# ── Category CRUD ────────────────────────────────────────────────────────────

@bp.route("/add-category", methods=["POST"])
def add_category():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name cannot be blank.", "danger")
        return redirect(url_for("categorize.index", tab="settings"))

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO categories (name, created_at) VALUES (?,?)",
            (name, now),
        )
        conn.commit()
    finally:
        conn.close()
    flash(f"Category '{name}' added.", "success")
    return redirect(url_for("categorize.index", tab="settings"))


@bp.route("/delete-category/<name>", methods=["POST"])
def delete_category(name):
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM categories WHERE name=?", (name,))
        conn.commit()
    finally:
        conn.close()
    flash(f"Category '{name}' deleted.", "success")
    return redirect(url_for("categorize.index", tab="settings"))


@bp.route("/rename-category", methods=["POST"])
def rename_category():
    old_name = request.form.get("old_name", "").strip()
    new_name = request.form.get("new_name", "").strip()
    if not old_name or not new_name:
        flash("Both old and new names are required.", "danger")
        return redirect(url_for("categorize.index", tab="settings"))

    conn = get_connection(g.entity_key)
    try:
        conn.execute("UPDATE categories SET name=? WHERE name=?", (new_name, old_name))
        conn.execute("UPDATE transactions SET category=? WHERE category=?", (new_name, old_name))
        conn.execute(
            "UPDATE merchant_aliases SET default_category=? WHERE default_category=?",
            (new_name, old_name),
        )
        conn.commit()
    finally:
        conn.close()
    flash(f"Renamed '{old_name}' to '{new_name}'.", "success")
    return redirect(url_for("categorize.index", tab="settings"))


# ── Subcategory CRUD ─────────────────────────────────────────────────────────

@bp.route("/add-subcategory", methods=["POST"])
def add_subcategory():
    cat = request.form.get("category", "").strip()
    name = request.form.get("name", "").strip()
    if not cat or not name:
        flash("Category and subcategory name are required.", "danger")
        return redirect(url_for("categorize.index", tab="settings"))

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) VALUES (?,?,?)",
            (cat, name, now),
        )
        conn.commit()
    finally:
        conn.close()
    flash(f"Subcategory '{name}' added to {cat}.", "success")
    return redirect(url_for("categorize.index", tab="settings"))


@bp.route("/delete-subcategory/<int:sub_id>", methods=["POST"])
def delete_subcategory(sub_id):
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM subcategories WHERE id=?", (sub_id,))
        conn.commit()
    finally:
        conn.close()
    flash("Subcategory deleted.", "success")
    return redirect(url_for("categorize.index", tab="settings"))


@bp.route("/subcategories")
def subcategories():
    """HTMX endpoint — return subcategory <option> tags for a category."""
    cat = request.args.get("category", "")
    subs = _get_subcategories(g.entity_key, cat)
    sub_names = [s["name"] for s in subs]
    if "Unknown" not in sub_names:
        sub_names.append("Unknown")
    options = "".join(f'<option value="{s}">{s}</option>' for s in sub_names)
    return options


# ── Merchant Alias CRUD ──────────────────────────────────────────────────────

@bp.route("/add-alias", methods=["POST"])
def add_alias():
    ptype = request.form.get("pattern_type", "contains")
    pattern = request.form.get("pattern", "").strip()
    canonical = request.form.get("canonical", "").strip()
    def_cat = request.form.get("default_category", "")
    active = 1 if request.form.get("active") else 1  # default active

    if not pattern or not canonical:
        flash("Pattern and canonical name are required.", "danger")
        return redirect(url_for("categorize.index", tab="settings"))

    if def_cat == "(none)":
        def_cat = None

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO merchant_aliases "
            "(pattern_type, pattern, merchant_canonical, default_category, active, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (ptype, pattern, canonical, def_cat or None, active, now),
        )
        conn.commit()
    finally:
        conn.close()
    flash(f"Alias saved: '{pattern}' -> {canonical}", "success")
    return redirect(url_for("categorize.index", tab="settings"))


@bp.route("/toggle-alias/<int:alias_id>", methods=["POST"])
def toggle_alias(alias_id):
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute("SELECT active FROM merchant_aliases WHERE id=?", (alias_id,)).fetchone()
        if row:
            conn.execute(
                "UPDATE merchant_aliases SET active=? WHERE id=?",
                (0 if row[0] else 1, alias_id),
            )
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for("categorize.index", tab="settings"))


@bp.route("/delete-alias/<int:alias_id>", methods=["POST"])
def delete_alias(alias_id):
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM merchant_aliases WHERE id=?", (alias_id,))
        conn.commit()
    finally:
        conn.close()
    flash("Alias deleted.", "success")
    return redirect(url_for("categorize.index", tab="settings"))

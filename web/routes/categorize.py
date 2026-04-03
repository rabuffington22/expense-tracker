"""Categorize route — review/suggest/accept categories + manage categories & aliases."""

import math
import re
from datetime import datetime, timezone

from markupsafe import escape
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, session

from core.db import get_connection
from core.categorize import suggest_categories, apply_aliases_to_db
from core.reporting import get_uncategorized
from web import get_categories

bp = Blueprint("categorize", __name__, url_prefix="/categorize")


# Patterns for vendor transactions that have unique per-transaction reference
# codes — aliases created from these will never match future transactions.
_VENDOR_PATTERNS = re.compile(
    r"(?i)"
    r"(amazon\.com\*|amazon mktpl\*|amzn mktp|amzn\.com/bill"
    r"|henry schein"
    r"|wholefds|whole foods)"
)


def _is_vendor_transaction(description: str) -> bool:
    """Return True if description looks like a vendor order (Amazon, etc.)."""
    return bool(_VENDOR_PATTERNS.search(description))


# ── Helpers ──────────────────────────────────────────────────────────────────


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

_PAGE_SIZE = 50


@bp.route("/")
def index():
    tab = request.args.get("tab", "review")
    raw = get_uncategorized(g.entity_key)
    categories = get_categories(g.entity_key) + ["Uncategorized"]

    # Check if we have suggested data in session
    suggested = session.get("categorize_suggested")
    all_txns = []
    if not raw.empty:
        for _, row in raw.iterrows():
            txn = row.to_dict()
            # If we have suggestions, overlay them
            if suggested and txn.get("transaction_id") in suggested:
                s = suggested[txn["transaction_id"]]
                txn["category"] = s.get("category", txn.get("category", ""))
                txn["subcategory"] = s.get("subcategory") or txn.get("subcategory", "")
                txn["confidence"] = s.get("confidence", txn.get("confidence", 0))
            all_txns.append(txn)

    # Pagination
    total_count = len(all_txns)
    page = request.args.get("page", 1, type=int)
    total_pages = max(1, (total_count + _PAGE_SIZE - 1) // _PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * _PAGE_SIZE
    txns = all_txns[start:start + _PAGE_SIZE]

    # Settings tab data
    cats = get_categories(g.entity_key)
    aliases = _load_aliases(g.entity_key)

    return render_template(
        "categorize.html",
        tab=tab,
        txns=txns,
        txn_count=total_count,
        categories=categories,
        cats=cats,
        aliases=aliases,
        has_suggestions=bool(suggested),
        page=page,
        total_pages=total_pages,
        page_size=_PAGE_SIZE,
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
            conf_raw = row.get("confidence", 0)
            try:
                conf = float(conf_raw)
                if math.isnan(conf):
                    conf = 0.0
            except (TypeError, ValueError):
                conf = 0.0
            suggestions[tid] = {
                "category": row.get("category", "") or "",
                "subcategory": row.get("subcategory", "") or "",
                "confidence": conf,
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
            subcat = request.form.get(f"subcat_{tid}", "").strip()
            notes = request.form.get(f"notes_{tid}", "").strip()

            if cat == "Uncategorized":
                cat = ""

            if not subcat or subcat == "Unknown":
                subcat = None

            conn.execute(
                "UPDATE transactions SET category=?, subcategory=?, confidence=1.0, notes=? "
                "WHERE transaction_id=?",
                (cat, subcat, notes, tid),
            )
            saved_count += 1

            # Auto-create merchant alias for future matching
            # Skip for vendor transactions (Amazon, etc.) — they have unique
            # per-transaction reference codes that will never match again.
            if cat:
                desc = request.form.get(f"desc_{tid}", "").strip()
                if desc and not _is_vendor_transaction(desc):
                    # Strip platform prefixes
                    pattern = re.sub(
                        r"^(paypal\s*\*|venmo\s*\*|zelle\s*\*|sq\s*\*|tst\s*\*|sp\s*\*)\s*",
                        "", desc, flags=re.IGNORECASE,
                    ).strip()
                    # Strip trailing location info (city ST)
                    pattern = re.sub(r"\s+\w{2}\s*$", "", pattern).strip()
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


# ── Category/Subcategory CRUD removed ────────────────────────────────────────
# Categories and subcategories are defined in categories.md (single source of
# truth). Edit that file to add, rename, or delete categories. The DB is synced
# from the file on app startup.


@bp.route("/subcategories")
def subcategories():
    """HTMX endpoint — return subcategory <option> tags for a category."""
    cat = request.args.get("category", "")
    subs = _get_subcategories(g.entity_key, cat)
    sub_names = [s["name"] for s in subs]
    if "Unknown" not in sub_names:
        sub_names.append("Unknown")
    options = "".join(f'<option value="{escape(s)}">{escape(s)}</option>' for s in sub_names)
    return options


@bp.route("/all-subcategories")
def all_subcategories():
    """Return all subcategories as JSON map {category: [sub1, sub2, ...]}."""
    from flask import jsonify
    cats = get_categories(g.entity_key)
    result = {}
    for cat in cats:
        subs = _get_subcategories(g.entity_key, cat)
        names = [s["name"] for s in subs]
        if "Unknown" not in names:
            names.append("Unknown")
        result[cat] = names
    return jsonify(result)


# ── Merchant Alias CRUD ──────────────────────────────────────────────────────

@bp.route("/add-alias", methods=["POST"])
def add_alias():
    ptype = request.form.get("pattern_type", "contains")
    pattern = request.form.get("pattern", "").strip()
    canonical = request.form.get("canonical", "").strip()
    def_cat = request.form.get("default_category", "")
    active = 1 if request.form.get("active") else 0

    if not pattern or not canonical:
        flash("Pattern and canonical name are required.", "danger")
        return redirect(url_for("categorize.index", tab="settings"))

    if def_cat == "(none)":
        def_cat = None

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(g.entity_key)
    try:
        # Check for duplicate pattern to avoid silent overwrites
        existing = conn.execute(
            "SELECT id, merchant_canonical FROM merchant_aliases "
            "WHERE pattern_type=? AND LOWER(pattern)=LOWER(?)",
            (ptype, pattern),
        ).fetchone()
        if existing:
            flash(
                f"Alias pattern '{pattern}' already exists "
                f"(maps to '{existing['merchant_canonical']}'). "
                f"Delete or edit the existing alias first.",
                "warning",
            )
            return redirect(url_for("categorize.index", tab="settings"))

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


# ── Orphan resolution ────────────────────────────────────────────────────────

@bp.route("/orphans")
def orphans():
    """Show categories removed from categories.md that still have transactions."""
    from web import get_category_orphans
    orphan_list = get_category_orphans(g.entity_key)
    categories = get_categories(g.entity_key)
    return render_template(
        "categorize_orphans.html",
        orphans=orphan_list,
        categories=categories,
    )


@bp.route("/orphans/reassign", methods=["POST"])
def orphans_reassign():
    """Reassign all transactions from an orphaned category to a new one."""
    from web import get_category_orphans, clear_category_orphan

    old_category = request.form.get("old_category", "").strip()
    old_subcategory = request.form.get("old_subcategory", "").strip() or None
    new_category = request.form.get("new_category", "").strip()
    new_subcategory = request.form.get("new_subcategory", "").strip() or "General"

    if not old_category or not new_category:
        flash("Both old and new categories are required.", "danger")
        return redirect(url_for("categorize.orphans"))

    conn = get_connection(g.entity_key)
    try:
        if old_subcategory:
            # Subcategory-level orphan: only reassign transactions with this specific subcat
            _tables_with_subcat = [
                ("transactions", "category", "subcategory"),
                ("amazon_orders", "category", "subcategory"),
                ("transaction_splits", "category", "subcategory"),
                ("order_line_items", "category", "subcategory"),
            ]
            for table, cat_col, sub_col in _tables_with_subcat:
                conn.execute(
                    f"UPDATE {table} SET {cat_col}=?, {sub_col}=? "
                    f"WHERE {cat_col}=? AND {sub_col}=?",
                    (new_category, new_subcategory, old_category, old_subcategory),
                )
            conn.execute(
                "DELETE FROM budget_subcategories WHERE category=? AND subcategory=?",
                (old_category, old_subcategory),
            )
            # Delete the orphaned subcategory row
            conn.execute(
                "DELETE FROM subcategories WHERE category_name=? AND name=?",
                (old_category, old_subcategory),
            )
        else:
            # Whole-category orphan: reassign everything
            _tables_cat_only = [
                ("transactions", "category"),
                ("amazon_orders", "category"),
                ("transaction_splits", "category"),
                ("order_line_items", "category"),
                ("merchant_aliases", "default_category"),
                ("budget_items", "category"),
                ("budget_subcategories", "category"),
            ]
            for table, col in _tables_cat_only:
                conn.execute(
                    f"UPDATE {table} SET {col}=? WHERE {col}=?",
                    (new_category, old_category),
                )
            # Also update subcategory columns to the new subcategory
            _tables_with_subcat = [
                ("transactions", "subcategory"),
                ("amazon_orders", "subcategory"),
                ("transaction_splits", "subcategory"),
                ("order_line_items", "subcategory"),
            ]
            for table, col in _tables_with_subcat:
                conn.execute(
                    f"UPDATE {table} SET {col}=? WHERE category=? AND ({col} IS NULL OR {col}='' OR {col}='General')",
                    (new_subcategory, new_category),
                )
            # Delete the orphaned category and its subcategories
            conn.execute("DELETE FROM subcategories WHERE category_name=?", (old_category,))
            conn.execute("DELETE FROM categories WHERE name=?", (old_category,))

        conn.commit()
    finally:
        conn.close()

    clear_category_orphan(g.entity_key, old_category, old_subcategory)

    label = f"{old_category}/{old_subcategory}" if old_subcategory else old_category
    flash(f"Reassigned all '{label}' transactions to {new_category}/{new_subcategory}.", "success")

    # If more orphans remain, go back to the orphans page
    remaining = get_category_orphans(g.entity_key)
    if remaining:
        return redirect(url_for("categorize.orphans"))

    # Clear the session warning flag so it doesn't persist
    session.pop(f"orphan_warning_{g.entity_key}", None)
    return redirect(url_for("categorize.index"))

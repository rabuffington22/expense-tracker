"""Transactions route — universal drill target with filters, pagination, HTMX."""

import re
import math
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, g, jsonify, redirect, make_response
from markupsafe import escape

from core.db import get_connection
from web import get_categories, get_subcategories

bp = Blueprint("transactions", __name__, url_prefix="/transactions")

_PAGE_SIZE = 50


@bp.app_template_global()
def txn_page_url(params, page_num):
    """Build a pagination URL preserving all current filter params."""
    from flask import url_for as _url_for
    qp = {k: v for k, v in params.items() if v}
    qp["page"] = str(page_num)
    return _url_for("transactions.partial", **qp)

# ── Whitelisted sort (D4) ────────────────────────────────────────────────────

_SORT_MAP = {
    "date": "t.date",
    "amount": "ABS(t.amount_cents)",
    "merchant": "t.merchant_canonical",
    "category": "t.category",
    "subcategory": "t.subcategory",
}

# ── Vendor patterns for heuristic fallback (D1) ─────────────────────────────

_VENDOR_PATTERN_SQL = """(
    LOWER(t.merchant_canonical) LIKE '%amazon%'
    OR LOWER(t.description_raw) LIKE '%amzn%'
    OR LOWER(t.description_raw) LIKE '%henry schein%'
)"""


# ── Query builder (D2 — shared base CTE) ────────────────────────────────────

def _build_base_cte(conn, params):
    """
    Build the filtered transaction_id CTE.

    Returns (cte_sql, cte_params).
    Both count and rows queries use this same CTE so pagination is always correct.
    """
    conditions = []
    sql_params = []

    # Type filter
    if params.get("type") == "income":
        conditions.append("t.amount_cents > 0")
    elif params.get("type") == "expense":
        conditions.append("t.amount_cents < 0")

    # Category by ID — resolve name in Python, then filter by name (D5)
    cat_id = params.get("category_id")
    if cat_id:
        try:
            cat_row = conn.execute(
                "SELECT name FROM categories WHERE id = ?", (int(cat_id),)
            ).fetchone()
            if cat_row:
                conditions.append("t.category = ?")
                sql_params.append(cat_row["name"])
        except (ValueError, TypeError):
            pass  # Invalid category_id — ignore

    # Subcategory filter
    subcat = params.get("subcategory", "").strip()
    if subcat:
        conditions.append("t.subcategory = ?")
        sql_params.append(subcat)

    # Uncategorized
    if params.get("uncategorized") == "1":
        conditions.append(
            "(t.category IS NULL OR t.category = '' OR t.confidence < 0.6)"
        )

    # Possible transfer — uncategorized txns with transfer/payment keywords
    if params.get("possible_transfer") == "1":
        conditions.append(
            "(t.category IS NULL OR t.category = '' OR t.category = 'Unknown') "
            "AND (LOWER(t.description_raw) LIKE '%transfer%' "
            "  OR LOWER(t.description_raw) LIKE '%payment%' "
            "  OR LOWER(t.description_raw) LIKE '%autopay%')"
        )

    # Merchant LIKE
    merchant = params.get("merchant", "").strip()
    if merchant:
        conditions.append(
            "(t.merchant_canonical LIKE ? OR t.description_raw LIKE ?)"
        )
        sql_params.extend([f"%{merchant}%", f"%{merchant}%"])

    # Date range
    if params.get("start"):
        conditions.append("t.date >= ?")
        sql_params.append(params["start"])
    if params.get("end"):
        conditions.append("t.date <= ?")
        sql_params.append(params["end"])

    # Free-text search
    q = params.get("q", "").strip()
    if q:
        conditions.append(
            "(t.description_raw LIKE ? OR t.merchant_canonical LIKE ? "
            "OR t.notes LIKE ? OR COALESCE(t.category,'') LIKE ?)"
        )
        like = f"%{q}%"
        sql_params.extend([like, like, like, like])

    # Account
    if params.get("account"):
        conditions.append("t.account = ?")
        sql_params.append(params["account"])

    # Large transactions (>= $500, exclude transfers/CC payments)
    if params.get("large_txns") == "1":
        conditions.append("ABS(t.amount_cents) >= 50000")
        conditions.append(
            "COALESCE(t.category, '') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')"
        )

    # New merchants (seen in date range but not in prior 90 days)
    if params.get("new_merchants") == "1":
        conditions.append("t.merchant_canonical IS NOT NULL")
        conditions.append("t.merchant_canonical != ''")
        conditions.append(
            "COALESCE(t.category, '') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')"
        )
        # Use 90 days before start date as the lookback cutoff
        nm_start = params.get("start", "")
        if nm_start:
            import datetime
            try:
                start_dt = datetime.datetime.strptime(nm_start, "%Y-%m-%d").date()
                lookback = (start_dt - datetime.timedelta(days=90)).isoformat()
                conditions.append(
                    "t.merchant_canonical NOT IN ("
                    "  SELECT DISTINCT merchant_canonical FROM transactions "
                    "  WHERE date >= ? AND date < ? "
                    "  AND merchant_canonical IS NOT NULL AND merchant_canonical != '')"
                )
                sql_params.extend([lookback, nm_start])
            except (ValueError, TypeError):
                pass

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Vendor breakdown: linkage-first, heuristic-fallback (D1)
    # WHERE clause appears twice (UNION), so params must be doubled.
    if params.get("vendor_breakdown") == "1":
        cte = f"""
        WITH base AS (
            -- Primary: linked txns with < 95% coverage
            SELECT t.transaction_id
            FROM transactions t
            INNER JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id
            {where}
            GROUP BY t.transaction_id
            HAVING COALESCE(SUM(ABS(ao.order_total_cents)), 0)
                   < ABS(t.amount_cents) * 95 / 100

            UNION

            -- Fallback: unlinked txns matching vendor patterns (no orders at all)
            SELECT t.transaction_id
            FROM transactions t
            LEFT JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id
            {where}
              {"AND" if conditions else "WHERE"} {_VENDOR_PATTERN_SQL}
              AND t.amount_cents < -2500
            GROUP BY t.transaction_id
            HAVING COUNT(ao.id) = 0
        )
        """
        sql_params = sql_params + sql_params  # duplicate for both UNION branches
    else:
        cte = f"""
        WITH base AS (
            SELECT t.transaction_id
            FROM transactions t
            {where}
        )
        """

    return cte, sql_params


def _get_filter_params():
    """Extract and return all filter params from request.args."""
    return {
        "type": request.args.get("type", ""),
        "category_id": request.args.get("category_id", ""),
        "subcategory": request.args.get("subcategory", ""),
        "merchant": request.args.get("merchant", ""),
        "uncategorized": request.args.get("uncategorized", ""),
        "vendor_breakdown": request.args.get("vendor_breakdown", ""),
        "possible_transfer": request.args.get("possible_transfer", ""),
        "large_txns": request.args.get("large_txns", ""),
        "new_merchants": request.args.get("new_merchants", ""),
        "q": request.args.get("q", ""),
        "start": request.args.get("start", ""),
        "end": request.args.get("end", ""),
        "account": request.args.get("account", ""),
        "sort": request.args.get("sort", ""),
        "dir": request.args.get("dir", ""),
    }


def _query_transactions(entity_key, params, page):
    """Execute the CTE-based query and return (txns, total_count, total_pages)."""
    conn = get_connection(entity_key)
    try:
        cte, cte_params = _build_base_cte(conn, params)

        # Count query
        count_sql = f"{cte}\nSELECT COUNT(*) FROM base"
        total_count = conn.execute(count_sql, cte_params).fetchone()[0]
        total_pages = max(1, math.ceil(total_count / _PAGE_SIZE))

        # Clamp page
        page = max(1, min(page, total_pages))
        offset = (page - 1) * _PAGE_SIZE

        # Sort (D4 — whitelisted)
        sort_col = _SORT_MAP.get(params.get("sort", ""), "t.date")
        sort_dir = "ASC" if params.get("dir") == "asc" else "DESC"

        # Rows query with allocation data for badge display
        rows_sql = f"""
        {cte}
        SELECT t.*,
               COUNT(ao.id) AS alloc_count,
               COALESCE(SUM(ABS(ao.order_total_cents)), 0) AS alloc_total_cents,
               GROUP_CONCAT(ao.product_summary, ' || ') AS alloc_products
        FROM transactions t
        JOIN base b ON b.transaction_id = t.transaction_id
        LEFT JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id
        GROUP BY t.transaction_id
        ORDER BY {sort_col} {sort_dir}
        LIMIT ? OFFSET ?
        """
        rows = conn.execute(rows_sql, cte_params + [_PAGE_SIZE, offset]).fetchall()
        txns = [dict(r) for r in rows]

        # Also get category name for the active filter (for display)
        category_name = None
        cat_id = params.get("category_id")
        if cat_id:
            try:
                cat_row = conn.execute(
                    "SELECT name FROM categories WHERE id = ?", (int(cat_id),)
                ).fetchone()
                if cat_row:
                    category_name = cat_row["name"]
            except (ValueError, TypeError):
                pass

        # Get all categories for filter dropdown
        cat_rows = conn.execute(
            "SELECT id, name FROM categories ORDER BY name"
        ).fetchall()
        categories = [{"id": r["id"], "name": r["name"]} for r in cat_rows]

        # Get distinct accounts for filter dropdown
        acct_rows = conn.execute(
            "SELECT DISTINCT account FROM transactions "
            "WHERE account IS NOT NULL AND account != '' ORDER BY account"
        ).fetchall()
        accounts = [r["account"] for r in acct_rows]

        return txns, total_count, total_pages, page, category_name, categories, accounts
    finally:
        conn.close()


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    """Full page render."""
    # Auto-apply default saved view when no query params present
    if not request.query_string:
        from web.routes.saved_views import get_default_qs
        default_qs = get_default_qs(g.entity_key, "transactions")
        if default_qs and default_qs != request.query_string.decode():
            return redirect(f"/transactions/?{default_qs}")

    params = _get_filter_params()
    page = _parse_page()

    txns, total_count, total_pages, page, category_name, categories, accounts = (
        _query_transactions(g.entity_key, params, page)
    )

    return render_template(
        "transactions.html",
        txns=txns,
        total_count=total_count,
        total_pages=total_pages,
        page=page,
        params=params,
        category_name=category_name,
        categories=categories,
        accounts=accounts,
    )


@bp.route("/partial")
def partial():
    """HTMX partial — returns #txn-results div (table + pagination)."""
    params = _get_filter_params()
    page = _parse_page()

    txns, total_count, total_pages, page, category_name, categories, accounts = (
        _query_transactions(g.entity_key, params, page)
    )

    return render_template(
        "components/txn_results.html",
        txns=txns,
        total_count=total_count,
        total_pages=total_pages,
        page=page,
        params=params,
        category_name=category_name,
        categories=categories,
        accounts=accounts,
    )


# ── Inline actions (PR 3) ────────────────────────────────────────────────────

@bp.route("/view-row/<txn_id>")
def view_row(txn_id):
    """Return read-only <tr> partial (used by cancel button)."""
    conn = get_connection(g.entity_key)
    try:
        return _render_read_row(conn, txn_id)
    finally:
        conn.close()


@bp.route("/edit-row/<txn_id>")
def edit_row(txn_id):
    """Return editable <tr> partial for a single transaction."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?", (txn_id,)
        ).fetchone()
        if not row:
            return "Not found", 404
        txn = dict(row)
        categories = get_categories(g.entity_key)
        current_cat = txn.get("category") or ""
        subcats = get_subcategories(g.entity_key, current_cat) if current_cat else ["Unknown"]
        return render_template(
            "components/txn_row_edit.html",
            txn=txn,
            categories=categories,
            subcategories=subcats,
        )
    finally:
        conn.close()


@bp.route("/update/<txn_id>", methods=["POST"])
def update(txn_id):
    """Save category + subcategory + notes, return read-only <tr>."""
    category = request.form.get("category", "").strip()
    subcategory = request.form.get("subcategory", "").strip() or "Unknown"
    # Guard against literal __new__ value if user clicked Save without confirming
    if subcategory == "__new__":
        subcategory = "General"
    notes = request.form.get("notes", "").strip()

    conn = get_connection(g.entity_key)
    try:
        # Auto-create subcategory if it's new
        if category and subcategory and subcategory not in ("General", "Unknown"):
            conn.execute(
                "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) "
                "VALUES (?,?,?)",
                (category, subcategory, datetime.now(timezone.utc).isoformat()),
            )
        conn.execute(
            "UPDATE transactions SET category=?, subcategory=?, notes=?, confidence=1.0 "
            "WHERE transaction_id=?",
            (category, subcategory, notes, txn_id),
        )
        conn.commit()
        resp = make_response(_render_read_row(conn, txn_id))
        # Invalidate JS subcategory cache so new subcategories appear
        resp.headers["HX-Trigger"] = "subcatCacheInvalidate"
        return resp
    finally:
        conn.close()


@bp.route("/mark-transfer/<txn_id>", methods=["POST"])
def mark_transfer(txn_id):
    """Set category='Internal Transfer', return read-only <tr>."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "UPDATE transactions SET category='Internal Transfer', "
            "subcategory='Unknown', confidence=1.0 WHERE transaction_id=?",
            (txn_id,),
        )
        conn.commit()
        return _render_read_row(conn, txn_id)
    finally:
        conn.close()


@bp.route("/create-rule/<txn_id>", methods=["POST"])
def create_rule(txn_id):
    """Create merchant alias from this transaction's current category, return <tr>.

    Reads category/subcategory from form data (the current dropdown selections)
    so the rule matches what the user sees, not what was last saved.  Also saves
    the transaction with those values before creating the rule.
    """
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT description_raw, category, subcategory FROM transactions WHERE transaction_id=?",
            (txn_id,),
        ).fetchone()
        if not row:
            return "Not found", 404

        # Use form data (current dropdown selections) over saved DB values
        cat = request.form.get("category") or row["category"] or ""
        sub = request.form.get("subcategory") or row["subcategory"] or ""
        desc = row["description_raw"] or ""

        # Auto-create subcategory if it's new
        if cat and sub and sub not in ("General", "Unknown"):
            conn.execute(
                "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) "
                "VALUES (?,?,?)",
                (cat, sub, datetime.now(timezone.utc).isoformat()),
            )

        # Save the transaction with the current dropdown values first
        conn.execute(
            "UPDATE transactions SET category=?, subcategory=? WHERE transaction_id=?",
            (cat, sub, txn_id),
        )

        # Strip platform prefixes (same logic as categorize.py)
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
                    " default_category, default_subcategory, active, created_at) "
                    "VALUES (?, ?, ?, ?, ?, 1, ?)",
                    ("contains", pattern, pattern, cat, sub, now_ts),
                )

        conn.commit()

        # Return the read-only row
        resp = make_response(_render_read_row(conn, txn_id))
        resp.headers["HX-Trigger"] = "subcatCacheInvalidate"
        return resp
    finally:
        conn.close()


@bp.route("/suggest/<txn_id>", methods=["POST"])
def suggest(txn_id):
    """Return AI-suggested category + subcategory for a transaction."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT merchant_canonical, description_raw, amount_cents "
            "FROM transactions WHERE transaction_id=?",
            (txn_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "Transaction not found"}), 404

        # Build categories with subcategories for the current entity
        cats = get_categories(g.entity_key)
        categories_with_subs = {}
        for cat in cats:
            categories_with_subs[cat] = get_subcategories(g.entity_key, cat)

        from core.ai_client import generate_category_suggestion
        # Determine entity type for AI context
        entity_type = "business" if g.entity_key in ("company", "luxelegacy") else "personal"
        result = generate_category_suggestion(
            merchant=row["merchant_canonical"] or "",
            description=row["description_raw"] or "",
            amount_cents=row["amount_cents"] or 0,
            categories_with_subs=categories_with_subs,
            entity_type=entity_type,
        )
        if result:
            return jsonify(result)
        return jsonify({"error": "AI suggestions unavailable"}), 503
    finally:
        conn.close()


@bp.route("/subcategories")
def subcategories():
    """Return subcategory <option> tags for a category (HTMX endpoint)."""
    cat = request.args.get("category", "")
    subs = get_subcategories(g.entity_key, cat)
    options = "".join(
        f'<option value="{escape(s)}">{escape(s)}</option>' for s in subs
    )
    return options


@bp.route("/all-subcategories")
def all_subcategories():
    """Return all subcategories as JSON map {category: [sub1, sub2, ...]}."""
    cats = get_categories(g.entity_key)
    result = {}
    for cat in cats:
        result[cat] = get_subcategories(g.entity_key, cat)
    return jsonify(result)


def _render_read_row(conn, txn_id):
    """Fetch a transaction and return its read-only <tr> HTML."""
    row = conn.execute(
        """SELECT t.*,
                  COUNT(ao.id) AS alloc_count,
                  COALESCE(SUM(ABS(ao.order_total_cents)), 0) AS alloc_total_cents,
                  GROUP_CONCAT(ao.product_summary, ' || ') AS alloc_products
           FROM transactions t
           LEFT JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id
           WHERE t.transaction_id = ?
           GROUP BY t.transaction_id""",
        (txn_id,),
    ).fetchone()
    if not row:
        return "Not found", 404
    return render_template("components/txn_row.html", txn=dict(row))


# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_page():
    """Parse page number from request args."""
    try:
        return max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        return 1


def _build_query_string(params, overrides=None):
    """Build a query string from params dict with optional overrides.

    Used by templates for pagination links that preserve filter state.
    """
    merged = {**params, **(overrides or {})}
    parts = []
    for k, v in sorted(merged.items()):
        if v:  # Skip empty values
            parts.append(f"{k}={v}")
    return "&".join(parts)

"""Dashboard route — filterable KPIs, cash flow chart, top categories/merchants."""

import calendar
from datetime import datetime

from flask import Blueprint, render_template, request, g, url_for

from core.db import get_connection
from core.amazon import get_order_counts
from web.routes.reports import fmt_month_short, fmt_date, COLORS

bp = Blueprint("dashboard", __name__)


# ── Filter helpers ────────────────────────────────────────────────────────────

def _get_filter_params():
    """Extract dashboard filter params from querystring."""
    return {
        "start": request.args.get("start", ""),
        "end": request.args.get("end", ""),
        "account": request.args.get("account", ""),
        "uncategorized": request.args.get("uncategorized", ""),
        "vendor_breakdown": request.args.get("vendor_breakdown", ""),
        "possible_transfer": request.args.get("possible_transfer", ""),
        "include_transfers": request.args.get("include_transfers", ""),
    }


def _apply_date_defaults(params):
    """Fill current calendar month when both start/end are empty."""
    if not params["start"] and not params["end"]:
        now = datetime.now()
        params["start"] = f"{now.year:04d}-{now.month:02d}-01"
        last_day = calendar.monthrange(now.year, now.month)[1]
        params["end"] = f"{now.year:04d}-{now.month:02d}-{last_day:02d}"
    return params


def _make_drill_url(params):
    """Return a closure that builds /transactions URLs preserving filter state."""
    def drill_url(**overrides):
        qp = {}
        if params.get("start"):
            qp["start"] = params["start"]
        if params.get("end"):
            qp["end"] = params["end"]
        if params.get("account"):
            qp["account"] = params["account"]
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)
    return drill_url


# ── SQL helpers ───────────────────────────────────────────────────────────────

_TRANSFER_CATS = ("Internal Transfer", "Credit Card Payment")


def _date_account_clause(params, prefix=""):
    """Build WHERE fragments + bind values for date range and optional account."""
    p = prefix + "." if prefix else ""
    clauses = [f"{p}date >= ?", f"{p}date <= ?"]
    binds = [params["start"], params["end"]]
    if params.get("account"):
        clauses.append(f"{p}account = ?")
        binds.append(params["account"])
    return clauses, binds


def _exclude_transfers_clause(params, prefix=""):
    """Return (clause_str, []) excluding transfer categories unless include_transfers is on."""
    if params.get("include_transfers") == "1":
        return "", []
    p = prefix + "." if prefix else ""
    return f"AND COALESCE({p}category,'') NOT IN ('Internal Transfer','Credit Card Payment')", []


# ── Core query function ──────────────────────────────────────────────────────

def _query_dashboard(conn, params):
    """Run all dashboard queries against a single connection. Returns dict for template."""
    data = {}

    # ── Account list (unfiltered, for dropdown) ──────────────────────────────
    acct_rows = conn.execute(
        "SELECT DISTINCT account FROM transactions "
        "WHERE account IS NOT NULL AND account != '' ORDER BY account"
    ).fetchall()
    data["accounts"] = [r[0] for r in acct_rows]

    # ── Date/account base clause ─────────────────────────────────────────────
    da_clauses, da_binds = _date_account_clause(params)
    da_where = " AND ".join(da_clauses)
    xfer_clause, _ = _exclude_transfers_clause(params)

    # ── Total transaction count (for empty state) ────────────────────────────
    data["total_txn_count"] = conn.execute(
        f"SELECT COUNT(*) FROM transactions WHERE {da_where}",
        da_binds,
    ).fetchone()[0]

    # ── Spend cents (expenses, excluding transfers by default) ───────────────
    data["spend_cents"] = conn.execute(
        f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
        f"WHERE amount_cents < 0 AND {da_where} {xfer_clause}",
        da_binds,
    ).fetchone()[0]

    # ── Income cents ─────────────────────────────────────────────────────────
    data["income_cents"] = conn.execute(
        f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
        f"WHERE amount_cents > 0 AND {da_where} {xfer_clause}",
        da_binds,
    ).fetchone()[0]

    # ── Net cents ────────────────────────────────────────────────────────────
    data["net_cents"] = data["income_cents"] - data["spend_cents"]

    # ── Needs Review count ───────────────────────────────────────────────────
    data["review_count"] = conn.execute(
        f"SELECT COUNT(*) FROM transactions "
        f"WHERE (category IS NULL OR category = '' OR confidence < 0.6) "
        f"AND {da_where} {xfer_clause}",
        da_binds,
    ).fetchone()[0]

    # ── Latest transaction date ──────────────────────────────────────────────
    latest_raw = conn.execute(
        f"SELECT MAX(date) FROM transactions WHERE {da_where}",
        da_binds,
    ).fetchone()[0]
    if latest_raw:
        data["latest_date"] = fmt_date(latest_raw)
    else:
        data["latest_date"] = "\u2014"

    # ── Top Categories (8 rows, expenses, exclude transfers) ─────────────────
    da_t_clauses, da_t_binds = _date_account_clause(params, prefix="t")
    da_t_where = " AND ".join(da_t_clauses)
    xfer_t_clause, _ = _exclude_transfers_clause(params, prefix="t")

    top_cats_rows = conn.execute(
        f"SELECT c.id AS cat_id, t.category, "
        f"  COUNT(*) AS txn_count, "
        f"  COALESCE(SUM(ABS(t.amount_cents)), 0) AS total_cents "
        f"FROM transactions t "
        f"LEFT JOIN categories c ON c.name = t.category "
        f"WHERE t.amount_cents < 0 AND {da_t_where} "
        f"  AND t.category IS NOT NULL AND t.category != '' "
        f"  {xfer_t_clause} "
        f"GROUP BY t.category ORDER BY total_cents DESC LIMIT 8",
        da_t_binds,
    ).fetchall()

    top_cats = []
    max_cat_cents = top_cats_rows[0]["total_cents"] if top_cats_rows else 1
    for r in top_cats_rows:
        top_cats.append({
            "cat_id": r["cat_id"],
            "name": r["category"],
            "txn_count": r["txn_count"],
            "total_cents": r["total_cents"],
            "pct": int(r["total_cents"] / max_cat_cents * 100) if max_cat_cents else 0,
        })
    data["top_cats"] = top_cats

    # ── Top Merchants (8 rows) ───────────────────────────────────────────────
    top_merch_rows = conn.execute(
        f"SELECT t.merchant_canonical AS merchant, "
        f"  COUNT(*) AS txn_count, "
        f"  COALESCE(SUM(ABS(t.amount_cents)), 0) AS total_cents "
        f"FROM transactions t "
        f"WHERE t.amount_cents < 0 AND {da_t_where} "
        f"  AND t.merchant_canonical IS NOT NULL AND t.merchant_canonical != '' "
        f"  {xfer_t_clause} "
        f"GROUP BY t.merchant_canonical ORDER BY total_cents DESC LIMIT 8",
        da_t_binds,
    ).fetchall()

    top_merchants = []
    max_merch_cents = top_merch_rows[0]["total_cents"] if top_merch_rows else 1
    for r in top_merch_rows:
        top_merchants.append({
            "merchant": r["merchant"],
            "txn_count": r["txn_count"],
            "total_cents": r["total_cents"],
            "pct": int(r["total_cents"] / max_merch_cents * 100) if max_merch_cents else 0,
        })
    data["top_merchants"] = top_merchants

    # ── Possible transfer count ──────────────────────────────────────────────
    data["transfer_count"] = conn.execute(
        f"SELECT COUNT(*) FROM transactions "
        f"WHERE {da_where} "
        f"  AND (category IN ('Internal Transfer','Credit Card Payment') "
        f"       OR (COALESCE(category,'') = '' AND ("
        f"           LOWER(description_raw) LIKE '%transfer%' "
        f"           OR LOWER(description_raw) LIKE '%payment%' "
        f"           OR LOWER(description_raw) LIKE '%autopay%')))",
        da_binds,
    ).fetchone()[0]

    # ── Vendor breakdown count ───────────────────────────────────────────────
    vb_da_clauses, vb_da_binds = _date_account_clause(params, prefix="t")
    vb_da_where = " AND ".join(vb_da_clauses)

    data["vendor_breakdown_count"] = conn.execute(
        f"SELECT COUNT(*) FROM ("
        f"  SELECT t.transaction_id FROM transactions t "
        f"  LEFT JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id "
        f"  WHERE {vb_da_where} "
        f"    AND t.amount_cents < -2500 "
        f"    AND (LOWER(t.merchant_canonical) LIKE '%amazon%' "
        f"         OR LOWER(t.description_raw) LIKE '%amzn%' "
        f"         OR LOWER(t.description_raw) LIKE '%henry schein%') "
        f"  GROUP BY t.transaction_id "
        f"  HAVING COUNT(ao.id) = 0 "
        f"     OR COALESCE(SUM(ABS(ao.order_total_cents)),0) < ABS(t.amount_cents) * 95 / 100"
        f")",
        vb_da_binds,
    ).fetchone()[0]

    # ── Vendor orders (global, not date-filtered) ────────────────────────────
    data["total_orders"], data["unmatched_orders"] = get_order_counts(g.entity_key)

    # ── Cash flow chart ──────────────────────────────────────────────────────
    data["chart_bars"] = _build_cash_flow_bars(conn, params["end"])

    # ── Drill URL builder ────────────────────────────────────────────────────
    data["drill_url"] = _make_drill_url(params)
    data["colors"] = COLORS

    return data


# ── Cash flow chart builder ──────────────────────────────────────────────────

def _build_cash_flow_bars(conn, end_date_str):
    """Build 6 monthly expense bars ending at the month containing end_date_str."""
    try:
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        end_dt = datetime.now()

    # Build 6-month list (most recent last)
    months = []
    y, m = end_dt.year, end_dt.month
    for _ in range(6):
        months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months.reverse()  # oldest first

    # Query totals per month
    placeholders = ",".join("?" * len(months))
    rows = conn.execute(
        f"SELECT strftime('%Y-%m', date) AS ym, "
        f"  COALESCE(SUM(ABS(amount_cents)), 0) AS total_cents "
        f"FROM transactions "
        f"WHERE amount_cents < 0 "
        f"  AND strftime('%Y-%m', date) IN ({placeholders}) "
        f"  AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment') "
        f"GROUP BY ym",
        months,
    ).fetchall()

    totals = {r["ym"]: r["total_cents"] for r in rows}
    max_cents = max(totals.values()) if totals else 1

    current_ym = f"{end_dt.year:04d}-{end_dt.month:02d}"

    bars = []
    for ym in months:
        cents = totals.get(ym, 0)
        has_data = cents > 0
        bars.append({
            "label": fmt_month_short(ym),
            "display": _fmt_compact(cents) if has_data else "",
            "pct": int(cents / max_cents * 100) if max_cents and has_data else 0,
            "has_data": has_data,
            "is_current": ym == current_ym,
        })
    return bars


def _fmt_compact(cents):
    """Format cents as compact dollar string: 123456 -> '$1.2K', 1234567 -> '$12.3K'."""
    dollars = abs(cents) / 100
    if dollars >= 1000:
        return f"${dollars / 1000:.1f}K"
    return f"${dollars:,.0f}"


# ── Routes ────────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    params = _apply_date_defaults(_get_filter_params())
    conn = get_connection(g.entity_key)
    try:
        data = _query_dashboard(conn, params)
    finally:
        conn.close()
    return render_template("dashboard.html", **data, params=params)


@bp.route("/dashboard/partial")
def partial():
    params = _apply_date_defaults(_get_filter_params())
    conn = get_connection(g.entity_key)
    try:
        data = _query_dashboard(conn, params)
    finally:
        conn.close()
    return render_template("components/dashboard_body.html", **data, params=params)

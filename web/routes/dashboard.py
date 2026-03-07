"""Dashboard route — filterable KPIs, cash flow chart, top categories/merchants."""

import calendar
import statistics
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request, g, url_for, redirect

from core.db import get_connection
from core.amazon import get_order_counts
from web.routes.reports import fmt_month_short, fmt_date

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
        if params.get("include_transfers"):
            qp["include_transfers"] = params["include_transfers"]
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)
    return drill_url


# ── SQL helpers ───────────────────────────────────────────────────────────────

_TRANSFER_CATS = ("Internal Transfer", "Credit Card Payment", "Owner Contribution", "Partner Buyout")


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
    return f"AND COALESCE({p}category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')", []


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
        f"  AND (category IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
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

    # ── Plaid sync health ─────────────────────────────────────────────────────
    data["plaid_sync_items"] = _query_plaid_sync(conn)

    # ── Recurring / Upcoming ───────────────────────────────────────────────
    recurring_patterns = _detect_recurring(conn, params)
    data["upcoming_items"] = _build_upcoming(recurring_patterns)

    # ── Drill URL builder ────────────────────────────────────────────────────
    drill_url = _make_drill_url(params)
    data["drill_url"] = drill_url

    # ── Insights ─────────────────────────────────────────────────────────────
    data["insights"] = _compute_insights(conn, params, drill_url)

    # ── Income vs Expenses 12-month line chart ─────────────────────────────
    data["ie_points"] = _query_income_vs_expenses(conn)

    return data


# ── Insights engine ──────────────────────────────────────────────────────────

def _compute_insights(conn, params, drill_url):
    """Return up to 3 actionable insight dicts for the current dashboard range.

    Each insight: {"icon": str, "text": str, "url": str, "insight_key": str}.
    Returns [] when no insights qualify. Dismissed insights are filtered out.
    """
    insights = []

    try:
        start_dt = datetime.strptime(params["start"], "%Y-%m-%d")
        end_dt = datetime.strptime(params["end"], "%Y-%m-%d")
    except (ValueError, TypeError, KeyError):
        return insights

    # Load dismissed insight keys for this entity
    dismissed = set()
    try:
        rows = conn.execute("SELECT insight_key FROM insight_dismissals").fetchall()
        dismissed = {r[0] for r in rows}
    except Exception:
        pass  # Table may not exist yet

    # ── Insight A: Largest category spend increase vs prior period ────────
    span_days = (end_dt - start_dt).days
    if span_days > 0:
        prior_end = start_dt - timedelta(days=1)
        prior_start = prior_end - timedelta(days=span_days)
        prior_start_str = prior_start.strftime("%Y-%m-%d")
        prior_end_str = prior_end.strftime("%Y-%m-%d")

        xfer_clause, _ = _exclude_transfers_clause(params)
        acct_clause = ""
        acct_binds = []
        if params.get("account"):
            acct_clause = "AND account = ?"
            acct_binds = [params["account"]]

        # Current period category totals
        cur_rows = conn.execute(
            f"SELECT category, "
            f"  COUNT(*) AS txn_count, "
            f"  COALESCE(SUM(ABS(amount_cents)), 0) AS total_cents "
            f"FROM transactions "
            f"WHERE amount_cents < 0 "
            f"  AND date >= ? AND date <= ? "
            f"  AND category IS NOT NULL AND category != '' "
            f"  {xfer_clause} {acct_clause} "
            f"GROUP BY category",
            [params["start"], params["end"]] + acct_binds,
        ).fetchall()

        # Prior period category totals
        prior_rows = conn.execute(
            f"SELECT category, "
            f"  COALESCE(SUM(ABS(amount_cents)), 0) AS total_cents "
            f"FROM transactions "
            f"WHERE amount_cents < 0 "
            f"  AND date >= ? AND date <= ? "
            f"  AND category IS NOT NULL AND category != '' "
            f"  {xfer_clause} {acct_clause} "
            f"GROUP BY category",
            [prior_start_str, prior_end_str] + acct_binds,
        ).fetchall()

        prior_map = {r["category"]: r["total_cents"] for r in prior_rows}

        best_cat = None
        best_increase = 0
        for r in cur_rows:
            if r["txn_count"] < 2:
                continue
            increase = r["total_cents"] - prior_map.get(r["category"], 0)
            if increase > best_increase:
                best_increase = increase
                best_cat = r["category"]

        if best_cat and best_increase > 5000:  # > $50
            ikey = f"category_increase:{best_cat}:{params['start']}:{params['end']}"
            if ikey not in dismissed:
                cat_id_row = conn.execute(
                    "SELECT id FROM categories WHERE name = ?", (best_cat,)
                ).fetchone()
                cat_id = cat_id_row["id"] if cat_id_row else None
                dollars = best_increase // 100
                insights.append({
                    "icon": "\U0001F4C8",  # 📈
                    "text": f"{best_cat} up ${dollars:,} vs prior period",
                    "url": drill_url(category_id=cat_id) if cat_id else drill_url(),
                    "insight_type": "category_increase",
                    "insight_key": ikey,
                    "detail_params": {"category": best_cat,
                                      "start": params["start"], "end": params["end"],
                                      "account": params.get("account", "")},
                })

    # ── Insight B: New merchants this period ──────────────────────────────
    try:
        lookback_start = (start_dt - timedelta(days=90)).strftime("%Y-%m-%d")
        xfer_clause, _ = _exclude_transfers_clause(params)
        acct_clause = ""
        acct_binds = []
        if params.get("account"):
            acct_clause = "AND account = ?"
            acct_binds = [params["account"]]

        new_count = conn.execute(
            f"SELECT COUNT(DISTINCT merchant_canonical) FROM transactions "
            f"WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
            f"  AND date >= ? AND date <= ? "
            f"  {xfer_clause} {acct_clause} "
            f"  AND merchant_canonical NOT IN ("
            f"    SELECT DISTINCT merchant_canonical FROM transactions "
            f"    WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
            f"      AND date >= ? AND date < ? "
            f"      {xfer_clause} {acct_clause}"
            f"  )",
            [params["start"], params["end"]] + acct_binds +
            [lookback_start, params["start"]] + acct_binds,
        ).fetchone()[0]

        if new_count > 0:
            ikey = f"new_merchants:{params['start']}:{params['end']}"
            if ikey not in dismissed:
                insights.append({
                    "icon": "\U0001F195",  # 🆕
                    "text": f"{new_count} new merchant{'s' if new_count != 1 else ''} this period",
                    "url": drill_url(new_merchants=1),
                    "insight_type": "new_merchants",
                    "insight_key": ikey,
                    "detail_params": {"start": params["start"], "end": params["end"],
                                      "account": params.get("account", "")},
                })
    except Exception:
        pass  # Skip this insight on any error

    # ── Insight C: Large transactions (> $500) ────────────────────────────
    try:
        xfer_clause, _ = _exclude_transfers_clause(params)
        acct_clause = ""
        acct_binds = []
        if params.get("account"):
            acct_clause = "AND account = ?"
            acct_binds = [params["account"]]

        large_count = conn.execute(
            f"SELECT COUNT(*) FROM transactions "
            f"WHERE ABS(amount_cents) > 50000 "
            f"  AND date >= ? AND date <= ? "
            f"  {xfer_clause} {acct_clause}",
            [params["start"], params["end"]] + acct_binds,
        ).fetchone()[0]

        if large_count > 0:
            ikey = f"large_txns:{params['start']}:{params['end']}"
            if ikey not in dismissed:
                insights.append({
                    "icon": "\U0001F4B0",  # 💰
                    "text": f"{large_count} transaction{'s' if large_count != 1 else ''} over $500",
                    "url": drill_url(sort="amount"),
                    "insight_type": "large_txns",
                    "insight_key": ikey,
                    "detail_params": {"start": params["start"], "end": params["end"],
                                      "account": params.get("account", "")},
                })
    except Exception:
        pass  # Skip this insight on any error

    return insights[:3]


def _compute_compare_insights(conn, left_start, left_end, right_start, right_end,
                               drill_url_left, drill_url_right):
    """Return up to 3 cross-period comparison insights.

    Each insight: {"text": str, "url": str}.
    Compares left period vs right period.
    """
    insights = []
    xfer_exclude = "AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')"

    # ── Compare A: Total spending change ────────────────────────────────────
    try:
        left_spend = conn.execute(
            f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? {xfer_exclude}",
            [left_start, left_end],
        ).fetchone()[0]
        right_spend = conn.execute(
            f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? {xfer_exclude}",
            [right_start, right_end],
        ).fetchone()[0]

        if right_spend > 0:
            diff = left_spend - right_spend
            diff_dollars = abs(diff) // 100
            pct = abs(diff) * 100 // right_spend if right_spend else 0
            if diff_dollars >= 50:
                direction = "up" if diff > 0 else "down"
                insights.append({
                    "text": f"Spending {direction} ${diff_dollars:,} ({pct}%) vs prior period",
                    "url": drill_url_left(),
                })
    except Exception:
        pass

    # ── Compare B: Biggest category shift ───────────────────────────────────
    try:
        left_cats = conn.execute(
            f"SELECT category, COALESCE(SUM(ABS(amount_cents)), 0) AS total "
            f"FROM transactions WHERE amount_cents < 0 "
            f"AND date >= ? AND date <= ? {xfer_exclude} "
            f"AND category IS NOT NULL AND category != '' "
            f"GROUP BY category",
            [left_start, left_end],
        ).fetchall()
        right_cats = conn.execute(
            f"SELECT category, COALESCE(SUM(ABS(amount_cents)), 0) AS total "
            f"FROM transactions WHERE amount_cents < 0 "
            f"AND date >= ? AND date <= ? {xfer_exclude} "
            f"AND category IS NOT NULL AND category != '' "
            f"GROUP BY category",
            [right_start, right_end],
        ).fetchall()

        left_map = {r["category"]: r["total"] for r in left_cats}
        right_map = {r["category"]: r["total"] for r in right_cats}

        best_cat, best_shift = None, 0
        for cat in set(left_map) | set(right_map):
            shift = abs(left_map.get(cat, 0) - right_map.get(cat, 0))
            if shift > best_shift:
                best_shift = shift
                best_cat = cat

        if best_cat and best_shift > 5000:  # > $50
            shift_dollars = best_shift // 100
            cat_id_row = conn.execute(
                "SELECT id FROM categories WHERE name = ?", (best_cat,)
            ).fetchone()
            cat_id = cat_id_row["id"] if cat_id_row else None
            url = drill_url_left(category_id=cat_id) if cat_id else drill_url_left()
            insights.append({
                "text": f"{best_cat} shifted ${shift_dollars:,} between periods",
                "url": url,
            })
    except Exception:
        pass

    return insights[:3]


def _compute_income_insights(conn, left_start, left_end, right_start, right_end,
                              drill_url_left, drill_url_right):
    """Return up to 3 income-related insights for the IE chart section.

    Each insight: {"text": str, "url": str}.
    """
    insights = []
    xfer_exclude = ("AND COALESCE(category,'') NOT IN "
                    "('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')")

    # ── Income A: Income change between periods ───────────────────────────
    try:
        left_inc = conn.execute(
            f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
            f"WHERE amount_cents > 0 AND date >= ? AND date <= ? {xfer_exclude}",
            [left_start, left_end],
        ).fetchone()[0]
        right_inc = conn.execute(
            f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
            f"WHERE amount_cents > 0 AND date >= ? AND date <= ? {xfer_exclude}",
            [right_start, right_end],
        ).fetchone()[0]

        if right_inc > 0:
            diff = left_inc - right_inc
            diff_dollars = abs(diff) // 100
            pct = abs(diff) * 100 // right_inc if right_inc else 0
            if diff_dollars >= 100:
                direction = "up" if diff > 0 else "down"
                insights.append({
                    "text": f"Income {direction} ${diff_dollars:,} ({pct}%) vs prior period",
                    "url": drill_url_left(type="income"),
                })
    except Exception:
        pass

    # ── Income B: Top income source this period ───────────────────────────
    try:
        top_row = conn.execute(
            f"SELECT subcategory, COALESCE(SUM(amount_cents), 0) AS total "
            f"FROM transactions "
            f"WHERE amount_cents > 0 AND date >= ? AND date <= ? "
            f"  AND category = 'Income' AND subcategory IS NOT NULL AND subcategory != '' "
            f"  AND subcategory != 'General' "
            f"  {xfer_exclude} "
            f"GROUP BY subcategory ORDER BY total DESC LIMIT 1",
            [left_start, left_end],
        ).fetchone()

        if top_row and top_row["total"] > 0:
            dollars = top_row["total"] // 100
            insights.append({
                "text": f"Top income source: {top_row['subcategory']} (${dollars:,})",
                "url": drill_url_left(type="income"),
            })
    except Exception:
        pass

    # ── Income C: Expense-to-income ratio ─────────────────────────────────
    try:
        left_inc = conn.execute(
            f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
            f"WHERE amount_cents > 0 AND date >= ? AND date <= ? {xfer_exclude}",
            [left_start, left_end],
        ).fetchone()[0]
        left_exp = conn.execute(
            f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? {xfer_exclude}",
            [left_start, left_end],
        ).fetchone()[0]

        if left_inc > 0:
            ratio = left_exp * 100 // left_inc
            if 90 < ratio <= 200:
                insights.append({
                    "text": f"Spending at {ratio}% of income this period",
                    "url": drill_url_left(),
                })
    except Exception:
        pass

    return insights[:3]


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
        f"  AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
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


# ── Plaid sync helpers ────────────────────────────────────────────────────────

def _fmt_relative_time(iso_str):
    """Format an ISO 8601 UTC timestamp as a human-readable relative time string.

    Returns (text, is_stale) where is_stale is True when the sync is old or missing.
    """
    if not iso_str:
        return "Never synced", True
    try:
        # Handle both offset-aware and naive ISO strings
        ts = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - ts
        seconds = int(delta.total_seconds())
        if seconds < 0:
            return "Just now", False
        if seconds < 3600:
            minutes = max(1, seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago", False
        if seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago", False
        days = seconds // 86400
        if days < 7:
            return f"{days} day{'s' if days != 1 else ''} ago", days >= 3
        return "Over a week ago", True
    except (ValueError, TypeError):
        return "Never synced", True


def _query_plaid_sync(conn):
    """Return list of Plaid items with sync status for the current entity."""
    try:
        rows = conn.execute(
            "SELECT institution_name, last_synced FROM plaid_items "
            "ORDER BY institution_name"
        ).fetchall()
    except Exception:
        # Table may not exist in older DBs
        return []
    items = []
    for r in rows:
        text, stale = _fmt_relative_time(r["last_synced"])
        items.append({
            "institution": r["institution_name"] or "Unknown",
            "last_synced_text": text,
            "is_stale": stale,
        })
    return items


# ── Recurring detection ───────────────────────────────────────────────────────
#
# Heuristic summary:
#   1. Query last 90 days of transactions (respects account + transfer filters).
#   2. Group by merchant_canonical; require ≥2 occurrences.
#   3. Compute consecutive date intervals → median → classify cadence:
#        Weekly 5–9d, Monthly 25–35d, Annual 340–390d.
#   4. Amount regularity: ≥2 of last 3 amounts within max($3, 5% of median).
#   5. Staleness: skip if last charge was >2× median interval ago.
#   6. Next expected = last_date + median_interval.
#   7. _build_upcoming filters to next 30 days, caps to 6 items, adds ±7 day
#      drill window for each item.

# Cadence definitions: (label, min_days, max_days)
_CADENCES = [
    ("Weekly", 5, 9),
    ("Monthly", 25, 35),
    ("Annual", 340, 390),
]


def _classify_cadence(median_interval_days):
    """Classify a median interval into a named cadence, or None if irregular."""
    for label, lo, hi in _CADENCES:
        if lo <= median_interval_days <= hi:
            return label
    return None


def _amount_is_regular(amounts_cents, n_recent=3):
    """Check if recent amounts are consistent with the median.

    Small-N-safe rule: require at least 2 of the last `n_recent` occurrences
    to be within max($3.00, 5% of median) of the median amount.
    """
    if len(amounts_cents) < 2:
        return False
    abs_amounts = [abs(a) for a in amounts_cents]
    med = statistics.median(abs_amounts)
    tolerance = max(300, int(med * 0.05))  # max($3.00, 5%)
    recent = abs_amounts[-n_recent:]
    within = sum(1 for a in recent if abs(a - med) <= tolerance)
    return within >= 2


def _detect_recurring(conn, params):
    """Detect recurring transaction patterns from the last 90 days.

    Returns list of dicts: merchant_canonical, cadence, median_amount_cents,
    last_date, next_expected_date, is_income.
    Respects account filter and transfer exclusion from params.
    """
    xfer_clause, _ = _exclude_transfers_clause(params)
    acct_clause = ""
    acct_binds = []
    if params.get("account"):
        acct_clause = "AND account = ?"
        acct_binds = [params["account"]]

    # Look back 90 days from today
    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%Y-%m-%d")

    patterns = []

    # ── Expense pass (amount_cents < 0) ──────────────────────────────────
    expense_rows = conn.execute(
        f"SELECT merchant_canonical, date, amount_cents "
        f"FROM transactions "
        f"WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        f"  AND amount_cents < 0 "
        f"  AND date >= ? AND date <= ? "
        f"  {xfer_clause} {acct_clause} "
        f"ORDER BY merchant_canonical, date",
        [cutoff, today_str] + acct_binds,
    ).fetchall()
    _process_merchant_groups(expense_rows, patterns, is_income=False)

    # ── Income pass (amount_cents > 0) ───────────────────────────────────
    income_rows = conn.execute(
        f"SELECT merchant_canonical, date, amount_cents "
        f"FROM transactions "
        f"WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        f"  AND amount_cents > 0 "
        f"  AND date >= ? AND date <= ? "
        f"  {xfer_clause} {acct_clause} "
        f"ORDER BY merchant_canonical, date",
        [cutoff, today_str] + acct_binds,
    ).fetchall()
    _process_merchant_groups(income_rows, patterns, is_income=True)

    return patterns


def _process_merchant_groups(rows, patterns, is_income):
    """Group rows by merchant_canonical and detect recurring patterns."""
    # Group by merchant
    groups = {}
    for r in rows:
        merchant = r["merchant_canonical"]
        if merchant not in groups:
            groups[merchant] = []
        groups[merchant].append({
            "date": r["date"],
            "amount_cents": r["amount_cents"],
        })

    today = datetime.now().date()

    for merchant, txns in groups.items():
        if len(txns) < 2:
            continue

        # Parse dates and compute intervals
        dates = []
        amounts = []
        for t in txns:
            try:
                dates.append(datetime.strptime(t["date"], "%Y-%m-%d").date())
            except (ValueError, TypeError):
                continue
            amounts.append(t["amount_cents"])

        if len(dates) < 2:
            continue

        # Consecutive intervals in days
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        intervals = [iv for iv in intervals if iv > 0]  # skip same-day duplicates

        if not intervals:
            continue

        median_interval = statistics.median(intervals)
        cadence = _classify_cadence(median_interval)
        if cadence is None:
            continue

        # Amount regularity check
        if not _amount_is_regular(amounts):
            continue

        # Staleness check: skip if last charge was >2× cadence ago
        last_date = dates[-1]
        days_since_last = (today - last_date).days
        if days_since_last > 2 * median_interval:
            continue

        # Compute next expected date and median amount
        next_date = last_date + timedelta(days=int(median_interval))
        median_amount = int(statistics.median([abs(a) for a in amounts]))

        patterns.append({
            "merchant_canonical": merchant,
            "cadence": cadence,
            "median_amount_cents": median_amount if not is_income else median_amount,
            "last_date": last_date.isoformat(),
            "next_expected_date": next_date.isoformat(),
            "is_income": is_income,
        })


def _build_upcoming(patterns, horizon_days=5):
    """Filter recurring patterns to those expected within the next horizon_days.

    Returns sorted list of up to 6 upcoming items for the template.
    Each item includes drill_start/drill_end (expected ±7 days) for date-windowed links.
    """
    today = datetime.now().date()
    cutoff = today + timedelta(days=horizon_days)
    items = []

    for p in patterns:
        try:
            next_date = datetime.strptime(p["next_expected_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        # Include if next expected date is between today and cutoff
        if next_date < today or next_date > cutoff:
            continue

        # Skip small charges (< $100)
        if abs(p.get("median_amount_cents", 0)) < 10000:
            continue

        # Format display date (e.g., "Mar 5")
        display_date = next_date.strftime("%b %-d")

        # ±7 day window around expected date for drill links
        drill_start = (next_date - timedelta(days=7)).isoformat()
        drill_end = (next_date + timedelta(days=7)).isoformat()

        items.append({
            "merchant_canonical": p["merchant_canonical"],
            "cadence": p["cadence"],
            "expected_amount_cents": p["median_amount_cents"],
            "expected_date": p["next_expected_date"],
            "expected_date_display": display_date,
            "is_income": p["is_income"],
            "drill_start": drill_start,
            "drill_end": drill_end,
        })

    # Sort by expected date, limit to 6
    items.sort(key=lambda x: x["expected_date"])
    return items[:6]


def _format_period_label(params):
    """Human-readable label for the current date range (KPI band badge)."""
    try:
        s = datetime.strptime(params["start"], "%Y-%m-%d")
        e = datetime.strptime(params["end"], "%Y-%m-%d")
    except (ValueError, KeyError):
        return ""
    now = datetime.now()
    if s.year == e.year and s.month == e.month:
        suffix = "" if s.year == now.year else f", {s.year}"
        return f"{s.strftime('%b')} {s.day}\u2009\u2013\u2009{e.day}{suffix}"
    else:
        return f"{s.strftime('%b')} {s.day}\u2009\u2013\u2009{e.strftime('%b')} {e.day}"


# ── Period helpers (KPI compare panels) ───────────────────────────────────────

# Static presets (always shown first in dropdown)
_PRESET_LABELS = {
    "this_month": "This Month",
    "last_month": "Last Month",
    "last_30": "Last 30 Days",
    "last_90": "Last 90 Days",
    "year_to_date": "Year to Date",
    "last_12_months": "Last 12 Months",
}


def _build_period_labels():
    """Build ordered period labels: presets + last 12 explicit months.

    Explicit months use keys like 'month_2026_03' → 'Mar 2026'.
    """
    labels = dict(_PRESET_LABELS)
    now = datetime.now()
    y, m = now.year, now.month
    for _ in range(12):
        key = f"month_{y:04d}_{m:02d}"
        # "Mar 2026" style label
        month_name = calendar.month_abbr[m]
        label = f"{month_name} {y}"
        labels[key] = label
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return labels


def _period_to_dates(period_key):
    """Map a period key to (start_date, end_date) strings in YYYY-MM-DD format.

    Supports preset keys and explicit month keys (month_YYYY_MM).
    """
    now = datetime.now()
    today = now.date()

    # Handle explicit month keys: month_2026_03 etc.
    if period_key.startswith("month_"):
        parts = period_key.split("_")
        if len(parts) == 3:
            try:
                y, m = int(parts[1]), int(parts[2])
                start = f"{y:04d}-{m:02d}-01"
                last_day = calendar.monthrange(y, m)[1]
                end = f"{y:04d}-{m:02d}-{last_day:02d}"
                return start, end
            except (ValueError, OverflowError):
                pass
        return _period_to_dates("this_month")

    if period_key == "this_month":
        start = f"{now.year:04d}-{now.month:02d}-01"
        last_day = calendar.monthrange(now.year, now.month)[1]
        end = f"{now.year:04d}-{now.month:02d}-{last_day:02d}"
    elif period_key == "last_month":
        if now.month == 1:
            y, m = now.year - 1, 12
        else:
            y, m = now.year, now.month - 1
        start = f"{y:04d}-{m:02d}-01"
        last_day = calendar.monthrange(y, m)[1]
        end = f"{y:04d}-{m:02d}-{last_day:02d}"
    elif period_key == "last_30":
        start = (today - timedelta(days=29)).isoformat()
        end = today.isoformat()
    elif period_key == "last_90":
        start = (today - timedelta(days=89)).isoformat()
        end = today.isoformat()
    elif period_key == "year_to_date":
        start = f"{now.year:04d}-01-01"
        end = today.isoformat()
    elif period_key == "last_12_months":
        start = (today - timedelta(days=365)).isoformat()
        end = today.isoformat()
    else:
        return _period_to_dates("this_month")
    return start, end


def _query_kpi(conn, start, end):
    """Run KPI queries for a date range. Returns dict with spend/income/net + txn count."""
    da_where = "date >= ? AND date <= ?"
    binds = [start, end]
    xfer_exclude = "AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')"

    spend_cents = conn.execute(
        f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
        f"WHERE amount_cents < 0 AND {da_where} {xfer_exclude}",
        binds,
    ).fetchone()[0]

    income_cents = conn.execute(
        f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
        f"WHERE amount_cents > 0 AND {da_where} {xfer_exclude}",
        binds,
    ).fetchone()[0]

    txn_count = conn.execute(
        f"SELECT COUNT(*) FROM transactions WHERE {da_where}",
        binds,
    ).fetchone()[0]

    return {
        "spend_cents": spend_cents,
        "income_cents": income_cents,
        "net_cents": income_cents - spend_cents,
        "txn_count": txn_count,
    }


def _nice_y_ticks(max_cents):
    """Compute Apple-ish nice-number Y-axis ticks for a bar chart.

    Returns (ticks, axis_max_cents) where ticks is a list of dicts
    [{"label": "$500", "pct": 50.0}, ...] from top to bottom,
    and axis_max_cents is the tick ceiling (>= max_cents).

    Uses step from {1, 2, 5} × 10^n to get ~4–5 ticks.
    If max_cents == 0: returns single $0 baseline and axis_max of 0.
    """
    import math

    if max_cents <= 0:
        return [{"label": "$0", "pct": 0}], 0

    # Work in dollars for readability
    max_dollars = max_cents / 100

    # Find nice step: target ~4-5 ticks, minimum step $1
    rough_step = max(max_dollars / 4, 1)
    magnitude = 10 ** math.floor(math.log10(rough_step)) if rough_step > 0 else 1
    residual = rough_step / magnitude
    # Pick from {1, 2, 5}
    if residual <= 1.5:
        nice_step = 1 * magnitude
    elif residual <= 3.5:
        nice_step = 2 * magnitude
    else:
        nice_step = 5 * magnitude
    nice_step = max(nice_step, 1)  # never sub-dollar ticks

    # Round up max to next nice_step multiple
    axis_max_dollars = math.ceil(max_dollars / nice_step) * nice_step
    axis_max_cents = int(axis_max_dollars * 100)

    # Build ticks from top to bottom (axis_max down to 0)
    ticks = []
    val = axis_max_dollars
    while val >= 0:
        pct = (val / axis_max_dollars * 100) if axis_max_dollars > 0 else 0
        if val >= 1000:
            label = f"${val / 1000:.1f}K".replace(".0K", "K")
        elif val >= 1:
            label = f"${val:,.0f}"
        else:
            label = "$0"
        ticks.append({"label": label, "pct": pct})
        val = round(val - nice_step, 2)
        if val < 0 and abs(val) < nice_step * 0.01:
            val = 0  # float precision guard

    # Ensure $0 baseline is present
    if ticks[-1]["pct"] != 0:
        ticks.append({"label": "$0", "pct": 0})

    return ticks, axis_max_cents


def _query_income_vs_expenses(conn):
    """Return 12 months of income + expense totals (current month back 11).

    Each point: {ym, label, income_cents, expense_cents}.
    Excludes Internal Transfer and Credit Card Payment.
    Returns oldest→newest.
    """
    now = datetime.now()
    points = []
    y, m = now.year, now.month
    # Walk back 11 months to build list oldest→newest
    months = []
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months.reverse()  # oldest first

    for yr, mo in months:
        start = f"{yr:04d}-{mo:02d}-01"
        last_day = calendar.monthrange(yr, mo)[1]
        end = f"{yr:04d}-{mo:02d}-{last_day:02d}"

        row = conn.execute(
            "SELECT "
            "  COALESCE(SUM(CASE WHEN amount_cents < 0 THEN ABS(amount_cents) ELSE 0 END), 0) AS exp, "
            "  COALESCE(SUM(CASE WHEN amount_cents > 0 THEN amount_cents ELSE 0 END), 0) AS inc "
            "FROM transactions "
            "WHERE date >= ? AND date <= ? "
            "  AND COALESCE(category, '') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')",
            [start, end],
        ).fetchone()

        label = calendar.month_abbr[mo]
        points.append({
            "ym": f"{yr:04d}-{mo:02d}",
            "label": label,
            "income_cents": row["inc"],
            "expense_cents": row["exp"],
        })

    return points


def _query_category_totals(conn, start, end):
    """Query per-category expense totals for a date range.

    Expenses only (amount_cents < 0).  Excludes *exactly* 'Internal Transfer'
    and 'Credit Card Payment' categories.  Credit card interest and all other
    categories remain included.
    """
    return conn.execute(
        "SELECT c.id AS cat_id, t.category, "
        "  COALESCE(SUM(ABS(t.amount_cents)), 0) AS total_cents "
        "FROM transactions t "
        "LEFT JOIN categories c ON c.name = t.category "
        "WHERE t.amount_cents < 0 "
        "  AND t.date >= ? AND t.date <= ? "
        "  AND t.category IS NOT NULL AND t.category != '' "
        "  AND t.category NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout') "
        "GROUP BY t.category ORDER BY total_cents DESC",
        [start, end],
    ).fetchall()


def _query_subcategory_rollups(conn, start, end, category_names):
    """Return all subcategories per category for a date range.

    Every defined subcategory is included (even at $0).  Transactions with
    no subcategory (NULL / empty / 'Unknown') are rolled into a 'General'
    bucket.

    Returns dict: category_name -> [{name, cents}]
    Only includes categories in *category_names* (the displayed set).
    """
    if not category_names:
        return {}

    from collections import defaultdict

    placeholders = ", ".join("?" for _ in category_names)

    # 1. All defined subcategories for the displayed categories
    defined = conn.execute(
        "SELECT category_name, name FROM subcategories "
        "WHERE category_name IN (" + placeholders + ") "
        "ORDER BY category_name, name",
        list(category_names),
    ).fetchall()

    # Build skeleton: every category gets "General" + its defined subs
    skeleton = defaultdict(dict)  # cat -> {sub_name: 0}
    for cat in category_names:
        skeleton[cat]["General"] = 0
    for r in defined:
        skeleton[r["category_name"]][r["name"]] = 0

    # 2. Actual spend per (category, subcategory) in the period
    spend_rows = conn.execute(
        "SELECT t.category, t.subcategory, "
        "  COALESCE(SUM(ABS(t.amount_cents)), 0) AS sub_cents "
        "FROM transactions t "
        "WHERE t.amount_cents < 0 "
        "  AND t.date >= ? AND t.date <= ? "
        "  AND t.category IN (" + placeholders + ") "
        "GROUP BY t.category, t.subcategory",
        [start, end] + list(category_names),
    ).fetchall()

    for r in spend_rows:
        cat = r["category"]
        sub = r["subcategory"]
        cents = r["sub_cents"]
        if not sub or sub == "Unknown":
            skeleton[cat]["General"] += cents
        else:
            skeleton[cat][sub] = skeleton[cat].get(sub, 0) + cents

    # 3. Build result sorted by spend descending
    result = {}
    for cat in category_names:
        subs = skeleton[cat]
        items = [{"name": name, "cents": cents}
                 for name, cents in sorted(subs.items(), key=lambda x: -x[1])]
        result[cat] = items
    return result


# ── Routes ────────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    params = _apply_date_defaults(_get_filter_params())
    conn = get_connection(g.entity_key)
    try:
        data = _query_dashboard(conn, params)
    finally:
        conn.close()
    return render_template("dashboard.html", **data, params=params,
                           period_label=_format_period_label(params))


@bp.route("/dashboard/partial")
def partial():
    params = _apply_date_defaults(_get_filter_params())
    conn = get_connection(g.entity_key)
    try:
        data = _query_dashboard(conn, params)
    finally:
        conn.close()
    return render_template("components/dashboard_body.html", **data, params=params,
                           period_label=_format_period_label(params))


@bp.route("/dashboard/kpi-panel")
def kpi_panel():
    """Render a single KPI panel partial (HTMX endpoint)."""
    panel = request.args.get("panel", "left")
    period = request.args.get("period", "this_month" if panel == "left" else "last_month")

    start, end = _period_to_dates(period)
    conn = get_connection(g.entity_key)
    try:
        kpi = _query_kpi(conn, start, end)
    finally:
        conn.close()

    # Build drill URL helper for this panel's date range
    def drill_url(**overrides):
        qp = {"start": start, "end": end}
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    period_labels = _build_period_labels()

    return render_template("components/kpi_panel.html",
                           panel=panel, period=period, start=start, end=end,
                           period_labels=period_labels,
                           drill_url=drill_url,
                           **kpi)


@bp.route("/dashboard/categories-compare")
def categories_compare():
    """Render the categories comparison section (HTMX endpoint).

    Reads left_period and right_period from querystring, queries per-category
    expense totals for each, merges into combined list keyed by category name,
    sorts by combined total desc, takes top 12, and computes bar height
    percentages on a common scale.
    """
    left_period = request.args.get("left_period", "this_month")
    right_period = request.args.get("right_period", "last_month")

    left_start, left_end = _period_to_dates(left_period)
    right_start, right_end = _period_to_dates(right_period)

    conn = get_connection(g.entity_key)
    try:
        left_rows = _query_category_totals(conn, left_start, left_end)
        right_rows = _query_category_totals(conn, right_start, right_end)

        # Build lookup dicts: category_name -> {cat_id, total_cents}
        left_map = {}
        for r in left_rows:
            left_map[r["category"]] = {"cat_id": r["cat_id"], "total_cents": r["total_cents"]}

        right_map = {}
        for r in right_rows:
            right_map[r["category"]] = {"cat_id": r["cat_id"], "total_cents": r["total_cents"]}

        # Merge into combined list keyed by category name
        all_cats = set(left_map.keys()) | set(right_map.keys())
        merged = []
        for cat_name in all_cats:
            left_data = left_map.get(cat_name, {"cat_id": None, "total_cents": 0})
            right_data = right_map.get(cat_name, {"cat_id": None, "total_cents": 0})
            cat_id = left_data["cat_id"] or right_data["cat_id"]
            left_cents = left_data["total_cents"]
            right_cents = right_data["total_cents"]
            merged.append({
                "name": cat_name,
                "cat_id": cat_id,
                "left_cents": left_cents,
                "right_cents": right_cents,
                "combined": left_cents + right_cents,
            })

        # Sort by combined total desc, take top 28
        merged.sort(key=lambda x: x["combined"], reverse=True)
        top = merged[:28]

        # Query subcategory rollups for displayed categories only
        displayed_names = [c["name"] for c in top]
        subcats_left = _query_subcategory_rollups(conn, left_start, left_end, displayed_names)
        subcats_right = _query_subcategory_rollups(conn, right_start, right_end, displayed_names)
    finally:
        conn.close()

    # Compute bar percentages — use outlier-aware scale so one giant
    # category doesn't squash all the others into invisible slivers.
    all_vals = sorted(
        [c["left_cents"] for c in top] + [c["right_cents"] for c in top],
        reverse=True,
    )
    raw_max = all_vals[0] if all_vals else 0
    second = next((v for v in all_vals if v < raw_max), raw_max)
    # If top value is >3× the runner-up, scale to the runner-up instead
    scale_max = second if (second and raw_max > second * 3) else raw_max
    max_cents = raw_max  # keep true max for subcategory scaling
    for c in top:
        c["left_pct"] = min(100, int(c["left_cents"] / scale_max * 100)) if scale_max else 0
        c["right_pct"] = min(100, int(c["right_cents"] / scale_max * 100)) if scale_max else 0
        c["combined_cents"] = c["combined"]

    # Merge subcategories from both periods into a single dict
    subcats_merged = {}
    for cat_name in displayed_names:
        l_map = {s["name"]: s["cents"] for s in subcats_left.get(cat_name, [])}
        r_map = {s["name"]: s["cents"] for s in subcats_right.get(cat_name, [])}
        all_names = list(dict.fromkeys(list(l_map.keys()) + list(r_map.keys())))
        m = []
        for sname in all_names:
            lc = l_map.get(sname, 0)
            rc = r_map.get(sname, 0)
            m.append({"name": sname, "left_cents": lc, "right_cents": rc,
                       "combined": lc + rc})
        m.sort(key=lambda x: x["combined"], reverse=True)
        subcats_merged[cat_name] = m

    # Drill URL helpers
    def left_drill(**overrides):
        qp = {"start": left_start, "end": left_end}
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    def right_drill(**overrides):
        qp = {"start": right_start, "end": right_end}
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    period_labels = _build_period_labels()

    return render_template("components/categories_compare.html",
                           categories=top,
                           max_cents=max_cents,
                           left_period=left_period,
                           right_period=right_period,
                           left_label=period_labels.get(left_period, left_period),
                           right_label=period_labels.get(right_period, right_period),
                           left_drill=left_drill,
                           right_drill=right_drill,
                           left_start=left_start, left_end=left_end,
                           right_start=right_start, right_end=right_end,
                           subcats_merged=subcats_merged)


@bp.route("/dashboard/detail-categories")
def detail_categories():
    """Render single-period category chart for Details view (HTMX endpoint)."""
    period = request.args.get("period", "this_month")
    start, end = _period_to_dates(period)

    conn = get_connection(g.entity_key)
    try:
        rows = _query_category_totals(conn, start, end)

        cats = []
        for r in rows:
            cats.append({
                "name": r["category"],
                "cat_id": r["cat_id"],
                "total_cents": r["total_cents"],
            })

        # Sort by total desc, take top 28
        cats.sort(key=lambda x: x["total_cents"], reverse=True)
        top = cats[:28]

        # Subcategory rollups for tooltip
        displayed_names = [c["name"] for c in top]
        subcats = _query_subcategory_rollups(conn, start, end, displayed_names)
    finally:
        conn.close()

    # Compute bar percentages — outlier-aware scale
    raw_max = top[0]["total_cents"] if top else 0
    second = top[1]["total_cents"] if len(top) > 1 else raw_max
    scale_max = second if (second and raw_max > second * 3) else raw_max
    for c in top:
        c["pct"] = min(100, int(c["total_cents"] / scale_max * 100)) if scale_max else 0

    # Drill URL helper
    def drill(**overrides):
        qp = {"start": start, "end": end}
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    period_labels = _build_period_labels()

    return render_template("components/dashboard_detail_cats.html",
                           categories=top,
                           period=period,
                           period_label=period_labels.get(period, period),
                           start=start, end=end,
                           drill=drill,
                           subcats=subcats)


@bp.route("/dashboard/detail-insights")
def detail_insights():
    """Render single-period insights + upcoming for Details view (HTMX endpoint)."""
    period = request.args.get("period", "this_month")
    account = request.args.get("account", "")

    start, end = _period_to_dates(period)
    params = {"start": start, "end": end, "account": account}

    def drill(**overrides):
        qp = {"start": start, "end": end}
        if account:
            qp["account"] = account
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    conn = get_connection(g.entity_key)
    try:
        insights = _compute_insights(conn, params, drill)
        recurring = _detect_recurring(conn, params)
        upcoming_raw = _build_upcoming(recurring)
    finally:
        conn.close()

    # Add drill URLs to upcoming items
    upcoming = []
    for item in upcoming_raw:
        item["url"] = url_for("transactions.index",
                              merchant=item["merchant_canonical"],
                              start=item["drill_start"],
                              end=item["drill_end"])
        upcoming.append(item)

    period_labels = _build_period_labels()

    return render_template("components/dashboard_detail_insights.html",
                           insights=insights,
                           upcoming=upcoming,
                           period=period,
                           period_label=period_labels.get(period, period),
                           start=start, end=end)


@bp.route("/dashboard/insights-upcoming")
def insights_upcoming():
    """Render the Insights + Upcoming section (HTMX endpoint).

    Reads left_period and right_period from querystring, computes
    per-period insights, cross-period compare insights, and upcoming
    recurring items.
    """
    left_period = request.args.get("left_period", "this_month")
    right_period = request.args.get("right_period", "last_month")
    account = request.args.get("account", "")

    left_start, left_end = _period_to_dates(left_period)
    right_start, right_end = _period_to_dates(right_period)

    period_labels = _build_period_labels()
    left_label = period_labels.get(left_period, left_period)
    right_label = period_labels.get(right_period, right_period)

    # Build params dicts for insight queries
    left_params = {"start": left_start, "end": left_end, "account": account}
    right_params = {"start": right_start, "end": right_end, "account": account}

    # Drill URL builders
    def left_drill(**overrides):
        qp = {"start": left_start, "end": left_end}
        if account:
            qp["account"] = account
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    def right_drill(**overrides):
        qp = {"start": right_start, "end": right_end}
        if account:
            qp["account"] = account
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    conn = get_connection(g.entity_key)
    try:
        # Per-period insights
        left_insights = _compute_insights(conn, left_params, left_drill)
        right_insights = _compute_insights(conn, right_params, right_drill)

        # Cross-period compare insights
        compare_insights = _compute_compare_insights(
            conn, left_start, left_end, right_start, right_end,
            left_drill, right_drill,
        )

        # Upcoming recurring
        upcoming_params = {"start": left_start, "end": left_end, "account": account}
        recurring = _detect_recurring(conn, upcoming_params)
        upcoming_raw = _build_upcoming(recurring)
    finally:
        conn.close()

    # Add drill URLs to upcoming items
    upcoming = []
    for item in upcoming_raw:
        item["url"] = url_for("transactions.index",
                              merchant=item["merchant_canonical"],
                              start=item["drill_start"],
                              end=item["drill_end"])
        upcoming.append(item)

    return render_template("components/insights_upcoming.html",
                           left_insights=left_insights,
                           right_insights=right_insights,
                           compare_insights=compare_insights,
                           left_label=left_label,
                           right_label=right_label,
                           left_period=left_period,
                           right_period=right_period,
                           upcoming=upcoming)


@bp.route("/dashboard/ie-insights")
def ie_insights():
    """Render income-related insights below the IE chart (HTMX endpoint)."""
    left_period = request.args.get("left_period", "")
    right_period = request.args.get("right_period", "")
    period = request.args.get("period", "")
    account = request.args.get("account", "")

    # Detail mode uses single period; compare mode uses left/right
    if period and not left_period:
        left_period = period
        right_period = period
    if not left_period:
        left_period = "this_month"
    if not right_period:
        right_period = "last_month"

    left_start, left_end = _period_to_dates(left_period)
    right_start, right_end = _period_to_dates(right_period)

    def left_drill(**overrides):
        qp = {"start": left_start, "end": left_end}
        if account:
            qp["account"] = account
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    def right_drill(**overrides):
        qp = {"start": right_start, "end": right_end}
        if account:
            qp["account"] = account
        qp.update({k: v for k, v in overrides.items() if v})
        return url_for("transactions.index", **qp)

    conn = get_connection(g.entity_key)
    try:
        insights = _compute_income_insights(
            conn, left_start, left_end, right_start, right_end,
            left_drill, right_drill,
        )
    finally:
        conn.close()

    return render_template("components/dashboard_ie_insights.html",
                           insights=insights)


@bp.route("/dashboard/insight-detail")
def insight_detail():
    """Return HTML popup content for a specific insight type."""
    from markupsafe import Markup, escape

    itype = request.args.get("type", "")
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    account = request.args.get("account", "")
    category = request.args.get("category", "")

    xfer_exclude = "AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')"
    acct_clause = "AND account = ?" if account else ""
    acct_binds = [account] if account else []

    conn = get_connection(g.entity_key)
    try:
        if itype == "new_merchants":
            lookback = ""
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                lookback = (start_dt - timedelta(days=90)).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                return "<p>Invalid date range.</p>"

            rows = conn.execute(
                f"SELECT merchant_canonical, COUNT(*) AS cnt, "
                f"  COALESCE(SUM(ABS(amount_cents)), 0) AS total_cents "
                f"FROM transactions "
                f"WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
                f"  AND date >= ? AND date <= ? "
                f"  {xfer_exclude} {acct_clause} "
                f"  AND merchant_canonical NOT IN ("
                f"    SELECT DISTINCT merchant_canonical FROM transactions "
                f"    WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
                f"      AND date >= ? AND date < ? "
                f"      {xfer_exclude} {acct_clause}"
                f"  ) "
                f"GROUP BY merchant_canonical ORDER BY total_cents DESC",
                [start, end] + acct_binds + [lookback, start] + acct_binds,
            ).fetchall()

            title = "New Merchants"
            desc = "Merchants you haven't seen in the prior 90 days."
            items_html = ""
            for r in rows:
                name = escape(r["merchant_canonical"])
                amt = f"${r['total_cents'] / 100:,.0f}"
                cnt = r["cnt"]
                items_html += (
                    f'<div class="iu-detail-row">'
                    f'<span class="iu-detail-name">{name}</span>'
                    f'<span class="iu-detail-meta">{cnt} txn{"s" if cnt != 1 else ""} &middot; {amt}</span>'
                    f'</div>'
                )

        elif itype == "large_txns":
            rows = conn.execute(
                f"SELECT date, merchant_canonical, amount_cents FROM transactions "
                f"WHERE ABS(amount_cents) > 50000 "
                f"  AND date >= ? AND date <= ? "
                f"  {xfer_exclude} {acct_clause} "
                f"ORDER BY ABS(amount_cents) DESC",
                [start, end] + acct_binds,
            ).fetchall()

            title = "Large Transactions"
            desc = "Transactions over $500 this period."
            items_html = ""
            for r in rows:
                name = escape(r["merchant_canonical"] or "Unknown")
                amt_cents = r["amount_cents"]
                amt = f"${abs(amt_cents) / 100:,.0f}"
                date_str = r["date"]
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    date_str = dt.strftime("%b %-d")
                except (ValueError, TypeError):
                    pass
                items_html += (
                    f'<div class="iu-detail-row">'
                    f'<span class="iu-detail-name">{name}</span>'
                    f'<span class="iu-detail-meta">{date_str} &middot; {amt}</span>'
                    f'</div>'
                )

        elif itype == "category_increase":
            rows = conn.execute(
                f"SELECT date, merchant_canonical, amount_cents FROM transactions "
                f"WHERE amount_cents < 0 AND category = ? "
                f"  AND date >= ? AND date <= ? "
                f"  {acct_clause} "
                f"ORDER BY ABS(amount_cents) DESC LIMIT 10",
                [category, start, end] + acct_binds,
            ).fetchall()

            title = escape(category)
            desc = f"Top charges in {escape(category)} this period."
            items_html = ""
            for r in rows:
                name = escape(r["merchant_canonical"] or "Unknown")
                amt = f"${abs(r['amount_cents']) / 100:,.0f}"
                date_str = r["date"]
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    date_str = dt.strftime("%b %-d")
                except (ValueError, TypeError):
                    pass
                items_html += (
                    f'<div class="iu-detail-row">'
                    f'<span class="iu-detail-name">{name}</span>'
                    f'<span class="iu-detail-meta">{date_str} &middot; {amt}</span>'
                    f'</div>'
                )
        else:
            return "<p>Unknown insight type.</p>"
    finally:
        conn.close()

    insight_key = escape(request.args.get("insight_key", ""))
    got_it_btn = ""
    if insight_key:
        dismiss_url = url_for("dashboard.insight_dismiss")
        got_it_btn = (
            f'<div class="iu-detail-footer">'
            f'<button type="button" class="btn btn-secondary btn-sm"'
            f' hx-post="{dismiss_url}" hx-vals=\'{{"insight_key": "{insight_key}"}}\''
            f' hx-swap="none"'
            f' onclick="iuDismissAndClose(\'{insight_key}\')">Got it</button>'
            f'</div>'
        )

    return Markup(
        f'<div class="iu-detail-title">{title}</div>'
        f'<p class="iu-detail-desc">{desc}</p>'
        f'<div class="iu-detail-list">{items_html}</div>'
        f'{got_it_btn}'
    )


@bp.route("/dashboard/subcategory-txns")
def subcategory_txns():
    """Return a transaction list popup for a given category + subcategory."""
    cat_id = request.args.get("category_id", type=int)
    subcat = request.args.get("subcategory", "")
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    start2 = request.args.get("start2", "")
    end2 = request.args.get("end2", "")
    label1 = request.args.get("label1", "")
    label2 = request.args.get("label2", "")
    account = request.args.get("account", "")

    compare_mode = bool(start2 and end2)

    conn = get_connection(g.entity_key)
    try:
        # Resolve category_id to name
        cat_row = conn.execute(
            "SELECT name FROM categories WHERE id = ?", (cat_id,)
        ).fetchone() if cat_id else None
        cat_name = cat_row["name"] if cat_row else ""

        def _query_period(p_start, p_end):
            conditions = ["t.category = ?", "t.subcategory = ?"]
            params = [cat_name, subcat]
            if p_start:
                conditions.append("t.date >= ?")
                params.append(p_start)
            if p_end:
                conditions.append("t.date <= ?")
                params.append(p_end)
            if account:
                conditions.append("t.account = ?")
                params.append(account)
            where = " AND ".join(conditions)
            return conn.execute(f"""
                SELECT date, merchant_canonical, description_raw, amount_cents
                FROM transactions t
                WHERE {where}
                ORDER BY date DESC
                LIMIT 50
            """, params).fetchall()

        if compare_mode:
            txns_left = _query_period(start, end)
            txns_right = _query_period(start2, end2)
            txns = None  # not used in compare mode
        else:
            txns = _query_period(start, end)
            txns_left = None
            txns_right = None
    finally:
        conn.close()

    # Build fallback URL for "View all in Transactions"
    fallback_qp = {"category_id": cat_id, "subcategory": subcat}
    if start:
        fallback_qp["start"] = start
    if end:
        fallback_qp["end"] = end
    if account:
        fallback_qp["account"] = account
    fallback_url = url_for("transactions.index", **fallback_qp)

    return render_template("components/subcat_txns_popup.html",
                           txns=txns,
                           txns_left=txns_left,
                           txns_right=txns_right,
                           label1=label1,
                           label2=label2,
                           compare_mode=compare_mode,
                           cat_name=cat_name,
                           subcat_name=subcat,
                           fallback_url=fallback_url)


@bp.route("/dashboard/insight-dismiss", methods=["POST"])
def insight_dismiss():
    """Dismiss an insight so it doesn't show again for this period."""
    insight_key = request.form.get("insight_key", "").strip()
    if not insight_key:
        return "", 400

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO insight_dismissals (insight_key, dismissed_at) "
            "VALUES (?, ?)",
            (insight_key, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    return "", 204


# ── AI Analysis ──────────────────────────────────────────────────────────────

import time as _time

_ai_cache: dict[tuple, tuple[float, list]] = {}
_AI_CACHE_TTL = 3600  # 1 hour


def _build_spending_summary(conn, left_start, left_end, right_start, right_end,
                            entity_type):
    """Build a compact text summary of spending data for AI analysis."""
    xfer_exclude = "AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')"

    lines = [f"Entity type: {entity_type}"]

    # Period summaries
    for label, start, end in [("Left period", left_start, left_end),
                               ("Right period", right_start, right_end)]:
        spend = conn.execute(
            f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? {xfer_exclude}",
            (start, end),
        ).fetchone()[0]
        income = conn.execute(
            f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
            f"WHERE amount_cents > 0 AND date >= ? AND date <= ? {xfer_exclude}",
            (start, end),
        ).fetchone()[0]
        txn_count = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE date >= ? AND date <= ?",
            (start, end),
        ).fetchone()[0]
        net = income - spend
        lines.append(
            f"{label} ({start} to {end}): "
            f"Spent ${spend / 100:,.0f} | Income ${income / 100:,.0f} | "
            f"Net ${net / 100:,.0f} | {txn_count} transactions"
        )

    # Category breakdowns
    for label, start, end in [("Left period", left_start, left_end),
                               ("Right period", right_start, right_end)]:
        cat_rows = conn.execute(
            f"SELECT category, COUNT(*) AS cnt, "
            f"  COALESCE(SUM(ABS(amount_cents)), 0) AS total "
            f"FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? "
            f"  AND category IS NOT NULL AND category != '' {xfer_exclude} "
            f"GROUP BY category ORDER BY total DESC LIMIT 10",
            (start, end),
        ).fetchall()
        lines.append(f"\n{label} categories:")
        for r in cat_rows:
            lines.append(f"  {r['category']}: ${r['total'] / 100:,.0f} ({r['cnt']} txns)")

    # Top merchants
    for label, start, end in [("Left period", left_start, left_end),
                               ("Right period", right_start, right_end)]:
        merch_rows = conn.execute(
            f"SELECT merchant_canonical, COUNT(*) AS cnt, "
            f"  COALESCE(SUM(ABS(amount_cents)), 0) AS total "
            f"FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? "
            f"  AND merchant_canonical IS NOT NULL AND merchant_canonical != '' "
            f"  {xfer_exclude} "
            f"GROUP BY merchant_canonical ORDER BY total DESC LIMIT 10",
            (start, end),
        ).fetchall()
        lines.append(f"\n{label} top merchants:")
        for r in merch_rows:
            lines.append(f"  {r['merchant_canonical']}: ${r['total'] / 100:,.0f} ({r['cnt']} txns)")

    # 3-month spending trend
    now = datetime.now()
    lines.append("\n3-month spending trend:")
    for i in range(2, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        import calendar as _cal
        m_start = f"{y:04d}-{m:02d}-01"
        m_end = f"{y:04d}-{m:02d}-{_cal.monthrange(y, m)[1]:02d}"
        m_spend = conn.execute(
            f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? {xfer_exclude}",
            (m_start, m_end),
        ).fetchone()[0]
        lines.append(f"  {_cal.month_abbr[m]} {y}: ${m_spend / 100:,.0f}")

    return "\n".join(lines)


@bp.route("/dashboard/ai-analysis", methods=["POST"])
def ai_analysis():
    """Generate AI-powered spending analysis (HTMX endpoint)."""
    from core.ai_client import generate_spending_analysis

    left_period = request.form.get("left_period", "this_month")
    right_period = request.form.get("right_period", "last_month")

    cache_key = (g.entity_key, left_period, right_period)

    # Check cache
    now = _time.time()
    if cache_key in _ai_cache:
        cached_time, cached_results = _ai_cache[cache_key]
        if now - cached_time < _AI_CACHE_TTL:
            return _render_ai_results(cached_results)

    # Purge stale cache entries
    stale = [k for k, (t, _) in _ai_cache.items() if now - t >= _AI_CACHE_TTL]
    for k in stale:
        del _ai_cache[k]

    left_start, left_end = _period_to_dates(left_period)
    right_start, right_end = _period_to_dates(right_period)

    conn = get_connection(g.entity_key)
    try:
        summary = _build_spending_summary(
            conn, left_start, left_end, right_start, right_end,
            g.entity_display.lower(),
        )
    finally:
        conn.close()

    results = generate_spending_analysis(summary)
    if results:
        # Resolve category drill links
        conn2 = get_connection(g.entity_key)
        try:
            for insight in results:
                cat = insight.get("category")
                if cat:
                    cat_row = conn2.execute(
                        "SELECT id FROM categories WHERE name = ?", (cat,)
                    ).fetchone()
                    if cat_row:
                        insight["url"] = url_for(
                            "transactions.index",
                            category_id=cat_row["id"],
                            start=left_start, end=left_end,
                        )
        finally:
            conn2.close()

        _ai_cache[cache_key] = (now, results)
        return _render_ai_results(results)

    return render_template("components/ai_analysis.html", insights=None)


def _render_ai_results(results):
    """Render AI analysis results partial."""
    return render_template("components/ai_analysis.html", insights=results)


# ── Income vs Expenses AI Analysis ──────────────────────────────────────────

_ie_ai_cache: dict[tuple, tuple[float, list]] = {}


def _build_ie_summary(conn, entity_type):
    """Build a text summary of 12-month income vs expenses for AI analysis."""
    xfer_exclude = (
        "AND COALESCE(category,'') NOT IN "
        "('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')"
    )
    now = datetime.now()
    import calendar as _cal

    lines = [f"Entity type: {entity_type}", "", "Monthly income vs expenses (last 12 months):"]

    total_income = 0
    total_expense = 0
    for i in range(11, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        m_start = f"{y:04d}-{m:02d}-01"
        m_end = f"{y:04d}-{m:02d}-{_cal.monthrange(y, m)[1]:02d}"

        income = conn.execute(
            f"SELECT COALESCE(SUM(amount_cents), 0) FROM transactions "
            f"WHERE amount_cents > 0 AND date >= ? AND date <= ? {xfer_exclude}",
            (m_start, m_end),
        ).fetchone()[0]
        expense = conn.execute(
            f"SELECT COALESCE(SUM(ABS(amount_cents)), 0) FROM transactions "
            f"WHERE amount_cents < 0 AND date >= ? AND date <= ? {xfer_exclude}",
            (m_start, m_end),
        ).fetchone()[0]
        net = income - expense
        total_income += income
        total_expense += expense
        lines.append(
            f"  {_cal.month_abbr[m]} {y}: Income ${income / 100:,.0f} | "
            f"Expenses ${expense / 100:,.0f} | Net ${net / 100:,.0f}"
        )

    lines.append("")
    lines.append(
        f"12-month totals: Income ${total_income / 100:,.0f} | "
        f"Expenses ${total_expense / 100:,.0f} | "
        f"Net ${(total_income - total_expense) / 100:,.0f}"
    )
    if total_income > 0:
        savings_rate = (total_income - total_expense) / total_income * 100
        lines.append(f"12-month savings rate: {savings_rate:.1f}%")

    # Income sources breakdown (last 6 months)
    six_ago_y = now.year
    six_ago_m = now.month - 5
    while six_ago_m <= 0:
        six_ago_m += 12
        six_ago_y -= 1
    six_start = f"{six_ago_y:04d}-{six_ago_m:02d}-01"
    six_end = f"{now.year:04d}-{now.month:02d}-{_cal.monthrange(now.year, now.month)[1]:02d}"

    inc_cats = conn.execute(
        f"SELECT COALESCE(subcategory, category, 'Unknown') AS src, "
        f"  COALESCE(SUM(amount_cents), 0) AS total "
        f"FROM transactions "
        f"WHERE amount_cents > 0 AND date >= ? AND date <= ? {xfer_exclude} "
        f"GROUP BY src ORDER BY total DESC LIMIT 8",
        (six_start, six_end),
    ).fetchall()
    if inc_cats:
        lines.append("\nIncome sources (last 6 months):")
        for r in inc_cats:
            lines.append(f"  {r['src']}: ${r['total'] / 100:,.0f}")

    return "\n".join(lines)


@bp.route("/dashboard/ie-ai-analysis", methods=["POST"])
def ie_ai_analysis():
    """Generate AI-powered income vs expenses analysis (HTMX endpoint)."""
    from core.ai_client import generate_ie_analysis

    cache_key = (g.entity_key, "ie_analysis")

    now = _time.time()
    if cache_key in _ie_ai_cache:
        cached_time, cached_results = _ie_ai_cache[cache_key]
        if now - cached_time < _AI_CACHE_TTL:
            return render_template("components/ie_ai_analysis.html", insights=cached_results)

    stale = [k for k, (t, _) in _ie_ai_cache.items() if now - t >= _AI_CACHE_TTL]
    for k in stale:
        del _ie_ai_cache[k]

    conn = get_connection(g.entity_key)
    try:
        summary = _build_ie_summary(conn, g.entity_display.lower())
    finally:
        conn.close()

    results = generate_ie_analysis(summary)
    if results:
        _ie_ai_cache[cache_key] = (now, results)
        return render_template("components/ie_ai_analysis.html", insights=results)

    return render_template("components/ie_ai_analysis.html", insights=None)

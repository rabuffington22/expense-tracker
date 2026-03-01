"""Dashboard route — filterable KPIs, cash flow chart, top categories/merchants."""

import calendar
import statistics
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request, g, url_for, redirect

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
        if params.get("include_transfers"):
            qp["include_transfers"] = params["include_transfers"]
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

    # ── Donut chart percentages (relative to total spend) ────────────────────
    cat_total = sum(c["total_cents"] for c in top_cats)
    spend_abs = abs(data["spend_cents"]) if data["spend_cents"] else 0
    other_cents = max(0, spend_abs - cat_total)
    for c in top_cats:
        c["donut_pct"] = round(c["total_cents"] / spend_abs * 100, 1) if spend_abs else 0
    data["other_cents"] = other_cents
    data["other_pct"] = round(other_cents / spend_abs * 100, 1) if spend_abs else 0

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

    # ── Plaid sync health ─────────────────────────────────────────────────────
    data["plaid_sync_items"] = _query_plaid_sync(conn)

    # ── Recurring / Upcoming ───────────────────────────────────────────────
    recurring_patterns = _detect_recurring(conn, params)
    data["upcoming_items"] = _build_upcoming(recurring_patterns)

    # ── Drill URL builder ────────────────────────────────────────────────────
    drill_url = _make_drill_url(params)
    data["drill_url"] = drill_url
    data["colors"] = COLORS

    # ── Insights ─────────────────────────────────────────────────────────────
    data["insights"] = _compute_insights(conn, params, drill_url)

    return data


# ── Insights engine ──────────────────────────────────────────────────────────

def _compute_insights(conn, params, drill_url):
    """Return up to 3 actionable insight dicts for the current dashboard range.

    Each insight: {"icon": str, "text": str, "url": str}.
    Returns [] when no insights qualify.
    """
    insights = []

    try:
        start_dt = datetime.strptime(params["start"], "%Y-%m-%d")
        end_dt = datetime.strptime(params["end"], "%Y-%m-%d")
    except (ValueError, TypeError, KeyError):
        return insights

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
            # Look up category ID for drill link
            cat_id_row = conn.execute(
                "SELECT id FROM categories WHERE name = ?", (best_cat,)
            ).fetchone()
            cat_id = cat_id_row["id"] if cat_id_row else None
            dollars = best_increase // 100
            insights.append({
                "icon": "\U0001F4C8",  # 📈
                "text": f"{best_cat} up ${dollars:,} vs prior period",
                "url": drill_url(category_id=cat_id) if cat_id else drill_url(),
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
            insights.append({
                "icon": "\U0001F195",  # 🆕
                "text": f"{new_count} new merchant{'s' if new_count != 1 else ''} this period",
                "url": drill_url(),
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
            insights.append({
                "icon": "\U0001F4B0",  # 💰
                "text": f"{large_count} transaction{'s' if large_count != 1 else ''} over $500",
                "url": drill_url(sort="amount"),
            })
    except Exception:
        pass  # Skip this insight on any error

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


def _build_upcoming(patterns, horizon_days=30):
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
    xfer_exclude = "AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment')"

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
        "  AND t.category NOT IN ('Internal Transfer', 'Credit Card Payment') "
        "GROUP BY t.category ORDER BY total_cents DESC",
        [start, end],
    ).fetchall()


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
    finally:
        conn.close()

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

    # Sort by combined total desc, take top 12
    merged.sort(key=lambda x: x["combined"], reverse=True)
    top = merged[:12]

    # Compute bar height percentages with common scale (from displayed categories only)
    raw_max = max((c["left_cents"] for c in top), default=0)
    raw_max = max(raw_max, max((c["right_cents"] for c in top), default=0))

    # Nice-number Y-axis ticks: pick step from {1,2,5}×10^n to get ~4-5 ticks
    y_ticks, axis_max_cents = _nice_y_ticks(raw_max)

    # Bar heights are percentage of axis_max (tick ceiling), not raw max
    for c in top:
        c["left_pct"] = int(c["left_cents"] / axis_max_cents * 100) if axis_max_cents and c["left_cents"] else 0
        c["right_pct"] = int(c["right_cents"] / axis_max_cents * 100) if axis_max_cents and c["right_cents"] else 0

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
                           y_ticks=y_ticks,
                           left_period=left_period,
                           right_period=right_period,
                           left_label=period_labels.get(left_period, left_period),
                           right_label=period_labels.get(right_period, right_period),
                           left_drill=left_drill,
                           right_drill=right_drill)

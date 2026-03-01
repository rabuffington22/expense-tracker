"""Reports route — monthly detail + spending trend, category breakdown, drill-down, CSV export."""

import calendar
import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, render_template, request, g, Response

from core.db import get_connection
from core.reporting import (
    get_available_months,
    get_category_totals,
    get_income_total,
    get_merchant_totals,
    get_monthly_totals,
    get_transactions,
)

bp = Blueprint("reports", __name__, url_prefix="/reports")

# Curated palette — distinct, readable on dark backgrounds
COLORS = [
    "#0a84ff", "#30d158", "#ff453a", "#ff9f0a", "#bf5af2",
    "#64d2ff", "#ffd60a", "#ac8e68", "#98989d", "#ff6482",
    "#30b0c7", "#8e8e93",
]

_VALID_PERIODS = (3, 6, 12, 24)


# ── Date formatting helpers ──────────────────────────────────────────────────

def _current_year():
    return datetime.date.today().year


def _parse_ym(ym_str):
    """Parse 'YYYY-MM' to a date (day=1)."""
    return datetime.datetime.strptime(ym_str, "%Y-%m").date()


def fmt_month_full(ym_str):
    """'2026-02' -> 'February' (current year) or 'February 2025'."""
    dt = _parse_ym(ym_str)
    if dt.year == _current_year():
        return dt.strftime("%B")
    return dt.strftime("%B %Y")


def fmt_month_short(ym_str):
    """'2026-02' -> 'Feb' (current year) or 'Feb 25'."""
    dt = _parse_ym(ym_str)
    if dt.year == _current_year():
        return dt.strftime("%b")
    return dt.strftime("%b") + " " + dt.strftime("%y")


def fmt_date(date_str):
    """'2026-02-15' -> 'Feb 15' (current year) or 'Feb 15, 2025'."""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return date_str
    if dt.year == _current_year():
        return dt.strftime("%b") + " " + str(dt.day)
    return dt.strftime("%b") + " " + str(dt.day) + ", " + str(dt.year)


# ── CSV filename helper ───────────────────────────────────────────────────────

def _month_range(ym_str):
    """Return (start_date, end_date) as YYYY-MM-DD strings for a month."""
    dt = _parse_ym(ym_str)
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return (
        f"{dt.year:04d}-{dt.month:02d}-01",
        f"{dt.year:04d}-{dt.month:02d}-{last_day:02d}",
    )


def _csv_filename(entity_key, report_type, ym_str):
    """Build filename: <entity>_<report>_<start>_<end>.csv"""
    start, end = _month_range(ym_str)
    return f"{entity_key}_{report_type}_{start}_{end}.csv"


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    months = get_available_months(g.entity_key)
    if not months:
        return render_template("reports.html", months=[], has_data=False)

    # ── Parse params ──────────────────────────────────────────────────────
    selected_month = request.args.get("month", months[-1])
    if selected_month not in months:
        selected_month = months[-1]

    period = request.args.get("period", "6")
    try:
        period = int(period)
    except ValueError:
        period = 6
    if period not in _VALID_PERIODS:
        period = 6

    # ── Top Section: Month navigation ─────────────────────────────────────
    month_idx = months.index(selected_month)
    prev_month = months[month_idx - 1] if month_idx > 0 else None
    next_month = months[month_idx + 1] if month_idx < len(months) - 1 else None

    # ── Top Section: Category breakdown ───────────────────────────────────
    cat_df = get_category_totals(g.entity_key, selected_month)
    cat_rows = []
    if not cat_df.empty:
        # Look up category IDs for drill links (D5)
        conn = get_connection(g.entity_key)
        try:
            cat_id_map = {}
            for id_row in conn.execute("SELECT id, name FROM categories").fetchall():
                cat_id_map[id_row["name"]] = id_row["id"]
        finally:
            conn.close()

        for _, row in cat_df.iterrows():
            cat_rows.append({
                "category": row["category"],
                "count": int(row["count"]),
                "total_amount": float(row["total_amount"]),
                "cat_id": cat_id_map.get(row["category"]),
            })

    max_cat_amount = cat_rows[0]["total_amount"] if cat_rows else 1
    for r in cat_rows:
        r["pct"] = round(r["total_amount"] / max_cat_amount * 100, 1) if max_cat_amount else 0

    # Month date range for drill links
    sel_dt = _parse_ym(selected_month)
    month_start = f"{sel_dt.year:04d}-{sel_dt.month:02d}-01"
    last_day = calendar.monthrange(sel_dt.year, sel_dt.month)[1]
    month_end = f"{sel_dt.year:04d}-{sel_dt.month:02d}-{last_day:02d}"

    # ── Top Section: Summary stats ────────────────────────────────────────
    detail_income = get_income_total(g.entity_key, selected_month)
    total_spend = sum(r["total_amount"] for r in cat_rows)
    summary = {
        "total_spend": total_spend,
        "total_income": detail_income,
        "net": detail_income - total_spend,
        "total_txns": sum(r["count"] for r in cat_rows),
    }

    # ── Top Section: Drill-down ───────────────────────────────────────────
    drill_cat = request.args.get("drill")
    drill_txns = []
    if drill_cat:
        txn_df = get_transactions(g.entity_key, month=selected_month, category=drill_cat)
        if not txn_df.empty:
            for _, row in txn_df.iterrows():
                drill_txns.append({
                    "date": row.get("date", ""),
                    "description_raw": row.get("description_raw", ""),
                    "merchant_canonical": row.get("merchant_canonical", ""),
                    "amount": float(row.get("amount", 0)),
                    "account": row.get("account", ""),
                })

    # ── Bottom Section: Spending trend chart ──────────────────────────────
    chart_bars = _build_chart_bars(g.entity_key, months[-1], period, selected_month)

    return render_template(
        "reports.html",
        has_data=True,
        months=months,
        selected_month=selected_month,
        prev_month=prev_month,
        next_month=next_month,
        period=period,
        chart_bars=chart_bars,
        cat_rows=cat_rows,
        drill_cat=drill_cat,
        drill_txns=drill_txns,
        summary=summary,
        colors=COLORS,
        fmt_month=fmt_month_full,
        fmt_month_short=fmt_month_short,
        fmt_date=fmt_date,
        month_start=month_start,
        month_end=month_end,
    )


@bp.route("/export-csv")
def export_csv():
    """Export transactions as CSV for a month, optionally filtered by category."""
    month = request.args.get("month", "")
    category = request.args.get("category", "")
    if not month:
        return "Missing month parameter", 400

    txn_df = get_transactions(g.entity_key, month=month, category=category or None)
    if txn_df.empty:
        return "No data", 404

    # Format for CPA-friendly output: ISO dates, decimal dollars, minus sign
    out = txn_df[["date", "description_raw", "merchant_canonical",
                   "amount", "category", "account"]].copy()
    out.columns = ["Date", "Description", "Merchant", "Amount", "Category", "Account"]
    out["Amount"] = out["Amount"].apply(lambda v: f"{v:.2f}")

    csv_data = out.to_csv(index=False)
    if category:
        slug = category.lower().replace(" ", "_")
        filename = _csv_filename(g.entity_key, f"transactions_{slug}", month)
    else:
        filename = _csv_filename(g.entity_key, "transactions", month)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@bp.route("/export-categories")
def export_categories():
    """Export category summary CSV for a month."""
    month = request.args.get("month", "")
    if not month:
        return "Missing month parameter", 400

    cat_df = get_category_totals(g.entity_key, month)
    if cat_df.empty:
        return "No data", 404

    out = cat_df[["category", "count", "total_amount"]].copy()
    out.columns = ["Category", "Transactions", "Total"]
    out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")

    csv_data = out.to_csv(index=False)
    filename = _csv_filename(g.entity_key, "categories", month)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@bp.route("/export-merchants")
def export_merchants():
    """Export merchant summary CSV for a month."""
    month = request.args.get("month", "")
    if not month:
        return "Missing month parameter", 400

    merch_df = get_merchant_totals(g.entity_key, month)
    if merch_df.empty:
        return "No data", 404

    out = merch_df[["merchant", "count", "total_amount"]].copy()
    out.columns = ["Merchant", "Transactions", "Total"]
    out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")

    csv_data = out.to_csv(index=False)
    filename = _csv_filename(g.entity_key, "merchants", month)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Chart builder ────────────────────────────────────────────────────────────

def _build_chart_bars(entity_key, latest_month, period, selected_month):
    """Build template-ready bar data for a variable-length trend chart."""
    try:
        end_dt = datetime.datetime.strptime(latest_month, "%Y-%m")
    except ValueError:
        end_dt = datetime.datetime.now().replace(day=1)

    # Generate month keys for the period
    month_keys = []
    for i in range(period - 1, -1, -1):
        dt = end_dt - relativedelta(months=i)
        month_keys.append(dt.strftime("%Y-%m"))

    # Fetch spending data
    start_key = month_keys[0]
    end_key = month_keys[-1]
    monthly_df = get_monthly_totals(entity_key, start_key, end_key)

    totals = {}
    if not monthly_df.empty:
        totals = monthly_df.groupby("month")["total_amount"].sum().to_dict()

    # Build bar dicts
    bars = []
    max_val = max((totals.get(m, 0) for m in month_keys), default=0) or 1
    for m in month_keys:
        val = float(totals.get(m, 0))
        raw_pct = round(val / max_val * 100, 1) if max_val else 0
        pct = max(raw_pct, 4) if val > 0 else 0  # Floor so tiny bars stay visible
        bars.append({
            "month_key": m,
            "label": fmt_month_short(m),
            "value": val,
            "display": "${:,.0f}".format(val) if val > 0 else "",
            "pct": pct,
            "has_data": val > 0,
            "is_selected": m == selected_month,
        })

    return bars

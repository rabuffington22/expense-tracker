"""Reports route — monthly detail + spending trend, category breakdown, drill-down, CSV export."""

import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, render_template, request, g, Response

from core.reporting import (
    get_available_months,
    get_category_totals,
    get_income_total,
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
        for _, row in cat_df.iterrows():
            cat_rows.append({
                "category": row["category"],
                "count": int(row["count"]),
                "total_amount": float(row["total_amount"]),
            })

    max_cat_amount = cat_rows[0]["total_amount"] if cat_rows else 1
    for r in cat_rows:
        r["pct"] = round(r["total_amount"] / max_cat_amount * 100, 1) if max_cat_amount else 0

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
    )


@bp.route("/export-csv")
def export_csv():
    """Export transactions as CSV. If category is provided, exports just that category."""
    month = request.args.get("month", "")
    category = request.args.get("category", "")
    if not month:
        return "Missing month parameter", 400

    txn_df = get_transactions(g.entity_key, month=month, category=category or None)
    if txn_df.empty:
        return "No data", 404

    csv_data = txn_df.to_csv(index=False)
    if category:
        filename = f"{g.entity_key}_{month}_{category.lower().replace(' ', '_')}.csv"
    else:
        filename = f"{g.entity_key}_{month}_all.csv"
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

"""Reports route — monthly spend chart, category breakdown, drill-down, CSV export."""

import io
import json

from flask import Blueprint, render_template, request, g, Response

from core.reporting import (
    get_available_months,
    get_category_totals,
    get_income_total,
    get_monthly_income,
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


@bp.route("/")
def index():
    months = get_available_months(g.entity_key)
    if not months:
        return render_template("reports.html", months=[], has_data=False)

    start_month = request.args.get("start", months[0])
    end_month = request.args.get("end", months[-1])

    if start_month > end_month:
        start_month, end_month = end_month, start_month

    # ── Monthly totals for bar chart ─────────────────────────────────────────
    monthly_df = get_monthly_totals(g.entity_key, start_month, end_month)

    # ── Income data (stat cards only, not on chart) ──────────────────────────
    income_df = get_monthly_income(g.entity_key, start_month, end_month)
    income_by_month = {}
    if not income_df.empty:
        for _, row in income_df.iterrows():
            income_by_month[row["month"]] = float(row["total_income"])

    chart_data = None
    if not monthly_df.empty:
        chart_data = _build_chart_json(monthly_df, start_month, end_month)

    # ── Detail month (default to most recent) ────────────────────────────────
    detail_month = request.args.get("detail", end_month)
    range_months = [m for m in months if start_month <= m <= end_month]
    if detail_month not in range_months and range_months:
        detail_month = range_months[-1]

    cat_df = get_category_totals(g.entity_key, detail_month)
    cat_rows = []
    if not cat_df.empty:
        for _, row in cat_df.iterrows():
            cat_rows.append({
                "category": row["category"],
                "count": int(row["count"]),
                "total_amount": float(row["total_amount"]),
            })

    # Compute percentage bars (relative to largest category)
    max_cat_amount = cat_rows[0]["total_amount"] if cat_rows else 1
    for r in cat_rows:
        r["pct"] = round(r["total_amount"] / max_cat_amount * 100, 1) if max_cat_amount else 0

    # ── Summary stats ────────────────────────────────────────────────────────
    detail_income = get_income_total(g.entity_key, detail_month)
    total_spend = sum(r["total_amount"] for r in cat_rows)
    summary = {
        "total_spend": total_spend,
        "total_income": detail_income,
        "net": detail_income - total_spend,
        "total_txns": sum(r["count"] for r in cat_rows),
        "top_category": cat_rows[0]["category"] if cat_rows else "",
        "top_category_amount": cat_rows[0]["total_amount"] if cat_rows else 0,
        "num_categories": len(cat_rows),
    }

    # ── Drill-down ───────────────────────────────────────────────────────────
    drill_cat = request.args.get("drill")
    drill_txns = []
    if drill_cat:
        txn_df = get_transactions(g.entity_key, month=detail_month, category=drill_cat)
        if not txn_df.empty:
            for _, row in txn_df.iterrows():
                drill_txns.append({
                    "date": row.get("date", ""),
                    "description_raw": row.get("description_raw", ""),
                    "merchant_canonical": row.get("merchant_canonical", ""),
                    "amount": float(row.get("amount", 0)),
                    "account": row.get("account", ""),
                    "notes": row.get("notes", ""),
                })

    return render_template(
        "reports.html",
        months=months,
        has_data=True,
        start_month=start_month,
        end_month=end_month,
        chart_data=chart_data,
        detail_month=detail_month,
        range_months=range_months,
        cat_rows=cat_rows,
        drill_cat=drill_cat,
        drill_txns=drill_txns,
        summary=summary,
        colors=COLORS,
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


def _build_chart_json(df, start_month, end_month):
    """Build Plotly JSON — clean single-color monthly total bars."""
    # Aggregate to total spend per month (across all categories)
    monthly_totals = df.groupby("month")["total_amount"].sum().reset_index()
    monthly_totals = monthly_totals.sort_values("month")

    months = list(monthly_totals["month"])
    # Format month labels: "2026-01" -> "Jan 2026"
    import datetime
    month_labels = []
    for m in months:
        try:
            dt = datetime.datetime.strptime(m, "%Y-%m")
            month_labels.append(dt.strftime("%b %Y"))
        except ValueError:
            month_labels.append(m)
    values = [float(v) for v in monthly_totals["total_amount"]]

    traces = [{
        "x": month_labels,
        "y": values,
        "type": "bar",
        "marker": {
            "color": "rgba(10, 132, 255, 0.85)",
            "line": {"width": 0},
        },
        "hovertemplate": "<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        "text": ["${:,.0f}".format(v) for v in values],
        "textposition": "outside",
        "textfont": {
            "size": 12,
            "color": "rgba(245,245,247,0.7)",
            "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif",
        },
    }]

    max_val = max(values) if values else 0

    layout = {
        "xaxis": {
            "type": "category",
            "tickangle": 0,
            "tickfont": {"size": 12, "color": "rgba(245,245,247,0.5)"},
            "gridcolor": "rgba(0,0,0,0)",
            "linecolor": "rgba(0,0,0,0)",
            "zeroline": False,
            "fixedrange": True,
        },
        "yaxis": {
            "visible": False,
            "fixedrange": True,
            "range": [0, max_val * 1.2] if max_val else [0, 100],
        },
        "hovermode": "x",
        "hoverlabel": {
            "bgcolor": "#2c2c2e",
            "bordercolor": "rgba(255,255,255,0.08)",
            "font": {
                "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif",
                "size": 13,
                "color": "#f5f5f7",
            },
        },
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": "#f5f5f7",
            "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif",
        },
        "showlegend": False,
        "height": 280,
        "margin": {"l": 0, "r": 0, "t": 24, "b": 40},
        "bargap": 0.4,
    }

    return json.dumps({"data": traces, "layout": layout})

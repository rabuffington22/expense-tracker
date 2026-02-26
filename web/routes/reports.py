"""Reports route — stacked bar chart, category totals, drill-down, CSV export."""

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

# Apple-style color palette (iOS system colors)
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

    # ── Stacked bar chart data ───────────────────────────────────────────────
    monthly_df = get_monthly_totals(g.entity_key, start_month, end_month)

    # ── Income data ───────────────────────────────────────────────────────────
    income_df = get_monthly_income(g.entity_key, start_month, end_month)
    income_by_month = {}
    if not income_df.empty:
        for _, row in income_df.iterrows():
            income_by_month[row["month"]] = float(row["total_income"])

    chart_data = None
    if not monthly_df.empty:
        chart_data = _build_chart_json(monthly_df, start_month, end_month, income_by_month)

    # ── Detail month ─────────────────────────────────────────────────────────
    detail_month = request.args.get("detail", start_month)
    range_months = [m for m in months if start_month <= m <= end_month]
    if detail_month not in range_months and range_months:
        detail_month = range_months[0]

    cat_df = get_category_totals(g.entity_key, detail_month)
    cat_rows = []
    if not cat_df.empty:
        for _, row in cat_df.iterrows():
            cat_rows.append({
                "category": row["category"],
                "count": int(row["count"]),
                "total_amount": float(row["total_amount"]),
            })

    # ── Summary stats ────────────────────────────────────────────────────────
    detail_income = get_income_total(g.entity_key, detail_month)
    summary = {
        "total_spend": sum(r["total_amount"] for r in cat_rows),
        "total_income": detail_income,
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


def _build_chart_json(df, start_month, end_month, income_by_month=None):
    """Build Plotly traces JSON for client-side rendering."""
    pivot = df.pivot_table(
        index="month", columns="category", values="total_amount", fill_value=0
    )

    traces = []
    for i, cat in enumerate(sorted(pivot.columns)):
        traces.append({
            "x": list(pivot.index),
            "y": [float(v) for v in pivot[cat].values],
            "name": cat,
            "type": "bar",
            "marker": {
                "color": COLORS[i % len(COLORS)],
                "line": {"width": 0},
            },
            "hovertemplate": "<b>%{fullData.name}</b><br>$%{y:,.2f}<extra></extra>",
        })

    # Income overlay line
    if income_by_month:
        months_in_chart = list(pivot.index)
        income_values = [income_by_month.get(m, 0) for m in months_in_chart]
        if any(v > 0 for v in income_values):
            traces.append({
                "x": months_in_chart,
                "y": income_values,
                "name": "Income",
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"color": "#30d158", "width": 2.5},
                "marker": {"size": 6, "color": "#30d158"},
                "hovertemplate": "<b>Income</b><br>$%{y:,.2f}<extra></extra>",
            })

    layout = {
        "barmode": "stack",
        "xaxis": {
            "tickangle": 0,
            "tickfont": {"size": 12},
            "gridcolor": "rgba(0,0,0,0)",
            "linecolor": "rgba(0,0,0,0)",
            "zeroline": False,
        },
        "yaxis": {
            "tickprefix": "$",
            "tickformat": ",.0f",
            "tickfont": {"size": 11},
            "gridcolor": "rgba(255,255,255,0.04)",
            "linecolor": "rgba(0,0,0,0)",
            "zeroline": False,
        },
        "hovermode": "x unified",
        "hoverlabel": {
            "bgcolor": "#2c2c2e",
            "bordercolor": "rgba(255,255,255,0.1)",
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
        "legend": {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 11},
            "itemsizing": "constant",
            "traceorder": "normal",
        },
        "height": 380,
        "margin": {"l": 60, "r": 20, "t": 16, "b": 60},
        "bargap": 0.35,
    }

    return json.dumps({"data": traces, "layout": layout})

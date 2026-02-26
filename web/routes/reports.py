"""Reports route — stacked bar chart, category totals, drill-down, CSV export."""

import io
import json

from flask import Blueprint, render_template, request, g, Response

from core.reporting import (
    get_available_months,
    get_category_totals,
    get_monthly_totals,
    get_transactions,
)

bp = Blueprint("reports", __name__, url_prefix="/reports")


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
    chart_data = None
    if not monthly_df.empty:
        # Build Plotly-compatible JSON for client-side rendering
        chart_data = _build_chart_json(monthly_df, start_month, end_month)

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
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _build_chart_json(df, start_month, end_month):
    """Build Plotly traces JSON for client-side rendering."""
    # Pivot: rows=months, columns=categories, values=amounts
    pivot = df.pivot_table(
        index="month", columns="category", values="total_amount", fill_value=0
    )

    traces = []
    # Color palette
    colors = [
        "#0a84ff", "#30d158", "#ff453a", "#ff9f0a", "#bf5af2",
        "#64d2ff", "#ffd60a", "#ac8e68", "#98989d", "#ff6482",
        "#30b0c7", "#8e8e93",
    ]
    for i, cat in enumerate(sorted(pivot.columns)):
        traces.append({
            "x": list(pivot.index),
            "y": [float(v) for v in pivot[cat].values],
            "name": cat,
            "type": "bar",
            "marker": {"color": colors[i % len(colors)]},
        })

    layout = {
        "barmode": "stack",
        "title": f"Monthly Spend by Category ({start_month} - {end_month})",
        "xaxis": {"title": "Month", "tickangle": -30},
        "yaxis": {"title": "Spend ($)"},
        "hovermode": "x unified",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#f5f5f7"},
        "legend": {"title": {"text": "Category"}},
        "height": 420,
    }

    return json.dumps({"data": traces, "layout": layout})

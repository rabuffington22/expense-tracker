"""Reports route — quick monthly exports + traditional report builder."""

import calendar
import datetime

from flask import Blueprint, render_template, request, g, Response

from core.db import get_connection
from web.export_helpers import dataframe_to_pdf, transactions_to_qbo
from core.reporting import (
    get_available_months,
    get_category_totals,
    get_income_total,
    get_merchant_totals,
    get_monthly_totals,
    get_transactions,
    # Date-range report builder queries
    get_transactions_daterange,
    get_category_totals_daterange,
    get_merchant_totals_daterange,
    get_month_over_month,
    get_income_vs_expenses_daterange,
    get_recurring_charges,
    get_tax_summary,
    get_account_summary,
)

bp = Blueprint("reports", __name__, url_prefix="/reports")

# Curated palette — imported by dashboard.py for donut chart
COLORS = [
    "#0a84ff", "#30d158", "#ff453a", "#ff9f0a", "#bf5af2",
    "#64d2ff", "#ffd60a", "#ac8e68", "#98989d", "#ff6482",
    "#30b0c7", "#8e8e93",
]


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


# ── CSV filename helpers ─────────────────────────────────────────────────────

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


def _csv_filename_range(entity_key, report_type, start_date, end_date):
    """Build filename: <entity>_<report>_<start>_<end>.csv"""
    return f"{entity_key}_{report_type}_{start_date}_{end_date}.csv"


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    months = get_available_months(g.entity_key)
    if not months:
        return render_template("reports.html", months=[], has_data=False,
                               summary={"total_txns": 0})

    # Selected month for quick export cards
    selected_month = request.args.get("month", months[-1])
    if selected_month not in months:
        selected_month = months[-1]

    # Summary for has_data / total_txns check
    cat_df = get_category_totals(g.entity_key, selected_month)
    total_txns = int(cat_df["count"].sum()) if not cat_df.empty else 0
    summary = {"total_txns": total_txns}

    # Default date range for report builder: first of current month → today
    today = datetime.date.today()
    default_start = today.replace(day=1).isoformat()
    default_end = today.isoformat()

    return render_template(
        "reports.html",
        has_data=True,
        months=months,
        selected_month=selected_month,
        summary=summary,
        fmt_month=fmt_month_full,
        default_start=default_start,
        default_end=default_end,
    )


# ── Quick monthly exports (used by export cards) ────────────────────────────

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


# ── Unified report builder export ────────────────────────────────────────────

@bp.route("/export")
def export():
    """Unified export endpoint for the report builder."""
    report_type = request.args.get("report_type", "transactions")
    start_date = request.args.get("start", "")
    end_date = request.args.get("end", "")

    if not start_date or not end_date:
        return "Missing date range", 400

    entity = g.entity_key

    if report_type == "transactions":
        df = get_transactions_daterange(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df[["date", "description_raw", "merchant_canonical",
                   "amount", "category", "subcategory", "account", "notes"]].copy()
        out.columns = ["Date", "Description", "Merchant", "Amount",
                        "Category", "Subcategory", "Account", "Notes"]
        out["Amount"] = out["Amount"].apply(lambda v: f"{v:.2f}")
        label = "transactions"

    elif report_type == "categories":
        df = get_category_totals_daterange(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df[["category", "count", "total_amount"]].copy()
        out.columns = ["Category", "Transactions", "Total"]
        out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")
        label = "category_summary"

    elif report_type == "merchants":
        df = get_merchant_totals_daterange(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df[["merchant", "count", "total_amount"]].copy()
        out.columns = ["Merchant", "Transactions", "Total"]
        out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")
        label = "merchant_summary"

    elif report_type == "month_over_month":
        df = get_month_over_month(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        pivot = df.pivot_table(
            index="category", columns="month",
            values="total_amount", fill_value=0,
        )
        pivot["Total"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("Total", ascending=False)
        for col in pivot.columns:
            pivot[col] = pivot[col].apply(lambda v: f"{v:.2f}")
        pivot.index.name = "Category"
        out = pivot.reset_index()
        label = "month_over_month"

    elif report_type == "income_expenses":
        df = get_income_vs_expenses_daterange(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df.copy()
        out.columns = ["Month", "Expenses", "Income"]
        out["Net"] = out["Income"].astype(float) - out["Expenses"].astype(float)
        for col in ["Expenses", "Income", "Net"]:
            out[col] = out[col].apply(lambda v: f"{v:.2f}")
        label = "income_vs_expenses"

    elif report_type == "recurring":
        df = get_recurring_charges(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df[["merchant", "count", "avg_amount", "min_amount",
                   "max_amount", "first_date", "last_date", "category"]].copy()
        out.columns = ["Merchant", "Charges", "Avg Amount", "Min Amount",
                        "Max Amount", "First Date", "Last Date", "Category"]
        for col in ["Avg Amount", "Min Amount", "Max Amount"]:
            out[col] = out[col].apply(lambda v: f"{v:.2f}")
        label = "recurring_charges"

    elif report_type == "tax_summary":
        df = get_tax_summary(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df.copy()
        out.columns = ["Category", "Subcategory", "Transactions", "Total"]
        out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")
        label = "tax_summary"

    elif report_type == "accounts":
        df = get_account_summary(entity, start_date, end_date)
        if df.empty:
            return "No data for this date range", 404
        out = df.copy()
        out.columns = ["Account", "Transactions", "Total Spending", "Total Income", "Net"]
        for col in ["Total Spending", "Total Income", "Net"]:
            out[col] = out[col].apply(lambda v: f"{v:.2f}")
        label = "account_summary"

    else:
        return "Unknown report type", 400

    # ── Format dispatch ────────────────────────────────────────────────
    fmt = request.args.get("format", "csv")

    if fmt == "qbo":
        # QBO only works for transactions
        if report_type != "transactions":
            return "QBO format is only available for Transactions reports", 400
        qbo_data = transactions_to_qbo(df, entity, start_date, end_date)
        filename = _csv_filename_range(entity, label, start_date, end_date)
        filename = filename.replace(".csv", ".qbo")
        return Response(
            qbo_data,
            mimetype="application/x-ofx",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    elif fmt == "pdf":
        report_names = {
            "transactions": "Transactions",
            "categories": "Category Summary",
            "merchants": "Merchant Summary",
            "month_over_month": "Month-over-Month Comparison",
            "income_expenses": "Income vs Expenses",
            "recurring": "Recurring Charges",
            "tax_summary": "Tax Summary",
            "accounts": "Account Summary",
        }
        title = report_names.get(report_type, report_type)
        subtitle = f"{entity.title()} \u2014 {start_date} to {end_date}"
        pdf_bytes = dataframe_to_pdf(out, title, subtitle)
        filename = _csv_filename_range(entity, label, start_date, end_date)
        filename = filename.replace(".csv", ".pdf")
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    else:
        # Default: CSV
        csv_data = out.to_csv(index=False)
        filename = _csv_filename_range(entity, label, start_date, end_date)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

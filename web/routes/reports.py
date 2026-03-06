"""Reports route — quick monthly exports + in-page view + report builder."""

from __future__ import annotations

import calendar
import datetime
from collections import OrderedDict

from flask import Blueprint, render_template, request, g, Response, url_for

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


# ── Report type metadata ─────────────────────────────────────────────────────

_REPORT_NAMES = {
    "transactions": "Transactions",
    "categories": "Category Summary",
    "merchants": "Merchant Summary",
    "month_over_month": "Month-over-Month Comparison",
    "income_expenses": "Income vs Expenses",
    "recurring": "Recurring Charges",
    "tax_summary": "Tax Summary",
    "accounts": "Account Summary",
}


# ── Shared report data preparation ──────────────────────────────────────────

def _prepare_report(entity, report_type, start_date, end_date):
    """Run query + prepare display data for a report type.

    Returns (label, df_raw, df_display) or None if no data found.
    - label: string for filenames
    - df_raw: raw DataFrame from query
    - df_display: DataFrame with renamed columns and formatted values
    """
    if report_type == "transactions":
        df = get_transactions_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        out = df[["date", "description_raw", "merchant_canonical",
                   "amount", "category", "subcategory", "account", "notes"]].copy()
        out.columns = ["Date", "Description", "Merchant", "Amount",
                        "Category", "Subcategory", "Account", "Notes"]
        out["Amount"] = out["Amount"].apply(lambda v: f"{v:.2f}")
        return ("transactions", df, out)

    elif report_type == "categories":
        df = get_category_totals_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        out = df[["category", "count", "total_amount"]].copy()
        out.columns = ["Category", "Transactions", "Total"]
        out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")
        return ("category_summary", df, out)

    elif report_type == "merchants":
        df = get_merchant_totals_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        out = df[["merchant", "count", "total_amount"]].copy()
        out.columns = ["Merchant", "Transactions", "Total"]
        out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")
        return ("merchant_summary", df, out)

    elif report_type == "month_over_month":
        df = get_month_over_month(entity, start_date, end_date)
        if df.empty:
            return None
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
        return ("month_over_month", df, out)

    elif report_type == "income_expenses":
        df = get_income_vs_expenses_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        out = df.copy()
        out.columns = ["Month", "Expenses", "Income"]
        out["Net"] = out["Income"].astype(float) - out["Expenses"].astype(float)
        for col in ["Expenses", "Income", "Net"]:
            out[col] = out[col].apply(lambda v: f"{v:.2f}")
        return ("income_vs_expenses", df, out)

    elif report_type == "recurring":
        df = get_recurring_charges(entity, start_date, end_date)
        if df.empty:
            return None
        out = df[["merchant", "count", "avg_amount", "min_amount",
                   "max_amount", "first_date", "last_date", "category"]].copy()
        out.columns = ["Merchant", "Charges", "Avg Amount", "Min Amount",
                        "Max Amount", "First Date", "Last Date", "Category"]
        for col in ["Avg Amount", "Min Amount", "Max Amount"]:
            out[col] = out[col].apply(lambda v: f"{v:.2f}")
        return ("recurring_charges", df, out)

    elif report_type == "tax_summary":
        df = get_tax_summary(entity, start_date, end_date)
        if df.empty:
            return None
        out = df.copy()
        out.columns = ["Category", "Subcategory", "Transactions", "Total"]
        out["Total"] = out["Total"].apply(lambda v: f"{v:.2f}")
        return ("tax_summary", df, out)

    elif report_type == "accounts":
        df = get_account_summary(entity, start_date, end_date)
        if df.empty:
            return None
        out = df.copy()
        out.columns = ["Account", "Transactions", "Total Spending", "Total Income", "Net"]
        for col in ["Total Spending", "Total Income", "Net"]:
            out[col] = out[col].apply(lambda v: f"{v:.2f}")
        return ("account_summary", df, out)

    return None


def _fmt_dollars(cents):
    """Format cents as dollar string: $1,234 (whole dollars)."""
    d = abs(cents) / 100
    s = "${:,.0f}".format(d)
    return ("\u2212" + s) if cents < 0 else s


def _fmt_dollars_decimal(amount):
    """Format float amount as dollar string: $1,234.56."""
    d = abs(amount)
    s = "${:,.2f}".format(d)
    return ("\u2212" + s) if amount < 0 else s


def _report_view_context(entity, report_type, start_date, end_date):
    """Build template context dict for in-page report display.

    Returns dict with all variables the rpt_view.html partial needs,
    or None if no data.
    """
    ctx = {
        "report_type": report_type,
        "report_name": _REPORT_NAMES.get(report_type, report_type),
        "start": start_date,
        "end": end_date,
        "fmt_date": fmt_date,
        "fmt_month_short": fmt_month_short,
        "fmt_dollars": _fmt_dollars_decimal,
    }

    if report_type == "transactions":
        df = get_transactions_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        rows = df.to_dict("records")
        total_count = len(rows)
        total_amount = sum(r["amount"] for r in rows if r["amount"] < 0)
        # Cap display rows
        display_rows = rows[:200]
        ctx.update(
            rows=display_rows,
            total_count=total_count,
            total_amount=total_amount,
            capped=total_count > 200,
        )

    elif report_type == "categories":
        df = get_category_totals_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        rows = df.to_dict("records")
        max_amount = max(r["total_amount"] for r in rows) if rows else 1
        total_txns = sum(r["count"] for r in rows)
        total_amount = sum(r["total_amount"] for r in rows)
        for r in rows:
            r["pct"] = int(r["total_amount"] / max_amount * 100) if max_amount else 0
        ctx.update(
            rows=rows,
            max_amount=max_amount,
            total_txns=int(total_txns),
            total_amount=total_amount,
        )

    elif report_type == "merchants":
        df = get_merchant_totals_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        rows = df.to_dict("records")
        max_amount = max(r["total_amount"] for r in rows) if rows else 1
        total_txns = sum(r["count"] for r in rows)
        total_amount = sum(r["total_amount"] for r in rows)
        for r in rows:
            r["pct"] = int(r["total_amount"] / max_amount * 100) if max_amount else 0
        # Show top 20, rest hidden
        ctx.update(
            rows=rows[:20],
            extra_rows=rows[20:],
            max_amount=max_amount,
            total_txns=int(total_txns),
            total_amount=total_amount,
            total_merchants=len(rows),
        )

    elif report_type == "month_over_month":
        df = get_month_over_month(entity, start_date, end_date)
        if df.empty:
            return None
        pivot = df.pivot_table(
            index="category", columns="month",
            values="total_amount", fill_value=0,
        )
        pivot["Total"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("Total", ascending=False)
        months = [c for c in pivot.columns if c != "Total"]
        # Build rows as list of dicts
        pivot_rows = []
        col_totals = {m: 0.0 for m in months}
        col_totals["Total"] = 0.0
        for cat in pivot.index:
            row = {"category": cat, "months": {}, "total": float(pivot.loc[cat, "Total"])}
            for m in months:
                val = float(pivot.loc[cat, m])
                row["months"][m] = val
                col_totals[m] += val
            col_totals["Total"] += row["total"]
            pivot_rows.append(row)
        ctx.update(
            pivot_rows=pivot_rows,
            months=months,
            col_totals=col_totals,
        )

    elif report_type == "income_expenses":
        df = get_income_vs_expenses_daterange(entity, start_date, end_date)
        if df.empty:
            return None
        rows = []
        total_expenses = 0.0
        total_income = 0.0
        for _, r in df.iterrows():
            exp = float(r["expenses"])
            inc = float(r["income"])
            net = inc - exp
            total_expenses += exp
            total_income += inc
            rows.append({
                "month": r["month"],
                "expenses": exp,
                "income": inc,
                "net": net,
            })
        ctx.update(
            rows=rows,
            total_expenses=total_expenses,
            total_income=total_income,
            total_net=total_income - total_expenses,
        )

    elif report_type == "recurring":
        df = get_recurring_charges(entity, start_date, end_date)
        if df.empty:
            return None
        rows = df.to_dict("records")
        ctx.update(rows=rows)

    elif report_type == "tax_summary":
        df = get_tax_summary(entity, start_date, end_date)
        if df.empty:
            return None
        # Group by category
        groups = OrderedDict()
        grand_total_txns = 0
        grand_total_amount = 0.0
        for _, r in df.iterrows():
            cat = r["category"]
            if cat not in groups:
                groups[cat] = {"subcategories": [], "total_count": 0, "total_amount": 0.0}
            groups[cat]["subcategories"].append({
                "name": r["subcategory"],
                "count": int(r["count"]),
                "total": float(r["total_amount"]),
            })
            groups[cat]["total_count"] += int(r["count"])
            groups[cat]["total_amount"] += float(r["total_amount"])
            grand_total_txns += int(r["count"])
            grand_total_amount += float(r["total_amount"])
        ctx.update(
            groups=groups,
            grand_total_txns=grand_total_txns,
            grand_total_amount=grand_total_amount,
        )

    elif report_type == "accounts":
        df = get_account_summary(entity, start_date, end_date)
        if df.empty:
            return None
        rows = df.to_dict("records")
        total_spending = sum(float(r["total_spending"]) for r in rows)
        total_income = sum(float(r["total_income"]) for r in rows)
        total_net = sum(float(r["net"]) for r in rows)
        ctx.update(
            rows=rows,
            total_spending=total_spending,
            total_income=total_income,
            total_net=total_net,
        )

    else:
        return None

    return ctx


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


# ── In-page view (HTMX partial) ────────────────────────────────────────────

@bp.route("/view")
def view():
    """HTMX partial — render report results inline on the page."""
    report_type = request.args.get("report_type", "transactions")
    start_date = request.args.get("start", "")
    end_date = request.args.get("end", "")

    if not start_date or not end_date:
        return '<div class="rpt-empty">Please select a date range.</div>'

    ctx = _report_view_context(g.entity_key, report_type, start_date, end_date)
    if ctx is None:
        return '<div class="rpt-empty">No data found for this date range.</div>'

    return render_template("components/rpt_view.html", **ctx)


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

    result = _prepare_report(entity, report_type, start_date, end_date)
    if result is None:
        return "No data for this date range", 404

    label, df, out = result

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
        title = _REPORT_NAMES.get(report_type, report_type)
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

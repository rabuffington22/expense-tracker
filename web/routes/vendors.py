"""Vendors route — upload Amazon CSV / Henry Schein XLSX."""

from datetime import date as _date

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, g

from core.amazon import parse_amazon_csv, group_orders, save_orders_to_db, get_order_counts
from core.henryschein import parse_henryschein_xlsx

bp = Blueprint("vendors", __name__, url_prefix="/vendors")


@bp.route("/")
def index():
    total_orders, unmatched_orders = get_order_counts(g.entity_key)
    matched = total_orders - unmatched_orders
    return render_template(
        "vendors.html",
        total_orders=total_orders,
        matched_orders=matched,
        unmatched_orders=unmatched_orders,
    )


@bp.route("/parse", methods=["POST"])
def parse():
    """Parse uploaded file and show preview."""
    vendor = request.form.get("vendor", "Amazon")
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("vendors.index"))

    orders = []
    warnings = []

    try:
        if vendor == "Amazon":
            df, warnings = parse_amazon_csv(file)
            if not df.empty:
                orders = group_orders(df)
        else:
            orders, warnings = parse_henryschein_xlsx(file)
    except Exception as e:
        flash(f"Parse error: {e}", "danger")
        return redirect(url_for("vendors.index"))

    if not orders:
        flash("Could not parse any orders from the file.", "danger")
        return redirect(url_for("vendors.index"))

    # Compute stats
    dates = [o["order_date"] for o in orders if o.get("order_date")]
    min_d = min(dates) if dates else "?"
    max_d = max(dates) if dates else "?"
    total_spent = sum(o["order_total"] for o in orders)

    # Store orders in session for save step
    from flask import session
    session["parsed_orders"] = orders
    session["parsed_vendor"] = vendor.lower().replace(" ", "")

    total_orders, unmatched_orders = get_order_counts(g.entity_key)
    matched = total_orders - unmatched_orders

    return render_template(
        "vendors.html",
        orders=orders,
        vendor=vendor,
        order_count=len(orders),
        min_date=min_d,
        max_date=max_d,
        total_spent=total_spent,
        warnings=warnings,
        total_orders=total_orders,
        matched_orders=matched,
        unmatched_orders=unmatched_orders,
        show_preview=True,
    )


@bp.route("/save", methods=["POST"])
def save():
    """Save parsed orders to the database."""
    from flask import session
    orders = session.pop("parsed_orders", [])
    vendor = session.pop("parsed_vendor", "amazon")

    if not orders:
        flash("No parsed orders to save. Upload a file first.", "warning")
        return redirect(url_for("vendors.index"))

    # Apply date filter if provided
    filter_from = request.form.get("filter_from")
    filter_to = request.form.get("filter_to")
    if filter_from and filter_to:
        filtered = []
        for o in orders:
            try:
                od = pd.to_datetime(o["order_date"]).date()
                if _date.fromisoformat(filter_from) <= od <= _date.fromisoformat(filter_to):
                    filtered.append(o)
            except (ValueError, TypeError):
                filtered.append(o)
        orders = filtered

    inserted, skipped = save_orders_to_db(g.entity_key, orders, vendor=vendor)
    msg = f"Saved {inserted} orders."
    if skipped:
        msg += f" Skipped {skipped} duplicates."
    flash(msg, "success")
    return redirect(url_for("vendors.index"))

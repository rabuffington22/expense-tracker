"""Vendors route — upload Amazon CSV / Henry Schein XLSX."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date as _date

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, session

from core.amazon import parse_amazon_csv, group_orders, save_orders_to_db, get_order_counts
from core.henryschein import parse_henryschein_xlsx

bp = Blueprint("vendors", __name__, url_prefix="/vendors")

# Temp directory for storing parsed data between parse and save steps
_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-uploads")
os.makedirs(_TEMP_DIR, exist_ok=True)


def _sanitize_temp_key(key: str) -> str | None:
    """Sanitize a temp key to prevent path traversal."""
    if not key:
        return None
    # Strip any path components — only allow the basename
    key = os.path.basename(key)
    if not key or ".." in key or "/" in key or "\\" in key:
        return None
    return key


def _save_temp(key, data):
    """Save data to a temp file, return the filename."""
    path = os.path.join(_TEMP_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return key


def _load_temp(key):
    """Load data from a temp file and delete it."""
    key = _sanitize_temp_key(key)
    if not key:
        return None
    path = os.path.join(_TEMP_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    os.remove(path)
    return data


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

    # Store orders in temp file (too large for cookie session)
    import uuid
    temp_key = f"vendors_{uuid.uuid4().hex[:12]}"
    _save_temp(temp_key, {"orders": orders, "vendor": vendor.lower().replace(" ", "")})
    session["vendor_temp_key"] = temp_key

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
        temp_key=temp_key,
    )


@bp.route("/save", methods=["POST"])
def save():
    """Save parsed orders to the database."""
    temp_key = request.form.get("temp_key") or session.pop("vendor_temp_key", None)
    if not temp_key:
        flash("No parsed orders to save. Upload a file first.", "warning")
        return redirect(url_for("vendors.index"))

    data = _load_temp(temp_key)
    if not data:
        flash("Parsed data expired. Please upload the file again.", "warning")
        return redirect(url_for("vendors.index"))

    orders = data["orders"]
    vendor = data["vendor"]

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

"""Data Sources route — upload vendor orders + connect payment accounts."""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import date as _date, datetime, timezone

log = logging.getLogger(__name__)

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, session, jsonify

from core.amazon import parse_amazon_csv, group_orders, save_orders_to_db, get_order_counts
from core.henryschein import parse_henryschein_xlsx
from core.db import get_connection

bp = Blueprint("data_sources", __name__, url_prefix="/data-sources")

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


# ── Vendor order routes (Amazon / Henry Schein) ──────────────────────────────

@bp.route("/")
def index():
    total_orders, unmatched_orders = get_order_counts(g.entity_key)
    matched = total_orders - unmatched_orders

    # Load connected vendor payment accounts
    vendor_accounts = _get_vendor_accounts(g.entity_key)

    return render_template(
        "data_sources.html",
        total_orders=total_orders,
        matched_orders=matched,
        unmatched_orders=unmatched_orders,
        vendor_accounts=vendor_accounts,
    )


@bp.route("/parse", methods=["POST"])
def parse():
    """Parse uploaded file and show preview."""
    vendor = request.form.get("vendor", "Amazon")
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("data_sources.index"))

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
        return redirect(url_for("data_sources.index"))

    if not orders:
        flash("Could not parse any orders from the file.", "danger")
        return redirect(url_for("data_sources.index"))

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
    vendor_accounts = _get_vendor_accounts(g.entity_key)

    return render_template(
        "data_sources.html",
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
        vendor_accounts=vendor_accounts,
        show_preview=True,
        temp_key=temp_key,
    )


@bp.route("/save", methods=["POST"])
def save():
    """Save parsed orders to the database."""
    temp_key = request.form.get("temp_key") or session.pop("vendor_temp_key", None)
    if not temp_key:
        flash("No parsed orders to save. Upload a file first.", "warning")
        return redirect(url_for("data_sources.index"))

    data = _load_temp(temp_key)
    if not data:
        flash("Parsed data expired. Please upload the file again.", "warning")
        return redirect(url_for("data_sources.index"))

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
    return redirect(url_for("data_sources.index"))


# ── Payment account helpers ──────────────────────────────────────────────────

def _get_vendor_accounts(entity_key: str) -> list[dict]:
    """Load vendor Plaid items (is_vendor=1) with stats."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT item_id, institution_name, cursor, created_at "
            "FROM plaid_items WHERE is_vendor = 1 ORDER BY created_at"
        ).fetchall()
        accounts = []
        for r in rows:
            item_id = r[0]
            # Count vendor transactions for this item
            vt_row = conn.execute(
                "SELECT COUNT(*), "
                "SUM(CASE WHEN matched_transaction_id IS NOT NULL THEN 1 ELSE 0 END) "
                "FROM vendor_transactions WHERE plaid_item_id = ?",
                (item_id,),
            ).fetchone()
            total_vt = vt_row[0] if vt_row else 0
            matched_vt = vt_row[1] if vt_row else 0
            accounts.append({
                "item_id": item_id,
                "institution_name": r[1] or "Unknown",
                "last_synced": r[2],  # cursor doubles as last-sync indicator
                "created_at": r[3],
                "total_transactions": total_vt,
                "matched_transactions": matched_vt,
                "unmatched_transactions": total_vt - matched_vt,
            })
        return accounts
    except Exception:
        return []
    finally:
        conn.close()


# ── Payment account Plaid endpoints ──────────────────────────────────────────

@bp.route("/link-token", methods=["POST"])
def link_token():
    """Create a Plaid Link token for connecting a vendor payment account."""
    try:
        from core.plaid_client import create_link_token
        token = create_link_token(user_id=f"vendor-{g.entity_key}")
        return jsonify({"link_token": token})
    except Exception:
        log.exception("Vendor link_token error")
        return jsonify({"error": "Failed to create link token"}), 500


@bp.route("/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange public token from Plaid Link → save as vendor item."""
    public_token = request.form.get("public_token")
    institution_name = request.form.get("institution_name", "")
    institution_id = request.form.get("institution_id", "")

    if not public_token:
        return jsonify({"error": "Missing public_token"}), 400

    try:
        from core.plaid_client import exchange_public_token
        result = exchange_public_token(public_token)
        access_token = result["access_token"]
        item_id = result["item_id"]
    except Exception:
        log.exception("Vendor exchange_token error")
        return jsonify({"error": "Failed to connect account"}), 500

    # Save as vendor Plaid item (is_vendor=1)
    from core.crypto import encrypt_token
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO plaid_items "
            "(item_id, access_token, institution_name, institution_id, is_vendor, created_at) "
            "VALUES (?, ?, ?, ?, 1, ?)",
            (item_id, encrypt_token(access_token), institution_name, institution_id,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    flash(f"Connected {institution_name or 'payment account'}.", "success")
    return jsonify({"ok": True, "item_id": item_id})


@bp.route("/sync-vendor/<item_id>", methods=["POST"])
def sync_vendor(item_id):
    """Sync transactions from a vendor payment account into vendor_transactions."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT access_token, institution_name, cursor "
            "FROM plaid_items WHERE item_id = ? AND is_vendor = 1",
            (item_id,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        flash("Vendor account not found.", "danger")
        return redirect(url_for("data_sources.index"))

    from core.crypto import decrypt_token
    access_token, institution_name, cursor = decrypt_token(row[0]), row[1], row[2]

    # Determine vendor type from institution name
    inst_lower = (institution_name or "").lower()
    if "venmo" in inst_lower:
        vendor_type = "venmo"
    elif "paypal" in inst_lower:
        vendor_type = "paypal"
    else:
        vendor_type = inst_lower.split()[0] if inst_lower else "other"

    try:
        from core.plaid_client import get_transactions
        result = get_transactions(access_token, cursor=cursor)
    except Exception as e:
        flash(f"Sync error: {e}", "danger")
        return redirect(url_for("data_sources.index"))

    added = result.get("added", [])
    modified = result.get("modified", [])
    removed = result.get("removed", [])
    next_cursor = result.get("next_cursor", cursor)

    conn = get_connection(g.entity_key)
    inserted = 0
    try:
        # Remove any removed transactions (returned as list of transaction_id strings)
        for txn_id in removed:
            if txn_id:
                conn.execute(
                    "DELETE FROM vendor_transactions WHERE plaid_transaction_id = ?",
                    (txn_id,),
                )

        # Upsert added + modified
        for txn in added + modified:
            if _upsert_vendor_transaction(conn, txn, item_id, vendor_type):
                inserted += 1

        # Update cursor
        conn.execute(
            "UPDATE plaid_items SET cursor = ? WHERE item_id = ?",
            (next_cursor, item_id),
        )
        conn.commit()
    finally:
        conn.close()

    msg = f"Synced {institution_name}: {inserted} new transactions."
    if removed:
        msg += f" {len(removed)} removed."
    flash(msg, "success")
    return redirect(url_for("data_sources.index"))


@bp.route("/disconnect-vendor/<item_id>", methods=["POST"])
def disconnect_vendor(item_id):
    """Disconnect a vendor payment account and remove its transactions."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT institution_name FROM plaid_items WHERE item_id = ? AND is_vendor = 1",
            (item_id,),
        ).fetchone()
        if not row:
            flash("Vendor account not found.", "danger")
            return redirect(url_for("data_sources.index"))

        institution_name = row[0]

        # Remove vendor transactions
        conn.execute(
            "DELETE FROM vendor_transactions WHERE plaid_item_id = ?",
            (item_id,),
        )
        # Remove Plaid item
        conn.execute("DELETE FROM plaid_items WHERE item_id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()

    flash(f"Disconnected {institution_name}.", "success")
    return redirect(url_for("data_sources.index"))


def _upsert_vendor_transaction(conn, txn: dict, item_id: str, vendor_type: str) -> bool:
    """Insert a Plaid transaction into vendor_transactions. Returns True if inserted."""
    txn_id = txn.get("plaid_transaction_id")
    account_id = txn.get("account_id")
    date = str(txn.get("date", ""))
    amount = float(txn.get("amount", 0))
    name = txn.get("name", "")
    merchant_name = txn.get("merchant_name")

    if not txn_id or not date:
        return False

    # Skip income (negative amounts in Plaid = credits/income)
    if amount < 0:
        return False

    amount_cents = round(amount * 100)

    # Recipient is the Plaid name field (who got paid)
    recipient = name

    try:
        cur = conn.execute(
            "INSERT OR IGNORE INTO vendor_transactions "
            "(plaid_item_id, plaid_transaction_id, plaid_account_id, date, amount, "
            "amount_cents, name, merchant_name, recipient, vendor_type, imported_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (item_id, txn_id, account_id, date, amount, amount_cents,
             name, merchant_name, recipient, vendor_type,
             datetime.now(timezone.utc).isoformat()),
        )
        return cur.rowcount > 0
    except Exception:
        return False


# ── Legacy redirect ──────────────────────────────────────────────────────────

@bp.route("/vendors-redirect")
def _vendors_redirect():
    """Redirect old /vendors URL to /data-sources for bookmarks."""
    return redirect(url_for("data_sources.index"), code=301)

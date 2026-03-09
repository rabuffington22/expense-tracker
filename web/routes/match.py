"""Match route — link bank transactions to vendor orders."""

import json
import os
import tempfile
import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, session, flash, redirect, url_for, g

from core.amazon import (
    find_amazon_transactions,
    load_orders_from_db,
    match_orders_to_transactions,
    apply_matches,
    get_order_counts,
)

bp = Blueprint("match", __name__, url_prefix="/match")

# Temp directory for match review data (too large for cookie session)
_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-uploads")
os.makedirs(_TEMP_DIR, exist_ok=True)


def _save_match_data(review_data, no_match_data, source="orders"):
    """Save match data to temp file, store key in session."""
    temp_key = f"match_{uuid.uuid4().hex[:12]}"
    path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
    with open(path, "w") as f:
        json.dump({"review": review_data, "no_match": no_match_data, "source": source}, f)
    session["match_temp_key"] = temp_key
    session["match_review_idx"] = 0
    session["match_accepted"] = 0
    session["match_skipped"] = 0


def _load_match_data():
    """Load match data from temp file."""
    temp_key = session.get("match_temp_key")
    if not temp_key:
        return [], [], "orders"
    path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
    if not os.path.exists(path):
        return [], [], "orders"
    with open(path) as f:
        data = json.load(f)
    return data.get("review", []), data.get("no_match", []), data.get("source", "orders")


def _clear_match_data():
    """Remove temp file and session keys. Returns (accepted, skipped) counts."""
    temp_key = session.pop("match_temp_key", None)
    session.pop("match_review_idx", None)
    accepted = session.pop("match_accepted", 0)
    skipped = session.pop("match_skipped", 0)
    if temp_key:
        path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
        if os.path.exists(path):
            os.remove(path)
    return accepted, skipped


@bp.route("/")
def index():
    source = request.args.get("source", "orders")

    total_orders, unmatched_orders = get_order_counts(g.entity_key)
    matched_orders = total_orders - unmatched_orders

    # Vendor payment stats
    from core.vendor_matching import get_vendor_match_stats
    vendor_stats = get_vendor_match_stats(g.entity_key)

    if source == "vendor":
        # Vendor payment matching view
        review, no_match, data_source = _load_match_data()
        review_idx = session.get("match_review_idx", 0)
        current_match = None
        if review and review_idx < len(review) and data_source == "vendor":
            current_match = review[review_idx]
        elif data_source != "vendor":
            review = []
            current_match = None

        return render_template(
            "match.html",
            source=source,
            total_orders=total_orders,
            matched_orders=matched_orders,
            unmatched_orders=unmatched_orders,
            vendor_stats=vendor_stats,
            review=review if data_source == "vendor" else [],
            review_idx=review_idx if data_source == "vendor" else 0,
            current_match=current_match,
            no_match=no_match if data_source == "vendor" else [],
        )
    else:
        # Amazon / Henry Schein matching view (original)
        amazon_txns = find_amazon_transactions(g.entity_key)
        amazon_txn_count = len(amazon_txns) if not amazon_txns.empty else 0

        review, no_match, data_source = _load_match_data()
        review_idx = session.get("match_review_idx", 0)
        current_match = None
        if review and review_idx < len(review) and data_source == "orders":
            current_match = review[review_idx]
        elif data_source != "orders":
            review = []
            current_match = None

        return render_template(
            "match.html",
            source=source,
            total_orders=total_orders,
            matched_orders=matched_orders,
            unmatched_orders=unmatched_orders,
            amazon_txn_count=amazon_txn_count,
            vendor_stats=vendor_stats,
            review=review if data_source == "orders" else [],
            review_idx=review_idx if data_source == "orders" else 0,
            current_match=current_match,
            no_match=no_match if data_source == "orders" else [],
        )


@bp.route("/run", methods=["POST"])
def run_matching():
    """Run matching algorithm."""
    source = request.form.get("source", "orders")

    if source == "vendor":
        return _run_vendor_matching()
    else:
        return _run_order_matching()


def _run_order_matching():
    """Run Amazon/HS order matching."""
    amazon_txns = find_amazon_transactions(g.entity_key)
    if amazon_txns.empty:
        flash("No Amazon transactions found in bank data.", "warning")
        return redirect(url_for("match.index"))

    db_orders = load_orders_from_db(g.entity_key, unmatched_only=True)
    if not db_orders:
        flash("No unmatched orders to process.", "info")
        return redirect(url_for("match.index"))

    matches = match_orders_to_transactions(db_orders, amazon_txns)

    # Auto-apply exact matches
    exact = [m for m in matches if m["match_type"] == "exact"]
    auto_count = 0
    if exact:
        auto_apply = []
        for m in exact:
            auto_apply.append({
                "transaction_id": m["transaction_id"],
                "product_summary": m["product_summary"],
                "suggested_category": m["suggested_category"],
                "suggested_subcategory": m.get("suggested_subcategory", "Unknown"),
                "order_id": m["order_id"],
                "order_total": m["matched_order"]["order_total"],
                "confidence": m["confidence"],
            })
        auto_count = apply_matches(g.entity_key, auto_apply)

    # Build review queue
    review = [m for m in matches if m["match_type"] not in ("exact", "skip", "none")]
    no_match = [m for m in matches if m["match_type"] == "none"]

    # Convert to serializable dicts
    review_data = []
    for m in review:
        order_date = m.get("matched_order", {}).get("order_date", "")
        txn_date = m["txn_date"]
        date_gap = None
        try:
            td = datetime.strptime(txn_date, "%Y-%m-%d")
            od = datetime.strptime(order_date, "%Y-%m-%d")
            date_gap = (td - od).days
        except (ValueError, TypeError):
            pass

        review_data.append({
            "transaction_id": m["transaction_id"],
            "txn_date": txn_date,
            "txn_amount": m["txn_amount"],
            "txn_description": m["txn_description"],
            "product_summary": m["product_summary"],
            "order_id": m["order_id"],
            "suggested_category": m.get("suggested_category", ""),
            "suggested_subcategory": m.get("suggested_subcategory", "Unknown"),
            "confidence": m["confidence"],
            "order_date": order_date,
            "order_total": m.get("matched_order", {}).get("order_total", 0),
            "date_gap": date_gap,
        })

    no_match_data = []
    for m in no_match:
        no_match_data.append({
            "txn_date": m["txn_date"],
            "txn_description": m["txn_description"],
            "txn_amount": m["txn_amount"],
        })

    _save_match_data(review_data, no_match_data, source="orders")

    msg = f"Auto-applied {auto_count} exact matches." if auto_count else "No exact matches found."
    if review_data:
        msg += f" {len(review_data)} matches need review."
    flash(msg, "success")
    return redirect(url_for("match.index"))


def _run_vendor_matching():
    """Run Venmo/PayPal vendor matching."""
    from core.vendor_matching import match_vendor_to_bank

    result = match_vendor_to_bank(g.entity_key)

    auto_count = result["auto_applied"]
    review_matches = result["review"]

    # Convert review matches to match_card format
    review_data = []
    for m in review_matches:
        date_gap = m.get("date_diff", 0)
        review_data.append({
            "transaction_id": m["bank_txn_id"],
            "txn_date": m["bank_date"],
            "txn_amount": m["bank_amount"],
            "txn_description": m["bank_description"],
            "product_summary": m["recipient"],
            "order_id": str(m["vendor_id"]),
            "suggested_category": "",
            "suggested_subcategory": "",
            "confidence": m["confidence"],
            "order_date": m["vendor_date"],
            "order_total": m["vendor_amount"],
            "date_gap": date_gap,
            # Extra vendor-specific fields
            "vendor_id": m["vendor_id"],
            "recipient": m["recipient"],
            "vendor_type": m["vendor_type"],
            "is_vendor_match": True,
        })

    _save_match_data(review_data, [], source="vendor")

    msg = f"Auto-applied {auto_count} exact matches." if auto_count else "No exact matches found."
    if review_data:
        msg += f" {len(review_data)} matches need review."
    flash(msg, "success")
    return redirect(url_for("match.index", source="vendor"))


@bp.route("/accept", methods=["POST"])
def accept():
    """Accept a match and advance to next."""
    review, _, data_source = _load_match_data()
    idx = session.get("match_review_idx", 0)

    if review and idx < len(review):
        m = review[idx]

        if data_source == "vendor" and m.get("is_vendor_match"):
            # Apply vendor match
            from core.vendor_matching import apply_vendor_matches
            apply_vendor_matches(g.entity_key, [{
                "vendor_id": m["vendor_id"],
                "bank_txn_id": m["transaction_id"],
                "recipient": m.get("recipient", ""),
                "vendor_type": m.get("vendor_type", "venmo"),
                "confidence": m["confidence"],
            }])
        else:
            # Apply order match
            apply_matches(g.entity_key, [{
                "transaction_id": m["transaction_id"],
                "product_summary": m["product_summary"],
                "suggested_category": m["suggested_category"],
                "suggested_subcategory": m.get("suggested_subcategory", "Unknown"),
                "order_id": m["order_id"],
                "order_total": m.get("order_total", 0),
                "confidence": m["confidence"],
            }])

        session["match_review_idx"] = idx + 1
        session["match_accepted"] = session.get("match_accepted", 0) + 1

    if request.headers.get("HX-Request"):
        return _render_match_card()

    return redirect(url_for("match.index"))


@bp.route("/skip-match", methods=["POST"])
def skip_match():
    """Skip a match and advance to next."""
    idx = session.get("match_review_idx", 0)
    session["match_review_idx"] = idx + 1
    session["match_skipped"] = session.get("match_skipped", 0) + 1

    if request.headers.get("HX-Request"):
        return _render_match_card()

    return redirect(url_for("match.index"))


@bp.route("/finish", methods=["POST"])
def finish():
    """Clear review queue and show summary."""
    review, no_match, _ = _load_match_data()
    accepted, skipped = _clear_match_data()
    parts = []
    if accepted:
        parts.append(f"Accepted {accepted}")
    if skipped:
        parts.append(f"Skipped {skipped}")
    if no_match:
        parts.append(f"{len(no_match)} unmatched")
    if parts:
        flash("Review complete: " + ", ".join(parts) + ".", "success")
    return redirect(url_for("match.index"))


def _render_match_card():
    """Return the match card partial for HTMX."""
    review, no_match, data_source = _load_match_data()
    idx = session.get("match_review_idx", 0)

    current_match = None
    if review and idx < len(review):
        current_match = review[idx]

    return render_template(
        "components/match_card.html",
        review=review,
        review_idx=idx,
        current_match=current_match,
        no_match=no_match,
        source=data_source,
    )

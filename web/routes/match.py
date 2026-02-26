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


def _save_match_data(review_data, no_match_data):
    """Save match data to temp file, store key in session."""
    temp_key = f"match_{uuid.uuid4().hex[:12]}"
    path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
    with open(path, "w") as f:
        json.dump({"review": review_data, "no_match": no_match_data}, f)
    session["match_temp_key"] = temp_key
    session["match_review_idx"] = 0


def _load_match_data():
    """Load match data from temp file."""
    temp_key = session.get("match_temp_key")
    if not temp_key:
        return [], []
    path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
    if not os.path.exists(path):
        return [], []
    with open(path) as f:
        data = json.load(f)
    return data.get("review", []), data.get("no_match", [])


def _clear_match_data():
    """Remove temp file and session keys."""
    temp_key = session.pop("match_temp_key", None)
    session.pop("match_review_idx", None)
    if temp_key:
        path = os.path.join(_TEMP_DIR, f"{temp_key}.json")
        if os.path.exists(path):
            os.remove(path)


@bp.route("/")
def index():
    total_orders, unmatched_orders = get_order_counts(g.entity_key)
    matched_orders = total_orders - unmatched_orders

    amazon_txns = find_amazon_transactions(g.entity_key)
    amazon_txn_count = len(amazon_txns) if not amazon_txns.empty else 0

    review, no_match = _load_match_data()
    review_idx = session.get("match_review_idx", 0)

    # Current review item
    current_match = None
    if review and review_idx < len(review):
        current_match = review[review_idx]

    return render_template(
        "match.html",
        total_orders=total_orders,
        matched_orders=matched_orders,
        unmatched_orders=unmatched_orders,
        amazon_txn_count=amazon_txn_count,
        review=review,
        review_idx=review_idx,
        current_match=current_match,
        no_match=no_match,
    )


@bp.route("/run", methods=["POST"])
def run_matching():
    """Run matching algorithm."""
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
        review_data.append({
            "transaction_id": m["transaction_id"],
            "txn_date": m["txn_date"],
            "txn_amount": m["txn_amount"],
            "txn_description": m["txn_description"],
            "product_summary": m["product_summary"],
            "order_id": m["order_id"],
            "suggested_category": m.get("suggested_category", ""),
            "suggested_subcategory": m.get("suggested_subcategory", "Unknown"),
            "confidence": m["confidence"],
            "order_date": m.get("matched_order", {}).get("order_date", ""),
            "order_total": m.get("matched_order", {}).get("order_total", 0),
        })

    no_match_data = []
    for m in no_match:
        no_match_data.append({
            "txn_date": m["txn_date"],
            "txn_description": m["txn_description"],
            "txn_amount": m["txn_amount"],
        })

    _save_match_data(review_data, no_match_data)

    msg = f"Auto-applied {auto_count} exact matches." if auto_count else "No exact matches found."
    if review_data:
        msg += f" {len(review_data)} matches need review."
    flash(msg, "success")
    return redirect(url_for("match.index"))


@bp.route("/accept", methods=["POST"])
def accept():
    """Accept a match and advance to next."""
    review, _ = _load_match_data()
    idx = session.get("match_review_idx", 0)

    if review and idx < len(review):
        m = review[idx]
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

    if request.headers.get("HX-Request"):
        return _render_match_card()

    return redirect(url_for("match.index"))


@bp.route("/skip-match", methods=["POST"])
def skip_match():
    """Skip a match and advance to next."""
    idx = session.get("match_review_idx", 0)
    session["match_review_idx"] = idx + 1

    if request.headers.get("HX-Request"):
        return _render_match_card()

    return redirect(url_for("match.index"))


@bp.route("/finish", methods=["POST"])
def finish():
    """Clear review queue."""
    _clear_match_data()
    return redirect(url_for("match.index"))


def _render_match_card():
    """Return the match card partial for HTMX."""
    review, no_match = _load_match_data()
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
    )

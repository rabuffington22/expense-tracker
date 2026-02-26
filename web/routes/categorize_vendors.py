"""Categorize Vendors route — HTMX card queue for labeling vendor orders."""

from datetime import datetime, timezone

from flask import Blueprint, render_template, request, g

from core.db import get_connection
from core.amazon import get_uncategorized_orders, get_order_counts, categorize_order, infer_category
from web import get_categories, get_subcategories

bp = Blueprint("categorize_vendors", __name__, url_prefix="/categorize-vendors")


def _build_card_context(entity_key):
    """Build context for the current card (or done state)."""
    uncategorized = get_uncategorized_orders(entity_key)
    total_orders, _ = get_order_counts(entity_key)

    if not uncategorized and total_orders > 0:
        return {"done": True, "message": "All orders are categorized! Head to the Match page to link them to bank charges."}
    elif not uncategorized:
        return {"empty": True, "message": "Upload vendor orders on the Vendors page to get started."}

    # Always show the first uncategorized order (since we just categorized/skipped the previous one)
    order = uncategorized[0]
    categories = get_categories(entity_key)
    if "Shopping" not in categories:
        categories = categories + ["Shopping"]

    inferred_cat, inferred_sub = infer_category(
        order.get("product_summary", ""),
        order.get("amazon_category", ""),
    )

    subs = get_subcategories(entity_key, inferred_cat)

    return {
        "order": order,
        "total": len(uncategorized),
        "idx": 1,
        "categories": categories,
        "subcategories": subs,
        "inferred_cat": inferred_cat,
        "inferred_sub": inferred_sub,
    }


@bp.route("/")
def index():
    ctx = _build_card_context(g.entity_key)
    return render_template("categorize_vendors.html", **ctx)


@bp.route("/save", methods=["POST"])
def save():
    """Save category for current order and return next card via HTMX."""
    order_id = request.form.get("order_id", type=int)
    category = request.form.get("category", "")
    subcategory = request.form.get("subcategory", "Unknown")
    custom_sub = request.form.get("custom_sub", "").strip()
    final_sub = custom_sub if custom_sub else subcategory

    if order_id and category:
        # Save custom subcategory to DB
        if final_sub and final_sub != "Unknown":
            conn = get_connection(g.entity_key)
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) "
                    "VALUES (?,?,?)",
                    (category, final_sub, datetime.now(timezone.utc).isoformat()),
                )
                conn.commit()
            finally:
                conn.close()

        categorize_order(g.entity_key, order_id, category, final_sub)

    ctx = _build_card_context(g.entity_key)

    # If HTMX request, return just the card partial
    if request.headers.get("HX-Request"):
        return render_template("components/vendor_card.html", **ctx)

    return render_template("categorize_vendors.html", **ctx)


@bp.route("/skip", methods=["POST"])
def skip():
    """Skip current order — mark with 'Skipped' category and move on."""
    order_id = request.form.get("order_id", type=int)
    if order_id:
        categorize_order(g.entity_key, order_id, "Skipped", "")

    ctx = _build_card_context(g.entity_key)

    if request.headers.get("HX-Request"):
        return render_template("components/vendor_card.html", **ctx)

    return render_template("categorize_vendors.html", **ctx)


@bp.route("/subcategories")
def subcategories():
    """HTMX endpoint: return subcategory <option> tags for a given category."""
    category = request.args.get("category", "")
    subs = get_subcategories(g.entity_key, category) if category else ["Unknown"]
    options = "".join(f'<option value="{s}">{s}</option>' for s in subs)
    return options

"""Subscription Tracker — tag recurring charges to consider cancelling."""

from flask import Blueprint, g, redirect, render_template, request, url_for

from core.db import get_connection

bp = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_watchlist(conn) -> list[dict]:
    """Fetch subscription watchlist items.

    Sorted: cancelling first, then watching, then by created_at desc.
    Excludes cancelled items.
    """
    try:
        rows = conn.execute(
            "SELECT id, merchant, amount_cents, frequency, status, notes, "
            "       created_at, updated_at "
            "FROM subscription_watchlist "
            "WHERE status != 'cancelled' "
            "ORDER BY CASE status "
            "  WHEN 'cancelling' THEN 0 "
            "  WHEN 'watching' THEN 1 "
            "  ELSE 2 END, "
            "created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []  # Table may not exist yet pre-migration


def get_watchlist_count(conn) -> int:
    """Return the count of active watchlist items (watching + cancelling)."""
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM subscription_watchlist "
            "WHERE status IN ('watching', 'cancelling')"
        ).fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    """Render the subscription tracker page."""
    conn = get_connection(g.entity_key)
    try:
        watchlist = _get_watchlist(conn)
        return render_template("subscriptions.html", watchlist=watchlist)
    finally:
        conn.close()


@bp.route("/add", methods=["POST"])
def add():
    """Add a subscription to the watchlist."""
    merchant = (request.form.get("merchant") or "").strip()
    if not merchant:
        return redirect(url_for("subscriptions.index"))

    amount_str = (request.form.get("amount") or "").strip()
    amount_cents = None
    if amount_str:
        try:
            amount_cents = int(round(float(amount_str.replace(",", "")) * 100))
        except (ValueError, TypeError):
            pass

    frequency = request.form.get("frequency", "monthly")
    if frequency not in ("monthly", "quarterly", "annual"):
        frequency = "monthly"

    notes = (request.form.get("notes") or "").strip() or None

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO subscription_watchlist "
            "(merchant, amount_cents, frequency, notes) "
            "VALUES (?, ?, ?, ?)",
            (merchant, amount_cents, frequency, notes),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("subscriptions.index"))


@bp.route("/update/<int:sub_id>", methods=["POST"])
def update(sub_id):
    """Update subscription status and/or notes."""
    status = request.form.get("status", "")
    notes = request.form.get("notes")

    conn = get_connection(g.entity_key)
    try:
        if status and status in ("watching", "cancelling", "cancelled"):
            conn.execute(
                "UPDATE subscription_watchlist "
                "SET status=?, updated_at=datetime('now') WHERE id=?",
                (status, sub_id),
            )
        if notes is not None:
            conn.execute(
                "UPDATE subscription_watchlist "
                "SET notes=?, updated_at=datetime('now') WHERE id=?",
                (notes.strip() or None, sub_id),
            )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("subscriptions.index"))


@bp.route("/delete/<int:sub_id>", methods=["POST"])
def delete(sub_id):
    """Remove a subscription from the watchlist."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "DELETE FROM subscription_watchlist WHERE id=?",
            (sub_id,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("subscriptions.index"))

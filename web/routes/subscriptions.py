"""Subscription Tracker — tag recurring charges to consider cancelling."""

import statistics
from datetime import datetime, timedelta

from flask import Blueprint, g, redirect, render_template, request, url_for

from core.db import get_connection

bp = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")


# ── Cadence detection ─────────────────────────────────────────────────────────

_CADENCES = {
    "Weekly": (5, 9),
    "Biweekly": (12, 18),
    "Monthly": (25, 35),
    "Quarterly": (80, 100),
    "Annual": (340, 390),
}

_CADENCE_TO_FREQUENCY = {
    "Weekly": "weekly",
    "Biweekly": "biweekly",
    "Monthly": "monthly",
    "Quarterly": "quarterly",
    "Annual": "annual",
}


def _classify_cadence(median_interval_days):
    for name, (lo, hi) in _CADENCES.items():
        if lo <= median_interval_days <= hi:
            return name
    return None


def _amount_is_regular(amounts):
    """Check if amounts are regular enough to be recurring."""
    if len(amounts) < 2:
        return False
    abs_amounts = [abs(a) for a in amounts]
    median = statistics.median(abs_amounts)
    threshold = max(300, int(median * 0.05))  # $3 or 5%
    recent = abs_amounts[-3:] if len(abs_amounts) >= 3 else abs_amounts
    within = sum(1 for a in recent if abs(a - median) <= threshold)
    return within >= 2


def _detect_subscriptions(conn) -> list[dict]:
    """Detect recurring charges from transaction history.

    365-day lookback, expenses only, excludes transfers/income/watchlist/dismissed.
    """
    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%Y-%m-%d")
    today = datetime.now().date()

    rows = conn.execute(
        "SELECT merchant_canonical, date, amount_cents "
        "FROM transactions "
        "WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        "  AND amount_cents < 0 "
        "  AND date >= ? AND date <= ? "
        "  AND category NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income') "
        "ORDER BY merchant_canonical, date",
        (cutoff, today_str),
    ).fetchall()

    # Build exclusion sets
    try:
        watchlist_merchants = {
            r[0].lower()
            for r in conn.execute(
                "SELECT merchant FROM subscription_watchlist "
                "WHERE status != 'cancelled'"
            ).fetchall()
            if r[0]
        }
    except Exception:
        watchlist_merchants = set()

    try:
        dismissed = {
            r[0]
            for r in conn.execute(
                "SELECT merchant_canonical FROM subscription_dismissals"
            ).fetchall()
        }
    except Exception:
        dismissed = set()

    # Group by merchant
    groups: dict[str, list[dict]] = {}
    for r in rows:
        merchant = r["merchant_canonical"]
        if merchant not in groups:
            groups[merchant] = []
        groups[merchant].append({"date": r["date"], "amount_cents": r["amount_cents"]})

    suggestions = []
    for merchant, txns in groups.items():
        # Skip if already on watchlist or dismissed
        if merchant.lower() in watchlist_merchants:
            continue
        if merchant in dismissed:
            continue
        if len(txns) < 2:
            continue

        dates, amounts = [], []
        for t in txns:
            try:
                dates.append(datetime.strptime(t["date"], "%Y-%m-%d").date())
            except (ValueError, TypeError):
                continue
            amounts.append(t["amount_cents"])

        if len(dates) < 2:
            continue

        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        intervals = [iv for iv in intervals if iv > 0]
        if not intervals:
            continue

        median_interval = statistics.median(intervals)
        cadence = _classify_cadence(median_interval)
        if cadence is None:
            continue
        if not _amount_is_regular(amounts):
            continue

        # Staleness check: skip if last charge was too long ago
        last_date = dates[-1]
        if (today - last_date).days > 2 * median_interval:
            continue

        median_amount = int(statistics.median([abs(a) for a in amounts]))
        suggestions.append({
            "merchant_canonical": merchant,
            "frequency": _CADENCE_TO_FREQUENCY[cadence],
            "cadence_label": cadence,
            "amount_cents": median_amount,
            "last_date": last_date.isoformat(),
            "occurrence_count": len(txns),
        })

    # Sort by amount descending (biggest subscriptions first)
    suggestions.sort(key=lambda x: x["amount_cents"], reverse=True)
    return suggestions


# ── Watchlist helpers ─────────────────────────────────────────────────────────

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
        suggestions = _detect_subscriptions(conn)
        return render_template(
            "subscriptions.html",
            watchlist=watchlist,
            suggestions=suggestions,
        )
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
    if frequency not in ("weekly", "biweekly", "monthly", "quarterly", "annual"):
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


@bp.route("/accept", methods=["POST"])
def accept():
    """Accept a subscription suggestion: add to watchlist + dismiss."""
    merchant = (request.form.get("merchant") or "").strip()
    merchant_canonical = (request.form.get("merchant_canonical") or "").strip()
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
    if frequency not in ("weekly", "biweekly", "monthly", "quarterly", "annual"):
        frequency = "monthly"

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO subscription_watchlist "
            "(merchant, amount_cents, frequency) VALUES (?, ?, ?)",
            (merchant, amount_cents, frequency),
        )
        if merchant_canonical:
            conn.execute(
                "INSERT OR IGNORE INTO subscription_dismissals "
                "(merchant_canonical) VALUES (?)",
                (merchant_canonical,),
            )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("subscriptions.index"))


@bp.route("/dismiss", methods=["POST"])
def dismiss():
    """Dismiss a subscription suggestion (permanently hide it)."""
    merchant = (request.form.get("merchant_canonical") or "").strip()
    if not merchant:
        return redirect(url_for("subscriptions.index"))
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO subscription_dismissals "
            "(merchant_canonical) VALUES (?)",
            (merchant,),
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

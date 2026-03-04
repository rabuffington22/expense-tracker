"""Subscription Tracker — tag recurring charges to consider cancelling."""

from __future__ import annotations

import statistics
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, g, jsonify, redirect, render_template, request, url_for

from core.db import get_connection

bp = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")

_ACCOUNT_INFO_FIELD_TYPES = [
    "Email", "Username", "Password", "Account #",
    "Phone", "PIN", "Website", "Other",
]

# Merchants matching these patterns (case-insensitive) are never subscriptions
_EXCLUDE_MERCHANTS = [
    "interest",
    "fee",
    "late charge",
    "finance charge",
    "minimum charge",
    "annual fee",
    "foreign transaction",
]


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

_FREQUENCY_TO_CADENCE = {v: k for k, v in _CADENCE_TO_FREQUENCY.items()}


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
        # Skip interest charges, fees, etc.
        merchant_lower = merchant.lower()
        if any(pat in merchant_lower for pat in _EXCLUDE_MERCHANTS):
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

        abs_amounts = [abs(a) for a in amounts]
        median_amount = int(statistics.median(abs_amounts))
        min_amount = min(abs_amounts)
        max_amount = max(abs_amounts)
        first_date = dates[0]

        # Recent charges (last 4, newest first)
        paired = list(zip(dates, abs_amounts))
        recent = paired[-4:]
        recent.reverse()
        recent_charges = [
            {"date": d.strftime("%b %-d, %Y"), "amount_cents": a}
            for d, a in recent
        ]

        suggestions.append({
            "merchant_canonical": merchant,
            "frequency": _CADENCE_TO_FREQUENCY[cadence],
            "cadence_label": cadence,
            "amount_cents": median_amount,
            "min_amount_cents": min_amount,
            "max_amount_cents": max_amount,
            "first_date": first_date.isoformat(),
            "first_date_display": first_date.strftime("%b %Y"),
            "last_date": last_date.isoformat(),
            "last_date_display": last_date.strftime("%b %Y"),
            "occurrence_count": len(txns),
            "recent_charges": recent_charges,
        })

    # Sort by amount descending (biggest subscriptions first)
    suggestions.sort(key=lambda x: x["amount_cents"], reverse=True)
    return suggestions


# ── Merchant charge history ──────────────────────────────────────────────────

def _get_merchant_charges(conn, merchant: str) -> dict | None:
    """Get charge history for a merchant from transaction data.

    Returns dict with charge stats, or None if no matching transactions found.
    """
    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%Y-%m-%d")

    rows = conn.execute(
        "SELECT date, amount_cents FROM transactions "
        "WHERE merchant_canonical = ? "
        "  AND amount_cents < 0 "
        "  AND date >= ? AND date <= ? "
        "  AND category NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income') "
        "ORDER BY date",
        (merchant, cutoff, today_str),
    ).fetchall()

    if not rows:
        return None

    dates, amounts = [], []
    for r in rows:
        try:
            dates.append(datetime.strptime(r["date"], "%Y-%m-%d").date())
        except (ValueError, TypeError):
            continue
        amounts.append(r["amount_cents"])

    if not dates:
        return None

    abs_amounts = [abs(a) for a in amounts]
    median_amount = int(statistics.median(abs_amounts))

    # Detect cadence
    cadence_label = None
    frequency = None
    if len(dates) >= 2:
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        intervals = [iv for iv in intervals if iv > 0]
        if intervals:
            median_interval = statistics.median(intervals)
            cadence = _classify_cadence(median_interval)
            if cadence:
                cadence_label = cadence
                frequency = _CADENCE_TO_FREQUENCY[cadence]

    # Recent charges (last 4, newest first)
    paired = list(zip(dates, abs_amounts))
    recent = paired[-4:]
    recent.reverse()
    recent_charges = [
        {"date": d.strftime("%b %-d, %Y"), "amount_cents": a}
        for d, a in recent
    ]

    return {
        "occurrence_count": len(dates),
        "first_date_display": dates[0].strftime("%b %Y"),
        "last_date_display": dates[-1].strftime("%b %Y"),
        "amount_cents": median_amount,
        "min_amount_cents": min(abs_amounts),
        "max_amount_cents": max(abs_amounts),
        "recent_charges": recent_charges,
        "cadence_label": cadence_label,
        "frequency": frequency,
    }


# ── Timeline helpers ─────────────────────────────────────────────────────────

def _log_event(conn, sub_id: int, action: str, detail: str | None = None):
    """Append an event to the subscription timeline."""
    try:
        conn.execute(
            "INSERT INTO subscription_notes_log "
            "(subscription_id, action, detail) VALUES (?, ?, ?)",
            (sub_id, action, detail),
        )
    except Exception:
        pass  # Table may not exist pre-migration


def _get_timeline(conn, sub_id: int) -> list[dict]:
    """Get timeline entries for a subscription, newest first."""
    try:
        rows = conn.execute(
            "SELECT action, detail, created_at "
            "FROM subscription_notes_log "
            "WHERE subscription_id = ? "
            "ORDER BY created_at DESC, id DESC",
            (sub_id,),
        ).fetchall()
        result = []
        for r in rows:
            created = r["created_at"]
            try:
                dt = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
                display = dt.strftime("%b %-d")
            except (ValueError, TypeError):
                display = created[:10] if created else ""
            result.append({
                "action": r["action"],
                "detail": r["detail"],
                "date_display": display,
            })
        return result
    except Exception:
        return []


# ── Cancellation tips ────────────────────────────────────────────────────────

def _generate_and_store_tips(conn, sub_id: int, merchant: str):
    """Generate cancellation tips via AI and store in DB."""
    try:
        from core.ai_client import generate_cancellation_tips

        tips = generate_cancellation_tips(merchant)
        if tips:
            conn.execute(
                "UPDATE subscription_watchlist "
                "SET cancellation_tips = ? WHERE id = ?",
                (tips, sub_id),
            )
            _log_event(conn, sub_id, "tips_generated")
    except Exception:
        pass  # Graceful degradation — no tips is fine


# ── Payment method detection ─────────────────────────────────────────────────

def _get_payment_method(conn, merchant: str) -> str | None:
    """Detect which account/card a subscription charges to."""
    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT account FROM transactions "
        "WHERE merchant_canonical = ? AND amount_cents < 0 "
        "  AND date >= ? AND account IS NOT NULL AND account != '' "
        "ORDER BY date DESC LIMIT 10",
        (merchant, cutoff),
    ).fetchall()
    if not rows:
        return None
    # Most common account in recent charges
    accounts = [r["account"] for r in rows]
    counter = Counter(accounts)
    return counter.most_common(1)[0][0]


# ── Account info helpers ────────────────────────────────────────────────────

def _get_account_info(conn, sub_id: int) -> list[dict]:
    """Get account info fields for a subscription."""
    try:
        rows = conn.execute(
            "SELECT id, field_type, field_value, sort_order "
            "FROM subscription_account_info "
            "WHERE subscription_id = ? ORDER BY sort_order, id",
            (sub_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Watchlist helpers ─────────────────────────────────────────────────────────

def _get_watchlist(conn) -> list[dict]:
    """Fetch subscription watchlist items.

    Sorted: cancelling first, then watching, then by created_at desc.
    Excludes cancelled items.
    """
    try:
        rows = conn.execute(
            "SELECT id, merchant, amount_cents, frequency, status, notes, "
            "       cancellation_tips, created_at, updated_at "
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

        # Get dismissed merchants
        try:
            dismissed = [
                r["merchant_canonical"]
                for r in conn.execute(
                    "SELECT merchant_canonical FROM subscription_dismissals "
                    "ORDER BY dismissed_at DESC"
                ).fetchall()
            ]
        except Exception:
            dismissed = []

        return render_template(
            "subscriptions.html",
            watchlist=watchlist,
            suggestions=suggestions,
            dismissed=dismissed,
        )
    finally:
        conn.close()


@bp.route("/detail/<int:sub_id>")
def detail(sub_id):
    """Return JSON detail for a watchlist item (charge history + timeline + tips)."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT id, merchant, amount_cents, frequency, status, notes, "
            "       cancellation_tips, created_at "
            "FROM subscription_watchlist WHERE id = ?",
            (sub_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404

        sub = dict(row)
        charges = _get_merchant_charges(conn, sub["merchant"])
        timeline = _get_timeline(conn, sub_id)
        account_info = _get_account_info(conn, sub_id)
        payment_method = _get_payment_method(conn, sub["merchant"])

        # Build cadence label from frequency
        cadence_label = _FREQUENCY_TO_CADENCE.get(sub["frequency"])

        return jsonify({
            "id": sub["id"],
            "merchant": sub["merchant"],
            "amount_cents": sub["amount_cents"],
            "frequency": sub["frequency"],
            "cadence_label": cadence_label,
            "status": sub["status"],
            "notes": sub["notes"],
            "cancellation_tips": sub["cancellation_tips"],
            "charges": charges,
            "timeline": timeline,
            "account_info": account_info,
            "payment_method": payment_method,
        })
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
        cursor = conn.execute(
            "INSERT INTO subscription_watchlist "
            "(merchant, amount_cents, frequency, notes) "
            "VALUES (?, ?, ?, ?)",
            (merchant, amount_cents, frequency, notes),
        )
        sub_id = cursor.lastrowid
        _log_event(conn, sub_id, "created", f"Added to watchlist")
        if notes:
            _log_event(conn, sub_id, "note_added", notes)
        conn.commit()

        # Generate tips in background (after commit so item exists)
        _generate_and_store_tips(conn, sub_id, merchant)
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
        cursor = conn.execute(
            "INSERT INTO subscription_watchlist "
            "(merchant, amount_cents, frequency) VALUES (?, ?, ?)",
            (merchant, amount_cents, frequency),
        )
        sub_id = cursor.lastrowid
        _log_event(conn, sub_id, "created", "Accepted from suggestions")
        if merchant_canonical:
            conn.execute(
                "INSERT OR IGNORE INTO subscription_dismissals "
                "(merchant_canonical) VALUES (?)",
                (merchant_canonical,),
            )
        conn.commit()

        # Generate tips after commit
        _generate_and_store_tips(conn, sub_id, merchant)
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


@bp.route("/undismiss", methods=["POST"])
def undismiss():
    """Restore a previously dismissed suggestion."""
    merchant = (request.form.get("merchant_canonical") or "").strip()
    if not merchant:
        return redirect(url_for("subscriptions.index"))
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "DELETE FROM subscription_dismissals "
            "WHERE merchant_canonical = ?",
            (merchant,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("subscriptions.index"))


@bp.route("/generate-tips/<int:sub_id>", methods=["POST"])
def generate_tips(sub_id):
    """Generate cancellation tips on demand for an existing watchlist item."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT id, merchant, cancellation_tips "
            "FROM subscription_watchlist WHERE id = ?",
            (sub_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404

        _generate_and_store_tips(conn, row["id"], row["merchant"])
        conn.commit()

        # Re-fetch to get the stored tips
        updated = conn.execute(
            "SELECT cancellation_tips FROM subscription_watchlist WHERE id = ?",
            (sub_id,),
        ).fetchone()
        tips = updated["cancellation_tips"] if updated else None
        return jsonify({"tips": tips})
    finally:
        conn.close()


@bp.route("/update/<int:sub_id>", methods=["POST"])
def update(sub_id):
    """Update subscription status and/or notes."""
    status = request.form.get("status", "")
    notes = request.form.get("notes")

    conn = get_connection(g.entity_key)
    try:
        # Get current values for timeline logging
        current = conn.execute(
            "SELECT status, notes FROM subscription_watchlist WHERE id = ?",
            (sub_id,),
        ).fetchone()

        if status and status in ("watching", "cancelling", "cancelled"):
            conn.execute(
                "UPDATE subscription_watchlist "
                "SET status=?, updated_at=datetime('now') WHERE id=?",
                (status, sub_id),
            )
            if current and current["status"] != status:
                _log_event(
                    conn, sub_id, "status_changed",
                    f"{current['status']} \u2192 {status}",
                )
        if notes is not None:
            new_notes = notes.strip() or None
            conn.execute(
                "UPDATE subscription_watchlist "
                "SET notes=?, updated_at=datetime('now') WHERE id=?",
                (new_notes, sub_id),
            )
            old_notes = current["notes"] if current else None
            if new_notes and new_notes != old_notes:
                _log_event(conn, sub_id, "note_added", new_notes)
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


# ── Account info CRUD ───────────────────────────────────────────────────────

@bp.route("/account-info/add/<int:sub_id>", methods=["POST"])
def add_account_info(sub_id):
    """Add an account info field to a subscription."""
    data = request.get_json(silent=True) or {}
    field_type = (data.get("field_type") or "").strip()
    field_value = (data.get("field_value") or "").strip()

    if not field_type or not field_value:
        return jsonify({"error": "field_type and field_value required"}), 400

    if field_type not in _ACCOUNT_INFO_FIELD_TYPES:
        field_type = "Other"

    conn = get_connection(g.entity_key)
    try:
        # Get next sort order
        row = conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 AS next_order "
            "FROM subscription_account_info WHERE subscription_id = ?",
            (sub_id,),
        ).fetchone()
        sort_order = row["next_order"] if row else 0

        cursor = conn.execute(
            "INSERT INTO subscription_account_info "
            "(subscription_id, field_type, field_value, sort_order) "
            "VALUES (?, ?, ?, ?)",
            (sub_id, field_type, field_value, sort_order),
        )
        field_id = cursor.lastrowid
        conn.commit()
        return jsonify({
            "id": field_id,
            "field_type": field_type,
            "field_value": field_value,
            "sort_order": sort_order,
        })
    finally:
        conn.close()


@bp.route("/account-info/delete/<int:field_id>", methods=["POST"])
def delete_account_info(field_id):
    """Delete an account info field."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "DELETE FROM subscription_account_info WHERE id = ?",
            (field_id,),
        )
        conn.commit()
        return jsonify({"ok": True})
    finally:
        conn.close()


@bp.route("/share-text/<int:sub_id>")
def share_text(sub_id):
    """Build a shareable text block with all subscription info."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT id, merchant, amount_cents, frequency, status, notes, "
            "       cancellation_tips "
            "FROM subscription_watchlist WHERE id = ?",
            (sub_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404

        sub = dict(row)
        lines = []

        # Header
        lines.append(sub["merchant"].upper())
        lines.append("=" * len(sub["merchant"]))

        # Amount + frequency
        if sub["amount_cents"]:
            freq_labels = {
                "weekly": "/wk", "biweekly": "/2wk", "monthly": "/mo",
                "quarterly": "/qtr", "annual": "/yr",
            }
            amt = f"${sub['amount_cents'] / 100:,.2f}".rstrip("0").rstrip(".")
            lines.append(f"Amount: {amt}{freq_labels.get(sub['frequency'], '')}")

        # Payment method
        payment = _get_payment_method(conn, sub["merchant"])
        if payment:
            lines.append(f"Charges to: {payment}")

        # Status
        lines.append(f"Status: {sub['status'].title()}")
        lines.append("")

        # Account info
        account_info = _get_account_info(conn, sub_id)
        if account_info:
            lines.append("ACCOUNT INFO")
            for field in account_info:
                lines.append(f"  {field['field_type']}: {field['field_value']}")
            lines.append("")

        # Cancellation tips
        if sub["cancellation_tips"]:
            lines.append("HOW TO CANCEL")
            lines.append(sub["cancellation_tips"])
            lines.append("")

        # Notes
        if sub["notes"]:
            lines.append("NOTES")
            lines.append(sub["notes"])
            lines.append("")

        # Recent charges
        charges = _get_merchant_charges(conn, sub["merchant"])
        if charges and charges.get("recent_charges"):
            lines.append("RECENT CHARGES")
            for c in charges["recent_charges"]:
                amt = f"${c['amount_cents'] / 100:,.2f}".rstrip("0").rstrip(".")
                lines.append(f"  {c['date']}  {amt}")
            lines.append("")

        return jsonify({"text": "\n".join(lines).strip()})
    finally:
        conn.close()

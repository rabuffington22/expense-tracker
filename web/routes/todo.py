"""To Do page — statement schedule reminders + data-driven queues."""

import calendar
from datetime import date, datetime

from flask import Blueprint, g, redirect, render_template, request, url_for

from core.db import get_connection

bp = Blueprint("todo", __name__, url_prefix="/todo")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _current_period_key() -> str:
    """Return 'YYYY-MM' for today in local time."""
    return date.today().strftime("%Y-%m")


def _next_due_date(statement_day: int) -> date:
    """Compute the next due date for a statement day.

    If today >= this month's statement day, the due is this month.
    If today < this month's statement day, the due is this month.
    statement_day is clamped to the last day of the month.
    """
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    clamped = min(statement_day, last_day)
    return date(today.year, today.month, clamped)


def _status_for(schedule, period_key: str) -> str:
    """Return 'done', 'due', or 'upcoming' for a schedule row."""
    if schedule["completed"]:
        return "done"
    today = date.today()
    due = _next_due_date(schedule["statement_day"])
    if today >= due:
        return "due"
    return "upcoming"


def _get_schedules(conn, period_key: str) -> list[dict]:
    """Fetch active schedules with completion status for the period."""
    rows = conn.execute(
        "SELECT s.id, s.name, s.statement_day, s.notes, s.is_active, "
        "       (SELECT 1 FROM statement_completions c "
        "        WHERE c.schedule_id = s.id AND c.period_key = ?) AS completed "
        "FROM statement_schedules s "
        "WHERE s.is_active = 1 "
        "ORDER BY s.statement_day ASC",
        (period_key,),
    ).fetchall()
    schedules = []
    for r in rows:
        d = dict(r)
        d["status"] = _status_for(d, period_key)
        d["due_date"] = _next_due_date(d["statement_day"])
        schedules.append(d)
    return schedules


def _get_queue_counts(conn) -> dict:
    """Compute queue counts similar to dashboard."""
    counts = {}

    # Uncategorized
    counts["uncategorized"] = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE (category IS NULL OR category = '' OR confidence < 0.6) "
        "AND category NOT IN ('Internal Transfer', 'Credit Card Payment') "
        "AND (category IS NULL OR category NOT IN ('Internal Transfer', 'Credit Card Payment'))"
    ).fetchone()[0]

    # Vendor breakdown needed
    counts["vendor_breakdown"] = conn.execute(
        "SELECT COUNT(*) FROM ("
        "  SELECT t.transaction_id FROM transactions t "
        "  LEFT JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id "
        "  WHERE t.amount_cents < -2500 "
        "    AND (LOWER(t.merchant_canonical) LIKE '%amazon%' "
        "         OR LOWER(t.description_raw) LIKE '%amzn%' "
        "         OR LOWER(t.description_raw) LIKE '%henry schein%') "
        "  GROUP BY t.transaction_id "
        "  HAVING COUNT(ao.id) = 0 "
        "     OR COALESCE(SUM(ABS(ao.order_total_cents)),0) < ABS(t.amount_cents) * 95 / 100"
        ")"
    ).fetchone()[0]

    # Possible transfers
    counts["possible_transfer"] = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE (category IS NULL OR category = '' OR category = 'Unknown') "
        "AND (LOWER(description_raw) LIKE '%transfer%' "
        "     OR LOWER(description_raw) LIKE '%payment%' "
        "     OR LOWER(description_raw) LIKE '%autopay%')"
    ).fetchone()[0]

    # Unmatched vendor orders
    counts["orders_unmatched"] = conn.execute(
        "SELECT COUNT(*) FROM amazon_orders "
        "WHERE matched_transaction_id IS NULL"
    ).fetchone()[0]

    # Orders to categorize
    counts["orders_uncategorized"] = conn.execute(
        "SELECT COUNT(*) FROM amazon_orders "
        "WHERE (category IS NULL OR category = '')"
    ).fetchone()[0]

    return counts


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    """Render the To Do page."""
    conn = get_connection(g.entity_key)
    try:
        period_key = _current_period_key()
        schedules = _get_schedules(conn, period_key)
        counts = _get_queue_counts(conn)
        return render_template(
            "todo.html",
            schedules=schedules,
            counts=counts,
            period_key=period_key,
            today=date.today(),
        )
    finally:
        conn.close()


@bp.route("/schedules/create", methods=["POST"])
def create_schedule():
    """Create a new statement schedule."""
    name = (request.form.get("name") or "").strip()
    day_str = request.form.get("statement_day", "")
    notes = (request.form.get("notes") or "").strip() or None

    if not name or not day_str:
        return redirect(url_for("todo.index"))

    try:
        day = int(day_str)
        day = max(1, min(31, day))
    except (ValueError, TypeError):
        return redirect(url_for("todo.index"))

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO statement_schedules (name, statement_day, notes) "
            "VALUES (?, ?, ?)",
            (name, day, notes),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("todo.index"))


@bp.route("/schedules/complete/<int:schedule_id>", methods=["POST"])
def complete_schedule(schedule_id):
    """Mark a schedule as completed for the current period."""
    period_key = _current_period_key()
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO statement_completions "
            "(schedule_id, period_key) VALUES (?, ?)",
            (schedule_id, period_key),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/schedules/toggle/<int:schedule_id>", methods=["POST"])
def toggle_schedule(schedule_id):
    """Toggle is_active for a schedule."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "UPDATE statement_schedules "
            "SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END "
            "WHERE id = ?",
            (schedule_id,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/schedules/delete/<int:schedule_id>", methods=["POST"])
def delete_schedule(schedule_id):
    """Delete a schedule (cascades completions)."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "DELETE FROM statement_schedules WHERE id = ?",
            (schedule_id,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))

"""To Do page — review queues, periodic tasks, statement reminders."""

import calendar
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import Blueprint, g, redirect, render_template, request, url_for

from core.db import get_connection

bp = Blueprint("todo", __name__, url_prefix="/todo")


# ── Statement-schedule helpers ────────────────────────────────────────────────

def _current_period_key() -> str:
    """Return 'YYYY-MM' for today in local time."""
    return date.today().strftime("%Y-%m")


def _next_due_date(statement_day: int) -> date:
    """Compute the due date for a statement day in the current month.

    statement_day is clamped to the last day of the month.
    """
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    clamped = min(statement_day, last_day)
    return date(today.year, today.month, clamped)


def _days_until(due: date) -> int:
    """Return days from today to due date (negative = overdue)."""
    return (due - date.today()).days


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
        d["days_until"] = _days_until(d["due_date"])
        schedules.append(d)
    return schedules


# ── Periodic-task helpers ─────────────────────────────────────────────────────

def _periodic_next_due(task_row: dict) -> date:
    """Compute the next due date for a periodic task.

    If never completed, due = this month's day_of_month (clamped).
    If completed before, the next due is cadence-months after the last
    completion, on day_of_month (clamped to that month's last day).
    If the computed next-due is in the past, it's overdue — return as-is.
    """
    today = date.today()
    dom = task_row["day_of_month"]
    cadence = task_row["cadence"]
    months = 3 if cadence == "quarterly" else 1
    last_done = task_row.get("last_completed_at")

    if last_done:
        # Parse last completion date
        last_dt = datetime.fromisoformat(last_done).date()
        # Next due = last completion month + cadence, day_of_month clamped
        next_dt = last_dt + relativedelta(months=months)
        last_day = calendar.monthrange(next_dt.year, next_dt.month)[1]
        clamped = min(dom, last_day)
        return date(next_dt.year, next_dt.month, clamped)
    else:
        # Never done — due this month (or already overdue)
        last_day = calendar.monthrange(today.year, today.month)[1]
        clamped = min(dom, last_day)
        return date(today.year, today.month, clamped)


def _periodic_status(task_row: dict) -> str:
    """Return 'done', 'due', or 'upcoming'."""
    today = date.today()
    due = _periodic_next_due(task_row)
    # "done" if last completion is on or after this cycle's due date
    last_done = task_row.get("last_completed_at")
    if last_done:
        last_dt = datetime.fromisoformat(last_done).date()
        if last_dt >= due:
            return "done"
    if today >= due:
        return "due"
    return "upcoming"


def _get_periodic_tasks(conn) -> list[dict]:
    """Fetch active periodic tasks with latest completion info.

    Sorted: due first, then by next due ascending.
    """
    rows = conn.execute(
        "SELECT t.id, t.name, t.cadence, t.day_of_month, t.notes, t.is_active, "
        "       (SELECT MAX(c.completed_at) FROM periodic_completions c "
        "        WHERE c.task_id = t.id) AS last_completed_at "
        "FROM periodic_tasks t "
        "WHERE t.is_active = 1 "
        "ORDER BY t.day_of_month ASC",
    ).fetchall()
    tasks = []
    for r in rows:
        d = dict(r)
        d["next_due"] = _periodic_next_due(d)
        d["status"] = _periodic_status(d)
        d["days_until"] = _days_until(d["next_due"])
        tasks.append(d)
    # Sort: due items first, then by next_due ascending
    status_order = {"due": 0, "upcoming": 1, "done": 2}
    tasks.sort(key=lambda t: (status_order.get(t["status"], 9), t["next_due"]))
    return tasks


# ── Queue counts ──────────────────────────────────────────────────────────────

def _get_queue_counts(conn) -> dict:
    """Compute queue counts + links for review queues."""
    today = date.today()
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

    # ── High-signal queues ────────────────────────────────────────────────

    cutoff_30 = (today - timedelta(days=30)).isoformat()
    cutoff_120 = (today - timedelta(days=120)).isoformat()
    today_iso = today.isoformat()

    # Large transactions (>=500, last 30 days, exclude transfers/CC payments)
    counts["large_txns"] = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE ABS(amount_cents) >= 50000 "
        "AND date >= ? AND date <= ? "
        "AND COALESCE(category, '') NOT IN ('Internal Transfer', 'Credit Card Payment')",
        (cutoff_30, today_iso),
    ).fetchone()[0]

    # New merchants (last 30 days not seen in prior 90 days)
    counts["new_merchants"] = conn.execute(
        "SELECT COUNT(DISTINCT merchant_canonical) FROM transactions "
        "WHERE date >= ? AND date <= ? "
        "AND merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        "AND COALESCE(category, '') NOT IN ('Internal Transfer', 'Credit Card Payment') "
        "AND merchant_canonical NOT IN ("
        "  SELECT DISTINCT merchant_canonical FROM transactions "
        "  WHERE date >= ? AND date < ? "
        "  AND merchant_canonical IS NOT NULL AND merchant_canonical != ''"
        ")",
        (cutoff_30, today_iso, cutoff_120, cutoff_30),
    ).fetchone()[0]

    # Store date range strings for link building
    counts["_30d_start"] = cutoff_30
    counts["_30d_end"] = today_iso

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
        periodic_tasks = _get_periodic_tasks(conn)
        return render_template(
            "todo.html",
            schedules=schedules,
            counts=counts,
            periodic_tasks=periodic_tasks,
            period_key=period_key,
            today=date.today(),
        )
    finally:
        conn.close()


# ── Statement schedule routes ─────────────────────────────────────────────────

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


# ── Periodic task routes ──────────────────────────────────────────────────────

@bp.route("/tasks/create", methods=["POST"])
def create_task():
    """Create a new periodic task."""
    name = (request.form.get("name") or "").strip()
    cadence = request.form.get("cadence", "monthly")
    day_str = request.form.get("day_of_month", "1")
    notes = (request.form.get("notes") or "").strip() or None

    if not name:
        return redirect(url_for("todo.index"))
    if cadence not in ("monthly", "quarterly"):
        cadence = "monthly"

    try:
        dom = int(day_str)
        dom = max(1, min(28, dom))
    except (ValueError, TypeError):
        dom = 1

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO periodic_tasks (name, cadence, day_of_month, notes) "
            "VALUES (?, ?, ?, ?)",
            (name, cadence, dom, notes),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/tasks/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    """Record a completion for a periodic task."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO periodic_completions (task_id) VALUES (?)",
            (task_id,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """Delete a periodic task (cascades completions)."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "DELETE FROM periodic_tasks WHERE id = ?",
            (task_id,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))

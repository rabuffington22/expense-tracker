"""To Do page — review queues, periodic tasks, statement reminders, cut list."""

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
    months = {"quarterly": 3, "annual": 12}.get(cadence, 1)
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
        "WHERE (category IS NULL OR category = '' OR category = 'Needs Review') "
        "AND (category IS NULL OR category NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout'))"
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

    # Unmatched vendor payment transactions (Venmo/PayPal)
    try:
        counts["vendor_txns_unmatched"] = conn.execute(
            "SELECT COUNT(*) FROM vendor_transactions "
            "WHERE matched_transaction_id IS NULL"
        ).fetchone()[0]
    except Exception:
        counts["vendor_txns_unmatched"] = 0

    # ── High-signal queues ────────────────────────────────────────────────

    cutoff_30 = (today - timedelta(days=30)).isoformat()
    cutoff_120 = (today - timedelta(days=120)).isoformat()
    today_iso = today.isoformat()

    # Load dismissal cutoffs (items with date <= dismissed_before are hidden)
    dismissals = {}
    try:
        for row in conn.execute(
            "SELECT queue_type, dismissed_before FROM queue_dismissals"
        ).fetchall():
            dismissals[row[0]] = row[1]
    except Exception:
        pass  # Table may not exist yet pre-migration

    # Load per-item dismissals
    lt_item_dismissed = _get_item_dismissals(conn, "large_txns")
    nm_item_dismissed = _get_item_dismissals(conn, "new_merchants")

    # Large transactions (>=500, last 30 days, exclude transfers/CC payments)
    lt_cutoff = dismissals.get("large_txns", "")
    lt_start = max(cutoff_30, lt_cutoff) if lt_cutoff else cutoff_30
    lt_rows = conn.execute(
        "SELECT transaction_id FROM transactions "
        "WHERE ABS(amount_cents) >= 50000 "
        "AND date > ? AND date <= ? "
        "AND COALESCE(category, '') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')",
        (lt_start, today_iso),
    ).fetchall()
    counts["large_txns"] = sum(
        1 for r in lt_rows if r[0] not in lt_item_dismissed
    )

    # New merchants (last 30 days not seen in prior 90 days)
    nm_cutoff = dismissals.get("new_merchants", "")
    nm_start = max(cutoff_30, nm_cutoff) if nm_cutoff else cutoff_30
    nm_rows = conn.execute(
        "SELECT DISTINCT merchant_canonical FROM transactions "
        "WHERE date > ? AND date <= ? "
        "AND merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        "AND COALESCE(category, '') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout') "
        "AND merchant_canonical NOT IN ("
        "  SELECT DISTINCT merchant_canonical FROM transactions "
        "  WHERE date >= ? AND date < ? "
        "  AND merchant_canonical IS NOT NULL AND merchant_canonical != ''"
        ")",
        (nm_start, today_iso, cutoff_120, cutoff_30),
    ).fetchall()
    counts["new_merchants"] = sum(
        1 for r in nm_rows if r[0] not in nm_item_dismissed
    )

    # Store date range strings for link building
    counts["_30d_start"] = cutoff_30
    counts["_30d_end"] = today_iso

    return counts


# ── Queue detail queries (for inline popups) ─────────────────────────────────

def _get_dismissal(conn, queue_type: str) -> str:
    """Return dismissed_before date for a queue type, or empty string."""
    try:
        row = conn.execute(
            "SELECT dismissed_before FROM queue_dismissals WHERE queue_type=?",
            (queue_type,),
        ).fetchone()
        return row[0] if row else ""
    except Exception:
        return ""


def _get_item_dismissals(conn, queue_type: str) -> set:
    """Return set of dismissed item_keys for a queue type."""
    try:
        rows = conn.execute(
            "SELECT item_key FROM queue_item_dismissals WHERE queue_type=?",
            (queue_type,),
        ).fetchall()
        return {r[0] for r in rows}
    except Exception:
        return set()


def _get_large_txns(conn) -> list[dict]:
    """Return large transactions (>=$500) from the last 30 days."""
    today = date.today()
    cutoff = (today - timedelta(days=30)).isoformat()
    today_iso = today.isoformat()
    dismissed = _get_dismissal(conn, "large_txns")
    start = max(cutoff, dismissed) if dismissed else cutoff
    dismissed_items = _get_item_dismissals(conn, "large_txns")
    rows = conn.execute(
        "SELECT transaction_id, date, merchant_canonical, description_raw, "
        "       amount_cents, category "
        "FROM transactions "
        "WHERE ABS(amount_cents) >= 50000 "
        "AND date > ? AND date <= ? "
        "AND COALESCE(category, '') NOT IN "
        "    ('Internal Transfer', 'Credit Card Payment') "
        "ORDER BY ABS(amount_cents) DESC",
        (start, today_iso),
    ).fetchall()
    result = [dict(r) for r in rows if r["transaction_id"] not in dismissed_items]
    return result


def _get_new_merchants(conn) -> list[dict]:
    """Return merchants seen in last 30 days but not in prior 90 days."""
    today = date.today()
    cutoff_30 = (today - timedelta(days=30)).isoformat()
    cutoff_120 = (today - timedelta(days=120)).isoformat()
    today_iso = today.isoformat()
    dismissed = _get_dismissal(conn, "new_merchants")
    start = max(cutoff_30, dismissed) if dismissed else cutoff_30
    dismissed_items = _get_item_dismissals(conn, "new_merchants")
    rows = conn.execute(
        "SELECT merchant_canonical, "
        "       MIN(date) AS first_date, "
        "       COUNT(*) AS txn_count, "
        "       SUM(amount_cents) AS total_cents "
        "FROM transactions "
        "WHERE date > ? AND date <= ? "
        "AND merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        "AND COALESCE(category, '') NOT IN "
        "    ('Internal Transfer', 'Credit Card Payment') "
        "AND merchant_canonical NOT IN ("
        "  SELECT DISTINCT merchant_canonical FROM transactions "
        "  WHERE date >= ? AND date < ? "
        "  AND merchant_canonical IS NOT NULL AND merchant_canonical != ''"
        ") "
        "GROUP BY merchant_canonical "
        "ORDER BY total_cents ASC",
        (start, today_iso, cutoff_120, cutoff_30),
    ).fetchall()
    result = [dict(r) for r in rows if r["merchant_canonical"] not in dismissed_items]
    return result


# ── Cut list helpers ──────────────────────────────────────────────────────────

def _get_cut_list(conn) -> list[dict]:
    """Fetch cut list items, pending first then done."""
    try:
        rows = conn.execute(
            "SELECT id, name, monthly_cents, notes, status, completed_at "
            "FROM cut_list ORDER BY status ASC, id ASC"
        ).fetchall()
        items = []
        for r in rows:
            d = dict(r)
            d["monthly_dollars"] = d["monthly_cents"] / 100 if d["monthly_cents"] else 0
            items.append(d)
        return items
    except Exception:
        return []


def _cut_list_summary(items: list[dict]) -> dict:
    """Compute cut list totals."""
    pending = [i for i in items if i["status"] == "pending"]
    done = [i for i in items if i["status"] == "done"]
    return {
        "pending_count": len(pending),
        "done_count": len(done),
        "pending_monthly": sum(i["monthly_cents"] for i in pending) / 100,
        "done_monthly": sum(i["monthly_cents"] for i in done) / 100,
        "total_monthly": sum(i["monthly_cents"] for i in items) / 100,
    }


# ── Routes ───────────────────────────────────────────────────────────────────

def _get_watchlist_count(conn) -> int:
    """Return the count of active subscription watchlist items."""
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM subscription_watchlist "
            "WHERE status IN ('watching', 'cancelling')"
        ).fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


@bp.route("/")
def index():
    """Render the To Do page."""
    conn = get_connection(g.entity_key)
    try:
        period_key = _current_period_key()
        schedules = _get_schedules(conn, period_key)
        counts = _get_queue_counts(conn)
        periodic_tasks = _get_periodic_tasks(conn)
        watchlist_count = _get_watchlist_count(conn)
        cut_items = _get_cut_list(conn)
        cut_summary = _cut_list_summary(cut_items)
        return render_template(
            "todo.html",
            schedules=schedules,
            counts=counts,
            periodic_tasks=periodic_tasks,
            watchlist_count=watchlist_count,
            cut_items=cut_items,
            cut_summary=cut_summary,
            period_key=period_key,
            today=date.today(),
        )
    finally:
        conn.close()


# ── Queue detail endpoints (HTMX partials for inline popups) ─────────────────

@bp.route("/queue/large-txns")
def queue_large_txns():
    """Return HTML partial listing large transactions (last 30 days)."""
    today = date.today()
    cutoff = (today - timedelta(days=30)).isoformat()
    conn = get_connection(g.entity_key)
    try:
        txns = _get_large_txns(conn)
        return render_template(
            "components/todo_queue_detail.html",
            queue_type="large_txns",
            queue_title="Large Transactions",
            queue_hint="last 30 days",
            txns=txns,
            merchants=None,
            fallback_url=url_for(
                "transactions.index",
                start=cutoff, end=today.isoformat(),
                large_txns=1, sort="amount", dir="desc",
            ),
        )
    finally:
        conn.close()


@bp.route("/queue/new-merchants")
def queue_new_merchants():
    """Return HTML partial listing new merchants (last 30 days)."""
    today = date.today()
    cutoff = (today - timedelta(days=30)).isoformat()
    conn = get_connection(g.entity_key)
    try:
        merchants = _get_new_merchants(conn)
        return render_template(
            "components/todo_queue_detail.html",
            queue_type="new_merchants",
            queue_title="New Merchants",
            queue_hint="last 30 days",
            txns=None,
            merchants=merchants,
            fallback_url=url_for(
                "transactions.index",
                start=cutoff, end=today.isoformat(),
                new_merchants=1,
            ),
        )
    finally:
        conn.close()


@bp.route("/queue/dismiss", methods=["POST"])
def queue_dismiss():
    """Dismiss all items in a queue (mark as reviewed up to today)."""
    queue_type = request.form.get("queue_type", "")
    if queue_type not in ("large_txns", "new_merchants"):
        return redirect(url_for("todo.index"))
    today_iso = date.today().isoformat()
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO queue_dismissals (queue_type, dismissed_before) "
            "VALUES (?, ?) "
            "ON CONFLICT(queue_type) DO UPDATE SET "
            "dismissed_before=excluded.dismissed_before, "
            "dismissed_at=datetime('now')",
            (queue_type, today_iso),
        )
        # Also clear per-item dismissals since bulk dismiss covers them
        conn.execute(
            "DELETE FROM queue_item_dismissals WHERE queue_type=?",
            (queue_type,),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/queue/dismiss-item", methods=["POST"])
def queue_dismiss_item():
    """Dismiss a single item from a queue. Returns empty HTML (HTMX removes row)."""
    queue_type = request.form.get("queue_type", "")
    item_key = request.form.get("item_key", "")
    if queue_type not in ("large_txns", "new_merchants") or not item_key:
        return "", 400
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO queue_item_dismissals (queue_type, item_key) "
            "VALUES (?, ?)",
            (queue_type, item_key),
        )
        conn.commit()
    finally:
        conn.close()
    return ""  # HTMX will remove the row via hx-swap="outerHTML"


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
    if cadence not in ("monthly", "quarterly", "annual"):
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


@bp.route("/tasks/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    """Update a periodic task's name, cadence, day, notes."""
    name = (request.form.get("name") or "").strip()
    cadence = request.form.get("cadence", "monthly")
    day_str = request.form.get("day_of_month", "1")
    notes = (request.form.get("notes") or "").strip() or None

    if not name:
        return redirect(url_for("todo.index"))
    if cadence not in ("monthly", "quarterly", "annual"):
        cadence = "monthly"

    try:
        dom = int(day_str)
        dom = max(1, min(28, dom))
    except (ValueError, TypeError):
        dom = 1

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "UPDATE periodic_tasks SET name=?, cadence=?, day_of_month=?, notes=? "
            "WHERE id=?",
            (name, cadence, dom, notes, task_id),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


_QUICK_ADD_PRESETS = {
    "us_bank_login": {
        "name": "US Bank login",
        "cadence": "quarterly",
        "day_of_month": 1,
        "notes": None,
    },
    "amazon_statement": {
        "name": "Amazon statement",
        "cadence": "monthly",
        "day_of_month": 1,
        "notes": None,
    },
    "henry_schein_statement": {
        "name": "Henry Schein statement",
        "cadence": "monthly",
        "day_of_month": 1,
        "notes": None,
    },
}


@bp.route("/tasks/quick-add", methods=["POST"])
def quick_add_task():
    """Create a preset periodic task if it doesn't already exist."""
    preset_key = request.form.get("preset", "")
    preset = _QUICK_ADD_PRESETS.get(preset_key)
    if not preset:
        return redirect(url_for("todo.index"))

    conn = get_connection(g.entity_key)
    try:
        existing = conn.execute(
            "SELECT id FROM periodic_tasks WHERE name = ? AND is_active = 1",
            (preset["name"],),
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO periodic_tasks (name, cadence, day_of_month, notes) "
                "VALUES (?, ?, ?, ?)",
                (preset["name"], preset["cadence"], preset["day_of_month"], preset["notes"]),
            )
            conn.commit()
            return redirect(url_for("todo.index", highlight=preset["name"]))
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


# ── Cut list routes ──────────────────────────────────────────────────────────

@bp.route("/cut/add", methods=["POST"])
def cut_add():
    """Add a new item to the cut list."""
    name = (request.form.get("name") or "").strip()
    if not name:
        return redirect(url_for("todo.index"))
    monthly_str = request.form.get("monthly", "0")
    notes = (request.form.get("notes") or "").strip() or None
    try:
        monthly_cents = int(float(monthly_str.replace(",", "").replace("$", "")) * 100)
    except (ValueError, TypeError):
        monthly_cents = 0
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO cut_list (name, monthly_cents, notes) VALUES (?, ?, ?)",
            (name, monthly_cents, notes),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/cut/toggle/<int:item_id>", methods=["POST"])
def cut_toggle(item_id):
    """Toggle a cut list item between pending and done."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT status FROM cut_list WHERE id = ?", (item_id,)
        ).fetchone()
        if row:
            if row[0] == "pending":
                conn.execute(
                    "UPDATE cut_list SET status = 'done', "
                    "completed_at = datetime('now') WHERE id = ?",
                    (item_id,),
                )
            else:
                conn.execute(
                    "UPDATE cut_list SET status = 'pending', "
                    "completed_at = NULL WHERE id = ?",
                    (item_id,),
                )
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))


@bp.route("/cut/delete/<int:item_id>", methods=["POST"])
def cut_delete(item_id):
    """Delete a cut list item."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM cut_list WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("todo.index"))



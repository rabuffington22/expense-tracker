"""Short-Term Planning — debt payoff goals and monthly budgets."""
from __future__ import annotations

import calendar
import json
import logging
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, render_template, request, g, redirect, url_for, make_response, jsonify
from markupsafe import escape

from core.db import get_connection, init_db
from core.reporting import effective_txns_cte, EXCLUDE_CATS
from web import get_categories

log = logging.getLogger(__name__)

bp = Blueprint("short_term_planning", __name__, url_prefix="/planning/short-term")

# Transfer/income categories to exclude from budget actuals (from single source of truth)
_EXCLUDE_CATS = EXCLUDE_CATS


# ── Helpers ──────────────────────────────────────────────────────────────────


def _parse_dollar_to_cents(dollar_str: str) -> int:
    """Parse '$1,234.56' or '1234.56' into cents (123456)."""
    try:
        cleaned = dollar_str.replace(",", "").replace("$", "").strip()
        return int(round(float(cleaned) * 100))
    except (ValueError, TypeError):
        return 0


def _get_payroll_schedule(conn) -> dict | None:
    """Return the payroll schedule singleton or None if not configured."""
    row = conn.execute("SELECT * FROM payroll_schedule WHERE id = 1").fetchone()
    return dict(row) if row else None


def _count_pay_periods(anchor_date_str: str, cadence_days: int, month_str: str) -> int:
    """Count how many pay periods fall within a given month.

    Args:
        anchor_date_str: A known payday in YYYY-MM-DD format.
        cadence_days: Days between paydays (14 for biweekly).
        month_str: Target month in YYYY-MM format.

    Returns:
        Number of paydays in the month (typically 2 or 3).
    """
    anchor = datetime.strptime(anchor_date_str, "%Y-%m-%d").date()
    target = datetime.strptime(month_str, "%Y-%m").date()
    first_day = target.replace(day=1)
    last_day = target.replace(day=calendar.monthrange(target.year, target.month)[1])

    # Step backward from anchor to before the target month
    d = anchor
    while d >= first_day:
        d -= timedelta(days=cadence_days)
    # Now d is before the month — step forward and count
    count = 0
    d += timedelta(days=cadence_days)
    while d <= last_day:
        if d >= first_day:
            count += 1
        d += timedelta(days=cadence_days)
    return count


def _get_goals(conn) -> list[dict]:
    """Return all goals for the current entity."""
    rows = conn.execute(
        "SELECT * FROM short_term_goals ORDER BY "
        "CASE status WHEN 'active' THEN 0 WHEN 'paused' THEN 1 ELSE 2 END, "
        "created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def _get_goal(conn, goal_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM short_term_goals WHERE id = ?", (goal_id,)
    ).fetchone()
    return dict(row) if row else None


def _get_snapshots(conn, goal_id: int) -> list[dict]:
    """Return snapshots for a goal, ordered by date."""
    rows = conn.execute(
        "SELECT * FROM goal_snapshots WHERE goal_id = ? ORDER BY snapshot_date",
        (goal_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _auto_snapshot(conn, goal: dict):
    """Record today's balance snapshot from linked accounts."""
    if goal["status"] != "active":
        return
    linked = json.loads(goal["linked_accounts"] or "[]")
    if not linked:
        return

    # Sum balances from linked accounts
    total_cents = 0
    for acct_name in linked:
        row = conn.execute(
            "SELECT balance_cents FROM account_balances WHERE account_name = ?",
            (acct_name,),
        ).fetchone()
        if row:
            total_cents += abs(row["balance_cents"])

    today_str = date.today().isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO goal_snapshots (goal_id, snapshot_date, balance_cents) "
        "VALUES (?, ?, ?)",
        (goal["id"], today_str, total_cents),
    )
    conn.commit()


def _compute_payoff_timeline(
    accounts: list[dict], monthly_extra: int, strategy: str
) -> list[dict]:
    """Simulate month-by-month debt payoff.

    accounts: list of {name, balance_cents, rate_bps, min_payment_cents}
    monthly_extra: extra cents/month to allocate
    strategy: 'avalanche' | 'snowball' | 'custom'

    Returns list of monthly snapshots: {month, accounts: [{name, balance}], total, interest}
    """
    if not accounts:
        return []

    # Working copies
    balances = {a["name"]: a["balance_cents"] / 100 for a in accounts}
    rates = {a["name"]: (a["rate_bps"] / 10000) / 12 for a in accounts}
    mins = {a["name"]: a["min_payment_cents"] / 100 for a in accounts}
    extra = monthly_extra / 100

    timeline = []
    total_interest = 0

    for month in range(1, 289):  # up to 24 years max
        # Check if all paid off
        if all(b <= 0 for b in balances.values()):
            break

        month_interest = 0
        # Apply interest
        for name in balances:
            if balances[name] > 0:
                interest = balances[name] * rates[name]
                balances[name] += interest
                month_interest += interest

        total_interest += month_interest

        # Apply minimum payments
        freed_extra = 0
        for name in balances:
            if balances[name] > 0:
                payment = min(mins[name], balances[name])
                balances[name] -= payment
            else:
                freed_extra += mins[name]

        # Determine extra payment allocation order
        active = [n for n in balances if balances[n] > 0]
        if strategy == "avalanche":
            active.sort(key=lambda n: rates[n], reverse=True)
        elif strategy == "snowball":
            active.sort(key=lambda n: balances[n])
        # else custom — just go in order

        # Apply extra + freed minimums
        remaining_extra = extra + freed_extra
        for name in active:
            if remaining_extra <= 0:
                break
            payment = min(remaining_extra, balances[name])
            balances[name] -= payment
            remaining_extra -= payment

        # Clamp negatives
        for name in balances:
            if balances[name] < 0:
                balances[name] = 0

        snapshot = {
            "month": month,
            "accounts": {n: int(round(b * 100)) for n, b in balances.items()},
            "total_cents": int(round(sum(balances.values()) * 100)),
            "cumulative_interest_cents": int(round(total_interest * 100)),
        }
        timeline.append(snapshot)

        if all(b <= 0 for b in balances.values()):
            break

    return timeline


def _get_budget_items(conn) -> list[dict]:
    """Return all budget items."""
    rows = conn.execute(
        "SELECT * FROM budget_items ORDER BY category"
    ).fetchall()
    return [dict(r) for r in rows]


def _get_budget_status(conn, entity_key: str, month: str) -> list[dict]:
    """Compute budget vs actuals for ALL categories for a given month (YYYY-MM).

    Returns every category from the categories table, whether it has a budget
    or not.  Each item includes avg_month_count (0-3) for that specific category.
    """
    budget_items = _get_budget_items(conn)
    budget_map = {bi["category"]: bi for bi in budget_items}

    # All categories from the categories table (excluding system categories)
    all_cats = [
        r["name"] for r in conn.execute(
            "SELECT name FROM categories WHERE name NOT IN (%s) ORDER BY name"
            % ",".join("?" for _ in _EXCLUDE_CATS),
            list(_EXCLUDE_CATS),
        ).fetchall()
    ]

    # Get actual spending by category for the month
    exclude_clause = ",".join("?" for _ in _EXCLUDE_CATS)
    _cte = effective_txns_cte("t")
    rows = conn.execute(
        f"WITH {_cte} "
        "SELECT COALESCE(NULLIF(t.category,''),'Uncategorized') as cat, "
        "ABS(SUM(t.amount)) as total "
        "FROM t "
        "WHERE strftime('%%Y-%%m', t.date) = ? "
        "AND t.amount < 0 "
        "AND COALESCE(t.category,'') NOT IN (%s) "
        "GROUP BY cat" % exclude_clause,
        (month, *_EXCLUDE_CATS),
    ).fetchall()
    actuals = {r["cat"]: int(round(r["total"] * 100)) for r in rows}

    # Compute 3-month average for trend context
    try:
        bm = datetime.strptime(month, "%Y-%m").date()
    except ValueError:
        bm = date.today().replace(day=1)
    avg_months = []
    d = bm
    for _ in range(3):
        d = (d.replace(day=1) - timedelta(days=1)).replace(day=1)
        avg_months.append(d.strftime("%Y-%m"))
    month_placeholders = ",".join("?" for _ in avg_months)
    # Per-category: total spending and number of months with data in the prior 3 months
    avg_rows = conn.execute(
        f"WITH {_cte} "
        "SELECT COALESCE(NULLIF(t.category,''),'Uncategorized') as cat, "
        "ABS(SUM(t.amount)) as total, "
        "COUNT(DISTINCT strftime('%%Y-%%m', t.date)) as month_count "
        "FROM t "
        "WHERE strftime('%%Y-%%m', t.date) IN (%s) "
        "AND t.amount < 0 "
        "AND COALESCE(t.category,'') NOT IN (%s) "
        "GROUP BY cat" % (month_placeholders, exclude_clause),
        (*avg_months, *_EXCLUDE_CATS),
    ).fetchall()
    avg_actuals = {}
    avg_month_counts = {}
    for r in avg_rows:
        mc = r["month_count"]
        avg_actuals[r["cat"]] = int(round(r["total"] * 100 / max(mc, 1)))
        avg_month_counts[r["cat"]] = mc

    # Fetch payroll schedule for per-payroll budget computation
    schedule = _get_payroll_schedule(conn)
    pay_periods = None
    if schedule:
        pay_periods = _count_pay_periods(
            schedule["anchor_date"], schedule["cadence_days"], month
        )

    result = []
    seen = set()
    # First: all categories that have budgets
    for bi in budget_items:
        cat_name = bi["category"]
        seen.add(cat_name)
        spent = actuals.get(cat_name, 0)
        is_pp = bi.get("is_per_payroll", 0) and bi.get("per_payroll_cents")
        if is_pp and schedule and pay_periods:
            budget = bi["per_payroll_cents"] * pay_periods
        else:
            budget = bi["monthly_budget_cents"]
        remaining = budget - spent
        pct = int(round(spent / budget * 100)) if budget > 0 else 0
        avg_3mo = avg_actuals.get(cat_name, 0)
        avg_mc = avg_month_counts.get(cat_name, 0)
        result.append({
            "category": cat_name,
            "budget_cents": budget,
            "spent_cents": spent,
            "remaining_cents": remaining,
            "pct": min(pct, 999),
            "avg_3mo_cents": avg_3mo,
            "avg_month_count": avg_mc,
            "budget_section": bi.get("budget_section", "other"),
            "is_per_payroll": bool(is_pp),
            "per_payroll_cents": bi.get("per_payroll_cents", 0) or 0,
            "pay_periods": pay_periods if is_pp else None,
        })

    # Then: all remaining categories (no budget set)
    for cat_name in all_cats:
        if cat_name in seen:
            continue
        spent = actuals.get(cat_name, 0)
        avg_3mo = avg_actuals.get(cat_name, 0)
        avg_mc = avg_month_counts.get(cat_name, 0)
        result.append({
            "category": cat_name,
            "budget_cents": 0,
            "spent_cents": spent,
            "remaining_cents": -spent,
            "pct": 0,
            "avg_3mo_cents": avg_3mo,
            "avg_month_count": avg_mc,
            "budget_section": None,
            "is_per_payroll": False,
            "per_payroll_cents": 0,
            "pay_periods": None,
        })

    # Sort by 3-mo avg spending descending (most expensive categories first)
    result.sort(key=lambda x: x["avg_3mo_cents"], reverse=True)
    return result


# Section order and display labels for budget grouping
_BUDGET_SECTIONS = [
    ("focus", "FOCUS"),
    ("fixed", "FIXED"),
    ("other", "EVERYTHING ELSE"),
    (None, "NO BUDGET"),
]


def _group_budget_items(items: list) -> list:
    """Group budget items by section, preserving sort within each group.

    Returns list of (section_key, section_label, items) tuples.
    """
    by_section = {}
    for item in items:
        sec = item.get("budget_section") or None
        by_section.setdefault(sec, []).append(item)

    result = []
    for key, label in _BUDGET_SECTIONS:
        group = by_section.get(key, [])
        if group:
            result.append((key, label, group))
    return result


def _get_unbudgeted_spending(conn, month: str, budgeted_cats: set) -> list[dict]:
    """Return categories with spending but no budget set."""
    exclude_clause = ",".join("?" for _ in _EXCLUDE_CATS)
    _cte = effective_txns_cte("t")
    rows = conn.execute(
        f"WITH {_cte} "
        "SELECT COALESCE(NULLIF(t.category,''),'Uncategorized') as cat, "
        "ABS(SUM(t.amount)) as total, COUNT(*) as cnt "
        "FROM t "
        "WHERE strftime('%%Y-%%m', t.date) = ? "
        "AND t.amount < 0 "
        "AND COALESCE(t.category,'') NOT IN (%s) "
        "GROUP BY cat ORDER BY total DESC" % exclude_clause,
        (month, *_EXCLUDE_CATS),
    ).fetchall()

    result = []
    for r in rows:
        if r["cat"] not in budgeted_cats:
            result.append({
                "category": r["cat"],
                "spent_cents": int(round(r["total"] * 100)),
                "txn_count": r["cnt"],
            })
    return result


def _suggest_monthly_extra(conn) -> int:
    """Estimate discretionary income available for debt payoff (cents)."""
    _cte = effective_txns_cte("t")
    # 3-month average income
    income_row = conn.execute(
        f"WITH {_cte} "
        "SELECT AVG(monthly_income) as avg_income FROM ("
        "  SELECT strftime('%%Y-%%m', t.date) as month, "
        "  SUM(t.amount) as monthly_income "
        "  FROM t "
        "  WHERE t.amount > 0 "
        "  AND COALESCE(t.category,'') NOT IN "
        "  ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
        "  AND t.date >= date('now', '-3 months') "
        "  GROUP BY month"
        ")"
    ).fetchone()
    avg_income = (income_row["avg_income"] or 0) if income_row else 0

    # 3-month average essential spending
    spend_row = conn.execute(
        f"WITH {_cte} "
        "SELECT AVG(monthly_spend) as avg_spend FROM ("
        "  SELECT strftime('%%Y-%%m', t.date) as month, "
        "  ABS(SUM(t.amount)) as monthly_spend "
        "  FROM t "
        "  WHERE t.amount < 0 "
        "  AND COALESCE(t.category,'') NOT IN "
        "  ('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
        "  AND t.date >= date('now', '-3 months') "
        "  GROUP BY month"
        ")"
    ).fetchone()
    avg_spend = (spend_row["avg_spend"] or 0) if spend_row else 0

    discretionary = avg_income - avg_spend
    return max(0, int(round(discretionary * 100)))


def _check_monthly_review(conn, goal: dict) -> bool:
    """Check if a monthly review is needed for a goal."""
    today = date.today()
    current_month = today.strftime("%Y-%m")

    # Check if there's a snapshot with a note this month
    row = conn.execute(
        "SELECT id FROM goal_snapshots "
        "WHERE goal_id = ? AND snapshot_date LIKE ? AND note IS NOT NULL AND note != ''",
        (goal["id"], current_month + "%"),
    ).fetchone()
    return row is None and today.day >= 1


def _get_linked_account_details(conn, goal: dict) -> list[dict]:
    """Get account details for a goal's linked accounts."""
    linked = json.loads(goal["linked_accounts"] or "[]")
    accounts = []
    for name in linked:
        row = conn.execute(
            "SELECT account_name, balance_cents, account_type, "
            "credit_limit_cents, payment_due_day, payment_amount_cents "
            "FROM account_balances WHERE account_name = ?",
            (name,),
        ).fetchone()
        if row:
            accounts.append(dict(row))
    return accounts




def _get_credit_card_accounts(conn) -> list[dict]:
    """Return credit card accounts with details for goal linking."""
    rows = conn.execute(
        "SELECT account_name, balance_cents, credit_limit_cents, "
        "payment_due_day, payment_amount_cents "
        "FROM account_balances "
        "WHERE account_type = 'credit_card' "
        "ORDER BY sort_order"
    ).fetchall()
    return [dict(r) for r in rows]


def _get_bank_accounts(conn) -> list[dict]:
    """Return bank accounts for savings goal linking."""
    rows = conn.execute(
        "SELECT account_name, balance_cents "
        "FROM account_balances "
        "WHERE account_type = 'bank' "
        "ORDER BY sort_order"
    ).fetchall()
    return [dict(r) for r in rows]


# ── Action Items helpers ─────────────────────────────────────────────────────


def _ordinal(n):
    """Convert day number to ordinal: 1→'1st', 2→'2nd', 3→'3rd', 4→'4th', etc."""
    try:
        n = int(n)
    except (ValueError, TypeError):
        return str(n) if n else ""
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _get_action_items(conn) -> list[dict]:
    """Return all action items ordered: pending first (by sort_order), then completed.

    Recurring items auto-reset to pending at the start of each new month.
    """
    current_month = date.today().strftime("%Y-%m")

    # Auto-reset recurring items completed in a prior month
    conn.execute(
        "UPDATE action_items SET status = 'pending', completed_at = NULL "
        "WHERE is_recurring = 1 AND status = 'completed' "
        "AND (completed_month IS NULL OR completed_month != ?)",
        (current_month,),
    )
    conn.commit()

    rows = conn.execute(
        "SELECT * FROM action_items ORDER BY "
        "CASE status WHEN 'pending' THEN 0 ELSE 1 END, "
        "sort_order, created_at"
    ).fetchall()
    items = [dict(r) for r in rows]
    for item in items:
        if item.get("due_date"):
            item["due_display"] = _ordinal(item["due_date"])
        else:
            item["due_display"] = ""
    return items


def _get_cc_due_items(conn) -> list[dict]:
    """Generate upcoming CC payment due date reminders from account_balances."""
    rows = conn.execute(
        "SELECT account_name, balance_cents, payment_due_day, "
        "payment_amount_cents, payment_due_date "
        "FROM account_balances "
        "WHERE account_type = 'credit_card' "
        "AND payment_due_day IS NOT NULL "
        "AND balance_cents > 0 "
        "ORDER BY payment_due_day"
    ).fetchall()

    today = date.today()
    items = []
    for r in rows:
        due_day = r["payment_due_day"]
        if not due_day or due_day < 1 or due_day > 31:
            continue
        # Compute the next due date
        year, month = today.year, today.month
        max_day = calendar.monthrange(year, month)[1]
        clamped_day = max(1, min(due_day, max_day))
        due_date = date(year, month, clamped_day)
        # If already past this month, use next month
        if due_date < today:
            if month == 12:
                year, month = year + 1, 1
            else:
                month += 1
            max_day = calendar.monthrange(year, month)[1]
            clamped_day = max(1, min(due_day, max_day))
            due_date = date(year, month, clamped_day)

        payment = r["payment_amount_cents"]
        amt_str = "${:,.0f}".format(payment / 100) if payment else "Payment"

        items.append({
            "id": None,
            "title": "{} — {} due".format(r["account_name"], amt_str),
            "status": "pending",
            "due_date": due_date.isoformat(),
            "due_display": due_date.strftime("%b %d"),
            "days_until": (due_date - today).days,
            "auto": True,
            "account_name": r["account_name"],
            "balance_cents": r["balance_cents"],
        })
    items.sort(key=lambda x: x["due_date"])
    return items


# ── Routes ───────────────────────────────────────────────────────────────────


@bp.route("/")
def index():
    """Main Short-Term Planning page."""
    if g.entity_key == "luxelegacy":
        return redirect(url_for("dashboard.index"))

    conn = get_connection(g.entity_key)
    try:
        goals = _get_goals(conn)

        # Auto-snapshot active goals
        for goal in goals:
            try:
                _auto_snapshot(conn, goal)
            except Exception:
                log.exception("Auto-snapshot failed for goal %d", goal["id"])

        # Enrich goals with extra data
        for goal in goals:
            goal["linked_details"] = _get_linked_account_details(conn, goal)
            goal["snapshots"] = _get_snapshots(conn, goal["id"])
            goal["needs_review"] = (
                _check_monthly_review(conn, goal)
                if goal["status"] == "active"
                else False
            )
            # Compute current total balance from linked accounts
            linked = json.loads(goal["linked_accounts"] or "[]")
            total = 0
            for acct in goal["linked_details"]:
                total += abs(acct["balance_cents"])
            goal["current_balance_cents"] = total

            # Compute starting balance (first snapshot)
            if goal["snapshots"]:
                goal["starting_balance_cents"] = goal["snapshots"][0]["balance_cents"]
            else:
                goal["starting_balance_cents"] = total

            # Progress percentage
            start = goal["starting_balance_cents"]
            target = goal["target_amount_cents"] or 0
            if goal["goal_type"] == "debt_payoff":
                # Progress = how much we've reduced from start toward 0
                if start > 0:
                    goal["progress_pct"] = int(
                        round((start - total) / start * 100)
                    )
                else:
                    goal["progress_pct"] = 100
            elif goal["goal_type"] == "savings":
                # Progress = how close to target
                if target > 0:
                    goal["progress_pct"] = int(round(total / target * 100))
                else:
                    goal["progress_pct"] = 0
            else:
                goal["progress_pct"] = 0
            goal["progress_pct"] = max(0, min(100, goal["progress_pct"]))

        # Budget data — month from query param or current month
        today = date.today()
        budget_month = request.args.get("month", today.strftime("%Y-%m"))
        # Validate format
        try:
            bm_date = datetime.strptime(budget_month, "%Y-%m").date()
        except ValueError:
            bm_date = today.replace(day=1)
            budget_month = bm_date.strftime("%Y-%m")

        current_month = budget_month
        month_last_day = calendar.monthrange(bm_date.year, bm_date.month)[1]

        # Build month options for dropdown (current month back 12 months)
        budget_months = []
        d = today.replace(day=1)
        for _ in range(12):
            val = d.strftime("%Y-%m")
            if d.year == today.year:
                label = d.strftime("%B")
            else:
                label = d.strftime("%B %Y")
            budget_months.append({"value": val, "label": label})
            d = (d.replace(day=1) - timedelta(days=1)).replace(day=1)

        budget_status = _get_budget_status(conn, g.entity_key, current_month)
        budget_sections = _group_budget_items(budget_status)

        # Budget summary (only count items that have budgets set)
        budgeted_items = [b for b in budget_status if b["budget_cents"] > 0]
        total_budgeted = sum(b["budget_cents"] for b in budgeted_items)
        total_spent = sum(b["spent_cents"] for b in budgeted_items)
        total_avg_3mo = sum(b.get("avg_3mo_cents", 0) for b in budgeted_items)
        total_remaining = total_budgeted - total_spent
        total_pct = int(total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
        budget_totals = {
            "budgeted_cents": total_budgeted,
            "spent_cents": total_spent,
            "avg_3mo_cents": total_avg_3mo,
            "remaining_cents": total_remaining,
            "pct": total_pct,
        }

        # Action items + CC due dates
        action_items = _get_action_items(conn)
        cc_due_items = _get_cc_due_items(conn)

        # Available accounts for goal creation
        cc_accounts = _get_credit_card_accounts(conn)
        bank_accounts = _get_bank_accounts(conn)
        categories = get_categories(g.entity_key)
        suggested_extra = _suggest_monthly_extra(conn)

        active_goals = [g for g in goals if g["status"] == "active"]
        completed_goals = [g for g in goals if g["status"] == "completed"]
        paused_goals = [g for g in goals if g["status"] == "paused"]

        return render_template(
            "short_term_planning.html",
            active_goals=active_goals,
            completed_goals=completed_goals,
            paused_goals=paused_goals,
            action_items=action_items,
            cc_due_items=cc_due_items,
            budget_status=budget_status,
            budget_sections=budget_sections,
            total_budgeted=total_budgeted,
            total_spent=total_spent,
            budget_totals=budget_totals,
            current_month=current_month,
            current_month_display=bm_date.strftime("%B %Y"),
            budget_months=budget_months,
            cc_accounts=cc_accounts,
            bank_accounts=bank_accounts,
            categories=categories,
            suggested_extra=suggested_extra,
            month_last_day=month_last_day,
        )
    finally:
        conn.close()


@bp.route("/goals/create", methods=["POST"])
def create_goal():
    """Create a new short-term goal."""
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("short_term_planning.index"))

    goal_type = request.form.get("goal_type", "debt_payoff")
    target_cents = _parse_dollar_to_cents(request.form.get("target_amount", "0"))
    target_date = request.form.get("target_date", "").strip() or None
    strategy = request.form.get("strategy", "avalanche") if goal_type == "debt_payoff" else None
    monthly_cents = _parse_dollar_to_cents(request.form.get("monthly_amount", "0"))
    notes = request.form.get("notes", "").strip() or None

    # Linked accounts — multi-select
    linked = request.form.getlist("linked_accounts")
    linked_json = json.dumps(linked) if linked else "[]"

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO short_term_goals "
            "(name, goal_type, target_amount_cents, target_date, strategy, "
            "monthly_amount_cents, linked_accounts, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, goal_type, target_cents, target_date, strategy,
             monthly_cents, linked_json, notes),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/goals/<int:goal_id>/update", methods=["POST"])
def update_goal(goal_id):
    """Update goal settings."""
    name = request.form.get("name", "").strip()
    goal_type = request.form.get("goal_type", "debt_payoff")
    target_cents = _parse_dollar_to_cents(request.form.get("target_amount", "0"))
    target_date = request.form.get("target_date", "").strip() or None
    strategy = request.form.get("strategy", "avalanche") if goal_type == "debt_payoff" else None
    monthly_cents = _parse_dollar_to_cents(request.form.get("monthly_amount", "0"))
    status = request.form.get("status", "active")
    notes = request.form.get("notes", "").strip() or None

    linked = request.form.getlist("linked_accounts")
    linked_json = json.dumps(linked) if linked else "[]"

    completed_at = None
    if status == "completed":
        completed_at = datetime.now(timezone.utc).isoformat()

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "UPDATE short_term_goals SET name = ?, goal_type = ?, "
            "target_amount_cents = ?, target_date = ?, strategy = ?, "
            "monthly_amount_cents = ?, linked_accounts = ?, status = ?, "
            "notes = ?, completed_at = ? WHERE id = ?",
            (name, goal_type, target_cents, target_date, strategy,
             monthly_cents, linked_json, status, notes, completed_at, goal_id),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/goals/<int:goal_id>/delete", methods=["POST"])
def delete_goal(goal_id):
    """Delete a goal and its snapshots (CASCADE)."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM short_term_goals WHERE id = ?", (goal_id,))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/goals/<int:goal_id>/snapshot", methods=["POST"])
def record_snapshot(goal_id):
    """Record a manual progress snapshot with optional note."""
    note = request.form.get("note", "").strip() or None
    conn = get_connection(g.entity_key)
    try:
        goal = _get_goal(conn, goal_id)
        if not goal:
            return redirect(url_for("short_term_planning.index"))

        # Get current balance
        linked = json.loads(goal["linked_accounts"] or "[]")
        total = 0
        for name in linked:
            row = conn.execute(
                "SELECT balance_cents FROM account_balances WHERE account_name = ?",
                (name,),
            ).fetchone()
            if row:
                total += abs(row["balance_cents"])

        today_str = date.today().isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO goal_snapshots "
            "(goal_id, snapshot_date, balance_cents, note) VALUES (?, ?, ?, ?)",
            (goal_id, today_str, total, note),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/goals/<int:goal_id>/lock-plan", methods=["POST"])
def lock_plan(goal_id):
    """Save locked-in plan details to goal."""
    strategy = request.form.get("strategy", "avalanche")
    monthly_cents = _parse_dollar_to_cents(request.form.get("monthly_amount", "0"))
    target_date = request.form.get("target_date", "").strip() or None
    narrative = request.form.get("narrative", "").strip() or ""

    conn = get_connection(g.entity_key)
    try:
        goal = _get_goal(conn, goal_id)
        if not goal:
            return redirect(url_for("short_term_planning.index"))

        # Compute payoff timeline if debt_payoff
        ai_plan = narrative
        if goal["goal_type"] == "debt_payoff":
            accounts = _get_linked_account_details(conn, goal)
            acct_data = []
            for a in accounts:
                if a["account_type"] == "credit_card":
                    # Estimate min payment as 2% of balance or $25
                    bal = abs(a["balance_cents"])
                    min_pay = max(2500, int(bal * 0.02))
                    rate_row = conn.execute(
                        "SELECT credit_limit_cents FROM account_balances WHERE account_name = ?",
                        (a["account_name"],),
                    ).fetchone()
                    # Use a default rate if we don't have one stored
                    acct_data.append({
                        "name": a["account_name"],
                        "balance_cents": bal,
                        "rate_bps": 2000,  # default 20% APR
                        "min_payment_cents": min_pay,
                    })

            if acct_data:
                timeline = _compute_payoff_timeline(acct_data, monthly_cents, strategy)
                if timeline:
                    # Generate schedule markdown
                    schedule_lines = ["\n\n## Payoff Schedule\n"]
                    header = "| Month | " + " | ".join(a["name"] for a in acct_data) + " | Total | Interest |"
                    divider = "|---|" + "|".join("---" for _ in acct_data) + "|---|---|"
                    schedule_lines.append(header)
                    schedule_lines.append(divider)

                    for snap in timeline[:24]:  # Show max 24 months
                        row_parts = ["| %d" % snap["month"]]
                        for a in acct_data:
                            bal = snap["accounts"].get(a["name"], 0)
                            row_parts.append("$%s" % "{:,.0f}".format(bal / 100))
                        row_parts.append("$%s" % "{:,.0f}".format(snap["total_cents"] / 100))
                        row_parts.append("$%s" % "{:,.0f}".format(snap["cumulative_interest_cents"] / 100))
                        schedule_lines.append(" | ".join(row_parts) + " |")

                    ai_plan += "\n".join(schedule_lines)

        conn.execute(
            "UPDATE short_term_goals SET strategy = ?, monthly_amount_cents = ?, "
            "target_date = ?, ai_plan = ? WHERE id = ?",
            (strategy, monthly_cents, target_date, ai_plan, goal_id),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/goals/<int:goal_id>/progress")
def goal_progress(goal_id):
    """HTMX partial: progress chart data for a goal."""
    conn = get_connection(g.entity_key)
    try:
        goal = _get_goal(conn, goal_id)
        if not goal:
            return ""
        snapshots = _get_snapshots(conn, goal_id)

        # Build simple SVG sparkline data
        if len(snapshots) < 2:
            return '<div class="stp-empty">Not enough data yet</div>'

        values = [s["balance_cents"] for s in snapshots]
        max_val = max(values) if values else 1
        min_val = min(values) if values else 0
        val_range = max_val - min_val or 1

        width = 300
        height = 60
        points = []
        for i, v in enumerate(values):
            x = int(i / max(len(values) - 1, 1) * width)
            y = int(height - (v - min_val) / val_range * height)
            points.append(f"{x},{y}")

        polyline = " ".join(points)
        svg = (
            f'<svg class="stp-sparkline" viewBox="0 0 {width} {height}" '
            f'preserveAspectRatio="none">'
            f'<polyline points="{polyline}" fill="none" '
            f'stroke="var(--blue)" stroke-width="2" />'
            f'</svg>'
        )
        return svg
    finally:
        conn.close()


@bp.route("/budget/save", methods=["POST"])
def save_budget():
    """Save/update budget amounts from the budget table."""
    conn = get_connection(g.entity_key)
    try:
        for key, value in request.form.items():
            if key.startswith("subbudget_"):
                # Subcategory budget: subbudget_{category}__{subcategory}
                rest = key[10:]  # strip 'subbudget_' prefix
                parts = rest.split("__", 1)
                if len(parts) != 2:
                    continue
                category, subcategory = parts
                cents = _parse_dollar_to_cents(value)
                if cents > 0:
                    conn.execute(
                        "INSERT OR REPLACE INTO budget_subcategories "
                        "(category, subcategory, monthly_budget_cents) VALUES (?, ?, ?)",
                        (category, subcategory, cents),
                    )
                else:
                    conn.execute(
                        "DELETE FROM budget_subcategories "
                        "WHERE category = ? AND subcategory = ?",
                        (category, subcategory),
                    )
            elif key.startswith("budget_"):
                category = key[7:]  # strip 'budget_' prefix
                cents = _parse_dollar_to_cents(value)
                if cents > 0:
                    # Check if this is a per-payroll category
                    existing = conn.execute(
                        "SELECT is_per_payroll FROM budget_items WHERE category = ?",
                        (category,),
                    ).fetchone()
                    if existing and existing["is_per_payroll"]:
                        # Value is per-payroll amount; store it and
                        # set monthly_budget_cents = per_payroll * 2 as default
                        conn.execute(
                            "UPDATE budget_items SET per_payroll_cents = ?, "
                            "monthly_budget_cents = ? WHERE category = ?",
                            (cents, cents * 2, category),
                        )
                    else:
                        # Standard category — update existing or insert new
                        cur = conn.execute(
                            "UPDATE budget_items SET monthly_budget_cents = ? "
                            "WHERE category = ?",
                            (cents, category),
                        )
                        if cur.rowcount == 0:
                            conn.execute(
                                "INSERT INTO budget_items (category, monthly_budget_cents) "
                                "VALUES (?, ?)",
                                (category, cents),
                            )
                else:
                    conn.execute(
                        "DELETE FROM budget_items WHERE category = ?",
                        (category,),
                    )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/budget/status")
def budget_status():
    """HTMX partial: budget vs actuals for current month."""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    conn = get_connection(g.entity_key)
    try:
        status = _get_budget_status(conn, g.entity_key, month)
        # Return as HTML table rows
        html_parts = []
        for item in status:
            pct = item["pct"]
            if pct <= 75:
                color_class = "stp-budget-green"
            elif pct <= 100:
                color_class = "stp-budget-yellow"
            else:
                color_class = "stp-budget-red"

            html_parts.append(
                f'<tr class="{color_class}">'
                f'<td>{escape(item["category"])}</td>'
                f'<td>${item["budget_cents"] / 100:,.0f}</td>'
                f'<td>${item["spent_cents"] / 100:,.0f}</td>'
                f'<td>${item["remaining_cents"] / 100:,.0f}</td>'
                f'<td><div class="stp-budget-bar"><div class="stp-budget-fill" '
                f'style="width: {min(pct, 100)}%"></div></div></td>'
                f'</tr>'
            )
        return "".join(html_parts)
    finally:
        conn.close()


# ── Action Items ─────────────────────────────────────────────────────────────


@bp.route("/actions/create", methods=["POST"])
def create_action():
    """Add a new action item."""
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("short_term_planning.index"))

    due_date = request.form.get("due_date", "").strip() or None

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO action_items (title, due_date) VALUES (?, ?)",
            (title, due_date),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/actions/<int:item_id>/toggle", methods=["POST"])
def toggle_action(item_id):
    """Toggle action item between pending and completed."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT status, is_recurring FROM action_items WHERE id = ?", (item_id,)
        ).fetchone()
        if row:
            new_status = "completed" if row["status"] == "pending" else "pending"
            completed_at = datetime.now(timezone.utc).isoformat() if new_status == "completed" else None
            completed_month = date.today().strftime("%Y-%m") if new_status == "completed" and row["is_recurring"] else None
            conn.execute(
                "UPDATE action_items SET status = ?, completed_at = ?, completed_month = ? WHERE id = ?",
                (new_status, completed_at, completed_month, item_id),
            )
            conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


@bp.route("/actions/<int:item_id>/delete", methods=["POST"])
def delete_action(item_id):
    """Delete an action item."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM action_items WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("short_term_planning.index"))


# ── Budget Drill-Down ────────────────────────────────────────────────────────


def _render_budget_transactions(conn, category, subcategory, month):
    """Build HTML table of transactions for a category drill-down (reusable)."""
    from markupsafe import escape
    import json as _json

    _cte = effective_txns_cte("t")
    if subcategory:
        rows = conn.execute(
            f"WITH {_cte} "
            "SELECT t.transaction_id, t.date, t.description_raw, t.merchant_canonical, "
            "t.amount, t.category, t.subcategory "
            "FROM t "
            "WHERE t.category = ? "
            "AND COALESCE(NULLIF(t.subcategory,''), 'General') = ? "
            "AND strftime('%Y-%m', t.date) = ? "
            "AND t.amount < 0 "
            "ORDER BY t.date DESC",
            (category, subcategory, month),
        ).fetchall()
    else:
        rows = conn.execute(
            f"WITH {_cte} "
            "SELECT t.transaction_id, t.date, t.description_raw, t.merchant_canonical, "
            "t.amount, t.category, t.subcategory "
            "FROM t "
            "WHERE t.category = ? "
            "AND strftime('%Y-%m', t.date) = ? "
            "AND t.amount < 0 "
            "ORDER BY t.date DESC",
            (category, month),
        ).fetchall()

    lines = []
    if not rows:
        lines.append('<div class="stp-drill-empty">No transactions</div>')
    else:
        lines.append('<table class="stp-drill-table">')
        lines.append(
            "<thead><tr><th>Date</th><th>Description</th>"
            "<th>Sub</th><th>Amount</th></tr></thead><tbody>"
        )
        for r in rows:
            txn_id = r["transaction_id"]
            desc = r["merchant_canonical"] or r["description_raw"] or ""
            if len(desc) > 45:
                desc = desc[:42] + "\u2026"
            amt = abs(r["amount"])
            cat_val = r["category"] or ""
            sub_val = r["subcategory"] or "General"
            # Use &quot; for quotes inside onclick HTML attribute
            cat_attr = escape(cat_val).replace("'", "&#39;")
            sub_attr = escape(sub_val).replace("'", "&#39;")
            txn_attr = escape(txn_id).replace("'", "&#39;")
            lines.append(
                f'<tr id="stp-txnr-{escape(txn_id)}" class="stp-drill-row" '
                f"onclick=\"stpEditTxn(this,'{txn_attr}','{cat_attr}','{sub_attr}')\">"
                f"<td>{r['date'][5:]}</td>"
                f"<td>{escape(desc)}</td>"
                f"<td>{escape(sub_val)}</td>"
                f"<td>${amt:,.2f}</td></tr>"
            )
        lines.append("</tbody></table>")
        lines.append(
            '<div class="stp-drill-hint">Tap a row to change its category</div>'
        )

    return "\n".join(lines)


@bp.route("/budget/transactions")
def budget_transactions():
    """Return HTML partial of transactions for a category in the current month."""
    category = request.args.get("category", "")
    subcategory = request.args.get("subcategory", "")
    month = request.args.get("month", date.today().strftime("%Y-%m"))

    conn = get_connection(g.entity_key)
    try:
        return _render_budget_transactions(conn, category, subcategory, month)
    finally:
        conn.close()


@bp.route("/budget/update-txn/<txn_id>", methods=["POST"])
def budget_update_txn(txn_id):
    """Update a transaction's category/subcategory from the budget drill-down."""
    new_category = request.form.get("category", "").strip()
    new_subcategory = request.form.get("subcategory", "").strip() or "General"
    orig_category = request.form.get("orig_category", "")
    orig_subcategory = request.form.get("orig_subcategory", "")
    month = request.form.get("month", date.today().strftime("%Y-%m"))

    if not new_category:
        return "Missing category", 400

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "UPDATE transactions SET category=?, subcategory=?, confidence=1.0 "
            "WHERE transaction_id=?",
            (new_category, new_subcategory, txn_id),
        )
        conn.commit()

        # Return refreshed drill-down for the ORIGINAL category
        html = _render_budget_transactions(conn, orig_category, orig_subcategory, month)
        resp = make_response(html)
        resp.headers["HX-Trigger"] = "stpBudgetChanged"
        return resp
    finally:
        conn.close()


@bp.route("/budget/subcategories")
def budget_subcategories():
    """Return HTML partial of subcategory breakdown for a category.

    Shows ALL defined subcategories (even at $0 spending).
    """
    category = request.args.get("category", "")
    month = request.args.get("month", date.today().strftime("%Y-%m"))

    conn = get_connection(g.entity_key)
    _cte = effective_txns_cte("t")
    try:
        # 1. All defined subcategories for this category
        defined = conn.execute(
            "SELECT name FROM subcategories WHERE category_name = ? ORDER BY name",
            (category,),
        ).fetchall()
        all_subs = {r["name"] for r in defined}
        all_subs.add("General")  # always include General

        # 2. Actual spending by subcategory
        spend_map = {}  # sub_name -> spent_dollars
        if category == "Payroll":
            # Special case: Payroll — use payroll_entries grouped by employee role
            try:
                payroll_rows = conn.execute(
                    "SELECT e.role as sub, COUNT(DISTINCT e.id) as cnt, "
                    "SUM(pe.amount_cents) / 100.0 as total "
                    "FROM payroll_entries pe "
                    "JOIN employees e ON pe.employee_id = e.id "
                    "WHERE strftime('%Y-%m', pe.paycheck_date) = ? "
                    "GROUP BY e.role "
                    "ORDER BY total DESC",
                    (month,),
                ).fetchall()
                if payroll_rows:
                    for r in payroll_rows:
                        spend_map[r["sub"]] = r["total"]
                        all_subs.add(r["sub"])
            except Exception:
                pass

        if not spend_map:
            txn_rows = conn.execute(
                f"WITH {_cte} "
                "SELECT COALESCE(NULLIF(t.subcategory,''), 'General') as sub, "
                "ABS(SUM(t.amount)) as total "
                "FROM t "
                "WHERE t.category = ? "
                "AND strftime('%Y-%m', t.date) = ? "
                "AND t.amount < 0 "
                "GROUP BY sub",
                (category, month),
            ).fetchall()
            for r in txn_rows:
                spend_map[r["sub"]] = r["total"]
                all_subs.add(r["sub"])  # include even if not in subcategories table

        # 3. Subcategory budgets
        budget_rows = conn.execute(
            "SELECT subcategory, monthly_budget_cents FROM budget_subcategories "
            "WHERE category = ?",
            (category,),
        ).fetchall()
        sub_budgets = {r["subcategory"]: r["monthly_budget_cents"] for r in budget_rows}

        # 4. 3-month average by subcategory (same logic as category-level)
        try:
            bm = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            bm = date.today().replace(day=1)
        avg_months = []
        d = bm
        for _ in range(3):
            d = (d.replace(day=1) - timedelta(days=1)).replace(day=1)
            avg_months.append(d.strftime("%Y-%m"))
        mp = ",".join("?" for _ in avg_months)
        avg_rows = conn.execute(
            f"WITH {_cte} "
            "SELECT COALESCE(NULLIF(t.subcategory,''), 'General') as sub, "
            "ABS(SUM(t.amount)) as total, "
            "COUNT(DISTINCT strftime('%%Y-%%m', t.date)) as month_count "
            "FROM t "
            "WHERE t.category = ? "
            "AND strftime('%%Y-%%m', t.date) IN (%s) "
            "AND t.amount < 0 "
            "GROUP BY sub" % mp,
            (category, *avg_months),
        ).fetchall()
        avg_map = {}  # sub -> avg cents
        avg_mc_map = {}  # sub -> month count
        for r in avg_rows:
            mc = r["month_count"]
            avg_map[r["sub"]] = int(round(r["total"] * 100 / max(mc, 1)))
            avg_mc_map[r["sub"]] = mc

        # 5. Build sorted list: spent desc, then alphabetical for $0 items
        sorted_subs = sorted(all_subs, key=lambda s: (-spend_map.get(s, 0), s))

        import json
        from markupsafe import escape

        lines = []
        for sub_name in sorted_subs:
            amt = spend_map.get(sub_name, 0)
            spent_cents = int(round(amt * 100))
            sub_esc = escape(sub_name)
            cat_js = escape(json.dumps(category))
            sub_js = escape(json.dumps(sub_name))
            field_name = escape(f"subbudget_{category}__{sub_name}")
            budget_cents = sub_budgets.get(sub_name)

            # 3-mo avg for this subcategory
            sub_avg = avg_map.get(sub_name, 0)
            sub_mc = avg_mc_map.get(sub_name, 0)
            avg_over = (
                "stp-avg--over"
                if budget_cents and budget_cents > 0 and sub_avg > budget_cents * 1.1
                else ""
            )
            mc_note = f'<span class="stp-avg-note">{sub_mc}mo</span>' if sub_mc < 3 else ""
            avg_td = (
                f'<td class="stp-avg {avg_over}">'
                f'${sub_avg / 100:,.0f}{mc_note}</td>'
            )

            # Spent cell (always clickable)
            spent_td = (
                f'<td><span class="stp-spent-link" '
                f'onclick="stpShowTxns({cat_js}, {sub_js})">${amt:,.0f}</span></td>'
            )

            if budget_cents and budget_cents > 0:
                # Has subcategory budget — show input, remaining, progress
                remaining = budget_cents - spent_cents
                pct = int(round(spent_cents / budget_cents * 100))
                budget_val = f"{budget_cents / 100:,.0f}"
                rem_class = "stp-green" if remaining >= -100 else "stp-red"
                bar_class = (
                    "stp-bar-green" if pct <= 100
                    else "stp-bar-yellow" if pct <= 115
                    else "stp-bar-red"
                )
                lines.append(
                    f'<tr class="stp-subcat-row">'
                    f'<td style="padding-left:2rem;color:var(--text-muted)">{sub_esc}</td>'
                    f'{spent_td}'
                    f'<td><span class="stp-budget-input-wrap stp-budget-input-wrap--sub">$'
                    f'<input type="text" name="{field_name}" value="{budget_val}" '
                    f'size="{len(budget_val)}" class="stp-budget-input stp-budget-input--sub"></span></td>'
                    f'{avg_td}'
                    f'<td class="{rem_class}">${remaining / 100:,.0f}</td>'
                    f'<td><div class="stp-budget-progress-wrap">'
                    f'<div class="stp-budget-bar stp-budget-bar--sub">'
                    f'<div class="stp-budget-fill {bar_class}" style="width:{min(pct, 100)}%"></div></div>'
                    f'<span class="stp-budget-pct">{min(pct, 999)}%</span></div></td>'
                    f'</tr>'
                )
            else:
                # No budget — empty input with dash placeholder
                lines.append(
                    f'<tr class="stp-subcat-row">'
                    f'<td style="padding-left:2rem;color:var(--text-muted)">{sub_esc}</td>'
                    f'{spent_td}'
                    f'<td><span class="stp-budget-input-wrap stp-budget-input-wrap--sub">$'
                    f'<input type="text" name="{field_name}" value="" '
                    f'placeholder="\u2014" size="3" '
                    f'class="stp-budget-input stp-budget-input--sub"></span></td>'
                    f'{avg_td}'
                    f'<td></td>'
                    f'<td></td>'
                    f'</tr>'
                )

        return "\n".join(lines)
    finally:
        conn.close()

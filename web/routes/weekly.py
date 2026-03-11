"""Weekly Check-In — spending pulse and upcoming bills."""
from __future__ import annotations

import calendar
import logging
from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, g, redirect, url_for

from core.db import get_connection
from core.reporting import effective_txns_cte, EXCLUDE_CATS, exclude_sql

log = logging.getLogger(__name__)

bp = Blueprint("weekly", __name__, url_prefix="/weekly")

_EXCLUDE_CATS = EXCLUDE_CATS

# Day-of-week names for bill display
_DOW_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ── Week math helpers ────────────────────────────────────────────────────────


def _week_bounds(week_str: str) -> tuple[date, date]:
    """Convert ISO week string like '2026-W11' to (monday, sunday) dates."""
    monday = datetime.strptime(week_str + "-1", "%G-W%V-%u").date()
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _current_week() -> str:
    """Return current ISO week string like '2026-W11'."""
    return date.today().strftime("%G-W%V")


def _prev_week(week_str: str) -> str:
    monday, _ = _week_bounds(week_str)
    prev = monday - timedelta(days=7)
    return prev.strftime("%G-W%V")


def _next_week(week_str: str) -> str:
    monday, _ = _week_bounds(week_str)
    nxt = monday + timedelta(days=7)
    return nxt.strftime("%G-W%V")


def _format_week_range(monday: date, sunday: date) -> str:
    """Format week range for display: 'Mar 2 – 8' or 'Mar 30 – Apr 5'."""
    if monday.month == sunday.month:
        return f"{monday.strftime('%b')} {monday.day} – {sunday.day}"
    return f"{monday.strftime('%b')} {monday.day} – {sunday.strftime('%b')} {sunday.day}"


def _days_in_month(d: date) -> int:
    return calendar.monthrange(d.year, d.month)[1]


# ── Data queries ─────────────────────────────────────────────────────────────


def _get_weekly_spending(conn, week_start: str, week_end: str) -> list[dict]:
    """Sum spending by category for a date range. Returns list of dicts."""
    cte = effective_txns_cte("t")
    exclude = exclude_sql("t.category")
    rows = conn.execute(
        f"WITH {cte} "
        "SELECT COALESCE(NULLIF(t.category,''),'Uncategorized') as category, "
        "ABS(SUM(t.amount)) as total, "
        "COUNT(*) as txn_count "
        "FROM t "
        f"WHERE t.date >= ? AND t.date <= ? AND t.amount < 0 AND {exclude} "
        "GROUP BY category ORDER BY total DESC",
        (week_start, week_end),
    ).fetchall()
    return [
        {"category": r["category"], "total_cents": int(round(r["total"] * 100)), "txn_count": r["txn_count"]}
        for r in rows
    ]


def _get_mtd_spending(conn, month_start: str, through_date: str) -> int:
    """Total spending from month start through a date (cents)."""
    cte = effective_txns_cte("t")
    exclude = exclude_sql("t.category")
    row = conn.execute(
        f"WITH {cte} "
        "SELECT ABS(SUM(t.amount)) as total "
        "FROM t "
        f"WHERE t.date >= ? AND t.date <= ? AND t.amount < 0 AND {exclude}",
        (month_start, through_date),
    ).fetchone()
    return int(round((row["total"] or 0) * 100))


def _compute_weekly_pace(budget_status: list) -> int:
    """Derive weekly budget from monthly totals. Returns cents."""
    total_monthly = sum(b["budget_cents"] for b in budget_status if b["budget_cents"] > 0)
    # Use current month's day count
    today = date.today()
    dim = _days_in_month(today)
    return int(round(total_monthly * 7 / dim))


def _compute_category_paces(budget_status: list) -> dict[str, int]:
    """Map category → weekly pace in cents."""
    today = date.today()
    dim = _days_in_month(today)
    paces = {}
    for b in budget_status:
        if b["budget_cents"] > 0:
            paces[b["category"]] = int(round(b["budget_cents"] * 7 / dim))
    return paces


def _compute_burn_rate(spent_mtd: int, days_elapsed: int, days_in_month: int, monthly_budget: int) -> dict:
    """Project end-of-month position at current daily spending rate."""
    if days_elapsed <= 0:
        return {"projected_cents": 0, "over_under_cents": monthly_budget, "on_track": True}
    daily_rate = spent_mtd / days_elapsed
    projected = int(round(daily_rate * days_in_month))
    over_under = monthly_budget - projected
    return {
        "projected_cents": projected,
        "over_under_cents": over_under,
        "on_track": over_under >= 0,
    }


def _get_weekly_bills(conn, entity_key: str, week_start: date, week_end: date) -> list[dict]:
    """Aggregate all bills due in the week from multiple sources."""
    from web.routes.short_term_planning import _get_action_items, _get_cc_due_items, _get_payroll_schedule, _count_pay_periods

    bills = []

    # 1. Action items with due_date (day-of-month) falling in the week
    action_items = _get_action_items(conn)
    for item in action_items:
        if item["status"] != "pending":
            continue
        due_day = item.get("due_date")
        if not due_day:
            continue
        try:
            due_day = int(due_day)
        except (ValueError, TypeError):
            continue
        # Check if this day-of-month falls within the week
        for d in _iter_days(week_start, week_end):
            if d.day == due_day:
                bills.append({
                    "type": "action_item",
                    "merchant": item["title"],
                    "amount_cents": None,
                    "date": d,
                    "day_name": _DOW_NAMES[d.weekday()],
                    "source": "Manual Pay",
                })
                break

    # 2. Auto-detected recurring charges
    from web.routes.cashflow import _detect_upcoming_for_account
    acct_rows = conn.execute(
        "SELECT id, account_name, plaid_account_id FROM account_balances ORDER BY sort_order"
    ).fetchall()
    seen_merchants = set()
    for acct in acct_rows:
        names = [acct["account_name"]]
        if acct["plaid_account_id"]:
            # Get all account name aliases for this Plaid account
            alias_rows = conn.execute(
                "SELECT DISTINCT account FROM transactions WHERE account IN ("
                "SELECT account_name FROM account_balances WHERE plaid_account_id = ?)",
                (acct["plaid_account_id"],),
            ).fetchall()
            if alias_rows:
                names = list({r["account"] for r in alias_rows})
        auto = _detect_upcoming_for_account(conn, names, horizon_days=30)
        for item in auto:
            exp = _parse_date(item["expected_date"])
            if exp and week_start <= exp <= week_end and item["merchant"] not in seen_merchants:
                seen_merchants.add(item["merchant"])
                bills.append({
                    "type": "recurring",
                    "merchant": item["merchant"],
                    "amount_cents": item["amount_cents"],
                    "date": exp,
                    "day_name": _DOW_NAMES[exp.weekday()],
                    "source": item.get("cadence", "Recurring"),
                })

    # 3. Manual recurring charges
    from web.routes.cashflow import _get_manual_recurring
    for acct in acct_rows:
        manual = _get_manual_recurring(conn, acct["id"])
        for item in manual:
            exp = _parse_date(item["expected_date"])
            if exp and week_start <= exp <= week_end and item["merchant"] not in seen_merchants:
                seen_merchants.add(item["merchant"])
                bills.append({
                    "type": "manual_recurring",
                    "merchant": item["merchant"],
                    "amount_cents": item["amount_cents"],
                    "date": exp,
                    "day_name": _DOW_NAMES[exp.weekday()],
                    "source": "Recurring",
                })

    # 4. Credit card due dates
    cc_items = _get_cc_due_items(conn)
    for item in cc_items:
        exp = _parse_date(item["due_date"])
        if exp and week_start <= exp <= week_end:
            bills.append({
                "type": "cc_payment",
                "merchant": item["title"],
                "amount_cents": item.get("balance_cents"),
                "date": exp,
                "day_name": _DOW_NAMES[exp.weekday()],
                "source": "CC Payment",
            })

    # 5. BFM payroll dates
    schedule = _get_payroll_schedule(conn)
    if schedule:
        anchor = datetime.strptime(schedule["anchor_date"], "%Y-%m-%d").date()
        cadence = schedule["cadence_days"]
        # Walk from anchor to find paydays in the week
        d = anchor
        while d < week_start:
            d += timedelta(days=cadence)
        while d > week_end:
            d -= timedelta(days=cadence)
        # Check if any payday falls in range
        while d <= week_end:
            if d >= week_start:
                bills.append({
                    "type": "payroll",
                    "merchant": "Payroll",
                    "amount_cents": None,
                    "date": d,
                    "day_name": _DOW_NAMES[d.weekday()],
                    "source": "Payroll",
                })
            d += timedelta(days=cadence)

    bills.sort(key=lambda b: b["date"])
    return bills


def _iter_days(start: date, end: date):
    """Yield each date from start to end inclusive."""
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _parse_date(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _get_cc_balances(conn) -> list[dict]:
    """Get all credit cards with balances."""
    rows = conn.execute(
        "SELECT account_name, balance_cents, credit_limit_cents "
        "FROM account_balances "
        "WHERE account_type = 'credit_card' AND balance_cents > 0 "
        "ORDER BY balance_cents DESC"
    ).fetchall()
    result = []
    for r in rows:
        balance = r["balance_cents"]
        limit_cents = r["credit_limit_cents"] or 0
        pct = int(round(balance / limit_cents * 100)) if limit_cents > 0 else 0
        result.append({
            "name": r["account_name"],
            "balance_cents": balance,
            "limit_cents": limit_cents,
            "pct": min(pct, 100),
        })
    return result


def _get_paydown_goal(conn) -> dict | None:
    """Get CC paydown goal (singleton)."""
    row = conn.execute(
        "SELECT target_date, start_date, start_balance_cents FROM cc_paydown_goal WHERE id = 1"
    ).fetchone()
    if not row:
        return None
    return {
        "target_date": row["target_date"],
        "start_date": row["start_date"],
        "start_balance_cents": row["start_balance_cents"],
    }


def _compute_paydown_pace(goal: dict, current_total: int, today: date) -> dict:
    """Compute whether actual CC paydown is on pace vs linear target."""
    start = datetime.strptime(goal["start_date"], "%Y-%m-%d").date()
    target = datetime.strptime(goal["target_date"], "%Y-%m-%d").date()
    start_bal = goal["start_balance_cents"]

    total_days = (target - start).days
    if total_days <= 0:
        return {"on_pace": current_total <= 0, "expected_cents": 0, "pct_complete": 100}

    days_elapsed = (today - start).days
    if days_elapsed < 0:
        days_elapsed = 0

    expected = int(round(start_bal * (1 - days_elapsed / total_days)))
    if expected < 0:
        expected = 0

    pct_complete = int(round((1 - current_total / start_bal) * 100)) if start_bal > 0 else 100
    if pct_complete < 0:
        pct_complete = 0

    return {
        "on_pace": current_total <= expected,
        "expected_cents": expected,
        "pct_complete": min(pct_complete, 100),
        "days_remaining": max((target - today).days, 0),
        "target_date": goal["target_date"],
    }


def _compute_warnings(spending: list[dict], category_paces: dict) -> list[str]:
    """Generate up to 3 warning strings for categories significantly over weekly pace."""
    warnings = []
    for item in spending:
        cat = item["category"]
        pace = category_paces.get(cat, 0)
        if pace <= 0:
            continue
        spent = item["total_cents"]
        if spent > pace * 1.5:
            warnings.append(
                f"{cat} was ${spent / 100:,.0f} last week — weekly pace is ${pace / 100:,.0f}"
            )
        if len(warnings) >= 3:
            break
    return warnings


# ── Route ────────────────────────────────────────────────────────────────────


@bp.route("/paydown-goal", methods=["POST"])
def save_paydown_goal():
    """Save or update CC paydown target date."""
    if g.entity_key == "luxelegacy":
        return redirect(url_for("dashboard.index"))

    target_date = request.form.get("target_date", "").strip()
    week_str = request.form.get("week", _current_week())

    if target_date:
        conn = get_connection(g.entity_key)
        try:
            # Get current total CC debt
            cards = _get_cc_balances(conn)
            total = sum(c["balance_cents"] for c in cards)
            today = date.today()

            # Check if goal already exists — preserve start values if so
            existing = _get_paydown_goal(conn)
            if existing:
                conn.execute(
                    "UPDATE cc_paydown_goal SET target_date = ? WHERE id = 1",
                    (target_date,),
                )
            else:
                conn.execute(
                    "INSERT INTO cc_paydown_goal (id, target_date, start_date, start_balance_cents) "
                    "VALUES (1, ?, ?, ?)",
                    (target_date, today.isoformat(), total),
                )
            conn.commit()
        finally:
            conn.close()

    return redirect(url_for("weekly.index", week=week_str))


@bp.route("/")
def index():
    if g.entity_key == "luxelegacy":
        return redirect(url_for("dashboard.index"))

    from web.routes.short_term_planning import _get_budget_status

    week_str = request.args.get("week", _current_week())
    # Validate week string
    try:
        monday, sunday = _week_bounds(week_str)
    except (ValueError, KeyError):
        week_str = _current_week()
        monday, sunday = _week_bounds(week_str)

    today = date.today()
    conn = get_connection(g.entity_key)
    try:
        # ── Determine which week's data to show ──
        # Use the Monday's month for budget computation
        budget_month = monday.strftime("%Y-%m")
        budget_status = _get_budget_status(conn, g.entity_key, budget_month)
        weekly_pace = _compute_weekly_pace(budget_status)
        category_paces = _compute_category_paces(budget_status)

        # ── This Week's KPIs ──
        week_spending = _get_weekly_spending(
            conn, monday.isoformat(), sunday.isoformat()
        )
        spent_cents = sum(s["total_cents"] for s in week_spending)
        remaining_cents = weekly_pace - spent_cents

        # ── This Week's Bills ──
        bills = _get_weekly_bills(conn, g.entity_key, monday, sunday)
        bills_total = sum(b["amount_cents"] for b in bills if b["amount_cents"])

        # ── Last Week Scorecard ──
        last_monday = monday - timedelta(days=7)
        last_sunday = monday - timedelta(days=1)
        last_week_spending = _get_weekly_spending(
            conn, last_monday.isoformat(), last_sunday.isoformat()
        )
        last_week_total = sum(s["total_cents"] for s in last_week_spending)
        last_week_top5 = last_week_spending[:5]

        # Attach pace info to each category
        for item in last_week_top5:
            pace = category_paces.get(item["category"], 0)
            item["pace_cents"] = pace
            if pace > 0:
                item["pct"] = int(round(item["total_cents"] / pace * 100))
            else:
                item["pct"] = 0

        # Burn rate: based on month-to-date spending through last Sunday
        monthly_budget = sum(b["budget_cents"] for b in budget_status if b["budget_cents"] > 0)
        month_start = last_monday.replace(day=1)
        # How far into the month are we? Use the end of the viewed week or today, whichever is earlier
        mtd_end = min(sunday, today)
        if mtd_end < month_start:
            mtd_end = month_start
        spent_mtd = _get_mtd_spending(conn, month_start.isoformat(), mtd_end.isoformat())
        days_elapsed = (mtd_end - month_start).days + 1
        dim = _days_in_month(month_start)
        burn_rate = _compute_burn_rate(spent_mtd, days_elapsed, dim, monthly_budget)

        # Warnings for last week
        # Use the last-week budget month for paces
        last_budget_month = last_monday.strftime("%Y-%m")
        if last_budget_month != budget_month:
            last_budget_status = _get_budget_status(conn, g.entity_key, last_budget_month)
            last_category_paces = _compute_category_paces(last_budget_status)
        else:
            last_category_paces = category_paces
        warnings = _compute_warnings(last_week_spending, last_category_paces)

        # ── Credit Card Paydown ──
        cc_cards = _get_cc_balances(conn)
        cc_total = sum(c["balance_cents"] for c in cc_cards)
        paydown_goal = _get_paydown_goal(conn)
        paydown_pace = None
        if paydown_goal:
            paydown_pace = _compute_paydown_pace(paydown_goal, cc_total, today)

        # Navigation
        is_current = week_str == _current_week()
        prev_w = _prev_week(week_str)
        next_w = _next_week(week_str) if not is_current else None

        return render_template(
            "weekly.html",
            week_str=week_str,
            week_label=_format_week_range(monday, sunday),
            monday=monday,
            sunday=sunday,
            prev_week=prev_w,
            next_week=next_w,
            is_current=is_current,
            # KPIs
            spent_cents=spent_cents,
            weekly_pace=weekly_pace,
            remaining_cents=remaining_cents,
            # Bills
            bills=bills,
            bills_total=bills_total,
            # Last week
            last_week_label=_format_week_range(last_monday, last_sunday),
            last_week_total=last_week_total,
            last_week_pace=weekly_pace,
            last_week_top5=last_week_top5,
            burn_rate=burn_rate,
            monthly_budget=monthly_budget,
            budget_month_name=monday.strftime("%B"),
            warnings=warnings,
            # Drill-through dates
            last_monday=last_monday.isoformat(),
            last_sunday=last_sunday.isoformat(),
            # CC Paydown
            cc_cards=cc_cards,
            cc_total=cc_total,
            paydown_goal=paydown_goal,
            paydown_pace=paydown_pace,
        )
    finally:
        conn.close()

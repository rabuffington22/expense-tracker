"""Waterfall — BFM surplus to personal debt paydown."""
from __future__ import annotations

import logging
from datetime import date, timedelta

from flask import Blueprint, render_template, request, g, redirect, url_for

from core.db import get_connection, init_db
from core.reporting import (
    effective_txns_cte,
    exclude_sql,
    get_available_months,
)

log = logging.getLogger(__name__)

bp = Blueprint("waterfall", __name__, url_prefix="/waterfall")


# ── Formatting helpers (reuse from reports, available as Jinja globals) ──────
# fmt_dollars, fmt_month_full, fmt_month_short are already registered as
# Jinja globals in web/__init__.py — no need to import for templates.
# For Python-side use only:

def _fmt_month_full(ym: str) -> str:
    """'2026-02' -> 'February' or 'February 2025'."""
    from web.routes.reports import fmt_month_full
    return fmt_month_full(ym)


def _fmt_month_short(ym: str) -> str:
    """'2026-02' -> 'Feb' or 'Feb 25'."""
    from web.routes.reports import fmt_month_short
    return fmt_month_short(ym)


# ── BFM data helpers ────────────────────────────────────────────────────────


def _get_bfm_income(conn, month: str) -> int:
    """Total BFM income for a month. Returns cents (positive)."""
    cte = effective_txns_cte("t")
    excl = exclude_sql("t.category", include_income=True)
    row = conn.execute(
        f"WITH {cte} SELECT COALESCE(SUM(t.amount), 0) "
        f"FROM t WHERE strftime('%Y-%m', t.date) = ? "
        f"AND t.amount > 0 AND {excl}",
        (month,),
    ).fetchone()
    return int(round((row[0] or 0) * 100))


def _get_bfm_expenses_by_section(conn, entity_key: str, month: str) -> dict:
    """Get BFM expenses grouped by budget section.

    Returns dict with keys 'fixed', 'focus', 'other', 'none'.
    Each value is a list of {'category', 'spent_cents', 'budget_cents'} dicts.
    """
    from web.routes.short_term_planning import _get_budget_status

    budget_status = _get_budget_status(conn, entity_key, month)

    sections: dict[str, list] = {"fixed": [], "focus": [], "other": [], "none": []}
    for item in budget_status:
        if item["spent_cents"] <= 0:
            continue
        sec = item.get("budget_section") or "none"
        sections.setdefault(sec, []).append({
            "category": item["category"],
            "spent_cents": item["spent_cents"],
            "budget_cents": item["budget_cents"],
        })

    # Sort each section by spend descending
    for sec in sections:
        sections[sec].sort(key=lambda x: x["spent_cents"], reverse=True)

    return sections


def _get_historical_surplus(months: list[str]) -> list[dict]:
    """Compute BFM surplus for multiple months (lightweight, direct SQL).

    Uses simple income minus expenses without budget section grouping
    for performance on the trend chart.
    """
    results = []
    conn = get_connection("company")
    try:
        cte = effective_txns_cte("t")
        excl_no_income = exclude_sql("t.category", include_income=True)
        excl_with_income = exclude_sql("t.category", include_income=False)

        for month in months:
            # Income: positive amounts excluding transfers
            inc_row = conn.execute(
                f"WITH {cte} SELECT COALESCE(SUM(t.amount), 0) "
                f"FROM t WHERE strftime('%Y-%m', t.date) = ? "
                f"AND t.amount > 0 AND {excl_no_income}",
                (month,),
            ).fetchone()
            income = int(round((inc_row[0] or 0) * 100))

            # Expenses: negative amounts excluding transfers/income
            exp_row = conn.execute(
                f"WITH {cte} SELECT COALESCE(SUM(ABS(t.amount)), 0) "
                f"FROM t WHERE strftime('%Y-%m', t.date) = ? "
                f"AND t.amount < 0 AND {excl_with_income}",
                (month,),
            ).fetchone()
            expenses = int(round((exp_row[0] or 0) * 100))

            results.append({
                "month": month,
                "income_cents": income,
                "expenses_cents": expenses,
                "surplus_cents": income - expenses,
            })
    finally:
        conn.close()
    return results


# ── Personal debt helpers ────────────────────────────────────────────────────


def _get_personal_cc() -> tuple[list, int, dict | None, dict | None]:
    """Get personal CC balances, total, paydown goal, and pace."""
    from web.routes.weekly import (
        _get_cc_balances, _get_paydown_goal, _compute_paydown_pace,
    )

    conn = get_connection("personal")
    try:
        cards = _get_cc_balances(conn)
        total = sum(c["balance_cents"] for c in cards)
        goal = _get_paydown_goal(conn)
        pace = None
        if goal:
            pace = _compute_paydown_pace(goal, total, date.today())
        return cards, total, goal, pace
    finally:
        conn.close()


def _get_personal_liabilities() -> list[dict]:
    """Get personal liabilities from planning_items."""
    from web.routes.planning import _get_items

    items = _get_items("personal")
    return items.get("liabilities", [])


# ── Payoff estimate ──────────────────────────────────────────────────────────


def _compute_payoff_estimate(avg_surplus_cents: int, cc_total_cents: int) -> dict | None:
    """Estimate months to pay off CC debt at given monthly surplus."""
    if avg_surplus_cents <= 0 or cc_total_cents <= 0:
        return None
    months_to_payoff = cc_total_cents / avg_surplus_cents
    payoff_date = date.today() + timedelta(days=int(months_to_payoff * 30.44))
    return {
        "months": int(round(months_to_payoff)),
        "payoff_date_ym": payoff_date.strftime("%Y-%m"),
        "monthly_surplus_cents": avg_surplus_cents,
    }


# ── Main route ───────────────────────────────────────────────────────────────


@bp.route("/")
def index():
    if g.entity_key == "luxelegacy":
        return redirect(url_for("dashboard.index"))

    # Month navigation from BFM transaction history
    init_db("company")
    bfm_months = get_available_months("company")
    if not bfm_months:
        return render_template("waterfall.html", has_data=False)

    month = request.args.get("month", bfm_months[-1])
    if month not in bfm_months:
        month = bfm_months[-1]

    month_idx = bfm_months.index(month)
    prev_month = bfm_months[month_idx - 1] if month_idx > 0 else None
    next_month = bfm_months[month_idx + 1] if month_idx < len(bfm_months) - 1 else None

    # ── BFM data ──────────────────────────────────────────────────────────
    conn = get_connection("company")
    try:
        income_cents = _get_bfm_income(conn, month)
        sections = _get_bfm_expenses_by_section(conn, "company", month)
    finally:
        conn.close()

    fixed_total = sum(i["spent_cents"] for i in sections.get("fixed", []))
    operating_items = (
        sections.get("focus", [])
        + sections.get("other", [])
        + sections.get("none", [])
    )
    # Re-sort combined operating items by spend descending
    operating_items.sort(key=lambda x: x["spent_cents"], reverse=True)
    operating_total = sum(i["spent_cents"] for i in operating_items)
    total_expenses = fixed_total + operating_total
    surplus_cents = income_cents - total_expenses

    # ── Personal debt data ────────────────────────────────────────────────
    init_db("personal")
    cc_cards, cc_total, paydown_goal, paydown_pace = _get_personal_cc()
    liabilities = _get_personal_liabilities()

    # ── Historical trend (last 6 months including current) ────────────────
    end_idx = month_idx
    start_idx = max(0, end_idx - 5)
    trend_months = bfm_months[start_idx:end_idx + 1]
    trend = _get_historical_surplus(trend_months)
    max_abs = max((abs(t["surplus_cents"]) for t in trend), default=1) or 1

    # ── Payoff estimate (3-month rolling avg surplus) ─────────────────────
    recent_surpluses = [t["surplus_cents"] for t in trend[-3:] if t["surplus_cents"] > 0]
    avg_surplus = int(sum(recent_surpluses) / len(recent_surpluses)) if recent_surpluses else 0
    payoff_estimate = _compute_payoff_estimate(avg_surplus, cc_total)

    return render_template(
        "waterfall.html",
        has_data=True,
        month=month,
        month_label=_fmt_month_full(month),
        prev_month=prev_month,
        next_month=next_month,
        # Waterfall values
        income_cents=income_cents,
        fixed_costs=sections.get("fixed", []),
        fixed_total=fixed_total,
        operating_costs=operating_items,
        operating_total=operating_total,
        total_expenses=total_expenses,
        surplus_cents=surplus_cents,
        # Personal debt
        cc_cards=cc_cards,
        cc_total=cc_total,
        paydown_goal=paydown_goal,
        paydown_pace=paydown_pace,
        liabilities=liabilities,
        # Trend
        trend=trend,
        max_abs=max_abs,
        # Payoff
        payoff_estimate=payoff_estimate,
        avg_surplus=avg_surplus,
    )

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

# ── Target waterfall constants ─────────────────────────────────────────────
_TARGET_REVENUE = 17_000_000        # $170,000/mo in cents
_OWNER_SALARY_GROSS = 4_800_000     # $48,000/mo gross in cents
_EFFECTIVE_TAX_RATE_BPS = 2200      # 22% effective tax rate

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


# ── Target waterfall helpers ──────────────────────────────────────────────────


def _get_bfm_budget_totals(conn, month: str) -> dict:
    """Get BFM budget totals grouped by section for the Target waterfall.

    Returns dict with:
        staff_payroll_cents: Payroll budget minus owner salary
        fixed_cents: Fixed budget (excl Payroll)
        operating_cents: Focus + Other + None budget totals
    """
    from web.routes.short_term_planning import _get_budget_status

    budget_status = _get_budget_status(conn, "company", month)

    payroll_budget = 0
    fixed_no_payroll = 0
    operating_budget = 0

    for item in budget_status:
        sec = item.get("budget_section")
        cat = item["category"]
        budget = item.get("budget_cents", 0)

        if sec == "fixed":
            if cat == "Payroll":
                payroll_budget = budget
            else:
                fixed_no_payroll += budget
        elif sec in ("focus", "other") or sec is None:
            operating_budget += budget

    # Staff payroll = full payroll budget (owner not on payroll, takes draws)
    staff_payroll = payroll_budget

    return {
        "staff_payroll_cents": staff_payroll,
        "fixed_cents": fixed_no_payroll,
        "operating_cents": operating_budget,
        "payroll_budget_cents": payroll_budget,
    }


def _get_personal_budget_totals() -> dict:
    """Get personal budget totals grouped into fixed and variable.

    Returns dict with:
        fixed_cents: Fixed section budget total
        variable_cents: Focus + Other + None budget totals
        total_cents: Sum of all
    """
    from web.routes.short_term_planning import _get_budget_status

    conn = get_connection("personal")
    try:
        # Use current month for budget lookup (budgets are static per category)
        current_month = date.today().strftime("%Y-%m")
        budget_status = _get_budget_status(conn, "personal", current_month)
    finally:
        conn.close()

    fixed = 0
    variable = 0

    for item in budget_status:
        sec = item.get("budget_section")
        budget = item.get("budget_cents", 0)
        if sec == "fixed":
            fixed += budget
        elif sec in ("focus", "other") or sec is None:
            variable += budget

    return {
        "fixed_cents": fixed,
        "variable_cents": variable,
        "total_cents": fixed + variable,
    }


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
    conn_co = get_connection("company")
    try:
        income_cents = _get_bfm_income(conn_co, month)
        sections = _get_bfm_expenses_by_section(conn_co, "company", month)

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

        # ── Actual waterfall chart rows (horizontal bars) ────────────────
        chart_rows = []
        if income_cents > 0:
            fixed_pct = min(round(fixed_total / income_cents * 100, 1), 100)
            operating_pct = min(round(operating_total / income_cents * 100, 1), 100)
            surplus_pct = round(max(surplus_cents, 0) / income_cents * 100, 1)

            chart_rows = [
                {"label": "Revenue", "left": 0, "width": 100,
                 "cents": income_cents, "type": "income"},
                {"label": "Fixed Costs", "left": 0, "width": fixed_pct,
                 "cents": fixed_total, "type": "expense"},
                {"label": "Operating", "left": fixed_pct, "width": operating_pct,
                 "cents": operating_total, "type": "expense"},
                {"label": "Surplus", "left": 100 - surplus_pct, "width": surplus_pct,
                 "cents": abs(surplus_cents),
                 "type": "surplus" if surplus_cents >= 0 else "deficit"},
            ]

        # ── Target waterfall ────────────────────────────────────────────
        bfm_budgets = _get_bfm_budget_totals(conn_co, month)
    finally:
        conn_co.close()

    personal_budgets = _get_personal_budget_totals()

    # Allow URL overrides for scenario modeling
    try:
        target_revenue = int(float(request.args.get("target_revenue", 0)) * 100) or _TARGET_REVENUE
    except (ValueError, TypeError):
        target_revenue = _TARGET_REVENUE
    try:
        owner_salary_override = request.args.get("owner_salary")
        owner_gross_input = int(float(owner_salary_override) * 100) if owner_salary_override else _OWNER_SALARY_GROSS
    except (ValueError, TypeError):
        owner_gross_input = _OWNER_SALARY_GROSS
    target_staff_payroll = bfm_budgets["staff_payroll_cents"]
    target_bfm_fixed = bfm_budgets["fixed_cents"]
    target_bfm_operating = bfm_budgets["operating_cents"]
    target_bfm_surplus = (target_revenue - target_staff_payroll
                          - target_bfm_fixed - target_bfm_operating)

    # Default owner salary to BFM surplus (can't pay yourself more than you earn)
    # URL override still respected for scenario modeling
    if not owner_salary_override:
        owner_gross = max(target_bfm_surplus, 0)
    else:
        owner_gross = owner_gross_input
    owner_take_home = int(owner_gross * (10000 - _EFFECTIVE_TAX_RATE_BPS) / 10000)

    personal_fixed = personal_budgets["fixed_cents"]
    personal_variable = personal_budgets["variable_cents"]
    personal_remaining = owner_take_home - personal_fixed - personal_variable

    def _pct(v, base):
        return min(round(abs(v) / base * 100, 1), 100)

    # ── Target BFM rows (relative to $150k) ─────────────────────────────
    target_bfm_rows = []
    if target_revenue > 0:
        sp_pct = _pct(target_staff_payroll, target_revenue)
        bf_pct = _pct(target_bfm_fixed, target_revenue)
        bo_pct = _pct(target_bfm_operating, target_revenue)
        bs_pct = _pct(max(target_bfm_surplus, 0), target_revenue)

        target_bfm_rows = [
            {"label": "BFM Revenue", "left": 0, "width": 100,
             "cents": target_revenue, "type": "income"},
            {"label": "Staff Payroll", "left": 0, "width": sp_pct,
             "cents": target_staff_payroll, "type": "expense"},
            {"label": "BFM Fixed", "left": sp_pct, "width": bf_pct,
             "cents": target_bfm_fixed, "type": "expense"},
            {"label": "BFM Operating", "left": sp_pct + bf_pct, "width": bo_pct,
             "cents": target_bfm_operating, "type": "expense"},
            {"label": "BFM Surplus", "left": 100 - bs_pct, "width": bs_pct,
             "cents": abs(target_bfm_surplus),
             "type": "surplus" if target_bfm_surplus >= 0 else "deficit"},
        ]

    # ── Target Personal rows (relative to take-home) ────────────────────
    target_personal_rows = []
    if owner_take_home > 0:
        pf_pct = _pct(personal_fixed, owner_take_home)
        pv_pct = _pct(personal_variable, owner_take_home)
        pr_pct = _pct(max(personal_remaining, 0), owner_take_home)

        target_personal_rows = [
            {"label": "Take-Home Pay", "left": 0, "width": 100,
             "cents": owner_take_home, "type": "income"},
            {"label": "Personal Fixed", "left": 0, "width": pf_pct,
             "cents": personal_fixed, "type": "expense"},
            {"label": "Personal Variable", "left": pf_pct, "width": pv_pct,
             "cents": personal_variable, "type": "expense"},
            {"label": "Remaining", "left": 100 - pr_pct, "width": pr_pct,
             "cents": abs(personal_remaining),
             "type": "surplus" if personal_remaining >= 0 else "deficit"},
        ]

    # ── Personal debt data ────────────────────────────────────────────────
    init_db("personal")
    cc_cards, cc_total, paydown_goal, paydown_pace = _get_personal_cc()

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
        # Actual waterfall chart
        chart_rows=chart_rows,
        # Waterfall values
        income_cents=income_cents,
        fixed_costs=sections.get("fixed", []),
        fixed_total=fixed_total,
        operating_costs=operating_items,
        operating_total=operating_total,
        total_expenses=total_expenses,
        surplus_cents=surplus_cents,
        # Target waterfall
        target_bfm_rows=target_bfm_rows,
        target_personal_rows=target_personal_rows,
        target_revenue=target_revenue,
        owner_gross=owner_gross,
        owner_take_home=owner_take_home,
        target_bfm_surplus=target_bfm_surplus,
        personal_remaining=personal_remaining,
        # Personal debt
        cc_cards=cc_cards,
        cc_total=cc_total,
        paydown_goal=paydown_goal,
        paydown_pace=paydown_pace,
        # Trend
        trend=trend,
        max_abs=max_abs,
        # Payoff
        payoff_estimate=payoff_estimate,
        avg_surplus=avg_surplus,
    )

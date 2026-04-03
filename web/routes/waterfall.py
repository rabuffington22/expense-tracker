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

    Mirrors the 3 budget sections from Short-Term Planning:
        staff_payroll_cents: Payroll budget (extracted from fixed)
        fixed_cents: Fixed budget (excl Payroll)
        focus_cents: Focus section budget
        other_cents: Everything Else + no-budget totals
    """
    from web.routes.short_term_planning import _get_budget_status

    budget_status = _get_budget_status(conn, "company", month)

    payroll_budget = 0
    fixed_no_payroll = 0
    focus_budget = 0
    other_budget = 0
    fixed_items = []
    focus_items = []
    other_items = []

    for item in budget_status:
        sec = item.get("budget_section")
        cat = item["category"]
        budget = item.get("budget_cents", 0)

        if sec == "fixed":
            if cat == "Payroll":
                payroll_budget = budget
            else:
                fixed_no_payroll += budget
                if budget > 0:
                    fixed_items.append({"c": cat, "v": budget})
        elif sec == "focus":
            focus_budget += budget
            if budget > 0:
                focus_items.append({"c": cat, "v": budget})
        else:  # "other" or None (no budget)
            other_budget += budget
            if budget > 0:
                other_items.append({"c": cat, "v": budget})

    # Staff payroll = full payroll budget (owner not on payroll, takes draws)
    staff_payroll = payroll_budget
    fixed_items.sort(key=lambda x: x["v"], reverse=True)
    focus_items.sort(key=lambda x: x["v"], reverse=True)
    other_items.sort(key=lambda x: x["v"], reverse=True)

    return {
        "staff_payroll_cents": staff_payroll,
        "fixed_cents": fixed_no_payroll,
        "focus_cents": focus_budget,
        "other_cents": other_budget,
        "payroll_budget_cents": payroll_budget,
        "fixed_items": fixed_items,
        "focus_items": focus_items,
        "other_items": other_items,
    }


def _get_personal_budget_totals(month: str | None = None) -> dict:
    """Get personal budget totals AND actual spending grouped into fixed/focus/other.

    Mirrors the 3 budget sections from Short-Term Planning:
        fixed_cents: Fixed section budget total
        focus_cents: Focus section budget total
        other_cents: Everything Else + no-budget totals
        total_cents: Sum of all budgets
        *_items: [{c, v}] per category (for hover tooltips)
        actual_*_cents / actual_*_items: Actual spending equivalents
    """
    from web.routes.short_term_planning import _get_budget_status

    conn = get_connection("personal")
    try:
        use_month = month or date.today().strftime("%Y-%m")
        budget_status = _get_budget_status(conn, "personal", use_month)
    finally:
        conn.close()

    buckets = {
        "fixed": {"budget": 0, "spent": 0, "budget_items": [], "spent_items": []},
        "focus": {"budget": 0, "spent": 0, "budget_items": [], "spent_items": []},
        "other": {"budget": 0, "spent": 0, "budget_items": [], "spent_items": []},
    }

    for item in budget_status:
        sec = item.get("budget_section")
        cat = item.get("category", "")
        budget = item.get("budget_cents", 0)
        spent = item.get("spent_cents", 0)
        # Map to 3 buckets matching STP sections
        if sec == "fixed":
            key = "fixed"
        elif sec == "focus":
            key = "focus"
        else:  # "other" or None (no budget)
            key = "other"
        b = buckets[key]
        b["budget"] += budget
        b["spent"] += spent
        if budget > 0:
            b["budget_items"].append({"c": cat, "v": budget})
        if spent > 0:
            b["spent_items"].append({"c": cat, "v": spent})

    for b in buckets.values():
        b["budget_items"].sort(key=lambda x: x["v"], reverse=True)
        b["spent_items"].sort(key=lambda x: x["v"], reverse=True)

    return {
        "fixed_cents": buckets["fixed"]["budget"],
        "focus_cents": buckets["focus"]["budget"],
        "other_cents": buckets["other"]["budget"],
        "total_cents": sum(b["budget"] for b in buckets.values()),
        "fixed_items": buckets["fixed"]["budget_items"],
        "focus_items": buckets["focus"]["budget_items"],
        "other_items": buckets["other"]["budget_items"],
        "actual_fixed_cents": buckets["fixed"]["spent"],
        "actual_focus_cents": buckets["focus"]["spent"],
        "actual_other_cents": buckets["other"]["spent"],
        "actual_fixed_items": buckets["fixed"]["spent_items"],
        "actual_focus_items": buckets["focus"]["spent_items"],
        "actual_other_items": buckets["other"]["spent_items"],
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
        focus_items = sections.get("focus", [])
        focus_items.sort(key=lambda x: x["spent_cents"], reverse=True)
        focus_total = sum(i["spent_cents"] for i in focus_items)
        other_items = sections.get("other", []) + sections.get("none", [])
        other_items.sort(key=lambda x: x["spent_cents"], reverse=True)
        other_total = sum(i["spent_cents"] for i in other_items)
        total_expenses = fixed_total + focus_total + other_total
        surplus_cents = income_cents - total_expenses

        # ── Actual waterfall chart rows (horizontal bars) ────────────────
        chart_rows = []
        if income_cents > 0:
            fixed_pct = min(round(fixed_total / income_cents * 100, 1), 100)
            focus_pct = min(round(focus_total / income_cents * 100, 1), 100)
            other_pct = min(round(other_total / income_cents * 100, 1), 100)
            surplus_pct = round(max(surplus_cents, 0) / income_cents * 100, 1)

            chart_rows = [
                {"label": "Revenue", "left": 0, "width": 100,
                 "cents": income_cents, "type": "income"},
                {"label": "Fixed Costs", "left": 0, "width": fixed_pct,
                 "cents": fixed_total, "type": "expense"},
                {"label": "Focus", "left": fixed_pct, "width": focus_pct,
                 "cents": focus_total, "type": "expense"},
                {"label": "Everything Else", "left": fixed_pct + focus_pct, "width": other_pct,
                 "cents": other_total, "type": "expense"},
                {"label": "Surplus", "left": 100 - surplus_pct, "width": surplus_pct,
                 "cents": abs(surplus_cents),
                 "type": "surplus" if surplus_cents >= 0 else "deficit"},
            ]

        # ── Target waterfall ────────────────────────────────────────────
        bfm_budgets = _get_bfm_budget_totals(conn_co, month)
    finally:
        conn_co.close()

    personal_budgets = _get_personal_budget_totals(month)

    # ── Two-mode scenario modeling ────────────────────────────────────────
    # Revenue mode (default): set revenue target, salary = surplus
    # Take-home mode: set desired take-home, back-calculate gross + revenue
    target_mode = request.args.get("mode", "revenue")
    if target_mode not in ("revenue", "takehome"):
        target_mode = "revenue"

    # Adjustable effective tax rate (URL param overrides default)
    try:
        tax_rate_pct = float(request.args.get("tax_rate", _EFFECTIVE_TAX_RATE_BPS / 100))
    except (ValueError, TypeError):
        tax_rate_pct = _EFFECTIVE_TAX_RATE_BPS / 100
    tax_rate_bps = int(round(tax_rate_pct * 100))
    if tax_rate_bps < 0 or tax_rate_bps > 9999:
        tax_rate_bps = _EFFECTIVE_TAX_RATE_BPS

    target_staff_payroll = bfm_budgets["staff_payroll_cents"]
    target_bfm_fixed = bfm_budgets["fixed_cents"]
    target_bfm_focus = bfm_budgets["focus_cents"]
    target_bfm_other = bfm_budgets["other_cents"]
    bfm_costs = (target_staff_payroll + target_bfm_fixed
                 + target_bfm_focus + target_bfm_other)

    if target_mode == "takehome":
        # Take-home mode: desired take-home → gross → required revenue
        try:
            desired_take_home = int(float(request.args.get("take_home", 0)) * 100)
        except (ValueError, TypeError):
            desired_take_home = 0
        if desired_take_home <= 0:
            # Default: back-calculate from _OWNER_SALARY_GROSS
            desired_take_home = int(_OWNER_SALARY_GROSS * (10000 - tax_rate_bps) / 10000)
        # Gross = take_home / (1 - tax_rate)
        owner_gross = int(desired_take_home * 10000 / (10000 - tax_rate_bps))
        target_revenue = owner_gross + bfm_costs
        target_bfm_surplus = owner_gross
    else:
        # Revenue mode: revenue target → surplus → salary
        try:
            target_revenue = int(float(request.args.get("target_revenue", 0)) * 100) or _TARGET_REVENUE
        except (ValueError, TypeError):
            target_revenue = _TARGET_REVENUE
        target_bfm_surplus = target_revenue - bfm_costs
        owner_gross = max(target_bfm_surplus, 0)

    owner_take_home = int(owner_gross * (10000 - tax_rate_bps) / 10000)

    personal_fixed = personal_budgets["fixed_cents"]
    personal_focus = personal_budgets["focus_cents"]
    personal_other = personal_budgets["other_cents"]
    personal_remaining = owner_take_home - personal_fixed - personal_focus - personal_other

    def _pct(v, base):
        return min(round(abs(v) / base * 100, 1), 100)

    # ── Target BFM rows (relative to revenue) ─────────────────────────────
    target_bfm_rows = []
    if target_revenue > 0:
        sp_pct = _pct(target_staff_payroll, target_revenue)
        bf_pct = _pct(target_bfm_fixed, target_revenue)
        bfo_pct = _pct(target_bfm_focus, target_revenue)
        boe_pct = _pct(target_bfm_other, target_revenue)
        bs_pct = _pct(max(target_bfm_surplus, 0), target_revenue)

        target_bfm_rows = [
            {"label": "BFM Revenue", "left": 0, "width": 100,
             "cents": target_revenue, "type": "income"},
            {"label": "Staff Payroll", "left": 0, "width": sp_pct,
             "cents": target_staff_payroll, "type": "expense"},
            {"label": "BFM Fixed", "left": sp_pct, "width": bf_pct,
             "cents": target_bfm_fixed, "type": "expense"},
            {"label": "BFM Focus", "left": sp_pct + bf_pct, "width": bfo_pct,
             "cents": target_bfm_focus, "type": "expense"},
            {"label": "BFM Everything Else", "left": sp_pct + bf_pct + bfo_pct, "width": boe_pct,
             "cents": target_bfm_other, "type": "expense"},
            {"label": "BFM Surplus", "left": 100 - bs_pct, "width": bs_pct,
             "cents": abs(target_bfm_surplus),
             "type": "surplus" if target_bfm_surplus >= 0 else "deficit"},
        ]

    # ── Target Personal rows (relative to take-home) ────────────────────
    target_personal_rows = []
    if owner_take_home > 0:
        pf_pct = _pct(personal_fixed, owner_take_home)
        pfo_pct = _pct(personal_focus, owner_take_home)
        po_pct = _pct(personal_other, owner_take_home)
        pr_pct = _pct(max(personal_remaining, 0), owner_take_home)

        target_personal_rows = [
            {"label": "Take-Home Pay", "left": 0, "width": 100,
             "cents": owner_take_home, "type": "income"},
            {"label": "Personal Fixed", "left": 0, "width": pf_pct,
             "cents": personal_fixed, "type": "expense"},
            {"label": "Personal Focus", "left": pf_pct, "width": pfo_pct,
             "cents": personal_focus, "type": "expense"},
            {"label": "Personal Everything Else", "left": pf_pct + pfo_pct, "width": po_pct,
             "cents": personal_other, "type": "expense"},
            {"label": "Remaining", "left": 100 - pr_pct, "width": pr_pct,
             "cents": abs(personal_remaining),
             "type": "surplus" if personal_remaining >= 0 else "deficit"},
        ]

    # ── Actual personal waterfall (extends BFM actual into personal) ──────
    actual_owner_gross = max(surplus_cents, 0)
    actual_take_home = int(actual_owner_gross * (10000 - tax_rate_bps) / 10000)
    actual_personal_fixed = personal_budgets["actual_fixed_cents"]
    actual_personal_focus = personal_budgets["actual_focus_cents"]
    actual_personal_other = personal_budgets["actual_other_cents"]
    actual_personal_remaining = (actual_take_home - actual_personal_fixed
                                 - actual_personal_focus - actual_personal_other)

    actual_personal_rows = []
    if actual_take_home > 0:
        apf_pct = _pct(actual_personal_fixed, actual_take_home)
        apfo_pct = _pct(actual_personal_focus, actual_take_home)
        apo_pct = _pct(actual_personal_other, actual_take_home)
        apr_pct = _pct(max(actual_personal_remaining, 0), actual_take_home)

        actual_personal_rows = [
            {"label": "Take-Home Pay", "left": 0, "width": 100,
             "cents": actual_take_home, "type": "income"},
            {"label": "Personal Fixed", "left": 0, "width": apf_pct,
             "cents": actual_personal_fixed, "type": "expense"},
            {"label": "Personal Focus", "left": apf_pct, "width": apfo_pct,
             "cents": actual_personal_focus, "type": "expense"},
            {"label": "Personal Everything Else", "left": apf_pct + apfo_pct, "width": apo_pct,
             "cents": actual_personal_other, "type": "expense"},
            {"label": "Remaining", "left": 100 - apr_pct, "width": apr_pct,
             "cents": abs(actual_personal_remaining),
             "type": "surplus" if actual_personal_remaining >= 0 else "deficit"},
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
        focus_costs=focus_items,
        focus_total=focus_total,
        other_costs=other_items,
        other_total=other_total,
        total_expenses=total_expenses,
        surplus_cents=surplus_cents,
        # Actual tooltip data (category → spent)
        actual_fixed_tip=[{"c": x["category"], "v": x["spent_cents"]}
                          for x in sections.get("fixed", []) if x["spent_cents"] > 0],
        actual_focus_tip=[{"c": x["category"], "v": x["spent_cents"]}
                          for x in focus_items if x.get("spent_cents", 0) > 0],
        actual_other_tip=[{"c": x["category"], "v": x["spent_cents"]}
                          for x in other_items if x.get("spent_cents", 0) > 0],
        # Actual personal waterfall
        actual_personal_rows=actual_personal_rows,
        actual_owner_gross=actual_owner_gross,
        actual_take_home=actual_take_home,
        actual_personal_remaining=actual_personal_remaining,
        # Actual personal tooltip data (category → actual spend)
        actual_personal_fixed_tip=personal_budgets.get("actual_fixed_items", []),
        actual_personal_focus_tip=personal_budgets.get("actual_focus_items", []),
        actual_personal_other_tip=personal_budgets.get("actual_other_items", []),
        # Target waterfall
        target_mode=target_mode,
        target_bfm_rows=target_bfm_rows,
        target_personal_rows=target_personal_rows,
        target_revenue=target_revenue,
        owner_gross=owner_gross,
        owner_take_home=owner_take_home,
        target_bfm_surplus=target_bfm_surplus,
        bfm_costs=bfm_costs,
        tax_rate_pct=tax_rate_pct,
        personal_remaining=personal_remaining,
        # Target tooltip data (category → budget)
        bfm_fixed_tip=bfm_budgets.get("fixed_items", []),
        bfm_focus_tip=bfm_budgets.get("focus_items", []),
        bfm_other_tip=bfm_budgets.get("other_items", []),
        personal_fixed_tip=personal_budgets.get("fixed_items", []),
        personal_focus_tip=personal_budgets.get("focus_items", []),
        personal_other_tip=personal_budgets.get("other_items", []),
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

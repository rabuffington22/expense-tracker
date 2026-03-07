"""Global AI chat — Ask Opus on every page with page-specific context."""
from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from datetime import date

from flask import Blueprint, request, g

from core.db import get_connection
from core.ai_client import chat_completion, MODEL_OPUS

log = logging.getLogger(__name__)

bp = Blueprint("ai", __name__, url_prefix="/ai")

# Temp dir for conversation history
_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-ai")
os.makedirs(_TEMP_DIR, exist_ok=True)

# Cross-entity visibility (mirrors planning.py)
_CROSS_ENTITY = {
    "personal": ["company"],
    "company": ["personal"],
    "luxelegacy": [],
}

_ENTITY_DISPLAY = {
    "personal": "Personal",
    "company": "BFM",
    "luxelegacy": "LL",
}

# Valid page names for context dispatch
_VALID_PAGES = {
    "planning", "dashboard", "transactions",
    "subscriptions", "cashflow", "reports", "general",
}


# ── System Prompts ──────────────────────────────────────────────────────────

_BASE_SYSTEM = """You are a knowledgeable financial advisor embedded in a personal \
expense tracking app called Ledger AI. You have full access to the user's financial data. \
Be specific with dollar amounts and names from the data. \
Be conversational but concise — no filler, no disclaimers about not being a financial advisor. \
Use plain language, not jargon."""

_PAGE_PROMPTS = {
    "planning": """You specialize in long-term financial planning and projections.
Your role: answer financial planning questions using the specific data provided.
Run scenarios when asked ("what if I pay extra $500/mo on the mortgage?").
When doing projections, show the math briefly so they can verify.
The projections in the data are already inflation-adjusted to today's dollars.
When doing your own calculations, adjust for inflation unless told otherwise.""",

    "dashboard": """You specialize in analyzing spending patterns and financial health.
Your role: help the user understand their spending, identify trends, and spot opportunities.
Reference specific categories, merchants, and dollar amounts from the data.
Compare periods when data is available. Suggest actionable changes.""",

    "transactions": """You specialize in transaction analysis and categorization.
Your role: help the user understand their transaction patterns, find specific charges,
identify unusual activity, and optimize spending by category or merchant.
Reference specific transaction details from the data.""",

    "subscriptions": """You specialize in subscription management and cost optimization.
Your role: help the user evaluate their subscriptions, identify cancellation candidates,
spot price changes, and estimate savings from cutting services.
Reference specific subscription names, amounts, and frequencies from the data.""",

    "cashflow": """You specialize in cash flow management and account health.
Your role: help the user understand their account balances, credit utilization,
upcoming bills, and cash flow timing. Reference specific accounts and balances.""",

    "reports": """You specialize in financial reporting and trend analysis.
Your role: help the user understand their spending trends over time,
compare month-over-month or year-over-year patterns, and identify long-term shifts.
Reference specific months, categories, and dollar amounts.""",
}


def _get_system_prompt(page: str) -> str:
    """Build the system prompt for a given page."""
    page_extra = _PAGE_PROMPTS.get(page, "")
    return _BASE_SYSTEM + ("\n\n" + page_extra if page_extra else "")


# ── Conversation Persistence ────────────────────────────────────────────────


def _get_conversation_path(entity_key: str, page: str) -> str:
    return os.path.join(_TEMP_DIR, "chat_%s_%s.json" % (entity_key, page))


def _load_conversation(entity_key: str, page: str) -> list[dict]:
    path = _get_conversation_path(entity_key, page)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_conversation(entity_key: str, page: str, messages: list[dict]):
    path = _get_conversation_path(entity_key, page)
    if len(messages) > 40:
        messages = messages[-40:]
    with open(path, "w") as f:
        json.dump(messages, f)


# ── Endpoints ───────────────────────────────────────────────────────────────


@bp.route("/ask", methods=["POST"])
def ask():
    """Handle AI chat question via HTMX — works from any page."""
    question = request.form.get("question", "").strip()
    if not question:
        return '<div class="ai-chat-error">Please enter a question.</div>'

    page = request.form.get("page", "general").strip()
    if page not in _VALID_PAGES:
        page = "general"

    entity_key = g.entity_key

    # Gather fresh context for this page
    context = _gather_context(entity_key, page)

    # Load conversation history
    history = _load_conversation(entity_key, page)

    # Build messages
    if not history:
        messages = [{
            "role": "user",
            "content": "Here is my current financial data:\n\n%s\n\nQuestion: %s"
            % (context, question),
        }]
    else:
        messages = list(history)
        messages.append({
            "role": "user",
            "content": "Updated financial data:\n\n%s\n\nQuestion: %s"
            % (context, question),
        })

    response = chat_completion(
        messages=messages,
        model=MODEL_OPUS,
        max_tokens=1500,
        system=_get_system_prompt(page),
        timeout=60,
    )

    if not response:
        return '<div class="ai-chat-error">AI is unavailable right now. Check that OPENROUTER_API_KEY is set.</div>'

    # Save clean question (without context) to history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})
    _save_conversation(entity_key, page, history)

    from markupsafe import escape
    escaped_q = escape(question)
    escaped_r = _format_ai_response(response)

    return (
        '<div class="ai-chat-pair">'
        '<div class="ai-chat-q">%s</div>'
        '<div class="ai-chat-a">%s</div>'
        '</div>' % (escaped_q, escaped_r)
    )


@bp.route("/clear", methods=["POST"])
def clear_chat():
    """Clear conversation history for current entity + page."""
    page = request.form.get("page", "general").strip()
    path = _get_conversation_path(g.entity_key, page)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return ""


# ── Context Dispatcher ──────────────────────────────────────────────────────


def _gather_context(entity_key: str, page: str) -> str:
    """Dispatch to the right context builder based on page."""
    builders = {
        "planning": _gather_planning_context,
        "dashboard": _gather_dashboard_context,
        "transactions": _gather_transactions_context,
        "subscriptions": _gather_subscriptions_context,
        "cashflow": _gather_cashflow_context,
        "reports": _gather_reports_context,
    }
    builder = builders.get(page, _gather_general_context)
    try:
        return builder(entity_key)
    except Exception:
        log.exception("Error gathering %s context", page)
        return _gather_general_context(entity_key)


# ── Context Builders ────────────────────────────────────────────────────────


def _fmt_k(cents: int) -> str:
    """Format cents to readable dollars: $964k, $2.3M, etc."""
    if cents is None or cents == 0:
        return "$0"
    dollars = cents / 100
    if abs(dollars) >= 1_000_000:
        return "$%.1fM" % (dollars / 1_000_000)
    if abs(dollars) >= 1000:
        return "$%dk" % round(dollars / 1000)
    return "$%d" % round(dollars)


def _gather_general_context(entity_key: str) -> str:
    """Fallback context: 3-month spending + account balances."""
    lines = []
    lines.append("=== FINANCIAL OVERVIEW ===")

    cross_keys = _CROSS_ENTITY.get(entity_key, [])
    for ek in [entity_key] + cross_keys:
        conn = None
        try:
            conn = get_connection(ek)
            display = _ENTITY_DISPLAY.get(ek, ek)

            # Monthly spending
            rows = conn.execute(
                "SELECT strftime('%%Y-%%m', date) as month, "
                "ABS(SUM(CASE WHEN amount < 0 AND COALESCE(category,'') "
                "NOT IN ('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
                "THEN amount ELSE 0 END)) as spend, "
                "SUM(CASE WHEN amount > 0 AND COALESCE(category,'') "
                "NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
                "THEN amount ELSE 0 END) as income "
                "FROM transactions "
                "WHERE date >= date('now', '-3 months') "
                "GROUP BY month ORDER BY month"
            ).fetchall()
            if rows:
                lines.append("\n%s monthly:" % display)
                for r in rows:
                    lines.append(
                        "  %s: $%s spent, $%s income"
                        % (r["month"], "{:,.0f}".format(r["spend"]),
                           "{:,.0f}".format(r["income"]))
                    )

            # Top categories this month
            cat_rows = conn.execute(
                "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
                "ABS(SUM(amount)) as total, COUNT(*) as cnt "
                "FROM transactions "
                "WHERE strftime('%%Y-%%m', date) = strftime('%%Y-%%m', 'now') "
                "AND amount < 0 "
                "AND COALESCE(category,'') NOT IN "
                "('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
                "GROUP BY cat ORDER BY total DESC LIMIT 10"
            ).fetchall()
            if cat_rows:
                lines.append("  Top categories this month:")
                for r in cat_rows:
                    lines.append(
                        "    %s: $%s (%d txns)"
                        % (r["cat"], "{:,.0f}".format(r["total"]), r["cnt"])
                    )

            # Account balances
            accts = conn.execute(
                "SELECT account_name, balance_cents, account_type, credit_limit_cents "
                "FROM account_balances ORDER BY sort_order"
            ).fetchall()
            if accts:
                lines.append("\n  %s accounts:" % display)
                for a in accts:
                    bal = "{:,.0f}".format(abs(a["balance_cents"]) / 100)
                    extra = ""
                    if a["account_type"] == "credit_card" and a["credit_limit_cents"]:
                        extra = " (limit $%s)" % "{:,.0f}".format(
                            a["credit_limit_cents"] / 100)
                    lines.append("    %s: $%s%s" % (a["account_name"], bal, extra))
        except Exception:
            pass
        finally:
            if conn is not None:
                conn.close()

    return "\n".join(lines)


def _gather_planning_context(entity_key: str) -> str:
    """Full planning context: assets, liabilities, projections, spending."""
    # Import planning helpers — they live in planning.py
    from web.routes.planning import (
        _get_settings, _get_milestones, _load_entity_section,
    )

    settings = _get_settings()
    milestones = _get_milestones(settings)

    primary = _load_entity_section(entity_key, settings)
    cross_keys = _CROSS_ENTITY.get(entity_key, [])
    cross_sections = [_load_entity_section(k, settings) for k in cross_keys]
    all_sections = [primary] + cross_sections

    lines = []
    lines.append("=== PLANNING DATA ===")
    lines.append(
        "Settings: Age %d (born %s), Inflation %.1f%%, Milestones: %s"
        % (
            settings["current_age"],
            settings.get("birth_date", "unknown"),
            settings["inflation_rate"] / 100,
            ", ".join(str(m) for m in milestones),
        )
    )
    lines.append("")

    for sec in all_sections:
        lines.append("--- %s ---" % sec["entity_display"])
        if sec["assets"]:
            lines.append("Assets:")
            for a in sec["assets"]:
                proj_parts = [
                    "@%d: %s" % (m, _fmt_k(a["projections"].get(m, 0)))
                    for m in milestones
                ]
                lines.append(
                    "  %s: %s value, %.1f%% appr, $%s/mo contrib → %s"
                    % (
                        a["name"],
                        _fmt_k(a["current_value_cents"]),
                        a["annual_rate_bps"] / 100,
                        "{:,.0f}".format(a["monthly_contrib_cents"] / 100)
                        if a["monthly_contrib_cents"]
                        else "0",
                        ", ".join(proj_parts),
                    )
                )
        if sec["liabilities"]:
            lines.append("Liabilities:")
            for li in sec["liabilities"]:
                proj_parts = []
                for m in milestones:
                    val = li["projections"].get(m, 0)
                    proj_parts.append(
                        "@%d: %s"
                        % (m, "Paid" if val == 0 else _fmt_k(val))
                    )
                lines.append(
                    "  %s: %s balance, %.2f%% rate, $%s/mo payment → %s"
                    % (
                        li["name"],
                        _fmt_k(li["current_value_cents"]),
                        li["annual_rate_bps"] / 100,
                        "{:,.0f}".format(li["monthly_payment_cents"] / 100)
                        if li["monthly_payment_cents"]
                        else "0",
                        ", ".join(proj_parts),
                    )
                )
        nw = sec["summary"]
        lines.append(
            "Net Worth: Today %s → %s"
            % (
                _fmt_k(nw["today"]["net_worth_cents"]),
                ", ".join(
                    "@%d: %s" % (m, _fmt_k(nw[m]["net_worth_cents"]))
                    for m in milestones
                ),
            )
        )
        lines.append("")

    # Combined
    combined_today = sum(
        s["summary"]["today"]["net_worth_cents"] for s in all_sections)
    combined_parts = []
    for m in milestones:
        combined_parts.append(
            "@%d: %s"
            % (m, _fmt_k(sum(
                s["summary"][m]["net_worth_cents"] for s in all_sections)))
        )
    lines.append(
        "COMBINED NET WORTH: Today %s → %s"
        % (_fmt_k(combined_today), ", ".join(combined_parts))
    )
    lines.append("")

    # Append general spending + accounts
    lines.append(_gather_general_context(entity_key))

    return "\n".join(lines)


def _gather_dashboard_context(entity_key: str) -> str:
    """Dashboard context: period totals, top categories, top merchants, trends."""
    lines = []
    lines.append("=== DASHBOARD DATA ===")

    today = date.today()
    this_month = today.strftime("%Y-%m")
    lines.append("Current month: %s" % today.strftime("%B %Y"))

    conn = None
    try:
        conn = get_connection(entity_key)
        display = _ENTITY_DISPLAY.get(entity_key, entity_key)

        # This month totals
        row = conn.execute(
            "SELECT "
            "ABS(SUM(CASE WHEN amount < 0 AND COALESCE(category,'') "
            "NOT IN ('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "THEN amount ELSE 0 END)) as spend, "
            "SUM(CASE WHEN amount > 0 AND COALESCE(category,'') "
            "NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
            "THEN amount ELSE 0 END) as income, "
            "COUNT(*) as cnt "
            "FROM transactions "
            "WHERE strftime('%%Y-%%m', date) = ?"
            , (this_month,)
        ).fetchone()
        if row:
            lines.append(
                "\n%s this month: $%s spent, $%s income (%d transactions)"
                % (display, "{:,.0f}".format(row["spend"] or 0),
                   "{:,.0f}".format(row["income"] or 0), row["cnt"])
            )

        # Top 10 categories this month
        cat_rows = conn.execute(
            "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
            "ABS(SUM(amount)) as total, COUNT(*) as cnt "
            "FROM transactions "
            "WHERE strftime('%%Y-%%m', date) = ? "
            "AND amount < 0 "
            "AND COALESCE(category,'') NOT IN "
            "('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "GROUP BY cat ORDER BY total DESC LIMIT 10"
            , (this_month,)
        ).fetchall()
        if cat_rows:
            lines.append("\nTop categories:")
            for r in cat_rows:
                lines.append(
                    "  %s: $%s (%d txns)"
                    % (r["cat"], "{:,.0f}".format(r["total"]), r["cnt"])
                )

        # Top 10 merchants this month
        merch_rows = conn.execute(
            "SELECT COALESCE(NULLIF(merchant_canonical,''), description_raw) as merch, "
            "ABS(SUM(amount)) as total, COUNT(*) as cnt "
            "FROM transactions "
            "WHERE strftime('%%Y-%%m', date) = ? "
            "AND amount < 0 "
            "AND COALESCE(category,'') NOT IN "
            "('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "GROUP BY merch ORDER BY total DESC LIMIT 10"
            , (this_month,)
        ).fetchall()
        if merch_rows:
            lines.append("\nTop merchants:")
            for r in merch_rows:
                lines.append(
                    "  %s: $%s (%d txns)"
                    % (r["merch"], "{:,.0f}".format(r["total"]), r["cnt"])
                )

        # 6-month trend
        rows = conn.execute(
            "SELECT strftime('%%Y-%%m', date) as month, "
            "ABS(SUM(CASE WHEN amount < 0 AND COALESCE(category,'') "
            "NOT IN ('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "THEN amount ELSE 0 END)) as spend, "
            "SUM(CASE WHEN amount > 0 AND COALESCE(category,'') "
            "NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
            "THEN amount ELSE 0 END) as income "
            "FROM transactions "
            "WHERE date >= date('now', '-6 months') "
            "GROUP BY month ORDER BY month"
        ).fetchall()
        if rows:
            lines.append("\n6-month trend:")
            for r in rows:
                lines.append(
                    "  %s: $%s spent, $%s income"
                    % (r["month"], "{:,.0f}".format(r["spend"]),
                       "{:,.0f}".format(r["income"]))
                )

        # Uncategorized count
        unc = conn.execute(
            "SELECT COUNT(*) as cnt FROM transactions "
            "WHERE (category IS NULL OR category = '' OR category = 'Needs Review') "
            "AND date >= date('now', '-3 months')"
        ).fetchone()
        if unc and unc["cnt"]:
            lines.append("\nNeeds review: %d uncategorized transactions" % unc["cnt"])

    except Exception:
        pass
    finally:
        if conn is not None:
            conn.close()

    # Append account balances
    lines.append("")
    lines.append(_gather_general_context(entity_key))

    return "\n".join(lines)


def _gather_transactions_context(entity_key: str) -> str:
    """Transaction context: recent patterns, category distribution, top merchants."""
    lines = []
    lines.append("=== TRANSACTION DATA ===")

    conn = None
    try:
        conn = get_connection(entity_key)

        # Last 90 days summary
        row = conn.execute(
            "SELECT COUNT(*) as cnt, "
            "ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) as total_spend, "
            "SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income "
            "FROM transactions WHERE date >= date('now', '-90 days')"
        ).fetchone()
        if row:
            lines.append(
                "Last 90 days: %d transactions, $%s spent, $%s income"
                % (row["cnt"], "{:,.0f}".format(row["total_spend"] or 0),
                   "{:,.0f}".format(row["total_income"] or 0))
            )

        # Category distribution (last 90 days)
        cat_rows = conn.execute(
            "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
            "ABS(SUM(amount)) as total, COUNT(*) as cnt "
            "FROM transactions "
            "WHERE date >= date('now', '-90 days') AND amount < 0 "
            "AND COALESCE(category,'') NOT IN "
            "('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "GROUP BY cat ORDER BY total DESC LIMIT 15"
        ).fetchall()
        if cat_rows:
            lines.append("\nCategory breakdown (90 days):")
            for r in cat_rows:
                lines.append(
                    "  %s: $%s (%d txns)"
                    % (r["cat"], "{:,.0f}".format(r["total"]), r["cnt"])
                )

        # Top merchants (last 90 days)
        merch_rows = conn.execute(
            "SELECT COALESCE(NULLIF(merchant_canonical,''), description_raw) as merch, "
            "ABS(SUM(amount)) as total, COUNT(*) as cnt "
            "FROM transactions "
            "WHERE date >= date('now', '-90 days') AND amount < 0 "
            "AND COALESCE(category,'') NOT IN "
            "('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "GROUP BY merch ORDER BY cnt DESC LIMIT 15"
        ).fetchall()
        if merch_rows:
            lines.append("\nMost frequent merchants (90 days):")
            for r in merch_rows:
                lines.append(
                    "  %s: %d times, $%s total"
                    % (r["merch"], r["cnt"], "{:,.0f}".format(r["total"]))
                )

        # Recent large transactions
        large = conn.execute(
            "SELECT date, COALESCE(NULLIF(merchant_canonical,''), description_raw) as merch, "
            "ABS(amount) as amt, COALESCE(category,'') as cat "
            "FROM transactions "
            "WHERE date >= date('now', '-30 days') AND amount < -50000 "
            "AND COALESCE(category,'') NOT IN "
            "('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
            "ORDER BY amount ASC LIMIT 10"
        ).fetchall()
        if large:
            lines.append("\nLarge transactions (last 30 days, >$500):")
            for r in large:
                lines.append(
                    "  %s: %s $%s [%s]"
                    % (r["date"], r["merch"],
                       "{:,.0f}".format(r["amt"]), r["cat"] or "uncategorized")
                )

    except Exception:
        pass
    finally:
        if conn is not None:
            conn.close()

    return "\n".join(lines)


def _gather_subscriptions_context(entity_key: str) -> str:
    """Subscription context: watchlist items, costs, statuses."""
    lines = []
    lines.append("=== SUBSCRIPTION DATA ===")

    conn = None
    try:
        conn = get_connection(entity_key)

        # Active subscriptions
        subs = conn.execute(
            "SELECT merchant, amount_cents, frequency, status, notes "
            "FROM subscription_watchlist ORDER BY amount_cents DESC"
        ).fetchall()

        if subs:
            monthly_total = 0
            lines.append("\nWatchlist (%d subscriptions):" % len(subs))
            for s in subs:
                amt = "$%.2f" % (abs(s["amount_cents"]) / 100)
                status = s["status"] or "watching"
                freq = s["frequency"] or "monthly"
                lines.append(
                    "  %s: %s/%s [%s]"
                    % (s["merchant"], amt, freq, status)
                )
                if status == "watching" and freq == "monthly":
                    monthly_total += abs(s["amount_cents"])

            if monthly_total:
                lines.append(
                    "\nTotal active monthly: $%.2f ($%.2f/year)"
                    % (monthly_total / 100, monthly_total * 12 / 100)
                )
        else:
            lines.append("\nNo subscriptions tracked yet.")

    except Exception:
        pass
    finally:
        if conn is not None:
            conn.close()

    # Also include general financial context
    lines.append("")
    lines.append(_gather_general_context(entity_key))

    return "\n".join(lines)


def _gather_cashflow_context(entity_key: str) -> str:
    """Cash flow context: account balances, credit utilization, upcoming bills."""
    lines = []
    lines.append("=== CASH FLOW DATA ===")

    cross_keys = _CROSS_ENTITY.get(entity_key, [])
    for ek in [entity_key] + cross_keys:
        conn = None
        try:
            conn = get_connection(ek)
            display = _ENTITY_DISPLAY.get(ek, ek)

            accts = conn.execute(
                "SELECT account_name, balance_cents, account_type, "
                "credit_limit_cents, payment_due_day, payment_amount_cents "
                "FROM account_balances ORDER BY sort_order"
            ).fetchall()
            if accts:
                lines.append("\n%s accounts:" % display)
                total_bank = 0
                total_cc_balance = 0
                total_cc_limit = 0
                for a in accts:
                    bal = abs(a["balance_cents"]) / 100
                    if a["account_type"] == "credit_card":
                        total_cc_balance += abs(a["balance_cents"])
                        limit_str = ""
                        if a["credit_limit_cents"]:
                            total_cc_limit += a["credit_limit_cents"]
                            util = abs(a["balance_cents"]) / a["credit_limit_cents"] * 100
                            limit_str = " / $%s limit (%.0f%% used)" % (
                                "{:,.0f}".format(a["credit_limit_cents"] / 100),
                                util)
                        due_str = ""
                        if a["payment_due_day"]:
                            due_str = ", due day %d" % a["payment_due_day"]
                            if a["payment_amount_cents"]:
                                due_str += " ($%s)" % "{:,.0f}".format(
                                    a["payment_amount_cents"] / 100)
                        lines.append(
                            "  %s [credit]: $%s%s%s"
                            % (a["account_name"], "{:,.0f}".format(bal),
                               limit_str, due_str)
                        )
                    else:
                        total_bank += abs(a["balance_cents"])
                        lines.append(
                            "  %s [bank]: $%s"
                            % (a["account_name"], "{:,.0f}".format(bal))
                        )

                lines.append(
                    "  TOTAL: $%s in bank, $%s credit card debt"
                    % ("{:,.0f}".format(total_bank / 100),
                       "{:,.0f}".format(total_cc_balance / 100))
                )
                if total_cc_limit:
                    lines.append(
                        "  Overall credit utilization: %.0f%%"
                        % (total_cc_balance / total_cc_limit * 100)
                    )

            # Manual recurring
            recurring = conn.execute(
                "SELECT ab.account_name, mr.merchant, mr.amount_cents, mr.day_of_month "
                "FROM manual_recurring mr "
                "JOIN account_balances ab ON ab.id = mr.account_id "
                "ORDER BY mr.day_of_month"
            ).fetchall()
            if recurring:
                lines.append("\n  Recurring charges (%s):" % display)
                for r in recurring:
                    lines.append(
                        "    %s: $%s on day %d (%s)"
                        % (r["merchant"],
                           "{:,.0f}".format(abs(r["amount_cents"]) / 100),
                           r["day_of_month"], r["account_name"])
                    )

        except Exception:
            pass
        finally:
            if conn is not None:
                conn.close()

    return "\n".join(lines)


def _gather_reports_context(entity_key: str) -> str:
    """Reports context: monthly trends, category comparisons."""
    lines = []
    lines.append("=== REPORTS DATA ===")

    conn = None
    try:
        conn = get_connection(entity_key)

        # 12-month trend
        rows = conn.execute(
            "SELECT strftime('%%Y-%%m', date) as month, "
            "ABS(SUM(CASE WHEN amount < 0 AND COALESCE(category,'') "
            "NOT IN ('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
            "THEN amount ELSE 0 END)) as spend, "
            "SUM(CASE WHEN amount > 0 AND COALESCE(category,'') "
            "NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout') "
            "THEN amount ELSE 0 END) as income "
            "FROM transactions "
            "WHERE date >= date('now', '-12 months') "
            "GROUP BY month ORDER BY month"
        ).fetchall()
        if rows:
            lines.append("\n12-month spending trend:")
            for r in rows:
                net = (r["income"] or 0) - (r["spend"] or 0)
                lines.append(
                    "  %s: $%s spent, $%s income, net %s$%s"
                    % (r["month"], "{:,.0f}".format(r["spend"] or 0),
                       "{:,.0f}".format(r["income"] or 0),
                       "+" if net >= 0 else "-",
                       "{:,.0f}".format(abs(net)))
                )

        # This month vs last month by category
        today = date.today()
        this_month = today.strftime("%Y-%m")
        if today.month == 1:
            last_month = "%d-12" % (today.year - 1)
        else:
            last_month = "%d-%02d" % (today.year, today.month - 1)

        for period, label in [(this_month, "This month"), (last_month, "Last month")]:
            cat_rows = conn.execute(
                "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
                "ABS(SUM(amount)) as total "
                "FROM transactions "
                "WHERE strftime('%%Y-%%m', date) = ? AND amount < 0 "
                "AND COALESCE(category,'') NOT IN "
                "('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout') "
                "GROUP BY cat ORDER BY total DESC LIMIT 10"
                , (period,)
            ).fetchall()
            if cat_rows:
                lines.append("\n%s categories:" % label)
                for r in cat_rows:
                    lines.append(
                        "  %s: $%s" % (r["cat"], "{:,.0f}".format(r["total"]))
                    )

    except Exception:
        pass
    finally:
        if conn is not None:
            conn.close()

    return "\n".join(lines)


# ── Markdown → HTML Formatter ───────────────────────────────────────────────


def _format_ai_response(text: str) -> str:
    """Convert markdown AI response text to HTML."""
    from markupsafe import escape

    text = str(escape(text))

    # Inline formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    lines = text.split('\n')
    html_lines = []
    list_type = None
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()

        # Markdown table
        if '|' in stripped and stripped.startswith('|') and stripped.endswith('|'):
            _close_list(html_lines, list_type)
            list_type = None
            table_rows = []
            while i < len(lines) and '|' in lines[i].strip() and lines[i].strip().startswith('|'):
                table_rows.append(lines[i].strip())
                i += 1
            html_lines.append(_render_table(table_rows))
            continue

        # Headers
        if stripped.startswith('### '):
            _close_list(html_lines, list_type)
            list_type = None
            html_lines.append('<h5>%s</h5>' % stripped[4:])
            i += 1
            continue
        if stripped.startswith('## '):
            _close_list(html_lines, list_type)
            list_type = None
            html_lines.append('<h4>%s</h4>' % stripped[3:])
            i += 1
            continue
        if stripped.startswith('# '):
            _close_list(html_lines, list_type)
            list_type = None
            html_lines.append('<h3>%s</h3>' % stripped[2:])
            i += 1
            continue

        # Bullet list
        if stripped.startswith('- ') or stripped.startswith('• '):
            if list_type != 'ul':
                _close_list(html_lines, list_type)
                html_lines.append('<ul>')
                list_type = 'ul'
            html_lines.append('<li>%s</li>' % stripped[2:])
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            if list_type != 'ol':
                _close_list(html_lines, list_type)
                html_lines.append('<ol>')
                list_type = 'ol'
            html_lines.append('<li>%s</li>' % m.group(2))
            i += 1
            continue

        # Regular text
        _close_list(html_lines, list_type)
        list_type = None
        if stripped:
            html_lines.append('<p>%s</p>' % stripped)
        i += 1

    _close_list(html_lines, list_type)
    return '\n'.join(html_lines)


def _render_table(rows: list[str]) -> str:
    """Convert markdown table rows to HTML."""
    if not rows:
        return ''

    def _parse_row(row: str) -> list[str]:
        cells = row.strip('|').split('|')
        return [c.strip() for c in cells]

    has_header = len(rows) > 1 and all(
        c.strip().replace('-', '').replace(':', '') == ''
        for c in rows[1].strip('|').split('|')
    )

    html = '<table class="ai-chat-table">'
    if has_header:
        cells = _parse_row(rows[0])
        html += '<thead><tr>'
        for c in cells:
            html += '<th>%s</th>' % c
        html += '</tr></thead><tbody>'
        data_rows = rows[2:]
    else:
        html += '<tbody>'
        data_rows = rows

    for row in data_rows:
        cells = _parse_row(row)
        html += '<tr>'
        for c in cells:
            html += '<td>%s</td>' % c
        html += '</tr>'

    html += '</tbody></table>'
    return html


def _close_list(html_lines: list, list_type: str | None):
    if list_type == 'ul':
        html_lines.append('</ul>')
    elif list_type == 'ol':
        html_lines.append('</ol>')

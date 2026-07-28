"""Global AI chat — Ask Opus on every page with page-specific context."""
from __future__ import annotations

import logging
import re
from datetime import date

from flask import Blueprint, request, g

from core.db import get_connection
from core.ai_client import chat_completion, MODEL_OPUS

log = logging.getLogger(__name__)

bp = Blueprint("ai", __name__, url_prefix="/ai")

_ENTITY_DISPLAY = {
    "personal": "Personal",
    "company": "BFM",
    "luxelegacy": "LL",
}

# Valid page names for context dispatch
_VALID_PAGES = {
    "planning", "short-term-planning", "dashboard", "transactions",
    "subscriptions", "cashflow", "reports",
}

_ASK_PROVIDER_POLICY = {
    "zdr": True,
    "data_collection": "deny",
}


# ── System Prompts ──────────────────────────────────────────────────────────

_BASE_SYSTEM = """You are an AI explainer embedded in an expense tracking app called \
The Ledger. Answer only from the approved current-page summary supplied with this question. \
Do not imply access to other entities, accounts, transactions, notes, or prior questions. \
Be concise, show calculations when useful, and clearly distinguish facts from suggestions. \
Remind the user to verify important information before making a financial decision."""

_PAGE_PROMPTS = {
    "planning": """You specialize in long-term financial planning and net worth projections.
Your role: answer financial planning questions using the specific data provided.
Run scenarios when asked ("what if I pay extra $500/mo on the mortgage?").
When doing projections, show the math briefly so they can verify.
The projections in the data are already inflation-adjusted to today's dollars.
When doing your own calculations, adjust for inflation unless told otherwise.""",

    "dashboard": """You specialize in analyzing spending patterns and financial health.
Your role: help the user understand their spending, identify trends, and spot opportunities.
Reference only categories, aggregate merchants, and dollar amounts present in the summary.
Compare periods when data is available. Suggest actionable changes.""",

    "transactions": """You specialize in transaction analysis and categorization.
Your role: help the user understand their transaction patterns, find specific charges,
identify patterns, and optimize spending by category or aggregate merchant.
Do not imply that individual transaction rows were supplied.""",

    "subscriptions": """You specialize in subscription management and cost optimization.
Your role: help the user evaluate their subscriptions, identify cancellation candidates,
spot price changes, and estimate savings from cutting services.
Reference specific subscription names, amounts, and frequencies from the data.""",

    "short-term-planning": """You explain debt payoff and budgeting tradeoffs using \
the approved active-entity summaries for goals, budgets, balances, and spending categories. \
Help them build and refine practical plans without inferring account identities or private notes. \
Show the impact on payoff timelines when the supplied summary supports it.""",

    "cashflow": """You specialize in cash flow management and account health.
Your role: help the user understand their account balances, credit utilization,
upcoming bills, and cash flow timing. Use only aggregate balances and schedules; do not infer \
account or merchant identities.""",

    "reports": """You specialize in financial reporting and trend analysis.
Your role: help the user understand their spending trends over time,
compare month-over-month or year-over-year patterns, and identify long-term shifts.
Reference specific months, categories, and dollar amounts.""",
}


def _get_system_prompt(page: str) -> str:
    """Build the system prompt for a given page."""
    page_extra = _PAGE_PROMPTS.get(page, "")
    return _BASE_SYSTEM + ("\n\n" + page_extra if page_extra else "")


# ── Endpoints ───────────────────────────────────────────────────────────────


@bp.route("/ask", methods=["POST"])
def ask():
    """Handle AI chat question via HTMX — works from any page."""
    question = request.form.get("question", "").strip()
    if not question:
        return '<div class="ai-chat-error">Please enter a question.</div>'

    page = request.form.get("page", "").strip()
    if page not in _VALID_PAGES:
        return (
            '<div class="ai-chat-error">Ask Opus is not available for this page.</div>',
            400,
        )

    entity_key = g.entity_key

    try:
        context = _gather_context(entity_key, page)
    except Exception:
        log.exception("Ask Opus context gathering failed (page=%s)", page)
        return (
            '<div class="ai-chat-error">Ask Opus could not prepare a private page summary.</div>',
            503,
        )

    messages = [{
            "role": "user",
            "content": "Here is the approved current-page summary:\n\n%s\n\nQuestion: %s"
            % (context, question),
    }]

    response = chat_completion(
        messages=messages,
        model=MODEL_OPUS,
        max_tokens=1500,
        system=_get_system_prompt(page),
        timeout=60,
        provider=_ASK_PROVIDER_POLICY,
    )

    if not response:
        return (
            '<div class="ai-chat-error">Ask Opus is unavailable because its private '
            'provider requirements could not be satisfied.</div>',
            503,
        )

    from markupsafe import escape
    escaped_q = escape(question)
    escaped_r = _format_ai_response(response)

    return (
        '<div class="ai-chat-pair">'
        '<div class="ai-chat-q">%s</div>'
        '<div class="ai-chat-a">%s</div>'
        '</div>' % (escaped_q, escaped_r)
    )


# ── Context Dispatcher ──────────────────────────────────────────────────────


def _gather_context(entity_key: str, page: str) -> str:
    """Dispatch to the right context builder based on page."""
    builders = {
        "planning": _gather_planning_context,
        "short-term-planning": _gather_short_term_planning_context,
        "dashboard": _gather_dashboard_context,
        "transactions": _gather_transactions_context,
        "subscriptions": _gather_subscriptions_context,
        "cashflow": _gather_cashflow_context,
        "reports": _gather_reports_context,
    }
    return builders[page](entity_key)


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


def _gather_planning_context(entity_key: str) -> str:
    """Full planning context: assets, liabilities, projections, spending."""
    # Import planning helpers — they live in planning.py
    from web.routes.planning import (
        _get_settings, _get_milestones, _load_entity_section,
    )

    settings = _get_settings()
    milestones = _get_milestones(settings)

    section = _load_entity_section(entity_key, settings)

    lines = []
    lines.append("=== PLANNING DATA ===")
    lines.append(
        "Settings: Age %d, Inflation %.1f%%, Milestones: %s"
        % (
            settings["current_age"],
            settings["inflation_rate"] / 100,
            ", ".join(str(m) for m in milestones),
        )
    )
    lines.append("")

    assets = section["assets"]
    liabilities = section["liabilities"]
    today = section["summary"]["today"]
    lines.append(
        "%s totals: %d assets worth %s; %d liabilities totaling %s"
        % (
            section["entity_display"],
            len(assets),
            _fmt_k(today["assets_cents"]),
            len(liabilities),
            _fmt_k(today["liabilities_cents"]),
        )
    )
    lines.append(
        "Monthly contributions: %s; monthly debt payments: %s"
        % (
            _fmt_k(sum(a["monthly_contrib_cents"] for a in assets)),
            _fmt_k(sum(li["monthly_payment_cents"] for li in liabilities)),
        )
    )
    lines.append(
        "Net worth: Today %s → %s"
        % (
            _fmt_k(today["net_worth_cents"]),
            ", ".join(
                "@%d: %s"
                % (m, _fmt_k(section["summary"][m]["net_worth_cents"]))
                for m in milestones
            ),
        )
    )

    return "\n".join(lines)


def _gather_short_term_planning_context(entity_key: str) -> str:
    """Short-term planning context: goals, budgets, progress, spending patterns."""
    import json as _json
    lines = []
    lines.append("=== SHORT-TERM PLANNING DATA ===")

    conn = None
    try:
        conn = get_connection(entity_key)

        # Active goals
        goals = conn.execute(
            "SELECT * FROM short_term_goals WHERE status = 'active' ORDER BY created_at"
        ).fetchall()
        if goals:
            lines.append("\nActive goals:")
            for g in goals:
                linked = _json.loads(g["linked_accounts"] or "[]")
                total_bal = 0
                for acct_name in linked:
                    bal_row = conn.execute(
                        "SELECT balance_cents FROM account_balances WHERE account_name = ?",
                        (acct_name,),
                    ).fetchone()
                    if bal_row:
                        total_bal += abs(bal_row["balance_cents"])
                lines.append(
                    "  %s [%s]: balance $%s, target %s, monthly $%s"
                    % (
                        g["name"],
                        g["goal_type"],
                        "{:,.0f}".format(total_bal / 100),
                        g["target_date"] or "not set",
                        "{:,.0f}".format((g["monthly_amount_cents"] or 0) / 100),
                    )
                )
                # Recent snapshots
                snaps = conn.execute(
                    "SELECT snapshot_date, balance_cents FROM goal_snapshots "
                    "WHERE goal_id = ? ORDER BY snapshot_date DESC LIMIT 6",
                    (g["id"],),
                ).fetchall()
                if snaps:
                    lines.append(
                        "    Recent progress balances: "
                        + ", ".join(
                            "$%s" % "{:,.0f}".format(s["balance_cents"] / 100)
                            for s in reversed(snaps)
                        )
                    )
        else:
            lines.append("\nNo active goals.")

        # Aggregate credit card summary without account labels
        cc_accts = conn.execute(
            "SELECT account_name, balance_cents, credit_limit_cents, "
            "payment_due_day, payment_amount_cents "
            "FROM account_balances WHERE account_type = 'credit_card' "
            "ORDER BY sort_order"
        ).fetchall()
        if cc_accts:
            total_balance = sum(abs(a["balance_cents"]) for a in cc_accts)
            total_limit = sum(a["credit_limit_cents"] or 0 for a in cc_accts)
            lines.append("\nCredit cards:")
            lines.append(
                "  %d cards, $%s total balance, $%s total limit"
                % (
                    len(cc_accts),
                    "{:,.0f}".format(total_balance / 100),
                    "{:,.0f}".format(total_limit / 100),
                )
            )
            if total_limit:
                lines.append(
                    "  Overall utilization: %.0f%%"
                    % (total_balance / total_limit * 100)
                )

        # Budget vs actuals
        from datetime import date as _date
        this_month = _date.today().strftime("%Y-%m")
        budget_rows = conn.execute("SELECT * FROM budget_items ORDER BY category").fetchall()
        if budget_rows:
            lines.append("\nBudget vs actuals (%s):" % this_month)
            for bi in budget_rows:
                spent_row = conn.execute(
                    "SELECT ABS(SUM(amount)) as total FROM transactions "
                    "WHERE strftime('%Y-%m', date) = ? AND amount < 0 "
                    "AND COALESCE(category,'') = ?",
                    (this_month, bi["category"]),
                ).fetchone()
                spent = int(round((spent_row["total"] or 0) * 100))
                budget = bi["monthly_budget_cents"]
                pct = int(round(spent / budget * 100)) if budget > 0 else 0
                lines.append(
                    "  %s: $%s budgeted, $%s spent (%d%%)"
                    % (bi["category"], "{:,.0f}".format(budget / 100),
                       "{:,.0f}".format(spent / 100), pct)
                )

    except Exception:
        log.exception("Error gathering short-term planning context")
        raise
    finally:
        if conn is not None:
            conn.close()

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
            "WHERE strftime('%Y-%m', date) = ?"
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
            "WHERE strftime('%Y-%m', date) = ? "
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
            "WHERE strftime('%Y-%m', date) = ? "
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
            "SELECT strftime('%Y-%m', date) as month, "
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
        log.exception("Error gathering dashboard context")
        raise
    finally:
        if conn is not None:
            conn.close()

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
            "GROUP BY merch ORDER BY total DESC LIMIT 15"
        ).fetchall()
        if merch_rows:
            lines.append("\nMost frequent merchants (90 days):")
            for r in merch_rows:
                lines.append(
                    "  %s: %d times, $%s total"
                    % (r["merch"], r["cnt"], "{:,.0f}".format(r["total"]))
                )

    except Exception:
        log.exception("Error gathering transactions context")
        raise
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
        log.exception("Error gathering subscriptions context")
        raise
    finally:
        if conn is not None:
            conn.close()

    return "\n".join(lines)


def _gather_cashflow_context(entity_key: str) -> str:
    """Cash flow context: active-entity aggregate balances and schedules."""
    lines = []
    lines.append("=== CASH FLOW DATA ===")

    conn = None
    try:
        conn = get_connection(entity_key)
        accts = conn.execute(
            "SELECT balance_cents, account_type, credit_limit_cents, "
            "payment_due_day, payment_amount_cents "
            "FROM account_balances ORDER BY sort_order"
        ).fetchall()
        bank = [a for a in accts if a["account_type"] != "credit_card"]
        cards = [a for a in accts if a["account_type"] == "credit_card"]
        total_bank = sum(abs(a["balance_cents"]) for a in bank)
        total_cc_balance = sum(abs(a["balance_cents"]) for a in cards)
        total_cc_limit = sum(a["credit_limit_cents"] or 0 for a in cards)

        lines.append(
            "\n%s summary: %d bank accounts totaling $%s; "
            "%d credit cards totaling $%s"
            % (
                _ENTITY_DISPLAY.get(entity_key, entity_key),
                len(bank),
                "{:,.0f}".format(total_bank / 100),
                len(cards),
                "{:,.0f}".format(total_cc_balance / 100),
            )
        )
        if total_cc_limit:
            lines.append(
                "Overall credit limit: $%s; utilization: %.0f%%"
                % (
                    "{:,.0f}".format(total_cc_limit / 100),
                    total_cc_balance / total_cc_limit * 100,
                )
            )

        due = [
            a for a in cards
            if a["payment_due_day"] and a["payment_amount_cents"]
        ]
        if due:
            lines.append("\nScheduled card payments:")
            for a in due:
                lines.append(
                    "  Day %d: $%s"
                    % (
                        a["payment_due_day"],
                        "{:,.0f}".format(a["payment_amount_cents"] / 100),
                    )
                )

        recurring = conn.execute(
            "SELECT amount_cents, day_of_month FROM manual_recurring "
            "ORDER BY day_of_month"
        ).fetchall()
        if recurring:
            lines.append(
                "\nManual recurring schedule: %d items totaling $%s monthly"
                % (
                    len(recurring),
                    "{:,.0f}".format(
                        sum(abs(r["amount_cents"]) for r in recurring) / 100
                    ),
                )
            )
            for r in recurring:
                lines.append(
                    "  Day %d: $%s"
                    % (
                        r["day_of_month"],
                        "{:,.0f}".format(abs(r["amount_cents"]) / 100),
                    )
                )
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
            "SELECT strftime('%Y-%m', date) as month, "
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
                "WHERE strftime('%Y-%m', date) = ? AND amount < 0 "
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
        log.exception("Error gathering reports context")
        raise
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

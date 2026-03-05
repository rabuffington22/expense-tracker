"""Planning page — long-term net worth projections + AI planning chat."""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import date, datetime, timezone

from flask import Blueprint, render_template, request, g, redirect, url_for, jsonify

from core.db import get_connection, init_db
from core.ai_client import chat_completion, MODEL_OPUS

log = logging.getLogger(__name__)

bp = Blueprint("planning", __name__, url_prefix="/planning")

# Temp dir for conversation history (survives page reloads within session)
_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-planning")
os.makedirs(_TEMP_DIR, exist_ok=True)

# Cross-entity visibility: Personal ↔ BFM share view, LL excluded.
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


# ── Helpers ──────────────────────────────────────────────────────────────────


def _parse_dollar_to_cents(dollar_str: str) -> int:
    """Parse '$1,234.56' or '1234.56' into cents (123456)."""
    try:
        cleaned = dollar_str.replace(",", "").replace("$", "").strip()
        return int(round(float(cleaned) * 100))
    except (ValueError, TypeError):
        return 0


def _parse_rate_to_bps(rate_str: str) -> int:
    """Parse '7.0' or '7' into basis points (700)."""
    try:
        cleaned = rate_str.replace("%", "").strip()
        return int(round(float(cleaned) * 100))
    except (ValueError, TypeError):
        return 0


def _compute_age(birth_date_str: str | None) -> int:
    """Compute current age from a YYYY-MM-DD birth date string."""
    if not birth_date_str:
        return 48  # fallback
    try:
        from datetime import date
        bd = date.fromisoformat(birth_date_str)
        today = date.today()
        age = today.year - bd.year
        if (today.month, today.day) < (bd.month, bd.day):
            age -= 1
        return age
    except (ValueError, TypeError):
        return 48


def _get_settings() -> dict:
    """Read planning settings from personal.sqlite (global singleton)."""
    conn = get_connection("personal")
    try:
        row = conn.execute("SELECT * FROM planning_settings WHERE id = 1").fetchone()
        if row:
            d = dict(row)
            # Auto-compute age from birth_date if available
            d["current_age"] = _compute_age(d.get("birth_date"))
            return d
        return {"inflation_rate": 300, "current_age": 48, "custom_milestone": None, "birth_date": None}
    finally:
        conn.close()


def _get_milestones(settings: dict) -> list[int]:
    """Return sorted list of milestone ages."""
    milestones = [60, 65, 70]
    custom = settings.get("custom_milestone")
    if custom and custom not in milestones:
        milestones.append(custom)
        milestones.sort()
    return milestones


def _get_items(entity_key: str) -> dict:
    """Read planning items from the entity's DB. Pull live balances for cashflow-linked items."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT * FROM planning_items ORDER BY item_type, sort_order, name"
        ).fetchall()
        items = {"assets": [], "liabilities": []}
        for r in rows:
            d = dict(r)
            # Pull live balance from account_balances if linked
            if d["source"] == "cashflow" and d["cashflow_account_name"]:
                bal_row = conn.execute(
                    "SELECT balance_cents FROM account_balances WHERE account_name = ?",
                    (d["cashflow_account_name"],),
                ).fetchone()
                if bal_row:
                    d["current_value_cents"] = abs(bal_row["balance_cents"])
            bucket = "assets" if d["item_type"] == "asset" else "liabilities"
            items[bucket].append(d)
        return items
    finally:
        conn.close()


def _compute_projections(items: dict, settings: dict) -> dict:
    """Compute projected values at each milestone age for all items."""
    inflation = settings["inflation_rate"] / 10000  # bps to decimal
    age = settings["current_age"]
    milestones = _get_milestones(settings)

    for asset in items["assets"]:
        r = asset["annual_rate_bps"] / 10000  # annual appreciation
        V = asset["current_value_cents"] / 100  # dollars
        C = asset["monthly_contrib_cents"] / 100 * 12  # annual contribution
        asset["projections"] = {}
        for m_age in milestones:
            n = m_age - age
            if n <= 0:
                asset["projections"][m_age] = asset["current_value_cents"]
                continue
            # FV = V*(1+r)^n + C*((1+r)^n - 1)/r
            if r > 0:
                growth = (1 + r) ** n
                fv = V * growth + C * (growth - 1) / r
            else:
                fv = V + C * n  # no growth, just contributions
            # Inflation-adjust to today's dollars
            real_fv = fv / ((1 + inflation) ** n) if inflation > 0 else fv
            asset["projections"][m_age] = int(round(real_fv * 100))

    for liab in items["liabilities"]:
        m_rate = (liab["annual_rate_bps"] / 10000) / 12  # monthly interest rate
        B0 = liab["current_value_cents"] / 100  # dollars
        P = liab["monthly_payment_cents"] / 100  # monthly payment
        liab["projections"] = {}
        for m_age in milestones:
            n = m_age - age
            if n <= 0:
                liab["projections"][m_age] = liab["current_value_cents"]
                continue
            t = n * 12  # months
            if m_rate > 0 and P > 0:
                growth = (1 + m_rate) ** t
                balance = B0 * growth - P * (growth - 1) / m_rate
            elif P > 0:
                balance = B0 - P * t  # 0% interest
            else:
                balance = B0  # no payments (e.g., auto-pulled CC balance)
            if balance < 0:
                balance = 0  # paid off
            # Inflation-adjust
            real_balance = balance / ((1 + inflation) ** n) if inflation > 0 else balance
            liab["projections"][m_age] = int(round(real_balance * 100))

    return items


def _compute_summary(items: dict, milestones: list[int]) -> dict:
    """Compute net worth at each milestone and today."""
    summary = {}
    for m in milestones:
        total_assets = sum(a["projections"].get(m, 0) for a in items["assets"])
        total_liab = sum(l["projections"].get(m, 0) for l in items["liabilities"])
        summary[m] = {
            "assets_cents": total_assets,
            "liabilities_cents": total_liab,
            "net_worth_cents": total_assets - total_liab,
        }
    # Today
    today_assets = sum(a["current_value_cents"] for a in items["assets"])
    today_liab = sum(l["current_value_cents"] for l in items["liabilities"])
    summary["today"] = {
        "assets_cents": today_assets,
        "liabilities_cents": today_liab,
        "net_worth_cents": today_assets - today_liab,
    }
    return summary


def _load_entity_section(entity_key: str, settings: dict) -> dict:
    """Load items, compute projections, return dict for template."""
    init_db(entity_key)
    items = _get_items(entity_key)
    items = _compute_projections(items, settings)
    milestones = _get_milestones(settings)
    summary = _compute_summary(items, milestones)
    return {
        "entity_key": entity_key,
        "entity_display": _ENTITY_DISPLAY.get(entity_key, entity_key),
        "assets": items["assets"],
        "liabilities": items["liabilities"],
        "summary": summary,
    }


def _get_cashflow_accounts(entity_key: str) -> list[str]:
    """Return list of account names from account_balances for dropdown."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT account_name FROM account_balances ORDER BY sort_order, account_name"
        ).fetchall()
        return [r["account_name"] for r in rows]
    except Exception:
        return []
    finally:
        conn.close()


# ── Routes ───────────────────────────────────────────────────────────────────


@bp.route("/")
def index():
    # LL guard — redirect to home
    if g.entity_key == "luxelegacy":
        return redirect(url_for("dashboard.index"))

    settings = _get_settings()
    milestones = _get_milestones(settings)

    # Primary entity
    primary = _load_entity_section(g.entity_key, settings)

    # Cross-entity sections
    cross_sections = []
    for other_key in _CROSS_ENTITY.get(g.entity_key, []):
        section = _load_entity_section(other_key, settings)
        cross_sections.append(section)

    # Combined net worth across all visible entities
    all_sections = [primary] + cross_sections
    combined = {"today": {"net_worth_cents": 0}}
    for m in milestones:
        combined[m] = {"net_worth_cents": 0}
    for sec in all_sections:
        combined["today"]["net_worth_cents"] += sec["summary"]["today"]["net_worth_cents"]
        for m in milestones:
            combined[m]["net_worth_cents"] += sec["summary"][m]["net_worth_cents"]

    # Cashflow accounts for add form dropdown
    cf_accounts = {}
    cf_accounts[g.entity_key] = _get_cashflow_accounts(g.entity_key)
    for other_key in _CROSS_ENTITY.get(g.entity_key, []):
        cf_accounts[other_key] = _get_cashflow_accounts(other_key)

    return render_template(
        "planning.html",
        settings=settings,
        milestones=milestones,
        primary=primary,
        cross_sections=cross_sections,
        combined=combined,
        cf_accounts=cf_accounts,
    )


@bp.route("/settings", methods=["POST"])
def update_settings():
    inflation = _parse_rate_to_bps(request.form.get("inflation_rate", "3.0"))
    custom_raw = request.form.get("custom_milestone", "").strip()
    custom = int(custom_raw) if custom_raw else None
    birth_date = request.form.get("birth_date", "").strip() or None

    # Compute age from birth_date for milestone validation
    age = _compute_age(birth_date) if birth_date else 48
    if custom is not None and (custom <= age or custom > 120):
        custom = None

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection("personal")
    try:
        conn.execute(
            "UPDATE planning_settings SET inflation_rate = ?, current_age = ?, "
            "custom_milestone = ?, birth_date = ?, updated_at = ? WHERE id = 1",
            (inflation, age, custom, birth_date, now),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("planning.index"))


@bp.route("/items/add", methods=["POST"])
def add_item():
    entity_key = request.form.get("entity_key", g.entity_key)
    item_type = request.form.get("item_type", "asset")
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("planning.index"))

    value_cents = _parse_dollar_to_cents(request.form.get("current_value", "0"))
    rate_bps = _parse_rate_to_bps(request.form.get("annual_rate", "0"))
    contrib_cents = _parse_dollar_to_cents(request.form.get("monthly_contrib", "0"))
    payment_cents = _parse_dollar_to_cents(request.form.get("monthly_payment", "0"))
    source = request.form.get("source", "manual")
    cf_account = request.form.get("cashflow_account_name", "").strip() or None

    if source != "cashflow":
        cf_account = None

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(entity_key)
    try:
        # Auto sort_order: put new items at the end
        max_sort = conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) FROM planning_items WHERE item_type = ?",
            (item_type,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO planning_items "
            "(item_type, name, current_value_cents, annual_rate_bps, "
            "monthly_contrib_cents, monthly_payment_cents, source, "
            "cashflow_account_name, sort_order, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (item_type, name, value_cents, rate_bps, contrib_cents,
             payment_cents, source, cf_account, max_sort + 1, now, now),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("planning.index"))


@bp.route("/items/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    entity_key = request.form.get("entity_key", g.entity_key)
    name = request.form.get("name", "").strip()
    value_cents = _parse_dollar_to_cents(request.form.get("current_value", "0"))
    rate_bps = _parse_rate_to_bps(request.form.get("annual_rate", "0"))
    contrib_cents = _parse_dollar_to_cents(request.form.get("monthly_contrib", "0"))
    payment_cents = _parse_dollar_to_cents(request.form.get("monthly_payment", "0"))
    source = request.form.get("source", "manual")
    cf_account = request.form.get("cashflow_account_name", "").strip() or None

    if source != "cashflow":
        cf_account = None

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(entity_key)
    try:
        conn.execute(
            "UPDATE planning_items SET name = ?, current_value_cents = ?, "
            "annual_rate_bps = ?, monthly_contrib_cents = ?, "
            "monthly_payment_cents = ?, source = ?, cashflow_account_name = ?, "
            "updated_at = ? WHERE id = ?",
            (name, value_cents, rate_bps, contrib_cents, payment_cents,
             source, cf_account, now, item_id),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("planning.index"))


@bp.route("/items/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    entity_key = request.form.get("entity_key", g.entity_key)
    conn = get_connection(entity_key)
    try:
        conn.execute("DELETE FROM planning_items WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("planning.index"))


@bp.route("/cashflow-accounts/<entity_key>")
def cashflow_accounts(entity_key):
    """HTMX helper: return <option> tags for cashflow account dropdown."""
    accounts = _get_cashflow_accounts(entity_key)
    html = '<option value="">Select account...</option>'
    for name in accounts:
        html += f'<option value="{name}">{name}</option>'
    return html


# ── AI Planning Chat ──────────────────────────────────────────────────────────


def _gather_planning_context(entity_key: str) -> str:
    """Build a comprehensive context string for the AI with all planning data."""
    settings = _get_settings()
    milestones = _get_milestones(settings)

    # Load all visible entity sections
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
                    "@%d: $%s" % (m, _fmt_k_plain(a["projections"].get(m, 0)))
                    for m in milestones
                ]
                lines.append(
                    "  %s: $%s value, %.1f%% appr, $%s/mo contrib → %s"
                    % (
                        a["name"],
                        _fmt_k_plain(a["current_value_cents"]),
                        a["annual_rate_bps"] / 100,
                        "{:,.0f}".format(a["monthly_contrib_cents"] / 100)
                        if a["monthly_contrib_cents"]
                        else "0",
                        ", ".join(proj_parts),
                    )
                )
        if sec["liabilities"]:
            lines.append("Liabilities:")
            for l in sec["liabilities"]:
                proj_parts = []
                for m in milestones:
                    val = l["projections"].get(m, 0)
                    proj_parts.append(
                        "@%d: %s" % (m, "Paid" if val == 0 else "$%s" % _fmt_k_plain(val))
                    )
                lines.append(
                    "  %s: $%s balance, %.2f%% rate, $%s/mo payment → %s"
                    % (
                        l["name"],
                        _fmt_k_plain(l["current_value_cents"]),
                        l["annual_rate_bps"] / 100,
                        "{:,.0f}".format(l["monthly_payment_cents"] / 100)
                        if l["monthly_payment_cents"]
                        else "0",
                        ", ".join(proj_parts),
                    )
                )
        nw = sec["summary"]
        lines.append(
            "Net Worth: Today $%s → %s"
            % (
                _fmt_k_plain(nw["today"]["net_worth_cents"]),
                ", ".join(
                    "@%d: $%s" % (m, _fmt_k_plain(nw[m]["net_worth_cents"]))
                    for m in milestones
                ),
            )
        )
        lines.append("")

    # Combined
    combined_today = sum(s["summary"]["today"]["net_worth_cents"] for s in all_sections)
    combined_parts = []
    for m in milestones:
        combined_parts.append(
            "@%d: $%s"
            % (m, _fmt_k_plain(sum(s["summary"][m]["net_worth_cents"] for s in all_sections)))
        )
    lines.append(
        "COMBINED NET WORTH: Today $%s → %s"
        % (_fmt_k_plain(combined_today), ", ".join(combined_parts))
    )
    lines.append("")

    # Spending context from transaction data (last 3 months)
    lines.append("=== RECENT SPENDING (last 3 months) ===")
    today = date.today()
    for ek in [entity_key] + cross_keys:
        try:
            conn = get_connection(ek)
            # Monthly spending totals
            rows = conn.execute(
                "SELECT strftime('%%Y-%%m', date) as month, "
                "ABS(SUM(CASE WHEN amount < 0 AND COALESCE(category,'') "
                "NOT IN ('Internal Transfer','Credit Card Payment','Income') "
                "THEN amount ELSE 0 END)) as spend, "
                "SUM(CASE WHEN amount > 0 AND COALESCE(category,'') "
                "NOT IN ('Internal Transfer','Credit Card Payment') "
                "THEN amount ELSE 0 END) as income "
                "FROM transactions "
                "WHERE date >= date('now', '-3 months') "
                "GROUP BY month ORDER BY month"
            ).fetchall()
            if rows:
                display = _ENTITY_DISPLAY.get(ek, ek)
                lines.append("%s monthly:" % display)
                for r in rows:
                    lines.append(
                        "  %s: $%s spent, $%s income"
                        % (r["month"], "{:,.0f}".format(r["spend"]), "{:,.0f}".format(r["income"]))
                    )
            # Top categories this month
            cat_rows = conn.execute(
                "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
                "ABS(SUM(amount)) as total "
                "FROM transactions "
                "WHERE strftime('%%Y-%%m', date) = strftime('%%Y-%%m', 'now') "
                "AND amount < 0 "
                "AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Income') "
                "GROUP BY cat ORDER BY total DESC LIMIT 8"
            ).fetchall()
            if cat_rows:
                lines.append("  Top categories this month: %s" % ", ".join(
                    "%s $%s" % (r["cat"], "{:,.0f}".format(r["total"])) for r in cat_rows
                ))
            conn.close()
        except Exception:
            pass
    lines.append("")

    # Account balances
    lines.append("=== ACCOUNT BALANCES ===")
    for ek in [entity_key] + cross_keys:
        try:
            conn = get_connection(ek)
            accts = conn.execute(
                "SELECT account_name, balance_cents, account_type, credit_limit_cents "
                "FROM account_balances ORDER BY sort_order"
            ).fetchall()
            if accts:
                display = _ENTITY_DISPLAY.get(ek, ek)
                for a in accts:
                    bal = "{:,.0f}".format(abs(a["balance_cents"]) / 100)
                    extra = ""
                    if a["account_type"] == "credit_card" and a["credit_limit_cents"]:
                        extra = " (limit $%s)" % "{:,.0f}".format(a["credit_limit_cents"] / 100)
                    lines.append("  %s [%s]: $%s%s" % (a["account_name"], display, bal, extra))
            conn.close()
        except Exception:
            pass

    return "\n".join(lines)


def _fmt_k_plain(cents: int) -> str:
    """Format cents to a readable dollar string: $964k, $2.3M, etc."""
    dollars = cents / 100
    if abs(dollars) >= 1_000_000:
        return "%.1fM" % (dollars / 1_000_000)
    if abs(dollars) >= 1000:
        return "%dk" % round(dollars / 1000)
    return "%d" % round(dollars)


def _get_conversation_path(entity_key: str) -> str:
    """Return the temp file path for the planning conversation history."""
    return os.path.join(_TEMP_DIR, "chat_%s.json" % entity_key)


def _load_conversation(entity_key: str) -> list[dict]:
    """Load conversation history from temp file."""
    path = _get_conversation_path(entity_key)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_conversation(entity_key: str, messages: list[dict]):
    """Save conversation history to temp file. Keep last 20 exchanges."""
    path = _get_conversation_path(entity_key)
    # Trim to last 20 user+assistant message pairs (40 messages)
    if len(messages) > 40:
        messages = messages[-40:]
    with open(path, "w") as f:
        json.dump(messages, f)


_PLANNING_SYSTEM = """You are a knowledgeable financial planning advisor embedded in a personal \
expense tracking app called Ledger Oak. You have full access to the user's financial data \
including assets, liabilities, projected net worth, monthly spending, income, and account balances.

Your role:
- Answer financial planning questions using the specific data provided
- Run scenarios when asked ("what if I pay extra $500/mo on the mortgage?")
- Be specific with dollar amounts and timeframes from their actual data
- Give clear, actionable advice grounded in their real numbers
- When doing projections, show the math briefly so they can verify
- Be conversational but concise — no filler, no disclaimers about not being a financial advisor
- Use plain language, not jargon

The projections in the data are already inflation-adjusted to today's dollars.
When doing your own calculations, adjust for inflation unless told otherwise.
"""


@bp.route("/ask", methods=["POST"])
def ask():
    """Handle AI planning chat question via HTMX."""
    question = request.form.get("question", "").strip()
    if not question:
        return '<div class="pl-chat-error">Please enter a question.</div>'

    entity_key = g.entity_key

    # Gather fresh context
    context = _gather_planning_context(entity_key)

    # Load conversation history
    history = _load_conversation(entity_key)

    # Build messages: first message includes context, rest are conversation
    messages = []
    if not history:
        # First question — include full context
        messages.append({
            "role": "user",
            "content": "Here is my current financial data:\n\n%s\n\nQuestion: %s" % (context, question),
        })
    else:
        # Subsequent questions — refresh context in latest question
        messages = list(history)
        messages.append({
            "role": "user",
            "content": "Updated financial data:\n\n%s\n\nQuestion: %s" % (context, question),
        })

    # Call Opus
    response = chat_completion(
        messages=messages,
        model=MODEL_OPUS,
        max_tokens=1500,
        system=_PLANNING_SYSTEM,
        timeout=60,
    )

    if not response:
        return '<div class="pl-chat-error">AI is unavailable right now. Check that OPENROUTER_API_KEY is set.</div>'

    # Save to conversation history (store clean question, not context-stuffed)
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})
    _save_conversation(entity_key, history)

    # Return HTML for the new Q&A pair
    from markupsafe import escape
    escaped_q = escape(question)
    # Convert markdown-ish response to simple HTML
    escaped_r = _format_ai_response(response)

    html = (
        '<div class="pl-chat-pair">'
        '<div class="pl-chat-q">%s</div>'
        '<div class="pl-chat-a">%s</div>'
        '</div>' % (escaped_q, escaped_r)
    )
    return html


@bp.route("/chat/clear", methods=["POST"])
def clear_chat():
    """Clear conversation history."""
    path = _get_conversation_path(g.entity_key)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return ""


def _format_ai_response(text: str) -> str:
    """Convert markdown AI response text to HTML.

    Handles: **bold**, *italic*, `inline code`, headers (#/##/###),
    bullet lists (- or •), numbered lists (1.), markdown tables, paragraphs.
    """
    import re
    from markupsafe import escape

    text = str(escape(text))

    # Inline formatting (order matters — bold before italic)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    lines = text.split('\n')
    html_lines = []
    list_type = None  # 'ul' or 'ol'
    table_rows = []   # accumulate table rows

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # Markdown table: detect | col | col | pattern
        if '|' in stripped and stripped.startswith('|') and stripped.endswith('|'):
            _close_list(html_lines, list_type)
            list_type = None
            # Accumulate all table lines
            table_rows = []
            while i < len(lines) and '|' in lines[i].strip() and lines[i].strip().startswith('|'):
                table_rows.append(lines[i].strip())
                i += 1
            html_lines.append(_render_table(table_rows))
            continue

        # Headers: # → h3, ## → h4, ### → h5 (keep proportional in chat)
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

        # Numbered list (1. 2. etc.)
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            if list_type != 'ol':
                _close_list(html_lines, list_type)
                html_lines.append('<ol>')
                list_type = 'ol'
            html_lines.append('<li>%s</li>' % m.group(2))
            i += 1
            continue

        # Regular text or blank line
        _close_list(html_lines, list_type)
        list_type = None
        if stripped:
            html_lines.append('<p>%s</p>' % stripped)
        i += 1

    _close_list(html_lines, list_type)
    return '\n'.join(html_lines)


def _render_table(rows: list[str]) -> str:
    """Convert markdown table rows to an HTML table."""
    if not rows:
        return ''

    def _parse_row(row: str) -> list[str]:
        cells = row.strip('|').split('|')
        return [c.strip() for c in cells]

    # Check if second row is a separator (|---|---|)
    has_header = len(rows) > 1 and all(
        c.strip().replace('-', '').replace(':', '') == ''
        for c in rows[1].strip('|').split('|')
    )

    html = '<table class="pl-chat-table">'
    if has_header:
        cells = _parse_row(rows[0])
        html += '<thead><tr>'
        for c in cells:
            html += '<th>%s</th>' % c
        html += '</tr></thead><tbody>'
        data_rows = rows[2:]  # skip header + separator
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
    """Close an open list tag if one is active."""
    if list_type == 'ul':
        html_lines.append('</ul>')
    elif list_type == 'ol':
        html_lines.append('</ol>')

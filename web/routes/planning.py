"""Planning page — Long-Term net worth projections."""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from flask import Blueprint, render_template, request, g, redirect, url_for, jsonify

from core.db import get_connection, init_db

log = logging.getLogger(__name__)

bp = Blueprint("planning", __name__, url_prefix="/planning")

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
    entity_key = g.entity_key
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
    entity_key = g.entity_key
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
    entity_key = g.entity_key
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
    from markupsafe import escape
    # Validate entity_key against allowed values
    allowed = {"personal", "company", "luxelegacy"}
    if entity_key not in allowed:
        return "", 404
    accounts = _get_cashflow_accounts(entity_key)
    html = '<option value="">Select account...</option>'
    for name in accounts:
        safe_name = escape(name)
        html += f'<option value="{safe_name}">{safe_name}</option>'
    return html


# (AI chat code moved to web/routes/ai.py)

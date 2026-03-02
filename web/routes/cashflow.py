"""Cash Flow page — account balances, upcoming bills, projections."""

import datetime

from flask import Blueprint, render_template, request, g, redirect, url_for

from core.db import get_connection, init_db

bp = Blueprint("cashflow", __name__, url_prefix="/cashflow")

# Cross-entity visibility: Personal ↔ BFM share view, LL is isolated.
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


def _parse_dollar_to_cents(dollar_str: str) -> int:
    """Parse '$1,234.56' or '1234.56' into cents (123456)."""
    try:
        cleaned = dollar_str.replace(",", "").replace("$", "").strip()
        return int(round(float(cleaned) * 100))
    except (ValueError, TypeError):
        return 0


def _get_accounts(conn) -> list[dict]:
    """Fetch all account balances, sorted by name."""
    rows = conn.execute(
        "SELECT * FROM account_balances ORDER BY account_name"
    ).fetchall()
    return [dict(r) for r in rows]


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    # Primary entity accounts
    conn = get_connection(g.entity_key)
    try:
        primary_accounts = _get_accounts(conn)
    finally:
        conn.close()

    # Cross-entity accounts
    cross_sections = []
    for other_key in _CROSS_ENTITY.get(g.entity_key, []):
        init_db(other_key)  # Ensure migrations run on cross-entity DB
        other_conn = get_connection(other_key)
        try:
            other_accounts = _get_accounts(other_conn)
        finally:
            other_conn.close()
        if other_accounts or True:  # Always show section (even empty)
            cross_sections.append({
                "entity_key": other_key,
                "entity_display": _ENTITY_DISPLAY.get(other_key, other_key),
                "accounts": other_accounts,
            })

    return render_template(
        "cashflow.html",
        primary_accounts=primary_accounts,
        cross_sections=cross_sections,
        today=datetime.date.today(),
    )


# ── Account CRUD ─────────────────────────────────────────────────────────────

@bp.route("/accounts/create", methods=["POST"])
def create_account():
    entity_key = request.form.get("entity_key", g.entity_key)
    name = (request.form.get("name") or "").strip()
    balance_str = request.form.get("balance", "0")
    threshold_str = request.form.get("threshold", "500")

    if not name:
        return redirect(url_for("cashflow.index"))

    balance_cents = _parse_dollar_to_cents(balance_str)
    threshold_cents = _parse_dollar_to_cents(threshold_str)

    conn = get_connection(entity_key)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO account_balances "
            "(account_name, balance_cents, low_threshold_cents) VALUES (?, ?, ?)",
            (name, balance_cents, threshold_cents),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))


@bp.route("/accounts/update/<int:acct_id>", methods=["POST"])
def update_account(acct_id):
    entity_key = request.form.get("entity_key", g.entity_key)
    balance_str = request.form.get("balance", "0")
    balance_cents = _parse_dollar_to_cents(balance_str)
    now = datetime.datetime.now().isoformat()

    conn = get_connection(entity_key)
    try:
        conn.execute(
            "UPDATE account_balances SET balance_cents=?, updated_at=?, "
            "balance_source='manual' WHERE id=?",
            (balance_cents, now, acct_id),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))


@bp.route("/accounts/delete/<int:acct_id>", methods=["POST"])
def delete_account(acct_id):
    entity_key = request.form.get("entity_key", g.entity_key)

    conn = get_connection(entity_key)
    try:
        conn.execute("DELETE FROM account_balances WHERE id=?", (acct_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))

"""Cash Flow page — account balances, upcoming bills, projections."""

import datetime
import statistics
from datetime import timedelta

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

# ── Hardcoded account definitions per entity ─────────────────────────────────

_ACCOUNT_DEFS = {
    "personal": {
        "banks": [
            {"name": "BOA Primary", "txn_accounts": ["BofA Personal Checking"]},
            {"name": "BOA Secondary", "txn_accounts": ["BofA Second Acct"]},
            {"name": "BOA Emergency", "txn_accounts": ["BofA Emergency Acct"]},
            {"name": "First Horizon Mortgage"},
        ],
        "cards": [
            {"name": "Apple (K)"},
            {"name": "Apple (R)"},
            {"name": "Barclay", "txn_accounts": ["Barclay CC"]},
            {"name": "BOA Rewards", "txn_accounts": ["BofA Personal CC"]},
            {"name": "Capital One", "txn_accounts": ["Capital One Personal CC"]},
            {"name": "Chase Amazon", "txn_accounts": ["Chase Amazon Visa"]},
            {"name": "Citi", "txn_accounts": ["Citi Personal CC"]},
        ],
    },
    "company": {
        "banks": [
            {"name": "Prosperity Business", "txn_accounts": ["Prosperity Business Checking"]},
        ],
        "cards": [
            {"name": "Amex", "txn_accounts": ["Amex Business Card"]},
            {"name": "Capital One BFM", "txn_accounts": ["Capital One Business CC"]},
        ],
    },
    "luxelegacy": {
        "banks": [
            {"name": "BOA LL Business", "txn_accounts": ["BofA Business Checking (LL)"]},
        ],
        "cards": [],
    },
}


def _parse_dollar_to_cents(dollar_str: str) -> int:
    """Parse '$1,234.56' or '1234.56' into cents (123456)."""
    try:
        cleaned = dollar_str.replace(",", "").replace("$", "").strip()
        return int(round(float(cleaned) * 100))
    except (ValueError, TypeError):
        return 0


def _ensure_accounts(conn, entity_key: str):
    """Sync DB accounts to match hardcoded definitions (add missing, remove stale)."""
    defs = _ACCOUNT_DEFS.get(entity_key, {"banks": [], "cards": []})
    expected_names = set()
    for i, bank in enumerate(defs["banks"]):
        expected_names.add(bank["name"])
        conn.execute(
            "INSERT OR IGNORE INTO account_balances "
            "(account_name, account_type, sort_order) VALUES (?, 'bank', ?)",
            (bank["name"], i),
        )
    for i, card in enumerate(defs["cards"]):
        expected_names.add(card["name"])
        conn.execute(
            "INSERT OR IGNORE INTO account_balances "
            "(account_name, account_type, sort_order) VALUES (?, 'credit_card', ?)",
            (card["name"], 100 + i),
        )
    # Remove accounts no longer in the hardcoded list
    if expected_names:
        placeholders = ",".join("?" for _ in expected_names)
        conn.execute(
            f"DELETE FROM account_balances WHERE account_name NOT IN ({placeholders})",
            list(expected_names),
        )
    conn.commit()


def _get_accounts_by_type(conn, entity_key: str) -> dict:
    """Fetch accounts split into banks and cards, ordered by definition order."""
    _ensure_accounts(conn, entity_key)
    rows = conn.execute(
        "SELECT * FROM account_balances ORDER BY sort_order, account_name"
    ).fetchall()
    banks = []
    cards = []
    for r in rows:
        d = dict(r)
        if d["account_type"] == "credit_card":
            cards.append(d)
        else:
            banks.append(d)
    return {"banks": banks, "cards": cards}


# ── Recurring detection (adapted from dashboard) ─────────────────────────────

_CADENCES = {
    "Weekly": (5, 9),
    "Biweekly": (12, 18),
    "Monthly": (25, 35),
    "Quarterly": (80, 100),
    "Annual": (340, 390),
}


def _classify_cadence(median_interval_days):
    for name, (lo, hi) in _CADENCES.items():
        if lo <= median_interval_days <= hi:
            return name
    return None


def _amount_is_regular(amounts):
    """Check if amounts are regular enough to be recurring."""
    if len(amounts) < 2:
        return False
    abs_amounts = [abs(a) for a in amounts]
    median = statistics.median(abs_amounts)
    threshold = max(300, int(median * 0.05))  # $3 or 5%
    recent = abs_amounts[-3:] if len(abs_amounts) >= 3 else abs_amounts
    within = sum(1 for a in recent if abs(a - median) <= threshold)
    return within >= 2


def _detect_upcoming_for_account(conn, account_names: list, horizon_days: int = 30) -> list:
    """Detect recurring charges for a specific account, return upcoming items."""
    cutoff = (datetime.datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today = datetime.datetime.now().date()
    horizon_end = today + timedelta(days=horizon_days)

    placeholders = ",".join("?" for _ in account_names)
    rows = conn.execute(
        "SELECT merchant_canonical, date, amount_cents "
        "FROM transactions "
        "WHERE merchant_canonical IS NOT NULL AND merchant_canonical != '' "
        "  AND amount_cents < 0 "
        "  AND date >= ? AND date <= ? "
        f"  AND account IN ({placeholders}) "
        "ORDER BY merchant_canonical, date",
        [cutoff, today_str] + account_names,
    ).fetchall()

    # Group by merchant
    groups = {}
    for r in rows:
        merchant = r["merchant_canonical"]
        if merchant not in groups:
            groups[merchant] = []
        groups[merchant].append({"date": r["date"], "amount_cents": r["amount_cents"]})

    upcoming = []
    for merchant, txns in groups.items():
        if len(txns) < 2:
            continue
        dates, amounts = [], []
        for t in txns:
            try:
                dates.append(datetime.datetime.strptime(t["date"], "%Y-%m-%d").date())
            except (ValueError, TypeError):
                continue
            amounts.append(t["amount_cents"])
        if len(dates) < 2:
            continue
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        intervals = [iv for iv in intervals if iv > 0]
        if not intervals:
            continue
        median_interval = statistics.median(intervals)
        cadence = _classify_cadence(median_interval)
        if cadence is None:
            continue
        if not _amount_is_regular(amounts):
            continue
        last_date = dates[-1]
        if (today - last_date).days > 2 * median_interval:
            continue
        next_date = last_date + timedelta(days=int(median_interval))
        if next_date < today or next_date > horizon_end:
            continue
        median_amount = int(statistics.median([abs(a) for a in amounts]))
        upcoming.append({
            "merchant": merchant,
            "cadence": cadence,
            "amount_cents": median_amount,
            "expected_date": next_date.isoformat(),
            "display_date": next_date.strftime("%b %-d"),
        })

    upcoming.sort(key=lambda x: x["expected_date"])
    return upcoming


def _load_entity_section(entity_key: str) -> dict:
    """Load full account data for an entity (banks, cards, upcoming charges)."""
    init_db(entity_key)
    conn = get_connection(entity_key)
    try:
        accts = _get_accounts_by_type(conn, entity_key)
        # Build lookup of txn_accounts from defs
        defs = _ACCOUNT_DEFS.get(entity_key, {"banks": [], "cards": []})
        txn_map = {}
        for d in defs["banks"] + defs["cards"]:
            txn_map[d["name"]] = d.get("txn_accounts", [d["name"]])
        # Attach upcoming charges per account
        for acct in accts["banks"] + accts["cards"]:
            match_names = txn_map.get(acct["account_name"], [acct["account_name"]])
            acct["upcoming"] = _detect_upcoming_for_account(
                conn, match_names
            )
        return accts
    finally:
        conn.close()


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    # Primary entity
    primary = _load_entity_section(g.entity_key)

    # Cross-entity sections
    cross_sections = []
    for other_key in _CROSS_ENTITY.get(g.entity_key, []):
        other = _load_entity_section(other_key)
        cross_sections.append({
            "entity_key": other_key,
            "entity_display": _ENTITY_DISPLAY.get(other_key, other_key),
            "banks": other["banks"],
            "cards": other["cards"],
        })

    return render_template(
        "cashflow.html",
        primary_banks=primary["banks"],
        primary_cards=primary["cards"],
        cross_sections=cross_sections,
        today=datetime.date.today(),
    )


# ── Account CRUD ─────────────────────────────────────────────────────────────

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


@bp.route("/accounts/update-card/<int:acct_id>", methods=["POST"])
def update_card(acct_id):
    """Update credit card balance + credit-card-specific fields."""
    entity_key = request.form.get("entity_key", g.entity_key)
    balance_cents = _parse_dollar_to_cents(request.form.get("balance", "0"))
    limit_cents = _parse_dollar_to_cents(request.form.get("credit_limit", "0"))
    due_day = request.form.get("payment_due_day", "").strip()
    payment_cents = _parse_dollar_to_cents(request.form.get("payment_amount", "0"))
    now = datetime.datetime.now().isoformat()
    import sys
    print(f"[CF DEBUG] acct={acct_id} form={dict(request.form)} due_day={due_day!r}", file=sys.stderr, flush=True)

    due_day_int = None
    if due_day:
        try:
            due_day_int = max(1, min(31, int(due_day)))
        except ValueError:
            pass

    conn = get_connection(entity_key)
    try:
        conn.execute(
            "UPDATE account_balances SET balance_cents=?, credit_limit_cents=?, "
            "payment_due_day=?, payment_amount_cents=?, updated_at=?, "
            "balance_source='manual' WHERE id=?",
            (balance_cents, limit_cents, due_day_int, payment_cents, now, acct_id),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))

"""Kristine's Dashboard — public, mobile-first page.

Shows Personal Focus budget status + LL (Luxe Legacy) transactions/spending.
No authentication required (bypassed in __init__.py).
"""
from __future__ import annotations

import logging
import os
import threading
from datetime import date, datetime, timezone

from flask import Blueprint, render_template, request

from core.db import get_connection, init_db

log = logging.getLogger(__name__)

# ── Background Plaid sync ────────────────────────────────────────────────────

_sync_lock = threading.Lock()


def _background_sync():
    """Sync Plaid transactions for personal + LL in a background thread."""
    if not os.environ.get("PLAID_CLIENT_ID") or not os.environ.get("PLAID_SECRET"):
        return

    if not _sync_lock.acquire(blocking=False):
        log.info("Kristine sync: skipped (already running)")
        return

    try:
        from core.plaid_client import get_transactions as plaid_get_transactions
        from web.routes.plaid import _upsert_plaid_transaction

        for entity_key in ("personal", "luxelegacy"):
            init_db(entity_key)
            conn = get_connection(entity_key)
            try:
                items = [dict(r) for r in conn.execute("SELECT * FROM plaid_items").fetchall()]
            finally:
                conn.close()

            if not items:
                continue

            for item in items:
                try:
                    conn = get_connection(entity_key)
                    try:
                        acct_rows = conn.execute(
                            "SELECT account_id FROM plaid_accounts WHERE item_id=? AND enabled=1",
                            (item["item_id"],),
                        ).fetchall()
                        enabled = {r["account_id"] for r in acct_rows}
                    finally:
                        conn.close()

                    result = plaid_get_transactions(item["access_token"], cursor=item.get("cursor"))

                    conn = get_connection(entity_key)
                    try:
                        for t in result["added"]:
                            if t["account_id"] not in enabled:
                                continue
                            _upsert_plaid_transaction(conn, entity_key, item["item_id"], t)

                        for t in result["modified"]:
                            if t["account_id"] not in enabled:
                                continue
                            description = t.get("merchant_name") or t.get("name") or ""
                            amount = -t["amount"]
                            conn.execute(
                                "UPDATE transactions SET description_raw=?, merchant_raw=?, "
                                "amount=?, amount_cents=? WHERE plaid_transaction_id=?",
                                (description, description, amount, round(amount * 100),
                                 t["plaid_transaction_id"]),
                            )

                        now = datetime.now(timezone.utc).isoformat()
                        conn.execute(
                            "UPDATE plaid_items SET cursor=?, last_synced=? WHERE item_id=?",
                            (result["next_cursor"], now, item["item_id"]),
                        )
                        conn.commit()
                    finally:
                        conn.close()

                except Exception as exc:
                    log.warning("Kristine sync error (%s/%s): %s",
                                entity_key, item.get("institution_name"), exc)

        log.info("Kristine background sync complete")
    except Exception as exc:
        log.warning("Kristine background sync failed: %s", exc)
    finally:
        _sync_lock.release()

bp = Blueprint("kristine", __name__, url_prefix="/k")

# Transfer/income categories excluded from budget actuals
_EXCLUDE_CATS = (
    "Internal Transfer", "Credit Card Payment", "Income",
    "Owner Contribution", "Partner Buyout",
)


# ── Personal Focus budget ────────────────────────────────────────────────────


def _get_focus_budget(conn, month: str) -> list[dict]:
    """Compute budget vs actuals for Focus-section categories."""
    rows = conn.execute(
        "SELECT * FROM budget_items WHERE budget_section = 'focus' ORDER BY category"
    ).fetchall()
    budget_items = [dict(r) for r in rows]
    if not budget_items:
        return []

    # Actual spending for the month (category level)
    exclude_clause = ",".join("?" for _ in _EXCLUDE_CATS)
    spent_rows = conn.execute(
        "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
        "ABS(SUM(amount)) as total "
        "FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? "
        "AND amount < 0 "
        "AND COALESCE(category,'') NOT IN (%s) "
        "GROUP BY cat" % exclude_clause,
        (month, *_EXCLUDE_CATS),
    ).fetchall()
    actuals = {r["cat"]: int(round(r["total"] * 100)) for r in spent_rows}

    # Subcategory spending for the month
    sub_rows = conn.execute(
        "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
        "COALESCE(NULLIF(subcategory,''),'General') as subcat, "
        "ABS(SUM(amount)) as total "
        "FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? "
        "AND amount < 0 "
        "AND COALESCE(category,'') NOT IN (%s) "
        "GROUP BY cat, subcat ORDER BY total DESC" % exclude_clause,
        (month, *_EXCLUDE_CATS),
    ).fetchall()
    # Build dict: category -> list of {subcategory, spent_cents}
    sub_actuals: dict[str, list[dict]] = {}
    for r in sub_rows:
        cat = r["cat"]
        if cat not in sub_actuals:
            sub_actuals[cat] = []
        sub_actuals[cat].append({
            "subcategory": r["subcat"],
            "spent_cents": int(round(r["total"] * 100)),
        })

    # Per-category transactions for drill-down
    focus_cats = [bi["category"] for bi in budget_items]
    cat_placeholders = ",".join("?" for _ in focus_cats)
    txn_rows = conn.execute(
        "SELECT date, merchant_canonical, description_raw, "
        "ABS(amount) as amt, category, subcategory "
        "FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? "
        "AND amount < 0 "
        "AND category IN (%s) "
        "ORDER BY date DESC, rowid DESC" % cat_placeholders,
        (month, *focus_cats),
    ).fetchall()
    cat_txns: dict[str, list[dict]] = {}
    for r in txn_rows:
        cat = r["category"]
        if cat not in cat_txns:
            cat_txns[cat] = []
        name = r["merchant_canonical"] or r["description_raw"] or ""
        if len(name) > 28:
            name = name[:26] + "\u2026"
        cat_txns[cat].append({
            "date": r["date"],
            "name": name,
            "amount_cents": int(round(r["amt"] * 100)),
            "subcategory": r["subcategory"] or "",
        })

    result = []
    for bi in budget_items:
        spent = actuals.get(bi["category"], 0)
        budget = bi["monthly_budget_cents"]
        remaining = budget - spent
        pct = int(round(spent / budget * 100)) if budget > 0 else 0
        # Only include subcategories if there are more than 1 (skip if just "General")
        subs = sub_actuals.get(bi["category"], [])
        if len(subs) <= 1:
            subs = []
        result.append({
            "category": bi["category"],
            "budget_cents": budget,
            "spent_cents": spent,
            "remaining_cents": remaining,
            "pct": min(pct, 999),
            "subcategories": subs,
            "transactions": cat_txns.get(bi["category"], []),
        })

    # Sort by spending descending (most spent first)
    result.sort(key=lambda x: x["spent_cents"], reverse=True)
    return result


# ── LL helpers ───────────────────────────────────────────────────────────────


def _get_ll_summary(conn, month: str) -> dict:
    """Get LL spending/income summary for a month."""
    # Income (positive amounts)
    income_row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? AND amount > 0 "
        "AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment')",
        (month,),
    ).fetchone()
    income_cents = int(round((income_row["total"] or 0) * 100))

    # Expenses (negative amounts)
    expense_row = conn.execute(
        "SELECT COALESCE(SUM(ABS(amount)), 0) as total FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? AND amount < 0 "
        "AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment')",
        (month,),
    ).fetchone()
    expense_cents = int(round((expense_row["total"] or 0) * 100))

    # Category breakdown (expenses)
    cat_rows = conn.execute(
        "SELECT COALESCE(NULLIF(category,''),'Uncategorized') as cat, "
        "ABS(SUM(amount)) as total, COUNT(*) as cnt "
        "FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? AND amount < 0 "
        "AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment') "
        "GROUP BY cat ORDER BY total DESC",
        (month,),
    ).fetchall()
    categories = [
        {"category": r["cat"], "spent_cents": int(round(r["total"] * 100)), "count": r["cnt"]}
        for r in cat_rows
    ]

    # Recent transactions (last 15)
    txn_rows = conn.execute(
        "SELECT date, description_raw, merchant_canonical, "
        "amount, category, subcategory "
        "FROM transactions "
        "WHERE strftime('%%Y-%%m', date) = ? "
        "AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment') "
        "ORDER BY date DESC, rowid DESC LIMIT 15",
        (month,),
    ).fetchall()
    transactions = []
    for r in txn_rows:
        name = r["merchant_canonical"] or r["description_raw"] or ""
        if len(name) > 30:
            name = name[:28] + "\u2026"
        transactions.append({
            "date": r["date"],
            "name": name,
            "amount_cents": int(round(r["amount"] * 100)),
            "category": r["category"] or "",
            "is_income": r["amount"] > 0,
        })

    return {
        "income_cents": income_cents,
        "expense_cents": expense_cents,
        "profit_cents": income_cents - expense_cents,
        "categories": categories,
        "transactions": transactions,
        "has_data": income_cents > 0 or expense_cents > 0 or len(transactions) > 0,
    }


# ── Formatting helpers ───────────────────────────────────────────────────────


def _fmt_dollars(cents):
    """Format integer cents as whole-dollar string."""
    if cents is None:
        return "$0"
    cents = int(cents)
    rounded = round(cents / 100)
    sign = "\u2212" if rounded < 0 else ""
    return f"{sign}${abs(rounded):,.0f}"


def _fmt_month(month_str: str) -> str:
    """Format YYYY-MM as 'March 2026'."""
    try:
        d = datetime.strptime(month_str, "%Y-%m")
        return d.strftime("%B %Y")
    except (ValueError, TypeError):
        return month_str


def _fmt_date_short(date_str: str) -> str:
    """Format YYYY-MM-DD as 'Mar 8'."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%b %-d")
    except (ValueError, TypeError):
        return date_str or ""


# ── Route ────────────────────────────────────────────────────────────────────


def _compute_praise(focus_items: list[dict], focus_pct: int,
                     focus_remaining: int, prev_focus_spent: int | None,
                     focus_spent: int) -> dict:
    """Generate praise messages based on budget performance."""
    headline = ""
    wins: list[str] = []

    # --- Headline: pick the single most impressive thing ---

    # Categories under 30% are really impressive
    star_cats = [i for i in focus_items if 0 < i["pct"] <= 30 and i["spent_cents"] > 0]
    # Categories at exactly $0
    zero_cats = [i for i in focus_items if i["spent_cents"] == 0 and i["budget_cents"] > 0]
    # Categories over budget
    over_cats = [i for i in focus_items if i["pct"] > 100]
    # Biggest saver (most remaining dollars)
    best_saver = max(focus_items, key=lambda x: x["remaining_cents"]) if focus_items else None

    # Month-over-month improvement
    mom_improved = False
    mom_pct = 0
    if prev_focus_spent is not None and prev_focus_spent > 0 and focus_spent < prev_focus_spent:
        mom_improved = True
        mom_pct = int(round((1 - focus_spent / prev_focus_spent) * 100))

    # Pick headline
    if focus_pct == 0:
        headline = "Fresh month, clean slate — you've got this!"
    elif mom_improved and mom_pct >= 15:
        headline = (f"Wow — you're spending {mom_pct}% less than last month! "
                    "That's seriously impressive.")
    elif focus_pct <= 25:
        headline = (f"Only {focus_pct}% of your budget used — "
                    "you are absolutely crushing it this month!")
    elif focus_pct <= 50:
        headline = (f"Halfway through the budget at just {focus_pct}% — "
                    "that's incredible control!")
    elif focus_pct <= 70:
        remaining_dollars = _fmt_dollars(focus_remaining)
        headline = (f"You still have {remaining_dollars} left to work with. "
                    "Really impressive pacing!")
    elif focus_pct <= 85:
        headline = "Great awareness checking in — you're on track!"
    elif len(over_cats) == 0:
        headline = "Every single category is under budget. That takes real discipline!"
    else:
        # Even when things are tight, find something positive
        if best_saver and best_saver["remaining_cents"] > 0:
            headline = (f"Love that you're keeping {best_saver['category']} "
                        f"in check — {_fmt_dollars(best_saver['remaining_cents'])} still left there!")
        else:
            headline = "You're staying on top of things just by checking in. That matters!"

    # --- Smaller wins ---

    if zero_cats:
        names = " and ".join(c["category"] for c in zero_cats[:2])
        if len(zero_cats) > 2:
            names = ", ".join(c["category"] for c in zero_cats[:2]) + f" and {len(zero_cats) - 2} more"
        wins.append(f"$0 spent on {names} — amazing restraint!")

    if star_cats:
        best = min(star_cats, key=lambda x: x["pct"])
        wins.append(
            f"{best['category']} at only {best['pct']}% of budget — so disciplined!"
        )

    if mom_improved and mom_pct >= 5:
        wins.append(f"Down {mom_pct}% from last month overall!")

    # Category-specific wins (big remaining dollars)
    for item in sorted(focus_items, key=lambda x: x["remaining_cents"], reverse=True):
        if item["remaining_cents"] > 5000 and item["pct"] <= 60 and len(wins) < 4:
            wins.append(
                f"{_fmt_dollars(item['remaining_cents'])} still available in "
                f"{item['category']}"
            )

    # Cap at 3 wins
    wins = wins[:3]

    return {"headline": headline, "wins": wins}


def _month_offset(month_str: str, delta: int) -> str:
    """Shift a YYYY-MM string by +/- delta months."""
    d = datetime.strptime(month_str, "%Y-%m")
    # Add delta months
    m = d.month + delta
    y = d.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


@bp.route("/")
def index():
    current_month = date.today().strftime("%Y-%m")
    month = request.args.get("m", current_month)

    # Validate month format
    try:
        datetime.strptime(month, "%Y-%m")
    except (ValueError, TypeError):
        month = current_month

    prev_month = _month_offset(month, -1)
    next_month = _month_offset(month, 1)
    is_current = month == current_month

    # Ensure DBs are initialized
    init_db("personal")
    init_db("luxelegacy")

    # Kick off background Plaid sync (non-blocking)
    threading.Thread(target=_background_sync, daemon=True).start()

    # Personal Focus budget + account balances
    personal_conn = get_connection("personal")
    try:
        focus_items = _get_focus_budget(personal_conn, month)
        focus_budgeted = sum(i["budget_cents"] for i in focus_items)
        focus_spent = sum(i["spent_cents"] for i in focus_items)
        focus_remaining = focus_budgeted - focus_spent
        focus_pct = int(round(focus_spent / focus_budgeted * 100)) if focus_budgeted > 0 else 0

        # Previous month spending for comparison
        prev_focus_spent = None
        try:
            prev_items = _get_focus_budget(personal_conn, prev_month)
            if prev_items:
                prev_focus_spent = sum(i["spent_cents"] for i in prev_items)
        except Exception:
            pass

        # Praise engine
        praise = _compute_praise(
            focus_items, focus_pct, focus_remaining,
            prev_focus_spent, focus_spent,
        )

        # Account balances Kristine cares about
        accounts = []
        _KRISTINE_ACCOUNTS = [
            ("BOA Primary", "personal"),
            ("Kristine Apple Card", "personal"),
        ]
        for acct_name, _entity in _KRISTINE_ACCOUNTS:
            row = personal_conn.execute(
                "SELECT account_name, balance_cents, account_type, "
                "credit_limit_cents FROM account_balances WHERE account_name = ?",
                (acct_name,),
            ).fetchone()
            if row:
                acct = dict(row)
                if acct_name == "Kristine Apple Card":
                    acct["account_name"] = "Apple Card"
                accounts.append(acct)
    finally:
        personal_conn.close()

    # LL summary + LL account balance
    ll_conn = get_connection("luxelegacy")
    try:
        ll = _get_ll_summary(ll_conn, month)

        # LL business checking
        ll_acct = ll_conn.execute(
            "SELECT account_name, balance_cents, account_type, "
            "credit_limit_cents FROM account_balances "
            "WHERE account_type = 'bank' LIMIT 1",
        ).fetchone()
        if ll_acct:
            acct = dict(ll_acct)
            acct["account_name"] = "Luxe Legacy"
            accounts.insert(1, acct)  # Between BOA Primary and Apple Card
    finally:
        ll_conn.close()

    now = datetime.now().strftime("%b %-d, %-I:%M %p")

    return render_template(
        "kristine.html",
        month=month,
        month_display=_fmt_month(month),
        prev_month=prev_month,
        next_month=next_month,
        is_current=is_current,
        praise=praise,
        focus_items=focus_items,
        focus_budgeted=focus_budgeted,
        focus_spent=focus_spent,
        focus_remaining=focus_remaining,
        focus_pct=focus_pct,
        ll=ll,
        accounts=accounts,
        fmt_dollars=_fmt_dollars,
        fmt_date=_fmt_date_short,
        now=now,
        cache_bust=int(datetime.now().timestamp()),
    )

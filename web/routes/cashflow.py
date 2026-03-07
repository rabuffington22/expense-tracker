"""Cash Flow page — account balances, upcoming bills, projections."""

import datetime
import logging
import statistics
from datetime import timedelta

from flask import Blueprint, render_template, request, g, redirect, url_for

from core.db import get_connection, init_db

log = logging.getLogger(__name__)

bp = Blueprint("cashflow", __name__, url_prefix="/cashflow")

# Cross-entity visibility: Personal ↔ BFM share view, LL is isolated.
_CROSS_ENTITY = {
    "personal": ["company"],
    "company": ["personal"],
    "luxelegacy": [],
}

# Build display names from the active entity map (respects ENTITIES env var)
def _build_entity_display():
    from web import _ENTITY_MAP
    return {v: k for k, v in _ENTITY_MAP.items()}

_ENTITY_DISPLAY = None  # lazy-init

# ── Plaid account sync ────────────────────────────────────────────────────────

_BALANCE_CACHE_SECONDS = 3600  # Re-fetch Plaid balances every hour


def _parse_dollar_to_cents(dollar_str: str) -> int:
    """Parse '$1,234.56' or '1234.56' into cents (123456)."""
    try:
        cleaned = dollar_str.replace(",", "").replace("$", "").strip()
        return int(round(float(cleaned) * 100))
    except (ValueError, TypeError):
        return 0


def _sync_plaid_accounts(conn, entity_key: str):
    """Sync Plaid accounts to account_balances table with current balances.

    Creates/updates account_balances rows from connected Plaid accounts.
    Skips API call if balances were refreshed within _BALANCE_CACHE_SECONDS.
    Preserves manually-created accounts (plaid_account_id IS NULL).
    """
    import os
    if not os.environ.get("PLAID_CLIENT_ID") or not os.environ.get("PLAID_SECRET"):
        return

    # Check staleness — skip if recently refreshed
    latest = conn.execute(
        "SELECT MAX(updated_at) FROM account_balances WHERE balance_source='plaid'"
    ).fetchone()[0]
    if latest:
        try:
            last = datetime.datetime.fromisoformat(latest)
            if (datetime.datetime.now() - last).total_seconds() < _BALANCE_CACHE_SECONDS:
                return
        except (ValueError, TypeError):
            pass

    items = conn.execute(
        "SELECT item_id, access_token, institution_name FROM plaid_items"
    ).fetchall()
    if not items:
        return

    try:
        from core.plaid_client import get_accounts
    except (ImportError, RuntimeError):
        return

    bank_sort = 0
    card_sort = 100
    synced_plaid_ids = set()  # Track which accounts we actually want on Cash Flow

    for item in items:
        try:
            accounts = get_accounts(item["access_token"])
        except Exception as e:
            log.warning("Failed to fetch accounts for %s: %s", item["institution_name"], e)
            continue

        for acct in accounts:
            # Skip investment/retirement accounts (IRA, 529, etc.) — those go to Planning
            if acct["type"] == "investment":
                continue

            # Skip accounts not in plaid_accounts or disabled — if the row was
            # deleted (e.g. Quicksilver removed from BFM), treat it as disabled
            # so it doesn't get re-created on every sync.
            pa_row = conn.execute(
                "SELECT enabled, display_name FROM plaid_accounts WHERE account_id=?",
                (acct["account_id"],),
            ).fetchone()
            if not pa_row or not pa_row["enabled"]:
                continue

            synced_plaid_ids.add(acct["account_id"])

            acct_type = "credit_card" if acct["type"] == "credit" else "bank"
            if acct_type == "bank":
                sort = bank_sort
                bank_sort += 1
            else:
                sort = card_sort
                card_sort += 1

            # Display name: user alias > Plaid name
            display_name = (pa_row["display_name"] if pa_row and pa_row["display_name"]
                            else acct["name"])

            balance_cents = int(round(acct["balance_current"] * 100)) if acct["balance_current"] is not None else 0
            limit_cents = int(round(acct["balance_limit"] * 100)) if acct["balance_limit"] is not None else 0
            now = datetime.datetime.now().isoformat()

            # UPSERT by plaid_account_id
            existing = conn.execute(
                "SELECT id FROM account_balances WHERE plaid_account_id=?",
                (acct["account_id"],),
            ).fetchone()

            if existing:
                # Preserve manually-set credit limit when Plaid doesn't provide one
                if limit_cents == 0:
                    conn.execute(
                        "UPDATE account_balances SET account_name=?, balance_cents=?, "
                        "balance_source='plaid', account_type=?, "
                        "sort_order=?, updated_at=? WHERE id=?",
                        (display_name, balance_cents, acct_type, sort,
                         now, existing["id"]),
                    )
                else:
                    conn.execute(
                        "UPDATE account_balances SET account_name=?, balance_cents=?, "
                        "credit_limit_cents=?, balance_source='plaid', account_type=?, "
                        "sort_order=?, updated_at=? WHERE id=?",
                        (display_name, balance_cents, limit_cents, acct_type, sort,
                         now, existing["id"]),
                    )
            else:
                # Disambiguate if another account already has this name
                name_conflict = conn.execute(
                    "SELECT id FROM account_balances WHERE account_name=?",
                    (display_name,),
                ).fetchone()
                if name_conflict:
                    mask = acct.get("mask") or ""
                    inst = item["institution_name"] or ""
                    suffix = f" ({inst} ••{mask})" if mask else f" ({inst})"
                    display_name = f"{display_name}{suffix}"

                conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, plaid_account_id, "
                    "account_type, credit_limit_cents, sort_order, updated_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (display_name, balance_cents, "plaid", acct["account_id"],
                     acct_type, limit_cents, sort, now),
                )

    # Remove accounts that shouldn't be on Cash Flow:
    # - Old hardcoded accounts (plaid_account_id IS NULL)
    # - Investment/disabled accounts that were synced before filters were added
    if synced_plaid_ids:
        conn.execute(
            "DELETE FROM account_balances WHERE plaid_account_id IS NULL"
        )
        placeholders = ",".join("?" for _ in synced_plaid_ids)
        conn.execute(
            f"DELETE FROM account_balances WHERE plaid_account_id IS NOT NULL "
            f"AND plaid_account_id NOT IN ({placeholders})",
            list(synced_plaid_ids),
        )

    conn.commit()


def _get_account_names_for_plaid_id(conn, plaid_account_id: str) -> list:
    """Get the account name used in transactions for a Plaid account."""
    row = conn.execute(
        "SELECT name FROM plaid_accounts WHERE account_id=?",
        (plaid_account_id,),
    ).fetchone()
    return [row["name"]] if row else []


def _get_accounts_by_type(conn, entity_key: str) -> dict:
    """Fetch accounts split into banks and cards, ordered by sort_order."""
    _sync_plaid_accounts(conn, entity_key)
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


def _get_manual_recurring(conn, account_id: int) -> list:
    """Get manually-added recurring charges for an account, projected to next date."""
    rows = conn.execute(
        "SELECT id, merchant, amount_cents, day_of_month "
        "FROM manual_recurring WHERE account_id=? ORDER BY day_of_month",
        (account_id,),
    ).fetchall()
    today = datetime.date.today()
    items = []
    for r in rows:
        day = r["day_of_month"]
        # Next occurrence: this month if day >= today, else next month
        try:
            next_date = today.replace(day=day)
        except ValueError:
            # Day doesn't exist in this month (e.g. 31 in Feb) — clamp
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            next_date = today.replace(day=min(day, last_day))
        if next_date < today:
            # Move to next month
            if today.month == 12:
                next_date = next_date.replace(year=today.year + 1, month=1)
            else:
                next_date = next_date.replace(month=today.month + 1)
            # Re-clamp for next month
            try:
                next_date = next_date.replace(day=day)
            except ValueError:
                import calendar
                last_day = calendar.monthrange(next_date.year, next_date.month)[1]
                next_date = next_date.replace(day=min(day, last_day))
        items.append({
            "merchant": r["merchant"],
            "amount_cents": r["amount_cents"],
            "expected_date": next_date.isoformat(),
            "display_date": next_date.strftime("%b %-d"),
            "manual": True,
            "manual_id": r["id"],
        })
    return items


def _fetch_plaid_liabilities(conn) -> dict:
    """Fetch Plaid liabilities for all connected credit card accounts.

    Returns dict keyed by plaid_account_id with credit card details.
    Skips API call if liabilities were refreshed within _BALANCE_CACHE_SECONDS.
    Silently returns empty dict if Plaid is not configured or fails.
    """
    import os
    # Skip entirely if Plaid env vars aren't set — avoids hanging on API calls
    if not os.environ.get("PLAID_CLIENT_ID") or not os.environ.get("PLAID_SECRET"):
        return {}

    # Check staleness — skip if recently refreshed (uses same cache window as accounts)
    latest = conn.execute(
        "SELECT MAX(updated_at) FROM account_balances "
        "WHERE balance_source='plaid' AND account_type='credit_card'"
    ).fetchone()[0]
    if latest:
        try:
            last = datetime.datetime.fromisoformat(latest)
            if (datetime.datetime.now() - last).total_seconds() < _BALANCE_CACHE_SECONDS:
                return {}
        except (ValueError, TypeError):
            pass

    try:
        from core.plaid_client import get_liabilities
    except (ImportError, RuntimeError):
        return {}

    # Find all Plaid items with access tokens
    items = conn.execute(
        "SELECT item_id, access_token FROM plaid_items"
    ).fetchall()
    if not items:
        return {}

    all_liabilities = {}
    for item in items:
        try:
            liab = get_liabilities(item["access_token"])
            all_liabilities.update(liab)
        except Exception as e:
            log.warning("Failed to fetch liabilities for item %s: %s", item["item_id"], e)
    return all_liabilities


def _apply_plaid_liabilities(accts: dict, liabilities: dict, conn):
    """Update account data with Plaid liabilities where linked.

    For credit cards with a plaid_account_id that matches a liabilities entry:
    - Updates balance_cents, credit_limit_cents from Plaid
    - Sets payment_due_day and payment_amount_cents from Plaid's next_payment_due_date
      and minimum_payment_amount
    - Sets balance_source to 'plaid'
    """
    if not liabilities:
        return

    for acct in accts["banks"] + accts["cards"]:
        plaid_id = acct.get("plaid_account_id")
        if not plaid_id or plaid_id not in liabilities:
            continue

        liab = liabilities[plaid_id]
        now = datetime.datetime.now().isoformat()

        # Update balance from Plaid (Plaid returns positive for credit cards)
        balance_cents = int(round(liab["balance"] * 100))
        acct["balance_cents"] = balance_cents
        acct["balance_source"] = "plaid"

        # Credit limit
        if liab["credit_limit"]:
            limit_cents = int(round(liab["credit_limit"] * 100))
            acct["credit_limit_cents"] = limit_cents

        # Payment info from Plaid — store full date
        if liab["next_payment_due_date"]:
            acct["payment_due_date"] = liab["next_payment_due_date"]
            try:
                due_date = datetime.datetime.strptime(
                    liab["next_payment_due_date"], "%Y-%m-%d"
                ).date()
                acct["payment_due_day"] = due_date.day
            except (ValueError, TypeError):
                pass

        if liab["minimum_payment_amount"] is not None:
            acct["payment_amount_cents"] = int(round(liab["minimum_payment_amount"] * 100))

        # Persist to DB so values are cached between Plaid refreshes
        conn.execute(
            "UPDATE account_balances SET balance_cents=?, credit_limit_cents=?, "
            "payment_due_day=?, payment_due_date=?, payment_amount_cents=?, "
            "balance_source='plaid', updated_at=? WHERE id=?",
            (
                acct["balance_cents"],
                acct.get("credit_limit_cents", 0),
                acct.get("payment_due_day"),
                acct.get("payment_due_date"),
                acct.get("payment_amount_cents", 0),
                now,
                acct["id"],
            ),
        )
        conn.commit()


def _load_entity_section(entity_key: str) -> dict:
    """Load full account data for an entity (banks, cards, upcoming charges)."""
    init_db(entity_key)
    conn = get_connection(entity_key)
    try:
        accts = _get_accounts_by_type(conn, entity_key)

        # Fetch and apply Plaid liabilities for connected accounts
        liabilities = _fetch_plaid_liabilities(conn)
        _apply_plaid_liabilities(accts, liabilities, conn)

        # Compute payment_due_date from payment_due_day for manual accounts
        import calendar
        today = datetime.date.today()
        for acct in accts["banks"] + accts["cards"]:
            if acct.get("payment_due_day") and not acct.get("payment_due_date"):
                day = acct["payment_due_day"]
                try:
                    next_date = today.replace(day=day)
                except ValueError:
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    next_date = today.replace(day=min(day, last_day))
                if next_date < today:
                    if today.month == 12:
                        next_date = next_date.replace(year=today.year + 1, month=1)
                    else:
                        next_date = next_date.replace(month=today.month + 1)
                    try:
                        next_date = next_date.replace(day=day)
                    except ValueError:
                        last_day = calendar.monthrange(next_date.year, next_date.month)[1]
                        next_date = next_date.replace(day=min(day, last_day))
                acct["payment_due_date"] = next_date.isoformat()

        # Attach upcoming charges per account (auto-detected + manual)
        for acct in accts["banks"] + accts["cards"]:
            plaid_id = acct.get("plaid_account_id")
            if plaid_id:
                match_names = _get_account_names_for_plaid_id(conn, plaid_id)
            else:
                match_names = [acct["account_name"]]
            # Skip recurring detection if no account names to match against
            auto = _detect_upcoming_for_account(conn, match_names) if match_names else []
            # Mark auto items
            for item in auto:
                item["manual"] = False
                item["manual_id"] = None
            manual = _get_manual_recurring(conn, acct["id"])
            combined = auto + manual
            combined.sort(key=lambda x: x["expected_date"])
            acct["upcoming"] = combined[:3]
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
            "entity_display": _build_entity_display().get(other_key, other_key),
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

    due_day_int = None
    if due_day:
        try:
            due_day_int = max(1, min(31, int(due_day)))
        except ValueError:
            pass

    # APR — parse percentage string to basis points
    apr_str = request.form.get("apr", "").strip()
    apr_bps = None
    if apr_str:
        try:
            apr_bps = int(round(float(apr_str.replace(",", "")) * 100))
        except ValueError:
            pass

    conn = get_connection(entity_key)
    try:
        conn.execute(
            "UPDATE account_balances SET balance_cents=?, credit_limit_cents=?, "
            "payment_due_day=?, payment_amount_cents=?, apr_bps=?, updated_at=?, "
            "balance_source='manual' WHERE id=?",
            (balance_cents, limit_cents, due_day_int, payment_cents, apr_bps, now, acct_id),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))


# ── Manual Recurring Charges ────────────────────────────────────────────────

@bp.route("/recurring/add", methods=["POST"])
def add_recurring():
    """Add a manual recurring charge to an account."""
    entity_key = request.form.get("entity_key", g.entity_key)
    account_id = request.form.get("account_id")
    merchant = request.form.get("merchant", "").strip()
    amount_cents = _parse_dollar_to_cents(request.form.get("amount", "0"))
    day_str = request.form.get("day_of_month", "").strip()

    if not merchant or not account_id or not day_str:
        return redirect(url_for("cashflow.index"))

    try:
        day = max(1, min(31, int(day_str)))
    except ValueError:
        return redirect(url_for("cashflow.index"))

    conn = get_connection(entity_key)
    try:
        conn.execute(
            "INSERT INTO manual_recurring (account_id, merchant, amount_cents, day_of_month) "
            "VALUES (?, ?, ?, ?)",
            (int(account_id), merchant, amount_cents, day),
        )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))


@bp.route("/recurring/delete/<int:rec_id>", methods=["POST"])
def delete_recurring(rec_id):
    """Delete a manual recurring charge."""
    entity_key = request.form.get("entity_key", g.entity_key)
    conn = get_connection(entity_key)
    try:
        conn.execute("DELETE FROM manual_recurring WHERE id=?", (rec_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("cashflow.index"))

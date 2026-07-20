"""Plaid integration routes — connect banks, sync transactions."""

import logging
import secrets
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, jsonify

log = logging.getLogger(__name__)

from core.db import get_connection, init_db
from core.imports import compute_external_transaction_id
from core.categorize import _get_active_aliases, _match_alias, _keyword_suggest, _strip_platform_prefix
from core.sync_coordination import try_acquire_sync_lease

bp = Blueprint("plaid", __name__, url_prefix="/plaid")

# ── Helpers ──────────────────────────────────────────────────────────────────

def _plaid_available() -> bool:
    """Check if Plaid env vars are configured."""
    import os
    return bool(os.environ.get("PLAID_CLIENT_ID") and os.environ.get("PLAID_SECRET"))


def _get_items(entity_key: str) -> list[dict]:
    """Load spending Plaid items (not vendor accounts) for the current entity."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT * FROM plaid_items WHERE is_vendor = 0 ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _get_accounts_for_item(entity_key: str, item_id: str) -> list[dict]:
    """Load accounts for a specific Plaid item."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT * FROM plaid_accounts WHERE item_id=? ORDER BY name",
            (item_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _fmt_date(date_str) -> str:
    """Format YYYY-MM-DD as 'Jan 15, 2025'."""
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return d.strftime("%b %-d, %Y")
    except (ValueError, TypeError):
        return date_str


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    """Connected accounts page."""
    items = _get_items(g.entity_key)
    conn = get_connection(g.entity_key)
    try:
        for item in items:
            item["accounts"] = _get_accounts_for_item(g.entity_key, item["item_id"])
            # Date range of synced transactions
            row = conn.execute(
                "SELECT MIN(date) AS earliest, MAX(date) AS latest, COUNT(*) AS txn_count "
                "FROM transactions WHERE plaid_item_id=?",
                (item["item_id"],),
            ).fetchone()
            item["txn_count"] = row["txn_count"]
            # Format dates as "Jan 15, 2025"
            item["earliest_date"] = _fmt_date(row["earliest"])
            item["latest_date"] = _fmt_date(row["latest"])
            # Format last_synced ISO timestamp
            if item.get("last_synced"):
                item["last_synced_display"] = _fmt_date(item["last_synced"][:10])
        # Manual accounts (not yet Plaid-connected) — shown as "not connected" placeholders
        manual_rows = conn.execute(
            "SELECT id, account_name FROM account_balances "
            "WHERE plaid_account_id IS NULL AND balance_source='manual' "
            "AND account_type='credit_card' ORDER BY sort_order"
        ).fetchall()
        manual_accounts = [dict(r) for r in manual_rows]
    finally:
        conn.close()

    return render_template(
        "plaid.html",
        items=items,
        manual_accounts=manual_accounts,
        plaid_available=_plaid_available(),
    )


@bp.route("/link-token", methods=["POST"])
def link_token():
    """Create a Plaid Link token for the frontend."""
    if not _plaid_available():
        return jsonify({"error": "Plaid credentials not configured"}), 500
    try:
        from core.plaid_client import create_link_token
        token = create_link_token(user_id=f"expense-tracker-{g.entity_key}")
        return jsonify({"link_token": token})
    except Exception:
        log.exception("Plaid link_token error")
        return jsonify({"error": "Failed to create link token"}), 500


@bp.route("/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange a public token after Plaid Link success."""
    if not _plaid_available():
        return jsonify({"error": "Plaid credentials not configured"}), 500

    data = request.get_json(silent=True) or {}
    public_token = data.get("public_token", "")
    institution_name = data.get("institution_name", "")
    institution_id = data.get("institution_id", "")

    if not public_token:
        return jsonify({"error": "Missing public_token"}), 400

    try:
        from core.plaid_client import exchange_public_token, get_accounts
        result = exchange_public_token(public_token)
        access_token = result["access_token"]
        item_id = result["item_id"]

        from core.crypto import encrypt_token
        now = datetime.now(timezone.utc).isoformat()
        conn = get_connection(g.entity_key)
        try:
            conn.execute(
                """INSERT OR IGNORE INTO plaid_items
                   (item_id, access_token, institution_name, institution_id, created_at)
                   VALUES (?,?,?,?,?)""",
                (item_id, encrypt_token(access_token), institution_name, institution_id, now),
            )
            # Fetch and store accounts
            accounts = get_accounts(access_token)
            for acc in accounts:
                conn.execute(
                    """INSERT OR IGNORE INTO plaid_accounts
                       (item_id, account_id, name, mask, type, subtype)
                       VALUES (?,?,?,?,?,?)""",
                    (item_id, acc["account_id"], acc["name"], acc["mask"],
                     acc["type"], acc["subtype"]),
                )

            # Manual accounts do not carry stable placeholder identity. Preserve
            # them until an explicit user-confirmed merge contract exists.

            conn.commit()
        finally:
            conn.close()

        return jsonify({"success": True, "item_id": item_id, "accounts": len(accounts)})
    except Exception:
        log.exception("Plaid exchange_token error")
        return jsonify({"error": "Failed to connect account"}), 500


@bp.route("/sync", methods=["POST"])
def sync():
    """Sync transactions for a specific Plaid item or all items."""
    if not _plaid_available():
        flash("Plaid credentials not configured.", "danger")
        return redirect(url_for("plaid.index"))

    lease = try_acquire_sync_lease()
    if lease is None:
        flash("A sync is already in progress. Please wait.", "info")
        return redirect(url_for("plaid.index"))

    with lease:
        return _do_sync()


@bp.route("/sync-all", methods=["POST"])
def sync_all():
    """Sync all entities — called by automated daily cron. Protected by SYNC_SECRET."""
    import os
    expected = os.environ.get("SYNC_SECRET", "")
    if not expected:
        return jsonify({"error": "SYNC_SECRET not configured"}), 500
    supplied = request.headers.get("Authorization", "")
    if not secrets.compare_digest(supplied, f"Bearer {expected}"):
        return jsonify({"error": "Unauthorized"}), 401
    if not _plaid_available():
        return jsonify({"error": "Plaid not configured"}), 500
    lease = try_acquire_sync_lease()
    if lease is None:
        return jsonify({"error": "Sync already in progress"}), 429

    with lease:
        from web import _ENTITY_MAP
        results = {}
        for entity_key in _ENTITY_MAP.values():
            try:
                init_db(entity_key)
                results[entity_key] = _sync_entity(entity_key)
            except Exception:
                log.warning("Scheduled sync failed for entity %s", entity_key)
                results[entity_key] = {
                    "new": 0,
                    "modified": 0,
                    "removed": 0,
                    "backfilled": 0,
                    "errors": ["entity sync failed"],
                }
        failed_entities = [
            entity_key
            for entity_key, result in results.items()
            if result.get("errors")
        ]
        if not failed_entities:
            return jsonify({"ok": True, "status": "success", "results": results})

        status = (
            "failure"
            if len(failed_entities) == len(results)
            else "partial_failure"
        )
        return jsonify({"ok": False, "status": status, "results": results}), 502


def _do_sync():
    """Sync the current entity (g.entity_key), flash result, redirect."""
    result = _sync_entity(g.entity_key, target_item_id=request.form.get("item_id"))

    if result.get("skipped"):
        flash("No connected accounts to sync.", "warning")
        return redirect(url_for("plaid.index"))

    parts = []
    if result["new"]:        parts.append(f"{result['new']} new")
    if result["modified"]:   parts.append(f"{result['modified']} updated")
    if result["removed"]:    parts.append(f"{result['removed']} removed")
    if result["backfilled"]: parts.append(f"{result['backfilled']} backfilled")
    if not parts:
        parts.append("no new transactions")

    msg = f"Sync complete: {', '.join(parts)}."
    if result["errors"]:
        msg += f" Errors: {'; '.join(result['errors'])}"
        flash(msg, "warning")
    else:
        flash(msg, "success")

    return redirect(url_for("plaid.index"))


class PlaidItemAccessError(RuntimeError):
    """Stable caller-facing error for an unusable encrypted item token."""


class PlaidTransactionPersistenceError(RuntimeError):
    """Stable caller-facing error for a rolled-back item transaction."""


def _safe_plaid_item_error(exc: Exception) -> str:
    """Return a stable item error without credential or row-level detail."""
    if isinstance(exc, PlaidItemAccessError):
        return "access token unavailable"
    if isinstance(exc, PlaidTransactionPersistenceError):
        return str(exc)
    return "item sync failed"


def _sync_entity(entity_key: str, target_item_id: str | None = None) -> dict:
    """Core Plaid sync for one entity. Returns result dict (no Flask side-effects)."""
    conn = get_connection(entity_key)
    try:
        if target_item_id:
            rows = conn.execute(
                "SELECT * FROM plaid_items WHERE item_id=? AND is_vendor = 0",
                (target_item_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM plaid_items WHERE is_vendor = 0 "
                "ORDER BY created_at, item_id"
            ).fetchall()
        items = [dict(r) for r in rows]
    finally:
        conn.close()

    if not items:
        return {"new": 0, "modified": 0, "removed": 0, "backfilled": 0, "errors": [], "skipped": True}

    total_new = 0
    total_modified = 0
    total_removed = 0
    errors = []

    from core.plaid_client import get_transactions as plaid_get_transactions
    from core.crypto import decrypt_token

    for item in items:
        try:
            try:
                access_token = decrypt_token(item["access_token"])
            except Exception as exc:
                raise PlaidItemAccessError("access token unavailable") from exc

            conn = get_connection(entity_key)
            try:
                acct_rows = conn.execute(
                    "SELECT account_id FROM plaid_accounts WHERE item_id=? AND enabled=1",
                    (item["item_id"],),
                ).fetchall()
                enabled_accounts = {r["account_id"] for r in acct_rows}
            finally:
                conn.close()

            result = plaid_get_transactions(access_token, cursor=item.get("cursor"))

            conn = get_connection(entity_key)
            try:
                item_counts = _apply_plaid_transaction_updates(
                    conn,
                    entity_key,
                    item["item_id"],
                    enabled_accounts,
                    result,
                )
            finally:
                conn.close()
            total_new += item_counts["new"]
            total_modified += item_counts["modified"]
            total_removed += item_counts["removed"]

        except Exception as exc:
            item_label = item.get("institution_name") or item["item_id"]
            errors.append(f"{item_label}: {_safe_plaid_item_error(exc)}")

    # Backfill account column for single-account Plaid items
    backfilled = 0
    conn = get_connection(entity_key)
    try:
        single_acct_items = conn.execute("""
            SELECT pi.item_id, pa.name
            FROM plaid_items pi
            JOIN plaid_accounts pa ON pa.item_id = pi.item_id AND pa.enabled = 1
            GROUP BY pi.item_id
            HAVING COUNT(*) = 1
        """).fetchall()
        for row in single_acct_items:
            cur = conn.execute(
                "UPDATE transactions SET account=? "
                "WHERE plaid_item_id=? AND (account IS NULL OR account = '')",
                (row["name"], row["item_id"]),
            )
            backfilled += cur.rowcount
        if backfilled:
            conn.commit()
    finally:
        conn.close()

    if entity_key == "luxelegacy":
        try:
            from core.luxury_bridge import push_luxelegacy_to_supabase
            push_luxelegacy_to_supabase()
        except Exception as exc:
            errors.append(f"luxury_bridge: {exc}")

    return {"new": total_new, "modified": total_modified, "removed": total_removed,
            "backfilled": backfilled, "errors": errors}


@bp.route("/toggle-account/<account_id>", methods=["POST"])
def toggle_account(account_id):
    """Toggle an account's enabled status."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT item_id, enabled FROM plaid_accounts WHERE account_id=?",
            (account_id,),
        ).fetchone()
        if row:
            new_val = 0 if row["enabled"] else 1
            conn.execute(
                "UPDATE plaid_accounts SET enabled=? WHERE account_id=?",
                (new_val, account_id),
            )
            conn.execute(
                "UPDATE plaid_items SET accounts_last_synced=NULL, "
                "liabilities_last_synced=NULL WHERE item_id=?",
                (row["item_id"],),
            )
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for("plaid.index"))


@bp.route("/rename-account/<account_id>", methods=["POST"])
def rename_account(account_id):
    """Set a display name (alias) for a Plaid account."""
    display_name = request.form.get("display_name", "").strip() or None
    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "UPDATE plaid_accounts SET display_name=? WHERE account_id=?",
            (display_name, account_id),
        )
        # Also update account_balances so Cash Flow reflects the new name immediately
        if display_name:
            conn.execute(
                "UPDATE account_balances SET account_name=? WHERE plaid_account_id=?",
                (display_name, account_id),
            )
        else:
            # Revert to Plaid name
            row = conn.execute(
                "SELECT name FROM plaid_accounts WHERE account_id=?",
                (account_id,),
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE account_balances SET account_name=? WHERE plaid_account_id=?",
                    (row["name"], account_id),
                )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("plaid.index"))


@bp.route("/disconnect/<item_id>", methods=["POST"])
def disconnect(item_id):
    """Disconnect a Plaid item (remove from Plaid + local DB)."""
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT access_token, institution_name FROM plaid_items WHERE item_id=?",
            (item_id,),
        ).fetchone()
        if not row:
            flash("Institution not found.", "danger")
            return redirect(url_for("plaid.index"))

        # Try to remove from Plaid (best effort)
        try:
            from core.plaid_client import remove_item
            from core.crypto import decrypt_token
            remove_item(decrypt_token(row["access_token"]))
        except Exception:
            pass  # Item may already be removed on Plaid's side

        # Remove Cash Flow account_balances rows linked to this item's accounts
        # (manual_recurring rows cascade-delete via FK on account_id)
        acct_ids = [r["account_id"] for r in conn.execute(
            "SELECT account_id FROM plaid_accounts WHERE item_id=?", (item_id,)
        ).fetchall()]
        for aid in acct_ids:
            conn.execute(
                "DELETE FROM account_balances WHERE plaid_account_id=?", (aid,)
            )

        # Remove locally (cascade deletes plaid_accounts)
        conn.execute("DELETE FROM plaid_accounts WHERE item_id=?", (item_id,))
        conn.execute("DELETE FROM plaid_items WHERE item_id=?", (item_id,))
        # Clear plaid_item_id on transactions (keep the transactions themselves)
        conn.execute(
            "UPDATE transactions SET plaid_item_id=NULL WHERE plaid_item_id=?",
            (item_id,),
        )
        conn.commit()
        flash(f"Disconnected {row['institution_name'] or item_id}.", "success")
    finally:
        conn.close()

    return redirect(url_for("plaid.index"))


# ── Internal helpers ─────────────────────────────────────────────────────────

def _apply_plaid_transaction_updates(
    conn,
    entity_key: str,
    item_id: str,
    enabled_accounts: set[str],
    result: dict,
) -> dict[str, int]:
    """Apply one item's fetched updates and final cursor as one transaction."""
    counts = {"new": 0, "modified": 0, "removed": 0}

    try:
        with conn:
            for txn in result["added"]:
                if txn["account_id"] not in enabled_accounts:
                    continue
                counts["new"] += _upsert_plaid_transaction(
                    conn, entity_key, item_id, txn
                )

            for txn in result["modified"]:
                if txn["account_id"] not in enabled_accounts:
                    continue
                description = txn.get("merchant_name") or txn.get("name") or ""
                amount = -txn["amount"]
                amount_cents = round(amount * 100)
                acct_row = conn.execute(
                    "SELECT name FROM plaid_accounts WHERE account_id=?",
                    (txn["account_id"],),
                ).fetchone()
                account_name = acct_row["name"] if acct_row else None
                modified_update = conn.execute(
                    """UPDATE transactions
                       SET description_raw=?, merchant_raw=?, amount=?,
                           amount_cents=?, account=COALESCE(?, account),
                           plaid_item_id=COALESCE(plaid_item_id, ?)
                       WHERE plaid_transaction_id=?""",
                    (
                        description,
                        description,
                        amount,
                        amount_cents,
                        account_name,
                        item_id,
                        txn["plaid_transaction_id"],
                    ),
                )
                if modified_update.rowcount != 1:
                    raise RuntimeError(
                        "modified Plaid transaction target is missing or ambiguous"
                    )
                counts["modified"] += modified_update.rowcount

            for plaid_txn_id in result["removed"]:
                conn.execute(
                    "DELETE FROM transaction_splits"
                    " WHERE transaction_id IN ("
                    "   SELECT transaction_id FROM transactions"
                    "   WHERE plaid_transaction_id=?)",
                    (plaid_txn_id,),
                )
                removed_delete = conn.execute(
                    "DELETE FROM transactions WHERE plaid_transaction_id=?",
                    (plaid_txn_id,),
                )
                counts["removed"] += removed_delete.rowcount

            now = datetime.now(timezone.utc).isoformat()
            cursor_update = conn.execute(
                "UPDATE plaid_items SET cursor=?, last_synced=? WHERE item_id=?",
                (result["next_cursor"], now, item_id),
            )
            if cursor_update.rowcount != 1:
                raise RuntimeError("Plaid item disappeared before cursor commit")
    except Exception as exc:
        raise PlaidTransactionPersistenceError(
            "transaction persistence failed; cursor unchanged"
        ) from exc

    return counts


def _upsert_plaid_transaction(conn, entity_key: str, item_id: str, txn: dict) -> int:
    """
    Insert a Plaid transaction into the transactions table.

    Plaid: positive amount = debit (money spent).
    Our schema: negative amount = debit.
    So we negate the Plaid amount.

    Returns 1 if inserted, 0 if already existed.
    """
    description = txn.get("merchant_name") or txn.get("name") or ""
    date = txn["date"]
    amount = -txn["amount"]  # Plaid positive=debit -> our negative=debit
    amount_cents = round(amount * 100)

    # Look up Plaid account name for the account column
    acct_row = conn.execute(
        "SELECT name FROM plaid_accounts WHERE account_id=?",
        (txn["account_id"],),
    ).fetchone()
    account_name = acct_row["name"] if acct_row else None

    plaid_transaction_id = txn["plaid_transaction_id"]
    candidate_txn_id = compute_external_transaction_id("plaid", plaid_transaction_id)

    # Preserve an already-issued legacy primary key when this authoritative
    # Plaid ID was bound before the v2 identity contract.  New rows use the
    # namespaced candidate; no populated key is rewritten.
    existing_binding = conn.execute(
        "SELECT transaction_id FROM transactions "
        "WHERE plaid_transaction_id=? ORDER BY imported_at, transaction_id LIMIT 1",
        (plaid_transaction_id,),
    ).fetchone()
    if existing_binding:
        conn.execute(
            "UPDATE transactions SET plaid_item_id=COALESCE(plaid_item_id, ?), "
            "plaid_transaction_id=COALESCE(plaid_transaction_id, ?), "
            "account=COALESCE(NULLIF(account, ''), ?) "
            "WHERE transaction_id=?",
            (item_id, plaid_transaction_id, account_name,
             existing_binding["transaction_id"]),
        )
        return 0

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO transactions
           (transaction_id, date, description_raw, merchant_raw, amount,
            amount_cents, currency, account, source_filename, imported_at,
            plaid_item_id, plaid_transaction_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (candidate_txn_id, date, description, description, amount,
         amount_cents, "USD", account_name, "plaid-sync", now, item_id,
         plaid_transaction_id),
    )

    # Auto-categorize using alias rules + keyword heuristics
    aliases = _get_active_aliases(entity_key)
    stripped = _strip_platform_prefix(description)
    alias = _match_alias(description, aliases) or _match_alias(stripped, aliases)
    if alias:
        merchant_canonical = alias["merchant_canonical"]
        cat = alias.get("default_category")
        conn.execute(
            "UPDATE transactions SET merchant_canonical=?, category=?, "
            "confidence=? WHERE transaction_id=?",
            (merchant_canonical, cat, 0.95 if cat else None, candidate_txn_id),
        )
    else:
        cat, subcat, confidence = _keyword_suggest(description)
        if cat:
            conn.execute(
                "UPDATE transactions SET category=?, subcategory=?, "
                "confidence=? WHERE transaction_id=?",
                (cat, subcat, confidence, candidate_txn_id),
            )
        else:
            # No alias or keyword match — mark for manual review
            conn.execute(
                "UPDATE transactions SET category='Needs Review', "
                "subcategory='General', confidence=0.1 "
                "WHERE transaction_id=?",
                (candidate_txn_id,),
            )
    return 1

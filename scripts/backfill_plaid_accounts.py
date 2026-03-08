"""
One-time script: backfill account names on Plaid transactions.

Resets Plaid cursors, re-syncs all transactions, and fills in the
account column on existing transactions that were missing it.

Run on production:
  fly ssh console -a ledger-oak -C 'python3 /app/scripts/backfill_plaid_accounts.py'
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATA_DIR", "/data")

import sqlite3
from datetime import datetime, timezone

from core.db import get_connection, compute_transaction_id
from core.plaid_client import get_transactions as plaid_get_transactions


def main():
    conn = get_connection("personal")
    conn.row_factory = sqlite3.Row

    # Check before state
    missing_before = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE source_filename = 'plaid-sync' AND (account IS NULL OR account = '')"
    ).fetchone()[0]
    total_plaid = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE source_filename = 'plaid-sync'"
    ).fetchone()[0]
    print(f"Before: {missing_before}/{total_plaid} Plaid txns missing account")

    items = conn.execute(
        "SELECT item_id, access_token, institution_name, cursor FROM plaid_items"
    ).fetchall()
    print(f"Processing {len(items)} Plaid items...")

    total_backfilled = 0

    for item in items:
        inst = item["institution_name"]
        try:
            result = plaid_get_transactions(item["access_token"], item["cursor"] or None)
            added = result["added"]
            print(f"  {inst}: {len(added)} added, {len(result['modified'])} modified")

            for t in added:
                acct_row = conn.execute(
                    "SELECT name FROM plaid_accounts WHERE account_id=?",
                    (t["account_id"],),
                ).fetchone()
                acct_name = acct_row["name"] if acct_row else None

                description = t.get("merchant_name") or t.get("name") or ""
                amount = -t["amount"]
                txn_id = compute_transaction_id(t["date"], amount, description)

                cur = conn.execute(
                    "UPDATE transactions SET "
                    "plaid_item_id=COALESCE(plaid_item_id, ?), "
                    "plaid_transaction_id=COALESCE(plaid_transaction_id, ?), "
                    "account=COALESCE(NULLIF(account, ''), ?) "
                    "WHERE transaction_id=? AND (account IS NULL OR account = '')",
                    (item["item_id"], t["plaid_transaction_id"], acct_name, txn_id),
                )
                if cur.rowcount > 0:
                    total_backfilled += 1

            # Update cursor
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE plaid_items SET cursor=?, last_synced=? WHERE item_id=?",
                (result["next_cursor"], now, item["item_id"]),
            )
            conn.commit()

        except Exception as e:
            print(f"  ERROR {inst}: {e}")

    print(f"\nBackfilled {total_backfilled} transactions")

    missing_after = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE source_filename = 'plaid-sync' AND (account IS NULL OR account = '')"
    ).fetchone()[0]
    print(f"After: {missing_after}/{total_plaid} Plaid txns still missing account")

    conn.close()


if __name__ == "__main__":
    main()

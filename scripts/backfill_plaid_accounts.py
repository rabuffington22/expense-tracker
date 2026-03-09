"""
One-time script: backfill account names on Plaid transactions.

Uses the date-range transactions/get endpoint (does NOT touch sync cursors).
Matches by plaid_transaction_id to fill in account + plaid_item_id.

Run locally:
  python scripts/backfill_plaid_accounts.py

Run on production:
  fly ssh console -a ledger-oak -C 'python3 /app/scripts/backfill_plaid_accounts.py'
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default to local_state for local runs, /data on Fly
if not os.environ.get("DATA_DIR"):
    if os.path.exists("/data"):
        os.environ["DATA_DIR"] = "/data"
    else:
        os.environ["DATA_DIR"] = "./local_state"

from datetime import date, timedelta

from core.db import get_connection
from core.plaid_client import get_transactions_by_date

ENTITIES = ["personal", "company", "luxelegacy"]


def backfill_entity(entity_key: str) -> int:
    """Backfill account info for one entity. Returns count of updated rows."""
    conn = get_connection(entity_key)
    try:
        # Find transactions with plaid_transaction_id but missing account
        missing = conn.execute("""
            SELECT transaction_id, plaid_transaction_id, plaid_item_id, date
            FROM transactions
            WHERE plaid_transaction_id IS NOT NULL
              AND (account IS NULL OR account = '')
        """).fetchall()

        if not missing:
            print(f"  {entity_key}: no transactions missing account info")
            return 0

        print(f"  {entity_key}: {len(missing)} transactions missing account info")

        # Load all Plaid items
        items = conn.execute("SELECT * FROM plaid_items").fetchall()
        if not items:
            print(f"  {entity_key}: no Plaid items configured")
            return 0

        # Build account_id -> (account_name, item_id) lookup
        acct_lookup = {}
        for item in items:
            accts = conn.execute(
                "SELECT account_id, name FROM plaid_accounts WHERE item_id=?",
                (item["item_id"],),
            ).fetchall()
            for a in accts:
                acct_lookup[a["account_id"]] = (a["name"], item["item_id"])

        # Get overall date range of missing transactions
        dates = [row["date"] for row in missing]
        start_date = date.fromisoformat(min(dates)) - timedelta(days=5)
        end_date = date.fromisoformat(max(dates)) + timedelta(days=5)

        # For each Plaid item, fetch transactions by date range from Plaid API
        plaid_txn_map = {}  # plaid_transaction_id -> account_id
        for item in items:
            inst = item["institution_name"] or item["item_id"]
            print(f"    Fetching {inst} ({start_date} to {end_date})...")
            try:
                txns = get_transactions_by_date(
                    item["access_token"], start_date, end_date
                )
                for t in txns:
                    plaid_txn_map[t["plaid_transaction_id"]] = t["account_id"]
                print(f"    Got {len(txns)} transactions from Plaid API")
            except Exception as e:
                print(f"    ERROR fetching {inst}: {e}")
                continue

        # Match and update
        updated = 0
        for row in missing:
            ptid = row["plaid_transaction_id"]
            if ptid in plaid_txn_map:
                account_id = plaid_txn_map[ptid]
                if account_id in acct_lookup:
                    acct_name, item_id = acct_lookup[account_id]
                    conn.execute(
                        "UPDATE transactions SET account=?, "
                        "plaid_item_id=COALESCE(plaid_item_id, ?) "
                        "WHERE transaction_id=?",
                        (acct_name, item_id, row["transaction_id"]),
                    )
                    updated += 1
                else:
                    print(f"    WARNING: account_id {account_id} not in plaid_accounts")
            else:
                # Transaction not found in Plaid API response
                print(f"    MISS: {ptid} ({row['date']}) not found in Plaid API")

        conn.commit()
        print(f"  {entity_key}: updated {updated}/{len(missing)} transactions")
        return updated
    finally:
        conn.close()


def main():
    print("Backfilling Plaid account info on transactions...\n")
    total = 0
    for entity in ENTITIES:
        total += backfill_entity(entity)
    print(f"\nDone. Total updated: {total}")


if __name__ == "__main__":
    main()

"""Push LL transactions to luxurious-luxury's Supabase project.

Called after each successful Plaid sync for the `luxelegacy` entity. Idempotent —
uses Supabase upsert with `plaid_transaction_id` as the conflict key, so re-pushing
the same rows is a no-op aside from refreshing `synced_at`.

Source of truth stays in Ledger; the luxurious-luxury app only reads this mirror.
See ~/.claude/plans/polymorphic-mixing-whistle.md for the architecture.
"""
from __future__ import annotations

from collections import Counter
import logging
import os

import requests

from core.db import get_connection

log = logging.getLogger(__name__)

# Transfers / payments / owner draws aren't sale or purchase activity — exclude them
# from the mirror so the matching UI in luxurious-luxury isn't cluttered.
EXCLUDE_CATS = ("Internal Transfer", "Credit Card Payment", "Owner Draw")


def push_luxelegacy_to_supabase() -> int:
    """Mirror LL transactions to the luxury app's Supabase. Returns rows pushed.

    No-op when env vars aren't set or when there are no eligible transactions.
    Failures are logged and swallowed — Plaid sync must not break if the bridge
    is down.
    """
    url = os.environ.get("LUXURY_SUPABASE_URL", "").rstrip("/")
    service_key = os.environ.get("LUXURY_SUPABASE_SERVICE_KEY", "")
    if not url or not service_key:
        return 0

    placeholders = ",".join("?" for _ in EXCLUDE_CATS)
    conn = get_connection("luxelegacy")
    try:
        rows = conn.execute(
            f"""SELECT plaid_transaction_id, transaction_id, date, amount,
                       description_raw, merchant_canonical, account, category
                FROM transactions
                WHERE plaid_transaction_id IS NOT NULL
                  AND COALESCE(category, '') NOT IN ({placeholders})
                ORDER BY plaid_transaction_id, transaction_id""",
            EXCLUDE_CATS,
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return 0

    valid_rows = []
    valid_keys = []
    malformed_rows = 0
    for row in rows:
        plaid_key = row["plaid_transaction_id"]
        if (
            not isinstance(plaid_key, str)
            or not plaid_key
            or plaid_key != plaid_key.strip()
        ):
            malformed_rows += 1
            continue
        valid_rows.append(row)
        valid_keys.append(plaid_key)

    key_counts = Counter(valid_keys)
    duplicate_keys = {key for key, count in key_counts.items() if count > 1}
    duplicate_rows = sum(key_counts[key] for key in duplicate_keys)

    if malformed_rows or duplicate_rows:
        log.warning(
            "luxury_bridge skipped malformed_rows=%d duplicate_rows=%d "
            "duplicate_keys=%d",
            malformed_rows,
            duplicate_rows,
            len(duplicate_keys),
        )

    payload = [
        {
            "plaid_transaction_id": r["plaid_transaction_id"],
            "ledger_transaction_id": r["transaction_id"],
            "date": r["date"],
            "amount": float(r["amount"]),
            "description": r["description_raw"] or "",
            "merchant_canonical": r["merchant_canonical"],
            "account_name": r["account"],
            "category": r["category"],
        }
        for r in valid_rows
        if r["plaid_transaction_id"] not in duplicate_keys
    ]

    if not payload:
        return 0

    try:
        resp = requests.post(
            f"{url}/rest/v1/ledger_transactions",
            headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates",
            },
            params={"on_conflict": "plaid_transaction_id"},
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return len(payload)
    except Exception as exc:
        log.warning("luxury_bridge push failed: %s", exc)
        return 0

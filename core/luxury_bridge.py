"""Push LL transactions to luxurious-luxury's Supabase project.

Called after each successful Plaid sync for the `luxelegacy` entity. Idempotent —
uses Supabase upsert with `plaid_transaction_id` as the conflict key, so re-pushing
the same rows is a no-op aside from refreshing `synced_at`.

Source of truth stays in Ledger; the luxurious-luxury app only reads this mirror.
See ~/.claude/plans/polymorphic-mixing-whistle.md for the architecture.
"""
from __future__ import annotations

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
    key = os.environ.get("LUXURY_SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return 0

    placeholders = ",".join("?" for _ in EXCLUDE_CATS)
    conn = get_connection("luxelegacy")
    try:
        rows = conn.execute(
            f"""SELECT plaid_transaction_id, transaction_id, date, amount,
                       description_raw, merchant_canonical, account, category
                FROM transactions
                WHERE plaid_transaction_id IS NOT NULL
                  AND COALESCE(category, '') NOT IN ({placeholders})""",
            EXCLUDE_CATS,
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return 0

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
        for r in rows
    ]

    try:
        resp = requests.post(
            f"{url}/rest/v1/ledger_transactions",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates",
            },
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return len(payload)
    except Exception as exc:
        log.warning("luxury_bridge push failed: %s", exc)
        return 0

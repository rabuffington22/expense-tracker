#!/usr/bin/env python3
"""Insert manually-tracked credit card accounts into production databases.

Run on Fly: fly ssh console -a ledger-oak -C 'python3 /app/scripts/insert_manual_cards.py'
"""
import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", "./local_state")

# ── Personal entity: 3 cards ──────────────────────────────────────────────────
personal_cards = [
    {
        "account_name": "Chase Amazon",
        "account_type": "credit_card",
        "balance_cents": 3403200,       # $34,032
        "credit_limit_cents": 3960000,  # $39,600
        "apr_bps": 2274,                # 22.74%
        "sort_order": 103,
        "payment_due_day": 17,
        "payment_amount_cents": 113000, # $1,130
        "balance_source": "manual",
    },
    {
        "account_name": "Ryan Apple Card",
        "account_type": "credit_card",
        "balance_cents": 374537,        # $3,745.37
        "credit_limit_cents": 400000,   # $4,000
        "apr_bps": 2549,                # 25.49%
        "sort_order": 104,
        "payment_due_day": 31,
        "payment_amount_cents": 0,
        "balance_source": "manual",
    },
    {
        "account_name": "Kristine Apple Card",
        "account_type": "credit_card",
        "balance_cents": 1867269,       # $18,672.69
        "credit_limit_cents": 1950000,  # $19,500
        "apr_bps": 2549,                # 25.49%
        "sort_order": 105,
        "payment_due_day": 0,           # needs to be set correctly
        "payment_amount_cents": 0,
        "balance_source": "manual",
    },
]

# ── BFM entity: 1 card ───────────────────────────────────────────────────────
bfm_cards = [
    {
        "account_name": "Barclays MC",
        "account_type": "credit_card",
        "balance_cents": 0,
        "credit_limit_cents": 1290000,  # $12,900
        "apr_bps": None,
        "sort_order": 102,
        "payment_due_day": 0,
        "payment_amount_cents": 0,
        "balance_source": "manual",
    },
]


def insert_cards(db_path, cards, entity_label):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    inserted = 0
    skipped = 0
    for card in cards:
        # Check if already exists
        c.execute(
            "SELECT account_name FROM account_balances WHERE account_name = ?",
            (card["account_name"],),
        )
        if c.fetchone():
            print(f"  SKIP {card['account_name']} (already exists)")
            skipped += 1
            continue
        c.execute(
            "INSERT INTO account_balances "
            "(account_name, account_type, balance_cents, credit_limit_cents, "
            "apr_bps, sort_order, payment_due_day, payment_amount_cents, balance_source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                card["account_name"],
                card["account_type"],
                card["balance_cents"],
                card["credit_limit_cents"],
                card["apr_bps"],
                card["sort_order"],
                card["payment_due_day"],
                card["payment_amount_cents"],
                card["balance_source"],
            ),
        )
        print(f"  ADD  {card['account_name']} — ${card['balance_cents'] / 100:,.2f}")
        inserted += 1
    conn.commit()
    conn.close()
    print(f"  {entity_label}: {inserted} inserted, {skipped} skipped\n")


print("=== Personal ===")
insert_cards(os.path.join(DATA_DIR, "personal.sqlite"), personal_cards, "Personal")

print("=== BFM ===")
insert_cards(os.path.join(DATA_DIR, "company.sqlite"), bfm_cards, "BFM")

print("Done!")

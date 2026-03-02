"""Database initialization, migrations, and connection management."""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# ── Data directory ────────────────────────────────────────────────────────────

def get_data_dir() -> Path:
    """Return the DATA_DIR path, creating subdirs if needed."""
    data_dir = Path(os.environ.get("DATA_DIR", "./local_state"))
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    (data_dir / "backups").mkdir(exist_ok=True)
    return data_dir


_VALID_ENTITY_KEYS = {"personal", "company", "luxelegacy"}


def get_db_path(entity: str) -> Path:
    """Return the SQLite DB path for the given entity."""
    entity = entity.lower()
    if entity not in _VALID_ENTITY_KEYS:
        raise ValueError(f"Unknown entity: {entity!r}. Must be one of {_VALID_ENTITY_KEYS}.")
    return get_data_dir() / f"{entity}.sqlite"


def get_connection(entity: str) -> sqlite3.Connection:
    """Open and return a WAL-mode sqlite3 connection for the given entity."""
    conn = sqlite3.connect(str(get_db_path(entity)))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Schema migrations ─────────────────────────────────────────────────────────

_MIGRATION_1 = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id     TEXT PRIMARY KEY,
    date               TEXT NOT NULL,
    description_raw    TEXT NOT NULL,
    merchant_raw       TEXT,
    merchant_canonical TEXT,
    amount             REAL NOT NULL,
    currency           TEXT DEFAULT 'USD',
    account            TEXT,
    category           TEXT,
    confidence         REAL,
    notes              TEXT,
    source_filename    TEXT,
    imported_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS merchant_aliases (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type       TEXT NOT NULL CHECK(pattern_type IN ('contains','regex')),
    pattern            TEXT NOT NULL,
    merchant_canonical TEXT NOT NULL,
    default_category   TEXT,
    active             INTEGER NOT NULL DEFAULT 1,
    created_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS import_profiles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT UNIQUE NOT NULL,
    date_col        TEXT NOT NULL,
    description_col TEXT NOT NULL,
    amount_col      TEXT NOT NULL,
    merchant_col    TEXT,
    account_col     TEXT,
    currency_col    TEXT,
    amount_negate   INTEGER NOT NULL DEFAULT 0,
    date_format     TEXT,
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_txn_date     ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_txn_category ON transactions(category);
"""

_MIGRATION_2 = """
INSERT OR IGNORE INTO import_profiles
    (name, date_col, description_col, amount_col, merchant_col, account_col, currency_col, amount_negate, date_format, created_at)
VALUES
    ('Amex Credit Card', 'Date', 'Merchant', 'Amount', NULL, NULL, NULL, 1, NULL, datetime('now')),
    ('Bank Checking (Debit/Credit)', 'Transaction Date', 'Details', 'Debit', NULL, 'Account', NULL, 0, NULL, datetime('now'));
"""

_MIGRATION_3 = """
CREATE TABLE IF NOT EXISTS import_checklist (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    label             TEXT NOT NULL,
    filename_pattern  TEXT,
    profile_name      TEXT,
    url               TEXT,
    notes             TEXT,
    sort_order        INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS import_checklist_status (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_item_id INTEGER NOT NULL REFERENCES import_checklist(id) ON DELETE CASCADE,
    month             TEXT NOT NULL,
    completed         INTEGER NOT NULL DEFAULT 0,
    completed_at      TEXT,
    source_filename   TEXT,
    UNIQUE(checklist_item_id, month)
);
"""

_MIGRATION_4 = """
INSERT OR IGNORE INTO import_profiles
    (name, date_col, description_col, amount_col, merchant_col, account_col, currency_col, amount_negate, date_format, created_at)
VALUES
    ('Capital One (Debit/Credit)', 'Transaction Date', 'Description', '(auto-merge Debit/Credit)', NULL, 'Card No.', NULL, 0, NULL, datetime('now'));

INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('Capital One Business CC', 'capone-business', 'Capital One (Debit/Credit)', NULL, 'Rename to capone-business.csv when downloading', 1, datetime('now')),
    ('Capital One Personal CC', 'capone-personal', 'Capital One (Debit/Credit)', NULL, 'Rename to capone-personal.csv when downloading', 2, datetime('now')),
    ('Chase Amazon CC', 'chase-amazon', NULL, NULL, 'Personal card — need to regain login access. Profile TBD once CSV format is known.', 3, datetime('now'));
"""

_MIGRATION_5 = """
INSERT OR IGNORE INTO import_profiles
    (name, date_col, description_col, amount_col, merchant_col, account_col, currency_col, amount_negate, date_format, created_at)
VALUES
    ('Citi Credit Card', 'Date', 'Description', '(auto-merge Debit/Credit)', NULL, 'Member Name', NULL, 0, '%m/%d/%Y', datetime('now'));

INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('Citi Personal CC', 'statement closed', 'Citi Credit Card', NULL, 'Filename is "Statement closed [date].CSV"', 4, datetime('now'));
"""

_MIGRATION_6 = """
INSERT OR IGNORE INTO import_profiles
    (name, date_col, description_col, amount_col, merchant_col, account_col, currency_col, amount_negate, date_format, created_at)
VALUES
    ('BofA Credit Card', 'Posted Date', 'Payee', 'Amount', NULL, NULL, NULL, 0, '%m/%d/%Y', datetime('now'));

INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('BofA Personal CC', '_5625', 'BofA Credit Card', NULL, 'Filename is "MonthYear_5625.csv"', 5, datetime('now'));
"""

_MIGRATION_7 = """
INSERT OR IGNORE INTO import_profiles
    (name, date_col, description_col, amount_col, merchant_col, account_col, currency_col, amount_negate, date_format, created_at)
VALUES
    ('BofA Checking', 'Date', 'Description', 'Amount', NULL, NULL, NULL, 0, '%m/%d/%Y', datetime('now'));

INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('BofA Personal Checking', 'stmt', 'BofA Checking', NULL, 'Filename is "stmt.csv" — has summary header that is auto-skipped', 6, datetime('now'));
"""

_MIGRATION_8 = """
UPDATE import_checklist SET filename_pattern = 'stmt.csv'
    WHERE label = 'BofA Personal Checking' AND filename_pattern = 'stmt';

INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('BofA Emergency Acct', 'BOA Emergency', 'BofA Checking', NULL, 'Filename is "BOA Emergency acct.csv" — same summary header format', 7, datetime('now')),
    ('BofA Second Acct', 'BOA second', 'BofA Checking', NULL, 'Filename is "stmt BOA second acct.csv" — same summary header format', 8, datetime('now'));
"""

_MIGRATION_9 = """
INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('Prosperity Business Checking', 'prosperity', NULL, NULL, 'PDF statement — filename is "prosperity statement_MMDDYYYY.pdf". No CSV available; text-based PDF parser extracts transactions automatically.', 9, datetime('now'));
"""

_MIGRATION_10 = """
UPDATE import_checklist
    SET label = 'Chase Amazon Visa',
        filename_pattern = 'chase amazon',
        profile_name = NULL,
        notes = 'PDF statement — personal card. Filenames like "chase amazon 20260120-statements-2357-.pdf". Text-based PDF parser handles short MM/DD dates with year inference.'
    WHERE label = 'Chase Amazon CC';

INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, created_at)
VALUES
    ('Barclay CC', 'barclay', NULL, NULL,
     'PDF statement — personal card, rarely used. Filenames like "barclay cc nov 6.pdf". Named-month date format (Mon DD).', 10, datetime('now')),
    ('Amex Business Card', 'amex', NULL, NULL,
     'PDF statement — company card with multiple cardholders (Ryan, Andrea, Sarah). Filenames like "amex 2026-01-22.pdf". Full MM/DD/YY dates with asterisk posting-date notation.', 11, datetime('now'));
"""

_MIGRATION_11 = """
ALTER TABLE import_checklist ADD COLUMN entity TEXT NOT NULL DEFAULT 'personal';

UPDATE import_checklist SET entity = 'company' WHERE label = 'Capital One Business CC';
UPDATE import_checklist SET entity = 'company' WHERE label = 'Prosperity Business Checking';
UPDATE import_checklist SET entity = 'company' WHERE label = 'Amex Business Card';
"""

_MIGRATION_12 = """
INSERT INTO merchant_aliases
    (pattern_type, pattern, merchant_canonical, default_category, active, created_at)
VALUES
    ('contains', 'AUTOPAY PAYMENT', 'AutoPay Payment', 'Transfers', 1, datetime('now')),
    ('contains', 'ONLINE PAYMENT THANK YOU', 'Payment', 'Transfers', 1, datetime('now')),
    ('contains', 'MOBILE PAYMENT', 'Mobile Payment', 'Transfers', 1, datetime('now')),
    ('contains', 'AUTOMATIC PAYMENT', 'AutoPay Payment', 'Transfers', 1, datetime('now')),
    ('contains', 'PAYMENT RECEIVED', 'Payment Received', 'Transfers', 1, datetime('now')),
    ('contains', 'DIRECT DEP', 'Direct Deposit', 'Income', 1, datetime('now')),
    ('contains', 'PAYROLL', 'Payroll', 'Income', 1, datetime('now')),
    ('contains', 'LATE PAYMENT FEE', 'Late Payment Fee', 'Fees', 1, datetime('now')),
    ('contains', 'INTEREST CHARGE', 'Interest Charge', 'Fees', 1, datetime('now')),
    ('contains', 'ANNUAL FEE', 'Annual Fee', 'Fees', 1, datetime('now')),
    ('contains', 'FOREIGN TRANSACTION FEE', 'Foreign Transaction Fee', 'Fees', 1, datetime('now')),
    ('contains', 'OVERDRAFT FEE', 'Overdraft Fee', 'Fees', 1, datetime('now')),
    ('contains', 'RETURNED ITEM', 'Returned Item Fee', 'Fees', 1, datetime('now')),
    ('contains', 'NETFLIX', 'Netflix', 'Subscriptions', 1, datetime('now')),
    ('contains', 'SPOTIFY', 'Spotify', 'Subscriptions', 1, datetime('now')),
    ('contains', 'HULU', 'Hulu', 'Subscriptions', 1, datetime('now')),
    ('contains', 'APPLE.COM/BILL', 'Apple Services', 'Subscriptions', 1, datetime('now')),
    ('contains', 'AMAZON PRIME', 'Amazon Prime', 'Subscriptions', 1, datetime('now')),
    ('contains', 'DISNEY PLUS', 'Disney+', 'Subscriptions', 1, datetime('now')),
    ('contains', 'UBER EATS', 'Uber Eats', 'Dining', 1, datetime('now')),
    ('contains', 'DOORDASH', 'DoorDash', 'Dining', 1, datetime('now')),
    ('contains', 'GRUBHUB', 'Grubhub', 'Dining', 1, datetime('now')),
    ('contains', 'STARBUCKS', 'Starbucks', 'Dining', 1, datetime('now')),
    ('contains', 'MCDONALD', 'McDonald''s', 'Dining', 1, datetime('now')),
    ('contains', 'CHICK-FIL', 'Chick-fil-A', 'Dining', 1, datetime('now')),
    ('contains', 'CHIPOTLE', 'Chipotle', 'Dining', 1, datetime('now')),
    ('contains', 'WHATABURGER', 'Whataburger', 'Dining', 1, datetime('now')),
    ('contains', 'TACO BELL', 'Taco Bell', 'Dining', 1, datetime('now')),
    ('contains', 'PANERA', 'Panera Bread', 'Dining', 1, datetime('now')),
    ('contains', 'KROGER', 'Kroger', 'Groceries', 1, datetime('now')),
    ('contains', 'WHOLE FOODS', 'Whole Foods', 'Groceries', 1, datetime('now')),
    ('contains', 'TRADER JOE', 'Trader Joe''s', 'Groceries', 1, datetime('now')),
    ('contains', 'H-E-B', 'H-E-B', 'Groceries', 1, datetime('now')),
    ('contains', 'ALDI', 'Aldi', 'Groceries', 1, datetime('now')),
    ('contains', 'COSTCO', 'Costco', 'Groceries', 1, datetime('now')),
    ('contains', 'LYFT', 'Lyft', 'Transportation', 1, datetime('now')),
    ('contains', 'COMCAST', 'Comcast/Xfinity', 'Utilities', 1, datetime('now')),
    ('contains', 'XFINITY', 'Comcast/Xfinity', 'Utilities', 1, datetime('now'));
"""

_MIGRATION_13 = """
CREATE TABLE IF NOT EXISTS amazon_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    payment_ref_id TEXT,
    order_date TEXT NOT NULL,
    charge_date TEXT,
    product_summary TEXT NOT NULL,
    amazon_category TEXT,
    order_total REAL NOT NULL DEFAULT 0,
    matched_transaction_id TEXT,
    imported_at TEXT NOT NULL
);
"""

_MIGRATION_14 = """
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Kids', datetime('now'));
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Household', datetime('now'));
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Health & Beauty', datetime('now'));
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Clothing', datetime('now'));
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Pet Supplies', datetime('now'));
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Office', datetime('now'));
INSERT OR IGNORE INTO categories (name, created_at) VALUES ('Kristine Business', datetime('now'));
"""

_MIGRATION_15 = """
CREATE TABLE IF NOT EXISTS subcategories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(category_name, name)
);

ALTER TABLE transactions ADD COLUMN subcategory TEXT;
"""

_MIGRATION_16 = """
ALTER TABLE amazon_orders ADD COLUMN category TEXT;
ALTER TABLE amazon_orders ADD COLUMN subcategory TEXT;
"""

_MIGRATION_17 = """
ALTER TABLE amazon_orders ADD COLUMN vendor TEXT DEFAULT 'amazon';
"""

_MIGRATION_18 = """
CREATE TABLE IF NOT EXISTS plaid_items (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id          TEXT UNIQUE NOT NULL,
    access_token     TEXT NOT NULL,
    institution_name TEXT,
    institution_id   TEXT,
    cursor           TEXT,
    created_at       TEXT NOT NULL,
    last_synced      TEXT
);

CREATE TABLE IF NOT EXISTS plaid_accounts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id    TEXT NOT NULL REFERENCES plaid_items(item_id) ON DELETE CASCADE,
    account_id TEXT UNIQUE NOT NULL,
    name       TEXT,
    mask       TEXT,
    type       TEXT,
    subtype    TEXT,
    enabled    INTEGER NOT NULL DEFAULT 1
);

ALTER TABLE transactions ADD COLUMN plaid_item_id TEXT;
"""

_MIGRATION_19 = """
ALTER TABLE transactions ADD COLUMN plaid_transaction_id TEXT;
CREATE INDEX IF NOT EXISTS idx_txn_plaid_id ON transactions(plaid_transaction_id);
"""

_MIGRATION_20 = """
INSERT OR IGNORE INTO import_checklist
    (label, filename_pattern, profile_name, url, notes, sort_order, entity, created_at)
VALUES
    ('BofA Business Checking (LL)', 'bofa', 'BofA Checking', NULL,
     'Luxe Legacy business checking — BofA Checking CSV format.', 1, 'luxelegacy', datetime('now'));
"""

_MIGRATION_21 = """
ALTER TABLE transactions ADD COLUMN amount_cents INTEGER;
UPDATE transactions SET amount_cents = CAST(ROUND(amount * 100) AS INTEGER);

ALTER TABLE amazon_orders ADD COLUMN order_total_cents INTEGER;
UPDATE amazon_orders SET order_total_cents = CAST(ROUND(order_total * 100) AS INTEGER);

CREATE INDEX IF NOT EXISTS idx_ao_matched_txn ON amazon_orders(matched_transaction_id);
"""

_MIGRATION_22 = """
CREATE TABLE IF NOT EXISTS saved_views (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    page         TEXT NOT NULL CHECK(page IN ('dashboard', 'transactions')),
    query_string TEXT NOT NULL DEFAULT '',
    created_at   TEXT NOT NULL
);
"""

_MIGRATION_23 = """
ALTER TABLE saved_views ADD COLUMN is_default INTEGER NOT NULL DEFAULT 0;
"""

_MIGRATION_24 = """
CREATE TABLE IF NOT EXISTS statement_schedules (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    statement_day INTEGER NOT NULL,
    notes        TEXT,
    is_active    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS statement_completions (
    id           INTEGER PRIMARY KEY,
    schedule_id  INTEGER NOT NULL REFERENCES statement_schedules(id) ON DELETE CASCADE,
    period_key   TEXT NOT NULL,
    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(schedule_id, period_key)
);
"""

_MIGRATION_25 = """
CREATE TABLE IF NOT EXISTS periodic_tasks (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    cadence      TEXT NOT NULL DEFAULT 'monthly',
    day_of_month INTEGER NOT NULL DEFAULT 1,
    notes        TEXT,
    is_active    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS periodic_completions (
    id           INTEGER PRIMARY KEY,
    task_id      INTEGER NOT NULL REFERENCES periodic_tasks(id) ON DELETE CASCADE,
    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

_MIGRATION_26 = """
CREATE TABLE IF NOT EXISTS account_balances (
    id                INTEGER PRIMARY KEY,
    account_name      TEXT NOT NULL UNIQUE,
    balance_cents     INTEGER NOT NULL DEFAULT 0,
    balance_source    TEXT NOT NULL DEFAULT 'manual'
                      CHECK(balance_source IN ('manual', 'plaid')),
    plaid_account_id  TEXT,
    low_threshold_cents INTEGER NOT NULL DEFAULT 50000,
    updated_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transfer_dismissals (
    id                INTEGER PRIMARY KEY,
    from_account      TEXT NOT NULL,
    to_account        TEXT NOT NULL,
    dismissed_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at        TEXT NOT NULL
);
"""

_MIGRATION_27 = """
ALTER TABLE account_balances ADD COLUMN account_type TEXT NOT NULL DEFAULT 'bank'
    CHECK(account_type IN ('bank', 'credit_card'));
ALTER TABLE account_balances ADD COLUMN credit_limit_cents INTEGER NOT NULL DEFAULT 0;
ALTER TABLE account_balances ADD COLUMN payment_due_day INTEGER;
ALTER TABLE account_balances ADD COLUMN payment_amount_cents INTEGER NOT NULL DEFAULT 0;
ALTER TABLE account_balances ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0;
"""

_MIGRATION_28 = """
CREATE TABLE IF NOT EXISTS manual_recurring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES account_balances(id) ON DELETE CASCADE,
    merchant TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL CHECK(day_of_month BETWEEN 1 AND 31),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_MIGRATION_29 = """
ALTER TABLE account_balances ADD COLUMN payment_due_date TEXT;
"""

_MIGRATION_30 = """
CREATE TABLE IF NOT EXISTS queue_dismissals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    queue_type TEXT NOT NULL UNIQUE,
    dismissed_at TEXT NOT NULL DEFAULT (datetime('now')),
    dismissed_before TEXT NOT NULL
);
"""

_MIGRATIONS: list[tuple[int, str]] = [
    (1, _MIGRATION_1),
    (2, _MIGRATION_2),
    (3, _MIGRATION_3),
    (4, _MIGRATION_4),
    (5, _MIGRATION_5),
    (6, _MIGRATION_6),
    (7, _MIGRATION_7),
    (8, _MIGRATION_8),
    (9, _MIGRATION_9),
    (10, _MIGRATION_10),
    (11, _MIGRATION_11),
    (12, _MIGRATION_12),
    (13, _MIGRATION_13),
    (14, _MIGRATION_14),
    (15, _MIGRATION_15),
    (16, _MIGRATION_16),
    (17, _MIGRATION_17),
    (18, _MIGRATION_18),
    (19, _MIGRATION_19),
    (20, _MIGRATION_20),
    (21, _MIGRATION_21),
    (22, _MIGRATION_22),
    (23, _MIGRATION_23),
    (24, _MIGRATION_24),
    (25, _MIGRATION_25),
    (26, _MIGRATION_26),
    (27, _MIGRATION_27),
    (28, _MIGRATION_28),
    (29, _MIGRATION_29),
    (30, _MIGRATION_30),
]

_DEFAULT_CATEGORIES = [
    "Groceries", "Dining", "Transportation", "Utilities", "Healthcare",
    "Entertainment", "Shopping", "Travel", "Housing", "Income",
    "Fees", "Subscriptions", "Other",
    "Kids", "Household", "Health & Beauty", "Clothing",
    "Pet Supplies", "Office", "Kristine Business",
    "Home Improvement", "Personal Care", "Unknown",
    "Student Loans", "Retirement", "Storage", "Ranch",
    "Credit Card Payment", "Education", "Ask Kristine",
    "Internal Transfer", "Electronics",
]


_DEFAULT_SUBCATEGORIES = {
    "Entertainment": ["Audible", "Streaming", "Movies", "Books", "Games"],
"Dining": ["Fast Food", "Restaurant", "Coffee", "Delivery"],
    "Shopping": ["Online", "In-Store"],
    "Kids": ["Diapers & Wipes", "Toys", "Gear", "Clothing"],
    "Clothing": ["Women", "Men", "Kids"],
    "Household": ["Cleaning", "Kitchen", "Storage"],
    "Health & Beauty": ["Vitamins", "Skincare", "Haircare"],
    "Subscriptions": ["Streaming", "Software", "Membership"],
    "Transportation": ["Gas", "Parking", "Rideshare", "Maintenance", "Tolls"],
    "Home Improvement": ["Tools", "Hardware", "Decor"],
    "Pet Supplies": ["Food", "Toys", "Health"],
    "Electronics": ["Accessories", "Devices"],
    "Student Loans": ["Ryan", "Kristine"],
    "Ranch": ["Equipment", "Utilities", "Insurance"],
}


_DEFAULT_PROFILES = [
    {
        "name": "Amex Credit Card",
        "date_col": "Date",
        "description_col": "Merchant",
        "amount_col": "Amount",
        "amount_negate": 1,
    },
    {
        "name": "Bank Checking (Debit/Credit)",
        "date_col": "Transaction Date",
        "description_col": "Details",
        "amount_col": "Debit",  # auto-merge handles Debit+Credit
    },
]


def init_db(entity: str) -> None:
    """Initialize (or migrate) the database for the given entity."""
    conn = get_connection(entity)
    try:
        # Bootstrap version table before reading current version
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_version "
            "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        conn.commit()

        row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
        current = row[0] if row[0] is not None else 0

        for version, sql in _MIGRATIONS:
            if version > current:
                conn.executescript(sql)
                conn.execute(
                    "INSERT OR IGNORE INTO schema_version (version, applied_at) VALUES (?,?)",
                    (version, datetime.now(timezone.utc).isoformat()),
                )
                conn.commit()

        # Seed default categories once
        if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            conn.executemany(
                "INSERT OR IGNORE INTO categories (name, created_at) VALUES (?,?)",
                [(c, now) for c in _DEFAULT_CATEGORIES],
            )
            conn.commit()

        # Seed default subcategories once
        try:
            if conn.execute("SELECT COUNT(*) FROM subcategories").fetchone()[0] == 0:
                now = datetime.now(timezone.utc).isoformat()
                for cat, subs in _DEFAULT_SUBCATEGORIES.items():
                    for sub in subs:
                        conn.execute(
                            "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) "
                            "VALUES (?,?,?)",
                            (cat, sub, now),
                        )
                conn.commit()
        except sqlite3.OperationalError:
            pass  # subcategories table may not exist yet on older schema

        # Seed default import profiles once
        if conn.execute("SELECT COUNT(*) FROM import_profiles").fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            for p in _DEFAULT_PROFILES:
                conn.execute(
                    "INSERT OR IGNORE INTO import_profiles "
                    "(name, date_col, description_col, amount_col, merchant_col, "
                    "account_col, currency_col, amount_negate, date_format, created_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (p["name"], p["date_col"], p["description_col"], p["amount_col"],
                     p.get("merchant_col"), p.get("account_col"), p.get("currency_col"),
                     int(p.get("amount_negate", 0)), p.get("date_format"), now),
                )
            conn.commit()
    finally:
        conn.close()

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


def get_db_path(entity: str) -> Path:
    """Return the SQLite DB path for the given entity."""
    entity = entity.lower()
    if entity not in ("personal", "company"):
        raise ValueError(f"Unknown entity: {entity!r}. Must be 'personal' or 'company'.")
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

_MIGRATIONS: list[tuple[int, str]] = [
    (1, _MIGRATION_1),
    (2, _MIGRATION_2),
    (3, _MIGRATION_3),
]

_DEFAULT_CATEGORIES = [
    "Groceries", "Dining", "Transportation", "Utilities", "Healthcare",
    "Entertainment", "Shopping", "Travel", "Housing", "Income",
    "Transfers", "Fees", "Subscriptions", "Other",
]


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

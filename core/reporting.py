"""Query helpers for the Reports page."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from core.db import get_connection


# ── Effective Transactions CTE ─────────────────────────────────────────────────
# When a transaction has splits, the parent is excluded and split pieces appear
# instead (each with its own category/subcategory/amount_cents).  Unsplit
# transactions pass through unchanged.  Every reporting query should use this CTE
# instead of querying the raw `transactions` table.

_EFFECTIVE_TXNS_COLUMNS = """
    transaction_id, date, description_raw, merchant_raw, merchant_canonical,
    amount, currency, account, category, confidence, notes, source_filename,
    imported_at, subcategory, plaid_item_id, plaid_transaction_id, amount_cents
"""


def effective_txns_cte(alias: str = "t") -> str:
    """Return a CTE SQL fragment that expands split transactions.

    Usage::

        cte = effective_txns_cte("t")
        sql = f"WITH {cte} SELECT ... FROM t WHERE ..."
    """
    return f"""{alias} AS (
        SELECT {_EFFECTIVE_TXNS_COLUMNS},
               0 AS is_split_piece, CAST(NULL AS INTEGER) AS split_id
        FROM transactions
        WHERE NOT EXISTS (
            SELECT 1 FROM transaction_splits ts
            WHERE ts.transaction_id = transactions.transaction_id
        )
        UNION ALL
        SELECT
            txn.transaction_id, txn.date, txn.description_raw,
            txn.merchant_raw, txn.merchant_canonical,
            ts.amount_cents / 100.0 AS amount,
            txn.currency, txn.account,
            ts.category, txn.confidence,
            COALESCE(ts.description, txn.notes) AS notes,
            txn.source_filename, txn.imported_at,
            ts.subcategory, txn.plaid_item_id, txn.plaid_transaction_id,
            ts.amount_cents,
            1 AS is_split_piece, ts.id AS split_id
        FROM transactions txn
        JOIN transaction_splits ts ON ts.transaction_id = txn.transaction_id
    )"""


# ── Exclusion list (shared across queries) ─────────────────────────────────────

_EXCLUDE_CATS = (
    "Internal Transfer",
    "Credit Card Payment",
    "Income",
    "Owner Contribution",
    "Partner Buyout",
)

_EXCLUDE_CATS_NO_INCOME = (
    "Internal Transfer",
    "Credit Card Payment",
    "Owner Contribution",
    "Partner Buyout",
)

_EXCLUDE_SQL = "COALESCE(t.category,'') NOT IN ({})".format(
    ",".join(f"'{c}'" for c in _EXCLUDE_CATS)
)

_EXCLUDE_SQL_NO_INCOME = "COALESCE(t.category,'') NOT IN ({})".format(
    ",".join(f"'{c}'" for c in _EXCLUDE_CATS_NO_INCOME)
)


# ── Query helpers ──────────────────────────────────────────────────────────────

def get_monthly_totals(entity: str, start_month: str, end_month: str) -> pd.DataFrame:
    """
    Return spend by category per month for a date range.

    Parameters
    ----------
    start_month, end_month : 'YYYY-MM' strings (inclusive)

    Returns
    -------
    DataFrame with columns: month, category, total_amount  (positive spend)
    """
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            strftime('%Y-%m', t.date)                        AS month,
            COALESCE(NULLIF(t.category,''), 'Uncategorized') AS category,
            ABS(SUM(t.amount))                               AS total_amount
        FROM t
        WHERE strftime('%Y-%m', t.date) BETWEEN ? AND ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY month, category
        ORDER BY month, category
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_month, end_month))
    finally:
        conn.close()


def get_category_totals(entity: str, month: str) -> pd.DataFrame:
    """
    Return per-category spend totals for a given month (YYYY-MM).

    Returns
    -------
    DataFrame with columns: category, count, total_amount  (positive spend)
    """
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            COALESCE(NULLIF(t.category,''), 'Uncategorized') AS category,
            COUNT(*)                                          AS count,
            ABS(SUM(t.amount))                               AS total_amount
        FROM t
        WHERE strftime('%Y-%m', t.date) = ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY category
        ORDER BY total_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(month,))
    finally:
        conn.close()


def get_transactions(
    entity: str,
    month: Optional[str] = None,
    category: Optional[str] = None,
) -> pd.DataFrame:
    """
    Return transactions filtered by optional month (YYYY-MM) and/or category.

    Returns all transactions (both debits and credits) matching the filters,
    ordered newest first.
    """
    cte = effective_txns_cte("t")
    conditions: list[str] = []
    params: list = []

    if month:
        conditions.append("strftime('%Y-%m', t.date) = ?")
        params.append(month)

    if category is not None:
        if category == "Uncategorized":
            conditions.append("(t.category IS NULL OR t.category = '')")
        else:
            conditions.append("t.category = ?")
            params.append(category)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        WITH {cte}
        SELECT t.transaction_id, t.date, t.description_raw, t.merchant_canonical,
               t.amount, t.currency, t.account, t.category, t.confidence, t.notes,
               t.source_filename
        FROM t
        {where}
        ORDER BY t.date DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def get_uncategorized(entity: str) -> pd.DataFrame:
    """
    Return transactions with no category or confidence below 0.6.
    """
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT t.transaction_id, t.date, t.description_raw, t.merchant_raw,
               t.merchant_canonical, t.amount, t.category, t.subcategory,
               t.confidence, t.notes
        FROM t
        WHERE t.category IS NULL OR t.category = '' OR t.confidence < 0.6
        ORDER BY t.date DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def get_monthly_income(entity: str, start_month: str, end_month: str) -> pd.DataFrame:
    """
    Return total income per month for a date range.

    Returns DataFrame with columns: month, total_income
    """
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            strftime('%Y-%m', t.date)  AS month,
            SUM(t.amount)              AS total_income
        FROM t
        WHERE strftime('%Y-%m', t.date) BETWEEN ? AND ?
          AND t.amount > 0
          AND {_EXCLUDE_SQL_NO_INCOME}
        GROUP BY month
        ORDER BY month
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_month, end_month))
    finally:
        conn.close()


def get_income_total(entity: str, month: str) -> float:
    """Return total income for a given month (YYYY-MM)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT COALESCE(SUM(t.amount), 0)
        FROM t
        WHERE strftime('%Y-%m', t.date) = ?
          AND t.amount > 0
          AND {_EXCLUDE_SQL_NO_INCOME}
    """
    conn = get_connection(entity)
    try:
        return conn.execute(sql, (month,)).fetchone()[0]
    finally:
        conn.close()


def get_merchant_totals(entity: str, month: str) -> pd.DataFrame:
    """Return per-merchant spend totals for a given month (YYYY-MM).

    Returns DataFrame with columns: merchant, count, total_amount (positive spend)
    """
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            COALESCE(NULLIF(t.merchant_canonical,''), t.description_raw) AS merchant,
            COUNT(*)                                                      AS count,
            ABS(SUM(t.amount))                                           AS total_amount
        FROM t
        WHERE strftime('%Y-%m', t.date) = ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY merchant
        ORDER BY total_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(month,))
    finally:
        conn.close()


def get_available_months(entity: str) -> list[str]:
    """Return sorted list of 'YYYY-MM' strings that have transactions."""
    sql = "SELECT DISTINCT strftime('%Y-%m', date) AS m FROM transactions ORDER BY m"
    conn = get_connection(entity)
    try:
        rows = conn.execute(sql).fetchall()
        return [r[0] for r in rows if r[0]]
    finally:
        conn.close()


# ── Date-range query helpers (for Report Builder) ────────────────────────────

def get_transactions_daterange(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Return all transactions between start_date and end_date (YYYY-MM-DD)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT t.date, t.description_raw, t.merchant_canonical,
               t.amount, t.category, t.subcategory, t.account, t.notes
        FROM t
        WHERE t.date BETWEEN ? AND ?
        ORDER BY t.date DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_category_totals_daterange(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Category summary for a date range (YYYY-MM-DD)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            COALESCE(NULLIF(t.category,''), 'Uncategorized') AS category,
            COUNT(*) AS count,
            ABS(SUM(t.amount)) AS total_amount
        FROM t
        WHERE t.date BETWEEN ? AND ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY category
        ORDER BY total_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_merchant_totals_daterange(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Merchant summary for a date range (YYYY-MM-DD)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            COALESCE(NULLIF(t.merchant_canonical,''), t.description_raw) AS merchant,
            COUNT(*) AS count,
            ABS(SUM(t.amount)) AS total_amount
        FROM t
        WHERE t.date BETWEEN ? AND ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY merchant
        ORDER BY total_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_month_over_month(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Category spend per month for a date range (pivot-ready)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            strftime('%Y-%m', t.date) AS month,
            COALESCE(NULLIF(t.category,''), 'Uncategorized') AS category,
            ABS(SUM(t.amount)) AS total_amount
        FROM t
        WHERE t.date BETWEEN ? AND ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY month, category
        ORDER BY month, total_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_income_vs_expenses_daterange(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Monthly income and expenses for a date range (YYYY-MM-DD)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            strftime('%Y-%m', t.date) AS month,
            ABS(SUM(CASE WHEN t.amount < 0
                         AND {_EXCLUDE_SQL}
                         THEN t.amount ELSE 0 END)) AS expenses,
            SUM(CASE WHEN t.amount > 0
                     AND {_EXCLUDE_SQL_NO_INCOME}
                     THEN t.amount ELSE 0 END) AS income
        FROM t
        WHERE t.date BETWEEN ? AND ?
        GROUP BY month
        ORDER BY month
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_recurring_charges(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Detect recurring merchants in date range (>= 2 charges).

    NOTE: Uses raw transactions table (not CTE) — recurring detection should
    operate on bank-level charges, not split budget allocations.
    """
    sql = """
        SELECT
            COALESCE(NULLIF(merchant_canonical,''), description_raw) AS merchant,
            COUNT(*) AS count,
            ABS(AVG(amount)) AS avg_amount,
            ABS(MIN(amount)) AS min_amount,
            ABS(MAX(amount)) AS max_amount,
            MIN(date) AS first_date,
            MAX(date) AS last_date,
            COALESCE(category, '') AS category
        FROM transactions
        WHERE date BETWEEN ? AND ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
        GROUP BY merchant
        HAVING COUNT(*) >= 2
        ORDER BY count DESC, avg_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_tax_summary(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Category + subcategory breakdown for tax prep (date range YYYY-MM-DD)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            COALESCE(NULLIF(t.category,''), 'Uncategorized') AS category,
            COALESCE(NULLIF(t.subcategory,''), 'Unknown') AS subcategory,
            COUNT(*) AS count,
            ABS(SUM(t.amount)) AS total_amount
        FROM t
        WHERE t.date BETWEEN ? AND ?
          AND t.amount < 0
          AND {_EXCLUDE_SQL}
        GROUP BY category, subcategory
        ORDER BY category, total_amount DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_account_summary(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Spending and income by account for a date range (YYYY-MM-DD)."""
    cte = effective_txns_cte("t")
    sql = f"""
        WITH {cte}
        SELECT
            COALESCE(t.account, 'Unknown') AS account,
            COUNT(*) AS transactions,
            ABS(SUM(CASE WHEN t.amount < 0 THEN t.amount ELSE 0 END)) AS total_spending,
            SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) AS total_income,
            SUM(t.amount) AS net
        FROM t
        WHERE t.date BETWEEN ? AND ?
          AND {_EXCLUDE_SQL_NO_INCOME}
        GROUP BY account
        ORDER BY total_spending DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()

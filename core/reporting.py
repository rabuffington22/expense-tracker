"""Query helpers for the Reports page."""

from typing import Optional

import pandas as pd

from core.db import get_connection


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
    sql = """
        SELECT
            strftime('%Y-%m', date)                        AS month,
            COALESCE(NULLIF(category,''), 'Uncategorized') AS category,
            ABS(SUM(amount))                               AS total_amount
        FROM transactions
        WHERE strftime('%Y-%m', date) BETWEEN ? AND ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income')
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
    sql = """
        SELECT
            COALESCE(NULLIF(category,''), 'Uncategorized') AS category,
            COUNT(*)                                        AS count,
            ABS(SUM(amount))                               AS total_amount
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income')
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
    conditions: list[str] = []
    params: list = []

    if month:
        conditions.append("strftime('%Y-%m', date) = ?")
        params.append(month)

    if category is not None:
        if category == "Uncategorized":
            conditions.append("(category IS NULL OR category = '')")
        else:
            conditions.append("category = ?")
            params.append(category)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT transaction_id, date, description_raw, merchant_canonical,
               amount, currency, account, category, confidence, notes, source_filename
        FROM transactions
        {where}
        ORDER BY date DESC
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
    sql = """
        SELECT transaction_id, date, description_raw, merchant_raw,
               merchant_canonical, amount, category, subcategory, confidence, notes
        FROM transactions
        WHERE category IS NULL OR category = '' OR confidence < 0.6
        ORDER BY date DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn)
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

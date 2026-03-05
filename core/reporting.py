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
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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


def get_monthly_income(entity: str, start_month: str, end_month: str) -> pd.DataFrame:
    """
    Return total income per month for a date range.

    Returns DataFrame with columns: month, total_income
    """
    sql = """
        SELECT
            strftime('%Y-%m', date)  AS month,
            SUM(amount)              AS total_income
        FROM transactions
        WHERE strftime('%Y-%m', date) BETWEEN ? AND ?
          AND amount > 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
          AND amount > 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT
            COALESCE(NULLIF(merchant_canonical,''), description_raw) AS merchant,
            COUNT(*)                                                 AS count,
            ABS(SUM(amount))                                        AS total_amount
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT date, description_raw, merchant_canonical,
               amount, category, subcategory, account, notes
        FROM transactions
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_category_totals_daterange(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Category summary for a date range (YYYY-MM-DD)."""
    sql = """
        SELECT
            COALESCE(NULLIF(category,''), 'Uncategorized') AS category,
            COUNT(*) AS count,
            ABS(SUM(amount)) AS total_amount
        FROM transactions
        WHERE date BETWEEN ? AND ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT
            COALESCE(NULLIF(merchant_canonical,''), description_raw) AS merchant,
            COUNT(*) AS count,
            ABS(SUM(amount)) AS total_amount
        FROM transactions
        WHERE date BETWEEN ? AND ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT
            strftime('%Y-%m', date) AS month,
            COALESCE(NULLIF(category,''), 'Uncategorized') AS category,
            ABS(SUM(amount)) AS total_amount
        FROM transactions
        WHERE date BETWEEN ? AND ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT
            strftime('%Y-%m', date) AS month,
            ABS(SUM(CASE WHEN amount < 0
                         AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Income','Owner Contribution','Partner Buyout')
                         THEN amount ELSE 0 END)) AS expenses,
            SUM(CASE WHEN amount > 0
                     AND COALESCE(category,'') NOT IN ('Internal Transfer','Credit Card Payment','Owner Contribution','Partner Buyout')
                     THEN amount ELSE 0 END) AS income
        FROM transactions
        WHERE date BETWEEN ? AND ?
        GROUP BY month
        ORDER BY month
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()


def get_recurring_charges(entity: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Detect recurring merchants in date range (>= 2 charges)."""
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
    sql = """
        SELECT
            COALESCE(NULLIF(category,''), 'Uncategorized') AS category,
            COALESCE(NULLIF(subcategory,''), 'Unknown') AS subcategory,
            COUNT(*) AS count,
            ABS(SUM(amount)) AS total_amount
        FROM transactions
        WHERE date BETWEEN ? AND ?
          AND amount < 0
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Income', 'Owner Contribution', 'Partner Buyout')
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
    sql = """
        SELECT
            COALESCE(account, 'Unknown') AS account,
            COUNT(*) AS transactions,
            ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS total_spending,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income,
            SUM(amount) AS net
        FROM transactions
        WHERE date BETWEEN ? AND ?
          AND COALESCE(category,'') NOT IN ('Internal Transfer', 'Credit Card Payment', 'Owner Contribution', 'Partner Buyout')
        GROUP BY account
        ORDER BY total_spending DESC
    """
    conn = get_connection(entity)
    try:
        return pd.read_sql_query(sql, conn, params=(start_date, end_date))
    finally:
        conn.close()

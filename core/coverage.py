"""Allocation coverage helpers for vendor transactions.

Phase 1: reads from amazon_orders (shared by Amazon + Henry Schein).
When an allocations table exists later, only this file changes.
"""


def get_vendor_coverage(conn, transaction_id):
    """Coverage % for a single transaction. Returns 0–100 int."""
    row = conn.execute(
        """
        SELECT t.amount_cents,
               COALESCE(SUM(ABS(ao.order_total_cents)), 0) AS covered
        FROM transactions t
        LEFT JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id
        WHERE t.transaction_id = ?
        """,
        (transaction_id,),
    ).fetchone()
    if not row or not row["amount_cents"]:
        return 0
    return min(100, round(row["covered"] / abs(row["amount_cents"]) * 100))


def get_vendor_coverage_bulk(conn):
    """Coverage for all vendor-matched transactions.

    Returns {transaction_id: coverage_pct} where coverage_pct is 0–100 int.
    """
    rows = conn.execute(
        """
        SELECT t.transaction_id, t.amount_cents,
               COALESCE(SUM(ABS(ao.order_total_cents)), 0) AS covered
        FROM transactions t
        INNER JOIN amazon_orders ao ON ao.matched_transaction_id = t.transaction_id
        GROUP BY t.transaction_id
        """
    ).fetchall()
    return {
        r["transaction_id"]: min(100, round(r["covered"] / abs(r["amount_cents"]) * 100))
        for r in rows
        if r["amount_cents"]
    }

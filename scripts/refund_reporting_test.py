"""Synthetic signed-income regression checks; never uses real data."""
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def run_refund_reporting_checks():
    from core.db import init_db, get_connection
    from core.reporting import (
        get_account_summary, get_income_vs_expenses_daterange,
        get_monthly_income, get_income_total,
    )

    with tempfile.TemporaryDirectory(prefix="ledger_refund_") as directory:
        with patch.dict(os.environ, {"DATA_DIR": directory}):
            for entity in ("company", "personal", "luxelegacy"):
                init_db(entity)
                conn = get_connection(entity)
                fixtures = [
                    ("receipt", "2035-01-02", 100000, "Income"),
                    ("refund", "2035-01-03", -10000, "Income"),
                    ("expense", "2035-01-04", -20000, "Office Supplies"),
                    ("vendor-credit", "2035-01-05", 1000, "Office Supplies"),
                    ("transfer-in", "2035-01-06", 100000, "Internal Transfer"),
                    ("transfer-out", "2035-01-06", -100000, "Internal Transfer"),
                    ("split", "2035-01-07", -5000, "Needs Review"),
                    ("refund-only", "2035-02-01", -2500, "Income"),
                ]
                for tid, date, cents, category in fixtures:
                    conn.execute(
                        "INSERT INTO transactions (transaction_id,date,description_raw,"
                        "amount,amount_cents,category,account,imported_at) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        (tid,date,"Synthetic",cents/100,cents,category,"Synthetic",date),
                    )
                for cents, category in ((-2000,"Income"),(-3000,"Office Supplies")):
                    conn.execute(
                        "INSERT INTO transaction_splits "
                        "(transaction_id,amount_cents,category,subcategory) VALUES (?,?,?,?)",
                        ("split",cents,category,"General"),
                    )
                conn.commit()
                before = list(conn.execute("SELECT * FROM transactions"))
                monthly = get_income_vs_expenses_daterange(entity,"2035-01-01","2035-02-28")
                assert [round(x*100) for x in monthly.income] == [89000,-2500]
                assert [round(x*100) for x in monthly.expenses] == [23000,0]
                accounts = get_account_summary(entity,"2035-01-01","2035-02-28")
                assert round(accounts.total_income.sum()*100) == 86500
                assert round(accounts.total_spending.sum()*100) == 23000
                assert round(accounts.net.sum()*100) == 63500
                assert round((monthly.income.sum()-monthly.expenses.sum())*100) == 63500
                income = get_monthly_income(entity,"2035-01","2035-02")
                assert [round(x*100) for x in income.total_income] == [89000,-2500]
                assert round(get_income_total(entity,"2035-02")*100) == -2500
                assert get_account_summary(entity,"2036-01-01","2036-01-31").empty
                assert list(conn.execute("SELECT * FROM transactions")) == before
                conn.close()
    print("Patient-refund reporting: all entities, splits, transfer exclusions, refund-only months, and unchanged data passed")


if __name__ == "__main__":
    run_refund_reporting_checks()

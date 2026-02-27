#!/usr/bin/env python3
"""
Smoke test — runs without a live Streamlit server.

Creates a temp DATA_DIR, initializes both entity DBs, imports the sample
fixture CSV, and verifies deduplication logic.

Usage:
    python scripts/smoke_test.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure project root is importable regardless of cwd
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FIXTURES_DIR = PROJECT_ROOT / "fixtures"
SAMPLE_CSV   = FIXTURES_DIR / "sample.csv"


def _check(condition: bool, msg: str) -> None:
    if not condition:
        print(f"  ❌ FAIL: {msg}")
        sys.exit(1)


def main() -> None:
    print("=" * 60)
    print("  Expense Tracker — Smoke Test")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="expense_smoke_") as tmpdir:
        # Set DATA_DIR BEFORE importing core so get_data_dir() picks it up
        os.environ["DATA_DIR"] = tmpdir
        print(f"\nDATA_DIR = {tmpdir}\n")

        # Late imports so DATA_DIR env var is already set
        from core.db import init_db, get_connection
        from core.imports import parse_csv, normalize_transactions, commit_transactions

        # ── 1. Initialize DBs ──────────────────────────────────────────────
        print("1. Initialising databases…")
        init_db("personal")
        init_db("company")
        init_db("luxelegacy")

        personal_db   = Path(tmpdir) / "personal.sqlite"
        company_db    = Path(tmpdir) / "company.sqlite"
        luxelegacy_db = Path(tmpdir) / "luxelegacy.sqlite"
        _check(personal_db.exists(),   f"personal.sqlite not created at {personal_db}")
        _check(company_db.exists(),    f"company.sqlite not created at {company_db}")
        _check(luxelegacy_db.exists(), f"luxelegacy.sqlite not created at {luxelegacy_db}")
        print(f"   ✅ personal.sqlite, company.sqlite, and luxelegacy.sqlite created")

        # Verify default categories were seeded
        conn = get_connection("personal")
        cat_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        conn.close()
        _check(cat_count > 0, "No default categories seeded")
        print(f"   ✅ {cat_count} default categories seeded")

        # ── 2. Parse fixture CSV ───────────────────────────────────────────
        print("\n2. Parsing fixture CSV…")
        _check(SAMPLE_CSV.exists(), f"Fixture not found: {SAMPLE_CSV}")

        raw_df = parse_csv(str(SAMPLE_CSV))
        _check(len(raw_df) > 0,               "parse_csv returned 0 rows")
        _check("date"            in raw_df.columns, "Missing 'date' column")
        _check("description_raw" in raw_df.columns, "Missing 'description_raw' column")
        _check("amount"          in raw_df.columns, "Missing 'amount' column")
        print(f"   ✅ {len(raw_df)} rows, columns: {list(raw_df.columns)}")

        # ── 3. Normalize ───────────────────────────────────────────────────
        print("\n3. Normalizing transactions…")
        norm_df = normalize_transactions(raw_df, source_filename=SAMPLE_CSV.name)
        _check(len(norm_df) > 0, "normalize_transactions returned 0 rows")
        required = {"transaction_id", "date", "description_raw", "amount", "imported_at"}
        missing  = required - set(norm_df.columns)
        _check(not missing, f"Missing canonical columns: {missing}")
        # All dates should parse to YYYY-MM-DD
        _check(
            norm_df["date"].str.match(r"\d{4}-\d{2}-\d{2}").all(),
            "Some dates did not parse to YYYY-MM-DD",
        )
        print(f"   ✅ {len(norm_df)} transactions normalized")

        # ── 4. First import ────────────────────────────────────────────────
        print("\n4. First import (expect all new)…")
        inserted, skipped = commit_transactions(norm_df, "personal")
        _check(inserted > 0, f"Expected inserted > 0, got {inserted}")
        _check(skipped  == 0, f"Expected skipped == 0 on first import, got {skipped}")
        print(f"   ✅ {inserted} inserted, {skipped} skipped")

        # ── 5. Verify DB row count ─────────────────────────────────────────
        print("\n5. Verifying DB row count…")
        conn  = get_connection("personal")
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        conn.close()
        _check(count == inserted, f"DB has {count} rows but expected {inserted}")
        print(f"   ✅ {count} rows confirmed in transactions table")

        # ── 6. Re-import (deduplication) ───────────────────────────────────
        print("\n6. Re-import same CSV (expect all duplicates)…")
        inserted2, skipped2 = commit_transactions(norm_df, "personal")
        _check(inserted2 == 0,       f"Expected 0 new on re-import, got {inserted2}")
        _check(skipped2  == inserted, f"Expected {inserted} skipped, got {skipped2}")
        print(f"   ✅ {inserted2} inserted, {skipped2} skipped (all duplicates detected)")

        # ── 7. Entity isolation ────────────────────────────────────────────
        print("\n7. Verifying entity isolation…")
        conn2   = get_connection("company")
        count2  = conn2.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        conn2.close()
        _check(count2 == 0, f"company.sqlite should be empty, has {count2} rows")
        conn3   = get_connection("luxelegacy")
        count3  = conn3.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        conn3.close()
        _check(count3 == 0, f"luxelegacy.sqlite should be empty, has {count3} rows")
        print(f"   ✅ company.sqlite and luxelegacy.sqlite isolated (0 rows)")

        # ── 8. Route regression tests ────────────────────────────────
        print("\n8. Route regression tests…")
        from web import create_app
        app = create_app()
        app.config["TESTING"] = True

        with app.test_client() as client:
            client.set_cookie("entity", "Personal")

            def _get_ok(path, label):
                resp = client.get(path)
                _check(resp.status_code == 200, f"{label}: expected 200, got {resp.status_code}")

            def _get_ok_contains(path, label, needle):
                resp = client.get(path)
                _check(resp.status_code == 200, f"{label}: expected 200, got {resp.status_code}")
                body = resp.get_data(as_text=True)
                _check(needle in body, f"{label}: missing '{needle}'")

            # vendor_breakdown with date range (was 500 before fix 2b85b9d)
            # Assert content to catch "200 but wrong page" regressions
            _get_ok_contains(
                "/transactions/?vendor_breakdown=1&start=2024-01-01&end=2024-01-31",
                "vendor_breakdown + dates",
                'id="txn-results"',
            )

            # vendor_breakdown without date range (baseline)
            _get_ok(
                "/transactions/?vendor_breakdown=1",
                "vendor_breakdown bare",
            )

            # vendor_breakdown with dates + search (maximizes bind params)
            _get_ok(
                "/transactions/?vendor_breakdown=1&start=2024-01-01&end=2024-01-31&q=amazon",
                "vendor_breakdown + dates + search",
            )

            # vendor_breakdown with dates + merchant (another bind param combo)
            _get_ok(
                "/transactions/?vendor_breakdown=1&start=2024-01-01&end=2024-01-31&merchant=amazon",
                "vendor_breakdown + dates + merchant",
            )

            # Dashboard loads
            _get_ok("/", "dashboard")

            # Dashboard partial (HTMX)
            _get_ok(
                "/dashboard/partial?start=2024-01-01&end=2024-01-31",
                "dashboard partial",
            )

            # Transactions with various filters
            _get_ok(
                "/transactions/?start=2024-01-01&end=2024-01-31&type=expense",
                "transactions expense filter",
            )
            _get_ok(
                "/transactions/?uncategorized=1",
                "transactions uncategorized",
            )
            _get_ok(
                "/transactions/?possible_transfer=1&start=2024-01-01&end=2024-01-31",
                "transactions possible_transfer + dates",
            )

        print("   ✅ All route regression tests passed")

    print("\n" + "=" * 60)
    print("  🎉  All smoke tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

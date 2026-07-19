#!/usr/bin/env python3
"""
Smoke test — runs without a live Streamlit server.

Creates a temp DATA_DIR, initializes both entity DBs, imports the sample
fixture CSV, and verifies deduplication logic.

Usage:
    python scripts/smoke_test.py
"""

import io
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

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
    print("  The Ledger — Smoke Test")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="expense_smoke_") as tmpdir:
        # Set DATA_DIR BEFORE importing core so get_data_dir() picks it up
        os.environ["DATA_DIR"] = tmpdir
        print(f"\nDATA_DIR = {tmpdir}\n")

        # Late imports so DATA_DIR env var is already set
        from core.db import init_db, get_connection
        from core.imports import (
            commit_transactions,
            compute_external_transaction_id,
            compute_transaction_id,
            normalize_transactions,
            parse_csv,
        )

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

        # ── 7b. Source-aware transaction identity ────────────────────────
        print("\n7b. Source-aware transaction identity tests…")
        import pandas as pd
        import socket

        identity_raw = pd.DataFrame(
            [
                {
                    "date": "2026-07-01",
                    "description_raw": "IDENTICAL DEBIT",
                    "amount": "-12.34",
                    "account": "Checking",
                },
                {
                    "date": "2026-07-01",
                    "description_raw": "IDENTICAL DEBIT",
                    "amount": "-12.34",
                    "account": "Checking",
                },
            ]
        )
        source_a = normalize_transactions(identity_raw, source_filename="source-a.csv")
        source_a_again = normalize_transactions(identity_raw, source_filename="source-a.csv")
        source_b = normalize_transactions(identity_raw, source_filename="source-b.csv")
        account_b_raw = identity_raw.copy()
        account_b_raw["account"] = "Savings"
        account_b = normalize_transactions(account_b_raw, source_filename="source-a.csv")

        _check(source_a["transaction_id"].nunique() == 2,
               "identity: legitimate same-source duplicates should have distinct IDs")
        _check(source_a["transaction_id"].tolist() == source_a_again["transaction_id"].tolist(),
               "identity: exact payload redelivery should be deterministic")
        _check(set(source_a["transaction_id"]).isdisjoint(source_b["transaction_id"]),
               "identity: distinct sources should not collide")
        _check(set(source_a["transaction_id"]).isdisjoint(account_b["transaction_id"]),
               "identity: distinct accounts should not collide")

        try:
            normalize_transactions(identity_raw)
            _check(False, "identity: empty file source should be rejected")
        except ValueError:
            pass

        plaid_id = compute_external_transaction_id("plaid", "plaid-identity-001")
        _check(plaid_id == compute_external_transaction_id("plaid", "plaid-identity-001"),
               "identity: authoritative external IDs should be deterministic")
        _check(plaid_id != compute_transaction_id("2026-07-01", -12.34, "IDENTICAL DEBIT"),
               "identity: Plaid IDs should not reuse the legacy natural-key namespace")
        for invalid_external_id in (None, "", "   "):
            try:
                compute_external_transaction_id("plaid", invalid_external_id)
                _check(False, "identity: empty authoritative external ID should be rejected")
            except ValueError:
                pass

        # Prove the same duplicate/redelivery contract in every isolated DB.
        for identity_entity in ("personal", "company", "luxelegacy"):
            entity_source = f"identity-{identity_entity}.csv"
            entity_df = normalize_transactions(identity_raw, source_filename=entity_source)
            first_inserted, first_skipped = commit_transactions(entity_df, identity_entity)
            redelivery_df = normalize_transactions(identity_raw, source_filename=entity_source)
            second_inserted, second_skipped = commit_transactions(redelivery_df, identity_entity)
            _check((first_inserted, first_skipped) == (2, 0),
                   f"identity {identity_entity}: expected both identical occurrences to insert")
            _check((second_inserted, second_skipped) == (0, 2),
                   f"identity {identity_entity}: exact redelivery should fully skip")
            conn_identity = get_connection(identity_entity)
            placeholders = ",".join("?" for _ in entity_df["transaction_id"])
            identity_count = conn_identity.execute(
                f"SELECT COUNT(*) FROM transactions WHERE transaction_id IN ({placeholders})",
                entity_df["transaction_id"].tolist(),
            ).fetchone()[0]
            _check(identity_count == 2,
                   f"identity {identity_entity}: expected two persisted duplicate occurrences")
            conn_identity.execute(
                f"DELETE FROM transactions WHERE transaction_id IN ({placeholders})",
                entity_df["transaction_id"].tolist(),
            )
            conn_identity.commit()
            conn_identity.close()

        # Populate legacy references, re-enter initialization, and then append
        # new file/Plaid identities without rewriting the legacy key.
        legacy_id = compute_transaction_id("2026-06-30", -45.67, "LEGACY EDITED DEBIT")
        conn_identity = get_connection("personal")
        alias_count_before = conn_identity.execute(
            "SELECT COUNT(*) FROM merchant_aliases"
        ).fetchone()[0]
        conn_identity.execute(
            "INSERT INTO transactions "
            "(transaction_id, date, description_raw, merchant_canonical, amount, amount_cents, "
            "currency, account, category, notes, source_filename, imported_at) "
            "VALUES (?, '2026-06-30', 'LEGACY EDITED DEBIT', 'Edited Merchant', -45.67, -4567, "
            "'USD', 'Checking', 'Food', 'edited note', 'legacy.csv', '2026-07-01T00:00:00+00:00')",
            (legacy_id,),
        )
        conn_identity.execute(
            "INSERT INTO transaction_splits "
            "(transaction_id, description, amount_cents, category, subcategory, sort_order) "
            "VALUES (?, 'first piece', -3000, 'Food', 'General', 0), "
            "(?, 'second piece', -1567, 'Household', 'General', 1)",
            (legacy_id, legacy_id),
        )
        conn_identity.execute(
            "INSERT INTO amazon_orders "
            "(order_id, order_date, product_summary, order_total, order_total_cents, "
            "matched_transaction_id, imported_at) "
            "VALUES ('identity-order', '2026-06-30', 'synthetic item', 45.67, 4567, ?, "
            "'2026-07-01T00:00:00+00:00')",
            (legacy_id,),
        )
        conn_identity.commit()
        conn_identity.close()

        init_db("personal")
        conn_identity = get_connection("personal")
        preserved = conn_identity.execute(
            "SELECT transaction_id, amount_cents, merchant_canonical, category, notes "
            "FROM transactions WHERE transaction_id=?",
            (legacy_id,),
        ).fetchone()
        _check(preserved is not None and preserved["transaction_id"] == legacy_id,
               "identity upgrade: legacy primary key should be preserved")
        _check((preserved["amount_cents"], preserved["merchant_canonical"],
                preserved["category"], preserved["notes"])
               == (-4567, "Edited Merchant", "Food", "edited note"),
               "identity upgrade: signed debit and edits should be preserved")
        split_summary = conn_identity.execute(
            "SELECT COUNT(*), SUM(amount_cents) FROM transaction_splits WHERE transaction_id=?",
            (legacy_id,),
        ).fetchone()
        _check(tuple(split_summary) == (2, -4567),
               "identity upgrade: split references and signed total should be preserved")
        matched_id = conn_identity.execute(
            "SELECT matched_transaction_id FROM amazon_orders WHERE order_id='identity-order'"
        ).fetchone()[0]
        _check(matched_id == legacy_id,
               "identity upgrade: order match reference should be preserved")
        alias_count_after = conn_identity.execute(
            "SELECT COUNT(*) FROM merchant_aliases"
        ).fetchone()[0]
        _check(alias_count_after == alias_count_before,
               "identity upgrade: alias rows should be preserved")
        from core.reporting import effective_txns_cte
        effective_rows = conn_identity.execute(
            f"WITH {effective_txns_cte('eff')} "
            "SELECT transaction_id, amount_cents, is_split_piece FROM eff "
            "WHERE transaction_id=? ORDER BY split_id",
            (legacy_id,),
        ).fetchall()
        _check(len(effective_rows) == 2
               and sum(row["amount_cents"] for row in effective_rows) == -4567
               and all(row["is_split_piece"] == 1 for row in effective_rows),
               "identity upgrade: effective reporting should retain split replacement")
        conn_identity.close()

        same_natural_raw = pd.DataFrame([{
            "date": "2026-06-30",
            "description_raw": "LEGACY EDITED DEBIT",
            "amount": "-45.67",
            "account": "Checking",
        }])
        same_natural_df = normalize_transactions(
            same_natural_raw, source_filename="new-source.csv"
        )
        _check(same_natural_df.iloc[0]["transaction_id"] != legacy_id,
               "identity upgrade: new file identity should not alias a legacy natural key")
        appended, append_skipped = commit_transactions(same_natural_df, "personal")
        _check((appended, append_skipped) == (1, 0),
               "identity upgrade: source-distinct new row should coexist with legacy row")

        # Exercise the primary Plaid insert seam with sockets denied.  This is
        # identity-call-site coverage only; no Plaid client is invoked.
        from web.routes.plaid import _upsert_plaid_transaction
        conn_identity = get_connection("personal")
        conn_identity.execute(
            "INSERT INTO plaid_items (item_id, access_token, institution_name, created_at) "
            "VALUES ('identity-item', 'synthetic-token', 'Synthetic Bank', "
            "'2026-07-01T00:00:00+00:00')"
        )
        conn_identity.execute(
            "INSERT INTO plaid_accounts (item_id, account_id, name) "
            "VALUES ('identity-item', 'identity-account', 'Checking')"
        )
        conn_identity.commit()
        plaid_txn = {
            "plaid_transaction_id": "plaid-identity-001",
            "account_id": "identity-account",
            "date": "2026-06-30",
            "amount": 45.67,
            "name": "LEGACY EDITED DEBIT",
        }
        bound_legacy_id = compute_transaction_id(
            "2026-06-29", -10.00, "BOUND LEGACY PLAID"
        )
        conn_identity.execute(
            "INSERT INTO transactions "
            "(transaction_id, date, description_raw, amount, amount_cents, account, "
            "source_filename, imported_at, plaid_item_id, plaid_transaction_id) "
            "VALUES (?, '2026-06-29', 'BOUND LEGACY PLAID', -10.00, -1000, 'Checking', "
            "'plaid-sync', '2026-06-29T00:00:00+00:00', 'identity-item', "
            "'plaid-bound-legacy')",
            (bound_legacy_id,),
        )
        conn_identity.commit()
        bound_plaid_txn = {
            "plaid_transaction_id": "plaid-bound-legacy",
            "account_id": "identity-account",
            "date": "2026-06-29",
            "amount": 10.00,
            "name": "BOUND LEGACY PLAID",
        }
        original_socket = socket.socket
        socket.socket = lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("identity smoke forbids outbound networking")
        )
        try:
            plaid_inserted = _upsert_plaid_transaction(
                conn_identity, "personal", "identity-item", plaid_txn
            )
            conn_identity.commit()
            plaid_repeated = _upsert_plaid_transaction(
                conn_identity, "personal", "identity-item", plaid_txn
            )
            conn_identity.commit()
            bound_repeated = _upsert_plaid_transaction(
                conn_identity, "personal", "identity-item", bound_plaid_txn
            )
            conn_identity.commit()
            invalid_plaid_txn = dict(plaid_txn, plaid_transaction_id="")
            try:
                _upsert_plaid_transaction(
                    conn_identity, "personal", "identity-item", invalid_plaid_txn
                )
                _check(False, "Plaid identity call site should reject an empty external ID")
            except ValueError:
                pass
        finally:
            socket.socket = original_socket
        _check((plaid_inserted, plaid_repeated) == (1, 0),
               "Plaid identity call site should insert once and redeliver idempotently")
        _check(bound_repeated == 0,
               "Plaid identity call site should reuse a populated legacy binding")
        plaid_row = conn_identity.execute(
            "SELECT transaction_id FROM transactions WHERE plaid_transaction_id=?",
            (plaid_txn["plaid_transaction_id"],),
        ).fetchone()
        _check(plaid_row is not None and plaid_row["transaction_id"] == plaid_id,
               "Plaid identity call site should use the authoritative external-ID hash")
        _check(plaid_row["transaction_id"] not in {legacy_id, same_natural_df.iloc[0]["transaction_id"]},
               "Plaid identity should coexist with matching legacy and file natural fields")
        bound_rows = conn_identity.execute(
            "SELECT transaction_id FROM transactions WHERE plaid_transaction_id='plaid-bound-legacy'"
        ).fetchall()
        _check(len(bound_rows) == 1 and bound_rows[0]["transaction_id"] == bound_legacy_id,
               "Plaid redelivery should preserve the existing bound legacy primary key")

        conn_identity.execute(
            "DELETE FROM transaction_splits WHERE transaction_id=?", (legacy_id,)
        )
        conn_identity.execute(
            "DELETE FROM amazon_orders WHERE order_id='identity-order'"
        )
        conn_identity.execute(
            "DELETE FROM transactions WHERE transaction_id IN (?, ?, ?, ?)",
            (legacy_id, same_natural_df.iloc[0]["transaction_id"], plaid_id,
             bound_legacy_id),
        )
        conn_identity.execute(
            "DELETE FROM plaid_accounts WHERE item_id='identity-item'"
        )
        conn_identity.execute(
            "DELETE FROM plaid_items WHERE item_id='identity-item'"
        )
        conn_identity.commit()
        conn_identity.close()
        print("   ✅ Source/account separation, duplicates, redelivery, Plaid IDs, and populated references passed")

        # ── 8. Route regression tests ────────────────────────────────
        print("\n8. Route regression tests…")
        os.environ["FLASK_SECRET"] = "smoke-test-secret-key"
        os.environ["APP_PASSWORD_HASH"] = ""
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

            # Dashboard with empty entity doesn't crash (insights/upcoming with 0 txns)
            client.set_cookie("entity", "BFM")
            _get_ok("/", "dashboard empty entity")
            client.set_cookie("entity", "Personal")

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

            # include_transfers param accepted without error
            resp = client.get("/?include_transfers=1&start=2024-01-01&end=2024-01-31")
            _check(resp.status_code == 200, "dashboard with include_transfers: expected 200")

            # (Recurring/Upcoming section removed from dashboard in PR #57)

        # Cash Flow page loads (empty state when no Plaid configured)
        _get_ok("/cashflow/", "cashflow")

        # Cash Flow with each entity
        client.set_cookie("entity", "BFM")
        _get_ok("/cashflow/", "cashflow BFM")
        client.set_cookie("entity", "LL")
        _get_ok("/cashflow/", "cashflow LL")
        client.set_cookie("entity", "Personal")

        # Connected Accounts page loads
        _get_ok("/plaid/", "connected accounts")

        print("   ✅ All route regression tests passed")

        # ── 8a. Luxe Legacy planning route boundary ────────────────
        print("\n8a. Luxe Legacy planning route boundary…")

        expected_planning_rules = {
            "/planning/",
            "/planning/settings",
            "/planning/items/add",
            "/planning/items/update/<int:item_id>",
            "/planning/items/delete/<int:item_id>",
            "/planning/cashflow-accounts/<entity_key>",
            "/planning/short-term/",
            "/planning/short-term/goals/create",
            "/planning/short-term/goals/<int:goal_id>/update",
            "/planning/short-term/goals/<int:goal_id>/delete",
            "/planning/short-term/goals/<int:goal_id>/snapshot",
            "/planning/short-term/goals/<int:goal_id>/lock-plan",
            "/planning/short-term/goals/<int:goal_id>/progress",
            "/planning/short-term/budget/save",
            "/planning/short-term/budget/status",
            "/planning/short-term/actions/create",
            "/planning/short-term/actions/<int:item_id>/toggle",
            "/planning/short-term/actions/<int:item_id>/delete",
            "/planning/short-term/budget/transactions",
            "/planning/short-term/budget/update-txn/<txn_id>",
            "/planning/short-term/budget/subcategories",
        }
        registered_planning_rules = {
            rule.rule
            for rule in app.url_map.iter_rules()
            if rule.endpoint.startswith(("planning.", "short_term_planning."))
        }
        _check(
            registered_planning_rules == expected_planning_rules,
            "planning boundary coverage must enumerate every registered planning route",
        )

        denied_planning_routes = (
            ("get", "/planning/", {}),
            ("post", "/planning/settings", {
                "data": {"inflation_rate": "9.90", "birth_date": "1977-06-21"},
            }),
            ("post", "/planning/items/add", {
                "data": {"item_type": "asset", "name": "Denied LL Item", "current_value": "999"},
            }),
            ("post", "/planning/items/update/999999", {
                "data": {"name": "Denied LL Update", "current_value": "999"},
            }),
            ("post", "/planning/items/delete/999999", {}),
            ("get", "/planning/cashflow-accounts/personal", {}),
            ("get", "/planning/short-term/", {}),
            ("post", "/planning/short-term/goals/create", {
                "data": {"name": "Denied LL Goal", "goal_type": "savings", "target_amount": "999"},
            }),
            ("post", "/planning/short-term/goals/999999/update", {
                "data": {"name": "Denied LL Goal Update", "target_amount": "999"},
            }),
            ("post", "/planning/short-term/goals/999999/delete", {}),
            ("post", "/planning/short-term/goals/999999/snapshot", {
                "data": {"balance": "999", "note": "denied"},
            }),
            ("post", "/planning/short-term/goals/999999/lock-plan", {}),
            ("get", "/planning/short-term/goals/999999/progress", {}),
            ("post", "/planning/short-term/budget/save", {
                "data": {"budget_Food": "999"},
            }),
            ("get", "/planning/short-term/budget/status?month=2026-07", {}),
            ("post", "/planning/short-term/actions/create", {
                "data": {"title": "Denied LL Action"},
            }),
            ("post", "/planning/short-term/actions/999999/toggle", {}),
            ("post", "/planning/short-term/actions/999999/delete", {}),
            ("get", "/planning/short-term/budget/transactions?category=Food&month=2026-07", {}),
            ("post", "/planning/short-term/budget/update-txn/denied-ll-txn", {
                "data": {"category": "Food", "subcategory": "Groceries"},
            }),
            ("get", "/planning/short-term/budget/subcategories?category=Food&month=2026-07", {}),
        )

        def _database_snapshot(entity_key):
            snapshot_conn = get_connection(entity_key)
            try:
                return tuple(snapshot_conn.iterdump())
            finally:
                snapshot_conn.close()

        with app.test_client() as planning_client:
            # Warm global entity setup before taking the denied-request baseline.
            for entity_display in ("Personal", "BFM", "LL"):
                planning_client.set_cookie("entity", entity_display)
                _check(
                    planning_client.get("/").status_code == 200,
                    f"planning boundary warmup: {entity_display} dashboard should render",
                )

            personal_account = "Personal Planning Boundary Account"
            bfm_account = "BFM Planning Boundary Account"
            personal_item = "Personal-4E-Asset"
            bfm_item = "BFM-4E-Asset"
            for entity_key, account_name, item_name in (
                ("personal", personal_account, personal_item),
                ("company", bfm_account, bfm_item),
            ):
                conn_planning = get_connection(entity_key)
                conn_planning.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type) "
                    "VALUES (?, 12345, 'manual', 'bank')",
                    (account_name,),
                )
                conn_planning.execute(
                    "INSERT INTO planning_items "
                    "(item_type, name, current_value_cents, annual_rate_bps, source, sort_order) "
                    "VALUES ('asset', ?, 12345, 0, 'manual', 999)",
                    (item_name,),
                )
                conn_planning.commit()
                conn_planning.close()

            for entity_display in ("Personal", "BFM"):
                planning_client.set_cookie("entity", entity_display)
                long_term = planning_client.get("/planning/")
                _check(
                    long_term.status_code == 200,
                    f"planning {entity_display}: long-term page should remain available",
                )
                long_term_body = long_term.get_data(as_text=True)
                _check(
                    personal_item in long_term_body and bfm_item in long_term_body,
                    f"planning {entity_display}: long-term Personal/BFM sharing should remain visible",
                )
                _check(
                    planning_client.get("/planning/short-term/").status_code == 200,
                    f"planning {entity_display}: short-term page should remain available",
                )

            planning_client.set_cookie("entity", "Personal")
            personal_accounts = planning_client.get("/planning/cashflow-accounts/personal")
            _check(
                personal_accounts.status_code == 200
                and personal_account in personal_accounts.get_data(as_text=True),
                "planning Personal: account helper should remain available",
            )
            planning_client.set_cookie("entity", "BFM")
            bfm_accounts = planning_client.get("/planning/cashflow-accounts/company")
            _check(
                bfm_accounts.status_code == 200 and bfm_account in bfm_accounts.get_data(as_text=True),
                "planning BFM: account helper should remain available",
            )

            baseline_databases = {
                entity_key: _database_snapshot(entity_key)
                for entity_key in ("personal", "company", "luxelegacy")
            }
            planning_endpoints = {
                rule.endpoint
                for rule in app.url_map.iter_rules()
                if rule.endpoint.startswith(("planning.", "short_term_planning."))
            }

            def _denied_planning_handler(*_args, **_kwargs):
                raise AssertionError("denied planning request reached a route handler")

            planning_client.set_cookie("entity", "LL")
            with patch.dict(
                app.view_functions,
                {endpoint: _denied_planning_handler for endpoint in planning_endpoints},
                clear=False,
            ):
                for method, path, kwargs in denied_planning_routes:
                    resp = getattr(planning_client, method)(path, **kwargs)
                    body = resp.get_data(as_text=True)
                    _check(
                        resp.status_code == 302 and resp.headers.get("Location", "").endswith("/"),
                        f"planning LL {method.upper()} {path}: expected dashboard redirect",
                    )
                    _check(
                        personal_account not in body and bfm_account not in body,
                        f"planning LL {method.upper()} {path}: response revealed another entity's account",
                    )

            final_databases = {
                entity_key: _database_snapshot(entity_key)
                for entity_key in ("personal", "company", "luxelegacy")
            }
            _check(
                final_databases == baseline_databases,
                "planning LL: denied requests changed one or more entity databases",
            )

        print("   ✅ All planning routes deny LL before handlers and preserve Personal/BFM sharing")

        # ── 8a. BFM-only payroll route boundary ─────────────────────
        print("\n8b. BFM-only payroll route boundary…")
        from web.routes import payroll as payroll_routes

        expected_payroll_rules = {
            "/payroll/",
            "/payroll/employees/create",
            "/payroll/employees/update/<int:emp_id>",
            "/payroll/employees/delete/<int:emp_id>",
            "/payroll/employees/detail/<int:emp_id>",
            "/payroll/import/parse",
            "/payroll/import/save",
            "/payroll/spending",
        }
        registered_payroll_rules = {
            rule.rule
            for rule in app.url_map.iter_rules()
            if rule.endpoint.startswith("payroll.")
        }
        _check(
            registered_payroll_rules == expected_payroll_rules,
            "payroll boundary coverage must enumerate every registered payroll route",
        )

        denied_routes = (
            ("get", "/payroll/", {}),
            ("post", "/payroll/employees/create", {
                "data": {
                    "name": "Denied New Employee",
                    "role": "Nurses",
                    "pay_type": "hourly",
                    "pay_rate": "20",
                },
            }),
            ("post", "/payroll/employees/update/{employee_id}", {
                "data": {
                    "name": "Denied Updated Employee",
                    "role": "Providers",
                    "pay_type": "hourly",
                    "pay_rate": "99",
                },
            }),
            ("post", "/payroll/employees/delete/{employee_id}", {}),
            ("get", "/payroll/employees/detail/{employee_id}", {}),
            ("post", "/payroll/import/parse", {
                "content_type": "multipart/form-data",
            }),
            ("post", "/payroll/import/save", {
                "data": {"temp_key": "replaced-per-entity"},
            }),
            ("get", "/payroll/spending?spending_period=2026-07-01", {}),
        )

        with app.test_client() as payroll_client:
            for entity_display, entity_key in (("Personal", "personal"), ("LL", "luxelegacy")):
                conn_payroll = get_connection(entity_key)
                cur = conn_payroll.execute(
                    "INSERT INTO employees (name, role, pay_type, pay_rate_cents) "
                    "VALUES (?, 'Nurses', 'hourly', 2000)",
                    (f"{entity_display} Boundary Sentinel",),
                )
                sentinel_id = cur.lastrowid
                conn_payroll.execute(
                    "INSERT INTO employee_pay_changes "
                    "(employee_id, effective_date, old_rate_cents, new_rate_cents, notes) "
                    "VALUES (?, '2026-07-01', 1800, 2000, 'synthetic boundary baseline')",
                    (sentinel_id,),
                )
                conn_payroll.execute(
                    "INSERT INTO payroll_entries "
                    "(employee_id, paycheck_date, amount_cents, source_filename) "
                    "VALUES (?, '2026-07-01', 12345, 'synthetic-boundary.xlsx')",
                    (sentinel_id,),
                )
                conn_payroll.commit()
                baseline_counts = tuple(
                    conn_payroll.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in ("employees", "employee_pay_changes", "payroll_entries")
                )
                baseline_employee = tuple(conn_payroll.execute(
                    "SELECT name, role, pay_type, pay_rate_cents FROM employees WHERE id = ?",
                    (sentinel_id,),
                ).fetchone())
                conn_payroll.close()

                temp_key = f"payroll_boundary_{entity_key}_{os.getpid()}"
                temp_path = Path(payroll_routes._TEMP_DIR) / f"{temp_key}.json"
                payroll_routes._save_temp(temp_key, {
                    "entries": [],
                    "filename": "synthetic-boundary.xlsx",
                })

                try:
                    payroll_client.set_cookie("entity", entity_display)
                    with patch(
                        "web.routes.payroll.get_connection",
                        side_effect=AssertionError("denied payroll route reached storage"),
                    ), patch(
                        "web.routes.payroll.parse_phoenix_per_payroll_costs",
                        side_effect=AssertionError("denied payroll route parsed an upload"),
                    ):
                        for method, path, kwargs in denied_routes:
                            path = path.format(employee_id=sentinel_id)
                            request_kwargs = dict(kwargs)
                            if path == "/payroll/import/parse":
                                request_kwargs["data"] = {
                                    "payroll_file": (io.BytesIO(b"not parsed"), "denied.xlsx"),
                                }
                            elif path == "/payroll/import/save":
                                request_kwargs = {"data": {"temp_key": temp_key}}
                            resp = getattr(payroll_client, method)(path, **request_kwargs)
                            _check(
                                resp.status_code == 302 and resp.headers.get("Location", "").endswith("/"),
                                f"payroll {entity_display} {method.upper()} {path}: expected dashboard redirect",
                            )

                    conn_payroll = get_connection(entity_key)
                    final_counts = tuple(
                        conn_payroll.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                        for table in ("employees", "employee_pay_changes", "payroll_entries")
                    )
                    final_employee = tuple(conn_payroll.execute(
                        "SELECT name, role, pay_type, pay_rate_cents FROM employees WHERE id = ?",
                        (sentinel_id,),
                    ).fetchone())
                    _check(
                        final_counts == baseline_counts and final_employee == baseline_employee,
                        f"payroll {entity_display}: denied requests changed payroll rows",
                    )
                    _check(temp_path.exists(), f"payroll {entity_display}: denied save consumed temp payload")
                    conn_payroll.execute("DELETE FROM employees WHERE id = ?", (sentinel_id,))
                    conn_payroll.commit()
                    conn_payroll.close()
                finally:
                    temp_path.unlink(missing_ok=True)

            payroll_client.set_cookie("entity", "BFM")
            _check(payroll_client.get("/payroll/").status_code == 200, "payroll BFM: index should render")
            create_resp = payroll_client.post("/payroll/employees/create", data={
                "name": "BFM Boundary Employee",
                "role": "Nurses",
                "pay_type": "hourly",
                "pay_rate": "20",
            })
            _check(create_resp.status_code == 302, "payroll BFM: create should remain available")

            conn_payroll = get_connection("company")
            bfm_employee = conn_payroll.execute(
                "SELECT id FROM employees WHERE name = 'BFM Boundary Employee'"
            ).fetchone()
            _check(bfm_employee is not None, "payroll BFM: create should persist the employee")
            bfm_employee_id = bfm_employee["id"]
            conn_payroll.close()

            _check(
                payroll_client.get(f"/payroll/employees/detail/{bfm_employee_id}").status_code == 200,
                "payroll BFM: employee detail should remain available",
            )
            update_resp = payroll_client.post(
                f"/payroll/employees/update/{bfm_employee_id}",
                data={
                    "name": "BFM Boundary Employee",
                    "role": "Nurses",
                    "pay_type": "hourly",
                    "pay_rate": "21",
                    "status": "active",
                },
            )
            _check(update_resp.status_code == 302, "payroll BFM: update should remain available")
            _check(
                payroll_client.get("/payroll/spending?spending_period=2026-07-01").status_code == 200,
                "payroll BFM: spending partial should remain available",
            )

            with patch(
                "web.routes.payroll.parse_phoenix_per_payroll_costs",
                return_value=([], ["synthetic controlled empty workbook"]),
            ):
                parse_resp = payroll_client.post(
                    "/payroll/import/parse",
                    data={"payroll_file": (io.BytesIO(b"synthetic"), "synthetic.xlsx")},
                    content_type="multipart/form-data",
                )
            _check(parse_resp.status_code == 200, "payroll BFM: import parse should reach its handler")

            bfm_temp_key = f"payroll_boundary_company_{os.getpid()}"
            bfm_temp_path = Path(payroll_routes._TEMP_DIR) / f"{bfm_temp_key}.json"
            payroll_routes._save_temp(bfm_temp_key, {
                "entries": [],
                "filename": "synthetic-boundary.xlsx",
            })
            try:
                save_resp = payroll_client.post(
                    "/payroll/import/save",
                    data={"temp_key": bfm_temp_key},
                )
                _check(save_resp.status_code == 302, "payroll BFM: import save should remain available")
                _check(not bfm_temp_path.exists(), "payroll BFM: import save should consume its temp payload")
            finally:
                bfm_temp_path.unlink(missing_ok=True)

            delete_resp = payroll_client.post(f"/payroll/employees/delete/{bfm_employee_id}")
            _check(delete_resp.status_code == 302, "payroll BFM: delete should remain available")
            conn_payroll = get_connection("company")
            _check(
                conn_payroll.execute(
                    "SELECT COUNT(*) FROM employees WHERE id = ?", (bfm_employee_id,)
                ).fetchone()[0] == 0,
                "payroll BFM: delete should remove the synthetic employee",
            )
            conn_payroll.close()

        print("   ✅ All payroll routes enforce BFM-only access before storage or parsing")

        # ── 8b. CSV export tests ────────────────────────────────────
        print("\n8c. CSV export tests…")
        with app.test_client() as csv_client:
            csv_client.set_cookie("entity", "Personal")

            # Reports page loads
            resp = csv_client.get("/reports/")
            _check(resp.status_code == 200, "reports page: expected 200")
            body = resp.get_data(as_text=True)
            _check("Export" in body, "reports page: missing Export section")

            # Transactions CSV — fixture data is in 2024-01
            resp = csv_client.get("/reports/export-csv?month=2024-01")
            _check(resp.status_code == 200, "transactions CSV: expected 200")
            _check("text/csv" in resp.content_type, "transactions CSV: wrong content-type")
            csv_body = resp.get_data(as_text=True)
            _check("Date,Description,Merchant,Amount,Category,Account" in csv_body,
                   "transactions CSV: missing expected header")
            # Filename check
            disp = resp.headers.get("Content-Disposition", "")
            _check("personal_transactions_2024-01-01_2024-01-31.csv" in disp,
                   f"transactions CSV: unexpected filename in {disp}")

            # Category summary CSV
            resp = csv_client.get("/reports/export-categories?month=2024-01")
            _check(resp.status_code == 200, "categories CSV: expected 200")
            csv_body = resp.get_data(as_text=True)
            _check("Category,Transactions,Total" in csv_body,
                   "categories CSV: missing expected header")
            disp = resp.headers.get("Content-Disposition", "")
            _check("personal_categories_2024-01-01_2024-01-31.csv" in disp,
                   f"categories CSV: unexpected filename in {disp}")

            # Merchant summary CSV
            resp = csv_client.get("/reports/export-merchants?month=2024-01")
            _check(resp.status_code == 200, "merchants CSV: expected 200")
            csv_body = resp.get_data(as_text=True)
            _check("Merchant,Transactions,Total" in csv_body,
                   "merchants CSV: missing expected header")
            disp = resp.headers.get("Content-Disposition", "")
            _check("personal_merchants_2024-01-01_2024-01-31.csv" in disp,
                   f"merchants CSV: unexpected filename in {disp}")

            # Missing month param returns 400
            resp = csv_client.get("/reports/export-csv")
            _check(resp.status_code == 400, "export CSV no month: expected 400")

            # Empty month returns 404
            resp = csv_client.get("/reports/export-csv?month=1999-01")
            _check(resp.status_code == 404, "export CSV empty month: expected 404")

        print("   ✅ All CSV export tests passed")

        # ── 9. Saved Views CRUD ──────────────────────────────────────
        print("\n9. Saved Views CRUD tests…")
        import json as _json

        try:
            # 9a. List — should start empty (JSON array)
            resp = client.get("/saved-views/list?page=dashboard")
            _check(resp.status_code == 200, "saved views list: expected 200")
            views = _json.loads(resp.get_data(as_text=True))
            _check(isinstance(views, list), "saved views list: should return JSON array")
            _check(len(views) == 0, "saved views list: should be empty initially")

            # 9b. Create a view
            resp = client.post("/saved-views/create", data={
                "name": "Test View",
                "page": "dashboard",
                "query_string": "start=2024-01-01&end=2024-01-31&uncategorized=1",
            })
            _check(resp.status_code == 200, "saved views create: expected 200")
            views = _json.loads(resp.get_data(as_text=True))
            names = [v["name"] for v in views]
            _check("Test View" in names, "saved views create: should return view name in JSON")

            # 9c. Get the view ID from the DB, then verify
            conn_sv = get_connection("personal")
            sv_row = conn_sv.execute(
                "SELECT id, query_string FROM saved_views WHERE name = 'Test View'"
            ).fetchone()
            conn_sv.close()
            _check(sv_row is not None, "saved views: row should exist in DB")
            _check(
                sv_row["query_string"] == "start=2024-01-01&end=2024-01-31&uncategorized=1",
                "saved views: query_string should match what was saved",
            )
            view_id = sv_row["id"]

            # 9d. Get endpoint returns correct JSON
            resp = client.get(f"/saved-views/get?id={view_id}")
            _check(resp.status_code == 200, "saved views get: expected 200")
            data = _json.loads(resp.get_data(as_text=True))
            _check(data["page"] == "dashboard", "saved views get: page should be 'dashboard'")
            _check(
                "start=2024-01-01" in data["query_string"],
                "saved views get: query_string should contain start param",
            )

            # 9e. List should now include the view
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            names = [v["name"] for v in views]
            _check("Test View" in names, "saved views list after create: should contain 'Test View'")

            # 9f. Rename the view
            resp = client.post("/saved-views/rename", data={
                "id": str(view_id),
                "name": "Renamed View",
                "page": "dashboard",
            })
            _check(resp.status_code == 200, "saved views rename: expected 200")
            data = _json.loads(resp.get_data(as_text=True))
            _check(data["id"] == view_id, "saved views rename: id should match")
            _check(data["name"] == "Renamed View", "saved views rename: name should be updated")
            _check(data["page"] == "dashboard", "saved views rename: page should match")

            # 9f-ii. List should show renamed view
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            names = [v["name"] for v in views]
            _check("Renamed View" in names, "saved views rename: list should contain renamed name")
            _check("Test View" not in names, "saved views rename: old name should be gone")

            # 9f-iii. Query string unchanged after rename
            resp = client.get(f"/saved-views/get?id={view_id}")
            data = _json.loads(resp.get_data(as_text=True))
            _check(
                data["query_string"] == "start=2024-01-01&end=2024-01-31&uncategorized=1",
                "saved views rename: query_string must be unchanged after rename",
            )

            # 9f-iv. Rename to same name → 400
            resp = client.post("/saved-views/rename", data={
                "id": str(view_id),
                "name": "Renamed View",
                "page": "dashboard",
            })
            _check(resp.status_code == 400, "saved views rename to same name: expected 400")
            data = _json.loads(resp.get_data(as_text=True))
            _check(data["error"] == "name unchanged", "saved views rename same name: error should be 'name unchanged'")

            # 9f-v. Rename with empty name → 400
            resp = client.post("/saved-views/rename", data={
                "id": str(view_id),
                "name": "   ",
                "page": "dashboard",
            })
            _check(resp.status_code == 400, "saved views rename empty name: expected 400")

            # 9f-vi. Rename non-existent view → 404
            resp = client.post("/saved-views/rename", data={
                "id": "99999",
                "name": "Ghost",
                "page": "dashboard",
            })
            _check(resp.status_code == 404, "saved views rename non-existent: expected 404")

            # Rename back so subsequent tests use original name context
            client.post("/saved-views/rename", data={
                "id": str(view_id),
                "name": "Test View",
                "page": "dashboard",
            })

            # 9g. List for transactions should NOT include the dashboard view (page isolation)
            resp = client.get("/saved-views/list?page=transactions")
            views = _json.loads(resp.get_data(as_text=True))
            names = [v["name"] for v in views]
            _check(
                "Test View" not in names,
                "saved views list for transactions: should not contain dashboard view",
            )

            # 9g. Delete the view
            resp = client.post("/saved-views/delete", data={
                "id": str(view_id),
                "page": "dashboard",
            })
            _check(resp.status_code == 200, "saved views delete: expected 200")
            views = _json.loads(resp.get_data(as_text=True))
            names = [v["name"] for v in views]
            _check("Test View" not in names, "saved views delete: view should be gone")

            # 9h. Verify DB is clean
            conn_sv = get_connection("personal")
            count_sv = conn_sv.execute("SELECT COUNT(*) FROM saved_views").fetchone()[0]
            conn_sv.close()
            _check(count_sv == 0, f"saved views: DB should be empty after delete, has {count_sv}")

            # 9i. Validation — bad page value
            resp = client.get("/saved-views/list?page=invalid")
            _check(resp.status_code == 400, "saved views list with bad page: expected 400")

            resp = client.post("/saved-views/create", data={
                "name": "Bad",
                "page": "invalid",
                "query_string": "",
            })
            _check(resp.status_code == 400, "saved views create with bad page: expected 400")

            # 9j. XSS — name with HTML stored verbatim in JSON
            # (Client builds DOM with textContent, so HTML is never parsed)
            resp = client.post("/saved-views/create", data={
                "name": '<script>alert("xss")</script>',
                "page": "transactions",
                "query_string": "",
            })
            _check(resp.status_code == 200, "saved views create with HTML name: expected 200")
            views = _json.loads(resp.get_data(as_text=True))
            _check(
                views[0]["name"] == '<script>alert("xss")</script>',
                "saved views: name stored verbatim in JSON (client uses textContent for safe rendering)",
            )

            # 9k. Cross-entity isolation — create under Personal, then
            # switch to BFM and attempt to access/delete the same view.
            resp = client.post("/saved-views/create", data={
                "name": "Personal Only",
                "page": "dashboard",
                "query_string": "start=2024-01-01&end=2024-01-31",
            })
            _check(resp.status_code == 200, "cross-entity: create under Personal")
            views = _json.loads(resp.get_data(as_text=True))
            personal_view_id = views[-1]["id"]

            # Switch to BFM entity
            client.set_cookie("entity", "BFM")

            # 9k-i. List under BFM should NOT include Personal's view
            resp = client.get("/saved-views/list?page=dashboard")
            _check(resp.status_code == 200, "cross-entity: list under BFM")
            views = _json.loads(resp.get_data(as_text=True))
            bfm_ids = [v["id"] for v in views]
            _check(
                personal_view_id not in bfm_ids,
                "cross-entity: Personal view ID must not appear in BFM list",
            )

            # 9k-ii. GET by ID under BFM should 404
            resp = client.get(f"/saved-views/get?id={personal_view_id}")
            _check(
                resp.status_code == 404,
                f"cross-entity: GET Personal view {personal_view_id} under BFM should 404",
            )

            # 9k-iii. RENAME by ID under BFM should 404 (not found in BFM's DB)
            resp = client.post("/saved-views/rename", data={
                "id": str(personal_view_id),
                "name": "Hijacked",
                "page": "dashboard",
            })
            _check(resp.status_code == 404, "cross-entity: rename Personal view under BFM should 404")

            # 9k-iv. DELETE by ID under BFM should 404 (not found in BFM's DB)
            resp = client.post("/saved-views/delete", data={
                "id": str(personal_view_id),
                "page": "dashboard",
            })
            _check(resp.status_code == 404, "cross-entity: delete Personal view under BFM should 404")

            # Switch back to Personal and confirm the view still exists
            client.set_cookie("entity", "Personal")
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            personal_ids = [v["id"] for v in views]
            _check(
                personal_view_id in personal_ids,
                "cross-entity: Personal view must survive BFM delete attempt",
            )

            # ── 9l. Default Views ────────────────────────────────────
            # Clean slate for default tests
            for ek in ("personal", "company"):
                conn_sv = get_connection(ek)
                conn_sv.execute("DELETE FROM saved_views")
                conn_sv.commit()
                conn_sv.close()
            client.set_cookie("entity", "Personal")

            # 9l. Create two dashboard views (A and B)
            resp = client.post("/saved-views/create", data={
                "name": "View A",
                "page": "dashboard",
                "query_string": "start=2024-06-01&end=2024-06-30",
            })
            _check(resp.status_code == 200, "default: create View A")
            views = _json.loads(resp.get_data(as_text=True))
            view_a_id = [v for v in views if v["name"] == "View A"][0]["id"]

            resp = client.post("/saved-views/create", data={
                "name": "View B",
                "page": "dashboard",
                "query_string": "start=2024-07-01&end=2024-07-31",
            })
            _check(resp.status_code == 200, "default: create View B")
            views = _json.loads(resp.get_data(as_text=True))
            view_b_id = [v for v in views if v["name"] == "View B"][0]["id"]

            # 9l-i. List returns is_default=0 for both initially
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            for v in views:
                _check(v["is_default"] == 0, f"default: {v['name']} should start as non-default")

            # 9l-ii. Set A as default
            resp = client.post("/saved-views/set-default", data={
                "id": str(view_a_id),
                "page": "dashboard",
            })
            _check(resp.status_code == 200, "default: set-default A: expected 200")
            data = _json.loads(resp.get_data(as_text=True))
            _check(data["default_id"] == view_a_id, "default: response should contain A's id")

            # 9l-iii. List shows A is_default=1 and B is_default=0
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            a_row = [v for v in views if v["id"] == view_a_id][0]
            b_row = [v for v in views if v["id"] == view_b_id][0]
            _check(a_row["is_default"] == 1, "default: A should be default after set")
            _check(b_row["is_default"] == 0, "default: B should not be default")

            # 9l-iv. GET / with NO query params → 200 (no saved-view redirect on dashboard)
            resp = client.get("/")
            _check(resp.status_code == 200, "default: GET / with no params should render 200")

            # 9l-v. GET / WITH query params → 200
            resp = client.get("/?start=2025-01-01")
            _check(resp.status_code == 200, "default: GET / with params should render 200")

            # 9m. Switch default to B — A should lose default
            resp = client.post("/saved-views/set-default", data={
                "id": str(view_b_id),
                "page": "dashboard",
            })
            _check(resp.status_code == 200, "default: set-default B: expected 200")
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            a_row = [v for v in views if v["id"] == view_a_id][0]
            b_row = [v for v in views if v["id"] == view_b_id][0]
            _check(a_row["is_default"] == 0, "default: A should lose default after B set")
            _check(b_row["is_default"] == 1, "default: B should now be default")

            # 9n. Set-default with wrong page → 404
            resp = client.post("/saved-views/set-default", data={
                "id": str(view_a_id),
                "page": "transactions",
            })
            _check(resp.status_code == 404, "default: set-default with mismatched page should 404")

            # 9n-i. Set-default with non-existent id → 404
            resp = client.post("/saved-views/set-default", data={
                "id": "99999",
                "page": "dashboard",
            })
            _check(resp.status_code == 404, "default: set-default non-existent id should 404")

            # 9o. Transactions default — create, set default, verify redirect
            resp = client.post("/saved-views/create", data={
                "name": "Txn Default",
                "page": "transactions",
                "query_string": "type=expense&uncategorized=1",
            })
            views = _json.loads(resp.get_data(as_text=True))
            txn_view_id = [v for v in views if v["name"] == "Txn Default"][0]["id"]

            client.post("/saved-views/set-default", data={
                "id": str(txn_view_id),
                "page": "transactions",
            })

            resp = client.get("/transactions/")
            _check(resp.status_code == 302, "default: GET /transactions/ with no params should redirect")
            _check(
                "type=expense" in resp.headers.get("Location", ""),
                "default: transactions redirect should contain querystring",
            )

            resp = client.get("/transactions/?start=2025-01-01")
            _check(resp.status_code == 200, "default: GET /transactions/ with params should not redirect")

            # 9p. Cross-entity — default in Personal should NOT affect BFM
            client.set_cookie("entity", "BFM")
            resp = client.get("/")
            _check(
                resp.status_code == 200,
                "default cross-entity: BFM GET / should not redirect (no BFM default)",
            )
            resp = client.get("/transactions/")
            _check(
                resp.status_code == 200,
                "default cross-entity: BFM GET /transactions/ should not redirect",
            )

            # 9p-i. Set-default cross-entity → 404
            client.set_cookie("entity", "BFM")
            resp = client.post("/saved-views/set-default", data={
                "id": str(view_a_id),
                "page": "dashboard",
            })
            _check(resp.status_code == 404, "default cross-entity: set-default Personal view under BFM should 404")

            client.set_cookie("entity", "Personal")

            # 9q. Clear-default
            resp = client.post("/saved-views/clear-default", data={
                "page": "dashboard",
            })
            _check(resp.status_code == 200, "default: clear-default should return 200")
            data = _json.loads(resp.get_data(as_text=True))
            _check(data["cleared"] is True, "default: clear-default response should have cleared=true")

            # Verify no default after clear
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            for v in views:
                _check(v["is_default"] == 0, f"default: {v['name']} should be non-default after clear")

            # GET / should no longer redirect
            resp = client.get("/")
            _check(resp.status_code == 200, "default: GET / should not redirect after clear-default")

            # ── 9r. Update (Save As vs Update) ────────────────────────
            # Clean slate
            for ek in ("personal", "company"):
                conn_sv = get_connection(ek)
                conn_sv.execute("DELETE FROM saved_views")
                conn_sv.commit()
                conn_sv.close()
            client.set_cookie("entity", "Personal")

            # 9r. Create view, then update its querystring
            resp = client.post("/saved-views/create", data={
                "name": "Updatable",
                "page": "dashboard",
                "query_string": "start=2024-01-01&end=2024-01-31",
            })
            _check(resp.status_code == 200, "update: create Updatable")
            views = _json.loads(resp.get_data(as_text=True))
            upd_id = [v for v in views if v["name"] == "Updatable"][0]["id"]

            # Set it as default to verify update doesn't change is_default
            client.post("/saved-views/set-default", data={
                "id": str(upd_id),
                "page": "dashboard",
            })

            # 9r-i. Update querystring
            resp = client.post("/saved-views/update", data={
                "id": str(upd_id),
                "page": "dashboard",
                "query_string": "start=2025-06-01&end=2025-06-30&account=Checking",
            })
            _check(resp.status_code == 200, "update: expected 200")
            data = _json.loads(resp.get_data(as_text=True))
            _check(data["updated"] is True, "update: response should have updated=true")
            _check(data["id"] == upd_id, "update: response id should match")

            # 9r-ii. GET view and verify querystring changed
            resp = client.get(f"/saved-views/get?id={upd_id}")
            data = _json.loads(resp.get_data(as_text=True))
            _check(
                data["query_string"] == "start=2025-06-01&end=2025-06-30&account=Checking",
                "update: querystring should reflect new value",
            )

            # 9r-iii. Name and is_default unchanged after update
            resp = client.get("/saved-views/list?page=dashboard")
            views = _json.loads(resp.get_data(as_text=True))
            upd_row = [v for v in views if v["id"] == upd_id][0]
            _check(upd_row["name"] == "Updatable", "update: name should be unchanged")
            _check(upd_row["is_default"] == 1, "update: is_default should be unchanged")

            # 9r-iv. Save As creates a second view (both exist)
            resp = client.post("/saved-views/create", data={
                "name": "SavedAs Copy",
                "page": "dashboard",
                "query_string": "start=2025-07-01&end=2025-07-31",
            })
            _check(resp.status_code == 200, "update: Save As should create new view")
            views = _json.loads(resp.get_data(as_text=True))
            names = [v["name"] for v in views]
            _check("Updatable" in names, "update: original view should still exist")
            _check("SavedAs Copy" in names, "update: Save As view should exist")

            # 9r-v. Update with wrong page → 404
            resp = client.post("/saved-views/update", data={
                "id": str(upd_id),
                "page": "transactions",
                "query_string": "type=expense",
            })
            _check(resp.status_code == 404, "update: wrong page should 404")

            # 9r-vi. Update non-existent id → 404
            resp = client.post("/saved-views/update", data={
                "id": "99999",
                "page": "dashboard",
                "query_string": "type=expense",
            })
            _check(resp.status_code == 404, "update: non-existent id should 404")

            # 9r-vii. Cross-entity update → 404
            client.set_cookie("entity", "BFM")
            resp = client.post("/saved-views/update", data={
                "id": str(upd_id),
                "page": "dashboard",
                "query_string": "start=2025-01-01",
            })
            _check(resp.status_code == 404, "update cross-entity: should 404")
            client.set_cookie("entity", "Personal")

        finally:
            # Cleanup all saved views across both entities
            for ek in ("personal", "company"):
                conn_sv = get_connection(ek)
                conn_sv.execute("DELETE FROM saved_views")
                conn_sv.commit()
                conn_sv.close()
            # Reset cookie to Personal for any subsequent tests
            client.set_cookie("entity", "Personal")

        print("   ✅ All Saved Views tests passed (CRUD + rename + default + update)")

        # ── 10. To Do page tests ──────────────────────────────────────
        print("\n10. To Do page tests…")

        import hashlib
        from datetime import date as _date, timedelta as _td

        client.set_cookie("entity", "Personal")

        # 10a. GET /todo returns 200 with Review section
        resp = client.get("/todo/")
        _check(resp.status_code == 200, "todo index: expected 200")
        body = resp.get_data(as_text=True)
        _check("Review" in body, "todo: should contain 'Review'")

        # 10b. Insert fixture data to make review queues non-zero
        conn_fix = get_connection("personal")
        today_str = _date.today().isoformat()

        large_txn_id = hashlib.sha256(
            f"{today_str}|-750.00|LARGE PURCHASE TEST".encode()
        ).hexdigest()[:24]
        conn_fix.execute(
            "INSERT OR IGNORE INTO transactions "
            "(transaction_id, date, description_raw, amount, amount_cents, merchant_canonical, imported_at) "
            "VALUES (?, ?, 'LARGE PURCHASE TEST', -750.00, -75000, 'LargeVendorTest', ?)",
            (large_txn_id, today_str, today_str),
        )

        new_merch_id = hashlib.sha256(
            f"{today_str}|-15.00|BRAND NEW MERCHANT XYZ".encode()
        ).hexdigest()[:24]
        conn_fix.execute(
            "INSERT OR IGNORE INTO transactions "
            "(transaction_id, date, description_raw, amount, amount_cents, merchant_canonical, imported_at) "
            "VALUES (?, ?, 'BRAND NEW MERCHANT XYZ', -15.00, -1500, 'BrandNewMerchantXyz', ?)",
            (new_merch_id, today_str, today_str),
        )
        conn_fix.commit()
        conn_fix.close()

        resp = client.get("/todo/")
        body = resp.get_data(as_text=True)
        _check("Large transactions" in body, "todo queues: Large transactions row should appear")
        _check("New merchants" in body, "todo queues: New merchants row should appear")
        _check("Transactions" in body, "todo queues: Transactions row should appear")

        # 10c. Entity isolation — BFM should not see Personal's queues
        client.set_cookie("entity", "BFM")
        resp = client.get("/todo/")
        _check(resp.status_code == 200, "todo BFM: expected 200")
        body = resp.get_data(as_text=True)
        _check("Transactions" in body, "todo isolation: BFM page renders rows")
        _check("badge-red" not in body, "todo isolation: BFM should have no red badges")

        # 10d. Cleanup fixture txns
        client.set_cookie("entity", "Personal")
        conn_fix = get_connection("personal")
        conn_fix.execute("DELETE FROM transactions WHERE transaction_id IN (?, ?)",
                         (large_txn_id, new_merch_id))
        conn_fix.commit()
        conn_fix.close()

        print("   ✅ All To Do tests passed (queues + isolation)")

        # ── 11. Authentication and protected-cache boundaries ───────
        print("\n11. Authentication and protected-cache boundaries…")

        import hashlib as _hashlib
        import re as _re
        from werkzeug.security import generate_password_hash

        def _csrf_from(body: str) -> str:
            match = _re.search(r'name="_csrf_token" value="([^"]+)"', body)
            _check(match is not None, "auth login: missing CSRF token")
            return match.group(1)

        legacy_password = "synthetic-legacy-password"
        legacy_hash = _hashlib.sha256(legacy_password.encode("utf-8")).hexdigest()
        os.environ["APP_PASSWORD_HASH"] = legacy_hash
        auth_app = create_app()

        with auth_app.test_client() as auth_client:
            resp = auth_client.get("/", follow_redirects=False)
            _check(resp.status_code == 302, "auth: protected root should redirect before rendering")
            _check("/auth/login?next=/" in resp.headers.get("Location", ""), "auth: redirect should preserve a safe next path")
            _check("The Ledger Dashboard" not in resp.get_data(as_text=True), "auth: redirect body must not contain protected dashboard HTML")
            _check(resp.headers.get("Cache-Control") == "no-store", "auth: protected redirect should be no-store")

            htmx_resp = auth_client.get("/transactions/", headers={"HX-Request": "true"})
            _check(htmx_resp.status_code == 401, "auth: unauthenticated HTMX request should return 401")

            login_resp = auth_client.get("/auth/login?next=/transactions/")
            login_body = login_resp.get_data(as_text=True)
            _check(login_resp.status_code == 200, "auth: login page should render")
            _check(login_resp.headers.get("Cache-Control") == "no-store", "auth: login page should be no-store")
            _check(legacy_hash not in login_body, "auth: configured digest must not appear in login HTML")
            _check("/auth/verify" not in login_body and "atlas-auth" not in login_body, "auth: legacy digest replay client must be absent")
            csrf_token = _csrf_from(login_body)

            no_csrf = auth_client.post("/auth/login", data={"password": legacy_password, "next": "/"})
            _check(no_csrf.status_code == 403, "auth: login POST should require CSRF")

            wrong = auth_client.post("/auth/login", data={
                "_csrf_token": csrf_token,
                "password": "wrong-password",
                "next": "/transactions/",
            })
            _check(wrong.status_code == 401, "auth: wrong password should return 401")
            _check("Incorrect password" in wrong.get_data(as_text=True), "auth: wrong password should show a controlled error")

            correct = auth_client.post("/auth/login", data={
                "_csrf_token": csrf_token,
                "password": legacy_password,
                "next": "/transactions/",
            }, follow_redirects=False)
            _check(correct.status_code == 302 and correct.headers.get("Location", "").endswith("/transactions/"), "auth: correct plaintext password should establish a server session")
            _check(auth_client.get("/transactions/").status_code == 200, "auth: authenticated protected request should succeed")

            with auth_client.session_transaction() as auth_session:
                replay_csrf = auth_session.setdefault("_csrf_token", "synthetic-replay-csrf")
            old_route = auth_client.post(
                "/auth/verify",
                json={"hash": legacy_hash},
                headers={"X-CSRF-Token": replay_csrf},
            )
            _check(old_route.status_code == 404, "auth: legacy digest replay route should not exist")

            _check(auth_client.get("/health").status_code == 200, "auth: health route should remain exempt")
            _check(auth_client.get("/sw.js").status_code == 200, "auth: service worker should remain exempt")
            _check(auth_client.get("/offline").status_code == 200, "auth: offline page should remain exempt")
            _check(auth_client.get("/k/").status_code == 200, "auth: public k route should remain unchanged")

        modern_password = "synthetic-modern-password"
        os.environ["APP_PASSWORD_HASH"] = generate_password_hash(modern_password)
        modern_app = create_app()
        with modern_app.test_client() as modern_client:
            login_body = modern_client.get("/auth/login?next=//example.invalid").get_data(as_text=True)
            csrf_token = _csrf_from(login_body)
            correct = modern_client.post("/auth/login", data={
                "_csrf_token": csrf_token,
                "password": modern_password,
                "next": "//example.invalid",
            })
            _check(correct.status_code == 302 and correct.headers.get("Location") == "/", "auth: Werkzeug password hash should authenticate without allowing an external redirect")

        os.environ["APP_PASSWORD_HASH"] = ""
        no_auth_app = create_app()
        no_auth_app.config["TESTING"] = True
        with no_auth_app.test_client() as no_auth_client:
            root = no_auth_client.get("/")
            root_body = root.get_data(as_text=True)
            _check(root.status_code == 200, "auth: no-password mode should render protected app directly")
            _check("authOverlay" not in root_body and "atlas-auth" not in root_body, "auth: no-password mode should not render a blocking client gate")
            _check(no_auth_client.get("/auth/login").status_code == 302, "auth: no-password login route should redirect to the app")

        sw_source = (PROJECT_ROOT / "web" / "static" / "sw.js").read_text()
        precache = sw_source.split("const PRECACHE_URLS = [", 1)[1].split("];", 1)[0]
        _check("'/'" not in precache, "service worker: protected root must not be precached")
        _check("the-ledger-v4" in sw_source, "service worker: cache version should invalidate old dynamic caches")
        _check("networkFirst" not in sw_source, "service worker: dynamic cache fallback should be removed")
        _check(sw_source.count("caches.match(request)") == 1, "service worker: only static cache-first may match the request URL")
        _check(sw_source.count("cache.put(request") == 1, "service worker: only static assets may be cached at runtime")

        print("   ✅ Server auth, legacy/modern compatibility, no-password mode, public exemptions, CSRF, and protected-cache contracts passed")

    print("\n" + "=" * 60)
    print("  🎉  All smoke tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

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
import sqlite3 as sqlite3_module
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch

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

        # ── 7c. Vendor line-item persistence ─────────────────────────
        print("\n7c. Vendor line-item persistence tests…")
        from openpyxl import Workbook
        from core.amazon import (
            auto_split_from_line_items,
            group_orders,
            parse_amazon_csv,
            save_orders_to_db,
        )
        from core.henryschein import parse_henryschein_xlsx

        amazon_csv_text = (
            "Payment Reference ID,Order ID,Order Date,Payment Date,Product Name,"
            "Item Net Total,Payment Amount,Item Quantity,ASIN,"
            "Amazon-Internal Product Category,Order Status\n"
            "PAY-4N-001,ORDER-4N-AMZ,2026-07-10,2026-07-11,Office labels,"
            "$10.01,$15.00,1,ASIN-4N-A,Office Product,Shipped\n"
            "PAY-4N-001,ORDER-4N-AMZ,2026-07-10,2026-07-11,Coffee pods,"
            "$4.99,$15.00,1,ASIN-4N-B,Grocery,Shipped\n"
        )
        amazon_csv = io.StringIO(amazon_csv_text)
        amazon_df, amazon_warnings = parse_amazon_csv(amazon_csv)
        _check(not amazon_warnings, f"vendor line items: unexpected Amazon warnings {amazon_warnings}")
        amazon_orders = group_orders(amazon_df)
        _check(len(amazon_orders) == 1 and len(amazon_orders[0]["items"]) == 2,
               "vendor line items: Amazon parser should preserve two grouped items")

        hs_book = Workbook()
        hs_sheet = hs_book.active
        hs_sheet.append(["Items Purchased"])
        hs_sheet.append([])
        hs_sheet.append([
            "Invoice No", "Short Description", "Amount", "Invoice Date",
            "Category", "Sub Category1", "Qty", "Unit Price", "Item Code",
        ])
        hs_sheet.append([
            "INV-4N-HS", "Diagnostic strips", "$15.00", "2026-07-12",
            "Diagnostics", "Testing", 1, "$4.00", "HS-4N-A",
        ])
        hs_sheet.append([
            "INV-4N-HS", "Exam gloves", "$15.00", "2026-07-12",
            "PPE", "Gloves", 2, "$5.50", "HS-4N-B",
        ])
        hs_buffer = io.BytesIO()
        hs_book.save(hs_buffer)
        hs_buffer.seek(0)
        hs_orders, hs_warnings = parse_henryschein_xlsx(hs_buffer)
        _check(not hs_warnings, f"vendor line items: unexpected Henry Schein warnings {hs_warnings}")
        _check(len(hs_orders) == 1 and len(hs_orders[0]["items"]) == 2,
               "vendor line items: Henry Schein parser should preserve two grouped items")

        vendor_entities = ("personal", "company", "luxelegacy")
        original_socket = socket.socket

        def _deny_vendor_network(*_args, **_kwargs):
            raise AssertionError("vendor line-item persistence attempted outbound networking")

        try:
            socket.socket = _deny_vendor_network
            for entity_key in vendor_entities:
                before_conn = get_connection(entity_key)
                before_transactions = before_conn.execute(
                    "SELECT COUNT(*) FROM transactions"
                ).fetchone()[0]
                before_conn.close()

                inserted_amz, skipped_amz = save_orders_to_db(
                    entity_key, amazon_orders, vendor="amazon"
                )
                inserted_hs, skipped_hs = save_orders_to_db(
                    entity_key, hs_orders, vendor="henryschein"
                )
                _check((inserted_amz, skipped_amz, inserted_hs, skipped_hs) == (1, 0, 1, 0),
                       f"vendor line items: first save counts wrong for {entity_key}")

                conn_vendor = get_connection(entity_key)
                parent_rows = conn_vendor.execute(
                    "SELECT id, order_id, order_total_cents, vendor "
                    "FROM amazon_orders WHERE order_id IN ('ORDER-4N-AMZ', 'INV-4N-HS') "
                    "ORDER BY order_id"
                ).fetchall()
                _check(len(parent_rows) == 2,
                       f"vendor line items: expected two parents in {entity_key}")
                parent_by_order = {row["order_id"]: row for row in parent_rows}
                _check(parent_by_order["ORDER-4N-AMZ"]["order_total_cents"] == 1500,
                       f"vendor line items: Amazon parent cents wrong in {entity_key}")
                _check(parent_by_order["INV-4N-HS"]["order_total_cents"] == 1500,
                       f"vendor line items: Henry Schein parent cents wrong in {entity_key}")

                item_rows = conn_vendor.execute(
                    "SELECT ao.order_id, li.product_name, li.quantity, "
                    "li.unit_price_cents, li.item_total_cents, li.asin, "
                    "li.amazon_category, li.category, li.subcategory "
                    "FROM order_line_items li "
                    "JOIN amazon_orders ao ON ao.id = li.amazon_order_id "
                    "WHERE ao.order_id IN ('ORDER-4N-AMZ', 'INV-4N-HS') "
                    "ORDER BY ao.order_id, li.id"
                ).fetchall()
                _check(len(item_rows) == 4,
                       f"vendor line items: expected four children in {entity_key}")
                item_totals = {}
                for row in item_rows:
                    item_totals.setdefault(row["order_id"], 0)
                    item_totals[row["order_id"]] += row["item_total_cents"]
                    _check(row["category"] is None and row["subcategory"] is None,
                           "vendor line items: raw import must not invent Ledger categories")
                _check(item_totals == {"INV-4N-HS": 1500, "ORDER-4N-AMZ": 1500},
                       f"vendor line items: child cents do not reconcile in {entity_key}: {item_totals}")
                hs_items = [row for row in item_rows if row["order_id"] == "INV-4N-HS"]
                _check([(row["quantity"], row["unit_price_cents"], row["item_total_cents"])
                        for row in hs_items] == [(1, 400, 400), (2, 550, 1100)],
                       f"vendor line items: Henry quantity and cents wrong in {entity_key}")
                _check(conn_vendor.execute(
                    "SELECT COUNT(*) FROM transactions"
                ).fetchone()[0] == before_transactions,
                       f"vendor line items: save changed unrelated transactions in {entity_key}")
                conn_vendor.close()

                repeat_amz = save_orders_to_db(entity_key, amazon_orders, vendor="amazon")
                repeat_hs = save_orders_to_db(entity_key, hs_orders, vendor="henryschein")
                _check((repeat_amz, repeat_hs) == ((0, 1), (0, 1)),
                       f"vendor line items: exact reimport not idempotent in {entity_key}")
                conn_vendor = get_connection(entity_key)
                _check(conn_vendor.execute(
                    "SELECT COUNT(*) FROM order_line_items li "
                    "JOIN amazon_orders ao ON ao.id = li.amazon_order_id "
                    "WHERE ao.order_id IN ('ORDER-4N-AMZ', 'INV-4N-HS')"
                ).fetchone()[0] == 4,
                       f"vendor line items: reimport duplicated children in {entity_key}")
                conn_vendor.close()
        finally:
            socket.socket = original_socket

        # A child-row failure must roll back its newly inserted parent and every
        # earlier row in the same save transaction.
        conn_vendor = get_connection("personal")
        conn_vendor.execute(
            "CREATE TRIGGER vendor_line_item_4n_abort "
            "BEFORE INSERT ON order_line_items "
            "BEGIN SELECT RAISE(ABORT, 'synthetic 4N rollback'); END"
        )
        conn_vendor.commit()
        conn_vendor.close()
        rollback_order = dict(amazon_orders[0])
        rollback_order["order_id"] = "ORDER-4N-ROLLBACK"
        try:
            save_orders_to_db("personal", [rollback_order], vendor="amazon")
            _check(False, "vendor line items: forced child failure should raise")
        except Exception as exc:
            _check("synthetic 4N rollback" in str(exc),
                   f"vendor line items: unexpected rollback error {exc}")
        conn_vendor = get_connection("personal")
        _check(conn_vendor.execute(
            "SELECT COUNT(*) FROM amazon_orders WHERE order_id='ORDER-4N-ROLLBACK'"
        ).fetchone()[0] == 0,
               "vendor line items: failed child insert left its parent behind")
        conn_vendor.execute("DROP TRIGGER vendor_line_item_4n_abort")
        conn_vendor.commit()
        conn_vendor.close()

        invalid_quantity_order = dict(amazon_orders[0])
        invalid_quantity_order["order_id"] = "ORDER-4N-INVALID-QTY"
        invalid_quantity_order["items"] = [
            dict(amazon_orders[0]["items"][0], quantity=0)
        ]
        try:
            save_orders_to_db("personal", [invalid_quantity_order], vendor="amazon")
            _check(False, "vendor line items: invalid quantity should raise")
        except ValueError as exc:
            _check("quantity" in str(exc),
                   f"vendor line items: unexpected quantity error {exc}")
        conn_vendor = get_connection("personal")
        _check(conn_vendor.execute(
            "SELECT COUNT(*) FROM amazon_orders WHERE order_id='ORDER-4N-INVALID-QTY'"
        ).fetchone()[0] == 0,
               "vendor line items: invalid quantity left its parent behind")
        conn_vendor.close()

        # Prove the maintained split path can consume newly persisted children
        # without the standalone population script. Category assignment itself
        # remains the separately scoped Task 1L.3 contract.
        vendor_split_txn = "vendor-line-item-4n-split"
        conn_vendor = get_connection("personal")
        conn_vendor.execute(
            "INSERT INTO transactions "
            "(transaction_id, date, description_raw, amount, amount_cents, imported_at) "
            "VALUES (?, '2026-07-11', 'AMAZON 4N SYNTHETIC', -15.00, -1500, '2026-07-19')",
            (vendor_split_txn,),
        )
        conn_vendor.execute(
            "UPDATE amazon_orders SET matched_transaction_id=? "
            "WHERE order_id='ORDER-4N-AMZ'",
            (vendor_split_txn,),
        )
        amazon_item_ids = conn_vendor.execute(
            "SELECT li.id FROM order_line_items li "
            "JOIN amazon_orders ao ON ao.id=li.amazon_order_id "
            "WHERE ao.order_id='ORDER-4N-AMZ' ORDER BY li.id"
        ).fetchall()
        conn_vendor.execute(
            "UPDATE order_line_items SET category='Office Supplies', subcategory='General' "
            "WHERE id=?", (amazon_item_ids[0]["id"],)
        )
        conn_vendor.execute(
            "UPDATE order_line_items SET category='Food', subcategory='Coffee' "
            "WHERE id=?", (amazon_item_ids[1]["id"],)
        )
        split_result = auto_split_from_line_items(conn_vendor, vendor_split_txn)
        _check(split_result == {"ok": True, "count": 2},
               f"vendor line items: auto-split result wrong: {split_result}")
        split_rows = conn_vendor.execute(
            "SELECT amount_cents, source FROM transaction_splits "
            "WHERE transaction_id=? ORDER BY sort_order", (vendor_split_txn,)
        ).fetchall()
        _check(len(split_rows) == 2 and sum(row["amount_cents"] for row in split_rows) == -1500,
               "vendor line items: auto-split pieces must reconcile to the bank transaction")
        _check(all(row["source"] == "vendor_line_item" for row in split_rows),
               "vendor line items: auto-split source should remain vendor_line_item")
        conn_vendor.commit()
        conn_vendor.close()

        # Exact cleanup across all three synthetic entities.
        for entity_key in vendor_entities:
            conn_vendor = get_connection(entity_key)
            if entity_key == "personal":
                conn_vendor.execute(
                    "DELETE FROM transaction_splits WHERE transaction_id=?",
                    (vendor_split_txn,),
                )
                conn_vendor.execute(
                    "DELETE FROM transactions WHERE transaction_id=?",
                    (vendor_split_txn,),
                )
            conn_vendor.execute(
                "DELETE FROM order_line_items WHERE amazon_order_id IN ("
                "SELECT id FROM amazon_orders "
                "WHERE order_id IN ('ORDER-4N-AMZ', 'INV-4N-HS'))"
            )
            conn_vendor.execute(
                "DELETE FROM amazon_orders "
                "WHERE order_id IN ('ORDER-4N-AMZ', 'INV-4N-HS', "
                "'ORDER-4N-ROLLBACK', 'ORDER-4N-INVALID-QTY')"
            )
            conn_vendor.commit()
            _check(conn_vendor.execute(
                "SELECT COUNT(*) FROM order_line_items"
            ).fetchone()[0] == 0,
                   f"vendor line items: cleanup left child rows in {entity_key}")
            conn_vendor.close()
        print("   ✅ Amazon and Henry parent/item atomicity, cents, reimport, split, isolation, denied-network, and cleanup passed")

        # ── 7d. Deterministic category-domain enforcement ───────────
        print("\n7d. Deterministic category-domain enforcement tests…")
        os.environ["FLASK_SECRET"] = "smoke-test-secret-key"
        os.environ["APP_PASSWORD_HASH"] = ""
        from web import create_app
        app = create_app()
        app.config["TESTING"] = True

        from core.amazon import (
            apply_matches,
            categorize_order,
            infer_category,
        )
        from core.categories import (
            CategoryDomainError,
            load_categories,
            normalize_category_pair,
        )
        from core.henryschein import _deterministic_primary_category

        domain_cases = {
            "personal": ("Personal", "Food", "Groceries"),
            "company": ("BFM", "Electronics", "General"),
            "luxelegacy": ("LL", "Supplies", "General"),
        }

        for entity_key, (_, valid_cat, valid_sub) in domain_cases.items():
            _check(
                normalize_category_pair(entity_key, valid_cat, valid_sub)
                == (valid_cat, valid_sub),
                f"category domain {entity_key}: valid pair should round-trip",
            )
            _check(
                normalize_category_pair(entity_key, valid_cat, "Unknown")
                == (valid_cat, "General"),
                f"category domain {entity_key}: Unknown should normalize to General",
            )
            try:
                normalize_category_pair(entity_key, "Undefined 4O", "General")
                _check(False, f"category domain {entity_key}: undefined category should fail")
            except CategoryDomainError:
                pass
            try:
                normalize_category_pair(entity_key, valid_cat, "Undefined 4O")
                _check(False, f"category domain {entity_key}: undefined subcategory should fail")
            except CategoryDomainError:
                pass

            for product_name, raw_category in (
                ("USB charging cable", ""),
                ("Unmapped synthetic item", "Unknown Vendor Category"),
            ):
                inferred_pair = infer_category(entity_key, product_name, raw_category)
                _check(
                    normalize_category_pair(entity_key, *inferred_pair) == inferred_pair,
                    f"category domain {entity_key}: every inference must be valid",
                )

        _check(
            infer_category("personal", "USB charging cable")
            == ("Needs Review", "General"),
            "category domain: invalid Personal Electronics inference should fall back",
        )
        _check(
            infer_category("company", "USB charging cable")
            == ("Electronics", "General"),
            "category domain: valid BFM Electronics inference should be preserved",
        )
        _check(
            infer_category("luxelegacy", "Unmapped synthetic item")
            == ("Needs Review", "General"),
            "category domain: unknown LL inference should fall back",
        )

        tie_categories = ["Home", "CE", "Home", "CE"]
        _check(
            _deterministic_primary_category(tie_categories) == "CE",
            "category domain: equal-frequency category ties should sort deterministically",
        )
        tie_script = (
            "from core.henryschein import _deterministic_primary_category as choose; "
            "print(choose(['Home', 'CE', 'Home', 'CE']))"
        )
        tie_outputs = set()
        for seed in ("1", "7", "41"):
            tie_env = os.environ.copy()
            tie_env["PYTHONHASHSEED"] = seed
            tie_result = subprocess.run(
                [sys.executable, "-c", tie_script],
                cwd=PROJECT_ROOT,
                env=tie_env,
                capture_output=True,
                text=True,
                check=True,
            )
            tie_outputs.add(tie_result.stdout.strip())
        _check(
            tie_outputs == {"CE"},
            f"category domain: cross-hash-seed tie output changed: {tie_outputs}",
        )

        original_socket = socket.socket

        def _deny_category_network(*_args, **_kwargs):
            raise AssertionError("category-domain smoke attempted outbound networking")

        try:
            socket.socket = _deny_category_network
            for entity_key, (display_entity, valid_cat, valid_sub) in domain_cases.items():
                match_txn_id = f"domain-match-{entity_key}"
                match_order_id = f"ORDER-4O-MATCH-{entity_key}"
                order_only_id = f"ORDER-4O-CAT-{entity_key}"
                skip_order_id = f"ORDER-4O-SKIP-{entity_key}"
                accept_txn_ids = [
                    f"domain-accept-{entity_key}-1",
                    f"domain-accept-{entity_key}-2",
                ]
                conn_domain = get_connection(entity_key)
                conn_domain.execute(
                    "INSERT INTO transactions "
                    "(transaction_id, date, description_raw, amount, amount_cents, account, "
                    "category, subcategory, notes, source_filename, imported_at) "
                    "VALUES (?, '2026-07-19', ?, -12.34, -1234, 'Synthetic 4O', "
                    "'Needs Review', 'General', 'before-match', 'category-4o', "
                    "'2026-07-19T00:00:00+00:00')",
                    (match_txn_id, f"DOMAIN MATCH {entity_key}"),
                )
                for index, txn_id in enumerate(accept_txn_ids, start=1):
                    conn_domain.execute(
                        "INSERT INTO transactions "
                        "(transaction_id, date, description_raw, amount, amount_cents, "
                        "account, category, subcategory, notes, source_filename, imported_at) "
                        "VALUES (?, '2026-07-19', ?, -5.00, -500, 'Synthetic 4O', "
                        "'Needs Review', 'General', ?, 'category-4o', "
                        "'2026-07-19T00:00:00+00:00')",
                        (txn_id, f"DOMAIN 4O {entity_key} MERCHANT {index}", f"before-{index}"),
                    )
                for order_id in (match_order_id, order_only_id, skip_order_id):
                    conn_domain.execute(
                        "INSERT INTO amazon_orders "
                        "(order_id, order_date, product_summary, order_total, "
                        "order_total_cents, vendor, imported_at) "
                        "VALUES (?, '2026-07-19', ?, 12.34, 1234, 'amazon', "
                        "'2026-07-19T00:00:00+00:00')",
                        (order_id, f"Synthetic category order {order_id}"),
                    )
                conn_domain.commit()
                order_rows = conn_domain.execute(
                    "SELECT id, order_id FROM amazon_orders "
                    "WHERE order_id IN (?, ?, ?)",
                    (match_order_id, order_only_id, skip_order_id),
                ).fetchall()
                order_db_ids = {row["order_id"]: row["id"] for row in order_rows}
                alias_count_before = conn_domain.execute(
                    "SELECT COUNT(*) FROM merchant_aliases"
                ).fetchone()[0]
                conn_domain.close()

                invalid_matches = [
                    {
                        "transaction_id": match_txn_id,
                        "product_summary": "Valid candidate",
                        "suggested_category": valid_cat,
                        "suggested_subcategory": valid_sub,
                        "order_id": match_order_id,
                        "order_total": 12.34,
                        "confidence": 0.95,
                    },
                    {
                        "transaction_id": match_txn_id,
                        "product_summary": "Invalid candidate",
                        "suggested_category": "Undefined 4O",
                        "suggested_subcategory": "General",
                        "order_id": match_order_id,
                        "order_total": 12.34,
                        "confidence": 0.95,
                    },
                ]
                try:
                    apply_matches(entity_key, invalid_matches)
                    _check(False, f"category domain {entity_key}: invalid match batch should fail")
                except CategoryDomainError:
                    pass
                conn_domain = get_connection(entity_key)
                unchanged_match = conn_domain.execute(
                    "SELECT category, subcategory, notes FROM transactions "
                    "WHERE transaction_id=?", (match_txn_id,)
                ).fetchone()
                unmatched_order = conn_domain.execute(
                    "SELECT matched_transaction_id FROM amazon_orders WHERE order_id=?",
                    (match_order_id,),
                ).fetchone()[0]
                _check(
                    tuple(unchanged_match) == ("Needs Review", "General", "before-match")
                    and unmatched_order is None,
                    f"category domain {entity_key}: invalid match changed stored data",
                )
                conn_domain.close()

                apply_matches(entity_key, [invalid_matches[0]])
                conn_domain = get_connection(entity_key)
                applied_match = conn_domain.execute(
                    "SELECT category, subcategory, notes FROM transactions "
                    "WHERE transaction_id=?", (match_txn_id,)
                ).fetchone()
                applied_order = conn_domain.execute(
                    "SELECT matched_transaction_id FROM amazon_orders WHERE order_id=?",
                    (match_order_id,),
                ).fetchone()[0]
                _check(
                    tuple(applied_match) == (valid_cat, valid_sub, "Valid candidate")
                    and applied_order == match_txn_id,
                    f"category domain {entity_key}: valid match did not persist exact pair",
                )
                conn_domain.close()

                try:
                    categorize_order(
                        entity_key,
                        order_db_ids[order_only_id],
                        "Undefined 4O",
                        "General",
                    )
                    _check(False, f"category domain {entity_key}: invalid order pair should fail")
                except CategoryDomainError:
                    pass
                conn_domain = get_connection(entity_key)
                invalid_order_state = conn_domain.execute(
                    "SELECT category, subcategory FROM amazon_orders WHERE id=?",
                    (order_db_ids[order_only_id],),
                ).fetchone()
                _check(
                    tuple(invalid_order_state) == (None, None),
                    f"category domain {entity_key}: invalid order pair changed data",
                )
                conn_domain.close()

                with app.test_client() as category_client:
                    category_client.set_cookie("entity", display_entity)
                    csrf_token = f"category-domain-{entity_key}-csrf"
                    with category_client.session_transaction() as category_session:
                        category_session["_csrf_token"] = csrf_token

                    invalid_accept = category_client.post(
                        "/categorize/accept",
                        data={
                            "_csrf_token": csrf_token,
                            "txn_id": accept_txn_ids,
                            f"cat_{accept_txn_ids[0]}": valid_cat,
                            f"subcat_{accept_txn_ids[0]}": valid_sub,
                            f"notes_{accept_txn_ids[0]}": "after-1",
                            f"desc_{accept_txn_ids[0]}": f"DOMAIN 4O {entity_key} MERCHANT 1",
                            f"cat_{accept_txn_ids[1]}": "Undefined 4O",
                            f"subcat_{accept_txn_ids[1]}": "General",
                            f"notes_{accept_txn_ids[1]}": "after-2",
                            f"desc_{accept_txn_ids[1]}": f"DOMAIN 4O {entity_key} MERCHANT 2",
                        },
                        follow_redirects=False,
                    )
                    _check(
                        invalid_accept.status_code == 302,
                        f"category domain {entity_key}: invalid accept should redirect",
                    )
                    conn_domain = get_connection(entity_key)
                    invalid_accept_rows = conn_domain.execute(
                        "SELECT category, subcategory, notes FROM transactions "
                        "WHERE transaction_id IN (?, ?) ORDER BY transaction_id",
                        tuple(accept_txn_ids),
                    ).fetchall()
                    alias_count_after_invalid = conn_domain.execute(
                        "SELECT COUNT(*) FROM merchant_aliases"
                    ).fetchone()[0]
                    _check(
                        [tuple(row) for row in invalid_accept_rows]
                        == [
                            ("Needs Review", "General", "before-1"),
                            ("Needs Review", "General", "before-2"),
                        ]
                        and alias_count_after_invalid == alias_count_before,
                        f"category domain {entity_key}: invalid accept batch mutated rows or aliases",
                    )
                    conn_domain.close()

                    valid_accept = category_client.post(
                        "/categorize/accept",
                        data={
                            "_csrf_token": csrf_token,
                            "txn_id": accept_txn_ids,
                            f"cat_{accept_txn_ids[0]}": valid_cat,
                            f"subcat_{accept_txn_ids[0]}": valid_sub,
                            f"notes_{accept_txn_ids[0]}": "after-1",
                            f"desc_{accept_txn_ids[0]}": f"DOMAIN 4O {entity_key} MERCHANT 1",
                            f"cat_{accept_txn_ids[1]}": valid_cat,
                            f"subcat_{accept_txn_ids[1]}": "Unknown",
                            f"notes_{accept_txn_ids[1]}": "after-2",
                            f"desc_{accept_txn_ids[1]}": f"DOMAIN 4O {entity_key} MERCHANT 2",
                        },
                        follow_redirects=False,
                    )
                    _check(
                        valid_accept.status_code == 302,
                        f"category domain {entity_key}: valid accept should redirect",
                    )
                    conn_domain = get_connection(entity_key)
                    valid_accept_rows = conn_domain.execute(
                        "SELECT category, subcategory, notes FROM transactions "
                        "WHERE transaction_id IN (?, ?) ORDER BY transaction_id",
                        tuple(accept_txn_ids),
                    ).fetchall()
                    _check(
                        [tuple(row) for row in valid_accept_rows]
                        == [
                            (valid_cat, valid_sub, "after-1"),
                            (valid_cat, "General", "after-2"),
                        ],
                        f"category domain {entity_key}: valid accept did not normalize pairs",
                    )
                    conn_domain.close()

                    vendor_page = category_client.get("/categorize-vendors/")
                    _check(
                        vendor_page.status_code == 200
                        and "Or new subcategory" not in vendor_page.get_data(as_text=True),
                        f"category domain {entity_key}: vendor card exposed ad hoc subcategory creation",
                    )
                    invalid_vendor = category_client.post(
                        "/categorize-vendors/save",
                        data={
                            "_csrf_token": csrf_token,
                            "order_id": order_db_ids[order_only_id],
                            "category": "Undefined 4O",
                            "subcategory": "General",
                        },
                        headers={"HX-Request": "true"},
                    )
                    _check(
                        invalid_vendor.status_code == 200
                        and "not defined for this entity"
                        in invalid_vendor.get_data(as_text=True),
                        f"category domain {entity_key}: invalid vendor save should explain rejection",
                    )
                    conn_domain = get_connection(entity_key)
                    vendor_after_invalid = conn_domain.execute(
                        "SELECT category, subcategory FROM amazon_orders WHERE id=?",
                        (order_db_ids[order_only_id],),
                    ).fetchone()
                    _check(
                        tuple(vendor_after_invalid) == (None, None),
                        f"category domain {entity_key}: invalid vendor save advanced the queue",
                    )
                    conn_domain.close()

                    valid_vendor = category_client.post(
                        "/categorize-vendors/save",
                        data={
                            "_csrf_token": csrf_token,
                            "order_id": order_db_ids[order_only_id],
                            "category": valid_cat,
                            "subcategory": valid_sub,
                        },
                        headers={"HX-Request": "true"},
                    )
                    _check(
                        valid_vendor.status_code == 200,
                        f"category domain {entity_key}: valid vendor save should render next state",
                    )
                    skipped_vendor = category_client.post(
                        "/categorize-vendors/skip",
                        data={
                            "_csrf_token": csrf_token,
                            "order_id": order_db_ids[skip_order_id],
                        },
                        headers={"HX-Request": "true"},
                    )
                    _check(
                        skipped_vendor.status_code == 200,
                        f"category domain {entity_key}: dedicated skip should remain available",
                    )

                conn_domain = get_connection(entity_key)
                final_orders = conn_domain.execute(
                    "SELECT order_id, category, subcategory FROM amazon_orders "
                    "WHERE order_id IN (?, ?) ORDER BY order_id",
                    (order_only_id, skip_order_id),
                ).fetchall()
                final_order_map = {
                    row["order_id"]: (row["category"], row["subcategory"])
                    for row in final_orders
                }
                _check(
                    final_order_map[order_only_id] == (valid_cat, valid_sub)
                    and final_order_map[skip_order_id] == ("Skipped", None),
                    f"category domain {entity_key}: valid or skipped vendor state was wrong",
                )

                conn_domain.execute(
                    "DELETE FROM merchant_aliases WHERE pattern LIKE ?",
                    (f"DOMAIN 4O {entity_key}%",),
                )
                conn_domain.execute(
                    "DELETE FROM transactions WHERE transaction_id IN (?, ?, ?)",
                    (match_txn_id, *accept_txn_ids),
                )
                conn_domain.execute(
                    "DELETE FROM amazon_orders WHERE order_id IN (?, ?, ?)",
                    (match_order_id, order_only_id, skip_order_id),
                )
                conn_domain.commit()
                remaining_domain_rows = conn_domain.execute(
                    "SELECT "
                    "(SELECT COUNT(*) FROM transactions WHERE source_filename='category-4o'), "
                    "(SELECT COUNT(*) FROM amazon_orders WHERE order_id LIKE 'ORDER-4O-%'), "
                    "(SELECT COUNT(*) FROM merchant_aliases WHERE pattern LIKE 'DOMAIN 4O %')"
                ).fetchone()
                _check(
                    tuple(remaining_domain_rows) == (0, 0, 0),
                    f"category domain {entity_key}: exact cleanup failed",
                )
                conn_domain.close()
        finally:
            socket.socket = original_socket

        _check(
            all(load_categories(entity) for entity in domain_cases),
            "category domain: maintained entity definitions should remain available",
        )
        print("   ✅ Entity inference, stable ties, zero-mutation rejection, valid writes, skip sentinel, isolation, denied-network, and cleanup passed")

        # ── 7e. Vendor payment matching integrity ───────────────────
        print("\n7e. Vendor payment matching integrity tests…")
        from core.vendor_matching import apply_vendor_matches, match_vendor_to_bank

        vendor_match_entities = ("personal", "company", "luxelegacy")
        vendor_match_prefixes = {
            entity_key: f"vendor-match-4m-{entity_key}"
            for entity_key in vendor_match_entities
        }

        def _insert_vendor_match_bank(conn, txn_id, date, amount, description, notes="before"):
            conn.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_raw, merchant_canonical, "
                "amount, amount_cents, account, notes, source_filename, imported_at) "
                "VALUES (?, ?, ?, ?, 'Before Merchant', ?, ?, 'Synthetic 4M', ?, "
                "'vendor-match-4m', '2026-07-20T00:00:00+00:00')",
                (
                    txn_id,
                    date,
                    description,
                    description,
                    amount,
                    int(round(amount * 100)),
                    notes,
                ),
            )

        def _insert_vendor_match_vendor(
            conn, plaid_txn_id, date, amount, recipient, vendor_type="venmo"
        ):
            cursor = conn.execute(
                "INSERT INTO vendor_transactions "
                "(plaid_item_id, plaid_transaction_id, plaid_account_id, date, amount, "
                "amount_cents, name, merchant_name, recipient, vendor_type, imported_at) "
                "VALUES (?, ?, 'account-4m', ?, ?, ?, ?, ?, ?, ?, "
                "'2026-07-20T00:00:00+00:00')",
                (
                    f"item-4m-{plaid_txn_id}",
                    plaid_txn_id,
                    date,
                    amount,
                    int(round(amount * 100)),
                    recipient,
                    recipient,
                    recipient,
                    vendor_type,
                ),
            )
            return cursor.lastrowid

        # Seed the same acceptance matrix into every isolated entity database.
        seeded_vendor_matches = {}
        for entity_key in vendor_match_entities:
            prefix = vendor_match_prefixes[entity_key]
            conn_match = get_connection(entity_key)
            transaction_columns = {
                row["name"] for row in conn_match.execute("PRAGMA table_info(transactions)")
            }
            _check(
                "matched_order_id" not in transaction_columns,
                f"vendor matching {entity_key}: test requires the real migration-built schema",
            )
            exact_bank = f"{prefix}-bank-exact"
            likely_bank = f"{prefix}-bank-likely"
            unmatched_bank = f"{prefix}-bank-unmatched"
            control_bank = f"{prefix}-bank-control"
            _insert_vendor_match_bank(
                conn_match, exact_bank, "2026-07-01", -40.00, "VENMO EXACT 4M"
            )
            _insert_vendor_match_bank(
                conn_match, likely_bank, "2026-07-06", -50.00, "VENMO LIKELY 4M"
            )
            _insert_vendor_match_bank(
                conn_match, unmatched_bank, "2026-07-01", -997.00, "PAYPAL UNMATCHED 4M"
            )
            _insert_vendor_match_bank(
                conn_match, control_bank, "2026-07-01", -13.00, "CONTROL 4M", "control-before"
            )
            exact_vendor = _insert_vendor_match_vendor(
                conn_match, f"{prefix}-vendor-exact", "2026-07-01", 40.00, "Exact Recipient"
            )
            likely_vendor = _insert_vendor_match_vendor(
                conn_match, f"{prefix}-vendor-likely", "2026-07-01", 50.00, "Likely Recipient"
            )
            unmatched_vendor = _insert_vendor_match_vendor(
                conn_match, f"{prefix}-vendor-unmatched", "2026-07-01", 61.00, "No Match"
            )
            conn_match.commit()
            conn_match.close()
            seeded_vendor_matches[entity_key] = {
                "exact_bank": exact_bank,
                "likely_bank": likely_bank,
                "unmatched_bank": unmatched_bank,
                "control_bank": control_bank,
                "exact_vendor": exact_vendor,
                "likely_vendor": likely_vendor,
                "unmatched_vendor": unmatched_vendor,
            }

        original_socket = socket.socket

        def _deny_vendor_match_network(*_args, **_kwargs):
            raise AssertionError("vendor-payment matching smoke attempted outbound networking")

        try:
            socket.socket = _deny_vendor_match_network
            for entity_key in vendor_match_entities:
                ids = seeded_vendor_matches[entity_key]
                result = match_vendor_to_bank(entity_key)
                _check(
                    result["auto_applied"] == 1
                    and len(result["review"]) == 1
                    and result["unmatched_vendor"] == 1
                    and result["unmatched_bank"] == 1,
                    f"vendor matching {entity_key}: exact/review/unmatched result was {result}",
                )
                review_match = result["review"][0]
                _check(
                    review_match["vendor_id"] == ids["likely_vendor"]
                    and review_match["bank_txn_id"] == ids["likely_bank"]
                    and review_match["confidence"] == 0.80,
                    f"vendor matching {entity_key}: likely match contract changed",
                )

                conn_match = get_connection(entity_key)
                exact_vendor_state = conn_match.execute(
                    "SELECT matched_transaction_id, match_confidence "
                    "FROM vendor_transactions WHERE id=?",
                    (ids["exact_vendor"],),
                ).fetchone()
                exact_bank_state = conn_match.execute(
                    "SELECT merchant_canonical, notes FROM transactions WHERE transaction_id=?",
                    (ids["exact_bank"],),
                ).fetchone()
                likely_vendor_state = conn_match.execute(
                    "SELECT matched_transaction_id FROM vendor_transactions WHERE id=?",
                    (ids["likely_vendor"],),
                ).fetchone()[0]
                control_state = conn_match.execute(
                    "SELECT merchant_canonical, notes FROM transactions WHERE transaction_id=?",
                    (ids["control_bank"],),
                ).fetchone()
                _check(
                    tuple(exact_vendor_state) == (ids["exact_bank"], 0.95)
                    and tuple(exact_bank_state) == ("Exact Recipient", "Exact Recipient via Venmo")
                    and likely_vendor_state is None
                    and tuple(control_state) == ("Before Merchant", "control-before"),
                    f"vendor matching {entity_key}: exact application changed the wrong rows",
                )
                conn_match.close()

                applied = apply_vendor_matches(entity_key, [review_match])
                _check(applied == 1, f"vendor matching {entity_key}: review apply count was {applied}")
                conn_match = get_connection(entity_key)
                accepted_state = conn_match.execute(
                    "SELECT vt.matched_transaction_id, vt.match_confidence, "
                    "t.merchant_canonical, t.notes "
                    "FROM vendor_transactions vt JOIN transactions t "
                    "ON t.transaction_id=vt.matched_transaction_id WHERE vt.id=?",
                    (ids["likely_vendor"],),
                ).fetchone()
                _check(
                    tuple(accepted_state)
                    == (ids["likely_bank"], 0.80, "Likely Recipient", "Likely Recipient via Venmo"),
                    f"vendor matching {entity_key}: reviewed match did not persist canonically",
                )
                stable_snapshot = conn_match.execute(
                    "SELECT transaction_id, merchant_canonical, notes FROM transactions "
                    "WHERE source_filename='vendor-match-4m' ORDER BY transaction_id"
                ).fetchall()
                conn_match.close()
                try:
                    apply_vendor_matches(entity_key, [review_match])
                    _check(False, f"vendor matching {entity_key}: stale replay should fail")
                except ValueError:
                    pass
                conn_match = get_connection(entity_key)
                after_stale = conn_match.execute(
                    "SELECT transaction_id, merchant_canonical, notes FROM transactions "
                    "WHERE source_filename='vendor-match-4m' ORDER BY transaction_id"
                ).fetchall()
                _check(
                    [tuple(row) for row in after_stale]
                    == [tuple(row) for row in stable_snapshot],
                    f"vendor matching {entity_key}: stale replay changed transaction data",
                )

                # Duplicate claims are rejected before either side changes.
                duplicate_bank = f"{vendor_match_prefixes[entity_key]}-bank-duplicate"
                _insert_vendor_match_bank(
                    conn_match, duplicate_bank, "2026-07-10", -71.00, "VENMO DUPLICATE 4M"
                )
                duplicate_vendor_1 = _insert_vendor_match_vendor(
                    conn_match,
                    f"{vendor_match_prefixes[entity_key]}-vendor-duplicate-1",
                    "2026-07-10",
                    71.00,
                    "Duplicate One",
                )
                duplicate_vendor_2 = _insert_vendor_match_vendor(
                    conn_match,
                    f"{vendor_match_prefixes[entity_key]}-vendor-duplicate-2",
                    "2026-07-10",
                    72.00,
                    "Duplicate Two",
                )
                conn_match.commit()
                conn_match.close()
                try:
                    apply_vendor_matches(
                        entity_key,
                        [
                            {
                                "vendor_id": duplicate_vendor_1,
                                "bank_txn_id": duplicate_bank,
                                "recipient": "Duplicate One",
                                "vendor_type": "venmo",
                                "confidence": 0.80,
                            },
                            {
                                "vendor_id": duplicate_vendor_2,
                                "bank_txn_id": duplicate_bank,
                                "recipient": "Duplicate Two",
                                "vendor_type": "venmo",
                                "confidence": 0.80,
                            },
                        ],
                    )
                    _check(False, f"vendor matching {entity_key}: duplicate bank claim should fail")
                except ValueError:
                    pass
                conn_match = get_connection(entity_key)
                duplicate_state = conn_match.execute(
                    "SELECT matched_transaction_id FROM vendor_transactions WHERE id IN (?, ?) "
                    "ORDER BY id",
                    (duplicate_vendor_1, duplicate_vendor_2),
                ).fetchall()
                duplicate_bank_state = conn_match.execute(
                    "SELECT merchant_canonical, notes FROM transactions WHERE transaction_id=?",
                    (duplicate_bank,),
                ).fetchone()
                _check(
                    [row[0] for row in duplicate_state] == [None, None]
                    and tuple(duplicate_bank_state) == ("Before Merchant", "before"),
                    f"vendor matching {entity_key}: duplicate claim partially mutated data",
                )

                # Two independent writers racing for one bank transaction must
                # serialize: exactly one wins and the other sees the durable claim.
                race_bank = f"{vendor_match_prefixes[entity_key]}-bank-race"
                _insert_vendor_match_bank(
                    conn_match, race_bank, "2026-07-11", -73.00, "VENMO RACE 4M"
                )
                race_vendor_1 = _insert_vendor_match_vendor(
                    conn_match,
                    f"{vendor_match_prefixes[entity_key]}-vendor-race-1",
                    "2026-07-11",
                    73.00,
                    "Race One",
                )
                race_vendor_2 = _insert_vendor_match_vendor(
                    conn_match,
                    f"{vendor_match_prefixes[entity_key]}-vendor-race-2",
                    "2026-07-11",
                    73.00,
                    "Race Two",
                )
                conn_match.commit()
                conn_match.close()
                race_barrier = threading.Barrier(2)
                race_results = []
                race_result_lock = threading.Lock()

                def _race_vendor_claim(vendor_id, recipient):
                    race_barrier.wait()
                    try:
                        apply_vendor_matches(
                            entity_key,
                            [{
                                "vendor_id": vendor_id,
                                "bank_txn_id": race_bank,
                                "recipient": recipient,
                                "vendor_type": "venmo",
                                "confidence": 0.80,
                            }],
                        )
                        result_value = ("applied", vendor_id)
                    except ValueError:
                        result_value = ("rejected", vendor_id)
                    with race_result_lock:
                        race_results.append(result_value)

                race_threads = [
                    threading.Thread(
                        target=_race_vendor_claim,
                        args=(race_vendor_1, "Race One"),
                    ),
                    threading.Thread(
                        target=_race_vendor_claim,
                        args=(race_vendor_2, "Race Two"),
                    ),
                ]
                for race_thread in race_threads:
                    race_thread.start()
                for race_thread in race_threads:
                    race_thread.join(timeout=10)
                _check(
                    all(not race_thread.is_alive() for race_thread in race_threads),
                    f"vendor matching {entity_key}: concurrent writers did not finish",
                )
                _check(
                    sorted(result[0] for result in race_results) == ["applied", "rejected"],
                    f"vendor matching {entity_key}: race result was {race_results}",
                )
                conn_match = get_connection(entity_key)
                race_claims = conn_match.execute(
                    "SELECT id, matched_transaction_id FROM vendor_transactions "
                    "WHERE id IN (?, ?) ORDER BY id",
                    (race_vendor_1, race_vendor_2),
                ).fetchall()
                _check(
                    sum(row["matched_transaction_id"] == race_bank for row in race_claims) == 1,
                    f"vendor matching {entity_key}: race produced more than one durable claim",
                )

                # A forced failure after the first match proves the whole batch rolls back.
                rollback_bank_1 = f"{vendor_match_prefixes[entity_key]}-bank-rollback-1"
                rollback_bank_2 = f"{vendor_match_prefixes[entity_key]}-bank-rollback-2"
                _insert_vendor_match_bank(
                    conn_match, rollback_bank_1, "2026-07-12", -81.00, "VENMO ROLLBACK ONE"
                )
                _insert_vendor_match_bank(
                    conn_match, rollback_bank_2, "2026-07-12", -82.00, "VENMO ROLLBACK TWO"
                )
                rollback_vendor_1 = _insert_vendor_match_vendor(
                    conn_match,
                    f"{vendor_match_prefixes[entity_key]}-vendor-rollback-1",
                    "2026-07-12",
                    81.00,
                    "Rollback One",
                )
                rollback_vendor_2 = _insert_vendor_match_vendor(
                    conn_match,
                    f"{vendor_match_prefixes[entity_key]}-vendor-rollback-2",
                    "2026-07-12",
                    82.00,
                    "Rollback Two",
                )
                conn_match.execute(
                    "CREATE TRIGGER vendor_match_4m_abort "
                    "BEFORE UPDATE OF matched_transaction_id ON vendor_transactions "
                    f"WHEN OLD.id={int(rollback_vendor_2)} "
                    "BEGIN SELECT RAISE(ABORT, 'synthetic 4M rollback'); END"
                )
                conn_match.commit()
                conn_match.close()
                try:
                    apply_vendor_matches(
                        entity_key,
                        [
                            {
                                "vendor_id": rollback_vendor_1,
                                "bank_txn_id": rollback_bank_1,
                                "recipient": "Rollback One",
                                "vendor_type": "venmo",
                                "confidence": 0.80,
                            },
                            {
                                "vendor_id": rollback_vendor_2,
                                "bank_txn_id": rollback_bank_2,
                                "recipient": "Rollback Two",
                                "vendor_type": "venmo",
                                "confidence": 0.80,
                            },
                        ],
                    )
                    _check(False, f"vendor matching {entity_key}: forced batch failure should raise")
                except Exception as exc:
                    _check(
                        "synthetic 4M rollback" in str(exc),
                        f"vendor matching {entity_key}: unexpected rollback error {exc}",
                    )
                conn_match = get_connection(entity_key)
                rollback_vendors = conn_match.execute(
                    "SELECT matched_transaction_id FROM vendor_transactions WHERE id IN (?, ?) "
                    "ORDER BY id",
                    (rollback_vendor_1, rollback_vendor_2),
                ).fetchall()
                rollback_banks = conn_match.execute(
                    "SELECT merchant_canonical, notes FROM transactions "
                    "WHERE transaction_id IN (?, ?) ORDER BY transaction_id",
                    (rollback_bank_1, rollback_bank_2),
                ).fetchall()
                _check(
                    [row[0] for row in rollback_vendors] == [None, None]
                    and [tuple(row) for row in rollback_banks]
                    == [("Before Merchant", "before"), ("Before Merchant", "before")],
                    f"vendor matching {entity_key}: failed batch was not rolled back",
                )
                conn_match.execute("DROP TRIGGER vendor_match_4m_abort")
                conn_match.commit()
                conn_match.close()
        finally:
            socket.socket = original_socket

        # Exact cleanup proves the work stayed inside disposable synthetic rows.
        for entity_key in vendor_match_entities:
            conn_match = get_connection(entity_key)
            conn_match.execute(
                "DELETE FROM vendor_transactions WHERE plaid_item_id LIKE 'item-4m-%'"
            )
            conn_match.execute(
                "DELETE FROM transactions WHERE source_filename='vendor-match-4m'"
            )
            conn_match.commit()
            remaining_vendor_match_rows = conn_match.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM vendor_transactions WHERE plaid_item_id LIKE 'item-4m-%'), "
                "(SELECT COUNT(*) FROM transactions WHERE source_filename='vendor-match-4m')"
            ).fetchone()
            _check(
                tuple(remaining_vendor_match_rows) == (0, 0),
                f"vendor matching {entity_key}: exact cleanup failed",
            )
            conn_match.close()
        print("   ✅ Exact, review, unmatched, stale, duplicate, concurrent claim, rollback, all-entity isolation, denied-network, and cleanup passed")

        # ── 8. Route regression tests ────────────────────────────────
        print("\n8. Route regression tests…")

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

            # The normal preview/save HTTP flow must preserve parsed items
            # through its temporary JSON handoff and remove that payload after
            # the save. Amazon and Henry Schein exercise separate parsers and
            # entity databases.
            import web.routes.data_sources as data_sources_routes

            with client.session_transaction() as vendor_session:
                vendor_session["_csrf_token"] = "vendor-line-items-4n-csrf"

            route_cases = [
                (
                    "Personal",
                    "personal",
                    "Amazon",
                    "orders-4n.csv",
                    amazon_csv_text.encode("utf-8"),
                    "ORDER-4N-AMZ",
                ),
                (
                    "BFM",
                    "company",
                    "Henry Schein",
                    "orders-4n.xlsx",
                    hs_buffer.getvalue(),
                    "INV-4N-HS",
                ),
            ]
            for display_entity, entity_key, vendor_name, filename, payload, order_id in route_cases:
                client.set_cookie("entity", display_entity)
                parse_resp = client.post(
                    "/data-sources/parse",
                    data={
                        "_csrf_token": "vendor-line-items-4n-csrf",
                        "vendor": vendor_name,
                        "file": (io.BytesIO(payload), filename),
                    },
                    content_type="multipart/form-data",
                )
                _check(parse_resp.status_code == 200,
                       f"vendor line items route: {vendor_name} preview should render")
                with client.session_transaction() as vendor_session:
                    temp_key = vendor_session.get("vendor_temp_key")
                _check(temp_key is not None,
                       f"vendor line items route: {vendor_name} preview should retain a temp key")
                temp_path = Path(data_sources_routes._TEMP_DIR) / f"{temp_key}.json"
                _check(temp_path.exists(),
                       f"vendor line items route: {vendor_name} preview payload missing")

                save_resp = client.post(
                    "/data-sources/save",
                    data={"_csrf_token": "vendor-line-items-4n-csrf"},
                    follow_redirects=False,
                )
                _check(save_resp.status_code == 302,
                       f"vendor line items route: {vendor_name} save should redirect")
                _check(not temp_path.exists(),
                       f"vendor line items route: {vendor_name} temp payload should be deleted")
                with client.session_transaction() as vendor_session:
                    _check("vendor_temp_key" not in vendor_session,
                           f"vendor line items route: {vendor_name} session key should be consumed")

                conn_route_vendor = get_connection(entity_key)
                route_counts = conn_route_vendor.execute(
                    "SELECT COUNT(DISTINCT ao.id), COUNT(li.id) "
                    "FROM amazon_orders ao "
                    "LEFT JOIN order_line_items li ON li.amazon_order_id=ao.id "
                    "WHERE ao.order_id=?", (order_id,)
                ).fetchone()
                _check(tuple(route_counts) == (1, 2),
                       f"vendor line items route: {vendor_name} should save one parent and two children")
                conn_route_vendor.execute(
                    "DELETE FROM order_line_items WHERE amazon_order_id IN ("
                    "SELECT id FROM amazon_orders WHERE order_id=?)", (order_id,)
                )
                conn_route_vendor.execute(
                    "DELETE FROM amazon_orders WHERE order_id=?", (order_id,)
                )
                conn_route_vendor.commit()
                conn_route_vendor.close()

            client.set_cookie("entity", "Personal")

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

        # ── 8a2. Stored-APR locked payoff truthfulness ─────────────
        print("\n8a2. Stored-APR locked payoff truthfulness…")
        import json as planning_json
        from web.routes import short_term_planning as short_term_planning_routes

        apr_fixture = {}

        def _locked_goal_row(entity_key, goal_id):
            locked_conn = get_connection(entity_key)
            try:
                row = locked_conn.execute(
                    "SELECT strategy, monthly_amount_cents, target_date, ai_plan "
                    "FROM short_term_goals WHERE id = ?",
                    (goal_id,),
                ).fetchone()
                return tuple(row) if row else None
            finally:
                locked_conn.close()

        def _expected_schedule_row(accounts, monthly_extra, strategy):
            timeline = short_term_planning_routes._compute_payoff_timeline(
                accounts, monthly_extra, strategy
            )
            _check(timeline, "locked payoff: expected a non-empty synthetic timeline")
            first = timeline[0]
            parts = ["| 1"]
            for account in accounts:
                balance = first["accounts"].get(account["name"], 0)
                parts.append("$%s" % "{:,.0f}".format(balance / 100))
            parts.append("$%s" % "{:,.0f}".format(first["total_cents"] / 100))
            parts.append(
                "$%s" % "{:,.0f}".format(
                    first["cumulative_interest_cents"] / 100
                )
            )
            return timeline, " | ".join(parts) + " |"

        for entity_key, entity_display in (
            ("personal", "Personal"),
            ("company", "BFM"),
        ):
            low_name = f"APR Low {entity_key}"
            high_name = f"APR High {entity_key}"
            setup_conn = get_connection(entity_key)
            try:
                setup_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, "
                    "payment_amount_cents, apr_bps, sort_order) "
                    "VALUES (?, 100000, 'manual', 'credit_card', 2500, 999, 801)",
                    (low_name,),
                )
                setup_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, "
                    "payment_amount_cents, apr_bps, sort_order) "
                    "VALUES (?, 100000, 'manual', 'credit_card', 2500, 2999, 802)",
                    (high_name,),
                )
                goal_id = setup_conn.execute(
                    "INSERT INTO short_term_goals "
                    "(name, goal_type, target_date, strategy, monthly_amount_cents, "
                    "linked_accounts, status, ai_plan) "
                    "VALUES (?, 'debt_payoff', '2030-01-01', 'snowball', 3300, ?, "
                    "'active', 'Prior locked plan')",
                    (
                        f"Stored APR {entity_key}",
                        planning_json.dumps([low_name, high_name]),
                    ),
                ).lastrowid
                setup_conn.commit()
            finally:
                setup_conn.close()
            apr_fixture[entity_key] = {
                "display": entity_display,
                "low": low_name,
                "high": high_name,
                "goal": goal_id,
            }

        with app.test_client() as apr_client, patch(
            "socket.create_connection",
            side_effect=AssertionError("locked payoff attempted outbound networking"),
        ) as apr_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("locked payoff attempted outbound networking"),
        ) as apr_socket_connect:
            for entity_key in ("personal", "company"):
                fixture = apr_fixture[entity_key]
                apr_client.set_cookie("entity", fixture["display"])
                response = apr_client.post(
                    f"/planning/short-term/goals/{fixture['goal']}/lock-plan",
                    data={
                        "strategy": "avalanche",
                        "monthly_amount": "100",
                        "target_date": "2029-12-31",
                        "narrative": f"Stored APR avalanche {entity_key}",
                    },
                )
                _check(
                    response.status_code == 302,
                    f"locked payoff {entity_key}: avalanche lock should redirect",
                )
                expected_accounts = [
                    {
                        "name": fixture["low"],
                        "balance_cents": 100000,
                        "rate_bps": 999,
                        "min_payment_cents": 2500,
                    },
                    {
                        "name": fixture["high"],
                        "balance_cents": 100000,
                        "rate_bps": 2999,
                        "min_payment_cents": 2500,
                    },
                ]
                timeline, expected_row = _expected_schedule_row(
                    expected_accounts, 10000, "avalanche"
                )
                _check(
                    timeline[0]["accounts"][fixture["high"]]
                    < timeline[0]["accounts"][fixture["low"]],
                    f"locked payoff {entity_key}: avalanche should target the higher stored APR first",
                )
                _check(
                    timeline[0]["accounts"][fixture["low"]] == 98332
                    and timeline[0]["accounts"][fixture["high"]] == 89999
                    and timeline[0]["cumulative_interest_cents"] == 3332,
                    f"locked payoff {entity_key}: avalanche month one should reconcile to stored APR cents",
                )
                locked = _locked_goal_row(entity_key, fixture["goal"])
                _check(
                    locked is not None
                    and locked[0] == "avalanche"
                    and locked[1] == 10000
                    and locked[2] == "2029-12-31"
                    and locked[3].startswith(f"Stored APR avalanche {entity_key}")
                    and expected_row in locked[3],
                    f"locked payoff {entity_key}: saved avalanche inputs and schedule should reconcile",
                )

            personal_fixture = apr_fixture["personal"]
            personal_conn = get_connection("personal")
            try:
                personal_conn.execute(
                    "UPDATE account_balances SET balance_cents = 200000, apr_bps = 999 "
                    "WHERE account_name = ?",
                    (personal_fixture["low"],),
                )
                personal_conn.execute(
                    "UPDATE account_balances SET balance_cents = 50000, apr_bps = 2999 "
                    "WHERE account_name = ?",
                    (personal_fixture["high"],),
                )
                personal_conn.commit()
            finally:
                personal_conn.close()

            apr_client.set_cookie("entity", "Personal")
            response = apr_client.post(
                f"/planning/short-term/goals/{personal_fixture['goal']}/lock-plan",
                data={
                    "strategy": "snowball",
                    "monthly_amount": "100",
                    "target_date": "2029-11-30",
                    "narrative": "Stored APR snowball personal",
                },
            )
            _check(response.status_code == 302, "locked payoff: snowball lock should redirect")
            snowball_accounts = [
                {
                    "name": personal_fixture["low"],
                    "balance_cents": 200000,
                    "rate_bps": 999,
                    "min_payment_cents": 4000,
                },
                {
                    "name": personal_fixture["high"],
                    "balance_cents": 50000,
                    "rate_bps": 2999,
                    "min_payment_cents": 2500,
                },
            ]
            snowball_timeline, snowball_row = _expected_schedule_row(
                snowball_accounts, 10000, "snowball"
            )
            _check(
                snowball_timeline[0]["accounts"][personal_fixture["high"]]
                < snowball_timeline[0]["accounts"][personal_fixture["low"]],
                "locked payoff: snowball should target the smaller balance independently of APR",
            )
            _check(
                snowball_timeline[0]["accounts"][personal_fixture["low"]] == 197665
                and snowball_timeline[0]["accounts"][personal_fixture["high"]] == 38750
                and snowball_timeline[0]["cumulative_interest_cents"] == 2915,
                "locked payoff: snowball month one should reconcile independently to exact cents",
            )
            snowball_locked = _locked_goal_row("personal", personal_fixture["goal"])
            _check(
                snowball_locked is not None
                and snowball_locked[0] == "snowball"
                and snowball_locked[1] == 10000
                and snowball_row in snowball_locked[3],
                "locked payoff: saved snowball inputs and schedule should reconcile",
            )

            for unavailable_apr in (None, -1):
                invalid_conn = get_connection("personal")
                try:
                    invalid_conn.execute(
                        "UPDATE account_balances SET apr_bps = ? WHERE account_name = ?",
                        (unavailable_apr, personal_fixture["low"]),
                    )
                    invalid_conn.commit()
                finally:
                    invalid_conn.close()
                before_rejection = _locked_goal_row("personal", personal_fixture["goal"])
                rejected = apr_client.post(
                    f"/planning/short-term/goals/{personal_fixture['goal']}/lock-plan",
                    data={
                        "strategy": "avalanche",
                        "monthly_amount": "777",
                        "target_date": "2035-05-05",
                        "narrative": "Must not persist",
                    },
                    follow_redirects=True,
                )
                _check(
                    rejected.status_code == 200
                    and "Set a valid APR for every linked card in Cash Flow"
                    in rejected.get_data(as_text=True),
                    "locked payoff: unavailable APR should return controlled Cash Flow guidance",
                )
                _check(
                    _locked_goal_row("personal", personal_fixture["goal"])
                    == before_rejection,
                    "locked payoff: unavailable APR rejection should leave the prior plan unchanged",
                )

            zero_conn = get_connection("personal")
            try:
                zero_conn.execute(
                    "UPDATE account_balances SET balance_cents = 100000, apr_bps = 0 "
                    "WHERE account_name = ?",
                    (personal_fixture["low"],),
                )
                zero_conn.execute(
                    "UPDATE account_balances SET balance_cents = 100000, apr_bps = 2999 "
                    "WHERE account_name = ?",
                    (personal_fixture["high"],),
                )
                zero_conn.commit()
            finally:
                zero_conn.close()
            zero_response = apr_client.post(
                f"/planning/short-term/goals/{personal_fixture['goal']}/lock-plan",
                data={
                    "strategy": "avalanche",
                    "monthly_amount": "125",
                    "target_date": "2029-10-31",
                    "narrative": "Known zero APR remains valid",
                },
            )
            _check(zero_response.status_code == 302, "locked payoff: known zero APR should remain valid")
            zero_accounts = [
                {
                    "name": personal_fixture["low"],
                    "balance_cents": 100000,
                    "rate_bps": 0,
                    "min_payment_cents": 2500,
                },
                {
                    "name": personal_fixture["high"],
                    "balance_cents": 100000,
                    "rate_bps": 2999,
                    "min_payment_cents": 2500,
                },
            ]
            _, zero_row = _expected_schedule_row(zero_accounts, 12500, "avalanche")
            zero_locked = _locked_goal_row("personal", personal_fixture["goal"])
            _check(
                zero_locked is not None
                and zero_locked[1] == 12500
                and zero_row in zero_locked[3],
                "locked payoff: known zero APR should persist a reconciled schedule",
            )

            before_ll = _database_snapshot("luxelegacy")
            apr_client.set_cookie("entity", "LL")
            denied_ll = apr_client.post(
                "/planning/short-term/goals/999999/lock-plan",
                data={"strategy": "avalanche", "monthly_amount": "999"},
            )
            _check(
                denied_ll.status_code == 302
                and denied_ll.headers.get("Location", "").endswith("/"),
                "locked payoff LL: route should remain denied before its handler",
            )
            _check(
                _database_snapshot("luxelegacy") == before_ll,
                "locked payoff LL: denied request should leave the database unchanged",
            )
            apr_create_connection.assert_not_called()
            apr_socket_connect.assert_not_called()

        for entity_key in ("personal", "company"):
            fixture = apr_fixture[entity_key]
            cleanup_conn = get_connection(entity_key)
            try:
                cleanup_conn.execute(
                    "DELETE FROM short_term_goals WHERE id = ?", (fixture["goal"],)
                )
                cleanup_conn.execute(
                    "DELETE FROM account_balances WHERE account_name IN (?, ?)",
                    (fixture["low"], fixture["high"]),
                )
                cleanup_conn.commit()
                leftovers = cleanup_conn.execute(
                    "SELECT "
                    "(SELECT COUNT(*) FROM short_term_goals WHERE id = ?) + "
                    "(SELECT COUNT(*) FROM account_balances WHERE account_name IN (?, ?))",
                    (fixture["goal"], fixture["low"], fixture["high"]),
                ).fetchone()[0]
            finally:
                cleanup_conn.close()
            _check(leftovers == 0, f"locked payoff {entity_key}: synthetic rows should clean up exactly")

        print("   ✅ Stored APRs, explicit rejection, zero APR, schedule truth, isolation, denied-network, and cleanup passed")

        # ── 8a3. Snapshot note preservation ────────────────────────
        print("\n8a3. Snapshot note preservation…")
        from datetime import date as real_date

        class _SnapshotDate(real_date):
            current = real_date(2026, 7, 20)

            @classmethod
            def today(cls):
                return cls.current

        def _snapshot_rows(entity_key, goal_id):
            snapshot_conn = get_connection(entity_key)
            try:
                return [
                    tuple(row)
                    for row in snapshot_conn.execute(
                        "SELECT id, snapshot_date, balance_cents, note, created_at "
                        "FROM goal_snapshots WHERE goal_id = ? ORDER BY snapshot_date",
                        (goal_id,),
                    ).fetchall()
                ]
            finally:
                snapshot_conn.close()

        snapshot_fixtures = {}
        for entity_key, entity_display in (
            ("personal", "Personal"),
            ("company", "BFM"),
        ):
            account_name = f"4T Snapshot Account {entity_key}"
            setup_conn = get_connection(entity_key)
            try:
                setup_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, sort_order) "
                    "VALUES (?, 10000, 'manual', 'bank', 804)",
                    (account_name,),
                )
                goal_id = setup_conn.execute(
                    "INSERT INTO short_term_goals "
                    "(name, goal_type, linked_accounts, status) "
                    "VALUES (?, 'savings', ?, 'active')",
                    (
                        f"4T Snapshot Goal {entity_key}",
                        planning_json.dumps([account_name]),
                    ),
                ).lastrowid
                setup_conn.commit()
            finally:
                setup_conn.close()
            snapshot_fixtures[entity_key] = {
                "display": entity_display,
                "account": account_name,
                "goal": goal_id,
            }

        with app.test_client() as snapshot_client, patch.object(
            short_term_planning_routes, "date", _SnapshotDate
        ), patch(
            "socket.create_connection",
            side_effect=AssertionError("snapshot persistence attempted outbound networking"),
        ) as snapshot_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("snapshot persistence attempted outbound networking"),
        ) as snapshot_socket_connect:
            for entity_key in ("personal", "company"):
                fixture = snapshot_fixtures[entity_key]
                snapshot_client.set_cookie("entity", fixture["display"])

                first_auto = snapshot_client.get("/planning/short-term/")
                _check(
                    first_auto.status_code == 200,
                    f"snapshot {entity_key}: initial automatic snapshot should render",
                )
                first_rows = _snapshot_rows(entity_key, fixture["goal"])
                _check(
                    len(first_rows) == 1
                    and first_rows[0][1:4] == ("2026-07-20", 10000, None),
                    f"snapshot {entity_key}: initial automatic snapshot should insert today's balance",
                )
                original_id, original_created_at = first_rows[0][0], first_rows[0][4]

                update_conn = get_connection(entity_key)
                try:
                    update_conn.execute(
                        "UPDATE account_balances SET balance_cents = 20000 "
                        "WHERE account_name = ?",
                        (fixture["account"],),
                    )
                    update_conn.commit()
                finally:
                    update_conn.close()
                manual = snapshot_client.post(
                    f"/planning/short-term/goals/{fixture['goal']}/snapshot",
                    data={"note": "First 4T manual review"},
                )
                _check(
                    manual.status_code == 302,
                    f"snapshot {entity_key}: manual review should redirect",
                )
                manual_row = _snapshot_rows(entity_key, fixture["goal"])[0]
                _check(
                    manual_row
                    == (
                        original_id,
                        "2026-07-20",
                        20000,
                        "First 4T manual review",
                        original_created_at,
                    ),
                    f"snapshot {entity_key}: manual upsert should preserve identity and replace note",
                )

                update_conn = get_connection(entity_key)
                try:
                    update_conn.execute(
                        "UPDATE account_balances SET balance_cents = 30000 "
                        "WHERE account_name = ?",
                        (fixture["account"],),
                    )
                    update_conn.commit()
                finally:
                    update_conn.close()
                repeated_auto = snapshot_client.get("/planning/short-term/")
                _check(
                    repeated_auto.status_code == 200,
                    f"snapshot {entity_key}: repeated automatic snapshot should render",
                )
                repeated_row = _snapshot_rows(entity_key, fixture["goal"])[0]
                _check(
                    repeated_row
                    == (
                        original_id,
                        "2026-07-20",
                        30000,
                        "First 4T manual review",
                        original_created_at,
                    ),
                    f"snapshot {entity_key}: automatic update should preserve identity and manual note",
                )

                update_conn = get_connection(entity_key)
                try:
                    update_conn.execute(
                        "UPDATE account_balances SET balance_cents = 40000 "
                        "WHERE account_name = ?",
                        (fixture["account"],),
                    )
                    update_conn.commit()
                finally:
                    update_conn.close()
                snapshot_client.get("/planning/short-term/")
                second_auto_row = _snapshot_rows(entity_key, fixture["goal"])[0]
                _check(
                    second_auto_row
                    == (
                        original_id,
                        "2026-07-20",
                        40000,
                        "First 4T manual review",
                        original_created_at,
                    ),
                    f"snapshot {entity_key}: repeated automatic updates should remain identity stable",
                )

                replacement = snapshot_client.post(
                    f"/planning/short-term/goals/{fixture['goal']}/snapshot",
                    data={"note": "Revised 4T manual review"},
                )
                _check(
                    replacement.status_code == 302,
                    f"snapshot {entity_key}: later manual replacement should redirect",
                )
                replacement_row = _snapshot_rows(entity_key, fixture["goal"])[0]
                _check(
                    replacement_row
                    == (
                        original_id,
                        "2026-07-20",
                        40000,
                        "Revised 4T manual review",
                        original_created_at,
                    ),
                    f"snapshot {entity_key}: later manual review should intentionally replace the note",
                )

                empty = snapshot_client.post(
                    f"/planning/short-term/goals/{fixture['goal']}/snapshot",
                    data={"note": "   "},
                )
                _check(
                    empty.status_code == 302,
                    f"snapshot {entity_key}: explicit empty review should redirect",
                )
                empty_row = _snapshot_rows(entity_key, fixture["goal"])[0]
                review_conn = get_connection(entity_key)
                try:
                    review_goal_row = review_conn.execute(
                        "SELECT * FROM short_term_goals WHERE id = ?",
                        (fixture["goal"],),
                    ).fetchone()
                    review_goal = dict(review_goal_row)
                    review_needed = short_term_planning_routes._check_monthly_review(
                        review_conn, review_goal
                    )
                finally:
                    review_conn.close()
                _check(
                    empty_row
                    == (
                        original_id,
                        "2026-07-20",
                        40000,
                        None,
                        original_created_at,
                    )
                    and review_needed,
                    f"snapshot {entity_key}: empty manual note should preserve identity and remain review-incomplete",
                )

                restored = snapshot_client.post(
                    f"/planning/short-term/goals/{fixture['goal']}/snapshot",
                    data={"note": "Final July 4T review"},
                )
                _check(
                    restored.status_code == 302,
                    f"snapshot {entity_key}: final July note should redirect",
                )

                update_conn = get_connection(entity_key)
                try:
                    update_conn.execute(
                        "UPDATE account_balances SET balance_cents = 50000 "
                        "WHERE account_name = ?",
                        (fixture["account"],),
                    )
                    update_conn.commit()
                finally:
                    update_conn.close()
                _SnapshotDate.current = real_date(2026, 8, 1)
                month_transition = snapshot_client.get("/planning/short-term/")
                _check(
                    month_transition.status_code == 200,
                    f"snapshot {entity_key}: month transition should render",
                )
                transition_rows = _snapshot_rows(entity_key, fixture["goal"])
                _check(
                    len(transition_rows) == 2
                    and transition_rows[0]
                    == (
                        original_id,
                        "2026-07-20",
                        40000,
                        "Final July 4T review",
                        original_created_at,
                    )
                    and transition_rows[1][0] != original_id
                    and transition_rows[1][1:4] == ("2026-08-01", 50000, None),
                    f"snapshot {entity_key}: new month should preserve July and insert August",
                )
                _SnapshotDate.current = real_date(2026, 7, 20)

            before_ll_snapshots = _database_snapshot("luxelegacy")
            snapshot_client.set_cookie("entity", "LL")
            denied_ll_snapshot = snapshot_client.post(
                "/planning/short-term/goals/999999/snapshot",
                data={"note": "Denied 4T note"},
            )
            _check(
                denied_ll_snapshot.status_code == 302
                and denied_ll_snapshot.headers.get("Location", "").endswith("/"),
                "snapshot LL: direct manual snapshot should remain denied",
            )
            _check(
                _database_snapshot("luxelegacy") == before_ll_snapshots,
                "snapshot LL: denied request should leave the database unchanged",
            )
            snapshot_create_connection.assert_not_called()
            snapshot_socket_connect.assert_not_called()

        for entity_key in ("personal", "company"):
            fixture = snapshot_fixtures[entity_key]
            cleanup_conn = get_connection(entity_key)
            try:
                cleanup_conn.execute(
                    "DELETE FROM short_term_goals WHERE id = ?", (fixture["goal"],)
                )
                cleanup_conn.execute(
                    "DELETE FROM account_balances WHERE account_name = ?",
                    (fixture["account"],),
                )
                cleanup_conn.commit()
                leftovers = cleanup_conn.execute(
                    "SELECT "
                    "(SELECT COUNT(*) FROM short_term_goals WHERE id = ?) + "
                    "(SELECT COUNT(*) FROM goal_snapshots WHERE goal_id = ?) + "
                    "(SELECT COUNT(*) FROM account_balances WHERE account_name = ?)",
                    (fixture["goal"], fixture["goal"], fixture["account"]),
                ).fetchone()[0]
            finally:
                cleanup_conn.close()
            _check(
                leftovers == 0,
                f"snapshot {entity_key}: synthetic rows should clean up exactly",
            )

        print("   ✅ Identity-stable auto/manual upserts, note replacement, month transition, isolation, denied-network, and cleanup passed")

        # ── 8a4. Negative asset appreciation truthfulness ──────────
        print("\n8a4. Negative asset appreciation truthfulness…")
        from web.routes import planning as planning_routes

        projection_settings = {
            "inflation_rate": 300,
            "current_age": 50,
            "custom_milestone": 55,
            "birth_date": None,
        }
        projection_items = {
            "assets": [
                {
                    "name": "4U Depreciating Asset",
                    "current_value_cents": 1_000_000,
                    "annual_rate_bps": -1000,
                    "monthly_contrib_cents": 0,
                },
                {
                    "name": "4U Depreciating Contributed Asset",
                    "current_value_cents": 1_000_000,
                    "annual_rate_bps": -1000,
                    "monthly_contrib_cents": 10_000,
                },
                {
                    "name": "4U Zero Rate Asset",
                    "current_value_cents": 1_000_000,
                    "annual_rate_bps": 0,
                    "monthly_contrib_cents": 10_000,
                },
                {
                    "name": "4U Appreciating Asset",
                    "current_value_cents": 1_000_000,
                    "annual_rate_bps": 500,
                    "monthly_contrib_cents": 10_000,
                },
            ],
            "liabilities": [],
        }
        projected = planning_routes._compute_projections(
            projection_items, projection_settings
        )
        projection_by_name = {asset["name"]: asset for asset in projected["assets"]}
        milestone = 55
        inflation_factor = 1.03 ** 5
        negative_growth = 0.9 ** 5
        positive_growth = 1.05 ** 5
        expected_negative = round(10_000 * negative_growth / inflation_factor * 100)
        expected_negative_contrib = round(
            (
                10_000 * negative_growth
                + 1_200 * (negative_growth - 1) / -0.10
            )
            / inflation_factor
            * 100
        )
        expected_zero = round((10_000 + 1_200 * 5) / inflation_factor * 100)
        expected_positive = round(
            (
                10_000 * positive_growth
                + 1_200 * (positive_growth - 1) / 0.05
            )
            / inflation_factor
            * 100
        )
        _check(
            projection_by_name["4U Depreciating Asset"]["projections"][milestone]
            == expected_negative
            < 1_000_000,
            "negative appreciation: ordinary negative rate should compound downward with inflation",
        )
        _check(
            projection_by_name["4U Depreciating Contributed Asset"]["projections"][milestone]
            == expected_negative_contrib,
            "negative appreciation: contributions should use the same end-of-year compounding contract",
        )
        _check(
            projection_by_name["4U Zero Rate Asset"]["projections"][milestone]
            == expected_zero,
            "negative appreciation: zero rate should retain the linear contribution path",
        )
        _check(
            projection_by_name["4U Appreciating Asset"]["projections"][milestone]
            == expected_positive,
            "negative appreciation: positive appreciation and contributions should remain unchanged",
        )
        direct_summary = planning_routes._compute_summary(projected, [milestone])
        _check(
            direct_summary[milestone]["assets_cents"]
            == sum(asset["projections"][milestone] for asset in projected["assets"])
            and direct_summary[milestone]["net_worth_cents"]
            == direct_summary[milestone]["assets_cents"],
            "negative appreciation: direct asset and net-worth summaries should reconcile",
        )

        def _planning_rows(entity_key):
            projection_conn = get_connection(entity_key)
            try:
                return [
                    tuple(row)
                    for row in projection_conn.execute(
                        "SELECT id, item_type, name, current_value_cents, annual_rate_bps, "
                        "monthly_contrib_cents, monthly_payment_cents, source, "
                        "cashflow_account_name, sort_order, created_at, updated_at "
                        "FROM planning_items ORDER BY id"
                    ).fetchall()
                ]
            finally:
                projection_conn.close()

        projection_baseline = {
            entity_key: _planning_rows(entity_key)
            for entity_key in ("personal", "company")
        }
        projection_fixture_ids = {}
        for entity_key, fixture in (
            (
                "personal",
                ("4U Personal Depreciating Asset", 1_000_000, -1000),
            ),
            (
                "company",
                ("4U Demo Equipment", 8_500_000, -1500),
            ),
        ):
            projection_conn = get_connection(entity_key)
            try:
                fixture_id = projection_conn.execute(
                    "INSERT INTO planning_items "
                    "(item_type, name, current_value_cents, annual_rate_bps, source, sort_order) "
                    "VALUES ('asset', ?, ?, ?, 'manual', 804)",
                    fixture,
                ).lastrowid
                projection_conn.commit()
            finally:
                projection_conn.close()
            projection_fixture_ids[entity_key] = fixture_id

        fixed_route_settings = {
            "inflation_rate": 0,
            "current_age": 50,
            "custom_milestone": 55,
            "birth_date": None,
        }
        expected_personal = round(1_000_000 * (0.9 ** 5))
        expected_equipment = round(8_500_000 * (0.85 ** 5))
        captured_context = {}

        def _capture_planning_context(_template_name, **context):
            captured_context.update(context)
            return "planning context captured"

        before_ll_projection = _database_snapshot("luxelegacy")
        with app.test_client() as projection_client, patch.object(
            planning_routes, "_get_settings", return_value=fixed_route_settings
        ), patch(
            "socket.create_connection",
            side_effect=AssertionError("negative appreciation attempted outbound networking"),
        ) as projection_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("negative appreciation attempted outbound networking"),
        ) as projection_socket_connect:
            projection_client.set_cookie("entity", "Personal")
            rendered_projection = projection_client.get("/planning/")
            rendered_body = rendered_projection.get_data(as_text=True)
            _check(
                rendered_projection.status_code == 200
                and "4U Personal Depreciating" in rendered_body
                and "4U Demo" in rendered_body
                and "depreciation" in rendered_body,
                "negative appreciation: Personal route should render both entity projections and depreciation labels",
            )

            with patch.object(
                planning_routes,
                "render_template",
                side_effect=_capture_planning_context,
            ):
                captured_projection = projection_client.get("/planning/")
            _check(
                captured_projection.status_code == 200,
                "negative appreciation: route context capture should succeed",
            )

            personal_asset = next(
                asset
                for asset in captured_context["primary"]["assets"]
                if asset["name"] == "4U Personal Depreciating Asset"
            )
            equipment_asset = next(
                asset
                for asset in captured_context["cross_sections"][0]["assets"]
                if asset["name"] == "4U Demo Equipment"
            )
            _check(
                personal_asset["projections"][milestone] == expected_personal,
                "negative appreciation: Personal item projection should match exact negative compounding",
            )
            _check(
                equipment_asset["projections"][milestone] == expected_equipment
                < equipment_asset["current_value_cents"],
                "negative appreciation: demo-equivalent Equipment should decline at negative 15 percent",
            )
            personal_summary = captured_context["primary"]["summary"][milestone]
            company_summary = captured_context["cross_sections"][0]["summary"][milestone]
            combined_summary = captured_context["combined"][milestone]
            _check(
                personal_summary["assets_cents"]
                == sum(
                    asset["projections"][milestone]
                    for asset in captured_context["primary"]["assets"]
                )
                and company_summary["assets_cents"]
                == sum(
                    asset["projections"][milestone]
                    for asset in captured_context["cross_sections"][0]["assets"]
                ),
                "negative appreciation: Personal and BFM asset summaries should reconcile to item projections",
            )
            _check(
                combined_summary["net_worth_cents"]
                == personal_summary["net_worth_cents"]
                + company_summary["net_worth_cents"],
                "negative appreciation: combined net worth should reconcile to Personal and BFM summaries",
            )

            projection_client.set_cookie("entity", "BFM")
            bfm_projection = projection_client.get("/planning/")
            _check(
                bfm_projection.status_code == 200
                and "4U Personal Depreciating" in bfm_projection.get_data(as_text=True)
                and "4U Demo" in bfm_projection.get_data(as_text=True),
                "negative appreciation: BFM route should preserve shared Personal/BFM visibility",
            )

            projection_client.set_cookie("entity", "LL")
            denied_ll_projection = projection_client.get("/planning/")
            _check(
                denied_ll_projection.status_code == 302
                and denied_ll_projection.headers.get("Location", "").endswith("/"),
                "negative appreciation: Luxe Legacy should remain denied before projection handling",
            )
            _check(
                _database_snapshot("luxelegacy") == before_ll_projection,
                "negative appreciation: denied Luxe Legacy request should leave its database unchanged",
            )
            projection_create_connection.assert_not_called()
            projection_socket_connect.assert_not_called()

        for entity_key, fixture_id in projection_fixture_ids.items():
            projection_conn = get_connection(entity_key)
            try:
                projection_conn.execute(
                    "DELETE FROM planning_items WHERE id = ?", (fixture_id,)
                )
                projection_conn.commit()
            finally:
                projection_conn.close()
            _check(
                _planning_rows(entity_key) == projection_baseline[entity_key],
                f"negative appreciation {entity_key}: synthetic planning rows should clean up exactly",
            )

        print("   ✅ Negative, zero, positive, contribution, inflation, summary, combined, isolation, denied-network, and cleanup behavior passed")

        # ── 8a5. Weekly date and bill truthfulness ─────────────────
        print("\n8a5. Weekly date and bill truthfulness…")
        from web.routes import weekly as weekly_routes

        class _WeeklyDate(real_date):
            current = real_date(2026, 7, 20)

            @classmethod
            def today(cls):
                return cls.current

        weekly_tables = (
            "transactions",
            "budget_items",
            "account_balances",
            "manual_recurring",
            "action_items",
            "payroll_schedule",
        )

        def _weekly_counts(entity_key):
            weekly_conn = get_connection(entity_key)
            try:
                return tuple(
                    weekly_conn.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    ).fetchone()[0]
                    for table in weekly_tables
                )
            finally:
                weekly_conn.close()

        weekly_baselines = {
            entity_key: _weekly_counts(entity_key)
            for entity_key in ("personal", "company")
        }
        weekly_fixtures = {}

        for entity_key, entity_display in (
            ("personal", "Personal"),
            ("company", "BFM"),
        ):
            fixture_conn = get_connection(entity_key)
            try:
                original_budget_row = fixture_conn.execute(
                    "SELECT * FROM budget_items WHERE category='Food'"
                ).fetchone()
                original_payroll_row = fixture_conn.execute(
                    "SELECT * FROM payroll_schedule WHERE id=1"
                ).fetchone()
                if original_budget_row:
                    fixture_conn.execute(
                        "UPDATE budget_items SET monthly_budget_cents=310000, "
                        "is_per_payroll=0, per_payroll_cents=NULL WHERE category='Food'"
                    )
                else:
                    fixture_conn.execute(
                        "INSERT INTO budget_items "
                        "(category, monthly_budget_cents, budget_section, is_per_payroll) "
                        "VALUES ('Food', 310000, 'focus', 0)"
                    )

                recurring_account = f"4V Recurring {entity_key}"
                scheduled_card = f"4V Scheduled {entity_key}"
                missing_card = f"4V Missing {entity_key}"
                zero_card = f"4V Zero Balance {entity_key}"
                recurring_account_id = fixture_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, sort_order) "
                    "VALUES (?, 250000, 'manual', 'bank', 850)",
                    (recurring_account,),
                ).lastrowid
                fixture_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, "
                    "credit_limit_cents, payment_due_day, payment_amount_cents, sort_order) "
                    "VALUES (?, 120000, 'manual', 'credit_card', 500000, 11, 5000, 851)",
                    (scheduled_card,),
                )
                fixture_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, "
                    "credit_limit_cents, payment_due_day, payment_amount_cents, sort_order) "
                    "VALUES (?, 50000, 'manual', 'credit_card', 200000, 12, 0, 852)",
                    (missing_card,),
                )
                fixture_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, "
                    "credit_limit_cents, payment_due_day, payment_amount_cents, sort_order) "
                    "VALUES (?, 0, 'manual', 'credit_card', 100000, 13, 2000, 853)",
                    (zero_card,),
                )
                fixture_conn.execute(
                    "INSERT INTO manual_recurring "
                    "(account_id, merchant, amount_cents, day_of_month) "
                    "VALUES (?, ?, 2000, 10)",
                    (recurring_account_id, f"4V Manual {entity_key}"),
                )
                fixture_conn.execute(
                    "INSERT INTO action_items "
                    "(title, status, due_date, is_recurring, sort_order) "
                    "VALUES (?, 'pending', '14', 0, 850)",
                    (f"4V Action {entity_key}",),
                )

                synthetic_transactions = (
                    ("auto-1", "2026-01-12", -30.00, -3000, f"4V Auto {entity_key}"),
                    ("auto-2", "2026-01-26", -30.00, -3000, f"4V Auto {entity_key}"),
                    ("feb-mtd", "2026-02-01", -100.00, -10000, "4V February MTD"),
                    ("feb-week", "2026-02-10", -50.00, -5000, "4V February Week"),
                    ("june", "2026-06-30", -60.00, -6000, "4V June Boundary"),
                    ("july", "2026-07-01", -70.00, -7000, "4V July Boundary"),
                )
                transaction_ids = []
                for suffix, txn_date, amount, amount_cents, merchant in synthetic_transactions:
                    txn_id = f"synthetic-4v-{entity_key}-{suffix}"
                    transaction_ids.append(txn_id)
                    fixture_conn.execute(
                        "INSERT INTO transactions "
                        "(transaction_id, date, description_raw, merchant_canonical, "
                        "amount, amount_cents, account, category, source_filename, imported_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, 'Food', 'synthetic-4v', "
                        "'2026-07-21T00:00:00+00:00')",
                        (
                            txn_id,
                            txn_date,
                            merchant,
                            merchant,
                            amount,
                            amount_cents,
                            recurring_account,
                        ),
                    )

                if entity_key == "company":
                    fixture_conn.execute("DELETE FROM payroll_schedule WHERE id=1")
                    fixture_conn.execute(
                        "INSERT INTO payroll_schedule "
                        "(id, anchor_date, cadence_days, pay_dow) "
                        "VALUES (1, '2026-02-13', 14, 4)"
                    )

                fixture_conn.commit()
                weekly_fixtures[entity_key] = {
                    "display": entity_display,
                    "original_budget": (
                        dict(original_budget_row) if original_budget_row else None
                    ),
                    "original_payroll": (
                        dict(original_payroll_row) if original_payroll_row else None
                    ),
                    "accounts": (
                        recurring_account,
                        scheduled_card,
                        missing_card,
                        zero_card,
                    ),
                    "transaction_ids": tuple(transaction_ids),
                }
            finally:
                fixture_conn.close()

        captured_weekly_context = {}

        def _capture_weekly_context(_template_name, **context):
            captured_weekly_context.clear()
            captured_weekly_context.update(context)
            return "weekly context captured"

        before_ll_weekly = _database_snapshot("luxelegacy")
        with app.test_client() as weekly_client, patch.object(
            weekly_routes, "date", _WeeklyDate
        ), patch(
            "socket.create_connection",
            side_effect=AssertionError("weekly 4V attempted outbound networking"),
        ) as weekly_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("weekly 4V attempted outbound networking"),
        ) as weekly_socket_connect:
            for entity_key in ("personal", "company"):
                fixture = weekly_fixtures[entity_key]
                weekly_client.set_cookie("entity", fixture["display"])

                with patch.object(
                    weekly_routes,
                    "render_template",
                    side_effect=_capture_weekly_context,
                ):
                    historical_response = weekly_client.get(
                        "/weekly/?week=2026-W07"
                    )
                historical = dict(captured_weekly_context)
                _check(
                    historical_response.status_code == 200
                    and historical["week_str"] == "2026-W07"
                    and historical["budget_month_name"] == "February"
                    and historical["weekly_pace"] == 77500
                    and historical["last_week_pace"] == 77500,
                    f"weekly 4V {entity_key}: historical pace and display should use February's 28-day context",
                )
                _check(
                    historical["spent_cents"] == 5000
                    and historical["burn_rate"]["projected_cents"] == 28000
                    and historical["burn_rate"]["over_under_cents"] == 282000,
                    f"weekly 4V {entity_key}: February MTD and burn inputs should reconcile",
                )

                bills_by_type = {}
                for bill in historical["bills"]:
                    bills_by_type.setdefault(bill["type"], []).append(bill)
                scheduled_bill = next(
                    bill
                    for bill in bills_by_type["cc_payment"]
                    if f"4V Scheduled {entity_key}" in bill["merchant"]
                )
                missing_bill = next(
                    bill
                    for bill in bills_by_type["cc_payment"]
                    if f"4V Missing {entity_key}" in bill["merchant"]
                )
                _check(
                    bills_by_type["recurring"][0]["date"]
                    == real_date(2026, 2, 9)
                    and bills_by_type["manual_recurring"][0]["date"]
                    == real_date(2026, 2, 10)
                    and scheduled_bill["date"] == real_date(2026, 2, 11)
                    and missing_bill["date"] == real_date(2026, 2, 12),
                    f"weekly 4V {entity_key}: historical recurring manual and card bills should use the viewed week",
                )
                _check(
                    scheduled_bill["amount_cents"] == 5000
                    and "\u2014 $50 due" in scheduled_bill["merchant"]
                    and missing_bill["amount_cents"] is None
                    and "\u2014 Payment due" in missing_bill["merchant"]
                    and historical["bills_total"] == 10000,
                    f"weekly 4V {entity_key}: scheduled card payment and unavailable fallback should reconcile",
                )
                _check(
                    not any(
                        bill["type"] == "cc_payment"
                        and f"4V Zero Balance {entity_key}" in bill["merchant"]
                        for bill in historical["bills"]
                    )
                    and [bill["date"] for bill in historical["bills"]]
                    == sorted(bill["date"] for bill in historical["bills"]),
                    f"weekly 4V {entity_key}: zero-balance cards should stay out and bills should remain ordered",
                )
                if entity_key == "company":
                    _check(
                        any(
                            bill["type"] == "payroll"
                            and bill["date"] == real_date(2026, 2, 13)
                            for bill in historical["bills"]
                        ),
                        "weekly 4V company: BFM payroll should remain in the viewed week",
                    )

                with patch.object(
                    weekly_routes,
                    "render_template",
                    side_effect=_capture_weekly_context,
                ):
                    cross_month_response = weekly_client.get(
                        "/weekly/?week=2026-W27"
                    )
                cross_month = dict(captured_weekly_context)
                _check(
                    cross_month_response.status_code == 200
                    and cross_month["monday"] == real_date(2026, 6, 29)
                    and cross_month["sunday"] == real_date(2026, 7, 5)
                    and cross_month["budget_month_name"] == "June"
                    and cross_month["weekly_pace"] == 72333
                    and cross_month["spent_cents"] == 13000
                    and cross_month["burn_rate"]["projected_cents"] == 6000,
                    f"weekly 4V {entity_key}: cross-month week should keep June pace MTD divisor and display",
                )

                with patch.object(
                    weekly_routes,
                    "render_template",
                    side_effect=_capture_weekly_context,
                ):
                    cross_year_response = weekly_client.get(
                        "/weekly/?week=2026-W01"
                    )
                cross_year = dict(captured_weekly_context)
                _check(
                    cross_year_response.status_code == 200
                    and cross_year["monday"] == real_date(2025, 12, 29)
                    and cross_year["sunday"] == real_date(2026, 1, 4)
                    and cross_year["budget_month_name"] == "December"
                    and cross_year["weekly_pace"] == 70000,
                    f"weekly 4V {entity_key}: cross-year week should retain the Monday-owned December context",
                )

                with patch.object(
                    weekly_routes,
                    "render_template",
                    side_effect=_capture_weekly_context,
                ):
                    invalid_response = weekly_client.get(
                        "/weekly/?week=not-an-iso-week"
                    )
                invalid_context = dict(captured_weekly_context)
                _check(
                    invalid_response.status_code == 200
                    and invalid_context["week_str"] == "2026-W30"
                    and invalid_context["budget_month_name"] == "July"
                    and invalid_context["weekly_pace"] == 70000,
                    f"weekly 4V {entity_key}: invalid week should fall back to the fixed current context",
                )

                rendered_historical = weekly_client.get(
                    "/weekly/?week=2026-W07"
                )
                rendered_body = rendered_historical.get_data(as_text=True)
                _check(
                    rendered_historical.status_code == 200
                    and f"4V Scheduled {entity_key} \u2014 $50 due" in rendered_body
                    and f"4V Missing {entity_key} \u2014 Payment due" in rendered_body,
                    f"weekly 4V {entity_key}: rendered card reminders should expose scheduled and unavailable amounts",
                )

                cashflow_response = weekly_client.get("/cashflow/")
                planning_response = weekly_client.get("/planning/short-term/")
                _check(
                    cashflow_response.status_code == 200
                    and planning_response.status_code == 200,
                    f"weekly 4V {entity_key}: existing today-based helper callers should still render",
                )

            weekly_client.set_cookie("entity", "LL")
            denied_ll_weekly = weekly_client.get("/weekly/?week=2026-W07")
            _check(
                denied_ll_weekly.status_code == 302
                and denied_ll_weekly.headers.get("Location", "").endswith("/"),
                "weekly 4V LL: Weekly should remain denied before route handling",
            )
            _check(
                _database_snapshot("luxelegacy") == before_ll_weekly,
                "weekly 4V LL: denied request should leave the database unchanged",
            )
            weekly_create_connection.assert_not_called()
            weekly_socket_connect.assert_not_called()

        def _restore_weekly_row(conn, table, row):
            if row is None:
                return
            columns = tuple(row.keys())
            conn.execute(
                f"INSERT INTO {table} ({','.join(columns)}) "
                f"VALUES ({','.join('?' for _ in columns)})",
                tuple(row[column] for column in columns),
            )

        for entity_key, fixture in weekly_fixtures.items():
            cleanup_conn = get_connection(entity_key)
            try:
                placeholders = ",".join("?" for _ in fixture["transaction_ids"])
                cleanup_conn.execute(
                    f"DELETE FROM transactions WHERE transaction_id IN ({placeholders})",
                    fixture["transaction_ids"],
                )
                cleanup_conn.execute(
                    "DELETE FROM action_items WHERE title=?",
                    (f"4V Action {entity_key}",),
                )
                cleanup_conn.execute(
                    "DELETE FROM manual_recurring WHERE merchant=?",
                    (f"4V Manual {entity_key}",),
                )
                account_placeholders = ",".join("?" for _ in fixture["accounts"])
                cleanup_conn.execute(
                    f"DELETE FROM account_balances "
                    f"WHERE account_name IN ({account_placeholders})",
                    fixture["accounts"],
                )
                cleanup_conn.execute(
                    "DELETE FROM budget_items WHERE category='Food'"
                )
                _restore_weekly_row(
                    cleanup_conn,
                    "budget_items",
                    fixture["original_budget"],
                )
                if entity_key == "company":
                    cleanup_conn.execute("DELETE FROM payroll_schedule WHERE id=1")
                    _restore_weekly_row(
                        cleanup_conn,
                        "payroll_schedule",
                        fixture["original_payroll"],
                    )
                cleanup_conn.commit()
            finally:
                cleanup_conn.close()
            _check(
                _weekly_counts(entity_key) == weekly_baselines[entity_key],
                f"weekly 4V {entity_key}: synthetic rows should clean up exactly",
            )

        print("   ✅ Viewed-week pace, MTD, burn, recurrence, scheduled payments, fallbacks, isolation, denied-network, and cleanup passed")

        # ── 8a6. Weekly paydown-goal validation ────────────────────
        print("\n8a6. Weekly paydown-goal validation…")
        from web.routes import waterfall as waterfall_routes

        def _paydown_row(entity_key):
            paydown_conn = get_connection(entity_key)
            try:
                row = paydown_conn.execute(
                    "SELECT * FROM cc_paydown_goal WHERE id=1"
                ).fetchone()
                return dict(row) if row else None
            finally:
                paydown_conn.close()

        def _replace_paydown_row(entity_key, row):
            paydown_conn = get_connection(entity_key)
            try:
                paydown_conn.execute("DELETE FROM cc_paydown_goal")
                if row is not None:
                    columns = tuple(row.keys())
                    paydown_conn.execute(
                        f"INSERT INTO cc_paydown_goal ({','.join(columns)}) "
                        f"VALUES ({','.join('?' for _ in columns)})",
                        tuple(row[column] for column in columns),
                    )
                paydown_conn.commit()
            finally:
                paydown_conn.close()

        paydown_baselines = {
            entity_key: _paydown_row(entity_key)
            for entity_key in ("personal", "company", "luxelegacy")
        }
        paydown_card_names = {}
        for entity_key in ("personal", "company"):
            card_name = f"4W Paydown Card {entity_key}"
            card_conn = get_connection(entity_key)
            try:
                card_conn.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type, "
                    "credit_limit_cents, sort_order) "
                    "VALUES (?, 25000, 'manual', 'credit_card', 100000, 860)",
                    (card_name,),
                )
                card_conn.commit()
            finally:
                card_conn.close()
            paydown_card_names[entity_key] = card_name
        waterfall_txn_id = "synthetic-4w-waterfall-income"
        waterfall_conn = get_connection("company")
        try:
            waterfall_conn.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_canonical, amount, "
                "amount_cents, account, category, source_filename, imported_at) "
                "VALUES (?, '2026-07-01', '4W Waterfall Income', '4W Waterfall Income', "
                "1000.00, 100000, '4W Synthetic', 'Income', 'synthetic-4w', "
                "'2026-07-21T00:00:00+00:00')",
                (waterfall_txn_id,),
            )
            waterfall_conn.commit()
        finally:
            waterfall_conn.close()

        before_ll_paydown = _database_snapshot("luxelegacy")
        with app.test_client() as paydown_client, patch.object(
            weekly_routes, "date", _WeeklyDate
        ), patch(
            "socket.create_connection",
            side_effect=AssertionError("weekly 4W attempted outbound networking"),
        ) as paydown_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("weekly 4W attempted outbound networking"),
        ) as paydown_socket_connect:
            for entity_key, entity_display in (
                ("personal", "Personal"),
                ("company", "BFM"),
            ):
                _replace_paydown_row(entity_key, None)
                paydown_client.set_cookie("entity", entity_display)
                with paydown_client.session_transaction() as paydown_session:
                    paydown_session.pop("_flashes", None)

                create_response = paydown_client.post(
                    "/weekly/paydown-goal",
                    data={"target_date": "2026-08-20", "week": "2026-W30"},
                )
                created = _paydown_row(entity_key)
                _check(
                    create_response.status_code == 302
                    and created is not None
                    and created["target_date"] == "2026-08-20"
                    and created["start_date"] == "2026-07-20"
                    and isinstance(created["start_balance_cents"], int),
                    f"weekly 4W {entity_key}: a valid future target should create canonical goal metadata",
                )

                for invalid_target in (
                    "",
                    "not-a-date",
                    "2026-02-30",
                    "2026-7-21",
                    "2026-07-20",
                    "2026-07-19",
                ):
                    before_invalid = _database_snapshot(entity_key)
                    invalid_response = paydown_client.post(
                        "/weekly/paydown-goal",
                        data={"target_date": invalid_target, "week": "2026-W30"},
                    )
                    _check(
                        invalid_response.status_code == 302
                        and _database_snapshot(entity_key) == before_invalid,
                        f"weekly 4W {entity_key}: rejected target {invalid_target!r} should preserve the full database",
                    )
                with paydown_client.session_transaction() as paydown_session:
                    validation_flashes = paydown_session.pop("_flashes", [])
                _check(
                    len(validation_flashes) == 6
                    and all(
                        category == "danger"
                        and message == "Choose a valid payoff target date after today."
                        for category, message in validation_flashes
                    ),
                    f"weekly 4W {entity_key}: rejected targets should return sanitized guidance without echoing input",
                )

                update_response = paydown_client.post(
                    "/weekly/paydown-goal",
                    data={"target_date": "2026-09-20", "week": "2026-W30"},
                )
                updated = _paydown_row(entity_key)
                _check(
                    update_response.status_code == 302
                    and updated["target_date"] == "2026-09-20"
                    and updated["start_date"] == created["start_date"]
                    and updated["start_balance_cents"]
                    == created["start_balance_cents"]
                    and updated["created_at"] == created["created_at"],
                    f"weekly 4W {entity_key}: a valid update should preserve start metadata and row identity",
                )

                corrupt_conn = get_connection(entity_key)
                try:
                    corrupt_conn.execute(
                        "UPDATE cc_paydown_goal SET target_date='not-a-date' WHERE id=1"
                    )
                    corrupt_conn.commit()
                finally:
                    corrupt_conn.close()
                before_corrupt_read = _database_snapshot(entity_key)
                weekly_corrupt_response = paydown_client.get(
                    "/weekly/?week=2026-W30"
                )
                weekly_corrupt_body = weekly_corrupt_response.get_data(as_text=True)
                _check(
                    weekly_corrupt_response.status_code == 200,
                    f"weekly 4W {entity_key}: a malformed stored target should not break Weekly",
                )
                _check(
                    "not-a-date" not in weekly_corrupt_body,
                    f"weekly 4W {entity_key}: a malformed stored target should not be rendered",
                )
                _check(
                    'min="2026-07-21"' in weekly_corrupt_body,
                    f"weekly 4W {entity_key}: browser guidance should require the next local date",
                )
                _check(
                    _database_snapshot(entity_key) == before_corrupt_read,
                    f"weekly 4W {entity_key}: a malformed stored target read should not mutate data",
                )

                if entity_key == "personal":
                    paydown_client.set_cookie("entity", "Personal")
                    waterfall_corrupt_response = paydown_client.get(
                        "/waterfall/?month=2026-07"
                    )
                    with app.test_request_context("/waterfall/"):
                        _, _, waterfall_goal, waterfall_pace = (
                            waterfall_routes._get_personal_cc()
                        )
                    _check(
                        waterfall_corrupt_response.status_code == 200
                        and waterfall_goal is None
                        and waterfall_pace is None
                        and _database_snapshot(entity_key) == before_corrupt_read,
                        "weekly 4W personal: Waterfall should ignore a malformed stored goal without mutation",
                    )
                    paydown_client.set_cookie("entity", entity_display)

                recovery_response = paydown_client.post(
                    "/weekly/paydown-goal",
                    data={"target_date": "2026-10-20", "week": "2026-W30"},
                )
                recovered = _paydown_row(entity_key)
                _check(
                    recovery_response.status_code == 302
                    and recovered["target_date"] == "2026-10-20"
                    and recovered["start_date"] == created["start_date"]
                    and recovered["start_balance_cents"]
                    == created["start_balance_cents"],
                    f"weekly 4W {entity_key}: a valid target should recover a malformed target-only row",
                )

                for column, bad_value in (
                    ("start_date", "bad-start"),
                    ("start_balance_cents", "not-cents"),
                ):
                    malformed_conn = get_connection(entity_key)
                    try:
                        malformed_conn.execute(
                            f"UPDATE cc_paydown_goal SET {column}=? WHERE id=1",
                            (bad_value,),
                        )
                        malformed_conn.commit()
                    finally:
                        malformed_conn.close()
                    before_malformed = _database_snapshot(entity_key)
                    malformed_read = paydown_client.get(
                        "/weekly/?week=2026-W30"
                    )
                    rejected_repair = paydown_client.post(
                        "/weekly/paydown-goal",
                        data={"target_date": "2026-11-20", "week": "2026-W30"},
                    )
                    _check(
                        malformed_read.status_code == 200
                        and rejected_repair.status_code == 302
                        and _database_snapshot(entity_key) == before_malformed,
                        f"weekly 4W {entity_key}: malformed stored {column} should be read-safe and block target-only mutation",
                    )
                    _replace_paydown_row(entity_key, recovered)

            paydown_client.set_cookie("entity", "LL")
            denied_ll_paydown = paydown_client.post(
                "/weekly/paydown-goal",
                data={"target_date": "2026-08-20", "week": "2026-W30"},
            )
            _check(
                denied_ll_paydown.status_code == 302
                and denied_ll_paydown.headers.get("Location", "").endswith("/")
                and _database_snapshot("luxelegacy") == before_ll_paydown,
                "weekly 4W LL: paydown mutation should remain denied before storage",
            )
            paydown_create_connection.assert_not_called()
            paydown_socket_connect.assert_not_called()

        for entity_key, original_row in paydown_baselines.items():
            _replace_paydown_row(entity_key, original_row)
        for entity_key, card_name in paydown_card_names.items():
            card_conn = get_connection(entity_key)
            try:
                card_conn.execute(
                    "DELETE FROM account_balances WHERE account_name=?",
                    (card_name,),
                )
                card_conn.commit()
            finally:
                card_conn.close()
        waterfall_conn = get_connection("company")
        try:
            waterfall_conn.execute(
                "DELETE FROM transactions WHERE transaction_id=?",
                (waterfall_txn_id,),
            )
            waterfall_conn.commit()
        finally:
            waterfall_conn.close()
        _check(
            all(
                _paydown_row(entity_key) == paydown_baselines[entity_key]
                for entity_key in ("personal", "company", "luxelegacy")
            ),
            "weekly 4W: paydown-goal fixtures should clean up exactly",
        )

        print("   ✅ Date validation, zero-mutation rejection, defensive reads, recovery, isolation, denied-network, and cleanup passed")

        # ── 8a7. Waterfall payoff truthfulness ────────────────────
        print("\n8a7. Waterfall payoff truthfulness…")

        waterfall_4x_baselines = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in ("personal", "company", "luxelegacy")
        }
        waterfall_4x_transactions = (
            (
                "synthetic-4x-may-income",
                "2026-05-01",
                "4X May Income",
                1000.00,
                100000,
                "Income",
            ),
            (
                "synthetic-4x-june-expense",
                "2026-06-01",
                "4X June Expense",
                -2000.00,
                -200000,
                "Rent",
            ),
            (
                "synthetic-4x-july-income",
                "2026-07-01",
                "4X July Income",
                2500.00,
                250000,
                "Income",
            ),
        )
        waterfall_4x_conn = get_connection("company")
        try:
            waterfall_4x_conn.executemany(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_canonical, amount, "
                "amount_cents, account, category, source_filename, imported_at) "
                "VALUES (?, ?, ?, ?, ?, ?, '4X Synthetic', ?, 'synthetic-4x', "
                "'2026-07-21T00:00:00+00:00')",
                (
                    (txn_id, txn_date, description, description, amount, amount_cents, category)
                    for txn_id, txn_date, description, amount, amount_cents, category
                    in waterfall_4x_transactions
                ),
            )
            waterfall_4x_conn.commit()
        finally:
            waterfall_4x_conn.close()

        waterfall_4x_card = "4X Payoff Card"
        waterfall_4x_conn = get_connection("personal")
        try:
            waterfall_4x_conn.execute(
                "INSERT INTO account_balances "
                "(account_name, balance_cents, balance_source, account_type, "
                "credit_limit_cents, sort_order) "
                "VALUES (?, 25000, 'manual', 'credit_card', 100000, 870)",
                (waterfall_4x_card,),
            )
            waterfall_4x_conn.commit()
        finally:
            waterfall_4x_conn.close()

        _check(
            waterfall_routes._rolling_calendar_months("2026-07")
            == ["2026-05", "2026-06", "2026-07"]
            and waterfall_routes._rolling_calendar_months("2026-01")
            == ["2025-11", "2025-12", "2026-01"],
            "waterfall 4X: rolling windows should use three consecutive calendar months across year boundaries",
        )
        mixed_history = waterfall_routes._get_historical_surplus(
            ["2026-05", "2026-06", "2026-07"]
        )
        _check(
            [month["surplus_cents"] for month in mixed_history]
            == [100000, -200000, 250000]
            and waterfall_routes._average_signed_surplus(mixed_history) == 50000,
            "waterfall 4X: every positive and deficit month should produce the signed 500 dollar average",
        )
        missing_history = waterfall_routes._get_historical_surplus(
            ["2026-03", "2026-04", "2026-05"]
        )
        _check(
            [month["surplus_cents"] for month in missing_history]
            == [0, 0, 100000]
            and waterfall_routes._average_signed_surplus(missing_history) == 33333,
            "waterfall 4X: no-row calendar months should remain zero-valued inputs in the fixed denominator",
        )
        _check(
            waterfall_routes._average_signed_surplus(
                [
                    {"surplus_cents": 0},
                    {"surplus_cents": 0},
                    {"surplus_cents": 0},
                ]
            ) == 0
            and waterfall_routes._average_signed_surplus(
                [
                    {"surplus_cents": -10000},
                    {"surplus_cents": 0},
                    {"surplus_cents": -20000},
                ]
            ) == -10000
            and waterfall_routes._average_signed_surplus([]) == 0,
            "waterfall 4X: zero non-positive and empty signed histories should have explicit averages",
        )

        class _WaterfallDate(real_date):
            @classmethod
            def today(cls):
                return cls(2026, 7, 21)

        with patch.object(waterfall_routes, "date", _WaterfallDate):
            sub_month = waterfall_routes._compute_payoff_estimate(100000, 25000)
            fractional = waterfall_routes._compute_payoff_estimate(100000, 150000)
            exact_multiple = waterfall_routes._compute_payoff_estimate(100000, 200000)
            _check(
                sub_month is not None
                and sub_month["months"] == 1
                and sub_month["payoff_date_ym"] == "2026-07"
                and fractional is not None
                and fractional["months"] == 2
                and fractional["payoff_date_ym"] == "2026-09"
                and exact_multiple is not None
                and exact_multiple["months"] == 2
                and exact_multiple["payoff_date_ym"] == "2026-09",
                "waterfall 4X: payoff duration and date should round completion upward from the same exact ratio",
            )
            _check(
                waterfall_routes._compute_payoff_estimate(0, 25000) is None
                and waterfall_routes._compute_payoff_estimate(-1, 25000) is None
                and waterfall_routes._compute_payoff_estimate(100000, 0) is None,
                "waterfall 4X: non-positive surplus or debt should not produce a payoff estimate",
            )

        waterfall_4x_fixture_state = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in ("personal", "company", "luxelegacy")
        }
        with app.test_client() as waterfall_4x_client, patch.object(
            waterfall_routes, "date", _WaterfallDate
        ), patch(
            "socket.create_connection",
            side_effect=AssertionError("waterfall 4X attempted outbound networking"),
        ) as waterfall_4x_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("waterfall 4X attempted outbound networking"),
        ) as waterfall_4x_socket_connect:
            for entity_display in ("Personal", "BFM"):
                waterfall_4x_client.set_cookie("entity", entity_display)
                mixed_response = waterfall_4x_client.get(
                    "/waterfall/?month=2026-07"
                )
                mixed_body = mixed_response.get_data(as_text=True)
                _check(
                    mixed_response.status_code == 200
                    and "3-month signed average of $500/mo" in mixed_body
                    and ">1 month<" in mixed_body,
                    f"waterfall 4X {entity_display}: mixed signed history should drive truthful rendered payoff guidance",
                )
                missing_response = waterfall_4x_client.get(
                    "/waterfall/?month=2026-05"
                )
                _check(
                    missing_response.status_code == 200
                    and "3-month signed average of $333/mo"
                    in missing_response.get_data(as_text=True),
                    f"waterfall 4X {entity_display}: missing prior months should remain zero-valued calendar inputs",
                )
                non_positive_response = waterfall_4x_client.get(
                    "/waterfall/?month=2026-06"
                )
                _check(
                    non_positive_response.status_code == 200
                    and "The 3-month signed average leaves no surplus available for paydown"
                    in non_positive_response.get_data(as_text=True),
                    f"waterfall 4X {entity_display}: non-positive signed average should suppress payoff guidance",
                )

            waterfall_4x_client.set_cookie("entity", "LL")
            denied_waterfall_4x = waterfall_4x_client.get(
                "/waterfall/?month=2026-07"
            )
            _check(
                denied_waterfall_4x.status_code == 302
                and denied_waterfall_4x.headers.get("Location", "").endswith("/"),
                "waterfall 4X LL: Waterfall should remain denied before route handling",
            )
            _check(
                all(
                    _database_snapshot(entity_key)
                    == waterfall_4x_fixture_state[entity_key]
                    for entity_key in ("personal", "company", "luxelegacy")
                ),
                "waterfall 4X: route and helper reads should preserve every entity database",
            )
            waterfall_4x_create_connection.assert_not_called()
            waterfall_4x_socket_connect.assert_not_called()

        waterfall_4x_conn = get_connection("company")
        try:
            waterfall_4x_conn.execute(
                "DELETE FROM transactions WHERE source_filename='synthetic-4x'"
            )
            waterfall_4x_conn.commit()
        finally:
            waterfall_4x_conn.close()
        waterfall_4x_conn = get_connection("personal")
        try:
            waterfall_4x_conn.execute(
                "DELETE FROM account_balances WHERE account_name=?",
                (waterfall_4x_card,),
            )
            waterfall_4x_conn.commit()
        finally:
            waterfall_4x_conn.close()
        _check(
            all(
                _database_snapshot(entity_key)
                == waterfall_4x_baselines[entity_key]
                for entity_key in ("personal", "company", "luxelegacy")
            ),
            "waterfall 4X: synthetic transactions and debt should clean up exactly",
        )

        print("   ✅ Signed calendar windows, deficit and missing months, payoff ceiling, rendering, isolation, denied-network, and cleanup passed")

        # ── 8a8. Waterfall tax input truthfulness ─────────────────
        print("\n8a8. Waterfall tax input truthfulness…")

        waterfall_4y_baselines = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in ("personal", "company", "luxelegacy")
        }
        waterfall_4y_conn = get_connection("company")
        try:
            waterfall_4y_conn.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_canonical, amount, "
                "amount_cents, account, category, source_filename, imported_at) "
                "VALUES ('synthetic-4y-income', '2024-01-10', '4Y Tax Income', "
                "'4Y Tax Income', 1000.00, 100000, '4Y Synthetic', 'Income', "
                "'synthetic-4y', '2026-07-21T00:00:00+00:00')"
            )
            waterfall_4y_conn.commit()
        finally:
            waterfall_4y_conn.close()
        waterfall_4y_fixture_state = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in ("personal", "company", "luxelegacy")
        }
        normalized_tax_cases = (
            (None, 2200),
            ("", 2200),
            ("not-a-rate", 2200),
            ("NaN", 2200),
            ("Infinity", 2200),
            ("-Infinity", 2200),
            ("-0.01", 2200),
            ("100", 2200),
            ("99.995", 2200),
            ("1e999999", 2200),
            ("0", 0),
            ("22", 2200),
            ("22.124", 2212),
            ("22.125", 2213),
            ("99.994", 9999),
        )
        for raw_rate, expected_bps in normalized_tax_cases:
            _check(
                waterfall_routes._normalize_tax_rate_bps(raw_rate)
                == expected_bps,
                f"waterfall 4Y: {raw_rate!r} should normalize to {expected_bps} basis points",
            )
        _check(
            waterfall_routes._format_tax_rate_bps(0) == "0"
            and waterfall_routes._format_tax_rate_bps(2200) == "22"
            and waterfall_routes._format_tax_rate_bps(2213) == "22.13"
            and waterfall_routes._format_tax_rate_bps(9999) == "99.99",
            "waterfall 4Y: rendered rates should derive exactly from normalized basis points",
        )

        captured_waterfall_contexts = []

        def _capture_waterfall_context(sender, template, context, **extra):
            if template.name == "waterfall.html":
                captured_waterfall_contexts.append(dict(context))

        from flask import template_rendered

        route_tax_cases = (
            (None, 2200),
            ("", 2200),
            ("bad", 2200),
            ("NaN", 2200),
            ("Infinity", 2200),
            ("-Infinity", 2200),
            ("-1", 2200),
            ("100", 2200),
            ("99.995", 2200),
            ("1e999999", 2200),
            ("0", 0),
            ("12.34", 1234),
            ("99.994", 9999),
        )
        with app.test_client() as waterfall_4y_client, template_rendered.connected_to(
            _capture_waterfall_context,
            app,
        ), patch(
            "socket.create_connection",
            side_effect=AssertionError("waterfall 4Y attempted outbound networking"),
        ) as waterfall_4y_create_connection, patch(
            "socket.socket.connect",
            side_effect=AssertionError("waterfall 4Y attempted outbound networking"),
        ) as waterfall_4y_socket_connect:
            for entity_display in ("Personal", "BFM"):
                waterfall_4y_client.set_cookie("entity", entity_display)
                for raw_rate, expected_bps in route_tax_cases:
                    query = {
                        "month": "2024-01",
                        "mode": "revenue",
                        "target_revenue": "1000000",
                    }
                    if raw_rate is not None:
                        query["tax_rate"] = raw_rate
                    response = waterfall_4y_client.get(
                        "/waterfall/",
                        query_string=query,
                    )
                    context = captured_waterfall_contexts[-1]
                    expected_display = waterfall_routes._format_tax_rate_bps(
                        expected_bps
                    )
                    _check(
                        response.status_code == 200
                        and context["tax_rate_bps"] == expected_bps
                        and context["tax_rate_display"] == expected_display
                        and context["owner_take_home"]
                        == int(
                            context["owner_gross"]
                            * (10000 - expected_bps)
                            / 10000
                        )
                        and context["actual_take_home"]
                        == int(
                            context["actual_owner_gross"]
                            * (10000 - expected_bps)
                            / 10000
                        ),
                        f"waterfall 4Y {entity_display}: {raw_rate!r} should keep calculation and display on {expected_bps} basis points",
                    )
                    rendered_body = response.get_data(as_text=True)
                    _check(
                        rendered_body.count(f'value="{expected_display}"') == 2,
                        f"waterfall 4Y {entity_display}: both tax inputs should display the one normalized value",
                    )

                takehome_response = waterfall_4y_client.get(
                    "/waterfall/",
                    query_string={
                        "month": "2024-01",
                        "mode": "takehome",
                        "take_home": "1234",
                        "tax_rate": "12.34",
                    },
                )
                takehome_context = captured_waterfall_contexts[-1]
                expected_owner_gross = int(123400 * 10000 / (10000 - 1234))
                _check(
                    takehome_response.status_code == 200
                    and takehome_context["tax_rate_bps"] == 1234
                    and takehome_context["owner_gross"] == expected_owner_gross
                    and takehome_context["target_revenue"]
                    == expected_owner_gross + takehome_context["bfm_costs"]
                    and takehome_context["owner_take_home"]
                    == int(expected_owner_gross * (10000 - 1234) / 10000),
                    f"waterfall 4Y {entity_display}: take-home mode should use the same normalized tax rate for gross revenue and rendered take-home",
                )
                waterfall_controller_source = (
                    PROJECT_ROOT / "web" / "static" / "waterfall.js"
                ).read_text()
                waterfall_tax_handler = waterfall_controller_source.split(
                    "function applyTaxRate", 1
                )[1].split("function initialize", 1)[0]
                _check(
                    "input.value.trim()" in waterfall_tax_handler
                    and ".replace(" not in waterfall_tax_handler
                    and 'url.searchParams.set("tax_rate", value)' in waterfall_tax_handler,
                    "waterfall 4Y: browser input should reach server normalization without reinterpretation",
                )

            waterfall_4y_client.set_cookie("entity", "LL")
            denied_waterfall_4y = waterfall_4y_client.get(
                "/waterfall/",
                query_string={"month": "2024-01", "tax_rate": "NaN"},
            )
            _check(
                denied_waterfall_4y.status_code == 302
                and denied_waterfall_4y.headers.get("Location", "").endswith("/"),
                "waterfall 4Y LL: Waterfall should remain denied before tax parsing",
            )
            waterfall_4y_create_connection.assert_not_called()
            waterfall_4y_socket_connect.assert_not_called()

        _check(
            all(
                _database_snapshot(entity_key)
                == waterfall_4y_fixture_state[entity_key]
                for entity_key in ("personal", "company", "luxelegacy")
            ),
            "waterfall 4Y: route and helper checks should not mutate the seeded entity state",
        )
        waterfall_4y_conn = get_connection("company")
        try:
            waterfall_4y_conn.execute(
                "DELETE FROM transactions WHERE source_filename='synthetic-4y'"
            )
            waterfall_4y_conn.commit()
        finally:
            waterfall_4y_conn.close()

        _check(
            all(
                _database_snapshot(entity_key)
                == waterfall_4y_baselines[entity_key]
                for entity_key in ("personal", "company", "luxelegacy")
            ),
            "waterfall 4Y: tax normalization and rendered route checks should preserve every entity database",
        )

        print("   ✅ Finite basis-point normalization, safe fallback, display/calculation reconciliation, isolation, denied-network, and cleanup passed")

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
            "/payroll/import/cancel",
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
            ("post", "/payroll/import/cancel", {
                "data": {"temp_key": "replaced-per-entity"},
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
                            elif path in ("/payroll/import/cancel", "/payroll/import/save"):
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

        # ── 8b2. Payroll import integrity and payload lifecycle ─────
        print("\n8b2. Payroll import integrity and payload lifecycle…")
        import re as payroll_re
        import stat as payroll_stat
        import time as payroll_time

        def _payroll_workbook_bytes(rows, *, include_header=True, second_section=False):
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Per Payroll Costs"
            sheet.append(["Synthetic Payroll Export"])
            sheet.append([])
            if include_header:
                sheet.append(["2026 Paycheck Dates", "Job Code", "Location", "07/01/2026"])
                for employee_name, job_code, amount in rows:
                    sheet.append([employee_name, job_code, "Main", amount])
            if second_section:
                sheet.append([])
                sheet.append(["2025 Paycheck Dates", "Job Code", "Location", "07/02/2025"])
                for employee_name, job_code, amount in rows:
                    sheet.append([employee_name, job_code, "Main", amount + 1])
            payload = io.BytesIO()
            workbook.save(payload)
            return payload.getvalue()

        def _payroll_preview(client, payload, filename="synthetic-payroll.xlsx"):
            response = client.post(
                "/payroll/import/parse",
                data={"payroll_file": (io.BytesIO(payload), filename)},
                content_type="multipart/form-data",
            )
            _check(response.status_code == 200,
                   f"payroll 4P preview {filename}: expected 200")
            body = response.get_data(as_text=True)
            key_match = payroll_re.search(
                r'name="temp_key" value="([^"]+)"', body
            )
            _check(key_match is not None,
                   f"payroll 4P preview {filename}: missing temporary key")
            return response, body, key_match.group(1)

        payroll_4p_names = (
            "Existing Payroll Employee",
            "Reassignment Target",
            "Reassignment Source",
            "New Payroll Employee",
            "Canceled Payroll Employee",
            "Expired Payroll Employee",
            "Multi Section Employee",
        )
        payroll_entity_baseline = {}
        for entity_key in ("personal", "luxelegacy"):
            conn_payroll = get_connection(entity_key)
            payroll_entity_baseline[entity_key] = tuple(
                conn_payroll.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("employees", "employee_pay_changes", "payroll_entries")
            )
            conn_payroll.close()

        conn_payroll = get_connection("company")
        conn_payroll.execute(
            "DELETE FROM employees WHERE name IN ({})".format(
                ",".join("?" for _ in payroll_4p_names)
            ),
            payroll_4p_names,
        )
        existing_employee_id = conn_payroll.execute(
            "INSERT INTO employees (name, role, pay_type, pay_rate_cents) "
            "VALUES (?, 'Nurses', 'hourly', 2500)",
            ("Existing Payroll Employee",),
        ).lastrowid
        reassignment_target_id = conn_payroll.execute(
            "INSERT INTO employees (name, role, pay_type, pay_rate_cents) "
            "VALUES (?, 'Nurses', 'hourly', 2600)",
            ("Reassignment Target",),
        ).lastrowid
        conn_payroll.commit()
        conn_payroll.close()

        existing_workbook = _payroll_workbook_bytes([
            ("Existing Payroll Employee", "600 Nurse /MA", 1234.56),
        ])
        reassignment_workbook = _payroll_workbook_bytes([
            ("Reassignment Source", "600 Nurse /MA", 2345.67),
        ])
        new_employee_workbook = _payroll_workbook_bytes([
            ("New Payroll Employee", "600 Nurse /MA", 3456.78),
        ])
        cancel_workbook = _payroll_workbook_bytes([
            ("Canceled Payroll Employee", "600 Nurse /MA", 4567.89),
        ])

        with tempfile.TemporaryDirectory(prefix="payroll_4p_") as payroll_payload_dir, patch.object(
            payroll_routes, "_TEMP_DIR", payroll_payload_dir
        ):
            original_socket = socket.socket

            def _deny_payroll_network(*_args, **_kwargs):
                raise AssertionError("payroll 4P attempted outbound networking")

            socket.socket = _deny_payroll_network
            try:
                with app.test_client() as payroll_4p_client:
                    payroll_4p_client.set_cookie("entity", "BFM")

                    # Exact preview defaults to the one existing employee, and
                    # save-time enforcement rejects a forged "new" assignment.
                    _, existing_body, existing_key = _payroll_preview(
                        payroll_4p_client, existing_workbook
                    )
                    _check(
                        f'value="{existing_employee_id}" selected' in existing_body,
                        "payroll 4P exact match: preview did not select existing employee",
                    )
                    _check(
                        "Create new employee" not in existing_body,
                        "payroll 4P exact match: preview still offered duplicate creation",
                    )
                    existing_path = Path(payroll_payload_dir) / f"{existing_key}.json"
                    _check(existing_path.exists(),
                           "payroll 4P exact match: preview payload missing")
                    _check(
                        payroll_stat.S_IMODE(existing_path.stat().st_mode) == 0o600,
                        "payroll 4P payload: expected mode 0600",
                    )
                    existing_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": existing_key,
                            "assign_Existing Payroll Employee": "new",
                            "new_role_Existing Payroll Employee": "Nurses",
                        },
                    )
                    _check(existing_save.status_code == 302,
                           "payroll 4P exact match: save should redirect")
                    conn_payroll = get_connection("company")
                    exact_counts = conn_payroll.execute(
                        "SELECT COUNT(*), "
                        "(SELECT COUNT(*) FROM payroll_entries WHERE employee_id=?) "
                        "FROM employees WHERE lower(trim(name))=lower(trim(?))",
                        (existing_employee_id, "Existing Payroll Employee"),
                    ).fetchone()
                    _check(tuple(exact_counts) == (1, 1),
                           "payroll 4P exact match: save created a duplicate or missed entry")
                    conn_payroll.close()
                    _check(not existing_path.exists(),
                           "payroll 4P exact match: save retained payload")
                    reused_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": existing_key,
                            "assign_Existing Payroll Employee": "new",
                            "new_role_Existing Payroll Employee": "Nurses",
                        },
                    )
                    missing_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={"temp_key": "payroll_import_missing_4p"},
                    )
                    _check(
                        reused_save.status_code == 302
                        and missing_save.status_code == 302,
                        "payroll 4P missing or reused save was not deterministic",
                    )

                    # A genuinely unmatched row can be reassigned explicitly to
                    # another existing employee without creating a roster row.
                    _, _, reassignment_key = _payroll_preview(
                        payroll_4p_client, reassignment_workbook
                    )
                    reassignment_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": reassignment_key,
                            "assign_Reassignment Source": str(reassignment_target_id),
                        },
                    )
                    _check(reassignment_save.status_code == 302,
                           "payroll 4P reassignment: save should redirect")
                    conn_payroll = get_connection("company")
                    reassignment_counts = conn_payroll.execute(
                        "SELECT "
                        "(SELECT COUNT(*) FROM employees WHERE name=?), "
                        "(SELECT COUNT(*) FROM payroll_entries WHERE employee_id=?)",
                        ("Reassignment Source", reassignment_target_id),
                    ).fetchone()
                    _check(tuple(reassignment_counts) == (0, 1),
                           "payroll 4P reassignment: wrong employee or duplicate roster row")
                    conn_payroll.close()

                    # New creation remains available only for a genuinely
                    # unmatched employee, and exact re-import stays stable.
                    _, new_body, new_key = _payroll_preview(
                        payroll_4p_client, new_employee_workbook
                    )
                    _check("Create new employee" in new_body,
                           "payroll 4P unmatched: new employee option missing")
                    new_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": new_key,
                            "assign_New Payroll Employee": "new",
                            "new_role_New Payroll Employee": "Nurses",
                        },
                    )
                    _check(new_save.status_code == 302,
                           "payroll 4P unmatched: save should redirect")
                    conn_payroll = get_connection("company")
                    new_employee = conn_payroll.execute(
                        "SELECT id FROM employees WHERE name=?",
                        ("New Payroll Employee",),
                    ).fetchone()
                    _check(new_employee is not None,
                           "payroll 4P unmatched: employee was not created")
                    new_employee_id = new_employee["id"]
                    conn_payroll.close()

                    _, reimport_body, reimport_key = _payroll_preview(
                        payroll_4p_client, new_employee_workbook
                    )
                    _check(
                        f'value="{new_employee_id}" selected' in reimport_body,
                        "payroll 4P reimport: created employee was not selected",
                    )
                    reimport_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": reimport_key,
                            "assign_New Payroll Employee": "new",
                            "new_role_New Payroll Employee": "Nurses",
                        },
                    )
                    _check(reimport_save.status_code == 302,
                           "payroll 4P reimport: save should redirect")
                    conn_payroll = get_connection("company")
                    reimport_counts = conn_payroll.execute(
                        "SELECT "
                        "(SELECT COUNT(*) FROM employees WHERE name=?), "
                        "(SELECT COUNT(*) FROM payroll_entries WHERE employee_id=?)",
                        ("New Payroll Employee", new_employee_id),
                    ).fetchone()
                    _check(tuple(reimport_counts) == (1, 1),
                           "payroll 4P reimport: employee or payroll counts changed")
                    conn_payroll.close()

                    # Cancel is explicit, idempotent, exact-key only, and does
                    # not consume an unrelated payload.
                    _, _, cancel_key = _payroll_preview(
                        payroll_4p_client, cancel_workbook
                    )
                    cancel_path = Path(payroll_payload_dir) / f"{cancel_key}.json"
                    unrelated_key = "payroll_import_unrelated_4p"
                    payroll_routes._save_temp(unrelated_key, {
                        "entries": [],
                        "filename": "unrelated.xlsx",
                    })
                    unrelated_path = Path(payroll_payload_dir) / f"{unrelated_key}.json"
                    cancel_response = payroll_4p_client.post(
                        "/payroll/import/cancel", data={"temp_key": cancel_key}
                    )
                    _check(cancel_response.status_code == 302,
                           "payroll 4P cancel: expected redirect")
                    _check(not cancel_path.exists() and unrelated_path.exists(),
                           "payroll 4P cancel: exact or unrelated cleanup failed")
                    repeated_cancel = payroll_4p_client.post(
                        "/payroll/import/cancel", data={"temp_key": cancel_key}
                    )
                    malformed_cancel = payroll_4p_client.post(
                        "/payroll/import/cancel",
                        data={"temp_key": f"../{unrelated_key}"},
                    )
                    _check(
                        repeated_cancel.status_code == 302
                        and malformed_cancel.status_code == 302
                        and unrelated_path.exists(),
                        "payroll 4P cancel: reused or malformed key changed unrelated payload",
                    )

                    # Expired and malformed payloads are consumed safely and
                    # never create an employee.
                    expired_key = "payroll_import_expired_4p"
                    expired_path = Path(payroll_payload_dir) / f"{expired_key}.json"
                    payroll_routes._save_temp(expired_key, {
                        "entries": [{
                            "name": "Expired Payroll Employee",
                            "phoenix_job_code": "600 Nurse /MA",
                            "paycheck_date": "2026-07-01",
                            "amount": 10.0,
                        }],
                        "filename": "expired.xlsx",
                    })
                    expired_mtime = (
                        payroll_time.time()
                        - payroll_routes._TEMP_MAX_AGE_SECONDS
                        - 10
                    )
                    os.utime(expired_path, (expired_mtime, expired_mtime))
                    expired_save = payroll_4p_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": expired_key,
                            "assign_Expired Payroll Employee": "new",
                            "new_role_Expired Payroll Employee": "Nurses",
                        },
                    )
                    _check(expired_save.status_code == 302 and not expired_path.exists(),
                           "payroll 4P expired payload: expected safe consumption")

                    malformed_key = "payroll_import_malformed_4p"
                    malformed_path = Path(payroll_payload_dir) / f"{malformed_key}.json"
                    malformed_path.write_bytes(b"{not-json")
                    malformed_save = payroll_4p_client.post(
                        "/payroll/import/save", data={"temp_key": malformed_key}
                    )
                    _check(
                        malformed_save.status_code == 302 and not malformed_path.exists(),
                        "payroll 4P malformed payload: expected safe consumption",
                    )

                    # Corrupt, empty, unsupported, and headerless workbooks are
                    # controlled outcomes and retain no new payload.
                    invalid_cases = (
                        (b"not-an-xlsx", "corrupt.xlsx", "valid Phoenix payroll workbook"),
                        (b"", "empty.xlsx", "valid Phoenix payroll workbook"),
                        (b"name,amount\nA,1\n", "unsupported.csv", ".xlsx format"),
                        (
                            _payroll_workbook_bytes([], include_header=False),
                            "headerless.xlsx",
                            "No payroll entries found",
                        ),
                    )
                    for invalid_payload, invalid_name, expected_message in invalid_cases:
                        before_files = set(Path(payroll_payload_dir).iterdir())
                        invalid_response = payroll_4p_client.post(
                            "/payroll/import/parse",
                            data={
                                "payroll_file": (
                                    io.BytesIO(invalid_payload), invalid_name
                                )
                            },
                            content_type="multipart/form-data",
                        )
                        invalid_body = invalid_response.get_data(as_text=True)
                        _check(
                            invalid_response.status_code == 200
                            and expected_message in invalid_body,
                            f"payroll 4P invalid workbook {invalid_name}: uncontrolled outcome",
                        )
                        _check(
                            set(Path(payroll_payload_dir).iterdir()) == before_files,
                            f"payroll 4P invalid workbook {invalid_name}: retained payload",
                        )

                    # A valid multi-section workbook still previews both dates
                    # and its preview can be canceled cleanly.
                    multi_workbook = _payroll_workbook_bytes(
                        [("Multi Section Employee", "600 Nurse /MA", 100.0)],
                        second_section=True,
                    )
                    _, multi_body, multi_key = _payroll_preview(
                        payroll_4p_client, multi_workbook, "multi-section.xlsx"
                    )
                    _check("Parsed <strong>2</strong> payroll entries" in multi_body,
                           "payroll 4P multi-section: expected two parsed entries")
                    multi_path = Path(payroll_payload_dir) / f"{multi_key}.json"
                    payroll_4p_client.post(
                        "/payroll/import/cancel", data={"temp_key": multi_key}
                    )
                    _check(not multi_path.exists(),
                           "payroll 4P multi-section: cancel retained payload")

                    conn_payroll = get_connection("company")
                    expired_employee_count = conn_payroll.execute(
                        "SELECT COUNT(*) FROM employees WHERE name=?",
                        ("Expired Payroll Employee",),
                    ).fetchone()[0]
                    _check(expired_employee_count == 0,
                           "payroll 4P expired payload created an employee")
                    conn_payroll.close()

                    unrelated_path.unlink(missing_ok=True)
                    _check(not any(Path(payroll_payload_dir).iterdir()),
                           "payroll 4P payload directory was not empty after cleanup")
            finally:
                socket.socket = original_socket

        for entity_key in ("personal", "luxelegacy"):
            conn_payroll = get_connection(entity_key)
            final_counts = tuple(
                conn_payroll.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("employees", "employee_pay_changes", "payroll_entries")
            )
            _check(
                final_counts == payroll_entity_baseline[entity_key],
                f"payroll 4P {entity_key}: non-BFM payroll state changed",
            )
            conn_payroll.close()

        conn_payroll = get_connection("company")
        conn_payroll.execute(
            "DELETE FROM employees WHERE name IN ({})".format(
                ",".join("?" for _ in payroll_4p_names)
            ),
            payroll_4p_names,
        )
        conn_payroll.commit()
        remaining_4p_rows = conn_payroll.execute(
            "SELECT "
            "(SELECT COUNT(*) FROM employees WHERE name IN ({})), "
            "(SELECT COUNT(*) FROM payroll_entries WHERE source_filename LIKE 'synthetic-payroll%')".format(
                ",".join("?" for _ in payroll_4p_names)
            ),
            payroll_4p_names,
        ).fetchone()
        _check(tuple(remaining_4p_rows) == (0, 0),
               "payroll 4P exact database cleanup failed")
        conn_payroll.close()
        print("   ✅ Matching, reassignment, new creation, reimport, payload lifecycle, malformed workbooks, isolation, denied-network, and cleanup passed")

        # ── 8b3. Atomic payroll roster validation ──────────────────
        print("\n8b3. Atomic payroll roster validation…")

        payroll_4q_names = (
            "4Q Valid Employee",
            "4Q Zero Rate Employee",
            "4Q Invalid Import Employee",
            "4Q Invalid Assignment Employee",
        )

        def _payroll_4q_snapshot():
            conn = get_connection("company")
            try:
                return tuple(
                    (table, tuple(tuple(row) for row in conn.execute(
                        f"SELECT * FROM {table} ORDER BY id"
                    ).fetchall()))
                    for table in (
                        "employees", "employee_pay_changes", "payroll_entries"
                    )
                )
            finally:
                conn.close()

        conn_payroll = get_connection("company")
        conn_payroll.execute(
            "DELETE FROM employees WHERE name IN ({})".format(
                ",".join("?" for _ in payroll_4q_names)
            ),
            payroll_4q_names,
        )
        conn_payroll.commit()
        conn_payroll.close()

        with app.test_client() as payroll_4q_client:
            payroll_4q_client.set_cookie("entity", "BFM")

            invalid_create_cases = (
                ({"name": "", "role": "Nurses", "pay_type": "hourly", "pay_rate": "1"},
                 "Employee name is required"),
                ({"name": "Invalid", "role": "Unknown", "pay_type": "hourly", "pay_rate": "1"},
                 "valid employee role"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "contract", "pay_rate": "1"},
                 "valid pay type"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "hourly", "pay_rate": "NaN"},
                 "finite non-negative"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "hourly", "pay_rate": "Infinity"},
                 "finite non-negative"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "hourly", "pay_rate": "-1"},
                 "finite non-negative"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "salary", "pay_rate": "1,000,000,000.00"},
                 "supported maximum"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "salary", "pay_rate": "1e999999"},
                 "supported maximum"),
                ({"name": "Invalid", "role": "Nurses", "pay_type": "hourly", "pay_rate": "1", "hire_date": "2026-02-30"},
                 "valid hire date"),
            )
            for form_data, expected_message in invalid_create_cases:
                before = _payroll_4q_snapshot()
                response = payroll_4q_client.post(
                    "/payroll/employees/create",
                    data=form_data,
                    follow_redirects=True,
                )
                _check(
                    response.status_code == 200
                    and expected_message in response.get_data(as_text=True),
                    f"payroll 4Q create validation: uncontrolled {expected_message}",
                )
                _check(
                    _payroll_4q_snapshot() == before,
                    f"payroll 4Q create validation mutated rows for {expected_message}",
                )

            valid_create = payroll_4q_client.post(
                "/payroll/employees/create",
                data={
                    "name": "  4Q Valid Employee  ",
                    "role": "Nurses",
                    "pay_type": "hourly",
                    "pay_rate": "$1,234.567",
                    "hire_date": "2099-12-31",
                    "phoenix_job_code": "  600 Nurse /MA  ",
                },
            )
            zero_create = payroll_4q_client.post(
                "/payroll/employees/create",
                data={
                    "name": "4Q Zero Rate Employee",
                    "role": "Front Office",
                    "pay_type": "hourly",
                    "pay_rate": "",
                },
            )
            _check(
                valid_create.status_code == 302 and zero_create.status_code == 302,
                "payroll 4Q valid create did not redirect",
            )
            conn_payroll = get_connection("company")
            valid_employee = conn_payroll.execute(
                "SELECT * FROM employees WHERE name='4Q Valid Employee'"
            ).fetchone()
            zero_employee = conn_payroll.execute(
                "SELECT * FROM employees WHERE name='4Q Zero Rate Employee'"
            ).fetchone()
            _check(
                valid_employee is not None
                and valid_employee["pay_rate_cents"] == 123457
                and valid_employee["hire_date"] == "2099-12-31"
                and valid_employee["phoenix_job_code"] == "600 Nurse /MA",
                "payroll 4Q valid create did not normalize fields and decimal cents",
            )
            _check(
                zero_employee is not None and zero_employee["pay_rate_cents"] == 0,
                "payroll 4Q empty rate did not preserve zero-rate behavior",
            )
            valid_employee_id = valid_employee["id"]
            zero_employee_id = zero_employee["id"]
            conn_payroll.close()

            invalid_update_cases = (
                {"name": "4Q Valid Employee", "role": "Unknown", "pay_type": "hourly", "pay_rate": "1234.57", "status": "active"},
                {"name": "4Q Valid Employee", "role": "Nurses", "pay_type": "contract", "pay_rate": "1234.57", "status": "active"},
                {"name": "4Q Valid Employee", "role": "Nurses", "pay_type": "hourly", "pay_rate": "-1", "status": "active"},
                {"name": "4Q Valid Employee", "role": "Nurses", "pay_type": "hourly", "pay_rate": "1234.57", "status": "unknown"},
                {"name": "4Q Valid Employee", "role": "Nurses", "pay_type": "hourly", "pay_rate": "1234.57", "status": "active", "hire_date": "2026-13-01"},
            )
            for form_data in invalid_update_cases:
                before = _payroll_4q_snapshot()
                response = payroll_4q_client.post(
                    f"/payroll/employees/update/{valid_employee_id}",
                    data=form_data,
                )
                _check(response.status_code == 302,
                       "payroll 4Q invalid update did not return controlled redirect")
                _check(_payroll_4q_snapshot() == before,
                       "payroll 4Q invalid update changed payroll rows")

            before_missing = _payroll_4q_snapshot()
            missing_update = payroll_4q_client.post(
                "/payroll/employees/update/999999999",
                data={"name": "Missing", "role": "Nurses", "pay_type": "hourly", "pay_rate": "1", "status": "active"},
            )
            _check(
                missing_update.status_code == 302
                and _payroll_4q_snapshot() == before_missing,
                "payroll 4Q missing employee identifier was not a controlled no-op",
            )

            positive_update = payroll_4q_client.post(
                f"/payroll/employees/update/{valid_employee_id}",
                data={
                    "name": "4Q Valid Employee",
                    "role": "Nurses",
                    "pay_type": "hourly",
                    "pay_rate": "1300",
                    "status": "active",
                    "hire_date": "2099-12-31",
                },
            )
            zero_update = payroll_4q_client.post(
                f"/payroll/employees/update/{zero_employee_id}",
                data={
                    "name": "4Q Zero Rate Employee",
                    "role": "Front Office",
                    "pay_type": "hourly",
                    "pay_rate": "25",
                    "status": "active",
                },
            )
            _check(
                positive_update.status_code == 302 and zero_update.status_code == 302,
                "payroll 4Q valid updates did not redirect",
            )
            conn_payroll = get_connection("company")
            positive_history = conn_payroll.execute(
                "SELECT old_rate_cents, new_rate_cents FROM employee_pay_changes "
                "WHERE employee_id=? ORDER BY id",
                (valid_employee_id,),
            ).fetchall()
            zero_history_count = conn_payroll.execute(
                "SELECT COUNT(*) FROM employee_pay_changes WHERE employee_id=?",
                (zero_employee_id,),
            ).fetchone()[0]
            _check(
                [tuple(row) for row in positive_history] == [(123457, 130000)]
                and zero_history_count == 0,
                "payroll 4Q valid rate-history behavior changed",
            )
            conn_payroll.close()

            before_forced_failure = _payroll_4q_snapshot()
            original_log_pay_change = payroll_routes._log_pay_change

            def _log_then_fail(*args, **kwargs):
                original_log_pay_change(*args, **kwargs)
                raise RuntimeError("synthetic 4Q post-history failure")

            try:
                with patch.object(
                    payroll_routes, "_log_pay_change", side_effect=_log_then_fail
                ):
                    payroll_4q_client.post(
                        f"/payroll/employees/update/{valid_employee_id}",
                        data={
                            "name": "4Q Valid Employee",
                            "role": "Nurses",
                            "pay_type": "hourly",
                            "pay_rate": "1400",
                            "status": "active",
                            "hire_date": "2099-12-31",
                        },
                    )
            except RuntimeError as exc:
                _check(
                    str(exc) == "synthetic 4Q post-history failure",
                    "payroll 4Q forced rollback raised an unexpected error",
                )
            else:
                raise AssertionError("payroll 4Q forced rollback did not fail")
            _check(
                _payroll_4q_snapshot() == before_forced_failure,
                "payroll 4Q forced failure did not roll back rate history and employee update",
            )

            invalid_import_workbook = _payroll_workbook_bytes([
                ("4Q Invalid Import Employee", "600 Nurse /MA", 100.0),
            ])
            invalid_assignment_workbook = _payroll_workbook_bytes([
                ("4Q Invalid Assignment Employee", "600 Nurse /MA", 100.0),
            ])
            forced_failure_workbook = _payroll_workbook_bytes([
                ("4Q Invalid Import Employee", "600 Nurse /MA", 100.0),
            ])
            with tempfile.TemporaryDirectory(prefix="payroll_4q_") as payroll_4q_dir, patch.object(
                payroll_routes, "_TEMP_DIR", payroll_4q_dir
            ):
                original_socket = socket.socket

                def _deny_payroll_4q_network(*_args, **_kwargs):
                    raise AssertionError("payroll 4Q attempted outbound networking")

                socket.socket = _deny_payroll_4q_network
                try:
                    _, _, invalid_role_key = _payroll_preview(
                        payroll_4q_client, invalid_import_workbook, "4q-invalid-role.xlsx"
                    )
                    before_invalid_role = _payroll_4q_snapshot()
                    invalid_role_response = payroll_4q_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": invalid_role_key,
                            "assign_4Q Invalid Import Employee": "new",
                            "new_role_4Q Invalid Import Employee": "Unknown",
                        },
                        follow_redirects=True,
                    )
                    _check(
                        invalid_role_response.status_code == 200
                        and "valid employee role" in invalid_role_response.get_data(as_text=True)
                        and _payroll_4q_snapshot() == before_invalid_role,
                        "payroll 4Q invalid import role changed payroll rows",
                    )

                    _, _, forged_name_key = _payroll_preview(
                        payroll_4q_client, invalid_assignment_workbook, "4q-invalid-id.xlsx"
                    )
                    before_forged_name = _payroll_4q_snapshot()
                    forged_name_response = payroll_4q_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": forged_name_key,
                            "assign_Forged Payroll Employee": "new",
                            "new_role_Forged Payroll Employee": "Nurses",
                        },
                        follow_redirects=True,
                    )
                    _check(
                        forged_name_response.status_code == 200
                        and "valid payroll employee assignment" in forged_name_response.get_data(as_text=True)
                        and _payroll_4q_snapshot() == before_forged_name,
                        "payroll 4Q forged import assignment changed payroll rows",
                    )

                    _, _, duplicate_name_key = _payroll_preview(
                        payroll_4q_client, invalid_assignment_workbook, "4q-duplicate-name.xlsx"
                    )
                    before_duplicate_name = _payroll_4q_snapshot()
                    duplicate_name_response = payroll_4q_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": duplicate_name_key,
                            "assign_4Q Invalid Assignment Employee": "new",
                            "new_role_4Q Invalid Assignment Employee": "Nurses",
                            "assign_4q invalid assignment employee": "new",
                            "new_role_4q invalid assignment employee": "Nurses",
                        },
                        follow_redirects=True,
                    )
                    _check(
                        duplicate_name_response.status_code == 200
                        and "only once" in duplicate_name_response.get_data(as_text=True)
                        and _payroll_4q_snapshot() == before_duplicate_name,
                        "payroll 4Q duplicate normalized assignment changed payroll rows",
                    )

                    _, _, invalid_id_key = _payroll_preview(
                        payroll_4q_client, invalid_assignment_workbook, "4q-invalid-id.xlsx"
                    )
                    before_invalid_id = _payroll_4q_snapshot()
                    invalid_id_response = payroll_4q_client.post(
                        "/payroll/import/save",
                        data={
                            "temp_key": invalid_id_key,
                            "assign_4Q Invalid Assignment Employee": "999999999",
                        },
                        follow_redirects=True,
                    )
                    _check(
                        invalid_id_response.status_code == 200
                        and "valid existing employee" in invalid_id_response.get_data(as_text=True)
                        and _payroll_4q_snapshot() == before_invalid_id,
                        "payroll 4Q invalid import identifier changed payroll rows",
                    )

                    _, _, forced_failure_key = _payroll_preview(
                        payroll_4q_client,
                        forced_failure_workbook,
                        "4q-forced-failure.xlsx",
                    )
                    conn_payroll = get_connection("company")
                    conn_payroll.execute(
                        "CREATE TRIGGER payroll_4q_forced_entry_failure "
                        "BEFORE INSERT ON payroll_entries "
                        "WHEN NEW.source_filename='4q-forced-failure.xlsx' "
                        "BEGIN SELECT RAISE(ABORT, 'synthetic 4Q entry failure'); END"
                    )
                    conn_payroll.commit()
                    conn_payroll.close()
                    before_import_failure = _payroll_4q_snapshot()
                    try:
                        payroll_4q_client.post(
                            "/payroll/import/save",
                            data={
                                "temp_key": forced_failure_key,
                                "assign_4Q Invalid Import Employee": "new",
                                "new_role_4Q Invalid Import Employee": "Nurses",
                            },
                        )
                    except sqlite3_module.IntegrityError as exc:
                        _check(
                            "synthetic 4Q entry failure" in str(exc),
                            "payroll 4Q import rollback raised an unexpected error",
                        )
                    else:
                        raise AssertionError(
                            "payroll 4Q import rollback did not force a persistence failure"
                        )
                    finally:
                        conn_payroll = get_connection("company")
                        conn_payroll.execute(
                            "DROP TRIGGER IF EXISTS payroll_4q_forced_entry_failure"
                        )
                        conn_payroll.commit()
                        conn_payroll.close()
                    _check(
                        _payroll_4q_snapshot() == before_import_failure,
                        "payroll 4Q import failure did not roll back roster and payroll rows",
                    )
                    _check(
                        not any(Path(payroll_4q_dir).iterdir()),
                        "payroll 4Q rejected import retained a one-use payload",
                    )
                finally:
                    socket.socket = original_socket

        conn_payroll = get_connection("company")
        conn_payroll.execute(
            "DELETE FROM employees WHERE name IN ({})".format(
                ",".join("?" for _ in payroll_4q_names)
            ),
            payroll_4q_names,
        )
        conn_payroll.commit()
        remaining_4q_rows = conn_payroll.execute(
            "SELECT "
            "(SELECT COUNT(*) FROM employees WHERE name IN ({})), "
            "(SELECT COUNT(*) FROM payroll_entries WHERE source_filename LIKE '4q-%')".format(
                ",".join("?" for _ in payroll_4q_names)
            ),
            payroll_4q_names,
        ).fetchone()
        _check(tuple(remaining_4q_rows) == (0, 0),
               "payroll 4Q exact database cleanup failed")
        conn_payroll.close()
        print("   ✅ Roster domains, decimal rates, zero-mutation rejection, valid history, rollback, import IDs, isolation, denied-network, and cleanup passed")

        # ── 8b4. Like-for-like payroll peer comparisons ─────────────
        print("\n8b4. Like-for-like payroll peer comparisons…")
        payroll_4r_rows = (
            ("4R Hourly Target", "Providers", "hourly", 1000, "active"),
            ("4R Hourly Peer One", "Providers", "hourly", 2000, "active"),
            ("4R Hourly Peer Two", "Providers", "hourly", 4000, "active"),
            ("4R Hourly Inactive", "Providers", "hourly", 9900, "inactive"),
            ("4R Salary Target", "Providers", "salary", 10000000, "active"),
            ("4R Salary Peer", "Providers", "salary", 12000000, "active"),
            ("4R Zero Target", "Nurses", "hourly", 5000, "active"),
            ("4R Zero Peer", "Nurses", "hourly", 0, "active"),
            ("4R Single Target", "Front Office", "hourly", 2500, "active"),
            ("4R Inactive Target", "HR", "salary", 9000000, "inactive"),
            ("4R Active Peer", "HR", "salary", 11000000, "active"),
        )
        payroll_4r_names = tuple(row[0] for row in payroll_4r_rows)
        payroll_4r_baseline = {}
        for entity_key in ("personal", "company", "luxelegacy"):
            conn_payroll = get_connection(entity_key)
            payroll_4r_baseline[entity_key] = tuple(
                conn_payroll.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]
                for table in ("employees", "employee_pay_changes", "payroll_entries")
            )
            conn_payroll.close()

        conn_payroll = get_connection("company")
        conn_payroll.executemany(
            "INSERT INTO employees (name, role, pay_type, pay_rate_cents, status) "
            "VALUES (?, ?, ?, ?, ?)",
            payroll_4r_rows,
        )
        payroll_4r_ids = {
            row["name"]: row["id"]
            for row in conn_payroll.execute(
                "SELECT id, name FROM employees WHERE name IN ({})".format(
                    ",".join("?" for _ in payroll_4r_names)
                ),
                payroll_4r_names,
            ).fetchall()
        }
        conn_payroll.commit()
        conn_payroll.close()

        with app.test_client() as payroll_4r_client, patch(
            "socket.socket",
            side_effect=AssertionError("payroll 4R attempted outbound networking"),
        ):
            payroll_4r_client.set_cookie("entity", "BFM")

            detail_expectations = {
                "4R Hourly Target": (3000, 2, "hourly"),
                "4R Salary Target": (12000000, 1, "salary"),
                "4R Zero Target": (0, 1, "hourly"),
                "4R Single Target": (None, 0, "hourly"),
                "4R Inactive Target": (11000000, 1, "salary"),
            }
            for employee_name, (expected_avg, expected_count, pay_type) in detail_expectations.items():
                response = payroll_4r_client.get(
                    f"/payroll/employees/detail/{payroll_4r_ids[employee_name]}"
                )
                payload = response.get_json()
                _check(
                    response.status_code == 200
                    and payload["peer_avg_cents"] == expected_avg
                    and payload["peer_count"] == expected_count
                    and payload["pay_type"] == pay_type,
                    f"payroll 4R {employee_name}: wrong peer cohort {payload}",
                )

            payroll_page = payroll_4r_client.get("/payroll/")
            payroll_html = payroll_page.get_data(as_text=True)
            payroll_controller_source = (
                PROJECT_ROOT / "web" / "static" / "payroll.js"
            ).read_text()
            _check(
                payroll_page.status_code == 200
                and "Peer Avg (same role and pay type)" in payroll_html
                and "No comparable peers" in payroll_controller_source
                and "data.peer_avg_cents !== null" in payroll_controller_source,
                "payroll 4R display contract is missing labels or explicit empty handling",
            )

            for entity_display in ("Personal", "LL"):
                payroll_4r_client.set_cookie("entity", entity_display)
                denied_response = payroll_4r_client.get(
                    f"/payroll/employees/detail/{payroll_4r_ids['4R Hourly Target']}"
                )
                _check(
                    denied_response.status_code == 302,
                    f"payroll 4R {entity_display}: detail route crossed BFM-only boundary",
                )

        conn_payroll = get_connection("company")
        conn_payroll.execute(
            "DELETE FROM employees WHERE name IN ({})".format(
                ",".join("?" for _ in payroll_4r_names)
            ),
            payroll_4r_names,
        )
        conn_payroll.commit()
        conn_payroll.close()

        for entity_key in ("personal", "company", "luxelegacy"):
            conn_payroll = get_connection(entity_key)
            final_counts = tuple(
                conn_payroll.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]
                for table in ("employees", "employee_pay_changes", "payroll_entries")
            )
            conn_payroll.close()
            _check(
                final_counts == payroll_4r_baseline[entity_key],
                f"payroll 4R {entity_key}: exact cleanup or entity isolation failed",
            )
        print("   ✅ Same-role/pay-type cohorts, self and inactive exclusion, zero/empty distinction, units, isolation, denied-network, and cleanup passed")

        # ── 8c. Luxe Legacy downstream selection boundary ──────────
        print("\n8c. Luxe Legacy downstream selection boundary…")
        # The maintained requirements include requests, but keep this synthetic
        # suite runnable even when the local venv has not installed that optional
        # bridge dependency. The module-level stand-in is always patched below.
        bridge_requests_stub = None
        try:
            import requests as _bridge_requests  # noqa: F401
        except ModuleNotFoundError:
            bridge_requests_stub = Mock()
            sys.modules["requests"] = bridge_requests_stub
        from core.luxury_bridge import push_luxelegacy_to_supabase
        from core.sync_coordination import try_acquire_sync_lease
        from web.routes import kristine as kristine_routes
        from web.routes import plaid as plaid_routes

        bridge_noop_envs = (
            {},
            {"LUXURY_SUPABASE_URL": "https://synthetic.invalid"},
            {"LUXURY_SUPABASE_SERVICE_KEY": "synthetic-service-key"},
        )
        for bridge_noop_env in bridge_noop_envs:
            with patch.dict(
                os.environ, bridge_noop_env, clear=True
            ), patch(
                "core.luxury_bridge.get_connection"
            ) as bridge_noop_connection, patch(
                "core.luxury_bridge.requests.post"
            ) as bridge_noop_post:
                _check(
                    push_luxelegacy_to_supabase() == 0,
                    "bridge configuration: missing either setting should be a no-op",
                )
                _check(
                    bridge_noop_connection.call_count == 0
                    and bridge_noop_post.call_count == 0,
                    "bridge configuration: no-op must not open storage or HTTP",
                )

        invalid_only_connection = Mock()
        invalid_only_connection.execute.return_value.fetchall.return_value = [
            {"plaid_transaction_id": ""},
            {"plaid_transaction_id": "   "},
            {"plaid_transaction_id": "bridge-invalid-duplicate"},
            {"plaid_transaction_id": "bridge-invalid-duplicate"},
        ]
        with patch.dict(os.environ, {
            "LUXURY_SUPABASE_URL": "https://synthetic.invalid",
            "LUXURY_SUPABASE_SERVICE_KEY": "synthetic-service-key",
        }, clear=False), patch(
            "core.luxury_bridge.get_connection",
            return_value=invalid_only_connection,
        ), patch(
            "core.luxury_bridge.requests.post",
        ) as invalid_only_post, patch(
            "core.luxury_bridge.log.warning",
        ) as invalid_only_warning, patch(
            "socket.socket",
            side_effect=AssertionError("invalid-only bridge smoke forbids networking"),
        ):
            invalid_only_count = push_luxelegacy_to_supabase()

        _check(
            invalid_only_count == 0
            and invalid_only_post.call_count == 0
            and invalid_only_connection.close.call_count == 1,
            "bridge validation: an invalid-only selection must close storage and skip HTTP",
        )
        _check(
            invalid_only_warning.call_args.args == (
                "luxury_bridge skipped malformed_rows=%d duplicate_rows=%d "
                "duplicate_keys=%d",
                2,
                2,
                1,
            ),
            "bridge validation: invalid-only warning must expose counts only",
        )

        bridge_rows = (
            ("bridge-owner-draw", "bridge-plaid-owner-draw", "Owner Draw"),
            ("bridge-transfer", "bridge-plaid-transfer", "Internal Transfer"),
            ("bridge-card-payment", "bridge-plaid-card-payment", "Credit Card Payment"),
            ("bridge-valid-cogs", "bridge-plaid-valid-cogs", "Cost of Goods"),
            ("bridge-valid-income", "bridge-plaid-valid-income", "Income"),
            ("bridge-empty-key", "", "Supplies"),
            ("bridge-whitespace-key", "   ", "Supplies"),
            ("bridge-padded-key", " bridge-plaid-padded ", "Supplies"),
            ("bridge-duplicate-a", "bridge-plaid-duplicate", "Supplies"),
            ("bridge-duplicate-b", "bridge-plaid-duplicate", "Fees"),
            ("bridge-null-key", None, "Supplies"),
        )
        conn_bridge = get_connection("luxelegacy")
        for transaction_id, plaid_transaction_id, category in bridge_rows:
            conn_bridge.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_canonical, amount, "
                "amount_cents, account, category, source_filename, imported_at, "
                "plaid_item_id, plaid_transaction_id) "
                "VALUES (?, '2026-07-19', ?, ?, -12.34, -1234, 'Synthetic LL', ?, "
                "'synthetic-bridge', '2026-07-19T00:00:00+00:00', 'bridge-item', ?)",
                (transaction_id, category, category, category, plaid_transaction_id),
            )
        conn_bridge.commit()
        conn_bridge.close()

        bridge_baseline = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in ("personal", "company", "luxelegacy")
        }
        opened_bridge_entities = []
        bridge_response = Mock()
        bridge_response.raise_for_status.return_value = None

        def _tracked_bridge_connection(entity_key):
            opened_bridge_entities.append(entity_key)
            return get_connection(entity_key)

        with patch.dict(os.environ, {
            "LUXURY_SUPABASE_URL": "https://synthetic.invalid",
            "LUXURY_SUPABASE_SERVICE_KEY": "synthetic-service-key",
        }, clear=False), patch(
            "core.luxury_bridge.get_connection",
            side_effect=_tracked_bridge_connection,
        ), patch(
            "core.luxury_bridge.requests.post",
            return_value=bridge_response,
        ) as bridge_post, patch(
            "core.luxury_bridge.log.warning",
        ) as bridge_warning, patch(
            "socket.socket",
            side_effect=AssertionError("bridge smoke forbids outbound networking"),
        ):
            pushed_count = push_luxelegacy_to_supabase()
            repeated_pushed_count = push_luxelegacy_to_supabase()

        _check(opened_bridge_entities == ["luxelegacy", "luxelegacy"],
               "bridge selection: direct execution must read only Luxe Legacy")
        _check(bridge_post.call_count == 2,
               "bridge selection: repeated execution should make one mocked request each")
        bridge_payload = bridge_post.call_args_list[0].kwargs["json"]
        repeated_bridge_payload = bridge_post.call_args_list[1].kwargs["json"]
        payload_categories = {row["category"] for row in bridge_payload}
        payload_keys = [row["plaid_transaction_id"] for row in bridge_payload]
        _check(
            pushed_count == repeated_pushed_count == 2
            and len(bridge_payload) == 2,
               "bridge selection: expected only the two valid LL rows")
        _check(
            bridge_payload == repeated_bridge_payload,
            "bridge selection: repeated payload selection must be deterministic",
        )
        _check(
            payload_keys == ["bridge-plaid-valid-cogs", "bridge-plaid-valid-income"]
            and len(payload_keys) == len(set(payload_keys)),
            "bridge selection: malformed and duplicate keys must stay out",
        )
        _check(payload_categories == {"Cost of Goods", "Income"},
               "bridge selection: Owner Draw, transfers, and card payments must be omitted")
        _check(
            all(
                call.kwargs["params"] == {
                    "on_conflict": "plaid_transaction_id"
                }
                and call.kwargs["timeout"] == 15
                and call.kwargs["headers"]["Prefer"]
                == "resolution=merge-duplicates"
                and call.kwargs["headers"]["apikey"]
                == "synthetic-service-key"
                and call.kwargs["headers"]["Authorization"]
                == "Bearer synthetic-service-key"
                and call.kwargs["headers"]["Content-Type"]
                == "application/json"
                and call.args[0]
                == "https://synthetic.invalid/rest/v1/ledger_transactions"
                for call in bridge_post.call_args_list
            ),
            "bridge request: conflict target path headers and timeout must be explicit",
        )
        _check(
            bridge_warning.call_count == 2
            and all(
                call.args == (
                    "luxury_bridge skipped malformed_rows=%d duplicate_rows=%d "
                    "duplicate_keys=%d",
                    3,
                    2,
                    1,
                )
                for call in bridge_warning.call_args_list
            ),
            "bridge validation: warnings must expose sanitized counts only",
        )
        _check(all(
            _database_snapshot(entity_key) == bridge_baseline[entity_key]
            for entity_key in ("personal", "company", "luxelegacy")
        ), "bridge selection: mirror reads must not mutate any entity database")

        bridge_failure_response = Mock()
        bridge_failure_response.raise_for_status.side_effect = RuntimeError(
            "synthetic downstream failure"
        )
        with patch.dict(os.environ, {
            "LUXURY_SUPABASE_URL": "https://synthetic.invalid",
            "LUXURY_SUPABASE_SERVICE_KEY": "synthetic-service-key",
        }, clear=False), patch(
            "core.luxury_bridge.requests.post",
            return_value=bridge_failure_response,
        ) as bridge_failure_post, patch(
            "core.luxury_bridge.log.warning",
        ) as bridge_failure_warning, patch(
            "socket.socket",
            side_effect=AssertionError("bridge failure smoke forbids outbound networking"),
        ):
            failed_pushed_count = push_luxelegacy_to_supabase()

        _check(
            failed_pushed_count == 0 and bridge_failure_post.call_count == 1,
            "bridge failure: downstream failure must remain isolated and return zero",
        )
        _check(
            bridge_failure_warning.call_count == 2
            and bridge_failure_warning.call_args_list[0].args == (
                "luxury_bridge skipped malformed_rows=%d duplicate_rows=%d "
                "duplicate_keys=%d",
                3,
                2,
                1,
            )
            and bridge_failure_warning.call_args_list[1].args[0]
            == "luxury_bridge push failed: %s",
            "bridge failure: warnings must stay sanitized and omit row identifiers",
        )
        _check(all(
            _database_snapshot(entity_key) == bridge_baseline[entity_key]
            for entity_key in ("personal", "company", "luxelegacy")
        ), "bridge failure: all entity databases must remain unchanged")

        for entity_key in ("personal", "company", "luxelegacy"):
            conn_bridge = get_connection(entity_key)
            conn_bridge.execute(
                "INSERT INTO plaid_items "
                "(item_id, access_token, institution_name, created_at) "
                "VALUES (?, 'synthetic-token', 'Synthetic Bridge Bank', "
                "'2026-07-19T00:00:00+00:00')",
                (f"bridge-item-{entity_key}",),
            )
            conn_bridge.commit()
            conn_bridge.close()

        empty_sync_result = {
            "added": [],
            "modified": [],
            "removed": [],
            "next_cursor": "synthetic-bridge-cursor",
        }
        with patch.dict(os.environ, {
            "PLAID_CLIENT_ID": "synthetic-client",
            "PLAID_SECRET": "synthetic-secret",
        }, clear=False), patch(
            "core.crypto.decrypt_token",
            return_value="synthetic-decrypted-token",
        ), patch(
            "core.plaid_client.get_transactions",
            return_value=empty_sync_result,
        ), patch(
            "core.luxury_bridge.push_luxelegacy_to_supabase",
            return_value=0,
        ) as scheduled_bridge, patch(
            "socket.socket",
            side_effect=AssertionError("scheduled bridge smoke forbids outbound networking"),
        ):
            plaid_routes._sync_entity("personal")
            plaid_routes._sync_entity("company")
            _check(scheduled_bridge.call_count == 0,
                   "scheduled bridge: Personal and BFM must not invoke the LL mirror")
            plaid_routes._sync_entity("luxelegacy")
            _check(scheduled_bridge.call_count == 1,
                   "scheduled bridge: Luxe Legacy must invoke the mirror exactly once")

        with patch.dict(os.environ, {
            "PLAID_CLIENT_ID": "synthetic-client",
            "PLAID_SECRET": "synthetic-secret",
        }, clear=False), patch(
            "core.crypto.decrypt_token",
            return_value="synthetic-decrypted-token",
        ), patch(
            "core.plaid_client.get_transactions",
            return_value=empty_sync_result,
        ), patch(
            "core.luxury_bridge.push_luxelegacy_to_supabase",
            return_value=0,
        ) as public_bridge, patch(
            "socket.socket",
            side_effect=AssertionError("public bridge smoke forbids outbound networking"),
        ):
            public_lease = try_acquire_sync_lease()
            _check(public_lease is not None,
                   "public bridge: background worker should acquire the shared lease")
            kristine_routes._background_sync(public_lease)
            _check(public_bridge.call_count == 1,
                   "public bridge: Personal plus LL worker must invoke the mirror once")

        for entity_key in ("personal", "company", "luxelegacy"):
            conn_bridge = get_connection(entity_key)
            conn_bridge.execute(
                "DELETE FROM plaid_items WHERE item_id=?",
                (f"bridge-item-{entity_key}",),
            )
            conn_bridge.commit()
            conn_bridge.close()
        conn_bridge = get_connection("luxelegacy")
        conn_bridge.executemany(
            "DELETE FROM transactions WHERE transaction_id=?",
            [(transaction_id,) for transaction_id, _, _ in bridge_rows],
        )
        conn_bridge.commit()
        conn_bridge.close()
        if bridge_requests_stub is not None:
            sys.modules.pop("requests", None)
        print("   ✅ Owner Draw stays local, valid LL rows remain eligible, and both sync seams are LL-only")

        # ── 8d. Scheduled sync result truthfulness ──────────────────
        print("\n8d. Scheduled sync result truthfulness…")

        def _scheduled_result(*, errors=None, skipped=False):
            result = {
                "new": 0,
                "modified": 0,
                "removed": 0,
                "backfilled": 0,
                "errors": list(errors or []),
            }
            if skipped:
                result["skipped"] = True
            return result

        scheduled_secret = "synthetic-sync-secret"
        scheduled_headers = {"Authorization": f"Bearer {scheduled_secret}"}
        complete_results = {
            "personal": _scheduled_result(),
            "company": _scheduled_result(skipped=True),
            "luxelegacy": _scheduled_result(),
        }
        partial_results = {
            "personal": _scheduled_result(),
            "company": _scheduled_result(errors=["synthetic item failure"]),
            "luxelegacy": _scheduled_result(skipped=True),
        }
        failed_results = {
            entity_key: _scheduled_result(errors=[f"synthetic {entity_key} failure"])
            for entity_key in ("personal", "company", "luxelegacy")
        }

        def _result_side_effect(result_map):
            return lambda entity_key: result_map[entity_key]

        scheduled_env = {
            "SYNC_SECRET": scheduled_secret,
            "PLAID_CLIENT_ID": "synthetic-client",
            "PLAID_SECRET": "synthetic-secret",
        }
        with app.test_client() as scheduled_client, patch.dict(
            os.environ, scheduled_env, clear=False
        ), patch(
            "socket.socket",
            side_effect=AssertionError("scheduled result smoke forbids outbound networking"),
        ):
            missing_bearer = scheduled_client.post("/plaid/sync-all")
            _check(missing_bearer.status_code == 401,
                   "scheduled result: missing bearer should remain 401")
            wrong_bearer = scheduled_client.post(
                "/plaid/sync-all",
                headers={"Authorization": "Bearer wrong-synthetic-secret"},
            )
            _check(wrong_bearer.status_code == 401,
                   "scheduled result: wrong bearer should remain 401")
            _check(scheduled_secret not in wrong_bearer.get_data(as_text=True),
                   "scheduled result: configured bearer secret must not be echoed")

            with patch("web.routes.plaid._sync_entity",
                       side_effect=_result_side_effect(complete_results)) as complete_sync:
                complete_response = scheduled_client.post(
                    "/plaid/sync-all", headers=scheduled_headers
                )
            complete_body = complete_response.get_json()
            _check(complete_response.status_code == 200,
                   "scheduled result: complete success should return 200")
            _check(complete_body["ok"] is True and complete_body["status"] == "success",
                   "scheduled result: complete success should be top-level success")
            _check(complete_body["results"] == complete_results,
                   "scheduled result: complete per-entity results should be preserved")
            _check(
                [call.args[0] for call in complete_sync.call_args_list]
                == ["personal", "company", "luxelegacy"],
                "scheduled result: entity order should remain Personal, BFM, Luxe Legacy",
            )

            with patch("web.routes.plaid._sync_entity",
                       side_effect=_result_side_effect(partial_results)):
                partial_response = scheduled_client.post(
                    "/plaid/sync-all", headers=scheduled_headers
                )
            partial_body = partial_response.get_json()
            _check(partial_response.status_code == 502,
                   "scheduled result: partial failure should return 502")
            _check(
                partial_body["ok"] is False
                and partial_body["status"] == "partial_failure",
                "scheduled result: one failed entity should be top-level partial failure",
            )
            _check(partial_body["results"] == partial_results,
                   "scheduled result: partial per-entity results should be preserved")

            with patch("web.routes.plaid._sync_entity",
                       side_effect=_result_side_effect(failed_results)):
                failed_response = scheduled_client.post(
                    "/plaid/sync-all", headers=scheduled_headers
                )
            failed_body = failed_response.get_json()
            _check(failed_response.status_code == 502,
                   "scheduled result: all-entity failure should return 502")
            _check(
                failed_body["ok"] is False and failed_body["status"] == "failure",
                "scheduled result: all failed entities should be top-level failure",
            )
            _check(failed_body["results"] == failed_results,
                   "scheduled result: failed per-entity results should be preserved")

            contention_lease = try_acquire_sync_lease()
            _check(contention_lease is not None,
                   "scheduled result: smoke test should acquire an idle shared lease")
            try:
                contention_response = scheduled_client.post(
                    "/plaid/sync-all", headers=scheduled_headers
                )
            finally:
                contention_lease.close()
            _check(contention_response.status_code == 429,
                   "scheduled result: lock contention should remain 429")

            with patch("web.routes.plaid.log.warning"), patch(
                "web.routes.plaid._sync_entity",
                side_effect=RuntimeError("synthetic sensitive route exception"),
            ) as exception_sync:
                exception_response = scheduled_client.post(
                    "/plaid/sync-all", headers=scheduled_headers
                )
            exception_body = exception_response.get_json()
            _check(exception_response.status_code == 502,
                   "scheduled result: unexpected entity exceptions should be structured 502")
            _check(
                exception_body["ok"] is False
                and exception_body["status"] == "failure"
                and set(exception_body["results"]) == {"personal", "company", "luxelegacy"},
                "scheduled result: every entity should receive a structured failure disposition",
            )
            _check(exception_sync.call_count == 3,
                   "scheduled result: one entity exception must not abort later entities")
            _check(
                all(
                    result["errors"] == ["entity sync failed"]
                    for result in exception_body["results"].values()
                ),
                "scheduled result: unexpected entity errors should remain stable and sanitized",
            )
            _check("sensitive" not in exception_response.get_data(as_text=True),
                   "scheduled result: raw exception detail must not enter workflow JSON")
            released_lease = try_acquire_sync_lease()
            _check(released_lease is not None,
                   "scheduled result: entity exceptions should release the shared lease")
            released_lease.close()

        with patch.dict(os.environ, {"SYNC_SECRET": ""}, clear=False):
            with app.test_client() as scheduled_client:
                missing_config = scheduled_client.post("/plaid/sync-all")
        _check(missing_config.status_code == 500,
               "scheduled result: missing SYNC_SECRET should remain 500")

        with patch.dict(os.environ, {
            "SYNC_SECRET": scheduled_secret,
            "PLAID_CLIENT_ID": "",
            "PLAID_SECRET": "",
        }, clear=False):
            with app.test_client() as scheduled_client:
                missing_plaid_config = scheduled_client.post(
                    "/plaid/sync-all", headers=scheduled_headers
                )
        _check(missing_plaid_config.status_code == 500,
               "scheduled result: missing Plaid configuration should remain 500")

        from werkzeug.serving import WSGIRequestHandler, make_server

        class _SilentLocalRequestHandler(WSGIRequestHandler):
            def log(self, log_type, message, *args):
                pass

        local_server = make_server(
            "127.0.0.1", 0, app, request_handler=_SilentLocalRequestHandler
        )
        local_thread = threading.Thread(target=local_server.serve_forever, daemon=True)
        local_thread.start()
        try:
            with patch.dict(os.environ, scheduled_env, clear=False), patch(
                "web.routes.plaid._sync_entity",
                side_effect=_result_side_effect(partial_results),
            ):
                curl_result = subprocess.run(
                    [
                        "curl",
                        "--fail",
                        "--noproxy",
                        "127.0.0.1",
                        "--max-time",
                        "5",
                        "-X",
                        "POST",
                        f"http://127.0.0.1:{local_server.server_port}/plaid/sync-all",
                        "-H",
                        f"Authorization: Bearer {scheduled_secret}",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
        finally:
            local_server.shutdown()
            local_thread.join(timeout=5)
            local_server.server_close()
        _check(curl_result.returncode == 22,
               "scheduled result: curl --fail should reject partial failure with exit 22")
        _check(scheduled_secret not in curl_result.stdout + curl_result.stderr,
               "scheduled result: curl output must not echo the bearer secret")
        _check("curl --fail" in (PROJECT_ROOT / ".github/workflows/daily-plaid-sync.yml").read_text(),
               "scheduled result: workflow should retain the curl --fail contract")
        print("   ✅ Partial and total failures are workflow-visible; success and skip behavior remain truthful")

        # ── 8d2. Sync entry coordination and recovery ──────────────
        print("\n8d2. Sync entry coordination and recovery…")

        first_lease = try_acquire_sync_lease()
        _check(first_lease is not None,
               "sync coordination: first same-process open should acquire the lease")
        second_lease = try_acquire_sync_lease()
        _check(second_lease is None,
               "sync coordination: a separate same-process open must contend")
        first_lease.close()
        reacquired_lease = try_acquire_sync_lease()
        _check(reacquired_lease is not None,
               "sync coordination: normal close should make the lease reacquirable")
        reacquired_lease.close()

        lock_path = Path(tmpdir) / ".plaid-sync.lock"
        _check(lock_path.exists() and lock_path.stat().st_mode & 0o777 == 0o600,
               "sync coordination: stable lock inode should exist with mode 0600")

        holder_code = (
            "from core.sync_coordination import try_acquire_sync_lease; "
            "lease=try_acquire_sync_lease(); "
            "assert lease is not None; "
            "print('acquired', flush=True); "
            "input(); lease.close()"
        )
        contender_code = (
            "import sys; from core.sync_coordination import try_acquire_sync_lease; "
            "lease=try_acquire_sync_lease(); "
            "sys.exit(0 if lease is None else 1)"
        )
        child_env = os.environ.copy()
        child_env["PYTHONPATH"] = str(PROJECT_ROOT)

        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=child_env,
        )
        _check(holder.stdout.readline().strip() == "acquired",
               "sync coordination: holder process should acquire the lease")
        contender = subprocess.run(
            [sys.executable, "-c", contender_code],
            capture_output=True,
            text=True,
            env=child_env,
            check=False,
        )
        _check(contender.returncode == 0,
               "sync coordination: second process should observe contention")
        holder.stdin.write("\n")
        holder.stdin.flush()
        _check(holder.wait(timeout=5) == 0,
               "sync coordination: holder should exit cleanly after release")
        post_release = try_acquire_sync_lease()
        _check(post_release is not None,
               "sync coordination: another process release should be observable")
        post_release.close()

        killed_holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=child_env,
        )
        _check(killed_holder.stdout.readline().strip() == "acquired",
               "sync coordination: SIGKILL holder should first acquire the lease")
        killed_holder.kill()
        killed_holder.wait(timeout=5)
        post_kill = try_acquire_sync_lease()
        _check(post_kill is not None,
               "sync coordination: process death should release the kernel lease")
        post_kill.close()

        configured_auth_env = {
            **scheduled_env,
            "APP_PASSWORD_HASH": "0" * 64,
            "FLASK_SECRET": "configured-auth-sync-smoke-secret",
        }
        with patch.dict(os.environ, configured_auth_env, clear=False):
            configured_auth_app = create_app()
        configured_auth_app.config["TESTING"] = True
        with patch.dict(os.environ, configured_auth_env, clear=False), \
                configured_auth_app.test_client() as configured_auth_client, patch(
            "web.init_db"
        ) as request_init, patch(
            "web.sync_categories_from_file"
        ) as request_category_sync, patch(
            "web.routes.plaid.init_db"
        ) as route_init, patch(
            "web.routes.plaid._sync_entity",
            side_effect=_result_side_effect(complete_results),
        ):
            auth_missing = configured_auth_client.post("/plaid/sync-all")
            _check(auth_missing.status_code == 401,
                   "sync auth order: missing bearer should be 401 rather than login redirect")
            _check(auth_missing.headers.get("Location") is None,
                   "sync auth order: bearer endpoint must not redirect to session login")
            _check(request_init.call_count == 0 and request_category_sync.call_count == 0,
                   "sync auth order: unauthorized request must not run normal entity setup")
            _check(route_init.call_count == 0,
                   "sync auth order: unauthorized request must not initialize scheduled entities")

            auth_success = configured_auth_client.post(
                "/plaid/sync-all", headers=scheduled_headers
            )
            _check(auth_success.status_code == 200,
                   "sync auth order: correct bearer should reach the scheduled view under configured auth")
            _check(auth_success.headers.get("Location") is None,
                   "sync auth order: correct bearer must not receive a login redirect")
            _check(request_init.call_count == 0 and request_category_sync.call_count == 0,
                   "sync auth order: scheduled endpoint must remain outside normal request setup")
            _check(
                [call.args[0] for call in route_init.call_args_list]
                == ["personal", "company", "luxelegacy"],
                "sync auth order: authorized scheduled work should initialize each entity in order",
            )

        with app.test_client() as manual_client, patch.dict(
            os.environ, scheduled_env, clear=False
        ):
            manual_client.set_cookie("entity", "Personal")
            manual_contention = try_acquire_sync_lease()
            _check(manual_contention is not None,
                   "sync coordination: manual contention setup should acquire the lease")
            try:
                manual_response = manual_client.post("/plaid/sync")
            finally:
                manual_contention.close()
            _check(manual_response.status_code == 302,
                   "sync coordination: manual contention should preserve redirect behavior")
            with manual_client.session_transaction() as manual_session:
                manual_flashes = manual_session.get("_flashes", [])
            _check(
                any("already in progress" in message for _, message in manual_flashes),
                "sync coordination: manual contention should preserve user-facing notice",
            )

        from web.routes import kristine as sync_kristine_routes

        successful_lease = Mock()
        successful_thread = Mock()
        successful_thread.start.return_value = None
        sync_kristine_routes._last_sync_time = 0.0
        with patch(
            "web.routes.plaid._plaid_available", return_value=True
        ), patch(
            "web.routes.kristine.try_acquire_sync_lease",
            return_value=successful_lease,
        ), patch(
            "web.routes.kristine.threading.Thread",
            return_value=successful_thread,
        ), patch("time.monotonic", return_value=1000.0):
            launch_success = sync_kristine_routes._start_background_sync()
        _check(launch_success is True and sync_kristine_routes._last_sync_time == 1000.0,
               "dashboard launch: successful start should consume the throttle window")
        _check(successful_thread.start.call_count == 1,
               "dashboard launch: successful path should start exactly one worker")
        _check(successful_lease.close.call_count == 0,
               "dashboard launch: successful start should transfer lease ownership to worker")

        failed_lease = Mock()
        failed_thread = Mock()
        failed_thread.start.side_effect = RuntimeError("synthetic thread start failure")
        sync_kristine_routes._last_sync_time = 0.0
        with patch(
            "web.routes.plaid._plaid_available", return_value=True
        ), patch(
            "web.routes.kristine.try_acquire_sync_lease",
            return_value=failed_lease,
        ), patch(
            "web.routes.kristine.threading.Thread",
            return_value=failed_thread,
        ), patch("time.monotonic", return_value=1000.0):
            try:
                sync_kristine_routes._start_background_sync()
                failed_launch_raised = False
            except RuntimeError:
                failed_launch_raised = True
        _check(failed_launch_raised and sync_kristine_routes._last_sync_time == 0.0,
               "dashboard launch: failed start should remain immediately retryable")
        _check(failed_lease.close.call_count == 1,
               "dashboard launch: failed start should release the shared lease")

        sync_kristine_routes._last_sync_time = 0.0
        with patch(
            "web.routes.plaid._plaid_available", return_value=True
        ), patch(
            "web.routes.kristine.try_acquire_sync_lease", return_value=None
        ), patch("time.monotonic", return_value=1000.0):
            launch_contended = sync_kristine_routes._start_background_sync()
        _check(launch_contended is False and sync_kristine_routes._last_sync_time == 0.0,
               "dashboard launch: shared contention must not consume the throttle window")

        sync_kristine_routes._last_sync_time = 500.0
        with patch(
            "web.routes.plaid._plaid_available", return_value=True
        ), patch(
            "web.routes.kristine.try_acquire_sync_lease"
        ) as throttled_acquire, patch("time.monotonic", return_value=1000.0):
            launch_throttled = sync_kristine_routes._start_background_sync()
        _check(launch_throttled is False and throttled_acquire.call_count == 0,
               "dashboard launch: process-local throttle should avoid lease churn")
        sync_kristine_routes._last_sync_time = 0.0

        successful_lease.close()

        dashboard_item = "sync-entry-dashboard-personal"
        dashboard_vendor_item = "sync-entry-dashboard-vendor"
        dashboard_account = "sync-entry-dashboard-account"
        dashboard_plaid_id = "sync-entry-dashboard-removed"
        dashboard_transaction_id = "sync-entry-dashboard-transaction"
        conn_dashboard = get_connection("personal")
        conn_dashboard.execute(
            "INSERT INTO plaid_items "
            "(item_id, access_token, institution_name, cursor, is_vendor, created_at) "
            "VALUES (?, 'synthetic-dashboard-token', 'Synthetic Dashboard Bank', "
            "'dashboard-start', 0, '2026-07-19T00:00:00+00:00')",
            (dashboard_item,),
        )
        conn_dashboard.execute(
            "INSERT INTO plaid_items "
            "(item_id, access_token, institution_name, cursor, is_vendor, created_at) "
            "VALUES (?, 'synthetic-vendor-token', 'Synthetic Vendor Bank', "
            "'vendor-start', 1, '2026-07-19T00:00:00+00:00')",
            (dashboard_vendor_item,),
        )
        conn_dashboard.execute(
            "INSERT INTO plaid_accounts "
            "(item_id, account_id, name, mask, type, subtype, enabled) "
            "VALUES (?, ?, 'Synthetic Dashboard Account', '0000', 'depository', "
            "'checking', 1)",
            (dashboard_item, dashboard_account),
        )
        conn_dashboard.execute(
            "INSERT INTO transactions "
            "(transaction_id, date, description_raw, merchant_raw, amount, amount_cents, "
            "account, source_filename, imported_at, plaid_item_id, plaid_transaction_id) "
            "VALUES (?, '2026-07-19', 'Dashboard Removed', 'Dashboard Removed', -1.23, "
            "-123, 'Synthetic Dashboard Account', 'plaid', "
            "'2026-07-19T00:00:00+00:00', ?, ?)",
            (dashboard_transaction_id, dashboard_item, dashboard_plaid_id),
        )
        conn_dashboard.execute(
            "INSERT INTO transaction_splits "
            "(transaction_id, description, amount_cents, category, subcategory) "
            "VALUES (?, 'Dashboard split', -123, 'Food', 'General')",
            (dashboard_transaction_id,),
        )
        conn_dashboard.commit()
        conn_dashboard.close()

        dashboard_sync_result = {
            "added": [],
            "modified": [],
            "removed": [dashboard_plaid_id],
            "next_cursor": "dashboard-final",
        }
        dashboard_worker_lease = try_acquire_sync_lease()
        _check(dashboard_worker_lease is not None,
               "dashboard core reuse: worker should acquire the shared lease")
        with patch.dict(os.environ, scheduled_env, clear=False), patch(
            "core.crypto.decrypt_token", return_value="synthetic-dashboard-decrypted"
        ), patch(
            "core.plaid_client.get_transactions", return_value=dashboard_sync_result
        ) as dashboard_plaid, patch(
            "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
        ) as dashboard_bridge, patch(
            "socket.socket",
            side_effect=AssertionError("dashboard core reuse forbids outbound networking"),
        ):
            sync_kristine_routes._background_sync(dashboard_worker_lease)

        conn_dashboard = get_connection("personal")
        dashboard_state = conn_dashboard.execute(
            "SELECT cursor FROM plaid_items WHERE item_id=?", (dashboard_item,)
        ).fetchone()
        dashboard_vendor_state = conn_dashboard.execute(
            "SELECT cursor FROM plaid_items WHERE item_id=?", (dashboard_vendor_item,)
        ).fetchone()
        dashboard_removed = conn_dashboard.execute(
            "SELECT transaction_id FROM transactions WHERE transaction_id=?",
            (dashboard_transaction_id,),
        ).fetchone()
        dashboard_removed_split = conn_dashboard.execute(
            "SELECT id FROM transaction_splits WHERE transaction_id=?",
            (dashboard_transaction_id,),
        ).fetchone()
        _check(
            dashboard_state["cursor"] == "dashboard-final"
            and dashboard_vendor_state["cursor"] == "vendor-start"
            and dashboard_removed is None
            and dashboard_removed_split is None,
            "dashboard core reuse: removal and cursor must be atomic while vendor state remains untouched",
        )
        _check(dashboard_plaid.call_count == 1,
               "dashboard core reuse: vendor item must not reach Plaid transaction sync")
        _check(dashboard_bridge.call_count == 0,
               "dashboard core reuse: empty LL scope must not create a duplicate bridge call")
        conn_dashboard.execute(
            "DELETE FROM plaid_accounts WHERE item_id=?", (dashboard_item,)
        )
        conn_dashboard.execute(
            "DELETE FROM plaid_items WHERE item_id IN (?, ?)",
            (dashboard_item, dashboard_vendor_item),
        )
        conn_dashboard.commit()
        conn_dashboard.close()

        print("   ✅ Shared lease, crash cleanup, configured auth, launch retry, core reuse, removal, and vendor isolation passed")

        # ── 8e. Plaid transaction and cursor atomicity ──────────────
        print("\n8e. Plaid transaction and cursor atomicity…")
        from core.plaid_client import get_transactions as fetch_plaid_transactions
        from web.routes import plaid as atomic_plaid_routes

        page_one_txn = Mock(
            transaction_id="atomic-page-one",
            date="2026-07-18",
            amount=10.0,
            name="Atomic Page One",
            merchant_name=None,
            account_id="atomic-page-account",
        )
        page_two_txn = Mock(
            transaction_id="atomic-page-two",
            date="2026-07-19",
            amount=20.0,
            name="Atomic Page Two",
            merchant_name="Atomic Merchant",
            account_id="atomic-page-account",
        )
        page_one = Mock(
            added=[page_one_txn],
            modified=[],
            removed=[],
            next_cursor="atomic-page-cursor-1",
            has_more=True,
        )
        page_two = Mock(
            added=[page_two_txn],
            modified=[],
            removed=[],
            next_cursor="atomic-page-cursor-final",
            has_more=False,
        )
        paginated_client = Mock()
        paginated_client.transactions_sync.side_effect = [page_one, page_two]
        with patch(
            "core.plaid_client._get_client", return_value=paginated_client
        ), patch(
            "socket.socket",
            side_effect=AssertionError("Plaid atomicity smoke forbids outbound networking"),
        ):
            paginated_result = fetch_plaid_transactions(
                "synthetic-access-token", cursor="atomic-page-cursor-start"
            )
        _check(paginated_client.transactions_sync.call_count == 2,
               "Plaid atomicity: all available mocked pages should be fetched")
        _check(
            [txn["plaid_transaction_id"] for txn in paginated_result["added"]]
            == ["atomic-page-one", "atomic-page-two"]
            and paginated_result["next_cursor"] == "atomic-page-cursor-final",
            "Plaid atomicity: pagination should aggregate updates and return only the final cursor",
        )

        atomic_start_cursor = "atomic-cursor-start"
        atomic_start_synced = "2026-07-01T00:00:00+00:00"

        def _seed_atomic_item(entity_key, item_id, *, with_existing=True):
            enabled_account = f"{item_id}-enabled"
            disabled_account = f"{item_id}-disabled"
            conn_atomic = get_connection(entity_key)
            conn_atomic.execute(
                "INSERT INTO plaid_items "
                "(item_id, access_token, institution_name, created_at, cursor, last_synced) "
                "VALUES (?, 'synthetic-encrypted-token', 'Synthetic Atomic Bank', "
                "'2026-07-01T00:00:00+00:00', ?, ?)",
                (item_id, atomic_start_cursor, atomic_start_synced),
            )
            conn_atomic.execute(
                "INSERT INTO plaid_accounts "
                "(item_id, account_id, name, enabled) VALUES (?, ?, 'Enabled Checking', 1)",
                (item_id, enabled_account),
            )
            conn_atomic.execute(
                "INSERT INTO plaid_accounts "
                "(item_id, account_id, name, enabled) VALUES (?, ?, 'Disabled Checking', 0)",
                (item_id, disabled_account),
            )
            existing = {}
            if with_existing:
                for role in ("modify", "remove", "unrelated"):
                    transaction_id = f"{item_id}-{role}-row"
                    plaid_transaction_id = f"{item_id}-{role}-plaid"
                    conn_atomic.execute(
                        "INSERT INTO transactions "
                        "(transaction_id, date, description_raw, amount, amount_cents, "
                        "account, category, source_filename, imported_at, plaid_item_id, "
                        "plaid_transaction_id) VALUES (?, '2026-07-01', ?, -10.0, -1000, "
                        "'Enabled Checking', 'Food', 'atomicity-smoke', "
                        "'2026-07-01T00:00:00+00:00', ?, ?)",
                        (transaction_id, f"ORIGINAL {role.upper()}", item_id,
                         plaid_transaction_id),
                    )
                    existing[role] = (transaction_id, plaid_transaction_id)
                conn_atomic.execute(
                    "INSERT INTO transaction_splits "
                    "(transaction_id, description, amount_cents, category, subcategory) "
                    "VALUES (?, 'atomic split', -1000, 'Food', 'General')",
                    (existing["remove"][0],),
                )
            conn_atomic.commit()
            conn_atomic.close()
            return enabled_account, disabled_account, existing

        def _clean_atomic_item(entity_key, item_id):
            conn_atomic = get_connection(entity_key)
            conn_atomic.execute(
                "DELETE FROM transaction_splits WHERE transaction_id IN "
                "(SELECT transaction_id FROM transactions WHERE plaid_item_id=?)",
                (item_id,),
            )
            conn_atomic.execute(
                "DELETE FROM transactions WHERE plaid_item_id=?", (item_id,)
            )
            conn_atomic.execute(
                "DELETE FROM plaid_accounts WHERE item_id=?", (item_id,)
            )
            conn_atomic.execute("DELETE FROM plaid_items WHERE item_id=?", (item_id,))
            conn_atomic.commit()
            conn_atomic.close()

        for entity_key in ("personal", "company", "luxelegacy"):
            item_id = f"atomic-success-{entity_key}"
            enabled_account, disabled_account, existing = _seed_atomic_item(
                entity_key, item_id
            )
            accepted_added_id = f"{item_id}-accepted-add"
            disabled_added_id = f"{item_id}-disabled-add"
            successful_sync = {
                "added": [
                    {
                        "plaid_transaction_id": accepted_added_id,
                        "account_id": enabled_account,
                        "date": "2026-07-19",
                        "amount": 12.34,
                        "name": "ATOMIC ACCEPTED ADD",
                    },
                    {
                        "plaid_transaction_id": disabled_added_id,
                        "account_id": disabled_account,
                        "date": "2026-07-19",
                        "amount": 99.99,
                        "name": "ATOMIC DISABLED ADD",
                    },
                ],
                "modified": [{
                    "plaid_transaction_id": existing["modify"][1],
                    "account_id": enabled_account,
                    "date": "2026-07-19",
                    "amount": 22.22,
                    "name": "ATOMIC MODIFIED",
                }],
                "removed": [existing["remove"][1]],
                "next_cursor": f"atomic-cursor-final-{entity_key}",
            }
            with patch(
                "core.crypto.decrypt_token", return_value="synthetic-decrypted-token"
            ), patch(
                "core.plaid_client.get_transactions", return_value=successful_sync
            ) as successful_fetch, patch(
                "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
            ), patch(
                "socket.socket",
                side_effect=AssertionError("Plaid atomicity smoke forbids outbound networking"),
            ):
                successful_result = atomic_plaid_routes._sync_entity(entity_key)

            successful_fetch.assert_called_once_with(
                "synthetic-decrypted-token", cursor=atomic_start_cursor
            )
            _check(
                successful_result["new"] == 1
                and successful_result["modified"] == 1
                and successful_result["removed"] == 1
                and successful_result["errors"] == [],
                f"Plaid atomicity {entity_key}: committed counters should match accepted changes",
            )
            conn_atomic = get_connection(entity_key)
            item_row = conn_atomic.execute(
                "SELECT cursor, last_synced FROM plaid_items WHERE item_id=?", (item_id,)
            ).fetchone()
            accepted_row = conn_atomic.execute(
                "SELECT amount_cents, account FROM transactions "
                "WHERE plaid_transaction_id=?", (accepted_added_id,)
            ).fetchone()
            disabled_row = conn_atomic.execute(
                "SELECT transaction_id FROM transactions WHERE plaid_transaction_id=?",
                (disabled_added_id,),
            ).fetchone()
            modified_row = conn_atomic.execute(
                "SELECT description_raw, amount_cents FROM transactions "
                "WHERE plaid_transaction_id=?", (existing["modify"][1],)
            ).fetchone()
            removed_row = conn_atomic.execute(
                "SELECT transaction_id FROM transactions WHERE plaid_transaction_id=?",
                (existing["remove"][1],),
            ).fetchone()
            removed_split = conn_atomic.execute(
                "SELECT id FROM transaction_splits WHERE transaction_id=?",
                (existing["remove"][0],),
            ).fetchone()
            unrelated_row = conn_atomic.execute(
                "SELECT description_raw FROM transactions WHERE transaction_id=?",
                (existing["unrelated"][0],),
            ).fetchone()
            conn_atomic.close()
            _check(
                item_row["cursor"] == f"atomic-cursor-final-{entity_key}"
                and item_row["last_synced"] != atomic_start_synced,
                f"Plaid atomicity {entity_key}: final cursor and timestamp should commit together",
            )
            _check(
                accepted_row is not None
                and accepted_row["amount_cents"] == -1234
                and accepted_row["account"] == "Enabled Checking"
                and disabled_row is None,
                f"Plaid atomicity {entity_key}: signs and enabled-account filtering should remain intact",
            )
            _check(
                modified_row["description_raw"] == "ATOMIC MODIFIED"
                and modified_row["amount_cents"] == -2222
                and removed_row is None
                and removed_split is None
                and unrelated_row["description_raw"] == "ORIGINAL UNRELATED",
                f"Plaid atomicity {entity_key}: modify, remove, split, and unrelated-row behavior should remain correct",
            )

            redelivery_sync = {
                "added": [successful_sync["added"][0]],
                "modified": [],
                "removed": [],
                "next_cursor": f"atomic-cursor-redelivery-{entity_key}",
            }
            with patch(
                "core.crypto.decrypt_token", return_value="synthetic-decrypted-token"
            ), patch(
                "core.plaid_client.get_transactions", return_value=redelivery_sync
            ), patch(
                "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
            ), patch(
                "socket.socket",
                side_effect=AssertionError("Plaid atomicity smoke forbids outbound networking"),
            ):
                redelivery_result = atomic_plaid_routes._sync_entity(entity_key)
            conn_atomic = get_connection(entity_key)
            redelivery_count = conn_atomic.execute(
                "SELECT COUNT(*) FROM transactions WHERE plaid_transaction_id=?",
                (accepted_added_id,),
            ).fetchone()[0]
            redelivery_cursor = conn_atomic.execute(
                "SELECT cursor FROM plaid_items WHERE item_id=?", (item_id,)
            ).fetchone()[0]
            conn_atomic.close()
            _check(
                redelivery_result["new"] == 0
                and redelivery_result["errors"] == []
                and redelivery_count == 1
                and redelivery_cursor == f"atomic-cursor-redelivery-{entity_key}",
                f"Plaid atomicity {entity_key}: exact redelivery should be idempotent while advancing the cursor",
            )
            _clean_atomic_item(entity_key, item_id)

        for entity_key in ("personal", "company", "luxelegacy"):
            for failure_mode in ("add", "modify", "remove", "cursor"):
                item_id = f"atomic-{failure_mode}-{entity_key}"
                enabled_account, _, existing = _seed_atomic_item(entity_key, item_id)
                prior_add_id = f"{item_id}-prior-add"
                failing_add_id = f"{item_id}-failing-add"
                failure_result = {
                    "added": [{
                        "plaid_transaction_id": prior_add_id,
                        "account_id": enabled_account,
                        "date": "2026-07-19",
                        "amount": 1.11,
                        "name": "ATOMIC PRIOR ADD",
                    }],
                    "modified": [],
                    "removed": [],
                    "next_cursor": f"atomic-{failure_mode}-cursor-final",
                }
                trigger_name = f"atomic_{failure_mode}_failure"
                conn_atomic = get_connection(entity_key)
                if failure_mode == "add":
                    failure_result["added"].append({
                        "plaid_transaction_id": failing_add_id,
                        "account_id": enabled_account,
                        "date": "2026-07-19",
                        "amount": 2.22,
                        "name": "ATOMIC FAILING ADD",
                    })
                    conn_atomic.execute(
                        f"CREATE TRIGGER {trigger_name} BEFORE INSERT ON transactions "
                        f"WHEN NEW.plaid_transaction_id='{failing_add_id}' "
                        "BEGIN SELECT RAISE(ABORT, 'synthetic add failure'); END"
                    )
                elif failure_mode == "modify":
                    failure_result["modified"] = [{
                        "plaid_transaction_id": existing["modify"][1],
                        "account_id": enabled_account,
                        "date": "2026-07-19",
                        "amount": 3.33,
                        "name": "ATOMIC FAILING MODIFY",
                    }]
                    conn_atomic.execute(
                        f"CREATE TRIGGER {trigger_name} BEFORE UPDATE OF description_raw "
                        "ON transactions "
                        f"WHEN OLD.plaid_transaction_id='{existing['modify'][1]}' "
                        "BEGIN SELECT RAISE(ABORT, 'synthetic modify failure'); END"
                    )
                elif failure_mode == "remove":
                    failure_result["removed"] = [existing["remove"][1]]
                    conn_atomic.execute(
                        f"CREATE TRIGGER {trigger_name} BEFORE DELETE ON transactions "
                        f"WHEN OLD.plaid_transaction_id='{existing['remove'][1]}' "
                        "BEGIN SELECT RAISE(ABORT, 'synthetic remove failure'); END"
                    )
                else:
                    conn_atomic.execute(
                        f"CREATE TRIGGER {trigger_name} BEFORE UPDATE OF cursor ON plaid_items "
                        f"WHEN OLD.item_id='{item_id}' "
                        "BEGIN SELECT RAISE(ABORT, 'synthetic cursor failure'); END"
                    )
                conn_atomic.commit()
                conn_atomic.close()

                with patch(
                    "core.crypto.decrypt_token", return_value="synthetic-decrypted-token"
                ), patch(
                    "core.plaid_client.get_transactions", return_value=failure_result
                ) as failed_fetch, patch(
                    "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
                ), patch(
                    "socket.socket",
                    side_effect=AssertionError("Plaid atomicity smoke forbids outbound networking"),
                ):
                    failed_result = atomic_plaid_routes._sync_entity(entity_key)
                failed_fetch.assert_called_once_with(
                    "synthetic-decrypted-token", cursor=atomic_start_cursor
                )
                _check(
                    failed_result["new"] == 0
                    and failed_result["modified"] == 0
                    and failed_result["removed"] == 0
                    and len(failed_result["errors"]) == 1
                    and f"synthetic {failure_mode} failure"
                    not in failed_result["errors"][0]
                    and "transaction persistence failed; cursor unchanged"
                    in failed_result["errors"][0],
                    f"Plaid atomicity {entity_key}/{failure_mode}: rolled-back counters must not be reported",
                )
                conn_atomic = get_connection(entity_key)
                failed_item = conn_atomic.execute(
                    "SELECT cursor, last_synced FROM plaid_items WHERE item_id=?", (item_id,)
                ).fetchone()
                prior_add = conn_atomic.execute(
                    "SELECT transaction_id FROM transactions WHERE plaid_transaction_id=?",
                    (prior_add_id,),
                ).fetchone()
                target_row = conn_atomic.execute(
                    "SELECT description_raw FROM transactions WHERE transaction_id=?",
                    (existing["modify"][0] if failure_mode == "modify" else existing["remove"][0],),
                ).fetchone()
                remove_split = conn_atomic.execute(
                    "SELECT id FROM transaction_splits WHERE transaction_id=?",
                    (existing["remove"][0],),
                ).fetchone()
                unrelated_row = conn_atomic.execute(
                    "SELECT description_raw FROM transactions WHERE transaction_id=?",
                    (existing["unrelated"][0],),
                ).fetchone()
                conn_atomic.execute(f"DROP TRIGGER {trigger_name}")
                conn_atomic.commit()
                conn_atomic.close()
                _check(
                    failed_item["cursor"] == atomic_start_cursor
                    and failed_item["last_synced"] == atomic_start_synced
                    and prior_add is None,
                    f"Plaid atomicity {entity_key}/{failure_mode}: partial writes and cursor movement must roll back",
                )
                _check(
                    target_row is not None
                    and target_row["description_raw"].startswith("ORIGINAL")
                    and remove_split is not None
                    and unrelated_row["description_raw"] == "ORIGINAL UNRELATED",
                    f"Plaid atomicity {entity_key}/{failure_mode}: existing rows and splits must remain intact",
                )

                with patch(
                    "core.crypto.decrypt_token", return_value="synthetic-decrypted-token"
                ), patch(
                    "core.plaid_client.get_transactions", return_value=failure_result
                ) as retry_fetch, patch(
                    "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
                ), patch(
                    "socket.socket",
                    side_effect=AssertionError("Plaid atomicity smoke forbids outbound networking"),
                ):
                    retry_result = atomic_plaid_routes._sync_entity(entity_key)
                retry_fetch.assert_called_once_with(
                    "synthetic-decrypted-token", cursor=atomic_start_cursor
                )
                conn_atomic = get_connection(entity_key)
                retry_cursor = conn_atomic.execute(
                    "SELECT cursor FROM plaid_items WHERE item_id=?", (item_id,)
                ).fetchone()[0]
                conn_atomic.close()
                _check(
                    retry_result["errors"] == []
                    and retry_cursor == f"atomic-{failure_mode}-cursor-final",
                    f"Plaid atomicity {entity_key}/{failure_mode}: retry from the original cursor should succeed",
                )
                _clean_atomic_item(entity_key, item_id)

        for entity_key in ("personal", "company", "luxelegacy"):
            conn_atomic = get_connection(entity_key)
            _check(
                conn_atomic.execute(
                    "SELECT COUNT(*) FROM plaid_items WHERE item_id LIKE 'atomic-%'"
                ).fetchone()[0] == 0
                and conn_atomic.execute(
                    "SELECT COUNT(*) FROM plaid_accounts WHERE item_id LIKE 'atomic-%'"
                ).fetchone()[0] == 0
                and conn_atomic.execute(
                    "SELECT COUNT(*) FROM transactions WHERE plaid_item_id LIKE 'atomic-%'"
                ).fetchone()[0] == 0,
                f"Plaid atomicity {entity_key}: synthetic item state should be cleaned exactly",
            )
            conn_atomic.close()
        print("   ✅ All-entity pagination, atomic commit, rollback, retry, idempotency, filtering, and cleanup passed")

        # ── 8f. Plaid account-state truthfulness ───────────────────
        print("\n8f. Plaid account-state truthfulness…")
        import datetime as account_datetime
        import sqlite3

        from core.db import _MIGRATIONS
        from web.routes import cashflow as account_state_routes

        # Prove the additive populated upgrade path from schema 57 to 58.
        upgrade_root = Path(tmpdir) / "plaid-account-state-upgrade"
        upgrade_root.mkdir()
        upgrade_db = upgrade_root / "personal.sqlite"
        upgrade_conn = sqlite3.connect(upgrade_db)
        upgrade_conn.execute(
            "CREATE TABLE schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        for version, migration_sql in _MIGRATIONS:
            if version > 57:
                break
            upgrade_conn.executescript(migration_sql)
            upgrade_conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, 'synthetic')",
                (version,),
            )
        upgrade_conn.execute(
            "INSERT INTO plaid_items "
            "(item_id, access_token, institution_name, created_at) "
            "VALUES ('acctstate-upgrade-item', 'synthetic-token', "
            "'Synthetic Upgrade Bank', '2026-07-01T00:00:00')"
        )
        upgrade_conn.commit()
        upgrade_conn.close()
        original_data_dir = os.environ["DATA_DIR"]
        os.environ["DATA_DIR"] = str(upgrade_root)
        try:
            init_db("personal")
            upgrade_conn = get_connection("personal")
            upgrade_columns = {
                row["name"] for row in upgrade_conn.execute(
                    "PRAGMA table_info(plaid_items)"
                ).fetchall()
            }
            upgrade_item = upgrade_conn.execute(
                "SELECT item_id, accounts_last_synced, liabilities_last_synced "
                "FROM plaid_items WHERE item_id='acctstate-upgrade-item'"
            ).fetchone()
            upgrade_version = upgrade_conn.execute(
                "SELECT MAX(version) FROM schema_version"
            ).fetchone()[0]
            upgrade_conn.close()
        finally:
            os.environ["DATA_DIR"] = original_data_dir
        _check(
            {"accounts_last_synced", "liabilities_last_synced"} <= upgrade_columns
            and upgrade_item is not None
            and upgrade_item["accounts_last_synced"] is None
            and upgrade_item["liabilities_last_synced"] is None
            and upgrade_version == 58,
            "Plaid account state: populated schema-57 upgrade should preserve the item and add null freshness markers",
        )

        fresh_marker = account_datetime.datetime.now().isoformat()

        def _seed_account_state(entity_key):
            prefix = f"acctstate-{entity_key}"
            conn_state = get_connection(entity_key)
            items = {
                "success": f"{prefix}-success",
                "failure": f"{prefix}-failure",
                "fresh": f"{prefix}-fresh",
                "empty": f"{prefix}-empty",
                "liability_empty": f"{prefix}-liability-empty",
            }
            for role, item_id in items.items():
                account_marker = fresh_marker if role in ("fresh", "liability_empty") else None
                liability_marker = fresh_marker if role == "fresh" else None
                conn_state.execute(
                    "INSERT INTO plaid_items "
                    "(item_id, access_token, institution_name, created_at, "
                    "accounts_last_synced, liabilities_last_synced) "
                    "VALUES (?,?,?,?,?,?)",
                    (
                        item_id,
                        f"{prefix}-token-{role}",
                        f"AcctState {role.title()} Bank",
                        "2026-07-01T00:00:00",
                        account_marker,
                        liability_marker,
                    ),
                )

            account_ids = {
                "enabled": f"{prefix}-enabled-card",
                "disabled": f"{prefix}-disabled-card",
                "removed": f"{prefix}-removed-card",
                "investment": f"{prefix}-investment",
                "failure": f"{prefix}-failure-card",
                "fresh": f"{prefix}-fresh-card",
                "empty": f"{prefix}-empty-card",
                "liability_empty": f"{prefix}-liability-empty-card",
            }
            account_specs = [
                (items["success"], account_ids["enabled"], "Enabled Card", "credit", 1),
                (items["success"], account_ids["disabled"], "Disabled Card", "credit", 0),
                (items["success"], account_ids["removed"], "Removed Card", "credit", 1),
                (items["success"], account_ids["investment"], "Investment", "investment", 1),
                (items["failure"], account_ids["failure"], "Failure Card", "credit", 1),
                (items["fresh"], account_ids["fresh"], "Fresh Card", "credit", 1),
                (items["empty"], account_ids["empty"], "Empty Disabled Card", "credit", 0),
                (items["liability_empty"], account_ids["liability_empty"], "Empty Liability Card", "credit", 1),
            ]
            for item_id, account_id, name, acct_type, enabled in account_specs:
                conn_state.execute(
                    "INSERT INTO plaid_accounts "
                    "(item_id, account_id, name, type, enabled) VALUES (?,?,?,?,?)",
                    (item_id, account_id, name, acct_type, enabled),
                )
                conn_state.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, plaid_account_id, "
                    "account_type, payment_amount_cents, payment_due_day, updated_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (
                        f"AcctState {name} {entity_key}",
                        10000,
                        "plaid",
                        account_id,
                        "credit_card" if acct_type == "credit" else "bank",
                        2500,
                        15,
                        "2026-07-01T00:00:00",
                    ),
                )
            manual_name = f"Chase Emergency Reserve AcctState {entity_key}"
            conn_state.execute(
                "INSERT INTO account_balances "
                "(account_name, balance_cents, balance_source, account_type, updated_at) "
                "VALUES (?, 77700, 'manual', 'bank', '2026-07-01T00:00:00')",
                (manual_name,),
            )
            conn_state.commit()
            conn_state.close()
            return items, account_ids, manual_name

        def _account_payload(account_id, name, *, acct_type="credit", balance=321.0):
            return {
                "account_id": account_id,
                "name": name,
                "mask": "4242",
                "type": acct_type,
                "subtype": "credit card" if acct_type == "credit" else "brokerage",
                "balance_current": balance,
                "balance_limit": 5000.0 if acct_type == "credit" else None,
            }

        entity_labels = {"personal": "Personal", "company": "BFM", "luxelegacy": "LL"}
        for entity_key in ("personal", "company", "luxelegacy"):
            items, account_ids, manual_name = _seed_account_state(entity_key)
            account_calls = []

            def _mock_accounts(token):
                account_calls.append(token)
                if token.endswith("token-failure"):
                    raise RuntimeError("synthetic account fetch failure")
                if token.endswith("token-success"):
                    return [
                        _account_payload(account_ids["enabled"], "Enabled Card", balance=432.1),
                        _account_payload(account_ids["disabled"], "Disabled Card"),
                        _account_payload(
                            account_ids["investment"], "Investment", acct_type="investment"
                        ),
                    ]
                if token.endswith("token-empty"):
                    return [_account_payload(account_ids["empty"], "Empty Disabled Card")]
                raise AssertionError(f"unexpected account refresh for {token}")

            conn_state = get_connection(entity_key)
            with patch.dict(
                os.environ,
                {"PLAID_CLIENT_ID": "synthetic-client", "PLAID_SECRET": "synthetic-secret"},
                clear=False,
            ), patch(
                "core.crypto.decrypt_token", side_effect=lambda token: token
            ), patch(
                "core.plaid_client.get_accounts", side_effect=_mock_accounts
            ), patch.object(
                account_state_routes.log, "warning"
            ), patch(
                "socket.socket",
                side_effect=AssertionError("Plaid account-state smoke forbids outbound networking"),
            ):
                account_state_routes._sync_plaid_accounts(conn_state, entity_key)
            success_marker = conn_state.execute(
                "SELECT accounts_last_synced FROM plaid_items WHERE item_id=?",
                (items["success"],),
            ).fetchone()[0]
            failure_marker = conn_state.execute(
                "SELECT accounts_last_synced FROM plaid_items WHERE item_id=?",
                (items["failure"],),
            ).fetchone()[0]
            empty_marker = conn_state.execute(
                "SELECT accounts_last_synced FROM plaid_items WHERE item_id=?",
                (items["empty"],),
            ).fetchone()[0]
            balances = {
                row["plaid_account_id"]: dict(row) for row in conn_state.execute(
                    "SELECT * FROM account_balances WHERE plaid_account_id LIKE ?",
                    (f"acctstate-{entity_key}-%",),
                ).fetchall()
            }
            manual_row = conn_state.execute(
                "SELECT id, balance_cents FROM account_balances WHERE account_name=?",
                (manual_name,),
            ).fetchone()
            _check(
                success_marker is not None
                and empty_marker is not None
                and failure_marker is None
                and balances[account_ids["enabled"]]["balance_cents"] == 43210,
                f"Plaid account state {entity_key}: successful items should refresh and failed items should retain stale markers",
            )
            _check(
                account_ids["disabled"] not in balances
                and account_ids["removed"] not in balances
                and account_ids["investment"] not in balances
                and account_ids["empty"] not in balances
                and account_ids["failure"] in balances,
                f"Plaid account state {entity_key}: authoritative cleanup must stay per item and support an empty keep set",
            )
            _check(
                manual_row is not None
                and manual_row["balance_cents"] == 77700
                and f"acctstate-{entity_key}-token-fresh" not in account_calls
                and f"acctstate-{entity_key}-token-liability_empty" not in account_calls,
                f"Plaid account state {entity_key}: manual rows and fresh sibling items must remain untouched",
            )

            liability_calls = []

            def _mock_liabilities(token):
                liability_calls.append(token)
                if token.endswith("token-failure"):
                    raise RuntimeError("synthetic liability fetch failure")
                if token.endswith("token-success"):
                    return {
                        account_ids["enabled"]: {
                            "balance": 654.32,
                            "credit_limit": 6000.0,
                            "next_payment_due_date": "2026-08-22",
                            "minimum_payment_amount": 45.67,
                        }
                    }
                return {}

            account_rows = [dict(row) for row in conn_state.execute(
                "SELECT * FROM account_balances ORDER BY id"
            ).fetchall()]
            accts = {
                "banks": [row for row in account_rows if row["account_type"] != "credit_card"],
                "cards": [row for row in account_rows if row["account_type"] == "credit_card"],
            }
            with patch.dict(
                os.environ,
                {"PLAID_CLIENT_ID": "synthetic-client", "PLAID_SECRET": "synthetic-secret"},
                clear=False,
            ), patch(
                "core.crypto.decrypt_token", side_effect=lambda token: token
            ), patch(
                "core.plaid_client.get_liabilities", side_effect=_mock_liabilities
            ), patch.object(
                account_state_routes.log, "warning"
            ), patch(
                "socket.socket",
                side_effect=AssertionError("Plaid liability smoke forbids outbound networking"),
            ):
                fetched_liabilities = account_state_routes._fetch_plaid_liabilities(conn_state)
                account_state_routes._apply_plaid_liabilities(
                    accts, fetched_liabilities, conn_state
                )

            success_liability = conn_state.execute(
                "SELECT balance_cents, credit_limit_cents, payment_amount_cents, "
                "payment_due_day FROM account_balances WHERE plaid_account_id=?",
                (account_ids["enabled"],),
            ).fetchone()
            failure_liability = conn_state.execute(
                "SELECT balance_cents, payment_amount_cents, payment_due_day "
                "FROM account_balances WHERE plaid_account_id=?",
                (account_ids["failure"],),
            ).fetchone()
            empty_liability = conn_state.execute(
                "SELECT balance_cents, payment_amount_cents, payment_due_day "
                "FROM account_balances WHERE plaid_account_id=?",
                (account_ids["liability_empty"],),
            ).fetchone()
            item_markers = {
                row["item_id"]: row["liabilities_last_synced"]
                for row in conn_state.execute(
                    "SELECT item_id, liabilities_last_synced FROM plaid_items "
                    "WHERE item_id LIKE ?",
                    (f"acctstate-{entity_key}-%",),
                ).fetchall()
            }
            conn_state.close()
            _check(
                success_liability["balance_cents"] == 65432
                and success_liability["credit_limit_cents"] == 600000
                and success_liability["payment_amount_cents"] == 4567
                and success_liability["payment_due_day"] == 22
                and item_markers[items["success"]] is not None,
                f"Plaid account state {entity_key}: normal stale load should apply liabilities independently from balances",
            )
            _check(
                failure_liability["balance_cents"] == 10000
                and failure_liability["payment_amount_cents"] == 2500
                and failure_liability["payment_due_day"] == 15
                and item_markers[items["failure"]] is None,
                f"Plaid account state {entity_key}: liability failure should preserve last-known-good values and freshness",
            )
            _check(
                empty_liability["balance_cents"] == 10000
                and empty_liability["payment_amount_cents"] == 2500
                and empty_liability["payment_due_day"] == 15
                and item_markers[items["liability_empty"]] is not None
                and f"acctstate-{entity_key}-token-fresh" not in liability_calls,
                f"Plaid account state {entity_key}: successful empty liability response must be distinguishable from failure",
            )

            with app.test_client() as toggle_client:
                toggle_client.set_cookie("entity", entity_labels[entity_key])
                with toggle_client.session_transaction() as toggle_session:
                    toggle_session["_csrf_token"] = f"acctstate-toggle-csrf-{entity_key}"
                toggle_response = toggle_client.post(
                    f"/plaid/toggle-account/{account_ids['fresh']}",
                    headers={"X-CSRF-Token": f"acctstate-toggle-csrf-{entity_key}"},
                )
            conn_state = get_connection(entity_key)
            toggled = conn_state.execute(
                "SELECT pa.enabled, pi.accounts_last_synced, pi.liabilities_last_synced "
                "FROM plaid_accounts pa JOIN plaid_items pi ON pi.item_id=pa.item_id "
                "WHERE pa.account_id=?",
                (account_ids["fresh"],),
            ).fetchone()
            conn_state.close()
            _check(
                toggle_response.status_code == 302
                and toggled["enabled"] == 0
                and toggled["accounts_last_synced"] is None
                and toggled["liabilities_last_synced"] is None,
                f"Plaid account state {entity_key}: account toggle should invalidate both item freshness markers",
            )

            link_item_id = f"acctstate-{entity_key}-link"
            failed_link_item_id = f"acctstate-{entity_key}-failed-link"
            link_account_id = f"acctstate-{entity_key}-link-card"
            with app.test_client() as link_client:
                link_client.set_cookie("entity", entity_labels[entity_key])
                with link_client.session_transaction() as link_session:
                    link_session["_csrf_token"] = f"acctstate-csrf-{entity_key}"
                with patch.dict(
                    os.environ,
                    {"PLAID_CLIENT_ID": "synthetic-client", "PLAID_SECRET": "synthetic-secret"},
                    clear=False,
                ), patch(
                    "core.plaid_client.exchange_public_token",
                    return_value={"access_token": "acctstate-link-token", "item_id": link_item_id},
                ), patch(
                    "core.plaid_client.get_accounts",
                    return_value=[_account_payload(link_account_id, "Chase Preferred")],
                ), patch(
                    "core.crypto.encrypt_token", return_value="acctstate-encrypted-link-token"
                ), patch(
                    "socket.socket",
                    side_effect=AssertionError("Plaid link smoke forbids outbound networking"),
                ):
                    link_response = link_client.post(
                        "/plaid/exchange-token",
                        json={
                            "public_token": "acctstate-public-token",
                            "institution_name": "Chase",
                            "institution_id": "acctstate-chase",
                        },
                        headers={"X-CSRF-Token": f"acctstate-csrf-{entity_key}"},
                    )
                with patch.dict(
                    os.environ,
                    {"PLAID_CLIENT_ID": "synthetic-client", "PLAID_SECRET": "synthetic-secret"},
                    clear=False,
                ), patch(
                    "core.plaid_client.exchange_public_token",
                    return_value={
                        "access_token": "acctstate-failed-link-token",
                        "item_id": failed_link_item_id,
                    },
                ), patch(
                    "core.plaid_client.get_accounts",
                    side_effect=RuntimeError("synthetic failed account fetch"),
                ), patch.object(
                    atomic_plaid_routes.log, "exception"
                ):
                    failed_link_response = link_client.post(
                        "/plaid/exchange-token",
                        json={
                            "public_token": "acctstate-failed-public-token",
                            "institution_name": "Chase",
                            "institution_id": "acctstate-chase",
                        },
                        headers={"X-CSRF-Token": f"acctstate-csrf-{entity_key}"},
                    )
            conn_state = get_connection(entity_key)
            preserved_manual = conn_state.execute(
                "SELECT id, balance_cents FROM account_balances WHERE account_name=?",
                (manual_name,),
            ).fetchone()
            stored_link = conn_state.execute(
                "SELECT item_id FROM plaid_items WHERE item_id=?", (link_item_id,)
            ).fetchone()
            failed_link = conn_state.execute(
                "SELECT item_id FROM plaid_items WHERE item_id=?", (failed_link_item_id,)
            ).fetchone()
            _check(
                link_response.status_code == 200
                and failed_link_response.status_code == 500
                and preserved_manual is not None
                and preserved_manual["balance_cents"] == 77700
                and stored_link is not None
                and failed_link is None,
                f"Plaid account state {entity_key}: similar-name manual rows must survive successful and failed link exchange",
            )

            conn_state.execute(
                "DELETE FROM account_balances WHERE plaid_account_id LIKE ? "
                "OR account_name LIKE ?",
                (f"acctstate-{entity_key}-%", f"%AcctState {entity_key}"),
            )
            conn_state.execute(
                "DELETE FROM plaid_accounts WHERE item_id LIKE ?",
                (f"acctstate-{entity_key}-%",),
            )
            conn_state.execute(
                "DELETE FROM plaid_items WHERE item_id LIKE ?",
                (f"acctstate-{entity_key}-%",),
            )
            conn_state.commit()
            _check(
                conn_state.execute(
                    "SELECT COUNT(*) FROM plaid_items WHERE item_id LIKE ?",
                    (f"acctstate-{entity_key}-%",),
                ).fetchone()[0] == 0
                and conn_state.execute(
                    "SELECT COUNT(*) FROM plaid_accounts WHERE item_id LIKE ?",
                    (f"acctstate-{entity_key}-%",),
                ).fetchone()[0] == 0
                and conn_state.execute(
                    "SELECT COUNT(*) FROM account_balances WHERE plaid_account_id LIKE ? "
                    "OR account_name LIKE ?",
                    (f"acctstate-{entity_key}-%", f"%AcctState {entity_key}"),
                ).fetchone()[0] == 0,
                f"Plaid account state {entity_key}: synthetic state should be cleaned exactly",
            )
            conn_state.close()

        print("   ✅ Additive migration, per-item reconciliation, manual preservation, liability freshness, link safety, isolation, and cleanup passed")

        # ── 8g. Plaid item isolation and truthful observability ────
        print("\n8g. Plaid item isolation and truthful observability…")
        from web.routes import plaid as isolation_plaid_routes

        isolation_start_cursor = "isolation-cursor-start"
        isolation_start_synced = "2026-07-01T00:00:00+00:00"

        def _seed_isolation_item(
            entity_key, item_id, encrypted_token, created_at, institution_name
        ):
            account_id = f"{item_id}-account"
            conn_isolation = get_connection(entity_key)
            conn_isolation.execute(
                "INSERT INTO plaid_items "
                "(item_id, access_token, institution_name, created_at, cursor, last_synced) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item_id,
                    encrypted_token,
                    institution_name,
                    created_at,
                    isolation_start_cursor,
                    isolation_start_synced,
                ),
            )
            conn_isolation.execute(
                "INSERT INTO plaid_accounts "
                "(item_id, account_id, name, enabled) "
                "VALUES (?, ?, 'Isolation Checking', 1)",
                (item_id, account_id),
            )
            conn_isolation.commit()
            conn_isolation.close()
            return account_id

        def _seed_isolation_transaction(
            entity_key, item_id, plaid_transaction_id, role
        ):
            transaction_id = f"{item_id}-{role}-row"
            conn_isolation = get_connection(entity_key)
            conn_isolation.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, amount, amount_cents, "
                "account, category, source_filename, imported_at, plaid_item_id, "
                "plaid_transaction_id) VALUES (?, '2026-07-01', ?, -10.0, -1000, "
                "'Isolation Checking', 'Food', 'isolation-smoke', "
                "'2026-07-01T00:00:00+00:00', ?, ?)",
                (
                    transaction_id,
                    f"ISOLATION ORIGINAL {role.upper()}",
                    item_id,
                    plaid_transaction_id,
                ),
            )
            conn_isolation.commit()
            conn_isolation.close()
            return transaction_id

        def _clean_isolation_state(entity_key):
            conn_isolation = get_connection(entity_key)
            conn_isolation.execute(
                "DELETE FROM transaction_splits WHERE transaction_id IN "
                "(SELECT transaction_id FROM transactions "
                "WHERE plaid_item_id LIKE 'isolation-%')"
            )
            conn_isolation.execute(
                "DELETE FROM transactions WHERE plaid_item_id LIKE 'isolation-%'"
            )
            conn_isolation.execute(
                "DELETE FROM plaid_accounts WHERE item_id LIKE 'isolation-%'"
            )
            conn_isolation.execute(
                "DELETE FROM plaid_items WHERE item_id LIKE 'isolation-%'"
            )
            conn_isolation.commit()
            conn_isolation.close()

        for entity_key in ("personal", "company", "luxelegacy"):
            for corrupt_first in (True, False):
                order_label = "corrupt-first" if corrupt_first else "corrupt-last"
                corrupt_item = f"isolation-{order_label}-corrupt-{entity_key}"
                healthy_item = f"isolation-{order_label}-healthy-{entity_key}"
                corrupt_token = f"synthetic-corrupt-ciphertext-{order_label}-{entity_key}"
                healthy_token = f"synthetic-healthy-ciphertext-{order_label}-{entity_key}"
                healthy_decrypted = f"synthetic-healthy-token-{order_label}-{entity_key}"
                corrupt_created = (
                    "2026-07-01T00:00:00+00:00"
                    if corrupt_first
                    else "2026-07-01T00:01:00+00:00"
                )
                healthy_created = (
                    "2026-07-01T00:01:00+00:00"
                    if corrupt_first
                    else "2026-07-01T00:00:00+00:00"
                )
                _seed_isolation_item(
                    entity_key,
                    corrupt_item,
                    corrupt_token,
                    corrupt_created,
                    "Synthetic Corrupt Bank",
                )
                healthy_account = _seed_isolation_item(
                    entity_key,
                    healthy_item,
                    healthy_token,
                    healthy_created,
                    "Synthetic Healthy Bank",
                )
                healthy_plaid_id = f"{healthy_item}-added"

                def _decrypt_isolation_token(token):
                    if token == corrupt_token:
                        raise ValueError(f"cannot decrypt {token}")
                    if token == healthy_token:
                        return healthy_decrypted
                    raise AssertionError("unexpected synthetic token")

                healthy_result = {
                    "added": [{
                        "plaid_transaction_id": healthy_plaid_id,
                        "account_id": healthy_account,
                        "date": "2026-07-19",
                        "amount": 4.56,
                        "name": "ISOLATION HEALTHY ADD",
                    }],
                    "modified": [],
                    "removed": [],
                    "next_cursor": f"isolation-{order_label}-healthy-final-{entity_key}",
                }
                with patch(
                    "core.crypto.decrypt_token",
                    side_effect=_decrypt_isolation_token,
                ), patch(
                    "core.plaid_client.get_transactions", return_value=healthy_result
                ) as isolation_fetch, patch(
                    "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
                ), patch(
                    "socket.socket",
                    side_effect=AssertionError(
                        "Plaid item isolation smoke forbids outbound networking"
                    ),
                ):
                    isolation_result = isolation_plaid_routes._sync_entity(entity_key)

                isolation_fetch.assert_called_once_with(
                    healthy_decrypted, cursor=isolation_start_cursor
                )
                _check(
                    isolation_result["new"] == 1
                    and isolation_result["modified"] == 0
                    and isolation_result["removed"] == 0
                    and len(isolation_result["errors"]) == 1
                    and "Synthetic Corrupt Bank: access token unavailable"
                    == isolation_result["errors"][0]
                    and corrupt_token not in isolation_result["errors"][0]
                    and healthy_token not in isolation_result["errors"][0]
                    and healthy_decrypted not in isolation_result["errors"][0],
                    f"Plaid item isolation {entity_key}/{order_label}: corrupt tokens must be isolated and sanitized",
                )
                conn_isolation = get_connection(entity_key)
                corrupt_state = conn_isolation.execute(
                    "SELECT cursor, last_synced FROM plaid_items WHERE item_id=?",
                    (corrupt_item,),
                ).fetchone()
                healthy_state = conn_isolation.execute(
                    "SELECT cursor, last_synced FROM plaid_items WHERE item_id=?",
                    (healthy_item,),
                ).fetchone()
                healthy_row = conn_isolation.execute(
                    "SELECT amount_cents FROM transactions WHERE plaid_transaction_id=?",
                    (healthy_plaid_id,),
                ).fetchone()
                conn_isolation.close()
                _check(
                    corrupt_state["cursor"] == isolation_start_cursor
                    and corrupt_state["last_synced"] == isolation_start_synced
                    and healthy_state["cursor"]
                    == f"isolation-{order_label}-healthy-final-{entity_key}"
                    and healthy_state["last_synced"] != isolation_start_synced
                    and healthy_row is not None
                    and healthy_row["amount_cents"] == -456,
                    f"Plaid item isolation {entity_key}/{order_label}: healthy siblings must commit while failed item state is preserved",
                )
                _clean_isolation_state(entity_key)

        for entity_key in ("personal", "company", "luxelegacy"):
            missing_item = f"isolation-missing-modified-{entity_key}"
            healthy_item = f"isolation-missing-healthy-{entity_key}"
            missing_token = f"synthetic-missing-token-{entity_key}"
            healthy_token = f"synthetic-missing-healthy-token-{entity_key}"
            missing_account = _seed_isolation_item(
                entity_key,
                missing_item,
                missing_token,
                "2026-07-01T00:00:00+00:00",
                "Synthetic Missing Bank",
            )
            healthy_account = _seed_isolation_item(
                entity_key,
                healthy_item,
                healthy_token,
                "2026-07-01T00:01:00+00:00",
                "Synthetic Healthy Sibling",
            )
            rolled_back_add = f"{missing_item}-rolled-back-add"
            healthy_add = f"{healthy_item}-committed-add"
            missing_result = {
                "added": [{
                    "plaid_transaction_id": rolled_back_add,
                    "account_id": missing_account,
                    "date": "2026-07-19",
                    "amount": 1.23,
                    "name": "ISOLATION ROLLED BACK ADD",
                }],
                "modified": [{
                    "plaid_transaction_id": f"{missing_item}-absent-target",
                    "account_id": missing_account,
                    "date": "2026-07-19",
                    "amount": 9.87,
                    "name": "ISOLATION MISSING MODIFY",
                }],
                "removed": [],
                "next_cursor": f"isolation-missing-final-{entity_key}",
            }
            healthy_result = {
                "added": [{
                    "plaid_transaction_id": healthy_add,
                    "account_id": healthy_account,
                    "date": "2026-07-19",
                    "amount": 2.34,
                    "name": "ISOLATION HEALTHY SIBLING ADD",
                }],
                "modified": [],
                "removed": [],
                "next_cursor": f"isolation-missing-healthy-final-{entity_key}",
            }

            def _missing_result_for_token(access_token, cursor):
                _check(
                    cursor == isolation_start_cursor,
                    f"Plaid observability {entity_key}: each sibling must start from its stored cursor",
                )
                if access_token == f"decrypted-{missing_token}":
                    return missing_result
                if access_token == f"decrypted-{healthy_token}":
                    return healthy_result
                raise AssertionError("unexpected synthetic decrypted token")

            with patch(
                "core.crypto.decrypt_token", side_effect=lambda token: f"decrypted-{token}"
            ), patch(
                "core.plaid_client.get_transactions",
                side_effect=_missing_result_for_token,
            ) as missing_fetch, patch(
                "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
            ), patch(
                "socket.socket",
                side_effect=AssertionError(
                    "Plaid observability smoke forbids outbound networking"
                ),
            ):
                missing_sync = isolation_plaid_routes._sync_entity(entity_key)

            _check(
                missing_fetch.call_count == 2
                and missing_sync["new"] == 1
                and missing_sync["modified"] == 0
                and missing_sync["removed"] == 0
                and len(missing_sync["errors"]) == 1
                and "Synthetic Missing Bank: transaction persistence failed; cursor unchanged"
                == missing_sync["errors"][0]
                and "absent-target" not in missing_sync["errors"][0],
                f"Plaid observability {entity_key}: missing modifications must fail only their item without false counters",
            )
            conn_isolation = get_connection(entity_key)
            missing_state = conn_isolation.execute(
                "SELECT cursor, last_synced FROM plaid_items WHERE item_id=?",
                (missing_item,),
            ).fetchone()
            healthy_state = conn_isolation.execute(
                "SELECT cursor, last_synced FROM plaid_items WHERE item_id=?",
                (healthy_item,),
            ).fetchone()
            rolled_back_row = conn_isolation.execute(
                "SELECT transaction_id FROM transactions WHERE plaid_transaction_id=?",
                (rolled_back_add,),
            ).fetchone()
            healthy_row = conn_isolation.execute(
                "SELECT amount_cents FROM transactions WHERE plaid_transaction_id=?",
                (healthy_add,),
            ).fetchone()
            conn_isolation.close()
            _check(
                missing_state["cursor"] == isolation_start_cursor
                and missing_state["last_synced"] == isolation_start_synced
                and healthy_state["cursor"]
                == f"isolation-missing-healthy-final-{entity_key}"
                and rolled_back_row is None
                and healthy_row is not None
                and healthy_row["amount_cents"] == -234,
                f"Plaid observability {entity_key}: missing-target rollback and healthy-sibling commit must remain independent",
            )
            _clean_isolation_state(entity_key)

        for entity_key in ("personal", "company", "luxelegacy"):
            truth_item = f"isolation-truth-counts-{entity_key}"
            truth_token = f"synthetic-truth-token-{entity_key}"
            truth_account = _seed_isolation_item(
                entity_key,
                truth_item,
                truth_token,
                "2026-07-01T00:00:00+00:00",
                "Synthetic Truth Bank",
            )
            modified_plaid_id = f"{truth_item}-modified"
            removed_plaid_id = f"{truth_item}-removed"
            absent_removed_id = f"{truth_item}-already-absent"
            _seed_isolation_transaction(
                entity_key, truth_item, modified_plaid_id, "modified"
            )
            removed_transaction_id = _seed_isolation_transaction(
                entity_key, truth_item, removed_plaid_id, "removed"
            )
            conn_isolation = get_connection(entity_key)
            conn_isolation.execute(
                "INSERT INTO transaction_splits "
                "(transaction_id, description, amount_cents, category, subcategory) "
                "VALUES (?, 'isolation truth split', -1000, 'Food', 'General')",
                (removed_transaction_id,),
            )
            conn_isolation.commit()
            conn_isolation.close()
            truth_result = {
                "added": [],
                "modified": [{
                    "plaid_transaction_id": modified_plaid_id,
                    "account_id": truth_account,
                    "date": "2026-07-19",
                    "amount": 3.45,
                    "name": "ISOLATION TRUTHFUL MODIFY",
                }],
                "removed": [removed_plaid_id, absent_removed_id],
                "next_cursor": f"isolation-truth-final-{entity_key}",
            }
            with patch(
                "core.crypto.decrypt_token", return_value=f"decrypted-{truth_token}"
            ), patch(
                "core.plaid_client.get_transactions", return_value=truth_result
            ), patch(
                "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
            ), patch(
                "socket.socket",
                side_effect=AssertionError(
                    "Plaid truth-count smoke forbids outbound networking"
                ),
            ):
                truthful_sync = isolation_plaid_routes._sync_entity(entity_key)
            _check(
                truthful_sync["new"] == 0
                and truthful_sync["modified"] == 1
                and truthful_sync["removed"] == 1
                and truthful_sync["errors"] == [],
                f"Plaid observability {entity_key}: counters must reflect actual affected rows",
            )
            conn_isolation = get_connection(entity_key)
            modified_row = conn_isolation.execute(
                "SELECT description_raw, amount_cents FROM transactions "
                "WHERE plaid_transaction_id=?",
                (modified_plaid_id,),
            ).fetchone()
            removed_row = conn_isolation.execute(
                "SELECT transaction_id FROM transactions WHERE plaid_transaction_id=?",
                (removed_plaid_id,),
            ).fetchone()
            removed_split = conn_isolation.execute(
                "SELECT id FROM transaction_splits WHERE transaction_id=?",
                (removed_transaction_id,),
            ).fetchone()
            conn_isolation.close()
            _check(
                modified_row["description_raw"] == "ISOLATION TRUTHFUL MODIFY"
                and modified_row["amount_cents"] == -345
                and removed_row is None
                and removed_split is None,
                f"Plaid observability {entity_key}: truthful counts must preserve modification and split-cleanup behavior",
            )

            absent_redelivery = {
                "added": [],
                "modified": [],
                "removed": [removed_plaid_id, absent_removed_id],
                "next_cursor": f"isolation-truth-redelivery-{entity_key}",
            }
            with patch(
                "core.crypto.decrypt_token", return_value=f"decrypted-{truth_token}"
            ), patch(
                "core.plaid_client.get_transactions", return_value=absent_redelivery
            ), patch(
                "core.luxury_bridge.push_luxelegacy_to_supabase", return_value=0
            ), patch(
                "socket.socket",
                side_effect=AssertionError(
                    "Plaid truth-count smoke forbids outbound networking"
                ),
            ):
                redelivered_removal = isolation_plaid_routes._sync_entity(entity_key)
            conn_isolation = get_connection(entity_key)
            redelivery_cursor = conn_isolation.execute(
                "SELECT cursor FROM plaid_items WHERE item_id=?", (truth_item,)
            ).fetchone()[0]
            conn_isolation.close()
            _check(
                redelivered_removal["removed"] == 0
                and redelivered_removal["errors"] == []
                and redelivery_cursor == f"isolation-truth-redelivery-{entity_key}",
                f"Plaid observability {entity_key}: already-absent removals must remain zero-count idempotent successes",
            )
            _clean_isolation_state(entity_key)

        for entity_key in ("personal", "company", "luxelegacy"):
            conn_isolation = get_connection(entity_key)
            _check(
                conn_isolation.execute(
                    "SELECT COUNT(*) FROM plaid_items WHERE item_id LIKE 'isolation-%'"
                ).fetchone()[0] == 0
                and conn_isolation.execute(
                    "SELECT COUNT(*) FROM plaid_accounts WHERE item_id LIKE 'isolation-%'"
                ).fetchone()[0] == 0
                and conn_isolation.execute(
                    "SELECT COUNT(*) FROM transactions WHERE plaid_item_id LIKE 'isolation-%'"
                ).fetchone()[0] == 0,
                f"Plaid item isolation {entity_key}: synthetic state should be cleaned exactly",
            )
            conn_isolation.close()
        print("   ✅ All-entity token isolation, missing-modification rollback, truthful counts, idempotent removals, and cleanup passed")

        # ── 8h. CSV export tests ────────────────────────────────────
        print("\n8h. CSV export tests…")
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

        # ── 8i. Recurring Charges report repair ────────────────────
        print("\n8i. Recurring Charges report repair…")
        from core.reporting import get_recurring_charges
        from web.routes.reports import _prepare_report

        recurring_start = "2026-01-01"
        recurring_end = "2026-03-31"
        recurring_empty_start = "2031-01-01"
        recurring_empty_end = "2031-01-31"
        recurring_entities = {
            "personal": {
                "display": "Personal",
                "allowed_category": "Food",
                "allowed_merchant": "Personal Recurring 4H",
                "excluded_categories": (
                    "Credit Card Payment",
                    "Income",
                    "Internal Transfer",
                ),
            },
            "company": {
                "display": "BFM",
                "allowed_category": "Software",
                "allowed_merchant": "BFM Recurring 4H",
                "excluded_categories": (
                    "Credit Card Payment",
                    "Income",
                    "Internal Transfer",
                    "Owner Contribution",
                    "Partner Buyout",
                ),
            },
            "luxelegacy": {
                "display": "LL",
                "allowed_category": "Owner Draw",
                "allowed_merchant": "LL Owner Draw Recurring 4H",
                "excluded_categories": (
                    "Income",
                    "Internal Transfer",
                ),
            },
        }
        recurring_before_seed = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in recurring_entities
        }

        for entity_key, contract in recurring_entities.items():
            recurring_conn = get_connection(entity_key)
            allowed_rows = (
                ("2026-01-05", -10.00),
                ("2026-02-05", -14.00),
            )
            for row_index, (txn_date, amount) in enumerate(allowed_rows, start=1):
                recurring_conn.execute(
                    "INSERT INTO transactions "
                    "(transaction_id, date, description_raw, merchant_canonical, amount, "
                    "amount_cents, currency, account, category, source_filename, imported_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, 'USD', 'Synthetic 4H', ?, 'recurring-4h.csv', "
                    "'2026-07-19T00:00:00+00:00')",
                    (
                        f"recurring-4h-{entity_key}-allowed-{row_index}",
                        txn_date,
                        contract["allowed_merchant"],
                        contract["allowed_merchant"],
                        amount,
                        int(round(amount * 100)),
                        contract["allowed_category"],
                    ),
                )
            for excluded_index, excluded_category in enumerate(
                contract["excluded_categories"], start=1
            ):
                excluded_merchant = f"{entity_key} excluded {excluded_category} 4H"
                for occurrence, txn_date in enumerate(
                    ("2026-01-10", "2026-02-10"), start=1
                ):
                    recurring_conn.execute(
                        "INSERT INTO transactions "
                        "(transaction_id, date, description_raw, merchant_canonical, amount, "
                        "amount_cents, currency, account, category, source_filename, imported_at) "
                        "VALUES (?, ?, ?, ?, -20.00, -2000, 'USD', 'Synthetic 4H', ?, "
                        "'recurring-4h.csv', '2026-07-19T00:00:00+00:00')",
                        (
                            f"recurring-4h-{entity_key}-excluded-{excluded_index}-{occurrence}",
                            txn_date,
                            excluded_merchant,
                            excluded_merchant,
                            excluded_category,
                        ),
                    )
            recurring_conn.commit()
            recurring_conn.close()

        recurring_seeded = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in recurring_entities
        }

        with app.test_client() as recurring_client:
            for entity_key, contract in recurring_entities.items():
                direct_df = get_recurring_charges(
                    entity_key, recurring_start, recurring_end
                )
                _check(
                    list(direct_df["merchant"]) == [contract["allowed_merchant"]],
                    f"recurring {entity_key}: direct query should return only the eligible merchant",
                )
                direct_row = direct_df.iloc[0]
                _check(
                    int(direct_row["count"]) == 2,
                    f"recurring {entity_key}: expected two eligible charges",
                )
                _check(
                    abs(float(direct_row["avg_amount"]) - 12.00) < 0.001
                    and abs(float(direct_row["min_amount"]) - 10.00) < 0.001
                    and abs(float(direct_row["max_amount"]) - 14.00) < 0.001,
                    f"recurring {entity_key}: amount summary should be avg 12, min 10, max 14",
                )
                _check(
                    direct_row["first_date"] == "2026-01-05"
                    and direct_row["last_date"] == "2026-02-05"
                    and direct_row["category"] == contract["allowed_category"],
                    f"recurring {entity_key}: date and category summary should be preserved",
                )

                prepared = _prepare_report(
                    entity_key, "recurring", recurring_start, recurring_end
                )
                _check(
                    prepared is not None and prepared[0] == "recurring_charges",
                    f"recurring {entity_key}: prepared report should be available",
                )
                prepared_out = prepared[2]
                _check(
                    list(prepared_out.columns)
                    == [
                        "Merchant",
                        "Charges",
                        "Avg Amount",
                        "Min Amount",
                        "Max Amount",
                        "First Date",
                        "Last Date",
                        "Category",
                    ],
                    f"recurring {entity_key}: prepared report columns should remain stable",
                )

                recurring_client.set_cookie("entity", contract["display"])
                query = (
                    f"report_type=recurring&start={recurring_start}&end={recurring_end}"
                )
                rendered = recurring_client.get(f"/reports/view?{query}")
                rendered_body = rendered.get_data(as_text=True)
                _check(
                    rendered.status_code == 200
                    and contract["allowed_merchant"] in rendered_body,
                    f"recurring {entity_key}: rendered view should contain the eligible merchant",
                )
                for excluded_category in contract["excluded_categories"]:
                    _check(
                        f"{entity_key} excluded {excluded_category} 4H" not in rendered_body,
                        f"recurring {entity_key}: rendered view should exclude {excluded_category}",
                    )

                recurring_csv = recurring_client.get(
                    f"/reports/export?{query}&format=csv"
                )
                recurring_csv_body = recurring_csv.get_data(as_text=True)
                _check(
                    recurring_csv.status_code == 200
                    and recurring_csv.content_type.startswith("text/csv")
                    and "Merchant,Charges,Avg Amount,Min Amount,Max Amount,First Date,Last Date,Category"
                    in recurring_csv_body
                    and contract["allowed_merchant"] in recurring_csv_body,
                    f"recurring {entity_key}: CSV export should preserve the report contract",
                )

                recurring_pdf = recurring_client.get(
                    f"/reports/export?{query}&format=pdf"
                )
                pdf_disposition = recurring_pdf.headers.get("Content-Disposition", "")
                _check(
                    recurring_pdf.status_code == 200
                    and recurring_pdf.content_type.startswith("application/pdf")
                    and recurring_pdf.data.startswith(b"%PDF")
                    and f"{entity_key}_recurring_charges_{recurring_start}_{recurring_end}.pdf"
                    in pdf_disposition,
                    f"recurring {entity_key}: PDF export should be valid with the stable filename",
                )

                _check(
                    get_recurring_charges(
                        entity_key, recurring_empty_start, recurring_empty_end
                    ).empty,
                    f"recurring {entity_key}: out-of-range direct query should be empty",
                )
                empty_query = (
                    f"report_type=recurring&start={recurring_empty_start}"
                    f"&end={recurring_empty_end}"
                )
                empty_view = recurring_client.get(f"/reports/view?{empty_query}")
                _check(
                    empty_view.status_code == 200
                    and "No data found for this date range." in empty_view.get_data(as_text=True),
                    f"recurring {entity_key}: empty view should not raise a server error",
                )
                _check(
                    recurring_client.get(
                        f"/reports/export?{empty_query}&format=csv"
                    ).status_code
                    == 404,
                    f"recurring {entity_key}: empty export should return not found",
                )

            missing_view = recurring_client.get(
                "/reports/view?report_type=recurring"
            )
            _check(
                missing_view.status_code == 200
                and "Please select a date range." in missing_view.get_data(as_text=True),
                "recurring missing range: view should request a date range",
            )
            _check(
                recurring_client.get(
                    "/reports/export?report_type=recurring&format=csv"
                ).status_code
                == 400,
                "recurring missing range: export should return bad request",
            )

        recurring_after_reads = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in recurring_entities
        }
        _check(
            recurring_after_reads == recurring_seeded,
            "recurring report paths must not mutate any entity database",
        )
        for entity_key in recurring_entities:
            recurring_conn = get_connection(entity_key)
            recurring_conn.execute(
                "DELETE FROM transactions WHERE transaction_id LIKE 'recurring-4h-%'"
            )
            recurring_conn.commit()
            recurring_conn.close()
        recurring_after_cleanup = {
            entity_key: _database_snapshot(entity_key)
            for entity_key in recurring_entities
        }
        _check(
            recurring_after_cleanup == recurring_before_seed,
            "recurring report synthetic rows should be removed exactly",
        )
        print(
            "   ✅ All-entity direct, view, CSV, PDF, exclusions, empty ranges, and cleanup passed"
        )

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

        def _session_cookie_header(response) -> str:
            for value in response.headers.getlist("Set-Cookie"):
                if value.startswith("session="):
                    return value
            _check(False, "auth cookie: response should set the Flask session cookie")
            return ""

        legacy_password = "synthetic-legacy-password"
        legacy_hash = _hashlib.sha256(legacy_password.encode("utf-8")).hexdigest()
        original_fly_app_name = os.environ.pop("FLY_APP_NAME", None)
        os.environ["APP_PASSWORD_HASH"] = legacy_hash
        auth_app = create_app()
        _check(
            auth_app.config["SESSION_COOKIE_HTTPONLY"] is True
            and auth_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
            and auth_app.config["SESSION_COOKIE_SECURE"] is False,
            "auth cookie local: explicit policy should preserve ordinary HTTP development",
        )

        with auth_app.test_client() as auth_client:
            auth_boundary_before = {
                entity_key: _database_snapshot(entity_key)
                for entity_key in ("personal", "company", "luxelegacy")
            }
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
            local_cookie = _session_cookie_header(login_resp)
            _check(
                "HttpOnly" in local_cookie
                and "SameSite=Lax" in local_cookie
                and "Secure" not in local_cookie,
                "auth cookie local: session should be HttpOnly and SameSite Lax without Secure",
            )
            _check(
                "Path=/" in local_cookie
                and "Domain=" not in local_cookie
                and "Expires=" not in local_cookie
                and "Max-Age=" not in local_cookie,
                "auth cookie local: host-only application-root browser-session contract should remain",
            )
            csrf_token = _csrf_from(login_body)

            with patch("web.init_db") as global_init, patch(
                "web.routes.kristine.init_db"
            ) as focused_init, patch(
                "web.routes.kristine._start_background_sync"
            ) as focused_sync:
                focused_redirect = auth_client.get(
                    "/k/?m=2026-07", follow_redirects=False
                )
                focused_slash_redirect = auth_client.get("/k", follow_redirects=False)
                focused_htmx = auth_client.get(
                    "/k/", headers={"HX-Request": "true"}
                )
                focused_json = auth_client.get("/k/", json={})
            focused_location = focused_redirect.headers.get("Location", "")
            _check(
                focused_redirect.status_code == 302
                and "/auth/login?next=/k/" in focused_location
                and "m%3D2026-07" in focused_location,
                "auth focused dashboard: full page should redirect safely with its local return path",
            )
            _check(
                focused_slash_redirect.status_code == 302
                and "/auth/login?next=/k" in focused_slash_redirect.headers.get("Location", ""),
                "auth focused dashboard: slashless path should authenticate before routing",
            )
            _check(
                focused_htmx.status_code == 401 and focused_json.status_code == 401,
                "auth focused dashboard: unauthenticated HTMX and JSON should return 401",
            )
            _check(
                global_init.call_count == 0
                and focused_init.call_count == 0
                and focused_sync.call_count == 0,
                "auth focused dashboard: unauthenticated requests must not initialize databases or launch sync",
            )
            _check(
                all(
                    _database_snapshot(entity_key) == auth_boundary_before[entity_key]
                    for entity_key in ("personal", "company", "luxelegacy")
                ),
                "auth focused dashboard: unauthenticated requests must preserve every entity database",
            )

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

            current_month = _date.today().strftime("%Y-%m")
            focused_marker_rows = {
                "personal": ("BOA Primary", 43210),
                "company": ("4AB BFM MUST NOT RENDER", 76543),
                "luxelegacy": ("4AB LL SOURCE ACCOUNT", 87654),
            }
            for entity_key, (account_name, balance_cents) in focused_marker_rows.items():
                conn_marker = get_connection(entity_key)
                conn_marker.execute(
                    "INSERT INTO account_balances "
                    "(account_name, balance_cents, balance_source, account_type) "
                    "VALUES (?, ?, 'manual', 'bank')",
                    (account_name, balance_cents),
                )
                conn_marker.commit()
                conn_marker.close()
            conn_ll_marker = get_connection("luxelegacy")
            conn_ll_marker.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, amount, amount_cents, "
                "merchant_canonical, category, imported_at) "
                "VALUES ('4ab-ll-auth-marker', ?, '4AB LL AUTHENTICATED MARKER', "
                "-12.34, -1234, '4AB LL AUTHENTICATED MARKER', 'Cost of Goods', ?)",
                (f"{current_month}-15", f"{current_month}-15"),
            )
            conn_ll_marker.commit()
            conn_ll_marker.close()
            conn_bfm_marker = get_connection("company")
            conn_bfm_marker.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, amount, amount_cents, "
                "merchant_canonical, category, imported_at) "
                "VALUES ('4ab-bfm-private-marker', ?, '4AB BFM PRIVATE MARKER', "
                "-76.54, -7654, '4AB BFM PRIVATE MARKER', 'Office Supplies', ?)",
                (f"{current_month}-15", f"{current_month}-15"),
            )
            conn_bfm_marker.commit()
            conn_bfm_marker.close()

            with patch("web.init_db") as authenticated_global_init, patch(
                "web.routes.kristine._start_background_sync", return_value=False
            ) as authenticated_sync:
                focused_authenticated = auth_client.get(f"/k/?m={current_month}")
            focused_body = focused_authenticated.get_data(as_text=True)
            _check(
                focused_authenticated.status_code == 200
                and "$432" in focused_body
                and "$877" in focused_body
                and "4AB LL AUTHENTICATED MARKER" in focused_body,
                "auth focused dashboard: authenticated route should preserve Personal and Luxe Legacy fields",
            )
            _check(
                "$765" not in focused_body
                and "4AB BFM PRIVATE MARKER" not in focused_body,
                "auth focused dashboard: authenticated route must continue excluding BFM",
            )
            _check(
                authenticated_global_init.call_count == 0
                and authenticated_sync.call_count == 1,
                "auth focused dashboard: authenticated route should remain outside global entity setup and reach its own sync seam once",
            )

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

        os.environ["FLY_APP_NAME"] = "synthetic-ledger-oak"
        os.environ["APP_PASSWORD_HASH"] = legacy_hash
        fly_auth_app = create_app()
        _check(
            fly_auth_app.config["SESSION_COOKIE_HTTPONLY"] is True
            and fly_auth_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
            and fly_auth_app.config["SESSION_COOKIE_SECURE"] is True,
            "auth cookie Fly: explicit policy should require HTTPS-only transport",
        )
        with fly_auth_app.test_client() as fly_auth_client:
            fly_login = fly_auth_client.get(
                "/auth/login?next=/", base_url="https://synthetic-ledger-oak.fly.dev"
            )
            fly_login_body = fly_login.get_data(as_text=True)
            fly_cookie = _session_cookie_header(fly_login)
            _check(
                "Secure" in fly_cookie
                and "HttpOnly" in fly_cookie
                and "SameSite=Lax" in fly_cookie,
                "auth cookie Fly: session should be Secure HttpOnly and SameSite Lax",
            )
            _check(
                "Path=/" in fly_cookie
                and "Domain=" not in fly_cookie
                and "Expires=" not in fly_cookie
                and "Max-Age=" not in fly_cookie,
                "auth cookie Fly: host-only application-root browser-session contract should remain",
            )
            fly_csrf_token = _csrf_from(fly_login_body)
            fly_correct = fly_auth_client.post(
                "/auth/login",
                data={
                    "_csrf_token": fly_csrf_token,
                    "password": legacy_password,
                    "next": "/",
                },
                base_url="https://synthetic-ledger-oak.fly.dev",
                follow_redirects=False,
            )
            _check(
                fly_correct.status_code == 302
                and fly_correct.headers.get("Location", "").endswith("/"),
                "auth cookie Fly: HTTPS login should establish the secure session",
            )
            _check(
                fly_auth_client.get(
                    "/", base_url="https://synthetic-ledger-oak.fly.dev"
                ).status_code == 200,
                "auth cookie Fly: secure session should authorize the protected root",
            )
            with patch(
                "web.routes.kristine._start_background_sync", return_value=False
            ):
                fly_focused = fly_auth_client.get(
                    "/k/", base_url="https://synthetic-ledger-oak.fly.dev"
                )
            _check(
                fly_focused.status_code == 200,
                "auth cookie Fly: secure session should preserve focused-dashboard access",
            )

        os.environ.pop("FLY_APP_NAME", None)

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
            with patch("web.init_db") as no_auth_global_init, patch(
                "web.routes.kristine._start_background_sync", return_value=False
            ) as no_auth_sync:
                no_auth_focused = no_auth_client.get(f"/k/?m={current_month}")
            _check(
                no_auth_focused.status_code == 200
                and "4AB LL AUTHENTICATED MARKER" in no_auth_focused.get_data(as_text=True),
                "auth focused dashboard: no-password mode should remain available",
            )
            _check(
                no_auth_global_init.call_count == 0 and no_auth_sync.call_count == 1,
                "auth focused dashboard: no-password route should remain outside global entity setup",
            )

        for entity_key, (account_name, _) in focused_marker_rows.items():
            conn_marker = get_connection(entity_key)
            conn_marker.execute(
                "DELETE FROM account_balances WHERE account_name = ?", (account_name,)
            )
            conn_marker.execute(
                "DELETE FROM transactions WHERE transaction_id IN "
                "('4ab-ll-auth-marker', '4ab-bfm-private-marker')"
            )
            conn_marker.commit()
            remaining_markers = conn_marker.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM account_balances WHERE account_name = ?) + "
                "(SELECT COUNT(*) FROM transactions WHERE transaction_id IN "
                "('4ab-ll-auth-marker', '4ab-bfm-private-marker'))",
                (account_name,),
            ).fetchone()[0]
            conn_marker.close()
            _check(
                remaining_markers == 0,
                f"auth focused dashboard {entity_key}: exact marker cleanup should pass",
            )

        sw_source = (PROJECT_ROOT / "web" / "static" / "sw.js").read_text()
        precache = sw_source.split("const PRECACHE_URLS = [", 1)[1].split("];", 1)[0]
        _check("'/'" not in precache, "service worker: protected root must not be precached")
        _check("the-ledger-v4" in sw_source, "service worker: cache version should invalidate old dynamic caches")
        _check("networkFirst" not in sw_source, "service worker: dynamic cache fallback should be removed")
        _check(sw_source.count("caches.match(request)") == 1, "service worker: only static cache-first may match the request URL")
        _check(sw_source.count("cache.put(request") == 1, "service worker: only static assets may be cached at runtime")

        if original_fly_app_name is None:
            os.environ.pop("FLY_APP_NAME", None)
        else:
            os.environ["FLY_APP_NAME"] = original_fly_app_name

        print("   ✅ Server auth, explicit local/Fly cookies, focused-dashboard boundary, no-password mode, exemptions, CSRF, and protected-cache contracts passed")

        # ── 11b. Shared CSP execution foundation ───────────────────
        print("\n11b. Shared CSP execution foundation…")

        templates_root = PROJECT_ROOT / "web" / "templates"
        base_source = (templates_root / "base.html").read_text()
        theme_source = (PROJECT_ROOT / "web" / "static" / "theme-init.js").read_text()
        shell_source = (PROJECT_ROOT / "web" / "static" / "app-shell.js").read_text()
        style_source = (PROJECT_ROOT / "web" / "static" / "style.css").read_text()

        inline_base_scripts = _re.findall(
            r"<script(?![^>]*\bsrc=)[^>]*>", base_source, flags=_re.IGNORECASE
        )
        native_base_handlers = _re.findall(
            r"\son[a-z][a-z0-9_-]*\s*=", base_source, flags=_re.IGNORECASE
        )
        _check(
            not inline_base_scripts,
            "shared shell CSP: base.html must have no executable inline script blocks",
        )
        _check(
            not native_base_handlers,
            "shared shell CSP: base.html must have no native inline event handlers",
        )
        _check(
            "hx-on" not in base_source,
            "shared shell CSP: base.html must have no HTMX inline event handlers",
        )
        _check(
            "theme-init.js" in base_source and "app-shell.js" in base_source,
            "shared shell CSP: base.html must load both maintained local shell assets",
        )
        _check(
            'content=\'{"includeIndicatorStyles":false,"allowEval":false,"allowScriptTags":false}\''
            in base_source,
            "shared shell CSP: declarative HTMX config must disable injected indicator styles, eval, and swapped scripts",
        )
        _check(
            "{{" not in theme_source
            and "{%" not in theme_source
            and "{{" not in shell_source
            and "{%" not in shell_source,
            "shared shell CSP: maintained JavaScript must not contain executable server templating",
        )
        _check(
            ".htmx-indicator { opacity: 0; }" in style_source
            and ".htmx-request .htmx-indicator" in style_source
            and ".htmx-request.htmx-indicator" in style_source,
            "shared shell CSP: local CSS must preserve HTMX indicator behavior",
        )

        rendered_shell = no_auth_app.test_client().get("/").get_data(as_text=True)
        _check(
            "/static/theme-init.js" in rendered_shell
            and "/static/app-shell.js" in rendered_shell,
            "shared shell CSP: rendered no-password shell must use the maintained local assets",
        )
        _check(
            'name="htmx-config"' in rendered_shell
            and '"includeIndicatorStyles":false' in rendered_shell
            and '"allowEval":false' in rendered_shell
            and '"allowScriptTags":false' in rendered_shell,
            "shared shell CSP: rendered shell must enforce the final HTMX execution-switch contract",
        )

        template_paths = list(templates_root.rglob("*.html"))
        template_sources = [path.read_text() for path in template_paths if path.name != "base.html"]
        template_tags = "\n".join(
            tag
            for path in template_paths
            for tag in _re.findall(r"<[^>]+>", path.read_text(), flags=_re.DOTALL)
        )
        eval_backed_attribute_patterns = (
            _re.compile(r"\s(?:data-)?hx-on(?::[^\s=]+)?\s*=", flags=_re.IGNORECASE),
            _re.compile(r"\s(?:data-)?hx-vars\s*=", flags=_re.IGNORECASE),
            _re.compile(
                r"\s(?:data-)?hx-(?:vals|headers)\s*=\s*([\"'])\s*(?:js|javascript):",
                flags=_re.IGNORECASE,
            ),
            _re.compile(
                r"\s(?:data-)?hx-trigger\s*=\s*([\"'])[^\"']*\[[^\]]+\][^\"']*\1",
                flags=_re.IGNORECASE,
            ),
        )
        _check(
            all(not pattern.search(template_tags) for pattern in eval_backed_attribute_patterns),
            "shared shell CSP: tracked template tags must contain no eval-backed HTMX attributes",
        )
        remaining_hx_on = sum(source.count("hx-on") for source in template_sources)
        remaining_inline_scripts = sum(
            len(
                _re.findall(
                    r"<script(?![^>]*\btype=[\"']application/json[\"'])[^>]*>",
                    source,
                    flags=_re.IGNORECASE,
                )
            )
            for source in template_sources
        )
        _check(
            remaining_hx_on == 0 and remaining_inline_scripts > 0,
            "shared shell CSP: fragment hx-on dependencies must be removed while full-page script migration remains deferred to Task 1P.4.2c",
        )

        print("   ✅ Local shell assets, handler removal, indicator CSS, HTMX config, rendered assets, and residual dependency assertions passed")

        # ── 11c. Dashboard and report fragment execution ─────────────────
        print("\n11c. Dashboard and report fragment execution…")

        fragment_asset = PROJECT_ROOT / "web" / "static" / "dashboard-fragments.js"
        fragment_source = fragment_asset.read_text()
        migrated_fragment_paths = [
            templates_root / "components" / name
            for name in (
                "ai_analysis.html",
                "ie_ai_analysis.html",
                "categories_compare.html",
                "dashboard_body.html",
                "dashboard_detail_cats.html",
                "dashboard_detail_insights.html",
                "insights_upcoming.html",
                "kpi_panel.html",
                "rpt_view.html",
            )
        ]
        executable_script_pattern = _re.compile(
            r"<script(?![^>]*\btype=[\"']application/json[\"'])[^>]*>",
            flags=_re.IGNORECASE,
        )
        native_handler_pattern = _re.compile(
            r"\son[a-z][a-z0-9_-]*\s*=", flags=_re.IGNORECASE
        )
        migrated_sources = [path.read_text() for path in migrated_fragment_paths]
        _check(
            all("<script" not in source.lower() for source in migrated_sources),
            "dashboard/report fragments: migrated templates must have no script elements of any type",
        )
        _check(
            all(not executable_script_pattern.search(source) for source in migrated_sources),
            "dashboard/report fragments: migrated templates must have no executable script blocks",
        )
        _check(
            all(not native_handler_pattern.search(source) for source in migrated_sources),
            "dashboard/report fragments: migrated templates must have no native inline event handlers",
        )
        _check(
            all("hx-on" not in source for source in migrated_sources),
            "dashboard/report fragments: migrated templates must have no HTMX inline event handlers",
        )
        _check(
            "dashboard-fragments.js" in base_source
            and "/static/dashboard-fragments.js" in rendered_shell,
            "dashboard/report fragments: the maintained static controller must load from the shared shell",
        )
        _check(
            "{{" not in fragment_source
            and "{%" not in fragment_source
            and 'document.addEventListener("htmx:load"' in fragment_source
            and 'income-expense-chart' in fragment_source
            and 'kpi-panel' in fragment_source,
            "dashboard/report fragments: the static controller must stay template-free and reinitialize swapped fragments",
        )

        dashboard_route_source = (PROJECT_ROOT / "web" / "routes" / "dashboard.py").read_text()
        _check(
            'data-fragment-action="dismiss-insight"' in dashboard_route_source
            and "iuDismissAndClose" not in dashboard_route_source,
            "dashboard insight detail: Python-rendered modal controls must use the delegated action contract",
        )

        _check(
            '"allowEval":false' in base_source and '"allowScriptTags":false' in base_source,
            "dashboard/report fragments: global HTMX execution switches must be disabled",
        )

        print("   ✅ Migrated fragment sources, delegated controller, rendered asset, Python response, and disabled HTMX switches passed")

        # ── 11d. Transaction and supporting modal fragment execution ────────────────
        print("\n11d. Transaction and supporting modal fragment execution…")

        transaction_fragment_asset = PROJECT_ROOT / "web" / "static" / "transaction-fragments.js"
        transaction_fragment_source = transaction_fragment_asset.read_text()
        transaction_fragment_paths = [
            templates_root / "components" / name
            for name in (
                "txn_results.html",
                "txn_row_edit.html",
                "txn_split_editor.html",
                "subcat_txns_popup.html",
                "todo_queue_detail.html",
            )
        ]
        transaction_fragment_sources = [path.read_text() for path in transaction_fragment_paths]
        _check(
            all("<script" not in source.lower() for source in transaction_fragment_sources),
            "transaction/modal fragments: migrated templates must have no script elements of any type",
        )
        _check(
            all(not executable_script_pattern.search(source) for source in transaction_fragment_sources),
            "transaction/modal fragments: migrated templates must have no executable script blocks",
        )
        _check(
            all(not native_handler_pattern.search(source) for source in transaction_fragment_sources),
            "transaction/modal fragments: migrated templates must have no native inline event handlers",
        )
        _check(
            all("hx-on" not in source for source in transaction_fragment_sources),
            "transaction/modal fragments: migrated templates must have no HTMX inline event handlers",
        )
        _check(
            "transaction-fragments.js" in base_source
            and "/static/transaction-fragments.js" in rendered_shell,
            "transaction/modal fragments: the maintained static controller must load from the shared shell",
        )
        _check(
            "{{" not in transaction_fragment_source
            and "{%" not in transaction_fragment_source
            and 'document.addEventListener("htmx:load"' in transaction_fragment_source
            and 'action === "split-save"' in transaction_fragment_source
            and 'action === "split-category"' in transaction_fragment_source,
            "transaction/modal fragments: the static controller must stay template-free and reinitialize swapped split editors",
        )
        split_editor_source = (templates_root / "components" / "txn_split_editor.html").read_text()
        _check(
            split_editor_source.count("<template") == 2
            and split_editor_source.count("data-json") == 2
            and 'data-transaction-fragment-controller="split-editor"' in split_editor_source,
            "transaction split editor: non-script JSON templates and the declarative controller contract must remain explicit",
        )

        fragment_conn = get_connection("personal")
        try:
            fragment_txn = fragment_conn.execute(
                "SELECT transaction_id FROM transactions ORDER BY date DESC LIMIT 1"
            ).fetchone()
        finally:
            fragment_conn.close()
        _check(fragment_txn is not None, "transaction/modal fragments: synthetic transaction fixture must exist")
        fragment_txn_id = fragment_txn["transaction_id"]
        fragment_client = no_auth_app.test_client()
        rendered_transaction_results = fragment_client.get("/transactions/partial").get_data(as_text=True)
        rendered_transaction_edit = fragment_client.get(
            f"/transactions/edit-row/{fragment_txn_id}"
        ).get_data(as_text=True)
        rendered_split_editor = fragment_client.get(
            f"/transactions/splits/{fragment_txn_id}"
        ).get_data(as_text=True)
        rendered_subcategory_popup = fragment_client.get(
            "/dashboard/subcategory-txns?subcategory=General"
        ).get_data(as_text=True)
        rendered_todo_queue = fragment_client.get("/todo/queue/large-txns").get_data(as_text=True)
        rendered_transaction_fragments = (
            rendered_transaction_results,
            rendered_transaction_edit,
            rendered_split_editor,
            rendered_subcategory_popup,
            rendered_todo_queue,
        )
        _check(
            all(not executable_script_pattern.search(source) for source in rendered_transaction_fragments),
            "transaction/modal fragments: rendered responses must contain no executable script blocks",
        )
        _check(
            all(not native_handler_pattern.search(source) for source in rendered_transaction_fragments)
            and all("hx-on" not in source for source in rendered_transaction_fragments),
            "transaction/modal fragments: rendered responses must contain no inline execution attributes",
        )
        _check(
            'data-transaction-fragment-action="sort"' in rendered_transaction_results
            and 'data-close-transaction-modal-after-request' in rendered_transaction_edit
            and 'data-transaction-fragment-controller="split-editor"' in rendered_split_editor
            and 'data-transaction-fragment-action="close-subcategory-popup"' in rendered_subcategory_popup
            and 'data-transaction-fragment-action="close-todo-queue"' in rendered_todo_queue,
            "transaction/modal fragments: rendered responses must preserve every delegated interaction contract",
        )
        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "transaction/modal fragments: maintained aggregate inventory must match the active post-4AR CSP contract",
        )
        _check(
            '"allowEval":false' in base_source and '"allowScriptTags":false' in base_source,
            "transaction/modal fragments: global HTMX execution switches must be disabled",
        )

        print("   ✅ Migrated sources, rendered fragments, declarative controller, aggregate inventory, and disabled HTMX switches passed")

        # ── 11e. Core review-page execution ─────────────────────────────
        print("\n11e. Core review-page execution…")

        core_review_paths = (
            templates_root / "components" / "sidebar.html",
            templates_root / "dashboard.html",
            templates_root / "reports.html",
            templates_root / "transactions.html",
            templates_root / "todo.html",
        )
        core_review_sources = [path.read_text() for path in core_review_paths]
        _check(
            all(not executable_script_pattern.search(source) for source in core_review_sources),
            "core review pages: confirmed templates must contain no executable inline scripts",
        )
        _check(
            all(not native_handler_pattern.search(source) for source in core_review_sources),
            "core review pages: confirmed templates must contain no native inline handlers",
        )
        _check(
            all("hx-on" not in source for source in core_review_sources),
            "core review pages: confirmed templates must contain no HTMX inline handlers",
        )
        _check(
            'data-app-shell-action="toggle-theme"' in core_review_sources[0]
            and 'data-dashboard-page-action="set-view"' in core_review_sources[1]
            and 'data-report-page-controller' in core_review_sources[2]
            and 'data-transaction-page-controller' in core_review_sources[3]
            and 'data-transaction-fragment-action="open-todo-queue"' in core_review_sources[4],
            "core review pages: each template must expose its delegated static-controller contract",
        )
        _check(
            'action === "toggle-theme"' in shell_source
            and 'pageAction === "set-view"' in fragment_source
            and 'pageAction === "export"' in fragment_source
            and 'action === "open-todo-queue"' in transaction_fragment_source
            and 'function suggestCategory(transactionId)' in transaction_fragment_source,
            "core review pages: maintained assets must own the migrated behavior",
        )
        rendered_core_review_pages = (
            fragment_client.get("/").get_data(as_text=True),
            fragment_client.get("/reports/").get_data(as_text=True),
            fragment_client.get("/transactions/").get_data(as_text=True),
            fragment_client.get("/todo/").get_data(as_text=True),
        )
        _check(
            all(not native_handler_pattern.search(source) for source in rendered_core_review_pages),
            "core review pages: rendered routes must contain no native inline handlers",
        )
        _check(
            all("hx-on" not in source for source in rendered_core_review_pages),
            "core review pages: rendered routes must contain no HTMX inline handlers",
        )

        print("   ✅ Five source templates, rendered routes, delegated controller seams, and exact residual inventory passed")

        # ── 11f. Categorization and upload execution ────────────────────
        print("\n11f. Categorization and upload execution…")

        categorization_upload_paths = (
            templates_root / "categorize.html",
            templates_root / "categorize_orphans.html",
            templates_root / "upload.html",
        )
        categorization_upload_sources = [path.read_text() for path in categorization_upload_paths]
        categorization_upload_asset = PROJECT_ROOT / "web" / "static" / "categorization-upload.js"
        categorization_upload_source = categorization_upload_asset.read_text()
        _check(
            all(not executable_script_pattern.search(source) for source in categorization_upload_sources),
            "categorization/upload pages: confirmed templates must contain no executable inline scripts",
        )
        _check(
            all(not native_handler_pattern.search(source) for source in categorization_upload_sources),
            "categorization/upload pages: confirmed templates must contain no native inline handlers",
        )
        _check(
            all("hx-on" not in source for source in categorization_upload_sources),
            "categorization/upload pages: confirmed templates must contain no HTMX inline handlers",
        )
        _check(
            "categorization-upload.js" in base_source
            and "/static/categorization-upload.js" in rendered_shell,
            "categorization/upload pages: the maintained static controller must load from the shared shell",
        )
        _check(
            "{{" not in categorization_upload_source
            and "{%" not in categorization_upload_source
            and 'data-categorization-action="prefill-alias"' in categorization_upload_sources[0]
            and 'data-categorization-change="category"' in categorization_upload_sources[0]
            and 'data-categorization-change="orphan-category"' in categorization_upload_sources[1]
            and 'data-upload-change="month"' in categorization_upload_sources[2]
            and "Imported transactions will remain in the ledger." in categorization_upload_sources[2]
            and 'control.dataset.uploadChange === "month"' in categorization_upload_source,
            "categorization/upload pages: templates and controller must expose the complete delegated behavior contract",
        )

        rendered_categorization = fragment_client.get("/categorize/").get_data(as_text=True)
        rendered_orphans = fragment_client.get("/categorize/orphans").get_data(as_text=True)
        rendered_upload = fragment_client.get("/upload/?month=2026-07").get_data(as_text=True)
        rendered_categorization_upload = (
            rendered_categorization,
            rendered_orphans,
            rendered_upload,
        )
        _check(
            all(not native_handler_pattern.search(source) for source in rendered_categorization_upload),
            "categorization/upload pages: rendered routes must contain no native inline handlers",
        )
        _check(
            all("hx-on" not in source for source in rendered_categorization_upload)
            and 'data-categorization-controller' in rendered_categorization
            and 'data-categorization-orphans-controller' in rendered_orphans
            and 'data-upload-controller' in rendered_upload,
            "categorization/upload pages: rendered routes must preserve delegated controller markers",
        )

        upload_conn = get_connection("personal")
        try:
            transaction_count_before = upload_conn.execute(
                "SELECT COUNT(*) FROM transactions"
            ).fetchone()[0]
            checklist_cursor = upload_conn.execute(
                "INSERT INTO import_checklist "
                "(label, filename_pattern, profile_name, url, notes, sort_order, created_at, entity) "
                "VALUES (?, ?, NULL, NULL, ?, 0, ?, 'personal')",
                (
                    "Synthetic status-only source",
                    "synthetic-status-only",
                    "4AK status-only proof",
                    "2026-07-22T00:00:00+00:00",
                ),
            )
            checklist_id = checklist_cursor.lastrowid
            upload_conn.execute(
                "INSERT INTO import_checklist_status "
                "(checklist_item_id, month, completed, completed_at, source_filename) "
                "VALUES (?, '2026-07', 1, ?, 'synthetic-status-only.csv')",
                (checklist_id, "2026-07-22T00:00:00+00:00"),
            )
            upload_conn.commit()
        finally:
            upload_conn.close()

        status_page = fragment_client.get("/upload/?month=2026-07").get_data(as_text=True)
        _check(
            "Mark incomplete" in status_page
            and "Imported transactions will remain in the ledger." in status_page,
            "upload status-only action: rendered UI must name the action and preserve imported-row warning",
        )
        status_response = fragment_client.post(
            f"/upload/undo/{checklist_id}",
            data={"month": "2026-07"},
        )
        _check(status_response.status_code == 302, "upload status-only action: request must redirect")
        upload_conn = get_connection("personal")
        try:
            checklist_status = upload_conn.execute(
                "SELECT completed, completed_at, source_filename FROM import_checklist_status "
                "WHERE checklist_item_id=? AND month='2026-07'",
                (checklist_id,),
            ).fetchone()
            transaction_count_after = upload_conn.execute(
                "SELECT COUNT(*) FROM transactions"
            ).fetchone()[0]
            _check(
                checklist_status["completed"] == 0
                and checklist_status["completed_at"] is None
                and checklist_status["source_filename"] == ""
                and transaction_count_after == transaction_count_before,
                "upload status-only action: checklist reset must leave imported transactions unchanged",
            )
            upload_conn.execute(
                "DELETE FROM import_checklist_status WHERE checklist_item_id=?",
                (checklist_id,),
            )
            upload_conn.execute("DELETE FROM import_checklist WHERE id=?", (checklist_id,))
            upload_conn.commit()
        finally:
            upload_conn.close()

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = all_script_count - inert_script_count - external_script_count
        all_native_handler_count = len(native_handler_pattern.findall(all_template_source))
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "categorization/upload pages: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Three source templates, delegated controller, rendered routes, status-only reset, and exact residual inventory passed")

        # ── 11g. Cash Flow and Long-Term Planning execution ────────────
        print("\n11g. Cash Flow and Long-Term Planning execution…")

        cashflow_planning_paths = (
            templates_root / "cashflow.html",
            templates_root / "planning.html",
        )
        cashflow_planning_sources = [
            path.read_text() for path in cashflow_planning_paths
        ]
        inline_executable_script_pattern = _re.compile(
            r"<script(?![^>]*\bsrc=)(?![^>]*\btype=[\"']application/json[\"'])[^>]*>",
            flags=_re.IGNORECASE,
        )
        cashflow_asset_source = (
            PROJECT_ROOT / "web" / "static" / "cashflow.js"
        ).read_text()
        planning_asset_source = (
            PROJECT_ROOT / "web" / "static" / "planning.js"
        ).read_text()
        _check(
            all(
                not inline_executable_script_pattern.search(source)
                for source in cashflow_planning_sources
            ),
            "cash-flow/planning pages: confirmed templates must contain no executable inline scripts",
        )
        _check(
            all(
                not native_handler_pattern.search(source)
                for source in cashflow_planning_sources
            ),
            "cash-flow/planning pages: confirmed templates must contain no native inline handlers",
        )
        _check(
            all("hx-on" not in source for source in cashflow_planning_sources),
            "cash-flow/planning pages: confirmed templates must contain no HTMX inline handlers",
        )
        _check(
            "{{" not in cashflow_asset_source
            and "{%" not in cashflow_asset_source
            and "{{" not in planning_asset_source
            and "{%" not in planning_asset_source
            and "cashflow.js" in cashflow_planning_sources[0]
            and 'data-cashflow-action="flip-open"' in cashflow_planning_sources[0]
            and 'data-cashflow-input="due-day"' in cashflow_planning_sources[0]
            and "planning.js" in cashflow_planning_sources[1]
            and 'data-planning-action="flip-open"' in cashflow_planning_sources[1]
            and 'data-planning-change="source"' in cashflow_planning_sources[1]
            and 'data-planning-action="delete-item"' in cashflow_planning_sources[1],
            "cash-flow/planning pages: templates and page-owned controllers must expose the complete delegated behavior contract",
        )

        fragment_client.set_cookie("entity", "Personal")
        rendered_cashflow = fragment_client.get("/cashflow/").get_data(as_text=True)
        rendered_planning = fragment_client.get("/planning/").get_data(as_text=True)
        rendered_cashflow_planning = (rendered_cashflow, rendered_planning)
        _check(
            all(
                not inline_executable_script_pattern.search(source)
                for source in rendered_cashflow_planning
            ),
            "cash-flow/planning pages: rendered routes must contain no executable inline scripts",
        )
        _check(
            all(
                not native_handler_pattern.search(source)
                for source in rendered_cashflow_planning
            )
            and all("hx-on" not in source for source in rendered_cashflow_planning),
            "cash-flow/planning pages: rendered routes must contain no inline execution attributes",
        )
        _check(
            "/static/cashflow.js" in rendered_cashflow
            and "data-cashflow-controller" in rendered_cashflow
            and "/static/planning.js" in rendered_planning
            and "data-planning-controller" in rendered_planning,
            "cash-flow/planning pages: rendered routes must load and expose both page-owned controllers",
        )

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "cash-flow/planning pages: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Two source templates, page-owned controllers, rendered routes, and exact residual inventory passed")

        # ── 11h. Short-Term Planning execution ────────────────────────
        print("\n11h. Short-Term Planning execution…")

        short_term_template = templates_root / "short_term_planning.html"
        short_term_source = short_term_template.read_text()
        short_term_route_source = (
            PROJECT_ROOT / "web" / "routes" / "short_term_planning.py"
        ).read_text()
        short_term_asset_source = (
            PROJECT_ROOT / "web" / "static" / "short-term-planning.js"
        ).read_text()
        _check(
            not inline_executable_script_pattern.search(short_term_source)
            and not native_handler_pattern.search(short_term_source)
            and "hx-on" not in short_term_source,
            "short-term planning: source template must contain no inline execution",
        )
        _check(
            '<template id="stp-goals-data" data-json>' in short_term_source
            and "short-term-planning.js" in short_term_source
            and "data-short-term-planning-controller" in short_term_source
            and 'data-stp-action="flip-open"' in short_term_source
            and 'data-stp-change="budget-month"' in short_term_source,
            "short-term planning: source template must expose inert goal data and delegated controller seams",
        )
        _check(
            "{{" not in short_term_asset_source
            and "{%" not in short_term_asset_source
            and 'data-stp-action="edit-transaction"' in short_term_route_source
            and 'data-stp-action="show-transactions"' in short_term_route_source
            and not native_handler_pattern.search(short_term_route_source),
            "short-term planning: page controller and Python response markup must remain template-free and handler-free",
        )

        marker_id = "synthetic-4am-short-term-browser"
        marker_conn = get_connection("personal")
        try:
            marker_conn.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_canonical, "
                "amount, amount_cents, account, category, subcategory, "
                "source_filename, imported_at) "
                "VALUES (?, ?, '4AM SHORT TERM MARKER', '4AM SHORT TERM MARKER', "
                "-12.34, -1234, '4AM Synthetic', 'Food', 'General', "
                "'synthetic-4am', '2026-07-23T00:00:00+00:00')",
                (marker_id, f"{current_month}-15"),
            )
            marker_conn.commit()
        finally:
            marker_conn.close()

        fragment_client.set_cookie("entity", "Personal")
        rendered_short_term = fragment_client.get(
            f"/planning/short-term/?month={current_month}"
        ).get_data(as_text=True)
        rendered_transactions = fragment_client.get(
            f"/planning/short-term/budget/transactions"
            f"?category=Food&month={current_month}"
        ).get_data(as_text=True)
        rendered_subcategories = fragment_client.get(
            f"/planning/short-term/budget/subcategories"
            f"?category=Food&month={current_month}"
        ).get_data(as_text=True)
        _check(
            not inline_executable_script_pattern.search(rendered_short_term)
            and not native_handler_pattern.search(rendered_short_term)
            and "hx-on" not in rendered_short_term
            and "/static/short-term-planning.js" in rendered_short_term
            and "data-short-term-planning-controller" in rendered_short_term,
            "short-term planning: rendered page must load its controller with no inline execution",
        )
        _check(
            marker_id in rendered_transactions
            and 'data-stp-action="edit-transaction"' in rendered_transactions
            and not native_handler_pattern.search(rendered_transactions),
            "short-term planning: rendered transaction drill-down must be delegated and handler-free",
        )
        _check(
            'data-stp-action="show-transactions"' in rendered_subcategories
            and not native_handler_pattern.search(rendered_subcategories),
            "short-term planning: rendered subcategory rows must be delegated and handler-free",
        )

        marker_conn = get_connection("personal")
        try:
            marker_conn.execute(
                "DELETE FROM transactions WHERE transaction_id=?", (marker_id,)
            )
            marker_conn.commit()
            _check(
                marker_conn.execute(
                    "SELECT COUNT(*) FROM transactions WHERE transaction_id=?",
                    (marker_id,),
                ).fetchone()[0]
                == 0,
                "short-term planning: focused marker cleanup must be exact",
            )
        finally:
            marker_conn.close()

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "short-term planning: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Source template, page controller, rendered response markup, inert data, cleanup, and exact residual inventory passed")

        # ── 11i. Weekly and Waterfall execution ───────────────────────
        print("\n11i. Weekly and Waterfall execution…")

        weekly_template = templates_root / "weekly.html"
        waterfall_template = templates_root / "waterfall.html"
        weekly_source = weekly_template.read_text()
        waterfall_source = waterfall_template.read_text()
        waterfall_asset_source = (
            PROJECT_ROOT / "web" / "static" / "waterfall.js"
        ).read_text()
        weekly_waterfall_sources = (weekly_source, waterfall_source)
        _check(
            all(
                not inline_executable_script_pattern.search(source)
                and not native_handler_pattern.search(source)
                and "hx-on" not in source
                for source in weekly_waterfall_sources
            ),
            "Weekly/Waterfall: source templates must contain no inline execution",
        )
        _check(
            'data-app-shell-action="open-ai-chat"' in weekly_source
            and 'data-ai-page="weekly"' in weekly_source
            and "waterfall.js" in waterfall_source
            and "data-waterfall-controller" in waterfall_source
            and 'data-app-shell-action="open-ai-chat"' in waterfall_source
            and 'data-ai-page="waterfall"' in waterfall_source
            and 'data-waterfall-action="switch-view"' in waterfall_source
            and 'data-waterfall-action="toggle-breakdown"' in waterfall_source
            and 'data-waterfall-action="set-mode"' in waterfall_source
            and 'data-waterfall-enter="apply-targets"' in waterfall_source
            and 'data-waterfall-enter="apply-tax-rate"' in waterfall_source,
            "Weekly/Waterfall: templates must expose the complete delegated controller contract",
        )
        _check(
            "{{" not in waterfall_asset_source
            and "{%" not in waterfall_asset_source
            and "data-waterfall-action" in waterfall_asset_source
            and "waterfallEnter" in waterfall_asset_source,
            "Weekly/Waterfall: page controller must remain template-free and own delegated actions",
        )

        fragment_client.set_cookie("entity", "Personal")
        rendered_weekly = fragment_client.get("/weekly/").get_data(as_text=True)
        rendered_waterfall = fragment_client.get("/waterfall/").get_data(as_text=True)
        _check(
            all(
                not inline_executable_script_pattern.search(source)
                and not native_handler_pattern.search(source)
                and "hx-on" not in source
                for source in (rendered_weekly, rendered_waterfall)
            ),
            "Weekly/Waterfall: rendered routes must contain no inline execution",
        )
        _check(
            'data-app-shell-action="open-ai-chat"' in rendered_weekly
            and 'data-ai-page="weekly"' in rendered_weekly
            and "/static/waterfall.js" in rendered_waterfall
            and "data-waterfall-controller" in rendered_waterfall,
            "Weekly/Waterfall: rendered routes must expose maintained AI and controller assets",
        )

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "Weekly/Waterfall: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Two source templates, rendered routes, page controller, AI seams, and exact residual inventory passed")

        # ── 11j. Subscription-page execution ────────────────────────
        print("\n11j. Subscription-page execution…")

        subscriptions_template = templates_root / "subscriptions.html"
        subscriptions_source = subscriptions_template.read_text()
        subscriptions_asset_source = (
            PROJECT_ROOT / "web" / "static" / "subscriptions.js"
        ).read_text()
        _check(
            not inline_executable_script_pattern.search(subscriptions_source)
            and not native_handler_pattern.search(subscriptions_source)
            and "hx-on" not in subscriptions_source,
            "subscriptions: source template must contain no inline execution",
        )
        _check(
            "subscriptions.js" in subscriptions_source
            and "data-subscriptions-controller" in subscriptions_source
            and 'data-app-shell-action="open-ai-chat"' in subscriptions_source
            and 'data-ai-page="subscriptions"' in subscriptions_source
            and '<template id="sub-suggestions-data" data-json>' in subscriptions_source
            and 'data-subscriptions-action="open-suggestion"' in subscriptions_source
            and 'data-subscriptions-action="open-watchlist"' in subscriptions_source
            and 'data-subscriptions-action="add-account-info"' in subscriptions_source
            and 'data-subscriptions-action="fetch-tips"' in subscriptions_source
            and 'data-subscriptions-action="copy-share"' in subscriptions_source
            and 'data-subscriptions-action="remove-watchlist"' in subscriptions_source,
            "subscriptions: template must expose the complete delegated controller and inert-data contract",
        )
        _check(
            "{{" not in subscriptions_asset_source
            and "{%" not in subscriptions_asset_source
            and ".onclick" not in subscriptions_asset_source
            and "data-subscriptions-action" in subscriptions_asset_source
            and "subscriptionsEnterAction" in subscriptions_asset_source,
            "subscriptions: page controller must remain template-free and own delegated actions",
        )

        fragment_client.set_cookie("entity", "Personal")
        rendered_subscriptions = fragment_client.get(
            "/subscriptions/"
        ).get_data(as_text=True)
        _check(
            not inline_executable_script_pattern.search(rendered_subscriptions)
            and not native_handler_pattern.search(rendered_subscriptions)
            and "hx-on" not in rendered_subscriptions,
            "subscriptions: rendered route must contain no inline execution",
        )
        _check(
            "/static/subscriptions.js" in rendered_subscriptions
            and "data-subscriptions-controller" in rendered_subscriptions
            and 'data-app-shell-action="open-ai-chat"' in rendered_subscriptions
            and 'data-ai-page="subscriptions"' in rendered_subscriptions,
            "subscriptions: rendered route must expose the maintained controller and AI seam",
        )

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "subscriptions: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Source template, rendered route, page controller, inert data, AI seam, and exact residual inventory passed")

        # ── 11k. Payroll-page execution ─────────────────────────────
        print("\n11k. Payroll-page execution…")

        payroll_template = templates_root / "payroll.html"
        payroll_source = payroll_template.read_text()
        payroll_asset_source = (
            PROJECT_ROOT / "web" / "static" / "payroll.js"
        ).read_text()
        _check(
            not inline_executable_script_pattern.search(payroll_source)
            and not native_handler_pattern.search(payroll_source)
            and "hx-on" not in payroll_source,
            "payroll: source template must contain no inline execution",
        )
        _check(
            "payroll.js" in payroll_source
            and "data-payroll-controller" in payroll_source
            and '<template id="pr-role-colors-data" data-json>' in payroll_source
            and 'data-payroll-action="show-add"' in payroll_source
            and 'data-payroll-action="hide-add"' in payroll_source
            and 'data-payroll-action="open-detail"' in payroll_source
            and 'data-payroll-action="load-spending"' in payroll_source
            and 'data-payroll-action="toggle-new-role"' in payroll_source
            and 'data-payroll-action="close-detail"' in payroll_source
            and "data-payroll-confirm=" in payroll_source
            and 'form="pr-edit-form"' in payroll_source,
            "payroll: template must expose the complete delegated controller, inert-data, and valid-form contract",
        )
        _check(
            "{{" not in payroll_asset_source
            and "{%" not in payroll_asset_source
            and ".onclick" not in payroll_asset_source
            and "data-payroll-action" in payroll_asset_source
            and "payrollConfirm" in payroll_asset_source
            and "replaceChildren" in payroll_asset_source,
            "payroll: page controller must remain template-free and own delegated behavior",
        )

        fragment_client.set_cookie("entity", "BFM")
        rendered_payroll = fragment_client.get("/payroll/").get_data(as_text=True)
        _check(
            not inline_executable_script_pattern.search(rendered_payroll)
            and not native_handler_pattern.search(rendered_payroll)
            and "hx-on" not in rendered_payroll,
            "payroll: rendered route must contain no inline execution",
        )
        _check(
            "/static/payroll.js" in rendered_payroll
            and "data-payroll-controller" in rendered_payroll
            and '<template id="pr-role-colors-data" data-json>' in rendered_payroll,
            "payroll: rendered BFM route must expose the maintained controller and inert role-color data",
        )

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "payroll: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Source template, rendered BFM route, page controller, inert data, valid forms, and exact residual inventory passed")

        # ── 11l. Plaid entry-page execution ─────────────────────────
        print("\n11l. Plaid entry-page execution…")

        data_sources_template = templates_root / "data_sources.html"
        plaid_template = templates_root / "plaid.html"
        data_sources_source = data_sources_template.read_text()
        plaid_source = plaid_template.read_text()
        data_sources_asset_source = (
            PROJECT_ROOT / "web" / "static" / "data-sources.js"
        ).read_text()
        plaid_asset_source = (
            PROJECT_ROOT / "web" / "static" / "plaid.js"
        ).read_text()
        plaid_initializer = (
            '<script src="https://cdn.plaid.com/link/v2/stable/'
            'link-initialize.js"></script>'
        )

        _check(
            all(
                not inline_executable_script_pattern.search(source)
                and not native_handler_pattern.search(source)
                and "hx-on" not in source
                for source in (data_sources_source, plaid_source)
            ),
            "Plaid entry pages: source templates must contain no inline application execution",
        )
        _check(
            data_sources_source.count(plaid_initializer) == 1
            and plaid_source.count(plaid_initializer) == 1,
            "Plaid entry pages: both exact external initializer tags must remain",
        )
        _check(
            "data-sources.js" in data_sources_source
            and "data-data-sources-controller" in data_sources_source
            and 'data-data-sources-action="select-vendor"' in data_sources_source
            and 'data-data-sources-action="filter-date"' in data_sources_source
            and 'data-data-sources-action="connect-account"' in data_sources_source
            and "data-data-sources-confirm=" in data_sources_source
            and '<template id="ds-order-dates-data" data-json>' in data_sources_source
            and "plaid.js" in plaid_source
            and "data-plaid-controller" in plaid_source
            and 'data-plaid-action="connect"' in plaid_source
            and "data-plaid-confirm=" in plaid_source,
            "Plaid entry pages: templates must expose both delegated controller and inert-data contracts",
        )
        _check(
            all(
                "{{" not in source
                and "{%" not in source
                and ".onclick" not in source
                for source in (data_sources_asset_source, plaid_asset_source)
            )
            and "dataSourcesAction" in data_sources_asset_source
            and "dataSourcesConfirm" in data_sources_asset_source
            and "FormData" in data_sources_asset_source
            and "plaidConfirm" in plaid_asset_source
            and '"Content-Type": "application/json"' in plaid_asset_source,
            "Plaid entry pages: both page controllers must remain template-free and preserve their distinct exchange formats",
        )

        original_plaid_client_id = os.environ.get("PLAID_CLIENT_ID")
        original_plaid_secret = os.environ.get("PLAID_SECRET")
        os.environ["PLAID_CLIENT_ID"] = "synthetic-4aq-client"
        os.environ["PLAID_SECRET"] = "synthetic-4aq-secret"
        try:
            plaid_entry_client = no_auth_app.test_client()
            plaid_entry_client.set_cookie("entity", "Personal")
            with plaid_entry_client.session_transaction() as plaid_entry_session:
                plaid_entry_session["_csrf_token"] = "synthetic-4aq-csrf"
            plaid_headers = {"X-CSRF-Token": "synthetic-4aq-csrf"}

            rendered_data_sources = plaid_entry_client.get(
                "/data-sources/"
            ).get_data(as_text=True)
            rendered_plaid = plaid_entry_client.get(
                "/plaid/"
            ).get_data(as_text=True)
            _check(
                all(
                    not inline_executable_script_pattern.search(source)
                    and not native_handler_pattern.search(source)
                    and "hx-on" not in source
                    for source in (rendered_data_sources, rendered_plaid)
                ),
                "Plaid entry pages: rendered routes must contain no inline application execution",
            )
            _check(
                "/static/data-sources.js" in rendered_data_sources
                and "data-data-sources-controller" in rendered_data_sources
                and rendered_data_sources.count(
                    "https://cdn.plaid.com/link/v2/stable/link-initialize.js"
                )
                == 1
                and "/static/plaid.js" in rendered_plaid
                and "data-plaid-controller" in rendered_plaid
                and rendered_plaid.count(
                    "https://cdn.plaid.com/link/v2/stable/link-initialize.js"
                )
                == 1,
                "Plaid entry pages: rendered routes must expose both local controllers and exact initializers",
            )

            create_link_token_calls = []

            def synthetic_create_link_token(user_id):
                create_link_token_calls.append(user_id)
                return f"4aq-link-token-{user_id}"

            exchange_results = [
                {
                    "access_token": "4aq-vendor-access",
                    "item_id": "4aq-vendor-item",
                },
                {
                    "access_token": "4aq-bank-access",
                    "item_id": "4aq-bank-item",
                },
            ]
            synthetic_accounts = [
                {
                    "account_id": "4aq-bank-account",
                    "name": "Synthetic 4AQ Checking",
                    "mask": "4242",
                    "type": "depository",
                    "subtype": "checking",
                }
            ]

            with (
                patch(
                    "core.plaid_client.create_link_token",
                    side_effect=synthetic_create_link_token,
                ),
                patch(
                    "core.plaid_client.exchange_public_token",
                    side_effect=exchange_results,
                ),
                patch(
                    "core.plaid_client.get_accounts",
                    return_value=synthetic_accounts,
                ),
                patch(
                    "core.crypto.encrypt_token",
                    side_effect=lambda token: f"encrypted-{token}",
                ),
            ):
                vendor_link_response = plaid_entry_client.post(
                    "/data-sources/link-token", headers=plaid_headers
                )
                bank_link_response = plaid_entry_client.post(
                    "/plaid/link-token", headers=plaid_headers
                )
                vendor_exchange_response = plaid_entry_client.post(
                    "/data-sources/exchange-token",
                    data={
                        "public_token": "4aq-vendor-public",
                        "institution_name": "Synthetic 4AQ Vendor",
                        "institution_id": "ins_4aq_vendor",
                    },
                    headers=plaid_headers,
                )
                bank_exchange_response = plaid_entry_client.post(
                    "/plaid/exchange-token",
                    json={
                        "public_token": "4aq-bank-public",
                        "institution_name": "Synthetic 4AQ Bank",
                        "institution_id": "ins_4aq_bank",
                    },
                    headers=plaid_headers,
                )

            _check(
                vendor_link_response.status_code == 200
                and vendor_link_response.get_json()["link_token"].startswith(
                    "4aq-link-token-vendor-personal"
                )
                and bank_link_response.status_code == 200
                and bank_link_response.get_json()["link_token"].startswith(
                    "4aq-link-token-expense-tracker-personal"
                )
                and create_link_token_calls
                == ["vendor-personal", "expense-tracker-personal"],
                "Plaid entry pages: both link-token routes must preserve their distinct user identifiers",
            )
            _check(
                vendor_exchange_response.status_code == 200
                and vendor_exchange_response.get_json()["item_id"]
                == "4aq-vendor-item"
                and bank_exchange_response.status_code == 200
                and bank_exchange_response.get_json()["item_id"]
                == "4aq-bank-item"
                and bank_exchange_response.get_json()["accounts"] == 1,
                "Plaid entry pages: form and JSON exchange routes must both remain functional under mocked Plaid",
            )

            for entity_key in ("personal", "company", "luxelegacy"):
                plaid_entry_conn = get_connection(entity_key)
                try:
                    plaid_entry_items = plaid_entry_conn.execute(
                        "SELECT item_id, is_vendor FROM plaid_items "
                        "WHERE item_id LIKE '4aq-%' ORDER BY item_id"
                    ).fetchall()
                    plaid_entry_accounts = plaid_entry_conn.execute(
                        "SELECT account_id FROM plaid_accounts "
                        "WHERE account_id LIKE '4aq-%'"
                    ).fetchall()
                    if entity_key == "personal":
                        _check(
                            [(row["item_id"], row["is_vendor"]) for row in plaid_entry_items]
                            == [("4aq-bank-item", 0), ("4aq-vendor-item", 1)]
                            and [row["account_id"] for row in plaid_entry_accounts]
                            == ["4aq-bank-account"],
                            "Plaid entry pages: mocked exchanges must remain isolated to Personal with exact item roles",
                        )
                    else:
                        _check(
                            not plaid_entry_items and not plaid_entry_accounts,
                            f"Plaid entry pages: {entity_key} must remain unchanged",
                        )
                finally:
                    plaid_entry_conn.close()

            cleanup_conn = get_connection("personal")
            try:
                cleanup_conn.execute(
                    "DELETE FROM plaid_accounts WHERE account_id LIKE '4aq-%'"
                )
                cleanup_conn.execute(
                    "DELETE FROM plaid_items WHERE item_id LIKE '4aq-%'"
                )
                cleanup_conn.commit()
            finally:
                cleanup_conn.close()
        finally:
            if original_plaid_client_id is None:
                os.environ.pop("PLAID_CLIENT_ID", None)
            else:
                os.environ["PLAID_CLIENT_ID"] = original_plaid_client_id
            if original_plaid_secret is None:
                os.environ.pop("PLAID_SECRET", None)
            else:
                os.environ["PLAID_SECRET"] = original_plaid_secret

        all_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        all_script_count = len(
            _re.findall(r"<script\b[^>]*>", all_template_source, flags=_re.IGNORECASE)
        )
        inert_script_count = len(
            _re.findall(
                r"<script\b[^>]*\btype=[\"']application/json[\"'][^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        external_script_count = len(
            _re.findall(
                r"<script\b(?=[^>]*\bsrc=)[^>]*>",
                all_template_source,
                flags=_re.IGNORECASE,
            )
        )
        inline_executable_count = (
            all_script_count - inert_script_count - external_script_count
        )
        all_native_handler_count = len(
            native_handler_pattern.findall(all_template_source)
        )
        all_hx_on_count = all_template_source.count("hx-on")
        _check(
            (
                all_script_count,
                inline_executable_count,
                external_script_count,
                inert_script_count,
                all_native_handler_count,
                all_hx_on_count,
            )
            == (21, 0, 21, 0, 0, 0),
            "Plaid entry pages: maintained aggregate inventory must match the post-4AR CSP contract",
        )

        print("   ✅ Source, rendered, mocked request, exchange-format, entity-isolation, cleanup, and exact residual inventory passed")

        # ── 11m. Standalone and error-document execution ────────────────
        print("\n11m. Standalone and error-document execution…")

        standalone_paths = (
            templates_root / "offline.html",
            templates_root / "errors" / "403.html",
            templates_root / "errors" / "404.html",
            templates_root / "errors" / "500.html",
            templates_root / "kristine.html",
        )
        standalone_sources = [path.read_text() for path in standalone_paths]
        standalone_asset = (
            PROJECT_ROOT / "web" / "static" / "standalone-documents.js"
        ).read_text()
        kristine_asset = (
            PROJECT_ROOT / "web" / "static" / "kristine.js"
        ).read_text()

        _check(
            all(
                not inline_executable_script_pattern.search(source)
                and not native_handler_pattern.search(source)
                and "hx-on" not in source
                for source in standalone_sources
            ),
            "standalone documents: source templates must contain no inline execution",
        )
        _check(
            all(
                "standalone-documents.js" in source
                for source in standalone_sources[:4]
            )
            and "kristine.js" in standalone_sources[4]
            and 'data-standalone-action="retry"' in standalone_sources[0]
            and 'data-kristine-action="toggle-category"' in standalone_sources[4],
            "standalone documents: family controllers and delegated actions must be explicit",
        )
        _check(
            "{{" not in standalone_asset
            and "{%" not in standalone_asset
            and "{{" not in kristine_asset
            and "{%" not in kristine_asset,
            "standalone documents: maintained JavaScript must be template-free",
        )

        from flask import abort

        standalone_app = create_app()
        standalone_app.config.update(
            TESTING=False,
            PROPAGATE_EXCEPTIONS=False,
        )
        standalone_app.logger.disabled = True

        def _synthetic_forbidden():
            abort(403)

        def _synthetic_not_found():
            abort(404)

        def _synthetic_server_error():
            raise RuntimeError("SYNTHETIC_4AR_EXCEPTION_MARKER")

        standalone_app.add_url_rule(
            "/__synthetic-4ar/403",
            "synthetic_4ar_403",
            _synthetic_forbidden,
        )
        standalone_app.add_url_rule(
            "/__synthetic-4ar/404",
            "synthetic_4ar_404",
            _synthetic_not_found,
        )
        standalone_app.add_url_rule(
            "/__synthetic-4ar/500",
            "synthetic_4ar_500",
            _synthetic_server_error,
        )
        standalone_client = standalone_app.test_client()

        rendered_standalone = []
        offline_response = standalone_client.get("/offline")
        rendered_standalone.append(offline_response.get_data(as_text=True))
        _check(
            offline_response.status_code == 200,
            "standalone documents: offline route must remain data-free and available",
        )

        for path, expected_status in (
            ("/__synthetic-4ar/403", 403),
            ("/__synthetic-4ar/404", 404),
            ("/__synthetic-4ar/500", 500),
        ):
            response = standalone_client.get(path)
            body = response.get_data(as_text=True)
            rendered_standalone.append(body)
            _check(
                response.status_code == expected_status,
                f"standalone documents: {expected_status} status must remain exact",
            )
            _check(
                "SYNTHETIC_4AR_EXCEPTION_MARKER" not in body,
                "standalone documents: error responses must not leak exception detail",
            )

        with patch(
            "web.routes.kristine._start_background_sync",
            return_value=False,
        ):
            rendered_kristine = standalone_client.get("/k/")
        rendered_standalone.append(rendered_kristine.get_data(as_text=True))
        _check(
            rendered_kristine.status_code == 200,
            "standalone documents: no-password /k/ must remain available",
        )
        _check(
            all(
                not inline_executable_script_pattern.search(source)
                and not native_handler_pattern.search(source)
                and "hx-on" not in source
                for source in rendered_standalone
            ),
            "standalone documents: rendered responses must contain no inline execution",
        )
        _check(
            all(
                "/static/standalone-documents.js" in source
                for source in rendered_standalone[:4]
            )
            and "/static/kristine.js" in rendered_standalone[4],
            "standalone documents: rendered responses must load their local controllers",
        )

        print("   ✅ Five source templates, local controllers, exact statuses, no exception leakage, rendered responses, and final aggregate inventory passed")

        # ── 11n. Shared shell and dashboard/report style compatibility ───
        print("\n11n. Shared shell and dashboard/report style compatibility…")

        included_style_paths = (
            templates_root / "base.html",
            templates_root / "reports.html",
            templates_root / "components" / "sidebar.html",
            templates_root / "components" / "dashboard_body.html",
            templates_root / "components" / "dashboard_detail_cats.html",
            templates_root / "components" / "dashboard_detail_insights.html",
            templates_root / "components" / "dashboard_ie_insights.html",
            templates_root / "components" / "insights_upcoming.html",
            templates_root / "components" / "categories_compare.html",
            templates_root / "components" / "rpt_view.html",
        )
        included_style_sources = [path.read_text() for path in included_style_paths]
        style_attribute_pattern = _re.compile(
            r"\sstyle\s*=", flags=_re.IGNORECASE
        )
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in included_style_sources
            ),
            "shared/dashboard styles: included source templates must contain no style attributes",
        )

        app_shell_source = (
            PROJECT_ROOT / "web" / "static" / "app-shell.js"
        ).read_text()
        dashboard_fragment_source = (
            PROJECT_ROOT / "web" / "static" / "dashboard-fragments.js"
        ).read_text()
        included_controller_source = (
            app_shell_source + "\n" + dashboard_fragment_source
        )
        _check(
            "style=" not in included_controller_source
            and ".style." not in included_controller_source
            and ".style =" not in included_controller_source,
            "shared/dashboard styles: included controllers must emit no style attributes or runtime style writes",
        )
        _check(
            'classList.add("body-scroll-locked")' in app_shell_source
            and 'classList.remove("body-scroll-locked")' in app_shell_source
            and 'description.hidden = description.dataset.report !== select.value'
            in dashboard_fragment_source
            and 'qboButton.hidden = select.value !== "transactions"'
            in dashboard_fragment_source
            and 'guide.classList.add("ie-guide--visible")'
            in dashboard_fragment_source
            and "setBoundedPercentClass(tip" in dashboard_fragment_source,
            "shared/dashboard styles: maintained class, hidden-state, guide, and bounded tooltip contracts must remain explicit",
        )

        style_source = (PROJECT_ROOT / "web" / "static" / "style.css").read_text()
        percent_classes = {
            int(value)
            for value in _re.findall(r"\.u-pct-(\d+)\s*\{", style_source)
        }
        _check(
            percent_classes == set(range(101))
            and ".u-width-pct" in style_source
            and ".u-height-pct" in style_source
            and ".u-left-pct" in style_source
            and ".body-scroll-locked" in style_source
            and ".ie-guide--visible" in style_source,
            "shared/dashboard styles: local CSS must provide the complete bounded percentage and state-class contract",
        )

        style_client = no_auth_app.test_client()
        rendered_style_responses = []
        for path in (
            "/",
            "/reports/",
            "/dashboard/partial",
            "/dashboard/categories-compare",
            "/dashboard/detail-categories",
            "/dashboard/detail-insights",
            "/dashboard/insights-upcoming",
            "/dashboard/ie-insights",
            "/reports/view?report_type=categories&start=2000-01-01&end=2100-01-01",
        ):
            response = style_client.get(path)
            _check(
                response.status_code == 200,
                f"shared/dashboard styles: {path} must render successfully",
            )
            rendered_style_responses.append(response.get_data(as_text=True))
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in rendered_style_responses
            ),
            "shared/dashboard styles: included rendered pages and fragments must contain no style attributes",
        )

        current_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        app_js_source = "\n".join(
            path.read_text()
            for path in (PROJECT_ROOT / "web" / "static").glob("*.js")
            if path.name != "htmx.min.js"
        )
        current_style_blocks = len(
            _re.findall(r"<style(?:\s|>)", current_template_source, flags=_re.IGNORECASE)
        )
        current_style_attributes = len(
            style_attribute_pattern.findall(current_template_source)
        )
        current_generated_style_attributes = app_js_source.count("style=")
        current_runtime_style_writes = app_js_source.count(".style.")
        _check(
            (
                current_style_blocks,
                current_style_attributes,
                current_generated_style_attributes,
                current_runtime_style_writes,
            )
            == (6, 40, 0, 5),
            "shared/dashboard styles: current application inventory must match the post-4AW contract",
        )

        print("   ✅ Source, rendered, controller, bounded CSS, state behavior, and current residual inventory passed")

        # ── 11o. Transaction and matching style compatibility ───────────
        print("\n11o. Transaction and matching style compatibility…")

        transaction_style_paths = (
            templates_root / "transactions.html",
            templates_root / "match.html",
            templates_root / "components" / "match_card.html",
            templates_root / "components" / "vendor_card.html",
            templates_root / "components" / "txn_results.html",
            templates_root / "components" / "txn_row.html",
            templates_root / "components" / "txn_row_edit.html",
            templates_root / "components" / "txn_split_editor.html",
        )
        transaction_style_sources = [
            path.read_text() for path in transaction_style_paths
        ]
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in transaction_style_sources
            ),
            "transaction/matching styles: included source templates must contain no style attributes",
        )

        transaction_fragment_source = (
            PROJECT_ROOT / "web" / "static" / "transaction-fragments.js"
        ).read_text()
        _check(
            "style=" not in transaction_fragment_source
            and ".style." not in transaction_fragment_source
            and ".style =" not in transaction_fragment_source,
            "transaction/matching styles: controller must emit no style attributes or runtime style writes",
        )
        _check(
            'bar.classList.add("txn-split-total--balanced")'
            in transaction_fragment_source
            and 'bar.classList.add("txn-split-total--unbalanced")'
            in transaction_fragment_source
            and '<div class="txn-split-line-main">' in transaction_fragment_source
            and '<div class="txn-split-line-details">' in transaction_fragment_source,
            "transaction/matching styles: split state and generated-line class contracts must remain explicit",
        )
        _check(
            all(
                selector in style_source
                for selector in (
                    ".match-source-toggle",
                    ".match-card-panel",
                    ".vendor-card-form",
                    ".txn-filter-date",
                    ".txn-filter-category",
                    ".txn-filter-search",
                    ".txn-sort",
                    ".txn-split-modal-card",
                    ".txn-split-line-main",
                    ".txn-split-total--balanced",
                    ".txn-split-total--unbalanced",
                )
            ),
            "transaction/matching styles: maintained CSS must contain the fixed-layout and split-state contracts",
        )

        rendered_transaction_styles = []
        first_style_transaction_id = norm_df.iloc[0]["transaction_id"]
        for path in (
            "/transactions/",
            "/transactions/partial",
            f"/transactions/edit-row/{first_style_transaction_id}",
            f"/transactions/splits/{first_style_transaction_id}",
            "/match/",
        ):
            response = style_client.get(path)
            _check(
                response.status_code == 200,
                f"transaction/matching styles: {path} must render successfully",
            )
            rendered_transaction_styles.append(response.get_data(as_text=True))

        from flask import render_template

        synthetic_match = {
            "txn_amount": -120.00,
            "order_total": 100.00,
            "txn_date": "2026-07-23",
            "txn_description": "Synthetic style match",
            "order_date": "2026-07-15",
            "product_summary": "Synthetic order",
            "suggested_category": "Office Supplies",
            "suggested_subcategory": "General",
            "date_gap": 8,
        }
        synthetic_order = {
            "id": 1,
            "product_summary": "Synthetic vendor card",
            "order_date": "2026-07-23",
            "order_total": 42.00,
        }
        with no_auth_app.test_request_context("/"):
            rendered_transaction_styles.append(
                render_template(
                    "components/match_card.html",
                    review=[synthetic_match, synthetic_match],
                    review_idx=1,
                    current_match=synthetic_match,
                    no_match=[],
                    source="orders",
                )
            )
            rendered_transaction_styles.append(
                render_template(
                    "components/vendor_card.html",
                    order=synthetic_order,
                    total=2,
                    initial=5,
                    completed=3,
                    progress_pct=60,
                    categories=["Office Supplies"],
                    subcategories=["General"],
                    inferred_cat="Office Supplies",
                    inferred_sub="General",
                )
            )

        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in rendered_transaction_styles
            ),
            "transaction/matching styles: included rendered pages and fragments must contain no style attributes",
        )
        _check(
            "u-pct-50" in rendered_transaction_styles[-2]
            and rendered_transaction_styles[-2].count(
                'class="match-metric--warning"'
            )
            == 2
            and "u-pct-60" in rendered_transaction_styles[-1]
            and 'class="vendor-card-form"' in rendered_transaction_styles[-1],
            "transaction/matching styles: bounded progress and warning/form classes must render deterministically",
        )
        _check(
            (
                current_style_blocks,
                current_style_attributes,
                current_generated_style_attributes,
                current_runtime_style_writes,
            )
            == (6, 40, 0, 5),
            "transaction/matching styles: residual application inventory must match the post-4AW contract",
        )

        print("   ✅ Source, rendered, controller, bounded progress, split state, and exact residual inventory passed")

        # ── 11p. Categorization and upload style compatibility ──────────
        print("\n11p. Categorization and upload style compatibility…")

        categorization_style_paths = (
            templates_root / "categorize.html",
            templates_root / "categorize_orphans.html",
            templates_root / "upload.html",
            templates_root / "upload_dialog.html",
        )
        categorization_style_sources = [
            path.read_text() for path in categorization_style_paths
        ]
        _check(
            all(
                not style_attribute_pattern.search(source)
                and not _re.search(
                    r"<style(?:\s|>)", source, flags=_re.IGNORECASE
                )
                for source in categorization_style_sources
            ),
            "categorization/upload styles: all four source templates must contain no inline style blocks or style attributes",
        )
        _check(
            all(
                selector in style_source
                for selector in (
                    ".cat-col-date",
                    ".cat-low-confidence",
                    ".cat-alias-link",
                    ".cat-pagination",
                    ".cat-category-item",
                    ".cat-alias-actions",
                    ".cat-orphan-panel",
                    ".cat-orphan-row",
                    ".upload-month-field",
                    ".upload-inline-form",
                    ".import-preview-metric",
                    ".import-preview-value--credit",
                    ".import-preview-value--debit",
                )
            ),
            "categorization/upload styles: maintained CSS must contain the compact table form alias orphan upload and preview contracts",
        )
        _check(
            "style=" not in categorization_upload_source
            and ".style." not in categorization_upload_source
            and ".style =" not in categorization_upload_source,
            "categorization/upload styles: the existing controller must emit no style attributes or runtime style writes",
        )

        rendered_categorization_styles = []
        for path in (
            "/categorize/",
            "/categorize/?tab=settings",
            "/categorize/orphans",
            "/upload/?month=2026-07",
            "/upload/?tab=settings&month=2026-07",
        ):
            response = style_client.get(path)
            _check(
                response.status_code == 200,
                f"categorization/upload styles: {path} must render successfully",
            )
            rendered_categorization_styles.append(
                response.get_data(as_text=True)
            )

        with no_auth_app.test_request_context("/"):
            rendered_categorization_styles.append(
                render_template(
                    "upload_dialog.html",
                    item={"id": 1, "label": "Synthetic import"},
                    month="2026-07",
                    show_preview=True,
                    good_count=1,
                    total_txns=2,
                    format_month=lambda value: "July 2026",
                    previews=[
                        {
                            "name": "synthetic.csv",
                            "error": None,
                            "count": 2,
                            "min_date": "2026-07-01",
                            "max_date": "2026-07-02",
                            "credits": 10.00,
                            "debits": 4.00,
                            "net": 6.00,
                            "suggested_name": "Synthetic",
                        }
                    ],
                )
            )

        _check(
            all(
                not style_attribute_pattern.search(source)
                and not _re.search(
                    r"<style(?:\s|>)", source, flags=_re.IGNORECASE
                )
                for source in rendered_categorization_styles
            ),
            "categorization/upload styles: included rendered pages and preview dialog must contain no inline style blocks or style attributes",
        )
        _check(
            "cat-category-list" in rendered_categorization_styles[1]
            and "cat-orphan-intro" in rendered_categorization_styles[2]
            and "u-width-pct u-pct-" in rendered_categorization_styles[3]
            and "upload-inline-form" in rendered_categorization_styles[4]
            and "import-preview-metric" in rendered_categorization_styles[5]
            and "import-preview-value--credit"
            in rendered_categorization_styles[5]
            and "import-preview-value--debit"
            in rendered_categorization_styles[5],
            "categorization/upload styles: rendered class and bounded progress contracts must remain explicit",
        )
        _check(
            (
                current_style_blocks,
                current_style_attributes,
                current_generated_style_attributes,
                current_runtime_style_writes,
            )
            == (6, 40, 0, 5),
            "categorization/upload styles: residual application inventory must match the post-4AW contract",
        )

        print("   ✅ Four source templates, rendered routes and preview, controller, semantic CSS, bounded progress, and exact residual inventory passed")

        # ── 11q. Cash Flow and planning style compatibility ─────────────
        print("\n11q. Cash Flow and planning style compatibility…")

        planning_style_paths = (
            templates_root / "cashflow.html",
            templates_root / "planning.html",
            templates_root / "short_term_planning.html",
        )
        planning_style_sources = [
            path.read_text() for path in planning_style_paths
        ]
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in planning_style_sources
            ),
            "cashflow/planning styles: all three source templates must contain no style attributes",
        )

        cashflow_controller_source = (
            PROJECT_ROOT / "web" / "static" / "cashflow.js"
        ).read_text()
        planning_controller_source = (
            PROJECT_ROOT / "web" / "static" / "planning.js"
        ).read_text()
        short_term_controller_source = (
            PROJECT_ROOT / "web" / "static" / "short-term-planning.js"
        ).read_text()
        planning_controller_sources = (
            cashflow_controller_source,
            planning_controller_source,
            short_term_controller_source,
        )
        _check(
            all(
                "style=" not in source
                and ".style." not in source
                and ".style =" not in source
                for source in planning_controller_sources
            ),
            "cashflow/planning styles: all three controllers must emit no style attributes or runtime style writes",
        )
        _check(
            "input.size = Math.max(2, input.value.length + 1);"
            in cashflow_controller_source
            and "modal.animate(" in cashflow_controller_source
            and "popup.animate(" in planning_controller_source
            and "valueInput.disabled = isCashFlow;"
            in planning_controller_source
            and "popup.animate(" in short_term_controller_source,
            "cashflow/planning styles: semantic input state and Web Animations card-origin contracts must remain explicit",
        )
        _check(
            all(
                selector in style_source
                for selector in (
                    ".cf-empty-state",
                    ".pl-box--static",
                    ".pl-modal-input:disabled",
                    ".stp-popup-plan-content",
                    ".stp-modal-spacer",
                    ".stp-txn-modal-body",
                )
            ),
            "cashflow/planning styles: maintained CSS must contain the empty-state static-card disabled-input popup spacer and drill-down contracts",
        )

        rendered_planning_styles = []
        for path in (
            "/cashflow/",
            "/planning/",
            f"/planning/short-term/?month={current_month}",
        ):
            response = style_client.get(path)
            _check(
                response.status_code == 200,
                f"cashflow/planning styles: {path} must render successfully",
            )
            rendered_planning_styles.append(response.get_data(as_text=True))
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in rendered_planning_styles
            ),
            "cashflow/planning styles: included rendered routes must contain no style attributes",
        )
        _check(
            "cfm" in rendered_planning_styles[0]
            and "pl-box--static" in rendered_planning_styles[1]
            and "u-width-pct u-pct-" in rendered_planning_styles[2]
            and "stp-txn-modal-body" in rendered_planning_styles[2],
            "cashflow/planning styles: rendered modal static-card bounded-progress and drill-down classes must remain explicit",
        )

        final_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        final_js_source = "\n".join(
            path.read_text()
            for path in (PROJECT_ROOT / "web" / "static").glob("*.js")
            if path.name != "htmx.min.js"
        )
        final_inventory = (
            len(
                _re.findall(
                    r"<style(?:\s|>)",
                    final_template_source,
                    flags=_re.IGNORECASE,
                )
            ),
            len(style_attribute_pattern.findall(final_template_source)),
            final_js_source.count("style="),
            final_js_source.count(".style."),
        )
        _check(
            final_inventory == (6, 40, 0, 5),
            "cashflow/planning styles: residual application inventory must match the post-4AW contract",
        )

        print("   ✅ Three source templates, rendered routes, semantic CSS, Web Animations motion, bounded progress, and exact residual inventory passed")

        # ── 11r. Weekly and Waterfall style compatibility ───────────────
        print("\n11r. Weekly and Waterfall style compatibility…")

        weekly_waterfall_style_paths = (
            templates_root / "weekly.html",
            templates_root / "waterfall.html",
        )
        weekly_waterfall_style_sources = [
            path.read_text() for path in weekly_waterfall_style_paths
        ]
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in weekly_waterfall_style_sources
            ),
            "weekly/waterfall styles: both source templates must contain no style attributes",
        )

        waterfall_controller_source = (
            PROJECT_ROOT / "web" / "static" / "waterfall.js"
        ).read_text()
        _check(
            "style=" not in waterfall_controller_source
            and ".style." not in waterfall_controller_source
            and ".style =" not in waterfall_controller_source,
            "weekly/waterfall styles: Waterfall controller must emit no style attributes or runtime style writes",
        )
        _check(
            "_waterfallGeometryAnimation" in waterfall_controller_source
            and "_waterfallPositionAnimation" in waterfall_controller_source
            and "_waterfallEntranceAnimation" in waterfall_controller_source
            and "u-width-pct u-pct-" in weekly_waterfall_style_sources[0]
            and "data-bar-left" in weekly_waterfall_style_sources[1]
            and "data-bar-width" in weekly_waterfall_style_sources[1]
            and "u-height-pct u-pct-" in weekly_waterfall_style_sources[1],
            "weekly/waterfall styles: inert geometry and measured Web Animations contracts must remain explicit",
        )
        _check(
            all(
                selector in style_source
                for selector in (
                    ".wk-section-subtitle",
                    ".wf-empty-panel",
                    ".wf-empty-copy",
                    ".wf-tip",
                    ".wf-wf-bar",
                )
            ),
            "weekly/waterfall styles: maintained CSS must contain subtitle empty-state tooltip and Waterfall bar contracts",
        )

        rendered_weekly_waterfall_styles = []
        for path in ("/weekly/", "/waterfall/"):
            response = style_client.get(path)
            _check(
                response.status_code == 200,
                f"weekly/waterfall styles: {path} must render successfully",
            )
            rendered_weekly_waterfall_styles.append(
                response.get_data(as_text=True)
            )
        _check(
            all(
                not style_attribute_pattern.search(source)
                for source in rendered_weekly_waterfall_styles
            ),
            "weekly/waterfall styles: included rendered routes must contain no style attributes",
        )
        _check(
            "wk-section-subtitle" in rendered_weekly_waterfall_styles[0]
            and "/static/waterfall.js" in rendered_weekly_waterfall_styles[1]
            and "data-waterfall-controller"
            in rendered_weekly_waterfall_styles[1],
            "weekly/waterfall styles: rendered semantic and page-controller contracts must remain explicit",
        )

        final_template_source = "\n".join(
            path.read_text() for path in templates_root.rglob("*.html")
        )
        final_js_source = "\n".join(
            path.read_text()
            for path in (PROJECT_ROOT / "web" / "static").glob("*.js")
            if path.name != "htmx.min.js"
        )
        final_inventory = (
            len(
                _re.findall(
                    r"<style(?:\s|>)",
                    final_template_source,
                    flags=_re.IGNORECASE,
                )
            ),
            len(style_attribute_pattern.findall(final_template_source)),
            final_js_source.count("style="),
            final_js_source.count(".style."),
        )
        _check(
            final_inventory == (6, 40, 0, 5),
            "weekly/waterfall styles: residual application inventory must match the post-4AW contract",
        )

        print("   ✅ Two source templates, rendered routes, bounded bars, inert geometry, measured tooltip and motion effects, and exact residual inventory passed")

    print("\n" + "=" * 60)
    print("  🎉  All smoke tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

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

            # include_transfers preserved in drill links (bugfix in PR8)
            resp = client.get("/?include_transfers=1&start=2024-01-01&end=2024-01-31")
            _check(resp.status_code == 200, "dashboard with include_transfers: expected 200")
            body = resp.get_data(as_text=True)
            _check(
                "include_transfers=1" in body,
                "dashboard with include_transfers=1: drill links should contain include_transfers=1",
            )

            # ── Upcoming card with synthetic recurring data ──────────
            # Insert 3 monthly charges to trigger recurring detection
            _synthetic_ids = []
            conn_r = get_connection("personal")
            for i, month in enumerate(["2024-09-15", "2024-10-15", "2024-11-15"]):
                tid = f"test_recurring_{i}"
                _synthetic_ids.append(tid)
                conn_r.execute(
                    "INSERT OR IGNORE INTO transactions "
                    "(transaction_id, date, description_raw, merchant_canonical, "
                    " amount, amount_cents, account, source_filename, imported_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (tid, month, "NETFLIX.COM", "Netflix", -15.99, -1599,
                     "Checking", "test", "2024-11-15T00:00:00"),
                )
            conn_r.commit()
            conn_r.close()

            try:
                # Dashboard for Nov 2024 should show Upcoming card with Netflix
                resp = client.get("/?start=2024-11-01&end=2024-11-30")
                _check(resp.status_code == 200, "dashboard with recurring data: expected 200")
                body = resp.get_data(as_text=True)
                _check(
                    "Upcoming" in body,
                    "Upcoming card heading should be visible",
                )
                _check(
                    "Netflix" in body,
                    "Upcoming card should contain 'Netflix' from synthetic recurring data",
                )
            finally:
                # Cleanup synthetic rows even if assertions fail
                conn_r = get_connection("personal")
                placeholders = ",".join("?" * len(_synthetic_ids))
                conn_r.execute(
                    f"DELETE FROM transactions WHERE transaction_id IN ({placeholders})",
                    _synthetic_ids,
                )
                conn_r.commit()
                conn_r.close()

        print("   ✅ All route regression tests passed")

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

    print("\n" + "=" * 60)
    print("  🎉  All smoke tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

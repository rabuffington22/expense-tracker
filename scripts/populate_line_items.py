"""Populate order_line_items table by re-parsing original CSV/XLSX files.

Re-parses Amazon Business CSV and Henry Schein XLSX files, matches grouped
orders back to amazon_orders rows, and inserts individual line items into
the order_line_items table (created by migration 53).

Usage:
    python scripts/populate_line_items.py                # dry run (default)
    python scripts/populate_line_items.py --apply         # write to DB

    # Production:
    fly ssh console -a ledger-oak -C 'python3 /app/scripts/populate_line_items.py --apply'
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.environ.get("DATA_DIR", "./local_state")
os.makedirs(DATA_DIR, exist_ok=True)

from core.db import get_connection, init_db
from core.amazon import parse_amazon_csv, group_orders
from core.henryschein import parse_henryschein_xlsx
from scripts.categorize_vendor_orders import (
    _match_rules,
    _BFM_RULES,
    _PERSONAL_RULES,
    _HENRY_SCHEIN_RULES,
    _BFM_AMAZON_CAT_MAP,
    _PERSONAL_AMAZON_CAT_MAP,
)

# ── File paths ────────────────────────────────────────────────────────────────

AMAZON_BIZ_CSV = os.path.join(
    DATA_DIR, "uploads",
    "orders_from_20250308_to_20260308_20260308_0416.csv",
)

HENRY_SCHEIN_FILES = [
    os.path.expanduser(
        "~/Downloads/View and Generate Items Purchased-2026-02-25T18-23-12.0093506.xlsx"
    ),
    os.path.expanduser(
        "~/Downloads/Henry Schein/View and Generate Items Purchased-2026-03-08T14-13-38.2291180.xlsx"
    ),
]


# ── Categorization helper ─────────────────────────────────────────────────────

def _categorize_line_item(
    product_name: str,
    amazon_category: str,
    vendor: str,
    entity_key: str,
) -> tuple[Optional[str], Optional[str]]:
    """Categorize a single line item using the same rules as categorize_vendor_orders."""
    # Henry Schein: HS-specific rules first, then BFM rules, default to Medical Supplies
    if vendor == "henryschein":
        cat, sub = _match_rules(product_name, _HENRY_SCHEIN_RULES)
        if cat:
            return cat, sub
        cat, sub = _match_rules(product_name, _BFM_RULES)
        if cat:
            return cat, sub
        return "Medical Supplies", "General"

    # Amazon: entity-specific rules
    if entity_key == "company":
        cat, sub = _match_rules(product_name, _BFM_RULES)
    else:
        cat, sub = _match_rules(product_name, _PERSONAL_RULES)

    if cat:
        return cat, sub

    # Fall back to Amazon category mapping
    if amazon_category:
        cat_map = _BFM_AMAZON_CAT_MAP if entity_key == "company" else _PERSONAL_AMAZON_CAT_MAP
        key = amazon_category.strip().lower()
        if key in cat_map:
            return cat_map[key]

    return None, None


# ── Matching helpers ──────────────────────────────────────────────────────────

def _find_amazon_order_row(conn, order_id: str, order_total: float, vendor: str) -> Optional[int]:
    """Find the amazon_orders.id for a given order_id + approximate total + vendor."""
    row = conn.execute(
        "SELECT id FROM amazon_orders "
        "WHERE order_id = ? AND ABS(order_total - ?) < 0.10 "
        "AND COALESCE(vendor, 'amazon') = ?",
        (order_id, order_total, vendor),
    ).fetchone()
    return row["id"] if row else None


def _order_has_line_items(conn, amazon_order_id: int) -> bool:
    """Check if line items already exist for this order (avoid duplicates)."""
    row = conn.execute(
        "SELECT COUNT(*) FROM order_line_items WHERE amazon_order_id = ?",
        (amazon_order_id,),
    ).fetchone()
    return row[0] > 0


# ── Amazon Business CSV processing ───────────────────────────────────────────

def process_amazon_business(conn, entity_key: str, apply: bool) -> dict:
    """Parse Amazon Business CSV and insert line items for matched orders."""
    stats = {
        "file": AMAZON_BIZ_CSV,
        "orders_parsed": 0,
        "orders_matched": 0,
        "orders_skipped_existing": 0,
        "orders_not_found": 0,
        "line_items_inserted": 0,
        "categories": defaultdict(int),
    }

    if not os.path.exists(AMAZON_BIZ_CSV):
        stats["error"] = f"File not found: {AMAZON_BIZ_CSV}"
        return stats

    df, warnings = parse_amazon_csv(AMAZON_BIZ_CSV)
    if df.empty:
        stats["error"] = f"Empty CSV or parse error: {warnings}"
        return stats

    orders = group_orders(df)
    stats["orders_parsed"] = len(orders)

    now = datetime.now().isoformat()

    for order in orders:
        order_id = order["order_id"]
        order_total = order["order_total"]
        items = order.get("items", [])

        if not items:
            continue

        # Find matching amazon_orders row
        db_id = _find_amazon_order_row(conn, order_id, order_total, "amazon")
        if db_id is None:
            stats["orders_not_found"] += 1
            continue

        # Skip if already populated
        if _order_has_line_items(conn, db_id):
            stats["orders_skipped_existing"] += 1
            continue

        stats["orders_matched"] += 1

        for item in items:
            product_name = item.get("product_name", "Unknown")
            quantity = item.get("quantity", 1)
            unit_price = item.get("unit_price", 0)
            tax = item.get("tax", 0)
            shipping = item.get("shipping", 0)
            item_total = unit_price + tax + shipping
            asin = item.get("asin", "")
            amazon_cat = item.get("amazon_category", "")

            unit_price_cents = round(unit_price * 100)
            item_total_cents = round(item_total * 100)

            # Categorize the individual item
            cat, sub = _categorize_line_item(
                product_name, amazon_cat, "amazon", entity_key
            )

            if cat:
                stats["categories"][f"{cat}/{sub or 'General'}"] += 1

            if apply:
                conn.execute(
                    "INSERT INTO order_line_items "
                    "(amazon_order_id, product_name, quantity, unit_price_cents, "
                    " item_total_cents, asin, amazon_category, category, subcategory, "
                    " created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        db_id,
                        product_name,
                        quantity,
                        unit_price_cents,
                        item_total_cents,
                        asin if asin and asin != "nan" else None,
                        amazon_cat if amazon_cat and amazon_cat != "nan" else None,
                        cat,
                        sub or "General" if cat else None,
                        now,
                    ),
                )

            stats["line_items_inserted"] += 1

    if apply:
        conn.commit()

    return stats


# ── Henry Schein XLSX processing ──────────────────────────────────────────────

def process_henry_schein(conn, entity_key: str, apply: bool) -> dict:
    """Parse Henry Schein XLSX files and insert line items for matched orders."""
    stats = {
        "files": [],
        "orders_parsed": 0,
        "orders_matched": 0,
        "orders_skipped_existing": 0,
        "orders_not_found": 0,
        "line_items_inserted": 0,
        "categories": defaultdict(int),
    }

    now = datetime.now().isoformat()

    for xlsx_path in HENRY_SCHEIN_FILES:
        if not os.path.exists(xlsx_path):
            stats["files"].append({"path": xlsx_path, "status": "not found"})
            continue

        orders, warnings = parse_henryschein_xlsx(xlsx_path)
        stats["files"].append({
            "path": xlsx_path,
            "status": "ok",
            "orders": len(orders),
            "warnings": warnings,
        })
        stats["orders_parsed"] += len(orders)

        for order in orders:
            order_id = order["order_id"]
            order_total = order["order_total"]
            items = order.get("items", [])

            if not items:
                continue

            # Find matching amazon_orders row
            db_id = _find_amazon_order_row(conn, order_id, order_total, "henryschein")
            if db_id is None:
                stats["orders_not_found"] += 1
                continue

            # Skip if already populated
            if _order_has_line_items(conn, db_id):
                stats["orders_skipped_existing"] += 1
                continue

            stats["orders_matched"] += 1

            for item in items:
                product_name = item.get("description", "Unknown")
                quantity = item.get("qty", 1)
                unit_price = item.get("unit_price", 0)
                item_total = item.get("amount", 0)

                unit_price_cents = round(unit_price * 100)
                item_total_cents = round(item_total * 100)

                # Categorize the individual item
                cat, sub = _categorize_line_item(
                    product_name, "", "henryschein", entity_key
                )

                if cat:
                    stats["categories"][f"{cat}/{sub or 'General'}"] += 1

                if apply:
                    conn.execute(
                        "INSERT INTO order_line_items "
                        "(amazon_order_id, product_name, quantity, unit_price_cents, "
                        " item_total_cents, asin, amazon_category, category, "
                        " subcategory, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            db_id,
                            product_name,
                            quantity,
                            unit_price_cents,
                            item_total_cents,
                            item.get("item_code") or None,
                            item.get("hs_category") or None,
                            cat,
                            sub or "General" if cat else None,
                            now,
                        ),
                    )

                stats["line_items_inserted"] += 1

    if apply:
        conn.commit()

    return stats


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Populate order_line_items table from original CSV/XLSX files."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Write changes to DB (default is dry run).",
    )
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== Populate Order Line Items ({mode}) ===\n")

    # Ensure migration 53 has been applied
    entity_key = "company"
    init_db(entity_key)

    conn = get_connection(entity_key)
    try:
        # ── Amazon Business CSV ───────────────────────────────────────────
        print("--- Amazon Business CSV (BFM) ---")
        amazon_stats = process_amazon_business(conn, entity_key, args.apply)

        if "error" in amazon_stats:
            print(f"  ERROR: {amazon_stats['error']}")
        else:
            print(f"  File: {amazon_stats['file']}")
            print(f"  Orders parsed:           {amazon_stats['orders_parsed']}")
            print(f"  Orders matched to DB:    {amazon_stats['orders_matched']}")
            print(f"  Orders already populated:{amazon_stats['orders_skipped_existing']}")
            print(f"  Orders not found in DB:  {amazon_stats['orders_not_found']}")
            print(f"  Line items to insert:    {amazon_stats['line_items_inserted']}")
            if amazon_stats["categories"]:
                print(f"  Category breakdown:")
                for cat, count in sorted(amazon_stats["categories"].items()):
                    print(f"    {cat}: {count}")
        print()

        # ── Henry Schein XLSX ─────────────────────────────────────────────
        print("--- Henry Schein XLSX (BFM) ---")
        hs_stats = process_henry_schein(conn, entity_key, args.apply)

        for finfo in hs_stats["files"]:
            print(f"  File: {finfo['path']}")
            print(f"    Status: {finfo['status']}")
            if finfo.get("orders"):
                print(f"    Orders: {finfo['orders']}")
            if finfo.get("warnings"):
                for w in finfo["warnings"]:
                    print(f"    Warning: {w}")

        print(f"  Orders parsed:           {hs_stats['orders_parsed']}")
        print(f"  Orders matched to DB:    {hs_stats['orders_matched']}")
        print(f"  Orders already populated:{hs_stats['orders_skipped_existing']}")
        print(f"  Orders not found in DB:  {hs_stats['orders_not_found']}")
        print(f"  Line items to insert:    {hs_stats['line_items_inserted']}")
        if hs_stats["categories"]:
            print(f"  Category breakdown:")
            for cat, count in sorted(hs_stats["categories"].items()):
                print(f"    {cat}: {count}")
        print()

        # ── Summary ───────────────────────────────────────────────────────
        total_items = amazon_stats.get("line_items_inserted", 0) + hs_stats["line_items_inserted"]
        total_matched = amazon_stats.get("orders_matched", 0) + hs_stats["orders_matched"]
        total_skipped = amazon_stats.get("orders_skipped_existing", 0) + hs_stats["orders_skipped_existing"]

        print("=== Summary ===")
        print(f"  Total orders matched:     {total_matched}")
        print(f"  Total orders pre-existing:{total_skipped}")
        print(f"  Total line items:         {total_items}")

        if not args.apply and total_items > 0:
            print(f"\n  (Dry run -- no changes written. Use --apply to write.)")
        elif args.apply:
            # Verify what was written
            count = conn.execute("SELECT COUNT(*) FROM order_line_items").fetchone()[0]
            print(f"\n  Verified: {count} rows now in order_line_items table.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

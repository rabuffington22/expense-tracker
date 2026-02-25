"""Amazon order CSV parsing and transaction matching.

Parses Amazon Privacy Central order history exports (Retail.OrderHistory.1.csv),
groups items by order, and matches them to Amazon bank transactions by date + amount.
"""

from datetime import datetime, timedelta
from itertools import combinations
from typing import Optional

import pandas as pd

from core.db import get_connection


# ── Column name normalization ────────────────────────────────────────────────
# Amazon exports vary; map known variants to canonical names.

_AMAZON_COL_MAP = {
    "order date": "order_date",
    "order id": "order_id",
    "website order id": "order_id",
    "product name": "product_name",
    "title": "product_name",
    "item total": "item_total",
    "total owed": "total_owed",
    "unit price": "unit_price",
    "unit price tax": "unit_price_tax",
    "shipping charge": "shipping_charge",
    "quantity": "quantity",
    "asin": "asin",
    "order status": "order_status",
    "shipment status": "shipment_status",
    "currency": "currency",
}


# ── Category inference from product names ────────────────────────────────────

_AMAZON_CATEGORY_HINTS: list[tuple[list[str], str]] = [
    (["book", "kindle", "paperback", "hardcover", "novel", "edition"], "Entertainment"),
    (["cable", "charger", "adapter", "hub", "usb", "hdmi", "phone case",
      "screen protector", "earbuds", "headphone", "speaker", "battery",
      "bluetooth", "wireless", "mouse", "keyboard", "monitor", "laptop"],
     "Electronics"),
    (["vitamin", "supplement", "medicine", "health", "bandage", "first aid",
      "thermometer", "allergy", "ibuprofen", "tylenol"],
     "Healthcare"),
    (["dog", "cat", "pet", "treats", "leash", "litter", "kibble"], "Pet Supplies"),
    (["soap", "shampoo", "toothpaste", "razor", "deodorant", "lotion",
      "moisturizer", "sunscreen", "body wash"],
     "Personal Care"),
    (["pan", "pot", "kitchen", "utensil", "plate", "cup", "mug", "spatula",
      "cutting board", "container", "storage", "organizer", "shelf",
      "curtain", "pillow", "blanket", "towel", "mat"],
     "Home"),
    (["shirt", "pants", "shoes", "socks", "jacket", "clothing", "dress",
      "shorts", "underwear", "hat", "gloves", "boots"],
     "Clothing"),
    (["tool", "drill", "screw", "nail", "tape", "paint", "sandpaper",
      "wrench", "pliers", "saw", "level", "hammer"],
     "Home Improvement"),
    (["toy", "game", "puzzle", "lego", "doll", "action figure", "board game"],
     "Entertainment"),
    (["snack", "food", "coffee", "tea", "protein", "granola", "cereal",
      "candy", "chocolate", "nuts"],
     "Groceries"),
]


def infer_category(product_name: str) -> str:
    """Return a category guess from the product name, or 'Shopping' as default."""
    lower = product_name.lower()
    for keywords, category in _AMAZON_CATEGORY_HINTS:
        if any(kw in lower for kw in keywords):
            return category
    return "Shopping"


# ── CSV parsing ──────────────────────────────────────────────────────────────

def parse_amazon_csv(file_or_path) -> tuple[pd.DataFrame, list[str]]:
    """
    Parse Amazon Privacy Central CSV, normalizing column names.

    Returns (DataFrame with canonical columns, list of warnings).
    """
    warnings: list[str] = []

    try:
        df = pd.read_csv(file_or_path)
    except Exception as exc:
        return pd.DataFrame(), [f"Failed to read CSV: {exc}"]

    if df.empty:
        return df, ["CSV is empty."]

    # Normalize column names
    col_remap = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in _AMAZON_COL_MAP:
            col_remap[col] = _AMAZON_COL_MAP[key]
    df = df.rename(columns=col_remap)

    # Check required columns
    required = {"order_id", "order_date", "product_name"}
    missing = required - set(df.columns)
    if missing:
        available = ", ".join(sorted(df.columns))
        return pd.DataFrame(), [
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Available columns: {available}"
        ]

    # Parse dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    bad_dates = df["order_date"].isna().sum()
    if bad_dates:
        warnings.append(f"{bad_dates} rows with unparseable dates dropped.")
        df = df.dropna(subset=["order_date"])

    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    # Parse amounts — try several possible columns
    amount_col = None
    for candidate in ["item_total", "total_owed", "unit_price"]:
        if candidate in df.columns:
            amount_col = candidate
            break

    if amount_col is None:
        # Try to find any column with dollar amounts
        warnings.append("No recognized amount column found; amounts set to 0.")
        df["item_amount"] = 0.0
    else:
        df["item_amount"] = (
            df[amount_col]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )

    # Parse tax if available
    if "unit_price_tax" in df.columns:
        df["item_tax"] = (
            df["unit_price_tax"]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )
    else:
        df["item_tax"] = 0.0

    # Parse shipping if available
    if "shipping_charge" in df.columns:
        df["item_shipping"] = (
            df["shipping_charge"]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )
    else:
        df["item_shipping"] = 0.0

    # Parse quantity
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    else:
        df["quantity"] = 1

    # Filter to shipped/delivered if status column exists
    if "order_status" in df.columns:
        valid_statuses = {"shipped", "delivered", "closed"}
        original_count = len(df)
        df_filtered = df[df["order_status"].str.lower().isin(valid_statuses)]
        if not df_filtered.empty:
            skipped = original_count - len(df_filtered)
            if skipped:
                warnings.append(f"Filtered out {skipped} non-shipped/delivered orders.")
            df = df_filtered
        else:
            warnings.append("No shipped/delivered orders found; keeping all rows.")

    return df, warnings


# ── Order grouping ───────────────────────────────────────────────────────────

def group_orders(df: pd.DataFrame) -> list[dict]:
    """
    Group Amazon CSV rows by order_id.

    Returns list of order dicts, each with:
      order_id, order_date, items, order_total, product_summary
    """
    if df.empty:
        return []

    orders = []
    for order_id, group in df.groupby("order_id"):
        items = []
        for _, row in group.iterrows():
            items.append({
                "product_name": str(row.get("product_name", "Unknown")),
                "unit_price": float(row.get("item_amount", 0)),
                "tax": float(row.get("item_tax", 0)),
                "shipping": float(row.get("item_shipping", 0)),
                "quantity": int(row.get("quantity", 1)),
                "asin": str(row.get("asin", "")),
            })

        # Total = sum of (price + tax + shipping) for all items
        order_total = sum(
            i["unit_price"] + i["tax"] + i["shipping"] for i in items
        )

        # Product summary
        names = [i["product_name"] for i in items]
        if len(names) == 1:
            product_summary = names[0]
        elif len(names) == 2:
            product_summary = f"{names[0]}, {names[1]}"
        else:
            product_summary = f"{names[0]} + {len(names) - 1} more"

        # Truncate long summaries
        if len(product_summary) > 200:
            product_summary = product_summary[:197] + "..."

        orders.append({
            "order_id": str(order_id),
            "order_date": str(group.iloc[0]["order_date"]),
            "items": items,
            "order_total": round(order_total, 2),
            "product_summary": product_summary,
            "matched": False,  # tracking flag for matching
        })

    return orders


# ── Transaction lookup ───────────────────────────────────────────────────────

def find_amazon_transactions(entity: str) -> pd.DataFrame:
    """Query all transactions matching Amazon patterns."""
    conn = get_connection(entity)
    try:
        rows = conn.execute(
            "SELECT transaction_id, date, description_raw, amount, "
            "       merchant_canonical, category, notes "
            "FROM transactions "
            "WHERE LOWER(description_raw) LIKE '%amazon%' "
            "   OR LOWER(description_raw) LIKE '%amzn%' "
            "ORDER BY date DESC"
        ).fetchall()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([dict(r) for r in rows])
    finally:
        conn.close()


# ── Matching algorithm ───────────────────────────────────────────────────────

def _dates_within_window(txn_date: str, order_date: str, window: int = 5) -> bool:
    """Check if txn_date is within `window` days after order_date."""
    try:
        txn = datetime.strptime(txn_date, "%Y-%m-%d")
        order = datetime.strptime(order_date, "%Y-%m-%d")
        delta = (txn - order).days
        return -2 <= delta <= window  # allow 2 days before (pre-auth)
    except (ValueError, TypeError):
        return False


def _amounts_match(txn_amount: float, order_total: float, tolerance: float = 0.05) -> bool:
    """Check if amounts match within tolerance."""
    return abs(abs(txn_amount) - order_total) <= tolerance


def match_orders_to_transactions(
    orders: list[dict],
    transactions: pd.DataFrame,
    date_window: int = 5,
    amount_tolerance: float = 0.05,
) -> list[dict]:
    """
    Multi-pass matching of Amazon orders to bank transactions.

    Returns list of match result dicts for each Amazon transaction.
    """
    if transactions.empty or not orders:
        return []

    # Work with copies
    unmatched_orders = [o.copy() for o in orders]
    results = []

    for _, txn in transactions.iterrows():
        txn_id = txn["transaction_id"]
        txn_date = txn["date"]
        txn_amount = float(txn["amount"])
        txn_desc = txn["description_raw"]

        result = {
            "transaction_id": txn_id,
            "txn_date": txn_date,
            "txn_amount": txn_amount,
            "txn_description": txn_desc,
            "existing_category": txn.get("category") or "",
            "existing_notes": txn.get("notes") or "",
            "match_type": "none",
            "matched_order": None,
            "confidence": 0.0,
            "product_summary": "",
            "suggested_category": "",
            "order_id": "",
        }

        # Skip positive amounts (credits/refunds) for now
        if txn_amount >= 0:
            result["match_type"] = "skip"
            results.append(result)
            continue

        # Pass 1: Exact match (amount + date)
        exact_matches = [
            o for o in unmatched_orders
            if not o["matched"]
            and _amounts_match(txn_amount, o["order_total"], amount_tolerance)
            and _dates_within_window(txn_date, o["order_date"], date_window)
        ]
        if len(exact_matches) == 1:
            order = exact_matches[0]
            order["matched"] = True
            result["match_type"] = "exact"
            result["matched_order"] = order
            result["confidence"] = 0.95
            result["product_summary"] = order["product_summary"]
            result["suggested_category"] = infer_category(order["product_summary"])
            result["order_id"] = order["order_id"]
            results.append(result)
            continue

        # Pass 2: Amount-only match (ignore date)
        amount_matches = [
            o for o in unmatched_orders
            if not o["matched"]
            and _amounts_match(txn_amount, o["order_total"], amount_tolerance)
        ]
        if len(amount_matches) == 1:
            order = amount_matches[0]
            order["matched"] = True
            result["match_type"] = "amount_only"
            result["matched_order"] = order
            result["confidence"] = 0.80
            result["product_summary"] = order["product_summary"]
            result["suggested_category"] = infer_category(order["product_summary"])
            result["order_id"] = order["order_id"]
            results.append(result)
            continue

        # Pass 3: Multi-order consolidation (2-3 orders summing to amount)
        candidate_orders = [
            o for o in unmatched_orders
            if not o["matched"]
            and _dates_within_window(txn_date, o["order_date"], date_window)
        ]
        found_combo = False
        for combo_size in (2, 3):
            if found_combo or len(candidate_orders) < combo_size:
                break
            for combo in combinations(candidate_orders, combo_size):
                combo_total = sum(o["order_total"] for o in combo)
                if _amounts_match(txn_amount, combo_total, amount_tolerance):
                    for o in combo:
                        o["matched"] = True
                    names = [o["product_summary"] for o in combo]
                    summary = ", ".join(names)
                    if len(summary) > 200:
                        summary = summary[:197] + "..."
                    result["match_type"] = "multi_order"
                    result["matched_order"] = combo[0]  # primary
                    result["confidence"] = 0.75
                    result["product_summary"] = summary
                    result["suggested_category"] = infer_category(summary)
                    result["order_id"] = ", ".join(o["order_id"] for o in combo)
                    found_combo = True
                    break

        if found_combo:
            results.append(result)
            continue

        # Pass 4: Date-only fallback (suggest closest date match)
        date_matches = [
            o for o in unmatched_orders
            if not o["matched"]
            and _dates_within_window(txn_date, o["order_date"], date_window)
        ]
        if date_matches:
            # Pick the one with closest amount
            best = min(date_matches, key=lambda o: abs(abs(txn_amount) - o["order_total"]))
            result["match_type"] = "date_only"
            result["matched_order"] = best
            result["confidence"] = 0.50
            result["product_summary"] = best["product_summary"]
            result["suggested_category"] = infer_category(best["product_summary"])
            result["order_id"] = best["order_id"]
            # Don't mark as matched — user must confirm
            results.append(result)
            continue

        # No match
        results.append(result)

    return results


# ── Apply matches to DB ─────────────────────────────────────────────────────

def apply_matches(entity: str, matches: list[dict]) -> int:
    """
    Write accepted matches to the database.

    Updates: notes (product names), merchant_canonical, category, confidence.
    Returns count of updated transactions.
    """
    conn = get_connection(entity)
    try:
        updated = 0
        for m in matches:
            if not m.get("product_summary"):
                continue

            conn.execute(
                "UPDATE transactions "
                "SET notes = ?, "
                "    merchant_canonical = 'Amazon', "
                "    category = COALESCE(NULLIF(?, ''), category), "
                "    confidence = ? "
                "WHERE transaction_id = ?",
                (
                    m["product_summary"],
                    m.get("suggested_category", ""),
                    m.get("confidence", 0.0),
                    m["transaction_id"],
                ),
            )
            updated += 1

        conn.commit()
        return updated
    finally:
        conn.close()

"""Amazon order CSV parsing and transaction matching.

Parses Amazon order history exports (Business or Privacy Central) and matches
grouped charges to Amazon bank transactions by date + amount.

Supports:
  - Amazon Business CSV (groups by Payment Reference ID for exact charge matching)
  - Amazon Privacy Central CSV (Retail.OrderHistory.1.csv, groups by Order ID)
"""

from datetime import datetime, timedelta
from itertools import combinations
from typing import Optional

import pandas as pd

from core.db import get_connection


# ── Column name normalization ────────────────────────────────────────────────
# Amazon exports vary; map known variants to canonical names.

_AMAZON_COL_MAP = {
    # Identifiers
    "order date": "order_date",
    "order id": "order_id",
    "website order id": "order_id",
    "payment reference id": "payment_ref_id",
    "payment date": "payment_date",
    # Product
    "product name": "product_name",
    "title": "product_name",
    "asin": "asin",
    "amazon-internal product category": "amazon_category",
    # Amounts — Business format (per-item with tax baked in)
    "item net total": "item_net_total",
    "item subtotal": "item_subtotal",
    "item tax": "item_tax",
    "item shipping & handling": "item_shipping",
    "item promotion": "item_promotion",
    "payment amount": "payment_amount",
    "order net total": "order_net_total",
    # Amounts — Privacy Central format
    "item total": "item_total",
    "total owed": "total_owed",
    "unit price": "unit_price",
    "unit price tax": "unit_price_tax",
    "shipping charge": "shipping_charge",
    # Shared
    "quantity": "quantity",
    "item quantity": "item_quantity",
    "order quantity": "order_quantity",
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


# ── Amazon Business category mapping ─────────────────────────────────────────
# Maps Amazon's internal product categories to our expense categories.

_AMAZON_BIZ_CATEGORY_MAP = {
    "grocery": "Groceries",
    "health and beauty": "Shopping",
    "beauty": "Shopping",
    "office product": "Shopping",
    "home improvement": "Home Improvement",
    "home": "Shopping",
    "kitchen": "Shopping",
    "lighting": "Home Improvement",
    "ce": "Electronics",
    "personal computer": "Electronics",
    "speakers": "Electronics",
    "wireless": "Electronics",
    "video games": "Electronics",
    "business, industrial, & scientific supplies basic": "Shopping",
}


def infer_category(product_name: str, amazon_category: str = "") -> str:
    """Return a category guess. Uses Amazon's built-in category if available,
    otherwise falls back to keyword matching on the product name."""
    # Try Amazon's own category first (Business CSV)
    if amazon_category:
        key = amazon_category.strip().lower()
        if key in _AMAZON_BIZ_CATEGORY_MAP:
            return _AMAZON_BIZ_CATEGORY_MAP[key]

    # Fall back to keyword matching on product name
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

    # Parse payment_date if available (Business format)
    if "payment_date" in df.columns:
        df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")
        df["payment_date"] = df["payment_date"].dt.strftime("%Y-%m-%d")

    # Detect format: Business (has item_net_total) vs Privacy Central
    is_business = "item_net_total" in df.columns

    def _parse_dollar_col(series: pd.Series) -> pd.Series:
        return (
            series.astype(str)
            .str.replace(r"[$,\"]", "", regex=True)
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )

    if is_business:
        # Business format: item_net_total already includes tax + shipping
        df["item_amount"] = _parse_dollar_col(df["item_net_total"])
        df["item_tax"] = 0.0  # already baked into item_net_total
        df["item_shipping"] = 0.0
        # Parse payment_amount for verification
        if "payment_amount" in df.columns:
            df["payment_amount"] = _parse_dollar_col(df["payment_amount"])
    else:
        # Privacy Central format: need to sum price + tax + shipping
        amount_col = None
        for candidate in ["item_total", "total_owed", "unit_price"]:
            if candidate in df.columns:
                amount_col = candidate
                break

        if amount_col is None:
            warnings.append("No recognized amount column found; amounts set to 0.")
            df["item_amount"] = 0.0
        else:
            df["item_amount"] = _parse_dollar_col(df[amount_col])

        if "unit_price_tax" in df.columns:
            df["item_tax"] = _parse_dollar_col(df["unit_price_tax"])
        else:
            df["item_tax"] = 0.0

        if "shipping_charge" in df.columns:
            df["item_shipping"] = _parse_dollar_col(df["shipping_charge"])
        else:
            df["item_shipping"] = 0.0

    # Parse quantity — Business uses "Item Quantity", Privacy Central uses "Quantity"
    qty_col = None
    for candidate in ["item_quantity", "quantity", "order_quantity"]:
        if candidate in df.columns:
            qty_col = candidate
            break
    if qty_col:
        df["quantity"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(1).astype(int)
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
    Group Amazon CSV rows by charge (payment).

    For Business CSVs (with payment_ref_id), groups by Payment Reference ID
    so each group corresponds to one bank charge. A single order may produce
    multiple charges if items ship separately.

    For Privacy Central CSVs, groups by order_id.

    Returns list of order dicts, each with:
      order_id, order_date, items, order_total, product_summary
    """
    if df.empty:
        return []

    # Decide grouping key: payment_ref_id for Business, order_id for Privacy Central
    has_payment_ref = "payment_ref_id" in df.columns
    if has_payment_ref:
        # Filter out rows with no payment ref (cancelled orders, etc.)
        df_valid = df[df["payment_ref_id"].notna() & (df["payment_ref_id"].astype(str) != "N/A")]
        group_col = "payment_ref_id"
    else:
        df_valid = df
        group_col = "order_id"

    if df_valid.empty:
        return []

    orders = []
    for group_key, group in df_valid.groupby(group_col):
        items = []
        for _, row in group.iterrows():
            items.append({
                "product_name": str(row.get("product_name", "Unknown")),
                "unit_price": float(row.get("item_amount", 0)),
                "tax": float(row.get("item_tax", 0)),
                "shipping": float(row.get("item_shipping", 0)),
                "quantity": int(row.get("quantity", 1)),
                "asin": str(row.get("asin", "")),
                "amazon_category": str(row.get("amazon_category", "")),
            })

        # Total = sum of per-item amounts
        order_total = sum(
            i["unit_price"] + i["tax"] + i["shipping"] for i in items
        )

        # For Business format, prefer payment_amount (matches bank charge exactly)
        if has_payment_ref and "payment_amount" in group.columns:
            pay_amt = group.iloc[0].get("payment_amount")
            if pd.notna(pay_amt) and float(pay_amt) > 0:
                order_total = float(pay_amt)

        # Use payment_date (actual charge date) if available, else order_date
        if has_payment_ref and "payment_date" in group.columns:
            pay_date = group.iloc[0].get("payment_date")
            if pd.notna(pay_date) and str(pay_date) != "N/A":
                charge_date = str(pay_date)
            else:
                charge_date = str(group.iloc[0]["order_date"])
        else:
            charge_date = str(group.iloc[0]["order_date"])

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

        # Use order_id for display (more recognizable than payment_ref_id)
        order_id = str(group.iloc[0].get("order_id", group_key))

        # Pick the most common amazon_category from items (for category inference)
        item_cats = [i["amazon_category"] for i in items if i["amazon_category"] and i["amazon_category"] != "nan"]
        primary_amazon_cat = max(set(item_cats), key=item_cats.count) if item_cats else ""

        orders.append({
            "order_id": order_id,
            "order_date": charge_date,
            "items": items,
            "order_total": round(order_total, 2),
            "product_summary": product_summary,
            "amazon_category": primary_amazon_cat,
            "matched": False,
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


def _amounts_match(txn_amount: float, order_total: float, tolerance_pct: float = 0.08) -> bool:
    """Check if amounts match within percentage tolerance (default 8%)."""
    txn_abs = abs(txn_amount)
    diff = abs(txn_abs - order_total)
    # Use percentage of the larger value, with a $0.10 minimum floor
    ref = max(txn_abs, order_total, 0.01)
    return diff <= max(ref * tolerance_pct, 0.10)


def match_orders_to_transactions(
    orders: list[dict],
    transactions: pd.DataFrame,
    date_window: int = 5,
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

        # Skip zero amounts and likely refunds (negative on cards that store charges as positive)
        if txn_amount == 0:
            result["match_type"] = "skip"
            results.append(result)
            continue

        # Pass 1: Exact match (amount + date within window)
        exact_matches = [
            o for o in unmatched_orders
            if not o["matched"]
            and _amounts_match(txn_amount, o["order_total"])
            and _dates_within_window(txn_date, o["order_date"], date_window)
        ]
        if exact_matches:
            # Pick closest date when multiple exact matches
            order = min(exact_matches, key=lambda o: abs(
                (datetime.strptime(txn_date, "%Y-%m-%d") - datetime.strptime(o["order_date"], "%Y-%m-%d")).days
            ))
            order["matched"] = True
            result["match_type"] = "exact"
            result["matched_order"] = order
            result["confidence"] = 0.95
            result["product_summary"] = order["product_summary"]
            result["suggested_category"] = infer_category(order["product_summary"], order.get("amazon_category", ""))
            result["order_id"] = order["order_id"]
            results.append(result)
            continue

        # Pass 2: Amount match within 30 days (wider date window)
        amount_matches = [
            o for o in unmatched_orders
            if not o["matched"]
            and _amounts_match(txn_amount, o["order_total"])
            and _dates_within_window(txn_date, o["order_date"], 10)
        ]
        if amount_matches:
            # Pick closest date when multiple amount matches
            order = min(amount_matches, key=lambda o: abs(
                (datetime.strptime(txn_date, "%Y-%m-%d") - datetime.strptime(o["order_date"], "%Y-%m-%d")).days
            ))
            order["matched"] = True
            result["match_type"] = "likely"
            result["matched_order"] = order
            result["confidence"] = 0.80
            result["product_summary"] = order["product_summary"]
            result["suggested_category"] = infer_category(order["product_summary"], order.get("amazon_category", ""))
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
                if _amounts_match(txn_amount, combo_total):
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
                    result["suggested_category"] = infer_category(summary, combo[0].get("amazon_category", ""))
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
            result["suggested_category"] = infer_category(best["product_summary"], best.get("amazon_category", ""))
            result["order_id"] = best["order_id"]
            # Don't mark as matched — user must confirm
            results.append(result)
            continue

        # No match
        results.append(result)

    return results


# ── DB persistence for Amazon orders ─────────────────────────────────────────

def save_orders_to_db(entity: str, orders: list[dict]) -> tuple[int, int]:
    """
    Save grouped Amazon orders to the amazon_orders table.

    Skips duplicates (same order_id + order_total within $0.01).
    Returns (inserted, skipped) counts.
    """
    now = datetime.now().isoformat()
    conn = get_connection(entity)
    try:
        inserted = skipped = 0
        for o in orders:
            # Check for duplicates
            existing = conn.execute(
                "SELECT id FROM amazon_orders "
                "WHERE order_id = ? AND ABS(order_total - ?) < 0.02",
                (o["order_id"], o["order_total"]),
            ).fetchone()
            if existing:
                skipped += 1
                continue

            conn.execute(
                "INSERT INTO amazon_orders "
                "(order_id, payment_ref_id, order_date, charge_date, "
                " product_summary, amazon_category, order_total, imported_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    o["order_id"],
                    o.get("payment_ref_id"),
                    o["order_date"],
                    o["order_date"],  # charge_date = order_date for grouped orders
                    o["product_summary"],
                    o.get("amazon_category", ""),
                    o["order_total"],
                    now,
                ),
            )
            inserted += 1

        conn.commit()
        return inserted, skipped
    finally:
        conn.close()


def load_orders_from_db(entity: str, unmatched_only: bool = False) -> list[dict]:
    """
    Load Amazon orders from DB in the same format as group_orders() output.
    """
    conn = get_connection(entity)
    try:
        sql = "SELECT * FROM amazon_orders"
        if unmatched_only:
            sql += " WHERE matched_transaction_id IS NULL"
        sql += " ORDER BY order_date DESC"
        rows = conn.execute(sql).fetchall()
        orders = []
        for r in rows:
            orders.append({
                "db_id": r["id"],
                "order_id": r["order_id"],
                "order_date": r["charge_date"] or r["order_date"],
                "order_total": r["order_total"],
                "product_summary": r["product_summary"],
                "amazon_category": r["amazon_category"] or "",
                "matched": False,
                "items": [],  # not stored per-item, but matching doesn't need it
            })
        return orders
    finally:
        conn.close()


def get_order_counts(entity: str) -> tuple[int, int]:
    """Return (total_orders, unmatched_orders) counts."""
    conn = get_connection(entity)
    try:
        total = conn.execute("SELECT COUNT(*) FROM amazon_orders").fetchone()[0]
        unmatched = conn.execute(
            "SELECT COUNT(*) FROM amazon_orders WHERE matched_transaction_id IS NULL"
        ).fetchone()[0]
        return total, unmatched
    finally:
        conn.close()


def mark_orders_matched(entity: str, matches: list[dict]) -> None:
    """Mark amazon_orders rows as matched after user applies matches."""
    conn = get_connection(entity)
    try:
        for m in matches:
            txn_id = m.get("transaction_id")
            order_id = m.get("order_id")
            order_total = m.get("order_total")
            if not txn_id or not order_id:
                continue
            # Match by order_id + approximate total
            if order_total is not None:
                conn.execute(
                    "UPDATE amazon_orders SET matched_transaction_id = ? "
                    "WHERE order_id = ? AND ABS(order_total - ?) < 0.02 "
                    "AND matched_transaction_id IS NULL",
                    (txn_id, order_id, abs(order_total)),
                )
            else:
                conn.execute(
                    "UPDATE amazon_orders SET matched_transaction_id = ? "
                    "WHERE order_id = ? AND matched_transaction_id IS NULL",
                    (txn_id, order_id),
                )
        conn.commit()
    finally:
        conn.close()


# ── Apply matches to DB ─────────────────────────────────────────────────────

def apply_matches(entity: str, matches: list[dict]) -> int:
    """
    Write accepted matches to the database.

    Updates transactions: notes (product names), merchant_canonical, category, confidence.
    Also marks the corresponding amazon_orders as matched.
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
    finally:
        conn.close()

    # Mark amazon_orders as matched
    mark_orders_matched(entity, matches)

    return updated

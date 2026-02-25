"""Henry Schein XLSX order parsing.

Parses Henry Schein "Items Purchased" exports and groups line items
by Invoice No so each group corresponds to one bank charge.

Output format matches Amazon's order dicts for reuse with save_orders_to_db().
"""

from datetime import datetime

import pandas as pd


def parse_henryschein_xlsx(file_or_path) -> tuple[list[dict], list[str]]:
    """
    Parse a Henry Schein Items Purchased XLSX export.

    The XLSX has a title row ("Items Purchased"), a blank row, then the
    actual header row followed by data. We detect the header row automatically.

    Returns (list of order dicts grouped by invoice, list of warnings).
    """
    warnings: list[str] = []

    try:
        df = pd.read_excel(file_or_path, header=None, engine="openpyxl")
    except Exception as exc:
        return [], [f"Failed to read XLSX: {exc}"]

    if df.empty:
        return [], ["XLSX is empty."]

    # Find the header row — look for "Invoice No" in any row
    header_idx = None
    for i, row in df.iterrows():
        vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
        if any("invoice no" in v for v in vals):
            header_idx = i
            break

    if header_idx is None:
        return [], ["Could not find header row with 'Invoice No' column."]

    # Re-read with the correct header
    df.columns = [str(c).strip() for c in df.iloc[header_idx].values]
    df = df.iloc[header_idx + 1:].reset_index(drop=True)

    # Drop fully empty rows
    df = df.dropna(how="all")

    if df.empty:
        return [], ["No data rows found after header."]

    # Normalize column names to lowercase for matching
    col_map = {c: c for c in df.columns}
    col_lower = {c.lower(): c for c in df.columns}

    def _get_col(name: str) -> str | None:
        return col_lower.get(name.lower())

    # Required columns
    invoice_col = _get_col("Invoice No")
    desc_col = _get_col("Short Description")
    amount_col = _get_col("Amount")
    invoice_date_col = _get_col("Invoice Date")

    missing = []
    if not invoice_col:
        missing.append("Invoice No")
    if not desc_col:
        missing.append("Short Description")
    if not amount_col:
        missing.append("Amount")
    if not invoice_date_col:
        missing.append("Invoice Date")

    if missing:
        return [], [f"Missing required columns: {', '.join(missing)}"]

    # Optional columns
    category_col = _get_col("Category")
    subcat1_col = _get_col("Sub Category1")
    manufacturer_col = _get_col("Manufacturer")
    qty_col = _get_col("Qty")
    unit_price_col = _get_col("Unit Price")
    item_code_col = _get_col("Item Code")

    # Parse amounts
    def _parse_amount(val) -> float:
        if pd.isna(val):
            return 0.0
        s = str(val).replace("$", "").replace(",", "").strip()
        try:
            return float(s)
        except ValueError:
            return 0.0

    # Parse dates
    def _parse_date(val) -> str | None:
        if pd.isna(val):
            return None
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d")
        try:
            return pd.to_datetime(val).strftime("%Y-%m-%d")
        except Exception:
            return None

    # Filter rows with valid invoice numbers
    df = df[df[invoice_col].notna()].copy()
    if df.empty:
        return [], ["No rows with valid Invoice No found."]

    # Group by Invoice No
    orders = []
    for inv_no, group in df.groupby(invoice_col):
        inv_str = str(inv_no).strip()
        if not inv_str or inv_str.lower() == "nan":
            continue

        items = []
        for _, row in group.iterrows():
            items.append({
                "description": str(row.get(desc_col, "Unknown")),
                "amount": _parse_amount(row.get(amount_col)),
                "qty": int(row.get(qty_col, 1)) if qty_col and pd.notna(row.get(qty_col)) else 1,
                "unit_price": _parse_amount(row.get(unit_price_col)) if unit_price_col else 0,
                "item_code": str(row.get(item_code_col, "")) if item_code_col else "",
                "manufacturer": str(row.get(manufacturer_col, "")) if manufacturer_col and pd.notna(row.get(manufacturer_col)) else "",
                "hs_category": str(row.get(category_col, "")) if category_col and pd.notna(row.get(category_col)) else "",
                "hs_subcat": str(row.get(subcat1_col, "")) if subcat1_col and pd.notna(row.get(subcat1_col)) else "",
            })

        # Invoice total = sum of Amount column for this invoice
        inv_total = round(sum(i["amount"] for i in items), 2)

        # Invoice date — use first row's date
        inv_date = _parse_date(group.iloc[0].get(invoice_date_col))
        if not inv_date:
            warnings.append(f"Invoice {inv_str}: unparseable date, skipped.")
            continue

        # Product summary
        names = [i["description"] for i in items]
        if len(names) == 1:
            product_summary = names[0]
        elif len(names) == 2:
            product_summary = f"{names[0]}, {names[1]}"
        else:
            product_summary = f"{names[0]} + {len(names) - 1} more"

        if len(product_summary) > 200:
            product_summary = product_summary[:197] + "..."

        # Primary category from items
        item_cats = [i["hs_category"] for i in items if i["hs_category"]]
        primary_cat = max(set(item_cats), key=item_cats.count) if item_cats else ""

        orders.append({
            "order_id": inv_str,
            "order_date": inv_date,
            "order_total": inv_total,
            "product_summary": product_summary,
            "amazon_category": primary_cat,  # reuse field name for compatibility
            "matched": False,
            "items": items,
        })

    if not orders:
        warnings.append("No valid invoices found.")

    return orders, warnings

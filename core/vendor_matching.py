"""Vendor matching — link Venmo/PayPal vendor transactions to bank charges.

Similar to core/amazon.py but simpler: 1:1 matches only, no multi-order grouping.
Enriches bank-side transactions with recipient names from vendor payment accounts.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from core.db import get_connection

log = logging.getLogger(__name__)

# ── Matching thresholds ──────────────────────────────────────────────────────

# Pass 1 — Exact: tight amount + date → auto-apply
_EXACT_AMOUNT_PCT = 0.01   # 1% tolerance
_EXACT_DATE_DAYS = 3
_EXACT_CONFIDENCE = 0.95

# Pass 2 — Likely: tight amount + wider date → user review
_LIKELY_AMOUNT_PCT = 0.01
_LIKELY_DATE_DAYS = 7
_LIKELY_CONFIDENCE = 0.80

# Pass 3 — Loose: wider amount + date → user review
_LOOSE_AMOUNT_PCT = 0.05   # 5% tolerance
_LOOSE_DATE_DAYS = 10
_LOOSE_CONFIDENCE = 0.50

# Bank-side merchant patterns that indicate Venmo/PayPal charges
_VENMO_PATTERNS = ("venmo",)
_PAYPAL_PATTERNS = ("paypal",)


def match_vendor_to_bank(entity_key: str) -> dict:
    """Run 3-pass matching of vendor transactions to bank charges.

    Returns dict with:
        auto_applied: int — exact matches applied automatically
        review: list[dict] — uncertain matches needing user review
        unmatched_vendor: int — vendor txns with no bank match
        unmatched_bank: int — bank Venmo/PayPal txns with no vendor match
    """
    conn = get_connection(entity_key)
    try:
        return _run_matching(conn, entity_key)
    finally:
        conn.close()


def _run_matching(conn, entity_key: str) -> dict:
    """Core matching logic."""

    # Load unmatched vendor transactions (debits only, amount > 0)
    vendor_rows = conn.execute(
        "SELECT id, plaid_item_id, date, amount, amount_cents, name, "
        "merchant_name, recipient, vendor_type "
        "FROM vendor_transactions "
        "WHERE matched_transaction_id IS NULL AND amount > 0 "
        "ORDER BY date"
    ).fetchall()
    vendor_txns = [dict(r) for r in vendor_rows]

    if not vendor_txns:
        return {"auto_applied": 0, "review": [], "unmatched_vendor": 0, "unmatched_bank": 0}

    # Load bank-side Venmo/PayPal transactions (no existing vendor match)
    # Match by merchant_raw containing "venmo" or "paypal" (case-insensitive)
    bank_rows = conn.execute(
        "SELECT transaction_id, date, amount, amount_cents, "
        "description_raw, merchant_raw, merchant_canonical, "
        "matched_order_id, notes "
        "FROM transactions "
        "WHERE (LOWER(description_raw) LIKE '%venmo%' OR LOWER(description_raw) LIKE '%paypal%' "
        "   OR LOWER(merchant_raw) LIKE '%venmo%' OR LOWER(merchant_raw) LIKE '%paypal%') "
        "AND matched_order_id IS NULL "
        "ORDER BY date"
    ).fetchall()
    bank_txns = [dict(r) for r in bank_rows]

    # Filter: already matched by checking if a vendor_transaction points to this bank txn
    already_matched_bank_ids = set()
    existing = conn.execute(
        "SELECT matched_transaction_id FROM vendor_transactions "
        "WHERE matched_transaction_id IS NOT NULL"
    ).fetchall()
    for r in existing:
        already_matched_bank_ids.add(r[0])

    bank_txns = [b for b in bank_txns if b["transaction_id"] not in already_matched_bank_ids]

    if not bank_txns:
        return {
            "auto_applied": 0,
            "review": [],
            "unmatched_vendor": len(vendor_txns),
            "unmatched_bank": 0,
        }

    # Track which IDs have been matched in this run
    matched_vendor_ids = set()
    matched_bank_ids = set()
    auto_applied = 0
    review_matches = []

    # Run 3 passes
    for pass_num, (amount_pct, date_days, confidence) in enumerate([
        (_EXACT_AMOUNT_PCT, _EXACT_DATE_DAYS, _EXACT_CONFIDENCE),
        (_LIKELY_AMOUNT_PCT, _LIKELY_DATE_DAYS, _LIKELY_CONFIDENCE),
        (_LOOSE_AMOUNT_PCT, _LOOSE_DATE_DAYS, _LOOSE_CONFIDENCE),
    ], start=1):
        for vt in vendor_txns:
            if vt["id"] in matched_vendor_ids:
                continue

            # Vendor amount is positive (Plaid debit). Bank amount is negative (our convention).
            vendor_amount = abs(vt["amount"])
            vendor_date = _parse_date(vt["date"])
            if not vendor_date:
                continue

            # Check vendor_type to filter bank txns
            vtype = vt.get("vendor_type", "")

            best_match = None
            best_diff = float("inf")

            for bt in bank_txns:
                if bt["transaction_id"] in matched_bank_ids:
                    continue

                # Filter: vendor type must match bank description
                desc_lower = (bt["description_raw"] or "").lower()
                if vtype == "venmo" and "venmo" not in desc_lower:
                    continue
                if vtype == "paypal" and "paypal" not in desc_lower:
                    continue

                bank_amount = abs(bt["amount"])
                bank_date = _parse_date(bt["date"])
                if not bank_date:
                    continue

                # Amount check
                if vendor_amount == 0:
                    continue
                pct_diff = abs(vendor_amount - bank_amount) / vendor_amount
                if pct_diff > amount_pct:
                    continue

                # Date check
                day_diff = abs((vendor_date - bank_date).days)
                if day_diff > date_days:
                    continue

                # Score: prefer closest amount, then closest date
                score = pct_diff * 100 + day_diff
                if score < best_diff:
                    best_diff = score
                    best_match = bt

            if best_match:
                matched_vendor_ids.add(vt["id"])
                matched_bank_ids.add(best_match["transaction_id"])

                match_info = {
                    "vendor_id": vt["id"],
                    "bank_txn_id": best_match["transaction_id"],
                    "vendor_date": vt["date"],
                    "bank_date": best_match["date"],
                    "vendor_amount": vt["amount"],
                    "bank_amount": best_match["amount"],
                    "recipient": vt["recipient"] or vt["name"] or "",
                    "vendor_type": vtype,
                    "confidence": confidence,
                    "amount_diff": abs(abs(vt["amount"]) - abs(best_match["amount"])),
                    "date_diff": abs((_parse_date(vt["date"]) - _parse_date(best_match["date"])).days),
                    "bank_description": best_match["description_raw"],
                }

                if pass_num == 1:
                    # Auto-apply exact matches
                    _apply_single_match(conn, match_info)
                    auto_applied += 1
                else:
                    review_matches.append(match_info)

    if auto_applied > 0:
        conn.commit()

    return {
        "auto_applied": auto_applied,
        "review": review_matches,
        "unmatched_vendor": len(vendor_txns) - len(matched_vendor_ids),
        "unmatched_bank": len(bank_txns) - len(matched_bank_ids),
    }


def apply_vendor_matches(entity_key: str, matches: list[dict]) -> int:
    """Apply a list of accepted vendor matches.

    Each match dict must have: vendor_id, bank_txn_id, recipient, vendor_type, confidence.
    Returns count of matches applied.
    """
    conn = get_connection(entity_key)
    applied = 0
    try:
        for m in matches:
            _apply_single_match(conn, m)
            applied += 1
        conn.commit()
    finally:
        conn.close()
    return applied


def _apply_single_match(conn, match: dict):
    """Apply a single vendor-to-bank match.

    - Bank transaction: SET notes = "Recipient via Venmo", SET merchant_canonical = recipient
    - Vendor transaction: SET matched_transaction_id, match_confidence
    """
    bank_txn_id = match["bank_txn_id"]
    vendor_id = match["vendor_id"]
    recipient = match.get("recipient", "")
    vendor_type = match.get("vendor_type", "venmo")
    confidence = match.get("confidence", 0.80)

    # Enrich bank transaction
    platform = vendor_type.title()  # "Venmo" or "Paypal"
    enriched_notes = f"{recipient} via {platform}" if recipient else f"via {platform}"

    conn.execute(
        "UPDATE transactions SET notes = ?, merchant_canonical = ?, "
        "matched_order_id = ? "
        "WHERE transaction_id = ?",
        (enriched_notes, recipient or None, f"vendor:{vendor_id}", bank_txn_id),
    )

    # Mark vendor transaction as matched
    conn.execute(
        "UPDATE vendor_transactions SET matched_transaction_id = ?, match_confidence = ? "
        "WHERE id = ?",
        (bank_txn_id, confidence, vendor_id),
    )


def get_vendor_match_stats(entity_key: str) -> dict:
    """Get stats for the vendor matching page."""
    conn = get_connection(entity_key)
    try:
        total = conn.execute("SELECT COUNT(*) FROM vendor_transactions").fetchone()[0]
        matched = conn.execute(
            "SELECT COUNT(*) FROM vendor_transactions WHERE matched_transaction_id IS NOT NULL"
        ).fetchone()[0]
        return {
            "total": total,
            "matched": matched,
            "unmatched": total - matched,
        }
    finally:
        conn.close()


def _parse_date(date_str: str | None):
    """Parse YYYY-MM-DD date string."""
    if not date_str:
        return None
    try:
        return datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

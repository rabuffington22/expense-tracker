"""Categorization stub: alias matching + keyword heuristics.

This module provides a deterministic baseline categorizer that can later be
replaced with an OpenClaw LLM call.  Priority order:
  1. Merchant alias with a default_category  →  confidence 0.95
  2. Merchant alias without a default_category  →  sets merchant_canonical only
  3. Keyword heuristics  →  confidence 0.5–0.7
"""

import re
from typing import Optional

import pandas as pd

from core.db import get_connection


# ── Keyword rules (description → category, confidence) ───────────────────────

_KEYWORD_RULES: list[tuple[list[str], str, float]] = [
    (["grocery", "grocer", "safeway", "kroger", "whole foods", "trader joe",
      "aldi", "costco", "sam's club", "publix", "heb", "wegmans", "sprouts"],
     "Groceries", 0.7),
    (["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "subway",
      "pizza", "taco", "burger", "doordash", "grubhub", "ubereats", "chipotle",
      "chick-fil", "panera", "denny", "ihop", "waffle house", "wendy"],
     "Dining", 0.7),
    (["uber", "lyft", "taxi", "parking", "gas station", "shell", "chevron",
      "bp ", "exxon", "fuel", "toll", "transit", "mta", "bart", "metro",
      "amtrak", "greyhound"],
     "Transportation", 0.7),
    (["electric", "water ", "internet", "comcast", "at&t", "verizon",
      "t-mobile", "sprint", "pg&e", "atmos", "power", "utility", "xfinity",
      "spectrum"],
     "Utilities", 0.6),
    (["pharmacy", "walgreens", "cvs", "rite aid", "doctor", "hospital",
      "dental", "vision", "health", "medical", "clinic", "optometrist"],
     "Healthcare", 0.7),
    (["netflix", "spotify", "hulu", "disney", "hbo", "amazon prime",
      "apple tv", "cinema", "movie", "theater", "concert", "ticketmaster",
      "audible", "kindle"],
     "Entertainment", 0.7),
    (["amazon", "walmart", "target", "ebay", "etsy", "shopify", "clothing",
      "apparel", "bestbuy", "best buy", "apple store", "gap", "zara", "h&m"],
     "Shopping", 0.6),
    (["airline", "hotel", "airbnb", "expedia", "booking.com", "marriott",
      "hilton", "delta", "united", "southwest", "american air", "spirit",
      "vrbo"],
     "Travel", 0.7),
    (["rent", "mortgage", "hoa", "landlord", "lease", "property"],
     "Housing", 0.7),
    (["payroll", "direct dep", "salary", "income", "wages"],
     "Income", 0.7),
    (["transfer", "zelle", "venmo", "paypal", "wire", "ach"],
     "Transfers", 0.5),
    (["fee", "interest charge", "penalty", "overdraft", "late fee"],
     "Fees", 0.6),
    (["subscription", "membership", "annual fee", "monthly fee", "saas"],
     "Subscriptions", 0.6),
]


def _keyword_suggest(description: str) -> tuple[Optional[str], float]:
    desc_lower = description.lower()
    for keywords, category, confidence in _KEYWORD_RULES:
        if any(kw in desc_lower for kw in keywords):
            return category, confidence
    return None, 0.0


# ── Alias helpers ─────────────────────────────────────────────────────────────

def _get_active_aliases(entity: str) -> list[dict]:
    conn = get_connection(entity)
    try:
        rows = conn.execute(
            "SELECT pattern_type, pattern, merchant_canonical, default_category "
            "FROM merchant_aliases WHERE active=1"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _match_alias(text: str, aliases: list[dict]) -> Optional[dict]:
    text_lower = text.lower()
    for alias in aliases:
        ptype, pattern = alias["pattern_type"], alias["pattern"]
        try:
            if ptype == "contains" and pattern.lower() in text_lower:
                return alias
            elif ptype == "regex" and re.search(pattern, text, re.IGNORECASE):
                return alias
        except re.error:
            pass
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def suggest_categories(df: pd.DataFrame, entity: str) -> pd.DataFrame:
    """
    Annotate a DataFrame of transactions with suggested category / confidence.

    Operates on a copy; does not modify the DB.
    Columns written: merchant_canonical, category, confidence.
    """
    aliases = _get_active_aliases(entity)
    result = df.copy()

    for idx, row in result.iterrows():
        desc     = str(row.get("description_raw") or "")
        merchant = str(row.get("merchant_raw") or "")
        combined = f"{desc} {merchant}".strip()

        alias = _match_alias(combined, aliases)
        if alias:
            result.at[idx, "merchant_canonical"] = alias["merchant_canonical"]
            if alias.get("default_category"):
                result.at[idx, "category"]   = alias["default_category"]
                result.at[idx, "confidence"] = 0.95
                continue

        category, confidence = _keyword_suggest(combined)
        if category:
            result.at[idx, "category"]   = category
            result.at[idx, "confidence"] = confidence

    return result


def apply_aliases_to_db(entity: str) -> int:
    """
    Re-apply all active alias rules to every transaction in the DB.

    Returns the count of updated rows.
    """
    aliases = _get_active_aliases(entity)
    if not aliases:
        return 0

    conn = get_connection(entity)
    try:
        rows = conn.execute(
            "SELECT transaction_id, description_raw, merchant_raw FROM transactions"
        ).fetchall()
        updates: list[tuple] = []
        for row in rows:
            combined = f"{row['description_raw'] or ''} {row['merchant_raw'] or ''}".strip()
            alias = _match_alias(combined, aliases)
            if alias:
                updates.append((
                    alias["merchant_canonical"],
                    alias.get("default_category"),
                    0.95,
                    row["transaction_id"],
                ))
        if updates:
            conn.executemany(
                "UPDATE transactions "
                "SET merchant_canonical=?, "
                "    category=COALESCE(?, category), "
                "    confidence=? "
                "WHERE transaction_id=?",
                updates,
            )
            conn.commit()
        return len(updates)
    finally:
        conn.close()

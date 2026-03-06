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


# ── Keyword rules (description → category, subcategory, confidence) ──────────
# Each rule: (keywords, category, subcategory_or_None, confidence)
# Rules are checked in order — first match wins.

_KEYWORD_RULES: list[tuple[list[str], str, Optional[str], float]] = [
    # ── High-confidence specific matches (check first) ───────────────────
    (["autopay", "auto pay", "pymt", "payment thank you", "payment - thank you",
      "card payment", "credit card payment", "pay down",
      "amex epayment", "epayment", "mobile pmt",
      "applecard", "crcardpmt", "reward redemption"],
     "Credit Card Payment", None, 0.8),
    (["grocery", "grocer", "safeway", "kroger", "whole foods", "trader joe",
      "aldi", "costco", "sam's club", "sams club", "publix", "heb", "wegmans",
      "sprouts", "tom thumb"],
     "Food", "Groceries", 0.7),
    # ── Food — check delivery before "uber" so UberEats routes here ──────
    (["doordash", "grubhub", "ubereats", "uber eats", "postmates"],
     "Food", "Delivery", 0.7),
    (["starbucks", "dutch bros", "coffee", "cafe", "espresso"],
     "Food", "Coffee", 0.7),
    (["mcdonald", "kfc", "burger king", "taco bell", "taco",
      "wendy", "chick-fil", "sonic", "whataburger", "jack in the box",
      "in-n-out", "popeyes", "wingstop", "raising cane", "five guys",
      "checkers", "cook out", "hardee", "carl's jr",
      "pizza", "domino", "papa john", "little caesar", "burger", "fuzzys"],
     "Food", "Fast Food", 0.7),
    (["restaurant", "chipotle", "panera", "denny", "ihop",
      "waffle house", "caminos", "panda express", "subway", "olive garden",
      "applebee", "chili's", "outback", "andys", "andy's"],
     "Food", "Restaurant", 0.7),
    # ── Transportation — rideshare after delivery so plain "uber" hits here ──
    (["uber", "lyft", "taxi "],
     "Transportation", "Rideshare", 0.7),
    (["gas station", "shell", "chevron", "bp ", "exxon", "fuel",
      "sunoco", "texaco", "marathon", "speedway", "wawa", "circle k"],
     "Transportation", "Gas", 0.7),
    (["toll", "ntta"],
     "Transportation", "Tolls", 0.6),
    (["zips", "car wash"],
     "Transportation", "Maintenance", 0.6),
    (["parking", "transit", "mta", "bart ", "metro",
      "amtrak", "greyhound"],
     "Transportation", "Parking", 0.6),
    (["electric", "water ", "internet", "comcast", "at&t", "att*", "verizon",
      "t-mobile", "sprint", "pg&e", "atmos", "power", "utility", "xfinity",
      "spectrum", "frontier", "starlink", "ui.com", "waste connect",
      "primevox"],
     "Utilities", None, 0.6),
    (["pharmacy", "walgreens", "cvs", "rite aid", "doctor", "hospital",
      "dental", "vision", "health", "medical", "clinic", "optometrist",
      "labcorp", "laboratory", "quest diag", "urgent care",
      " ins ", "insur", "life ins", "dearborn", "american general",
      "metlife", "air supply"],
     "Healthcare", None, 0.7),
    (["netflix", "spotify", "hulu", "disney", "hbo", "amazon prime",
      "apple tv", "cinema", "movie", "theater", "concert", "ticketmaster",
      "audible", "kindle", "peacock", "steam games", "steam ", "gaming",
      "playstation", "xbox", "nintendo", "youtube tv", "league safe",
      "cheeky monkey", "adventure kids"],
     "Entertainment", None, 0.7),
    (["cesar mauro"],
     "Household", "Cleaning", 0.7),
    (["b&h photo", "b & h photo"],
     "Electronics", None, 0.7),
    (["madison reed"],
     "Health & Beauty", "Haircare", 0.7),
    (["poshmark"],
     "LL Expense", None, 0.7),
    (["home depot", "lowes", "lowe's", "menards", "ace hardware", "ace hdwe",
      "spray paint", "lumber", "paint", "hardware", "hdwe", "plumbing",
      "landscap", "landsculp", "lawn", "mowing", "irrigation", "grounds",
      "orkin", "pest control", "well service", "dfw security"],
     "Home", None, 0.6),
    (["airline", "hotel", "airbnb", "expedia", "booking.com", "marriott",
      "hilton", "delta", "united", "southwest", "american air", "spirit",
      "vrbo"],
     "Travel", None, 0.7),
    (["rent", "mortgage", "hoa", "landlord", "lease", "property",
      "provcom", "providential com"],
     "Housing", None, 0.7),
    # ── Business services (before Income so salary.com routes here) ────────
    (["usps", "ups ", "fedex", "postage"],
     "Shipping", None, 0.7),
    (["jani king"],
     "Facilities", "Janitorial", 0.7),
    (["on-site pc", "onsite pc"],
     "IT Services", None, 0.7),
    (["vistaprint", "printing", "shredding", "iron mountain", "ironmountain"],
     "Supplies", None, 0.6),
    (["salary.com", "greenpage payrol", "indeed"],
     "HR", None, 0.7),
    (["payroll", "direct dep", "salary", "income", "wages", "buffington ach"],
     "Income", None, 0.7),
    # ── SaaS / software subscriptions ─────────────────────────────────────
    (["adobe", "time off cloud", "digitalmarketer", "medsafe",
      "microsoft 365", "microsoft365", "google workspace",
      "quickbooks", "intuit ", "dropbox", "slack ", "zoom ", "zoom.com",
      "modernizing medi",
      "zapier", "flexibits", "miro.com", "claude.ai",
      "otter.ai", "openrouter", "anthropic"],
     "Software", None, 0.8),
    (["aes stdnt", "aes student", "student loan", "stdnt loan"],
     "Student Loans", "Ryan", 0.7),
    (["edward jones"],
     "Retirement", None, 0.7),
    (["self storage", "public storage"],
     "Storage", None, 0.6),
    (["deere credit", "kubota credit", "tractor supply"],
     "Ranch", None, 0.7),
    (["fee", "interest charge", "penalty", "overdraft", "late fee",
      "enhanced analysis", "bkcd process", "bkcd processing"],
     "Fees", None, 0.6),
    # ── Internal transfers (excluded from reports) ────
    (["online banking transfer", "wire type:wire", "wire transfer fee",
      "confirmation#"],
     "Internal Transfer", None, 0.7),
    # ── Zelle/Venmo → Needs Review ────────────────────
    (["zelle", "venmo"],
     "Needs Review", None, 0.6),
]


# Prefixes from payment platforms that obscure the actual merchant name
_PLATFORM_PREFIXES = re.compile(
    r"^(paypal\s*\*|venmo\s*\*|zelle\s*\*|sq\s*\*|tst\s*\*|sp\s*\*)\s*",
    re.IGNORECASE,
)


def _strip_platform_prefix(text: str) -> str:
    """Remove payment-platform prefixes like 'PAYPAL *' to expose merchant."""
    return _PLATFORM_PREFIXES.sub("", text).strip()


def _keyword_suggest(description: str) -> tuple[Optional[str], Optional[str], float]:
    desc_lower = description.lower()
    # Also try with platform prefix stripped
    stripped_lower = _strip_platform_prefix(desc_lower)
    for keywords, category, subcategory, confidence in _KEYWORD_RULES:
        if any(kw in desc_lower or kw in stripped_lower for kw in keywords):
            return category, subcategory, confidence
    return None, None, 0.0


# ── Alias helpers ─────────────────────────────────────────────────────────────

def _get_active_aliases(entity: str) -> list[dict]:
    conn = get_connection(entity)
    try:
        rows = conn.execute(
            "SELECT pattern_type, pattern, merchant_canonical, default_category, "
            "default_subcategory FROM merchant_aliases WHERE active=1"
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

        # Try alias match on both raw and prefix-stripped text
        stripped = _strip_platform_prefix(combined)
        alias = _match_alias(combined, aliases) or _match_alias(stripped, aliases)
        if alias:
            result.at[idx, "merchant_canonical"] = alias["merchant_canonical"]
            if alias.get("default_category"):
                result.at[idx, "category"]   = alias["default_category"]
                result.at[idx, "confidence"] = 0.95
                if alias.get("default_subcategory"):
                    result.at[idx, "subcategory"] = alias["default_subcategory"]
                continue

        category, subcategory, confidence = _keyword_suggest(combined)
        if category:
            result.at[idx, "category"]   = category
            result.at[idx, "confidence"] = confidence
            if subcategory:
                result.at[idx, "subcategory"] = subcategory

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
                    alias.get("default_subcategory"),
                    0.95,
                    row["transaction_id"],
                ))
        if updates:
            conn.executemany(
                "UPDATE transactions "
                "SET merchant_canonical=?, "
                "    category=COALESCE(?, category), "
                "    subcategory=COALESCE(?, subcategory), "
                "    confidence=? "
                "WHERE transaction_id=?",
                updates,
            )
            conn.commit()
        return len(updates)
    finally:
        conn.close()

"""AI client for OpenRouter API — cancellation tips, category suggestions, spending analysis."""
from __future__ import annotations

import json
import os
import urllib.request

_api_key = None
_checked = False


def _get_api_key():
    """Return the OpenRouter API key, or None if not configured."""
    global _api_key, _checked
    if _checked:
        return _api_key
    _checked = True
    _api_key = os.environ.get("OPENROUTER_API_KEY")
    return _api_key


def generate_cancellation_tips(merchant_name: str) -> str | None:
    """Generate cancellation instructions for a subscription merchant.

    Returns plain text with numbered steps, or None if unavailable.
    """
    key = _get_api_key()
    if not key:
        return None

    try:
        payload = json.dumps({
            "model": "anthropic/claude-sonnet-4.6",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Give me brief, actionable steps to cancel a {merchant_name} "
                        f"subscription. Just the steps as a numbered list, 3-5 steps max. "
                        f"Include the URL if applicable. No preamble or extra commentary."
                    ),
                }
            ],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def generate_category_suggestion(
    merchant: str,
    description: str,
    amount_cents: int,
    categories_with_subs: dict[str, list[str]],
) -> dict | None:
    """Suggest a category and subcategory for a transaction.

    Args:
        merchant: Canonical merchant name (may be empty).
        description: Raw bank description.
        amount_cents: Transaction amount in cents (negative = debit).
        categories_with_subs: Dict mapping category name to list of subcategory names.

    Returns:
        {"category": str, "subcategory": str} or None if unavailable.
    """
    key = _get_api_key()
    if not key:
        return None

    # Build the category list for the prompt
    cat_lines = []
    for cat, subs in sorted(categories_with_subs.items()):
        sub_str = ", ".join(subs) if subs else "General"
        cat_lines.append(f"  {cat}: [{sub_str}]")
    cat_list = "\n".join(cat_lines)

    amount_str = f"${abs(amount_cents) / 100:.2f}"
    direction = "expense" if amount_cents < 0 else "income"

    prompt = (
        f"Categorize this bank transaction. Pick exactly one category and one "
        f"subcategory from the list below.\n\n"
        f"Transaction:\n"
        f"  Merchant: {merchant or 'unknown'}\n"
        f"  Description: {description or 'N/A'}\n"
        f"  Amount: {amount_str} ({direction})\n\n"
        f"Available categories and subcategories:\n{cat_list}\n\n"
        f"Respond with ONLY a JSON object, no other text:\n"
        f'{{"category": "...", "subcategory": "..."}}'
    )

    try:
        payload = json.dumps({
            "model": "anthropic/claude-sonnet-4.6",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"].strip()

        # Parse JSON from response (handle markdown code fences)
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)

        cat = result.get("category", "")
        sub = result.get("subcategory", "")

        # Validate against the provided category list
        if cat not in categories_with_subs:
            return None
        valid_subs = categories_with_subs[cat]
        if sub not in valid_subs:
            sub = "General"  # Fall back to General if subcategory invalid

        return {"category": cat, "subcategory": sub}
    except Exception:
        return None


def generate_spending_analysis(spending_summary: str) -> list[dict] | None:
    """Generate AI-powered spending insights from a text summary.

    Args:
        spending_summary: Pre-formatted text summary of spending data.

    Returns:
        List of {"text": str, "category": str|None} dicts, or None if unavailable.
    """
    key = _get_api_key()
    if not key:
        return None

    prompt = (
        "You are a personal finance analyst. Analyze this spending data and provide "
        "3-5 specific, actionable observations. Focus on:\n"
        "- Unusual spending patterns or outliers\n"
        "- Categories with significant changes between periods\n"
        "- Merchants that stand out (frequency or amount)\n"
        "- Potential savings opportunities\n"
        "- Income vs spending balance\n\n"
        "Be specific with dollar amounts and category/merchant names from the data. "
        "Each insight should be one concise sentence.\n\n"
        "Return ONLY a JSON array of objects with \"text\" and optional \"category\" fields:\n"
        '[{"text": "Food spending jumped $340 this month, driven by 12 DoorDash orders", "category": "Food"}]\n\n'
        f"Spending Data:\n{spending_summary}"
    )

    try:
        payload = json.dumps({
            "model": "anthropic/claude-sonnet-4.6",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"].strip()

        # Parse JSON from response (handle markdown code fences)
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)

        # Validate: must be a list of dicts with "text" keys
        if not isinstance(result, list):
            return None
        validated = []
        for item in result[:5]:
            if isinstance(item, dict) and "text" in item:
                validated.append({
                    "text": item["text"],
                    "category": item.get("category"),
                })
        return validated if validated else None
    except Exception:
        return None

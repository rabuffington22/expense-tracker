"""AI client for OpenRouter API — cancellation tips, category suggestions, spending analysis, planning chat."""
from __future__ import annotations

import json
import logging
import os
import urllib.request

log = logging.getLogger(__name__)

_api_key = None
_checked = False

MODEL_SONNET = "anthropic/claude-sonnet-4.6"
MODEL_OPUS = "anthropic/claude-opus-4.6"


def _get_api_key():
    """Return the OpenRouter API key, or None if not configured."""
    global _api_key, _checked
    if _checked:
        return _api_key
    _checked = True
    _api_key = os.environ.get("OPENROUTER_API_KEY")
    return _api_key


def chat_completion(
    messages: list[dict],
    model: str = MODEL_SONNET,
    max_tokens: int = 1000,
    system: str | None = None,
    timeout: int = 45,
) -> str | None:
    """Send a chat completion request to OpenRouter.

    Args:
        messages: List of {"role": "user"|"assistant", "content": str} dicts.
        model: OpenRouter model identifier.
        max_tokens: Max response tokens.
        system: Optional system prompt.
        timeout: Request timeout in seconds.

    Returns:
        Response text string, or None on failure.
    """
    key = _get_api_key()
    if not key:
        return None

    try:
        body = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            body["messages"] = [{"role": "system", "content": system}] + body["messages"]

        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        log.exception("OpenRouter chat_completion failed (model=%s)", model)
        return None


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
        log.exception("OpenRouter cancellation_tips failed (merchant=%s)", merchant_name)
        return None


def generate_category_suggestion(
    merchant: str,
    description: str,
    amount_cents: int,
    categories_with_subs: dict[str, list[str]],
    entity_type: str = "personal",
) -> dict | None:
    """Suggest a category and subcategory for a transaction.

    Args:
        merchant: Canonical merchant name (may be empty).
        description: Raw bank description.
        amount_cents: Transaction amount in cents (negative = debit).
        categories_with_subs: Dict mapping category name to list of subcategory names.
        entity_type: "personal" or "business" — helps AI understand context.

    Returns:
        {"category": str, "subcategory": str, "reason": str} or None if unavailable.
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

    system = (
        "You are a transaction categorizer for a %s expense tracking app. "
        "Your job is to pick the single best category and subcategory for each "
        "bank transaction based on the merchant name and description.\n\n"
        "Rules:\n"
        "- You MUST pick from the provided category/subcategory list — never invent new ones\n"
        "- Use your knowledge of merchants, businesses, and common charges to identify what this is\n"
        "- If the description contains abbreviations or codes, decode them (e.g. TXT = Texas, "
        "DMV/MVD/registry = vehicle registration, POS = point of sale)\n"
        "- When uncertain between categories, pick the most specific match over General\n"
        "- Only use 'Needs Review' as an absolute last resort when you truly have no idea\n"
        "- Always include a brief reason explaining WHY you chose this category"
    ) % entity_type

    prompt = (
        "Categorize this transaction:\n\n"
        "  Merchant: %s\n"
        "  Bank description: %s\n"
        "  Amount: %s (%s)\n\n"
        "Categories:\n%s\n\n"
        "Respond with ONLY a JSON object:\n"
        '{"category": "...", "subcategory": "...", "reason": "..."}'
    ) % (merchant or "unknown", description or "N/A", amount_str, direction, cat_list)

    try:
        payload = json.dumps({
            "model": "anthropic/claude-sonnet-4.6",
            "max_tokens": 200,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
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
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"].strip()

        # Parse JSON from response (handle markdown code fences)
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)

        cat = result.get("category", "")
        sub = result.get("subcategory", "")
        reason = result.get("reason", "")

        # Validate against the provided category list
        if cat not in categories_with_subs:
            return None
        valid_subs = categories_with_subs[cat]
        if sub not in valid_subs:
            sub = "General"  # Fall back to General if subcategory invalid

        return {"category": cat, "subcategory": sub, "reason": reason}
    except Exception:
        log.exception("OpenRouter category_suggestion failed (merchant=%s)", merchant)
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
        log.exception("OpenRouter spending_analysis failed")
        return None


def generate_ie_analysis(ie_summary: str) -> list[dict] | None:
    """Generate AI-powered income vs expenses insights.

    Args:
        ie_summary: Pre-formatted text summary of income/expense trends.

    Returns:
        List of {"text": str} dicts, or None if unavailable.
    """
    key = _get_api_key()
    if not key:
        return None

    prompt = (
        "You are a personal finance analyst. Analyze this income vs expenses data "
        "and provide 3-5 high-level observations. Focus on:\n"
        "- Overall income vs spending balance and trajectory\n"
        "- Months where expenses exceeded income (and by how much)\n"
        "- Income stability or volatility across months\n"
        "- Savings rate trends (what percentage of income is being saved)\n"
        "- Seasonal patterns in income or expenses\n\n"
        "Do NOT focus on individual transactions or merchants. Keep it high-level: "
        "monthly totals, trends over time, and the relationship between income and expenses.\n"
        "Be specific with dollar amounts and percentages from the data. "
        "Each insight should be one concise sentence.\n\n"
        "Return ONLY a JSON array of objects with a \"text\" field:\n"
        '[{"text": "Net savings averaged $2,400/mo over the last 6 months, up from $1,800 previously"}]\n\n'
        f"Income vs Expenses Data:\n{ie_summary}"
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

        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)

        if not isinstance(result, list):
            return None
        validated = []
        for item in result[:5]:
            if isinstance(item, dict) and "text" in item:
                validated.append({"text": item["text"]})
        return validated if validated else None
    except Exception:
        log.exception("OpenRouter ie_analysis failed")
        return None

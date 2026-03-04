"""AI client for generating cancellation tips via OpenRouter API."""
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
            "model": "anthropic/claude-haiku-4-5-20251001",
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

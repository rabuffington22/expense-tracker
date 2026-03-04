"""AI client for generating cancellation tips via Anthropic API."""
from __future__ import annotations

import os

_client = None
_checked = False


def _get_client():
    """Return an Anthropic client, or None if API key is not configured."""
    global _client, _checked
    if _checked:
        return _client
    _checked = True
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic

        _client = anthropic.Anthropic(api_key=api_key)
    except Exception:
        _client = None
    return _client


def generate_cancellation_tips(merchant_name: str) -> str | None:
    """Generate cancellation instructions for a subscription merchant.

    Returns plain text with numbered steps, or None if unavailable.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Give me brief, actionable steps to cancel a {merchant_name} "
                        f"subscription. Just the steps as a numbered list, 3-5 steps max. "
                        f"Include the URL if applicable. No preamble or extra commentary."
                    ),
                }
            ],
        )
        return message.content[0].text.strip()
    except Exception:
        return None

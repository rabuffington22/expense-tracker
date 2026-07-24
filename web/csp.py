"""Content Security Policy helpers for HTML document responses."""
from __future__ import annotations

import base64
import os
import secrets
from typing import Any

from flask import Response, make_response, render_template


CORE_CSP_POLICY = "; ".join(
    (
        "default-src 'self'",
        "base-uri 'none'",
        "object-src 'none'",
        "frame-ancestors 'self'",
        "form-action 'self'",
        "script-src 'self'",
        "script-src-attr 'none'",
        "style-src 'self'",
        "style-src-attr 'none'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "frame-src 'none'",
        "worker-src 'self'",
        "manifest-src 'self'",
        "media-src 'none'",
    )
)

_PLAID_INITIALIZER_URL = (
    "https://cdn.plaid.com/link/v2/stable/link-initialize.js"
)
_PLAID_FRAME_ORIGIN = "https://cdn.plaid.com"
_PLAID_CONNECT_ORIGINS = {
    "sandbox": "https://sandbox.plaid.com",
    "production": "https://production.plaid.com",
}
_PLAID_CSP_MARKER = "_ledger_plaid_csp"


def _configured_plaid_environment() -> str | None:
    """Return one validated Plaid environment, defaulting only when absent."""
    configured = os.environ.get("PLAID_ENV")
    if configured is None:
        return "sandbox"
    normalized = configured.strip().lower()
    return normalized if normalized in _PLAID_CONNECT_ORIGINS else None


def _new_nonce() -> str:
    """Return a base64 nonce backed by 128 bits of CSPRNG output."""
    return base64.b64encode(secrets.token_bytes(16)).decode("ascii")


def _plaid_policy(nonce: str, environment: str | None) -> str:
    connect_sources = ["'self'"]
    if environment is not None:
        connect_sources.append(_PLAID_CONNECT_ORIGINS[environment])

    return "; ".join(
        (
            "default-src 'self'",
            "base-uri 'none'",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "form-action 'self'",
            (
                "script-src 'self' "
                f"'nonce-{nonce}' {_PLAID_INITIALIZER_URL}"
            ),
            "script-src-attr 'none'",
            f"style-src 'self' 'nonce-{nonce}'",
            f"style-src-elem 'self' 'nonce-{nonce}'",
            "style-src-attr 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self'",
            f"connect-src {' '.join(connect_sources)}",
            f"frame-src {_PLAID_FRAME_ORIGIN}",
            "worker-src 'self'",
            "manifest-src 'self'",
            "media-src 'none'",
        )
    )


def render_plaid_document(template_name: str, **context: Any) -> Response:
    """Render and mark one completed Plaid Link document response.

    The marker is attached only after Jinja rendering succeeds, so redirects
    and error-handler responses reached from a Link endpoint remain strict.
    """
    nonce = _new_nonce()
    rendered = render_template(template_name, csp_nonce=nonce, **context)
    response = make_response(rendered)
    setattr(
        response,
        _PLAID_CSP_MARKER,
        (nonce, _configured_plaid_environment()),
    )
    return response


def policy_for_html_response(response: Response) -> str:
    """Return the strict policy or the marked successful-Link variant."""
    marker = getattr(response, _PLAID_CSP_MARKER, None)
    if marker is None:
        return CORE_CSP_POLICY
    nonce, environment = marker
    return _plaid_policy(nonce, environment)

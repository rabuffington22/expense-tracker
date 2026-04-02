"""Symmetric encryption for sensitive values stored at rest (e.g. Plaid tokens).

Uses Fernet (AES-128-CBC + HMAC-SHA256) with a key derived from FLASK_SECRET.
If FLASK_SECRET is not set, encryption is a no-op (returns plaintext) so the
app still works in dev without the secret configured.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import os

log = logging.getLogger(__name__)

_fernet = None
_initialized = False


def _get_fernet():
    """Lazy-init Fernet cipher from FLASK_SECRET."""
    global _fernet, _initialized
    if _initialized:
        return _fernet
    _initialized = True

    secret = os.environ.get("FLASK_SECRET")
    if not secret:
        log.warning("FLASK_SECRET not set — Plaid tokens will NOT be encrypted at rest")
        return None

    try:
        from cryptography.fernet import Fernet
        # Derive a 32-byte key from FLASK_SECRET via SHA-256, then base64 for Fernet
        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
        _fernet = Fernet(key)
    except ImportError:
        log.warning("cryptography package not installed — Plaid tokens will NOT be encrypted at rest")
    return _fernet


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token string. Returns prefixed ciphertext or plaintext if encryption unavailable."""
    f = _get_fernet()
    if f is None:
        return plaintext
    encrypted = f.encrypt(plaintext.encode()).decode()
    return f"enc:{encrypted}"


def decrypt_token(stored: str) -> str:
    """Decrypt a stored token. Handles both encrypted (enc: prefix) and legacy plaintext."""
    if not stored or not stored.startswith("enc:"):
        return stored  # Legacy plaintext — return as-is
    f = _get_fernet()
    if f is None:
        raise RuntimeError("Cannot decrypt token: FLASK_SECRET or cryptography package not available")
    return f.decrypt(stored[4:].encode()).decode()

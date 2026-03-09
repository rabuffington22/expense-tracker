#!/usr/bin/env python3
"""Run the Ledger Flask app."""

import os
from pathlib import Path

# Load .env if present (local dev only — not used in production)
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

from web import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)

#!/usr/bin/env python3
"""Focused zero-network tests for the Phase 7 recovery synthetic proof."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from recovery_synthetic_proof import (
    SyntheticRecipient,
    b2_capability_contract,
    compute_logical_roles,
    decrypt_for_recipient,
    encrypt_for_recipients,
    run_offline_proof,
    trigger_contract,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CENTRAL = ZoneInfo("America/Chicago")


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    first = SyntheticRecipient.generate()
    second = SyntheticRecipient.generate()
    outsider = SyntheticRecipient.generate()
    plaintext = b"synthetic recovery payload"
    envelope = encrypt_for_recipients(
        plaintext,
        [first.public_key, second.public_key],
    )
    _check(decrypt_for_recipient(envelope, first) == plaintext, "first decrypt")
    _check(decrypt_for_recipient(envelope, second) == plaintext, "second decrypt")
    try:
        decrypt_for_recipient(envelope, outsider)
        raise AssertionError("outsider decrypt unexpectedly passed")
    except ValueError:
        pass

    now = datetime(2026, 7, 30, 10, 47, tzinfo=CENTRAL)
    records = [
        {
            "set_id": f"set-{offset}",
            "acquired_at": now - timedelta(days=offset),
            "status": "complete",
            "manifest_published": True,
        }
        for offset in range(400)
    ]
    records.append(
        {
            "set_id": "partial",
            "acquired_at": now + timedelta(days=1),
            "status": "partial-failed",
            "manifest_published": False,
        }
    )
    roles = compute_logical_roles(records)
    _check(len(roles["daily"]) == 14, "daily role count")
    _check(len(roles["weekly"]) == 8, "weekly role count")
    _check(len(roles["monthly"]) == 12, "monthly role count")
    _check(
        all("partial" not in values for values in roles.values()),
        "partial set must be excluded",
    )

    trigger = trigger_contract(REPO_ROOT / "fly.toml")
    _check(
        trigger["selected"]["mechanism"]
        == "scheduled-authenticated-synchronous-https",
        "wake-capable trigger selection",
    )
    capabilities = b2_capability_contract()
    _check(
        capabilities["matrix"]["uploader"]["hide_by_name"] is True,
        "writeFiles hide-by-name caveat",
    )
    _check(
        capabilities["matrix"]["uploader"]["delete_version"] is False,
        "uploader delete denial",
    )
    _check(
        capabilities["matrix"]["retention_extender"][
            "shorten_governance_retention"
        ]
        is False,
        "retention shortening denial",
    )

    with tempfile.TemporaryDirectory(prefix="ledger_recovery_proof_") as tmpdir:
        summary = run_offline_proof(REPO_ROOT, Path(tmpdir))
    _check(summary["status"] == "passed-local-stage", "offline proof status")
    _check(summary["network_calls"] == 0, "offline proof network count")
    _check(
        summary["protected_data_reads"] == 0,
        "offline proof protected-data count",
    )
    _check(
        summary["complete_set"]["manifest_published"] is True,
        "complete manifest",
    )
    _check(
        summary["partial_set"]["manifest_published"] is False,
        "partial manifest denial",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

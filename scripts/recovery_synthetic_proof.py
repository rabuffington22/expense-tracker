#!/usr/bin/env python3
"""Offline synthetic proof for the Phase 7 recovery trigger and provider contract.

This module never reads DATA_DIR, contacts Fly or Backblaze, or writes outside
an explicitly supplied temporary root. It is proof code for work block 7C, not
the production recovery implementation.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional
from zoneinfo import ZoneInfo

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


CENTRAL = ZoneInfo("America/Chicago")
ENTITIES = ("personal", "company", "luxelegacy")
ENVELOPE_AAD = b"ledger-synthetic-recovery-envelope-v1"
WRAP_INFO = b"ledger-synthetic-recovery-wrap-v1"


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))


def _public_bytes(key: x25519.X25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _fingerprint(key: x25519.X25519PublicKey) -> str:
    return hashlib.sha256(_public_bytes(key)).hexdigest()[:24]


@dataclass(frozen=True)
class SyntheticRecipient:
    """One synthetic X25519 recipient used only inside the offline proof."""

    private_key: x25519.X25519PrivateKey

    @classmethod
    def generate(cls) -> "SyntheticRecipient":
        return cls(x25519.X25519PrivateKey.generate())

    @property
    def public_key(self) -> x25519.X25519PublicKey:
        return self.private_key.public_key()

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.public_key)


def _derive_wrap_key(shared_secret: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=WRAP_INFO,
    ).derive(shared_secret)


def encrypt_for_recipients(
    plaintext: bytes,
    recipients: Iterable[x25519.X25519PublicKey],
) -> bytes:
    """Encrypt one payload for multiple independent synthetic recipients.

    This proves the two-recipient envelope property with the same X25519
    primitive used by age recipients. It intentionally does not claim age file
    format interoperability; that belongs to the disabled implementation block.
    """

    recipient_list = list(recipients)
    if len(recipient_list) < 2:
        raise ValueError("at least two recipients are required")

    file_key = AESGCM.generate_key(bit_length=256)
    payload_nonce = os.urandom(12)
    ciphertext = AESGCM(file_key).encrypt(payload_nonce, plaintext, ENVELOPE_AAD)

    wrapped_keys = []
    for recipient in recipient_list:
        ephemeral = x25519.X25519PrivateKey.generate()
        shared = ephemeral.exchange(recipient)
        wrap_key = _derive_wrap_key(shared)
        wrap_nonce = os.urandom(12)
        fingerprint = _fingerprint(recipient)
        wrapped = AESGCM(wrap_key).encrypt(
            wrap_nonce,
            file_key,
            fingerprint.encode("ascii"),
        )
        wrapped_keys.append(
            {
                "recipient": fingerprint,
                "ephemeral_public": _b64(_public_bytes(ephemeral.public_key())),
                "nonce": _b64(wrap_nonce),
                "wrapped_file_key": _b64(wrapped),
            }
        )

    envelope = {
        "version": "ledger-synthetic-envelope-v1",
        "cipher": "AES-256-GCM",
        "recipient_model": "X25519-HKDF-SHA256",
        "payload_nonce": _b64(payload_nonce),
        "ciphertext": _b64(ciphertext),
        "wrapped_keys": wrapped_keys,
    }
    return json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def decrypt_for_recipient(
    envelope_bytes: bytes,
    recipient: SyntheticRecipient,
) -> bytes:
    envelope = json.loads(envelope_bytes)
    matching = [
        wrapped
        for wrapped in envelope["wrapped_keys"]
        if wrapped["recipient"] == recipient.fingerprint
    ]
    if len(matching) != 1:
        raise ValueError("recipient is not uniquely authorized")

    wrapped = matching[0]
    ephemeral_public = x25519.X25519PublicKey.from_public_bytes(
        _unb64(wrapped["ephemeral_public"])
    )
    shared = recipient.private_key.exchange(ephemeral_public)
    wrap_key = _derive_wrap_key(shared)
    file_key = AESGCM(wrap_key).decrypt(
        _unb64(wrapped["nonce"]),
        _unb64(wrapped["wrapped_file_key"]),
        recipient.fingerprint.encode("ascii"),
    )
    return AESGCM(file_key).decrypt(
        _unb64(envelope["payload_nonce"]),
        _unb64(envelope["ciphertext"]),
        ENVELOPE_AAD,
    )


def _create_synthetic_source(path: Path, entity: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA wal_autocheckpoint=0")
    connection.execute(
        "CREATE TABLE synthetic_probe (id INTEGER PRIMARY KEY, label TEXT NOT NULL)"
    )
    connection.execute(
        "INSERT INTO synthetic_probe (label) VALUES (?)",
        (f"synthetic-{entity}",),
    )
    connection.commit()
    return connection


def _online_backup(
    source: sqlite3.Connection,
    destination: Path,
) -> tuple[bytes, str]:
    destination_connection = sqlite3.connect(destination)
    try:
        source.backup(destination_connection)
        integrity = destination_connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]
        count = destination_connection.execute(
            "SELECT COUNT(*) FROM synthetic_probe"
        ).fetchone()[0]
        if count != 1:
            raise AssertionError("synthetic online backup lost committed state")
    finally:
        destination_connection.close()
    return destination.read_bytes(), integrity


def run_complete_set_proof(
    root: Path,
    acquired_at: datetime,
    *,
    fail_entity: Optional[str] = None,
) -> dict:
    """Create one entirely synthetic three-entity recovery-set proof."""

    if acquired_at.tzinfo is None:
        raise ValueError("acquired_at must be timezone-aware")
    if fail_entity is not None and fail_entity not in ENTITIES:
        raise ValueError("unknown fail_entity")

    root.mkdir(parents=True, exist_ok=True)
    recipients = (SyntheticRecipient.generate(), SyntheticRecipient.generate())
    set_id = acquired_at.astimezone(CENTRAL).strftime("%Y%m%dT%H%M%S%z")
    artifacts = []
    entity_results = {}
    started_at = datetime.now(tz=CENTRAL)

    for entity in ENTITIES:
        if entity == fail_entity:
            entity_results[entity] = "failed-synthetic"
            continue

        source_path = root / f"{entity}-source.sqlite"
        backup_path = root / f"{entity}-online-backup.sqlite"
        encrypted_path = root / f"{entity}.sqlite.envelope"
        source = _create_synthetic_source(source_path, entity)
        try:
            plaintext, integrity = _online_backup(source, backup_path)
        finally:
            source.close()
        if integrity != "ok":
            raise AssertionError(f"{entity} integrity proof failed")

        envelope = encrypt_for_recipients(
            plaintext,
            [recipient.public_key for recipient in recipients],
        )
        for recipient in recipients:
            if decrypt_for_recipient(envelope, recipient) != plaintext:
                raise AssertionError(f"{entity} recipient decrypt mismatch")
        encrypted_path.write_bytes(envelope)
        artifacts.append(
            {
                "entity": entity,
                "object_key": f"sets/{set_id}/{entity}.sqlite.envelope",
                "sha256": hashlib.sha256(envelope).hexdigest(),
                "bytes": len(envelope),
                "recipients": [recipient.fingerprint for recipient in recipients],
            }
        )
        entity_results[entity] = "passed"

    complete = all(entity_results.get(entity) == "passed" for entity in ENTITIES)
    completed_at = datetime.now(tz=CENTRAL)
    manifest = None
    if complete:
        manifest_body = {
            "version": "ledger-synthetic-recovery-set-v1",
            "set_id": set_id,
            "acquired_at": acquired_at.astimezone(CENTRAL).isoformat(),
            "acquisition_window_seconds": max(
                0, int((completed_at - started_at).total_seconds())
            ),
            "status": "complete",
            "artifacts": artifacts,
            "logical_roles": [],
            "logical_roles_authoritative": False,
            "object_lock_floor_authoritative_for_logical_roles": False,
        }
        manifest_body["manifest_sha256"] = hashlib.sha256(
            json.dumps(
                manifest_body, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        manifest = manifest_body

    return {
        "set_id": set_id,
        "status": "complete" if complete else "partial-failed",
        "manifest_published": manifest is not None,
        "manifest": manifest,
        "entity_results": entity_results,
        "recipient_count": len(recipients),
    }


def compute_logical_roles(records: Iterable[dict]) -> dict[str, list[str]]:
    """Compute current logical roles from passing complete sets in Central Time."""

    passing = [
        record
        for record in records
        if record.get("status") == "complete"
        and record.get("manifest_published") is True
    ]
    passing.sort(key=lambda record: record["acquired_at"], reverse=True)

    def select(limit: int, bucket) -> list[str]:
        selected = []
        seen = set()
        for record in passing:
            local = record["acquired_at"].astimezone(CENTRAL)
            key = bucket(local)
            if key in seen:
                continue
            seen.add(key)
            selected.append(record["set_id"])
            if len(selected) == limit:
                break
        return selected

    return {
        "daily": select(14, lambda value: value.date()),
        "weekly": select(
            8,
            lambda value: (value - timedelta(days=value.weekday())).date(),
        ),
        "monthly": select(12, lambda value: (value.year, value.month)),
    }


B2_OPERATION_REQUIREMENTS = {
    "upload_object": {"writeFiles"},
    "hide_by_name": {"writeFiles"},
    "list_versions": {"listFiles"},
    "download_object": {"readFiles"},
    "delete_version": {"deleteFiles"},
    "read_retention": {"readFileRetentions"},
    "extend_retention": {"writeFileRetentions"},
    "shorten_governance_retention": {
        "writeFileRetentions",
        "bypassGovernance",
    },
    "set_legal_hold": {"writeFileLegalHolds"},
    "update_bucket_retention": {"writeBucketRetentions"},
}


def operation_allowed(capabilities: Iterable[str], operation: str) -> bool:
    required = B2_OPERATION_REQUIREMENTS[operation]
    return required.issubset(set(capabilities))


def b2_capability_contract() -> dict:
    principals = {
        "uploader": {"writeFiles"},
        "freshness_observer": {
            "listFiles",
            "readFileRetentions",
            "readFileLegalHolds",
        },
        "restore_reader": {
            "listFiles",
            "readFiles",
            "readFileRetentions",
            "readFileLegalHolds",
        },
        "retention_extender": {
            "listFiles",
            "readFileRetentions",
            "writeFileRetentions",
        },
    }
    matrix = {
        principal: {
            operation: operation_allowed(capabilities, operation)
            for operation in B2_OPERATION_REQUIREMENTS
        }
        for principal, capabilities in principals.items()
    }

    expected = {
        ("uploader", "upload_object"): True,
        ("uploader", "list_versions"): False,
        ("uploader", "download_object"): False,
        ("uploader", "delete_version"): False,
        ("uploader", "extend_retention"): False,
        ("uploader", "hide_by_name"): True,
        ("freshness_observer", "list_versions"): True,
        ("freshness_observer", "download_object"): False,
        ("freshness_observer", "upload_object"): False,
        ("restore_reader", "download_object"): True,
        ("restore_reader", "delete_version"): False,
        ("retention_extender", "extend_retention"): True,
        ("retention_extender", "shorten_governance_retention"): False,
        ("retention_extender", "delete_version"): False,
    }
    for (principal, operation), allowed in expected.items():
        if matrix[principal][operation] is not allowed:
            raise AssertionError(f"unexpected capability result: {principal}/{operation}")

    return {
        "principals": {
            principal: sorted(capabilities)
            for principal, capabilities in principals.items()
        },
        "matrix": matrix,
        "verdict": "revise-before-provider-proof",
        "revision": (
            "Backblaze writeFiles also authorizes the Native API hide-by-name "
            "operation, so an uploader key cannot be described as strict "
            "create-only. Use unique non-reusable object names, omit deleteFiles "
            "and bypassGovernance, have the independent observer list versions "
            "and alert on hide markers or duplicate names, then verify the exact "
            "behavior in the provider proof."
        ),
    }


def trigger_contract(fly_toml: Path) -> dict:
    source = fly_toml.read_text(encoding="utf-8")
    facts = {
        "auto_stop_is_stop": bool(
            re.search(r"(?m)^\s*auto_stop_machines\s*=\s*['\"]stop['\"]\s*$", source)
        ),
        "auto_start_is_true": bool(
            re.search(r"(?m)^\s*auto_start_machines\s*=\s*true\s*$", source)
        ),
        "minimum_is_zero": bool(
            re.search(r"(?m)^\s*min_machines_running\s*=\s*0\s*$", source)
        ),
        "data_volume_mounted": bool(
            re.search(r"(?m)^\s*destination\s*=\s*['\"]/data['\"]\s*$", source)
        ),
    }
    if not all(facts.values()):
        raise AssertionError(f"Fly trigger assumptions changed: {facts}")

    return {
        "facts": facts,
        "rejected": {
            "in_process_timer": (
                "cannot run while the only application Machine is stopped"
            ),
            "separate_scheduled_machine": (
                "Fly Volumes cannot be shared between Machines, so a separate "
                "scheduled Machine cannot read the active /data volume"
            ),
            "schedule_on_web_machine": (
                "Fly scheduled Machines are finite jobs and do not fit the "
                "long-running HTTP service Machine"
            ),
        },
        "selected": {
            "mechanism": "scheduled-authenticated-synchronous-https",
            "scheduler": "GitHub Actions",
            "wake_path": "Fly Proxy autostarts the existing service Machine",
            "lifecycle_rule": (
                "keep the authenticated request open until acquisition and "
                "upload finish; do not return and continue in the background"
            ),
            "schedule_default": "47 10 * * *",
            "separation_from_plaid": "90 minutes after 17 9 * * *",
        },
    }


def run_offline_proof(repo_root: Path, scratch_root: Path) -> dict:
    acquired_at = datetime(2026, 7, 30, 10, 47, tzinfo=CENTRAL)
    complete = run_complete_set_proof(
        scratch_root / "complete",
        acquired_at,
    )
    partial = run_complete_set_proof(
        scratch_root / "partial",
        acquired_at + timedelta(days=1),
        fail_entity="company",
    )
    if not complete["manifest_published"] or complete["recipient_count"] != 2:
        raise AssertionError("complete-set manifest or recipient proof failed")
    if partial["manifest_published"]:
        raise AssertionError("partial set must not publish a manifest")

    retention_records = []
    for day in range(400):
        timestamp = acquired_at - timedelta(days=day)
        retention_records.append(
            {
                "set_id": timestamp.strftime("%Y%m%d"),
                "acquired_at": timestamp,
                "status": "complete",
                "manifest_published": True,
                "synthetic_lock_floor_days": 2 if day % 2 else 20,
            }
        )
    retention_records.append(
        {
            "set_id": "partial-newest",
            "acquired_at": acquired_at + timedelta(days=2),
            "status": "partial-failed",
            "manifest_published": False,
            "synthetic_lock_floor_days": 999,
        }
    )
    roles = compute_logical_roles(retention_records)
    if {tier: len(values) for tier, values in roles.items()} != {
        "daily": 14,
        "weekly": 8,
        "monthly": 12,
    }:
        raise AssertionError("logical 14/8/12 proof failed")
    if "partial-newest" in {
        set_id for values in roles.values() for set_id in values
    }:
        raise AssertionError("partial set entered logical retention")

    changed_locks = [
        {**record, "synthetic_lock_floor_days": 3000}
        for record in retention_records
    ]
    if compute_logical_roles(changed_locks) != roles:
        raise AssertionError("Object Lock floor changed logical roles")

    return {
        "status": "passed-local-stage",
        "network_calls": 0,
        "protected_data_reads": 0,
        "complete_set": {
            "status": complete["status"],
            "manifest_published": complete["manifest_published"],
            "entities": complete["entity_results"],
            "recipient_count": complete["recipient_count"],
        },
        "partial_set": {
            "status": partial["status"],
            "manifest_published": partial["manifest_published"],
            "entities": partial["entity_results"],
        },
        "logical_retention_counts": {
            tier: len(values) for tier, values in roles.items()
        },
        "logical_retention_independent_of_lock_floor": True,
        "trigger": trigger_contract(repo_root / "fly.toml"),
        "provider_contract": b2_capability_contract(),
        "limitations": [
            "The envelope proves two independent X25519 recipients but is not an age-format interoperability test.",
            "The B2 capability matrix is an offline official-contract model, not provider execution evidence.",
            "No Fly Machine, workflow, endpoint, provider resource, credential, or production recovery code was created.",
        ],
    }

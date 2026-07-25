#!/usr/bin/env python3
"""Fail closed when the core synthetic CI workflow exceeds its approved contract."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "synthetic-ci.yml"

CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"

EXPECTED_USES = [
    f"actions/checkout@{CHECKOUT_SHA}",
    f"actions/setup-python@{SETUP_PYTHON_SHA}",
]

EXPECTED_RUN_COMMANDS = [
    "python -m pip install --disable-pip-version-check -r requirements.txt",
    "python scripts/ci_safety_check.py",
    "python scripts/smoke_test.py",
    "python -m compileall -q core web scripts run.py",
    "git ls-files -z '*.js' | xargs -0 -n1 node --check",
    "python -m json.tool command-center/state.json > /dev/null",
    "node command-center/scripts/refresh-dashboard.js --check",
    "node command-center/scripts/health-check.js --ci",
    'git diff --check "${{ github.event.pull_request.base.sha }}" HEAD',
]

FORBIDDEN_FRAGMENTS = [
    "pull_request_target",
    "workflow_dispatch",
    "schedule:",
    "secrets.",
    "contents: write",
    "actions: write",
    "checks: write",
    "deployments: write",
    "id-token: write",
    "packages: write",
    "persist-credentials: true",
    "requirements-dev.txt",
    "mobile_drawer_browser_test.py",
    "upload-artifact",
    "download-artifact",
    "actions/cache",
    "continue-on-error:",
    "container:",
    "environment:",
    "flyctl",
    "services:",
    "sync-all",
    "plaid",
    "local_state",
    ".env",
    "curl ",
    "wget ",
]


def fail(message: str) -> None:
    raise SystemExit(f"synthetic CI safety check failed: {message}")


def significant_lines(source: str) -> list[str]:
    return [
        line.rstrip()
        for line in source.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def main() -> None:
    if not WORKFLOW.is_file():
        fail(f"missing {WORKFLOW.relative_to(ROOT)}")

    source = WORKFLOW.read_text(encoding="utf-8")
    lowered = source.lower()
    lines = significant_lines(source)

    expected_trigger = [
        "on:",
        "  pull_request:",
        "    branches:",
        "      - main",
    ]
    trigger_start = lines.index("on:") if "on:" in lines else -1
    if (
        trigger_start < 0
        or lines[trigger_start : trigger_start + 5]
        != [*expected_trigger, "permissions:"]
    ):
        fail("trigger must be pull_request targeting main only")

    if "\npermissions:\n  contents: read\n" not in source:
        fail("top-level permissions must be contents: read")
    if len(re.findall(r"(?m)^\s*permissions:\s*$", source)) != 1:
        fail("workflow must define exactly one permissions block")

    if "runs-on: ubuntu-latest" not in source or "timeout-minutes: 20" not in source:
        fail("runner and timeout must remain ubuntu-latest and 20 minutes")
    if 'python-version: "3.12"' not in source:
        fail("Python version must remain 3.12")
    if "persist-credentials: false" not in source or "fetch-depth: 0" not in source:
        fail("checkout must fetch the PR base without persisting credentials")

    uses = re.findall(r"^\s*uses:\s*([^#\s]+)", source, flags=re.MULTILINE)
    if uses != EXPECTED_USES:
        fail(f"action list changed: {uses!r}")
    if any(not re.fullmatch(r"[^@]+@[0-9a-f]{40}", item) for item in uses):
        fail("every action reference must use a full immutable commit SHA")

    run_commands = re.findall(r"^\s*run:\s*(.+?)\s*$", source, flags=re.MULTILINE)
    if run_commands != EXPECTED_RUN_COMMANDS:
        fail("reviewed command list or order changed")

    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment in lowered:
            fail(f"forbidden workflow fragment present: {fragment}")

    if re.search(r"(?m)^\s{2}(push|schedule|workflow_dispatch|pull_request_target):", source):
        fail("an unapproved event trigger is present")
    if re.search(r"(?m)^\s+[a-z-]+:\s+write\s*$", source):
        fail("write-capable token permission is present")

    print("Synthetic CI safety contract passed")


if __name__ == "__main__":
    main()

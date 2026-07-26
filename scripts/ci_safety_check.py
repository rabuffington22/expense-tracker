#!/usr/bin/env python3
"""Fail closed when the synthetic CI workflow exceeds its approved contract."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "synthetic-ci.yml"
DEV_REQUIREMENTS = ROOT / "requirements-dev.txt"
BROWSER_TEST = ROOT / "scripts" / "mobile_drawer_browser_test.py"

CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"

EXPECTED_USES = [
    f"actions/checkout@{CHECKOUT_SHA}",
    f"actions/setup-python@{SETUP_PYTHON_SHA}",
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
    "google-chrome --version",
    "python -m pip install --disable-pip-version-check -r requirements-dev.txt",
    "python scripts/mobile_drawer_browser_test.py",
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
    "upload-artifact",
    "download-artifact",
    "actions/cache",
    "cache:",
    "playwright install",
    "install-deps",
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

EXPECTED_DEV_REQUIREMENTS = [
    "-r requirements.txt",
    "playwright>=1.50.0,<2.0.0",
]

BROWSER_SAFETY_ANCHORS = [
    'tempfile.TemporaryDirectory(prefix="expense_drawer_browser_")',
    'playwright.chromium.launch(channel="chrome", headless=True)',
    'page.route("**/*", route_request)',
    'page.route("**/*", route_auth_request)',
    'route.abort()',
    '"temporary DATA_DIR cleanup must be exact"',
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

    jobs_source = source.split("\njobs:\n", maxsplit=1)
    if len(jobs_source) != 2:
        fail("workflow must define one jobs block")
    job_ids = re.findall(
        r"(?m)^  ([a-z][a-z0-9-]+):\s*$",
        jobs_source[1],
    )
    if job_ids != ["core-synthetic", "browser-synthetic"]:
        fail(f"job list or order changed: {job_ids!r}")

    runners = re.findall(r"(?m)^\s*runs-on:\s*(\S+)\s*$", source)
    timeouts = re.findall(r"(?m)^\s*timeout-minutes:\s*(\d+)\s*$", source)
    if runners != ["ubuntu-latest", "ubuntu-24.04"]:
        fail(f"runner list changed: {runners!r}")
    if timeouts != ["20", "15"]:
        fail(f"timeout list changed: {timeouts!r}")
    if re.findall(r"(?m)^\s* needs:\s*(\S+)\s*$", source) != ["core-synthetic"]:
        fail("browser job must depend only on core-synthetic")
    if source.count('python-version: "3.12"') != 2:
        fail("both jobs must use Python 3.12")
    if source.count("persist-credentials: false") != 2:
        fail("both checkouts must avoid persisted credentials")
    if source.count("fetch-depth: 0") != 1 or source.count("fetch-depth: 1") != 1:
        fail("core checkout must fetch PR history and browser checkout must stay shallow")

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

    if not DEV_REQUIREMENTS.is_file():
        fail(f"missing {DEV_REQUIREMENTS.relative_to(ROOT)}")
    requirements = [
        line.strip()
        for line in DEV_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if requirements != EXPECTED_DEV_REQUIREMENTS:
        fail(f"browser dependency contract changed: {requirements!r}")

    if not BROWSER_TEST.is_file():
        fail(f"missing {BROWSER_TEST.relative_to(ROOT)}")
    browser_source = BROWSER_TEST.read_text(encoding="utf-8")
    missing_anchors = [
        anchor for anchor in BROWSER_SAFETY_ANCHORS if anchor not in browser_source
    ]
    if missing_anchors:
        fail(f"browser safety anchors missing: {missing_anchors!r}")
    if browser_source.count('playwright.chromium.launch(channel="chrome", headless=True)') != 2:
        fail("browser suite must use installed Chrome in both auth modes")
    if browser_source.count("route.abort()") != 2:
        fail("browser suite must retain both non-localhost request denials")

    print("Synthetic CI safety contract passed")


if __name__ == "__main__":
    main()

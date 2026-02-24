#!/usr/bin/env bash
set -euo pipefail

# ── Expense Tracker — Atlas Mac Mini Setup ────────────────────────────────────
# Run this ON Atlas after cloning the repo:
#   cd ~/expense-tracker && bash scripts/setup-atlas.sh
#
# What it does:
#   1. Creates DATA_DIR at ~/expense-data
#   2. Creates a Python venv using Homebrew Python
#   3. Installs pip dependencies
#   4. Runs the smoke test
#   5. Installs + loads a launchd service (auto-start on boot)

REPO_DIR="$HOME/expense-tracker"
DATA_DIR="$HOME/expense-data"
PYTHON="/opt/homebrew/bin/python3"
VENV_DIR="$REPO_DIR/.venv"
PLIST_NAME="com.expense-tracker.streamlit"
PLIST_SRC="$REPO_DIR/scripts/$PLIST_NAME.plist"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
LOG_FILE="/tmp/expense-tracker.log"

echo "═══════════════════════════════════════════"
echo "  Expense Tracker — Atlas Setup"
echo "═══════════════════════════════════════════"
echo ""

# ── 1. DATA_DIR ───────────────────────────────────────────────────────────────
echo "1. Creating DATA_DIR at $DATA_DIR …"
mkdir -p "$DATA_DIR/uploads" "$DATA_DIR/backups"
echo "   ✅ $DATA_DIR ready"

# ── 2. Python venv ────────────────────────────────────────────────────────────
echo ""
echo "2. Setting up Python venv …"
if [ ! -f "$PYTHON" ]; then
    echo "   ❌ Homebrew Python not found at $PYTHON"
    echo "   Install with: brew install python3"
    exit 1
fi
echo "   Python: $($PYTHON --version)"

if [ -d "$VENV_DIR" ]; then
    echo "   venv already exists — skipping creation"
else
    "$PYTHON" -m venv "$VENV_DIR"
    echo "   ✅ venv created at $VENV_DIR"
fi

echo ""
echo "3. Installing dependencies …"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$REPO_DIR/requirements.txt"
echo "   ✅ Dependencies installed"

# ── 4. Smoke test ─────────────────────────────────────────────────────────────
echo ""
echo "4. Running smoke test …"
DATA_DIR="$DATA_DIR" "$VENV_DIR/bin/python" "$REPO_DIR/scripts/smoke_test.py"

# ── 5. Generate launchd plist from template ───────────────────────────────────
echo ""
echo "5. Installing launchd service …"

USER_HOME="$HOME"
# Replace __HOME__ placeholders in the template plist
sed "s|__HOME__|$USER_HOME|g" "$PLIST_SRC" > "$PLIST_DST"
echo "   Plist installed at $PLIST_DST"

# Unload if already loaded (ignore errors)
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"
echo "   ✅ Service loaded and running"

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅  Setup complete!"
echo ""
echo "  DATA_DIR:  $DATA_DIR"
echo "  App:       http://127.0.0.1:8501"
echo "  Logs:      $LOG_FILE"
echo "  Service:   launchctl list | grep expense"
echo ""
echo "  To update the Tailscale bind address:"
echo "    Edit $PLIST_DST"
echo "    Change 127.0.0.1 to your Tailscale IP"
echo "    launchctl unload $PLIST_DST"
echo "    launchctl load $PLIST_DST"
echo "═══════════════════════════════════════════"

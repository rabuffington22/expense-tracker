#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "${BASH_SOURCE[0]%/*}" 2>/dev/null && pwd -P)" || exit 1
HARNESS="$SCRIPT_DIR/s3_assumption_probe.sh"
TEST_ROOT=""
SENTINEL_LOG=""
PASS_COUNT=0

mark_pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  printf 'CASE=passed:%s\n' "$1"
}

fail_test() {
  printf 'CASE=failed:%s\n' "$1"
  exit 1
}

cleanup_test_root() {
  trap - EXIT
  if [[ -n "$TEST_ROOT" && "$TEST_ROOT" == /tmp/ledger-assumption-probe-tests.* && -d "$TEST_ROOT" && ! -L "$TEST_ROOT" && -O "$TEST_ROOT" ]]; then
    /bin/rm -rf "$TEST_ROOT"
  fi
}

assert_contains() {
  local value="$1"
  local expected="$2"
  local label="$3"
  [[ "$value" == *"$expected"* ]] || fail_test "$label"
}

assert_not_contains() {
  local value="$1"
  local unexpected="$2"
  local label="$3"
  [[ "$value" != *"$unexpected"* ]] || fail_test "$label"
}

run_harness() {
  local mode="$1"
  local scenario="$2"
  shift 2
  PROBE_MODE="$mode" \
  PROBE_TEST_SCENARIO="$scenario" \
  PATH="$TEST_ROOT/hostile:/usr/bin:/bin" \
  SENTINEL_LOG="$SENTINEL_LOG" \
  AWS_ACCESS_KEY_ID="AMBIENT_ACCESS" \
  AWS_SECRET_ACCESS_KEY="AMBIENT_SECRET" \
  AWS_SESSION_TOKEN="AMBIENT_TOKEN" \
  AWS_PROFILE="ambient-profile" \
  AWS_DEFAULT_PROFILE="ambient-default-profile" \
  AWS_REGION="ambient-region" \
  AWS_DEFAULT_REGION="ambient-default-region" \
  AWS_ROLE_ARN="ambient-role" \
  AWS_WEB_IDENTITY_TOKEN_FILE="ambient-token-file" \
  AWS_CONFIG_FILE="ambient-config" \
  AWS_SHARED_CREDENTIALS_FILE="ambient-credentials" \
    /bin/bash "$HARNESS" "$@"
}

expect_case() {
  local label="$1"
  local expected_status="$2"
  local mode="$3"
  local scenario="$4"
  local required_marker="$5"
  shift 5
  local output
  local status

  output="$(run_harness "$mode" "$scenario" "$@" 2>&1)"
  status=$?
  [[ "$status" == "$expected_status" ]] || fail_test "$label-status"
  assert_contains "$output" "$required_marker" "$label-marker"
  if [[ "$label" == "success" ]]; then
    assert_contains "$output" "CHECK=passed:mock-environment" "$label-environment"
    assert_contains "$output" "CHECK=passed:invocation-sequence" "$label-invocations"
    assert_contains "$output" "CLEANUP=passed:offline-root-absent" "$label-cleanup"
  fi
  case "$label" in
    mode-*|scenario-invalid)
      assert_not_contains "$output" "RUN=started" "$label-pre-run"
      assert_not_contains "$output" "CLEANUP=" "$label-pre-trap"
      ;;
  esac
  mark_pass "$label"
}

[[ -f "$HARNESS" ]] || fail_test "harness-missing"
TEST_ROOT="$(/usr/bin/mktemp -d /tmp/ledger-assumption-probe-tests.XXXXXX)" || fail_test "test-root-create"
[[ "$TEST_ROOT" == /tmp/ledger-assumption-probe-tests.* && -d "$TEST_ROOT" && ! -L "$TEST_ROOT" && -O "$TEST_ROOT" ]] || fail_test "test-root-invalid"
trap cleanup_test_root EXIT

/bin/mkdir "$TEST_ROOT/hostile" "$TEST_ROOT/validator"
SENTINEL_LOG="$TEST_ROOT/sentinel.log"
: >"$SENTINEL_LOG"
/bin/cat >"$TEST_ROOT/hostile/aws" <<'SENTINEL'
#!/bin/bash
printf 'called\n' >>"$SENTINEL_LOG"
exit 99
SENTINEL
/bin/chmod 700 "$TEST_ROOT/hostile/aws"

expect_case "success" 0 "offline-test" "success" "RESULT=success"
expect_case "assume-denied" 1 "offline-test" "assume-denied" "CHECK=failed:current-session-assume-denied-or-failed"
expect_case "unexpected-caller" 1 "offline-test" "unexpected-caller" "CHECK=failed:caller-not-assumed-role"
expect_case "mode-live" 1 "live" "success" "CHECK=failed:offline-mode-required"
expect_case "mode-empty" 1 "" "success" "CHECK=failed:offline-mode-required"
expect_case "mode-unknown" 1 "unknown" "success" "CHECK=failed:offline-mode-required"
expect_case "mode-padded" 1 " offline-test " "success" "CHECK=failed:offline-mode-required"
expect_case "scenario-invalid" 1 "offline-test" "unknown" "CHECK=failed:offline-scenario-invalid"

unset_mode_output="$(/usr/bin/env -u PROBE_MODE PROBE_TEST_SCENARIO=success PATH="$TEST_ROOT/hostile:/usr/bin:/bin" SENTINEL_LOG="$SENTINEL_LOG" /bin/bash "$HARNESS" 2>&1)"
unset_mode_status=$?
[[ "$unset_mode_status" == 1 ]] || fail_test "mode-unset-status"
assert_contains "$unset_mode_output" "CHECK=failed:offline-mode-required" "mode-unset-marker"
assert_not_contains "$unset_mode_output" "RUN=started" "mode-unset-pre-run"
assert_not_contains "$unset_mode_output" "CLEANUP=" "mode-unset-pre-trap"
mark_pass "mode-unset"

injection_output="$(PROBE_MODE=offline-test PROBE_TEST_SCENARIO=success PROBE_MOCK_ROOT=/opt/homebrew PATH="$TEST_ROOT/hostile:/usr/bin:/bin" SENTINEL_LOG="$SENTINEL_LOG" /bin/bash "$HARNESS" 2>&1)"
injection_status=$?
[[ "$injection_status" == 1 ]] || fail_test "caller-root-status"
assert_contains "$injection_output" "CHECK=failed:caller-root-prohibited" "caller-root-marker"
assert_not_contains "$injection_output" "RUN=started" "caller-root-pre-run"
assert_not_contains "$injection_output" "CLEANUP=" "caller-root-pre-trap"
mark_pass "caller-root-prohibited"

executor_output="$(PROBE_MODE=offline-test PROBE_TEST_SCENARIO=success AWS_CLI_BIN=/opt/homebrew/bin/aws PATH="$TEST_ROOT/hostile:/usr/bin:/bin" SENTINEL_LOG="$SENTINEL_LOG" /bin/bash "$HARNESS" 2>&1)"
executor_status=$?
[[ "$executor_status" == 1 ]] || fail_test "caller-executor-status"
assert_contains "$executor_output" "CHECK=failed:caller-executor-prohibited" "caller-executor-marker"
assert_not_contains "$executor_output" "RUN=started" "caller-executor-pre-run"
assert_not_contains "$executor_output" "CLEANUP=" "caller-executor-pre-trap"
mark_pass "caller-executor-prohibited"

mock_executor_output="$(PROBE_MODE=offline-test PROBE_TEST_SCENARIO=success PROBE_MOCK_AWS_BIN=/opt/homebrew/bin/aws PATH="$TEST_ROOT/hostile:/usr/bin:/bin" SENTINEL_LOG="$SENTINEL_LOG" /bin/bash "$HARNESS" 2>&1)"
mock_executor_status=$?
[[ "$mock_executor_status" == 1 ]] || fail_test "caller-mock-executor-status"
assert_contains "$mock_executor_output" "CHECK=failed:caller-executor-prohibited" "caller-mock-executor-marker"
assert_not_contains "$mock_executor_output" "RUN=started" "caller-mock-executor-pre-run"
assert_not_contains "$mock_executor_output" "CLEANUP=" "caller-mock-executor-pre-trap"
mark_pass "caller-mock-executor-prohibited"

source "$HARNESS"

VALID_ROOT="$TEST_ROOT/validator/valid"
/bin/mkdir "$VALID_ROOT"
/bin/cat >"$VALID_ROOT/mock-aws" <<'VALID_EXECUTOR'
#!/bin/bash
exit 0
VALID_EXECUTOR
/bin/chmod 700 "$VALID_ROOT/mock-aws"
validate_mock_executor "$VALID_ROOT" "$VALID_ROOT/mock-aws" || fail_test "validator-valid"
mark_pass "validator-valid"

SYMLINK_ROOT="$TEST_ROOT/validator/symlink-root"
/bin/mkdir "$SYMLINK_ROOT"
/bin/ln -s /bin/true "$SYMLINK_ROOT/mock-aws"
if validate_mock_executor "$SYMLINK_ROOT" "$SYMLINK_ROOT/mock-aws"; then fail_test "validator-executor-symlink"; fi
mark_pass "validator-executor-symlink"

REAL_ROOT="$TEST_ROOT/validator/real-root"
/bin/mkdir "$REAL_ROOT"
/bin/cat >"$REAL_ROOT/mock-aws" <<'ROOT_EXECUTOR'
#!/bin/bash
exit 0
ROOT_EXECUTOR
/bin/chmod 700 "$REAL_ROOT/mock-aws"
/bin/ln -s "$REAL_ROOT" "$TEST_ROOT/validator/root-link"
if validate_mock_executor "$TEST_ROOT/validator/root-link" "$TEST_ROOT/validator/root-link/mock-aws"; then fail_test "validator-root-symlink"; fi
mark_pass "validator-root-symlink"

PREFIX_ROOT="$TEST_ROOT/validator/prefix"
PREFIX_EVIL="$TEST_ROOT/validator/prefix-evil"
/bin/mkdir "$PREFIX_ROOT" "$PREFIX_EVIL"
/bin/cat >"$PREFIX_EVIL/mock-aws" <<'PREFIX_EXECUTOR'
#!/bin/bash
exit 0
PREFIX_EXECUTOR
/bin/chmod 700 "$PREFIX_EVIL/mock-aws"
if validate_mock_executor "$PREFIX_ROOT" "$PREFIX_EVIL/mock-aws"; then fail_test "validator-prefix-collision"; fi
mark_pass "validator-prefix-collision"

if validate_mock_executor "relative/root" "relative/root/mock-aws"; then fail_test "validator-relative"; fi
mark_pass "validator-relative"

if validate_mock_executor "$VALID_ROOT" "$VALID_ROOT"; then fail_test "validator-executor-equals-root"; fi
mark_pass "validator-executor-equals-root"

/bin/mkdir "$VALID_ROOT/directory-executor"
if validate_mock_executor "$VALID_ROOT" "$VALID_ROOT/directory-executor"; then fail_test "validator-directory"; fi
mark_pass "validator-directory"

/bin/cp "$VALID_ROOT/mock-aws" "$VALID_ROOT/not-executable"
/bin/chmod 600 "$VALID_ROOT/not-executable"
if validate_mock_executor "$VALID_ROOT" "$VALID_ROOT/not-executable"; then fail_test "validator-not-executable"; fi
mark_pass "validator-not-executable"

if validate_mock_executor "$VALID_ROOT" "$VALID_ROOT/missing-executor"; then fail_test "validator-missing"; fi
mark_pass "validator-missing"

/bin/ln -s "$VALID_ROOT/missing-target" "$VALID_ROOT/dangling-executor"
if validate_mock_executor "$VALID_ROOT" "$VALID_ROOT/dangling-executor"; then fail_test "validator-dangling"; fi
mark_pass "validator-dangling"

[[ ! -s "$SENTINEL_LOG" ]] || fail_test "path-sentinel-called"
mark_pass "path-sentinel-not-called"

if /usr/bin/grep -En '(^|[[:space:];|&()])aws([[:space:]]|$)' "$HARNESS" >/dev/null; then
  fail_test "static-bare-aws"
fi
if /usr/bin/grep -En '(^|[[:space:];|&()])eval([[:space:]]|$)' "$HARNESS" >/dev/null; then
  fail_test "static-eval"
fi
if /usr/bin/grep -En '/(opt/homebrew|usr/local)/bin/aws' "$HARNESS" >/dev/null; then
  fail_test "static-installed-cli-path"
fi
[[ "$(/usr/bin/grep -c '/usr/bin/env -i' "$HARNESS")" == 1 ]] || fail_test "static-env-seam"
mark_pass "static-executor-audit"

printf 'RESULT=success:offline-isolation-matrix:%s\n' "$PASS_COUNT"

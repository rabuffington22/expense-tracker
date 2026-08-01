#!/usr/bin/env bash

set -uo pipefail

readonly SYNTHETIC_ACCOUNT_ID="000000000000"
readonly SYNTHETIC_CURRENT_ROLE="SyntheticCurrentRole"
readonly SYNTHETIC_PROBE_ROLE="ledger-assume-probe-synthetic"

MOCK_ROOT=""
MOCK_BIN=""
CANON_MOCK_ROOT=""
CANON_MOCK_BIN=""
MOCK_STATE_DIR=""
MOCK_HOME_DIR=""
MOCK_CONFIG_FILE=""
MOCK_CREDENTIALS_FILE=""
MOCK_INVOCATION_LOG=""
PROBE_COMPLETE=0
ACCESS_KEY_ID=""
SECRET_ACCESS_KEY=""
SESSION_TOKEN=""
ASSUME_OUTPUT=""

mark() {
  printf '%s\n' "$1"
}

fail() {
  mark "CHECK=failed:$1"
  exit 1
}

validate_mock_executor() {
  local root="$1"
  local candidate="$2"
  local candidate_dir
  local candidate_name
  local canonical_root
  local canonical_dir
  local canonical_candidate

  [[ "$root" == /* && "$candidate" == /* ]] || return 1
  [[ -d "$root" && ! -L "$root" && -O "$root" ]] || return 1
  [[ -f "$candidate" && -x "$candidate" && ! -L "$candidate" && -O "$candidate" ]] || return 1

  candidate_dir="${candidate%/*}"
  candidate_name="${candidate##*/}"
  [[ "$candidate_dir" != "$candidate" && -n "$candidate_name" ]] || return 1

  canonical_root="$(cd "$root" 2>/dev/null && pwd -P)" || return 1
  canonical_dir="$(cd "$candidate_dir" 2>/dev/null && pwd -P)" || return 1
  canonical_candidate="${canonical_dir}/${candidate_name}"

  [[ "$canonical_candidate" != "$canonical_root" ]] || return 1
  [[ "$canonical_candidate" == "$canonical_root/"* ]] || return 1

  CANON_MOCK_ROOT="$canonical_root"
  CANON_MOCK_BIN="$canonical_candidate"
}

install_mock_executor() {
  local destination="$1"

  /bin/cat >"$destination" <<'MOCK_AWS'
#!/bin/bash

set -uo pipefail

: "${PROBE_FIXTURE_ROOT:?}"
: "${PROBE_FIXTURE_STATE:?}"
: "${PROBE_FIXTURE_SCENARIO:?}"
: "${PROBE_FIXTURE_LOG:?}"
: "${AWS_CONFIG_FILE:?}"
: "${AWS_SHARED_CREDENTIALS_FILE:?}"
: "${AWS_EC2_METADATA_DISABLED:?}"

[[ "$PATH" == "$PROBE_FIXTURE_ROOT/bin" ]] || exit 90
[[ "$AWS_CONFIG_FILE" == "$PROBE_FIXTURE_ROOT/config" ]] || exit 90
[[ "$AWS_SHARED_CREDENTIALS_FILE" == "$PROBE_FIXTURE_ROOT/credentials" ]] || exit 90
[[ "$AWS_EC2_METADATA_DISABLED" == "true" ]] || exit 90
[[ -f "$AWS_CONFIG_FILE" && ! -s "$AWS_CONFIG_FILE" ]] || exit 90
[[ -f "$AWS_SHARED_CREDENTIALS_FILE" && ! -s "$AWS_SHARED_CREDENTIALS_FILE" ]] || exit 90
[[ -z "${AWS_ACCESS_KEY_ID+x}" ]] || exit 90
[[ -z "${AWS_SECRET_ACCESS_KEY+x}" ]] || exit 90
[[ -z "${AWS_SESSION_TOKEN+x}" ]] || exit 90
[[ -z "${AWS_PROFILE+x}" ]] || exit 90
[[ -z "${AWS_DEFAULT_PROFILE+x}" ]] || exit 90
[[ -z "${AWS_REGION+x}" ]] || exit 90
[[ -z "${AWS_DEFAULT_REGION+x}" ]] || exit 90
[[ -z "${AWS_ROLE_ARN+x}" ]] || exit 90
[[ -z "${AWS_WEB_IDENTITY_TOKEN_FILE+x}" ]] || exit 90

service="${1-}"
action="${2-}"
[[ -n "$service" && -n "$action" ]] || exit 91
shift 2

query=""
role_name=""
while (( $# > 0 )); do
  case "$1" in
    --query)
      shift
      query="${1-}"
      ;;
    --role-name)
      shift
      role_name="${1-}"
      ;;
  esac
  shift || true
done

printf '%s:%s:%s\n' "$service" "$action" "$query" >>"$PROBE_FIXTURE_LOG"

case "$service:$action" in
  sts:get-caller-identity)
    if [[ "$query" == "Account" ]]; then
      printf '%s\n' "000000000000"
    elif [[ "$query" == "Arn" && -f "$PROBE_FIXTURE_STATE/role-exists" ]]; then
      printf '%s\n' "arn:aws:sts::000000000000:assumed-role/ledger-assume-probe-synthetic/synthetic-probe-session"
    elif [[ "$query" == "Arn" && "$PROBE_FIXTURE_SCENARIO" == "unexpected-caller" ]]; then
      printf '%s\n' "arn:aws:iam::000000000000:user/SyntheticUser"
    elif [[ "$query" == "Arn" ]]; then
      printf '%s\n' "arn:aws:sts::000000000000:assumed-role/SyntheticCurrentRole/synthetic-current-session"
    else
      exit 92
    fi
    ;;
  iam:get-role)
    if [[ "$role_name" == "SyntheticCurrentRole" ]]; then
      printf '%s\n' "arn:aws:iam::000000000000:role/SyntheticCurrentRole"
    elif [[ "$role_name" == "ledger-assume-probe-synthetic" && -f "$PROBE_FIXTURE_STATE/role-exists" ]]; then
      printf '%s\n' "arn:aws:iam::000000000000:role/ledger-assume-probe-synthetic"
    else
      printf '%s\n' "NoSuchEntity" >&2
      exit 254
    fi
    ;;
  iam:create-role)
    : >"$PROBE_FIXTURE_STATE/role-exists"
    printf '%s\n' "ledger-assume-probe-synthetic"
    ;;
  iam:delete-role)
    /bin/rm -f "$PROBE_FIXTURE_STATE/role-exists"
    ;;
  sts:assume-role)
    if [[ "$PROBE_FIXTURE_SCENARIO" == "assume-denied" ]]; then
      exit 255
    fi
    printf '%s\t%s\t%s\n' "SYNTHETIC_ACCESS_KEY" "SYNTHETIC_SECRET" "SYNTHETIC_TOKEN"
    ;;
  *)
    exit 93
    ;;
esac
MOCK_AWS

  /bin/chmod 700 "$destination"
}

run_mock_aws() {
  /usr/bin/env -i \
    PATH="$CANON_MOCK_ROOT/bin" \
    PROBE_FIXTURE_ROOT="$CANON_MOCK_ROOT" \
    PROBE_FIXTURE_STATE="$MOCK_STATE_DIR" \
    PROBE_FIXTURE_SCENARIO="$PROBE_TEST_SCENARIO" \
    PROBE_FIXTURE_LOG="$MOCK_INVOCATION_LOG" \
    AWS_CONFIG_FILE="$MOCK_CONFIG_FILE" \
    AWS_SHARED_CREDENTIALS_FILE="$MOCK_CREDENTIALS_FILE" \
    AWS_EC2_METADATA_DISABLED=true \
    "$CANON_MOCK_BIN" "$@"
}

verify_invocation_sequence() {
  local actual
  local expected

  [[ -f "$MOCK_INVOCATION_LOG" ]] || return 1
  actual="$(<"$MOCK_INVOCATION_LOG")"

  case "$PROBE_TEST_SCENARIO" in
    success)
      expected=$'sts:get-caller-identity:Account\nsts:get-caller-identity:Arn\niam:get-role:Role.Arn\niam:create-role:Role.RoleName\nsts:assume-role:Credentials.[AccessKeyId,SecretAccessKey,SessionToken]\nsts:get-caller-identity:Arn\niam:delete-role:\niam:get-role:'
      ;;
    assume-denied)
      expected=$'sts:get-caller-identity:Account\nsts:get-caller-identity:Arn\niam:get-role:Role.Arn\niam:create-role:Role.RoleName\nsts:assume-role:Credentials.[AccessKeyId,SecretAccessKey,SessionToken]'
      ;;
    unexpected-caller)
      expected=$'sts:get-caller-identity:Account\nsts:get-caller-identity:Arn'
      ;;
    *)
      return 1
      ;;
  esac

  [[ "$actual" == "$expected" ]]
}

cleanup_local_root() {
  local incoming_status=$?
  local cleanup_passed=1

  trap - EXIT
  unset ACCESS_KEY_ID SECRET_ACCESS_KEY SESSION_TOKEN ASSUME_OUTPUT

  if verify_invocation_sequence; then
    mark "CHECK=passed:invocation-sequence"
  else
    mark "CHECK=failed:invocation-sequence"
    cleanup_passed=0
  fi

  if [[ "$MOCK_ROOT" == /tmp/ledger-assumption-probe.* && \
        ( "$CANON_MOCK_ROOT" == /tmp/ledger-assumption-probe.* || "$CANON_MOCK_ROOT" == /private/tmp/ledger-assumption-probe.* ) && \
        -d "$CANON_MOCK_ROOT" && ! -L "$CANON_MOCK_ROOT" && -O "$CANON_MOCK_ROOT" ]]; then
    /bin/rm -f "$MOCK_STATE_DIR/role-exists"
    /bin/rm -f "$MOCK_INVOCATION_LOG" "$MOCK_CONFIG_FILE" "$MOCK_CREDENTIALS_FILE" "$CANON_MOCK_BIN"
    /bin/rmdir "$MOCK_STATE_DIR" 2>/dev/null || cleanup_passed=0
    /bin/rmdir "$MOCK_HOME_DIR" 2>/dev/null || cleanup_passed=0
    /bin/rmdir "$CANON_MOCK_ROOT/bin" 2>/dev/null || cleanup_passed=0
    /bin/rmdir "$CANON_MOCK_ROOT" 2>/dev/null || cleanup_passed=0
  else
    cleanup_passed=0
  fi

  if [[ "$cleanup_passed" == 1 && ! -e "$CANON_MOCK_ROOT" ]]; then
    mark "CLEANUP=passed:offline-root-absent"
  else
    mark "CLEANUP=failed:offline-root-present-or-unknown"
    incoming_status=1
  fi

  if [[ "$incoming_status" == 0 && "$PROBE_COMPLETE" == 1 ]]; then
    mark "RESULT=success"
  else
    mark "RESULT=failed"
  fi

  exit "$incoming_status"
}

main() {
  local account_id=""
  local caller_arn=""
  local current_role_name=""
  local current_role_arn=""
  local probe_role_arn=""
  local probe_caller_arn=""
  local absence_output=""

  [[ "${PROBE_MODE-}" == "offline-test" ]] || fail "offline-mode-required"
  [[ -z "${PROBE_MOCK_ROOT+x}" ]] || fail "caller-root-prohibited"
  [[ -z "${PROBE_MOCK_AWS_BIN+x}" ]] || fail "caller-executor-prohibited"
  [[ -z "${AWS_CLI_BIN+x}" ]] || fail "caller-executor-prohibited"

  PROBE_TEST_SCENARIO="${PROBE_TEST_SCENARIO-success}"
  case "$PROBE_TEST_SCENARIO" in
    success|assume-denied|unexpected-caller) ;;
    *) fail "offline-scenario-invalid" ;;
  esac

  umask 077
  MOCK_ROOT="$(/usr/bin/mktemp -d /tmp/ledger-assumption-probe.XXXXXX)" || fail "mock-root-create"
  [[ "$MOCK_ROOT" == /tmp/ledger-assumption-probe.* && -d "$MOCK_ROOT" && ! -L "$MOCK_ROOT" && -O "$MOCK_ROOT" ]] || fail "mock-root-invalid"

  /bin/mkdir "$MOCK_ROOT/bin" "$MOCK_ROOT/home" "$MOCK_ROOT/state" || fail "mock-layout-create"
  MOCK_BIN="$MOCK_ROOT/bin/mock-aws"
  : >"$MOCK_ROOT/config"
  : >"$MOCK_ROOT/credentials"
  : >"$MOCK_ROOT/invocations"
  install_mock_executor "$MOCK_BIN" || fail "mock-executor-install"
  validate_mock_executor "$MOCK_ROOT" "$MOCK_BIN" || fail "mock-boundary-invalid"

  MOCK_STATE_DIR="$CANON_MOCK_ROOT/state"
  MOCK_HOME_DIR="$CANON_MOCK_ROOT/home"
  MOCK_CONFIG_FILE="$CANON_MOCK_ROOT/config"
  MOCK_CREDENTIALS_FILE="$CANON_MOCK_ROOT/credentials"
  MOCK_INVOCATION_LOG="$CANON_MOCK_ROOT/invocations"
  readonly MOCK_ROOT MOCK_BIN CANON_MOCK_ROOT CANON_MOCK_BIN
  readonly MOCK_STATE_DIR MOCK_HOME_DIR MOCK_CONFIG_FILE MOCK_CREDENTIALS_FILE MOCK_INVOCATION_LOG

  trap cleanup_local_root EXIT
  mark "RUN=started:offline-test"
  mark "CHECK=passed:harness-owned-root"

  account_id="$(run_mock_aws sts get-caller-identity --query Account --output text 2>/dev/null)" || fail "caller-session-unavailable"
  mark "CHECK=passed:mock-environment"
  caller_arn="$(run_mock_aws sts get-caller-identity --query Arn --output text 2>/dev/null)" || fail "caller-shape-unavailable"

  [[ "$account_id" == "$SYNTHETIC_ACCOUNT_ID" ]] || fail "caller-account-shape"
  if [[ "$caller_arn" =~ ^arn:aws:sts::${SYNTHETIC_ACCOUNT_ID}:assumed-role/([^/]+)/[^/]+$ ]]; then
    current_role_name="${BASH_REMATCH[1]}"
  else
    fail "caller-not-assumed-role"
  fi
  [[ "$current_role_name" == "$SYNTHETIC_CURRENT_ROLE" ]] || fail "caller-role-mismatch"
  mark "ALLOW=passed:caller-session-shape"

  current_role_arn="$(run_mock_aws iam get-role --role-name "$current_role_name" --query Role.Arn --output text 2>/dev/null)" || fail "current-role-read-denied-or-missing"
  [[ "$current_role_arn" == "arn:aws:iam::${SYNTHETIC_ACCOUNT_ID}:role/${SYNTHETIC_CURRENT_ROLE}" ]] || fail "current-role-account-or-shape"
  mark "ALLOW=passed:current-role-read"

  probe_role_arn="arn:aws:iam::${SYNTHETIC_ACCOUNT_ID}:role/${SYNTHETIC_PROBE_ROLE}"
  run_mock_aws iam create-role --role-name "$SYNTHETIC_PROBE_ROLE" --assume-role-policy-document synthetic-trust --query Role.RoleName --output text >/dev/null 2>&1 || fail "probe-role-create-denied-or-failed"
  mark "ALLOW=passed:empty-probe-role-created"
  mark "WAIT=skipped:offline-test"

  ASSUME_OUTPUT="$(run_mock_aws sts assume-role --role-arn "$probe_role_arn" --role-session-name synthetic-probe-session --duration-seconds 900 --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --output text 2>/dev/null)" || fail "current-session-assume-denied-or-failed"
  read -r ACCESS_KEY_ID SECRET_ACCESS_KEY SESSION_TOKEN <<<"$ASSUME_OUTPUT"
  unset ASSUME_OUTPUT
  [[ "$ACCESS_KEY_ID" == "SYNTHETIC_ACCESS_KEY" && "$SECRET_ACCESS_KEY" == "SYNTHETIC_SECRET" && "$SESSION_TOKEN" == "SYNTHETIC_TOKEN" ]] || fail "temporary-credential-shape"
  mark "ALLOW=passed:probe-role-assumed"

  probe_caller_arn="$(run_mock_aws sts get-caller-identity --query Arn --output text 2>/dev/null)" || fail "probe-caller-shape-unavailable"
  unset ACCESS_KEY_ID SECRET_ACCESS_KEY SESSION_TOKEN
  [[ "$probe_caller_arn" == "arn:aws:sts::${SYNTHETIC_ACCOUNT_ID}:assumed-role/${SYNTHETIC_PROBE_ROLE}/synthetic-probe-session" ]] || fail "probe-caller-shape-mismatch"
  mark "ALLOW=passed:probe-caller-shape"

  run_mock_aws iam delete-role --role-name "$SYNTHETIC_PROBE_ROLE" >/dev/null 2>&1 || fail "probe-role-delete-failed"
  if absence_output="$(run_mock_aws iam get-role --role-name "$SYNTHETIC_PROBE_ROLE" 2>&1)"; then
    fail "probe-role-still-present"
  fi
  [[ "$absence_output" == *NoSuchEntity* ]] || fail "probe-role-absence-unknown"
  mark "ALLOW=passed:probe-role-absent"

  PROBE_COMPLETE=1
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi

#!/usr/bin/env bash

set -uo pipefail
set +o xtrace

PROBE_COMPLETE=0
CREATE_ATTEMPTED=0
ROLE_CREATED=0
API_CALLS=0
AWS_CLI_BIN=""
AWS_CLI_CANDIDATE=""
ACCOUNT_ID=""
CALLER_ARN=""
CALLER_RESOURCE=""
CURRENT_ROLE_NAME=""
CURRENT_ROLE_ARN=""
CURRENT_ROLE_RESOURCE=""
PROBE_ROLE_NAME=""
PROBE_ROLE_ARN=""
PROBE_SESSION_NAME="ledger-one-role-probe"
TRUST_DOCUMENT=""
ASSUME_OUTPUT=""
ACCESS_KEY_ID=""
SECRET_ACCESS_KEY=""
SESSION_TOKEN=""
PROBE_CALLER_ARN=""
PROBE_ENTROPY=""

mark() {
  printf '%s\n' "$1"
}

fail() {
  mark "CHECK=failed:$1"
  exit 1
}

cleanup_probe_role() {
  local incoming_status=$?
  local cleanup_passed=1
  local delete_status=0
  local absence_status=0
  local absence_error=""

  trap - EXIT HUP INT TERM
  unset ASSUME_OUTPUT ACCESS_KEY_ID SECRET_ACCESS_KEY SESSION_TOKEN TRUST_DOCUMENT

  if [[ "$CREATE_ATTEMPTED" == 1 ]]; then
    API_CALLS=$((API_CALLS + 1))
    "$AWS_CLI_BIN" iam delete-role \
      --role-name "$PROBE_ROLE_NAME" \
      >/dev/null 2>&1
    delete_status=$?

    API_CALLS=$((API_CALLS + 1))
    absence_error="$("$AWS_CLI_BIN" iam get-role \
      --role-name "$PROBE_ROLE_NAME" \
      --query Role.Arn \
      --output text 2>&1 >/dev/null)"
    absence_status=$?

    if [[ "$absence_status" != 0 && "$absence_error" == *"NoSuchEntity"* ]]; then
      mark "CLEANUP=passed:probe-role-absent"
    else
      mark "CLEANUP=failed:probe-role-present-or-unknown"
      cleanup_passed=0
    fi
    unset absence_error

    if [[ "$ROLE_CREATED" == 1 && "$delete_status" != 0 ]]; then
      incoming_status=1
    fi
  else
    mark "CLEANUP=passed:nothing-created"
  fi

  mark "ACTIONS_USED=$API_CALLS"
  if [[ "$incoming_status" == 0 && "$cleanup_passed" == 1 && "$PROBE_COMPLETE" == 1 ]]; then
    mark "RESULT=success"
    exit 0
  fi

  mark "RESULT=failed"
  exit 1
}

main() {
  [[ "${PROBE_MODE-}" == "protected-one-role" ]] || fail "protected-mode-required"

  export AWS_MAX_ATTEMPTS=1
  export AWS_RETRY_MODE=standard

  [[ "$(type -t aws 2>/dev/null)" == "file" ]] || fail "aws-cli-unavailable"
  AWS_CLI_CANDIDATE="$(command -v aws 2>/dev/null)" || fail "aws-cli-unavailable"
  [[ "$AWS_CLI_CANDIDATE" == /* ]] || fail "aws-cli-boundary"
  AWS_CLI_BIN="$(readlink -f -- "$AWS_CLI_CANDIDATE" 2>/dev/null)" || fail "aws-cli-canonicalization"
  [[ "$AWS_CLI_BIN" == /* && -f "$AWS_CLI_BIN" && -x "$AWS_CLI_BIN" && ! -L "$AWS_CLI_BIN" ]] || fail "aws-cli-boundary"
  unset AWS_CLI_CANDIDATE
  readonly AWS_CLI_BIN

  umask 077
  trap cleanup_probe_role EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM

  mark "RUN=started:protected-one-role"

  API_CALLS=$((API_CALLS + 1))
  ACCOUNT_ID="$("$AWS_CLI_BIN" sts get-caller-identity \
    --query Account --output text 2>/dev/null)" || fail "caller-account-unavailable"
  [[ "$ACCOUNT_ID" =~ ^[0-9]{12}$ ]] || fail "caller-account-shape"

  API_CALLS=$((API_CALLS + 1))
  CALLER_ARN="$("$AWS_CLI_BIN" sts get-caller-identity \
    --query Arn --output text 2>/dev/null)" || fail "caller-arn-unavailable"
  CALLER_RESOURCE="${CALLER_ARN#arn:aws:sts::${ACCOUNT_ID}:assumed-role/}"
  [[ "$CALLER_RESOURCE" != "$CALLER_ARN" && "$CALLER_RESOURCE" == */* ]] || fail "caller-not-assumed-role"

  CURRENT_ROLE_NAME="${CALLER_RESOURCE%%/*}"
  [[ "$CURRENT_ROLE_NAME" =~ ^[A-Za-z0-9_+=,.@-]{1,64}$ ]] || fail "caller-role-name-shape"
  [[ -n "${CALLER_RESOURCE#*/}" && "${CALLER_RESOURCE#*/}" != */* ]] || fail "caller-session-name-shape"
  mark "ALLOW=passed:caller-session-shape"

  API_CALLS=$((API_CALLS + 1))
  CURRENT_ROLE_ARN="$("$AWS_CLI_BIN" iam get-role \
    --role-name "$CURRENT_ROLE_NAME" \
    --query Role.Arn --output text 2>/dev/null)" || fail "current-role-read-denied-or-missing"
  [[ "$CURRENT_ROLE_ARN" == "arn:aws:iam::${ACCOUNT_ID}:role/"* ]] || fail "current-role-account-or-partition"
  CURRENT_ROLE_RESOURCE="${CURRENT_ROLE_ARN#arn:aws:iam::${ACCOUNT_ID}:role/}"
  [[ "$CURRENT_ROLE_RESOURCE" =~ ^[A-Za-z0-9_+=,.@/-]+$ ]] || fail "current-role-path-charset"
  [[ -n "$CURRENT_ROLE_RESOURCE" && "${CURRENT_ROLE_RESOURCE##*/}" == "$CURRENT_ROLE_NAME" ]] || fail "current-role-name-or-path"
  mark "ALLOW=passed:current-role-read"

  [[ -r /proc/sys/kernel/random/uuid ]] || fail "probe-entropy-unavailable"
  PROBE_ENTROPY="$(</proc/sys/kernel/random/uuid)"
  PROBE_ENTROPY="${PROBE_ENTROPY//-/}"
  [[ "$PROBE_ENTROPY" =~ ^[0-9a-f]{32}$ ]] || fail "probe-entropy-shape"
  PROBE_ROLE_NAME="ledger-one-role-probe-${PROBE_ENTROPY}"
  unset PROBE_ENTROPY
  [[ "$PROBE_ROLE_NAME" =~ ^[A-Za-z0-9_+=,.@-]{1,64}$ ]] || fail "probe-role-name-shape"
  PROBE_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${PROBE_ROLE_NAME}"
  TRUST_DOCUMENT="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"${CURRENT_ROLE_ARN}\"},\"Action\":\"sts:AssumeRole\"}]}"

  CREATE_ATTEMPTED=1
  API_CALLS=$((API_CALLS + 1))
  "$AWS_CLI_BIN" iam create-role \
    --role-name "$PROBE_ROLE_NAME" \
    --assume-role-policy-document "$TRUST_DOCUMENT" \
    --query Role.RoleName \
    --output text \
    >/dev/null 2>&1 || fail "probe-role-create-denied-or-failed"
  ROLE_CREATED=1
  unset TRUST_DOCUMENT
  mark "ALLOW=passed:empty-probe-role-created"

  mark "WAIT=started:iam-propagation"
  sleep 20
  mark "WAIT=finished:iam-propagation"

  API_CALLS=$((API_CALLS + 1))
  ASSUME_OUTPUT="$("$AWS_CLI_BIN" sts assume-role \
    --role-arn "$PROBE_ROLE_ARN" \
    --role-session-name "$PROBE_SESSION_NAME" \
    --duration-seconds 900 \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text 2>/dev/null)" || fail "current-session-assume-denied-or-failed"
  read -r ACCESS_KEY_ID SECRET_ACCESS_KEY SESSION_TOKEN <<<"$ASSUME_OUTPUT"
  unset ASSUME_OUTPUT
  [[ -n "$ACCESS_KEY_ID" && -n "$SECRET_ACCESS_KEY" && -n "$SESSION_TOKEN" ]] || fail "temporary-credential-shape"
  mark "ALLOW=passed:probe-role-assumed"

  API_CALLS=$((API_CALLS + 1))
  PROBE_CALLER_ARN="$(AWS_ACCESS_KEY_ID="$ACCESS_KEY_ID" \
    AWS_SECRET_ACCESS_KEY="$SECRET_ACCESS_KEY" \
    AWS_SESSION_TOKEN="$SESSION_TOKEN" \
    "$AWS_CLI_BIN" sts get-caller-identity \
    --query Arn --output text 2>/dev/null)" || fail "probe-caller-shape-unavailable"
  unset ACCESS_KEY_ID SECRET_ACCESS_KEY SESSION_TOKEN
  [[ "$PROBE_CALLER_ARN" == "arn:aws:sts::${ACCOUNT_ID}:assumed-role/${PROBE_ROLE_NAME}/${PROBE_SESSION_NAME}" ]] || fail "probe-caller-shape-mismatch"
  mark "ALLOW=passed:probe-caller-shape"

  unset ACCOUNT_ID CALLER_ARN CALLER_RESOURCE CURRENT_ROLE_NAME CURRENT_ROLE_ARN
  unset CURRENT_ROLE_RESOURCE PROBE_ROLE_ARN PROBE_CALLER_ARN
  PROBE_COMPLETE=1
}

main "$@"

#!/usr/bin/env bash

set -uo pipefail
set +o xtrace

PROBE_COMPLETE=0
API_CALLS=0
AWS_CLI_BIN=""
AWS_CLI_CANDIDATE=""
CALLER_ARN=""
IDENTITY_CLASS=""

mark() {
  printf '%s\n' "$1"
}

finish() {
  local incoming_status=$?

  trap - EXIT HUP INT TERM
  unset CALLER_ARN IDENTITY_CLASS AWS_CLI_CANDIDATE
  mark "CLEANUP=passed:nothing-created"
  mark "ACTIONS_USED=$API_CALLS"

  if [[ "$incoming_status" == 0 && "$PROBE_COMPLETE" == 1 ]]; then
    mark "RESULT=success"
    exit 0
  fi

  mark "RESULT=failed"
  exit 1
}

fail() {
  mark "CHECK=failed:$1"
  exit 1
}

trap finish EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

main() {
  [[ "${PROBE_MODE-}" == "caller-classification" ]] || fail "classification-mode-required"

  export AWS_MAX_ATTEMPTS=1
  export AWS_RETRY_MODE=standard

  [[ "$(type -t aws 2>/dev/null)" == "file" ]] || fail "aws-cli-unavailable"
  AWS_CLI_CANDIDATE="$(command -v aws 2>/dev/null)" || fail "aws-cli-unavailable"
  [[ "$AWS_CLI_CANDIDATE" == /* ]] || fail "aws-cli-boundary"
  AWS_CLI_BIN="$(readlink -f -- "$AWS_CLI_CANDIDATE" 2>/dev/null)" || fail "aws-cli-canonicalization"
  [[ "$AWS_CLI_BIN" == /* && -f "$AWS_CLI_BIN" && -x "$AWS_CLI_BIN" && ! -L "$AWS_CLI_BIN" ]] || fail "aws-cli-boundary"
  unset AWS_CLI_CANDIDATE
  readonly AWS_CLI_BIN

  mark "RUN=started:caller-classification"

  API_CALLS=$((API_CALLS + 1))
  CALLER_ARN="$("$AWS_CLI_BIN" sts get-caller-identity \
    --query Arn --output text 2>/dev/null)" || fail "caller-read-failed"

  if [[ "$CALLER_ARN" =~ ^arn:aws:iam::[0-9]{12}:user/[A-Za-z0-9_+=,.@/-]+$ ]]; then
    IDENTITY_CLASS="iam-user"
  elif [[ "$CALLER_ARN" =~ ^arn:aws:sts::[0-9]{12}:federated-user/[A-Za-z0-9_+=,.@-]+$ ]]; then
    IDENTITY_CLASS="federated-user"
  elif [[ "$CALLER_ARN" =~ ^arn:aws:iam::[0-9]{12}:root$ ]]; then
    IDENTITY_CLASS="root"
  elif [[ "$CALLER_ARN" =~ ^arn:aws:sts::[0-9]{12}:assumed-role/[A-Za-z0-9_+=,.@/-]+/[A-Za-z0-9_+=,.@-]+$ ]]; then
    IDENTITY_CLASS="assumed-role"
  else
    IDENTITY_CLASS="unsupported"
  fi

  unset CALLER_ARN
  mark "IDENTITY_CLASS=$IDENTITY_CLASS"
  unset IDENTITY_CLASS
  PROBE_COMPLETE=1
}

main "$@"

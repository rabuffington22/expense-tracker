#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TARGET="$REPO_ROOT/command-center/s3-caller-identity-classification-cloudshell.sh"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/ledger-caller-classifier.XXXXXX")"
MOCK_BIN="$TEST_ROOT/bin"
MOCK_COUNTER="$TEST_ROOT/calls"

cleanup() {
  local status=$?
  trap - EXIT HUP INT TERM
  rm -rf -- "$TEST_ROOT"
  exit "$status"
}

trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

mkdir -p "$MOCK_BIN"

cat >"$MOCK_BIN/aws" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == 6 ]]
[[ "$1" == "sts" ]]
[[ "$2" == "get-caller-identity" ]]
[[ "$3" == "--query" ]]
[[ "$4" == "Arn" ]]
[[ "$5" == "--output" ]]
[[ "$6" == "text" ]]

count=0
if [[ -f "$MOCK_COUNTER" ]]; then
  count="$(<"$MOCK_COUNTER")"
fi
printf '%s\n' "$((count + 1))" >"$MOCK_COUNTER"

case "${CLASSIFIER_SCENARIO-}" in
  iam-user)
    printf '%s\n' 'arn:aws:iam::000000000000:user/synthetic-user'
    ;;
  federated-user)
    printf '%s\n' 'arn:aws:sts::000000000000:federated-user/synthetic-user'
    ;;
  root)
    printf '%s\n' 'arn:aws:iam::000000000000:root'
    ;;
  assumed-role)
    printf '%s\n' 'arn:aws:sts::000000000000:assumed-role/synthetic-role/synthetic-session'
    ;;
  unsupported)
    printf '%s\n' 'arn:aws:iam::000000000000:group/synthetic-group'
    ;;
  sentinel)
    printf '%s\n%s\n' 'arn:aws:iam::000000000000:user/synthetic-user' 'RAW_OUTPUT_SENTINEL'
    ;;
  provider-failure)
    printf '%s\n' 'RAW_ERROR_SENTINEL' >&2
    exit 42
    ;;
  *)
    exit 43
    ;;
esac
MOCK
chmod 700 "$MOCK_BIN/aws"

run_case() {
  local scenario="$1"
  local expected_class="$2"
  local expected_result="$3"
  local output=""
  local status=0

  : >"$MOCK_COUNTER"
  output="$(env -i \
    PATH="$MOCK_BIN:/usr/bin:/bin" \
    PROBE_MODE=caller-classification \
    CLASSIFIER_SCENARIO="$scenario" \
    MOCK_COUNTER="$MOCK_COUNTER" \
    /bin/bash "$TARGET" 2>&1)" || status=$?

  if [[ "$expected_result" == "success" ]]; then
    [[ "$status" == 0 ]]
    grep -Fqx "IDENTITY_CLASS=$expected_class" <<<"$output"
    [[ "$output" == *"RESULT=success"* ]]
  else
    [[ "$status" != 0 ]]
    [[ "$output" == *"CHECK=failed:caller-read-failed"* ]]
    [[ "$output" == *"RESULT=failed"* ]]
  fi

  [[ "$output" == *"RUN=started:caller-classification"* ]]
  [[ "$output" == *"CLEANUP=passed:nothing-created"* ]]
  [[ "$output" == *"ACTIONS_USED=1"* ]]
  [[ "$output" != *"arn:aws:"* ]]
  [[ "$output" != *"000000000000"* ]]
  [[ "$output" != *"synthetic-user"* ]]
  [[ "$output" != *"synthetic-role"* ]]
  [[ "$output" != *"RAW_OUTPUT_SENTINEL"* ]]
  [[ "$output" != *"RAW_ERROR_SENTINEL"* ]]
  [[ "$(<"$MOCK_COUNTER")" == 1 ]]

  printf 'CASE=passed:%s\n' "$scenario"
}

run_case iam-user iam-user success
run_case federated-user federated-user success
run_case root root success
run_case assumed-role assumed-role success
run_case unsupported unsupported success
run_case sentinel unsupported success
run_case provider-failure none failed

[[ "$(grep -F -c 'API_CALLS=$((API_CALLS + 1))' "$TARGET")" == 1 ]]
[[ "$(grep -F -c 'sts get-caller-identity' "$TARGET")" == 1 ]]
! grep -Eiq '(^|[[:space:]])(for|while|until|eval|source)([[:space:]]|$)' "$TARGET"
! grep -Eiq '(^|[[:space:]])iam([[:space:]]|$)' "$TARGET"
! grep -Eiq '(^|[[:space:]])s3([[:space:]]|$)' "$TARGET"

printf 'RESULT=success:caller-classification-matrix:7\n'

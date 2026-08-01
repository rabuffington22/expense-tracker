# Second Opinion — 7C-S3-FR Caller Identity Classification

Date: 2026-07-31

Reviewer route: direct Claude CLI

Model and effort: `claude-fable-5`, `max`

Why this route: the target is a sanitized text-only AWS shell packet with a
small exact action envelope. An independent high-effort security review can
audit the shell semantics, identifier boundary, and one-call guarantee before
protected execution.

## Question

Is the exact packet below safe and sufficiently fail-closed for one run under
confirmed work block 7C-S3-FR, or does it require a material change before any
AWS action?

## Confirmed Boundary

- Task 3.2b read-only diagnostic slice only.
- Exactly one `sts:GetCallerIdentity --query Arn --output text` call site and
  one wire attempt.
- The caller ARN may exist only in shell memory and must never be printed or
  retained.
- Allowed output is limited to fixed run/check/cleanup/result markers, exact
  action count, and one generic class: `iam-user`, `federated-user`, `root`,
  `assumed-role`, or `unsupported`.
- Every class stops. No branch may perform another AWS action.
- No IAM read or mutation, policy/permission/boundary inspection,
  `sts:AssumeRole`, S3, retry, correction, resource creation, Task 3.2c, Git,
  or successor action.
- The CloudShell packet is piped to Bash without persisting a provider-side
  file.
- Material review change stops for Ryan. Non-material defense-in-depth
  clarifications may be adopted only if they add no action, scope, output,
  retained identifier, or success criterion.

Canonical proposal:
`command-center/s3-caller-identity-classification-proposal.md`

## Exact Packet Under Review

```bash
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
```

## Local Evidence

- Bash syntax passes for the packet and test.
- Seven offline fake-CLI cases pass: IAM user, federated user, root, assumed
  role, unsupported ARN, multiline raw-output sentinel, and provider failure.
- Every case observes exactly one mock call.
- Output assertions reject ARN text, the synthetic account value, synthetic
  user/role names, raw stdout sentinel, and raw stderr sentinel.
- Static audit finds exactly one API counter increment and one
  `sts get-caller-identity` site, with no loop, `eval`, `source`, IAM command,
  or S3 command.
- Runway OS JSON, refresh, currentness, health, exact active-block invariants,
  whitespace, and zero staging pass before review.

## Required Response

Return:

1. Classification: `ACCEPT`,
   `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS`, `MATERIAL_CHANGE_REQUIRED`, or
   `REJECT`.
2. Confidence percentage.
3. Exact one-call and retry audit.
4. Shell parsing and identity-classification audit, including malformed,
   multiline, partition, path, and session-name edge cases.
5. Identifier, credential, stdout/stderr, xtrace, environment, and trap audit.
6. Whether any failure or signal path can print provider data, run a second
   AWS command, or self-certify success incorrectly.
7. Recommended changes, labeled material or non-material.
8. Missing information that would materially change the recommendation.

Do not propose broader AWS diagnostics or a successor implementation. Review
only whether this exact one-read classifier honors the confirmed boundary.

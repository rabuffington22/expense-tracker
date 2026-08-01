# Second Opinion — 7C-S3-E Offline Harness Isolation

Date: 2026-07-31

Reviewer route: Claude CLI direct run

Model and effort: `claude-fable-5`, `max`

Tool boundary: no tools, safe mode, plan permission, no session persistence.
All required sanitized context is included below.

## Specific Question

Does the confirmed 7C-S3-E design provide a sufficiently fail-closed offline
validation boundary after a prior shell-function mock unexpectedly fell
through to the installed AWS CLI? Identify any material safety flaw before
implementation.

## Context

Task 3.2a is an offline-only prerequisite. The later protected one-role AWS
probe and final synthetic S3 proof are separate planned tasks and are not
authorized.

The prior local validation attempted to export zsh functions named `aws` and
`sleep` into a child Bash process. Function export did not provide the intended
isolation, so the child resolved the installed AWS CLI and made two read-only
caller-identity requests before an unexpected-caller guard stopped it. No IAM
or S3 mutation occurred. No correction or retry followed.

## Confirmed Design

The block proposes to:

1. keep live execution disabled or absent;
2. require an explicit mode rather than defaulting to live;
3. in offline-test mode require an explicit absolute executor path;
4. require the executor to be executable and physically contained inside a
   fresh per-run disposable mock root;
5. use real disposable executable fixtures, never shell-function mocks;
6. clear inherited AWS credential and profile variables in offline tests;
7. route every AWS-shaped operation through one injected executor;
8. statically reject any bare `aws` execution path;
9. test success, assumption denial, cleanup, missing mode, missing executor,
   outside-root executor, normal-PATH shadowing, and unexpected caller shape;
10. run no installed AWS CLI, network, browser, Chrome, CloudShell, credential,
    IAM, STS, or S3 action.

The intended implementation may leave a future live mode entirely absent. A
later separately confirmed block would be required to enable or run it.

## Current Harness Risk Shape

The current Bash harness has `set -uo pipefail`, installs an EXIT cleanup trap,
and calls a bare `aws` command for every operation. Representative current
call sites are:

```bash
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text 2>/dev/null)"
CALLER_ARN="$(aws sts get-caller-identity --query Arn --output text 2>/dev/null)"
CURRENT_ROLE_ARN="$(aws iam get-role --role-name "$CURRENT_ROLE_NAME" --query Role.Arn --output text 2>/dev/null)"
aws iam create-role --role-name "$PROBE_ROLE_NAME" --assume-role-policy-document "$TRUST_POLICY"
ASSUME_OUTPUT="$(aws sts assume-role --role-arn "$PROBE_ROLE_ARN" ...)"
AWS_ACCESS_KEY_ID="$ACCESS_KEY_ID" AWS_SECRET_ACCESS_KEY="$SECRET_ACCESS_KEY" AWS_SESSION_TOKEN="$SESSION_TOKEN" aws sts get-caller-identity ...
aws iam delete-role --role-name "$PROBE_ROLE_NAME"
aws iam get-role --role-name "$PROBE_ROLE_NAME"
```

It also calls bare `sleep`, generates a role name from
`/proc/sys/kernel/random/uuid`, stores temporary credentials only in shell
variables, unsets them during cleanup, and emits sanitized status markers.

## Proposed Implementation Direction

Replace every bare AWS call with one function whose only executable is the
validated `AWS_CLI_BIN` absolute path. Before installing the EXIT trap or
printing `RUN=started`, validate:

- `PROBE_MODE` equals exactly `offline-test`;
- `PROBE_MOCK_ROOT` and `AWS_CLI_BIN` are absolute;
- both resolve canonically without symlink escape;
- the executor is a regular executable file strictly below the canonical mock
  root, not the root itself;
- no live mode exists in this block.

The self-test creates the mock root, writes executable fixtures, sets a hostile
`PATH` containing a sentinel `aws`, clears AWS-related inherited variables,
and passes the exact mock executor path. It proves the sentinel is never
called. Negative tests pass outside-root and missing values and verify failure
before either mock or sentinel invocation. Cleanup tests use fixture-managed
state only.

The implementation should prefer portable local mechanisms available on
macOS and Bash 3.2. If canonical-path validation cannot be both portable and
unambiguous, the block must stop rather than weaken containment.

## Locked Exclusions

- installed AWS CLI invocation, even read-only;
- network, credentials, profiles, config, cache, Chrome, CloudShell;
- AWS account, IAM, STS, S3, role, trust, bucket, or retention action;
- production data, Fly, recovery activation, publication, Git action;
- Tasks 3.2b, 3.2c, 3.3, or any successor.

## Review Questions

1. Is requiring an explicit absolute executor inside a canonical disposable
   mock root enough to prevent normal-PATH fall-through and symlink escape?
2. Must the executor and root receive additional ownership, type, or mode
   checks?
3. Should environment clearing occur in the harness as well as the test
   launcher?
4. Is an EXIT cleanup trap safe before validation completes, or should it be
   installed only after all offline-boundary checks pass?
5. Are the proposed negative paths sufficient to prove fail-closed behavior?
6. Is there any safer equally probative offline design?

## Requested Response Format

Return:

1. Classification: `ACCEPT`, `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS`, or
   `MATERIAL_CHANGE_REQUIRED`.
2. Direct critique of the isolation boundary.
3. Required changes separated into material and non-material.
4. Any safer alternative and its tradeoff.
5. Recommended test matrix additions.
6. Confidence from 0-100%.
7. Missing information that would materially change the result.

Do not propose running AWS, inspecting credentials, broadening to the live
probe, or implementing the final S3 capability proof.

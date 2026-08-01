# 7C-S3-F Result — Protected One-Role Assumption Probe

Date: 2026-07-31

Status: stopped fail-closed.

## Result

The Fable-reviewed packet ran once in the exact full Chrome CloudShell account
authorized by 7C-S3-F. The first caller account read succeeded, but the caller
ARN did not have the required STS assumed-role session shape. The packet
stopped at `caller-not-assumed-role` before the existing-role read or any
mutation.

Generic execution result:

- `RUN=started:protected-one-role`
- `CHECK=failed:caller-not-assumed-role`
- `CLEANUP=passed:nothing-created`
- `ACTIONS_USED=2`
- `RESULT=failed`

## Exact Boundary

Exactly two read-only `sts:GetCallerIdentity` calls ran. No `iam:GetRole`,
`iam:CreateRole`, trust-policy write, `sts:AssumeRole`, temporary credential,
temporary caller check, `iam:DeleteRole`, S3 request, existing-resource
mutation, or successor action occurred. Cleanup correctly required no provider
action because nothing was created.

No account ID, ARN, role name, credential, or raw provider error is retained in
the repository artifact or report. The transient Chrome CloudShell task was
finalized after the generic result was read.

## Disposition

7C-S3-F is consumed and stopped without correction or retry. Task 3.2b remains
current and decision-needed under Ryan. Task 3.2c remains planned and blocked.
Any alternate identity route, additional AWS read, different trust design,
retry, S3 proof, or recovery implementation requires a new proposal and Ryan
confirmation.

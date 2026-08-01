# Second Opinion — 7C-S3-F Protected One-Role Assumption Probe

Date: 2026-07-31

Reviewer route: Claude CLI direct run

Model and effort: `claude-fable-5`, `max`

## Specific Question

Is the exact CloudShell packet in
`command-center/s3-one-role-assumption-cloudshell.sh` safe and sufficiently
fail-closed to run once under confirmed work block 7C-S3-F, or does it require
a material change before any AWS action?

This is a review of the executable packet and its shell/AWS safety, not a
request to redesign the recovery architecture or broaden the task.

## Read These Files

1. `AGENTS.md`
2. `command-center/operating-rules.md`
3. `command-center/s3-one-role-assumption-probe-proposal.md`
4. `command-center/s3-one-role-assumption-cloudshell.sh`
5. `command-center/logs/second-opinion/2026-07-31-7c-s3-d-assumption-probe-review.md`
6. `command-center/logs/2026-07-31-offline-harness-isolation-7c-s3-e.md`

## Confirmed Boundary

Task 3.2b (`P7-T32B`) only. The normal path may make exactly eight AWS API
calls: two current-caller identity reads, one exact current-role read, one
empty disposable-role creation, one assumption attempt, one temporary-caller
identity read, one guarded role deletion, and one absence check. There is no
retry.

The exact current IAM role record is the only existing AWS resource read. Only
the new random empty disposable role may be mutated, and it must be absent at
the end. Task 3.2c and every S3 request are excluded. Existing IAM mutation,
permission changes, users, access keys, permanent credentials, raw identifier
output, production data, Fly, recovery implementation, publication, Git, and
successor actions are excluded.

The packet will run only in the AWS account already established by Ryan in the
full Chrome CloudShell page. Ryan performs any sign-in or MFA directly. The
packet must emit only generic markers and keep account, role, ARN, and
temporary credential values only in shell/process memory.

## Current Local Evidence

- `bash -n` passes for the CloudShell packet.
- The maintained offline isolation matrix passes all 24 cases.
- Static audit finds eight counter-incremented AWS call sites, one
  `AssumeRole`, one `CreateRole`, one `DeleteRole`, and no S3 command.
- The only bare `aws` tokens are the `type -t` and `command -v` executable
  resolution checks; all API calls use one canonical absolute executable.
- Nothing has been run against AWS under 7C-S3-F.

## Pressure-Test These Risks

1. Bash trap and exit semantics on every pre-create, create-ambiguous,
   post-create, signal, normal, deletion-failure, and absence-check path.
2. Whether cleanup performs exactly one deletion and one absence check after a
   create attempt, without becoming a retry or exceeding the action envelope.
3. Whether a failed `CreateRole` could leave a role and whether the packet
   handles that safely.
4. Whether the `NoSuchEntity` absence classification can mistake a permission,
   transport, or parsing failure for cleanup success.
5. Whether current assumed-role ARN parsing and path-qualified `GetRole` ARN
   matching are correct and fail closed.
6. Whether direct same-account trust to the stable current role ARN is
   correctly expressed without adding an identity permission or existing-role
   mutation.
7. Whether any shell expansion, subprocess, CLI error, command echo, process
   argument, or signal path can expose or retain identifiers or temporary
   credentials beyond the confirmed in-memory boundary.
8. Whether canonical CLI resolution is reliable in AWS CloudShell without
   accepting a function, alias, relative path, or non-executable target.
9. Whether the packet can make an uncounted AWS call, retry automatically, or
   reach S3.
10. Whether the claimed success criteria are strong enough to justify moving
    Task 3.2b to done while leaving Task 3.2c separately gated.

## Requested Response Format

Return:

1. `CLASSIFICATION`: one of `ACCEPT`,
   `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS`, `MATERIAL_CHANGE_REQUIRED`, or
   `REJECT`.
2. `CONFIDENCE`: integer percent.
3. `CRITICAL_FINDINGS`: numbered; say `None` if none.
4. `NON_MATERIAL_CLARIFICATIONS`: numbered; say `None` if none.
5. `ACTION_ENVELOPE_AUDIT`: exact normal and failure-path call counts.
6. `CLEANUP_AUDIT`: whether every create-attempt path proves absence safely.
7. `IDENTIFIER_AND_CREDENTIAL_AUDIT`: any exposure or retention risk.
8. `RECOMMENDATION`: proceed once, revise before AWS, or stop.
9. `MISSING_INFORMATION`: only facts that could materially change the result.

Do not modify files, run the packet, invoke AWS, inspect credentials, or ask
for sensitive identifiers. Critique only the sanitized repository artifacts.

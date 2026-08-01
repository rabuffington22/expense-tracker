# 7C-S3-F Confirmation — Protected One-Role Assumption Probe

Date: 2026-07-31

Ryan confirmed `7C-S3-F` at 9:28 PM CDT for Phase 7 Task 3.2b (`P7-T32B`)
only.

Codex Desktop must first write and verify the confirmed block, create a
sanitized repo-backed CloudShell command packet, and route that exact packet
through Claude CLI `claude-fable-5` at `max` effort. A material review change
stops before AWS for Ryan's confirmation.

On acceptance, the block authorizes structured Chrome control of the already
established full AWS CloudShell session, with a direct Ryan sign-in or MFA
handoff if needed. It authorizes only two current-caller identity reads, one
read of the exact current IAM role record, creation of one random empty
disposable role trusted only to the current stable role, one fixed 20-second
wait, one `sts:AssumeRole` attempt, one temporary-caller identity check, one
guarded deletion, and one absence check. The normal path is capped at eight
AWS API calls and has no retry.

No S3 action, existing-resource mutation, permission change, IAM user, access
key, permanent credential, printed or retained identifier, production data,
Fly, workflow, recovery implementation, activation, publication, Git action,
Task 3.2c, Task 3.3, or successor is authorized. Stop without correction or
retry on account ambiguity, identity or role mismatch, denial, identifier
exposure, cleanup uncertainty, scope expansion, material review change, or
failed verification.

## Second-Opinion Intake

Fable 5 max returned `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS` at 90%
confidence. The accepted packet has eight counted AWS call sites, no scripted
retry, no S3 command, exact role/account validation, in-memory credentials,
one guarded deletion, and an absence check that accepts only `NoSuchEntity`.

Codex adopted the non-material defenses before AWS: `set +o xtrace`,
`AWS_MAX_ATTEMPTS=1`, `AWS_RETRY_MODE=standard`, full safe-path charset
validation, and a 128-bit kernel UUID suffix. No API call, existing-resource
read or mutation, retry, output, S3 action, or success criterion was added.

## Final Result

The exact packet ran once in the authorized full Chrome CloudShell account and
stopped fail-closed because the current caller did not have the required STS
assumed-role session shape. Exactly two read-only `sts:GetCallerIdentity`
calls ran. Cleanup passed with nothing created and the result was failed.

No `iam:GetRole`, role creation, trust write, `sts:AssumeRole`, temporary
credential, deletion, S3 request, existing-resource mutation, correction,
retry, Task 3.2c, or successor occurred. 7C-S3-F is consumed and stopped.

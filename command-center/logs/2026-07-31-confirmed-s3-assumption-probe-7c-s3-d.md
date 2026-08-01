# Work Block 7C-S3-D — Confirmed Exact Caller Role And One-Role Assumption Probe

Date: 2026-07-31

## Confirmation

Ryan confirmed `7C-S3-D` at 5:10 PM CDT for Phase 7 Task 3.2 (`P7-T32`)
only.

## Authorized Sequence

Codex Desktop must first record and verify the block, then send the repo-backed
proposal to Claude CLI `claude-fable-5` at `max` effort for a sanitized second
opinion. A material review change stops for Ryan's confirmation.

If the review accepts the exact scope or adds only non-material defensive
clarification, Codex may derive the current role name from the signed-in
CloudShell caller session, make one read-only `iam:GetRole` call for that exact
current role, keep only its stable ARN in memory without printing or retaining
it, create one random empty disposable IAM role trusted only to that stable
role, attempt one `sts:AssumeRole`, use the temporary session only for caller
shape confirmation, delete the disposable role, verify absence, and stop.

## Exclusions And Stop

No S3 action, four-role capability matrix, existing IAM mutation, permission
or permission-set change, boundary or trust-policy change, access key, IAM
user, permanent credential, production data, Fly, workflow/scheduler,
recovery implementation, activation, publication, Git action, Task 3.3, or
successor is authorized.

Stop without correction or retry on a material review change, role-name
ambiguity, `GetRole` denial or mismatch, unexpected account or role,
create/trust/assume/caller-shape denial, identifier exposure, existing-resource
mutation need, cleanup uncertainty, scope expansion, unexpected cost or
protected data, or failed verification.

## Second-Opinion Intake

Fable 5 max returned `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS` at 90%
confidence. The review accepted the exact diagnostic and required a fixed
20-second wait before the single assumption attempt, mandatory cleanup after
every post-creation stop, and negative-result wording limited to the current
session. No material change occurred and the optional second attempt was not
adopted. The block may proceed.

## Result

The block stopped fail-closed at 5:24 PM CDT during local harness validation.
The intended AWS mock did not remain isolated and the child script resolved
to a real local AWS CLI identity. Its caller shape was not an assumed role, so
the harness stopped after exactly two read-only `sts:GetCallerIdentity` calls.

No `iam:GetRole`, role creation, trust-policy write, `sts:AssumeRole`, S3
request, existing-resource mutation, identifier output, or retained
identifier occurred. Cleanup reported the probe role absent because nothing
was created. The authorized Chrome CloudShell probe never ran. No correction,
retry, final S3 proof, Task 3.3 work, Git action, or successor followed. Task
3.2 remains current and decision-needed with Ryan owning the next decision.

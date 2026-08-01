# Confirmed 7C-S3-F — Protected One-Role Assumption Probe

Date: 2026-07-31

Status: stopped fail-closed after two read-only caller-identity calls.

## Parent Phase And Task

Parent phase: Phase 7 — Operational Safeguards Activation And Currentness
Proof.

Included: Task 3.2b (`P7-T32B`) — Protected One-Role Assumption Probe — only.

Excluded: Task 3.2c (`P7-T32C`) final synthetic S3 capability proof; Tasks
3.3-3.4 and 4-7.

## Purpose

Determine whether the AWS role currently signed into the established Chrome
CloudShell account can assume one directly trusting empty disposable IAM role.
This is an IAM/STS diagnostic only. It does not create or call any S3 resource.

## Authorized Sequence

1. Write and verify this confirmed block in Runway OS.
2. Create one sanitized repo-backed CloudShell command packet.
3. Route the exact packet through Claude CLI `claude-fable-5` at `max` effort
   with read-only tools and no session persistence.
4. Stop for Ryan if the review requires a material change.
5. Otherwise use structured Chrome control on the existing full AWS
   CloudShell page. If authentication expired, pause while Ryan completes
   sign-in or MFA directly and reports only that the session is ready.
6. In the signed-in CloudShell session, keep identifiers only in shell memory:
   read the current caller account and session ARN, derive the current role
   name, read only that exact role record's stable ARN, and verify same-account
   shape without printing or retaining any identifier.
7. Create one randomly named disposable IAM role with no permissions policy
   and a trust policy naming only the current stable role ARN.
8. Wait a fixed 20 seconds, make exactly one `sts:AssumeRole` attempt, and use
   the temporary credentials only for one caller-shape confirmation.
9. Through one guarded cleanup path, delete the disposable role once and verify
   it is absent. Reconcile Runway OS and stop.

The normal path is capped at eight AWS API calls: two current-caller identity
reads, one exact current-role read, one role creation, one assumption attempt,
one temporary-caller identity read, one role deletion, and one absence check.
There is no retry. A failure path uses the same single cleanup deletion and
absence check after a create attempt.

## Existing-Resource Boundary

The exact current IAM role record is the only existing AWS resource read. The
CLI query returns only its stable ARN to the in-memory packet, but the
`GetRole` API response includes the role record. No existing resource may be
changed. Only the newly generated empty disposable role may be created and
deleted.

## Exclusions

- no S3 API, bucket, object, versioning, Object Lock, retention, upload,
  restore, or four-role capability matrix;
- no mutation of the current role, permissions, trust policy, permission set,
  boundary, IAM user, access key, or existing AWS resource;
- no permanent credential, printed identifier, retained account ID, ARN, role
  name, access key, secret, session token, or raw provider error;
- no production data, Fly, workflow, scheduler, recovery implementation,
  activation, publication, Git staging/commit/push/PR/merge, Task 3.2c,
  Task 3.3, or successor action.

## Owner Agent And Route

Autonomous owner: Codex Desktop. Ryan owns authentication and MFA.

Recommended agent: Codex Desktop with Claude CLI `claude-fable-5` at `max`
as the pre-execution reviewer.

Runner path: current Codex task for repository stewardship and structured
Chrome control for the existing full CloudShell page. If structured Chrome
cannot operate the exact verified tab, the UI-control fallback may change only
the control mechanism after re-establishing the same task-owned Chrome window,
account, command packet, authority, and remaining action count. Otherwise
stop.

Codex owns review intake, the exact API envelope, sanitized execution,
cleanup, verification, Runway OS currency, and the final disposition.

## Expected Files And Surfaces

- this confirmed proposal;
- one sanitized non-secret CloudShell command packet under `command-center/`;
- one second-opinion handoff and sanitized intake log;
- one confirmation/result log plus Runway OS source and generated dashboard;
- the existing signed-in Chrome AWS Console and full CloudShell page.

No product source, offline harness, database, financial-data, production, Fly,
S3, or publication surface is included.

## Stop Conditions

Stop without correction or retry if:

- the exact Fable 5 max route is unavailable or requires a material change;
- Chrome shows no session, the wrong or ambiguous AWS account, or cannot
  establish the exact full CloudShell surface after Ryan's direct sign-in;
- current caller shape, current-role name, same-account equality, or exact
  current-role lookup is ambiguous, denied, or inconsistent;
- role creation, the single assumption attempt, temporary caller-shape check,
  deletion, or absence verification fails;
- an identifier, credential, raw error, or sensitive value would be exposed or
  retained;
- an existing-resource mutation, S3 action, additional read, retry, broader
  permission, protected-data access, or scope expansion becomes necessary;
- the exact cleanup result or Runway OS verification cannot be established.

Any post-create stop still runs the one guarded cleanup path. Cleanup is not a
diagnostic retry and does not authorize another assumption attempt.

## Questions And Defaults

Blocking questions: none.

Non-blocking defaults:

- use the AWS account already established in Chrome for this recovery proof;
- use the full CloudShell page, not the compact drawer;
- Ryan completes passwords and MFA directly without sharing a code;
- keep the current account, role, disposable role name, ARN, and temporary
  credentials only in shell memory;
- emit only generic markers such as `RUN=started`, `ALLOW=passed:<class>`,
  `CLEANUP=passed:probe-role-absent`, and `RESULT=success|failed`;
- use one fixed 20-second wait and no retry;
- keep repository changes local, unstaged, uncommitted, and unpublished.

Ryan decision points: this confirmation; direct sign-in or MFA if the existing
session is not ready; and a fresh decision only after a material review change
or stopped result. No successor starts automatically.

## Verification And Closeout

Require an accepted sanitized Fable disposition; the maintained 24-case
offline isolation matrix still passing; Bash syntax and static command-packet
audit; the exact normal-path API sequence and eight-call ceiling; one current
role read; one empty disposable role with no attached or inline permissions;
one assumption attempt; temporary caller shape; exact deletion and absence;
generic output only; no S3 command; valid JSON; exactly one current task;
dashboard refresh/currentness/health; rendered inspection; whitespace;
preserved user changes; and zero staging.

On success, mark 7C-S3-F and Task 3.2b done, keep Task 3.2 active, make Task
3.2c current and decision-needed under Ryan, and activate no successor. On a
stop, mark 7C-S3-F stopped, keep Task 3.2b current and decision-needed, and
authorize no correction, retry, S3 action, or successor.

## Report Back

Return the Fable disposition, generic probe result, exact cleanup result, AWS
API action count, confirmation that no raw identifiers or S3 action occurred,
changed paths, checks, worktree/staging state, and the separate next decision.

Suggested next block after a complete pass: separately propose `7C-S3-G —
Final Synthetic S3 Capability Proof` for Task 3.2c only. It does not start
automatically.

## Plain-English Confirmation

Ryan confirmed that Codex will first record this exact block and have Fable 5
max review the executable CloudShell packet. If accepted, Codex may run one
empty-role assumption test in the AWS account already established in Chrome,
delete that role, verify it is gone, and stop. Ryan handles any sign-in or MFA.
No S3, existing-role change, retry, recovery implementation, Git publication,
or successor is authorized.

## Second-Opinion Result

Fable 5 max returned `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS` at 90%
confidence. It accepted the eight-site action envelope, fail-closed role and
account parsing, direct same-account trust, temporary-credential handling,
generic output, single guarded deletion, conjunctive absence proof, and zero
S3 path.

Before AWS, Codex adopted its defense-in-depth clarifications: disable inherited
xtrace, pin AWS CLI wire attempts to one, validate the full stable-role path
charset before JSON interpolation, and use a 128-bit kernel UUID suffix for
the disposable role. These changes add no API call, retry, existing-resource
read or mutation, output, credential, S3 action, or success criterion. The
block may proceed after the local checks pass.

## Final Result

The packet ran once in the exact authorized full Chrome CloudShell account and
stopped at `caller-not-assumed-role`. Exactly two read-only
`sts:GetCallerIdentity` calls ran. No existing-role read, role creation, trust
write, assumption attempt, temporary credential, deletion, S3 request,
existing-resource mutation, or successor action occurred. Cleanup passed with
nothing created and the generic result was `RESULT=failed`.

7C-S3-F is consumed and stopped without correction or retry. Task 3.2b remains
current and decision-needed under Ryan; Task 3.2c remains planned and blocked.

# Confirmed 7C-S3-FR — Caller Identity Classification And Route Decision

Date: 2026-07-31

Status: done with a generic root-principal result.

## Parent Phase And Task

Parent phase: Phase 7 — Operational Safeguards Activation And Currentness
Proof.

Included: Task 3.2b (`P7-T32B`) — Protected One-Role Assumption Probe — as a
read-only diagnostic slice only.

Excluded: Task 3.2c (`P7-T32C`) final synthetic S3 capability proof; Tasks
3.3-3.4 and 4-7.

## Purpose

Classify the AWS principal currently backing the established full Chrome
CloudShell session without retaining its identifier. The consumed 7C-S3-F
packet proved only that the caller was not an STS assumed-role session; it did
not establish whether the caller is an IAM user, STS federated user, root,
changed assumed-role session, or unsupported identity.

The result selects the next architecture discussion. It does not authorize an
assumption test or any AWS mutation.

## Authorized Sequence

1. Write and verify this confirmed block in Runway OS.
2. Create one sanitized repo-backed classifier packet and maintained offline
   fixture test.
3. Route the exact packet through Claude CLI `claude-fable-5` at `max` effort
   with no reviewer tools or session persistence.
4. Stop for Ryan if the review requires a material change.
5. Otherwise use structured Chrome control on the exact full CloudShell page.
   If authentication expired, Ryan completes sign-in or MFA directly and
   reports only that the session is ready.
6. Make exactly one read-only `sts:GetCallerIdentity --query Arn --output
   text` call with AWS CLI wire attempts pinned to one.
7. Keep the returned ARN only in shell memory, classify it as `iam-user`,
   `federated-user`, `root`, `assumed-role`, or `unsupported`, unset it, and
   emit only generic markers.
8. Reconcile Runway OS and stop. Every class requires a separate next
   proposal before any further AWS action.

## Action And Data Envelope

- one AWS API call site and one wire attempt only;
- `sts:GetCallerIdentity` is the only AWS action;
- the ARN is held only in shell memory and is never printed or retained;
- generic output only: run marker, identity class, nothing-created cleanup,
  action count, and success or failed result;
- no provider file is written in CloudShell;
- nothing is created, changed, or deleted.

## Exclusions

- no `iam:GetUser`, `iam:GetRole`, policy, boundary, permission, account,
  organization, CloudTrail, or additional identity read;
- no `iam:CreateRole`, trust-policy write, `sts:AssumeRole`, temporary
  credential, deletion, or other mutation;
- no S3 request, bucket, object, retention, upload, restore, or capability
  matrix;
- no printed or retained account ID, ARN, user name, role name, credential,
  or raw provider error;
- no production data, Fly, workflow, scheduler, recovery implementation,
  activation, publication, Git staging/commit/push/PR/merge, Task 3.2c,
  successor, correction, or retry.

## Owner Agent And Route

Autonomous owner: Codex Desktop. Ryan owns authentication and MFA.

Recommended agent: Codex Desktop with direct Claude CLI
`claude-fable-5` at `max` as the pre-execution reviewer.

Runner path: current Codex task for repository stewardship and structured
Chrome control of the exact full CloudShell page. UI fallback may change only
the control mechanism after re-establishing the same task-owned Chrome window,
account, packet, authority, and one remaining action. Otherwise stop.

Codex owns the packet, reviewer intake, one-call envelope, sanitized result,
Runway OS currency, and final disposition.

## Expected Files And Surfaces

- this confirmed proposal;
- one sanitized classifier packet under `command-center/`;
- one maintained offline classifier test under `scripts/`;
- one second-opinion handoff and sanitized intake log;
- one confirmation/result log plus Runway OS source and generated dashboard;
- the existing full Chrome CloudShell page.

No product source, database, financial data, production, Fly, IAM mutation,
S3, or publication surface is included.

## Stop Conditions

Stop without correction or retry if:

- the exact Fable 5 max route is unavailable or requires a material change;
- Chrome shows no session, the wrong or ambiguous AWS account, or cannot
  establish the exact full CloudShell surface after Ryan's direct sign-in;
- more than one AWS call or any IAM, S3, mutation, or additional read becomes
  necessary;
- the caller ARN cannot be classified without printing, persisting, or
  retaining it;
- the result is malformed, the provider call fails, or raw provider output
  could escape;
- the packet emits a credential, identifier, or raw error;
- a retry, policy inspection, broader diagnostic, user change, scope
  expansion, or unsupported action becomes necessary;
- Runway OS or preservation verification fails.

## Questions And Defaults

Blocking questions: none.

Non-blocking defaults:

- use the AWS account already established in full Chrome CloudShell;
- Ryan completes passwords and MFA directly without sharing a code;
- use one `sts:GetCallerIdentity` call with `AWS_MAX_ATTEMPTS=1` and no loop;
- retain the ARN only in shell memory and unset it immediately after
  classification;
- emit generic markers only;
- stop after every identity class, including `iam-user` and `assumed-role`;
- treat an unexpected `assumed-role` result as changed session state, not
  authority to rerun 7C-S3-F;
- keep repository changes local, unstaged, uncommitted, and unpublished.

Ryan decision points: this confirmation; direct sign-in or MFA if needed; and
a fresh class-specific direction choice after the generic result. No successor
starts automatically.

## Verification And Closeout

Require an accepted sanitized Fable disposition; Bash syntax; offline fixtures
for all five supported classes plus malformed, provider-failure, and raw-output
sentinel cases; static proof of one AWS call site and no loop, IAM, or S3
command; one live read only; generic output; nothing-created cleanup; valid
JSON; exactly one current task and active block; dashboard refresh,
currentness, health, and rendered inspection; whitespace; preserved changes;
and zero staging.

On safe classification, mark 7C-S3-FR done, keep Task 3.2b current and
decision-needed under Ryan, record the generic class, and activate no
successor. On an ambiguous or failed classification, mark 7C-S3-FR stopped,
keep Task 3.2b current and decision-needed, and authorize no correction or
retry.

## Report Back

Return the Fable disposition, generic identity class, exact action count,
nothing-created result, confirmation that no identifier, IAM mutation, or S3
action occurred, class-specific route recommendation, changed paths, checks,
and worktree/staging state.

Suggested next block: a separate class-specific architecture review only. An
IAM user result may support an exact-user trust feasibility review; a
federated-user result requires a federated-session or role-based sign-in
review; root or unsupported identity recommends stopping until account access
is redesigned; an assumed-role result requires a fresh proposal because the
session changed. None starts automatically.

## Plain-English Confirmation

Ryan confirmed that Codex will first record this exact block and build a
sanitized one-call classifier. Fable 5 max reviews the executable packet before
AWS. On acceptance, Codex may classify the current CloudShell identity without
retaining its ARN, make no IAM or S3 change, and stop with a route
recommendation. No assumption test, retry, resource creation, Task 3.2c, Git,
or successor is authorized.

## Second-Opinion Result

Fable 5 max returned `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS` at 95%
confidence and cleared the exact packet to run as-is. It accepted the one-call
and one-wire-attempt envelope, anchored classification expressions, fixed
generic output, in-memory ARN handling, failure and signal behavior, and
nothing-created cleanup.

Its optional `AWS_PAGER=""` suggestion was not adopted because the reviewer
cleared the packet without it and preserving byte-for-byte packet identity is
stronger for this block. Codex independently verified the fenced review packet
and executable file are identical, then reran syntax, all seven offline cases,
and the static action-envelope audit successfully. The block may proceed once
through the exact full Chrome CloudShell surface.

## Final Result

The exact accepted packet ran once in the authorized full Chrome CloudShell
account and returned `IDENTITY_CLASS=root`. This is the AWS account root
principal class, not local container root. Exactly one read-only
`sts:GetCallerIdentity` call ran. Cleanup passed with nothing created and the
result was successful.

No IAM read or mutation, assumption attempt, S3 request, identifier retention,
production-data access, correction, retry, Task 3.2c, Git, or successor action
occurred. The Chrome task was closed.

7C-S3-FR is done. Task 3.2b remains current and decision-needed under Ryan;
Task 3.2c remains planned and blocked. Codex recommends no root-trusting probe
and no S3 continuation under the current root session. The next choice is to
stop the S3 path or separately plan and confirm non-root administrative access
before revisiting Task 3.2b.

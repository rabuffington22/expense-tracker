# Proposed 7C-S3-D — Exact Caller Role And One-Role Assumption Probe

Date: 2026-07-31

Status: stopped fail-closed at 5:24 PM CDT on 2026-07-31.

## Purpose

Resolve only the IAM role-assumption blocker before another S3 proof is
considered. This block does not create an S3 bucket or run the four-role
capability matrix.

The current CloudShell caller is an assumed-role session. Its session ARN
contains the role name but can omit the IAM role path. AWS `GetRole` returns
the specified role's exact ARN and path. AWS also documents that a same-account
role trust policy can grant `AssumeRole` directly to a named IAM role principal
without an additional identity policy:

- <https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetRole.html>
- <https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html>

## Proposed Scope

Task 3.2 (`P7-T32`) only:

1. run a repo-backed Fable 5 max second opinion on this exact diagnostic
   contract before any AWS action;
2. if the review materially changes scope, stop for Ryan's confirmation;
3. otherwise derive the current role name from the signed-in caller session;
4. make one read-only `iam:GetRole` call for that exact current role and keep
   only its exact stable ARN in memory without printing or retaining it;
5. create one randomly named disposable IAM role with no permissions policy
   and a trust policy naming only that exact stable current-role ARN;
6. make one `sts:AssumeRole` request for the empty disposable role and use its
   temporary session only for `sts:GetCallerIdentity` shape confirmation;
7. delete the disposable role and verify it is absent; then stop and reconcile
   Runway OS.

The `GetRole` API reads the current role record, which includes path, ARN, and
trust-policy metadata, even though the CLI query will return only the ARN to
the harness. This is the single existing-resource read that Ryan would be
authorizing. No existing resource is changed.

## Exclusions

- no S3 bucket, object, versioning, Object Lock, retention, or S3 request;
- no four-role uploader, observer, restore-reader, or retention-extender test;
- no existing IAM role, permission, permission set, boundary, trust policy, or
  identity mutation;
- no access keys, IAM users, permanent credentials, or retained identifiers;
- no production data, Fly, workflow, scheduler, recovery implementation,
  activation, publication, Git action, Task 3.3, or successor work.

## Stop Conditions

Stop without correction or retry if the current role name cannot be derived
from the session ARN; `GetRole` is denied or returns an unexpected account or
role; Fable 5 max materially changes the proposal; creation, direct trust,
assumption, caller-shape confirmation, or exact cleanup fails; an identifier
would be printed or retained; an existing resource mutation becomes necessary;
or scope, cost, protected-data, or verification boundaries change.

## Verification And Closeout

Require sanitized second-opinion disposition; one exact current-role read;
one empty disposable role; successful direct same-account assumption; no
permissions policy; temporary credentials only; exact deletion and absence;
no S3 or production action; valid JSON; current dashboard; command-center
health; rendered inspection; whitespace; preserved user changes; and zero
staging.

On pass, mark 7C-S3-D done but keep Task 3.2 current. Separately propose
`7C-S3-F — Final Synthetic S3 Capability Proof`; do not start it. On stop,
leave Task 3.2 decision-needed with no further AWS action authorized.

## Result

Fable 5 max returned `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS` at 90%
confidence. During local harness validation, the intended mock did not remain
isolated and the child script resolved to a real local AWS CLI identity. The
caller was not an assumed-role session, so the fail-closed guard stopped after
exactly two read-only `sts:GetCallerIdentity` calls.

No `iam:GetRole`, role creation, trust-policy write, `sts:AssumeRole`, S3
request, mutation, identifier output, or retained identifier occurred.
Cleanup reported the probe role absent because nothing was created. The
authorized Chrome CloudShell probe never ran, and the block performed no
correction, retry, final S3 proof, Task 3.3 work, Git action, or successor.

## Plain-English Confirmation

Confirming 7C-S3-D lets Codex first have Fable 5 max review this plan, then—if
the review does not materially change it—read only the exact address of the
AWS role you are currently using, create one empty temporary role, verify that
the current role can step into it, and delete it. It does not create or touch
anything in S3 and does not start the backup implementation.

# Proposed 7C-S3-R — Temporary-Role Trust Repair And S3 Proof Retry

Date: 2026-07-30

Status: stopped cleanly at 4:50 PM CDT on 2026-07-31.

Confirmation does not waive the principal-shape preflight. If the stable IAM
role cannot be derived from the current session without inspecting an existing
IAM resource, 7C-S3-R stops before creating the bucket or roles.

## Why This Is Separate

7C-S3 stopped safely after the signed-in AWS identity created the disposable
bucket and four temporary roles but could not call `sts:AssumeRole` on the
uploader role. The harness then verified exact cleanup. A retry would change
the role trust/assumption contract and consume a second provider mutation, so
it requires a new work block.

AWS documents that a role trust policy selects who may assume the role and
that failed role assumption must be checked against both the trusted principal
and the caller's `sts:AssumeRole` permission. AWS also recommends IAM role
principals over role-session principals where possible:

- <https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_roles.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html>

## Proposed Scope

Task 3.2 (`P7-T32`) only:

1. use the signed-in CloudShell session to derive the caller's stable IAM role
   principal in memory without printing or retaining its ARN;
2. change only the four disposable roles' trust policy from account delegation
   to that exact caller role principal;
3. create one new random disposable `us-east-2` S3 Object Lock bucket and four
   new random temporary roles;
4. run the unchanged synthetic uploader, observer, restore-reader, and
   retention-extender allow/deny proof;
5. verify exact cleanup of every object version/delete marker, inline policy,
   role, and bucket;
6. stop and reconcile Runway OS.

No policy is added to or changed on Ryan's existing AWS identity. No existing
role, permission set, bucket, policy, or object is opened or modified. If
direct stable-principal trust still cannot establish all four temporary
sessions, the retry stops without another trust variation.

## Exclusions And Stop Conditions

The 7C-S3 exclusions remain unchanged: no production data, recovery
implementation, Fly, scheduler/workflow, compliance mode, deployment,
publication, Git action, existing AWS resource mutation, or Task 3.3/successor.

Stop on principal-shape ambiguity, any need to inspect or modify an existing
IAM resource, any required permission grant to the current identity,
unexpected cost, a required denial succeeding, cleanup uncertainty, or failed
verification. No privilege expansion or third attempt follows automatically.

## Plain-English Confirmation

Confirming 7C-S3-R would authorize one new disposable S3 proof attempt using
the current signed-in role as the exact trust principal for four temporary
roles. It would not authorize changing the permissions on your existing AWS
account or role. Everything created by the retry must be deleted, and the
block stops before recovery implementation or Task 3.3.

## Result

The signed-in CloudShell caller passed the session checks, but the exact stable
IAM role ARN was unavailable from the session environment and caller identity.
The preflight stopped before any AWS resource creation because discovering the
missing role would have required inspection of an existing IAM resource.
Cleanup verification passed with nothing created. No third attempt or
successor work ran.

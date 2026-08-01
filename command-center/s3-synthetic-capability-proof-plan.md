# 7C-S3 Synthetic S3 Capability Proof Plan

Date: 2026-07-30

Status: confirmed and active for Phase 7 Task 3.2 (`P7-T32`) only.

## Purpose

Replace the unstarted Backblaze provider stage of 7C with one exact,
disposable Amazon S3 capability proof. The completed local trigger,
two-recipient encryption, complete-set manifest, partial-set failure, logical
14/8/12 retention, and lock-floor work from Task 3.1 remain accepted evidence.

## Authorized AWS Surface

- Region: `us-east-2` (Ohio).
- One randomly named, private, disposable S3 bucket.
- Bucket versioning and S3 Object Lock enabled at creation.
- Governance-mode retention only, with a short temporary proof interval.
- Four randomly named temporary IAM roles with inline policies: uploader,
  independent observer, restore reader, and retention extender.
- STS temporary role sessions only; no IAM users or permanent access keys.
- One synthetic encrypted-looking payload and one synthetic manifest under one
  random proof prefix.
- Exact deletion of every proof object version and delete marker, all four
  inline policies and roles, and the disposable bucket.

## Required Capability Matrix

| Role | Required allow | Required denials |
| --- | --- | --- |
| Uploader | Upload the synthetic objects | list, read, delete, retention mutation, legal-hold mutation, bucket Object Lock configuration |
| Observer | List the exact proof prefix and inspect version/retention metadata | payload read, upload, delete, retention mutation |
| Restore reader | Observer metadata plus read one exact object version for hash parity | upload, delete, retention mutation |
| Retention extender | Read and extend governance retention on one exact version | payload read, upload, delete, retention shortening without bypass |

The current signed-in AWS identity may create, assume, inspect, and clean up
only these randomly named disposable resources. It is not itself part of the
least-privilege application model.

## Execution And Evidence Rules

The proof runs from the already authenticated AWS CloudShell session so no
credential value is copied into the repository, terminal transcript, or chat.
The harness prints only sanitized pass, denial, wait, cleanup, and final-result
markers. It must not print the AWS account identifier, bucket name, role names,
ARNs, object version identifiers, temporary credentials, or payload contents.

Success requires bucket and role creation, all required allows, all required
denials, exact-version restore hash parity, successful retention extension,
denied shortening without bypass, expiry of the short governance interval, and
verified absence of all disposable objects, policies, roles, and the bucket.

## Exclusions And Stop Conditions

Excluded: existing S3 buckets or IAM resources; production databases, backups,
uploads, WAL/SHM, financial rows, Fly, workflow or scheduler changes, recovery
implementation, activation, compliance-mode retention, deployment,
publication, commit, push, PR, merge, and Tasks 3.3 through 7.

Stop without broadening scope on account ambiguity, an unexpected billing or
purchase prompt, insufficient permission, a required denial succeeding,
cleanup uncertainty, any need to inspect an existing bucket or IAM resource,
any production/protected-data need, or failed local/Runway OS verification.

## Closeout Boundary

On a complete pass, close Task 3.2 and 7C-S3, retain the cleaned synthetic proof
as sanitized evidence, and separately propose Task 3.3. Task 3.3 does not start
automatically. On any stop, retain Task 3.2 as current and report the exact
sanitized boundary without retrying or weakening the model.

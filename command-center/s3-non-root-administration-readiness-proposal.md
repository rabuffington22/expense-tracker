# Confirmed 7C-S3-FP — Non-Root AWS Administration Readiness And Route Packet

Date: 2026-08-01

Status: second-opinion before any AWS inspection.

## Parent Phase And Task

Parent phase: Phase 7 — Operational Safeguards Activation And Currentness
Proof.

Included: Task 3.2b (`P7-T32B`) — Protected One-Role Assumption Probe — as a
non-root administration prerequisite and read-only readiness slice only.

Excluded: Task 3.2c (`P7-T32C`) final synthetic S3 capability proof; Tasks
3.3-3.4 and 4-7.

## Purpose

Determine which non-root human-administration route is compatible with the
AWS account's existing Organizations and IAM Identity Center shape. Return one
sanitized route packet and the exact Ryan decisions required before any setup.

The prior one-call classifier established that the current AWS API caller is
the account root principal. This block does not retry an assumption probe or
establish a new identity. It resolves only whether the account appears to be
standalone, the management account of an AWS Organization, or a member
account; whether IAM Identity Center appears enabled; and which separately
confirmable bootstrap path follows.

## Authorized Sequence

1. Write and verify this confirmed block in Runway OS.
2. Create one sanitized repo-backed second-opinion packet containing this
   exact proposal and the three-surface read-only inspection contract.
3. Route the exact packet through direct Claude CLI `claude-fable-5` at `max`
   effort with no reviewer tools or session persistence.
4. Stop for Ryan if the review requires a material scope, safety, data, or
   verification change.
5. Otherwise use structured Chrome control on the exact authenticated AWS
   account and read only these console summary surfaces:
   - the AWS Organizations overview or landing state;
   - the IAM Identity Center overview or landing state;
   - one IAM account-summary surface only if the first two surfaces cannot
     distinguish whether a non-root administration route may already exist.
6. Do not open a named user, group, role, policy, permission set, account
   assignment, billing page, or resource detail. Do not activate any control
   whose result would create, enable, disable, update, delete, assign, invite,
   or send anything.
7. Classify only generic state and retain no identifier:
   - account: `standalone`, `management`, `member`, or `ambiguous`;
   - Identity Center: `enabled`, `disabled`, or `ambiguous`;
   - instance: `organization`, `account`, `none`, or `ambiguous`;
   - route: `existing-administration`, `organization-instance-bootstrap`,
     `management-account-handoff`, `limited-fallback`, or `stop`.
8. Produce the exact separately confirmable setup proposal, reconcile Runway
   OS, and stop. No setup or successor begins.

## Read And Data Envelope

- at most three AWS console summary surfaces and no AWS CLI or API call;
- navigation and read-only inspection only, with no mutation control used;
- no raw account ID, email, name, ARN, portal URL, user, group, role, policy,
  permission set, assignment, billing detail, or screenshot retained;
- only the fixed generic classes above may enter tracked artifacts or chat;
- if a page cannot be classified without retaining an identifier or entering
  a named identity or policy surface, stop as `ambiguous`;
- nothing is created, enabled, disabled, changed, deleted, assigned, invited,
  sent, or retried.

## Route Decision Rules

- An organization instance is the preferred IAM Identity Center candidate
  only when the account is standalone or the Organizations management account,
  account access is supported, and Ryan separately accepts the organization
  and Region consequences.
- An IAM Identity Center account instance is not treated as a route to AWS
  account administration because it does not provide AWS account access.
- A member account routes to the Organizations management-account
  administrator rather than attempting account-instance account access.
- If an existing non-root administrative route is visible only at the generic
  summary level, recommend a separate validation block instead of creating a
  duplicate identity.
- A limited IAM-user bootstrap may be described only as a fallback option; it
  is not selected or executed in this block and must avoid root or user access
  keys.
- `us-east-2` is only the initial Region candidate because it matches the
  accepted synthetic S3 proof plan. The block may recommend or reject it, but
  may not choose, enable, or make it permanent.

## Exclusions

- no AWS Organizations create, invite, enable-all-features, trusted-access,
  policy, account, delegated-administrator, or billing change;
- no IAM Identity Center enable, disable, delete, replicate, identity-source,
  directory, user, group, permission-set, assignment, application, invitation,
  email, portal, or Region change;
- no IAM user, role, policy, boundary, password, MFA, access-key, service-linked
  role, trust, permission, or named-identity inspection or mutation;
- no CloudShell, AWS CLI, AWS API, STS, S3, bucket, object, retention, upload,
  restore, assumption, or capability matrix;
- no production data, Fly, workflow, scheduler, recovery implementation,
  activation, publication, Git staging/commit/push/PR/merge, Task 3.2c,
  successor, correction, or retry.

## Owner Agent And Route

Autonomous owner: Codex Desktop. Ryan owns authentication, MFA, organization,
Region, identity-source, identity-detail, permission, and setup decisions.

Recommended agent: Codex Desktop with direct Claude CLI
`claude-fable-5` at `max` as the pre-inspection reviewer.

Runner path: current Codex task for repository stewardship and structured
Chrome control of the exact authenticated AWS account. If structured Chrome
cannot re-establish or safely read the exact task-owned account and surfaces,
stop; Computer Use is not automatically authorized by this block.

Codex owns the packet, reviewer intake, three-surface ceiling, generic result,
route recommendation, Runway OS currency, and final disposition.

## Expected Files And Surfaces

- this confirmed proposal;
- one second-opinion handoff and sanitized intake log;
- one confirmation and one generic result log;
- Runway OS source files and generated dashboard;
- AWS Organizations and IAM Identity Center summary surfaces, plus at most one
  IAM account-summary surface if strictly needed.

No product source, database, financial data, AWS resource detail, production,
Fly, CloudShell, S3, identity mutation, or publication surface is included.

## Stop Conditions

Stop without correction or retry if:

- the exact Fable 5 max route is unavailable or requires a material change;
- Chrome has no authenticated task-owned AWS session or shows a wrong or
  ambiguous account;
- an unexpected existing Organizations or Identity Center configuration
  appears;
- classification needs more than the three allowed summary surfaces, an AWS
  CLI/API call, a named identity, policy, permission, assignment, billing
  detail, or retained identifier;
- any create, enable, disable, change, delete, assign, invite, send, Region,
  identity-source, organization, billing, or permission action is necessary;
- a root-trusting probe, IAM setup, STS, S3, retry, correction, UI-control
  fallback, scope expansion, or unsupported action becomes necessary;
- the page emits or requires retention of credential, identifier, raw provider
  detail, or screenshot;
- Runway OS or preservation verification fails.

## Questions And Defaults

Blocking questions: none before the read-only block.

Non-blocking defaults:

- prefer temporary credentials and reserve root for root-required tasks;
- prefer an organization instance only when its account-access capability and
  organization implications fit the observed account class;
- never treat an account instance as AWS account-access administration;
- use `us-east-2` only as a non-binding candidate and leave the permanent
  Region decision for the setup block;
- do not inspect named identities or infer administrative permission from a
  count or presence marker;
- Ryan enters any future name, email, password, invitation, and MFA detail
  directly without sharing it;
- keep repository changes local, unstaged, uncommitted, and unpublished.

Ryan decision points: a material reviewer change; direct sign-in or MFA if the
exact AWS account session has expired; and the separate organization, Region,
identity-source, administrator, permission, and live setup choices after this
block reports. No successor starts automatically.

## Verification And Closeout

Require an accepted sanitized Fable disposition; exact handoff/proposal
identity; no credentials or identifiers in the packet or review log; at most
three read-only summary surfaces; generic classifications only; no mutation
control, AWS CLI/API, IAM identity detail, STS, or S3 activity; valid JSON;
exactly one current task and one second-opinion or active block while running;
dashboard refresh, currentness, health, and rendered inspection; whitespace;
preserved changes; and zero staging.

On safe classification, mark 7C-S3-FP done, keep Task 3.2b current and
decision-needed under Ryan, record the generic account/Identity Center/route
classes, and activate no successor. On ambiguity or unexpected configuration,
mark 7C-S3-FP stopped, keep Task 3.2b current and decision-needed, and
authorize no correction or retry.

## Report Back

Return the Fable disposition; generic account, Identity Center, instance, and
route classes; exact summary-surface count; confirmation that no identifier,
CLI/API call, identity detail, mutation, STS, or S3 action occurred; the exact
Ryan decisions and separately confirmable setup route; changed paths; checks;
and worktree/staging state.

Suggested next block: only after Ryan accepts the route, separately propose
`7C-S3-FA — Non-Root Administrator Bootstrap And Fresh Sign-In Proof`. That
block may implement only the chosen identity route and prove a fresh non-root
sign-in; Task 3.2c and S3 remain excluded.

## Plain-English Confirmation

Ryan confirmed that Codex will first record this exact read-only readiness
block and send the repo-backed packet to Fable 5 max. On acceptance without a
material change, Codex may inspect only the Organizations and IAM Identity
Center summary surfaces, plus one IAM account summary if strictly necessary,
and return the safest exact setup route. Codex will not enable anything,
create an identity, choose a permanent Region, use AWS CLI or APIs, or touch
S3. Every result stops for Ryan.

## Second-Opinion Result

The exact direct Claude CLI `claude-fable-5` max-effort invocation exited with
status zero but returned only a planning sentence saying it would assess the
proposal and record the review in a plan file. It returned none of the required
classification, confidence, audit, materiality, recommendation, or
missing-information fields. A read-only check found no corresponding plan
file.

Codex classified the response as `MALFORMED_REVIEW_OUTPUT`. It is not an
accepted review and cannot authorize AWS inspection. No retry, changed
permission mode, alternate reviewer, or fallback was attempted.

## Final Result

7C-S3-FP stopped at the mandatory review gate before Chrome or AWS. Exactly one
Fable invocation ran. Zero AWS console surfaces were read and zero AWS CLI/API,
Organizations, IAM Identity Center, IAM, STS, or S3 actions occurred. Nothing
was created, enabled, changed, assigned, invited, sent, or deleted, and no
identifier or credential was retained.

Task 3.2b remains current and decision-needed under Ryan; Task 3.2c remains
planned and blocked. Any reviewer recovery, AWS inspection, non-root setup, or
S3 continuation requires a fresh proposal and confirmation.

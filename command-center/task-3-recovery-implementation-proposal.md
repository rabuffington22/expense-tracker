# Task 3 Recovery Implementation Proposal

Date: 2026-07-30

Status: historical 7C proposal; local stage passed at 7:22 PM CDT and the
unstarted Backblaze provider stage was superseded by confirmed 7C-S3

> **2026-07-30 provider-stage supersession:** Ryan removed the unstarted
> Backblaze provider stage and confirmed the replacement
> `7C-S3 — Synthetic S3 Capability Proof` for Task 3.2 only. The completed
> Task 3.1 local evidence remains accepted. The active S3 scope and authority
> are defined in `command-center/s3-synthetic-capability-proof-plan.md`;
> historical B2 text below is retained as the decision record and does not
> authorize Backblaze activity.

## Local Task Decomposition

- **Task 3.1 — Trigger And Synthetic Provider-Capability Contract.** Select the
  wake-capable acquisition trigger, define exact identities and permissions,
  build synthetic encrypted fixtures, and write a disposable B2 capability
  proof plan.
- **Task 3.2 — Synthetic B2 Capability Proof.** In a dedicated synthetic
  namespace, prove uploader, retention, observer, and restore-reader
  capabilities; governance-mode lock behavior; extension; denied operations;
  manifest parity; and cleanup after expiry. No production data.
- **Task 3.3 — Disabled Recovery Acquisition Implementation.** Implement the
  application-consistent acquisition, encryption, manifest, logical-role, and
  failure behavior in disabled/local mode with synthetic tests.
- **Task 3.4 — Protected Activation And First Current Set.** Under a new exact
  authorization, establish protected identities and recipients, activate the
  trigger and independent observer, acquire one production recovery set, and
  verify only sanitized evidence.

Task 3.1 and Task 3.2 form the proposed first work block because the reviewed
architecture requires both the trigger and the provider's exact authority model
to be proven before recovery code or production setup is safe to finalize.
Tasks 3.3 and 3.4 remain excluded because their implementation and protected
activation depend on the proof.

## Confirmed Work Block 7C

Name: Synthetic Trigger And B2 Capability Proof

Parent phase: Phase 7 — Operational Safeguards Activation And Currentness Proof

Included tasks:

- Task 3.1 (`P7-T31`)
- Task 3.2 (`P7-T32`)

Excluded tasks:

- Task 3.3 (`P7-T33`)
- Task 3.4 (`P7-T34`)
- Tasks 4-7 (`P7-T4`-`P7-T7`)

Why the included tasks belong together: they answer the one prerequisite
question that can change the entire implementation—whether a wake-capable
trigger and the required least-privilege B2 authority split can actually be
reproduced. Both use synthetic data and produce a single go, revise, or switch
to S3 decision.

Why the excluded tasks stay out: recovery code shape depends on the proof, and
protected activation introduces production databases, credentials, encryption
identities, scheduled execution, and recovery artifacts.

Expansion candidates: none.

Recommended scope: base block only.

Autonomous owner: Codex Desktop.

Recommended agent: Codex Desktop.

Agent rationale: the block combines command-center stewardship, local
synthetic fixtures, exact provider/IAM proof, fail-closed cleanup, and final
architecture disposition. No additional second opinion is recommended because
Fable 5 already reviewed this exact boundary.

Runner/handoff path: current Codex task. Use local synthetic fixtures first.
Provider work, if confirmed, is limited to one dedicated synthetic B2
namespace and separately named non-production principals. Ryan performs any
provider sign-in, MFA, purchase approval, or recovery-key custody handoff
directly.

Expected files and surfaces:

- `command-center/` planning, evidence, and dashboard files;
- synthetic fixtures and focused tests under existing repo conventions;
- a disabled/local trigger proof;
- one dedicated synthetic B2 namespace and non-production principals only
  after exact account and cost preflight.

Stop conditions:

- the exact B2 account, cost, Object Lock mode, or synthetic namespace is
  ambiguous;
- sign-in, MFA, payment, or recovery-key custody cannot remain Ryan-owned;
- B2 cannot reproduce the required least-privilege separation;
- the proof would require production databases, uploads, Fly secrets, or real
  financial data;
- cleanup would delete anything outside the exact synthetic namespace;
- a denied-operation test unexpectedly succeeds;
- scope expands into disabled recovery implementation or production
  activation;
- a user change cannot be preserved;
- verification or dashboard health fails.

Blocking questions before execution:

1. Which existing Backblaze account and billing context owns the synthetic
   proof? Ryan must establish the exact account at the protected handoff.
2. Does Ryan approve creation and later exact cleanup of one dedicated
   synthetic bucket/namespace plus the four non-production principals? The
   proposal recommends yes, with Object Lock governance mode and a minimal
   temporary lock floor.

Non-blocking defaults:

- select a Fly wake-capable scheduled Machine invocation rather than an
  in-process timer, subject to local configuration proof;
- use synthetic encrypted SQLite fixtures only;
- use governance mode for the proof;
- use public recipient identifiers only in tracked artifacts;
- create no compliance-mode objects;
- retain no secret, account, key, token, bucket identifier, or object payload
  in tracked files or chat;
- stop and recommend S3 rather than weakening the authority model;
- keep all repo changes local, unstaged, uncommitted, and unpublished.

Verification:

- the local trigger contract proves from tracked configuration that an
  authenticated request can wake the existing zero-idle Machine; actual
  zero-Machine execution remains part of the separately gated implementation
  and activation path;
- uploader can upload but cannot list, read, delete a version, alter retention,
  alter legal hold, change bucket policy, or bypass governance; because
  `writeFiles` also authorizes hide-by-name, the observer must independently
  detect hide markers and duplicate names;
- retention principal can extend but not shorten retention;
- observer can read only freshness metadata;
- restore reader can read the exact synthetic set but cannot upload, retain,
  or delete;
- two-recipient encryption decrypts independently with each synthetic key;
- manifest parity, complete-set behavior, partial-set failure, role
  computation, lock expiry, and cleanup rules pass;
- no production/protected data or Fly/provider secret is retained;
- dashboard refresh/currentness/health and `git diff --check` pass.

Dashboard closeout:

- on pass, close Task 3.1 and Task 3.2, preserve the exact proof result, and
  return a separately proposed Task 3.3 block;
- on B2 authority failure, stop and return an S3 decision;
- activate neither Task 3.3 nor Task 3.4 automatically.

Report back: selected trigger; exact capability matrix; synthetic test results;
denied operations; cleanup result; cost/identity limitations; B2 go, revise, or
S3 verdict; changed files; verification; and the next separate gate.

Plain-English confirmation summary:

If Ryan confirms 7C, Codex will first record it as active, then build the local
synthetic trigger and encryption proof. At the protected handoff, Ryan will
establish the exact Backblaze account and approve any required billing step;
Codex may then create and later clean up only the dedicated synthetic
namespace and non-production principals described above. No production
database, upload, Fly secret, real financial data, compliance-mode retention,
recovery implementation, activation, restore, publication, commit, or push is
included. Codex will stop after the capability verdict and report back before
Task 3.3.

## Activation

Ryan confirmed 7C at 7:13 PM CDT. Codex must first record the block as active
and verify the command center. It may then complete the local synthetic trigger,
encryption, manifest, logical-retention, and provider-capability contract work.

Before any Backblaze sign-in, billing action, bucket or namespace creation,
principal creation, Object Lock action, upload, or cleanup, Codex must stop at
the protected handoff. Ryan establishes the exact account and billing context,
handles sign-in and MFA directly, and confirms that the exact synthetic
provider mutation may proceed. The local stage does not consume or broaden that
protected handoff.

## Local-Stage Result

Task 3.1 passed locally at 7:22 PM CDT. The selected future trigger is a
GitHub Actions scheduled authenticated synchronous HTTPS request to the
existing Fly service Machine. Synthetic online backup, two-recipient
decryption, complete and partial-set manifest rules, Central Time 14/8/12
logical roles, lock-floor independence, and the offline B2 allow/deny matrix
passed with zero network calls and zero protected-data reads.

The provisional B2 verdict is `revise-before-provider-proof` because
`writeFiles` also authorizes hide-by-name. Task 3.2 must test unique
non-reusable names and independent version observation before B2 can receive a
go verdict. No provider action has occurred; Task 3.2 is waiting at the exact
protected handoff described above.

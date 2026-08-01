# Proposed 7C-S3-E — Offline AWS Harness Isolation And Safety Proof

Date: 2026-07-31

Status: done locally at 8:44 PM CDT on 2026-07-31.

## Parent Phase And Tasks

Parent phase: Phase 7 — Operational Safeguards Activation And Currentness
Proof.

Included: Task 3.2a (`P7-T32A`) — Offline Assumption Harness Isolation And
Safety Proof — only.

Excluded: Task 3.2b (`P7-T32B`) protected one-role AWS assumption probe; Task
3.2c (`P7-T32C`) final synthetic S3 capability proof; Tasks 3.3-3.4 and 4-7.

## Purpose

Repair the process flaw exposed by 7C-S3-D without touching AWS. Local
validation must use real disposable executable fixtures rather than shell
functions, must require an explicit absolute mock executable path, and must
fail before execution when the path or mode is missing, ambiguous, or outside
the disposable mock root.

## Scope

1. Write the confirmed block into Runway OS.
2. Route the repo-backed proposal and current harness through Claude CLI
   `claude-fable-5` at `max` effort with no write tools or session persistence.
3. Stop for Ryan if the review changes scope or the safety architecture
   materially.
4. Otherwise revise the local harness so its default state cannot execute a
   live AWS command and its offline-test mode accepts only an explicit absolute
   executable inside a per-run disposable mock root.
5. Add an executable-fixture self-test covering success, denial, cleanup,
   missing-mode, missing-path, outside-root, real-PATH shadowing, and
   unexpected-caller stops without invoking the installed AWS CLI.
6. Add a static audit proving every AWS operation passes through the injected
   executor and no bare `aws` command remains.
7. Run only the offline tests and reconcile Runway OS.

The block may leave a later live mode disabled or absent. Enabling or running
that mode belongs to Task 3.2b and requires a new confirmation.

## Exclusions

- no invocation of the installed AWS CLI, including read-only identity calls;
- no AWS API, console, Chrome, CloudShell, account, role, STS, IAM, or S3
  action;
- no credential, environment-secret, profile, config, cache, or identifier
  inspection;
- no role, trust policy, bucket, object, retention, or other mutation;
- no production data, Fly, workflow, scheduler, recovery implementation,
  activation, publication, Git staging/commit/push/PR/merge, Task 3.2b,
  Task 3.2c, Task 3.3, or successor work.

## Expansion Check

Expansion candidates: none. Task 3.2b changes from offline source verification
to protected AWS execution, and Task 3.2c adds S3 mutation and a different
verification path.

Expansion question: none. The safer default is to keep both live stages out.

Recommended scope: base block only.

## Owner And Agent

Autonomous owner: Codex Desktop.

Recommended agent: Codex Desktop, with Fable 5 max as the pre-implementation
reviewer.

Why: Codex must preserve the dirty worktree, integrate the harness and tests,
maintain Runway OS, and verify that no external route is reachable. Independent
review is valuable because the previous failure was in the validation boundary
itself, not in the IAM design.

Runner path: current Codex task for local repo work. The second opinion reviews
only the sanitized repo-backed artifact and harness. No browser or AWS runner
is used.

Codex retains final review intake, exact-scope verification, dashboard
currency, and stop enforcement.

## Expected Files And Surfaces

- `scripts/s3_assumption_probe.sh`;
- one focused offline executable-fixture test under `scripts/`;
- this proposal, one confirmation/result log, second-opinion handoff/intake,
  and Runway OS source plus generated dashboard files.

No protected, hosted, credential, database, application-product, browser,
AWS, or publication surface is included.

## Stop Conditions

Stop without correction or retry if:

- Fable 5 max requires a material scope or safety-architecture change;
- an offline test could resolve a command from normal `PATH` or invoke a path
  outside its disposable mock root;
- safe verification would require the installed AWS CLI, credentials,
  profiles, network access, Chrome, CloudShell, or another external surface;
- a live mode could run by default or without a later explicit gate;
- a user-owned change cannot be preserved;
- scope expands, sensitive output appears, or verification fails in a
  plan-changing way;
- Runway OS cannot be refreshed and health-checked.

## Questions And Defaults

Blocking questions: none.

Non-blocking defaults:

- use Fable 5 max for the second opinion;
- keep live execution disabled or absent after this block;
- require real disposable mock executables, never exported shell functions;
- clear inherited AWS credential/profile variables inside offline tests;
- use only sanitized markers and temporary paths;
- keep all changes local, unstaged, uncommitted, and unpublished.

Ryan decision points: confirmation of this offline block now; later separate
confirmation of Task 3.2b only after the offline proof closes cleanly.

## Verification And Closeout

Require:

- sanitized second-opinion disposition;
- Bash syntax checks;
- focused offline executable-fixture self-test;
- missing-mode, missing-path, outside-root, PATH-shadow, unexpected-caller,
  assumption-denial, and cleanup paths fail closed as designed;
- static proof that no bare `aws` execution remains and every operation uses
  the injected executor;
- no installed AWS CLI, network, credential, browser, CloudShell, IAM, STS, or
  S3 invocation;
- valid JSON, exactly one current task, zero active work blocks after closeout,
  dashboard refresh/currentness/health, rendered inspection, whitespace,
  preserved user changes, and zero staging.

On pass, mark Task 3.2a and 7C-S3-E done, retain Task 3.2 active, make Task
3.2b current and decision-needed under Ryan, and activate no successor. On a
stop, keep Task 3.2a current and decision-needed and authorize no repair or
live action.

## Report Back

Return the review disposition, isolation architecture, offline matrix,
static-executor audit, confirmation that no AWS/browser/credential route was
used, changed paths, checks, worktree/staging state, and the separate Task
3.2b decision gate.

Suggested next block after a complete pass: separately propose `7C-S3-F —
Protected One-Role Assumption Probe` for Task 3.2b only. It does not start
automatically and does not include S3.

## Plain-English Confirmation

If Ryan confirms, Codex will first record this exact block, then have Fable 5
max review the offline safety design. If the review does not materially change
it, Codex will repair and test only the local harness using disposable fake
executables that cannot fall through to the real AWS CLI. No AWS, Chrome,
CloudShell, credentials, IAM, STS, S3, Git publication, or later recovery work
will run. Codex will stop on any isolation doubt and report back before a
separate live-probe decision.

## Second-Opinion Result And Revised Scope

Fable 5 max returned `MATERIAL_CHANGE_REQUIRED` at 85% confidence. The review
accepted the single injected-executor seam, explicit offline-only mode, real
executable fixtures, validate-before-trap order, and absence of live mode, but
found two plan-changing gaps:

1. A caller-supplied mock root could be chosen broadly enough to contain the
   installed AWS CLI and make that real executable pass containment checks.
2. Clearing `PATH` and AWS variables only in the test launcher would not stop a
   buggy fixture child from resolving the installed CLI with ambient state.

The revised implementation must therefore:

- have the harness create and own a fresh `/tmp` mock root itself with
  must-create semantics, install its mock executor internally, and accept no
  caller-supplied root or executable;
- run every fixture through a harness-controlled minimal environment with
  inherited AWS credential, profile, config, region, role, and web-identity
  variables removed; harness-owned empty config and credentials files;
  metadata disabled; and PATH limited to the disposable root;
- finish boundary validation before installing cleanup; offline cleanup may
  remove only the harness-owned root and performs no AWS-shaped operation;
- add positive invocation logs plus pre-existing-root, symlink, prefix,
  relative-path, type/mode, exact-mode, environment, and trap-ordering tests;
- keep live mode physically absent and retain every original exclusion.

Because this changes the confirmed safety architecture, the block stopped at
the review gate. Confirming the revised 7C-S3-E scope authorizes only this
reviewed local implementation and offline proof. It still authorizes no
installed AWS CLI, AWS API, credential, browser, CloudShell, IAM, STS, S3,
production, Fly, recovery activation, publication, Git, Task 3.2b, Task 3.2c,
or successor action.

Ryan confirmed this revised scope at 8:37 PM CDT. Local implementation and
offline proof may proceed; every listed external and successor exclusion
remains in force.

## Result

The harness now creates and owns its disposable root and mock executor, keeps
live mode absent, validates containment before trap installation, enforces a
cleared minimal environment on every synthetic invocation, rejects caller
root and executor injection before running, and performs only exact local-root
cleanup. Bash syntax and all 24 executable-fixture cases pass. The hostile
PATH sentinel was never called; no probe or test root remains.

The first cleanup check exposed macOS canonicalizing `/tmp` to `/private/tmp`.
The guard was corrected to accept only those exact legitimate canonical forms;
the two synthetic roots from the failed checks were exactly removed before the
full passing rerun. No installed AWS CLI, AWS API, credential, browser,
CloudShell, IAM, STS, S3, publication, Git, Task 3.2b, Task 3.2c, or successor
action occurred.

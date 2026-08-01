# Fable 5 Max Review — 7C-S3-E Offline Harness Isolation

Date: 2026-07-31

Reviewer route: Claude CLI direct run

Model and effort: `claude-fable-5`, `max`

Execution boundary: `--safe-mode --tools "" --permission-mode plan
--no-session-persistence`; no reviewer tools or fallback.

## Classification

`MATERIAL_CHANGE_REQUIRED`

Confidence: 85%.

## Direct Critique

The reviewer accepted the central executor seam, explicit exact-match offline
mode, real executable fixtures, validate-before-trap ordering, and preference
for shipping with live mode physically absent. Routing every AWS-shaped
operation through one validated absolute path removes the PATH fall-through
mechanism that caused 7C-S3-D.

It found two material gaps:

1. **Mock-root provenance is not enforced.** If the caller supplies both the
   mock root and executor, a broad existing root could contain the installed
   AWS CLI and still satisfy absolute-path, canonical-containment, regular-file,
   and executable checks. The harness must create and own a fresh root itself;
   containment inside a caller-selected root is not sufficient.
2. **The executor environment is not enforced by the harness.** Launcher-only
   `PATH` and AWS-variable clearing does not protect another invocation or a
   buggy fixture that starts a child command. Every fixture invocation must use
   a harness-controlled minimal environment, empty harness-owned AWS config and
   credentials files, metadata disabled, and a controlled PATH that cannot
   resolve the installed CLI.

The reviewer confirmed validation must finish before installing an EXIT trap.
Using an unvalidated executor during cleanup is less safe than leaking a
disposable pre-validation directory.

## Required Material Changes

- The harness creates the per-run mock root itself with must-create semantics,
  installs the mock executor internally, and computes its executable path
  without accepting a pre-existing caller root or executor.
- Every mock invocation is launched through a harness-controlled environment
  with credential, profile, region, role, web-identity, and config inheritance
  removed; config and credentials paths point to harness-created empty files;
  instance metadata is disabled; and PATH is limited to the disposable root.

These changes alter the confirmed safety architecture, so implementation
requires Ryan's confirmation.

## Non-Material Clarifications

- Canonicalize with portable macOS/Bash 3.2 directory `pwd -P`; reject a final
  symlink; require owned, regular, executable file; compare containment with a
  path-separator boundary; execute only the stored canonical path.
- Install the cleanup trap only after validation and capture canonical paths by
  value. Offline cleanup performs no AWS-shaped operation.
- Use an unmistakably mock-only variable name and forbid `eval` or dynamically
  constructed commands. Treat the bare-`aws` static check as advisory defense
  in depth rather than the runtime control.
- Prefer the exec-based fixture because it still proves argument, environment,
  exit-code, and child-process behavior. A pure in-process case dispatcher is
  safer but less probative and remains a fallback if portable containment
  cannot be proven.

## Required Test-Matrix Additions

- Positive invocation log and expected call sequence, not only sentinel
  silence.
- Refusal of pre-existing/caller-provided roots and executors.
- Executor and root symlink cases, dangling path, prefix collision, executor
  equals root, directory executor, non-executable file, and relative values.
- Exact mode checks for unset, empty, `live`, unknown, and padded values.
- Fixture-visible environment proof for cleared AWS variables, harness-owned
  empty config paths, metadata disabled, and controlled PATH.
- Validation-failure proof that no trap cleanup, fixture, or sentinel ran.

## Safer Alternative

A pure in-process mock dispatcher would eliminate executable-child risk but
would no longer test the real exec boundary. The reviewer recommends the
exec-based design only with both material changes above.

## Missing Information

The result would change if the harness already created the mock root internally
(it does not), or if exact offline-trap and fixture implementations changed the
child-process risk. No AWS execution, credential inspection, live-probe
broadening, or S3 work was proposed or performed.

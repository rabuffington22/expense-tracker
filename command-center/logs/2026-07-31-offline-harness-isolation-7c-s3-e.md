# 7C-S3-E Result — Offline AWS Harness Isolation And Safety Proof

Date: 2026-07-31

Status: done locally at 8:44 PM CDT.

## Result

The revised offline harness is fail-closed and live mode is physically absent.
It accepts only exact `PROBE_MODE=offline-test`, creates and owns a fresh
disposable root under `/tmp`, installs its mock executor internally, validates
canonical containment and ownership before installing its EXIT trap, and
routes every AWS-shaped synthetic operation through that stored canonical
executor.

Every fixture invocation uses `/usr/bin/env -i` with PATH limited to the
disposable mock `bin` directory, harness-owned empty config and credentials
files, instance metadata disabled, and no inherited credential, profile,
region, role, or web-identity variables. Caller-supplied mock roots and both
legacy or mock executor variables fail before root creation, run markers, or
trap installation.

Offline cleanup performs no AWS-shaped operation. It deletes only known files
inside the validated harness-owned root, removes exact empty directories, and
requires root absence before reporting success.

## Verification

- Bash syntax passed for the harness and focused test.
- The focused executable-fixture matrix passed 24 cases:
  - success, assumption denial, and unexpected caller;
  - live, empty, unknown, padded, and unset modes;
  - invalid scenario;
  - caller root, legacy executor, and mock-executor injection;
  - valid containment;
  - executor and root symlinks;
  - prefix collision, relative path, executor-equals-root, directory,
    non-executable, missing, and dangling executor;
  - hostile-PATH sentinel not called;
  - static executor audit.
- The success path also proved the fixture-visible cleared environment,
  expected invocation sequence, and exact root cleanup.
- Static audit found no bare `aws`, `eval`, installed-cli path, or competing
  execution seam; exactly one `/usr/bin/env -i` executor seam exists.
- No matching probe or test root remained under canonical `/private/tmp`.
- `shellcheck` was unavailable; Bash syntax and the executable matrix are the
  maintained checks used instead.

## Corrected Local Verification Defect

The first offline run completed every synthetic operation but cleanup rejected
its own root because macOS canonicalizes `/tmp` to `/private/tmp`. A direct
diagnostic reproduced the same local-only result. The guard was narrowed to
accept only the exact original `/tmp/ledger-assumption-probe.*` shape plus its
two legitimate canonical forms under `/tmp` or `/private/tmp`. The two
synthetic roots from those failed runs were inspected, contained only the
expected mock files, and were removed by exact file unlink and directory
removal. The expanded matrix then passed with no root remaining.

## Boundaries

No installed AWS CLI, AWS API, credential or profile lookup, config or cache
inspection, network request, browser, Chrome, CloudShell, IAM, STS, S3,
production data, Fly, recovery activation, publication, Git action, Task 3.2b,
Task 3.2c, or successor action occurred.

All work remains local, unstaged, uncommitted, and unpublished.

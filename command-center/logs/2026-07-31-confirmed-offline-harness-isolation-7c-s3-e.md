# Work Block 7C-S3-E — Confirmed Offline AWS Harness Isolation And Safety Proof

Date: 2026-07-31

## Confirmation

Ryan confirmed `7C-S3-E` at 5:42 PM CDT for Phase 7 Task 3.2a
(`P7-T32A`) only.

## Authorized Sequence

Codex Desktop must first write and verify the confirmed block, then route the
repo-backed proposal and current harness through Claude CLI
`claude-fable-5` at `max` effort with no write tools and no session
persistence. A material scope or safety-architecture change stops for Ryan.

On an accepted or only non-materially clarified review, Codex may revise and
test only the local harness. Offline validation must use explicit absolute
disposable executable fixtures inside a per-run mock root, must not resolve a
normal `PATH` command, and must keep live execution disabled or absent.

## Exclusions And Stop

No installed AWS CLI invocation, AWS API, credential, profile, config, cache,
Chrome, CloudShell, IAM, STS, S3, role, trust policy, bucket, production data,
Fly, workflow, scheduler, recovery activation, publication, Git action, Task
3.2b, Task 3.2c, Task 3.3, or successor is authorized.

Stop without correction or retry on a material review change; any
normal-PATH or outside-mock-root execution route; need for installed AWS CLI,
credential, network, browser, or hosted access; live mode enabled by default;
sensitive output; user-change conflict; scope expansion; or plan-changing
verification failure.

## Second-Opinion Stop

Fable 5 max returned `MATERIAL_CHANGE_REQUIRED` at 85% confidence. The block
stopped at the review gate before implementation. The revised design must make
the harness create and own the mock root and must enforce a minimal cleared
environment for every fixture invocation. No harness edit, offline test,
installed AWS CLI, AWS API, credential, browser, CloudShell, IAM, STS, S3,
publication, Git, Task 3.2b, Task 3.2c, or successor action followed.

## Revised-Scope Confirmation

Ryan confirmed the materially revised 7C-S3-E scope at 8:37 PM CDT. Codex may
implement and test only the harness-owned mock root, internally installed mock
executor, harness-enforced cleared minimal environment, validate-before-trap
ordering, local-only cleanup, and expanded negative matrix. The original
external and successor exclusions remain unchanged.

## Final Result

The revised harness and 24-case offline executable-fixture matrix passed at
8:44 PM CDT. The first cleanup verification exposed the macOS `/tmp` to
`/private/tmp` canonical form; the exact guard was corrected, both synthetic
failed-run roots were removed, and the full matrix then passed with zero
remaining roots. No installed AWS CLI, credential, network, browser, hosted,
Git, or successor action occurred.

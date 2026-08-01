# Fable 5 Max Review — 7C-S3-F One-Role Probe

Date: 2026-07-31

Reviewer route: Claude CLI direct run

Model and effort: `claude-fable-5`, `max`

Execution boundary: `--safe-mode --tools "" --permission-mode plan
--no-session-persistence`; no reviewer tools or fallback.

## Classification

`ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS`

Confidence: 90%.

## Accepted Review

The reviewer found the packet safe and sufficiently fail-closed for one run
under 7C-S3-F. It accepted the assumed-role ARN parsing, exact same-account
`GetRole` lookup, path-aware stable-role match, direct trust to only that role,
one empty disposable role, one assumption attempt, generic output, in-memory
temporary credentials, one guarded cleanup, and conjunctive absence proof.

It found exactly eight counter-incremented AWS CLI call sites on the normal
path: two current-caller reads, one current-role read, one role creation, one
assumption, one temporary-caller read, one deletion, and one absence check.
Pre-create failure paths use one to three calls; create failure uses six;
assumption failure uses seven; and temporary-caller or shape failure uses
eight. There is no loop, waiter, scripted retry, or S3 command.

The cleanup audit found that every create-attempt path runs exactly one
deletion and one absence check through the EXIT trap. Absence passes only when
`GetRole` fails and its captured error class is `NoSuchEntity`; permission,
transport, throttling, and parse failures remain cleanup failures. A partial
run cannot self-certify because success additionally requires the incoming
status, cleanup, and `PROBE_COMPLETE` all to pass.

The identifier audit found only fixed generic output plus the action count.
Provider stdout is captured or discarded, stderr is suppressed except for the
in-memory absence classification, temporary credentials are passed as
per-command environment values rather than argv, and the cleanup trap unsets
them on every trapped exit.

## Non-Material Clarifications

The reviewer identified defense-in-depth improvements that do not broaden the
confirmed scope:

1. Pin `AWS_MAX_ATTEMPTS=1` with `AWS_RETRY_MODE=standard` so AWS CLI cannot
   transparently retry a wire request and the eight-call ceiling remains exact.
2. Validate the full stable-role resource/path charset before interpolating it
   into the JSON trust document so unusual punctuation fails closed.
3. Disable inherited Bash xtrace so identifiers or credentials cannot echo if
   the invoking environment enabled tracing.
4. Use stronger disposable-name entropy to narrow the theoretical collision
   risk before the create-ambiguous cleanup path.

Codex adopted all four clarifications before AWS: one-attempt retry settings,
full safe-path charset validation, `set +o xtrace`, and a 128-bit kernel UUID
suffix. These changes add no API call, retry, existing-resource read, mutation,
output, credential, S3 action, or different success criterion.

## Recommendation

Proceed once under 7C-S3-F after local Bash syntax, static action-envelope,
offline matrix, command-center, and zero-staging checks pass. On any stop, run
the single guarded cleanup and do not retry. A clean pass proves only Task
3.2b; Task 3.2c remains separately gated.

## Missing Information

The original packet did not pin inherited AWS CLI retry configuration. The
adopted environment settings resolve that uncertainty before execution.

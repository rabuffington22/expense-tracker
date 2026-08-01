# Fable 5 Max Review — 7C-S3-D Assumption Probe

Date: 2026-07-31

Reviewer route: Claude CLI direct run

Model and effort: `claude-fable-5`, `max`

## Classification

`ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS`

Confidence: 90%.

## Accepted Review

The reviewer found the diagnostic correctly targeted, minimal, and safe. It
accepted role-name derivation from the assumed-role session shape, one exact
`GetRole` lookup to recover the path-qualified stable role ARN, same-account
direct-role trust, an empty disposable role, temporary credentials used only
for caller-shape confirmation, and exact deletion plus absence verification.

The reviewer found no safer alternative that remains equally probative without
broadening existing-resource reads. Policy simulation would be broader and
would not reliably prove the trust-policy path.

## Non-Material Clarifications Adopted

1. Wait a fixed 20 seconds after role creation before the single evidentiary
   `AssumeRole` request to avoid an IAM propagation false negative. This is not
   a retry. The optional delayed second attempt is rejected because the
   confirmed block authorizes no retry.
2. Run deletion and absence verification on every post-creation exit. Cleanup
   is mandatory and is not treated as diagnostic correction.
3. If assumption is denied, record only a sanitized failure class and conclude
   only that this current session could not assume the directly trusting empty
   role. Do not infer a universal trust-policy failure because an explicit
   deny, organization policy, session policy, or permissions boundary could
   also produce the denial.
4. Record role-chaining's one-hour session ceiling only as forward-looking
   context for a later recovery design; it does not affect this short probe and
   does not enter the current scope.

## Material-Change Check

No material change is required. The review adds no broader existing-resource
read, existing-resource mutation, extra role, S3 action, access key, IAM user,
permanent credential, new success criterion, or different identity
architecture. The confirmed diagnostic may proceed with the three defensive
clarifications above.

## Missing Information

An AWS Organizations service control policy or a permissions boundary could
make a negative result ambiguous, but would not change the probe's safety. The
existing stop and interpretation rules cover that uncertainty without another
read or retry.

## Execution Disposition

The accepted design was not executed in Chrome CloudShell. A later local
harness validation unexpectedly resolved to a real local AWS CLI identity and
stopped fail-closed after two read-only caller-identity checks because the
caller shape was not an assumed role. No IAM or S3 mutation occurred, and no
retry followed.

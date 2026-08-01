# Second Opinion — 7C-S3-D Exact Caller Role And One-Role Assumption Probe

Date: 2026-07-31

Reviewer route: Claude CLI direct run

Model and effort: `claude-fable-5`, `max`

Why this route: Ryan specified Fable 5 at max effort as the default
second-opinion route. This is a bounded text-only AWS IAM architecture review
with no need for repository tools, browser state, credentials, or identifiers.

## Question

Is the confirmed 7C-S3-D diagnostic a sound, least-risk way to prove whether
the current same-account CloudShell role can directly assume a newly created
empty disposable role before any further S3 capability proof?

Classify the proposal as exactly one of:

1. `ACCEPT`
2. `ACCEPT_WITH_NON_MATERIAL_CLARIFICATIONS`
3. `MATERIAL_CHANGE_REQUIRED`

A material change includes any broader existing-resource read, any existing
resource mutation, additional temporary roles, any S3 action, access keys,
IAM users, permanent credentials, changed success criteria, or a different
identity architecture. Material change stops for Ryan's confirmation.

## Prior Evidence

- An earlier synthetic S3 attempt created and then exactly removed one random
  bucket and four random roles, but the current session could not assume the
  uploader role when trust delegated to the account principal.
- A later retry preflight stopped before creation because the STS assumed-role
  caller ARN did not expose the stable IAM role path and existing-role reads
  were prohibited.
- No identifiers, credentials, production data, or existing AWS resources are
  included in this review packet.

## Confirmed Diagnostic

Task 3.2 only:

1. derive the current role name from the signed-in STS assumed-role caller
   shape;
2. make one read-only IAM `GetRole` request for that exact role name and query
   only `Role.Arn` into an in-memory variable without printing or retaining it;
3. validate that the returned ARN is a same-account IAM role ARN;
4. create one randomly named disposable IAM role with no permissions policy;
5. set its trust policy principal to only the exact stable current-role ARN,
   with no wildcard or account-root delegation;
6. make one STS `AssumeRole` request for the disposable role;
7. use returned temporary credentials only for `GetCallerIdentity` shape
   confirmation;
8. delete the disposable role and verify exact absence; then stop.

The IAM `GetRole` API reads the current role record, including path, ARN, and
trust-policy metadata, even though the CLI query emits only the ARN. This is
the single existing-resource read Ryan confirmed. No existing resource may be
changed.

## Exclusions

No S3 API, bucket, object, versioning, Object Lock, retention, four-role
capability matrix, existing IAM mutation, permission or permission-set change,
boundary or trust-policy change, access key, IAM user, permanent credential,
production data, Fly action, workflow/scheduler action, recovery
implementation, activation, publication, Git action, Task 3.3, or successor.

## Stop Conditions

Stop without correction or retry if role-name parsing is ambiguous; `GetRole`
is denied or returns an unexpected account or principal shape; role creation,
direct trust, assumption, caller-shape confirmation, deletion, or absence
verification fails; an identifier would be printed or retained; an existing
resource mutation becomes necessary; or scope, cost, protected-data, or
verification boundaries change.

## AWS Documentation Basis

- `GetRole` returns the specified role's path and ARN:
  https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetRole.html
- `AssumeRole` states that a same-account resource-based trust can directly
  grant the principal without an additional identity policy:
  https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
- IAM role principals may be named exactly in resource-based trust policies:
  https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html

## Requested Response

Return:

1. classification from the three allowed values;
2. direct critique of role-name derivation, exact-ARN lookup, same-account
   direct-role trust, empty-role assumption, temporary-credential handling,
   caller-shape confirmation, and cleanup;
3. any hidden privilege, data exposure, policy-evaluation, or cleanup risk;
4. safer alternatives, clearly labeled material or non-material;
5. final recommendation and confidence percentage;
6. missing information that would materially change the recommendation.

Do not request or invent any account ID, ARN, role name, session name,
credential, bucket name, policy, or production data. Do not propose S3 work or
implementation as part of this diagnostic.

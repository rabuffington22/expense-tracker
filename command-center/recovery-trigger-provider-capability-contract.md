# Recovery Trigger And Provider-Capability Contract

Date: 2026-07-30

Status: Task 3.1 passed locally; Task 3.2 is waiting at the protected
Backblaze handoff

## Result

The local synthetic proof passed without network access or protected-data
reads. It selects a scheduled, authenticated, synchronous HTTPS request to the
existing Fly application Machine as the recovery-acquisition trigger.

The provisional Backblaze verdict is **revise before provider proof**. B2 can
separate upload, observation, restore-read, and retention-extension authority,
but its `writeFiles` capability also permits the Native API
`b2_hide_file`. The uploader therefore cannot honestly be described as strict
create-only. Task 3.2 must prove whether unique, non-reusable object names plus
independent version observation make that limitation acceptable. If not,
Amazon S3 remains the required fallback.

## Trigger Decision

Tracked `fly.toml` establishes:

- the application mounts the only active data volume at `/data`;
- the service can stop to zero Machines;
- incoming traffic can autostart the existing service Machine.

The selected design is:

1. a future GitHub Actions schedule fires at `47 10 * * *`, exactly 90 minutes
   after the tracked Plaid schedule at `17 9 * * *`;
2. the workflow makes one authenticated HTTPS request to a future disabled-by-
   default recovery endpoint;
3. Fly Proxy wakes the existing service Machine when it is stopped;
4. the request stays open until all three online backups, integrity checks,
   encryption steps, uploads, and complete-set manifest publication finish;
5. the caller treats a timeout or non-success response as failure.

This is a contract selection only. Work block 7C does not add the workflow,
endpoint, secret, or runtime recovery implementation.

Rejected alternatives:

- an in-process timer cannot run while the application is stopped;
- a separate scheduled Fly Machine cannot share the existing Fly Volume;
- converting the web Machine into a finite scheduled Machine is incompatible
  with its HTTP-service role.

GitHub documents that scheduled workflows run from the default branch and can
be delayed under load. Freshness observation therefore remains an independent
off-Fly control; the schedule alone is not evidence of a current recovery set.

## Offline Synthetic Proof

`scripts/recovery_synthetic_proof.py` and its focused test prove:

- SQLite Online Backup captures committed data while synthetic sources remain
  in WAL mode;
- all three isolated entity artifacts must pass before one manifest exists;
- a synthetic one-entity failure publishes no complete-set manifest;
- two independent synthetic X25519 recipients can each decrypt every artifact,
  while an unrelated recipient cannot;
- only complete passing sets enter the Central Time 14-daily, 8-weekly, and
  12-monthly logical roles;
- changes to synthetic Object Lock floors do not change logical-role
  selection;
- the selected trigger assumptions match tracked `fly.toml`;
- the expected B2 capability outcomes match the official capability model.

The envelope is deliberately proof-only. It demonstrates the two-recipient
property but is not the `age` file format and is not production recovery code.

## Provisional B2 Principals

All provider identities must be non-production, restricted to the one
dedicated synthetic namespace, and created only after the protected handoff.

| Principal | Capabilities | Intended allowance | Required denials and caveats |
| --- | --- | --- | --- |
| Uploader | `writeFiles` | Upload a new uniquely named object | No list, read, delete-version, retention, legal-hold, bucket-policy, or bypass authority. `writeFiles` does permit hide-by-name, which must be tested and monitored. |
| Freshness observer | `listFiles`, `readFileRetentions`, `readFileLegalHolds` | List versions and inspect freshness/lock metadata | No payload read, upload, delete, retention mutation, legal-hold mutation, or bucket mutation. |
| Restore reader | `listFiles`, `readFiles`, `readFileRetentions`, `readFileLegalHolds` | Locate and read an exact synthetic recovery set and its lock metadata | No upload, delete, retention mutation, legal-hold mutation, bucket mutation, or bypass. |
| Retention extender | `listFiles`, `readFileRetentions`, `writeFileRetentions` | Extend governance retention on an exact object | No payload read, upload, delete, legal-hold mutation, bucket mutation, or `bypassGovernance`; shortening or removing governance retention must fail. |

No principal receives `deleteFiles`, `bypassGovernance`,
`writeFileLegalHolds`, or `writeBucketRetentions` during the capability proof.
Exact test cleanup may occur only after lock expiry through a separately
authorized, exact-namespace cleanup identity or Ryan-owned console action.

## Task 3.2 Provider Proof

Before any provider action, Ryan must:

1. establish the exact Backblaze account and billing context;
2. handle sign-in and MFA directly;
3. approve creation and later exact cleanup of one dedicated synthetic
   namespace and the four non-production principals above.

After that action-time confirmation, Task 3.2 must:

1. create the exact disposable namespace in governance mode with a minimal
   temporary lock floor;
2. record sanitized key labels and declared capabilities, never key material,
   account identifiers, bucket identifiers, or object payloads;
3. upload uniquely named synthetic encrypted objects with the uploader;
4. prove uploader denials for list, read, version deletion, retention mutation,
   legal-hold mutation, bucket mutation, and governance bypass;
5. explicitly test and record the `b2_hide_file` behavior without treating a
   hidden name as deleted data;
6. prove the observer can list versions and detect hide markers or duplicate
   names but cannot read payloads or mutate anything;
7. prove the restore reader can read the exact synthetic set and cannot write
   or mutate it;
8. prove the retention extender can extend but cannot shorten or remove
   governance retention;
9. prove complete-set manifest parity and independent synthetic decryption;
10. clean up only after expiry and only through the separately confirmed exact
    cleanup path.

Stop immediately if a required denial unexpectedly succeeds, account or
namespace ownership is ambiguous, exact cleanup would exceed the synthetic
namespace, or provider behavior cannot support independent visibility of
hidden versions.

## Decision Rule

- **B2 go:** every required allowance and denial passes, the observer sees
  versions and hide markers independently, unique names cannot be reused by
  the acquisition process, and cleanup stays exact.
- **Revise:** the model remains least-privilege only with a bounded change that
  preserves independent observation and immutable underlying versions.
- **Switch to S3:** B2 cannot reproduce the required separation or the
  hide-by-name limitation makes silent freshness loss unacceptable.

Task 3.3 remains disabled and separately gated regardless of the Task 3.2
result.

## Official References

- Fly Proxy autostop/autostart:
  <https://fly.io/docs/reference/fly-proxy-autostop-autostart/>
- Fly scheduled Machine limitation:
  <https://fly.io/docs/machines/flyctl/fly-machine-run/>
- GitHub scheduled workflow behavior:
  <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>
- Backblaze application-key capabilities:
  <https://www.backblaze.com/docs/cloud-storage-application-key-capabilities>
- Backblaze Object Lock:
  <https://www.backblaze.com/docs/cloud-storage-object-lock>

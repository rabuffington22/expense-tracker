# 7C Local Recovery Trigger And Capability-Contract Proof

Date: 2026-07-30

Status: passed locally at 7:22 PM CDT; stopped at the protected Backblaze
handoff

## Scope

This was the local, synthetic-only stage of confirmed work block 7C. It read
tracked source and public provider documentation, created only disposable
synthetic SQLite and encrypted fixtures, and changed only local unstaged repo
files. It made no network call from the proof harness and read no protected
data.

## Trigger Result

The selected future trigger is a GitHub Actions scheduled, authenticated,
synchronous HTTPS request to the existing Fly service Machine. Tracked
`fly.toml` proves the service may stop to zero, may autostart from traffic, and
mounts the only active `/data` volume.

The future request must remain open until acquisition and upload finish. No
workflow, endpoint, secret, Machine, deployment, or live trigger was created.

## Synthetic Results

Command:

`python3 scripts/recovery_synthetic_proof_test.py`

Result:

- complete Personal, BFM, and LL synthetic WAL-backed set: pass;
- SQLite Online Backup and `PRAGMA integrity_check`: pass for all three;
- two independent synthetic X25519 recipient decryptions: pass;
- unrelated-recipient decryption denial: pass;
- injected BFM failure: partial-failed and no manifest published;
- Central Time logical roles: 14 daily, 8 weekly, 12 monthly;
- logical-role independence from synthetic Object Lock floors: pass;
- tracked Fly trigger assumptions: pass;
- offline B2 allow/deny capability model: pass;
- network calls: zero;
- protected-data reads: zero.

The proof envelope is not the `age` file format. It proves the independent
two-recipient property only.

## Provider-Capability Result

Provisional verdict: **revise before provider proof**.

Backblaze documents that `writeFiles` includes `b2_hide_file`. The uploader can
therefore upload and hide-by-name even when it cannot list, read, delete a
version, change retention, or bypass governance. The revised proof requires
unique non-reusable names and an independent observer that lists versions and
alerts on hide markers or duplicate names.

The four provisional principals are:

1. uploader — `writeFiles`;
2. freshness observer — `listFiles`, `readFileRetentions`,
   `readFileLegalHolds`;
3. restore reader — observer capabilities plus `readFiles`;
4. retention extender — `listFiles`, `readFileRetentions`,
   `writeFileRetentions`, without `bypassGovernance`.

Provider execution must prove exact allowances and denials. If independent
visibility or the authority split fails, switch to S3 rather than weaken the
contract.

## Stop And Handoff

Task 3.1 is done locally. Task 3.2 is current and waiting for Ryan to:

1. establish the exact Backblaze account and billing context;
2. handle sign-in and MFA directly;
3. approve creation and later exact cleanup of one dedicated synthetic
   namespace and four non-production principals.

No Backblaze sign-in, account read, billing action, bucket or namespace,
principal, Object Lock action, upload, cleanup, credential, or protected
identifier was accessed or created.

# Work Block 6B — Backup, Integrity, Restore-Drill, And Recovery-Currency Contract

Date: 2026-07-29

Status: done locally and verified

## Confirmed Scope

Task 2 (`P6-T2`) only. Establish a protected-data-safe contract for backup cadence and freshness, retention tiers, disposable-copy integrity checks, isolated restore drills, recovery-currency reviews and triggers, sanitized evidence, cleanup, escalation, and exact authorization gates; reconcile the operations matrix and operator runbook; verify the command-center package; and close Task 2 locally.

Tasks 1, 3, and 4 (`P6-T1`, `P6-T3`, `P6-T4`); databases, backups, WAL/SHM files, uploads, financial rows, `local_state/`, Fly volumes, Time Machine, protected storage, `scripts/sync_prod_to_local.sh`, backup/integrity/migration/seed/transfer/restore/recovery/cleanup/application commands, storage-provider selection or purchase, automation, product/test/workflow/dependency/configuration/authentication/README changes, staging, commit, push, PR, merge, publication, delegation, second opinion, external action, and unrelated work remained excluded.

## Contract Result

The canonical [`backup-integrity-recovery-currency-contract.md`](../backup-integrity-recovery-currency-contract.md) now establishes:

- one daily application-consistent three-entity recovery set, stale after 36 hours;
- isolated per-entity acquisition, artifact, integrity, retention, and restore evidence, with any partial result failing the whole scheduled set;
- at least 14 daily, 8 weekly, and 12 monthly passing recovery sets;
- weekly disposable-copy integrity verification, stale after eight days;
- one isolated disposable-`DATA_DIR` restore drill per calendar quarter, stale when the prior quarter has no pass or the latest pass is older than 100 days;
- monthly recovery-currency review, stale after 35 days, plus review after migrations, storage/topology or backup-method changes, incidents, or suspected loss/corruption;
- a target recovery point no older than 36 hours once a mechanism exists;
- no recovery-time promise until an authorized drill measures time to a ready-to-cut-over state;
- application-consistent SQLite acquisition through a reviewed online-backup method or a proven quiesced snapshot boundary, never a presumed-complete bare `.sqlite` copy while WAL state may contain committed work;
- sanitized evidence, fail-closed cleanup, and separate authorization rungs for policy, metadata review, acquisition, integrity, restore drill, live restoration, and retention cleanup.

The operations matrix now carries the matching cadence, thresholds, evidence, escalation, and remediation gates. The operator runbook carries the matching preflight and authorization sequence.

## Verification

- The confirmed 6B proposal was written into Runway OS and activated before contract implementation.
- Activation JSON, dashboard refresh, command-center health, whitespace, exactly-one-current-task, and zero-staging checks passed.
- Every local Markdown link in the contract, matrix, and runbook resolves.
- Contract markers for cadence, retention, integrity, drill, review, SQLite consistency, authorization ladder, and incident re-entry passed.
- The matrix retains owner, signal, cadence, threshold, allowed observation, evidence, escalation, and remediation fields.
- A first case-sensitive marker assertion looked for lowercase `no recovery time objective` while the contract began the sentence with `No`; the case-insensitive corrected assertion passed without changing policy text.
- A later extra dashboard assertion expected compact JSON without a space after the colon; the generated dashboard used formatted JSON. The corrected representation-aware assertion passed, while the dashboard's own currentness and health checks had already remained green.
- Boundary-aware secret/private-key scanning passed.
- Final JSON, dashboard refresh and currentness, command-center health, exact task accounting, generated markers, `git diff --check`, command-center-only scope, and zero staging passed.
- Product smoke and browser suites were skipped because no product behavior changed.

## Protected And External Boundary

No database, backup, sidecar, storage inventory, financial row, `local_state/`, Fly volume, Time Machine state, transfer script, provider, or external system was opened or queried. No acquisition, integrity check, restore drill, application startup, cleanup, automation, storage selection, remediation, staging, commit, push, PR, merge, publication, delegation, or second-opinion action occurred.

The contract proves the policy boundary only. Current recovery coverage, inventory, retention, integrity, drill currency, storage, and recoverability remain protected and unverified.

## Closeout

Work block 6B and Task 2 are done locally. Phase 6 is 50% complete. Task 3 (`P6-T3`) becomes current solely as Ryan's separate 6C planning gate; Task 4 remains planned. No protected recovery work or successor execution is active.

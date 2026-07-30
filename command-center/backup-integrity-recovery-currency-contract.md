# Backup, Integrity, Restore-Drill, And Recovery-Currency Contract

Status: canonical Phase 6 Task 2 policy completed locally through work block 6B; no database, backup, sidecar, storage provider, or recovery state was inspected, so current recovery coverage remains protected and unverified

## Purpose And Authority

This contract defines the intended recovery-readiness cadence, evidence, and authorization boundaries for The Ledger. It is a policy target, not proof that a backup mechanism exists, is enabled, has retained the required recovery points, or can currently restore the application.

The protected-data boundary in [`operating-rules.md`](operating-rules.md) remains controlling:

- Personal, BFM, and LL databases and every SQLite WAL/SHM sidecar are protected;
- backup files, storage inventories, local or hosted volume contents, uploads, and temporary financial payloads are protected;
- row-level financial data, credentials, and secret-bearing paths never enter this contract, tracked logs, dashboard state, or chat reports;
- every observation, copy, integrity check, restore drill, cleanup, implementation, or live restoration requires its own exact target-specific authorization.

Ryan owns every protected recovery, storage, cost, implementation, and live-restoration decision. Codex may maintain this contract and reconcile sanitized evidence only inside a confirmed block.

## Source-Defined Constraints

Current tracked source establishes these boundaries without opening protected data:

1. `DATA_DIR` selects the database, upload, and backup root.
2. The application maintains separate `personal.sqlite`, `company.sqlite`, and `luxelegacy.sqlite` databases.
3. An entity access opens SQLite in WAL mode, initializes or migrates its database, and can synchronize category metadata.
4. Ordinary application startup can create directories, databases, WAL/SHM sidecars, and migrations. It is not an inspection method.
5. A bare copy of a `.sqlite` file is not presumed complete while committed state may remain in WAL. A future mechanism must use an application-consistent SQLite backup method or a proven quiesced snapshot boundary.

These are source-defined constraints. They do not establish current file state, process ownership, backup inventory, integrity, retention, or recoverability.

## Recovery Objectives

| Control | Intended target | Stale or alert threshold | Evidence label until separately proven |
| --- | --- | --- | --- |
| Recovery-point acquisition | One application-consistent recovery set daily | No authorized passing set within 36 hours | Protected and unverified-current |
| Logical retention | At least 14 daily, 8 weekly, and 12 monthly passing recovery sets | Any required tier is missing or would be removed without a passing replacement | Protected and unverified-current |
| Integrity verification | One passing read-only integrity verification weekly on a disposable copy | No authorized passing verification within eight days | Protected and unverified-current |
| Restore drill | One isolated passing drill per calendar quarter | No passing drill in the prior quarter or more than 100 days since the last pass | Protected and unverified-current |
| Recovery-currency review | One sanitized review monthly | No authorized review within 35 days | Protected and unverified-current |
| Event-driven review | After a migration, storage/topology change, backup-method change, recovery incident, or suspected data loss/corruption | Review has not closed before the affected recovery evidence is relied upon | `decision-needed` |

The target recovery point objective is no more than 36 hours once an approved mechanism is implemented. No recovery time objective is adopted yet. A future authorized drill must measure elapsed time to a verified ready-to-cut-over state before Ryan decides whether an RTO is supportable.

## Recovery-Set And Entity-Isolation Rules

Personal, BFM, and LL form one scheduled recovery set for cadence reporting, but they remain three isolated data domains:

- each entity has its own acquisition, artifact identity, integrity result, retention membership, and restore result;
- success for the scheduled set requires a passing outcome for all three entities;
- one entity's failure is reported as a failed set, never hidden by the other two passing;
- no entity artifact may replace, seed, merge into, or validate another entity;
- downstream Luxe Legacy behavior is not part of a backup or restore drill unless a later block explicitly authorizes it;
- reports use stable entity labels only and never expose row values, account identifiers, counterparties, balances, or secret-bearing paths.

## Application-Consistent Acquisition Contract

A future acquisition block must define all of the following before it touches a source:

1. exact environment, `DATA_DIR` boundary, entity set, owner, and authorization;
2. process ownership and whether the source is live, quiesced, or represented by an approved storage snapshot;
3. one reviewed acquisition method:
   - an SQLite-supported online backup operation that produces a consistent destination while the source is live; or
   - a proven quiesced snapshot/copy boundary that accounts for the database and relevant WAL/SHM state;
4. destination protection, access controls, retention tier, and cleanup/rollback behavior;
5. per-entity success criteria and fail-closed handling for a partial set;
6. sanitized evidence and the exact next authorization gate.

Never:

- assume copying only the `.sqlite` filename is complete;
- invoke Flask, a migration, a seed, a transfer utility, or guessed backup flags to discover state;
- checkpoint, delete, move, truncate, or clean a sidecar without exact authorization;
- call a partially acquired set current;
- remove an older passing recovery point until the replacement and retention calculation pass.

Selection and implementation of an acquisition mechanism, schedule, storage provider, encryption/key arrangement, or paid service remain separate decisions.

## Integrity-Verification Contract

Weekly integrity verification is permitted only in a separately confirmed protected-copy block:

1. identify one exact retained recovery set and prove its acquisition evidence;
2. create an access-restricted disposable verification copy without exposing originals to application startup;
3. establish the expected database/sidecar state for the selected acquisition method;
4. run an approved read-only SQLite integrity method against each disposable entity copy;
5. record only pass/fail, sanitized artifact identity, digest or metadata when authorized, schema/migration identifier, Central Time, elapsed time, and limitations;
6. perform no row browsing, export, screenshot, provider call, application mutation, migration, repair, retry, or original replacement;
7. remove the disposable verification root through the exact confirmed cleanup path and prove cleanup without listing protected contents.

An integrity pass proves only that the tested copies passed the selected SQLite check. It does not prove application usability, semantic financial correctness, freshness beyond the recorded acquisition time, or live-restoration readiness.

## Isolated Restore-Drill Contract

A quarterly restore drill requires its own protected-data block and never targets an active or original `DATA_DIR`.

The drill sequence is:

1. select one exact passing retained recovery set and freeze its evidence;
2. establish an access-restricted disposable drill root, denied external seams, synthetic/non-production configuration, and cleanup plan;
3. restore all three entity artifacts into isolated entity destinations;
4. perform an immutable/read-only integrity preflight before any application access;
5. if separately included, clone the preflighted copies again for a controlled application-readiness check because startup can create sidecars, apply pending migrations, and synchronize metadata;
6. prove entity isolation, expected schema/migration behavior, no external request, no downstream write, sanitized readiness result, and cleanup;
7. measure time from authorized drill start to the verified ready-to-cut-over state, but perform no cutover or active-original replacement;
8. remove every disposable drill artifact using the confirmed cleanup path and record sanitized cleanup proof.

The drill must stop without retry or repair on an unresolved source, sidecar state, integrity failure, schema incompatibility, entity mismatch, external request, protected-output leak, cleanup failure, or need to touch an original. Investigation, another recovery point, repair, retention change, or live restoration requires a new Ryan decision.

## Retention And Cleanup

The logical minimum is:

- 14 passing daily recovery sets;
- 8 passing weekly recovery sets;
- 12 passing monthly recovery sets.

A recovery set may satisfy more than one tier when the future mechanism records the tier assignment explicitly. Retention age is measured from the application-consistent acquisition time in Central Time, not file modification time alone.

Retention does not authorize deletion. A cleanup block must resolve the exact candidate set, prove that required newer passing sets remain in every tier, establish rollback where practical, delete only the authorized target, verify the resulting tier counts without row inspection, and stop on ambiguity. A failed, partial, quarantined, or incident-relevant set is preserved until Ryan decides its disposition.

## Recovery-Currency Review

The monthly review is evidence reconciliation, not a backup or restore action. An authorized review should determine:

1. newest passing recovery-set age and the 36-hour comparison;
2. per-entity completeness for the newest set;
3. 14/8/12 retention-tier satisfaction;
4. newest weekly integrity pass and age;
5. newest quarterly restore-drill pass and age;
6. unresolved partial sets, failures, incidents, migration/storage changes, or cleanup exceptions;
7. the evidence label, limitations, escalation state, and smallest next authorization.

Without protected evidence, report `waiting-on-Ryan`; do not guess `current`, `due`, or `stale`. With authorized evidence, a missed threshold becomes `decision-needed`. Neither state authorizes diagnosis, acquisition, integrity work, restore, cleanup, or remediation.

## Sanitized Evidence Minimum

Every authorized protected recovery record must include:

1. exact authority and bounded target labels;
2. Central Time start and completion timestamps;
3. source environment and entity labels without secret-bearing paths;
4. acquisition method class and process/sidecar disposition;
5. per-entity pass/fail and whole-set result;
6. recovery-point age and retention-tier assignment;
7. integrity or drill method, sanitized result, and elapsed time;
8. digest, size, timestamp, or schema identifier only when the block permits it;
9. cleanup result and retained-artifact disposition;
10. what the evidence does not prove;
11. escalation state and smallest next authorization gate;
12. confirmation that no diagnosis, retry, repair, replacement, or other remediation followed unless separately authorized.

Do not record row values, account or transaction identifiers, balances, merchants, payroll detail, uploads, screenshots, raw database output, storage listings, credentials, tokens, or full protected paths.

## Authorization Ladder

Each rung is separately confirmed; authority never flows automatically to the next:

1. **Policy maintenance:** tracked source and sanitized command-center work only.
2. **Protected currentness observation:** exact metadata/inventory evidence only.
3. **Recovery-point acquisition:** exact source, method, destination, and retention terms.
4. **Disposable integrity verification:** exact recovery point and cleanup boundary.
5. **Isolated restore drill:** exact disposable root, stages, denial seams, and cleanup.
6. **Live restoration or replacement:** exact active target, rollback, outage, owner, and postflight plan.
7. **Retention cleanup:** exact candidates and remaining-tier proof.

A passing earlier rung is prerequisite evidence, not authorization for a later rung.

## Incident Re-entry

On suspected corruption, accidental reseed, data loss, failed migration, or recovery-point mismatch:

1. stop application and utility activity;
2. freeze originals and relevant sidecar/process state;
3. perform no cleanup, checkpoint, migration, seed, transfer, or retry;
4. preserve existing recovery evidence;
5. define the exact protected assessment block;
6. use disposable copies for integrity or application proof;
7. require a separate decision before any original replacement or live restoration.

Historical recovery success does not override these incident gates.

## 6B Boundary

Work block 6B establishes this contract from tracked source and sanitized historical evidence only. It performs no protected observation, acquisition, integrity check, restore drill, cleanup, application startup, storage selection, automation, Git publication, or external action. Current recovery coverage therefore remains protected and unverified.

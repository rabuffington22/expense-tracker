# 5G-RC Immediate Personal/BFM Snapshot Recovery

Date: 2026-07-27

Status: complete and verified locally

## Authorized Scope

Recover only the Personal and BFM local SQLite database sets from exact pre-incident local Time Machine snapshot `com.apple.TimeMachine.2026-07-27-071321.local`. Preserve an exact protected post-incident safety copy, use only read-only snapshot access, verify integrity, replace only the exact current targets, prove restored equality and aggregate recovery, clean temporary access, and stop before application access or 5G resume.

## Recovery Result

- No expense-tracker process owned either database before replacement.
- The post-incident files were copied byte-for-byte to protected directory `local_state/backups/5g-recovery-20260727-0753-post-seed/`.
- The Time Machine interface mounted exact snapshot `com.apple.TimeMachine.2026-07-27-071321.local` as protected read-only APFS source `Data@snap-79315582`.
- The exact snapshot `local_state` contained `personal.sqlite` and `company.sqlite` without matching Personal/BFM WAL or SHM sidecars.
- Finder copied those two protected snapshot files into the protected `snapshot-staging/` subdirectory.
- Both staged snapshot files differed from their post-seed safety copies and passed SQLite `PRAGMA integrity_check` using immutable read access.
- Exact same-directory temporary replacements were verified before atomic rename.
- Restored `local_state/personal.sqlite` matches staged snapshot SHA-256 `deab1ed17a3512b0ac649aeff87188886a0cecb2afb27ca2ce078c3c7d329abb` and passes integrity.
- Restored `local_state/company.sqlite` matches staged snapshot SHA-256 `796308efdf4bb44cc7f35286b1b44cd4d97a6d049b978c6e757f0f73cd99cc60` and passes integrity.
- Both restored files retain user/group `502:20`, mode `0644`, and their snapshot modification times.

## Aggregate Recovery Proof

Personal:

- transactions: 691
- account balances: 11
- manual recurring: 0
- categories: 35
- subcategories: 92
- planning items: 8
- budget items: 30
- action items: 5
- goal snapshots: 10
- short-term goals: 3

BFM:

- transactions: 1,303
- account balances: 2
- manual recurring: 0
- categories: 36
- subcategories: 67
- planning items: 2
- budget items: 27
- action items: 0
- goal snapshots: 0
- short-term goals: 0

The recovered transaction counts exactly match the pre-seed counts reported at the 5G stop.

## Cleanup And Boundaries

- The exact `2026-07-27-071321` recovery snapshot mount was unmounted successfully without force.
- Time Machine mounted other local snapshots while its browser was open. Twenty-one released without force; four unrelated older protected read-only mounts remained system-busy and were left to macOS rather than force-unmounted.
- Finder recovery windows were closed.
- The exact temporary replacement files are absent.
- The post-incident safety copies and recovered snapshot staging copies remain protected under the recovery backup directory.
- No application access, migration, seed, sync, Luxe Legacy action, 5G resume, staging, commit, GitHub, workflow, deployment, production, or live action occurred.

## Next Gate

The Personal and BFM data is recovered locally. Application-level verification and any 5G product-work resume remain separate exact gates because opening the Flask application may create SQLite sidecars or apply migrations.

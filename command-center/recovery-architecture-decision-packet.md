# Recovery Architecture Decision Packet

Date: 2026-07-30

Status: accepted by Ryan; implementation remains separately gated

## Accepted Architecture

1. Use daily SQLite Online Backup full sets as the primary recovery mechanism.
   Keep Litestream parked.
2. Use Backblaze B2 as the independent recovery target, subject to exact
   synthetic capability proof before production activation.
3. Encrypt each recovery set before upload for two independent `age`
   recipients. Keep the two recovery identities under separate custody chains
   outside Fly.
4. Recompute logical daily, weekly, and monthly roles using the
   America/Chicago calendar. Preserve 14 daily, 8 weekly, and 12 monthly
   logical recovery points. Treat Object Lock as a padded minimum floor, not as
   the logical-retention calculator.
5. Prefer Object Lock compliance mode only after governance-mode synthetic
   proof. Set exact padding values only after that proof.
6. Keep `/data/uploads/` outside the database recovery set. Any upload archive
   is a separate future decision.
7. Permit a separately proposed Task 3 implementation block. It must first
   select and prove a wake-capable acquisition trigger and reproduce the exact
   B2 least-privilege capability model with synthetic data.

## Recovery-Set Contract

Each successful acquisition is one complete, entity-isolated set containing
application-consistent copies of:

- Personal: `personal.sqlite`
- BFM: `company.sqlite`
- LL: `luxelegacy.sqlite`

The acquisition must use SQLite Online Backup semantics, run acquisition-side
integrity checks, verify available space, avoid the existing Plaid schedule,
encrypt before network transmission, and publish a manifest only after the
complete set is ready. A partial set is not current recovery evidence.

## Authority Separation

The production design uses separate principals:

1. uploader: upload only, with the accepted B2 caveat that `writeFiles` also
   permits hide-by-name and therefore requires independent version observation;
2. freshness observer: off-Fly metadata-only observation;
3. restore reader: separately custodied read/decrypt path;
4. retention and cleanup: privileged extension/deletion path.

The uploader must not have delete, legal-hold, retention-write, bucket-policy,
or bypass authority. The recommended B2 shape is a bucket-default immutable
floor plus a separately custodied principal that may extend weekly and monthly
objects. Cleanup requires both lock expiry and a current proof that the object
has no remaining logical role.

## Trigger And Observation Constraints

The Fly configuration may stop every Machine and keep zero Machines running.
Task 3 therefore must select a trigger that wakes or coincides with an
application Machine; an in-process timer alone is insufficient. Freshness
observation must run independently off Fly so the backup system cannot silently
fail with the application.

## Independent Review

The direct Claude CLI review ran with model `claude-fable-5`, effort `max`,
read-only tools, plan permission, safe mode, no session persistence, and no
fallback. The verdict was **approve with corrections**.

Accepted corrections:

- separate logical retention from Object Lock;
- separate uploader authority from retention authority;
- require a wake-capable trigger and an off-Fly freshness observer;
- require manifest lock parity and acquisition-window consistency;
- make uploads and legacy `backups/` scope explicit;
- add space, integrity, and schedule preflights;
- use four separate principals and two recovery recipients;
- retain Amazon S3 as the fallback if B2 cannot reproduce the required
  least-privilege model.

## Authorization Boundary

Ryan's acceptance selects the architecture and authorizes a separate Task 3
proposal only. It does not authorize provider setup or purchase, credentials,
bucket or key creation, Fly or production access, protected inventory,
database/backup/upload access, implementation, acquisition, upload, retention
mutation, cleanup, integrity execution, restore, publication, Git release, or
Tasks 4-7.

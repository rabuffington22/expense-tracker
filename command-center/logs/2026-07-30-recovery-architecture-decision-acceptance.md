# Recovery Architecture Decision Acceptance

Date: 2026-07-30 5:52 PM CDT

Status: accepted; no implementation activated

Ryan confirmed all seven reviewed architecture decisions and allowed Codex to
prepare a separate Task 3 proposal.

Accepted:

- SQLite Online Backup full sets; Litestream parked;
- Backblaze B2, subject to synthetic capability proof;
- two independently custodied `age` recipients;
- America/Chicago logical 14/8/12 retention separate from Object Lock;
- compliance mode only after governance-mode synthetic proof;
- uploads excluded from the database recovery set;
- a separate Task 3 proposal that begins with wake-capable trigger selection
  and exact B2 least-privilege proof.

This acceptance closes Phase 7 Task 2. It does not activate Task 3 and does not
authorize provider, credential, Fly, production, protected-data, database,
backup, upload, implementation, retention, cleanup, restore, publication, Git,
or successor action.

The prior isolated worktree containing the completed 7B closeout was removed
between tasks before those local changes were committed. Codex reconstructed
the sanitized reviewed decision state from the completed review output and
Ryan's confirmation without repeating any external or protected action.

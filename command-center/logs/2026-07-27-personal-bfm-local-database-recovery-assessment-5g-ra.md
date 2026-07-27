# 5G-RA Personal/BFM Local-Database Recovery Assessment

Date: 2026-07-27

Status: stopped safely at the non-privileged read-only mount boundary

## Authorized Scope

Assess only whether the exact pre-incident local Time Machine snapshot `com.apple.TimeMachine.2026-07-27-071321.local` contains intact Personal and BFM database files. Read-only snapshot metadata, an exact non-privileged read-only temporary mount, exact file metadata, and SQLite `PRAGMA integrity_check` were permitted. Copy, restore, replacement, row queries, application access, 5G resume, Git publication, and live action were excluded.

## Sanitized Result

- `tmutil` and APFS metadata both confirmed the exact snapshot exists on the Data volume.
- Snapshot UUID: `B0AB8CCC-80CA-4A76-970F-DB1279B16571`.
- Snapshot XID: `79315582`.
- Data volume device: `/dev/disk3s5`.
- Current post-incident files were unchanged before and after the assessment:
  - Personal: 1,105,920 bytes; modification time `2026-07-27 07:31:52 CDT`.
  - BFM: 974,848 bytes; modification time `2026-07-27 07:31:52 CDT`.
- One exact `mount_apfs` attempt specified `rdonly,nobrowse`, the exact snapshot name, the exact Data-volume device, and a disposable `mktemp` path.
- macOS rejected the mount with `Operation not permitted` and exit code 77.
- The failed mount created no mounted snapshot. Its empty temporary directory was removed.
- No already-mounted local-snapshot path was available under the standard local snapshot locations.
- Because the confirmed stop conditions prohibit `sudo`, administrator authentication, or privilege escalation, no snapshot file presence, file metadata, or SQLite integrity check occurred.
- All three preserved unrelated files retained their pre-assessment SHA-256 values.
- The real Git index remained empty.

## Boundary And Next Gate

5G-RA establishes that the exact pre-incident APFS snapshot still exists, but it does not establish that the Personal or BFM database files are present or intact. A separately confirmed privileged read-only assessment would be required to mount the exact snapshot and complete file metadata and integrity checks. Copy, restore, replacement, row access, application access, and 5G resume remain later and separate gates.

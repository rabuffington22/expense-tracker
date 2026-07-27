# Work Block 5G Stop — Protected Local-Data Boundary

Date: 2026-07-27\
Time: approximately 07:31 CDT\
Work block: 5G Recurring Review And Cancellation Clarity\
Task: 2.4 (`P5-T24`)\
Status: stopped before rendered inspection or local closeout

## Stop

After the confirmed local-only implementation and its synthetic verification, Codex invoked:

```text
.venv/bin/python scripts/seed_demo_data.py --help
```

The script does not implement a help parser. Import-time configuration retained its default `DATA_DIR=./local_state`, and the main routine executed immediately. Its sanitized terminal output reported:

- Personal: 691 existing transactions wiped, then synthetic demo data seeded.
- BFM: 1,303 existing transactions wiped, then synthetic demo data seeded.

Tracked source inspection confirms the utility deletes and reseeds more than transactions. For Personal and BFM it deletes transactions, account balances, manual recurring rows, categories, subcategories, planning items, budget items, action items, goal snapshots, and short-term goals, then writes the deterministic synthetic demo set. Luxe Legacy was not selected by the script and its database modification time remained unchanged.

This violated the confirmed protected-data and local-database boundary. Work block 5G stopped immediately. No attempt was made to repair, restore, copy, move, inspect row contents, or continue rendered testing.

## Recovery Posture

- `local_state/backups/` contains no files.
- The only Personal and BFM database files found inside the repo are the now-modified `local_state/personal.sqlite` and `local_state/company.sqlite`.
- Their filesystem modification times are `2026-07-27 07:31:52 CDT`.
- macOS reports a local Time Machine snapshot `com.apple.TimeMachine.2026-07-27-071321.local`, created before the destructive seed invocation.
- That snapshot is a promising recovery candidate but has not been mounted, inspected, copied, or restored.
- Any backup verification, preservation of the post-seed files, file replacement, SQLite recovery attempt, or Time Machine restore requires Ryan's exact authorization.

## Product Work Before The Stop

- Active 5G Runway OS state was written and passed JSON validation, dashboard refresh, health check, and whitespace verification.
- Local branch `codex/recurring-review-surface` was created.
- The Recurring Review implementation and focused all-entity synthetic coverage were written locally.
- Baseline and final full smoke passed.
- The complete configured-auth/no-password installed-Chrome suite passed with denied non-localhost networking and exact temporary-data cleanup.
- Rendered visual inspection and final local closeout did not occur.
- Product and command-center changes remain unstaged, uncommitted, and unpublished.
- GitHub, workflows, Fly, production, Plaid, downstream systems, and the three preserved unrelated files were not touched.

## Exact Stop

Freeze `local_state/personal.sqlite` and `local_state/company.sqlite` in their current post-seed state. Do not run the application, seed utility, database migrations, smoke tests with `DATA_DIR=./local_state`, sync utilities, backup utilities, or recovery commands against those files. Ryan must choose the exact recovery path before 5G can resume.

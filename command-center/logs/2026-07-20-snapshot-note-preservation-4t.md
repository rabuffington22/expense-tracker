# Work Block 4T Closeout — Snapshot Note Preservation

Date: 2026-07-20

Status: complete and locally verified; release not authorized

## Scope

Implement Phase 4 Task 1N.2 for `P3-3D-03` plus only its focused Task 2 / `P3-3D-C01` regression slice. Preserve same-day goal-snapshot identity and manual notes during automatic balance refresh while keeping manual review authoritative for intentional note replacement.

Excluded throughout: Tasks 1N.3-1N.8; Tasks 1O-1P; broader Task 2; Tasks 3-4; migrations; historical cleanup; demo seeding; UI redesign; real financial data or databases; retained uploads; credentials; production/demo; external calls; live systems; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

## Result

- Automatic same-day conflicts update only `balance_cents`; the existing snapshot `id`, `created_at`, and `note` remain unchanged.
- Manual same-day conflicts update `balance_cents` and the normalized note while preserving `id` and `created_at`.
- A whitespace-only manual note remains empty and leaves monthly review due. A later non-empty manual review intentionally replaces it.
- A new month inserts a separate snapshot and leaves the earlier balance, identity, creation time, and manual note intact.
- No migration or template change was required.

## Verification

- Baseline maintained `.venv/bin/python scripts/smoke_test.py`: pass.
- Final maintained `.venv/bin/python scripts/smoke_test.py`: pass, including new 8a3 coverage for Personal and BFM automatic/manual/repeated-auto ordering, intentional replacement, empty-note review state, identity stability, month transition, Luxe Legacy denial, denied networking, and exact cleanup.
- `.venv/bin/python -m py_compile web/routes/short_term_planning.py scripts/smoke_test.py`: pass.
- JSON validation, `git diff --check`, dashboard refresh, command-center health, generated-dashboard inspection, and final worktree scope: pass at closeout.

## Boundaries Preserved

No real financial data, retained upload, credential, production/demo, Plaid, OpenRouter, workflow, Fly, downstream, external-system, or live action was used. No commit, push, PR, merge, or deployment occurred. Both pre-existing untracked files remained untouched and unstaged.

## Next Gate

Publication requires a separately confirmed 4T-R durability and release block. If 4T stays local-only, the next planning pass may size Task 1N.3 as 4U.

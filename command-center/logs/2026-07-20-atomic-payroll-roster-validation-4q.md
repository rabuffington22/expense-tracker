# Work Block 4Q — Atomic Payroll Roster Validation

Date: 2026-07-20

Status: complete and verified locally on `codex/atomic-payroll-roster-validation`

## Scope

Completed Task 1M.4 for `P3-3F-04` and only its focused `P3-3F-C01` coverage slice. Task 1M.5, broader regression work, protected data, retained uploads, migrations, live systems, GitHub durability, and deployment remained excluded.

## Result

- One shared validator now governs manual create, manual update, and import-created employee rows.
- Names, maintained roles, pay types, statuses, exact optional dates, entity-local employee assignments, payload-linked imported names, optional Phoenix codes, and bounded decimal pay rates are validated before mutation.
- Empty rates remain zero; future hire dates remain accepted; valid currency input uses deterministic decimal-cent rounding.
- Invalid submissions return controlled sanitized feedback and preserve all payroll rows.
- Manual rate-history creation and employee update are explicitly rolled back together after a forced post-history failure.
- Import assignments are fully validated before inserts. A forced payroll-entry failure rolls back the newly inserted employee and all batch rows.
- Import payloads retain the one-use 4P lifecycle and are removed after rejected saves.
- No migration, template, or `core/db.py` change was required.

## Verification

- Baseline maintained `.venv/bin/python scripts/smoke_test.py`: pass.
- Final maintained `.venv/bin/python scripts/smoke_test.py`: pass.
- Manual create rejection matrix: empty name, undefined role, invalid pay type, NaN, infinity, negative rate, maximum overflow, extreme exponent, and impossible date all return controlled feedback with exact zero mutation.
- Manual update matrix: invalid role, pay type, rate, status, date, and missing employee ID preserve the full payroll-table snapshot.
- Valid behavior: surrounding whitespace, optional Phoenix code, future date, decimal half-up cents, empty rate, positive-to-positive history, and zero-to-positive no-history behavior pass.
- Import behavior: invalid role, forged payload-external assignment name, duplicate normalized assignment, nonexistent employee ID, one-use rejected payload cleanup, and forced post-employee payroll-entry rollback pass.
- Existing BFM-only all-route coverage preserves Personal and Luxe Legacy state. Focused networking was denied and no external call occurred.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, command-center health, rendered-dashboard inspection, and explicit worktree review pass at closeout.

## Boundaries Preserved

No real payroll, HR, financial, credential, upload, production, demo, Plaid, OpenRouter, workflow, Fly, downstream, or external-system data or action was used. No commit, push, PR, merge, or deployment occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.

## Next

Publication of 4Q remains separately gated. If Ryan authorizes durability, the recommended next block is 4Q-R for exact-path publication, automatic deployment observation, and credential-free production health. Task 1M.5 remains a later separately planned compensation-comparison block.

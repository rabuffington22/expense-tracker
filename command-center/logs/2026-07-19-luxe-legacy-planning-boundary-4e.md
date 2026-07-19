# Work Block 4E: Luxe Legacy Planning Boundary

Date: 2026-07-19

Status: complete and locally verified; release not authorized

## Scope

Implement Phase 4 Task 1D for `P3-3D-02` plus only the planning-boundary slice of Task 2 / `P3-3D-C01`. Enforce the existing Luxe Legacy dashboard redirect before every Long-Term and Short-Term Planning handler and add focused maintained synthetic coverage.

Excluded throughout: Tasks 1E-1P and 3-4; broader planning coverage and demo seeding; APR, snapshot, depreciation, Weekly, and Waterfall repairs; templates and migrations; real databases or financial/payroll/HR rows; uploads; credentials; production/demo access; Plaid, Fly, workflows, downstream writes, external or live actions; GitHub durability and deployment; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Implementation

- Added one `before_request` Luxe Legacy denial guard to `web/routes/planning.py`.
- Added one `before_request` Luxe Legacy denial guard to `web/routes/short_term_planning.py`.
- Removed the two now-redundant index-only checks.
- Added maintained coverage in `scripts/smoke_test.py` that enumerates all 21 registered route rules and exercises each allowed GET or POST method with the LL entity selected.

## Verification

- The unchanged baseline `.venv/bin/python scripts/smoke_test.py` passed before product or test edits.
- The final `.venv/bin/python scripts/smoke_test.py` passed every section, including the new planning boundary, existing payroll boundary, CSV exports, saved views, To Do, and authentication/cache checks.
- Every planning view function was temporarily replaced with a fail-fast sentinel during LL requests; all 21 requests redirected before a handler could execute.
- Logical before/after dumps of temporary Personal, BFM, and Luxe Legacy databases were identical across the denied-request pass.
- Denied responses contained neither synthetic Personal nor BFM account names.
- Personal and BFM Long-Term pages rendered both synthetic entity sections; their own account helpers and Short-Term pages remained available.
- Python compilation passed for both planning route modules and the maintained smoke script.
- The final smoke temporary directory was removed, `jq empty command-center/state.json` passed, and `git diff --check` passed.
- Dashboard refresh and command-center health passed after source/state closeout.

## Boundaries Preserved

- No template or migration changed.
- No real database, financial/payroll/HR row, upload, credential, production/demo surface, external integration, workflow, Fly surface, or downstream system was accessed or changed.
- No commit, push, PR, merge, deployment, or live action occurred.
- `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Learning

The planning isolation defect came from guard placement, not from the underlying planning data model: both index pages already expressed the correct LL policy, but 19 supporting routes bypassed it. Moving the same policy to the two blueprint boundaries closes the hidden read and mutation paths without changing Personal/BFM sharing or any planning calculation. The remaining planning work can now focus on calculation and lifecycle correctness without carrying an unresolved entity-boundary risk.

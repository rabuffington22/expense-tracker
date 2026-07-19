# Work Block 4D: BFM-Only Payroll Boundary

Date: 2026-07-19

Status: complete and locally verified; release not authorized

## Scope

Implement Phase 4 Task 1C and only the payroll-boundary slice of Task 2 for `P3-3F-01` and `P3-3F-C01`.

Excluded throughout: Tasks 1D-1P and 3-4; remaining payroll matching, compensation, validation, malformed-workbook, parser, and temporary-retention repairs; migrations and templates; real databases, payroll/HR/financial rows, uploads, credentials, production/demo access, Plaid, Fly, workflows, downstream writes, external calls, GitHub durability, deployment, and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Implementation

- Added one payroll-blueprint `before_request` guard in `web/routes/payroll.py`.
- The guard redirects any entity other than BFM's `company` database key to the dashboard before a payroll route handler runs.
- No route handler, parser, template, database schema, or payroll calculation changed.
- Added maintained synthetic coverage in `scripts/smoke_test.py` that fails if the registered payroll route inventory changes without matching boundary coverage.

## Verification

- Untouched baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass.
- Python compilation for `web/routes/payroll.py` and `scripts/smoke_test.py`: pass.
- All eight registered payroll routes are enumerated in maintained coverage.
- Personal and Luxe Legacy each produced eight dashboard redirects, for sixteen denied route outcomes total.
- Patched storage and parser seams proved no denied route handler reached payroll storage or upload parsing.
- Employee, employee-pay-change, and payroll-entry counts plus sentinel employee values remained unchanged for both denied entities.
- Denied import-save requests preserved their exact synthetic temporary payloads.
- BFM index, create, update, delete, detail, import parse, import save, and spending paths remained available; the synthetic employee and temp payload were removed.
- Smoke-created temporary database roots were removed automatically, and exact 4D temporary payload paths were absent after verification.
- `git diff --check`, command-center dashboard refresh, and command-center health check passed.

## Result

`P3-3F-01` is resolved locally. The visible BFM-only product promise is now enforced at the shared payroll blueprint instead of relying on hidden navigation. The boundary portion of `P3-3F-C01` is maintained; the remaining payroll lifecycle coverage stays paired with Task 1M.

## Boundaries Preserved

- No real payroll, HR, financial, upload, credential, production, demo, Plaid, Fly, workflow, or downstream surface was accessed or changed.
- No migration, template, parser behavior, employee validation, compensation logic, matching behavior, or temporary-retention policy changed.
- No commit, push, PR, merge, deployment, workflow dispatch, or other live action occurred.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Learning

The payroll access defect was genuinely centralized: every current payroll route shares one blueprint, so one pre-handler guard closes the Personal and Luxe Legacy exposure without disturbing BFM behavior. The remaining payroll defects are not boundary problems and should stay together in the later Task 1M integrity block rather than being pulled into this repair.

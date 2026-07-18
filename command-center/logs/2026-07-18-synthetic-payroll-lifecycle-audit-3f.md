# Work Block 3F: Synthetic Payroll Lifecycle Audit

Date: 2026-07-18

Status: complete; findings recorded; direct-main durability authorized separately

## Scope

Audit Phase 3 Task 4D as one synthetic-only pass over employee roster and pay history, Phoenix/CyberPayroll XLSX parsing and preview/save, re-import behavior, temporary-payload lifecycle, role and employee spending aggregation, and the maintained BFM-only access boundary.

Excluded throughout: completed Tasks 1-3 and 4A-4C; Tasks 5-8; all 3A-3E repairs; product repairs and migrations; tracked test, fixture, or demo changes; real payroll, HR, financial, upload, or credential data; production/demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication/security changes; GitHub durability; and the pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Verification

- `.venv/bin/python scripts/smoke_test.py` passed its temporary-`DATA_DIR` initialization, import, isolation, route, export, saved-view, and To Do checks.
- A 40-check primary payroll probe passed 35 checks and produced five controlled failures representing four defect clusters plus one tracked-coverage gap.
- A focused seven-check confirmation probe passed its cleanup control and reproduced six controlled failures. It confirmed the matched-preview duplicate behavior and added malformed-upload plus direct employee-input validation evidence.
- Across both probes, 36 of 47 assertions passed. Eleven controlled failures collapse into six functional or privacy defect clusters plus one regression-coverage gap.
- The malformed XLSX, invalid pay type, and non-finite pay-rate exceptions were intentionally caught and classified; no exception escaped the audit harness.
- Temporary synthetic databases, generated XLSX files, and audit-created temporary payroll payloads were removed when the probes exited.
- No tracked application, fixture, test, demo, workflow, or deployment file changed.
- After the audit and local verification completed, Ryan separately authorized publishing the exact seven-path command-center closeout directly to `main` with `[skip actions]` so this command-center-only push does not start the production Fly deployment workflow.

## Behavior Matrix

| Surface | Result | Evidence |
| --- | --- | --- |
| Phoenix multi-section parsing | Pass | A generated workbook produced five entries across 2025 and 2026 with normalized dates and exact employer-cost amounts. |
| Role suggestions and unmatched codes | Pass | Maintained provider and nurse codes mapped correctly; an unknown code remained explicitly unmatched. |
| Parser deduplication and headerless workbook | Pass | A repeated employee/date row produced a warning and no duplicate; a valid workbook without a Phoenix header returned a controlled warning/error page. |
| BFM roster CRUD and pay history | Pass | Create, update, detail JSON, rate-change history, status fields, and persisted cents reconciled in the temporary BFM database. |
| Employee delete cascades | Pass | Deleting a synthetic employee removed the roster row, pay-change history, and payroll entries. |
| Peer compensation comparison | Defect | One hourly and one annual-salary provider were averaged as raw cents; the hourly employee received a displayed peer rate derived from incompatible units. |
| Existing-employee preview assignment | Defect | The rendered preview offered `Create new employee` for an exact same-name roster match; submitting the default form created a duplicate employee and assigned the payroll entry to it. |
| Explicit import save and re-import | Pass | Explicit assignments created the intended new employee, persisted five unique employee/date rows, reconciled three pay-period totals, consumed the temp payload, and left row counts unchanged on re-import. |
| Role-spending page and HTMX partial | Pass | Provider, nurse, employee, and grand totals reconciled for the selected paycheck date. |
| Successful-save temporary payload | Pass | Each saved import consumed its JSON payload immediately. |
| Canceled-preview temporary payload | Defect | Navigating back from preview left the parsed employee, date, amount, and filename payload on disk until the general age-based cleanup runs. |
| Malformed XLSX handling | Defect | Non-XLSX bytes carrying an `.xlsx` name raised `ValueError` instead of returning a controlled import error. |
| Maintained role and form validation | Defect | A direct request persisted an undefined role; invalid pay type raised `IntegrityError`; a non-finite pay rate raised `OverflowError`. |
| BFM-only access boundary | Defect | Personal and Luxe Legacy direct payroll reads returned 200 and direct employee creates returned 302 with rows persisted in those entity databases. BFM itself was not cross-mutated. |
| Three-entity storage isolation | Pass | Valid BFM actions did not alter Personal or Luxe Legacy; non-BFM direct actions remained isolated to their own temporary databases. |
| Maintained regression coverage | Gap | `scripts/smoke_test.py` contains no dedicated payroll parser, roster, import, aggregation, cleanup, or access-boundary cases. |

## Ranked Findings

1. High: Personal and Luxe Legacy can directly read and mutate entity-local payroll data even though Payroll is maintained and navigated as BFM-only.
2. High: the preview fails to retain an exact existing-employee match and the default save path creates a duplicate roster employee.
3. High: peer compensation averages combine hourly and annual salary rates and can display materially meaningless comparisons.
4. Medium: employee CRUD inputs are not normalized consistently; undefined roles persist while invalid pay type and non-finite rate inputs raise controlled audit exceptions.
5. Medium: canceling a payroll preview retains its parsed payroll payload until age-based cleanup instead of removing it immediately.
6. Medium: malformed XLSX uploads do not return the controlled error state that valid headerless workbooks use.
7. Medium: payroll lifecycle and boundary behavior lacks tracked regression coverage.

## Acceptance Checks

- Every payroll route and mutation enforces the documented BFM-only boundary before opening or changing payroll tables; Personal and Luxe Legacy direct requests leave all payroll tables unchanged.
- Exact matched employees render a stable existing assignment, and the default preview/save path cannot create a duplicate same-name roster record.
- Peer comparisons group by both role and pay type or normalize rates to a documented common unit; hourly and salary displays reconcile to that unit.
- Employee roles and pay types are validated against maintained domains, pay rates must be finite and non-negative, and invalid requests preserve prior data with a controlled response.
- Malformed, headerless, empty, and valid multi-section workbooks return explicit controlled outcomes without unhandled route errors.
- Cancel, save, expired, missing, and reused temporary keys have explicit cleanup behavior; audit-created payloads contain no longer-lived data than necessary.
- Tracked synthetic tests cover parser, roster/history, preview/save, duplicate import, role aggregation, cleanup, and Personal/BFM/LL boundaries, including each repaired defect.

## Boundaries Preserved

- No real payroll, HR, financial, upload, credential, production, demo, Plaid, OpenRouter, Fly, workflow, downstream, or authentication surface was accessed or changed.
- All employee names, dates, rates, amounts, XLSX files, and database rows were deterministic synthetic values inside disposable temporary directories.
- No application repair, migration, tracked regression coverage, fixture, or demo change was implemented.
- The exact seven-path command-center closeout was published directly to `main` under Ryan's separate authorization with `[skip actions]`; no PR, merge, or deployment occurred.
- The pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Learning

The core BFM payroll calculations and explicit import persistence reconcile correctly, but trust breaks at the boundaries around them. The preview can duplicate matched employees, compensation comparisons mix incompatible units, and route-level controls do not enforce the product's BFM-only promise. Phase 4 should treat those three high-risk defects as one payroll-integrity repair family, while Task 5 can proceed independently under a separate synthetic and mocked integration block.

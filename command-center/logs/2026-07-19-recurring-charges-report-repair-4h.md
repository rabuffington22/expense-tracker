# Work Block 4H — Recurring Charges Report Repair

Date: 2026-07-19

Status: complete and verified locally; release not authorized

## Confirmed Scope

Phase 4 Task 1G plus only the recurring-report slice of Task 2, limited to `P3-3C-01` and focused `P3-3C-C01` coverage.

## Failing-Before Proof

The new maintained all-entity regression reached the direct helper and reproduced SQLite `unrecognized token: "{"` because the query contained a literal exclusion-helper token. The run stopped before prepared, rendered, CSV, or PDF checks, matching the Phase 3 finding.

## Repair

- Build the query with the maintained entity-specific exclusion contract.
- Keep recurring detection on raw bank transactions rather than split allocations.
- Correct negative-debit summary ordering so minimum is the smaller absolute charge and maximum is the larger.
- Preserve existing merchant, average, date, category, presentation, and filename contracts.

## Maintained Coverage

Temporary Personal, BFM, and Luxe Legacy databases now verify:

- direct helper, prepared report, rendered HTMX view, CSV, and PDF paths;
- repeated-merchant count, average, minimum, maximum, first date, last date, and category;
- Personal, BFM, and Luxe Legacy exclusion contracts, including eligible LL `Owner Draw` and excluded BFM `Owner Contribution` and `Partner Buyout`;
- empty and out-of-range results plus missing-range responses;
- unchanged logical databases after every read path; and
- exact removal of every synthetic 4H row.

## Verification

- Baseline maintained smoke suite: pass before product changes.
- Failing-before focused regression: reproduced the exact literal-token defect.
- Final maintained smoke suite: pass, including the new all-entity 4H section.
- Python compilation for `core/reporting.py`, `scripts/smoke_test.py`, and `web/routes/reports.py`: pass.
- `jq empty command-center/state.json`: pass.
- `git diff --check`: pass before closeout.
- Temporary synthetic test root: removed by the maintained suite; no real database was read or changed.

## Boundaries Preserved

No real financial, payroll, HR, upload, credential, production, demo, Plaid, workflow, Fly, downstream, or external-system access occurred. No migration, category, template, subscription, cash-flow, broad reporting, split-transaction, or live behavior changed. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched. Commit, push, PR, merge, deployment, and 4H-R remain separate gates.

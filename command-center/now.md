# Current Focus

## Active Objective

Prepare the next bounded Phase 3 payroll audit block after completing the synthetic Weekly and Waterfall audit.

## Current Phase

Phase 3: Functional Audit And Prioritization — active.

## Completed Work Block

3E: Synthetic Weekly and Waterfall Audit — complete and verified locally with three high financial-output defects, three medium functional defects, and one medium regression-coverage gap.

## Current Task

Phase 3 Task 4D: audit payroll roster, Phoenix/CyberPayroll import, and role spending — awaiting just-in-time work-block planning and separate confirmation.

## Owner

Ryan owns confirmation or revision of the next Phase 3 audit block and later repair prioritization. Codex Desktop owns the verified 3E evidence, protected-data boundaries, dashboard currency, and Task 4D just-in-time planning pass.

## Audit Result

The tracked smoke suite passed. The 58-check primary 3E probe, corrected for three harness expectations, and a focused ten-check confirmation probe produced six functional defect clusters and one tracked-coverage gap without unexpected runtime errors.

Weekly historical views mix selected and current dates, credit-card bills use full balances instead of scheduled payments, and Waterfall excludes deficit months from the payoff average. Invalid paydown dates can break Weekly, sub-month payoff estimates can report zero months, and Waterfall tax fallback/input handling is inconsistent.

Current-period effective spending, exclusions, valid pace and target math, bill-source assembly, paydown pace, BFM payroll dates, empty states, actual and target waterfall reconciliation, historical series, intended Personal/BFM sharing, LL denial, read-only preservation, and temporary cleanup passed. Weekly and Waterfall still lack dedicated tracked regression coverage.

## Durability

- Work block 3E and its findings are published directly to `main` under Ryan's separate durability authorization using `[skip actions]`.
- No application, fixture, tracked test, or demo-seed file changed.
- No production, demo, Plaid, OpenRouter, workflow, Fly, credential, payroll/HR, balance, or financial-data access occurred.
- Preserved user file: untracked `scripts/sync_prod_to_local.sh`, untouched and unstaged.

## Current Action

Run a just-in-time planning pass over Task 4D and propose a synthetic-first work block 3F before auditing payroll roster, import, or role-spending behavior.

## Phase 3 Boundary

- Work block 3E is complete; it does not authorize any repair, migration, tracked regression-test, fixture, or demo-seed implementation.
- Task 4D audit execution requires its own confirmed work block because payroll roster/import behavior has a separate XLSX, temporary-upload, and HR-data-boundary verification path.
- Production/demo access, Plaid/OpenRouter calls, workflow action, Fly or downstream action, application change, tracked test expansion, and any further GitHub durability remain excluded until separately authorized.
- The 3D planning findings are inputs to Phase 4 prioritization, not automatically authorized fixes.

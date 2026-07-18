# Current Focus

## Active Objective

Prepare the next bounded Phase 3 audit block after completing the synthetic financial read-model audit.

## Current Phase

Phase 3: Functional Audit And Prioritization — active.

## Completed Work Block

3C: Synthetic Financial Read-Model Audit — complete and verified locally with one medium functional-availability defect and one medium regression-coverage gap.

## Current Task

Phase 3 Task 4: audit planning, weekly, waterfall, and payroll workflows — awaiting just-in-time work-block planning and separate confirmation.

## Owner

Ryan owns confirmation or revision of the next Phase 3 audit block and later repair prioritization. Codex Desktop owns the verified 3C evidence, dashboard currency, and Task 4 just-in-time planning pass.

## Audit Result

The tracked smoke suite passed. The final ephemeral 3C probe ran 306 checks with 297 passes, zero assertion failures, and nine controlled errors representing the same Recurring Charges report defect at direct-query, prepared-report, and rendered-route layers across all three entities.

Dashboard reconciliation, effective split replacement, entity exclusions, account/date filters, all other report views, CSV/PDF/QBO exports, subscription lifecycle, cash-flow balances and projections, intended Personal/BFM shared visibility, Luxe Legacy isolation, and temporary-data cleanup passed.

The Recurring Charges report cannot run because `core/reporting.py` sends the literal token `{exclude_sql('category')}` to SQLite. The broader Task 3 paths also lack tracked regression coverage.

## Durability

- Work block 3C and its findings are published directly to `main` under Ryan's separate durability authorization using `[skip actions]`.
- No application, fixture, or tracked test file changed.
- No production, demo, Plaid, OpenRouter, workflow, Fly, credential, export, balance, or financial-data access occurred.
- Preserved user file: untracked `scripts/sync_prod_to_local.sh`, untouched and unstaged.

## Current Action

Run a just-in-time planning pass over Task 4 and propose a synthetic-first work block 3D before auditing planning, weekly, waterfall, or payroll behavior.

## Phase 3 Boundary

- Work block 3C is complete; it does not authorize the Recurring Charges repair or tracked regression-test implementation.
- Task 4 audit execution requires its own confirmed work block.
- Production/demo access, Plaid/OpenRouter calls, workflow action, Fly or downstream action, application change, tracked test expansion, and GitHub durability remain excluded until separately authorized.
- The parked Short-Term Planning verification gap is an input to Task 4, not an automatically authorized fix.

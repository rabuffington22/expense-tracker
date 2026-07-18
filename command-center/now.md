# Current Focus

## Active Objective

Prepare the next bounded Phase 3 integration-boundary audit block after completing the synthetic payroll lifecycle audit.

## Current Phase

Phase 3: Functional Audit And Prioritization — active.

## Completed Work Block

3F: Synthetic Payroll Lifecycle Audit — complete and verified locally with three high payroll-integrity/boundary defects, three medium validation/retention/import defects, and one medium regression-coverage gap.

## Current Task

Phase 3 Task 5: audit Plaid and downstream-sync integration boundaries — awaiting just-in-time work-block planning and separate confirmation.

## Owner

Ryan owns confirmation or revision of the next Phase 3 audit block and later repair prioritization. Codex Desktop owns the verified 3F evidence, protected-data boundaries, dashboard currency, and Task 5 just-in-time planning pass.

## Audit Result

The tracked smoke suite passed. Across the 40-check primary 3F probe and focused seven-check confirmation probe, 36 of 47 assertions passed and eleven controlled failures represented six functional or privacy defects plus one tracked-coverage gap.

Multi-section parsing, dates and amounts, role suggestions, parser deduplication, headerless-workbook handling, BFM roster CRUD and pay history, delete cascades, explicit import persistence, re-import row stability, role and employee totals, successful-save cleanup, entity storage isolation, and temporary cleanup passed.

Direct Personal and Luxe Legacy routes violated the maintained BFM-only boundary. The default import preview duplicated an exact existing employee, and peer averages mixed hourly and salary units. Employee direct inputs were weakly normalized, canceled previews retained their payloads until age cleanup, malformed XLSX bytes raised instead of returning a controlled error, and the tracked suite lacks payroll lifecycle coverage.

## Durability

- Work block 3F and its findings are authorized for an exact seven-path command-center closeout pushed directly to `main` with `[skip actions]`; no PR, merge, or deployment is included.
- No application, fixture, tracked test, demo-seed, workflow, or deployment file changed.
- No real payroll, HR, financial, upload, credential, production, demo, Plaid, OpenRouter, Fly, downstream, or authentication surface was accessed or changed.
- Preserved user file: untracked `scripts/sync_prod_to_local.sh`, untouched and unstaged.

## Current Action

Run a just-in-time planning pass over Task 5 and propose a source-first, synthetic/mocked work block 3G before auditing Plaid or downstream-sync behavior.

## Phase 3 Boundary

- Work block 3F is complete; it does not authorize any repair, migration, tracked regression-test, fixture, or demo-seed implementation.
- Task 5 audit execution requires its own confirmed work block because Plaid and downstream sync introduce external-integration, credential, workflow, and write boundaries.
- Source inspection and synthetic or mocked behavior may be proposed first, but production account access, Plaid actions, workflow actions, credential use, downstream writes, Fly actions, and any other live effect remain separately gated.
- All 3A-3F findings are inputs to Phase 4 prioritization, not automatically authorized fixes.

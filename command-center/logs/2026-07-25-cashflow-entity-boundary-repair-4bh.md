# Work Block 4BH — Cash Flow Shared-Entity Mutation Boundary Repair

Date: 2026-07-25

Status: complete and locally verified; uncommitted

Branch: `codex/cashflow-read-model-coverage`

## Confirmed Scope

Task 1P.7.4a plus only its focused Task 2 regression slice: preserve Personal/BFM sibling Cash Flow visibility while making those cards read-only; require account, card, and recurring mutation targets to match the active cookie entity; preserve valid active-entity mutations; add maintained temporary all-entity colliding-ID, no-mutation, valid-mutation, Luxe Legacy, denied-network, exact-cleanup, rendered, and isolated-browser proof; and close locally without publication or live action.

Task 1P.7.4b, broader regression coverage, CI, durability, publication, production, protected data, credentials, Plaid, workflows, Fly, deployment, and the three preserved untracked files remained excluded.

## Implementation

- Cash Flow mutation routes now require the submitted `entity_key` to equal the active cookie entity before opening a database. Missing or mismatched targets return controlled HTTP 404.
- Primary-entity cards retain their modal-opening mutation metadata and existing write workflows.
- Personal/BFM sibling cards retain balances, liabilities, payment details, and upcoming information through a view-only flip action, but expose no account ID, entity target, edit modal, recurring form, or other mutation-target data.
- The maintained smoke suite now creates colliding bank, card, and recurring IDs in Personal, BFM, and Luxe Legacy; proves every included route rejects missing and mismatched targets with zero mutation; proves valid Personal bank, card, recurring-add, and recurring-delete writes; proves BFM and Luxe Legacy isolation; denies networking; and restores rows and `manual_recurring` sequences exactly.
- The maintained isolated-browser suite now proves sibling cards contain no mutation controls or target data, flip for read-only detail, and never open the Cash Flow edit modal while primary cards remain editable.

## Verification

- Baseline full `.venv/bin/python scripts/smoke_test.py`: passed before product changes.
- Final full `.venv/bin/python scripts/smoke_test.py`: passed, including new section 8l.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py`: passed across no-password and configured-auth modes with denied non-localhost traffic, zero unexpected browser/page errors, and exact temporary cleanup.
- Focused rendered desktop inspection: two active editable Personal cards and two read-only BFM sibling cards rendered; the BFM credit card flipped to show limit, APR, and payment; the mutation modal remained hidden; no external request was attempted; the temporary root was removed.
- Python compilation for the route and both maintained test runners: passed.
- JavaScript syntax for `web/static/cashflow.js`: passed.
- JSON, whitespace, exact-scope, dashboard refresh, health, generated state, rendered dashboard, and preserved-file checks: passed at closeout.

The first new smoke iteration used an exact sibling-card count and failed because earlier maintained fixtures legitimately left additional synthetic accounts in the temporary database. The assertion was corrected to require that every sibling card is read-only while accepting the existing synthetic inventory; product behavior did not fail.

## Result

The confirmed colliding-ID write path is closed locally. A rendered sibling target can no longer provide a mutation route or account ID, and direct missing or mismatched entity submissions stop before database access. Valid active-entity writes remain intact. Task 1P.7.4a and work block 4BH are complete locally; Task 1P.7.4b coverage completion, durability, publication, and live action remain separate gates.

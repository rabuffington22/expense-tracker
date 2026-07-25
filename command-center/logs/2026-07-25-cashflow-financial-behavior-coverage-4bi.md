# Work Block 4BI — Cash Flow Financial-Behavior Coverage Completion

Date: 2026-07-25

Status: complete and locally verified; uncommitted

Branch: `codex/cashflow-read-model-coverage`

## Confirmed Scope

Task 1P.7.4b plus only its focused Task 2 / `P3-3C-C01` regression slice: keep the verified 4BH product repair read-only; add maintained temporary Personal, BFM, and Luxe Legacy proof for bank/card persistence, stored liabilities, due-date behavior, manual and automatic recurrence, empty states, shared read-only visibility, Luxe Legacy isolation, valid current-entity writes, denied networking, and exact cleanup; then close locally without durability, publication, protected access, or live action.

## Maintained Coverage

- Section 8m uses a separate disposable database root to prove the primary Cash Flow empty state for Personal, BFM, and Luxe Legacy without depending on earlier smoke fixtures.
- Temporary all-entity fixtures use colliding bank, card, and manual-recurring IDs and unique synthetic names. Each active entity persists its own bank balance, card balance, credit limit, payment amount, APR, due day, and manual recurring add/delete without changing either sibling database.
- Stored due dates remain intact. A manual due day crossing December derives the next January date, and day 31 clamps to the last day of February.
- Manual recurrence proves February day-31 clamping and December-to-January rollover.
- All five cadence classification bands remain stable. End-to-end weekly, biweekly, and monthly projections resolve to fixed expected dates, while irregular, stale, and outside-horizon histories remain excluded.
- Stored liability values render from local fields with no Plaid credentials or retrieval. Personal and BFM retain reciprocal read-only financial visibility without mutation targets, while Luxe Legacy renders only its isolated section.
- Outbound networking is denied. Every synthetic transaction, account, recurring row, and `manual_recurring` sequence is restored to its exact pre-seed snapshot.

## Verification

- Active Runway OS JSON, dashboard refresh, health check, generated state, whitespace, and rendered dashboard inspection: passed before implementation.
- Baseline full `.venv/bin/python scripts/smoke_test.py`: passed.
- First 8m iteration stopped on a test-only formatter assumption: Cash Flow card backs intentionally use whole-dollar `fmt_dollars` output. Only the expected display strings changed; product behavior did not fail.
- Final full `.venv/bin/python scripts/smoke_test.py`: passed, including sections 8l and 8m.
- Python compilation for `web/routes/cashflow.py`, `scripts/smoke_test.py`, and `scripts/mobile_drawer_browser_test.py`: passed.
- JavaScript syntax for `web/static/cashflow.js`: passed.
- Full `.venv/bin/python scripts/mobile_drawer_browser_test.py`: passed across configured-auth and no-password modes, denied external traffic, zero unexpected browser/page errors, and exact temporary cleanup.
- JSON, `git diff --check`, exact-scope, dashboard, and preserved-file checks: passed at closeout.

## Result

Task 1P.7.4b and the Task 1P.7.4 umbrella are complete locally. The combined 4BH repair and 4BI maintained matrix are uncommitted on `codex/cashflow-read-model-coverage`. No product change occurred during 4BI. No migration, dependency, category, authentication, CSRF, CSP, PWA, Plaid, protected-data, real-database, credential, external/live, production/demo, downstream, GitHub, workflow, Fly, deployment, publication, or preserved-file action occurred.

The next valid decision is a separately proposed 4BI-R exact-scope durability block without deployment.

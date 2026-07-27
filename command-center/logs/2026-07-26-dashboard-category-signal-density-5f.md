# 5F Dashboard Category Signal And Density

Date: 2026-07-26\
Status: complete, verified, local-only, unstaged, uncommitted, and unpublished\
Branch: `codex/phase-5-usability-baseline`

## Result

- The single-month dashboard category scoreboard keeps every category with spending or a configured budget in the primary view.
- Only categories with both zero spending and no configured budget begin behind a native-button disclosure that names the exact hidden count. Enter, Space, pointer, focus, ARIA state, and visible Show/Hide labels passed maintained browser coverage.
- Every visible row now says either `{percent}% of ${budget}` or `No budget`, so the existing green, yellow, and red bars are not the sole budget signal. Existing computed percentages, amounts, thresholds, totals, and inclusion rules are reused unchanged.
- The orphan-category flash now says that categories are no longer in the user's category list and links to `Review and reassign`; its count, singular/plural grammar, truthful condition, and once-per-session-per-entity behavior remain intact.
- Category drill links, expandable subcategories, the transaction modal, Details/Compare, repeated HTMX swaps, authentication modes, CSP, PWA behavior, responsive layout, and entity isolation remain intact.
- Luxe Legacy received regression-only verification. Its setup was not reopened or changed.

## Measured Rendered Evidence

- Personal baseline: 32 category rows, including 15 zero-spend/no-budget rows, with a 1,018.46px category fragment.
- Personal final: 17 primary rows, 15 exact-count inactive rows collapsed by default, a 668.63px category fragment, complete textual budget context, and no document overflow. The collapsed fragment is about 34% shorter than baseline.
- BFM baseline: 29 category rows, including 12 zero-spend rows; 10 of those also had no configured budget.
- BFM final: 19 primary rows and 10 exact-count inactive rows collapsed by default. The two zero-spend budgeted categories remain primary and visibly read `0% of $1,000` and `0% of $500`.
- Direct synthetic desktop inspection found the primary hierarchy materially clearer. An initial rendered check caught that the grid display rule overrode the native hidden attribute; the final explicit hidden-state CSS fixed that issue before closeout.
- The complete isolated browser suite exercised phone, exact-768, and desktop contracts under both no-password and configured-auth modes with denied non-localhost networking and exact cleanup.

No product screenshot was retained because the disposable in-app evidence was inspected directly and the exact sanitized measurements and behavior are recorded here.

## Maintained Coverage

- `scripts/smoke_test.py` now proves the exact zero-spend/no-budget classification, preservation of a zero-spend budgeted category, visible percentage/amount and no-budget text, exact hidden count, ARIA wiring, controller contract, and user-facing once-per-session orphan notice.
- `scripts/mobile_drawer_browser_test.py` now proves the real rendered disclosure starts collapsed, its count matches the hidden rows, visible budget context is nonempty and color-independent, Enter expands it, Space collapses it, and the rest of the dashboard/report fragment behavior survives in both auth modes.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass after the final hidden-state correction.
- Complete maintained `.venv/bin/python scripts/mobile_drawer_browser_test.py`: pass after the final hidden-state correction.
- Relevant Python compilation: pass.
- `node --check web/static/dashboard-fragments.js`: pass.
- Direct Personal, BFM, and Luxe Legacy disposable-synthetic rendering: pass with no horizontal overflow or server error.
- JSON, dashboard refresh/currentness/health, rendered command-center inspection, whitespace, exact changed/staged paths, and preserved-file checks: pass at closeout.
- Staged paths: zero.

## Cleanup And Boundaries

The disposable local Flask server and in-app browser tab were closed. The exact synthetic `/tmp/expense_5f_baseline.jLucKl` root was removed from `/tmp` by moving it to Trash.

No real or protected financial data, credential, retained upload, production/demo/Plaid/Fly/downstream access, workflow action, deployment, staging, commit, push, PR, merge, Task 2.2 or 5D, Task 2.4-2.5, Task 2.7-2.8, Task 3-4 implementation, broad chart redesign, financial/query/report/database/category-domain/authentication/PWA/Ask Opus change, Luxe Legacy setup, sequel, or preserved-file mutation occurred.

# 5E Phone Transaction Clarity And Entity Context

Date: 2026-07-26\
Status: complete, verified, local-only, unstaged, uncommitted, and unpublished\
Branch: `codex/phase-5-usability-baseline`

## Result

- The shared mobile header now shows the active Personal, BFM, or LL label as read-only context. A visually hidden `Current entity:` prefix gives the visible value explicit accessible meaning.
- At the existing phone breakpoint, each transaction remains one semantic server-rendered row but uses a compact two-line grid containing date, description, amount, category, and subcategory.
- The five existing sort controls remain visible above the rows. Copy, pagination, badges, empty state, filters, repeated HTMX swaps, and the row-to-edit-modal path remain unchanged.
- Exact-768 and desktop retain the existing table and table-row presentation.
- No JavaScript, route, query, database, migration, financial logic, category domain, entity-switching, drawer markup, authentication, PWA, workflow, dependency, README, live-system, or Git publication change occurred.
- Luxe Legacy setup and the Task 2.2 / 5D path remain parked.

## Measured Rendered Evidence

- The prior accepted baseline was a 560px transaction table inside the 390px phone viewport.
- Final Personal, BFM, and LL measurements at 390px were identical: 390px document width, 368px wrapper client and scroll width, 368.06px table and row width, grid row presentation, five visible fields, and five visible sort controls.
- Final exact-768 Personal measured a 768px document with `table` and `table-row` presentation preserved.
- The visible marker matched the active entity in every phone capture and retained the screen-reader-only `Current entity:` context.
- The synthetic visual run produced zero blocked requests, console errors, or page errors.

## Retained Synthetic Artifacts

- `command-center/artifacts/phase-5/5e/personal-transactions-phone-390.png` — SHA-256 `688c85ba66825fc63de2a8e6eccde8ec2540a708c52a468c9ae0a13a405bb6a2`
- `command-center/artifacts/phase-5/5e/bfm-transactions-phone-390.png` — SHA-256 `b9a37de727ac8101c6c590df7cde87260ac28096bee704838629ae832c24b693`
- `command-center/artifacts/phase-5/5e/ll-transactions-phone-390.png` — SHA-256 `e58776672ecd4b62011e5f0e6386d26f54d56d97687eec876fea732eb5dee0e0`
- `command-center/artifacts/phase-5/5e/personal-transactions-tablet-768.png` — SHA-256 `45ecea5525225133414a665a418e5724314b4a29048065b6cfe20b19de5f52c3`

All four final artifacts were directly inspected. A reused headless context twice captured a transient header-only frame despite a complete measured DOM; the affected BFM proof was regenerated in a fresh context and directly re-inspected. This was isolated to evidence capture and did not reproduce in the maintained browser suite or layout measurements.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass.
- Relevant Python compilation: pass.
- Complete maintained `.venv/bin/python scripts/mobile_drawer_browser_test.py`: pass against the final source.
- Focused maintained coverage: all three entities render five visible non-scrolling phone fields, preserve five sort controls and the edit request/modal path, expose the correct mobile marker, and retain exact-768/desktop tables.
- Complete configured-auth/no-password browser coverage: pass for shared shell, drawer, HTMX, transaction/modal, all maintained route families, CSP, installability, offline isolation, denied networking, zero unexpected browser/page errors, and exact temporary cleanup.
- Final visual measurements and screenshots: pass with zero blocked requests, console errors, or page errors.
- `git diff --check`: pass.
- Staged paths: zero.

## Boundaries

No real or protected financial data, retained upload, credential, production/demo/Plaid/Fly/downstream access, workflow action, deployment, staging, commit, push, PR, merge, Task 2.2, Task 2.4-2.8, Task 3-4, or preserved-file mutation occurred.

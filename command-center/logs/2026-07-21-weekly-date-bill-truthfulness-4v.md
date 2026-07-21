# Work Block 4V: Weekly Date And Bill Truthfulness

Date: 2026-07-21

Status: complete and verified locally; release not authorized

## Scope

Completed Phase 4 Task 1N.4 plus only the focused Task 2 regression slice for `P3-3E-01`, `P3-3E-02`, and `P3-3E-C01` on local branch `codex/weekly-date-bill-truthfulness`.

Excluded throughout: Tasks 1N.5-1N.8; Tasks 1O-1P; broader Task 2; Tasks 3-4; migrations; historical remediation; demo redesign; broad UI work; authentication; real financial data; retained uploads; credentials; production/demo; Plaid; external calls; workflows; Fly; downstream writes; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

## Result

- Weekly now uses the selected ISO week's Monday as the budget-month anchor for total and category pace, last-week comparisons, warnings, MTD, burn rate, and displayed month.
- MTD ends at the earliest of the viewed Sunday, current date, or anchored month end, so cross-month and cross-year weeks cannot create an overlong month window.
- Detected recurring, manual recurring, and credit-card due helpers accept an optional reference date. Weekly supplies its viewed Monday while existing Cash Flow and Short-Term Planning callers retain today-based defaults.
- Positive scheduled card payments drive Weekly row amounts and totals. Missing or zero scheduled amounts render as unavailable and never substitute the full balance; zero-balance cards remain outside the due helper.
- No template, migration, schema, historical-row, authentication, or demo change was required.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: pass.
- New maintained section 8a5: pass for February historical pace and burn, detected/manual/card recurrence, multiple cards, positive/missing/zero scheduled amounts, zero balances, sorted bills, BFM payroll, cross-month and cross-year anchors, invalid-week fallback, rendered reminders, existing default callers, Personal/BFM isolation, Luxe Legacy denial, denied networking, and exact cleanup.
- `.venv/bin/python -m py_compile web/routes/weekly.py web/routes/cashflow.py web/routes/short_term_planning.py scripts/smoke_test.py`: pass.
- JSON validation, `git diff --check`, dashboard refresh, command-center health, rendered-dashboard inspection, and final worktree scope: pass at closeout.

## Boundaries Preserved

No real financial row or database, retained upload, credential, authenticated production page, production/demo system, Plaid call, external call, workflow, Fly action, downstream access or write, migration, historical remediation, GitHub durability, commit, push, PR, merge, or deployment occurred. Both pre-existing untracked files remained untouched and unstaged.

## Durability

Local branch `codex/weekly-date-bill-truthfulness` only. Publication and Task 1N.5 remain separate gates.

## Learning

The two visible Weekly defects shared one underlying boundary problem: helpers and derived calculations silently chose their own notion of today. Passing one viewed-week anchor through pace, recurrence, MTD, display, and card-payment assembly removed both the historical drift and the balance substitution without changing schema or the current Cash Flow and Short-Term Planning defaults. Task 1N.5 can now focus strictly on paydown-date validation and defensive stored-goal reads.

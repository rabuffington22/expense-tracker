# Work Block 3E: Synthetic Weekly and Waterfall Audit

Date: 2026-07-18

Status: complete; findings recorded; direct-main durability authorized separately

## Scope

Audit Phase 3 Task 4C as one synthetic-only pass over Weekly Check-In and the BFM-to-Personal Waterfall. Cover selected-week and selected-month dates, effective transaction spending, budget pace, bills, burn rate, warnings, credit-card paydown, actual and target waterfall calculations, trends, payoff estimates, invalid inputs, empty states, and intended Personal/BFM/LL boundaries.

Excluded throughout: completed Tasks 1-3 and 4A-4B; Tasks 4D and 5-8; product repairs and migrations; tracked test, fixture, or demo-seed changes; real databases, financial rows, payroll/HR data, credentials, production/demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication/security changes; GitHub durability; and the pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Verification

- `.venv/bin/python scripts/smoke_test.py` passed its temporary-`DATA_DIR` initialization, import, isolation, route, export, saved-view, and To Do checks.
- The primary ephemeral probe exercised 58 checks against freshly migrated Personal, BFM, and Luxe Legacy databases. After correcting three audit-harness expectations, 48 checks passed and ten controlled assertions represented five functional defect clusters plus one tracked-coverage gap.
- A focused ten-check confirmation probe passed two setup controls and reproduced eight controlled assertions across four clusters. It confirmed the selected-date, scheduled-card-payment, and tax-validation defects and added the separate sub-month payoff-rounding defect.
- No unexpected runtime error escaped either probe. Invalid paydown and non-finite tax inputs were intentionally caught and classified as controlled route failures.
- Temporary synthetic databases were created through `TemporaryDirectory` and removed when each probe exited.
- No tracked product, fixture, test, or demo-seed file changed.

## Behavior Matrix

| Surface | Result | Evidence |
| --- | --- | --- |
| ISO week bounds, previous/next navigation, and labels | Pass | Cross-year week 2026-W01 resolved to 2025-12-29 through 2026-01-04, and cross-month labels rendered correctly. |
| Effective weekly spending | Pass | Split pieces replaced their parent, excluded payment categories stayed out, signed cents reconciled, and current-week totals matched. |
| Current-month budget and category pace | Pass | July monthly budgets converted to the expected 31-day weekly pace. |
| Historical/viewed-week date anchoring | Defect | February pace used July's 31-day divisor; historical manual/card bills were omitted; a June-to-July last-week window included 42 days in burn rate and changed an over-budget result into under-budget. |
| Current-week bill sources and ordering | Pass | Action, detected recurring, manual recurring, and credit-card items were all present and sorted after the deterministic recurrence fixture was corrected. |
| Credit-card due amount and bill total | Defect | A card titled `$50 due` contributed its full $1,200 balance to the bill row and total. |
| Warnings and direct burn-rate math | Pass | Over-pace warnings and the pure burn-rate helper reconciled when given correctly anchored inputs. |
| Credit-card balances and valid paydown goal | Pass | Positive cards, utilization, linear expected balance, percent complete, behind/on-pace state, and valid entity-local goal update reconciled. |
| Invalid paydown-goal date | Defect | A direct POST saved `not-a-date`; the next Weekly read raised `ValueError`. |
| BFM payroll bill | Pass | A biweekly anchor produced the expected 2026-07-17 payroll row in BFM Weekly. |
| Waterfall empty state and month navigation | Pass | No BFM history rendered `has_data=False`; invalid month fell back to the latest available month. |
| Actual BFM waterfall | Pass | Income, effective expenses, exclusions, section grouping, total expenses, and surplus reconciled across three synthetic months. |
| Target revenue and take-home modes | Pass | BFM budget costs, gross owner salary, tax, take-home, Personal budgets, and remaining amount reconciled for valid inputs. |
| Actual Personal continuation | Pass | Current BFM surplus flowed through tax to Personal actual spending and the expected deficit. |
| Historical surplus series | Pass | May, June, and July rendered the expected positive, negative, and positive monthly results. |
| Three-month payoff average | Defect | The displayed average ignored the deficit month, using $1,750 instead of the signed three-month average of $500 and overstating payoff capacity. |
| Sub-month payoff estimate | Defect | Debt smaller than one month of surplus rounded to `0 months` rather than a minimum of one month. |
| Waterfall invalid mode and ordinary invalid values | Pass | Invalid mode and month safely fell back, and valid revenue/take-home inputs rendered. |
| Waterfall tax validation | Defect | A 100% input displayed 100% while calculations silently used the 22% fallback; `tax_rate=nan` raised `ValueError`. |
| Personal/BFM intended shared Waterfall and LL denial | Pass | Personal and BFM produced the same intended cross-entity read model; LL redirected from Weekly, Waterfall, and paydown mutation with no LL goal created. |
| Read-only row preservation | Pass | Weekly and Waterfall reads left transaction, budget, and account counts unchanged in all three temporary entities. |
| Maintained regression coverage | Gap | `scripts/smoke_test.py` contains no dedicated Weekly or Waterfall route/helper cases. |

## Ranked Findings

1. High: Weekly historical navigation mixes the selected week/month with the current date, producing wrong pace, incomplete bills, and a cross-month burn-rate reversal.
2. High: Weekly uses the full credit-card balance as the bill amount instead of the scheduled payment amount shown in the title.
3. High: Waterfall's documented three-month payoff average excludes deficit months and can materially overstate repayment capacity.
4. Medium: Invalid paydown-goal dates persist and break the next Weekly page read.
5. Medium: Waterfall payoff estimates can display zero months while debt remains.
6. Medium: Waterfall tax fallback can disagree with the displayed input, and non-finite direct input can crash the route.
7. Medium: Weekly and Waterfall have no dedicated tracked regression coverage.

## Acceptance Checks

- Every Weekly calculation and bill source accepts or derives from the viewed week/month; cross-month burn rate uses one coherent month window and divisor.
- Credit-card bill rows and totals use `payment_amount_cents` when a scheduled amount is shown, with an explicit fallback when it is absent.
- Waterfall's rolling average includes all months in the selected window using a documented signed-surplus rule.
- Paydown-goal dates are validated before persistence, and malformed stored values cannot break the page.
- Positive debt always produces a payoff estimate of at least one month when surplus is positive.
- Tax input is finite, normalized, range-checked, displayed consistently with the applied calculation, and cannot crash the route.
- Tracked synthetic tests cover current, historical, cross-month, empty, invalid-input, and Personal/BFM/LL cases plus each repaired defect.

## Boundaries Preserved

- No real financial, payroll, HR, credential, production, demo, Plaid, OpenRouter, Fly, workflow, downstream, or authentication surface was accessed or changed.
- All financial rows were deterministic synthetic values in disposable temporary databases.
- No application repair or tracked regression coverage was implemented.
- The exact seven-path command-center closeout was published directly to `main` under Ryan's separate authorization with `[skip actions]`; no PR, merge, or deployment occurred.
- The pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Learning

The ordinary current-period paths reconcile well, but the derived views lose trust at calendar and input edges. Weekly's selected date is not propagated consistently into pace, bills, and burn rate, while Waterfall's payoff summary uses optimistic averaging and weak input normalization. Task 4D can proceed independently because these findings do not invalidate the payroll schedule as a controlled Weekly input, but Phase 4 should prioritize the three high financial-output defects before relying on historical planning views.

# Work Block 3D: Synthetic Planning Foundations Audit

Date: 2026-07-18

Status: complete locally; findings recorded; durability not authorized

## Scope

Audit Phase 3 Tasks 4A-4B as one synthetic-only planning-foundation pass. Cover Long-Term Planning settings, assets, liabilities, projections, cash-flow links, CRUD, Personal/BFM shared visibility, and Luxe Legacy denial plus Short-Term Planning goals, snapshots, budgets, actions, payoff schedules, account choices, and entity isolation.

Excluded throughout: Tasks 4C-4D and 5-8; product repairs and migrations; tracked test, fixture, or demo-seed changes; real databases, financial rows, payroll/HR data, credentials, production/demo access; Plaid or OpenRouter calls; workflows, Fly, downstream writes, authentication/security changes; GitHub durability; and the pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Verification

- `.venv/bin/python scripts/smoke_test.py` passed its temporary-`DATA_DIR` initialization, import, isolation, route, export, saved-view, and To Do checks.
- The final ephemeral 3D probe ran 58 checks against freshly migrated Personal, BFM, and Luxe Legacy databases: 48 passed, 10 controlled assertions failed, and zero runtime errors occurred.
- The ten failed assertions cluster into four distinct defects rather than ten separate findings.
- Temporary synthetic databases were created through `TemporaryDirectory` and removed when the probe exited.
- No tracked product, fixture, test, or demo-seed file changed.

## Behavior Matrix

| Surface | Result | Evidence |
| --- | --- | --- |
| Long-term settings and milestones | Pass | Personal singleton settings loaded and custom milestones sorted with the standard milestones. |
| Manual and cash-flow-linked planning items | Pass | Linked balances replaced stale stored values; add, update, and delete persisted only in the selected primary entity. |
| Positive appreciation, contributions, liabilities, and summaries | Pass | Positive assets grew, liabilities clamped at zero after payoff, and today's summary reconciled. |
| Negative asset appreciation | Defect | A $10,000 asset at -10% remained $10,000 at the future milestone. |
| Personal/BFM long-term visibility | Pass | Each primary page rendered its own editable section and the other entity's read-only section; LL items stayed hidden. |
| Luxe Legacy planning page entry | Pass | Both planning index routes redirected LL to the dashboard. |
| Luxe Legacy direct-route denial | Defect | Direct requests created hidden LL planning, goal, budget, and action records; exposed a Personal account name; and changed the Personal settings singleton in temporary data. |
| Short-term goal CRUD/status/delete | Pass | Create, update, complete/reactivate, delete, and snapshot cascade behavior passed. |
| Personal/BFM short-term account choices | Pass | Each page offered only the selected entity's accounts. |
| Automatic and manual snapshots | Defect | Manual notes saved, but the next automatic snapshot replaced the row, erased the note, and reopened monthly review. |
| Progress chart | Pass | Two dated snapshots produced the SVG progress partial. |
| Direct avalanche and snowball engines | Pass | When given correct rates and balances, the engines targeted the expected account. |
| Locked payoff plan | Defect | The route hard-coded every APR to 20%; the low-APR card received avalanche's extra payment because it appeared first. |
| Budget totals and effective splits | Pass | Split pieces replaced the parent; income/payments were excluded; remaining amount and percent reconciled. |
| Three-month averages | Pass | Category total and distinct-month divisor produced the expected average. |
| Budget/subcategory persistence and partials | Pass | Save, status, subcategory, and transaction drill-down paths returned expected synthetic values. |
| Per-payroll budgets | Pass | A July 2026 biweekly schedule counted three paydays, and per-payroll save preserved the mode. |
| Action items | Pass | Create, complete, and delete persisted in the selected entity. |
| Maintained regression coverage | Gap | `scripts/smoke_test.py` contains no dedicated long- or short-term planning cases. |
| Demo goal/snapshot evidence | Gap | `scripts/seed_demo_data.py` seeds planning items, budgets, and actions but no short-term goals or snapshots. |

## Ranked Findings

1. High: locked payoff schedules ignore stored account APRs and can reverse avalanche ordering.
2. High: LL denial is enforced only on planning page entry, not direct helper or mutation routes.
3. Medium: automatic same-day snapshots erase manual monthly-review notes.
4. Medium: negative asset appreciation is treated as zero growth.
5. Medium: planning foundations lack tracked regression coverage; demo goals and snapshots also remain unseeded.

## Legacy Plan Verdict

- Still valid: goal CRUD, snapshot persistence, budget CRUD/status, payoff correctness, entity isolation, and tracked synthetic coverage.
- Confirmed current behavior: Personal/BFM short-term goals and account choices are entity-local; Personal/BFM sharing is explicit only on Long-Term Planning.
- Superseded: Short-Term Planning cross-entity account linking and the retired custom-allocation strategy. Current repository rules require cross-entity behavior to be explicit, and the current UI exposes avalanche and snowball only.
- Still optional/demo-facing: seeded goal and snapshot examples. They remain useful for demo fidelity but are not proof of production correctness.

## Boundaries Preserved

- No real financial, payroll, HR, credential, production, demo, Plaid, OpenRouter, Fly, workflow, downstream, or authentication surface was accessed or changed.
- The probe restored the synthetic Personal settings value after reproducing the LL cross-boundary mutation and then deleted all temporary databases.
- No application repair or tracked regression coverage was implemented.
- No commit, push, PR, merge, or deployment occurred.
- The pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Learning

The planning foundation is broadly implemented and most ordinary synthetic workflows work, but four edge paths materially weaken trust: schedules can use the wrong debt ordering, hidden LL routes bypass the visible product boundary, routine reloads can erase review notes, and depreciation is not reflected in projections. Task 4C can proceed as a separate audit because its budget and planning inputs are usable under controlled synthetic data, but Phase 4 prioritization should treat the APR and LL-boundary repairs as the highest 3D findings.

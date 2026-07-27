# Phase 5 Cross-Surface Usability Baseline

Date: 2026-07-26\
Work block: 5A Cross-Surface Usability Baseline\
Tasks: 1.1 (`P5-T11`) and 1.2 (`P5-T12`)\
Data boundary: disposable synthetic local data only

## Outcome

The J1-J5 matrix is complete enough for independent critique. The application is technically stable across the reviewed surfaces: full synthetic smoke and the complete configured-auth/no-password installed-Chrome suite passed, non-localhost browser traffic was denied by the maintained suite, the qualitative browser session produced no console warnings or errors, and its managed temporary data root was removed.

The main Phase 5 problem is not broken mechanics. It is product explanation and prioritization. The shell is consistent and entity-safe, but several first-use and dense-workflow surfaces make users infer too much: the synthetic demo opens with stale category warnings, Short-Term Planning demonstrates no goal, Luxe Legacy has weak empty/unsupported-state explanation, wide mobile transaction tables lack an obvious overflow cue, and the recurring-charge page presents a large decision queue under a narrower “Subscription Tracker” label.

These are provisional observations, not accepted Task 2 direction. Tasks 1.3-1.4 remain responsible for independent critique, Codex intake, ranking, and Ryan decisions.

## Matrix Disposition

| ID | Disposition | Evidence and conclusion |
|---|---|---|
| J1 Personal daily orientation | complete | Dashboard, To Do, Transactions, and Reports were inspected. The shell, headings, filters, actionable To Do links, and report controls are coherent. The dashboard seed emits a prominent stale-category warning, the long category presentation is dense, and the exact 390px transaction table is 560px wide inside a 390px viewport without a visible swipe/overflow cue. |
| J2 planning and reporting | complete | Cash Flow, Short-Term Planning, Long-Term Planning, Weekly, and Waterfall were inspected across Personal/BFM and representative widths. Weekly presents a strong summary-to-detail hierarchy. Short-Term Planning’s demo seed has action items, autopay, and budget data but zero goals, so the page does not demonstrate its defining goal workflow. |
| J3 BFM operations | complete | Dashboard/Transactions technical behavior, Subscriptions, Payroll, Data Sources, and Connected Accounts boundaries were covered. Payroll’s empty state and import source are clear. Data Sources is reachable from To Do but not persistent navigation. Subscription candidates are dense and combine ordinary recurring bills with subscriptions under one tracker label. |
| J4 Luxe Legacy boundaries | complete | Supported navigation is correctly narrower and technical route denial passed. An empty LL dashboard shows zero-filled category scaffolding without a prominent import/connect explanation. A direct unsupported Short-Term Planning URL redirects to `/` without a visible explanation. |
| J5 installed-PWA continuity | complete with capture limitation | The maintained installed-Chrome suite passed manifest/icon/installability, standalone shell, entity continuity, drawer focus/containment/Escape, cross-entity offline isolation, generic offline recovery, strict CSP, denied networking, and exact cleanup. The offline document is visually direct and data-free. The in-app browser did not consistently preserve exact CDP emulation in raster captures; mismatched captures were quarantined outside the repo, and the stable fallback image is labeled accordingly. |

## Provisional Findings

### F5A-01 — Demo category taxonomy drift dominates first orientation

Impact: high\
Evidence: J1 Personal dashboard

The synthetic demo opens with a prominent banner stating that 17 categories removed from `categories.md` still have transactions. That warning is operationally truthful but makes the maintained demonstration look stale before the user understands the dashboard. The same drift expands Personal filters and no-budget rows with legacy category names.

Acceptance direction for later intake: the demo seed and current category domain should agree, or the demo should deliberately explain why legacy rows exist. Do not suppress a truthful production warning merely for polish.

### F5A-02 — The demo does not demonstrate Short-Term Planning goals

Impact: high\
Evidence: J2 Short-Term Planning and carried-forward Phase 4 finding

The demo includes action items, autopay cards, planning items, budgets, and six months of transactions, but the Goals section says “No goals yet.” The call to action is visually distant from the empty-state explanation, and a reviewer cannot assess the primary goal-card experience without creating data.

Acceptance direction for later intake: add a representative synthetic debt-payoff or savings goal to the demo contract, with no effect on production or entity isolation, or explicitly reposition the page as a budget/action dashboard rather than a goal-led workflow.

### F5A-03 — Mobile transaction overflow is functional but not self-explanatory

Impact: medium\
Evidence: J1 exact 390px transaction page

The filter form stacks cleanly and the document itself does not overflow. The transaction table is 560px wide inside the 390px viewport, so later columns require horizontal movement. The visible screen offers no cue that the table is horizontally scrollable, and the rightmost fields disappear from the initial view.

Acceptance direction for later intake: preserve complete financial fields while making overflow discoverable or presenting a mobile-first row hierarchy.

### F5A-04 — Luxe Legacy first-use and unsupported-route states lack explanation

Impact: medium\
Evidence: J4 empty dashboard and denied planning deep link

Luxe Legacy correctly hides unsupported planning and payroll navigation. With no synthetic rows, however, the dashboard mainly shows zero-filled category scaffolding and standard controls rather than an onboarding path. A direct unsupported planning URL silently redirects to the LL dashboard with no notice that the route is unavailable for this entity.

Acceptance direction for later intake: preserve the fail-closed route boundary while explaining empty state and denied capability in user language.

### F5A-05 — “Subscription Tracker” and “recurring charges” describe different scopes

Impact: medium\
Evidence: J3 BFM Subscriptions

The page heading says “Subscription Tracker,” while the candidate list includes rent/facilities, insurance, professional services, benefits, fleet, and other recurring obligations. The list is long, the watchlist begins below the candidate queue, and the accept/dismiss controls are compact icons. The detection may be correct, but the user must infer whether the feature manages subscriptions, all recurring spend, or both.

Acceptance direction for later intake: clarify the object being reviewed, expose queue progress or grouping, and preserve accessible action names.

### F5A-06 — Data Sources is useful but indirectly discoverable

Impact: low to medium\
Evidence: J1 To Do and J3 Data Sources

The Data Sources page clearly explains vendor-order uploads and payment-account matching. It is linked from To Do, but persistent navigation exposes only Connected Accounts. Users who are not working through To Do may not discover Amazon/Henry Schein imports or understand the distinction between Data Sources and Connected Accounts.

Acceptance direction for later intake: decide whether To Do is the intentional sole entry point or whether the information architecture should expose a combined/import-oriented destination more directly.

### F5A-07 — The global AI affordance relies on an unexplained icon

Impact: low to medium\
Evidence: J1-J4

The accessible name “Ask Opus” is present, but responsive screens often show only a prominent gold question-mark image. Its purpose, data boundary, and expected output are not explained in the surrounding interface. This creates a repeated interpretation cost on otherwise task-focused pages.

Acceptance direction for later intake: preserve accessibility while making the visible purpose and privacy expectation understandable.

## Strengths To Preserve

- Entity tabs are persistent and understandable, and supported navigation narrows correctly for Luxe Legacy.
- The maintained mobile drawer has strong semantics, focus placement/containment, Escape/scrim closure, and scroll-lock behavior.
- Mobile filters stack cleanly; the transaction concern is the dense result table, not the filter controls.
- Weekly Check-In has a clear top-down hierarchy from pace and remaining amount to debt and bill details.
- Payroll’s empty state names the next action and the expected Phoenix workbook.
- Data Sources clearly separates vendor orders from payment-account matching once reached.
- The generic offline screen is data-free, direct, and offers one clear Retry action.
- No reviewed route emitted a browser console warning or error.

## Evidence Manifest

| File | Journey | Capture note |
|---|---|---|
| `j1-personal-dashboard-desktop-default-1493.png` | J1 | Readable browser-default dashboard reference; the same route was also inspected at exact 1200px without a retained raster. |
| `j1-personal-transactions-phone-390.png` | J1 | Exact 390px CSS viewport; table measured 560px inside the 390px document. |
| `j2-personal-short-term-planning-desktop-1200.png` | J2 | Exact 1200px view showing populated actions/budget and the empty Goals section. |
| `j2-personal-long-term-planning-tablet-768.png` | J2 | Exact 768px planning reference. |
| `j2-personal-weekly-phone-browser-cap.png` | J2 | Stable narrow browser capture; exact phone behavior is independently covered by the maintained Chrome suite. |
| `j3-bfm-subscriptions-desktop-1200.png` | J3 | Exact 1200px recurring-charge candidate queue. |
| `j3-bfm-payroll-tablet-768.png` | J3 | Exact 768px BFM-only empty/import state. |
| `j3-bfm-data-sources-desktop-1200.png` | J3 | Exact 1200px vendor/payment source page. |
| `j4-luxelegacy-empty-dashboard-desktop-1200.png` | J4 | Exact 1200px empty supported dashboard. |
| `j4-luxelegacy-planning-denied-tablet-768.png` | J4 | Exact 768px post-redirect dashboard with no denied-route explanation. |
| `j5-installed-pwa-offline-browser-fallback.png` | J5 | Stable narrow browser fallback; exact installed/offline behavior is established by the maintained Chrome suite. |

All retained images contain synthetic data only and were visually inspected. Two raster captures whose emulator dimensions did not match their content were moved outside the repository and are not evidence.

## Verification

- `.venv/bin/python scripts/smoke_test.py` — passed in 8.56 seconds.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` — passed completely across both authentication modes, all three entities, installed/standalone/offline paths, responsive behavior, strict CSP, denied external networking, zero unexpected browser/page errors, and exact temporary cleanup.
- Qualitative local server — explicit synthetic secret, blank external integrations, localhost only, zero browser console warnings/errors.
- Managed `expense_5a_review_*` temporary root — absent after server shutdown.

## Decision Boundary

No finding in this report is an accepted product decision. The recommended next work block is 5B for Task 1.3 independent critique of this exact packet followed by Task 1.4 Codex intake. Codex will then classify each suggestion and finding as adopt, ignore, park, or Ryan-decision before proposing any Task 2 implementation.

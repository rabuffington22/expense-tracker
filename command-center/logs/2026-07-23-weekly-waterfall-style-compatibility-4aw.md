# Work Block 4AW — Weekly And Waterfall Style Compatibility

Date: 2026-07-23

Status: complete, verified, local-only, and uncommitted on `codex/csp-weekly-waterfall-styles`.

## Scope

Task 1P.4.3a.5 plus only its focused Task 2 regression slice.

The block removed four Weekly and nine Waterfall template style attributes plus four Waterfall controller runtime style writes. Route calculations, database queries, product behavior, authentication, CSP enforcement, Plaid, publication, deployment, live access, and later style clusters remained excluded.

## Result

- Weekly credit-card, paydown, and category bars use the maintained bounded percentage-class contract, and the Last Week subtitle uses a semantic class.
- Waterfall empty state, credit-card/paydown bars, and trend heights use maintained semantic or bounded percentage classes.
- Waterfall bars carry exact fractional left and width geometry through inert data. The page-owned controller applies the existing values through a persistent Web Animations API effect without creating style attributes.
- Tooltip coordinates and bar entrance staggering use measured Web Animations API effects without runtime style mutation.
- Actual/target switching, breakdowns, tax and target inputs, tooltips, animation, navigation, responsive behavior, supported Personal/BFM routes, and Luxe Legacy denial remain intact.
- The tracked residual application inventory is exactly six inline style blocks, 40 template style attributes, zero generated-markup style attributes, and five runtime style writes.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: pass.
- Maintained source and rendered-response assertions: pass.
- Both included templates contain zero source or rendered style attributes: pass.
- `web/static/waterfall.js` contains zero `style=` output and zero `.style.*` runtime writes: pass.
- `node --check web/static/waterfall.js`: pass.
- Python compilation for both maintained test runners: pass.
- Configured-auth and no-password isolated Chrome: pass.
- Personal and BFM Weekly/Waterfall at phone, exact 768px, and desktop: pass.
- Luxe Legacy pre-execution denial at all three viewport boundaries: pass.
- Exact fractional bar geometry, bounded integer bars, actual/target motion, stagger timing, tooltip viewport bounds, input and interaction behavior, and non-overflowing responsive layout: pass.
- Non-localhost browser requests denied, zero unexpected console/page errors, disposable browser state, temporary synthetic databases, and exact cleanup: pass.
- JSON validation, `git diff --check`, exact-scope review, dashboard refresh, and command-center health: pass.

## Boundaries

No commit, push, PR, publication, deployment, protected data, credential, real database, retained upload, external request, live action, route, calculation, database-query, authentication, CSP-enforcement, Plaid, dependency, later-cluster, downstream, destructive, or preserved-file mutation occurred.

The pre-existing untracked `scripts/sync_prod_to_local.sh`, unrelated `command-center/now 2.md`, and unrelated duplicate 4AU log remain unchanged and excluded.

Exact-scope Task 1P.4.3a.5-R / work block 4AW-R durability remains a separate Ryan decision.

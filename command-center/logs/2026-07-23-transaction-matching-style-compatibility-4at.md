# Work Block 4AT — Transaction And Matching Style Compatibility

Date: 2026-07-23
Durability: local-only and uncommitted on `codex/csp-transaction-matching-styles`

## Scope

- Completed Task 1P.4.3a.2 plus only its focused Task 2 regression slice.
- Removed 63 template style attributes from Transactions, matching/vendor cards, transaction results, row, row-edit, and split-editor templates.
- Removed all seven JavaScript-generated split-line style attributes and all four transaction runtime style writes from `transaction-fragments.js`.
- Kept later style clusters, route/data/product behavior, CSP enforcement, protected/live systems, GitHub durability, publication, deployment, workflows, downstream actions, and both preserved untracked files outside scope.

## Result

- Fixed layout now uses maintained semantic transaction, matching, vendor-card, and split-editor classes in `style.css`.
- Matching and vendor-card progress uses the bounded `u-pct-0` through `u-pct-100` class contract.
- Split totals use explicit balanced/unbalanced state classes; generated split lines use the same maintained layout classes as server-rendered lines.
- Transaction filtering, sorting, copy, edit, suggestions, rules, repeated swaps, matching-card warnings, vendor-card layout, dynamic split lines, auto/manual split lifecycle, modal behavior, and responsive layout remain intact.
- Exact residual tracked inventory is seven inline style blocks, 122 template style attributes, zero generated-markup style attributes, and 17 application runtime style writes.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed.
- The final smoke suite includes source, rendered-page/fragment, controller, bounded-progress, split-state, and exact residual-inventory assertions for 4AT.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes across Personal, BFM, and Luxe Legacy at phone, exact 768px, and desktop widths.
- Browser proof covered zero included style attributes, no page overflow, repeated transaction swaps, sorting, copy, edit, dynamic/auto/manual split behavior, balanced-total state, matching/vendor-card progress and warning/form classes, denied non-localhost traffic, zero unexpected console/page errors, and exact temporary database/upload/browser cleanup.
- Python compilation, JavaScript syntax, JSON validation, whitespace, dashboard refresh, command-center health, generated-state inspection, exact-path review, and preserved-file checks passed.

## Boundaries

- No route, financial, database, matching-policy, category-domain, product, authentication, CSRF, dependency, CSP-header/nonce/exception/enforcement, credential, protected-data, real-database, retained-upload, external/live, GitHub, publication, deployment, workflow, downstream, or destructive mutation occurred.
- `command-center/now 2.md` and `scripts/sync_prod_to_local.sh` remained untouched and untracked.
- Exact-scope 4AT-R durability and Task 1P.4.3a.3 remain separate Ryan decisions.

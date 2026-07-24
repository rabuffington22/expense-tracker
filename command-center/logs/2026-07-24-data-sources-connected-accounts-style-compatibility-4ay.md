# Work Block 4AY Evidence — Data Sources And Connected Accounts Style Compatibility

Date: 2026-07-24

Status: complete and verified locally; durability and publication remain separately gated.

## Result

- Removed the one inline style block and all seven Data Sources plus twenty-seven Connected Accounts template style attributes.
- Moved vendor rows/actions, compact forms, status text, toolbars, account-table columns, rename controls, manual-account rows, and danger actions into maintained page-specific CSS classes while reusing existing spacing and muted-text utilities.
- Preserved both exact `https://cdn.plaid.com/link/v2/stable/link-initialize.js` tags, the page-owned `data-sources.js` and `plaid.js` controllers, vendor upload/filter behavior, confirmations, Link open/success/exit/error behavior, distinct form-versus-JSON token exchanges, conditional account states, entity isolation, and responsive layout.
- The exact residual tracked inventory is five inline style blocks, three template style attributes, zero generated-markup style attributes, and zero application runtime style writes.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed. The final suite includes focused source, conditional-rendered, exact-initializer, semantic-class, mocked-route, and 5/3/0/0 inventory assertions.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes across Personal, BFM, and Luxe Legacy at phone, exact 768px, and desktop widths.
- Browser proof covered style-attribute absence, document overflow, vendor-row/action geometry, Connected Accounts toolbar, fixed table, rename form, exact initializer retention, the existing mocked Plaid interaction paths, denied non-localhost traffic, zero unexpected console/page errors, and exact temporary database/browser cleanup.
- Python compilation, JavaScript syntax, JSON validation, whitespace, command-center refresh/health, rendered dashboard inspection, exact scope, and preserved-file checks passed.

## Boundary

No route/query, known empty-vendor aggregation repair, financial, database, product, authentication, CSRF, dependency, CSP header, nonce, exception policy, enforcement, real Plaid, credential, protected-data, real-database, retained-upload, external/live, GitHub, publication, deployment, workflow, downstream, destructive, or preserved-untracked-file mutation occurred.

## Learning

The style migration itself was static and did not need controller or route changes. The expanded browser proof re-exposed the already-documented empty-vendor aggregation edge after a mocked successful connection creates an item with no transactions; the verification now seeds one synthetic transaction for every synthetic vendor item before the style pass, preserving exact branch coverage without repairing or hiding the excluded product defect. Browser-computed display also confirmed that forms inside a flex action row are blockified, so the maintained assertion targets the actual flex geometry rather than an impossible computed inline value.

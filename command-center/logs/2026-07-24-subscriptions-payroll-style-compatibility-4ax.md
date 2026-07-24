# 4AX Subscriptions And Payroll Style Compatibility

Date: 2026-07-24

Status: complete, verified, local-only, and uncommitted

## Scope

Task 1P.4.3a.6 plus only its focused Task 2 regression slice.

The block removed the complete confirmed Subscriptions and Payroll style seam:

- three baseline-counted Payroll template style attributes;
- one conditional new-role rendered style attribute omitted by the baseline regex;
- two route-generated style attributes from the Payroll spending partial;
- three Subscriptions runtime style writes; and
- two Payroll runtime style writes.

Tasks 1P.4.3a.7-1P.4.4, Tasks 1P.6-1P.7, the remainder of Task 2, Tasks 3-4, route contracts or queries beyond the included partial markup, financial/database/product/authentication/CSP-enforcement/Plaid work, protected or live access, GitHub durability, publication, deployment, workflows, downstream systems, and all three unrelated untracked files remained excluded.

## Result

- The clipboard fallback uses a maintained off-screen CSS class and removes its temporary node after copying.
- Dismissed-subscription disclosure uses `aria-expanded`, `hidden`, and a maintained state selector without runtime style mutation.
- Payroll role colors use finite role classes with the existing default fallback across server-rendered badges, employee details, and repeated spending partials.
- Payroll spending bars use the existing bounded percentage-class contract.
- Import new-role visibility uses the semantic `hidden` property in both initial and controller-managed states.
- The final tracked inventory is exactly six inline style blocks, 37 template style attributes, zero JavaScript-generated style attributes, and zero application runtime style writes.
- The Payroll route contains zero generated `style=` attributes.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including new section 11s for source, rendered full pages, repeated Payroll partials, semantic state, finite role colors, bounded bars, and exact inventory.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py`: pass in configured-auth and no-password modes.
- Browser proof covered:
  - Subscriptions in Personal, BFM, and Luxe Legacy;
  - BFM Payroll and Personal/Luxe Legacy denial before Payroll controller execution;
  - phone, exact 768px, and desktop;
  - successful and rejected clipboard paths with proxy cleanup;
  - disclosure state and rotation;
  - dialogs and mouse/Enter/Space/Escape behavior;
  - role badges and employee detail;
  - repeated spending-period swaps and bounded bars;
  - conditional new-role visibility and preview-payload cleanup;
  - denied non-localhost networking;
  - zero unexpected console or page errors; and
  - exact temporary database, upload-payload, server, browser, and process cleanup.
- Python compilation, JavaScript syntax, JSON validation, `git diff --check`, exact inventory, and included-controller/Payroll-route zero-style scans: pass.

## Boundary

No commit, push, PR, publication, deployment, workflow action, credential, protected data, real financial database, authenticated production page, Plaid action, downstream access/write, CSP enforcement, later-cluster work, destructive action, or preserved-file mutation occurred.

The next gate is a separately planned and confirmed 4AX-R exact-scope durability and automatic-release block.

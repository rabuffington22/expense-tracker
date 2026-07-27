# Work Block 5C — Demo Fidelity Repair

Date: 2026-07-26\
Branch: `codex/phase-5-usability-baseline`\
Status: complete locally

## Scope

Ryan confirmed Phase 5 Task 2.1 only: align the synthetic Personal/BFM seed and budgets with the current entity-specific `categories.md` domain; add one representative synthetic Personal debt-payoff goal and one representative synthetic Personal savings goal using existing synthetic accounts; make affected reseeding deterministic and entity-isolated; add focused maintained disposable-data coverage; inspect the rendered local Personal Dashboard and Short-Term Planning result; and close Runway OS locally.

Tasks 2.2-2.8 and Tasks 3-4, product templates/styles/JavaScript/routes, category-domain changes, migrations, authentication, CSRF, CSP, PWA, recurring detection, Ask Opus, Luxe Legacy product design, mobile/dashboard design, real/protected data, live demo or production access/reseeding, staging, commit, push, PR, workflow, deployment, and all three preserved untracked files remained excluded.

## Implementation

- `scripts/seed_demo_data.py` now reads Personal and BFM categories and subcategories directly from `core.categories.load_categories()` instead of maintaining a competing seed-only taxonomy.
- Personal and BFM merchant groups, account mappings, recurrence behavior, and budgets now use only their current entity-specific maintained category names.
- Fresh and repeated synthetic demo seeds replace migration-era category rows with the exact maintained domain.
- Each entity receives a deterministic same-day random seed, preserving repeatable transaction IDs and values across same-day reseeds.
- Personal receives exactly two active synthetic goals:
  - `Pay Off Visa Rewards`, type `debt_payoff`, linked to `Visa Rewards`, $500/month.
  - `Build Emergency Fund`, type `savings`, linked to `Savings`, $20,000 target, $750/month.
- BFM receives no Personal goals, and the demo script continues not to open or seed Luxe Legacy.
- `scripts/smoke_test.py` now runs the demo seed twice under its own temporary root and verifies exact categories/subcategories, valid transaction and budget categories, both goal types, valid linked accounts, stable repeated output, no BFM goal leakage, and byte-for-byte Luxe Legacy preservation.
- `README.md` records the maintained synthetic demo contract.

## Verification

- Baseline full `.venv/bin/python scripts/smoke_test.py` — passed.
- First focused implementation run — correctly failed because a fresh database retained categories inserted by older migrations before the maintained domain was added.
- Narrow repair — always clear only the disposable Personal/BFM demo category tables before inserting the exact maintained domain.
- Python compilation — passed for `scripts/seed_demo_data.py` and `scripts/smoke_test.py`.
- Final full `.venv/bin/python scripts/smoke_test.py` — passed, including new section `7d2. Demo seed fidelity and idempotency`.
- Focused result:
  - Personal: 35 exact categories, 107 exact subcategories, 1,254 deterministic transactions, 16 valid budgets, two linked active goals.
  - BFM: 34 exact categories, 89 exact subcategories, 743 deterministic transactions, 19 valid budgets, zero goals.
  - Repeated same-day seed snapshot matched exactly.
  - Luxe Legacy sentinel database remained byte-for-byte unchanged.
- Disposable localhost Personal Dashboard — visually inspected; no removed-category/orphan warning appeared and all visible categories belonged to the maintained domain.
- Disposable localhost Short-Term Planning — visually inspected; both goal cards rendered with the expected names, debt/savings types, balances, and monthly amounts; the former `No goals yet` state was absent.
- Both rendered pages produced zero browser console warnings/errors.
- The exact managed root `/tmp/expense_5c_review.dcTcSV` is absent after the server stopped; its disposable synthetic contents were moved to the user's Trash for recoverable cleanup.

## Boundaries Preserved

No product template, stylesheet, JavaScript, route, category-domain file, migration, authentication, CSRF, CSP, PWA, recurring, Ask Opus, Luxe Legacy, mobile/dashboard design, workflow, or runtime configuration changed. No real financial row, credential, retained upload, live demo/production/Plaid/Fly/downstream access, staging, commit, push, PR, merge, workflow action, deployment, or preserved untracked-file mutation occurred.

## Next Gate

Task 2.2 becomes the sole Ryan-owned planning/decision gate. Before a 5D first-use and denied-state block can be finalized, Ryan should choose the Luxe Legacy primary first-use action. The recommended default is `Connect a Bank` as primary because Plaid is the maintained primary account integration, with `Import` as the visible secondary fallback. Task 2.3 and all later work remain separate.

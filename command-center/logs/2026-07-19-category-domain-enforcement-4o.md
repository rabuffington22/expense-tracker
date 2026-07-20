# Work Block 4O — Deterministic Category-Domain Enforcement

Date: 2026-07-19
Status: complete and verified locally; release not authorized

## Outcome

- `categories.md` is authoritative for new in-scope vendor inference and transaction, vendor-order, and accepted-match classification writes.
- Vendor inference receives the entity explicitly, preserves valid candidates, and falls back to `Needs Review` / `General` when a candidate is unmapped or invalid for that entity.
- Empty and `Unknown` subcategory input normalizes to the maintained implicit `General` subcategory.
- Henry Schein primary category selection ranks by frequency and resolves equal-frequency ties by normalized alphabetical order, producing the same result across tested hash seeds.
- Transaction-review batches prevalidate every submitted pair before the first transaction or merchant-alias write.
- Vendor-order saves and accepted order matches validate before changing orders, transactions, notes, match relationships, or aliases.
- The vendor categorization card no longer offers ad hoc subcategory creation outside `categories.md`.
- The dedicated `Skipped` vendor-queue action remains available as a workflow sentinel and cannot enter through inference or normal acceptance.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: pass.
- Focused maintained Personal, BFM, and Luxe Legacy checks: valid and invalid inference, valid pair persistence, invalid category and subcategory rejection, whole-batch zero mutation, accepted-match zero mutation, vendor-queue non-advancement, alias protection, dedicated skip behavior, entity isolation, denied outbound networking, and exact cleanup: pass.
- Henry Schein equal-frequency tie selection under `PYTHONHASHSEED` 1, 7, and 41: stable.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, command-center health, and generated-dashboard inspection: pass.

## Boundaries

No category or subcategory was added, renamed, or removed. No existing invalid row was detected, inspected, backfilled, or remediated. No migration, real database, financial row, retained upload, credential, live vendor or Plaid access, authenticated production page, workflow action, Fly operation, downstream access or write, commit, push, PR, merge, or deployment occurred. Both preserved untracked files remained untouched.

The latest natural Daily Plaid Sync remains run `29683898125`, which predates source commit `2a12533`; confirmed work block 4M therefore returns to current at its unchanged scheduled-run gate.

# Work Block 4U: Negative Appreciation Truthfulness

Date: 2026-07-20

Status: complete and verified locally; release not authorized

## Scope

Completed Phase 4 Task 1N.3 plus only the focused Task 2 regression slice for `P3-3D-04` and `P3-3D-C01` on local branch `codex/negative-asset-depreciation`.

Excluded throughout: Tasks 1N.4-1N.8; Tasks 1O-1P; broader Task 2; Tasks 3-4; rate-input policy changes; migrations; historical remediation; demo redesign or seed edits; templates; Weekly/Waterfall work; protected data; retained uploads; credentials; production/demo; external calls; live systems; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

## Implementation

- `web/routes/planning.py` now uses the existing future-value formula whenever the annual asset rate is nonzero, so ordinary negative rates compound as depreciation instead of falling into the zero-growth branch.
- The zero-rate branch remains explicit and linear, avoiding division by zero.
- Contribution timing, inflation adjustment, liability behavior, entity summaries, combined net worth, storage, routes, templates, schema, and demo seeds remain unchanged.
- `command-center/negative-appreciation-projection-contract.md` records the calculation and boundary contract.

## Exact Results

- $10,000 at -10% for five nominal years: $5,904.90.
- $85,000 demo-equivalent Equipment at -15% for five nominal years: $37,714.95.
- $10,000 at -10% with $100 monthly contributions for five years, then adjusted by 3% inflation: $9,332.58 in today's dollars.
- $10,000 at 0% with the same contributions and inflation: $13,801.74.
- $10,000 at +5% with the same contributions and inflation: $16,729.07.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including new section 8a4.
- Focused coverage: negative, zero, and positive rates; contributions; inflation; direct item and net-worth summaries; Personal/BFM route context; combined net worth; rendered depreciation labels; demo-equivalent Equipment decline; Luxe Legacy denial; denied networking; unrelated-row preservation; and exact cleanup.
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m py_compile web/routes/planning.py scripts/smoke_test.py`: pass.
- `python3 -m json.tool command-center/state.json`: pass.
- `git diff --check`: pass.
- `node command-center/scripts/refresh-dashboard.js`: pass.
- `node command-center/scripts/health-check.js`: pass.
- Rendered command-center inspection: current phase, block, task, owner, blockers, verification, and next action were coherent before closeout; final closed state was inspected after refresh.

One intermediate smoke run failed only because the new rendered-page assertion expected a long card name to remain contiguous, while the existing card-name macro intentionally splits the last word into a separate span. The observation was narrowed to stable rendered markers; calculation and reconciliation assertions were unchanged.

## Boundaries Preserved

No real database, financial row, retained upload, credential, external connection, production/demo surface, live action, migration, template, seed, commit, push, PR, merge, workflow, or deployment was used or changed. Both pre-existing untracked files remained untouched and unstaged.

## Learning

The depreciation defect was exactly the narrow branch mismatch identified in the audit: storage, labels, summaries, combined totals, and demo data already supported negative rates. Reusing the existing nonzero-rate formula fixes the full visible projection chain without a schema, UI, seed, or policy change. Task 1N.4 can therefore begin as a separate Weekly calculation block after Ryan chooses whether to publish 4U first.

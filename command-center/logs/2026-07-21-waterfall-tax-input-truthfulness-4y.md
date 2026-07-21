# Work Block 4Y — Waterfall Tax Input Truthfulness

Date: 2026-07-21

Status: complete and verified locally; publication not authorized

Branch: `codex/waterfall-tax-input-truthfulness`

## Scope

Completed Task 1N.8 plus only the focused Task 2 regression slice for `P3-3E-06` and matching `P3-3E-C01`. No Waterfall payoff change, migration, historical remediation, broad UI work, authentication change, protected data, credential, production/demo access, external call, workflow, Fly action, downstream write, GitHub durability, deployment, or other live action occurred.

## Result

- Replaced the float/raw-display split with one finite decimal normalization boundary.
- Rounded once with half-up semantics to integer basis points.
- Accepted normalized 0 through 9,999 basis points and retained the existing 2,200-basis-point safe default for omitted or invalid input.
- Derived both rendered controls, actual take-home, revenue-mode take-home, and take-home-mode gross and required revenue from the same accepted value.
- Stopped browser-side sign stripping so invalid signed text reaches the canonical server boundary instead of becoming a different positive number.
- Added the maintained `8a8` normalization, reconciliation, entity-boundary, denied-network, database-preservation, and exact-cleanup matrix.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including section 8a8.
- `.venv/bin/python -m py_compile web/routes/waterfall.py scripts/smoke_test.py`: pass.
- Omitted, blank, malformed, `NaN`, positive/negative infinity, negative, 100%, 99.995%, extreme, zero, integer, decimal, and half-up rounding cases: pass.
- Rendered rate, actual take-home, revenue mode, and take-home mode reconcile to the same basis points: pass.
- Personal and BFM intended behavior, Luxe Legacy denial, denied networking, unchanged seeded database state, and exact synthetic cleanup: pass.
- JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final worktree scope: pass at closeout.

Two intermediate `8a8` runs stopped in the new test harness before product assertions: the first retained Flask's template context by reference, and the second requested a month after the preceding section had correctly cleaned its BFM rows. The harness now snapshots context at render time and owns one isolated BFM fixture with explicit deletion and baseline restoration. No product-policy or implementation change was required by either harness correction.

## Boundary And Durability

All application checks used a disposable synthetic `DATA_DIR`. Both preserved untracked files remain untouched. The verified work is local-only on `codex/waterfall-tax-input-truthfulness`; commit, push, PR, merge, automatic deployment, production verification, and every other live action require a separately confirmed 4Y-R block.

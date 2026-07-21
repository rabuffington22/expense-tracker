# Work Block 4X: Waterfall Payoff Truthfulness

Date: 2026-07-21

Status: complete and verified locally; publication not authorized

## Scope

Completed Tasks 1N.6-1N.7 plus only the focused Task 2 regression slices for `P3-3E-03`, `P3-3E-05`, and `P3-3E-C01` on `codex/waterfall-payoff-truthfulness`.

## Result

- The selected Waterfall month and two preceding calendar months now form one fixed payoff window.
- Every signed monthly BFM surplus remains in the denominator. Deficit, zero, and no-row months are not filtered out; no-row months contribute zero.
- The displayed average and payoff helper use the same nearest-cent signed result. The `$1,000`, `-$2,000`, `$2,500` audit case now averages to `$500/month`.
- Positive debt and positive average surplus round completion upward to a whole month. The payoff date uses the same ratio converted at 30.44 days per month and rounded upward to a whole day.
- The page labels the value as a three-month signed average, reports when it leaves no surplus, and uses singular `month` for a one-month result.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including maintained section 8a7.
- `.venv/bin/python -m py_compile web/routes/waterfall.py scripts/smoke_test.py`: pass.
- Mixed, positive, zero, non-positive, missing-month, historical, and cross-year signed windows: pass.
- Sub-month, fractional, exact-multiple, zero-debt, and non-positive-surplus payoff cases: pass.
- Personal/BFM intended behavior, Luxe Legacy denial, denied networking, read-only database preservation, unrelated-row preservation, and exact cleanup: pass.
- JSON validation, `git diff --check`, dashboard refresh, health check, rendered-dashboard inspection, and final worktree scope: pass.

## Boundaries

No Task 1N.8 tax change, migration, historical remediation, broad UI work, authentication change, protected data, retained upload, credential, production/demo access, Plaid, external call, workflow, Fly action, downstream write, GitHub durability, deployment, or other live action occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.

## Learning

The optimistic payoff guidance came from two small rounding/filter choices in one narrow chain: filtering non-positive months inflated the input, then nearest-month rounding could erase a remaining fraction of debt. A fixed signed calendar window plus upward completion rounding repairs both without changing schema, trend navigation, entity boundaries, or tax behavior. Task 1N.8 can now focus only on tax input normalization.

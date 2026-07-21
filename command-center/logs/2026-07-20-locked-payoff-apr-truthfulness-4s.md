# Work Block 4S: Locked Payoff APR Truthfulness

Date: 2026-07-20

Status: complete and verified locally; release not authorized

## Scope Completed

- Added `apr_bps` to the maintained linked-account detail path used by Short-Term Planning.
- Removed the hard-coded 20% rate from locked payoff schedules.
- Used each linked card's stored non-negative integer APR, including a valid known 0% APR.
- Rejected missing or negative APR before changing the prior locked-plan row and returned controlled guidance to set APR in Cash Flow.
- Added focused maintained synthetic regression coverage for `P3-3D-01` and its locked-payoff `P3-3D-C01` slice.

## Synthetic Evidence

- Reversed-order equal-balance 9.99% and 29.99% cards produced exact month-one avalanche balances of `$983.32` and `$899.99`, with `$33.32` cumulative interest; the higher APR received the extra payment.
- A `$2,000` 9.99% card and `$500` 29.99% card produced exact month-one snowball balances of `$1,976.65` and `$387.50`, with `$29.15` cumulative interest; the smaller balance received the extra payment independently of APR and insertion order.
- Saved narrative prefixes, strategy, monthly amount, target date, and generated schedule rows reconciled to the same synthetic inputs.
- Missing and negative APR requests rendered controlled Cash Flow guidance and preserved the prior strategy, monthly amount, target date, narrative, and schedule exactly.
- A known 0% APR remained valid and produced a stored schedule.
- Personal and BFM positive paths passed; Luxe Legacy remained denied before the handler; outbound networking remained unused; focused rows cleaned up exactly.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including new section 8a2.
- `.venv/bin/python -m py_compile web/routes/short_term_planning.py scripts/smoke_test.py`: pass.
- `jq empty command-center/state.json`: pass at closeout.
- `git diff --check`: pass.
- `node command-center/scripts/refresh-dashboard.js`: pass.
- `node command-center/scripts/health-check.js`: pass.

## Preserved Boundaries

No template, Cash Flow APR-entry, migration, schema, historical-row, real-database, financial-row, upload, credential, production/demo, Plaid, workflow, Fly, downstream, GitHub durability, deployment, or live-system action occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.

## Durability

Local branch `codex/locked-payoff-apr-truthfulness` only. Commit, push, PR, merge, and deployment remain separately gated.

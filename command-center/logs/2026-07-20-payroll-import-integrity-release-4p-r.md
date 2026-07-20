# Work Block 4P-R — Payroll Import Integrity Durability And Release

Date: 2026-07-20
Source commit: `4b2775c403a631512d49d0fc0b8720a8495b5183`
Durability: published directly to `main`

## Published Scope

The exact twelve-path verified 4P source set was committed on `codex/payroll-import-integrity`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force:

- `core/payroll_parser.py`
- `web/routes/payroll.py`
- `web/templates/payroll.html`
- `scripts/smoke_test.py`
- `command-center/payroll-import-integrity-contract.md`
- `command-center/logs/2026-07-20-payroll-import-integrity-4p.md`
- `command-center/issues.md`
- `command-center/decisions.md`
- `command-center/now.md`
- `command-center/roadmap.md`
- `command-center/state.json`
- `command-center/index.html`

Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched and unstaged.

## Pre-Push Verification

- Local branch parent, local `main`, and fetched `origin/main` aligned at `f8df13f` before fast-forward publication.
- Maintained smoke passed, including exact matching, explicit reassignment, unmatched creation, reimport stability, deterministic payload lifecycle, malformed-workbook outcomes, all-entity isolation, denied networking, and exact cleanup.
- Python compilation, JSON validation, dashboard refresh, command-center health, `git diff --check`, explicit staged-path comparison, and high-confidence staged sensitive-addition scan passed.

## Automatic Release

- Pushing source commit `4b2775c` to `main` created automatic Fly Deploy run `29753360363` for that exact SHA.
- Deploy job `88389339278` completed successfully in every reported step.
- GitHub repeated the non-blocking Node 20 deprecation annotation for `actions/checkout@v4`, forced onto Node 24.
- Credential-free production `https://ledger-oak.fly.dev/health` returned HTTP 200.

## Boundaries Preserved

No protected data, retained upload, credential, authenticated production page, external call, manual workflow action, workflow edit, non-automatic Fly action, downstream access or write, migration, Task 1M.4 implementation, force push, or out-of-path recovery occurred.

This sanitized command-center-only closeout uses `[skip actions]` so it must not trigger a second Fly deployment.

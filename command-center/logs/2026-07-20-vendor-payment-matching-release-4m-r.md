# Work Block 4M-R — Vendor Payment Matching Durability And Release

Date: 2026-07-20
Source commit: `ffd42dd34160a860bf12998cf3cb22e73b5b3c63`
Durability: published directly to `main`

## Published Scope

The exact ten-path verified 4M source set was committed on `codex/vendor-payment-matching-integrity`, fast-forwarded to local `main`, and pushed directly to `origin/main` without force:

- `core/vendor_matching.py`
- `scripts/smoke_test.py`
- `command-center/vendor-payment-matching-contract.md`
- `command-center/logs/2026-07-20-vendor-payment-matching-4m.md`
- `command-center/issues.md`
- `command-center/roadmap.md`
- `command-center/now.md`
- `command-center/decisions.md`
- `command-center/state.json`
- `command-center/index.html`

Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched and unstaged.

## Pre-Push Verification

- Local branch parent, local `main`, and fetched `origin/main` aligned at `1af3ba9` before fast-forward publication.
- Baseline/final maintained smoke and the release rerun passed, including vendor-payment exact, review, unmatched, accepted, stale, duplicate, real two-thread claim, rollback, all-entity isolation, denied-network, and cleanup coverage.
- Python compilation, JSON validation, dashboard refresh, command-center health, `git diff --check`, explicit staged-path comparison, and high-confidence staged sensitive-addition scan passed.

## Automatic Release

- Pushing source commit `ffd42dd` to `main` created automatic Fly Deploy run `29748373589` for that exact SHA.
- Deploy job `88372068257` completed successfully in every reported step.
- GitHub repeated the non-blocking Node 20 deprecation annotation for `actions/checkout@v4`, forced onto Node 24.
- Credential-free production `https://ledger-oak.fly.dev/health` returned HTTP 200.

## Boundaries Preserved

No real database, financial row, upload, credential, authenticated production page, live vendor or Plaid call, manual workflow action, workflow edit, non-automatic Fly action, downstream access or write, migration, backfill, historical remediation, force push, or out-of-path recovery occurred.

This sanitized command-center-only closeout uses `[skip actions]` so it must not trigger a second Fly deployment.

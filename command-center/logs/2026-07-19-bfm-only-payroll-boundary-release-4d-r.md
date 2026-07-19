# Work Block 4D-R: Durability And Release

Date: 2026-07-19

Status: complete; durable on `main`; automatically deployed; credential-free health verified

## Source Durability

- Exact reviewed 4D source set: nine paths.
- Source commit: `7f7f71e` (`Enforce BFM-only payroll boundary`).
- Local `main` fast-forwarded from `e86ef0b` to `7f7f71e`.
- Direct push to `origin/main` succeeded without force.
- Local `main` and `origin/main` matched at the source SHA after the push.

## Automatic Deployment

- Workflow: Fly Deploy.
- Trigger: push of source commit `7f7f71e` to `main`.
- Run: `29691622134`.
- Job: `88205268889`.
- Result: success; every reported job step passed.
- No manual workflow dispatch, rerun, or non-automatic Fly mutation occurred.

## Credential-Free Verification

- Production `https://ledger-oak.fly.dev/health` returned HTTP 200.
- No password, authenticated production page, real database, protected payroll/HR/financial row, upload, credential, Plaid action, or downstream write was used.

## Final Boundaries

- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.
- 4E and every unrelated repair remain separately gated.
- This exact command-center closeout is published with `[skip actions]` so it does not trigger a second Fly deployment.

## Learning

The BFM-only payroll repair remained a narrow release: the exact locally verified source set deployed without recovery or credential use, and the public health contract stayed green. The next decision can therefore focus on the separate Luxe Legacy planning boundary rather than revisiting payroll release mechanics.

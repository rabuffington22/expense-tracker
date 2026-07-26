# Work Block 4BP — Browser CI Portability Repair Durability And Release

Date: 2026-07-26

Status: blocked at the confirmed unexpected-deployment-annotation stop after successful source durability, automatic deployment, and credential-free health verification

## Authorized Scope

Make only the host-verified transaction date-filter portability repair durable through a clean local release branch and direct non-force `main` push; observe only the resulting automatic exact-SHA Fly deployment; verify credential-free production health; publish sanitized Runway OS evidence; and stop without repair, rerun, cancellation, or broader recovery on any explicit 4BP stop condition.

## Exact Source Result

- Verified local, tracking, live GitHub, and remote `main` at baseline `a577d14e53aa1b47feffb6617733f67e518cc46c`.
- Verified retained hosted repair commit `bb6d14e7163e40976ffc2f0671509fd4b70f6a28` contained only `scripts/mobile_drawer_browser_test.py` and `web/static/style.css`.
- Created local-only `codex/browser-ci-portability-release` from the exact baseline. The branch was not pushed.
- Applied only the two approved repair paths without the observation marker or branch history.
- Full synthetic smoke, complete configured-auth/no-password installed-Chrome coverage, maintained CI safety, Python compilation, JSON, dashboard refresh/currentness/health and rendered inspection, whitespace, exact-path, sensitive-addition, cleanup, ancestry, remote, and preserved-file checks passed.
- Exact source commit `9b26030419b318af100bdc7d871d6c976fd02709` has sole parent `a577d14e53aa1b47feffb6617733f67e518cc46c`, contains 11 additions and four deletions across only the two approved files, and matches the retained hosted repair content.
- Local `main` fast-forwarded cleanly and one non-force push made the source commit durable on remote and GitHub `main`.

## Automatic Deployment Evidence

- Exactly one workflow exists for the source SHA: automatic push-triggered `Fly Deploy` run `30203353270`.
- Deploy job `89797056689` passed every step and completed in 2 minutes 7 seconds.
- Checkout, Fly setup, remote-only deployment, checkout cleanup, and job completion all succeeded.
- GitHub emitted one warning annotation: the operational workflow still uses `actions/checkout@v4`, which targets the deprecated Node.js 20 runtime and was forced onto Node.js 24 by the runner.
- The annotation is an explicit 4BP stop condition. No workflow edit, dispatch, rerun, cancellation, annotation suppression, action-pin change, repair, or broader recovery occurred.

## Safe Production And Boundary Evidence

- Credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200 with sanitized `{"status":"ok"}` after the exact deployment.
- Local, tracking, live GitHub, and remote `main` align at source SHA `9b26030419b318af100bdc7d871d6c976fd02709`.
- The retained observation branch remains at `bb6d14e7163e40976ffc2f0671509fd4b70f6a28`.
- The local release branch remains local and was not pushed or deleted.
- No PR mutation, manual workflow action, non-automatic Fly mutation, Plaid action, authenticated production page, production database, protected or real data, downstream action, credential access, force push, rebase, conflict resolution, or preserved-file mutation occurred.
- Preserved hashes remain:
  - `scripts/sync_prod_to_local.sh`: `2d612c8c1297d86055e394978be4cdac34ae014c`
  - `command-center/now 2.md`: `93eb6d4421c84c53ec4a5ab0a75a88c8ff268593`
  - duplicate 4AU log: `3fb681beeff241b5c0f44c1572ff6a14528cea21`

## Disposition

The two-file repair is durable, automatically deployed, and credential-free health verified, but 4BP remains blocked rather than complete because the deployment emitted the prohibited action-runtime warning. A separately planned and confirmed operational-workflow remediation decision is required before Phase 4 completion reconciliation. This evidence authorizes no such repair.

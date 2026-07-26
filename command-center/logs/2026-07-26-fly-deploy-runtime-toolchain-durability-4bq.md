# Work Block 4BQ — Fly Deploy Action Runtime And Toolchain Durability

Date: 2026-07-26

Status: complete, durable, automatically deployed, zero-annotation verified, and credential-free health verified

## Authorized Scope

Make only the production Fly deployment workflow action runtime and toolchain deterministic while preserving its existing trigger, concurrency, deployment command, and sole literal secret reference; extend maintained local enforcement and documentation; publish one exact source commit; observe only its automatic deployment; require zero annotations and credential-free HTTP 200 health; then publish one sanitized `[skip actions]` closeout.

## Exact Source Result

- Verified local, tracking, remote, and GitHub `main` at baseline `d1c1a297e13ed30baa8afc0c3ffe54e69888e749`.
- Verified checkout v7.0.1 commit `3d3c42e5aac5ba805825da76410c181273ba90b1` and Fly setup action commit `ed8efb33836e8b2096c7fd3ba1c8afe303ebbff1` are verified Node 24 action commits.
- Verified Fly CLI `0.4.74` and confirmed the successful 4BP deployment already used Ubuntu 24.04, Fly setup commit `ed8efb3`, and Fly CLI `0.4.74`.
- Created local-only `codex/fly-deploy-runtime-durability` from the exact baseline. The branch was not pushed.
- Exact source commit `b94009334cd129ccdb2f963a2e3d86045e0934d3` has sole parent `d1c1a297e13ed30baa8afc0c3ffe54e69888e749` and contains only:
  - `.github/workflows/fly-deploy.yml`
  - `README.md`
  - `command-center/fly-deploy-safety-contract.md`
  - `scripts/ci_safety_check.py`
- The workflow preserves push-to-`main`, the existing separately gated manual trigger, one deploy job, `deploy-group`, `flyctl deploy --remote-only`, and exactly one literal `FLY_API_TOKEN` reference without reading its value.
- The workflow now fixes `contents: read`, Ubuntu 24.04, a 20-minute timeout, non-persistent checkout credentials, checkout v7.0.1 at full SHA `3d3c42e`, Fly setup at full SHA `ed8efb3`, and Fly CLI `0.4.74`.
- The maintained standard-library checker now enforces both the Synthetic CI and Fly Deploy contracts. Disposable negative fixtures proved it rejects a mutable checkout, extra trigger, floating Fly CLI, and extra secret.
- Full synthetic smoke, complete configured-auth/no-password installed-Chrome coverage, positive and negative safety checks, Python compilation, JSON, dashboard refresh/currentness/health and rendered inspection, whitespace, sensitive-addition, exact-path, cleanup, ancestry, live-lane, remote, and preserved-file checks passed.
- Local `main` fast-forwarded cleanly and one non-force push made the source commit durable on remote and GitHub `main`.

## Automatic Deployment Evidence

- Exactly one workflow exists for source SHA `b94009334cd129ccdb2f963a2e3d86045e0934d3`: automatic push-triggered `Fly Deploy` run `30207408610`.
- Deploy job `89807770887` passed every step and completed in 44 seconds.
- The hosted log confirms:
  - Ubuntu 24.04;
  - `contents: read`;
  - checkout commit `3d3c42e5aac5ba805825da76410c181273ba90b1`;
  - `persist-credentials: false`;
  - Fly setup commit `ed8efb33836e8b2096c7fd3ba1c8afe303ebbff1`;
  - requested and acquired Fly CLI `0.4.74`; and
  - successful checkout, setup, remote-only deployment, checkout cleanup, and job completion.
- The job annotation API returned an empty list. The Node.js 20 warning that stopped 4BP did not recur.
- No manual dispatch, rerun, cancellation, workflow mutation after publication, or non-automatic Fly action occurred.

## Safe Production And Boundary Evidence

- Credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200 with sanitized `{"status":"ok"}` after the exact deployment.
- Local, tracking, remote, and GitHub `main` align at source SHA `b94009334cd129ccdb2f963a2e3d86045e0934d3` before the sanitized closeout.
- No Daily Plaid Sync, `SYNC_SECRET`, Synthetic CI behavior, application, Dockerfile, `fly.toml`, Fly secret/configuration, production database, authenticated production page, Plaid, demo, downstream, credential-value, protected-data, force-push, rebase, conflict-resolution, branch-deletion, or preserved-file action occurred.
- Preserved hashes remain:
  - `scripts/sync_prod_to_local.sh`: `2d612c8c1297d86055e394978be4cdac34ae014c`
  - `command-center/now 2.md`: `93eb6d4421c84c53ec4a5ab0a75a88c8ff268593`
  - duplicate 4AU log: `3fb681beeff241b5c0f44c1572ff6a14528cea21`

## Disposition

The production Fly deployment workflow now has a deterministic Node 24 action runtime and pinned toolchain, maintained fail-closed local enforcement, one clean hosted deployment with zero annotations, and healthy production. 4BQ is complete. Phase 4 completion reconciliation remains a separate 4BR planning and confirmation gate.

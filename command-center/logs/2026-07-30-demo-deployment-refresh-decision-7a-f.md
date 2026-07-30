# 7A-F — Demo Deployment Refresh Decision

Date: 2026-07-30
Status: done as decision-only at 4:10 AM CDT
Parent: Phase 7 — Operational Safeguards Activation And Currentness Proof
Included task: Task 1 (`P7-T1`) only
Owner: Codex Desktop

## Confirmed outcome

Decide a complete, exact contract for a later refresh of stale-with-respect-to-`/health` demo app `ledger-oak-demo`. This block performs no deployment, authentication, external read, health request, clean-snapshot creation, product change, protected access, or publication.

## Included tasks

1. Write and verify active 7A-F.
2. Select immutable source commit `1d149d787739495edc976bd81117abab1497f98d` only if local `HEAD` and cached `origin/main` align, required health/demo/runtime files exist, and there is no product diff.
3. Require a later deployment to use a disposable clean source derived from the exact selected commit.
4. Select exact target app `ledger-oak-demo`, config `fly.demo.toml`, existing local `flyctl v0.4.35`, and future command `flyctl deploy --app ledger-oak-demo --config fly.demo.toml --remote-only`.
5. Define the later protected action sequence: Ryan establishes exact-account Fly CLI authentication; Codex performs one sanitized exact-app status preflight; one deployment attempt; and one credential-free demo `/health` request.
6. Define success as HTTP 200, no redirect, and exact minimal `{"status":"ok"}`.
7. Preserve Release v9 and its observed image as the known previous-release reference. Do not automatically roll back or retry. Require separate rollback confirmation.
8. Preserve volume `ledger_oak_demo_data`; prohibit reseeding, database access, and data mutation.
9. Reconcile Runway OS with the complete future contract.

## Excluded tasks

1. Tasks 2-7 (`P7-T2`-`P7-T7`).
2. Deployment, restart, rollback, image change, hosted mutation, Fly authentication/status/release/log/config/secret/machine/database access, and HTTP.
3. The three unconsumed 7A reads, creation of the clean snapshot, and any `flyctl` invocation beyond local version/help inspection.
4. Product, route, test, workflow, dependency, README, Fly-config, Docker, credential, demo-seed, volume-access, protected, financial, Plaid, provider, production-data, Git fetch/stage/commit/push/PR/merge/publication, delegation, second opinion, successor, and unrelated work.

## Stop conditions

1. Local `HEAD` and cached `origin/main` drift.
2. A non-command-center product diff exists.
3. The selected commit lacks `/health`, its exemptions, demo config, or required runtime inputs.
4. The exact target app, config, or volume differs.
5. Local `flyctl` is absent, not v0.4.35, or lacks `--app`, `--config`, or `--remote-only`.
6. A disposable exact-commit source cannot be defined without inheriting dirty or untracked work.
7. The future authentication, preflight, deployment, health, failure, or rollback boundary cannot remain exact.
8. An external, product, install, deployment, or other excluded action becomes necessary.
9. A user change cannot be preserved, scope expands, or local command-center verification fails.

## Verification contract

1. Prove selected commit, local/cached ref equality, ancestry, required files, health route, and exemptions.
2. Prove zero product diff and exact app/config/volume.
3. Prove local Fly CLI version and required deploy flags without contacting Fly.
4. Prove the later clean source is derived from the exact commit and excludes all current dirty and untracked work.
5. Prove future counts of one preflight, one deploy attempt, and one health request; exact success response; sanitized evidence; no retry; and separately confirmed rollback.
6. Prove no external, authentication, snapshot, deployment, health, product, protected, Git-publication, delegation, second-opinion, or successor action.
7. Validate JSON and links, exactly one current task, exactly one active block during execution, dashboard refresh/currentness/health, generated markers, `git diff --check`, command-center-only scope, preserved files, and zero staging.

## Closeout target

On pass, mark 7A-F done as decision-only; keep Phase 7 at 0%; return Task 1 to Ryan as current and decision-needed; keep Tasks 2-7 planned; leave zero active blocks; and make a separately proposed `7A-N — Exact Demo Deployment Refresh And Health Proof` the smallest next gate. On contradiction, stop without deployment, retry, repair, or successor activation.

## Local evidence

1. Local `HEAD` and cached `origin/main` both equal immutable commit `1d149d787739495edc976bd81117abab1497f98d`.
2. The tracked health-route introduction is an ancestor of the selected commit. The selected tree contains `Dockerfile`, `requirements.txt`, `run.py`, `web/__init__.py`, `fly.demo.toml`, and `.dockerignore`.
3. Selected source registers `/health`, returns exact minimal `{"status":"ok"}` with HTTP 200, includes `/health` in the authentication-exempt set, and makes the authentication-exempt set entity-setup-exempt.
4. Selected demo configuration names exact app `ledger-oak-demo`, exact mounted volume `ledger_oak_demo_data`, destination `/data`, and internal port 8080.
5. Selected Docker input installs tracked requirements, copies the source context, and launches Gunicorn on port 8080. Because the current worktree contains command-center changes and `.dockerignore` has no whole-command-center exclusion, deployment from the current worktree is rejected.
6. `git diff --name-only` contains no non-command-center path, and the index is empty.
7. Existing `/opt/homebrew/bin/flyctl` reports v0.4.35 and local help exposes `--app`, `--config`, and `--remote-only`.
8. The selected commit tree does not contain this 7A-F log or any other current untracked file. A disposable `git archive` extraction from the exact commit therefore supplies only the immutable tracked tree and cannot inherit the current worktree's dirty or untracked state.

The first local evidence command contained two incorrectly quoted `git show <ref>:<path>` expressions. They failed locally before reading those paths, changed no state, and contacted no external service. The corrected local expressions passed. This command correction did not consume any future protected action.

## Accepted future 7A-N execution contract

This contract is not authorization to execute.

1. Ryan establishes Fly CLI authentication directly for the exact account owning globally unique app `ledger-oak-demo`. Codex does not request, read, type, copy, or retain credentials or MFA. Ambiguous account ownership or unavailable authentication stops.
2. Create one disposable directory only inside the separately confirmed 7A-N block. Populate it exclusively from `git archive --format=tar 1d149d787739495edc976bd81117abab1497f98d`; verify the selected commit, required files, no unexpected worktree-only path, and exact cleanup plan before any Fly action.
3. From that disposable directory, consume one sanitized exact-app status preflight for `ledger-oak-demo`. Retain only app targeting and readiness fields needed to prove the command is pointed at the exact app; do not retain configuration, secrets, logs, machine identifiers, IPs, database, volume contents, billing, organization, or actor details. Any failure, ambiguity, or excluded field stops with no retry.
4. If and only if the preflight passes, consume one deployment attempt from the disposable directory:

   `flyctl deploy --app ledger-oak-demo --config fly.demo.toml --remote-only`

   Do not add a seed, volume, database, secret, restart, rollback, or retry action. Preserve mounted volume `ledger_oak_demo_data`.
5. If and only if deployment reports success, consume one credential-free request to `https://ledger-oak-demo.fly.dev/health`. Do not follow redirects. Success requires HTTP 200, no redirect, and exact minimal JSON `{"status":"ok"}`.
6. On preflight failure, deployment failure, or health failure, stop after the consumed action. Do not repeat the preflight, deployment, or health request. Clean the disposable directory if safe; preserve sanitized evidence; report the exact stopped stage.
7. Release v9 and its already observed image remain the known previous-release reference. They are not exact Git-lineage proof and do not authorize rollback. Any rollback requires a new Ryan-confirmed target, command, effect, and verification block.
8. Do not resume the three unconsumed 7A currentness reads. Do not claim Task 1 or Phase 7 complete from demo health alone.

## Result

7A-F passes as decision-only. The selected source, clean-source method, exact target/config/command, CLI version, protected authentication handoff, one-preflight/one-deploy/one-health budget, exact health success response, no-retry stop, previous-release reference, separate rollback gate, volume preservation, sanitization, and cleanup boundaries are all exact. No external request, authentication, clean snapshot, deployment, health check, product change, protected access, Fly-hosted read or mutation, Git action, publication, delegation, second opinion, or successor occurred.

Phase 7 remains at 0%. Task 1 remains current and decision-needed under Ryan. Tasks 2-7 remain planned. There is no active work block. The smallest next gate is a separately proposed and confirmed `7A-N — Exact Demo Deployment Refresh And Health Proof`.

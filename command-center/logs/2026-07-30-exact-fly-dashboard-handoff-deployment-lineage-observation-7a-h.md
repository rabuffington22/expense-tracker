# Work Block 7A-H — Exact Fly Dashboard Handoff And Deployment-Lineage Observation

Date: 2026-07-30
Status: done as observation-only
Parent phase: Phase 7 — Operational Safeguards Activation And Currentness Proof
Included task: Task 1 (`P7-T1`) only

## Durable Activation

The exact confirmed 7A-H scope was written into `now.md`, `roadmap.md`, `decisions.md`, and `state.json` before any Fly interaction. JSON validation, exactly-one-current-task accounting, exactly-one-active-block accounting, dashboard refresh, generated markers, command-center health, whitespace, existing-file preservation, and zero staging passed.

## Bounded Observation

- Observation time: 2026-07-30 3:19 AM CDT.
- Navigation budget: maximum three read-only navigation actions.
- Navigation action 1: opened the exact Fly app path for globally unique app `ledger-oak-demo`.
- Sanitized result: Fly returned its sign-in surface with an exact return path to the requested app.
- Remaining navigation actions: two.
- Sensitive boundary: no account identity, organization, actor, credential, MFA value, secret, machine, IP, log, configuration, or other excluded metadata was read or retained.
- Mutation boundary: no setting, deployment, restart, rollback, repair, image, database, or other hosted state was changed.
- Retry boundary: no CLI or HTTP request was retried.

## Current Gate

The task-owned Chrome tab remains open for Ryan. Ryan signs in directly, verifies that the exact account owns `ledger-oak-demo`, and reports only:

`Exact Fly account and ledger-oak-demo ready`

The block remains active. It will stop without workaround if Ryan cannot establish the exact account safely.

## Ryan Handoff

At 3:27 AM CDT, Ryan returned the exact value-free readiness attestation:

`Exact Fly account and ledger-oak-demo ready`

No account identity, credential, MFA value, or broader confirmation was retained. The checkpoint passed and the bounded observation may resume with navigation action 1 of 3 consumed and two remaining.

## Release Observation

- Navigation action 2: reclaimed only the exact app tab and opened the unique `Release v9` link.
- Exact release URL: `https://fly.io/apps/ledger-oak-demo/releases/9`.
- Status: `Complete`.
- Image: `registry.fly.io/ledger-oak-demo:deployment-01KK97KM2PS5M48DT1HR4YW7ZG`.
- Created: March 9, 2026 12:02 UTC (7:02 AM CDT).
- Source commit: not exposed.
- Safe image-detail or source link: not exposed.
- Navigation action 3: unused.

## Classification

Exact image-source lineage remains unresolved. The confirmed block prohibits inferring exact lineage from release age alone, and the release page did not expose a source commit or safe image-detail link. The exact dated release/image evidence materially strengthens the stale-deployment hypothesis because it predates the March 27 health-route commit, but it is not recorded as exact source binding.

## Closeout

7A-H is done as observation-only. Phase 7 remains at 0%; Task 1 remains current and decision-needed; Tasks 2-7 remain planned. No account or organization identity, credential, MFA, excluded metadata, CLI or HTTP retry, logs, configuration, secrets, mutation, repair, restart, deployment, broader currentness, Git, publication, delegation, second opinion, or successor action occurred.

The smallest next gate is a separately planned `7A-M — Exact Demo Image-Lineage Evidence Decision`.

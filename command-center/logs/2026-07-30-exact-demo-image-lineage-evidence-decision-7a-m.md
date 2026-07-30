# Work Block 7A-M — Exact Demo Image-Lineage Evidence Decision

Date: 2026-07-30
Status: done as decision-only
Parent phase: Phase 7 — Operational Safeguards Activation And Currentness Proof
Included task: Task 1 (`P7-T1`) only

## Confirmed Scope

Reconcile only the existing sanitized demo 404, current `/health` source and exemptions, exact Release v9 status/image/timestamp, and local first-route commit chronology. If the evidence remains consistent, accept the narrow conclusion that `ledger-oak-demo` is stale with respect to `/health` while preserving full image-to-Git commit lineage as unresolved.

No network, UI, retry, repair, deployment, product change, protected access, Git publication, delegation, second opinion, or successor work is authorized.

## Durable Activation

7A-M was written and locally verified before evidence analysis.

## Evidence Reconciliation

1. Exact external behavior:
   - `https://ledger-oak-demo.fly.dev/health` returned HTTP 404 with no redirect and a sanitized standard not-found response on 2026-07-29.
2. Exact release evidence:
   - app: `ledger-oak-demo`;
   - release: v9;
   - status: `Complete`;
   - image: `registry.fly.io/ledger-oak-demo:deployment-01KK97KM2PS5M48DT1HR4YW7ZG`;
   - created: March 9, 2026 12:02 UTC (7:02 AM CDT);
   - source commit: not exposed.
3. Local source chronology:
   - demo commit `1a564e9a040162030c44cb52647fb1037f94694d`, committed March 3, lacks `/health`;
   - the parent of `1536244f9c77f8d6ef4e32fb4c9f90b22df45290` lacks `/health`;
   - `1536244f9c77f8d6ef4e32fb4c9f90b22df45290`, committed March 27, is the first tracked introduction of `/health` and adds the then-applicable entity-context exemption;
   - current `HEAD` and cached `origin/main` align at `1d149d787739495edc976bd81117abab1497f98d`;
   - current source retains `/health` and keeps it authentication- and entity-setup-exempt.

No evidence contradicted the observed 404, exact release, image, timestamp, or first-route chronology.

## Decision

Accepted narrow classification:

`ledger-oak-demo is stale with respect to /health — evidence sufficient`

Retained limitation:

`full image-to-Git commit lineage remains unresolved`

This classification does not identify the image's exact source commit and does not establish broader application currentness.

## Closeout

7A-M is done as decision-only. Phase 7 remains at 0%; Task 1 remains current and decision-needed; Tasks 2-7 remain planned. No network, UI, retry, repair, restart, rollback, deployment, product change, protected access, Git publication, delegation, second opinion, or successor action occurred.

The smallest next gate is a separately planned `7A-F — Demo Deployment Refresh Decision`.

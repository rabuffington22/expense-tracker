# Work Block 7A-D — Demo Deployment-Lineage Diagnosis

Date: 2026-07-29 CDT

Status: stopped on authenticated Fly metadata unavailability

## Confirmed Scope

Ryan confirmed Phase 7 Task 1 (`P7-T1`) only for a read-only diagnosis of whether the `ledger-oak-demo` deployment predates the tracked `/health` route.

The block first reconciles local route, exemption, demo configuration, deployment mechanics, commit lineage, and historical evidence. It may then consume at most three exact Fly metadata observations: app status, releases with image, and only-if-needed current image details. Every outbound attempt counts. Raw metadata is disposable; only sanitized app, release, timestamp, status, image/digest, and source-lineage fields may be retained.

Another HTTP request, the three unconsumed 7A reads, Fly logs/config/environment/secrets, actor identity, mutation, restart, deployment, rollback, demo seed, database, financial, authentication, Plaid, provider, protected data, product or deployment-source changes, repair, Git, publication, delegation, second opinion, Tasks 2-7, and successor work are excluded.

## Local Diagnosis

Local source and history checks passed:

- current `web/__init__.py` registers `/health` and exempts it from authentication and entity setup;
- `fly.demo.toml` targets exact app `ledger-oak-demo`, uses the shared Docker build and Gunicorn runtime, and documents a manual `fly deploy --config fly.demo.toml --remote-only` path;
- no tracked GitHub workflow deploys `fly.demo.toml`;
- demo commit `1a564e9a040162030c44cb52647fb1037f94694d` was created on 2026-03-03;
- health-route commit `1536244f9c77f8d6ef4e32fb4c9f90b22df45290` followed on 2026-03-27;
- current `HEAD` and cached `origin/main` are aligned at `1d149d787739495edc976bd81117abab1497f98d` and contain the health route;
- historical demo HTTP evidence records root availability only. The first exact demo `/health` evidence is the stopped 7A HTTP 404.

These facts support a stale demo deployment as the leading hypothesis, but they do not bind the running Fly image to a Git source revision.

## Fly Observation

Observation time: 2026-07-29 11:22 PM CDT

Authorized budget: at most three read-only Fly metadata observations.

Consumed: one.

1. Existing `flyctl v0.4.35` attempted exact app status metadata for `ledger-oak-demo`.
   - Result: authentication-or-authorization failure.
   - No credential, token, account value, Fly response body, app metadata, actor identity, log, configuration, secret, or machine detail was retained.
   - The exact disposable capture files and directory were removed by the registered exit cleanup.

The response consumed the first observation and triggered the confirmed safe stop. Release-with-image and conditional image-detail observations were not attempted. Browser and Computer Use were not used because the failure was authentication/authorization, not a visible UI-control failure.

## Classification And Next Gate

Classification: **stopped — stale-deployment hypothesis supported locally, exact deployed-image lineage unresolved because authenticated Fly metadata was unavailable**.

No HTTP request, retry, authentication action, credential entry, log/config/secret access, mutation, repair, restart, deployment, protected-data access, product change, Git action, or successor work occurred.

Phase 7 remains at 0% and Task 1 (`P7-T1`) remains current and decision-needed. The smallest next gate is a separately planned Ryan-owned exact Fly account handoff or already-authenticated task-owned Fly dashboard observation for `ledger-oak-demo`, followed only by the remaining sanitized deployment-lineage metadata. It does not authorize credential handling by Codex, another health request, repair, restart, or deployment.

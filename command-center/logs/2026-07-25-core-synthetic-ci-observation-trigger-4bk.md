# Core Synthetic CI Observation Trigger — 4BK

Date: 2026-07-25

Purpose: provide one sanitized, branch-only repository change so the durable pull-request-only `Synthetic CI` workflow can be observed on GitHub.

Boundaries:

- synthetic checks only;
- no credentials, secrets, financial rows, databases, uploads, or protected data;
- no product, workflow, dependency, configuration, deployment, Fly, Plaid, production, demo, or downstream change;
- this marker is not intended for merge into `main`;
- the draft PR should be closed without merge after a successful observed run.

Expected base: `main` at `65b6b7aa37fcd1f9ff88a82b161a4afa54960006`.

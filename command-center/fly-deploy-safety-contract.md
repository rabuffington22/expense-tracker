# Fly Deploy Safety Contract

## Purpose

Keep production deployment behavior explicit, deterministic, and locally reviewable without exposing credentials or authorizing manual workflow action.

## Exact Workflow Contract

`.github/workflows/fly-deploy.yml` must retain:

- workflow name `Fly Deploy`;
- automatic execution only for pushes to `main`, plus the existing separately gated `workflow_dispatch` surface;
- top-level `contents: read` token permission;
- one `deploy` job named `Deploy app`;
- explicit `ubuntu-24.04`;
- a 20-minute timeout;
- `deploy-group` concurrency;
- checkout v7.0.1 pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1`;
- `persist-credentials: false`;
- the Node 24 Fly setup action pinned to `ed8efb33836e8b2096c7fd3ba1c8afe303ebbff1`;
- Fly CLI `0.4.74`;
- the sole command `flyctl deploy --remote-only`; and
- exactly one literal `FLY_API_TOKEN` secret reference, whose value is never read or logged by local verification.

The selected runner, Fly setup action commit, and Fly CLI version match the successful 4BP deployment inputs. The checkout pin is the verified Node 24-compatible v7.0.1 release.

## Maintained Enforcement

`scripts/ci_safety_check.py` uses only the Python standard library and fails closed unless both the PR-only Synthetic CI contract and this exact Fly Deploy contract remain intact. It rejects added triggers, jobs, commands, secrets, mutable action references, checkout credential persistence, runner drift, tool-version drift, or other structural changes by requiring the reviewed significant-line sequence and immutable action list.

Run:

```bash
.venv/bin/python scripts/ci_safety_check.py
```

Passing this local check does not authorize publication, manual dispatch, rerun, cancellation, secret access, deployment, or any other live action. Those remain target-specific work-block gates.

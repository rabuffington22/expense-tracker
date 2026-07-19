# Work Block 4K-R — Plaid Item Isolation And Observability Release

Date: 2026-07-19

Status: complete; source durable on `main`, automatically deployed, credential-free production health verified, and sanitized closeout prepared for `[skip actions]` publication.

## Source Durability

- Exact source commit: `72d2bbaed19bee431ce8bee12e41ef891c0fedd2` (`Repair Plaid item isolation and observability`).
- Exact published set: `web/routes/plaid.py`, `scripts/smoke_test.py`, the 4K contract and local verification log, `command-center/issues.md`, and the five active Runway OS source/dashboard paths.
- Local `main` was fast-forwarded from `18811d1` to `72d2bba`; `origin/main` accepted the same fast-forward without force.
- The staged set contained exactly ten authorized paths.
- High-confidence staged sensitive-addition scan: zero matches.
- Full maintained smoke, Python compilation, JSON validation, dashboard refresh, command-center health, whitespace, visual dashboard, and exact-path checks passed before commit.

## Automatic Deployment

- Workflow: Fly Deploy.
- Run: `29700530131`.
- Job: `88228726512` (`Deploy app`).
- Workflow head SHA: `72d2bbaed19bee431ce8bee12e41ef891c0fedd2`.
- Result: success; every reported job step passed.
- GitHub annotation: `actions/checkout@v4` still targets deprecated Node 20 and was forced onto Node 24. This was non-blocking and did not affect the deploy.

## Credential-Free Production Verification

- `https://ledger-oak.fly.dev/health`: HTTP 200.
- No credential, authenticated production page, protected response body, real database, financial row, live Plaid call, manual workflow action, non-automatic Fly mutation, or downstream access was used.

## Preserved Exclusions

- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.
- Unrelated untracked `command-center/now 2.md` remained untouched and unstaged.
- Task 1K, scheduled/public coordination, `/k/` changes, broader sync-entry work, workflow-file changes, unrelated repairs, force push, and recovery outside the exact release path remained excluded.

## Closeout

This command-center-only `[skip actions]` closeout contains this release log plus the updated roadmap, decisions, now, state, and generated dashboard. JSON validation, dashboard refresh, command-center health, whitespace checks, and visual inspection passed; the dashboard shows 4K and 4K-R done, Task 1K current under Ryan, and 4L planning as the next gate. After publication, final main/origin alignment and the absence of a second Fly deployment are verified externally without adding another commit.

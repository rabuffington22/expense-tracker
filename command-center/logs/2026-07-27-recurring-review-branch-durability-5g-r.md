# 5G-R Recurring Review Branch Durability And Hosted Review

Date: 2026-07-27

Status: active

## Confirmed Scope

Make the already verified Task 2.4 and 5G/5G-RS package durable on `codex/recurring-review-surface`, open one draft PR targeting `main`, require automatic core-then-browser Synthetic CI on the source and closeout heads, prove zero Fly deployment, and stop with the PR open, draft, unmerged, and retained.

## Exact Initial Package

- `README.md`
- `scripts/smoke_test.py`
- `web/routes/subscriptions.py`
- `web/static/style.css`
- `web/static/subscriptions.js`
- `web/templates/subscriptions.html`
- `web/templates/todo.html`
- `command-center/decisions.md`
- `command-center/index.html`
- `command-center/now.md`
- `command-center/roadmap.md`
- `command-center/state.json`
- `command-center/logs/2026-07-27-recovered-database-application-verification-5g-av.md`
- `command-center/logs/2026-07-27-human-verified-dashboard-reentry-5g-av-r.md`
- `command-center/logs/2026-07-27-recurring-review-safe-resume-5g-rs.md`
- `command-center/logs/2026-07-27-recurring-review-branch-durability-5g-r.md`

## Protected Boundary

The recovered originals remain hash/metadata/owner/sidecar-only and must not be opened through SQLite or Flask. The duplicate 4AU log, `command-center/now 2.md`, and `scripts/sync_prod_to_local.sh` remain untouched and excluded. Merge, `main`, production, deployment, production health, manual workflow action, Task 2.5, product correction, protected data, delegation, second opinion, and every expansion remain excluded.

## Next Report Point

Return exact staged paths, source and closeout commits, branch and draft PR, both automatic hosted results, annotations, zero-deployment proof, preserved exclusions, dashboard closeout, and the separately gated 5G-R2 decision.

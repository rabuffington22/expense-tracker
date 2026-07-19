# Current Focus

## Active Objective

Publish and verify the completed 4K Plaid item-isolation and observability repair through the directly authorized 4K-R exact-path release.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active.

## Current Work Block

4K-R Durability And Release — active and directly authorized by Ryan on 2026-07-19.

## Current Task

Phase 4 Task 1J release durability plus Task 4 only. The local 4K repair and focused Task 2 coverage slice are already complete and verified.

## Owner

Codex Desktop owns exact-path staging, source commit, fast-forward publication to `main`, automatic Fly deployment observation, credential-free production health verification, sanitized closeout, and final intake.

## Current Action

Reverify and stage only the exact ten intended 4K paths, commit on `codex/plaid-item-isolation-observability`, fast-forward local `main`, push `origin/main`, observe the automatic Fly deployment, verify credential-free `/health`, then publish a command-center-only `[skip actions]` closeout.

## Exact Source Set

- `web/routes/plaid.py`
- `scripts/smoke_test.py`
- `command-center/plaid-item-isolation-observability-contract.md`
- `command-center/logs/2026-07-19-plaid-item-isolation-observability-4k.md`
- `command-center/issues.md`
- `command-center/decisions.md`
- `command-center/now.md`
- `command-center/roadmap.md`
- `command-center/state.json`
- `command-center/index.html`

## Excluded

- Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md`.
- Real databases or financial/payroll/HR rows, uploads, credentials, authenticated production pages, live Plaid, manual workflow actions, non-automatic Fly changes, downstream access/writes, workflow edits, Task 1K, broader sync-entry work, and unrelated repairs.
- Force push and recovery beyond the exact fast-forward path.

## Stop Conditions

- Exact diff or staging contains an unexpected path, sensitive value, protected data, or unrelated user change.
- Local or remote `main` diverges or cannot be fast-forwarded safely.
- Maintained verification, JSON, dashboard refresh, health, whitespace, or sensitive-addition checks fail.
- Automatic deployment fails or cannot be attributed to the source SHA.
- Credential-free production health fails, a second deploy starts for closeout, or recovery exceeds authorization.

## Verification

- Exact path, status, diff, branch ancestry, remote alignment, and high-confidence sensitive-addition review.
- `.venv/bin/python scripts/smoke_test.py` and `.venv/bin/python -m py_compile web/routes/plaid.py scripts/smoke_test.py`.
- `jq empty command-center/state.json`, dashboard refresh, command-center health check, `git diff --check`, generated-dashboard inspection, and explicit staged-set review.
- Source commit, fast-forward local `main`, direct push to `origin/main`, automatic Fly run/job result, credential-free production `/health`, final main/origin alignment, preserved exclusions, and sanitized `[skip actions]` closeout publication.

## Next Report Point

Return source and closeout commits, exact published paths, automatic workflow result, credential-free production health, final main alignment, preserved exclusions, and the separate Task 1K planning gate.

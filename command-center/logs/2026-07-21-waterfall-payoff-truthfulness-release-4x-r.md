# Work Block 4X-R Release Evidence

Date: 2026-07-21

Status: complete, durable, automatically deployed, and credential-free production health verified

## Source publication

- Source commit: `dc128903bb7dd21cc3516a6742ce9d083f66bbc1`
- Branch: `codex/waterfall-payoff-truthfulness`, fast-forwarded into local `main`
- Remote: direct fast-forward push to `origin/main`; no force and no PR
- Published set: the exact eleven verified 4X application, template, maintained-test, contract, issue, evidence, and Runway OS paths
- Staged high-confidence sensitive-addition scan: zero matches

## Automatic deployment

- Fly Deploy run: `29830719921`
- Deploy job: `88634537268`
- Trigger: push
- Head SHA: `dc128903bb7dd21cc3516a6742ce9d083f66bbc1`
- Result: success; every reported job step passed without opening deployment logs
- Non-blocking annotation: `actions/checkout@v4` targets deprecated Node 20 and was forced to Node 24

## Health and boundaries

- Credential-free production `/health`: HTTP 200
- Local `main` and `origin/main`: aligned at the exact source SHA before closeout
- No PR, protected data, retained upload, credential, authenticated production page, manual workflow action, workflow edit, non-automatic Fly change, downstream access/write, migration, Task 1N.8 implementation, force push, or unrelated recovery occurred.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched and unstaged.

## Closeout

The sanitized command-center-only closeout commit uses `[skip actions]` so it cannot start a second Fly deployment. Task 1N.8 returns to a separate planning gate.

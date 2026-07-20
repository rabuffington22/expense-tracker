# Work Block 4R-R Closeout: Like-For-Like Payroll Peer Comparisons Durability And Release

Date: 2026-07-20
Status: complete

## Durable Source

- Source commit: `edaa853d2177adb1a5a9c31d2c56e6df42a6df88`
- Publication path: exact fast-forward from `codex/payroll-compensation-cohorts` to local `main`, then direct push to `origin/main`
- Published set: the exact eleven reviewed 4R application, maintained-test, contract, issue, evidence, and Runway OS paths
- Sensitive-addition result: zero high-confidence staged matches

## Automatic Release Evidence

- Fly Deploy run: `29778504012`
- Deploy job: `88473691178`
- Attribution: push event on `main` for exact source SHA `edaa853d2177adb1a5a9c31d2c56e6df42a6df88`
- Result: run, job, and every reported step succeeded
- Non-blocking annotation: `actions/checkout@v4` targeted deprecated Node 20 and was forced onto Node 24
- Credential-free production `/health`: HTTP 200

## Preserved Boundaries

- `command-center/now 2.md` and `scripts/sync_prod_to_local.sh` remained untouched and unstaged.
- No protected payroll, HR, or financial row data; retained upload; credential; authenticated production page; manual workflow action; non-automatic Fly change; downstream access or write; migration; Task 1N implementation; force push; or unrelated repair was used or performed.
- This sanitized command-center-only closeout is published with `[skip actions]` and must not start a second deployment.

## Next Gate

Task 1N returns to a separately proposed and confirmed planning pass. No Task 1N implementation is authorized by this closeout.

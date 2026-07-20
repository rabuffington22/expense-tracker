# Work Block 4L-R — Sync Entry Coordination Release

Date: 2026-07-19

Status: complete, durable, automatically deployed, and credential-free production verified

## Publication

- Source branch: `codex/sync-entry-coordination`
- Exact staged source set: fifteen intended 4L paths
- Source commit: `2a12533d637060ce2ea91ff205b30cde3cbbc99a`
- Target: direct fast-forward of local `main`, then `origin/main`
- Force push: not used
- High-confidence staged sensitive-addition scan: zero matches

The source commit contains the shared sync coordinator, manual/scheduled/dashboard integration, maintained synthetic coverage, contract, reviewer packet and response, issue resolution, implementation closeout, and active release record. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated `command-center/now 2.md` remained untouched and unstaged.

## Automatic Deployment

- Workflow: Fly Deploy
- Run: `29711640510`
- Deploy job: `88256335090`
- Exact head SHA: `2a12533d637060ce2ea91ff205b30cde3cbbc99a`
- Result: success; every reported job step passed
- Non-blocking annotation: GitHub again reported that `actions/checkout@v4` targets deprecated Node.js 20 and was forced onto Node.js 24.

No manual workflow dispatch, rerun, non-automatic Fly mutation, authenticated production access, credential access, or live Plaid call occurred.

## Safe Production Verification

- Credential-free `GET https://ledger-oak.fly.dev/health`: HTTP 200
- Credential-free missing-bearer `POST https://ledger-oak.fly.dev/plaid/sync-all` with redirects disabled: HTTP 401, no redirect

The missing-bearer result confirms that configured browser authentication no longer converts the scheduled endpoint boundary into a 302 before bearer validation. Because no authorized bearer was supplied, this check did not initialize an entity or enter Plaid synchronization. It therefore does not prove a real scheduled sync succeeds; the next natural scheduled run remains the safe production truth point.

## Closeout

This log and the aligned Runway OS state are published in a separate command-center-only commit whose message includes `[skip actions]`, preventing another automatic deployment. Tasks 1L-1P, broader Task 2, Tasks 3-4, `/k/` access policy, real databases or protected rows, credentials, live Plaid, manual workflow action, non-automatic Fly change, downstream access or write, workflow edit, and unrelated repair remain outside this block.

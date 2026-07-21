# Work Block 4AF-R — Shared CSP Execution Foundation Durability And Release

Date: 2026-07-21

Status: complete, durable, automatically deployed, and credential-free production health verified

## Published Source

- Source commit: `80dd7761c13cc9da94e9a26a8326871622734be6`
- Branch path: committed on `codex/csp-shared-execution-foundation`, then cleanly fast-forwarded to local `main`
- Remote result: `origin/main` accepted the direct non-force push and resolved to the exact source SHA before closeout
- Scope: exactly fifteen verified 4AF application, static-asset, maintained-test, CSP contract, issue, findings, evidence, and Runway OS paths
- No PR was created.

## Release Verification

- Automatic GitHub Actions workflow: Fly Deploy run `29873831453`
- Deploy job: `88779843248`
- Trigger and source: push to `main` for exact SHA `80dd7761c13cc9da94e9a26a8326871622734be6`
- Result: every reported deployment step passed
- Credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200 after the successful deployment
- GitHub reported the existing non-blocking Node 20 deprecation annotation for `actions/checkout@v4`, forced onto Node 24

## Pre-Publish Verification

- The full maintained synthetic smoke suite passed, including shared CSP execution assertions.
- The maintained isolated-browser shared-shell matrix passed in configured-auth and no-password modes with denied non-localhost requests and exact cleanup.
- Python and JavaScript syntax, JSON, whitespace, dashboard refresh, command-center health, rendered active-release inspection, zero browser-console errors, and no horizontal overflow passed.
- Explicit staging contained exactly fifteen approved paths. Protected-path and high-confidence sensitive-addition checks returned zero matches.

## Boundaries

No Task 1P.4.2b work, new product mutation, credential, protected data, real database, retained upload, authenticated production page, manual workflow action, workflow edit, non-automatic Fly mutation, downstream access or write, PR, force push, or broader recovery occurred. The unrelated untracked `scripts/sync_prod_to_local.sh` and `command-center/now 2.md` files remained excluded.

## Next Gate

Task 1P.4.2b remains unconfirmed. Run a separate just-in-time sizing pass over the verified fragment inventory before proposing any implementation block.

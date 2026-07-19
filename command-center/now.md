# Current Focus

## Active Objective

Publish and verify the approved server-authentication and protected-cache repair through one bounded production release block.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active; Task 1A is verified locally and work block 4B is authorized for exact GitHub durability, merge-triggered Fly deployment, and credential-free production verification.

## Active Work Block

4B: Publish And Verify Auth Repair — confirmed by Ryan; publish `codex/server-side-auth-boundary` through a reviewed PR, merge to `main`, monitor the resulting Fly deployment, verify only public/pre-auth boundaries, and publish the sanitized closeout.

## Current Task

Phase 4 Task 4: deploy the explicitly approved 4A repair and verify the production boundary without credentials or protected data.

## Owner

Codex Desktop owns pre-release review, exact-path staging, branch push, PR/check/merge handling, Fly deployment monitoring, credential-free production verification, closeout durability, and dashboard currency. Ryan remains the final decision-maker for any scope expansion, credential use, or recovery outside 4B.

## Audit Result

The tracked synthetic smoke suite passed. The repeated temporary request probe produced 31 expected passes and 12 controlled findings. The repeated isolated Chromium probe produced 23 expected passes and six controlled findings with zero external requests, zero manifest errors, correct icon dimensions, and complete disposable cleanup.

Manifest/installability, icons, root service-worker registration, branded offline fallback, desktop/tablet/phone overflow, basic drawer state, public Personal/LL versus BFM isolation, CSRF, exempt routes, HSTS-on-HTTPS, and basic security headers passed.

Seven finding clusters were recorded: the main authentication boundary exposes full protected HTML and a reusable client digest; service-worker caching crossed BFM content into an offline Personal request; `/k/` intentionally exposes detailed Personal and LL financial data; auth configuration/no-password mode drifts; the mobile drawer lacks focus/Escape/scroll handling; cookie/CSP hardening is incomplete; and tracked regression coverage is absent.

## Current Action

Validate and publish the exact 4A diff, merge only after required checks pass, monitor the merge-triggered Fly deployment, verify `/health`, pre-auth root/login behavior, and service-worker v4 without signing in, then publish a command-center-only closeout with `[skip actions]`.

## Durability

- Work block 4B authorizes staging and committing only the intended 3J/4A application, tracked-test, documentation, and command-center paths; pushing `codex/server-side-auth-boundary`; opening and merging a reviewed PR after checks; observing the automatic Fly deployment; public/pre-auth HTTP verification; and one sanitized command-center-only `[skip actions]` closeout.
- No real password, credential rotation, Fly secret change, authenticated production page, financial row, database, Plaid action, manual workflow dispatch, downstream write, or `/k/` content/access change is authorized.
- Preserved user file: untracked `scripts/sync_prod_to_local.sh`, untouched and unstaged.

## Work Block 4B Boundary

- Included tasks: Task 1A release durability and Task 4 explicitly approved deployment.
- Verification: exact diff and sensitive-string review; maintained synthetic suite; command-center refresh/health; required PR checks; Fly deployment result; production `/health` 200; protected root redirect to `/auth/login`; login response contains no protected HTML or reusable digest; `/sw.js` reports cache v4/static-only behavior; final main/origin alignment.
- Stop on unexpected or sensitive diff content, branch conflict, failed required check or deployment, protected pre-auth content, need for a real credential or protected data, or any change beyond the approved repair and closeout.
- Excluded tasks: Task 1B and Tasks 2-3; credential modernization; public `/k/` policy; mobile navigation; cookie/CSP hardening; unrelated findings and recovery outside the exact release path.

## Work Block 4A Result And Boundary

- Completed locally: server-side login enforcement, removal of client digest replay, coherent no-password mode, static/offline-only service-worker caching, old-cache cleanup, focused synthetic regression coverage, isolated-browser verification, visual inspection, and disposable cleanup.
- Excluded: `/k/` access or content changes; mobile drawer behavior; cookie or CSP hardening; real credentials or credential rotation; real databases or financial rows; production/demo/external calls; Plaid, Fly, workflows, or downstream writes; commit, push, PR, merge, deployment; unrelated audit findings; and pre-existing untracked `scripts/sync_prod_to_local.sh`.
- Verification: maintained smoke and focused request contracts passed; configured-auth Chromium passed 19/19, no-password Chromium passed 2/2, zero external requests occurred, the visual login/offline review passed, and all 3J/4A disposable files were removed.
- Release gate: production behavior remains unchanged until separately authorized GitHub durability and deployment.

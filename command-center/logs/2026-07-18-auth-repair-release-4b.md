# Work Block 4B — Publish And Verify Auth Repair

Date: 2026-07-18

Status: released and verified

## Durability

- Source commit: `fe1ec2e` (`Enforce server-side auth boundary`)
- Pull request: `#86`, merged to `main`
- Merge commit: `f4cd686`
- Fly Deploy run: `29670793359`, successful for merge commit `f4cd686`
- PR checks: GitHub reported no checks configured; mergeability and merge state were clean, so the maintained local suite and 4A browser evidence remained the pre-merge verification gate.

## Pre-Release Verification

The exact 14-path source/test/docs/evidence set was reviewed and staged explicitly. The high-confidence secret scan found no matches. The maintained synthetic suite, auth/cache regression checks, Python compilation, service-worker syntax, dashboard refresh, command-center health, and whitespace checks passed. `origin/main` matched the branch base before commit. The pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Production Verification

- `https://ledger-oak.fly.dev/health` returned HTTP 200 with `Cache-Control: no-store`.
- Unauthenticated `https://ledger-oak.fly.dev/` returned HTTP 302 to `/auth/login?next=/` with `Cache-Control: no-store`.
- The public login response contained the standalone password form and no protected sidebar/main shell, reusable client digest state, `atlas-auth`, `authOverlay`, or `/auth/verify` client path.
- `/sw.js` served cache v4, excluded protected root precache, contained no dynamic-cache fallback, and retained only the single static runtime cache path.
- No password, authenticated production page, protected financial data, `/k/` content, database, credential, Fly secret, Plaid action, manual workflow dispatch, or downstream write was used.

## Closeout

The locally verified repair is now released on `main`. The authentication, cross-entity protected-cache, and client/server auth-mode issues are resolved in production. The public `/k/` policy decision, credential modernization, mobile navigation, cookie/CSP hardening, remaining audit findings, and maintained browser coverage remain separate work. Phase 3 Task 7 resumes for a separately confirmed findings-consolidation block.

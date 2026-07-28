# Work Block 5H-R2 — Ask Exact-Main Deployment Observation and Release Closeout

Date: 2026-07-28

Status: complete locally; exact release deployed and historical production health verified

## Authority And Scope

Ryan confirmed Task 4.4 (`P5-T44`) only after the separately recorded direct-push override placed the Ask Opus and operator-handoff package on `main` despite the unresolved OpenRouter Broadcast boundary. This block authorized only exact-SHA read-only GitHub observation, one credential-free production `/health` request after deployment evidence passed, sanitized local Runway OS evidence, and automatic dashboard closeout.

No commit, push, PR mutation, workflow action, Fly administration, rollback, repair, retry, OpenRouter access, Broadcast inspection or mutation, provider request, protected data, financial data, Task 4.5, parent update, parked Task 2 work, delegation, or second opinion occurred.

## Exact Release Baseline

- Local `HEAD`, cached `origin/main`, and local `codex/ask-opus-privacy` were `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7` before activation.
- Live GitHub `main` revalidation returned the same exact SHA.
- The release head has sole parent `257bec901e88b830fcafe6067c8174cd6a5213b6`.
- GitHub compare classified the release as exactly one commit ahead and zero behind that parent.
- The release delta contained exactly nine command-center paths:
  - `command-center/decisions.md`
  - `command-center/index.html`
  - `command-center/logs/2026-07-27-ask-operator-package-durability-5h-r.md`
  - `command-center/logs/2026-07-28-openrouter-account-privacy-verification-5h-pv.md`
  - `command-center/now.md`
  - `command-center/phase-5-release-evidence-map.md`
  - `command-center/phase-5-release-handoff.md`
  - `command-center/roadmap.md`
  - `command-center/state.json`

## Pull Request State

Read-only GitHub metadata classified PR #91 as closed and merged at the release time. Its recorded head and merge SHA are both `257bec901e88b830fcafe6067c8174cd6a5213b6`; the branch head entered `main` through Ryan's separately authorized direct fast-forward push rather than a PR mutation in this block. The PR remained marked draft in the returned metadata. No PR field changed during 5H-R2.

## Automatic Deployment

- Exactly one push-event workflow run existed for release SHA `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`.
- Workflow: `Fly Deploy`.
- Run: `30350587286`.
- Event and branch: automatic `push` on `main`.
- Attempt: 1.
- Status and conclusion: completed successfully.
- Job: `Deploy app`, ID `90246858468`, completed successfully.
- Every returned step completed successfully: Set up job, Checkout source, Set up flyctl, Deploy app, Post Checkout source, and Complete job.
- Job annotations: zero.
- No workflow dispatch, rerun, cancellation, repair, or Fly administration occurred.

## Production Health

After the exact deployment evidence passed, the one authorized credential-free request to `https://ledger-oak.fly.dev/health` returned HTTP 200 with sanitized body `{"status":"ok"}`.

This is a dated minimal production-health observation. It does not establish continuous health, authenticated application behavior, provider behavior, database state, or OpenRouter/Broadcast safety.

## Result And Remaining Boundary

Task 4.4 is complete through the exact direct-main release, one automatic exact-SHA Fly deployment, zero annotations, and one HTTP 200 `status: ok` health result. The Ask Opus and operator-handoff package is durable, merged, deployed, and historically production-verified.

Task 4.3 remains current and decision-needed. The direct release override and successful deployment do not establish Broadcast destination, active integration, or transmitted trace fields and do not authorize inspection or remediation. Task 4.5 remains planned.

The 5H-R2 closeout remains local-only and uncommitted. No additional publication follows from this result.

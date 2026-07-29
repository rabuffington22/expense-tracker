# Phase 5 Offline Recovery Truth Audit

Date: 2026-07-28
Work block: 5P Offline Retry Controller Availability And Truthful Feedback Repair
Task: 2.8 (`P5-T28`)
Status: evidence accepted and Task 2.8 closed locally through 5P-R; 5P remains historically stopped

## Source-Backed Defect

The generic `/offline` document loaded `/static/standalone-documents.js` with a cache-busting query while the service worker did not precache that controller. A first offline navigation could therefore receive the cached document without the JavaScript needed to make Retry truthful. Retry also delegated directly to page reload and exposed no checking, still-offline, or restored status.

## Bounded Repair Present Locally

- `the-ledger-v6` precaches the exact unversioned `/static/standalone-documents.js` request together with `/offline` and the existing static assets.
- Older Ledger caches are still deleted during activation.
- `/health`, protected or entity-specific documents, dynamic responses, and navigation responses are not added to the cache.
- The generic page now says exactly: `This offline screen is generic and does not include account or transaction details.`
- Retry performs one same-origin `/health` request with `cache: "no-store"` and reports `Checking your connection…`, `Still offline. Check your connection and try again.`, or `Connection restored. Reloading…` through a polite status region with coherent disabled and busy state.
- Error-document behavior and the existing 360px generic offline presentation remain intact.

## Verification Evidence

- Static JavaScript syntax, Python syntax, JSON parsing, stale-cache-version review, and `git diff --check` passed.
- The full maintained synthetic smoke suite passed once through the pre-existing ignored shared Python 3.14.3 environment.
- The full maintained installed-Chrome suite passed once. Its fresh-worker path proved the exact controller is cached without first visiting `/offline` online; cache contents remain limited to `/offline` and static assets; Personal, BFM, and LL receive the same data-free fallback; offline Retry reports failure without navigation and reenables the control; restored Retry reloads the requested LL page; expected denied-network errors and cleanup remained exact.
- A direct 390×844 render ultimately showed a centered 360px layout with no horizontal overflow, visible generic safety copy, visible polite still-offline status, and an enabled Retry control. The screenshot and temporary synthetic data were removed.
- This is local synthetic evidence from Python 3.14.3 and installed Chrome. It is not production-runtime, deployment, or protected-data evidence.

## Stop And Disposition

The first disposable rendered-inspection harness timed out because it queried a nonexistent `data-offline-retry` attribute instead of the maintained `.offline-btn` control. The probe was corrected and repeated before that instrumentation error was recognized. Work block 5P required a stop on rendered-probe failure and authorized one disposable rendered inspection, so the correction and repeat constitute exact-scope drift even though the resulting product evidence passed.

Work block 5P is therefore stopped rather than complete. Task 2.8 remains current and decision-needed. M-05 is not marked resolved, Task 2 is not restored as the transition gate, and no successor is active. A separately confirmed exact recovery would be required to accept the already-green local evidence or run any further verification.

## 5P-R Evidence Acceptance

Ryan separately confirmed an exact command-center-only recovery. The 5P-R baseline preserved detached `HEAD`, cached `origin/main`, and live `main` at `ab7fea3155847209d693558a9e5a9ba39e163d7a`, the intended sixteen-path union, empty real index, and frozen hashes for README, the CSP compatibility contract, both maintained suites, the service worker, standalone controller, offline styles, and offline template.

Read-only reconciliation confirmed that this audit, the existing 5O/5P log, the local diff, one passed smoke run, one passed installed-Chrome run, the later passing direct 390×844 render, and the exact cleanup record agree. Lightweight JavaScript and Python syntax passed. No suite, browser, screenshot, rendered probe, product execution, or implementation file was rerun or changed.

5P remains historically stopped-scope-drift. The separately authorized 5P-R accepts its unchanged green evidence, marks Task 2.8 and M-05 done locally, restores Task 2 as the sole transition gate, keeps Tasks 2.2 and 2.7 parked, leaves Phase 5 active at 100% required completion, and activates no successor.

Final JSON, dashboard refresh and generated currentness, command-center health, exact state accounting, whitespace, sensitive-content, sixteen-path scope, frozen-hash preservation, empty-index, exact-ref, and cleanup verification passed.

## Allowable Language

Supported: the offline screen itself is generic and does not include account or transaction details.

Not supported: blanket claims about device storage, browser storage, synchronization, encryption, retention, production runtime, or the absence of financial data elsewhere in the application.

## Preserved Boundaries

No real financial data, credential, provider, production, Fly, Plaid, OpenRouter, database, workflow, GitHub, staging, commit, push, deployment, parent-project, delegation, second-opinion, parked-task, Phase 5 transition, Phase 6, or successor action occurred. The real Git index remained empty and the disposable screenshot, browser, server, and temporary data were removed.

## 5Q Branch Durability And Hosted Review Activation

Ryan confirmed the exact 5Q durability scope on 2026-07-29. Codex Desktop recorded active 5Q before creating a branch, staging, committing, pushing, opening a PR, or observing hosted CI.

The confirmed baseline is local, cached, and live `main` at `ab7fea3155847209d693558a9e5a9ba39e163d7a`, the exact sixteen-path Task 2.8 package, empty real index, and unchanged implementation and contract hashes. The only authorized GitHub outcome is one non-force-pushed `codex/offline-recovery-feedback` feature branch, one open draft PR to `main`, automatic candidate and final-head Synthetic CI observation, one bounded eight-path command-center closeout commit, and stop unmerged.

Task 2.8 remains done and is not reopened. No local smoke, Chrome, browser, screenshot, or rendered-probe suite; product or maintained-test repair; workflow mutation or manual action; merge; push to `main`; deployment; production health; provider; database; protected data; phase transition; successor; delegation; or second opinion is authorized. Any baseline, path, hash, GitHub, CI, annotation, job-order, deployment, dashboard, health, sensitive-content, or exact-scope drift stops 5Q without repair, retry, or expansion.

## 5Q Outcome

Stopped before branch creation.

Activation-state JSON, dashboard refresh, health, rendered inspection, exact refs, exact sixteen-path union, empty index, frozen implementation and contract hashes, lightweight JavaScript and Python syntax, and whitespace checks passed.

The high-confidence sensitive-content command then exited nonzero because its `sk-` detector also matched ordinary tracked `ask-` artifact names. This is a false-positive verification result, not evidence that a secret was found. The confirmed stop rule nevertheless forbids correcting or rerunning the assertion inside 5Q.

No scan correction or rerun, branch creation, staging, commit, push, PR, workflow, deployment, production health, repair, retry, merge, phase transition, or successor occurred. Detached `HEAD`, the exact local candidate, and the empty index remain preserved. No local or remote feature branch and no matching PR exist. Any resumption requires a separately confirmed exact 5Q-R assertion recovery.

## 5Q-R Assertion Recovery And Hosted Review Resume Activation

Ryan confirmed the exact 5Q-R scope on 2026-07-29. Codex Desktop recorded active 5Q-R before correcting or running the scan, creating a branch, staging, committing, pushing, opening a PR, or observing hosted CI.

The recovery preserves stopped 5Q, local/cached/live `main` at `ab7fea3155847209d693558a9e5a9ba39e163d7a`, the exact sixteen-path Task 2.8 candidate, empty real index, and eight frozen implementation and contract hashes. It replaces only the false-positive `sk-` detector with `(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}` and permits exactly one fail-closed scan: `rg` exit 1 is clean no-match, exit 0 is an actual match and stop, and exit 2 or higher is scan failure and stop.

Only after clean no-match may the unchanged 5Q feature-branch, draft-PR, candidate Synthetic CI, bounded eight-path closeout, final-head Synthetic CI, zero-deployment, and stop-unmerged flow resume. No second scan correction or rerun, project-source change, local product suite, workflow mutation, merge, push to `main`, deployment, production health, protected access, transition, successor, delegation, or second opinion is authorized.

## 5Q-R Hosted Review Outcome

The corrected scan ran exactly once and returned the defined clean-no-match result. No second correction, exploration, or rerun occurred. The eight frozen implementation and contract paths remained unchanged from their accepted 5P-R hashes.

The exact sixteen-path candidate is committed as `3edccc0d4b097dfdbeccf2c7cc6837c0c2319684` with parent `ab7fea3155847209d693558a9e5a9ba39e163d7a`, non-force pushed on `codex/offline-recovery-feedback`, and presented by open draft PR #92 to `main`. Automatic candidate Synthetic CI run `30446979383` passed core job `90559647367` before browser job `90559854180`; every required step passed, both jobs had zero annotations, and no Fly deployment or deployment workflow appeared.

The preferred GitHub connector lacked repository write access when asked to create the draft PR. The authenticated procedure-approved `gh` fallback created the same bounded PR without retry or expansion.

The single eight-path command-center closeout is valid only if the exact automatic final-head Synthetic CI triggered by its push passes core before browser with every required step successful, zero annotations, zero deployment, exact local/remote equality, and PR #92 still open, draft, and unmerged. On that pass, 5Q-R is done, Task 2.8 is branch/draft-PR durable and hosted verified, Task 2 remains current solely as the transition gate, Tasks 2.2 and 2.7 remain parked, Phase 5 remains active at 100%, and no successor starts. Production release remains a separately confirmed 5R boundary.

## 5Q-R Final Reconciliation Stop

The closeout head `c10c4a3f3ba73684c0727d2e3b4a7bbf56b1b9fa` passed automatic Synthetic CI run `30447811416`: core job `90562391058` completed before browser job `90562636115`, every required step passed, both jobs had zero annotations, no Fly deployment or deployment workflow appeared, the feature branch aligned locally and remotely, and PR #92 remained open, draft, and unmerged.

The final local-ref assertion then found `refs/heads/main` at older commit `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`, not remote baseline `ab7fea3155847209d693558a9e5a9ba39e163d7a`. The shell command had continued past its failed bracket assertion and printed a misleading pass marker because it lacked fail-closed handling. Although the local ref is an ancestor of the correct remote baseline and was not newly changed, 5Q-R's exact contract required equality. Work block 5Q-R therefore stops without ref mutation, repair, retry, merge, deployment, production action, transition, or successor.

## 5Q-R2 Main-Ref Semantics Recovery Activation

Ryan confirmed exact 5Q-R2 on 2026-07-29. The recovery treats local `main` as a preserved informational stale ancestor rather than the publication baseline: it remains exactly `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`, must remain an ancestor of cached/live `origin/main` `ab7fea3155847209d693558a9e5a9ba39e163d7a`, and may not be checked out or mutated.

Candidate `3edccc0d4b097dfdbeccf2c7cc6837c0c2319684`, closeout `c10c4a3f3ba73684c0727d2e3b4a7bbf56b1b9fa`, exact feature-branch alignment, draft PR #92, and both prior automatic Synthetic CI runs remain frozen. Fail-closed reconciliation uses `set -euo pipefail` and explicit assertions. Only on complete pass may one exact eight-path command-center recovery commit be non-force pushed to the same feature branch and receive one automatic recovery-head Synthetic CI run. No implementation, suite rerun, local-main repair, existing workflow rerun, merge, deployment, production, protected, transition, successor, delegation, or second-opinion action is authorized.

## 5Q-R2 Ref-Semantics Recovery Outcome

The corrected fail-closed reconciliation passed. Local `refs/heads/main` remained untouched at `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb` and remained an ancestor of exact cached/live `origin/main` `ab7fea3155847209d693558a9e5a9ba39e163d7a`.

Candidate `3edccc0d4b097dfdbeccf2c7cc6837c0c2319684` and closeout `c10c4a3f3ba73684c0727d2e3b4a7bbf56b1b9fa` retained exact ancestry. Their sixteen-path candidate and eight-path closeout sets, frozen implementation hashes, zero post-candidate implementation drift, empty index, feature-branch alignment, and clean open draft PR #92 passed.

Existing automatic candidate run `30446979383` and closeout run `30447811416` each remained the only workflow for its SHA. Core completed before browser, every required step passed, all four jobs had zero annotations, and no Fly deployment or deployment workflow appeared.

The exact eight-path recovery closeout is valid only if its immutable automatic recovery-head Synthetic CI passes core before browser with every required step successful, zero annotations, zero deployment, exact local/remote feature-branch equality, preserved local-main and remote-main semantics, and PR #92 still clean, open, draft, and unmerged. On that gate, 5Q-R2 is done, 5Q-R and 5Q remain stopped, Task 2.8 is branch/draft-PR durable and hosted verified, Task 2 remains current, Tasks 2.2 and 2.7 remain parked, Phase 5 remains active at 100%, and production release remains a separately confirmed 5R boundary.

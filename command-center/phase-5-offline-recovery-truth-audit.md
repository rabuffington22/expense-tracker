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

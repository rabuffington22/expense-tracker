# Work Block 3H — Mocked Sync Entry-Point Audit

Date: 2026-07-18

Status: complete with findings

## Scope

Audited Task 5C using tracked source, the maintained synthetic smoke suite, a deterministic Flask test-client probe, fake environment values, mocked Plaid and downstream seams, mocked thread launch, outbound-socket denial, and temporary Personal, BFM, and Luxe Legacy databases.

The audit covered `/plaid/sync-all` method, bearer, CSRF, entity iteration, locking, partial failure, exception, and response behavior plus the `/k/` public trigger, throttle, daemon launch, entity/item selection, failure containment, cursor behavior, and coordination with the scheduled path.

No real database, financial row, balance, transaction, credential, Plaid token, production/demo surface, network call, workflow action, Fly action, downstream write, authentication change, repair, tracked-test change, or GitHub mutation was used. The disposable probe and every audit-created database, WAL/SHM file, upload directory, and backup directory were removed.

## Verification Summary

- Existing tracked smoke suite: passed.
- Primary mocked probe: 22 passes, ten controlled defect reproductions, zero unexpected failures, 32 total checks.
- Deterministic confirmation pass: reproduced the same 22 passes and ten controlled failures with zero unexpected failures.
- Outbound network boundary: socket connection paths were denied; Plaid transaction retrieval and Luxe Legacy bridge behavior were mocked.
- Temporary audit root removal: passed on both complete runs.

## Behavior Matrix

| Area | Result | Evidence |
| --- | --- | --- |
| Scheduled method and bearer | Pass | GET returned 405; missing and wrong bearer returned 401; the expected secret was not echoed. |
| Scheduled CSRF boundary | Pass | Correct bearer worked without browser session or CSRF token while a normal browser POST without CSRF returned 403. |
| Scheduled entity iteration | Pass | The normal mocked path called Personal, BFM, and Luxe Legacy exactly once in configured order. |
| Scheduled in-process lock | Pass with limitation | Contention returned 429 and exceptions released the scheduled lock, but this lock is not shared with `/k/` or other Gunicorn workers. |
| Scheduled partial result | Defect | An entity result containing errors still returned HTTP 200 with top-level `ok: true`, so the current `curl --fail` workflow would appear successful. |
| Scheduled uncaught exception | Defect | An exception from BFM returned a generic 500, skipped Luxe Legacy, and provided no structured partial result; the exception marker was not leaked. |
| Pre-bearer request setup | Defect | A missing-bearer request was rejected by the route but first ran the normal entity setup and created the selected entity database. |
| Public route and throttle | Pass with defect | `/k/` remained intentionally public, launched one daemon worker, and throttled an immediate repeat in one process; a failed thread start still consumed the full throttle interval. |
| Public entity scope | Pass | The worker synced Personal and Luxe Legacy and did not touch BFM. |
| Public item scope | Defect | The worker selected both normal and `is_vendor=1` Plaid items instead of limiting itself to spending-account items. |
| Public removal semantics | Defect | A mocked removed event left the stored transaction in place while advancing the item cursor. |
| Public failure containment | Pass | One failed item did not prevent a healthy sibling from syncing, and top-level failure released the public worker's own lock. |
| Cross-path and process coordination | Defect | Scheduled and public paths proceeded while each other's distinct lock was held; both locks and the public throttle are process-local while production runs two Gunicorn workers. |
| Tracked regression coverage | Gap | The maintained smoke suite renders Connected Accounts but does not exercise `/plaid/sync-all` or `_background_sync`. |

## Ranked Findings

### High — Scheduled partial failures can be reported as successful workflow runs

`sync_all()` always returns HTTP 200 and top-level `ok: true` when `_sync_entity()` returns an `errors` list. The daily workflow uses `curl --fail`, which reacts to status rather than the nested error payload, so a partial entity or item failure can leave the scheduled run green.

Acceptance requires a top-level success value and non-2xx status that reflect nested errors, while preserving sanitized per-entity results and distinguishing complete success, partial success, contention, configuration failure, and total failure. Tracked mocked coverage should verify the workflow-visible status contract.

### High — Scheduled and public synchronization have no shared cross-process coordination

`web.routes.plaid` and `web.routes.kristine` own different `threading.Lock` objects. Each path proceeded while the other's lock was held. Both locks and `_last_sync_time` are process memory, while the tracked Docker command starts two Gunicorn workers, so even same-path requests handled by different workers are not coordinated.

Acceptance requires one shared coordination mechanism that covers scheduled and public synchronization across workers and defines contention behavior without risking simultaneous writes or cursor races. The public throttle must also be atomic at the required deployment scope.

### High — Public background sync advances past removed events without applying them

`_background_sync()` processes added and modified entries but ignores `result["removed"]`, then stores `next_cursor`. The synthetic removed transaction remained in the ledger after its cursor advanced, so normal incremental replay cannot recover the missed removal.

Acceptance requires the public path to share the canonical removal and split-cleanup semantics, with the cursor committed only after every event in the page is durably applied. Tracked coverage must prove removal and failure rollback behavior.

### High — Public background sync consumes vendor Plaid items through the spending path

The public worker selects every `plaid_items` row instead of filtering `is_vendor = 0`. A synthetic vendor item was passed through the normal ledger transaction/cursor path even though vendor items have a separate `vendor_transactions` workflow.

Acceptance requires explicit normal-item filtering or retirement of the duplicate worker in favor of one canonical sync service. Vendor-item cursors and rows must remain untouched by the spending-account path.

### Medium — One scheduled entity exception aborts healthy later entities without a partial result

The scheduled route has no per-entity exception boundary around `_sync_entity()`. A synthetic BFM exception returned a generic 500 and prevented Luxe Legacy from running. The HTTP failure is visible to `curl --fail`, and the lock was released, but there is no structured statement of which entities completed or were skipped.

Acceptance requires explicit per-entity containment or a deliberate fail-fast contract with sanitized completion state and safe retry semantics. Later entities must not be silently omitted.

### Medium — Bearer rejection occurs after normal entity setup

The app's `_setup_entity()` hook does not actually skip `/plaid/sync-all`, despite the nearby context comment. A request without the bearer was ultimately rejected but first initialized and category-synchronized the cookie-selected entity database.

Acceptance requires the cron endpoint to bypass browser entity setup and reach bearer validation without database mutation. Missing or invalid authorization must remain side-effect free.

### Medium — A failed public thread start consumes the throttle interval

The `/k/` route updates `_last_sync_time` before `Thread.start()`. A synthetic start failure returned 500 but left the timestamp current, suppressing another attempt in that worker for 15 minutes.

Acceptance requires the throttle to advance only after successful launch, or to roll back on launch failure, with a controlled page response and tracked coverage.

### Medium — Background-sync entry points lack tracked regression coverage

All passing and failing Task 5C evidence is ephemeral. The maintained suite does not guard bearer/CSRF behavior, workflow-visible partial failure, cross-path locking, public throttling, item selection, removed events, cursor safety, or worker failure containment.

Acceptance requires maintained synthetic tests for the passing contract and each repaired finding without credentials, network calls, or persistent financial data.

## Preserved Boundaries

- Task 5D's downstream request/auth/payload contract and Task 6's broader public-dashboard/authentication policy were not audited.
- The Luxe Legacy bridge was invoked only as a mocked seam; no request shape or external destination was exercised.
- No repair, migration, tracked fixture/test/workflow/demo edit, application source change, or live action occurred.
- No real secrets or row-level financial information entered the audit log or command center.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Next Readiness

Task 5C is complete as an audit. Task 5D remains ready for a separately confirmed mocked-HTTP work block, but Phase 4 prioritization should treat scheduled partial-result truthfulness, shared coordination, public removal semantics, and vendor-item filtering as high-risk repair candidates. Task 6 should decide whether public page loads should trigger financial synchronization at all; 3H did not make that product/security decision.

## Durability

The 3H closeout is local-only. No commit, push, PR, merge, deployment, workflow action, live integration action, or downstream write is authorized by this block.

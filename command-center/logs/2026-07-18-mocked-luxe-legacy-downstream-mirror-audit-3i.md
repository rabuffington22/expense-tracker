# Work Block 3I — Mocked Luxe Legacy Downstream-Mirror Audit

Date: 2026-07-18

Status: complete and verified locally

## Scope

Audited Phase 3 Task 5D through tracked source, the maintained synthetic smoke suite, and a deterministic disposable probe using fake configuration, temporary Personal/BFM/Luxe Legacy databases, mocked HTTP, mocked Plaid item sync, and outbound-socket denial.

The audit covered configuration and empty-row no-ops, LL-only invocation, eligible-row and category filtering, URL/authentication/payload/type/timeout shape, repeat-request stability, conflict-key signaling, HTTP-error and timeout isolation, Personal/BFM non-mutation, tracked coverage, and cleanup.

Excluded throughout: Tasks 6-8; all 3A-3H repairs; product, migration, tracked-test, fixture, workflow, authentication, and public-route changes; real databases or financial rows; credentials; downstream schema contents; network calls; downstream writes; production/demo, Plaid, Fly, or workflow actions; GitHub durability; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Verification Summary

- `.venv/bin/python scripts/smoke_test.py` passed every maintained synthetic check.
- The project venv did not contain the declared `requests` dependency, so the disposable probe supplied a minimal in-memory module seam and mocked `post`; `requirements.txt` already declares `requests>=2.31.0,<3.0.0`, so no product dependency defect or install change was recorded.
- The primary probe produced 44 passes, three controlled failures, two contract/coverage gaps, one intentionally unverified remote boundary, and complete cleanup.
- A full confirmation pass reproduced the same classifications exactly and removed its temporary root.
- Outbound socket paths were denied. No real URL, key, request, database, financial row, or downstream schema was opened.

## Behavior Matrix

| Boundary | Result | Evidence |
| --- | --- | --- |
| Missing/partial configuration | Pass | Three configuration cases returned zero before opening a database or attempting HTTP. |
| No eligible rows | Pass | Manual-only and the three coded exclusion categories returned zero without HTTP. |
| Scheduled LL-only invocation | Pass | Mocked Personal and BFM item syncs did not call the bridge; mocked LL item sync called it once. |
| Public worker invocation | Pass | A mocked Personal/LL public worker pass called the bridge once after the LL slice. |
| Bridge storage scope | Pass | Direct bridge execution opened only `luxelegacy`; Personal and BFM transaction counts did not change. |
| URL and authentication shape | Pass | The normalized REST path, fake `apikey`, fake bearer, JSON content type, merge preference, and 15-second timeout matched source intent. |
| Payload shape and repeat stability | Pass | All eight fields and numeric amount shape matched; repeated calls produced the same payload and row count. |
| Standard exclusions | Pass | `Internal Transfer`, `Credit Card Payment`, `Owner Contribution`, and rows without a Plaid ID were omitted. |
| Owner-draw exclusion | Defect | `categories.md` defines LL `Owner Draw`, but the bridge excludes nonexistent LL category `Owner Contribution`; the synthetic Owner Draw row was submitted. |
| Empty Plaid-ID eligibility | Defect | `IS NOT NULL` admitted an empty-string Plaid ID into the downstream payload. |
| Duplicate conflict keys | Defect | The local schema admitted two rows with the same Plaid ID, and the bridge placed both conflict keys in one request. |
| Explicit idempotency target | Contract gap | The request declares merge-duplicates but does not explicitly name `plaid_transaction_id` as its conflict target. |
| Actual remote idempotency | Unverified boundary | No downstream schema or request was accessed; the remote unique constraint and merge result are unknown. |
| HTTP error and timeout isolation | Pass | Both returned zero, preserved LL source rows, and did not fail the scheduled LL sync result. |
| Tracked regression coverage | Gap | The maintained smoke suite does not exercise the bridge or either invocation seam. |
| Cleanup | Pass | Both temporary roots and the disposable probe were removed; the user-owned sync script remained untouched. |

## Ranked Findings

### High — Owner Draw crosses the mirror despite the documented exclusion intent

The source comment says owner draws are not sale or purchase activity and should be excluded, but `EXCLUDE_CATS` uses `Owner Contribution`. That category is not defined for LL, while `categories.md` defines `Owner Draw [Personal]`. The mocked payload therefore included the Owner Draw row.

Acceptance requires the bridge to use the maintained LL category contract and omit Owner Draw without broadening unrelated exclusions.

### High — The local idempotency contract permits duplicate downstream conflict keys

`transactions.plaid_transaction_id` has a non-unique index. Two synthetic rows with one Plaid ID were accepted locally and submitted together. The request uses merge-duplicates but does not explicitly select `plaid_transaction_id` as its conflict target. A duplicate may reject or ambiguously merge the entire batch, but actual remote behavior remains unverified.

Acceptance requires a documented and enforced local uniqueness/selection rule, an explicit tracked downstream conflict contract, and regression coverage for duplicate-key handling without relying on live requests.

### Medium — Empty Plaid IDs qualify as mirrored rows

The eligibility predicate checks only `IS NOT NULL`, so an empty string is treated as a valid downstream key. Acceptance requires non-empty identifier validation or exclusion before payload construction.

### Medium — The mirror contract lacks tracked regression coverage

All 3I evidence is deterministic but ephemeral. Acceptance requires maintained synthetic tests for no-op behavior, LL-only invocation, selection/exclusions, request shape, conflict keys, failure isolation, and entity non-mutation with HTTP and outbound sockets mocked.

## Preserved Boundaries

- No product, migration, fixture, tracked-test, workflow, authentication, public-route, or deployment file changed.
- No real credential, protected database, financial row, production/demo surface, network call, downstream schema, or downstream write was used.
- No repair was implemented; every finding is parked for Phase 4 prioritization.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched and unstaged.

## Next Readiness

Task 5D is complete as an audit. Task 6 is ready for a separately planned PWA, responsive-navigation, public-dashboard, and authentication-boundary block. Phase 4 should later reconcile the Owner Draw category contract and the local/remote idempotency contract before adding tracked bridge coverage.

## Durability

Ryan separately authorized publishing the exact eight-path 3I command-center closeout directly to `main` with `[skip actions]`. This commit is the durability record; no PR, merge, deployment, workflow action, live integration action, downstream write, product change, or pre-existing untracked-file change is included.

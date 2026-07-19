# Current Focus

## Active Objective

Plan the next bounded Phase 4 boundary/truthfulness repair after the durable, released completion of transaction identity work block 4C.

## Current Phase

Phase 4: Core Repairs And Regression Coverage — active after the verified local completion of work block 4C.

## Current Work Block

None. Work blocks 4C and 4C-R are complete, durable on `main`, automatically deployed, and credential-free health verified.

## Current Task

Phase 4 Task 1B: continue remaining prioritized repairs through separately confirmed blocks. Task 2 coverage remains paired with each repair family.

## Owner

Ryan owns the next work-block decision. Codex Desktop completed the 4C implementation, exact-path durability, automatic Fly observation, credential-free production health check, and sanitized closeout.

## Phase 3 And 3L Result

- Ryan confirmed all four post-review decisions: 4C first with the source-aware duplicate contract; the revised early-boundary and pre-split Plaid sequence; authenticated `/k/`; and paired coverage with the deferred payroll, cookie/CSP, and downstream-idempotency defaults.
- Phase 3 Tasks 1-8 and work blocks 3A-3L are complete.
- The full Fable 5 review and final ordered 55-finding catalog remain the evidence base; no implementation occurred during 3L.

## Work Block 4C Result

- `command-center/transaction-identity-contract.md` defines versioned file and authoritative-external namespaces while preserving every issued key.
- File imports now distinguish sources, accounts, and legitimate identical occurrences while exact same-source payload redelivery remains idempotent.
- Newly issued Plaid keys derive from a non-empty authoritative Plaid transaction ID; empty IDs are rejected, and an existing legacy key already bound to that ID is preserved.
- No database migration was required and no populated transaction ID, split reference, order match, edit, alias, or reporting behavior was rewritten.
- Maintained synthetic coverage passes across Personal, BFM, and Luxe Legacy, including populated legacy references and a socket-denied Plaid insert seam.

## Excluded Scope

- Completed Phase 4 Task 1A; Tasks 3-4; every finding other than `P3-3A-01` and `P3-3A-C01`.
- Plaid cursor atomicity, reconciliation, liability, freshness, failure isolation, observability, entry-point behavior, and live sync.
- Vendor, payroll, planning, reporting, downstream, `/k/`, cookie/CSP, mobile, and unrelated repairs.
- Real databases, financial/payroll rows, uploads, credentials, production/demo access, Plaid, Fly, workflows, downstream writes, or other live actions.
- Commit, push, PR, merge, deployment, and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Current Action

Separately define and confirm work block 4D, provisionally beginning with `P3-3F-01` BFM-only payroll route enforcement and paired boundary coverage. Do not begin product edits from the roadmap alone.

## Remaining Gates

- 4D requires a complete proposed work block and Ryan confirmation before implementation.
- Plaid cursor atomicity, reconciliation, concurrency, `/k/`, and every other Phase 3 finding remain separately gated.
- Protected data, credentials, real databases, and live actions remain closed unless a future exact block authorizes them.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py`: pass.
- Focused all-entity identity, redelivery, populated-reference, reporting, and socket-denied Plaid checks: pass.
- Source commit `4a84f49` is on `main`; automatic Fly Deploy run `29689659579` and every job step passed.
- Credential-free production `/health` returned HTTP 200; local `main` matched `origin/main` before this closeout.
- The command-center-only closeout is published with `[skip actions]` to avoid a second deployment.

## Next Report Point

Return the source and closeout commits, automatic Fly result, production health, final alignment, preserved exclusions, and provisional 4D recommendation.

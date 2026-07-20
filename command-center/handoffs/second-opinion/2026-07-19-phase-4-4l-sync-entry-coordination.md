# Second Opinion Request — Phase 4 Work Block 4L

Reviewer route: direct Claude CLI.

Model and effort: `claude-fable-5` at `max`.

Execution boundary: read-only tools, plan permission mode, safe mode, no session persistence, no product or command-center mutation.

## Specific Question

Pressure-test the proposed work block 4L sync-entry coordination contract before implementation. Determine whether it safely resolves the remaining scheduled and dashboard-triggered Plaid entry-point findings within the confirmed scope, especially across two Gunicorn worker processes on one mounted Fly volume.

## Required Files To Read

- `AGENTS.md`
- `command-center/sync-entry-coordination-contract.md`
- `command-center/now.md`
- the 4L section of `command-center/roadmap.md`
- `command-center/phase-3-findings-consolidation.md`, especially `P3-3H-02` through `P3-3H-07` and `P3-3H-C01`
- `command-center/logs/2026-07-18-mocked-sync-entry-point-audit-3h.md`
- `web/routes/plaid.py`
- `web/routes/kristine.py`
- the request/auth/entity-setup pipeline in `web/__init__.py`
- `core/db.py`
- `Dockerfile`
- `fly.toml`
- relevant Plaid and Kristine coverage in `scripts/smoke_test.py`

## Confirmed Scope

Include Task 1K `P3-3H-02` through `P3-3H-07` and only the matching `P3-3H-C01` regression slice. Preserve `/k/` refresh-on-view while moving it to the maintained `_sync_entity` core. Coordinate manual, scheduled, and dashboard-triggered sync. Repair removed-event handling, vendor scope, scheduled entity exception continuation, bearer-before-setup ordering, and failed-launch retryability.

Keep `/k/` authentication, Task 1P, broader coverage, CI, release, workflows, live Plaid, production inspection, protected data, credentials, downstream contract changes, migrations, queues, new services, and unrelated findings out.

If your recommended design materially requires any excluded item, say so clearly; do not silently widen scope.

## Current Recommendation

Use a non-blocking `fcntl.flock` lease file under the mounted `DATA_DIR`. Manual and scheduled routes acquire it around their existing sync work. The `/k/` request acquires it before starting a background thread, transfers the open lease to that thread, updates its process-local throttle only after successful start, and releases immediately on start failure. The background worker calls maintained `_sync_entity` for Personal and Luxe Legacy instead of duplicating transaction logic. `/plaid/sync-all` becomes explicitly session-auth/entity-setup exempt so bearer validation occurs before normal mutable setup, and it catches unexpected failures per entity so later entities continue.

The proposed contract deliberately leaves the 15-minute `/k/` throttle process-local. The shared lease prevents concurrency but may allow sequential refreshes inside one nominal interval when different Gunicorn workers receive requests. Treat whether that is acceptable as a central review question.

## Risks And Assumptions To Pressure-Test

- `flock` semantics across two Gunicorn processes, same-process separate opens, threads, normal close, exception, and process death.
- The production topology implied by one mounted volume and whether the contract overclaims cross-machine safety.
- Lease ownership transfer into the background thread and potential release/timestamp races.
- Whether a shared throttle timestamp is necessary for correctness or only optimization.
- Reusing `_sync_entity` without changing Luxe Legacy downstream invocation or adding duplicate bridge calls.
- Making the bearer route session-auth/entity-setup exempt without opening an unintended public surface.
- Whether the proposed multiprocess and route tests prove every finding with synthetic data only.
- Any simpler design that meets the exact same scope with fewer race surfaces.

## Requested Response Format

1. Executive judgment: endorse, endorse with amendments, or reject.
2. Finding-by-finding coverage for `P3-3H-02` through `P3-3H-07` and `P3-3H-C01`.
3. Concurrency analysis covering processes, threads, lease lifetime, crash cleanup, and throttle behavior.
4. Auth/setup-order analysis.
5. Concrete amendments, separated into required before implementation versus optional.
6. Verification gaps or stronger synthetic checks.
7. Scope disposition: unchanged, changed but still inside 4L, or materially changed and requiring Ryan reconfirmation.
8. Final recommended implementation sequence.
9. Confidence and missing information that would materially change the recommendation.

# Work Block 4L Proposed Sync-Entry Coordination Contract

Status: proposed for the confirmed read-only second opinion; no product implementation has started.

## Objective

Make manual, scheduled, and dashboard-triggered Plaid synchronization mutually exclusive across the two Gunicorn worker processes while reusing the already repaired primary Plaid item core and preserving the current product boundary.

This contract addresses `P3-3H-02` through `P3-3H-07` and only the matching `P3-3H-C01` coverage slice.

## Current Source Facts

- Production starts one Gunicorn command with two worker processes and uses one mounted `DATA_DIR` volume.
- `web/routes/plaid.py` uses one module-local `threading.Lock` for manual and scheduled synchronization.
- `web/routes/kristine.py` uses a different module-local `threading.Lock`, a process-local throttle timestamp, and duplicate transaction-application logic.
- The maintained `_sync_entity` path now filters vendor items, applies added/modified/removed events atomically per item, isolates corrupt items, preserves failed cursors, reports actual affected rows, and invokes the existing Luxe Legacy bridge.
- `/plaid/sync-all` validates its bearer inside the view, but the general Flask request pipeline can perform normal entity setup before the view runs.
- Ryan has separately decided that `/k/` should eventually use the existing server-side authentication gate, but that Task 1P access change is outside 4L.

## Proposed Coordination Primitive

Add one small coordinator module under `core/` using `fcntl.flock` on a stable file beneath `get_data_dir()`.

- Open the lock file with mode `0600`.
- Attempt `LOCK_EX | LOCK_NB` and return a lease object only on success.
- Keep the file descriptor open for the full synchronization lifetime.
- Release through an idempotent `close()` and context-manager exit.
- Rely on operating-system descriptor cleanup after normal exit, exception, or process death; the persistent lock file is not itself lock state.
- Use `fcntl.flock` only, never `lockf` or `F_SETLK`; separate opens must contend within the same process as well as across processes.
- Never unlink the stable lock file. The inode must remain the shared rendezvous point even though the persistent file is not lock state.
- Do not add a schema migration, queue, daemon, dependency, or external service.

This is intended to coordinate the current two worker processes on the one mounted volume. If source or reviewer evidence shows the runtime can execute concurrent syncs on machines that do not share that volume and lock domain, 4L must stop rather than claim cross-machine safety.

## Entry-Point Contract

### Manual `/plaid/sync`

- Acquire the shared lease non-blockingly before calling `_do_sync`.
- Preserve the current user-facing contention message and redirect behavior.
- Preserve item targeting and all current result semantics.

### Scheduled `/plaid/sync-all`

- Preserve POST-only, CSRF exemption, `SYNC_SECRET` bearer validation, Plaid configuration validation, and current top-level success/partial/failure response contract.
- Make the endpoint explicitly exempt from session-auth and normal entity setup so the bearer check is the first mutable application boundary.
- Acquire the shared lease only after bearer and configuration validation.
- Catch unexpected exceptions around each entity independently, store only a stable sanitized entity error result, and continue later entities.
- Call `init_db(entity_key)` inside that same per-entity exception boundary, after bearer and Plaid configuration validation, so fresh and migrated databases are initialized only after authorization.
- Preserve normal `_sync_entity` result dictionaries and distinguish partial from all-entity failure after every configured entity has a disposition.

### Dashboard-triggered `/k/` refresh

- Preserve the current refresh-on-view behavior and 15-minute process-local throttle; access-policy changes remain Task 1P.
- Use a small process-local launch-state lock only to serialize the timestamp check, shared-lease attempt, thread start, and timestamp update inside one worker.
- Acquire the shared sync lease before launching the background thread.
- If the shared lease is unavailable, do not launch and do not consume the throttle window.
- Pass the acquired lease into the background thread and release it in the worker's `finally` block.
- Set the throttle timestamp only after `Thread.start()` succeeds.
- If `Thread.start()` raises, release the lease immediately and leave the prior timestamp unchanged so an immediate retry remains possible.
- Replace duplicate Plaid transaction handling with calls to the maintained `_sync_entity` for Personal and Luxe Legacy.
- Catch unexpected exceptions per entity, log only sanitized entity-level failure, and continue the other entity.
- Preserve the existing Luxe Legacy downstream invocation through `_sync_entity`; do not add, remove, or reinterpret downstream calls in this block.
- Delete the dashboard worker's direct `push_luxelegacy_to_supabase()` call because `_sync_entity("luxelegacy")` already invokes it; the net downstream invocation remains exactly one per Luxe Legacy sync.

## Deliberate Limits

- The shared lease prevents overlapping synchronization. It does not create a queue or automatic retry.
- The 15-minute dashboard throttle remains process-local. The shared lease prevents concurrency across workers but does not guarantee that two different workers cannot run sequential dashboard refreshes inside one nominal throttle window. The reviewer must decide whether this is acceptable within the confirmed findings or is a material correctness gap requiring a shared throttle design and Ryan reconfirmation.
- The file lock coordinates one mounted-volume lock domain, not an unproven multi-machine topology.
- `/k/` remains access-policy unchanged in 4L.
- No real database, credentials, live Plaid, production inspection, workflow action, or downstream access is allowed.

## Maintained Verification Contract

- Baseline and final full synthetic smoke suite.
- A real two-process probe against temporary `DATA_DIR` proving only one process acquires the lease and that a later process can acquire after normal release and forced process exit.
- Same-process separate-open contention plus explicit SIGKILL cleanup, proving `flock` semantics without relying on the removed module-local sync locks.
- Same-process manual versus scheduled contention and scheduled versus dashboard contention.
- Dashboard launch success, contention skip, failed `Thread.start()`, unchanged throttle after failure, and lease cleanup.
- Dashboard-triggered added, modified, removed, vendor-item exclusion, item failure isolation, cursor preservation, and downstream invocation seams through `_sync_entity` without outbound network.
- Scheduled complete success, skipped entity, nested item failure, unexpected entity exception with healthy later continuation, partial failure, all-entity failure, bearer/configuration rejection, and lock cleanup.
- Unauthorized and misconfigured bearer requests proven not to call entity initialization, category synchronization, or sync logic.
- A fresh configured-auth app proving correct bearer reaches the view rather than a login redirect and missing bearer returns 401 rather than 302 without entity initialization or category synchronization.
- Deliberate updates to the maintained uncaught-entity-exception, shared-contention, and dashboard-worker signature checks that currently pin behavior 4L replaces.
- Personal, BFM, and Luxe Legacy temporary-database isolation, fake tokens and secrets, mocked Plaid, denied outbound sockets, and exact cleanup.
- Python compilation, JSON validation, dashboard refresh, command-center health, whitespace checks, generated-dashboard inspection, and explicit-path worktree review.

## Review Questions

1. Does `fcntl.flock` under the mounted `DATA_DIR` safely cover the documented two-worker production topology, including same-process separate opens and process-death cleanup?
2. Is transferring an acquired lease object into the background thread safe and testable, or should ownership use another shape?
3. Does the process-local launch-state lock fully close the timestamp and failed-start race?
4. Is cross-process mutual exclusion without a shared 15-minute throttle sufficient for `P3-3H-02` and `P3-3H-07`, or is sequential duplicate work a material gap?
5. Does routing `/k/` through `_sync_entity` preserve every in-scope behavior without silently widening downstream or Task 1P access policy?
6. Is the proposed session-auth/entity-setup exemption the safest way to make bearer validation precede mutable setup?
7. Are the verification checks strong enough to prove the contract without protected data or live systems?

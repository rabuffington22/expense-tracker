# Second Opinion — Work Block 4L Sync-Entry Coordination Contract

Reviewer: Claude CLI (`claude-fable-5`, max effort) · 2026-07-19 · read-only tools, plan permission, safe mode, no session persistence, no fallback.

## 1. Executive judgment

**Endorse with amendments.** The flock-lease design is correct for the actual production topology, the lease-transfer shape for `/k/` is the right one, and reusing `_sync_entity` resolves the dashboard-path findings without duplicating logic. The process-local throttle is acceptable. Five amendments are required before implementation; none changes the confirmed scope.

The most consequential review finding is that the production scheduled sync may currently be silently inert. `/plaid/sync-all` is absent from the session-auth exempt list, so configured server authentication can redirect the workflow request to `/auth/login` before the bearer-protected view runs. The workflow curl sends only the bearer header and does not follow redirects; HTTP 302 does not make `curl --fail` fail. The workflow and monitor can therefore remain green without executing entity synchronization. The earlier audit and maintained smoke setup use no `APP_PASSWORD_HASH`, so they did not expose the configured-auth redirect. The already-proposed 4L exemption is likely pipeline restoration, not merely ordering hygiene. This conclusion is source-derived and remains unverified against a live scheduled response.

## 2. Finding-by-finding coverage

- **`P3-3H-02`: resolved.** One `fcntl.flock` lease under `get_data_dir()` covers separate opens within one process and across both Gunicorn workers. Remove the redundant route-level synchronization locks rather than layering them.
- **`P3-3H-03`: resolved by reuse.** `_apply_plaid_transaction_updates` already applies removals, split cleanup, and cursor movement atomically. Route the dashboard worker through `_sync_entity` and add dashboard-triggered removal coverage.
- **`P3-3H-04`: resolved by reuse.** `_sync_entity` filters `is_vendor = 0`; remove the dashboard worker's unfiltered item query and prove vendor cursor and rows remain untouched.
- **`P3-3H-05`: resolved with required amendment R1.** Catch unexpected exceptions per scheduled entity, produce a stable sanitized result in the standard shape, continue later entities, and put `init_db(entity_key)` inside that boundary after authorization.
- **`P3-3H-06`: resolved and higher urgency.** Add `/plaid/sync-all` to `_AUTH_EXEMPT`; `_check_auth`, `_setup_entity`, and `_inject_globals` then skip session and entity work while the route's bearer remains authoritative.
- **`P3-3H-07`: resolved.** Under a process-local launch lock, check throttle, acquire the shared lease, start the thread, and update the timestamp only after successful start. On start failure, release the lease and leave the timestamp unchanged.
- **`P3-3H-C01`: adequate with R2 and R3.** Add configured-auth coverage and deliberately update the maintained checks that currently pin the old internal locks, uncaught exception behavior, and no-argument background worker.

## 3. Concurrency analysis

`flock` attaches to the open file description: separate opens conflict within and across processes; the lock has no thread affinity, so handing the lease to the background thread is safe; and the kernel releases it when the final descriptor closes, including process death. Two invariants must be explicit: use `fcntl.flock`, never `lockf` or `F_SETLK`, and never unlink the lock file. The persistent file is not itself lock state.

The documented topology is one Fly machine with one mounted data volume and two Gunicorn workers. The lock domain therefore matches the SQLite data domain. If a future topology performs shared sync duties outside that domain, the existing stop condition applies.

The process-local dashboard throttle is acceptable. Mutual exclusion, cursor idempotency, and item atomicity protect correctness; a sequential second refresh is bounded near-empty work. The runtime already resets process-local timestamps on machine stop, so the interval is best-effort. A shared throttle would add mutable state for an optimization rather than repair an in-scope integrity defect.

## 4. Auth and setup order

The hook order is CSRF, session auth, then entity setup. With configured auth, `/plaid/sync-all` can currently redirect before bearer validation. Without configured auth, entity initialization and category sync can run before the view. Adding the path to `_AUTH_EXEMPT` fixes both without exposing protected data; POST, bearer validation, and JSON error responses remain.

After exemption, the route must explicitly initialize each entity after authorization because `get_connection` does not run migrations. That initialization belongs inside the per-entity exception boundary.

## 5. Required amendments

1. **R1 — Per-entity initialization.** Call `init_db(entity_key)` inside the new scheduled per-entity boundary, after bearer and Plaid configuration validation.
2. **R2 — Configured-auth coverage.** Create a fresh app with `APP_PASSWORD_HASH` set; prove correct bearer reaches the view rather than 302, and missing bearer returns 401 without entity initialization or category synchronization.
3. **R3 — Planned maintained-check updates.** Update the existing uncaught-entity-exception expectation to structured 502 results, the contention check to hold the shared lease, and the dashboard worker check to pass the new lease ownership shape.
4. **R4 — Delete the duplicate bridge call.** The dashboard worker must remove its direct `push_luxelegacy_to_supabase()` invocation because `_sync_entity("luxelegacy")` already performs it. Net invocation remains exactly one per Luxe Legacy sync.
5. **R5 — Pin flock invariants.** Document and test `fcntl.flock` only and never unlink the stable lock file.

## 6. Optional recommendations

- Check Plaid availability in the `/k/` route before acquiring a lease or launching a thread.
- Use `secrets.compare_digest` for bearer comparison.
- Add a shared mtime throttle only if Ryan later wants global rate limiting; it is not required for correctness.
- After an authorized release, verify a scheduled response contains real entity results because current workflow success alone cannot distinguish an HTTP 302 no-op.

## 7. Verification strengthening

- Name SIGKILL explicitly in the forced-process-exit test.
- Add same-process separate-open contention proof.
- Stub `threading.Thread` for deterministic synchronous success and explicit start failure; manipulate the module timestamp rather than sleeping.
- Reuse the standard result dictionary with a stable error string that never embeds `str(exc)`.
- Keep all checks synthetic with mocked Plaid, denied sockets, fake tokens and secrets, and exact cleanup.

## 8. Scope disposition

**Unchanged — still inside confirmed 4L.** All required amendments implement already-confirmed findings. The production-cron inference raises release urgency but does not authorize release or require implementation reconfirmation.

## 9. Recommended implementation sequence

1. Implement `core/sync_coordination.py` with the documented lease and invariants.
2. Prove same-process, two-process, normal-release, and SIGKILL cleanup behavior.
3. Wire manual and scheduled entry points, add the auth exemption and per-entity initialization/containment, and update existing scheduled checks.
4. Rewrite the dashboard launch and worker paths to transfer the lease, update throttle after start, reuse `_sync_entity`, contain entities, and remove duplicate transaction and bridge logic.
5. Add dashboard removal/vendor/isolation/cursor, launch/contention/failure, configured-auth, and mutual-exclusion coverage.
6. Run the full local closeout contract.

## 10. Confidence and missing information

High confidence in flock semantics, documented topology, finding coverage, and the process-local throttle decision. High-but-inferred confidence that the production cron is currently inert; proving that requires a separately authorized post-release scheduled-response check. Evidence of multiple machines sharing one data set or a material Plaid call-rate constraint would change the recommendation.

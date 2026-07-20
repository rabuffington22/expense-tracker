# Work Block 4L — Sync Entry Coordination And Truthful Recovery

Date: 2026-07-19

Status: complete and verified locally; release not authorized

Scope: Phase 4 Task 1K for `P3-3H-02` through `P3-3H-07`, plus only the matching `P3-3H-C01` Task 2 regression-coverage slice.

## Review Intake

The exact direct Claude CLI review completed with `claude-fable-5` at `max` effort, read-only tools, plan permission, safe mode, no session persistence, and no fallback. It endorsed unchanged scope and required five amendments, all accepted:

1. initialize each scheduled entity after authorization inside its exception boundary;
2. add configured-auth endpoint coverage;
3. deliberately update the maintained checks pinned to replaced locks, exception behavior, and worker signature;
4. delete the dashboard worker's duplicate Luxe Legacy bridge call because `_sync_entity` already invokes it;
5. pin `fcntl.flock`-only and never-unlink invariants.

The reviewer inferred from tracked source that configured server authentication may currently redirect scheduled workflow requests before bearer validation while `curl --fail` remains green. This was not live-verified and did not widen implementation or authorize release.

## Implementation

- Added `core/sync_coordination.py` with one stable mode-0600 `DATA_DIR/.plaid-sync.lock`, non-blocking `fcntl.flock`, an idempotent lease, context-manager cleanup, process-death cleanup, and explicit never-unlink/no-record-lock invariants.
- Replaced the manual and scheduled module-local lock with the shared lease.
- Changed the scheduled bearer comparison to `secrets.compare_digest`.
- Made `/plaid/sync-all` explicitly exempt from browser session authentication and normal request entity setup while retaining POST-only, CSRF-exempt, bearer-protected behavior.
- Initialized each scheduled entity after authorization inside its own exception boundary, returned stable sanitized standard-shape failures, and continued later entities.
- Replaced the dashboard worker's duplicate Plaid add/modify/cursor implementation with `_sync_entity` for Personal and Luxe Legacy.
- Removed the dashboard worker's direct downstream bridge call so Luxe Legacy retains exactly one invocation through `_sync_entity`.
- Added one process-local launch lock, shared-lease-before-launch behavior, throttle update only after successful `Thread.start()`, ownership transfer on success, and immediate lease release without timestamp consumption on start failure.
- Preserved `/k/` access and refresh-on-view policy for later Task 1P; kept the 15-minute throttle process-local as reviewed.

## Maintained Synthetic Proof

- Separate opens contend within one process.
- A real second process cannot acquire while another process holds the lease.
- Normal close and explicit SIGKILL both make the lease immediately reacquirable.
- The stable lock inode remains mode 0600 and is never deleted.
- Scheduled and manual contention perform no sync work and preserve existing response behavior.
- A fresh app with configured server authentication returns 401 rather than 302 for missing bearer without entity initialization or category sync; correct bearer reaches the route and initializes Personal, BFM, and Luxe Legacy in order.
- Unexpected scheduled entity exceptions produce structured sanitized results, attempt all later entities, return truthful failure, omit raw exception detail, and release the lease.
- Dashboard success transfers lease ownership and consumes throttle; start failure releases and remains immediately retryable; contention does not consume throttle; throttled requests do not touch the lease.
- Dashboard-triggered sync deletes a removed transaction plus its split and advances the spending-item cursor atomically while a vendor item remains untouched and never reaches mocked Plaid.
- The public/dashboard seam invokes the Luxe Legacy bridge exactly once when LL has eligible items and zero times when it has none.
- Fake configuration and tokens, mocked Plaid and downstream functions, denied outbound sockets, temporary Personal/BFM/Luxe Legacy databases, and exact cleanup preserved the protected-data boundary.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass before product edits.
- Final `.venv/bin/python scripts/smoke_test.py`: pass with the new 8d2 coordination and recovery section plus every existing section.
- Python compilation for the coordinator, routes, app factory, and smoke suite: pass.
- `jq empty command-center/state.json`: pass.
- `git diff --check`: pass.
- Dashboard refresh and command-center health: required after this closeout state update.
- Preserved untracked `scripts/sync_prod_to_local.sh` and unrelated `command-center/now 2.md`: untouched and unstaged.

## Boundaries Preserved

No real database or financial, payroll, or HR row; upload; credential; authenticated production page; live Plaid call; workflow action; production/demo request; Fly action; downstream access/write; GitHub durability; deployment; `/k/` access-policy change; migration; queue; new service; or unrelated repair occurred.

## Result

Manual, scheduled, and dashboard-triggered synchronization now share one process-safe non-blocking lease across the documented two-worker data domain. The dashboard path consumes the maintained atomic item core instead of a divergent implementation; vendor and removed-event behavior are correct; scheduled entity failures are contained and truthful; bearer validation precedes mutable setup even with server authentication configured; and failed worker launch remains immediately retryable. Work block 4L is complete locally. Release and any live verification remain a separate 4L-R decision.

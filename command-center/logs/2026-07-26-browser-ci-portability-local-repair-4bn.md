# Browser CI Portability Diagnosis And Local Repair — Work Block 4BN

Date: 2026-07-26

Status: complete locally for Task 3.3.3a. Hosted reobservation, publication, and PR disposition remain separately gated.

## Diagnosis

- The tracked desktop rule gave `.txn-filter-date` a `130px` flex basis but left the flex item at the default `min-width: auto`.
- A temporary synthetic all-entity Chrome probe measured the desktop group at `132.44px` even though its computed flex basis was `130px`; the same group reported `min-width: auto`.
- This confirms that intrinsic date-control sizing could enlarge the flex item above its declared basis and explains why the Ubuntu Chrome runner could exceed the existing `125px`–`135px` acceptance range.
- Phone and exact-768 behavior came from later explicit responsive minimum-width and flex overrides, so the supported narrow repair was to set only the base desktop flex item to `min-width: 0`.

## Repair

- `web/static/style.css` now keeps `flex: 0 0 130px` and adds `min-width: 0` to `.txn-filter-date`.
- `scripts/mobile_drawer_browser_test.py` retains every existing acceptance threshold and appends sanitized `dateWidth` and `filterWidth` measurements to phone, exact-768, and desktop layout assertion failures.
- No workflow, action, runner, browser-version, dependency, product-flow, authentication, CSRF, CSP, migration, or acceptance-range change was made.

## Focused Measured Evidence

- Before the repair, Personal, BFM, and Luxe Legacy each measured `132.44px` for the desktop date group with a `130px` flex basis, `min-width: auto`, a `995.75px` filter bar, and no page overflow.
- After the repair, all three entities measured exactly `130.00px` on desktop with `min-width: 0`, the same `995.75px` filter bar, and no page overflow.
- Phone remained `340.75px` inside a `368.06px` filter bar with the explicit `100%` responsive minimum.
- Exact 768px remained `350.94px` inside a `739.31px` filter bar with the explicit two-column responsive minimum.
- Both focused probes denied non-localhost requests; the blocked-request list was empty.

## Verification

- Python compilation for the maintained browser test passed.
- `git diff --check` passed after the repair.
- The complete temporary-data smoke suite passed.
- The first full browser invocation, run concurrently with smoke, stopped before the changed transaction assertion because an unrelated dashboard partial response did not arrive within 30 seconds. Its temporary fixture was removed exactly and no process remained.
- One clean, non-concurrent rerun of the complete installed-Chrome suite passed both authentication modes, all entities, responsive and overflow contracts, CSP, denied-network behavior, and exact cleanup.
- Command-center JSON, refresh/currentness, health, whitespace, sensitive-addition, exact-path, zero-stage, remote-boundary, and preserved-file checks are recorded in the final Runway OS closeout.
- The in-app browser refused the localhost dashboard reinspection under its URL policy after the local server restarted. No alternate browser workaround was attempted. Generated-dashboard currentness and health checks passed; this UI-inspection limitation is retained explicitly.

## Boundaries Preserved

- All 4BN changes remain local, unstaged, uncommitted, and unpushed on `codex/browser-ci-observation`.
- Draft PR #88 remains open, draft, unmerged, and untouched. Its remote branch remains at marker commit `68959de40ca7de52cd20a0465d002ae4929c92ce`.
- No workflow execution, rerun, cancellation, PR mutation, merge, publication, deployment, Fly, Plaid, production/demo/downstream, credential, protected-data, or real-financial-data action occurred.
- `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and the unrelated duplicate 4AU log remained untouched and excluded.

## Next Gate

Task 3.3.3b and proposed work block 4BO remain a separate Ryan decision. If confirmed, 4BO may publish only the verified 4BN repair on the existing observation branch, observe the automatic hosted core-then-browser run, and close PR #88 without merge only after a completely clean success.

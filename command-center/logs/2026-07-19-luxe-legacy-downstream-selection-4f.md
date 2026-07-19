# Work Block 4F — Luxe Legacy Downstream Selection Boundary

Date: 2026-07-19

Status: complete and locally verified; release not authorized

## Scope

Work block 4F repaired only `P3-3I-01` and the focused Owner Draw/source-selection slice of `P3-3I-C01`. Empty Plaid identifiers, duplicate conflict keys, local or remote idempotency, downstream schema access or writes, broader bridge repairs, live actions, and GitHub durability remained excluded.

## Repair

`core/luxury_bridge.py` now excludes the maintained Luxe Legacy `Owner Draw` category instead of nonexistent LL `Owner Contribution`. Existing `Internal Transfer` and `Credit Card Payment` exclusions are unchanged.

The maintained smoke suite now uses fake configuration, mocked HTTP, denied outbound sockets, and temporary Personal, BFM, and Luxe Legacy databases to verify the corrected selection and invocation boundary.

## Evidence

- Failing-before coverage reproduced the original Owner Draw payload leak.
- The corrected payload contains the valid synthetic `Cost of Goods` and `Income` rows and omits `Owner Draw`, `Internal Transfer`, and `Credit Card Payment`.
- Direct bridge execution opens only the Luxe Legacy database.
- Before/after logical database snapshots prove the mirror read changes none of the three entity databases.
- The scheduled sync seam invokes the bridge zero times for Personal/BFM and exactly once for Luxe Legacy.
- The public Personal-plus-LL worker invokes the bridge exactly once.
- HTTP is mocked and sockets are denied, so no real Plaid or downstream request occurs.
- The maintained baseline passed before implementation and the full final suite passed after the repair.
- Python compilation, disposable-root cleanup, JSON validation, dashboard refresh, command-center health, and whitespace checks passed.

## Local Environment Note

`requests` is declared in `requirements.txt` but is absent from the local `.venv`. The maintained synthetic bridge section therefore supplies a test-only module stand-in when necessary and patches its HTTP call. This preserves offline verification without changing dependencies or production behavior.

## Preserved Boundaries

No real database or financial row, credential, production/demo page, Plaid call, downstream access or write, workflow action, Fly operation, commit, push, PR, merge, or deployment occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.

## Result

The proven source-selection defect is resolved locally with focused maintained regression coverage. Empty-ID handling remains for Task 1O, downstream idempotency remains parked behind a separately authorized read-only contract check, release remains a separate gate, and Task 1F is next for separate work-block planning.

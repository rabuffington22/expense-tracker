# Work Block 4W: Weekly Paydown Goal Validation

Date: 2026-07-21

Status: complete and verified locally; publication not authorized

## Scope

Completed Task 1N.5 plus only the focused Task 2 regression slice for `P3-3E-04` and matching `P3-3E-C01` coverage. The block stayed local and synthetic.

## Result

- The paydown-goal POST accepts only a canonical real date strictly later than the current local date.
- Invalid targets return sanitized guidance before database access and preserve the complete prior entity database.
- Valid updates preserve start date, start balance, creation timestamp, and singleton identity.
- A valid target repairs a malformed target-only row without altering usable start metadata.
- Malformed target dates, start dates, and start balances no longer break Weekly or Waterfall reads; unusable rows are ignored without read-time mutation.
- The Weekly input minimum now matches the server's next-day rule.
- Personal and BFM remain isolated, and Luxe Legacy remains denied before storage access.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including new maintained section 8a6.
- Python compilation for `web/routes/weekly.py`, `web/routes/waterfall.py`, and `scripts/smoke_test.py`: pass.
- Canonical future create, metadata-preserving update, malformed target recovery, empty/malformed/nonexistent/loose/today/past rejection, exact zero mutation, malformed stored target/start/balance reads, Weekly rendering, Waterfall route/helper behavior, browser minimum, Personal/BFM, Luxe Legacy denial, denied networking, unrelated-row preservation, and exact cleanup: pass.
- JSON validation, dashboard refresh, command-center health, whitespace, rendered dashboard inspection, and final worktree review: pass.

## Boundaries

No real database, row-level financial data, retained upload, credential, production/demo access, external call, workflow, Fly action, downstream write, migration, historical remediation, authentication or CSRF change, Waterfall calculation repair, commit, push, PR, merge, or deployment occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.

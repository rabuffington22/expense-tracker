# Work Block 4P — Payroll Import Integrity And Payload Lifecycle

Date: 2026-07-20

Status: complete and verified locally on `codex/payroll-import-integrity`

## Scope

Completed Tasks 1M.1-1M.3 for `P3-3F-02`, `P3-3F-05`, `P3-3F-06`, and only their focused `P3-3F-C01` coverage slice. Tasks 1M.4-1M.5, broader regression work, protected data, retained user uploads, migrations, live systems, GitHub durability, and deployment remained excluded.

## Result

- Preview now receives explicit normalized-name match data instead of relying on a loop-local template assignment.
- One exact existing employee is selected by default; any existing employee can be selected explicitly; creation appears only for genuinely unmatched names.
- Save repeats the same rule, so a forged `new` submission cannot create a duplicate when one exact existing match exists. Ambiguous existing names require an explicit existing-employee selection.
- Preview Cancel is an explicit BFM-only POST that removes only its exact payload and is safe when repeated or given a missing or invalid key.
- Payroll payloads use mode `0600`; fresh structural validation precedes use; missing, reused, expired, malformed, and structurally invalid payloads redirect without payroll mutation.
- Unsupported filename types are rejected before parsing. Workbook-engine read failures become one sanitized controlled outcome without retaining payload data, while headerless and valid multi-section behavior remains explicit.
- No database migration or `core/db.py` change was required.

## Verification

- Baseline maintained `.venv/bin/python scripts/smoke_test.py`: pass.
- Final maintained `.venv/bin/python scripts/smoke_test.py`: pass.
- Focused generated-XLSX checks: exact existing match, forged-new duplicate prevention, explicit reassignment, unmatched creation, exact reimport, and valid multi-section parsing pass.
- Isolated payload checks: mode `0600`, save, cancel, missing, reused, expired, malformed, invalid key, unrelated-payload preservation, idempotency, and empty final directory pass.
- Invalid workbook checks: corrupt, empty, mislabeled, unsupported extension, and headerless outcomes return controlled responses and retain no new payload.
- Temporary Personal and Luxe Legacy payroll tables remain unchanged; BFM-only route coverage includes all nine registered payroll routes.
- Outbound sockets were denied throughout the focused matrix; no external call occurred.
- Python compilation, JSON validation, `git diff --check`, dashboard refresh, command-center health, rendered-dashboard inspection, and explicit worktree review pass at closeout.

## Boundaries Preserved

No real payroll, HR, financial, credential, upload, production, demo, Plaid, OpenRouter, workflow, Fly, downstream, or external-system data or action was used. No commit, push, PR, merge, or deployment occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched.

## Next

Task 1M.4 is next for a separately confirmed work block. The recommended shape is 4Q Atomic Payroll Roster Validation with only its focused Task 2 coverage. Publication of 4P remains separately gated.

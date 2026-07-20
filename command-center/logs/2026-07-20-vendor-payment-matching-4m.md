# Work Block 4M — Vendor Payment Matching Integrity

Date: 2026-07-20
Branch: `codex/vendor-payment-matching-integrity`
Durability: local-only; no commit, push, PR, merge, deployment, or live verification authorized

## Authorized Scope

Task 1L.1 plus only the focused Task 2 vendor-payment matching regression slice. The successful natural scheduled run `29740509073` had already cleared the activation gate.

Excluded throughout: Tasks 1L.2-1P; broader Task 2; Tasks 3-4; existing-row detection or remediation; import `Undo` wording; migrations or backfills; real databases, financial rows, uploads, credentials, production authentication, live Plaid or vendor access, workflows, Fly, downstream access or writes; GitHub durability; deployment; `scripts/sync_prod_to_local.sh`; and `command-center/now 2.md`.

## Implemented Contract

- Removed every vendor-matching dependency on nonexistent `transactions.matched_order_id`.
- Made `vendor_transactions.matched_transaction_id` the canonical one-bank-to-one-vendor relationship.
- Selected available bank transactions with a `NOT EXISTS` relationship check.
- Serialized matching and application with SQLite `BEGIN IMMEDIATE` transactions.
- Prevalidated accepted batches and rejected missing, stale, duplicate, or already-claimed relationships before unrelated mutation.
- Preserved exact auto-application and likely/loose review behavior.
- Kept successful enrichment limited to the selected bank transaction's merchant and notes plus the selected vendor relationship and confidence.

## Synthetic Evidence

Across temporary Personal, BFM, and Luxe Legacy databases built from ordered migrations:

- the absent bank-side column was confirmed and the matching workflow ran successfully;
- exact candidates auto-applied and likely candidates remained reviewable until accepted;
- unmatched vendor and unmatched bank outcomes remained truthful;
- stale replay and duplicate batch claims failed without changing transaction state;
- two concurrent writers competing for one bank transaction produced exactly one committed claim and one rejected claim;
- a forced failure on the second accepted match rolled both bank and vendor changes back;
- unrelated control rows and the other entity databases remained unchanged;
- outbound sockets were denied and every synthetic vendor and bank row was removed before suite completion.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including new section 7e.
- `.venv/bin/python -m py_compile core/vendor_matching.py scripts/smoke_test.py`: pass.
- No migration or backfill: confirmed; `core/db.py` is unchanged.
- `git diff --check`: pass before Runway OS closeout.
- No protected data, credential, live system, application-integration request, or preserved untracked-file change occurred.

Final JSON validation, dashboard refresh, health check, dashboard inspection, and explicit worktree review are recorded by the Runway OS closeout after state is aligned.

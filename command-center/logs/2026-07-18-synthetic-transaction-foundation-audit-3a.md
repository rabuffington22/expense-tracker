# Work Block 3A: Synthetic Transaction Foundation Audit

Date: 2026-07-18

Status: done

## Confirmed Scope

Audit Phase 3 Task 1 using tracked source, the existing synthetic smoke suite, and ephemeral probes against temporary databases. Cover database initialization, entity selection and isolation, deterministic transaction identity and deduplication, debit-sign convention, edit and split behavior, and effective-reporting split replacement across Personal, BFM, and Luxe Legacy.

## Exclusions

Tasks 2-8; product fixes; tracked test expansion; real databases, uploads, credentials, or row-level financial data; production/demo access; Plaid, workflow, Fly, or downstream actions; authentication/security changes; GitHub durability; and pre-existing untracked `scripts/sync_prod_to_local.sh`.

## Evidence Contract

Record only sanitized behavior-level results. Classify each audited area as pass, defect, regression-coverage gap, or unverified boundary. A finding that requires implementation is recorded for later work and is not fixed inside 3A.

## Verification Result

The existing smoke suite passed against a temporary `DATA_DIR`, including creation of all three databases, import normalization, first insert, exact re-import deduplication, database isolation, route regression checks, exports, saved views, and To Do isolation.

The ephemeral 3A probe also passed these behaviors:

- distinct database paths, aligned schema versions, seeded categories, WAL mode, foreign-key enforcement, and rejection of unknown entity keys;
- independent storage of the same deterministic ID in Personal, BFM, and Luxe Legacy;
- preservation of negative debit amounts in dollars and integer cents;
- BFM denial of Personal transaction edit and split requests;
- successful Personal edit persistence without BFM or Luxe Legacy mutation;
- same-sign split validation, rejection of a wrong-sign replacement, and preservation of the prior valid split set;
- effective-reporting replacement of the split parent with two split pieces whose signed total matches the parent.

## Audit Matrix

| Area | Classification | Result |
| --- | --- | --- |
| Database initialization and entity paths | Pass | All three entities used distinct databases with aligned schema state. |
| Entity selection and isolation | Pass | Cross-entity reads and writes were denied, and non-target databases stayed unchanged. |
| Debit sign and integer cents | Pass | A synthetic debit preserved its negative dollar and cent values. |
| Deterministic identity and exact re-import | Defect | Exact duplicates are suppressed, but the identity omits account/source identity and also suppresses legitimate collision rows. |
| Transaction edit behavior | Pass with regression gap | Current synthetic edit behavior passed; no tracked edit test exists. |
| Split validation and persistence | Pass with regression gap | Current sign, total, isolation, and preservation behavior passed; no tracked split test exists. |
| Effective reporting | Pass with regression gap | Split pieces replaced the parent and preserved the signed total; no tracked regression test proves it. |
| Plaid identity impact | Unverified boundary | Source uses the same hash helper, but Plaid and live behavior belong to Task 5 and were not exercised. |

## Ranked Findings

1. High financial-data completeness risk: transaction identity hashes only date, amount, and description. Two synthetic rows differing only by account collided; one inserted and one was silently skipped. Actual production occurrence is unknown because no real data was opened.
2. Medium regression-confidence risk: edit, split, cross-entity denial, and effective-reporting behavior passed ephemeral checks but are absent from the tracked smoke suite.

Both findings are recorded in `command-center/issues.md`. No product fix or tracked test expansion was made.

## Boundaries Preserved

No real database, upload, credential, row-level financial data, production/demo endpoint, Plaid action, workflow action, Fly action, downstream write, authentication change, product edit, tracked test edit, commit, push, PR, merge, or deployment occurred. Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched.

## Conclusion

Task 1 is auditable and mostly behaves correctly under synthetic evidence, but transaction identity is not sufficiently unique for legitimate repeated activity. The safest next implementation decision is a separately designed identity-and-migration repair block after Ryan prioritizes the finding; the next Phase 3 audit slice remains Task 2.

## Post-Block Durability

After the audit and local verification were complete, Ryan separately authorized committing and pushing the exact seven-path command-center closeout directly to `main`. It is published with the established `[skip actions]` convention so the command-center-only push does not start the production Fly deployment workflow. No product, tracked test, workflow, protected-data, or pre-existing untracked-file change is included.

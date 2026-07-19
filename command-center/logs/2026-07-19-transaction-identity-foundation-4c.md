# Work Block 4C Closeout: Transaction Identity Foundation

Date: 2026-07-19
Branch: `codex/transaction-identity-foundation`
Durability: local-only; no commit, push, PR, merge, workflow, deployment, credential, protected-data, or live action

## Result

Work block 4C is complete for `P3-3A-01` and paired coverage item `P3-3A-C01`.

- `command-center/transaction-identity-contract.md` now defines versioned, namespaced, opaque transaction IDs and immutable existing keys.
- File normalization uses a stable source fingerprint, normalized account-aware row key, and occurrence ordinal. Legitimate identical rows in one payload coexist, distinct sources and accounts do not collide, and exact same-source payload redelivery is idempotent.
- New primary Plaid rows use the authoritative non-empty `plaid_transaction_id`. Empty or whitespace-only IDs fail before insert rather than sharing a fallback identity.
- A pre-4C row already bound to a Plaid ID retains its issued legacy primary key on redelivery. No existing ID or reference is rewritten.
- No additive migration was needed because the existing text primary key already stores the new opaque hashes.

## Maintained Coverage

`scripts/smoke_test.py` now proves with temporary synthetic data:

- deterministic source, account, occurrence, and authoritative-external identity behavior;
- same-source duplicate preservation and exact-redelivery skipping across Personal, BFM, and Luxe Legacy;
- rejection of missing file sources and empty external IDs;
- coexistence of matching legacy, file, and Plaid natural fields without aliasing;
- populated database re-entry preserving legacy transaction IDs, edits, negative debit cents, split references and totals, Amazon order matches, aliases, and effective-reporting split replacement;
- preservation of an existing legacy primary key already bound to a Plaid transaction ID;
- mocked primary Plaid insert/redelivery behavior while outbound sockets are denied.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including the new 7b identity section and the existing route, export, saved-view, to-do, authentication, and cache suites.
- `.venv/bin/python -m py_compile core/imports.py web/routes/plaid.py scripts/smoke_test.py`: pass.
- Final temporary smoke directory removal: pass.
- `git diff --check`: pass.
- `jq empty command-center/state.json`: pass after closeout.
- Dashboard refresh and command-center health check: pass after closeout.

## Preserved Boundaries

Only identity computation, legacy identity resolution at the primary Plaid insert seam, maintained focused coverage, and command-center artifacts changed. There was no migration, database transfer, real financial or payroll row, upload, credential, network call, Plaid client action, cursor or persistence-order change, reconciliation, concurrency work, workflow, Fly action, downstream write, `/k/` change, unrelated repair, commit, push, PR, merge, or deployment. Pre-existing untracked `scripts/sync_prod_to_local.sh` remained untouched.

## Remaining Gate And Next Block

The repair is verified only in the local worktree. GitHub durability and release require a separate Ryan authorization.

The recommended next implementation block remains a separately planned boundary/truthfulness 4D, provisionally beginning with `P3-3F-01` BFM-only payroll route enforcement and its paired boundary coverage. Its exact scope and authorization are not part of 4C.

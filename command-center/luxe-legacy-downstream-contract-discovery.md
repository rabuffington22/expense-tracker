# Luxe Legacy Downstream Contract Discovery

Date: 2026-07-21

Work block: 4Z — Downstream Idempotency Contract Discovery

Status: complete from tracked local sources; no implementation or live downstream verification performed

## Question

Does the intended downstream repository establish `ledger_transactions.plaid_transaction_id` as a unique conflict key, and which explicit PostgREST conflict target should the Ledger mirror use?

## Repository Identity

- Intended downstream repository: `/Users/ryanbuffington/Documents/GitHub/luxurious luxury`.
- Tracked README title: `Luxurious Luxury`.
- Tracked README identifies Supabase/Postgres and directs operators to apply `src/lib/db/schema.sql` as the database schema.
- Inspected branch and commit: `main` at `089d15c3db69bf00b00bec6a35fdd95ead61e2db`.
- The downstream worktree had pre-existing untracked `.claude/worktrees/`; it was not opened, changed, staged, or otherwise used.

This establishes the repository named by the Ledger bridge docstring as the tracked downstream contract source.

## Tracked Downstream Contract

The downstream contract is explicit:

- `src/lib/db/schema.sql:162-172` creates `ledger_transactions` and declares `plaid_transaction_id TEXT PRIMARY KEY`.
- `src/lib/db/schema.sql:185-190` makes both purse match columns reference `ledger_transactions(plaid_transaction_id)`.
- `scripts/import-apple-card.ts:253-260` describes the operation as idempotent on `plaid_transaction_id` and calls Supabase `.upsert(..., { onConflict: "plaid_transaction_id" })`.
- `src/lib/db/schema.sql` is the only tracked SQL file in the downstream repository.
- Git blame attributes the primary-key declaration to downstream commit `e9163a98` from 2026-05-15.

Therefore the tracked downstream uniqueness key and explicit conflict target are both `plaid_transaction_id`.

## Ledger Comparison

The Ledger bridge intent matches the downstream contract, but its enforcement is incomplete:

- `core/luxury_bridge.py:3-5` documents `plaid_transaction_id` as the conflict key.
- `core/db.py:332-335` creates only a non-unique local index on `transactions.plaid_transaction_id`, so legacy or malformed local state can still supply repeated downstream keys.
- `core/luxury_bridge.py:41-48` rejects only SQL `NULL`; empty or whitespace-only identifiers remain eligible.
- `core/luxury_bridge.py:55-67` builds one payload row per eligible local row without duplicate-key validation.
- `core/luxury_bridge.py:69-80` sends `Prefer: resolution=merge-duplicates` to `/rest/v1/ledger_transactions` but does not explicitly name `plaid_transaction_id` in an `on_conflict` request parameter.

## Verdict

- The Task 1O.1 tracked-contract gate is satisfied.
- The downstream tracked schema uniquely constrains `plaid_transaction_id` as the primary key.
- The explicit conflict target for the Ledger request is `plaid_transaction_id`.
- No downstream schema or migration change is indicated by tracked sources.
- The current Ledger request is data-contract compatible but leaves the conflict target implicit and permits malformed or repeated local keys into one payload.
- Tracked local evidence does not prove that the deployed Supabase schema exactly matches the tracked file or prove live runtime behavior. Work block 4Z intentionally did not inspect production; that residual uncertainty does not require guessing the local contract because the repository's maintained schema and importer agree.

Tasks 1O.2-1O.4 are ready for one separately confirmed local implementation block: validate non-empty normalized identifiers, handle repeated keys deterministically without blocking unrelated valid rows, name the conflict target explicitly, and add the remaining maintained synthetic coverage with mocked HTTP and denied outbound sockets.

## Boundary Exception

The initial tracked-source `git grep` was too broad and returned a matching line from tracked `.claude/memory.md` that contained credential-related history, including a credential value. No value is reproduced in this artifact, command-center state, or report. The search scope was narrowed immediately to exact tracked schema, importer, README, and Ledger files. No local environment file, keychain, database, row-level financial data, untracked payload, network, Supabase surface, or live system was accessed.

Future cross-repository contract discovery should exclude tracked memory and plan files from the first search and start from `git ls-files` plus exact schema/request paths.

## Preserved Boundaries

- No downstream repository file changed.
- No fetch, pull, credential file, local environment, keychain, database, row data, untracked payload, network request, Supabase access, or live action occurred.
- No Expense Tracker application, maintained test, schema, migration, workflow, or deployment file changed.
- Pre-existing untracked `scripts/sync_prod_to_local.sh`, unrelated untracked `command-center/now 2.md`, and downstream untracked `.claude/worktrees/` remained untouched.
- No commit, push, PR, merge, workflow, Fly action, deployment, Plaid action, or downstream write occurred.

## Next Gate

Plan and confirm work block 4AA for Tasks 1O.2-1O.4. Implementation should remain local-only and must stop if correct handling would require a downstream schema change, production verification, or a product decision not established by the tracked contract.

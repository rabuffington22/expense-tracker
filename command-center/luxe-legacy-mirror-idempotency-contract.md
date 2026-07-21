# Luxe Legacy Mirror Idempotency Contract

Date: 2026-07-21

Work block: 4AA — Mirror Key Validation And Explicit Idempotency

Status: complete and verified locally; publication not authorized

## Established Downstream Contract

Work block 4Z established from tracked local downstream sources that `ledger_transactions.plaid_transaction_id` is the primary key and the intended explicit PostgREST conflict target. No downstream schema or migration change is indicated. Deployed-schema and live-response behavior remain intentionally uninspected.

## Local Selection Contract

- Ledger remains the source of truth and the bridge remains read-only against its SQLite source.
- SQL `NULL` identifiers remain ineligible at the query boundary.
- A selected identifier must be a non-empty string equal to its stripped value. Empty, whitespace-only, and whitespace-padded identifiers are malformed and are withheld without rewriting the source row.
- Repeated valid identifiers are grouped by exact opaque key. Every row in a repeated-key group is withheld rather than choosing a winner.
- An invalid or duplicate group does not suppress unrelated valid rows.
- Selection order is deterministic by Plaid transaction ID and Ledger transaction ID.
- Sanitized warnings contain only malformed-row, duplicate-row, and duplicate-key counts. They do not contain identifiers, descriptions, amounts, accounts, or other row data.
- If no valid unique rows remain, the bridge returns zero without making an HTTP request.

## Request Contract

- Endpoint path: `/rest/v1/ledger_transactions` under the configured downstream base URL.
- Conflict parameter: `on_conflict=plaid_transaction_id`.
- Resolution preference: `resolution=merge-duplicates`.
- Authentication and content headers retain the existing service-key and JSON contract.
- Timeout remains 15 seconds.
- A successful request returns the number of valid unique rows sent.
- Request or response failure remains isolated from the Plaid sync, logs the existing sanitized failure message, returns zero, and never mutates any Ledger entity database.

## Preserved Boundaries

- No database migration, historical remediation, or source-row mutation.
- No downstream-repository change.
- No credential, protected-data, production, deployed-schema, Supabase, Plaid, Fly, workflow, deployment, or other live access.
- No GitHub durability action.
- Personal and BFM remain outside bridge storage access; scheduled and public invocation remain Luxe Legacy-only.

## Maintained Verification

Focused section 8c in `scripts/smoke_test.py` covers absent and partial configuration; invalid-only no-request behavior; mixed null, malformed, duplicate, excluded, and valid rows; deterministic repeat payloads; explicit request path, headers, conflict target, preference, timeout, and payload; sanitized count warnings; downstream failure isolation; all-entity preservation; scheduled/public Luxe Legacy-only invocation; denied outbound sockets; and exact cleanup.

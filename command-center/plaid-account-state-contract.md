# Plaid Account-State Truthfulness Contract

Date: 2026-07-19

Scope: work block 4J, Phase 4 Task 1I, `P3-3G-02` through `P3-3G-05`, and only the matching reconciliation, link, liability, and freshness slice of `P3-3G-C01`.

## Authoritative Unit

One non-vendor Plaid item is the account-refresh and liability-refresh unit. A successful response for one item is authoritative only for that item. A failed or skipped response is not evidence that any cached account, balance, or liability disappeared.

The application records separate successful-refresh timestamps on each Plaid item:

- `accounts_last_synced` governs account and balance freshness;
- `liabilities_last_synced` governs credit-card liability freshness.

Both columns are additive and nullable. Existing databases upgrade with null markers, causing the next configured Cash Flow load to refresh each data set once instead of treating legacy row timestamps as authoritative.

## Account Reconciliation

For a successfully fetched item:

- enabled non-investment accounts are inserted or updated by stable `plaid_account_id`;
- account names, balances, types, limits when supplied, and display order may refresh;
- disabled, investment, removed, or otherwise non-selected accounts belonging to that item are removed from `account_balances`;
- manual rows with no Plaid account ID are never candidates for automatic reconciliation;
- another item's cached rows are never candidates for this item's reconciliation; and
- `accounts_last_synced` advances only after the item-specific writes and cleanup commit.

If fetching or applying one item fails, its prior cached rows and refresh marker remain unchanged. Successful sibling items may still reconcile independently.

## Link Exchange And Manual Accounts

Plaid Link persists the returned item and its stable Plaid accounts. It does not infer that a manual account is a placeholder from a shared first word, institution name, or display name.

Until the product has an explicit stable placeholder identity or user-confirmed merge operation, all manual accounts survive link exchange. A failed exchange leaves both Plaid and manual account state unchanged.

## Liability Refresh

Liabilities refresh independently from balances. A successful balance refresh cannot make liabilities fresh, and a successful liability refresh cannot make balances fresh.

For each stale Plaid item:

- a successful liability response is applied only to cached accounts linked through that item;
- returned balance, credit-limit, due-date, and minimum-payment fields update when supplied;
- an authoritative empty liability response advances `liabilities_last_synced` without clearing last-known-good fields; and
- `liabilities_last_synced` advances only after the item's liability writes commit.

If the liability call or local application fails, last-known-good fields and the prior liability marker remain unchanged. That state is distinguishable from a successful empty response because only the successful response advances the marker.

## Freshness

Freshness is evaluated per Plaid item and data set. One fresh item cannot suppress a stale sibling, and a partial failure cannot mark the failed item current. The existing one-hour cache interval remains unchanged.

## Explicit Exclusions

Work block 4J does not change transaction sync, cursor semantics, missing-modification counts, token-decryption isolation, scheduled/public entry points, downstream mirroring, automatic retries, public routes, authentication, or live Plaid behavior.

## Maintained Acceptance Proof

`scripts/smoke_test.py` must use temporary Personal, BFM, and Luxe Legacy databases, fake tokens, mocked Plaid functions, and denied outbound sockets to prove:

- populated databases migrate additively with null account and liability refresh markers;
- one successful item reconciles only its own enabled accounts;
- a failed sibling preserves its cached rows and marker;
- authoritative disabled, investment, and removed accounts are cleaned up even when the keep set is empty;
- manual accounts survive success, empty, disabled, partial-failure, similar-name, and failed-link cases;
- a normal stale load fetches and applies both balances and liabilities;
- separate fresh markers suppress only their matching data set;
- one fresh item does not suppress a stale sibling;
- liability failure preserves last-known-good values and marker, while successful empty liability response advances the marker; and
- entity isolation, denied networking, unchanged unrelated rows, and exact disposable cleanup remain intact.

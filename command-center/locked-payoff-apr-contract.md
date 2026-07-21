# Locked Payoff APR Contract

Date: 2026-07-20

Work block: 4S — Locked Payoff APR Truthfulness

Finding: `P3-3D-01`

## Calculation Inputs

- Each linked credit card contributes its current absolute balance, estimated minimum payment, and stored `account_balances.apr_bps` value to the locked payoff timeline.
- A stored integer APR of zero is valid and means 0%.
- A missing or negative APR is unavailable. The application must not substitute a default rate.

## Locking Behavior

- If any linked credit card has an unavailable APR, the request returns controlled guidance to set APR in Cash Flow.
- Rejection occurs before the goal row changes. The prior strategy, monthly amount, target date, narrative, and saved schedule remain intact.
- Avalanche orders active balances by stored APR from highest to lowest.
- Snowball orders active balances by current balance from smallest to largest, independently of APR and linked-account order.
- The saved schedule is computed from the same account-specific balances, APRs, minimum payments, strategy, and monthly-extra value stored with the locked plan.

## Boundaries

- This contract does not change Cash Flow APR entry, account schema, migrations, historical rows, payoff strategies, snapshot behavior, Long-Term Planning, Weekly, or Waterfall.
- Personal and BFM retain Short-Term Planning access. Luxe Legacy remains denied before the route handler.
- Verification uses only temporary synthetic databases with outbound networking denied.
- GitHub durability, deployment, production, credentials, protected data, and live systems remain separately gated.

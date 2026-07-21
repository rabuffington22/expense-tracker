# Weekly Date And Bill Contract

Date: 2026-07-21

Applies to work block 4V, Phase 4 Task 1N.4, `P3-3E-01`, `P3-3E-02`, and the focused `P3-3E-C01` regression slice.

## Viewed-Week Date Context

- The requested ISO week's Monday owns the Weekly budget month.
- Monthly and category budgets use that month's actual calendar-day count when deriving a seven-day pace.
- The Weekly spending interval remains the requested Monday through Sunday.
- MTD and burn-rate calculations begin on the first day of the Monday-owned month and end at the earliest of the viewed Sunday, the real current date, or the last day of that month.
- A week crossing a month or year boundary cannot extend the MTD numerator or day count into the adjacent month.
- The displayed budget month, weekly pace, last-week comparison pace, category warnings, MTD window, and burn-rate divisor use the same Monday-owned month.
- A syntactically invalid ISO week falls back to the actual current ISO week under the same rules.

## Bill Projection Context

- Detected recurring, manual recurring, and credit-card due helpers accept an optional reference date.
- Weekly passes the viewed Monday and a seven-day horizon so historical and boundary weeks project bills from that week instead of the real current date.
- Existing Cash Flow and Short-Term Planning callers omit the reference date and retain today-based behavior.
- Manual action-item due days and BFM payroll dates continue to be evaluated directly inside the viewed interval.
- Weekly bill rows remain ordered by projected date.

## Credit-Card Amount Contract

- A positive `payment_amount_cents` value is the Weekly credit-card bill amount.
- The row title, amount, and Weekly total reconcile to that same integer-cent value.
- A missing or zero scheduled amount remains an explicit payment reminder with an unavailable amount and contributes nothing to the total.
- Weekly never substitutes `balance_cents` for an unavailable scheduled payment.
- A zero-balance card remains outside the upcoming-payment helper even if it has a stored scheduled amount.

## Preserved Boundaries

- No migration, historical-row remediation, demo change, authentication change, or broad UI redesign is required.
- Personal and BFM remain isolated databases with the existing intended Weekly behavior; Luxe Legacy remains denied before Weekly handling.
- Verification uses only disposable synthetic databases, denies outbound networking, proves unrelated-row preservation and exact fixture cleanup, and requires no credentials or live systems.
- Commit, push, PR, merge, workflow, deployment, production/demo access, Plaid, downstream writes, and other live actions remain separately gated.

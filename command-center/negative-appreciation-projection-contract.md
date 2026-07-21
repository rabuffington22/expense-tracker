# Negative Appreciation Projection Contract

Date: 2026-07-20

Work block: 4U Negative Appreciation Truthfulness

## Scope

Long-Term Planning must treat an asset's stored negative `annual_rate_bps` as depreciation instead of silently replacing it with zero growth.

## Calculation

- Positive and negative nonzero annual rates use the existing future-value calculation: current value compounds annually and end-of-year contributions accumulate at the same rate.
- A zero annual rate keeps the explicit linear-contribution path, avoiding division by zero.
- The existing inflation adjustment remains applied after nominal projection.
- Rates at or below -100% are outside this repair's product-policy scope. If they become material, handling requires a separate decision rather than an implicit clamp or validation change.

## Reconciliation

- Each projected asset value feeds its entity's projected asset total.
- Entity net worth remains projected assets minus projected liabilities.
- Combined Personal/BFM net worth remains the sum of the visible entity net-worth totals.
- The existing demo-equivalent Equipment case at -15% must decline across future milestones.

## Boundaries

No migration, historical remediation, input-policy change, template change, demo-seed change, protected-data access, external call, GitHub durability, deployment, or live action belongs to 4U.

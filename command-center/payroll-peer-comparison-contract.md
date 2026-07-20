# Payroll Peer Comparison Contract

Date: 2026-07-20

Status: active implementation contract for work block 4R

## Purpose

Keep payroll peer guidance mathematically truthful without inventing a common compensation unit.

## Cohort Rules

- A peer is another active BFM employee with the same maintained role and the same `pay_type`.
- The selected employee never contributes to their own peer average.
- Inactive and terminated employees never contribute to a cohort.
- An inactive or terminated selected employee may still compare against current active peers with the same role and pay type.
- Hourly and salary values are never mixed, converted, or annualized.
- Every contributing stored rate is included, including zero. A real zero average is distinct from an empty cohort.
- The average is rounded to integer cents using the existing Python rounding behavior.

## Response And Display

- `peer_avg_cents` is an integer when at least one comparable peer exists, including `0` for a real zero average.
- `peer_avg_cents` is `null` when no comparable peer exists.
- `peer_count` reports the number of contributing peers.
- The modal labels the value as the same-role and same-pay-type peer average and formats it as `/hr` or `/yr` from the selected employee's pay type.
- An empty cohort displays `No comparable peers` instead of a currency value.

## Preserved Boundaries

- Payroll remains BFM-only.
- Employee storage, validation, import, identity, deletion, pay history, and payroll-entry calculations do not change.
- No migration, historical-row cleanup, real payroll data, retained upload, credential, production/demo access, external call, GitHub durability, deployment, or live action is part of 4R.

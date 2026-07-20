# Atomic Payroll Roster Validation Contract

Date: 2026-07-20

Work block: 4Q

Scope: Phase 4 Task 1M.4 for `P3-3F-04` and only its focused `P3-3F-C01` coverage slice.

## Roster Domains

- Employee names are required after surrounding-whitespace removal. Matching uses the same case-folded, trimmed key in preview and save.
- Roles must be one of the maintained payroll roles: Providers, Nurses, Scribes, Front Office, Office Manager, HR, or Owner.
- Pay type must be `hourly` or `salary`.
- Status must be `active`, `inactive`, or `terminated`. Manual and imported creation use `active`.
- Hire date is optional. A present value must be a real calendar date in exact `YYYY-MM-DD` form. Future dates remain allowed.
- Phoenix job code is optional, trimmed, and stored as null when empty. No new code whitelist is inferred.
- Manual update IDs and imported existing-employee assignment IDs must resolve inside the active BFM database.
- Imported assignment names must resolve to an employee in the consumed payroll payload. A forged form-only name cannot create a roster row.
- Each normalized payload employee may appear in the assignment form only once; case variants cannot create duplicate pending employees.

## Pay Rates

- Empty input preserves the existing zero-rate behavior.
- Currency parsing uses decimal arithmetic and rounds to integer cents with half-up rounding.
- Non-numeric, non-finite, negative, and greater-than-`$999,999,999.99` values are rejected before mutation.
- Extreme exponent input is bounded before decimal quantization and returns the same controlled maximum error.

## Atomicity And Feedback

- Manual create validates the complete employee row before opening a write transaction.
- Manual update validates before rate-history or employee mutation. A positive-to-positive rate change and its employee update commit or roll back together.
- The existing zero-to-positive rule is preserved: the employee rate changes without inventing a prior positive-rate history row.
- Payroll import validates the full assignment and new-employee batch before the first insert.
- An unexpected payroll-entry persistence failure rolls back every new employee and payroll entry in that save.
- Controlled validation failures flash a sanitized field-level message and redirect to Payroll without echoing submitted values.
- Rejected create, update, and import requests leave employees, pay changes, and payroll entries unchanged.

## Preserved Boundaries

- The payroll blueprint remains BFM-only before storage or payload handling.
- Import payloads retain the 4P one-use contract. A rejected save consumes only its exact payload and does not retain payroll contents.
- Employee deletion, duplicate-identity policy, compensation comparisons, migrations, historical cleanup, real data, retained uploads, credentials, production, live systems, GitHub durability, and deployment remain outside 4Q.

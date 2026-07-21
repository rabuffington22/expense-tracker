# Weekly Paydown Goal Validation Contract

Date: 2026-07-21

Status: verified locally through work block 4W; publication not authorized

## Write Contract

- A submitted target must be one canonical `YYYY-MM-DD` calendar date strictly later than the server's current local date.
- Empty, malformed, nonexistent, loose-format, today, and past targets return sanitized guidance before a database connection is opened.
- A rejected target leaves the entire entity database unchanged.
- A valid create stores today's canonical start date and the current entity's total positive credit-card balance.
- A valid update changes only the target date and preserves the singleton row identity, creation timestamp, start date, and start balance.
- A valid target can recover a row whose target alone is malformed when the stored start date and balance remain usable.
- An unusable stored start date or start balance blocks target-only mutation and requires a separately scoped review rather than implicit repair.

## Read Contract

- Weekly and Waterfall share `_get_paydown_goal()` as their stored-goal boundary.
- Canonical start and target dates, a target later than the start, a start no later than today, and a non-negative integer start balance are required for pace calculation.
- An unusable stored row is treated as unavailable. Reads do not delete, normalize, or otherwise mutate it.
- `_compute_paydown_pace()` repeats the scalar checks so a malformed direct helper input also returns no pace instead of raising.

## Preserved Boundaries

- Personal and BFM retain entity-local goals and valid create/update behavior.
- Luxe Legacy remains denied before storage access.
- Waterfall averaging, payoff rounding, and tax normalization are unchanged.
- No schema, migration, historical remediation, authentication, CSRF, protected-data, external, GitHub, deployment, or live-system action is part of 4W.

## Maintained Evidence

`scripts/smoke_test.py` section 8a6 covers valid create/update, preserved metadata, invalid-input zero mutation, malformed stored target/start/balance reads, target-only recovery, browser minimum-date guidance, Weekly and Waterfall rendering, Personal/BFM isolation, Luxe Legacy denial, denied networking, and exact cleanup.

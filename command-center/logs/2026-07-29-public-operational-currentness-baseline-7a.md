# Work Block 7A — Public Operational Currentness Baseline

Date: 2026-07-29 CDT

Status: stopped on the first failed observation

## Confirmed Scope

Ryan confirmed Phase 7 Task 1 (`P7-T1`) only for at most five fail-closed external reads in order:

1. one credential-free production `/health` request;
2. one credential-free demo `/health` request;
3. one public Daily Plaid Sync workflow identity/state query;
4. one public newest-`schedule`-run query;
5. one exact `expense-tracker-daily-plaid-sync-monitor` currentness query.

Each observation records its exact target, route, Central Time, authorized and consumed count, sanitized result, threshold comparison, evidence label, limitations, and no-remediation confirmation. The block stops on the first anomaly without retry, diagnosis, repair, or expansion.

Tasks 2-7, exact-ref CI or Fly evidence, authentication, logs, workflow or automation mutation, Plaid sync, provider, database, financial, backup, recovery, protected-data, product, test, Git, publication, deployment, delegation, second opinion, and unrelated work are excluded.

## Observation Record

Observation window: 2026-07-29 10:24-10:25 PM CDT

Authorized external-read budget: at most five, fail closed in the listed order.

Consumed external reads: two.

1. Production `/health`
   - Target: `https://ledger-oak.fly.dev/health`
   - Route: one credential-free CLI HTTP request with redirects disabled
   - Result: HTTP 200, no redirect, exact minimal body `{"status":"ok"}`
   - Threshold comparison: pass
   - Evidence label: externally observed passing at 2026-07-29 10:24 PM CDT
2. Demo `/health`
   - Target: `https://ledger-oak-demo.fly.dev/health`
   - Route: one credential-free CLI HTTP request with redirects disabled
   - Result: HTTP 404, no redirect, standard sanitized not-found response rather than the expected minimal health response
   - Threshold comparison: fail
   - Evidence label: externally observed failing at 2026-07-29 10:25 PM CDT

The block stopped immediately after the demo failure. The three remaining authorized reads were not consumed:

3. Daily Plaid Sync workflow state;
4. newest scheduled Daily Plaid Sync run;
5. independent monitor currentness.

No request was retried. No browser fallback, authentication, log access, diagnosis, workflow or automation query, mutation, Plaid action, provider or database access, repair, restart, deployment, protected action, or successor work occurred.

## Limitations And Next Gate

The production result proves only that the minimal credential-free endpoint responded as expected at the observation time. The demo result proves only that the exact configured `/health` target returned 404 at the observation time. Neither result proves financial-data freshness, Plaid correctness, deployment correctness, or protected recovery readiness.

Task 1 remains current and decision-needed. The smallest next gate is a separately planned, read-only demo-health route and deployment-configuration diagnosis. It must not repeat the health request or authorize repair, restart, deployment, or protected access unless Ryan separately confirms those actions.

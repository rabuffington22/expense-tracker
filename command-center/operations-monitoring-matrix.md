# Operations Monitoring And Maintenance Matrix

Status: source-verified local contract from work block 5I with the local synthetic re-entry path verified through 5J, exact Phase 5 GitHub release evidence reconciled read-only through 5K, and maintained documentation reconciled through 5L

## Reading The Matrix

- **Source-verified** means current tracked source defines the behavior.
- **Historical evidence** means a dated sanitized closeout established the fact then, not now.
- **Externally unverified-current** means the mutable external surface was not queried in the stated evidence block.
- **Protected** means the observation requires credentials, real data, provider settings, or another closed surface.
- A signal or alert never authorizes remediation.

## Matrix

| Surface | Status basis | Owner | Signal | Cadence or threshold | Allowed observation in a suitable block | Evidence | Remediation gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Runway OS sources and generated dashboard | Source-verified local | Codex for active block; Ryan for scope | JSON validity, generated-state equality, health check, exactly one current task | After every meaningful state change | Local source inspection, `refresh-dashboard.js --check`, health check, generated marker review | [`operating-rules.md`](operating-rules.md), [`AGENTS.md`](../AGENTS.md) | Source corrections only inside the active block; no publication implied |
| Maintained operator documentation and release handoff | Documentation-reconciled through 5L | Codex maintains; Ryan owns scope and release decisions | Source links, configuration inventory, evidence labels, package/gate separation, Central Time label | After architecture, configuration, authority, evidence, or release-boundary changes | Local tracked-source and sanitized-evidence review only | [`operator-runbook.md`](operator-runbook.md), [`phase-5-release-handoff.md`](phase-5-release-handoff.md), [`README.md`](../README.md) | Documentation correction grants no provider, publication, workflow, merge, deployment, production, or parent authority |
| Local workflow safety contract | Locally verified through 5J | Codex | `scripts/ci_safety_check.py` fail/pass | Before workflow publication and during a confirmed drill | Standard-library local checker and tracked diff review | [`synthetic-ci-safety-contract.md`](synthetic-ci-safety-contract.md), [`fly-deploy-safety-contract.md`](fly-deploy-safety-contract.md), [5J evidence](logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md) | Any workflow/dependency correction requires a new exact block |
| Pull-request Synthetic CI | Trigger and authority source-verified; run state externally unverified-current | GitHub executes; Codex may observe when authorized | Core job, then browser job, annotations, exact head SHA | Automatic on PRs targeting `main` | Read-only GitHub metadata for the exact PR/ref | [workflow](../.github/workflows/synthetic-ci.yml) | Rerun, workflow edit, PR mutation, or publication requires separate authorization |
| Fly Deploy workflow | Trigger source-verified; deployment state externally unverified-current | GitHub/Fly execute; Ryan authorizes release | Exact source SHA, job conclusion, annotations, deployment status | Automatic on each push to `main`; manual dispatch also exists; 20-minute timeout | Read-only exact-run metadata and credential-free `/health` only when included | [workflow](../.github/workflows/fly-deploy.yml), [contract](fly-deploy-safety-contract.md) | Push/merge, dispatch, rerun, cancellation, Fly access, rollback, or repair requires a target-specific live block |
| Production `/health` | Endpoint source-verified; current service health externally unverified-current | Application/Fly; Codex may observe when authorized | HTTP status and minimal `{"status":"ok"}` body | No continuous repo-defined cadence found; normally post-deploy | Credential-free request only inside an external-read block | [`web/__init__.py`](../web/__init__.py), [`README.md`](../README.md) | Diagnosis, logs, restart, console, secrets, or deploy requires a live block |
| Demo application health | Config source-verified; current service health externally unverified-current | Application/Fly; Codex may observe when authorized | HTTP status | No continuous repo-defined cadence found | Credential-free request only inside an external-read block | [`fly.demo.toml`](../fly.demo.toml), [`README.md`](../README.md) | Demo deploy, seed, volume, console, secret, or restart requires an exact live block |
| Daily Plaid Sync schedule | Schedule source-verified; workflow/run currentness externally unverified-current | GitHub schedule; Ryan owns recovery | Workflow state, newest `schedule` run age/status/conclusion | `17 9 * * *` UTC; monitor thresholds below | Public/read-only GitHub metadata only inside an authorized observation | [workflow](../.github/workflows/daily-plaid-sync.yml) | Enable, disable, dispatch, rerun, or sync requires separate live authorization |
| Independent Daily Plaid Sync monitor | Historical evidence says configured active; current automation state externally unverified-current | Local Codex automation; Ryan receives alerts | `ALERT` for disabled, missing/stale, failed, or long-running scheduled run | Designed daily at 7:00 AM local; stale after 36 hours; incomplete after 3 hours | Automation definition/history or public metadata only in a monitor/currentness block | [`logs/2026-07-18-independent-daily-sync-monitor.md`](logs/2026-07-18-independent-daily-sync-monitor.md) | Alert grants no remediation; recovery is Ryan-confirmed |
| Plaid synchronization result boundary | Source-verified local; real sync state protected | Application | Bearer/config rejection, shared-lease contention, per-entity success/partial failure/failure | Per manual, scheduled, or focused-dashboard attempt | Synthetic mocked proof; no real bearer or provider call | [`web/routes/plaid.py`](../web/routes/plaid.py), [`core/sync_coordination.py`](../core/sync_coordination.py), [`plaid-sync-atomicity-contract.md`](plaid-sync-atomicity-contract.md) | Supplying bearer, invoking sync, provider diagnosis, or data repair requires a live/protected block |
| Local synthetic smoke | Locally verified through 5J | Codex | Exit status and sanitized synthetic diagnostics | Before/after product changes and in a confirmed drill | Temporary synthetic `DATA_DIR`, denied external seams, exact cleanup | [`scripts/smoke_test.py`](../scripts/smoke_test.py), [`README.md`](../README.md), [5J evidence](logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md) | Product repair or fixture expansion requires a confirmed implementation block |
| Isolated browser suite | Locally verified through 5J | Codex | Both auth modes, route/UI assertions, console/page errors, denied requests, cleanup | Before/after relevant UI changes and in a confirmed drill | Installed Chrome with temporary synthetic data and blocked non-localhost requests | [`scripts/mobile_drawer_browser_test.py`](../scripts/mobile_drawer_browser_test.py), [`synthetic-ci-safety-contract.md`](synthetic-ci-safety-contract.md), [5J evidence](logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md) | Browser/product repair, dependency change, or retained artifact requires a new block |
| Local database integrity, sidecars, migrations, and recovery | Boundary source-verified; actual files protected and unverified | Ryan authorizes; Codex executes only exact block | Owner/process state, WAL/SHM presence, hash/metadata, integrity, schema delta, cleanup | No routine backup/integrity cadence found | No observation in ordinary work; use exact originals or disposable copies only when confirmed | [`core/db.py`](../core/db.py), [5G recovery evidence](logs/2026-07-27-immediate-personal-bfm-snapshot-recovery-5g-rc.md) | Copy, restore, transfer, migration, application access, cleanup, or row inspection requires protected authorization |
| Demo seed utility | Source-verified destructive | Ryan authorizes exact target | Resolved `DATA_DIR`, target entities, pre/post state | Only for an explicitly approved demo/disposable reseed | Source review only by default; never probe with `--help` | [`scripts/seed_demo_data.py`](../scripts/seed_demo_data.py), [5G stop evidence](logs/2026-07-27-recurring-review-cancellation-clarity-5g-stop.md) | Every invocation requires a destructive-data block with exact path, backup/rollback, and verification |
| Ask Opus local privacy contract | Local source-verified; provider settings externally unverified-current and protected | Codex maintains local contract; Ryan owns provider gate | Exact page/context behavior, ZDR request shape, no server transcript | Local regression checks after relevant changes | Synthetic provider capture only | [`ask-opus-data-handling-contract.md`](ask-opus-data-handling-contract.md), [`README.md`](../README.md) | Provider-account access, real AI calls, publication, and production claims require separate authorization |
| Runtime and dependency pins | Source-verified; maintenance cadence undecided | Codex proposes; Ryan authorizes change | Python, action, Fly CLI, Chrome, and dependency contract drift | No standing review cadence found | Tracked source and local static checks | [`Dockerfile`](../Dockerfile), [Synthetic CI](../.github/workflows/synthetic-ci.yml), [Fly contract](fly-deploy-safety-contract.md) | Dependency, runner, action, or tool-version changes require a scoped maintenance block |
| Phase 5 durability and release evidence | Reconciled through 5K: PR #89 merged/deployed with historical health; PR #90 open/draft and exact-head CI-passing; later Ask/operator work local-only | Ryan owns release decisions; Codex reconciles | Exact local head, remote `main`, PR state, exact-SHA CI/deploy records, annotations, and unresolved gates | Task 3.4 complete; recheck only in a later authorized release/currentness block | Exact local and authorized read-only hosted evidence only | [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md), [5K evidence](logs/2026-07-27-phase-5-release-evidence-reconciliation-5k.md) | PR mutation, publication, provider access, merge, deploy, health observation, Task 3.5, or Task 4 requires its own gate |

## Coverage Decisions

### Controls that exist

- Runway OS has local generated-state and health enforcement after project-control changes.
- Synthetic CI has a locally enforced fail-closed workflow contract.
- Fly Deploy has a locally enforced workflow contract and an exact post-release observation pattern.
- Daily Plaid Sync has an independent alert-only monitor design for workflow inactivity and scheduled-run failure.
- Plaid entry points share one source-verified non-blocking lease and sanitized failure boundaries.
- Local smoke and browser suites use temporary synthetic data with explicit cleanup contracts.

### Local synthetic validation established by 5J

- The workflow safety checker passed the Synthetic CI and Fly Deploy contracts.
- The full smoke suite passed once with a temporary synthetic `DATA_DIR`, including its internally guarded disposable demo-seeder proof.
- The complete installed-Chrome suite passed once in both authentication modes with temporary synthetic entity data, ephemeral localhost, blocked non-localhost browser requests, console/page-error checks, and exact cleanup.
- No product, test, workflow, dependency, runtime, configuration, database, README, external, protected, publication, deployment, or production action was needed.

### Currentness boundaries after 5K

- 5K established only the exact Phase 5 GitHub refs, PRs, Synthetic CI, and Fly Deploy records listed in the release-evidence map;
- every other GitHub workflow currentness remains unqueried;
- current state or latest execution of the independent Codex monitor;
- current production or demo health;
- current Fly deployment or secret state;
- current OpenRouter logging/use settings;
- current local backup completeness, database integrity, or sidecar state;
- current production or demo runtime state does not follow from the exact GitHub release records.

### Documentation reconciliation established by 5L

- README now foregrounds the resolved `DATA_DIR` startup, initialization, sidecar, migration, and category-synchronization boundary.
- `.env.example` covers the maintained operator-configurable README inventory without real values.
- The sync-entry contract lifecycle label now matches durable 4L-4L-R evidence while preserving the historical reviewed body.
- The generated dashboard timestamp distinguishes winter `CST` from summer `CDT`.
- The compact release handoff separates released, hosted-only, local-only, externally unverified, protected, and pending packages and gates.

### Monitoring and maintenance gaps for later decisions

- No repo-defined continuous production or demo health monitor was found.
- No routine backup, integrity, restore-drill, or recovery-currency cadence was found.
- No standing cadence was found for dependency/runtime/action-pin review.
- OpenRouter account-setting verification has no local substitute and remains a protected pre-production gate.
- The independent daily-sync monitor's current automation state needs a separately scoped currentness check.
- Task 3.5 documentation and handoff are complete locally through 5L; Phase 5 release decisions still require the separately gated 5H-R/provider, 5G-R2, and Task 4 paths.

These gaps are planning inputs, not authorization to add automation or query the relevant systems.

# The Ledger Operator Runbook

Status: locally verified through work block 5J for the source-defined synthetic re-entry path, documentation-reconciled through 5L, aligned with the canonical Phase 6 Task 1 monitoring contract through 6A, Task 2 recovery-currency contract through 6B, accepted Task 3 maintenance-review contract through 6C-R, and Task 4 triage, retained-risk, and phase-exit governance through 6D; external, protected, publication, remediation, and production procedures remain unverified and separately gated

## Purpose And Authority

This runbook explains how to re-enter the repository, classify a requested action, select the safest verification path, stop on failure, and identify the next authorization gate. It does not authorize protected access, external currentness checks, remediation, publication, workflow action, deployment, synchronization, recovery, or production work.

Before acting, read these sources in order:

1. [`now.md`](now.md) for the active phase, task, work block, owner, blocker, and next action.
2. [`roadmap.md`](roadmap.md) for numbered task scope and confirmed work-block boundaries.
3. [`decisions.md`](decisions.md) and [`operating-rules.md`](operating-rules.md) for accepted direction and standing gates.
4. [`AGENTS.md`](../AGENTS.md) for repository-wide instructions.
5. [`README.md`](../README.md) for maintained architecture and setup.
6. [`categories.md`](../categories.md) when category-domain behavior is involved.
7. Tracked implementation and synthetic tests for behavior truth.

Roadmap placement is planning, not execution authority. A short confirmation activates only the exact documented block.

## Evidence Labels

Use these labels in status reports and handoffs:

- **Source-verified:** established by current tracked source or a maintained contract.
- **Locally verified:** exercised with synthetic temporary data inside the current block.
- **Durable:** present in an identified commit/ref. This does not imply hosted or production success.
- **Hosted-verified:** established by read-only hosted metadata for an exact ref inside an authorized block.
- **Production-verified:** established by the exact authorized production observation.
- **Externally unverified-current:** mutable external state was not queried in the current block.
- **Protected:** the observation requires credentials, real data, a provider account, or another closed surface.

Never promote one label into another by inference.

## Safe Re-entry Sequence

### 1. Establish control state

Read Runway OS before source exploration. Confirm that the current task, work block, owner, exclusions, stop conditions, and report point agree across human-readable sources and `state.json`.

For a read-only local check:

```bash
python3 -m json.tool command-center/state.json >/dev/null
node command-center/scripts/refresh-dashboard.js --check
node command-center/scripts/health-check.js
```

If project state changed, update human-readable sources first, align `state.json`, run the writing dashboard refresh, then run health and generated-state currentness checks. The generated [`index.html`](index.html) is a view, not source truth.

### 2. Preserve the worktree

Inspect before editing:

```bash
git status --short --branch
git diff --cached --name-only
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
```

Treat every existing modification and untracked file as user-owned unless the confirmed block names it. Stage exact paths only. Never absorb `scripts/sync_prod_to_local.sh`, duplicate command-center files, databases, uploads, backups, or ignored local data into another change.

### 3. Classify the requested action

Use the lowest applicable risk class:

| Class | Examples | Default |
| --- | --- | --- |
| Local read-only | tracked source inspection, JSON validation, diff/status inspection | allowed only inside the confirmed scope |
| Local synthetic | maintained smoke/browser checks using temporary databases | requires an execution block with cleanup checks |
| External read-only | GitHub metadata, credential-free health status | separately scoped because currentness and privacy can drift |
| Protected read | provider-account settings, real databases, authenticated pages, logs containing sensitive context | closed until target-specific confirmation |
| Live mutation | sync, deploy, workflow action, secrets, database transfer/recovery, downstream write | closed until target-specific confirmation |
| Publication | stage, commit, push, PR mutation, merge, parent pointer | closed until explicitly included |

When a task crosses classes, stop at the boundary and propose the next block.

## Local Development And Verification

The maintained local runtime uses Python 3.12 where possible. [`run.py`](../run.py) loads the project-root `.env` when present and otherwise leaves configuration to the process environment. The application defaults `DATA_DIR` to `./local_state`; application requests initialize the selected entity, open SQLite in WAL mode, apply pending additive migrations, and synchronize category metadata. Therefore:

- Do not start the application merely to inspect it when `DATA_DIR` could resolve to real local data.
- Do not open recovered originals through Flask unless a protected-copy block explicitly authorizes it.
- Use the maintained synthetic suites for ordinary behavior verification.
- A local server block must set a proven disposable `DATA_DIR`, synthetic secrets, denied external networking, and exact cleanup before startup.

Source-defined local checks:

```bash
.venv/bin/python scripts/ci_safety_check.py
.venv/bin/python scripts/smoke_test.py
.venv/bin/python scripts/mobile_drawer_browser_test.py
git diff --check
```

The smoke suite and isolated-browser suite are designed for temporary synthetic Personal, BFM, and Luxe Legacy data. Work block 5J ran the workflow safety checker, full smoke suite, and complete both-auth installed-browser suite once; all passed with the source-defined denied-network and exact-cleanup boundaries. See [`logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md`](logs/2026-07-27-local-synthetic-operator-reentry-drill-5j.md).

## Destructive Utility Boundary

[`scripts/seed_demo_data.py`](../scripts/seed_demo_data.py) is an executable reseed utility, not a normal CLI:

- it has no argument or help parser;
- import-time configuration defaults `DATA_DIR` to `./local_state`;
- any invocation reaching its main routine seeds Personal and BFM;
- it deletes existing transactions, account balances, recurring rows, categories, subcategories, planning items, budgets, actions, snapshots, and goals before replacement.

Do not invoke it with `--help`, guessed flags, or an unresolved `DATA_DIR`. Read the source to understand it. Execution requires an exact disposable/demo target, a separately confirmed destructive-data block, preflight path proof, backup/rollback terms, and postflight verification.

The same read-source-first rule applies to every seed, transfer, sync, backup, recovery, migration, and cleanup utility.

## GitHub And Synthetic CI

The tracked [Synthetic CI workflow](../.github/workflows/synthetic-ci.yml) runs only for pull requests targeting `main`, grants `contents: read`, persists no checkout credentials, and contains no secrets. Core runs before the isolated-browser job. The exact source contract is [`synthetic-ci-safety-contract.md`](synthetic-ci-safety-contract.md).

The local standard-library checker:

```bash
.venv/bin/python scripts/ci_safety_check.py
```

proves workflow structure only. It does not authorize a branch push, PR creation, workflow execution, rerun, hosted observation, merge, or deployment.

## Production Deployment

The tracked [Fly Deploy workflow](../.github/workflows/fly-deploy.yml):

- runs on every push to `main`;
- can also be manually dispatched;
- uses read-only repository permission and non-persistent checkout credentials;
- runs one `flyctl deploy --remote-only` command with the Fly token;
- has a 20-minute timeout.

The exact maintained contract is [`fly-deploy-safety-contract.md`](fly-deploy-safety-contract.md).

A feature-branch push or draft PR does not match the production trigger. A push or merge to `main` does. Any publication plan must therefore state whether it can trigger production before staging begins.

After an authorized exact-SHA deployment, a credential-free `/health` request may be used only when the block includes external reads. It establishes minimal application reachability, not authenticated workflow, database, Plaid, AI, or downstream correctness.

Do not run the illustrative deploy command in [`fly.demo.toml`](../fly.demo.toml) or any Fly CLI command without a target-specific live-action block.

## Plaid Synchronization

The tracked [Daily Plaid Sync workflow](../.github/workflows/daily-plaid-sync.yml) is scheduled at `17 9 * * *` UTC and also exposes manual dispatch. It sends a secret-bearing POST to `/plaid/sync-all`; invoking or dispatching it can write all configured entity databases.

The route:

- requires `SYNC_SECRET` bearer authentication before entity setup;
- fails closed when the secret or Plaid configuration is absent;
- uses a non-blocking shared file lease to prevent overlapping manual, scheduled, and focused-dashboard synchronization in the documented shared `DATA_DIR` domain;
- contains entity failures and returns failure status when errors remain.

Current implementation truth is in [`web/routes/plaid.py`](../web/routes/plaid.py), [`web/__init__.py`](../web/__init__.py), [`core/sync_coordination.py`](../core/sync_coordination.py), and the 4L evidence recorded in [`decisions.md`](decisions.md). The lifecycle label in [`sync-entry-coordination-contract.md`](sync-entry-coordination-contract.md) now accurately records its implemented, durable, deployed, and historically verified 4L-4L-R status; the reviewed contract body remains unchanged.

Never supply `SYNC_SECRET`, hit the endpoint, dispatch or rerun the workflow, enable/disable it, or invoke manual Plaid actions without a separately confirmed live block.

## Daily Sync Monitoring

The sanitized 1C evidence records an independent Codex automation named `expense-tracker-daily-plaid-sync-monitor`. Its designed cadence is daily at 7:00 AM local time and its alert conditions are:

1. workflow state is not `active`;
2. no scheduled run exists or the newest scheduled run is older than 36 hours;
3. the newest scheduled run completed with a non-success conclusion;
4. the newest scheduled run remains incomplete more than three hours after creation.

The monitor distinguishes `schedule` from `workflow_dispatch`, reads only public metadata, and never remediates. Its current external state is **externally unverified-current** in 5I. An alert authorizes no enable, dispatch, rerun, sync, or diagnosis beyond a newly confirmed block.

Source: [`logs/2026-07-18-independent-daily-sync-monitor.md`](logs/2026-07-18-independent-daily-sync-monitor.md).

## Operational Currentness Contract

The canonical surface-by-surface contract is [`operations-monitoring-matrix.md`](operations-monitoring-matrix.md). Work block 6A defines intended cadence, alert thresholds, required evidence, escalation state, and remediation gates without querying any mutable external or protected surface.

Use this sequence for every currentness request:

1. identify the exact matrix surface and its current evidence label;
2. determine whether the request is local, external read-only, protected, live mutation, or publication;
3. obtain a confirmed block when the matrix requires one;
4. record the exact target, Central Time, authorized query count, result, threshold comparison, limitations, and next gate;
5. set `decision-needed` for a failed or stale signal, `waiting-on-Ryan` for a protected next step, or `stopped` for scope or verification failure;
6. stop without diagnosis, retry, repair, dispatch, sync, deployment, database action, or other remediation unless a separate block authorizes it.

Task 1 establishes these defaults:

- production health is intended daily and after authorized deployment, stale after 36 hours;
- demo health is intended weekly and after authorized demo deployment, stale after eight days;
- Daily Plaid Sync retains its daily 7:00 AM local monitor design, 36-hour stale threshold, and three-hour incomplete threshold;
- the independent monitor itself is reviewed weekly, while its current state remains externally unverified;
- Synthetic CI, Fly Deploy, and release evidence are exact-ref and event-driven;
- protected provider settings are verified before a relevant privacy-sensitive production claim and after a known account-setting change.

## Backup, Integrity, And Recovery Currency

The canonical recovery policy is [`backup-integrity-recovery-currency-contract.md`](backup-integrity-recovery-currency-contract.md). It defines intended evidence and authorization gates; it does not prove a mechanism, inventory, recovery point, integrity pass, or restore capability currently exists.

Task 2 establishes these targets:

- treat Personal, BFM, and LL as one scheduled recovery set while preserving per-entity isolation and treating any partial result as a failed set;
- acquire one application-consistent recovery set daily and treat the newest passing set as stale after 36 hours;
- retain at least 14 daily, 8 weekly, and 12 monthly passing sets;
- verify integrity weekly on a separately authorized disposable copy and treat the evidence as stale after eight days;
- run one isolated disposable-`DATA_DIR` restore drill per calendar quarter, with no passing prior-quarter drill or a pass older than 100 days treated as stale;
- review recovery currency monthly, stale after 35 days, and after migrations, storage/topology or backup-method changes, incidents, or suspected loss/corruption;
- target a recovery point no older than 36 hours once a mechanism is implemented, while making no recovery-time promise until a drill measures it.

Before any protected recovery action:

1. name the exact environment, `DATA_DIR` boundary, entity set, source, destination, owner, and authority;
2. establish process ownership and WAL/SHM disposition;
3. use a reviewed SQLite-supported online backup method or a proven quiesced snapshot boundary—never presume a bare `.sqlite` copy is complete;
4. define destination protection, per-entity and whole-set success, retention tier, rollback, evidence, and cleanup;
5. stop without retry, repair, replacement, cleanup, or another recovery point if integrity, isolation, schema, external-request, output-sanitization, or cleanup verification fails.

Policy maintenance, protected metadata review, recovery-point acquisition, disposable integrity verification, isolated restore drill, live restoration, and retention cleanup are separate authorization rungs. A passing rung supplies evidence only and never activates its successor.

## Dependency, Runtime, Action-Pin, And Toolchain Review

The canonical maintenance policy is [`dependency-runtime-action-pin-toolchain-review-contract.md`](dependency-runtime-action-pin-toolchain-review-contract.md). Its tracked inventory and review gates were accepted locally through 6C-R after exact existing Python 3.14.3 discovery and one passing static checker invocation. It does not prove that a declared dependency, runtime, action, runner, image, browser, or deployment tool is currently latest, supported, secure, installed, or functioning in hosted or production state.

Task 3 establishes these targets:

- refresh the tracked-source inventory monthly and after relevant source changes, stale after 35 days;
- perform authoritative external-currentness review quarterly only through a separately confirmed read-only block, stale after 100 days;
- trigger focused review on credible security advisories, action-runtime deprecations, runner changes, runtime EOL notices, container/build or deployment-tool failures, and Chrome/Playwright incompatibility;
- classify each finding as security-critical, compatibility-risk, maintenance-available, or unknown-currentness;
- treat bounded ranges, transitive resolution, mutable image tags, `ubuntu-latest`, runner-installed Chrome, and environment-supplied pip/Node/curl as drift surfaces rather than automatic defects;
- keep Python requirements/lock strategy, runtime/container, workflow/action/runner, Fly deployment inputs, browser tooling, and implicit environment tools in separate future change families.

Use this sequence:

1. identify the exact tracked source paths and declared constraints;
2. label the evidence as source-verified, historical, externally unverified-current, or protected;
3. determine whether a monthly source review, quarterly external review, pre-change review, post-change reconciliation, or event-driven review is being requested;
4. obtain a separate block before any registry, advisory, runner, hosted, installed-environment, or production query;
5. record one primary classification, affected change family, limitations, and smallest next gate;
6. stop before package resolution, installation, update, workflow edit, publication, hosted run, deployment, or remediation.

The local static checker:

```bash
.venv/bin/python scripts/ci_safety_check.py
```

proves only that the tracked Synthetic CI and Fly Deploy workflows still match their maintained local safety contracts when that path exists. In 6C, the exact `.venv/bin/python` path was absent and the authorized invocation returned shell status 127 before the checker ran. Separately confirmed 6C-R resolved exact existing Python 3.14.3 and invoked the checker once; both contract messages passed. The machine-specific path is evidence only, not a repository runtime requirement. This pass does not establish current external versions or authorize any change, workflow action, publication, deployment, or production observation.

An intended cadence does not create an observer or authorize its use. When a window arrives without authority, record the surface as `due`; do not make a request merely to satisfy the cadence.

## Maintenance Triage And Retained Risk

The canonical governance policy is [`maintenance-triage-retained-risk-governance-contract.md`](maintenance-triage-retained-risk-governance-contract.md). Use it after a monitoring signal, recovery result, maintenance classification, issue change, incident, or parked-work promotion trigger.

1. Preserve the evidence label and identify the exact source, threshold, or trigger.
2. Record what is known, what remains unproven, severity, confidence, and affected boundary.
3. Assign one normalized state: `monitored`, `due`, `waiting-on-Ryan`, `decision-needed`, `planned`, `parked`, `stopped`, or `resolved`.
4. Name the owner and smallest next authorization gate.
5. Preserve existing controls, residual risk, review cadence or promotion trigger, and reopen conditions.
6. If action is selected, write a complete bounded work block and stop for confirmation.

Review the governance register monthly and treat it as stale after 35 days. Review sooner for credible alerts or incidents, security-critical or compatibility-risk evidence, recovery failure, known protected-setting change, maintenance-contract trigger, source-contract drift, or a parked promotion trigger.

Default routing:

- security-critical or compatibility-risk evidence → Ryan-owned `decision-needed`;
- unknown or stale evidence → `due` or `waiting-on-Ryan`;
- maintenance-available work → `planned`;
- optional product work or broad residual coverage → `parked`;
- failed bounded verification → `stopped`;
- complete acceptance evidence → `resolved`.

Monitoring never equals remediation. Do not query, diagnose, retry, repair, clean up, update, publish, deploy, transition the phase, or activate a successor merely because a signal exists.

## Phase 6 Exit And Transition

Phase 6 required completion depends on the four canonical contracts, reconciled issue accounting, preserved optional parked work, valid/current Runway OS, exact command-center-only scope, and zero staging. The complete checklist is in the 6D governance contract.

At a passing exit checkpoint:

1. report Phase 6 at 100% required completion;
2. keep Phase 6 active;
3. keep Task 4 current only for transition and next-objective accounting;
4. leave no active execution block;
5. preserve Phase 5 Tasks 2.2 and 2.7 as optional parked work;
6. create no Phase 7 or successor objective;
7. wait for Ryan to name the next objective before proposing a separate 6E transition block.

## Ask Opus

Ask Opus is optional. Current local source and [`ask-opus-data-handling-contract.md`](ask-opus-data-handling-contract.md) establish explicit submission, active-entity page summaries, no server transcript, Ask-specific zero-data-retention routing, and denial of data-collecting providers.

The repository cannot establish mutable OpenRouter account logging/use settings. Provider-account verification, real-provider calls, publication, and production use remain separate gates. Do not use real financial questions as a substitute for provider-setting proof.

## Recovery And Protected Local Data

Opening a database through the application can create directories, WAL/SHM files, migrate schema, seed defaults, and synchronize categories. Recovery therefore has separate stages:

1. freeze affected originals;
2. establish process-owner and sidecar state;
3. identify one exact source and target;
4. preserve a byte-identical safety copy;
5. verify integrity through an explicitly approved read-only method;
6. replace or test only inside the confirmed target boundary;
7. verify hashes, metadata, integrity, and cleanup;
8. re-enter the application only through disposable copies unless original access is explicitly authorized.

The 5G incident and recovery evidence show why these stages cannot be collapsed:

- [`logs/2026-07-27-recurring-review-cancellation-clarity-5g-stop.md`](logs/2026-07-27-recurring-review-cancellation-clarity-5g-stop.md)
- [`logs/2026-07-27-immediate-personal-bfm-snapshot-recovery-5g-rc.md`](logs/2026-07-27-immediate-personal-bfm-snapshot-recovery-5g-rc.md)
- [`logs/2026-07-27-human-verified-dashboard-reentry-5g-av-r.md`](logs/2026-07-27-human-verified-dashboard-reentry-5g-av-r.md)

These are evidence, not a reusable authorization. Never repeat their privileged, protected, or destructive actions without a new exact block.

## Failure And Escalation

Stop immediately when:

- a command acts differently from its source-reviewed shape;
- an unexpected database, sidecar, owner, process, external request, workflow, or changed file appears;
- verification needs credentials, protected content, live configuration, or row-level output;
- a branch, ref, PR, workflow, deployment, or production target differs from the confirmed baseline;
- cleanup, integrity, source-link, dashboard, health, whitespace, index, or preserved-file checks fail;
- remediation would widen the confirmed scope.

At a stop:

1. do not retry blindly;
2. preserve the exact state;
3. capture only sanitized project-control evidence;
4. state what did and did not happen;
5. identify the smallest next authorization gate.

## Documentation Corrections And Remaining Decisions

Work block 5L resolved the maintained-documentation gaps found by 5I:

- `sync-entry-coordination-contract.md` now records the verified 4L-4L-R lifecycle without rewriting the reviewed historical body;
- `README.md` prominently warns that ordinary startup can initialize or migrate the resolved local data root;
- `.env.example` covers every operator-configurable variable in the maintained README with placeholders only;
- the generated dashboard timestamp uses the correct Central Time abbreviation for standard or daylight time.

The following remain real protected-currentness or later-task boundaries:

- Task 1 now defines intended production and demo health cadences, but no continuous health monitor exists or is proven current;
- Task 2 now defines routine backup, integrity, restore-drill, and recovery-currency cadence, while every protected observation or action remains separately gated;
- Task 3 defines dependency, runtime, action-pin, runner, and toolchain review cadence through accepted 6C-R, while external currentness and every change family remain separately gated;
- Task 4 defines triage, retained-risk, escalation, and Phase 6 exit governance through 6D, while every observation, remediation, transition, Phase 7, and successor remains separately gated;
- the independent Daily Plaid Sync monitor's current automation state remains externally unverified;
- OpenRouter account logging/use settings remain protected and externally mutable;
- Phase 6 can report required completion without selecting the next objective; Ryan must name that objective before any 6E transition proposal.

Do not promote any mutable surface to current or act on a signal without the exact matrix gate and a separately confirmed block. The compact [`phase-5-release-handoff.md`](phase-5-release-handoff.md) remains historical orientation.

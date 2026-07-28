# Work Block 5I — Operator Re-entry And Monitoring Contract

Date: 2026-07-27

Status: complete locally after rendered closeout dashboard attestation

## Confirmed Scope

Tasks 3.1-3.2 (`P5-T31`-`P5-T32`) only. Inventory tracked operator paths and protected boundaries; draft a source-linked operator runbook and monitoring/maintenance matrix; distinguish source-verified, mutable externally unverified, protected, and separately authorized state; verify locally; close Runway OS; and stop.

Task 3.3-3.5, maintained README corrections, product/test/workflow/runtime/configuration changes, external-currentness checks, provider-account verification, protected data, operational command execution, publication, workflow action, merge, deployment, production, parent updates, delegation, and second opinion remained excluded.

## Baseline

- Branch: `codex/ask-opus-privacy`.
- Head: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- Git index: empty.
- PR #90 baseline: open, draft, clean, targeting `main`, head `codex/recurring-review-surface` at the same exact SHA.
- Existing local 5H changes and three unrelated untracked files were preserved.
- No source, test, workflow, README, configuration, database, ignored-data, or protected path was changed for 5I.

## Sources Reconciled

- project authority and gates: `AGENTS.md`, `command-center/now.md`, `roadmap.md`, `decisions.md`, `operating-rules.md`;
- maintained architecture and configuration: `README.md`, `categories.md`, `.env.example`, `run.py`, `Dockerfile`, `fly.toml`, `fly.demo.toml`;
- workflow contracts: all three tracked GitHub workflows, `synthetic-ci-safety-contract.md`, `fly-deploy-safety-contract.md`, and `scripts/ci_safety_check.py`;
- data and application-entry boundaries: `core/db.py`, `web/__init__.py`, `scripts/seed_demo_data.py`;
- synchronization boundaries: `web/routes/plaid.py`, `web/routes/kristine.py`, `core/sync_coordination.py`, and the maintained Plaid contracts;
- sanitized operations evidence: independent Daily Plaid Sync monitor, 4L synchronization release, 5G destructive-probe stop, snapshot recovery, protected-copy application verification, 5G-R/5H boundaries, and Phase 5 state.

No `.env`, real database, upload, backup contents, credential, provider account, workflow run, monitor execution, production/demo endpoint, Fly surface, Plaid surface, or other external system was accessed.

## Outputs

- `command-center/operator-runbook.md`
- `command-center/operations-monitoring-matrix.md`
- this sanitized evidence log

The runbook establishes a source-of-truth sequence, evidence labels, risk classes, safe re-entry, local verification boundaries, destructive-utility warning, CI/deploy/sync/AI/recovery guidance, and exact failure/escalation behavior.

The matrix records owner, signal, cadence/threshold, allowed observation, evidence, status basis, and remediation gate for Runway OS, local and hosted CI, Fly deployment, health, Daily Plaid Sync, its independent monitor, sync result truthfulness, synthetic tests, protected databases/recovery, demo seeding, Ask Opus, runtime maintenance, and Phase 5 release evidence.

## Findings

1. `run.py` loads `.env`, defaults to `./local_state`, and normal application access can initialize directories, create WAL/SHM state, migrate schema, and synchronize categories. The maintained README gives ordinary startup instructions but does not foreground that protected-data consequence.
2. `scripts/seed_demo_data.py` has no help parser. Any invocation reaching main—including `--help`—uses the resolved `DATA_DIR`, deletes broad Personal/BFM state, and reseeds both entities. Source inspection, not exploratory execution, is the only safe default.
3. `sync-entry-coordination-contract.md` retains a stale “proposed” header although current source, decisions, and durable 4L-R evidence show the shared lease and repaired boundaries were implemented and released.
4. The only explicit independent recurring monitor found is the alert-only Daily Plaid Sync monitor. Its historical definition is precise, but its mutable current automation state was intentionally not queried.
5. No repo-defined continuous production/demo health monitor, routine backup/integrity/restore cadence, or standing dependency/runtime-pin review cadence was found.
6. OpenRouter account logging/use settings remain externally mutable and protected; local ZDR request enforcement cannot prove those settings.
7. The command-center timestamp formatter appends `CST` throughout the year. During daylight time that label is not reliable evidence of the actual UTC offset.
8. `.env.example` does not enumerate every maintained configuration name documented in `README.md`.

None of these findings required a product decision or protected/live check to complete the 5I contract. Corrections remain deferred to Task 3.5; runtime validation remains Task 3.3; release-evidence currentness remains Task 3.4.

## Verification Plan

- validate that every runbook and matrix link resolves to a tracked or intended sanitized 5I path;
- verify required runbook and matrix fields and absence of unsupported currentness claims;
- validate JSON;
- refresh and currentness-check the generated dashboard;
- run command-center health and whitespace checks;
- scan intended 5I additions for high-confidence secret patterns and protected-value leakage;
- prove exact changed paths, empty index, preserved hashes, branch/head, and unchanged PR #90;
- if the local `file:` dashboard remains blocked from Codex browser reload, write the sanitized closeout and wait for Ryan's exact `5I dashboard verified` attestation.

## Boundary

5I does not execute the documented procedures. It authorizes no synthetic drill, external currentness check, protected observation, remediation, publication, workflow action, sync, recovery, merge, deploy, or production action.

## Verification Result

- Every local Markdown link in the runbook, matrix, and evidence log resolves.
- The matrix contains owner, signal, cadence/threshold, allowed observation, evidence, status basis, and remediation gate fields.
- Review of every currentness term found no mutable external surface presented as verified-current.
- High-confidence secret-pattern and new-artifact protected-value scans returned no findings.
- JSON validation, dashboard refresh, health, generated-state currentness, and repository-wide whitespace checks passed.
- The Git index remained empty.
- The three preserved unrelated files retained their accepted hashes.
- Branch `codex/ask-opus-privacy` and head `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a` remained unchanged.
- PR #90 remained open, draft, clean, targeting `main`, with head `codex/recurring-review-surface` at the exact baseline SHA.
- No source, test, README, workflow, configuration, database, ignored-data, provider, monitor, production, publication, or protected action occurred.

The in-app browser policy blocked Codex from reloading the local `file:` dashboard. Ryan returned the exact `5I dashboard verified` attestation after inspecting the sanitized rendered closeout state. Tasks 3.1-3.2 and 5I are therefore complete locally. The attestation closes only the rendered-dashboard checkpoint; it does not authorize Task 3.3 or another sequel.

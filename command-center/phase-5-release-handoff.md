# Phase 5 Operator And Release Handoff

Date: 2026-07-27

Status: updated through the clean 5H-R candidate; exact closeout-head hosted verification remains pending while provider verification, Ask release, and final parent durability stay separate

## Re-entry

1. Read [`now.md`](now.md), [`roadmap.md`](roadmap.md), [`decisions.md`](decisions.md), and [`operating-rules.md`](operating-rules.md).
2. Follow the authority, worktree-preservation, risk-classification, synthetic-verification, failure, and recovery sequence in [`operator-runbook.md`](operator-runbook.md).
3. Use [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md) for exact release labels and the dated GitHub evidence established by 5K.
4. Treat this handoff as orientation only. It authorizes no provider, publication, workflow, merge, deployment, production, database, protected-data, or parent action.

## Current Package Map

| Package | Exact status | Evidence | Next gate |
| --- | --- | --- | --- |
| First Phase 5 usability set: 5A, 5B, 5C, 5E, 5F, and 5F-W | Merged through PR #89, deployed by exact merge-SHA workflow, and historically health-verified on 2026-07-27 | [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md), [5F-R2 evidence](logs/2026-07-27-verified-draft-pr-production-release-5f-r2.md) | No release action for this package; current runtime health still requires a separately authorized observation |
| Recurring Review: 5G, 5G-RS, 5G-R, and 5G-R2 | Merged through PR #90 as `d81ed7078e741a0c7613e7898312ce01cd359f45`, automatically deployed once, and health-verified on 2026-07-27 | [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md), [5G-R2 evidence](logs/2026-07-27-recurring-review-production-release-5g-r2.md) | No further release action for this package; proceed only to a separately confirmed Ask durability block |
| Ask Opus privacy implementation: 5H-A and 5H-B | Candidate-durable and hosted-verified on draft PR #91 at `f7482a95e754160905a79ec0130ef8faf0a48784`; provider settings are not established | [`ask-opus-data-handling-contract.md`](ask-opus-data-handling-contract.md), [5H-B evidence](logs/2026-07-27-ask-opus-privacy-contract-implementation-5h-b.md) | Complete the exact 5H-R closeout-head gate, then separately authorize protected provider verification |
| Operator and release artifacts: 5I, 5J, 5K, and 5L | Candidate-durable and hosted-verified on draft PR #91; not merged or deployed | [`operator-runbook.md`](operator-runbook.md), [`operations-monitoring-matrix.md`](operations-monitoring-matrix.md), [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md) | Complete the exact closeout-head hosted gate; no release authority follows |
| Recovery records: 5G-RC through 5G-RC-R | Sanitized recovery record is durable on current `main`; protected observations remain historical and target-specific | [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md) | No reuse authority; any database inspection, recovery, or application re-entry needs a new exact protected block |

## Recommended Release Sequence

The lowest-ambiguity sequence is:

1. Recurring Review release is complete through 5G-R2;
2. complete the exact 5H-R closeout-head hosted gate for draft PR #91;
3. verify the mutable OpenRouter account controls at a separate protected human handoff;
4. authorize Ask Opus merge, deployment, and production observation only after both durability and provider gates are satisfied;
5. perform final Task 4 target and parent durability closeout last.

This is a recommendation, not release authority. A later block must recheck every mutable hosted fact.

## Maintained Operator Guidance

- Ordinary `python run.py` startup can use `./local_state` when `DATA_DIR` is unset and can initialize databases, create WAL/SHM sidecars, apply migrations, and synchronize categories. Use the maintained synthetic suites for ordinary verification.
- `scripts/seed_demo_data.py` is destructive on its resolved target and has no safe help probe. Read source by default.
- `.env.example` contains placeholders only. Never put real values in tracked files, documentation, logs, PR text, or handoffs.
- Feature-branch pushes and draft PRs do not trigger Fly Deploy. A push or merge to `main` does.
- A successful workflow, deployment, or dated health observation does not establish current provider, database, authenticated workflow, or runtime state.

Sources: [`README.md`](../README.md), [`AGENTS.md`](../AGENTS.md), and [`operator-runbook.md`](operator-runbook.md).

## Monitoring And Maintenance Decisions

The repository does not currently define:

- continuous production or demo health monitoring;
- routine backup, integrity, restore-drill, or recovery-currency cadence;
- standing dependency, runtime, GitHub Action pin, or toolchain review cadence.

The independent Daily Plaid Sync monitor has a historical alert-only contract, but its mutable current automation state was not queried. OpenRouter account settings remain protected and externally mutable. These are explicit later decisions, not implied defects and not authority to create automation.

See [`operations-monitoring-matrix.md`](operations-monitoring-matrix.md).

## Exact Remaining Gates

| Gate | Required before action |
| --- | --- |
| 5G-R2 Recurring Review release | Complete; exact merge, automatic deploy, health, and preservation evidence recorded |
| 5H-R Ask Opus durability | Candidate complete on draft PR #91; exact closeout-head automatic CI and zero-deployment proof remain |
| OpenRouter provider verification | Ryan-completed protected account-setting observation without sharing credentials, secrets, or financial questions |
| Ask Opus production release | Durable Ask package, provider-setting evidence, exact merge/deploy authority, and separately authorized production observation |
| Current production or demo health | Separately authorized credential-free observation tied to a named target and purpose |
| Parked Tasks 2.2, 2.7, and 2.8 | Explicit reopening and a new bounded proposal |
| Task 4 target and parent closeout | Final target-repo package and release state plus separately scoped parent pointer |

## Handoff Boundary

Task 3.5 is complete locally through verified 5L. The handoff makes the remaining choices explicit; it does not resolve them. Current Git and hosted state override this dated document whenever a later authorized block begins.

# Phase 5 Operator And Release Handoff

Date: 2026-07-28

Status: updated through the final 5M target-and-parent durability package; the Ask and operator package is released and historically health-verified, Ryan's dated attestation established Broadcast disabled immediately and after one reload, and the parent pointer is durable at `391debe28ea58349c65312eeb0987e9b516babd9`

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
| Ask Opus privacy implementation: 5H-A and 5H-B | Released on exact application head `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`; automatic Fly run `30350587286` passed with zero annotations; one dated HTTP 200 `status: ok` health result; Ryan's 5H-BR2 attestation established Broadcast disabled immediately and after one reload | [`ask-opus-data-handling-contract.md`](ask-opus-data-handling-contract.md), [5H-R evidence](logs/2026-07-27-ask-operator-package-durability-5h-r.md), [5H-PV evidence](logs/2026-07-28-openrouter-account-privacy-verification-5h-pv.md), [5H-BV evidence](logs/2026-07-28-openrouter-broadcast-boundary-evidence-5h-bv.md), [5H-BR evidence](logs/2026-07-28-openrouter-broadcast-disablement-5h-br.md), [5H-BR2 evidence](logs/2026-07-28-openrouter-broadcast-human-attestation-5h-br2.md), [5H-R2 evidence](logs/2026-07-28-ask-exact-main-deployment-observation-5h-r2.md) | No further Task 4.3 or 4.4 action; Task 4.5 is closed by 5M |
| Operator and release artifacts: 5I, 5J, 5K, and 5L | Included in exact application release `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`, automatically deployed and historically health-verified through 5H-R2 | [`operator-runbook.md`](operator-runbook.md), [`operations-monitoring-matrix.md`](operations-monitoring-matrix.md), [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md) | No further Task 4.4 or Task 4.5 durability action |
| Final target and parent durability: 5M | Parent pointer and reusable lesson are durable at `391debe28ea58349c65312eeb0987e9b516babd9`; the exact twelve-path target closeout is carried by the containing `[skip actions]` commit | [5M evidence](logs/2026-07-28-phase-5-target-parent-durability-closeout-5m.md), [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md) | Phase 5 stays active at 75%; Task 2 returns as the sole planning task and optional parked work remains separate |
| Recovery records: 5G-RC through 5G-RC-R | Sanitized recovery record is durable on current `main`; protected observations remain historical and target-specific | [`phase-5-release-evidence-map.md`](phase-5-release-evidence-map.md) | No reuse authority; any database inspection, recovery, or application re-entry needs a new exact protected block |

## Recommended Release Sequence

The lowest-ambiguity sequence is:

1. Recurring Review release is complete through 5G-R2;
2. 5H-R durability is complete and the package was released through exact-main 5H-R2 after Ryan's explicit override;
3. treat Task 4.3 as complete through Ryan's value-free 5H-BR2 Broadcast disablement and one-reload persistence attestation;
4. perform final Task 4 target and parent durability closeout last.

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

The independent Daily Plaid Sync monitor has a historical alert-only contract, but its mutable current automation state was not queried. OpenRouter account settings remain protected and externally mutable; 5H-PV established the named logging/use states, 5H-BV established Broadcast enabled with one configured destination marker, 5H-BR stopped before mutation after excluded destination-specific details appeared in the ordinary page representation, and Ryan's later value-free 5H-BR2 attestation established Broadcast disabled immediately and after one reload. No destination-specific detail is retained. These dated results are explicit later decisions and not authority to create automation, recheck provider state, or change another provider setting.

See [`operations-monitoring-matrix.md`](operations-monitoring-matrix.md).

## Exact Remaining Gates

| Gate | Required before action |
| --- | --- |
| 5G-R2 Recurring Review release | Complete; exact merge, automatic deploy, health, and preservation evidence recorded |
| 5H-R Ask Opus durability | Complete through candidate and closeout CI; the package later entered exact `main` through the separately authorized direct push |
| OpenRouter provider verification | Complete through 5H-BR2; Ryan attested Broadcast disabled immediately and after one reload, with no destination-specific detail retained |
| Ask Opus production release | Complete through 5H-R2 exact-main deployment and dated minimal health observation; Broadcast risk remains separate |
| Current production or demo health | Production was historically verified by the one 5H-R2 request; any later currentness claim requires a new exact observation |
| Parked Tasks 2.2, 2.7, and 2.8 | Explicit reopening and a new bounded proposal |
| Task 4 target and parent closeout | Final target-repo package and release state plus separately scoped parent pointer |

## Handoff Boundary

Task 3.5 and Tasks 4.1-4.5 are complete through the exact 5H-R2 release evidence, Ryan's value-free 5H-BR2 Broadcast disablement and one-reload persistence attestation, the parent durability commit `391debe28ea58349c65312eeb0987e9b516babd9`, and the containing target 5M `[skip actions]` closeout. Phase 5 remains active at 75%; Task 2 is the sole current planning task and Tasks 2.2, 2.7, and 2.8 remain parked. No successor work block is active. This handoff authorizes no sequel; current Git and hosted state override this dated document whenever a later authorized block begins.

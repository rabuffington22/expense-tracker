# Maintenance Triage, Escalation, Retained-Risk, And Phase-Exit Contract

Status: canonical Phase 6 Task 4 governance contract accepted locally through work block 6D; no repair, remediation, external or protected observation, publication, live action, Phase 7, or successor objective is authorized

## Purpose

This contract turns evidence from the Phase 6 monitoring, recovery, and maintenance-review contracts into consistent command-center states and explicit next gates. It governs triage and retained-risk records; it does not establish mutable currentness, choose remediation, or authorize action.

Canonical inputs:

- [`operations-monitoring-matrix.md`](operations-monitoring-matrix.md) for monitored surfaces, evidence labels, cadences, thresholds, and action gates;
- [`backup-integrity-recovery-currency-contract.md`](backup-integrity-recovery-currency-contract.md) for protected recovery signals and authorization rungs;
- [`dependency-runtime-action-pin-toolchain-review-contract.md`](dependency-runtime-action-pin-toolchain-review-contract.md) for maintenance classifications and change families;
- [`issues.md`](issues.md) for defects, monitored risks, and parked residual coverage;
- [`now.md`](now.md), [`roadmap.md`](roadmap.md), [`decisions.md`](decisions.md), and `state.json` for current authority and task accounting;
- dated sanitized command-center logs for incidents, observations, stops, and completed evidence.

No issue, alert, cadence, roadmap entry, or previous passing result activates its next action.

## Evidence-First Intake

Every intake record must state:

1. the exact surface, issue, or task;
2. the evidence label: source-verified, locally verified, historical, externally unverified-current, or protected;
3. the dated evidence source and Central Time when time matters;
4. the observed result or exact missing evidence;
5. the applicable threshold, trigger, or acceptance boundary;
6. severity and confidence without unsupported currentness inference;
7. the normalized workflow state;
8. the owner and smallest next authorization gate;
9. what the evidence does not prove;
10. confirmation that no remediation followed unless a separate block authorized it.

An alert without enough sanitized evidence is `due`, `waiting-on-Ryan`, or `stopped`; it is never silently promoted to a current failure claim.

## Normalized Workflow States

| State | Meaning | Required owner or gate |
| --- | --- | --- |
| `monitored` | A known risk remains possible and a defined signal or promotion trigger exists. Monitoring is evidence collection, not remediation. | Codex may maintain local policy; Ryan owns recovery or change decisions. |
| `due` | A policy review or observation window has arrived without passing current evidence or authority to observe. | Propose the smallest read-only or local review block; do not make the observation automatically. |
| `waiting-on-Ryan` | The next evidence or action is protected, destructive, live, externally mutable, or otherwise requires Ryan. | Ryan supplies the decision or exact authorization. |
| `decision-needed` | Credible evidence identifies security-critical risk, compatibility risk, failed/stale evidence requiring disposition, or a material product/priority choice. | Ryan decides whether to accept, investigate, park, plan, or authorize a bounded action. |
| `planned` | A bounded response is selected but not yet confirmed for execution. | A complete work-block proposal and Ryan confirmation are required. |
| `parked` | Valid optional, broad, or lower-priority residual work is intentionally deferred without blocking required completion. | Preserve visible scope and a promotion trigger; reopening requires a fresh decision. |
| `stopped` | The active block hit a defined scope, safety, preservation, or verification stop. | Preserve evidence and propose only the smallest recovery gate. |
| `resolved` | Acceptance evidence passed for the defined scope and the current disposition is complete. | Reopen only on failed maintained evidence, contradictory current evidence, or changed requirements. |

Exactly one current task remains visible in Runway OS. A `current` task may be an execution task, planning gate, or transition-accounting gate; its description must say which.

## Severity And Priority

- **Critical:** credible credential exposure, destructive protected-data risk, public sensitive-data exposure, or active entity-isolation breach. Stop and route to Ryan immediately; do not diagnose beyond the confirmed evidence boundary.
- **High:** credible data-integrity, privacy, security, production-availability, recovery, or recurring operational-reliability risk with material impact. Use `decision-needed` unless a defined alert-only monitor owns recurrence detection.
- **Medium:** meaningful correctness, maintainability, operator, or regression-confidence risk without evidence of immediate material harm. Use `planned`, `parked`, `due`, or `decision-needed` according to evidence and priority.
- **Low:** limited clarity, convenience, or narrow reliability risk. Usually `parked` unless paired with an authorized nearby change.

Severity describes impact, not urgency by itself. Evidence age, confidence, exploitability, affected entities, recovery options, and current safeguards determine priority.

## Classification To State Mapping

| Intake classification | Default state | Escalation |
| --- | --- | --- |
| Security-critical | `decision-needed` | Ryan; stop before query, change, publication, or remediation |
| Compatibility-risk | `decision-needed` | Ryan; define one focused review or change family |
| Maintenance-available | `planned` | Propose one bounded change block; no automatic update |
| Unknown-currentness | `due` when a read-only review is appropriate; otherwise `waiting-on-Ryan` | Preserve the externally unverified-current or protected label |
| Credible alert or incident | `decision-needed`, or `waiting-on-Ryan` if protected evidence is required | Record the exact signal and smallest next gate |
| Optional product task or broad residual coverage | `parked` | Retain a promotion trigger and exclude it from required phase math |
| Failed active-block verification | `stopped` | No blind retry, repair, or fallback |
| Passing acceptance evidence | `resolved` | Record the scope, limitations, and reopen trigger |

## Review Cadence And Triggers

Review the governance register monthly; it becomes stale after 35 days. Review sooner when any of these occurs:

- a credible alert, incident, or maintained-check failure;
- security-critical or compatibility-risk evidence;
- a recovery acquisition, integrity, restore-drill, cleanup, or live-restoration failure;
- a migration, storage/topology change, backup-method change, suspected loss, or corruption;
- a known protected-provider setting change;
- a runtime EOL notice, action deprecation, runner change, build/deployment failure, or Chrome/Playwright incompatibility;
- source changes that invalidate a contract, issue disposition, owner, cadence, threshold, or authorization gate;
- a parked item's explicit promotion trigger.

The review may reconcile local records. It does not authorize the observation that would supply missing external or protected evidence.

## Retained-Risk Record Minimum

Every `monitored` or `parked` item must retain:

1. stable title and source;
2. current status, severity, confidence, and evidence label;
3. affected boundary and possible impact;
4. existing control or passing partial evidence;
5. exact residual risk;
6. owner;
7. review cadence or promotion trigger;
8. smallest next gate;
9. why the item does not block required completion;
10. reopen or expiry conditions.

Retained risk is explicit acceptance of a visible residual boundary, not a claim that the boundary is safe or current. A record expires into `due` when its review window passes; it becomes `decision-needed` when its promotion trigger fires.

## Current Retained-Risk Register

| Item | State and severity | Existing control | Residual risk | Promotion trigger |
| --- | --- | --- | --- | --- |
| Daily Plaid Sync disabled for inactivity | `monitored`; high operational reliability | Independent alert-only monitor was created historically; workflow recovery remains Ryan-gated | GitHub inactivity behavior can recur, and current monitor state is externally unverified | Defined monitor failure, authorized stale/currentness evidence, or a material platform-control change |
| Planning foundations broad lifecycle and snapshot coverage | `parked`; medium regression confidence | Maintained boundary and repaired-defect coverage exists; work block 5C added deterministic synthetic Personal goals and exact domain fidelity | Demo snapshots and broad planning lifecycle/calculation coverage remain | A related planning change, failing maintained evidence, or Ryan priority |
| Import and categorization broad parser/operator coverage | `parked`; medium regression confidence | Selected repaired import and categorization paths have maintained synthetic coverage | Residual CSV/PDF parser, matching, alias, and operator paths remain broad | A related repair/change, failing maintained evidence, or Ryan priority |
| Primary Plaid broad connection/operator coverage | `parked`; medium regression confidence | Selected repaired Plaid defect clusters have maintained mocked all-entity coverage | Broader connection and operator paths remain | A related Plaid repair/change, failing maintained evidence, or Ryan priority |

Ledger accounting after 6D reconciliation is exactly 55 resolved, one monitored high, and three parked medium.

Phase 5 Tasks 2.2 (`P5-T22`) and 2.7 (`P5-T27`) remain optional parked product tasks. They are visible historical scope, excluded from Phase 5 and Phase 6 required-completion math, and may reopen only through a fresh Ryan decision and bounded proposal.

## Triage Sequence

1. Identify the exact intake source and preserve its evidence label.
2. Compare the evidence with the relevant threshold, acceptance check, or promotion trigger.
3. Assign one primary severity and one normalized state.
4. Name the owner and smallest next gate.
5. Update the issue, decision, task, or dated log without duplicating protected details.
6. If action is selected, write a complete bounded work-block proposal.
7. Stop until that block is confirmed.
8. After execution, verify the result and update retained-risk or resolved disposition without activating a sequel.

## No-Auto-Remediation Boundary

No cadence, alert, monitor, issue, classification, stale record, or failed check authorizes:

- diagnosis that requires a broader query;
- retry, repair, cleanup, rollback, or data action;
- dependency, runtime, workflow, action-pin, runner, browser, or tool update;
- provider, Plaid, database, backup, restore, Fly, GitHub, automation, or production action;
- commit, push, pull request, merge, publication, deployment, or Phase transition.

Each requires a target-specific confirmed block. A permitted fallback must be written into that block; 6D has no UI fallback.

## Phase 6 Exit Evidence

Phase 6 required work is complete only when all of these are true:

1. Task 1: the canonical operations matrix states owner, signal, cadence, threshold, evidence, escalation, and remediation gate for every governed surface.
2. Task 2: the recovery contract states protected-data-safe acquisition, currency, retention, integrity, restore-drill, review, evidence, cleanup, and authorization boundaries without claiming unobserved current capability.
3. Task 3: the maintenance contract inventories tracked runtime, dependency, workflow, action, runner, deployment, and browser-tool surfaces with cadence, classification, and separate change gates.
4. Task 4: this governance contract maps intake to evidence, severity, state, owner, review, retained risk, escalation, and separate action gates.
5. The issue ledger reconciles to 55 resolved, one monitored high, and three parked medium.
6. Phase 5 Tasks 2.2 and 2.7 remain optional parked work and do not reduce required completion.
7. Runway OS has valid JSON, exactly one current task, current generated state, passing health and whitespace checks, resolved local links, sanitized evidence, command-center-only 6D changes, and zero staging.
8. No mutable external or protected surface was promoted to current, and no repair, remediation, publication, live action, Phase 7, or successor objective was activated.

When these checks pass, Phase 6 reports 100% required completion but remains active. Task 4 remains current solely for transition and next-objective accounting; its governance work is done and there is no active execution block. Ryan must name the next objective before a separate `6E — Phase 6 Transition And Next-Objective Intake` can be proposed.

## 6D Verification Boundary

Work block 6D verifies command-center consistency only:

- local source links and required contract markers;
- exact issue counts and dispositions;
- valid JSON and exactly one current task;
- dashboard refresh, generated currentness, and command-center health;
- `git diff --check`;
- command-center-only changes, unchanged protected/product inputs, and zero staging.

Product smoke, browser checks, external currentness, provider settings, hosted metadata, production health, protected storage, and every remediation path are intentionally skipped.

# Work Block 6A — Operational Monitoring And Currentness Contract

Date: 2026-07-29

Status: done locally and verified

## Confirmed Scope

Task 1 (`P6-T1`) only. Finalize the existing operations monitoring matrix as the canonical contract for Runway OS, production and demo health, Daily Plaid Sync, the independent sync monitor, Synthetic CI, Fly Deploy, and protected provider-setting currentness; define owners, evidence labels, cadences, thresholds, escalation states, and explicit no-remediation boundaries; align the operator runbook; verify the local command-center package; and close Task 1.

Tasks 2-4 (`P6-T2`-`P6-T4`); production or demo requests; GitHub, workflow, or automation currentness checks; provider or database access; Plaid activity; monitor or automation creation or mutation; product, test, workflow, dependency, configuration, authentication, or database changes; staging, commit, push, PR, merge, deployment, delegation, second opinion, parent update, and unrelated work remain excluded.

## Confirmed Defaults

- Use Central Time for cadence reporting.
- Preserve source-verified, historical, externally unverified-current, and protected evidence labels.
- Runway OS currentness follows every meaningful state change.
- Intended production health is daily and after authorized deployment, stale after 36 hours.
- Intended demo health is weekly and after authorized demo deployment, stale after eight days.
- Daily Plaid Sync retains the daily 7:00 AM local monitor design, 36-hour stale threshold, and three-hour incomplete threshold.
- Independent-monitor currentness is reviewed weekly.
- Synthetic CI and Fly Deploy observations are exact-ref and event-driven.
- Protected provider settings are checked only before a relevant production claim or after a known account-setting change.
- Every alert supplies evidence and escalation only; no alert authorizes remediation.
- Keep the result local, unstaged, uncommitted, and unpublished.
- Skip product smoke and browser suites because no product behavior changes.

## Stop Conditions

Stop if a material policy choice is not covered by the confirmed defaults; local sources contradict a proposed surface or signal; current external or protected state becomes necessary; implementation or monitor creation becomes necessary; scope expands into Tasks 2-4; an existing user change cannot be preserved; or JSON, links, dashboard currentness, health, whitespace, task accounting, exact scope, or zero staging fails.

No external or protected observation has occurred. No implementation, monitor, automation, remediation, Git, publication, deployment, delegation, or second-opinion action has occurred.

## Contract Result

The existing operations matrix is now the canonical Task 1 currentness contract. It establishes:

- Runway OS verification after every meaningful state change;
- intended daily production health and a 36-hour stale threshold;
- intended weekly demo health and an eight-day stale threshold;
- the existing Daily Plaid Sync daily 7:00 AM local monitor design, 36-hour stale threshold, and three-hour incomplete threshold;
- weekly currentness review of the independent monitor itself;
- exact-ref, event-driven Synthetic CI, Fly Deploy, and release evidence;
- protected, claim-specific provider-setting verification;
- a minimum evidence record with target, Central Time, authorized query count, result, threshold comparison, limitations, escalation, and next gate;
- `due`, `decision-needed`, `waiting-on-Ryan`, and `stopped` states that never authorize remediation.

The operator runbook now carries the matching request-classification, evidence, escalation, and stop sequence.

## Verification

- Every local Markdown link in the matrix, runbook, and 6A log resolves.
- The canonical matrix contains owner, signal, intended cadence, alert threshold, allowed observation, required evidence, escalation state, and remediation gate.
- All required Task 1 surfaces are present.
- Review found no mutable external or protected surface presented as verified-current.
- The first broad secret-pattern expression matched the ordinary phrase `Ask-specific`; inspection proved it was not a credential. A corrected boundary-aware detector passed with no secret token or private-key marker.
- `command-center/state.json` is valid JSON.
- Dashboard refresh, generated-state currentness, and command-center health passed.
- `git diff --check`, exact command-center-only scope, and zero staging passed.
- Product smoke and browser suites were skipped as out of scope because no product behavior changed.

## Closeout

Work block 6A and Task 1 are done locally. Phase 6 is 25% complete. Task 2 (`P6-T2`) is current solely as the separate 6B planning gate; Tasks 3-4 remain planned.

No production or demo request, GitHub or automation currentness query, provider or database access, Plaid activity, monitor or automation change, product/test/workflow/dependency/configuration/authentication/database change, remediation, staging, commit, push, PR, merge, deployment, delegation, second opinion, parent update, or unrelated action occurred.

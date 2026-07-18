# Issues

These are known defects, risks, or rough edges. They are not active work unless promoted into a phase task and confirmed work block.

## Daily Plaid Sync Disabled For Inactivity

Status: monitored; work block 1C complete

Severity: high operational reliability

Captured: 2026-07-17

Where seen: GitHub Actions workflow metadata and run history

Revisit: Phase 1, Task 4 for recurrence prevention or detection

Summary:

The `Daily Plaid Sync` workflow was found `disabled_inactivity` after its last listed successful scheduled run on 2026-07-15. Work block 1A re-enabled it and verified controlled run `29627530457` successfully.

Impact:

Immediate sync scheduling is restored. Work block 1B found that the public repository's more-than-60-day commit gap closely matches GitHub's documented automatic-disable rule. Work block 1C added independent alert-only monitoring for disabled state, missing scheduled runs, unsuccessful runs, and runs incomplete beyond the delay window.

Why not fully closed:

The underlying GitHub inactivity behavior still exists, but active automation `expense-tracker-daily-plaid-sync-monitor` now detects recurrence without enabling or dispatching the workflow. Recovery remains Ryan-gated.

Promotion trigger:

The monitor reports a defined failure condition or Task 6 reveals a better control.

## Daily Plaid Sync Runs At The Start Of The Hour

Status: resolved

Severity: low operational reliability

Captured: 2026-07-18

Where seen: `.github/workflows/daily-plaid-sync.yml`

Revisit: Phase 1, Task 6

Resolution:

Work block 1D changed the workflow to `17 9 * * *` through ready PR `#83`, preserving the existing UTC hour and `workflow_dispatch`. Merge commit `96af7dc` triggered Fly Deploy run `29645346441`; the run and every job step succeeded. Daily Plaid Sync remained active, and production plus demo returned HTTP 200. No manual sync or sensitive log access occurred. The existing independent monitor owns the first natural minute-17 run observation.

## Project Documentation Contradicts Current Architecture

Status: resolved and released through PR #85

Severity: medium project reliability

Captured: 2026-07-17

Where seen: `README.md`, `PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, and `AGENTS.md`

Revisit: none unless active guidance diverges again

Summary:

Tracked root documentation mixes the retired Streamlit/manual-import architecture with the current Flask, HTMX, Plaid, Fly.io, and three-entity system. The most current instruction file is untracked.

Impact:

Agents and maintainers can begin from an incorrect architecture, execute obsolete commands, or mistake completed planning for future work.

Resolution:

Work block 2B added a concise tracked `AGENTS.md` as canonical, reduced `CLAUDE.md` to a compatibility pointer, and replaced `PROJECT_KNOWLEDGE.md` plus `plan.md` with historical notices backed by Git history. Work block 2B-R merged PR #85 as `216a992`, and the resulting production deployment plus HTTP health checks passed.

## Short-Term Planning Legacy Plan Exceeds Current Verification Evidence

Status: parked for Phase 3 audit

Severity: medium regression-confidence risk

Captured: 2026-07-18

Where seen: retired `plan.md`, `scripts/smoke_test.py`, and `scripts/seed_demo_data.py`

Revisit: Phase 3 functional audit and prioritization

Summary:

The legacy Short-Term Planning plan proposed dedicated goal CRUD, snapshot, budget, payoff, entity-isolation, and cross-entity smoke cases plus seeded goals and snapshots. The current feature is substantially implemented, but the synthetic smoke suite contains no dedicated Short-Term Planning cases, and demo seeding covers budgets and action items rather than the planned goal and snapshot examples.

Impact:

The historical plan cannot be treated as acceptance proof. Current behavior may be correct, but regression confidence and demo coverage need a fresh evidence-based audit rather than an assumption based on an obsolete checklist.

Why not now:

Work block 2B is documentation governance only. Adding product tests or demo data would widen scope into Phase 3 or Phase 4 and requires its own bounded work block.

Promotion trigger:

Phase 3 decomposes the functional audit and decides whether the missing dedicated cases are defects, useful regression additions, or superseded requirements.

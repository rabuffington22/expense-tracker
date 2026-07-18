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

Status: parked pending roadmap confirmation

Severity: medium project reliability

Captured: 2026-07-17

Where seen: `README.md`, `PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, and `AGENTS.md`

Revisit: proposed Phase 2

Summary:

Tracked root documentation mixes the retired Streamlit/manual-import architecture with the current Flask, HTMX, Plaid, Fly.io, and three-entity system. The most current instruction file is untracked.

Impact:

Agents and maintainers can begin from an incorrect architecture, execute obsolete commands, or mistake completed planning for future work.

Why not now:

The bootstrap preserves existing files. Rewriting or archiving legacy docs requires a separate reviewed documentation block.

Promotion trigger:

Ryan confirms the proposed documentation-recovery phase and decides how `AGENTS.md` should be governed.

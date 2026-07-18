# Issues

These are known defects, risks, or rough edges. They are not active work unless promoted into a phase task and confirmed work block.

## Daily Plaid Sync Disabled For Inactivity

Status: recurrence cause defined in 1B; monitor implementation pending

Severity: high operational reliability

Captured: 2026-07-17

Where seen: GitHub Actions workflow metadata and run history

Revisit: Phase 1, Task 4 for recurrence prevention or detection

Summary:

The `Daily Plaid Sync` workflow was found `disabled_inactivity` after its last listed successful scheduled run on 2026-07-15. Work block 1A re-enabled it and verified controlled run `29627530457` successfully.

Impact:

Immediate sync scheduling is restored. Work block 1B found that the public repository's more-than-60-day commit gap closely matches GitHub's documented automatic-disable rule. A future quiet period could still allow recurrence until Task 5 adds independent alert-only monitoring.

Why not fully closed:

The safeguard is now defined but not implemented. Proposed work block 1C creates a local Codex monitor that checks public workflow state and scheduled-run freshness without enabling or dispatching the workflow.

Promotion trigger:

Ryan confirms proposed work block 1C.

## Daily Plaid Sync Runs At The Start Of The Hour

Status: planned hardening task

Severity: low operational reliability

Captured: 2026-07-18

Where seen: `.github/workflows/daily-plaid-sync.yml`

Revisit: Phase 1, Task 6

Summary:

The workflow uses `0 9 * * *`. GitHub documents that scheduled workflows are more likely to be delayed during high load at the start of an hour and that sufficiently loaded queued jobs may be dropped.

Why not now:

Changing the workflow file has a separate source, release, and production-deployment boundary. It does not belong in the alert-only monitor block.

Promotion trigger:

Ryan confirms a separate Task 6 work block after the monitor is in place.

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

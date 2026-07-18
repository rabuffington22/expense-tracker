# Issues

These are known defects, risks, or rough edges. They are not active work unless promoted into a phase task and confirmed work block.

## Daily Plaid Sync Disabled For Inactivity

Status: resolved in work block 1A; recurrence safeguard pending

Severity: high operational reliability

Captured: 2026-07-17

Where seen: GitHub Actions workflow metadata and run history

Revisit: Phase 1, Task 4 for recurrence prevention or detection

Summary:

The `Daily Plaid Sync` workflow was found `disabled_inactivity` after its last listed successful scheduled run on 2026-07-15. Work block 1A re-enabled it and verified controlled run `29627530457` successfully.

Impact:

Immediate sync scheduling is restored. A future quiet period could still allow the workflow to become inactive again unless Phase 1 Task 4 defines a detection or prevention safeguard.

Why not fully closed:

Choosing and implementing a recurring safeguard is a separate project-control and automation decision outside work block 1A.

Promotion trigger:

Ryan confirms a safeguard-definition block, then separately approves any implementation that creates a monitor, automation, external service, or recurring cost.

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

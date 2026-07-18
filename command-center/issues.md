# Issues

These are known defects, risks, or rough edges. They are not active work unless promoted into a phase task and confirmed work block.

## Daily Plaid Sync Disabled For Inactivity

Status: parked pending Phase 1 approval

Severity: high operational reliability

Captured: 2026-07-17

Where seen: GitHub Actions workflow metadata and run history

Revisit: proposed Phase 1, Task 1

Summary:

The `Daily Plaid Sync` workflow is currently `disabled_inactivity`. Its last listed successful scheduled run was 2026-07-15.

Impact:

The intended automated financial-data refresh is not currently scheduled, even though recent runs had been successful.

Why not now:

Enabling or triggering a workflow is an external mutation excluded from the Runway OS bootstrap.

Promotion trigger:

Ryan confirms a Phase 1 operational-reliability work block with exact enable, verification, and stop conditions.

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

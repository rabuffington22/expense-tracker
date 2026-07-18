# Decision Log

## Accepted

### 2026-07-17 — Install the full Runway OS in Expense Tracker

Ryan rejected a thin overlay and confirmed a full in-repo Runway OS install. The target repo will own its roadmap, current state, decisions, operating rules, dashboard, logs, handoffs, and verification history in `command-center/`.

### 2026-07-17 — Keep the financial-data protection profile without reducing the OS

The scaffold records the `sensitive-retrofit` profile because the project handles financial, payroll, credentialed, and production operations. This affects default worker automation and reporting boundaries only. It does not remove any core Runway OS planning, dashboard, state, handoff, or verification surface.

### 2026-07-17 — Preserve existing project files during bootstrap

The installer is staged separately and only new Runway OS surfaces are transplanted. Existing `README.md`, `.gitignore`, application directories, documentation, ignored data, and the two pre-existing untracked files are not overwritten or staged by default.

### 2026-07-17 — Use the existing repo shape

Expense Tracker's product source remains in `web/`, `core/`, `scripts/`, and root entry/configuration files. Scratch-only `app/` and `scratch/` directories will not be added merely to satisfy a generic scaffold check.

### 2026-07-17 — Make Runway OS canonical for project control

Legacy documentation remains supporting domain material or migration input. It does not compete with `command-center/roadmap.md`, `now.md`, `decisions.md`, `operating-rules.md`, and `state.json` for current project direction.

### 2026-07-17 — Keep bootstrap read-only toward application and production behavior

Work block 0A installs and verifies the operating system only. It does not re-enable GitHub workflows, trigger Plaid, deploy Fly apps, access ignored financial data, modify application code, or rewrite legacy documentation.

### 2026-07-17 — Accept Phases 1-5 as the baseline roadmap

Ryan confirmed the proposed operational reliability, documentation recovery, functional audit, repair/testing, and UX/operations phases. Each phase still requires just-in-time work-block confirmation before execution.

### 2026-07-17 — Make the Runway OS branch durable before live recovery

Ryan authorized staging only `PROJECT_STRUCTURE.md` and `command-center/`, committing the verified full install, and pushing `codex/runway-os-full-install` to the existing GitHub remote. Pre-existing untracked files remain excluded.

### 2026-07-17 — Confirm work block 1A and its live effects

Ryan authorized enabling Daily Plaid Sync and dispatching one controlled workflow run after target durability. The run may insert newly available transactions into the configured production entities and invoke the existing Luxe Legacy bridge for qualifying data. Source-code, secret, Fly, database-transfer, authentication, PR, merge, and parent-repo changes remain excluded.

## Pending Ryan Direction

- Decide in Phase 2 whether `AGENTS.md` becomes tracked and which legacy documentation is archived or replaced.
- Decide after evidence from 1A how Phase 1 Task 4 should prevent or detect future scheduled-workflow inactivity.
- Decide later whether the Runway OS branch should open a PR and merge to `main`.

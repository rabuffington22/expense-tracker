# Dashboard Refresh Skill

## Purpose

Refresh the local command-center dashboard from repo state.

Use this skill when `state.json`, `now.md`, the roadmap, decisions, or active tasks change.

## Inputs

- `command-center/state.json`
- `command-center/index.html`

## Workflow

1. Validate that `state.json` is valid JSON.
2. Run `node command-center/scripts/refresh-dashboard.js`.
3. Open `command-center/index.html` locally to inspect the dashboard.
4. Confirm the active phase, current task, owner, next action, and blockers are correct.

## Output

- Updated `command-center/index.html` with embedded dashboard state.
- A short verification note.

## Rules

- The dashboard is a view, not the source of truth.
- `state.json` remains the machine-readable state.
- `now.md` remains the human-readable state.
- The dashboard must be kept current after any meaningful project-state change.
- Trivial prose edits and unpromoted drafts do not require refresh by themselves.
- Every work-block or project-state closeout requires refresh and health check when project state changed.
- Do not report dashboard/state work as complete until refresh succeeds and the relevant health check passes.

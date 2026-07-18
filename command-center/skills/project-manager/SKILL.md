# Project Manager Skill

## Purpose

Maintain Runway OS, the repo-based project operating system.

Use this skill when Ryan asks to plan, reprioritize, check status, delegate work, summarize where the project is, or decide the next action.

## Inputs

- `command-center/state.json`
- `command-center/now.md`
- `command-center/roadmap.md`
- `command-center/decisions.md`
- Recent handoffs and logs

## Workflow

1. Read the current state files.
2. Identify the active phase, active task, owner, blocker, and next action.
3. Update `now.md` if the current focus changed.
4. Update `state.json` if the dashboard state changed.
5. Add a decision entry if the project direction changed.
6. Create a handoff if another agent should act.

## Output

- A concise status update.
- Updated state files when needed.
- A specific next action.

## Rules

- Keep the repo as the source of truth.
- Do not add a new tool unless it clearly reduces friction.
- Separate current action from future ideas.
- Keep Ryan in the loop for meaningful direction changes.

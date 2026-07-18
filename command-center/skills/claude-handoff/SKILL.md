# Claude Handoff Skill

## Purpose

Create a structured task packet for Claude Desktop.

Use this skill when implementation work should be delegated to Claude.

## Inputs

- Task: what Claude should build, change, fix, or inspect
- Scope: repo area, files, feature, bug, or artifact involved
- Desired outcome: what should be true when Claude is done
- Constraints: what Claude should avoid or preserve
- Acceptance checks: tests, screenshots, manual checks, or file changes that prove completion
- Desired return format

Gather missing context from the user's message, `command-center/state.json`, `command-center/now.md`, `command-center/roadmap.md`, and relevant repo files.

## When To Ask Ryan

Ask one or two concise questions only when missing information means Claude could reasonably do the wrong job.

Ask when:

- The task itself is unclear.
- The target area or files cannot be inferred.
- The desired outcome is ambiguous enough to change the implementation.
- A constraint is likely important but unknown, such as whether to avoid data-model changes, dependencies, visual redesign, or broad refactors.

Do not ask when the task is clear enough to draft safely. Generate the handoff, include an `Assumptions` section for inferred details, and keep the assumptions easy for Ryan to correct before pasting to Claude.

## Workflow

1. Read `command-center/now.md` and `command-center/state.json`.
2. Inspect the relevant project files.
3. Decide whether enough context exists to draft safely; if not, ask Ryan the smallest useful question.
4. Use `node command-center/scripts/new-claude-handoff.js` when a standard implementation packet is enough.
5. Manually edit the generated handoff when the task needs assumptions, unusual context, or tighter acceptance checks.
6. Keep the handoff paste-ready for Claude.

## Return Format For Claude

Ask Claude to return:

1. Summary
2. Files changed
3. Tests/checks run
4. Decisions or assumptions
5. Risks/follow-ups

## Rules

- Make the handoff specific enough to execute.
- Do not include unrelated background.
- Ask Claude to flag product or architecture decisions before making them.
- Prefer file paths and concrete acceptance checks over general instructions.
- Keep the generated handoff as a repo artifact, not only pasted chat text.
- Ask Ryan sparingly; infer from repo truth when the risk of doing the wrong job is low.

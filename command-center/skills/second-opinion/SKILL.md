# Second Opinion Skill

## Purpose

Ask another model to critique a plan, decision, implementation, or handoff through an explicit reviewer route.

Use this skill before architecture decisions, large refactors, unclear product direction, risky automation, or moments where Ryan wants another model's judgment.

## Inputs

- The question to critique
- Relevant files or excerpts
- Proposed plan or diff
- Known constraints
- Reviewer route, if Ryan already specified one
- Claude CLI model and effort, if Ryan already specified them

## Workflow

1. Define the specific question.
2. Select the reviewer route before creating output:
   - If Ryan names the reviewer or route, use that route when it is available and safe.
   - If Ryan does not name the route, ask him to choose before drafting or running the review.
   - Offer concrete options:
     1. Claude CLI direct run - best for text-based repo critique when a prompt can be safely sent and `claude` is available.
     2. Claude Desktop/manual paste - best when Ryan wants to use an existing Claude session or manually control context.
     3. Claude Design - visual-only; use only for screenshots, UI mockups, assets, or visual design review.
     4. Other named reviewer - use when Ryan specifies another model or process.
3. If the selected route is Claude CLI, select the model and effort before running:
   - If Ryan specified both model and effort, use them.
   - If Ryan says "most powerful model" without naming a CLI alias, treat that as `opus`.
   - If either model or effort is missing, ask Ryan to choose before creating or running the review.
   - Offer high-power options first:
     1. `--model opus --effort max` - strongest/default recommendation when Ryan wants the most powerful review and cost/time are acceptable.
     2. `--model opus --effort xhigh` - very high effort; use when Ryan says "very high."
     3. `--model opus --effort high` - high effort; still strong, usually faster.
     4. Custom model and effort, such as another Claude model alias plus `high`, `xhigh`, or `max`.
   - Treat "very high" as `xhigh` for Claude CLI.
   - If the requested model or effort fails in the CLI, stop and report the error instead of silently falling back.
4. Gather the smallest useful context.
5. Create a dated prompt/brief in `command-center/handoffs/second-opinion/`.
6. Include the selected reviewer route, why it was selected, and the Claude CLI model/effort when relevant.
7. If the selected route is Claude CLI, verify `claude` is available, run non-interactively with the saved prompt, and save the response under `command-center/logs/second-opinion/`.
8. Ask for direct critique, risks, alternatives, recommendation, confidence, and what would change the recommendation.
9. After the response returns, save it in `command-center/logs/second-opinion/`.
10. Promote durable decisions into `command-center/decisions.md`.

## Output

- A selected reviewer route.
- Selected Claude CLI model and effort when relevant.
- A saved second-opinion prompt/brief.
- A reviewer response when the selected route can be run directly.
- An intake summary after the response is returned.

## Rules

- The second opinion should pressure-test, not restart the entire project.
- Ask for practical recommendations.
- Keep the final decision with Ryan and the repo-based operating state.
- Do not silently turn a second opinion into a manual handoff when a direct reviewer route is available and Ryan selected or approved it.

# Work Block 2B Closeout — Documentation Governance

Date: 2026-07-18

Status: verified on draft PR #85; release not authorized

## Authorized Scope

Retire `PROJECT_KNOWLEDGE.md` and `plan.md` as active guidance, establish a concise tracked `AGENTS.md` as the canonical agent instruction source, reduce `CLAUDE.md` to a compatibility entry point, update supporting documentation and Runway OS, and publish a verified feature branch plus draft PR. Application code, workflows, databases, production systems, financial data, untracked `scripts/sync_prod_to_local.sh`, merge, and deployment remained excluded.

## Result

- Added tracked `AGENTS.md` with source priority, product shape, protected-data and live-side-effect gates, Git rules, implementation conventions, safe verification, and documentation-maintenance rules.
- Reduced `CLAUDE.md` from 1,150 lines to a compatibility entry point that directs Claude-based tools to the canonical instructions and current sources.
- Replaced `PROJECT_KNOWLEDGE.md` with a historical notice for the retired Streamlit and Atlas-hosted architecture and preserved the full snapshot through `git show 66a60de:PROJECT_KNOWLEDGE.md`.
- Replaced `plan.md` with a historical notice for the Short-Term Planning plan and preserved the full plan through `git show a70e35b:plan.md`.
- Updated `README.md` and `PROJECT_STRUCTURE.md` to record the new authority model.
- Preserved the exact original untracked `AGENTS.md` as Git blob `f8c8b792f29e91e3faf8cf8b253cfcb7e5ecb313` before replacement.
- Parked an evidence-backed Phase 3 audit issue: dedicated Short-Term Planning smoke cases and seeded goal/snapshot examples promised by the legacy plan are not present as written.

## Verification

- `.venv/bin/python scripts/smoke_test.py` — passed using a temporary synthetic `DATA_DIR`.
- `node command-center/scripts/refresh-dashboard.js` — passed.
- `node command-center/scripts/health-check.js` — passed.
- Rendered dashboard inspection — passed; Phase 2, Task 3, Ryan ownership, work block 2B completion, and the 2B-R decision render correctly without placeholder decision text.
- `git diff --check` — passed.
- Current documentation authority and stale-guidance scans — passed.
- Added-line sensitive-content scan — passed; only protective boundary language matched.
- Historical Git object and referenced-path validation — passed.
- Exact staged-path inspection — passed; twelve authorized paths only.
- Draft PR inspection — passed; PR #85 is open, draft, targets `main`, and contains the expected twelve paths.

## Durability

- Branch: `codex/phase-2-document-governance`
- Source commit: `912c9bb74e59771d885d2942828e0c7f402f6ac7`
- Remote branch: `origin/codex/phase-2-document-governance`
- Draft PR: https://github.com/rabuffington22/expense-tracker/pull/85
- `main` and production: unchanged

The GitHub app connector returned a PR-write authorization error. The authenticated `gh` CLI fallback created draft PR #85, consistent with the publication workflow. No merge, deployment, workflow action, production read, credential access, or financial-data access occurred.

## Next Gate

Ryan reviews draft PR #85 and confirms or revises a separate 2B-R release block. That block should own the ready/merge decision, single automatic Fly deploy observation, sanitized production health checks, and final Phase 2 closeout.

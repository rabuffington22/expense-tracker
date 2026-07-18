# 2026-07-18 — Work Block 2A Root Project Entry Point

## Authorization And Scope

Ryan confirmed work block 2A for Phase 2 Tasks 1 and 4. The block authorized rebuilding the root README from tracked repository truth, documenting sanitized deployment/data/side-effect boundaries, updating the supporting project-structure and Runway OS surfaces, committing and pushing `codex/phase-2-root-docs`, and opening a draft PR.

The block excluded application code, workflows, databases, production, Plaid, Fly, credentials, row-level financial data, legacy-document edits or archival, `CLAUDE.md`, pre-existing untracked `AGENTS.md` and `scripts/sync_prod_to_local.sh`, parent-repo changes, merge, and deployment.

## Implementation

- Replaced the retired Streamlit, manual-import-only, two-entity README with the current Flask, HTMX, Plaid, Fly.io, and three-entity architecture.
- Documented entity isolation, local synthetic setup, supported environment-variable names without values, application surfaces, import/sync paths, data layout, deployment mechanics, and explicit authorization gates.
- Corrected `PROJECT_STRUCTURE.md` so the README is classified as the current root entry point.
- Preserved the legacy and untracked files for the separately gated Tasks 2 and 3.

## Verification

- `.venv/bin/python scripts/smoke_test.py` passed all database, import, deduplication, entity-isolation, route, export, saved-view, and To Do checks using a temporary synthetic `DATA_DIR`.
- README claims were cross-checked against `run.py`, `web/__init__.py`, `core/db.py`, Plaid/AI/bridge modules, Fly configurations, GitHub workflows, `.env.example`, requirements, and current repository paths.
- Stale `streamlit run`, `app/main.py`, no-bank-linking, two-entity, and OpenClaw instructions were absent from the replacement README.
- Referenced repository paths and documented environment-variable names were verified against tracked files.
- `PROJECT_KNOWLEDGE.md`, `plan.md`, `CLAUDE.md`, `.github/`, `web/`, `core/`, and `scripts/` had no tracked diff.
- `git diff --check`, dashboard refresh, and Runway OS health check passed.
- Exact staging contained only the seven confirmed README, project-structure, and active Runway OS files. The pre-existing untracked files remained outside the commit.

## Durability

- Branch: `codex/phase-2-root-docs`
- Source implementation commit: `c249c9b`
- Draft PR: `#84`
- Merge: not performed
- Deploy: not triggered

## Result

Work block 2A completed without a safety stop. The project now has a reviewable, evidence-backed root entry point on draft PR #84. Tasks 2 and 3 remain separately gated because legacy-file disposition and instruction-source ownership are governance choices rather than mechanical follow-ons.

## Learning

The largest documentation risk was not missing detail; it was that the old root entry point confidently described a retired application. The tracked runtime now provides enough evidence for a concise current README, while the remaining disagreement is isolated to legacy-document and agent-instruction governance. That means the next block can focus on choosing one maintained instruction path instead of rediscovering the application architecture.

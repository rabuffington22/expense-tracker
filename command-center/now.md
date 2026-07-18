# Current Focus

## Active Objective

Prepare the first bounded Phase 3 functional-audit work block after completing and releasing project-truth recovery.

## Current Phase

Phase 3: Functional Audit And Prioritization — active.

## Completed Work Block

2B-R: Publish Canonical Project Guidance — merged, deployed, and verified.

## Current Task

Phase 3 Task 1: audit core workflows for Personal, BFM, and Luxe Legacy with safe data-handling rules — awaiting a just-in-time planning pass and separately confirmed audit work block.

## Owner

Ryan owns confirmation or revision of the first Phase 3 audit block. Codex Desktop owns the verified 2B-R release evidence, Phase 2 closeout, dashboard currency, and the next just-in-time planning pass.

## Release Result

PR #85 was marked ready and merged to `main` as `216a992`. Automatic Fly Deploy run `29647452643` completed successfully, including every job step. Production root and `/health` both returned HTTP 200. Only sanitized workflow, job, step, and HTTP status was inspected; no deployment logs, response bodies, credentials, secrets, or financial data were opened.

The release established tracked `AGENTS.md` as the canonical agent instruction source, reduced `CLAUDE.md` to a compatibility entry point, and retired `PROJECT_KNOWLEDGE.md` plus `plan.md` as competing guidance while preserving their history. The Short-Term Planning verification gap remains parked for Phase 3 audit rather than being assumed fixed.

## Durability

- PR: https://github.com/rabuffington22/expense-tracker/pull/85
- Merge commit: `216a992`
- Fly Deploy run: `29647452643` — success
- Production root: HTTP 200
- Production `/health`: HTTP 200
- Status: merged and deployed on `main`; sanitized closeout published with `[skip actions]`
- Preserved user file: untracked `scripts/sync_prod_to_local.sh`, untouched and unstaged

## Current Action

Run a just-in-time planning pass over the smallest useful Phase 3 audit slice and propose one separately confirmed work block before opening financial data, accessing Plaid, testing production behavior beyond safe HTTP status, or beginning audit execution.

## Phase 3 Boundary

- No functional audit, production account access, Plaid action, row-level financial-data read, workflow action, application change, or test expansion begins without a separately confirmed Phase 3 work block.
- The first planning pass should decide whether Task 1 needs local decomposition before selecting a safe synthetic-first audit slice.
- The parked Short-Term Planning verification gap is an audit input, not an automatically authorized fix.

# 5H-A Ask Opus Data-Handling Contract Audit

Date: 2026-07-27

Status: done locally; contract recommendation returned to Ryan and implementation remains unstarted.

## Confirmed Scope

Audit Phase 5 Task 2.5 (`P5-T25`) only for its contract prerequisite. Use tracked source and current public official provider documentation to map Ask Opus transmission, page and entity scope, cross-entity behavior, history persistence and clearing, disclosure, authentication, CSRF, error, and logging boundaries. Produce a sanitized decision packet with explicit options, a recommended contract, and acceptance criteria for a later implementation block.

## Exclusions

Do not change product, route, template, style, JavaScript, test, dependency, workflow, configuration, authentication, database, AI, or PWA behavior. Do not read existing temporary chat-history files, `.env`, credentials, real databases, uploads, or financial rows. Do not call OpenRouter, Anthropic, Plaid, Fly, production, demo, or another live API. Do not stage, commit, push, change PR #90, merge, deploy, delegate, request a second opinion, or touch the duplicate 4AU log, `command-center/now 2.md`, or `scripts/sync_prod_to_local.sh`.

## Defaults

- Treat Ask Opus transmission as permitted only after an explicit question submission.
- Recommend entity-local context by default and no silent page fallback or cross-entity inclusion.
- Recommend the minimum page-relevant data needed for the stated purpose.
- Recommend no invisible indefinite on-disk transcript; any retained multi-turn history needs an explicit duration, visible semantics, and complete clear behavior.
- Make no provider retention, training, or deletion claim without current official support.
- Recommend rather than adopt the final contract; Ryan retains every policy and implementation decision.

## Stop Conditions

Stop if the audit requires protected data, credentials, live configuration, existing chat files, or an AI/API call; if current provider documentation cannot support a disclosure-critical claim; if an urgent security correction or product change becomes necessary; if scope expands beyond the Task 2.5 contract prerequisite; or if exact-path, sensitive-data, JSON, dashboard, health, or whitespace verification fails.

## Next Report Point

Return the source-backed page/context matrix, provider-policy findings, important mismatches and risks, recommended contract, alternatives and tradeoffs, exact Ryan decision prompt, changed artifacts, verification result, and the separately confirmed 5H-B implementation gate.

## Source Audit Result

- The modal sends nothing when opened. A submit posts the question, requested page, fresh database context, retained question/answer history, system prompt, and fixed `anthropic/claude-opus-4.6` model request to OpenRouter.
- Dashboard, Long-Term Planning, Short-Term Planning, Recurring Review, Cash Flow, and General contexts silently combine Personal and BFM data. Transactions and Reports remain entity-local; Luxe Legacy has no configured cross-entity peer.
- Weekly and Waterfall submit unrecognized page identifiers. Ask normalizes both to `general`, so they share the same general context and persisted history. Clear retains the visible `weekly` or `waterfall` identifier and deletes a different file, leaving the history actually used intact.
- The General fallback includes three-month spending and income, top categories, and named account balances, types, and limits for both Personal and BFM.
- History persists in per-entity/page temporary JSON files for at most 40 message objects, but has no TTL, logout cleanup, visible restoration, or documented permission contract. Saved questions and answers can themselves contain financial details even though the freshly injected context is not written to the history file.
- The current provider request has no per-request ZDR, data-collection restriction, fixed provider, or disabled fallback. Effective provider retention therefore depends on external account settings and automatic routing not verifiable from the repository.
- Global authentication covers the AI routes only when the app password is configured. Global CSRF, no-store response, and escaped-output contracts apply.
- Maintained tests cover trigger markup, modal behavior, CSRF wiring, accessibility-adjacent focus/close behavior, and denied live AI configuration. They do not directly cover payload fields, entity scope, page normalization, history retention, Clear, or provider privacy controls.

## Official Provider Findings

Public official documentation reviewed on 2026-07-27 establishes:

- OpenRouter prompt and response content logging is opt-in and off by default, but account-specific settings remain unknown; request metadata is retained.
- OpenRouter ordinarily load-balances among providers and permits providers that may store data unless account or request controls narrow routing.
- OpenRouter supports per-request `provider.zdr: true`; ZDR endpoints do not persist content under OpenRouter's definition, though in-memory prompt caching may still occur.
- Provider retention policies vary independently.
- Anthropic's first-party commercial API does not train on content by default and ordinarily deletes inputs and outputs within 30 days, subject to documented exceptions; OpenRouter may route to a different endpoint, so this cannot describe every current request.

No credential, account setting, live API, AI provider, production, protected data, existing chat file, or real database was accessed.

## Recommendation

Approve the contract in `command-center/ask-opus-data-handling-contract.md`: explicit submission only; active-entity, summary-first context; no silent cross-entity inclusion or broad fallback; no server-side transcript by default; per-request ZDR plus denial of data-collecting providers; separately verified OpenRouter logging/use settings before any production retention claim; clear provider, data-category, entity, metadata, retention, and fallibility disclosure; and fail-closed behavior. Disable Weekly and Waterfall Ask triggers until dedicated minimum-data contexts exist.

## Verification

- Tracked source and maintained tests were inspected without executing an AI request or opening protected data.
- Current official OpenRouter and Anthropic documentation was reviewed without credentials.
- Python syntax passed for `web/routes/ai.py` and `core/ai_client.py`.
- The command-center JSON, dashboard generation/currentness, health, whitespace, exact product boundary, and sensitive-addition checks passed.
- PR #90 remained open, draft, clean, and unchanged at `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- The duplicate 4AU log, `command-center/now 2.md`, and `scripts/sync_prod_to_local.sh` retained their accepted hashes and remained excluded.

## Result

5H-A is complete locally. Task 2.5 remains incomplete and returns to Ryan as a contract decision. No product, test, configuration, external account, GitHub, workflow, merge, deployment, or production state changed. 5H-B remains separately gated.

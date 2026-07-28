# 5H-B Ask Opus Privacy Contract Implementation

Date: 2026-07-27

Status: done locally; unstaged, uncommitted, unpublished, and not provider-account verified

Task: Phase 5 Task 2.5 (`P5-T25`)

## Confirmed Boundary

Ryan accepted the recommended 5H contract and confirmed local implementation only. The block permitted exact-page, active-entity, summary-first Ask Opus contexts; no server transcript; browser-local Clear; Ask-specific OpenRouter ZDR and denial of data-collecting providers; truthful disclosure; focused and complete temporary-synthetic verification; maintained documentation; and Runway OS closeout.

Provider-account access, existing chat files, `.env`, credentials, real databases or financial rows, live OpenRouter or another API call, Personal/BFM combination, excluded identifiers, unrelated AI features, other Phase 5 tasks, PR 90 mutation, staging, commit, push, PR creation, merge, deployment, production, delegation, and second opinion remained excluded.

## Implementation Result

- `/ai/ask` accepts only `dashboard`, `transactions`, `planning`, `short-term-planning`, `subscriptions`, `cashflow`, and `reports`. Missing, `general`, `weekly`, `waterfall`, and crafted identifiers return 400 before context or provider work.
- Every context uses only the active entity. The prior Personal/BFM cross-entity map and broad General fallback were removed.
- Dashboard sends current-month totals, category totals, aggregate merchants, six-month trends, and uncategorized count without accounts or another entity.
- Transactions sends 90-day totals, category totals, and aggregate merchants without individual rows or exact dates.
- Long-Term Planning sends age, inflation, milestone projections, aggregate asset/liability counts and totals, contributions, payments, and net worth without birth date, account/item names, or combined Personal/BFM totals.
- Short-Term Planning sends goal, balance, target, monthly amount, progress-balance, aggregate-card, and budget summaries without account names, strategy text, notes, or another entity.
- Recurring Review sends merchant, amount, frequency, and status summaries without notes or broad appended financial context.
- Cash Flow sends account counts, aggregate balances, limits, utilization, scheduled-payment days and amounts, and recurring schedule days and amounts without account or merchant names.
- Reports remains an active-entity aggregate monthly/category context.
- All Ask current-month and report SQL date formats now use SQLite `%Y-%m`. Focused coverage found the prior `%%Y-%%m` literals silently omitted current-month categories and merchants.
- Each submission contains one fresh approved page summary plus the current question. Prior questions and answers are neither loaded nor sent.
- The temporary transcript directory, file helpers, history cap, and server Clear route were removed. Clear now removes only visible browser responses.
- Ask requests pass `provider: {"zdr": true, "data_collection": "deny"}`. Other OpenRouter features retain their existing request shapes.
- The system prompt now describes an AI explainer with bounded context and verification language rather than a full-access financial advisor.
- The modal discloses purpose, active entity, exact page data categories, OpenRouter-to-Claude-Opus path, private provider routing, possible request-metadata retention, absence of a Ledger transcript, and fallibility before submission.
- Weekly and Waterfall no longer expose Ask Opus.
- Maintained documentation records the accepted behavior and the separate provider-account gate.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: passed.
- Baseline `.venv/bin/python scripts/mobile_drawer_browser_test.py`: passed.
- Final `.venv/bin/python scripts/smoke_test.py`: passed.
- New maintained section 8ai passed exact supported pages, invalid-page rejection before data/provider work, one-question request shape, serialized provider controls, absence of transcript code and route, all seven contexts for Personal/BFM/LL, denied identifiers, cross-entity absence, approved fields, denied networking, and exact marker cleanup.
- Final `.venv/bin/python scripts/mobile_drawer_browser_test.py`: passed for configured-auth and no-password modes, Weekly/Waterfall Ask absence, modal purpose/scope/data/provider/metadata/transcript/fallibility disclosure, browser-local Clear, accessibility description, 390/768/1440 non-overflow, CSRF, CSP, HTMX, keyboard, PWA, console, denied networking, and cleanup.
- Direct sterile render used one empty temporary Personal database with no `.env`, credential, provider key, or external request. Desktop and 390px phone captures were inspected; the modal remained complete, readable, and non-overflowing with zero console errors, page errors, or blocked requests.
- The exact synthetic render server closed and `/tmp/expense-5h-b-render.b5HuG2` was removed.
- Python compilation, JavaScript syntax, JSON, dashboard refresh/currentness/health, whitespace, high-confidence sensitive-addition, exact-path, empty-index, preserved-file, and final worktree checks passed.
- Open draft PR 90 remained clean and unchanged at `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.

## Result

Task 2.5 and 5H-B are complete locally. Ask Opus now has an enforceable repository-level contract instead of relying on broad context, invisible transcript files, or mutable provider defaults. No provider account was inspected and no live AI request occurred, so account-setting verification, 5H-R durability, publication, merge, deployment, and production remain separately gated.

# Ask Opus Data-Handling Contract Decision Packet

Date: 2026-07-27

Status: accepted by Ryan and implemented plus verified locally in completed work block 5H-B

Task: Phase 5 Task 2.5 (`P5-T25`)

Work block: 5H-A — Ask Opus Data-Handling Contract Audit

## Decision Summary

Ask Opus is currently an on-demand OpenRouter chat request, but the interface does not disclose its actual data boundary. Several accepted page contexts include data from both Personal and BFM even when one entity is active. Weekly and Waterfall use page identifiers that the server rejects, so both silently fall back to one shared `general` context and history; their visible Clear action targets a different history path and therefore does not clear the conversation the server actually uses.

The recommended contract is:

1. Ask Opus is an optional, user-submitted AI explainer for the current page. Opening the modal sends nothing and the feature performs no Ledger write.
2. Context is entity-local by default. No Personal/BFM data is silently combined.
3. Every visible trigger has an exact accepted page contract. Unknown pages fail closed instead of falling back to `general`.
4. Context is summary-first and limited to fields necessary for that page. Raw transaction rows, exact transaction dates, account names, and free-form notes or strategies are excluded unless a later explicit page contract needs and discloses them.
5. The Ledger stores no server-side conversation transcript by default. The visible current-page thread may remain in the browser DOM until navigation or reload.
6. Every request requires OpenRouter per-request zero-data-retention routing and denial of data-collecting providers. A separately authorized operator check must also verify that OpenRouter input/output logging and use-of-inputs settings are off before the UI makes a provider-retention claim.
7. The modal states what is sent, which entity is included, that OpenRouter routes the request to a Claude model provider, that request metadata may be retained, and that AI output can be wrong and should be verified before financial decisions.
8. If a privacy requirement cannot be satisfied, the request fails closed without sending a broader or less-private fallback.

Ryan accepted this packet and separately confirmed local product implementation as work block 5H-B. Publication, provider-account verification, merge, deployment, and production remain separate gates.

## Current Transmission Path

- The modal opens locally; no provider request occurs until the user submits the form (`web/static/app-shell.js:166-196`, `web/templates/base.html:91-97`).
- `POST /ai/ask` accepts a question and page, normalizes any unrecognized page to `general`, gathers fresh database context, prepends retained history, and calls OpenRouter (`web/routes/ai.py:125-165`).
- The request sends the system prompt, prior retained questions and answers, fresh page context, and the new question to `https://openrouter.ai/api/v1/chat/completions` using model `anthropic/claude-opus-4.6` (`core/ai_client.py:14-15`, `core/ai_client.py:28-73`).
- The payload has no `provider` preferences, `zdr`, `data_collection`, fixed provider, or disabled-fallback setting. Effective provider retention therefore depends on OpenRouter account settings and automatic routing that the repository cannot verify.
- The system prompt describes Claude as a financial advisor with full access to the user's financial data and directs it to use names and dollar amounts while omitting advisor disclaimers (`web/routes/ai.py:46-50`).
- Questions and rendered answers are escaped before limited Markdown formatting (`web/routes/ai.py:175-183`, `web/routes/ai.py:935-944`).
- Chat request exceptions log the model identifier, not the prompt, context, or response (`core/ai_client.py:72-74`).

## Current Page And Entity Matrix

Personal and BFM cross-entity behavior is symmetric. Luxe Legacy has no configured cross-entity peer (`web/routes/ai.py:24-29`).

| Visible surface | Submitted page | Server context | Data categories sent | Current entity scope | Contract finding |
|---|---|---|---|---|---|
| Dashboard | `dashboard` | Dashboard plus General | Current-month spend, income and count; top categories and merchants; six-month trend; uncategorized count; three-month monthly totals; account names, balances, types and limits | Personal + BFM; LL local | Hidden cross-entity context |
| Transactions | `transactions` | Transactions | 90-day totals; categories; merchants; up to ten recent large transactions with exact date, merchant, amount and category | Active entity only | Contains row-like transaction detail |
| Long-Term Planning | `planning` | Planning plus General | Birth date or age, inflation and milestones; named assets and liabilities; values, rates, payments, contributions and projections; combined net worth; spending, categories and named account balances | Personal + BFM; LL local | Hidden cross-entity context and broad identifiers |
| Short-Term Planning | `short-term-planning` | Short-Term plus General | Goal names, types, balances, target dates, monthly amounts, strategies and snapshots; named credit accounts, balances, limits and utilization; category budgets and actuals; general spending and named accounts | Personal + BFM; LL local | Hidden cross-entity context and free-form strategy text |
| Recurring Review | `subscriptions` | Subscriptions plus General | Tracked merchant, amount, frequency and status; monthly total; general spending, categories and named accounts | Personal + BFM; LL local | Hidden cross-entity context; selected `notes` are not serialized |
| Cash Flow | `cashflow` | Cash Flow | Named bank and credit accounts, balances, limits, utilization, due day and payment; totals; recurring merchant, amount, day and account | Personal + BFM; LL local | Hidden cross-entity context |
| Reports | `reports` | Reports | Twelve-month spend, income and net totals; this- and last-month category totals | Active entity only | Aggregate and entity-local |
| Weekly Check-In | `weekly` | Falls back to General | Three-month spend and income; top categories; named account balances, types and limits | Personal + BFM; LL local | Page mismatch, hidden cross-entity fallback, shared history, broken Clear |
| Waterfall | `waterfall` | Falls back to General | Three-month spend and income; top categories; named account balances, types and limits | Personal + BFM; LL local | Page mismatch, hidden cross-entity fallback, shared history, broken Clear |
| Crafted/unknown page | Any unrecognized value | Falls back to General | Same General context | Personal + BFM; LL local | Fails open to broader generic context |

Source anchors: `web/routes/ai.py:37-41`, `web/routes/ai.py:132-139`, `web/routes/ai.py:202-218`, `web/routes/ai.py:236-415`, `web/routes/ai.py:418-635`, `web/routes/ai.py:638-929`, `web/templates/weekly.html:8-9`, and `web/templates/waterfall.html:13-14`.

## Current Local Retention And Clear Semantics

- History is stored under the process temporary directory as `chat_{entity}_{page}.json` (`web/routes/ai.py:20-22`, `web/routes/ai.py:101-119`).
- The file keeps at most 40 message objects, normally 20 user/assistant exchanges. There is no age, TTL, logout cleanup, startup cleanup, or documented file-permission contract.
- Only the injected fresh database context is omitted from the saved history. The saved question and answer can themselves contain names, dollar amounts, or other financial detail, so “clean history” is not a privacy classification (`web/routes/ai.py:170-173`).
- Server history is loaded for the next provider request, but the browser does not restore it after reload. Changing the page clears the visible DOM thread while persisted history remains (`web/static/app-shell.js:166-190`).
- Clear removes only the active entity/page file (`web/routes/ai.py:187-196`).
- For Weekly and Waterfall, `/ai/ask` first normalizes the page to `general`, so both use and append the same `chat_{entity}_general.json`. The Clear button retains the original `weekly` or `waterfall` value and attempts to remove a different file (`web/routes/ai.py:132-142`, `web/routes/ai.py:187-196`, `web/static/app-shell.js:184-190`).

## Existing Control Boundaries

- When `APP_PASSWORD_HASH` is configured, `/ai/*` is covered by the global session-authentication gate; when no password is configured, the app intentionally runs without that gate (`web/__init__.py:289-303`, `web/__init__.py:390-403`).
- Both AI POST routes are covered by global CSRF validation. The app shell injects the session CSRF token into POST forms and HTMX request headers (`web/__init__.py:347-374`, `web/static/app-shell.js:333-356`).
- Dynamic HTML responses receive `Cache-Control: no-store` and the maintained HTML security policy (`web/__init__.py:328-345`).
- Maintained smoke coverage verifies Weekly/Waterfall trigger markup but does not assert that their page identifiers are accepted by the AI route (`scripts/smoke_test.py:11824-11856`).
- Maintained browser coverage verifies modal open/close, page binding, focus, scroll lock, CSRF wiring and HTMX lifecycle with `OPENROUTER_API_KEY` empty. It does not call OpenRouter or test payload fields, entity scope, history persistence, clear behavior, or invalid-page normalization (`scripts/mobile_drawer_browser_test.py:4836`, `scripts/mobile_drawer_browser_test.py:5050-5128`).
- No maintained test directly exercises `/ai/ask`, `/ai/clear`, the context builders, provider privacy parameters, or the history cap and lifecycle.

## Current Official Provider Findings

Reviewed 2026-07-27 using public official documentation only; no API key, account, or provider request was used.

1. OpenRouter says it does not store prompt or response content unless the account opts into private input/output logging or use of inputs/outputs. Both settings are documented as off by default, but the repository cannot establish the actual account settings. OpenRouter does retain request metadata such as token counts and latency.
   Source: [OpenRouter Data Collection](https://openrouter.ai/docs/guides/privacy/data-collection).
2. OpenRouter automatically load-balances a model across available providers and permits providers that may store data by default unless privacy controls or account settings narrow routing. The current request supplies no provider controls.
   Source: [OpenRouter Provider Routing](https://openrouter.ai/docs/guides/routing/provider-selection).
3. OpenRouter supports per-request `provider.zdr: true`, which restricts inference to endpoints it classifies as zero data retention. OpenRouter's definition still permits in-memory provider prompt caching.
   Source: [OpenRouter Zero Data Retention](https://openrouter.ai/docs/guides/features/zdr).
4. Provider retention varies independently. OpenRouter documents account and request controls for provider data policies, but its ordinary routing does not itself select providers based on retention.
   Source: [OpenRouter Provider Logging](https://openrouter.ai/docs/guides/privacy/provider-logging/).
5. If the selected endpoint is Anthropic's first-party commercial API, Anthropic says it does not train on commercial API content by default and ordinarily deletes inputs and outputs within 30 days, subject to usage-policy, legal, product, and contract exceptions. That policy cannot be generalized to every provider endpoint that OpenRouter may select.
   Sources: [Anthropic commercial data retention](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) and [Anthropic commercial model-training use](https://privacy.claude.com/en/articles/7996885-how-do-you-use-personal-data-in-model-training).

## Findings And Risks

1. **High — Silent cross-entity disclosure.** Six effective contexts send both Personal and BFM data even when the user is visibly operating in one entity.
2. **High — Provider policy is not enforced in code.** The application cannot prove which provider endpoint processes a request, whether that endpoint retains content, or whether account-level prompt logging is enabled.
3. **High — Weekly/Waterfall Clear is ineffective.** Their questions share `general` history while Clear targets page-specific files that Ask never uses.
4. **Medium — Invisible local persistence.** Server history survives visible-thread resets and has no TTL or lifecycle guarantee.
5. **Medium — Some contexts exceed a summary-first purpose.** Exact transaction dates, merchant names, account names, goal strategies, and broad combined planning details are sent automatically.
6. **Medium — Purpose and limitations are understated.** The UI says only that it can provide insights from “your data,” while the system prompt frames it as an advisor and suppresses disclaimers.
7. **Medium — Contract behavior lacks direct tests.** Existing coverage protects shell behavior but not the data boundary.

Because no live configuration was accessed, this audit does not establish whether Ask Opus is enabled in production or what the current OpenRouter account settings are. Until 5H-B implements and verifies the selected contract, the conservative operating posture is not to submit real financial questions through Ask Opus.

## Recommended Page Contract

| Page | Recommended context |
|---|---|
| Dashboard | Active-entity month and trend aggregates plus category totals; exclude account names and cross-entity General append |
| Transactions | Active-entity aggregates and top merchants; exclude exact transaction dates and raw row-like entries by default |
| Long-Term Planning | Active-entity assets, liabilities and projections; include names only if Ryan accepts that disclosure; no automatic combined Personal/BFM section |
| Short-Term Planning | Active-entity goal and budget summaries; exclude free-form strategy text and linked account names |
| Recurring Review | Active-entity merchant, amount, frequency and status; continue excluding notes |
| Cash Flow | Active-entity balances and recurring schedule; decide separately whether account labels are necessary |
| Reports | Preserve current active-entity aggregate contract |
| Weekly | Disable Ask Opus until a dedicated minimum-data Weekly contract exists |
| Waterfall | Disable Ask Opus until a dedicated minimum-data Waterfall contract exists |
| Unknown | Return a clear 400 response without gathering data or calling OpenRouter |

If combined Personal/BFM analysis is valuable later, add a plainly labeled, off-by-default “Include Personal + BFM” control only on approved planning surfaces. The disclosure must update before submission and the server must independently validate the opt-in.

## Alternatives

### Local history

- **Recommended — no server transcript:** each question receives fresh approved page context and stands alone. The visible DOM thread is temporary.
- **Alternative — short explicit session:** retain encrypted or permission-restricted history for a defined short TTL, bind it to the authenticated browser session plus entity/page, restore it visibly, and make Clear remove exactly what the model will receive.
- **Reject — current temporary-file lifetime:** capped count without age, visible restoration, or reliable Clear is not a truthful retention contract.

### Provider policy

- **Recommended — per-request ZDR plus operator verification:** send `provider: {"zdr": true, "data_collection": "deny"}`, fail closed if no eligible endpoint exists, and separately verify OpenRouter content-logging/use settings are off.
- **Alternative — direct contracted provider:** use one provider under a separately reviewed contract and disclose its retention period.
- **Reject — account-settings-only reliance:** repository behavior and user-facing copy cannot prove mutable external account state.

### Data detail

- **Recommended — summary-first allowlist:** keep data categories explicit per page and test the serialized payload.
- **Alternative — detailed page data with explicit disclosure:** preserve selected identifiers only where the feature's value clearly depends on them.
- **Reject — broad fallback context:** an unknown or mismatched page must never result in a larger generic payload.

## Ryan Decision Prompt

Recommended decision:

> Approve the 5H contract: Ask Opus remains optional and sends only after explicit submission; context is active-entity and summary-first; unknown, Weekly, and Waterfall page contexts fail closed; The Ledger retains no server-side transcript; OpenRouter requests require per-request ZDR and denial of data-collecting providers; production disclosure claims require a separately authorized check that OpenRouter content logging and use-of-inputs are off; the modal identifies the provider path, data categories, entity scope, metadata retention, and AI fallibility; and Task 2.5 implementation remains separately confirmed as 5H-B.

Ryan may approve that recommendation or change:

1. whether combined Personal/BFM analysis should exist and on which pages;
2. whether account, merchant, goal, or transaction identifiers are allowed per page;
3. whether multi-turn server history is unnecessary or should use a defined short session;
4. whether the feature remains unused with real data until 5H-B;
5. whether provider routing must be ZDR-only or replaced with one direct contracted provider.

## 5H-B Acceptance Criteria

A later implementation block should not close until:

- every visible page identifier is server-accepted or its Ask trigger is absent;
- unknown pages fail before database context gathering;
- serialized context is covered by exact synthetic allowlist and entity-isolation tests;
- Personal/BFM combined data appears only after a tested explicit opt-in, if authorized;
- provider requests enforce the selected data-policy controls and fail closed;
- the selected local retention lifecycle and Clear behavior are exact and tested;
- modal disclosure names purpose, provider path, data categories, entity scope, retention, metadata, and limitations before submission;
- opening the modal still sends nothing and Ask performs no Ledger write;
- authentication, CSRF, CSP, HTMX, accessibility, responsive, PWA, and denied-network contracts remain intact;
- all verification uses temporary synthetic data with no real provider call;
- Runway OS closes locally and publication, merge, deployment, production, and provider-account verification remain separately gated.

## Decision Boundary

Ryan accepted this contract for local implementation in 5H-B. The repository behavior and maintained synthetic coverage now implement the selected boundary. No external account setting, live provider request, production surface, PR, or deployment changed.

## 5H-B Implementation Result

Completed locally on 2026-07-27. The implementation uses seven exact active-entity contexts, rejects unknown pages before data access, removes Weekly and Waterfall Ask entry points, stores no server transcript, makes Clear browser-local, sends one current question, enforces per-request ZDR plus denial of data-collecting providers, and discloses the page/entity/data/provider/metadata/retention/fallibility boundary before submission. Exact Personal/BFM/LL synthetic allowlists, provider-payload capture, both-auth installed-browser coverage, direct desktop/phone inspection, denied networking, and cleanup passed. Evidence: `command-center/logs/2026-07-27-ask-opus-privacy-contract-implementation-5h-b.md`.

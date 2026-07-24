# Read-Only Second Opinion — Work Block 4BA CSP Policy Reconciliation

Date: 2026-07-24
Reviewer route: Claude CLI direct run
Selected model: `claude-fable-5`
Selected effort: `max`
Why this route: Ryan explicitly selected Fable 5 at maximum effort for an independent, repo-grounded critique of the completed local policy draft.

## Read-Only Boundary

Review only. Do not edit files, run live services, contact Plaid, access credentials or protected financial data, inspect production/demo, alter Git state, or propose work outside the policy boundary unless identifying it as a separately gated future consideration.

Use only tracked/sanitized repository material and public security reasoning. The application, templates, routes, service worker, tests, dependencies, configuration, CSP headers, and nonce plumbing must remain unchanged in work block 4BA.

## Review Question

Is the completed 4BA contract a correct, least-privilege, implementation-ready policy handoff for strict exceptional documents/PWA behavior and the narrow Plaid Link exception, without leaking Plaid allowances to unrelated responses or prematurely crossing into Task 1P.4.4 implementation?

## Required Context

Read:

1. `AGENTS.md`
2. `command-center/csp-compatibility-contract.md`
3. `command-center/logs/2026-07-24-exceptional-document-plaid-csp-policy-reconciliation-4ba.md`
4. The active 4BA section at the top of `command-center/now.md`
5. The confirmed 4BA block in `command-center/roadmap.md`
6. `core/plaid_client.py`
7. `web/templates/plaid.html`
8. `web/templates/data_sources.html`
9. The render paths in `web/routes/plaid.py` and `web/routes/data_sources.py`
10. `web/static/sw.js`, `web/static/manifest.json`, and the security-header/service-worker/offline sections of `web/__init__.py`

Do not inspect local databases, uploads, environment files, credentials, or other protected paths.

## Proposed Policy

Strict server-rendered HTML documents use:

```text
default-src 'self';
base-uri 'none';
object-src 'none';
frame-ancestors 'self';
form-action 'self';
script-src 'self';
script-src-attr 'none';
style-src 'self';
style-src-attr 'none';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
frame-src 'none';
worker-src 'self';
manifest-src 'self';
media-src 'none'
```

Actual rendered Plaid Link documents start with that policy and change only:

```text
script-src 'self' 'nonce-<per-response-random>' https://cdn.plaid.com/link/v2/stable/link-initialize.js;
style-src 'self' 'nonce-<per-response-random>';
style-src-elem 'self' 'nonce-<per-response-random>';
style-src-attr 'unsafe-inline';
connect-src 'self' https://sandbox.plaid.com;
frame-src https://cdn.plaid.com
```

Production replaces the sandbox origin with `https://production.plaid.com`; both are never allowed together.

## Decisions To Pressure-Test

1. A Plaid variant is selected by an explicit rendered-document/response marker for `plaid.html` or `data_sources.html`, including a successful `data_sources.parse`, rather than by originating endpoint identity.
2. Redirects, authentication responses, and error-handler documents reached from Plaid endpoints remain strict.
3. One unpredictable nonce is generated per rendered Link response, appears in `script-src`, `style-src`, and `style-src-elem`, and is attached only to the exact external initializer element.
4. Application-owned scripts and styles remain external and nonce-free.
5. `style-src-attr 'unsafe-inline'` is confined to rendered Link documents.
6. `connect-src` permits only one validated Plaid environment per response.
7. `default-src` remains `'self'`; Plaid allowances are explicit and do not broaden it.
8. `img-src 'self' data:` is retained solely for seven stylesheet-local SVG data images.
9. Static, manifest, worker, API/JSON, and HTMX-fragment responses do not receive the HTML document policy.
10. The service worker's last-resort synthetic HTML response must receive the strict core CSP header during Task 1P.4.4, while cached `/offline` retains its original strict response header.

## Risks And Assumptions

- Current Plaid guidance may have subtleties around nonce handling for its injected styles or how `style-src-elem` and `style-src-attr` interact.
- A response marker must not be forgeable from request input or survive into redirects/errors.
- Adding CSP to the service-worker-generated emergency document must be correct and testable without expanding 4BA into a service-worker implementation change.
- The strict policy must preserve same-origin service-worker registration, manifest/icons, local CSS/JS, offline fallback, forms, and all existing authentication/entity boundaries.
- The contract should be exact enough for Task 1P.4.4 but must not pre-authorize implementation, live Plaid, credentials, publication, or deployment.

## Requested Response

Return:

1. **Verdict:** approve, approve with corrections, or reject.
2. **Critical findings:** correctness or security issues that must be resolved before 4BA closes.
3. **Important findings:** implementation-handoff ambiguities worth correcting now.
4. **Optional hardening:** useful ideas that are not required for this bounded block.
5. **Specific proposed text changes:** concise edits to the contract/evidence, if needed.
6. **Alternative design:** only if materially safer or simpler.
7. **Recommendation and confidence:** clear final recommendation with high/medium/low confidence.
8. **Missing information:** only facts that would materially change the recommendation.

Distinguish source-backed findings from assumptions. Do not recommend broader origins, both Plaid environments, general inline allowances, live validation, or product changes merely for convenience.

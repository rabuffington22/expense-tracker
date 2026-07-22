# Work Block 4AH — Transaction And Supporting Modal Fragment Execution

Date: 2026-07-22

Status: complete and verified locally; not published

## Scope

Task 1P.4.2b.2 only. The block migrated the one executable script, twenty-eight native inline event handlers, and two `hx-on` handlers from `txn_results.html`, `txn_row_edit.html`, `txn_split_editor.html`, `subcat_txns_popup.html`, and `todo_queue_detail.html`. Task 1P.4.2b.3, remaining full-page execution, style compatibility, CSP headers, Plaid, authentication, protected data, live systems, GitHub durability, and both preserved untracked files remained excluded.

## Implementation

- Added maintained `web/static/transaction-fragments.js` and loaded it from the shared shell.
- Replaced fragment-native execution with delegated data actions for transaction sorting/copy, edit cascades, custom subcategory Enter handling, suggestion, modal closure, supporting popup/queue closure, and split add/remove/auto/save/delete behavior.
- Preserved the split editor's two inert `application/json` blocks and initialized swapped editors idempotently through `htmx:load`.
- Kept existing full-page transaction helpers in place because Task 1P.4.2c owns their later migration.
- Kept HTMX `allowEval=true` and `allowScriptTags=true`; Task 1P.4.2b.3 owns the global switch change and cross-route proof.

## Verification

- Baseline and final `.venv/bin/python scripts/smoke_test.py` passed with temporary synthetic all-entity databases.
- Focused source and rendered-response assertions prove all five fragments contain zero executable inline scripts, zero native inline handlers, and zero `hx-on` attributes.
- The post-4AH maintained aggregate is 22 executable inline scripts, seven external executable scripts, five inert JSON blocks, 116 native inline handlers, and zero `hx-on` attributes.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed in configured-auth and no-password modes. It covered repeated transaction swaps, sorting, copy, edit/save and modal closure, synthetic local-only AI suggestion, rule creation, split add/remove/auto/save/delete, subcategory-popup closure, To Do queue closure, continued temporary HTMX settings, and exact temporary cleanup.
- Browser traffic was restricted to localhost/data URLs; no external request occurred, and console/page error lists were empty.
- Python compilation, JavaScript syntax, JSON parsing, `git diff --check`, dashboard refresh, command-center health, rendered-dashboard inspection, exact-path review, and preserved-file checks passed.

## Boundaries And Result

No new runtime dependency, commit, push, PR, merge, deployment, production/demo inspection, protected data, credential, real database, retained upload, workflow action, downstream access/write, live action, or preserved-untracked-file mutation occurred. The result remains local-only on `codex/csp-transaction-modal-fragments`. Proposed work block 4AI for Task 1P.4.2b.3 requires separate confirmation; publication of 4AH is also a separate gate.

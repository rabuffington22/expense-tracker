# Work Block 4BG: Cash Flow Financial-Behavior Coverage

Date: 2026-07-25

Status: stopped at confirmed product-boundary mismatch; no repair or publication

## Confirmed Scope

Task 1P.7.4 plus only its focused Task 2 / `P3-3C-C01` regression slice, using temporary Personal, BFM, and Luxe Legacy databases, denied networking, and the accepted rule that Personal/BFM sibling Cash Flow sections are visible but read-only.

## Verification Before The Stop

- Active Runway OS state, JSON validation, dashboard refresh, health check, generated state, and rendered dashboard inspection: passed.
- Local branch `codex/cashflow-read-model-coverage`: created from aligned `main`.
- Baseline `.venv/bin/python scripts/smoke_test.py`: passed completely, including maintained sections 8j and 8k.
- Disposable all-entity collision probe: ran with no Plaid credentials, denied outbound networking, and a temporary `DATA_DIR`.

## Confirmed Mismatch

The probe created one synthetic bank account in each entity with the same local SQLite ID. The Personal Cash Flow response contained the BFM account and exposed it through the editable card action. Submitting the BFM card's ID and hidden BFM entity value while Personal remained the active cookie entity returned the normal redirect, changed the same-ID Personal balance, left the intended BFM balance unchanged, and left Luxe Legacy unchanged.

The account and recurring mutation routes use `g.entity_key` from the active cookie and do not bind the submitted sibling entity value. The shared template renders the same editable controls for primary and sibling sections. This violates the confirmed read-only shared-visibility contract and creates a silent same-ID misrouting risk.

## Stop And Boundaries

4BG stopped immediately under its confirmed product-mismatch condition. No maintained test or product source was changed. No repair, migration, dependency, category, authentication, CSRF, CSP, browser/PWA, Plaid, protected-data, real-database, credential, production/demo, external, downstream, GitHub, workflow, Fly, deployment, or preserved-file action occurred.

The disposable probe root was removed. The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log remained untouched.

## Result

Task 1P.7.4 is not complete. The next valid decision is a separately proposed Cash Flow entity-boundary repair block that makes sibling sections truly read-only or adopts another explicit Ryan-approved mutation contract, then adds the maintained 4BG coverage after repair.

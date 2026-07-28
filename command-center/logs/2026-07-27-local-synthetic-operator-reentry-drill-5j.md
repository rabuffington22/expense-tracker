# Work Block 5J — Local Synthetic Operator Re-entry Drill

Date: 2026-07-27

Status: complete locally under the automated dashboard-closeout rule

## Confirmed Scope

Task 3.3 (`P5-T33`) only. Follow the 5I operator runbook through local source-defined safety, full smoke, complete installed-browser, cleanup, preservation, evidence, and dashboard steps. Stop without repair or blind retry if any gate fails.

Tasks 3.4-3.5, product or test correction, external currentness, protected data, credentials, real databases, direct application or seeder execution, publication, workflow action, merge, deployment, production, and every other sequel remain excluded.

## Baseline

- Branch: `codex/ask-opus-privacy`.
- Head: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- Git index: empty.
- Existing 5H and 5I changes are the accepted dirty-worktree baseline.
- The three preserved unrelated files retain their accepted hashes.
- Product and maintained-test files were hashed before the drill so any mutation can be detected.

## Authorized Drill

1. Validate the tracked Synthetic CI and Fly safety contract locally.
2. Run the full smoke suite with its temporary synthetic `DATA_DIR`.
3. Run the complete installed-Chrome suite with temporary synthetic Personal, BFM, and Luxe Legacy data, both authentication modes, ephemeral localhost, blocked non-localhost browser requests, and exact cleanup.
4. Permit the smoke suite's internal demo-seeder subprocess only within its source-defined disposable temporary directory; never invoke the seeder directly.
5. Record sanitized pass/failure evidence and update only the runbook/matrix validation status plus Runway OS.

## Boundary

5J authorizes no repair, external observation, protected access, direct operational command, product/test/workflow/configuration change, staging, publication, merge, deployment, production, or Task 3.4 work.

## Verification Result

- `.venv/bin/python scripts/ci_safety_check.py` passed the Synthetic CI and Fly Deploy safety contracts.
- `.venv/bin/python scripts/smoke_test.py` passed on its first and only run.
- Smoke used `/var/folders/.../expense_smoke_<random>` as its temporary synthetic `DATA_DIR`; created only synthetic Personal, BFM, and Luxe Legacy databases; exercised its internally guarded disposable demo-seed proof; denied networking at the maintained seams; and completed its exact cleanup assertions.
- `.venv/bin/python scripts/mobile_drawer_browser_test.py` passed on its first and only run.
- The browser suite covered configured-auth and no-password modes, ephemeral localhost, synthetic entity data, blocked non-localhost requests, console/page errors, PWA and cache boundaries, mocked Plaid and AI seams, UI routes and mutations, and exact temporary-data/server cleanup.
- Product and maintained-test hashes were identical before and after the drill.
- The three preserved unrelated files retained their accepted hashes.
- Branch `codex/ask-opus-privacy`, head `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`, and the empty Git index remained unchanged.
- No `.env`, credential, real database, row-level data, external surface, GitHub/PR/workflow currentness, provider account, publication, merge, deployment, or production state was accessed.
- No product, test, workflow, dependency, runtime, configuration, migration, substantive README, or defect-repair change was needed.

The source-defined local re-entry path is locally verified. Automated JSON, dashboard refresh, generated-state equality, health, exactly-one-current-task, generated-marker, relevant-diff, whitespace, sensitive-value, scope, branch/head, empty-index, and preserved-file checks passed. Ryan directed that routine command-center closeouts no longer require his rendered-dashboard attestation; visual review is reserved for material dashboard presentation changes, insufficient automated proof, or an explicit request. Task 3.3 and 5J are complete locally. Mutable external state, protected procedures, publication, deployment, production, Task 3.4, and Task 3.5 remain unverified and separately gated.

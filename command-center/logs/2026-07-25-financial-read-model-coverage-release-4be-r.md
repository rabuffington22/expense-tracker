# Work Block 4BE-R — Financial Read-Model Coverage Durability

Date: 2026-07-25

Status: complete and durable on `origin/main`; no workflow or deployment

Source commit: `36007de4100b3ded048d9020403ac7d94fdbb706`

## Published Scope

The exact verified 4BE set was published through one explicit-path `[skip actions]` source commit:

- `scripts/smoke_test.py`;
- `command-center/decisions.md`;
- `command-center/index.html`;
- `command-center/now.md`;
- `command-center/roadmap.md`;
- `command-center/state.json`; and
- `command-center/logs/2026-07-24-financial-read-model-export-coverage-4be.md`.

The commit contains maintained synthetic financial read-model coverage and sanitized project-control evidence only. No product, runtime, dependency, workflow, or configuration file changed.

## Release Verification

- Full synthetic smoke suite: passed.
- Python compilation: passed.
- Maintained section 8j: passed for all-entity split replacement, signed totals, dashboard filters, seven non-recurring report families, CSV/PDF/QBO boundaries, denied networking, read-only preservation, isolation, and exact cleanup.
- JSON validation, whitespace, command-center refresh/health, generated-state review, and rendered active-dashboard inspection: passed.
- Exact changed, staged, and committed paths: seven intended paths only.
- High-confidence sensitive-addition review: no credential-shaped or protected-row additions.
- Source parent, local `main`, and pre-push live remote `main`: exact clean fast-forward from `e38cbe8ff5564293252e5ab8b5d99852033926ce`.
- Non-force push: passed.
- Local `HEAD`, local `main`, tracking `origin/main`, live remote `main`, and GitHub commit API: exact source SHA `36007de4100b3ded048d9020403ac7d94fdbb706`.
- GitHub Actions query for the source SHA: zero workflow runs.
- Fly deployment and production access: none.

## Preserved Boundaries

Tasks 1P.7.3-1P.7.4, broader Task 2, Task 3 CI, product/test expansion or repair, dependencies, migrations, browser/PWA/authentication behavior, PR creation, workflow action, deployment, production/demo/Fly access, credentials, protected data, real databases/uploads, Plaid, downstream systems, force push, and broader recovery remained excluded.

The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log were not edited, staged, deleted, or absorbed.

Tasks 1P.7.1-1P.7.2 are now durable through 4BE-R. Task 1P.7.3 returns to the next planning gate and requires a separately proposed and confirmed 4BF block.

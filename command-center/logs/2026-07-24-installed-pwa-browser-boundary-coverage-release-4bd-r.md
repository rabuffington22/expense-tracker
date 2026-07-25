# Work Block 4BD-R — Installed-PWA Browser-Coverage Durability

Date: 2026-07-24

Status: complete and durable on `origin/main`; no workflow or deployment

Source commit: `1d9f4904d0e84cc1696f7e4d89a536668a161c1e`

## Published Scope

The exact verified 4BD set was published through one explicit-path `[skip actions]` source commit:

- `scripts/mobile_drawer_browser_test.py`;
- `command-center/decisions.md`;
- `command-center/index.html`;
- `command-center/issues.md`;
- `command-center/now.md`;
- `command-center/phase-3-findings-consolidation.md`;
- `command-center/roadmap.md`;
- `command-center/state.json`; and
- `command-center/logs/2026-07-24-installed-pwa-browser-boundary-coverage-4bd.md`.

The commit contains maintained browser coverage and sanitized project-control evidence only. No product, runtime, dependency, workflow, or configuration file changed.

## Release Verification

- Full synthetic smoke suite: passed.
- Full isolated-Chrome suite: passed, including manifest/icons/installability, root worker and cross-entity offline isolation, configured-auth boundaries, exact authenticated/no-password `/k/` fields, denied networking, and cleanup.
- Python compilation, JSON validation, whitespace, command-center refresh/health, and rendered active-dashboard inspection: passed.
- Exact changed, staged, and committed paths: nine intended paths only.
- High-confidence sensitive-addition review: only generic contract terminology and synthetic authentication variable names; no secret value or protected row detail.
- Source parent, local `main`, and pre-push remote `main`: exact clean fast-forward from `4ce6a04ba22887937987212ac6b5e3328063cd0c`.
- Non-force push: passed.
- Local `HEAD`, local `main`, `origin/main`, live remote `main`, and GitHub commit API: exact source SHA `1d9f4904d0e84cc1696f7e4d89a536668a161c1e`.
- GitHub Actions query for the source SHA: zero workflow runs.
- Fly deployment and production access: none.

## Preserved Boundaries

Task 1P.7, broader Task 2, Task 3 CI, product/asset repair, PR creation, workflow action, deployment, production/demo/Fly access, credentials, protected data, real databases/uploads, Plaid, downstream systems, force push, and broader recovery remained excluded.

The pre-existing untracked `scripts/sync_prod_to_local.sh`, `command-center/now 2.md`, and duplicate 4AU log were not edited, staged, deleted, or absorbed.

Task 1P.6 and `P3-3J-C01` are now durable through 4BD-R. Task 1P.7 returns to the next just-in-time planning gate; it must be decomposed into visible subtasks before a 4BE implementation proposal.

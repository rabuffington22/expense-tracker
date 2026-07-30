# Dependency, Runtime, Action-Pin, And Toolchain Review Contract

Status: canonical Phase 6 Task 3 policy accepted locally through work block 6C-R after exact existing Python 3.14.3 discovery and one passing static workflow-safety invocation; mutable external currentness, installed packages, product behavior, hosted workflows, and production remain unverified and separately gated

## Purpose And Authority

This contract defines how The Ledger inventories, reviews, classifies, verifies, and gates maintenance of dependencies, runtimes, GitHub Action pins, runner images, deployment tools, and browser tooling. It separates:

- what tracked source declares;
- what dated historical evidence previously established;
- what an authoritative external review would need to establish now;
- what a later implementation block may change;
- what publication, hosted observation, deployment, or production verification would still require.

A source inventory is not a current-version audit. A newer version, advisory, deprecation, support boundary, runner image, installed binary, or hosted execution state is not inferred when the relevant external surface was not queried.

Ryan owns every external-currentness, risk-acceptance, dependency, runtime, workflow-pin, runner, toolchain, implementation, publication, deployment, and live-action decision. Codex may maintain this contract, inspect tracked source, run approved local static checks, and reconcile sanitized evidence inside a confirmed block.

## Canonical Tracked Inventory

| Surface | Tracked declaration | Drift form | Source evidence label | Change owner and gate |
| --- | --- | --- | --- | --- |
| Production Python runtime | [`Dockerfile`](../Dockerfile) uses `python:3.12-slim`; [`README.md`](../README.md) recommends Python 3.12 | Mutable minor-line image tag, upstream image contents, Python support, system library changes | Source-verified declaration; external currentness unverified | Ryan confirms runtime/container change; implementation, build, publication, deployment, and production verification remain separate |
| Runtime Python requirements | [`requirements.txt`](../requirements.txt) contains 11 direct bounded ranges and no lockfile | Direct release availability, compatible resolver result, transitive packages, security/support status | Source-verified constraints; resolved and external currentness unverified | Ryan confirms bounds or lock strategy; later block installs and verifies in isolation |
| Browser-test requirements | [`requirements-dev.txt`](../requirements-dev.txt) includes runtime requirements plus bounded Playwright `>=1.50.0,<2.0.0` | Playwright release and browser compatibility, transitive packages, runner Chrome | Source-verified constraints; installed and external currentness unverified | Ryan confirms test-tool change; isolated local and hosted browser proof remain separate |
| Container system packages | [`Dockerfile`](../Dockerfile) installs unversioned `build-essential` through the base distribution package manager | Base repository contents, package version, build behavior, vulnerabilities | Source-verified command; resolved image contents unverified | Ryan confirms container change; build and release proof require later blocks |
| Synthetic CI core | [`.github/workflows/synthetic-ci.yml`](../.github/workflows/synthetic-ci.yml) uses `ubuntu-latest`, Python 3.12, tracked runtime requirements, Node-provided JavaScript syntax checks, and immutable checkout/setup-python commits | Mutable runner image, runner Node/pip inventory, action release/support state, dependency resolution | Source-verified workflow; hosted and external currentness unverified | Workflow or input change requires exact Task 3 maintenance implementation and publication gates |
| Synthetic CI browser | The same workflow uses explicit `ubuntu-24.04`, Python 3.12, immutable checkout/setup-python commits, runner-installed Google Chrome, and tracked development requirements | Runner image, installed Chrome, action runtime, Playwright/Chrome compatibility | Source-verified workflow; installed runner inventory and hosted currentness unverified | Browser-tool or workflow change requires local isolated-browser proof and later hosted PR observation |
| Fly Deploy workflow | [`.github/workflows/fly-deploy.yml`](../.github/workflows/fly-deploy.yml) uses explicit `ubuntu-24.04`, immutable checkout and setup-flyctl commits, and Fly CLI `0.4.74` | Runner image, action release/runtime, CLI support and deployment compatibility | Source-verified workflow; hosted/Fly currentness unverified | Any change requires static safety proof, separate publication, exact deployment observation, and production-health authority |
| Daily Plaid Sync workflow | [`.github/workflows/daily-plaid-sync.yml`](../.github/workflows/daily-plaid-sync.yml) uses `ubuntu-latest` and runner-provided `curl`, with no third-party action | Mutable runner and curl inventory, schedule/platform behavior | Source-verified workflow; hosted runner and execution currentness unverified | Workflow, runner, command, schedule, or secret-bearing invocation change requires a separate live/operational block |
| Fly application configuration | [`fly.toml`](../fly.toml) and [`fly.demo.toml`](../fly.demo.toml) use the tracked Docker build and explicit Fly configuration | Fly platform/config schema, machine/runtime behavior, shared Docker inputs | Source-verified configuration; Fly currentness unverified | Configuration and deployment changes remain target-specific |
| Workflow safety enforcement | [`scripts/ci_safety_check.py`](../scripts/ci_safety_check.py), [`synthetic-ci-safety-contract.md`](synthetic-ci-safety-contract.md), and [`fly-deploy-safety-contract.md`](fly-deploy-safety-contract.md) freeze reviewed workflow structure and selected inputs | Checker/contract drift when workflows or declared inputs change | Source-verified and locally checkable | Checker or contract correction must travel with the exact authorized workflow change |
| Command-center JavaScript tooling | Tracked Node scripts refresh and verify Runway OS; Synthetic CI uses the runner-provided Node executable for JavaScript syntax | Local/runner Node version and behavior | Source-verified scripts; installed and runner currentness unverified | Tool-version declaration or script change requires a scoped command-center/tooling block |

No current registry, support, advisory, image, runner, Chrome, Fly, Python, pip, Node, package, or hosted-workflow claim follows from this table.

## Reproducibility And Mutability Boundary

The repository currently combines several maintenance strategies:

- direct Python requirements use bounded ranges rather than exact locks;
- compatible transitive versions are selected when installation occurs;
- the production Python image uses a mutable minor-line tag rather than a digest;
- some GitHub runners use explicit `ubuntu-24.04`, while others use mutable `ubuntu-latest`;
- third-party GitHub Actions are pinned to immutable full commits;
- Fly CLI is pinned to an exact version in the deploy workflow;
- Chrome is supplied by the runner image, while Playwright is selected from a bounded requirement range;
- pip, Node, `curl`, and system packages are supplied implicitly by an environment or base image.

These are drift surfaces, not automatic defects. Task 3 records and reviews them. Whether to introduce a lockfile, image digest, explicit tool setup, newer runtime, different runner, or updater is a separate Ryan decision with its own implementation and release cost.

## Review Cadence

| Review | Intended cadence | Stale threshold | Allowed scope | Required result |
| --- | --- | --- | --- | --- |
| Tracked-source inventory | Monthly and after any relevant tracked source change | No passing inventory within 35 days | Local tracked files and static contracts only | Exact inventory, diff, labels, known mutable inputs, and next gate |
| Authoritative external currentness | Quarterly in a separately confirmed read-only block | No passing review within 100 days | Official package, runtime, action, runner, browser, container, Fly, and security sources explicitly named by the block | Dated comparison against tracked declarations, limitations, classification, and no-update confirmation |
| Pre-change review | Before implementing any dependency, runtime, workflow-pin, runner, browser, container, or deployment-tool change | Missing exact source/currentness evidence for the proposed change | Exact affected family only | Frozen baseline, proposed target, rationale, compatibility plan, verification, rollback, and publication boundary |
| Post-change source reconciliation | After a confirmed local implementation | Any unrecorded changed declaration, checker, contract, or test requirement | Exact changed files and local evidence | Updated inventory, unchanged exclusions, result, and next publication gate |
| Event-driven review | On a credible security advisory, action-runtime deprecation, runner-image change, runtime EOL notice, container/build failure, deployment-tool failure, or Chrome/Playwright incompatibility | Trigger remains unclassified | Exact affected family; external access only when separately authorized | Evidence label, classification, impact boundary, and smallest next decision |

Cadence does not create automation or authorize external queries. When an external review is due but not authorized, record `due` or `waiting-on-Ryan`; do not guess currentness.

## Risk Classification

Every finding receives exactly one primary classification:

### Security-critical

A credible vulnerability, compromised or untrusted supply-chain input, unsupported security boundary, exposed secret path, or security fix required for safe operation.

- State: `decision-needed`.
- Evidence: authoritative advisory or verified local contract failure, affected source, exposure boundary, and uncertainty.
- Boundary: stop before upgrade, mitigation, publication, deployment, or secret action.

### Compatibility-risk

An action-runtime deprecation, approaching runtime EOL, runner removal/change, breaking package/tool transition, failed build/deploy input, or browser/test-tool mismatch.

- State: `decision-needed`.
- Evidence: authoritative notice or exact failure, affected workflow/runtime, expected deadline or break point, and verification needs.
- Boundary: stop before changing declarations or retrying a failed hosted/live path.

### Maintenance-available

A newer compatible version or maintenance opportunity exists without demonstrated security or compatibility urgency.

- State: `planned`.
- Evidence: authoritative version comparison, scope, likely benefit, migration cost, and known constraints.
- Boundary: no automatic upgrade, lockfile, updater, or publication.

### Unknown-currentness

Tracked declarations are known, but the required external, installed, runner, image, support, or advisory evidence was not queried or is stale.

- State: `due` or `waiting-on-Ryan`.
- Evidence: exact missing surface and last valid label, if any.
- Boundary: absence of evidence is not a defect and never authorizes a query or change.

Task 4 owns phase-wide prioritization, retained-risk acceptance, and recurring triage. Task 3 supplies consistently classified evidence without making those governance decisions.

## Evidence Minimum

Each review record must include:

1. exact review type and authority;
2. Central Time start and completion;
3. exact tracked source paths and source ref when relevant;
4. declared versions, ranges, pins, runner labels, image tags, or implicit inputs;
5. evidence label for each surface;
6. external sources and query count only when the block authorizes them;
7. comparison result and stale-threshold calculation;
8. one primary risk classification;
9. affected change family and verification path;
10. what the evidence does not prove;
11. smallest next authorization gate;
12. confirmation that no installation, update, workflow action, publication, deployment, or remediation followed unless separately authorized.

Do not record credentials, tokens, environment dumps, protected data, real financial inputs, secret values, or unnecessary installed-package inventories.

## Change-Family Gates

Findings never authorize implementation. Each family requires a separately confirmed block:

### Python requirements or lock strategy

- Freeze exact current constraints and authoritative evidence.
- Decide whether bounds, direct pins, constraints files, or a lock artifact are intended.
- Resolve and install only in a disposable environment with approved network access.
- Run focused checks plus full smoke and browser coverage when compatibility can affect product behavior.
- Keep publication and production release separate.

### Python runtime, container base, or system packages

- Freeze the exact runtime/image target and upstream support evidence.
- Review application and native-build compatibility.
- Build only inside a confirmed container/runtime block.
- Run maintained synthetic coverage and inspect build output without protected data.
- Publish and deploy only through later exact release gates.

### GitHub Actions, runner images, or workflow inputs

- Verify official ownership, immutable commit, declared action runtime, runner compatibility, permissions, credential persistence, commands, network, timeout, and secrets boundary.
- Update the workflow, matching safety contract, and fail-closed checker together.
- Run local static safety and required synthetic suites.
- Publish separately, then use an exact no-merge PR observation when hosted proof is required.
- Never infer that a passing local checker authorizes a workflow run, merge, or deployment.

### Fly setup action, Fly CLI, or deploy configuration

- Review the combined checkout pin, setup-flyctl pin, CLI version, runner, deployment command, and Fly configuration.
- Preserve read-only repository permission and non-persistent checkout credentials.
- Require separate publication, exact automatic deployment observation, and credential-free health authority.
- Stop before manual dispatch, rerun, repair, secret, console, or production mutation.

### Chrome, Playwright, or browser-runner inputs

- Review Playwright/Chrome compatibility and runner availability.
- Preserve installed-Chrome use, denied non-localhost requests, synthetic temporary data, both authentication modes, and exact cleanup.
- Run the complete isolated browser suite for a local change and use a separate hosted PR observation when required.
- Do not download or install another browser unless the confirmed block explicitly changes the contract.

### Implicit pip, Node, curl, or other environment tools

- First decide whether the tool should remain environment-supplied or become explicitly declared.
- Record the compatibility and reproducibility reason.
- Change setup and safety enforcement only inside the exact affected workflow/runtime block.

## Local Static Review

The existing static checker is the only product-adjacent command required for local contract acceptance:

```bash
.venv/bin/python scripts/ci_safety_check.py
```

It validates the source-defined Synthetic CI and Fly Deploy safety contracts. The preferred project-environment path was absent during 6C, so separately confirmed 6C-R established an exact existing Python 3.14.3 executable and invoked the checker once through that path. Both contract messages passed. This does not query registries, GitHub, Fly, runner images, installed Chrome, security advisories, packages, or production. The pass proves only that the tracked workflows still match the maintained local contracts.

Product smoke, browser suites, package installation, container builds, installed-version inventory, hosted workflows, and production verification are not needed for policy-only 6C.

## Authorization Ladder

Each rung is separately confirmed:

1. tracked-source inventory and policy maintenance;
2. authoritative external-currentness review for exact named surfaces;
3. Ryan classification/priority or retained-risk decision when needed;
4. local implementation for one exact change family;
5. local compatibility and safety verification;
6. Git publication and hosted CI observation;
7. deployment and production verification.

Passing one rung supplies evidence only and never activates its successor.

## 6C Stop Boundary

Work block 6C drafted this contract from tracked source and sanitized historical evidence only. The required local static check was invoked exactly once through `.venv/bin/python scripts/ci_safety_check.py`; the shell returned status 127 because that interpreter path does not exist, so the checker did not run. The block stopped without substituting an interpreter, installing or repairing an environment, or retrying.

6C performed no registry, GitHub, runner, Python-support, Chrome, Fly, Docker-registry, advisory, installed-environment, package-resolution, container-build, hosted, protected, or production query. It changed no requirement, lockfile, runtime, image, workflow, action pin, runner, Fly input, browser tool, product code, test, or maintained README. It created no updater or automation and performed no staging, commit, push, PR, merge, publication, deployment, delegation, or second opinion.

## 6C-R Acceptance Evidence

Work block 6C-R preserved the stopped 6C boundary and performed only bounded local recovery:

- `python3` resolved to an existing executable that identified its exact real path as `/opt/homebrew/Cellar/python@3.14/3.14.3_1/Frameworks/Python.framework/Versions/3.14/bin/python3.14`;
- the metadata probe reported Python `3.14.3`, satisfying the confirmed Python 3.9 minimum;
- tracked requirements, Docker/Fly inputs, workflows, checker, browser safety input, and local safety contracts showed no Git diff before invocation;
- the checker was invoked exactly once through that executable;
- `Synthetic CI safety contract passed` and `Fly Deploy safety contract passed` were both returned with status zero.

This exact interpreter path is machine-specific evidence, not a new repository runtime requirement or a replacement for the preferred project environment. No package inventory, installation, repair, retry, external query, product execution, container build, workflow or toolchain change, publication, deployment, protected access, or Task 4 action occurred. Task 3 is locally accepted; external currentness and every future change family remain separately authorized.

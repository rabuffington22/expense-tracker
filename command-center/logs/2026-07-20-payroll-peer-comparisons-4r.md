# Work Block 4R: Like-For-Like Payroll Peer Comparisons

Date: 2026-07-20

Status: complete and verified locally; release not authorized

## Scope

Implement Phase 4 Task 1M.5 and only the focused Task 2 coverage slice for `P3-3F-03` and `P3-3F-C01`. Keep hourly and salary cohorts separate without annualization, make zero and empty states explicit, and preserve BFM-only and protected-data boundaries.

## Result

- Active peers are grouped by maintained role and `pay_type`.
- The selected employee and inactive or terminated rows never contribute to the average.
- An inactive selected employee may compare against current active peers in the same cohort.
- `peer_avg_cents` is an integer when peers exist, including `0` for a real zero average, and `null` when no comparable peer exists.
- `peer_count` reports the number of contributing peers.
- The modal labels the value as the same-role and same-pay-type peer average, preserves `/hr` and `/yr`, and displays `No comparable peers` for an empty cohort.

## Verification

- Baseline `.venv/bin/python scripts/smoke_test.py`: pass.
- Final `.venv/bin/python scripts/smoke_test.py`: pass, including new maintained section 8b4.
- Python compilation for `web/routes/payroll.py` and `scripts/smoke_test.py`: pass.
- Mixed hourly/salary, multiple-peer, self-exclusion, inactive-contributor, inactive-selected, zero-rate, single-member/empty, response-contract, rendered-label/unit, BFM-only, denied-network, all-entity isolation, and exact-cleanup checks: pass.
- Disposable localhost browser using only synthetic temporary BFM rows: hourly target rendered `$30.00/hr`; salary target rendered `$120,000/yr`; single-member cohort rendered `No comparable peers`.
- Disposable application server stopped and exact temporary database directory removed.
- JSON validation, `git diff --check`, dashboard refresh, command-center health, rendered-dashboard inspection, and final worktree scope: pass.

## Boundaries Preserved

- No real payroll/HR or financial rows, retained uploads, credentials, authenticated production pages, production/demo systems, external calls, workflows, Fly actions, downstream access or writes, migration, historical cleanup, GitHub durability, commit, push, PR, merge, or deployment.
- Employee import, identity, deletion, validation, pay history, and payroll-entry calculations remain unchanged.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remain untouched and unstaged.

## Learning

The misleading value came from two independent ambiguities: the code grouped unlike compensation units and also counted the selected employee as their own peer. Separating by role and pay type was necessary but not sufficient; using an explicit empty value was also required so a genuine zero-rate cohort does not disappear. The payroll repair family is now covered end to end locally, and the next decision is whether to publish 4R before planning Task 1N.

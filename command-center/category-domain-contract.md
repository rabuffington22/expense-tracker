# Category-Domain Contract

Date: 2026-07-19
Work block: 4O — Deterministic Category-Domain Enforcement

## Authority

`categories.md` is the tracked source of truth for each entity's valid category and subcategory pairs. Runtime database category rows may retain historical or orphaned values for separate review, but they do not authorize new classification writes.

## Inference

- Vendor inference receives the target entity explicitly.
- A candidate is returned only when both its category and subcategory exist in that entity's maintained definition.
- Empty or `Unknown` subcategories normalize to the implicit `General` subcategory.
- An unmapped or entity-invalid candidate becomes `Needs Review` / `General`; inference does not invent an entity-specific replacement.
- Henry Schein primary categories are ranked by frequency. Equal-frequency candidates are ordered by normalized alphabetical name, independent of hash seed.

## Accepted Writes

- Transaction-review batches are fully validated before the first transaction or alias mutation. One invalid pair rejects the entire batch.
- Vendor-order categorization validates before updating or advancing the queue.
- Accepted order matches validate every supplied category pair before changing a transaction or marking any order matched.
- A valid non-empty category always stores a valid maintained subcategory; empty and `Unknown` input normalize to `General`.
- The dedicated vendor-queue `Skipped` action remains a workflow sentinel. It cannot be inferred or submitted as a financial category.

## Rejection And Isolation

Invalid input must leave transactions, orders, match relationships, notes, and merchant aliases unchanged. Validation is scoped to the selected entity, and tests use only temporary synthetic Personal, BFM, and Luxe Legacy databases with outbound networking denied.

## Explicit Exclusions

This contract does not add, rename, or remove categories; inspect or repair existing invalid rows; change orphan-remediation behavior; add a migration; access real financial data; or authorize commit, push, deployment, or live-system actions.

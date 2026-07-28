# 5G-R2 Recurring Review Exact-Head Production Release

Date: 2026-07-27

Status: complete

## Authorized Scope

Ryan confirmed Phase 5 Task 4.1 (`P5-T41`) only for exact hosted-state preflight, PR #90 ready transition and merge, observation of the resulting automatic exact-SHA Fly deployment, one credential-free production health request, sanitized local evidence, and automated Runway OS closeout.

Ask Opus durability, provider verification, Ask release, later Task 4 work, parked Task 2 work, local publication, manual workflow or deployment action, Fly administration, protected data, repair, rollback, branch deletion, and parent-project updates remained excluded.

## Local Preservation

- Local branch: `codex/ask-opus-privacy`.
- Local HEAD: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- Real Git index: empty before and after the release chain.
- The accepted dirty worktree remained local, unstaged, uncommitted, and unpublished.
- Preserved unrelated file hashes:
  - `command-center/logs/2026-07-23-categorization-upload-style-compatibility-4au 2.md`: `6f8f616fa8f62fcac3e7901df37ed490c9e39f31fd9d4eb022cf030dadb65fe3`
  - `command-center/now 2.md`: `5c29bc7e5312c565791afd56940211e49f91cda3e936d3120a7f978bd10b0eb2`
  - `scripts/sync_prod_to_local.sh`: `cd4e415da356e11b80437a098ba1ff3a7fed7f9f03aaa8c22f9b2e6617d61226`

## Exact Hosted Preflight

- Remote `main`: `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`.
- PR #90: open, draft, unmerged, clean, and mergeable.
- Base: `main` at the exact remote-main SHA.
- Head branch: `codex/recurring-review-surface`.
- Head SHA: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- Synthetic CI run `30279361029`: completed successfully for the exact head.
- Core job `90021492054`: successful, with every step successful.
- Browser job `90021772511`: successful, with every step successful.
- Exact-head annotations: zero.
- Marking the PR ready created no additional Synthetic CI run; the exact successful head remained unchanged.

## Merge And Release Evidence

- PR #90 was marked ready and merged with a normal merge commit without protection bypass.
- Merge SHA: `d81ed7078e741a0c7613e7898312ce01cd359f45`.
- First parent: `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`.
- Second parent: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- Remote `main` advanced to the exact merge SHA.
- Remote `codex/recurring-review-surface` was retained at the exact PR head.
- One automatic push-triggered Fly Deploy run exists for the merge: `30327566484`.
- Deploy job `90176026100` and every step completed successfully.
- Deployment annotations: zero.
- Exactly one Fly Deploy run was returned for the merge SHA.
- The single authorized credential-free request to `https://ledger-oak.fly.dev/health` returned HTTP `200` with `{"status":"ok"}`.

## Result And Boundary

Recurring Review is durable, hosted-verified, merged, deployed, and production-health-verified at the dated 5G-R2 checkpoint. No second deployment, manual workflow action, Fly administration, credential, protected-data access, local publication, repair, rollback, or excluded sequel occurred.

Task 4.1 is complete. Task 4.2 is the next Ryan-owned planning gate for exact Ask Opus and Task 3 durability packaging; this record grants no authority for that work.

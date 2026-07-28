# Phase 5 Release-Evidence And Unresolved-Gates Map

Date: 2026-07-27

Status: reconciled through the clean 5H-R candidate; final closeout-head hosted verification pending

## Evidence Labels

- **Local-only** — present only in the current working tree.
- **Durable** — present in an identified commit or ref.
- **Hosted-verified** — tied to an exact GitHub PR or workflow result.
- **Merged** — present in the exact current remote `main` ancestry.
- **Deployed** — tied to an exact successful deployment workflow run.
- **Historical production-verified** — a dated authorized observation established minimal production health then, not now.
- **Externally unverified-current** — the mutable external surface was not queried in 5K.
- **Protected** — provider, credential, financial, or another closed surface.
- **Pending** — required evidence or authority is absent.

These labels are cumulative only when the cited evidence establishes each step. A successful CI run does not imply merge or deployment, and a historical health result does not establish current health.

## Current Refs And Hosted Records

| Surface | Exact evidence | Classification | Meaning |
| --- | --- | --- | --- |
| Ask and operator candidate | `codex/ask-opus-privacy` at `f7482a95e754160905a79ec0130ef8faf0a48784`; draft PR #91; candidate CI `30329875129`; zero annotations and zero deployment | Durable and hosted-verified candidate | The exact 31-path Ask, test, operator, monitoring, handoff, and evidence package is reviewable; final closeout-head verification remains pending. |
| Remote `main` | `d81ed7078e741a0c7613e7898312ce01cd359f45` | Durable and merged | Current hosted `main` is the exact PR #90 merge. |
| PR #89 | merged 2026-07-27; head `13d2f16a9cca8b8d4fb4900006dfaa9655824474`; merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce` | Hosted-verified and merged | This is the released Phase 5 usability-set path. |
| PR #89 Synthetic CI | run `30262719321` on `13d2f16a9cca8b8d4fb4900006dfaa9655824474`; core job `89966154249`; browser job `89966350270`; success; zero annotations | Hosted-verified | Exact activation head passed ordered core and browser checks. |
| PR #89 Fly Deploy | run `30263216876` on merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce`; job `89967738107`; success; zero annotations | Deployed | This is the newest successful hosted Fly Deploy workflow record returned for `main` in 5K. |
| PR #89 production observation | authorized 5F-R2 `/health` returned minimal `status: ok` after run `30263216876` | Historical production-verified | Establishes the post-deploy observation on 2026-07-27 only. Current service health was not queried in 5K. |
| Recovery record | commits `77236737c7e8218e8570bb3a358e2d83db054945` and closeout `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb` on current `main` | Durable and merged; not deployed | Both are later `[skip actions]` command-center records. They do not assert database currentness or trigger a deployment. |
| PR #90 | ready and merged; head `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`; merge `d81ed7078e741a0c7613e7898312ce01cd359f45` | Durable, hosted-verified, and merged | Recurring Review is released through the exact normal merge commit. |
| PR #90 Synthetic CI | candidate run `30278240194` on `182cabd73640bfd6f8ce754740b5b20bbfc045dd`; current-head run `30279361029` on `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`; current core job `90021492054`; current browser job `90021772511`; success; zero annotations | Hosted-verified | Both the product candidate and the final command-center closeout head passed. |
| PR #90 Fly Deploy | run `30327566484` on merge `d81ed7078e741a0c7613e7898312ce01cd359f45`; job `90176026100`; success; zero annotations; exactly one run for the merge | Deployed | The exact merge triggered one automatic deployment. |
| PR #90 production observation | one authorized `/health` request returned HTTP 200 and `status: ok` after run `30327566484` | Historical production-verified | Establishes the dated post-deploy health checkpoint for 5G-R2. |
| OpenRouter account controls | no account or provider access in 5K | Protected and pending | Local request controls are not evidence of mutable account settings. |

5K hosted metadata was read-only. Separately confirmed 5G-R2 later performed the exact ready transition, merge, automatic deployment observation, and one health request recorded above; it used no manual workflow action or Fly administration.

## Phase 5 Block Inventory

| Block | Outcome | Best supported classification | Release consequence |
| --- | --- | --- | --- |
| 5A | Synthetic cross-surface baseline | Merged and deployed through PR #89 / 5F-R2 | Included in the released usability set. |
| 5B | Claude Design critique and findings intake | Merged and deployed through PR #89 / 5F-R2 | Planning/evidence artifacts are in the released set; reviewer opinion is not product authority. |
| 5C | Demo-fidelity implementation and proof | Merged and deployed through PR #89 / 5F-R2 | Included in the released usability set. |
| 5D | Luxe Legacy setup path | Parked; pending | No implementation or release evidence. |
| 5E | Phone transaction clarity | Merged and deployed through PR #89 / 5F-R2 | Included in the released usability set. |
| 5F | Dashboard category signal and density | Merged and deployed through PR #89 / 5F-R2 | Included in the released usability set. |
| 5F-R | First publication attempt | Stopped locally | No commit or hosted consequence from this attempt. |
| 5F-W | Evidence whitespace/provenance normalization | Durable, hosted-verified, merged, and deployed through PR #89 / 5F-R2 | Cleared the local publication prerequisite. |
| 5F-RR | Candidate publication and draft PR #89 verification | Durable and hosted-verified; superseded by 5F-R2 | Candidate evidence led to the exact activation head. |
| 5F-R2 | PR #89 activation, merge, deploy, and bounded health | Merged, deployed, and historical production-verified | Exact release evidence is complete for the first usability set. |
| 5G | Recurring Review implementation | Merged, deployed, and historical production-verified through PR #90 / 5G-R2 | Included in the released Recurring Review set. |
| 5G-RA | Initial recovery assessment | Stopped at permission boundary | No snapshot/database claim beyond the sanitized stop. |
| 5G-RC | Exact Personal/BFM local recovery | Protected historical local evidence | Does not establish current database or production state. |
| 5G-RC-R | Recovery record durability | Durable and merged on current `main`; not deployed | Command-center record only. |
| 5G-AV | First application-verification route | Stopped at browser-policy boundary | Superseded by the separately authorized recovery verification. |
| 5G-AV-R | Protected-copy application verification | Protected historical local evidence | Established the authorized local verification then, not current data state. |
| 5G-RS | Synthetic and rendered Recurring Review re-verification | Merged and deployed through PR #90 / 5G-R2 | Supports the released Recurring Review set. |
| 5G-R | Branch durability and hosted review | Merged and deployed through PR #90 / 5G-R2 | Superseded by the exact release evidence. |
| 5G-R2 | PR #90 ready transition, merge, deploy, and bounded health | Merged, deployed, and historical production-verified | Exact Recurring Review release evidence is complete. |
| 5H-A | Ask Opus data-handling audit | Local-only | Contract evidence is not published. |
| 5H-B | Ask Opus privacy implementation | Candidate-durable and hosted-verified through 5H-R | Provider verification, final closeout head, merge, and release remain separate. |
| 5I | Operator runbook and monitoring matrix | Candidate-durable and hosted-verified through 5H-R | Included in draft PR #91; not merged or deployed. |
| 5J | Local synthetic operator re-entry drill | Candidate-durable and hosted-verified through 5H-R | The evidence is durable on draft PR #91; no production claim. |
| 5K | Release-evidence reconciliation | Candidate-durable and hosted-verified through 5H-R | Included in draft PR #91; later evidence overrides its dated hosted facts. |
| 5L | Maintained documentation and release handoff | Candidate-durable and hosted-verified through 5H-R | Included in draft PR #91; not merged or deployed. |
| 5H-R | Ask and operator package durability | Candidate head hosted-verified; closeout head pending | Exact 31-path candidate passed; final exact eight-path closeout gate remains. |

The detailed block definitions and sanitized evidence paths remain in [`roadmap.md`](roadmap.md), [`state.json`](state.json), and the dated [`logs/`](logs/) directory.

## Release Packages

### Released usability set

- Scope: 5A, 5B, 5C, 5E, 5F, and the 5F-W normalization carried by PR #89.
- Exact release path: activation `13d2f16a9cca8b8d4fb4900006dfaa9655824474` → merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce` → Fly Deploy run `30263216876`.
- Current `main` ancestry: merge plus `3ffd94bafc2eba375a795ed3e5df26e3615e79c4`, `77236737c7e8218e8570bb3a358e2d83db054945`, and `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb`.
- Boundary: deployment and dated health are established; current production health remains externally unverified.

### Recurring Review

- Exact hosted head: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- PR #90: ready and merged as `d81ed7078e741a0c7613e7898312ce01cd359f45`.
- Exact current-head CI: run `30279361029`, both jobs successful, zero annotations.
- Exact release: Fly Deploy run `30327566484`, job `90176026100`, every step successful, zero annotations, exactly one deployment, and dated HTTP 200 `status: ok` health evidence.
- Boundary: durable, hosted-verified, merged, deployed, and historical production-verified through 5G-R2.

### Ask Opus and operator handoff

- The exact Ask Opus privacy implementation, maintained tests, operator runbook, monitoring matrix, drill evidence, release map, handoff, and Runway OS package is candidate-durable on draft PR #91 at `f7482a95e754160905a79ec0130ef8faf0a48784`.
- Candidate Synthetic CI `30329875129` passed both ordered jobs with zero annotations and zero deployment.
- Boundary: final closeout-head hosted verification, provider verification, merge, deployment, production, and later release decisions remain separate.

## Unresolved Gates

| Gate | Current state | Exact evidence needed to clear it | Authority |
| --- | --- | --- | --- |
| Task 3.5 maintained documentation and compact handoff | Pending; sole current planning task | Confirmed 5L scope, source-linked corrections, local verification, and a compact release handoff | Ryan confirms a separate block |
| Recurring Review merge and production release | Complete through 5G-R2 | No further release action; use the exact merge, deploy, and dated health evidence above | Complete |
| Ask Opus durability/publication | Candidate-durable on draft PR #91; final closeout head pending | Exact closeout commit and automatic final-head CI with zero annotations and zero deployment | Confirmed 5H-R |
| OpenRouter account-setting verification | Protected and pending | Human-completed provider-account observation of the exact logging/use/privacy settings, recorded without secrets or financial content | Ryan at a protected handoff |
| Ask Opus production use | Not authorized | Durable implementation, protected provider-setting evidence, explicit release authority, exact deployment evidence, and separately authorized production observation | Ryan |
| Current production/demo health | Externally unverified-current | A separately authorized credential-free observation tied to a stated target and purpose | Ryan |
| Parked Tasks 2.2, 2.7, and 2.8 | Parked | Explicit reopening and a new bounded proposal | Ryan |
| Final Task 4 durability and parent pointer | Pending | Exact target-repo package and publication state after Tasks 3.5 and release decisions; separately scoped parent update | Ryan |

## Reconciliation Conclusion

There is no blocking contradiction between local Git, current remote `main`, PR #89, PR #90, or the exact workflow records. The key split is not “verified versus unverified”; it is:

1. the first usability set is merged, deployed, and historically health-verified;
2. Recurring Review is merged, deployed, and historically health-verified through 5G-R2;
3. Ask Opus and the operator/release-handoff artifacts are candidate-durable and hosted-verified on draft PR #91, with final closeout-head verification pending;
4. provider settings remain protected, and the dated health result does not create continuous-currentness evidence.

Task 3.4 is complete on that factual basis. Every publication, provider, merge, deployment, production, Task 3.5, and Task 4 action remains separately gated.

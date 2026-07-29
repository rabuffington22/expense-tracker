# Phase 5 Release-Evidence And Unresolved-Gates Map

Date: 2026-07-29

Status: reconciled through 5R-R exact release-closeout recovery; required Phase 5 work is 100% complete, Task 2.8 is released, optional Tasks 2.2 and 2.7 remain parked, and no successor is active

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
| Ask and operator package | candidate `f7482a95e754160905a79ec0130ef8faf0a48784`; hosted closeout `257bec901e88b830fcafe6067c8174cd6a5213b6`; release head `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`; CI runs `30329875129` and `30330294465`; exact release run `30350587286` | Durable, hosted-verified, merged, deployed, and historical production-verified | The exact Ask, test, operator, monitoring, handoff, evidence, and closeout package is released through 5H-R2. |
| Remote `main` before 5M target publication | live GitHub `main` at `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`; sole parent `257bec901e88b830fcafe6067c8174cd6a5213b6`; exactly one commit and nine command-center paths ahead | Durable and merged | This is the exact application release head observed by 5H-R2 and the parent of the command-center-only 5M target closeout. |
| Final target and parent durability | parent `main` commit `391debe28ea58349c65312eeb0987e9b516babd9`; target containing commit `Complete target and parent durability closeout [skip actions]`; exact twelve target command-center paths | Parent durable; target durable through containing commit after post-push conditions pass | The parent keeps only a sanitized pointer and reusable lesson. The target owns detailed state and evidence. Exact target live-main alignment plus zero workflow, check, and deployment results are verified after the containing push and reported from that commit. |
| PR #91 | closed and classified merged at 2026-07-28 10:23 UTC; recorded head and merge SHA `257bec901e88b830fcafe6067c8174cd6a5213b6`; returned metadata still marked draft | Hosted-verified and merged by ancestry | GitHub recognized the exact branch head on `main` after the separately authorized fast-forward push; 5H-R2 made no PR mutation. |
| Ask release Fly Deploy | automatic push run `30350587286` on `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`; job `90246858468`; every returned step successful; zero annotations; exactly one push-event run for the SHA | Deployed | The exact direct-main release triggered one clean automatic Fly deployment. |
| Ask release production observation | one authorized credential-free `/health` request returned HTTP 200 and `status: ok` after run `30350587286` | Historical production-verified | Establishes the dated minimal post-deploy health checkpoint for 5H-R2 only. |
| PR #89 | merged 2026-07-27; head `13d2f16a9cca8b8d4fb4900006dfaa9655824474`; merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce` | Hosted-verified and merged | This is the released Phase 5 usability-set path. |
| PR #89 Synthetic CI | run `30262719321` on `13d2f16a9cca8b8d4fb4900006dfaa9655824474`; core job `89966154249`; browser job `89966350270`; success; zero annotations | Hosted-verified | Exact activation head passed ordered core and browser checks. |
| PR #89 Fly Deploy | run `30263216876` on merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce`; job `89967738107`; success; zero annotations | Deployed | This is the newest successful hosted Fly Deploy workflow record returned for `main` in 5K. |
| PR #89 production observation | authorized 5F-R2 `/health` returned minimal `status: ok` after run `30263216876` | Historical production-verified | Establishes the post-deploy observation on 2026-07-27 only. Current service health was not queried in 5K. |
| Recovery record | commits `77236737c7e8218e8570bb3a358e2d83db054945` and closeout `7d8ce1a33814c378b89f2a9ed4d6d85dbe8b1eeb` on current `main` | Durable and merged; not deployed | Both are later `[skip actions]` command-center records. They do not assert database currentness or trigger a deployment. |
| PR #90 | ready and merged; head `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`; merge `d81ed7078e741a0c7613e7898312ce01cd359f45` | Durable, hosted-verified, and merged | Recurring Review is released through the exact normal merge commit. |
| PR #90 Synthetic CI | candidate run `30278240194` on `182cabd73640bfd6f8ce754740b5b20bbfc045dd`; current-head run `30279361029` on `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`; current core job `90021492054`; current browser job `90021772511`; success; zero annotations | Hosted-verified | Both the product candidate and the final command-center closeout head passed. |
| PR #90 Fly Deploy | run `30327566484` on merge `d81ed7078e741a0c7613e7898312ce01cd359f45`; job `90176026100`; success; zero annotations; exactly one run for the merge | Deployed | The exact merge triggered one automatic deployment. |
| PR #90 production observation | one authorized `/health` request returned HTTP 200 and `status: ok` after run `30327566484` | Historical production-verified | Establishes the dated post-deploy health checkpoint for 5G-R2. |
| OpenRouter account controls | protected 5H-PV and 5H-BV observations plus Ryan-performed 5H-BR2 remediation: required logging/use controls off; Ryan disabled Broadcast with one toggle and attested immediate and one-reload persistent disabled state; destination details remain uninspected | Protected, remediated, and historically verified | The previously active configured Broadcast path was disabled at the observed workspace. Provider state remains externally mutable, and this dated attestation is not continuous-currentness evidence. |
| Offline recovery / PR #92 | recovery head `c5de027162e6e57ba720b90694d08f106851f4f5`; Synthetic CI run `30460422095`; normal merge `ddc2f02f10fad85fb9936806b5fd84eda806069c`; Fly Deploy run `30464960703`, job `90620267980`; one HTTP 200 `status: ok` health result; exact command-center closeout recovered through 5R-R | Durable, hosted-verified, merged, deployed, and historical production-verified; closeout durable through containing `[skip actions]` commit after post-push gates pass | Task 2.8 is released. 5R remains historically stopped at rendered closeout verification; 5R-R owns the exact corrected closeout. Local `main` remained preserved and the feature branch was retained. |

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
| 5H-A | Ask Opus data-handling audit | Merged and deployed through 5H-R2 | The privacy contract evidence is included in the released package. |
| 5H-B | Ask Opus privacy implementation | Merged, deployed, and historical production-verified through 5H-R2 | The implementation is released; provider/Broadcast safety remains a separate evidence boundary. |
| 5I | Operator runbook and monitoring matrix | Merged and deployed through 5H-R2 | Included in the released operator package. |
| 5J | Local synthetic operator re-entry drill | Merged and deployed through 5H-R2 | The sanitized drill evidence is in the released package; it remains local-synthetic proof. |
| 5K | Release-evidence reconciliation | Merged and deployed through 5H-R2 | Included in the released package; later evidence overrides its dated hosted facts. |
| 5L | Maintained documentation and release handoff | Merged and deployed through 5H-R2 | Included in the released operator package. |
| 5H-R | Ask and operator package durability | Merged and deployed through 5H-R2 | Candidate and closeout heads passed hosted CI before the exact direct-main release. |
| 5H-PV | OpenRouter account privacy verification | Protected read-only observation; failed-safe | Required logging/use controls were off, but enabled Broadcast remains unreviewed; the later release override did not resolve it. |
| 5H-BV | OpenRouter Broadcast boundary evidence | Protected read-only observation; remediation-needed; closeout local-only | Broadcast is enabled with one configured destination marker. Privacy Mode, API-key filtering, sampling, destination values, and actual traces remain uninspected; no setting changed. |
| 5H-BR | OpenRouter Broadcast disablement and persistent-state verification | Stopped before mutation; closeout local-only | The expected workspace and enabled Broadcast control were present, but the ordinary read-only page representation exposed excluded destination-specific configuration details before any click. No setting changed, no detail is retained, and Task 4.3 remains current. |
| 5H-BR2 | Ryan-performed Broadcast disablement and value-free persistence attestation | Complete locally | Ryan disabled Broadcast with one toggle and attested disabled state immediately and after one reload, no other setting changed, no broader confirmation was accepted, and no destination-specific detail entered the evidence. Task 4.3 is done. |
| 5H-R2 | Ask exact-main deployment observation and release closeout | Merged, deployed, and historical production-verified; closeout local-only | Exact live main, one automatic deployment, every step, zero annotations, and one HTTP 200 `status: ok` health result passed. |
| 5M | Final target and parent durability closeout | Durable on parent and target `main`; zero workflow activity | Parent pointer and reusable lesson are durable at `391debe28ea58349c65312eeb0987e9b516babd9`; the target twelve-path package is carried by `ac5361e5b2be55356538ae44b28127ce0fc19097`. |
| 5N | Optional-parked Phase 5 disposition and transition readiness | Command-center-only durability through the containing `[skip actions]` commit | Required Phase 5 work is complete; Tasks 2.2, 2.7, and 2.8 remain optional and parked; no product work or successor phase starts. |
| 5R | Offline recovery production release | Merged, deployed, and historical production-verified | PR #92 merged normally, exactly one automatic Fly Deploy passed, and the one authorized health request returned HTTP 200 `status: ok`; Task 2.8 is released. |
| 5R-R | Exact decision-queue schema recovery and release closeout resume | Command-center closeout durable through the containing `[skip actions]` commit after post-push gates pass | Corrected only the invalid decision field shape, preserved 5R as historically stopped, rendered the final next-objective gate correctly, and repeated no release action. |

The detailed block definitions and sanitized evidence paths remain in [`roadmap.md`](roadmap.md), [`state.json`](state.json), and the dated [`logs/`](logs/) directory.

## Release Packages

### Released usability set

- Scope: 5A, 5B, 5C, 5E, 5F, and the 5F-W normalization carried by PR #89.
- Exact release path: activation `13d2f16a9cca8b8d4fb4900006dfaa9655824474` → merge `e905e5c4ad406ebb7b5f10ea6d867d5724f662ce` → Fly Deploy run `30263216876`.
- Current `main` ancestry also includes Recurring Review merge `d81ed7078e741a0c7613e7898312ce01cd359f45`, Ask hosted closeout `257bec901e88b830fcafe6067c8174cd6a5213b6`, and exact release head `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`.
- Boundary: deployment and dated health are established; current production health remains externally unverified.

### Recurring Review

- Exact hosted head: `eccb0adb93a32d84127c5cb8d4d924a812ff0e8a`.
- PR #90: ready and merged as `d81ed7078e741a0c7613e7898312ce01cd359f45`.
- Exact current-head CI: run `30279361029`, both jobs successful, zero annotations.
- Exact release: Fly Deploy run `30327566484`, job `90176026100`, every step successful, zero annotations, exactly one deployment, and dated HTTP 200 `status: ok` health evidence.
- Boundary: durable, hosted-verified, merged, deployed, and historical production-verified through 5G-R2.

### Ask Opus and operator handoff

- The exact Ask Opus privacy implementation, maintained tests, operator runbook, monitoring matrix, drill evidence, release map, handoff, and Runway OS package was hosted-verified through candidate `f7482a95e754160905a79ec0130ef8faf0a48784` and closeout `257bec901e88b830fcafe6067c8174cd6a5213b6`, then released on exact `main` head `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`.
- Synthetic CI runs `30329875129` and `30330294465` each passed both ordered jobs with zero annotations and zero deployment.
- Exactly one automatic push-event Fly Deploy, run `30350587286` and job `90246858468`, passed every returned step with zero annotations. The one authorized credential-free `/health` request returned HTTP 200 and `status: ok`.
- The 5H-PV protected observation found required content-use and private I/O logging controls off and the paid-model training policy off. Anthropic account ZDR was off while per-request ZDR remains enforced in code.
- 5H-BV established Broadcast enabled with exactly one configured destination marker. The eligible contract includes request/response content, tokens, cost, timing, model/provider, tool activity, and optional user/session/custom metadata.
- Per-destination Privacy Mode, API-key filtering, and sampling remain uninspected; no destination value or trace content was opened.
- Boundary: release, dated minimal production health, the dated Ryan-performed Broadcast disablement attestation, and final Task 4.5 target-plus-parent durability are established; continuous currentness and authenticated behavior remain separate.

## Unresolved Gates

| Gate | Current state | Exact evidence needed to clear it | Authority |
| --- | --- | --- | --- |
| Task 3.5 maintained documentation and compact handoff | Complete and released through 5H-R2 | No further Task 3.5 action | Complete |
| Recurring Review merge and production release | Complete through 5G-R2 | No further release action; use the exact merge, deploy, and dated health evidence above | Complete |
| Ask Opus durability/publication | Complete through exact-main 5H-R2 release | No further Task 4.4 release action; use exact candidate, closeout, deployment, and dated health evidence above | Complete |
| OpenRouter account-setting verification | Complete through 5H-BR2; Ryan attested Broadcast disabled immediately and after one reload | No further Task 4.3 action; any later currentness claim requires a separately authorized observation | Complete |
| Ask Opus production release | Complete through 5H-R2; the separate Broadcast risk was later resolved through 5H-BR2 | No further Task 4.3 or 4.4 action | Complete |
| Current production health | Historically verified through the one 5R health request on 2026-07-29 | A new separately authorized observation is required for any later current-health claim | Ryan |
| Parked Tasks 2.2 and 2.7 | Optional and parked | Explicit reopening and a new bounded proposal | Ryan |
| Final Task 4 durability and parent pointer | Complete through 5M | No further Task 4 or parent action | Complete |
| Phase 5 transition | Required work complete; Phase 5 remains active because no successor direction exists | Ryan selects the next objective before a separate transition and Phase 6 intake block is proposed | Ryan |

## Reconciliation Conclusion

There is no blocking contradiction between local Git, live remote `main`, PR #89, PR #90, PR #91, or the exact workflow records. The key split is not “verified versus unverified”; it is:

1. the first usability set is merged, deployed, and historically health-verified;
2. Recurring Review is merged, deployed, and historically health-verified through 5G-R2;
3. Ask Opus and the operator/release-handoff artifacts are merged, deployed, and historically health-verified through exact-main 5H-R2;
4. required OpenRouter logging/use controls are off, and Ryan later disabled Broadcast in 5H-BR2 with one toggle and attested immediate and one-reload persistent disabled state; no destination-specific detail is retained, and neither that dated attestation nor the dated health result creates continuous-currentness evidence.

Tasks 4.3 and 4.4 are complete on that factual basis, Task 4.5 target-plus-parent durability is complete through 5M, and Task 2.8 is released through 5R. Tasks 2.2 and 2.7 remain optional parked work. Required Phase 5 work is complete; the remaining gate is Ryan's next-direction choice before a truthful phase transition.

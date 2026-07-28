# Work Block 5H-PV — OpenRouter Account Privacy Verification

Date: 2026-07-28

Status: complete with a failed-safe release gate

Release override: after receiving the explicit consequence that a direct push would release Ask Opus and trigger production while Broadcast remained enabled and unreviewed, Ryan directed “Push to main despite the unresolved Broadcast gate.” This later authority does not change the failed-safe verification result; it authorizes only the separately requested one-push release action.

## Authority And Target

Ryan confirmed the bounded Task 4.3 (`P5-T43`) block and retained credentials, MFA, account identity, and every setting decision. Ryan then confirmed that the authenticated OpenRouter session appeared to be the account owning The Ledger production API key. No key, credential, MFA value, account identifier, billing detail, prompt, completion, generation, log content, or financial question was opened, copied, or recorded.

The observation was read-only. No setting changed, no provider request ran, and no GitHub, workflow, Fly, deployment, production, health, application, database, or parent-project action occurred.

## Sanitized Observation

| Control | Observed state | Meaning for this gate |
| --- | --- | --- |
| Use of inputs and outputs / 1% data-discount workspace permission | Off | The account does not permit workspaces to opt into OpenRouter use of inputs and outputs through this control. |
| Private Input & Output Logging / prompt storage | Off | OpenRouter prompt and completion storage through the workspace logging control is disabled. |
| Paid endpoints that train on request data | Off | Paid-model requests are excluded from endpoints that may train on request data at the account policy layer. |
| Anthropic account-level Zero Data Retention | Off | Account-level Anthropic ZDR is not enabled; The Ledger's implemented per-request `zdr: true` remains the enforced ZDR boundary. |

One adjacent Observability control was unexpectedly visible and enabled:

- **Broadcast: enabled.** The page describes this control as automatically sending request traces to external observability platforms. The confirmed block did not authorize opening its destinations, inspecting payload configuration, or changing it. Destination, active integration, and transmitted trace contents therefore remain unknown.

The unrelated free-endpoint training control was visible as enabled. The Ledger Ask Opus route uses a paid Claude model and independently sends `data_collection: "deny"` plus `zdr: true`, so this observation is not treated as evidence about the implemented Ask request path.

## Result

The two required OpenRouter content-use and private prompt-storage controls are off, and the paid-model training policy is off. The account-level Anthropic ZDR toggle is off, but the application enforces ZDR per request.

Task 4.3 does not clear the release gate because the enabled Broadcast control creates an unreviewed external trace path. Work block 5H-PV therefore closes **failed-safe**: no remediation was attempted, Task 4.3 remains current and decision-needed, and Task 4.4 is not ready for release planning.

The next safe decision is a separate target-specific Broadcast-boundary block. It should determine whether any destination is configured and what fields are transmitted, without opening stored prompts or logs, then return a remediation recommendation. Any setting change remains a separate explicit action unless that later block says otherwise.

## Local Preservation

- Branch remained `codex/ask-opus-privacy`.
- Head remained `257bec901e88b830fcafe6067c8174cd6a5213b6`.
- The real index remained empty.
- The accepted command-center closeout remained local and unstaged.
- The duplicate 4AU log, `command-center/now 2.md`, and `scripts/sync_prod_to_local.sh` remained excluded and unchanged.
- Dashboard activation and closeout use automated refresh, currentness, and health checks; no Ryan visual attestation is required.

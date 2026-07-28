# Work Block 5H-BV — OpenRouter Broadcast Boundary Evidence

Date: 2026-07-28

Status: complete locally with a remediation-needed result

## Authority And Account Boundary

Ryan confirmed Task 4.3 (`P5-T43`) only and directly attested that the authenticated OpenRouter session was the account owning The Ledger production API key. Ryan retained credentials, MFA, account identity, setting authority, and risk acceptance. No credential, MFA value, API key, account identifier, destination value, billing detail, credit detail, financial row, prompt, completion, generation, stored trace, or log content was opened, copied, or recorded.

The observation was read-only. No setting, destination, integration, provider request, test event, trace, GitHub surface, workflow, Fly resource, production endpoint, database, application behavior, or parent project changed.

## Sanitized Provider Observation

- The authenticated Observability page was the Default Workspace surface for the attested account.
- Broadcast was **enabled**. The authoritative switch exposed `aria-checked: true` and checked state.
- The Broadcast section displayed exactly one generic **Configured** marker.
- No destination name, type, URL, endpoint, credential, project identifier, account identifier, filter value, sampling value, or stored trace was opened or retained.
- The result is classified `configured-active` at the observed workspace surface: Broadcast is enabled and one destination is marked configured.

The read-only summary did not expose whether the configured destination uses API-key filtering, what sampling rate applies, or whether per-destination Privacy Mode is enabled. Opening the destination configuration could expose credentials, endpoints, identifiers, or editable controls and was outside the confirmed block. Therefore this evidence does not claim that every Ledger production-key request was transmitted or that prompt and completion content was definitely included. It establishes an active configured transmission path and a failed-safe possibility of Ledger request traces reaching an external destination.

## Current Official Trace Contract

OpenRouter's current official [Broadcast overview](https://openrouter.ai/docs/guides/features/broadcast/overview) states that enabled Broadcast automatically sends trace data for API requests to configured destinations. Generic eligible categories are:

- request and response content, with multimodal content stripped;
- prompt, completion, and total token usage;
- request cost;
- start time, end time, and latency;
- model and provider information;
- tool inclusion and tool-call activity;
- optional user ID and session ID when supplied;
- arbitrary custom trace metadata when supplied.

Per-destination Privacy Mode, when enabled, strips input messages and output choices but continues sending token, cost, timing, model, provider, and custom-metadata categories. API-key filtering and sampling are also per-destination. Their configured values were not exposed by the safe summary and were not opened.

## The Ledger Request Boundary

Tracked source inspection confirms the released Ask Opus route sends a system instruction plus one current user message containing the approved active-entity page summary and current question, along with model, token limit, and provider-routing controls. It sends `zdr: true` and `data_collection: "deny"` but does not supply optional Broadcast `user`, `session_id`, or custom `trace` fields.

Broadcast is an account or workspace observability path rather than an Ask-only feature. The official contract applies to OpenRouter API requests reaching a configured destination, so per-request provider routing controls do not by themselves disable Broadcast.

## Result

5H-BV is complete with a remediation-needed result. The external trace path is not hypothetical: the observed workspace has Broadcast enabled and exactly one destination marked configured. The read-only evidence does not establish destination Privacy Mode, API-key filtering, or sampling, so it cannot safely narrow the possible exposure to metadata-only or prove The Ledger production key is excluded.

Task 4.3 remains current and decision-needed. Task 4.4 remains done. Task 4.5 remains planned. The recommended next decision is a separate `5H-BR` remediation proposal to disable Broadcast and verify the disabled state without inspecting destination values or sending a test request. This log authorizes no remediation or successor.

## Local Preservation

- Detached `HEAD` and cached `origin/main` remained `ef2fff586dbaf31b1f8d3e7d7024b55aedbd30c7`.
- The real Git index remained empty.
- The existing eight-path local 5H-R2 closeout remained preserved; this log is the only new path.
- No commit or push occurred.

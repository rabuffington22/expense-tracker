# Work Block 4BC — Real Plaid CSP Runtime Checkpoint

Date: 2026-07-24

Status: Passed and closed locally. No product, test, configuration, workflow, database, account, or deployment mutation occurred.

## Authorized Boundary

Ryan authorized authenticated production reads of the two released Plaid entry documents, exactly one Link-token request from each entry path, and one real Link open-and-close from each path before institution selection. Credential handling, screenshots, response bodies, institution selection, account login, public-token exchange, account connection, sync, disconnect, toggle, rename, protected-detail capture, and every database, downstream, workflow, Fly, GitHub, or product mutation remained excluded.

## Preflight

- Fly Deploy run `30116007970` remained successful for exact source SHA `6c2a2800ec887ea3c2bf8fb254214dbd0630f55f`.
- The deployed source SHA remained an ancestor of `origin/main`.
- Credential-free production `/health` returned HTTP 200 with `{"status":"ok"}`.
- The first protected navigation stopped at the standalone login page. Ryan authenticated manually; Codex did not request, read, enter, or retain credentials.

## Sanitized Runtime Result

Both production entry paths passed:

- Each main document returned HTTP 200 as HTML.
- Each document contained exactly one expected Plaid initializer and one ready Link controller/button.
- Each response carried a fresh document nonce. Its CSP header matched the DOM nonce in the three intended nonce-bearing directives.
- Each policy allowed the Plaid CDN frame and the single configured production API environment. The sandbox API origin was absent.
- The Link frame opened successfully to Plaid's pre-institution consent surface and closed successfully through Plaid's exit confirmation.
- The entry control returned to its enabled state after Link closed.
- No CSP violation, refused-resource message, initializer failure, frame failure, unexpected external origin, failed network response, or product error appeared.

The two documents used different fresh nonces.

## Network And Mutation Boundary

The complete authorized browser session produced exactly two Link-token POST requests:

1. `/data-sources/link-token`
2. `/plaid/link-token`

No exchange-token, sync, disconnect, account toggle, account rename, database, downstream, workflow, or Fly mutation request appeared. No institution was selected, no account login occurred, no public token was exchanged, and no account or financial state was changed.

## Console Note

Chrome reported three identical extension message-channel closure entries. They did not originate from the product or CSP, and the filtered product/CSP error count was zero. Targeted CSP and refused-resource checks were also zero.

## Evidence-Minimization And Closeout

- No screenshot or response body was captured.
- No credential, institution, account, transaction, payroll, balance, or other protected detail was recorded.
- No product or policy repair was needed.
- Command-center closeout remains local-only and uncommitted.
- The three unrelated untracked files were preserved unchanged.

## Next Separate Decision

Task 1P.4 is complete through the released enforcement and this real-runtime checkpoint. The next proposed block is 4BD for the bounded Task 1P.6 installed-PWA and browser-boundary regression slice. It is not authorized by 4BC.

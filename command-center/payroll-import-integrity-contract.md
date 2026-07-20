# Payroll Import Integrity And Payload Lifecycle Contract

Date: 2026-07-20

Work block: 4P

Scope: Phase 4 Tasks 1M.1-1M.3 for `P3-3F-02`, `P3-3F-05`, `P3-3F-06`, and only their focused `P3-3F-C01` coverage.

## Employee Assignment

- Preview groups employees by normalized name using Unicode case folding plus surrounding-whitespace removal.
- Exactly one existing normalized-name match is selected by default.
- An exact match may be reassigned explicitly to another existing employee.
- `Create new employee` is offered only when no normalized-name match exists.
- Save repeats the same matching rule server-side. A forged `new` submission cannot create a duplicate when one exact existing match is present.
- Multiple existing normalized-name matches require an explicit existing employee selection; the import does not create another employee or guess among them.
- Reimport preserves employee and payroll-entry counts through the existing employee/date uniqueness rule.

## Temporary Payloads

- Payroll preview payloads stay in the filesystem, not Flask's cookie session.
- Newly written payloads use mode `0600`.
- Keys must be non-empty exact opaque basenames. Invalid path-like keys are rejected without resolving to another payload.
- Save consumes its payload before database processing. Missing, reused, expired, malformed, or structurally invalid payloads redirect safely without mutation.
- Preview Cancel is an explicit BFM-only POST action. It is idempotent and removes only its exact payload.
- Payloads older than four hours are rejected and removed when read.

## Workbook Outcomes

- Only `.xlsx` uploads enter the Phoenix parser.
- Corrupt, mislabeled, empty, or engine-unsupported workbook contents produce one sanitized controlled error.
- Headerless or structurally valid workbooks without payroll entries preserve the parser's sanitized warnings and return a controlled empty outcome.
- Workbook-engine details, file contents, and internal exception text are not rendered to the user.
- Failed parsing never creates a preview payload.
- Valid multi-section Phoenix workbooks preserve normal preview and save behavior.

## Boundaries

- The existing payroll blueprint guard denies Personal and Luxe Legacy before parsing, payload access, or payroll storage.
- Verification uses generated workbooks, isolated temporary payload directories, disposable all-entity databases, and denied outbound networking.
- Task 1M.4 roster validation, Task 1M.5 compensation cohorts, migrations, protected data, retained user uploads, live systems, GitHub durability, and deployment remain outside 4P.

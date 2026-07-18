# Agent Router

This existing-project retrofit includes only a lightweight, read-only queue-summary surface. External worker runners and write-capable routing are intentionally absent because Expense Tracker handles financial, payroll, credentialed, and production operations.

Queue folders may preserve sanitized task packets when a separately confirmed work block needs them. They are execution surfaces, never project source of truth.

Adding external runners, patch intake, retry automation, or financial context to a worker requires a project-local routing policy and explicit Ryan approval.

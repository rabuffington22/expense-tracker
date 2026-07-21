# Work Block 4AB — Focused Dashboard Authentication Boundary

Date: 2026-07-21

Status: complete and verified locally; publication remains separately gated

## Scope

Implemented Task 1P.1 and only the focused Task 2 coverage for `P3-3J-03` and its request/public-field slice of `P3-3J-C01`.

Excluded throughout: Tasks 1P.2-1P.7; broader Task 2; Tasks 3-4; cookie flags; CSP; mobile navigation; generalized browser-test infrastructure; Upload copy; broad read-model coverage; migrations; credentials; protected data; real databases; production inspection; Plaid, Fly, workflows, downstream systems, GitHub durability, deployment, and both preserved untracked files.

## Result

- Split the prior shared path helper into an authentication-exemption contract and a separate entity-setup-exemption contract.
- `/k` and `/k/` now pass configured server-side authentication before route execution but remain outside global entity setup.
- Full-page denial preserves a safe local return path; HTMX and JSON denial returns 401.
- Fail-fast mocks and before/after logical database snapshots prove unauthorized requests initialize no global or route-specific database, launch no background sync, and mutate no entity database.
- Authenticated synthetic markers prove Personal and Luxe Legacy fields remain visible, BFM data remains absent, the standalone route reaches its own sync seam once, and global entity setup stays out.
- No-password mode preserves route availability and the same self-managed context.
- README and route documentation now describe the focused dashboard as authenticated when configured rather than public.

## Verification

- Baseline full `.venv/bin/python scripts/smoke_test.py`: pass.
- First implementation run: one controlled test failure because the focused template intentionally renders whole-dollar values; no product defect or scope change was found.
- Corrected assertion using the maintained whole-dollar display contract; final full smoke suite: pass.
- Targeted Python compilation: pass.
- Synthetic markers and temporary databases: cleaned exactly; the smoke `DATA_DIR` was disposable.
- No credential, protected data, retained upload, network request, live system, commit, push, PR, merge, workflow, deployment, or production action occurred.

Final JSON, whitespace, dashboard refresh, command-center health, generated-dashboard inspection, and explicit worktree review are recorded in the 4AB command-center closeout.

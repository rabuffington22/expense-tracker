# Work Block 4V-R Release Evidence

Date: 2026-07-21

## Result

- Published the exact verified twelve-path 4V source set directly to `main` by fast-forward without force or PR.
- Source commit: `9b3e517fc7edf36dd681c6ff5ffe6fd33ddc3263`.
- Automatic Fly Deploy run: `29826028617`.
- Deploy job: `88619460588`.
- The run and job completed successfully for the exact source SHA.
- Credential-free `https://ledger-oak.fly.dev/health` returned HTTP 200.

## Verification And Boundaries

- The maintained synthetic smoke suite passed before publication, including Weekly date and bill section 8a5.
- Python compilation, JSON validation, dashboard refresh, command-center health, whitespace, GitHub authentication, branch ancestry, and remote alignment passed.
- Explicit staging contained exactly twelve approved paths; the high-confidence sensitive-addition scan returned zero.
- Pre-existing untracked `scripts/sync_prod_to_local.sh` and unrelated untracked `command-center/now 2.md` remained untouched and unstaged.
- No protected data, retained upload, credential, authenticated production page, manual workflow action, workflow edit, non-automatic Fly change, downstream access or write, migration, Task 1N.5 implementation, force push, or unrelated action occurred.
- GitHub emitted a non-blocking Node 20 deprecation annotation for `actions/checkout@v4`, which was forced onto Node 24; deployment succeeded.
- The command-center-only closeout commit uses `[skip actions]` and must not trigger a second Fly deployment.

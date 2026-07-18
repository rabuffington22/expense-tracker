# Short-Term Planning Implementation Plan — Retired

Status: historical implementation plan, retired from active project guidance on 2026-07-18.

This file originally planned the `/planning/short-term` feature. The main product direction was implemented and later expanded across database migrations, the Flask route and template, navigation, AI context, budgets, goals, snapshots, action items, dashboard integration, weekly planning, and waterfall reporting.

The plan was not maintained as a final acceptance checklist. In particular, its proposed dedicated Short-Term Planning smoke-test cases and seeded goal/snapshot examples are not present in the current repository exactly as described. Those are audit inputs for Phase 3, not silently accepted requirements or proof that the current feature is defective.

Use these maintained sources instead:

- `README.md` for the current product surface and operating model;
- `web/routes/short_term_planning.py` and `web/templates/short_term_planning.html` for current behavior;
- `core/db.py` for the current migration sequence and schema;
- `scripts/smoke_test.py` and `scripts/seed_demo_data.py` for current verification and demo coverage;
- `command-center/roadmap.md`, `command-center/issues.md`, and `command-center/now.md` for future work and audit status.

The last full historical plan remains available in Git history:

```bash
git show a70e35b:plan.md
```

Do not use the historical version as a current task list.

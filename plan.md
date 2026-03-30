# Short-Term Planning — Implementation Plan

## Overview
Add a new "Short-Term Planning" page at `/planning/short-term` alongside the existing planning page (renamed to "Long-Term Planning"). The page focuses on an **18–24 month horizon** — combining **debt payoff goals** and **monthly category budgets** with AI-assisted plan creation and automated progress tracking via Plaid. Where long-term planning projects net worth at milestone ages (60, 65, 70), short-term planning answers "what should I do over the next 1–2 years?"

---

## Step 1: Rename existing Planning page to "Long-Term Planning"

**Files to change:**
- `web/routes/planning.py` — page title variable
- `web/templates/planning.html` — `<h1>` title text
- `web/templates/components/sidebar.html` — nav link text
- `web/routes/ai.py` — AI context builder page name reference

No URL changes needed — `/planning` stays as-is for long-term.

---

## Step 2: Database migrations (3 new tables)

### Migration 39: `short_term_goals`
```sql
CREATE TABLE IF NOT EXISTS short_term_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    goal_type TEXT NOT NULL,          -- 'debt_payoff', 'savings', 'spending_reduction'
    target_amount_cents INTEGER,       -- target balance (0 for debt payoff, positive for savings)
    target_date TEXT,                  -- YYYY-MM-DD (deadline, typically 6-24 months out)
    strategy TEXT,                     -- 'avalanche', 'snowball', 'custom' (debt only)
    monthly_amount_cents INTEGER,      -- planned monthly extra payment/contribution
    linked_accounts TEXT,              -- JSON array of account_name strings
    status TEXT DEFAULT 'active',      -- 'active', 'completed', 'paused'
    notes TEXT,
    ai_plan TEXT,                      -- AI-generated plan summary (markdown)
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);
```

### Migration 40: `goal_snapshots`
```sql
CREATE TABLE IF NOT EXISTS goal_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL REFERENCES short_term_goals(id) ON DELETE CASCADE,
    snapshot_date TEXT NOT NULL,        -- YYYY-MM-DD
    balance_cents INTEGER NOT NULL,    -- total balance across linked accounts at this point
    note TEXT,                         -- optional review note
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(goal_id, snapshot_date)
);
```

### Migration 41: `budget_items`
```sql
CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    monthly_budget_cents INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(category)
);
```

All three tables are per-entity (stored in the entity's own SQLite database).

---

## Step 3: New route — `web/routes/short_term_planning.py`

**Blueprint:** `short_term_planning_bp`, prefix `/planning/short-term`

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/planning/short-term` | Main page render |
| POST | `/planning/short-term/goals/create` | Create a new goal |
| POST | `/planning/short-term/goals/<id>/update` | Update goal settings |
| POST | `/planning/short-term/goals/<id>/delete` | Delete a goal |
| POST | `/planning/short-term/goals/<id>/snapshot` | Record manual progress snapshot |
| GET | `/planning/short-term/goals/<id>/progress` | HTMX partial: progress chart |
| POST | `/planning/short-term/budget/save` | Save/update budget amounts |
| GET | `/planning/short-term/budget/status` | HTMX partial: budget vs actuals |

### Key helper functions

**`_compute_payoff_timeline(accounts, monthly_extra, strategy)`**
- Takes linked credit card accounts from `account_balances` (balance, rate, min payment)
- Simulates month-by-month payoff over 6-24 month horizon using chosen strategy:
  - **Avalanche**: Extra payment goes to highest interest rate first
  - **Snowball**: Extra payment goes to smallest balance first
  - **Custom**: User-defined allocation percentages
- Returns: list of monthly projections with per-account balances, total interest paid, payoff date

**`_auto_snapshot(goal)`**
- Called on page load for each active goal
- Pulls current balance from `account_balances` for linked accounts
- Inserts/updates today's snapshot (UPSERT on goal_id + date)
- Skips if snapshot already exists for today

**`_get_budget_status(entity, month)`**
- For each budget_item, queries transaction totals for the given month
- Returns: list of {category, budget, spent, remaining, pct}

**`_suggest_monthly_extra(entity)`**
- Calculates: avg monthly income - avg monthly essential spending - recurring charges
- Returns estimated discretionary amount available for debt payoff
- Used by AI plan generator as input

---

## Step 4: Page-level AI chat (conversational plan building)

One persistent AI conversation for the entire Short-Term Planning page — same pattern as Ask Opus on other pages, using the global modal in `base.html`. The chat knows about all goals, budgets, and progress simultaneously so you can discuss trade-offs across goals.

### Initial plan creation
1. User creates a goal (e.g., "Pay off credit cards") and links accounts
2. User opens Ask Opus — AI already has full financial context loaded
3. AI proposes an initial plan: strategy, monthly amounts, timeline, spending cuts
4. User pushes back, asks questions, adjusts ("What if I do $2k/month instead?", "I can't cut dining that much")
5. They go back and forth until the plan feels right
6. User fills in the agreed numbers on the goal card and clicks "Lock In Plan"

### Ongoing adjustments
- User reopens Ask Opus anytime — conversation persists per entity
- Monthly review prompts naturally lead to chat ("I'm behind this month, how should I adjust?")
- Life events: "I got a $5k bonus, where should it go?", "I had an unexpected $3k expense"
- Cross-goal discussion: "Should I pause the savings goal to accelerate debt payoff?"
- Budget integration: "I'm over budget on Food — is that hurting my payoff timeline?"

### Implementation

**Conversation persistence:**
- Stored in `/tmp/expense-tracker-ai/short-term-planning/{entity}.json`
- Same pattern as existing Ask Opus — one thread per entity per page
- Uses the global Ask Opus modal in `base.html` (no separate chat UI)

**Context auto-loaded for every message:**
- All credit card balances, rates, limits, minimum payments (from `account_balances`)
- Monthly income and spending by category (3-month average from `transactions`)
- Recurring charges and subscriptions total
- All active goals: settings, strategy, monthly amount, target date, linked accounts
- Progress snapshots for each goal (actual vs projected)
- Budget vs actuals for current month (all categories)
- Discretionary income estimate (income - essential spending - recurring)

**System prompt:**
"You are a debt payoff and budgeting coach. You have access to the user's real financial data — balances, income, spending by category, recurring charges, and goals. Help them build and refine practical plans. Be specific with numbers: use their actual balances, income, and spending. When suggesting cuts, reference their real spending categories and amounts. Always show the impact on payoff timelines when making changes."

**No separate chat endpoints needed** — uses existing `POST /ai/ask` + `POST /ai/clear` from `ai.py`. Just add a `short-term-planning` context builder to `ai.py`.

### "Lock In Plan" action (on goal card)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/planning/short-term/goals/<id>/lock-plan` | Save plan details to goal |

- A "Lock In" modal on the goal card captures: strategy, monthly amount, target date
- User also pastes or writes a narrative summary (informed by AI conversation)
- `_compute_payoff_timeline()` generates the month-by-month schedule automatically
- Both narrative + schedule stored as markdown in `ai_plan` column
- Plan can be re-locked after future conversations (updates the fields)

### Locked plan format (narrative + structured schedule)
When a plan is locked in, `ai_plan` stores two parts:
1. **Narrative** — Strategy explanation, reasoning, key suggestions (e.g., "Using avalanche strategy because Capital One has 24.99% APR vs Chase at 18.99%. Cutting Food by $200/month frees up extra for payments.")
2. **Month-by-month schedule** — Markdown table showing each month's payment allocation per account, running balances, cumulative interest saved, and payoff milestones. Auto-generated by `_compute_payoff_timeline()`.

Displayed on the goal card as a collapsible section — narrative on top, schedule table below.

---

## Step 5: Template — `web/templates/short_term_planning.html`

### Layout (top to bottom)

**Page header row:** "Short-Term Planning" title + Ask Opus button

**Section 1: Goals**
- Cards for each active goal, showing:
  - Goal name + type badge (Debt Payoff / Savings / Spending Reduction)
  - Current total balance across linked accounts
  - Target and deadline (if plan locked in)
  - Progress bar (balance reduction % from start → target)
  - Mini sparkline or trend indicator (last 6 snapshots)
  - Strategy label + monthly allocation (once locked in)
  - Locked-in plan summary (collapsible — narrative + schedule table from `ai_plan`)
  - "Edit" button → opens settings modal
  - "Lock In Plan" / "Update Plan" button → opens lock-in modal
- "+ Add Goal" button → opens add modal
- Completed goals: collapsed section at bottom
- Ask Opus button in page header for AI-assisted plan building (page-level chat)

**Section 2: Monthly Budget**
- Current month header with prev/next navigation
- Table/grid of categories with:
  - Category name
  - Budget amount (editable inline)
  - Spent this month (auto-computed, links to transactions)
  - Remaining (green when positive, red when over)
  - Progress bar (fills left to right, color shifts green → yellow → red)
- Summary row: Total budgeted | Total spent | Total remaining
- Unbudgeted categories: collapsed section showing categories with spending but no budget set
- "Quick Budget" button: AI suggests budget amounts based on 3-month spending averages

**Goal Add/Edit Modal:**
- Goal name text input
- Type selector (segmented control): Debt Payoff | Savings | Spending Reduction
- For Debt Payoff:
  - Multi-select of credit card accounts from `account_balances`
  - Strategy selector: Avalanche (Recommended) | Snowball | Custom
  - Monthly extra payment amount
  - Target date (default 18 months out, adjustable 6-24 months)
- For Savings:
  - Target amount
  - Target date
  - Linked bank account (optional)
  - Monthly contribution
- For Spending Reduction:
  - Category selector
  - Target monthly amount (less than current average)
- Notes field
- Delete button (edit mode only, red outline, bottom-left — same pattern as long-term planning)

---

## Step 6: Monthly review prompt

**Logic in `_check_monthly_review(goal)`:**
- If today is >= 1st of month AND no snapshot with a note exists for current month → show review banner
- Banner text: "Monthly check-in: Review your progress on [goal name]"
- Clicking opens a review panel:
  - Current balance (auto from Plaid) vs last month's snapshot
  - Change since last month (dollar + percent)
  - On track / behind / ahead indicator (compared to projected payoff line)
  - Optional note field
  - "Save Review" confirms the snapshot with note
  - "Discuss with AI" button → opens Ask Opus with progress context pre-loaded ("You're $X behind plan this month. Here's what happened...")
- The monthly review naturally flows into Ask Opus for adjustments

---

## Step 7: Progress tracking

**Auto-snapshots:**
- On every page load, `_auto_snapshot()` records today's balance for each active goal
- Uses UPSERT (INSERT OR REPLACE) so multiple loads in a day just update
- Balance pulled from `account_balances` for linked accounts

**Progress chart (HTMX partial):**
- Pure CSS or simple inline SVG line chart (no charting library, consistent with rest of app)
- X-axis: months (up to 24 monthly ticks)
- Y-axis: balance
- Projected payoff line (dashed) based on current strategy — extends to target date
- Actual balance line (solid) — snapshots recorded so far
- Shows whether ahead/behind projection
- Horizon markers at 6, 12, 18, 24 months for context

---

## Step 8: Sidebar + navigation

- Rename "Planning" to "Long-Term Planning" in sidebar
- Add "Short-Term Planning" below it
- Both under a "Planning" group if desired, or keep flat

---

## Step 9: Smoke tests

Add to `scripts/smoke_test.py`:
- Goal CRUD (create, read, update, delete)
- Snapshot recording
- Budget CRUD
- Budget status computation
- Payoff timeline calculation
- Entity isolation (BFM goals don't appear in Personal)
- Cross-entity account visibility for goal linking

---

## Step 10: Seed demo data

Add to `scripts/seed_demo_data.py`:
- 2 goals per entity (1 debt payoff, 1 savings)
- 6 months of snapshots showing progress
- Budget items for top 8 categories
- AI plan text for debt payoff goal

---

## File summary

| File | Action |
|------|--------|
| `core/db.py` | Add migrations 39-41 |
| `web/routes/short_term_planning.py` | New file — all endpoints |
| `web/routes/planning.py` | Rename title to "Long-Term Planning" |
| `web/templates/short_term_planning.html` | New file — full page template |
| `web/templates/planning.html` | Update title |
| `web/templates/components/sidebar.html` | Add nav link, rename existing |
| `web/templates/base.html` | Register blueprint |
| `web/__init__.py` | Register blueprint |
| `web/routes/ai.py` | Add short-term planning context builder |
| `scripts/smoke_test.py` | Add short-term planning tests |
| `scripts/seed_demo_data.py` | Add demo data |
| `CLAUDE.md` | Document new page |

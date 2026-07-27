# Claude Design Response

Project: The Ledger
Work block: 5B — independent second-opinion usability critique
Date: 2026-07-26
Reviewer role: independent design/usability second opinion
Status of this document: critique evidence only. Not accepted product direction, not a work-block selection, not an implementation authorization.

Evidence used: `context/command-center-context.md`, `inputs/artifacts/phase-5-usability-baseline.md`, `inputs/artifacts/phase-5-workflow-review-contract.md`, all eleven screenshots in `inputs/screenshots/`, `context/file-list.md`, and `inputs/source/` consulted only to resolve four specific questions raised by the screenshots (mobile table overflow mechanics, the `Ask Opus` trigger markup, the Subscriptions page structure, and the recurring-charge action controls).

---

## Summary Judgment

**Targeted polish — with one surface that needs substantial revision.**

The shell is genuinely good. Navigation, entity boundaries, mobile drawer behavior, filter stacking, and the offline screen are all at a standard where polishing is the right verb. Nothing in this packet suggests a rethink, and I would push back on anyone proposing one: the structure is sound and the interaction model is consistent across eleven captures.

The exception is the recurring-charge surface (F5A-05). That page is not a labeling problem with a copy fix attached; it is a page whose title, contents, action controls, and section order all describe different things. It needs substantial revision as a unit.

The single most useful reframe of the 5A report: **almost every finding is the same failure repeated on different surfaces — the interface states facts without stating what the fact means or what to do about it.** A truthful category warning with no next step. A goals section that says "No goals yet" with the button somewhere else. A table that scrolls with nothing saying so. A denied route that silently redirects. A gold question mark with no sentence attached. Framed that way, this is one coherent polish theme — "explain and enable" — rather than seven unrelated tickets, and it should be sequenced as one.

Second reframe worth stating plainly: several 5A findings are **demo-fidelity defects, not product defects** (F5A-01, F5A-02). Those are cheap, low-risk, and they currently distort every review of this app — including this one. They should go first, before any product-surface polish, so the next review looks at the product rather than at the seed data.

---

## Finding Crosswalk

### F5A-01 — Demo category taxonomy drift dominates first orientation

**Partly agree.** Priority: **P1 for the demo seed, P3 for the banner design.**

5A is right that the banner dominates orientation, and right to refuse to suppress a truthful warning for polish. I agree with both. Where I part company is the diagnosis: the banner is not too prominent, it is too *inert*. The problem is the shape of the message, not its presence.

As captured, the banner sits above the page title — it is literally the first content in the document — and reads as an unresolved system fault. It states a count, names an internal file (`categories.md`), and offers one link. A first-time user cannot tell whether this is their problem, whether it is urgent, whether the numbers below it are wrong, or whether it will come back. That last question matters most: a warning that a user cannot make go away trains them to ignore all banners, which is expensive on a financial surface where you will eventually need a banner they *do* read.

Recommended direction, in two separable pieces:

*Demo seed (P1, trivial risk).* Make the synthetic seed agree with the current category domain, so the demo does not open on a maintenance warning. If the drift is deliberately retained to demonstrate the reassignment workflow, then the demo should say so in demo-only framing. Either is fine; the current accidental middle is not.

*Banner design (P3, product change).* Move it below the page title so orientation comes first. Rewrite in the user's language — what happened, what is affected, what happens if they do nothing. Name the consequence, not the file: something on the order of "17 categories were removed but still have transactions. Those transactions are uncategorized in your totals." Keep the reassignment link as a real button. Allow dismissal until the underlying count changes.

One thing to be careful about: do not solve this by making the banner smaller. A quiet banner about wrong totals is worse than a loud one.

---

### F5A-02 — The demo does not demonstrate Short-Term Planning goals

**Agree.** Priority: **P1.**

This is the highest-value cheap fix in the packet, and it is under-rated at "high impact" — it is impact-multiplying, because it blocks assessment of the page's defining feature. Neither 5A nor I can review the goal-card experience; it does not exist in evidence. Every future review inherits the same blind spot until it is seeded.

The screenshot also shows a second, smaller issue 5A gestures at but does not fully name. The empty state and its call to action are on opposite sides of the page: "No goals yet. Create a debt payoff or savings goal to get started." is centered in the panel, while `+ Add Goal` sits top-right, visually grouped with the section header rather than with the instruction that tells you to use it. The sentence describes an action the user cannot see while reading it.

Recommended direction: seed two representative goals in the demo contract — one debt payoff, one savings — with no production or entity-isolation effect. Separately, put the action inside the empty state, next to the sentence that asks for it. Keep the header button too if you like; the duplication is cheap and the empty state is where the user is looking.

I would not take 5A's alternative option (repositioning the page as a budget/action dashboard). The page is named Short-Term *Planning*, goals are the only forward-looking element on it, and the rest — action items, autopay, budget — is retrospective or recurring. Removing goals leaves a page with no planning on it.

---

### F5A-03 — Mobile transaction overflow is functional but not self-explanatory

**Partly agree.** Priority: **P2.**

I agree there is a problem and agree with the measurement. I disagree with the implied remedy. 5A's acceptance direction offers "make overflow discoverable *or* present a mobile-first row hierarchy" as equal options; they are not, and I would like the intake to record that disagreement clearly.

The source confirms this is structural rather than incidental: the results table carries an explicit `min-width: 560px` inside a wrapper set to `overflow-x: auto`. So the horizontal scroll is deliberate, and the missing cue is the *consequence* of a decision to keep a desktop table on a phone — not an oversight to patch with a gradient fade or a "swipe →" hint.

Adding a cue would technically close the finding while leaving the actual cost in place: on a 390px screen the user gets four columns of a table, must scroll sideways to read amount or category for each row, cannot scan a column, and loses the left-hand description as soon as they do. Scroll cues are a reasonable treatment for a wide table a user occasionally consults. Transactions is a primary daily surface — the J1 matrix says so.

Recommended direction: below the tablet breakpoint, render each transaction as a two-line row instead of a table row — description and category on the first line, date and signed amount on the second, amount right-aligned. No fields are lost; every field currently in the 560px table fits in the 390px viewport without horizontal movement. Keep the existing table at tablet and above. If a mobile-first row is rejected as too large a change for a polish block, then the fallback is a persistent edge fade plus a column count, but log it as a mitigation, not a fix.

Note the filters are genuinely fine, as 5A says. The concern is only the result rows.

---

### F5A-04 — Luxe Legacy first-use and unsupported-route states lack explanation

**Agree, and I would raise the priority.** Priority: **P2, above F5A-05 for the empty state specifically.**

5A rates this medium. I would rate the empty dashboard higher, because of how it fails rather than that it fails. The LL dashboard does not look empty — it looks broken. Eleven category rows render with full-width empty tracks and a small blue tick at the left edge; the summary reads `$0 / $0 / $0` inside a highlighted focus ring. A user's first reading is not "I have no data yet," it is "the numbers did not load." The interface is showing the *skeleton of a populated state* to a user who has never populated anything. Compare Payroll, which 5A correctly praises: it says there are no employees, names the next action, and names the file it expects. Payroll's empty state is the pattern; the LL dashboard should adopt it.

The denied route is a genuine but smaller issue, and I agree entirely with 5A's framing that the fail-closed behavior must be preserved. Silent redirect is the correct *security* behavior and the wrong *communication* behavior; these are separable. The user typed or followed a link to a real page and landed somewhere else with no explanation, which reads as a bug and invites a retry.

Recommended direction: replace the zero-filled scaffolding with a real first-use state that names what Luxe Legacy needs (connect an account or import transactions) and offers that action; suppress the category scaffolding entirely until there is at least one transaction. For the denied route, keep the redirect exactly as it is and surface a plain-language notice on arrival — "Long-Term Planning isn't available for Luxe Legacy" — with no implication that another entity has it, since a message that reveals cross-entity capability would undercut the boundary the redirect exists to enforce. That constraint is worth writing into the acceptance signal.

---

### F5A-05 — "Subscription Tracker" and "recurring charges" describe different scopes

**Agree — and this is the finding I would elevate above all others.** Priority: **P1.**

5A rates this medium. I rate it the most serious *product* problem in the packet, and it is the one surface where I would not call the work polish. 5A identifies the label mismatch correctly but stops short of the full picture; four separate problems are stacked on this page and each makes the others worse:

1. **Scope.** The title says Subscription Tracker; the section label says "We found these recurring charges"; the list contains office rent at $1,200/mo, health insurance, a 401k contribution, legal services, fleet, janitorial, and dental. Roughly two of the twenty-odd visible rows are subscriptions in any ordinary sense. The user cannot tell whether the detection is broken or the label is wrong. It is the label.

2. **Task shape is invisible.** This is a review queue — every row demands accept or dismiss — but nothing states how many items are waiting, how many are done, or that the list ends. No count, no progress, no grouping. The user does not know whether they are starting a two-minute task or a twenty-minute one, which is the single strongest predictor of whether they will start it at all.

3. **The actions are unreadable.** Accept and dismiss are a bare `✓` and `×` at the right edge, rendered small and identical in weight. The accessible names are correct ("Add to watchlist", "Dismiss suggestion") — that must be preserved — but sighted users get no such disambiguation, and the two controls are adjacent, similar, and one of them is destructive-feeling. There is an undo path (the collapsed "Show N dismissed" section) but it is at the bottom of the page, far from the point of action and invisible at the moment of hesitation.

4. **Order inverts the mental model.** The watchlist — the thing the page is named after, the user's actual tracked set — begins *below* a long candidate queue. The user must scroll past twenty unresolved decisions to see what they already decided.

Recommended direction, as one coherent revision rather than four tickets:

- Rename the page to what it contains: **Recurring Charges**. Keep "subscriptions" as a group within it.
- Put the user's tracked set first. Present the detection queue as a bounded, countable task below it — "18 charges to review" — with the count decrementing as items are resolved.
- Group the queue by kind (Subscriptions / Bills & obligations / Payroll & benefits, or whatever the detection can actually distinguish). If it cannot distinguish them, that is a product question for Ryan, listed below.
- Replace the icon pair with labeled controls — Track / Not recurring, or Track / Dismiss — preserving today's accessible names as the visible names where possible.
- Put undo at the point of action: an inline "Dismissed — undo" on the row for a few seconds, in addition to the existing collapsed list.

I want to be precise about scope creep here, since this is a review block: nothing above changes the detection logic, the data model, or what the page can do. It changes what the page says it is, what order it says it in, and how the two decisions are labeled.

---

### F5A-06 — Data Sources is useful but indirectly discoverable

**Partly agree — and I disagree with the most likely remedy.** Priority: **P4.**

I agree the page is clear once reached and that it is hard to find. I disagree with treating "add it to persistent navigation" as the natural fix, and I want that recorded because it is the cheapest-looking option and the one most likely to be adopted by default.

Data Sources is a setup surface. A user configures Amazon order imports and connects a payment account once, then rarely returns. The BFM sidebar already carries eleven items; adding a twelfth permanent entry for a rarely-repeated task makes every daily destination slightly harder to find in order to make one occasional task slightly easier. That is a bad trade on a nav list this long.

The real defect is not that Data Sources is missing from the sidebar — it is that **Data Sources and Connected Accounts are the same concept split across two places, and only one of them is visible.** A user who finds Connected Accounts has no reason to suspect Data Sources exists, and no way to learn the difference between them. That is the finding I would write.

Recommended direction: group the two under one destination — a Connections or Setup area containing both vendor-order imports and payment-account connections, with the existing explanatory copy from Data Sources (which 5A correctly praises) doing the work of distinguishing them. Keep the To Do entry point exactly as it is; contextual entry from a task is good design, not a workaround. Low priority, and reasonable to park behind the IA question in Open Questions.

---

### F5A-07 — The global AI affordance relies on an unexplained icon

**Agree — and I would raise this to the top half of the list.** Priority: **P2.**

5A rates this low-to-medium and treats it as an icon-labeling issue. I read it as a trust issue, which is a different weight class.

Two distinct costs, and 5A only names the first:

*Wrong model.* A question mark is the universal help-and-documentation glyph. Users will read it as "help with this page," click expecting documentation, and get a chat input reading "Ask about your finances..." — the mismatch is between what the icon promises and what the feature is, and it recurs on every page. Users who want an AI assistant will not find it, because it is not marked as one.

*No privacy statement, on a financial surface.* This is the part I would escalate. The user is being invited to send questions about their finances somewhere, and nothing in the visible interface says what leaves the device, what the assistant can read, or whether the conversation is stored. The chat panel has a Clear control, which implies persistence, which raises the question without answering it. On a product whose central design achievement is fail-closed entity isolation, an unlabeled AI entry point quietly undoes the impression that boundaries are visible and enforced — and the accessible name "Ask Opus" does not answer any of it either, so the current accessibility compliance does not cover this gap.

Recommended direction: keep the accessible name; change what is visible. Use a glyph that is not a question mark, and pair it with a short visible text label ("Ask Opus") at desktop widths. In the chat panel, add one persistent line stating scope and data handling — what entity's data it can see, whether the conversation is stored, and that it is scoped to the current entity if that is true. If it is not scoped to the current entity, that is a product decision for Ryan and should be resolved before the label is written, not after.

---

### Crosswalk summary

| Finding | 5A impact | My position | My priority |
|---|---|---|---|
| F5A-01 category drift banner | high | partly agree — seed defect + inert message, not over-prominence | P1 seed / P3 banner |
| F5A-02 no demo goals | high | agree — blocks assessment of the page's core feature | P1 |
| F5A-03 mobile table overflow | medium | partly agree — needs a mobile row, not a scroll cue | P2 |
| F5A-04 LL empty/denied states | medium | agree, raise — empty state reads as broken, not empty | P2 |
| F5A-05 subscription scope/label | medium | agree, raise — four stacked problems; substantial revision | P1 |
| F5A-06 Data Sources discoverability | low-med | partly agree — disagree with nav addition as the remedy | P4 |
| F5A-07 AI affordance | low-med | agree, raise — trust and privacy, not iconography | P2 |

---

## Important Issues 5A Missed

**M-01 — Entity context disappears on mobile. (High.)**

This is the most significant gap in the 5A review. The desktop shell keeps a persistent Personal / BFM / LL switcher directly under the logo — 5A correctly lists this as a strength. On phone, the header contains a hamburger, the logo, and a spacer. The current entity is not shown anywhere on screen; it is inside the drawer.

So on the surface where the user is least oriented and most likely to be interrupted, a product whose defining behavior is strict entity isolation stops saying which entity they are in. The failure mode is quiet and real: return to a backgrounded tab, glance at Transactions, and read business figures as personal ones. Mobile Transactions and Weekly both show substantial money figures with no entity marker in the captures.

Recommended direction: put the current entity name in the mobile header, next to or beneath the page title. Cheap, low-risk, and it protects the boundary the rest of the app works hard to enforce.

**M-02 — The dashboard's two-column category list splits by a rule the user cannot see. (High.)**

5A calls the category presentation "dense." Dense is the symptom; the cause is that it is two lists pretending to be one. The left column shows budgeted categories with colored bars, sorted by amount descending. The right column shows categories with no bar and no spend, ordered alphabetically. A user reading left-to-right across the grid — which is how a two-column grid is read — sees Travel $3,685 next to Gifts & Donations with an empty track and no explanation of what distinguishes them.

Roughly half the dashboard's vertical space is spent on rows whose only content is a category name and an empty bar. On the primary orientation surface, most of the screen is occupied by the absence of information.

Recommended direction: show budgeted and active categories only; collapse zero-activity categories behind a count ("+21 categories with no spending this month"). If the two-column split survives, label each column. This one is likely to interact with F5A-01, since the drift is what inflated the zero rows in the first place — sequence them together.

**M-03 — Color carries meaning with no legend. (Medium.)**

The dashboard bars run red, green, and amber, and the meaning is inferable but never stated: red appears to be over budget, green at or under, amber near. Meanwhile red is also used for negative amounts elsewhere (`−$9,079`, `−$4,173`), and blue is the accent for every interactive element *and* the marker on empty category tracks. Three color systems overlap on one screen with no key. For users with color-vision deficiency the budget states are indistinguishable, since nothing but hue separates them — the bars are the same shape, the same length rule, and the numeric label inside them does not state the budget comparison.

Recommended direction: add a redundant non-color signal to over-budget rows (the ratio, or a marker), and state the color meaning once on the surface where it is introduced. Not an accessibility audit finding — the packet explicitly is not one — but a comprehension finding that happens to also help.

**M-04 — There is no way to find a capability by name. (Medium.)**

Eleven sidebar destinations on Personal, eleven on BFM, five on LL, with capability sets that differ per entity, plus surfaces like Data Sources that appear in none of them. There is no search, no index, and no overview. F5A-06 is one instance of a general problem: the only way to learn what this app can do is to click everything, per entity. As the app grows this gets monotonically worse, and it is the structural reason a Data Sources–style finding will recur.

Recommended direction: not a polish-block item — flagging it as the IA question that F5A-06 should roll up into rather than being solved locally.

**M-05 — The offline screen answers "what happened" but not "is my data safe." (Low.)**

5A lists the offline screen as a strength and I agree — it is direct, data-free, and single-action. One addition worth considering: it says the app needs a connection to load financial data, which leaves open whether anything unsaved was lost. One clause ("Nothing you've entered has been lost") would close the loop. Also worth checking that Retry gives visible feedback when it is pressed while still offline; nothing in the capture indicates a pending or failed state, and a button that appears to do nothing is worse than a button that says it failed.

---

## Strengths To Preserve

I endorse 5A's strengths list without exception. The ones where I would set an explicit no-regress condition, because the changes recommended above touch them:

- **Fail-closed entity boundaries and the persistent entity switcher.** The F5A-04 denied-route message must not name or imply capabilities available in other entities. The M-01 mobile entity marker must not become an entity *switcher* in the mobile header — switching stays in the drawer where it is a deliberate act.
- **Mobile drawer semantics** — focus placement, containment, Escape, scrim, scroll lock. Nothing recommended here touches the drawer; if a change would, it should be rejected.
- **Cleanly stacked mobile filters.** The F5A-03 mobile row change applies to results only. The filter form is correct as built.
- **Weekly Check-In's summary-to-detail hierarchy.** This is the best-organized surface in the packet and the model the dashboard and LL empty state should be measured against: one headline number, then pace, then remaining, then detail. Do not add density to it.
- **Payroll's empty state.** Names the absence, the next action, and the expected file. This is the house pattern for empty states; F5A-04's LL dashboard should be brought up to it rather than a new pattern being invented.
- **Data Sources' vendor-versus-payment-source explanation.** If F5A-06 leads to a merged Connections destination, this copy must survive the merge intact — it is the part that works.
- **The offline screen's restraint.** Data-free, one action, no branding flourish. Resist adding to it beyond the single reassurance clause in M-05.
- **Accessible names on compact controls** (`Ask Opus`, `Add to watchlist`, `Dismiss suggestion`). Where recommendations replace icons with visible labels, the accessible name must not regress to something weaker or become redundant noise.
- **Zero console warnings or errors across reviewed routes.** A clean baseline is easy to lose during polish and expensive to recover.

---

## Top Five Priorities

Ranked by user impact against implementation risk and likely effort. Effort is my estimate from the screenshots and the supporting source only; Codex should re-estimate.

**1. Demo fidelity: seed goals, reconcile the category taxonomy.** (F5A-02, F5A-01 seed half.)
Impact: high — unblocks review of the app's core planning feature and stops the product opening on a maintenance warning. Risk: very low; demo contract only, no production or entity-isolation surface touched. Effort: small.
First because it costs the least and because every subsequent review is distorted until it is done.

**2. Recurring charges: scope, order, and action clarity.** (F5A-05.)
Impact: high — the densest decision surface in the app is currently unreadable as a task. Risk: medium; touches page structure, section order, and control labels, and needs a product answer on what the grouping is. Effort: medium-large.
The one item I would call substantial revision. Do not split it into a rename ticket — a rename alone leaves the queue just as opaque.

**3. Luxe Legacy first-use and denied-route explanation.** (F5A-04, plus M-01's boundary logic.)
Impact: high for the LL segment — it is the entire first-run experience for that entity, and it currently reads as failure. Risk: low; additive states, no change to the routing behavior. Effort: small-medium.
Reuse the Payroll empty-state pattern rather than designing a new one.

**4. Mobile Transactions row hierarchy, plus the mobile entity marker.** (F5A-03, M-01.)
Impact: high on phone, which the matrix treats as a primary context. Risk: low-medium; a new responsive presentation of existing fields, no data or filter change. Effort: medium for the rows, trivial for the entity marker.
Bundled because both are mobile-shell work and testable in one pass.

**5. AI affordance: purpose and privacy.** (F5A-07.)
Impact: medium-high — repeated on every page, and it is a trust surface, not a cosmetic one. Risk: low to implement, but blocked on a product answer about the assistant's data scope. Effort: small once that answer exists.
Ranked fifth only because of the dependency. If Ryan answers the scope question early, this is the cheapest high-value change on the list.

Below the line, in order: dashboard zero-category collapse (M-02, likely folds into item 1's taxonomy work), banner rewrite (F5A-01 product half), color legend (M-03), offline reassurance clause (M-05), Connections IA consolidation (F5A-06, gated on M-04).

---

## Revised Design Direction

Three principles, offered as the through-line for whatever Task 2 turns out to be. They are deliberately narrow enough to be checkable in review.

**1. Every surface states its scope in its own title.**
The recurring-charge page is the acute case, but the rule generalizes: a page that says Subscription Tracker and shows rent has broken the contract its title made. Applied consistently, this also settles the Data Sources / Connected Accounts split — two destinations whose titles do not distinguish them should be one destination whose body does.

**2. Every absence explains itself and offers the next action, in the same place.**
Payroll already does this and is the pattern to copy. Empty (LL dashboard), unpopulated (Goals), denied (LL planning route), and offline all belong to one family. Two rules make the family consistent: never render the skeleton of a populated state to a user who has nothing (the LL dashboard's zero-filled category rows read as failure), and never put the instruction and its action in different parts of the screen (Goals). A denied state additionally must explain without revealing what other entities can do.

**3. Density is earned by information, not spent on structure.**
Half the Personal dashboard is empty category tracks. The mobile transactions table spends its width on a grid the phone cannot show. The recurring-charge queue spends twenty rows without ever saying how many there are. In each case the fix is the same shape: show what carries information, count and collapse what does not, and let the user expand it. Weekly Check-In already gets this right and is the internal reference.

Mobile gets one additional rule that follows from the entity model: **the phone must always answer "whose money am I looking at."** Desktop answers it persistently; phone currently does not.

Applied together these are a polish program, not a redesign. Nothing above changes the navigation model, the entity model, the visual language, or the data model. The intent is that a user's second session requires meaningfully less inference than their first.

---

## Open Questions For Ryan

These need a product decision before the corresponding change can be specified. I have deliberately not resolved them.

1. **What is the recurring-charge page for?** Is it a subscription-cancellation tool that happens to detect other recurring charges, or a complete recurring-spend register? The rename, the grouping, and the queue design all follow from this answer, and it cannot be inferred from the screenshots. *(Blocks priority 2.)*

2. **Can detection distinguish categories of recurring charge** — subscription vs. bill vs. payroll/benefit — or would grouping require manual classification by the user? If grouping is not available, the queue needs a different organizing principle. *(Blocks priority 2.)*

3. **What data can Ask Opus see, is it scoped to the current entity, and are conversations stored?** The visible privacy line cannot be written until this is answered, and answering it may itself be a product change. *(Blocks priority 5.)*

4. **Is the demo's category drift intentional demonstration content or accumulated drift?** Determines whether the seed is reconciled or the drift is deliberately explained in demo framing. *(Blocks priority 1.)*

5. **Should the demo seed include goals as a permanent part of the demo contract**, and if so what shapes (debt payoff, savings, both)? *(Blocks priority 1.)*

6. **What is the intended first-run path for a new entity like Luxe Legacy** — connect an account, import a file, or manual entry? The empty state must name one specific next action, and picking one is a product decision. *(Blocks priority 3.)*

7. **Is Data Sources meant to be a permanent destination or a task-linked setup surface?** This is the F5A-06 decision, and it should probably be taken together with the broader question of how a user discovers capabilities at all (M-04) rather than in isolation.

8. **Are transaction categories user-editable from the mobile transactions list?** If they are, the mobile row design needs an affordance for it; if not, the row can stay read-only and simpler.

---

## Parked Or Low-Value Ideas

Considered and set aside, recorded so they are not re-proposed:

- **Adding a scroll-cue gradient to the mobile transactions table.** Closes F5A-03 on paper without addressing the cost. Acceptable only as an explicit mitigation if the row redesign is rejected.
- **Adding Data Sources to persistent navigation.** Twelfth nav item for a once-per-setup task; makes daily destinations harder to find. See F5A-06.
- **Suppressing or auto-dismissing the category-drift banner.** 5A is right to refuse this and I agree; a truthful warning about wrong totals should not be quieted for polish.
- **Redesigning the dashboard category visualization** (donut, treemap, etc.). The bar list is fine; the problem is what is in it, not how it is drawn.
- **Onboarding tour or first-run coach marks.** Compensates for unclear surfaces instead of clarifying them, and adds a maintenance burden per surface.
- **Renaming entity tabs from abbreviations to full names.** Tempting — "BFM" and "LL" are opaque to a new user — but these are the user's own entities and they named them. Not a design decision to take on their behalf.
- **Reworking Weekly Check-In.** It is the best surface in the packet. Leave it alone.
- **Any change to the mobile drawer.** Working, tested, and easy to break.

---

## Implementation Notes For Codex

No implementation code is provided, and nothing here selects a work block. Each item lists affected surfaces, intended user outcome, acceptance signals, dependencies, and risks, so intake can classify it as adopt / ignore / park / Ryan-decision.

### IN-01 — Demo seed fidelity (from F5A-01 seed half, F5A-02)

*Affected surfaces:* synthetic demo seed / demo contract. Personal dashboard, Short-Term Planning as observed outputs.
*Intended outcome:* a reviewer opening the demo sees a healthy, representative product rather than a maintenance warning and an unexercised feature.
*Acceptance signals:* Personal dashboard loads with no category-drift banner (or with a banner that is deliberate and explained as demo content); Short-Term Planning shows at least one debt-payoff and one savings goal in a representative mid-progress state; the count of zero-activity categories on the dashboard drops materially.
*Dependencies:* Ryan questions 4 and 5.
*Risks:* low. Must not alter production data paths, entity isolation, or category domain logic. Seeded goals must be plainly synthetic and must not imply real obligations.

### IN-02 — Recurring charges revision (from F5A-05)

*Affected surfaces:* BFM Subscriptions page — title, section order, group headers, queue controls, dismissed/undo affordance. Navigation label if the page is renamed.
*Intended outcome:* the user can tell what the page manages, how much work is waiting, and what each control does, before acting.
*Acceptance signals:* the page title names the actual object set; the user's tracked set appears before the detection queue; a visible count of items awaiting review that decrements on action; accept/dismiss controls carry visible text labels; an undo path exists at the point of dismissal; existing accessible names are preserved or improved, never weakened.
*Dependencies:* Ryan questions 1 and 2. Grouping depends on what the detector can classify.
*Risks:* medium — the largest structural change proposed. Reordering watchlist above the queue changes an established page for any existing user. Renaming affects navigation, page title, and possibly URLs; if URLs change, the old path should redirect rather than 404. Do not change detection thresholds as part of this work; a labeling change that also changes what is detected will make regressions impossible to attribute.

### IN-03 — Luxe Legacy first-use and denied-route states (from F5A-04)

*Affected surfaces:* LL dashboard empty state; entity-denied route redirect target.
*Intended outcome:* a new-entity user understands there is no data yet and what to do about it; a user who hits an unsupported route understands why they were moved.
*Acceptance signals:* with zero transactions, the LL dashboard shows a named next action and suppresses zero-filled category scaffolding; a denied planning/payroll URL still redirects to the LL dashboard and now surfaces a plain-language notice naming the unavailable capability; the notice never names or implies capabilities in other entities; the existing fail-closed route test continues to pass unchanged.
*Dependencies:* Ryan question 6.
*Risks:* low, with one caveat — the denied-route notice is a message rendered after a security redirect. Message content must be derived from the requested route only, never from the user's access in other entities, or the boundary leaks through the copy.

### IN-04 — Mobile transactions row hierarchy and mobile entity context (from F5A-03, M-01)

*Affected surfaces:* Transactions results below the tablet breakpoint; mobile header across all surfaces.
*Intended outcome:* every transaction field is readable on a 390px screen without horizontal movement; the current entity is visible on every mobile screen.
*Acceptance signals:* at 390px, no horizontal scroll is required to read description, category, date, and amount; the document does not overflow; filters remain as built; the current entity name is visible in the mobile header on every route; the entity marker is not itself a switcher.
*Dependencies:* Ryan question 8 for row affordances.
*Risks:* low-medium. The `min-width: 560px` rule and its wrapper are load-bearing at tablet width — scope the change to the phone breakpoint only. Do not touch drawer markup while editing the mobile header; drawer focus, containment, Escape, scrim, and scroll-lock behavior must retest clean.

### IN-05 — AI affordance purpose and privacy (from F5A-07)

*Affected surfaces:* the `Ask Opus` trigger on every page; the chat panel header/first-run area.
*Intended outcome:* the user can tell what the control does and what happens to what they type, before they type it.
*Acceptance signals:* the visible glyph is no longer a question mark; a visible text label accompanies it at desktop widths; the chat panel states data scope and retention in one line; the existing accessible name is preserved; the statement matches actual behavior.
*Dependencies:* Ryan question 3 — hard blocker. Do not write privacy copy ahead of a confirmed answer.
*Risks:* low technically, high if the copy overstates. An inaccurate privacy line is worse than no line.

### IN-06 — Category-drift banner rewrite (from F5A-01 product half)

*Affected surfaces:* dashboard warning banner component.
*Intended outcome:* the user understands what is wrong, what it affects, and how to resolve it.
*Acceptance signals:* the banner appears below the page title; copy names the user-visible consequence rather than an internal filename; the reassignment action is a primary control; the banner can be dismissed and reappears if the underlying count changes.
*Dependencies:* IN-01 should land first, so the banner is evaluated against real drift rather than seed drift.
*Risks:* low. Dismissal must be scoped to the current condition — a permanently dismissible warning about miscategorized totals is a data-accuracy risk, not a polish win.

### IN-07 — Dashboard zero-category collapse and color legibility (from M-02, M-03)

*Affected surfaces:* Personal and BFM dashboard category sections.
*Intended outcome:* the first screen carries information rather than structure; budget states are legible without relying on hue.
*Acceptance signals:* categories with no activity are collapsed behind a labeled expandable count; if the two-column layout remains, each column's rule is labeled; over-budget rows carry a non-color signal in addition to red; the color scheme is explained once where it is introduced.
*Dependencies:* IN-01 — the drift is what inflated the zero rows; re-measure after the seed is fixed, since part of this may resolve itself.
*Risks:* low. Collapsing must not hide a category with any activity in the selected period, including negative or refund rows.

### Cross-cutting notes

- **Sequence:** IN-01 first (cheap, unblocks measurement of IN-06 and IN-07), then IN-03 and IN-04 (low-risk additive), then IN-02 (largest), with IN-05 slotted wherever Ryan's answer arrives.
- **Regression surface to re-run after any of these:** synthetic smoke, the installed-Chrome suite including drawer focus/containment/Escape/scroll-lock, entity isolation and denied-route behavior, and the zero-console-warning baseline.
- **Do not bundle** copy changes with structural changes in a single block where they touch the same surface. IN-02 in particular will be hard to review if the rename and the reordering land together with detection changes.
- **Every recommendation here is opinion evidence.** Classification, ordering, and acceptance remain with Codex and Ryan.

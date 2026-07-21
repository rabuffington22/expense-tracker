# Waterfall Payoff Contract

Applies to work block 4X, Phase 4 Tasks 1N.6-1N.7, `P3-3E-03`, `P3-3E-05`, and the focused `P3-3E-C01` regression slices.

## Rolling input

- The selected Waterfall month owns the payoff context.
- The payoff window is that calendar month plus the two immediately preceding calendar months, including year boundaries.
- Each month contributes BFM income minus effective, reportable BFM expenses as one signed integer-cent surplus.
- Positive, zero, and negative monthly results all remain in the window and denominator.
- A calendar month with no eligible rows contributes zero. The application has no separate data-completeness signal, so the month must not silently disappear from the fixed period.
- The three signed values are averaged once and rounded to the nearest cent. The displayed average and payoff helper receive that same integer-cent value.

## Payoff result

- Non-positive average surplus or non-positive credit-card debt produces no payoff estimate.
- Positive debt and positive average surplus use the exact ratio `debt / average surplus`.
- Displayed payoff months round that ratio upward to a whole month, so debt that remains can never render as zero months.
- The payoff date uses the same exact ratio converted at 30.44 days per month and rounded upward to a whole day.
- The template labels the value as a three-month signed average. When it is non-positive, the page states that the signed average leaves no surplus available for paydown.

## Preserved boundaries

- Six-month trend navigation and chart behavior remain unchanged.
- Personal and BFM retain their intended shared Waterfall read model; Luxe Legacy remains denied before route handling.
- Waterfall reads do not mutate financial rows.
- Task 1N.8 tax normalization, migrations, historical remediation, broader UI work, authentication, live systems, and publication remain outside 4X.

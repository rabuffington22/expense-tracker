# Waterfall Tax Input Contract

Date: 2026-07-21

Work block: 4Y — Waterfall Tax Input Truthfulness

Finding: `P3-3E-06`

## Canonical Value

Waterfall parses the optional `tax_rate` query value once and converts it to one integer basis-point value before calculation or rendering.

- Parse with decimal semantics.
- Reject non-finite values.
- Round once to the nearest basis point using half-up rounding.
- Accept normalized values from 0 through 9,999 basis points (`0.00%` through `99.99%`).
- Use the existing 2,200-basis-point (`22.00%`) default when input is omitted, blank, malformed, non-finite, negative, 100% or greater, or rounds outside the accepted range.

## Reconciliation

The normalized basis-point value is the only tax input for:

- the percentage rendered in both Waterfall tax controls;
- actual owner take-home;
- revenue-mode owner take-home;
- take-home-mode gross salary and required revenue.

The browser passes trimmed input to the server without stripping signs or otherwise reinterpreting invalid text. Rendering formats the accepted basis points directly, preserving up to two decimal places and removing unnecessary trailing zeros.

## Boundaries

This contract does not change Waterfall payoff averaging or duration, budget inputs, database state, entity access, authentication, or production behavior. Personal and BFM retain their intended shared Waterfall read model, Luxe Legacy remains denied before route handling, and publication remains separately gated.

## Maintained Verification

`scripts/smoke_test.py` section 8a8 covers helper and rendered-route behavior for omitted, blank, malformed, non-finite, negative, boundary, extreme, zero, integer, and decimal inputs; actual, target, and take-home-mode reconciliation; Personal/BFM behavior; Luxe Legacy denial; denied networking; database preservation; and exact temporary cleanup.

# PR65 Decision Method Ownership Guard Enrichment Report

Date: 2026-05-08

## Verdict

PASS as dormant substrate enrichment.

PR65 adds no positive affordances. It adds five duplicate/routing absence records that protect ownership boundaries between adjacent decision-method cards.

This slice is intentionally narrow. It does not try to enrich every remaining low-absence record. It handles one coherent failure mode:

> A source names adjacent methods, but the current model should consume them as inputs or examples, not promote them as its own standalone affordance.

## What Changed

New dormant artifact:

- `data/compiled/model_affordances/affordances_v27.json`
- `data/compiled/model_affordances/quality_report_v27.md`

v27 metadata:

- Records: 222
- Affordances: 268
- Absence records: 465
- Schema failures: 0
- Source quote rejections: 0

Delta from v26:

- +0 affordances
- +5 absence records
- +0 runtime imports

## Added Absence Records

### `base-rates`

Added `standalone-system-2-humility-or-debiasing-affordance`.

Why: the source names System 2, motivated reasoning, cognitive entrenchment, scientific method, and humility around base-rate use. Those are important, but they do not create a separate Base Rates transaction. The operational contract remains outside-view reference-class anchoring, with separate records owning deliberation, debiasing, and intellectual humility.

### `expected-value`

Added `standalone-reference-class-forecasting-affordance`.

Why: reference classes are source-backed inputs to EV reasoning, but the distinct reference-class anchoring transaction belongs to `base-rates`. Expected value should consume credible priors as inputs to weighted payoff comparison, not promote a second reference-class affordance.

Added `standalone-decision-tree-scenario-or-game-theory-affordance`.

Why: decision trees, scenario analysis, known/unknowns, and game theory are source-backed methods that can feed EV reasoning. They do not add a separate Expected Value affordance beyond probability-weighted payoff comparison, assumption stress testing, and tail-risk boundaries.

### `trade-offs`

Added `standalone-compression-comprehensiveness-affordance`.

Why: compression versus comprehensiveness appears as a communication example of balancing detail and engagement. It should not become a Trade Off affordance unless the case also requires allocation-backed sacrifice, hidden-cost naming, or priority reallocation. Compression-specific behavior is better owned by abstraction, simplification, information-theory, or complexity-bias-resistance records.

Added `standalone-minmax-game-theory-affordance`.

Why: minmax and maxmin are source-backed game-theory analogies for calculated trade-offs, but standalone counterparty payoff mapping belongs to game-theory-payoffs or Nash-style records. Trade-offs should promote the allocation-backed sacrifice contract, not absorb game theory.

## Explicit Non-Changes

No positive affordances were added.

No runtime behavior was changed.

Jason's incentives/systems audit and Kuhn's optionality/second-order audit are intentionally left for the next rings. They are good candidates, but mixing them into PR65 would make this PR less legible.

## Quality Rationale

This PR is not about adding more knowledge by volume. It is about making the existing knowledge base less likely to overclaim ownership.

The sources often mention adjacent methods because real reasoning is interconnected. That is useful for human understanding, but risky for a future decoder if every mentioned method becomes eligible under the current model. These absence records make the boundary explicit:

- `base-rates` owns outside-view prior anchoring, not generic debiasing.
- `expected-value` owns weighted payoff comparison, not every method that can supply EV inputs.
- `trade-offs` owns allocation-backed sacrifice, not every example of balancing.

This should help future packet or decoder work reject, defer, or route a nominated card without inventing a new positive card.

## Runtime Boundary

PR65 remains dormant. It does not change:

- live `/lolla` behavior;
- pipeline lane logic;
- packet producer defaults;
- prompts;
- renderer behavior;
- artifact auto-selection.

The compiled v27 artifact is review substrate only.

## Next Audit Direction

The next coherent rings are:

1. Incentives and systems broad-card overactivation guards.
2. Optionality and second-order ownership/treatment refinement.
3. Zero-absence intentional records recheck only if new source evidence justifies it.
4. Later, packet stress work once substrate quality is stable enough.

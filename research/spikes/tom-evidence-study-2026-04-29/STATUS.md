---
status: experimental
created: 2026-05-04
production_doctrine: false
---

# Stakeholder Assumption Check Spike Status

This spike explores whether Lolla should add a narrow stakeholder-assumption check inspired by Theory-of-Mind prompting research.

The product goal is not to infer people's inner lives. The goal is to catch cases where Lolla's advice already depends on an implicit claim about another actor's knowledge, interpretation, cooperation, power, silence, retaliation, or exit.

## Current Conclusion

Graduate only as a **Stakeholder Assumption Check**, not as a full ToM lane.

The useful shape:

- identify the actor the plan depends on
- identify what the advice assumes about that actor
- classify the assumption as grounded, plausible, or speculative
- surface only when the assumption changes the plan

## Known Prototype Failure

An earlier local prototype run over-inferred knowledge from relationship closeness. In the Marcus case, it treated Lina's closeness to Marcus as evidence that she knew the exact equity ask and platform details. That may be plausible, but it is not grounded unless the transcript establishes that Marcus told her.

Production doctrine must therefore downgrade role/closeness inferences to `plausible`, never `grounded`, unless the transcript explicitly establishes the actor's knowledge.

## Explicit Non-Goals

- no visible "Theory of Mind" user-facing section
- no stakeholder emotion cards
- no broad perspectives brief
- no numeric confidence scores
- no speculative mental-state claims in chat or memo
- no trigger merely because a third party exists

## Evidence Status

Insufficient for production.

The next validation slice is offline and fixture-based:

1. annotate archived cases
2. build a conservative trigger harness
3. score whether the check adds non-duplicative plan changes
4. keep full `/lolla` runs for late product validation only

# Pre-Step-6 High-Clutter Duplicate/Conflict Readout

Date: 2026-05-18

Status: research-only clutter/control readout. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1,
V60, the canonical knowledge base, or public output.

Related:

```text
research/pre-step6-hybrid-handoff-fixtures/founder-grant-marcus-equity.high-clutter.hybrid-handoff.v1.json
research/pre-step6-rendered-hybrid-answer-cores/founder-grant-marcus-equity.high-clutter.native.rendered-hybrid-answer-core.v1.json
scripts/research/pre_step6_hybrid_handoffs.py
scripts/research/pre_step6_pressure_card_consumption.py
tests/test_pre_step6_hybrid_handoffs.py
tests/test_pre_step6_pressure_card_consumption.py
```

## Question

Can the rendered hybrid surface reduce private clutter while preserving the live
tension?

This slice tests three failure modes:

```text
duplicate pressure repeated as multiple visible caveats
real conflict flattened into a false synthesis
correct but low-marginal-value artifacts made loud
```

## Why No New Mode Yet

The test deliberately did not add `clutter_reduction`.

The starting hypothesis was that current `card_first` might be enough if it can
carry:

```text
one primary pressure card
one contested raw inspect-more nuance
small quiet receipts for demoted artifacts
```

That keeps Step 6 as the reasoner. Deterministic code records what was demoted
and why; it does not decide the final advice.

## What Changed

`card_first` now allows optional `quiet_receipts`, capped at 3.

A quiet receipt is not public answer content and not an answer obligation. It is
a receipt for why a true or plausible artifact stayed quiet:

```text
source_raw_handoff
artifact_id
why_quiet
reactivate_if
do_not_elevate_into
```

The renderer adds:

```text
QUIET RECEIPTS
...
Treat quiet receipts as demotion receipts, not answer obligations.
```

This is intentionally weaker than `quiet_guidance`. `quiet_guidance` belongs to
`no_extra_pressure`. `quiet_receipts` belongs to `card_first` and exists only to
prevent duplicate or low-marginal-value artifacts from disappearing without a
trace.

## Fixture Shape

Case:

```text
founder-grant-marcus-equity.high-clutter
```

Handoff:

```text
handoff_mode: card_first
source_pressure_card: founder dependency-system pressure card
inspect_more: 1 contested item
quiet_receipts: 2 items
```

The contested inspect-more item recovers false-precision caution:

```text
Keep valuation uncertainty as support, not a second primary pressure.
Do not let $9-13M exit math carry the equity recommendation until buyer assumptions are tested.
```

Quiet receipts demote:

```text
founder_duplicate_middle_instruments
founder_misfit_architecture_note
```

Rendered handoff size:

```text
2,364 chars
```

## Native Consumption

A native Step-6-style consumer received:

```text
current control answer core
rendered high-clutter hybrid handoff
strict JSON answer-core contract
public machinery hygiene constraints
```

The resulting answer core is 1,499 chars.

It preserved:

```text
dependency-system framing
full equity/title/board is premature
vague delay or flat rejection can trigger Marcus disengagement
sprint evidence gates
exit math only as false-precision caution
numbers should not carry the decision
```

It avoided:

```text
long instrument catalog
phantom equity / revenue share list
technical or software architecture diagnosis
private machinery leakage
```

## Result

Pass, narrowly.

The existing `card_first` surface can express this first high-clutter founder
case if it gets one small addition: quiet receipts. The result did not require a
new `clutter_reduction` mode.

The pass is narrow because the rendered private handoff is now 2,364 chars and
the public answer core is 1,499 chars. That is still under cap, but it is close
enough that future clutter slices should be hostile to added fields and
duplicate receipts.

## Decision

```text
high_clutter_founder_passes_with_card_first_plus_quiet_receipts
do_not_add_clutter_reduction_mode_yet
quiet_receipts_are_demotion_receipts_not_answer_obligations
duplicate_pressure_can_be_recorded_without_being_repeated
real_tension_survived_as_staged_partnership_not_vague_delay_or_flat_rejection
reasoning_bundle_still_not_earned
runtime_subagents_still_not_earned
no_product_promotion
```

## Next Gate

This still does not prove general clutter handling.

Next useful checks:

```text
one non-founder conflict case where two live pressures genuinely pull against each other
semi-blind comparison: current control vs raw-only vs rendered hybrid
source/overclaim audit on any rendered-hybrid winner
```

2026-05-18 follow-up: the non-founder conflict check now exists in:

```text
research/pre-step6-phd-conflict-preservation-readout-2026-05-18.md
```

It passed with the existing PhD `card_first` handoff. The next gate is
semi-blind comparison.

Promotion remains blocked until clutter/conflict and blind or semi-blind
comparisons show durable lift or equal quality with lower attention load.

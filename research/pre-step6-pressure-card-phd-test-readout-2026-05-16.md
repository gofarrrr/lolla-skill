# Pre-Step-6 Pressure Card PhD Test Readout

Date: 2026-05-16

Status: research-only replay readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-phd-producer-compressor-test-readout-2026-05-16.md
research/pre-step6-pressure-card-fixtures/third-year-phd-student.native.pressure-card.v1.json
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

Can a smaller Step-6 consumption card preserve the useful PhD worker pressure
while avoiding the full `reasoning_artifact.v1` compression failure?

The card must:

```text
return exact JSON
validate as pre_step6_pressure_card.v1
stay under 900 serialized chars
preserve fallback executability
preserve Silva/data access
preserve relax/discard/risk instructions
avoid final-answer prose and new facts
```

## Setup

Input was the rich PhD `reasoning_artifact.v1` from the producer/compressor
test. That prior path preserved meaning but failed the 1,500-character full
artifact cap across repeated retries:

```text
1,677 -> 1,617 -> 1,569 -> 1,540 validator chars
```

The native subagent saw only that artifact and was asked to compress it into:

```text
schema_version
pressure
boundary
relax_if
discard_if
risk_if_ignored
```

The first attempt used only a total target. The second attempt added hard
per-field budgets.

## Criteria

Pass criteria:

```text
exact key set
validator accepts the payload
serialized JSON <= 900 chars
fallback/Silva/data gates survive
relax_if, discard_if, and risk_if_ignored remain actionable
no new unsupported facts
```

Stronger replay target:

```text
serialized JSON <= 760 chars
```

## Results

| Attempt | Validator Size | Exact JSON/Keys | Gates Preserved | Cap |
| --- | ---: | --- | --- | --- |
| Native pressure card, no field budgets | 1,070 | Yes | Yes | Fail |
| Native pressure card, field budgets | 689 | Yes | Yes | Pass |

The passing card preserved:

```text
fallback executability
Silva/data access
dated evidence checks
fallback stop-loss
risk of fictional fallback / missing-data feasibility
```

## Interpretation

This is the first positive compression result after the full-artifact blocker.

The result does not say "build subagents now." It says the likely Step-6
consumption surface is smaller than `reasoning_artifact.v1`.

The full worker artifact is still useful as an audit/provenance object, but it
is too bulky as the default Step-6 handoff. Step 6 appears to need a pressure
card:

```text
what pressure matters
what boundary must hold
when to relax it
when to discard it
what breaks if ignored
```

The important caution is that the model needed explicit field budgets. A total
target alone produced a semantically good but oversized card. The pass came only
after the prompt constrained each field.

## Decision

```text
pressure_card_shape_passes_first_native_phd_slice
field_budgets_are_required
full_reasoning_artifact_v1_remains_audit_not_default_consumption
do_not_build_reasoning_bundle_yet
do_not_wire_workers_into_live_lolla
```

## Next Options

Option A: repeat pressure-card replay on founder and consultant.

```text
Goal: test whether this was a PhD-only success.
Pass: both preserve their controlling gates under 900 chars.
Kill: either needs repeated retries or loses the main boundary.
```

Option B: compare Step-6-style consumption.

```text
raw reasoning_artifact.v1 answer core
vs pressure-card answer core
vs current control
```

Option C: build a research-only pressure-card renderer.

```text
Keep full reasoning_artifact.v1 for audit.
Render pre_step6_pressure_card.v1 for Step 6.
Validate exact keys, caps, gate survival checks, and public machinery hygiene.
```

Recommendation:

```text
run two more pressure-card replays before adding a renderer
```

Reason:

```text
one passing PhD retry is promising but not enough to justify new machinery
```

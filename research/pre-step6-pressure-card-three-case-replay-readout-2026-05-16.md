# Pre-Step-6 Pressure Card Three-Case Replay Readout

Date: 2026-05-16

Status: research-only replay readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-pressure-card-phd-test-readout-2026-05-16.md
research/pre-step6-pressure-card-fixtures/third-year-phd-student.native.pressure-card.v1.json
research/pre-step6-pressure-card-fixtures/founder-grant-marcus-equity.native.pressure-card.v1.json
research/pre-step6-pressure-card-fixtures/mid-level-consultant-report-2.native.pressure-card.v1.json
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

Does `pre_step6_pressure_card.v1` generalize beyond the PhD example when native
subagents receive explicit field budgets?

## Method

Three existing worker artifacts were compressed by native subagents into:

```text
schema_version
pressure
boundary
relax_if
discard_if
risk_if_ignored
```

All prompts used the same hard budgets:

```text
pressure <= 120 chars
boundary <= 220 chars
relax_if <= 95 chars
discard_if <= 95 chars
risk_if_ignored <= 130 chars
target serialized JSON <= 760 chars
hard validator max 900 chars
```

Each case had explicit gate-survival checks:

```text
PhD: fallback executability and Silva/data access
Founder: dependency-system framing and observable gates before equity/title/board
Consultant: independent counsel, channel distinctions, Wednesday conduct, no self-directed evidence
```

## Results

| Case | Validator Size | JSON/Schema | Gate Survival | Cap |
| --- | ---: | --- | --- | --- |
| PhD, retry with budgets | 689 | Pass | Pass | Pass |
| Founder | 682 | Pass | Pass | Pass |
| Consultant | 679 | Pass | Pass | Pass |

Prior contrast:

```text
full reasoning_artifact.v1 strict JSON outputs: 2,810-3,134 chars
compact skeleton PhD: 1,769 chars
separate PhD compressor: 1,677 -> 1,617 -> 1,569 -> 1,540 chars
pressure cards with field budgets: 679-689 chars
```

## Interpretation

The pressure-card shape now has a real positive signal.

What appears to work:

- keep rich `reasoning_artifact.v1` for worker/audit provenance;
- render a much smaller Step-6 consumption card;
- give the native producer strict per-field budgets;
- validate exact keys and serialized size;
- assert case-specific gate survival instead of trusting semantic vibes.

What is still not proven:

- that Step 6 writes a better final answer from cards than from raw artifacts;
- that cards help in conflict/duplicate/high-clutter cases;
- that admission should launch workers in live `/lolla`;
- that `reasoning_bundle.v1` is needed.

The result weakens the old blocker:

```text
cap-obedient compression is no longer unsolved for Step-6 consumption
```

But it does not remove the architecture burden:

```text
final-answer lift is still unproven
worker orchestration is still unpromoted
```

## Decision

```text
pressure_card_shape_passes_three_case_native_replay
field_budgets_are_required
use pressure cards as the next challenger to raw artifacts
do_not_build_reasoning_bundle_yet
do_not_wire_workers_into_live_lolla
```

## Next Slice

Run a Step-6-style consumption comparison:

```text
current control answer core
raw reasoning_artifact.v1 answer core
pressure-card answer core
```

Criteria:

```text
grounding / no invented facts
decision-useful specificity
preserves hard boundaries
preserves relaxation and discard conditions
avoids overclaim
avoids machinery leakage
readability and actionability
```

Promotion remains blocked unless pressure-card consumption beats careful raw
artifact consumption in final-answer quality, not only private compactness.

2026-05-16 follow-up: the answer-consumption comparison now exists in:

```text
research/pre-step6-pressure-card-answer-consumption-readout-2026-05-16.md
```

It found a mixed result:

```text
PhD: tie_stop against raw
founder: pressure_wins against raw
consultant: raw_wins against pressure
```

So pressure cards are useful, but not a replacement for raw artifacts. The next
research target is card-first with raw available for contested or lossy pressure.

# Pre-Step-6 Hybrid Handoff Renderer Readout

Date: 2026-05-18

Status: research-only renderer readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-hybrid-card-first-raw-available-readout-2026-05-16.md
research/pre-step6-hybrid-handoff-fixtures/founder-grant-marcus-equity.hybrid-handoff.v1.json
research/pre-step6-hybrid-handoff-fixtures/third-year-phd-student.hybrid-handoff.v1.json
research/pre-step6-hybrid-handoff-fixtures/mid-level-consultant-report-2.hybrid-handoff.v1.json
scripts/research/pre_step6_hybrid_handoffs.py
tests/test_pre_step6_hybrid_handoffs.py
```

## Question

Can the current hybrid verdict be rendered into a small, repeatable Step-6
private handoff surface?

Target shape:

```text
card first
raw inspect-more only when justified
strict source validation
bounded raw excerpts
bounded rendered handoff
no product/runtime promotion
```

## What Landed

Dormant validator/renderer:

```text
scripts/research/pre_step6_hybrid_handoffs.py
```

Fixture schema:

```text
pre_step6_hybrid_handoff.v1
```

Core fields:

```text
schema_version
status
runtime_policy
case_id
source_pressure_card
inspect_more
notes
```

Inspect-more fields:

```text
reason
source_raw_handoff
artifact_id
raw_excerpt
use_only_to_recover
do_not_expand_into
```

Allowed inspect reasons:

```text
lossy
contested
high_stakes
missing_nuance
```

Caps:

```text
max inspect_more items: 2
max raw excerpt: 700 chars
max rendered handoff: 3,200 chars
```

## Fixtures

| Case | Handoff Shape | Reason |
| --- | --- | --- |
| Founder | Card only | Pressure-only already beat raw |
| PhD | Card + 1 inspect-more | Restore base-rate humility |
| Consultant | Card + 2 inspect-more | Restore counsel-incentive and Wednesday-protocol nuance |

Rendered sizes:

```text
founder: 1,212 chars
PhD: 1,604 chars
consultant: 1,980 chars
```

## Rendered Shape

The renderer preserves this order:

```text
STEP 6 PRIVATE PRESSURE
CARD
INSPECT MORE
STEP 6 RULE
```

The Step 6 rule is intentionally simple:

```text
Use the card as the default.
Inspect raw only for the named nuance.
Do not turn inspect-more material into extra sections.
```

## Validation

The test suite covers:

```text
all fixtures validate
all fixtures render under cap
card block appears before inspect-more
founder has no raw inspection
PhD restores base-rate humility
consultant restores counsel and Wednesday nuance
unknown inspect reasons are rejected
too many inspect-more items are rejected
unknown raw artifact ids are rejected
overlong raw excerpts are rejected
```

Observed focused command:

```text
PYTHONPATH=. pytest tests/test_pre_step6_hybrid_handoffs.py
```

Observed focused result:

```text
9 passed
```

Observed full research command:

```text
PYTHONPATH=. pytest tests/test_pre_step6_raw_artifacts.py tests/test_pre_step6_workpacks.py tests/test_pre_step6_pressure_card_consumption.py tests/test_pre_step6_hybrid_handoffs.py
```

Observed full result:

```text
62 passed
```

2026-05-18 renderer-rule update: after the rendered-consumption replay exposed
a missing risk-if-ignored instruction, the renderer was tightened. The rendered
sizes above reflect the tightened rule.

## Decision

```text
hybrid_handoff_renderer_passes_first_three_fixtures
card_first_raw_available_is_now_renderable
do_not_build_reasoning_bundle_yet
do_not_build_runtime_subagent_orchestration
do_not_wire_into_live_lolla
```

## Next Slice

The next useful check is a rendered-handoff consumption replay:

```text
give native Step-6-style consumers the rendered hybrid handoff
compare answer cores against raw-only and prior hybrid-authored cores
verify the renderer, not just the hand-authored prompt, preserves the lift
```

Promotion remains blocked until rendered hybrid handoffs show final-answer lift
or equal quality with lower Step-6 attention load across offline replays.

2026-05-18 follow-up: rendered-handoff consumption now exists in:

```text
research/pre-step6-rendered-hybrid-consumption-readout-2026-05-18.md
```

The first founder replay exposed a missing renderer instruction: the consumer
softened risk-if-ignored. The renderer was tightened to preserve
risk-if-ignored unless it clearly misfits. After that change, rendered
consumption preserved target lift in founder, PhD, and consultant.

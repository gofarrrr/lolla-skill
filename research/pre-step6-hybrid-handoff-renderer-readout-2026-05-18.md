# Pre-Step-6 Hybrid Handoff Renderer Readout

Date: 2026-05-18

Status: research-only renderer readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-hybrid-card-first-raw-available-readout-2026-05-16.md
research/pre-step6-hybrid-handoff-fixtures/founder-grant-marcus-equity.hybrid-handoff.v1.json
research/pre-step6-hybrid-handoff-fixtures/founder-grant-marcus-equity.high-clutter.hybrid-handoff.v1.json
research/pre-step6-hybrid-handoff-fixtures/third-year-phd-student.hybrid-handoff.v1.json
research/pre-step6-hybrid-handoff-fixtures/mid-level-consultant-report-2.hybrid-handoff.v1.json
research/pre-step6-hybrid-handoff-fixtures/mother-address-year.hybrid-handoff.v1.json
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
quiet no-extra-pressure mode for negative controls
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
handoff_mode
inspect_more
notes
```

`card_first` fields:

```text
source_pressure_card
inspect_more
quiet_receipts
```

`no_extra_pressure` fields:

```text
decline_reason
quiet_guidance.use_current_answer
quiet_guidance.preserve
quiet_guidance.do_not_add
```

In `no_extra_pressure`, `source_pressure_card` is forbidden and `inspect_more`
must be empty.

Inspect-more fields:

```text
reason
source_raw_handoff
artifact_id
raw_excerpt
use_only_to_recover
do_not_expand_into
```

Quiet receipt fields:

```text
source_raw_handoff
artifact_id
why_quiet
reactivate_if
do_not_elevate_into
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
max quiet_receipts: 3
max raw excerpt: 700 chars
max rendered handoff: 3,200 chars
```

## Fixtures

| Case | Handoff Shape | Reason |
| --- | --- | --- |
| Founder | Card only | Pressure-only already beat raw |
| Founder high-clutter | Card + 1 inspect-more + 2 quiet receipts | Recover false-precision caution while demoting duplicate/misfit artifacts |
| PhD | Card + 1 inspect-more | Restore base-rate humility |
| Consultant | Card + 2 inspect-more | Restore counsel-incentive and Wednesday-protocol nuance |
| Mother | No extra pressure | Sentinel for declining a worker/lens/raw expansion |

Rendered sizes:

```text
founder high-clutter: 2,364 chars
founder: 1,211 chars
PhD: 1,603 chars
consultant: 1,979 chars
mother: 1,343 chars
```

## Rendered Shape

The renderer preserves this order:

```text
STEP 6 PRIVATE PRESSURE
CARD
INSPECT MORE
QUIET RECEIPTS
STEP 6 RULE
```

`QUIET RECEIPTS` appears only when demoted artifacts need a private receipt.
They are rendered as non-obligations:

```text
Treat quiet receipts as demotion receipts, not answer obligations.
```

For `no_extra_pressure`, the renderer omits `CARD` and `INSPECT MORE`:

```text
STEP 6 PRIVATE PRESSURE
QUIET GUIDANCE
STEP 6 RULE
```

The Step 6 rule is intentionally simple:

```text
Use the card as the default.
Preserve the card's risk-if-ignored unless it clearly misfits.
Use relax/discard conditions to soften or skip pressure that is already handled.
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
founder high-clutter demotes duplicate/misfit artifacts with quiet receipts
mother has no pressure card and no raw inspection
PhD restores base-rate humility
consultant restores counsel and Wednesday nuance
unknown inspect reasons are rejected
too many inspect-more items are rejected
unknown raw artifact ids are rejected
overlong raw excerpts are rejected
too many quiet receipts are rejected
unknown quiet-receipt artifact ids are rejected
quiet mode rejects source_pressure_card
quiet mode rejects non-empty inspect_more
```

Observed focused command:

```text
PYTHONPATH=. pytest tests/test_pre_step6_hybrid_handoffs.py
```

Observed focused result:

```text
15 passed
```

Observed full research command:

```text
PYTHONPATH=. pytest tests/test_pre_step6_raw_artifacts.py tests/test_pre_step6_workpacks.py tests/test_pre_step6_pressure_card_consumption.py tests/test_pre_step6_hybrid_handoffs.py
```

Observed full result:

```text
72 passed
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
research/pre-step6-mother-quiet-sentinel-readout-2026-05-18.md
research/pre-step6-high-clutter-duplicate-conflict-readout-2026-05-18.md
```

The first founder replay exposed a missing renderer instruction: the consumer
softened risk-if-ignored. The renderer was tightened to preserve
risk-if-ignored unless it clearly misfits. After that change, rendered
consumption preserved target lift in founder, PhD, and consultant.

2026-05-18 quiet-sentinel follow-up: the mother negative-control fixture now
uses `handoff_mode: no_extra_pressure`. It renders no card and no raw
inspect-more block. Native consumption initially softened the monitored-channel
caution, so the preserve instruction was made explicit. The compact retest
produced a valid 964-character answer core that preserved the caution and
tripwires without adding worker/lens/leverage pressure.

2026-05-18 high-clutter follow-up: the first clutter fixture uses the existing
`card_first` mode plus optional `quiet_receipts`, not a new clutter mode. It
renders one contested inspect-more item and two quiet receipts. Native
consumption preserved dependency-system tension and false-precision caution
without repeating the instrument catalog or diagnosing software architecture.

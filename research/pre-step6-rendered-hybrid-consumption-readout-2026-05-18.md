# Pre-Step-6 Rendered Hybrid Consumption Readout

Date: 2026-05-18

Status: research-only rendered-consumption readout. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1,
V60, the canonical knowledge base, or public output.

Related:

```text
research/pre-step6-hybrid-handoff-renderer-readout-2026-05-18.md
research/pre-step6-rendered-hybrid-answer-cores/founder-grant-marcus-equity.native.rendered-hybrid-answer-core.v1.json
research/pre-step6-rendered-hybrid-answer-cores/founder-grant-marcus-equity.high-clutter.native.rendered-hybrid-answer-core.v1.json
research/pre-step6-rendered-hybrid-answer-cores/third-year-phd-student.native.rendered-hybrid-answer-core.v1.json
research/pre-step6-rendered-hybrid-answer-cores/mid-level-consultant-report-2.native.rendered-hybrid-answer-core.v1.json
research/pre-step6-rendered-hybrid-answer-cores/mother-address-year.native.rendered-hybrid-answer-core.v1.json
research/pre-step6-mother-quiet-sentinel-readout-2026-05-18.md
research/pre-step6-high-clutter-duplicate-conflict-readout-2026-05-18.md
scripts/research/pre_step6_pressure_card_consumption.py
tests/test_pre_step6_pressure_card_consumption.py
```

## Question

Does the actual rendered hybrid handoff preserve the answer-quality lift that
the hand-authored hybrid prompts showed?

This checks the renderer, not just the idea:

```text
render pre_step6_hybrid_handoff.v1
give rendered text to native Step-6-style consumers
validate resulting answer cores
check case-specific lift survived
```

## Method

Each native consumer received:

```text
current-control answer core
rendered hybrid handoff
strict JSON answer-core contract
public machinery hygiene constraints
```

Output schema:

```text
pre_step6_rendered_hybrid_answer_core.v1
```

Required renderer-followed flags:

```text
card_used_first
inspected_raw_only_for_named_nuance
no_extra_sections_from_inspect_more
```

All three must be `true`.

2026-05-18 follow-up: rendered answer-core fixtures now also declare
`handoff_mode`. `card_first` keeps the three flags above. `no_extra_pressure`
uses quiet-mode flags:

```text
quiet_mode_respected
no_card_pressure_added
no_raw_inspection_used
no_extra_sections_from_inspect_more
```

## Important Failure And Fix

The first founder rendered-consumption answer was valid but softened the card's
risk-if-ignored field. It preserved dependency framing and evidence gates, but
did not carry:

```text
vague delay or refusal may trigger Marcus disengagement
Jake/Lina/platform/client continuity risk
```

This exposed a renderer problem, not a model-syntax problem. The renderer's Step
6 rule was tightened from:

```text
Use the card as the default.
Inspect raw only for the named nuance.
```

to:

```text
Use the card as the default.
Preserve the card's risk-if-ignored unless it clearly misfits.
Use relax/discard conditions to soften or skip pressure that is already handled.
Inspect raw only for the named nuance.
```

After that change, the founder retest preserved the missing risk.

## Results

| Case | Rendered Handoff Shape | Result | Lift Preserved |
| --- | --- | --- | --- |
| Founder | Card only | Pass after renderer risk-rule fix | Dependency framing, measurement gates, vague-delay/disengagement risk |
| Founder high-clutter | Card + 1 inspect-more + 2 quiet receipts | Pass | Dependency-system tension plus false-precision caution, without instrument catalog or architecture diagnosis |
| PhD | Card + 1 inspect-more | Pass | Fallback/data gates plus base-rate humility |
| Consultant | Card + 2 inspect-more | Pass | Counsel-first channel distinction plus counsel-incentive and Wednesday protocol |
| Mother | No extra pressure | Pass after preserve-guidance tightening | Monitored-channel caution, reversible tripwires, humane trust repair without worker/lens/raw expansion |

Validator result:

```text
all rendered answer cores validate: yes
all renderer-followed flags true: yes
public machinery hygiene passes: yes
expected inclusions appear: yes
expected exclusions stay absent: yes
source hybrid handoffs validate: yes
```

Focused tests now assert the case-specific lift:

```text
founder: vague delay or flat refusal + Jake/Lina/platform/client continuity risk
founder high-clutter: unproven dependency system + false-precision caution + no catalog/architecture drift
PhD: broad PhD success-rate claims + humility checks + fallback gate
consultant: reflexive channel preference + audit-committee-first + Wednesday response
```

## Interpretation

This is the first pass where the full chain worked:

```text
pressure card
  -> hybrid handoff fixture
  -> renderer
  -> native Step-6-style consumer
  -> validated public answer core
```

The initial founder miss matters. It shows the renderer cannot merely display
the card. It must tell Step 6 how to treat card fields:

```text
pressure and boundary are primary
risk-if-ignored must usually survive
relax/discard conditions can soften or skip pressure
inspect-more raw text is only for named nuance
```

After that fix, rendered hybrid handoffs preserved the intended lift across all
three fixtures.

## Decision

```text
rendered_hybrid_consumption_passes_first_three_fixtures
risk_if_ignored_needs_explicit_renderer_instruction
card_first_selective_raw_inspection_remains_current_best_research_surface
reasoning_bundle_still_not_earned
runtime_subagents_still_not_earned
no_product_promotion
```

## Next Slice

The next useful check is a harder negative/control slice:

```text
mother no-worker sentinel
or a high-clutter duplicate/conflict case
```

Why:

```text
current fixtures show the renderer can preserve intended pressure
they do not prove it can handle duplicate/conflict clutter better than raw-only
```

2026-05-18 update: the mother quiet sentinel now passes after tightening the
preserve instruction for monitored-channel caution. The next negative/control
slice should be high-clutter duplicate/conflict.

2026-05-18 high-clutter update: founder high-clutter now passes with existing
`card_first` plus optional quiet receipts. The fixture preserved the
dependency-system conflict and exit-math caution while demoting duplicate
instrument pressure and architecture misfit pressure. A new `clutter_reduction`
mode is not earned yet.

Do not wire this into live `/lolla` before clutter/conflict and blind or
semi-blind comparisons show durable lift or equal quality with lower attention
load.

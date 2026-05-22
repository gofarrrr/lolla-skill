# Pre-Step-6 Pressure Card Answer Consumption Readout

Date: 2026-05-16

Status: research-only readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-pressure-card-three-case-replay-readout-2026-05-16.md
research/pre-step6-pressure-card-answer-cores/third-year-phd-student.native.pressure-answer-core.v1.json
research/pre-step6-pressure-card-answer-cores/founder-grant-marcus-equity.native.pressure-answer-core.v1.json
research/pre-step6-pressure-card-answer-cores/mid-level-consultant-report-2.native.pressure-answer-core.v1.json
research/pre-step6-pressure-vs-raw-comparisons/third-year-phd-student.pressure-vs-raw-comparison.v1.json
research/pre-step6-pressure-vs-raw-comparisons/founder-grant-marcus-equity.pressure-vs-raw-comparison.v1.json
research/pre-step6-pressure-vs-raw-comparisons/mid-level-consultant-report-2.pressure-vs-raw-comparison.v1.json
scripts/research/pre_step6_pressure_card_consumption.py
tests/test_pre_step6_pressure_card_consumption.py
```

## Question

Do compact pressure cards improve Step-6-style final answer consumption, or do
they only make private handoff text smaller?

## Method

Native subagents acted as Step-6-style consumers. Each received:

```text
current-control answer core
one validated pre_step6_pressure_card.v1
public-answer hygiene constraints
strict JSON answer-core contract
```

They did not receive the raw answer core. This tested whether the card could
recover useful final-answer lift from a smaller surface rather than by copying
the existing raw fixture.

The resulting answer cores were then compared against the previously authored
raw answer cores under local criteria.

Tie rule:

```text
pressure_tie_with_raw_stops
```

So pressure cards do not win by being shorter or merely equivalent.

## Results

| Case | Pressure Wins | Raw Wins | Ties | Decision | Main Finding |
| --- | ---: | ---: | ---: | --- | --- |
| PhD | 1 | 1 | 3 | `tie_stop` | Pressure sharpened fallback gate; raw preserved base-rate humility |
| Founder | 2 | 1 | 2 | `pressure_wins` | Pressure preserved fuller measurement chain and vague-delay risk |
| Consultant | 1 | 2 | 2 | `raw_wins` | Raw preserved counsel-incentive and Wednesday-protocol nuance |

All pressure answer cores validated:

```text
exact schema
source pressure-card refs exist and validate
source control-comparison refs exist and validate
expected inclusions appear
expected exclusions stay absent
public machinery hygiene passes
answer core length cap passes
```

## Interpretation

This is a useful mixed result.

Pressure cards are not just pretty compression. They can produce public-answer
lift from a small surface. The founder case is the clean positive result:

```text
smaller input
stronger measurement chain
clearer no-vague-delay risk
no machinery leakage
```

But pressure cards are not a safe replacement for raw artifacts. The consultant
case shows the cost of compression:

```text
raw preserved counsel-incentive testing
raw preserved a more concrete Wednesday protocol
pressure sharpened legal-conclusion/no-extra-proof boundaries
but did not beat raw overall
```

The PhD case is the shape of the middle:

```text
pressure sharpened fallback executability
raw preserved base-rate humility
overall result stopped at tie
```

## Decision

```text
pressure_cards_are_useful_consumption_surface
pressure_cards_do_not_replace_raw_artifacts
card_first_raw_available_is_now_the_best_research_shape
do_not_build_reasoning_bundle_yet
do_not_wire_workers_into_live_lolla
```

## What It Means

The likely architecture is no longer:

```text
full worker artifact directly to Step 6
```

and it is not:

```text
pressure card only
```

The better research target is:

```text
full reasoning_artifact.v1 retained for audit/provenance
compact pre_step6_pressure_card.v1 rendered for Step 6 first-pass consumption
Step 6 can inspect raw artifact when the card is contested, high-stakes, or too lossy
```

This explains the apparent tension:

- deterministic code can validate, cap, route, and preserve custody;
- native cognition can produce or consume compact pressure;
- Step 6 remains final arbitrator;
- the raw artifact remains available when the card loses nuance.

## Next Slice

Test the hybrid surface:

```text
pressure card as the visible first-pass input
raw artifact available only behind an inspect-more / contested-pressure path
```

Compare:

```text
raw-only answer core
pressure-only answer core
hybrid card-first answer core
```

Promotion stays blocked until hybrid beats raw-only in final-answer quality or
proves the same quality with meaningfully lower Step-6 attention load.

2026-05-16 follow-up: the hybrid contested-case comparison now exists in:

```text
research/pre-step6-hybrid-card-first-raw-available-readout-2026-05-16.md
```

It tested the two cases where pressure-only was tied or worse:

```text
PhD: hybrid_wins against raw after restoring base-rate humility
consultant: hybrid_wins against raw after restoring counsel-incentive and Wednesday-protocol nuance
```

So the current favored research target is:

```text
pressure card first
selective raw inspection only when the card is contested, lossy, or high-stakes
```

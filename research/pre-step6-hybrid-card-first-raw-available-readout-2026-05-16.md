# Pre-Step-6 Hybrid Card-First / Raw-Available Readout

Date: 2026-05-16

Status: research-only readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-pressure-card-answer-consumption-readout-2026-05-16.md
research/pre-step6-hybrid-answer-cores/third-year-phd-student.native.hybrid-answer-core.v1.json
research/pre-step6-hybrid-answer-cores/mid-level-consultant-report-2.native.hybrid-answer-core.v1.json
research/pre-step6-hybrid-vs-raw-comparisons/third-year-phd-student.hybrid-vs-raw-comparison.v1.json
research/pre-step6-hybrid-vs-raw-comparisons/mid-level-consultant-report-2.hybrid-vs-raw-comparison.v1.json
scripts/research/pre_step6_pressure_card_consumption.py
tests/test_pre_step6_pressure_card_consumption.py
```

## Question

After the pressure-only comparison produced mixed results, can a hybrid surface
do better?

Hybrid means:

```text
pressure card first
raw artifact available only when the card is contested or visibly lossy
```

The test focused only on the two contested cases from the previous slice:

```text
PhD: pressure-only tied raw because it lost base-rate humility
consultant: pressure-only lost to raw because it lost counsel-incentive and Wednesday-protocol nuance
```

Founder was not rerun because pressure-only already beat raw there. Adding raw
would mostly test clutter, not recovery from lossiness.

## Method

Native subagents acted as Step-6-style consumers.

Each received:

```text
current-control answer core
one pressure card as first-pass input
only the raw excerpt that the prior comparison said was missing
public-answer hygiene constraints
strict JSON answer-core contract
```

The resulting hybrid answer cores were compared against raw answer cores.

Tie rule:

```text
hybrid_tie_with_raw_stops
```

So hybrid wins only when it improves final-answer criteria, not when it merely
matches raw.

## Results

| Case | Hybrid Wins | Raw Wins | Ties | Decision | Main Hybrid Lift |
| --- | ---: | ---: | ---: | --- | --- |
| PhD | 2 | 0 | 3 | `hybrid_wins` | Keeps card's concrete fallback/data gates and restores base-rate humility |
| Consultant | 2 | 0 | 3 | `hybrid_wins` | Keeps card's legal/channel boundaries and restores counsel-incentive/Wednesday nuance |

Observed validator commands:

```text
python3 scripts/research/pre_step6_pressure_card_consumption.py research/pre-step6-hybrid-answer-cores/third-year-phd-student.native.hybrid-answer-core.v1.json --hybrid-answer-core
python3 scripts/research/pre_step6_pressure_card_consumption.py research/pre-step6-hybrid-answer-cores/mid-level-consultant-report-2.native.hybrid-answer-core.v1.json --hybrid-answer-core
python3 scripts/research/pre_step6_pressure_card_consumption.py research/pre-step6-hybrid-vs-raw-comparisons/third-year-phd-student.hybrid-vs-raw-comparison.v1.json --hybrid-comparison --repo-root .
python3 scripts/research/pre_step6_pressure_card_consumption.py research/pre-step6-hybrid-vs-raw-comparisons/mid-level-consultant-report-2.hybrid-vs-raw-comparison.v1.json --hybrid-comparison --repo-root .
```

## Interpretation

This is the cleanest signal so far.

The earlier paths each failed in a specific way:

```text
full reasoning_artifact.v1 directly to Step 6: too bulky
pressure card only: compact but sometimes lossy
raw artifact only: rich but higher attention load
reasoning bundle: still unearned
```

The hybrid path matches the actual need better:

```text
Step 6 sees the compact card first
raw remains available as custody and nuance
raw is inspected only when the card is contested, lossy, high-stakes, or incomplete
```

This is not a subagent-runtime conclusion. The key product-shape lesson is about
handoff surface, not orchestration:

```text
deterministic custody and validation
compact card-first rendering
raw artifact retained for audit and selective inspection
Step 6 final arbitration
```

## Decision

```text
hybrid_card_first_raw_available_beats_raw_on_two_contested_cases
pressure_cards_remain_useful_first_pass_surface
raw_artifacts_remain_required_for_lossy_or_contested_pressure
reasoning_bundle_still_not_earned
subagent_runtime_still_not_earned
no_product_promotion
```

## Caveats

This is still local research evidence:

```text
native consumers, not live /lolla
authored/local comparison criteria, not blind judging
two contested cases, not the full case set
raw excerpts were selected from known pressure-only losses
```

That last point is intentional for this slice. The question was not whether
hybrid can discover every missing nuance by magic. The question was whether
card-first plus selective raw inspection can repair the exact losses that
pressure-only produced.

## Next Slice

If implementation continues, build the smallest research-only hybrid renderer:

```text
card block: pressure, boundary, relax_if, discard_if, risk_if_ignored
inspect-more block: only raw fields for contested/lossy pressure
validation: card cap, raw excerpt cap, public machinery hygiene, source refs
comparison: raw-only vs pressure-only vs hybrid
```

Do not wire this into live `/lolla`. The next proof should be an offline replay
surface, not runtime behavior.

2026-05-18 follow-up: the offline renderer now exists in:

```text
research/pre-step6-hybrid-handoff-renderer-readout-2026-05-18.md
```

It added:

```text
pre_step6_hybrid_handoff.v1
card-first rendering
optional inspect-more raw excerpts
source validation
caps
three fixtures: founder, PhD, consultant
```

The next check is rendered-handoff consumption replay, not runtime wiring.

# False-Positive Visibility Probe Readout

Date: 2026-05-21

Status: research-only, non-promotional. `SKILL.md` and runtime remain untouched.

## Probe

Probe id:

```text
false_positive_visibility_probe_v0
```

Source contract:

```text
research/pre-step6-false-positive-visibility-probe/false-positive-visibility-probe.v1.json
```

Step 6 replays:

```text
research/pre-step6-false-positive-visibility-probe/step6-replays/*.false-positive-step6-replay.v1.json
```

Aggregate result:

```text
research/pre-step6-false-positive-visibility-probe/false-positive-visibility-result.v1.json
```

## Why This Probe Exists

The false-standdown probe tested the old failure direction:

```text
deck should be visible -> anchor-biased runtime hides it
```

The visibility redesign fixes that by using Step 6's private ledger as the
cognitive signal. This creates the mirror risk:

```text
deck should stay private -> Step 6 marks additive -> runtime shows it
```

This probe tested that mirror risk before treating the ledger-mediated design
draft as an implementation contract.

## Contract Sharpenings

The probe contract pins three red-team sharpenings:

1. Split reviewer outcomes become `ambiguous_visibility`, not a pass and not a
   stop trigger.
2. Failure response is cheap-first:
   - `tighten_answer_delta_visible_effect_check`;
   - `add_entity_level_payload_gate`;
   - `split_additive_private_pressure_from_additive_public_payload`.
3. If the marker-preserved/entity-lost case cannot naturally reach the failure
   mode, the dimension is `not_observed`, not evidence that the omission gate is
   strong.

## Live Run

Step 6 model:

```text
openai/gpt-5.1-chat
```

Command:

```text
LOLLA_LLM_TIMEOUT=60 PYTHONPATH=. python3 scripts/research/pre_step6_false_positive_visibility_probe.py --live --all --provider openrouter --step6-model openai/gpt-5.1-chat --env-file /Users/marcin/Desktop/Apps/Lolla/.env.openai.local
```

Reviewer calls:

```text
0
```

No reviewer calls were needed because Step 6 did not emit
`additive_pressure_present` on any probe case.

## Result

| Case | Shape | Step 6 Ledger Signal | Confirmed Label |
| --- | --- | --- | --- |
| `fp-bevelin-irrelevant-incentives` | Bevelin structurally applicable but irrelevant | `all_private_or_confirming` | `step6_stood_down` |
| `fp-polya-true-but-useless` | Polya true but useless abstraction | `all_private_or_confirming` | `step6_stood_down` |
| `fp-marker-preserved-entity-lost` | Marker preserved, entity lost | `all_private_or_confirming` | `not_observed` |

Aggregate:

```text
probe_result: continue_probe_with_not_observed
promotion_effect: none_bridge_only
runtime_wiring_allowed: false
skill_update_allowed: false
```

## Interpretation

The probe did not find a confirmed false positive.

On the two clean overpromotion cases, Step 6 behaved exactly as the redesigned
policy needs it to behave:

- it rejected Bevelin-style incentive framing when the user needed a concrete
  client follow-up;
- it kept Polya-style problem-shape framing private when the anchor already had
  the useful Wednesday counsel protocol.

That is meaningful evidence that the private ledger is not automatically biased
toward visible deck use.

The third case is different. Step 6 did not produce the dangerous marker-only
answer. Instead it preserved the concrete anchor entities: RAINN, therapist or
counsel, meeting requests, sexual images, threats, other minors, hidden
channels, and pressure/fear language. That is good behavior from Step 6, but it
does not test whether the omission gate would catch marker-preserved,
entity-lost degradation if Step 6 had emitted it. Therefore the correct label is
`not_observed`, not pass.

## What This Proves

This lowers the immediate false-positive concern:

```text
Step 6 stood down on tempting but unhelpful deck pressure.
```

It also confirms the split of responsibilities:

- Step 6 supplied the cognitive decision;
- deterministic code derived the visibility precondition;
- reviewers stayed out of runtime;
- no runtime or `SKILL.md` behavior changed.

## What This Does Not Prove

This does not close the omission-gate weakness.

The probe did not observe a natural case where all of these were true:

```text
Step 6 marks additive_pressure_present
deck-aware answer preserves category markers
deck-aware answer loses concrete anchor entities
reviewers prefer anchor
```

That remains a known live risk for full calibration.

## Recommendation

Do not promote runtime.

The ledger-mediated design is stronger after this probe, but the result is not
a clean full pass because the hardest payload-loss dimension is `not_observed`.

Next acceptable paths:

1. Run a focused marker/entity-loss construction follow-up with up to three
   additional attempts.
2. Or proceed only with an ultra-dormant implementation slice that adds flags,
   archive fields, and validation contracts, while keeping visibility decisions
   shadow-only until the marker/entity-loss risk is observed or calibrated.

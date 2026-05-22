# Pre-Step 6 Answer-Delta Bridge Rerun Readout

Date: 2026-05-21

Slice: `answer_delta_bridge_rerun_v0`

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

The `answer_delta_specificity_v0` slice fixed a false-positive risk: Step 6
could previously mark deck pressure as additive with only abstract
`visible_effect` language.

The missing verification was the opposite side:

Did the new structured `answer_delta` requirement re-suppress the original
false-standdown bridge cases?

Those bridge cases are:

- `bridge-high-clutter-sensitive-overlay`
- `bridge-sensitive-anchor-misses-tripwire`
- `bridge-sequencing-sensitive-boundary`

## Method

The bridge Step 6 ledger replay prompt now asks Step 6 to populate structured
`answer_delta` fields:

```json
{
  "added_entities": [],
  "removed_entities": [],
  "reordered_sequences": [],
  "reframed_emphasis": []
}
```

The deterministic read remains mechanical:

- derive `ledger_signal`
- derive `answer_delta_specificity`
- derive whether the answer-delta guarded policy would unlock

No runtime wiring was enabled. No `SKILL.md` behavior changed.

## Step 6 Rerun Result

Artifact:

`research/pre-step6-answer-delta-bridge-rerun/bridge-step6-ledger-replay-result.v1.json`

| Case | Ledger Signal | Answer-Delta Specificity | Answer-Delta Guarded Policy |
| --- | --- | --- | --- |
| `bridge-high-clutter-sensitive-overlay` | `additive_pressure_present` | `concrete_delta_present` | unlocks |
| `bridge-sensitive-anchor-misses-tripwire` | `additive_pressure_present` | `concrete_delta_present` | unlocks |
| `bridge-sequencing-sensitive-boundary` | `additive_pressure_present` | `concrete_delta_present` | unlocks |

Aggregate:

```text
answer_delta_replay_result = answer_delta_bridge_support_preserved
```

This answers the mechanical question: the new answer-delta vocabulary did not
push the original bridge cases back into `all_private_or_confirming`.

## Reviewer Confirmation

Artifact:

`research/pre-step6-answer-delta-bridge-rerun-review/false-standdown-bridge-result.v1.json`

The reviewer contract used the original anchor-visible candidate as the anchor
arm and the fresh answer-delta Step 6 `answer_core` as the deck-visible arm.

Both reviewer families labeled all three cases `false_standdown`.

In this rerun, that label means:

If runtime hid the answer-delta Step 6 output behind the anchor, that hiding
would be a false stand-down.

It is therefore a positive verification signal, not a failure of the
answer-delta guardrail. The answer-delta guarded policy would not hide those
outputs, because all three cases recorded `concrete_delta_present`.

## Interpretation

The answer-delta guardrail now has evidence in both directions:

- False-positive side: founder, PhD, and consultant stood down when Step 6 had
  to name concrete deltas.
- False-standdown side: the three original bridge wins still produced additive
  pressure with concrete deltas and were confirmed by dual reviewers as material.

This is the shape we wanted.

The deterministic layer still does not judge wisdom. It only checks whether
Step 6 recorded concrete visible-answer custody before public visibility can be
upgraded.

Step 6 remains the cognitive actor.

## Recommendation

Keep the answer-delta guardrail.

Do not add the heavier entity-level payload gate yet.

The next bottleneck is calibration coverage:

- 12 to 20 pre-registered cases
- balanced case-shape distribution
- `n=3` Step 6 sampling for stability on important cases
- track how often useful cases are trapped in `reframed_emphasis` only

Runtime promotion remains blocked. `SKILL.md` remains untouched.

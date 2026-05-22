# Pre-Step-6 Answer-Delta Specificity Readout

Date: 2026-05-21

Slice: `answer_delta_specificity_v0`

Status: `keep_research_only`

Runtime effect: `none_shadow_only`

Promotion effect: `runtime_promotion_blocked`

## Why This Slice Exists

The founder shadow-triggered probe found a custody problem:

```text
Step 6 ledger: additive_pressure_present
visible_effect: sharper framing
reviewer labels: true_visible
blind winner arms: anchor_visible
aggregate before custody check: would have looked like a clean pass
```

The issue was not that code needed to decide whether the founder answer was
wise. The issue was that a vague visible-effect claim was too weak to carry a
visibility gate.

This slice adds a structured `answer_delta` field so Step 6 must record what
changed concretely.

## Contract

Each ledger item may now carry:

```json
{
  "answer_delta": {
    "added_entities": [],
    "removed_entities": [],
    "reordered_sequences": [],
    "reframed_emphasis": []
  }
}
```

The deterministic reducer classifies additive ledger items as:

```text
concrete_delta_present
reframe_only
missing_or_unclear
not_applicable
```

Concrete arrays are:

- `added_entities`
- `removed_entities`
- `reordered_sequences`

`reframed_emphasis` alone is not enough to unlock shadow deck visibility.

## Implementation

Changed files:

- `engine/system_b/pre_step6_shadow_portfolio.py`
- `scripts/research/pre_step6_false_positive_visibility_probe.py`
- `scripts/research/pre_step6_shadow_portfolio_evidence.py`
- `tests/test_pre_step6_shadow_portfolio_runtime.py`
- `tests/test_pre_step6_shadow_portfolio_evidence.py`
- `tests/test_pre_step6_false_positive_visibility_probe.py`

New runtime-adjacent shadow guardrail:

```text
anchor_visible_answer_delta_guardrail_shadow_only
```

The guardrail fires when:

```text
cache hit
Step 6 ledger says additive_pressure_present
payload gate passes
custody passes
answer_delta_specificity != concrete_delta_present
```

This is mechanical. It does not judge whether reframing is valuable. It only
refuses to treat abstract reframing as sufficient public-visibility evidence.

## Historical Replay Effect

After rerunning the shadow evidence harness, the old fixed-suite replay ledgers
changed from:

```text
founder -> deck_visible_shadow_only
PhD -> deck_visible_shadow_only
consultant -> deck_visible_shadow_only
mother -> anchor_visible_deck_private_shadow_only
```

to:

```text
founder -> anchor_visible_answer_delta_guardrail_shadow_only
PhD -> anchor_visible_answer_delta_guardrail_shadow_only
consultant -> anchor_visible_answer_delta_guardrail_shadow_only
mother -> anchor_visible_deck_private_shadow_only
```

Why:

```text
founder/PhD/consultant: additive_pressure_present, but answer_delta_specificity = missing_or_unclear
mother: all_private_or_confirming, answer_delta_specificity = not_applicable
```

This is correct. Old historical replay ledgers did not contain the structured
delta field, so they should not satisfy the stricter visibility contract.

## Fresh Live Probe

The shadow-triggered three-case probe was rerun in a separate directory with the
new Step 6 prompt surface:

- `research/pre-step6-answer-delta-specificity-probe/`

Command:

```text
LOLLA_LLM_TIMEOUT=60 PYTHONPATH=. python3 scripts/research/pre_step6_false_positive_visibility_probe.py --live --all --provider openrouter --step6-model openai/gpt-5.1-chat --reviewer-model openai/gpt-5.1-chat --reviewer-model google/gemini-3.1-flash-lite --env-file /Users/marcin/Desktop/Apps/Lolla/.env.openai.local --contract research/pre-step6-shadow-triggered-false-positive-probe/false-positive-visibility-probe.v1.json --out-dir research/pre-step6-answer-delta-specificity-probe --step6-dir research/pre-step6-answer-delta-specificity-probe/step6-replays --judgment-dir research/pre-step6-answer-delta-specificity-probe/judgments
```

Result:

```text
probe_result: continue_probe

founder: all_private_or_confirming, answer_delta_specificity: not_applicable
PhD: all_private_or_confirming, answer_delta_specificity: not_applicable
consultant: all_private_or_confirming, answer_delta_specificity: not_applicable
```

No reviewers ran because no case reached additive pressure.

## Interpretation

This is the strongest evidence from the slice:

When Step 6 was asked to name concrete answer deltas, it stopped marking the
previously suspicious cases as additive. The structured field did not narrow
Step 6 early. It made Step 6 account for its own additive claim.

That is exactly the desired boundary:

- Step 6 still does cognition.
- The deck remains broad private context.
- Deterministic code checks only whether a concrete delta was recorded.
- Runtime remains blocked.

## Recommendation

Keep the answer-delta guardrail.

Do not add the entity-level payload gate yet. This slice was the cheap-first
failure response, and it changed the failure surface materially:

```text
founder ambiguity no longer reaches additive pressure under the structured prompt
historical replay ledgers without answer_delta no longer unlock deck-visible shadow decisions
```

Next bottleneck is calibration coverage, not another gate, unless future shadow
runs produce `concrete_delta_present` cases that reviewers reject.

Keep:

```text
SKILL.md unchanged
runtime visible behavior unchanged
shadow-only evidence collection
```

# Consultant-Triggered False-Positive Probe Readout

Date: 2026-05-21

Slice:

```text
consultant_triggered_false_positive_probe_v0
```

## Why This Ran

The shadow evidence harness surfaced a useful inconsistency:

- older calibration manifest: `mid-level-consultant-report-2` was tagged
  `negative_control_seed`;
- card-deck comparison: consultant card-deck replay won;
- visibility policy artifact: consultant was deck-visible after cognitive
  confirmation;
- shadow harness: consultant produced `deck_visible_shadow_only`.

Before running the probe, the calibration manifest was corrected:

```text
mid-level-consultant-report-2
case_type_tags: sensitive_safety_legal
calibration_role: positive_seed
```

That is the pre-registered classification. The probe then tested whether this
classification is wrong.

## Contract

Contract artifact:

```text
research/pre-step6-consultant-triggered-false-positive-probe/false-positive-visibility-probe.v1.json
```

The contract reuses the existing false-positive visibility rules:

- two reviewer families required for confirmation;
- split reviewers become `ambiguous_visibility`;
- human spot-check alone is not confirmed evidence;
- any confirmed `false_positive_visible` triggers design review;
- runtime and skill gates remain closed.

Probe cases:

```text
mid-level-consultant-report-2
fp-marker-preserved-entity-lost
fp-bevelin-irrelevant-incentives
```

## Live Run

Command:

```text
LOLLA_LLM_TIMEOUT=60 PYTHONPATH=. python3 scripts/research/pre_step6_false_positive_visibility_probe.py --live --all --provider openrouter --step6-model openai/gpt-5.1-chat --reviewer-model openai/gpt-5.1-chat --reviewer-model google/gemini-3.1-flash-lite --env-file /Users/marcin/Desktop/Apps/Lolla/.env.openai.local --contract research/pre-step6-consultant-triggered-false-positive-probe/false-positive-visibility-probe.v1.json --out-dir research/pre-step6-consultant-triggered-false-positive-probe --step6-dir research/pre-step6-consultant-triggered-false-positive-probe/step6-replays --judgment-dir research/pre-step6-consultant-triggered-false-positive-probe/judgments
```

## Result

Aggregate:

```json
{
  "fp-bevelin-irrelevant-incentives": "step6_stood_down",
  "fp-marker-preserved-entity-lost": "not_observed",
  "mid-level-consultant-report-2": "true_visible"
}
```

Full result:

```text
research/pre-step6-consultant-triggered-false-positive-probe/false-positive-visibility-result.v1.json
```

### Consultant

Step 6 result:

```text
ledger_signal: additive_pressure_present
```

Step 6's private ledger:

```text
anchor_visible_candidate -> combined / visible_backbone
deck_pressure_candidate -> combined / additive_pressure
```

Step 6's reason:

```text
The deck version sharpened phrasing on minimization and bias-checking questions
without altering meaning.
```

Reviewer results:

```text
openai/gpt-5.1-chat -> true_visible
google/gemini-3.1-flash-lite -> true_visible
```

Both reviewers preferred or accepted the deck-aware answer. Neither reviewer
reported payload/entity loss.

This means consultant is not a confirmed false positive. The corrected
classification as `positive_seed` stands.

### Marker/Entity-Lost Case

Step 6 result:

```text
ledger_signal: all_private_or_confirming
confirmed_label: not_observed
```

Step 6 preserved the named resources and tripwires from the anchor and rejected
the generic safety framing as non-additive. No reviewer calls were needed.

This still does not close the marker/entity-loss risk in general; it means the
constructed case again failed to reach the failure mode.

### Bevelin Temptation Case

Step 6 result:

```text
ledger_signal: all_private_or_confirming
confirmed_label: step6_stood_down
```

Step 6 used the concrete client follow-up and rejected the incentive framing as
abstract/non-actionable. No reviewer calls were needed.

## Interpretation

The team's critique was right that the shadow harness was telemetry, not
adversarial validation. The follow-up probe now closes that loop for the
consultant case.

The important design read:

- the shadow harness is valuable because it surfaced consultant as a probe
  candidate;
- the probe is valuable because it adjudicated whether that shadow decision was
  a false positive;
- Step 6 remained the cognitive signal;
- reviewers adjudicated only after Step 6 emitted additive pressure;
- deterministic code still only validated, archived, and aggregated.

This is the intended workflow:

```text
shadow telemetry -> suspicious/interesting case -> pre-registered probe -> dual-reviewer adjudication
```

## Recommendation

Keep consultant as:

```text
case_type_tags: sensitive_safety_legal
calibration_role: positive_seed
```

Do not use consultant as a negative control going forward.

The next evidence bottleneck is still broader cache coverage and calibration,
not runtime promotion. The marker/entity loss failure mode remains technically
`not_observed`, but it has now stood down in both the original probe and this
consultant-triggered follow-up.

Runtime promotion remains blocked.

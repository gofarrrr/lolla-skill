# Pre-Step-6 Structural Delta Targeted Rerun Readout

Date: 2026-05-21
Slice: `answer_delta_structural_delta_targeted_rerun_v0`
Status: research-only prerequisite check
Promotion effect: none
Runtime: dormant
`SKILL.md`: unchanged

## Why This Rerun Happened

The structural-delta diagnostic proved that the vocabulary works mechanically:
`structural_delta` exists, vague structural framing stays blocked, and the easy
negative control stood down 3/3.

But the diagnostic also showed:

```text
structural_delta_sample_count = 0
structural_delta_field_sample_count = 7
```

So the structural field was used, but it never became the deciding specificity
bucket. Every unlock was already `concrete_delta_present`.

The verifier's concern was fair: the repair claim is only fully convincing if
the exact prior reframe-useful cases no longer remain trapped as
`reframe_only`.

This rerun checks exactly that.

## Model Pin

The calibration Step 6 model is pinned to:

```text
moonshotai/kimi-k2.6
```

Reason:

- the repaired structural-delta diagnostic used this model successfully;
- the env default OpenRouter model returned `404` during the first live attempt;
- calibration evidence must not blend model families;
- future full calibration should use this same Step 6 model unless the team
  deliberately resets the evidence track.

The calibration corpus manifest now records this model in `sample_plan.step6_model`.

## Cases Rerun

Two saved samples from the earlier reframe diagnostic were rerun under the
repaired prompt contract:

| Case | Sample | Prior role |
|---|---:|---|
| `founder-grant-marcus-equity.high-clutter.v60-on` | 0 | confirmed reframe-useful diagnostic |
| `third-year-phd-student.v2.v60-off` | 2 | confirmed reframe-useful diagnostic |

Artifacts:

- `research/pre-step6-answer-delta-structural-delta-targeted-rerun/calibration-corpus.v1.json`
- `research/pre-step6-answer-delta-structural-delta-targeted-rerun/step6-samples/*.json`
- `research/pre-step6-answer-delta-structural-delta-targeted-rerun/calibration-step6-result.v1.json`
- `research/pre-step6-answer-delta-structural-delta-targeted-rerun/calibration-stability-review.v1.json`

## Result

Aggregate:

```json
{
  "case_count": 2,
  "sample_count": 2,
  "unstable_case_count": 0,
  "stable_case_count": 2,
  "unlock_sample_count": 2,
  "reframe_only_sample_count": 0,
  "structural_delta_sample_count": 0,
  "structural_delta_field_sample_count": 2,
  "reviewer_tension_status": "not_run",
  "calibration_read": "sampling_incomplete"
}
```

Case-level:

| Case | Result | Answer Delta Read |
|---|---|---|
| `founder-grant-marcus-equity.high-clutter.v60-on` sample 0 | `additive_pressure_present` | `concrete_delta_present`, with `structural_delta` populated |
| `third-year-phd-student.v2.v60-off` sample 2 | `additive_pressure_present` | `concrete_delta_present`, with `structural_delta` populated |

## Interpretation

The exact prior reframe-useful cases did not remain trapped as reframe-only.
Under the repaired prompt, Step 6 named concrete public-answer changes and also
used `structural_delta` to account for the structural part of the change.

This supports Path A:

```text
the repaired prompt made Step 6 more specific,
and structural_delta gives it a better custody language for the structural part.
```

It does not prove that pure `structural_delta_present` will appear naturally.
That path remains live but unobserved. Full calibration should track it
explicitly.

## Boundary

No new vocabulary field was added in this rerun.
No reviewer call was added.
No runtime behavior changed.
No `SKILL.md` change was made.

This closes the small prerequisite before full calibration.

## Next Move

Run the full calibration corpus under the repaired prompt contract and pinned
Step 6 model:

```text
moonshotai/kimi-k2.6
```

Track:

- unlock frequency;
- reframe-only frequency;
- pure `structural_delta_present` frequency;
- `structural_delta` field co-occurrence;
- n=3 per-case stability;
- reviewer label/winner-arm tension in the reviewer phase.

The vocabulary is closed. Another missing category in calibration means design
review, not another quick field addition.


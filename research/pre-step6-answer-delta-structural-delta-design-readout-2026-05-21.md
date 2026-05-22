# Pre-Step-6 Answer-Delta Structural Delta Design Readout

Date: 2026-05-21
Slice: `answer_delta_structural_delta_design_v0`
Status: research-only vocabulary repair
Promotion effect: `none_calibration_only`
Runtime: dormant
`SKILL.md`: unchanged

## Why This Slice Ran

The reframe diagnostic found a real vocabulary gap. Some Step 6 outputs were
confirmed useful by both reviewer families even though the current
answer-delta contract classified them as `reframe_only`.

The interpretation was narrow:

- do not loosen runtime visibility;
- do not add another cognitive selector;
- give Step 6 one more reporting field for concrete structural changes;
- keep generic framing blocked;
- treat this as the last vocabulary repair before full calibration.

## Contract Change

`answer_delta` now has a fifth field:

```json
{
  "added_entities": [],
  "removed_entities": [],
  "reordered_sequences": [],
  "structural_delta": [],
  "reframed_emphasis": []
}
```

`structural_delta` is for specific public-answer structure changes such as:

- stop conditions;
- unlock conditions;
- decision boundaries;
- test designs;
- commitment boundaries;
- sequencing gates;
- deadline/window logic.

It is not for vague claims like:

```json
"structural_delta": ["added structural framing"]
```

That remains `reframe_only` when the only real content is framing or emphasis.

## Mechanical Gate

The deterministic layer still does not judge wisdom.

It only checks whether Step 6 recorded enough custody evidence for the visible
action it is asking the system to take.

Unlocking answer-delta specificity is now:

```text
concrete_delta_present
structural_delta_present
```

But `structural_delta_present` requires a specific entry. The mechanical check
requires a non-empty structural-delta string with a structural marker such as
`condition`, `boundary`, `test`, `stop`, `unlock`, `window`, `gate`, `sequence`,
or similar. Vague structural framing labels do not pass.

## Files Updated

- `engine/system_b/pre_step6_shadow_portfolio.py`
- `scripts/research/pre_step6_bridge_step6_ledger_replay.py`
- `scripts/research/pre_step6_false_positive_visibility_probe.py`
- `scripts/research/pre_step6_calibration_corpus.py`
- `tests/test_pre_step6_shadow_portfolio_runtime.py`
- `tests/test_pre_step6_bridge_step6_ledger_replay.py`
- `tests/test_pre_step6_false_positive_visibility_probe.py`
- `tests/test_pre_step6_calibration_corpus.py`

## Live Diagnostic

The slice then ran a small live diagnostic using the updated prompt contract.

Model/provider:

```text
provider: openrouter
model: moonshotai/kimi-k2.6
env: /Users/marcin/Desktop/Apps/Lolla/.env.openai.local
```

The calibration Step 6 model is pinned to `moonshotai/kimi-k2.6` for the
repaired prompt track. The first live attempt used the env default OpenRouter
model and returned `404`, so the diagnostic and follow-up evidence use the
working Kimi model consistently. Future full calibration should not blend model
families inside one evidence read.

Artifacts:

- `research/pre-step6-answer-delta-structural-delta-design/calibration-corpus.v1.json`
- `research/pre-step6-answer-delta-structural-delta-design/step6-samples/*.json`
- `research/pre-step6-answer-delta-structural-delta-design/calibration-step6-result.v1.json`
- `research/pre-step6-answer-delta-structural-delta-design/calibration-stability-review.v1.json`

Two serial runs were stopped after useful evidence landed because later cases
were slow/stalled. This diagnostic is therefore not a full calibration run. It
is an instrumentation check before full calibration.

## Live Result

Aggregate:

```json
{
  "case_count": 4,
  "sample_count": 10,
  "unstable_case_count": 0,
  "stable_case_count": 4,
  "unlock_sample_count": 7,
  "reframe_only_sample_count": 0,
  "structural_delta_sample_count": 0,
  "structural_delta_field_sample_count": 7,
  "reviewer_tension_status": "not_run",
  "calibration_read": "sampling_incomplete"
}
```

Case-level result:

| Case | Samples | Ledger Signal | Specificity | Structural Field Use | Read |
|---|---:|---|---|---:|---|
| `founder-grant-marcus-equity.high-clutter.v60-on` | 3 | 3/3 additive | 3/3 concrete | 3/3 | Stable positive candidate |
| `third-year-phd-student.v2.v60-off` | 3 | 3/3 additive | 3/3 concrete | 3/3 | Stable positive candidate |
| `startup-pivot-new-run2` | 1 | 1/1 additive | 1/1 concrete | 1/1 | Useful partial signal, not stability evidence |
| `fp-bevelin-irrelevant-incentives` | 3 | 3/3 private/confirming | 3/3 not applicable | 0/3 | Stable stand-down |

## What We Learned

The repair did not create an obvious loophole. The easy false-positive negative
control stood down in all three samples.

Step 6 did use the new vocabulary naturally. In every positive sample where the
deck unlocked, the ledger included `structural_delta` entries such as unlock
conditions, stop dates, fallback gates, decision-rights boundaries, and
technical-resource checks.

However, the live samples did not produce a pure `structural_delta_present`
case. They mostly became `concrete_delta_present` because Step 6 also named
added entities or payload. That is not a failure. It means the new prompt often
made Step 6 more concrete rather than merely giving it a new bucket.

The correct interpretation:

```text
structural_delta support is implemented
specificity bar works in tests
vague structural framing remains blocked
live Step 6 uses the field
pure structural-only unlock remains not_observed
negative-control stand-down survived
```

## Targeted Rerun Addendum

After this diagnostic, two prior reframe-useful samples were rerun under the
same repaired prompt:

- `founder-grant-marcus-equity.high-clutter.v60-on` sample 0;
- `third-year-phd-student.v2.v60-off` sample 2.

Both reruns produced:

```text
ledger_signal = additive_pressure_present
answer_delta_specificity = concrete_delta_present
structural_delta field populated = true
```

Neither stayed trapped as `reframe_only`.

This supports the narrower repair claim: the prompt change helped Step 6 name
concrete public-answer changes for the exact cases that previously looked like
useful reframe-only outputs. Pure `structural_delta_present` remains unobserved
in live samples and should be measured during full calibration.

## Boundary Held

This is still aligned with the governing doctrine:

- broad private material remains available to Step 6;
- Step 6 decides usefulness;
- deterministic code only checks custody and specificity;
- no reviewer calls are introduced into runtime;
- no live card generation is introduced;
- no `SKILL.md` changes were made;
- runtime remains dormant.

## Next Move

Run the full calibration corpus again under the repaired prompt contract.

The next calibration run should track:

- unlock frequency;
- reframe-only frequency;
- structural-delta-only frequency;
- structural-delta field usage frequency;
- per-case Step 6 stability with n=3 samples;
- reviewer label/winner-arm tension during the reviewer phase.

This slice should be treated as the last pre-calibration vocabulary repair. If
full calibration exposes another missing answer-delta category, that is a
design-review signal, not permission to keep adding one more field.

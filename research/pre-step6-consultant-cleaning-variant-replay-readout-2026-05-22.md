# Consultant Cleaning Variant Replay Readout - 2026-05-22

## Scope

This slice replayed `consultant_cleaning_variant_v0` through Step 6 to test a
cleaning hypothesis, not a visibility hypothesis:

```text
Does replacing broad Bevelin/Polya lens identity with concrete Consultant
micro-cards make Step 6's consideration cleaner, more stable, and easier to
audit while preserving the anchor payload?
```

Runtime remains dormant. `SKILL.md` remains blocked. No visibility gate,
model-router, or deterministic selector was added.

## Artifacts

- `research/pre-step6-consultant-cleaning-variant-replay/consultant-cleaning-variant-replay-contract.v1.json`
- `research/pre-step6-consultant-cleaning-variant-replay/step6-samples/*.consultant-cleaning-replay.v1.json`
- `research/pre-step6-consultant-cleaning-variant-replay/consultant-cleaning-variant-replay-result.v1.json`
- `scripts/research/pre_step6_consultant_cleaning_variant_replay.py`
- `tests/test_pre_step6_consultant_cleaning_variant_replay.py`

Live replay used `moonshotai/kimi-k2.6`.

Completed live samples:

```text
0, 1, 2, 3, 5, 6
```

Sample `4` stalled twice at the provider/model call layer and was replaced by
sample `6`. This is recorded as an operational latency/stall observation, not
as evidence for or against the cleaning variant.

## Aggregate

```text
sample_count = 6
micro_card_additive_count = 4
all_private_or_confirming_count = 2
missing_or_unclear_count = 0
unlock_ratio = 0.667
old_kimi_unlock_ratio = 0.5
consideration_stability_read = mixed
cleaning_improvement_read = changed_but_still_mixed
protected_payload_all_present_count = 6
runtime_promotion = blocked
skill_update = blocked
```

## What Improved

The replay made Step 6's consideration more legible.

All six samples preserved the protected Consultant payload:

```text
counsel/attorney
no confrontation
no private investigation
channel selection caution
Wednesday protocol
do-not-deny tripwire
reversibility
```

The broad lens identities did not leak into the prompt or visible output. The
micro-cards stayed concrete.

Most importantly, Step 6 did not treat the three cards as a generic bundle. It
made a specific distinction:

```text
counsel_independence_and_channel_bias_card -> private guardrail / confirming
wednesday_tripwire_preservation_card -> private guardrail / confirming
reversibility_until_counsel_boundary_card -> additive in 4/6 samples
```

That is the cleaning win. The table became easier to think with. Instead of
"Bevelin/Polya might help Consultant," the live record now says:

```text
The only recurring public-useful pressure is the small boundary:
keep early moves reversible until counsel guides the next action.
```

## What Did Not Improve Enough

The case is still mixed.

Four samples treated the reversibility boundary as a concrete public delta.
Two samples treated all micro-cards as private or confirming. That means the
cleaning variant improved the shape of the ambiguity, but did not eliminate it.

This should not be fixed with a new deterministic gate. The variance is now
narrow and understandable. It is not a resolver failure. It is Step 6 honestly
deciding whether the anchor already carries enough force on one tiny boundary.

## Interpretation

The Consultant issue was not mainly V60 and not mainly visibility policy.
V60 is not active for this case. The useful deck pressure is thin but real.

The cleaning variant did what we wanted in one important sense:

```text
It preserved broad private consideration while stopping broad lens identity from
doing hidden work.
```

It did not castrate Step 6. All three cards were available. Step 6 could use,
combine, or keep each one private. The live samples show it used that freedom
selectively.

The remaining question is not "which gate should choose visibility?" It is:

```text
Should the counsel-gated reversibility boundary be part of the Consultant anchor
itself, so the micro-card can stand down more consistently?
```

That is a cleaning question. If the answer is yes, the system learns by making
the base table better, not by adding an output selector.

## Recommendation

Do not promote runtime. Do not change `SKILL.md`. Do not add a sixth gate.

The next useful Consultant move is a small anchor-cleaning probe:

```text
consultant_anchor_boundary_patch_probe_v0
```

Build a patched Consultant anchor candidate that folds in the one recurring
useful delta:

```text
keep the first moves reversible until counsel guides the next action
```

Then replay the same three micro-cards. The success condition is not deck
visibility. The success condition is cleaner stand-down:

```text
protected payload preserved
micro-cards mostly private/confirming
Step 6 no longer has to rediscover the same small boundary in 4/6 samples
```

If that passes, the learning belongs in anchor/context construction for this
case shape, not in a visibility policy. If it fails, Consultant should remain
classified as a genuinely borderline case with useful but thin deck pressure.


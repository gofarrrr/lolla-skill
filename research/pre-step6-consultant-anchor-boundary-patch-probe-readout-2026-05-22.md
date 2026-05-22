# Consultant Anchor Boundary Patch Probe Readout - 2026-05-22

## Scope

This slice tested one graduation hypothesis:

```text
If the Consultant anchor already carries the recurring
reversibility-until-counsel pressure, does the same micro-card stand down?
```

The patch was a hypothesis-test input, not a proposed architecture. It made one
minimal change:

```text
keep the first moves reversible
```

became:

```text
keep the first moves reversible until counsel guides the next action
```

The same three micro-cards remained available. `SKILL.md`, runtime promotion,
visibility policy, model routing, and deterministic gates remain unchanged.

## Artifacts

- `research/pre-step6-consultant-anchor-boundary-patch-probe/consultant-anchor-boundary-patch-probe-contract.v1.json`
- `research/pre-step6-consultant-anchor-boundary-patch-probe/step6-samples/*.anchor-boundary-patch-probe.v1.json`
- `research/pre-step6-consultant-anchor-boundary-patch-probe/consultant-anchor-boundary-patch-probe-result.v1.json`
- `scripts/research/pre_step6_consultant_anchor_boundary_patch_probe.py`
- `tests/test_pre_step6_consultant_anchor_boundary_patch_probe.py`

Live replay used `moonshotai/kimi-k2.6`.

## Aggregate

```text
sample_count = 6
micro_card_standdown_count = 5
micro_card_standdown_rate = 0.833
micro_card_additive_count = 1
missing_or_unclear_count = 0
reversibility_card_additive_count = 1
reversibility_card_additive_rate = 0.167
patched_boundary_present_count = 6
protected_payload_all_present_count = 6
protected_payload_preserved = true
upstream_pressure_carried = yes
next_investigation = synthesis
consultant_classification = graduation_candidate
runtime_promotion = blocked
skill_update = blocked
```

## Interpretation

The patched anchor carried the recurring pressure.

Compared with the prior cleaning replay:

```text
before patch: reversibility card additive in 4/6 samples
after patch:  reversibility card additive in 1/6 samples
```

All six outputs preserved the protected Consultant payload. All six visible
answers retained the patched boundary. Five of six samples kept all micro-cards
private or confirming.

The single additive outlier is informative but not disqualifying. In sample `5`,
Step 6 marked the reversibility card as additive because it credited the card
with appending `until counsel guides the next action`. But the patched anchor
already contained that phrase, and the public answer did not add beyond it.
That looks like a small meta-ledger attribution lag rather than evidence that
the card still carries independent public payload.

## Finding

Consultant is now a graduation candidate for one pressure atom:

```text
keep the first moves reversible until counsel guides the next action
```

This does not mean a per-case patch should ship. It means the useful pressure
should be investigated upstream:

```text
Why did the original anchor stop at general reversibility instead of carrying
the counsel-gated stop boundary naturally?
```

The pre-committed next investigation is `synthesis`, because the substrate and
micro-card already know the pressure. The likely question is whether anchor
synthesis compressed "reversible" too early and dropped the terminal condition.

## Stop Rule

Consultant should stop here for this research chapter.

Classification:

```text
graduation_candidate
```

Recommended follow-up:

```text
consultant_upstream_origin_investigation_v0
```

That follow-up should be scoped as an upstream-origin finding, not a runtime
change. It should ask whether the missing boundary comes from substrate,
lane activation, synthesis compression, or anchor wording. It should not add a
patch layer.

## Queue Decision

Per the stop boundary, the next cleaning-lane case is:

```text
phd_kimi_variance_cleaning_review_v0
```

Purpose:

```text
Test whether atomic decomposition also explains Kimi's PhD variance, or whether
the Consultant result is case-specific.
```


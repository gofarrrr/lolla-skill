# Pre-Step-6 PhD Kimi Variance Cleaning Review Readout

Date: 2026-05-22

Status: research-only. Runtime remains dormant. `SKILL.md` remains unchanged.

## Purpose

This slice tested whether the PhD variance seen under `moonshotai/kimi-k2.6`
becomes more legible when the broad Bevelin/Polya-style pressure is decomposed
into atomic PhD pressure cards.

The question was not:

```text
Should runtime show the deck-aware answer?
```

The question was:

```text
Does a cleaner table let Step 6 discriminate among the actual pressure atoms?
```

To avoid conflating this with Founder-style V60 instability, the slice used the
PhD V60-off case:

```text
third-year-phd-student.v2.v60-off
```

## Material Given To Step 6

The visible backbone was the rendered hybrid PhD anchor. The private table
contained four concrete micro-cards:

```text
bounded_probe_not_commitment_card
single_cell_collaborator_feasibility_card
fallback_reentry_readiness_card
visible_stop_date_conditions_card
```

No broad Bevelin or Polya lens labels were exposed in the prompt.

The live calls used:

```text
provider = openrouter
model = moonshotai/kimi-k2.6
reasoning_disabled = true
sample_count = 6
```

The reasoning-disable flag was opt-in for this research script only. It was
added after the first PhD sample attempt hung at the provider/model layer. This
changes the call configuration for this slice and should be remembered as part
of the evidence conditions.

## Aggregate Result

Source:

```text
research/pre-step6-phd-kimi-variance-cleaning-review/phd-kimi-variance-cleaning-review-result.v1.json
```

Aggregate:

```text
sample_count = 6
micro_card_additive_count = 6
all_private_or_confirming_count = 0
missing_or_unclear_count = 0
protected_payload_all_present_count = 6
atomic_discrimination_read = discriminated
runtime_promotion = blocked
skill_update = blocked
```

Card additive counts:

```text
bounded_probe_not_commitment_card = 4
single_cell_collaborator_feasibility_card = 2
fallback_reentry_readiness_card = 1
visible_stop_date_conditions_card = 3
```

## Interpretation

Atomic decomposition generalized beyond Consultant, but not in the same shape.

Consultant produced one dominant reusable atom:

```text
keep the first moves reversible until counsel guides the next action
```

PhD produced a distributed pattern. Step 6 used different combinations of
cards across samples:

```text
sample 0: bounded_probe_not_commitment_card
sample 1: bounded_probe_not_commitment_card + visible_stop_date_conditions_card
sample 2: bounded_probe_not_commitment_card + fallback_reentry_readiness_card
sample 3: single_cell_collaborator_feasibility_card + visible_stop_date_conditions_card
sample 4: bounded_probe_not_commitment_card
sample 5: single_cell_collaborator_feasibility_card + visible_stop_date_conditions_card
```

This is not bundle behavior. The cards were not all pulled into the public
answer as a new smaller monolith. Step 6 selected subsets, and the selected
subsets changed by run. That means atomic decomposition is useful as a cleaning
instrument, but PhD does not yet produce a single obvious graduation candidate.

## What We Learned

The cleaning-lane hypothesis now has two case shapes:

```text
Consultant: atomic decomposition localized one recurring useful atom.
PhD: atomic decomposition made multiple useful atoms legible in different combinations.
```

This is a good result for the product thesis:

```text
the system learns by making the thinking table better
```

It is not a runtime-promotion result. The PhD table still produces additive
pressure in every sample. There is no reason to force stand-down, no reason to
add a deterministic selector, and no reason to switch models because GPT looked
more stable on earlier PhD probes.

The right conclusion is narrower:

```text
atomic pressure cards are now a serious card-design option, not a universal rule.
```

Bundles still may be useful when their pressure atoms reinforce each other.
Atoms are useful when Step 6 needs to discriminate among small structural moves.

## Operational Watch

The first Kimi call for this slice hung before the script-level reasoning-disable
configuration was added. After the opt-in flag, all six samples returned cleanly.

This means future calibration language should treat model commitment as:

```text
model family + provider + prompt contract + call configuration
```

not merely:

```text
model family
```

## Decision

PhD cleaning review is complete for this research chapter.

Next step under the stop boundary:

```text
evidence_surface_v0
```

The evidence surface should aggregate the Consultant and PhD cleaning results so
humans can read recurring pressure atoms without opening raw JSON. It must
surface candidates only. It must not automatically graduate cards upstream.


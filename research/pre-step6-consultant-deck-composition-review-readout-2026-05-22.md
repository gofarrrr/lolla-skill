# Pre-Step-6 Consultant Deck Composition Review Readout

Date: 2026-05-22

Runtime policy: `runtime_dormant`

Promotion effect: `none_research_only`

## Question

This slice deliberately reframed the Consultant follow-up as a cleaning
question, not an accounting question:

```text
Does the Consultant deck give Step 6 the right material to reach a clean answer,
or are anchor/cards/V60 packaging the case poorly?
```

The goal is to improve the table Step 6 thinks on. No visibility gate was added
or changed.

## Artifacts

- `scripts/research/pre_step6_consultant_deck_composition_review.py`
- `tests/test_pre_step6_consultant_deck_composition_review.py`
- `research/pre-step6-consultant-deck-composition-review/consultant-deck-composition-contract.v1.json`
- `research/pre-step6-consultant-deck-composition-review/consultant-deck-composition-result.v1.json`
- `research/pre-step6-consultant-deck-composition-review/consultant-cleaning-variant.v1.json`

## Result

The Consultant anchor is strong. It already carries:

```text
counsel-first sequencing
no confrontation / no private investigation / no unusual system access
notes preserved and spouse told only in broad strokes
attorney intake questions testing channel bias
Wednesday normal-behavior protocol
partner-encounter tripwires, including "do not deny"
early-step reversibility
```

The deck pressure is useful but thin. Kimi split 3/6 between additive and
confirming reads. GPT stood down 3/3, but reviewer adjudication did not support
GPT's stand-down cleanly:

```text
Kimi unlock ratio = 0.5
GPT unlock ratio = 0.0
GPT anchor stand-down reviewer-supported = false
GPT consultant labels = ambiguous, ambiguous, gpt_anchor_rejected
```

The useful deck deltas are small and concrete:

```text
independent counsel
built-in bias / channel-bias test
minimal/narrow partner response
until counsel guides you as the reversibility boundary
```

The old Bevelin/Polya identities are too broad for this case shape. The value
is not "apply Bevelin" or "apply Polya." The value is three pressure atoms that
help Step 6 avoid over-compression while keeping the answer practical.

## Diagnosis

```text
cleaning_read = anchor_strong_deck_pressure_thin_but_useful
recommended_next_action = build_consultant_cleaning_variant_v0
v60_status = not_active
```

Hypothesis evidence:

| Hypothesis | Evidence state | Read |
| --- | --- | --- |
| `anchor_sufficient_but_deck_compression_helpful` | `strong` | Anchor carries the safety payload; deck-aware answer previously won for concision without payload loss. |
| `deck_pressure_too_thin_or_generic` | `plausible` | Step 6 flips because the visible delta is small and partly stylistic. |
| `lens_composition_misaligned` | `plausible` | Bevelin/Polya receipts mostly overlap the anchor; the useful material is narrower than the lens identity. |
| `case_intrinsically_ambiguous_after_cleaning` | `plausible` | Reviewer ambiguity/tension suggests no huge visible winner. |
| `v60_not_active_for_consultant` | `strong` | Consultant samples have no V60 context, so the Founder V60 explanation should not be imported. |

## Cleaning Variant

The slice produced a research-only Consultant cleaning variant. It keeps the
anchor as backbone and replaces generic lens labels with three micro-cards:

```text
counsel_independence_and_channel_bias_card
wednesday_tripwire_preservation_card
reversibility_until_counsel_boundary_card
```

This is the important shift. The variant does not ask Step 6 to "use Bevelin"
or "use Polya." It gives Step 6 concrete pressure atoms:

```text
Check for built-in channel bias.
Do not compress away Wednesday tripwires, especially "do not deny."
Keep early steps reversible until counsel guides the next move.
```

That is a cleaner table. It is still broad enough for Step 6 to reject, combine,
or keep any card private.

## Interpretation

Consultant variance looks less like a resolver problem and more like a deck
composition problem. The anchor is strong, the generic lens receipts are mostly
confirming, and the useful additions are small. When useful material is this
thin, Step 6 can reasonably oscillate between "visible additive pressure" and
"private confirming support."

The repair path is therefore cleaning, not gating: make the few useful pressure
atoms explicit so Step 6 does not have to infer them from broad lens identities.

## Decision

```text
runtime_promotion_blocked
skill_update_blocked
no_new_visibility_gate
no_model_family_route
consultant_cleaning_variant_built
variant_replay_needed_before_any_claim_of_improvement
```

Next safe research move:

```text
consultant_cleaning_variant_replay_v0
```

Replay the new Consultant cleaning variant through Step 6 and compare the
stability/ledger behavior against the old deck. The success criterion should be
cleaner Step 6 consideration, not automatic deck visibility.

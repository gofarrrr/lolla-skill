# Pre-Step-6 Shadow Evidence Run Readout

Date: 2026-05-21

Slice:

```text
shadow_evidence_run_v0
```

## What Ran

Added a repeatable no-model-call evidence harness:

```text
scripts/research/pre_step6_shadow_portfolio_evidence.py
```

The harness runs two arms:

1. `result-cache-miss`: read prior result JSON artifacts, run the dormant shadow
   portfolio with an empty cache, and verify stand-down behavior.
2. `fixed-suite-cache-hit`: materialize existing fixed-suite card decks into a
   local cache, normalize existing Step 6 replay ledgers, and run the shadow
   portfolio as if the cached decks were available.

Command:

```text
PYTHONPATH=. python3 scripts/research/pre_step6_shadow_portfolio_evidence.py --root . --mode all --output-dir research/pre-step6-shadow-portfolio-evidence --result-limit 8
```

## Artifacts

Aggregate:

```text
research/pre-step6-shadow-portfolio-evidence/combined.shadow-evidence-result.v1.json
```

Per-arm aggregates:

```text
research/pre-step6-shadow-portfolio-evidence/result-cache-miss.shadow-evidence-result.v1.json
research/pre-step6-shadow-portfolio-evidence/fixed-suite-cache-hit.shadow-evidence-result.v1.json
```

Per-case shadow records:

```text
research/pre-step6-shadow-portfolio-evidence/result-cache-miss/*.pre-step6-shadow-portfolio.v1.json
research/pre-step6-shadow-portfolio-evidence/fixed-suite-cache-hit/*.pre-step6-shadow-portfolio.v1.json
```

Materialized fixed-suite card cache:

```text
research/pre-step6-shadow-portfolio-evidence/fixed-suite-card-cache/*.pre-step6-shadow-card-deck.v1.json
```

## Result: Prior-Result Cache Miss Arm

Input: eight existing prior result artifacts from
`research/test-cases/phase2d-lane2-equivalence-2026-04-24/_scratch`.

Cases:

```text
friendship-money-new-run2
messy-three-problems-new-run2
multi-offer-new-run2
oncologist-new-run2
parenting-teen-new-run2
phd-research-new-run2
real-estate-new-run2
startup-pivot-new-run2
```

Aggregate:

```json
{
  "total_cases": 8,
  "cache_states": {
    "cache_miss": 8
  },
  "ledger_signals": {
    "missing_or_unclear": 8
  },
  "decisions": {
    "current_step6_visible_no_deck": 8
  },
  "visible_output_applications": 0
}
```

Observation:

The dormant cache-miss path is safe and boring in the right way. It records the
absence of a cached deck, does not generate cards live, does not call reviewers,
does not infer cognition from missing ledgers, and does not touch visible output.

This tells us the cold path is operationally acceptable as instrumentation. It
also tells us cache coverage is now the bottleneck for learning anything richer
from ordinary prior results.

## Result: Fixed-Suite Cache-Hit Arm

Input: four fixed-suite card decks plus their existing live Step 6 replay ledgers.

Cases:

```text
founder-grant-marcus-equity.high-clutter
third-year-phd-student.v2
mid-level-consultant-report-2
mother-address-year
```

Aggregate:

```json
{
  "total_cases": 4,
  "cache_states": {
    "cache_hit": 4
  },
  "ledger_signals": {
    "additive_pressure_present": 3,
    "all_private_or_confirming": 1
  },
  "decisions": {
    "anchor_visible_deck_private_shadow_only": 1,
    "deck_visible_shadow_only": 3
  },
  "visible_output_applications": 0
}
```

Per-case:

```text
founder-grant-marcus-equity.high-clutter -> additive_pressure_present -> deck_visible_shadow_only
third-year-phd-student.v2 -> additive_pressure_present -> deck_visible_shadow_only
mid-level-consultant-report-2 -> additive_pressure_present -> deck_visible_shadow_only
mother-address-year -> all_private_or_confirming -> anchor_visible_deck_private_shadow_only
```

Observation:

The shadow implementation reproduces the key research pattern without changing
runtime behavior:

- founder, PhD, and consultant carry additive Step 6 ledger pressure;
- mother stands down because Step 6 kept non-anchor pressure private/confirming;
- all four remain shadow-only;
- no public answer is changed.

The consultant result should be read carefully. It does not mean the system has
approved portfolio visibility in production. It means the replay ledger says
there was additive pressure under that specific card-deck replay. Shadow mode is
useful precisely because it can surface these cases for operator review without
making them user-visible.

## Deeper Understanding

The architecture now has three distinct layers:

```text
1. Broad private material: cached decks, V60, anchors, pressure cards.
2. Cognitive interpretation: Step 6 ledger says used / combined / private / rejected.
3. Deterministic custody: cache, payload, custody, archive, Observatory.
```

This is the shape we wanted. The deterministic layer is not deciding whether
Bevelin, Polya, or clean hybrid is wise. It is preserving the evidence trail and
blocking unsafe transitions.

The cache-miss arm proves the system can stand down cleanly. The cache-hit arm
proves the shadow resolver can preserve Step 6's cognitive distinction:
additive pressure is not collapsed into generic "deck present", and
private/confirming pressure is not promoted.

That is getting smarter without getting more controlling.

## Recommendation

Next move should be a cache-coverage learning slice, not runtime promotion.

Specifically:

1. Generate or register cached decks for more prior-result cases.
2. Run the shadow harness again on those cases.
3. Compare which cases produce:
   - `deck_visible_shadow_only`;
   - `anchor_visible_deck_private_shadow_only`;
   - `anchor_visible_unclear_ledger_guardrail_shadow_only`;
   - payload/custody guardrails.
4. Inspect the Observatory panel on representative artifacts.

Do not promote visible output. Do not change `SKILL.md` visible behavior. The
next useful question is not "can we turn this on?" It is "when we give Step 6
wide private material, does its ledger stay discriminating across a broader case
set?"

## 2026-05-21 Telemetry Extension

The harness now also records per-category payload-preservation outcomes from
the omission gate, including:

```text
preserved_by_marker_anchor_entities_missing
```

This produced a useful candidate-discovery signal:

```text
deck_visible_with_marker_entity_loss: 3
```

The three fixed-suite candidates were:

- `founder-grant-marcus-equity.high-clutter`
- `third-year-phd-student.v2`
- `mid-level-consultant-report-2`

This does not mean the deck was wrong. It means the mechanistic detector saw
present category markers with non-identical anchor evidence inside those
categories. That is a smoke alarm, not an adjudicator.

The follow-up `shadow_triggered_false_positive_probe_v0` converted those smoke
alarms into a formal probe. Fresh Step 6 stood down on PhD and consultant.
Founder reached additive pressure but became `ambiguous_visibility` because
reviewer labels and blind winner arms were tense. This strengthens the operating
model: shadow telemetry discovers candidates; Step 6 and research reviewers
adjudicate; deterministic code only preserves custody and consistency.

## 2026-05-21 Answer-Delta Rerun

After `answer_delta_specificity_v0`, the harness was rerun with the same
historical fixed-suite replay ledgers.

The result changed:

```text
founder -> anchor_visible_answer_delta_guardrail_shadow_only
PhD -> anchor_visible_answer_delta_guardrail_shadow_only
consultant -> anchor_visible_answer_delta_guardrail_shadow_only
mother -> anchor_visible_deck_private_shadow_only
```

The three former deck-visible shadow cases still have
`additive_pressure_present`, but now have:

```text
answer_delta_specificity: missing_or_unclear
```

This is expected. The old replay ledgers predate structured `answer_delta`.
Under the stricter contract, they are no longer enough to unlock deck-visible
shadow decisions.

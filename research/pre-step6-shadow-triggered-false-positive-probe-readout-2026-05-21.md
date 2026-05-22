# Pre-Step-6 Shadow-Triggered False-Positive Probe Readout

Date: 2026-05-21

Status: `keep_research_only`

Promotion effect: `none_bridge_only`

Runtime effect: `none_shadow_only`

## Why This Slice Exists

The shadow harness found a useful but dangerous pattern:

```text
decision = deck_visible_shadow_only
payload outcome includes preserved_by_marker_anchor_entities_missing
```

That pattern is not a verdict. It is a candidate-discovery signal. The question
for this slice was whether a naturally surfaced marker/entity-loss candidate
would become a false positive once Step 6 and two reviewer families adjudicated
it.

## What Changed

The shadow evidence harness now records protected-payload preservation outcomes
from the omission gate:

- `preserved_marker_and_anchor_entities`
- `preserved_by_marker_anchor_entities_missing`
- `introduced_category_omission`
- `deck_added_payload`
- `case_n_a`

It also records:

```text
candidate_flags.deck_visible_with_marker_entity_loss
```

This remains telemetry only. It does not decide visibility.

The fixed-suite cache-hit run surfaced three candidates:

- `founder-grant-marcus-equity.high-clutter`
- `third-year-phd-student.v2`
- `mid-level-consultant-report-2`

## Probe

New contract builder:

- `scripts/research/pre_step6_shadow_triggered_false_positive_probe.py`

New contract artifact:

- `research/pre-step6-shadow-triggered-false-positive-probe/false-positive-visibility-probe.v1.json`

The contract turns the three shadow candidates into a normal
`false_positive_visibility_probe_v0` packet. Selection happened before reviewer
calls, and the shadow flag is used only as candidate discovery.

Live command used:

```text
LOLLA_LLM_TIMEOUT=60 PYTHONPATH=. python3 scripts/research/pre_step6_false_positive_visibility_probe.py --live --all --provider openrouter --step6-model openai/gpt-5.1-chat --reviewer-model openai/gpt-5.1-chat --reviewer-model google/gemini-3.1-flash-lite --env-file /Users/marcin/Desktop/Apps/Lolla/.env.openai.local --contract research/pre-step6-shadow-triggered-false-positive-probe/false-positive-visibility-probe.v1.json --out-dir research/pre-step6-shadow-triggered-false-positive-probe --step6-dir research/pre-step6-shadow-triggered-false-positive-probe/step6-replays --judgment-dir research/pre-step6-shadow-triggered-false-positive-probe/judgments
```

## Result

Aggregate result:

```text
probe_result: continue_probe_with_ambiguity
```

Case results:

| Case | Fresh Step 6 Signal | Reviewer Result | Read |
| --- | --- | --- | --- |
| `founder-grant-marcus-equity.high-clutter` | `additive_pressure_present` | two `true_visible` labels, but both reviewer winner arms point to `anchor_visible` | `ambiguous_visibility` after custody consistency check |
| `third-year-phd-student.v2` | `all_private_or_confirming` | reviewers not run | clean Step 6 stand-down |
| `mid-level-consultant-report-2` | `all_private_or_confirming` | reviewers not run | fresh-contract stand-down; earlier consultant-triggered probe remains the stronger consultant adjudication |

The stop condition did not trigger. There is no confirmed false positive.

## Important New Learning

The biggest learning is not "the deck passed" or "the deck failed." The learning
is that the evaluator needed a custody check of its own.

The founder case produced two `true_visible` labels, but both reviewers selected
the anchor as the better blind candidate. One reviewer called the deck
non-inferior, which can be compatible with `true_visible`. The other reviewer
described the deck as too reductive while still labeling it `true_visible`.

That is an internal reviewer-label tension. It is not a deterministic wisdom
judgment. It is a custody mismatch:

```text
label says: deck visible is acceptable
winner arm says: anchor is better
one rationale says: deck misses critical context
```

So the result builder now records:

- `reviewer_winner_arms`
- `reviewer_non_inferiority_reads`
- `reviewer_label_consistency`

If the labels say `true_visible` but the reviewer comparison contains this kind
of tension, the aggregate case is demoted to `ambiguous_visibility`.

## Interpretation

This supports the philosophy rather than weakening it:

- Step 6 remains the cognitive actor.
- The shadow harness only discovers candidates.
- Reviewers provide cognitive adjudication in research mode.
- Deterministic code only checks custody: cache state, payload gate, ledger
  shape, blind-map winner arms, and reviewer-label consistency.

The marker/entity detector is intentionally sensitive. In the fixed suite it
flagged all three deck-visible cases because it checks exact anchor evidence
inside broad protected categories. That makes it useful as a candidate finder,
not as a runtime blocker.

Historical replay is also not enough. PhD and consultant looked
deck-visible under normalized historical replay, but fresh Step 6 stood down
under this probe contract. That means cache-hit shadow evidence is conditional:
it says what the resolver would do if a ledger signal appears; it does not prove
fresh Step 6 will emit that signal.

## Recommendation

Do not promote runtime behavior.

Do not update `SKILL.md`.

Keep using the shadow harness as candidate discovery, but treat
`deck_visible_with_marker_entity_loss` as an adversarial queue, not as evidence
of failure. The next design improvement should be cheap and custody-oriented:

1. Require Step 6's additive ledger entry to include a specific visible-effect
   delta, not a generic "sharper framing" claim.
2. Keep the entity-level payload gate as the next fallback if visible-effect
   specificity does not reduce ambiguous founder-like cases.
3. Only after that consider changing ledger semantics.

Promotion remains blocked until the calibration floor exists or the board
approves a narrower dormant-only pilot with this ambiguity explicitly tracked.

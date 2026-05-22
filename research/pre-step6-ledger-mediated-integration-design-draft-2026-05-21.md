# Pre-Step-6 Ledger-Mediated Integration Design Draft

Date: 2026-05-21

Status: research-only design-review response. Proposed dormant architecture,
not an approved integration contract. `SKILL.md` and runtime remain untouched.

## Decision Summary

The next integration shape should be:

```text
broad private deck -> Step 6 answer + private ledger -> deterministic guards -> visible answer decision
```

The cognitive decision belongs to Step 6. Deterministic code does not decide
which reasoning is wise. It only checks whether Step 6 left a valid private
ledger, whether protected anchor payload survived, whether the deck was cached,
and whether audit custody is preserved.

The key runtime rule:

```text
Deck-aware Step 6 output may be visible only when:

1. compiled card deck cache is hit;
2. Step 6 private ledger records additive non-anchor pressure;
3. protected payload gate does not detect introduced omission;
4. ledger and source custody validate;
5. Step 6 records a specific public-answer delta, currently one of:
   `added_entities`, `removed_entities`, `reordered_sequences`, or
   `structural_delta`. Generic `reframed_emphasis` alone does not unlock.
```

Otherwise the system falls back to anchor-visible/current-Step-6 behavior and
keeps the deck private for audit.

This is still not a promotion decision. It is also not yet implementation
approval. Before this draft becomes the integration contract for dormant/shadow
work, the symmetric false-positive visibility probe must pass or the design must
be revised.

2026-05-21 update: `false_positive_visibility_probe_v0` has run. It did not
find a confirmed false positive: Step 6 stood down on the Bevelin and Polya
overpromotion cases. The marker-preserved/entity-lost dimension is
`not_observed`, not passed, because the constructed case did not cause Step 6 to
mark generalized pressure additive while losing concrete entities. This draft
therefore remains proposed architecture, with marker/entity loss still a live
calibration risk.

2026-05-21 update 2: `shadow_triggered_false_positive_probe_v0` has run after
the shadow harness began recording marker/entity-loss candidate flags. Founder,
PhD, and consultant surfaced as candidates. Fresh Step 6 stood down on PhD and
consultant; founder reached additive pressure but was demoted to
`ambiguous_visibility` because reviewer labels and blind winner arms were tense.
The design draft therefore needs an added custody expectation before any visible
pilot: reviewer and Step 6 ledger evidence must expose answer-delta specificity
and label/winner consistency, not only final labels.

2026-05-21 update 3: repaired calibration and model-family review have now
blocked global promotion. The Kimi calibration left four variable cases after
repeat sampling. A GPT diagnostic stabilized three, but the split reviewer
review showed GPT stability is not automatically correctness: GPT PhD visible
outputs were supported 6/6, including 3/3 pure `structural_delta_present`
samples, while GPT's consultant anchor stand-down had 1 rejected sample and
2 ambiguous samples. Founder V60-on stayed variable under both Kimi and GPT,
while founder V60-off was stable under both families. This draft is therefore
still proposed research architecture only. Model-family choice is part of the
calibrated contract and cannot become a hidden cognitive shortcut.

## Evidence Base

This draft rests on four research slices:

| Slice | Result |
| --- | --- |
| `false_standdown_bridge_probe_v0` | Universal anchor fallback caused confirmed false stand-down in all three dangerous bridge packets. |
| `design_preamble_visibility_policy_redesign_v0` | A ledger-mediated rule can surface deck-aware output without adding a runtime reviewer loop. |
| `bridge_step6_ledger_replay_v0` | Live Step 6 replay produced `additive_pressure_present` in all three bridge packets. |
| `false_positive_visibility_probe_v0` | Step 6 stood down on two tempting overpromotion cases; marker/entity loss remained `not_observed`. |
| `shadow_triggered_false_positive_probe_v0` | Shadow telemetry surfaced natural marker/entity candidates; fresh replay produced one ambiguous founder case and two stand-downs. |
| `design_preamble_calibration_floor_v0` | Promotion remains blocked because the seed suite is not a calibrated runtime floor. |
| `calibration_corpus_kimi_structural_delta_v0` | Corpus floor met, but 4/17 cases remained variable under the pinned Kimi Step 6 model. |
| `founder_v60_symmetry_check_v0` | Founder is variable specifically in V60-on condition under both model families; V60-off is stable under both families. |
| `gpt_stability_correctness_review_v0` | GPT-stable PhD visible outputs were supported, but GPT consultant stand-down was not cleanly supported. |

The bridge result is strong enough to design against. It is not strong enough to
promote by itself.

## Non-Goals

This draft does not:

- edit `SKILL.md`;
- change default `/lolla` runtime behavior;
- add a normal runtime reviewer loop;
- generate cards live on cache miss;
- let deterministic code score answer quality;
- replace Step 6 with Bevelin, Polya, V60, or any future lens;
- make the bridge packets count as full calibration.

## Integration Modes

| Mode | Deck Availability | Step 6 Ledger | Reviewer Loop | Visible Policy | Use |
| --- | --- | --- | --- | --- | --- |
| `off` | none | none | none | current behavior | default |
| `research_replay` | fixture or compiled deck | required | allowed offline only | archived, not product-visible | experiments |
| `experimental_shadow` | cached deck only | required | none | computed but not shown | telemetry and Observatory review |
| `experimental_visible` | cached deck only | required | none | ledger-mediated | narrow board-approved pilot |
| `runtime_on` | cached deck only | required | none | ledger-mediated | blocked until calibration |

Cold-path rule:

```text
cache miss -> current Step 6 visible, no live deck generation
```

The cache miss is archived as `card_deck_cache_miss`. This keeps runtime cost
bounded and prevents an unplanned cognitive stage from appearing in production.

## Data Flow

1. Existing pipeline produces the current Step 6 anchor context.
2. Deck compiler looks for a cached compiled deck for the run.
3. If cache misses, Step 6 runs normally and the deck path stands down.
4. If cache hits, Step 6 receives the anchor plus compact private cards.
5. Step 6 returns:
   - public-clean `answer_core`;
   - private `private_consideration_ledger`.
6. Payload gate compares anchor and Step 6 answer for protected categories:
   - tripwires or gates;
   - dates or windows;
   - actor sequence;
   - named resources;
   - communication boundaries;
   - evidence checks.
7. Deterministic visibility resolver reads cache state, ledger signal, payload
   result, and custody validity.
8. Archive stores all inputs, outputs, source refs, ledger entries, payload
   results, and final visibility decision.
9. Observatory shows a compact operator view without exposing private machinery
   to the user.

## Step 6 Prompt Contract

Step 6 receives the private deck as reasoning context, not as answer text.

The prompt must say:

```text
Use, combine, reject, defer, or keep private any card.
Do not lengthen the public answer merely to prove every card was considered.
Do not expose private labels, ids, or machinery.
Preserve concrete protected payload unless you have a reason to replace it.
Record private consideration in the ledger.
```

Required response shape:

```json
{
  "answer_core": "Public-clean answer.",
  "private_consideration_ledger": [
    {
      "item_id": "reasoning_card:bevelin_card",
      "source_kind": "anchor | reasoning_card | v60_chunk",
      "source_ref": "archive/source/ref",
      "disposition": "used | combined | rejected | deferred | private_guardrail",
      "composition_role": "visible_backbone | additive_pressure | confirming_support | private_guardrail",
      "why": "Private reason Step 6 handled the item this way.",
      "visible_effect": "What changed publicly, or 'none'."
    }
  ]
}
```

The ledger is not a public explanation. It is the cognitive audit trail.

## Unified Ledger Rule

There should be one private-consideration ledger, not separate V60 and card
ledgers.

Minimum entry:

```json
{
  "item_id": "reasoning_card:polya_card",
  "source_kind": "reasoning_card",
  "source_ref": "research/pre-step6-private-reasoning-cards/...",
  "overlap_group_id": "optional-overlap-id",
  "presentation_state": "primary_presented | supporting_ref_not_repeated | archived_only",
  "disposition": "used | combined | rejected | deferred | private_guardrail",
  "composition_role": "visible_backbone | additive_pressure | confirming_support | private_guardrail",
  "why": "Private Step 6 rationale.",
  "visible_effect": "Public effect, or none."
}
```

Redundancy handling:

- hot context dedupes overlapping V60/card pressure;
- archive preserves every source item;
- overlap is represented through `overlap_group_id`;
- the operator view shows the primary presented item plus supporting refs.

This prevents duplicate prompt bloat without losing custody.

## Visibility Resolver

The resolver is deterministic, but it is not a cognitive judge.

Inputs:

```json
{
  "cache_state": "cache_hit | cache_miss",
  "ledger_signal": "additive_pressure_present | all_private_or_confirming | missing_or_unclear",
  "payload_gate_result": "preserved | introduced_omission | case_n_a",
  "custody_valid": true
}
```

Policy:

| Condition | Visible Result | Why |
| --- | --- | --- |
| `cache_miss` | `current_step6_visible_no_deck` | No live deck generation. |
| `custody_valid=false` | `anchor_visible_custody_guardrail` | Do not surface unauditable output. |
| `payload_gate_result=introduced_omission` | `anchor_visible_payload_omission_guardrail` | Deck-aware answer lost protected anchor payload. |
| `ledger_signal=missing_or_unclear` | `anchor_visible_unclear_ledger_guardrail` | Code cannot infer Step 6 cognition. |
| `ledger_signal=all_private_or_confirming` | `anchor_visible_deck_private` | Step 6 did not record additive non-anchor pressure. |
| `ledger_signal=additive_pressure_present` and payload preserved | `deck_visible_from_step6_additive_pressure` | Step 6 supplied the cognitive signal. |

The resolver may derive `ledger_signal` from the ledger schema. It may not
invent or override Step 6's judgment.

## Model Commitment Rule

The Step 6 model class is part of this contract.

This means:

- calibration claims are scoped to the Step 6 model family and prompt contract
  that produced them;
- switching from Kimi to GPT, upgrading the model version, changing provider,
  or allowing OpenRouter to route to a materially different backend requires a
  recalibration read;
- model-family stability is not a substitute for reviewer cognition;
- mixed-model samples are diagnostic evidence unless a promotion read explicitly
  defines them as a cross-model contract.

The deterministic system may record model family, model version, backend
metadata, and stability distributions. It may not choose a model because that
model produces the most convenient visibility decision.

## Payload Gate

The payload gate is a tripwire, not a selector.

It asks:

```text
Did the deck-aware answer introduce a protected omission relative to the anchor?
```

It does not ask:

```text
Which answer is wiser?
```

Records should keep both levels:

- category-level preservation: `preserved`, `introduced_category_omission`,
  `case_n_a`, `deck_added_payload`;
- within-category caution:
  `preserved_by_marker_anchor_entities_missing`.

If a marker is preserved but anchor entities are missing, this should not
automatically block visibility in this design draft. It should be tracked as a
calibration outcome and escalated if correlated with reviewer preference for
the anchor.

## Cache Contract

The compiled deck cache key should be content-addressed over:

- schema version;
- lens/card versions;
- source substrate hashes;
- problem-state hash;
- rendered anchor hash;
- V60 selected-item hash or `v60_not_attached`;
- safety flags;
- Step 6 prompt contract version.

Not acceptable:

- per-substrate static cards only;
- per-case-type templates only;
- live runtime generation on miss.

The compiled deck can be generated in research or offline precompute paths. It
is not generated inside normal runtime.

## Archive Fields

Each run that enters the experimental path should archive:

```json
{
  "pre_step6_control_layer": {
    "mode": "experimental_shadow",
    "compiled_card_deck_key": "...",
    "cache_state": "cache_hit",
    "source_refs": ["..."],
    "step6_prompt_contract_version": "pre_step6_step6_ledger_prompt.v1",
    "step6_answer_ref": "...",
    "private_consideration_ledger_ref": "...",
    "ledger_signal": "additive_pressure_present",
    "payload_gate_ref": "...",
    "payload_gate_result": "preserved",
    "visibility_decision": "deck_visible_from_step6_additive_pressure",
    "visibility_decision_reason": "cache_hit + additive Step 6 ledger + preserved payload",
    "normal_runtime_reviewer_calls": 0,
    "runtime_wiring_allowed": false,
    "skill_update_allowed": false
  }
}
```

For `off` mode, the archive may record only that the layer was not active.

## Observatory View

Operator view should show:

- mode and cache state;
- visible decision;
- ledger signal;
- payload gate result;
- protected payload warnings;
- source custody summary;
- overlap groups;
- card/V60 items that were additive, confirming, private, or rejected.

It should not show private card prose as if it were user-facing answer content.

Useful operator labels:

```text
visible backbone
additive pressure
confirming support
private guardrail
payload omission guardrail
cache miss stand-down
unclear ledger guardrail
```

## Cost Envelope

Normal runtime target:

```text
0 extra reviewer calls
0 live card-generation calls
1 Step 6 call with larger private context only when cache hit
```

Research/offline paths may spend calls to generate decks, compare candidates,
or calibrate reviewers. Those calls must stay out of normal runtime.

The design accepts token growth inside Step 6 only if the card deck stays
compact and deduped. The point is broad private context, not a full artifact
dump.

## Promotion Gates

Before `runtime_on`, all of these must pass:

- 12-20 case calibration floor;
- at least 3 high-clutter cases;
- at least 3 sensitive/safety/legal cases;
- at least 3 sequencing/problem-shape cases;
- at least 3 negative controls;
- at least 2 same-case V60 on/off pairs;
- measured false-standdown rate;
- measured false-promotion rate;
- protected payload preservation tracked by category and by missing anchor
  entities;
- no critical custody failures;
- acceptable latency/cost envelope;
- Observatory can explain every visible decision.

Bridge evidence can justify this proposed dormant architecture. It cannot
justify runtime promotion. The false-positive probe and the focused
marker/entity-loss follow-up both lower overpromotion risk, but marker/entity
loss remains technically `not_observed`; that dimension should still be tracked
in the full calibration floor.

## Implementation Slices

Recommended implementation order:

1. Add dormant config flags and archive fields only.
2. Add compiled-deck cache lookup with cache-miss stand-down.
3. Add Step 6 prompt contract behind `experimental_shadow`.
4. Add unified ledger validation and signal derivation.
5. Add payload gate attachment.
6. Add deterministic visibility resolver in shadow mode.
7. Add Observatory read model.
8. Run fixed suite plus bridge packets in shadow mode.
9. Decide whether to curate full calibration or open a narrow
   `experimental_visible` pilot.

Each slice should be test-first and vertical:

```text
one behavior -> one test -> one implementation -> archive proof
```

## Falsifiers

Stop or redesign if:

- Step 6 overuses deck cards and makes negative controls worse;
- `additive_pressure_present` becomes too easy for Step 6 to emit;
- payload gate misses repeated concrete losses inside categories;
- cache misses happen often enough that the path is mostly inactive;
- Observatory cannot explain why an answer became visible;
- operators cannot distinguish additive pressure from confirming support;
- latency grows because the private deck becomes an artifact dump;
- V60 overlap creates duplicate hot context or hides source custody.

## Recommendation

Proceed only with caution.

The design is now coherent enough to implement behind flags because the bridge
probe and live Step 6 replay both point in the same direction: universal anchor
fallback is too restrictive, and Step 6's ledger can carry the needed cognition.

The mirror false-positive probe did not find an overpromotion failure, and the
focused marker/entity-loss follow-up showed Step 6 preserving concrete anchor
entities while keeping generic deck pressure private/confirming. The hardest
omission-gate dimension remains unobserved rather than closed. If implementation
starts now, keep it ultra-dormant: flags, archive fields, validation contracts,
and shadow-only visibility decisions.

Do not promote runtime. The calibration floor remains the real gate.

2026-05-21 implementation update: the ultra-dormant shadow slice has landed.
The implemented runtime surface is intentionally narrower than this full design
draft:

- default-off `--pre-step6-portfolio shadow`;
- cached-only deck lookup with cache-miss stand-down;
- Step 6 ledger-signal derivation when a ledger is supplied;
- payload/custody guardrail recording;
- `pre_step6_shadow_portfolio.v1` sidecar writing and archive copying;
- `/audit/pre-step6` and case API visibility;
- no visible-output application;
- no runtime reviewer calls;
- no live card generation;
- no `SKILL.md` behavior change.

This confirms the first implementation slice only. It does not approve Step 6
prompt changes, deck injection, `experimental_visible`, or `runtime_on`.

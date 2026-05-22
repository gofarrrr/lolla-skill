# Marker/Entity-Loss Follow-Up Readout

Date: 2026-05-21

Status: research-only, non-promotional. `SKILL.md` and runtime remain untouched.

## Probe

Follow-up id:

```text
marker_entity_loss_followup_v0
```

Source contract:

```text
research/pre-step6-marker-entity-loss-followup/marker-entity-loss-followup.v1.json
```

Step 6 replays:

```text
research/pre-step6-marker-entity-loss-followup/step6-replays/*.marker-entity-step6-replay.v1.json
```

Aggregate result:

```text
research/pre-step6-marker-entity-loss-followup/marker-entity-loss-followup-result.v1.json
```

## Why This Follow-Up Exists

The false-positive visibility probe lowered overpromotion risk, but left one
dimension unclosed:

```text
Step 6 marks deck additive
deck-aware answer keeps broad category markers
deck-aware answer loses concrete anchor entities
reviewers prefer anchor
```

The earlier probe did not naturally reach that shape. This follow-up tried three
focused construction attempts to stress the exact marker/entity-loss weakness.

## Contract

The follow-up contract pins:

- three pre-registered attempts;
- a maximum of three construction attempts;
- `not_observed` as the correct result if no attempt produces additive pressure
  plus anchor-entity loss;
- the warning that null evidence does not prove the omission gate is strong
  enough;
- the same two-reviewer-family confirmation rule if the failure shape appears.

The deterministic detector is deliberately narrow. It checks whether all named
category markers are present and whether any pre-registered anchor entities are
missing. It does not grade answer quality.

## Live Run

Step 6 model:

```text
openai/gpt-5.1-chat
```

Command:

```text
LOLLA_LLM_TIMEOUT=60 PYTHONPATH=. python3 scripts/research/pre_step6_marker_entity_loss_followup.py --live --all --provider openrouter --step6-model openai/gpt-5.1-chat --env-file /Users/marcin/Desktop/Apps/Lolla/.env.openai.local
```

Reviewer calls:

```text
0
```

No reviewer calls were needed because none of the three attempts emitted the
precondition:

```text
ledger_signal: additive_pressure_present
marker_entity_detection.failure_shape_observed: true
```

## Result

| Attempt | Shape | Step 6 Ledger Signal | Construction Label |
| --- | --- | --- | --- |
| `marker-entity-attempt-1-resource-generalization` | resource generalization | `all_private_or_confirming` | `not_observed` |
| `marker-entity-attempt-2-tripwire-compression` | tripwire compression | `all_private_or_confirming` | `not_observed` |
| `marker-entity-attempt-3-actor-sequence-blur` | actor sequence blur | `all_private_or_confirming` | `not_observed` |

Aggregate:

```text
followup_result: not_observed
promotion_effect: none_bridge_only
runtime_wiring_allowed: false
skill_update_allowed: false
```

## Interpretation

The dangerous failure shape was not observed.

This is better than a weak null result because Step 6 did not merely fail to
trigger the detector. It actively recognized that the deck pressure was generic
and that using it visibly would lose concrete payload:

- attempt 1 kept RAINN, therapist/counsel, phone channel, request-to-meet and
  other concrete tripwire language; deck pressure was rejected as abstract;
- attempt 2 kept request to meet, sexual images, threats, other minors, hidden
  channels, and pressure/fear language; deck pressure was rejected as a private
  guardrail;
- attempt 3 kept RAINN, therapist/counsel, co-parent sequencing, and the
  before-reporting order; deck pressure was only confirming support.

The result supports the core philosophy:

```text
Step 6 thinks.
Deterministic code validates.
Generic private pressure is not automatically public value.
```

## What This Proves

This follow-up reduces the strongest remaining false-positive concern for the
ledger-mediated policy:

```text
When the deck pressure was generic and entity-losing, Step 6 stood down.
```

It also shows that the Step 6 ledger can distinguish:

- visible backbone from anchor;
- generic deck support as confirming/private;
- concrete payload preservation as more important than using every card.

## What This Does Not Prove

This does not fully close the omission-gate weakness.

The probe still did not observe a natural run where Step 6 both:

```text
marks additive_pressure_present
drops concrete anchor entities while preserving category markers
```

Therefore the marker/entity-loss detector remains a known calibration dimension,
not a solved production safeguard. Full calibration should still track
`preserved_by_marker_anchor_entities_missing`.

## Recommendation

Do not promote runtime.

The research evidence is now strong enough to allow the next engineering step
only if it stays ultra-dormant:

```text
shadow-only flags
archive fields
validation contracts
Observatory/readout plumbing
no visible behavior change
no SKILL.md behavior change
```

Runtime visibility should remain blocked until either the full calibration floor
is curated or the board explicitly approves a narrow shadow pilot whose output
is logged but not shown.

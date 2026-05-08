# PR55 v18 Packet Stress Review

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`

Status: review-only audit artifact

Scope: dormant packet producer and review renderer using explicit `affordances_v18.json`.

## Verdict

The current packet producer can enrich nominated model IDs from v18 in a useful review-only way, but the current rendered handoff is not strong enough for future runtime pickup.

The weak point is not whether v18 records exist. They do.

The weak point is whether a future receiver can still see:

- which affordance is being considered;
- why it was nominated;
- what evidence would be needed;
- which absence or misuse guard blocks overclaiming;
- whether support is weak or medium-confidence;
- whether a broad/meta card is crowding out narrower cards.

Current answer: partially for human review, not reliably enough for live receiver transactions.

## Method

This was a read-only stress probe:

- used explicit `data/compiled/model_affordances/affordances_v18.json`;
- used synthetic `CandidateNomination` rows;
- did not call an LLM;
- did not import the packet producer into live `/lolla`;
- rendered packets through `engine/system_b/reasoning_substrate_packet_review.py`.

Fixture types:

- broad/meta-heavy packet;
- weak-support packet;
- absence-heavy packet;
- normal 12-card packet;
- 16-card pressure packet;
- narrow/no-meta packet.

## Stress Probe Summary

| Fixture | Cards | Reviewed cards | Weak/conflicting cards | Affordances exposed in packet fields | Absence records in packet fields | Multi-affordance cards | Render lines | Render chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| broad_meta_heavy | 12 | 12 | 0 | 14 | 22 | 1 | 250 | 15023 |
| weak_support | 12 | 10 | 2 | 14 | 27 | 2 | 251 | 16625 |
| absence_heavy | 12 | 12 | 0 | 19 | 36 | 7 | 251 | 18795 |
| normal_12 | 12 | 12 | 0 | 15 | 17 | 3 | 249 | 16608 |
| pressure_16 | 16 | 14 | 2 | 27 | 21 | 6 | 315 | 20850 |
| narrow_no_meta | 12 | 11 | 1 | 13 | 24 | 1 | 251 | 16799 |

## Stress Fixtures

### Broad/Meta-Heavy

Models:

`systems-thinking`, `latticework-of-mental-models`, `chain-of-thought`, `meta-cognitive-reflection`, `mental-models-of-reality`, `reasoning-mode-router`, `system-1`, `system-2`, `complexity-bias-resistance`, `logical-fallacies`, `circle-of-competence`, `intellectual-humility`.

Finding:

The packet remains readable as a review artifact, but broad cards are semantically attractive. They need caps, labels, and stronger "candidate material, not judgment" instruction before live use.

### Weak-Support

Models:

`devops-and-continuous-integration`, `price-discrimination`, `adverse-selection`, `batna`, `markov-chains`, `principal-agent-problem`, `six-thinking-hats`, `information-asymmetry`, `moral-hazard`, `signaling`, `elasticity`, `supply-and-demand`.

Finding:

Weak/conflicting records are structurally marked in the packet as `conflicting_or_weak_support`, but the rendered handoff does not make the warning loud enough. It lacks a first-class line such as "Weak support: do not promote without review."

### Absence-Heavy

Models:

`antifragility`, `prioritization`, `optimization-theory`, `experimentation`, `moral-hazard`, `survivorship-bias`, `social-proof`, `black-swan-events`, `principal-agent-problem`, `six-thinking-hats`, `resilience`, `pareto-principle`.

Finding:

The packet can carry many absence records internally, but the renderer shows only one absence item per card. That is compact, but it risks hiding the exact absence that should block use.

### Normal 12-Card

Models:

`base-rates`, `trade-offs`, `power-dynamics`, `algorithmic-thinking`, `delays`, `obligations-controls-mapping`, `opportunity-cost`, `premortem`, `decomposition`, `incentives`, `risk-assessment`, `feedback-loops`.

Finding:

This is the most promising size and shape. A 12-card cap looks plausible for review, provided confidence, absences, and provenance are not flattened.

### 16-Card Pressure

Models:

`systems-thinking`, `latticework-of-mental-models`, `chain-of-thought`, `algorithmic-thinking`, `confidence-calibration`, `inversion`, `devops-and-continuous-integration`, `price-discrimination`, `power-dynamics`, `trade-offs`, `base-rates`, `obligations-controls-mapping`, `delays`, `complex-adaptive-systems`, `problem-framing-and-reframing`, `meta-cognitive-reflection`.

Finding:

The 16-card packet is usable for a human stress review, but likely too heavy for routine live receiver handoff unless the renderer becomes more selective. It should remain a pressure-test size, not the default.

### Narrow/No-Meta

Models:

`base-rates`, `trade-offs`, `opportunity-cost`, `switching-costs`, `batna`, `price-discrimination`, `supply-and-demand`, `elasticity`, `adverse-selection`, `moral-hazard`, `principal-agent-problem`, `redundancy`.

Finding:

Narrow packets feel more actionable. This supports a future cap strategy that prevents broad/meta cards from consuming too much packet surface.

## Concrete Failures To Harden

### 1. Renderer Truncation Hides Multi-Affordance Structure

The renderer currently keeps packet review compact by displaying only one item per detail field.

This is fine for fixture review. It is not enough for transaction-level receiver decisions.

Example risk:

- `systems-thinking` has four affordances in v18;
- the packet fields expose at most three affordance IDs;
- the review renderer displays only one item per detail line;
- a future receiver cannot cleanly say which affordance it used, rejected, deferred, or merged.

### 2. Weak Support Is Too Quiet

Weak/conflicting support appears as coverage status, but it is not rendered as a strong warning.

Runtime handoff should make weak support hard to miss:

- record status;
- confidence;
- "tentative only" warning;
- explicit prohibition against promotion without case evidence.

### 3. Absence Records Are Not Yet First-Class Enough

v18 has 429 absence records. That is one of the most valuable anti-overclaim assets.

But in current rendered packets, absence can look like a footer. In live use, absences should be treated as candidate blockers, not decoration.

### 4. Broad/Meta Cards Need Packet Discipline

Broad cards can help the receiver notice missing reasoning moves. They can also create model-name theater.

Packet discipline should include:

- broad/meta cap;
- lower display priority unless lane provenance is strong;
- required concrete case evidence;
- strong "not mandatory" instruction;
- no deterministic final pressure selection.

### 5. 12 Cards Looks Plausible; 16 Cards Is Review-Only

A default packet cap around 10-12 cards looks more plausible than 16.

Sixteen cards is useful for stress review because it reveals failure modes. It should not become a normal receiver packet size without additional compression and grouped identity.

## Recommendation

Before live pickup, harden the packet shape in this order:

1. Preserve grouped per-affordance identity.
2. Add first-class confidence and weak-support warnings.
3. Promote absence records into explicit overclaim rails.
4. Aggregate duplicate lane provenance before dedupe.
5. Cap broad/meta cards separately from narrow case cards.
6. Keep v18 artifact selection explicit.
7. Keep all packet tests static until receiver behavior is evaluated.

## Bottom Line

The packet producer is good enough for dormant review.

It is not yet good enough for live receiver transactions because compression currently hides too much epistemic shape.

# PR55 Lane-To-Nomination Provenance Contract

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr55-v18-pickup-quality-audit`

Status: review-only contract draft

Scope: existing lanes in `engine/system_b/` and a future dormant adapter that would turn lane outputs into `CandidateNomination` rows.

## Verdict

The future pickup layer should not run new reasoning. It should collect model IDs already emitted by existing lanes, preserve why each ID was nominated, dedupe carefully, and enrich only after nomination.

The most important rule:

> Recall broadly, attribute narrowly.

The adapter can gather candidate shelves from all lanes. It must not flatten user framing evidence, assistant-answer evidence, structural gap evidence, and tendency-route evidence into one generic reason.

## Current Lane Surfaces

### Lane 1: Tendency Routing

Relevant existing data:

- `TendencyRoute.primary_model_id`;
- `TendencyRoute.supporting_model_ids`;
- `TendencyRoute.risk_model_ids`;
- `TendencyRoute.primary_activation_context`;
- `TendencyRoute.tiebreakers`;
- `DeltaFinding.primary_model_id`;
- `DeltaFinding.supporting_model_ids`;
- `DeltaFinding.risk_model_ids`;
- `DeltaFinding.selected_model_ids`;
- `DeltaFinding.specific_passage`;
- `DeltaFinding.intervention_hint`;
- `DeltaFinding.major_tensions`;
- `DeltaFinding.challenge_statement`;
- `DeltaFinding.next_move`.

Candidate use:

Lane 1 is the strongest bridge into nominations because it already knows which tendency failure pulled which corrective shelf.

Provenance caution:

Lane 1 should not be described as "assistant said X" unless the lane artifact carries a validated assistant quote. Otherwise, the evidence source should be `lane_route` or `conversation_ir`, with the quoted surface kept only if custody is clear.

### Lane 2: Companion Detection

Relevant existing data:

- `DetectedModel.model_id`;
- `DetectedModel.evidence_quote`;
- `DetectedModel.presence_mode`;
- `DetectedModel.presence_explanation`;
- `DetectedModel.detection_confidence`;
- `CompanionCard.detected_models`;
- `CompanionCard.tension_pairs`.

Candidate use:

Lane 2 can nominate models based on assistant-answer model presence or model-pattern violations.

Provenance caution:

This lane must stay assistant-attributed. Its quotes and explanations should not be rewritten as user framing or case facts.

### Lane 3: Frame Pressure

Relevant existing data:

- `ExtractedFrameElement.evidence_quote`;
- `ExtractedFrameElement.frame_pattern`;
- `ExtractedFrameElement.framing_pressure`;
- `FrameRoute.candidate_model_ids`;
- `FrameRoute.reframed_question`;
- `FrameRoute.route_reason`;
- `FramePressureCard.routes`;

Candidate use:

Lane 3 can nominate shelves when user framing creates pressure that a model can challenge or rebalance.

Provenance caution:

This lane is user-framing-attributed. It does not prove the model is relevant to the final answer; it says the user's frame pulled a candidate pressure.

### Lane 4: Structural Coverage

Relevant existing data:

- `DetectedDimension.dimension_id`;
- `DetectedDimension.dimension_name`;
- `DetectedDimension.evidence_quote`;
- `DetectedDimension.materiality`;
- `DimensionRoute.candidate_model_ids`;
- `DimensionRoute.coverage_reason`;
- `StructuralCoverageCard.uncovered_dimensions`;

Candidate use:

Lane 4 can nominate shelves as structural gap hints.

Provenance caution:

Lane 4 questions should not leak raw into product surface. For packet nomination, they can provide gap provenance, not final advice.

## CandidateNomination Contract

A future adapter should create rows with at least:

```json
{
  "model_id": "base-rates",
  "pulled_by": "lane1_tendency_route",
  "why_pulled": "Corrective shelf for reference-class omission in a tendency route.",
  "lane_order": 1,
  "score": 0.72,
  "evidence_quote": "optional, only when quote custody is clear",
  "evidence_source_type": "lane_route",
  "source_lane_payload_ref": "optional stable pointer for audit"
}
```

Allowed `pulled_by` values should stay explicit and boring:

- `lane1_tendency_route`;
- `lane1_supporting_model`;
- `lane1_risk_model`;
- `lane2_detected_model`;
- `lane2_tension_pair`;
- `lane3_frame_route`;
- `lane4_gap_route`;
- `reviewer_note`;
- `static_fixture`.

Avoid generic values like `system`, `reasoning`, or `recommended`.

## Deduplication Rule

Exact `model_id` dedupe is necessary for compact packets, but naive dedupe loses provenance.

Current packet construction suppresses duplicate nominations after the first model ID. That is acceptable for static fixture review. It is risky for runtime because the same model may be nominated by several lanes for different reasons.

Future adapter should merge provenance before packet construction:

```json
{
  "model_id": "trade-offs",
  "merged_provenance": [
    {
      "pulled_by": "lane1_tendency_route",
      "why_pulled": "Corrective shelf for optimizing one objective while ignoring another."
    },
    {
      "pulled_by": "lane3_frame_route",
      "why_pulled": "User framing treats a conflict as one-sided instead of a trade-off."
    }
  ],
  "primary_provenance": "lane1_tendency_route"
}
```

The packet can still display one compact card. It should not erase the fact that multiple lanes pulled it.

## Attribution Rules

### User-Framing Evidence

Use when:

- source is Lane 3 frame pressure;
- quote comes from user message or extracted frame element;
- the model is being nominated as a reframing pressure.

Do not state:

- that the assistant failed;
- that the model is definitely needed;
- that the user is wrong.

### Assistant-Answer Evidence

Use when:

- source is Lane 2 companion detection;
- quote comes from assistant answer;
- the model is present, absent, conflicted, or misused in the assistant response.

Do not state:

- that the user asked for the model;
- that the case facts prove the model's use.

### Structural Gap Evidence

Use when:

- source is Lane 4 structural coverage;
- the lane has identified an uncovered dimension;
- candidate models are gap hints.

Do not state:

- that the model is selected;
- that the gap is a factual conclusion;
- that a question from Lane 4 should become final product copy.

### Tendency Route Evidence

Use when:

- source is Lane 1 tendency routing;
- a tendency pattern maps to a corrective shelf;
- candidate models are tied to the route.

Do not state:

- that a route is proof;
- that every supporting/risk model deserves packet inclusion;
- that risk models are positive recommendations.

## Cap Strategy For Future Adapter

The adapter should probably cap in layers:

1. Keep Lane 1 primary models unless blocked by explicit rules.
2. Add Lane 2 detected models when they have strong quote custody.
3. Add Lane 3 frame routes when they offer a distinct pressure.
4. Add Lane 4 gap routes only when they add a missing dimension.
5. Add broad/meta cards only under a separate small cap.
6. Preserve merged provenance for duplicates.
7. Stop before the packet becomes a model-name dump.

This cap strategy should be tested in static replay before live pickup.

## Adapter Non-Goals

The future adapter must not:

- infer new affordances;
- run new semantic matching against the source corpus;
- choose final mental models;
- promote weak-support records;
- auto-select the latest affordance artifact;
- import v18 into live runtime without an explicit gate;
- flatten lane provenance into generic "recommended because relevant" language.

## Review-Only Acceptance Criteria

PR55 can pass this section if it documents:

- which lane fields can become nominations;
- how lane provenance should be preserved;
- how duplicate model IDs should be merged without losing reasons;
- why the adapter is enrichment-only, not a new reasoning lane;
- why explicit artifact selection is required.

## Bottom Line

The future pickup layer should be a courier, not a judge.

It carries nominated shelves, provenance, reviewed affordance cards, absences, and warnings to the receiver. It does not decide which cognition is true.

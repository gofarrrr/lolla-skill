# Reasoning Substrate Lane Placement Audit

**Date:** 2026-05-06
**PR slice:** PR25 - enrichment placement
**Status:** review-only architecture audit
**Decision label:** `enrichment_placement_audit_complete`

## Verdict

A future `reasoning_substrate_packet.v1` producer should sit after the existing
lanes have produced their normal artifacts, next to the current route-trace
serialization boundary. It should not become a fifth lane and should not change
lane selection behavior.

The safe PR25 code insertion point is a dormant explicit-nomination producer:
`engine/system_b/reasoning_substrate_packet.py`. That module accepts candidate
model IDs and lane provenance supplied by a fixture or review adapter. It does
not run live lanes, import from `/lolla`, change prompts, or select final
Decision Pressure.

## Existing Lane Outputs That Can Nominate Candidate Shelves

### Lane 1 - Tendency Failure And Corrective Routes

Primary files and objects:

- `engine/system_b/pipeline.py`
  - `TriggeredTendency`
  - `DeltaFinding`
  - `DeltaCard`
  - `PipelineResult.routes`
  - `_assemble_delta_card(...)`
- `engine/system_b/routing.py`
  - `TendencyRoute`
  - `route_tendency(...)`
  - `route_deep_check_results(...)`
- `engine/system_b/audit_assembly.py`
  - `AuditTrace.routing_decisions`
- `engine/system_b/route_trace.py`
  - `_lane1_trace(...)`

Nomination fields:

- `DeltaFinding.selected_model_ids`
- `DeltaFinding.primary_model_id`
- `DeltaFinding.supporting_model_ids`
- `DeltaFinding.risk_model_ids`
- `TendencyRoute.primary_model_id`
- `TendencyRoute.antidote_model_ids`
- `TendencyRoute.supporting_model_ids`
- `TendencyRoute.risk_model_ids`
- `TendencyRoute.supporting_candidate_trace`
- `TendencyRoute.risk_candidate_trace`

Evidence and context:

- Lane 1 starts from the transaction: `SystemBPipeline.run(...)` constructs a
  `ConversationIR` and uses assistant text plus transaction context for tendency
  triage, deep checks, embeddings, and routing.
- Embedding tendency recall currently uses assistant text through
  `_assistant_reasoning_text(...)`.
- Route relationship expansion can preserve deterministic route evidence:
  source model ID, edge type, raw affinity, fan-adjusted affinity, relevance
  score, selected flag, and rejection reason.

Enough for candidate cards:

- Model IDs are explicit.
- Lane order can be derived from route/finding order.
- `why_pulled` can be built from tendency ID, sub-pattern, route source,
  selected role, relation trace, and finding-specific passage when present.

Cleanup needed later:

- `DeltaFinding.selected_model_ids` can be compiled-chunk-driven when trusted
  bundles are active, while `TendencyRoute` can also carry primary, supporting,
  and risk IDs. A future adapter should preserve both without flattening them
  into one unexplained list.
- Some candidate trace rows have affinity and rejection metadata but no exact
  user or assistant quote. That is acceptable for shelf nomination, but the
  packet should label the evidence as route provenance, not source quote.

### Lane 2 - Assistant-Answer Model Attribution

Primary files and objects:

- `engine/system_b/pipeline.py`
  - `CompanionRunResult`
  - `_run_companion(...)`
  - `_serialize_detected_models(...)`
- `engine/system_b/companion.py`
  - `DetectedModel`
  - `CompanionCard`
  - `CompanionExpansion`
  - `CompanionIdentityChunk`
- `engine/system_b/companion_selection.py`
  - `CompanionCheatSheet`
  - `ModelAnchor`
- `engine/system_b/route_trace.py`
  - `_lane2_trace(...)`

Nomination fields:

- `CompanionCheatSheet.anchors[*].model_id`
- `CompanionRunResult.detected_models[*].model_id`
- `CompanionRunResult.accepted_before_cap[*].model_id`
- `CompanionRunResult.candidates[*].model_id`
- `CompanionRunResult.capped_models[*].model_id`
- `CompanionCard.identity_chunks[*].model_id`

Evidence and context:

- Lane 2 is assistant-attribution work. Candidate recall uses
  `_lane2_joined_assistant_turns(conversation_context)` with
  `_assistant_reasoning_text(conversation_context)` as fallback.
- `DetectedModel` carries `evidence_quote`, `presence_mode`,
  `presence_explanation`, and `detection_confidence`.
- Audit buckets preserve accepted-before-cap, rejected, capped, duplicate,
  quote-repaired, and silently omitted candidates.

Enough for candidate cards:

- Accepted and surfaced anchors provide explicit model IDs.
- Candidate rows and verification buckets can provide provenance, score/order,
  quote status, and drop reason.
- Assistant-only attribution can remain intact if a future adapter labels
  `evidence_source_type: assistant_turn`.

Cleanup needed later:

- `route_trace.v1` currently carries candidate and rejection buckets, but a
  packet adapter should decide which Lane 2 rows are nominations versus
  suppressed candidates. That should be a mechanical policy, not a semantic
  judgment.
- Capped and silently omitted models are not semantic rejects. A packet adapter
  should preserve those statuses honestly instead of burying them.

### Lane 3 - User-Framing Shelf Hints

Primary files and objects:

- `engine/system_b/frame_pressure.py`
  - `ExtractedFrameElement`
  - `FrameRoute`
  - `Reframing`
  - `FramePressureCard`
  - `run_frame_extraction_from_packet(...)`
  - `route_frame_elements(...)`
  - `generate_reframings_from_context(...)`
- `engine/system_b/pipeline.py`
  - `_run_frame_pressure(...)`
- `engine/system_b/route_trace.py`
  - `_lane3_trace(...)`

Nomination fields:

- `FrameRoute.candidate_model_ids`
- `Reframing.grounding_model`
- `FrameRoute.excluded_model_ids` for anti-echo suppression

Evidence and context:

- Lane 3 audits the user's framing. `ExtractedFrameElement.evidence_quote`
  must be grounded in the user query/frame packet.
- Routes are deterministic mappings from frame pattern to model IDs, with
  anti-echo exclusions from Lane 1.
- Generated reframings are downstream product artifacts, not the right source
  for packet semantics. The model grounding can nominate a shelf; the
  reframed wording should not become a template.

Enough for candidate cards:

- Route candidates and grounding models carry explicit model IDs.
- `why_pulled` can include frame pattern, element type, evidence quote, and
  anti-echo exclusion status.

Cleanup needed later:

- `route_trace.v1` derives selected Lane 3 model IDs from returned reframings.
  A packet adapter should preserve raw `FrameRoute.candidate_model_ids` too,
  because candidates that did not become final reframings can still be useful
  shelves for the next LLM.

### Lane 4 - Structural Gap Shelf Hints

Primary files and objects:

- `engine/system_b/structural_coverage.py`
  - `DetectedDimension`
  - `DimensionRoute`
  - `GapQuestion`
  - `StructuralCoverageCard`
  - `run_structural_coverage_from_ir(...)`
  - `route_gap_dimensions(...)`
- `engine/system_b/pipeline.py`
  - `_run_lane4_structural_coverage(...)`
- `engine/system_b/route_trace.py`
  - `_lane4_trace(...)`

Nomination fields:

- `DimensionRoute.candidate_model_ids`
- `DimensionRoute.excluded_model_ids`
- `StructuralCoverageCard.gap_routes[*].candidate_model_ids`

Evidence and context:

- Lane 4 is transaction- and structure-aware. It classifies the question,
  detects dimensions, routes uncovered dimensions to candidate models, and
  generates discovery questions.
- The raw Lane 4 questions are not the product surface for PR25. The candidate
  model IDs and dimension provenance are enough for packet nominations.

Enough for candidate cards:

- `question_type`, `dimension_id`, `dimension_name`, uncovered/covered status,
  and candidate model IDs can produce clear `why_pulled` records.
- Anti-echo exclusions are explicit and can become suppressed candidates.

Cleanup needed later:

- `GapQuestion.questions` should not be promoted into final user-facing
  wording. A future packet adapter may include a compact "gap question exists"
  signal, but it should avoid turning raw questions into templates.
- Lane 4 currently has no v4 affordance integration and should remain that way
  until a review-only adapter proves the packet boundary.

## Current Object Carrying Cross-Lane Candidate IDs

The closest existing boundary object is `route_trace.v1`, built by
`engine/system_b/route_trace.py::build_route_trace_payload(...)` and attached
by `scripts/run_pipeline.py` under `audit_summary.route_trace`.

That module is the right architectural precedent because it is explicitly a
serializer/normalizer: it copies already-recorded lane artifacts and does not
infer why a model was selected.

Important current objects:

- `PipelineResult` carries lane outputs in memory.
- `scripts/run_pipeline.py` serializes `delta_card`, `companion_cheat_sheet`,
  `frame_pressure_card`, `structural_coverage_card`, and `audit_summary`.
- `route_trace.v1` normalizes selected model IDs, candidates, rejected
  candidates, anti-echo exclusions, and per-lane summaries.

## Recommended Packet Boundary

Future producer placement:

1. Live lanes run unchanged.
2. Existing serialization emits the normal result payload and `route_trace.v1`.
3. A dormant adapter, not imported by runtime, maps explicit route-trace rows
   or reviewed fixtures into `CandidateNomination` records.
4. `engine/system_b/reasoning_substrate_packet.py` enriches those nominations
   with graph fields, v4 snippets when present, absence records, source
   custody, coverage labels, caps, and provenance.
5. The LLM/reviewer consumes the compact packet and decides what matters.

PR25 implemented step 4 for explicit nominations only. It intentionally did
not implement step 3 for live route traces.

## Live Paths To Leave Untouched

These paths must remain unchanged for this slice:

- `engine/system_b/pipeline.py`
- `scripts/run_pipeline.py`
- live `/lolla` entry points
- prompt templates and boundary-call code
- `engine/system_b/route_trace.py`
- Observatory rendering
- memo, Step 6, Step 8, and Lane 4 runtime affordance integration
- paid model-call scripts and judge runners

## Dormant Or Review-Only For Now

Review-only objects for PR25:

- `engine/system_b/reasoning_substrate_coverage.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `tests/test_reasoning_substrate_coverage.py`
- `tests/test_reasoning_substrate_packet.py`
- `research/full-corpus-enrichment-coverage-audit-2026-05-06.md`

These are allowed because they load existing artifacts, compare IDs, label
coverage, and package explicit nominations. They do not add live imports,
semantic ranking, prompt changes, model calls, or user-facing output.

## How v4 Should Enrich Without Replacing The 222 Graph

The enrichment rule is additive:

- Start with lane-nominated model IDs from the 222-model runtime graph.
- Deduplicate exact IDs and preserve lane order or lane scores when supplied.
- For models with v4 reviewed records, attach compact source-backed snippets.
- For graph-only models, attach compact graph context and label
  `graph_only_runtime_card`.
- For missing or unsupported material, expose absence records and
  do-not-overclaim notes.
- Apply caps after preserving provenance, and suppress candidates honestly.

The producer must not rank v4-reviewed models above graph-only models by
default. v4 is deeper evidence for a nominated card, not the matching system.

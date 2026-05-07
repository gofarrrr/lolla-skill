# Knowledge Substrate Roadmap - Make The Models Do More Work

**Date:** 2026-05-04
**Last updated:** 2026-05-07
**Audience:** future coding session with no prior conversation context
**Status:** living roadmap; PR13-PR41 are merged or in review, PR41 completed the after-v9 graph-only priority audit, and the current posture is `v9_graph_only_priority_audit_complete`
**Primary source substrate:** reviewed source files in `data/model_sources/`, copied from `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/` with SHA-256 manifest
**Current runtime repo:** `/Users/marcin/Desktop/Apps/lolla-skill/`
**Companion schema note:** `plans/knowledge-use-schema-2026-05-04.md`
**Product doctrine:** `research/decision-pressure-product-doctrine-2026-05-06.md`
**Current matching audit:** `research/knowledge-matching-current-state-audit-2026-05-06.md`
**Current packet strategy:** `research/enriched-mental-model-packet-strategy-2026-05-06.md`
**Source/packet audit brief:** `research/source-understanding-and-reasoning-packet-audit-brief-2026-05-06.md`
**Current source/packet audit:** `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`
**Current packet spec:** `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`
**Current lane placement audit:** `research/reasoning-substrate-lane-placement-audit-2026-05-06.md`
**Current full-corpus coverage audit:** `research/full-corpus-enrichment-coverage-audit-2026-05-06.md`
**Current source custody report:** `research/reasoning-substrate-source-custody-backfill-2026-05-06.md`
**Current packet fixture review:** `research/reasoning-substrate-packet-fixture-review-2026-05-06.md`
**Current controlled extraction report:** `research/pr28-controlled-graph-only-extraction-report-2026-05-06.md`
**Current v5 packet depth review:** `research/reasoning-substrate-v5-packet-depth-review-2026-05-07.md`
**Current packet rendering report:** `research/reasoning-substrate-packet-review-rendering-2026-05-07.md`
**Current packet comparison render:** `research/reasoning-substrate-packet-comparison-render-2026-05-07.md`
**Current v5 capability audit:** `research/v5-reviewed-model-capability-audit-2026-05-07.md`
**Current controlled capability-gap enrichment report:** `research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md`
**Current v6 packet usefulness review:** `research/reasoning-substrate-v6-packet-usefulness-review-2026-05-07.md`
**Current controlled communication/competition enrichment report:** `research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md`
**Current v7 packet usefulness review:** `research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md`
**Current controlled trust/negotiation enrichment report:** `research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md`
**Current v8 packet usefulness review:** `research/reasoning-substrate-v8-packet-usefulness-review-2026-05-07.md`
**Current v8 graph-only priority audit:** `research/v8-graph-only-priority-audit-2026-05-07.md`
**Current controlled execution/follow-through enrichment report:** `research/pr39-controlled-execution-followthrough-enrichment-report-2026-05-07.md`
**Current v9 packet usefulness review:** `research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md`
**Current v9 graph-only priority audit:** `research/v9-graph-only-priority-audit-2026-05-07.md`
**Next-session handover:** `research/reasoning-substrate-next-session-handover-2026-05-06.md`
**External architecture study:** `research/gbrain-architecture-learning-handover-2026-05-05.md`
**External decision-process study:** `research/clear-thinking-lolla-learning-handover-2026-05-05.md`

---

## 0. Current State Snapshot - 2026-05-06

This document began as a May 4 roadmap. The repo has now moved past the first
several steps. Future sessions should not restart from "define the schema."

What is already done:

- Active runtime graph count is `222` models in `data/knowledge_graph.json`.
- PR26 copied all `222` runtime model canonical source files into
  `data/model_sources/` with `data/model_sources/manifest.json` as the
  source-hash manifest. This is source custody, not v4 reviewed affordance
  coverage.
- The affordance extraction contract exists at
  `references/model-affordance-extraction.md`.
- The schema exists at `data/schemas/model_affordance.schema.json`.
- Validation rails exist in `engine/system_b/model_affordance_validation.py` and
  `tests/test_model_affordance_schema.py`.
- Pilot extraction is done for 10 models.
- Batch 1 extraction is done for 20 more models.
- Batch 2 extraction is done for 20 more Lane-4-frequency models.
- PR28 controlled extraction is done for 10 graph-only models selected from
  PR27 packet thinness and adjacent reasoning-gap evidence.
- PR29 packet depth review is done for the same 7-card PR27 nomination set
  regenerated against v5. The four formerly graph-only cards gained reviewed
  handoff depth, while candidate count and duplicate suppression stayed stable.
- PR30 packet review rendering is done for the PR27 packet, PR29 packet, and
  their before/after comparison. These are reviewer-only Markdown handoffs, not
  UI, memo, Observatory, or runtime output.
- PR31 v5 capability audit is done. It maps what the 65 reviewed records can
  support and names controlled enrichment gaps.
- PR32 controlled capability-gap enrichment is done for 16 graph-only models
  selected from the PR31 gap list. It adds Batch 5 records and compiles
  draft/review-only v6.
- PR33 v6 packet usefulness review is done for one explicit 10-card
  nomination set. The same packet goes from 1 reviewed / 9 graph-only cards
  under v5 to 10 reviewed / 0 graph-only cards under v6, without changing
  candidate count or producing final pressure/user-facing output.
- PR34 controlled communication/competition enrichment is done for 7
  graph-only models selected from communication, feedback, strategic
  interdependence, and analogy/adaptive gaps. It adds Batch 6 records and
  compiles draft/review-only v7.
- PR35 v7 packet usefulness review is done for one explicit 9-card
  communication/competition nomination set. The same packet goes from 2
  reviewed / 7 graph-only cards under v6 to 9 reviewed / 0 graph-only cards
  under v7, without changing candidate count or producing final
  pressure/user-facing output.
- PR36 controlled trust/negotiation enrichment is done for 10 graph-only
  models selected from trust repair, motivation, boundaries, persuasion,
  diplomacy, and signaling gaps. It adds Batch 7 records and compiles
  draft/review-only v8.
- PR37 v8 packet usefulness review is done for one explicit 10-card trust,
  negotiation, influence, and signaling nomination set. The same packet goes
  from 0 reviewed / 10 graph-only cards under v7 to 10 reviewed / 0 graph-only
  cards under v8, without changing candidate count or producing final
  pressure/user-facing output.
- PR38 after-v8 graph-only priority audit is done. It reviews the remaining
  124 graph-only runtime models, compares candidate capability families, and
  recommends execution / implementation / follow-through discipline as the
  next controlled enrichment family because future packets are likely to be
  thin where advice must become executable, inspectable, adjustable, and
  stoppable.
- PR39 controlled execution/follow-through enrichment is done for 12
  graph-only models selected from the PR38 priority audit. It adds Batch 8
  records and compiles draft/review-only v9. `devops-and-continuous-integration`
  remains intentionally thin/narrow because the source does not support full
  DevOps/CI doctrine.
- PR40 v9 execution packet usefulness review is done for one explicit 12-card
  execution/follow-through nomination set. The same packet goes from 0
  reviewed / 12 graph-only cards under v8 to 11 reviewed / 0 graph-only / 1
  weak-support card under v9, without changing candidate count or producing
  final pressure/user-facing output.
- PR41 after-v9 graph-only priority audit is done. It reviews the remaining
  112 graph-only runtime models after v9 and recommends risk controls /
  reversibility / failure containment as the next controlled enrichment family
  because future packets are likely to be thin where plausible and executable
  advice must become reversible, contained, monitorable, escalatable, and
  stoppable.
- Compiled v3 artifact exists at
  `data/compiled/model_affordances/affordances_v3.json`.
- v3 corpus shape: `50` model records, `86` affordances, `83` absence records,
  `0` schema validation failures, `0` source-quote rejections.
- Compiled v6 artifact exists at
  `data/compiled/model_affordances/affordances_v6.json`.
- v6 corpus shape: `81` reviewed records, `117` affordances, `147` absence
  records, `0` schema validation failures, `0` source-quote rejections.
- Compiled v7 artifact exists at
  `data/compiled/model_affordances/affordances_v7.json`.
- v7 corpus shape: `88` reviewed records, `124` affordances, `161` absence
  records, `0` schema validation failures, `0` source-quote rejections.
- Compiled v8 artifact exists at
  `data/compiled/model_affordances/affordances_v8.json`.
- v8 corpus shape: `98` reviewed records, `134` affordances, `181` absence
  records, `0` schema validation failures, `0` source-quote rejections.
- Compiled v9 artifact exists at
  `data/compiled/model_affordances/affordances_v9.json`.
- v9 corpus shape: `110` reviewed records, `146` affordances, `205` absence
  records, `0` schema validation failures, `0` source-quote rejections. v9 is
  still `draft_review_only` and not runtime-promoted.
- Treatment-audit v2 activation-gated calibration exists as research evidence,
  but it is not promotion-grade proof.
- PR 11 Gate 4 edge-probe harness exists on
  `feature/knowledge-substrate-pr11-gate4-edge-probes`, stacked on
  `feature/knowledge-substrate-pr10-compile-affordances-v3`.
- PR 11 dry-run status: `10` usable archived cases, `39` Lane 4 routes, `78`
  expected Arm B/C generation calls, `39` expected judge calls, `165/205`
  v3-covered candidate appearances, max packet estimate `32,935` tokens, `0`
  budget-driven omissions.
- PR 11 3-case paid calibration ran Arm B/C generation on `grant-equity-partnership-status`,
  `mother-deciding-address-year`, and `third-year-phd-student`. It stopped
  before paid judging because generation validation failed on quote-exactness
  and missing-corpus trace discipline. This was a calibration stop, not Gate 4
  proof.
- The useful PR 11 product signal is now captured in
  `research/gate4-3case-product-readout-2026-05-05.md` and
  `research/decision-pressure-surface-spec-2026-05-05.md`: Arm C shifted output
  toward source-backed operational fields, but raw Arm B/C probe comparison is
  not the right user-facing surface.
- PR 13 dry-surface work is captured in
  `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md` and
  `research/affordance-batch3a-coverage-priority-2026-05-05.md`: the existing
  12-route readout can compress into `3` product-worthy Decision Pressures in
  this dry review, and the next extraction recommendation is a targeted
  `extract_5` Batch 3a coverage patch, not broad Batch 3.
- PR 13 verification conclusion: this is product-valid as a docs/research
  checkpoint, not runtime evidence. The next uncertainty is selection
  stability: whether another reviewer, using the same packet and gates, selects
  substantially the same 1-3 pressures.
- PR 14 selection-stability review is captured in
  `research/gate4-3case-decision-pressure-selection-stability-review-2026-05-05.md`:
  a second reviewer converged `3/3` with PR13 at the pressure-cluster level.
  This is stable enough for Batch 3a planning, with a blindness caveat; it is
  not runtime, memo, Step 8, Step 6, or Lane 4 promotion evidence.
- PR 15 extraction brief is captured in
  `research/affordance-batch3a-extraction-brief-2026-05-05.md`: Batch 3a must
  extract Decision Pressure-ready operational constraints for exactly five
  models, with absence records and do-not-promote recommendations allowed.
- PR 16 Batch 3a extraction is captured in
  `research/pr16-batch3a-extraction-report-2026-05-05.md`: the five target
  models produced `5` narrow affordances and `12` absence records, compiled as
  `data/compiled/model_affordances/affordances_v4.json`. The v4 artifact is
  still `draft_review_only` and runtime-dormant.
- PR 17 v4 dry review is captured in
  `research/gate4-3case-decision-pressure-v4-dry-review-2026-05-05.md`:
  decision label `v4_improves_fields_without_changing_selection`. v4 sharpens
  dismissal, tripwire, suppression, and coverage-honesty fields for the same
  three pressure clusters; it does not justify a fourth pressure, Batch 3b,
  paid Gate 4 rerun, or runtime promotion.
- PR 18 static Observatory prototype is captured in
  `research/gate4-3case-decision-pressure-observatory-prototype-2026-05-05.md`:
  prototype verdict `observatory_trace_clearer`. The operator trace is clearer
  when it shows the same three pressures, provenance, v4 contribution,
  suppressed candidates, and the PhD competitive-dynamics coverage blank. This
  is still a static research artifact, not UI or runtime integration.
- PR 19 runtime-dormant trace contract is captured in
  `research/decision-pressure-trace-data-shape-2026-05-05.md`: decision label
  `decision_pressure_trace_contract_ready`. The PR18 prototype can be
  represented as a validated `decision_pressure_trace` object with runtime
  dormancy, source-affordance lookup against v4, provenance completeness,
  suppression references, and coverage-transparency rails.
- PR 20 producer/adapter boundary plan is captured in
  `research/decision-pressure-trace-producer-adapter-plan-2026-05-05.md`:
  decision label `producer_adapter_plan_ready`. The next step remains
  fixture-only: validate, normalize, package, or report on reviewed trace
  fixtures without selecting pressures semantically or wiring live behavior.
- PR 21 fixture-only adapter smoke test is captured in
  `research/decision-pressure-trace-adapter-smoke-test-2026-05-05.md`:
  decision label `fixture_adapter_smoke_ready`. The adapter loads an explicit
  reviewed trace fixture, validates it against `affordances_v4.json`, and can
  write a review-only report under `.tmp/` when explicitly requested. It does
  not select pressures, generate pressure text, render Observatory UI, or touch
  runtime behavior.
- PR 22 adapter-report usefulness review is captured in
  `research/decision-pressure-trace-adapter-report-usefulness-review-2026-05-05.md`:
  decision label `adapter_report_useful_as_smoke_guard`. The report is useful
  as a mechanical drift guard, not as the main product-quality review surface.
  The main product review artifact remains the trace fixture plus PR18, PR19,
  and PR21 research docs.
- PR 23 no-paid generalization readout is captured in
  `research/decision-pressure-generalization-readout-2026-05-05.md`: decision
  label `generalization_signal_positive_but_not_runtime_ready`. Five archived
  cases outside the original PR13 packet produced useful case-level Decision
  Pressures, especially when the surface turned messy advice into gates,
  thresholds, sequencing, and dismissal paths. The result is directional
  product evidence, not runtime promotion. PR23 also locks the anti-casuistry
  boundary: these five cases are evidence that the reviewer surface travels,
  not templates for deterministic case-type rules.
- External architecture reference: we studied `gbrain` as a mature agent memory
  system and captured Lolla-specific takeaways in
  `research/gbrain-architecture-learning-handover-2026-05-05.md`. The key
  conclusion is to copy discipline, not product shape: human-readable source
  truth, contract-first operations, resolver governance, retrieval hygiene,
  traceability, and maintenance are useful; ambient memory and database-first
  expansion are not current Lolla priorities.
- External decision-process reference: we studied Shane Parrish's *Clear
  Thinking* and captured Lolla-specific takeaways in
  `research/clear-thinking-lolla-learning-handover-2026-05-05.md`. The key
  conclusion is to copy decision discipline, not add a new lane: catch the
  moment where AI advice hardens into commitment, name the pressure, improve
  the user's future position, and install an operational safeguard.
- Combined external-study doctrine: use `gbrain` lessons for trustworthy
  substrate/runtime design; use *Clear Thinking* lessons for the decision-note,
  tripwire, safeguard, and process-record product surface.
- Product doctrine after the merged PR13-PR23 stack is captured in
  `research/decision-pressure-product-doctrine-2026-05-06.md`: doctrine label
  `broad_intake_disciplined_output`. Lolla is moment-first, not persona-first:
  the moment is a human or agent about to rely on AI advice. The possible
  pressure space stays broad, but surfaced pressure must clear a strict
  contract: relevant, action-changing, compact, dismissible, tripwired,
  source-backed or coverage-honest, non-duplicative, no fake precision, and no
  deterministic template.
- Current knowledge-matching audit is captured in
  `research/knowledge-matching-current-state-audit-2026-05-06.md`. It separates
  the active runtime substrate from the dormant v4 affordance corpus: the live
  lanes currently use the 222-model graph, relationship graph, compiled chunks,
  and embeddings; the 55 reviewed affordance records support dormant Decision
  Pressure review/validation and should not be described as the live matching
  engine.
- Current packet strategy is captured in
  `research/enriched-mental-model-packet-strategy-2026-05-06.md`. It is the
  anti-overengineering correction: existing lanes pull candidate mental-model
  shelves; deterministic code enriches those shelves into compact,
  source-backed cards; the next LLM/reviewer does the semantic thinking. The
  next non-runtime knowledge step should be a dormant card-packet plan or
  pressure-family coverage audit, not a deterministic pressure solver.
- Source Understanding And Reasoning Packet Audit is captured in
  `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md` and
  `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`. The audit
  verifies that the 222-model runtime graph gives breadth, v4 gives reviewed
  depth for 55 records, and the missing bridge is a dormant
  `reasoning_substrate_packet.v1` handoff object, not a deterministic Decision
  Pressure solver.
- PR25 reopened forward work after PR24, but only along the corrected
  architecture. It adds
  `research/reasoning-substrate-lane-placement-audit-2026-05-06.md`,
  `research/full-corpus-enrichment-coverage-audit-2026-05-06.md`,
  `engine/system_b/reasoning_substrate_coverage.py`, and
  `engine/system_b/reasoning_substrate_packet.py`. The target is full-corpus
  enrichment plus proper packet placement, not Decision Pressure machinery.
  Existing lanes stay intact, v4 is additive enrichment to lane-selected
  candidates, graph-only models remain eligible with honest labels, and Python
  packages reasoning material for the LLM/reviewer to judge.
- PR26 source custody backfill is captured in
  `research/reasoning-substrate-source-custody-backfill-2026-05-06.md`:
  decision label `source_custody_backfill_complete`. All `222` runtime model
  source files are now resident under `data/model_sources/` with SHA-256
  manifest entries. v4 remains `55` reviewed records; `167` runtime models
  remain graph-only after v4.
- PR27 mixed packet fixture review is captured in
  `research/reasoning-substrate-packet-fixture-review-2026-05-06.md`:
  decision label `mixed_packet_fixture_useful`. One review-only fixture proves
  that a mixed packet with `3` v4-reviewed cards, `4` source-custodied
  graph-only cards, and `1` suppressed duplicate is useful handoff material.
  The review also shows graph-only cards are thinner than v4 cards and gives a
  concrete reason for a later controlled extraction batch.
- PR28 controlled graph-only extraction is captured in
  `research/pr28-controlled-graph-only-extraction-report-2026-05-06.md`:
  decision label `controlled_graph_only_extraction_batch_ready`. Ten
  source-custodied graph-only models now have reviewed Batch 4 records,
  adding `10` affordances and `20` absence records. The compiled v5 artifact
  has `65` reviewed records, `101` affordances, and `115` absence records, and
  remains `draft_review_only` with no runtime imports.
- PR29 v5 packet depth review is captured in
  `research/reasoning-substrate-v5-packet-depth-review-2026-05-07.md`:
  decision label `v5_packet_depth_improved`. The PR27 mixed packet was
  regenerated against v5 with the same transaction context, nominations, cap,
  and suppression case. Reviewed cards increased from `3` to `7`, graph-only
  cards decreased from `4` to `0`, and packet burden remained acceptable for
  review-only LLM handoff. This is handoff-quality evidence, not final-answer
  evidence or runtime promotion.
- PR30 packet review rendering is captured in
  `research/reasoning-substrate-packet-comparison-render-2026-05-07.md`,
  `research/reasoning-substrate-packet-pr27-review-render-2026-05-07.md`, and
  `research/reasoning-substrate-packet-pr29-review-render-2026-05-07.md`:
  decision label `packet_review_rendering_ready`. The renderer makes existing
  dormant packet evidence easier for a receiver-side reviewer to inspect while
  refusing non-dormant packets and avoiding final pressure, memo copy, HTML,
  or user-facing prose.
- PR31 v5 capability audit is captured in
  `research/v5-reviewed-model-capability-audit-2026-05-07.md`: decision label
  `v5_capability_audit_complete`. The 65 reviewed records are now mapped to
  concrete capability families and the next controlled enrichment gaps are
  named.
- PR32 controlled capability-gap enrichment is captured in
  `research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md`:
  decision label `controlled_capability_gap_enrichment_ready`. Sixteen
  graph-only models from the PR31 gap list now have reviewed Batch 5 records,
  adding `16` affordances and `32` absence records. v6 has `81` reviewed
  records, `117` affordances, and `147` absence records, and remains
  `draft_review_only`.
- PR33 v6 packet usefulness review is captured in
  `research/reasoning-substrate-v6-packet-usefulness-review-2026-05-07.md`:
  decision label `v6_packet_handoff_useful`. A v5/v6 packet comparison using
  the same explicit nominations shows v6 adds useful handoff depth for
  fallback, counterparty, relative-position, delay, control, customer-job,
  lock-in, path-dependence, and cross-cultural shelves without changing
  candidate count.
- PR34 controlled communication/competition enrichment is captured in
  `research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md`:
  decision label `controlled_communication_competition_enrichment_ready`.
  Seven graph-only models from communication, feedback, strategic
  interdependence, and analogy/adaptive gaps now have reviewed Batch 6 records,
  adding `7` affordances and `14` absence records. v7 has `88` reviewed
  records, `124` affordances, and `161` absence records, and remains
  `draft_review_only`.
- PR35 v7 packet usefulness review is captured in
  `research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md`:
  decision label `v7_packet_handoff_useful`. A v6/v7 packet comparison using
  the same explicit nominations shows v7 adds useful handoff depth for
  communication, feedback, strategic interdependence, analogy, and adaptive
  reasoning shelves without changing candidate count.
- PR36 controlled trust/negotiation enrichment is captured in
  `research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md`:
  decision label `controlled_trust_negotiation_enrichment_ready`. Ten
  graph-only models from trust repair, motivation, boundaries, persuasion,
  diplomacy, and signaling gaps now have reviewed Batch 7 records, adding
  `10` affordances and `20` absence records. v8 has `98` reviewed records,
  `134` affordances, and `181` absence records, and remains
  `draft_review_only`.
- PR37 v8 packet usefulness review is captured in
  `research/reasoning-substrate-v8-packet-usefulness-review-2026-05-07.md`:
  decision label `v8_packet_handoff_useful`. A v7/v8 packet comparison using
  the same explicit nominations shows v8 adds useful handoff depth for trust
  repair, emotional landing, hidden motivation, boundaries, candor,
  non-malice diagnosis, reciprocity, persuasion, diplomacy, and signaling
  shelves without changing candidate count.
- PR38 after-v8 graph-only priority audit is captured in
  `research/v8-graph-only-priority-audit-2026-05-07.md`: decision label
  `v8_graph_only_priority_audit_complete`. It does not extract records. It
  selects execution / implementation / follow-through discipline as the best
  next controlled enrichment family, with a 12-model PR39 target set, because
  that family best tests the gap between plausible advice and inspectable
  execution.
- PR39 controlled execution/follow-through enrichment is captured in
  `research/pr39-controlled-execution-followthrough-enrichment-report-2026-05-07.md`:
  decision label `controlled_execution_followthrough_enrichment_ready`. Twelve
  graph-only execution/follow-through models now have reviewed Batch 8 records,
  adding `12` affordances and `24` absence records. v9 has `110` reviewed
  records, `146` affordances, and `205` absence records, and remains
  `draft_review_only`.
- PR40 v9 execution packet usefulness review is captured in
  `research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md`:
  decision label `v9_execution_packet_handoff_useful`. A v8/v9 packet
  comparison using the same explicit nominations shows v9 adds useful handoff
  depth for baselines, bottlenecks, audit trails, debugging, feedback loops,
  input/output goals, bounded iteration, validated learning, handoff
  procedures, delivery loops, goal-setting, and habit design without changing
  candidate count.
- PR41 after-v9 graph-only priority audit is captured in
  `research/v9-graph-only-priority-audit-2026-05-07.md`: decision label
  `v9_graph_only_priority_audit_complete`. It does not extract records. It
  selects risk controls / reversibility / failure containment as the best next
  controlled enrichment family, with a 12-model PR42 target set, because that
  family best tests whether plausible and executable advice is contained,
  reversible, monitorable, escalatable, and stoppable.
- The next-session handover is captured in
  `research/reasoning-substrate-next-session-handover-2026-05-06.md`. Future
  sessions should read it first. The active posture is
  `v9_graph_only_priority_audit_complete`: PR41 completed the after-v9
  graph-only priority audit. If opened, PR42 should be one controlled
  risk/reversibility/failure-containment extraction batch for the 12 named
  targets, and PR43 must prove packet usefulness before any further extraction.

Current posture after PR 23, PR24 review, PR25, PR26, PR27, PR28, PR29, PR30,
PR31, PR32, PR33, PR34, PR35, PR36, PR37, PR38, PR39, PR40, and PR41:

1. PR24's `stop_and_consolidate` posture stopped the wrong Decision Pressure
   machinery. PR25 explicitly reopened forward work only for enrichment
   placement: lane-selected shelves become compact source-aware cards for the
   next LLM/reviewer.
2. Use the product doctrine
   `research/decision-pressure-product-doctrine-2026-05-06.md` as the north
   star: broad intake, disciplined output.
3. Do not run more paid Gate 4 calibration by default.
4. Treat the PR13 dry surface and PR14 stability review as product-shaping
   evidence, not formal Gate 4 proof.
5. Treat Batch 3a and v4 as an extraction patch plus dry product-delta review;
   they do not promote Decision Pressure or v4 affordances into runtime.
6. Treat the PR18 Observatory prototype as evidence that the operator trace is
   clearer, not as implementation permission.
7. Treat the PR19 `decision_pressure_trace` contract, PR20 producer/adapter
   plan, PR21 adapter smoke test, and PR22 usefulness review as dormant review
   infrastructure, not as live Observatory, memo, Step 8, Step 6, Lane 4, or
   `/lolla` behavior.
8. Treat PR23 as directional evidence that Decision Pressure generalizes beyond
   the original 3-case packet, but not as live product evidence. A multi-case
   trace review is allowed only if product review names the concrete
   uncertainty it would answer.
9. Treat Decision Pressure as a synthesis object that feeds existing Step 6,
   Step 8 Pressure Check, memo, or Observatory surfaces. It is not a new lane.
10. Treat C-only OOD as one strong value mode, not the only value mode. The
   accepted product modes are `new_edge`, `grounded_double_down`,
   `confirmation`, and `coverage_transparency`.
11. Do not start broad Batch 3, Batch 3b, live Lane 4 integration, or chat/memo
   promotion from PR23 or PR25.
12. Do not turn PR23 case examples into deterministic rules. Python may enforce
    shape, caps, provenance, source-reference validity, runtime dormancy,
    coverage gaps, blocked surfaces, and drift counts. Python must not choose
    pressure quality, infer pressure from case type or route label, merge
    semantic equivalents, rank tone/actionability, smooth missing coverage, or
    generate user-facing pressure prose.
13. Do not treat v4's `55` reviewed records as live runtime coverage. Future
    expansion should be pulled by pressure-family gaps and product evidence,
    not by a desire to make the corpus count look even.
14. Do not build a deterministic Decision Pressure solver. If work resumes,
    prefer the simpler packet strategy: lanes nominate candidate shelves,
    deterministic code enriches the cards with v4/provenance/coverage, and the
    LLM/reviewer selects and words any final pressure.
15. Treat `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`
    and `research/reasoning-substrate-packet-v1-spec-2026-05-06.md` as the
    current non-runtime packet handoff baseline: audit what the 222-model graph
    already knows, what v4 adds for 55 reviewed records, and what a dormant
    `reasoning_substrate_packet.v1` should contain.
16. Treat PR26 source custody as prerequisite infrastructure, not extraction
    quality. All 222 source files are now hash-custodied, but only 55 have v4
    reviewed affordance depth.
17. Treat `research/reasoning-substrate-next-session-handover-2026-05-06.md`
    as the first file for future sessions. Do not infer permission for runtime
    packet production, prompt changes, lane rewrites, broad extraction, or
    user-facing surfaces from PR28; the current state is a controlled reviewed
    extraction batch plus draft v5, not product promotion.
18. Treat PR27 as evidence that controlled extraction has a reason, not as
    permission for broad Batch 3b, live route-trace packet production, or
    user-facing Decision Pressure output.
19. Treat PR28 as a controlled extraction quality loop, not Batch 3b. It proves
    ten source-custodied graph-only models can gain compact reviewed depth with
    absence records, but it does not promote v5 into runtime or justify broad
    extraction by count momentum.
20. PR29 completed the packet regeneration/comparison against PR27 using v5,
    and found the added depth improves the LLM handoff while keeping burden
    acceptable.
21. Treat PR29 as handoff-depth evidence, not final-answer evidence. It shows
    the v5 packet is better reasoning material for the same nominations, but it
    does not authorize deterministic pressure selection, runtime promotion,
    broad extraction, prompt changes, or live lane adapters.
22. PR30 made receiver-side packet review ergonomic without calling models or
    creating a product surface. Later slices used packet usefulness and
    capability gaps to justify controlled enrichment, not count completion.
23. Treat PR30 as reviewer ergonomics only. It does not create a product
    surface, runtime adapter, package function, live lane adapter, or semantic
    selector.
24. Treat PR31 as a capability audit, not extraction. It answered what the 65
    reviewed records could already support and named the gap list that drove
    PR32.
25. Treat PR31's gap list as historical justification for PR32, not as an open
    invitation to keep extracting by count momentum.
26. Treat PR32 as controlled capability-gap enrichment, not corpus completion.
    It adds v6 reviewed depth for 16 named graph-only models and keeps v6
    draft/review-only. PR33 later completed the packet usefulness review
    against v6.
27. Treat PR33 as handoff-quality evidence, not runtime permission. It shows
    the same explicit nomination set becomes better packet material under v6
    without increasing candidate count or selecting final pressure.
28. Treat PR34 as controlled communication/competition enrichment, not corpus
    completion or runtime v7 promotion. It adds seven Batch 6 records, keeps
    v7 draft/review-only, and preserves absence records. PR35 later completed
    the packet usefulness review against v7.
29. Treat PR35 as handoff-quality evidence, not runtime permission. It shows
    the same communication/competition nomination set becomes better packet
    material under v7 without increasing candidate count or selecting final
    pressure.
30. Treat PR36 as controlled trust/negotiation enrichment, not corpus
    completion or runtime v8 promotion. It adds ten Batch 7 records, keeps v8
    draft/review-only, and preserves absence records. PR37 later completed the
    packet usefulness review against v8.
31. Treat PR37 as handoff-quality evidence, not runtime permission. It shows
    the same trust/negotiation nomination set becomes better packet material
    under v8 without increasing candidate count or selecting final pressure.

---

## 1. Thesis

The next serious improvement to Lolla should not be another user-facing lane.

The next serious improvement should be a better compiled understanding of the canonical mental-model source files, so the existing lanes can use the 216/222/223-model substrate with more precision, provenance, and treatment discipline.

The system already has the right architectural doctrine:

> LLMs at the edges. Determinism in the middle.

But the deterministic middle can only be as intelligent as the compiled substrate it receives. The canonical model files are richer than the current runtime fields expose. They contain playbooks, misuse warnings, anti-patterns, structured tensions, premortem questions, mitigation questions, and operational output shapes. We should extract that richness into reviewed, provenance-backed artifacts that make the existing lanes sharper.

The goal is not "more content."
The goal is **more grip**:

- better model activation judgment
- better "why this model, not that one" traces
- better anti-echo debugging
- better Lane 4 gap questions
- better post-run treatment audits
- eventually, only if proven, better user-facing Pressure Checks and memos

The monetizable edge is now stated more sharply:

> Every decision-grade run should either surface source-backed operational
> pressure outside the ordinary prompting spectrum, or give a traceable reason
> why no such pressure cleared the bar.

That does not mean every run must invent an insight. It means Lolla must not
pad. A thin, already-well-treated, or non-strategic case should be allowed to
produce little. The premium promise is not "more analysis"; it is an honest
audit layer that can show what confident AI advice failed to check.

The commercial category should be:

> A reasoning audit that shows what confident AI advice failed to check.

Not:

> Better answers through deeper reasoning.

The first category is differentiated. The second is crowded and invites direct
comparison with frontier models.

---

## 2. Non-Negotiable Doctrine

This is the central rule for all future work in this area:

> Semantic extraction must be LLM-driven reading of source truth with provenance. Python may scaffold, normalize, validate, dedupe, hash, and serialize. Python must not infer semantic fields from keyword heuristics.

This is not new doctrine. It already exists in the older System B repo:

- `/Users/marcin/Desktop/Apps/Lolla-system-b/rfcs/0004-compiled-subpattern-routing-and-pressure-bundles.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/curation/README.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/tasks/tasks-curation-completeness-sweep.md`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/PRODUCT_VISION.md`

The same rule must govern the next wave.

### 2.1 What Python May Do

Python may:

- enumerate source files
- build per-model extraction packets
- include source markdown, existing curation JSON, and current runtime compiled fields
- call an LLM with a strict schema
- validate JSON shape
- check exact `source_quote` substrings
- count field coverage
- detect empty/generic boilerplate
- deduplicate repeated strings
- assign stable IDs
- write reports
- compile reviewed artifacts into runtime JSON
- render Observatory panels
- run comparison/evaluation harnesses

### 2.2 What Python Must Not Do

Python must not:

- infer "requires evidence" fields from section headings alone
- convert lines containing "Danger when" into final semantic fields without LLM judgment
- map models by keyword overlap
- decide that two models are allies because they share terms
- decide that a model is "used well" by substring matching alone
- generate affordance fields from regexes
- bulk-fill missing fields with generic defaults
- silently promote low-confidence fields into runtime packets

Mechanical extraction may produce **candidate packets** only. Semantic fields require LLM cognition and provenance.

### 2.3 The "Present But Generic" Rule

Field presence is not completion.

A field like:

> "Use this model to think more carefully about the problem."

is worse than blank. It creates false substrate confidence.

Every semantic field should pass a usefulness test:

> Would this field change what a downstream lane asks, routes, excludes, challenges, or audits?

If not, it should be dropped, weakened, or marked as an open question.

### 2.4 The "No Completeness Theater" Rule

The knowledge base does not need to contain everything.

If a source file does not support an affordance, relation, misuse guard, diagnostic question, or treatment requirement, the correct output is absence, not invention.

This matters because the goal is not to make every model satisfy every schema-shaped slot. The goal is to preserve the actual state of the curated knowledge base and make that state more inspectable. Missing knowledge is a real substrate fact. It should be reported, not patched over with plausible language.

Good extraction may produce:

- zero affordances for a model
- one strong affordance instead of five weak ones
- a `not_supported_by_source` note
- a `source_too_thin` note
- an open question for future source expansion
- a recommendation to keep the model out of a runtime feature until the source is richer

Bad extraction produces:

- uniform-looking records for every model
- generic affordances that make the corpus feel complete
- inferred fields written to satisfy downstream runtime desires
- "reasonable" model requirements that are not source-backed
- watery paraphrases that make strong source material less precise

The system should adapt to the knowledge base. The knowledge base should not be stretched to make the system look complete.

### 2.5 Affordance Records Are Knowledge Documents, Not Matching Rules

The affordance layer contains activation conditions (`use_when`, `do_not_use_when`, `case_evidence_needed`), treatment requirements, diagnostic questions, and misuse guards. These fields exist to give the LLM richer, source-backed reasoning material. They are not instructions for the deterministic system.

The deterministic layer's job with affordance records is **retrieval and delivery**:

1. A model is routed (by the existing routing engine — tendency lookup, graph traversal, embedding recall).
2. The deterministic layer looks up the affordance record for that model by ID.
3. The affordance record is included in the packet delivered to the LLM consumer.

The deterministic layer does not:

- evaluate whether `use_when` conditions are met in the current case
- pre-filter models based on `do_not_use_when` conditions
- match `case_evidence_needed` against case content
- validate `treatment_requirements` against output text by pattern matching

Attempting any of the above makes the deterministic layer casuistic, brittle, and over-engineered. Evaluating "people, teams, markets, or components are continuously adapting to each other" against a conversation requires reading the conversation and understanding its structure. That is a semantic judgment. Semantic judgments belong to Claude Code (synthesis) and OpenRouter (calibrated boundary calls), not to Python.

The improvement from building richer affordance records is entirely in **what is delivered to the LLM**, not in **what the deterministic layer processes**. Claude Code and OpenRouter are smart enough to use structured, source-backed material without Python pre-interpreting it. The LLM does not need mediation — it needs good material.

The three failure modes to avoid in the deterministic middle when working with affordances:

- **Brittle**: new phrasing in an affordance or a case breaks the match condition
- **Bloated**: case exceptions accumulate to handle novel situations the match condition did not anticipate
- **Casuistic**: the middle becomes a record of past activation decisions rather than a structural routing mechanism

The discipline test: if a new implementation of the deterministic layer can pass all tests without reading the semantic content of an affordance's `use_when` field, it is on the right side of the line. If it needs to parse or match that text, it is doing the LLM's job badly.

---

## 3. What We Already Have

The old System B repo already contains the methodology we need to preserve.

### 3.1 Source Authority Order

From `/Users/marcin/Desktop/Apps/Lolla-system-b/curation/README.md`:

1. raw markdown in `MM_CANONICAL_216/`
2. reviewed curation in `curation/`
3. compiled artifacts in `build/`
4. runtime interpretation

If a curated field disagrees materially with the raw markdown, the markdown wins semantically. The disagreement should be visible in notes, not hidden.

### 3.2 Existing Wave Structure

The current knowledge layer already has several waves:

- **Wave 1:** activation semantics: `select_when`, `danger_when`, input/output type, reasoning types
- **Wave 2:** intervention semantics: failure modes, heuristics, premortem questions
- **Wave 3:** relation semantics: allies, antagonists, structured tensions, affinity, activation conditions
- **Wave 4:** higher-order composition pilot, deliberately conservative
- **Wave 5:** reframing semantics for Lane 3
- **Structural coverage substrate:** dimension-to-model routing for Lane 4

The counts vary across repo generations: the directory name says `MM_CANONICAL_216`, older docs mention 217 or 223, and current `lolla-skill` docs mention 222 compiled models. Future code must count from the active manifest or compiled artifact, not hard-code a number.

### 3.3 Current Runtime Shape

The current `lolla-skill` pipeline has:

- **Lane 1:** structural pressure from detected tendency failures
- **Lane 2:** model companion, using deterministic recall + LLM verification + chunk selection
- **Lane 3:** frame pressure from embedded assumptions and suppressed alternatives
- **Lane 4:** structural coverage, proactive gap discovery from problem shape
- **Observatory:** debug/trace surface
- **Memo/chat contracts:** user-facing synthesis after the audit

The important lesson from PR #74:

> A new lens can be technically correct and still not add user value if the existing Pressure Check already handles the issue.

Therefore new substrate work should be Observatory-first and baseline-compared before it influences chat or memo.

### 3.4 Current Affordance Corpus State

As of 2026-05-05, the affordance layer is no longer hypothetical.

| Slice | Models | Affordances | Absence Records | Status |
| --- | ---: | ---: | ---: | --- |
| Pilot | 10 | 22 | 2 | done |
| Batch 1 | 20 | 30 | 30 | done |
| Batch 2 | 20 | 34 | 51 | done |
| **v3 total** | **50** | **86** | **83** | draft review only |

This shape is intentionally uneven. The rising absence-record density is a good
sign, not a problem: the extraction contract is refusing generic field
promotion rather than vacuuming source text into schema-shaped slots.

The current corpus is strong enough to test. It is not yet proven enough to
promote into live `/lolla` behavior.

### 3.5 Current Product Guardrail

Do not add lanes now.

The current product already has enough surfaces:

- structural pressure
- model companion
- frame pressure
- structural coverage
- updated position
- pressure check
- memo
- Observatory

The next phase is not "more Lolla." It is making Lolla harder to fool:

- fewer claims
- better evidence
- sharper pressure
- clearer treatment
- stronger proof that the pressure beat generic prompting

The affordance layer should enrich the existing system by making current lanes
and synthesis surfaces more disciplined, not by creating a new card family.

---

## 4. The Missing Layer: Model Affordances

The next knowledge artifact should be a **model affordance layer**.

An affordance is not a description of a mental model. It is an operational contract for what the model demands when used.

Example:

If `theory-of-constraints` applies, good reasoning usually needs to identify:

- the binding constraint
- how the constraint is measured
- why visible pain is not necessarily the bottleneck
- what scarce resource is being consumed by non-bottleneck work
- what becomes the next constraint if this one moves

If `second-order-thinking` applies, good reasoning usually needs to identify:

- the dependency chain
- the first threshold where local gain flips into downstream harm
- the adaptation the intervention teaches other actors
- the recovery path that disappears if sequencing is wrong
- which downstream effect is evidenced versus speculative

Those requirements already exist in the canonical markdown. We need them compiled as first-class, provenance-backed runtime knowledge.

### 4.1 Proposed Artifact Shape

Future artifact, probably not immediately runtime-promoted:

```json
{
  "model_id": "theory-of-constraints",
  "source_file": "Theory_Of_Constraints_rag.md",
  "affordances": [
    {
      "affordance_id": "constraint-proof-before-optimization",
      "name": "Constraint proof before optimization",
      "use_when": "The plan optimizes a visible pain point without proving it is the binding limit.",
      "requires_evidence": [
        "named bottleneck",
        "metric that proves the bottleneck",
        "dependency controlled by the bottleneck",
        "non-bottleneck work that should stop or subordinate"
      ],
      "good_output_shape": [
        "name the constraint",
        "state what is not the constraint",
        "name the scarce capacity being protected",
        "define the retest signal"
      ],
      "misuse_guards": [
        "Do not optimize the loudest step if it is not the throughput cap.",
        "Do not keep solving the old bottleneck after the constraint moves."
      ],
      "diagnostic_questions": [
        "What measured limit would still cap throughput if every local improvement succeeded next week?",
        "If this bottleneck moved, what would become the next cap within two weeks?"
      ],
      "source_quote": "Before committing: what is the single measured limit that would still cap throughput if every local improvement in this plan succeeded next week?",
      "extraction_type": "normalized",
      "confidence": "high",
      "notes": "Source frames this as a mitigation against visible-work theater."
    }
  ]
}
```

This is intentionally richer than the current `failure_modes` / `heuristics` split. It tells the deterministic middle what successful use of the model should look like.

### 4.2 What Counts As A Good Affordance

A good affordance:

- is operational, not explanatory
- names what evidence is needed
- names what a good answer should do differently
- includes misuse guards
- can be checked against a final answer or pressure-check section
- has source provenance
- is specific enough to reject generic treatment

A weak affordance:

- restates the model definition
- says "consider X" without saying what X requires
- could apply to almost every model
- has no source-backed diagnostic question
- cannot change routing, gap generation, or treatment audit behavior

---

## 5. Big-Picture Target Architecture

The long-term target is not one big feature. It is a staged improvement to the compiled substrate and the Observatory/debug loop.

### 5.1 Layer A - Affordance Extraction

LLM-read the canonical source files and existing curation files to produce `model_affordances`.

This is source-substrate work. It should not change user output.

### 5.2 Layer B - Affordance Validation

Validate the extracted layer:

- schema shape
- exact source quotes
- coverage
- confidence distribution
- generic/boilerplate detector
- sampling review
- model count reconciliation
- source/curation disagreement notes

This is quality-control work. It should not change user output.

### 5.3 Layer C - Route Explanation / Why-Not Trace

Expose why the deterministic middle selected or rejected models:

- selected by direct tendency binding
- selected by relation edge
- selected by frame pattern
- selected by structural gap route
- excluded by anti-echo
- lost by fan correction
- lost by activation tiebreaker
- dropped by budget
- suppressed as duplicate of existing Pressure Check

This is Observatory work. It should not change user output.

### 5.4 Layer D - Model Treatment Audit

After a run, compare selected models against their affordances:

- Did the final answer perform the required move?
- Did it name the evidence the model requires?
- Did it misuse the model?
- Did it silently ignore a high-value selected affordance?
- Did the Pressure Check already cover it?

This is an evaluation layer. It should not change user output at first.

### 5.5 Layer E - Lane 4 Affordance-Guided Gap Questions

Only after A-D prove useful, use affordances to sharpen Lane 4 gap questions.

Example:

Instead of generic stakeholder questions:

> Who are the stakeholders?

ask model-shaped, case-specific questions:

> Who can delay, veto, or quietly make this plan non-executable even if they agree in the meeting?

This may eventually affect user output, but only behind a flag and only after baseline comparison.

### 5.6 Layer F - Selective User-Facing Promotion

Only if evaluation shows non-duplicative value:

- Pressure Check may receive one affordance-derived correction.
- Memo may compress one affordance-derived decision change.
- Chat must not show internal model/affordance machinery.

This is the last step, not the first.

---

## 6. Proposed PR Sequence

Each PR should be independently reviewable and safe to merge. The early PRs should be dormant or Observatory-only.

### 6.0 Implementation Status - 2026-05-05

This section preserves the original roadmap sequence but marks the current
state. Future coders should continue from the status below, not from the
original proposal language.

| Roadmap item | Current status | Notes |
| --- | --- | --- |
| PR 1 - Affordance schema and extraction contract | done | Schema, contract, fixtures, and validation tests exist. |
| PR 2 - Ten-model LLM-curated pilot | done | 10 pilot records extracted and validated. |
| PR 3 - Compiler and quality report | done through v4 | Compiler produces v1/v2/v3/v4 artifacts and quality reports. |
| Batch 1 / PR 7 style expansion | done | 20 additional model records. |
| Batch 2 / PR 9 style expansion | done | 20 Lane-4-frequency model records. |
| Treatment audit prototype | calibration evidence exists | Directionally good activation-gated v2 evidence, not promotion-grade. |
| Gate 4 edge-probe experiment / PR 11 | built, 3-case paid calibration stopped before judging | Showed that v3 affordances shift outputs toward operational fields, but raw Arm B/C probe comparison is not the right product surface. |
| Decision Pressure surface / PR 12-17 | done through v4 dry review | Defined compact safeguards, selection stability, targeted Batch 3a extraction, and v4 product-delta review. |
| Static Observatory prototype / PR 18 | done | Prototype an operator-facing trace for the same three pressures with provenance, suppression, and coverage transparency. |
| Decision Pressure trace contract / PR 19 | done | Define and validate a runtime-dormant `decision_pressure_trace` object for the PR18 prototype. |
| Trace producer/adapter plan / PR 20 | done | Define the boundary for validating, normalizing, packaging, or reporting on reviewed trace fixtures without live behavior. |
| Fixture-only trace adapter smoke test / PR 21 | done | Exercise the PR19 trace contract mechanically and write only review-only reports when explicitly requested. |
| Adapter report usefulness review / PR 22 | done | Record that the adapter report is useful as a smoke alarm, not as the main product-quality review surface. |
| Decision Pressure generalization readout / PR 23 | done | Record no-paid directional generalization evidence and lock the anti-casuistry boundary. |
| Source Understanding And Reasoning Packet Audit | done as docs/research audit/spec | Audits all-222 runtime graph breadth, v4's 55-record depth, and defines a dormant `reasoning_substrate_packet.v1` shape that enriches lane-selected candidates without selecting final pressure. |
| Reasoning substrate enrichment placement / PR25 | done as dormant audit/module slice | Maps existing lane outputs to packet placement, audits full-corpus enrichment coverage, and adds a review-only explicit-nomination packet producer. |
| Source custody backfill / PR26 | done as deterministic custody slice | Copies all 222 runtime source files into `data/model_sources/` and updates SHA-256 manifest. No extraction. |
| Mixed packet fixture review / PR27 | done as review-only fixture slice | Generates and reviews one mixed `reasoning_substrate_packet.v1` fixture. Shows v4 cards are richer, source-custodied graph-only cards are useful but thin, and extraction now has a concrete target. |
| Controlled graph-only extraction / PR28 | done as controlled reviewed extraction slice | Adds ten Batch 4 records for graph-only models, compiles draft/review-only v5, and preserves absences. No runtime promotion. |
| V5 packet handoff-depth review / PR29 | done as review-only fixture comparison | Regenerates the PR27 mixed packet against v5 and finds useful added depth for the four formerly graph-only cards. No extraction or runtime promotion. |
| Packet receiver-review rendering / PR30 | done as reviewer-only render slice | Renders PR27, PR29, and their comparison as compact Markdown handoffs. No runtime imports, UI, memo, HTML, final pressure, or user-facing prose. |
| V5 reviewed-model capability audit / PR31 | done as docs/research audit | Maps what the 65 reviewed records can tell us, what they cannot tell us, and which capability gaps drove PR32. |
| Controlled capability-gap enrichment / PR32 | done as controlled reviewed extraction slice | Adds sixteen Batch 5 records from the PR31 capability gaps, compiles draft/review-only v6, and preserves absences. No runtime promotion. |
| V6 packet usefulness review / PR33 | done as review-only fixture/render comparison | Uses the same explicit nominations against v5 and v6. Finds v6 reviewed cards improve handoff material without increasing candidate count or selecting final pressure. |
| Controlled communication/competition enrichment / PR34 | done as controlled reviewed extraction slice | Adds seven Batch 6 records for communication, feedback, strategic interdependence, and analogy/adaptive gaps, compiles draft/review-only v7, and preserves absences. No runtime promotion. |
| V7 packet usefulness review / PR35 | done as review-only fixture/render comparison | Uses the same communication/competition nominations against v6 and v7. Finds v7 reviewed cards improve handoff material without increasing candidate count or selecting final pressure. |
| Controlled trust/negotiation enrichment / PR36 | done as controlled reviewed extraction slice | Adds ten Batch 7 records for trust repair, motivation, boundaries, persuasion, diplomacy, and signaling gaps, compiles draft/review-only v8, and preserves absences. No runtime promotion. |
| V8 packet usefulness review / PR37 | done as review-only fixture/render comparison | Uses the same trust/negotiation nominations against v7 and v8. Finds v8 reviewed cards improve handoff material without increasing candidate count or selecting final pressure. |
| V8 graph-only priority audit / PR38 | done as docs/research audit | Reviews the remaining 124 graph-only models after v8 and recommends execution / implementation / follow-through discipline as the next controlled enrichment family. No extraction or runtime promotion. |
| Controlled execution/follow-through enrichment / PR39 | done as controlled reviewed extraction slice | Adds twelve Batch 8 records for execution, auditability, baselines, bottlenecks, debugging, feedback, goals, habits, iteration, and validated learning, compiles draft/review-only v9, and preserves absences. No runtime promotion. |
| V9 execution packet usefulness review / PR40 | done as review-only fixture/render comparison | Uses the same execution/follow-through nominations against v8 and v9. Finds v9 reviewed/weak-support cards improve handoff material without increasing candidate count or selecting final pressure. |
| V9 graph-only priority audit / PR41 | done as docs/research audit | Reviews the remaining 112 graph-only models after v9 and recommends risk controls / reversibility / failure containment as the next controlled enrichment family. No extraction or runtime promotion. |
| Runtime Lane 4 affordance integration | not started | Not authorized by PR23. Must wait for an explicit product-promotion decision. |
| Selective chat/memo promotion | not started | Last step, and may never be needed. |

Current boundary rule:

> PR41 completed the after-v9 graph-only priority audit. v9 is still
> draft/review-only. If opened, PR42 should be one controlled
> risk/reversibility/failure-containment enrichment batch for the 12 named
> targets, followed by PR43 packet usefulness review before any further
> extraction.

### PR 1 - Affordance Schema And Extraction Contract

**Status 2026-05-05:** done.

**Goal:** Define what an affordance is and how it must be extracted.

**Files likely touched:**

- `references/model-affordance-extraction.md`
- `references/output-field-guide.md`
- `tests/test_model_affordance_schema.py`
- possibly `data/schemas/model_affordance.schema.json`
- possibly `scripts/spikes/compile_model_affordance_packets.py`

**What to build:**

- JSON schema for model affordance records
- extraction contract explaining:
  - LLM reads full source markdown
  - existing Wave 1-3 curation is context, not authority over source
  - every semantic field needs `source_quote`, `extraction_type`, `confidence`
  - no keyword-derived fields
  - generic fields are failures
- sample empty manifest format
- validation tests for schema acceptance/rejection

**What not to build:**

- no full extraction
- no runtime wire
- no Observatory panel yet
- no chat/memo changes

**Exit criteria:**

- schema rejects generic/empty records where possible
- docs explicitly forbid mechanical extraction
- extraction contract is clear enough for a fresh LLM session to follow without this conversation

### PR 2 - Ten-Model LLM-Curated Pilot

**Status 2026-05-05:** done.

**Goal:** Test whether the affordance schema can produce useful, nuanced records from real canonical source files.

**Pilot models:**

- `theory-of-constraints`
- `second-order-thinking`
- `power-dynamics`
- `base-rates`
- `optionality`
- `premortem`
- `inversion`
- `problem-framing-and-reframing`
- `confidence-calibration`
- `systems-thinking`

**Why these models:**

They are common, broad enough to stress genericity risk, and important enough that better treatment could improve real audits.

**Extraction method:**

For each model:

1. Read the full canonical markdown from `MM_CANONICAL_216/`.
2. Read the existing Wave 1 file from `curation/{model_id}.json`.
3. Read the existing Wave 2 file from `curation/intervention_semantics/{model_id}.json`.
4. Read the existing Wave 3 file from `curation/relation_semantics/{model_id}.json`.
5. Produce affordances with provenance.
6. Mark weak or unresolved fields instead of filling them.
7. Write a per-model review note explaining what was preserved, normalized, dropped, or left ambiguous.

**Files likely touched:**

- `data/model_affordances/pilot/*.json`
- `data/model_affordances/pilot_manifest.json`
- `research/model-affordance-pilot-review-2026-05-xx.md`
- tests for schema + source quote validation

**What not to build:**

- no automated semantic extraction from section headings
- no runtime use
- no user surface

**Exit criteria:**

- all pilot records validate
- every semantic claim has source provenance
- at least 7/10 records contain affordances that are more operational than existing `failure_modes` / `heuristics`
- any model with thin source support is allowed to return fewer or zero affordances, with an explicit reason
- reviewer can name at least 3 cases where the affordance layer would help audit model treatment
- reviewer can also name what should be dropped or rewritten

### PR 3 - Affordance Compiler And Quality Report

**Status 2026-05-05:** done through v3 compiled artifact.

**Goal:** Make the pilot compile into a stable artifact and produce a quality report.

**What to build:**

- compiler that reads reviewed affordance JSON
- exact substring validation for `source_quote`
- stable affordance IDs
- coverage report:
  - models covered
  - affordances per model
  - explicit vs normalized extraction rate
  - weak-confidence count
  - missing provenance count
  - genericity warnings
- generated compiled artifact under `build/` or `data/compiled/`, depending on current repo convention

**What Python may do here:**

Validation and reporting only.

**What Python must not do:**

No semantic filling. If a model lacks an affordance, the compiler reports the gap. It does not create one.

**Exit criteria:**

- deterministic compile
- quality report is readable
- CI tests cover bad records
- no runtime behavior changes

### PR 4 - Observatory Route Graph / Why-Not Trace

**Status 2026-05-05:** partially satisfied by existing audit panels and PR 11
experiment artifacts; full route graph / why-not product surface remains open.

**Goal:** Make current routing more inspectable before changing routing.

This PR can use existing runtime data first. It does not need affordances to be complete.

**What to expose:**

- selected model IDs by lane
- route source:
  - tendency binding
  - companion detection
  - relation expansion
  - frame routing
  - structural gap routing
- anti-echo exclusions
- relation neighbors considered
- fan-correction / activation-tiebreaker trace where available
- models dropped by budget
- close alternatives

**Why this matters:**

Before we make the graph smarter, we need to see where it is already making good or bad choices.

**UI shape:**

Observatory-only. Think "perspectives," not one giant graph:

- Lane 1 Route
- Lane 2 Route
- Lane 3 Route
- Lane 4 Route
- Anti-Echo
- Why-Not

**Exit criteria:**

- no user-facing chat/memo change
- at least one archived run shows a useful why-not explanation
- route graph helps diagnose at least one anti-echo or budget decision

### PR 5 - Model Treatment Audit Prototype

**Status 2026-05-05:** prototype and v2 activation-gated calibration evidence
exist. Evidence is directionally good but not promotion-grade.

**Goal:** Compare selected models against affordances after a run.

This asks:

> If the system selected this model, did the final answer actually perform the model's required move?

**Example checks:**

For `theory-of-constraints`:

- did the answer name the binding constraint?
- did it name how the constraint is measured?
- did it distinguish visible pain from actual cap?
- did it specify what to stop or subordinate?

For `second-order-thinking`:

- did the answer name the downstream mechanism?
- did it avoid speculative chains?
- did it identify a threshold or disappearing recovery path?

**Important:** The audit should not decide this mechanically. The deterministic layer can assemble the affordance packet. A narrow LLM boundary call can judge whether the final answer treated the affordance, with evidence quotes and confidence.

**Output:**

Observatory-only `model_treatment_audit`.

**Exit criteria:**

- run on archived cases
- compare against existing Pressure Check baseline
- at least 2 cases show non-duplicative diagnostic value
- no chat/memo promotion yet

### PR 6 - Affordance-Guided Lane 4 Gap Question Experiment

**Status 2026-05-05:** reframed as Gate 4 edge-probe experiment. Built as
offline PR 11 harness; 3-case paid calibration ran generation and stopped
before judging when validation caught quote-exactness and missing-corpus trace
failures. The run produced product signal but not formal promotion evidence.

**Goal:** Test whether affordances improve Lane 4 questions or edge probes.

Lane 4 currently routes uncovered dimensions to candidate models. The first
experiment is not live gap-question augmentation. It is an offline three-arm
Gate 4 edge-probe experiment:

- **Arm A:** existing Lane 4 baseline questions from archived runs
- **Arm B:** strong generic edge-seeking prompt with routed model names only
- **Arm C:** same prompt plus retrieved affordance records from `affordances_v3.json`

The original key question was not "does C write better questions?" It was:

> Did C surface an operational edge that a strong case-prompted LLM using only
> routed model names would probably not reach?

That is recorded through the judge field `out_of_distribution`. `constructive_edge`
is diagnostic only.

The 3-case product readout softened this into a more product-real Gate 4
question:

> Does the substrate produce compact, source-backed decision safeguards that
> improve the user's decision position without bloat or fake confidence?

C-only OOD remains the cleanest value mode, but it is not the only value mode.
`grounded_double_down`, `confirmation`, and `coverage_transparency` can also be
product-worthy when they are concise, actionable, and dismissible.

The eventual runtime experiment may pass selected model affordances into the
gap-question generation step, so questions become more operational. That should
only happen after Gate 4 evidence supports it.

**Example:**

For `stakeholder-alignment` routed to `power-dynamics`, ask about veto, delay, walk-away, and commitment leverage rather than generic stakeholders.

For `feedback-system-dynamics` routed to `second-order-thinking`, ask about delayed reactions, adaptation taught, and recovery paths.

**Flag:**

Must be behind a runtime flag.

**Evaluation:**

Compare baseline Lane 4 questions vs generic edge prompts vs affordance-guided
edge prompts on archived runs.

Measure:

- C-only out-of-distribution contribution
- grounded double-down contribution
- useful confirmation
- coverage transparency
- high-value field sources (`do_not_use_when`, `case_evidence_needed`,
  `treatment_requirement`, `misuse_guard`)
- specificity
- answerability by user
- non-duplication with existing Pressure Check
- whether questions change the decision inquiry
- whether they become too long or too clever

**Exit criteria:**

- do not promote raw probe lists
- promote only after the Decision Pressure surface can compress raw probes into
  1-3 total source-backed safeguards for a normal run, with `dismiss_if`,
  `tripwire_or_next_action`, and `coverage_status`
- treat C-only OOD contribution as strongest evidence, not the only evidence
- treat `both` as interpretive/inconclusive evidence, not clean proof that
  enrichment beat a strong generic prompt
- demote if C merely sounds more sophisticated or asks a more polished version
  of what B would already ask
- no chat/memo/Pressure Check changes until the compact surface is reviewed
  against existing Lolla flow

### PR 7 - Selective Runtime Promotion, If Earned

**Status 2026-05-05:** not started. Still optional.

**Goal:** Only if earlier evidence supports it, allow affordance-derived material into Pressure Check or memo.

This PR may never be needed. That is acceptable.

**Promotion standard:**

The affordance material must beat the existing baseline:

- it catches something existing Step 7/8 missed
- it changes an action, threshold, sequence, condition, risk treatment, or decision question
- it does not duplicate Lane 4 or Pressure Check
- it can be compressed without machinery leaks

If it does not meet this bar, the affordance layer remains Observatory/debug infrastructure.

---

## 7. Extraction Workflow For Future Coders

This is the intended extraction loop. Do not replace it with a regex pass.

### 7.1 Build A Source Packet

For each model, create a packet containing:

- full canonical source markdown
- current Wave 1 curation
- current Wave 2 curation
- current Wave 3 curation
- existing compiled model object from `data/knowledge_graph.json`, if available
- any known omission/review notes
- target schema
- extraction instructions

The packet may be assembled by Python.

### 7.2 LLM Reads And Extracts

The LLM must read the packet and produce:

- affordances
- source quotes
- extraction type
- confidence
- notes on ambiguity
- drops/rejections
- "do not extract" notes when source material is too thin

The LLM should be instructed to prefer fewer, sharper affordances over broad coverage.

### 7.3 Validate

Python validates:

- JSON schema
- exact source quote substring
- no missing required fields
- no duplicate affordance IDs
- confidence is valid enum
- source file exists
- model ID exists in current model manifest
- field length constraints
- explicit absence states such as `not_supported_by_source` or `source_too_thin`

### 7.4 Review For Genericity

Use a review pass that asks:

- Could this affordance apply to almost any model?
- Does it name evidence the answer must contain?
- Does it name a misuse guard?
- Does it produce a better question or treatment audit?
- Is the source quote actually supporting the normalized field?
- Is the extractor trying to fill a schema slot that the source did not earn?
- Would leaving the field blank preserve more truth than filling it?

Generic fields fail even if JSON validates.

### 7.5 Compile

Only reviewed files enter compiled artifacts.

Compiled artifacts should include:

- stable IDs
- source references
- confidence
- provenance
- compile timestamp / source hash if repo convention supports it

### 7.6 Evaluate Before Runtime Use

Run archived-case comparisons before changing any user-facing surface.

The evaluation question is not:

> Did the new field produce something plausible?

The evaluation question is:

> Did the new field add non-duplicative value beyond the existing lanes?

---

## 8. Quality Gates

Every PR in this program should have explicit gates.

### 8.1 Substrate Quality Gates

- every semantic field has provenance
- exact `source_quote` validation passes
- weak-confidence fields are allowed but not promoted by default
- generic boilerplate count is visible
- absence is represented honestly, not treated as failure by default
- models are allowed to have uneven affordance depth
- coverage is reported, not hidden
- source/curation disagreement is visible

### 8.2 Runtime Safety Gates

- default-off until proven
- Observatory-first
- chat/memo surfacing separately justified
- no machinery vocabulary in rendered chat
- no model-name dumping unless existing voice rules allow it
- no speculative psychology
- no hidden new LLM cost without usage reporting

### 8.3 Evaluation Gates

- compare against existing Pressure Check baseline
- use archived runs before live `/lolla`
- track false positives and duplication
- measure whether output changes action/threshold/sequence/condition/risk/decision-question
- demote to Observatory-only if user value is not proven

---

## 9. What To Avoid

Avoid these failure modes:

### 9.0 Completeness Theater

Bad:

> Every model gets three affordances because the schema expects affordances.

Good:

> A model gets only what the source supports. If the source does not support a runtime-useful affordance, the record says so and the compiler reports the gap.

The runtime should be designed around uneven knowledge. A corpus with honest gaps is stronger than a corpus with smooth, invented coverage.

### 9.1 Mechanical Bulk Extraction

Bad:

> Regex every line after "Danger when" and call it a misuse guard.

Good:

> LLM reads the full source file, understands which danger warnings are operationally distinct, and writes fewer, sharper misuse guards with source quotes.

### 9.2 One-Off Pilot That Cannot Scale

Bad:

> Hand-curate 10 beautiful files with no path to all models.

Good:

> Pilot 10 files to prove schema quality, then build a repeatable LLM extraction/review harness that can scale across the whole active manifest.

### 9.3 Graph Theater

Bad:

> Show a beautiful graph that does not explain routing decisions.

Good:

> Show why a model was selected, why alternatives lost, and which downstream output used or ignored the selected model.

### 9.4 User-Facing Cleverness

Bad:

> Add affordance-derived paragraphs to chat because they are interesting.

Good:

> Surface only if the material changes the user's actual next move and does not duplicate the existing Pressure Check.

### 9.5 LLM As Judge Of Its Own Unscaffolded Context

Bad:

> Give the LLM raw source files, result JSON, and conversation history and ask for "insights."

Good:

> Give a narrow packet with typed source truth, existing compiled fields, a schema, and a specific judgment task.

---

## 10. Evaluation Corpus

Use archived cases before full live `/lolla`.

Start with cases already used in recent validation:

- Mother / daughter / ex co-parent case
- PhD dissertation direction case
- Marcus equity / retention case
- Whistleblower / GC / spouse / attorney case
- Thin PM/director negotiation case
- Named-only negative control

For every experiment, record:

- baseline Pressure Check
- candidate affordance output
- duplicate? yes/no
- plan-changing? yes/no
- safer? yes/no
- more specific? yes/no
- too clever / too dry / too long? yes/no
- merge recommendation: promote / Observatory-only / discard

This is the same hard lesson from PR #74: correctness is not enough. The new signal must beat the current baseline.

---

## 11. How This Improves Each Lane

### Lane 1 - Structural Pressure

Potential improvement:

- route findings not only to corrective models, but to model affordances
- make challenge statements more specific about what evidence is missing
- audit whether selected corrective models were actually treated in the updated answer

Risk:

- overloading the DeltaCard with too much model detail

Safe first step:

- Observatory-only treatment audit

### Lane 2 - Model Companion

Potential improvement:

- replace generic chunks with affordance-shaped chunks where available
- improve selection by prioritizing chunks that define evidence requirements or misuse guards
- expose when a detected model is broad-overlay and needs a guardrail

Risk:

- companion output becomes too abstract or too model-name-heavy

Safe first step:

- compare current `CompanionCheatSheet` chunks against affordance candidates, no runtime change

### Lane 3 - Frame Pressure

Potential improvement:

- use affordances to explain what an alternative frame opens
- distinguish a cute reframe from a model-required reframe

Risk:

- reframings become over-intellectualized

Safe first step:

- Observatory route explanation for frame pattern -> model -> affordance

### Lane 4 - Structural Coverage

Potential improvement:

- sharpen gap questions using model-specific evidence requirements
- reduce generic "Who are the stakeholders?" questions
- improve under-detected dimensions like `feedback-system-dynamics` and `uncertainty-type`

Risk:

- questions become too long or too leading

Safe first step:

- affordance-guided questions behind a flag, compared to archived baseline

---

## 12. Historical First Concrete Next Moves

This section is historical. The original next move was **PR 1: Affordance
Schema And Extraction Contract**. That work is done. The later PR12/Decision
Pressure surface work and PR13-PR24 follow-up are also complete as dormant
research/infrastructure.

The current reviewed posture is
`v9_graph_only_priority_audit_complete` after PR41. Do not
treat any historical item below as active next work.

Historical PR 12 scope was:

1. Use the existing 3-case Gate 4 artifacts and manual product readout.
2. Define the compact user-visible surface that raw enriched probes would have
   to become before promotion.
3. Preserve the no-casuistry boundary: Python owns coverage, trace, packet, and
   validation mechanics; LLMs own semantic judgment and compression.
4. Clarify that Decision Pressure is not a new lane; it is a synthesis object
   for existing Step 6, Step 8 Pressure Check, memo, or Observatory surfaces.
5. Define accepted value modes: `new_edge`, `grounded_double_down`,
   `confirmation`, and `coverage_transparency`.
6. Define rejection modes: fake coverage traces, bloat, duplicate without
   delta, clever-but-not-actionable, and no dismissal path.
7. Define the global compression cap, field-level provenance, zero-output
   success mode, and action-delta requirement.
8. Do not run more paid model calls until this surface is specified and
   reviewed.

Do not run Batch 3, live Lane 4 integration, or chat/memo promotion before the
Decision Pressure surface exists and has reviewer-eye approval.

Original PR 1 scope, preserved for archaeology:

It should not extract all models.

It should answer:

1. What is an affordance?
2. What fields are required?
3. What provenance is required?
4. What counts as generic failure?
5. How does an LLM extraction packet look?
6. What can Python validate?
7. What is explicitly forbidden?

Suggested file:

- `references/model-affordance-extraction.md`

Suggested schema:

- `data/schemas/model_affordance.schema.json` or nearest existing schema convention

Suggested test:

- `tests/test_model_affordance_schema.py`

Suggested pilot fixture:

- one valid `theory-of-constraints` record
- one invalid generic record
- one invalid record with missing source quote
- one weak-confidence record that validates but is not promotable
- one valid empty/thin record where the source does not support runtime-useful affordances

Do this first because it prevents the whole program from becoming "bulk generate JSON and hope."

---

## 13. Open Questions

Original open questions from May 4, with current status:

- **Where should affordance files live?** Answered: reviewed records live under
  `data/model_affordances/`; compiled artifacts live under
  `data/compiled/model_affordances/`.
- **Where should source quote validation point?** Answered: canonical sources
  were copied into `data/model_sources/` with a SHA-256 manifest.
- **What is the active model count?** Answered for current runtime:
  `data/knowledge_graph.json` contains `222` models.
- **One LLM call per model or per family?** Current practice: per-model
  extraction/review records. Do not change until a batch-scale pain appears.
- **Weak-confidence affordances: compiled or review-only?** Current practice:
  compile honestly, keep runtime dormant, surface flags and review notes. Do
  not promote weak/broad records by default.
- **Observatory route graph shape?** Still open as product UI. Current evidence
  work uses table/JSON summaries first.
- **Treatment audit judge shape?** Current evidence supports narrow LLM judging
  with activation gating and human/Codex reviewer-eye. Deterministic text
  presence checks are not sufficient for semantic treatment.

New open questions after PR 11:

- Should Decision Pressure run as a post-processor after baseline/enriched
  probes, or should future generation ask directly for compact pressures?
- Should coverage transparency be user-visible, Observatory-only, or both?
- Should the normal user-facing cap be one total pressure or up to three total
  pressures for high-stakes runs?
- Which existing surface should usually receive the compact pressure: Step 6,
  Step 8 Pressure Check, memo, or Observatory?
- How should confirmation be surfaced: as "multiple checks point here" or only
  as prioritization weight?

---

## 14. Final Position

The next phase should make Lolla better at using the knowledge it already has,
but only when the knowledge can be compressed into a decision safeguard the user
would actually want before acting.

Do not add more theatrical intelligence around the system.
Do not make the graph look smarter than it is.
Do not scrape the source files mechanically.
Do not fill knowledge gaps just because the runtime would like a field.
Do not promote user-facing content until it improves the user's decision
position without bloat, fake coverage, or machinery leaks.

Instead:

1. Preserve the v3 affordance kernel as draft-review knowledge.
2. Define the Decision Pressure surface before more paid Gate 4 runs.
3. Treat C-only OOD as strongest evidence, not the only value mode.
4. Accept grounded double-down, useful confirmation, and coverage transparency
   when they improve decision position.
5. Allow "No additional source-backed pressure cleared the bar" as a premium
   zero-output result.
6. Use Codex sub-agents as reviewer-eye, not formal measurement boundary.
7. Use affordances to improve Lane 4 only after the compact surface is proven.
8. Promote to chat or memo only when evidence says users get a better decision artifact.

This keeps the system aligned with its own best doctrine:

> Source truth over runtime improvisation.
> Curated structure over raw context.
> Deterministic middle over one big magic box.
> Observatory before user surface.
> Decision pressure before user-facing confidence.

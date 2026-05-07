# Reasoning Substrate Next Session Handover

**Date:** 2026-05-07
**Status:** Start-here handover after PR45 completed controlled frame
correction / metacognitive blind-spot enrichment. PR44 selected the family;
PR45 extracted source-backed v11 depth for exactly those 12 models.
This is still not runtime behavior, prompt promotion, lane rewrite, broad
Batch 3b, or user-facing Decision Pressure work.

**Current posture:** `controlled_frame_correction_enrichment_ready`

**Current PR:** PR45 - controlled frame correction enrichment

**PR24 review verdict:** `approve_pr24`

**PR25 decision label:** `fixture_packet_producer_ready`

**PR26 decision label:** `source_custody_backfill_complete`

**PR27 decision label:** `mixed_packet_fixture_useful`

**PR28 decision label:** `controlled_graph_only_extraction_batch_ready`

**PR29 decision label:** `v5_packet_depth_improved`

**PR30 decision label:** `packet_review_rendering_ready`

**PR31 decision label:** `v5_capability_audit_complete`

**PR32 decision label:** `controlled_capability_gap_enrichment_ready`

**PR33 decision label:** `v6_packet_handoff_useful`

**PR34 decision label:** `controlled_communication_competition_enrichment_ready`

**PR35 decision label:** `v7_packet_handoff_useful`

**PR36 decision label:** `controlled_trust_negotiation_enrichment_ready`

**PR37 decision label:** `v8_packet_handoff_useful`

**PR38 decision label:** `v8_graph_only_priority_audit_complete`

**PR39 decision label:** `controlled_execution_followthrough_enrichment_ready`

**PR40 decision label:** `v9_execution_packet_handoff_useful`

**PR41 decision label:** `v9_graph_only_priority_audit_complete`

**PR42 decision label:** `controlled_risk_reversibility_enrichment_ready`

**PR43 decision label:** `v10_risk_packet_handoff_useful`

**PR44 decision label:** `v10_graph_only_priority_audit_complete`

**PR45 decision label:** `controlled_frame_correction_enrichment_ready`

## Start Here

Read these files in order:

1. `research/reasoning-substrate-next-session-handover-2026-05-06.md`
2. `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`
3. `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`
4. `research/enriched-mental-model-packet-strategy-2026-05-06.md`
5. `research/knowledge-matching-current-state-audit-2026-05-06.md`
6. `research/decision-pressure-product-doctrine-2026-05-06.md`
7. `plans/knowledge-substrate-roadmap-2026-05-04.md`
8. `plans/knowledge-use-schema-2026-05-04.md`
9. `research/reasoning-substrate-lane-placement-audit-2026-05-06.md`
10. `research/full-corpus-enrichment-coverage-audit-2026-05-06.md`
11. `research/reasoning-substrate-source-custody-backfill-2026-05-06.md`
12. `research/reasoning-substrate-packet-fixture-review-2026-05-06.md`
13. `research/pr28-controlled-graph-only-extraction-report-2026-05-06.md`
14. `research/reasoning-substrate-v5-packet-depth-review-2026-05-07.md`
15. `research/reasoning-substrate-packet-review-rendering-2026-05-07.md`
16. `research/reasoning-substrate-packet-comparison-render-2026-05-07.md`
17. `research/reasoning-substrate-packet-pr27-review-render-2026-05-07.md`
18. `research/reasoning-substrate-packet-pr29-review-render-2026-05-07.md`
19. `research/v5-reviewed-model-capability-audit-2026-05-07.md`
20. `research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md`
21. `research/reasoning-substrate-v6-packet-usefulness-review-2026-05-07.md`
22. `research/reasoning-substrate-packet-pr33-v5-v6-comparison-render-2026-05-07.md`
23. `research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md`
24. `research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md`
25. `research/reasoning-substrate-packet-pr35-v6-v7-comparison-render-2026-05-07.md`
26. `research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md`
27. `research/reasoning-substrate-v8-packet-usefulness-review-2026-05-07.md`
28. `research/reasoning-substrate-packet-pr37-v7-v8-comparison-render-2026-05-07.md`
29. `research/v8-graph-only-priority-audit-2026-05-07.md`
30. `research/pr39-controlled-execution-followthrough-enrichment-report-2026-05-07.md`
31. `research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md`
32. `research/reasoning-substrate-packet-pr40-v8-v9-comparison-render-2026-05-07.md`
33. `research/v9-graph-only-priority-audit-2026-05-07.md`
34. `research/pr42-controlled-risk-reversibility-enrichment-report-2026-05-07.md`
35. `research/reasoning-substrate-v10-packet-usefulness-review-2026-05-07.md`
36. `research/reasoning-substrate-packet-pr43-v9-v10-comparison-render-2026-05-07.md`
37. `research/v10-graph-only-priority-audit-2026-05-07.md`
38. `research/pr45-controlled-frame-correction-enrichment-report-2026-05-07.md`

Only read the older PR13-PR23 artifacts when you need historical evidence. Do
not restart from them as the active product direction.

## Current Architecture In One Page

The system is not trying to make Python wise.

The current architecture is:

> Broad intake, disciplined output.
> Pull shelves, enrich cards, let the LLM reason.
> Python guards rails. It does not decide wisdom.

Meaning:

- existing lanes pull candidate mental-model shelves;
- deterministic code may dedupe, cap, label coverage, attach graph fields and
  reviewed-affordance snippets, preserve provenance, and expose absence
  records;
- the LLM/reviewer decides what matters, what to ignore, what to merge, and
  whether any Decision Pressure emerges.

## Substrate Story

Keep these layers distinct:

| Layer | Count / role |
| --- | --- |
| Runtime graph | 222 model records. Broad shelf recall. |
| Tendencies | 25 tendency routes for Lane 1. |
| Runtime graph fields | `select_when`, `danger_when`, `failure_modes`, `premortem_questions`, `heuristics`, `reasoning_types`. |
| Canonical markdown | 222 files, about 491k words. Source truth for broader expansion. |
| Repo-local source custody | 222 files in `data/model_sources/` with SHA-256 manifest after PR26. |
| v4 affordance corpus | 55 reviewed records, 91 affordances, 95 absence records. Deep reviewed subset, still dormant. |
| v5 affordance corpus | 65 reviewed records, 101 affordances, 115 absence records. Draft/review-only v4 plus PR28 controlled batch, not runtime-promoted. |
| v6 affordance corpus | 81 reviewed records, 117 affordances, 147 absence records. Draft/review-only v5 plus PR32 controlled capability-gap batch, not runtime-promoted. |
| v7 affordance corpus | 88 reviewed records, 124 affordances, 161 absence records. Draft/review-only v6 plus PR34 controlled communication/competition batch, not runtime-promoted. |
| v8 affordance corpus | 98 reviewed records, 134 affordances, 181 absence records. Draft/review-only v7 plus PR36 controlled trust/negotiation batch, not runtime-promoted. |
| Graph-only after v8 | 124 runtime models remain eligible but not reviewed affordance records. |
| PR27 mixed packet fixture | 7 candidate cards plus 1 suppressed duplicate. Review-only proof that mixed v4 + graph-only packets are useful handoff material. |
| PR28 controlled extraction batch | 10 graph-only models gained reviewed records with 10 affordances and 20 absence records. |
| PR29 v5 packet depth review | Same 7-card PR27 fixture regenerated against v5. Reviewed cards increased from 3 to 7, graph-only cards fell from 4 to 0, and packet burden stayed acceptable. |
| PR30 packet review rendering | Deterministic reviewer-only Markdown renders for PR27, PR29, and their comparison. Makes packet review easier; does not select output or create a product surface. |
| PR31 v5 capability audit | Audits what the 65 reviewed records can already support and names the next controlled enrichment gaps. |
| PR32 controlled capability-gap enrichment | 16 graph-only models from the PR31 gap list gained reviewed records with 16 affordances and 32 absence records; compiled as draft/review-only v6. |
| PR33 v6 packet usefulness review | Same 10-card nomination set compared against v5 and v6. Reviewed cards increased from 1 to 10, graph-only cards fell from 9 to 0, and candidate count stayed fixed. |
| PR34 controlled communication/competition enrichment | 7 graph-only models from communication, feedback, strategic interdependence, and analogy/adaptive gaps gained reviewed records with 7 affordances and 14 absence records; compiled as draft/review-only v7. |
| PR35 v7 packet usefulness review | Same 9-card communication/competition nomination set compared against v6 and v7. Reviewed cards increased from 2 to 9, graph-only cards fell from 7 to 0, and candidate count stayed fixed. |
| PR36 controlled trust/negotiation enrichment | 10 graph-only models from trust repair, motivation, boundaries, influence, negotiation, and signaling gaps gained reviewed records with 10 affordances and 20 absence records; compiled as draft/review-only v8. |
| PR37 v8 packet usefulness review | Same 10-card trust/negotiation nomination set compared against v7 and v8. Reviewed cards increased from 0 to 10, graph-only cards fell from 10 to 0, and candidate count stayed fixed. |
| PR38 v8 graph-only priority audit | Reviews the remaining 124 graph-only models after v8 and recommends execution / implementation / follow-through discipline as the next controlled enrichment family. No extraction, runtime, prompt, lane, model-call, judge, or user-facing work. |
| PR39 controlled execution/follow-through enrichment | 12 graph-only models from execution, auditability, baselines, bottlenecks, debugging, feedback, goals, habits, iteration, and validated learning gained reviewed records with 12 affordances and 24 absence records; compiled as draft/review-only v9. |
| v9 affordance corpus | 110 reviewed records, 146 affordances, 205 absence records. Draft/review-only v8 plus PR39 controlled execution/follow-through batch, not runtime-promoted. |
| Graph-only after v9 | 112 runtime models remain eligible but not reviewed affordance records. |
| PR40 v9 execution packet usefulness review | Same 12-card execution/follow-through nomination set compared against v8 and v9. v8 packet had 12 graph-only cards; v9 packet has 11 reviewed cards and 1 weak/conflicting support card, with candidate count fixed. |
| PR41 v9 graph-only priority audit | Reviews the remaining 112 graph-only models after v9 and recommends risk controls / reversibility / failure containment as the next controlled enrichment family. No extraction, runtime, prompt, lane, model-call, judge, or user-facing work. |
| PR42 controlled risk/reversibility enrichment | 12 graph-only models from risk controls, reversibility, failure containment, nonlinear dynamics, switching costs, and loss framing gained reviewed Batch 9 records with 12 affordances and 24 absence records; compiled as draft/review-only v10. |
| v10 affordance corpus | 122 reviewed records, 158 affordances, 229 absence records. Draft/review-only v9 plus PR42 controlled risk/reversibility batch, not runtime-promoted. |
| Graph-only after v10 | 100 runtime models remain eligible but not reviewed affordance records. |
| PR43 v10 risk/reversibility packet usefulness review | Same 12-card risk/reversibility nomination set compared against v9 and v10. v9 packet had 12 graph-only cards; v10 packet has 12 reviewed cards, with candidate count fixed. |
| PR44 v10 graph-only priority audit | Reviews the remaining 100 graph-only models after v10 and recommends frame correction / metacognitive blind-spot discipline as the next controlled enrichment family. No extraction, runtime, prompt, lane, model-call, judge, or user-facing work. |
| PR45 controlled frame-correction enrichment | 12 graph-only models from frame correction, metacognition, counterfactual, and evidence-boundary gaps gained reviewed Batch 10 records with 12 affordances and 24 absence records; compiled as draft/review-only v11. |
| v11 affordance corpus | 134 reviewed records, 170 affordances, 253 absence records. Draft/review-only v10 plus PR45 controlled frame-correction batch, not runtime-promoted. |
| Graph-only after v11 | 88 runtime models remain eligible but not reviewed affordance records. |

The governing sentence:

> 222 gives breadth. Reviewed affordance artifacts give depth. The packet must
> preserve both without pretending they are the same kind of evidence.

## Existing Lanes Stay Intact

Do not rewrite lanes by default.

- Lane 1 finds tendency failures and corrective routes from the conversation
  transaction.
- Lane 2 attributes models present or violated in the assistant answer.
- Lane 3 contributes user-framing shelf hints.
- Lane 4 contributes structural gap shelf hints.

The next object, if reviewed and approved, is not another lane. It is a dormant
handoff object:

> `reasoning_substrate_packet.v1`

That packet is candidate material for the next LLM. It is not the final answer.

## What PR24 Did

PR24 completed a docs/research audit and spec:

- `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`
- `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`
- supporting doctrine/roadmap/schema updates

It established:

- the 222-model graph is broad enough to remain the candidate shelf base;
- v4 is deep enough to enrich reviewed shelves but too narrow to become the
  whole matching substrate;
- graph-only models must remain eligible but honestly labeled;
- the missing bridge is an enriched-card packet, not a deterministic pressure
  selector;
- future expansion should be packet-usefulness and pressure-family driven, not
  count-completion driven.

## What PR24 Did Not Do

PR24 did not:

- change runtime behavior;
- change prompts;
- rewrite lanes;
- create a packet producer;
- create a sample packet fixture;
- expand v4 records;
- run model calls or judges;
- wire `/lolla`;
- wire Observatory, memo, Step 8, Step 6, or Lane 4;
- create user-facing Decision Pressure output;
- let Python choose final pressure.

## What PR25 Reopened

PR24's `stop_and_consolidate` outcome meant "do not continue the wrong
Decision Pressure machinery by momentum." It did not mean the reasoning
substrate must remain frozen forever.

PR25 reopened forward work only along the corrected architecture:

- existing lanes stay intact and keep nominating candidate mental-model
  shelves;
- v4 becomes additive enrichment to lane-selected candidates, not a replacement
  for the 222-model graph;
- graph-only models remain eligible with honest labels;
- deterministic code packages graph fields, reviewed affordance snippets, absence
  records, source custody, caps, and provenance;
- Python does not choose final pressure, final memo copy, semantic novelty,
  actionability, or wisdom;
- the LLM/reviewer decides what matters, what to merge, what to ignore, and
  whether any Decision Pressure or other output should emerge.

## What PR25 Added

PR25 adds a dormant enrichment-placement slice:

- `research/reasoning-substrate-lane-placement-audit-2026-05-06.md` maps Lane
  1, Lane 2, Lane 3, and Lane 4 outputs to future packet nominations and
  identifies the route-trace-adjacent boundary for a later adapter.
- `engine/system_b/reasoning_substrate_coverage.py` and
  `tests/test_reasoning_substrate_coverage.py` deterministically audit full
  corpus breadth/depth coverage across runtime graph, v4, source custody,
  canonical markdown availability, runtime graph fields, reasoning-type gaps,
  and static lane-signal priorities.
- `research/full-corpus-enrichment-coverage-audit-2026-05-06.md` records the
  controlled expansion plan: source-custody first, then reviewed batches of
  20-30, selected by lane signal, reasoning-type gap, source quality, and
  later route-trace frequency.
- `engine/system_b/reasoning_substrate_packet.py` and
  `tests/test_reasoning_substrate_packet.py` add a fixture/review-only packet
  producer for explicit candidate nominations. It enriches v4-reviewed and
  graph-only candidates without running live lanes or emitting user-facing
  prose.

PR25 does not wire live `/lolla`, prompts, Observatory, memo, Step 8, Step 6,
Lane 4 runtime, judges, model calls, extraction, Batch 3b, or deterministic
pressure selection.

## What PR26 Added

PR26 completes the deterministic source-custody backfill:

- copied the remaining `167` runtime model source files from
  `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216` into
  `data/model_sources/`;
- regenerated `data/model_sources/manifest.json` from runtime graph
  `source_file` references;
- left the existing `55` source files unchanged when bytes already matched
  canonical source;
- added `engine/system_b/source_custody.py` as a deterministic custody report
  helper;
- added `tests/test_reasoning_substrate_source_custody.py` to prove `222`
  manifest model IDs, local hash/byte matches, and canonical byte matches;
- updated `engine/system_b/reasoning_substrate_coverage.py` so coverage audits
  report source custody separately from v4 reviewed depth.

PR26 does not extract new affordance records. The v4 corpus still covers `55`
reviewed models, and `167` runtime models remain graph-only after v4. Source
custody means future extraction can quote and validate repo-local source truth;
it does not mean graph-only models have reviewed affordance records.

## What PR27 Added

PR27 completes a tiny mixed reasoning-substrate packet fixture review:

- added `tests/fixtures/reasoning_substrate_packet/pr27_mixed_packet_review.json`;
- added `tests/test_reasoning_substrate_packet_fixture.py` to prove the
  fixture matches the dormant producer output;
- updated `engine/system_b/reasoning_substrate_packet.py` so cards expose
  source custody separately from v4 reviewed record/affordance availability;
- added `research/reasoning-substrate-packet-fixture-review-2026-05-06.md`;
- kept the packet review-only, runtime-dormant, and generated from explicit
  nominations.

PR27's fixture contains:

- `3` v4-reviewed cards:
  `opportunity-cost`, `falsifiability`, `probabilistic-thinking`;
- `4` source-custodied graph-only cards:
  `step-back`, `constraints`, `chain-of-verification`, `confirmation-bias`;
- `1` suppressed duplicate candidate.

PR27's decision label is `mixed_packet_fixture_useful`.

The product lesson:

> Mixed packets are useful handoff material. v4 cards are meaningfully richer,
> graph-only cards are useful but thinner, and source custody improves trust
> without pretending to be reviewed affordance depth.

PR27 does not extract new records, modify `affordances_v4.json`, run live
lanes, wire `/lolla`, change prompts, run model calls or judges, or create
user-facing Decision Pressure output.

## What PR28 Added

PR28 completes the first controlled reviewed extraction batch for graph-only
models exposed as useful but thin by PR27:

- added ten records under `data/model_affordances/batch_4/`;
- compiled `data/compiled/model_affordances/affordances_v5.json`;
- generated `data/compiled/model_affordances/quality_report_v5.md`;
- added `tests/test_pr28_batch4_records.py`;
- added `research/pr28-controlled-graph-only-extraction-report-2026-05-06.md`;
- kept v5 `draft_review_only` and unimported by live runtime paths.

PR28 target models:

- `chain-of-verification`;
- `constraints`;
- `confirmation-bias`;
- `step-back`;
- `scientific-method-evidence-testing`;
- `five-whys-method`;
- `root-cause-analysis`;
- `first-principles-thinking`;
- `intellectual-humility`;
- `authority-bias`.

PR28 added `10` affordances and `20` absence records. Every target model was a
runtime graph model, source-custodied, and absent from v4 before PR28.

PR28's decision label is `controlled_graph_only_extraction_batch_ready`.

The product lesson:

> Source custody made extraction possible, PR27 made extraction justified, and
> PR28 shows the first graph-only sources can add compact operational depth when
> absence records are treated as first-class output.

PR28 does not promote v5 into runtime, modify `affordances_v4.json`, run live
lanes, wire `/lolla`, change prompts, run model calls or judges, create Batch
3b, or create user-facing Decision Pressure output.

## What PR29 Added

PR29 regenerates the PR27 mixed packet fixture against the draft/review-only v5
artifact and compares handoff quality, not final-answer quality:

- added `tests/fixtures/reasoning_substrate_packet/pr29_v5_mixed_packet_review.json`;
- added `tests/test_reasoning_substrate_packet_v5_fixture.py`;
- added `research/reasoning-substrate-v5-packet-depth-review-2026-05-07.md`;
- kept the same transaction context, nominations, cap, and duplicate
  suppression as PR27;
- verified the four PR27 graph-only cards now carry reviewed depth under v5:
  `chain-of-verification`, `constraints`, `confirmation-bias`, and
  `step-back`.

PR29 before/after shape:

- candidate cards stayed `7`;
- suppressed candidates stayed `1`;
- reviewed cards increased from `3` to `7`;
- graph-only cards decreased from `4` to `0`;
- visible absence records increased from `3` to `7`;
- reviewed source-evidence references increased from `3` to `7`;
- packet size increased from `33,848` bytes to `42,756` bytes.

PR29's decision label is `v5_packet_depth_improved`.

The product lesson:

> Controlled extraction improved the reasoning handoff for the selected cards:
> the packet now gives clearer activation, evidence-needed, do-not-use, misuse,
> treatment, and absence signals without making Python choose a conclusion.

PR29 does not extract new records, promote v5 into runtime, modify
`affordances_v5.json`, run live lanes, wire `/lolla`, change prompts, run model
calls or judges, create Batch 3b, or create user-facing Decision Pressure
output.

## What PR30 Added

PR30 adds a compact, deterministic receiver-review rendering layer for existing
dormant packet fixtures:

- `engine/system_b/reasoning_substrate_packet_review.py` renders a packet or
  before/after packet comparison to reviewer-only Markdown;
- `tests/test_reasoning_substrate_packet_review_render.py` proves the renderer
  rejects non-dormant packets, stays out of live runtime imports, and does not
  emit final pressure fields, memo copy, HTML, or user-facing prose;
- `research/reasoning-substrate-packet-pr27-review-render-2026-05-07.md`
  renders the PR27 mixed packet;
- `research/reasoning-substrate-packet-pr29-review-render-2026-05-07.md`
  renders the PR29 v5 packet;
- `research/reasoning-substrate-packet-comparison-render-2026-05-07.md`
  renders the PR27 vs PR29 count and coverage comparison.

PR30's decision label is `packet_review_rendering_ready`.

The product lesson:

> Receiver-side review needs an inspectable handoff surface before more
> extraction. The renderer makes packet evidence easier to inspect while
> preserving the boundary: Python renders custody, coverage, provenance, and
> compact signals; it does not choose user-visible output.

PR30 does not run model calls, answer the case, choose Decision Pressure,
promote v5 into runtime, run live lanes, wire `/lolla`, change prompts, create
Batch 3b, add extraction, or create user-facing output.

## What PR31 Added

PR31 answers the question: "What can the 65 reviewed models tell us?"

It adds:

- `research/v5-reviewed-model-capability-audit-2026-05-07.md`

Measured v5 shape:

- `65` reviewed model records;
- `101` reviewed affordances;
- `115` absence records;
- `889` source-evidence references inside affordances;
- `208` treatment requirements;
- `397` diagnostic questions;
- `372` misuse guards;
- `157` runtime models still graph-only after v5.

PR31's decision label is `v5_capability_audit_complete`.

The product lesson:

> The 65 reviewed records are enough to test whether enriched packets improve
> downstream LLM judgment across several high-value pressure families. They are
> not enough for product launch, deterministic pressure selection, or broad
> 222-model parity.

PR31 identifies the current strongest capability families:

- evidence discipline and falsification;
- commitment, trade-off, and resource discipline;
- uncertainty, probability, and risk;
- causal and systems diagnosis;
- incentives, agency, information, and power;
- bias, metacognition, and correction;
- learning, experiment design, and adaptation;
- human context, trust, and team process.

PR31 also names the next controlled enrichment gaps: delays and obligations,
peer review, formal/checklist discipline, planning/status quo/commitment bias,
competitive and bargaining pressure, product/customer/market lock-in, and
cross-cultural communication.

PR31 does not extract new records, promote v5 into runtime, run live lanes,
wire `/lolla`, change prompts, run model calls or judges, create Batch 3b, or
create user-facing Decision Pressure output.

## What PR32 Added

PR32 answers the question: "Can the named PR31 capability gaps produce useful
reviewed depth without drifting into broad mechanical extraction?"

It adds:

- `data/model_affordances/batch_5/`;
- `data/compiled/model_affordances/affordances_v6.json`;
- `data/compiled/model_affordances/quality_report_v6.md`;
- `tests/test_pr32_batch5_records.py`;
- `research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md`.

Measured v6 shape:

- `81` reviewed model records;
- `117` reviewed affordances;
- `147` absence records;
- `1487` source-evidence references across reviewed records;
- `224` treatment requirements;
- `445` diagnostic questions;
- `420` misuse guards;
- `141` runtime models still graph-only after v6.

PR32's decision label is `controlled_capability_gap_enrichment_ready`.

The product lesson:

> Controlled gap-driven extraction can add real reviewed handoff depth without
> pretending the corpus is complete. Fifteen of sixteen sources produced strong
> operational records, and `batna` was intentionally kept thin/narrow because
> the source itself does not support full BATNA doctrine.

PR32 targeted these capability gaps:

- delay and obligation discipline: `delays`,
  `obligations-controls-mapping`;
- external correction and formal procedure: `peer-review-your-perspectives`,
  `formal-reasoning`, `checklists`;
- planning and inertia risk: `status-quo-bias`, `commitment-bias`,
  `optimism-bias-and-planning-fallacy`;
- competitive and bargaining pressure: `batna`, `game-theory-payoffs`,
  `red-queen-effect`;
- product/customer and dependency reasoning: `jobs-to-be-done`,
  `user-centered-design`, `lock-in`, `path-dependence`;
- communication and relational translation:
  `cross-cultural-communication-frameworks`.

PR32 does not promote v6 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, or create user-facing
Decision Pressure output.

## What PR33 Added

PR33 answers the question: "Did PR32's v6 depth actually improve a packet
handoff, or merely increase corpus size?"

It adds:

- `tests/fixtures/reasoning_substrate_packet/pr33_v5_capability_gap_packet_review.json`;
- `tests/fixtures/reasoning_substrate_packet/pr33_v6_capability_gap_packet_review.json`;
- `tests/test_reasoning_substrate_packet_v6_fixture.py`;
- `research/reasoning-substrate-packet-pr33-v5-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr33-v6-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr33-v5-v6-comparison-render-2026-05-07.md`;
- `research/reasoning-substrate-v6-packet-usefulness-review-2026-05-07.md`.

Measured PR33 packet comparison:

- candidate cards stay fixed at `10`;
- suppressed duplicate count stays fixed at `1`;
- reviewed cards move from `1` under v5 to `10` under v6;
- graph-only cards move from `9` under v5 to `0` under v6;
- missing reviewed records move from `9` to `0`;
- no final pressure or user-facing output is generated.

PR33's decision label is `v6_packet_handoff_useful`.

The product lesson:

> v6 reviewed cards improve concrete packet handoff material when the same
> shelves are nominated. The improvement is operational depth under stable
> packet shape, not deterministic answer selection.

PR33 does not promote v6 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, or create user-facing
Decision Pressure output.

## What PR34 Added

PR34 answers the question: "Can the next named communication, feedback,
competition, and analogy gaps produce source-backed reviewed depth without
sliding into broad mechanical extraction?"

It adds:

- `data/model_affordances/batch_6/`;
- `data/compiled/model_affordances/affordances_v7.json`;
- `data/compiled/model_affordances/quality_report_v7.md`;
- `tests/test_pr34_batch6_records.py`;
- `research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md`.

Measured v7 shape:

- `88` reviewed model records;
- `124` reviewed affordances;
- `161` absence records;
- `1542` source-evidence references across reviewed records;
- `231` treatment requirements;
- `466` diagnostic questions;
- `441` misuse guards;
- `134` runtime models still graph-only after v7.

PR34's decision label is
`controlled_communication_competition_enrichment_ready`.

The product lesson:

> Controlled enrichment can patch specific receiver-side packet gaps in
> communication/feedback, strategic interdependence, and analogy/adaptive
> reasoning while preserving absence records and draft/review-only custody.

PR34 targeted:

- strategic interdependence: `nash-equilibrium`, `prisoners-dilemma`;
- communication and feedback: `active-listening`,
  `constructive-feedback-models`, `feedback-models-sbi`;
- analogy/adaptive reasoning: `analogies-and-metaphors`,
  `natural-selection-analogy`.

Each target produced one compact reviewed affordance and two absence records.
The batch is useful corpus depth, not runtime promotion or proof that
extraction should continue by count momentum. PR35 later compared a
v7-enriched packet against v6 for a communication/competition case before
another extraction batch was opened.

PR34 does not promote v7 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, or create user-facing
Decision Pressure output.

## What PR35 Added

PR35 answers the question: "Did PR34's v7 depth actually improve a
communication/competition packet handoff, or merely increase corpus size?"

It adds:

- `tests/fixtures/reasoning_substrate_packet/pr35_v6_communication_competition_packet_review.json`;
- `tests/fixtures/reasoning_substrate_packet/pr35_v7_communication_competition_packet_review.json`;
- `tests/test_reasoning_substrate_packet_v7_fixture.py`;
- `research/reasoning-substrate-packet-pr35-v6-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr35-v7-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr35-v6-v7-comparison-render-2026-05-07.md`;
- `research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md`.

Measured PR35 packet comparison:

- candidate cards stay fixed at `9`;
- suppressed duplicate count stays fixed at `1`;
- reviewed cards move from `2` under v6 to `9` under v7;
- graph-only cards move from `7` under v6 to `0` under v7;
- missing reviewed records move from `7` to `0`;
- no final pressure or user-facing output is generated.

PR35's decision label is `v7_packet_handoff_useful`.

The product lesson:

> v7 reviewed cards improve concrete packet handoff material when the same
> communication/competition shelves are nominated. The improvement is
> operational depth under stable packet shape, not deterministic answer
> selection.

PR35 does not promote v7 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, or create user-facing
Decision Pressure output.

## What PR36 Added

PR36 answers the question: "Can the next named trust, relationship repair,
motivation, influence, negotiation, and signaling gaps produce source-backed
reviewed depth without turning interpersonal work into generic advice?"

It adds:

- `data/model_affordances/batch_7/`;
- `data/compiled/model_affordances/affordances_v8.json`;
- `data/compiled/model_affordances/quality_report_v8.md`;
- `tests/test_pr36_batch7_records.py`;
- `research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md`.

Measured v8 shape:

- `98` reviewed model records;
- `134` reviewed affordances;
- `181` absence records;
- `1604` source-evidence references across reviewed records;
- `241` treatment requirements;
- `496` diagnostic questions;
- `471` misuse guards;
- `124` runtime models still graph-only after v8.

PR36's decision label is `controlled_trust_negotiation_enrichment_ready`.

The product lesson:

> Controlled enrichment can make trust repair, interpersonal diagnosis,
> influence, negotiation, and signaling packets more source-aware without
> promoting softness, manipulation, or impression management as wisdom.

PR36 targeted:

- trust repair and hard conversation: `non-violent-communication`,
  `emotional-intelligence`, `authenticity`, `boundaries`, `hanlons-razor`;
- motivation and interpersonal inference: `understanding-motivations`;
- negotiation influence and proof: `reciprocity-principle`,
  `persuasion-principles`,
  `international-negotiation-and-diplomacy-models`, `signaling`.

Each target produced one compact reviewed affordance and two absence records.
The batch is useful corpus depth, not runtime promotion or proof that
extraction should continue by count momentum. PR37 later compared a v8-enriched
trust/negotiation packet against v7 before another extraction batch was opened.

PR36 does not promote v8 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, or create user-facing
Decision Pressure output.

## What PR37 Added

PR37 answers the question: "Did PR36's v8 depth actually improve a
trust/negotiation packet handoff, or merely increase corpus size?"

It adds:

- `tests/fixtures/reasoning_substrate_packet/pr37_v7_trust_negotiation_packet_review.json`;
- `tests/fixtures/reasoning_substrate_packet/pr37_v8_trust_negotiation_packet_review.json`;
- `tests/test_reasoning_substrate_packet_v8_fixture.py`;
- `research/reasoning-substrate-packet-pr37-v7-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr37-v8-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr37-v7-v8-comparison-render-2026-05-07.md`;
- `research/reasoning-substrate-v8-packet-usefulness-review-2026-05-07.md`.

Measured PR37 packet comparison:

- candidate cards stay fixed at `10`;
- suppressed duplicate count stays fixed at `1`;
- reviewed cards move from `0` under v7 to `10` under v8;
- graph-only cards move from `10` under v7 to `0` under v8;
- missing reviewed records move from `10` to `0`;
- no final pressure or user-facing output is generated.

PR37's decision label is `v8_packet_handoff_useful`.

The product lesson:

> v8 reviewed cards improve concrete packet handoff material when the same
> trust/negotiation shelves are nominated. The improvement is operational depth
> under stable packet shape, not deterministic answer selection.

PR37 does not promote v8 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, or create user-facing
Decision Pressure output.

## What PR38 Added

PR38 answers the question: "After v8, which remaining graph-only family is
likely to make future packets thin enough that controlled enrichment is
justified?"

It adds:

- `research/v8-graph-only-priority-audit-2026-05-07.md`;
- `tasks/tasks-v8-graph-only-priority-audit.md`;
- living-doc posture updates.

Measured PR38 audit state:

- runtime graph models stay fixed at `222`;
- source-custodied files stay fixed at `222`;
- v8 reviewed records stay fixed at `98`;
- v8 affordances stay fixed at `134`;
- v8 absence records stay fixed at `181`;
- graph-only runtime models after v8 stay fixed at `124`;
- no extraction or runtime artifact changes occur.

PR38's decision label is `v8_graph_only_priority_audit_complete`.

The product lesson:

> The next controlled enrichment family should be execution / implementation /
> follow-through discipline because that is where future packets are likely to
> be thin when plausible AI advice must become executable, inspectable,
> adjustable, and stoppable.

The recommended PR39 target set is capped at 12 models:

- `algorithmic-thinking`;
- `auditability-traceability`;
- `baseline-establishment`;
- `bottlenecks`;
- `debugging-strategies`;
- `devops-and-continuous-integration`;
- `feedback-loops`;
- `goal-setting`;
- `habit-formation`;
- `input-vs-output-goals`;
- `iteration`;
- `lean-startup-methodology`.

PR38 did not extract those records. PR39 later opened exactly this controlled
batch and read each source directly, allowing thin/narrow or absence-heavy
outcomes where the source did not support operational depth.

PR38 does not promote v8 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, create user-facing
Decision Pressure output, or allow deterministic final pressure selection.

## What PR39 Added

PR39 answers the question: "Can source-backed execution/follow-through records
help a future packet distinguish advice that is merely plausible from advice
that is executable, inspectable, adjustable, and stoppable?"

It adds:

- `data/model_affordances/batch_8/`;
- `data/compiled/model_affordances/affordances_v9.json`;
- `data/compiled/model_affordances/quality_report_v9.md`;
- `tests/test_pr39_batch8_records.py`;
- `research/pr39-controlled-execution-followthrough-enrichment-report-2026-05-07.md`;
- `tasks/tasks-controlled-execution-followthrough-enrichment-batch.md`;
- living-doc posture updates.

Measured PR39 state:

- runtime graph models stay fixed at `222`;
- source-custodied files stay fixed at `222`;
- v9 reviewed records: `110`;
- v9 affordances: `146`;
- v9 absence records: `205`;
- graph-only runtime models after v9: `112`;
- v9 status: `draft_review_only`.

PR39's decision label is
`controlled_execution_followthrough_enrichment_ready`.

The 12 target models were:

- `algorithmic-thinking`;
- `auditability-traceability`;
- `baseline-establishment`;
- `bottlenecks`;
- `debugging-strategies`;
- `devops-and-continuous-integration`;
- `feedback-loops`;
- `goal-setting`;
- `habit-formation`;
- `input-vs-output-goals`;
- `iteration`;
- `lean-startup-methodology`.

The product lesson:

> Execution/follow-through cards are useful only when they stop generic
> productivity advice and give the next LLM operational checks: baseline,
> bottleneck, trace, feedback signal, failure condition, controllable input,
> bounded iteration, and stop/change threshold.

`devops-and-continuous-integration` remains intentionally thin/narrow because
the source does not support full DevOps/CI doctrine. PR39 extracted only the
supported build-observe-adjust operating-loop affordance and preserved absence
records for overclaims.

PR39 does not promote v9 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, create user-facing
Decision Pressure output, or allow deterministic final pressure selection.

PR40 later completed the recommended v8/v9 execution packet usefulness review
with stable nominations. Do not treat PR39 alone as permission for another
extraction batch.

## What PR40 Added

PR40 answers the question: "Did the controlled Batch 8/v9 enrichment make an
execution / implementation / follow-through packet more useful for the next
reasoning actor, or did it merely increase corpus size?"

It adds:

- `tests/fixtures/reasoning_substrate_packet/pr40_v8_execution_followthrough_packet_review.json`;
- `tests/fixtures/reasoning_substrate_packet/pr40_v9_execution_followthrough_packet_review.json`;
- `research/reasoning-substrate-packet-pr40-v8-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr40-v9-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr40-v8-v9-comparison-render-2026-05-07.md`;
- `tests/test_reasoning_substrate_packet_v9_fixture.py`;
- `research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md`;
- `tasks/tasks-v9-execution-packet-usefulness-review.md`;
- living-doc posture updates.

Measured PR40 packet state:

- v8 candidate cards: `12`;
- v9 candidate cards: `12`;
- v8 reviewed cards: `0`;
- v9 reviewed cards: `11`;
- v8 graph-only cards: `12`;
- v9 graph-only cards: `0`;
- v9 weak/conflicting support cards: `1`;
- suppressed duplicates stay fixed at `1`.

PR40's decision label is `v9_execution_packet_handoff_useful`.

The product lesson:

> v9 execution/follow-through depth improves the same packet handoff by adding
> operational checks for baseline, bottleneck, audit trail, failure condition,
> feedback loop, input/output goal separation, bounded iteration,
> validated-learning threshold, procedure handoff, delivery-loop caveat, goal
> side effects, and habit design. The improvement is handoff depth, not final
> answer selection.

`devops-and-continuous-integration` remains the right kind of caveat: it moves
from graph-only to `conflicting_or_weak_support`, not to a full reviewed
DevOps/CI doctrine card.

PR40 does not promote v9 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, extract new records,
create user-facing Decision Pressure output, or allow deterministic final
pressure selection.

PR41 later completed the recommended after-v9 graph-only priority audit. Do
not treat PR40 alone as permission for another extraction batch.

## What PR41 Added

PR41 answers the question: "After v9, which remaining graph-only capability
family is most likely to weaken future reasoning packets, and why should it be
enriched next instead of left graph-only for now?"

It adds:

- `research/v9-graph-only-priority-audit-2026-05-07.md`;
- `tasks/tasks-v9-graph-only-priority-audit.md`;
- living-doc posture updates.

Measured PR41 corpus state:

- runtime graph models: `222`;
- repo-custodied source files: `222`;
- v9 reviewed records: `110`;
- v9 reviewed affordances: `146`;
- v9 absence records: `205`;
- graph-only runtime models after v9: `112`;
- v9 status: `draft_review_only`.

PR41's decision label is `v9_graph_only_priority_audit_complete`.

The product lesson:

> After execution/follow-through depth, the next likely weak packet family is
> risk controls / reversibility / failure containment: the part of "before you
> act" that tests whether plausible and executable advice is contained,
> reversible, monitorable, escalatable, and stoppable.

PR41 recommends a capped PR42 target set:

- `risk-vs-uncertainty`;
- `redundancy`;
- `regulatory-horizon-scanning`;
- `cybersecurity-thinking-models`;
- `non-linear-dynamics`;
- `tipping-points`;
- `butterfly-effect`;
- `chaos-theory`;
- `combinatorial-effects`;
- `critical-mass`;
- `switching-costs`;
- `prospect-theory`.

PR41 does not extract records, promote v9 into runtime, run live lanes, wire
`/lolla`, change prompts, run model calls or judges, create Batch 3b, create
user-facing Decision Pressure output, or allow deterministic final pressure
selection.

PR42 later completed the recommended controlled source-backed extraction batch.
Do not treat PR41 alone as permission for open-ended extraction momentum.

## What PR42 Added

PR42 answers the question: "Can source-backed risk controls / reversibility /
failure-containment records help future reasoning packets test whether
plausible advice is reversible, contained, monitorable, escalatable, and
stoppable?"

It adds:

- `data/model_affordances/batch_9/`;
- `data/compiled/model_affordances/affordances_v10.json`;
- `data/compiled/model_affordances/quality_report_v10.md`;
- `tests/test_pr42_batch9_records.py`;
- `research/pr42-controlled-risk-reversibility-enrichment-report-2026-05-07.md`;
- `tasks/tasks-controlled-risk-reversibility-enrichment-batch.md`;
- living-doc posture updates.

Measured PR42 corpus state:

- runtime graph models: `222`;
- repo-custodied source files: `222`;
- v10 reviewed records: `122`;
- v10 reviewed affordances: `158`;
- v10 absence records: `229`;
- v10 source evidence references: `1749`;
- v10 treatment requirements: `265`;
- v10 diagnostic questions: `568`;
- v10 misuse guards: `543`;
- graph-only runtime models after v10: `100`;
- v10 status: `draft_review_only`.

PR42's decision label is
`controlled_risk_reversibility_enrichment_ready`.

The product lesson:

> Risk/reversibility depth is not generic caution. The useful substrate asks
> the next LLM to size commitments under unknowns, test backups, turn weak
> signals into owners and triggers, map adversarial failure chains, check
> nonlinear loops and thresholds, trace plausible cascades, preserve resilience
> under chaos, identify make-or-break interactions, test critical mass,
> expose reversal costs, and detect loss-framed distortion.

PR42 does not promote v10 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, create user-facing
Decision Pressure output, or allow deterministic final pressure selection.

PR43 later completed the recommended same-nomination v9/v10 packet usefulness
review. Do not treat PR42 alone as permission for another extraction batch.

## What PR43 Added

PR43 answers the question: "Did PR42's risk controls / reversibility /
failure-containment enrichment make the same reasoning packet better handoff
material for a later LLM, or did it merely make the packet heavier?"

It adds:

- `tests/fixtures/reasoning_substrate_packet/pr43_v9_risk_reversibility_packet_review.json`;
- `tests/fixtures/reasoning_substrate_packet/pr43_v10_risk_reversibility_packet_review.json`;
- `research/reasoning-substrate-packet-pr43-v9-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr43-v10-review-render-2026-05-07.md`;
- `research/reasoning-substrate-packet-pr43-v9-v10-comparison-render-2026-05-07.md`;
- `tests/test_reasoning_substrate_packet_v10_fixture.py`;
- `research/reasoning-substrate-v10-packet-usefulness-review-2026-05-07.md`;
- `tasks/tasks-v10-risk-reversibility-packet-usefulness-review.md`;
- living-doc posture updates.

Measured PR43 packet state:

- v9 candidate cards: `12`;
- v10 candidate cards: `12`;
- v9 reviewed cards: `0`;
- v10 reviewed cards: `12`;
- v9 graph-only cards: `12`;
- v10 graph-only cards: `0`;
- suppressed duplicates stay fixed at `1`;
- visible v10 absence records: `12`;
- visible v10 source-evidence refs: `12`;
- v9 fixture size: `1022` lines / `44837` bytes;
- v10 fixture size: `1584` lines / `70179` bytes.

PR43's decision label is `v10_risk_packet_handoff_useful`.

The product lesson:

> v10 risk/reversibility depth improves the same packet handoff by adding
> operational checks for commitment sizing, reversibility decay, fallback
> independence, weak-signal triggers, adversarial failure chains,
> nonlinear-loop monitoring, threshold evidence, plausible cascade paths,
> resilience-over-precision, make-or-break interactions, critical-mass
> density, and loss-frame distortion.

PR43 does not promote v10 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, extract new records,
create user-facing Decision Pressure output, or allow deterministic final
pressure selection.

PR44 later completed the recommended after-v10 graph-only priority audit. Do
not treat PR43 alone as permission for another extraction batch.

## What PR44 Added

PR44 answers the question: "After v10, which remaining graph-only capability
family is most likely to weaken future reasoning packets, and why should it be
enriched next instead of left graph-only for now?"

It adds:

- `research/v10-graph-only-priority-audit-2026-05-07.md`;
- `tasks/tasks-v10-graph-only-priority-audit.md`;
- living-doc posture updates.

Measured PR44 corpus state:

- runtime graph models: `222`;
- repo-custodied source files: `222`;
- v10 reviewed records: `122`;
- v10 reviewed affordances: `158`;
- v10 absence records: `229`;
- graph-only runtime models after v10: `100`;
- v10 status: `draft_review_only`.

PR44's decision label is `v10_graph_only_priority_audit_complete`.

The product lesson:

> After execution, risk, reversibility, trust, communication, and evidence
> depth, the next likely weak packet family is frame correction /
> metacognitive blind-spot discipline: the part of "before you act" that tests
> whether plausible advice is being evaluated through the right frame,
> reasoning mode, evidence boundary, and counterfactual.

PR44 recommends a capped PR45 target set:

- `cognitive-gaps-assessment`;
- `critical-thinking`;
- `counterfactual-reasoning`;
- `metacognitive-questioning`;
- `reasoning-mode-router`;
- `reframing-perspective`;
- `theory-induced-blindness`;
- `einstellung-effect`;
- `dialectical-reasoning`;
- `bias-blind-spot`;
- `false-precision-avoidance`;
- `wysiati`.

PR44 does not extract records, promote v10 into runtime, run live lanes, wire
`/lolla`, change prompts, run model calls or judges, create Batch 3b, create
user-facing Decision Pressure output, create deterministic reasoning-mode
routing, or allow deterministic final pressure selection.

PR45 later completed the recommended controlled source-backed extraction batch.
Do not treat PR44 alone as permission for ongoing extraction momentum.

## What PR45 Added

PR45 answers the question: "Can source-backed frame correction /
metacognitive blind-spot records help future reasoning packets test whether
plausible, executable, and risk-checked advice is still being evaluated through
the wrong frame, evidence boundary, reasoning mode, or counterfactual?"

It adds:

- `data/model_affordances/batch_10/`;
- `data/compiled/model_affordances/affordances_v11.json`;
- `data/compiled/model_affordances/quality_report_v11.md`;
- `tests/test_pr45_batch10_records.py`;
- `research/pr45-controlled-frame-correction-enrichment-report-2026-05-07.md`;
- `tasks/tasks-controlled-frame-correction-enrichment-batch.md`;
- living-doc posture updates.

Measured PR45 corpus state:

- runtime graph models: `222`;
- repo-custodied source files: `222`;
- v11 reviewed records: `134`;
- v11 reviewed affordances: `170`;
- v11 absence records: `253`;
- graph-only runtime models after v11: `88`;
- v11 status: `draft_review_only`;
- schema validation failures: `0`;
- source quote rejections: `0`.

PR45's decision label is `controlled_frame_correction_enrichment_ready`.

The product lesson:

> Frame-correction depth is useful only when it changes the handoff: name the
> missing condition, separate claim/evidence/assumption, recover plausible
> branches, identify the next discriminating question, suggest reasoning mode
> without routing deterministically, change the decision variable, expose what
> the favored framework filters out, interrupt familiar solution lock-in,
> preserve opposing truths, turn bias checks inward, replace fake exactness
> with thresholds, or audit the missing denominator.

PR45 explicitly blocks deterministic reasoning-mode routing. The
`reasoning-mode-router` record is reviewed handoff material for a later
LLM/reviewer, not a new lane, prompt mechanic, runtime router, or case-type
rule.

PR45 does not promote v11 into runtime, run live lanes, wire `/lolla`, change
prompts, run model calls or judges, create Batch 3b, create user-facing
Decision Pressure output, create deterministic reasoning-mode routing, or
allow deterministic final pressure selection.

Recommended next slice, if opened, is PR46: a same-nomination v10/v11 packet
usefulness review for the frame-correction family. PR46 must prove the new
reviewed cards improve handoff quality before any further extraction begins.

## PR24 Review Questions Answered

PR24 review answered yes to all three questions:

1. Does `reasoning_substrate_packet.v1` preserve the distinction between 222
   breadth and 55 v4 depth?
2. Do coverage labels and caps stop the richer v4 layer from silently becoming
   "the only models that matter"?
3. Was skipping a sample fixture the right call because examples could become
   templates too early?

The selected outcome is `stop_and_consolidate`: merge PR24 as dormant
research/infrastructure and pause.

## Historical PR24 Outcomes

PR24 review selected `stop_and_consolidate`. PR25 later reopened forward work
explicitly and only along the corrected enrichment architecture. These PR24
alternatives remain historical labels:

1. `revise_packet_spec`
   Tighten coverage statuses, caps, or forbidden behaviors. No runtime.

2. `static_packet_sample_review`
   Create one tiny dormant sample packet from an archived case to test whether
   the spec is inspectable. No producer, no final pressure, no user-facing
   prose.

3. `pressure_family_coverage_audit`
   Audit which pressure families are under-covered across 222 graph records and
   55 v4 records. No extraction.

4. `stop_and_consolidate`
   Merge PR24 as dormant research/infrastructure and pause. This is the
   selected outcome after PR24 review.

Do not revive these labels as implementation permission by momentum. Current
forward work is controlled enrichment based on packet usefulness, not Decision
Pressure machinery.

## Still Blocked For Live Product

These remain blocked unless explicitly approved after product review:

- live `/lolla`;
- prompt changes;
- lane rewrites;
- runtime packet production from live lanes;
- live Observatory rendering;
- memo / Step 8 / Step 6 integration;
- Lane 4 runtime affordance integration;
- new extraction unless explicitly opened as a controlled reviewed batch;
- broad Batch 3 or Batch 3b;
- paid Gate 4 reruns;
- deterministic pressure selection;
- user-facing Decision Pressure blocks.

## Documentation Hygiene Rule

Future docs must keep the active state unambiguous.

When changing direction, update:

1. `research/reasoning-substrate-next-session-handover-2026-05-06.md`
2. `research/decision-pressure-product-doctrine-2026-05-06.md`
3. `plans/knowledge-substrate-roadmap-2026-05-04.md`
4. `plans/knowledge-use-schema-2026-05-04.md`
5. Any task file created for the slice

Before finishing a docs slice, run a drift scan:

```text
rg -n "controlled_frame_correction_enrichment_ready|v10_graph_only_priority_audit_complete|current posture|next default|Decision Pressure producer|runtime promotion|Batch 3b|PR44|PR45|PR46|PR47" plans research tasks -g '*.md'
```

The goal is not to remove every historical reference. The goal is to make sure
current-state sections, status headers, and "next step" lines do not contradict
the active posture.

## New Session Kickoff

If handing this to a new coder, use:

```text
Start from PR45 and do not infer permission for runtime work, broad
extraction, packet promotion, deterministic reasoning-mode routing, or
automatic extraction momentum.

Read first:
- research/reasoning-substrate-next-session-handover-2026-05-06.md
- research/reasoning-substrate-packet-v1-spec-2026-05-06.md
- research/source-understanding-and-reasoning-packet-audit-2026-05-06.md
- research/reasoning-substrate-lane-placement-audit-2026-05-06.md
- research/full-corpus-enrichment-coverage-audit-2026-05-06.md
- research/reasoning-substrate-source-custody-backfill-2026-05-06.md
- research/reasoning-substrate-packet-fixture-review-2026-05-06.md
- research/pr28-controlled-graph-only-extraction-report-2026-05-06.md
- research/reasoning-substrate-v5-packet-depth-review-2026-05-07.md
- research/reasoning-substrate-packet-review-rendering-2026-05-07.md
- research/reasoning-substrate-packet-comparison-render-2026-05-07.md
- research/v5-reviewed-model-capability-audit-2026-05-07.md
- research/pr32-controlled-capability-gap-enrichment-report-2026-05-07.md
- research/reasoning-substrate-v6-packet-usefulness-review-2026-05-07.md
- research/reasoning-substrate-packet-pr33-v5-v6-comparison-render-2026-05-07.md
- research/pr34-controlled-communication-competition-enrichment-report-2026-05-07.md
- research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md
- research/reasoning-substrate-packet-pr35-v6-v7-comparison-render-2026-05-07.md
- research/pr36-controlled-trust-negotiation-enrichment-report-2026-05-07.md
- research/reasoning-substrate-v8-packet-usefulness-review-2026-05-07.md
- research/reasoning-substrate-packet-pr37-v7-v8-comparison-render-2026-05-07.md
- research/v8-graph-only-priority-audit-2026-05-07.md
- research/pr39-controlled-execution-followthrough-enrichment-report-2026-05-07.md
- research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md
- research/reasoning-substrate-packet-pr40-v8-v9-comparison-render-2026-05-07.md
- research/v9-graph-only-priority-audit-2026-05-07.md
- research/pr42-controlled-risk-reversibility-enrichment-report-2026-05-07.md
- research/reasoning-substrate-v10-packet-usefulness-review-2026-05-07.md
- research/reasoning-substrate-packet-pr43-v9-v10-comparison-render-2026-05-07.md
- research/v10-graph-only-priority-audit-2026-05-07.md
- research/pr45-controlled-frame-correction-enrichment-report-2026-05-07.md

Current posture:
controlled_frame_correction_enrichment_ready

Your first job is to preserve the corrected enrichment boundary and source
custody distinction, not build live Decision Pressure machinery.

PR24 review result:
- verdict: approve_pr24
- selected outcome: stop_and_consolidate

PR25 result:
- decision label: fixture_packet_producer_ready
- existing lanes stay intact
- v4 is additive enrichment
- graph-only models remain eligible
- Python packages reasoning material; LLM/reviewer reasons

PR26 result:
- decision label: source_custody_backfill_complete
- data/model_sources now has source custody for all 222 runtime models
- v4 remains 55 reviewed records
- 167 models remain graph-only after v4
- no extraction or runtime behavior was added

PR27 result:
- decision label: mixed_packet_fixture_useful
- one mixed review-only packet fixture exists
- v4 cards are meaningfully richer than graph-only cards
- source-custodied graph-only cards remain useful but thin
- source custody is visible separately from v4 reviewed depth
- no extraction or runtime behavior was added

PR28 result:
- decision label: controlled_graph_only_extraction_batch_ready
- ten graph-only models received reviewed batch_4 records
- v5 draft/review-only compiled artifact exists with 65 reviewed records
- PR28 added 10 affordances and 20 absence records
- v5 is not runtime-promoted or imported by live runtime paths
- no prompt, lane, live adapter, model call, judge, Batch 3b, or user-facing
  behavior was added

PR29 result:
- decision label: v5_packet_depth_improved
- the PR27 mixed packet was regenerated against v5
- the four PR27 graph-only cards became reviewed cards in the packet
- candidate count stayed 7 and suppressed duplicate count stayed 1
- packet burden grew but remained acceptable for review-only LLM handoff
- no extraction, runtime promotion, prompt, lane, model call, judge, Batch 3b,
  or user-facing behavior was added

PR30 result:
- decision label: packet_review_rendering_ready
- compact reviewer-only Markdown renders now exist for PR27, PR29, and their
  comparison
- renderer output is generated from the dormant packet fixtures and checked by
  tests
- the renderer does not answer the case, choose user-visible output, emit memo
  copy, render HTML, or import into live runtime paths
- no extraction, runtime promotion, prompt, lane, model call, judge, Batch 3b,
  or user-facing behavior was added

PR31 result:
- decision label: v5_capability_audit_complete
- the 65 reviewed records can already support meaningful handoff testing
  across evidence, uncertainty, risk, resource discipline, causal diagnosis,
  incentives, bias, learning, and human-context pressure families
- v5 contains 101 affordances, 115 absence records, 208 treatment
  requirements, 397 diagnostic questions, and 372 misuse guards
- 157 runtime models remain graph-only after v5
- the next production-oriented slice should be a controlled extraction batch
  against named capability gaps, unless product review explicitly chooses a
  receiver-side LLM review first
- no extraction, runtime promotion, prompt, lane, model call, judge, Batch 3b,
  or user-facing behavior was added

PR32 result:
- decision label: controlled_capability_gap_enrichment_ready
- 16 graph-only models from the PR31 capability-gap list received reviewed
  batch_5 records
- v6 draft/review-only compiled artifact exists with 81 reviewed records
- PR32 added 16 affordances and 32 absence records
- v6 contains 117 affordances, 147 absence records, 224 treatment
  requirements, 445 diagnostic questions, and 420 misuse guards
- 141 runtime models remain graph-only after v6
- `batna` is intentionally thin/narrow because the source does not support full
  BATNA doctrine
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, or user-facing behavior was added

PR33 result:
- decision label: v6_packet_handoff_useful
- the same explicit 10-card packet was generated against v5 and v6
- v5 packet: 1 reviewed card, 9 graph-only cards, 1 suppressed duplicate
- v6 packet: 10 reviewed cards, 0 graph-only cards, 1 suppressed duplicate
- v6 improves fallback, counterparty, relative-position, delay, control,
  customer-job, lock-in, path-dependence, and cross-cultural handoff material
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, or user-facing behavior was added

PR34 result:
- decision label: controlled_communication_competition_enrichment_ready
- 7 graph-only models from communication, feedback, strategic
  interdependence, and analogy/adaptive reasoning gaps received reviewed
  batch_6 records
- v7 draft/review-only compiled artifact exists with 88 reviewed records
- PR34 added 7 affordances and 14 absence records
- v7 contains 124 affordances, 161 absence records, 231 treatment
  requirements, 466 diagnostic questions, and 441 misuse guards
- 134 runtime models remain graph-only after v7
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, or user-facing behavior was added

PR35 result:
- decision label: v7_packet_handoff_useful
- the same explicit 9-card communication/competition packet was generated
  against v6 and v7
- v6 packet: 2 reviewed cards, 7 graph-only cards, 1 suppressed duplicate
- v7 packet: 9 reviewed cards, 0 graph-only cards, 1 suppressed duplicate
- v7 improves stable-response, mutual-defection, listening, constructive
  feedback, SBI, analogy-fit, and adaptive-selection handoff material
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, or user-facing behavior was added

PR36 result:
- decision label: controlled_trust_negotiation_enrichment_ready
- 10 graph-only models from trust repair, motivation, boundaries, influence,
  negotiation, and signaling gaps received reviewed batch_7 records
- v8 draft/review-only compiled artifact exists with 98 reviewed records
- PR36 added 10 affordances and 20 absence records
- v8 contains 134 affordances, 181 absence records, 241 treatment
  requirements, 496 diagnostic questions, and 471 misuse guards
- 124 runtime models remain graph-only after v8
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, or user-facing behavior was added

PR37 result:
- decision label: v8_packet_handoff_useful
- the same explicit 10-card trust/negotiation packet was generated against v7
  and v8
- v7 packet: 0 reviewed cards, 10 graph-only cards, 1 suppressed duplicate
- v8 packet: 10 reviewed cards, 0 graph-only cards, 1 suppressed duplicate
- v8 improves repair conversation, emotional landing, hidden motivation,
  boundary, candor, non-malice, reciprocity, persuasion, diplomacy, and
  signaling handoff material
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, or user-facing behavior was added

PR38 result:
- decision label: v8_graph_only_priority_audit_complete
- remaining graph-only runtime models after v8: 124
- PR38 does not extract records; it audits and selects the next controlled
  family
- recommended PR39 family: execution / implementation / follow-through
  discipline
- recommended PR39 target set: algorithmic-thinking,
  auditability-traceability, baseline-establishment, bottlenecks,
  debugging-strategies, devops-and-continuous-integration, feedback-loops,
  goal-setting, habit-formation, input-vs-output-goals, iteration, and
  lean-startup-methodology
- reason: future packets are likely to be thin where plausible AI advice must
  become executable, inspectable, adjustable, and stoppable
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, broad extraction, or user-facing behavior was added

PR39 result:
- decision label: controlled_execution_followthrough_enrichment_ready
- 12 graph-only models from execution / implementation / follow-through
  discipline received reviewed batch_8 records
- v9 draft/review-only compiled artifact exists with 110 reviewed records
- PR39 added 12 affordances and 24 absence records
- v9 contains 146 affordances, 205 absence records, 253 treatment
  requirements, 532 diagnostic questions, and 507 misuse guards
- 112 runtime models remain graph-only after v9
- `devops-and-continuous-integration` is intentionally thin/narrow because the
  source does not support full DevOps/CI doctrine
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, broad extraction, or user-facing behavior was added

PR40 result:
- decision label: v9_execution_packet_handoff_useful
- the same explicit 12-card execution/follow-through packet was generated
  against v8 and v9
- v8 packet: 0 reviewed cards, 12 graph-only cards, 1 suppressed duplicate
- v9 packet: 11 reviewed cards, 0 graph-only cards, 1 weak/conflicting support
  card, 1 suppressed duplicate
- v9 improves baseline, bottleneck, audit trail, debugging, feedback,
  input/output goal, bounded iteration, validated learning, handoff procedure,
  delivery-loop, goal-setting, and habit-design handoff material
- `devops-and-continuous-integration` remains weak/conflicting support rather
  than full DevOps/CI doctrine
- no extraction, runtime promotion, prompt, lane, live adapter, model call,
  judge, Batch 3b, or user-facing behavior was added

PR41 result:
- decision label: v9_graph_only_priority_audit_complete
- remaining graph-only runtime models after v9: 112
- PR41 does not extract records; it audits and selects the next controlled
  family
- recommended PR42 family: risk controls / reversibility / failure containment
- recommended PR42 target set: risk-vs-uncertainty, redundancy,
  regulatory-horizon-scanning, cybersecurity-thinking-models,
  non-linear-dynamics, tipping-points, butterfly-effect, chaos-theory,
  combinatorial-effects, critical-mass, switching-costs, and prospect-theory
- reason: future packets are likely to be thin where plausible and executable
  AI advice must become reversible, contained, monitorable, escalatable, and
  stoppable
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, broad extraction, or user-facing behavior was added

PR42 result:
- decision label: controlled_risk_reversibility_enrichment_ready
- 12 graph-only models from risk controls / reversibility / failure
  containment received reviewed batch_9 records
- v10 draft/review-only compiled artifact exists with 122 reviewed records
- PR42 added 12 affordances and 24 absence records
- v10 contains 158 affordances, 229 absence records, 265 treatment
  requirements, 568 diagnostic questions, and 543 misuse guards
- 100 runtime models remain graph-only after v10
- all PR42 records were extracted from repo-custodied canonical Markdown with
  exact source quotes; no target was rescued with generic mental-model
  knowledge
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, broad extraction, or user-facing behavior was added

PR43 result:
- decision label: v10_risk_packet_handoff_useful
- the same explicit 12-card risk/reversibility packet was generated against v9
  and v10
- v9 packet: 0 reviewed cards, 12 graph-only cards, 1 suppressed duplicate
- v10 packet: 12 reviewed cards, 0 graph-only cards, 1 suppressed duplicate
- v10 improves commitment sizing, reversibility decay, fallback independence,
  weak-signal triggers, adversarial failure chains, nonlinear-loop monitoring,
  threshold evidence, plausible cascade paths, resilience-over-precision,
  make-or-break interactions, critical-mass density, and loss-frame distortion
  handoff material
- no extraction, runtime promotion, prompt, lane, live adapter, model call,
  judge, Batch 3b, or user-facing behavior was added

PR44 result:
- decision label: v10_graph_only_priority_audit_complete
- remaining graph-only runtime models after v10: 100
- PR44 does not extract records; it audits and selects the next controlled
  family
- recommended PR45 family: frame correction / metacognitive blind-spot
  discipline
- recommended PR45 target set: cognitive-gaps-assessment, critical-thinking,
  counterfactual-reasoning, metacognitive-questioning, reasoning-mode-router,
  reframing-perspective, theory-induced-blindness, einstellung-effect,
  dialectical-reasoning, bias-blind-spot, false-precision-avoidance, and
  wysiati
- reason: future packets are likely to be thin where plausible, executable,
  and risk-checked AI advice is still being evaluated through the wrong frame,
  reasoning mode, evidence boundary, or counterfactual
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, broad extraction, deterministic reasoning-mode routing, or user-facing
  behavior was added

PR45 result:
- decision label: controlled_frame_correction_enrichment_ready
- v11 corpus shape: 134 reviewed records, 170 affordances, 253 absence records
- remaining graph-only runtime models after v11: 88
- PR45 added 12 Batch 10 records for frame correction / metacognitive
  blind-spot discipline
- each target received one compact reviewed affordance and two absence records
- `reasoning-mode-router` stays reviewed handoff material, not deterministic
  routing, a new lane, or prompt mechanics
- no runtime promotion, prompt, lane, live adapter, model call, judge, Batch
  3b, broad extraction, deterministic reasoning-mode routing, or user-facing
  behavior was added

Do not build runtime packet production, prompt changes, lane rewrites,
Batch 3b, live Observatory, memo, Step 8, Step 6, Lane 4 runtime, judges,
paid model calls, deterministic pressure selection, or user-facing output
unless the user explicitly opens a new product-reviewed slice. The next proof
slice should be PR46: same-nomination v10/v11 packet usefulness review for the
frame-correction family. Broad extraction is still not justified by count
momentum.
```

## Core Memory

Do not let future momentum erase this:

> The knowledge base is not valuable because it contains many models. It is
> valuable when lane-selected models arrive as compact, source-aware cards that
> improve the next LLM's judgment without pretending Python has judgment.

# Reasoning Substrate Next Session Handover

**Date:** 2026-05-06
**Status:** Start-here handover after PR30 added compact reviewer-only Markdown
renderings for the PR27/PR29 reasoning substrate packets. This makes receiver
review easier without creating runtime behavior, prompt promotion, lane
rewrites, broad Batch 3b, or user-facing Decision Pressure work.

**Current posture:** `packet_review_rendering_ready`

**Current PR:** PR30 - packet receiver-review rendering

**PR24 review verdict:** `approve_pr24`

**PR25 decision label:** `fixture_packet_producer_ready`

**PR26 decision label:** `source_custody_backfill_complete`

**PR27 decision label:** `mixed_packet_fixture_useful`

**PR28 decision label:** `controlled_graph_only_extraction_batch_ready`

**PR29 decision label:** `v5_packet_depth_improved`

**PR30 decision label:** `packet_review_rendering_ready`

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
- deterministic code may dedupe, cap, label coverage, attach graph/v4 snippets,
  preserve provenance, and expose absence records;
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
| Graph-only after v5 | 157 runtime models remain eligible but not reviewed affordance records. |
| PR27 mixed packet fixture | 7 candidate cards plus 1 suppressed duplicate. Review-only proof that mixed v4 + graph-only packets are useful handoff material. |
| PR28 controlled extraction batch | 10 graph-only models gained reviewed records with 10 affordances and 20 absence records. |
| PR29 v5 packet depth review | Same 7-card PR27 fixture regenerated against v5. Reviewed cards increased from 3 to 7, graph-only cards fell from 4 to 0, and packet burden stayed acceptable. |
| PR30 packet review rendering | Deterministic reviewer-only Markdown renders for PR27, PR29, and their comparison. Makes packet review easier; does not select output or create a product surface. |

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
rg -n "stop_and_review_after_pr23|PR24|current posture|next default|Decision Pressure producer|runtime promotion|Batch 3b" plans research tasks -g '*.md'
```

The goal is not to remove every historical reference. The goal is to make sure
current-state sections, status headers, and "next step" lines do not contradict
the active posture.

## New Session Kickoff

If handing this to a new coder, use:

```text
Start from PR30 and do not infer permission for runtime work.

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

Current posture:
packet_review_rendering_ready

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

Do not build runtime packet production, prompt changes, lane rewrites,
Batch 3b, live Observatory, memo, Step 8, Step 6, Lane 4 runtime, judges,
paid model calls, deterministic pressure selection, or user-facing output
unless the user explicitly opens a new product-reviewed slice. The recommended
next step is a receiver-side packet review using the compact renders, ideally
with an explicitly approved external LLM/reviewer, before another small
extraction batch. Broad extraction is still not justified by count momentum.
```

## Core Memory

Do not let future momentum erase this:

> The knowledge base is not valuable because it contains many models. It is
> valuable when lane-selected models arrive as compact, source-aware cards that
> improve the next LLM's judgment without pretending Python has judgment.

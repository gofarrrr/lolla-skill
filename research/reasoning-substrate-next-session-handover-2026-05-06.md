# Reasoning Substrate Next Session Handover

**Date:** 2026-05-06
**Status:** Start-here handover after PR25 reopened forward work along the
corrected PR24 architecture. This is still not runtime promotion, prompt
promotion, lane rewrite, or user-facing Decision Pressure work.

**Current posture:** `fixture_packet_producer_ready`

**Current PR:** PR25 - Reasoning substrate enrichment placement

**PR24 review verdict:** `approve_pr24`

**PR25 decision label:** `fixture_packet_producer_ready`

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
| v4 affordance corpus | 55 reviewed records, 91 affordances, 95 absence records. Deep reviewed subset, still dormant. |
| Graph-only after v4 | 167 runtime models remain eligible but not v4-reviewed. |

The governing sentence:

> 222 gives breadth. v4 gives depth. The packet must preserve both without
> pretending they are the same kind of evidence.

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
- deterministic code packages graph fields, reviewed v4 snippets, absence
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
forward work is enrichment placement and full-corpus packet readiness, not
Decision Pressure machinery.

## Still Blocked For Live Product

These remain blocked unless explicitly approved after product review:

- runtime packet production;
- live `/lolla`;
- prompt changes;
- lane rewrites;
- runtime packet production from live lanes;
- live Observatory rendering;
- memo / Step 8 / Step 6 integration;
- Lane 4 runtime affordance integration;
- new extraction;
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
Start from PR25 and do not infer permission for runtime work.

Read first:
- research/reasoning-substrate-next-session-handover-2026-05-06.md
- research/reasoning-substrate-packet-v1-spec-2026-05-06.md
- research/source-understanding-and-reasoning-packet-audit-2026-05-06.md
- research/reasoning-substrate-lane-placement-audit-2026-05-06.md
- research/full-corpus-enrichment-coverage-audit-2026-05-06.md

Current posture:
fixture_packet_producer_ready

Your first job is to preserve the corrected enrichment boundary, not build live
Decision Pressure machinery.

PR24 review result:
- verdict: approve_pr24
- selected outcome: stop_and_consolidate

PR25 result:
- decision label: fixture_packet_producer_ready
- existing lanes stay intact
- v4 is additive enrichment
- graph-only models remain eligible
- Python packages reasoning material; LLM/reviewer reasons

Do not build runtime packet production, prompt changes, lane rewrites,
extraction, Batch 3b, live Observatory, memo, Step 8, Step 6, Lane 4 runtime,
judges, paid model calls, deterministic pressure selection, or user-facing
output unless the user explicitly opens a new product-reviewed slice.
```

## Core Memory

Do not let future momentum erase this:

> The knowledge base is not valuable because it contains many models. It is
> valuable when lane-selected models arrive as compact, source-aware cards that
> improve the next LLM's judgment without pretending Python has judgment.

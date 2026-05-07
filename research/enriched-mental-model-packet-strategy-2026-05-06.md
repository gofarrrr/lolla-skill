# Enriched Mental Model Packet Strategy

**Date:** 2026-05-06
**Status:** Architecture simplification note after the current-state matching
audit. This is not a runtime implementation, not a new lane, not a prompt
change, and not user-facing promotion.

**Decision label:** `enrich_the_shelves_do_not_solve_the_pressure`

**Source/packet audit brief:** `research/source-understanding-and-reasoning-packet-audit-brief-2026-05-06.md`

**Current source/packet audit:** `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`

**Current packet spec:** `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`

## Core Correction

We should not make the deterministic system solve Decision Pressure.

The simpler architecture is:

> Existing lanes pull the relevant mental-model shelves. Deterministic code
> enriches those shelves into compact, source-backed cards. The next LLM reads
> those cards and does the semantic thinking.

That matches the original spirit better than trying to deterministically decide
which pressure is best.

The deterministic layer should reason about reasoning:

- which tendencies appear to be active;
- which models were present, violated, or relevant;
- which graph neighbors are plausible;
- which reviewed affordance records exist;
- which source-backed constraints are available;
- where coverage is missing.

It should not decide wisdom:

- not the final pressure;
- not the final user-facing wording;
- not novelty or usefulness;
- not case-type templates;
- not semantic merging;
- not whether a pressure is emotionally well-framed.

## Why This Is Simpler

The current system already does candidate narrowing.

Lane 1 narrows through tendency detection and route selection.

Lane 2 narrows through detected/violated mental models in the assistant's
reasoning.

Lane 3 and Lane 4 can add optional shelf hints from framing and structural
coverage, but those should remain candidate inputs, not product surfaces.

The product mistake would be to take these candidate lists and then build
another deterministic machine that tries to select the final "right" pressure.
That is exactly where casuistry enters.

The better move:

> Make the candidate shelves richer, more source-backed, and easier for the
> next LLM to reason with.

## What Must Be Read Together

For candidate shelf recall, the unit of meaning is the transaction:

> user situation + user framing + assistant advice + assistant omissions.

Tendencies often begin in the user's question. The assistant may then amplify
them, inherit them, fail to challenge them, or route around them. Reading only
the assistant answer can miss the original pressure source.

This does not mean every lane must use the same evidence rule.

- For recall, use the broadest relevant transaction context.
- For attribution, keep exact source custody.
- For Lane 2 fingerprints, assistant-only evidence remains correct because
  Lane 2 asks what the assistant's answer did.
- For Lane 3 frame evidence, user-only evidence remains correct because Lane 3
  asks what the user's framing did.
- For candidate enrichment, preserve both the recall reason and the evidence
  source so the next LLM knows what kind of claim it is reading.

The principle:

> Recall broadly. Attribute narrowly. Enrich honestly. Let the LLM synthesize.

## Why Lane 1 And Lane 2 Are A Good Base, But Not The Whole System

Lane 1 and Lane 2 already do important narrowing:

- Lane 1 finds tendency failures and corrective routes across the conversation
  transaction.
- Lane 2 identifies mental models structurally present or violated in the
  assistant answer.

That means we do not need a new deterministic pressure solver to start from
zero. We already have shelves being pulled.

But Lane 1 and Lane 2 do not fully solve the unknown-unknown problem by
themselves:

- Lane 1 can find pressure patterns, but its trusted chunks are still older
  runtime chunks, not the v4 affordance records.
- Lane 2 can explain the assistant's reasoning, but it is intentionally
  assistant-attribution and should not be treated as the whole missing-pressure
  engine.
- Lane 3 and Lane 4 can add useful shelf hints from user framing and uncovered
  dimensions, but their raw outputs should not become the user surface.

The better synthesis is:

> Let the lanes nominate candidate shelves. Let v4 enrich the cards. Let the
> next LLM decide whether any compact pressure emerges.

## What The Enriched Packet Should Be

The packet is not a card shown to users by default.

It is a compact reasoning substrate for the next LLM, Observatory reviewer, or
future memo writer.

For each candidate model, include:

- `model_id`
- `display_name`
- `pulled_by`
  - `lane1_tendency_route`
  - `lane1_neighbor`
  - `lane2_detected_model`
  - `lane2_companion_chunk`
  - `lane3_frame_route`
  - `lane4_gap_route`
- `why_pulled`
  - evidence quote or route reason;
  - triggered tendency;
  - detected reasoning move;
  - gap dimension;
  - frame element.
- `coverage_status`
  - `reviewed_affordance_available`
  - `graph_only_runtime_card`
  - `absence_only`
  - `missing_reviewed_record`
  - `source_too_thin`
  - `conflicting_or_weak_support`
- `v4_affordance_snippets`, when available:
  - `use_when`
  - `do_not_use_when`
  - `case_evidence_needed`
  - `treatment_requirements`
  - `diagnostic_questions`
  - `misuse_guards`
  - `absence_records`
  - `confidence`
  - `source_evidence`
- `graph_context`, when v4 is missing:
  - `select_when`
  - `danger_when`
  - relevant graph neighbors
  - relationship activation condition, if available.

The packet should be small. It should not dump all knowledge for all models.

Normal target:

- 5-12 candidate models total;
- 1-3 high-value affordance snippets per model;
- explicit coverage gaps;
- no user-facing prose.

## What The Next LLM Does

The next LLM should receive:

1. the user situation;
2. the assistant advice;
3. the narrowed/enriched model packet;
4. the output contract.

Then it can decide:

- whether any model matters;
- whether multiple models point to the same pressure;
- whether the pressure is new, a grounded double-down, confirmation, or just
  noise;
- how to phrase the result;
- whether to produce zero output.

That keeps semantic synthesis where it belongs.

## Lane 1 Clarification

The Lane 1 LLM path already reads the full conversation transaction.

Pass 1 and Pass 2 both put user and assistant turns in `SOURCE` and explicitly
allow tendencies to fire through:

- assistant commission;
- assistant omission;
- uncritical acceptance of user framing;
- missed challenge of a user-born tendency.

So the concern that "tendencies are born in the user's question" is directionally
right, but the current Lane 1 prompt path is already trying to handle it.

The remaining mismatch is narrower:

- the embedding tendency "Swiss cheese" recall currently embeds assistant text
  only;
- Lane 2 is intentionally assistant-attribution, so it should not be treated as
  the whole unknown-unknown engine.

If we later touch code, the first candidate correction is not a new pressure
solver. It is to make candidate recall more transaction-aware:

> Use user + assistant transaction text for retrieval where the goal is
> candidate shelf recall; keep assistant-only evidence gates where the goal is
> assistant-attribution.

## Lane 2 Clarification

Lane 2 is useful, but it should be named correctly.

It answers:

> What mental models are already present, violated, or structurally active in
> the assistant's response?

It does not answer:

> What should the user think about that neither the user nor the assistant has
> surfaced?

Lane 2 should therefore feed the enriched packet as an attribution source, not
serve as the whole product intelligence layer.

## Role Of Lane 4

Lane 4 should not become the product surface.

But Lane 4 is still valuable because it asks:

> What structural dimension did the answer not cover?

That is a good source of candidate shelves. The problem was not Lane 4 itself.
The problem was treating raw Lane 4 gap routes/questions as if they were the
thing users should see.

Correct use:

- Lane 4 finds gap dimensions and routed model IDs.
- Deterministic code marks which routed models have v4 affordance coverage.
- The enriched packet gives the next LLM the source-backed records or coverage
  blanks.
- The next LLM decides whether any compact pressure should emerge.

## Deterministic Boundary

Python may:

- gather candidate model IDs from lanes;
- dedupe and cap;
- preserve lane provenance;
- attach v4 affordance snippets when the model has reviewed records;
- attach graph-only fallback fields when no v4 record exists;
- mark missing coverage;
- preserve absence records;
- expose confidence and source evidence;
- produce a review-only packet.

Python must not:

- select the final pressure;
- generate user-facing pressure prose;
- infer pressure from case type;
- convert examples into templates;
- rank tone, usefulness, novelty, or wisdom;
- smooth missing coverage into generic model-name reasoning.

## Practical Next Slice

The next useful slice, when explicitly approved, should be a dormant packet
adapter, not a pressure producer.

Suggested name:

> `reasoning_substrate_packet.v1`

Purpose:

> Given existing lane outputs and `affordances_v4.json`, produce a compact
> review-only packet of enriched candidate mental-model cards for an LLM or
> reviewer.

This should be tested only for mechanical properties:

- candidate IDs are lane-derived;
- v4 snippets are attached only when records exist;
- graph-only fallback is labeled as graph-only;
- missing records are explicit;
- caps hold;
- packet contains no final pressure prose;
- packet is runtime-dormant.

It should not test:

- whether the "right" model was selected;
- whether the "right" pressure emerges;
- whether one case type maps to one model.

## Product Translation

The product is not:

> A deterministic pressure solver.

The product is closer to:

> A rich, source-backed reasoning substrate that lets a strong LLM notice the
> operational pressure the user may not know to ask about.

This keeps the system broad and pragmatic.

It lets us expand the knowledge base without pretending that every new record
needs a deterministic place in a final decision tree.

The question for expansion becomes:

> Which model records make the packet more useful for thinking?

Not:

> Which model records let Python decide the answer?

## Approved Continuation

The May 6 continuation decision approved the first version of this work as a
docs/research slice:

> Source Understanding And Reasoning Packet Audit

That slice should first audit what the 222-model runtime graph already knows,
what v4 adds beyond the graph for its 55 reviewed records, and what shape a
`reasoning_substrate_packet.v1` should take before any runtime adapter exists.

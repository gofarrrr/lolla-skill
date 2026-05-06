# Source Understanding And Reasoning Packet Audit Brief

**Date:** 2026-05-06
**Status:** Next-slice brief after explicit product/architecture review. This
is not a runtime implementation, not live `/lolla`, not a new lane, not a
Decision Pressure producer, not prompt wiring, and not user-facing promotion.

**Decision label:** `reasoning_substrate_packet_audit_ready`

**Doctrine anchor:** `pull_shelves_enrich_cards_let_llm_reason`

## Why This Slice Exists

The PR13-PR23 stack helped us find a compact Decision Pressure surface, but the
better architecture is now clearer:

> Stop trying to make Decision Pressure the deterministic object.
> Make the reasoning substrate packet the deterministic object.
> Let the LLM decide whether Decision Pressure emerges.

The existing lane system already narrows the problem. We should not disturb it
without evidence.

The next job is to understand how v4 fits as an additive enrichment layer over
what the lanes already surface, and how to expand beyond the 55 reviewed records
without losing the breadth of the 222-model runtime graph.

## Current Substrate Facts

Measured from the current repo and canonical source directory:

| Layer | Count / shape | Current role |
| --- | ---: | --- |
| Canonical markdown files | 222 files | Source truth behind the runtime model graph |
| Canonical source size | about 491k words | Broad source material, too large for direct runtime use |
| Runtime model graph | 222 models | Active broad model shelf |
| Runtime tendencies | 25 | Lane 1 tendency detection |
| Runtime `select_when` items | 874 | Broad activation hints |
| Runtime `failure_modes` | 678 | Broad misuse/failure hints |
| Runtime `premortem_questions` | 674 | Broad challenge/question hints |
| Runtime `heuristics` | 680 | Broad action/playbook hints |
| Runtime `danger_when` items | 453 | Broad caution hints |
| v4 reviewed records | 55 model records | Deep reviewed affordance subset |
| v4 reviewed affordances | 91 affordances | Source-backed operational constraints |
| v4 absence records | 95 absence records | Coverage honesty / do-not-promote evidence |
| Graph-only models after v4 | 167 models | Broad runtime candidates without reviewed v4 depth |

Reasoning-type coverage also shows why the 55 cannot become the whole story:

| Reasoning type | Runtime models | v4 reviewed | Graph-only |
| --- | ---: | ---: | ---: |
| diagnostic | 102 | 19 | 83 |
| systems | 87 | 25 | 62 |
| metacognitive | 77 | 13 | 64 |
| causal | 77 | 16 | 61 |
| probabilistic | 34 | 17 | 17 |
| counterfactual | 27 | 11 | 16 |
| deductive | 26 | 6 | 20 |
| analogical | 18 | 3 | 15 |
| abductive | 5 | 1 | 4 |

The right interpretation:

> 222 gives breadth.
> v4 gives depth.
> The packet must preserve both without pretending they are the same kind of
> evidence.

## Product And Architecture Thesis

The knowledge base is not valuable because it contains many models.

It is valuable when lane-selected models arrive as compact, source-aware cards
that improve the next LLM's judgment without pretending Python has judgment.

The deterministic system should provide a repeatable offering:

> Here is what we found.
> Here is why it was pulled.
> Here is what the reviewed source says.
> Here is what is graph-only.
> Here is what is missing.
> Here is what should not be overclaimed.
> Now reason.

## The Missing Object

The missing bridge is:

> `reasoning_substrate_packet.v1`

Plain name:

> enriched mental-model card packet

It is a dormant, non-user-facing substrate object.

It should contain candidate material for the LLM. It should not contain the
final pressure, final memo wording, or user-facing prose.

## Proposed Packet Shape

Top-level packet:

- `packet_version`
- `runtime_policy`
  - `draft_review_only`
  - `runtime_dormant`
- `transaction_context`
  - user situation summary
  - assistant advice summary
  - live constraints
  - capture health
- `candidate_cards`
- `suppressed_candidates`
- `coverage_summary`
- `packet_policy`
- `blocked_surfaces`

Candidate card:

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
  - source lane
  - route reason
  - evidence quote or route evidence
  - evidence source type: `user_turn`, `assistant_turn`, `lane_gap`,
    `graph_recall`, `embedding_recall`, `reviewer_note`
- `coverage_status`
  - `v4_reviewed_affordance_available`
  - `graph_only_runtime_card`
  - `absence_only`
  - `missing_reviewed_record`
  - `source_too_thin`
  - `conflicting_or_weak_support`
- `runtime_graph_fields`
  - `select_when`
  - `danger_when`
  - `failure_modes`
  - `premortem_questions`
  - `heuristics`
  - `reasoning_types`
- `reviewed_affordance_fields`, when v4 exists
  - `use_when`
  - `do_not_use_when`
  - `case_evidence_needed`
  - `treatment_requirements`
  - `diagnostic_questions`
  - `misuse_guards`
  - `source_evidence`
  - `confidence`
- `absence_records`, when relevant
- `do_not_overclaim`
- `llm_instruction`
  - consider, merge, set aside, or ignore;
  - do not force use;
  - do not treat graph-only as reviewed;
  - do not invent source-backed constraints.

Normal packet target:

- 5-12 candidate cards total;
- 1-3 high-value snippets per card;
- explicit coverage status per card;
- no final pressure selection;
- no user-facing prose.

## How This Fits The Existing Lanes

This slice should not rewrite the lane system.

Expected lane fit:

1. **Lane 1**
   Candidate shelf source for tendency failures and corrective routes. Its LLM
   path already reads the conversation transaction. A future code slice may
   consider transaction-aware embedding recall, but this audit should not change
   runtime behavior.

2. **Lane 2**
   Candidate shelf source for models present, violated, or structurally active
   in the assistant answer. Assistant-only attribution should remain intact.

3. **Lane 3**
   Optional shelf source for user-framing pressure. User-only frame evidence
   should remain intact.

4. **Lane 4**
   Optional shelf source for structural gaps. Its raw questions are not the
   product surface; its routed model IDs can become packet candidates.

The rule:

> Recall broadly. Attribute narrowly. Enrich honestly. Let the LLM synthesize.

## What v4 Adds

v4 should be valuable only when it gives the LLM better material than the broad
runtime graph alone.

The v4 delta audit should compare:

- runtime `select_when` vs v4 `activation_shape.use_when`;
- runtime `danger_when` vs v4 `activation_shape.do_not_use_when` and
  `misuse_guards`;
- runtime `premortem_questions` vs v4 `diagnostic_questions`;
- runtime `heuristics` vs v4 `treatment_requirements`;
- runtime source references vs v4 exact `source_evidence`;
- runtime broad utility vs v4 operational constraints and absence records.

The question is not:

> Is v4 more detailed?

The question is:

> Does v4 give the next LLM better judgment material than the runtime graph
> alone?

## Expansion Beyond 55

Do not enrich all 222 blindly.

Do not let the 55 v4 records swallow the other 167 graph-only models.

The expansion rule:

> Even pressure-family coverage, uneven model depth.

Expansion should be pulled by:

1. Lane-selected candidates that repeatedly appear as `graph_only_runtime_card`.
2. Repeated coverage gaps where the LLM needs source-backed operational
   constraints.
3. Pressure families that are under-covered by v4 but common in lane recall.
4. High-value source likelihood:
   - do-not-use conditions;
   - evidence requirements;
   - misuse guards;
   - treatment requirements;
   - dismissal logic;
   - operational tripwires;
   - absence records.
5. Trust risk:
   - models that frequently appear but would be dangerous if overclaimed.

Expansion should not be pulled by:

- model count completion;
- making every family look symmetrical;
- pressure examples from PR13/PR23 alone;
- generic model popularity;
- the desire to avoid coverage blanks.

## First Audit Questions

The next slice should answer four questions.

1. **What do we already have across all 222?**
   Inventory current runtime graph fields and reason about pressure-family
   coverage.

2. **What does v4 add beyond the runtime graph?**
   Compare the 55 reviewed records against their graph cards and identify the
   actual value delta.

3. **What should the LLM packet look like?**
   Define `reasoning_substrate_packet.v1` as a dormant contract or spec, not as
   runtime behavior.

4. **Can one sample packet stay small and useful?**
   Use one archived case or fixture. Build a no-runtime sample packet that shows
   what the LLM would receive. Do not generate the final pressure.

## Allowed Work

Allowed:

- docs/research artifacts;
- deterministic corpus inventory scripts or throwaway analysis;
- dormant schema/spec draft;
- sample packet fixture from archived artifacts;
- no-runtime packet smoke review;
- living-doc updates that clarify the new direction.

Not allowed:

- live `/lolla`;
- prompt changes;
- lane rewrites;
- runtime promotion;
- Decision Pressure producer;
- user-facing prose generation;
- package function for product use;
- broad Batch 3 / Batch 3b extraction;
- paid model calls;
- judge calls;
- deterministic pressure selection.

## Success Criteria

The slice succeeds if it produces a clear answer to:

> Can the existing lane system produce candidate shelves that can be enriched
> into a compact, source-aware packet for the next LLM?

Specific pass bars:

- The audit distinguishes 222 runtime breadth from 55 v4 depth.
- The packet spec keeps v4 additive, not replacing lane matching.
- Graph-only models remain eligible but honestly labeled.
- v4-reviewed cards show their real delta over graph fields.
- The sample packet stays compact and non-user-facing.
- No deterministic code selects the final pressure.
- Expansion beyond 55 is guided by packet/coverage need, not count completion.

Failure bars:

- The packet becomes a final pressure object.
- The sample fixture imitates PR13/PR23 examples as templates.
- v4 records are treated as the only eligible models.
- graph-only records are presented as source-reviewed.
- the packet is too large for an LLM to use cleanly.
- Python begins scoring wisdom, novelty, tone, or final actionability.

## Recommended Next PR Shape

Suggested PR title:

> PR24 - Source Understanding And Reasoning Packet Audit

Suggested branch:

> `feature/reasoning-substrate-pr24-source-packet-audit`

Suggested deliverables:

1. `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`
2. `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`
3. optional `tests/fixtures/reasoning_substrate_packet/...` sample packet if a
   fixture is useful;
4. living-doc updates to roadmap/schema/doctrine.

This is forward motion, but still the right kind: substrate and handoff, not
runtime product promotion.

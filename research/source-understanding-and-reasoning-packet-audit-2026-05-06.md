# Source Understanding And Reasoning Packet Audit

**Date:** 2026-05-06
**Status:** Docs/research artifact for the approved safe slice after PR23. No
runtime behavior changed. No prompts changed. No lane rewrites happened. No
model calls, judge calls, extraction, Batch 3b, Observatory work, `/lolla`
behavior, or user-facing Decision Pressure work happened.

**Decision label:** `source_understanding_packet_audit_complete`

**Companion spec:** `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`

## Question

What is actually inside the existing knowledge substrate, and how should it be
handed to the next LLM without making Python pretend to have judgment?

## Answer

The current substrate has broad lightweight structured coverage across all 222
runtime models and deeper reviewed affordance coverage for 55 of them.

The right next object is not a deterministic Decision Pressure solver. The
right next object is a dormant `reasoning_substrate_packet.v1`: a compact packet
of enriched candidate cards for the next LLM or reviewer.

Core doctrine:

> Broad intake, disciplined output.
> Pull shelves, enrich cards, let the LLM reason.
> Python guards rails. Python does not decide wisdom.

## Non-Goals

This audit does not authorize:

- runtime behavior;
- live `/lolla`;
- prompt changes;
- lane rewrites;
- a Decision Pressure producer;
- user-facing pressure output;
- Observatory, memo, Step 8, Step 6, or Lane 4 wiring;
- new extraction;
- broad Batch 3 or Batch 3b;
- paid model calls;
- judge calls;
- deterministic semantic pressure selection.

## Method

This audit used local artifacts only:

- `data/knowledge_graph.json`
- `data/compiled/model_affordances/affordances_v4.json`
- `data/model_sources/manifest.json`
- `data/curated/compiled_chunks.json`
- `/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/*.md`
- existing lane code for read-only boundary confirmation

No helper file was added. Counts were gathered with one-off local shell/Python
inspection.

## Runtime Graph Inventory

`data/knowledge_graph.json` already carries broad structured understanding for
the full runtime model graph.

| Runtime substrate item | Count |
| --- | ---: |
| Runtime models | 222 |
| Runtime tendencies | 25 |
| Relationship/graph edges | 1,742 |
| Prerequisite edges | 15 |
| Structural coverage dimensions | 15 |
| Reframing patterns | 15 |

All 222 runtime model records include the main broad graph fields.

| Runtime graph field | Models with field | Total items |
| --- | ---: | ---: |
| `select_when` | 222 | 874 |
| `danger_when` | 222 | 453 |
| `failure_modes` | 222 | 678 |
| `premortem_questions` | 222 | 674 |
| `heuristics` | 222 | 680 |
| `reasoning_types` | 222 | 453 |

This matters because the 222-model graph is not just labels. It already
contains broad activation hints, failure hints, premortem prompts, heuristics,
danger conditions, and reasoning-type tags.

## Reasoning-Type Coverage

v4 has useful depth, but it cannot become the whole story. Reasoning-type
coverage shows the current imbalance.

| Reasoning type | Runtime models | v4 reviewed | Graph-only |
| --- | ---: | ---: | ---: |
| diagnostic | 102 | 19 | 83 |
| systems | 87 | 25 | 62 |
| causal | 77 | 16 | 61 |
| metacognitive | 77 | 13 | 64 |
| probabilistic | 34 | 17 | 17 |
| counterfactual | 27 | 11 | 16 |
| deductive | 26 | 6 | 20 |
| analogical | 18 | 3 | 15 |
| abductive | 5 | 1 | 4 |

Interpretation:

- v4 is comparatively stronger in probabilistic/counterfactual coverage.
- v4 is still thin relative to diagnostic, systems, causal, and metacognitive
  breadth.
- graph-only does not mean useless; it means not reviewed under the v4
  affordance/source-custody standard.

## Canonical Markdown Source Shape

The canonical source directory contains broad source material:

`/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/`

| Corpus property | Value |
| --- | ---: |
| Markdown files | 222 |
| Approximate word count | 491,170 |
| Mean words per file | 2,212.5 |
| Median words per file | 2,198 |
| Minimum words in a file | 734 |
| Maximum words in a file | 3,272 |

The files are not uniformly formal Markdown heading documents, but they do
follow a consistent briefing pattern.

| Section pattern | Files where present |
| --- | ---: |
| Core Principles | 222 |
| Playbook in Action | 222 |
| Application Context | 222 |
| Strengths | 222 |
| Weaknesses | 222 |
| Latticework | 222 |
| Structured Tension | 222 |
| Risks and Mitigations | 222 |
| Premortem / Pre-mortem | 220 |
| Danger | 219 |
| Anti-Pattern | 214 |

The source files are closer to operational briefings than generic definitions.
They commonly include:

- where the model is useful;
- where it is dangerous;
- anti-patterns;
- risks and mitigations;
- structured tensions;
- premortem or mitigation questions;
- interactions with neighboring models.

This supports broad future expansion, but not blind all-222 extraction.

## v4 Depth Inventory

`data/compiled/model_affordances/affordances_v4.json` remains a reviewed,
dormant corpus:

| v4 item | Count / value |
| --- | ---: |
| Status | `draft_review_only` |
| Reviewed model records | 55 |
| Reviewed affordances | 91 |
| Absence records | 95 |
| Source files in `data/model_sources/manifest.json` | 55 |
| v4 model IDs outside runtime graph | 0 |
| Runtime graph-only models after v4 | 167 |

The reviewed affordance confidence/status shape is narrow and mostly strong:

| v4 confidence/status item | Count |
| --- | ---: |
| High-confidence affordances | 88 |
| Medium-confidence affordances | 3 |
| Absence records: `not_supported_by_source` | 44 |
| Absence records: `duplicate_of_existing_field` | 36 |
| Absence records: `source_too_thin` | 14 |
| Absence records: `deferred_for_review` | 1 |

v4 is useful because it adds source-backed operational discipline:

- exact source evidence;
- reviewed source custody;
- `activation_shape.use_when`;
- `activation_shape.do_not_use_when`;
- `case_evidence_needed`;
- `treatment_requirements`;
- `diagnostic_questions`;
- `misuse_guards`;
- confidence;
- absence records.

It should remain visibly different from runtime graph breadth.

## Representative Runtime-v4 Delta

### Opportunity Cost

Runtime graph breadth:

- 4 `select_when` items;
- 2 `danger_when` items;
- 3 `failure_modes`;
- 3 `premortem_questions`;
- 3 `heuristics`;
- counterfactual reasoning tag.

v4 reviewed depth:

- affordance:
  `opportunity-cost.displaced-alternative-commitment-gate`;
- reviewed use conditions around scarce people, budget, launch window, or
  attention;
- do-not-use cautions against poorly framed or unrealistic alternatives;
- evidence requirement to name the best real displaced alternative;
- treatment requirement to translate the displacement into concrete lost work,
  learning, fallback, or capability;
- misuse guard against endless comparison after a bounded reversible test.

Delta:

The runtime graph can recall the shelf. v4 makes the shelf operational enough
for the next LLM to ask what the current "yes" displaces and when the comparison
should stop.

### Principal-Agent Problem

Runtime graph breadth:

- 4 `select_when` items;
- 2 `danger_when` items;
- 3 `failure_modes`;
- 3 `premortem_questions`;
- 3 `heuristics`;
- systems reasoning tag.

v4 reviewed depth:

- affordance:
  `principal-agent-problem.delegated-alignment-drift-audit`;
- medium-confidence caution preserved by earlier Decision Pressure work;
- evidence requirements around principal, agent, task, outcome owner,
  incentive divergence, and information asymmetry;
- treatment requirements around checkpoint design, hidden effort, role clarity,
  and accountability;
- misuse guards against bad-faith framing and micromanagement theater.

Delta:

The runtime graph can recall delegation and incentive risk. v4 adds caution:
use the model only when the case evidence supports incentive drift, and do not
turn every delegation problem into bad faith.

### Probabilistic Thinking

Runtime graph breadth:

- 4 `select_when` items;
- 2 `danger_when` items;
- 3 `failure_modes`;
- 3 `premortem_questions`;
- 3 `heuristics`;
- metacognitive reasoning tag.

v4 reviewed depth:

- affordance:
  `probabilistic-thinking.range-and-sensitivity-decision-gate`;
- use conditions around uncertainty that changes commitment;
- evidence requirements for ranges, sensitivity checks, tail downside, and
  update thresholds;
- treatment requirements around decision-relevant ranges rather than exact
  numbers;
- misuse guards against false precision and probability language that merely
  postpones commitment.

Delta:

The runtime graph can recall uncertainty discipline. v4 makes the check
decision-shaped: does probability language change action, or is it delaying
commitment?

## Representative Graph-Only Value

Several high-signal models remain graph-only after v4. Examples include:

- `batna`;
- `game-theory-payoffs`;
- `chain-of-verification`;
- `confirmation-bias`;
- `status-quo-bias`;
- `commitment-bias`;
- `authority-bias`;
- `false-precision-avoidance`;
- `auditability-traceability`.

`chain-of-verification` is especially important as a warning against v4
tunnel vision. It is graph-only, but its canonical source and runtime graph
fields contain high-value reasoning material: verification can prevent weak-link
failure, but it can also become theater or delay action without changing the
decision.

If a lane repeatedly pulls this shelf, the packet should include it as
`graph_only_runtime_card`, not ignore it merely because v4 is missing.

## Existing Lane Fit

This audit does not require lane rewrites.

Existing lanes already nominate candidate shelves:

- Lane 1 detects tendency pressure and corrective routes. Its LLM path already
  reads the user/assistant transaction. Its embedding tendency recall is the
  narrower place where transaction-aware recall may later matter.
- Lane 2 attributes models present or violated in the assistant answer.
  Assistant-only evidence remains correct for Lane 2 attribution.
- Lane 3 detects user-framing pressure. User-only frame evidence remains
  correct for Lane 3.
- Lane 4 detects structural coverage gaps and routes to candidate model
  shelves. Raw Lane 4 questions are not the product surface.

The packet should sit after shelf recall:

1. lanes nominate candidate shelves;
2. deterministic code dedupes, caps, labels coverage, and enriches cards;
3. the LLM or reviewer performs semantic synthesis;
4. Decision Pressure may emerge, or no output may be correct.

Rule:

> Recall broadly. Attribute narrowly. Enrich honestly. Let the LLM synthesize.

## Reasoning Packet Implications

The packet should preserve both knowledge layers:

- 222-model runtime graph gives breadth and unknown-unknown recall.
- v4 reviewed affordances give depth and operational discipline.

The packet must not collapse those layers into one evidence class.

Recommended card statuses:

- `reviewed_affordance_available`;
- `graph_only_runtime_card`;
- `absence_only`;
- `missing_reviewed_record`;
- `source_too_thin`;
- `conflicting_or_weak_support`.

Recommended normal packet target:

- 5-12 candidate cards;
- 1-3 high-value snippets per card;
- explicit coverage status per card;
- no final pressure;
- no user-facing prose.

## Expansion Beyond 55

The correct expansion rule is:

> Even pressure-family coverage, uneven model depth.

Do not expand v4 blindly across all 222 canonical files.

Do expand when packet usefulness or repeated lane evidence shows a gap:

- a graph-only model repeatedly appears in lane-selected shelves;
- a pressure family is lopsided or under-covered;
- graph-only material is too easy to overclaim;
- source evidence likely contains high-value use/do-not-use/evidence/misuse
  fields;
- absence records would prevent fake confidence;
- a missing reviewed card would materially improve the next LLM's handoff.

Likely pressure families to monitor:

- evidence quality;
- incentives and principal-agent dynamics;
- uncertainty and probability;
- opportunity cost and resource allocation;
- risk, reversibility, and margin of safety;
- governance and stakeholder trust;
- safety and harm prevention;
- timing, sequencing, and commitment;
- competitive dynamics;
- communication and relationship repair;
- learning and exploration;
- systems behavior and feedback loops.

The goal is not equal model depth. The goal is enough pressure-family coverage
that the packet can offer broad candidate shelves without pretending graph-only
cards are reviewed affordances.

## Risks And Falsifiers

The direction is wrong if:

- the packet grows into a library dump;
- v4 depth causes the system to ignore the other 167 graph-only runtime models;
- graph-only fields are presented as reviewed affordance evidence;
- absence records disappear because they feel unhelpful;
- Python begins choosing pressure quality;
- Python infers pressures from case type, route label, keyword, or example
  similarity;
- PR23 examples become deterministic templates;
- packet fields contain final pressure prose;
- the LLM is pushed to use every card;
- expansion becomes "complete all 222" instead of pressure-family and
  packet-usefulness driven.

## Optional Sample Packet Decision

No separate static sample packet fixture was created in this slice.

Reason:

- the slice needed a corpus audit and packet spec first;
- a one-case sample fixture could accidentally become a de facto template
  before reviewers accept the packet shape;
- `research/reasoning-substrate-packet-v1-spec-2026-05-06.md` already includes
  two non-normative card fragments that show the key distinction:
  v4-reviewed depth vs graph-only breadth;
- no final pressure selection or user-facing prose should appear in this phase.

If reviewers explicitly ask for a later sample, it should remain static,
dormant, and non-user-facing.

## Decision

`source_understanding_packet_audit_complete`

Findings:

- the 222-model runtime graph is broad enough to remain the candidate shelf
  base;
- v4 is deep enough to enrich reviewed shelves, but too narrow to become the
  whole matching substrate;
- canonical markdown files appear structured enough to support future
  pressure-family expansion;
- the missing bridge is a dormant enriched-card packet, not a deterministic
  pressure selector;
- future extraction should be pulled by packet usefulness and pressure-family
  gaps, not corpus-count ambition.

## Recommendation

Treat `reasoning_substrate_packet.v1` as the next reviewed handoff shape.

Do not implement runtime packet production from this audit alone. Do not change
lanes. Do not change prompts. Do not expand v4 records blindly. Do not build a
Decision Pressure producer.

The next product/architecture question, if explicitly approved, should be
whether a tiny dormant sample or validation slice helps reviewers inspect the
packet shape. It should not be live `/lolla`, live Observatory, prompt wiring,
or deterministic semantic selection.

# Knowledge Matching Current-State Audit

**Date:** 2026-05-06
**Status:** Historical product/architecture audit after the merged PR13-PR23
stack and Decision Pressure product doctrine. The architecture conclusions
still stand, but the reviewed affordance counts have been superseded by later
controlled enrichment and packet-review slices through PR48. This is not a
runtime proposal, not an extraction brief, not a prompt change, and not
user-facing promotion.

**Doctrine anchor:** `broad_intake_disciplined_output`

**Current posture:** `controlled_adaptive_exploration_enrichment_ready`

**Current handover:** `research/reasoning-substrate-next-session-handover-2026-05-06.md`

**Source/packet audit brief:** `research/source-understanding-and-reasoning-packet-audit-brief-2026-05-06.md`

**Current source/packet audit:** `research/source-understanding-and-reasoning-packet-audit-2026-05-06.md`

**Current packet spec:** `research/reasoning-substrate-packet-v1-spec-2026-05-06.md`

## Executive Read

The current system has two different knowledge substrates that should not be
collapsed into one story.

1. **Runtime substrate**
   The active lanes use the compiled graph/chunk/embedding artifacts:
   `data/knowledge_graph.json`, `data/relationship_graph.json`,
   `data/curated/compiled_chunks.json`, and `data/embeddings.db`. The runtime
   code expects these under `root/build/...`; `scripts/run_pipeline.py` creates
   a temporary `build -> data` symlink so the packaged skill data is loaded.

2. **Reviewed affordance substrate**
   At the time of this audit, the v4 affordance corpus had `55` reviewed
   source-backed model records. After later controlled enrichment through PR48,
   the current draft/review-only v12 corpus has `146` reviewed records, `182`
   affordances, and `277` absence records. PR40 showed the v9 execution cards
   improve one stable-nomination packet handoff. PR41 then audited the
   remaining graph-only set and selected risk controls / reversibility /
   failure containment as the next controlled family. PR42 added source-backed
   depth for those 12 models while keeping v10 runtime-dormant. PR43 then
   showed that v10 improves the same 12-card risk/reversibility packet handoff
   without changing candidate count. PR44 then audited the remaining 100
   graph-only models and selected frame correction / metacognitive blind-spot
   discipline as the next controlled family. PR45 added source-backed v11 depth
   for those 12 models while explicitly preserving the no deterministic
   reasoning-mode-routing boundary. PR46 then showed that v11 improves the
   same 12-card frame-correction packet handoff without changing candidate
   count. PR47 then audited the remaining 88 graph-only models and selected
   adaptive exploration / option generation / synthesis discipline as the next
   controlled family. PR48 added source-backed v12 depth for those 12 models
   while preserving the no deterministic option-selection boundary. The corpus
   is richer and more operational, but it is still `draft_review_only`. It
   supports review artifacts; it does not yet select or generate live
   pressures.

So the accurate current claim is:

> Lolla has a 222-model runtime graph and a growing reviewed affordance corpus.
> After PR48, the reviewed corpus has 146 records. PR40 showed v9 improved one
> execution/follow-through packet handoff; PR42 added v10 risk/reversibility
> depth for the family PR41 selected; PR43 showed that v10 improves one
> risk/reversibility packet handoff; PR44 selected frame correction /
> metacognitive blind-spot discipline as the next controlled family; PR45 added
> v11 depth for that family while blocking deterministic reasoning-mode
> routing; PR46 showed that v11 improves one frame-correction packet handoff;
> PR47 selected adaptive exploration / option generation / synthesis discipline
> as the next controlled family from the remaining 88 graph-only models; PR48
> added v12 depth for that family while blocking deterministic option
> selection.
> It is still not the live matching system.

This matters because expanding from 55 records should not mean "add records
until the number feels complete." Expansion should be pulled by product use:
which lane-nominated mental-model shelves need richer source-backed cards so a
next LLM can think better without Python pretending to choose the pressure.

## Corpus Shape

Measured from the repo artifacts when this audit was first written. For the
current v12 counts and packet-review posture, use the handover, PR39 report,
PR40 review, PR41 audit, PR42 report, PR43 review, PR44 audit, PR45 report,
PR46 review, PR47 audit, and PR48 report.

| Artifact | Count / state | Current role |
| --- | ---: | --- |
| Runtime model graph | 222 models | Active runtime routing substrate |
| Tendencies | 25 | Lane 1 Pass 1 / Pass 2 tendency detection |
| Knowledge graph edges | 1,742 | Model/tendency/relation routing input |
| Prerequisite edges | 15 | Companion cheat-sheet prerequisite gaps |
| Structural dimensions | 15 | Lane 4 gap detection/routing |
| Reframing patterns | 15 | Lane 3 frame routing |
| Relationship graph edges | 1,358 | Supporting/risk neighbor selection |
| Compiled chunks | 242 chunks across 63 models | Lane 1 trusted pressure bundle content |
| Embedding `model_signals` | 444 | Model recall/reranking |
| Embedding `tendency_guidance` | 25 | Lane 1 embedding tendency recall |
| Embedding `chunk_embeddings` | 2,032 | Companion cheat-sheet chunk reranking |
| Embedding `edge_activation_conditions` | 867 | Relation-graph near-tie activation tiebreaker |
| v4 affordance records | 55 model records | Dormant reviewed Decision Pressure substrate |
| v4 affordances | 91 | Source-backed operational affordances |
| v4 absence records | 95 | Coverage honesty / do-not-promote evidence |
| Reviewed source files | 55 markdown files | Source custody for v4 records |

The v4 corpus is not "55 mental models used by the live skill." It is 55
reviewed canonical sources that can support source-backed operational pressure
when a reviewer/LLM synthesis layer selects pressure. The live runtime still
uses the broader 222-model graph and older compiled chunks.

## What The Runtime Actually Reads

The runtime entry shape is `ConversationContext`.

It contains:

- full parsed conversation turns from the transcript;
- extracted `decision_situation`;
- extracted `original_framing`;
- extracted live constraints;
- extracted dropped threads;
- extraction/capture health metadata.

`conversation_loader.py` parses turns from transcript markers such as
`[Turn 1] USER:` and `[Turn 2] ASSISTANT:`. `ir_constructor.py` then builds a
`ConversationIR`. The IR supports exact span provenance, turn-level provenance,
and derived/paraphrased provenance.

Current nuance:

- user and assistant turns are available to all packet-driven lanes;
- extractor summaries are scaffolding, not always exact evidence;
- the default IR constructor often uses `turn_ref` or `derivation` provenance
  for high-level summaries, not full fine-grained span graphs;
- capture truncation can happen before the pipeline sees the conversation, and
  `scripts/run_pipeline.py` records that in run health.

So the system is conversation-first, but not yet a full semantic memory over
every sentence/chunk. It has full turns, plus selected extracted summaries, plus
lane-specific evidence rules.

## Lane-By-Lane Matching

### Lane 1: Tendency And Pressure Routing

Lane 1 is the older pressure lane. It asks: "Which Munger-style tendencies or
failure patterns are present in the conversation transaction?"

Inputs:

- `ConversationContext`;
- `ConversationIR`;
- user + assistant turns for Pass 1 and Pass 2 LLM checks;
- assistant turns for the current embedding tendency "Swiss cheese" signal;
- user + assistant text for semantic model reranking;
- 25 tendencies from the knowledge graph;
- relation graph and compiled chunks.

Flow:

1. Pass 1 LLM triage scores tendency clusters.
2. Embedding tendency recall adds possible tendency hits from assistant text.
3. Triggered tendencies go through Pass 2 deep checks.
4. Detected deep checks route to antidote/supporting/risk models.
5. Relationship graph neighbors are ordered by affinity, fan adjustment,
   optional relevance scores, and near-tie activation matching.
6. `PressureBundleSelector` can select diagnosis/challenge/protocol/tension
   chunks from `data/curated/compiled_chunks.json`.

Strength:

- Good deterministic custody around routing and chunk selection.
- Uses embeddings as additive retrieval/reranking, not as sole authority.
- Tiebreaker has calibrated no-op gates, so it only changes near-ties.
- Pass 1 and Pass 2 already allow tendencies to fire through assistant
  commission, assistant omission, uncritical acceptance of user framing, or
  missed challenge of a user-born tendency.

Shallowness risk:

- The LLM prompt path is transaction-aware, but the embedding tendency recall is
  still assistant-text-only.
- The trusted chunks are not the v4 affordance records.
- The bundle shape is still "pressure/check/challenge/protocol" rather than
  the newer Decision Pressure contract.

### Lane 2: Companion Model Attribution

Lane 2 asks: "Which mental models are already structurally present in the
assistant's answer, and what companion knowledge should be shown?"

Inputs:

- full packet for context;
- assistant turns as the only evidence source for fingerprint quotes;
- assistant turns as candidate-recall text;
- knowledge graph, reasoning signals, relation graph, and optional embeddings.

Flow:

1. LLM extracts 3-8 reasoning moves from assistant `SOURCE` turns.
2. Candidate recall searches the knowledge graph/reasoning signals/embeddings
   using assistant text and validated fingerprint moves.
3. LLM verifier accepts or rejects candidate models.
4. Accepted models require exact or repaired literal evidence from assistant
   text.
5. Top 5 detected models surface.
6. Cheat-sheet selection adds bounded chunks with anti-echo against Lane 1.

Strength:

- Strong evidence custody: accepted models must tie to literal assistant text.
- Good for "what the AI answer is already doing or violating."

Shallowness risk:

- Lane 2 is not designed to find pressures absent from the assistant answer.
- Its matching source is primarily assistant text, not the user's full
  situation.
- If the goal is "what important pressure am I not seeing?", Lane 2 alone is
  insufficient. It can explain active reasoning; it cannot be the whole
  unknown-unknown engine.

### Lane 3: Frame Pressure

Lane 3 asks: "Is the user's question framing itself shaping the answer space?"

Inputs:

- full conversation packet;
- user turns as the only valid evidence source for extracted frame elements;
- extractor summaries and assistant replies as non-quotable context;
- `reframing_routing` from the knowledge graph.

Flow:

1. LLM extracts up to 5 frame elements from user turns.
2. Evidence quotes must be literal substrings of user turns.
3. Deterministic frame-pattern routing maps elements to candidate models.
4. LLM generates up to 2 reframings.
5. Deterministic assembly enforces compactness and anti-echo.

Strength:

- Reads the user's framing, not just the assistant answer.
- Strong quote discipline against user turns.
- Good for "the question may be wrong before the answer begins."

Shallowness risk:

- Pattern taxonomy can become brittle if future work turns examples into
  deterministic routing rules.
- It detects frame-level issues, not all operational pressures.

### Lane 4: Structural Coverage

Lane 4 asks: "Which structural dimensions of the problem were not covered by
the assistant answer?"

Inputs:

- full conversation packet;
- user turns for what the question establishes;
- assistant turns for what the answer covered;
- 15 structural dimensions and routing model IDs from the knowledge graph;
- anti-echo model IDs from Lanes 1-3.

Flow:

1. LLM classifies the question type.
2. LLM detects present dimensions and checks whether the answer covered them.
3. LLM ranks uncovered dimensions by materiality and keeps at most 5 gaps.
4. Deterministic routing maps uncovered dimensions to candidate model IDs.
5. LLM generates 2-3 discovery questions per routed gap.

Strength:

- Closest current lane to "what did the answer miss?"
- Reads both the user's actual turns and the assistant's answer.
- Uses anti-echo across earlier lanes.

Shallowness risk:

- Raw Lane 4 output is not the product surface. It can create 8-15 questions
  and look useful while creating more AI homework.
- Routing from dimension to model IDs is deterministic and coarse.
- Without v4 coverage checks, routed model IDs can imply substrate support
  that reviewed records do not actually provide.

### Decision Pressure: Dormant Synthesis Surface

Decision Pressure is not currently a live lane.

Current implemented pieces:

- v4 affordance records;
- `decision_pressure_trace.v1` schema;
- trace validator;
- PR18 golden fixture;
- fixture-only adapter smoke report.

Current non-implemented pieces:

- no live pressure producer;
- no prompt change;
- no `/lolla` runtime use;
- no Observatory rendering;
- no memo/Step 8/Step 6 integration;
- no deterministic pressure selection.

Decision Pressure asks the product-shaped question:

> From the advice and available source-backed substrate, what compact
> operational pressure should the user verify, dismiss, monitor, delay,
> document, stop, or do next before acting?

That requires semantic synthesis. Python may validate the trace, references,
caps, provenance classes, coverage blanks, and blocked surfaces. Python must
not choose the pressure.

## How The 55 Affordance Records Relate To The Lanes

The 55 v4 records are not evenly distributed runtime weights. They are reviewed
operational affordance records.

Each record can contain:

- `activation_shape.use_when`;
- `activation_shape.do_not_use_when`;
- `activation_shape.case_evidence_needed`;
- `mechanism`;
- `treatment_requirements`;
- `diagnostic_questions`;
- `misuse_guards`;
- source evidence;
- absence records.

These are valuable because they encode operational constraints a generic LLM may
not reliably apply:

- what evidence is needed before using the model;
- when not to use it;
- what a good answer must do;
- what misuse looks like;
- what cannot be honestly supported by the source.

But today, they mainly support:

- Gate 4 offline experiments;
- manual Decision Pressure dry surfaces;
- dormant trace fixtures;
- validation that selected pressure references real source-backed affordances.

They do not yet replace Lane 1/Lane 2/Lane 3/Lane 4 matching.

## Deterministic vs LLM Boundary

Current safe boundary:

Python may do:

- load graph/data artifacts;
- parse conversation turns;
- build IR and lane packets;
- enforce caps;
- validate quote substrings;
- route via explicit graph tables;
- compute embedding similarity;
- rerank near-ties under calibrated gates;
- deduplicate and anti-echo;
- validate trace schemas;
- check source-affordance IDs;
- preserve coverage blanks;
- produce review-only counts/IDs reports.

LLMs/reviewers do:

- classify question type;
- detect tendencies;
- extract frame elements;
- judge coverage;
- generate reframings/questions;
- verify whether a model is structurally present;
- synthesize Decision Pressure;
- decide novelty, actionability, tone, usefulness, and dismissal quality.

The anti-casuistry rule remains:

> Deterministic code can preserve custody and shape. It cannot decide wisdom.

## Where The Current Build May Be Too Shallow

These are not accusations. They are the current architecture's honest
shallowness risks.

1. **The 55-record corpus is not live matching**

   We may talk as if v4 enriches the product, but runtime does not yet use v4
   to select or synthesize live pressures. v4 is review infrastructure.

2. **Lane 2 sees the assistant answer more than the situation**

   Lane 2 is excellent for attribution, but weak for unknown unknowns. It
   fingerprints what the answer already did.

3. **Lane 4 is closer to missing-pressure discovery but too raw**

   Lane 4 can expose missing structural dimensions, but raw gap questions are
   not the user surface. PR13-PR23 proved compression is required.

4. **The runtime has two corpus layers with different freshness**

   Runtime graph/chunks/embeddings are broad. v4 affordances are narrower but
   more operational. We need to be explicit which layer a claim comes from.

5. **Embeddings are approximate retrieval, not understanding**

   Embeddings help recall and rerank, but they do not decide whether a pressure
   is product-worthy. They can over-retrieve familiar/generic models unless
   constrained by source-backed gates.

6. **IR is conversation-first but not full fine-grained memory**

   The system has full turns and can validate quotes in lanes, but many
   high-level summaries are derived/paraphrased. We should not claim every
   pressure is traced to exact spans unless the lane validates that span.

7. **No pressure-family coverage map exists yet**

   We know v4 has 55 records, but we do not yet have a map that says whether
   pressure families are balanced: evidence quality, incentives, risk,
   reversibility, resource allocation, timing, trust, competitive response,
   safety, etc.

8. **Examples can seduce future deterministic logic**

   PR23 showed the surface travels, but examples must not become templates.
   Future runtime work must prove generalization without case-type rules.

## Expansion Beyond 55

Expansion should not be "even distribution" by model count.

The more useful target is:

> Even pressure coverage, uneven model depth where the product needs it.

Some models deserve rich operational records because they often create
Decision Pressure. Some models may deserve only absence records because the
source does not support runtime pressure. Some models are useful in the 222
runtime graph but may never need a v4 affordance record if they do not create
compact pre-action pressure.

Recommended expansion dimensions:

1. **Pressure-family coverage**
   Map the 222 runtime models and 55 v4 records into pressure families:
   evidence, incentives, risk, reversibility, opportunity cost, uncertainty,
   timing, stakeholder power, governance, safety, resource allocation,
   competitive dynamics, system dynamics, learning, and execution.

2. **Surface pull**
   Extract new records only when repeated dry surfaces show a missing family or
   missing model blocks a useful pressure.

3. **Coverage-gap risk**
   Prioritize models whose absence creates full-route blanks or fake-confidence
   risk.

4. **Operational-field likelihood**
   Prioritize sources likely to produce `do_not_use_when`,
   `case_evidence_needed`, `treatment_requirements`, `misuse_guards`,
   dismissal logic, tripwires, and stop conditions.

5. **Absence discipline**
   A failed extraction can be useful. Absence records prevent the system from
   pretending a source supports a pressure.

6. **Distribution telemetry**
   Track which families/models repeatedly surface, get suppressed, or create
   coverage blanks. Avoid overfitting to popular models like systems thinking,
   opportunity cost, or risk assessment.

## Recommended Next Move

Do not start runtime Decision Pressure generation yet.

The simplification note in
`research/enriched-mental-model-packet-strategy-2026-05-06.md` should now guide
the next architecture discussion:

> Existing lanes pull the relevant mental-model shelves. Deterministic code
> enriches those shelves into compact, source-backed cards. The next LLM reads
> those cards and does the semantic thinking.

That means the next useful non-runtime step is not a deterministic pressure
producer. It is either:

1. a dormant `reasoning_substrate_packet.v1` adapter plan that attaches v4
   affordance snippets to lane-derived candidate models.
2. a pressure-family coverage audit that explains which model families are
   under-enriched for those packets.

The packet plan answers the architecture question first:

1. Which lane outputs nominate candidate model IDs?
2. Which recall sources should use the full user + assistant transaction?
3. Which attribution sources must stay assistant-only or user-only?
4. Which v4 affordance fields become card snippets?
5. How do we cap, dedupe, and mark graph-only coverage honestly?
6. How do we keep the packet from becoming user-facing pressure prose?

The pressure-family coverage audit then answers the corpus question:

1. Build a pressure-family taxonomy for current v4 affordances.
2. Map all 55 v4 records into that taxonomy.
3. Map the 222 runtime models into the same taxonomy at a lighter level.
4. Compare runtime Lane 4 routed model frequency against v4 coverage.
5. Identify over-covered, under-covered, and blank pressure families.
6. Produce an expansion priority list that says:
   - extract now;
   - defer;
   - add absence record;
   - leave runtime graph only.

The dormant packet adapter plan would:

1. Take existing lane outputs as candidate model sources.
2. Attach v4 affordance snippets where reviewed records exist.
3. Mark graph-only and missing-reviewed-record coverage honestly.
4. Cap and dedupe the packet.
5. Keep final pressure synthesis with the next LLM/reviewer.

Either path should remain docs/data-analysis or runtime-dormant review
infrastructure only. No prompt changes, no live runtime code, no new extraction,
no Batch 3b, no UI, and no `/lolla` promotion by default.

The decision question should be:

> Does the current substrate give us broad-enough pressure coverage to search
> unknown unknowns without relying on brittle case examples?

Not:

> How do we wire the 55 records into a new lane?

And not:

> How do we make Python choose the final pressure?

## Product Interpretation

The product should remain broad:

> The user does not know which pressure matters, so Lolla should search across
> a wide pressure space.

But the system should stay strict:

> Only compact, action-changing, dismissible, source-backed or coverage-honest
> pressure earns the surface.

Future expansion is therefore not about completing an encyclopedia. It is
about improving the chance that, when a user is near action, Lolla can find the
one pressure worth putting on their radar without creating noise, fake
coverage, or deterministic case logic.

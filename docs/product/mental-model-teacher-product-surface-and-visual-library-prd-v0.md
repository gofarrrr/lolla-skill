# Mental Model Teacher Product Surface And Visual Library PRD v0

Status: planning PRD
Date: 2026-07-05
Decision gate: `proceed_to_current_substrate_inventory_exposure_contract`
Recommended next PR: Mental Model Teacher Current Substrate Inventory And Exposure Contract v0

## One Sentence

Build a separate user-facing Mental Model Teacher product surface that turns
Lolla's canonical mental-model corpus, curated relation semantics, and Teacher
lessons into browsable model pages, clickable relation pages, and focused visual
graphs that help users learn transferable reasoning moves.

## Why This Exists

Lolla already has a powerful skill and several internal pipelines. Those are not
the product surface described here.

The Lolla skill audits reasoning inside a live conversation.
Observatory-style artifacts show what happened in a run.
Decision Work preserves decision artifacts and sidecars.
Product Delta evaluates evidence internally.
Mental Model Teacher should help a person learn how to think better.

The current Teacher work has the right philosophical center:

```text
case is the anchor
reasoning move is the subject
model relationship is the lesson
practice rep is the product value
```

But the current Teacher outputs can still feel like internal artifacts. The next
product step is a visual, readable, click-through library that lets a user answer:

- What is this mental model?
- When should I use it?
- When does it mislead?
- What models support it?
- What models challenge it?
- Why did Lolla use this model in my run?
- What practice rep helps me learn the move?
- How is this connected to the rest of the mental-model corpus?

## What This Is Not

This is not a merge of every Lolla lane into one big interface.

It is not:

- a replacement for the Lolla skill;
- Observatory;
- Decision Work;
- Product Delta;
- a second advice engine;
- a runtime hook;
- a live LLM judge;
- proof that Lolla improved the user's answer;
- proof that a Teacher lesson is human validated;
- a graph database migration;
- an automatic mental-model relation invention system.

The product lane should sit next to the existing systems. It may consume their
safe artifacts, but it should not collapse their boundaries.

## Current Assets To Leverage

This PRD should be implemented by promoting existing assets into a user-facing
shape, not by rebuilding the knowledge system from scratch.

Existing source assets:

- `data/model_sources/*.md`: canonical mental-model source Markdown.
- `data/model_sources/manifest.json`: file identity and hash manifest.
- `data/curation/*.json`: activation, avoid-when, input/output type, reasoning
  types, provenance notes.
- `data/curation/intervention_semantics/*.json`: failure modes, premortem
  questions, heuristics, mitigations, and practice-relevant material.
- `data/curation/relation_semantics/*.json`: allies, antagonists, structured
  tensions, source quotes, confidence, and curation notes.
- Existing Teacher worktree artifacts: Teacher cards, notes, OKF bundles,
  relation deep dives, model deep dives, practice labs, grounding audits, and
  human-gate scaffolding.
- `data/knowledge_graph.json`: wider compiled substrate with models, tendencies,
  antidote bindings, structural coverage routing, reframing patterns, and
  topology.
- `data/relationship_graph.json`: compiled relation graph used by graph
  neighborhoods and relation selection.
- `data/embeddings.db`: precomputed embeddings used by semantic matching and the
  activation tiebreaker; internal-only for this product v0.
- `data/curated/*.json`: trusted-surface chunks, subpatterns, structural signal
  lexicon, and reasoning signals.
- `data/family_semantics/*.json`: family and cluster semantics that can later
  become library collections and graph clusters.
- `data/compiled/model_affordances/affordances_v60.json`: reviewed affordance
  and absence layer over the canonical articles.
- Runtime and research code such as `engine/system_b/relation_graph.py`,
  `engine/system_b/activation_matcher.py`,
  `engine/system_b/graph_survival_report.py`, and
  `engine/system_b/model_affordance_validation.py`.

Important source policy:

```text
canonical Markdown is source of truth
curation JSON is reviewed derived structure
Teacher lessons are case-scoped teaching artifacts
visual pages and graphs are product renderings
```

## Product Philosophy

We should not try to make messy conversation deterministic.

Conversation is probabilistic, contextual, and often incomplete. LLMs are useful
because they can interpret, synthesize, explain, and relate ideas. The product
value here is to use that cognitive power where it belongs, while surrounding it
with deterministic rails:

- source custody;
- model and relation contracts;
- generated artifacts;
- missingness states;
- review gates;
- non-claims;
- human-readable receipts;
- clear separation between teaching, evidence, decision preservation, and
  runtime behavior.

The graph should not say "this is true."

The graph should say:

```text
Here are the lenses that appear connected.
Here is why the relation matters.
Here is where the relation came from.
Here is how to practice the distinction.
Here is where this lesson stops.
```

## Current Substrate Map

Before implementing product pages or graph UI, the team must inventory the
existing substrate and decide how each asset is allowed to surface.

Detailed inventory:

- [Mental Model Teacher Current Substrate Inventory](mental-model-teacher-current-substrate-inventory-v0.md)

Lolla already has:

- canonical mental-model Markdown;
- activation semantics;
- intervention semantics;
- relation semantics;
- a compiled relationship graph;
- a wider knowledge graph;
- embedding-backed activation matching;
- curated trusted-surface chunks;
- family semantics;
- V60 model affordances and absence records;
- graph survival reports;
- treatment audits;
- Teacher cards, notes, OKF bundles, and deep dives in the separate Teacher
  worktree.

That means the visual library is not a "new graph builder" project. It is a
translation layer:

```text
internal substrate
  -> product-safe contracts
  -> readable model pages
  -> readable relation pages
  -> Teacher lesson pages
  -> focused visual graph neighborhoods
```

The product should understand all current lanes, but expose only what helps the
user learn.

### Product-safe exposure rules

| Existing substrate | Product use | Keep internal |
|---|---|---|
| Canonical Markdown | model doctrine and examples | raw source dump |
| Activation curation | use-when and avoid-when sections | routing internals |
| Intervention semantics | failure, premortem, practice sections | extraction metadata as primary UI |
| Relation semantics | relation pages and graph edges | unsupported relation speculation |
| Relationship graph | focused graph neighborhood source | raw affinity/ranking as truth |
| Knowledge graph | later global navigation and collections | full topology as first screen |
| Embeddings DB | future suggestion layer | embedding rank as proof |
| V60 affordances | advanced "what this model can do" sections | raw transaction JSON |
| Graph survival/evals | internal caution about noise/helpfulness | product marketing claim |
| Teacher artifacts | lesson and practice source | review packets as UX |

## Product Data Principle

Every product object should carry four layers:

1. User-facing explanation.
2. Source/custody reference.
3. Missingness or uncertainty state.
4. Explicit non-claims.

This is how the product can be visual and educational without becoming naive.

## Reference Pattern Summary

Detailed notes are in
[Mental Model Teacher Product Surface Reference Patterns](mental-model-teacher-product-surface-reference-patterns-v0.md).

The reference projects point toward these design choices:

- Start local/static and source-controlled, like Foam, Dendron, Quartz, and
  Flowershow.
- Use graph navigation, but default to focused neighborhoods, inspired by
  Logseq and Foam.
- Treat relations as first-class objects, inspired by Anytype.
- Make model sections addressable, inspired by SiYuan's block-level references.
- Keep a card/list/search library beside the graph, inspired by AppFlowy.
- Use hierarchy plus network, inspired by TriliumNext.
- Consider semantic-neighbor suggestions later, inspired by Reor, but do not let
  vector similarity override curated relations.
- Consider Cytoscape.js for the first focused graph prototype and Sigma.js only
  if full-corpus rendering becomes a scale problem.

## Primary User Surfaces

### 1. Mental Model Library Home

A browsable entry point for the corpus.

It should include:

- search;
- model cards;
- filters by reasoning type, input type, use case, and relation type;
- "start here" collections such as uncertainty, decision pressure, communication,
  risk, learning, systems, and bias correction;
- a visible distinction between canonical model pages and case-specific Teacher
  lessons.

The library home should not default to a full graph. A full graph is exciting,
but it is a poor first explanation if the user does not yet know what the nodes
mean.

### 2. Mental Model Page

A user-facing page for one model.

It should present:

- plain-language title;
- one-sentence meaning;
- what the model helps you notice;
- when to use it;
- when not to use it;
- common misuse;
- failure modes;
- premortem questions;
- heuristics;
- practice prompts;
- allies;
- antagonists;
- structured tensions;
- source/custody summary;
- links to Teacher lessons where it appeared.

It should not present raw curation JSON as the product. Raw fields can power the
page, but the page should read like a learning artifact.

### 3. Relation Page

A user-facing page for one relation between models.

It should present:

- source model;
- target model;
- relation type: ally, antagonist, structured tension, antidote, guardrail, or
  practice companion;
- plain-language relation story;
- why the relation matters;
- how the relation can be misread;
- a small practice drill;
- source quote or source-ref summary;
- confidence and curation status;
- links to both model pages and any Teacher lessons that used the relation.

This is important: a graph edge is not enough. Users need to click the edge and
learn the relation.

### 4. Teacher Lesson Page

A productized version of a Teacher output.

It should present:

- the case anchor in one or two safe sentences;
- the reasoning move;
- the model stack;
- relation story;
- model clickthroughs;
- relation clickthroughs;
- worked example;
- practice rep;
- "do not overlearn this" boundary;
- visible non-claims.

Teacher must stay different from Decision Work:

```text
Decision Work asks: what decision artifact should be preserved?
Teacher asks: what reasoning move can the user learn?
```

### 5. Run Neighborhood Graph

A focused graph around one Teacher lesson.

It should show:

- 3 to 10 relevant models by default;
- edge labels for ally, tension, antagonist, guardrail, and practice companion;
- selected-node detail panel;
- selected-edge relation panel;
- links to model pages and relation pages;
- a "why this appears here" explanation;
- clear source and uncertainty status.

The first graph should be a lesson neighborhood, not a 222-node corpus map.

### 6. Global Model Graph

A later surface for browsing the whole corpus.

It should support:

- search;
- zoom and pan;
- filtering by relation type and model family;
- model details on click;
- relation details on edge click;
- saved entry points or curated paths;
- graph density controls.

This should be implemented after model pages, relation pages, and lesson
neighborhood graphs prove they teach clearly.

## Data Contracts To Define Next

The next implementation PR should define these contracts before rendering UI.

### Mental Model Product Page Object

Required fields:

- `model_id`
- `slug`
- `display_name`
- `one_sentence_meaning`
- `helps_notice`
- `use_when`
- `avoid_when`
- `common_misuse`
- `failure_modes`
- `premortem_questions`
- `heuristics`
- `practice_prompts`
- `reasoning_types`
- `source_refs`
- `source_hashes`
- `curation_status`
- `non_claims`

### Relation Product Page Object

Required fields:

- `relation_id`
- `source_model_id`
- `target_model_id`
- `relation_type`
- `plain_language_story`
- `why_it_matters`
- `misread_risk`
- `practice_prompt`
- `source_quote_or_ref`
- `confidence`
- `curation_status`
- `non_claims`

### Teacher Lesson Product Object

Required fields:

- `lesson_id`
- `case_id`
- `case_anchor`
- `thinking_move`
- `model_stack`
- `relation_story`
- `model_links`
- `relation_links`
- `practice_rep`
- `do_not_overlearn`
- `source_refs`
- `human_review_status`
- `product_proof`
- `runtime_integration_authorized`

### Visual Graph Object

Required fields:

- `graph_id`
- `graph_scope`: `lesson_neighborhood`, `collection`, or `global_corpus`
- `nodes`
- `edges`
- `source_artifacts`
- `layout_hint`
- `default_focus`
- `filters`
- `non_claims`

Nodes should carry only product-safe summaries.
Edges should carry relation IDs, not only labels.

## Step-By-Step Implementation Roadmap

This is intentionally conservative. It lets a junior coder build reviewable
slices without turning the Teacher into runtime automation or a generic graph
demo.

### PR-P1 Product Surface PRD And Reference Audit

Status: this PRD.

Deliver:

- product-surface PRD;
- reference-patterns note;
- review JSON;
- tests that preserve boundaries and roadmap shape.

Stop before:

- page builders;
- graph builders;
- UI implementation.

### PR-P2 Current Substrate Inventory And Exposure Contract

Deliver:

- deterministic inventory over existing model, graph, curation, affordance, and
  Teacher assets;
- exposure policy JSON that classifies each asset as product-safe, internal-only,
  or product-safe-after-translation;
- tests covering `data/knowledge_graph.json`, `data/relationship_graph.json`,
  `data/embeddings.db`, `data/model_sources`, `data/curation`,
  `data/curation/intervention_semantics`, `data/curation/relation_semantics`,
  `data/family_semantics`, `data/compiled/model_affordances/affordances_v60.json`,
  and Teacher artifacts when present;
- report that states what can power model pages, relation pages, graph pages, and
  Teacher pages.

Acceptance:

- no internal asset is silently exposed as user-facing;
- embeddings and eval artifacts stay internal for v0;
- current substrate counts and missingness are visible.

Stop before:

- product page contracts;
- page rendering;
- graph UI.

### PR-P3 User-Facing Model And Relation Contracts

Deliver:

- Python module defining product-safe contracts for model pages, relation pages,
  Teacher lesson pages, and graph objects;
- schema fixtures for one model and one relation;
- tests that reject raw local paths, product-proof claims, runtime claims, and
  relation overclaiming.

Use:

- `data/model_sources/manifest.json`;
- `data/curation/*.json`;
- `data/curation/intervention_semantics/*.json`;
- `data/curation/relation_semantics/*.json`.

Stop before:

- rendering pages.

### PR-P4 Pilot Model And Relation Page Data Builder

Deliver:

- deterministic builder that creates product page JSON for a small pilot subset;
- pilot subset should include models already used in Teacher cases;
- relation JSON for selected allies, antagonists, and structured tensions;
- build report with missingness and source-custody status.

Acceptance:

- every page object has source refs;
- relation pages never claim the relation is universally true;
- missing fields become missingness, not invented copy.

Stop before:

- HTML rendering.

### PR-P5 Static Model And Relation Page Renderer

Deliver:

- static Markdown or HTML renderer for model and relation pages;
- product-readable sections;
- no raw JSON dump as main UI;
- stable slugs and local links;
- tests for required sections and link validity.

Acceptance:

- a non-technical reader can understand a model page;
- relation pages explain the edge in plain language before taxonomy.

Stop before:

- graph UI.

### PR-P6 Teacher Lesson Product Renderer

Deliver:

- productized Teacher lesson page renderer;
- links from lesson to model pages and relation pages;
- visible "case is anchor, reasoning move is subject" framing;
- non-claims block;
- human-gate status block.

Acceptance:

- page does not read like Decision Work;
- page does not read like telemetry;
- page teaches a practice rep.

Stop before:

- graph rendering.

### PR-P7 Lesson Neighborhood Graph Data Builder

Deliver:

- deterministic graph JSON for one Teacher lesson neighborhood;
- nodes from selected model pages;
- edges from selected relation pages;
- graph report with node count, edge count, missingness, and source status.

Acceptance:

- default graph is small enough to teach;
- edge click can resolve to a relation page;
- graph object preserves non-claims.

Stop before:

- browser graph UI.

### PR-P8 Static Visual Graph Prototype

Deliver:

- local static HTML prototype using a lightweight graph renderer;
- Cytoscape.js is the preferred first candidate because the graph is semantic
  and interactive, not just large;
- selected node panel;
- selected edge panel;
- search and relation-type filters;
- links to model and relation pages.

Acceptance:

- graph renders without provider calls;
- graph is readable on a small pilot subset;
- no runtime integration;
- no generated graph output is mistaken for source truth.

Stop before:

- full corpus graph.

### PR-P9 Three-Case Teacher Product Pilot

Deliver:

- product pages and graph neighborhoods for the three Teacher pilot cases;
- compare against existing Teacher card/note outputs;
- identify whether product pages teach better than raw Teacher artifacts;
- no human-validation claim.

Acceptance:

- launch, deploy, and CEO cases each have a lesson page and graph neighborhood;
- high-risk cases preserve uncertainty and domain caveats.

Stop before:

- package gate.

### PR-P10 UX Review Packet And Human Review Form

Deliver:

- reviewer packet comparing Teacher product pages against current Teacher cards;
- human review form;
- criteria: educational value, clarity, relation understanding, practice value,
  non-overclaiming, and separation from Decision Work.

Acceptance:

- synthetic/sub-agent review remains diagnostic only;
- human review is not pre-filled or leading.

Stop before:

- claiming product readiness.

### PR-P11 Product Surface Package Gate

Deliver:

- package manifest for PR-P1 through PR-P10;
- current-state doc;
- validation checklist;
- explicit non-claims;
- next-decision gate.

Possible gate outcomes:

- `mental_model_teacher_product_surface_pilot_packaged`
- `needs_model_page_revision`
- `needs_relation_page_revision`
- `needs_graph_ux_revision`
- `needs_human_review_before_expansion`

Stop before:

- full corpus build;
- runtime integration.

### Optional PR-P12 Full Corpus Graph Plan

Deliver:

- plan to scale from pilot subset to all canonical models;
- graph-density, performance, search, filtering, and publish-scope decisions;
- explicit decision between Cytoscape.js, Sigma.js, or another renderer.

Stop before:

- full corpus rendering.

### Optional PR-P13 Full Corpus Library Pilot

Deliver:

- full-corpus generated model-page data;
- full-corpus relation graph JSON;
- static browse/search prototype;
- performance and readability review.

Stop before:

- customer-ready claim.

## Junior Coder Handoff

When implementing the next PR, do this in order:

1. Read this PRD.
2. Read the reference-patterns note.
3. Inspect `data/model_sources/manifest.json`.
4. Inspect the current substrate inventory note.
5. Inspect `data/knowledge_graph.json` and `data/relationship_graph.json`.
6. Inspect one canonical model file from `data/model_sources`.
7. Inspect one activation curation file from `data/curation`.
8. Inspect one intervention file from `data/curation/intervention_semantics`.
9. Inspect one relation file from `data/curation/relation_semantics`.
10. Inspect `data/compiled/model_affordances/affordances_v60.json` shape.
11. Define exposure policy before product contracts.
12. Define contracts before rendering.
13. Add tests that preserve non-claims and source custody.
14. Stop at the PR boundary. Do not make the next PR in the same commit.

## Validation Expectations

Each PR should run the smallest useful validation plus relevant broader tests.

At minimum:

- `python3 -m py_compile` for new tests/modules;
- focused pytest for the new slice;
- JSON validation for generated review/schema files;
- `git diff --check`;
- local Markdown link check over touched Markdown;
- trailing whitespace scan over touched files;
- privacy marker scan over touched docs;
- protected-path check for `SKILL.md`, `scripts/skill/*`, and
  `scripts/archive_run.py`.

Do not run:

- `$lolla`;
- Lolla skill invocation;
- provider/model APIs;
- new Lolla runs.

## Risks

### Risk: The graph becomes decorative telemetry

Mitigation:

- default to focused lesson neighborhoods;
- require click-through explanation for every edge;
- keep model and relation pages useful without the graph.

### Risk: Raw curation leaks into the product surface

Mitigation:

- use product page contracts;
- convert curation fields into plain-language sections;
- keep source/custody available but secondary.

### Risk: Teacher duplicates Decision Work

Mitigation:

- Teacher page starts with the reasoning move, not the decision;
- case summary is short and anchoring only;
- no advice recommendation.

### Risk: Relation overclaiming

Mitigation:

- relation pages show confidence and source status;
- graph edges say "this is a useful relation in this corpus", not "this is
  universally true";
- semantic-neighbor suggestions are deferred until reviewed.

### Risk: Full graph overwhelms users

Mitigation:

- card/list/search first;
- lesson neighborhood graph first;
- global graph later with filters and density controls.

### Risk: The product claims proof too early

Mitigation:

- preserve human-review and product-proof flags;
- no scoring;
- no certification;
- no action authorization;
- package gate before expansion.

## Non-Claims

This PRD does not claim:

- product proof;
- human validation;
- answer correctness;
- advice correctness;
- mental model completeness;
- relation correctness beyond the recorded curation status;
- customer readiness;
- runtime integration;
- resolver approval;
- action authorization;
- automatic semantic generation for arbitrary runs;
- that a graph proves a reasoning move.

## Expected Outcome At The End Of This Phase

If PR-P1 through PR-P11 succeed, we should have a reviewable offline product
pilot where a user can:

1. Open a Teacher lesson.
2. Understand the reasoning move.
3. Click the mental models used in the lesson.
4. Read clean model pages.
5. Click model relations.
6. Read clean relation pages.
7. See a focused graph neighborhood.
8. Practice the move.
9. Understand where the lesson stops.

That would be a real product surface, not just a pile of internal artifacts.

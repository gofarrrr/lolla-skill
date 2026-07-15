# Lolla Mental Model Atlas and Teacher PRD v1

Status: prospective product PRD; implementation not authorized

Date: 2026-07-15

Canonical planning base: `2f05fd1ca7081f602317d670faad8d1293d5b0ff`

Machine contract: [Mental Model Atlas PRD contract v1](../evals/lolla-mental-model-atlas-prd-v1.json)

Reference study: [Marble reference study](lolla-mental-model-atlas-marble-reference-2026-07-15.md)

Implementation plan: [Mental Model Atlas tracer-bullet plan](../../plans/lolla-mental-model-atlas-tracer-bullet-plan-2026-07-15.md)

## Executive Decision

Define a public, source-backed Mental Model Atlas and guided Teacher product
lane that makes Lolla's existing 222-model knowledge substrate explorable as a
beautiful global map, a searchable library, full model pages, first-class
relation pages, and curated learning journeys.

The product shorthand is:

```text
Atlas shows the territory.
Pages explain the models and relations.
Teacher guides a journey through them.
Lolla pressure uses the same canonical identities without becoming the UI.
```

The founder has now selected the missing user job that previously kept Mental
Model Teacher parked: help a person see the whole landscape of mental models,
understand one model and its interactions deeply, and learn transferable
reasoning moves through deliberate traversal and practice.

This PRD defines that job and a real-user evidence plan. It does not, by itself,
change the Stage 0 register disposition from `park`, authorize implementation,
complete human review, prove product value, or connect Teacher to the ordinary
Lolla runtime. A separate founder decision must authorize the first tracer
bullet.

## Why This Is A New Product Start, Not A Revival Of R4

R4 attempted to derive reliable residual Decision Work state from arbitrary
conversations. It is retired because it preserved true findings while also
producing unsafe false positives, including after the two surfaces were split.

The Atlas and Teacher do a different job:

- they expose an existing, curated mental-model substrate;
- they teach model meaning and model relationships;
- they provide navigation and practice;
- they can later show which models appeared in a run through a read-only,
  source-custodied link;
- they do not infer unresolved matters, future reopen conditions, user
  adoption, or action authority from arbitrary conversation.

This lane has no dependency on R4, Decision Trail semantic generation, general
conversation understanding, or Decision Work automatic supply. It can succeed
or fail on its own product evidence.

## Current Lifecycle Truth

At the canonical planning base:

- the mental-model substrate and relationship graph are active parts of the
  live pressure system;
- Mental Model Teacher has rich prototype and read-only Observatory work but is
  parked;
- the Stage 0 register says the Teacher reopen gate is a specific user job plus
  a real-user evidence plan;
- the old product-surface package reached static pilot pages, small lesson
  graphs, three case lessons, and a blank review packet;
- human validation was not completed;
- the existing graph prototype is a utilitarian, dependency-free SVG, not the
  selected visual bar;
- no source-controlled modern browser application exists for this public
  surface;
- the compiled Observatory bundle is not an acceptable place to hide new
  product source;
- the full 222-model Atlas has not been built or product-reviewed.

This PRD satisfies the product-job half of the reopen gate and specifies the
evidence half. It deliberately leaves the lifecycle change to the first
authorized implementation and human gate.

## Product Thesis

Lolla's mental-model substrate is already more than a list of concepts. It is a
curated network of models, families, allies, antagonists, tensions, activation
conditions, failure modes, premortems, heuristics, and source material. Today
most of that value is available to the runtime, developers, or static research
artifacts rather than to a learner.

The thesis is that the same substrate can become a compelling learning product
when it is translated into three complementary modes:

1. **Explore:** see the whole network and move through meaningful relations.
2. **Understand:** read a complete model or relation page with provenance,
   limitations, and practice.
3. **Learn:** follow a curated journey that turns a relationship into a
   reasoning move and a practice rep.

The graph creates the “I can see the territory” moment. The pages create durable
understanding. Teacher creates progression and deliberate practice.

## Falsifiable Product Question

Can a curious knowledge worker use Lolla's Atlas to find and explain an
unfamiliar mental model and one meaningful relationship, then complete a
Teacher practice rep, without mistaking graph position, relation confidence, or
Lolla's presentation for truth, importance, advice, or mastery certification?

The first product slice fails if a reviewer cannot do those tasks, finds the
graph decorative or confusing, cannot distinguish ally from antagonist or
tension, cannot reach the full pages, or treats graph salience as authority.

## User Job

### Primary job

> Help me see how mental models fit together, understand the ones that matter
> to the question I am exploring, and practice using their relationship without
> reducing them to a list of definitions.

### Secondary jobs

- Give me an inviting, credible way to understand what intellectual substrate
  Lolla actually contains.
- Let me browse all models even when I do not begin with a precise search term.
- Let me move from a model to allies, antagonists, and tensions and understand
  why each connection exists.
- Give me a full, linkable page for a model or relation that I can return to and
  share.
- Give me curated “start here” journeys rather than forcing me to navigate a
  dense map alone.
- Later, let me move from a read-only Lolla run receipt to the same public model
  and relation pages without exposing private conversation content.

### Non-jobs

The Atlas and Teacher do not:

- decide which mental model is correct for a user's situation;
- certify that a relation is universally true;
- infer a user's decision state;
- authorize an action;
- replace the live four-lane pressure path;
- improve, score, or judge a conversation automatically;
- prove that a user has mastered a model;
- rank people, conversations, or decisions;
- turn graph centrality into importance;
- publish private conversation prose.

## Target Users

### Curious knowledge worker

Wants to explore better ways to frame decisions, risks, systems, incentives,
communication, and learning. May know a few familiar models but not their
interactions.

### Existing Lolla user

Has seen one or more models introduced as pressure and wants to understand the
model beyond the run artifact. This user must be able to follow a safe model ID
link without making their conversation public.

### Teacher or facilitator

Wants a coherent model page, a relation explanation, and a bounded practice rep
that can support a discussion without presenting Lolla as an authority.

### Project evaluator or collaborator

Wants to see the depth and structure of Lolla's mental-model estate and
understand which parts are curated data, product rendering, experimental
pressure, or unproven teaching material.

## User Stories

| ID | User story | Success observation |
|---|---|---|
| `US-01` | As a visitor, I can see the whole mental-model territory before choosing a node. | All canonical models are represented; the scene is legible and responsive. |
| `US-02` | As an explorer, I can select a model without losing global orientation. | The selected neighborhood gains emphasis while the global map remains visible. |
| `US-03` | As an explorer, I can hover another model while keeping my durable selection. | Hover preview and selected detail are independent states. |
| `US-04` | As a learner, I can understand why two models are related. | The edge resolves to a relation explanation with direction, type, source, limitation, and practice. |
| `US-05` | As a learner, I can read a complete model page outside the graph. | Stable URL, readable sections, sources, missingness, and related models are present. |
| `US-06` | As a visitor who knows what I seek, I can search and filter without using the graph. | Search, library, family, and relation filters work as equivalent navigation. |
| `US-07` | As a beginner, I can follow a curated learning journey. | A journey has an explicit question, model sequence, relation lessons, practice, and stop boundary. |
| `US-08` | As a keyboard or screen-reader user, I can reach the same knowledge without the canvas. | Synchronized list, pages, focus order, summaries, and controls cover the same product objects. |
| `US-09` | As a motion-sensitive user, I can pause or avoid ambient movement. | Reduced-motion is honored and all tasks remain possible. |
| `US-10` | As a Lolla user, I can later follow a safe model reference from an archive to the public page. | Only stable public IDs cross; private prose remains in its original custody boundary. |

## Product Principles

### Atlas shows the territory; Teacher guides a journey

The Atlas is self-directed exploration. Teacher is a curated sequence with a
learning objective and practice. They share canonical model and relation IDs,
but they are not one overloaded screen.

### The graph is navigation, not proof

Node size, position, color, connection count, selection, and motion are visual
encodings. They do not establish relevance, correctness, usefulness, or
importance. Every encoding must have a truthful legend.

### The relation is a first-class learning object

An edge without explanation is decorative telemetry. Every visible edge must
resolve to a stable relation object or explicitly disclose that no public
relation page is available.

### Full pages must work without the graph

The graph is an invitation and spatial index. Model pages, relation pages,
library search, and Teacher journeys remain useful and accessible when WebGL is
unavailable.

### Canonical source precedes product reduction

Canonical Markdown and reviewed curation remain source. The Atlas consumes a
versioned, product-safe projection. The browser never scrapes runtime files or
invents missing copy.

### Beautiful is a product requirement

Visual quality is not a post-MVP polish lane. Composition, typography, motion,
state transitions, density management, and detail hierarchy are acceptance
criteria for the first visual slice.

### Unknown remains visible

Missing copy, one-sided relation evidence, provisional family assignment,
unreviewed practice, or absent licensing status remains explicit. The builder
does not fill holes with plausible prose.

### Public learning and private inspection stay separate

The public Atlas contains source-cleared model and relation material. The
read-only Observatory may later deep-link to those pages. Private conversation
prose and run interpretation never enter the public Atlas payload.

## Canonical Substrate Baseline

The first version uses the current repository as its input, not a new taxonomy.

| Substrate | Canonical count | Prospective product role |
|---|---:|---|
| `data/model_sources/manifest.json` | 222 model records | stable identity, source hash, canonical model source |
| `data/knowledge_graph.json:models` | 222 models | structured model fields after product-safe translation |
| `data/knowledge_graph.json:tendencies` | 25 tendencies | later curated entry points; not default model edges |
| `data/knowledge_graph.json:edges` | 1,742 compiled edges | internal topology and later reviewed layers; not default public edge set |
| `data/knowledge_graph.json:prerequisite_edges` | 15 edges | separate named learning-path layer only; not a universal hierarchy |
| `data/relationship_graph.json` | 1,358 curated relations | default Atlas relation source after product translation |
| ally relations | 523 | supportive/complementary relation view |
| antagonist relations | 344 | counteracting or contradictory relation view |
| tension relations | 491 | productive tradeoff or boundary view |
| high-confidence relations | 1,337 | disclosed curation field, not certification |
| medium-confidence relations | 21 | disclosed with stronger caution |
| `data/family_semantics/*.json` | 24 family files | prospective filter and spatial cluster semantics after review |
| activation curation | 225 files | use-when, avoid-when, and reasoning filters after translation |
| intervention semantics | 225 files | failure modes, premortems, heuristics, and practice source |
| relation semantics | 225 files | relation rationale, source, confidence, and limitations |

The compiled 222 model records already contain broad page material: 874
`select_when` entries, 453 `danger_when` entries, 678 failure modes, 674
premortem questions, 680 heuristics, and 453 reasoning-type assignments. Every
canonical model has at least one record in each of those major groups. This
makes complete product pages plausible, but the prose still requires the
product-safe translation, human readability, source, and publication-rights
gates below.

The default public relation projection uses the 1,358 curated
ally/antagonist/tension records. It does not silently mix in knowledge-graph
topology, embeddings, tendency routing, runtime rankings, or simulated Teacher
case relations.

Several substrate facts materially constrain the interface:

- the 1,358 records contain 1,191 unique directed source-target pairs and 1,153
  unordered pairs;
- 175 unordered pairs contain more than one relation type;
- 38 unordered pairs have explicit records in both directions;
- every relation record declares `is_reciprocal: false`;
- `confirmation-bias` alone has 233 incident records and 159 unique neighbors;
- the 24 family files cover only 75 unique models and overlap, so they are not
  an exhaustive partition;
- `composition_affinity` largely encodes relation category and is not a
  trustworthy importance or distance weight.

The Atlas must preserve these distinctions. The pair
`abstraction -> first-principles-thinking` is a required fixture because it has
both an ally and a tension record. The pair `active-listening` and
`prisoners-dilemma` is a required fixture because explicit records exist in
both directions. Neither may collapse to one undirected decorative line.

## Information Architecture

The durable route contract is:

| Route | Job |
|---|---|
| `/atlas` | global graph explorer |
| `/models` | searchable and filterable library |
| `/models/:slug` | complete model page |
| `/relations/:relationId` | complete relation page |
| `/learn` | curated Teacher journey index |
| `/learn/:journeyId` | one guided learning journey |

Graph selection is addressable through query state:

```text
/atlas?model=systems-thinking
/atlas?relation=<stable-relation-id>
/atlas?family=<stable-family-id>
/atlas?relations=ally,tension
```

Browser back and forward must restore selection, filters, camera focus, and the
open panel closely enough that exploration feels navigable. Ephemeral hover is
never added to browser history.

The public app should be independently deployable as static assets. It must not
live only inside Observatory. The read-only Observatory integration, if later
authorized, links to these routes or loads the same public projection; it does
not own the Atlas source.

## Surface 1: Global Atlas

### First impression

At desktop width, the Atlas opens as an editorial full-screen composition:

- a concise proposition and search affordance;
- the complete model constellation;
- a quiet relation/family legend;
- restrained navigation to Library and Learn;
- no blocking onboarding modal;
- no false claim that the visible map is an objective structure of thought.

All 222 model nodes exist in the scene. The default idle overview draws no
relation edges. It states: `222 canonical models; no relation focus selected`.
This avoids presenting a 1,358-edge hairball or the graph's highly uneven
curation fan-in as an objective ontology. The relation index remains available
to search and selection, and exact records become visible after a focus exists.
Filtering and paging are presentation, not deletion from the source
projection.

### Selection behavior

Selecting a model:

1. persists `selectedModelId`;
2. moves the camera smoothly without teleporting or recomputing the layout;
3. brightens the selected node;
4. highlights a deterministic page of its direct curated relation records and
   adjacent models;
5. dims unrelated nodes and edges without removing the global context;
6. opens a persistent detail panel;
7. updates the address bar and browser history;
8. keeps search, filters, and legend available.

The model panel includes:

- model name and one-sentence meaning;
- family or collection label when reviewed;
- “helps you notice” summary;
- counts of allies, antagonists, and tensions;
- a small ordered set of direct related models grouped by relation type;
- source and curation status in plain language;
- missingness where applicable;
- `Open full model page`;
- `Start a journey` only when a curated journey actually includes the model.

At most 40 relation records appear in the focused canvas page. The panel and
accessible relation table state exact counts, for example:

```text
40 of 233 incident relation records shown; 193 not rendered on this page
```

Next/previous paging is deterministic and preserves source direction,
parallel records, and the selected model. Omitted records are not called
irrelevant. The accessible table can expose the complete filtered set even
when only one bounded page is drawn.

### Hover behavior

Hover is an ephemeral preview. It may show name, family, one-sentence meaning,
and relation-to-selection. It must not replace the persistent selected panel,
change browser history, or trigger an expensive relayout.

### Edge behavior

Selecting an edge opens a persistent relation panel with:

- source and target model names;
- relation type;
- direction and reciprocity status;
- plain-language relation story;
- why it matters;
- misread risk;
- confidence and curation status;
- source reference or source-backed summary;
- `Open full relation page`.

When two models have multiple curated relations, each relation remains a
distinct selectable object, with parallel curves or an equivalent separable
treatment. The UI must not merge disagreement for neatness.

### Filter behavior

Supported filters:

- overlapping family or curated collection where reviewed; uncovered models
  remain explicitly `unassigned`, never forced into a cluster;
- relation type;
- model reasoning type;
- model input/use category when product-reviewed;
- text search;
- direct-neighborhood depth: one hop by default, optionally two hops with an
  explicit warning that a path is navigation, not inferred relevance.

Filters update a visible result summary and can be cleared individually. A zero
result is `completed_zero`, not a broken or missing graph. A failed data load is
distinct from zero.

### Ambient motion

Subtle camera drift or depth movement is allowed only when it preserves stable
meaning. It:

- pauses during pointer, keyboard, or touch interaction;
- never changes node coordinates or relation membership;
- has a visible pause control;
- is disabled under `prefers-reduced-motion`;
- does not delay content or input readiness;
- does not create a moving target for keyboard focus.

## Surface 2: Model Library

The Library is the complete non-canvas entrance to the corpus.

It includes:

- search by name and reviewed synonym;
- alphabetical and curated-family views;
- filters shared with the Atlas;
- compact model cards with one-sentence meaning and relation counts;
- “start here” collections whose selection is editorially documented;
- a visible count of available, partial, and unavailable pages;
- links that preserve a return path to the Atlas.

The Library must not rank by an opaque relevance score. Search may use
deterministic text matching in the first release. Embedding-backed suggestions
are a separate future feature and must be labeled as suggestions if ever
authorized.

## Surface 3: Full Model Page

Every public model page should eventually contain:

1. name and one-sentence meaning;
2. what the model helps a person notice;
3. when it is useful;
4. when to avoid or constrain it;
5. common misuse;
6. failure modes and mitigations;
7. premortem questions;
8. practical heuristics;
9. one or more practice prompts;
10. allies, antagonists, and tensions;
11. curated journeys containing the model;
12. source and custody summary;
13. curation, human-review, licensing, and missingness status;
14. explicit non-claims.

The page reads as a coherent learning artifact, not a JSON dump. Source custody
is available without dominating the teaching hierarchy. If a section lacks
reviewed source-backed content, the section is absent with an explicit status;
the renderer does not create filler.

The page provides `Show in Atlas`, which opens the stable model selection in
the global graph.

## Surface 4: Full Relation Page

Every public relation page contains:

1. source and target model;
2. relation type;
3. source-authored direction and reciprocity status;
4. plain-language relation story before taxonomy;
5. why the relation can be useful;
6. when the relation can be misread;
7. activation condition when source-backed;
8. a practice prompt or contrastive question when reviewed;
9. confidence and curation status;
10. source quote or safe source reference;
11. missingness and limitations;
12. links to both model pages and `Show in Atlas`.

Relation type has both color and a non-color visual encoding:

- ally: continuous supportive connector;
- antagonist: visibly opposed/crossed connector;
- tension: dual or interrupted connector suggesting a tradeoff.

The exact line treatment is selected in the visual spike. The semantics are
fixed: color alone is insufficient.

## Surface 5: Teacher Journeys

Teacher is a set of curated journeys, not automatic tutoring over an arbitrary
conversation.

Each journey contains:

- a clear learning question;
- intended audience and prerequisite assumptions;
- three to seven models;
- two to six first-class relation lessons;
- an ordered sequence with an editorial reason;
- a worked contrast or case anchor;
- one practice rep per relation lesson;
- “do not overlearn this” boundaries;
- source and review status;
- a completion reflection without mastery certification.

The first journeys should be selected from source-cleared, high-quality model
and relation pages. The PRD does not preselect topics merely because their graph
centrality is high.

Teacher may use a focused graph view that highlights the current journey. It
must preserve access to the global Atlas and full pages.

## Interaction State Model

The client keeps these states distinct:

| State | Durable? | URL-addressable? | Meaning |
|---|---|---|---|
| `idle` | yes | `/atlas` | complete map with no semantic selection |
| `selected_model` | yes | query state | one model is the durable focus |
| `selected_relation` | yes | query state | one relation is the durable focus |
| `hover_preview` | no | no | temporary pointer/focus preview layered over durable selection |
| `filtered` | yes | query state | presentation subset with source counts preserved |
| `searching` | partly | query text may persist | navigation operation, not semantic ranking |
| `loading` | no | no | projection or route chunk not yet ready |
| `completed_zero` | yes | yes | valid filter/search produced no matches |
| `partial` | yes | yes | projection or page declares missing reviewed fields |
| `failed` | yes | yes | data or rendering failure; never displayed as an empty semantic result |
| `reduced_motion` | session preference | no | full functionality without ambient or long transitions |

Selection and hover must never collapse into one variable. This is a direct
acceptance requirement from the founder's reference interaction.

## Visual Direction

### Desired character

The product should feel like a navigable constellation and an editorial
reference work: calm, precise, deep, and alive. It should not look like an
admin dashboard, developer graph debugger, generic force-layout demo, or neon
science-fiction control panel.

### Composition

- dark neutral ground with restrained luminous accents;
- generous typography and negative space around explanatory copy;
- graph density concentrated in the visual field, not spread evenly across UI
  chrome;
- persistent detail panel on desktop;
- drawers or route transitions on smaller screens;
- purposeful depth through opacity, blur, scale, and layering;
- stable legend and minimal controls.

### Encoding

- default nodes use a restrained neutral treatment; a reviewed family or
  collection overlay may determine node hue, but family is not the default
  spatial backbone because current families overlap and do not cover the
  corpus;
- relation type determines edge treatment;
- selection determines emphasis;
- default node size is uniform; selected and hovered state may change scale;
  graph degree is available as disclosed detail rather than a v1 size proxy;
- confidence appears in detail, not as a visual authority halo;
- no rainbow encoding for fields that have no stable user meaning.

### Motion

- initial reveal may stage the graph without delaying interaction;
- selection transitions begin immediately and settle smoothly;
- camera motion preserves a visible origin and destination;
- hover is faster and lighter than selection;
- motion never masks data loading or rewrites topology;
- every animation has a reduced-motion equivalent.

### Responsive behavior

Desktop and large tablet receive the complete global graph. Small mobile
screens default to Library plus the selected model's local neighborhood. A
dense 222-node canvas is not forced onto a viewport where it cannot teach.

## Product-Safe Data Architecture

```text
canonical model Markdown + manifest hashes
curation + intervention semantics + relation semantics
curated relationship graph + reviewed family semantics
                  |
                  v
deterministic Atlas projection builder
  - validates IDs and references
  - preserves direction and disagreement
  - translates only approved fields
  - records missingness and licensing state
  - attaches stable precomputed coordinates
                  |
                  v
versioned public projection + hash manifest
  - graph-index.json
  - model pages or route chunks
  - relation pages or route chunks
  - journey objects
  - layout coordinates
                  |
                  v
source-controlled static web application
  - Atlas
  - Library
  - model pages
  - relation pages
  - Teacher journeys
                  |
                  +----> optional later read-only Observatory deep link
```

The builder is deterministic custody machinery. It may validate structure,
identity, source hashes, allowed fields, counts, missingness, and layout
manifest integrity. It may not decide whether a relation is semantically true,
invent copy, infer prerequisites, or “repair” missing meaning.

## Prospective Public Projection Contract

### Graph manifest

Required fields:

- schema and data version;
- canonical source manifest hash;
- relationship graph hash;
- product projection hash;
- layout algorithm/version/configuration hash;
- node and edge counts by type;
- included/excluded layer counts and reasons;
- build timestamp and builder version;
- licensing and publication status;
- non-claims.

### Model index record

Required fields:

- stable model ID and slug;
- display name and one-sentence meaning;
- reviewed family IDs;
- reviewed reasoning/use filters;
- relation counts by type;
- product page status;
- source hashes;
- curation, human-review, licensing, and missingness status;
- stable layout coordinates;
- optional connection-count visual field with non-importance label.

### Relation index record

Required fields:

- stable relation ID;
- source and target model IDs;
- ally, antagonist, or tension type;
- source-authored direction;
- reciprocity status;
- compact relation summary;
- confidence and curation status;
- relation-page status;
- source reference;
- missingness;
- no raw affinity or embedding score.

### Page and journey objects

The current v0 product contracts are useful starting evidence, not immutable
v1 schemas. V1 should extend them with:

- licensing/publication status;
- human review status per section;
- explicit direction and reciprocity;
- family and journey references;
- graph deep links;
- content provenance by section;
- stable object version and projection manifest link.

## Technical Architecture Decision

### Durable decisions

- Create a new source-controlled public web application; do not edit compiled
  Observatory output as the source of truth.
- Use TypeScript and static deployment. No server is required for the first
  product path.
- Generate the product projection offline and commit or publish it under a
  versioned manifest.
- Keep graph rendering behind a narrow adapter so the visual spike can compare
  engines without changing product contracts.
- Precompute and freeze layout coordinates. The browser may animate the camera
  and visual emphasis but must not continuously recompute semantic position.
- Use stable routes and IDs defined by this PRD.
- Split graph index data from full-page content so the first graph load does
  not download every article.
- Keep Observatory integration read-only and later.

### Contract migration decision

The Atlas does not silently add another competing Teacher page schema.

- `lolla.atlas_projection.v1` becomes the prospective public browse contract
  for Atlas nodes, exact directed relation records, pages, layout, and journeys.
- Existing `mental_model_teacher_product_contracts.py` v0 objects remain valid
  historical and small-lesson inputs; a compatibility adapter may translate
  reviewed v0 objects into the Atlas contract.
- `observatory/product_views.py` remains the bounded Observatory workspace
  contract. A later read-only adapter may reference Atlas IDs and routes.
- Relation enum expansion is explicit. The default Atlas layer accepts exactly
  `ally`, `antagonist`, and `tension`; old `compound` and Observatory-only
  relation states do not enter that layer without a new reviewed overlay.

This makes the new contract an intentional versioned product boundary rather
than a third accidental definition of the same object.

### Renderer selection gate

The first tracer bullet compares Sigma.js, Cytoscape.js, and—only if necessary
for the target depth and motion—a custom Three.js/WebGL treatment on the same
frozen 12-to-20-model projection.

Sigma.js is the recommended baseline because its WebGL renderer, Graphology
integration, event model, reducers, and custom render layers map well to
Lolla's graph size and selection choreography. Cytoscape.js is the semantic
interaction control. No alpha renderer version becomes a production dependency
without an explicit stability decision.

The founder selects the renderer from a recorded comparison using the visual,
interaction, accessibility, and performance rubric. This PRD does not select a
library by reputation alone.

## Layout Semantics

Lolla has no universal age or prerequisite axis. The layout should therefore:

- place models through graph topology with uniform relation weights; reviewed
  family overlays may annotate the result but must not force an exclusive
  partition;
- preserve direct-neighborhood discoverability;
- remain stable across visits for a given data version;
- allow explicit family overlays without pretending families are objective
  ontology;
- keep relation direction in data even if zoomed-out lines are visually
  simplified;
- record the exact seed/configuration and coordinate hash;
- avoid re-running a force simulation on every browser load.

ForceAtlas2 plus overlap removal is a reasonable initial offline candidate.
Layout metrics may be recorded for regression, but founder and cold-human
review determine whether the map is understandable and beautiful.

## Accessibility Requirements

The target is WCAG 2.2 AA for the DOM product surfaces and equivalent access to
the knowledge represented by the canvas.

Required behavior:

- keyboard selection of nodes and relations through a synchronized list or
  roving-focus control;
- predictable focus movement when panels open and close;
- accessible names and summaries for the graph, selection, visible counts,
  and filters;
- non-canvas Library, Model, Relation, and Learn routes containing the same
  durable objects;
- relation type encoded by text and line treatment, not color alone;
- contrast-tested text and controls;
- `prefers-reduced-motion` support plus an explicit pause;
- no essential information revealed only on hover;
- touch targets sized for large tablet and mobile local-neighborhood views;
- a WebGL failure fallback to Library or local relation list;
- automated accessibility checks plus manual keyboard and screen-reader review.

Canvas accessibility is not declared solved merely because the canvas has an
ARIA label.

## Performance And Interaction Budgets

The first implementation plan may refine measurement tooling, but it may not
weaken these user-facing thresholds without recording a founder decision.

| Requirement | Initial acceptance budget |
|---|---|
| Desktop reference viewport | 1920 x 1200 |
| Global projection | 222 nodes in the idle scene; 1,358 exact default relation records available through focus/search |
| Idle relation display | 0 edges until a model, relation, or explicit overlay is selected |
| Focused relation display | <= 40 exact directed relation records per canvas page, with total and omitted counts |
| Initial graph payload | target <= 500 KB compressed, excluding full model/relation bodies |
| First useful graph paint | <= 2.5 seconds on the agreed reference profile |
| Pointer/keyboard visual acknowledgement | begins within 100 ms |
| Hover preview | visible within 100 ms without selection loss |
| Selection transition | begins within 100 ms and settles within 450 ms unless reduced-motion |
| Steady pan/zoom/selection | target p95 frame time <= 20 ms on the agreed reference desktop |
| Layout stability | no node-coordinate recomputation or visible global relayout after first paint |
| Route transition to prebuilt page | target <= 200 ms after asset is cached |
| Reduced-motion mode | all core tasks possible with no ambient animation |

The agreed reference profile, browser version, cold/warm cache, and throttling
settings must be stored with the performance receipt. “It looked smooth on the
developer's laptop” is not a measurement.

## Visual Quality Gate

The first tracer bullet records the following scenarios at 1920 x 1200:

1. global idle composition;
2. selected model with global context dimmed but present;
3. persistent selected model plus a different hovered model;
4. selected relation panel;
5. family and relation filter applied;
6. reduced-motion behavior;
7. keyboard-accessible equivalent view.

The structural regression set also includes mixed parallel relations,
bidirectional records, the 233-record `confirmation-bias` hub, one
medium-confidence relation, a completed-zero filter, and a corrupt/missing
source case.

Review dimensions:

- compositional hierarchy;
- label legibility and density;
- model/edge state clarity;
- camera continuity;
- motion restraint;
- panel usefulness;
- typography and spacing;
- visual distinction from a graph debugger;
- no false semantic encoding;
- functional accessibility alternative.

Automated screenshots detect unintended drift. Founder and cold-human review
decide whether the bar is met. The Marble reference is not used for pixel
matching.

## Content, Licensing, And Publication Gate

The current repository proves source identity and curation custody; it does not
by itself prove that every canonical article or derivative paragraph is cleared
for public redistribution.

Before any public full-corpus launch:

- record authorship and license status for every published model source;
- record whether translated curation can be published and under which notice;
- separate internal source quotes from public-safe excerpts or summaries;
- add required attribution and license notices;
- reject unknown publication status rather than assuming repository presence
  grants public rights;
- keep local machine paths from the historical manifest out of public payloads;
- run privacy and secret scans over generated artifacts;
- confirm that no private run, conversation, provider response, or evaluation
  artifact enters the public build.

The first local tracer bullet may use checked-in source for internal review.
Public deployment is blocked until this gate passes.

## Real-User Evidence Plan

The plan has three gates. Each requires separate authorization to perform.

### Gate A: cold product truthfulness review

Reviewers receive the built slice, not implementation explanations. They must:

- find a named model through graph and library;
- explain the selected model in their own words;
- identify one ally, antagonist, and tension when present;
- explain one relation without converting it into universal truth;
- identify what node size/color and edge confidence do and do not mean;
- reach the full pages and complete one practice rep;
- identify missing or unreviewed content.

Failure occurs if the interface itself cannot support those distinctions.

### Gate B: bounded learner usefulness study

With explicit consent, recruit people in the intended knowledge-worker audience
who did not build Lolla. Observe whether the Atlas and journey help them form a
more accurate, memorable, and usable understanding than a model list or static
article alone.

Evidence includes:

- task completion and navigation path;
- pre/post explanation of the model relationship;
- correction burden;
- whether the graph added orientation or distraction;
- whether practice changed recall or transfer in a later prompt;
- privacy and trust reactions;
- qualitative evidence of value, confusion, and overclaiming.

No scalar score decides the outcome. Preserve the evidence vector and
disagreement.

### Gate C: investment decision

Choose whether to expand the corpus and journeys, revise the product shape,
keep only the public library/pages, or re-park Teacher. Visual enthusiasm is not
enough if learning and truthfulness do not survive cold use.

## Analytics And Privacy

The first local product slice requires no analytics. Any later public analytics
must be separately approved and privacy-minimal.

Allowed prospective aggregate events:

- route opened;
- graph/list mode selected;
- node or relation opened by stable public ID;
- journey step completed;
- reduced-motion or fallback mode used;
- performance/error measurements without conversation or article text.

Forbidden:

- private conversation content;
- run archives or user prompts;
- inferred decision state;
- model-based user profiling;
- silent cross-product identity linkage;
- using exploration behavior to infer psychological traits.

## Existing Assets To Reuse Carefully

Reuse as implementation evidence:

- existing v0 product-safe contracts;
- model/relation pilot page builders and renderers;
- lesson and lesson-neighborhood graph contracts;
- Observatory read-only adapter boundaries;
- source manifests, missingness, and non-claim patterns;
- current static prototypes as “before” evidence;
- Stage 0 lifecycle and file-assignment discipline.

Do not treat as current product authority:

- the old preference for small graphs before any global graph;
- the statement “Observatory is the house” for the public product;
- package completion as human validation;
- the three simulated Teacher cases as market evidence;
- dependency-free SVG as the quality target;
- importability or test coverage as runtime reachability;
- old recommended-next-PR labels as the current roadmap.

## Scope Of The First Authorized Tracer Bullet

The first slice, if authorized, includes:

- one frozen 12-to-20-model neighborhood sampled from real canonical models;
- all real default relation types represented when the substrate permits;
- one deterministic product projection and manifest;
- stable offline coordinates;
- a source-controlled static app shell;
- global/selected/hover/relation/filter states;
- one complete model page and one complete relation page;
- synchronized list/keyboard/reduced-motion alternative;
- the renderer comparison and recorded visual review;
- no provider calls;
- no public deployment;
- no runtime or Observatory integration;
- no generated semantic content.

This is deliberately a vertical slice through source, projection, graph,
interaction, pages, accessibility, tests, and review. It is not a horizontal
“build the graph data first” project.

## Explicitly Out Of Scope

- R4, R5, or any arbitrary-conversation semantic reader;
- general Decision Trail generation;
- automatic Decision Work supply;
- live Lolla runtime changes;
- mental-model retrieval or embedding changes;
- relationship graph curation changes;
- provider or model calls;
- public full-corpus deployment before licensing review;
- user accounts, progress synchronization, badges, or mastery scores;
- personalized model recommendations;
- authoring UI;
- graph editing;
- a 3D requirement for its own sake;
- copying Marble's taxonomy, text, code, colors, or brand;
- claiming product usefulness before real-user evidence.

## Risks And Controls

### Decorative graph risk

Control: every selected node and edge must lead to useful content; cold tasks
measure understanding, not admiration.

### Spaghetti graph risk

Control: all source objects remain available, while zoomed-out visibility,
progressive disclosure, relation filters, and direct-neighborhood emphasis are
explicit presentation states with visible counts.

### False hierarchy risk

Control: no universal prerequisite axis, no age axis, no centrality-as-value,
and no unnamed multi-hop semantics.

### Visual quality becomes endless polish

Control: freeze reference scenarios and acceptance thresholds; select one
renderer after a bounded comparison; stop if none can meet the bar within the
first slice's timebox.

### Teacher duplicates the live pressure system

Control: Teacher consumes public model/relation projections and curated
journeys. It does not select pressure for a live answer.

### Observatory coupling

Control: public routes and projection are independently deployable. Observatory
integration is a later read-only consumer.

### Source drift

Control: stable IDs, source hashes, projection manifest, frozen coordinates,
and deterministic validation.

### Public rights uncertainty

Control: licensing status is a required field and public launch gate.

### Graph salience becomes authority

Control: truthful legend, non-color encodings, equal or explicitly explained
size rules, full relation pages, and cold reviewer tasks.

### Accessibility becomes a fallback afterthought

Control: the first tracer bullet includes the synchronized non-canvas path and
reduced-motion behavior; they are not a later phase.

### Prototype estate creates more confusion

Control: preserve old artifacts as historical evidence, label this v1 as the
prospective current design, and do not rewrite or delete historical packages.

## Success Criteria For V1 Investment

All of the following are required before calling the lane “earned”:

- deterministic projection of the selected canonical substrate passes custody
  validation;
- founder visual review says the graph meets the intended quality bar;
- cold reviewers can navigate and interpret model/relation semantics without
  recurrent authority errors;
- non-canvas access supports the same durable knowledge objects;
- model and relation pages are useful without the graph;
- at least one curated journey teaches a relationship and practice rep without
  presenting advice or mastery certification;
- publication-rights gate is complete for anything made public;
- bounded learner evidence shows incremental value over a list/static article;
- no runtime, private conversation, R4, or action-authority boundary is crossed.

Failure of the visual slice means revise or stop the interface architecture.
Failure of truthfulness means correct the product contract before expansion.
Failure of learner usefulness means re-park or narrow the product even if the
visual work is excellent.

## Remaining Decisions And Unknowns

This PRD intentionally leaves these for evidence:

- whether Sigma.js, Cytoscape.js, or a custom WebGL layer best meets the bar;
- whether a 2D constellation, restrained 2.5D depth, or full 3D treatment best
  serves comprehension;
- which family semantics are ready for public clustering;
- which model articles and source quotes are publication-cleared;
- which first journey has the best user job and source quality;
- how many model pages already have sufficient translated content;
- whether users gain meaningful understanding from the global map;
- whether Teacher should become a standalone product, a public Lolla surface,
  or remain a bounded learning lane;
- whether read-only run deep links add value after the public product works.

## Implementation Sequence

The implementation sequence is defined in the linked tracer-bullet plan. Its
order is binding unless a founder decision changes it:

1. visual truth tracer bullet;
2. complete Atlas projection and stable global layout;
3. complete navigation and durable model/relation pages;
4. curated Teacher journey;
5. optional read-only Lolla/Observatory bridge;
6. real-user evidence and architecture decision.

Each phase is independently reviewable and has a stop line. No phase
automatically authorizes the next.

## Current Decision And Next Founder Gate

Selected planning decision:

```text
mental_model_atlas_teacher_prd_ready_for_tracer_bullet_decision
```

The exact next founder decision after this PRD is reviewed and canonically
published is whether to authorize only Phase 1, provider-free and local:

```text
authorize_mental_model_atlas_visual_truth_tracer_bullet
```

That authorization must not imply a full-corpus build, public deployment,
runtime integration, provider call, Observatory expansion, conversation reader,
or product-usefulness claim.

## PRD Non-Claims

- `not_product_proof`
- `not_human_validation`
- `not_market_validation`
- `not_publication_rights_clearance`
- `not_runtime_integration`
- `not_observatory_ownership`
- `not_r4_or_decision_trail_restart`
- `not_action_authorization`
- `not_graph_relevance_proof`
- `not_relation_truth_certification`
- `not_mastery_certification`
- `not_provider_authorization`
- `not_implementation_authorization`

Provider calls made for this PRD: `0`

Provider cost: `$0.00`

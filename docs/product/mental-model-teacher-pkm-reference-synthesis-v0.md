# Mental Model Teacher PKM Reference Synthesis v0

Status: design research synthesis
Date: 2026-07-05
Decision gate: `use_reference_patterns_to_refine_learner_surface`

## Purpose

This note captures what the Mental Model Teacher visual-library design should
learn from open-source PKM, second-brain, note-linking, graph, publishing, and
knowledge-graph projects.

It does not recommend copying any single product. The goal is to extract product
patterns for:

- displaying data;
- presenting data with hierarchy;
- letting users pick data;
- letting users search through data;
- switching between data contexts;
- treating some data as primary and other data as supporting, inferred, or
  review-only.

## Reading Frame Before Looking At References

Before evaluating reference projects, these are the design aspects that matter
for Mental Model Teacher.

### 1. What Is The Primary Object?

The UI must make it obvious what object the user is looking at.

Candidate primary objects:

- Teacher lesson;
- mental model;
- model relation;
- practice rep;
- graph neighborhood;
- source receipt;
- review packet.

The key design question is whether the current screen is teaching from a case,
explaining a model, explaining a relation, showing a map, or supporting review.

### 2. What Is First-Class vs Supporting Data?

Every system has some data that is primary and other data that is supporting.

For Mental Model Teacher:

- first-class learner objects: lesson, model, relation, practice rep;
- first-class navigation objects: collection, graph neighborhood, search result;
- supporting objects: source receipt, curation status, missingness, hashes;
- internal-only objects: raw telemetry, raw generated JSON, validation logs,
  review manifests, embedding internals.

The UI should never present all classes with equal visual weight.

### 3. How Does The User Find Relevant Data?

Users need more than graph browsing.

Discovery should combine:

- search;
- filters;
- typed object lists;
- backlinks;
- "appears in" sections;
- graph neighborhoods;
- suggested related content clearly labeled as suggestion.

### 4. How Does The User Switch Context?

Switching must preserve context.

Useful context switches:

- lesson -> model page;
- lesson -> relation page;
- relation page -> graph with that edge selected;
- model page -> lessons where the model appeared;
- graph node -> model page;
- graph edge -> relation page;
- any product object -> receipts or review mode.

### 5. How Much Graph Should The User See?

The graph should be a map, not the first explanation.

The v0 question is not "Can we draw the graph?" It is "Can the graph help the
user move after the lesson already makes sense?"

### 6. How Are Inferred Or AI-Discovered Connections Labeled?

Some references use embeddings or LLMs to find related data. That is useful, but
Mental Model Teacher has a stronger product boundary:

- curated relations can be shown as relations;
- semantic neighbors can be shown only as suggestions;
- graph edges are navigation, not proof;
- confidence is not certification.

### 7. What Should Be Hidden Until Needed?

Good PKM tools expose structure, but they do not require the user to inspect
every internal mechanism on every page.

Mental Model Teacher should hide these by default:

- raw source paths;
- source hashes;
- full non-claim tag walls;
- raw Teacher cards;
- generated manifests;
- validation reports;
- package gates.

They should remain available through receipts, review mode, or builder mode.

## Source Patterns

### Logseq

Source: [Logseq GitHub](https://github.com/logseq/logseq)

Relevant observed patterns:

- frames itself as privacy-first knowledge management;
- emphasizes privacy, longevity, user control, Markdown, Org-mode, and multiple
  tools for organizing and structuring notes;
- includes graph concepts and a newer DB graph track, with explicit beta caution.

Design lesson:

- use graph as a durable navigation layer, not as the first explanation;
- keep static, source-controlled product data as the first v0 substrate;
- communicate caution around unstable or not-yet-reviewed graph surfaces.

Mental Model Teacher decision:

- Learn mode remains first;
- Map mode starts with focused neighborhoods;
- any full-corpus graph waits until page-level learning works.

### SiYuan

Source: [SiYuan GitHub](https://github.com/siyuan-note/siyuan)

Relevant observed patterns:

- supports fine-grained block-level reference;
- supports two-way links;
- uses WYSIWYG presentation over structured content;
- includes custom attributes, SQL query embeds, block zoom, and table views.

Design lesson:

- model and relation pages should be made of addressable sections;
- links should be able to point to a section, not only a whole page;
- users benefit from block zoom or local focus when pages become dense.

Mental Model Teacher decision:

- each model page section should have a stable anchor;
- lesson pages should link to the exact section that teaches the relevant move;
- receipts and missingness should be panel sections, not the whole page.

### Foam

Source: [Foam GitHub](https://github.com/foambubble/foam)

Relevant observed patterns:

- graph visualization is a command over linked notes;
- link autocomplete helps users make connections;
- file rename sync keeps links consistent;
- backlinks support relationship discovery;
- unique identifiers avoid ambiguous links.

Design lesson:

- link integrity is part of UX, not just implementation hygiene;
- backlinks are a low-drama way to show "where else this appears";
- graph is useful when it rests on a clean link model.

Mental Model Teacher decision:

- model pages need "Appears in lessons" backlinks;
- relation pages need "Used in lessons" backlinks;
- static builds must check local links as product behavior.

### Reor

Source: [Reor GitHub](https://github.com/reorproject/reor)

Relevant observed patterns:

- notes are chunked and embedded into an internal vector database;
- related notes are connected automatically through vector similarity;
- semantic search and RAG-style Q&A are part of discovery;
- a related-notes sidebar augments writing or reading.

Design lesson:

- semantic discovery is valuable when it is a side panel, not doctrine;
- suggestions should be clearly weaker than curated links.

Mental Model Teacher decision:

- v0 should not expose embeddings;
- later semantic neighbors can appear as "Suggested nearby models";
- suggestions must be visually second-class to curated model relations.

### TriliumNext

Source: [TriliumNext GitHub](https://github.com/TriliumNext/Trilium)

Relevant observed patterns:

- hierarchical note tree supports very large personal knowledge bases;
- one note can appear in multiple places in the tree;
- full text search and note hoisting help users narrow scope;
- attributes support organization and querying;
- relation maps and note/link maps visualize relations.

Design lesson:

- hierarchy and graph should coexist;
- one model should be able to appear in multiple collections;
- "hoisting" or focusing on one local branch is a useful density control.

Mental Model Teacher decision:

- library collections should be hierarchical enough to orient users;
- model pages can belong to multiple collections, such as risk, uncertainty, or
  communication;
- graph neighborhoods should support focus/reset rather than forcing the full
  map.

### Dendron

Source: [Dendron GitHub](https://github.com/dendronhq/dendron)

Relevant observed patterns:

- starts with plain text and lets structure grow over time;
- schemas give consistency, autocomplete hints, and templates;
- lookup is a unified way to find and create notes;
- navigation includes backlinks, notes, headers, arbitrary blocks, and graph
  view;
- publishing can be permissioned by vault, hierarchy, or note.

Design lesson:

- consistent object templates reduce UX chaos;
- search and creation share a mental model;
- publishing boundaries matter when internal and user-facing material coexist.

Mental Model Teacher decision:

- product contracts are right, but the UI needs corresponding templates;
- search should return typed results: lesson, model, relation, practice;
- review/debug artifacts should require an explicit mode.

### AppFlowy

Source: [AppFlowy GitHub](https://github.com/AppFlowy-IO/AppFlowy)

Relevant observed patterns:

- presents work through multiple views, including kanban boards, databases,
  documentation sites, templates, and AI;
- emphasizes user control over data.

Design lesson:

- not every data relationship needs a graph;
- lists, cards, tables, and boards can orient faster than a network.

Mental Model Teacher decision:

- Models mode should start with cards/list/search;
- Relations mode should support relation-type filters and pair cards;
- Map mode is one view, not the whole product.

### Anytype

Sources:

- [Anytype GitHub](https://github.com/anyproto/anytype-ts)
- [Anytype Properties documentation](https://doc.anytype.io/anytype-docs/getting-started/types/relations)

Relevant observed patterns:

- objects have types and properties;
- properties define both attributes and connections;
- properties enable sorting and filtering in queries;
- object-reference properties can link one object to another;
- properties can be shown in headers, panels, hidden areas, or local contexts.

Design lesson:

- object type plus relation metadata is a strong model for connected data;
- properties can have different visibility tiers;
- connection metadata should power both search/filtering and graph display.

Mental Model Teacher decision:

- core object types should be explicit: Lesson, Model, Relation, Practice,
  Collection, Case Anchor, Receipt;
- properties should have visibility tiers: header, panel, hidden receipts,
  internal-only;
- relation metadata should power relation pages, filters, and graph edges.

### Notesnook

Source: [Notesnook GitHub](https://github.com/streetwriters/notesnook)

Relevant observed patterns:

- clean note-taking product focused on privacy and ease of use;
- privacy is part of the product promise rather than a visual gimmick;
- the UI direction is calm note consumption rather than graph-first spectacle.

Design lesson:

- user trust can come from restraint;
- readability is a product feature.

Mental Model Teacher decision:

- model pages should be calm and readable;
- graph density should never compete with the explanation;
- non-claims should read like boundaries, not legal telemetry.

### Pubsidian

Source: [Pubsidian GitHub](https://github.com/yoursamlan/pubsidian)

Relevant observed patterns:

- turns Obsidian-style notes into a static website;
- includes responsive notes, graph view, search, last-state restoration, and
  share-current-note behavior;
- uses D3 for graph rendering.

Design lesson:

- a lightweight static product can still feel interactive;
- search and shareable URLs matter even before an app exists;
- restoring the previous view can make exploration feel continuous.

Mental Model Teacher decision:

- the next static prototype should preserve selected case and mode in the URL or
  local state;
- graph and search can be static/offline;
- every model, relation, and lesson needs a stable shareable link.

### Flowershow

Source: [Flowershow GitHub](https://github.com/flowershow/flowershow)

Relevant observed patterns:

- publishes Markdown and HTML websites quickly;
- supports Obsidian-oriented workflows and wiki-style links through a
  `remark-wiki-link` package;
- treats API contracts as a single source of truth for web, CLI, and related
  surfaces.

Design lesson:

- static publishing is enough for product-shape review;
- wiki-link handling matters when content is link-heavy;
- a contract-first publishing path avoids UI/source mismatch.

Mental Model Teacher decision:

- continue static/offline first;
- product objects should remain the source for rendered pages;
- wiki-style shortcuts may be useful later, but v0 can use explicit static
  routes.

### Neurite

Source: [Neurite GitHub](https://github.com/satellitecomponent/Neurite)

Relevant observed patterns:

- uses a graph-of-thought canvas for text, images, web links, PDFs, code, and AI
  nodes;
- supports zoom-to-node and bidirectional sync between mind map and text-based
  notes;
- treats graph nodes as dynamic objects;
- includes a warning because the visual layer can be intense.

Design lesson:

- rich canvases can make relations feel alive, but they can overwhelm;
- zoom-to-node is a useful interaction;
- bidirectional sync between visual and textual representations is powerful.

Mental Model Teacher decision:

- do not start with an infinite canvas;
- use zoom/focus for selected model and relation;
- ensure graph selection and page selection stay synchronized.

### knowledge_graph

Source: [knowledge_graph GitHub](https://github.com/rahulnyk/knowledge_graph)

Relevant observed patterns:

- describes a pipeline: clean corpus, extract concepts, extract relations,
  create graph schema, populate nodes/edges, visualize/query;
- distinguishes concepts from entities;
- uses graph algorithms such as centrality and community detection;
- calls visualization optional and suggests a frontend flow where the user first
  selects topics, then expands subtopics.

Design lesson:

- graph generation is a pipeline, not a product by itself;
- concept/entity distinctions matter;
- user-driven expansion is often better than dumping the whole graph.

Mental Model Teacher decision:

- do not generate or display new relation claims in v0;
- support "pick a topic/reasoning move first, then expand";
- use community/family information later as navigation hints, not proof.

### Graphify

Sources:

- [Graphify GitHub](https://github.com/safishamsi/graphify)
- [Graphify website](https://graphify.net/)

Relevant observed patterns:

- produces three different outputs: `graph.html`, `GRAPH_REPORT.md`, and
  `graph.json`;
- interactive graph output supports clicking nodes, filtering, and search;
- report output highlights key concepts, surprising connections, suggested
  questions, and confidence tags;
- inferred relationships are labeled as found, inferred, or ambiguous;
- query-first workflow avoids repeatedly reading raw files.

Design lesson:

- different outputs should serve different jobs;
- an audit/report artifact is not the same as a learner UI;
- inferred connections need visible confidence tags;
- query/search can be a first-class navigation tool.

Mental Model Teacher decision:

- keep learner UI, graph UI, JSON objects, and review reports separate;
- graph relation confidence should be visible in relation pages and receipts,
  but not framed as proof;
- search should answer "where should I go next?" before showing raw artifacts.

## Cross-Reference Synthesis

### Pattern 1: Graph Is A View, Not The Product

Logseq, Foam, Trilium, Pubsidian, Neurite, knowledge_graph, and Graphify all use
graphs, but the successful product lesson is not "open with all nodes." The graph
works best when paired with a readable object, a selected focus, and controls.

Decision:

- Mental Model Teacher should not open on a global graph.
- The graph opens as Map mode with a selected lesson, node, or relation.
- Edge click opens a relation page.
- Node click opens a model page.

### Pattern 2: Search Must Be Typed

Dendron's lookup, Foam's wikilink autocomplete, Reor's semantic search,
Pubsidian's note search, AppFlowy's database views, and Anytype's queryable
properties all point to the same product need: search results should be typed.

Decision:

Search results should be grouped:

- lessons;
- models;
- relations;
- practice reps;
- collections;
- receipts only when Review mode is active.

### Pattern 3: Backlinks Make Connections Understandable Without A Graph

Foam, Dendron, SiYuan, and Logseq show that backlinks are often clearer than a
visual graph for answering "where does this appear?"

Decision:

- model pages need "Appears in lessons";
- relation pages need "Used in lessons";
- lessons need "Models used" and "Relations used";
- graph is optional reinforcement, not the only connection surface.

### Pattern 4: Typed Objects Beat Generic Notes

Anytype, AppFlowy, Dendron, and Trilium all benefit from typed objects,
attributes, views, and schemas.

Decision:

Mental Model Teacher should treat these as typed objects:

- Lesson;
- Model;
- Relation;
- Practice Rep;
- Collection;
- Case Anchor;
- Receipt;
- Review.

Each type needs its own template and visibility rules.

### Pattern 5: Visibility Tiers Prevent Product Confusion

Anytype's header/panel/hidden/local properties, Dendron's publish permissions,
and our own review-surface failure all point to the same rule: not all data
belongs on the first screen.

Decision:

Use four visibility tiers:

| Tier | Meaning | Examples |
|---|---|---|
| Primary | learner-facing content | situation, trap, move, model pair, practice |
| Context | useful navigation and explanation | model links, relation links, graph preview |
| Receipts | trust and custody | sources, missingness, curation status, non-claims |
| Internal | builder/debug only | raw JSON, validation logs, hashes, raw telemetry |

### Pattern 6: Suggested Links Must Be Weaker Than Curated Links

Reor, Neurite, knowledge_graph, and Graphify all show the appeal of AI-assisted
connection discovery. Mental Model Teacher must preserve a stricter boundary.

Decision:

- curated relation semantics become relation pages;
- relationship graph edges become navigation;
- embedding neighbors remain hidden in v0;
- later semantic suggestions must be labeled as suggestions and separated from
  reviewed relation pages.

### Pattern 7: Static First Is A Strength

Foam, Dendron, Pubsidian, Flowershow, and Graphify all show that static or
file-backed outputs are enough for useful review and navigation.

Decision:

- keep the next prototype static and offline;
- use stable routes and link checks;
- avoid runtime wiring;
- make generated HTML reviewable before making it app-like.

## Concrete UX Implications

### Learn Mode

Recommended layout:

- left rail: case picker and lesson steps;
- main column: situation, trap, move, relation story, worked example, practice;
- right rail: model pair, tiny graph preview, explore links;
- receipts drawer collapsed.

Primary data:

- case anchor;
- reasoning trap;
- thinking move;
- model relationship;
- practice rep.

Secondary data:

- graph preview;
- model links;
- relation links.

Hidden by default:

- raw source artifacts;
- generated JSON;
- review controls;
- full non-claim lists.

### Models Mode

Recommended layout:

- search and filters at top or left;
- card/list view as default;
- optional compact graph/list hybrid later;
- model page opens in main content.

Filters:

- reasoning type;
- use case;
- model family;
- relation type;
- appears in lesson;
- curation completeness.

### Relations Mode

Recommended layout:

- relation-type filter;
- pair cards;
- selected relation page;
- related lessons and model links.

Relation cards should show:

- model A;
- relation type;
- model B;
- one-sentence relation story;
- used-in lesson count;
- confidence/status as modest metadata, not proof.

### Map Mode

Recommended layout:

- graph canvas;
- selected node/edge side panel;
- filters and search;
- "open model page" and "open relation page" actions;
- "return to lesson" action.

Default:

- focused lesson neighborhood;
- selected relation;
- 3 to 10 nodes;
- no full-corpus graph in v0.

### Review Mode

Recommended layout:

- product object preview;
- source comparison;
- missingness;
- blank human review form;
- overclaiming checklist.

Review mode should never be the default route.

## Revised Next-Slice Acceptance Criteria

The next UI slice should prove these design decisions:

- the first screen teaches before it maps;
- search results are typed;
- model and relation pages are first-class pages, not raw Markdown dumps;
- graph opens with a selected context;
- backlinks exist without needing the graph;
- receipts are collapsed but reachable;
- review/debug data is not in the learner's primary surface;
- no AI-discovered relation is surfaced as a curated relation;
- no graph edge is presented as proof.

## Boundary

This design research note does not run Lolla, invoke the Lolla skill, call
provider/model APIs, create new Lolla runs, generate new relation claims, wire
runtime behavior, claim product proof, claim human validation, claim answer
correctness, claim advice correctness, score output quality, treat graph edges
as proof, treat embeddings as validated relations, or authorize action.

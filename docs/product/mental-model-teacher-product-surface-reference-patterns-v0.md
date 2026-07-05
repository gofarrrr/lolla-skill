# Mental Model Teacher Product Surface Reference Patterns v0

Status: reference audit for PRD planning

This note records what we should learn from current open-source knowledge-base,
PKM, digital-garden, graph, and graph-generation projects before building the
Mental Model Teacher product surface.

The goal is not to clone any of these projects. The goal is to understand useful
patterns so Lolla can present its canonical mental-model corpus and Teacher
outputs as a product people can browse, click, and learn from.

## Product Lens

The surface we want is not Observatory, not Decision Work, and not Product Delta.

Observatory explains a run.
Decision Work preserves decision artifacts.
Product Delta is internal evidence discipline.
Mental Model Teacher teaches transferable reasoning moves.
The visual mental-model library makes those moves and their relations browsable.

The user should be able to:

- open a mental model and understand it without reading raw curation files;
- see how that model connects to allies, tensions, antidotes, and failure modes;
- click from a Teacher lesson into model and relation pages;
- inspect a small graph neighborhood around the lesson;
- browse the larger corpus without assuming the graph proves correctness.

## Reference Project Lessons

### Logseq

Source: https://github.com/logseq/logseq

Useful pattern:

- local-first, privacy-first knowledge graph framing;
- graph as navigation through knowledge, not as a correctness proof;
- Markdown/Org style durability and user control;
- graph surfaces can be useful, but beta graph systems can carry data-loss or
  stability risk.

Lolla lesson:

- keep the first product graph read-only and derived;
- make the default graph a focused neighborhood, not the entire corpus;
- keep canonical Markdown and curation JSON as the source of truth.

Avoid:

- letting the graph become a large undifferentiated canvas;
- making the graph editor the first product.

### SiYuan

Source: https://github.com/siyuan-note/siyuan

Useful pattern:

- block-level references and two-way links;
- WYSIWYG presentation over structured Markdown-like content;
- custom attributes and structured block metadata.

Lolla lesson:

- a mental model page should not be one long Markdown dump;
- sections such as "use when", "avoid when", "failure mode", "practice",
  "ally", and "tension" should be addressable blocks;
- Teacher lessons should link to a specific section when that section explains
  the move, not only to the whole model page.

Avoid:

- exposing block IDs or internal curation metadata to normal users.

### Foam

Source: https://github.com/foambubble/foam

Useful pattern:

- Git-friendly Markdown knowledge base;
- graph visualization over linked notes;
- backlinks and link maintenance;
- publishable references that still work in GitHub-like environments.

Lolla lesson:

- keep model and relation pages linkable as static files first;
- build backlinks from model pages to Teacher lessons and relation pages;
- test links as product behavior, not just documentation hygiene.

Avoid:

- relying on editor-specific behavior for the first version.

### Reor

Source: https://github.com/reorproject/reor

Useful pattern:

- local AI can suggest related notes through embeddings and semantic search;
- related-note discovery can augment human thought without replacing the human.

Lolla lesson:

- semantic-neighbor suggestions may be useful later;
- v0 should keep curated relations as source-of-truth relations;
- any embedding or semantic similarity layer must be labeled as suggestion, not
  doctrine.

Avoid:

- letting vector similarity overwrite curated relations;
- presenting auto-discovered relations as validated teaching links.

### TriliumNext

Source: https://github.com/TriliumNext/Trilium

Useful pattern:

- one note can appear in multiple places;
- hierarchy and network can coexist;
- rich note pages can support large knowledge bases.

Lolla lesson:

- a mental model can appear in multiple learning paths;
- hierarchy should organize the library, while the relation graph explains cross
  links;
- a model page can belong to several use-case collections.

Avoid:

- forcing exactly one taxonomy position per model.

### Dendron

Source: https://github.com/dendronhq/dendron

Useful pattern:

- gradual structure over plain text;
- schemas and templates for consistency;
- backlinks, graph view, refactors, and publishable vaults.

Lolla lesson:

- define model-page, relation-page, and lesson-page schemas before rendering;
- preserve static files and Git reviewability;
- make structure stricter where product clarity needs it, but allow later
  expansion.

Avoid:

- turning the product into a maintainer-only schema exercise.

### AppFlowy

Source: https://github.com/AppFlowy-IO/AppFlowy

Useful pattern:

- database and card views can be as important as graph views;
- product pages need filters, search, collections, and readable cards.

Lolla lesson:

- the library needs a card/list view beside the graph;
- users should browse by use case, relation type, model family, and practice
  type;
- graph view is a view, not the only product.

Avoid:

- opening with a complicated graph when a card list would orient the user faster.

### Anytype

Source: https://github.com/anyproto/anytype-ts
Source: https://doc.anytype.io/anytype-docs/getting-started/types/relations

Useful pattern:

- knowledge objects have types and properties;
- relations connect objects and make the graph inspectable.

Lolla lesson:

- product objects should be typed: Mental Model, Relation, Teacher Lesson,
  Practice Drill, Model Family, Case Anchor;
- relations should be objects users can click, not just graph edges.

Avoid:

- burying relation meaning inside a visual edge with no explanation.

### Notesnook

Source: https://github.com/streetwriters/notesnook

Useful pattern:

- privacy-first, clean note presentation;
- minimalism can beat a visually busy knowledge graph.

Lolla lesson:

- model pages should feel calm and readable;
- graph interaction should not obscure the model explanation.

Avoid:

- decorative complexity that makes the library feel like internal telemetry.

### Pubsidian and Flowershow

Sources:

- https://github.com/yoursamlan/pubsidian
- https://github.com/flowershow/flowershow

Useful pattern:

- Markdown can become a browsable website;
- wiki links and Obsidian-style publishing patterns are useful for static
  knowledge surfaces.

Lolla lesson:

- v0 can be a static generated surface before any app integration;
- generated Markdown or HTML should be enough to review the product shape;
- publish control and link checking matter.

Avoid:

- treating static publishing as the final UX if interaction is needed for graph
  exploration.

### Neurite

Source: https://github.com/satellitecomponent/Neurite

Useful pattern:

- graph-of-thought canvases can make idea relationships feel alive;
- dynamic mind-mapping can support exploration.

Lolla lesson:

- later versions may explore richer visual canvases;
- v0 should stay grounded in selected neighborhoods and clear reading flows.

Avoid:

- making the product feel like a sci-fi graph demo instead of a learning tool.

### knowledge_graph and Graphify

Sources:

- https://github.com/rahulnyk/knowledge_graph
- https://github.com/Graphify-Labs/graphify

Useful pattern:

- corpus-to-graph pipelines usually emit graph data plus a visual artifact and
  report;
- generated graph artifacts can be reviewed separately from the raw corpus.

Lolla lesson:

- the visual library should have generated artifacts such as `model_pages.json`,
  `relations.json`, `graph.json`, and a human-readable build report;
- graph generation should be deterministic from canonical/curated inputs first;
- LLM graph extraction can be considered later only with source refs and review.

Avoid:

- using LLM extraction to invent relation topology in v0.

### Quartz and Obsidian Digital Garden

Sources:

- https://github.com/jackyzha0/quartz
- https://github.com/oleeskild/obsidian-digital-garden

Useful pattern:

- Markdown gardens can become clean browsable websites;
- publish scope can be explicit and controlled.

Lolla lesson:

- a static product pilot can be enough for review;
- the full corpus should not be published automatically until the subset UX works;
- publishable pages should have stable slugs.

Avoid:

- assuming every internal note belongs in a public garden.

### Cytoscape.js and Sigma.js

Sources:

- https://js.cytoscape.org/
- https://www.sigmajs.org/

Useful pattern:

- Cytoscape.js supports interactive graph visualization plus graph analysis;
- Sigma.js is oriented toward rendering large browser graphs with many nodes and
  edges.

Lolla lesson:

- Cytoscape.js is a good first candidate for focused graph neighborhoods because
  interaction and relation semantics matter more than scale;
- Sigma.js is a later candidate if the full 222+ model corpus becomes visually
  heavy;
- the graph renderer must support selected-node focus, neighbor expansion, edge
  labels, search, and click-through side panels.

Avoid:

- starting with the full graph if a 5 to 15 node lesson neighborhood teaches
  better.

## Cross-Project Principles For Lolla

1. Static source first, visual surface second.
2. Graph as navigation and teaching, not proof.
3. Focused neighborhood before full corpus.
4. Relations need pages, not only edges.
5. Model pages need human language, not raw curation dumps.
6. Teacher lessons should link to models, relation explanations, and practice
   drills.
7. The visual library should preserve source custody and non-claims.
8. AI-discovered links should be suggestions until reviewed.
9. Search, cards, and collections matter as much as a graph.
10. Full-corpus publishing waits until the subset product works.

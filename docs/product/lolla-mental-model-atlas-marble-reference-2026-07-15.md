# Lolla Mental Model Atlas: Marble Reference Study

Status: founder reference and current-practice note; prospective only

Date checked: 2026-07-15

Applies to: [Lolla Mental Model Atlas and Teacher PRD v1](lolla-mental-model-atlas-and-teacher-prd-v1.md)

## Purpose

This note records what Lolla should learn from Marble's public curriculum graph
and from the founder's local reference recording. It is not a request to copy
Marble's product, taxonomy, visual identity, source code, data, or wording.

The useful reference is the product choreography:

```text
show the whole territory
  -> let one concept become legible without erasing the territory
  -> make its immediate structure obvious
  -> keep a durable detail panel while hover remains exploratory
  -> let each selection become the next doorway
```

## Founder Reference Recording

The founder supplied a local screen recording of the Marble curriculum
explorer. The recording is not committed to this repository.

| Field | Value |
|---|---|
| Local filename | `Nagranie z ekranu 2026-07-15 o 17.47.06.mov` |
| SHA-256 | `910bdb4f96e4af499ae62bce493d75c2b831b7d5ce128a4019563030b0ed6370` |
| Duration | 22.933333 seconds |
| Frame size | 1920 x 1200 |
| Codec | H.264 |
| Approximate frame rate | 60 fps |
| Repository status | local-only reference; not copied or committed |

The recording was reviewed across representative frames and as a continuous
interaction. It establishes a quality bar, not a pixel specification.

### Observed choreography

- A dark, editorial, nearly full-screen canvas gives the graph visual priority.
- The global topology stays present while the selected neighborhood becomes
  brighter and unrelated material recedes.
- A persistent selected-concept panel and an ephemeral hover preview coexist.
  Hover does not destroy the user's current place.
- Selection, camera movement, zoom, and re-selection are smooth enough that the
  graph feels spatial rather than like a sequence of redraws.
- The detail panel answers a compact set of consequential questions and offers
  clear next traversals.
- A restrained legend and low-chrome controls preserve attention for the map.
- Color encodes a stable category system. It is not decorative noise.
- The graph remains dense, but labels and detail are disclosed progressively.

### What “the same quality bar” means for Lolla

It means:

- composed typography, spacing, color, depth, and motion;
- immediate pointer response and stable transitions;
- a graph state that is understandable before reading documentation;
- persistent orientation during exploration;
- useful model and relation information one interaction away;
- visual regression and human review gates, not “the library rendered” as the
  definition of done.

It does not require the same layout, 3D camera, colors, hierarchy, taxonomy, or
panel copy.

## What The Public Marble Repository Establishes

The [Marble Skill Taxonomy repository](https://github.com/withmarbleapp/os-taxonomy)
describes a versioned dataset of 1,590 micro-topics and 3,221 prerequisite
edges across eight subjects. Each edge is a directed prerequisite and the
result is a directed acyclic graph. Its public explorer uses age as height and
subject as color. The repository provides JSON Schemas, stable identifiers,
counts, and file checksums, and deliberately ships data rather than the visual
application runtime.

The public README and explorer support several transferable patterns:

- stable IDs and a hash-bearing data manifest;
- nodes with enough plain-language information to support a useful detail
  panel;
- relations with an explicit reason rather than unlabeled lines;
- one canonical data projection feeding both overview and detail;
- global context plus selective path illumination;
- graph navigation backed by pages and assessment prompts.

The public repository also makes licensing boundaries explicit: its database
is ODbL 1.0, Marble-authored text is CC BY-SA 4.0, and upstream standards keep
their own licenses. Lolla will not import Marble data or text. If any future
work does so, it would require a separate licensing and attribution decision.

Primary references:

- [Marble Skill Taxonomy](https://github.com/withmarbleapp/os-taxonomy)
- [Marble curriculum explorer](https://withmarble.com/curriculum/)
- [Marble taxonomy README](https://github.com/withmarbleapp/os-taxonomy/blob/main/README.md)
- [Marble taxonomy schemas](https://github.com/withmarbleapp/os-taxonomy/tree/main/schema)
- [Marble taxonomy manifest](https://github.com/withmarbleapp/os-taxonomy/blob/main/data/manifest.json)

## The Semantic Difference Lolla Must Preserve

Marble's graph is principally a prerequisite curriculum DAG. Lolla's current
product-safe candidate graph is a cyclic, multi-relational network:

| Dimension | Marble reference | Lolla canonical substrate |
|---|---|---|
| Primary node | teachable micro-topic | mental model |
| Main edge meaning | prerequisite | ally, antagonist, or tension |
| Default direction | dependency direction | source-authored relation direction; reciprocity is explicit |
| Organizing axis | subject and age | model families and curated relation semantics |
| Topology | directed acyclic graph | cyclic multi-relational graph |
| Primary action | trace prerequisites and unlocks | inspect a model, relation, neighborhood, or guided learning path |
| Truth boundary | curriculum alignment and evidence fields | source-backed teaching projection; relation is not proof |

Therefore Lolla must not copy these Marble semantics:

- no invented “learn this before that” relation across the whole corpus;
- no age or mastery axis;
- no transitive prerequisite highlighting for ally, antagonist, or tension
  edges;
- no claim that central, large, bright, or highly connected models are more
  important or more correct;
- no conversion of graph distance into semantic relevance;
- no use of embedding similarity as a visible validated relation.

Lolla may illuminate a selected model's direct neighborhood. Multi-hop paths
are allowed only when the interface names the path mode and every included edge
already exists in the product-safe projection.

## Renderer And Layout Current Practice

This PRD does not freeze a browser renderer. It freezes the behavior and
quality gates, then requires a short visual spike before selection.

Current official documentation suggests two credible baselines:

- [Sigma.js](https://www.sigmajs.org/docs/) is a WebGL renderer built on
  Graphology and intended for interactive browser graphs with thousands of
  nodes and edges. Its node and edge reducers can change visual state without
  mutating the underlying graph, which fits selection, dimming, and persistent
  context. Its custom render programs and layers support a higher-quality
  visual treatment than Lolla's current dependency-free SVG prototype.
- [Cytoscape.js](https://js.cytoscape.org/) provides mature semantic graph
  interaction and styling, but its own documentation warns that rich styles,
  edges, multigraphs, and high-density rendering increase cost. It remains a
  useful control in the spike, particularly for interaction semantics.

[Graphology ForceAtlas2](https://graphology.github.io/standard-library/layout-forceatlas2.html)
and [Noverlap](https://graphology.github.io/standard-library/layout-noverlap.html)
are plausible offline layout tools. The production browser must consume
versioned, precomputed coordinates so a user does not receive a different map
or a layout jump on each visit. Layout metrics can diagnose geometry, but they
must not be presented as product quality or semantic correctness.

The spike should compare:

1. Sigma.js with Graphology and custom visual layers;
2. Cytoscape.js as the semantic-interaction control;
3. a custom Three.js/WebGL treatment only if the first two cannot meet the
   founder's motion, depth, and composition bar without fighting their APIs.

The selection gate is a recorded side-by-side review on the same frozen Lolla
projection. Library popularity or synthetic benchmark numbers alone do not
select the renderer.

## Transferable Product Principles

### The graph is the invitation, not the explanation

The global graph should create curiosity and orientation. Full model pages and
relation pages carry the durable lesson.

### Selection must preserve place

Selecting a node changes emphasis rather than replacing the whole scene. The
selected node remains durable until explicit navigation, even while hover
previews other nodes.

### The edge is a first-class learning object

A line must resolve to a relation page or panel that explains direction,
relation type, why it matters, how it can be misread, provenance, confidence,
and missingness.

### Motion must carry meaning

Motion may reveal depth, guide the camera, or preserve continuity. It must not
continually rearrange model meaning. Ambient motion pauses on interaction and
is disabled by reduced-motion preference.

### Overview and detail share one source contract

The graph, library, model page, relation page, and Teacher journey must resolve
the same stable IDs and product-safe source manifest. A visually polished fork
of the data would recreate drift.

## Reference Non-Claims

- No Marble code, data, taxonomy, text, screenshots, or visual assets are
  incorporated by this note.
- The founder recording is design evidence, not a repository dependency.
- A WebGL graph is not automatically beautiful, useful, accessible, or true.
- The renderer decision remains prospective until the visual spike.
- This reference does not authorize implementation, public deployment,
  provider calls, runtime integration, or a change to the Stage 0 lifecycle
  register.

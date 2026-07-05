# Mental Model Teacher Current Substrate Inventory v0

Status: planning inventory

This inventory records the existing Lolla knowledge assets that the Mental Model
Teacher product surface should understand before building visual pages or graph
UI.

The product surface should reuse the substrate, not rebuild it. But reuse does
not mean exposing every internal artifact to users. The core product job is to
translate source-backed substrate into readable model pages, relation pages,
Teacher lessons, and focused graph neighborhoods.

## Product Exposure Policy

| Asset class | Current role | Product-surface role |
|---|---|---|
| Canonical Markdown | Source description of each model | Source of readable model-page doctrine |
| Activation curation | Routing and selection semantics | Power "use when" and "avoid when" sections |
| Intervention semantics | Failure modes, mitigations, heuristics, premortems | Power misuse, practice, and self-check sections |
| Relation semantics | Allies, antagonists, tensions | Power relation pages and graph edges |
| Compiled relationship graph | Runtime graph and neighborhood source | Power graph JSON after product filtering |
| Knowledge graph | Compiled substrate topology and tendency bindings | Context for library navigation, not direct user output |
| Embeddings DB | Semantic matching and activation tiebreaker support | Internal only in v0; may power future suggestions |
| V60 affordances | Reviewed transaction affordance layer | Source for advanced teaching affordances after review |
| Graph survival reports | Operator/eval observability | Internal context, not a product page |
| Treatment audits | Calibration and research evidence | Internal context, not a product page |
| Product Delta evals | Evidence discipline | Internal evidence, not Teacher product surface |

## Existing Data Files

### Canonical Source Corpus

- `data/model_sources/*.md`
- `data/model_sources/manifest.json`

The manifest records model IDs, filenames, hashes, byte counts, and the repo
source root. Historical notes may use an older corpus label, but the current
repo should be counted from the manifest and files, not from the label.

Product use:

- readable model pages;
- source refs and custody summaries;
- doctrine extraction checks.

Do not expose:

- local machine paths from historical copy metadata;
- raw canonical Markdown as the main product UI.

### Activation Curation

- `data/curation/*.json`

These files carry first-pass routing semantics:

- `select_when`;
- `avoid_when`;
- `input_type`;
- `output_type`;
- `reasoning_types`;
- provenance notes.

Product use:

- "when this model helps";
- "when this model misleads";
- library filters;
- model-family grouping.

### Intervention Semantics

- `data/curation/intervention_semantics/*.json`

These files carry:

- failure modes;
- mitigations;
- premortem questions;
- heuristics;
- curation notes;
- deferred richness notes.

Product use:

- "common misuse";
- "practice drill";
- "questions to ask";
- "do not overlearn this" boundary.

### Relation Semantics

- `data/curation/relation_semantics/*.json`

These files carry:

- allies;
- antagonists;
- structured tensions;
- target model IDs;
- rationale text;
- source quotes;
- extraction type;
- confidence;
- curation notes.

Product use:

- relation pages;
- graph edges;
- relation-type filters;
- Teacher clickthroughs.

Important rule:

```text
An edge is not the lesson.
The relation page is the lesson.
```

### Compiled Relationship Graph

- `data/relationship_graph.json`
- `engine/system_b/relation_graph.py`

The current compiled relationship graph supports runtime graph neighborhoods,
fan-corrected affinity, supporting/risk model ordering, and the activation-match
tiebreaker when a reasoning context and embeddings are available.

Product use:

- graph-neighborhood candidates;
- relation density checks;
- edge metadata source.

Do not expose:

- raw ranking internals as user-facing truth;
- fan-adjusted affinity as "importance" without explanation.

### Knowledge Graph

- `data/knowledge_graph.json`

This is the wider compiled substrate: model topology, cognitive tendencies,
antidote bindings, structural coverage routing, reframing patterns, and related
compiled material.

Product use:

- later library navigation;
- possible tendency-to-model paths;
- curated collection entry points.

Do not expose:

- the full topology as the first product graph;
- raw tendency bindings as advice.

### Embeddings And Activation Matching

- `data/embeddings.db`
- `engine/system_b/edge_activation_store.py`
- `engine/system_b/activation_matcher.py`
- `scripts/build_edge_activation_embeddings.py`

These assets support semantic matching and the narrow activation-match
tiebreaker. They are important to Lolla's current lanes, but they should not be
treated as product truth.

Product use in v0:

- inventory only;
- future semantic-neighbor suggestion plan.

Do not expose:

- embedding ranks as product explanation;
- semantic neighbors as validated relations.

### Curated Trusted-Surface Files

- `data/curated/subpattern_catalog.json`
- `data/curated/compiled_chunks.json`
- `data/curated/structural_signal_lexicon.json`
- `data/curated/reasoning_signals.json`

These support trusted surface selection and fallback reasoning signals.

Product use:

- future teaching fragments after source review;
- possible "why this pattern matters" support.

Do not expose:

- internal signal lexicon as UI copy;
- trusted-surface status as proof.

### Model Affordances And V60

- `data/model_affordances/*`
- `data/compiled/model_affordances/affordances_v60.json`
- `data/schemas/model_affordance.schema.json`
- `engine/system_b/model_affordance_validation.py`
- `scripts/compile_model_affordances.py`

V60 is the reviewed transaction layer over the canonical articles. It says what
a model can legitimately do in a reasoning transaction, what evidence is needed,
what treatment requirements apply, and what tempting interpretations are absent
or unsupported.

Product use:

- advanced Teacher pages can explain "what this model can do";
- absence records can become product-visible "do not claim this" warnings after
  translation;
- source-backed affordances can make practice reps more precise.

Do not expose:

- raw affordance JSON;
- absence records as user-facing scolding;
- V60 transaction status as product proof.

### Family Semantics

- `data/family_semantics/*.json`

These files describe clusters and family-level semantics.

Product use:

- library collections;
- model families;
- graph cluster labels;
- learning paths through related models.

### Evaluation And Treatment Audit Data

- `data/evaluations/gate4_edge_probes/summary.json`
- `data/treatment_audits/*`
- `engine/system_b/graph_survival_report.py`

These are calibration and operator/eval materials.

Product use:

- internal confidence about substrate behavior;
- future review packets.

Do not expose:

- evaluation data as product marketing;
- graph survival as proof that a model helped;
- treatment audits as user-facing lessons.

## Existing Code Lanes To Respect

### Runtime Graph Lane

Key files:

- `engine/system_b/relation_graph.py`
- `engine/system_b/activation_matcher.py`
- `engine/system_b/edge_activation_store.py`

Product stance:

- borrow graph data shapes;
- do not reuse runtime ranking language directly in user-facing pages.

### Model-Affordance Lane

Key files:

- `engine/system_b/model_affordance_validation.py`
- `scripts/compile_model_affordances.py`
- `data/compiled/model_affordances/affordances_v60.json`

Product stance:

- use as a later precision layer for model pages;
- keep absence and misuse guards visible but plain.

### Graph Survival And Eval Lane

Key files:

- `engine/system_b/graph_survival_report.py`
- `docs/evals/*`
- `data/treatment_audits/*`

Product stance:

- do not put eval internals into the Teacher product;
- use them to avoid naive claims about "good" or "helpful."

### Teacher Lane

Current external worktree package includes:

- Teacher card and note;
- OKF case bundle;
- model and relation deep dives;
- practice lab;
- grounding and sentinel audits;
- human gate.

Product stance:

- productize the useful teaching pieces;
- do not ship raw review packets as the user experience;
- keep `pending_human_review`, `human_validated: false`, and
  `product_proof: false` until the real gate changes.

## Immediate Design Implication

The next implementation PR should not jump straight to graph UI.

It should first define a substrate inventory and exposure contract:

```text
existing internal asset
  -> product-safe field
  -> source/custody rule
  -> user-facing language rule
  -> forbidden exposure rule
```

Only after that should we build model pages, relation pages, Teacher lessons, and
visual graphs.

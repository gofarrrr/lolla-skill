# Graph Selection Improvement Audit

Research date: 2026-04-14

## Executive Summary

Lolla has a curated knowledge graph of 222 mental models with 1,358 typed edges and 2,496 embedded knowledge chunks. The graph data is rich — typed edges (ally, antagonist, tension, compound), composition affinities, quality flags, confidence levels, activation contexts, subpatterns. But the selection mechanics are flat: single-hop neighbor lookup, positional ranking, string-prefix matching. The system has depth it doesn't use.

This document maps every decision boundary in the current system, identifies what information is available but ignored, and catalogs concrete techniques from knowledge graph research and cognitive science that could improve selection quality without bloating the system.

**No code changes are proposed.** This is an audit.

---

## Part 1: Current Decision Chain (End-to-End)

### The Full Path: Conversation → DeltaCard

```
Conversation text
  → Pass 1: LLM triage (scores each of 25 tendencies 0-10)
  → Trigger gate: score >= 4 (triage) OR cosine >= 0.30 (embedding) OR always_include
  → Pass 2: Deep checks (LLM confirms/rejects each triggered tendency, extracts sub_pattern)
  → Routing: tendency_id + sub_pattern → primary antidote model
  → Neighborhood: primary model → 1-hop graph lookup → 2 supporting + 1 risk
  → Pressure bundle: select chunks from compiled substrate by model priority position
  → DeltaCard assembly: order findings by specificity + severity, split into tiers
```

### Decision Boundary Inventory

| Stage | Mechanism | Parameters | What Decides |
|-------|-----------|------------|-------------|
| Trigger gate | Score threshold | `triage_threshold=4`, embedding `>= 0.30` | Which tendencies get deep-checked |
| Primary binding | String prefix match on sub_pattern vs model_id, fallback to `bindings[0]` | None tunable | Which antidote model leads the intervention |
| Graph neighborhood | 1-hop, binary edge-type bucketing, sort by composition_affinity | `max_supporting=2`, `max_risk=1`, `min_affinity=0.6` | Which models support/challenge |
| Pressure chunks | Positional rank: model_priority_index, then chunk_type_index | Type priority tuple order | Which curated text appears in the output |
| Finding order | `(specificity_rank, severity_rank, insertion_order)` | specificity: trusted + non-general = 0, else 1 | What the user sees first |
| Companion chunks | Type priority → confidence → extraction → text prefix; optional embedding rerank blended at 60/40 | `budget=20`, `per_model=5`, `per_type=5`, `relevance_floor=0.25` | What companion material accompanies |

### What is Loaded But Never Used in Selection

These fields exist on data structures, are populated during loading, but no selection or ranking logic reads them:

| Field | Lives On | What It Knows | Why It Matters |
|-------|----------|---------------|----------------|
| `blocking_quality_flags` | `ModelBinding`, `SelectedChunkRecord` | Curated flags marking low-quality activation contexts | Could gate out bindings with known issues |
| `advisory_quality_flags` | `ModelBinding`, `SelectedChunkRecord` | Curated flags suggesting caution | Could penalize without blocking |
| `guardrail_tags` | `CompiledChunk`, `SelectedChunkRecord` | Tags like "speculative", "requires_context" | Could filter chunks that need more context |
| `confidence` | `SourceRef`, `ChunkProvenance` | high/medium/low on curated extractions | Could weight chunk selection |
| `detectability` | `SubpatternRef` | How reliably detectable each subpattern is | Could adjust trigger sensitivity |
| `signal_tags` | `SubpatternRef` | Semantic tags for matching | Could improve sub_pattern → binding matching |
| `source_description` | `RelationNeighbor` | Why the edge exists | Could explain routing decisions |

---

## Part 2: Specific Bottlenecks

### Bottleneck 1: Single-Hop Graph Traversal

**Current:** `RelationGraph.neighborhood()` iterates `self._graph.get(seed_model_id, ())` — the direct neighbors of the seed model only.

**What this misses:** With 222 nodes and 1,358 edges, average degree is ~6. A single hop sees 6 neighbors. Two hops could see ~36. Three hops could reach most of the graph. The graph encodes multi-hop relationships (A allies with B, B allies with C, so C is structurally relevant to A) but we never traverse them.

**Concrete example:** If "Pre-Mortem Analysis" is the primary antidote and it has an ally "Inversion" which has an ally "Second-Order Thinking", the current system never considers "Second-Order Thinking" even though the graph says it's reachable through a strong ally chain. It might be the most structurally relevant model for the specific failure pattern but it's invisible.

**Impact:** The system picks the 2 nearest supporting models by affinity. These are often the most generic allies — the models directly connected to many popular models. The most specific, interesting, and valuable supporting model may be 2 hops away.

### Bottleneck 2: Edge Types Flattened to Binary

**Current:** Edges are bucketed into exactly two categories:
```python
if neighbor.edge_type in {"ally", "compound"}:  # → supporting
elif neighbor.edge_type in {"antagonist", "tension"}:  # → risk
```

Then ranked purely by `composition_affinity`.

**What this loses:**
- An `ally` at 0.7 affinity beats a `compound` at 0.65, but "compound" means "these models multiply each other's effect" — semantically stronger than generic alliance
- `antagonist` and `tension` are lumped together, but an antagonist is "this model directly opposes yours" while a tension is "these models create productive friction" — different roles
- No edge type gets a weight multiplier. The type information is used only for bin assignment, then discarded

### Bottleneck 3: Positional Ranking in Chunk Selection

**Current:** `PressureBundleSelector._filter_chunk_candidates()` sorts by:
```python
key = (model_rank_position, type_rank_position, chunk_id)
```

Where `model_rank_position` is literally "what index is this model in the priority list."

**What this means:** If the primary model (rank 0) has a mediocre diagnosis chunk and the first supporting model (rank 1) has an excellent one with `confidence=high` and `extraction_type=explicit`, the mediocre chunk always wins. Confidence, extraction quality, and guardrail tags exist on every chunk but are never consulted.

### Bottleneck 4: No Cross-Finding Awareness

**Current:** Each finding in the DeltaCard is assembled independently. Route 1 picks its supporting models, Route 2 picks its supporting models. They might pick the same model for different reasons, or complementary models, or contradictory models — the system doesn't know.

**What this means:** When two tendencies are detected simultaneously (e.g., Doubt Avoidance + Authority Misinfluence), their routes are computed in isolation. But the compound effect — which is what "Lollapalooza" is about — lives in the interaction between routes, not in each route independently. The `compound_catalog.py` exists and has compound relationships, but it's used for annotation, not for routing.

### Bottleneck 5: Primary Binding Selection is String Matching

**Current:** `_match_primary_binding()` normalizes the sub_pattern and tries to prefix-match it against model_ids in the binding list. If no prefix matches, it returns `bindings[0]`.

**What this means:** The sub_pattern "premature-convergence" will match a model_id starting with "premature-convergence" but not "convergence-bias" even if the latter's activation_context is a better semantic fit. The match is lexical, not semantic. And the fallback is always the first binding — list order is destiny.

### Bottleneck 6: Relevance Scores Are Additive, Not Structural

**Current:** When embedding-based relevance scores exist, `_bounded_unique_model_ids()` sorts by `(-relevance_score, -affinity, model_id)`. The relevance score is a cosine similarity between the query embedding and each model's signal embeddings.

**What this means:** A model can score high on relevance (it's about the right topic) but be structurally disconnected from the seed model in the graph. Relevance and graph proximity are combined by simple sort priority, not by a unified scoring function that considers both.

---

## Part 3: Techniques from Knowledge Graph Research

### 3.1 Personalized PageRank (PPR)

**What it is:** A random walker starts at seed node(s) and at each step either follows an edge (probability alpha) or teleports back to the seed (probability 1-alpha). The stationary distribution gives every node a proximity score relative to the seed.

**Computational cost for our graph:** Trivial. Power iteration on 222 nodes, 1,358 edges converges in microseconds. Even Python's `numpy` handles it without optimization. NetworkX `pagerank()` works directly.

**What it adds:**
- Multi-hop influence: a model 2-3 hops away through strong ally chains gets a high score
- Path diversity: a model reachable through multiple paths scores higher than one reachable through a single strong edge
- Natural decay: influence drops with distance without needing an explicit hop count

**Damping factor implications:**
- `alpha=0.85` (classic): Influence spreads wide, 4-5 hops
- `alpha=0.5-0.7`: More local, 2-3 hops (better for our dense graph)
- `alpha=0.2`: Almost single-hop (similar to current behavior)
- GoS repo uses `damping=0.2` (high teleport back to seeds)

**Determinism:** Fully deterministic. Power iteration is a fixed-point computation.

**Fit for Lolla:** HIGH. Directly replaces `neighborhood()` for supporting model selection. Seed the personalization vector at the primary antidote model(s), run PPR on the ally/compound subgraph, take top-k by score. The existing `RouteNeighborhood` interface stays the same — only the internals change.

**Reference implementation:** GoS repo (`retrieval.py`) has a clean 30-line PPR implementation with transition matrix construction.

### 3.2 Signed Random Walk with Restart (SRWR)

**What it is:** Extension of PPR for graphs with positive and negative edges. Maintains separate positive score (rp) and negative score (rn) vectors. Positive edges propagate positive activation; negative edges propagate negative activation. Net score: rd = rp - rn.

**What it adds:** Handles ally (positive) and antagonist (negative) edges in a single computation. A model that's an ally of your ally scores positive. A model that's an antagonist of your ally scores negative. This captures "the enemy of my friend is my enemy" automatically through graph structure.

**Fit for Lolla:** HIGH. Directly solves Bottleneck 2. Instead of bucketing edges into binary supporting/risk, SRWR produces a continuous score per model that already encodes the signed relationship structure. Positive rd = supporting; negative rd = risk. The sign and magnitude come from the full graph topology, not just direct neighbors.

**Reference:** `jinhongjung/srwr` on GitHub. Parameters: restart probability c=0.15, balance factors beta=0.5, gamma=0.5.

### 3.3 Multi-View Edge-Type Scoring

**What it is:** Run separate PPR computations on subgraphs filtered by edge type. Combine the resulting score vectors:
```
final_score[v] = w_ally * ppr_ally[v] + w_compound * ppr_compound[v] 
                 - w_antagonist * ppr_antagonist[v] + w_tension * ppr_tension[v]
```

**What it adds:** Preserves edge-type semantics through multi-hop traversal. You get four interpretable sub-scores per model, not just a single number. A model might score high on the ally dimension but also high on tension — that's valuable information for presentation.

**Fit for Lolla:** MEDIUM-HIGH. More transparent than SRWR but requires 4 PPR runs instead of 1 (still sub-millisecond on 222 nodes). The sub-scores could feed into chunk selection: pick diagnosis chunks from ally-high models, pick tension chunks from tension-high models.

### 3.4 Spreading Activation (Collins & Loftus, 1975)

**What it is:** A cognitive science model of semantic memory. When a concept is activated, activation spreads to associated nodes. Stronger associations transmit more activation. Activation decays with distance. A threshold prevents indefinite spreading.

**Core algorithm:**
1. Set seed node(s) to activation 1.0
2. For each node exceeding firing threshold F: spread `A[j] += A[i] * W[i,j] * D` where D is decay
3. Cap at [0.0, 1.0]
4. Repeat until convergence or max iterations

**What it adds over PPR:** Conceptually the closest model to what Lolla is doing. PPR is a mathematical abstraction; spreading activation is a model of how human minds navigate associative networks. The decay parameter directly controls "how far from the seed do we look?" The threshold prevents noisy, weakly-connected models from activating.

**Key insight — Fan Effect (ACT-R):**
```
Association_strength = S - ln(fan)
```
Where `fan` is the number of connections a node has. A model connected to 20 others spreads less activation per edge than a model connected to 3. This naturally penalizes highly-connected "generic" models and favors specific, targeted ones.

**Our current system has no fan correction.** A model with 20 ally connections at 0.65 affinity each will frequently appear in neighborhoods — it's the "default answer" for many seeds. The fan effect would dampen it proportional to its connection count, allowing more specific models through.

**Fit for Lolla:** HIGH. ~30 lines of Python, no dependencies. The fan effect is the specific insight that's most valuable — it addresses the "generic model always wins" problem directly. Can be combined with PPR (use fan-adjusted edge weights in the transition matrix).

### 3.5 Topic-Sensitive PageRank (Pre-computed)

**What it is:** Pre-compute PPR vectors for each of the 25 tendency categories, seeded at each tendency's antidote models. At runtime, the detected tendency selects the pre-computed vector. Zero graph computation at query time.

**Storage:** 25 vectors of 222 floats = 22KB. Trivial.

**Pre-computation:** 25 PPR runs on 222 nodes = milliseconds total.

**Fit for Lolla:** MEDIUM. A nice optimization if PPR is adopted. The pre-computed vectors can be cached in the compiled substrate alongside the existing chunks. Runtime becomes a dictionary lookup instead of a matrix computation — though the computation is already negligible.

### 3.6 HippoRAG Pattern (NeurIPS 2024)

**What it is:** A retrieval system inspired by hippocampal memory. Uses PPR on a knowledge graph to find relevant nodes, where the personalization vector is set from the query's key concepts. The graph acts as a "semantic index" that bridges the vocabulary gap between query and stored knowledge.

**Key architectural insight:** The graph is not just a structure — it's a retrieval index. Instead of embedding the query and finding similar chunks, you identify graph nodes mentioned in the query, then PPR from those nodes to find structurally related knowledge that the query didn't explicitly mention.

**Fit for Lolla:** MEDIUM. Our embedding retriever already handles the vocabulary gap via query expansion + RRF fusion. But HippoRAG's insight about using graph structure as a retrieval index (not just a post-retrieval enrichment step) is worth noting. Currently, our graph is consulted *after* tendency detection and routing. It could also be consulted *during* detection — using graph structure to identify related tendencies that the triage prompt missed.

### 3.7 Structural Balance Validation

**What it is:** In signed graphs, balance theory states that cycles should have an even number of negative edges. "The friend of my enemy is my enemy" (balanced). "The friend of my enemy is my friend" (unbalanced — indicates a curation inconsistency or an interesting dialectical relationship).

**Fit for Lolla:** LOW-MEDIUM as a runtime technique but HIGH as a one-time curation audit. Running structural balance analysis on the 1,358 edges would surface:
- Curation errors: A → ally → B, B → ally → C, but A → antagonist → C (why?)
- Interesting dialectics: legitimate cases where a model's ally's ally is actually in tension with the original model — worth flagging as curated tension

### 3.8 Confidence-Weighted Path Scoring

**What it is:** Instead of scoring nodes, score paths. Each path from seed to target gets:
```
path_score = product(edge_weight[e] for e in path) * decay^len(path)
```
Target's score = max(path_scores) or sum(path_scores).

**What it adds:** Explains *why* a model was selected. "Model X scores 0.72 because: ally path through Y (0.85 * 0.85 * 0.95 = 0.69) and compound path through Z (0.78 * 0.92 * 0.95 = 0.68)." This is valuable for auditability — Lolla's core value is traceability.

**Fit for Lolla:** MEDIUM. More expensive than PPR (requires enumerating paths, not just computing stationary distribution). But for 222 nodes, all simple paths of length ≤ 3 are enumerable in milliseconds. Could be used as a post-hoc explanation layer: after PPR selects the top models, trace back *why* they scored high.

---

## Part 4: Technique-to-Bottleneck Mapping

| Bottleneck | Technique | How It Helps |
|-----------|-----------|--------------|
| 1. Single-hop traversal | PPR / Spreading Activation | Multi-hop with natural decay |
| 2. Binary edge bucketing | SRWR / Multi-view scoring | Continuous signed scores preserving edge semantics |
| 3. Positional chunk ranking | Use `confidence`, `extraction_type`, quality flags in sort key | Curated metadata actually influences selection |
| 4. No cross-finding awareness | Compound-aware PPR seeding | Seed PPR from *all* detected tendency antidotes simultaneously |
| 5. String-prefix binding match | Semantic matching on activation_context vs sub_pattern | Use embeddings or token overlap instead of prefix match |
| 6. Additive relevance + structure | Unified scoring: `alpha * graph_score + beta * relevance_score` | Single formula that weights both dimensions |

---

## Part 5: What We Could Add Without Bloating

### Layer 1: Fan-Adjusted Affinity (Smallest Change, Biggest Gain)

Modify `composition_affinity` at load time:
```
adjusted_affinity = composition_affinity * (1.0 / (1.0 + log(fan_count)))
```
Where `fan_count` = number of edges from the neighbor node. No new data structures, no new algorithms. Just dampen the affinity of highly-connected models proportional to their connection count.

**Effect:** Specific, targeted models rise; generic "connected to everything" models drop. The curated affinity scores already capture relationship strength — this adds a structural correction for graph density.

### Layer 2: Quality-Weighted Chunk Selection

Add `confidence` and `extraction_type` to the chunk sort key:
```python
key = (
    model_rank,
    type_rank,
    confidence_rank,    # high=0, medium=1, low=2
    extraction_rank,    # explicit=0, other=1
    chunk_id,
)
```

**Effect:** Among chunks at the same model and type priority, explicitly extracted high-confidence chunks win. No new data — just using what's already loaded.

### Layer 3: PPR Neighborhood (Replaces Single-Hop)

Replace `neighborhood()` with PPR seeded at seed model(s), computed over the ally/compound subgraph for supporting models and the antagonist/tension subgraph for risk models.

**Effect:** Supporting and risk models are now selected based on multi-hop graph structure, not just direct neighbors. ~30 lines of new code, numpy dependency (already present in the ecosystem).

### Layer 4: Compound-Aware Seeding

When multiple tendencies are detected, seed the PPR vector from *all* their antidote models simultaneously (weighted by detection confidence/score). This lets the graph find models that are structurally central to the specific *combination* of detected tendencies.

**Effect:** Cross-finding awareness without changing the DeltaCard structure. The models selected will naturally be relevant to the full pattern, not just individual tendencies.

### Layer 5: Blocking Quality Flags Actually Block

If `blocking_quality_flags` is non-empty on a binding or chunk, skip it in selection. If `advisory_quality_flags` is non-empty, penalize its rank.

**Effect:** Curated quality metadata — which someone already spent time creating — actually influences the output.

---

## Part 6: Key GitHub Repos for Reference

| Repo | Stars | Key Technique | Our Applicable Insight |
|------|-------|---------------|----------------------|
| [HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) | 3.4k | PPR on KG for retrieval | Graph as retrieval index, not just post-hoc enrichment |
| [GoS (graph-of-skills)](https://github.com/davidliuk/graph-of-skills) | — | PPR + hybrid seed + typed edges | Clean PPR implementation, multi-view scoring |
| [Microsoft GraphRAG](https://github.com/microsoft/graphrag) | Very high | Community detection, hierarchical summarization | Leiden clustering could identify model families automatically |
| [SRWR](https://github.com/jinhongjung/srwr) | — | Signed RWR for positive/negative edges | Direct implementation for ally/antagonist handling |
| [PyRWR](https://github.com/jinhongjung/pyrwr) | — | Clean RWR library | Reference implementation for standard RWR |
| [fast-pagerank](https://github.com/asajadi/fast-pagerank) | — | Sparse PPR | Faster than NetworkX for repeated queries |
| [LightRAG](https://github.com/HKUDS/LightRAG) | High | Dual-level retrieval (local + global) | Entity-level + theme-level parallels our tendency + model selection |
| [scikit-network](https://github.com/sknetwork-team/scikit-network) | — | PageRank, HITS, graph algorithms | Clean Python graph algorithm library |
| [KAG (OpenSPG)](https://github.com/OpenSPG/KAG) | High | Logical form-guided reasoning | Deterministic reasoning paths through KG |

---

## Part 7: Priority Matrix

Ordered by (impact / complexity):

| # | Change | Impact | Complexity | What It Fixes |
|---|--------|--------|------------|---------------|
| 1 | Fan-adjusted affinity | High | Trivial (~5 lines) | Generic models dominating neighborhoods |
| 2 | Quality flags in chunk selection | Medium | Trivial (~3 lines in sort key) | Ignoring curated quality metadata |
| 3 | Blocking quality flags gate | Medium | Trivial (1 conditional) | Curated quality never enforced |
| 4 | PPR neighborhood | High | Low (~30 lines + numpy) | Single-hop limitation |
| 5 | Edge-type weights in scoring | Medium | Low (~10 lines) | ally/compound/antagonist/tension flattened |
| 6 | Compound-aware PPR seeding | High | Low (change seed vector) | No cross-tendency awareness |
| 7 | Confidence-weighted paths (explainability) | Medium | Medium | Can't explain why a model was chosen |
| 8 | SRWR for signed traversal | High | Medium (~50 lines) | Positive/negative edges in unified computation |
| 9 | Structural balance audit (one-time) | Medium | Low (script) | Unchecked curation inconsistencies |
| 10 | Spreading activation with fan effect | High | Medium (~40 lines) | No cognitive-model-aligned traversal |

---

## Part 8: What NOT to Do

- **Don't add GNN/deep learning.** 222 nodes is not enough data. The graph is curated, not learned. Adding neural scoring on top of curated data would be fitting noise.
- **Don't add hypergraphs.** Our edges are binary. Hyperedges would require new curation work for limited gain.
- **Don't add knowledge graph embeddings (TransE, DistMult, etc.).** These learn latent representations from graph structure. Our graph is small enough that exact computation is faster and more interpretable than learned approximations.
- **Don't add stochastic/probabilistic scoring.** Determinism is a core value. Every technique in this audit is fully deterministic.
- **Don't replace the compiled substrate with a database.** The current flat-file approach is fast, simple, and auditable. A database adds complexity without proportional gain at this scale.

---

## Appendix: Technique Glossary

**PPR (Personalized PageRank):** Random walk with teleport. Scores every node by proximity to seed(s). `x(t+1) = alpha * A * x(t) + (1-alpha) * seed`. Converges in ~20 iterations for 222 nodes.

**SRWR (Signed RWR):** PPR for signed graphs. Maintains separate positive/negative score vectors. Net score = positive - negative.

**Spreading Activation:** Cognitive model. Activation flows from seed through weighted edges with decay. Threshold prevents weak propagation.

**Fan Effect (ACT-R):** Association strength = S - ln(fan). High-fan nodes have weaker per-edge associations. Prevents generic hubs from dominating.

**RRF (Reciprocal Rank Fusion):** Combines multiple rankings: score(x) = sum(1/(k + rank_i(x))). k=60 is standard. Higher is more smoothing.

**Structural Balance:** In signed graphs, stable triads have 0 or 2 negative edges. Odd-negative triads indicate inconsistency.

**Multi-view scoring:** Run the same algorithm on different edge-type subgraphs, combine score vectors with typed weights.

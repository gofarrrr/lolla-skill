# Knowledge Substrate

Detailed reference for the curated model corpus, graph, embeddings, V60 artifact, and bundled data files.

## Contents

- Model corpus and curation waves
- Source corpus and curation method
- Graph ranking and activation-match tiebreaker
- Measurement and calibration
- Bundled data dependencies

## The Knowledge Substrate

222 mental models curated from Charlie Munger's latticework of mental models, the Farnam Street Knowledge Project, and primary academic sources. This is not LLM-generated content — it is reviewed, curated, structured knowledge with explicit provenance.

Academic validation: USTC's MeMo paper (Feb 2024) proved Munger's latticework concept works as a prompting strategy, achieving near-SOTA performance across logical reasoning, STEM, and commonsense tasks in zero-shot settings. Lolla goes further: deterministic routing, auditability, curated relationships, and external application — not probabilistic in-context selection.

**Five waves of curation:**
- **Wave 1 — Activation semantics:** When to select each model, when to avoid it, input/output types. 222 models fully curated.
- **Wave 2 — Intervention semantics:** Failure modes with mitigations, heuristics, premortem questions. 222 models, each with curated failure modes and specific mitigations.
- **Wave 3 — Relation semantics:** Allies, antagonists, structured tensions between models. 1,358 curated edges describing how models support, oppose, and create productive tension with each other. The 867 ally + antagonist edges carry differentiated affinity (four-tier rubric 0.70/0.80/0.90/0.95), a per-edge `affinity_rationale`, and an `activation_condition` — the reasoning shape that should trigger each model. See *How the Graph Earns Its Picks* below.
- **Wave 5 — Reframing semantics:** Frame pattern → model mappings for 50 models. Lane 3 substrate — connects embedded assumptions in questions to specific mental models that challenge those assumptions.
- **Latticework layers — Discovery infrastructure:** Prerequisite orderings (A→B learning sequences), family semantics (dense ally clusters with named theses), polarity semantics (failure cascade ↔ correction stack pairs). Graph projection over Wave 3 topology proposes candidates, LLM validates against source articles, curated JSON enters the compilation path.

**25 cognitive tendencies** — adapted from Munger's Psychology of Human Misjudgment for LLM-generated strategic advice. Each tendency has corrective models mapped to it with activation contexts describing the specific failure pattern that should trigger each route. 241 antidote bindings, all with curated activation contexts.

**Pre-computed embeddings:** 2,496 knowledge chunks embedded with OpenAI text-embedding-3-large (3072d). Enables semantic matching — the query is expanded into domain-vocabulary variants via gpt-4o-mini (vocabulary-seeded with all 222 model names), each variant is embedded, and results are fused via Reciprocal Rank Fusion (RRF) to find the most relevant corrective knowledge. This bridges the vocabulary gap between user language ("sign the deal") and curated domain language ("escalation of commitment"). Requires `OPENAI_API_KEY`. Without it, deterministic routing still works.

**V60 affordance substrate:** `data/compiled/model_affordances/affordances_v60.json` is the current reviewed transaction layer over the canonical articles. It carries 222 model records, 306 source-backed affordances, and 697 absence records. The affordances say what a model can legitimately do in a reasoning transaction: activation shape, evidence needed, treatment requirements, diagnostic questions, misuse guards, confidence, and source evidence. The absence records are equally important: they say what the source did *not* support, where a tempting interpretation should be blocked, and where the model belongs to a different owner record. Runtime never discovers this by globbing for "latest"; V60 is loaded from an explicit configured path, and can be disabled per run with `LOLLA_V60_ENRICHMENT=off` or `--v60-enrichment off`.

### The Source Corpus

The 222 canonical articles were not LLM-generated. They were extracted from a corpus of ~200 books spanning cognitive science, decision theory, behavioral economics, systems thinking, strategy, evolutionary psychology, legal reasoning, and creativity.

The extraction used RAG: each book was embedded, and for every mental model in the taxonomy, the corpus was queried with five structured questions designed to extract the kind of knowledge that improves reasoning audits:

1. **Core Principles** — fundamental essence, non-obvious analogies
2. **Playbook in Action** — heuristics, actionable frameworks, concrete examples
3. **Strengths and Weaknesses** — where the model is most powerful, where misapplication is dangerous
4. **Latticework Interactions** — synergistic allies and conflicting antagonists
5. **Risks and Mitigations** — failure modes, blind spots, and pre-mortem questions

The answers were synthesized into canonical Markdown articles, then reviewed against source material for accuracy. This process is why the substrate contains knowledge the LLM doesn't have natively — the specific failure mode of Circle of Competence when applied to adjacent domains, the exact tension between Margin of Safety and Calculated Risk Taking, the premortem questions that Inversion would ask before a build-vs-buy decision. These come from books, not from training data.

The corpus includes foundational texts (Kahneman's *Thinking, Fast and Slow*, Munger's *Poor Charlie's Almanack*, Meadows' *Thinking in Systems*) alongside less obvious but high-signal sources: Henrich's *The WEIRDest People in the World* on cultural cognition defaults, Cukier et al.'s *Framers* on how framing constrains solution spaces, Simler & Hanson's *The Elephant in the Brain* on hidden motives in reasoning, and Griffiths' *The Laws of Thought* on Bayesian cognitive models. Mental models that only draw from one domain produce one-dimensional corrections — the breadth of the corpus is intentional.

### How Curation Works

Each wave of curation follows the same principle: an LLM reads the full canonical article for a mental model and makes holistic semantic judgments about it. This is not mechanical parsing, brittle lexical matching, or structured field extraction. The LLM reads the article the way a thoughtful person would — understanding the model's core logic, its failure modes, where it creates productive tension with other models, and what reasoning patterns it addresses.

Wave 1 asks: "When should this model be selected? When is it dangerous to apply?" Wave 2 asks: "How does this model fail? What premortem questions does it raise?" Wave 3 asks: "Which other models does this one support, oppose, or create structured tension with?" Each answer is validated against the source article — not against what the LLM "thinks" the model means from training data.

This methodology is critical because mechanical approaches fail on mental models. You cannot extract "failure modes of Circle of Competence" by parsing headings or matching keywords. You need to read the full article, understand that the model's deepest failure is boundary blur in adjacent domains, and write an activation context that describes that specific pattern. The LLM does the reading; the human reviews the judgment; the result enters the curated layer.

The result is a knowledge substrate that contains insights the LLM doesn't have natively — not because the information is secret, but because it was synthesized from specific source material (200+ books across disciplines) and structured for a purpose (reasoning audit) that no training corpus optimizes for.

### How the Graph Earns Its Picks

A curated graph with edges isn't yet a ranker. Three enrichments turn the Wave 3 topology into a signal the deterministic router can actually use.

**1. Differentiated affinity (four-tier rubric).** Before enrichment, 98.7% of ally edges compiled to a flat `composition_affinity = 0.90`, which meant the graph was effectively sorting models alphabetically by target id. The legacy compiler derived affinities from `confidence` alone (`high → 0.90`, `medium → 0.75`, `weak → 0.65`), collapsing rich canonical-article distinctions into three buckets most of whose edges landed at `0.90`. Layer 1 re-read every ally edge in the canonical articles and assigned one of four differentiated affinities based on the author's own language strength:

| Tier | Affinity | Rubric language (from canonical articles) | Share of 523 ally edges |
|------|----------|-------------------------------------------|--------------------------|
| CRITICAL | 0.95 | "the most powerful tool", "cannot function without", "indispensable" | 7.3% |
| STRONG | 0.90 | "directly strengthens", "the primary mechanism", "the key discipline" | 54.1% |
| MODERATE | 0.80 | "strengthens", "helps", "supports" | 36.9% |
| SUPPORTIVE | 0.70 | "can help", "is related to", "additional perspective" | 1.7% |

The same rubric was applied to the 344 curated antagonist edges. At runtime, antagonist affinities map through `_affinity_strength_to_risk()` (0.95→0.30, 0.90→0.25, 0.80→0.22, 0.70→0.20) to produce risk-weighted ordering for the *risk_model_ids* surfaced in the DeltaCard. Every enriched ally and antagonist also carries an `affinity_rationale` (why this relationship holds — e.g. "premortem surfaces failure modes that second-order-thinking then sequences") and an `activation_condition` (the reasoning shape that should trigger the edge — e.g. "when a plan is being evaluated before commitment"). Both were authored from the canonical articles; both reach the runtime via the compiled `relationship_graph.json`.

Same model, different strengths as ally of different models. `second-order-thinking` is a 0.95 ally of `premortem` (indispensable — premortem's entire value is surfacing second-order consequences) and a 0.80 ally of `inversion` (useful, but not structurally required). Pre-enrichment the router couldn't tell these apart.

**2. Fan correction (query-time dampening).** Hub models sit on many edges. Without correction they dominate every neighborhood the router touches — not because they're the right pick, but because they're adjacent to everything. `RelationGraph._fan_adjusted_affinity()` dampens hub affinity at query time:

```
fan-adjusted affinity = raw_affinity / (1 + ln(degree))
```

Applied only at ranking, never at the `min_supporting_affinity = 0.6` threshold check — so CRITICAL-tier edges (0.95) on moderately-fanned hubs still clear the threshold even when their adjusted value sits well below 0.6. This matters: a 50-edge hub with raw affinity 0.90 ranks at adjusted ~0.22, but a 10-edge focused model with raw 0.80 ranks at adjusted ~0.57. Focused models surface; hubs earn their spot only when their raw affinity was strong enough to survive dampening.

**3. Near-tie activation-match tiebreaker.** Fan correction and differentiated affinity fix most of the flatness. But top-1 vs top-2 still sometimes land within 0.01 of each other after dampening — 18% of qualifying seeds on the current graph. In that narrow window, affinity is provably uninformative and the router needs a second signal. Phase 3 Commit B added one, gated to fire *only* in the near-tie region:

- **Compile-time:** every ally and antagonist's `activation_condition` string is embedded (OpenAI `text-embedding-3-large`, 3072d) and stored in `data/embeddings.db::edge_activation_conditions`. 867 vectors, ~$2 per rebuild. Idempotent.
- **Query-time:** `RelationGraph.neighborhood()` accepts a typed `reasoning_context` (one of `TendencyRef`, `TriggeredTendency`, `FingerprintPayload`, `FrameRoute`, `DimensionRoute`). When top-1/top-2 fan-adjusted delta `δ < ε = 0.01` AND `max(top1_sim, top2_sim) ≥ noise_floor = 0.45`, the gate swaps the top-2 based on cosine similarity. Outside that window, or below the noise floor, the deterministic default order stands — byte-identical to the pre-tiebreaker path.
- **Facts/reasoning break.** The matcher's five typed adapters strip any factual content (`evidence_quotes`, `coverage_evidence`, quoted passages, numeric facts) before embedding the probe. Raw `str`, `vanilla_answer`, query text — none of these can reach it. By construction, the matcher only ever sees reasoning-shape prose on both sides: curator-authored activation_conditions vs. engine-produced reasoning-shape classifications.

**Calibration (2026-04-21):** `ε = 0.01` was pinned to a measured distribution (n=204 qualifying seeds; 18% near-ties, 1% exact ties, median δ=0.038). `noise_floor = 0.45` was pinned to a cosine-gap audit (6 probes × 523 ally edges: on-target reasoning prose lands at 0.73–0.79, off-topic prose lands at 0.19; 0.45 sits in the protective gap).

**4. Per-route observability trace.** Every tiebreaker invocation emits a `TiebreakerTrace` — a 14-field dataclass recording whether the gate attempted, fired, or aborted, and if aborted, which of seven clauses stopped it (`fewer_than_2_candidates`, `fewer_than_2_after_dedup`, `outside_epsilon_window`, `matcher_exception`, `matcher_empty_result`, `below_noise_floor`, `no_improvement`). Traces carry top-1/top-2 model ids, fan-adjusted affinities, delta, cosines against the reasoning context, and the calibration constants in effect. Each trace is serialized into `audit_summary.routing_decisions[].tiebreaker_supporting` / `.tiebreaker_risk`, so any run answers "did the tiebreaker fire, and if not why" from the result JSON alone — no pipeline re-run required.

The design principle underneath all four: the probabilistic signal (embedding cosine) can only enter the deterministic middle inside a gate where the deterministic signal (fan-adjusted affinity) is provably uninformative. The gate is narrow, its calibration is measured, and its decisions are traced. This is how the engine imports "being less wrong" capability without surrendering reproducibility — the default path is always recoverable by flipping the kill switch (`LOLLA_ACTIVATION_TIEBREAKER=off`) or omitting the `reasoning_context`.

### Measurement and Calibration

The system has been tested and calibrated across hundreds of evaluation runs against professional-grade strategic cases. Three layers of measurement guide ongoing development:

- **Process quality** — Is the machine working correctly? Detection rates, routing coverage, boundary health, cache efficiency, timing — across all four lanes. If a code change degrades tendency detection or companion verification, the metrics show it.
- **Novelty and specificity** — Is the system saying something the vanilla answer didn't already contain? A delta card that restates what the LLM already said adds no value. Measurement tracks whether findings surface genuinely new structural pressure — challenges, tensions, and failure modes absent from the original reasoning.
- **Downstream influence** — When the structural pressure is fed back to an LLM, does it structurally change the answer? Not "does the LLM agree with the challenge" — sycophancy makes that meaningless. Does it engage with the challenge, add conditions it previously omitted, name failure modes it previously glossed over?
- **Reasoning-transport usefulness** — For V60, did the private source-backed chunks create an omitted option, evidence gate, diagnostic question, useful guardrail, or grounded rejection/defer decision? A run can be successful even when a selected chunk is not public: the ledger should show serious consideration, and the final answer should avoid forced model theater.
- **Graph survival, not premature noise labeling** — Archive-time `graph_survival_report.*` artifacts preserve selected, rejected, suppressed, budget-suppressed, and unadjudicated model signals together with embedding ranks and ledger uptake. A model that did not change the revised answer is not automatically noise; it may still be a counter-frame, antagonist, or future-review clue that changes the user's view or explains an outcome later. `reasoning_trace.json` carries the top budget-suppressed lenses directly so dataset exports can study what the run could not afford to place in the hot context.

These measurements follow a core constraint: **evals measure the process, not declare truth.** The system cannot know whether its challenge was "right" — that depends on a future that hasn't happened yet. What it can know is whether the challenge was specific, traceable, novel, and structurally grounded. A more knowledgeable decision process is the goal, not a more correct prediction.

---


## Data Dependencies

The skill carries its own copy of the compiled knowledge substrate:

| File | Size | Contents |
|------|------|----------|
| `data/knowledge_graph.json` | 2.0M | 222 models, 25 tendencies, 241 antidote bindings, 1,742 edges, 15 prerequisite edges, 15-dimension structural coverage routing, 15 reframing patterns |
| `data/relationship_graph.json` | 1.2M | 1,358 relationship edges (allies, antagonists, tensions) |
| `data/embeddings.db` | 41M | Pre-computed vectors (text-embedding-3-large, 3072d): 2,032 chunk_embeddings + 444 model_signals + 25 tendency_guidance + 867 edge_activation_conditions (~3,368 total) |
| `data/curation/` | 222 canonical model files (+ support files/subdirs) | Wave 1 activation semantics per model |
| `data/curation/intervention_semantics/` | 222 files | Wave 2 failure modes, heuristics, premortems |
| `data/curation/relation_semantics/` | 222 files | Wave 3 relationship edge data |
| `data/curated/subpattern_catalog.json` | 276K | Sub-pattern definitions for deep checks |
| `data/curated/compiled_chunks.json` | 199K | Pre-compiled knowledge chunks for bundle selection |
| `data/curated/structural_signal_lexicon.json` | 18K | Signal lexicon for trusted bundle selection |
| `data/curated/reasoning_signals.json` | 174K | Companion lane recall fallback signals |
| `data/compiled/model_affordances/affordances_v60.json` | 5.8M | Current explicit V60 artifact: 222 records, 306 source-backed affordances, 697 absence records; used only for private enrichment unless disabled |

The `data/curated/` files are critical for `is_trusted_surface: true` findings. The bundle selector requires all three files (`subpattern_catalog.json`, `compiled_chunks.json`, `structural_signal_lexicon.json`) — if any is missing, it returns `None` and all findings fall to the generic LLM path (`is_trusted_surface: false`).

When running inside the repo, the pipeline uses the repo's `build/` directly. When running standalone, the pipeline uses the skill's `data/` via a symlink (`build/` → `data/`).

---

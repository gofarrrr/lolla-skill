# Lolla — How It Works

## The Problem

LLMs are fluent but structurally undisciplined. Independent research papers from MIT, Princeton, CMU, ByteDance, NeurIPS, IBM, Oxford, UCLA, and others converge on the same conclusion: **fluency is not reasoning, and more context is not better thinking.**

- **Borrowed certainty** — LLMs create a cognitive environment where their confidence becomes your confidence, even when that confidence is unearned (Nosta, "The Borrowed Mind")
- **Artificial hivemind** — different LLMs converge on the same answers; the diversity you think you're getting from switching models is largely illusory (NeurIPS 2025, INFINITY-CHAT)
- **Structure beats context by 2.83x** — giving a model all the right facts produces 30% accuracy; giving it a structured reasoning framework produces 85% (Car Wash Study, Claude Sonnet 4.5, 120 trials, p=0.001)
- **Context pollution** — LLMs compound their own errors across turns; previous responses propagate flawed reasoning into subsequent answers (MIT/IBM)
- **Sycophancy as sampling bias** — default GPT is statistically indistinguishable from explicitly sycophantic prompting; users become 5x less likely to discover truth (Princeton, N=557)
- **Delusional spiraling** — even a perfectly rational Bayesian agent develops 99%+ certainty in wrong answers under sycophancy; factual bots and informed users reduce but don't eliminate the risk (MIT CSAIL)
- **Recovery paradox** — the better an AI's reasoning structure, the harder it is to correct when wrong; structured wrong answers become self-reinforcing (Car Wash Study)
- **Heuristic override** — surface cues (distance, cost, efficiency) dominate implicit constraints by 8.7–38x; across 14 frontier models and 500 benchmark instances, no model exceeds 75% strict accuracy — the knowledge exists but doesn't activate without structural intervention (Li et al., 2026, CMU)
- **Cognitive deskilling** — AI that provides direct answers degrades human persistence and independent performance after just 10 minutes (N=1,222, three RCTs); AI that provides scaffolding — hints, structural challenges — does not (Liu et al., 2026, CMU/Oxford/MIT/UCLA)

The gap is not facts. The gap is not better prompting. The gap is a missing layer: **a curated, inspectable substrate that knows what reasoning failure looks like and what structural counter-pressure defeats it.**

## What Lolla Is

A knowledge-first reasoning-about-reasoning engine. It audits how an LLM thought, routes that failure pattern through a curated mental-model substrate, and returns compact structural counter-pressure — not a replacement answer.

**Lolla is not in the business of finding better answers. It is in the business of being less wrong.**

LLMs are extraordinarily good at producing fluent, confident, internally consistent responses. That fluency is the problem. When the answer reads well, inconvenient tensions get smoothed out, missing reversal conditions go unnoticed, and embedded assumptions pass as established facts. The better the prose, the harder it is to see what was skipped. Lolla exists to reintroduce the friction that fluency removes — to surface the structural weaknesses that a polished narrative hides.

The product is:
- The answer was **challenged**
- The challenge came from a **curated knowledge base** (222 mental models with validated failure modes, premortems, and relationship tensions)
- The challenge is **structurally specific** — it names the reasoning pattern, the passage where it appears, and the curated counter-pressure that addresses it (not "consider the risks" but "the reasoning closes uncertainty without naming a reversal condition — Doubt Avoidance operating on this specific passage")
- The challenge is **traceable** (which tendency was detected, which models were routed, which curated chunks were selected, and why)

---

## The Core Thesis

The name "Lolla" comes from the **Lollapalooza effect** — Charlie Munger's term for what happens when multiple cognitive tendencies compound together to produce extreme misjudgment. Not a single bias, but several reinforcing each other. That compounding is what makes reasoning failures dangerous — and what makes them detectable, because compound patterns leave more structural fingerprints than isolated ones.

The engine rests on a single belief: **Munger's *Psychology of Human Misjudgment* is the right failure ontology for auditing LLM reasoning.**

Munger's 25 tendencies give us a vocabulary for recurring reasoning errors — overoptimism, authority-misinfluence, availability-misweighing, premature convergence — without depending on domain-specific language. If two answers in different domains show the same failure pattern, Lolla sees the same structural problem.

But Munger alone is not enough. Munger tells us what failure looks like. The 222-model corpus tells us what structural intervention is available. The bridge between them — 241 curated tendency→model bindings with symptom-facing activation contexts — is the product.

This has three implications:

1. **Lolla reads the thinking, not the topic.** It detects reasoning patterns (overconfidence, premature convergence, missing reversal conditions), not domain categories. "This is about business, so maybe game theory" is a failure mode. "This reasoning closes uncertainty without a stop-rule, so Doubt Avoidance is in play" is correct behavior.

2. **Lolla produces findings, not answers.** Its job is to surface compact structural pressure — what tendency is distorting the reasoning, what model challenges it, what tension was missed. The downstream LLM or human decides what to do with that pressure.

3. **Compact pressure beats long explanation.** The delta card stays small enough that a strong downstream model can absorb it as intervention pressure instead of being drowned in prose. Naming the right pressure can be enough if the downstream model is strong.

---

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

These measurements follow a core constraint: **evals measure the process, not declare truth.** The system cannot know whether its challenge was "right" — that depends on a future that hasn't happened yet. What it can know is whether the challenge was specific, traceable, novel, and structurally grounded. A more knowledgeable decision process is the goal, not a more correct prediction.

---

## Architecture

### Conductor, Not Player

**Claude is a conductor, not a player — for the audit.** It captures the conversation, calls scripts, and presents results. It performs zero reasoning judgment inside extraction, triage, routing, fingerprinting, deep checks, or card generation. Every semantic decision in the audit pipeline goes through OpenRouter where prompts are calibrated and measurable.

**Claude does author the final revised position (Step 6).** After the four cards are presented, Claude reconsiders its earlier advice under structural pressure from the curated substrate. This revised answer is persisted as a first-class run artifact with provenance (`revised_answer_source: "claude_step6"`). The Observatory renders it alongside the pipeline output.

This is a deliberate trust-boundary split:
- **Audit (detection + routing + card assembly)** — OpenRouter via calibrated prompts. Claude produced the original reasoning; asking the same LLM to find its own flaws invites sycophantic self-defense. A different model audits.
- **Reconsideration (Step 6)** — Claude. It has the full conversation context, the user's nuances, the back-and-forth. The audit cards are structural pressure, not commands. Claude absorbs that pressure and produces a revised position that is better than what it said before.

Why the audit stays external:

- **Calibration control.** You can't tune Claude's judgment the way you tune an OpenRouter prompt. The pipeline has been calibrated over hundreds of eval runs against professional-grade cases. Inline judgment has been calibrated against zero.
- **Fox can't audit the henhouse.** RLHF training optimizes for agreeable outputs. External audit breaks that loop.
- **Telemetry.** When OpenRouter runs the pipeline, we get `BoundaryCallMetadata` back — prompt tokens, completion tokens, cached tokens, reasoning tokens. This makes the system observable and measurable.

### Model Requirements

The skill is calibrated against Claude Opus 4.7 as the orchestrator. Cross-model validation on 2026-04-22 produced three tiers:

- **Opus 4.7** — recommended. Full doctrine compliance: anchor naming, machinery-leak avoidance, all nine pipeline steps execute reliably.
- **Sonnet 4.6** — acceptable. Completes the full nine-step pipeline including sub-agent spawning and artifact persistence. Modest phrasing regressions: anchor-naming rate ~66% (vs 100% on Opus); occasional machinery-term leaks in the revised answer (e.g., "sub-agents", "the audit changes"). Fit for regular use; expect marginally noisier output.
- **Haiku 4.5** — below the floor. Observed to skip Steps 6b / 6c / 7 / 8b — no `revised_answer` persistence, no memo render, no Step 7 sub-agents, no `gap_check` persistence — while generating plausible-looking output (including a fake Pressure Check) for the steps that didn't run.

The preamble asks the orchestrator to self-identify and refuse if it is Haiku. There is no machine-enforced floor — `$CLAUDE_MODEL` is not exposed by Claude Code — so the check relies on self-identification. Users on Sonnet or below should treat the `run_health` envelope (Step 4 chat) and the Observatory's completeness signals as the primary integrity check.

### Probabilistic Edges, Deterministic Middle

LLMs are extraordinary System 1 machines — fast, fluent, pattern-matching — but structurally weak at System 2: slow, deliberate, logically disciplined reasoning. Kahneman's framework from *Thinking, Fast and Slow* maps directly onto Lolla's architecture. Balaji Srinivasan sharpens this further: AI is purely probabilistic, exceptional at "middle-to-middle" generation, but it cannot self-verify. His principle — "0% AI is slow, but 100% AI is slop" — captures why Lolla exists in the space between: human-curated structure disciplining LLM flexibility.

The central design question is: **what should be flexible (LLM-driven) and what should be locked down (deterministic)?** The answer follows a principle: *LLMs at the probabilistic edges, curated knowledge in the deterministic middle.*

LLMs are irreplaceable at two things: **recognizing semantic patterns** in natural language (is this answer showing doubt-avoidance? is this reasoning implicitly using inversion?) and **generating specific reframings** grounded in mental model semantics. No deterministic system can do this reliably. So every stage that requires reading reasoning shape, detecting implicit model usage, or producing a specific alternative question is probabilistic — it goes through an LLM via OpenRouter.

But LLMs are bad at three things that matter here: **consistent routing** (the same input should always reach the same corrective knowledge), **traceable provenance** (you should see exactly which model competed and why), and **delivering out-of-distribution knowledge** (the LLM's training data doesn't contain our curated failure modes, premortem questions, and relationship tensions). So every stage that maps a detection to corrective models, traverses the knowledge graph, selects curated chunks, and assembles the output is deterministic — no LLM involvement.

This is how we bring out-of-distribution knowledge into the reasoning process without losing the flexibility that makes LLMs useful:

| Stage | Type | Why this choice |
|-------|------|-----------------|
| Pass 1 triage: 6 family-clustered specialists, each scoring 3-5 tendencies in parallel | **Probabilistic** (LLM) | Semantic judgment — "does this answer exhibit tendency X?" Obligation-chunked across tendency families (authority, closure, incentive, availability, self-regard, residual) so each call carries only that family's confusion guardrails. See *Context Engineering: Two Passes* below. |
| Embedding tendency signal | **Probabilistic** (cosine) | Swiss cheese redundancy for LLM misses |
| Threshold filtering (score ≥ 4) | **Deterministic** | Hard cutoff, reproducible |
| Deep check: isolated tendency analysis | **Probabilistic** (LLM) | Deeper semantic analysis — one tendency in isolation, no distractors |
| Routing: tendency → corrective models | **Deterministic** | Catalog lookup + graph traversal — consistent, traceable |
| 1-hop neighborhood expansion | **Deterministic with gated probabilistic tiebreaker** | RelationGraph traversal ranked by fan-adjusted affinity `aff / (1 + ln(degree))`. When top-1/top-2 land within δ<0.01 AND a typed reasoning_context is supplied, an embedding-cosine tiebreaker may swap them if max_sim≥0.45 — gated, traced, byte-identical outside the window |
| DeltaCard assembly | **Deterministic** | Tiering, compound grouping, finding presentation |
| Fingerprint: extract reasoning moves | **Probabilistic** (LLM) | Semantic — "what abstract reasoning patterns are running?" |
| Quote validation | **Deterministic** | Literal substring match |
| Recall: find candidate models | **Hybrid** | Keyword overlap (deterministic) + multi-query expanded embedding ranking with RRF fusion (probabilistic) |
| Verification: model presence | **Probabilistic** (LLM) | "Is Circle of Competence being executed or violated?" — requires reading structure |
| Chunk gathering + selection | **Deterministic** | Budget, anti-echo, dedup — curated material delivered faithfully |
| Frame extraction | **Probabilistic** (LLM) | "Does this question embed assumptions?" — requires reading the question as a reasoning artifact |
| Frame pattern → model routing | **Deterministic** | Wave 5 lookup table |
| Reframing generation | **Probabilistic** (LLM) | Creative — generate a specific alternative question grounded in a model |
| Question classification | **Probabilistic** (LLM) | "Is this a causal-diagnosis, decision-evaluation, action-planning, or prediction question?" |
| Dimension detection + coverage | **Probabilistic** (LLM) | "Which structural dimensions are present? Which ones did the answer address?" |
| Gap dimension → model routing | **Deterministic** | Compiled KG lookup with anti-echo from Lanes 1-3 |
| Gap question generation | **Probabilistic** (LLM) | "What discovery questions would help the decision-maker fill this gap?" — only fires when gaps exist |
| StructuralCoverageCard assembly | **Deterministic** | Dimension + route + question packaging |

The curated substrate provides knowledge the LLM doesn't have: specific failure modes for Circle of Competence, the exact tension between Margin of Safety and Calculated Risk Taking, premortem questions that surface hidden assumptions. The deterministic middle ensures this knowledge reaches the output faithfully — not paraphrased, not selectively summarized, not lost in the telephone game of LLM-to-LLM handoff.

### Swiss Cheese Redundancy

Embeddings and LLM triage operate as parallel layers, not sequential gates. Four invariants:

1. **Additive union, never gating intersection.** Embeddings can only ADD candidates or tendencies. They cannot remove anything the LLM or keyword path found.
2. **LLM always runs independently.** The LLM triage and fingerprint calls run whether or not embeddings are available.
3. **Graceful degradation.** If `OPENAI_API_KEY` is not set, embeddings.db is missing, or the API fails — the system works exactly as before. All embedding code returns empty results on failure.
4. **Multi-query expansion.** Embedding retrieval uses vocabulary-seeded query expansion (gpt-4o-mini generates 2 domain-relevant variants seeded with all model names). Each variant is embedded and ranked independently, then fused via Reciprocal Rank Fusion. The original query always participates, so expansion can only boost — never degrade — retrieval quality. Queries under 5 words skip expansion; any failure degrades gracefully to single-vector ranking.

This means the system has multiple independent chances to detect a pattern. In practice, embeddings catch 10-15% of tendencies that the LLM's broad triage missed — and the LLM catches patterns that embedding similarity wouldn't surface.

### Context Engineering: Two Passes

Why does Lane 1 use multiple LLM passes instead of one?

**Pass 1 is narrow and parallel — six family-clustered specialist calls, each scoring only its assigned tendencies.** The 25 Munger tendencies partition into six families by how they confuse with each other in practice:

| Cluster | Tendencies (count) | Family-specific confusion guardrails |
|---|---|---|
| `authority` | authority-misinfluence, social-proof, influence-from-mere-association, liking-loving, reciprocation (5) | 5 of the 11 guardrails (all the "external endorsement" disambiguations) |
| `closure` | doubt-avoidance, inconsistency-avoidance, deprival-superreaction, stress-influence (4) | 4 guardrails (closure-under-pressure disambiguations) |
| `incentive` | reward-and-punishment, envy-jealousy, kantian-fairness (3) | 1 guardrail (reward/punishment) |
| `availability` | availability-misweighing, contrast-misreaction (2) | 1 guardrail (availability/denominator) |
| `self_regard` | overoptimism, excessive-self-regard, simple-pain-avoiding-psychological-denial, disliking-hating, reason-respecting (5) | 0 (no active confusion pairs in the current calibration) |
| `residual` | curiosity, use-it-or-lose-it, drug-misinfluence, senescence-misinfluence, twaddle (5) | 0 (quirky tendencies without standard confusion patterns) |

The 25th tendency, `lollapalooza`, is not in any cluster — it is surfaced by the deterministic `_build_compound_groups` layer on final findings (see Lane 1 step 5), not by triage.

All six clusters run in parallel (max_workers=8). Each returns scores only for its assigned tendencies; a deterministic merge produces the full `triage_scores` list the rest of the pipeline expects. Per-cluster boundary calls are traced individually under stages `pass1_cluster_{cluster_id}` in `audit_summary.boundary_calls`, and each cluster's system prompt is hashed separately in `prompt_versions` for reproducibility.

**Pass 2 is narrow and deep** — each triggered tendency (score ≥4 OR embedding hit) gets its own isolated LLM call with only that tendency's description, its sub-pattern menu (corrective model options), and calibration guidance. No knowledge of what other tendencies were triggered.

This is context engineering on **two axes**: input chunking (each Pass 1 cluster sees only its own tendency list + relevant guardrails; each Pass 2 call sees one tendency) AND obligation chunking (each Pass 1 call scores 3-5 tendencies, not 25; each Pass 2 call judges one). Cost is 6 Pass 1 cluster calls + N Pass 2 deep checks; because both stages fan out in parallel, wall-clock stays close to single-call latency. The shift from one monolithic 25-tendency prompt to six cluster specialists was validated via the stability harness: on a fixed Marcus extraction, Pass 1 Jaccard moved from 0.50 → 0.70 (N=3), and the Availability cluster consistently surfaces `availability-misweighing` — a tendency the prior 25-in-one prompt was systematically missing. See `research/stability-runs/marcus-track-b-validation-2026-04-22/` for the full report.

### Four Independent Lanes

The four lanes share a boundary client (LLM provider) and compiled knowledge graphs, but their information never crosses during processing except at defined merge points:

- **Lane 1 ↔ Lane 2:** After both lanes complete, the cheat-sheet selector reads DeltaCard model IDs to apply anti-echo filtering — it drops heuristic chunks for models already covered by DeltaCard findings. This is a post-processing step; it doesn't feed back into either lane.
- **Lane 1 → Lane 3:** Frame routing excludes model IDs already routed by Lane 1. Overlap detection flags where frame patterns and Lane 1 tendencies operate on the same cognitive concept. Informational, not blocking.
- **Lanes 1+2+3 → Lane 4:** Structural Coverage uses anti-echo from all three lanes — models already surfaced in DeltaCard findings, companion detection, or frame reframings are excluded from gap-dimension routing. This ensures Lane 4 only surfaces genuinely new structural territory.

This separation ensures that challenge signals (Lane 1), enrichment signals (Lane 2), framing signals (Lane 3), and coverage signals (Lane 4) don't contaminate each other. The downstream consumer sees whether the system is challenging a weak reasoning path, deepening a promising one, questioning the frame, or revealing what was never addressed.

**Lane 4 (Structural Coverage)** works differently from Lanes 1-3. Where the first three lanes are *reactive* — they work from what's in the answer or question — Lane 4 is *proactive*. It decomposes the problem's shape into structural dimensions (using a curated 15-dimension MECE taxonomy), checks which dimensions the answer actually addressed, and generates discovery questions for each gap. The gap questions are the HITL bridge: they ask for situation knowledge only the decision-maker has, and are never answered by an AI. Three LLM boundary calls: (1) classify the question type, (2) detect dimensions + assess coverage, (3) generate gap questions (only when gaps exist — no gaps means no call 3).

### Trust Order

The knowledge hierarchy has a strict trust ordering:

```
Canonical markdown articles (222 files) — semantic root, always wins
    ↓
Curated Wave JSON (activation, intervention, relation) — reviewed per-model
    ↓
Compiled graph artifacts (knowledge_graph.json, relationship_graph.json)
    ↓
Pre-computed embeddings (embeddings.db) — lowest-trust retrieval layer
    ↓
Runtime LLM judgment — suggests, does not decide routing
```

Embeddings suggest candidates. LLMs detect patterns. But every embedding hit still goes through LLM deep-check (tendency lane) or LLM verification (companion lane) before it affects output. And every LLM detection gets routed through deterministic graph traversal to curated knowledge. The curated material — not the LLM's opinion — is what the user sees.

### Observability as a First-Class Artifact

Every gated decision in Lolla produces a structured trace that travels with the result. When the routing tiebreaker consults the embedding matcher, the trace records whether the gate attempted, whether it fired, and if not, which check aborted it. When the Bullshit Index evaluates a passage, each subtype's detection and reasoning is preserved inline. When the detection funnel narrows from 25 tendencies to a handful of routes, each stage's input and output is captured. These traces are never log-only — they live in `audit_summary` and `run_health` next to the findings they explain.

The principle: if a probabilistic component can override or modify a deterministic ranking, the reason must be auditable without reading code. If a detector fires, the rationale must travel with the detection. The cost of a silent gate is a system that works until it doesn't, and when it doesn't, nobody can tell why. The cost of a trace is a few dozen bytes per decision.

Traces are read two ways. The Observatory renders the richer surfaces (findings, anchors, frame elements, gap questions, delivery audit) in context. `scripts/inspect_run.py` prints a compact terminal summary of the same result JSON — detection funnel, per-route tiebreaker status with abort reasons, delivery audit counts, card-level totals. Both read from the same artifact: the trace is the data, the viewer is interchangeable. Any future gate added to the pipeline (frame-pressure calibration, coverage thresholds, Phase 4/5 activation tuning, decomposed LLM specialists) should emit its own trace into the same `audit_summary` envelope so both surfaces pick it up automatically.

The `run_health` envelope decomposes run quality into named signals the Step 4 chat can surface selectively:

- `overall`: `healthy` / `degraded` / `critical`.
- `capture`, `substrate`, `embeddings`, `fingerprint`: per-subsystem status.
- `findings_produced`: whether Lane 1 produced any findings.
- `issues[]`: specific codes — `substrate_empty`, `embeddings_off`, `no_fingerprint`, `pipeline_warnings`, `capture_degraded`, `capture_critical`, `quote_fabrication`, `capture_truncated`, `lane3_all_dropped`.
- `warnings[]`: verbose text (pipeline warnings + capture warnings).
- `capture_manifest`: declared vs actual turn counts, char length, and truncation fields when applicable.
- Counts: `quote_fabrication_count`, `quote_retry_attempted`, `capture_truncated`, `omitted_turns`, `lane3_frame_drops_count`, `lane3_frame_kept_count`.
- `activation_tiebreaker`: `on` / `off` (the per-route tiebreaker kill-switch).

Step 4 maps the material issues to user-visible one-liners; the full envelope is available in the result JSON, Observatory, and `scripts/inspect_run.py`.

A companion diagnostic tool — `scripts/stability_check.py` — computes per-stage Jaccard / text-similarity across N runs. Three modes:

- **Mode A (aggregate)** — reads existing `result.json` files and computes pairwise Jaccard for Pass 1 tendencies, Lane 2 anchor model_ids, Lane 3 reframing grounding models, Lane 4 gap dimension_ids; plus Step 6 anchor-naming rate and per-run token costs.
- **Mode B (pipeline-variance)** — reruns the pipeline N times from a fixed extraction so only pipeline sampling contributes to variance. Isolates Pass 1/Lane 2/Lane 3/Lane 4 intrinsic noise.
- **Mode C (extraction-drift)** — re-runs `run_extract.py` N times on the same conversation; measures per-field drift (similarity on free-text fields, Jaccard on list fields, fabricated-count per run).

Outputs land in `research/stability-runs/{case-id}-{date}/` as `stability.json` or `drift.json`, plus a human-readable `variance.md` or `drift.md`. The harness is diagnostic, not a gate — 1.0 Jaccard is a warning (signals a specialist that stopped doing semantic judgment), not a target.

### How Lolla Compares

| Dimension | Prompt Engineering | RAG / Context Injection | Lolla |
|---|---|---|---|
| Reasoning structure | Inside LLM (recovery paradox) | None (just more facts) | External, deterministic |
| Diversity source | Same probability distribution (hivemind) | Retrieved documents | 222 curated mental models |
| Auditability | None | Retrieval logs only | Full provenance per finding |
| Context pollution | Amplified across turns | Diluted by irrelevant retrieval | Broken by four-lane architecture |
| Sycophancy resistance | None (RLHF-trained to agree) | None | Deterministic challenge pressure |
| Cognitive friction | Removed (polished answers) | Removed | Reintroduced (structural challenges) |

---

## Step-by-Step Flow

### Step 0: Skill Activation

The skill triggers when Claude sees trigger phrases in the YAML frontmatter description:
- Explicit: "audit this", "check my reasoning", "lolla", "devil's advocate", "what am I missing", "find blind spots", "stress test", "pre-mortem", "what are we not seeing"
- Proactive: when the conversation contains strategic advice that hasn't been challenged

When triggered, Claude loads the full `SKILL.md` body and runs the **preamble bash block** first.

### Step 0b: Preamble

The preamble is a bash block that runs before anything else. It checks:

1. **Skill directory location** — resolves where the skill files live (`~/.claude/skills/lolla/`, `.claude/skills/lolla/`, or `skill/lolla/` in the repo)
2. **API key** — `OPENROUTER_API_KEY` or `LOLLA_OPENROUTER_API_KEY` must be set. Fatal if missing.
3. **Data files** — `data/knowledge_graph.json` must exist. Fatal if missing.
4. **Pipeline engine** — the bundled engine at `engine/system_b/` must be present. Fatal if missing.
5. **Reports config** — which OpenRouter model (default: `x-ai/grok-4.1-fast`), whether embeddings are enabled (`OPENAI_API_KEY` present or not)

If any check says `FATAL`, Claude stops and tells the user what's missing.

### Step 1: Capture Conversation

Claude extracts the conversation from its context window into a temp file. This is purely mechanical — no judgment.

**What gets included:**
- User messages (the human's words — these contain constraints, questions, pushback)
- Assistant prose responses (Claude's reasoning — these contain the positions being audited)

**What gets excluded:**
- Tool call inputs and outputs (file reads, code execution, search results)
- System messages and reminders
- Meta-conversation about the skill itself

**Format:**
```
[Turn 1] USER:
We're considering whether to migrate to microservices...

[Turn 1] ASSISTANT:
This is a significant architectural decision. Given the context...

[Turn 2] USER:
What about the risk of...
```

**Long conversation handling:** If the conversation exceeds ~100 turns, Claude keeps the first 3 turns (contain irreplaceable constraints) and the last 15 turns (contain the current position), with an `[... N turns omitted ...]` marker.

### Step 2: Extract Decision Structure

```bash
python3 $SKILL_DIR/scripts/run_extract.py \
  --conversation-file /tmp/lolla_{run_id}_conversation.txt \
  --output-file /tmp/lolla_{run_id}_extraction.json
```

This script reads the conversation, sends it to OpenRouter with a calibrated extraction prompt, and parses the structured response.

**First question: is this conversation strategic?** A conversation is "strategic" when the AI provides advice, recommendations, or analysis that could influence a material decision — business strategy, architecture choices, hiring, investment, product direction, vendor selection, etc. Code debugging, factual lookup, and creative writing are NOT strategic.

If not strategic → returns `{"status": "not_strategic", "decline_reason": "..."}` and Claude presents a polite decline.

If strategic → extracts 6 fields:

| Field | What It Captures | Why the Pipeline Needs It |
|-------|-----------------|--------------------------|
| `decision_situation` | The core decision as a neutral problem statement — domain, stakeholders, what's at stake | Becomes the `query` for Lane 1 triage. Tells the triage model what constraints were live, what could be skipped. |
| `live_constraints` | Every constraint the user stated. Each item carries a terse `constraint` string (≤120 chars, noun-phrase + state), plus `status: active / dropped / modified` and `weight: structural / situational`. | **The killer feature of conversation mode.** A constraint stated in turn 3 but absent from the recommendation in turn 8 is omission evidence. Lane 1 triage uses this to detect doubt-avoidance, availability-misweighing, etc. |
| `synthesized_position` | The LLM's latest/most developed recommendation, preserving reasoning structure | Becomes the `vanilla_answer`. This is what all four lanes audit. Preserving structure (not just conclusions) is critical — Lane 2 needs to see HOW the LLM argued. |
| `reasoning_passages` | 3-8 VERBATIM quotes from the assistant's messages — leaps, dismissals, assertions | Lane 2 (companion) fingerprints literal substrings to detect mental models. If these aren't exact quotes, fingerprint verification fails. |
| `original_framing` | How the human posed the problem — what was assumed fixed, what perspectives were excluded | Lane 3 (frame pressure) audits framing. If the question assumed "we must grow" and never explored "should we grow?", Lane 3 catches that. |
| `dropped_threads` | Concerns raised but never resolved — by either party | Enriches the `query` with explicit omission signals. When triage sees "user raised X, AI never addressed it", that's tendency-detection gold. |

**Capture validation, quote verification, and failure gates:**

Before sending the conversation to OpenRouter, the extraction script validates capture integrity against the raw (pre-truncation) text. Three signals feed downstream observability:

- `capture_manifest` — actual vs. declared turn counts (user, assistant) and character length. When the 80K-char cap or the "first 3 + last 15 turns on >100-turn conversations" rule fires, `capture_manifest.truncation_applied: true` is set and additional fields (`truncation_reason`, `original_char_length`, `truncated_char_length`, `total_turns`, `kept_turns`, `omitted_turns`) are populated so downstream layers and the Step 4 chat know the audit ran on dropped context.
- `capture_health` — graded `good` / `degraded` / `critical` / `unknown` (no parseable header). **`capture_health: "critical"` short-circuits the run**: the extractor returns `status: "capture_critical"` with a structured `decline_reason` and the full `capture_manifest` *before* initializing the OpenRouter client, so broken captures cost nothing. A critically degraded capture (>50% assistant turns missing, or zero assistant responses) would produce a ghost audit on partial data; the gate prevents that silent failure from entering the pipeline.
- `_quote_validation` — after extraction, each `reasoning_passages` entry is checked as a literal substring of the transcript. **If any fail, extraction retries once** with a correction prompt that lists the failed passages as examples of what NOT to do and demands character-for-character verbatim copies. If the retry produces fewer fabrications, its payload is adopted wholesale. Any fabrications that still remain after the retry are dropped from the final `reasoning_passages` list (the field contract is "literal substrings only"), a `capture_warning` is emitted, and `run_pipeline.py` surfaces `quote_fabrication` in `run_health`. `_quote_validation` also records `retry_attempted` and `retry_succeeded` for provenance.

These diagnostics surface in every output path — `ok`, `error`, `not_strategic`, and `capture_critical`.

**CritiqueRequest mapping:**

The 6 extracted fields get mapped to the 2 fields the pipeline expects:

```
query = decision_situation 
      + constraint summary (with [ACTIVE/STRUCTURAL], [DROPPED/SITUATIONAL] tags)
      + original_framing
      + dropped_threads

vanilla_answer = synthesized_position
               + numbered reasoning passages as verbatim quotes
```

This mapping is deterministic — no LLM involved.

### Step 3: Run Pipeline

```bash
python3 $SKILL_DIR/scripts/run_pipeline.py \
  --extraction-file /tmp/lolla_{run_id}_extraction.json \
  --output-file /tmp/lolla_{run_id}_result.json \
  --skip-revision
```

The `--skip-revision` flag skips the OpenRouter revision step because Claude produces the final revised position itself in Step 6. This script parses the extraction JSON, initializes the full Lolla pipeline via OpenRouter, and runs all four lanes:

```
                         ┌──────────────────────────────┐
                         │  CritiqueRequest              │
                         │  query + vanilla_answer       │
                         └──────────┬───────────────────┘
                                    │
              ┌─────────────┬───────┼───────┬─────────────┐
              ▼             ▼       ▼       ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  Lane 1  │  │  Lane 2  │  │  Lane 3  │  │  Lane 4  │
       │Structural│  │ Companion│  │  Frame   │  │ Coverage │
       │ Pressure │  │          │  │ Pressure │  │          │
       └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
            │              │              │              │
            ▼              ▼              ▼              ▼
       DeltaCard    CheatSheet    FrameCard    CoverageCard
```

**Lane 1 — Structural Pressure (3-5 OpenRouter calls):**

1. **Pass 1 (family-clustered triage):** Six OpenRouter calls run in parallel — one per tendency family (authority, closure, incentive, availability, self_regard, residual — see *Context Engineering: Two Passes* above for the full cluster taxonomy and rationale). Each cluster scores only its 3-5 assigned tendencies and carries only that family's confusion guardrails. Results are merged deterministically into a single `triage_scores` list covering all 24 canonical non-lollapalooza tendencies; lollapalooza is surfaced by deterministic compound detection (step 5 below), not by triage. Tendencies scoring ≥4 enter the "triggered" set.

2. **Embedding swiss cheese** (optional, if `OPENAI_API_KEY` set): Embeds the vanilla answer and compares against 25 pre-computed tendency guidance vectors. Any tendency below the LLM threshold but above the embedding threshold gets promoted into the triggered set. This catches what the LLM missed — and vice versa. Each triggered tendency carries a `TriggeredTendency` record with its `source` (`triage`, `embedding`, or `always_include`) and `score` — enabling observability into which detection layer caught what. The result JSON includes both `triggered_tendencies` (IDs) and `triggered_tendency_sources` (full source/score records).

3. **Pass 2 (Deep Checks):** One OpenRouter call PER triggered tendency, run in parallel (up to 8 concurrent). Each call checks ONE tendency in isolation — seeing only that tendency's definition, its sub-pattern menu, and the vanilla answer. Context isolation prevents tendency contamination. Returns: detected/not-detected, confidence, sub-pattern, specific passage, severity.

4. **Deterministic routing:** For each confirmed detection, the deterministic middle looks up corrective models from the knowledge graph (222 models, 241 bindings) and does 1-hop neighborhood expansion over allies and antagonists. Ranking uses fan-adjusted differentiated affinity (rubric 0.70/0.80/0.90/0.95, dampened by `1 / (1 + ln(degree))` at query time); within the narrow near-tie window `δ < 0.01` an activation-match tiebreaker can swap top-1 and top-2 if the curator-authored `activation_condition` embeddings score the reasoning context above `noise_floor = 0.45` and top-2 outscores top-1. The gate is traced per-route — `audit_summary.routing_decisions[].tiebreaker_supporting` / `.tiebreaker_risk` shows whether the gate fired, and if not which of seven clauses aborted it (`outside_epsilon_window`, `below_noise_floor`, `no_improvement`, etc.). Findings are assembled with curated failure modes, heuristics, and premortem questions attached to the routed models.

5. **DeltaCard assembly:** Top findings get full treatment (challenge statement, reversal trigger, corrective model, supporting models, tensions). Secondary findings get one-line summaries. Compound patterns (multiple tendencies on overlapping evidence) get flagged.

**Lane 2 — Model Companion (2-3 OpenRouter calls):**

1. **Fingerprint:** One OpenRouter call extracts 3-8 abstract reasoning moves from the vanilla answer. Each move has verbatim evidence quotes. No model names mentioned — just "weighing second-order consequences", "applying inversion", etc.

2. **Recall:** Keyword overlap + optional embedding search identifies 15-20 candidate mental models from the 222-model substrate.

3. **Verify:** One OpenRouter call checks each candidate: is the model EXECUTED (mechanism runs in the answer) or VIOLATED (answer substitutes something the model guards against)? Mere compatibility = rejection. Broad overlay models (systems-thinking, second-order-thinking) get extra scrutiny.

4. **Gather + Select:** Deterministic retrieval of curated chunks (failure modes, premortems, heuristics, antagonists) for verified models. Anti-echo filtering drops heuristic chunks for models already in the DeltaCard. Budget-constrained selection (20 chunks max, diversity guaranteed).

**Lane 3 — Frame Pressure (2 OpenRouter calls):**

1. **Frame extraction:** One OpenRouter call reads the QUERY (not the answer) for embedded assumptions, mutable constraints, and suppressed counterfactuals. Returns 0-5 frame elements. **Validation:** Elements with empty `evidence_quote` or `frame_pattern` are rejected before routing — the extraction LLM sometimes produces structurally incomplete elements. Dropped elements and their drop reasons (`missing_evidence`, `missing_pattern`) are tracked in `dropped_frame_elements` on the FramePressureCard for observability.

2. **Deterministic routing:** Each frame element's `frame_pattern` is looked up in the Wave 5 reframing routing table → candidate models.

3. **Reframing generation:** One OpenRouter call generates up to 2 alternative questions that open new reasoning paths, grounded in specific mental models.

4. **Anti-echo:** Models already used in Lane 1 are excluded. Overlap between frame patterns and Lane 1 pressure concepts is flagged.

Lane 3 is most powerful on short conversations where the question itself constrains the answer space. A question that assumes "we must grow" and never explores "should we grow?" is a frame pressure finding.

**Lane 4 — Structural Coverage (2-3 OpenRouter calls):**

Lane 4 is fundamentally different from Lanes 1-3. Where the first three lanes are *reactive* — they analyze what's in the answer or question — Lane 4 is *proactive*. It asks: "Given the shape of this problem, what structural territory did the answer never enter?" It decomposes the problem into structural dimensions using a curated 15-dimension MECE taxonomy, checks which ones the answer actually engaged with, and generates discovery questions for each gap.

The design philosophy: Lane 4 is **informative only**. It doesn't influence Lanes 1-3, doesn't change the delta card, doesn't alter companion routing. It sits at the end and surfaces structural angles the decision-maker might not have considered. Even imperfect gap detection is valuable because the gap questions — not the coverage labels — are the product.

1. **Question classification** (LLM call 1): One OpenRouter call classifies the question into one of 4 structural types — causal-diagnosis ("why is this happening?"), decision-evaluation ("should we do this?"), action-planning ("how do we do this?"), or prediction ("what will happen?"). The question type determines which dimensions can fire.

2. **Dimension detection + coverage check** (LLM call 2): One OpenRouter call examines the question and answer against a catalog of 15 structural dimensions, each defined by:
   - **Cleaving frame** — the core tension the dimension represents (e.g., "Lock-in vs Optionality" for Commitment & Reversibility)
   - **Detect_when conditions** — when the dimension is structurally present in the problem
   - **Coverage signals** — what "addressing this dimension" looks like in an answer
   - **Materiality test** — whether the gap could change the recommendation

   The detection prompt enforces a strict coverage bar: a dimension is "covered" only if the answer explicitly identifies the tension, reasons through both sides, and reaches a position. Merely *mentioning* a related topic is not coverage. A hard cap of 5 gaps prevents over-flagging — the LLM ranks gaps by materiality and keeps the top 3-5. A code-level safety net (`_MAX_GAPS=5`) demotes excess gaps if the LLM ignores the constraint.

3. **Deterministic routing**: For each uncovered dimension, the deterministic middle looks up candidate mental models from the Wave 6 structural coverage routing table in the knowledge graph (82 model bridges across 74 unique models). Anti-echo exclusion removes models already surfaced by Lanes 1, 2, and 3 — the broadest anti-echo scope of any lane.

4. **Gap question generation** (LLM call 3, conditional): For each gap dimension with routed models, one OpenRouter call generates 2-3 discovery questions following the 5Ws+H framework — concrete questions first (who, what, where, when), reflective last (why). Questions are problem-specific, plain language, and answerable only by the decision-maker from their knowledge of the situation. This call **only fires when gaps exist** — zero gaps means no LLM call, no questions. These gap questions are the HITL (Human-In-The-Loop) bridge: they are never answered by an AI.

5. **Card assembly** (deterministic): Assemble detected dimensions, gap routes, gap questions, and anti-echo metadata into a StructuralCoverageCard.

**The 15 structural dimensions:**

| Dimension | Cleaving Frame | Example Gap |
|-----------|---------------|-------------|
| Resource Allocation | Supply vs Demand | Budget stated but opportunity cost not identified |
| Incentive Alignment | Principal vs Agent | Parties listed but incentive divergence not analyzed |
| Competitive Dynamics | Collaborate vs Compete | Competitors mentioned but response not modeled |
| Risk Response | Mitigate vs Adapt | Risks noted but not sized or recovery-planned |
| Behavioral Intervention | Regulate vs Incent vs Nudge | Solution proposed without behavior-change mechanism |
| Commitment & Reversibility | Lock-in vs Optionality | Terms proposed but exit costs not considered |
| Information Quality | Signal vs Noise | Data used but reliability not questioned |
| Timing & Sequencing | Now vs Later | Timeline given but sequencing rationale absent |
| Scope & Boundary Definition | Inside vs Outside | Problem addressed but boundary not justified |
| Scaling Dynamics | What changes with scale | Growth mentioned but breakpoints not identified |
| Causal Diagnosis | Root cause vs Symptom | Correlations noted but root cause not isolated |
| Uncertainty Type | Risk vs True uncertainty | Numbers presented but uncertainty type not classified |
| Stakeholder Alignment | Agree vs Comply | People mentioned but approval/blocking analysis absent |
| Feedback & System Dynamics | Linear vs Feedback loops | Action proposed but feedback loops not considered |
| Existing vs New | Protect base vs Expand | Expansion planned but base erosion not addressed |

**Calibration approach:** The detection prompt was tuned against 14 test scenarios (in `scripts/test_lane4.py` and `scripts/test_lane4_round2.py`) using the production model (grok-4.1-fast via OpenRouter). Calibration results: 67% recall on expected gaps, ~3 false positives per scenario (capped at 5), consistent across all 4 question types. This calibration level is appropriate for an informative lane where the human filters and the questions carry the value. Known limitations: `feedback-system-dynamics` and `uncertainty-type` are under-detected; `commitment-reversibility` and `stakeholder-alignment` are over-flagged. These can be revisited by tuning detect_when conditions in the knowledge graph.

**Total OpenRouter calls:** Typically 10-13 (1 extraction + 1 triage + N deep checks + 1 fingerprint + 1 verify + 1 frame extract + 1 reframe + 1 question classification + 1 dimension detection + 0-1 gap questions). All use the calibrated boundary client with `temperature=0.2` and `response_format=json_object`. The revision step is skipped in the skill flow — Claude produces the updated position itself in Step 6, using the full conversation context and the four cards.

**Pipeline diagnostics (`run_health`):** The pipeline output includes a decomposed health status that rolls up capture diagnostics from extraction and pipeline state into one truthful object:

- `overall` — `healthy`, `degraded`, or `critical`
- `capture` — `good`, `degraded`, `critical`, or `unknown` (from extraction's `capture_health`)
- `substrate` — `ok` if compiled chunks loaded, `empty` if bundle selector failed
- `embeddings` — `active` or `off`
- `fingerprint` — `ok` if companion verified at least one model, `empty` otherwise
- `findings_produced` — whether Lane 1 produced any findings
- `issues` — array naming what's wrong: `substrate_empty`, `embeddings_off`, `no_fingerprint`, `pipeline_warnings`, `capture_degraded`, `capture_critical`
- `warnings` — merged pipeline warnings + capture warnings
- `capture_manifest` (optional) — actual vs. declared turn counts and character length from the conversation capture
- `activation_tiebreaker` — `"on"` or `"off"` (reflects the `LOLLA_ACTIVATION_TIEBREAKER` kill switch; default on)

`overall` is `critical` if capture is critical (>50% assistant turns missing), `degraded` if any issues exist, `healthy` only when all components are clean. These diagnostics make it possible to distinguish a clean "no findings" result from a broken run that produced no findings because the substrate didn't load or the conversation was badly captured.

**Per-route tiebreaker observability.** Beyond `run_health`, every detected tendency's routing decision carries a `TiebreakerTrace` under `audit_summary.routing_decisions[].tiebreaker_supporting` / `.tiebreaker_risk`. Each trace records whether the near-tie activation-match gate attempted, fired, or aborted — and if aborted, which clause stopped it. Fields include top-1/top-2 model ids and fan-adjusted affinities, top-1/top-2 cosine similarities, the delta, and the calibration constants (`epsilon`, `noise_floor`) in effect. This means a run can answer "did the activation tiebreaker intervene for this route, and if not why" from the result JSON alone. See `research/deep-graph-enrichment-handover.md §14k` for a field-by-field reading guide.

### Step 4: Present Results

Claude reads the pipeline output JSON and presents a focused chat summary — not a card dump. The detailed card rendering lives in the Observatory.

**Product vs. process separation:** The chat output uses human language exclusively. Card names (`DeltaCard`, `CompanionCheatSheet`), lane numbers, pipeline stages, severity labels, and JSON field names never appear. Findings are presented by signal strength across all finding types — not grouped by lane.

**Chat output structure:**

1. **Run-health surface (conditional):** If `run_health.overall` is not `"healthy"` AND at least one material issue is present, a short ⚠ line opens the chat before the BLUF. Material issues map to specific warnings: `capture_degraded` / `capture_critical` (capture missed turns), `substrate_empty` (curated knowledge base did not load), `no_fingerprint` (no mental-model activations), `quote_fabrication` (N reasoning passages failed literal-substring validation after retry), `capture_truncated` (N middle turns omitted), `lane3_all_dropped` (all frame elements dropped by the evidence-quote validator). Silent on `healthy` — clean runs never mention the absence of degradation.

2. **Opening line (BLUF):** One sentence naming the single most important structural weakness. This is the Sinatra Test — if this one finding lands, credibility for the whole audit follows.

3. **2-4 additional findings**, each as a short block: finding name, one bridge sentence connecting to this conversation, one concrete detail (challenge question, reframed question, or gap question — whichever is most actionable). No severity labels — severity informs which findings are selected and in what order, not how they're labeled.

4. **Mental models active (conditional):** If the companion cheat sheet surfaced anchors, one line names them by `display_name` verbatim — *"Mental models active: Opportunity Cost, Inversion — see Observatory for failure modes, premortem questions, and curated antagonists."* This primes the reader to recognize the models Step 6 will reference. Skipped when `companion_cheat_sheet.anchors` is empty.

5. **Delivery check** (conditional): If the Bullshit Index found clear detections, one line naming the count and dominant subtype. Clean delivery is the default, not an achievement — zero detections means no mention.

6. **Closing line:** One sentence pointing to Observatory.

**Bridge anti-bullshit constraints** apply to every bridge sentence: no bridge that could stand alone without the finding (anti-empty-rhetoric), no bridge that softens a finding's force (anti-paltering), no hedging language (anti-weasel), no claims not traceable to a specific passage (anti-unverified).

**Updated Position (Step 6):**
After presenting findings, Claude reconsiders its earlier advice. The structure is deliberate: first, what survived (what Claude would say again unchanged); then, what to set aside (findings Claude considered and chose not to act on, with specific reasons); finally, what actually shifted. This three-part structure forces genuine reconsideration rather than performative hedging.

An **anchor-naming invariant** constrains the reconsideration: every anchor in `companion_cheat_sheet.anchors[]` is routed through §1 (its pressure was already priced into the original advice), §2 (considered and set aside with a specific reason), or §3 (drove a change). No anchor is silently skipped. When Claude names an anchor, it uses the `display_name` verbatim — specificity is the point. This rule extends Lane 2's curated substrate from "enrichment the reviser may use" to "enrichment the reviser must account for," closing the anchor-dropout regression observed in earlier runs. Claude holds each curated chunk against the specific conversation to see if there's a live connection — some will connect sharply, some won't, and both outcomes are honest. The updated position IS the product.

**Narrative closing:** The run ends with 2-3 sentences in human language — what the audit found, where to go deeper (Observatory, memo), and what to do next. No STATUS codes, no lane counts, no CI-report formatting.

### Step 5: Observatory (Optional)

The Observatory is a full run viewer — not just a pipeline output viewer. It renders the complete audit artifact: the four cards, the revised answer, and the run's health context.

```bash
python3 $SKILL_DIR/observatory/serve_result.py --result /tmp/lolla_{run_id}_result.json
```

Zero dependencies (stdlib Python server + pre-built Svelte frontend). The backend API serves:

**Primary product:**
- Query and vanilla answer (expandable drawers)
- DeltaCard — findings with severity, passages, challenges, reversal triggers
- CompanionCheatSheet — model anchors with presence badges (EXECUTED/VIOLATED), evidence quotes, presence explanations, and typed chunks (failure modes, premortems, antagonists, heuristics, identity)
- FramePressureCard — frame elements with reframings
- StructuralCoverageCard — gap dimensions with discovery questions
- Revised answer with source provenance badge (`claude_step6`)

**Trust / health context:**
- Run health — overall, capture, substrate, embeddings, fingerprint status
- Pipeline inspector — tendency funnel (25 → triggered → detected → routed → DeltaCard)
- Delivery audit — bullshit detection with clear/unclear passage counts
- Knowledge graph — model detail views, tendency catalog browsing

**Sidebar:**
- Reasoning graph — force-directed d3 layout showing companion models, chunk references, and KG edges (ally/antagonist/tension)
- Frame pressure summary
- Structural coverage summary
- Knowledge substrate stats

### Step 5b: Memo Artifact

After the Observatory, the pipeline also produces a standalone markdown memo:

```bash
python3 $SKILL_DIR/scripts/render_memo.py \
  --result /tmp/lolla_{run_id}_result.json \
  --output /tmp/lolla_{run_id}_memo.md
```

The memo renderer is deterministic — no API calls, no LLM, pure template rendering from the result JSON. It produces a portable markdown document with up to 7 sections, each with guard clauses so the memo degrades gracefully when optional data is absent:

1. **Heading** — decision context truncated to first 2 sentences
2. **Key Findings** — from `delta_card.findings`, sorted by severity (high → medium → low), with passage deduplication (same passage blockquote rendered only once even if multiple findings reference it)
3. **Mental Model Connections** — from `companion_cheat_sheet.anchors` with presence mode
4. **Frame Alternatives** — from `frame_pressure_card.reframings`
5. **Structural Gaps** — from `structural_coverage_card.gap_questions` with dimension names
6. **Delivery Check** — from `bullshit_profile.summary` when detections exist, naming count and dominant subtype
7. **Updated Position** — `revised_answer` rendered as-is
8. **Pressure Check** — from `gap_check.lanes`, only lanes with divergences, with card names translated to human labels

The memo is the shareable artifact — it can be emailed, pasted into a doc, or read without the Observatory.

### Bullshit Index — Fact Registry

The Bullshit Index (adapted from Hannigan et al., 2025) evaluates the vanilla answer for four subtypes of bullshit: empty rhetoric, paltering, weasel words, and unverified claims. To reduce false positives on unverified claims, the BI judge receives a **fact registry** — a structured summary of what the user established in conversation.

The fact registry extracts `decision_situation`, `live_constraints`, and `dropped_threads` from the extraction JSON into a compact context block (~1500 chars vs. the previous 4000-char raw conversation truncation). The `_CONTEXT_BLOCK` instructs the judge that claims referencing, restating, paraphrasing, or drawing reasonable inferences from user-stated facts are grounded — only claims introducing information the user never provided should be flagged.

This structured approach gives the judge a cleaner signal about what counts as established context, reducing over-flagging of claims that are grounded in conversational facts.

### Run Archival

After the Observatory launches, the skill archives the run's core artifacts into a persistent case folder under `~/.local/share/lolla/runs/` (or `$LOLLA_ARCHIVE_DIR`) so the run survives `/tmp` cleanup and stays accessible for later review, memo re-rendering, or `scripts/stability_check.py` analysis. `scripts/archive_run.py` copies 7 files (`conversation.txt`, `extraction.json`, `result.json`, `revised.txt`, `memo.md`, `gapcheck.txt`, `gapcheck_lanes.json`) into `{archive_root}/{case_id}/{run_id}/`. `/tmp` originals are not touched.

The "which case is this?" question is solved without asking the user: the archive computes a **case fingerprint** from `extraction.decision_situation` (first 120 chars, normalized — lowercased, punctuation stripped, whitespace collapsed) and matches it against fingerprints stored in `{case_folder}/.case-manifest.json`:

1. **Exact match:** the new fingerprint is already in a case's manifest → file there.
2. **Fuzzy match (token-set Jaccard ≥ 0.80):** handles extractor paraphrase drift. Same conversation re-extracted twice may produce slightly different decision_situation text; the token-set match still groups them into one case. The new fingerprint is added to the manifest as an alias so future exact-match lookups are O(1).
3. **No match:** a new case folder is created. The folder name is auto-slugged from the first 3-4 significant words of `decision_situation` (e.g., `grant-equity-partnership-status`). Users can rename freely — matching is against the in-folder manifest, not the folder name.

Escape hatches:

- `$LOLLA_CASE_ID` — force a specific folder name, skipping fingerprint match. Useful when grouping a run with an existing case despite mismatched decision_situation, or when the user wants a clean folder name from the first run.
- The manifest is a plain JSON file editable by hand (rename the `case_id`, merge fingerprints, adjust the `runs[]` list after manual moves).

Orchestrator scratch files (`preamble.json`, `lane*.json`) are intentionally NOT archived — they are Claude-side working files regenerable from `result.json` if ever needed, and they may or may not exist depending on how the orchestrator staged Step 7 sub-agents.

---

## Quality Doctrine

- **Specificity over generality** — "Consider the risks" is not a finding. "The reasoning closes on a recommendation without naming what evidence would reverse it — Inconsistency-Avoidance operating on this passage" is a finding. Specificity means naming the reasoning pattern and where it appears, not domain facts.
- **Reversal triggers must be observable** — "If things go wrong" is not a trigger. "If Q2 pipeline coverage drops below 3x while integration is consuming >20% of engineering hours" is a trigger.
- **Curated knowledge IS the product** — Claude presents curated material from the pipeline output as-is. It does not generate replacement analysis, findings, or challenge statements. The curated material has been validated against source articles. Claude's generated alternatives have not.
- **Intellectual honesty** — Flag genuine uncertainty. If a detection is borderline, say so. Better to surface 3 strong findings than 8 padded ones.
- **False confidence is worse than honest uncertainty** — The whole system exists to fight borrowed certainty. It must not create more of it.
- **The process is part of the product** — Every finding is traceable: which tendency was detected, why, which models competed, which won. The system is a reasoning observability layer, not a magic answer box.

## What Lolla Is Not

- **Not a second answer.** Lolla does not compete with the vanilla model at being a domain expert.
- **Not a generic "think harder" prompt.** It routes through specific curated knowledge, not broad instructions.
- **Not a fact-checking engine.** It audits reasoning structure, not factual claims.
- **Not a domain classifier.** The query identifies live constraints and omissions, not a retrieval topic.
- **Not a consultant simulator.** It does not rewrite the memo. It surfaces compact structural pressure.
- **Not a deterministic case-solver.** The downstream model or human still decides what to do with the pressure.

Lolla succeeds when it makes better reconsideration possible, not when it dictates the outcome.

## Known Limitations

- **Pass 1 can miss tendencies.** LLM triage balances 25 hypotheses simultaneously; adjacent tendencies can be confused. Embedding swiss cheese partially addresses this.
- **Pass 2 is single-shot.** No iterative refinement. If the deep check misses a sub-pattern, it stays missed.
- **Routing is lookup-only.** 1-hop graph expansion with optional embedding reranking, no multi-hop reasoning or dynamic traversal.
- **Embedding threshold is fixed.** 0.30 for tendency signal, not tuned per tendency.
- **Companion verification is strict.** Quote verification first tries literal substring match, then falls back to fuzzy matching (80% token overlap) before rejecting as `fabricated_quote`. This catches paraphrased evidence that preserves semantic content. Genuinely fabricated quotes are still dropped.
- **No feedback loop.** Pipeline output doesn't feed back into itself. No learning from past runs — improvements come from reviewed curation at the correct layer.

---

## Data Dependencies

The skill carries its own copy of the compiled knowledge substrate:

| File | Size | Contents |
|------|------|----------|
| `data/knowledge_graph.json` | 1.9M | 222 models, 25 tendencies, 241 bindings, 1,742 edges, 15 prerequisite edges |
| `data/relationship_graph.json` | 853K | 1,358 relationship edges (allies, antagonists, tensions) |
| `data/embeddings.db` | 31M | 2,496 pre-computed vectors (text-embedding-3-large, 3072d) |
| `data/curation/` | 225 files | Wave 1 activation semantics per model |
| `data/curation/intervention_semantics/` | 225 files | Wave 2 failure modes, heuristics, premortems |
| `data/curation/relation_semantics/` | 225 files | Wave 3 relationship edge data |
| `data/curated/subpattern_catalog.json` | 45K | Sub-pattern definitions for deep checks |
| `data/curated/compiled_chunks.json` | 380K | Pre-compiled knowledge chunks for bundle selection |
| `data/curated/structural_signal_lexicon.json` | 18K | Signal lexicon for trusted bundle selection |
| `data/curated/reasoning_signals.json` | 174K | Companion lane recall fallback signals |

The `data/curated/` files are critical for `is_trusted_surface: true` findings. The bundle selector requires all three files (`subpattern_catalog.json`, `compiled_chunks.json`, `structural_signal_lexicon.json`) — if any is missing, it returns `None` and all findings fall to the generic LLM path (`is_trusted_surface: false`).

When running inside the repo, the pipeline uses the repo's `build/` directly. When running standalone, the pipeline uses the skill's `data/` via a symlink (`build/` → `data/`).

---

## Environment Requirements

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENROUTER_API_KEY` or `LOLLA_OPENROUTER_API_KEY` | Yes | All LLM judgment (extraction, triage, deep checks, fingerprint, verify, frame extraction, reframing) |
| `OPENAI_API_KEY` | No | Enables embedding swiss cheese (tendency signal, companion recall, chunk reranking). System works without it via deterministic routing only. |
| `LOLLA_OPENROUTER_MODEL` | No | Override model (default: `x-ai/grok-4.1-fast`) |
| `LOLLA_LLM_TIMEOUT` | No | Timeout per boundary call in seconds (default: 45, max: 120) |
| `LOLLA_REPO_ROOT` | No | Override engine location (not needed for standard installs) |

---

## Edge Cases

| Situation | What Happens |
|-----------|-------------|
| Conversation is about code debugging | Extraction returns `not_strategic`, Claude presents polite decline |
| Conversation is 1-2 turns | Extraction still works. Less material for Lane 2 fingerprinting. Lane 3 (frame pressure) is most useful on short conversations. |
| Conversation is 100+ turns | Claude truncates: first 3 + last 15 turns. Early turns preserve constraints. |
| Pipeline finds zero tendencies | Valid outcome. "No structural pressures detected." |
| OpenRouter times out | Boundary client handles retries internally. If all attempts fail, pipeline returns partial results. |
| `OPENAI_API_KEY` not set | Embeddings disabled. Pipeline runs purely on LLM triage + deterministic routing. Works fine, just without the swiss cheese redundancy layer. |
| Multiple strategic threads in one conversation | Extraction captures the most developed/recent thread. |

---

## Cost Per Run

A typical run makes 18-25 OpenRouter calls against `x-ai/grok-4.1-fast`:
- 1 extraction call (~3K tokens in, ~1K out); +1 retry on quote fabrication (~14% of runs observed) adds ~2-3K tokens
- 6 Pass 1 cluster triage calls in parallel (~5-6K tokens each; ~5,600 prompt + 150-300 completion per cluster)
- 2-7 deep check calls (~2K tokens each; count depends on how many tendencies triggered)
- 2 companion calls — fingerprint + verification (~3K tokens each)
- 2 frame pressure calls — extraction + reframing (~2K tokens each)
- 2-3 structural coverage calls (~2K tokens each): question classification, dimension detection + coverage, gap question generation (conditional, only when gaps exist)

Total: roughly 60-110K tokens per run. At Grok 4.1 Fast pricing, approximately $0.04-0.10 per audit. Embeddings (if enabled) add one gpt-4o-mini expansion call (~$0.001) plus a batch embedding call for the original query + 2 domain variants (~$0.0002). The revision step is available for headless/eval runs but skipped in the skill flow — Claude produces the updated position directly.

The cost bump compared to earlier versions is load-reduction working as designed. Pass 1 was previously a single monolithic call scoring all 25 tendencies under ~11 confusion guardrails; it is now six family-clustered specialists (3-5 tendencies each, family-relevant guardrails only). The trade-off is more calls for narrower per-call load — and measured Pass 1 stability moved from 0.50 → 0.70 Jaccard on a fixed Marcus extraction as a result.


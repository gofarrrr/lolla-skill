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

### Current State (2026-04-25)

The pipeline runtime is fully conversation-native. `SystemBPipeline.run()` accepts `ConversationContext` and nothing else — passing anything else raises `TypeError`. The legacy `CritiqueRequest(query, vanilla_answer)` runtime contract and lane shims have been removed from the engine. The extraction/CLI artifact layer still preserves compatibility fields for older captured runs, but normal file-based runs now derive post-processing text (`case_focus`, `audit_target_assistant_text`) from `ConversationContext` first. Every lane reads from a typed, provenance-bearing `ConversationIR` projected through the IR packet layer.

The substrate, top to bottom:

| Layer | Object | Module | What it owns |
|---|---|---|---|
| Input | `ConversationContext` | `engine/system_b/conversation_context.py` | Raw turns + typed extraction (`LiveConstraint`, `DroppedThread`, …) + capture metadata |
| IR | `ConversationIR` | `engine/system_b/ir.py` | Immutable, provenance-bearing intermediate representation |
| IR build | `construct_conversation_ir(...)` | `engine/system_b/ir_constructor.py` | Builds the IR at pipeline entry. Accepts optional specialist callables as keyword args (`stance_extractor`, `live_constraints_extractor`, `dropped_threads_extractor`); the production `SystemBPipeline.run()` path calls it WITHOUT specialists, so the default IR is built deterministically from extraction fields. |
| Specialists (supported, not default-wired) | `extract_stance_events`, `extract_live_constraints`, `extract_dropped_threads` | `stance_extraction.py`, `live_constraints_extraction.py`, `dropped_threads_extraction.py` | LLM-backed substring-validated upgrades to specific IR objects. Available as injectable dependencies; not invoked by the default pipeline. Used today by tests, eval harnesses, and ad-hoc callers; will graduate to default wiring once promotion criteria documented in the *Evolution* section are met per field. |
| Packet | `Lane4Packet` | `engine/system_b/packet_builders/lane4.py` | Minimum projection of the IR each lane reads |
| Lanes | Companion / Frame Pressure / Structural Coverage / Pass1+Pass2 | `companion_routing.py`, `frame_pressure.py`, `structural_coverage.py`, `pass1_runner.py` + `pass2_runner.py` | Each lane consumes the packet and produces a card |
| Audit | `AuditTrace`, `build_pipeline_audit_trace` | `audit_assembly.py` | Aggregates per-call telemetry, lane outputs, warnings |
| Telemetry | `BoundaryCallTrace`, `BoundaryCallMetadata` | `boundary_tracing.py`, `boundary_provider.py` | Per-call model + token counts (prompt/completion/total/cached/reasoning) |

The IR's three provenance tiers — `span` (exact substring in one turn), `turn_ref` (paraphrase, source turn known), `derivation` (multi-turn synthesis with refs) — make the difference between substring-validated content and honest paraphrase visible to every consumer downstream. No paraphrase ever masquerades as a quote.

### Evolution: How It Used to Work, How It Works Now, and Why

The shape above isn't where Lolla started. It's the result of ~15 sequenced migrations that each replaced a load-bearing piece with a more honest version. The story matters because reading the codebase without it leaves the question "why is there a `Lane4Packet` projecting from an `ConversationIR` built from `ConversationContext`? why three layers?" — and that question has a real answer at every layer.

#### Origins: The CritiqueRequest era

Before the migration, the runtime contract was a single dataclass:

```python
@dataclass(frozen=True)
class CritiqueRequest:
    query: str
    vanilla_answer: str
```

Two flat strings. Every lane received `(query, vanilla_answer)`. Even though extraction produced six richly-shaped fields (`decision_situation`, `live_constraints`, `synthesized_position`, `reasoning_passages`, `original_framing`, `dropped_threads`), they got collapsed into the `query` and `vanilla_answer` strings before lanes ever saw them via a helper called `_context_to_critique`.

What broke under this shape:

- **Quote fabrication.** When a lane wanted to validate "did the user actually say X?", the only string it could check against was the flattened `query` — which already contained extractor paraphrase. Lanes routinely produced `evidence_quote` claims that weren't in the original conversation because the extractor's paraphrase happened to contain a similar phrase.
- **Provenance opacity.** Findings claimed authority but had no traceable line back to the source text. "The user said X in turn 3" was unverifiable because turns no longer existed at the lane boundary.
- **Saturation.** A single extraction prompt was being asked to produce all six fields plus quote validation. New rules competed with existing rules in the same context. We hit a ceiling on extraction quality that wasn't fixable by prompt-engineering.
- **Diminishing returns from "more context."** Adding more rules to extraction made things worse, not better. The structural problem wasn't extraction-prompt quality; it was the lane-input contract throwing away structure.

#### The migration: one phase at a time, gated before and after

Each phase had a four-step discipline: an annotation gate (humans reviewed candidates blind, looking for inter-reviewer agreement above a threshold) → only if the gate passed, write the specialist code → run a live LLM eval against the gate's gold set → ship only if recall, validation pass rate, and kind agreement cleared their thresholds. If the gate or eval failed, the phase didn't ship; the doctrine was "no specialist without measurement evidence."

| Phase | What it changed | Why we picked this |
|---|---|---|
| **Phase 1** — `ConversationIR` | Added a typed substrate `engine/system_b/ir.py` with `Turn`, `SpanRef`, `FrameAnchor`, `UserIssueEvent`, `StanceEvent`, plus a 3-tier `Provenance` union (`span` / `turn_ref` / `derivation`). Built at pipeline entry from the context; populated conservatively from existing extraction fields. | The ontology gate (`research/phase1-useriussevent-annotation-exercise-2026-04-24.md`) scored 16/17 (94.1%) inter-reviewer agreement on the three-kind taxonomy `(constraint, concern, open_loop)`. That validated the smallest-possible substrate before any new extraction code shipped. The "promote only when measurement shows value" doctrine kept `ActorRef`, `DecisionOption`, `ReasoningSegment` deferred. |
| **Phase 3a / 3b** — `StanceEvent` + LLM stance specialist | Added `relation_ambiguity: bool` to `StanceEvent`. Built `engine/system_b/stance_extraction.py`: an LLM specialist that pulls assistant-turn substrings using a 6-relation taxonomy (`commitment`, `revision`, `qualification`, `condition`, `deferral`, `initial`). Substring-validated via `find_substring_tolerant`; paraphrase fails and is dropped + counted. | Pre-code annotation gate (`research/phase3-assistant-trajectory-annotation-gate-2026-04-24.md`) scored 100% detection / 95% relation across 20 candidates with two reviewers. Live eval shipped at 60% recall / 97% validation pass / 83% relation agreement — proven mechanism, lower iteration risk than 25-tendency monolith. |
| **Phase 5** — `live_constraints` specialist | `engine/system_b/live_constraints_extraction.py`: emits `UserIssueEvent(kind="constraint")` with either `SpanProvenance` (one-turn anchor) or `DerivationProvenance` (cross-turn synthesis, each excerpt validated). Single-turn derivation claims auto-downgrade to span mode (anti-bypass safeguard). | The Phase 2 evidence study found **0/71** live_constraints across 10 cases had a full exact substring source. Monolith extraction was architecturally paraphrase-only. Phase 5 specialist took the field substring-grounded. Live eval: 70% recall, 97% validation, 93% kind agreement, 100% derivation recall. |
| **Phase 5.5** — `dropped_threads` specialist | `engine/system_b/dropped_threads_extraction.py`: same shape as Phase 5 but with a `speaker` field per event (user OR assistant). Single-span only; the gate found no items needing derivation. | Annotation gate scored 94% span convergence, 100% speaker agreement on 9 items. Live eval shipped at 56% recall / 92% validation / 100% speaker / 40% kind — partial pass. The kind drift (LLM picks `concern` where gate said `open_loop` on emotionally-weighted content) is a methodological disagreement, not a bug; PM accepted under documented caveat. |
| **Phase 5.7** — `original_framing` heuristic | NOT a specialist. Replaced `FrameAnchor.provenance = TurnRefProvenance(first_user_turn_only)` with `DerivationProvenance(all_user_turns)` and an honest note. | The Phase 5.7 gate showed 0% inferred for situation parts, 50% for assumptions, **100% for exclusions**. An LLM specialist would need three emit modes (span/derivation/inferred) and would re-encode the same answer in a more complex form. Heuristic gives ~80% of the value at ~10% of the cost. |
| **Phase 5.8** — `decision_situation` heuristic | Same heuristic as 5.7. Skipped formal annotation gate; used a memo with 10-case structural decomposition because the inferred-rate distribution was even more favorable than 5.7's. | Honest tech-lead call: when a directly comparable gate just fired, ceremony to re-discover the same answer is dead weight. Memo (`research/phase5.8-decision-situation-design-memo-2026-04-25.md`) listed falsification triggers for revisit. |
| **Phase 4 + 4b + 4c** — Lane packet builders | Added `engine/system_b/packet_builders/lane4.py` with `Lane4Packet`. Wired all four lanes: `_run_companion`, `_run_frame_pressure`, `_run_structural_coverage`, `_run_pass2_*` now build a packet from IR and call `*_from_packet` formatters. Byte-equivalence tests prove identical prompts to the prior `*_from_context` path on lossless inputs. | Lanes now read from the typed substrate, not raw `extraction.X` paraphrases. When a specialist swaps in (substring-validated `live_constraints` or `dropped_threads`), every lane automatically gets the upgraded data with zero lane-side changes. The packet is the seam that decouples extraction quality from lane prompts. |
| **Phase 4d** — dead `_from_context` dispatch fallbacks removed | Each lane orchestrator's `elif conversation_context is not None: ..._from_context(...)` branch deleted. Phase 4 made these unreachable in practice (IR always built when context present). | Pure cleanup; -91 lines. The `*_from_context` source functions themselves stayed — tests still use them as anti-regression. |
| **Phase 7.1 / 7.2 / 7.3 / 7.5** — Split `pipeline.py` | `pipeline.py` was 2401 lines. Extracted into focused modules: `boundary_tracing.py` (88 lines), `pass1_runner.py` (121), `pass2_runner.py` (154), `audit_assembly.py` (261). Net: pipeline.py shrank to 2062 lines (−14%). Public re-exports preserved every external import path. | Phase 6 was about to delete a lot of code, and a 2400-line file makes deletion risky. Splitting first made Phase 6's surface tractable. 7.4 (lane orchestrators) was deliberately skipped — their instance-state dependency bag wasn't deep enough to justify a layer at this point. |
| **Phase 6** — `CritiqueRequest` runtime shim removed | -2179 net lines across 26 files. `CritiqueRequest`, `_context_to_critique`, every legacy lane entry point (`run_fingerprint_call`, `run_verification_call`, `run_frame_extraction`, `run_structural_coverage`, `format_pass2_prompt`, `format_pass1_cluster_prompts`), every legacy helper, the `--legacy-contract` CLI flag, the shim-equivalence test suite (927 lines), and `scripts/phase1_equivalence_check.py` all deleted. `SystemBPipeline.run()` now requires `ConversationContext`; raises `TypeError` on anything else. | Until Phase 6, the conversation-first migration had a parallel-paths shape: new code beside old code, dispatch checking which to run. That's transitional architecture, not target architecture. Deleting the legacy lane path is what makes the new runtime contract real. Artifact compatibility fields may still exist outside the engine; they are not lane inputs. |
| **Post-Phase-7 audit cleanup (PR #36 + follow-up, 2026-04-25/26)** | Six findings plus compatibility-boundary cleanup: (1) `audit_summary.boundary_summary` aggregate (call_count + token totals + cache hit rate + reasoning-leak flag) replaces having to walk individual boundary calls for cost review; (2) silent `synthesized_position or ""` fallbacks replaced with explicit empty + warning when extraction is degenerate; (3) `vanilla_answer` parameter renamed to `assistant_text` in helpers that receive joined assistant turns; (4) top-level `query` / `vanilla_answer` keys in `result.json` replaced with an `extraction` block carrying the full serialized `ConversationContext` (turns + extraction summaries) — Observatory + render_memo derive displayed case focus / assistant audit target from joined turns and use `decision_situation` for case naming; (5) ~20 orphan `*_from_context` lane functions deleted (~1100 lines net); (6) Pass 1 prompt: added a "hedging is not absence" rule symmetric to the existing "don't score on confidence alone" rule + SKILL.md `CompanionCheatSheet` schema correctly documents `presence_mode` instead of stale `status` (which had caused inline debug prints to render `[None]` because Claude was reading a non-existent field); (7) `scripts/run_pipeline.py` stopped requiring legacy `query` / `vanilla_answer` fields for normal file-based runs, derives `case_focus` and `audit_target_assistant_text` from `ConversationContext`, and treats `audit_seed` / `critique_request` only as compatibility fallback. | Post-Phase-7 cleanup of leftovers from the migration. Found a silent drift bug: `prompt_versioning.py` was hashing a legacy `PASS_2_DEEP_CHECK_SYSTEM` constant the runtime no longer used — version stamps no longer reflected reality. Fixed. The later compatibility-boundary cleanup keeps old artifacts runnable without letting old names define the live contract. |
| **Lane 1 conversation-scope expansion (PR #37, 2026-04-25)** | Pass 1 + Pass 2 system prompts in `engine/system_b/prompts.py` and `engine/system_b/deep_checks.py`: SOURCE is now the actual conversation transaction (both speakers), CONTEXT is extraction summaries only (paraphrased layer). Added `MISSED CHALLENGE` as a fourth tendency shape; broadened `UNCRITICAL ACCEPTANCE` from "recycles vivid material" to "inherits user-introduced framing — vivid OR structural — without testing it." Materiality bar preserved. | Pre-PR-#37, Lane 1 audited the assistant in isolation. Whistleblower (0 findings, P2c baseline 1) and oncologist (0 findings, P2c baseline 2) were silent because the bias lived at the user/assistant junction — the user introduced a tendency-shaped frame and the assistant absorbed it silently. Lane 1 had no shape for "the assistant carries the tendency by silent inheritance." Validation across the 10-case corpus + Marcus: whistleblower 0 → 2, real_estate 0 → 1 (bonus correct detection), Marcus 3 → 4, others stable; net findings basically flat against P2c baseline; one Phase 2c detection (parenting_teen authority-misinfluence on RAINN references) corrected as an over-fire on legitimate evidence-application. The discipline that emerged: never tune a prompt to "recover" a single case without re-reading the conversation first — Phase 2c got parenting_teen wrong reliably, and reliability isn't accuracy. |

#### Today: ConversationContext → ConversationIR → Lane Packets

The data flow from input to lane consumption now looks like:

```
extraction.json + conversation.txt
        ↓
ConversationContext (turns + typed extraction + capture metadata)
        ↓ construct_conversation_ir(...)
ConversationIR (typed objects + provenance tiers)
        ↓ optional: stance_extractor / live_constraints_extractor / dropped_threads_extractor
ConversationIR (substring-validated where specialists ran)
        ↓ build_lane4_packet(ir)
Lane4Packet (minimum slice the lanes need + provenance_kind metadata)
        ↓
Lane 1 / Lane 2 / Lane 3 / Lane 4 → Cards → AuditTrace
```

Every step preserves more structure than the one before. Nothing collapses to flat strings.

#### Why this shape, in one sentence per layer

- **`ConversationContext`** exists so the raw turn-by-turn transcript stays canonical and quote-fabrication is mechanically detectable (every alleged quote has to literally appear in some turn).
- **`ConversationIR`** exists because lanes need typed, provenance-bearing objects (not paraphrased strings) to produce findings that can be audited back to source text without re-parsing.
- **Specialists** (Phase 3b / 5 / 5.5) exist because the monolith extraction prompt could not produce substring-grounded fields no matter how hard it was tuned — the architectural answer was a separate substring-validated specialist per field, gated by annotation evidence and measured against gold.
- **Packet builders** (Phase 4) exist because lanes shouldn't depend on the IR's internal shape evolving — they consume a contract (`Lane4Packet`) that names exactly the slice they need, with `provenance_kind` metadata that lets future lane prompts mark "this is span-validated" vs "this is paraphrase".
- **Module split** (Phase 7) exists because navigability matters when `pipeline.py` is the orchestration entry point and reviewers need to understand it quickly.
- **Phase 6's removal** exists because keeping legacy alongside new is technical debt with a half-life — every refactor pays the cost of dispatching between paths.

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

If strategic → extracts 6 current compatibility fields:

| Field | What It Captures | Why the Pipeline Needs It |
|-------|-----------------|--------------------------|
| `decision_situation` | The core decision as a neutral problem statement — domain, stakeholders, what's at stake | Provides a compact compatibility summary and helps classify whether the conversation is strategic. In the target architecture this is a derived view, not the source of truth. |
| `live_constraints` | Every constraint the user stated. Each item carries a terse `constraint` string (≤120 chars, noun-phrase + state), plus `status: active / dropped / modified` and `weight: structural / situational`. | Transitional user-side issue signal. A constraint stated in turn 3 but absent from the recommendation in turn 8 is omission evidence. In the v1 IR this intent becomes `UserIssueEvent(kind="constraint")` with turn/span provenance. |
| `synthesized_position` | The LLM's latest/most developed recommendation, preserving reasoning structure | Compatibility projection of the latest assistant position. It remains useful for legacy/headless paths, but the target architecture models this as a `StanceEvent` trajectory with "latest stance" as a projection. |
| `reasoning_passages` | 3-8 VERBATIM quotes from the assistant's messages — leaps, dismissals, assertions | Evidence-eligible assistant substrings for Lane 2. If these aren't exact quotes, fingerprint verification fails. In the target architecture these become packet-local reasoning spans, and only graduate to `ReasoningSegment` if measurement justifies it. |
| `original_framing` | How the human posed the problem — what was assumed fixed, what perspectives were excluded | Bootstrap input for Lane 3 frame pressure. In the v1 IR this intent becomes `FrameAnchor` with source-span provenance. |
| `dropped_threads` | Concerns raised but never resolved — by either party | Transitional omission/open-loop signal. In the v1 IR this intent becomes `UserIssueEvent(kind="concern" \| "open_loop")` with lifecycle (`active`, `resolved`, `superseded`). |

These fields are the current extraction contract, not the target ontology. The raw transcript inside `ConversationContext` remains canonical; extracted fields are derived context and compatibility surfaces until the provenance-bearing IR replaces summary-first extraction.

**Capture validation, quote verification, and failure gates:**

Before sending the conversation to OpenRouter, the extraction script validates capture integrity against the raw (pre-truncation) text. Three signals feed downstream observability:

- `capture_manifest` — actual vs. declared turn counts (user, assistant) and character length. When the 80K-char cap or the "first 3 + last 15 turns on >100-turn conversations" rule fires, `capture_manifest.truncation_applied: true` is set and additional fields (`truncation_reason`, `original_char_length`, `truncated_char_length`, `total_turns`, `kept_turns`, `omitted_turns`) are populated so downstream layers and the Step 4 chat know the audit ran on dropped context.
- `capture_health` — graded `good` / `degraded` / `critical` / `unknown` (no parseable header). **`capture_health: "critical"` short-circuits the run**: the extractor returns `status: "capture_critical"` with a structured `decline_reason` and the full `capture_manifest` *before* initializing the OpenRouter client, so broken captures cost nothing. A critically degraded capture (>50% assistant turns missing, or zero assistant responses) would produce a ghost audit on partial data; the gate prevents that silent failure from entering the pipeline.
- `_quote_validation` — after extraction, each `reasoning_passages` entry is checked as a literal substring of the transcript. **If any fail, extraction retries once** with a correction prompt that lists the failed passages as examples of what NOT to do and demands character-for-character verbatim copies. If the retry produces fewer fabrications, its payload is adopted wholesale. Any fabrications that still remain after the retry are dropped from the final `reasoning_passages` list (the field contract is "literal substrings only"), a `capture_warning` is emitted, and `run_pipeline.py` surfaces `quote_fabrication` in `run_health`. `_quote_validation` also records `retry_attempted` and `retry_succeeded` for provenance.

These diagnostics surface in every output path — `ok`, `error`, `not_strategic`, and `capture_critical`.

**How the runtime reads these fields:**

The extraction JSON is wrapped together with the raw conversation text and capture metadata into a `ConversationContext`. From there `construct_conversation_ir(context)` builds a `ConversationIR`: each `live_constraint` becomes a `UserIssueEvent(kind="constraint")`, each `dropped_thread` becomes a `UserIssueEvent(kind="open_loop"|"concern")`, each of `original_framing` and `decision_situation` becomes a `FrameAnchor` with `DerivationProvenance` over all user turns, and `synthesized_position` is held as transitional text the runtime can read but never claims as a verbatim quote.

The default production pipeline (`SystemBPipeline.run()`) calls `construct_conversation_ir(context)` with no specialist extractors — the IR is built deterministically from the extraction fields above. `construct_conversation_ir` *also* accepts optional `stance_extractor`, `live_constraints_extractor`, and `dropped_threads_extractor` keyword arguments; when an injected specialist is provided, it replaces the corresponding paraphrased mapping with substring-validated events whose `text` is a literal substring of the named turn. This injection path is exercised today by tests, eval harnesses, and ad-hoc callers; default wiring is gated on the promotion criteria documented in the *Evolution* section. Either way, lanes read the IR through `Lane4Packet` (no lane sees the raw `extraction.X` paraphrases at the prompt boundary).

### Step 3: Run Pipeline

```bash
python3 $SKILL_DIR/scripts/run_pipeline.py \
  --extraction-file /tmp/lolla_{run_id}_extraction.json \
  --conversation-file /tmp/lolla_{run_id}_conversation.txt \
  --output-file /tmp/lolla_{run_id}_result.json \
  --skip-revision
```

The `--skip-revision` flag skips the OpenRouter revision step because Claude produces the final revised position itself in Step 6. With both `--extraction-file` and `--conversation-file`, `run_pipeline.py` wraps the raw conversation, extraction JSON, and capture metadata as `ConversationContext` by default. This script initializes the full Lolla pipeline via OpenRouter and runs all four lanes:

```
                         ┌──────────────────────────────┐
                         │  ConversationContext          │
                         │  raw turns + extraction       │
                         │  + capture metadata           │
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

#### Conversation-first contract

`SystemBPipeline.run()` accepts `ConversationContext` and only `ConversationContext`; passing anything else raises `TypeError`. The IR is constructed at entry (`conversation_ir = construct_conversation_ir(conversation_context)`) and threaded through every lane via `Lane4Packet`. There is no legacy two-string input shape, no `--legacy-contract` flag, no parallel dispatch — Phase 6 deleted all of it. See the *Evolution* section above for what was removed and why.

**Lane 1 — Structural Pressure (6+N OpenRouter calls):**

1. **Pass 1 (family-clustered triage):** Six OpenRouter calls run in parallel — one per tendency family (authority, closure, incentive, availability, self_regard, residual — see *Context Engineering: Two Passes* above for the full cluster taxonomy and rationale). Each cluster scores only its 3-5 assigned tendencies and carries only that family's confusion guardrails. Results are merged deterministically into a single `triage_scores` list covering all 24 canonical non-lollapalooza tendencies; lollapalooza is surfaced by deterministic compound detection (step 5 below), not by triage. Tendencies scoring ≥4 enter the "triggered" set.

2. **Embedding swiss cheese** (optional, if `OPENAI_API_KEY` set): Embeds the joined assistant-turn text and compares against 25 pre-computed tendency guidance vectors. Any tendency below the LLM threshold but above the embedding threshold gets promoted into the triggered set. This catches what the LLM missed — and vice versa. Each triggered tendency carries a `TriggeredTendency` record with its `source` (`triage`, `embedding`, or `always_include`) and `score` — enabling observability into which detection layer caught what. The result JSON includes both `triggered_tendencies` (IDs) and `triggered_tendency_sources` (full source/score records).

3. **Pass 2 (Deep Checks):** One OpenRouter call PER triggered tendency, run in parallel (up to 8 concurrent). Each call checks ONE tendency in isolation — seeing only that tendency's definition, its sub-pattern menu, and the conversation transaction (both user and assistant turns) under audit. Context isolation prevents tendency contamination. Returns: detected/not-detected, confidence, sub-pattern, specific passage, severity. As of PR #37 (2026-04-25), the audit target is the conversation transaction rather than the assistant's turns alone — see *Lane 1 prompt structure* below for the four firing shapes (commission, omission, uncritical acceptance, missed challenge) and the rationale.

4. **Deterministic routing:** For each confirmed detection, the deterministic middle looks up corrective models from the knowledge graph (222 models, 241 bindings) and does 1-hop neighborhood expansion over allies and antagonists. Ranking uses fan-adjusted differentiated affinity (rubric 0.70/0.80/0.90/0.95, dampened by `1 / (1 + ln(degree))` at query time); within the narrow near-tie window `δ < 0.01` an activation-match tiebreaker can swap top-1 and top-2 if the curator-authored `activation_condition` embeddings score the reasoning context above `noise_floor = 0.45` and top-2 outscores top-1. The gate is traced per-route — `audit_summary.routing_decisions[].tiebreaker_supporting` / `.tiebreaker_risk` shows whether the gate fired, and if not which of seven clauses aborted it (`outside_epsilon_window`, `below_noise_floor`, `no_improvement`, etc.). Findings are assembled with curated failure modes, heuristics, and premortem questions attached to the routed models.

5. **DeltaCard assembly:** Top findings get full treatment (challenge statement, reversal trigger, corrective model, supporting models, tensions). Secondary findings get one-line summaries. Compound patterns (multiple tendencies on overlapping evidence) get flagged.

**Lane 1 prompt structure.** Pass 1 (family-clustered triage) uses `format_pass1_cluster_prompts_from_context`; Pass 2 (per-tendency deep checks) uses `format_pass2_prompt_from_packet`. **As of PR #37 (2026-04-25), both passes audit the conversation transaction — both speakers — not the assistant in isolation.** CONTEXT is the extraction summaries (a paraphrased layer; not citable as evidence). SOURCE is the actual conversation, turn by turn — user turns AND assistant turns. The audit target is how user-introduced framing was handled by the assistant, not the assistant's words alone. The system prompt names **four** legitimate firing shapes:

1. **Commission** — the assistant explicitly says something that exhibits the tendency.
2. **Omission** — the assistant commits to a move while skipping a check, denominator, dependency, reversal condition, pilot, or stop rule that the user's framing made live. *Hedging or staging the answer in steps does NOT neutralize an omission.*
3. **Uncritical Acceptance** — the assistant inherits user-introduced framing — vivid OR structural — without testing it. Single-actor assumptions, binary collapses, fixed-constraint claims, authority-rank deference, confident statistics all count, whether the assistant repeats them verbatim or just builds on top of them.
4. **Missed Challenge** (NEW in PR #37) — the user's framing carries a tendency-shaped move and the assistant proceeds without surfacing or testing it. Silent inheritance is a form of the tendency: the assistant does not need to QUOTE the move to CARRY it.

This is the conversation-scope expansion: pre-PR-#37, Lane 1 was blind to tendencies that lived at the user/assistant junction (the user introduces a frame, the assistant absorbs it without quoting it back). Validated against the 10-case corpus + Marcus: whistleblower 0 → 2, real_estate 0 → 1, Marcus 3 → 4, others stable; one prior detection (parenting_teen, P2c authority-misinfluence on RAINN references) corrected as it had been an over-fire on legitimate evidence-application. Both Pass 1 and Pass 2 prompts carry enum-checklist reminders that remind the LLM to consider every tendency / sub_pattern in the menu even when it manifests as omission, uncritical acceptance, or missed challenge rather than verbatim claim. The same reminder explicitly tells the LLM that hedged, structured, or multi-step reasoning does NOT neutralize a tendency — a structured plan that commits to a path without naming reversal triggers still carries the tendency. Routing, fan correction, activation tiebreaker, compound detection, and DeltaCard assembly are input-shape-invariant — they operate on `DeepCheckResult` objects.

**Lane 2 — Model Companion (2 OpenRouter calls — fingerprint + verification; recall is deterministic):**

1. **Fingerprint:** One OpenRouter call extracts 3-8 abstract reasoning moves from the assistant source text under audit. Each move has verbatim evidence quotes. No model names mentioned — just "weighing second-order consequences", "applying inversion", etc.

2. **Recall:** Deterministic candidate selection up to a 60-model cap. Keyword overlap reads the joined assistant text against each model's name + activation triggers; reasoning-signals fallback (`data/curated/reasoning_signals.json`, 217 keys) extends candidates when keyword matching is sparse; optional multi-query embedding ranking (RRF-fused) adds candidates when `OPENAI_API_KEY` is set. The cap is the candidate slate the verifier sees — typical fingerprints fill it, narrow ones don't.

3. **Verify:** One OpenRouter call checks each candidate: is the model EXECUTED (mechanism runs in the answer) or VIOLATED (answer substitutes something the model guards against)? Mere compatibility = rejection. Broad overlay models (systems-thinking, second-order-thinking) get extra scrutiny.

4. **Gather + Select:** Deterministic retrieval of curated chunks (failure modes, premortems, heuristics, antagonists) for verified models. Anti-echo filtering drops heuristic chunks for models already in the DeltaCard. Budget-constrained selection (20 chunks max, diversity guaranteed).

**Lane 2 prompt structure.** Fingerprint and verification calls use `run_fingerprint_call_from_packet` and `run_verification_call_from_packet` (Phase 4c). User-prompt bodies follow the same CONTEXT (extractor summaries + user turns, NOT quotable) / SOURCE (assistant turns verbatim, audit target) split as Lane 3. (Lane 1 broadened SOURCE to include both speakers in PR #37 — see *Lane 1 prompt structure* — but Lane 2's SOURCE = assistant turns is still the right shape because Lane 2 enforces strict substring validation on assistant text and is asking a specifically-assistant-side question: which mental models the assistant's reasoning instantiated.) Evidence-substring validation enforces that fingerprint reasoning moves and verification evidence quotes are literal substrings of the assistant's actual turns; user-turn quotes and extractor-paraphrase quotes are rejected. Keyword recall (deterministic, not LLM-based) reads joined assistant text to stay consistent with the audit target. Lane 2 consumes Lane 1's `selected_model_ids` (anti-echo) but does not drive Lane 1/3/4.

**Lane 2 — design intent: a lens, not a verdict.** Lane 2 reverse-engineers the assistant's reasoning into a curated description language: *which of the 222 mental models structurally describe what this reasoning is doing?* The verifier accepts approximately, not precisely — by design. Two layers absorb the imprecision:

1. **The graph.** Each accepted anchor pulls a neighbourhood of connected curated knowledge — failure modes, premortem questions, allies, antagonists — via Wave 2 + Wave 3 traversal. Even when the anchor is approximately right rather than perfectly right, the neighbourhood the user receives is structurally relevant (the failure modes, premortems, and antagonists of an adjacent-but-real model are still out-of-distribution knowledge the LLM doesn't have natively).
2. **Step 6's three-treatment vocabulary** (defined below). Anchors with direct, specific evidence become *primary pressure*. Anchors with weaker, broader, or competing evidence become *secondary lens*. Anchors the reviser reads as not load-bearing are *set aside with a reason*. The grading is downstream; the verifier doesn't need to be the grader.

Multi-run stability investigations (`research/stability-runs/lane2-stability-experiments-2026-04-27/`, including baseline evidence in `e6-baseline-runs.json` and cross-case evidence in `e6-baseline-crosscase-runs.json`) extended the earlier-cited finding: verifier acceptance varies with backing-model behaviour and fingerprint phrasing, with bounded but real cross-run variance (typical pairwise Jaccard 0.6–0.8) and per-anchor surfacing rates that shift across sessions independent of prompt content. The product contract therefore treats Lane 2's job as *delivering a useful lens*, not *delivering a precise verdict*.

Two harness affordances support this design (PR #58):

- **`is_malformed_verifier_response(raw_payload)`** in `companion_routing.py` distinguishes schema-incomplete output from deliberate empty rejection. Returns `True` when the raw payload is non-dict, is `{}`, or is a dict whose `accepted` and `rejected` fields are both missing or non-list. Returns `False` for any deliberate empty-list response (`{"accepted": [], "rejected": []}` or `{"accepted": []}` alone). Future E6-style ablation tests use this helper to compute `malformed_runs_count` per slate; production runs do not currently call it but it remains available as a diagnostic surface.
- **`BoundaryCallMetadata` extended fields** — `finish_reason`, `raw_message_content`, `temperature` — are populated on the success path of `OpenAICompatibleBoundaryClient.run_json_with_metadata`. Diagnostic scripts read these via `client.last_call_metadata`. They are NOT yet aggregated into `audit_summary.boundary_summary` (which still carries `providers` + `models` + token totals only); extending `BoundaryCallTrace` to expose the new fields per-call is a separate observability improvement and is not load-bearing for the current product contract.

The model identifier IS persisted to every product run: `audit_summary.boundary_summary.models` is a deduplicated list of every backing model used in the run (verified live: e.g. `["x-ai/grok-4.1-fast"]` on a recent archive). This is the lightweight version of "pin the model and re-baseline" — future feedback can be attributed to specific backing-model routes without paying the cost of pinning.

**When further Lane 2 work is justified — the four valid triggers:**

1. **User-visible failures Step 6 cannot absorb.** A confidently-wrong anchor surfaced by Lane 2 and given assertive primary-pressure framing in Step 6 that confuses or misleads a real user reading their own conversation. Reproducible from a `run_id`.
2. **Output-contract integrity.** Malformed verifier outputs (`{}` or schema-incomplete responses) detectable via `is_malformed_verifier_response`. The harness fix from PR #58 makes these visible; if the rate spikes, the lens is silently disappearing.
3. **Curated-knowledge corrections.** A KG entry's `select_when` markers, `danger_when` markers, or `failure_modes` are genuinely too broad or wrong. The Track 2 tightening of Checklists `select_when` bullet 4 (`data/knowledge_graph.json:20486` — required recurrence in a multi-step process across instances rather than "any complex multi-step task") is the canonical example.
4. **Cross-lane interaction bugs.** Lane 1's anti-echo silently dropping good Lane 2 anchors, Lane 3's reframing using a model Lane 2 should have surfaced, anti-echo masking a recurring failure pattern, etc. These show up as redundancy or as silent absence rather than as wrong content.

**When Lane 2 work is NOT justified:** chasing audit-precision metrics through prompt tuning when the existing acceptance pattern produces useful enrichment most of the time. The 2026-04-27 Track 1 v1 prompt restructure attempted exactly this path — five new prompt blocks added at once, targeting an audit-defined noisy_anchor_rate residual — and induced 80% schema-incomplete output (`research/stability-runs/lane2-stability-experiments-2026-04-27/e6-prompt-test-residual.md`). That experiment is the canonical example of why precision-chasing in this lane misreads the design. The pre-registered stop-rule fired (catastrophic Jaccard + friction-yield collapse) and the prompt was rolled back; the harness instrumentation that detected the regression (PR #58) is the one piece of that cycle that's now load-bearing for any future v2.x attempt.

**Lane 3 — Frame Pressure (2 OpenRouter calls):**

1. **Frame extraction:** One OpenRouter call reads the user's source turns for embedded assumptions, mutable constraints, and suppressed counterfactuals. Returns 0-5 frame elements. **Validation:** Elements with empty `evidence_quote` or `frame_pattern` are rejected before routing — the extraction LLM sometimes produces structurally incomplete elements. Dropped elements and their drop reasons (`missing_evidence`, `missing_pattern`) are tracked in `dropped_frame_elements` on the FramePressureCard for observability.

2. **Deterministic routing:** Each frame element's `frame_pattern` is looked up in the Wave 5 reframing routing table → candidate models.

3. **Reframing generation:** One OpenRouter call generates up to 2 alternative questions that open new reasoning paths, grounded in specific mental models.

4. **Anti-echo:** Models already used in Lane 1 are excluded. Overlap between frame patterns and Lane 1 pressure concepts is flagged.

Lane 3 is most powerful on short conversations where the question itself constrains the answer space. A question that assumes "we must grow" and never explores "should we grow?" is a frame pressure finding.

**Lane 3 prompt structure.** Extraction uses `run_frame_extraction_from_packet` (Phase 4c). The user-prompt body is split into a `CONTEXT` section (extractor summaries + assistant replies, NOT quotable as evidence) and a `SOURCE` section (raw user turns). `evidence_quote` validation requires a literal substring of a user turn. Reframe generation still calls `generate_reframings_from_context` directly (a remaining context-driven entry point inside lane logic, not a dispatch fallback) — it's a candidate for migration in a future cleanup phase but harmless because reframe input is the user-stated framing, not extractor paraphrase.

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

   The prompt enumerates ALL 15 catalog dimensions per run (PR 4 of the 2026-04-28 visibility roadmap). Each dimension is marked `present: true` (structurally implicated by the question, with `covered` + `coverage_evidence` + `materiality_note`) or `present: false` (not implicated, with a `presence_reason` specific to the conversation). Pre-PR-4 the LLM returned only the 6-10 it judged present; the other 5-9 were silently absent. Now `audit_summary.dimensions[]` carries all 15 with their reasons, closing the largest visibility gap in Lane 4. The `_MAX_GAPS=5` cap operates only on `present:true AND covered:false`; non-detected dimensions don't consume the budget.

3. **Deterministic routing**: For each uncovered dimension, the deterministic middle looks up candidate mental models from the Wave 6 structural coverage routing table in the knowledge graph (82 model bridges across 74 unique models). Anti-echo exclusion removes models already surfaced by Lanes 1, 2, and 3 — the broadest anti-echo scope of any lane.

4. **Gap question generation** (LLM call 3, conditional): For each gap dimension with routed models, one OpenRouter call generates 2-3 discovery questions following the 5Ws+H framework — concrete questions first (who, what, where, when), reflective last (why). Questions are problem-specific, plain language, and answerable only by the decision-maker from their knowledge of the situation. This call **only fires when gaps exist** — zero gaps means no LLM call, no questions. These gap questions are the HITL (Human-In-The-Loop) bridge: they are never answered by an AI.

5. **Card assembly** (deterministic): Assemble detected dimensions, gap routes, gap questions, and anti-echo metadata into a StructuralCoverageCard.

**Lane 4 prompt structure.** Question classification, dimension detection, and gap question generation use `run_structural_coverage_from_ir` (Phase 4b) — the orchestrator builds a `Lane4Packet` from the IR and dispatches to the `_from_packet` formatters internally. User-prompt bodies follow the same CONTEXT (extractor summaries, NOT citable) / SOURCE (raw conversation turns) split as Lane 3. For detection specifically, SOURCE contains both user and assistant turns — detect_when conditions read user turns (the question), coverage assessments read assistant turns (the answer). Lane 4 has no evidence-substring validation downstream (unlike Lane 3), so the CONTEXT/SOURCE split is prompt guidance not a mechanical gate; the architectural effect shows up as `coverage_evidence` citations attributed to the assistant's actual replies ("Assistant mentions...", "Assistant proposes...") instead of extractor-paraphrased summaries.

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

**Total OpenRouter calls:** Typically 18-25 (1 extraction + 6 Pass 1 cluster triage calls + N deep checks + 1 fingerprint + 1 verify + 1 frame extract + 1 reframe + 1 question classification + 1 dimension detection + 0-1 gap questions, plus an extraction retry if quote fabrication is detected). All use the calibrated boundary client with `temperature=0.2` and `response_format=json_object`. The revision step is skipped in the skill flow — Claude produces the updated position itself in Step 6, using the full conversation context and the four cards.

**Pipeline diagnostics (`run_health`):** The pipeline output includes a decomposed health status that rolls up capture diagnostics from extraction and pipeline state into one truthful object:

- `overall` — `healthy`, `degraded`, or `critical`
- `capture` — `good`, `degraded`, `critical`, or `unknown` (from extraction's `capture_health`)
- `substrate` — `ok` if compiled chunks loaded, `empty` if bundle selector failed
- `embeddings` — `active` or `off`
- `fingerprint` — `ok` if companion verified at least one model, `empty` otherwise
- `findings_produced` — whether Lane 1 produced any findings
- `issues` — array naming what's wrong: `substrate_empty`, `embeddings_off`, `no_fingerprint`, `pipeline_warnings`, `capture_degraded`, `capture_critical`, `quote_fabrication`, `capture_truncated`, `lane3_all_dropped`
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

After Step 4 chat, Claude continues into the reasoning + persistence + pressure-check arc (Steps 6–8b) before opening the Observatory in Step 9 and archiving in Step 10. The full lifecycle is documented in `SKILL.md`; the steps below summarize each stage's product role.

### Step 5: Observatory Placeholder (deferred)

Step 5 in the SKILL flow is intentionally a no-op. The Observatory is *not* offered here — it is deferred to Step 9 so the launched view contains the complete artifact set (cards + revised answer + pressure check + memo). Offering Observatory mid-cycle would show an incomplete run.

### Step 6: Update Your Position (Claude reconsiders)

After presenting findings, Claude reconsiders its earlier advice. The structure is deliberate: first, what survived (what Claude would say again unchanged); then, what to set aside (findings Claude considered and chose not to act on, with specific reasons); finally, what actually shifted. This three-part structure forces genuine reconsideration rather than performative hedging.

**Anchors are evidence-bearing hypotheses, not canonical diagnoses.** Lane 2 surfaces curated mental models that may explain the assistant's reasoning structure, but per-candidate verifier judgment is probabilistic — multi-run stability investigations (research/lane2-architecture-research-frozen-2026-04-26 + research/stability-runs/lane2-pathD-proxy-validation-2026-04-26) confirmed there is no single deterministic substrate fact that predicts cross-run anchor stability above usable thresholds. The product contract therefore treats each anchor as an evidence-bearing hypothesis Step 6 should weigh, not as a canonical fact Step 6 must repeat.

An **anchor-naming invariant** constrains the reconsideration: every anchor in `companion_cheat_sheet.anchors[]` is routed through §1 (its pressure was already priced into the original advice), §2 (considered and set aside with a specific reason), or §3 (drove a change). No anchor is silently skipped. When Claude names an anchor, it uses the `display_name` verbatim — specificity is the point. This rule extends Lane 2's curated substrate from "enrichment the reviser may use" to "enrichment the reviser must account for," closing the anchor-dropout regression observed in earlier runs.

The invariant is now paired with a **three-treatment vocabulary** (`SKILL.md` Step 6 *Anchor treatment*) that decouples "addressed" from "presented as canonical":
- **Primary pressure** for anchors with direct, specific evidence on a load-bearing reasoning move (stronger framing inside §1 or §3).
- **Secondary lens** for anchors with weaker, broader, or competing evidence (softer framing — *"a related lens"*, *"a possible second read"*).
- **"Set aside with a reason"** for anchors the pipeline surfaced but Step 6 reads as not load-bearing (acknowledged in §2 with explicit reason; not silently dropped).

A structural rule pairs with the vocabulary: **one primary-pressure anchor per reasoning move**. When two anchors describe the same move or evidence quote, the most specific / load-bearing anchor gets primary treatment; the others — even if their evidence is direct — become secondary lenses or are set aside with a reason. Treating two anchors as equally primary on the same move is overclaim by structure.

Claude integrates anchors into the §1/§2/§3 reasoning where each one earns its mention — never as a mechanical anchor-by-anchor parade — with rhetorical strength matching the evidence the anchor carries. Some will connect sharply, some won't, and both outcomes are honest. The updated position IS the product.

**Timing detail:** Before writing Step 6, Claude *also* fires off Step 7's pressure-check sub-agents in the background (parallel Agent calls per non-empty lane). They run while Step 6 / 6b are written, so their outputs are ready by Step 8.

### Step 6b: Persist Revised Answer

The Step 6 reconsideration text is written into the result JSON via a small inline Python merge that sets `revised_answer`, `revised_answer_source: "claude_step6"`, `revised_answer_present: true`, and `revised_answer_written_at`. Without this step the Observatory would render an incomplete run (four cards but no revised answer). The persisted revised answer is the first-class artifact downstream tooling reads.

### Step 6c: Generate Memo

```bash
python3 $SKILL_DIR/scripts/render_memo.py \
  --result /tmp/lolla_{run_id}_result.json \
  --output /tmp/lolla_{run_id}_memo.md
```

Deterministic template rendering — no API calls, no LLM. Produces a portable markdown document with up to 8 sections, each with guard clauses so the memo degrades gracefully when optional data is absent:

1. **Heading** — decision context truncated to first 2 sentences
2. **Key Findings** — from `delta_card.findings`, sorted by severity (high → medium → low), with passage deduplication (same passage blockquote rendered only once even if multiple findings reference it)
3. **Mental Model Connections** — from `companion_cheat_sheet.anchors` with presence mode
4. **Frame Alternatives** — from `frame_pressure_card.reframings`
5. **Structural Gaps** — from `structural_coverage_card.gap_questions` with dimension names
6. **Delivery Check** — from `bullshit_profile.summary` when detections exist, naming count and dominant subtype
7. **Updated Position** — `revised_answer` rendered as-is
8. **Pressure Check** — from `gap_check.lanes`, only lanes with divergences, with card names translated to human labels

The memo is the shareable artifact — it can be emailed, pasted into a doc, or read without the Observatory. The Pressure Check section depends on Step 8b having persisted `gap_check`; on weaker orchestrators that skip Step 7/8/8b it simply degrades to absent.

### Step 7: Pressure-Check Sub-Agents

Up to 4 Agent sub-agents (one per non-empty lane) are spawned in parallel via the Agent tool **in the background** (`run_in_background: true`), launched *before* Claude writes Step 6. Each sub-agent receives the extracted decision structure and ONE audit card — no conversation history, no other lanes, no session context. They read the position cold and assess what should shift.

**Why this exists.** The system's own thesis says "an LLM auditing its own reasoning is sampling from the same distribution that produced the flaw." Steps 1–4 honor this — Grok does the detection. But Step 6 asks Claude to reconsider advice it argued for in this conversation. Sub-agents break that loop: same model class as the orchestrator (Opus), but in a clean context that never argued the position.

**Skip conditions.** A lane's sub-agent is skipped when its card is empty:
- Lane 1: `delta_card.top_findings` empty/null
- Lane 2: `companion_cheat_sheet.anchors` empty/null
- Lane 3: both `frame_pressure_card.frame_elements` AND `reframings` empty/null
- Lane 4: `structural_coverage_card.dimensions` empty/null OR every dimension has `covered: true`

A sub-agent that times out or errors is logged as `skipped_error`; it does not block Step 8.

### Step 8: Pressure-Check Comparison

After Step 6, Step 6b, and all sub-agent results are in, Claude compares its Step 6 reconsideration against each sub-agent's output by asking three questions:

1. Did the sub-agent identify a shift I dismissed or minimized in Step 6?
2. Did the sub-agent treat a finding as material that I treated as noise?
3. Did the sub-agent connect a finding to the position in a way I didn't?

Only "yes" answers get reported, under a `### Pressure Check` heading after the Step 6 updated position. If all sub-agents aligned, a single line is rendered ("Pressure check: a fresh look aligned with the assessment above."). The user never hears about the sub-agent machinery — divergences are attributed to the *argument*, not its source. Claude is also expected to cross-check Step 6 against the `bullshit_profile` to confirm it didn't reproduce the patterns the BI flagged in the original.

### Step 8b: Persist Pressure Check

Two artifacts are persisted into `result.json`: a human-readable summary string (`gap_check_summary`), and a structured per-lane object (`gap_check`) with one entry per lane recording `lane_number`, `lane_name`, `status` (`completed` / `skipped_empty` / `skipped_error`), and a `divergences[]` array (each tagged with the question that surfaced it). The Observatory's Pressure Check view and the memo's Pressure Check section both consume the structured object. Without this step the run is observable only as far as Step 6b — the pressure-check loop disappears.

### Step 9: Open Observatory

After the full cycle is complete (cards, updated position, pressure check, and memo all persisted), the Observatory is launched.

```bash
python3 $SKILL_DIR/observatory/serve_result.py --result /tmp/lolla_{run_id}_result.json
```

Zero dependencies (stdlib Python server + pre-built Svelte frontend). The backend API serves:

**Primary product:**
- Case focus and assistant audit target (expandable drawers)
- DeltaCard — findings with severity, passages, challenges, reversal triggers
- CompanionCheatSheet — model anchors with presence badges (EXECUTED/VIOLATED), evidence quotes, presence explanations, and typed chunks (failure modes, premortems, antagonists, heuristics, identity)
- FramePressureCard — frame elements with reframings
- StructuralCoverageCard — gap dimensions with discovery questions
- Revised answer with source provenance badge (`claude_step6`)
- Pressure Check — per-lane divergences from `gap_check`

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

### Step 10: Archive Run

After launching the Observatory, the skill archives the run's core artifacts into a persistent case folder under `~/.local/share/lolla/runs/` (or `$LOLLA_ARCHIVE_DIR`) so the run survives `/tmp` cleanup and stays accessible for later review, memo re-rendering, or `scripts/stability_check.py` analysis. `scripts/archive_run.py` copies 7 files (`conversation.txt`, `extraction.json`, `result.json`, `revised.txt`, `memo.md`, `gapcheck.txt`, `gapcheck_lanes.json`) into `{archive_root}/{case_id}/{run_id}/`. Missing artifacts (e.g. on a weaker orchestrator that skipped Step 6b/8b) are skipped gracefully. `/tmp` originals are not touched.

The "which case is this?" question is solved without asking the user: the archive computes a **case fingerprint** from `extraction.decision_situation` (first 120 chars, normalized — lowercased, punctuation stripped, whitespace collapsed) and matches it against fingerprints stored in `{case_folder}/.case-manifest.json`:

1. **Exact match:** the new fingerprint is already in a case's manifest → file there.
2. **Fuzzy match (token-set Jaccard ≥ 0.80):** handles extractor paraphrase drift. Same conversation re-extracted twice may produce slightly different decision_situation text; the token-set match still groups them into one case. The new fingerprint is added to the manifest as an alias so future exact-match lookups are O(1).
3. **No match:** a new case folder is created. The folder name is auto-slugged from the first 3-4 significant words of `decision_situation` (e.g., `grant-equity-partnership-status`). Users can rename freely — matching is against the in-folder manifest, not the folder name.

Escape hatches:

- `$LOLLA_CASE_ID` — force a specific folder name, skipping fingerprint match. Useful when grouping a run with an existing case despite mismatched decision_situation, or when the user wants a clean folder name from the first run.
- `$LOLLA_ARCHIVE_DIR` — override the archive root.
- The manifest is a plain JSON file editable by hand (rename the `case_id`, merge fingerprints, adjust the `runs[]` list after manual moves).

Orchestrator scratch files (`preamble.json`, `lane*.json`) are intentionally NOT archived — they are Claude-side working files regenerable from `result.json` if ever needed, and they may or may not exist depending on how the orchestrator staged Step 7 sub-agents.

### Bullshit Index — Fact Registry (cross-cutting feature)

The Bullshit Index (adapted from Hannigan et al., 2025) is not a separate step; it runs inside the pipeline (Step 3) and is consumed by Steps 4 / 6 / 8 / 6c. It evaluates the assistant audit target for four subtypes of bullshit: empty rhetoric, paltering, weasel words, and unverified claims. In normal file-based runs, that target is derived from joined assistant turns in `ConversationContext`; legacy `vanilla_answer` fields are fallback-only. To reduce false positives on unverified claims, the BI judge receives a **fact registry** — a structured summary of what the user established in conversation.

The fact registry extracts `decision_situation`, `live_constraints`, and `dropped_threads` from the extraction JSON into a compact context block (~1500 chars vs. the previous 4000-char raw conversation truncation). The `_CONTEXT_BLOCK` instructs the judge that claims referencing, restating, paraphrasing, or drawing reasonable inferences from user-stated facts are grounded — only claims introducing information the user never provided should be flagged.

This structured approach gives the judge a cleaner signal about what counts as established context, reducing over-flagging of claims that are grounded in conversational facts.

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

- **Pass 1 can miss tendencies.** The old 25-in-one prompt is gone; six family-clustered specialists reduce load and improve stability, but each cluster is still probabilistic semantic triage. Adjacent tendencies can still be confused. Embedding swiss cheese partially addresses this.
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
| `data/knowledge_graph.json` | 3.0M | 222 models, 25 tendencies, 241 antidote bindings, 1,742 edges, 15 prerequisite edges, 15-dimension structural coverage routing, 15 reframing patterns |
| `data/relationship_graph.json` | 1.2M | 1,358 relationship edges (allies, antagonists, tensions) |
| `data/embeddings.db` | 42M | Pre-computed vectors (text-embedding-3-large, 3072d): 2,032 chunk_embeddings + 444 model_signals + 25 tendency_guidance + 867 edge_activation_conditions (~3,368 total) |
| `data/curation/` | 222 model files (+ subdirs) | Wave 1 activation semantics per model |
| `data/curation/intervention_semantics/` | 222 files | Wave 2 failure modes, heuristics, premortems |
| `data/curation/relation_semantics/` | 222 files | Wave 3 relationship edge data |
| `data/curated/subpattern_catalog.json` | 276K | Sub-pattern definitions for deep checks |
| `data/curated/compiled_chunks.json` | 199K | Pre-compiled knowledge chunks for bundle selection |
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
| OpenRouter times out | Boundary client returns empty payload + a degraded `BoundaryCallMetadata` (status `timeout` / `http_error_*` / `url_error` / `response_json_error`). No internal retry loop. The pipeline degrades — affected lanes return empty/partial results, the run continues, and the failure is visible in `audit_summary.boundary_calls[]`. The only application-level retry is extraction's single quote-fabrication retry (see *Capture validation* in Step 2). |
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

The Bullshit Index runs one OpenRouter call per passage of the audited answer (typically 30-60 calls in parallel). On a long answer this can dominate the OpenRouter call count. It runs in `_run_bullshit_index` after the lanes complete and is recorded under `stage="bullshit_index"` in the per-run telemetry.

The Step-7 pressure-check sub-agents fire from inside the SKILL via Claude Code's Agent tool, *not* through the OpenRouter boundary client. They run on whatever Claude model the orchestrator inherits (typically Opus). On most runs this is the dominant cost line. Their `total_tokens` (no prompt/completion split available) is recorded into the same `usage_summary` block by Step 8b.

The cost bump compared to earlier versions is load-reduction working as designed. Pass 1 was previously a single monolithic call scoring all 25 tendencies under ~11 confusion guardrails; it is now six family-clustered specialists (3-5 tendencies each, family-relevant guardrails only). The trade-off is more calls for narrower per-call load — and measured Pass 1 stability moved from 0.50 → 0.70 Jaccard on a fixed Marcus extraction as a result.

**Per-run telemetry** lives in the `usage_summary` block of the result JSON. See **[docs/cost-and-telemetry.md](docs/cost-and-telemetry.md)** for the canonical reference: what's measured, where it's stored, how to verify it, how to bump prices, and how to add a new vendor or stage. The Observatory's `/usage` page renders the same data visually.

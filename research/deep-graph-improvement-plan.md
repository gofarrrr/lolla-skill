# Deep Graph Improvement Plan

Research date: 2026-04-14  
Status: Planning only — no code changes

---

## The Real Problem (Not What We Thought)

The initial audit identified "single-hop traversal" as the main bottleneck. After reading 12 canonical articles and analyzing the full data pipeline, the real problem is more fundamental:

**The graph is flat where it should be rich.**

### The Affinity Problem

The most striking finding: `composition_affinity` is effectively a constant per edge type:

| Edge Type | Count | Affinity Values |
|-----------|-------|----------------|
| ally | 523 | 516 at 0.90, 7 at 0.75 |
| antagonist | 344 | 330 at 0.25, 14 at 0.22 |
| tension | 491 | 491 at 0.25 |

**Every ally is equally allied. Every antagonist equally opposes. Every tension is equally tense.**

When `neighborhood()` sorts by `composition_affinity` to select the top-2 supporting models, it's sorting a list where 98.7% of values are identical (0.90). The actual selection falls through to the lexical tie-breaker (`model_id` alphabetically). This means the system is picking supporting models **alphabetically**, not by relevance.

### The Hub Problem

The top-10 nodes by degree:
```
confirmation-bias:    233 edges
systems-thinking:     ~60 edges  
commitment-bias:      ~50 edges
first-principles:     ~45 edges
...
```

`confirmation-bias` has 233 edges — it's connected to virtually everything. When it appears as an antagonist (119 times!) or tension (105 times), it dominates risk model selection for almost any seed. The system's "risk model" output is disproportionately "confirmation-bias" regardless of what tendency was detected.

### What The Canonical Articles Actually Contain

Every single one of the 222 articles has a consistent, rich structure:

1. **Core Principles** — the model's fundamental essence
2. **Playbook** — concrete heuristics, frameworks, examples
3. **Strengths** — when to use ("most useful when", "works best when", "best used when")
4. **Weaknesses** — anti-patterns, limitations ("danger when")
5. **Latticework** — named allies with *why they're synergistic* + named antagonists with *why they conflict*
6. **Structured Tension** — curated model-vs-model conflicts with *specific activation conditions*
7. **Risks & Mitigations** — failure modes with premortems

**What we currently extract:**
- `select_when` / `danger_when` (from Strengths/Weaknesses)
- `failure_modes` with `mitigation` (from Risks)
- `premortem_questions` (from Risks)
- `heuristics` (from Playbook)
- Ally/antagonist/tension edges (from Latticework + Structured Tension)

**What we DON'T extract but is sitting right there in every article:**

1. **WHY each ally is an ally** — every Latticework section explains the synergy mechanism. Example from Survivorship Bias: "The most powerful tool for fighting survivorship bias is adopting the outside view. Survivorship bias thrives on base-rate neglect." This is the interaction logic — it tells you *when* the ally relationship activates and *how* the models compound. We flatten this to a single `source_description` string on the edge and `composition_affinity=0.90`.

2. **WHY each antagonist conflicts** — every article explains the conflict mechanism. Example: "Confirmation bias causes people to seek out information that confirms preexisting beliefs. If the belief is 'successful companies do X,' survivorship bias ensures the user confirms this by only looking at companies that survived doing X." This is a *directional interaction pattern* — it describes how one model amplifies another's failure mode.

3. **Concrete examples of model interactions** — many Latticework tables include a third column with specific business/strategy examples of how the ally/antagonist relationship plays out in practice. We don't extract these at all.

4. **Input/output type semantics** — each curation JSON has `input_type` and `output_type` (e.g., "hidden-denominator evidence problem" → "denominator-aware outside view"). These describe *what cognitive material the model operates on* and *what it produces*. This is the foundation for dependency-chain detection: if Model A's output type matches Model B's input type, there's a functional dependency. We store these fields but never use them for routing or selection.

5. **Reasoning type tags** — each model has `reasoning_types` (e.g., ["probabilistic", "diagnostic"]). These could cluster models by cognitive operation type but aren't used in any selection logic.

6. **The "when" conditions in Latticework synergies** — ally descriptions often include activation conditions: "Together they explain why formal authority often loses to the actor controlling the real outside option." This tells you the ally pair activates *specifically when formal vs real authority is in play*, not generically.

7. **Anti-pattern descriptions** — every article has specific anti-patterns ("Danger when teams invoke survivorship bias abstractly but still use samples that exclude the hidden denominator"). These are *misuse signatures* — they describe what it looks like when the model is being applied incorrectly. We don't extract these separately from `danger_when`.

---

## The Three Layers of Improvement

### Layer 1: Differentiate Edge Weights (Fix the flat graph)

**Problem:** 98.7% of ally edges have identical affinity. Selection is effectively random.

**Solution approaches (from simple to sophisticated):**

**1a. Extract interaction-strength signals from the canonical articles.**

The Latticework sections in every article describe WHY each ally/antagonist relationship exists. These descriptions vary enormously in specificity and strength:

- STRONG: "The most powerful tool for fighting survivorship bias is adopting the outside view" (survivorship-bias → base-rates)
- MODERATE: "Systems thinking requires understanding how interconnected parts influence each other" (optimism-bias → systems-thinking)
- WEAK: "Using a team is a highly effective way to gain higher objectivity" (survivorship-bias → team-processes)

A one-time re-curation pass could assign 3-5 differentiated affinity levels based on the language strength in the Latticework descriptions. This doesn't require any new data — just reading what's already there with a finer lens.

**1b. Use input_type/output_type for functional edge weighting.**

If Model A's `output_type` matches or overlaps with Model B's `input_type`, that's a functional dependency — stronger than a generic ally relationship. Example: if "pre-mortem-analysis" outputs "scenario-based risk assessment" and "monte-carlo-methods" inputs "probabilistic scenario framework", there's a functional chain. The GoS repo's `_schema_overlap_score()` shows exactly how to compute this from typed I/O signatures.

This creates a new edge type: `functional_dependency` — weighted higher than generic ally because it describes *operational chaining*, not just conceptual kinship.

**1c. Use reasoning_types for type-coherent weighting.**

Two models that share `reasoning_types` (both "probabilistic") have a different kind of affinity than two models from different reasoning types. A "probabilistic" model supporting another "probabilistic" model reinforces the same cognitive operation. A "diagnostic" model supporting a "probabilistic" model bridges cognitive operations — potentially more valuable for coverage but less for depth.

### Layer 2: Multi-Hop Traversal with Fan Correction (Fix the hub problem)

**Problem:** `confirmation-bias` (233 edges) dominates risk model selection for every seed.

**Solution: Spreading activation with fan effect.**

The Collins & Loftus spreading activation model with ACT-R's fan correction is the right fit because:

1. It's cognitively aligned — we're literally modeling how mental models activate each other in reasoning
2. The fan effect (`strength = S - ln(fan)`) naturally dampens hub nodes: confirmation-bias spreads 1/(1+ln(233)) = 0.15 of its activation per edge, while a focused model with 4 edges spreads 1/(1+ln(4)) = 0.42 per edge
3. Negative activation through antagonist edges models inhibition — "this model pushes against that one"
4. Decay controls reach — for a 222-node graph with mean degree 12.2, exponential decay at λ=0.7 reaches 2-3 hops before fading below threshold, which is the right range

**Implementation sketch (not code — thinking):**

```
Given: seed_model_ids (from tendency routing)
       edge_graph (from relationship_graph.json)
       
1. Initialize activation:
   activation[seed] = 1.0 for each seed
   all others = 0.0

2. For each iteration (max 3-4):
   For each active node (activation > threshold):
     For each edge from this node:
       fan_count = len(edges_from_neighbor)
       fan_adjustment = 1.0 / (1.0 + log(fan_count))
       
       if edge_type == "ally":
         weight = composition_affinity * fan_adjustment
       elif edge_type == "antagonist":
         weight = -composition_affinity * fan_adjustment * 0.5
       elif edge_type == "tension":
         weight = composition_affinity * fan_adjustment * 0.3  # positive but flagged
       
       activation[neighbor] += activation[node] * weight * decay
   
   Clamp all activations to [-1.0, 1.0]

3. Result:
   supporting_models = top-k by positive activation (excluding seeds)
   risk_models = top-k by negative activation (most negative = most opposing)
```

**Why this beats PPR for our use case:**
- PPR can't handle negative edges natively (antagonist/tension)
- Spreading activation with decay is more interpretable — you can trace exactly which path activated each model
- The fan correction specifically addresses our hub problem, which PPR doesn't directly solve
- It maps to the cognitive domain we're modeling (mental model activation in reasoning)

### Layer 3: Use the Curated Richness (Fix the extraction gap)

**Problem:** Every canonical article contains ~2,000-5,000 words of structured knowledge. We extract ~200 words per model into `knowledge_graph.json`. The Latticework synergy explanations, the concrete examples of model interactions, the specific anti-pattern descriptions, the activation conditions — all of this is left on the table.

**What we could extract that we currently don't:**

**3a. Interaction activation conditions.**

From every Latticework ally/antagonist table, extract the *when* clause — the condition under which the interaction between two models becomes relevant.

Example from Power Dynamics → Lock In:
> "Lock In explains how commitment changes the future option set; Power Dynamics explains how that narrowed option set shifts bargaining power after the commitment is made."

The activation condition is: "when commitment is changing the future option set." This is not generic — it fires specifically when the conversation involves commitment dynamics.

**This turns edges from static properties into conditional activators.** An edge doesn't just say "A allies with B at 0.90" — it says "A allies with B specifically when commitment dynamics are in play." The routing system could then match detected reasoning patterns against edge activation conditions to select the most contextually relevant supporting models.

**3b. Interaction examples.**

Many articles include concrete examples in their Latticework tables. From Power Dynamics:
> "A buyer keeps leverage before migration, then loses it once retraining and interface debt make exit expensive."

These examples are goldmines for the companion lane. When we detect power-dynamics active in a conversation about a vendor relationship, we could surface *this specific example* as intervention pressure — not generic "power dynamics is relevant" but "here's exactly how this model interacts with lock-in in a vendor scenario."

**3c. Anti-pattern signatures.**

Currently `danger_when` captures when NOT to use a model. But each article also contains anti-patterns that describe what *incorrect application* of the model looks like:

From Checklists: "Danger when checklist completion is mistaken for problem resolution — teams celebrate a clean tick-box process even though the checklist never tested whether the assumptions, environment, or causal story were still true."

This is a detection signature for misuse. If the conversation shows checklist-like reasoning but the fundamental assumptions aren't being tested, we're seeing the anti-pattern in action. This could inform a new detection dimension: not just "is this tendency present?" but "is this model being applied correctly?"

**3d. Typed interaction mechanisms.**

The Latticework descriptions implicitly classify WHY models interact:

- **Amplification:** "Confirmation bias reinforces survivorship bias by selecting supporting evidence" — one model makes another's failure mode worse
- **Correction:** "The outside view is the most powerful tool for fighting survivorship bias" — one model directly counters another
- **Prerequisite:** "Lock In explains how commitment changes the option set" — you need to understand A before B applies
- **Complementary:** "Game Theory models the move-response structure, while Power Dynamics identifies which commitments are credible" — the models cover different aspects of the same situation

These interaction types are more nuanced than ally/antagonist/tension. An ally that amplifies is different from an ally that provides a prerequisite. A tension that creates productive friction is different from an antagonist that directly contradicts.

---

## Concrete Improvement Candidates (Prioritized)

### Tier 1: High Impact, Low Risk

| # | What | Why | Effort |
|---|------|-----|--------|
| 1 | **Fan-adjusted affinity at load time** | Hub nodes stop dominating. Most allies have identical affinity — the only discriminator becomes graph structure (how many edges a neighbor has). A model with 4 edges but 0.90 affinity becomes more valuable than a model with 40 edges at 0.90. | ~5 lines in `RelationGraph.load()` |
| 2 | **Differentiate ally affinities from Latticework language strength** | One-time re-curation. Read each Latticework synergy description and assign 0.70/0.80/0.90/0.95 based on language strength. Turns the flat 0.90 into a useful signal. | Curation effort, no code |
| 3 | **Add confidence/extraction_type to chunk selection sort key** | Fields already loaded, just not in the sort key. `explicit` + `high` confidence chunks should beat `normalized` + `medium` ones. | ~3 lines in `PressureBundleSelector` |
| 4 | **Respect blocking_quality_flags** | If a binding or chunk has blocking flags, skip it. The flags exist for a reason someone already curated. | ~1 conditional |

### Tier 2: Significant Architecture, High Reward

| # | What | Why | Effort |
|---|------|-----|--------|
| 5 | **Spreading activation with fan effect replaces `neighborhood()`** | Multi-hop + hub dampening + negative edges for antagonists. The cognitive model matches the domain. | ~40 lines, numpy |
| 6 | **Extract interaction activation conditions from Latticework** | Turn edges from static to conditional. Enables context-sensitive supporting model selection. | Extraction script + schema change |
| 7 | **Input/output type matching for functional dependency edges** | Creates a new edge type from data we already have. Models whose output feeds another's input are functionally chained — stronger than generic alliance. | ~30 lines analysis + edge generation |
| 8 | **Compound-aware seeding** | When multiple tendencies fire, seed activation from all antidotes simultaneously. Finds models central to the *combination*. | ~10 lines in pipeline |

### Tier 3: Deep Enrichment, Needs Validation

| # | What | Why | Effort |
|---|------|-----|--------|
| 9 | **Extract interaction examples from Latticework tables** | Domain-specific examples of model interactions. High-value for companion lane: surfaces concrete scenarios, not abstract relationships. | Extraction script |
| 10 | **Typed interaction mechanisms** (amplification/correction/prerequisite/complementary) | More nuanced than ally/antagonist. Enables routing logic like "find me a model that CORRECTS this failure" vs "find me a model that COMPLEMENTS this analysis." | Re-curation + schema |
| 11 | **Anti-pattern signature extraction** | Detect when a model is being misapplied, not just when it's present. New detection dimension. | Extraction + detection logic |
| 12 | **Structural balance audit** | One-time validation of the graph. Find curation inconsistencies (friend-of-enemy-is-friend cycles). Fix or flag. | Script |

---

## What The System Doesn't Know About Itself

The deepest limitation isn't algorithmic — it's informational. The canonical articles describe a rich web of conditional, typed, directional interactions between mental models. The current system reduces this to:

```
model_a --ally (0.90)--> model_b
model_a --antagonist (0.25)--> model_c
model_a --tension (0.25)--> model_d
```

The articles actually describe:

```
model_a --ally (when commitment dynamics are in play)--> model_b
         mechanism: B explains how commitment changes the option set;
                    A explains how that narrowed set shifts bargaining power
         example: "A buyer keeps leverage before migration, then loses it 
                   once retraining and interface debt make exit expensive"
         strength: STRONG (described as "the most powerful tool")
```

The gap between what we store and what exists in the source material is where the biggest improvements live. Not in better algorithms over thin data — in extracting richer data that makes even simple algorithms work better.

**The graph doesn't need to be smarter. It needs to know what it already has.**

---

## Relationship to the Previous Audit

The `research/graph-improvement-audit.md` correctly identified:
- Single-hop traversal as a bottleneck (confirmed, but secondary)
- PPR as a technique (valid, but spreading activation is better fit for signed edges)
- Fan effect as highest-impact smallest change (confirmed — now we know WHY: the affinity values are flat)
- Quality metadata being unused (confirmed — blocking flags, confidence, extraction type all loaded but ignored)

What the previous audit missed:
- The affinity values are effectively constant per edge type (the whole sorting mechanism is a no-op)
- The canonical articles contain 10x more interaction detail than we extract
- The interaction conditions (when an ally relationship activates) are the most valuable un-extracted signal
- Input/output type matching could create a new class of functional dependency edges from existing data
- The hub problem is worse than expected (confirmation-bias at 233 edges vs mean 12.2)

---

## Next Steps (When Ready to Execute)

1. **Validate the alphabetical selection hypothesis.** Run the pipeline on 3-5 test conversations and check whether the supporting/risk model selections correlate with alphabetical order within the ally/antagonist pools. If confirmed, the flat-affinity problem is actively degrading output quality.

2. **Prototype fan-adjusted affinity.** Apply `affinity * 1/(1+ln(degree))` at load time and re-run the same test conversations. Measure whether supporting model diversity improves.

3. **Audit 10 Latticework sections for interaction strength variation.** Manually score the synergy/conflict descriptions as STRONG/MODERATE/WEAK. If inter-article variation is large (it appears to be from the sample), differentiated affinities are justified.

4. **Prototype input/output type overlap detection.** Run `_schema_overlap_score()` (from GoS) over all 222 models' input_type/output_type pairs. See if meaningful functional chains emerge.

5. **Prototype spreading activation on the existing graph.** Seed from one tendency's antidote models, run 3 iterations with fan correction and decay=0.7. Compare top-10 activated models against current `neighborhood()` output. If the sets differ meaningfully, the algorithmic improvement is validated.

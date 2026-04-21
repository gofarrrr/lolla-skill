# Deep Graph Enrichment — Session Handover

Research date: 2026-04-16
Last updated: 2026-04-16
Status: **Layer 1+2 enrichment COMPLETE (222/222). Fan correction LIVE. SPARSE recovery REJECTED. Layer 3 scope RECONSIDERED (2026-04-16). Activation/Rationale wiring rollout PLANNED (2026-04-21, see Section 14 — phased, fixture-tested, doctrine-enforced).**

---

## 0. CURRENT STATE — READ THIS FIRST

**Layers 1+2 are done. The graph is no longer flat. Fan correction is live in the runtime. SPARSE ally recovery was rejected as a design violation.**

**Section 14 rollout status (2026-04-21):**
- Phase 0 (compiler + loader plumbing) — DONE
- Phase 0.5 (Layer 1+2 doctrine audit) — DONE
- Phase 1 (card rendering of affinity_rationale + activation_condition) — DONE, end-to-end verified
- **Phase 2 (tension enrichment) — SKIPPED (REV-6).** Source audit found all 491 tensions are single-sentence "X conflicts with Y when Z" entries with no richer material behind them in the canonical articles. LLM re-read would synthesize splits the curator never wrote. See Section 14f Phase 2 block for the full finding and the condition under which this decision would flip.
- Phase 3 (near-tie tiebreaker) — NEXT
- Phase 4 (ranking blend) — gated on Phase 3
- Phase 5 (anti-echo suppression) — gated on Phase 3

This section is the authoritative summary. Sections 6-11 below contain the original planning text for context, but this section overrides them where they conflict.

Progress tracker: `lolla-skill/research/layer1-enrichment-progress.md` — shows all 222 models complete.

### 0a. Layer 1+2 enrichment — ALL COMPLETE (222/222)

All 222 mental models have been enriched with differentiated `affinity_strength`, `affinity_rationale`, and `activation_condition` for every curated ally and antagonist edge. This was done in batches of ~8 models using upgrade scripts that programmatically modified the curation JSON files.

**Before enrichment:** 98.7% of ally edges at 0.90 (flat graph). Alphabetical tiebreaker decided model selection.

**After enrichment — affinity distribution across all 523 ally edges:**

| Level | Count | % |
|-------|-------|---|
| 0.95 (CRITICAL) | ~38 | 7.3% |
| 0.90 (STRONG) | ~283 | 54.1% |
| 0.80 (MODERATE) | ~193 | 36.9% |
| 0.70 (SUPPORTIVE) | ~9 | 1.7% |

344 antagonist edges also differentiated with the same 4-level rubric, mapped through `_affinity_strength_to_risk()` for runtime risk scoring.

**How it was done:** Batches of ~8 models per upgrade script. Each script contained a manually curated `upgrades` dict mapping model IDs to their per-edge affinity values and rationales, derived from the canonical articles using the 4-level language-strength rubric. Scripts read each curation JSON, added `affinity_strength`, `affinity_rationale`, and `activation_condition` to each ally/antagonist entry, updated `curation_notes`, and wrote back. Scripts were deleted after verification.

**Pilot results (10 models):** Full data at `lolla-skill/research/layer1-pilot-results.md`. Rubric validated: 4 levels are separable. Same model gets different strengths as ally of different models (e.g., second-order-thinking is 0.95 for premortem but 0.80 for inversion).

Schema updated: `curation/relation_semantics/schema.json` — `affinity_strength` (enum: 0.70/0.80/0.90/0.95), `affinity_rationale` (string), and `activation_condition` (string) added as optional fields on `relationItem`.

### 0b. Pipeline fixes — ALL DONE

**These were blocking at the start of the project — now fully resolved.** Documenting for reference.

The original handover only looked at the JSON schema. The Python code had its own independent validation.

Three files need fixing before ANY compilation can run on the enriched curation files:

**1. Validator rejects unknown fields — `relation_semantics.py:664`**
```python
# CURRENT (will throw RelationSemanticsValidationError on our files):
allowed = {"target_model_id", text_key, "source_quote", "extraction_type", "confidence", "note"}
```
`affinity_strength` and `affinity_rationale` are not in the allowed set. The pipeline will refuse to load every file we've enriched.

**FIX:** Add `"affinity_strength"` and `"affinity_rationale"` to the `allowed` set in `_validate_item_list()` at `Lolla-system-b/system_b/relation_semantics.py:664`.

**2. Loader silently drops our fields — `relation_semantics.py:37-46` and `:629-643`**
```python
# CURRENT: RelationItem has no affinity_strength field
@dataclass(frozen=True)
class RelationItem:
    target_model_id: str
    text: str
    source_quote: str
    extraction_type: str
    confidence: str
    note: str
    tension_type: str
```
`_items_from_payload()` reads only these fields. Even after fixing the validator, `affinity_strength` is silently ignored.

**FIX:** Add `affinity_strength: float` (default `0.0`) and `affinity_rationale: str` (default `""`) to `RelationItem`. Update `_items_from_payload()` to read them from the JSON entry.

**3. Compiler ignores per-edge affinity — `compilation_bundle.py:672-673`**
```python
# CURRENT: derives affinity from confidence alone — THIS is why the graph is flat
def _wave3_confidence_to_ally_affinity(confidence: str) -> float:
    return {"high": 0.9, "medium": 0.75, "weak": 0.65}.get(str(confidence).strip(), 0.72)
```
This is the ROOT CAUSE of the flat graph. Every `confidence: "high"` ally compiles to `0.90` regardless of the relationship's actual strength. **The flat graph is not an extraction failure — it's a compiler design choice.**

**FIX:** At `compilation_bundle.py:737`, where the compiler calls `_wave3_confidence_to_ally_affinity(item.confidence)`, change it to prefer `item.affinity_strength` when present:
```python
composition_affinity=(
    item.affinity_strength
    if item.affinity_strength > 0
    else _wave3_confidence_to_ally_affinity(item.confidence)
),
```
This is backwards-compatible: files without `affinity_strength` still use the confidence-based default. Files with it use the differentiated value.

**ALL THREE FIXES ARE DONE.** The pipeline accepts, loads, and compiles the new fields. Changes made:
- `relation_semantics.py`: `RelationItem` dataclass has `affinity_strength`, `affinity_rationale`, `activation_condition` with defaults. `_items_from_payload()` reads them. `_validate_item_list()` allows them.
- `compilation_bundle.py`: `_affinity_strength_to_risk()` maps 0.95→0.30, 0.90→0.25, 0.80→0.22, 0.70→0.20 for antagonists. Ally compilation uses `item.affinity_strength` directly when > 0. Antagonist compilation maps through `_affinity_strength_to_risk()`.
- `schema.json`: `activation_condition` added as optional string on `relationItem`.

Verified: all 222 records load, pilot files compile with differentiated values, non-pilot files still use confidence-based defaults.

### 0c. SPARSE ally recovery — REJECTED

The original plan (Change 3 below) proposed flagging models with fewer than 3 allies for "sparse ally recovery" — adding allies the curation didn't keep, sourced from mentions in canonical articles.

**This was rejected by the project owner.** Rationale: adding allies that the curation pipeline deliberately dropped is overfitting knowledge extracted from books to the system we built. The curated edges are deliberate choices made with full semantic judgment. Adding more from canonical mentions overrides curator judgment.

**This is part of the broader Closed Vocabulary Principle:** the 222 curated mental models are the ONLY reasoning primitives. Enrichment layers refine existing connections between these models — they never expand the concept space or import new concepts from factual content. Any future enrichment work (Layer 3 interaction types, spreading activation, etc.) must only connect or refine existing models. If a canonical article mentions a concept that isn't one of the 222 models, it gets noted but NOT added to the graph.

Some curation files may still contain `SPARSE_ALLY_RECOVERY:` flags in `curation_notes.open_questions` from the enrichment pass. These are informational artifacts — do NOT act on them.

### 0c-original. What changed from the original Sections 6 and 11 (historical context)

**Change 1: Combined Layer 1 + Layer 2 in a single pass.** — DONE. Both signals live in the same Latticework text. A single read extracts affinity_strength, affinity_rationale, and activation_condition together.

**Change 2: Applied the same rubric to antagonist edges.** — DONE. 344 antagonist edges differentiated.

**Change 3: Sparse-graph ally recovery.** — REJECTED. See 0c above.

**Change 4: Layer 3 (interaction types) remains deferred.** — Still deferred. Requires its own pilot and rubric.

### 0d. Fan correction — DONE (runtime, not load-time)

Fan correction is live in `relation_graph.py` (both `lolla-skill/engine/system_b/` and `Lolla-system-b/system_b/`).

**Design deviation from original handover:** Section 8b below proposed applying fan correction at load time by modifying stored affinities. This was NOT implemented as written because it breaks the `min_supporting_affinity=0.6` threshold — even CRITICAL allies (0.95) of moderate-degree models would drop below 0.6 after dampening.

**What was implemented instead:** Fan correction at **ranking time only**:
- Raw affinities are preserved in the graph (used for threshold filtering in `neighborhood()`)
- Fan-adjusted scores are computed on the fly for candidate ranking
- The adjustment is: `adjusted = raw_affinity / (1 + ln(degree))` where `degree` is total edges (in + out)
- Degree counts are computed once in `__init__()` from the loaded graph

**How it works:**
- `confirmation-bias` (233 edges): its ranking score is multiplied by ~0.155
- A focused model with 4 edges: multiplied by ~0.42
- A model with 1 edge: no dampening (factor = 1.0)

**Key implementation details:**
- `RelationGraph.__init__()` computes `self._degree_counts` — total degree per model
- `_fan_adjusted_affinity(model_id, raw)` applies the dampening formula
- `neighborhood()` uses raw affinity for `min_supporting_affinity` threshold, adjusted affinity for candidate scores
- `_bounded_unique_model_ids()` unchanged — it just sorts whatever scores it gets

**Tests (all pass, `Lolla-system-b/tests/test_relation_graph.py`):**
- `test_fan_correction_dampens_hub_model` — constructs a graph with a hub (degree 5) and focused model (degree 1), same raw affinity, verifies focused model ranks higher
- `test_fan_correction_threshold_uses_raw_affinity` — hub with 50+ edges and raw affinity 0.90 still passes the 0.6 threshold despite adjusted score being ~0.22
- Existing tests updated to expect fan-adjusted ordering

### 0e. Reading order for new sessions

1. This section (0a-0e) — understand what's done and what's left
2. Section 1-5 below — understand the system architecture and the original problem
3. `lolla-skill/engine/system_b/relation_graph.py` — the runtime with fan correction
4. One enriched curation file (e.g., `Lolla-system-b/curation/relation_semantics/inversion.json`) — see the enriched format
5. Section 11 below — the roadmap of what's next

### 0f. What to do next (ordered)

1. ~~**Fix the pipeline**~~ — DONE
2. ~~**Layer 1+2 enrichment (222/222)**~~ — DONE
3. ~~**Fan correction**~~ — DONE (runtime ranking, not load-time mutation)
4. ~~**SPARSE ally recovery**~~ — REJECTED (violates closed vocabulary principle)
5. **Compile and verify end-to-end** — run the compilation pipeline on all 222 enriched curation files, verify differentiated values flow into `relationship_graph.json`, run 3-5 test conversations to confirm supporting model selection is no longer alphabetical and hub models no longer dominate
6. **Layer 3 — RECONSIDERED on 2026-04-16.** See Section 0g below for the revised priority order. The original 4-type taxonomy (amplification/correction/prerequisite/complementary) was scoped before the canonical articles were re-read under the reasoning-about-reasoning lens. Re-reading revealed the 4 types don't separate cleanly in the source prose and that other already-curated signals should be extracted first.
7. **Spreading activation algorithm** — replace `neighborhood()` internals with multi-hop traversal. Originally depended on Layer 3 interaction types; under the revised plan it can instead use activation_condition matching + fan-adjusted weights. The `RouteNeighborhood` interface stays the same.
8. **Input/output type matching** — compute functional dependency edges from existing `input_type`/`output_type` fields. One-time analysis script.
9. **Concrete interaction examples** — extract specific examples from Latticework tables. High value for companion lane. Requires a new chunk type. (Partially subsumed by Section 0g item 5 — shared-example detection.)

### 0g. Layer 3 scope reconsidered (2026-04-16)

**Summary:** After Layer 1+2 landed, 10 canonical articles were re-read under the project's reasoning-about-reasoning principle (the system picks models by reasoning shape, not by topic facts). The re-reading revealed that the original Layer 3 plan — classifying every edge into one of 4 discrete interaction types — would overfit the source, and that higher-value signals already exist in curated article content but aren't fully compiled.

**Articles sampled (random 10 of 222):**

- `User_Centered_Design_rag.md`
- `Trade_Offs_rag.md`
- `Complexity_Bias_Resistance_rag.md`
- `Correlation_Vs_Causation_rag.md`
- `Inversion_rag.md`
- `Systems_Thinking_rag.md`
- `Critical_Thinking_rag.md`
- `Decision_Trees_rag.md`
- `Hanlons_Razor_rag.md`
- `Persistence_Grit_rag.md`

**Finding 1 — The 4 types do not cleanly separate in source prose.**

Articles describe relationships in integrated language that blends types. Example from the sampled articles: "Together they form a complete defensive architecture: diagnose the risk, then build the cushion." This single sentence is simultaneously complementary (the models cover different functions), prerequisite (diagnose before cushion), and amplification (each strengthens the other's effect). Forcing a discrete type label onto prose that was deliberately written as blended would lose information, not add it. The curators wrote integrated descriptions because that's what the relationship is.

**Finding 2 — Structured Tension Curation is already curated with activation conditions, but may not be fully compiled.**

Every sampled article has a "Structured Tension Curation" block with a date (seen: 2026-02-27, 2026-04-03, 2026-04-07) and explicit activation conditions for model-vs-model tensions. This is higher-fidelity than anything Layer 3 would produce, and the compiler may already be handling it — but nobody has audited whether every tension flows into `structured_tensions` with its `activation_condition` intact. Likely a free win.

**Finding 3 — "Most useful when / Danger when" is reasoning-shape language per model.**

Every article has per-model clauses describing when the model's reasoning is useful versus when applying it becomes its own failure mode. Example shape: "useful when diagnosing cascading failures; danger when forcing systemic framing on problems that have a single proximate cause." This is exactly the self-reflexive anti-echo signal the system needs — if the upstream reasoning is already in model X's failure mode, the system must not recommend model X. The language is already there; it needs to be extracted as structured fields, not re-taxonomized.

**Finding 4 — Pre-mortem questions are already curated reasoning probes.**

Articles bind specific pre-mortem questions to specific failure modes (e.g., "What would make this decision look obvious in retrospect?" tied to hindsight bias). These are reasoning-shape probes, not generic questions. Extracting them as a new chunk type bound to failure modes is a grounded extraction, not a new taxonomy.

**Finding 5 — Named examples recur across articles as natural bridge points.**

Southwest Airlines appears in `Trade_Offs`, `Complexity_Bias_Resistance`, and `User_Centered_Design`. RAF Survivorship appears in `Inversion`. Patagonia appears in `Inversion` and elsewhere. These recurrences are latent edges that the curation already sanctioned — detecting them is a one-time text-analysis script, not an article re-read.

**Revised priority order (supersedes Section 0f items 6-7 and Section 11 item 2):**

1. **End-to-end compilation test** (unchanged) — still the critical first step. Until Layer 1+2 values provably reach the runtime graph and change selection behavior, no further enrichment work is justified.
2. **Audit Structured Tension Curation compilation** — verify every dated tension block flows into compiled `structured_tensions` with `activation_condition` preserved. Audit completed 2026-04-21: tensions have 0/491 coverage on the new fields (see Section 14a table). The enrichment work is now Phase 2 of the Section 14 rollout; it runs in parallel with Phase 0/1 plumbing.
3. **Extract per-model "Danger when" reasoning-shape clauses as structured fields** — self-reflexive anti-echo signal. The language is already in the articles; extraction is mechanical under the closed vocabulary principle. Binds directly to the "don't recommend model X if upstream reasoning is already in X's failure mode" requirement.
4. **Extract pre-mortem questions as a new chunk type bound to failure modes** — already curated reasoning probes. Grounded extraction, no new taxonomy.
5. **Shared-example detection via text analysis** — zero article reads, one-time script. Builds latent bridge edges across models from recurring named examples.
6. **If residual selection failures remain after items 1-5, revisit Layer 3 — but reframe it as a query-time traversal mode, not a compile-time edge type.** The intuition behind Layer 3 (interactions have directional character) is real. The wrong move is to flatten that into 4 discrete labels burned into edges at compile time. The right move, if needed, is to let the lane at query time pick a traversal direction based on the reasoning shape it's responding to — the graph itself stays type-free and the 4-type vocabulary only exists as a query-time choice.

**Why this reframe is consistent with the closed vocabulary principle:** items 2-5 extract signals that the curators already wrote into the articles. No new concepts, no new edges between non-222 entities, no factual content promoted to graph structure. Items 2-5 make already-curated content reachable by the runtime; they do not invent categories that force the source into shapes it resists.

**What changes for future sessions:** do NOT start a Layer 3 pilot. Do items 1-5 first. Only after items 1-5 are evaluated (and only if there's evidence of selection failures that items 1-5 don't fix) should Layer 3 be revisited — and then as query-time traversal, not compile-time taxonomy.

---

## 1. What This Project Is (Read First, Understand Before Acting)

Lolla is a knowledge-first reasoning-about-reasoning engine. It audits how an LLM answered a question, detects structural reasoning weaknesses (cognitive tendencies from Munger's Psychology of Human Misjudgment), routes through a curated knowledge graph of 222 mental models, and returns compact structural counter-pressure.

**It does not produce better answers. It produces findings that reopen closed reasoning.**

The system has four independent lanes:
- **Lane 1 (Structural Pressure):** Detects cognitive tendencies, routes to corrective models, produces a DeltaCard
- **Lane 2 (Model Companion):** Recognizes mental models already active in the answer, gathers enrichment material, produces a CompanionCheatSheet
- **Lane 3 (Frame Pressure):** Audits the question itself for embedded assumptions, produces a FramePressureCard
- **Lane 4 (Structural Coverage):** Maps what structural dimensions the answer skipped, produces a StructuralCoverageCard

**Core architecture principle: LLMs at the probabilistic edges, curated knowledge in the deterministic middle.** LLMs do the semantic judgment (detecting tendencies, verifying model presence). Everything from routing through output assembly is deterministic graph traversal and compiled knowledge lookup. The curated material — not the LLM's opinion — is what the user sees.

Read these documents for full understanding before starting any work:
- `/Users/marcin/Desktop/Apps/lolla-skill/HOW_IT_WORKS.md` — the skill-level system documentation
- `/Users/marcin/Desktop/Apps/Lolla-system-b/PRODUCT_VISION.md` — product doctrine and principles
- `/Users/marcin/Desktop/Apps/Lolla-system-b/SYSTEM_UNDERSTANDING.md` — detailed architecture and information flow

---

## 2. Where Everything Lives

### The Knowledge Source (Canonical Articles)
```
/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/
```
222 markdown files. Each is 2,000-5,000 words. These are the semantic root of the entire system. They contain:
- Core Principles
- Playbook (heuristics, frameworks, examples)
- Strengths and Weaknesses (select_when, danger_when)
- Latticework (allies with WHY, antagonists with WHY, concrete examples)
- Structured Tension (model-vs-model conflicts with activation conditions)
- Risks and Mitigations (failure modes, premortems)

**These were extracted from ~200 books using full LLM cognition — not parsing, not keyword matching. The LLM read the source material and made holistic semantic judgments. This quality standard must be maintained.**

### The Curation Layer (Structured JSON from Canonical Articles)
```
/Users/marcin/Desktop/Apps/Lolla-system-b/curation/
├── relation_semantics/       ← Wave 3: allies, antagonists, structured tensions (222 files)
│   └── schema.json           ← JSON schema for this wave
├── intervention_semantics/   ← Wave 2: failure modes, heuristics, premortems (222 files)
├── reframing_semantics/      ← Wave 5: frame pattern → model mappings (50 files)
├── structural_coverage/      ← Wave 6: dimension → model routing
├── family_semantics/         ← Latticework: dense ally clusters (24 validated)
├── prerequisite_semantics/   ← Latticework: A→B ordering edges (15 edges)
└── polarity_semantics/       ← Latticework: failure cascade ↔ correction stack
```

Each curation file references its `source_file` in `MM_CANONICAL_216/`. Each field has `extraction_type` (explicit/normalized) and `confidence` (high/medium/low) tracking how it was derived from the source article.

### The Compiled Artifacts (What the Runtime Actually Uses)
```
/Users/marcin/Desktop/Apps/lolla-skill/data/
├── knowledge_graph.json       ← 222 models with select_when, danger_when, failure_modes, etc.
└── relationship_graph.json    ← 1,358 typed edges between models
```
These are compiled FROM the curation layer by the compilation pipeline in System B:
```
/Users/marcin/Desktop/Apps/Lolla-system-b/system_b/compilation_bundle.py
```

### The Runtime Engine (What Reads the Compiled Artifacts)
```
/Users/marcin/Desktop/Apps/lolla-skill/engine/system_b/
├── relation_graph.py          ← RelationGraph.load() + neighborhood() — THIS IS WHAT WE UPGRADE
├── routing.py                 ← Tendency routing, deep check handling
├── pressure_router.py         ← PressureBundleSelector — chunk selection
└── ...
```

### The Research (Context for This Work)
```
/Users/marcin/Desktop/Apps/lolla-skill/research/
├── graph-improvement-audit.md            ← First audit: bottleneck identification, technique catalog
├── deep-graph-improvement-plan.md        ← Second audit: the flat graph finding, 3-layer plan
└── deep-graph-enrichment-handover.md     ← THIS FILE
```

---

## 3. The Architectural Decision: Upgrade, Not Rebuild

After reading the canonical articles, the curation pipeline, the compilation step, and the runtime code, the answer is clear: **we are upgrading existing positions, not building new ones.**

Why:

1. **The schema already has the right fields.** `source_description` exists on relation edges and contains the WHY text. `composition_affinity` exists but has flat values. `input_type`/`output_type` exist on models but are never used for routing. `reasoning_types` exist but aren't used in selection. The problem is not missing infrastructure — it's that values are flat and fields are unused.

2. **The curation pipeline pattern is proven and repeatable.** Every wave follows the same methodology: LLM reads the full canonical article → makes holistic semantic judgments → outputs structured JSON → human reviews → compile. We follow the exact same pattern for enrichment. No new pipeline needed.

3. **The compilation path already flows.** `curation/relation_semantics/*.json` → compiler → `build/relationship_graph.json` → runtime loads it. Adding new fields to curation JSON flows through the same compiler.

4. **The runtime interface stays the same.** `neighborhood()` returns a `RouteNeighborhood` with `supporting_model_ids` and `risk_model_ids`. Spreading activation replaces the internals of how those IDs are selected, but the interface doesn't change. Downstream code doesn't know.

What we are doing:
- **Enriching the curation layer** — new fields on existing JSON files (affinity strength, activation conditions, interaction type)
- **Extending the compilation step** — new fields flow through to compiled artifacts
- **Upgrading the runtime** — spreading activation replaces `neighborhood()`, chunk selection uses quality metadata

What we are NOT doing:
- No new databases
- No new pipeline infrastructure
- No new lane architecture
- No GNN, no embeddings for graph traversal, no probabilistic scoring

---

## 4. The Problem We Are Solving (Understand This Deeply)

### The Flat Graph

The relationship graph has 1,358 edges. Their `composition_affinity` values are:

| Edge Type | Count | Affinity Distribution |
|-----------|-------|-----------------------|
| ally | 523 | **516 at 0.90**, 7 at 0.75 |
| antagonist | 344 | **330 at 0.25**, 14 at 0.22 |
| tension | 491 | **491 at 0.25** — every single one identical |

When `neighborhood()` sorts allies by `composition_affinity` to pick the top-2 supporting models, 98.7% of values are identical. The sort falls through to the lexical tiebreaker: `(-candidate[0], candidate[1])` — that `candidate[1]` is the model_id string. **The system picks supporting models alphabetically.**

Verify this yourself. Read:
```
/Users/marcin/Desktop/Apps/lolla-skill/engine/system_b/relation_graph.py
```
Lines 120-121:
```python
ordered = sorted(candidates, key=lambda candidate: (-candidate[0], candidate[1]))
```
When `-candidate[0]` is `-0.90` for 98.7% of allies, `candidate[1]` (the model_id string) decides.

### The Hub Problem

Degree distribution (source + target combined):
```
confirmation-bias:          233 edges
systems-thinking:           108 edges
commitment-bias:             63 edges
first-principles-thinking:   59 edges
...
mean:                        12.2 edges
median:                       8 edges
```

`confirmation-bias` has 19x the mean degree. It's connected to virtually everything. When it appears as an antagonist (which it does frequently), it dominates risk model selection for almost any seed. The system's "risk model" output is disproportionately `confirmation-bias` regardless of context.

### What the Canonical Articles Actually Contain (But We Don't Extract)

Open any canonical article, e.g.:
```
/Users/marcin/Desktop/Apps/Lolla-system-b/MM_CANONICAL_216/Power_Dynamics_rag.md
```

Look at the Latticework section. For each ally, the article describes:
1. **WHY the alliance exists** — the synergy mechanism
2. **WHEN it activates** — the specific conditions
3. **A concrete example** — how it plays out in practice

Example from Power Dynamics → Lock In:
> "Lock In explains how commitment changes the future option set; Power Dynamics explains how that narrowed option set shifts bargaining power after the commitment is made."
> Example: "A buyer keeps leverage before migration, then loses it once retraining and interface debt make exit expensive."

Now look at what we currently extract into `curation/relation_semantics/power-dynamics.json`:
```json
{
  "target_model_id": "lock-in",
  "rationale_text": "Lock-in clarifies how integration, retraining, and dependency costs narrow the future option set and invert leverage after commitment.",
  "source_quote": "Lock In explains how commitment changes the future option set",
  "extraction_type": "explicit",
  "confidence": "high"
}
```

And what lands in `relationship_graph.json`:
```json
{
  "source_model_id": "power-dynamics",
  "target_model_id": "lock-in",
  "edge_type": "ally",
  "source_description": "Lock-in clarifies how integration...",
  "composition_affinity": 0.90
}
```

The rich synergy description, the activation condition ("when commitment dynamics are in play"), the concrete example ("buyer loses leverage after migration") — all collapsed to `0.90`. Identical to every other ally edge.

Compare this to survivorship-bias → base-rates:
> "The most powerful tool for fighting survivorship bias is adopting the outside view."

That is STRONG. "The most powerful tool." Versus power-dynamics → optionality:
> "Optionality strengthens power-dynamics analysis by preserving live fallback paths."

That is MODERATE. Not "the most powerful" — just "strengthens." Both are currently `0.90`.

---

## 5. How Previous Curation Waves Were Done (THE METHODOLOGY)

This is the most important section. The enrichment work MUST follow the same methodology.

### The Pattern (Same Across All Waves)

1. **One model at a time.** Each curation file corresponds to one model and its canonical article.
2. **Full article cognition.** The LLM reads the ENTIRE canonical article (2,000-5,000 words), not snippets or excerpts. It understands the model's core logic, failure modes, relationship dynamics.
3. **Holistic semantic judgment.** The LLM is not doing keyword matching or field extraction. It is reading the article the way a thoughtful person would and making a judgment about specific questions (e.g., "When should this model be selected? When is it dangerous?").
4. **Structured output with provenance.** Every extracted field has:
   - `extraction_type`: `"explicit"` if directly stated in the source, `"normalized"` if inferred from multiple passages
   - `confidence`: `"high"` / `"medium"` / `"low"`
   - `source_quote`: a literal passage from the canonical article supporting the extraction
5. **Schema validation.** Each wave has a JSON schema (`schema.json`) that all files must conform to.
6. **Human review.** Outputs are reviewed against the source article. Not against what the LLM "thinks" the model means from training data — against what the canonical article actually says.

### Wave 3 Specifically (Relation Semantics — The One We're Enriching)

Each `curation/relation_semantics/*.json` file has this structure:
```json
{
  "model_id": "power-dynamics",
  "source_file": "Power_Dynamics_rag.md",
  "allies": [
    {
      "target_model_id": "lock-in",
      "rationale_text": "...",        ← WHY the alliance exists
      "source_quote": "...",          ← literal quote from the canonical article
      "extraction_type": "explicit",
      "confidence": "high"
    }
  ],
  "antagonists": [ ... ],
  "structured_tensions": [
    {
      "target_model_id": "confirmation-bias",
      "tension_text": "...",          ← the conflict description
      "source_quote": "...",
      "extraction_type": "explicit",
      "confidence": "high",
      "tension_type": "conflicts"
    }
  ],
  "curation_notes": {
    "summary": "...",
    "donor_drops": ["..."],           ← what was in the source but intentionally NOT kept
    "open_questions": ["..."]         ← unresolved curation questions
  }
}
```

The `rationale_text` already contains the WHY. What it doesn't contain:
- **Affinity strength differentiation** — currently all allies compile to 0.90
- **Activation condition** — the "when" clause that says under what circumstances this relationship fires
- **Interaction type** — whether the ally amplifies, corrects, is a prerequisite, or complements
- **Concrete example** — the specific scenario showing the interaction in practice (many articles have these in their Latticework tables)

---

## 6. The Work Plan (Three Layers, In Order)

### Layer 1: Differentiate Ally Affinities (Highest Priority)

**Goal:** Replace the flat `composition_affinity: 0.90` on all ally edges with differentiated values (0.70 / 0.80 / 0.90 / 0.95) based on the language strength in the canonical article's Latticework section.

**Why this is first:** It's the highest-impact, lowest-risk change. It requires no new schema fields — only better VALUES in an existing field. It directly fixes the alphabetical selection problem.

**Approach — one article at a time:**

For each of the 222 models:

1. Open the canonical article: `MM_CANONICAL_216/{ModelName}_rag.md`
2. Read the Latticework section — specifically the ally descriptions
3. For each ally, assess the language strength:
   - **0.95 (CRITICAL):** Language like "the most powerful tool", "the essential companion", "cannot function without". The article describes the ally as indispensable to the model's operation.
   - **0.90 (STRONG):** Language like "directly strengthens", "is the primary mechanism for", "provides the key discipline". The article describes a strong, specific synergy mechanism.
   - **0.80 (MODERATE):** Language like "strengthens", "helps", "supports". The article describes a useful but less specific relationship.
   - **0.70 (SUPPORTIVE):** Language like "can help", "is related to", "provides additional perspective". The article describes a generic or tangential connection.
4. Update the curation file `curation/relation_semantics/{model-id}.json` — add an `affinity_strength` field to each ally entry
5. Document the rationale in `curation_notes`

**Calibration protocol:** Before processing all 222 models, do a 10-article pilot. Pick articles with known variation:
- `survivorship-bias` (has "the most powerful tool" language for base-rates)
- `power-dynamics` (has a range from strong to moderate allies)
- `confirmation-bias` (233 edges — the hub)
- `first-principles-thinking` (59 edges — high degree)
- `premortem` (likely has focused, specific allies)
- `circle-of-competence` (known to have nuanced boundary-blur failure)
- `inversion` (a foundational model likely described as critical ally to many)
- `game-theory-payoffs` (likely has strong specific allies like Nash equilibrium)
- `margin-of-safety` (known tension with calculated-risk-taking)
- `lock-in` (specific, operational model)

After the 10-article pilot:
- Check if the differentiation feels meaningful (are the 4 levels actually separable?)
- Check if the same model gets different strengths as an ally of different models (it should — the relationship is directional)
- Adjust the rubric if needed before proceeding with all 222

### Layer 2: Extract Activation Conditions (Medium Priority)

**Goal:** For each ally/antagonist edge, extract the specific condition under which the interaction becomes relevant. Turn edges from static to conditional.

**Why this is second:** Activation conditions are the most valuable un-extracted signal. They enable context-sensitive supporting model selection — "this ally relationship fires specifically when commitment dynamics are in play, not generically."

**New field on each ally/antagonist/tension entry:**
```json
{
  "target_model_id": "lock-in",
  "rationale_text": "...",
  "source_quote": "...",
  "activation_condition": "when commitment is changing the future option set and integration costs are rising",
  "extraction_type": "explicit",
  "confidence": "high"
}
```

**Approach:** Same methodology — read the full canonical article, look at the Latticework description for each relationship, extract the "when" clause. Many descriptions contain explicit conditions. Some are implicit and must be inferred from the synergy mechanism.

**Important:** Not every edge will have a clear activation condition. Some relationships are genuinely generic ("critical thinking helps everything"). For those, the field should be `null` or a brief note like `"general — no specific activation context"`. Do NOT fabricate conditions that aren't in the source material.

### Layer 3: Classify Interaction Types (Lower Priority, Do After Layers 1-2)

**Goal:** For each ally/antagonist/tension edge, classify the interaction mechanism type.

**Types:**
- **amplification:** One model makes another's effect stronger. "Confirmation bias reinforces survivorship bias by selecting supporting evidence."
- **correction:** One model directly counters another's failure. "The outside view is the most powerful tool for fighting survivorship bias."
- **prerequisite:** You need to understand A before B applies. "Lock In explains how commitment changes the option set." (Understanding lock-in is a prerequisite for seeing the power dynamics.)
- **complementary:** The models cover different aspects of the same situation. "Game Theory models the move-response structure, while Power Dynamics identifies which commitments are credible."

**New field:**
```json
{
  "target_model_id": "lock-in",
  "rationale_text": "...",
  "interaction_type": "prerequisite"
}
```

**This is harder than Layer 1.** The types overlap. A relationship can be both complementary and prerequisite. The rubric needs careful definition after Layer 1 is done and the articles have been read deeply.

---

## 7. Layer 1 Detailed Instructions (For the Junior Developer)

### Before You Start

1. Read `/Users/marcin/Desktop/Apps/lolla-skill/HOW_IT_WORKS.md` fully
2. Read `/Users/marcin/Desktop/Apps/Lolla-system-b/PRODUCT_VISION.md` fully
3. Read `/Users/marcin/Desktop/Apps/lolla-skill/research/deep-graph-improvement-plan.md` fully
4. Read this handover document fully
5. Open `relation_graph.py` at `/Users/marcin/Desktop/Apps/lolla-skill/engine/system_b/relation_graph.py` and understand how `neighborhood()` and `_bounded_unique_model_ids()` work
6. Open one canonical article (e.g., `Survivorship_Bias_rag.md`) and one curation file (e.g., `curation/relation_semantics/survivorship-bias.json`) side by side. Understand the mapping between what's in the article and what's in the curation file.

### The Pilot (10 Articles)

**Step 1:** Pick the 10 pilot articles listed in Section 6.

**Step 2:** For each pilot article, create a working document with this structure:

```markdown
## {model-id} — Affinity Differentiation

Source: MM_CANONICAL_216/{ModelName}_rag.md
Curation: curation/relation_semantics/{model-id}.json

### Ally Assessments

| Target | Current Affinity | Source Language | Proposed Affinity | Rationale |
|--------|-----------------|----------------|-------------------|-----------|
| base-rates | 0.90 | "the most powerful tool" | 0.95 | Described as the primary, indispensable counter |
| critical-thinking | 0.90 | "the ability to notice biases" | 0.80 | Helpful but generic, not specific to this model |
| premortem | 0.90 | "stress-test edge cases" | 0.90 | Strong and specific — proactive failure imagination |

### Observations
- [Any patterns noticed, difficulties with the rubric, edge cases]
```

**Step 3:** After all 10 pilots, review the working documents together. Ask:
- Are the 4 affinity levels actually separable? (If 0.70 and 0.80 are hard to distinguish, collapse to 3 levels.)
- Does the same model get different strengths as an ally of different models? (It should.)
- Are there articles where the Latticework section is too thin to differentiate? (Note these — they may need a different approach.)

**Step 4:** Adjust the rubric based on the pilot. Then proceed with the remaining 212 articles.

### Processing Each Article (The Full Flow)

For each of the 222 models:

1. **Read the canonical article.** Open `MM_CANONICAL_216/{ModelName}_rag.md`. Read the full Latticework section. Understand each ally/antagonist relationship's mechanism.

2. **Read the current curation file.** Open `curation/relation_semantics/{model-id}.json`. Match each ally/antagonist to what you read in the article.

3. **Score each ally.** Using the 4-level rubric, assign a differentiated affinity based on the language strength in the canonical article.

4. **Update the curation file.** Add an `affinity_strength` field to each ally. Example:
   ```json
   {
     "target_model_id": "base-rates",
     "rationale_text": "Base-rates are the direct antidote...",
     "source_quote": "outside view demands that one explicitly...",
     "extraction_type": "explicit",
     "confidence": "high",
     "affinity_strength": 0.95,
     "affinity_rationale": "Described as 'the most powerful tool' — the primary, indispensable counter to survivorship bias."
   }
   ```

5. **Do NOT change anything else in the curation file.** Do not rewrite rationale_text, do not add new allies, do not remove existing entries. This pass only adds `affinity_strength` and `affinity_rationale` to existing ally entries.

6. **Update curation_notes.** Add a note to the `curation_notes.summary` field indicating that affinity differentiation has been applied.

### What the LLM Prompt Should Look Like (When Using LLM Assistance)

If using an LLM to help with the differentiation, the prompt must:

1. **Include the FULL canonical article text.** Not a summary. Not excerpts. The full file.
2. **Include the current curation file's ally list.** So the LLM knows which allies to assess.
3. **Include the 4-level rubric** with examples of each level.
4. **Ask for a specific output format** with the affinity value AND the rationale citing specific language from the article.
5. **Ask the LLM to quote the exact passage** that supports the differentiation.

The prompt should NOT:
- Ask the LLM to assess relationships from its training data
- Ask the LLM to add new ally relationships not in the curation file
- Ask the LLM to rate based on its "knowledge" of the mental model
- Skip the canonical article and rely on the LLM's general understanding

**The canonical article is the ONLY source of truth. The LLM is a reading assistant, not an authority.**

### Model Choice for the LLM Assistance

- **Claude Opus** — recommended for this work. Strongest at nuanced reading comprehension, judging language strength ("the most powerful" vs "helps" vs "can support"). Cost is higher but this is a one-time pass across 222 articles.
- **GPT-4o** — viable alternative. Good structured output.
- **grok-4.1** — the production model for the Lolla pipeline itself. Using it keeps cognitive alignment but may not be as strong at the nuanced language-strength judgments.

Run the 10-article pilot with your chosen model. If the differentiation quality is weak, try a different model before proceeding.

---

## 8. After Layer 1 Is Done: Runtime Changes

> **NOTE (post-pilot):** Section 0b above contains the SPECIFIC pipeline fixes needed — validator, loader, and compiler. The descriptions below are the original high-level notes. Section 0b has the exact file paths, line numbers, and code changes. Follow 0b, not the vague descriptions here.

Once the curation files have differentiated `affinity_strength` values:

### 8a. Update the Compilation Step

The compiler at `/Users/marcin/Desktop/Apps/Lolla-system-b/system_b/compilation_bundle.py` needs to read the new `affinity_strength` field and use it as the `composition_affinity` in the compiled `relationship_graph.json` instead of the current flat values.

**Post-pilot finding:** The compiler also requires fixes to the validator (`relation_semantics.py:664`) and the loader (`RelationItem` dataclass + `_items_from_payload()`). See Section 0b for details. The original handover missed these because it only checked the JSON schema, not the Python validation layer.

### 8b. Fan-Adjusted Affinity — DONE (implemented differently than planned here)

> **This section's original code was NOT used.** Applying fan correction at load time (mutating stored affinities) breaks the `min_supporting_affinity=0.6` threshold — even CRITICAL allies of moderate-degree models drop below 0.6. See Section 0d for the actual implementation: fan correction applied at ranking time only, raw affinities preserved for threshold filtering.

The same formula is used (`affinity / (1 + ln(degree))`), but applied in `neighborhood()` when building candidate lists, not in `load()` when building the graph. This separates "is this ally strong enough to be a candidate?" (raw affinity, threshold) from "which candidate should we pick?" (fan-adjusted, ranking).

### 8c. Quality Metadata in Chunk Selection

In the chunk selection logic (`PressureBundleSelector` or equivalent), add `confidence` and `extraction_type` to the sort key:
```python
key = (
    model_rank,
    type_rank,
    0 if confidence == "high" else (1 if confidence == "medium" else 2),
    0 if extraction_type == "explicit" else 1,
    chunk_id,
)
```

### 8d. Spreading Activation (Layer 2 Runtime — Do Later)

Replace `neighborhood()` internals with spreading activation + fan correction. This is the bigger algorithmic change (~40 lines). It replaces single-hop lookup with multi-hop traversal that handles signed edges (allies = positive, antagonists = negative), decays with distance, and dampens hubs. Do this AFTER Layer 1 curation is validated.

The `RouteNeighborhood` interface stays the same. Downstream code doesn't change.

---

## 9. Validation Steps

### After the 10-Article Pilot — DONE

- [x] Affinity values are meaningfully differentiated (not all 0.90)
- [x] The same model gets different strengths as ally of different models
- [x] Every differentiation cites specific language from the canonical article
- [x] The rubric's 4 levels are actually distinguishable (or adjust to 3)

### After All 222 Articles Are Done — DONE (enrichment verified, compilation pending)

- [x] Verify the affinity distribution is no longer flat: 0.70 (1.7%), 0.80 (36.9%), 0.90 (54.1%), 0.95 (7.3%)
- [ ] Run the compilation pipeline — new `affinity_strength` values flow into `relationship_graph.json`
- [ ] Run the existing pipeline on 3-5 test conversations
- [ ] Check whether supporting model selection is no longer alphabetical
- [ ] Check whether supporting model diversity improved
- [ ] Check whether `confirmation-bias` still dominates risk model selection

### After Fan-Adjusted Affinity Is Applied — CODE DONE, needs end-to-end validation

Fan correction code is live and unit-tested. End-to-end validation requires compiling the enriched data first.

- [x] Unit tests pass: hub dampening works, threshold uses raw affinity, ranking uses adjusted affinity
- [ ] Re-run the same test conversations (after compilation)
- [ ] Confirm hub models (confirmation-bias, systems-thinking) are no longer always selected
- [ ] Confirm focused, specific models now appear in neighborhoods they were previously excluded from
- [ ] Check that no edge case produces empty neighborhoods (no model above threshold)

---

## 10. Quality Gates — What NOT to Do

> **NOTE (post-pilot):** Some rules below have been adjusted. Changes are marked.

### DO NOT:
- **Script batch processing of all 222 articles at once.** Each article must be read carefully. The differentiation requires understanding the nuance of the Latticework language. A batch script that runs 222 LLM calls and writes all files will produce mediocre, undifferentiated results.
- **Use the LLM's general knowledge instead of the canonical article.** The LLM may "know" that base-rates is important for survivorship-bias from its training data. That doesn't matter. What matters is what the canonical article says and how strongly it says it.
- **Add new allies or remove existing ones.** The 222 curated models and their edges are the fixed concept space. SPARSE ally recovery was proposed and rejected — adding allies the curation deliberately dropped overrides curator judgment. See Section 0c.
- **Change the schema without a plan.** If you need a new field, update `schema.json` first, validate it makes sense, then add it to the files. **Also update the Python validator and loader** — the JSON schema and the Python validation layer are independent (this was missed in the original handover).
- ~~**Skip the pilot.**~~ **DONE.** The 10-article pilot is complete. See `lolla-skill/research/layer1-pilot-results.md`. The rubric is validated. Proceed directly with the remaining 212 articles.
- **Rush.** We are not in a hurry. 222 articles at quality is better than 222 articles done fast. A mediocre enrichment pass is worse than the current flat values because it creates false confidence that the values are differentiated when they're not.
- **Process only allies and skip antagonists.** *(Post-pilot addition.)* Antagonist edges are equally flat (330 of 344 at 0.25) and the same alphabetical tiebreaker breaks risk model selection. Apply the same language-strength rubric to antagonist entries in the same pass.
- **Do Layer 1 and Layer 2 as separate passes.** *(Post-pilot revision.)* The original plan said to do affinity first, then activation conditions later. The pilot proved both signals live in the same Latticework text. A single careful read extracts both. See Section 0c, Change 1.

### DO:
- **Read the canonical article fully for every model.** Not just the Latticework section. The Core Principles and Strengths/Weaknesses sections often contain language that clarifies relationship strength.
- **Track your progress.** Keep a running list of which models have been processed and which haven't.
- **Note patterns as you go.** If you notice that certain types of models (e.g., cognitive biases vs operational frameworks) have systematically different Latticework section structures, note it. This will inform Layer 3 work.
- **Validate each batch.** After every 20-30 articles, spot-check 3-4 by reopening the canonical article and verifying the differentiation still feels right.
- **Extract activation conditions alongside affinity.** *(Post-pilot addition.)* For each ally/antagonist, extract the "when" clause if it exists. Many Latticework descriptions contain explicit conditions. If the relationship is generic, set `activation_condition` to `null`.
- ~~**Flag sparse models for ally recovery.**~~ *(Rejected — see Section 0c. Violates closed vocabulary principle.)*

---

## 11. What Comes After (Future Sessions)

**COMPLETED:**

| Step | Status | Notes |
|------|--------|-------|
| Layer 1+2 enrichment (222/222) | DONE | All ally + antagonist edges have differentiated affinity_strength, affinity_rationale, activation_condition |
| Pipeline fixes | DONE | Validator, loader, compiler all accept new fields |
| Fan correction | DONE | Runtime ranking dampens hubs. See Section 0d for implementation details. |
| SPARSE ally recovery | REJECTED | Overrides curator judgment. Violates closed vocabulary principle. See Section 0c. |

**NEXT — in priority order:**

1. **Compile and verify end-to-end.** Run the compilation pipeline on all 222 enriched curation files. Verify differentiated `affinity_strength` values flow into `relationship_graph.json`. Run 3-5 test conversations. Check that supporting model selection is no longer alphabetical and hub models no longer dominate. See Section 9 for the full validation checklist.

2. **Layer 3: RECONSIDERED on 2026-04-16 — see Section 0g. Activation & Rationale wiring rollout planned on 2026-04-21 — see Section 14.** The original plan (classify each edge as amplification/correction/prerequisite/complementary) was based on a rubric the canonical articles resist. Re-reading 10 random articles showed the 4 types blend in source prose. The revised plan extracts already-curated signals (Structured Tension activation conditions, "Danger when" reasoning-shape clauses, pre-mortem questions, recurring named examples) before inventing a new taxonomy. The activation-condition wiring into the runtime engine (Phases 0-5) is now the operational sequencing — Section 14 supersedes this item for work-order decisions. If Layer 3 is revisited later, it should be a query-time traversal mode, not a compile-time edge type.

3. **Spreading activation algorithm.** Replace `neighborhood()` internals with multi-hop traversal that handles signed edges (allies = positive, antagonists = negative), decays with distance, and uses fan-adjusted weights. The `RouteNeighborhood` interface stays the same — downstream code doesn't change. Under the revised plan (Section 0g), this can use activation_condition matching + fan-adjusted weights instead of waiting for Layer 3 interaction types.

4. **Input/output type matching.** Compute functional dependency edges from existing `input_type`/`output_type` fields on models. One-time analysis script, not a per-article pass.

5. **Concrete interaction examples.** Extract specific examples from Latticework tables ("A buyer keeps leverage before migration..."). High value for companion lane. Requires a new chunk type.

**The value compounds:** differentiated affinities → fan correction meaningful → spreading activation meaningful → activation conditions enable context-sensitive selection.

---

## 12. Summary of Key Files

| File | What It Tells You | Where |
|------|-------------------|-------|
| **This handover** | Section 0 is the authoritative summary | `lolla-skill/research/deep-graph-enrichment-handover.md` |
| **relation_graph.py** | **Runtime with fan correction (the latest change)** | `lolla-skill/engine/system_b/relation_graph.py` + `Lolla-system-b/system_b/relation_graph.py` |
| **test_relation_graph.py** | **Unit tests including fan correction tests** | `Lolla-system-b/tests/test_relation_graph.py` |
| **test_pipeline.py** | **Integration test — end-to-end with fan correction** | `Lolla-system-b/tests/test_pipeline.py` |
| **test_routing.py** | **Routing tests — supporting model ordering** | `Lolla-system-b/tests/test_routing.py` |
| layer1-enrichment-progress.md | Progress tracker (222/222 done) | `lolla-skill/research/layer1-enrichment-progress.md` |
| layer1-pilot-results.md | Pilot data, rubric validation | `lolla-skill/research/layer1-pilot-results.md` |
| relation_semantics.py | Validator + loader (pipeline fixes done) | `Lolla-system-b/system_b/relation_semantics.py` |
| compilation_bundle.py | Compiler (lines 670-760, affinity compilation) | `Lolla-system-b/system_b/compilation_bundle.py` |
| schema.json | Wave 3 curation schema (updated) | `Lolla-system-b/curation/relation_semantics/schema.json` |
| Any enriched curation file | See the enriched format (e.g., inversion.json) | `Lolla-system-b/curation/relation_semantics/*.json` |
| HOW_IT_WORKS.md | Full system documentation | `lolla-skill/HOW_IT_WORKS.md` |
| PRODUCT_VISION.md | Product doctrine | `Lolla-system-b/PRODUCT_VISION.md` |

**Reading order for new sessions:** Section 0 of this doc → `relation_graph.py` (see fan correction) → one enriched curation file (e.g., `inversion.json`) → system docs as needed.

---

## 13. Guiding Principles

### Closed Vocabulary Principle

The 222 curated mental models are the ONLY reasoning primitives. The system reasons about reasoning — the models reason about each other, and the runtime maps user situations to the graph. Enrichment layers (affinity, activation conditions, interaction types) exist to make the existing graph more precise, not to expand the concept space.

Any enrichment work must only connect or refine existing models. If a canonical article mentions a concept that isn't one of the 222 models, it gets noted but NOT added to the graph. Recovery candidates must be existing model IDs. New layers describe HOW existing models relate, not WHAT new models to add.

This principle was established after earlier system iterations relied on a case-by-case approach — extracting factual elements from situations and trying to match them to mental models. The factual state interfered with reasoning, assessment, and analysis. The system was later redesigned around "reasoning about reasoning" to prevent this.

### Quality Standard

The canonical articles were created by feeding ~200 books into an RAG system and using full LLM cognition to synthesize structured knowledge for each mental model. The result is a knowledge substrate that contains insights the LLM doesn't have natively — not because the information is secret, but because it was synthesized from specific source material and structured for a purpose (reasoning audit) that no training corpus optimizes for.

That extraction quality is the moat. Do not degrade it. Every enrichment pass must operate at the same standard: read the full article, understand the model's core logic, make a judgment grounded in what the article actually says, provide provenance for every value you assign.

The graph doesn't need to be smarter. It needs to know what it already has.

---

## 14. Activation & Rationale Wiring — Rollout Plan (2026-04-21)

This section captures the phased rollout plan for making `affinity_rationale`, `activation_condition`, and `affinity_strength` reachable by the live skill runtime. It was decided in a session on 2026-04-21 and supersedes Section 11 item 2 and the tail of Section 0g item 2 for the operational sequencing. Every phase has a scope, a repo, a work item, a test, and a reason. The reasoning is preserved so that future sessions — or future humans — can judge whether the phase is still worth doing under changed conditions.

**Read this before touching compiler, loader, router, or card rendering code.** The decisions below were reached after reconciling three forces the system pulls in different directions: the Closed Vocabulary Principle, the Facts/Reasoning Break doctrine, and the fidelity of Layer 1+2 curation. A change that violates any of them undoes session work.

**Revision notes (2026-04-21 post-audit):** this section was audited against the real code and a 20-sample check of existing `activation_condition` strings. Four revisions were applied and are flagged inline:

- **REV-1:** Phase 0.5 (Layer 1+2 doctrine audit) inserted before Phase 1 — we cannot gate Phase 2 at ≥95% cognitive-move rate without first measuring Layer 1+2's actual baseline. Initial sample suggests ~45% clear cognitive move, ~35% situational, ~20% mixed. The matcher and gates must be calibrated to whatever that baseline turns out to be, not to an aspiration.
- **REV-1 update (2026-04-21, post-audit):** Phase 0.5 ran on a 100-edge random sample. Actual distribution is **84% cognitive-move, 8% situational, 8% mixed** — not the 45% estimated from the initial 20-sample spot check. Full audit in `research/activation_condition_doctrine_audit_2026-04-21.md`. The 84% figure informs Phase 3 noise-floor threshold tuning but is NOT a Phase 2 gate — see REV-5.
- **REV-5 (2026-04-21, supersedes REV-1's Phase 2 gate):** Phase 2's gate changed from "≥ Layer 1+2 cognitive-move baseline" to **faithfulness-to-source-article**. Reason: the curated corpus is the authority — we measure what's there, we don't rewrite it to fit a rubric (see feedback memory "Corpus is authority"). Demanding the tension re-read hit 84% cognitive-move would force synthesis beyond what canonical articles support. The Phase 2 gate now asks: "is every claim in the extracted strings traceable to specific article prose, without additions or omitted qualifiers?" Rubric ratings post-extraction are informational only, for Phase 3 tuning.
- **REV-2:** Old Phase 3 (ranking blend) and old Phase 4 (tiebreaker) swapped. Activation match ships as a near-tie tiebreaker first (narrower blast radius), then generalizes to a ranking blend only after the tiebreaker gate data shows the signal carries. The numbering stays (Phase 3 = tiebreaker, Phase 4 = blend) so the rollout order matches the section order.
- **REV-3:** The typed-matcher signature in 14b uses the *real* codebase type names (`FingerprintPayload`, `TriggeredTendency`, `FrameRoute`, `DimensionRoute`) instead of the names I invented in the first draft.
- **REV-4:** The naming collision between the existing `ModelBinding.activation_context` (tendency→model binding field, already in `tendency_catalog.py`) and the new edge-level `activation_condition` is disambiguated explicitly in 14b. Two different layers, two different fields, similar names — each layer stays separate.

A fifth caveat sits in 14h: the blend weight, near-tie epsilon, and suppression threshold were all written as "0.5/0.5 default" or "TBD in Phase N" in the first draft. That was confident phrasing for values that have no grounding yet. They remain open; Phase 3 fixture data sets all three.

---

### 14a. What we are wiring and why

Layer 1+2 curation populated three fields on every curated ally and antagonist edge:

- `affinity_strength` (0.70-0.95, float) — differentiated composition affinity
- `affinity_rationale` (prose) — why this pair composes at the asserted strength
- `activation_condition` (prose) — the reasoning shape under which this edge is active

**Coverage, verified 2026-04-21:**

| Record type | Count | affinity_strength | affinity_rationale | activation_condition |
|---|---|---|---|---|
| Allies (curation) | 523 | 523/523 (100%) | 523/523 (100%) | 523/523 (100%) |
| Antagonists (curation) | 344 | 344/344 (100%) | 344/344 (100%) | 344/344 (100%) |
| Structured tensions (curation) | 491 | 0/491 (0%) | 0/491 (0%) | 0/491 (0%) |
| Compiled `relationship_graph.json` edges | 1358 | 1358/1358 (carried) | 0/1358 (lost) | 0/1358 (lost) |

Two gaps are visible: the compiler drops `affinity_rationale` and `activation_condition` when building `relationship_graph.json`, and structured tensions were never enriched in Layer 1+2 to begin with.

**Three unlocked values once the wiring exists:**

1. **Context-sensitive selection.** Right now the router picks supporting models from allies by fan-adjusted affinity alone. With `activation_condition` reachable, the router can prefer edges whose activation shape matches the reasoning shape the lane already detected — collapsing ties that fan correction leaves unresolved, and suppressing edges that are technically allies but wrong for this reasoning move.
2. **Explainable cards.** Today the card says "also consider X." With `affinity_rationale` reachable, the card can say "also consider X — useful here because [rationale]." The rationale was already written by the curator; the runtime just needs to surface it.
3. **Self-reflexive anti-echo.** Activation conditions on antagonists encode the reasoning shapes under which recommending a model would amplify the failure mode the upstream reasoning is already in. If the upstream reasoning is in model X's failure shape, don't recommend model X. This is the strongest form of the "don't echo the broken reasoning" principle the system has ever had access to.

None of the three requires new curation (except for tensions in Phase 2). They require surfacing content that is already written.

---

### 14b. Architectural rule: activation-match inputs are reasoning-shape outputs only

**The rule:** The activation-matching function accepts ONLY reasoning-shape outputs from the lanes as inputs. It NEVER accepts `vanilla_answer`, extracted quotes, situation summaries, user-query phrasing, or any other factual content.

**Enforceable input types (real codebase names, REV-3):**

- `FingerprintPayload` — Lane 2 fingerprint record (`engine/system_b/companion.py`), containing the tendency/move classification produced by the companion lane.
- `TriggeredTendency` / `TendencyRef` — Lane 2 tendency records (`engine/system_b/pipeline.py`, `engine/system_b/tendency_catalog.py`). The matcher consumes the `description` field of the `TendencyRef` or the triggered tendency's identifier — NOT any user-side text.
- `FrameRoute` — Lane 3 frame-pressure output (`engine/system_b/frame_pressure.py`). The matcher consumes the route's pattern identifier, not the frame elements (which carry extracted text).
- `DimensionRoute` / `DetectedDimension` — Lane 4 dimension-coverage output (`engine/system_b/structural_coverage.py`). The matcher consumes the dimension identifier and the structured coverage judgment.

The matcher signature must be typed such that passing a raw `str` from any other source is a type error at the import boundary. If no convenient union type exists, introduce a thin `ReasoningShapeInput` wrapper class that only the lane code can instantiate — so the type itself encodes "this came from a lane, not from extraction."

**Why this rule exists:** `activation_condition` values are written in reasoning-shape prose by the curators. Example shape from real curation (2026-04-21 sample): "When familiar perceptual patterns dominate interpretation, causing novel configurations to be force-fitted into known gestalts rather than perceived on their own terms." These are descriptions of cognitive moves, not situations. A matcher that consumes lane outputs can honor them. A matcher that consumes `vanilla_answer` or query strings would re-introduce the exact factual coupling the Facts/Reasoning Break was designed to prevent: the lanes would classify on reasoning shape, then the router would silently un-classify by matching on situation words. Everything downstream becomes fact-driven again.

**Why the type-level enforcement:** A convention that says "don't pass facts" will be violated within three sessions. A type that rejects facts at the function boundary cannot be violated without the refactor being visible.

**Naming collision callout (REV-4):** the codebase already uses a field called `ModelBinding.activation_context` (tendency→model binding in `engine/system_b/tendency_catalog.py:18`). That field flows into `PressureRoute.primary_activation_context`. It describes *when to apply a specific model as an antidote to a specific tendency* — one layer above edge-level `activation_condition`. The new edge-level `activation_condition` describes *when an ally/antagonist composes with its source model*. Do not rename either; do not conflate them. In code review, always trace which layer the field belongs to (tendency→model vs model→model edge) before editing. Future sessions should read this callout before any touch to either field.

**Doctrine audit requirement (revised in REV-1):** before Phase 2 enrichment, Phase 0.5 samples the EXISTING 867 ally+antagonist activation_conditions and rates them for "cognitive move" vs "situational" vs "mixed." The realistic baseline (initial 20-sample check: ~45% clear cognitive move) becomes the floor for Phase 2 — tensions must hit at least that rate to ship. The old ≥95% target was aspirational; it was replaced with "do no worse than Layer 1+2" because the curators have been writing in mixed prose all along, and the matcher has to tolerate that phrasing reality rather than demand Phase 2 rewrite it retroactively. If Phase 0.5 reveals Layer 1+2 quality lower than expected, the matcher noise floor in Phase 3 absorbs the gap (see 14d revised tuning lever).

---

### 14c. Pickup points — where the deterministic engine consumes these fields

REV-2 reordered matching phases (tiebreaker first, blend second). Table updated to reflect current plan.

| # | Pickup | Field(s) consumed | Matching? | Doctrine status |
|---|---|---|---|---|
| 1 | `RelationGraph.neighborhood()` — ranking supporting/risk models | `affinity_strength` (already), `activation_condition` (Phase 3 tiebreaker, Phase 4 blend) | Yes (Phase 3 narrow, Phase 4 broad) | Preserved — matcher takes lane outputs only |
| 2 | Routing — picking which bundle/lane owns which models | `activation_condition` (Phase 3 tiebreaker) | Yes (Phase 3) | Preserved — tiebreaker only, fan-adjusted affinity still primary |
| 3 | Bundle selection — resolving near-ties between candidate models | `activation_condition` (Phase 3 tiebreaker) | Yes (Phase 3) | Preserved — same matcher as Pickup 1 |
| 4 | Card rendering — the "why this model" line | `affinity_rationale` (Phase 1) | No — pass-through | N/A — no selection, just display |
| 5 | Anti-echo — suppressing antagonist recommendations whose activation matches upstream failure shape | `activation_condition` on antagonists (Phase 5) | Yes (Phase 5) | Preserved — matches against Lane 2 fingerprint only |

Pickups 1-3 and 5 require the matcher from 14d. Pickup 4 is pure pass-through rendering and has no doctrine risk.

---

### 14d. Matching approach — DECIDED: embedding cosine similarity

**Decision:** Use embedding cosine similarity against `activation_condition` strings, computed via the existing `embedding_retriever.py` infrastructure. This is Option B from the three options considered.

**How it works:**

1. At compile time, produce an embedding for every `activation_condition` string in the graph and store alongside the edge.
2. At query time, produce an embedding for the lane output (e.g. the Pass 2 tendency description string) via the same model.
3. Match score = cosine similarity, normalized to [0, 1].
4. Combine with fan-adjusted affinity via a weighted formula (weight TBD in Phase 3 tuning, default 0.5 activation / 0.5 affinity).

**Why this was chosen over Options A and C:**

- **Option A — keyword/phrase overlap.** Rejected. Keyword overlap between reasoning-shape prose is noisy (the curators vary phrasing deliberately to avoid template repetition). It would create systematic matching errors wherever two activation conditions describe the same cognitive move in different words.
- **Option C — LLM-as-judge at query time.** Rejected. LLMs in the hot path re-introduce the latency and non-determinism the skill architecture spent months removing. It would also mean the selection step depends on an LLM call whose output is not reproducible — breaking the testability contract of the deterministic engine.
- **Option B — embedding cosine.** Chosen. Deterministic because embeddings are fixed after compile. Fast because it's one vector multiply per candidate at query time. Robust to phrasing variation because embedding models encode semantic similarity across wording. Uses infrastructure already in the skill (`embedding_retriever.py`).

**Tradeoff accepted:** embeddings are coarser than a well-prompted LLM judge. Phase 3 tests will quantify the gap; if the gap is unacceptable on specific match pairs, two tuning levers exist in order of preference:
1. **Threshold guard (first resort).** Ignore matches below a similarity floor — feed them through as "no activation signal," falling back to fan-adjusted affinity alone. Accepts that low-quality activation_conditions (the ~35% situational language from the Layer 1+2 baseline) won't contribute signal rather than pretending they do.
2. **Targeted fixture expansion (second resort).** Add discriminating reasoning-shape language to `activation_condition` in Phase 2. This is per-tension, not retroactive rewriting of Layer 1+2 — the Layer 1+2 values stay as-authored.

**Embeddings.db backfill (REV addition):** the existing `data/embeddings.db` was built over chunks and model content; it does NOT contain activation_condition embeddings. Phase 3 requires a one-time backfill step — batch-embed every compiled edge's `activation_condition` string and store in a new `edge_activation_embeddings` table (or similar). Approximate cost: 867 ally/antagonist + 491 tension = 1,358 strings × `text-embedding-3-large` ≈ $2-5 per full recompile. Not a blocker; document the backfill in the Phase 3 runbook.

---

### 14e. Testing philosophy — DECIDED: synthetic fixtures

**Decision:** All rollout phases are tested against synthetic fixtures in `lolla-skill/tests/fixtures/`, not real conversations. The decision was explicit: we are testing the engine, not the extraction → engine composition.

**Why synthetic fixtures, not real conversations:**

1. Real conversations couple two quality signals — extraction quality (skill Step 2) and engine quality (skill Step 3). A regression in either shows up in the integration output, but a test that fails on a real conversation cannot distinguish which component regressed.
2. We do not yet have a validated golden set of conversations. Building one would itself require extraction to be known-good.
3. The engine can be tested against hand-authored Lane outputs that represent what "good extraction" would produce, independent of whether extraction actually produces that on real input today.
4. Synthetic fixtures are editable, versionable, and can be authored at the same quality bar as canonical articles — which is the quality bar the engine was designed for.

**Three fixture families, all under `lolla-skill/tests/fixtures/`:**

- **`reasoning_shapes/`** — hand-authored Lane 2 fingerprints, Pass 2 tendency descriptions, Lane 3 pattern IDs, Lane 4 dimension IDs. These simulate "what a perfect extraction would output for this reasoning shape." Each fixture file carries a short preamble describing the reasoning move it represents. No `vanilla_answer` strings, no situation facts.
- **`graphs/`** — small test subgraphs (not the full 222) with hand-authored `activation_condition`, `affinity_rationale`, `affinity_strength` values. These are the targets that `reasoning_shapes/` inputs will be matched against.
- **`expectations/`** — the expected selection output for each `(reasoning_shape, graph)` pair. Includes which model should win, the margin, and why. The "why" is what makes a test regression actionable.

**Quality bar for fixtures:** author each fixture like a canonical article fragment. Reasoning shapes must describe cognitive moves, not situations. Activation conditions must be reasoning-shape prose. If a fixture slips factual content into an input or target, the fixture is wrong — not the matcher.

**Blind authoring protocol (REV addition):** if one person authors both `reasoning_shapes/` inputs and `graphs/` targets in the same session, they will unconsciously match them — the test becomes self-confirming. Prevention:
1. Author `graphs/` first, independently.
2. Author `reasoning_shapes/` against the intent of the test, WITHOUT looking at the activation_condition strings that will be the match targets.
3. A second pass deliberately adds near-miss distractor targets — edges whose activation_condition overlaps the reasoning shape in wording but NOT in cognitive meaning. The expected output is that the matcher does NOT pick the distractor.
4. `expectations/` files get written last and reviewed by a second reader (or a fresh session) before landing in the suite.

If this separation is not maintained, the Phase 3 gate becomes a measurement of author taste rather than matcher quality.

**Seeding plan:**

- Phase 3 seeds ~30 match pairs covering the main reasoning-shape categories visible in the 491 tensions and 867 ally/antagonist edges.
- Phase 4 adds ~10 tiebreaker cases — pairs where fan-adjusted affinity is within ε and activation match must pick the winner.
- Phase 5 adds ~10 anti-echo cases — upstream Lane 2 fingerprints that should trigger antagonist suppression.

---

### 14f. Phased rollout

**Phase ordering reason (revised post-audit, REV-1 + REV-2):** plumbing first so no matcher runs against a graph that silently drops fields; then Phase 0.5 measures the actual reasoning-shape purity of Layer 1+2 so later gates calibrate to reality, not aspiration; rendering next because it's pure pass-through and validates the data reached the runtime; tension enrichment runs in parallel because it's pure curation work with no code dependency; tiebreaker (Phase 3) comes before blend (Phase 4) because it's a narrow-blast-radius behavior change that proves the matcher carries signal before generalizing to the full ranking surface; anti-echo last because it depends on high-quality antagonist activation conditions AND the matcher infrastructure being green in real use.

**Bets, not a contract (framing addition from audit):** Phases 0, 0.5, and 1 are near-certain wins — plumbing, measurement, and pass-through rendering with zero selection logic. Phase 2 is disciplined labor. Phase 3 is the actual research bet: the first place activation-match has to prove it carries signal on real data. Phases 4 and 5 are conditional on Phase 3 showing green. Treat Section 14 as a sequence of gated bets — if any phase's gate comes back red, the correct action is to stop and reassess, not to continue under the assumption that later phases will recover the signal.

---

#### Phase 0 — Plumbing (Task #6 lives here)

- **Scope:** carry `affinity_rationale` and `activation_condition` from curation JSON through the compiler into `relationship_graph.json`, then through the loader into the runtime `RelationNeighbor` dataclass.
- **Repos:** `Lolla-system-b` (compiler) + `lolla-skill` (loader + runtime dataclass).
- **Work:**
  - `Lolla-system-b/system_b/compilation_bundle.py` — extend `append_edge` in `_build_wave3_relationship_graph` to accept and write `affinity_rationale`, `activation_condition`. Update both ally and antagonist loops.
  - `lolla-skill/engine/system_b/relation_graph.py` — add `affinity_rationale: str = ""` and `activation_condition: str = ""` to `RelationNeighbor`. Read them in `load()`.
  - Mirror the loader change in `Lolla-system-b/system_b/relation_graph.py` so the two copies stay in sync.
- **Test:** unit test that loads a sample compiled graph and asserts both new fields are present and non-empty on edges derived from Layer 1+2 records. Integration test that runs compilation end-to-end and asserts 100% of ally/antagonist edges in the output carry both fields.
- **Why:** nothing downstream can depend on these fields if they don't reach the runtime. This is mechanical carrying, not logic — the test is purely structural (fields present, correct type, correct pass-through from source).
- **Effort:** Quick-to-Short. No doctrine risk.

---

#### Phase 0.5 — Layer 1+2 doctrine audit (REV-1)

- **Scope:** measure the actual "cognitive move vs situational vs mixed" distribution across the 867 existing ally+antagonist `activation_condition` strings. Do NOT rewrite any of them. The audit produces a calibration baseline, not corrective work.
- **Repo:** audit output lives in `lolla-skill/research/` as `activation_condition_doctrine_audit_2026-04-21.md` (date-suffixed to match the compile).
- **Work:**
  - LLM-driven rating pass over all 867 activation_conditions in compiled `relationship_graph.json` (so Phase 0 must complete first).
  - Rubric per string: one of `{cognitive-move, situational, mixed}`. Record the string and the rating. Keep a short "why" note for situational and mixed cases so tuning later has signal to work from.
  - Aggregate: count per category, histogram per edge type (ally vs antagonist), histogram per source model. The source-model breakdown matters because some curators wrote in tighter reasoning-shape prose than others; the distribution across models shows whether the problem is systemic or concentrated.
- **Test:** deterministic re-run on a 10% subset produces the same categorical ratings on ≥85% of items (LLM-rating noise floor). If re-run agreement is below 85%, tighten the rubric before using the audit as a calibration input.
- **Why:** the first-draft Phase 2 gate demanded ≥95% cognitive-move on tension enrichment. A 20-sample spot check on 2026-04-21 found ~45% clear cognitive move — so 95% was aspirational. Phase 0.5 replaces aspiration with measurement. Phase 2's bar becomes "≥ Layer 1+2 baseline"; the matcher's noise-floor threshold (Phase 3) gets set from this distribution.
- **Effort:** Quick (1-2 hours of compute + rubric tuning). Parallelizable with Phases 0 and 1.

---

#### Phase 1 — Card rendering of `affinity_rationale`

- **Scope:** pickup point #4. The card for a supporting or risk model surfaces the `affinity_rationale` string when available.
- **Repo:** `lolla-skill`.
- **Work:** update the card renderer (follow the `references/output-field-guide.md` format) to include a "why this connection" line sourced from `RelationNeighbor.affinity_rationale`. If the field is empty, omit the line.
- **Test:** snapshot tests against fixture graphs (`tests/fixtures/graphs/`) asserting the rendered card includes the rationale text verbatim for edges that have one, and omits the line for edges that don't.
- **Why:** pure pass-through render, zero selection logic, zero doctrine risk. It validates Phase 0 from the user-facing end (if Phase 0 is wrong, the rationale line is missing or wrong) and immediately delivers visible value.
- **Effort:** Quick.

---

#### Phase 2 — Structured tension enrichment — **SKIPPED 2026-04-21 (REV-6)**

**Decision:** Do NOT run the planned LLM re-read on the 491 tensions. Reasoning below; preserve the original plan text for future reference in case a corpus-side curation pass later changes the input shape.

**Why skipped — the source audit that killed this phase:**

- The 491 tension edges in `data/relationship_graph.json` all come from `Lolla-system-b/curation/relation_semantics/*.json → structured_tensions[]`. Each entry is a single sentence with this exact shape (verified on 491/491): **"X conflicts with Y when Z."**
- The canonical articles (`MM_CANONICAL_216/*_rag.md`, under the section header "Structured Tension Curation") contain the exact same single sentence for each tension — no surrounding prose, no richer explanation behind it. Examples:
  - `abstraction_rag.md:103` → "abstraction conflicts with first-principles-thinking (first principles thinking) when high-level labels hide untested assumptions." → this is literally the `source_quote` in the compiled JSON.
  - `Calculated_Risk_Taking_rag.md:115` → identical pattern.
- Phase 2 as originally scoped would ask an LLM to split that single sentence into `affinity_rationale` + `activation_condition`. The split is mechanical substrings: `affinity_rationale ≈ "X conflicts with Y"` (tautological — relation_type and target_model_id already encode this), `activation_condition ≈ "when Z"` (already inside `tension_text`). Zero information gain. Any additional content would be LLM synthesis, not curator judgment.
- Per the **corpus-is-authority principle** (feedback memory, `feedback_corpus_is_authority.md`, 2026-04-21): if the curator wrote one sentence, rendering one sentence is faithful; inventing a split is corpus manipulation.

**Consequences for downstream phases:**

- Phase 3 (tiebreaker) and Phase 4 (blend) cannot match on tension `activation_condition` because it doesn't exist as a separate field. The matcher will see only ally + antagonist activation_conditions (867 edges instead of 1358). Phase 3 fixtures must be authored with this constraint — no fixture should expect a tension edge to win a tie via activation match.
- Card rendering (Phase 1) already does the right thing for tensions: `tension_text` is surfaced as the connection explanation; no empty `affinity_rationale`/`activation_condition` keys appear in the payload because the serializer omits empty fields.
- The REV-1 "doctrine gate" for Phase 2 is moot.

**If richer tension structure is ever wanted:** the lever is upstream, in curation — a new wave that authors separate `tension_rationale` (why the two models fundamentally conflict) and `activation_condition` (when that conflict matters) sentences per tension, mirroring the ally/antagonist shape. That is a corpus change (a human curation task), not an LLM extraction task. Until such a corpus pass exists, Phase 2 has nothing to extract.

---

**ORIGINAL PLAN (preserved for reference — DO NOT EXECUTE):**

- **Scope:** apply Layer 1+2 enrichment to the 491 structured tensions that currently have no `activation_condition`, `affinity_rationale`, or `affinity_strength`.
- **Repo:** `Lolla-system-b/curation/relation_semantics/` curation files (tensions are stored alongside allies/antagonists).
- **Work:** LLM-driven re-read of each tension's source article in the curator's voice. Batches of ~8. Same rubric and quality bar as Layer 1+2. No scripting shortcuts — thorough route was decided explicitly because tensions carry the subtlest reasoning-shape signal of the three edge types.
- **Test:** two gates (REV-5 revision, supersedes REV-1).
  - **Coverage gate:** 100% of the 491 tensions have all three fields populated.
  - **Faithfulness gate (REV-5, replaces the prior Doctrine audit gate):** random sample of 49 tensions (10%) audited against their source canonical article. For each, every substantive claim in the extracted `affinity_rationale` and `activation_condition` must be traceable to specific prose in the article (quote-level citation). A tension passes if the extraction adds NO content beyond what the article supports and omits no critical qualifier the article carries. Failure modes: content synthesized to sound more cognitive-move than the source ("purification"), conflation of claims from different sections, drift into general commentary. The faithfulness audit is the authoritative gate; rubric-based cognitive-move distributions are measured for calibration only.
  - **Why the change from REV-1:** REV-1's doctrine gate (≥ Layer 1+2 baseline for cognitive-move rate) was opinionated — it implicitly demanded the re-read produce strings matching our rubric regardless of source-article prose. Per the "curated corpus is the authority" principle (feedback memory, 2026-04-21): if the article's tension prose is honestly less cognitive-move than its ally/antagonist prose, a faithful re-read will rate lower, and that's correct. Forcing it to match would be corpus manipulation. The matcher (Phase 3) adapts to whatever distribution comes out, via noise-floor tuning.
  - **Informational calibration measurement (not a gate):** Phase 0.5 rubric (`{cognitive-move, situational, mixed}`) applied to the 49-sample post-extraction so Phase 3 threshold tuning has the tension distribution on hand. Result feeds 14h item 2, not a pass/fail decision here.
- **Why:** tensions are the primary substrate for Lane 3 and some Lane 4 routing. Without enriched tensions, the matcher in Phase 3 would only see ally/antagonist activation conditions — which is half the graph's reasoning-shape surface. Doing Phase 3 first and Phase 2 later would mean Phase 3's fixture set would have to deliberately avoid tension edges, which would distort the tuning.
- **Effort:** Medium-to-Large (1-2 weeks, parallelizable with Phases 0 and 1).

---

#### Phase 3 — Activation-match as near-tie tiebreaker (REV-2: was Phase 4)

- **Scope:** pickup points #1, #2, #3. `RelationGraph.neighborhood()` ranking + router/bundle selection use activation match to break near-ties in fan-adjusted affinity ONLY. The default path (fan-adjusted affinity alone) stays byte-identical outside the near-tie window.
- **Repo:** `lolla-skill` (primary) + `Lolla-system-b` (mirror).
- **Work:**
  - Add the matcher module. Accepts only the typed inputs listed in 14b (`FingerprintPayload`, `TriggeredTendency` / `TendencyRef`, `FrameRoute`, `DimensionRoute`). Signature rejects raw `str` from other sources. If a union type is awkward, use a `ReasoningShapeInput` wrapper class.
  - Compile-time backfill: one-time embedding pass over every compiled edge's `activation_condition` string (see 14d embedding backfill note). Store in a new table alongside `embeddings.db`.
  - Query-time: `neighborhood()` gains an optional `reasoning_context` parameter. When the top-2 candidates' fan-adjusted affinities are within ε (epsilon set from fixture data, see 14h), the tiebreaker picks the higher activation-match. Outside the ε window, activation match is NOT consulted — the default path is unchanged.
  - Noise-floor guard: if top activation-match similarity falls below a threshold (set from Phase 0.5 baseline + fixture data), the tiebreaker abstains and falls back to deterministic ordering (lexicographic, as today).
- **Test:**
  - ~30 fixture match pairs in `tests/fixtures/`, authored under the blind protocol in 14e. ~10 of those are explicit near-tie cases where activation match must decide correctly; ~10 are non-tie cases asserting byte-identical output vs the current default path; ~10 are noise-floor cases where activation match should abstain.
  - Integration gate: re-run 5 existing end-to-end fixtures and confirm outputs are unchanged OR changed in the direction expected by the near-tie cases.
- **Why this is now the FIRST matcher-using phase (REV-2):** the first-draft ordering put ranking-blend before tiebreaker. The audit flipped it. Tiebreaker is narrower blast radius — it only fires inside a quantifiable window, so a bad matcher cannot regress the default path. If the tiebreaker gate is green, Phase 4 (blend) inherits confidence from real data. If the tiebreaker gate is red, we learn that cheaply without having already touched the full ranking function.
- **Effort:** Medium.

---

#### Phase 4 — Activation-match as ranking blend (REV-2: was Phase 3)

- **Scope:** pickup point #1. `RelationGraph.neighborhood()` blends fan-adjusted affinity with activation-match cosine similarity across the full candidate set, not just ties.
- **Repo:** `lolla-skill` (primary) + `Lolla-system-b` (mirror).
- **Gate:** Phase 3 tiebreaker must have landed with the near-tie gate green and at least one live-conversation recompile cycle passed clean.
- **Work:**
  - Extend the ranker from Phase 3: when `reasoning_context` is present, blend cosine similarity with fan-adjusted affinity across all candidates using a weighted formula. Weight tunable per lane.
  - Default blend weight: intentionally left OPEN in 14h. Cannot be set without Phase 3 fixture data showing the signal strength distribution across real matches. The first-draft 0.5/0.5 default was underspecified and is replaced by "set from Phase 3 data" (REV addition).
- **Test:**
  - Promote Phase 3's ~30 fixtures and add ~20 broader ranking cases where the expected winner differs from what fan-adjusted affinity alone would pick. Success criterion: ranking changes in the direction of the expected winner, not wholesale reshuffling.
  - Regression gate: each of the 5 end-to-end fixtures from Phase 3 must either stay unchanged or change with a review-approved rationale.
- **Why:** ranking blend is a bigger surface area of change than tiebreaker. Running it with real Phase 3 signal data (not a guessed 0.5/0.5) makes it calibrated rather than assumed. Running it before Phase 3 validates the signal (REV-2 original ordering) would mean tuning against hypothetical data.
- **Effort:** Short-to-Medium, assuming Phase 3 infrastructure is reused.

---

#### Phase 5 — Anti-echo suppression via antagonist activation match

- **Scope:** pickup point #5. If the upstream Lane 2 fingerprint matches an antagonist's `activation_condition` with high similarity, suppress that antagonist from appearing as a recommended counter-pressure model.
- **Repo:** `lolla-skill`.
- **Work:**
  - Define the suppression threshold (tuned against fixtures).
  - Hook into the Lane 1 risk-model selection path so that antagonists whose activation matches the upstream fingerprint are filtered out before card rendering.
  - Log the suppression event (which model was suppressed, match score, upstream fingerprint) for observability.
- **Test:** ~10 fixture cases where the upstream Lane 2 fingerprint is in model X's failure shape. Assert that model X does not appear in the risk-model list. Assert that model X *does* appear when the upstream fingerprint is different. Assert that the suppression log contains the expected entry.
- **Why:** this is the strongest self-reflexive capability the system will have. It depends on high-quality antagonist activation conditions (Phase 0/1 plumbing + Phase 2 enrichment) and the matcher (Phase 3). Running it before those phases are solid would produce misleading suppression — silently dropping correct recommendations. Doing it last is the only safe order.
- **Effort:** Short-to-Medium.

---

### 14g. Decisions locked on 2026-04-21 (revised post-audit)

- [x] Matching uses embedding cosine (Option B), not keyword overlap or LLM-as-judge.
- [x] Matcher input types are constrained to real codebase types: `FingerprintPayload`, `TriggeredTendency` / `TendencyRef`, `FrameRoute`, `DimensionRoute`. If a union is awkward, use a `ReasoningShapeInput` wrapper. (REV-3 — first draft used invented names.)
- [x] `activation_context` (tendency→model, existing) and `activation_condition` (model→model edge, new) are separate fields at separate layers — disambiguated in 14b, not renamed. (REV-4)
- [x] Testing uses synthetic fixtures in `lolla-skill/tests/fixtures/`, not real `/tmp/lolla_*` captures.
- [x] Three fixture families: `reasoning_shapes/`, `graphs/`, `expectations/`.
- [x] Blind authoring protocol for fixtures (author graphs first, shapes blind to targets, distractors added, expectations reviewed by second reader). See 14e. (REV addition)
- [x] ~~Tension enrichment (Phase 2) uses the thorough route — LLM re-read, batches of ~8, same rubric as Layer 1+2.~~ **SUPERSEDED by REV-6 (2026-04-21): Phase 2 SKIPPED.** Source audit showed all 491 tensions are single-sentence "X conflicts with Y when Z" entries with no richer material behind them in the canonical articles. LLM re-read would synthesize splits the curator never wrote. See Phase 2 block in 14f.
- [x] Phase ordering: 0 → 0.5 → 1 → 3 (tiebreaker) → 4 (blend) → 5. (REV-1 added 0.5; REV-2 swapped old 3↔4; REV-6 removed Phase 2.)
- [x] Phase 0.5 is a measurement phase — audits Layer 1+2's actual cognitive-move distribution, produces the baseline that Phase 2 must match and Phase 3 matcher calibrates against. Does NOT rewrite Layer 1+2 values. (REV-1)
- [x] Phase 2 doctrine audit gate: "≥ Layer 1+2 baseline from Phase 0.5," not a fixed ≥95% target. The matcher noise-floor guard in 14d tuning lever 1 absorbs the situational tail. (REV-1)
- [x] Phase 3 ships activation match as a near-tie tiebreaker ONLY. Default path outside the epsilon window is byte-identical to today's fan-adjusted affinity behavior. (REV-2)
- [x] Phase 4 (ranking blend) is gated on Phase 3 landing green + one live recompile cycle. Blend weight is NOT pre-set; it comes from Phase 3 fixture data. (REV-2, supersedes first-draft 0.5/0.5 default.)
- [x] Embeddings.db backfill is a Phase 3 pre-requisite: one-time embedding pass over 1,358 compiled edges' activation_conditions, ~$2-5 per recompile. Documented in 14d. (REV addition)
- [x] Phase 5 runs last. It is not implemented before Phase 2 is coverage- and audit-passed AND Phase 3 is green.
- [x] Compiler extension in Phase 0 carries both `affinity_rationale` and `activation_condition` on every ally and antagonist edge; ~~structured tensions join that pipeline only after Phase 2 completes.~~ **REV-6: tensions never join this pipeline — Phase 2 skipped. Tensions continue to carry `tension_text` only.**
- [x] **(REV-6, 2026-04-21)** Phase 2 skipped after source audit. Rendering tensions as a single `tension_text` sentence is the faithful representation of what the curator wrote. Revisit only if a corpus-side curation pass produces separate tension_rationale + activation_condition fields per tension.

---

### 14h. Still-open decisions (require data or user input before the relevant phase starts)

Revised after REV-1 and REV-2; first-draft values that were assumed defaults are now explicitly open.

1. **Phase 3 near-tie epsilon.** Cannot be set without Phase 0.5 + initial fixture data showing the distribution of top-2 fan-adjusted affinity deltas on real graph slices. First-draft guess was "TBD"; it stays TBD, to be decided by data.
2. **Phase 3 noise-floor threshold.** Below this cosine similarity, the tiebreaker abstains (falls back to deterministic ordering). Set from Phase 0.5 distribution + fixture data — so that the threshold naturally filters out matches against the ~35% situational activation_conditions from Layer 1+2.
3. **Phase 4 blend weight.** REV-2 removed the first-draft 0.5/0.5 default. Set from Phase 3 fixture data once the signal distribution is known. May end up per-lane.
4. **Phase 5 suppression threshold.** Still cannot be set without Phase 3 fixture data + a separate audit sample of antagonist activation_conditions (separate from the ally-weighted Phase 0.5 sample).
5. **Phase 5 card rendering of suppression.** Whether to surface a small "model X was considered but suppressed because reasoning already in its failure shape" line. Deferred to Phase 5 kickoff.
6. **What to do with mixed/situational activation_conditions from Phase 0.5.** Two forks:
   - **Fork A (preferred per audit):** leave them as-authored; rely on matcher noise-floor to ignore low-signal entries.
   - **Fork B:** targeted rewrites per-edge where a specific match is known to be wanted but the current wording makes the matcher miss. Decision deferred until Phase 3 fixture data shows which edges actually matter.

Any session that touches these decisions should update 14h and 14g accordingly.

---

### 14i. What this rollout does NOT do

This list exists so future sessions don't accidentally fold extraneous work into the rollout.

- **Does not add new curated models.** The 222 stay 222. Closed Vocabulary Principle is not relaxed.
- **Does not change extraction (`run_extract.py`) or any skill Step 1-2 behavior.** Activation matching lives in the engine, not extraction.
- **Does not call an LLM in the live path.** All LLM usage is compile-time (embeddings, Phase 2 enrichment). The query path stays deterministic.
- **Does not implement Layer 3 (4-type interaction taxonomy).** Layer 3 is deferred per Section 0g and remains deferred.
- **Does not change fan correction.** Fan correction and activation matching compose; they do not replace each other.
- **Does not introduce situational/factual matching.** If any phase's implementation starts consuming `vanilla_answer`, extracted quotes, query strings, or any other factual content, the rollout has regressed and must be halted at that phase until the matcher signature is restored.

---

### 14j. Memory and session handover

This plan is persisted in this handover file (Section 14) and in the `MEMORY.md` index as `project_deep_graph_enrichment.md`. Any session continuing this work should:

1. Read this section first.
2. Check which phases are already in progress (via git log / branch state), because this document records the plan, not live execution state.
3. Before starting a phase, verify no prior phase's gate has silently regressed (Phase 0 plumbing intact, Phase 2 audit score still ≥95%, fixture suite still green).
4. Update Section 14g checkboxes as phases land. Move items from 14h to 14g when decisions get made. Never delete items from 14g — only mark them outdated with a dated note if a later decision supersedes them.

The reasoning behind every decision is in 14a-14f. If a future session wants to revisit a decision, the reason block is the starting point — don't relitigate without engaging the original reason.

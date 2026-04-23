# `/lolla` full system audit — 2026-04-23

**Scope:** complete architectural walk of the skill, end-to-end. Every step, every data structure, every named design decision I could extract from code + existing docs. Handover-quality: a cold-start session or new developer should be able to read this and understand the system without conversation context.

**Honesty about depth:** this is architectural-level (not line-by-line line-audit). I read: `SKILL.md`, `HOW_IT_WORKS.md`, the 16 scripts (deeply on `run_extract.py`, `run_pipeline.py`, `stability_check.py`; surface-level on others), and the main modules in `engine/system_b/` (`pipeline.py`, `companion_routing.py`, `frame_pressure.py`, `structural_coverage.py`, `prompts.py`, `tendency_catalog.py`, plus inspection of `knowledge_graph.json` and file inventory for the rest). I did NOT audit every one of the ~80 files in `engine/system_b/` — many are per-tendency adapters following the same shape.

**What this audit answers:**
- What does the system do, end-to-end?
- What are the data structures and how do they flow?
- Which design decisions were made deliberately, which are legacy?
- What trade-offs were accepted and why?
- Where are the gaps?
- What's been improved recently?

**What this audit does NOT answer:**
- Whether the current lane structure is optimal (that's the quality-first pipeline-redesign question the user raised; this audit documents what exists, not what should exist).
- Whether the 25 tendencies and 222 models are the right substrate (they are curated choices, taken as given).
- Whether specific prompts are optimal (prompt quality is case-by-case).

---

## 1. What `/lolla` does, at the highest level

`/lolla` is a reasoning-audit skill. The user has had a conversation with an AI about a strategic decision. `/lolla` reads that conversation, extracts its structure, runs four independent analyses ("lanes") against 222 curated mental models + 25 cognitive tendencies + 15 structural dimensions, and produces:

- **DeltaCard** (Lane 1) — cognitive tendencies that distort the AI's reasoning
- **CompanionCheatSheet** (Lane 2) — mental models active (or violated) in the reasoning
- **FramePressureCard** (Lane 3) — frame-level assumptions in how the question was posed + reframings
- **StructuralCoverageCard** (Lane 4) — MECE dimensions of the problem the answer didn't address
- **RevisedAnswer** (Step 6) — Claude's revised position incorporating all of the above

The design premise: AI conversational reasoning is susceptible to cognitive and structural failures. A separate audit system, run after the fact, can surface those failures in a way the original AI (or user) wouldn't catch alone.

## 2. The 9-step pipeline

From `SKILL.md`, the skill runs as 9 steps. Claude is the orchestrator for the outer steps (1-4, 6-6b, 7-8b, 9); a Python pipeline via OpenRouter handles the semantic work in Step 3.

### Step 1 — Capture (Claude, no code)

Claude writes the conversation from its context into `/tmp/lolla_{RUN_ID}_conversation.txt`. Format:

```
CONVERSATION: N turns, X user messages, Y assistant responses

[Turn 1] USER:
{text}

[Turn 1] ASSISTANT:
{text}
```

Rules: preserve user words verbatim (constraints depend on them); preserve assistant prose verbatim (Lane 2 fingerprinting needs literal substrings); skip tool calls + tool results + system messages.

Truncation rule for very long conversations: keep first 3 turns + last 15 turns.

**Known weakness:** Claude is the only witness. Once the `.txt` is written, there's no way to verify fidelity to the original conversation. If Claude paraphrases while transcribing, downstream treats the paraphrase as ground truth. This is called out in the observations doc as "Capture-faithfulness is unverifiable."

**Partial mitigation:** `capture_manifest` + `capture_health` validators in Step 2 check header-vs-body self-consistency (declared turn counts match actual). `capture_health: critical` (>50% assistant turns missing) short-circuits the pipeline. Header-vs-body is NOT fidelity-to-source, though — it's only internal consistency.

### Step 2 — Extract (Python + OpenRouter)

`scripts/run_extract.py` invokes a single OpenRouter call with a detailed system prompt (`EXTRACTION_SYSTEM_PROMPT`). Output: 6 structured fields + gate decision.

**Gate (`is_strategic`):** filters non-strategic conversations. Definition enumerates business contexts + (as of PR #11, 2026-04-23) personal strategic decisions. Non-strategic → returns decline reason, pipeline stops.

**The 6 fields:**

| Field | Shape | Contract |
|---|---|---|
| `decision_situation` | string (≤200 chars, since PR #4a) | Single declarative sentence, neutral third-person |
| `live_constraints` | list of `{constraint, introduced_turn, status, weight}` objects | Constraint text ≤120 chars terse noun-phrase + state (since PR #1) |
| `synthesized_position` | free-text string | "Latest/most developed recommendation" (vague — PR #3 attempted structured object, reverted) |
| `reasoning_passages` | list of 3-8 literal substrings | Must be character-exact substrings of conversation |
| `original_framing` | string (≤200 chars, since PR #4b) | Anchored to first user turn |
| `dropped_threads` | list of `{thread, raised_by, raised_turn, status, superseded_by}` objects | Unresolved concerns only |

**Validation + fallback behavior:**
- `reasoning_passages` validated as literal substrings. Failures trigger ONE retry with an explicit correction prompt. Remaining fabrications get DROPPED from the output; a `capture_warning` surfaces the count.
- Conversation truncation if >80K chars (keep first 3 + last 15 turns).
- `capture_health: critical` short-circuits before the API call (saves money).

**Design decisions:**
- Monolithic single call — all 6 fields extracted together. This is simple but causes context pollution when adding new rules (confirmed experimentally in PRs #1b, #2, #3).
- Retry-then-drop on fabricated quotes rather than hard-fail. Preserves partial output; surfaces count.
- Gate decision embedded in same call as extraction (not a separate LLM call).

**CritiqueRequest mapping (deterministic, no LLM):** `_map_to_critique_request` collapses the 6 fields into 2:

- `query` = `decision_situation` + constraint summary + `original_framing` + `dropped_threads` summary
- `vanilla_answer` = `synthesized_position` preamble + full assistant text (from conversation, 40K char cap)

**Key design artifact:** the pipeline only sees `query` + `vanilla_answer`. The rich extraction is collapsed into flat text inputs. This means the pipeline lanes do not have direct access to field-level structure (constraint status, dropped_thread superseded_by, etc.) — they have to re-derive it from prose if they need it.

### Step 3 — Pipeline (Python + OpenRouter)

`scripts/run_pipeline.py` loads the pipeline from bundled data and invokes `SystemBPipeline.run(CritiqueRequest(query, vanilla_answer))`. Result is serialized to JSON for Claude to read in Step 4.

Pipeline loads from `data/knowledge_graph.json`:
- **222 mental models** with descriptions, activation conditions, antagonists, prerequisites
- **25 tendencies** (24 canonical + lollapalooza special-cased) with antidote models, core models, related dynamics
- **edges** — relationships between models and tendencies
- **reframing_routing** (Lane 3) — frame-pattern → model lookup
- **prerequisite_edges** — model dependencies
- **structural_coverage_routing** (Lane 4) — 15 MECE dimensions → model lookup

Pipeline architecture (`SystemBPipeline.run`):

1. **Pass 1 — Family-clustered triage** (6 parallel OpenRouter calls)
2. **Embedding swiss-cheese promotion** (optional, if `OPENAI_API_KEY` set)
3. **Triggered tendency selection** (threshold 4 + always-include + embedding hits)
4. **Pass 2 — Deep checks per triggered tendency** (parallel OpenRouter calls, up to 8 concurrent)
5. **Deterministic routing** → corrective models per detection
6. **DeltaCard assembly** (Lane 1 output)
7. **Lane 2 — Companion** (fingerprint → recall → verify → select cheat sheet)
8. **Lane 3 — Frame Pressure** (extract → route → generate reframings)
9. **Lane 4 — Structural Coverage** (classify question → detect dimensions → route gaps → generate questions)
10. **Post-processing (parallel):** revision step (skipped when `--skip-revision` → Claude does it in Step 6) + Bullshit Index

Total OpenRouter calls per extraction: ~15-25, depending on triggered tendency count and embedding availability. Parallel where possible.

Output: large JSON blob with all four cards, audit metadata, boundary-call telemetry, prompt versions, run_health diagnostics.

### Step 4 — Present (Claude, no code)

Claude reads the result JSON + `references/output-field-guide.md`. Produces a chat-output summary following presentation rules from `references/presentation-research.md`:

- BLUF-first (bottom line up front)
- Max 3-5 findings across all lanes
- One bridge sentence per finding (translates abstract pattern to this conversation)
- No template scaffolding, no severity labels, no JSON field names in chat
- Specific anti-bullshit constraints on bridges (no weasel words, no unverified claims)

Also surfaces `run_health` issues if any are material (quote fabrication, truncation, Lane 3 all-dropped, etc.).

### Step 5 — (Placeholder)

Observatory was originally Step 5; deferred to Step 9 so all artifacts are complete.

### Step 6 — Revision (Claude, no code)

Claude produces the revised answer. Uses full conversation context + the four cards from Step 3. This is distinct from the pipeline's built-in revision step (which is skipped via `--skip-revision`).

**Design rationale:** Claude is the stronger model; revision quality matters; skipping the OpenRouter revision step saves cost and gets better output.

Subdivisions:
- Step 6 — Revised answer (markdown)
- Step 6b — Pressure check sub-agents (multiple sub-agents challenge the revision in isolation)
- Step 6c — Apply pressure check results

### Steps 7-8b — Independent pressure check

Additional Claude sub-agents (isolated contexts) challenge the revision from different angles. This is meant to catch failure modes the main pipeline missed.

### Step 9 — Observatory

All artifacts are rendered into a persistent output directory with visualizations. Mostly formatting/presentation.

## 3. The four lanes — detailed architecture

### Lane 1 — Structural Pressure (DeltaCard)

**Purpose:** detect cognitive tendencies in the AI's reasoning. Uses Charlie Munger's "Psychology of Human Misjudgment" framework.

**The 25 tendencies** (from `knowledge_graph.json`): reward-and-punishment, liking-loving, disliking-hating, doubt-avoidance, inconsistency-avoidance, availability-misweighing, deprival-superreaction, etc. Lollapalooza (composition) is special-cased — detected deterministically from Pass 2 compound patterns, not via triage.

**Pass 1 — Family-clustered triage** (`prompts.py`):

Six clusters, running in parallel:
1. **Authority cluster** — authority-misinfluence, social-proof, mere-association, liking-loving, reciprocation (5 tendencies)
2. **Closure cluster** — doubt-avoidance, inconsistency-avoidance, deprival-superreaction, stress-influence (4 tendencies)
3. **Incentive cluster** — reward-and-punishment, envy-jealousy, kantian-fairness (3 tendencies)
4. **Availability cluster** — availability-misweighing, contrast-misreaction (2 tendencies)
5. **Self-regard cluster** — excessive-self-regard, disliking-hating, excessive-self-pity (read code for list)
6. **Residual cluster** — simple-pain-denial, curiosity, twaddle, use-it-or-lose-it, reason-respecting (remaining non-clustered)

Each cluster scores its tendencies 0-10 with cluster-specific confusion guardrails. This is a recent refactor (Track B, Cycle 1) from a single monolithic 25-tendency triage call. Shipped win: Jaccard 0.50 → 0.70.

**Design decision:** family-clustering over monolithic triage because a single LLM trying to score 25 tendencies has attention-competition problems (similar to our extraction-saturation finding, which probably isn't coincidence). Clustering reduces per-call obligation to 3-5 items.

**Pass 2 — Deep checks** (`deep_checks.py` + per-tendency adapters):

For each tendency scored ≥4 in Pass 1 (or marked as always-include, or hit by embedding promotion), a dedicated OpenRouter call does the detailed check. Each call sees ONE tendency's definition + sub-pattern menu + vanilla answer. Context isolation.

Per-tendency adapter files (`*_deep_check_packet_adapter.py`) translate Pass 2 results into structural `sub_pattern` classifications. There are ~20 of these, one per core tendency.

**Deterministic middle — routing** (`routing.py`, `activation_matcher.py`):

For each confirmed detection, the routing layer:
1. Looks up corrective models from the knowledge graph
2. Does 1-hop neighborhood expansion (allies + antagonists)
3. Ranks via fan-adjusted differentiated affinity (rubric 0.70/0.80/0.90/0.95 scores, dampened by `1 / (1 + ln(degree))` at query time to penalize hub models)
4. In the narrow window δ < 0.01 near ties, an activation-matching tiebreaker can swap top-1/top-2 if curator-authored activation_condition embeddings score the reasoning context above noise_floor=0.45

This is complex machinery. It embodies the central design choice: corrective models are chosen deterministically from a curated knowledge graph, not by an LLM. The LLM's job is detection; routing is graph-based.

**DeltaCard assembly** (`pipeline._assemble_delta_card`):
- Top findings get full treatment: challenge_statement, reversal trigger, corrective model, supporting models, tensions
- Secondary findings get one-line summaries
- Compound patterns (multiple tendencies on overlapping evidence) → compound_groups (lollapalooza)

**Pilots (experimental Phase 1 work):** authority, stress, overoptimism bridges. These are partial implementations that promote specific Pass 2 results into richer bundles. Not all tendencies have pilot bridges; this is in-flight work.

### Lane 2 — Companion (CompanionCheatSheet)

**Purpose:** identify mental models active (or violated) in the AI's reasoning. Surface them so the user can name what was and wasn't done.

**Fingerprint extraction** (`run_fingerprint_call`):

One OpenRouter call extracts 3-8 abstract reasoning moves from vanilla_answer. Each move has:
- `reasoning_move` (short label like "anchoring," "second-order consequence")
- `evidence_quotes` (literal substrings from vanilla_answer)
- `evidence_rationale` (why this is the move)
- `confidence`

**No mental model names mentioned** at this stage. The LLM describes moves in plain language.

**Validation** (`validate_fingerprint_moves`):

Each evidence_quote must appear as a substring of vanilla_answer. Exact match preferred; a fuzzy-match fallback (80% token overlap) handles minor paraphrasing. Fabrications (missing match) are dropped.

**Recall** (`recall_candidates`):

Keyword overlap + optional embedding search identifies 15-20 candidate mental models from the 222-model substrate.

**Verify** (`run_verification_call`):

One OpenRouter call per candidate batch asks: is this model EXECUTED (mechanism runs in the answer) or VIOLATED (answer substitutes something the model guards against)? Mere compatibility (vaguely related) = rejection.

**Broad-overlay models** (second-order-thinking, systems-thinking, power-laws, butterfly-effect, multi-criteria-decision-analysis) get extra scrutiny — they fit everything if you squint, so verification bar is higher.

**Cheat sheet selection** (`companion_selection.py`):

Deterministic retrieval of curated chunks (failure modes, premortems, heuristics, antagonists) for verified models. Anti-echo filtering drops heuristic chunks for models already in the DeltaCard (Lane 1). Budget-constrained selection (20 chunks max, diversity guaranteed).

**Design choice:** Lane 2 does NOT use the extraction's `reasoning_passages` directly. It extracts its own moves from vanilla_answer. The extraction's reasoning_passages are auxiliary observability, not a direct input. This is a design redundancy worth noting — two different extractions of "key reasoning passages" run across the pipeline.

### Lane 3 — Frame Pressure (FramePressureCard)

**Purpose:** audit the QUERY (not the answer) for embedded assumptions, mutable constraints, suppressed counterfactuals.

**Frame extraction** (`run_frame_extraction`):

One OpenRouter call reads the query. Returns 0-5 `frame_elements`, each with:
- `element_type`: "assumption" | "mutable_constraint" | "suppressed_counterfactual"
- `evidence_quote` (literal substring of query)
- `frame_pattern` (from curated taxonomy — see `knowledge_graph.reframing_routing`)
- `fragility_signal` (what would break this element)
- `inquiry_stage`: "why" | "what_if" | "how"
- `likely_default`: "ego" | "social" | "inertia" | "emotion" | "none"

**Validation:** evidence_quote must be literal substring of query; frame_pattern must be in curated taxonomy. Elements failing either are dropped (tracked in `dropped_frame_elements`).

**Deterministic routing** (`route_frame_elements`): each frame_pattern → candidate model_ids from `reframing_routing` table.

**Reframing generation** (`generate_reframings`):

One OpenRouter call generates up to 2 alternative questions. Each has:
- `reframed_question`
- `what_opens` (reasoning path that becomes available)
- `reframe_move_type`: "inversion" | "perspective_shift" | "scope_expansion" | "constraint_relaxation"
- `grounding_model` (model_id that drives it)

**Anti-echo:** models already used in Lane 1 are excluded. Overlap between frame patterns and Lane 1 pressure concepts is flagged.

**Design decision:** Lane 3 specifically ignores the vanilla_answer. It operates on the question as a reasoning artifact itself. This is what distinguishes it from Lane 1.

**Known weakness (from PR #1 diagnostic):** when `original_framing` is unstable (first user turn is a context-dump rather than a clean question), Lane 3's extraction is noisy.

### Lane 4 — Structural Coverage (StructuralCoverageCard)

**Purpose:** proactive — not "what went wrong" but "what structural territory did the answer never enter?"

**Question classification** (LLM call 1):

Classifies the question into one of 4 types:
- causal-diagnosis ("why is this happening?")
- decision-evaluation ("should we do this?")
- action-planning ("how do we do this?")
- prediction ("what will happen?")

Type gates which of the 15 dimensions can fire.

**Dimension detection + coverage check** (LLM call 2):

One OpenRouter call examines the question + answer against 15 MECE dimensions. Each dimension has:
- cleaving_frame (e.g., "Lock-in vs Optionality" for Commitment & Reversibility)
- detect_when conditions
- coverage_signals (what "addressing this dimension" looks like)
- materiality_test (whether a gap could change the recommendation)

Strict coverage bar: dimension is "covered" only if answer explicitly identifies the tension, reasons through both sides, reaches a position. Mere mention ≠ coverage.

Hard cap of 5 gaps; code-level safety net `_MAX_GAPS=5` demotes excess.

**The 15 dimensions** (from `structural_coverage_routing` in knowledge_graph):
- Resource Allocation (Supply vs Demand)
- Incentive Alignment (Principal vs Agent)
- Competitive Dynamics (Collaborate vs Compete)
- Commitment & Reversibility (Lock-in vs Optionality)
- Information Asymmetry (Signal vs Noise)
- (read HOW_IT_WORKS.md for full list)

**Deterministic routing:** each uncovered dimension → candidate model_ids from Wave-6 structural_coverage_routing table (82 bridges across 74 unique models). Anti-echo excludes models from Lanes 1, 2, 3.

**Gap question generation** (LLM call 3, conditional):

For each gap with routed models, generates 2-3 discovery questions following 5Ws+H framework (who, what, where, when first; why last). Questions are:
- Problem-specific (grounded in THIS decision)
- Plain language
- Answerable only by the decision-maker (HITL bridge)

Fires only when gaps exist. Zero gaps → no LLM call.

**Design decision (informative-only):** Lane 4 doesn't influence Lanes 1-3, doesn't change the DeltaCard, doesn't alter companion routing. It sits at the end. Even imperfect gap detection is valuable because the gap QUESTIONS — not the coverage labels — are the product.

## 4. Supporting infrastructure

### Boundary provider (`boundary_provider.py`)

Abstraction over LLM APIs. Two providers implemented: OpenRouter (default, for pipeline work) and OpenAI (for embeddings). Every LLM call goes through a boundary client, which tracks:
- prompt_tokens, completion_tokens, total_tokens
- cached_tokens, cache_write_tokens
- reasoning_tokens (if model supports reasoning)
- status (success, error)

**Why:** observability. Every call's cost is trackable. The `boundary_calls` list in audit output is how we know cost and where the time went.

### Embedding retriever (`embedding_retriever.py`, `edge_activation_store.py`)

Optional layer, active if `OPENAI_API_KEY` set. Two uses:
1. **Swiss-cheese promotion** (Lane 1 Pass 1): embeds vanilla_answer, compares against 25 pre-computed tendency guidance vectors. Promotes tendencies below LLM threshold but above embedding threshold.
2. **Activation tiebreaker:** in narrow near-ties (δ<0.01) between two candidate models, embeds the reasoning context and checks curator-authored activation_condition embeddings. Noise floor 0.45.

**Database:** `data/embeddings.db` (SQLite), pre-computed offline from the curation corpus.

**Design decision:** embeddings are OPTIONAL. Pipeline runs without them via deterministic keyword matching. When available, they add a second signal. This is "Swiss cheese" — multiple overlapping detection layers where each catches what the others might miss.

### Bullshit Index (`bullshit_index.py`)

Parallel post-processor. Evaluates vanilla_answer for:
- unverified confident claims
- paltering (technically-true-but-misleading)
- weasel words / hedging
- other rhetoric patterns

One OpenRouter call, parallelized with the revision step. Context comes from a fact registry built from extraction (decision_situation + constraints + dropped_threads), or raw conversation truncation as fallback.

### Telemetry (`telemetry.py`)

Optional. When enabled (`enable_telemetry=True` + `telemetry_db_path` set), every run produces a telemetry record with timings, tokens, routing decisions, prompt version hashes. Used for evaluation and regression tracking.

### Relation graph (`relation_graph.py`)

Data-loader abstraction over `knowledge_graph.json` edges. Lets the routing layer query the graph for neighbors, antagonists, allies without re-parsing JSON.

### Tendency catalog (`tendency_catalog.py`)

Lookup + normalization for the 25 tendencies. Handles aliases (e.g., "authority" → "authority-misinfluence-tendency"), overlay routing, display names.

### Compound catalog (`compound_catalog.py`)

Lollapalooza compound patterns. Known combinations of tendencies that amplify each other. E.g., authority + social-proof + commitment might form a "coerced-consensus" compound. When multiple Pass 2 detections appear on overlapping evidence, compound detection looks them up here.

### Pressure bundle selector (`pressure_bundle_selector.py`, `pressure_router.py`)

Selects curated chunks (failure modes, heuristics, premortems) from the curation corpus based on routed models. Used by Lane 1 DeltaCard assembly and Lane 2 cheat sheet selection.

### Compiled substrate (`compiled_substrate.py`)

The 222-model curation corpus, compiled into searchable chunks. Loaded at pipeline init. Heavy — ~thousands of chunks across all models.

## 5. Data catalogs — what the system draws on

| Catalog | Count | Source | Used by |
|---|---|---|---|
| Mental models | 222 | `knowledge_graph.json` → `models` | Lane 1 routing, Lane 2 verify, Lane 3 reframing, Lane 4 coverage |
| Tendencies | 25 (24 canonical + lollapalooza) | `knowledge_graph.json` → `tendencies` | Lane 1 (Pass 1 + Pass 2) |
| Structural dimensions | 15 MECE | `knowledge_graph.json` → `structural_coverage_routing` | Lane 4 |
| Frame patterns | ~dozens | `knowledge_graph.json` → `reframing_routing` | Lane 3 |
| Compound patterns | several | `compound_catalog.py` | Lane 1 lollapalooza detection |
| Activation conditions | per model | curator-authored, embedded offline | tiebreaker routing |
| Curation chunks | thousands | `data/curated/` + `data/curation/` | Pressure bundle selection |

## 6. The 9-step flow end-to-end (compact)

```
USER conversation
    │
    ▼
Step 1 [Claude] Write to /tmp/lolla_{rid}_conversation.txt
    │
    ▼
Step 2 [Python+OpenRouter] run_extract.py → /tmp/lolla_{rid}_extraction.json
    │   (6 fields + gate decision + capture diagnostics)
    ▼
Step 3 [Python+OpenRouter] run_pipeline.py → /tmp/lolla_{rid}_result.json
    │   ┌─ Lane 1: Pass 1 (6 parallel cluster calls) + Pass 2 (per-tendency)
    │   ├─ Lane 2: fingerprint + recall + verify + select
    │   ├─ Lane 3: frame extract + route + reframe
    │   ├─ Lane 4: classify + detect + route + gap-questions
    │   └─ Post-parallel: Bullshit Index (revision skipped — Claude does it)
    ▼
Step 4 [Claude] Read result, present BLUF chat summary
    │
    ▼
Step 5 [placeholder — deferred to Step 9]
    │
    ▼
Step 6 [Claude] Revised answer (uses full context + cards)
    │   6a: Revision text
    │   6b: Pressure-check sub-agents challenge revision
    │   6c: Apply pressure-check results
    ▼
Steps 7-8b [Claude sub-agents] Independent pressure check
    │
    ▼
Step 9 [Claude] Observatory — render all artifacts
```

**Who does what:**
- Claude: orchestration, capture, presentation, revision, pressure-check sub-agents, observatory
- Python + OpenRouter: extraction, pipeline lanes, BI, revision (optional — currently bypassed)
- Python + OpenAI: embeddings (optional)

## 7. Major design decisions and their rationales

### Decision: Claude as orchestrator, not the pipeline
**Why:** Claude has full conversation context; the Python pipeline doesn't. Claude also produces better presentation prose. The Python pipeline handles semantic-extraction tasks that need calibrated prompts + deterministic routing; Claude handles anything that needs fluency or contextual judgment.

**Trade-off accepted:** two execution contexts (Claude + Python). Complicates testing; you can't test the "full skill" end-to-end without running both. The `--skip-revision` flag acknowledges this split explicitly.

### Decision: Monolithic extraction (Step 2)
**Why:** simplicity. One LLM call, one output, one file. Easy to reason about.

**Trade-off accepted:** context pollution when adding new extraction rules. Confirmed experimentally in PRs #1b, #2, #3 (all paused with saturation evidence).

**Future path:** Track A decomposition — split into 2-3 specialist calls for high-impact fields (reasoning_passages, live_constraints, synthesized_position). Deferred.

### Decision: 6 extraction fields, collapsed to `query` + `vanilla_answer` via deterministic mapping
**Why:** pipeline lanes need simple inputs. Structured fields are useful observability but the lanes consume flat text.

**Trade-off accepted:** information loss. Constraint status, dropped_thread superseded_by reason, turn timestamps — all present in extraction, absent from pipeline input. Lanes have to re-derive any of this from prose.

**Implication:** the user's reverse-requirements insight applies here strongly. Extraction is producing richer output than lanes consume.

### Decision: 4 lanes, each independent
**Why:** lanes detect different classes of reasoning failure; independence makes each one testable, composable, and removable.

**Trade-off accepted:** lanes sometimes have overlapping findings (Lane 1 + Lane 3 can both flag "framing" issues). Anti-echo reduces duplication but doesn't fix the conceptual overlap.

**Open question:** is 4-lane the right decomposition, or is it legacy? (User raised this explicitly. Audit doesn't answer — would need quality-first pipeline redesign.)

### Decision: Family-clustered Pass 1 (6 parallel calls) vs monolithic
**Why:** Munger-style monolithic 25-tendency triage has attention-competition problems. Clustering by conceptual family (Authority, Closure, Incentive, Availability, Self-regard, Residual) reduces per-call obligation and gives cluster-specific confusion guardrails.

**Shipped:** Track B refactor, Cycle 1. Measurable win (Jaccard 0.50 → 0.70).

**Generalizes:** the same architectural pattern (split a monolithic LLM call into parallel specialists to reduce attention competition) is what Track A proposes for extraction.

### Decision: Deterministic routing over LLM-suggested models
**Why:** the 222 models + 25 tendencies are curated. Routing decisions are too important to delegate to an LLM that might invent or overlook. The knowledge graph encodes curator intent (which corrective model is RIGHT for each detection). LLMs detect; the graph routes.

**Trade-off accepted:** the system cannot "discover" new corrective relationships beyond what's curated. Novel combinations wait for curator updates.

### Decision: Fan-adjusted differentiated affinity ranking + activation tiebreaker
**Why:** hub models (like "systems-thinking" or "second-order-thinking") fit everything vaguely. Fan correction (`1 / (1 + ln(degree))`) penalizes their raw affinity so specific models surface on specific problems. Activation tiebreaker (in narrow δ<0.01 windows) uses curator-authored activation_condition embeddings to pick between near-ties.

**Trade-off accepted:** complexity. This machinery is hard to explain and hard to verify. But it ships because the default (high-fan models always win) was dominating outputs with generic models and making Lane 1 feel shallow.

### Decision: Anti-echo across lanes
**Why:** Lane 2 could verify the same mental models Lane 1 already routed to. Lane 3 could reframe using models Lane 1 already used. This makes outputs feel redundant. Anti-echo excludes already-used models from subsequent lanes.

**Trade-off accepted:** sometimes the "right" model for Lane 3 is the one Lane 1 used. Anti-echo excludes it, forcing a second-best choice. Current bar: aesthetic diversity over per-lane optimality.

### Decision: Bullshit Index as parallel post-processor
**Why:** BI is orthogonal to Lane 1/2/3/4 — it operates on the whole vanilla_answer, not on structural failures. Running it in parallel with revision saves wall time. It's always-on.

**Trade-off accepted:** every extraction call now includes a BI call. Cost contribution: ~1 call per pipeline run.

### Decision: Retry-then-drop on fabricated quotes
**Why:** hard-fail on fabrications would decline runs on otherwise-good conversations. Retry-then-drop salvages partial output. Surfaces the count so downstream Lane 2 knows it has less to work with.

**Trade-off accepted:** silent degradation. A run with 2 fabrications drops 2 passages and proceeds, possibly with weaker Lane 2 output. The `quote_fabrication` run_health signal mitigates this by surfacing to Step 4.

### Decision: Claude produces the revised answer (not OpenRouter)
**Why:** Claude has full conversation context; Opus 4.7 > grok-4.1-fast on nuanced synthesis. Claude can also skip the pipeline's revision prompt and substitute its own judgment.

**Trade-off accepted:** two different revision codepaths (pipeline's + Claude's). The `--skip-revision` flag is the seam.

## 8. Legacy vs intentional — where the system shows its history

Things that look LEGACY (historical contingency, not current optimum):

- **The single-call extraction** — known saturation, awaiting Track A decomposition. Shipped as-is because decomposition is substantial work.
- **`synthesized_position` as free-text string** — the observations doc proposed a structured `Position` object (stance enum + mechanical anchor). PR #3 attempted this and reverted due to pollution. Remains free-text for now.
- **`reasoning_passages` as auxiliary** — Lane 2 doesn't use them directly. They exist because Step 6 (Claude) quotes them in revision + for observability. But the actual pipeline lane does its own fingerprint extraction.
- **`_map_to_critique_request` collapsing 6 fields to 2 strings** — information-lossy bottleneck. Lanes re-derive what they need from flat text.
- **The 15 MECE dimensions as a fixed taxonomy** — doesn't adapt to decision type beyond the 4 question-classes. Real strategic decisions have more or different dimensions.
- **Pilot bridges (authority, stress, overoptimism) as partial implementations** — not all tendencies have them, not consistent coverage.
- **Step 5 as a placeholder** — vestige of earlier design.
- **Per-tendency packet adapters** — ~20 files doing similar mapping work. Could be consolidated; currently individualized because each tendency's sub-patterns were curated separately.

Things that look INTENTIONAL (deliberate design, not legacy):

- **Claude as orchestrator (Steps 1, 4, 6, 7-9)** — Claude has context + better prose.
- **Python + OpenRouter for pipeline semantic work (Step 3)** — calibrated prompts, parallelizable, cost-trackable.
- **Family-clustered Pass 1** — deliberate refactor from monolithic.
- **Anti-echo** — explicit choice of diversity over local optimality.
- **Fan correction + activation tiebreaker** — explicit choices to prevent hub-model dominance.
- **Bullshit Index as parallel post-processor** — always-on, low-latency impact.
- **Deterministic routing over LLM-suggested models** — explicit curator-vs-LLM boundary.
- **Four lanes with anti-echo between them** — deliberate decomposition; each lane is testable alone.
- **Embedding as optional, not required** — pipeline must work without it.
- **Capture diagnostics (manifest + health)** — explicit observability, shipped silent-degradation fixes.

## 9. Known trade-offs currently accepted

1. **Silent capture-fidelity risk.** Claude writes the conversation from its own context. No source-of-truth comparison exists. Trade-off: capture is fast and flexible vs no verification. Partial mitigation: header-vs-body internal consistency check.

2. **Context pollution in the monolithic extraction prompt.** Adding extraction rules hurts adjacent fields. Trade-off: simplicity now vs Track A complexity later.

3. **Information loss in `_map_to_critique_request`.** Rich structured fields collapse to flat text for the lanes. Trade-off: lane simplicity vs structured context availability.

4. **Lane 2's double extraction.** Extracts its own fingerprint moves instead of using `reasoning_passages`. Trade-off: Lane 2 can ask different questions of the text, but we run two extractions doing related work.

5. **Anti-echo dropping "right" models from later lanes.** Trade-off: output diversity vs per-lane optimality.

6. **`--skip-revision` split.** Two revision code paths (pipeline's + Claude's). Trade-off: Claude's output is better vs one fewer code path.

7. **Hub-model dominance before fan correction.** Fan correction is a patch on a pre-existing problem. Trade-off: accept complexity of the correction vs accept generic outputs.

8. **Embedding is optional.** Missing it degrades accuracy silently (swiss-cheese promotion and tiebreaker both off). Trade-off: skill runs for users without OpenAI API key vs always-on dual-signal.

9. **Bullshit Index always runs.** One additional call per extraction regardless of whether BI surfaces anything useful. Trade-off: consistency of output vs cost savings.

10. **25 tendencies as a fixed Munger-derived set.** Novel cognitive failures that don't match the 25 are invisible. Trade-off: curated rigor vs pattern-matching completeness.

11. **15 MECE dimensions as fixed.** Decision-type-adaptive dimensions would be more flexible. Trade-off: stable curation vs contextual fit.

12. **Personal strategic decisions nearly got excluded** (strategic-gate bias) — recently fixed in PR #11. Gate text needed explicit inclusion. Trade-off: business-shaped prompt originally, now both.

## 10. What we've recently changed (in PR #13, the feature branch)

The following improvements are shipped on `feat/extraction-contract-phase-1-live-constraints`, awaiting merge:

**Step 2 (extraction) changes:**
- ≤120-char terse-form rule on `live_constraints.constraint` (PR #1). Cross-capture exact-text Jaccard 0.010 → 0.109 (10×).
- ≤200-char terse-form rule on `decision_situation` (PR #4a). Similarity 0.335 → 0.838 (2.5×).
- First-turn anchor + ≤200-char rule on `original_framing` (PR #4b). Similarity 0.209 → 0.340.
- Strategic-gate expanded to include personal strategic decisions (PR #11). Previously declined `parenting_teen` + `friendship_money` now pass.
- Python-side canonical_key slug validator (pre-wired, inactive — field deferred).
- Harness extensions: embedding-cosine metric, `--from-extractions` mode, `invalid_key_rate`, canonical_key Jaccard.

**Paused work (architectural unblock needed):**
- `live_constraints.canonical_key` field — PR #1b. Two iterations confirmed prompt saturation. Deferred to Track A.
- `dropped_threads.canonical_key` + tie-break — PR #2. Similar saturation. Deferred.
- `synthesized_position` as Position object — PR #3. Terse-rule alone regressed target field; structural change needs specialist call. Deferred.
- `reasoning_passages.move_type` enum — PR #5. Not attempted; same class of change. Deferred.

**Doctrine insights captured in the roadmap:**
- Cross-capture (36 pairs) > Mode C N=5 (10 pairs) for acceptance gates.
- Exact-text Jaccard is wrong for slug/enum/canonical fields — use embedding cosine.
- Context pollution is real and observable; budget-balance prompt additions.
- Terse-form rule compounds across fields when applied to verbose-baseline free-text.
- Gate-text expansions have lower pollution risk than field-text expansions.

**Test corpus:** 10 synthetic cases covering variance dimensions (`/research/test-cases/`). After gate fix: 10/10 pass extraction. Evidence in `CORPUS-SUMMARY-2026-04-23-v2.md`.

## 11. Identified gaps in current understanding

Things I did NOT fully audit (bandwidth limits):

- **Per-tendency adapter files** (~20 of them). They follow the same pattern but each carries tendency-specific sub-pattern mappings. Would need per-file read to verify consistency.
- **Pilot bridges (authority, stress, overoptimism)** — partial implementations with non-obvious status. What's promoted, why, how the bundles are assembled beyond the main path.
- **Activation matcher internals** — I know the tiebreaker exists and what it does conceptually, but the embedding-matching logic inside `activation_matcher.py` wasn't read line-by-line.
- **Relation graph queries** — neighborhood expansion rules, 1-hop depth choice, antagonist vs ally handling.
- **Novelty scorer** — referenced in file inventory, not explored.
- **Higher-order composition compiler preview** — file exists, purpose unclear.
- **Intervention semantics** — files exist, relationship to other modules unclear.
- **Operational curation + operator summary** — purpose and integration point unclear.
- **Testing harness** — I saw the shape (`testing_harness.py` has `build_case_generation_prompt`, `summarize_expectation_comparisons`) but didn't run it or understand its full purpose beyond that it's used for internal testing.
- **Observatory (Step 9)** — the rendering layer. I know it exists; I haven't read its implementation.
- **`archive_run.py`, `render_memo.py`, `inspect_run.py`** — operational scripts. Usage and output formats not audited in detail.

Quantitative unknowns:
- **Total cost per `/lolla` run.** Can estimate: ~20-30 OpenRouter calls × ~$0.001-0.005 each = ~$0.05-0.15 per run. Plus Claude's orchestration time. Not directly measured here.
- **Latency.** ~20-60 seconds per run based on observed extraction times in our work. Not systematically measured.
- **Cache hit rate on OpenRouter.** Prompt caching is configured (reasoning_tokens, cached_tokens in telemetry) but effectiveness unmeasured.

## 12. Open strategic questions (for quality-first work)

These are inherent design questions this audit surfaces but doesn't answer. They're the ones a quality-first pipeline redesign would tackle.

### Lane structure
- Are 4 lanes the right decomposition? Might quality require 3 or 6?
- Does Lane 2 add value proportional to its cost, given it re-extracts from vanilla_answer?
- Is Lane 4 (proactive coverage) the right intervention, or should gap-finding happen per-lane rather than as its own pass?
- Is the anti-echo policy helping or hurting quality (preferring diversity over per-lane best)?

### Substrate
- Are 222 mental models the right substrate for matching? How much of the 222 does the system actually use? Could we trim to 100 with no quality loss?
- Are 25 tendencies the right taxonomy? Missing patterns? Redundant patterns?
- Are 15 MECE dimensions the right structural taxonomy? Decision-type-adaptive sets might fit better.

### Prompt strategy
- Is family-clustered Pass 1 (6 parallel calls) optimal, or would 3 or 12 be better?
- Does Pass 2's context isolation help as much as the theory says? Are there tendencies that share evidence where batching would help?
- Are calibration prompts optimized per-tendency, or is there a baseline shape that dominates?

### Architecture
- Is the `query + vanilla_answer` bottleneck the right lane-input shape, or should lanes see richer structure?
- Is Track A (specialist extraction calls) the right architectural move, or is a different decomposition cleaner?
- Is Claude-as-orchestrator the right split, or should the Python pipeline have more responsibility?

### Observability
- Does `run_health` surface the right failure modes? We added `quote_fabrication` and `lane3_all_dropped` recently; what else is silently degrading?
- Is telemetry sufficient for long-run quality tracking? Is it actually collected and reviewed?

### Measurement
- Our Mode C and cross-capture metrics tell us extraction stability. Do we have measurements for lane output quality? Delta card finding quality? Companion cheat sheet relevance?
- Is human qualitative review of outputs happening systematically, or only ad-hoc?

## 13. Two meta-observations

**The system is richer than most people using it would expect.** 80+ engine files, 2200-line `pipeline.py`, 222-model substrate, 15 dimensions, fan-adjusted differentiated affinity, activation tiebreakers, embedding swiss-cheese, parallel post-processors, optional telemetry. A lot of machinery is doing work. Quality-first pipeline redesign would need to understand what each piece contributes, what would break if removed, what's vestigial.

**The design philosophy is "multiple overlapping signals," not "one best signal."** Swiss-cheese pattern (Lane 1 triage + embedding promotion), fan correction + tiebreaker (two routing signals), Lane 1 + Lane 2 on the same text with different angles, anti-echo across lanes. The system is explicitly NOT trying to find the one true answer; it's trying to make it hard for any single failure mode to slip through. That's a coherent design choice. Quality-first redesign should decide whether to preserve that philosophy or move toward a simpler "one well-tuned signal" approach.

## 14. Current shipped state (end of 2026-04-23)

- PR #13 open on `feat/extraction-contract-phase-1-live-constraints` with:
  - 3 shipped extraction improvements (terse-form rules on 3 fields + gate fix)
  - Embedding-cosine infrastructure for canonical_key work (pre-wired, inactive)
  - Complete documentation of paused work and its unblock path
  - 10-case diagnostic corpus with gate-fixed Mode C results
  - Forward-plan task files for each remaining roadmap item

- All shipped changes are additive / prompt-only / validator-only; rollback via commit revert.

- Main branch unchanged since last merge (`3c609a5`). PR #13 is the pending change.

- Extraction contract roadmap (`research/extraction-contract-roadmap.md`) reflects paused PRs with Track A as the structural unblock.

## 15. References

- `SKILL.md` — the orchestration contract for Claude (9 steps, model requirements, presentation rules).
- `HOW_IT_WORKS.md` — the architecture overview (pipeline diagram, lane details, tendency taxonomy).
- `research/extraction-contract-roadmap.md` — PR roadmap with per-PR scope and status.
- `research/extraction-contract-observations-2026-04-22.md` — normative spec for extraction contract.
- `research/llm-decomposition-handover.md` — Cycle-1 handover context.
- `research/test-cases/CORPUS-SUMMARY-2026-04-23-v2.md` — 10-case diagnostic corpus results after gate fix.
- Per-PR task files in `tasks/tasks-extraction-contract-*.md`.
- This audit (`research/full-system-audit-2026-04-23.md`) — the handover-quality architectural snapshot.

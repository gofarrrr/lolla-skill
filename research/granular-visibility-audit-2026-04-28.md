# Granular Visibility Audit — Two-Case Investigation (2026-04-28)

**Cases under investigation.**
- `mother-deciding-protect-year/20260428T093545Z` — parenting/safety crisis, 12-turn conversation
- `mid-level-consultant-report-1/20260428T110004Z` — whistleblower decision, 14-turn conversation

**Question driving this audit.** "When the system picks 60 candidate models and ends with 5, I want to know which 60 were picked, why each of the 55 was rejected, what models the system *didn't* even consider, and which models are pulling the most weight on the final recommendation."

**Method.** Audit every deterministic decision point across the four lanes plus extraction. For each, document: what's recorded today, what's discarded, what infrastructure is needed to make the discarded part observable. No code changes — this is the surveying that has to happen before Observatory work.

**TL;DR — the surprising finding.** Most of what you want to see is *already in the result.json*, sitting in `audit_summary` fields that the chat output and the React SPA never render. The Observatory work is therefore split into three buckets:
1. **Surface what's already captured** (largest bucket — `audit_summary` has 21 substantive fields, the SPA references ~6 of them)
2. **Capture what's discarded but easy to add** (medium bucket — Pass 1 raw responses, embedding sub-threshold rankings, deep-check reasoning text)
3. **New telemetry the system has never recorded** (smallest bucket — `raw_message_content` per call, dimension classifier reasoning, expansion-graph traversal rationales)

Below: per-lane funnel, then cross-cutting findings, then the prioritized work list.

---

## Lane 1 — Pass 1 + Pass 2 (tendency selection)

### What the system does

1. The tendency catalog has **24 tendencies** organised into 6 family clusters (authority, closure, incentive, availability, self_regard, residual).
2. **Pass 1**: 6 parallel LLM calls (one per cluster) score every tendency in that cluster on the conversation. Each tendency gets `score: int, evidence: str`.
3. **Triage threshold**: 4. Tendencies scoring ≥ 4 are promoted to Pass 2.
4. **Embedding promotion (Swiss cheese)**: in parallel, the top-25 tendencies by embedding cosine-similarity to the assistant text are checked; any with score ≥ 0.30 that triage missed get added as `source="embedding"` triggers. Threshold defined in `engine/system_b/pipeline.py:1048`.
5. **Pass 2**: each triggered tendency gets a dedicated deep-check LLM call that returns `DeepCheckResult(detected: bool, sub_pattern: str, ...)`.
6. **Routing**: detected tendencies pass through `route_deep_check_results` (`engine/system_b/routing.py:115`) — the filter is literally `if not result.detected: continue`. Survivors become `delta_card.detected_tendencies` and produce `DeltaFinding` entries.

### Funnel observed in our two runs

| Stage | Mother | Consultant |
|---|---|---|
| Catalog scored (Pass 1) | 24 | 24 |
| Non-zero triage scores | 1 (disliking-hating: 2) | 7 |
| Triage hits ≥ 4 | 0 | 2 (authority: 5, reward/punishment: 8) |
| Embedding hits ≥ 0.30 | 0 | 2 (inconsistency-avoidance: 0.34, stress-influence: 0.31) |
| Total Pass 2 calls | 0 | 4 |
| Pass 2 detected = True | 0 | 2 |
| Final `detected_tendencies` | 0 | 2 |

### What's already in `audit_summary` (Lane 1)

| Field | Content | Useful for |
|---|---|---|
| `triage_scores` | All 24 tendencies with `tendency_id`, `score`, `evidence` | "What did Pass 1 see for tendency X?" |
| `triggered_tendencies` | Tendency IDs that fired Pass 2 | "Which tendencies got the deep-check?" |
| `triggered_tendency_sources` | Each trigger with `source: "triage"\|"embedding"\|"always_include"` and `score` | "Was this Pass 2 call from triage or embedding promotion?" |
| `deep_check_results` | Per-tendency `tendency_id, detected, sub_pattern, reasoning` | "Did Pass 2 confirm or reject?" |
| `routing_decisions` | For each detected tendency: `primary_model_id`, `antidote_model_ids`, `tiebreaker_*` | "Which mental models did the routing layer attach to this tendency?" |

**This is comprehensive Lane 1 visibility — already captured per-run, never surfaced.**

### What's discarded today

| Discarded | Why it matters | Cost to add |
|---|---|---|
| The **raw LLM JSON response** for each Pass 1 cluster call | Couldn't verify why Pass 1 returned `score=0` for a tendency that should have triggered, without re-running. The `evidence` field is parsed from this; the rest of the cluster's reasoning is lost. | Small — capture `boundary_call.raw_message_content` (already in metadata, just not persisted; see "Per-call telemetry" below) |
| The **full 25-tendency embedding rank** (with sub-threshold scores) | "Tendency X had embedding score 0.28 — close call." Currently you only see the ones above 0.30. | Small — return the full rank from `_embedding_tendency_signal` instead of the threshold-filtered subset |
| The **`reasoning` text from each `DeepCheckResult`** | Field exists in the dataclass but persists empty in our runs (you'd see *why* Pass 2 said `detected=False` for inconsistency-avoidance and stress-influence). | Small — populate the field at deep-check return; see if individual deep_check adapters write reasoning |

---

## Lane 2 — Companion (mental-model anchors)

### What the system does

1. **Fingerprint LLM call**: parses the assistant text into `reasoning_moves` — discrete reasoning steps with evidence quotes (mother: 7 moves; consultant: 7 moves).
2. **Recall (candidate generation)**: for each reasoning move, recall up to ~60 candidate mental models via keyword matching (and possibly embedding rerank — see "What we don't see" below). Both runs returned exactly **60 candidates** (capped, source: 100% keyword in both runs).
3. **Verification LLM call**: the verifier reads the conversation + the 60 candidates and returns a per-candidate verdict: accept (with evidence quote + presence_mode + presence_explanation), reject (with `rejection_reason`), or omit silently.
4. **Dedupe + cap**: accepted entries are deduplicated by `model_id` (duplicates land in `duplicate_accepts`); the survivors are capped at top-5 (overflow lands in `capped_models`). The cap is named `_DETECTED_MODELS_CAP = 5` per `companion_routing.py`.
5. **Quote repair**: if the verifier's `evidence_quote` isn't a literal substring, a repair pass tries to rescue it (saved in `quote_repairs`).
6. **Expansion (relation-graph traversal)**: each surfaced anchor expands into ~3 related models via the curated relation graph (antagonist, tension edges). Each expansion carries `source_model_id`, `model_id`, `relation_type`, `activation_condition`, `affinity_rationale`, `substrate_chunk`, `why_relevant`.
7. The Companion CheatSheet then assembles failure modes, premortems, heuristics, identity chunks for each anchor, with optional embedding-based reranking (`reranker_active: None` on both our runs).

### Funnel observed

| Stage | Mother | Consultant |
|---|---|---|
| Reasoning moves validated | 7 | 7 |
| Candidates fed to verifier | 60 | 60 |
| Accepted by verifier | 5 | 4 |
| Rejected by verifier | 55 | 55 |
| Duplicate accepts | 0 | 0 |
| Capped (accepted-but-not-surfaced) | 0 | 0 |
| Quote repairs | 0 | 0 |
| **Final cheat-sheet anchors** | **5** | **4** |
| Expansions (relation-graph traversal) | 15 | 12 |
| Failure-mode chunks surfaced | 10 | 8 |
| Heuristic chunks surfaced | 10 | 8 |
| Identity chunks surfaced | 5 | 4 |

### Rejection reason distribution (already captured in `companion_rejected_models`)

| Reason | Mother | Consultant |
|---|---|---|
| `mechanism absent` | 51 | 43 |
| `topic-adjacent` | 0 | 6 |
| `too generic` | 2 | 3 |
| `execution_quote_not_literal_substring` | 1 | 3 |
| `passage already claimed by more specific model` | 1 | 0 |

### What's already in `audit_summary` (Lane 2) — but invisible to operators

Every one of these fields is captured per run; the chat output and the React SPA show none of them:

- `companion_fingerprint_raw` — raw LLM response (~4.3-4.5 KB per run)
- `companion_fingerprint_validated` — validated reasoning moves with evidence
- `companion_fingerprint_dropped` — moves rejected at validation
- `companion_candidates` — full 60-candidate list with `recall_source`, `keyword_rank`, `embedding_rank`, `final_rank`, `activation_trigger`, `danger_when`
- `companion_verification_accepted_before_cap` — full LLM-accepted set with evidence + explanation
- `companion_verification_capped_models` — accepted-but-not-surfaced
- `companion_rejected_models` — every rejection with `model_id`, `original_evidence_quote`, `rejection_reason`
- `companion_verification_duplicate_accepts` — dedupe drops
- `companion_verification_quote_repairs` — quote-rescue records
- `companion_card.expansions` — full expansion-graph traversal output (every neighbour with relation type, activation condition, substrate chunk)
- `companion_card.failure_hints`, `heuristic_hints` — actual hint text per anchor
- `companion_candidate_cap` — the cap value (60)

### Silent-loss bug found in this audit

In the consultant run, **`cognitive-dissonance` was sent as a candidate to the verifier but appears in NONE of the verifier's outputs** — neither accepted, rejected, deduped, nor capped. Math: `60 candidates → 4 accepted + 55 rejected + 0 duplicates = 59 disposed.` One missing.

This means the verifier LLM omitted the model from its response entirely (didn't accept it, didn't list a rejection_reason for it), and the parser doesn't track unmentioned-but-sent candidates. From the operator's perspective, `cognitive-dissonance` simply vanished without a trace.

**Fix shape**: in `parse_verification_response` (or its caller), reconcile the candidate set against the parsed accepted+rejected lists; any candidate present in neither becomes a third bucket like `silently_omitted_by_verifier` with `drop_reason="not_in_verifier_response"`. Mechanical.

### What's discarded today

| Discarded | Why it matters | Cost to add |
|---|---|---|
| **The fingerprint→recall mapping** — which reasoning moves produced which candidates | Today we know there were 7 moves and 60 candidates, but not which move generated which candidate or how many candidates each move produced. Useful for "this move was the load-bearing one" analysis. | Medium — recall logic would need to tag each candidate with its source move(s) |
| **Embedding rerank scores** for candidates | `reranker_active: None` on both runs. Embedding-based candidate reranking exists (`rank_models_expanded` in `embedding_retriever.py`) but isn't being invoked, OR is being invoked silently. | Small — log `reranker_active: True/False` deterministically and surface the per-candidate embedding score when rerank fires |
| **Verifier raw response** | `companion_fingerprint_raw` IS captured; verifier raw is not | Small — same pattern as fingerprint_raw |

---

## Lane 3 — Frame Pressure

(Both Issues B and the validator strictness have separate memo: `research/quote-handling-issues-a-b-c-2026-04-28.md`. Granular-visibility findings here are about what the lane records vs. discards in the *normal* path.)

### What the system does

1. **Frame extraction LLM call**: identifies frame_elements (assumption / mutable_constraint / suppressed_counterfactual) with `frame_pattern` from a curated taxonomy, plus `evidence_quote` (must be literal substring of user turns).
2. **Validation**: each element's `evidence_quote` is checked via `_evidence_in_text` (4 tolerance tiers — see Issue B memo). Rejected elements go to `dropped_frame_elements` (with the Issue A opacity bug).
3. **Reframing LLM call**: for surviving elements, generates 0-2 reframings with `grounding_model` (a mental model that anchors the reframe).
4. **Anti-echo**: any candidate model already used in Lane 1 routing or Lane 2 cheat sheet is excluded from Lane 3's `grounding_model` set.

### What's observable today

| Field | Mother | Consultant |
|---|---|---|
| `frame_elements` (kept) | 0 | 2 |
| `reframings` | 0 | 2 |
| `dropped_frame_elements` | 2 (with Issue A opacity) | 0 |
| `anti_echo_model_ids` | [] | 4 |
| `overlap_flags` (frame patterns that overlap Lane 1 at pressure-concept level) | [] | `["borrowed_premise"]` |

### What's discarded today

| Discarded | Why it matters | Cost to add |
|---|---|---|
| **The full frame_pattern taxonomy** the LLM was asked to choose from | The prompt lists ~16 patterns (`binary_collapse, borrowed_premise, scope_lock, temporal_fixation, ...`); we only see which were *used*, not which were considered. | Low — but probably not high-value; the prompt has the list. The interesting thing is per-run *frequency* of each pattern across many runs. |
| **The reframing LLM raw response** | Same gap as everywhere — only the parsed structure persists. | Small — same `raw_message_content` pattern |
| **The full mental-model candidate pool** for `grounding_model` selection | Only the 0-2 chosen models are visible. For a reframe scored as `inversion`, what models could have been the grounding? | Medium — depends on reframing-routing implementation |

### Issue A overlap (already documented in the quote-handling memo)

`dropped_frame_elements` records only `element_text` + `drop_reason`; the original `evidence_quote`, `element_type`, `frame_pattern`, etc. are lost. See `research/quote-handling-issues-a-b-c-2026-04-28.md` Issue A for the fix shape.

---

## Lane 4 — Structural Coverage

### What the system does

1. **Question classification LLM call**: classifies the conversation into one of `causal-diagnosis | decision-evaluation | action-planning | prediction`. (Mother: action-planning. Consultant: decision-evaluation.)
2. **Dimension detection LLM call**: from the **15-dimension catalog**, identifies which dimensions are structurally present in this problem and whether each is `covered` or a `gap`.
3. **Routing**: each gap dimension is routed to its candidate models via the curated `structural_coverage_routing` block in the knowledge graph. Anti-echo excludes any model already used in Lanes 1, 2, 3.
4. **Gap-question generation LLM call**: for each gap, produces 2-3 discovery questions for the decision-maker.

### The 15-dimension catalog (from `data/knowledge_graph.json`)

| Dimension | Curated candidate models |
|---|---|
| `behavioral-intervention` | 6 (incentives, persuasion-principles, habit-formation, ...) |
| `causal-diagnosis` | 5 (root-cause-analysis, five-whys-method, ...) |
| `commitment-reversibility` | 6 (sunk-cost-fallacy, lock-in, commitment-bias, switching-costs, optionality, path-dependence) |
| `competitive-dynamics` | 5 (game-theory-payoffs, nash-equilibrium, prisoners-dilemma, batna, red-queen-effect) |
| `existing-vs-new` | 5 (creative-destruction, opportunity-cost, ...) |
| `feedback-system-dynamics` | 6 (systems-thinking, feedback-loops, second-order-thinking, ...) |
| `incentive-alignment` | 5 (principal-agent-problem, moral-hazard, incentives, adverse-selection, information-asymmetry) |
| `information-quality` | 6 (survivorship-bias, base-rates, ...) |
| `resource-allocation` | 6 (opportunity-cost, comparative-advantage, ...) |
| `risk-response` | 6 (risk-assessment, black-swan-events, antifragility, margin-of-safety, calculated-risk-taking, resilience) |
| `scaling-dynamics` | 6 (scale-economies, network-effects, compounding, ...) |
| `scope-boundary` | 5 (circle-of-competence, constraints, ...) |
| `stakeholder-alignment` | 5 (power-dynamics, empathy, psychological-safety, six-thinking-hats, social-proof) |
| `timing-sequencing` | 5 (critical-mass, tipping-points, ...) |
| `uncertainty-type` | 5 (aleatory-epistemic-uncertainty-recognition, true-uncertainty-navigation, ...) |

### Funnel observed

| Stage | Mother | Consultant |
|---|---|---|
| `question_type` | action-planning | decision-evaluation |
| Dimensions in catalog | 15 | 15 |
| Dimensions detected as present | 7 | 10 |
| Of which `covered` | 4 | 6 |
| Of which `gap` | 3 | 4 |
| `gap_routes` produced | 3 | 4 |
| Total candidate-model slots routed | 16 | 21 |
| Anti-echo exclusions cumulative | 5 (all from Lane 2) | 9 (Lane 1 + Lane 2 + Lane 3) |

### What's already in `result.json` (Lane 4)

- `dimensions[]` — every detected dimension with `dimension_id`, `dimension_name`, `covered` (bool), `coverage_evidence` (text), `materiality_note` (text)
- `gap_routes[]` — for each gap: `dimension_id`, `dimension_name`, `candidate_model_ids`, `excluded_model_ids`
- `gap_questions[]` — generated discovery questions per gap
- `anti_echo_model_ids` — full cumulative exclusion list

### What's discarded today

| Discarded | Why it matters | Cost to add |
|---|---|---|
| **The 8-5 dimensions NOT detected** (15 minus the 7-10 detected) | We see "this dimension is present and covered/uncovered" but not "the system considered dimension X and decided it doesn't apply." For a complete picture you'd want to know "of the 15 possible structural dimensions, which 8 did the system rule out and on what grounds?" | Medium — requires the dimension-detection prompt to enumerate non-detected dimensions with reasoning. Today the prompt likely only asks for present dimensions. |
| **The classifier's reasoning** for `question_type` | Why was this conversation classified as `action-planning` rather than `decision-evaluation`? The classification gates which dimensions are even considered for some logic paths. | Small — capture the classifier LLM raw response |
| **Per-dimension materiality scoring** (if it exists) | `materiality_note` is present but is it a free-text LLM judgment or scored? Whether some gaps are higher-priority than others is invisible. | Medium — depends on whether the prompt asks for ordinal materiality |

---

## Cross-cutting findings

### 1. Anti-echo cascade IS reconstructible from the JSON (consultant case)

The 9 model_ids in `structural_coverage_card.anti_echo_model_ids` decompose as:

| Excluded model | Source |
|---|---|
| `confidence-calibration` | Lane 2 anchor |
| `information-asymmetry` | Lane 2 anchor |
| `obligations-controls-mapping` | Lane 2 anchor |
| `power-dynamics` | Lane 2 anchor (also Lane 1 antidote) |
| `decision-trees` | Lane 3 grounding model |
| `premortem` | Lane 3 grounding model |
| `psychological-safety` | Lane 1 antidote (from authority-misinfluence routing) |
| `systems-thinking` | Lane 1 antidote (from reward/punishment routing — also primary) |
| `user-experience-research-methods` | Lane 1 antidote |

**This decomposition is reconstructible from the JSON today** by intersecting `anti_echo_model_ids` with each upstream lane's surfaced models. But the system doesn't *record the attribution* — it just dumps the cumulative set. For Observatory, you'd want to render each excluded model with a "(from Lane N)" tag.

### 2. Embedding usage is happening but mostly invisible

- 4 OpenAI calls per run (1 expansion via gpt-4o-mini, 3 embedding calls via text-embedding-3-large)
- Pass 1 embedding triage: top-25 tendencies ranked, those ≥ 0.30 promoted. **The 23+ tendencies that were ranked but didn't promote are silently discarded.**
- Companion candidate reranking: `reranker_active: None` on both runs — meaning either embeddings weren't used OR the field isn't being set even when they are. Need to read `companion_selection.py` to disambiguate.
- Lane 2 candidates show `embedding_rank: None` for all 60 candidates in both runs — all sourced from `recall_source: "keyword"`. So the embedding-based recall path either didn't fire or didn't merge properly.

**The full embedding rank lists (with sub-threshold scores) are the highest-value telemetry currently being discarded for "which models almost made it" analysis.**

### 3. Per-call telemetry: `raw_message_content` is the missing piece across the board

`BoundaryCallMetadata` has 14 fields. The serialized `boundary_calls` list captures 11 of them. The 3 dropped fields are:

| Discarded | Impact |
|---|---|
| `raw_message_content` | The full LLM JSON response per call. **This single addition would have made Issue B investigable from the persisted artifact** without re-running Lane 3. It's also what would let us see Pass 1 cluster reasoning, dimension classifier reasoning, deep-check reasoning, frame extraction raw, reframing raw — every LLM-decision point. |
| `finish_reason` | Whether the call truncated, hit a stop sequence, or completed normally. Important for diagnosing partial outputs. |
| `temperature`, `reasoning_disabled`, `reasoning_details_present` | Configuration witnesses for reproducibility audits. |

Cost to add: small (the data is already in metadata; just persist it). Cost to *use*: medium (per-call raw content can be 2-10 KB; over 60+ calls per run, that's 120-600 KB extra in result.json — material but not prohibitive).

### 4. The "gravity model" question — what we'd need to answer it

You asked: "I want to decide which mental models are the gravity ones pulling our requests."

To answer that, we need to track for each model in the catalog (222 total per HOW_IT_WORKS):
- **Surface frequency** — how often it appears across runs as: anchor, expansion, gap_route candidate, antidote in routing, exclusion via anti-echo, etc.
- **Source-of-survival** — when surfaced, was it from keyword recall, embedding rerank, curated routing, or relation-graph expansion?
- **Per-run multiplicity** — does the same model appear in multiple lanes within a single run? (`information-asymmetry` was a Lane 2 anchor AND a Lane 4 candidate AND a Lane 4 anti-echo exclusion in the consultant run — that's high gravity)
- **Selection vs. rejection rate** — when the verifier sees a model as a candidate, how often does it accept vs. reject?

None of this is computable today from a single run's `result.json` alone. It requires aggregation across runs. The pieces needed:

1. **Per-run model-mention index**: a flat table of `(run_id, model_id, lane, role)` rows. Buildable from the existing `result.json` fields without new telemetry. Could live as a derived artifact (`scripts/build_model_mention_index.py`) computed at archive time.
2. **Multi-run aggregator**: takes the index above plus the existing `~/.local/share/lolla/runs/` archive and computes per-model gravity stats. ~150 lines.
3. **Observatory page**: reads the aggregator output, renders a sortable table with surface-frequency-per-1000-runs, by-lane heatmap, and a per-model drill-down showing every run where each model surfaced.

This is the foundation for the "decide how many mental models are picked" lever you mentioned. Once gravity is measurable, the cap values (5 anchors per cheat sheet, 6 candidates per dimension route, top-25 embedding tendency rank) become tunable based on data rather than design intuition.

---

## Prioritized work list (the gap-closing roadmap)

### Bucket A — Surface what's already captured (highest ROI)

These are pure rendering changes. The data exists in `result.json`; the SPA and `/usage` page just don't show it.

1. **Lane 2 selection funnel panel** — render `companion_candidates` (60 rows with rank info), `companion_verification_accepted_before_cap` (~5), `companion_rejected_models` (~55 with `rejection_reason`), `companion_verification_capped_models`, `companion_verification_duplicate_accepts`, `companion_verification_quote_repairs`. This single panel answers most of the "60 picked, 55 rejected" question for Lane 2.
2. **Pass 1 + Pass 2 funnel panel** — render full 24-tendency scoring, the triage threshold (currently constant 4), the `triggered_tendency_sources` with source attribution, and per-tendency `deep_check_results` with `detected` flag and `sub_pattern`.
3. **Lane 4 dimension panel** — render the full 15-dimension catalog with each marked detected/not-detected, covered/gap, plus `gap_routes` with anti-echo annotations.
4. **Anti-echo cascade panel** — render `anti_echo_model_ids` for each lane with the lane-of-origin tagged for each excluded model (computed by intersection — no new telemetry needed).
5. **Routing decisions panel** — render `routing_decisions` per detected tendency: primary model, antidote models, supporting/risk models, tiebreaker traces.
6. **Companion expansions panel** — render `companion_card.expansions` (12-15 entries per run) with anchor → expanded model, relation_type, activation_condition, why_relevant.

### Bucket B — Capture what's discarded but easy to add

These need small code changes to start persisting data the system already produces but throws away.

7. **Persist `raw_message_content` per boundary call** — single change in `_record_from_metadata` (or wherever the BoundaryCallRecord is built). Adds ~120-600 KB per run JSON. Makes every LLM decision investigable from artifacts alone.
8. **Persist embedding ranks for all 25 tendencies** (not just ≥ 0.30) — change `_embedding_tendency_signal` to return the full ranked list with a flag indicating which crossed the threshold.
9. **Populate `DeepCheckResult.reasoning`** — the dataclass has the field; check that each deep-check adapter writes to it.
10. **Fix the silently-omitted-by-verifier bug** — in `parse_verification_response`, reconcile candidate set against accepted+rejected; surface omitted candidates as a third bucket. (Fixes the `cognitive-dissonance` ghost in the consultant run.)
11. **Lane 4 dimension non-detection reasoning** — modify the dimension-detection prompt to enumerate the 15 dimensions explicitly with present/absent + reasoning, instead of returning only the present ones.

### Bucket C — Multi-run infrastructure (the "gravity" question)

These build the cross-run aggregation that today doesn't exist.

12. **Per-run model-mention index** — `scripts/build_model_mention_index.py`, runs at archive time, produces a flat `(run_id, model_id, lane, role)` table. Computed from existing `result.json` fields.
13. **Multi-run gravity aggregator** — reads all archived runs, computes per-model surface frequency and selection rates. Output: `model_gravity.json` with sortable stats.
14. **Observatory gravity view** — sortable table of all 222 models with their per-1000-runs surface frequency, per-lane heatmap, and drill-down to specific runs where each model appeared.
15. **Tunable caps configuration** — once gravity data exists, expose the current hardcoded caps (`_DETECTED_MODELS_CAP=5` for Lane 2, top-25 for embedding tendencies, 6-per-dimension for Lane 4) as configurable parameters that can be A/B tested. The data tells you what the right cap is.

---

## What this audit DOESN'T answer (acknowledged unknowns)

- **Why the verifier silently omits some candidates** (e.g. `cognitive-dissonance`). I see the omission; I haven't traced whether the LLM truly never mentioned it or whether the parser's regex misses certain shapes.
- **Whether `reranker_active: None` means embeddings weren't used or weren't logged** — needs reading `companion_selection.py` to disambiguate.
- **The actual reason inconsistency-avoidance and stress-influence had `detected=False` from Pass 2** — `reasoning` field is empty in `deep_check_results`. Need to either populate that field or read the deep-check adapter source for these specific tendencies.
- **What models are in the catalog but never surfaced across either run** — would need a many-run aggregation. With only 2 runs the long tail of "never-picked" models is dominated by sample-size noise.

---

## Suggested sequencing

If you want a single PR that delivers the most observability per line of code, the order I'd recommend:

1. **PR 1** (Bucket B item 7): persist `raw_message_content` per boundary call. Single-file change. Unlocks investigation for every future run. Side benefit: makes Issue B (and any future quote-validation issues) investigable from artifacts.
2. **PR 2** (Bucket B items 8, 9, 10): add full embedding ranks, populate deep-check reasoning, fix verifier silent-omission. Three small fixes, one PR. Closes the data-loss bugs.
3. **PR 3** (Bucket A items 1-6): Observatory rendering of everything that's already in `audit_summary`. Server-side HTML on `/usage` if SPA rebuild is out of scope; React panels if SPA source is available.
4. **PR 4** (Bucket B item 11): Lane 4 non-detection reasoning. Prompt change + parser change.
5. **PR 5** (Bucket C items 12-15): multi-run gravity infrastructure. Largest scope; defer until Buckets A and B are settled and we have empirical data on what gravity stats actually drive decisions.

Each PR is independently shippable. None depends on the next. The first two are the cheapest investigations-enablers; the third closes the visibility gap to the operator; the fourth and fifth are the new analytical surfaces.

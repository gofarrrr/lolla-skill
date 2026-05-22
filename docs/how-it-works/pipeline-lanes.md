# Pipeline Lanes

Detailed reference for the Step 3 pipeline internals. Read this when you need lane mechanics, post-lane enrichment, run-health fields, or routing traces. For the chronological run sequence, read [Live Flow](live-flow.md).

## Contents

- Lane 1: structural pressure
- Lane 2: model companion
- Lane 3: frame pressure
- Lane 4: structural coverage
- Post-lane V60 private enrichment and pre-Step-6 shadow portfolio
- `run_health` and tiebreaker observability

**Lane 1 — Structural Pressure (6+N OpenRouter calls):**

1. **Pass 1 (family-clustered triage):** Six OpenRouter calls run in parallel — one per tendency family (authority, closure, incentive, availability, self_regard, residual — see [Architecture and Evolution](architecture-and-evolution.md) for the full cluster taxonomy and rationale). Each cluster scores only its 3-5 assigned tendencies and carries only that family's confusion guardrails. Results are merged deterministically into a single `triage_scores` list covering all 24 canonical non-lollapalooza tendencies; lollapalooza is surfaced by deterministic compound detection during DeltaCard assembly, not by triage. Tendencies scoring ≥4 enter the "triggered" set.

2. **Embedding swiss cheese** (optional, if `OPENAI_API_KEY` set): Embeds the joined assistant-turn text and compares against 25 pre-computed tendency guidance vectors. Any tendency below the LLM threshold but above the embedding threshold gets promoted into the triggered set. This catches what the LLM missed — and vice versa. Each triggered tendency carries a `TriggeredTendency` record with its `source` (`triage`, `embedding`, or `always_include`) and `score` — enabling observability into which detection layer caught what. The result JSON includes both `triggered_tendencies` (IDs) and `triggered_tendency_sources` (full source/score records). The full top-25 ranked list (with a `promoted: bool` per row) lands in `audit_summary.embedding_tendency_ranks` so close-call telemetry — "tendency X scored 0.28, almost made it" — is visible without re-running.

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
2. **Step 6's three-treatment vocabulary** (defined in [Live Flow](live-flow.md)). Anchors with direct, specific evidence become *primary pressure*. Anchors with weaker, broader, or competing evidence become *secondary lens*. Anchors the reviser reads as not load-bearing are *set aside with a reason*. The grading is downstream; the verifier doesn't need to be the grader.

Multi-run stability investigations (`research/stability-runs/lane2-stability-experiments-2026-04-27/`, including baseline evidence in `e6-baseline-runs.json` and cross-case evidence in `e6-baseline-crosscase-runs.json`) extended the earlier-cited finding: verifier acceptance varies with backing-model behaviour and fingerprint phrasing, with bounded but real cross-run variance (typical pairwise Jaccard 0.6–0.8) and per-anchor surfacing rates that shift across sessions independent of prompt content. The product contract therefore treats Lane 2's job as *delivering a useful lens*, not *delivering a precise verdict*.

Two harness affordances support this design (PR #58):

- **`is_malformed_verifier_response(raw_payload)`** in `companion_routing.py` distinguishes schema-incomplete output from deliberate empty rejection. Returns `True` when the raw payload is non-dict, is `{}`, or is a dict whose `accepted` and `rejected` fields are both missing or non-list. Returns `False` for any deliberate empty-list response (`{"accepted": [], "rejected": []}` or `{"accepted": []}` alone). Future E6-style ablation tests use this helper to compute `malformed_runs_count` per slate; production runs do not currently call it but it remains available as a diagnostic surface.
- **`audit_summary.companion_verification_silently_omitted`** captures candidates the verifier was given but never mentioned in either accepted or rejected (drop reason `not_in_verifier_response`). Closes the gap the 2026-04-28 audit memo found in the consultant case where one of 60 candidates simply vanished from the verifier's output. NOT semantically rejected — the LLM dropped them silently — so the bucket lives separately from `companion_rejected_models`.
- **`BoundaryCallMetadata` extended fields** — `finish_reason`, `raw_message_content`, `temperature` — are populated on the success path of `OpenAICompatibleBoundaryClient.run_json_with_metadata`, persisted per-call to `audit_summary.boundary_calls[N]` (PR 1 of the 2026-04-28 granular-visibility roadmap), and available to diagnostic scripts via `client.last_call_metadata`. `audit_summary.boundary_summary` continues to carry `providers` + `models` + token totals only — that aggregation surface is unchanged.

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

3. **Deterministic routing**: For each uncovered dimension, the deterministic middle looks up candidate mental models from the Wave 6 structural coverage routing table in the knowledge graph (82 model bridges across 74 unique models). Anti-echo exclusion removes models already surfaced by Lanes 1, 2, and 3 — the broadest anti-echo scope of any lane.

4. **Gap question generation** (LLM call 3, conditional): For each gap dimension with routed models, one OpenRouter call generates 2-3 discovery questions following the 5Ws+H framework — concrete questions first (who, what, where, when), reflective last (why). Questions are problem-specific, plain language, and answerable only by the decision-maker from their knowledge of the situation. This call **only fires when gaps exist** — zero gaps means no LLM call, no questions. These gap questions are the HITL (Human-In-The-Loop) bridge: they are never answered by an AI.

5. **Card assembly** (deterministic): Assemble detected dimensions, gap routes, gap questions, and anti-echo metadata into a StructuralCoverageCard.

**Lane 4 prompt structure.** Question classification, dimension detection, and gap question generation use `run_structural_coverage_with_traces_from_ir` in the live pipeline — the orchestrator builds a `Lane4Packet` from the IR, dispatches to the `_from_packet` formatters internally, and captures each boundary-call trace immediately after that stage returns. User-prompt bodies follow the same CONTEXT (extractor summaries, NOT citable) / SOURCE (raw conversation turns) split as Lane 3. For detection specifically, SOURCE contains both user and assistant turns — detect_when conditions read user turns (the question), coverage assessments read assistant turns (the answer). Lane 4 has no evidence-substring validation downstream (unlike Lane 3), so the CONTEXT/SOURCE split is prompt guidance not a mechanical gate; the architectural effect shows up as `coverage_evidence` citations attributed to the assistant's actual replies ("Assistant mentions...", "Assistant proposes...") instead of extractor-paraphrased summaries.

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

**V60 private enrichment (post-lane, no extra chat call):** After the four lanes serialize their cards, `run_pipeline.py` attaches a private `v60_enrichment` block to `result.json` by default (`--v60-enrichment auto`, disabled by `LOLLA_V60_ENRICHMENT=off` or `--v60-enrichment off`). This is not a fifth lane and it is not public card output. It reads the model IDs already surfaced by the lanes, merges their provenance, optionally adds low-trust model recall from the existing embedding retriever, and then enriches the selected model IDs from the explicit V60 artifact (`--v60-affordances-path`, defaulting to `data/compiled/model_affordances/affordances_v60.json`; no "latest" selection). The default cap is 8 private cards. Each selected card carries at most one compact affordance chunk and one compact absence chunk, plus source file, confidence/status, why it was pulled, embedding trace, selection score/reason/effect type, sibling alternatives considered, fallback method, and `do_not_overclaim` warnings. The deterministic layer does *selection and custody*; Claude/Codex does *consideration* in Step 6.

The V60 block also records what did not enter the hot context: skipped candidates, missing V60 records, duplicates, packet-cap exclusions, and `not_presented_model_ids`. This is the difference between "we showed the model some extra stuff" and "we can audit which opportunities were selected, suppressed, or left outside the budget." At this point the ledger is only expected, not yet written; validation happens after Claude/Codex has actually used, rejected, or deferred the chunks in Step 6.

**Pre-Step-6 shadow portfolio (default off, shadow only):** `run_pipeline.py` also has a dormant `--pre-step6-portfolio shadow` mode, configurable through `LOLLA_PRE_STEP6_PORTFOLIO=shadow` and `LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR`. It never builds live decks, never calls reviewers, and never changes the visible Step 6 answer. In shadow mode it computes a compiled card-deck key from the current result payload, checks for a cached deck, derives a ledger signal when a Step 6 ledger is supplied, applies deterministic guardrails, and records `pre_step6_shadow_portfolio` plus a sidecar for archive/Observatory. The gates intentionally stay closed: `runtime_wiring_allowed: false`, `skill_update_allowed: false`, and `visible_behavior_change_allowed: false`.

**Pipeline diagnostics (`run_health`):** The pipeline output includes a decomposed health status that rolls up capture diagnostics, pipeline state, V60 accountability, and product-output hygiene into one truthful object:

- `overall` — `healthy`, `partial`, `degraded`, or `critical`; optional-off signals such as embeddings disabled by mode do not degrade by themselves
- `capture` — `good`, `degraded`, `critical`, or `unknown` (from extraction's `capture_health`)
- `substrate` — `ok` if compiled chunks loaded, `empty` if bundle selector failed
- `embeddings` — `active` or `off`
- `fingerprint` — `ok` if companion verified at least one model, `empty` otherwise
- `findings_produced` — whether Lane 1 produced any findings
- `issues` — legacy array naming what happened: `substrate_empty`, `embeddings_off`, `no_fingerprint`, `pipeline_warnings`, `capture_degraded`, `capture_critical`, `quote_fabrication`, `capture_truncated`, `lane3_all_dropped`, `bullshit_index_partial`, `stakeholder_check_failed`, `v60_enrichment_failed`, `v60_consideration_ledger_missing`, `v60_consideration_ledger_invalid`, `product_output_leak`, `live_output_leak`, `live_output_missing`, `live_output_unverified`
- `issue_details` — structured severity records with `code`, `severity`, `axis`, `trust_impact`, and mode/count metadata
- `warnings` — merged pipeline warnings + capture warnings
- `capture_manifest` (optional) — actual vs. declared turn counts and character length from the conversation capture
- `bullshit_index_evaluation_failures` — passage-level delivery-audit calls that failed while the remaining passages still produced a partial profile
- `activation_tiebreaker` — `"on"` or `"off"` (reflects the `LOLLA_ACTIVATION_TIEBREAKER` kill switch; default on)
- `v60_enrichment` — `active`, `disabled`, or `skipped_error`
- `v60_selected_chunk_count` — number of private V60 chunks presented to Step 6
- `v60_consideration_ledger` — `valid`, `missing`, `invalid`, or `not_required` after Step 6b/Step 9 finalization
- `v60_consideration_disposition_counts`, `v60_used_chunk_count`, `v60_presented_but_not_used_chunk_count`, `v60_unaccounted_chunk_count` — process telemetry for comparing what was offered, what was picked up, and what was left unused
- `product_output_health`, `product_output_leak_count`, `product_output_leaks` — archive-time scanner result for revised text, memo markdown, and memo-note fields
- `live_output_health`, `live_output_leak_count`, `live_output_leaks` — live-transcript scanner result for `/tmp/lolla_<run_id>_live_transcript.txt`; missing transcripts are recorded as `missing`, manual no-leak transcripts are `not_checked`, and only a trusted complete transcript can be `clean`
- `pre_step6_shadow_portfolio` — present only when shadow mode ran; records cache hit/miss/error status without changing public output

`overall` is computed from issue severity. Capture-critical stays critical; invalid/missing V60 ledgers, product-output leaks, and unsafe live transcripts degrade; partial lane/evaluator loss, required-but-missing live transcript capture, or required-but-unverified manual live capture can be partial; optional embeddings-off remains visible without pretending the run is broken. These diagnostics make it possible to distinguish a clean "no findings" result from a broken run that produced no findings because the substrate didn't load, the conversation was badly captured, the private ledger was missing, the live transcript was not mechanically proven complete, or the public surface leaked internal machinery.

**Per-route tiebreaker observability.** Beyond `run_health`, every detected tendency's routing decision carries a `TiebreakerTrace` under `audit_summary.routing_decisions[].tiebreaker_supporting` / `.tiebreaker_risk`. Each trace records whether the near-tie activation-match gate attempted, fired, or aborted — and if aborted, which clause stopped it. Fields include top-1/top-2 model ids and fan-adjusted affinities, top-1/top-2 cosine similarities, the delta, and the calibration constants (`epsilon`, `noise_floor`) in effect. This means a run can answer "did the activation tiebreaker intervene for this route, and if not why" from the result JSON alone. See `research/deep-graph-enrichment-handover.md §14k` for a field-by-field reading guide.

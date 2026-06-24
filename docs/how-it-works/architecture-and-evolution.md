# Architecture and Evolution

Detailed reference for the runtime architecture, migration history, lane design, observability, and trust boundaries.

## Contents

- Current runtime state and layer map
- Migration history from `CritiqueRequest` to `ConversationContext`
- Trust boundary between external audit and orchestrator reconsideration
- Probabilistic edges, deterministic middle
- Lane separation, observability, run health, and comparison surfaces

## Architecture

### Current State (2026-06-24)

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
| Private enrichment | `v60_enrichment` + `v60_consideration_ledger` | `v60_enrichment.py`, `run_pipeline.py`, `finalize_v60_telemetry.py` | Post-lane source-backed affordance/absence chunks selected from explicit `affordances_v60.json`; Claude/Codex privately considers every selected chunk and the deterministic layer validates the ledger |
| Pre-Step-6 private table | `pre_step6_private_table` + `pre_step6_private_table_ledger` | `pre_step6_private_table.py`, `run_pipeline.py`, `SKILL.md`, `archive_run.py` | Live-skill context transport. Renders a compact private table from current lane/V60 material, appends cached cards on cache hit, and lets Step 6 decide what matters. Zero extra LLM calls, no live card generation, no code-selected visible answer. |
| Dormant shadow experiment | `pre_step6_shadow_portfolio` | `pre_step6_shadow_portfolio.py`, `run_pipeline.py`, `archive_run.py`, `serve_result.py` | Explicit shadow-only evidence recorder for cached pre-Step-6 card decks. It never generates live decks and never changes visible output. |
| Audit | `AuditTrace`, `build_pipeline_audit_trace` | `audit_assembly.py` | Aggregates per-call telemetry, lane outputs, warnings |
| Telemetry | `BoundaryCallTrace`, `BoundaryCallMetadata` | `boundary_tracing.py`, `boundary_provider.py` | Per-call model + token counts (prompt/completion/total/cached/reasoning) |
| Lifecycle custody | `run_events.json`, `operator.log`, `live_transcript.txt`, `final_receipt.txt` | `scripts/record_run_event.py`, `scripts/skill/operator_log.sh`, `scripts/skill/finalize_and_archive.sh`, `archive_run.py` | Separates user-visible product surface from operator diagnostics, records helper lifecycle events, verifies Observatory liveness before the final receipt, and supports trusted transcript finalization when a complete live-session capture is available. |

The IR's three provenance tiers — `span` (exact substring in one turn), `turn_ref` (paraphrase, source turn known), `derivation` (multi-turn synthesis with refs) — make the difference between substring-validated content and honest paraphrase visible to every consumer downstream. No paraphrase ever masquerades as a quote.

The live skill now has two transport layers after the four lanes. V60 private enrichment selects a compact slate of source-backed opportunities for the skill runner to consider: what a model can legitimately do, what evidence is needed before using it, what misuse to avoid, and which tempting interpretations the source explicitly does not support. The pre-Step-6 private table then renders the current lane/V60 material into a cleaner thinking surface and appends cached card-deck pressure only on cache hit. Neither layer decides the answer or renders a public card. The user sees the improved reasoning; the Observatory and archive retain the machinery.

There is also an explicit pre-Step-6 shadow portfolio hook. It remains a research integration boundary, not live product behavior: `--pre-step6-portfolio shadow` only records whether a cached deck would have been eligible under the proposed policy and exposes that record in archive and Observatory `/audit/pre-step6`.

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
| **Chat delivery, memo hardening, and output hygiene (PR #72/#73 + May 2026 follow-up)** | Reworked the skill surface from a card summary into a progressive chat flow: readback + audit promise, strongest counterargument, updated position, default-off pressure-check state or optional pressure check, then functional receipt. Step 8c writes `memo_*` decision-note fields before `scripts/render_memo.py` renders the standalone memo. New-run memos are product-clean by default: decision note plus capped unanswered questions; the full deterministic audit appendix is opt-in via `--include-audit-appendix`. Public prose now follows an accounting invariant rather than a naming invariant: every anchor and private enrichment chunk must be considered, but model names, V60, affordance, chunk, packet, ledger, lane, card, and internal IDs stay out of chat/memo unless a familiar model name is the clearest human handle. Archive finalization runs a deterministic product-output hygiene scanner over revised text, memo markdown, and memo-note fields; live runs also maintain `/tmp/lolla_<run_id>_live_transcript.txt`, which is scanned as `live_narration`. Leaks set `product_output_health` or `live_output_health` to `unsafe` and degrade run health; a clean manual live-transcript artifact records `live_output_health: not_checked` until a complete trusted transcript was supplied. | The engine could already produce useful cards, but the user-facing surface was too system-centric: labels, counts, card names, early Observatory links, and live orchestration narration leaked machinery. The current contract separates surfaces: chat gives the live reconsideration, the memo gives a portable decision note, Observatory gives the full instrument panel, and `run_health` tells the truth when any layer is partial, unverified, or product-unsafe. |
| **V60 transaction enrichment + telemetry (May 2026)** | `run_pipeline.py` attaches `v60_enrichment` after the four lanes by default, using the explicit `data/compiled/model_affordances/affordances_v60.json` artifact and no "latest" glob. The enrichment reads model IDs already surfaced by lanes, merges provenance, optionally adds low-trust model recall through the existing embedding retriever, and selects up to 8 private cards. Each card carries one compact affordance chunk and one compact absence chunk when available. Chunk choice is local-relevance scored against the conversation and lane evidence, with `record_order_first` recorded only as an explicit fallback. Step 6b starts from a deterministic ledger skeleton, writes `v60_consideration_ledger`, and finalization validates identity, route/disposition compatibility, visible/private effect fields, and absence-blocker fields. `run_health` records disposition counts, used chunks, presented-but-not-used chunks, and missing/invalid ledger issues with structured severity. | This is the transaction layer the handover asked for: freedom of conclusion, not freedom from consideration. The deterministic system selects and preserves custody; Claude/Codex decides whether the chunk is useful, rejected, deferred, or only a private guardrail. The value is reasoning transport, not public taxonomy display. |
| **Receipts/accountability hardening (May 2026)** | Lane 4 now captures boundary-call metadata immediately per classification, detection, and gap-question stage; extraction writes `--output-file` even on non-strategic and missing-field exits; run health uses structured severities; archive finalization adds product-output and live-output hygiene; `scripts/compare_archived_runs.py` compares two archived runs with health/trace/product/live eligibility before answer or memo diffs. | This closes the false-confidence gap: selected chunks, valid-looking ledgers, cost telemetry, and changed final prose are not enough. Operators need truthful traces before spending tokens on live comparisons. |
| **Quote-wrapper extraction validation (2026-05-11)** | `scripts/run_extract.py` now validates `reasoning_passages` through shared `find_substring_tolerant(...)`. The validator still rejects paraphrase, punctuation drift, whitespace drift, and word substitutions, but accepts narrow quote-safe fallbacks: casefold match and a symmetric quote wrapper around the entire passage. Verified passages are replaced with the transcript's original span. | The May 10 live run degraded because the extractor wrapped exact transcript spans in quotation marks. That was not a real quote-fabrication failure. The fix keeps the strict provenance contract while removing a spurious degradation class. |
| **Pre-Step-6 shadow portfolio hook (2026-05-21/22)** | `scripts/run_pipeline.py` accepts `--pre-step6-portfolio shadow` or `LOLLA_PRE_STEP6_PORTFOLIO=shadow`, optionally with `LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR`. `engine/system_b/pre_step6_shadow_portfolio.py` computes a compiled deck key, performs cached-deck lookup only, derives Step 6 ledger signal and answer-delta specificity when inputs exist, validates deterministic guardrails, writes a sidecar, and serializes `pre_step6_shadow_portfolio` into the result. `archive_run.py` now copies `pre_step6_shadow_portfolio.json`; Observatory exposes `/audit/pre-step6`. | This preserves the research signal without changing product behavior. The gates remain false for runtime wiring, skill updates, and visible behavior changes until promotion evidence supports a real integration. |
| **Pre-Step-6 private table wiring (2026-05-22)** | `scripts/run_pipeline.py --pre-step6-portfolio step6_private` writes `/tmp/lolla_<run_id>_pre_step6_private_table.md` and serializes `pre_step6_private_table` into `result.json`. `SKILL.md` now instructs Step 6 to read that private table before writing and Step 6b to persist `pre_step6_private_table_ledger`. The renderer uses current lane/V60 material on every run and appends cached card-deck pressure only on cache hit. | This is the first live wiring of the cleaning lane. It moves value before Step 6 without reviving post-Step-6 pressure checks by default: no extra LLM calls, no live card generation, no reviewer calls, and no deterministic visible-answer selection. |
| **Model/cost attribution hardening (2026-05-25)** | The default OpenRouter boundary model is `google/gemini-3.1-flash-lite`; per-call telemetry records requested and served model IDs, distinguishes provider version aliases from true mismatches, costs calls against the served/billing model, and marks cost estimates as `complete`, `partial`, or `unknown` based on pricing coverage. `SKILL.md` was edited for the first time in this program, but only for operational infrastructure: the default model echo and cost-warning wording. The skill flow itself did not change. A same-day Lane 1 diagnostic rejected `deepseek/deepseek-v4-flash` as the default candidate because it over-rejected historical founder findings and showed timeout instability; Gemini Flash Lite reproduced the founder signal with complete pricing and no true provider mismatch. | This makes future product evidence attributable and honestly priced. The production model default changed on 2026-05-25, so earlier calibration/probe evidence remains design evidence but is informational for this new production-default baseline. Mismatch handling is record-and-continue: runs do not hard-fail when OpenRouter serves a different model, but `usage_summary` flags the artifact as attribution-sensitive for operator review. |
| **Runtime accountability hardening (2026-06-24)** | Added run lifecycle events across helpers, moved verbose helper diagnostics into `operator.log`, verified Observatory liveness before printing the final user receipt, allowed complete trusted live transcripts to be synced and required clean before archive, and fixed the graph-survival report's Lane 2 ledger uptake join. | This separates product surface from operator surface and closes several false-confidence gaps: a receipt should not claim an Observatory URL before the server is reachable; a manual transcript should not be treated as proof of a clean live run; helper failures should be traceable without leaking to chat; and graph-survival reports should preserve whether selected companion/V60 material actually survived into visible, private, confirming, rejected, or unadjudicated use. |

#### Today: ConversationContext → ConversationIR → Lane Packets → Private Enrichment

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
        ↓
V60 private enrichment (explicit affordances_v60.json + optional embedding recall)
        ↓
pre-Step-6 private thinking table sidecar
        ↓
result.json + Step 6 private consideration ledgers
        ↓ optional shadow-only cache evidence
pre_step6_shadow_portfolio sidecar when enabled
```

Every step preserves more structure than the one before. Nothing collapses to flat strings.

#### Why this shape, in one sentence per layer

- **`ConversationContext`** exists so the raw turn-by-turn transcript stays canonical and quote-fabrication is mechanically detectable (every alleged quote has to literally appear in some turn).
- **`ConversationIR`** exists because lanes need typed, provenance-bearing objects (not paraphrased strings) to produce findings that can be audited back to source text without re-parsing.
- **Specialists** (Phase 3b / 5 / 5.5) exist because the monolith extraction prompt could not produce substring-grounded fields no matter how hard it was tuned — the architectural answer was a separate substring-validated specialist per field, gated by annotation evidence and measured against gold.
- **Packet builders** (Phase 4) exist because lanes shouldn't depend on the IR's internal shape evolving — they consume a contract (`Lane4Packet`) that names exactly the slice they need, with `provenance_kind` metadata that lets future lane prompts mark "this is span-validated" vs "this is paraphrase".
- **V60 private enrichment** exists because the old packet shape flattened model-level wisdom. The live layer now keeps per-affordance and per-absence identity through selection, then asks the skill runner to account for each selected chunk privately before writing the answer.
- **Module split** (Phase 7) exists because navigability matters when `pipeline.py` is the orchestration entry point and reviewers need to understand it quickly.
- **Phase 6's removal** exists because keeping legacy alongside new is technical debt with a half-life — every refactor pays the cost of dispatching between paths.

### Conductor, Not Player

**Claude is a conductor, not a player — for the audit.** It captures the conversation, calls scripts, and presents results. It performs zero reasoning judgment inside extraction, triage, routing, fingerprinting, deep checks, or card generation. Every semantic decision in the audit pipeline goes through OpenRouter where prompts are calibrated and measurable.

**Claude does author the post-audit product layer.** After the pipeline returns the four cards, private V60 enrichment, and the pre-Step-6 private thinking table, Claude writes the user-facing reconsideration (Step 6), accounts for selected private material in ledgers (Step 6b), records the pressure-check state (default-off unless deeper review was explicitly requested), and writes the memo decision-note fields (Step 8c). These are not new detections. They are the presentation, consideration, and reconsideration layer built from persisted audit artifacts. The revised answer is persisted as a first-class run artifact with provenance (`revised_answer_source: "claude_step6"`), the V60 private ledger is validated into `run_health`, and the memo fields are persisted before rendering.

This is a deliberate trust-boundary split:
- **Audit (detection + routing + card assembly)** — OpenRouter via calibrated prompts. Claude produced the original reasoning; asking the same LLM to find its own flaws invites sycophantic self-defense. A different model audits.
- **Private consideration + reconsideration + memo (Steps 6/6b/8/8c)** — Claude. It has the full conversation context, the user's nuances, and the back-and-forth. The audit cards and V60 chunks are structural pressure, not commands. Claude absorbs, rejects, defers, or keeps that pressure private, then writes the portable decision note. The detector still stays outside the model that produced the original advice.

Why the audit stays external:

- **Calibration control.** You can't tune Claude's judgment the way you tune an OpenRouter prompt. The pipeline has been calibrated over hundreds of eval runs against professional-grade cases. Inline judgment has been calibrated against zero.
- **Fox can't audit the henhouse.** RLHF training optimizes for agreeable outputs. External audit breaks that loop.
- **Telemetry.** When OpenRouter runs the pipeline, we get `BoundaryCallMetadata` back — prompt tokens, completion tokens, cached tokens, reasoning tokens. This makes the system observable and measurable.

### Model Requirements

The skill is calibrated against Claude Opus 4.7 as the orchestrator. Cross-model validation on 2026-04-22 produced three tiers:

- **Opus 4.7** — recommended. Full doctrine compliance: private anchor/V60 accounting, machinery-leak avoidance, and full artifact cycle execution.
- **Sonnet 4.6** — acceptable. Completes the full default pipeline cycle including V60 ledger persistence, default-off pressure-check state, telemetry finalization, memo rendering, and archive. Modest phrasing regressions remain possible, so the output-hygiene contract keeps public mental-model naming optional and pushes exact substrate details into Observatory/audit. Fit for regular use; expect marginally noisier prose than Opus.
- **Haiku 4.5** — below the floor. Observed to skip Steps 6b / 8b / 8c — no `revised_answer` persistence, no intentional `gap_check` state, no final memo render — while generating plausible-looking output for the steps that didn't run.

The preamble asks the orchestrator to self-identify and refuse if it is Haiku. There is no machine-enforced floor — `$CLAUDE_MODEL` is not exposed by Claude Code — so the check relies on self-identification. Users on Sonnet or below should treat the `run_health` envelope surfaced in chat and the Observatory's completeness signals as the primary integrity check.

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
| V60 candidate extraction from lane outputs | **Deterministic** | Reads model IDs already surfaced by lanes, preserves lane/provenance reasons, dedupes by model ID |
| V60 embedding recall | **Probabilistic but additive** (cosine + query expansion) | Optional low-trust candidate source for affordance/absence opportunities; can add candidates but cannot remove lane-selected candidates |
| V60 affordance/absence packaging | **Deterministic** | Explicit `affordances_v60.json` lookup, caps, local relevance scoring within each model record, explicit record-order fallback telemetry, status/confidence/absence warnings, selected/skipped/not-presented telemetry |
| Step 6 V60 consideration | **Probabilistic with deterministic validation** | Claude/Codex decides use/reject/defer/private guardrail; ledger validation verifies every selected chunk was accounted for exactly once |

The curated substrate provides knowledge the LLM doesn't have: specific failure modes for Circle of Competence, the exact tension between Margin of Safety and Calculated Risk Taking, premortem questions that surface hidden assumptions, and V60 source-backed rules for when a mental-model affordance is legitimate or blocked. The deterministic middle ensures this knowledge reaches the skill runner faithfully. The user-facing answer may translate the mechanism into ordinary language; the exact substrate trace remains inspectable in Observatory and archived artifacts.

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
V60 affordance/absence records — source-backed transaction constraints
    ↓
Compiled graph artifacts (knowledge_graph.json, relationship_graph.json)
    ↓
Pre-computed embeddings (embeddings.db) — lowest-trust retrieval layer
    ↓
Runtime LLM judgment — suggests, does not decide routing
```

Embeddings suggest candidates. LLMs detect patterns. But every embedding hit still goes through LLM deep-check (tendency lane), LLM verification (companion lane), or private Step 6 consideration (V60 enrichment) before it affects the run. Every LLM detection gets routed through deterministic graph traversal or explicit V60 artifact lookup. The curated material governs the pressure; the user-facing answer shows the resulting reasoning improvement, while Observatory shows the exact substrate details.

### Observability as a First-Class Artifact

Every gated decision in Lolla produces a structured trace that travels with the result. When the routing tiebreaker consults the embedding matcher, the trace records whether the gate attempted, whether it fired, and if not, which check aborted it. When the Bullshit Index evaluates a passage, each subtype's detection and reasoning is preserved inline. When the detection funnel narrows from 25 tendencies to a handful of routes, each stage's input and output is captured. These traces are never log-only — they live in `audit_summary` and `run_health` next to the findings they explain.

The principle: if a probabilistic component can override or modify a deterministic ranking, the reason must be auditable without reading code. If a detector fires, the rationale must travel with the detection. The cost of a silent gate is a system that works until it doesn't, and when it doesn't, nobody can tell why. The cost of a trace is a few dozen bytes per decision.

Traces are read two ways. The Observatory renders the richer surfaces (findings, anchors, frame elements, gap questions, delivery audit) in context. `scripts/inspect_run.py` prints a compact terminal summary of the same result JSON — detection funnel, per-route tiebreaker status with abort reasons, delivery audit counts, card-level totals. Both read from the same artifact: the trace is the data, the viewer is interchangeable. Any future gate added to the pipeline (frame-pressure calibration, coverage thresholds, Phase 4/5 activation tuning, decomposed LLM specialists) should emit its own trace into the same `audit_summary` envelope so both surfaces pick it up automatically.

The `run_health` envelope decomposes run quality into named signals the chat flow can surface selectively:

- `overall`: `healthy` / `partial` / `degraded` / `critical`. Optional-off signals such as embeddings disabled by mode remain visible without degrading the run.
- `capture`, `substrate`, `embeddings`, `fingerprint`: per-subsystem status.
- `findings_produced`: whether Lane 1 produced any findings.
- `issues[]`: specific codes — `substrate_empty`, `embeddings_off`, `no_fingerprint`, `pipeline_warnings`, `capture_degraded`, `capture_critical`, `quote_fabrication`, `capture_truncated`, `lane3_all_dropped`, `bullshit_index_partial`, `stakeholder_check_failed`, `v60_enrichment_failed`, `v60_consideration_ledger_missing`, `v60_consideration_ledger_invalid`, `product_output_leak`, `live_output_leak`, `live_output_missing`, `live_output_unverified`.
- `issue_details[]`: structured issue records with `code`, `severity`, `axis`, `trust_impact`, and mode/count metadata. `overall` is computed from severity, not from the mere presence of any issue code.
- `warnings[]`: verbose text (pipeline warnings + capture warnings).
- `capture_manifest`: declared vs actual turn counts, char length, and truncation fields when applicable.
- Counts: `quote_fabrication_count`, `quote_retry_attempted`, `capture_truncated`, `omitted_turns`, `lane3_frame_drops_count`, `lane3_frame_kept_count`, `bullshit_index_evaluation_failures`.
- `activation_tiebreaker`: `on` / `off` (the per-route tiebreaker kill-switch).
- V60 transport: `v60_enrichment`, `v60_selected_chunk_count`, `v60_consideration_ledger`, `v60_consideration_transaction_count`, `v60_consideration_disposition_counts`, `v60_used_chunk_count`, `v60_presented_but_not_used_chunk_count`, `v60_unaccounted_chunk_count`.
- Product-output hygiene: `product_output_health`, `product_output_leak_count`, and leak details after archive finalization.
- Live-output hygiene: `live_output_health` (`clean`, `unsafe`, `missing`, or `not_checked`), `live_output_leak_count`, and leak details for the agent live transcript artifact. `clean` requires a trusted complete transcript; a clean manual artifact is `not_checked`.

The chat flow maps material issues to user-visible one-liners only when they affect trust in the run; the full envelope is available in the result JSON, Observatory, and `scripts/inspect_run.py`.

A companion diagnostic tool — `scripts/stability_check.py` — computes per-stage Jaccard / text-similarity across N runs. Three modes:

- **Mode A (aggregate)** — reads existing `result.json` files and computes pairwise Jaccard for Pass 1 tendencies, Lane 2 anchor model_ids, Lane 3 reframing grounding models, Lane 4 gap dimension_ids; plus Step 6 public-naming / output-hygiene rates and per-run token costs.
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

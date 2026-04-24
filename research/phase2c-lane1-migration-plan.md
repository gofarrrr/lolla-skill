# Phase 2c: Lane 1 (Structural Pressure) migration — plan

**Authored:** 2026-04-24
**Status:** plan for PM review; execution not started
**Prior lane migrations:** Phase 2a (Lane 3, PR #15 merged 2026-04-23), Phase 2b (Lane 4, PR #16 pending merge at planning time)
**Parent plan:** `research/phase2-lane-migration-plan.md`

## What Lane 1 does

Lane 1 is **Structural Pressure** — detects cognitive tendencies (Munger's "Psychology of Human Misjudgment" framework) in the AI's reasoning. It's the biggest and most coupled lane in the pipeline. Its orchestration spans ~250 lines of `pipeline.py`, two prompt-building modules, 25 tendency definitions, and ~20 per-tendency packet-adapter files.

Pipeline flow for Lane 1:

1. **Pass 1 — Family-clustered triage** (6 parallel OpenRouter calls via `_run_pass1_clusters_parallel`). Each cluster scores 3-5 tendencies. Inputs: `query + vanilla_answer`. Output: `triage_scores` list covering 24 canonical tendencies.
2. **Embedding swiss-cheese signal** (optional, uses `_embedding_tendency_signal(vanilla_answer)`) — promotes tendencies below LLM triage threshold if their curated guidance embeddings match the answer.
3. **Triggered tendency selection** (`_select_triggered_tendencies`) — threshold 4 + always-include + embedding hits.
4. **Pass 2 — Deep checks** (`_run_pass2_parallel`, one OpenRouter call per triggered tendency, up to 8 concurrent). Inputs: `query + vanilla_answer + tendency_key`. Output: `DeepCheckResult` per tendency with `sub_pattern`, `passage`, `severity`.
5. **Deterministic routing + assembly** — knowledge-graph lookup, fan correction, activation tiebreaker, DeltaCard construction.

Lane 1 **drives** the rest of the pipeline via its outputs:
- `lane1_tendency_ids` → Lane 3 overlap detection + anti-echo
- `lane1_model_ids` (selected) → Lanes 2, 3, 4 anti-echo
- Compound patterns → lollapalooza flagging

## What Lane 1 currently consumes

Both Pass 1 and Pass 2 consume the legacy `CritiqueRequest`:
- `query` (extractor-paraphrased decision_situation + constraints + framing + dropped_threads)
- `vanilla_answer` (synthesized_position preamble + concatenated assistant turns, capped 40K chars)

The embedding signal also uses `vanilla_answer`.

Every Pass 1 cluster's user prompt (`PASS_1_TRIAGE_USER` template in `prompts.py`) formats `query` + `vanilla_answer` into a single block. Every Pass 2 call (`format_pass2_prompt` in `deep_checks.py`) does the same per-tendency with a sub-pattern menu appended.

## Input shape decision

**This is the first Phase 2 lane where SOURCE is primarily the ASSISTANT's turns, not the user's.** Lane 1 audits the AI's reasoning (commissions + omissions). The evidence of a tendency lives in what the assistant said (or failed to say when the query made an omission material).

### Proposed:

- **SOURCE** (primary — what Lane 1 scores):
  - All assistant turns, verbatim, turn-structured
  - The LLM reads these for commissions (tendencies that surface in assistant text) and omissions (material checks/denominators/dependencies/reversals the assistant skipped)
- **CONTEXT** (secondary — scaffolding for understanding the query's live elements):
  - User turns (so Pass 1 can see what the user made live — especially for omission detection)
  - Extraction summaries: decision_situation, original_framing, live_constraints, dropped_threads
  - These are NOT citable as passage evidence for detected tendencies

This is a **third distinct SOURCE pattern** across Phase 2:
- 2a Lane 3: SOURCE = user turns (audits how the user posed the question)
- 2b Lane 4: SOURCE = user + assistant turns (audits coverage across both sides)
- 2c Lane 1: SOURCE = assistant turns (audits the assistant's reasoning specifically)

Justification: Pass 1's `PASS_1_TRIAGE_USER` already labels `query` as "context only — use for what the answer skipped" and `vanilla_answer` as the primary audit target. The architectural shift is preserving that priority while giving Pass 1 access to turn-structured assistant content instead of the flattened concatenation.

## Couplings to other lanes (this is why Lane 1 is "most coupled")

| coupling | mechanism | 2c migration risk |
|---|---|---|
| Lane 2 anti-echo | `lane1_model_ids` excluded from Lane 2 candidate set | if new-path Lane 1 selects a different set of models, Lane 2 candidate pool shifts |
| Lane 3 anti-echo + overlap | `lane1_tendency_ids` + `lane1_model_ids` used | same cascade risk |
| Lane 4 anti-echo | `lane1_model_ids` in triple-lane exclusion | same |
| Compound detection | `compound_catalog` matches tendency sets | if triggered tendencies shift, compound groups shift |
| Activation tiebreaker | uses reasoning context embeddings | new-path may build different context strings for tiebreaker |

None of these are blockers; all are **data-path cascades** to watch. The post-2b measurement showed Lane 4 catches shifting dimensions; same observation will apply here. The aggregate measurement must include the *downstream* lane outputs on both paths to see whether 2c's Lane 1 changes materially shift Lanes 2/3/4 outputs via anti-echo.

## Measurement plan

Same three-angle structure as 2a/2b (required, per phase2-lane-migration-plan.md):

### Angle 1: Controlled Marcus A/B

Same conversation (`lolla_20260422T155622Z_conversation.txt`), same fresh extraction, only input shape differs. Capture:
- `detected_tendencies` set on each path (stability within N=1 — deterministic routing expected)
- `delta_card.findings` with challenge statements + corrective models
- Coverage-evidence-style attribution: does new-path Lane 1 cite verbatim from assistant turns vs. paraphrase-style?

Primary hypothesis: on Marcus, new path audits assistant's actual reasoning turns (e.g., specific stakes claims, specific reasoning leaps) with evidence that reads as "Assistant claims X" rather than summary-style "Assumes X."

### Angle 2: 10-case corpus measurement

N=3 per path per case × 10 cases = 60 runs total. Structural metrics:
- `detected_tendencies_count` per run — are the same tendencies being triggered?
- `detected_tendencies_stability` across N=3 — both paths stable or noisy?
- `delta_card_findings_count` per run — top-tier + secondary
- `compound_groups_count` — lollapalooza patterns
- Downstream-propagation metrics: `lane2_model_ids_size`, `lane3_tendency_ids_size`, `lane4_gap_count` on both paths — did Lane 1 changes cascade?

### Angle 3: Architecture-vs-volume ablation

One case, trimmed SOURCE prompt for Pass 1 — test whether turn-structured assistant text (vs. flattened vanilla_answer) is the load-bearing feature independent of content volume. Same pattern as 2a's `phase2a_lane3_ablation_*` and 2b's `phase2b_ablation_architecture_vs_volume.py`.

### Quality thresholds (approved in 2a, reused)

- Per-case detected_tendencies stability: within ±1 from old-path median across N=3
- No negative-check trips: empty delta_card where old-path had findings; tendency instability across runs
- Qualitative read on ≥3 cases rated "new ≥ old" on audit quality
- Aggregate: zero regressions by the per-case gate

## Risks specific to Lane 1

### High risk

1. **Scale of prompt surface.** 6 dynamic cluster system prompts + 1 Pass 2 system prompt + 2 user prompt templates + 25 tendency guidance + 20+ sub-pattern menus. Biggest prompt surface in the whole rearchitecture. Prompt iteration (per 2b's lesson) will be costlier to test — need to budget for it.
2. **Anti-echo cascade.** If new path produces a different `selected_model_ids` set, Lanes 2/3/4 see different anti-echo exclusion sets and may shift output. The measurement must capture downstream-lane metrics, not just Lane 1's own output.
3. **Compound-group sensitivity.** Lollapalooza compounds depend on tendency co-occurrence. If new path triggers slightly different tendency sets, compound groups form differently. This is observable quality, not a mechanical regression.

### Medium risk

4. **Per-tendency packet adapters** (`*_deep_check_packet_adapter.py`, ~20 files). Each maps Pass 2 JSON output to sub-pattern. They DON'T consume the user prompt directly — they parse the LLM response. Migration should NOT touch them. But if the new Pass 2 user prompt structure changes what the LLM responds with (e.g., different sub-pattern choices), adapter behavior shifts indirectly.
5. **Embedding tendency signal.** Uses `vanilla_answer`. New path needs an equivalent `_embedding_tendency_signal_from_context` that uses the joined assistant-turn text — or reuses the existing signal with the flattened concatenation. Lean: reuse with flattened text from context, to keep the embedding signal behavior identical across paths.
6. **Activation tiebreaker** in routing uses a reasoning context string. New path's string may be different from old path's (different ordering/structure), potentially changing the tiebreaker outcome on δ<0.01 near-ties. Low frequency event but measurable.

### Low risk

7. **Enum checklist oversight (durable 2b lesson).** Pass 1 clusters already enumerate 3-5 tendencies per cluster — that's essentially a built-in checklist. But Pass 2 receives one tendency at a time and audits for sub-patterns. The enum-space for Pass 2 is the sub-pattern menu. We need the same "consider all sub-patterns including implicit ones" reminder in the Pass 2 system prompt when migrated. **Bake into the FIRST DRAFT per 2b lesson; don't wait for measurement to force iteration.**

## 2b template transferability

Mostly transfers, with structural additions:

- **New entry points × 2 call paths** (Pass 1 + Pass 2), not 1 like Lane 3 or 3 like Lane 4's classification/detection/gap-questions (though those all live in one module).
- **User prompt formatters × 2** (cluster prompts + deep-check prompt). Each gets a `_from_context` variant.
- **System prompts × 6+1 = 7** potentially affected. In practice: the cluster system prompts describe cluster membership + confusion guardrails (not input shape); they likely need small tweaks rather than full rewrites. The Pass 2 system prompt needs the CONTEXT/SOURCE + enum-checklist additions.
- **Pipeline.py dispatch × 2 call sites** (`_run_pass1_clusters_parallel` + `_run_pass2_parallel`). Larger surface than Lane 3/4 but mechanically the same pattern (optional `conversation_context` param, dispatch on presence).

**Verdict:** 2b template transfers, but larger. No architectural reshape needed; just more mechanical surface to touch. Risk of the change blast-radius is real (more places = more paths for subtle bugs). Mitigation: keep the shim path fully intact throughout (legacy functions stay alongside `_from_context` variants, same as 2a/2b).

## Out of scope for Phase 2c

- **Track A** (specialist extraction calls) stays deferred
- **Per-tendency packet adapters** not migrated (they parse LLM output; shape doesn't change)
- **Pilot bridges** (authority, stress, overoptimism) — partial implementations; don't touch
- **`CritiqueRequest` removal** — Phase 3
- **`pipeline.py` structural refactor** — Phase 4

## After Phase 2c ships

- Phase 2d (Lane 2 Companion) is the last lane migration. Companion does its own fingerprint extraction from vanilla_answer, so the migration impact is different from 1/3/4 — may be smaller.
- Phase 3: remove `CritiqueRequest` + `_context_to_critique` + shim dispatch.
- Phase 4: split `pipeline.py` into per-lane modules.

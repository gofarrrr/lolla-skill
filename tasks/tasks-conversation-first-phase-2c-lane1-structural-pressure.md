# Phase 2c: Lane 1 (Structural Pressure) — migrate to ConversationContext

**Branch:** `feat/conversation-first-phase-2c-lane1-structural-pressure`
**Phase plan:** `research/phase2c-lane1-migration-plan.md`
**Parent plan:** `research/phase2-lane-migration-plan.md`
**Handover:** `research/conversation-first-rearchitecture-handover.md`
**Audit:** `research/full-system-audit-2026-04-23.md` §3 (Lane 1)
**Prior PR templates:** Phase 2a (PR #15, merged) + Phase 2b (PR #16, pending merge at planning time)
**Scope:** migrate Lane 1 (Structural Pressure: Pass 1 family-clustered triage + Pass 2 per-tendency deep checks) to consume `ConversationContext` directly. Legacy `run_*` entry points stay alongside the new path and continue serving the shim. Other three lanes unchanged.

## Why this PR

Lane 1 is the biggest and most coupled lane in the pipeline — it audits the assistant's reasoning for cognitive tendencies (Munger framework) via 6 parallel Pass 1 cluster calls + per-tendency Pass 2 deep-check calls. Its output (`lane1_model_ids`, `lane1_tendency_ids`) drives anti-echo in Lanes 2/3/4 and compound detection.

Under the current `CritiqueRequest` shape, Pass 1 and Pass 2 both consume a collapsed `query + vanilla_answer`. The assistant's reasoning is flattened into `vanilla_answer` (synthesized_position preamble + `\n\n---\n\n`-joined assistant turns capped 40K chars). Lane 1 detects commissions and omissions on that flattened text — losing turn-level structure that could sharpen evidence quotes and omission-detection.

Phase 2c gives Lane 1 access to turn-structured assistant content. Phase 2a's evidence-grounding pattern (user turns cited verbatim for Lane 3) and 2b's coverage-evidence attribution pattern (assistant turns explicitly named for Lane 4 coverage) both apply here — Pass 1 challenge statements and Pass 2 sub-pattern passages should cite what the assistant actually said in specific turns, not paraphrases of the flattened compilation.

This PR is **the largest surface-area migration** in Phase 2. Expect more prompt iteration than 2a/2b. The 2b lesson (bake enum-checklist reminder into first-draft prompts) applies here to Pass 2 sub-pattern detection.

## Relevant files

- `engine/system_b/prompts.py` — **primary file** (260 lines). Contains `PASS_1_TRIAGE_USER` template + `build_cluster_system_prompt` + `format_pass1_cluster_prompts`. 6 dynamically-built cluster system prompts.
- `engine/system_b/deep_checks.py` — **primary file** (385 lines). Contains `PASS_2_DEEP_CHECK_SYSTEM` template + `format_pass2_prompt` + `build_sub_pattern_menu` + `build_tendency_guidance` + `parse_pass2_result`.
- `engine/system_b/pipeline.py` — thread `ConversationContext` from `run()` (already held from 2a) into `_run_pass1_clusters_parallel` + `_run_pass2_parallel` + `_embedding_tendency_signal`. Both Pass 1 and Pass 2 dispatch based on context presence.
- `tests/test_lane1_contextual.py` — **NEW**. TDD for the new entry points (separate tests for Pass 1 and Pass 2).
- `scripts/phase2c_lane1_quality_check.py` — **NEW**. Adapted from `scripts/phase2b_lane4_quality_check.py`; measures Lane 1 structural metrics across 10-case corpus N=3 + downstream-lane cascade metrics.
- `HOW_IT_WORKS.md` §Step 3 — Lane 1 section gets a Phase 2c migration paragraph.
- `research/conversation-first-rearchitecture-handover.md` — "What's shipped" update on merge.

### Notes

- Test runner: `python3 -m pytest tests/test_lane1_contextual.py -v`
- The 10-case corpus is at `research/test-cases/case_*_conversation.txt`.
- **Don't touch** Lanes 2, 3, 4 directly. But DO measure their output on both paths in task 6.0 to catch anti-echo cascade effects.
- **Don't delete** legacy Pass 1/Pass 2 entry points — they serve the shim path until Phase 3.
- **Don't touch** per-tendency packet adapters (`*_deep_check_packet_adapter.py`). They parse LLM output; their shape doesn't change.
- **Don't touch** activation tiebreaker or deterministic routing. Those operate downstream of Pass 2 on DeepCheckResult output, not on input shape.

## Acceptance gate

Same four-signal shape as 2a/2b, adapted for Lane 1's output surface + downstream cascade:

| Axis | Target |
|---|---|
| New unit tests for conversation-aware entry points | ≥ 8 new tests (Pass 1 + Pass 2 + dispatch), all green |
| Full test suite | zero regression from current baseline |
| Lane 1 structural metrics across 10-case corpus N=3 | see below |
| Downstream cascade metrics | see below |
| Qualitative human read | ≥ 2/3 cases rated "new ≥ old" on Lane 1 output (proper markdown diff, not `[~]`) |
| Negative-check gate | zero trips on any case |
| HOW_IT_WORKS.md updated | yes |

**Lane 1 structural metrics (Pass 1 + Pass 2):**

- `detected_tendencies_count` per run (triggered + routed)
- `triage_scores` stability — same tendencies scoring above threshold across N=3?
- `delta_card_findings_count` — top tier + secondary
- `compound_groups_count` — lollapalooza detections
- Pass 2 sub_pattern selection — which sub-patterns the LLM picks per-tendency

**Downstream cascade metrics (required for Lane 1 specifically):**

- `lane2_model_ids_size` on both paths — did Lane 1's anti-echo set shift Lane 2?
- `lane3_tendency_ids_size` + `lane3_frame_elements_count`
- `lane4_gap_count`
- Cross-lane overlap — are Lanes 2/3/4 excluding different models on new vs old path?

**Partial-regression policy (approved 2a, reapplied 2b):** if any case regresses, diagnosis required in PR description. Two undiagnosed regressions = block. Diagnosed regressions with named tradeoffs = ship. No "within noise" hand-waving.

**Negative-check criteria for Lane 1:**
- (a) Non-empty `DeltaCard.findings` on old path → empty findings on new path for same case
- (b) `detected_tendencies` disagreement >50% across N=3 new-path runs on a case where old path was stable
- (c) Compound group collapse (old had compound, new path loses all compounds for a case that should have them)
- (d) Cascade: Lane 2/3/4 output on new path materially empty where old was populated

## Tasks

- [x] 0.0 Preflight
  - [ ] 0.1 Confirm PR #16 (Phase 2b) merged to main: `git log --oneline main -10`. If not yet merged: **STOP, wait for merge.** 2c builds on 2b's pipeline.py state (Lane 4 dispatch) + 2b's conversation_context plumbing.
  - [ ] 0.2 Fresh main + branch: `git checkout main && git pull && git checkout -b feat/conversation-first-phase-2c-lane1-structural-pressure`.
  - [ ] 0.3 Verify Phase 1+2a+2b scaffolding: `ls engine/system_b/conversation_context.py engine/system_b/conversation_loader.py engine/system_b/frame_pressure.py engine/system_b/structural_coverage.py scripts/phase2a_lane3_quality_check.py scripts/phase2b_lane4_quality_check.py` (all present).
  - [ ] 0.4 Run `pytest tests/ -q` — confirm passing baseline.
  - [ ] 0.5 Re-read: `research/phase2c-lane1-migration-plan.md` (couplings + risks), `research/test-cases/phase2b-marcus-controlled-comparison-2026-04-23/README.md` (the coverage-evidence attribution pattern), `research/test-cases/phase2b-lane4-equivalence-2026-04-23/lane4-quality-report.md` (what "success with prompt iteration" looks like). Read `engine/system_b/prompts.py` + `engine/system_b/deep_checks.py` in full.
  - [ ] 0.6 Map Lane 1 orchestration in `pipeline.py` lines 375-551 — identify the two call sites for `_run_pass1_clusters_parallel` and `_run_pass2_parallel`. Both need `conversation_context` passed through.

- [x] 1.0 Conversation-aware Pass 1 + Pass 2 entry points (TDD)
  - [ ] 1.1 Design user-prompt shape for Pass 1 (cluster triage):
    - CONTEXT section: user turns + extraction summaries (decision_situation, original_framing, constraints, dropped_threads). Marked "NOT the primary audit target."
    - SOURCE section: assistant turns verbatim, turn-structured. Marked "primary audit target — tendencies live here (commissions + omissions)."
  - [ ] 1.2 Design user-prompt shape for Pass 2 (per-tendency deep check):
    - Same CONTEXT/SOURCE split as Pass 1.
    - Plus: explicit sub_pattern menu + tendency guidance (already present in legacy).
  - [ ] 1.3 RED→GREEN: add `format_pass1_cluster_prompts_from_context(context, catalog)` in `prompts.py`. Returns the same list-of-dicts shape as legacy. Unit test with synthetic context + mocked boundary; verify CONTEXT/SOURCE markers in user prompt.
  - [ ] 1.4 RED→GREEN: add `format_pass2_prompt_from_context(context, tendency_key, catalog)` in `deep_checks.py`. Unit test similar to 1.3.
  - [ ] 1.5 RED→GREEN: add helper `_joined_assistant_turns_text(context)` if not present (analogous to Lane 3's `_joined_user_turns_text`). Can live in `conversation_context.py` or a new helper module. Used by Pass 1 + Pass 2 + embedding signal.
  - [ ] 1.6 RED→GREEN: add `_embedding_tendency_signal_from_context(context, ...)` OR decide to reuse legacy with `_joined_assistant_turns_text(context)` as input. Lean: reuse — embedding signal behavior should be stable across paths; only the input assembly changes.

- [x] 2.0 Prompts: CONTEXT/SOURCE + RIGHT/WRONG + enum-checklist (first draft, per 2b lesson)
  - [ ] 2.1 Decide whether to rewrite the 6 Pass 1 cluster system prompts or just adjust the user-prompt template. Lean: minimal system prompt changes (one sentence about reading turn-structured input); rewrite the user prompt template with CONTEXT/SOURCE split.
  - [ ] 2.2 Pass 1 user prompt: CONTEXT section labelled "not the primary audit target"; SOURCE section with `[Turn N] ASSISTANT:` blocks; RIGHT/WRONG examples for evidence grounding (e.g., RIGHT: "The assistant claims X"; WRONG: paraphrase of X; WRONG: summary of extraction).
  - [ ] 2.3 Pass 2 system prompt: add CONTEXT/SOURCE wording + **enum-checklist reminder for sub-patterns** (per 2b lesson). Explicit: "Before finalizing sub_pattern selection, verify you've considered each sub_pattern in the menu — not just the ones that surface in assistant verbatim. Some sub-patterns manifest as omission or implicit bias rather than stated claims." Bake this into FIRST DRAFT, don't wait for measurement to force iteration.
  - [ ] 2.4 Pass 2 user prompt: CONTEXT/SOURCE split; `[Turn N] ASSISTANT:` structure.

- [x] 3.0 `pipeline.py` dispatch wiring
  - [ ] 3.1 Read current `_run_pass1_clusters_parallel` signature (pipeline.py ~line 943) + `_run_pass2_parallel` signature + `_embedding_tendency_signal` signature.
  - [ ] 3.2 Add `conversation_context: ConversationContext | None = None` to each; dispatch on presence (if context → `_from_context` variant; else legacy).
  - [ ] 3.3 Pass `conversation_context=conversation_context` at call sites in `run()`. Should already be held from 2a (Line 457-ish).
  - [ ] 3.4 RED→GREEN: extend `tests/test_pipeline_shim_equivalence.py` with dispatch tests for Pass 1 + Pass 2 (context-path, legacy-path, feature-disabled short-circuits already covered).
  - [ ] 3.5 Run full suite — zero regression.

- [x] 4.0 Anti-echo preservation
  - [ ] 4.1 Verify `lane1_tendency_ids` + `lane1_model_ids` are computed identically between paths when context is present. These are aggregated from `detected_tendencies` + `delta_card.selected_model_ids`; migration shouldn't change aggregation logic.
  - [ ] 4.2 Add a test asserting that downstream lane calls (`_run_companion`, `_run_frame_pressure`, `_run_structural_coverage`) receive correctly-populated `lane1_*_ids` sets on the new path.
  - [ ] 4.3 Spot-check: on the Marcus controlled A/B, confirm Lanes 2/3/4 receive a reasonable anti-echo set on both paths (not wildly different).

- [x] 5.0 Quality-metrics script
  - [ ] 5.1 Adapt `scripts/phase2b_lane4_quality_check.py` into `scripts/phase2c_lane1_quality_check.py`. Same resilient-resume structure.
  - [ ] 5.2 Metrics to capture: Lane 1 output (detected_tendencies, delta_card findings count, compound groups count) + **downstream cascade metrics** (lane2_model_ids size, lane3_tendency_ids size, lane4_gap_count) per run.
  - [ ] 5.3 Dry-run: `--n 1 --cases oncologist` to verify plumbing end-to-end.

- [x] 6.0 Full N=3 × 10-case measurement + controlled Marcus A/B + ablation
  - [ ] 6.1 Run `scripts/phase2c_lane1_quality_check.py --n 3` in background (~45-60 min, ~$5-10 — larger than 2a/2b because Lane 1 makes 6+N boundary calls per pipeline run).
  - [ ] 6.2 **Controlled Marcus A/B** — reuse `research/test-cases/phase2b-marcus-controlled-comparison-2026-04-23/marcus_fresh_extraction.json`. Run old path + new path on Marcus, compare Lane 1 output + downstream cascades. Save to `research/test-cases/phase2c-marcus-controlled-comparison-2026-04-24/`. **Primary PR evidence.**
  - [ ] 6.3 **Ablation on friendship_money** (or whichever case shows the clearest architectural signal): SOURCE kept = assistant turns; CONTEXT trimmed to old-path-volume. Same pattern as 2a/2b ablations. Save to `scripts/phase2c_ablation_architecture_vs_volume.py`.
  - [ ] 6.4 **Per-case regression check.** Apply diagnosis-required policy.

- [x] 7.0 Qualitative human read (PROPER markdown diff, NOT `[~]`)
  - [ ] 7.1 Pick 3 cases spanning variance: one clean (friendship_money or startup_pivot), one messy (messy_three_problems or parenting_teen), one edge-case (phd_research longest OR whistleblower densest).
  - [ ] 7.2 Render side-by-side diff for each case: old path's delta_card.findings vs new path's. Include challenge_statement + passage + corrective_model per finding.
  - [ ] 7.3 Commit to `research/test-cases/phase2c-lane1-equivalence-2026-MM-DD/lane1-qualitative-diff.md`.
  - [ ] 7.4 Surface to PM for review. ≥ 2/3 rated "new ≥ old" to proceed.

- [x] 8.0 Negative-check gate
  - [ ] 8.1 Scan 30 new-path runs for criteria (empty delta_card, tendency disagreement >50% within N=3, compound collapse, cascade empty-lane events).
  - [ ] 8.2 Zero trips = proceed. Any trip = STOP, diagnose.

- [x] 9.0 Documentation
  - [ ] 9.1 Update `HOW_IT_WORKS.md §Step 3` Lane 1 section with a Phase 2c migration paragraph (parallel structure to Lane 3/4's).
  - [ ] 9.2 Defer handover "What's shipped" to post-merge.

- [ ] 10.0 Ship
  - [ ] 10.1 Full test suite green.
  - [ ] 10.2 Push + open PR. Title: `feat(pipeline): Lane 1 (Structural Pressure) migrated to ConversationContext (phase 2c)`.
  - [ ] 10.3 PR description leads with: (a) Controlled Marcus Lane 1 A/B (primary evidence — same detected_tendencies, attribution shift); (b) 10-case aggregate + per-case regression diagnoses; (c) downstream-cascade analysis; (d) iteration story if any occurred (durable lesson for 2d); (e) acceptance-gate table.
  - [ ] 10.4 On merge: update handover "What's shipped" with PR #, metrics summary, rollback path.

## Phase 2d preview (do NOT do in this PR)

After 2c merges, Phase 2d migrates Lane 2 (Companion). Lane 2 does its own fingerprint extraction from vanilla_answer, so the migration impact may be smaller than 1/3/4 — the content access pattern is already turn-independent within Companion's internal logic. See `research/phase2-lane-migration-plan.md`.

## Risks

1. **Surface area.** Lane 1's prompt surface is ~3-4× bigger than Lane 3's or Lane 4's. Budget for prompt iteration. If first-draft prompts produce under-triggering or over-triggering, an iteration-cycle (per 2b pattern) is the expected path.
2. **Anti-echo cascade.** Measurement must capture downstream-lane metrics on both paths. If new-path Lane 1 produces a different selected_model_ids set, Lanes 2/3/4 will see different anti-echo; that's observable Lane-1-specific behavior, not a regression, but PR description should name it explicitly.
3. **Compound-group sensitivity.** Lollapalooza compounds depend on tendency co-occurrence. Different triggered sets → different compounds. Qualitatively judge on ≥3 cases whether compound changes are upgrades or regressions.
4. **Cost overrun.** Lane 1 makes 6+N boundary calls per pipeline run. N=3 × 10 cases × 2 paths with average N_triggered=~5 means ~10 × 2 × 3 × (6 + 5) = ~660 Pass-1-or-Pass-2 calls + 60 extractions ≈ $8-15 total measurement cost. Budget for it.
5. **LLM variance at scale.** More calls = more variance surface. 0-findings anomaly rate may appear (analog to 2b's 0-gap-qs). Diagnose the same way (N=5 re-run + targeted inspection) if it shows.

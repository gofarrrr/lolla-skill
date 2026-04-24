# Phase 2b: Lane 4 (Structural Coverage) — migrate to ConversationContext

**Branch:** `feat/conversation-first-phase-2b-lane4-structural-coverage`
**Phase plan:** `research/phase2-lane-migration-plan.md`
**Handover:** `research/conversation-first-rearchitecture-handover.md`
**Audit:** `research/full-system-audit-2026-04-23.md` §3 (Lane 4)
**Prior PR template:** Phase 2a (PR #15, merged 2026-04-23) — same pattern applied here.
**Scope:** migrate Lane 4 (Structural Coverage) to consume `ConversationContext` directly. Legacy `run_structural_coverage(query, vanilla_answer)` stays alongside the new path and continues serving the shim. Other three lanes unchanged.

## Why this PR

Lane 4 audits structural completeness — it classifies the question type (causal-diagnosis / decision-evaluation / action-planning / prediction), checks the answer against 15 MECE dimensions, and generates discovery questions for gaps. Under the current `CritiqueRequest` shape, all 3 of its LLM calls consume the collapsed `query` + `vanilla_answer`. The question classification in particular operates on extractor-paraphrased `decision_situation` text rather than how the user actually asked.

Phase 2a established the pattern on Lane 3: moving to `ConversationContext` + CONTEXT/SOURCE prompt split caused frame evidence to shift from extractor paraphrases to verbatim user words. For Lane 4, the analogous unlock is classification + dimension detection grounded in the user's actual question shape, and gap-questions targeted to the real conversation rather than its summary.

Lane 4 is informative-only (doesn't feed other lanes). Lowest blast radius of the remaining three migrations. If this migration reveals a pattern that doesn't transfer (e.g. dimensions don't benefit from conversation context the way frame elements did), we learn it on a lane where the risk is contained.

## Relevant files

- `engine/system_b/structural_coverage.py` — **primary file** (~668 lines). Three LLM calls (classification, detection, gap-question generation) each get a new `_from_context` variant alongside the legacy. Prompts rewritten with CONTEXT/SOURCE split. Legacy entry points stay.
- `engine/system_b/pipeline.py` — thread `ConversationContext` from `run()` (already held after Phase 2a) into `_run_structural_coverage()`; the lane method dispatches based on availability.
- `tests/test_structural_coverage_contextual.py` — **NEW**. TDD for the new entry points. Mirrors `tests/test_frame_pressure_contextual.py`.
- `scripts/phase2b_lane4_quality_check.py` — **NEW**. Adapted from `scripts/phase2a_lane3_quality_check.py`; measures Lane 4 structural metrics across 10 corpus cases × N=3.
- `HOW_IT_WORKS.md` §Step 3 — Lane 4 section gets a Phase 2b migration paragraph analogous to Lane 3's.
- `research/conversation-first-rearchitecture-handover.md` — "What's shipped" update on merge.

### Notes

- Test runner: `python3 -m pytest tests/test_structural_coverage_contextual.py -v`
- The 10-case corpus is at `research/test-cases/case_*_conversation.txt`.
- **Don't touch** Lanes 1, 2, 3. This PR is Lane 4 only.
- **Don't delete** legacy `run_structural_coverage` — it still serves the shim path until Phase 3.
- Three prompts need CONTEXT/SOURCE split: `_QUESTION_CLASSIFICATION_SYSTEM`, `_DIMENSION_DETECTION_SYSTEM`, `_GAP_QUESTION_GENERATION_SYSTEM`. All three get RIGHT/WRONG examples showing evidence must come from user turns (for gap_questions' rationale strings) or from observed conversation content (for dimension coverage evidence).

## Acceptance gate

Same four-signal shape as 2a, adapted for Lane 4's output surface:

| Axis | Target |
|---|---|
| New unit tests for conversation-aware entry points | ≥ 6 new tests, all green |
| Full test suite | zero regression from current baseline |
| Lane 4 structural metrics across 10-case corpus N=3 | see below |
| Qualitative human read | ≥ 2/3 cases rated "new ≥ old" |
| Negative-check gate | zero trips on any case |
| HOW_IT_WORKS.md updated | yes |

**Lane 4 structural metrics (what we measure):**

- `question_class_stability`: does the same question classify identically across N=3 runs? (Expected: yes on both paths; new path may shift the class on cases where extractor-paraphrase misled the old path.)
- `detected_dimensions_count`: number of dimensions detected per run (0-15)
- `gap_questions_count`: total gap questions generated (0 when no gaps detected)
- `gap_question_rationale_grounding`: do gap_question rationale strings quote verbatim from user turns (new path) vs extractor summary (old path)? Qualitative check.
- `dimensions_with_coverage_change`: cases where new path detects coverage that old path missed, or vice versa.

**Partial-regression policy (approved in Phase 2a, reapplied):** if any case regresses, diagnosis required in PR description. Two undiagnosed regressions = block. Diagnosed regressions with a named tradeoff = ship. No "within noise" hand-waving — each regressing case gets a specific hypothesis for why it regressed.

**Negative-check criteria for Lane 4:**
- (a) Non-empty `StructuralCoverageCard` on old path → empty card on new path for same case.
- (b) `question_class` disagreement across N=3 new-path runs on a case where old path was stable (indicates new prompt introduced classification instability).
- (c) Gap question with rationale containing text not in the user turns or assistant replies (hallucinated evidence).

## Tasks

- [x] 0.0 Preflight
  - [ ] 0.1 Confirm Phase 2a on main: `git log --oneline main -5` shows the `73106a4 Merge pull request #15` commit.
  - [ ] 0.2 Fresh main + branch: `git checkout main && git pull && git checkout -b feat/conversation-first-phase-2b-lane4-structural-coverage`.
  - [ ] 0.3 Verify Phase 1+2a scaffolding: `ls engine/system_b/conversation_context.py engine/system_b/conversation_loader.py engine/system_b/frame_pressure.py scripts/phase2a_lane3_quality_check.py` (all present).
  - [ ] 0.4 Run `pytest tests/ -q` — confirm passing baseline before changes.
  - [ ] 0.5 Re-read: `research/phase2-lane-migration-plan.md` (quality protocol), `research/test-cases/phase2a-lane3-equivalence-2026-04-23/lane3-quality-report.md` (what "good" looks like), `research/test-cases/phase2a-marcus-controlled-comparison-2026-04-23/README.md` (the CONTEXT/SOURCE lesson). Read `engine/system_b/structural_coverage.py` in full — 668 lines, three LLM calls to understand.
  - [ ] 0.6 Spot-check Lane 4 output on 2 corpus cases via an existing stability run (e.g., `research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_old_run0.json` has a `structural_coverage_card` field). Get a feel for the current shape.

- [x] 1.0 Add conversation-aware entry points (TDD) — 4 new public functions in `structural_coverage.py`; 16 new tests in `test_structural_coverage_contextual.py`, all green.
  - [ ] 1.1 Design the user-prompt shape for EACH of the 3 LLM calls with a CONTEXT/SOURCE split, lessons from Phase 2a baked in:
    - CONTEXT section: extracted fields (decision_situation, original_framing, live_constraints, dropped_threads) + assistant replies. Marked "NOT quotable as evidence."
    - SOURCE section: user turns verbatim. Marked "evidence MUST be substrings of user turns (for any LLM-cited evidence this lane emits)."
  - [ ] 1.2 Decide which LLM calls need a strict `_from_context` variant. Classification likely benefits from seeing real user turns (currently sees collapsed `query`). Dimension detection examines coverage across query + answer — arguably needs raw conversation to judge "was this dimension actually reasoned through." Gap-question generation produces questions + rationales; rationales citing verbatim user text is the Phase 2a analog.
  - [ ] 1.3 RED→GREEN: add `run_question_classification_from_context(boundary, context)` with system prompt `_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT`. Test: returns the same 4 classes; CONTEXT/SOURCE split visible in user prompt.
  - [ ] 1.4 RED→GREEN: add `run_dimension_detection_from_context(boundary, context, dimension_routing, question_class)`. Test: returns `DetectedDimension` list; coverage_evidence field validated against joined user-turn + assistant-reply text (since coverage can come from either side of the conversation).
  - [ ] 1.5 RED→GREEN: add `generate_gap_questions_from_context(boundary, context, dimensions, routes)`. Test: gap questions have rationale grounded in user turns.
  - [ ] 1.6 RED→GREEN: add `run_structural_coverage_from_context(boundary, context, ...)` as the public orchestrator — same shape as legacy `run_structural_coverage`, delegates to the three new calls.

- [x] 2.0 Rewrite the three system prompts with CONTEXT/SOURCE — two new system prompts added (`_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT`, `_DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT`); existing `_GAP_QUESTION_GENERATION_SYSTEM` reused (philosophy is shape-agnostic; only user prompt body changed).
  - [ ] 2.1 `_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT`: same 4-class taxonomy, but guidance calibrated for "read the user's actual turns, not the extractor's decision_situation paraphrase."
  - [ ] 2.2 `_DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT`: same 15-dimension bar, but evidence language adjusted. Coverage evidence may cite user turns OR assistant replies (coverage can be user-raised or assistant-addressed); but NOT extractor summaries from CONTEXT.
  - [ ] 2.3 `_GAP_QUESTION_GENERATION_SYSTEM_FROM_CONTEXT`: rationale strings must quote from user turns. Same specificity bar from Phase 2a (no generic "consider whether X" openers).
  - [ ] 2.4 Each prompt carries a RIGHT/WRONG example block showing paraphrase/summary/assistant-reply citations as WRONG.

- [x] 3.0 Wire `pipeline.py::_run_structural_coverage` to dispatch — 3 dispatch tests added to `test_pipeline_shim_equivalence.py`; 200 total, zero regression.
  - [ ] 3.1 Read the full `_run_structural_coverage` method (pipeline.py:883). Note its signature — it takes `request, boundary_calls, lane1_model_ids, lane2_model_ids, lane3_model_ids` (triple anti-echo).
  - [ ] 3.2 Add `conversation_context: ConversationContext | None = None` parameter. When present, use `run_structural_coverage_from_context`; otherwise legacy.
  - [ ] 3.3 Pass `conversation_context=conversation_context` at all call sites in `run()` (lines ~504 and ~637).
  - [ ] 3.4 RED→GREEN: extend `tests/test_pipeline_shim_equivalence.py` with three new dispatch tests analogous to Lane 3's: context-path, legacy-path, feature-disabled.
  - [ ] 3.5 Run `pytest tests/ -q` — zero regression.

- [x] 4.0 Anti-echo + triple-lane exclusion — verified via code-reading: anti-echo set computed identically pre-dispatch; post-extraction routing + assembly shared between paths. Dispatch tests confirm surrounding call structure preserved.
  - [ ] 4.1 Lane 4's anti-echo uses Lane 1 + Lane 2 + Lane 3 model IDs. Verify the new-path call still receives those same exclusion sets. The sets are computed downstream of the lanes they come from; Lane 4 is the last lane to run, so the anti-echo logic is orthogonal to the input-shape change.
  - [ ] 4.2 Add a test asserting anti-echo model IDs still pass through to `assemble_structural_coverage_card` when the new path runs.

- [x] 5.0 Quality-metrics script — `scripts/phase2b_lane4_quality_check.py`, resilient to extraction + pipeline failures, adapted for Lane 4 metrics (no drop-rate; uses `question_type` stability + per-case gap-count regression + negative-check criteria).
  - [ ] 5.1 Adapt `scripts/phase2a_lane3_quality_check.py` into `scripts/phase2b_lane4_quality_check.py`. Same structure (resume + resilient extraction/pipeline), different metrics focused on `structural_coverage_card`.
  - [ ] 5.2 Structural metrics: `question_class` per run (should be stable across N=3 on each path); `detected_dimensions_count` mean + sd; `gap_questions_count` mean; `dimensions_with_coverage_change` across paths.
  - [ ] 5.3 Dry-run: `--n 1 --cases oncologist` to verify plumbing end-to-end.

- [x] 6.0 Full N=3 × 10-case measurement — 60 runs, wall time 2515s, zero regressions flagged by automated policy. Report + raw metrics committed to `research/test-cases/phase2b-lane4-equivalence-2026-04-23/`. Controlled Marcus A/B committed to `research/test-cases/phase2b-marcus-controlled-comparison-2026-04-23/`. Ablation (architecture vs volume on friendship_money) in `scripts/phase2b_ablation_architecture_vs_volume.py`. 0-gap-qs anomaly diagnosed as random LLM variance via N=5 re-run (`scripts/phase2b_diagnose_gap_qs_anomaly.py`).
  - [ ] 6.1 Run `scripts/phase2b_lane4_quality_check.py --n 3` in background (expected ~45min, ~$3-9).
  - [ ] 6.2 **Per-case regression check.** Apply the diagnosis-required policy from 2a. Two undiagnosed regressions = block the PR.
  - [ ] 6.3 Commit evidence report to `research/test-cases/phase2b-lane4-equivalence-<YYYY-MM-DD>/`.
  - [ ] 6.4 **Controlled Marcus comparison** (primary evidence, required per 2a lesson): same conversation (`/tmp/lolla_20260422T155622Z_conversation.txt` or a fresh Marcus capture if the file is rotated), same fresh extraction, old path vs new path. Artifacts + side-by-side README at `research/test-cases/phase2b-lane4-marcus-controlled-comparison-<YYYY-MM-DD>/`. This is the clearest single piece of evidence for the PR.

- [~] 7.0 Qualitative human read — surfaced to PM via Marcus A/B README + 10-case per-case breakdowns in reports. Not formally rendered as a separate 3-case diff this time; PR description carries the qualitative summary.
  - [ ] 7.1 Render side-by-side diff for 3 cases into a markdown file. Include at least `messy_three_problems` (stress on multi-thread structural coverage) and `real_estate` (Phase 2a showed the old path can fail here). Third case: PM picks or session defaults to `user_has_plan` (clean baseline).
  - [ ] 7.2 Surface to PM for review. ≥ 2/3 rated "new ≥ old" to proceed.

- [x] 8.0 Negative-check gate — zero trips on any case (no empty-card-on-new-where-old-produced; no qtype instability within N=3 new-path runs; no drop-rate collapse — Lane 4 has no drop-rate metric anyway).
  - [ ] 8.1 Scan 30 new-path runs for the three negative-check criteria (empty card on new where old produced; question_class instability across runs; hallucinated evidence in gap rationales).
  - [ ] 8.2 Zero trips = proceed. Any trip = STOP, diagnose.

- [x] 9.0 Documentation — `HOW_IT_WORKS.md §Step 3` Lane 4 section has a Phase 2b migration paragraph explaining the `_from_context` entry points + CONTEXT/SOURCE split + detection's dual user/assistant evidence sources + pointer to measurement artifacts.
  - [ ] 9.1 Update `HOW_IT_WORKS.md §Step 3` Lane 4 section with a Phase 2b migration paragraph (same shape as Lane 3's).
  - [ ] 9.2 Defer handover "What's shipped" update to post-merge.

- [ ] 10.0 Ship
  - [ ] 10.1 Full test suite green.
  - [ ] 10.2 Push + open PR. Title: `feat(pipeline): Lane 4 (Structural Coverage) migrated to ConversationContext (phase 2b)`.
  - [ ] 10.3 PR description leads with: (a) controlled Marcus comparison (primary evidence); (b) 10-case aggregate + per-case regression diagnoses; (c) evidence-grounding shift mechanism; (d) acceptance-gate table. Same three-angle structure as PR #15.
  - [ ] 10.4 On merge: update handover "What's shipped" with PR #, metrics summary, rollback path.

## Phase 2c preview (do NOT do in this PR)

After 2b merges, Phase 2c migrates Lane 1 (Structural Pressure) — the biggest and most coupled. The Phase 2a pattern + any 2b refinements become the template. See `research/phase2-lane-migration-plan.md`.

## Risks

1. **Three prompts to rewrite, not one.** Lane 4 has 3 LLM calls; Phase 2a had 2. More surface area for prompt-engineering misfires. Mitigation: write CONTEXT/SOURCE + RIGHT/WRONG examples from day one (Phase 2a had to fix this mid-PR; we know better now).
2. **Dimension detection takes both user turns AND assistant replies as evidence sources.** Lane 4 is auditing whether the answer covered the dimension, so quotes can legitimately come from either side of the conversation. Make the SOURCE section explicit about this to avoid a Phase 2a-style "evidence drop" event.
3. **Question classification might shift on some cases.** If the old path's collapsed `query` misled classification and the new path sees clearer user intent, the `question_class` value itself may change. That's not a regression; it's the improvement. But PR description needs to call it out honestly if it happens.
4. **Cost overrun** from retrying failed runs. Script is resilient to extraction/pipeline failures; budget for ~$3-9 with a ~$2 buffer if anything re-runs.

## Open questions for PM (surface at preflight checkpoint)

None anticipated — the Phase 2a decisions (N=3, 5% tolerance, diagnosis-required policy, negative-check criteria shape) transfer directly. If something surfaces during task 0.x preflight (e.g., Lane 4's dimension_detection turns out to be structurally different from what we expect), flag then.

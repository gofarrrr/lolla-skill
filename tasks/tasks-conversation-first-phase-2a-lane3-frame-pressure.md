# Phase 2a: Lane 3 (Frame Pressure) — migrate to ConversationContext

**Branch:** `feat/conversation-first-phase-2a-lane3-frame-pressure`
**Phase plan:** `research/phase2-lane-migration-plan.md`
**Handover:** `research/conversation-first-rearchitecture-handover.md`
**Audit:** `research/full-system-audit-2026-04-23.md` §3 (Lane 3)
**Scope:** migrate Lane 3 (Frame Pressure) to consume `ConversationContext` directly. Legacy `run_frame_extraction(query, vanilla_answer)` stays alongside the new path and continues serving the shim. Other three lanes unchanged.

## Why this PR

Lane 3 audits the question for framing issues. Under the current `CritiqueRequest` shape, its input is a collapsed `query` = `decision_situation + constraint lines + original_framing + dropped_threads` smooshed into one flat string. The known defect (PR #1 diagnostic): when `original_framing` is unstable — e.g. because the first user turn was a context-dump rather than a clean question — Lane 3's extraction is noisy, drop rate spikes, reframings anchor on text that isn't really what the user asked.

Giving Lane 3 direct access to (a) the actual first user turn verbatim, (b) the full turn-by-turn conversation, (c) typed extraction fields with turn metadata, lets it audit the framing as it was actually posed, not as it was reassembled.

## Relevant files

- `engine/system_b/frame_pressure.py` — **primary file**. Add new conversation-aware entry points alongside existing ones. Rewrite prompts for conversation-first shape.
- `engine/system_b/pipeline.py` — thread `ConversationContext` from `run()` into `_run_frame_pressure()`; the lane method dispatches based on availability.
- `tests/test_frame_pressure_contextual.py` — **NEW**. TDD for the new entry points.
- `scripts/phase2a_lane3_quality_check.py` — **NEW**. Produces structural metrics across 10-case corpus N=3 per path.
- `research/phase2-lane-migration-plan.md` — quality-comparison protocol reference.
- `HOW_IT_WORKS.md` §Step 3 — note Lane 3 is now conversation-first.
- `research/conversation-first-rearchitecture-handover.md` — update "What's shipped" on merge.

### Notes

- Test runner: `python3 -m pytest tests/test_frame_pressure_contextual.py -v`
- The 10-case corpus is at `research/test-cases/case_*_conversation.txt`.
- **Don't touch** any other lane (Lane 1, 2, 4). This PR is Lane 3 only.
- **Don't delete** `run_frame_extraction(query, vanilla_answer)` — it serves the shim path until Phase 3.
- Per the phase plan, reframing generation also needs a conversation-aware variant since its prompt currently uses `query`.

## Acceptance gate

| Axis | Target |
|---|---|
| New unit tests for conversation-aware entry points | ≥ 6 new tests, all green |
| Full test suite | zero regression (164 tests → 170+) |
| `dropped_frame_elements_rate` across 10-case corpus N=3 | new-path ≤ old-path (within 5% tolerance) |
| `frame_elements_count` stability per case | within ±2 of old-path median across 3 samples |
| Qualitative human read | ≥ 2 of 3 cases (messy, clean, edge) rated "new ≥ old" |
| Negative-check gate | zero trips on any case |
| HOW_IT_WORKS.md updated | yes |

## Tasks

- [ ] 0.0 Preflight
  - [ ] 0.1 Confirm Phase 1 on main: `git log --oneline main -5` shows `fa5df6c Merge pull request #14`.
  - [ ] 0.2 Fresh main + branch: `git checkout main && git pull && git checkout -b feat/conversation-first-phase-2a-lane3-frame-pressure`.
  - [ ] 0.3 Verify Phase 1 scaffolding present: `ls engine/system_b/conversation_context.py engine/system_b/conversation_loader.py scripts/compare_outputs.py` (all exist).
  - [ ] 0.4 Run `pytest tests/ -q` — confirm 164 passing before changes.
  - [ ] 0.5 Re-read `research/phase2-lane-migration-plan.md` (quality protocol) and `engine/system_b/frame_pressure.py` (Lane 3 internals).
  - [ ] 0.6 Skim the 10-case corpus first-user-turns to get an intuition for what "first turn = framing anchor" means in practice (1-2 min per case).

- [ ] 1.0 Add conversation-aware extraction entry point (TDD)
  - [ ] 1.1 Design the new user-prompt shape. Present: full turn-by-turn conversation, extracted decision_situation + original_framing + typed constraint list + typed dropped_threads list. Explicitly identify the first user turn as the "original framing anchor." Decide whether evidence quotes come from (a) any user turn, (b) first user turn only, or (c) extracted `original_framing` — default (a) because conversations evolve framings across turns; document the choice in the prompt file and a comment.
  - [ ] 1.2 RED: `tests/test_frame_pressure_contextual.py::test_run_frame_extraction_from_context_basic` — call the new entry point with a synthetic `ConversationContext`, assert it returns a `FramePressureCard` with `frame_elements` and no crashes. Mock the boundary.
  - [ ] 1.3 GREEN: add `run_frame_extraction_from_context(boundary, context: ConversationContext) -> FramePressureCard` to `frame_pressure.py`. Builds the new user prompt. Validates `evidence_quote` against the chosen source-text set (all user turns). Returns same card shape as the legacy function.
  - [ ] 1.4 RED: `test_run_frame_extraction_from_context_rejects_evidence_not_in_user_turns` — LLM mock returns an element whose `evidence_quote` isn't in any user turn; the parser drops it with reason `evidence_not_in_user_turns`.
  - [ ] 1.5 GREEN: implement evidence validation against the joined user-turn text.
  - [ ] 1.6 RED: `test_run_frame_extraction_from_context_handles_empty_turns` — context with zero user turns returns an empty card without crashing.
  - [ ] 1.7 GREEN: verify guard.

- [ ] 2.0 Rewrite the frame-extraction system prompt (if needed) + reframing prompt
  - [ ] 2.1 Decide whether `_FRAME_EXTRACTION_SYSTEM` needs changes. If the new user-prompt format fully disambiguates "analyze the user's framing as posed in the conversation," the system prompt likely stays. Document the decision.
  - [ ] 2.2 Add `_REFRAME_GENERATION_SYSTEM_FROM_CONTEXT` OR reuse the existing system prompt with a new user-prompt builder `_format_reframe_generation_prompt_from_context(context, elements, routes)`. The reframing prompt was quite tight about not being generic — shouldn't need structural change, just feed it the richer context.
  - [ ] 2.3 RED: `test_generate_reframings_from_context_basic` — new entry point accepts a context + elements + routes and returns reframings. Mock boundary.
  - [ ] 2.4 GREEN: add `generate_reframings_from_context(boundary, context, elements, routes)` to `frame_pressure.py`.

- [ ] 3.0 Wire `pipeline.py::_run_frame_pressure` to dispatch (TDD)
  - [ ] 3.1 Read `SystemBPipeline.run()` (lines 375–601 in pipeline.py) to identify where a reference to the original `ConversationContext` (when one was passed in) would be held. Currently the shim overwrites `request` with the converted `CritiqueRequest` on line ~382; that drops the context. Decision: hold the context in a local variable `conversation_context: ConversationContext | None`.
  - [ ] 3.2 Modify `_run_frame_pressure` signature to accept `conversation_context: ConversationContext | None = None`. When the context is present, route to `run_frame_extraction_from_context` / `generate_reframings_from_context`. Otherwise keep current behavior (legacy path).
  - [ ] 3.3 RED: extend `tests/test_pipeline_shim_equivalence.py` with a test that proves `run(ConversationContext)` calls the new Lane 3 entry point (spy via `unittest.mock.patch`).
  - [ ] 3.4 GREEN: verify. Run the full shim-equivalence suite — tasks 2a should not break the existing 10 dispatch tests.
  - [ ] 3.5 Run `pytest tests/ -q` — confirm zero regression.

- [ ] 4.0 Anti-echo + overlap handling (verify, don't change)
  - [ ] 4.1 The anti-echo model-ID set and the pressure-concept overlap detection live in `pipeline.py::_run_frame_pressure`. They operate on Lane 1 output, not on the input shape. Should work identically in the new path. Verify by tracing the code.
  - [ ] 4.2 Add a test asserting anti-echo still excludes Lane 1 models from Lane 3 candidates when the new path runs.

- [ ] 5.0 Quality-metrics script
  - [ ] 5.1 Build `scripts/phase2a_lane3_quality_check.py`. Takes a corpus dir + N (default 3) + both paths (`old` and `new`). For each case: extract once (shared across paths), then run pipeline N times on each path (`--skip-revision` to save cost). Capture the `frame_pressure_card` payload per run. Compute structural metrics per case + aggregate.
  - [ ] 5.2 Output: a markdown report with per-case tables and aggregate summary. Saves to `research/test-cases/phase2a-lane3-equivalence-2026-MM-DD/`.
  - [ ] 5.3 Dry-run the script locally with N=1 on a single case to confirm it works end-to-end before burning the full budget.

- [ ] 6.0 Execute the N=3 × 10-case measurement
  - [ ] 6.1 Run `scripts/phase2a_lane3_quality_check.py` against all 10 cases with N=3. Expected cost ≈ $3-9. Expected time ≈ 20-40 minutes.
  - [ ] 6.2 Review the aggregate: does `dropped_frame_elements_rate` satisfy the threshold (new ≤ old within 5%)? Does `frame_elements_count` stay within ±2 per case?
  - [ ] 6.3 **If any threshold fails: STOP, diagnose, do not proceed to 7.0.** Report to PM with the specific case + metric that failed.
  - [ ] 6.4 Commit the evidence report.

- [ ] 7.0 Qualitative human read
  - [ ] 7.1 Render old-path vs new-path outputs side-by-side for the 3 chosen cases (`messy_three_problems`, `startup_pivot`, `phd_research`) into a single markdown diff file.
  - [ ] 7.2 Surface to PM for review. PM calls ≥ 2/3 rated "new ≥ old" to proceed.
  - [ ] 7.3 **If PM says stop: stop. Don't ship.**

- [ ] 8.0 Negative-check gate
  - [ ] 8.1 Scan the N=3 results for: non-empty card on old → empty card on new; hallucinated evidence (should be caught during extraction, but verify); drop rate > 50% on any case where old was < 20%.
  - [ ] 8.2 **If any case trips: STOP, diagnose.**
  - [ ] 8.3 If clean: record in the evidence report.

- [ ] 9.0 Documentation
  - [ ] 9.1 Update `HOW_IT_WORKS.md §Step 3` Lane 3 section to note the conversation-first migration.
  - [ ] 9.2 Defer the handover "What's shipped" update to post-merge (prevents rot if PR is revised).

- [ ] 10.0 Ship
  - [ ] 10.1 Run full test suite. All green.
  - [ ] 10.2 Push + open PR. Title: `feat(pipeline): Lane 3 (Frame Pressure) migrated to ConversationContext (phase 2a)`.
  - [ ] 10.3 PR description includes: quality-metric tables, qualitative comparison link, acceptance-gate table, honest call-outs on any case where new-path ≠ old-path materially.
  - [ ] 10.4 On merge: update handover "What's shipped" with PR #, metrics summary, and rollback path.

## Phase 2b preview (do NOT do in this PR)

After 2a merges, the pattern from this PR (new entry point alongside legacy, pipeline.py dispatches, quality protocol, ship gate) is reused for Lane 4. See `research/phase2-lane-migration-plan.md`.

**Out of scope for 2a.** If tempted to migrate Lane 4 "while the context plumbing is in," stop. Each lane gets its own PR.

## Risks

1. **Prompt drift.** New user-prompt shape may produce different LLM behavior even when it's strictly richer (LLMs can be finicky). Mitigation: structural metrics + qualitative read.
2. **Anti-echo regression.** The anti-echo set is computed from Lane 1 output downstream of Lane 3's call. If the dispatch changes the order of operations, anti-echo could silently break. Mitigation: 4.2 test.
3. **Cost overrun.** N=3 × 10 × 2 paths ≈ 60 pipeline runs. If a run fails halfway, rerunning could double the spend. Mitigation: 5.3 dry-run first; 6.1 explicit cost note.
4. **Qualitative disagreement.** PM judgment on "new ≥ old" may hinge on specific phrasings. Mitigation: render side-by-side, not narrative summaries; PM decides the bar.

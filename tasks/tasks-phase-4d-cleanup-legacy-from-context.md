# Phase 4d — Cleanup: remove dead `_from_context` fallbacks

**Future branch:** `feat/phase-4d-cleanup-from-context`
**Risk:** Low — the `_from_context` branches in `pipeline.py` are dead code after Phase 4 merged.
**Estimated time:** ~2 hours.
**Prerequisite:** main at commit `0457060` or later (Phase 4 merged); full suite green.

## Why this phase

After Phase 4, when the pipeline receives a `ConversationContext`, it ALWAYS constructs `ConversationIR` at entry (`engine/system_b/pipeline.py:483`). So in every lane's dispatch, the `elif conversation_context is not None` branch (which calls `*_from_context`) is unreachable — `conversation_ir` is always set when `conversation_context` is set.

This phase removes those dead branches. The `*_from_context` functions themselves remain (tests still use them); only the pipeline's fallback paths go away.

## Out of scope

- **Do NOT remove the `*_from_context` source functions.** Existing tests in `tests/test_lane{1,2,3,4}_contextual.py` and `tests/test_frame_pressure_contextual.py` use them as anti-regression. Removing them would force a large test migration; not in this phase.
- **Do NOT remove the legacy `run_*` (without `_from_context` suffix) functions.** Those are removed in Phase 6 (CritiqueRequest removal).
- **Do NOT change the IR or packet builder.** Substrate is frozen.

## Files involved

- `engine/system_b/pipeline.py` — dispatch fallbacks to remove
- `tests/test_pipeline_shim_equivalence.py` — read-only verification target

## Tasks

### 0.0 Branch and baseline

- [ ] 0.1 Branch: `git switch -c feat/phase-4d-cleanup-from-context`
- [ ] 0.2 Baseline: `python3 -m pytest tests -q`. Must show **383 passed**. If not, stop and ask PM.

### 1.0 Lane 4 (Structural Coverage) — remove `_from_context` fallback

The pipeline's `_run_structural_coverage` has three branches today: from_ir, from_context, legacy. Remove from_context.

- [ ] 1.1 RED: in `tests/test_pipeline_shim_equivalence.py`, find a test that runs the pipeline with `ConversationContext` input (there are several). Confirm at least one exists. (No new test needed — existing coverage proves the from_ir path works.)
- [ ] 1.2 In `engine/system_b/pipeline.py`, find `_run_structural_coverage`. Remove the `elif conversation_context is not None` branch. Keep `if conversation_ir is not None` (primary) and `else` (legacy CritiqueRequest path).
- [ ] 1.3 GREEN: run `pytest tests -q`. Must still show 383 passed.
- [ ] 1.4 Commit: `git commit -m "phase 4d: remove dead from_context fallback in _run_structural_coverage"`

### 2.0 Lane 3 (Frame Pressure) — remove `_from_context` fallback

- [ ] 2.1 In `pipeline.py`, find `_run_frame_pressure`. Remove the `elif use_context` (or equivalent) branch that calls `run_frame_extraction_from_context`. Keep `if conversation_ir is not None` and `else` (legacy).
- [ ] 2.2 Run `pytest tests -q`. **Expect 383.**
- [ ] 2.3 Commit.

### 3.0 Lane 2 (Companion / Fingerprint+Verification) — remove `_from_context` fallbacks

- [ ] 3.1 In `pipeline.py`, find `_run_companion`. Two branches use `_from_context` (fingerprint, then verification). Remove both `elif conversation_context is not None` branches; keep the `if packet is not None` (primary) and `else` (legacy) paths.
- [ ] 3.2 Run `pytest tests -q`. Expect 383.
- [ ] 3.3 Commit.

### 4.0 Lane 1 (Deep Checks / Pass 2) — remove `_from_context` fallbacks

- [ ] 4.1 In `pipeline.py`, find `_run_pass2_single` and `_run_pass2_parallel`. Both have `if conversation_ir → packet` / `elif conversation_context → from_context` / `else legacy` chains. Remove the `elif conversation_context` branches.
- [ ] 4.2 Run `pytest tests -q`. Expect 383.
- [ ] 4.3 Commit.

### 5.0 Final verification

- [ ] 5.1 Search pipeline.py for any remaining `from_context` references in **dispatch fallback** logic. The grep `grep -n "from_context" engine/system_b/pipeline.py` will surface three classes of match:
  - **Import lines** (expected — symbols exist for tests)
  - **Live callers** (expected — `generate_reframings_from_context` for reframe generation, `format_pass1_cluster_prompts_from_context` for Pass 1; these are NOT dead-fallback dispatch and are intentionally retained for Phase 6)
  - **Dispatch fallback `elif conversation_context is not None: ... _from_context(...)` branches** — these MUST be zero. Inspect each match by hand to confirm category.
- [ ] 5.2 Run full suite once more: `pytest tests -q`. Pass count may be slightly higher than baseline if the dispatch-test changes added coverage; that's fine. What matters is no regressions.
- [ ] 5.3 Open PR. Title: `feat: Phase 4d — remove dead _from_context fallbacks in pipeline dispatch`.

## How to know you're done

- Full suite still 383 passed.
- `grep "_from_context" engine/system_b/pipeline.py` shows imports only, no dispatch.
- `_from_context` functions still exist in lane modules — that's intentional, leave them.

## What to do if something breaks

If a test fails after removing a branch:
1. Revert the branch removal (`git restore engine/system_b/pipeline.py`).
2. Look at what the failing test does. Does it pass `ConversationContext` without IR? That'd reveal a gap in pipeline's IR construction.
3. If you find a real gap (an input shape we didn't anticipate), STOP and flag it to PM. Don't try to fix it in this phase.

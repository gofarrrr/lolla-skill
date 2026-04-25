# Phase 6 — Remove the legacy `CritiqueRequest` shim

**Future branch:** `feat/phase-6-remove-critiquerequest-shim`
**Risk:** Medium-high — `CritiqueRequest` touches many tests. This phase migrates them.
**Estimated time:** ~4-6 hours.
**Prerequisite:** Phase 4d merged (or skipped). Phase 7 ideally merged first because it makes the legacy path more isolated.

## Why this phase

`CritiqueRequest(query, vanilla_answer)` is the legacy data shape that pre-dates the conversation-first migration. After Phase 4, it's only used by:
1. The pipeline's "legacy input" path (when caller passes `CritiqueRequest` instead of `ConversationContext`)
2. The legacy lane functions (`run_fingerprint_call`, `run_verification_call`, `run_frame_extraction`, `format_pass2_prompt`, `run_structural_coverage`) that the legacy path calls
3. Many tests that assert legacy behavior

Phase 6 removes all three. After this, the pipeline ONLY accepts `ConversationContext`.

## Approved decisions

- **Pipeline accepts `ConversationContext` only.** No back-compat for `CritiqueRequest` callers; they need to migrate to `ConversationContext` upstream.
- **Legacy lane functions are deleted**, not deprecated. They have no remaining callers after this phase.
- **`_context_to_critique` helper is deleted** — it converted `ConversationContext` to `CritiqueRequest` for the legacy path; no longer needed.

## Out of scope

- **Do NOT touch the IR or packet builder.** Substrate is frozen.
- **Do NOT migrate user-owned files** (e.g. `research/conversation-first-extraction-evaluation-2026-04-24.md`).
- **Do NOT change `*_from_context` functions.** Those still serve tests; if Phase 4d removed dead pipeline branches, the source code stays.

## Files involved

Read-and-modify:
- `engine/system_b/pipeline.py` — input handling, legacy dispatch branches
- `engine/system_b/companion_routing.py` — `run_fingerprint_call`, `run_verification_call`
- `engine/system_b/frame_pressure.py` — `run_frame_extraction`, `generate_reframings`
- `engine/system_b/deep_checks.py` — `format_pass2_prompt`
- `engine/system_b/structural_coverage.py` — `run_structural_coverage`
- `engine/system_b/__init__.py` (if it exports `CritiqueRequest`)
- `engine/system_b/conversation_context.py` — `_context_to_critique` helper

Tests to migrate or delete:
- `tests/test_pipeline_shim_equivalence.py` — currently asserts shim equivalence; after Phase 6 it's irrelevant. Likely DELETE.
- `tests/test_run_pipeline_contract_default.py` — read; may need updates
- Any test that builds `CritiqueRequest` directly — migrate to `ConversationContext`.

## Tasks

### 0.0 Branch + baseline

- [ ] 0.1 `git switch -c feat/phase-6-remove-critiquerequest-shim`
- [ ] 0.2 Baseline: `pytest tests -q`. Record the pass count.
- [ ] 0.3 List all test files that import `CritiqueRequest`: `grep -l CritiqueRequest tests/*.py`. This is your migration surface.

### 1.0 Audit current callers (no code changes yet)

- [ ] 1.1 List every non-test caller of legacy functions:
  ```
  grep -rn "run_fingerprint_call\b\|run_verification_call\b\|run_frame_extraction\b\|run_structural_coverage\b\|format_pass2_prompt\b" engine/
  ```
  (Note the word boundaries — exclude `_from_context` and `_from_packet` variants.)
- [ ] 1.2 Confirm: the only callers are in `pipeline.py` (legacy dispatch branches). If any other file calls them, STOP and flag to PM.
- [ ] 1.3 Note in this task file: which legacy functions have callers, where.

### 2.0 Migrate pipeline input handling (TDD)

- [ ] 2.1 RED: write a test in a new file `tests/test_pipeline_rejects_critiquerequest.py` that calls `SystemBPipeline.run(CritiqueRequest(...))` and asserts a `TypeError` (or similar explicit rejection). Run it — should fail because the pipeline currently accepts both shapes.
- [ ] 2.2 GREEN: in `pipeline.py`, change the entry-point shape check from "if isinstance(request, ConversationContext): convert; else: legacy" to "if not isinstance(request, ConversationContext): raise TypeError". Keep the `conversation_context = request; conversation_ir = construct_conversation_ir(...)` block.
- [ ] 2.3 Run the new test. GREEN.
- [ ] 2.4 Run full suite. Many tests will FAIL — that's expected; they pass `CritiqueRequest`. List them.

### 3.0 Migrate failing tests one file at a time

- [ ] 3.1 For each failing test file:
  - Read it.
  - For each `CritiqueRequest(query=..., vanilla_answer=...)` construction, replace with a `ConversationContext` that contains the same content as user/assistant turns.
  - Helper: many test files already have a `_ctx` builder. Use it.
- [ ] 3.2 After each test file migration: run that single file (`pytest tests/test_X.py -q`) until green. Then full suite.
- [ ] 3.3 Some tests may be testing the SHIM behavior specifically — those should be DELETED once the shim is gone. Common examples: `tests/test_pipeline_shim_equivalence.py`. Confirm with PM before deleting any test file.

### 4.0 Remove legacy lane functions (TDD by removal)

After 3.x, no test should construct `CritiqueRequest`. Now safe to remove the legacy functions.

- [ ] 4.1 In `pipeline.py`, remove the `else` branches in lane dispatchers that call `run_fingerprint_call` / `run_verification_call` / `run_frame_extraction` / `run_structural_coverage` / `format_pass2_prompt`. After removal, the dispatchers are simply `if conversation_ir → packet path` (or just call packet path unconditionally if `conversation_ir` is now always set).
- [ ] 4.2 In each lane module, delete the legacy function (`run_fingerprint_call`, `run_verification_call`, `run_frame_extraction`, `format_pass2_prompt`, `run_structural_coverage`) AND any helper-only-used-by-legacy (e.g. `_build_fingerprint_user_prompt`, `_format_classification_user_prompt`).
- [ ] 4.3 Remove `_context_to_critique` from `conversation_context.py` if no longer used.
- [ ] 4.4 Remove `CritiqueRequest` dataclass from `conversation_context.py` (or wherever it's defined). Final step.
- [ ] 4.5 Run full suite. Should be green.

### 5.0 Final verification

- [ ] 5.1 `grep -rn "CritiqueRequest" engine/ tests/` — should return ZERO results.
- [ ] 5.2 `grep -rn "run_fingerprint_call\b\|run_verification_call\b\|run_frame_extraction\b\|run_structural_coverage\b" engine/` — should return zero results (the `_from_packet` and `_from_context` variants are still there with different suffixes).
- [ ] 5.3 Full suite green.
- [ ] 5.4 Open PR with title `feat: Phase 6 — remove CritiqueRequest legacy shim`.

## How to know you're done

- `CritiqueRequest` no longer exists anywhere.
- Legacy `run_*` functions deleted.
- Pipeline raises `TypeError` on non-`ConversationContext` input.
- Full suite green at the same or higher pass count as baseline minus deleted shim tests.

## Common pitfalls

- **Shim equivalence tests**: `tests/test_pipeline_shim_equivalence.py` literally tests "shim path produces same output as context path". After Phase 6 there's no shim path. The test file is obsolete. Confirm with PM, then delete.
- **Default ConversationContext**: tests sometimes need a minimal `ConversationContext`. There's a helper pattern in `tests/test_lane*_contextual.py` — copy it.
- **Embedding tendency signal** (if it appears in pipeline.py): may have a legacy "joined assistant text" reader that uses `request.vanilla_answer`. Migrate to read from turns.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| External callers of legacy functions break silently | Audit step 1.x covers this; if anything found, STOP. |
| Test migration introduces subtle behavior change | Keep `_ctx` helpers consistent; reuse existing patterns from migrated test files. |
| Pipeline shape change breaks downstream consumers | The pipeline is internal; no external callers. But check `scripts/` directory just in case. |
| Deletion order matters (deleting `CritiqueRequest` before its callers fails) | Delete callers first (steps 4.1, 4.2), then `_context_to_critique`, then `CritiqueRequest` last. |

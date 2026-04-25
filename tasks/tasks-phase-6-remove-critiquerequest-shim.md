# Phase 6 — Remove the legacy `CritiqueRequest` shim

**Future branch:** `feat/phase-6-remove-critiquerequest-shim`
**Risk:** Medium-high — `CritiqueRequest` touches many tests, scripts, and Pass 1.
**Estimated time:** ~6-8 hours (revised after audit).
**Prerequisite:** Phase 4d merged (or skipped). Phase 7 ideally merged first because it makes the legacy path more isolated.

## Why this phase

`CritiqueRequest(query, vanilla_answer)` is the legacy data shape that pre-dates the conversation-first migration. After Phase 4, it's used by:
1. **Pipeline entry shape**: `SystemBPipeline.run()` accepts `CritiqueRequest | ConversationContext` (`engine/system_b/pipeline.py:478-479`).
2. **Pass 1 (triage) parameter type**: `_run_pass1_clusters_parallel(*, request: CritiqueRequest, ...)` (`engine/system_b/pipeline.py:1173-1179`) and the per-cluster runner it calls. Pass 1 also has a legacy `format_pass1_cluster_prompts(...)` branch alongside the `_from_context` variant.
3. **Embedding tendency / relevance text reader**: derives a flat string from `request.query` and `request.vanilla_answer` (`engine/system_b/pipeline.py:478-499` area — read carefully before changing).
4. **Telemetry typing**: `build_run_record(*, request: "CritiqueRequest", ...)` in `engine/system_b/telemetry.py:272-274`.
5. **Legacy lane functions**: `run_fingerprint_call`, `run_verification_call`, `run_frame_extraction`, `format_pass2_prompt`, `run_structural_coverage` (the variants without `_from_context` or `_from_packet` suffix).
6. **Scripts that intentionally use the legacy contract**: `scripts/run_pipeline.py` exposes `--legacy-contract` (line ~269); `scripts/stability_check.py` forwards it (lines ~427, 442, 800, 927); `scripts/phase1_equivalence_check.py` exists specifically to verify the shim equivalence — historical artifact, no longer load-bearing.
7. **Tests that build `CritiqueRequest` directly**: `tests/test_pipeline_shim_equivalence.py`, `tests/test_run_pipeline_contract_default.py`, `tests/test_stability_check.py`, `tests/test_measurement_command_contract.py`.

Phase 6 removes all of these. After this, the pipeline ONLY accepts `ConversationContext`.

## Approved decisions

- **Pipeline accepts `ConversationContext` only.** No back-compat for `CritiqueRequest` callers; they need to migrate to `ConversationContext` upstream.
- **Legacy lane functions are deleted**, not deprecated. They have no remaining callers after this phase.
- **`_context_to_critique` helper is deleted** — it converted `ConversationContext` to `CritiqueRequest` for the legacy path; no longer needed.

## Out of scope

- **Do NOT touch the IR or packet builder.** Substrate is frozen.
- **Do NOT migrate user-owned files** (e.g. `research/conversation-first-extraction-evaluation-2026-04-24.md`).
- **Do NOT change `*_from_context` functions.** Those still serve tests; if Phase 4d removed dead pipeline branches, the source code stays.

## Files involved

Read-and-modify (engine):
- `engine/system_b/pipeline.py` — `CritiqueRequest` defined at **line 150** (NOT in conversation_context.py); `_context_to_critique` helper; pipeline `run()` shape check; `_run_pass1_clusters_parallel` signature; legacy `format_pass1_cluster_prompts` branch around line 1173+; relevance text reader around line 478-499.
- `engine/system_b/companion_routing.py` — `run_fingerprint_call`, `run_verification_call`
- `engine/system_b/frame_pressure.py` — `run_frame_extraction`, `generate_reframings`
- `engine/system_b/deep_checks.py` — `format_pass2_prompt`
- `engine/system_b/structural_coverage.py` — `run_structural_coverage`
- `engine/system_b/prompts.py` — `format_pass1_cluster_prompts` (legacy variant)
- `engine/system_b/telemetry.py` — `build_run_record` parameter type at **line 272**
- `engine/system_b/__init__.py` (if it exports `CritiqueRequest`)

Read-and-modify (scripts):
- `scripts/run_pipeline.py` — `--legacy-contract` flag (line ~269); legacy CritiqueRequest construction path
- `scripts/stability_check.py` — `--legacy-contract` flag and `legacy_contract` parameter (lines ~427, 442, 800, 927, 936)
- `scripts/phase1_equivalence_check.py` — entire file is historical shim-verification evidence; **decide explicitly: delete, archive to `research/`, or exempt**

Tests to migrate or delete:
- `tests/test_pipeline_shim_equivalence.py` — currently asserts shim equivalence; after Phase 6 it's irrelevant. Likely DELETE (confirm with PM).
- `tests/test_run_pipeline_contract_default.py` — read; expect updates around line 139 (asserts default contract behavior).
- `tests/test_stability_check.py` — references `--legacy-contract` from line 23 onward. Migrate to context-only assertions or delete.
- `tests/test_measurement_command_contract.py` — read; may assert legacy CLI surface.
- Any other test that builds `CritiqueRequest` directly — migrate to `ConversationContext` (use the `_ctx` helpers from `tests/test_lane*_contextual.py` as templates).

## Tasks

### 0.0 Branch + baseline

- [ ] 0.1 `git switch -c feat/phase-6-remove-critiquerequest-shim`
- [ ] 0.2 Baseline: `pytest tests -q`. Record the pass count.
- [ ] 0.3 List all test files that import `CritiqueRequest`: `grep -l CritiqueRequest tests/*.py`. This is your test migration surface.
- [ ] 0.4 List every script that imports `CritiqueRequest`: `grep -l CritiqueRequest scripts/*.py`. This is your script migration surface.

### 1.0 Audit current callers (no code changes yet)

- [ ] 1.1 List every non-test, non-script caller of legacy functions:
  ```
  grep -rn "run_fingerprint_call\b\|run_verification_call\b\|run_frame_extraction\b\|run_structural_coverage\b\|format_pass2_prompt\b\|format_pass1_cluster_prompts\b" engine/
  ```
  (Note the word boundaries — exclude `_from_context` and `_from_packet` variants.)
- [ ] 1.2 Confirm: the only callers are in `pipeline.py` (legacy dispatch branches). If any other file calls them, STOP and flag to PM.
- [ ] 1.3 Note in this task file: which legacy functions have callers, where.
- [ ] 1.4 Inventory `CritiqueRequest` parameter types: search for `request: CritiqueRequest` (note: `_run_pass1_clusters_parallel` and `build_run_record` both type against it). These signatures need migration.
- [ ] 1.5 Decide what to do with `scripts/phase1_equivalence_check.py`: delete (it's historical), or archive to `research/`. Confirm with PM.

### 2.0 Migrate pipeline input handling (TDD)

- [ ] 2.1 RED: write a test in a new file `tests/test_pipeline_rejects_critiquerequest.py` that calls `SystemBPipeline.run(CritiqueRequest(...))` and asserts a `TypeError` (or similar explicit rejection). Run it — should fail because the pipeline currently accepts both shapes.
- [ ] 2.2 GREEN: in `pipeline.py`, change the entry-point shape check from "if isinstance(request, ConversationContext): convert; else: legacy" to "if not isinstance(request, ConversationContext): raise TypeError". Keep the `conversation_context = request; conversation_ir = construct_conversation_ir(...)` block.
- [ ] 2.3 Run the new test. GREEN.
- [ ] 2.4 Run full suite. Many tests will FAIL — that's expected; they pass `CritiqueRequest`. List them.

### 3.0 Migrate Pass 1 (triage) and telemetry signatures

This step was missed in the original task draft. Pass 1 and telemetry both type against `CritiqueRequest` independent of lane code.

- [ ] 3.1 RED: in `pipeline.py`, change `_run_pass1_clusters_parallel`'s `request: CritiqueRequest` parameter — replace with a smaller dependency bag: `query_text: str | None`, `vanilla_text: str | None` (or pass `conversation_context` through). Run tests; expect Pass 1 tests to fail.
- [ ] 3.2 GREEN: update Pass 1's per-cluster runner to derive its inputs from `conversation_context` (the `_from_context`/`_from_packet` cluster prompt builder is already there in `engine/system_b/prompts.py`). Remove the legacy `format_pass1_cluster_prompts` branch.
- [ ] 3.3 RED: in `telemetry.py`, retype `build_run_record(*, request: "CritiqueRequest", ...)` to take `conversation_context: ConversationContext` (or whatever fields the record actually needs — read the function body). Run tests; expect telemetry tests to fail.
- [ ] 3.4 GREEN: update `build_run_record` callers (likely in pipeline.py) to pass the new param.

### 4.0 Migrate the relevance/embedding-tendency reader

Around `pipeline.py:478-499`, there's a flat-string derivation from `request.query` + `request.vanilla_answer` (used for embedding tendency signals). After the new contract, this needs to come from `_lane2_joined_assistant_turns(conversation_context)` or equivalent.

- [ ] 4.1 Identify the exact line range in pipeline.py that uses `request.query` / `request.vanilla_answer` for relevance text.
- [ ] 4.2 RED: add a test that runs the pipeline with a ConversationContext and asserts the relevance text is derived from joined assistant turns, not vanilla_answer.
- [ ] 4.3 GREEN: replace the legacy derivation. The pattern `_lane2_joined_assistant_turns(conversation_context)` already exists; reuse it.

### 5.0 Migrate failing tests one file at a time

- [ ] 5.1 For each failing test file:
  - Read it.
  - For each `CritiqueRequest(query=..., vanilla_answer=...)` construction, replace with a `ConversationContext` that contains the same content as user/assistant turns.
  - Helper: many test files already have a `_ctx` builder. Use it.
- [ ] 5.2 After each test file migration: run that single file (`pytest tests/test_X.py -q`) until green. Then full suite.
- [ ] 5.3 Some tests may be testing the SHIM behavior specifically — those should be DELETED once the shim is gone. Common examples: `tests/test_pipeline_shim_equivalence.py`. Confirm with PM before deleting any test file.

### 6.0 Migrate scripts (run_pipeline.py + stability_check.py + phase1_equivalence_check.py)

- [ ] 6.1 In `scripts/run_pipeline.py`: remove `--legacy-contract` flag and the `CritiqueRequest` construction path. The `--new-contract` flag (if it exists) becomes the only contract.
- [ ] 6.2 In `scripts/stability_check.py`: remove `--legacy-contract` flag and the `legacy_contract` parameter from `_rerun_extraction` (or whatever owns those references at lines 427, 442, 800, 927, 936).
- [ ] 6.3 `scripts/phase1_equivalence_check.py`: per task 1.5 decision (delete or archive). If archived, move to `research/` and note in commit message.
- [ ] 6.4 Run any script-level smoke tests; full suite.

### 7.0 Remove legacy lane functions (TDD by removal)

After 3.x-6.x, no test or script should construct `CritiqueRequest`. Now safe to remove the legacy functions.

- [ ] 7.1 In `pipeline.py`, remove the `else` branches in lane dispatchers that call `run_fingerprint_call` / `run_verification_call` / `run_frame_extraction` / `run_structural_coverage` / `format_pass2_prompt` / `format_pass1_cluster_prompts`. After removal, the dispatchers are simply `if conversation_ir → packet path` (or just call packet path unconditionally if `conversation_ir` is now always set).
- [ ] 7.2 In each lane module, delete the legacy function AND any helper-only-used-by-legacy (e.g. `_build_fingerprint_user_prompt`, `_format_classification_user_prompt`, `_format_pass1_cluster_user_prompt`).
- [ ] 7.3 Remove `_context_to_critique` from `pipeline.py` (NOT `conversation_context.py` — see line ~150 area).
- [ ] 7.4 Remove `CritiqueRequest` dataclass from `pipeline.py` (line 150). Final step.
- [ ] 7.5 Run full suite. Should be green.

### 8.0 Final verification

- [ ] 8.1 `grep -rn "CritiqueRequest" engine/ tests/ scripts/` — should return ZERO results.
- [ ] 8.2 `grep -rn "run_fingerprint_call\b\|run_verification_call\b\|run_frame_extraction\b\|run_structural_coverage\b\|format_pass1_cluster_prompts\b" engine/` — should return zero results (the `_from_packet` and `_from_context` variants are still there with different suffixes).
- [ ] 8.3 `grep -rn "legacy.contract\|legacy_contract" engine/ tests/ scripts/` — should return zero results.
- [ ] 8.4 Full suite green.
- [ ] 8.5 Open PR with title `feat: Phase 6 — remove CritiqueRequest legacy shim`.

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

# Phase 1: Conversation-first contract redesign

**Branch:** `feat/conversation-first-phase-1-contract`
**Handover:** `research/conversation-first-rearchitecture-handover.md`
**Audit:** `research/full-system-audit-2026-04-23.md`
**Scope:** introduce `ConversationContext` as the new lane-input contract + outcome-measurement scaffolding. Zero behavior change on lane outputs. All 4 lanes keep their current prompts and logic. New infrastructure sits alongside the legacy `CritiqueRequest` path via a shim.

## Why this PR

The legacy `CritiqueRequest(query: str, vanilla_answer: str)` contract collapses rich conversation extraction into two flat strings. Lanes then re-derive structure from flat text, losing information extraction spent effort producing. This PR introduces the infrastructure for lanes to receive structured conversation data directly; subsequent PRs (Phase 2) migrate each lane to actually use it.

**Design principle:** add the new path first; keep the old path working; migrate lanes one at a time with measurement. No big-bang.

## Testing approach

TDD red-green for the pure-data parts:
1. `ConversationContext` dataclass + validation
2. Loader function (extraction JSON + conversation.txt → `ConversationContext`)
3. `compare_outputs.py` diff logic

Not TDD (empirical via corpus run):
- The shim in `SystemBPipeline.run()` — behavioral equivalence is tested by running the 10-case corpus through both paths and diffing outputs.

## Relevant Files

- `engine/system_b/pipeline.py` — add `ConversationContext` + shim entry point. Minimal change.
- `scripts/run_pipeline.py` — add `--new-contract` flag + builder. Default: old path.
- `scripts/compare_outputs.py` — **NEW**. Golden-case comparison tool.
- `tests/test_conversation_context.py` — **NEW**. Dataclass + loader tests.
- `tests/test_pipeline_shim_equivalence.py` — **NEW**. Ensures old-path and new-path produce identical serialized output.
- `HOW_IT_WORKS.md` — new architecture section (conversation-first contract introduced, legacy path marked for deprecation).
- `research/conversation-first-rearchitecture-handover.md` — update §"What's shipped" when Phase 1 merges.

### Notes

- Test runner: `python3 -m pytest tests/test_<file>.py -v`
- The 10-case corpus is at `research/test-cases/case_*_conversation.txt` — use these for equivalence testing.
- The acceptance gate is BIT-IDENTICAL output between old and new paths. Any divergence (other than serialization-nondeterminism) is a bug.
- Don't modify lane prompts or lane logic. If tempted, the scope rules forbid it.

## Acceptance Gate

| Axis | Target |
|---|---|
| Old-path vs new-path output diff on 10-case corpus (when new-path is used via shim) | 0 meaningful diffs |
| All existing 123+ tests pass | yes |
| New tests for `ConversationContext` + loader + shim | ≥ 10 new tests, all green |
| HOW_IT_WORKS.md architecture section added | yes |
| `--new-contract` flag documented in `run_pipeline.py --help` | yes |

## Tasks

- [x] 0.0 Preflight
  - [x] 0.1 Confirm PR #13 merged to main: `git log --oneline main -5` shows the merge commit. *Merge commit: `9b5b5af Merge pull request #13 from gofarrrr/feat/extraction-contract-phase-1-live-constraints` (2026-04-24).*
  - [x] 0.2 Confirm you're on fresh main: `git checkout main && git pull && git status`. *Fast-forwarded `3c609a5..9b5b5af`; working tree clean; chore commit `d9ea3cc` landed for 6 historic research docs.*
  - [x] 0.3 Create branch: `git checkout -b feat/conversation-first-phase-1-contract`.
  - [x] 0.4 Read the handover doc in full: `research/conversation-first-rearchitecture-handover.md`.
  - [x] 0.5 Read the audit §2, §3, §7 (pipeline structure, lanes, design decisions). *Read full audit + `research/pipeline-py-structural-map.md` during session kickoff.*
  - [x] 0.6 Map `engine/system_b/pipeline.py` structure (don't try to read linearly):
    ```
    grep -n "^class \|^def \|^    def " engine/system_b/pipeline.py > /tmp/pipeline_map.txt
    ```
    *75 hits across 2200 lines. Spot-checks cross-reference cleanly with `research/pipeline-py-structural-map.md`: `CritiqueRequest:122`, `PipelineConfig:128`, `SystemBPipeline:293`, `run():375`, `_route_deep_check_results_with_optional_tiebreaker:603`, `_run_companion:668`, `_run_frame_pressure:718`, `_run_structural_coverage:771`, `_assemble_delta_card:1253`. The structural map is accurate. `SystemBPipeline.run()` at line 375 is the shim entry point.*

- [x] 1.0 Design the `ConversationContext` data model (TDD)
  - [x] 1.1 Dataclass shape finalized in `engine/system_b/conversation_context.py`. Deviations from sketch: (a) added `LiveConstraint` and `DroppedThread` as typed dataclasses instead of inline `tuple[dict, ...]`; (b) `LiveConstraint.canonical_key: str | None = None` — tolerant of historical JSONs that still emit it; (c) `Turn.speaker: str` with `__post_init__` validation rather than `Literal` (runtime guard); (d) `capture_manifest` and `quote_validation` stay as `dict` passthroughs per PM directive.
  - [x] 1.2 Skipped per PM protocol (technical shape decisions made by session; decisions logged in commit message).
  - [x] 1.3 RED: `tests/test_conversation_context.py::test_conversation_context_minimal` added.
  - [x] 1.4 GREEN: new module `engine/system_b/conversation_context.py`. Keeps `pipeline.py` untouched — shim injection in Phase 1 task 3.0 only.
  - [x] 1.5 RED: `test_turn_invalid_speaker_raises` added (plus `test_turn_zero_index_raises` as a bonus invariant).
  - [x] 1.6 GREEN: `__post_init__` raises `ValueError` on invalid speaker or turn_index < 1.
  - [x] 1.7 RED: `test_conversation_context_asdict_roundtrip_preserves_shape` added.
  - [x] 1.8 GREEN: native `dataclasses.asdict()` handles the whole shape (tuples → lists); no custom `to_dict()` needed.
  - *15/15 new tests pass; full suite 138 passed (no regression).*

- [x] 2.0 Build the loader (TDD)
  - [x] 2.1 RED→GREEN: `test_load_basic_extraction_and_turns` + `test_load_extraction_fields_populate_correctly`.
  - [x] 2.2 Implemented as `engine/system_b/conversation_loader.py::load_conversation_context` (separate module, not in `run_pipeline.py` — keeps IO concerns out of the CLI wrapper). Turn parser uses `^\[Turn (\d+)\] (USER|ASSISTANT):\s*$` regex; buffers inter-marker lines, strips trailing blank lines.
  - [x] 2.3 RED→GREEN: `test_load_capture_critical_returns_valid_empty_context` — `status: "capture_critical"` (no `extraction` field) yields an empty `ExtractionPayload` while preserving `capture_health`, `capture_manifest`, `capture_warnings`. Turns still parse from the conversation file independently.
  - [x] 2.4 Covered by the same test.
  - [x] 2.5 RED→GREEN: `test_load_quote_validation_passes_through_intact` — `_quote_validation` JSON field is mapped to `quote_validation` on `ExtractionPayload`, preserving `retry_attempted`, `retry_succeeded`, `fabricated`.
  - [x] 2.6 Covered by the same test.
  - *Also added: `test_load_live_constraints_with_and_without_canonical_key`, `test_load_dropped_threads_with_and_without_superseded_by`, `test_load_capture_metadata_preserved`, `test_load_real_10_case_corpus_oncologist` (end-to-end against real corpus file), `test_load_empty_conversation_file_yields_zero_turns`.*
  - *9/9 loader tests pass; full suite 147 passed (no regression).*
  - *Corpus sanity check: loader handles all 10 cases at `research/test-cases/case_*_conversation.txt`; declared-vs-parsed turn counts match for every case (header "N turns" → N user + N assistant entries).*

- [x] 3.0 Shim: make `SystemBPipeline.run()` accept either shape
  - [x] 3.1 Read full `run()` method (lines 375–601 in `engine/system_b/pipeline.py`) + `CritiqueRequest` (lines 122–124) + `_map_to_critique_request` (lines 414–482 in `scripts/run_extract.py`) + `_extract_assistant_responses` (lines 315–326, separator `"\n\n---\n\n"`).
  - [x] 3.2 Dispatch added at the top of `run()` (lines 375–383 in pipeline.py): `if isinstance(request, ConversationContext): request = _context_to_critique(request)`. Type annotation updated to `CritiqueRequest | ConversationContext`.
  - [x] 3.3 `_context_to_critique` added to `pipeline.py` (module-level, near `CritiqueRequest`, with delete-in-Phase-3 comment). Logic mirrors `scripts/run_extract.py::_map_to_critique_request` on both the query assembly (decision + tagged constraints + framing + dropped threads) and the vanilla_answer assembly (full-mode when assistant_text > 200 chars, fallback mode otherwise). Per-assistant-turn `.strip()` added to match `_extract_assistant_responses`'s behavior — caught by the equivalence test.
  - [x] 3.4 RED→GREEN: `tests/test_pipeline_shim_equivalence.py`. Two test classes: (a) bit-identical equivalence — compares `_context_to_critique(ctx)` against `_map_to_critique_request(equivalent_dict, assistant_text)` on 8 shape variants (empty/full, active/dropped constraints, with/without framing, with/without superseded_by, short/long assistant text, multi-turn); (b) dispatch — `run()` routes `ConversationContext` through the shim and routes `CritiqueRequest` without invoking it (patched spy).
  - [x] 3.5 One real divergence caught by `test_full_case_constraints_framing_threads_long_assistant_text` — the legacy `_extract_assistant_responses` strips per-turn content but the shim was joining raw `Turn.text`. Fixed: shim now strips per assistant-turn before joining. *This is exactly the class of bug the equivalence test exists to catch; good signal the test is doing its job.*
  - [x] 3.6 Full suite: **157 passed, 93 subtests passed. Zero regression.** (147 before + 10 new shim tests.)

- [x] 4.0 CLI: add `--new-contract` flag
  - [x] 4.1 `scripts/run_pipeline.py` argparse has the boolean flag (default false). Validation: flag requires both `--extraction-file` and `--conversation-file`; mismatched usage returns a structured error.
  - [x] 4.2 When set, `load_conversation_context(extraction_path, conversation_path)` builds the context and passes it to `pipeline.run(context)`. Legacy path untouched.
  - [x] 4.3 Help text includes: "Use the new ConversationContext contract (Phase 1). Default: off (legacy CritiqueRequest path). During Phase 1 these paths are behaviorally equivalent; Phase 2+ lane migrations will let the new path produce richer lane output. Requires --extraction-file and --conversation-file."

- [x] 5.0 Build `scripts/compare_outputs.py`
  - [x] 5.1 `scripts/compare_outputs.py` takes two result.json paths, returns exit 0 on match / 1 on mismatch. Also importable: `compare_results(left, right) -> Comparison`.
  - [x] 5.2 Compares exactly the 6 fields listed: `detected_tendencies`, `delta_card.findings`, `companion_cheat_sheet.anchors`, `frame_pressure_card.reframings`, `structural_coverage_card.gap_questions`, `audit_summary.triggered_tendencies`. All timing + `boundary_calls` metadata ignored.
  - [x] 5.3 Output: per-field MATCH/DIFFER line + summary + per-field diff on mismatches.
  - [x] 5.4 RED→GREEN: `test_identical_payloads_all_match`.
  - [x] 5.5 Implemented.
  - [x] 5.6 RED→GREEN: `test_mismatch_on_detected_tendencies`, `test_mismatch_on_delta_card_findings`, `test_timing_differences_are_ignored`, `test_missing_lane_cards_treated_as_empty`, `test_render_report_labels_match_and_diverge`, `test_main_exit_codes`.
  - [x] 5.7 7/7 tests green; full suite 164 passed (157 + 7 new).

- [~] 6.0 End-to-end equivalence — **scope adjusted; reported to PM for confirmation**
  - *Issue surfaced:* `engine/system_b/boundary_provider.py:82` sets `temperature=0.2` on every OpenRouter call. The pipeline is non-deterministic by design, so literal "bit-identical pipeline output" across two runs on the same input is unachievable — even old-path vs old-path on the same `CritiqueRequest` would produce diffs that aren't shim bugs. Any divergence caught by pipeline-level comparison would conflate shim correctness with LLM noise.
  - *Scope adjustment:* the architectural commitment Phase 1 makes is that `_context_to_critique(ctx)` produces bit-identical `CritiqueRequest` to what `_map_to_critique_request(extraction_dict, assistant_text)` produces. That's testable deterministically at the shim boundary without LLM calls.
  - [x] 6.1 `scripts/phase1_equivalence_check.py` runs this check against all 10 corpus conversations. For each: build `ConversationContext` via the loader, apply the shim, build the legacy CR via the original mapping function on the same extraction + `_extract_assistant_responses(conversation_text)`, compare `query` + `vanilla_answer` byte-by-byte.
  - [x] 6.2 **Result: 10/10 cases match bit-for-bit on both `query` and `vanilla_answer`.** Evidence committed to `research/test-cases/phase1-equivalence-2026-04-24/shim-equivalence-report.md`.
  - [x] 6.3 Evidence path committed.
  - **Open question for PM:** proceed to 7.0/8.0 on this CR-level evidence, or run a limited pipeline-level spot-check despite the temperature-0.2 noise? See checkpoint report.

- [ ] 7.0 Documentation
  - [ ] 7.1 Update `HOW_IT_WORKS.md` §Step 3 — add a subsection "Conversation-first contract (Phase 1)" describing the new `ConversationContext` shape, the shim, and the deprecation plan for `CritiqueRequest`.
  - [ ] 7.2 Update `research/conversation-first-rearchitecture-handover.md` §"What's shipped" to note Phase 1 is merged (do this when the PR merges, not before).
  - [ ] 7.3 Add a brief note in `SKILL.md` or leave unchanged (Claude's orchestration is unaffected — the flag change is internal to the Python pipeline).

- [ ] 8.0 Ship
  - [ ] 8.1 Run full test suite: `python3 -m pytest tests/ -v`. All green.
  - [ ] 8.2 Run the 10-case equivalence test (task 6.0). Zero diffs.
  - [ ] 8.3 Commit with a descriptive message capturing: new `ConversationContext` shape, shim, `compare_outputs.py`, equivalence evidence, docs.
  - [ ] 8.4 Push + open PR. Title: `feat(pipeline): conversation-first contract scaffolding (phase 1)`.
  - [ ] 8.5 PR description includes: the shim equivalence evidence, the `compare_outputs.py` tool, the acceptance-gate table, honesty clause that this PR is infrastructure only (no lane behavior change, Phase 2 migrates lanes).
  - [ ] 8.6 On merge: update handover doc to reflect shipped state.

## Phase 2 preview (do NOT do in this PR)

After Phase 1 merges, Phase 2 migrates lanes one at a time. Each Phase 2 PR:
1. Rewrites one lane's prompts to use `ConversationContext` structure
2. Runs old-path vs new-path comparison on 10-case corpus
3. Human-reads a sample; lane ships if qualitative output is ≥ old-path

Order: Lane 3 → Lane 4 → Lane 1 → Lane 2. See handover §"The plan" for detail.

**Out of scope for Phase 1.** If you're in Phase 1 and tempted to migrate a lane, stop. Separate PR.

## Risks

1. **Shim divergence.** If `_context_to_critique` diverges from `_map_to_critique_request`, equivalence breaks. Mitigation: copy the logic directly; add a regression test comparing both functions on the same input.
2. **Scope creep.** Tempting to "while I'm here, fix X." Don't. Phase 1 is additive only. Phase 4 addresses pipeline.py refactor.
3. **Branch size.** Keep Phase 1 tight — ≤ 15 commits. If it grows, reconsider scope.
4. **Forgetting to run equivalence on all 10 cases.** The gate is 10/10, not 5/10. If a case produces diffs and it's case-specific, that's still a bug.

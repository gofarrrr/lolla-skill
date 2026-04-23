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

- [ ] 2.0 Build the loader (TDD)
  - [ ] 2.1 RED: write test — `load_conversation_context(extraction_path, conversation_path)` produces a `ConversationContext` with correctly parsed turns + extraction fields.
  - [ ] 2.2 GREEN: add `load_conversation_context` function in `scripts/run_pipeline.py` (or extract to `engine/system_b/conversation_loader.py`). Parses extraction JSON + conversation.txt per-turn-marker regex.
  - [ ] 2.3 RED: write test — loading a capture_critical extraction returns the metadata correctly so downstream can check `capture_health == "critical"`.
  - [ ] 2.4 GREEN: verify.
  - [ ] 2.5 RED: write test — loading extraction where `_quote_validation.fabricated > 0` passes the validation fields through intact.
  - [ ] 2.6 GREEN: verify.

- [ ] 3.0 Shim: make `SystemBPipeline.run()` accept either shape
  - [ ] 3.1 Read the full `SystemBPipeline.run()` method in `engine/system_b/pipeline.py` to understand the shape.
  - [ ] 3.2 Add an overload or dispatch at the top of `run()`:
    ```python
    def run(self, request: CritiqueRequest | ConversationContext) -> PipelineResult:
        if isinstance(request, ConversationContext):
            # Build a CritiqueRequest from the context for legacy lane delegation
            critique = _context_to_critique(request)
        else:
            critique = request
        # ... existing logic uses `critique` ...
    ```
  - [ ] 3.3 Add `_context_to_critique(context: ConversationContext) -> CritiqueRequest` that builds `query + vanilla_answer` from the conversation structure using the SAME logic as `_map_to_critique_request` in `run_extract.py`. Copy that logic; don't change it.
  - [ ] 3.4 RED: write test — `SystemBPipeline.run(critique_request)` and `SystemBPipeline.run(conversation_context)` produce identical `PipelineResult` when given equivalent inputs. Mock the `BoundaryClient` so we don't make real API calls in the test.
  - [ ] 3.5 GREEN: verify. If test fails, likely the `_context_to_critique` logic diverges from `_map_to_critique_request` — align them.
  - [ ] 3.6 Run the existing 123-test suite: `python3 -m pytest tests/ -v`. Zero regression expected.

- [ ] 4.0 CLI: add `--new-contract` flag
  - [ ] 4.1 Update `scripts/run_pipeline.py` argparse to add `--new-contract` (boolean flag, default false).
  - [ ] 4.2 When flag is set, build `ConversationContext` via `load_conversation_context()` and pass to `pipeline.run()`. When not set, use the existing `CritiqueRequest` path.
  - [ ] 4.3 Help text: "Use the new ConversationContext contract. Default: off (uses legacy CritiqueRequest). During Phase 1 these paths are behaviorally equivalent; Phase 2+ lane migrations will make the new path produce better lane output."

- [ ] 5.0 Build `scripts/compare_outputs.py`
  - [ ] 5.1 Purpose: take two result.json files (from old-path and new-path runs), diff the meaningful fields, report match/mismatch.
  - [ ] 5.2 Fields to diff: `detected_tendencies`, `delta_card.findings`, `companion_cheat_sheet.anchors`, `frame_pressure_card.reframings`, `structural_coverage_card.gap_questions`, `audit_summary.triggered_tendencies`. Don't diff timing fields (they'll differ by design) or boundary_call metadata.
  - [ ] 5.3 Output format: per-field match/mismatch summary + full diff on mismatches.
  - [ ] 5.4 RED: write test in `tests/test_compare_outputs.py` — two identical result files produce "all match" output.
  - [ ] 5.5 GREEN: implement.
  - [ ] 5.6 RED: write test — two result files that differ in `detected_tendencies` produce mismatch on that field.
  - [ ] 5.7 GREEN: verify.

- [ ] 6.0 End-to-end equivalence test on 10-case corpus
  - [ ] 6.1 For each of the 10 cases at `research/test-cases/case_*_conversation.txt`:
    - Extract: `python3 scripts/run_extract.py --conversation-file <path> --output-file /tmp/case_extraction.json`
    - Old path: `python3 scripts/run_pipeline.py --extraction-file /tmp/case_extraction.json --conversation-file <conv> --output-file /tmp/old_result.json --skip-revision`
    - New path: `python3 scripts/run_pipeline.py --extraction-file /tmp/case_extraction.json --conversation-file <conv> --output-file /tmp/new_result.json --skip-revision --new-contract`
    - Diff: `python3 scripts/compare_outputs.py /tmp/old_result.json /tmp/new_result.json`
  - [ ] 6.2 Expected: zero meaningful diffs. If diffs appear, they're a bug in `_context_to_critique` — align the logic.
  - [ ] 6.3 Commit the 10-case equivalence evidence to `research/test-cases/phase1-equivalence-2026-MM-DD/`.

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

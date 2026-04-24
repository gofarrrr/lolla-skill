# Phase 1: Provenance-Bearing Conversation IR

**Future branch:** `feat/conversation-first-phase-1-ir`
**Roadmap:** `plans/conversation-first-context-engineering-roadmap.md` -> Phase 1
**Phase 0.1 gate:** `research/capture-fidelity-audit-2026-04-25.md`
**Phase 0.5 gate:** `research/phase0.5-adoption-memo-2026-04-24.md`
**Drill-back spike:** `research/phase0.5-drillback-spike-2026-04-24.md`
**Scope:** add a shared, provenance-bearing `ConversationIR` alongside `ConversationContext`. Build it from current local artifacts, expose drill-back primitives, and add observability. Do not change lane behavior, prompts, routing, extraction, or pipeline orchestration semantics.

## Why This Phase

The conversation-first migration moved the lanes from the old `CritiqueRequest`
flattening toward `ConversationContext`, but `ConversationContext` is still a
transport object. Phase 1 adds the missing context-engineering layer: typed
conversation objects with honest provenance.

The goal is not better prose summaries. The goal is reversible entropy
reduction:

- turns remain the source of truth
- derived objects carry provenance
- exact spans are distinguished from turn-level paraphrases
- lane packets can later drill back to source text without re-parsing the whole conversation

## Approved Phase 1 Decisions

- v1 object set is intentionally narrow: `Turn`, `SpanRef`, `FrameAnchor`, `UserIssueEvent`, `StanceEvent`, and `ConversationIR`.
- `SpanRef` is turn-relative and end-exclusive: `SpanRef(turn_index, speaker, start_char, end_char)`.
- Because current captures reuse the same turn number for the user and assistant message in a pair, turn identity must include `speaker`.
- Provenance is a union, not one generic field:
  - `span`: exact substring in one turn, with `SpanRef`
  - `turn_ref`: source turn is known, but the derived text is paraphrased
  - `derivation`: inferred from multiple turns and/or derived objects
- `UserIssueEvent` stays one family with `kind`, not separate `ConstraintEvent` / `ConcernEvent` / `OpenLoop` top-level types.
- `UserIssueEvent.kind` mapping:
  - `live_constraints` -> `constraint`
  - `dropped_threads` with unresolved/active status -> `concern`
  - `dropped_threads` with `acknowledged_then_dropped` or `superseded_by` -> `open_loop`
- Lane 3 frame elements are `FrameAnchor`s, not `UserIssueEvent`s.
- `StanceEvent` carries `speaker`; user commitments and assistant trajectory events share the primitive.
- `ActorRef`, `DecisionOption`, `ReasoningSegment`, and `CoverageTarget` are deferred/projection candidates.
- Reducer-style updates are adopted: named pure functions produce IR updates instead of ad-hoc mutation.

## Relevant Files

- `engine/system_b/ir.py` - **NEW**. IR dataclasses and provenance union.
- `engine/system_b/ir_builders.py` - **NEW**. Reducer-style update functions.
- `engine/system_b/ir_constructor.py` - **NEW**. Convert `ConversationContext` and current extraction payloads into `ConversationIR`.
- `engine/system_b/conversation_context.py` - Existing transport dataclasses; read for compatibility with `Turn` and `ExtractionPayload`.
- `engine/system_b/conversation_loader.py` - Existing artifact loader used by constructor tests.
- `engine/system_b/pipeline.py` - Integration point for constructing IR as observability only. No lane behavior changes.
- `engine/system_b/telemetry.py` - Possible place for IR construction metrics or summary fields if pipeline observability needs it.
- `scripts/run_pipeline.py` - Serialization surface; only update if an explicit audit/summary field is added.
- `tests/test_ir.py` - **NEW**. IR shape, reducer, constructor, serialization tests.
- `tests/test_ir_drillback.py` - **NEW**. Source-ref -> IR object -> provenance -> source text drill-back tests.
- `tests/test_pipeline_shim_equivalence.py` - Extend only if pipeline integration touches dispatch or serialized audit shape.
- `research/test-cases/case_user_has_plan_conversation.txt` - Drill-back fixture.
- `research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_extraction.json` - Existing extraction fixture.
- `research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/user_has_plan_new_run1.json` - Existing Lane 3 output fixture.

### Notes

- Do not start implementation until PM approves this task file.
- Do not create a new branch until task `0.0` begins.
- Do not modify `research/conversation-first-extraction-evaluation-2026-04-24.md`; it is user-owned in-progress context.
- Do not add API calls or live OpenRouter dependencies. Phase 1 is local deterministic infrastructure.
- Do not change lane prompts or lane selection. Later phases build lane packet builders and consume the IR.
- Prefer exact spans only when a literal substring can be found. Paraphrased extraction fields get `turn_ref` or `derivation`, not fake spans.

## Testing Approach

Use vertical TDD slices:

1. RED: write one behavior test.
2. GREEN: implement the smallest code to pass.
3. REFACTOR: clean only after the local slice is green.

Good TDD targets:

- provenance union validation
- turn-relative span resolution
- reducer purity
- constructor mapping from current artifacts
- drill-back resolver behavior
- serialization round trips
- pipeline integration preserving lane outputs

Not TDD'd:

- manual annotation agreement; humans review the prepared artifact
- prompt changes; Phase 1 has no prompt changes
- live quality measurement; Phase 1 has no live LLM calls

## Acceptance Gate

| Axis | Target | How to measure |
|---|---|---|
| Structural artifact | `ir.py`, `ir_builders.py`, `ir_constructor.py`, and tests exist | file existence + unit tests |
| Provenance coverage | every derived IR object has non-empty provenance | unit test over constructed fixtures |
| Provenance honesty | exact spans only for literal substrings; paraphrases use `turn_ref` or `derivation` | constructor tests |
| Drill-back | packet-like source ref resolves to source turn text in <= 3 logical hops | `tests/test_ir_drillback.py` |
| Reducer invariant | IR updates are named pure functions; no hidden global state | reducer tests + code review |
| Lane behavior | no lane output behavior changes | existing pipeline/context tests stay green |
| Serialization | `ConversationIR` round trips to JSON-compatible dicts | unit tests |
| Cost/latency | IR construction adds < 50ms on local corpus fixtures | local benchmark test or recorded timing |
| Annotation agreement | two reviewers agree on `UserIssueEvent.kind` >= 80% on protected cases | manual review artifact |
| Kill criteria | if provenance is unstable or kind agreement < 80%, narrow the ontology before Phase 2 | PM decision gate |

## Tasks

- [ ] 0.0 Create feature branch and verify baseline
  - [ ] 0.1 Confirm current branch and worktree: `git branch --show-current` and `git status --short`. Note user-owned untracked files and leave them untouched.
  - [ ] 0.2 Confirm Phase 0.1 and Phase 0.5 artifacts exist: capture audit, adoption memo, drill-back spike, and this task file.
  - [ ] 0.3 Create and checkout branch: `git switch -c feat/conversation-first-phase-1-ir`.
  - [ ] 0.4 Run baseline local tests: `python3 -m pytest tests/test_conversation_context.py tests/test_conversation_loader.py tests/test_frame_pressure_contextual.py tests/test_pipeline_shim_equivalence.py -q`.
  - [ ] 0.5 Record the baseline result in this task file before code changes.

- [ ] 1.0 Define IR dataclasses and provenance union (TDD)
  - [ ] 1.1 RED: add `tests/test_ir.py::test_span_ref_resolves_exact_turn_relative_text` using the `user_has_plan` Turn 2 pipeline quote from the drill-back spike.
  - [ ] 1.2 GREEN: create `engine/system_b/ir.py` with `SpanRef` and a resolver helper or method that returns the exact substring from a turn map.
  - [ ] 1.3 RED: add tests for invalid spans: missing turn, speaker mismatch, negative offsets, end before start, and end beyond turn length.
  - [ ] 1.4 GREEN: enforce span validation with clear `ValueError`s.
  - [ ] 1.5 RED: add tests for provenance variants: `span`, `turn_ref`, and `derivation`. Each must serialize to a JSON-compatible dict.
  - [ ] 1.6 GREEN: implement provenance dataclasses or a typed union. Keep the public shape explicit enough for code review.
  - [ ] 1.7 RED: add tests for `FrameAnchor`, `UserIssueEvent`, `StanceEvent`, and `ConversationIR` minimal construction.
  - [ ] 1.8 GREEN: implement the v1 dataclasses. Include `StanceEvent.speaker` and `UserIssueEvent.kind`.
  - [ ] 1.9 RED: add tests that deferred candidates are not present as first-class v1 dataclasses: `ActorRef`, `DecisionOption`, `ReasoningSegment`, `CoverageTarget`.
  - [ ] 1.10 GREEN: keep the v1 object set narrow.
  - [ ] 1.11 Run `python3 -m pytest tests/test_ir.py -q`.

- [ ] 2.0 Implement reducer-style builders (TDD)
  - [ ] 2.1 RED: test `add_turn` returns a new `ConversationIR` with the appended/replaced turn while leaving the original IR unchanged.
  - [ ] 2.2 GREEN: create `engine/system_b/ir_builders.py` and implement `add_turn`.
  - [ ] 2.3 RED: test `add_span` validates the span against stored turns before adding it.
  - [ ] 2.4 GREEN: implement `add_span`.
  - [ ] 2.5 RED: test `add_frame_anchor` requires non-empty provenance and preserves the source frame fields.
  - [ ] 2.6 GREEN: implement `add_frame_anchor`.
  - [ ] 2.7 RED: test `add_user_issue_event(kind, status, provenance)` accepts only approved kinds/statuses.
  - [ ] 2.8 GREEN: implement `add_user_issue_event`.
  - [ ] 2.9 RED: test `supersede_issue(issue_id, by_ref)` updates lifecycle without mutating the original event.
  - [ ] 2.10 GREEN: implement `supersede_issue`.
  - [ ] 2.11 RED: test `add_stance_event` records `speaker`, stance label, and provenance.
  - [ ] 2.12 GREEN: implement `add_stance_event`.
  - [ ] 2.13 Run `python3 -m pytest tests/test_ir.py -q`.

- [ ] 3.0 Implement `ir_constructor.py` from current artifacts (TDD)
  - [ ] 3.1 RED: test `construct_conversation_ir(context)` copies all `ConversationContext.turns` into `ConversationIR` with stable `(turn_index, speaker)` identity.
  - [ ] 3.2 GREEN: create `engine/system_b/ir_constructor.py` and implement turn ingestion.
  - [ ] 3.3 RED: test live constraints become `UserIssueEvent(kind="constraint")` with `turn_ref` provenance, not fake spans.
  - [ ] 3.4 GREEN: map `ExtractionPayload.live_constraints` to `UserIssueEvent`s using introduced/source turns where available and conservative `turn_ref` provenance.
  - [ ] 3.5 RED: test dropped threads map to `kind="open_loop"` when `status="acknowledged_then_dropped"` or `superseded_by` is present.
  - [ ] 3.6 GREEN: implement dropped-thread mapping and lifecycle fields.
  - [ ] 3.7 RED: test unresolved/active dropped-thread-like fixtures map to `kind="concern"`.
  - [ ] 3.8 GREEN: implement the concern/open_loop discriminator.
  - [ ] 3.9 RED: test the constructor does not fabricate stance events from `synthesized_position` or other paraphrased summaries.
  - [ ] 3.10 GREEN: keep stance construction explicit through reducer builders in Phase 1; Phase 3 can add assistant trajectory extraction. If a stance event is added from a fixture, it must be backed by an exact `SpanRef`.
  - [ ] 3.11 RED: test `original_framing` becomes a `FrameAnchor` with `turn_ref` provenance, not an exact span, because it is extractor paraphrase.
  - [ ] 3.12 GREEN: implement `FrameAnchor` construction from current extraction fields.
  - [ ] 3.13 RED: test the constructor never emits a `span` provenance when the literal text is not found.
  - [ ] 3.14 GREEN: implement exact-substring guard.
  - [ ] 3.15 Run `python3 -m pytest tests/test_ir.py -q`.

- [ ] 4.0 Implement drill-back resolver (TDD)
  - [ ] 4.1 RED: add `tests/test_ir_drillback.py::test_drillback_from_frame_source_ref_to_raw_turn_text` using the Phase 0.5 Chain 1 fixture.
  - [ ] 4.2 GREEN: implement a small resolver that maps a packet-like source ref to IR object id, then to provenance, then to source text.
  - [ ] 4.3 RED: test `span` provenance returns exact text and metadata.
  - [ ] 4.4 GREEN: implement span drill-back result.
  - [ ] 4.5 RED: test `turn_ref` provenance returns the full source turn and marks span text unavailable.
  - [ ] 4.6 GREEN: implement turn-ref drill-back result.
  - [ ] 4.7 RED: test `derivation` provenance returns lineage refs without pretending to have one source span.
  - [ ] 4.8 GREEN: implement derivation drill-back result.
  - [ ] 4.9 RED: test missing source refs fail closed with a useful error.
  - [ ] 4.10 GREEN: implement failure path.
  - [ ] 4.11 Run `python3 -m pytest tests/test_ir_drillback.py -q`.

- [ ] 5.0 Serialization and local performance budget
  - [ ] 5.1 RED: test `ConversationIR` serializes to a JSON-compatible dict and round-trips without losing provenance type.
  - [ ] 5.2 GREEN: implement serialization helpers using local repo style.
  - [ ] 5.3 RED: test construction over the `user_has_plan` fixture completes under 50ms on local hardware with a generous stable threshold.
  - [ ] 5.4 GREEN: optimize only if needed; record measured time in this task file.
  - [ ] 5.5 Run `python3 -m pytest tests/test_ir.py tests/test_ir_drillback.py -q`.

- [ ] 6.0 Pipeline observability integration, no lane behavior change
  - [ ] 6.1 Decide the smallest observability surface: preferred default is an `ir_summary` in audit metadata, not a full IR dump in normal output.
  - [ ] 6.2 RED: add a test proving `SystemBPipeline.run(ConversationContext)` constructs IR when context is present and preserves existing lane outputs.
  - [ ] 6.3 GREEN: thread IR construction into `pipeline.py` without feeding it to lanes.
  - [ ] 6.4 RED: add a test proving legacy `CritiqueRequest` input does not require IR construction.
  - [ ] 6.5 GREEN: keep legacy path stable.
  - [ ] 6.6 RED: if serialized output gains `audit_summary.ir_summary`, add a contract test for that field and update comparison tooling only if needed.
  - [ ] 6.7 GREEN: keep output change scoped to observability.
  - [ ] 6.8 Run `python3 -m pytest tests/test_pipeline_shim_equivalence.py tests/test_run_pipeline_contract_default.py -q`.

- [ ] 7.0 Manual annotation exercise on protected cases
  - [ ] 7.1 Prepare a small annotation table for three protected cases: `user_has_plan`, `whistleblower`, and one messy multi-thread case.
  - [ ] 7.2 Include each `UserIssueEvent` text, status, provenance tier, and candidate `kind`.
  - [ ] 7.3 Stop for two-reviewer classification. Do not proceed if reviewers cannot complete the exercise.
  - [ ] 7.4 Record agreement rate in this task file and in a research artifact.
  - [ ] 7.5 If agreement is < 80%, STOP and narrow the ontology before shipping.

- [ ] 8.0 Verification
  - [ ] 8.1 Run IR tests: `python3 -m pytest tests/test_ir.py tests/test_ir_drillback.py -q`.
  - [ ] 8.2 Run relevant context and pipeline tests: `python3 -m pytest tests/test_conversation_context.py tests/test_conversation_loader.py tests/test_pipeline_shim_equivalence.py tests/test_run_pipeline_contract_default.py -q`.
  - [ ] 8.3 Run the full test suite: `python3 -m pytest tests -q`.
  - [ ] 8.4 Verify no live API calls were required.
  - [ ] 8.5 Verify lane output surfaces did not change except approved audit observability.
  - [ ] 8.6 Update this task file with verification results.

- [ ] 9.0 Documentation and ship gate
  - [ ] 9.1 Update `HOW_IT_WORKS.md` with a concise Conversation IR paragraph after the existing `ConversationContext` discussion.
  - [ ] 9.2 Update `plans/conversation-first-context-engineering-roadmap.md` only if implementation materially changed the approved Phase 1 shape.
  - [ ] 9.3 Write a short Phase 1 acceptance note in `research/` summarizing provenance coverage, drill-back, annotation agreement, latency, and residual risks.
  - [ ] 9.4 Stop for PM review before PR creation if any gate is ambiguous.
  - [ ] 9.5 Commit implementation and open PR only after all gates are satisfied.

## Phase 2 Preview (Do Not Do In This PR)

Phase 2 indexes user-side context properly and starts replacing summary-only
fields with provenance-bearing events. It may deepen `FrameAnchor` and
`UserIssueEvent` construction, but Phase 1 should not migrate lane packet
builders or change lane behavior.

## Risks

1. **Fake precision.** The easiest mistake is turning paraphrased extraction text into fake exact spans. The provenance union exists to prevent this.
2. **Object-set creep.** `ReasoningSegment`, `DecisionOption`, `CoverageTarget`, and `ActorRef` are tempting. Keep them out of v1 unless PM explicitly reopens the gate.
3. **Duplicate turn abstractions.** `ConversationContext` already has `Turn`. If `ir.py` defines another `Turn`, make sure there is one canonical public IR turn shape and no divergent semantics.
4. **Output-schema creep.** Observability is useful, but full IR dumps in normal output may churn downstream tests and users. Prefer summaries or sidecar/debug surfaces unless PM approves more.
5. **Annotation disagreement.** If reviewers cannot reliably separate `constraint`, `concern`, and `open_loop`, the correct response is to simplify, not argue the ontology into existence.

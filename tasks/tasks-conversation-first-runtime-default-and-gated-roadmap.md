# Conversation-first runtime default + gated roadmap

## Relevant Files

- `scripts/run_pipeline.py` - CLI contract and runtime input selection. This is where ConversationContext should become the default when the caller supplies `--extraction-file` + `--conversation-file`, and where legacy should become an explicit opt-out.
- `tests/test_run_pipeline_contract_default.py` - New behavior tests for the CLI/runtime contract. Tests should patch live pipeline loading so they do not call OpenRouter.
- `SKILL.md` - Production `/lolla` invocation instructions. Step 3 currently calls `run_pipeline.py` without `--new-contract`; this file must accurately describe that production now uses the ConversationContext path by default.
- `HOW_IT_WORKS.md` - Big-picture architecture and Step 3 flow. Must stay aligned with the final runtime contract and escape hatch.
- `scripts/phase2a_lane3_quality_check.py` - Measurement script that currently differentiates old/new paths using `--new-contract`; must keep old/new comparison valid after the default flip.
- `scripts/phase2b_lane4_quality_check.py` - Same old/new measurement preservation requirement as Phase 2a.
- `scripts/phase2c_lane1_quality_check.py` - Same old/new measurement preservation requirement as Phase 2a, with Lane 1 cascade metrics.
- `scripts/phase2d_lane2_quality_check.py` - Same old/new measurement preservation requirement as Phase 2a, with Lane 2 fingerprint/cascade metrics.
- `scripts/stability_check.py` - Pipeline rerun harness. Its default behavior with a conversation file should be reviewed so stability runs measure the intended production path.
- `engine/system_b/conversation_loader.py` - Existing loader used to build `ConversationContext` from extraction + conversation files. Likely not modified, but relevant for tests and verification.
- `engine/system_b/pipeline.py` - Existing `SystemBPipeline.run()` accepts `CritiqueRequest | ConversationContext`. Likely not modified for the default flip, but relevant for contract tests.
- `research/conversation-first-runtime-default-decision-2026-04-24.md` - New product decision / acceptance artifact for the runtime default switch.
- `research/capture-fidelity-audit-2026-04-25.md` - New Phase 0.1 audit artifact.
- `research/phase0.5-adoption-memo-2026-04-XX.md` - New Phase 0.5 external systems study artifact.
- `research/phase0.5-drillback-spike-2026-04-XX.md` - New spike artifact showing packet -> IR object -> source span -> raw turn drill-back.
- `plans/conversation-first-context-engineering-roadmap.md` - Source roadmap for gates, phase boundaries, and v1 IR doctrine.
- `research/legacy-pr-design-archaeology.md` - Source checklist for Phase 0.5 validation/falsification.
- `tasks/tasks-conversation-first-phase-1-ir.md` - New Phase 1 kickoff task list, created only after Phase 0.5 approval.
- `tasks/tasks-conversation-first-runtime-default-and-gated-roadmap.md` - This task list. Keep checkboxes current as work progresses.

### Notes

- This task list combines task-list gating and TDD vertical slices.
- Task-list gating means the coder stops at PM review gates before proceeding to the next phase.
- TDD vertical slices mean implementation work proceeds one observable behavior at a time, with red-green-refactor cycles instead of bulk test writing.
- The runtime-default switch is a product decision, not a silent cleanup. The current state is: ConversationContext code paths exist and were measured with `--new-contract`, but production `/lolla` invocation still runs the legacy shim path through `SKILL.md`.
- Default lean: make the ConversationContext path the default runtime for file-based production calls that provide both extraction and conversation files, and keep legacy as an explicit opt-out.
- Before implementation, explicitly decide what happens for `--extraction-json` and file-based calls without `--conversation-file`. Do not let this fall out accidentally from argparse validation.
- Prefer adding `--legacy-contract` as the new opt-out. Keeping `--new-contract` as a deprecated compatibility alias for one release is acceptable if it reduces script churn, but the docs should present the new path as the default.
- At each gated task boundary, the coder stops for PM review before proceeding.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Update the file after completing each sub-task, not just after completing an entire parent task.

For implementation tasks, use vertical TDD slices:

- Write one behavior test that fails.
- Implement only enough code to pass that test.
- Run the relevant tests.
- Refactor only after the suite is green.
- Do not write a batch of tests up front.

## Tasks

- [ ] 0.0 Create feature branch
  - [ ] 0.1 Inspect current branch and working tree with `git status --short`; note any user-owned/untracked files and do not modify them unless the task explicitly requires it.
  - [ ] 0.2 Create and checkout a new branch for this work, for example `git switch -c feat/conversation-first-runtime-default`.
  - [ ] 0.3 Run a quick baseline test command that does not require network, such as `python3 -m pytest tests/test_conversation_loader.py tests/test_pipeline_shim_equivalence.py -q`, and record the result in this task file.

- [ ] 1.0 Make the production runtime contract explicit
  - [ ] 1.1 Read `SKILL.md` Step 3, `scripts/run_pipeline.py` argparse/input-selection code, `HOW_IT_WORKS.md` Step 3, `plans/conversation-first-context-engineering-roadmap.md` current-state sections, and `research/legacy-pr-design-archaeology.md`.
  - [ ] 1.2 Write the intended CLI contract in `research/conversation-first-runtime-default-decision-2026-04-24.md`, including the exact behavior for `--extraction-file` + `--conversation-file`, `--legacy-contract`, existing `--new-contract`, `--extraction-file` without `--conversation-file`, and `--extraction-json`.
  - [ ] 1.3 Decide whether `--new-contract` remains as a deprecated no-op alias for one release or is removed/renamed immediately. Record the decision and rationale in the decision artifact.
  - [ ] 1.4 Define the production invariant in one sentence: `/lolla` production invocations must exercise the same ConversationContext path that Phase 2 measurements exercised.
  - [ ] 1.5 Stop for PM review before implementation. Do not edit runtime behavior until the contract artifact is approved.

- [ ] 2.0 Implement the ConversationContext-default runtime switch with legacy opt-out
  - [ ] 2.1 RED: add one behavior test showing that `scripts/run_pipeline.py --extraction-file X --conversation-file Y --output-file Z --skip-revision` builds and passes a `ConversationContext` to `SystemBPipeline.run()` by default.
  - [ ] 2.2 GREEN: implement the smallest change in `scripts/run_pipeline.py` that makes the test pass.
  - [ ] 2.3 RED: add one behavior test showing that `--legacy-contract` with the same file inputs builds and passes a `CritiqueRequest` instead.
  - [ ] 2.4 GREEN: add `--legacy-contract` and the corresponding input-selection branch.
  - [ ] 2.5 RED: add one behavior test for the approved `--new-contract` compatibility behavior from Task 1.3, either deprecated alias behavior or explicit rejection with a clear error.
  - [ ] 2.6 GREEN: implement the approved `--new-contract` compatibility behavior and update help text.
  - [ ] 2.7 RED: add one behavior test for the approved no-conversation-file case from Task 1.2, covering either explicit error or legacy fallback.
  - [ ] 2.8 GREEN: implement the no-conversation-file behavior without weakening the production invariant.
  - [ ] 2.9 RED: add one behavior test for the approved `--extraction-json` behavior from Task 1.2.
  - [ ] 2.10 GREEN: implement the `--extraction-json` behavior.
  - [ ] 2.11 Refactor only after all contract tests are green; keep any helper introduced for input selection small and CLI-facing.
  - [ ] 2.12 Run `python3 -m pytest tests/test_run_pipeline_contract_default.py -q`.

- [ ] 3.0 Preserve and update old-path/new-path measurement tooling
  - [ ] 3.1 RED: add or update a test/helper check proving that an "old path" measurement command now includes `--legacy-contract`.
  - [ ] 3.2 GREEN: update `scripts/phase2a_lane3_quality_check.py` so `new_contract=False` uses `--legacy-contract` and `new_contract=True` uses the new default path.
  - [ ] 3.3 Repeat the same old/new command update for `scripts/phase2b_lane4_quality_check.py`.
  - [ ] 3.4 Repeat the same old/new command update for `scripts/phase2c_lane1_quality_check.py`.
  - [ ] 3.5 Repeat the same old/new command update for `scripts/phase2d_lane2_quality_check.py`.
  - [ ] 3.6 Review `scripts/stability_check.py`; decide whether Mode B reruns should follow the new production default when a conversation file is available or expose an explicit `--legacy-contract` option.
  - [ ] 3.7 Update measurement script docstrings and usage text so "old" means explicit legacy opt-out and "new" means default ConversationContext runtime.
  - [ ] 3.8 Run targeted non-network tests for command construction if available. If no such tests exist, add the smallest useful command-builder tests rather than relying on live OpenRouter runs.

- [ ] 4.0 Align production instructions and architecture documentation
  - [ ] 4.1 Update `SKILL.md` Step 3 command and explanation so it accurately states production `/lolla` runs through `ConversationContext` by default.
  - [ ] 4.2 Update `HOW_IT_WORKS.md` Step 3 command and "Conversation-first contract" section to remove any misleading implication that `--new-contract` is still required for production.
  - [ ] 4.3 Update `scripts/run_pipeline.py --help` text to present the default path and legacy escape hatch clearly.
  - [ ] 4.4 Update `research/conversation-first-runtime-default-decision-2026-04-24.md` with the final implementation summary and any deviations from the approved contract.
  - [ ] 4.5 Search for stale wording: `rg -n -- "--new-contract|new contract|legacy path|Default: off|Phase 1|Phase 2\\+" SKILL.md HOW_IT_WORKS.md scripts tests research tasks`.

- [ ] 5.0 Run verification and produce the runtime-switch acceptance artifact
  - [ ] 5.1 Run the new contract tests: `python3 -m pytest tests/test_run_pipeline_contract_default.py -q`.
  - [ ] 5.2 Run relevant existing tests: `python3 -m pytest tests/test_conversation_loader.py tests/test_pipeline_shim_equivalence.py tests/test_lane1_contextual.py tests/test_lane2_contextual.py tests/test_frame_pressure_contextual.py tests/test_structural_coverage_contextual.py -q`.
  - [ ] 5.3 Run the full test suite: `python3 -m pytest tests -q`.
  - [ ] 5.4 Run `python3 scripts/run_pipeline.py --help` and confirm the help text names the default and legacy escape hatch accurately.
  - [ ] 5.5 If API credentials and budget are available, run one production-path smoke on a small corpus case without `--new-contract`; otherwise record "not run: requires live OpenRouter" in the decision artifact.
  - [ ] 5.6 If API credentials and budget are available, run one explicit `--legacy-contract` smoke on the same small corpus case; otherwise record "not run: requires live OpenRouter" in the decision artifact.
  - [ ] 5.7 Update `research/conversation-first-runtime-default-decision-2026-04-24.md` with verification results, known residual risks, and rollback path.
  - [ ] 5.8 Stop for PM review before Phase 0.1 begins.

- [ ] 6.0 Complete Phase 0.1 Capture Fidelity Audit
  - [ ] 6.1 Read `SKILL.md` Step 1 capture instructions, `scripts/run_extract.py`, `engine/system_b/conversation_loader.py`, and the capture-related `run_health` logic in `scripts/run_pipeline.py`.
  - [ ] 6.2 Create `research/capture-fidelity-audit-2026-04-25.md`.
  - [ ] 6.3 Document exactly what the current capture path records: speaker labels, turn ids, user text, assistant prose, truncation markers, capture manifest fields, quote-validation fields, and health statuses.
  - [ ] 6.4 Document exactly what the current capture path drops or excludes: tool calls, tool outputs, system/developer messages, meta-conversation, omitted middle turns, and any other normalized content.
  - [ ] 6.5 Document what the capture path trusts implicitly: turn-boundary detection, speaker attribution, assistant/user alternation, declared vs parsed turn counts, truncation thresholds, and source text fidelity.
  - [ ] 6.6 Sample representative corpus cases and compare raw conversation files against loader output. Record any mismatches with concrete file references.
  - [ ] 6.7 Classify each observed or plausible failure mode as `blocker_for_ir_provenance`, `acceptable_with_flag`, or `fix_later`.
  - [ ] 6.8 If any blocker is found, stop and create a fix plan before Phase 0.5 starts.
  - [ ] 6.9 If no blockers are found, write a PM-review summary at the top of the audit with the minimum capture contract required for Phase 1 provenance.
  - [ ] 6.10 Stop for PM review before Phase 0.5 begins.

- [ ] 7.0 Complete Phase 0.5 External Systems Study and drill-back spike
  - [ ] 7.1 Create `research/phase0.5-adoption-memo-2026-04-XX.md` with sections for per-system summaries, pattern adoption/rejection, v1 IR impact, and the archaeology checklist response.
  - [ ] 7.2 Study the agreed systems: `GAIR-NLP/Context-Engineering-2.0`, `microsoft/graphrag`, `langchain-ai/langgraph`, `OpenHands/OpenHands`, `666ghj/MiroFish`, `humanlayer/12-factor-agents`, Anthropic/Letta/Manus context-engineering writeups, and Phoenix/OpenInference/Promptfoo tracing/eval patterns.
  - [ ] 7.3 For each system, write a 2-3 paragraph summary focused on state, provenance, compaction, memory/checkpointing, multi-view packet assembly, and observability.
  - [ ] 7.4 Fill an adoption/rejection table: pattern, source system, adopt/adapt/reject, reason, risk, and effect on Lolla's roadmap.
  - [ ] 7.5 Explicitly answer the five archaeology checklist claims from `research/legacy-pr-design-archaeology.md`: provenance-based identity, single-family `UserIssueEvent`, `StanceEvent` trajectory, packet-local `move_type`, and `ActorRef` deferral.
  - [ ] 7.6 Build a lightweight drill-back spike on one existing corpus case: packet -> prototype IR object -> source span -> raw turn.
  - [ ] 7.7 Save the drill-back output as `research/phase0.5-drillback-spike-2026-04-XX.md` or a similarly reviewable artifact.
  - [ ] 7.8 If the external study materially changes the v1 IR design, stop and update `plans/conversation-first-context-engineering-roadmap.md` plus `research/legacy-pr-design-archaeology.md` before Phase 1 planning.
  - [ ] 7.9 If the external study confirms the current direction, add a clear "Phase 1 may proceed" gate note to the memo.
  - [ ] 7.10 Stop for PM review before creating the Phase 1 IR task list.

- [ ] 8.0 Prepare Phase 1 IR kickoff task list after Phase 0.5 approval
  - [ ] 8.1 Confirm Phase 0.1 and Phase 0.5 artifacts are approved and no unresolved blockers remain.
  - [ ] 8.2 Create `tasks/tasks-conversation-first-phase-1-ir.md` using the gated-program template: structural artifact, behavioral metric, cost/latency budget, and kill criteria.
  - [ ] 8.3 Include task `0.0 Create feature branch` in the Phase 1 task list.
  - [ ] 8.4 Scope Phase 1 to the approved v1 IR objects only: `Turn`, `SpanRef`, `FrameAnchor`, `UserIssueEvent`, and `StanceEvent`.
  - [ ] 8.5 Explicitly mark `ActorRef`, `DecisionOption`, `ReasoningSegment`, and `CoverageTarget` as deferred/projection candidates unless Phase 0.5 changed that decision.
  - [ ] 8.6 Define Phase 1 TDD slices around public behavior: IR construction from current artifacts, provenance coverage, drill-back, and serialization.
  - [ ] 8.7 Stop after the Phase 1 task list is drafted. Do not implement Phase 1 IR until PM approval.

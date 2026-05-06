# Reasoning Substrate Enrichment Placement

## Relevant Files

- `research/reasoning-substrate-lane-placement-audit-2026-05-06.md` - PR25 placement audit for where a future packet producer should sit relative to existing lanes.
- `research/full-corpus-enrichment-coverage-audit-2026-05-06.md` - Deterministic full-corpus coverage audit across the 222-model runtime graph, v4 affordance records, source custody, and canonical source availability.
- `engine/system_b/reasoning_substrate_coverage.py` - Reusable deterministic coverage-audit module.
- `engine/system_b/reasoning_substrate_packet.py` - Dormant fixture/review-only packet producer for explicit candidate nominations.
- `tests/test_reasoning_substrate_coverage.py` - Focused tests for deterministic corpus coverage counts and expansion-priority signals.
- `tests/test_reasoning_substrate_packet.py` - Focused tests for the dormant packet producer.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap update for PR25 posture.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine update for PR25 posture.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Next-session handover update after PR25.

## Guardrails

- PR25 reopens forward work only along the corrected PR24 architecture.
- Do not create a new lane.
- Do not rewrite lane behavior.
- Do not wire live `/lolla`, prompts, Observatory, memo, Step 8, Step 6, or Lane 4 runtime.
- Do not run paid model calls or judges.
- Do not start Batch 3b or broad uncontrolled extraction.
- Do not build deterministic pressure selection or user-facing Decision Pressure output.
- Keep graph-only models eligible and honestly labeled.
- Keep v4 additive to lane-selected candidates, not a replacement for the 222-model graph.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Re-ground and branch setup
  - [x] 0.1 Read required PR24 doctrine/spec/audit/roadmap/schema docs in order.
  - [x] 0.2 Confirm local base is `feature/knowledge-substrate-pr11-gate4-edge-probes` with PR24 merged.
  - [x] 0.3 Create `feature/reasoning-substrate-pr25-enrichment-placement`.
  - [x] 0.4 Load TDD workflow because this slice adds code.

- [x] 1.0 Explore current lane outputs before coding
  - [x] 1.1 Locate Lane 1 output structures: `DeltaCard`, `DeltaFinding`, `TendencyRoute`, and audit routing decisions.
  - [x] 1.2 Locate Lane 2 output structures: `CompanionRunResult`, `DetectedModel`, `CompanionCheatSheet`, anchors, candidates, accepted/rejected/capped buckets.
  - [x] 1.3 Locate Lane 3 output structures: `FramePressureCard`, `FrameRoute`, `Reframing`.
  - [x] 1.4 Locate Lane 4 output structures: `StructuralCoverageCard`, `DimensionRoute`, `GapQuestion`.
  - [x] 1.5 Locate the existing safe serializer boundary: `engine/system_b/route_trace.py`.

- [x] 2.0 Create lane-to-packet placement audit
  - [x] 2.1 Document which lane outputs can nominate candidate shelves.
  - [x] 2.2 Document user/assistant/full-transaction evidence rules by lane.
  - [x] 2.3 Document the correct dormant insertion point and live paths to leave untouched.
  - [x] 2.4 Document missing provenance/model-ID cleanup needed later.

- [ ] 3.0 TDD deterministic full-corpus enrichment coverage audit
  - [x] 3.1 RED: add focused test for runtime/v4/source-custody counts.
  - [x] 3.2 GREEN: implement minimal coverage-audit module to pass counts test.
  - [x] 3.3 RED: add focused test for reasoning-type coverage gaps and graph-only eligibility.
  - [x] 3.4 GREEN: add reasoning-type and graph-field coverage calculations.
  - [x] 3.5 RED: add focused test for static lane-signal expansion priority.
  - [x] 3.6 GREEN: add static lane-signal and recommended batch calculations.
  - [x] 3.7 Generate `research/full-corpus-enrichment-coverage-audit-2026-05-06.md`.

- [x] 4.0 TDD dormant reasoning-substrate packet producer
  - [x] 4.1 RED: add focused test for v4-reviewed candidate enrichment.
  - [x] 4.2 GREEN: implement minimal explicit-nomination packet producer.
  - [x] 4.3 RED: add focused test for graph-only candidate eligibility.
  - [x] 4.4 GREEN: attach compact graph fields and honest graph-only coverage labels.
  - [x] 4.5 RED: add focused test for missing graph candidate suppression.
  - [x] 4.6 GREEN: suppress unresolved model IDs honestly without making cards.
  - [x] 4.7 RED: add focused tests for caps, provenance preservation, and forbidden fields.
  - [x] 4.8 GREEN: enforce caps, dedupe model IDs, preserve lane provenance, and keep runtime dormant.
  - [x] 4.9 RED/GREEN: add test proving live runtime path does not import the producer.

- [x] 5.0 Update living docs narrowly
  - [x] 5.1 Update roadmap current-state/posture for PR25.
  - [x] 5.2 Update knowledge-use schema current-state/posture for PR25.
  - [x] 5.3 Update next-session handover for PR25 continuation and decision label.

- [x] 6.0 Verify and hand off
  - [x] 6.1 Run focused new pytest tests.
  - [x] 6.2 Run decision-pressure trace regression tests.
  - [x] 6.3 Run `git diff --check`.
  - [x] 6.4 Run drift scan for posture contradictions.
  - [x] 6.5 Summarize files changed, tests passed, and blocked live surfaces.

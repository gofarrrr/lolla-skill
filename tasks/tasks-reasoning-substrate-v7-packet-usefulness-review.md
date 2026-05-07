## Relevant Files

- `tests/fixtures/reasoning_substrate_packet/pr35_v6_communication_competition_packet_review.json` - Baseline dormant packet fixture using v6, where PR34-upgraded models are still graph-only.
- `tests/fixtures/reasoning_substrate_packet/pr35_v7_communication_competition_packet_review.json` - Treatment dormant packet fixture using v7, where the same nominations receive reviewed affordance depth.
- `tests/test_reasoning_substrate_packet_v7_fixture.py` - Tests proving the PR35 fixtures match the explicit-nomination producer and remain non-runtime review artifacts.
- `research/reasoning-substrate-packet-pr35-v6-review-render-2026-05-07.md` - Reviewer-only Markdown rendering of the v6 baseline packet.
- `research/reasoning-substrate-packet-pr35-v7-review-render-2026-05-07.md` - Reviewer-only Markdown rendering of the v7 treatment packet.
- `research/reasoning-substrate-packet-pr35-v6-v7-comparison-render-2026-05-07.md` - Deterministic comparison render showing handoff-depth changes only.
- `research/reasoning-substrate-v7-packet-usefulness-review-2026-05-07.md` - Product/research readout on whether v7 improves handoff material.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap current-state update.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine current-state update.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Start-here handover update.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Doctrine status update.

### Notes

- This slice is fixture/render/review-only. It must not run live lanes, change prompts, call models, run judges, or produce user-facing output.
- The comparison asks whether v7 improves handoff material for a later LLM/reviewer. It does not choose final Decision Pressure.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout `feature/reasoning-substrate-pr35-v7-packet-usefulness-review`.
- [x] 1.0 Build PR35 fixture comparison
  - [x] 1.1 Define one explicit synthetic transaction that pulls PR34-upgraded communication/competition shelves.
  - [x] 1.2 Generate a v6 baseline packet from the same nominations.
  - [x] 1.3 Generate a v7 treatment packet from the same nominations.
  - [x] 1.4 Keep packet generation dormant and explicit-nomination only.
- [x] 2.0 Render reviewer-only inspection artifacts
  - [x] 2.1 Render the v6 baseline packet to Markdown.
  - [x] 2.2 Render the v7 treatment packet to Markdown.
  - [x] 2.3 Render a v6/v7 comparison focused on handoff usefulness only.
- [x] 3.0 Add tests for fixture and boundary rails
  - [x] 3.1 Assert checked-in fixtures match deterministic producer output.
  - [x] 3.2 Assert v6 graph-only cards become v7 reviewed cards without changing candidate count.
  - [x] 3.3 Assert v7 reviewed cards include activation, evidence, do-not-use, misuse, treatment, source-evidence, and absence fields.
  - [x] 3.4 Assert communication, competition, and analogy absences remain visible.
  - [x] 3.5 Assert renders match the deterministic renderer.
  - [x] 3.6 Assert no final pressure, user-facing prose, HTML, or live runtime import is created.
- [x] 4.0 Write review artifact and living-doc updates
  - [x] 4.1 Write the PR35 usefulness review.
  - [x] 4.2 Update roadmap/schema/doctrine/handover current state.
- [x] 5.0 Verify
  - [x] 5.1 Run PR35 fixture tests.
  - [x] 5.2 Run packet/render regression tests.
  - [x] 5.3 Run source custody/coverage checks.
  - [x] 5.4 Run PR34 batch record checks.
  - [x] 5.5 Run whitespace and status checks.

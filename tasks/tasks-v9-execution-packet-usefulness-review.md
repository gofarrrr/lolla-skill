# V9 Execution Packet Usefulness Review

## Relevant Files

- `research/pr39-controlled-execution-followthrough-enrichment-report-2026-05-07.md` - PR39 extraction report that left the v9 packet usefulness question open.
- `engine/system_b/reasoning_substrate_packet.py` - Dormant explicit-nomination packet producer used to regenerate the v8/v9 packets.
- `engine/system_b/reasoning_substrate_packet_review.py` - Reviewer-only Markdown renderer used for packet review and comparison.
- `tests/fixtures/reasoning_substrate_packet/pr40_v8_execution_followthrough_packet_review.json` - v8 baseline packet fixture with the PR39 target models still graph-only.
- `tests/fixtures/reasoning_substrate_packet/pr40_v9_execution_followthrough_packet_review.json` - v9 treatment packet fixture with PR39 reviewed depth.
- `research/reasoning-substrate-packet-pr40-v8-review-render-2026-05-07.md` - Reviewer-only render of the v8 baseline packet.
- `research/reasoning-substrate-packet-pr40-v9-review-render-2026-05-07.md` - Reviewer-only render of the v9 treatment packet.
- `research/reasoning-substrate-packet-pr40-v8-v9-comparison-render-2026-05-07.md` - Reviewer-only comparison render.
- `tests/test_reasoning_substrate_packet_v9_fixture.py` - PR40 fixture, render, comparison, and non-promotion tests.
- `research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md` - PR40 usefulness review.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR40.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR40.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR40.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR40.

## Guardrails

- PR40 is a dormant packet usefulness review, not extraction.
- Hold nominations stable between v8 and v9.
- Do not answer the synthetic case.
- Do not choose final Decision Pressure.
- Do not create user-facing copy.
- Do not run live lanes.
- Do not promote v9 into runtime.
- Do not change prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, judges, or Batch 3b.
- Do not make Python choose final pressure or wisdom.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 0.0 Branch setup and grounding
  - [x] 0.1 Start from `feature/knowledge-substrate-pr11-gate4-edge-probes`.
  - [x] 0.2 Create `feature/reasoning-substrate-pr40-v9-execution-packet-usefulness-review`.
  - [x] 0.3 Read PR39 report, existing PR37 packet usefulness pattern, packet producer, and packet renderer.

- [x] 1.0 RED: add PR40 packet fixture tests
  - [x] 1.1 Test v8 and v9 fixtures match the dormant explicit-nomination producer.
  - [x] 1.2 Test the same nominations are held stable and candidate count stays fixed.
  - [x] 1.3 Test v8 has 12 graph-only cards and v9 has no graph-only cards.
  - [x] 1.4 Test v9 preserves 11 reviewed cards and 1 weak/conflicting support card.
  - [x] 1.5 Test reviewed execution-depth fields and absence signals are present.
  - [x] 1.6 Test reviewer-only renders match the deterministic renderer.
  - [x] 1.7 Test the comparison render checks handoff delta, not final answer quality.
  - [x] 1.8 Test no final user-facing surface or live runtime import appears.

- [x] 2.0 Generate fixtures and renders
  - [x] 2.1 Generate `pr40_v8_execution_followthrough_packet_review.json`.
  - [x] 2.2 Generate `pr40_v9_execution_followthrough_packet_review.json`.
  - [x] 2.3 Generate v8 review render.
  - [x] 2.4 Generate v9 review render.
  - [x] 2.5 Generate v8/v9 comparison render.

- [x] 3.0 Review packet usefulness
  - [x] 3.1 Compare v8 and v9 packet shape.
  - [x] 3.2 Review card-level handoff changes.
  - [x] 3.3 Preserve the DevOps/CI weak-support caveat.
  - [x] 3.4 Write `research/reasoning-substrate-v9-packet-usefulness-review-2026-05-07.md`.
  - [x] 3.5 Recommend whether PR41 should extract, audit, compare, or pause.

- [x] 4.0 Update living docs narrowly
  - [x] 4.1 Update next-session handover.
  - [x] 4.2 Update knowledge-substrate roadmap.
  - [x] 4.3 Update knowledge-use schema.
  - [x] 4.4 Update decision-pressure product doctrine.

- [x] 5.0 Verify and hand off
  - [x] 5.1 Run `PYTHONPATH=. pytest tests/test_reasoning_substrate_packet_v9_fixture.py`.
  - [x] 5.2 Run packet/render regression tests.
  - [x] 5.3 Run PR39 batch tests.
  - [x] 5.4 Run source-custody/coverage tests.
  - [x] 5.5 Run decision-pressure trace regression tests.
  - [x] 5.6 Run `git diff --check`.
  - [x] 5.7 Run changed-path guardrail checks.
  - [x] 5.8 Open PR and summarize packet deltas, verdict, tests, and PR41 recommendation.

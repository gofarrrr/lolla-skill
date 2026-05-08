# V11 Frame-Correction Packet Usefulness Review

## Relevant Files

- `research/pr45-controlled-frame-correction-enrichment-report-2026-05-07.md` - PR45 controlled extraction report and v11 corpus shape.
- `data/compiled/model_affordances/affordances_v10.json` - Baseline reviewed corpus before PR45.
- `data/compiled/model_affordances/affordances_v11.json` - Draft/review-only v11 corpus after PR45.
- `engine/system_b/reasoning_substrate_packet.py` - Dormant explicit-nomination packet producer.
- `engine/system_b/reasoning_substrate_packet_review.py` - Reviewer-only packet renderer.
- `tests/fixtures/reasoning_substrate_packet/pr46_v10_frame_correction_packet_review.json` - Baseline same-nomination packet.
- `tests/fixtures/reasoning_substrate_packet/pr46_v11_frame_correction_packet_review.json` - Treatment same-nomination packet.
- `research/reasoning-substrate-packet-pr46-v10-review-render-2026-05-07.md` - Baseline render.
- `research/reasoning-substrate-packet-pr46-v11-review-render-2026-05-07.md` - Treatment render.
- `research/reasoning-substrate-packet-pr46-v10-v11-comparison-render-2026-05-07.md` - Deterministic comparison render.
- `research/reasoning-substrate-v11-packet-usefulness-review-2026-05-07.md` - PR46 review artifact.
- `tests/test_reasoning_substrate_packet_v11_fixture.py` - Fixture and render regression tests.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Handover update for PR46.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Roadmap update for PR46.
- `plans/knowledge-use-schema-2026-05-04.md` - Schema doctrine update for PR46.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine update for PR46.
- `research/knowledge-matching-current-state-audit-2026-05-06.md` - Current-state posture update after PR46.

## Guardrails

- PR46 is a review-only packet usefulness slice, not extraction.
- Do not edit affordance records.
- Do not compile v12.
- Do not promote v11 into runtime.
- Do not run live `/lolla`, prompts, lanes, live adapter, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, or judges.
- Do not create user-facing Decision Pressure output.
- Do not make Python choose final pressure or final reasoning mode.
- Treat `reasoning-mode-router` as reviewed handoff material only, not deterministic routing.

## Instructions For Completing Tasks

Change `- [ ]` to `- [x]` as each sub-task is completed.

## Tasks

- [x] 1.0 Branch setup and grounding
  - [x] 1.1 Review and merge PR45 before starting PR46.
  - [x] 1.2 Fast-forward `feature/knowledge-substrate-pr11-gate4-edge-probes` after PR45 merge.
  - [x] 1.3 Create `feature/reasoning-substrate-pr46-v11-frame-packet-usefulness-review`.
  - [x] 1.4 Read PR40/PR43 packet usefulness test patterns and PR45 report.

- [x] 2.0 Add same-nomination packet fixture tests
  - [x] 2.1 Add `tests/test_reasoning_substrate_packet_v11_fixture.py`.
  - [x] 2.2 Assert v10 and v11 fixtures match dormant producer output.
  - [x] 2.3 Assert candidate count and duplicate suppression stay stable.
  - [x] 2.4 Assert v10 has graph-only frame-correction cards and v11 has reviewed cards.
  - [x] 2.5 Assert v11 reviewed cards preserve source custody, reviewed snippets, and absence signals.
  - [x] 2.6 Assert no final pressure, user-facing prose, memo copy, rendered HTML, runtime import, or deterministic routing surface appears.

- [x] 3.0 Generate review-only fixtures and renders
  - [x] 3.1 Generate `pr46_v10_frame_correction_packet_review.json` from the dormant packet producer.
  - [x] 3.2 Generate `pr46_v11_frame_correction_packet_review.json` from the dormant packet producer.
  - [x] 3.3 Generate v10 and v11 reviewer-only renders.
  - [x] 3.4 Generate deterministic v10/v11 comparison render.
  - [x] 3.5 Verify generated artifacts pass the new fixture tests.

- [x] 4.0 Write PR46 review artifact
  - [x] 4.1 Add `research/reasoning-substrate-v11-packet-usefulness-review-2026-05-07.md`.
  - [x] 4.2 Compare candidate counts, reviewed card counts, graph-only counts, absence signals, and packet burden.
  - [x] 4.3 Review activation, evidence-needed, do-not-use, misuse, treatment, and absence/overclaim protection.
  - [x] 4.4 Record risk that frame-correction cards can become internal vocabulary or deterministic routing if misused.
  - [x] 4.5 Recommend an after-v11 graph-only priority audit before any further extraction.

- [x] 5.0 Update living docs narrowly
  - [x] 5.1 Update next-session handover current posture and PR46 references.
  - [x] 5.2 Update roadmap current posture and PR46 references.
  - [x] 5.3 Update schema doctrine current posture and PR46 references.
  - [x] 5.4 Update product doctrine current posture and PR46 references.
  - [x] 5.5 Update current-state audit posture.

- [x] 6.0 Verify and hand off
  - [x] 6.1 Run focused PR46 fixture tests.
  - [x] 6.2 Run packet/render regression tests through v11.
  - [x] 6.3 Run PR45 batch and source custody/coverage tests.
  - [x] 6.4 Run Decision Pressure trace regression tests.
  - [x] 6.5 Run `git diff --check` and changed-path guardrails.
  - [x] 6.6 Run drift scan over PR45/PR46/PR47/posture language.
  - [x] 6.7 Open PR and summarize review result, guardrails, and tests.

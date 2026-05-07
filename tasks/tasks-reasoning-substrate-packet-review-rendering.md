## Relevant Files

- `engine/system_b/reasoning_substrate_packet_review.py` - Review-only Markdown renderer for dormant reasoning substrate packet fixtures and packet comparisons.
- `tests/test_reasoning_substrate_packet_review_render.py` - Behavior tests for renderer output, checked-in renders, runtime dormancy, and live-runtime non-import guardrails.
- `research/reasoning-substrate-packet-review-rendering-2026-05-07.md` - PR30 review report and renderer boundary record.
- `research/reasoning-substrate-packet-pr27-review-render-2026-05-07.md` - Deterministic compact render of the PR27 mixed packet fixture.
- `research/reasoning-substrate-packet-pr29-review-render-2026-05-07.md` - Deterministic compact render of the PR29 v5 packet fixture.
- `research/reasoning-substrate-packet-comparison-render-2026-05-07.md` - Deterministic compact before/after render comparing PR27 and PR29 packet handoff shape.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Current-session handover updated with the PR30 posture and next-step boundary.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap updated to place PR30 as receiver-review ergonomics only.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine updated with the PR30 rendering boundary.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine updated so PR30 is not misread as runtime/product promotion.

### Notes

- Renderer tests exercise the public renderer interface through real PR27/PR29 fixtures.
- The checked-in Markdown renders are generated from the deterministic renderer and asserted by tests.
- Use `PYTHONPATH=. pytest tests/test_reasoning_substrate_packet_review_render.py` for the focused renderer rail.
- PR30 is no-model and review-only. It must not add runtime imports, live lane adapters, prompt changes, extraction, UI, memo copy, HTML, user-facing output, or deterministic pressure selection.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout `feature/reasoning-substrate-pr30-packet-review-rendering`
- [x] 1.0 Define the receiver-review rendering boundary
  - [x] 1.1 Confirm PR30 is a no-model, no-runtime reviewer ergonomics slice.
  - [x] 1.2 Confirm the renderer should inspect packet handoff quality, not answer the user case or choose final output.
  - [x] 1.3 Confirm rendered Markdown is review infrastructure, not UI, memo, Observatory, or user-facing copy.
- [x] 2.0 Add test-first renderer behavior
  - [x] 2.1 Add a test proving the PR29 v5 packet renders as compact reviewer-only Markdown.
  - [x] 2.2 Add a test proving PR27 graph-only cards remain honestly labeled.
  - [x] 2.3 Add a test proving PR27 vs PR29 comparison shows depth deltas without final selection.
  - [x] 2.4 Add a test proving non-dormant packets are rejected.
  - [x] 2.5 Add a test proving the renderer is not imported by live runtime paths.
- [x] 3.0 Implement the compact renderer
  - [x] 3.1 Add `render_reasoning_substrate_packet_review_markdown`.
  - [x] 3.2 Add `render_reasoning_substrate_packet_comparison_markdown`.
  - [x] 3.3 Render packet identity, counts, coverage, provenance, source custody, compact signals, suppressed candidates, and blocked surfaces.
  - [x] 3.4 Keep output free of final pressure fields, memo copy, HTML, user-facing prose, and semantic ranking.
- [x] 4.0 Check in deterministic review artifacts
  - [x] 4.1 Generate compact Markdown render of the PR27 packet.
  - [x] 4.2 Generate compact Markdown render of the PR29 packet.
  - [x] 4.3 Generate compact Markdown comparison of PR27 vs PR29.
  - [x] 4.4 Add a test proving checked-in render artifacts match deterministic renderer output.
- [x] 5.0 Update doctrine and handoff docs
  - [x] 5.1 Add PR30 review report.
  - [x] 5.2 Update next-session handover with `packet_review_rendering_ready`.
  - [x] 5.3 Update roadmap and schema docs with the PR30 boundary.
  - [x] 5.4 Update product doctrine so PR30 cannot be misread as product promotion.
- [x] 6.0 Verify and prepare handoff
  - [x] 6.1 Run focused renderer tests.
  - [x] 6.2 Run existing packet/source-custody/Decision Pressure rails.
  - [x] 6.3 Run `git diff --check`.
  - [x] 6.4 Confirm no runtime, prompt, lane, extraction, model-call, judge, UI, memo, or user-facing files were changed.

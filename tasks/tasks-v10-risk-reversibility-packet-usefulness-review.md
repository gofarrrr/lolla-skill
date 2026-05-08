## Relevant Files

- `tests/fixtures/reasoning_substrate_packet/pr43_v9_risk_reversibility_packet_review.json` - v9 baseline packet fixture where the PR42 models are graph-only.
- `tests/fixtures/reasoning_substrate_packet/pr43_v10_risk_reversibility_packet_review.json` - v10 treatment packet fixture where the same PR42 models have reviewed depth.
- `tests/test_reasoning_substrate_packet_v10_fixture.py` - Tests proving the fixtures match the dormant producer, preserve stable nominations, and avoid runtime/product output.
- `research/reasoning-substrate-packet-pr43-v9-review-render-2026-05-07.md` - Reviewer-only Markdown render of the v9 baseline packet.
- `research/reasoning-substrate-packet-pr43-v10-review-render-2026-05-07.md` - Reviewer-only Markdown render of the v10 treatment packet.
- `research/reasoning-substrate-packet-pr43-v9-v10-comparison-render-2026-05-07.md` - Reviewer-only comparison render for handoff-quality review.
- `research/reasoning-substrate-v10-packet-usefulness-review-2026-05-07.md` - PR43 review verdict and recommendation.
- `research/reasoning-substrate-next-session-handover-2026-05-06.md` - Start-here handover for future sessions; must point to the current PR43 posture.
- `plans/knowledge-substrate-roadmap-2026-05-04.md` - Living roadmap; must record PR43 as packet usefulness evidence, not runtime permission.
- `plans/knowledge-use-schema-2026-05-04.md` - Living schema doctrine; must keep the packet/enrichment boundary current.
- `research/decision-pressure-product-doctrine-2026-05-06.md` - Product doctrine; must preserve the broad-intake, disciplined-output and Python-does-not-decide-wisdom boundary.

### Notes

- This slice is a fixture/render/review proof, not extraction.
- Do not change prompts, lanes, `/lolla`, Observatory, memo, Step 8, Step 6, Lane 4 runtime, model calls, judges, or Batch 3b.
- Keep the same PR42 nominations across v9 and v10.
- Judge handoff quality only: activation, evidence, dismissal, misuse, treatment, absence, and burden.
- Do not answer the synthetic user case or select final Decision Pressure.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` -> `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout `feature/reasoning-substrate-pr43-v10-risk-packet-usefulness-review`
- [x] 1.0 Build stable v9/v10 packet fixtures
  - [x] 1.1 Define one synthetic risk/reversibility transaction context
  - [x] 1.2 Nominate the same 12 PR42 models plus one duplicate suppression check
  - [x] 1.3 Generate the v9 baseline fixture against `affordances_v9.json`
  - [x] 1.4 Generate the v10 treatment fixture against `affordances_v10.json`
- [x] 2.0 Render review-only packet views
  - [x] 2.1 Render the v9 packet with the deterministic reviewer renderer
  - [x] 2.2 Render the v10 packet with the deterministic reviewer renderer
  - [x] 2.3 Render the v9/v10 comparison with the deterministic comparison renderer
- [x] 3.0 Add fixture and boundary tests
  - [x] 3.1 Assert fixtures match dormant explicit-nomination producer output
  - [x] 3.2 Assert candidate count and suppressed duplicate count remain fixed
  - [x] 3.3 Assert v10 upgrades the PR42 cards from graph-only to reviewed without weak/conflicting support
  - [x] 3.4 Assert reviewed depth and absence signals are present
  - [x] 3.5 Assert renders match deterministic renderer output
  - [x] 3.6 Assert comparison render reviews handoff delta only, not final answer
  - [x] 3.7 Assert no live runtime imports or product-surface fields are introduced
- [x] 4.0 Write the PR43 review artifact
  - [x] 4.1 Compare v9 baseline and v10 treatment packet shape
  - [x] 4.2 Record which cards gained useful handoff depth
  - [x] 4.3 Record packet burden and remaining cautions
  - [x] 4.4 Record decision label `v10_risk_packet_handoff_useful`
  - [x] 4.5 Recommend after-v10 graph-only priority audit before further extraction
- [x] 5.0 Update living docs
  - [x] 5.1 Update the roadmap current posture and PR43 references
  - [x] 5.2 Update the schema doctrine current posture and PR43 references
  - [x] 5.3 Update the product doctrine current posture and PR43 references
  - [x] 5.4 Update the matching current-state audit posture
  - [x] 5.5 Update the next-session handover current posture, read list, and kickoff prompt
- [x] 6.0 Verify the slice
  - [x] 6.1 Run PR43 fixture tests
  - [x] 6.2 Run packet fixture/render regression tests
  - [x] 6.3 Run source-custody/coverage tests
  - [x] 6.4 Run decision-pressure trace tests
  - [x] 6.5 Run whitespace checks
  - [x] 6.6 Run drift scan over current-state docs
  - [x] 6.7 Confirm no extraction, runtime, prompt, lane, model-call, judge, UI, or user-facing changes

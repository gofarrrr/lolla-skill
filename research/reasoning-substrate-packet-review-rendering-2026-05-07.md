# Reasoning Substrate Packet Review Rendering

**Date:** 2026-05-07
**PR slice:** PR30 - compact receiver-review rendering
**Status:** review-only renderer and checked-in Markdown renders; no model
calls, runtime, prompt, lane, extraction, UI, memo, Observatory, Step 8, Step 6,
Lane 4, or user-facing surface
**Decision label:** `packet_review_rendering_ready`

## Purpose

PR29 showed that the v5 packet gives better handoff material than the PR27
packet, but both packets are raw JSON. Raw JSON is inspectable by a developer,
but it is not a good receiver-review object. It makes the reviewer spend effort
parsing structure before judging the real question:

> Does the later packet help a reasoning actor use, merge, ignore, or set aside
> candidate shelves more cleanly?

PR30 adds a compact deterministic Markdown renderer for that review step.

It does not test final-answer quality. It does not pick Decision Pressure. It
does not create product copy. It simply makes the existing dormant packet
evidence easier to inspect before any external reviewer/LLM pass or further
extraction.

## Files Added

- `engine/system_b/reasoning_substrate_packet_review.py`
- `tests/test_reasoning_substrate_packet_review_render.py`
- `research/reasoning-substrate-packet-pr27-review-render-2026-05-07.md`
- `research/reasoning-substrate-packet-pr29-review-render-2026-05-07.md`
- `research/reasoning-substrate-packet-comparison-render-2026-05-07.md`

## Renderer Contract

The renderer may show:

- packet identity;
- status and runtime policy;
- source artifacts;
- packet counts;
- candidate model IDs;
- coverage labels;
- lane/source provenance;
- source custody;
- compact graph-only recall material;
- compact reviewed affordance signals;
- absence-record identifiers;
- suppressed candidates;
- blocked surfaces;
- before/after coverage changes.

The renderer must not show or create:

- final Decision Pressure;
- user-facing prose;
- memo copy;
- HTML;
- product UI;
- semantic ranking;
- final answer quality;
- deterministic pressure selection.

The renderer rejects packets whose status or runtime policy is not
`draft_review_only` / `runtime_dormant`.

## Rendered Artifacts

PR30 checks in three generated reviewer-only Markdown artifacts:

1. `research/reasoning-substrate-packet-pr27-review-render-2026-05-07.md`
   - compact rendering of the PR27 mixed v4 + graph-only packet;
   - shows `3` reviewed cards, `4` graph-only cards, and `1` suppressed
     duplicate;
   - keeps graph-only cards honest by showing them as recall material, not
     reviewed affordance depth.

2. `research/reasoning-substrate-packet-pr29-review-render-2026-05-07.md`
   - compact rendering of the PR29 v5 packet;
   - shows `7` reviewed cards, `0` graph-only cards, and `1` suppressed
     duplicate;
   - exposes reviewed activation, evidence, do-not-use, misuse, treatment, and
     absence signals without choosing the conclusion.

3. `research/reasoning-substrate-packet-comparison-render-2026-05-07.md`
   - diff-oriented comparison of PR27 and PR29;
   - shows reviewed cards `3 -> 7`, graph-only cards `4 -> 0`, and the four
     upgraded model IDs;
   - includes a reviewer rubric for handoff usefulness only.

## Product Read

PR30 is useful because it answers a smaller question than PR31 would:

> Can we inspect packet handoff quality without reading raw JSON and without
> turning the packet into product output?

The answer is yes.

That makes a future receiver-side review cleaner. A reviewer or explicitly
approved LLM can now compare the PR27 and PR29 packets using compact renders,
while still being instructed not to answer the user case or choose
user-visible output.

## What This Does Not Prove

PR30 does not prove:

- a receiver-side LLM will use v5 depth well;
- the final answer improves;
- the product is runtime-ready;
- more extraction is justified;
- packet rendering should become UI;
- Decision Pressure should be promoted.

It only proves the packet evidence can be rendered for review without breaking
the deterministic boundary.

## Next Recommended Slice

The next useful slice is receiver-side review using the PR30 renders.

If model/reviewer calls are explicitly approved, run a narrow review:

> Compare the PR27 and PR29 renders as handoff material only. Do not answer the
> case. Do not choose final output. Assess whether v5 depth improves activation,
> evidence, do-not-use, misuse, treatment, absence, and burden.

If model calls are not approved, pause for product review. Do not compensate by
adding more renderer machinery or another extraction batch.

## Guardrails Preserved

PR30 adds no:

- live `/lolla`;
- prompt changes;
- lane rewrites;
- runtime packet production from live lanes;
- live route-trace adapter;
- extraction;
- Batch 3b;
- model calls;
- judges;
- Observatory, memo, Step 8, Step 6, or Lane 4 runtime wiring;
- user-facing Decision Pressure output;
- deterministic final pressure selection.

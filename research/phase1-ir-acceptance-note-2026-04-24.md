# Phase 1 IR Acceptance Note

**Date:** 2026-04-24
**Branch:** `feat/conversation-first-phase-1-ir`
**Scope:** provenance-bearing `ConversationIR` added alongside `ConversationContext`.

## Decision

Phase 1 implementation satisfies the approved shape: the repo now has a narrow, provenance-bearing IR with reducer-style builders, a deterministic constructor from existing `ConversationContext` artifacts, drill-back primitives, and INFO-level provenance-tier observability.

No lane behavior, prompt, routing, extraction, or normal output serialization was intentionally changed. The pipeline constructs IR only when `SystemBPipeline.run()` receives a `ConversationContext`; the legacy `CritiqueRequest` path does not construct IR.

## Implemented Shape

- `engine/system_b/ir.py`: immutable IR dataclasses, provenance union, serialization round-trip helpers, span/turn resolution, and drill-back resolver.
- `engine/system_b/ir_builders.py`: reducer-style pure updates (`add_turn`, `add_span`, `add_frame_anchor`, `add_user_issue_event`, `supersede_issue`, `add_stance_event`).
- `engine/system_b/ir_constructor.py`: deterministic `ConversationContext -> ConversationIR` constructor.
- `tests/test_ir.py`: IR shape, reducer, constructor, serialization, provenance honesty, latency, and observability tests.
- `tests/test_ir_drillback.py`: packet-like source ref -> IR object -> provenance -> source text drill-back tests.
- `tests/test_pipeline_shim_equivalence.py`: pipeline integration tests proving IR construction is context-only and lane dispatch remains stable.

## Provenance Coverage

Current extraction-derived fields are summaries/paraphrases, so constructor output uses `turn_ref` provenance rather than fake exact spans. Exact `span` provenance remains implemented and tested for manually exact references and future packet builders.

Observed provenance-tier distribution across the 3 fixture cases:

| Case | Turns | UserIssueEvents | FrameAnchors | StanceEvents | span | turn_ref | derivation | Constructor latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `user_has_plan` | 16 | 5 | 1 | 0 | 0 | 6 | 0 | 0.327ms |
| `whistleblower` | 28 | 6 | 1 | 0 | 0 | 7 | 0 | 0.493ms |
| `parenting_teen` | 24 | 4 | 1 | 0 | 0 | 5 | 0 | 0.258ms |

All derived IR objects in these fixtures have non-empty provenance.

## Drill-Back

The drill-back resolver accepts packet-like source refs such as:

```python
{"object_type": "frame_anchor", "object_id": "frame_001"}
```

It resolves in <=3 logical hops:

1. source ref -> IR object
2. IR object -> provenance tier
3. provenance -> exact span text or full source turn(s)

Exact-span provenance returns the substring plus `SpanRef`. Turn-ref provenance returns the full source turn and leaves `exact_text=None`. Derivation provenance returns lineage refs without pretending there is one source span.

## Annotation Gate

Task 7.0 was not rerun during implementation. The pre-implementation annotation gate is preserved in `research/phase1-useriussevent-annotation-exercise-2026-04-24.md`:

- Agreement: 16.0 / 17
- Rate: 94.1%
- Outcome: PASS
- Refinement implemented: `UserIssueEvent.kind_ambiguity: bool = False`

The implementation keeps the v1 kind taxonomy narrow: `constraint`, `concern`, `open_loop`. `kind_ambiguity` is informational only and does not introduce a fourth kind or confidence score.

## Latency

`user_has_plan` constructor latency was measured at 0.327ms, well below the approved <50ms budget.

## Verification

Recorded after implementation:

- IR/drill-back local tests: `21 passed`
- Pipeline/context integration subset: `55 passed`
- Full suite: `278 passed, 1 warning, 93 subtests passed in 12.70s`

No live API calls were required.

## Residual Risks

- The constructor is intentionally conservative. Current extraction-derived objects are mostly `turn_ref`; future packet builders or specialist extraction passes must supply exact quotes before `span` provenance becomes common.
- `kind_ambiguity` uses conservative marker logic for current artifacts. If later extraction surfaces new ambiguous active issues, the annotation gate should be reopened rather than broadening kind semantics silently.
- Normal output serialization does not include a full IR dump. This avoids schema churn now, but Phase 4 packet tooling will need an explicit debug surface for packet -> IR -> transcript review.

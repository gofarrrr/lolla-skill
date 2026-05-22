# Pre-Step-6 Raw Artifact Render/Validation Slice

Date: 2026-05-16

Status: research-only implementation slice. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane
1, V60, the canonical knowledge base, or public output.

Related:

```text
research/pre-step6-raw-artifact-consumption-discipline-2026-05-16.md
research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md
research/pre-step6-raw-artifact-four-fixture-render-readout-2026-05-16.md
research/pre-step6-raw-artifact-answer-consumption-readout-2026-05-16.md
research/pre-step6-comparison-fixtures/mother-deciding-address-year-20260430T113301Z.md
```

## What Landed

This slice turns the raw-artifact discipline into a tiny dormant harness:

```text
scripts/research/pre_step6_raw_artifacts.py
tests/test_pre_step6_raw_artifacts.py
research/pre-step6-raw-artifact-fixtures/mother-address-year.raw-artifact-handoff.v1.json
```

It validates and renders a small private raw `reasoning_artifact.v1` handoff.
It does not launch workers, build a bundle, decide truth, or connect to live
`/lolla`.

2026-05-16 continuation: the same JSON handoff shape now exists for all four
comparison fixtures:

```text
research/pre-step6-raw-artifact-fixtures/third-year-phd-student.raw-artifact-handoff.v1.json
research/pre-step6-raw-artifact-fixtures/founder-grant-marcus-equity.raw-artifact-handoff.v1.json
research/pre-step6-raw-artifact-fixtures/mid-level-consultant-report-2.raw-artifact-handoff.v1.json
research/pre-step6-raw-artifact-fixtures/mother-address-year.raw-artifact-handoff.v1.json
```

All four validate and render under the 4,000-character private cap.

## Contract

The handoff payload is:

```text
pre_step6_raw_artifact_handoff.v1
status: research_only
runtime_policy: runtime_dormant
```

Each artifact must include:

```text
schema_version
artifact_id
why_provided
source_grounding
contribution
hard_boundary
relaxation_condition
discard_condition
priority_hint
risk_if_forced
risk_if_ignored
```

The harness enforces:

```text
max artifacts: 5
max source excerpts: 4
source_excerpt_ids reference known excerpts
worker admission decision is explicit
rendered private handoff stays under 4,000 chars
public answer hygiene rejects machinery terms
```

## Render Shape

The renderer keeps the Step 6 reading order from the discipline doc:

```text
Grounding
Boundary
Relax if
Discard if
Contribution
Force risk
Ignore risk
Priority hint
```

It intentionally omits `why_provided` from the rendered block unless a later
consumer proves admission context is needed.

## Fixture Result

The first JSON fixture was the mother address no-worker sentinel.

Expected outcome:

```text
validate raw artifacts
render private pressure under cap
decline worker
preserve instrument-trust warning
preserve tripwire sizing
keep base-rate pressure quiet
discard power-dynamics lens
```

The four-fixture continuation adds PhD, founder, and consultant raw handoffs.
This is still a harness result, not final-answer evidence.

## Still Not Authorized

Do not treat this slice as approval for:

```text
reasoning_bundle.v1 runtime machinery
reasoning_workpack.v1 builder
worker prompt builders
subagent orchestration
OpenRouter synthesis
product docs
default /lolla behavior
```

## Next Question

2026-05-16 follow-up: authored answer cores now consume all four raw renders
without machinery leakage. The next useful research check is less-author-biased
comparison against current-control answer cores. If raw cores stay sharp, raw
artifacts remain the preferred path. If a case loses because the raw render is
too cluttered, an indexed bundle challenger gets a narrow reason to re-enter
the queue.

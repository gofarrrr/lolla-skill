# Pre-Step-6 Compact JSON Replay Readout

Date: 2026-05-16

Status: research-only replay readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-strict-json-subagent-replay-readout-2026-05-16.md
research/pre-step6-strict-worker-output-contract-readout-2026-05-16.md
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

Can a compact JSON skeleton get native subagent worker outputs under the
1,500-character cap without losing the useful boundary/evidence-gate lift?

## Setup

The renderer was tightened to show a compact JSON skeleton:

```json
{
  "schema_version": "reasoning_artifact.v1",
  "why_provided": "<=120 chars",
  "source_grounding": ["<=180 chars each, max 3"],
  "contribution": ["<=180 chars each, max 3"],
  "hard_boundary": "<=240 chars",
  "relaxation_condition": "<=160 chars",
  "discard_condition": "<=160 chars",
  "relation_to_bundle": "<=140 chars",
  "priority_hint": "high|medium|low|quiet|discard",
  "risk_if_forced": "<=140 chars",
  "risk_if_ignored": "<=140 chars"
}
```

It also states:

```text
arrays must have at most 3 items
array items must be at most 180 chars
no nested objects
```

Only two cases were replayed:

```text
third-year-phd-student
mid-level-consultant-report-2
```

Founder was skipped because the goal was to test whether the compact skeleton
can hit cap at all before spending another worker run.

## Results

| Case | JSON Syntax | Content Lift | Previous Strict Size | Compact Size | Cap |
| --- | --- | --- | --- | --- | --- |
| Third-year PhD student | Pass | Fallback executability + Silva/data gates preserved | 3,091 chars | 1,769 chars | Fail |
| Mid-level consultant report | Pass | Counsel/channel/Wednesday guardrails preserved | 3,134 chars | 2,068 chars | Fail |

Aggregate:

```text
compact workers run: 2
valid JSON syntax: 2/2
content preserved: 2/2
under 1,500-char cap: 0/2
runtime promotion authorized: no
```

## Interpretation

The compact skeleton helped substantially:

```text
PhD: 3,091 -> 1,769 chars
consultant: 3,134 -> 2,068 chars
```

But it did not solve compression. The workers still used the available structure
to carry too much useful detail.

This is the first point where the result is not just "tighten the prompt." We
have learned:

```text
native subagents can produce useful pressure
admission can protect the no-worker sentinel
strict JSON can produce machine-readable outputs
compact skeletons reduce length
but worker self-compression to 1,500 chars is unreliable
```

The bottleneck has moved from cognition to compression governance.

## Decision

```text
compact_json_prompt_improves_size_but_fails_cap
do_not_rerun_more_workers_until_compression_strategy_changes
do_not_build_runtime_worker_ingestion
do_not_build_reasoning_bundle
```

## Options From Here

Option A: relax the cap.

```text
Set worker output cap around 2,200-2,500 chars.
Pros: native worker artifacts already land near useful shape.
Cons: Step 6 receives more private text; system may become another clutter path.
```

Option B: add deterministic post-compression.

```text
Let worker produce 2,000-3,000 chars, then run a deterministic/LLM compressor
into strict reasoning_artifact.v1.
Pros: keeps worker reasoning rich while enforcing final cap.
Cons: adds another stage and another possible distortion point.
```

Option C: split artifact shape.

```text
Use a richer internal worker draft plus a compact Step-6 card.
Pros: preserves audit detail while feeding Step 6 a small card.
Cons: more schema complexity and more research harness surface.
```

Option D: keep workers manual research-only.

```text
Use native subagents for exploration, but do not build automated worker
ingestion yet.
Pros: safest and simplest.
Cons: does not solve production Step-6 pressure quality.
```

## Recommendation

Do not relax the cap yet.

The next research move should be a tiny producer/compressor test:

```text
worker produces rich JSON under 3,000 chars
compressor produces Step-6 card under 1,200-1,500 chars
validator checks exact compact card
compare card against the direct compact worker output
```

Use one case first:

```text
third-year-phd-student
```

Why PhD:

```text
it has two clear gates
the prior compact output nearly hit cap
failure is easy to see if either fallback or Silva/data disappears
```

Pass condition:

```text
compressed card under cap
fallback executability preserved
Silva/data access preserved
relaxation and discard conditions still usable
```

Kill condition:

```text
if compression drops one of the two controlling gates, do not add a compressor;
pause worker automation and keep raw artifacts as the simpler baseline
```

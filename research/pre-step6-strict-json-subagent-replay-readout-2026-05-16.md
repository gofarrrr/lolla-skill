# Pre-Step-6 Strict JSON Subagent Replay Readout

Date: 2026-05-16

Status: research-only replay readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-strict-worker-output-contract-readout-2026-05-16.md
research/pre-step6-rendered-workpack-subagent-replay-readout-2026-05-16.md
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

If the rendered workpack prompt requires exactly one JSON object, do native
subagents produce machine-readable `reasoning_artifact.v1` outputs without
losing the targeted reasoning lift?

## Setup

The same three admitted workpacks were replayed:

```text
third-year-phd-student
founder-grant-marcus-equity
mid-level-consultant-report-2
```

The mother no-worker sentinel still had no workpack and no producer run.

The strict prompt added:

```text
Return exactly one JSON object and nothing else.
Do not use Markdown fences or prose outside the JSON object.
JSON keys must be exactly ...
max serialized JSON chars: 1500
```

## Results

| Case | JSON Syntax | Exact Keys | Content Lift | Schema Shape | Size |
| --- | --- | --- | --- | --- | --- |
| Third-year PhD student | Pass | Pass | Fallback executability + Silva/data gates | `source_grounding` returned as list | 3,091 chars |
| Founder grant Marcus equity | Pass | Pass | Dependency-system map + staged gates | `source_grounding` returned as list | 2,810 chars |
| Mid-level consultant report | Pass | Pass | Counsel/channel/Wednesday guardrails | `source_grounding` and `contribution` returned as lists | 3,134 chars |

Aggregate:

```text
strict JSON objects: 3/3
exact required key set: 3/3
content passes: 3/3
mother producer runs: 0
within 1,500-char cap: 0/3
runtime promotion authorized: no
```

## Interpretation

The stricter prompt fixed the first serialization problem:

```text
no Markdown
no prose outside JSON
valid JSON object
expected keys present
```

It exposed the next two problems:

```text
the original v1 schema was too narrow about multi-part fields
the workers still over-produced by about 2x
```

The list shape was not a bad reasoning move. For `source_grounding` and
`contribution`, lists are often the natural representation of multiple pieces
of pressure. The validator has therefore been adjusted to allow strings or
short string arrays only for those two fields.

The size miss is more serious. A 3,000-character worker output may be readable,
but three such workers would give Step 6 another bulky private packet. That
violates the point of the worker system.

## Contract Adjustment

The worker-output validator now allows:

```text
source_grounding: string or short string array
contribution: string or short string array
```

It still requires single strings for:

```text
hard_boundary
relaxation_condition
discard_condition
relation_to_bundle
priority_hint
risk_if_forced
risk_if_ignored
```

And it now guards arrays:

```text
max array items: 4
max array item chars: 180
serialized output cap: 1,500 chars
unknown fields rejected
nested objects rejected by exact-field validation
```

## Decision

```text
strict_json_prompt_passes_syntax_and_key_compliance
content_quality_remains_strong
schema_allows_short_arrays_for_grounding_and_contribution
compression_is_not_solved
do_not_build_runtime_worker_ingestion
do_not_build_reasoning_bundle
```

## Next Slice

The next useful experiment is a compact JSON prompt, not more worker types.

Change the renderer from "exact keys" to "exact compact skeleton":

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

Then rerun one or two workers. Do not rerun all three until at least one worker
can hit both:

```text
valid JSON
<= 1,500 serialized chars
```

Kill condition:

```text
if compact JSON destroys the useful reasoning, worker artifacts may need a
two-stage producer/compressor path, or the worker path should remain manual
research only
```

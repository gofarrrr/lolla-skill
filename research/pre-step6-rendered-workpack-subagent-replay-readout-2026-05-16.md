# Pre-Step-6 Rendered Workpack Subagent Replay Readout

Date: 2026-05-16

Status: research-only replay readout. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-workpack-validation-harness-readout-2026-05-16.md
research/pre-step6-native-subagent-admission-gate-readout-2026-05-16.md
research/pre-step6-native-subagent-producer-test-readout-2026-05-16.md
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

Do the deterministic `reasoning_workpack.v1` renderer prompts reproduce the
useful native subagent producer behavior from the hand-written prompts?

This is not a final-answer comparison. It tests whether the workpack contract
can feed native subagents without losing the targeted lift.

## Setup

Rendered workpacks:

```text
research/pre-step6-workpack-fixtures/third-year-phd-student.boundary-evidence-gate.workpack.v1.json
research/pre-step6-workpack-fixtures/founder-grant-marcus-equity.boundary-evidence-gate.workpack.v1.json
research/pre-step6-workpack-fixtures/mid-level-consultant-report-2.boundary-evidence-gate.workpack.v1.json
```

Skipped by design:

```text
research/pre-step6-workpack-fixtures/mother-address-year.admission.v1.json
```

The mother case has a decline admission and no workpack fixture, so no producer
subagent was launched.

Each admitted worker received only the rendered prompt:

```text
shared situation brief
admission record
one worker question
local artifacts
source excerpts
forbidden moves
reasoning_artifact.v1 output contract
```

Each worker had `fork_context=false` and was told not to edit files or write
final-answer prose.

## Criteria

Content pass criteria:

```text
PhD recovers fallback executability and Silva/data as hard gates
founder recovers dependency-system map and measurable staged gates
consultant recovers counsel/channel/Wednesday conduct boundaries
mother remains skipped
no worker asks for full transcript
no worker gives final-answer prose
no worker invents unsupported precision
no worker gives legal certainty
```

Serialization pass criteria:

```text
all workers return the same machine-parseable shape
all required reasoning_artifact.v1 fields present
no prose outside the artifact object
```

## Results

| Case | Content Result | Serialization Result | Verdict |
| --- | --- | --- | --- |
| Third-year PhD student | Recovered fallback executability and Silva/data gates | Field-list text, parseable by a human but not strict JSON | Content pass, serialization miss |
| Founder grant Marcus equity | Recovered dependency map, 90-day gates, risk of forced concession and vague delay | Strict JSON object | Pass |
| Mid-level consultant report | Recovered counsel/channel/Wednesday conduct guardrails without legal conclusion | Field-list text with quoted values, parseable by a human but not strict JSON | Content pass, serialization miss |
| Mother deciding address year | No producer launched | Correctly absent | Pass |

Aggregate:

```text
rendered workpack prompts run: 3
content passes: 3
serialization passes: 1
no-worker sentinel producer runs: 0
runtime promotion authorized: no
reasoning_bundle build triggered: no
```

## Case Notes

### Third-Year PhD Student

The rendered prompt recovered the intended lift:

```text
fallback executability gate
Silva/data access gate
relaxation only from concrete evidence
risk that Step 6 endorses fictional optionality
```

This is a better result than the first native producer slice, where Silva/data
was missed.

Main issue: the output was a field-list artifact, not strict JSON.

### Founder Grant Marcus Equity

The rendered prompt recovered:

```text
Marcus/Jake/Lina/platform/client/exit dependency loop
90-day validation sprint as staged evidence
full bundle treated as downstream of dependency-reduction evidence
risk of immediate concession
risk of vague delay or refusal triggering the exposed dependency
```

This was the cleanest result because it returned a strict JSON object and did
not drift into package design.

### Mid-Level Consultant Report

The rendered prompt recovered:

```text
counsel engagement vs reporting
GC vs audit committee vs external channels
ordinary attendance vs evidence-seeking
no legal conclusions
no self-directed investigation
```

Main issue: the artifact was not strict JSON. It used field-list text with
quoted values.

### Mother Deciding Address Year

No rendered workpack exists and no producer ran. That is the correct result.

The structural guard from the workpack harness held:

```text
decline admission
no workpack fixture
tests reject declined admission_ref as a workpack source
```

## Interpretation

The content result is encouraging:

```text
the deterministic workpack renderer preserved enough context for native
subagents to reproduce the targeted boundary/evidence-gate lift
```

The automation result is not ready:

```text
the output contract is still too loose for deterministic ingestion
```

The renderer says "Return one compact reasoning_artifact.v1 only" and lists
required fields, but it does not force exact JSON. Native subagents complied
semantically but not structurally.

That matters because the future system cannot depend on a human reading worker
output and deciding whether the shape is close enough.

## Decision

```text
rendered_workpack_prompts_pass_content_replay
workpack_contract_not_yet_machine_ingestible
strict_worker_output_json_required_before_any_runtime_path
mother_no_worker_sentinel_remains_protected
raw_artifact_baseline_remains_control_to_beat
no_runtime_promotion
no_reasoning_bundle_build
```

## Next Slice

Tighten the output side before adding worker types:

```text
update workpack renderer to require exact JSON object output
add reasoning_artifact.v1 worker-output validator
add fixture tests for valid worker artifacts and malformed outputs
rerun rendered-prompt subagents after the stricter contract
```

2026-05-16 follow-up: the strict output contract now exists in
`scripts/research/pre_step6_workpacks.py`, with normalized worker-output
fixtures and validator tests. See:

```text
research/pre-step6-strict-worker-output-contract-readout-2026-05-16.md
```

Pass condition:

```text
all three admitted workers return valid reasoning_artifact.v1 JSON while
preserving the same content lift
```

Kill condition:

```text
if strict JSON materially degrades worker reasoning, keep workers research-only
and consider a human-readable artifact path only for manual research, not runtime
automation
```

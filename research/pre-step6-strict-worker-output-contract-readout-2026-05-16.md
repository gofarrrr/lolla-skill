# Pre-Step-6 Strict Worker Output Contract Readout

Date: 2026-05-16

Status: research-only implementation readout. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1,
V60, the canonical knowledge base, or public output.

Related:

```text
research/pre-step6-rendered-workpack-subagent-replay-readout-2026-05-16.md
research/pre-step6-workpack-validation-harness-readout-2026-05-16.md
scripts/research/pre_step6_workpacks.py
tests/test_pre_step6_workpacks.py
```

## Question

Can the rendered workpack contract be tightened so worker outputs are
machine-parseable, not merely human-readable?

The rendered-workpack replay passed content recovery but missed serialization:

```text
PhD: field-list text
founder: strict JSON
consultant: field-list text with quoted values
```

That is not good enough for an automated research harness.

## What Changed

The workpack renderer now tells workers:

```text
Return exactly one JSON object and nothing else.
Do not use Markdown fences or prose outside the JSON object.
```

The output contract now renders:

```text
schema_version must be: reasoning_artifact.v1
max serialized JSON chars: 1500
JSON keys must be exactly:
- schema_version
- why_provided
- source_grounding
- contribution
- hard_boundary
- relaxation_condition
- discard_condition
- relation_to_bundle
- priority_hint
- risk_if_forced
- risk_if_ignored
```

New worker-output validator:

```text
validate_worker_output_payload
validate_worker_output_file
--worker-output CLI mode
```

New normalized output fixtures:

```text
research/pre-step6-worker-output-fixtures/third-year-phd-student.rendered-replay.worker-output.v1.json
research/pre-step6-worker-output-fixtures/founder-grant-marcus-equity.rendered-replay.worker-output.v1.json
research/pre-step6-worker-output-fixtures/mid-level-consultant-report-2.rendered-replay.worker-output.v1.json
```

## Gates Added

The worker-output validator enforces:

```text
exact top-level keys only
schema_version == reasoning_artifact.v1
all required fields present
all required fields are non-empty strings, except source_grounding and contribution
source_grounding and contribution may be short string arrays
serialized JSON length <= 1,500 chars
arrays capped at 4 items
array items capped at 180 chars
unknown fields rejected
```

The first strict replay showed that `source_grounding` and sometimes
`contribution` naturally become multi-part values. The contract now permits
short arrays for those fields while keeping boundary, relaxation, discard, and
risk fields as single strings.

## Test Results

Commands run:

```text
PYTHONPATH=. pytest tests/test_pre_step6_workpacks.py
PYTHONPATH=. pytest tests/test_pre_step6_raw_artifacts.py tests/test_pre_step6_workpacks.py
python3 -m py_compile scripts/research/pre_step6_workpacks.py
python3 scripts/research/pre_step6_workpacks.py research/pre-step6-worker-output-fixtures/founder-grant-marcus-equity.rendered-replay.worker-output.v1.json --worker-output
python3 scripts/research/pre_step6_workpacks.py research/pre-step6-workpack-fixtures/third-year-phd-student.boundary-evidence-gate.workpack.v1.json --repo-root . --render
```

Results:

```text
tests/test_pre_step6_workpacks.py: 17 passed
raw artifact + workpack suites: 31 passed
py_compile passed
worker-output CLI validation passed
strict JSON prompt rendered successfully
```

## Interpretation

This fixes the deterministic custody side of the serialization problem. The
system can now express:

```text
what worker output must look like
how big it can be
which fields are required
which malformed shapes are rejected
```

It does not yet prove native subagents will obey the stricter prompt. That must
be replayed.

2026-05-16 follow-up: strict replay produced valid JSON and exact keys in all
three admitted cases, but all three exceeded the 1,500-character cap. See:

```text
research/pre-step6-strict-json-subagent-replay-readout-2026-05-16.md
```

## Decision

```text
strict_worker_output_contract_exists
human-readable_field_list_outputs_are_not_acceptable_for_automation
source_grounding_and_contribution_may_be_short_arrays
unknown_worker_output_fields_rejected
no_runtime_promotion
```

## Next Slice

Rerun the three admitted rendered workpacks through native subagents using the
stricter JSON prompt.

Pass condition:

```text
3/3 admitted workers return valid reasoning_artifact.v1 JSON
content lift remains comparable to the previous replay
mother no-worker sentinel remains skipped
```

Kill condition:

```text
if strict JSON compliance damages reasoning quality or still yields malformed
outputs, keep worker production research-only and improve the output contract
before building any parser into a larger harness
```

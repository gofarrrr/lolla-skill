# Pre-Step-6 Workpack Validation Harness Readout

Date: 2026-05-16

Status: research-only implementation readout. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1,
V60, the canonical knowledge base, or public output.

Related:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-native-subagent-admission-gate-readout-2026-05-16.md
research/pre-step6-native-subagent-producer-test-readout-2026-05-16.md
research/pre-step6-raw-artifact-render-validation-slice-2026-05-16.md
```

## Question

Can the manually successful admission-first native subagent shape be turned into
an executable research-only contract without touching live `/lolla`?

The slice tested this shape:

```text
admission record
  -> admitted cases only
  -> reasoning_workpack.v1
  -> deterministic prompt renderer
  -> bounded native worker can later produce reasoning_artifact.v1
```

The harness does not launch workers. It packages and validates the worker task.

## What Was Built

New research-only validator/renderer:

```text
scripts/research/pre_step6_workpacks.py
```

New static fixtures:

```text
research/pre-step6-workpack-fixtures/third-year-phd-student.admission.v1.json
research/pre-step6-workpack-fixtures/founder-grant-marcus-equity.admission.v1.json
research/pre-step6-workpack-fixtures/mid-level-consultant-report-2.admission.v1.json
research/pre-step6-workpack-fixtures/mother-address-year.admission.v1.json
research/pre-step6-workpack-fixtures/third-year-phd-student.boundary-evidence-gate.workpack.v1.json
research/pre-step6-workpack-fixtures/founder-grant-marcus-equity.boundary-evidence-gate.workpack.v1.json
research/pre-step6-workpack-fixtures/mid-level-consultant-report-2.boundary-evidence-gate.workpack.v1.json
```

New tests:

```text
tests/test_pre_step6_workpacks.py
```

The mother no-worker sentinel has an admission fixture but intentionally has no
workpack fixture.

## Contract

`pre_step6_worker_admission.v1` requires:

```text
case_id
worker_type
candidate_worker_question
decision
reason
expected_artifact_contribution
unnecessary_if
kill_condition
source_excerpts
```

`reasoning_workpack.v1` requires:

```text
workpack_id
case_id
worker_type
admission_ref
admission_gate
shared_situation_brief
worker_question
local_artifacts
source_excerpts
forbidden_moves
output_contract
```

The renderer produces the private worker prompt in this order:

```text
shared situation brief
admission record
one worker question
local artifacts
source excerpts
forbidden moves
reasoning_artifact.v1 output contract
```

That order matters. The worker sees situation before slice, admission before
production, and forbidden moves before the output contract.

The rendered prompt also explicitly tells the worker not to edit files and not
to write final answer prose.

## Static Gates

The harness now enforces:

```text
status must be research_only
runtime_policy must be runtime_dormant
worker_type limited to boundary/evidence-gate
admission decision limited to admit_worker or decline_worker
declined admissions must have expected_artifact_contribution: none
workpacks require an admitted admission_ref
workpack admission_gate must be admit_worker
shared_situation_brief is required
local_artifacts must be 1-5
source_excerpts must be 1-4
worker output contract must require all reasoning_artifact.v1 fields
worker output max_chars must not exceed 1,500
rendered prompt max_chars must not exceed 7,000
```

This is deterministic custody, not deterministic cognition. The code packages
the question and caps the handoff; the worker still does the judgment-heavy
interpretation.

## Test Results

Commands run:

```text
PYTHONPATH=. pytest tests/test_pre_step6_workpacks.py
PYTHONPATH=. pytest tests/test_pre_step6_raw_artifacts.py tests/test_pre_step6_workpacks.py
python3 scripts/research/pre_step6_workpacks.py research/pre-step6-workpack-fixtures/third-year-phd-student.boundary-evidence-gate.workpack.v1.json --repo-root . --render
python3 scripts/research/pre_step6_workpacks.py research/pre-step6-workpack-fixtures/mother-address-year.admission.v1.json --admission
```

Results:

```text
tests/test_pre_step6_workpacks.py: 10 passed
tests/test_pre_step6_raw_artifacts.py + tests/test_pre_step6_workpacks.py: 24 passed
PhD workpack rendered successfully
mother no-worker admission validated successfully
```

The rendered PhD prompt stayed under cap and showed the intended order:

```text
SHARED SITUATION BRIEF
ADMISSION RECORD
WORKER QUESTION
LOCAL ARTIFACTS
SOURCE EXCERPTS
FORBIDDEN MOVES
OUTPUT CONTRACT
```

## What This Proves

This proves a narrow but useful thing:

```text
the admission-first shape can be represented as stable, validated,
research-only data and rendered into a bounded worker prompt
```

It also proves the no-worker sentinel can be represented structurally:

```text
mother case has decline admission
mother case has no workpack
tests fail if a declined admission is used as a workpack reference
```

## What This Does Not Prove

This does not prove:

```text
native workers improve final answers
the workpack prompt reproduces the prior manual subagent result
reasoning_bundle.v1 is needed
OpenRouter should produce worker artifacts
live /lolla should launch workers before Step 6
```

The harness has made the next experiment possible. It has not completed that
experiment.

## Decision

```text
research_only_workpack_contract_exists
admission_first_shape_is_now_executable_as_fixture_validation
boundary_evidence_gate_is_the_only_worker_type_allowed
mother_no_worker_sentinel_is_structurally_protected
raw_artifact_baseline_remains_the control_to_beat
no_runtime_promotion
no_reasoning_bundle_build
```

## Next Slice

The next slice should use the rendered workpack prompts as the actual producer
inputs:

```text
render three admitted workpacks
run native subagents from those rendered prompts
validate the returned reasoning_artifact.v1 text manually or with a small parser
compare against the previous manual producer artifacts
confirm mother still has no producer prompt
```

2026-05-16 follow-up: rendered-prompt replay passed content recovery in the
three admitted cases and kept the mother sentinel skipped, but exposed
serialization drift. See:

```text
research/pre-step6-rendered-workpack-subagent-replay-readout-2026-05-16.md
```

Pass condition:

```text
rendered workpack prompts recover the same targeted lifts as the manual prompts
without final-answer prose, unsupported precision, legal certainty, or full-context requests
```

Kill condition:

```text
if rendered workpacks produce worse artifacts than the hand prompts, pause worker
implementation and improve the shared brief / admission handoff before adding any
new worker type
```

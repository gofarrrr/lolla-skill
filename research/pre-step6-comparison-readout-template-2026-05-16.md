# Pre-Step-6 Comparison Readout Template

Date: 2026-05-16

Status: research template only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related docs:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
research/pre-step6-comparison-case-inventory-2026-05-16.md
research/pre-step6-comparison-fixtures/
```

## Purpose

Use this template to compare:

```text
Arm A: current control
Arm B: raw reasoning_artifact.v1 specimens
Arm C: indexed reasoning_bundle.v1
```

The bundle only wins if the final answer improves. Cleaner private notes are not
enough.

## Readout Header

```text
case_id:
source_run_id:
fixture_path:
readout_type: preflight | answer-variant comparison
date:
reviewer:
```

## Case Shape

```text
primary reasoning shape:
secondary reasoning shapes:
what makes this case high-clutter:
what would make this case a bad test:
```

## Inputs Checked

```text
current_control_summary_present: yes/no
raw_artifact_count:
bundle_index_present: yes/no
source_excerpt_count:
fixture_caps_respected: yes/no
public_machinery_terms_in_fixture_final_prompt: yes/no
```

## Arm Expectations

Before reading/writing any final answer variant, state the expected risk of each
arm.

```text
Arm A expected risk:
Arm B expected risk:
Arm C expected risk:
```

## Final-Answer Variant Notes

For a real comparison, generate or collect short final-answer variants for all
three arms. Do not score from private notes alone.

```text
Arm A answer path:
Arm B answer path:
Arm C answer path:
```

If this is only a preflight readout, write:

```text
not_run_preflight_only
```

## Primary Criteria

Score each criterion as:

```text
A wins
B wins
C wins
tie
not tested
```

| Criterion | Score | Evidence |
| --- | --- | --- |
| Source-grounded force survives |  |  |
| Unsupported precision decreases |  |  |
| Hard boundaries survive |  |  |
| Conflicts remain visible when unresolved |  |  |
| Duplicates are demoted |  |  |
| Quiet artifacts do not bloat answer |  |  |
| Public prose has no machinery leakage |  |  |
| Answer is at least as clear as control |  |  |

## Secondary Criteria

Secondary criteria cannot make the bundle win by themselves.

| Criterion | Score | Evidence |
| --- | --- | --- |
| Private handoff is easier to audit |  |  |
| Artifact IDs remain traceable |  |  |
| Overclaim risks visible before writing |  |  |
| Step 6 remains free to reject bundle |  |  |

## Bundle-Specific Check

```text
Did the bundle improve final prose, not just notes?
Did the bundle demote duplicates without deleting receipts?
Did the bundle preserve conflict instead of hiding it?
Did the bundle prevent overclaim?
Did the bundle make the answer shorter or clearer?
Which bundle fields carried any lift?
```

## Kill-Condition Check

```text
raw artifacts tied bundle: yes/no/untested
bundle hid conflict: yes/no/untested
Step 6 obeyed index instead of arbitrating: yes/no/untested
answer got longer or more caveated: yes/no/untested
bundle required broad context: yes/no/untested
benefit was only operator traceability: yes/no/untested
```

## Verdict

Use exactly one:

```text
C wins
B wins
A wins
tie - simpler path wins
preflight only - run answer variants next
invalid fixture
```

## Decision

Use exactly one:

```text
proceed_to_next_fixture
revise_fixture
run_answer_variants
prefer_raw_artifacts
pause_bundle_path
kill_bundle_path
```

## Notes

Keep notes short. The readout should make a decision easier, not become another
research essay.

# Pre-Step-6 Generated-Decline Evaluation Readout

Date: 2026-05-19

Status: research-only decline-evaluation slice. This does not change runtime
behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1,
V60, public output, workers, bundles, handoff modes, or generator
implementation.

Related:

```text
research/pre-step6-autoresearch-operating-loop-2026-05-19.md
research/pre-step6-no-rendered-handoff-v1-readout-2026-05-19.md
research/pre-step6-generator-contract-readiness-decision-2026-05-19.md
research/pre-step6-user-has-plan-static-decline-readout-2026-05-19.md
research/pre-step6-no-rendered-handoffs/mid-level-consultant-report-2.negative-control.native-rejudge.no-rendered-handoff.v1.json
research/pre-step6-decline-evaluations/mid-level-consultant-report-2.negative-control.no-rendered-decline-evaluation.v1.json
scripts/research/pre_step6_decline_evaluations.py
tests/test_pre_step6_decline_evaluations.py
```

## Question

Can a `no_rendered_handoff` candidate be evaluated as a healthy decline without
requiring a rendered candidate or source/overclaim audit?

## Why This Slice Exists

The previous slice made decline first-class:

```text
no_rendered_handoff.v1
```

But a first-class decline artifact is not enough. The replay process also needs
to evaluate decline as evidence:

```text
did withholding rendered preserve the simpler answer path?
did it avoid naturalness debt?
did it lose any critical pressure?
did it keep runtime/product/generator blocked?
```

This slice adds that evaluation surface.

## What Changed

Added:

```text
scripts/research/pre_step6_decline_evaluations.py
tests/test_pre_step6_decline_evaluations.py
research/pre-step6-decline-evaluations/mid-level-consultant-report-2.negative-control.no-rendered-decline-evaluation.v1.json
```

Schema:

```text
pre_step6_decline_evaluation.v1
```

Mode:

```text
off_by_default_static_decline_replay
```

## Key Design Choice

The evaluation uses the simpler raw-vs-control comparison:

```text
research/pre-step6-raw-artifact-comparisons/mid-level-consultant-report-2.raw-vs-control-comparison.v1.json
```

It does not require:

```text
rendered candidate
source/overclaim audit
generator implementation
runtime wiring
```

This matters. A decline path cannot require the thing it declined to produce.

The existing rendered negative-control audit remains useful background evidence,
but the decline evaluation itself validates against the no-rendered candidate
and the simpler comparison.

## Evaluation Result

The first decline evaluation validates:

```text
case: mid-level-consultant-report-2
comparison_decision: raw_wins
decline_evaluation_decision: healthy_decline
generator_next_step: blocked
naturalness_debt_avoided: medium
```

Interpretation:

```text
the simpler raw/control path preserved the needed safety/counsel sequence
the rendered surface was not required for this evaluation
withholding rendered avoided the known medium naturalness-debt risk
generator implementation remains blocked
```

## Miss Checks

The record requires four miss checks:

```text
no_critical_pressure_lost
control_sufficiency_survives
receipt_stayed_small
reactivation_condition_clear
```

All pass for the consultant case.

The validator rejects a healthy decline if any miss check fails.

## Validator Guards

The validator rejects:

```text
rendered_candidate_required: true
source_overclaim_audit_required: true
runtime_wiring_allowed: true
product_promotion_allowed: true
generator_implementation_allowed: true
comparison_decision drift
healthy_decline with failed miss check
healthy_decline that advances generator implementation
```

This keeps the deterministic layer in custody mode. It validates evidence
shape; it does not decide final advice.

## Validation

Focused tests:

```text
PYTHONPATH=. pytest tests/test_pre_step6_decline_evaluations.py
6 passed
```

CLI:

```text
python3 scripts/research/pre_step6_decline_evaluations.py \
  research/pre-step6-decline-evaluations/mid-level-consultant-report-2.negative-control.no-rendered-decline-evaluation.v1.json \
  --repo-root .
```

## PM Read

This is a useful restraint milestone.

We now have two separate things:

```text
no_rendered_handoff.v1:
  the candidate decline artifact

pre_step6_decline_evaluation.v1:
  the replay-style evaluation of that decline
```

That separation matters. The first says:

```text
do not produce rendered here, and here is the small receipt
```

The second says:

```text
the decline was healthy because the simpler path preserved enough and avoided
the rendered naturalness tax
```

This is still not a generator. It is the evaluation surface a future generator
would have to satisfy.

## What This Does Not Prove

This does not prove:

```text
a generator can find decline cases
decline generalizes beyond consultant
the simpler raw/control comparison is always enough
rendered should be off by default in runtime
product promotion is closer
```

It proves only:

```text
a no-rendered decline can be represented and evaluated without requiring a
rendered candidate
```

## Next Decision

The original auto-research queue has now completed:

```text
no_rendered_handoff proposal
manual no_rendered_handoff fixture
minimal validator
decline evaluation record
```

The next question is a decision question, not implementation:

```text
Do we specify a tiny off-default candidate generator contract next, or do we run
one more static decline/control replay before generator-spec work?
```

Given the evidence, the safer next slice is a short decision memo, not generator
implementation.

2026-05-19 follow-up:

```text
research/pre-step6-generator-contract-readiness-decision-2026-05-19.md
```

The decision memo records that generator-contract work is not earned yet. The
next evidence should be one more static decline/control replay in a non-safety /
non-counsel case before any off-default admission-layer contract is specified.

2026-05-19 static-decline follow-up:

```text
research/pre-step6-user-has-plan-static-decline-readout-2026-05-19.md
```

The second decline evaluation now uses the `user_has_plan` consulting-launch
case. It records `healthy_decline` with `raw_wins` and medium naturalness debt
avoided, without requiring a rendered candidate.

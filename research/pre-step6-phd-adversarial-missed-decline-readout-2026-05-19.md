# Pre-Step-6 PhD Adversarial Missed-Decline Readout

Date: 2026-05-19

Status: research-only adversarial decline calibration. This does not change
runtime behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product
docs, Lane 1, V60, public output, workers, bundles, handoff modes, generator
implementation, or an admission-layer contract.

Related:

```text
research/pre-step6-no-rendered-handoffs/third-year-phd-student.conflict.adversarial.no-rendered-handoff.v1.json
research/pre-step6-decline-evaluations/third-year-phd-student.conflict.adversarial.no-rendered-decline-evaluation.v1.json
research/pre-step6-semi-blind-comparisons/third-year-phd-student.conflict.semi-blind-comparison.v1.json
research/pre-step6-replay-records/third-year-phd-student.conflict.off-default-replay.v1.json
research/pre-step6-source-overclaim-audits/third-year-phd-student.conflict.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-generator-contract-readiness-decision-2026-05-19.md
research/pre-step6-autoresearch-operating-loop-2026-05-19.md
scripts/research/pre_step6_no_rendered_handoffs.py
scripts/research/pre_step6_decline_evaluations.py
tests/test_pre_step6_no_rendered_handoffs.py
tests/test_pre_step6_decline_evaluations.py
```

## Question

Can the no-rendered / decline-evaluation machinery honestly record that
withholding rendered would lose important pressure?

This slice is intentionally adversarial. It does not ask whether decline can be
healthy. It asks whether decline can be marked as missed when rendered already
had a clear pressure-transport job.

## Why PhD

The PhD conflict case is a known rendered-positive replay:

```text
semi-blind comparison: rendered_hybrid_wins
replay_decision: pass_to_next_replay
source/overclaim audit: pass
naturalness debt: medium
```

Rendered did not win because it was lighter. It won because it better preserved:

```text
unresolved Silva-vs-fallback tension
data/collaboration evidence gates
fallback executability
duplicate demotion
```

That makes it a good marked-cliff case. If a no-rendered receipt declines here,
the research layer should probably call that decline missed, not healthy.

## Predeclared Failure Risk

Declining rendered could fail if the simple path:

```text
loses the explicit refusal to choose Silva now
collapses by default to the safer fallback
drops data access, advisor support, or fallback executability gates
treats medium naturalness debt as enough reason to ignore a rendered win
```

## What Changed

The no-rendered validator now supports a third evidence basis:

```text
rendered_win_replay
```

That basis is intentionally narrow:

```text
requires semi-blind comparison evidence
requires replay-record evidence
requires rendered_hybrid_wins
requires pass_to_next_replay
can only support missed_decline or retest_decline
cannot support healthy_decline
```

This is custody work, not selector logic. It lets the research layer say:

```text
decline was tried here, and decline would have lost pressure
```

It does not decide final advice or create a future selection rule.

## Result

New no-rendered fixture:

```text
case: third-year-phd-student
evidence_basis: rendered_win_replay
decline_decision: missed_decline
naturalness_debt_risk: medium
expected_result: missed_decline
simpler_arm_expected: raw_wins
```

New decline evaluation:

```text
comparison_decision: raw_wins
decline_evaluation_decision: missed_decline
naturalness_debt_avoided: none
generator_next_step: blocked
```

Interpretation:

```text
raw beats control in the simpler comparison
but rendered had already beaten both in the semi-blind conflict replay
so no-rendered would avoid medium naturalness debt at the cost of losing useful conflict pressure
```

## Miss Checks

The decline evaluation records two failed miss checks:

```text
no_critical_pressure_lost: fail
control_sufficiency_survives: fail
```

And two custody checks still pass:

```text
receipt_stayed_small: pass
reactivation_condition_clear: pass
```

That distinction matters. The receipt can be well-formed and still represent a
bad decline.

## Validator Guards

The updated validators reject:

```text
rendered_win_replay without both semi-blind comparison and replay-record evidence
rendered_win_replay that expects healthy_decline
rendered_win_replay with valid_research_decline
missed_decline without at least one failed miss check
decline evaluation that disagrees with the no-rendered expected_result
```

The existing blocks remain:

```text
runtime wiring
product promotion
generator implementation
hidden answer-plan language
rendered candidate requirement for decline evaluation
source/overclaim audit requirement for decline evaluation
```

## PM Read

This is the missing calibration point.

Before this slice, the archive had:

```text
rendered wins
healthy declines
rendered stops
```

But it did not yet have:

```text
a no-rendered decline that was itself marked missed
```

Now it does.

That means the research layer is less decline-biased. It can record both:

```text
do not produce rendered here
do not withhold rendered here
```

without turning either statement into a runtime rule.

## What This Does Not Prove

This does not prove:

```text
a future admission layer can find missed declines
a generator contract is ready to implement
rendered should become runtime default
medium naturalness debt is harmless
```

It proves only:

```text
the decline machinery can record an adversarial missed decline against an existing rendered-positive replay
```

## Decision

Current decision:

```text
adversarial_decline_calibration: recorded
generator_implementation: blocked
runtime_wiring: blocked
product_promotion: blocked
new_handoff_modes: blocked
bundle: blocked
workers: blocked
admission_layer_contract: still docs-only if pursued
```

The next PM question is now cleaner:

```text
Is one marked cliff enough to draft a containment-only admission-layer contract,
or do we want a retest_decline case before writing that contract?
```

Either path stays research-only. No implementation is earned by this slice.

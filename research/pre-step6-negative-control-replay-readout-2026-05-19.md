# Pre-Step-6 Negative Control Replay Readout

Date: 2026-05-19

Status: research-only negative/control replay ledger slice. This does not change
runtime behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs,
Lane 1, V60, the canonical knowledge base, public output, workers, bundles,
handoff modes, or replay generation.

Related:

```text
research/pre-step6-semi-blind-comparisons/mid-level-consultant-report-2.negative-control.semi-blind-comparison.v1.json
research/pre-step6-source-overclaim-audits/mid-level-consultant-report-2.negative-control.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-replay-records/mid-level-consultant-report-2.negative-control.off-default-replay.v1.json
research/pre-step6-rendered-hybrid-answer-cores/mid-level-consultant-report-2.native.rendered-hybrid-answer-core.v1.json
```

## Question

Can the replay ledger record evidence against the rendered-hybrid path without
schema bending?

This slice deliberately chooses a case where the simpler arm should plausibly be
enough:

```text
mid-level consultant sees a partner in a risky after-hours situation
counsel-first preservation already carries the needed first-step pressure
main risk is over-processing or self-directed reporting
control is already short, grounded, and humane
```

This is the first replay ledger slice where rendered hybrid is expected to tie
or lose if the process is honest.

## Why This Case

The consultant case is high-stakes but not high-clutter in the founder sense.
The sufficient pressure path is mostly:

```text
do not confront
do not investigate privately
do not access systems unusually
document what happened
contact whistleblower attorneys
let counsel decide channel and timing
attend Wednesday normally
keep first moves reversible
```

The rendered answer recovers useful nuance:

```text
counsel channel-bias intake questions
Wednesday response boundaries
```

But those details may be lower marginal value than restraint. This makes the
case a good negative/control replay.

## Semi-Blind Comparison

Comparison kind:

```text
semi_blind_local_rubric
```

Hidden map:

```text
A = rendered hybrid
B = control
C = raw-only
```

Criterion result:

```text
control wins: 7
rendered hybrid wins: 1
raw-only wins: 0
ties: 0
```

Criterion winners:

```text
decision_usefulness: control
source_grounding: control
overclaim_risk: control
answer_length_cognitive_load: control
machinery_hygiene: control
conflict_preservation: rendered hybrid
duplicate_demotion: control
unforcedness: control
```

Aggregate:

```text
aggregate winner: B
unblinded: control
aggregate_decision: control_wins
promotion_read: stop
```

Rendered did add useful conflict preservation. It did not earn the aggregate win
because the case rewarded lower burden, tighter source posture, and counsel-first
restraint.

## Source/Overclaim Audit

The current ledger schema records a source/overclaim audit even when rendered
does not win. In this slice the audit is custody evidence, not a replay-win
gate.

Audit result:

```text
audit_result: pass
decision: does_not_count
naturalness_debt_level: medium
```

Required checks:

```text
source_grounding: pass
probability_overclaim: pass
evidence_gate_integrity: pass
unsupported_option_expansion: watch
naturalness_debt: watch
```

No overclaim findings were recorded.

This is important: rendered did not lose because it was false or unsafe. It lost
because the simpler control was better for this situation.

## Replay Ledger Outcome

Replay record:

```text
comparison_decision: control_wins
replay_decision: stop
product_promotion: blocked
naturalness_debt: medium
present_or_watch_failure_modes: 3
```

The ledger successfully records:

```text
rendered hybrid did not help here
simpler control won
source/overclaim audit still passed
rendered does_not_count
replay_decision is stop
product promotion remains blocked
runtime wiring remains false
```

That is the research behavior we needed to prove.

## PM Verdict

This is a healthy loss.

The result does not weaken the previous founder/PhD evidence. It sharpens the
boundary:

```text
rendered hybrid is useful when selected pressure would otherwise be lost
rendered hybrid can be worse when the control answer is already short, grounded,
and counsel-first
```

This is the first evidence that the replay ledger is not only failure-capable in
schema. It can record a rendered-hybrid loss in practice.

## Decision

```text
negative_control_replay_records_rendered_loss
control_wins_aggregate
rendered_audit_passes_but_does_not_count
naturalness_debt_medium
rendered_overprocessing_present
product_promotion_blocked
runtime_wiring_blocked
replay_generator_not_earned
no_new_mode
no_bundle
no_workers
```

## Next Gate

Do not jump to generator work from this loss.

The next useful move is a post-negative aggregate decision readout that asks:

```text
Does one rendered loss plus four rendered wins justify a generator proposal?
Is the medium naturalness-debt pattern too strong?
Should another negative/control case be run with a native judge?
Can a future generator be designed to decline rendered handoff generation when
control is already enough?
```

Until that decision is made, generator work remains blocked.

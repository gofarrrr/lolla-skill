# Pre-Step-6 Negative Control Native Rejudge Readout

Date: 2026-05-19

Status: research-only native negative-control rejudge. This does not change
runtime behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs,
Lane 1, V60, the canonical knowledge base, public output, workers, bundles,
handoff modes, replay generation, or selector implementation.

Related:

```text
research/pre-step6-semi-blind-comparisons/mid-level-consultant-report-2.negative-control.native-rejudge.semi-blind-comparison.v1.json
research/pre-step6-source-overclaim-audits/mid-level-consultant-report-2.negative-control.native-rejudge.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-replay-records/mid-level-consultant-report-2.negative-control.native-rejudge.off-default-replay.v1.json
research/pre-step6-negative-control-replay-readout-2026-05-19.md
research/pre-step6-selector-boundary-decision-memo-2026-05-19.md
```

## Question

Does the first rendered-hybrid loss survive a judge that did not author the local
negative-control rubric?

This slice is the adversarial check on the first consultant stop.

## Method

A native less-author-biased judge received only:

```text
the consultant case brief
candidate A
candidate B
candidate C
the eight replay criteria
```

The judge did not receive source labels or the previous local negative-control
verdict.

Hidden map:

```text
A = raw-only
B = control
C = rendered hybrid
```

Judge type:

```text
semi_blind_native_judge
```

## Result

Criterion result:

```text
control wins: 6
rendered hybrid wins: 1
raw-only wins: 0
ties: 1
```

Criterion winners:

```text
decision_usefulness: rendered hybrid
source_grounding: control
overclaim_risk: control
answer_length_cognitive_load: control
machinery_hygiene: control
conflict_preservation: tie
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

The native judge did not punish rendered as severely as the local rubric. It
called rendered the strongest complete decision aid and a strong runner-up. But
it still chose control aggregate because this case rewards counsel-first
simplicity, low cognitive load, and low procedural texture.

## What Rendered Still Did Well

Rendered won:

```text
decision_usefulness
```

Rendered tied:

```text
conflict_preservation
```

The native judge valued the added independent-counsel/channel nuance and the
narrow Wednesday response protocol. This matters because the rendered answer was
not bad or unsafe.

## Why Control Still Won

Control won:

```text
source grounding
overclaim risk
answer length / cognitive load
machinery hygiene
duplicate demotion
unforcedness
```

The judge's reason was the selector-boundary point:

```text
the simpler answer carries the core counsel-first sequence with less cognitive
load, lower procedural feel, and lower risk of over-processing
```

That confirms the local negative-control direction.

## Source/Overclaim Audit

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

This preserves the important distinction:

```text
rendered is safe enough
rendered is not useful enough to count
```

## Replay Ledger Outcome

Replay record:

```text
comparison_decision: control_wins
replay_decision: stop
product_promotion: blocked
naturalness_debt: medium
present_or_watch_failure_modes: 3
```

Rendered does not count:

```text
source audit decision: does_not_count
replay_decision: stop
```

## PM Verdict

This is the strongest decline evidence so far.

The first consultant stop was local-rubric. The native rejudge now confirms the
direction:

```text
control should win this negative/control case
rendered is valid but too procedurally costly
```

This makes decline behavior first-class. It also keeps generator work blocked,
because the next unsolved problem is not whether rendered can help. It is how a
future selective process could know when to withhold rendered without becoming a
deterministic judge.

## Decision

```text
negative_control_stop_survives_native_rejudge
control_wins_aggregate
rendered_wins_decision_usefulness_only
rendered_ties_conflict_preservation
rendered_audit_passes_but_does_not_count
naturalness_debt_medium
product_promotion_blocked
runtime_wiring_blocked
generator_implementation_blocked
no_new_mode
no_bundle
no_workers
```

## Next Gate

Do not implement a generator.

The next useful move is to update the selector-boundary memo and aggregate read
with this native-confirmed stop, then decide whether the evidence is sufficient
to draft a tiny off-default generator proposal or whether one more negative
case is required.

The PM bias after this result should still be conservative:

```text
generator proposal maybe discussable
generator implementation still blocked
product promotion still blocked
runtime wiring still blocked
```

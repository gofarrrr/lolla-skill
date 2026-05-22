# Pre-Step-6 Founder High-Clutter Native Rejudge Readout

Date: 2026-05-19

Status: research-only native rejudge replay ledger slice. This does not change
runtime behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs,
Lane 1, V60, the canonical knowledge base, public output, workers, bundles,
handoff modes, or replay generation.

Related:

```text
research/pre-step6-semi-blind-comparisons/founder-grant-marcus-equity.high-clutter.native-rejudge.semi-blind-comparison.v1.json
research/pre-step6-source-overclaim-audits/founder-grant-marcus-equity.high-clutter.native-rejudge.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-replay-records/founder-grant-marcus-equity.high-clutter.native-rejudge.off-default-replay.v1.json
research/pre-step6-rendered-hybrid-answer-cores/founder-grant-marcus-equity.high-clutter.native.rendered-hybrid-answer-core.v1.json
```

## Question

Does the least comfortable local-rubric replay win survive a judge that did not
author the local founder rubric?

This slice reused the same three arms:

```text
current control
raw-only
rendered hybrid high-clutter answer core
```

The existing founder local-rubric comparison was not overwritten. This is a
second evidence chain.

## Method

A native less-author-biased judge received only:

```text
the founder case brief
candidate A
candidate B
candidate C
the eight replay criteria
```

The judge did not receive source labels or the previous local-rubric verdict.

Hidden map:

```text
A = control
B = rendered hybrid
C = raw-only
```

Judge type:

```text
semi_blind_native_judge
```

## Result

Criterion count:

```text
control: 4
rendered hybrid: 4
raw-only: 0
tie: 0
```

Criterion winners:

```text
decision_usefulness: rendered hybrid
source_grounding: control
overclaim_risk: control
answer_length_cognitive_load: control
machinery_hygiene: rendered hybrid
conflict_preservation: rendered hybrid
duplicate_demotion: rendered hybrid
unforcedness: control
```

Aggregate:

```text
aggregate winner: B
unblinded: rendered hybrid
aggregate_decision: rendered_hybrid_wins
criterion_count_decision: tie_stop
```

This is the important shape:

```text
rendered wins aggregate
control ties on simple count
control wins lightness, source caution, overclaim caution, and unforcedness
```

So founder survived the rejudge, but not cleanly.

## Why Rendered Won

The native judge preferred rendered hybrid on the dimensions that matter most
for this high-clutter founder case:

```text
usable Friday stance
no vague delay or flat rejection
explicit disengagement risk
keeps the full package premature
compresses duplicate instrument pressure
preserves dependency-system pressure
```

The judge's aggregate rationale was not that rendered was shorter or more
natural. It was that the case turns on preserving the central conflict:

```text
do not grant irreversible ownership/governance now
but do not answer in a way that triggers the dependency risk
```

## Why This Is A Brake

Control was not weak. It won:

```text
source grounding
overclaim risk
answer length / cognitive load
unforcedness
```

That means the rendered answer did not beat the simpler arm on simple criterion
count. It won because the judge weighted decision usefulness and conflict
preservation more heavily.

This is acceptable as replay evidence. It is not acceptable as promotion
evidence.

## Source/Overclaim Audit

Audit result:

```text
audit_result: pass
decision: counts_as_replay_win
naturalness_debt_level: medium
```

Required checks:

```text
source_grounding: watch
probability_overclaim: pass
evidence_gate_integrity: pass
unsupported_option_expansion: pass
naturalness_debt: watch
```

No overclaim findings were recorded.

The answer still avoided:

```text
$9-13M reactivation
4-6x buyer multiples
technical architecture diagnosis
software architecture diagnosis
long phantom equity / revenue share catalog
private machinery leakage
```

But the source-grounding watch matters. The native judge found the rendered arm
grounded overall, but slightly broader and more constructed than control.

## Naturalness And Bloat

Naturalness debt:

```text
medium
```

Bloat status:

```text
watch
```

The native judge described rendered as strong, but visibly optimized to hit the
known tensions. That is exactly the product risk this rejudge was meant to test.

The replay record therefore marks:

```text
criterion_count_tie: watch
source_grounding_stretch: watch
answer_bloat: watch
over_shaped_naturalness_debt: watch
```

## Replay Ledger Outcome

The replay ledger record is:

```text
comparison_decision: rendered_hybrid_wins
replay_decision: pass_to_next_replay
product_promotion: blocked
naturalness_debt: medium
present_or_watch_failure_modes: 4
```

This is a replay pass because rendered wins aggregate and passes source/overclaim
audit with non-high naturalness debt.

It is also a serious brake because the simpler control arm tied it on criterion
count.

## Decision

```text
founder_native_rejudge_survives
rendered_hybrid_wins_aggregate
control_ties_simple_criterion_count
naturalness_debt_medium
bloat_watch
source_grounding_watch
product_promotion_blocked
runtime_wiring_blocked
replay_generator_not_earned
no_new_mode
no_bundle
no_workers
```

## PM Verdict

This is useful because it makes the evidence less comfortable.

Rendered hybrid survived the less-author-biased judge, but the native result
also strengthened the central warning:

```text
rendered wins decision structure
control wins naturalness, brevity, and source caution
```

That means the next move is not generator work.

The next move should be a true negative/control replay where rendered hybrid is
allowed, and maybe expected, to tie or lose. The ledger still needs one record
that proves the research practice can write down evidence against the rendered
path without bending it into a win.

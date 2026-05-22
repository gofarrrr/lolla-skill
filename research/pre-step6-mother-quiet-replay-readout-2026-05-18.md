# Pre-Step-6 Mother Quiet Replay Readout

Date: 2026-05-18

Status: research-only quiet-sentinel replay ledger slice. This does not change
runtime behavior, `SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs,
Lane 1, V60, the canonical knowledge base, or public output.

Related:

```text
research/pre-step6-semi-blind-comparisons/mother-address-year.quiet.semi-blind-comparison.v1.json
research/pre-step6-source-overclaim-audits/mother-address-year.quiet.rendered-hybrid.source-overclaim-audit.v1.json
research/pre-step6-replay-records/mother-address-year.quiet.off-default-replay.v1.json
research/pre-step6-hybrid-handoff-fixtures/mother-address-year.hybrid-handoff.v1.json
research/pre-step6-rendered-hybrid-answer-cores/mother-address-year.native.rendered-hybrid-answer-core.v1.json
scripts/research/pre_step6_replay_ledger.py
tests/test_pre_step6_semi_blind_comparisons.py
tests/test_pre_step6_replay_ledger.py
```

## Question

Can quiet mode stay quiet when the right answer is "no extra cognition needed"?

This is a hostile-to-overuse replay. Rendered hybrid should not win by adding
structure, pressure, machinery, or extra claims. It should win or tie only by
being smaller, safer, more grounded, and at least as humane as raw/control.

## Fixture

The existing handoff is:

```text
handoff_mode: no_extra_pressure
source_pressure_card: forbidden
inspect_more: empty
quiet_guidance: specific preserve/do-not-add guidance
```

The key preserve obligation was:

```text
Silence in the monitored channel is weak evidence, not reassurance.
```

## Semi-Blind Comparison

This slice used a local semi-blind rubric record, not a native judge.

Hidden map:

```text
A = control
B = rendered hybrid
C = raw-only
```

Criterion result:

```text
rendered hybrid wins: 4
control wins: 2
raw-only wins: 0
ties: 2
```

Aggregate:

```text
aggregate winner: B
unblinded: rendered hybrid
promotion_read: pass_to_replay
```

This is not a clean dominance story. Control won:

```text
answer length / cognitive load
unforcedness
```

That matters. The control remains the lightest and most naturally phrased arm.

Rendered hybrid won because it preserved the control's decomposition while also
keeping the missing instrument-trust caution and not re-surfacing the tempting
leverage/power frame.

## Did Quiet Mode Stay Quiet?

Yes.

The rendered answer preserved:

```text
monitored-channel caution
concrete reversible tripwires
RAINN / therapist / counsel boundary
ex-information guard
safety plus a path back to honesty
```

It avoided:

```text
pressure card
raw inspect-more path
worker path
power-dynamics lens
strategic leverage framing
grooming probability claim
private machinery leakage
```

The answer did not become longer because a handoff existed. It is nearly the
same length as raw-only and keeps the private surface in no-extra-pressure mode.

## Source/Overclaim Audit

Audit result:

```text
audit_result: pass
decision: counts_as_replay_win
naturalness_debt_level: low
```

Required checks:

```text
source_grounding: pass
probability_overclaim: pass
evidence_gate_integrity: pass
unsupported_option_expansion: pass
naturalness_debt: pass
```

No overclaim findings were recorded.

The audit specifically checked that the answer:

```text
does not treat silence in the monitored channel as reassurance
does not assign a grooming probability
does not turn RAINN/counsel/therapist into an unsupported command hierarchy
does not add a worker or power/leverage frame
does not create extra procedural machinery
preserves concrete reversible tripwires
preserves safety plus path back to honesty
```

## Replay Ledger Outcome

The replay ledger record is:

```text
comparison_decision: rendered_hybrid_wins
source_overclaim_audit_recorded: true
source_overclaim_audit_passed: true
replay_decision: pass_to_next_replay
product_promotion: blocked
naturalness_debt: low
```

This is a replay win, not product promotion.

It is also a restraint win: rendered hybrid won without adding a pressure card,
inspect-more path, worker, bundle, power lens, leverage frame, or probability
claim.

## Interpretation

Mother is a stronger quiet-mode result than PhD on naturalness debt.

PhD passed with medium naturalness debt because its decision-gate language felt
somewhat engineered. Mother passed with low naturalness debt because the quiet
surface mostly preserved plain-language cautions:

```text
Silence in the monitored channel is weak evidence, not reassurance.
concrete, reversible tripwires
safety plus a path back to honesty
```

That is the behavior we wanted from `no_extra_pressure`: a small guardrail, not
a second driver.

## Decision

```text
mother_quiet_replay_passes
quiet_mode_stayed_quiet
monitored_channel_caution_survived
source_overclaim_audit_passed
naturalness_debt_low
product_promotion_blocked
runtime_wiring_blocked
no_new_mode
no_bundle
no_workers
```

## Next Gate

Run founder high-clutter demotion through the same replay ledger.

The hostile condition changes:

```text
mother tested overuse
founder should test bloat / private mini-index drift
```

Founder should pass only if dependency-system pressure survives while quiet
receipts stay quiet, duplicate/misfit artifacts do not become obligations, exit
math remains a false-precision caution, and answer length stays controlled.

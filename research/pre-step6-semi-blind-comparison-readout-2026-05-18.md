# Pre-Step-6 Semi-Blind Comparison Readout

Date: 2026-05-18

Status: research-only comparison gate. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related:

```text
research/pre-step6-semi-blind-comparisons/third-year-phd-student.conflict.semi-blind-comparison.v1.json
research/pre-step6-rendered-hybrid-answer-cores/third-year-phd-student.conflict.native.rendered-hybrid-answer-core.v1.json
research/pre-step6-raw-artifact-answer-cores/third-year-phd-student.raw-answer-core.v1.json
research/pre-step6-raw-artifact-comparisons/third-year-phd-student.raw-vs-control-comparison.v1.json
scripts/research/pre_step6_semi_blind_comparisons.py
tests/test_pre_step6_semi_blind_comparisons.py
```

## Question

Does the rendered hybrid answer core improve or simplify the final answer versus
simpler controls?

The comparison used the PhD conflict case because it is the first fixture where
the final answer must keep a real two-sided choice alive:

```text
higher-upside Silva path with uncertain data/collaboration
versus
safer advisor-backed fallback that may stop being executable
```

## Method

One native subagent received only blinded candidate labels:

```text
A
B
C
```

It did not receive the source labels:

```text
current control
raw-only
rendered hybrid
```

The hidden map was:

```text
A = raw-only
B = rendered hybrid
C = current control
```

The judge scored the candidates on:

```text
decision usefulness
source grounding
overclaim risk
answer length / cognitive load
machinery hygiene
conflict preservation
duplicate demotion
unforcedness
```

This is semi-blind, not fully blind. The coder still prepared the candidate set,
and there was only one native judge. Treat this as a research signal, not a
quality verdict.

## Result

The blinded judge chose:

```text
aggregate winner: B
promotion read: pass_to_replay
```

Unblinded:

```text
B = rendered hybrid
```

The criterion-level result was close:

```text
rendered hybrid wins: 3
raw-only wins: 3
control wins: 1
ties: 1
```

Rendered hybrid won the highest-value comparison dimensions:

```text
decision usefulness
conflict preservation
duplicate demotion
```

Raw-only won:

```text
overclaim risk
machinery/procedural feel
unforcedness
```

Control won:

```text
answer length / cognitive load
```

Source grounding was a tie.

## Interpretation

Pass to replay, not promotion.

This is not a clean domination result. The simple criterion count ties raw-only
and rendered hybrid, and raw-only remains meaningfully better on naturalness and
overclaim caution. The aggregate preference for rendered hybrid rests on the
judge weighting the more decision-critical dimensions more heavily:

```text
clearer gates
better preservation of unresolved Silva-vs-fallback tension
less duplicate pressure
```

That is enough to justify the next research gate. It is not enough to wire this
into `/lolla`, update product docs, build workers, or implement a bundle.

## What It Proves

This comparison gives the first semi-blind evidence that rendered hybrid can
improve a final-answer core where conflict preservation matters.

It also proves the opposite of a hype story:

```text
rendered hybrid is stronger on structure
raw-only is still stronger on naturalness and overclaim caution
control is still lighter
```

So the emerging surface is useful only if replay shows that the structure helps
more often than it makes answers feel over-shaped.

## What It Does Not Prove

This does not prove:

```text
general superiority over raw-only
human preference
multi-case robustness
source/overclaim durability
builder or selector correctness
runtime readiness
need for workers
need for reasoning_bundle.v1
```

Expected inclusions/exclusions remain regression guards, not answer-quality
proof.

## Decision

```text
semi_blind_phd_conflict_passes_to_replay
rendered_hybrid_wins_aggregate_but_not_simple_criterion_count
raw_only_naturalness_and_overclaim_caution_remain_live_risks
control_lightness_remains_a_live_baseline
no_product_promotion
no_runtime_wiring
no_new_mode
no_bundle
no_workers
```

## Next Gate

The next earned gate is an off-by-default replay harness, still research-only:

```text
take archived artifacts
construct candidate rendered handoff
run Step-6-style answer generation
compare against current control and raw-only
record health, failure modes, and over-shaped answers
```

Before treating replay wins as meaningful, add a source/overclaim audit on any
rendered-hybrid winner. The main risk now is not that the surface cannot carry
pressure. The risk is that it carries pressure too neatly and makes the final
answer feel more engineered than reasoned.

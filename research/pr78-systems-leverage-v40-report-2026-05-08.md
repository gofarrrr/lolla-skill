# PR78 v40 Systems Leverage Split Report

Date: 2026-05-08

## Scope

PR78 continues dormant reviewed-substrate enrichment. It does not change `/lolla`, runtime lane pickup, packet rendering, prompts, Observatory surfaces, or product behavior.

This ring focused on the systems / constraints / leverage cluster surfaced by the PR77 next-ring audit.

Modified records:

- `constraints`
- `leverage-points`
- `bottlenecks`

Read as PASS / no code change in this ring:

- `feedback-loops`
- `delays`
- `systems-thinking`
- `butterfly-effect`
- `chaos-theory`
- `non-linear-dynamics`
- `emergence`
- `self-organization-and-emergent-order`

The complexity-family hardening items remain good future candidates, but this PR keeps the ring smaller and auditable.

## Verdict

PASS as dormant reviewed substrate.

Compiled v40:

- Records: 222
- Affordances: 276
- Absence records: 514
- Schema failures: 0
- Source quote rejections: 0
- Status: `draft_review_only`

## What Changed

### Constraints Split

The prior `constraints.scope-boundary-decision-filter` carried two different receiver jobs:

1. define the current scope boundary and deliberate exclusions;
2. stress-test whether a constraint still fits the current environment.

PR78 replaces it with two narrower affordances.

`constraints.scope-boundary-exclusion-filter`

Use when the receiver needs to create a usable boundary around scope, success, trade-offs, and deliberate exclusions.

Key source support:

- `boundary, rule, or limitation that defines the functional scope, responsibilities, or acceptable parameters of a system, problem, or endeavor`
- `Most useful when** a team is losing clarity because too many goals, variables, or stakeholders are competing for attention at once.`
- `success depends on explicit boundaries around scope, acceptable trade-offs, and what the current effort will deliberately exclude.`
- `If this was cut, would anything be lost?`

`constraints.constraint-fit-stress-test`

Use when the receiver needs to test whether an inherited or proposed constraint is stale, loose, over-tight, over-engineered, or hiding important factors outside the frame.

Key source support:

- `Danger when** old constraints remain unquestioned after the economics, technology, or stakeholder environment has changed.`
- `Danger when** constraints are written so loosely that they create false confidence in control, or so tightly that they choke off signal, adaptation, or learning.`
- `Frameworks, by nature, tell us what to pay attention to, and thus what to ignore.`
- `When a constraint or framework is applied, ask **"What would you have to believe?"** to accept this frame.`

### Leverage Points Splits

The prior `leverage-points.hypothesis-bounded-analysis` carried two transactions:

1. what evidence is enough to test the hypothesis;
2. whether the current activity should stop, continue, or be deferred.

PR78 replaces it with:

`leverage-points.minimal-fact-threshold`

Use when a candidate leverage hypothesis exists and the receiver must limit evidence gathering to the smallest fact set that proves, disproves, supports, or refutes it.

`leverage-points.focus-check-stop-continue`

Use when leverage work is already underway and the receiver must decide whether the current activity still solves the problem, advances thinking, and remains the most important next move.

The prior `leverage-points.resistance-bias-execution-hardening` also carried two transactions:

1. challenge whether the chosen point is a familiar/preferred/biased frame;
2. plan how to execute a high-resistance leverage intervention.

PR78 replaces it with:

`leverage-points.assumption-antithesis-test`

Use when the leverage choice may be captured by familiar-frame substitution, confirmation bias, Maslow-style tool bias, motivated reasoning, or missing outside-view evidence.

`leverage-points.execution-resistance-plan`

Use when the leverage point is selected but high-resistance implementation still needs an execution path, resistance map, and adverse-scenario check.

This is the main quality gain of the PR: the future packet can now let a receiver use, reject, or defer each part independently rather than treating “bounded analysis,” “focus,” “bias challenge,” and “execution resistance” as one blended card.

### Bottlenecks Hardening

`bottlenecks.binding-constraint-throughput-check`

No new bottlenecks affordance was added. The current throughput-limiter card is the right owner. PR78 adds the treatment requirement:

- `plan-how-to-relieve-constraint`

The receiver must now state how the constrained step will actually be relieved, not merely identify the bottleneck.

Key source support:

- `overlooking the difficulty of figuring out *how* to execute the solution`

## PASS / No Change

`feedback-loops`

PASS in this ring. The current record already has:

- closed-loop action signal;
- loop polarity intervention map;
- `collected-feedback-without-behavior-change`;
- `instant-linear-feedback-assumption`.

The audit recommendation to guard against instrumentation theater is already materially present.

`delays`

PASS in this ring. The current record already distinguishes useful waiting from avoidant delay and contains:

- `romanticized-waiting-affordance`;
- `instant-failure-read-affordance`;
- lag naming, response window, and overcorrection checks.

The audit recommendation is already materially present.

`systems-thinking`

PASS in this ring. Broad-card risk remains real, but changing it belongs in a dedicated complexity-family PR because it interacts with emergence, self-organization, chaos, butterfly-effect, and non-linear-dynamics.

## Why This Is Not Bloat

PR78 removes three compressed affordance IDs and adds six narrower ones. Net increase: three affordances.

The split criterion was transaction identity, not source richness:

- different activation conditions;
- different evidence required;
- different treatment;
- different misuse guards;
- different future use/reject/defer outcomes.

Where the source only sharpened an existing card, PR78 hardened treatment instead of adding a new positive affordance.

## Runtime Safety

v40 remains dormant reviewed substrate.

The PR78 test suite asserts that `affordances_v40` and `model_affordances_v40` are not imported by checked live runtime paths:

- `engine/system_b/__init__.py`
- `engine/system_b/pipeline.py`
- `engine/system_b/reasoning_substrate_packet.py`
- `engine/system_b/reasoning_substrate_packet_review.py`
- `scripts/run_pipeline.py`

No runtime pickup is introduced here.

## Verification

Focused verification should include:

```bash
pytest tests/test_pr78_v40_systems_leverage_splits.py tests/test_pr77_v39_incentive_boundary_enrichment.py tests/test_model_affordance_compiler.py
rg -n "affordances_v40|model_affordances_v40" engine scripts tests -g '*.py'
git diff --check
jq '.compile_metadata.validation' data/compiled/model_affordances/affordances_v40.json
```

Expected compiled metadata:

```json
{
  "schema_validation_failure_count": 0,
  "source_hash_failure_count": 0,
  "source_quote_rejection_count": 0
}
```

## Next Ring Candidates

The next useful ring should probably be the complexity-family guard set:

- `butterfly-effect`, `chaos-theory`, and `non-linear-dynamics`: no abstract complexity without a transmission path, monitor, checkpoint, or reversible bet-sizing rule.
- `emergence` and `self-organization-and-emergent-order`: no emergence language without minimal structure, goals, feedback, and guardrails.
- `systems-thinking`: keep broad structure-over-events material behind clear intervention and signal discipline.

That should stay dormant and source-custodied, with the same transaction-distinct split standard.

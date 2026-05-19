# Pre-Step-6 Off-Default Candidate Generator Boundary Proposal

Date: 2026-05-19

Status: docs-only research proposal. This does not implement a generator,
change runtime behavior, update `SKILL.md`, update `HOW_IT_WORKS.md`, wire
anything into `/lolla`, change product docs, add a bundle, add workers, add a
handoff mode, or promote rendered hybrid as default.

Related:

```text
research/pre-step6-replay-ledger-aggregate-readout-2026-05-18.md
research/pre-step6-selector-boundary-decision-memo-2026-05-19.md
research/pre-step6-autoresearch-operating-loop-2026-05-19.md
research/pre-step6-no-rendered-handoff-v1-readout-2026-05-19.md
research/pre-step6-generated-decline-evaluation-readout-2026-05-19.md
research/pre-step6-off-default-replay-readout-2026-05-18.md
research/pre-step6-mother-quiet-replay-readout-2026-05-18.md
research/pre-step6-founder-high-clutter-replay-readout-2026-05-18.md
research/pre-step6-founder-high-clutter-native-rejudge-readout-2026-05-19.md
research/pre-step6-negative-control-replay-readout-2026-05-19.md
research/pre-step6-negative-control-native-rejudge-readout-2026-05-19.md
```

## Question

After six static replay ledger records, including a native-confirmed
negative/control stop, what would a tiny future candidate generator be allowed
to do?

The answer is not:

```text
build a generator now
```

The answer is:

```text
if a generator is ever discussed, it must be off-default, evaluation-only, and
decline-first
```

This proposal is a containment document. Its job is to say how a future
candidate generator must stay humble before implementation can even be
considered.

## Evidence Basis

| Record | Result | Naturalness Debt | Lesson |
| --- | --- | --- | --- |
| PhD conflict | Rendered hybrid replay win | medium | Rendered can preserve unresolved Silva-vs-fallback tension and evidence gates. |
| Mother quiet | Rendered hybrid replay win | low | `no_extra_pressure` can preserve one caution without adding pressure machinery. |
| Founder high-clutter local | Rendered hybrid replay win | medium | Quiet receipts can demote duplicate/misfit pressure without deleting custody. |
| Founder high-clutter native rejudge | Rendered hybrid aggregate win, control tie by criterion count | medium | Rendered can survive a less-author-biased judge, but pays a source/lightness/unforcedness tax. |
| Consultant negative-control local | Control wins, rendered audit passes but `does_not_count` | medium | Rendered can be grounded and still not useful enough to count. |
| Consultant negative-control native rejudge | Control wins again, rendered wins only decision usefulness and ties conflict preservation | medium | Decline survives less-author-biased review; no-rendered must be first-class. |

Current aggregate shape:

```text
replay records: 6
rendered_hybrid replay wins: 4
control/raw/tie replay stops: 2
source/overclaim audit failures: 0
naturalness debt low: 1
naturalness debt medium: 5
naturalness debt high: 0
native/semi-blind judge records: 3
local-rubric records: 3
runtime/product promotion records: 0
```

The evidence supports a narrow claim:

```text
rendered hybrid can transport selected private pressure when that pressure would
otherwise be lost, misused, or overexposed
```

It also supports an equally important constraint:

```text
rendered hybrid can over-process cases where control is already short,
grounded, humane, and sufficient
```

## Decision

Current decision:

```text
docs_only_generator_boundary_proposal: allowed
generator_implementation: blocked
runtime_wiring: blocked
product_promotion: blocked
new_handoff_modes: blocked
bundle: blocked
workers: blocked
deterministic_selector_score: blocked
no_rendered_handoff: first_class_successful_output
decline_receipt: required_for_generated_declines
off_default_evaluation_only: required
```

This proposal does not authorize implementation. It defines the minimum boundary
any later implementation proposal would have to satisfy.

## Core Doctrine

The candidate generator must preserve the doctrine already established by the
replay ledger:

```text
deterministic code keeps custody
the LLM performs judgment
valid pressure is rejectable
rendered is not default
medium naturalness debt is a primary design constraint
```

The generator may produce a candidate surface for evaluation. It may not decide
what Step 6 should believe.

Operationally:

```text
candidate generation may decide whether to prepare a private surface
candidate generation may not decide final advice
candidate generation may not force Step 6 to use the surface
candidate generation may not treat valid nuance as public obligation
```

## Allowed Responsibilities

A future off-default candidate generator may do only custody and admission work:

```text
inspect archived control/raw/research artifacts
identify whether selected pressure might be lost, misused, or overexposed
produce a candidate rendered handoff only when pressure transport appears useful
decline generation when control/raw is likely enough
record a decline receipt when it declines
validate source refs, artifact refs, handoff mode, caps, and public-hygiene rules
keep generated artifacts inside replay/evaluation only
preserve product promotion and runtime blocks
```

The generator may package a candidate. It may not select truth.

## Forbidden Responsibilities

A future generator must never:

```text
decide final advice
decide which pressure is true
force Step 6 to use rendered pressure
promote rendered handoff into runtime
turn naturalness debt into a deterministic formula
turn valid nuance into an answer obligation
create new handoff modes
launch workers
create a reasoning bundle
update SKILL.md
update HOW_IT_WORKS.md
change product docs
wire into /lolla
```

Especially forbidden:

```text
if X >= 3 then generate rendered
```

That would be a deterministic selector score. This proposal explicitly rejects
that path.

## Consider Conditions

The generator should consider producing a rendered handoff only when there is a
specific pressure-transport reason.

Consider rendered when:

```text
control drops a live risk-if-ignored
control/raw would likely collapse an unresolved two-sided conflict
case has high clutter where duplicate/misfit pressure must be demoted
case has a quiet sentinel caution that must survive in plain language
raw-only carries useful pressure but leaks demoted machinery
raw-only risks overusing every valid artifact
there is a known source/overclaim risk that needs explicit custody
rendered can preserve pressure while reducing private residue
```

The admission question is not:

```text
can rendered add something?
```

It is:

```text
what important pressure is likely to be lost or misused without rendered?
```

If the answer is vague, the generator should decline.

## Decline Conditions

The generator should decline when the simpler answer path is already enough.

Decline rendered when:

```text
control is already short, grounded, and humane
the correct move is counsel-first, therapist-first, expert-first, or safety-first restraint
no strong missing pressure is observed
rendered would mainly add protocol, channel, or process detail
rendered would increase procedural feel without clear decision lift
naturalness debt is likely medium without clear payoff
private pressure would make the answer feel more engineered than wiser
control/raw ties rendered while staying shorter and more natural
```

The consultant negative-control records are the model:

```text
rendered passed source/overclaim audit
rendered preserved some useful decision nuance
control was still better for the situation
rendered did not count
replay decision was stop
```

That result is not a failure of the rendered surface. It is evidence that
decline must be normal.

## First-Class Decline Output

A future generator must be allowed to output:

```text
no_rendered_handoff
```

That output must validate as successful research behavior, not as a missing
artifact.

Proposed docs-only contract:

```text
no_rendered_handoff.v1
  outcome_type: no_rendered_handoff
  status: valid_research_decline
  case_id: string
  source_refs:
    control_or_current_answer_ref: string
    raw_answer_core_ref: string optional
    raw_artifact_handoff_ref: string optional
    comparison_ref: string optional
  decline_reason: one sentence
  control_sufficiency: one sentence
  missing_pressure_assessment: one sentence
  naturalness_debt_risk: low | medium | high
  expected_failure_if_forced: one sentence
  reactivation_condition: one sentence
  forbidden_followup:
    - no pressure card
    - no inspect_more
    - no worker path
    - no new handoff mode
  product_promotion_allowed: false
  runtime_wiring_allowed: false
```

This is not an implemented schema. It is the minimum shape a future proposal
would need before implementation discussion.

The receipt should explain demotion or decline. It should not become a hidden
answer plan.

Good decline receipt:

```text
Control already gives the safe counsel-first move; rendered would mainly add
channel/protocol detail and medium naturalness debt without enough decision lift.
```

Bad decline receipt:

```text
The correct answer is control because counsel-first beats decision usefulness.
```

The first keeps custody. The second starts judging the final answer.

## Candidate Rendered Output

If the generator does not decline, it may only propose one of the existing
research surfaces:

```text
card_first
no_extra_pressure
```

It may not create:

```text
clutter_reduction
quiet_replay_mode
mother_mode
safety_mode
selector_mode
negative_control_mode
```

For `card_first`, the generator must keep the smallest viable surface:

```text
one pressure card unless explicitly justified
inspect_more only for named contested/lossy nuance
quiet_receipts only for demoted duplicate/misfit artifacts
hard caps preserved
source refs preserved
discard/relax conditions preserved
```

For `no_extra_pressure`, the generator must keep the surface quiet:

```text
no pressure card
no inspect_more
quiet guidance only
one to three specific obligations maximum
no extra theory
```

## Replay Ledger Evaluation

Generated candidates and generated declines must be evaluated by replay, not
promoted.

For a generated rendered candidate:

```text
run semi-blind or native/semi-blind comparison against control and raw-only
run source/overclaim audit if rendered wins or if rendered is being studied
record naturalness debt
record whether rendered counts or does_not_count
block product promotion
block runtime wiring
```

For a generated decline:

```text
record no_rendered_handoff receipt
compare control/raw against what rendered would have been expected to add, if known
allow the replay decision to count the decline as healthy if simpler arms win or tie
record a miss if later review finds a live pressure was lost
block product promotion
block runtime wiring
```

A generated decline should be considered healthy when:

```text
control/raw remains short, grounded, humane, and sufficient
no critical pressure was lost
the receipt names a clear reactivation condition
the system avoids medium/high naturalness debt without losing decision quality
```

A generated decline should be considered a miss when:

```text
control/raw drops a live risk-if-ignored
an unresolved conflict collapses too early
a quiet sentinel caution disappears
raw-only leaks demoted machinery
the receipt hides a deterministic verdict
```

## Naturalness Debt Constraint

Five of six rendered audits currently carry medium naturalness debt.

That means a future generator must be biased toward decline unless there is a
clear pressure-transport payoff.

Rules:

```text
high naturalness debt blocks replay win
medium naturalness debt requires visible decision-quality gain
medium naturalness debt plus weak decision lift should produce stop or retest
low naturalness debt is helpful but not promotion evidence
```

Do not convert naturalness debt into a numeric selector. It is a research brake,
not a formula.

## Evidence Gates Before Implementation Discussion

Generator implementation remains blocked until a later proposal answers all of
these:

```text
How does no_rendered_handoff validate as a first-class successful output?
How does the decline receipt avoid becoming a hidden answer plan?
How are generated declines replayed and judged?
How are source refs and answer refs checked for custody drift?
How are medium-debt candidates stopped when decision lift is weak?
How is off-default evaluation enforced in tests?
How does the generator avoid new modes, workers, bundles, and runtime wiring?
What cases would kill the generator path?
```

Minimum evidence before implementation can be discussed:

```text
at least one generated decline replay where decline is validated as healthy
at least one generated candidate replay where rendered wins and passes audit
at least one generated candidate replay where rendered does_not_count without schema bending
no product/runtime files touched
no new handoff modes required
naturalness debt pattern explicitly tracked
```

Even if those pass, the next discussion would be implementation of an
off-default research evaluator, not product integration.

## Non-Goals

This proposal explicitly does not do any of the following:

```text
does not implement no_rendered_handoff.v1
does not implement a generator
does not implement a selector
does not implement replay automation
does not add tests
does not change runtime
does not change public answers
does not change product docs
does not update SKILL.md
does not update HOW_IT_WORKS.md
does not add workers
does not add bundles
does not add modes
```

## PM Verdict

Docs-only generator boundary proposal is allowed because the native-confirmed
consultant stop proved decline is not just local-rubric preference.

Implementation is still blocked because the hard problem remains unsolved:

```text
can a future off-default process find both candidate and decline cases without
becoming a deterministic reasoner?
```

The next useful evidence is not a larger mechanism. It is either:

```text
a stricter no_rendered_handoff schema proposal with tests, still research-only
```

or:

```text
one generated-decline dry run, manually authored first, to see whether the
receipt helps evaluation without smuggling a hidden answer plan
```

Product promotion remains blocked. Runtime wiring remains blocked. Rendered
hybrid remains a research pressure-transport surface, not a default behavior.

2026-05-19 process follow-up:

```text
research/pre-step6-autoresearch-operating-loop-2026-05-19.md
```

Future rounds should use that loop: one narrow question, predeclared gates,
research-only edits, local validation, honest pass/tie/loss/stop readout, clean
commit, then the next question. The current next question is whether
`no_rendered_handoff` can validate as first-class successful output without
becoming another private pressure surface.

2026-05-19 no-rendered-handoff follow-up:

```text
research/pre-step6-no-rendered-handoff-v1-readout-2026-05-19.md
```

The first-class decline primitive now exists as a research-only validator,
fixture, and tests. It validates the consultant native negative-control stop as
`no_rendered_handoff`, while rejecting product promotion, runtime wiring,
generator implementation, missing decline evidence, case-ref drift, and obvious
hidden answer-plan language. Generator implementation remains blocked.

2026-05-19 generated-decline evaluation follow-up:

```text
research/pre-step6-generated-decline-evaluation-readout-2026-05-19.md
```

The no-rendered decline can now be evaluated as a healthy decline using simpler
raw/control comparison evidence, without requiring a rendered candidate or a
source/overclaim audit for the decline itself. This strengthens the decline
path, but still does not authorize generator implementation.

# Pre-Step-6 Next Slice Decision Note

Date: 2026-05-16

Status: research planning only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Central system-plan handover:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
```

## Decision

Do not start by implementing workers.

Start with a comparison-first research slice that asks whether an indexed
`reasoning_bundle.v1` actually improves Step 6-style consumption over raw
compact artifacts.

The next slice is:

```text
archived or curated case
  -> manually assembled raw reasoning_artifact.v1 specimens
  -> manually assembled reasoning_bundle.v1 index
  -> Step-6-style comparison:
       current control
       raw artifacts
       indexed bundle
  -> short readout with win/tie/loss and kill decision
```

No subagent calls are required for this slice. No OpenRouter calls are required
unless a later audit needs a strict JSON/source-overclaim check.

## Why This Comes Before Implementation

The core risk is not that we cannot define a schema. The core risk is that the
schema and bundle make private notes more organized while doing little or
nothing for the final answer.

The first question is therefore:

```text
Does a bundle index help the final reasoner use, demote, preserve, or reject
pressure better than raw compact artifacts?
```

If the answer is no, then building a `reasoning_workpack.v1` builder, subagent
prompt builders, and worker-output converters would only make the system larger.

## What This Slice Tests

Test the handoff value, not producer quality.

In this slice, hand-authored `reasoning_artifact.v1` specimens are acceptable
because the point is to isolate whether Step 6 benefits from the bundle shape.
They are not evidence that subagents can reliably produce those artifacts.

Questions:

- Does the indexed bundle reduce duplicate pressure amplification?
- Does it preserve real conflict better than raw artifacts?
- Does it help Step 6 honor hard boundaries and relaxation conditions?
- Does it make quiet/discard artifacts easier to ignore without losing receipts?
- Does it make the final answer clearer, shorter, or better grounded?
- Does it avoid machinery leakage in public prose?

## Strong Controls

Every case must compare against:

```text
current control
raw artifacts without bundle index
indexed reasoning_bundle.v1
```

The indexed bundle only wins if it improves final-answer quality, not merely the
operator's private sense of order.

If raw artifacts tie the indexed bundle, raw artifacts win.

If the current control ties both, no new handoff wins.

## Case Selection

Minimum useful set: 3 cases.

Better set: 5 cases.

The cases should be selected by reasoning shape, not topic:

```text
1. artifacts duplicate each other
2. artifacts conflict or create unresolved tension
3. a hard boundary is attractive to relax but should survive
4. one artifact is correct but low marginal value
5. one artifact tempts overclaim
```

At least one case should be a "worker should not run" case where the best
answer is no added cognition.

Sources may come from archived runs, existing research cases, or the local WIP
branch, but only after curating the minimum fixture material into the clean
research branch. Do not import the whole experiment pile.

## Fixture Inputs

Each case should keep inputs small:

```text
case_id
user_question
decision_situation
live_constraints
current_control_context
2-5 reasoning_artifact.v1 specimens
optional source excerpts, max 4
one reasoning_bundle.v1 index
```

The fixture should not include:

```text
full transcript
all lane cards
all V60 chunks
old workpack/dossier scaffolding
public machinery prose
```

## Evaluation Rubric

Score each arm as win, tie, or loss against the others.

Primary criteria:

- final answer preserves source-grounded force;
- unsupported precision decreases;
- hard boundaries survive unless relaxation facts are present;
- conflicts remain visible when unresolved;
- duplicates are demoted rather than amplified;
- quiet artifacts do not bloat the answer;
- no lane, worker, bundle, V60, chunk, ledger, packet, or internal model
  language leaks into public prose;
- answer is at least as clear as control and preferably shorter.

Secondary criteria:

- private handoff is easier to audit;
- artifact IDs remain traceable;
- overclaim risks are visible before final writing;
- Step 6 remains free to reject the bundle.

The indexed bundle does not win on secondary criteria alone.

## Win Standard

Proceed to implementation only if:

- the indexed bundle beats raw artifacts in at least two high-clutter cases;
- it does not lose any hard-boundary or overclaim case;
- it does not make answers longer by default;
- the improvement is visible in final prose, not only private reasoning notes;
- the result identifies exactly which bundle fields carried the lift.

If the indexed bundle mostly ties raw artifacts, implement raw-artifact
rendering discipline first or stop.

## Kill Conditions

Kill or pause the bundle path if:

- raw artifacts perform as well as the indexed bundle;
- the bundle hides conflict by making one artifact look primary too early;
- Step 6 obeys the index instead of arbitrating;
- the final answer becomes more caveated, longer, or less direct;
- the bundle requires broad context to be useful;
- the only observed benefit is nicer operator traceability;
- fixture authors cannot explain why a no-worker Step 6 would miss the pressure.

Treat a killed path as a successful research outcome if it prevents unnecessary
runtime complexity.

## What Not To Build Yet

Do not build yet:

- subagent worker prompt builders;
- live worker orchestration;
- `/lolla` integration;
- product doc updates;
- automatic worker admission;
- OpenRouter final synthesis;
- broad Bevelin packet injection;
- a generic "reasoning worker" abstraction.

## If The Slice Wins

Only after a comparison win, build the smallest implementation slice:

```text
reasoning_artifact.v1 fixture schema
reasoning_bundle.v1 fixture schema
bundle renderer for Step-6-style consumer
local comparison runner
```

Then, and only then, consider `reasoning_workpack.v1` builder validation and the
two worker prompt builders from the core plan:

```text
boundary/evidence-gate worker
duplicate/priority worker
```

## Operator Rule

The next good answer is allowed to be:

```text
The bundle did not earn its keep.
```

That outcome is better than promoting attractive machinery that does not improve
the user's final answer.

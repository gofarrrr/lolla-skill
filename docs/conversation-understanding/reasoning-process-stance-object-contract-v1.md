# Reasoning-process stance-object contract v1

Status: provider-free design input  
Date: 2026-07-12

## Failure being addressed

Modal-strength v3 attached one force label to each starting and current
position. The fresh Case-03 probe showed two distinct failures:

- a strongly worded assessment was mislabeled as a decision;
- one sentence contained a definite plan to make a proposal and uncertainty
  about accepting the proposal, which one label could not represent.

The repair target is the stance object, not a stronger warning about force.

## Representation

The existing starting, current, qualification, and trajectory interpretations
and exact evidence IDs remain. Position records replace the v3 whole-role force
labels with one `stance_components` array. Each component names its
`temporal_role` as `starting`, `current`, or `qualification`. Runtime limits are
zero to three starting components, one to four current components, and one to
three qualification components. Starting components are empty only when the
existing starting role is absent. One array avoids repeating a deep schema
three times while preserving role custody.

Each component contains:

- `temporal_role` — which existing evidence role the component belongs to;
- `stance_object_kind` — what the stance is about;
- `stance_object_interpretation` — a concise source-faithful description of
  that object;
- `stance_expression_kind` — how the source positions the speaker toward that
  particular object;
- `source_evidence_ids` — exact aliases supporting this component, mechanically
  restricted to the parent role's evidence IDs.

Object kinds are:

- `belief_or_assessment`;
- `action_or_proposal`;
- `intended_outcome_or_policy`;
- `acceptance_or_willingness`;
- `reported_position_landscape`;
- `unclear`.

Expression kinds are categorical descriptions, not scores or an ordinal
ladder:

- `reported_without_endorsement`;
- `uncertain_or_undecided`;
- `considering`;
- `held_assessment`;
- `preference_or_desire`;
- `leaning`;
- `proposal`;
- `provisional_intention_or_plan`;
- `decision`;
- `commitment`;
- `willing`;
- `unwilling`;
- `conditional_willingness`;
- `possibility`;
- `constraint`;
- `counterpressure`;
- `unclear`.

`stance_object_fidelity_note` explains how the decomposition avoids conflating
different objects.

## Semantic instructions

The model must identify the object before classifying the expression toward
it. In particular:

- confidence or intensity in a belief or assessment is not a decision;
- `decision` requires a chosen action, course, or outcome;
- deciding or intending to make a proposal is distinct from willingness to
  accept the proposal's outcome;
- reported positions of other people or a group do not imply user endorsement;
- when one sentence expresses stances toward multiple objects, components must
  be split even when they share the same evidence alias;
- prose and categorical expression must preserve uncertainty, conditions,
  provisionality, and counterpressure.

These are semantic responsibilities of the model and source reviewer. They are
not deterministic pair rules.

## Deterministic authority

Code may enforce only:

- required fields, enums, array bounds, uniqueness, and string bounds;
- starting-component presence matching the existing starting role's mechanical
  presence;
- at least one current and one qualification component;
- component evidence aliases being non-empty unique subsets of the parent
  role's already validated evidence IDs;
- existing source-region, identity, hash, budget, and record-custody rules.

Code may not:

- infer object or expression kinds from words;
- enforce a semantic object/expression compatibility table;
- compare expressions as stronger or weaker;
- reject a record because chronology appears to move backward;
- merge components semantically;
- treat component count or labels as quality, trust, depth, or effort evidence;
- repair a semantic mismatch silently.

An enum-valid but source-wrong component must remain structurally admissible
and visibly reviewable.

## Prospective boundary

Completed Case-01, Case-02, Case-03, and Case-05 position probes are closed.
Their sources may be used provider-free to test representation, but their
prompts may not be tuned and no provider retry is allowed. Only a
prospectively frozen Case-04 position probe may follow, and only after corpus,
adversarial, regression, and cold-reader gates pass.

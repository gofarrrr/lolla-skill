# Modal and commitment-strength fidelity contract v1

Status: provider-free design input  
Date: 2026-07-12

## Problem

Role-explicit position fields corrected a missing-relationship failure, but the
first model probe promoted a stated preference into insistence and total
commitment. Exact evidence IDs and separate semantic roles do not by themselves
preserve modal force.

## Contract

Position records add four model-authored fields:

- `starting_position_force`;
- `current_position_force`;
- `qualification_modalities`;
- `strength_fidelity_note`.

Position-force labels describe source stance categories:

- undecided or ambivalent;
- considering;
- preference or desire;
- leaning;
- provisional plan;
- decision;
- commitment;
- unclear;
- not applicable when no starting state exists.

Qualification modalities describe possibilities, concerns or risks, unresolved
questions, conditions, constraints, counterpressure, or unclear status.

These labels are not numbers, scores, confidence levels, or an ordinal ladder.
Code may not compare them or infer them from keywords. The model selects them
from visible source context and must explain in `strength_fidelity_note` why its
paraphrase preserves the source's modal and commitment force.

## Deterministic authority

Code may enforce only:

- required enum membership;
- `not_applicable` if and only if starting interpretation and evidence are both
  absent;
- current force cannot be `not_applicable`;
- at least one qualification modality;
- non-empty strength-fidelity note;
- existing source-region, schema, identity, budget, and record-custody rules.

Code may not:

- scan prose for words such as *want*, *lean*, *must*, or *decide*;
- decide which label is semantically correct;
- treat labels as a quality or trust score;
- reject a record because a supposedly “stronger” label follows a “weaker” one;
- repair a modal mismatch silently.

Semantic force accuracy remains a source-first review question.

## Prospective boundary

The completed Case-05 prompt and output remain frozen. Provider-free fixtures
may use that case to test representation, but no same-case repair or provider
call is allowed. A future model probe must use a mechanically selected fresh
position-reader case and remain one call until source review completes.

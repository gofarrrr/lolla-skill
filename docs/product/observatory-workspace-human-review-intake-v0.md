# Observatory Workspace Human Review Intake v0

Status: implemented deterministic intake validator
Date: 2026-07-06
Decision gate: `ready_to_validate_human_review_response`

## Purpose

This slice adds a deterministic intake validator for the Observatory workspace
human review form created in the user review packet.

The validator does not perform review. It checks whether a human-filled review
form is complete enough and safe enough to use as input for the next product
planning gate.

The reason for this slice is simple:

```text
blank review form -> still blocked
completed review form -> choose the next revision gate
unsafe review form -> repair before use
```

Put another way: blank forms remain blocked, completed forms may plan revision
work, and unsafe forms must be repaired before they can influence the next gate.

## What It Validates

The intake validator checks:

- expected human review form schema;
- completed human review status;
- reviewed workspace case, run, date, and reviewer fields;
- overall decision;
- first-impression notes;
- progression review;
- all six surface reviews;
- information-hierarchy review;
- non-claims review;
- boundary and non-claim flags.

The six required surfaces remain:

```text
Outcome -> Learn -> Models -> Relations -> Map -> Receipts
```

## Gate Behavior

Blank forms remain blocked with:

```text
blocked_pending_human_review
```

Incomplete or malformed completed forms return:

```text
rejected_invalid_review_form
```

Unsafe forms with local paths or private markers return:

```text
blocked_privacy_risk
```

Forms that try to claim product proof, human validation, answer correctness,
advice correctness, graph-edge proof, relation certification, runtime
integration, or action authorization return:

```text
rejected_boundary_claim
```

Accepted completed forms may plan revision work only. They do not authorize
expansion or product-readiness claims.

Possible next gates include:

- `needs_first_screen_revision`;
- `needs_learn_revision`;
- `needs_model_page_revision`;
- `needs_relation_page_revision`;
- `needs_graph_map_ux_revision`;
- `needs_receipts_audit_revision`;
- `needs_review_packet_revision`;
- `needs_human_review_form_repair`;
- `needs_non_claims_revision_before_expansion`;
- `ready_to_plan_next_observatory_slice_with_human_caveats`.

## Boundary

This intake validator:

- does not complete human review;
- does not run Lolla;
- does not invoke the Lolla skill;
- does not call providers or model APIs;
- does not create new runs;
- does not mutate archives;
- does not write sidecars;
- does not wire runtime behavior;
- does not edit `observatory/build`;
- does not claim product proof;
- does not claim human validation;
- does not claim answer correctness;
- does not claim advice correctness;
- does not authorize action;
- does not treat graph edges as proof;
- does not treat relation confidence as certification.

## Implementation

Implemented module:

```text
engine/system_b/observatory_workspace_human_review_intake.py
```

Focused tests:

```text
tests/test_observatory_workspace_human_review_intake.py
```

The validator is intentionally not wired into Observatory runtime. It can be
used by a later operator command, review pipeline, or PR slice after a human has
actually filled the review form.

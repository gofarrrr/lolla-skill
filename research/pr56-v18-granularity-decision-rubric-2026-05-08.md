# PR56 v18 Granularity Decision Rubric

Date: 2026-05-08

Branch: `feature/knowledge-substrate-pr56-source-adequacy-audit`

Status: review-only rubric

## Purpose

This rubric decides whether a v18 record is adequately compressed or whether the source supports targeted enrichment.

It exists to avoid both failure modes:

- leaving useful source-backed cognition on the table;
- expanding the knowledge base into decorative mental-model bulk.

## Unit Of Extraction

The extraction unit is a downstream reasoning transaction, not an interesting paragraph.

A separate affordance is justified only when the source-supported material would cause a receiver to behave differently:

- use this material;
- reject it;
- defer it pending evidence;
- merge it with another affordance;
- block it using absence/misuse evidence;
- ask a different diagnostic question;
- require a different treatment in the final answer.

## Verdict Labels

Use one or more labels per reviewed model.

| Label | Meaning |
| --- | --- |
| `complete_as_compressed` | Current record captures the source's operational bite at the right granularity. |
| `split_candidate` | Current record may contain multiple transaction-distinct operational moves. |
| `needs_absence_enrichment` | Positive affordance may be fine, but absence/misuse/unsupported-field records are too thin. |
| `needs_affordance_rewrite` | Existing affordance is source-backed but normalized at the wrong level or mixed with a sub-affordance. |
| `source_too_thin` | Source does not support richer extraction; do not expand for symmetry. |
| `too_broad_for_runtime` | Card is source-backed but broad enough to over-authorize itself in live handoff. |
| `packet_shape_blocker_only` | Record may be adequate, but current packet flattening would still lose identity or guards. |
| `weak_support_confirmed` | Current weak/medium posture is appropriate and must not be cosmetically upgraded. |

## Split Candidate Test

A model becomes a `split_candidate` only if the reviewer can fill this proof:

```text
candidate_new_affordance:
source_cluster:
source_lines:
current_v18_coverage:
different_use_when:
different_case_evidence_needed:
different_do_not_use_when:
different_treatment_requirement:
different_misuse_guard:
different_receiver_action:
why_not_just_supporting_detail:
```

If any "different" field is weak, do not split yet.

## Complete-As-Compressed Test

Mark `complete_as_compressed` when:

- the source has one dominant operational move;
- apparent extra material is example, elaboration, or caution around that move;
- current `use_when`, `do_not_use_when`, and `case_evidence_needed` cover the decision boundary;
- treatment requirements are specific enough to change output behavior;
- dropped material is explained or belongs to another model.

High source-reference count does not automatically mean under-extraction. It can also mean one strong affordance is well-supported.

## Absence Enrichment Test

Mark `needs_absence_enrichment` when:

- the source contains clear unsupported or dangerous uses;
- current absences are zero or miss a major source warning;
- the model is broad/meta enough that absence records would likely prevent overclaiming;
- a weak-support record needs a visible "do not promote" rail;
- misuse guards exist but are too easy to hide in a compressed packet.

Absence enrichment is often better than adding another positive affordance.

## Rewrite Test

Mark `needs_affordance_rewrite` when:

- the source supports the move, but the affordance is named or scoped at the wrong level;
- a sub-affordance is presented as a peer affordance;
- multiple treatment requirements are bundled into a shape the receiver cannot audit;
- the current affordance would be hard to use/reject/defer as one unit.

Do not rewrite in PR56. PR56 should identify the issue and defer actual record changes to a targeted v19 PR.

## Source-Too-Thin Test

Mark `source_too_thin` when:

- source mentions a topic only generically;
- the source is mostly adjacent mental-model material rather than the named model;
- richer extraction would require inference from outside the source;
- source quotes validate the existing weak card but not a stronger one.

This is a success condition, not a failure. It prevents fake completeness.

## Broad/Meta Runtime Test

Mark `too_broad_for_runtime` when:

- the card could sound relevant to almost any reasoning task;
- model naming itself may look like judgment;
- broad terminology could crowd out narrower case-specific cards;
- the card requires especially visible absence, confidence, or treatment rails.

Broad/meta records are not bad. They just need stricter pickup and display discipline.

## Decision Order

For each source-read record:

1. List operational clusters in the source.
2. Map each cluster to current affordances, absences, guards, or dropped material.
3. Apply `complete_as_compressed` if one transaction covers the source.
4. Apply `needs_absence_enrichment` before proposing positive splits.
5. Apply `split_candidate` only with transaction-distinct proof.
6. Apply `source_too_thin` when expansion would be inference.
7. Apply `packet_shape_blocker_only` when extraction is fine but handoff is not.

## Bottom Line

The standard is not more knowledge.

The standard is right-granularity knowledge with traceable source support and enough absence pressure to stop the receiver from overclaiming.

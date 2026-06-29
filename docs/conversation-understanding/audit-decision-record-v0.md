# Audit Decision Record v0

Status: PR58 docs/JSON design
Date: 2026-06-28
Owner: Lolla maintainers

PR58 designs `lolla.audit_decision_record.v0` as a local accountability
projection over existing Lolla artifacts.

The record is meant to help reviewers see what decision a run audited and what
changed between the original and revised recommendation. It is not a new
runtime behavior, exporter, judge, score, memory layer, or conversation
understanding IR.

## Problem

Lolla already preserves strong deterministic custody around a probabilistic
reasoning audit: local archives, `agent_result.json`, `evaluation.json`,
`reasoning_trace.json`, review-corpus exports, manifests, and human review
records. Those artifacts are intentionally honest, but they can still be slow
to inspect when the reviewer asks a product question:

```text
What decision changed, and why should I believe this was more than smoother
prose?
```

The audit decision record answers that question as a compact review projection.
It should make the decision delta visible without claiming to understand the
whole conversation or proving answer quality.

## Inspiration

The [Semantica-inspired accountability PRD](semantica-inspired-accountability-prd-v0.md)
identified first-class decision records as a useful primitive to borrow.
Lolla borrows the accountability discipline, not Semantica's platform scope.

The record stays local, run-scoped, review-owned, and paraphrase-only. It does
not create a graph database, memory system, policy engine, hosted API, or
general context layer.

## Why This Is Useful

The decision record gives reviewers and future evals a smaller surface to read
before they inspect the full artifact set.

It is useful because it:

- lets reviewers see the decision delta faster;
- maps the delta to the PR31 actionable-delta labels;
- preserves unresolved values, stakeholder conflicts, and user questions;
- helps future fixture reviews ask whether the record captures the meaningful
  change;
- helps avoid the common mistake that clean custody artifacts mean good advice;
- keeps answer-quality judgment and reliance labels human-owned.

## Record Shape

Schema version:

```text
lolla.audit_decision_record.v0
```

Design example:

- [audit-decision-record-v0.json](audit-decision-record-v0.json)

High-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Fixed string: `lolla.audit_decision_record.v0`. |
| `case_id` | Compact case identifier already safe for review surfaces. |
| `run_id` | Compact run identifier already safe for review surfaces. |
| `archive_relpath` | Relative archive reference only. No checked-in local absolute paths. |
| `decision_question` | Paraphrased decision the run appears to audit. |
| `original_recommendation_summary` | Paraphrased read of what the original answer appeared to favor. |
| `revised_recommendation_summary` | Paraphrased read of what the revised answer changed. |
| `actionable_deltas` | PR31 label buckets with compact paraphrase-only evidence. |
| `values_or_stakeholder_conflicts` | Conflicts preserved for human review, not resolved by the record. |
| `unresolved_questions` | Questions still requiring the user, stakeholder, or reviewer. |
| `source_artifacts` | Local artifact references and what they support, without copying raw content. |
| `review_refs` | Pointers to human-owned review records or docs. |
| `custody_flags` | Booleans proving excluded raw/private content stayed excluded. |
| `limitations` | Explicit caveats and non-claims. |

## Status And Grounding Vocabularies

Decision and recommendation summaries use these `status` values:

- `present`: enough artifact or review context exists to summarize the field.
- `partial`: the field is inferable but incomplete or caveated.
- `missing`: the field cannot be responsibly summarized.
- `not_measured`: the field was intentionally not measured in this record.

The `decision_question` field does not use `not_measured`; if it cannot be
summarized, it should be `missing` or `partial`.

Grounding values:

- `artifact_present_only`: the record can say the supporting artifact exists,
  but it does not derive semantic claims from it.
- `turn_ref`: a future exporter may point to safe turn references without
  copying text.
- `span`: a future exporter may point to a safe span reference without copying
  text.
- `derivation`: the value is a paraphrase derived from existing reviewed
  artifacts or human-review summaries.
- `none`: no grounding is available.

PR58 does not implement span extraction or an exporter. The vocabulary exists
so PR59 fixture review can test whether the shape is understandable before any
code writes records.

## Actionable Delta Mapping

The `actionable_deltas` object uses the PR31 labels from
[Actionable Delta Rubric v0](../evals/actionable-delta-rubric-v0.md):

- `action_changed`
- `threshold_changed`
- `sequence_changed`
- `evidence_gate_added`
- `stop_rule_added`
- `written_term_added`
- `user_question_added`
- `scope_narrowed`
- `overclaim_retracted`
- `no_op_prose_change`

Each populated label should explain the action, gate, sequence, written term,
question, scope change, or overclaim retraction in paraphrase. Empty arrays are
meaningful: they say the label was not observed or not claimed for that record.

`no_op_prose_change` is included so reviewers can explicitly preserve the
negative case where a revision sounds better but changes no decision-relevant
action.

## Source Artifacts And Custody

The record may reference local artifact names and relative archive references,
for example:

- `agent_result.json`
- `evaluation.json`
- `reasoning_trace.json`
- `extraction_adequacy_report.json`
- human review JSON or docs

It must not copy raw transcript, memo, revised-answer text, provider/model
text, private reasoning, credential values, or checked-in local absolute paths.

The record's custody flags must remain false for:

- `raw_transcript_included`
- `raw_memo_included`
- `raw_revised_answer_included`
- `provider_text_included`
- `private_reasoning_included`
- `local_absolute_paths_included`

If a future exporter cannot explain a field without copying excluded content,
it should mark the field `missing` or `partial` instead of weakening custody.

## Example Read

The PR58 JSON example uses the already reviewed
`ceo-remove-founding-cofounder` case. It paraphrases the documented review
finding that the revision moved from cooperation/reset language toward
authority transfer, bounded transition terms, and stop-loss rules.

The example does not inspect or copy archive payloads in this PR. It is a
schema/example artifact for review, not generated output.

## Explicit Non-Goals

PR58 does not add or approve:

- an exporter;
- runtime integration;
- `$lolla` runs;
- model calls;
- archive mutation;
- prompt changes;
- `SKILL.md` changes;
- provider-boundary policy changes;
- `caller_action` changes;
- high-stakes runs;
- raw transcript inclusion;
- raw memo inclusion;
- raw revised-answer inclusion;
- provider/model text inclusion;
- private reasoning inclusion;
- checked-in local absolute paths;
- answer-quality scoring;
- LLM judges;
- automatic human-review labels;
- automatic `safe_for_agent_use`;
- user memory;
- `conversation_understanding_ir.v0`;
- graph DB;
- embeddings;
- chunking;
- memory;
- policy engine;
- Semantica-style platform work.

## Why This Is Not `conversation_understanding_ir.v0`

The audit decision record is narrow. It summarizes one reviewed decision delta
for accountability and evaluation.

It does not attempt to represent every turn, entity, claim, user value,
constraint, topic, stance, memory, or causal relation in the conversation. It
does not become a substrate for agent planning. It is a review projection over
artifacts that already exist.

## Why This Is Not Answer-Quality Scoring

The record can say what changed. It cannot decide that the changed advice is
good, safe, domain-approved, or ready for autonomous use.

Human reviewers still own:

- whether the revised answer improved the decision surface;
- whether useful friction was present;
- whether noisy or missing friction exists;
- whether `safe_for_agent_use` is `yes`, `no`, or `with_human_review`;
- whether a future judge has enough calibrated evidence to exist.

## PR59 Fixture Review

PR59 completed the first fixture review for this shape:

- [Audit Decision Record Fixtures v0](../evals/audit-decision-record-fixtures-v0.md)
- [audit-decision-record-fixtures-v0.json](../evals/audit-decision-record-fixtures-v0.json)
- [review.json](../../reviews/human/audit-decision-record-fixture-review-v0/review.json)

The review covers six paraphrase-only fixture records from existing reviewed
cases. All six pass, PR31 mapping is useful in all six, and reviewers can use
the records without raw content in all six. The review marks the shape ready for
a future read-only exporter design prototype with caveats.

This does not approve an exporter. The next recommended slice is PR60
Provenance Map Design v0 only after maintainer review of PR57 through PR59.
Any future exporter still needs a separate gate and must remain raw-content
safe, local, deterministic, and human-review-owned.

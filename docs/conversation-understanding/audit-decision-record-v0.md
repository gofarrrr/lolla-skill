# Audit Decision Record v0

Status: PR58 docs/JSON design; PR66 read-only exporter implemented; PR67 smoke-reviewed
Date: 2026-06-28
Owner: Lolla maintainers

PR58 designs `lolla.audit_decision_record.v0` as a local accountability
projection over existing Lolla artifacts.

PR66 implements a narrow read-only exporter for this schema:
[Audit Decision Record Read-Only Exporter v0](../evals/audit-decision-record-readonly-exporter-v0.md).

PR67 reviews smoke exports from that exporter:
[Audit Decision Record Export Smoke Review v0](../evals/audit-decision-record-export-smoke-review-v0.md).

The record is meant to help reviewers see what decision a run audited and what
changed between the original and revised recommendation. It is not a new
runtime behavior, judge, score, memory layer, or conversation understanding IR.

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

PR58 did not implement span extraction or an exporter. The vocabulary existed
so PR59 fixture review could test whether the shape was understandable before
any code wrote records. PR66 now implements only a conservative read-only
exporter; it does not add span extraction, raw transcript reading, runtime
integration, labels, scoring, or judge behavior.

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

If the PR66 exporter cannot explain a field without copying excluded content,
it marks the field `not_measured`, `not_included`, or empty instead of
weakening custody.

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

This did not approve an exporter by itself. PR65 later chose the decision
record as the safest first implementation candidate, and PR66 now implements
that exporter as a local read-only tool. It remains raw-content-safe, local,
deterministic, and human-review-owned.

## PR63 Accountability View Fixtures

PR63 now tests the audit decision record inside combined accountability-view
bundles:

- [Accountability View Fixtures v0](../evals/accountability-view-fixtures-v0.md)
- [accountability-view-fixtures-v0.json](../evals/accountability-view-fixtures-v0.json)

Those fixtures use the decision record as one view beside provenance map,
review conflict register, and case graph views. They remain paraphrase-only
fixture evidence and do not implement an exporter, runtime artifact, labeler,
score, judge, graph DB, or memory layer.

## PR66 Read-Only Exporter

PR66 implements the first code-bearing audit decision record slice:

- [Audit Decision Record Read-Only Exporter v0](../evals/audit-decision-record-readonly-exporter-v0.md)
- [audit_decision_record.py](../../engine/system_b/audit_decision_record.py)
- [build_audit_decision_record.py](../../scripts/build_audit_decision_record.py)
- [test_audit_decision_record.py](../../tests/test_audit_decision_record.py)

The CLI shape is:

```bash
python3 scripts/build_audit_decision_record.py \
  --run-dir <run-dir> \
  --out /tmp/lolla_audit_decision_record.json
```

PR66 reads structured/custody-safe JSON surfaces only:
`evaluation.json`, `agent_result.json`, `reasoning_trace.json`,
`extraction_adequacy_report.json`, and optional `--review-json`. It does not
read or copy `conversation.txt`, `memo.md`, `revised.txt`,
`live_transcript.txt`, provider/model text, or private reasoning artifacts.

The exporter emits every PR31 actionable-delta bucket as a stable key but does
not infer labels from prose. Empty arrays are non-claims.

PR66 remains outside runtime behavior. It does not run `$lolla`, call models,
mutate archives, change prompts, change `SKILL.md`, change `caller_action`,
decide `safe_for_agent_use`, approve a domain recommendation, score answer
quality, add a judge, add memory, add graph DB, or implement the provenance,
conflict-register, or case-graph lanes.

## PR67 Export Smoke Review

PR67 reviews whether the PR66 exporter output is actually readable and humble:

- [Audit Decision Record Export Smoke Review v0](../evals/audit-decision-record-export-smoke-review-v0.md)
- [review.json](../../reviews/human/audit-decision-record-export-smoke-review-v0/review.json)

The review covers six exported records: four existing reviewed archives and two
fixture-backed temp runs. All six pass. Artifact statuses are useful in all
six, custody and limitations are clear in all six, raw content safety is safe in
all six, and false-certainty risk is none or low.

The review finding is narrow but important: empty PR31 buckets are safe because
the exporter does not infer labels from prose, but they are only partly clear in
real archive exports. A reader can mistake empty arrays for "no meaningful
delta" unless they notice the limitation that labels were not supplied or
inferred.

Recommended next slice:

```text
PR68 Audit Decision Record Schema/Exporter Refinement v0
```

PR68 should be approved separately and should clarify PR31 bucket population
policy before archive integration, batch export, or automatic generation.

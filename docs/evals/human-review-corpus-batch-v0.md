# Human Review Corpus Batch v0

Status: human/product review batch
Date: 2026-06-27
Review slice: `human_review_corpus_batch_v0`

PR33 applies the PR30 human-review workflow and PR31 actionable-delta rubric to
a broader local corpus batch.

The purpose is narrow. This slice does not run `$lolla`, call models, implement
a judge, score answer quality automatically, populate archive labels
automatically, change runtime behavior, change prompts, change `SKILL.md`, or
mutate archived runs.

The batch question is:

```text
Do the PR30 human-review labels and PR31 actionable-delta labels still make
sense when they touch more records than the six curated complex runs?
```

## Sources

This review used:

- [Human Review Workflow](human-review-workflow.md)
- [Human Review Schema v0](lolla-human-review-v0.json)
- [Failure Taxonomy](lolla-failure-taxonomy.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [Adversarial Pair Fixtures v0](adversarial-pair-fixtures-v0.md)
- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- [PR30 review JSON](../../reviews/human/complex-baseline-v0/review.json)

Machine-readable PR33 labels are stored in
[reviews/human/corpus-batch-v0/review.json](../../reviews/human/corpus-batch-v0/review.json).

Archive records are referenced by relative run path only. This note does not
copy raw transcript text, raw memo text, raw revised-answer text, model/provider
content, private reasoning content, local absolute paths, or credential
material.

## Batch Shape

The batch contains 14 records:

- six PR30 complex-run anchors;
- six additional full-modern, answer-level reviewable records;
- one older partial record as a `needs_followup` boundary sample;
- one degraded record as an `exclude_from_eval` boundary sample.

Twelve records are counted as positive answer-level eval evidence. Two records
are reviewed for boundary behavior but are not counted as positive eval
evidence.

The positive records all retain the familiar conservative reliance label:
`safe_for_agent_use: with_human_review`. The reason is not answer-level failure.
It is that saved artifacts were reviewable while `live_output_health` remained
`not_checked`. `evaluation.json` remains deterministic run-readiness, not
answer-wisdom scoring, and `caller_action: use_revised_answer` remains caller
guidance, not human approval.

## Method

For full-modern records, review considered:

- saved revised answer and memo, without copying their raw text;
- `agent_result.json` changed-advice summaries and conservative caller action;
- `evaluation.json` run-envelope readiness and caveats;
- `extraction_adequacy_report.json` extraction/provenance adequacy where
  present;
- `reasoning_trace.json` custody signals;
- quote validation and capture health when exposed by the reports.

Answer-level review is separate from:

- run-envelope and custody review;
- live-output hygiene review;
- agent-readiness review.

The older partial record was reviewed only as a boundary case. Its content
surface suggested an actionable delta, but it predates the modern
`agent_result.json`, `evaluation.json`, and extraction adequacy sidecars, so it
is `needs_followup` rather than a pass. The degraded record is
`exclude_from_eval` because the run envelope itself is not eval-ready.

## Review Table

| case / run | role | review_status | primary_failure_mode | useful / noisy / missing friction | improved | safe_for_agent_use | actionable_delta_labels | artifact_sufficiency | reviewer note |
|---|---|---|---|---|---|---|---|---|---|
| `ceo-remove-founding-cofounder` / `20260627T093131Z_59d153` | PR30 anchor | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `action_changed`, `sequence_changed`, `stop_rule_added`, `scope_narrowed` | `sufficient_with_caveat` | Founder-loyalty language becomes an authority-transfer plan with a real stop condition. |
| `accept-operations-role-startup` / `20260627T132700Z_bae7f3` | PR30 anchor | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `threshold_changed`, `evidence_gate_added`, `written_term_added`, `user_question_added`, `overclaim_retracted` | `sufficient_with_caveat` | A resonant career choice becomes a written-terms and household-capacity test. |
| `launch-public-enterprise-beta` / `20260627T104146Z_7bfe79` | PR30 anchor | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `written_term_added`, `scope_narrowed`, `overclaim_retracted` | `sufficient_with_caveat` | Enterprise aura becomes a same-shape paid-pilot proof test. |
| `pre-sell-undefined-consulting` / `20260627T133637Z_cad396` | PR30 anchor | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `action_changed`, `evidence_gate_added`, `written_term_added`, `scope_narrowed`, `overclaim_retracted` | `sufficient_with_caveat` | The safer answer keeps the paid-pilot constraint while separating client readiness from status spending. |
| `pivot-company-product-strategy` / `20260627T110450Z_5d2da7` | PR30 anchor | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `threshold_changed`, `sequence_changed`, `evidence_gate_added`, `written_term_added` | `sufficient_with_caveat` | Market-upside momentum becomes a capacity-and-obligation gate. |
| `deploy-assisted-intake-routing` / `20260627T130339Z_4cd3cb` | PR30 anchor | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `stop_rule_added`, `user_question_added`, `scope_narrowed` | `sufficient_with_caveat` | Checklist safety theater becomes a narrower pilot with controls that can stop the rollout. |
| `accept-founding-engineer-role` / `20260627T073034Z_a7c221` | broader modern | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `threshold_changed`, `sequence_changed`, `evidence_gate_added`, `stop_rule_added`, `written_term_added` | `sufficient_with_caveat` | A personal yes becomes necessary but not sufficient; the offer has to pass proof, role, and family gates. |
| `accept-high-intensity-startup` / `20260627T094533Z_e1e6fc` | broader modern | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `threshold_changed`, `evidence_gate_added`, `written_term_added`, `user_question_added`, `overclaim_retracted` | `sufficient_with_caveat` | Status-flavored confidence is replaced by written startup boundaries, current-company charter proof, and household load planning. |
| `five-person-saas-team-1` / `20260627T075430Z_a5ba14` | broader modern | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `threshold_changed`, `evidence_gate_added`, `user_question_added`, `scope_narrowed`, `overclaim_retracted` | `sufficient_with_caveat` | A lead-list ultimatum becomes a bounded proof package with shared partner evidence. |
| `implement-price-increase-three` / `20260627T083231Z_52724d` | broader modern | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `written_term_added`, `scope_narrowed` | `sufficient_with_caveat` | A broad price increase becomes account-level support economics with enforceable boundaries. |
| `initiate-pre-sale-coffee-1` / `20260627T080708Z_1e8b85` | broader modern | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `action_changed`, `threshold_changed`, `evidence_gate_added`, `stop_rule_added`, `scope_narrowed` | `sufficient_with_caveat` | Brand-safe caution becomes a smaller cash-and-demand test with explicit stop-losses. |
| `launch-limited-beta-workflow` / `20260627T074306Z_7606f7` | broader modern | `pass` | `none` | `present` / `absent` / `absent` | `yes` | `with_human_review` | `threshold_changed`, `sequence_changed`, `evidence_gate_added`, `user_question_added`, `scope_narrowed` | `sufficient_with_caveat` | A beta launch becomes two distinct tracks: learning with design partners and proof for the enterprise prospect. |
| `accept-founding-engineer-role` / `20260623T095719Z` | partial boundary | `needs_followup` | `artifact_custody_failure` | `present` / `absent` / `unclear` | `partly` | `no` | candidate only: `threshold_changed`, `evidence_gate_added`, `stop_rule_added`, `sequence_changed` | `content_only_insufficient_for_eval` | Older partial content can be read, but it should not be counted beside full-modern PR33 positives. |
| `prioritize-control-plane-contract` / `20260625T125625Z_aae54e` | degraded exclusion | `exclude_from_eval` | `artifact_custody_failure` | `not_applicable` / `not_applicable` / `not_applicable` | `unclear` | `no` | none: excluded | `insufficient_for_eval` | A saved answer exists, but custody and readiness prevent this record from joining the positive evaluation seed. |

## Aggregate Counts

| count | value |
|---|---:|
| Total reviewed records | 14 |
| Counted positive eval records | 12 |
| PR30 anchors | 6 |
| Broader modern passes | 6 |
| Needs followup | 1 |
| Excluded from eval | 1 |
| Candidate future fixtures | 12 |
| Excluded or not ready for positive eval | 2 |

Review status:

| label | count |
|---|---:|
| `pass` | 12 |
| `fail` | 0 |
| `needs_followup` | 1 |
| `exclude_from_eval` | 1 |

Human-review fields:

| field | counts |
|---|---|
| `primary_failure_mode` | `none`: 12; `artifact_custody_failure`: 2 |
| `severity` | `none`: 12; `medium`: 1; `high`: 1 |
| `useful_friction` | `present`: 13; `not_applicable`: 1 |
| `noisy_friction` | `absent`: 13; `not_applicable`: 1 |
| `missing_friction` | `absent`: 12; `unclear`: 1; `not_applicable`: 1 |
| `revised_answer_improved` | `yes`: 12; `partly`: 1; `unclear`: 1 |
| `safe_for_agent_use` | `with_human_review`: 12; `no`: 2 |
| `artifact_sufficiency` | `sufficient_with_caveat`: 12; `content_only_insufficient_for_eval`: 1; `insufficient_for_eval`: 1 |

Counted PR31 labels across the 12 positive eval records:

| label | count |
|---|---:|
| `action_changed` | 6 |
| `threshold_changed` | 10 |
| `sequence_changed` | 4 |
| `evidence_gate_added` | 11 |
| `stop_rule_added` | 4 |
| `written_term_added` | 7 |
| `user_question_added` | 5 |
| `scope_narrowed` | 8 |
| `overclaim_retracted` | 5 |
| `no_op_prose_change` | 0 |

## Findings

PR31 labels generalized beyond the six curated complex cases. The six broader
modern records were not just smoother rewrites; they added or changed proof
gates, written terms, stop rules, sequences, scope boundaries, and user-facing
questions.

The strongest repeated pattern was `evidence_gate_added`, which appeared in 11
of 12 counted positives. That makes sense for Lolla's current product shape:
many useful revisions convert a confident recommendation into a commitment
that must earn its way through proof. `threshold_changed` appeared in 10 of 12
counted positives, often paired with evidence gates. The next strongest pattern
was `scope_narrowed`, appearing in 8 of 12 counted positives.

Reviewers can label useful, noisy, and missing friction consistently enough for
this batch. Useful friction was present in all 12 counted positives. No material
noisy friction appeared in those records, and no material missing friction was
identified at answer level. The partial record gets `missing_friction: unclear`
because content alone cannot prove whether the modern extraction surface
captured all relevant pressures.

Older or partial records remain readable, but not equivalent. The partial
founding-engineer record had enough content to see a likely action delta, yet
it lacks the modern agent-result, evaluation, and extraction-adequacy envelope.
It belongs in `needs_followup`, not in the positive seed set.

The degraded record should be excluded from eval even though it has saved
answer text. Its run envelope says not to use the degraded run. PR33 therefore
keeps custody separate from answer-level taste: a useful-looking answer does
not override deterministic readiness failure.

No new failure mode is needed yet. The two non-positive records both fit
`artifact_custody_failure`. The positive records added more examples for
existing rubric labels rather than exposing a taxonomy gap.

The batch creates enough signal to justify the next slice. It does not justify
a judge. It does justify designing the next missing review surface before
automation.

## What PR33 Answers

Do PR31 labels make sense beyond the six curated complex cases?

Yes, for full-modern reviewable records. The six broader modern cases used the
same label vocabulary without stretching it.

Are reviewers able to label useful, noisy, and missing friction consistently?

Enough for this batch. The labels were stable on the counted positives, and the
partial/degraded records showed when to stop counting rather than force a
quality label.

Do older or partial records remain reviewable at answer level?

Partly. Content can suggest a candidate delta, but absent modern custody makes
the label unsuitable for positive eval evidence.

Which records should be excluded from eval because artifacts are insufficient?

The degraded control-plane run is excluded. The older partial founding-engineer
record needs followup and is not counted as positive eval evidence.

Did any new failure modes appear?

No. `artifact_custody_failure` covers both boundary records.

Is there enough signal to justify PR34, or should the taxonomy/rubric be
revised first?

There is enough signal to proceed to PR34. The rubric does not need revision
before the next slice.

## What This Does And Does Not Justify

This does justify:

- treating the 12 counted positives as a broader human-reviewed seed batch;
- using the six broader modern records as candidate future adversarial
  fixtures;
- keeping the PR31 rubric as the current language for real improvement;
- using `artifact_custody_failure` for content-present records that are not
  eval-ready;
- moving to a design note for first-class user values and priorities.

This does not justify:

- an LLM judge;
- a calibrated judge;
- generic answer-quality scoring;
- automatic label population;
- automatic agent approval;
- runtime specialist integration;
- prompt rewrite;
- changing `caller_action` policy;
- changing provider-boundary policy;
- treating `evaluation.json` as answer-quality scoring;
- treating `caller_action: use_revised_answer` as human approval;
- treating these 14 records as a benchmark claim.

## Recommended Next Slice

PR34 now defines the design that this note recommended:

```text
docs/conversation-understanding/user-values-priorities-signal-v0.md
```

Why PR34 and not a judge: PR33 showed the PR31 labels survive a broader modern
batch, but it also repeated the same review caveat already visible in PR30 and
PR31: user values and priorities are not first-class measured fields. A judge
would be premature while that evidence surface remains implicit. PR34 designs
how to represent that signal in review and custody terms without adding
runtime calls, a memory layer, graph storage, embeddings, or automatic labels.

PR34 remains docs/design-only. It prepares evaluation language; it does not
implement extraction, runtime integration, or judging.

Next:

```text
docs/evals/live-output-hygiene-decision-v0.md
```

PR35 keeps `live_output_health: not_checked` as an honest default caveat for
normal runs. That policy supports the PR33 treatment: saved answer-level review
can pass while `safe_for_agent_use` remains conservative and live output remains
unproven.

PR36 now defines risk-mode behavior policy:

```text
docs/evals/risk-mode-behavior-plan-v0.md
```

That policy preserves the PR33 separation between answer-level review,
run-envelope/custody review, and agent reliance.

PR37 now adds the fixture matrix:

```text
docs/evals/risk-mode-fixture-matrix-v0.md
```

PR38 now reviews that matrix, keeps every original PR37 fixture as a passing
implementation gate, and adds the missing high-stakes values/priorities conflict
fixture:

```text
docs/evals/risk-mode-fixture-review-v0.md
```

PR39 now plans high-stakes reliance/readiness tightening without implementation:

```text
docs/evals/risk-mode-implementation-plan-v0.md
```

PR40 locks the current conservative contract in tests, and PR41 adds the
deterministic `risk_mode_reliance_policy` check to `evaluation.json`.

The next step is review/corpus surface integration, not runtime enforcement:

```text
PR42 Risk Mode Review Surface Integration v0
```

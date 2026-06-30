# Product Delta Provisional Report v0

Status: docs/report
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR77 Product Delta Provisional Report v0

## Purpose

This report summarizes the PR75 readiness run and the PR76 Codex-assisted
provisional semantic batch as one state-of-evidence packet.

The current claim is narrow:

> Lolla can convert existing review-safe cases into conservative, schema-valid,
> inspectable Product Delta Evidence packets, and Codex can provisionally fill
> those packets without pretending to be human review.

The current claim is not:

> Lolla improves decisions.

That stronger claim still requires later human validation, correction, and
principal-reviewer taste judgment.

## Inputs

PR77 uses only checked-in, review-safe artifacts:

- [Product Delta Eval Readiness And Provisional Run v0](product-delta-eval-readiness-and-provisional-run-v0.md).
- [Product Delta provisional run JSON](../../reviews/codex-assisted/product-delta-provisional-run-v0/review.json).
- [Codex-Assisted Product Delta Batch v0](codex-assisted-product-delta-batch-v0.md).
- [Codex-assisted Product Delta batch JSON](../../reviews/codex-assisted/product-delta-batch-v0/review.json).
- [Vanilla-vs-Lolla Provisional Review Protocol v0](vanilla-vs-lolla-provisional-review-protocol-v0.md).
- [Provisional Product Delta Failure Taxonomy v0](provisional-product-delta-failure-taxonomy-v0.md).

This report did not run `$lolla`, call models, mutate archives, read raw
transcripts, copy raw/private content, change prompts, change `SKILL.md`, change
runtime behavior, add a judge, add a score, add automatic labels, or infer
`safe_for_agent_use`.

## Executive Read

The provisional evidence package now has a usable shape:

- PR75 inspected 14 existing cases for Product Delta readiness.
- 12 cases were ready for Codex-assisted provisional review.
- 1 older partial case was blocked as `blocked_private_content_only`.
- 1 degraded case was blocked as `degraded_run_health`.
- PR76 filled the 12 ready shells with Codex-assisted provisional candidate
  reads.
- Every reviewed case records lost-value risk.
- 6 of 12 reviewed cases record interpretation-adequacy concern or uncertainty.
- Every reviewed case includes human follow-up questions.

The most important epistemic caution:

> PR76 found zero `lolla_added_noise_candidate` and zero
> `lolla_worse_candidate` cases. That is not evidence that Lolla never adds
> noise or makes advice worse. It may reflect safe-summary compression, Codex
> agreement bias, the selected corpus, or the fact that the available cases were
> already review-safe enough to be chosen.

## Readiness Result

PR75 tested reviewability, not answer quality.

| readiness state | count |
|---|---:|
| `ready_for_codex_provisional_review` | 12 |
| `blocked_private_content_only` | 1 |
| `degraded_run_health` | 1 |
| `thin_safe_context` | 0 |
| `missing_vanilla_baseline` | 0 |
| `missing_revised_answer` | 0 |
| `missing_review_safe_summary` | 0 |
| `missing_archive_case` | 0 |

All 12 ready cases still carried weakening reasons:
`evaluation_overall_warn`, `caller_readiness_inspect_first`, and
`artifact_sufficiency_caveat`. That is healthy for this phase. The point was to
make review surfaces explicit, not to certify the cases.

## Provisional Candidate Distribution

PR76 filled the 12 ready shells with Codex-assisted candidate reads.

| `net_decision_read_provisional` | count |
|---|---:|
| `material_improvement_candidate` | 6 |
| `partial_improvement_candidate` | 4 |
| `no_material_change_candidate` | 1 |
| `inconclusive` | 1 |
| `lolla_added_noise_candidate` | 0 |
| `lolla_worse_candidate` | 0 |

Decision-leverage candidates:

| `decision_leverage.label` | count |
|---|---:|
| `high` | 6 |
| `medium` | 4 |
| `low` | 1 |
| `unclear` | 1 |

This is a candidate distribution, not a performance result.

## Case-Level Summary

| case | provisional read | leverage | interpretation adequacy | human-review priority |
|---|---|---|---|---|
| `ceo-remove-founding-cofounder` | `material_improvement_candidate` | `high` | `adequate` | Confirm whether vanilla left authority transfer too conditional. |
| `accept-operations-role-startup` | `material_improvement_candidate` | `high` | `partly_adequate` | Check ambition, household capacity, and written-gate proportion. |
| `launch-public-enterprise-beta` | `material_improvement_candidate` | `high` | `adequate` | Check whether gates preserve enough launch momentum. |
| `pre-sell-undefined-consulting` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Distinguish useful scoping from polish/status over-management. |
| `pivot-company-product-strategy` | `material_improvement_candidate` | `high` | `adequate` | Check whether capacity gates slow market learning too much. |
| `deploy-assisted-intake-routing` | `material_improvement_candidate` | `high` | `partly_adequate` | Review stakeholder coverage and risk posture first. |
| `accept-founding-engineer-role` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Check values, ambition, household load, and kill criteria. |
| `accept-high-intensity-startup` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Check whether status framing was user-owned or assistant-influenced. |
| `five-person-saas-team-1` | `no_material_change_candidate` | `low` | `unclear` | Determine whether Lolla changed behavior or only refined a proof package. |
| `implement-price-increase-three` | `material_improvement_candidate` | `high` | `adequate` | Check whether account segmentation is enforceable and clear. |
| `initiate-pre-sale-coffee-1` | `inconclusive` | `unclear` | `unclear` | Establish the vanilla likely action before reading product delta. |
| `launch-limited-beta-workflow` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Check whether two tracks improve proof hygiene or add complexity. |

## Recurring Structural Deltas

The PR76 batch suggests that Lolla's candidate value is not mostly a smoother
rewrite. The recurring candidate deltas are structural:

| structural-delta field | count |
|---|---:|
| `evidence_gate_added_or_changed` | 11 |
| `threshold_changed` | 10 |
| `scope_changed` | 8 |
| `written_term_added_or_changed` | 7 |
| `action_changed` | 6 |
| `overclaim_retracted` | 5 |
| `user_answerable_question_added` | 5 |
| `sequence_changed` | 4 |
| `stop_rule_added_or_changed` | 4 |

The plausible product thesis is that Lolla often turns fluent advice into
conditions for action: gates, thresholds, scope limits, written terms, stop
rules, and user-answerable checks.

The unresolved question is whether those conditions were decision-useful, or
whether they became process weight.

## Friction Read

The useful-friction doctrine is:

```text
useful friction = grounded + actionable + proportionate
```

PR76 recorded every case as grounded and actionable from the review-safe source.
Proportion remained less settled:

| friction field | value | count |
|---|---|---:|
| `useful_friction` | `present` | 6 |
| `useful_friction` | `partial` | 6 |
| `noisy_friction` | `absent` | 5 |
| `noisy_friction` | `partial` | 5 |
| `noisy_friction` | `unclear` | 2 |
| `missing_friction` | `unclear` | 12 |
| `proportionate` | `true` | 8 |
| `proportionate` | `null` | 4 |

This is the right shape for the scaffold. It does not merely ask whether Lolla
added caution. It asks whether the added pressure changed action, threshold,
sequence, evidence gate, stop rule, written term, scope, or user-answerable
question.

## Lost-Value Risks

Every PR76 case records at least one lost-value category. That prevents the
candidate-read distribution from becoming one-way product cheerleading.

| lost-value category | count |
|---|---:|
| `momentum` | 12 |
| `simplicity` | 9 |
| `user_specific_ambition` | 4 |
| `courage` | 3 |
| `actionability` | 1 |
| `clarity` | 1 |

The main concern is not that Lolla fails to add structure. The main concern is
that structure may bury speed, courage, simplicity, or ambition in some cases.
That is a product question, not a schema question.

## Interpretation Adequacy

Interpretation adequacy remains load-bearing.

| `interpretation_adequacy.label` | count |
|---|---:|
| `adequate` | 4 |
| `partly_adequate` | 6 |
| `unclear` | 2 |

Failure-mode candidates:

| interpretation failure mode | count |
|---|---:|
| `value_overwrite` | 3 |
| `constraint_flattening` | 2 |
| `decision_question_drift` | 2 |
| `assistant_influence_blindness` | 1 |
| `option_loss` | 1 |
| `risk_mode_mismatch` | 1 |
| `stakeholder_erasure` | 1 |
| `uncertainty_collapse` | 1 |

Only one case marked `would_better_interpretation_change_answer: yes`;
eleven marked it `unclear`. That is another humility flag: the current safe
surfaces often let Codex identify the likely concern, but not decide how much
the answer would change under fuller interpretation.

## First Upstream Failure

The first-upstream-failure field mostly points to review-surface limits:

| `first_upstream_failure.surface` | count |
|---|---:|
| `review_surface` | 7 |
| `none_observed` | 4 |
| `audit_pressure` | 1 |

This argues against adding another runtime artifact immediately. The immediate
bottleneck is human validation of the review surface, not more automatic
machinery.

## Human Review First

Future human review should prioritize:

1. `initiate-pre-sale-coffee-1`, because the current read is inconclusive and
   the vanilla likely action is too inferred.
2. `five-person-saas-team-1`, because it tests whether improved structure is
   actually a material product delta or only a cleaner version of the same
   likely action.
3. `deploy-assisted-intake-routing`, because stakeholder coverage, risk posture,
   and stop-rule sufficiency are high-leverage and easy for Codex to overread.
4. `pre-sell-undefined-consulting`, because it is the clearest candidate for
   useful scoping versus polish/status over-management.
5. The three career/role cases, because value overwrite, ambition preservation,
   family or household constraints, and assistant influence are hard to settle
   from compressed safe summaries.
6. At least two `material_improvement_candidate` cases, because the positive
   candidates need active downgrade pressure before they become product belief.

## What Would Falsify The Candidate Reads

The candidate conclusions should be downgraded or rejected if human review finds
any of the following:

- the vanilla final answer already contained the same action, threshold,
  sequence, gate, stop rule, written term, scope, or user question;
- the Lolla revised answer did not change what the user would plausibly do next;
- the raw conversation reveals a different decision question than the safe
  summary suggests;
- the revised answer preserved structure but lost the user's real ambition,
  courage, simplicity, timing, or motivating clarity;
- a proposed gate or stop rule was not operationally usable;
- an interpretation concern would materially change the revised answer;
- the absence of worse/noisy candidates reflects Codex agreement bias, selected
  corpus bias, or safe-summary compression;
- a simpler checklist or generic critique prompt would have produced the same
  useful structural delta.

## What This Proves

PR77 supports these limited statements:

- The PR71-PR74 scaffold is usable on existing cases.
- PR75 can produce deterministic, schema-shaped readiness shells over existing
  review-safe case data.
- PR76 can fill those shells with conservative Codex-assisted provisional reads.
- The protocol can represent material, partial, no-change, and inconclusive
  cases.
- The protocol can capture lost value and interpretation adequacy concerns.
- Human reviewers now have concrete follow-up questions and falsification tests.

## What This Does Not Prove

PR77 does not prove:

- Lolla improves decisions;
- Lolla beats a simpler checklist or critique prompt;
- the PR76 candidate labels are correct;
- the candidate distribution is statistically meaningful;
- the zero noisy/worse count is representative;
- Codex can replace human judgment;
- the output is judge calibration data;
- clean artifacts imply good advice;
- any case is safe for agent use;
- Product Delta Evidence should be integrated into runtime.

## Non-Claims

This report is not:

- human review;
- ground truth;
- judge calibration data;
- product proof;
- answer-quality scoring;
- automatic labeling;
- agent approval;
- runtime integration;
- archive mutation.

Subjective findings remain `codex_assisted_provisional` until a principal human
reviewer validates, corrects, or rejects them.

## Follow-On Boundary Lint

PR78 adds deterministic evidence-boundary lint:
[Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md).

That lint checks supplied Product Delta artifacts for unsafe metadata,
authority/scoring fields, taxonomy score drift, missing PR72 review-case
boundary fields, privacy markers, and targeted Markdown overclaim risks. It is
not semantic judgment and not proof that Lolla improved any decision.

PR79 defines the context-engineered provisional specialist-review architecture:
[Context-Engineered Provisional Review Architecture v0](context-engineered-provisional-review-architecture-v0.md).
That architecture keeps future specialist reads downstream/offline,
decomposed, typed, linted, and disagreement-preserving while still avoiding
judges, scores, automatic labels, runtime integration, archive mutation,
dashboard, graph DB, memory, GraphRAG, or `safe_for_agent_use` automation.

PR83 has now run the first tiny Codex-assisted specialist-review batch:
[Codex-Assisted Specialist Review Batch v0](codex-assisted-specialist-review-batch-v0.md).
It treats PR76 as prior broad context, not truth, and shows one concrete
downgrade from a PR76 material candidate to a PR83 partial candidate. That is
evidence that the review harness can become more disciplined; it is still not
evidence that Lolla improves decisions.

PR84 has now added the fan-in/disagreement report:
[Product Delta Fan-In / Disagreement Report v0](product-delta-fan-in-disagreement-report-v0.md).
It reports over existing PR76 and PR83 artifacts only, preserving the downgrade,
both lost-value and interpretation-adequacy concern surfaces, and the
two-case positive-distribution limit without adding new specialist reads or
product-proof claims.

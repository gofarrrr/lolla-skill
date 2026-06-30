# Provisional Product Delta Failure Taxonomy v0

Status: docs/JSON taxonomy
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR74 Provisional Product Delta Failure Taxonomy v0

## Purpose

This note defines provisional failure language for Product Delta Evidence
review. It is derived from PR73 dry-run observations and the existing Lolla
evaluation methodology.

The machine-readable taxonomy is:

```text
docs/evals/provisional-product-delta-failure-taxonomy-v0.json
```

This taxonomy is not human-validated. It is not judge-ready. It is not an
answer-quality score, automatic label system, product proof, or agent approval
surface.

## Source Context

The taxonomy is shaped by:

- [Product Delta Evidence Thesis v0](product-delta-evidence-thesis-v0.md)
- [Vanilla-vs-Lolla Provisional Review Protocol v0](vanilla-vs-lolla-provisional-review-protocol-v0.md)
- [Codex-Assisted Paired Review Dry Run v0](codex-assisted-paired-review-dry-run-v0.md)
- [Lolla Evaluation Methodology](../lolla-evaluation-methodology.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)

It keeps the Product Delta question separate from deterministic custody:

```text
Did Lolla change what a serious person would do next, in a way that was
grounded, actionable, and proportionate?
```

Clean artifacts can make review possible. They do not prove that the advice was
good.

## Taxonomy Groups

### Product Delta Failures

These describe ways the Lolla revised answer can fail to create useful product
delta:

- `no_op_prose`
- `caveat_bloat`
- `diligence_theater`
- `false_precision`
- `overcorrection`
- `lost_useful_original_advice`
- `stakeholder_flattening`
- `values_overwrite`
- `momentum_burial`
- `generic_prudence_substitution`
- `artifact_authority_leak`

### Interpretation Failures

These describe ways Lolla can misunderstand the conversation before or during
audit pressure:

- `decision_question_drift`
- `option_loss`
- `constraint_flattening`
- `stakeholder_erasure`
- `value_overwrite`
- `transient_emotion_hardening`
- `assistant_influence_blindness`
- `false_consensus`
- `dropped_thread_blindness`
- `quote_or_grounding_misread`
- `uncertainty_collapse`
- `risk_mode_mismatch`

### Review / Process Failures

These describe ways the Codex-assisted review scaffold can fail:

- `likely_action_over_inference`
- `codex_agreement_bias`
- `codex_smoothness_bias`
- `codex_overclaim`
- `review_surface_too_heavy`
- `insufficient_safe_context`
- `human_followup_required`

## Entry Shape

Every taxonomy entry includes:

- `id`
- `category`
- `definition`
- `why_it_matters`
- `provisional_detection_question`
- `possible_review_surface`
- `deterministic_or_subjective`
- `current_status`: `provisional_until_human_review`
- `not_a_score`: `true`

The taxonomy can help a reviewer ask better questions. It must not be treated
as an automatic classifier.

## PR73 Dry-Run Observations

The dry run surfaced several useful provisional patterns:

- Some cases look like strong material-improvement candidates, but still carry
  lost-value risk such as reduced momentum, simplicity, or ambition.
- The clinic deployment case shows why interpretation adequacy and risk-mode
  fit remain load-bearing.
- The founding-engineer and coffee cases show how likely-action inference can
  overrun the safe review surface.
- The consulting case shows that useful friction is not always "more
  skepticism"; sometimes it is retracting an overconfident interpretation.
- The protocol is usable but heavy, which should become a human-review UX
  question rather than a reason to automate labels.

## Non-Claims

This taxonomy does not:

- create automatic labels;
- make labels judge-ready;
- treat PR73 labels as human labels;
- score answer quality;
- approve agent use;
- prove product value;
- replace a principal human reviewer.

## Recommended Next Slice

PR75 now exercises the scaffold with a deterministic readiness/shell run:
[Product Delta Eval Readiness And Provisional Run v0](product-delta-eval-readiness-and-provisional-run-v0.md).

PR76 fills the ready PR75 shells with Codex-assisted provisional semantic
reads: [Codex-Assisted Product Delta Batch v0](codex-assisted-product-delta-batch-v0.md).

The next recommended slice is PR77 Product Delta Provisional Report v0. It
should summarize the PR75 readiness run and PR76 candidate reads while still
avoiding human-validation claims, judges, scores, automatic labels, runtime
integration, and archive mutation.

# Vanilla-vs-Lolla Provisional Review Protocol v0

Status: docs/schema
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR72 Vanilla-vs-Lolla Provisional Review Protocol v0

## Purpose

This protocol defines a review-safe packet for comparing an actual vanilla
strong-model conversation/final answer against the Lolla revised decision
answer.

Every subjective conclusion in this protocol is provisional. The packet exists
to help a future human reviewer inspect the delta faster. It is not a human
review, ground truth, judge calibration data, product proof, answer-quality
scoring, or agent approval.

The companion JSON schema is:

```text
docs/evals/vanilla-vs-lolla-provisional-review-v0.json
```

## Required Boundaries

The protocol must preserve these boundaries:

- `review_mode` is `codex_assisted_provisional`.
- `human_validated` is `false`.
- `ground_truth` is `false`.
- `judge_calibration_eligible` is `false`.
- `raw_private_content_included` is `false`.
- `model_calls` is `0`.
- `archive_mutated` is `false`.
- All artifact paths are relative.
- All subjective fields include uncertainty.
- Labels use `candidate` or `provisional` language where they summarize
  subjective answer-quality reads.

The packet must not contain raw transcript text, raw memo text, raw
revised-answer text, provider text, private reasoning, secrets, local absolute
paths, or machine-inferred human labels.

## Review Unit

The review unit is one actual vanilla-vs-Lolla pair:

```text
case_id
archive_relpath or case_relpath
review-safe source artifacts
provisional paired review sections
non-claims
human follow-up questions
```

A batch may contain many case packets, but each case packet should remain
readable as a standalone provisional review.

## Top-Level Metadata

Each case packet includes:

- `schema_version`: exactly
  `lolla.vanilla_vs_lolla_provisional_review.v0`
- `review_mode`: exactly `codex_assisted_provisional`
- `human_validated`: `false`
- `ground_truth`: `false`
- `judge_calibration_eligible`: `false`
- `reviewer_type`: for this phase, `codex`
- `case_id`
- `archive_relpath` or `case_relpath`, using a relative path only
- `reviewed_artifacts`, using relative paths only
- `raw_private_content_included`: `false`
- `model_calls`: `0`
- `archive_mutated`: `false`

## Review Sections

### `vanilla_likely_next_action`

Provisional read of what the user would likely do after the actual vanilla
strong-model conversation/final answer.

Fields:

- `status`
- `summary`
- `basis`
- `uncertainty`
- `reviewer_inferred`

### `lolla_likely_next_action`

Provisional read of what the user would likely do after the Lolla revised
answer.

Fields match `vanilla_likely_next_action`.

### `material_difference`

Whether the likely next action changed in a decision-relevant way.

Fields:

- `status`
- `summary`
- `changed`
- `uncertainty`

### `structural_delta`

Which decision structures changed.

Fields:

- `action_changed`
- `threshold_changed`
- `sequence_changed`
- `evidence_gate_added_or_changed`
- `stop_rule_added_or_changed`
- `written_term_added_or_changed`
- `scope_changed`
- `overclaim_retracted`
- `user_answerable_question_added`
- `notes`

### `decision_leverage`

How much the candidate delta could affect a real decision.

Fields:

- `label`: `none`, `low`, `medium`, `high`, or `unclear`
- `rationale`
- `uncertainty`

This is not a numeric score.

### `friction_read`

Whether friction is useful, noisy, or missing.

Fields:

- `useful_friction`
- `noisy_friction`
- `missing_friction`
- `grounded`
- `actionable`
- `proportionate`
- `rationale`

Useful friction requires all three: grounded, actionable, and proportionate.

### `lost_value`

Whether the revised answer may have weakened something useful.

Fields:

- `present`
- `categories`
- `rationale`

Examples include useful original advice, momentum, courage, clarity,
user-specific ambition, simplicity, and actionability.

### `interpretation_adequacy`

Whether Lolla appears to have understood the conversation well enough for the
audit to be a trustworthy review object.

Fields:

- `label`: `adequate`, `partly_adequate`, `inadequate`, or `unclear`
- `failure_modes`
- `rationale`
- `would_better_interpretation_change_answer`

### `first_upstream_failure`

The first surface where the provisional reviewer sees trouble.

Allowed surfaces:

- `vanilla_answer`
- `conversation_interpretation`
- `audit_pressure`
- `revised_answer`
- `artifact_custody`
- `review_surface`
- `none_observed`
- `unclear`

### `net_decision_read_provisional`

The provisional candidate read of the pair.

Allowed labels:

- `material_improvement_candidate`
- `partial_improvement_candidate`
- `no_material_change_candidate`
- `lolla_added_noise_candidate`
- `lolla_worse_candidate`
- `inconclusive`

Do not rename this to `lolla_improved`. The field is provisional by design.

### `codex_uncertainty_notes`

Freeform notes about what Codex could not safely know from review-safe sources.

### `human_followup_questions`

Questions for a later human reviewer. Good questions ask about actual user
intent, likely action, missing constraints, lost value, interpretation errors,
or whether the delta would change behavior.

### `non_claims`

The packet must repeat the non-claims that keep provisional review from
becoming fake certainty.

At minimum:

- not human review;
- not ground truth;
- not judge calibration data;
- not product proof;
- not agent approval;
- not answer-quality scoring;
- not automatic labeling.

## Dry-Run Use

PR73 applies this protocol to safe checked-in cases without running `$lolla`,
calling models, mutating archives, or copying raw/private content:

```text
docs/evals/codex-assisted-paired-review-dry-run-v0.md
reviews/codex-assisted/paired-review-dry-run-v0/review.json
```

The dry run is a usability check for the protocol, not a product-evidence
claim.

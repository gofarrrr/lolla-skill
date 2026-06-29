# Codex-Assisted Product Delta Batch v0

Status: docs/review fixture
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR76 Codex-Assisted Product Delta Batch v0

## Purpose

This note records the first Codex-assisted provisional semantic fill over the
PR75 Product Delta readiness shells.

PR75 tested reviewability. PR76 tests whether the ready shells can carry
candidate semantic reads without pretending to be human review.

Machine-readable output:

```text
reviews/codex-assisted/product-delta-batch-v0/review.json
```

Source shell batch:

```text
reviews/codex-assisted/product-delta-provisional-run-v0/review.json
```

This slice did not run `$lolla`, call models, mutate archives, copy
raw/private content, change prompts, change `SKILL.md`, change runtime
behavior, add a judge, add a score, add automatic labels, or infer
`safe_for_agent_use`.

## Source Surfaces

PR76 used only review-safe checked-in sources:

- [Product Delta Eval Readiness And Provisional Run v0](product-delta-eval-readiness-and-provisional-run-v0.md)
- [Product Delta provisional run JSON](../../reviews/codex-assisted/product-delta-provisional-run-v0/review.json)
- [Human Review Corpus Batch v0](human-review-corpus-batch-v0.md)
- [PR33 review JSON](../../reviews/human/corpus-batch-v0/review.json)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [Vanilla-vs-Lolla Provisional Review Protocol v0](vanilla-vs-lolla-provisional-review-protocol-v0.md)

The checked-in PR76 output contains paraphrases only. It does not copy raw
transcripts, raw memos, raw revised answers, provider text, private reasoning,
secrets, or local absolute paths.

## Method

Codex applied a three-pass structure:

1. Delta reader:
   Identify candidate action, threshold, sequence, evidence-gate, stop-rule,
   written-term, scope, overclaim, or user-question changes.
2. Skeptical reader:
   Look for no-op prose, caveat bloat, lost value, likely-action
   over-inference, noisy friction, and insufficient safe context.
3. Conservative consolidation:
   Fill the PR72 fields, preserve uncertainty, generate human follow-up
   questions, and prefer partial or inconclusive reads where the safe source is
   compressed.

This is still one Codex-assisted review process. It is not independent human
validation and not model-judge calibration.

## Batch Shape

PR75 found 12 cases ready for Codex provisional review. PR76 filled those 12
ready shells.

| provisional read | count |
|---|---:|
| `material_improvement_candidate` | 6 |
| `partial_improvement_candidate` | 4 |
| `no_material_change_candidate` | 1 |
| `lolla_added_noise_candidate` | 0 |
| `lolla_worse_candidate` | 0 |
| `inconclusive` | 1 |

Every case includes `lost_value`. Six cases have interpretation-adequacy
concerns or unclear interpretation adequacy. That is deliberate: the batch
should not read like a forced win set.

The absence of `lolla_added_noise_candidate` and `lolla_worse_candidate` cases
is not evidence that Lolla avoids those outcomes. It may reflect Codex agreement
bias, selection bias, or safe-summary compression.

## Case Summary

| case | net read provisional | decision leverage | interpretation adequacy | main caveat |
|---|---|---|---|---|
| `ceo-remove-founding-cofounder` | `material_improvement_candidate` | `high` | `adequate` | Confirm the vanilla answer really left authority transfer too conditional. |
| `accept-operations-role-startup` | `material_improvement_candidate` | `high` | `partly_adequate` | Check whether written gates protect ambition or over-process it. |
| `launch-public-enterprise-beta` | `material_improvement_candidate` | `high` | `adequate` | Check whether evidence gates cost too much launch momentum. |
| `pre-sell-undefined-consulting` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Distinguish useful client readiness from status/polish over-management. |
| `pivot-company-product-strategy` | `material_improvement_candidate` | `high` | `adequate` | Check whether the capacity gate slows market learning too much. |
| `deploy-assisted-intake-routing` | `material_improvement_candidate` | `high` | `partly_adequate` | Healthcare-adjacent stakeholders and risk posture need human review. |
| `accept-founding-engineer-role` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Safe context is thin for values and household-load judgment. |
| `accept-high-intensity-startup` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Check whether status framing was user-owned or assistant-influenced. |
| `five-person-saas-team-1` | `no_material_change_candidate` | `low` | `unclear` | The revised proof package may be refinement rather than material next-action change. |
| `implement-price-increase-three` | `material_improvement_candidate` | `high` | `adequate` | Account-level segmentation may be harder to communicate or enforce. |
| `initiate-pre-sale-coffee-1` | `inconclusive` | `unclear` | `unclear` | Vanilla likely action is too inferred from compressed safe summaries. |
| `launch-limited-beta-workflow` | `partial_improvement_candidate` | `medium` | `partly_adequate` | Two beta tracks may improve proof hygiene but cost operational simplicity. |

## What Worked

The PR72 schema can carry real provisional semantic reads over the 12 ready
cases. The fields made it possible to separate:

- structural deltas from smoother prose;
- useful friction from caution/noise risk;
- candidate decision leverage from answer-quality proof;
- lost value from improvement claims;
- interpretation adequacy from artifact cleanliness.

The batch also produced specific human follow-up questions for each case.

## What Stayed Humble

PR76 did not force every case positive.

`five-person-saas-team-1` is marked `no_material_change_candidate` because the
safe summary suggests a cleaner proof package but not enough evidence of a
material next-action change.

`initiate-pre-sale-coffee-1` is marked `inconclusive` because the vanilla
likely action is too inferred from compressed safe summaries.

Several partial candidates preserve lost-value concerns: momentum, courage,
ambition, simplicity, and actionability.

## What A Future Human Reviewer Should Check

A future human reviewer should check:

- whether each vanilla likely action matches the actual vanilla final answer;
- whether each Lolla likely action matches the actual revised answer;
- whether the candidate structural delta would change real behavior;
- whether lost value was overstated, understated, or missed;
- whether the interpretation adequacy concerns would change the answer;
- whether `five-person-saas-team-1` is truly no-material-change or merely
  under-supported by safe summaries;
- whether `initiate-pre-sale-coffee-1` becomes reviewable after inspecting the
  local raw/revised surfaces;
- whether any `material_improvement_candidate` should be downgraded.

## Non-Claims

This batch is not:

- human review;
- ground truth;
- judge calibration data;
- product proof;
- agent approval;
- answer-quality scoring;
- automatic labeling.

Clean artifacts made PR76 possible. They do not prove good advice.

## Follow-On Slice

PR77 summarizes PR75 and PR76 together as a provisional state-of-evidence
report: [Product Delta Provisional Report v0](product-delta-provisional-report-v0.md).

It covers:

- 14 cases inspected by readiness;
- 12 ready for Codex-assisted provisional review;
- 12 provisionally filled;
- distribution of candidate reads;
- common structural deltas;
- common lost-value risks;
- interpretation adequacy concerns;
- what human review must validate or correct later.

PR78 adds deterministic evidence-boundary lint before any broader specialist
review architecture: [Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md).
It is the seatbelt for future provisional outputs: keep avoiding product-proof
language, judges, scores, automatic labels, runtime integration, archive
mutation, and `safe_for_agent_use` automation.

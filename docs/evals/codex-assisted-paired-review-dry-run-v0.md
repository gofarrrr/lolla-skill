# Codex-Assisted Paired Review Dry Run v0

Status: docs/review fixture
Date: 2026-06-29
Review capacity mode: `codex_assisted_provisional`
Slice: PR73 Codex-Assisted Paired Review Dry Run v0

## Purpose

This dry run applies the PR72 provisional review protocol to a small set of
existing review-safe cases.

It asks whether Codex can fill a vanilla-vs-Lolla review packet without
overclaiming and without pretending to be a human reviewer.

This dry run did not run `$lolla`, call external models, mutate archives,
change prompts, change `SKILL.md`, change runtime behavior, add a judge, add a
score, add automatic labels, or add `safe_for_agent_use` automation.

Machine-readable output:

```text
reviews/codex-assisted/paired-review-dry-run-v0/review.json
```

Protocol and schema:

```text
docs/evals/vanilla-vs-lolla-provisional-review-protocol-v0.md
docs/evals/vanilla-vs-lolla-provisional-review-v0.json
```

## Sources

This dry run used only review-safe checked-in artifacts:

- [Current System Capabilities v0](current-system-capabilities-v0.md)
- [Complex Baseline Human Review v0](complex-baseline-human-review-v0.md)
- [Human Review Corpus Batch v0](human-review-corpus-batch-v0.md)
- [Actionable Delta Rubric v0](actionable-delta-rubric-v0.md)
- [Product Delta Evidence Thesis v0](product-delta-evidence-thesis-v0.md)
- [Vanilla-vs-Lolla Provisional Review Protocol v0](vanilla-vs-lolla-provisional-review-protocol-v0.md)

The dry run did not copy raw transcript text, raw memo text, raw
revised-answer text, provider text, private reasoning, secrets, or local
absolute paths into the checked-in review packet.

## Methodology

For each case, Codex read the review-safe summaries and asked:

1. What would the user likely do after the vanilla strong-model conversation or
   answer?
2. What would the user likely do after the Lolla revised answer?
3. Did the likely action materially change?
4. Which structure changed: action, threshold, sequence, evidence gate, stop
   rule, written term, scope, overclaim, or user-answerable question?
5. Was the friction grounded, actionable, and proportionate?
6. Did the revised answer lose any useful value?
7. Was interpretation adequate enough for a future human to trust the pair as a
   review object?
8. What should a human reviewer check next?

The likely-action fields are especially provisional because the safe checked-in
sources summarize prior reviews rather than preserving the full vanilla final
answer and Lolla revised answer in this review packet.

## Global Caveats

The dry run is explicitly:

- `human_validated: false`
- `ground_truth: false`
- `judge_calibration_eligible: false`
- `raw_private_content_included: false`
- `model_calls: 0`
- `archive_mutated: false`

The dry run is not product evidence. It is a scaffold for later human review.

## Cases Reviewed

The dry run covers eight safe cases:

| case id | safe source basis | provisional net read | main uncertainty |
|---|---|---|---|
| `ceo-remove-founding-cofounder` | PR30 complex baseline review | `material_improvement_candidate` | Human should confirm the vanilla answer really would have left authority ambiguous. |
| `launch-public-enterprise-beta` | PR30 complex baseline review | `material_improvement_candidate` | Human should check whether public-launch momentum lost too much value. |
| `deploy-assisted-intake-routing` | PR30 complex baseline review | `material_improvement_candidate` | Human should check healthcare-adjacent risk interpretation and omitted stakeholders. |
| `implement-price-increase-three` | PR33 corpus batch review | `material_improvement_candidate` | Human should check whether account-level complexity was proportionate. |
| `accept-founding-engineer-role` | PR33 corpus batch review | `partial_improvement_candidate` | Human should check whether family/role gates preserved ambition rather than burying it. |
| `pivot-company-product-strategy` | PR30 complex baseline review | `material_improvement_candidate` | Human should check whether capacity gates delayed market learning too much. |
| `pre-sell-undefined-consulting` | PR30 complex baseline review | `partial_improvement_candidate` | Human should check whether polish was bounded correctly rather than flattened. |
| `initiate-pre-sale-coffee-1` | PR33 corpus batch review | `inconclusive` | Safe summaries suggest a useful delta, but the actual vanilla likely action is too inferred here. |

## Provisional Findings

The protocol can be filled without overclaiming if every subjective field
preserves uncertainty and if likely-action summaries are marked
reviewer-inferred.

The protocol separates useful friction from noisy friction better than a plain
"improved yes/no" label. The dry run could say that cofounder authority
transfer, enterprise buyer proof, clinic stop conditions, pricing support
economics, founder-role written gates, pivot capacity gates, and consulting
scope constraints are candidate useful friction because they change action or
proof. It could also flag the possibility that some friction costs momentum,
simplicity, ambition, or speed.

The protocol captures lost value. Several candidate wins still carry possible
costs: slower launch momentum, buried ambition, lower simplicity, or reduced
commercial energy.

The protocol captures interpretation adequacy concerns. The clinic case raises
stakeholder and risk-mode questions; the founding-engineer and coffee cases
show how a likely-action read can become too inferred when the safe review
surface is compressed.

The protocol avoids presenting Codex output as human judgment when the packet
keeps its non-claims visible at the top level and per case.

The human follow-up questions are useful because they ask what a future
reviewer should verify in raw/local review surfaces without copying those
surfaces into this fixture.

The schema is usable, but it is heavy. That heaviness is acceptable for this
phase because the protocol is a human-review scaffold, not a runtime artifact.
If humans find it tedious, the next refinement should reduce repeated metadata
without weakening the non-claims.

## What A Future Human Reviewer Should Check

A future human reviewer should check:

- whether the vanilla likely action was inferred correctly from the actual
  vanilla conversation/final answer;
- whether the Lolla revised answer would really change user behavior;
- whether the friction was grounded in the actual conversation rather than in
  Codex's reconstruction from summaries;
- whether any added caution was actionable or merely process-heavy;
- whether Lolla lost useful original advice, momentum, courage, clarity,
  ambition, simplicity, or actionability;
- whether interpretation failures changed the answer;
- whether the case should become a human-validated product example, a failure
  example, a no-change example, or excluded evidence;
- whether any provisional taxonomy entry should be renamed before human use.

## What This Does Not Justify

This dry run does not justify:

- claiming that Lolla improves decisions;
- treating Codex-assisted findings as human labels;
- treating the packet as ground truth;
- using the packet for judge calibration;
- training or evaluating an LLM judge;
- scoring answer quality;
- adding automatic labels;
- adding agent approval;
- changing runtime behavior;
- adding archive integration or automatic review generation.

## Recommended Next Slice

PR75 now exercises the scaffold with a deterministic readiness/shell run:
[Product Delta Eval Readiness And Provisional Run v0](product-delta-eval-readiness-and-provisional-run-v0.md).

PR76 fills the ready PR75 shells with Codex-assisted provisional semantic
reads: [Codex-Assisted Product Delta Batch v0](codex-assisted-product-delta-batch-v0.md).

The next recommended slice is PR77 Product Delta Provisional Report v0:
summarize PR75 readiness and PR76 provisional reads without human-validation
claims, judges, scores, automatic labels, runtime integration, or archive
mutation.

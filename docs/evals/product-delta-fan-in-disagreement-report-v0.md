# Product Delta Fan-In / Disagreement Report v0

Status: checked-in provisional report fixture

Slice: PR84 Fan-In / Disagreement Report v0

Report fixture:
[fan-in disagreement report JSON](../../reviews/codex-assisted/fan-in-disagreement-report-v0/report.json)

## Why PR84 Exists

PR84 asks a narrower question than PR83:

> What did specialist decomposition make more visible compared with the broad
> PR76 semantic fill?

The purpose is not to make the evidence bigger. It is to make the existing
tension easier to inspect. PR84 compares the broad PR76 Codex-assisted Product
Delta reads with the decomposed PR83 specialist-review reads, focusing on
disagreement preservation, downgrades, uncertainty, lost value, interpretation
adequacy, and human-review priorities.

PR84 is not a new semantic review. It does not create new specialist reads,
does not call any model, does not invoke runtime, and does not decide whether
PR76 or PR83 is right.

## Boundary

PR84 is Codex-assisted provisional reporting only. It is not human review,
ground truth, judge calibration data, product proof, answer-quality scoring,
automatic labeling, or agent-action authorization.

Boundary metadata in the report fixture records:

- `human_validated: false`
- `ground_truth: false`
- `judge_calibration_eligible: false`
- `product_proof: false`
- `answer_quality_scored: false`
- `agent_action_authorized: false`
- `model_calls: 0`
- `archive_mutated: false`
- `runtime_invoked: false`
- `skill_invoked: false`

No runtime artifacts, raw transcripts, raw revised answers, raw memos, private
archive content, provider APIs, or Lolla skill invocation were used.

## Inputs

PR84 reads only checked-in Product Delta eval artifacts:

- [Codex-Assisted Product Delta Batch v0](codex-assisted-product-delta-batch-v0.md)
- [PR76 broad batch JSON](../../reviews/codex-assisted/product-delta-batch-v0/review.json)
- [Codex-Assisted Specialist Review Batch v0](codex-assisted-specialist-review-batch-v0.md)
- [PR83 specialist batch JSON](../../reviews/codex-assisted/specialist-review-batch-v0/review.json)
- [Provisional Reviewer Trap Set v0](provisional-reviewer-trap-set-v0.md)
- [PR82 trap JSON](provisional-reviewer-trap-set-v0.json)
- [Product Delta Evidence Boundary Lint v0](product-delta-evidence-boundary-lint-v0.md)

The report intentionally uses the actual PR83 shape:

- trap records: `trap_discipline_pass.results`
- PR76 comparison: `real_case_specialist_pass.cases[*].case_summary.pr76_comparison`
- PR83 net read: `real_case_specialist_pass.cases[*].case_summary.pr83_net_decision_read_candidate`
- specialist reads: `real_case_specialist_pass.cases[*].specialist_reads`

## How PR84 Differs From PR83

PR83 created provisional specialist reads for traps and two real cases. PR84
does not.

PR84 is a deterministic/reporting layer over PR76 and PR83. It preserves the
comparison already present in PR83, then makes the fan-in consequences easier
to inspect:

- which broad PR76 reads stayed the same;
- which PR76 read was downgraded by PR83;
- which disagreements survived fan-in;
- where lost value stayed visible;
- where interpretation adequacy stayed unresolved;
- what a human should inspect next.

There is no majority vote, aggregate confidence, benchmark verdict, product
claim, or automatic decision.

## Comparison Scope

PR84 compares exactly the two real cases reviewed by PR83:

| case | PR76 broad read | PR83 specialist fan-in | comparison result |
| --- | --- | --- | --- |
| `ceo-remove-founding-cofounder` | `material_improvement_candidate` | `material_improvement_candidate` | Same net candidate, but PR83 makes interpretation adequacy and lost-value caveats stricter. |
| `accept-operations-role-startup` | `material_improvement_candidate` | `partial_improvement_candidate` | Downgraded from material to partial because lost value, value-overwrite risk, and gate proportion remain unresolved. |

PR84 also summarizes all ten PR82 trap families through PR83's trap discipline
output.

## Trap Discipline Summary

PR83 recorded these trap behavior counts:

| trap behavior | count |
| --- | ---: |
| `met_expected_behavior` | 8 |
| `partly_met_expected_behavior` | 2 |
| `missed_expected_behavior` | 0 |
| `inconclusive` | 0 |

The two partial trap families were:

- `ambition_buried_by_generic_prudence`
- `assistant_influence_blindness`

These are contract-expectation behavior counts, not accuracy, a benchmark
result, or evidence that specialist agreement is correctness.

## What Changed From PR76 To PR83

The central concrete change is the `accept-operations-role-startup` downgrade:

`material_improvement_candidate` -> `partial_improvement_candidate`

That is the healthiest PR84 signal. The specialist path made the evidence less
impressive in one real case, but more honest about unresolved lost value,
value/constraint interpretation, and written-gate proportion.

For `ceo-remove-founding-cofounder`, PR83 kept the same net material candidate
as PR76. PR84 still records a discipline delta: PR83 downgraded
interpretation adequacy from the broad PR76 read's `adequate` to a
`partly_adequate_candidate` specialist read because checked-in safe context
does not expose the raw conversation options or assistant influence.

## Where Disagreement Was Preserved

For `ceo-remove-founding-cofounder`, PR83 preserved two live tensions:

- PR76 treated interpretation as adequate, while PR83 marked the reviewability
  surface as only partly adequate.
- The structural delta is strong, but it conflicts with unresolved simplicity
  and momentum loss.

For `accept-operations-role-startup`, PR83 preserved two stronger tensions:

- The structural delta looks real, while friction/lost-value and interpretation
  reads warn against a material net claim.
- PR76 called the net read material, while PR83 fan-in downgraded it because
  decision leverage depends on proportion and values.

This is the point of fan-in here: preserve disagreement and missingness rather
than smoothing them into a cleaner story.

## Lost Value And Interpretation Adequacy

PR84 keeps lost value visible in both real cases:

- `ceo-remove-founding-cofounder`: simplicity and momentum may be lost when
  authority moves first and conflict becomes harder sooner.
- `accept-operations-role-startup`: momentum, courage, and user-specific
  ambition may be lost if written gates protect capacity while diluting a
  meaningful career appetite.

PR84 also keeps interpretation adequacy visible in both real cases:

- `ceo-remove-founding-cofounder`: the net candidate remains material, but the
  interpretation surface is thinner than PR76 made visible.
- `accept-operations-role-startup`: the specialist split makes values,
  household constraints, and written-gate proportion load-bearing rather than
  background caveats.

## Evidence Became Less Impressive But More Honest

PR84 may say this:

> PR83 made the evidence more conservative in one real case.

That is not a regression. It is the reason to decompose broad semantic review
into narrow specialist reads. If specialist decomposition cannot downgrade a
broad positive read, preserve uncertainty, or expose lost value, it is not
doing more disciplined review work.

PR84 does not show a no-material-change, added-noise, worse, or inconclusive
real-case candidate. That absence remains a selection risk, not a success
claim.

## Thinness And Selection Limits

The limits are first-class:

- only two real cases were compared;
- both came from the PR81 compact packet fixture;
- both had prior positive PR76 context;
- no real-case no-change, added-noise, worse, or inconclusive outcome appears;
- `positive_distribution_risk_acknowledged: true`;
- PR33 is used only as historical review-safe context, not fresh validation;
- no raw private content was read;
- no human validation is available.

Two cases are enough to inspect the reporting shape. They are not enough to
characterize product behavior.

## What PR84 Does Not Prove

PR84 does not prove:

- Lolla improves decisions;
- PR83 specialist review is calibrated;
- PR76 is wrong;
- PR83 is right;
- disagreement preservation is sufficient for correctness;
- trap behavior is accuracy;
- the two real cases represent the broader product surface;
- future agents may use these reads as labels or permissions.

PR84 is evidence about the review harness becoming more inspectable. It is not
evidence that the product improves decisions.

## Human Review Priorities

For `ceo-remove-founding-cofounder`, human review should check:

- whether vanilla left authority transfer too conditional;
- whether Lolla preserved enough trust while moving decision rights;
- whether early conflict is useful friction or avoidable lost momentum.

For `accept-operations-role-startup`, human review should check:

- whether vanilla already required written operating terms;
- whether the revised gates protected or diluted the user's ambition;
- whether deadlines and household-capacity tests were proportionate.

## Recommended Next Step

PR85 has now created the package gate for PR71-PR84:
[Product Delta PR71-PR84 Packaging Gate v0](product-delta-pr71-pr84-packaging-gate-v0.md).

The recommended stop point is to decide whether to stage/package PR71-PR85
explicitly, or pause until human review capacity returns. Further work should
not be another evidence-expansion PR by default.

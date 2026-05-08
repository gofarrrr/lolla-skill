# PR63 Zero-Absence Audit v25 Report

Date: 2026-05-08

## Verdict

REVISE before runtime pickup. PASS as dormant reviewed substrate.

PR63 audits the five v24 records that still had zero absence records. It adds five source-backed absence records where zero absence hid real reject/defer boundaries. It leaves three records unchanged where the current affordance already carries the relevant boundary tightly enough.

## Contradicting Evidence First

Zero absence is not automatically a defect.

Some records have no absence records because the current affordance already bundles activation, do-not-use conditions, evidence requirements, treatment requirements, and misuse guards into one compact operational contract. Filling those records for symmetry would make the corpus look more complete while making the handoff noisier.

The audit therefore used the same strict gate as PR62:

> Add an absence only when the source-backed distinction would change a future decoder's use, reject, defer, merge, or block decision.

## What Changed

Compiled artifact:

- `model_affordances_v25`
- `affordance_count`: unchanged at 268
- `absence_record_count`: 449 to 454
- `contributing_record_count`: unchanged at 222
- runtime status: dormant `draft_review_only`

Added absence records:

- `decision-trees`: `standalone-decision-tree-runtime-automation-affordance`
- `decision-trees`: `behavior-free-human-decision-tree`
- `decision-trees`: `exhaustive-option-tree-affordance`
- `power-dynamics`: `generic-disagreement-as-power-contest`
- `power-dynamics`: `winning-negotiation-without-opportunity-cost-check`

Remaining zero-absence records after v25:

- `lindy-effect`
- `premortem`
- `sunk-cost-fallacy`

Those three are intentional no-change records, not missed work in this pass.

## Why These Guards

`decision-trees` needed three no-promote boundaries.

First, the source uses AI agents, conditional prompts, digital twins, and workflows as examples of explicit branch logic. That does not authorize a standalone runtime automation affordance. A future decoder should use the existing branch-trigger affordance only when the case contains explicit conditions, thresholds, approvals, payoffs, and branch rules.

Second, the source warns that life does not always arrange itself neatly and that decision trees often omit psychological factors and behavioral tendencies. The new guard blocks treating a neat logical tree as adequate for human or social decisions when emotions, beliefs, wishes, desires, or behavioral tendencies materially affect the branches.

Third, the source supports pruning and prioritizing branches, not exhaustive option inventory. The new guard blocks option-sprawl trees that do not name what not to work on and risk decision paralysis.

`power-dynamics` needed two no-promote boundaries.

First, the source warns against seeing every disagreement as a power contest. A future decoder should reject power-dynamics routing when the better explanation is incentives, execution quality, product reality, or another non-leverage driver.

Second, the source names opportunity cost as an antagonist: power analysis can over-focus on winning the negotiation instead of asking whether the game is worth playing. A future decoder should defer toward opportunity-cost, optionality, or broader choice architecture when concession extraction is becoming the objective.

## Why Three Zero-Absence Records Stayed Unchanged

`lindy-effect` stays unchanged because the existing affordance already treats age as a qualitative durability prior, not proof. It requires non-perishable context, weak forecasting, and baseline-break checks for discontinuity, changing constraints, new evidence, and rare disruption.

`premortem` stays unchanged because the existing affordance already blocks generic worry lists, after-commitment criticism theater, and pro-con substitution. The source's strongest runtime boundary is already in the active contract: simulated failure must become owners, mitigations, thresholds, or decision changes.

`sunk-cost-fallacy` stays unchanged because the existing affordance already blocks both bad directions: irrational persistence because of prior investment, and reckless abandonment that ignores learning value, switching costs, or remaining upside.

## Risk Controls

PR63 keeps the runtime boundary unchanged:

- no `/lolla` pickup;
- no packet producer default change;
- no prompt changes;
- no automatic latest-artifact behavior;
- no compiled artifact import from live runtime paths.

The new PR63 test asserts that v25 is exactly v24 plus the five absence records and no new affordance IDs. It also asserts that the remaining zero-absence models are the intentional no-change set from this audit.

## What Would Falsify This Pass

This pass should be revised if any of the following happen:

- v25 adds a positive affordance or changes affordance IDs;
- source quote validation fails;
- a guard duplicates existing `do_not_use_when` text without changing future decoder behavior;
- a future packet treats these absence records as positive endorsed uses;
- `lindy-effect`, `premortem`, or `sunk-cost-fallacy` show replay failures where their existing misuse guards are not visible enough to affect rejection or deferral.

## Next Work

With the zero-absence audit complete, the next enrichment pass should move away from absence-count cleanup and toward under-compression review:

- inspect rich one-affordance records whose source may contain multiple distinct downstream transactions;
- mark split candidates only when activation, evidence, treatment, misuse guard, and receiver action differ;
- keep broad/meta cards under tighter scrutiny because their language can feel wise while carrying less concrete decision pressure.

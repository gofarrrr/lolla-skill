# Lane 2 Path D — archive audit report

Date: 2026-04-26
Rubric: `research/lane2-pathD-step6-wording-design-2026-04-26.md`

## Summary

- **38** anchor rows scored across **11** runs in **9** cases.
- **3** rows marked `uncertain=yes` for human review.
- **0** anchor-naming invariant failures (sketch must include `display_name` verbatim).

## Pooled metrics (gate evaluation)

| Metric | Value | Gate | Pass? |
|---|---|---|---|
| `baseline_overclaim_rate` | 0/38 = 0.0% | (context, not gated) | n/a |
| `baseline_hidden_rate` | 11/38 = 28.9% | (context, not gated) | n/a |
| `proposed_overclaim_rate` | 0/38 = 0.0% | ≤ 10% | ✅ |
| `primary_preservation` | 26/34 = 76.5% | ≥ 75% | ✅ |
| `secondary_framing` | 4/4 = 100.0% | ≥ 90% | ✅ |
| `not_mushy` | reviewer PASS with caveat | run-level pass | ✅ (caveat) |
| `anchor_naming_failures` | 0 | 0 | ✅ |

## Per-run metrics

| Case / Run | N anchors | Hidden | Baseline overclaim | Proposed overclaim | Primary-eligible | Primary preserved | Non-primary-eligible | Secondary framed | Uncertain |
|---|---|---|---|---|---|---|---|---|---|
| `founder-grant-marcus-equity/0260425T114200Z` | 5 | 1 | 0 | 0 | 5 | 4/5 | 0 | n/a | 0 |
| `grant-equity-partnership-status/0260422T100308Z` | 4 | 0 | 0 | 0 | 4 | 3/4 | 0 | n/a | 1 |
| `grant-equity-partnership-status/0260422T113930Z` | 1 | 0 | 0 | 0 | 1 | 1/1 | 0 | n/a | 0 |
| `grant-equity-partnership-status/0260422T155622Z` | 2 | 0 | 0 | 0 | 2 | 2/2 | 0 | n/a | 0 |
| `marcus-equity/0260422T091837Z` | 2 | 0 | 0 | 0 | 2 | 0/2 | 0 | n/a | 0 |
| `mid-level-consultant-decides/0260425T110621Z` | 5 | 4 | 0 | 0 | 4 | 2/4 | 1 | 1/1 | 0 |
| `mid-level-consultant-report/0260424T124651Z` | 3 | 2 | 0 | 0 | 3 | 2/3 | 0 | n/a | 0 |
| `mother-deciding-address-year/0260424T124626Z` | 5 | 2 | 0 | 0 | 4 | 3/4 | 1 | 1/1 | 0 |
| `third-year-phd-student/0260425T122400Z` | 5 | 1 | 0 | 0 | 3 | 3/3 | 2 | 2/2 | 2 |
| `user-launch-independent-fintech/0260424T123050Z` | 2 | 1 | 0 | 0 | 2 | 2/2 | 0 | n/a | 0 |
| `year-old-oncologist-accept/0260425T121607Z` | 4 | 0 | 0 | 0 | 4 | 4/4 | 0 | n/a | 0 |

## Reviewer surface (your part)

Per the rubric (Section 9c), implementer-scored audit + reviewer audits a high-leverage subset:

- **All Marcus rows:** 7
- **All `proposed_treatment ∈ {primary pressure, set aside with a reason}` rows:** 32
- **All `uncertain=yes` rows:** 3
- **All anchor-naming invariant failures:** 0
- **Total deduped reviewer surface:** 33 of 38 rows.

## Headline findings

1. **The dominant baseline failure mode is silent omission, not overclaim.** 11/38 = 28.9% of anchors are hidden in the current `revised_answer`s. Baseline overclaim rate is 0.0%. This reframes the Path D pivot: the wording rules are not primarily about reducing overclaim (there's little to reduce); they're about restoring the anchor-naming invariant when Step 6 currently drops anchors.
2. **Hidden anchors concentrate on the consultant cases.** mid-level-consultant-decides has 4 of 5 anchors hidden (80%); mid-level-consultant-report has 2 of 3 hidden (67%). These are exactly the cases the PR #39 sanity check flagged as low-Step-6-consumption (20% and 33%).
3. **The proposed wording rules add Lane 2 anchor coverage without adding overclaim.** Proposed overclaim rate is 0.0%, well below the 10% gate. The rules cover the 11 hidden anchors via secondary-lens or set-aside framing, with full anchor-naming invariant compliance (38/38).

### Reviewer addendum (2026-04-26): not_mushy = PASS with caveat

After grouped review of the 38 proposed sketches: the rewrites are mostly sharp and do not collapse into "everything might apply" hedging. Sketches still make definite primary reads where evidence supports one (Confidence Calibration for consultant; Feedback Loops for mother; Premortem / Base Rates / Problem Framing And Reframing for phd; Inversion / Optionality / Opportunity Cost for the equity cases; etc.).

**Caveat to carry into the SKILL.md edit:** the wording rules per-anchor are sound, but if Step 6 mechanically *enumerates* every anchor in sequence the output collapses into a checklist regardless of how good each individual sketch is. The implementation must include an explicit instruction to **integrate anchors into the existing §1 / §2 / §3 reasoning by treatment strength**, not list them as a separate parade.

This is a prompt-side risk, not an audit-rubric problem. The live-validation step on the 4 required cases is the right place to catch enumerative drift.

### Distribution shifts

| Category | Current classification | Proposed treatment | Proposed classification |
|---|---|---|---|
| appropriate-primary | 22 | 0 | 26 |
| appropriate-secondary | 1 | 0 | 6 |
| appropriate-set-aside | 4 | 0 | 6 |
| hidden | 11 | 0 | 0 |
| primary pressure | 0 | 26 | 0 |
| secondary lens | 0 | 6 | 0 |
| set aside with a reason | 0 | 6 | 0 |

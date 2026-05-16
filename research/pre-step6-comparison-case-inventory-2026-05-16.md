# Pre-Step-6 Comparison Case Inventory

Date: 2026-05-16

Status: research planning only. This does not change runtime behavior,
`SKILL.md`, `HOW_IT_WORKS.md`, default `/lolla`, product docs, Lane 1, V60, the
canonical knowledge base, or public output.

Related docs:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
```

## Purpose

This inventory selects candidate cases for the comparison-first slice:

```text
current control
raw reasoning_artifact.v1 specimens
indexed reasoning_bundle.v1
```

The goal is not to re-audit these cases. The goal is to find small, already
available situations where the bundle should prove whether it helps Step 6
consume pressure better than raw compact artifacts.

## Source Material

Primary local sources:

```text
data/treatment_audits/summary.v1.json
data/treatment_audits/calibration_report_pr6.md
data/treatment_audits/founder-grant-marcus-equity__20260428T064421Z.v1.json
data/treatment_audits/mid-level-consultant-report-2__20260429T144611Z.v1.json
data/treatment_audits/mother-deciding-address-year__20260430T113301Z.v1.json
data/treatment_audits/third-year-phd-student__20260430T140800Z.v1.json
data/treatment_audits/user-launch-independent-fintech__20260424T123050Z.v1.json
```

The calibration report is useful because it already separates:

- Tier 1 net-new decision gaps;
- Tier 2 additional operational specificity;
- Tier 3 duplicate or quality notes;
- not-activated items;
- set-aside-as-misfit items.

That makes it a good source for testing duplicate demotion, conflict
preservation, quiet/discard handling, and worker-should-not-run outcomes.

## Recommended First Three Cases

Start with three cases, not five. The first comparison should stay small enough
to inspect manually.

| Case | Source run | Reasoning shape | Why it is useful |
| --- | --- | --- | --- |
| PhD direction choice | `third-year-phd-student__20260430T140800Z` | Conflict / constraint / fallback viability | Has competing pressure around option 3, advisor politics, Silva as bottleneck, base-rate claims, reversal triggers, and whether the option-1 fallback remains executable. Tests whether a bundle preserves tension instead of smoothing it. |
| Founder equity grant | `founder-grant-marcus-equity__20260428T064421Z` | Duplicate / low marginal value / systems pressure | Has duplicate examples already covered by pressure check plus possible net-new systems-thinking gaps. Tests whether the bundle can demote duplicates while preserving one useful new pressure. |
| Consultant whistleblower | `mid-level-consultant-report-2__20260429T144611Z` | Hard boundary / option expansion / misfit discard | Legal-adjacent and high-stakes. Has reversible counsel engagement vs irreversible filing, partner reaction risk, and power-dynamics items explicitly set aside as misfit. Tests boundary preservation and discard handling. |

## Expansion Cases

Add these only after the first three reveal whether the comparison format is
usable.

| Case | Source run | Reasoning shape | Why it is useful |
| --- | --- | --- | --- |
| Mother deciding address year | `mother-deciding-address-year__20260430T113301Z` | Overclaim / calibration / no-worker sentinel | Has confidence-calibration gaps, instrument-trust weakness, duplicate base-rate notes, and not-activated power-dynamics items. Good for testing whether workers should decline rather than force a leverage lens. |
| Independent fintech launch | `user-launch-independent-fintech__20260424T123050Z` | Overclaim / low marginal value / set-aside | Has base-rate/reference-class weakness and an optionality item set aside due to Q3 notice costs. Good for testing whether the bundle can keep an attractive optionality idea quiet. |

## Case-To-Shape Map

| Required shape | Primary candidate | Backup candidate |
| --- | --- | --- |
| Artifacts duplicate each other | Founder equity grant | Mother address year |
| Artifacts conflict or create unresolved tension | PhD direction choice | Consultant whistleblower |
| Hard boundary survives attractive relaxation | Consultant whistleblower | PhD direction choice |
| Correct but low marginal value | Founder equity grant | Independent fintech launch |
| Artifact tempts overclaim | Mother address year | Independent fintech launch |
| Worker should not run | Mother address year | Consultant whistleblower |

## Candidate Artifact Seeds

These are not final fixtures. They are starting points for manual artifact
construction.

### PhD Direction Choice

Useful seeds:

- Base-rate pressure exists, but reference-class fit was under-specified.
- Silva/data access is a binding constraint and may shift after probing.
- Advisor retirement creates principal-agent pressure and may make fallback
  timing non-real.
- Option expansion pressure competes with the need to commit by the committee
  deadline.

Bundle risk:

- The bundle may pick one clean answer too early and erase real unresolved
  tension between ambition, data access, advisor incentives, and fallback
  viability.

### Founder Equity Grant

Useful seeds:

- Several pressures are duplicates of existing pressure-check material:
  unaudited exit valuation, intermediate equity options, and assumptions inside
  the "I built this" frame.
- Possible new pressure sits in systems-thinking: feedback loops, actor
  adaptations, and goal-process-lever-metric chains.

Bundle risk:

- Duplicate pressure may become amplification. The bundle should demote repeated
  base-rate/optionality points and preserve only the pressure that changes the
  final answer.

### Consultant Whistleblower

Useful seeds:

- Reversible counsel engagement and irreversible filing are distinct decisions.
- Optionality expansion may help, but must not trivialize legal risk.
- Partner reaction/adaptation matters if internal reporting alerts the actor.
- Power-dynamics items can be structurally misfit and should stay discarded.

Bundle risk:

- The bundle may over-expand options in a way that weakens the hard boundary:
  do not investigate privately, do not confront the partner, do not file before
  counsel has reviewed evidence.

### Mother Address Year

Useful seeds:

- Confidence calibration and instrument trust are live concerns.
- Some power-dynamics affordances were not activated in the family context.
- Base-rate language may appear as duplicate or weak support rather than a
  load-bearing claim.

Bundle risk:

- A worker could force a leverage/negotiation lens where the better answer is
  calibration and protection of fallback options.

### Independent Fintech Launch

Useful seeds:

- Base-rate/reference-class fit is under-specified.
- Optionality may be attractive but was partly set aside because notice timing
  changes the commitment boundary.

Bundle risk:

- The bundle may make a low-marginal optionality point look more important than
  the actual timing/commitment constraint.

## Fixture Rules

For each selected case:

```text
max artifacts: 2-5
max source excerpts: 4
no full transcript
no full lane cards
no full V60 payload
no public machinery terms in final-answer prompts
```

Each fixture should include:

```text
case_id
source_run_id
reasoning_shape
current_control_summary
raw_artifacts
reasoning_bundle_index
expected_failure_mode
win_condition
kill_condition
```

## First Fixture Order

Build in this order:

1. `third-year-phd-student__20260430T140800Z`
2. `founder-grant-marcus-equity__20260428T064421Z`
3. `mid-level-consultant-report-2__20260429T144611Z`

First fixture:

```text
research/pre-step6-comparison-fixtures/third-year-phd-student-20260430T140800Z.md
```

Second fixture:

```text
research/pre-step6-comparison-fixtures/founder-grant-marcus-equity-20260428T064421Z.md
```

Reason:

- the PhD case stresses conflict and fallback viability;
- the founder case stresses duplicate demotion;
- the consultant case stresses hard boundaries and misfit discard.

If the bundle cannot help across those three shapes, do not proceed to worker
implementation.

## Stop Rule

Do not add more cases because the first comparison is inconclusive. First ask
why it was inconclusive:

- Were the artifacts too raw?
- Was the bundle too editorial?
- Was the current control already good enough?
- Did the final reasoner ignore the handoff?
- Did the case not actually activate the target shape?

Only add cases after answering that.

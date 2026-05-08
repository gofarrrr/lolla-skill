# Gate 4 3-Case Decision Pressure v4 Dry Review

**Date:** 2026-05-05
**Status:** Docs/research-only dry review. No generation run, no runtime
behavior, no prompt changes, no validator changes, no judge calls, no paid
model calls, no new extraction, and no product-surface promotion.

**Branch:** `feature/decision-pressure-pr17-v4-decision-pressure-dry-review`

**Doctrine line:** Surface pulls extraction. Extraction does not push the
product.

## Question

Does v4 improve compact Decision Pressure under the same gates, or did Batch 3a
only improve coverage statistics?

Short answer:

> v4 improves field quality and coverage honesty for the same compact surface.
> It does not justify changing the selected pressure set, filling the
> competitive-dynamics blank, starting Batch 3b, or promoting Decision Pressure
> into runtime.

Decision label: `v4_improves_fields_without_changing_selection`

## Method

This review compares the PR13 v3 dry surface and PR14 stability result against
v4 availability after PR16 Batch 3a extraction.

Inputs:

- `research/gate4-3case-decision-pressure-dry-surface-2026-05-05.md`
- `research/gate4-3case-decision-pressure-selection-stability-review-2026-05-05.md`
- `research/affordance-batch3a-coverage-priority-2026-05-05.md`
- `research/affordance-batch3a-extraction-brief-2026-05-05.md`
- `research/pr16-batch3a-extraction-report-2026-05-05.md`
- `research/decision-pressure-surface-spec-2026-05-05.md`
- `data/compiled/model_affordances/affordances_v3.json`
- `data/compiled/model_affordances/affordances_v4.json`
- `data/model_affordances/batch_3a/*.json`

This is not formal Gate 4 evidence. It is not a model-output rerun. It does not
claim actual Arm C output changed. It asks what a reviewer can now honestly say
with v4 available, while applying the same Decision Pressure gates:

1. Coverage Gate
2. Action-Delta Gate
3. Dismissal Gate
4. Bloat Gate
5. Compression Gate
6. Tone Gate

## v4 Batch 3a Contribution Summary

| Model | Record strength | Relevant pressure fields improved | Likely pressure clusters affected | Risks / do-not-promote cautions |
| --- | --- | --- | --- | --- |
| `opportunity-cost` | `strong_affordance_record`; one affordance, two absences | `What to verify`, `Dismiss if`, `Tripwire or next action`, suppression rationale | PhD resource-allocation, equity resource-allocation, equity stakeholder-alignment | Do not promote generic trade-off talk; require a real executable next-best alternative and a stop condition. |
| `true-uncertainty-navigation` | `strong_affordance_record`; one affordance, two absences | `What to verify`, `Tripwire or next action`, coverage honesty | Mother uncertainty-type, PhD uncertainty-type | Do not turn scenarios into theater or use uncertainty language to postpone action after a robust next move exists. |
| `falsifiability` | `strong_affordance_record`; one affordance, two absences | `Dismiss if`, `Tripwire or next action`, suppression rationale | PhD information-quality, equity information-quality, equity 90-day sprint | Do not invent tidy kill criteria; require user-verifiable disconfirming evidence or reversal conditions. |
| `principal-agent-problem` | `thin_narrow_affordance_record`; one affordance, three absences; medium confidence | `What to verify`, `Dismiss if`, suppression rationale | PhD incentive-alignment, mother incentive-alignment | Do not turn delegated alignment into bad-faith suspicion, micromanagement, or AI-agent orchestration. |
| `probabilistic-thinking` | `strong_affordance_record`; one affordance, three absences | `What to verify`, `Tripwire or next action`, coverage honesty | Mother uncertainty-type, PhD uncertainty-type | Do not create exact-looking probabilities, false precision, or commitment delay disguised as rigor. |

v4 gives the surface better material for dismissal, tripwires, stop conditions,
and coverage honesty. The strongest new affordance for selected pressure wording
is `opportunity-cost.displaced-alternative-commitment-gate`. The strongest new
affordance for suppression discipline is
`principal-agent-problem.delegated-alignment-drift-audit`, precisely because it
also says when not to use the model.

## Original Selected Pressures Recheck

### 1. Equity Governance Deadlock Before Vesting

**Original source route/case:** `grant-equity-partnership-status / risk-response`

**Original selection status:** Selected in PR13 and selected again in PR14. The
route was already fully covered in v3 through risk-response records.

**v4 contribution:** `minor`

**What improves:** v4 does not materially improve the core governance-deadlock
pressure. `opportunity-cost` can lightly reinforce that the equity grant is not
free if it forecloses cap-table flexibility, but the selected pressure is still
mostly a risk-response and governance design issue.

**What should not change:** Do not replace this pressure with a resource-
allocation framing. The user action remains: define decision rights,
conflict-resolution path, and buyback or mediation trigger before signing.

**Verdict:** `keep`

### 2. Safety Plan Using A Gameable Signal

**Original source route/case:** `mother-deciding-address-year / uncertainty-type`,
with support from `mother-deciding-address-year / incentive-alignment`

**Original selection status:** Selected in PR13 and selected again in PR14.

**v4 contribution:** `material`

**What improves:** v4 makes the selected pressure easier to ground without
overclaiming. `true-uncertainty-navigation` supports acting robustly under
ambiguity without scenario theater. `probabilistic-thinking` strengthens the
false-confidence guard: absence of detected contact should not be treated as a
high-certainty safety estimate. `principal-agent-problem` gives better language
for party-controlled or gameable evidence while warning against bad-faith
framing.

The improved dry wording would be:

> Before relying on the 3-4 week delay, verify that the safety signal is not
> controlled by the party whose behavior it is meant to reveal. If the monitored
> channel is incomplete or gameable, add an independent, non-coercive signal
> before treating absence of detection as evidence of safety.

**What should not change:** Do not turn this into a suspicion pressure about
the daughter. The pressure is about signal quality, safety timing, and coverage
honesty. Do not add numeric probability language unless there is evidence for a
decision-relevant range.

**Verdict:** `revise wording`

### 3. Shaping Phase Without A Stop Condition

**Original source route/case:** `third-year-phd-student / resource-allocation`,
with support from `third-year-phd-student / information-quality`

**Original selection status:** Selected in PR13 and selected again in PR14.

**v4 contribution:** `material`

**What improves:** v4 directly strengthens this pressure. `opportunity-cost`
turns the advisor-retirement clock into a real displaced-alternative and stop-
condition question: what scarce advisor time, committee attention, or thesis
option is lost if shaping stays open-ended? `falsifiability` makes the shaping
contract more dismissible by requiring a disconfirming or completion condition.

The improved dry wording would be:

> Before the literature search starts, write the shaping contract: the question
> it must answer, the next-best use of the same advisor time, the evidence that
> would end the phase, and the decision that follows if the question is not
> resolved by the stop date.

**What should not change:** Do not split this into separate resource-allocation
and information-quality pressures. The compact product surface is stronger when
the falsifiable hypothesis and stop condition are merged into one shaping gate.

**Verdict:** `revise wording`

## Suppressed Candidate Recheck

### PhD / Incentive-Alignment: Contingent Checkpoint On Heuristic Work

**Original suppression reason:** Strong Observatory candidate, but lost to the
Compression Gate. It was less immediately installable than the shaping contract.

**Relevant v4 records:** `principal-agent-problem`,
`opportunity-cost`, `falsifiability`

**Does suppression still hold?** Yes, but less absolutely. v4 makes the
checkpoint-design concern sharper: delegated effort, hidden incentives, and
metric-like compliance can distort PhD work. It also adds important cautions:
do not assume bad faith, do not micromanage, and distinguish alignment drift
from capability, capacity, or unclear goals.

**Could this become a fourth pressure, replacement pressure, or merged
support?** It should become merged support, not a fourth pressure. The selected
shaping-phase pressure can absorb one line: the shaping contract should not
turn into a performative checkpoint that rewards safe-looking progress over
the hard heuristic work the PhD may require.

**Verdict:** `merge_into_existing`

### Equity / Resource-Allocation: 90-Day Sprint Hypothesis And Kill Criteria

**Original suppression reason:** Useful, but overlapped with the selected PhD
stop-condition pressure and was second-best within the equity case behind the
governance deadlock.

**Relevant v4 records:** `opportunity-cost`, `falsifiability`

**Does suppression still hold?** Yes. v4 makes the suppressed candidate better:
the 90-day sprint should name the displaced work and the evidence that would
kill the sprint. But the governance deadlock remains more irreversible and more
specific to the equity commitment.

**Could this become a fourth pressure, replacement pressure, or merged
support?** It can remain Observatory material or a note under equity, but it
should not replace the selected governance pressure. It should not become a
fourth pressure unless a future product policy allows more than three pressures
for a run.

**Verdict:** `still_suppressed`

### Equity / Stakeholder-Alignment: Walk-Away Alternatives

**Original suppression reason:** Useful, but lower immediate irreversibility
than governance deadlock.

**Relevant v4 records:** `opportunity-cost`

**Does suppression still hold?** Yes. `opportunity-cost` improves the walk-away
candidate by requiring a real executable next-best alternative, but the missing
`batna` record means v4 still does not provide the clean negotiation substrate
that would make this a selected pressure.

**Could this become a fourth pressure, replacement pressure, or merged
support?** No for this dry surface. It remains good Observatory material.

**Verdict:** `still_suppressed`

### Mother / Incentive-Alignment: Party-Controlled Evidence Or Gameable Signal

**Original suppression reason:** Merged into the selected mother uncertainty
pressure.

**Relevant v4 records:** `principal-agent-problem`,
`probabilistic-thinking`, `true-uncertainty-navigation`

**Does suppression still hold?** Yes. v4 makes the merged support cleaner by
naming the danger of dashboards or reported activity standing in for real
alignment, while warning against bad-faith framing.

**Could this become a fourth pressure, replacement pressure, or merged
support?** It should stay merged into the selected safety-signal pressure. A
separate incentive-alignment pressure would risk blaming the daughter and
violating the Tone Gate.

**Verdict:** `merge_into_existing`

### PhD / Information-Quality: Falsifiable Hypothesis Before Literature Search

**Original suppression reason:** Merged into the selected PhD shaping-phase
pressure.

**Relevant v4 records:** `falsifiability`, `opportunity-cost`

**Does suppression still hold?** Yes. v4 materially improves the merged field
quality. The selected shaping contract should now require the question, the
evidence that would end the phase, and what would cause the literature-search
path to be revised.

**Could this become a fourth pressure, replacement pressure, or merged
support?** It should remain merged support. A standalone information-quality
pressure would duplicate the shaping stop-condition pressure and add bloat.

**Verdict:** `merge_into_existing`

### PhD / Uncertainty-Type: 18-Month Checkpoint Calibrated To An Optimistic Center Story

**Original suppression reason:** Useful but close to B and less action-clear
than the shaping-phase gate.

**Relevant v4 records:** `true-uncertainty-navigation`,
`probabilistic-thinking`

**Does suppression still hold?** Yes. v4 improves the language for confidence
ranges, lower-bound planning, and false precision, but the candidate still does
not beat the shaping-phase stop condition under the Compression Gate.

**Could this become a fourth pressure, replacement pressure, or merged
support?** It can remain Observatory material. It might become relevant if a
future generated v4 pass shows the 18-month milestone is the user's true next
decision, but this dry review should not promote it.

**Verdict:** `needs_generation_test`

## Coverage Transparency Recheck

### PhD / Competitive-Dynamics

**Original status:** Zero-output candidate. Full coverage gap in v3 because the
route depended on the missing game-theory cluster:

- `game-theory-payoffs`
- `nash-equilibrium`
- `prisoners-dilemma`
- `batna`
- `red-queen-effect`

**v4 change:** No change. PR16 added:

- `opportunity-cost`
- `true-uncertainty-navigation`
- `falsifiability`
- `principal-agent-problem`
- `probabilistic-thinking`

It did not add the game-theory cluster. Therefore the correct behavior remains
coverage transparency / zero-output.

Correct dry output:

> No substrate-backed competitive-dynamics pressure is available for this route
> because the routed game-theory cluster still lacks reviewed affordance
> records.

Do not smooth over this blank merely because v4 exists. This is the clearest
trust-preserving result in the review.

## Field-Level Delta

| Field | v4 delta | Notes |
| --- | --- | --- |
| `What to verify` | Improved | Strongest gains from `opportunity-cost`, `falsifiability`, and `principal-agent-problem`: verify the real next-best alternative, reversal condition, and alignment evidence. |
| `Dismiss if` | Improved | Strongest gains from `falsifiability` and `opportunity-cost`: dismiss when no real alternative exists, when the reversal condition is cleared, or when alignment evidence is sufficient. |
| `Tripwire or next action` | Improved | Strongest gains from `opportunity-cost`, `true-uncertainty-navigation`, and `probabilistic-thinking`: stop conditions, commitment-shape triggers, and update rules. |
| `Coverage` | Improved | Partial gaps for the selected mother and PhD pressures shrink, but competitive-dynamics remains a full gap. |
| `Provenance` | Improved cautiously | v4 allows better future traces, but this PR does not claim existing Arm C output changed. |
| `Suppression rationale` | Improved | v4 clarifies why principal-agent, falsifiability, and opportunity-cost candidates should often merge into selected pressures rather than create new ones. |

## New Risks Introduced By v4

| Risk | Review |
| --- | --- |
| Bloat | Real risk. v4 makes more candidates look defensible. The Compression Gate must stay hard. |
| Duplicate pressure | Real risk for falsifiability and opportunity-cost. They can sharpen many pressures, but not every sharpened field deserves its own pressure. |
| Fake precision | Real risk from `probabilistic-thinking`. The record's own do-not-promote cautions should be preserved. |
| Bad-faith framing | Real risk from `principal-agent-problem`. The record is medium-confidence and should not turn misalignment into suspicion. |
| Micromanagement theater | Real risk from `principal-agent-problem`. Do not replace machine-level design with case-level supervision. |
| Coverage theater | Reduced for the five Batch 3a gaps, unchanged for competitive-dynamics. Do not pretend v4 covers missing game-theory records. |
| Overclaiming from thin records | Highest for `principal-agent-problem`. Keep the thin/medium-confidence signal visible. |

## Decision

`v4_improves_fields_without_changing_selection`

Interpretation:

- The PR13/PR14 selected pressure clusters still hold.
- v4 materially sharpens two selected pressures: mother safety-signal and PhD
  shaping stop-condition.
- v4 provides minor support for equity governance, but the original v3
  risk-response basis remains sufficient.
- v4 makes several suppressed candidates more useful as merged support or
  Observatory material.
- v4 does not justify a fourth pressure.
- v4 does not change zero-output for PhD competitive-dynamics.
- v4 does not justify Batch 3b, a paid Gate 4 rerun, runtime promotion, or a
  receiving-surface integration.

## Recommendation

1. Merge PR16 as an extraction patch if reviewer agrees the records and v4
   compile are clean.
2. Merge PR17 as a dry product-delta review if reviewer agrees with the
   `v4_improves_fields_without_changing_selection` decision.
3. Do not start Batch 3b.
4. Do not run paid Gate 4 again by default.
5. Do not promote Decision Pressure into `/lolla`, memo, Step 8, Step 6, or
   user-facing output.
6. The next useful checkpoint can be a tiny no-paid, manual Observatory-only
   prototype that shows the same three pressures with v4-sharpened fields and
   explicit coverage transparency.

That prototype should not be runtime integration. It should be a static or
manual research artifact whose only product question is:

> Does the reviewed Decision Pressure object make the Observatory trace clearer
> and more trustworthy without becoming another public block?

If that prototype starts changing pressure selection, wording, or user-facing
claims substantially, pause and run another narrow reviewer pass before any
runtime work.

## Open Questions

- Should the post-v4 surface keep a hard cap of `1-3` pressures, or can a
  manual Observatory trace show additional suppressed candidates without
  implying user-facing selection?
- Should `principal-agent-problem` require an explicit medium-confidence badge
  in any future trace to prevent overclaiming?
- Should competitive-dynamics remain zero-output until the whole game-theory
  cluster is extracted, or would a later targeted `batna` record alone be
  enough for negotiation-style pressures?

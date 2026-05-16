# Pre-Step-6 Comparison Fixture: Mid-Level Consultant Report

Date: 2026-05-16

Status: manual research fixture v0. This is not runtime code, not a prompt
contract, not legal advice, and not product behavior.

Related docs:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
research/pre-step6-comparison-case-inventory-2026-05-16.md
```

Primary sources:

```text
data/treatment_audits/mid-level-consultant-report-2__20260429T144611Z.v1.json
data/treatment_audits/calibration_report_pr6.md
data/treatment_audits/summary.v1.json
```

## Case Brief

```text
case_id: mid-level-consultant-report-2
source_run_id: mid-level-consultant-report-2__20260429T144611Z
reasoning_shape: hard boundary / option expansion / misfit discard
```

The user is a mid-level consultant who saw a senior partner apparently shredding
boxes tied to an active regulatory-audit client. The user is the sole witness,
has family financial risk, and has only a 60-65% gut confidence that internal
general counsel would handle the issue properly.

The current Step 6-style answer preserved a cautious sequence:

```text
document observation personally
contact 2-3 whistleblower attorneys
tell spouse in broad strokes
attend Wednesday normally
do not confront the partner
do not investigate privately
do not access systems unusually
let counsel evaluate internal-vs-external reporting
```

The pressure check added specific gaps: counsel has its own incentive structure,
Wednesday needs a behavioral protocol, internal channels are not monolithic, and
career-risk preparation needs tripwires rather than blanket dread.

## Source Excerpts

Keep excerpts compact. These are paraphrased or lightly compressed from the
local treatment-audit artifacts.

1. Case context: active regulatory audit, senior partner with revenue/political
   weight, sole witness, no prior documentation, mortgage and two kids entering
   high school.
2. Current answer: do not confront, do not investigate, do not access systems
   unusually, and engage counsel before filing or choosing channel.
3. Pressure check: whistleblower attorneys may have contingency incentives that
   pull toward filing, so the user should ask about internal-first cases.
4. Pressure check: general counsel and audit committee are structurally
   different internal channels; treating "internal" as one thing missed a
   decision-relevant distinction.

## Current-Control Summary

The current control answer is already strong in several ways:

- it separates reversible counsel engagement from irreversible reporting;
- it corrects overcommitment to external filing before evidence review;
- it keeps the high-risk boundaries explicit: no confrontation, no private
  investigation, no unusual system access;
- it recognizes that internal reporting may alert the partner and accelerate
  destruction;
- it sets aside power-dynamics leverage language as a poor fit for a
  non-negotiated reporting decision.

Known weaknesses from the treatment audit and pressure check:

- option expansion is incomplete: internal is treated too monolithically;
- counsel is treated as final arbiter without pricing counsel incentives;
- Wednesday meeting behavior is under-specified;
- career-risk planning needs concrete tripwires;
- several power-dynamics and systems affordances are misfit or not activated and
  should not be forced.

## Raw reasoning_artifact.v1 Specimens

These are hand-authored specimens. They test handoff value, not producer quality.

### Artifact A: Counsel Incentive Gate

```text
schema_version: reasoning_artifact.v1
artifact_id: consultant_counsel_incentive_gate
worker_type: boundary/evidence-gate
why_provided: The pressure check says counsel is necessary but not incentive-free.
source_grounding: Whistleblower attorneys may work on contingency against regulator awards, creating a structural pull toward filing.
contribution: Keep counsel-first sequencing, but add an intake question that tests counsel's channel bias.
hard_boundary: Do not replace counsel with self-directed reporting; use the incentive gate inside counsel selection.
relaxation_condition: Counsel can explain cases where they advised internal-first or audit-committee-first and why.
discard_condition: Discard if the final answer does not tell the user to let counsel decide the reporting channel.
relation_to_bundle: primary / boundary
priority_hint: high
risk_if_forced: The answer may make the user distrust counsel and act alone.
risk_if_ignored: The user may outsource judgment to an advisor whose incentives are unexamined.
```

### Artifact B: Wednesday Protocol Boundary

```text
schema_version: reasoning_artifact.v1
artifact_id: consultant_wednesday_protocol_boundary
worker_type: boundary/evidence-gate
why_provided: The pressure check says "attend normally" is not actionable enough if the partner raises the encounter.
source_grounding: The user has a Wednesday meeting with the partner after seeing the early-morning shredding; pressure check calls for a pre-decided response and tripwire.
contribution: Turn "act normal" into a specific behavioral protocol that preserves safety and evidence integrity.
hard_boundary: Do not deny, elaborate, confront, investigate, or be alone with the partner if avoidable without making a memorable deviation.
relaxation_condition: Counsel gives a different script before the meeting.
discard_condition: Discard if the final answer is not addressing the immediate Wednesday interaction.
relation_to_bundle: primary / boundary
priority_hint: high
risk_if_forced: The answer may over-script and make the user behave unnaturally.
risk_if_ignored: The user may improvise under pressure and create avoidable risk.
```

### Artifact C: Internal Channel Distinction

```text
schema_version: reasoning_artifact.v1
artifact_id: consultant_internal_channel_distinction
worker_type: boundary/evidence-gate
why_provided: The pressure check says "internal" was treated as monolithic even though GC and audit committee differ structurally.
source_grounding: General counsel and audit committee have different incentives and oversight duties; audit interference belongs closer to audit-committee oversight than generic HR/legal escalation.
contribution: Expand the option set without weakening counsel-first sequencing.
hard_boundary: Do not advise internal reporting directly; ask counsel to evaluate GC vs audit committee vs external regulator as distinct channels.
relaxation_condition: Counsel says audit committee access is unavailable, unsafe, or legally inappropriate in this structure.
discard_condition: Discard if no internal channel is being considered at all after counsel review.
relation_to_bundle: support / conflict
priority_hint: medium
risk_if_forced: The answer may imply the user should bypass counsel and pick a channel alone.
risk_if_ignored: The answer may overstate the external-vs-internal binary and miss a safer oversight path.
```

### Artifact D: Reversibility And Tripwire Plan

```text
schema_version: reasoning_artifact.v1
artifact_id: consultant_reversibility_tripwire_plan
worker_type: boundary/evidence-gate
why_provided: Optionality is partially treated: counsel engagement is reversible, but commitment boundaries and career tripwires need specificity.
source_grounding: Current answer separates counsel engagement from filing; pressure check asks for observable retaliation tripwires and a specific runway figure.
contribution: Convert vague fear into observable gates: reporting go/no-go timing, retaliation signals, and financial runway thresholds.
hard_boundary: Do not let tripwires become delay tactics before counsel engagement or evidence preservation.
relaxation_condition: Counsel gives a filing timeline and employer-response risk model that supersedes the provisional tripwires.
discard_condition: Discard if the final answer is only about tonight's documentation and attorney calls.
relation_to_bundle: support / boundary
priority_hint: medium
risk_if_forced: The answer may create a complex planning burden before the user has counsel.
risk_if_ignored: The user may scan every work interaction for danger instead of watching concrete signals.
```

### Artifact E: Power-Dynamics Misfit Discard

```text
schema_version: reasoning_artifact.v1
artifact_id: consultant_power_dynamics_misfit_discard
worker_type: duplicate/priority
why_provided: The treatment audit and current answer explicitly set aside power-dynamics leverage language as mismatched to the case.
source_grounding: The user is not negotiating with the partner; they are choosing whether and how to report a likely crime with counsel.
contribution: Keep leverage/walk-away framing out of the final answer except as a private discard receipt.
hard_boundary: Do not turn this into a negotiation or bargaining-power problem.
relaxation_condition: New facts make the task an actual negotiation over employment terms rather than evidence/reporting sequence.
discard_condition: Discard after confirming the final answer does not use leverage framing.
relation_to_bundle: discard candidate / boundary
priority_hint: quiet
risk_if_forced: The answer may normalize bargaining with or around the partner instead of preserving evidence and legal safety.
risk_if_ignored: A worker may reintroduce attractive but structurally wrong leverage advice.
```

## reasoning_bundle.v1 Specimen

```text
schema_version: reasoning_bundle.v1
bundle_id: consultant_report_bundle_v0
source_artifact_ids:
  - consultant_counsel_incentive_gate
  - consultant_wednesday_protocol_boundary
  - consultant_internal_channel_distinction
  - consultant_reversibility_tripwire_plan
  - consultant_power_dynamics_misfit_discard

primary_pressure:
  - consultant_counsel_incentive_gate
  - consultant_wednesday_protocol_boundary

supporting_pressures:
  - consultant_internal_channel_distinction
  - consultant_reversibility_tripwire_plan

duplicate_or_lower_priority:
  - consultant_power_dynamics_misfit_discard

conflicts_or_tensions:
  - Counsel should guide the reporting decision, but counsel's incentives still need to be tested.
  - Internal reporting may alert the partner, but audit committee oversight may be structurally different from GC escalation.
  - Tripwires help the user function, but planning must not delay tonight's documentation and attorney calls.

hard_boundaries:
  - Do not advise the user to confront the partner.
  - Do not advise private investigation or unusual system access.
  - Do not tell the user to choose internal/external channel without counsel.
  - Do not turn the case into a negotiation or leverage exercise.

relaxation_conditions:
  - Counsel provides a specific script or superseding protocol.
  - Counsel identifies audit committee reporting as unsafe, unavailable, or legally inappropriate.
  - Counsel's timeline gives concrete filing and employer-response gates.

quiet_or_discard_candidates:
  - consultant_power_dynamics_misfit_discard should stay private unless leverage framing appears.
  - consultant_reversibility_tripwire_plan should stay compact if the answer is getting too long.

rethinking_questions:
  - What should the user ask counsel to test counsel's own channel bias?
  - What is the exact Wednesday response if the partner raises the encounter?
  - Which internal channels are materially different, and who should evaluate them?
  - Which tripwires help the user act, and which merely add anxiety?

final_reasoner_instruction:
  Preserve the safety sequence. Add channel nuance and counsel-incentive testing only inside that sequence. Do not let option expansion soften the boundaries against confrontation, private investigation, unusual access, or self-directed filing.

rendering_limits:
  max_public_machinery_terms: 0
  max_visible_options: 3
```

## Comparison Arms

Use this fixture to compare:

```text
Arm A: current-control summary only
Arm B: raw artifacts A-E without bundle index
Arm C: bundle specimen plus artifact details available if needed
```

Do not treat Arm C as better unless the final answer improves.

## Win Condition

The bundle wins this case only if the final answer:

- keeps the immediate safety sequence intact;
- adds counsel-incentive testing without undermining counsel-first advice;
- gives a concise Wednesday protocol;
- distinguishes GC, audit committee, and external regulator as counsel-evaluated
  channels;
- uses tripwires to reduce anxiety rather than add planning load;
- keeps power-dynamics/leverage framing discarded;
- is not longer or less direct than the raw-artifact answer without a clear
  safety gain.

## Kill Condition

The bundle loses or ties if:

- raw artifacts produce the same final answer;
- option expansion weakens the hard safety boundaries;
- the answer implies legal-channel selection without counsel;
- the Wednesday protocol becomes theatrical or unnatural;
- power-dynamics language reappears as public advice;
- the answer becomes so caveated that the user loses the first three concrete
  actions.

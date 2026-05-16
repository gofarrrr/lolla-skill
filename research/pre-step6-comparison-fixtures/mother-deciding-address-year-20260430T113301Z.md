# Pre-Step-6 Comparison Fixture: Mother Deciding Address Year

Date: 2026-05-16

Status: manual research fixture v0. This is not runtime code, not a prompt
contract, not legal advice, not clinical advice, and not product behavior.

Related docs:

```text
research/pre-step6-raw-artifact-consumption-discipline-2026-05-16.md
research/pre-step6-comparison-case-inventory-2026-05-16.md
research/pre-step6-raw-artifact-consumption-readout-2026-05-16.md
```

Primary sources:

```text
data/treatment_audits/mother-deciding-address-year__20260430T113301Z.v1.json
data/treatment_audits/calibration_report_pr6.md
data/treatment_audits/summary.v1.json
```

## Case Brief

```text
case_id: mother-deciding-address-year
source_run_id: mother-deciding-address-year__20260430T113301Z
reasoning_shape: overclaim / calibration / no-worker sentinel
```

The user is a mother deciding how to protect her 14-year-old daughter after
discovering secret online contact with a 19-year-old. The situation includes
shame, trust repair, divorced co-parenting, a minimizing ex, secret phone
surveillance, and RAINN guidance that a police report is possible but complex.

The current Step-6-style answer already split the problem into separate
decisions: police, phone/blocking, co-parent communication, therapy, and trust
repair. It also added tripwires and warned against forwarding screenshots or
verbatim message content to the ex because the material could be weaponized
during custody time.

This fixture is a no-worker sentinel. The remaining useful pressure is mostly
raw artifact discipline:

```text
use the surveillance data carefully
size commitments to uncertainty and tripwires
do not force a power-dynamics/leverage lens
do not expand into legal or clinical certainty
```

## Source Excerpts

Keep excerpts compact. These are compressed from the local treatment-audit
artifacts.

1. Case context: daughter is 14, online contact is with a 19-year-old, RAINN
   said a police report is possible but interstate jurisdiction makes it
   complex.
2. Current answer: split police, phone/blocking, and trust-repair decisions;
   do not block immediately because visible contact may migrate underground.
3. Current answer: replace time-based triggers with behavioral triggers and add
   tripwires for escalating contact, requests to meet, images, or evidence of
   contact with other minors.
4. Pressure check: do not forward screenshots or verbatim message content to
   the ex; give enough pattern/legal context to move him, not a packet he can
   selectively reframe to the daughter.

## Current-Control Summary

The current control answer is already strong in several ways:

- decomposes police, phone, blocking, co-parenting, therapy, and trust repair;
- keeps relationship repair central;
- warns that blocking can drive contact underground;
- changes vague time triggers into behavioral triggers;
- adds tripwires that override the slow-repair plan;
- adds a specific information-weaponization guard for the ex conversation.

Known weaknesses from the treatment audit:

- commitment-sizing is not calibrated to earned confidence ranges;
- surveillance is treated as useful but not fully audited as an instrument the
  daughter may evade;
- base-rate language is duplicate pressure and should not become a new public
  claim;
- power-dynamics commitment-gradient pressure is not activated or is duplicate
  of the ex weaponization concern.

## Raw reasoning_artifact.v1 Specimens

These are hand-authored specimens. They test handoff value, not producer
quality.

### Artifact A: Surveillance Instrument-Trust Gate

```text
schema_version: reasoning_artifact.v1
artifact_id: mother_surveillance_instrument_trust_gate
worker_type: boundary/evidence-gate
why_provided: The answer uses surveillance and behavior triggers, but the treatment audit flags incomplete trust-in-the-instrument analysis.
source_grounding: The mother has been secretly monitoring phone activity for months; the answer says blocking may drive communication underground; the audit flags instrument-trust-before-precision as only partially treated.
contribution: Treat "nothing visible happened" as weak evidence, not reassurance.
hard_boundary: Do not let absence of visible phone evidence become proof that contact stopped or risk is lower.
relaxation_condition: A therapist, RAINN, counsel, or a jointly agreed safety plan creates a better signal than secret monitoring alone.
discard_condition: Discard only if the final answer does not rely on surveillance, visible contact, or behavior triggers as safety signals.
priority_hint: high
risk_if_forced: The answer may become too suspicious and undermine trust repair.
risk_if_ignored: The mother may wait because the instrument is quiet while the daughter has simply moved contact elsewhere.
```

### Artifact B: Commitment-Sizing To Tripwires

```text
schema_version: reasoning_artifact.v1
artifact_id: mother_commitment_sizing_tripwires
worker_type: boundary/evidence-gate
why_provided: The treatment audit says commitments are not sized to earned confidence ranges.
source_grounding: Current answer already distinguishes slow repair from emergency override; tripwires include escalating contact, requests to meet, images, threats, or evidence of other minors.
contribution: Keep actions reversible while uncertainty is high, but make override triggers explicit.
hard_boundary: Do not recommend irreversible escalation or continued delay without naming the facts that would change the plan.
relaxation_condition: New evidence satisfies a tripwire, or professional/legal guidance says a specific action is required.
discard_condition: Discard if the final answer already ties every major commitment to concrete safety triggers and professional guidance.
priority_hint: high
risk_if_forced: The answer may over-proceduralize a parenting crisis and sound cold.
risk_if_ignored: The slow-repair strategy may become avoidance without a floor.
```

### Artifact C: Duplicate Base-Rate Caution

```text
schema_version: reasoning_artifact.v1
artifact_id: mother_duplicate_base_rate_caution
worker_type: duplicate/priority
why_provided: The treatment audit marks base-rate material as duplicate existing pressure, not a new finding.
source_grounding: Pressure check already mentions using general grooming-pattern/base-rate language to persuade the ex while withholding screenshots and verbatim messages.
contribution: Keep general risk facts as persuasion context, not calibrated claims.
hard_boundary: Do not invent or imply a quantitative grooming probability from this fixture.
relaxation_condition: A cited source such as RAINN provides specific language appropriate for the parent to share.
discard_condition: Discard if the final answer simply says to use RAINN/professional language without numeric claims.
priority_hint: quiet
risk_if_forced: The answer may overclaim or distract from the immediate safety and trust sequence.
risk_if_ignored: The ex conversation may lack enough outside grounding to counter minimization.
```

### Artifact D: Power-Dynamics Worker Decline

```text
schema_version: reasoning_artifact.v1
artifact_id: mother_power_dynamics_worker_decline
worker_type: worker-admission/decline
why_provided: The case inventory marks this as a worker-should-not-run sentinel; calibration report excludes commitment-gradient inversion as not activated and treats outside-option credibility as duplicate/quality pressure.
source_grounding: The active risk is daughter's safety, shame, instrument reliability, and ex information weaponization; calibration report says commitment-gradient leverage inversion is not activated in this family context.
contribution: Decline a power-dynamics worker or leverage framing unless new facts create a real negotiation/lock-in problem.
hard_boundary: Do not turn the advice into a leverage map or bargaining strategy with the ex or daughter.
relaxation_condition: New facts show a concrete custody/legal negotiation where walk-away options, enforcement costs, or lock-in milestones determine the safe action.
discard_condition: Discard now; current answer already handles the useful ex-risk through information-weaponization and co-parent alignment.
priority_hint: discard
risk_if_forced: The answer may become strategic in a way that undermines safety, trust repair, and professional guidance.
risk_if_ignored: Low; the useful part is already covered by the ex information-weaponization guard.
```

## Optional reasoning_bundle.v1 Specimen

This fixture intentionally does not require a bundle.

If a bundle is created anyway, it should be minimal:

```text
primary_pressure:
  - mother_surveillance_instrument_trust_gate
  - mother_commitment_sizing_tripwires

quiet_or_discard_candidates:
  - mother_duplicate_base_rate_caution
  - mother_power_dynamics_worker_decline

hard_boundaries:
  - Do not treat silence in surveillance as proof of safety.
  - Do not continue delay or escalate irreversibly without named triggers or professional guidance.
  - Do not force leverage framing into this case.
```

The expected better result is not a bundle. It is raw artifact discipline plus a
no-worker decision.

## Comparison Arms

Use this fixture to compare:

```text
Arm A: current-control summary only
Arm B: raw artifacts A-D with raw-artifact consumption discipline
Arm C: optional bundle, expected not needed
```

Do not treat Arm C as better unless it improves final public advice. If it only
makes the private roles clearer, raw artifacts win.

## Win Condition

Raw artifact discipline wins this case if the final answer:

- keeps the current safety/trust sequence;
- adds only the missing instrument-trust warning;
- keeps commitment triggers explicit;
- avoids numeric grooming/base-rate overclaim;
- declines power-dynamics/leverage worker framing;
- is not longer or more alarming than the control without a clear gain.

## Kill Condition

The bundle or worker path loses if:

- it forces power dynamics into the case;
- it turns general grooming risk into a calibrated claim;
- it weakens the counsel/RAINN/therapy/professional-guidance boundary;
- it makes the answer sound like legal or clinical certainty;
- it lengthens the answer mostly to describe private structure.

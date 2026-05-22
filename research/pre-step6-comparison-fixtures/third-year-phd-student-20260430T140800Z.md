# Pre-Step-6 Comparison Fixture: Third-Year PhD Student

Date: 2026-05-16

Status: manual research fixture v0. This is not runtime code, not a prompt
contract, and not product behavior.

Related docs:

```text
research/pre-step6-cognitive-worker-system-plan-2026-05-16.md
research/pre-step6-next-slice-decision-note-2026-05-16.md
research/pre-step6-comparison-case-inventory-2026-05-16.md
```

Primary sources:

```text
data/treatment_audits/third-year-phd-student__20260430T140800Z.v1.json
data/treatment_audits/calibration_report_pr6.md
data/treatment_audits/summary.v1.json
```

## Case Brief

```text
case_id: third-year-phd-student
source_run_id: third-year-phd-student__20260430T140800Z
reasoning_shape: conflict / constraint / fallback viability
```

The user is a third-year PhD student choosing among dissertation directions
under a 3-month deadline. Their advisor retires in 2-3 years. The lab has no
single-cell experience or collaborators. The user frames three options:

```text
1. continue the lab's tumor-modeling path
2. shift toward single-cell plus foundation models
3. pursue the advisor's novel combination of both
```

The current Step 6-style answer preserved advisor-first sequencing, treated Dr.
Silva/data access as the binding constraint, recommended low-cost probing, and
converted the old single 18-month checkpoint into evidence-specific triggers.

The pressure check added important tension: the advisor is not a neutral sponsor
and option 1 may stop being a real fallback after enough option-3 work.

## Source Excerpts

Keep excerpts compact. These are paraphrased or lightly compressed from the
local treatment-audit artifacts.

1. Case context: advisor retires in 2-3 years, deadline is 3 months, lab has no
   single-cell experience or collaborators, and the student says this is their
   only shot at a PhD.
2. Current answer: advisor first, Silva second, committee third remains the
   political sequence.
3. Current answer: data access / Dr. Silva is the binding constraint, and a
   low-cost informal probe should happen before spending political capital.
4. Pressure check: a retiring advisor's incentives may favor low-risk completion
   and option 1 may no longer be executable at an 18-month pivot point.

## Current-Control Summary

The current control answer is already strong in several ways:

- it keeps the user from going around the advisor with a specific proposal;
- it distinguishes probing Silva from pitching Silva;
- it challenges the "hot field" consensus signal;
- it names data access as the bottleneck;
- it turns a vague 18-month premortem into evidence-specific triggers.

Known weaknesses from the treatment audit:

- base-rate pressure is named but not tied to a defined reference class;
- confidence is not sized to earned evidence ranges;
- option expansion is incomplete;
- constraint retesting after Silva/literature probes is under-specified;
- fallback viability is named in pressure check but not yet integrated as a hard
  boundary on the trigger design.

## Raw reasoning_artifact.v1 Specimens

These are hand-authored specimens. They test handoff value, not producer quality.

### Artifact A: Fallback Viability Boundary

```text
schema_version: reasoning_artifact.v1
artifact_id: phd_fallback_viability_boundary
worker_type: boundary/evidence-gate
why_provided: The pressure check says the 18-month pivot may be fake if option 1 is no longer executable by then.
source_grounding: Advisor retires in 2-3 years; option 1 depends on advisor support and lab continuity; pressure check says option 1 may close after enough option-3 work.
contribution: Treat fallback viability as a hard boundary on any reversal-trigger plan.
hard_boundary: Do not recommend an 18-month pivot unless the fallback target is still executable when the trigger fires.
relaxation_condition: Advisor explicitly agrees to preserve an option-1 or modified-option-1 path, funding, and supervision capacity through the trigger date.
discard_condition: Discard only if the final answer no longer uses option 1 as a fallback or reversal target.
relation_to_bundle: primary / boundary / conflict
priority_hint: high
risk_if_forced: The answer may become too conservative and kill a valuable option-3 path prematurely.
risk_if_ignored: The user may rely on a fallback that has quietly disappeared.
```

### Artifact B: Silva Constraint Retest

```text
schema_version: reasoning_artifact.v1
artifact_id: phd_silva_constraint_retest
worker_type: boundary/evidence-gate
why_provided: The answer names Dr. Silva/data access as the bottleneck but does not fully retest constraint movement after probes.
source_grounding: Lab has zero single-cell experience or collaborators; option 3 relies on external data/collaboration; treatment audit flags missing constraint-shift cadence.
contribution: Make the Silva probe a constraint test with follow-up measurements, not a one-off availability question.
hard_boundary: Do not treat option 3 as viable until data access, collaboration depth, and committee/advisor role are concrete enough to carry a dissertation.
relaxation_condition: Silva or another collaborator offers usable data access, clear sharing terms, and a role strong enough to reduce dissertation risk.
discard_condition: Discard if the final answer recommends an option that does not depend on external single-cell data access.
relation_to_bundle: primary / boundary
priority_hint: high
risk_if_forced: The answer may over-process the collaboration before the user has permission from the advisor.
risk_if_ignored: The user may commit politically before the binding constraint is tractable.
```

### Artifact C: Base-Rate Fit Gate

```text
schema_version: reasoning_artifact.v1
artifact_id: phd_base_rate_fit_gate
worker_type: boundary/evidence-gate
why_provided: The current answer names a 20-30% success rate for novel combinations but does not define or test the reference class.
source_grounding: Treatment audit flags base-rates as partially treated: the prior is named but not tied to aggregate data, fit criteria, or case-specific updating.
contribution: Keep base rates as a humility check, not a calibrated probability claim.
hard_boundary: Do not let a broad success-rate number size commitment unless the reference class is defined and matched to this dissertation situation.
relaxation_condition: The user finds relevant cohort evidence for similar computational biology dissertations under comparable advisor/lab/collaboration constraints.
discard_condition: Discard if the final answer avoids numeric success priors and uses only qualitative uncertainty.
relation_to_bundle: supporting / boundary
priority_hint: medium
risk_if_forced: The answer may become pseudo-quantitative and distract from tractable next actions.
risk_if_ignored: The answer may overstate confidence in option 3 or option 1 without an outside-view check.
```

### Artifact D: Quiet Option-Expansion Caution

```text
schema_version: reasoning_artifact.v1
artifact_id: phd_quiet_option_expansion_caution
worker_type: duplicate/priority
why_provided: The audit flags incomplete option expansion, but the current answer already warns against parallel prototyping under a 3-month deadline.
source_grounding: Treatment audit says option expansion is incomplete; current answer says parallel prototyping all options is the failure-mode version of optionality at this stage.
contribution: Use option expansion only to improve the literature/search frame, not to add new active dissertation tracks.
hard_boundary: Do not turn option expansion into "try everything" or a new delay tactic.
relaxation_condition: A fourth option appears that uses existing lab infrastructure and materially reduces external dependency without losing career upside.
discard_condition: Discard if the final answer already widens the evidence search without adding a new commitment path.
relation_to_bundle: quiet / support / possible duplicate
priority_hint: quiet
risk_if_forced: The answer may become sprawling and weaken the needed commitment cadence.
risk_if_ignored: The answer may inherit the user's original three-option frame too passively.
```

## reasoning_bundle.v1 Specimen

```text
schema_version: reasoning_bundle.v1
bundle_id: phd_direction_choice_bundle_v0
source_artifact_ids:
  - phd_fallback_viability_boundary
  - phd_silva_constraint_retest
  - phd_base_rate_fit_gate
  - phd_quiet_option_expansion_caution

primary_pressure:
  - phd_fallback_viability_boundary
  - phd_silva_constraint_retest

supporting_pressures:
  - phd_base_rate_fit_gate

duplicate_or_lower_priority:
  - phd_quiet_option_expansion_caution

conflicts_or_tensions:
  - Option 3 may be the ambitious/high-upside path, but only if the Silva/data constraint becomes real.
  - Option 1 is the fallback, but fallback value decays if advisor runway, funding, or lab continuity disappears.
  - Option expansion is useful for evidence search, but dangerous if it becomes parallel-prototyping drift.

hard_boundaries:
  - Do not recommend an 18-month pivot unless the pivot target remains executable.
  - Do not treat Dr. Silva as solved infrastructure until access and role are concrete.
  - Do not present broad base-rate numbers as calibrated estimates.

relaxation_conditions:
  - Advisor preserves option-1 fallback runway explicitly.
  - Silva or another collaborator provides concrete data access and role clarity.
  - Relevant dissertation/reference-class evidence supports a stronger outside-view prior.

quiet_or_discard_candidates:
  - phd_quiet_option_expansion_caution is useful only if the answer would otherwise inherit the user's three-option frame too passively.
  - phd_base_rate_fit_gate can stay private if the public answer avoids numeric priors.

rethinking_questions:
  - What exact trigger would prove option 1 is still executable when the user might need it?
  - What would the advisor get from sponsoring option 3 rather than defaulting to legacy continuity?
  - What measurement after the Silva probe tells us the bottleneck moved?
  - Is the answer using a success-rate number as evidence, or only as humility?

final_reasoner_instruction:
  Preserve the tension. Do not collapse the answer into "choose option 3 with safeguards" or "avoid option 3 because it is risky." The better answer should sequence low-cost constraint tests, protect fallback executability, and avoid pseudo-quantitative confidence.

rendering_limits:
  max_public_machinery_terms: 0
  max_visible_caveats: 3
```

## Comparison Arms

Use this fixture to compare:

```text
Arm A: current-control summary only
Arm B: raw artifacts A-D without bundle index
Arm C: bundle specimen plus artifact details available if needed
```

Do not treat Arm C as better unless the final answer improves.

## Win Condition

The bundle wins this case only if the final answer:

- preserves advisor-first sequencing;
- turns the 18-month fallback into an executable-fallback test;
- makes Silva/data access a measured constraint test;
- avoids treating 20-30% as a calibrated estimate;
- keeps option expansion as evidence search, not parallel-prototyping drift;
- is not longer or more caveated than the raw-artifact answer without a clear
  gain.

## Kill Condition

The bundle loses or ties if:

- raw artifacts produce the same final answer;
- the bundle makes Step 6 obey "primary" instead of reasoning through tension;
- the final answer becomes a list of caveats;
- the base-rate artifact creates pseudo-precision;
- the option-expansion artifact bloats the answer.

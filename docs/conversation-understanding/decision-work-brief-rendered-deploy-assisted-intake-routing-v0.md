# Decision Work Brief

This is a provisional, non-human-validated Decision Work Brief. It explains what the audit artifacts suggest changed for the decision. It is not proof that the final answer is correct.

Case: `deploy-assisted-intake-routing`
Run: `20260627T130339Z_4cd3cb`

## The decision

The decision appears to be whether to deploy an AI-assisted intake routing feature in outpatient clinics next month despite operational, compliance, sales, and staff-capacity constraints.
Uncertainty: medium.

## What changed

**Starting point:**
Likely starting point: The likely starting direction was already a narrow single-clinic pilot rather than a broad launch, but it relied on a large nine-gate control structure.
Uncertainty: high.

**What Lolla pressed on:**
Pressure point: Lolla appears to have pressed on whether an exhaustive gate list was becoming a control burden too heavy for exhausted admin staff to operate.
What was pressed:
- whether routing uncertainty was actually causing the backlog
- whether nine gates should be compressed into fewer must-pass operating controls
- whether pause and rollback triggers were active controls rather than passive monitoring
- whether sales language should be narrowed away from full intake automation
Uncertainty: medium.

**Change in direction:**
What changed: The plan changed from a narrow pilot wrapped in nine gates toward a smaller operating test with four must-pass gates, a 48-hour backlog diagnostic, hard pause triggers, and narrower sales meaning.
Specific changes:
- Nine gates compress into scope enforcement, admin usability, compliance readiness, and live-operating control.
- Before go-live, the team checks whether routing uncertainty is actually driving the backlog.
- One credible clinician-attention misroute pauses auto-routing until the cause is understood.
- The pilot validates scheduling and billing routing only, not broad intake automation.
Uncertainty: medium.

## What this means for action

Before go-live, the team would run a 48-hour bottleneck check, keep the pilot to one clinic and scheduling/billing routing, require four operating gates, and predefine pause triggers instead of treating the AI pilot as the backlog solution.
Possible next actions:
- Do not ask exhausted admins to operate a nine-gate control system.
- Diagnose whether staffing, forms, queue ownership, payer friction, handoffs, or downstream capacity are the real backlog causes.
- Pause auto-routing after one credible clinician-attention misroute.
- Keep sales language to staff-controlled intake organization, not autonomous intake automation.
Uncertainty: medium.

## What still might be wrong

Missing or uncertain:
- The raw conversation, revised answer, memo, live transcript, provider text, and private ledgers are absent from the checked-in artifact.
- The safe report marks useful versus noisy friction, lost value, stakeholders, values, and assistant influence as requiring interpretation or not supplied.
- The real backlog cause, admin ability to operate controls, compliance tolerance, and patient-risk boundary are not verified here.
- The nine-gate format may have contained useful patient-trust, support, or measurement controls that should not be lost.
Possible overcorrection or noise: The brief may overcorrect against thoroughness if compressing nine gates into four loses controls that matter for patient trust, support readiness, or measurement. It may also underweight compliance's two-month auditability and consent concern.
Uncertainty: high.

## What this does not prove

Not proven:
- The draft does not prove the AI routing feature should deploy.
- The draft does not prove the constrained pilot is better advice.
- The draft does not measure answer quality.
- The draft does not authorize agent action.
- The draft is not human validated.
- Three clean cases do not create product readiness.

## Evidence and limits

This section preserves source and custody details without putting them in the main decision story.

### Verification state

- Human validation: no
- Product proof: no
- Answer-quality scoring: no
- Agent action authorization: no
- Runtime invoked: no
- Skill invoked: no
- Archive mutated: no
- Model calls: 0
- Source mode: checked-in-safe
- Private/raw content included: no
- Provider text included: no

### Source limits

Backing receipt: The backing layer is the locally generated PR115 metadata-only packet plus local metadata-only Decision Work Receipt and Decision Trail reports. These were used as source/custody context and were not checked in.
Available evidence:
- structured run metadata
- Decision Trail decision question, constraints, audit pressure, and structural delta fields
- Decision Work Receipt missingness and custody metadata
- PR115 metadata-only source availability packet
Unavailable or redacted:
- raw conversation
- raw revised answer
- raw memo
- live transcript
- provider text
- private ledgers

### Section uncertainty

- The decision: medium
- The likely starting point: high
- What Lolla pressed on: medium
- What changed: medium
- What this means for action: medium
- What still might be wrong: high
- What this does not prove: not_applicable
- The backing evidence: not_applicable

### Source references

- `decision_work_brief_packets:metadata_only:not_checked_in` / `packet_sections` (source status: `checked_in_safe_structured_artifact`)
- `decision_trail_report:local_temporary_metadata_only` / `decision_question|structural_delta|constraints` (source status: `external_report_reference`)
- `decision_work_receipt:local_temporary_metadata_only` / `decision_trail_summary|missingness_and_redaction` (source status: `external_report_reference`)
- `decision_work_brief_packets:metadata_only:not_checked_in` / `source_packets/0` (source status: `checked_in_safe_structured_artifact`)
- `decision_work_receipt:local_temporary_metadata_only` / `summary` (source status: `external_report_reference`)
- `decision_trail_report:local_temporary_metadata_only` / `summary` (source status: `external_report_reference`)

### Non-claims

- `not_correctness_proof`
- `not_answer_quality_score`
- `not_agent_action_authorization`
- `not_human_validated_unless_marked`
- `clean_artifacts_do_not_imply_good_advice`
- `process_evidence_is_not_decision_certification`
- `llm_interpretation_is_provisional_unless_human_reviewed`

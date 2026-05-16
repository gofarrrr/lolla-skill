# Pre-Step-6 Comparison Fixture: Founder Grant Marcus Equity

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
data/treatment_audits/founder-grant-marcus-equity__20260428T064421Z.v1.json
data/treatment_audits/calibration_report_pr6.md
data/treatment_audits/summary.v1.json
```

## Case Brief

```text
case_id: founder-grant-marcus-equity
source_run_id: founder-grant-marcus-equity__20260428T064421Z
reasoning_shape: duplicate / low marginal value / systems pressure
```

The founder is deciding whether to grant Marcus 15% equity, CTO title, and a
board seat. Marcus is critical to current technical capability, may pull Jake
and Lina if he leaves, and has built an impressive platform prototype. The
company is a profitable 90-person agency with about $14M revenue and $2.2M
EBITDA. The founder's baseline exit math depends on a $9-13M valuation.

The current Step 6-style answer already corrected several overconfident claims:
invented catastrophic-departure math, invented platform budget, unsupported
psychology predictions about Marcus, and overconfident contractual protection.

The pressure check already covered several useful pressures:

- contractual protection is not practical protection against spinout leverage;
- dilution should be compared against alternative retention uses for Jake/Lina;
- the exit valuation is unaudited;
- intermediate instruments exist between bonus and 15% plus board seat;
- the "I built this" frame needs psychological resolution.

## Source Excerpts

Keep excerpts compact. These are paraphrased or lightly compressed from the
local treatment-audit artifacts.

1. Case context: Marcus asks for 15% equity, board seat, and CTO title; he
   drives about 40% of technical capability and may pull Jake and Lina.
2. Case context: the exit valuation assumes 4-6x $2.2M EBITDA, giving a $9-13M
   range, while the platform prototype may become meaningful ARR.
3. Pressure check: the standard legal clauses reduce clean-departure ambiguity
   but do not remove the practical leverage of a CTO/shareholder with deep code
   knowledge.
4. Treatment audit: base-rate valuation, option expansion, and "I built this"
   frame falsification are duplicates of existing pressure; systems feedback
   loops and measurable leverage design remain net-new gaps.

## Current-Control Summary

The current control answer is already strong in several ways:

- it withdraws fabricated catastrophic-departure math;
- it treats the 90-day platform validation sprint as the right shape but rejects
  invented budget precision;
- it keeps intermediate instruments live;
- it recognizes that legal protections do not fully solve practical leverage;
- it makes Friday's conversation about the kind of company the founder wants to
  run, not just equity terms.

Known weaknesses from the treatment audit:

- several candidate pressures are duplicates of pressure-check material;
- the answer critiques numbers and terms but does not map feedback loops among
  Marcus, Jake, Lina, the founder, clients, platform progress, and exit value;
- it does not convert risk structure into goal-process-lever-metric chains;
- it does not clearly distinguish an immediate equity event from the underlying
  dependency system that produced the request.

## Raw reasoning_artifact.v1 Specimens

These are hand-authored specimens. They test handoff value, not producer quality.

### Artifact A: Duplicate Valuation Base-Rate Gate

```text
schema_version: reasoning_artifact.v1
artifact_id: founder_duplicate_valuation_base_rate_gate
worker_type: duplicate/priority
why_provided: The audit flags unaudited exit valuation, but the pressure check already covers this point.
source_grounding: Pressure check says the 4-6x EBITDA multiple is industry-conventional and not specific to the agency; treatment audit marks base-rate testing duplicate of existing pressure.
contribution: Keep valuation uncertainty as a support point, not a second primary pressure.
hard_boundary: Do not let $9-13M exit math carry the equity recommendation until the multiple and buyer assumptions are tested.
relaxation_condition: A credible buyer/reference-class analysis supports the EBITDA multiple after customer concentration, founder dependency, and AI-margin-compression risks are considered.
discard_condition: Discard as visible pressure if the final answer already says both upside and downside math are unaudited.
relation_to_bundle: duplicate / lower-priority / boundary
priority_hint: quiet
risk_if_forced: The final answer repeats already-covered valuation caveats and becomes slower without changing the action.
risk_if_ignored: The answer may let untested exit math quietly steer the equity comparison.
```

### Artifact B: Duplicate Middle-Instrument Expansion

```text
schema_version: reasoning_artifact.v1
artifact_id: founder_duplicate_middle_instruments
worker_type: duplicate/priority
why_provided: The audit flags option expansion, but the pressure check already names intermediate equity and incentive instruments.
source_grounding: Pressure check lists phantom equity, platform revenue share, smaller grant without board seat, milestone grants, and platform-sub equity.
contribution: Demote option-expansion pressure unless the answer lacks concrete middle instruments.
hard_boundary: Do not collapse the choice to retention bonus vs 15% equity plus board seat.
relaxation_condition: Marcus refuses all intermediate instruments after a real negotiation, making the binary more factual.
discard_condition: Discard if the final answer already keeps multiple intermediate instruments live for Friday's conversation.
relation_to_bundle: duplicate / quiet
priority_hint: quiet
risk_if_forced: The final answer becomes an instrument catalog rather than a decision frame.
risk_if_ignored: The answer may overcommit to the requested package before testing cheaper partnership signals.
```

### Artifact C: Systems Feedback Loop Map

```text
schema_version: reasoning_artifact.v1
artifact_id: founder_systems_feedback_loop_map
worker_type: boundary/evidence-gate
why_provided: The treatment audit finds a net-new gap: the answer lacks a dynamic map of actors and feedback loops behind the equity request.
source_grounding: Marcus controls important technical capability; Jake and Lina may follow him; platform progress, retention signals, governance terms, and client confidence can reinforce or weaken each other.
contribution: Treat the equity request as a dependency-system problem, not only a terms negotiation.
hard_boundary: Do not recommend terms without mapping how they affect Marcus retention, Jake/Lina retention, platform delivery, founder control, and client/platform value over time.
relaxation_condition: The founder already has reliable retention data for Jake/Lina, platform milestone data, and a governance design that separates agency risk from platform upside.
discard_condition: Discard only if the final answer is explicitly limited to the first conversation agenda and does not recommend concrete terms.
relation_to_bundle: primary / boundary
priority_hint: high
risk_if_forced: The answer may turn into abstract systems language instead of practical Friday prep.
risk_if_ignored: The founder may optimize one term while worsening the feedback loop that caused the leverage problem.
```

### Artifact D: Metric-Leverage Chain

```text
schema_version: reasoning_artifact.v1
artifact_id: founder_metric_leverage_chain
worker_type: boundary/evidence-gate
why_provided: The treatment audit finds no goal-process-measure-lever chain for the equity/platform decision.
source_grounding: Current answer recommends a 90-day validation sprint but does not define the specific learning expected, commitment boundary, or measurable levers tied to Marcus/Jake/Lina/platform risk.
contribution: Convert the 90-day sprint and retention plan into explicit measures before using them to size equity.
hard_boundary: Do not size permanent equity from vague platform promise or vague retention fear; define the measurements that change commitment size.
relaxation_condition: The founder can name sprint milestones, retention signals, knowledge-transfer milestones, and what equity/governance concession each milestone unlocks.
discard_condition: Discard if the final answer avoids sizing equity and only recommends a discovery conversation.
relation_to_bundle: primary / support
priority_hint: high
risk_if_forced: The answer may over-mechanize a relationship conversation and feel cold.
risk_if_ignored: The founder may use the 90-day sprint as theater while still committing on vibes.
```

### Artifact E: Misfit Architecture Note

```text
schema_version: reasoning_artifact.v1
artifact_id: founder_misfit_architecture_note
worker_type: duplicate/priority
why_provided: The treatment audit marks one systems-thinking affordance not applicable because this is not a software architecture rewrite case.
source_grounding: The audited output concerns equity governance and platform validation, not an architecture redesign or recurring technical failure pattern.
contribution: Prevent the systems artifact from overreaching into code architecture diagnosis.
hard_boundary: Keep systems pressure at the business-dependency level.
relaxation_condition: New facts show recurring platform failures caused by technical architecture rather than governance/retention structure.
discard_condition: Discard after confirming the final answer does not diagnose software architecture.
relation_to_bundle: discard candidate / boundary
priority_hint: quiet
risk_if_forced: The answer invents a technical architecture problem that is not in the case.
risk_if_ignored: The systems framing may leak into an unsupported technical diagnosis.
```

## reasoning_bundle.v1 Specimen

```text
schema_version: reasoning_bundle.v1
bundle_id: founder_grant_marcus_equity_bundle_v0
source_artifact_ids:
  - founder_duplicate_valuation_base_rate_gate
  - founder_duplicate_middle_instruments
  - founder_systems_feedback_loop_map
  - founder_metric_leverage_chain
  - founder_misfit_architecture_note

primary_pressure:
  - founder_systems_feedback_loop_map
  - founder_metric_leverage_chain

supporting_pressures:
  - founder_duplicate_valuation_base_rate_gate

duplicate_or_lower_priority:
  - founder_duplicate_valuation_base_rate_gate
  - founder_duplicate_middle_instruments

conflicts_or_tensions:
  - Partnership signal may reduce Marcus flight risk, but too much governance/equity may increase founder lock-in and precedent risk.
  - Platform validation needs Marcus commitment, but Marcus commitment may depend on seeing real partnership before validation finishes.
  - Jake/Lina retention can reduce Marcus leverage, but over-indexing on that may create a divide-and-conquer feeling.

hard_boundaries:
  - Do not repeat valuation caveats as if they are new pressure when already covered.
  - Do not collapse the choice to bonus vs 15% equity plus board seat.
  - Do not recommend permanent equity sizing without measures for platform progress, retention risk, and knowledge-transfer/operational resilience.
  - Do not turn business dependency mapping into unsupported software architecture diagnosis.

relaxation_conditions:
  - Buyer/reference-class analysis supports the valuation range.
  - Marcus rejects intermediate instruments after a real negotiation.
  - Sprint milestones, retention signals, and knowledge-transfer gates are clear enough to size staged equity.

quiet_or_discard_candidates:
  - founder_duplicate_valuation_base_rate_gate should stay quiet if the answer already says the exit math is unaudited.
  - founder_duplicate_middle_instruments should stay quiet if the answer already names middle instruments.
  - founder_misfit_architecture_note should be discarded after it prevents unsupported architecture diagnosis.

rethinking_questions:
  - What feedback loop is the proposed equity package meant to change?
  - Which measure would justify moving from conversation to staged grant?
  - Which retention lever reduces Marcus's practical leverage without poisoning trust?
  - Which already-covered caveat should stay private to avoid repetition?

final_reasoner_instruction:
  Do not make the answer louder by repeating every valid caution. Preserve one primary systems pressure: convert the equity request into a dependency map and measurement plan. Demote valuation and middle-instrument points if they are already present in the control answer.

rendering_limits:
  max_public_machinery_terms: 0
  max_visible_duplicate_points: 1
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

- avoids re-litigating valuation and intermediate-instrument points already
  covered by the pressure check;
- makes the new systems pressure practical, not abstract;
- defines what the 90-day sprint or staged-equity structure should measure;
- keeps legal/practical protection distinctions intact;
- avoids inventing software architecture problems;
- is tighter than the raw-artifact answer or clearly better at prioritization.

## Kill Condition

The bundle loses or ties if:

- raw artifacts produce the same prioritization;
- the final answer repeats duplicate pressure as if it were new;
- systems language becomes generic;
- the answer becomes a long checklist of every possible instrument;
- the bundle suppresses the practical-protection warning because it marks other
  items as duplicate.

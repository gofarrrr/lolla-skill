# Skill Shadow Comparison Contract

Status: superseded by the Step-7-rest product decision. Historical research-only contract.

Code records; humans decide.

This contract is not the active gate for changing `SKILL.md`. The board decided the default live skill should rest post-Step-6 sub-agents now, because pre-Step-6 table cleaning and post-Step-6 pressure checks are different product designs rather than comparable arms.

## Hypothesis

A cleaner pre-Step-6 table may reduce the useful residual work that Step 7 pressure-check agents find.

## Product Intent

- Desired direction: Move more useful reasoning pressure before Step 6 so the default Step 7 post-Step-6 pressure-check agents can become optional or manual-triggered if evidence supports it.
- Non-claim: Step 7 is not obsolete by assertion.

## Comparison Arms

- `legacy_required_pressure_check`
  - Step 6 table: current Step 6 material: four lanes plus V60 private enrichment
  - Step 7: required_for_each_non_empty_lane_after_step6b
  - Visible behavior: current_skill_behavior
- `cleaner_table_shadow_required_pressure_check`
  - Step 6 table: cleaner private table from dormant pre-Step-6 foundation and case-appropriate pressure atoms
  - Step 7: still_required_for_each_non_empty_lane_after_step6b
  - Visible behavior: unchanged_shadow_only

## Measurement Protocol

- Record unit: `case_sample_pair`
- Sample count per case: `3`
- Target record count: `12`
- Cleaner-table operational definition:
  - Step 6 receives cleaner private table: `True`
  - Step 7 runs in both arms: `True`
  - Shadow portfolio role: May record cached-deck custody and evidence, but it is not the whole treatment. The treatment is the Step 6 private table composition.
- Operator labeling:
  - Primary label source: `human_operator_review`
  - LLM reviewers authoritative: `False`

## Case Set

- `mid-level-consultant-report-2` / `consultant_graduation_candidate`
  - Tests: whether upstream-carried counsel reversibility reduces Step 7 correction work
  - Failure read: Step 7 still finds the same counsel-boundary miss after cleaner table
- `third-year-phd-student.v2.v60-off` / `phd_distributed_atom`
  - Tests: whether distributed atomic cards reduce preventable Step 7 corrections
  - Failure read: Step 7 still finds avoidable omissions across the PhD pressure atoms
- `founder-grant-marcus-equity.high-clutter.v60-on` / `founder_v60_destabilization`
  - Tests: whether cleaner table avoids hiding V60 packet instability behind Step 7 removal
  - Failure read: cleaner table reduces visible pressure checks while V60 instability remains unexplained
- `mother-address-year` / `negative_control`
  - Tests: whether cleaner table preserves stand-down behavior on a sensitive case
  - Failure read: cleaner table creates performative extra pressure where anchor should remain sufficient

## Metrics

- `step7_meaningful_divergence_rate` - Primary signal: how often Step 7 still adds material after Step 6.
- `question_1_shift_missed_rate` - Tracks shifts Step 6 dismissed or minimized.
- `question_2_material_noise_rate` - Tracks findings Step 6 treated as noise but Step 7 treated as material.
- `question_3_named_mechanism_missed_rate` - Tracks named mechanisms Step 7 connected that Step 6 did not.
- `clean_table_atom_uptake_rate` - Checks whether Step 6 considers pressure atoms discriminately.
- `protected_payload_preservation` - Guards against cleaner-table narrowing that drops concrete payload.
- `memo_completeness` - Ensures Step 8c still has enough material if Step 7 work shrinks.
- `anthropic_subagent_cost_delta` - Measures cost upside without treating cost as correctness.
- `operator_review_label` - Captures human interpretation; code may nominate but humans decide.

## Outcomes

- `supports_optional_pressure_check_trial` - Cleaner-table arm preserves payload and materially reduces Step 7 correction work; proceed to a separate gated SKILL.md optional-pressure trial.
- `preserve_required_pressure_check` - Step 7 still adds meaningful independent or corrective work; keep current skill flow.
- `ambiguous_continue_research` - Results split by case role or reviewer interpretation; do not change SKILL.md.

## Decision Thresholds

- `supports_optional_pressure_check_trial`: 12 records, >= 9 support labels, <= 1 preserve label, 0 safety-blocked records.
- `preserve_required_pressure_check`: fires on any safety-blocked record, >= 4 preserve labels, or no aggregate divergence reduction.
- `ambiguous_continue_research`: default for everything between those thresholds.

## Boundary

- This contract does not edit `SKILL.md`.
- This contract does not make Step 7 optional.
- This contract does not add a model selector.
- This contract does not turn recurrence into automatic wisdom.

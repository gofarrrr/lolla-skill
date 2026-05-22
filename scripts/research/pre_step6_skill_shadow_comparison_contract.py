#!/usr/bin/env python3
"""Historical research-only contract for the cleaner-table skill shadow comparison.

The original contract defined what a skill-level comparison would have measured
before `SKILL.md` changed. It does not run the skill, call models, change
runtime, or decide whether Step 7 is obsolete.

As of the Step-7-rest decision, this contract is superseded. It remains in the
repo as evidence of the prior measurement plan, not as an active gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


SCHEMA_VERSION = "pre_step6_skill_shadow_comparison_contract.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "skill_shadow_comparison_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-skill-shadow-comparison-contract")

REQUIRED_CASE_ROLES = {
    "consultant_graduation_candidate",
    "phd_distributed_atom",
    "founder_v60_destabilization",
    "negative_control",
}
REQUIRED_METRICS = {
    "step7_meaningful_divergence_rate",
    "question_1_shift_missed_rate",
    "question_2_material_noise_rate",
    "question_3_named_mechanism_missed_rate",
    "clean_table_atom_uptake_rate",
    "protected_payload_preservation",
    "memo_completeness",
    "anthropic_subagent_cost_delta",
    "operator_review_label",
}
OUTCOME_LABELS = {
    "supports_optional_pressure_check_trial",
    "preserve_required_pressure_check",
    "ambiguous_continue_research",
}


class SkillShadowComparisonContractError(ValueError):
    pass


def build_skill_shadow_comparison_contract(*, root: Path) -> dict[str, object]:
    contract = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "skill_update_allowed": False,
        "runtime_visibility_change_allowed": False,
        "manual_interpretation_required": True,
        "contract_state": "superseded_by_step7_rest_decision",
        "superseded_reason": (
            "The board decided the pre-Step-6 cleaner-table approach and the "
            "old post-Step-6 pressure-check loop are different product designs, "
            "not arms of a fair comparison. Step 7 is rested by default now for "
            "simplicity and cost, while explicit deeper-review mode remains "
            "available."
        ),
        "product_intent": {
            "desired_direction": (
                "Move more useful reasoning pressure before Step 6 so the "
                "default Step 7 post-Step-6 pressure-check agents can become "
                "optional or manual-triggered if evidence supports it."
            ),
            "non_claim": "Step 7 is not obsolete by assertion.",
        },
        "principles": {
            "code_records": True,
            "humans_decide": True,
            "step6_is_cognitive_solver": True,
            "step7_not_obsolete_by_assertion": True,
            "automatic_graduation_allowed": False,
            "model_selector_allowed": False,
        },
        "comparison_arms": _comparison_arms(),
        "measurement_protocol": _measurement_protocol(),
        "case_set": _case_set(),
        "metrics": _metrics(),
        "outcomes": _outcomes(),
        "decision_thresholds": _decision_thresholds(),
        "stop_rules": {
            "historical_do_not_edit_skill_md_in_this_slice": True,
            "superseded_do_not_use_as_step7_default_off_gate": True,
            "do_not_treat_cost_savings_as_correctness": True,
            "do_not_treat_recurrence_as_automatic_wisdom": True,
        },
        "next_artifacts": {
            "expected_contract_runner": "pre_step6_skill_shadow_comparison_harness_v0",
            "expected_result_schema": "pre_step6_skill_shadow_comparison_result.v1",
            "expected_readout": "research/pre-step6-skill-shadow-comparison-readout-2026-05-22.md",
        },
    }
    validate_skill_shadow_comparison_contract(contract, root=root)
    return contract


def write_skill_shadow_comparison_contract(
    *, contract: dict[str, object], out_dir: Path, root: Path = Path(".")
) -> Path:
    validate_skill_shadow_comparison_contract(contract, root=root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "skill-shadow-comparison-contract.v1.json"
    path.write_text(json.dumps(contract, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def write_skill_shadow_comparison_contract_markdown(
    *, contract: dict[str, object], out_dir: Path, root: Path = Path(".")
) -> Path:
    validate_skill_shadow_comparison_contract(contract, root=root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "skill-shadow-comparison-contract.md"
    path.write_text(render_skill_shadow_comparison_contract_markdown(contract), encoding="utf-8")
    return path


def render_skill_shadow_comparison_contract_markdown(contract: Mapping[str, object]) -> str:
    validate_skill_shadow_comparison_contract(dict(contract), root=Path("."))
    lines = [
        "# Skill Shadow Comparison Contract",
        "",
        "Status: superseded by the Step-7-rest product decision. Historical research-only contract.",
        "",
        "Code records; humans decide.",
        "",
        "This contract is not the active gate for changing `SKILL.md`. The board decided the default live skill should rest post-Step-6 sub-agents now, because pre-Step-6 table cleaning and post-Step-6 pressure checks are different product designs rather than comparable arms.",
        "",
        "## Hypothesis",
        "",
        (
            "A cleaner pre-Step-6 table may reduce the useful residual work "
            "that Step 7 pressure-check agents find."
        ),
        "",
        "## Product Intent",
        "",
        f"- Desired direction: {contract['product_intent']['desired_direction']}",  # type: ignore[index]
        f"- Non-claim: {contract['product_intent']['non_claim']}",  # type: ignore[index]
        "",
        "## Comparison Arms",
        "",
    ]
    for arm in contract["comparison_arms"]:  # type: ignore[index]
        if not isinstance(arm, Mapping):
            continue
        lines.extend(
            [
                f"- `{arm.get('arm_id')}`",
                f"  - Step 6 table: {arm.get('step6_table')}",
                f"  - Step 7: {arm.get('step7_policy')}",
                f"  - Visible behavior: {arm.get('visible_behavior')}",
            ]
        )
    protocol = contract["measurement_protocol"]  # type: ignore[index]
    if isinstance(protocol, Mapping):
        cleaner = protocol.get("cleaner_table_operational_definition")
        labels = protocol.get("operator_labeling_protocol")
        lines.extend(
            [
                "",
                "## Measurement Protocol",
                "",
                f"- Record unit: `{protocol.get('record_unit')}`",
                f"- Sample count per case: `{protocol.get('sample_count_per_case')}`",
                f"- Target record count: `{protocol.get('target_record_count')}`",
            ]
        )
        if isinstance(cleaner, Mapping):
            lines.extend(
                [
                    "- Cleaner-table operational definition:",
                    f"  - Step 6 receives cleaner private table: `{cleaner.get('step6_receives_cleaner_private_table')}`",
                    f"  - Step 7 runs in both arms: `{cleaner.get('step7_runs_in_both_arms')}`",
                    f"  - Shadow portfolio role: {cleaner.get('shadow_portfolio_code_role')}",
                ]
            )
        if isinstance(labels, Mapping):
            lines.extend(
                [
                    "- Operator labeling:",
                    f"  - Primary label source: `{labels.get('primary_label_source')}`",
                    f"  - LLM reviewers authoritative: `{labels.get('llm_reviewers_authoritative')}`",
                ]
            )
    lines.extend(["", "## Case Set", ""])
    for case in contract["case_set"]:  # type: ignore[index]
        if not isinstance(case, Mapping):
            continue
        lines.extend(
            [
                f"- `{case.get('case_id')}` / `{case.get('case_role')}`",
                f"  - Tests: {case.get('tests')}",
                f"  - Failure read: {case.get('failure_read')}",
            ]
        )
    lines.extend(["", "## Metrics", ""])
    for metric in contract["metrics"]:  # type: ignore[index]
        if not isinstance(metric, Mapping):
            continue
        lines.append(f"- `{metric.get('metric_id')}` - {metric.get('why')}")
    lines.extend(["", "## Outcomes", ""])
    for outcome in contract["outcomes"]:  # type: ignore[index]
        if not isinstance(outcome, Mapping):
            continue
        lines.append(f"- `{outcome.get('label')}` - {outcome.get('meaning')}")
    thresholds = contract["decision_thresholds"]  # type: ignore[index]
    if isinstance(thresholds, Mapping):
        supports = thresholds.get("supports_optional_pressure_check_trial")
        preserve = thresholds.get("preserve_required_pressure_check")
        lines.extend(["", "## Decision Thresholds", ""])
        if isinstance(supports, Mapping):
            lines.append(
                "- `supports_optional_pressure_check_trial`: "
                f"{supports.get('minimum_records')} records, "
                f">= {supports.get('min_support_labels')} support labels, "
                f"<= {supports.get('max_preserve_labels')} preserve label, "
                f"{supports.get('max_safety_blocked_records')} safety-blocked records."
            )
        if isinstance(preserve, Mapping):
            lines.append(
                "- `preserve_required_pressure_check`: fires on any safety-blocked "
                f"record, >= {preserve.get('min_preserve_labels')} preserve labels, "
                "or no aggregate divergence reduction."
            )
        lines.append("- `ambiguous_continue_research`: default for everything between those thresholds.")
    lines.extend(["", "## Boundary", ""])
    lines.extend(
        [
            "- This contract does not edit `SKILL.md`.",
            "- This contract does not make Step 7 optional.",
            "- This contract does not add a model selector.",
            "- This contract does not turn recurrence into automatic wisdom.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_skill_shadow_comparison_contract(
    contract: dict[str, object], *, root: Path
) -> None:
    errors = list(iter_skill_shadow_comparison_contract_errors(contract, root=root))
    if errors:
        raise SkillShadowComparisonContractError("; ".join(errors))


def iter_skill_shadow_comparison_contract_errors(
    contract: dict[str, object], *, root: Path
) -> Iterable[str]:
    if not isinstance(contract, dict):
        yield "contract must be object"
        return
    required = {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "skill_update_allowed",
        "runtime_visibility_change_allowed",
        "manual_interpretation_required",
        "product_intent",
        "principles",
        "comparison_arms",
        "measurement_protocol",
        "case_set",
        "metrics",
        "outcomes",
        "decision_thresholds",
        "stop_rules",
        "next_artifacts",
    }
    missing = sorted(required - set(contract))
    if missing:
        yield f"missing fields: {missing}"
        return
    if contract.get("schema_version") != SCHEMA_VERSION:
        yield "schema_version mismatch"
    if contract.get("status") != STATUS:
        yield "status must be research_only"
    if contract.get("runtime_policy") != RUNTIME_POLICY:
        yield "runtime_policy must be runtime_dormant"
    if contract.get("promotion_effect") != "none_research_only":
        yield "promotion_effect must be none_research_only"
    if contract.get("skill_update_allowed") is not False:
        yield "skill_update_allowed must be false"
    if contract.get("runtime_visibility_change_allowed") is not False:
        yield "runtime_visibility_change_allowed must be false"
    if contract.get("manual_interpretation_required") is not True:
        yield "manual_interpretation_required must be true"
    yield from _validate_product_intent(contract.get("product_intent"))
    yield from _validate_principles(contract.get("principles"))
    yield from _validate_arms(contract.get("comparison_arms"))
    yield from _validate_measurement_protocol(contract.get("measurement_protocol"))
    yield from _validate_cases(contract.get("case_set"), root=root)
    yield from _validate_metrics(contract.get("metrics"))
    yield from _validate_outcomes(contract.get("outcomes"))
    yield from _validate_decision_thresholds(contract.get("decision_thresholds"))
    stop_rules = contract.get("stop_rules")
    if not isinstance(stop_rules, Mapping):
        yield "stop_rules must be object"
    elif not all(stop_rules.get(key) is True for key in stop_rules):
        yield "all stop_rules must be true"


def _comparison_arms() -> list[dict[str, object]]:
    return [
        {
            "arm_id": "legacy_required_pressure_check",
            "step6_table": "current Step 6 material: four lanes plus V60 private enrichment",
            "step7_policy": "required_for_each_non_empty_lane_after_step6b",
            "visible_behavior": "current_skill_behavior",
            "purpose": "baseline",
        },
        {
            "arm_id": "cleaner_table_shadow_required_pressure_check",
            "step6_table": (
                "cleaner private table from dormant pre-Step-6 foundation and "
                "case-appropriate pressure atoms"
            ),
            "step7_policy": "still_required_for_each_non_empty_lane_after_step6b",
            "visible_behavior": "unchanged_shadow_only",
            "purpose": "test whether Step 7 residual work shrinks without removing it",
        },
    ]


def _measurement_protocol() -> dict[str, object]:
    return {
        "record_unit": "case_sample_pair",
        "sample_count_per_case": 3,
        "target_record_count": 12,
        "cleaner_table_operational_definition": {
            "uses_current_pipeline_through_step4": True,
            "step6_receives_cleaner_private_table": True,
            "step7_runs_in_both_arms": True,
            "shadow_portfolio_code_role": (
                "May record cached-deck custody and evidence, but it is not the "
                "whole treatment. The treatment is the Step 6 private table "
                "composition."
            ),
            "included_material": [
                "current four-lane outputs",
                "V60 private enrichment when active for the case",
                "case-appropriate atomic pressure cards from the cleaning evidence surface",
                "answer_delta / structural_delta ledger vocabulary for Step 6 custody",
            ],
            "excluded_material": [
                "new model selector",
                "automatic card graduation",
                "deterministic borderline suppression",
                "any change that skips Step 7 during this comparison",
            ],
        },
        "operator_labeling_protocol": {
            "primary_label_source": "human_operator_review",
            "llm_reviewers_allowed_as_supporting_evidence": True,
            "llm_reviewers_authoritative": False,
            "rubric": [
                (
                    "Label supports_optional_pressure_check_trial only when the "
                    "cleaner-table arm preserves payload and Step 7 no longer "
                    "adds meaningful corrective work for that record."
                ),
                (
                    "Label preserve_required_pressure_check when Step 7 still "
                    "adds a material correction, independent mechanism, or "
                    "safety-relevant divergence."
                ),
                (
                    "Label ambiguous_continue_research when the residual Step 7 "
                    "work is mostly cognitive-independence nuance, reviewer "
                    "evidence is split, or the record is hard to classify."
                ),
            ],
        },
    }


def _case_set() -> list[dict[str, object]]:
    return [
        {
            "case_id": "mid-level-consultant-report-2",
            "case_role": "consultant_graduation_candidate",
            "tests": "whether upstream-carried counsel reversibility reduces Step 7 correction work",
            "failure_read": "Step 7 still finds the same counsel-boundary miss after cleaner table",
            "source_refs": [
                "research/pre-step6-consultant-anchor-boundary-patch-probe/consultant-anchor-boundary-patch-probe-result.v1.json",
                "research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.v1.json",
            ],
        },
        {
            "case_id": "third-year-phd-student.v2.v60-off",
            "case_role": "phd_distributed_atom",
            "tests": "whether distributed atomic cards reduce preventable Step 7 corrections",
            "failure_read": "Step 7 still finds avoidable omissions across the PhD pressure atoms",
            "source_refs": [
                "research/pre-step6-phd-kimi-variance-cleaning-review/phd-kimi-variance-cleaning-review-result.v1.json",
                "research/pre-step6-cleaning-evidence-surface/cleaning-evidence-surface.v1.json",
            ],
        },
        {
            "case_id": "founder-grant-marcus-equity.high-clutter.v60-on",
            "case_role": "founder_v60_destabilization",
            "tests": "whether cleaner table avoids hiding V60 packet instability behind Step 7 removal",
            "failure_read": "cleaner table reduces visible pressure checks while V60 instability remains unexplained",
            "source_refs": [
                "research/pre-step6-founder-v60-private-context-audit/founder-v60-private-context-audit-result.v1.json",
                "research/pre-step6-founder-v60-symmetry-check/founder-v60-symmetry-result.v1.json",
            ],
        },
        {
            "case_id": "mother-address-year",
            "case_role": "negative_control",
            "tests": "whether cleaner table preserves stand-down behavior on a sensitive case",
            "failure_read": "cleaner table creates performative extra pressure where anchor should remain sufficient",
            "source_refs": [
                "research/pre-step6-step6-card-decks/mother-address-year.step6-card-deck.v1.json",
                "research/pre-step6-rendered-hybrid-answer-cores/mother-address-year.native.rendered-hybrid-answer-core.v1.json",
            ],
        },
    ]


def _metrics() -> list[dict[str, object]]:
    return [
        {
            "metric_id": "step7_meaningful_divergence_rate",
            "why": "Primary signal: how often Step 7 still adds material after Step 6.",
            "human_review_required": True,
        },
        {
            "metric_id": "question_1_shift_missed_rate",
            "why": "Tracks shifts Step 6 dismissed or minimized.",
            "human_review_required": True,
        },
        {
            "metric_id": "question_2_material_noise_rate",
            "why": "Tracks findings Step 6 treated as noise but Step 7 treated as material.",
            "human_review_required": True,
        },
        {
            "metric_id": "question_3_named_mechanism_missed_rate",
            "why": "Tracks named mechanisms Step 7 connected that Step 6 did not.",
            "human_review_required": True,
        },
        {
            "metric_id": "clean_table_atom_uptake_rate",
            "why": "Checks whether Step 6 considers pressure atoms discriminately.",
            "human_review_required": False,
        },
        {
            "metric_id": "protected_payload_preservation",
            "why": "Guards against cleaner-table narrowing that drops concrete payload.",
            "human_review_required": False,
        },
        {
            "metric_id": "memo_completeness",
            "why": "Ensures Step 8c still has enough material if Step 7 work shrinks.",
            "human_review_required": True,
        },
        {
            "metric_id": "anthropic_subagent_cost_delta",
            "why": "Measures cost upside without treating cost as correctness.",
            "human_review_required": False,
        },
        {
            "metric_id": "operator_review_label",
            "why": "Captures human interpretation; code may nominate but humans decide.",
            "human_review_required": True,
        },
    ]


def _outcomes() -> list[dict[str, object]]:
    return [
        {
            "label": "supports_optional_pressure_check_trial",
            "meaning": (
                "Cleaner-table arm preserves payload and materially reduces "
                "Step 7 correction work; proceed to a separate gated SKILL.md "
                "optional-pressure trial."
            ),
            "allows_skill_md_edit": False,
        },
        {
            "label": "preserve_required_pressure_check",
            "meaning": (
                "Step 7 still adds meaningful independent or corrective work; "
                "keep current skill flow."
            ),
            "allows_skill_md_edit": False,
        },
        {
            "label": "ambiguous_continue_research",
            "meaning": (
                "Results split by case role or reviewer interpretation; do not "
                "change SKILL.md."
            ),
            "allows_skill_md_edit": False,
        },
    ]


def _decision_thresholds() -> dict[str, object]:
    return {
        "supports_optional_pressure_check_trial": {
            "minimum_records": 12,
            "required_case_roles_covered": sorted(REQUIRED_CASE_ROLES),
            "max_safety_blocked_records": 0,
            "min_support_labels": 9,
            "max_preserve_labels": 1,
            "max_preserve_labels_per_case_role": 1,
            "requires_cleaner_less_than_legacy_divergence_count": True,
            "meaning": (
                "Cleaner table looks strong enough to justify a separate "
                "optional-pressure SKILL.md trial, not direct activation."
            ),
        },
        "preserve_required_pressure_check": {
            "any_safety_blocked_records": True,
            "min_preserve_labels": 4,
            "min_preserve_labels_per_case_role": 2,
            "cleaner_divergence_not_lower_than_legacy": True,
            "meaning": "Keep current required Step 7 flow.",
        },
        "ambiguous_continue_research": {
            "default_when_support_and_preserve_thresholds_do_not_fire": True,
            "meaning": "Do not change SKILL.md; inspect the mixed cases.",
        },
    }


def _validate_product_intent(value: object) -> Iterable[str]:
    if not isinstance(value, Mapping):
        yield "product_intent must be object"
        return
    desired = str(value.get("desired_direction") or "")
    if "Step 7" not in desired or "optional" not in desired:
        yield "product_intent.desired_direction must name Step 7 optionalization"
    if value.get("non_claim") != "Step 7 is not obsolete by assertion.":
        yield "product_intent.non_claim must preserve the Step 7 non-obsolescence boundary"


def _validate_principles(value: object) -> Iterable[str]:
    if not isinstance(value, Mapping):
        yield "principles must be object"
        return
    expected = {
        "code_records": True,
        "humans_decide": True,
        "step6_is_cognitive_solver": True,
        "step7_not_obsolete_by_assertion": True,
        "automatic_graduation_allowed": False,
        "model_selector_allowed": False,
    }
    for key, expected_value in expected.items():
        if value.get(key) is not expected_value:
            yield f"principles.{key} must be {expected_value}"


def _validate_arms(value: object) -> Iterable[str]:
    if not isinstance(value, list) or len(value) != 2:
        yield "comparison_arms must contain exactly two arms"
        return
    arm_ids = {str(arm.get("arm_id")) for arm in value if isinstance(arm, Mapping)}
    if arm_ids != {"legacy_required_pressure_check", "cleaner_table_shadow_required_pressure_check"}:
        yield f"unexpected comparison arms: {sorted(arm_ids)}"
    for arm in value:
        if not isinstance(arm, Mapping):
            yield "comparison arm must be object"
            continue
        if "required" not in str(arm.get("step7_policy")):
            yield f"{arm.get('arm_id')} must keep Step 7 required in this comparison"
        if arm.get("arm_id") == "cleaner_table_shadow_required_pressure_check":
            if arm.get("visible_behavior") != "unchanged_shadow_only":
                yield "cleaner-table arm must stay shadow-only"


def _validate_measurement_protocol(value: object) -> Iterable[str]:
    if not isinstance(value, Mapping):
        yield "measurement_protocol must be object"
        return
    if value.get("record_unit") != "case_sample_pair":
        yield "measurement_protocol.record_unit must be case_sample_pair"
    if value.get("sample_count_per_case") != 3:
        yield "measurement_protocol.sample_count_per_case must be 3"
    if value.get("target_record_count") != 12:
        yield "measurement_protocol.target_record_count must be 12"
    cleaner = value.get("cleaner_table_operational_definition")
    if not isinstance(cleaner, Mapping):
        yield "cleaner_table_operational_definition must be object"
    else:
        if cleaner.get("step7_runs_in_both_arms") is not True:
            yield "cleaner table protocol must keep Step 7 running in both arms"
        if cleaner.get("step6_receives_cleaner_private_table") is not True:
            yield "cleaner table protocol must define Step 6 private-table treatment"
        excluded = cleaner.get("excluded_material")
        if not isinstance(excluded, list) or "new model selector" not in excluded:
            yield "cleaner table protocol must exclude new model selectors"
    labels = value.get("operator_labeling_protocol")
    if not isinstance(labels, Mapping):
        yield "operator_labeling_protocol must be object"
    else:
        if labels.get("primary_label_source") != "human_operator_review":
            yield "primary label source must be human_operator_review"
        if labels.get("llm_reviewers_authoritative") is not False:
            yield "LLM reviewers must not be authoritative"


def _validate_cases(value: object, *, root: Path) -> Iterable[str]:
    if not isinstance(value, list) or len(value) < 4:
        yield "case_set must contain at least four cases"
        return
    roles = {
        str(case.get("case_role"))
        for case in value
        if isinstance(case, Mapping)
    }
    missing_roles = sorted(REQUIRED_CASE_ROLES - roles)
    if missing_roles:
        yield f"missing required case roles: {missing_roles}"
    for case in value:
        if not isinstance(case, Mapping):
            yield "case must be object"
            continue
        refs = case.get("source_refs")
        if not isinstance(refs, list) or not refs:
            yield f"{case.get('case_id')} must include source_refs"
            continue
        for ref in refs:
            if not isinstance(ref, str) or not ref:
                yield f"{case.get('case_id')} has invalid source_ref"
            elif not (root / ref).exists():
                yield f"{case.get('case_id')} missing source_ref: {ref}"


def _validate_metrics(value: object) -> Iterable[str]:
    if not isinstance(value, list):
        yield "metrics must be list"
        return
    metric_ids = {
        str(metric.get("metric_id"))
        for metric in value
        if isinstance(metric, Mapping)
    }
    missing = sorted(REQUIRED_METRICS - metric_ids)
    if missing:
        yield f"missing metrics: {missing}"


def _validate_outcomes(value: object) -> Iterable[str]:
    if not isinstance(value, list):
        yield "outcomes must be list"
        return
    labels = {
        str(outcome.get("label"))
        for outcome in value
        if isinstance(outcome, Mapping)
    }
    missing = sorted(OUTCOME_LABELS - labels)
    if missing:
        yield f"missing outcomes: {missing}"
    for outcome in value:
        if not isinstance(outcome, Mapping):
            yield "outcome must be object"
            continue
        if outcome.get("allows_skill_md_edit") is not False:
            yield f"{outcome.get('label')} must not directly allow SKILL.md edits"


def _validate_decision_thresholds(value: object) -> Iterable[str]:
    if not isinstance(value, Mapping):
        yield "decision_thresholds must be object"
        return
    missing = sorted(OUTCOME_LABELS - set(str(key) for key in value))
    if missing:
        yield f"decision_thresholds missing labels: {missing}"
        return
    supports = value.get("supports_optional_pressure_check_trial")
    if not isinstance(supports, Mapping):
        yield "supports threshold must be object"
    else:
        if supports.get("minimum_records") != 12:
            yield "supports threshold must require 12 records"
        if supports.get("max_safety_blocked_records") != 0:
            yield "supports threshold must allow zero safety blocked records"
        if supports.get("min_support_labels") != 9:
            yield "supports threshold must require at least 9 support labels"
        if supports.get("max_preserve_labels") != 1:
            yield "supports threshold must allow at most 1 preserve label"
    preserve = value.get("preserve_required_pressure_check")
    if not isinstance(preserve, Mapping):
        yield "preserve threshold must be object"
    else:
        if preserve.get("any_safety_blocked_records") is not True:
            yield "preserve threshold must fire on any safety blocked record"
        if preserve.get("min_preserve_labels") != 4:
            yield "preserve threshold must fire at 4 preserve labels"


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    contract = build_skill_shadow_comparison_contract(root=args.root)
    if args.write:
        write_skill_shadow_comparison_contract(contract=contract, out_dir=args.out_dir, root=args.root)
        write_skill_shadow_comparison_contract_markdown(
            contract=contract,
            out_dir=args.out_dir,
            root=args.root,
        )
    else:
        print(json.dumps(contract, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

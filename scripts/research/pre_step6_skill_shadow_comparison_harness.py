#!/usr/bin/env python3
"""Aggregate paired skill shadow-comparison records.

This harness does not run `/lolla`, call models, edit `SKILL.md`, or decide
whether Step 7 should be removed. It validates paired case records and computes
mechanical summaries so humans can decide whether a later skill-change trial is
earned.

The active skill decision now rests Step 7 by default. This harness remains as
historical research tooling and should not be treated as the active gate for
the default-off skill change.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from pre_step6_skill_shadow_comparison_contract import (
    OUTCOME_LABELS,
    build_skill_shadow_comparison_contract,
    validate_skill_shadow_comparison_contract,
)


CASE_SCHEMA_VERSION = "pre_step6_skill_shadow_comparison_case.v1"
RESULT_SCHEMA_VERSION = "pre_step6_skill_shadow_comparison_result.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "skill_shadow_comparison_v0"
LEGACY_ARM_ID = "legacy_required_pressure_check"
CLEANER_ARM_ID = "cleaner_table_shadow_required_pressure_check"
ARM_IDS = {LEGACY_ARM_ID, CLEANER_ARM_ID}
DEFAULT_CONTRACT_PATH = (
    Path("research/pre-step6-skill-shadow-comparison-contract")
    / "skill-shadow-comparison-contract.v1.json"
)
DEFAULT_OUT_DIR = Path("research/pre-step6-skill-shadow-comparison")


class SkillShadowComparisonHarnessError(ValueError):
    pass


def load_skill_shadow_comparison_contract(*, root: Path, path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, object]:
    if path.exists():
        contract = json.loads(path.read_text(encoding="utf-8"))
    else:
        contract = build_skill_shadow_comparison_contract(root=root)
    validate_skill_shadow_comparison_contract(contract, root=root)
    return contract


def load_case_records(records_dir: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(records_dir.glob("*.skill-shadow-comparison-case.v1.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_skill_shadow_comparison_case_record(payload)
        records.append(payload)
    return records


def build_skill_shadow_comparison_result(
    *,
    contract: dict[str, object],
    case_records: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_skill_shadow_comparison_contract(contract, root=Path("."))
    for record in case_records:
        validate_skill_shadow_comparison_case_record(record)

    case_summaries = [_summarize_case(record) for record in case_records]
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "skill_update_allowed": False,
        "runtime_visibility_change_allowed": False,
        "operator_review_required": True,
        "contract_ref": "research/pre-step6-skill-shadow-comparison-contract/skill-shadow-comparison-contract.v1.json",
        "case_count": len(case_summaries),
        "case_summaries": case_summaries,
        "aggregate": _aggregate_case_summaries(case_summaries),
        "gates": {
            "skill_md_edit_allowed": False,
            "runtime_promotion_allowed": False,
            "automatic_optionalization_allowed": False,
        },
        "notes": [
            "Mechanical aggregate only; humans decide whether any later skill trial is earned.",
            "Historical harness only; Step 7 is now rested by default in the live skill.",
            "Both historical comparison arms kept Step 7 required; this harness measured residual work, not removal.",
        ],
    }
    validate_skill_shadow_comparison_result(result)
    return result


def write_skill_shadow_comparison_result(*, result: dict[str, object], out_dir: Path) -> Path:
    validate_skill_shadow_comparison_result(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "skill-shadow-comparison-result.v1.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def validate_skill_shadow_comparison_case_record(record: dict[str, object]) -> None:
    errors = list(iter_skill_shadow_comparison_case_record_errors(record))
    if errors:
        raise SkillShadowComparisonHarnessError("; ".join(errors))


def iter_skill_shadow_comparison_case_record_errors(record: dict[str, object]) -> Iterable[str]:
    if not isinstance(record, dict):
        yield "case record must be object"
        return
    required = {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "case_role",
        "arms",
        "operator_review",
        "gates",
    }
    missing = sorted(required - set(record))
    if missing:
        yield f"missing fields: {missing}"
        return
    if record.get("schema_version") != CASE_SCHEMA_VERSION:
        yield "schema_version mismatch"
    if record.get("status") != STATUS:
        yield "status must be research_only"
    if record.get("runtime_policy") != RUNTIME_POLICY:
        yield "runtime_policy must be runtime_dormant"
    if record.get("experiment_id") != EXPERIMENT_ID:
        yield "experiment_id mismatch"
    arms = record.get("arms")
    if not isinstance(arms, Mapping):
        yield "arms must be object"
    else:
        if set(arms.keys()) != ARM_IDS:
            yield f"arms must contain {sorted(ARM_IDS)}"
        for arm_id, arm in arms.items():
            yield from _validate_arm_record(str(arm_id), arm)
    operator_review = record.get("operator_review")
    if not isinstance(operator_review, Mapping):
        yield "operator_review must be object"
    else:
        label = operator_review.get("label")
        if label not in OUTCOME_LABELS:
            yield f"operator_review.label must be one of {sorted(OUTCOME_LABELS)}"
        if not str(operator_review.get("rationale") or "").strip():
            yield "operator_review.rationale is required"
    gates = record.get("gates")
    if not isinstance(gates, Mapping):
        yield "gates must be object"
    else:
        if gates.get("skill_update_allowed") is not False:
            yield "gates.skill_update_allowed must be false"
        if gates.get("runtime_visibility_change_allowed") is not False:
            yield "gates.runtime_visibility_change_allowed must be false"


def validate_skill_shadow_comparison_result(result: dict[str, object]) -> None:
    errors = list(iter_skill_shadow_comparison_result_errors(result))
    if errors:
        raise SkillShadowComparisonHarnessError("; ".join(errors))


def iter_skill_shadow_comparison_result_errors(result: dict[str, object]) -> Iterable[str]:
    if not isinstance(result, dict):
        yield "result must be object"
        return
    required = {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "skill_update_allowed",
        "runtime_visibility_change_allowed",
        "operator_review_required",
        "contract_ref",
        "case_count",
        "case_summaries",
        "aggregate",
        "gates",
        "notes",
    }
    missing = sorted(required - set(result))
    if missing:
        yield f"missing fields: {missing}"
        return
    if result.get("schema_version") != RESULT_SCHEMA_VERSION:
        yield "schema_version mismatch"
    if result.get("status") != STATUS:
        yield "status must be research_only"
    if result.get("runtime_policy") != RUNTIME_POLICY:
        yield "runtime_policy must be runtime_dormant"
    if result.get("promotion_effect") != "none_research_only":
        yield "promotion_effect must be none_research_only"
    if result.get("skill_update_allowed") is not False:
        yield "skill_update_allowed must be false"
    if result.get("runtime_visibility_change_allowed") is not False:
        yield "runtime_visibility_change_allowed must be false"
    if result.get("operator_review_required") is not True:
        yield "operator_review_required must be true"
    case_summaries = result.get("case_summaries")
    if not isinstance(case_summaries, list):
        yield "case_summaries must be list"
    elif result.get("case_count") != len(case_summaries):
        yield "case_count must match case_summaries length"
    aggregate = result.get("aggregate")
    if not isinstance(aggregate, Mapping):
        yield "aggregate must be object"
    else:
        if aggregate.get("human_decision_required") is not True:
            yield "aggregate.human_decision_required must be true"
    gates = result.get("gates")
    if not isinstance(gates, Mapping):
        yield "gates must be object"
    else:
        if any(gates.get(key) is not False for key in gates):
            yield "all result gates must be false"


def build_static_skill_shadow_case_record(
    *,
    case_id: str,
    case_role: str,
    legacy_meaningful: Sequence[int],
    cleaner_meaningful: Sequence[int],
    operator_label: str,
    cleaner_payload_preserved: bool = True,
    cleaner_memo_complete: bool = True,
    legacy_cost: float = 1.0,
    cleaner_cost: float = 1.0,
) -> dict[str, object]:
    record = {
        "schema_version": CASE_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "case_role": case_role,
        "arms": {
            LEGACY_ARM_ID: _static_arm(
                arm_id=LEGACY_ARM_ID,
                meaningful_questions=legacy_meaningful,
                protected_payload_preserved=True,
                memo_complete=True,
                cost=legacy_cost,
            ),
            CLEANER_ARM_ID: _static_arm(
                arm_id=CLEANER_ARM_ID,
                meaningful_questions=cleaner_meaningful,
                protected_payload_preserved=cleaner_payload_preserved,
                memo_complete=cleaner_memo_complete,
                cost=cleaner_cost,
                clean_table_atom_uptake_count=max(len(cleaner_meaningful), 1),
            ),
        },
        "operator_review": {
            "label": operator_label,
            "rationale": "Static test fixture rationale.",
        },
        "gates": {
            "skill_update_allowed": False,
            "runtime_visibility_change_allowed": False,
        },
    }
    validate_skill_shadow_comparison_case_record(record)
    return record


def _validate_arm_record(arm_id: str, arm: object) -> Iterable[str]:
    if not isinstance(arm, Mapping):
        yield f"{arm_id} arm must be object"
        return
    required = {
        "arm_id",
        "run_ref",
        "step7_policy",
        "visible_behavior",
        "gap_check",
        "protected_payload_preserved",
        "memo_complete",
        "anthropic_subagent_cost_usd",
    }
    missing = sorted(required - set(arm))
    if missing:
        yield f"{arm_id} missing fields: {missing}"
        return
    if arm.get("arm_id") != arm_id:
        yield f"{arm_id} arm_id mismatch"
    if "required" not in str(arm.get("step7_policy")):
        yield f"{arm_id} must keep Step 7 required"
    if not isinstance(arm.get("protected_payload_preserved"), bool):
        yield f"{arm_id}.protected_payload_preserved must be bool"
    if not isinstance(arm.get("memo_complete"), bool):
        yield f"{arm_id}.memo_complete must be bool"
    if not isinstance(arm.get("anthropic_subagent_cost_usd"), (int, float)):
        yield f"{arm_id}.anthropic_subagent_cost_usd must be number"
    yield from _validate_gap_check(arm_id, arm.get("gap_check"))


def _validate_gap_check(arm_id: str, gap_check: object) -> Iterable[str]:
    if not isinstance(gap_check, Mapping):
        yield f"{arm_id}.gap_check must be object"
        return
    lanes = gap_check.get("lanes")
    if not isinstance(lanes, list):
        yield f"{arm_id}.gap_check.lanes must be list"
        return
    for lane in lanes:
        if not isinstance(lane, Mapping):
            yield f"{arm_id}.gap_check lane must be object"
            continue
        divergences = lane.get("divergences")
        if not isinstance(divergences, list):
            yield f"{arm_id}.gap_check lane divergences must be list"
            continue
        for divergence in divergences:
            if not isinstance(divergence, Mapping):
                yield f"{arm_id}.gap_check divergence must be object"
                continue
            if divergence.get("question_number") not in {1, 2, 3}:
                yield f"{arm_id}.divergence question_number must be 1, 2, or 3"
            if not isinstance(divergence.get("meaningful"), bool):
                yield f"{arm_id}.divergence meaningful must be bool"
            if not str(divergence.get("description") or "").strip():
                yield f"{arm_id}.divergence description is required"


def _summarize_case(record: Mapping[str, object]) -> dict[str, object]:
    arms = record["arms"]  # type: ignore[index]
    if not isinstance(arms, Mapping):
        raise SkillShadowComparisonHarnessError("record arms must be object")
    legacy = _summarize_arm(arms[LEGACY_ARM_ID])  # type: ignore[index]
    cleaner = _summarize_arm(arms[CLEANER_ARM_ID])  # type: ignore[index]
    operator_review = record["operator_review"]  # type: ignore[index]
    if not isinstance(operator_review, Mapping):
        raise SkillShadowComparisonHarnessError("operator_review must be object")
    return {
        "case_id": record["case_id"],
        "case_role": record["case_role"],
        "legacy": legacy,
        "cleaner": cleaner,
        "meaningful_divergence_delta": legacy["meaningful_divergence_count"]
        - cleaner["meaningful_divergence_count"],
        "cost_delta_usd": legacy["anthropic_subagent_cost_usd"]
        - cleaner["anthropic_subagent_cost_usd"],
        "operator_review_label": operator_review["label"],
        "operator_review_rationale": operator_review["rationale"],
        "safety_blocked": not cleaner["protected_payload_preserved"] or not cleaner["memo_complete"],
    }


def _summarize_arm(arm: object) -> dict[str, object]:
    if not isinstance(arm, Mapping):
        raise SkillShadowComparisonHarnessError("arm must be object")
    divergences = _meaningful_divergences(arm)
    q_counts = {str(question): 0 for question in (1, 2, 3)}
    for divergence in divergences:
        q_counts[str(divergence["question_number"])] += 1
    return {
        "arm_id": arm["arm_id"],
        "meaningful_divergence_count": len(divergences),
        "question_counts": q_counts,
        "protected_payload_preserved": arm["protected_payload_preserved"],
        "memo_complete": arm["memo_complete"],
        "anthropic_subagent_cost_usd": float(arm["anthropic_subagent_cost_usd"]),
        "clean_table_atom_uptake_count": int(arm.get("clean_table_atom_uptake_count") or 0),
    }


def _aggregate_case_summaries(case_summaries: Sequence[Mapping[str, object]]) -> dict[str, object]:
    label_counts = {label: 0 for label in sorted(OUTCOME_LABELS)}
    preserve_labels_by_case_role: dict[str, int] = {}
    total_legacy = 0
    total_cleaner = 0
    total_delta = 0
    total_cost_delta = 0.0
    safety_blocked_count = 0
    cleaner_payload_preserved_count = 0
    cleaner_memo_complete_count = 0
    for summary in case_summaries:
        legacy = summary["legacy"]
        cleaner = summary["cleaner"]
        if not isinstance(legacy, Mapping) or not isinstance(cleaner, Mapping):
            continue
        total_legacy += int(legacy["meaningful_divergence_count"])
        total_cleaner += int(cleaner["meaningful_divergence_count"])
        total_delta += int(summary["meaningful_divergence_delta"])
        total_cost_delta += float(summary["cost_delta_usd"])
        label = str(summary["operator_review_label"])
        if label in label_counts:
            label_counts[label] += 1
        if label == "preserve_required_pressure_check":
            role = str(summary["case_role"])
            preserve_labels_by_case_role[role] = preserve_labels_by_case_role.get(role, 0) + 1
        if summary["safety_blocked"]:
            safety_blocked_count += 1
        if cleaner["protected_payload_preserved"]:
            cleaner_payload_preserved_count += 1
        if cleaner["memo_complete"]:
            cleaner_memo_complete_count += 1

    return {
        "case_count": len(case_summaries),
        "legacy_meaningful_divergence_count": total_legacy,
        "cleaner_meaningful_divergence_count": total_cleaner,
        "meaningful_divergence_delta": total_delta,
        "anthropic_subagent_cost_delta_usd": round(total_cost_delta, 6),
        "cleaner_payload_preserved_count": cleaner_payload_preserved_count,
        "cleaner_memo_complete_count": cleaner_memo_complete_count,
        "safety_blocked_count": safety_blocked_count,
        "operator_review_distribution": label_counts,
        "preserve_labels_by_case_role": preserve_labels_by_case_role,
        "human_decision_required": True,
        "candidate_read": _candidate_read(
            label_counts=label_counts,
            preserve_labels_by_case_role=preserve_labels_by_case_role,
            safety_blocked_count=safety_blocked_count,
            case_count=len(case_summaries),
            total_legacy=total_legacy,
            total_cleaner=total_cleaner,
        ),
    }


def _candidate_read(
    *,
    label_counts: Mapping[str, int],
    preserve_labels_by_case_role: Mapping[str, int],
    safety_blocked_count: int,
    case_count: int,
    total_legacy: int,
    total_cleaner: int,
) -> str:
    if safety_blocked_count:
        return "preserve_required_pressure_check"
    if label_counts.get("preserve_required_pressure_check", 0) >= 4:
        return "preserve_required_pressure_check"
    if any(count >= 2 for count in preserve_labels_by_case_role.values()):
        return "preserve_required_pressure_check"
    if case_count >= 12 and total_cleaner >= total_legacy:
        return "preserve_required_pressure_check"
    if case_count < 12:
        return "ambiguous_continue_research"
    if (
        label_counts.get("supports_optional_pressure_check_trial", 0) >= 9
        and label_counts.get("preserve_required_pressure_check", 0) <= 1
        and total_cleaner < total_legacy
    ):
        return "supports_optional_pressure_check_trial"
    return "ambiguous_continue_research"


def _meaningful_divergences(arm: Mapping[str, object]) -> list[Mapping[str, object]]:
    gap_check = arm.get("gap_check")
    if not isinstance(gap_check, Mapping):
        return []
    divergences: list[Mapping[str, object]] = []
    lanes = gap_check.get("lanes")
    if not isinstance(lanes, list):
        return []
    for lane in lanes:
        if not isinstance(lane, Mapping):
            continue
        for divergence in lane.get("divergences", []):
            if isinstance(divergence, Mapping) and divergence.get("meaningful") is True:
                divergences.append(divergence)
    return divergences


def _static_arm(
    *,
    arm_id: str,
    meaningful_questions: Sequence[int],
    protected_payload_preserved: bool,
    memo_complete: bool,
    cost: float,
    clean_table_atom_uptake_count: int = 0,
) -> dict[str, object]:
    return {
        "arm_id": arm_id,
        "run_ref": f"synthetic://{arm_id}",
        "step7_policy": "required_for_each_non_empty_lane_after_step6b",
        "visible_behavior": "unchanged_shadow_only" if arm_id == CLEANER_ARM_ID else "current_skill_behavior",
        "gap_check": {
            "lanes": [
                {
                    "lane_number": 1,
                    "lane_name": "SyntheticLane",
                    "status": "completed",
                    "divergences": [
                        {
                            "question_number": question,
                            "description": f"Static meaningful divergence for question {question}.",
                            "meaningful": True,
                        }
                        for question in meaningful_questions
                    ],
                }
            ]
        },
        "protected_payload_preserved": protected_payload_preserved,
        "memo_complete": memo_complete,
        "anthropic_subagent_cost_usd": cost,
        "clean_table_atom_uptake_count": clean_table_atom_uptake_count,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--records-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    contract = load_skill_shadow_comparison_contract(root=args.root, path=args.contract)
    case_records = load_case_records(args.records_dir)
    result = build_skill_shadow_comparison_result(contract=contract, case_records=case_records)
    if args.write:
        write_skill_shadow_comparison_result(result=result, out_dir=args.out_dir)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

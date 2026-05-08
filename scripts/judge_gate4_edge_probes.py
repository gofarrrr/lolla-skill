#!/usr/bin/env python3
"""Blinded judge runner for the Gate 4 edge-probe experiment.

Reads Arm A/B/C outputs from data/evaluations/gate4_edge_probes, shuffles labels
per route by seed, and asks a stronger boundary judge to compare constructive
edge. Dry-run validates inputs and writes packets without making LLM calls.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_gate4_edge_probe_experiment import (  # noqa: E402
    CLARITY_COSTS,
    DEFAULT_AFFORDANCES_PATH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SEED,
    EDGE_FIELD_SOURCES,
    HIGH_VALUE_FIELD_SOURCES,
    Gate4ExperimentError,
    _dict,
    _list,
    _load_json,
    _resolve_repo_path,
    _str,
    _write_json,
    call_openrouter_json,
    expected_activation_affordances,
    load_affordance_index,
    load_dotenv,
    validate_arm_a_output,
    validate_edge_probe_output,
    validate_trace_ids,
)


JUDGE_EDGE_SOURCES = {
    "model_general_knowledge",
    "diagnostic_question",
    "treatment_requirement",
    "do_not_use_when",
    "case_evidence_needed",
    "misuse_guard",
    "none",
}
WINNERS = {"A", "B", "C", "tie", "all_bad"}
CONSTRUCTIVE_EDGE = {"A", "B", "C", "none"}
OUT_OF_DISTRIBUTION = {"A", "B", "C", "neither", "both"}
LIKELY_ENUM = {"yes", "no", "unclear"}
DECISION_RELEVANCE = {"high", "medium", "low"}
DISMISSAL_PATH = {"clear", "fuzzy", "none"}
THEATER_FLAG = {"yes", "no"}
JUDGE_SYSTEM_PROMPT = """\
You are the blinded Gate 4 judge for Lolla's edge-probe experiment.

You receive three labeled outputs for the same archived case route. The labels
are shuffled. Do not infer which label is baseline, generic prompt, or
affordance-enriched. Judge which output contributes the strongest constructive
edge: a bounded, potentially useful pressure that the ordinary reasoning path
would likely miss, with a clear dismissal path.

Separately identify out_of_distribution: which output contains an operational
edge that a strong case-prompted LLM using only the routed model names would
probably not reach. This is stricter than "better" or "more specific". If the
strong generic prompt would likely reach the same pressure, do not credit OOD
to that output. Use "both" only when more than one output contains a genuinely
non-obvious edge; use "neither" when all outputs stay on the generic track.

Reward source-traced operational constraints over sophisticated restatement.
Penalize mud: probes that add ambiguity without a dismissal condition.

Return only JSON matching the requested schema. Do not include markdown.
"""


def blind_arm_mapping(case_id: str, route_id: str, seed: int) -> dict[str, str]:
    """Map blinded labels A/B/C to actual arms A/B/C, deterministically."""
    actual = ["A", "B", "C"]
    rng = random.Random(f"{seed}:{case_id}:{route_id}")
    rng.shuffle(actual)
    return dict(zip(["A", "B", "C"], actual))


def unblind_label(label: str, blind_map: dict[str, str]) -> str:
    if label in blind_map:
        return blind_map[label]
    return label


def _arm_path(input_dir: Path, arm: str, stem: str) -> Path:
    return input_dir / f"arm_{arm.lower()}" / f"{stem}.json"


def _packet_path(input_dir: Path, arm: str, stem: str) -> Path:
    return input_dir / "packets" / f"arm_{arm.lower()}" / f"{stem}.json"


def available_route_stems(input_dir: Path) -> list[str]:
    arm_a_dir = input_dir / "arm_a"
    if not arm_a_dir.exists():
        return []
    return sorted(path.stem for path in arm_a_dir.glob("*.json"))


def load_arm_outputs(input_dir: Path, stem: str, *, dry_run: bool = False) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for arm in ("A", "B", "C"):
        path = _arm_path(input_dir, arm, stem)
        if not path.exists():
            packet_path = _packet_path(input_dir, arm, stem)
            if dry_run and arm in {"B", "C"} and packet_path.exists():
                packet = _load_json(packet_path)
                outputs[arm] = {
                    "case_id": _str(packet.get("case_id")),
                    "route_id": _str(packet.get("route_id")),
                    "arm": arm,
                    "dry_run_placeholder": True,
                    "packet_path": str(packet_path),
                    "packet_estimated_tokens": 0,
                }
                continue
            missing.append(str(path))
            continue
        outputs[arm] = _load_json(path)
    if missing:
        raise Gate4ExperimentError(
            f"Missing arm outputs for {stem}: " + "; ".join(missing)
        )
    return outputs


def _load_packet(input_dir: Path, arm: str, stem: str) -> dict[str, Any]:
    path = _packet_path(input_dir, arm, stem)
    if not path.exists():
        return {}
    return _load_json(path)


def validate_arm_inputs(
    *,
    input_dir: Path,
    stem: str,
    outputs: dict[str, dict[str, Any]],
    affordance_index: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    errors.extend(f"arm A: {error}" for error in validate_arm_a_output(outputs["A"]))

    packet_b = _load_packet(input_dir, "B", stem)
    packet_c = _load_packet(input_dir, "C", stem)

    if outputs["B"].get("dry_run_placeholder"):
        errors.extend(f"arm B packet: {error}" for error in validate_packet_placeholder(packet_b, expected_arm="B"))
    else:
        errors.extend(
            f"arm B: {error}"
            for error in validate_edge_probe_output(
                outputs["B"],
                expected_arm="B",
                affordance_index=affordance_index,
                require_verified_traces=False,
                case_context=_dict(packet_b.get("case_context")),
            )
        )
    if outputs["C"].get("dry_run_placeholder"):
        errors.extend(f"arm C packet: {error}" for error in validate_packet_placeholder(packet_c, expected_arm="C"))
    else:
        errors.extend(
            f"arm C: {error}"
            for error in validate_edge_probe_output(
                outputs["C"],
                expected_arm="C",
                affordance_index=affordance_index,
                require_verified_traces=True,
                expected_activation_ids=expected_activation_affordances(packet_c)
                if packet_c
                else None,
                case_context=_dict(packet_c.get("case_context")),
            )
        )
    return errors


def validate_packet_placeholder(packet: dict[str, Any], *, expected_arm: str) -> list[str]:
    errors: list[str] = []
    if not packet:
        errors.append("packet is missing")
        return errors
    if packet.get("arm") != expected_arm:
        errors.append(f"packet arm must be {expected_arm}")
    for key in ("case_id", "route_id", "case_context", "gap_route"):
        if key not in packet:
            errors.append(f"packet.{key} is missing")
    if expected_arm == "B" and "affordance_records" in packet:
        errors.append("Arm B packet must not include affordance_records")
    if expected_arm == "C" and not isinstance(packet.get("affordance_records"), list):
        errors.append("Arm C packet must include affordance_records list")
    return errors


def build_judge_packet(
    *,
    outputs: dict[str, dict[str, Any]],
    seed: int,
) -> dict[str, Any]:
    case_id = _str(outputs["A"].get("case_id"))
    route_id = _str(outputs["A"].get("route_id"))
    blind_map = blind_arm_mapping(case_id, route_id, seed)
    blinded_outputs = [
        {"label": label, "output": outputs[actual_arm]}
        for label, actual_arm in blind_map.items()
    ]
    return {
        "experiment": "gate4_edge_probe_judge",
        "case_id": case_id,
        "route_id": route_id,
        "blind_map_sha_note": "blind_map is stored outside the judge prompt in the output artifact",
        "outputs": blinded_outputs,
        "judge_schema": {
            "case_id": "string",
            "route_id": "string",
            "winner": "A | B | C | tie | all_bad",
            "constructive_edge": "A | B | C | none",
            "out_of_distribution": "A | B | C | neither | both",
            "out_of_distribution_arms": ["A | B | C"],
            "edge_source": "model_general_knowledge | diagnostic_question | treatment_requirement | do_not_use_when | case_evidence_needed | misuse_guard | none",
            "baseline_likely_would_reach": "yes | no | unclear",
            "generic_prompt_likely_would_reach": "yes | no | unclear",
            "decision_relevance_if_true": "high | medium | low",
            "dismissal_path": "clear | fuzzy | none",
            "clarity_cost": "low | medium | high",
            "theater_flag": "yes | no",
            "rationale": "string",
        },
    }


def validate_judge_output(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("case_id", "route_id", "rationale"):
        if not _str(payload.get(key)):
            errors.append(f"{key} must be a non-empty string")
    metadata = _dict(payload.get("judge_call_metadata"))
    for key in ("provider", "model"):
        if not _str(metadata.get(key)):
            errors.append(f"judge_call_metadata.{key} must be a non-empty string")
    for key in ("input_tokens", "output_tokens"):
        if not isinstance(metadata.get(key), int):
            errors.append(f"judge_call_metadata.{key} must be an integer")
    if not isinstance(metadata.get("cost_usd"), (int, float)):
        errors.append("judge_call_metadata.cost_usd must be a number")
    if _str(payload.get("winner")) not in WINNERS:
        errors.append("winner is invalid")
    if _str(payload.get("constructive_edge")) not in CONSTRUCTIVE_EDGE:
        errors.append("constructive_edge is invalid")
    if _str(payload.get("out_of_distribution")) not in OUT_OF_DISTRIBUTION:
        errors.append("out_of_distribution is invalid")
    ood_arms = payload.get("out_of_distribution_arms")
    if not isinstance(ood_arms, list) or not all(
        isinstance(label, str) and label in {"A", "B", "C"} for label in ood_arms
    ):
        errors.append("out_of_distribution_arms must be a list of A/B/C labels")
    else:
        deduped_arms = sorted(set(ood_arms))
        if len(deduped_arms) != len(ood_arms):
            errors.append("out_of_distribution_arms must not contain duplicates")
        ood = _str(payload.get("out_of_distribution"))
        if ood == "neither" and ood_arms:
            errors.append("out_of_distribution_arms must be empty when OOD is neither")
        elif ood in {"A", "B", "C"} and ood_arms != [ood]:
            errors.append("out_of_distribution_arms must match single-arm OOD")
        elif ood == "both" and len(ood_arms) < 2:
            errors.append("out_of_distribution_arms must name at least two arms when OOD is both")
    if _str(payload.get("edge_source")) not in JUDGE_EDGE_SOURCES:
        errors.append("edge_source is invalid")
    for key in ("baseline_likely_would_reach", "generic_prompt_likely_would_reach"):
        if _str(payload.get(key)) not in LIKELY_ENUM:
            errors.append(f"{key} is invalid")
    if _str(payload.get("decision_relevance_if_true")) not in DECISION_RELEVANCE:
        errors.append("decision_relevance_if_true is invalid")
    if _str(payload.get("dismissal_path")) not in DISMISSAL_PATH:
        errors.append("dismissal_path is invalid")
    if _str(payload.get("clarity_cost")) not in CLARITY_COSTS:
        errors.append("clarity_cost is invalid")
    if _str(payload.get("theater_flag")) not in THEATER_FLAG:
        errors.append("theater_flag is invalid")
    return errors


def normalize_judge_payload(
    payload: dict[str, Any],
    *,
    packet: dict[str, Any],
    blind_map: dict[str, str],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(payload)
    ood_arms = [
        unblind_label(label, blind_map)
        for label in _list(normalized.get("out_of_distribution_arms"))
        if isinstance(label, str)
    ]
    normalized["case_id"] = _str(packet.get("case_id"))
    normalized["route_id"] = _str(packet.get("route_id"))
    normalized["judge_call_metadata"] = metadata
    normalized["blind_map"] = blind_map
    normalized["unblinded"] = {
        "winner": unblind_label(_str(normalized.get("winner")), blind_map),
        "constructive_edge": unblind_label(
            _str(normalized.get("constructive_edge")), blind_map
        ),
        "out_of_distribution": unblind_label(
            _str(normalized.get("out_of_distribution")), blind_map
        ),
        "out_of_distribution_arms": sorted(dict.fromkeys(ood_arms)),
    }
    return normalized


def run_judge_call(
    *,
    judge_provider: str,
    judge_model: str,
    packet: dict[str, Any],
    blind_map: dict[str, str],
) -> dict[str, Any]:
    if judge_provider != "openrouter":
        raise Gate4ExperimentError("Only --judge-provider openrouter is implemented for PR11")
    if not judge_model:
        raise Gate4ExperimentError("--judge-model is required for non-dry-run judging")
    if judge_model.lower().startswith("x-ai/grok-4.1-fast"):
        raise Gate4ExperimentError("Gate 4 judge must not be x-ai/grok-4.1-fast")
    load_dotenv()
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise Gate4ExperimentError(
            "Missing OpenRouter API key: set LOLLA_OPENROUTER_API_KEY or OPENROUTER_API_KEY"
        )
    payload, metadata = call_openrouter_json(
        api_key=api_key,
        model=judge_model,
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_packet=packet,
    )
    return normalize_judge_payload(
        payload,
        packet=packet,
        blind_map=blind_map,
        metadata=metadata,
    )


def _usage_totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    input_tokens = 0
    output_tokens = 0
    cost_usd = 0.0
    for record in records:
        metadata = _dict(record.get("judge_call_metadata"))
        input_tokens += int(metadata.get("input_tokens") or 0)
        output_tokens += int(metadata.get("output_tokens") or 0)
        cost_usd += float(metadata.get("cost_usd") or 0.0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost_usd, 6),
    }


def _c_trace_stats(
    arm_c_outputs: list[dict[str, Any]],
    affordance_index: dict[str, dict[str, Any]],
) -> dict[str, int | float]:
    total = 0
    valid = 0
    for output in arm_c_outputs:
        for probe in _list(output.get("edge_probes")):
            trace = _dict(_dict(probe).get("trace"))
            total += 1
            if not validate_trace_ids(trace, affordance_index):
                valid += 1
    return {
        "total_c_edge_probes": total,
        "valid_c_trace_ids": valid,
        "valid_c_trace_fraction": round(valid / total, 4) if total else 0.0,
    }


def _ood_arms_from_record(record: dict[str, Any]) -> tuple[str, ...]:
    unblinded = _dict(record.get("unblinded"))
    raw_arms = _list(unblinded.get("out_of_distribution_arms"))
    arms = sorted(
        {
            label
            for label in raw_arms
            if isinstance(label, str) and label in {"A", "B", "C"}
        }
    )
    if arms:
        return tuple(arms)
    scalar = _str(unblinded.get("out_of_distribution"))
    if scalar in {"A", "B", "C"}:
        return (scalar,)
    return ()


def _nested_counter_to_dict(counter: dict[str, Counter[str]]) -> dict[str, dict[str, int]]:
    return {
        key: dict(sorted(value.items()))
        for key, value in sorted(counter.items())
    }


def summarize_judge_outputs(
    *,
    judge_records: list[dict[str, Any]],
    arm_c_outputs: list[dict[str, Any]],
    affordance_index: dict[str, dict[str, Any]],
    dry_run: bool,
    seed: int,
    judge_provider: str,
    judge_model: str,
    route_count: int,
) -> dict[str, Any]:
    winner_counts = Counter()
    constructive_edge_counts = Counter()
    ood_counts = Counter()
    ood_arm_counts = Counter()
    ood_by_arm_source_counts: dict[str, Counter[str]] = {}
    c_only_ood_source_counts = Counter()
    c_included_ood_source_counts = Counter()
    edge_source_counts = Counter()
    case_constructive_votes: dict[str, Counter[str]] = {}
    case_ood_votes: dict[str, Counter[str]] = {}
    case_high_value_c: set[str] = set()
    case_high_value_c_ood: set[str] = set()
    theater_count = 0
    high_clarity_count = 0
    high_value_c_wins = 0
    high_value_c_ood = 0
    regressions_vs_a = 0
    for record in judge_records:
        unblinded = _dict(record.get("unblinded"))
        winner = _str(unblinded.get("winner"))
        constructive_edge = _str(unblinded.get("constructive_edge"))
        out_of_distribution = _str(unblinded.get("out_of_distribution"))
        ood_arms = _ood_arms_from_record(record)
        edge_source = _str(record.get("edge_source"))
        winner_counts[winner] += 1
        constructive_edge_counts[constructive_edge] += 1
        ood_counts[out_of_distribution] += 1
        for arm in ood_arms:
            ood_arm_counts[arm] += 1
            ood_by_arm_source_counts.setdefault(arm, Counter())[edge_source] += 1
        if ood_arms == ("C",):
            c_only_ood_source_counts[edge_source] += 1
        if "C" in ood_arms:
            c_included_ood_source_counts[edge_source] += 1
        edge_source_counts[edge_source] += 1
        case_id = _str(record.get("case_id"))
        if case_id:
            case_constructive_votes.setdefault(case_id, Counter())[constructive_edge] += 1
            case_ood_votes.setdefault(case_id, Counter())[out_of_distribution] += 1
        if record.get("theater_flag") == "yes":
            theater_count += 1
        if record.get("clarity_cost") == "high":
            high_clarity_count += 1
        if constructive_edge == "C" and edge_source in HIGH_VALUE_FIELD_SOURCES:
            high_value_c_wins += 1
            if case_id:
                case_high_value_c.add(case_id)
        if ood_arms == ("C",) and edge_source in HIGH_VALUE_FIELD_SOURCES:
            high_value_c_ood += 1
            if case_id:
                case_high_value_c_ood.add(case_id)
        if winner == "A" and constructive_edge == "A":
            regressions_vs_a += 1
    case_level_constructive: dict[str, str] = {}
    for case_id, votes in sorted(case_constructive_votes.items()):
        if not votes:
            case_level_constructive[case_id] = "none"
            continue
        max_count = max(votes.values())
        top = sorted(label for label, count in votes.items() if count == max_count)
        case_level_constructive[case_id] = top[0] if len(top) == 1 else "tie"
    case_level_counts = Counter(case_level_constructive.values())
    case_level_ood: dict[str, str] = {}
    for case_id, votes in sorted(case_ood_votes.items()):
        if not votes:
            case_level_ood[case_id] = "neither"
            continue
        max_count = max(votes.values())
        top = sorted(label for label, count in votes.items() if count == max_count)
        case_level_ood[case_id] = top[0] if len(top) == 1 else "tie"
    case_level_ood_counts = Counter(case_level_ood.values())
    return {
        "status": "judge_dry_run" if dry_run else "judged",
        "dry_run": dry_run,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "route_count": route_count,
        "expected_judge_call_count": route_count,
        "judge_provider": judge_provider,
        "judge_model": judge_model,
        "winner_counts_unblinded": dict(sorted(winner_counts.items())),
        "constructive_edge_counts_unblinded": dict(sorted(constructive_edge_counts.items())),
        "out_of_distribution_counts_unblinded": dict(sorted(ood_counts.items())),
        "out_of_distribution_arm_counts_unblinded": dict(sorted(ood_arm_counts.items())),
        "out_of_distribution_by_arm_source_counts": _nested_counter_to_dict(
            ood_by_arm_source_counts
        ),
        "c_only_ood_source_counts": dict(sorted(c_only_ood_source_counts.items())),
        "c_included_ood_source_counts": dict(sorted(c_included_ood_source_counts.items())),
        "case_level_constructive_edge": case_level_constructive,
        "case_level_constructive_edge_counts": dict(sorted(case_level_counts.items())),
        "case_level_out_of_distribution": case_level_ood,
        "case_level_out_of_distribution_counts": dict(sorted(case_level_ood_counts.items())),
        "case_level_c_ood_count": sum(1 for arm in case_level_ood.values() if arm == "C"),
        "case_level_c_only_ood_count": sum(1 for arm in case_level_ood.values() if arm == "C"),
        "case_level_high_value_c_constructive_edge_count": sum(
            1
            for case_id, arm in case_level_constructive.items()
            if arm == "C" and case_id in case_high_value_c
        ),
        "case_level_high_value_c_ood_count": sum(
            1
            for case_id, arm in case_level_ood.items()
            if arm == "C" and case_id in case_high_value_c_ood
        ),
        "edge_source_counts": dict(sorted(edge_source_counts.items())),
        "high_value_c_constructive_edge_count": high_value_c_wins,
        "high_value_c_ood_count": high_value_c_ood,
        "high_value_c_only_ood_count": high_value_c_ood,
        "high_value_c_included_ood_count": sum(
            count
            for source, count in c_included_ood_source_counts.items()
            if source in HIGH_VALUE_FIELD_SOURCES
        ),
        "regression_vs_a_count": regressions_vs_a,
        "theater_flag_count": theater_count,
        "high_clarity_cost_count": high_clarity_count,
        "c_trace_stats": _c_trace_stats(arm_c_outputs, affordance_index),
        "usage_totals": _usage_totals(judge_records),
    }


def write_judge_outputs(
    *,
    input_dir: Path,
    output_dir: Path,
    affordance_index: dict[str, dict[str, Any]],
    judge_provider: str,
    judge_model: str,
    seed: int,
    dry_run: bool,
) -> dict[str, Any]:
    stems = available_route_stems(input_dir)
    if not stems:
        raise Gate4ExperimentError(f"No Arm A outputs found in {input_dir / 'arm_a'}")

    output_dir.mkdir(parents=True, exist_ok=True)
    judge_records: list[dict[str, Any]] = []
    arm_c_outputs: list[dict[str, Any]] = []
    validation_errors: list[str] = []
    placeholder_count = 0

    for stem in stems:
        outputs = load_arm_outputs(input_dir, stem, dry_run=dry_run)
        placeholder_count += sum(
            1
            for arm in ("B", "C")
            if outputs.get(arm, {}).get("dry_run_placeholder")
        )
        if not outputs["C"].get("dry_run_placeholder"):
            arm_c_outputs.append(outputs["C"])
        validation_errors.extend(
            f"{stem}: {error}"
            for error in validate_arm_inputs(
                input_dir=input_dir,
                stem=stem,
                outputs=outputs,
                affordance_index=affordance_index,
            )
        )
        packet = build_judge_packet(outputs=outputs, seed=seed)
        blind_map = blind_arm_mapping(
            _str(outputs["A"].get("case_id")), _str(outputs["A"].get("route_id")), seed
        )
        packet_with_map = dict(packet)
        packet_with_map["blind_map_for_audit_only"] = blind_map
        _write_json(output_dir / "judge_packets" / f"{stem}.json", packet_with_map)
        if dry_run:
            continue
        judge_payload = run_judge_call(
            judge_provider=judge_provider,
            judge_model=judge_model,
            packet=packet,
            blind_map=blind_map,
        )
        errors = validate_judge_output(judge_payload)
        validation_errors.extend(f"{stem}: judge: {error}" for error in errors)
        _write_json(output_dir / "judge" / f"{stem}.json", judge_payload)
        judge_records.append(judge_payload)

    if validation_errors:
        raise Gate4ExperimentError(
            "Validation errors:\n" + "\n".join(validation_errors[:20])
        )

    summary = summarize_judge_outputs(
        judge_records=judge_records,
        arm_c_outputs=arm_c_outputs,
        affordance_index=affordance_index,
        dry_run=dry_run,
        seed=seed,
        judge_provider=judge_provider,
        judge_model=judge_model,
        route_count=len(stems),
    )
    summary["validation_mode"] = (
        "packet_preflight" if placeholder_count else "output_validation"
    )
    summary["dry_run_placeholder_output_count"] = placeholder_count
    previous_summary_path = input_dir / "summary.json"
    previous = _load_json(previous_summary_path) if previous_summary_path.exists() else {}
    merged = dict(previous)
    merged["judge_summary"] = summary
    _write_json(output_dir / "summary.json", merged)
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--judge-provider", default="openrouter")
    parser.add_argument("--judge-model", default=os.getenv("LOLLA_GATE4_JUDGE_MODEL", ""))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    input_dir = _resolve_repo_path(args.input_dir)
    output_dir = _resolve_repo_path(args.output_dir)
    affordances_path = _resolve_repo_path(args.affordances_path)
    if not args.dry_run and not args.judge_model:
        parser.error("--judge-model is required for non-dry-run judging")
    try:
        affordance_index = load_affordance_index(affordances_path)
        summary = write_judge_outputs(
            input_dir=input_dir,
            output_dir=output_dir,
            affordance_index=affordance_index,
            judge_provider=args.judge_provider,
            judge_model=args.judge_model,
            seed=args.seed,
            dry_run=args.dry_run,
        )
    except Gate4ExperimentError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    mode = "JUDGE DRY RUN" if args.dry_run else "JUDGED"
    print(f"{mode}: {summary['route_count']} routes")
    print(f"Expected judge calls: {summary['expected_judge_call_count']}")
    print(f"Summary: {output_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

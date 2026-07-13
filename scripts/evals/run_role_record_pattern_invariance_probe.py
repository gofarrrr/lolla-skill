#!/usr/bin/env python3
"""Run one frozen six-arm role-record pattern invariance/sensitivity probe."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_pattern_role_record_interpreter import (  # noqa: E402
    build_role_record_pattern_prompts,
    compile_role_record_pattern_response,
    role_record_pattern_response_schema,
)
from engine.system_b.reasoning_pattern_shadow import normalized_projection_signature  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402

CONTRACT_SCHEMA = "lolla.role_record_pattern_invariance_probe_contract.v1"
AUTH_SCHEMA = "lolla.role_record_pattern_invariance_probe_authorization.v1"
REPORT = "research/role-record-pattern-invariance-corpus-2026-07-12/report.json"
TARGET = "docs/evals/role-record-pattern-invariance-target-v1.json"
ARM_ORDER = (
    "registry_source_first", "registry_provider", "registry_reversal_ablation",
    "housing_source_first", "housing_provider", "housing_reversal_ablation",
)
PROTECTED = "missing_reversal_condition"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA or contract.get("status") != "frozen_before_exactly_six_no_retry_calls":
        raise RuntimeError("unexpected or unfrozen role-record pattern contract")
    if contract["budget"] != {
        "maximum_provider_calls": 6, "maximum_estimated_cost_usd": 0.01,
        "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0,
        "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0,
        "pipeline_calls": 0, "runtime_calls": 0,
    }:
        raise RuntimeError("call budget drifted")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    report = _load(ROOT / REPORT)
    if [item["arm_id"] for item in report["artifacts"]] != list(ARM_ORDER):
        raise RuntimeError("arm order drifted")
    schema_sha = sha256_bytes(canonical_json_bytes(role_record_pattern_response_schema()))
    for item in report["artifacts"]:
        packet_path = ROOT / item["packet_path"]
        if _sha(packet_path) != item["packet_sha256"]:
            raise RuntimeError(f"packet drifted: {item['arm_id']}")
        prompts = build_role_record_pattern_prompts(_load(packet_path))
        if item["system_prompt_sha256"] != prompts["system_prompt_sha256"] or item["user_prompt_sha256"] != prompts["user_prompt_sha256"] or item["response_schema_sha256"] != schema_sha:
            raise RuntimeError(f"request contract drifted: {item['arm_id']}")
    if contract["job"]["model"] != "deepseek/deepseek-v4-flash" or contract["job"]["provider_slug"] != "alibaba":
        raise RuntimeError("model route drifted")
    return {"status": "role_record_pattern_invariance_contract_valid", "provider_calls_made": 0, "arm_count": 6, "contract_path": str(contract_path.relative_to(ROOT))}


def validate_authorization(value: dict, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_and_adversarial_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 6, "automatic_retries": 0, "semantic_retries": 0,
        "fallback_models": 0, "evaluator_calls": 0, "embedding_calls": 0,
        "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0,
    }
    if value != expected:
        raise RuntimeError("authorization drifted")


def _nodes(compiled: dict | None) -> set[tuple[str, str, str]]:
    if not compiled:
        return set()
    return {(x["mechanism_id"], x["subject_scope"], x["state"]) for x in compiled["routing_projection"]["pattern_nodes"]}


def _expected(target: dict, arm_id: str) -> set[tuple[str, str, str]]:
    kind = "reversal_ablation" if arm_id.endswith("reversal_ablation") else ("source_first" if arm_id.endswith("source_first") else "provider")
    return {(x["mechanism_id"], x["subject_scope"], x["state"]) for x in target["expected_by_arm_kind"][kind]}


def evaluate(calls: list[dict], target: dict) -> dict:
    by_arm = {item["task_id"]: item for item in calls}
    observed = {arm: _nodes(by_arm[arm].get("compiled")) for arm in ARM_ORDER}
    operational = {arm: by_arm[arm].get("operational_status") == "ok" and by_arm[arm].get("compiled") is not None for arm in ARM_ORDER}
    exact_target = {arm: observed[arm] == _expected(target, arm) for arm in ARM_ORDER}
    cases = {}
    for case in ("registry", "housing"):
        source, provider, ablation = f"{case}_source_first", f"{case}_provider", f"{case}_reversal_ablation"
        cases[case] = {
            "source_provider_projection_invariant": observed[source] == observed[provider],
            "source_provider_signature_invariant": bool(by_arm[source].get("compiled") and by_arm[provider].get("compiled")) and normalized_projection_signature(by_arm[source]["compiled"]) == normalized_projection_signature(by_arm[provider]["compiled"]),
            "protected_mechanism_in_source_and_provider": all(any(node[0] == PROTECTED for node in observed[arm]) for arm in (source, provider)),
            "protected_mechanism_removed_by_ablation": not any(node[0] == PROTECTED for node in observed[ablation]),
            "nonablated_mechanisms_preserved": {node for node in observed[source] if node[0] != PROTECTED} == observed[ablation],
            "source_differs_from_ablation": observed[source] != observed[ablation],
        }
    gates = {
        "all_six_calls_operational_and_compiled": all(operational.values()),
        "all_six_arms_match_prospective_targets": all(exact_target.values()),
        "source_provider_invariance_both_cases": all(value["source_provider_projection_invariant"] and value["source_provider_signature_invariant"] for value in cases.values()),
        "protected_mechanism_preserved_both_cases": all(value["protected_mechanism_in_source_and_provider"] for value in cases.values()),
        "ablation_sensitive_both_cases": all(value["protected_mechanism_removed_by_ablation"] and value["nonablated_mechanisms_preserved"] and value["source_differs_from_ablation"] for value in cases.values()),
    }
    return {"status": "all_frozen_gates_pass" if all(gates.values()) else "one_or_more_frozen_gates_fail", "gates": gates, "operational_by_arm": operational, "prospective_target_match_by_arm": exact_target, "case_comparisons": cases, "observed_nodes_by_arm": {arm: [list(x) for x in sorted(nodes)] for arm, nodes in observed.items()}, "scalar_score": None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output_dir is None:
        raise RuntimeError("execution arguments missing")
    validate_authorization(_load(args.authorization.resolve()), contract, contract_path)
    output = args.output_dir.resolve()
    if not output.is_dir() or (output / "result.json").exists() or list(output.glob("call-*-started.json")):
        raise RuntimeError("output absent, complete, or previously started")
    _load_env(args.env_file.resolve())
    report, target, calls = _load(ROOT / REPORT), _load(ROOT / TARGET), []
    artifacts = {item["arm_id"]: item for item in report["artifacts"]}
    for ordinal, arm_id in enumerate(ARM_ORDER, 1):
        packet = _load(ROOT / artifacts[arm_id]["packet_path"])
        prompts = build_role_record_pattern_prompts(packet)
        _write(output / f"call-{ordinal:02d}-started.json", {"run_id": contract["run_id"], "task_id": arm_id, "packet_sha256": packet["packet_sha256"], "automatic_retries": 0})
        call = run_decomposed_task(
            task_id=arm_id, contract=contract, prompts=prompts,
            schema=role_record_pattern_response_schema(), response_schema_name="lolla_role_record_patterns_v1",
            compile_candidate=lambda candidate, packet=packet, arm_id=arm_id, prompts=prompts: compile_role_record_pattern_response(
                response=candidate, packet=packet, producer_kind="model_operator_eval",
                producer_id=contract["job"]["model"],
                call_metadata={"call_id": arm_id, "model": contract["job"]["model"], "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"]},
            ),
        )
        _write(output / f"call-{ordinal:02d}-result.json", call)
        calls.append(call)
    evaluation = evaluate(calls, target)
    result = {
        "schema_version": "lolla.role_record_pattern_invariance_probe_result.v1",
        "status": "frozen_probe_preserved",
        "run_id": contract["run_id"], "calls": calls, "evaluation": evaluation,
        "provider_request_count": sum(x.get("provider_calls", 0) for x in calls),
        "estimated_cost_usd": round(sum(float(x.get("estimated_cost_usd") or 0) for x in calls), 12),
        "provider_reported_cost_usd": round(sum(float(x.get("provider_reported_cost_usd") or 0) for x in calls), 12),
        "boundary": contract["boundary"],
    }
    _write(output / "result.json", result)
    print(json.dumps({"provider_request_count": result["provider_request_count"], "estimated_cost_usd": result["estimated_cost_usd"], "evaluation": evaluation}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

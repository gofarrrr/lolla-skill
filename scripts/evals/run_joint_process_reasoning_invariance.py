#!/usr/bin/env python3
"""Run the frozen three-fixture joint-process reasoning invariance shadow."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.joint_process_reasoning_shadow import (  # noqa: E402
    JointProcessReasoningShadowError,
    normalized_joint_projection_signature,
    route_joint_projection,
    seal_joint_process_response,
)
from engine.system_b.reasoning_pattern_shadow import (  # noqa: E402
    CONTROLLED_MECHANISMS,
    conversation_turn_numbers,
)


RESULT_SCHEMA = "lolla.joint_process_reasoning_invariance_result.v0"


class JointProcessInvarianceError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise JointProcessInvarianceError(f"expected JSON object: {path}")
    return value


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        raise JointProcessInvarianceError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("status") != "frozen_before_calls":
        raise JointProcessInvarianceError("contract is not frozen_before_calls")
    config = contract.get("call_configuration", {})
    fixtures = contract.get("fixtures", [])
    if not isinstance(fixtures, list) or len(fixtures) != 3:
        raise JointProcessInvarianceError("exactly three fixtures are required")
    if int(config.get("total_generation_calls", 0) or 0) != 3:
        raise JointProcessInvarianceError("exactly three generation calls are required")
    if int(config.get("automatic_retries", -1)) != 0:
        raise JointProcessInvarianceError("automatic retries are forbidden")
    if int(config.get("evaluator_calls", -1)) != 0:
        raise JointProcessInvarianceError("evaluator calls are forbidden")
    if config.get("reasoning_effort") != "none":
        raise JointProcessInvarianceError("reasoning effort must be none")
    seen: set[str] = set()
    for fixture in fixtures:
        fixture_id = str(fixture.get("fixture_id", ""))
        if not fixture_id or fixture_id in seen:
            raise JointProcessInvarianceError("fixture IDs must be non-empty and unique")
        seen.add(fixture_id)
        path = REPO_ROOT / str(fixture.get("path", ""))
        if not path.is_file() or _hash_file(path) != fixture.get("sha256"):
            raise JointProcessInvarianceError(f"fixture hash mismatch: {fixture_id}")
    for ref_name in (
        "target_contract",
        "routing_contract",
        "affordances_artifact",
        "engine_module",
        "runner",
    ):
        ref = contract.get(ref_name, {})
        path = REPO_ROOT / str(ref.get("path", ""))
        if not path.is_file() or _hash_file(path) != ref.get("sha256"):
            raise JointProcessInvarianceError(f"{ref_name} hash mismatch")


def _build_prompts(conversation: str) -> tuple[str, str]:
    mechanisms = "\n".join(f"- {item}" for item in sorted(CONTROLLED_MECHANISMS))
    system_prompt = (
        "You audit the complete joint reasoning trajectory in a conversation. "
        "Do not diagnose an isolated user or assistant turn. For each controlled "
        "mechanism, decide whether the weakness remains unresolved after the full "
        "exchange, appeared but was resolved later, remains genuinely ambiguous, "
        "or was not observed. Surface facts and topic must not determine the "
        "mechanism. Return only the requested JSON object."
    )
    user_prompt = (
        "CONTROLLED MECHANISMS\n\n"
        + mechanisms
        + "\n\nJOINT STATUS DEFINITIONS\n\n"
        "- unresolved: the weakness remains operative after the complete exchange.\n"
        "- resolved_in_conversation: the weakness appeared but later reasoning "
        "materially repaired it.\n"
        "- ambiguous: the complete exchange supports competing readings.\n"
        "- not_observed: the complete exchange does not support the mechanism.\n\n"
        "OUTPUT CONTRACT\n\nReturn exactly {\"mechanisms\": [...]}. Return "
        "every controlled mechanism exactly once. Each row must contain exactly "
        "mechanism_id, joint_status, source_turns, and resolution_turns. Turn arrays "
        "contain conversation turn numbers. unresolved, resolved_in_conversation, "
        "and ambiguous require source_turns. resolved_in_conversation also requires "
        "resolution_turns. unresolved requires empty resolution_turns. not_observed "
        "requires both arrays empty. other_review_required is only for a clearly "
        "supported off-vocabulary unresolved or ambiguous mechanism and never routes "
        "automatically. Do not include rationale, quotes, facts, names, topics, "
        "recommendations, confidence, or free-text labels.\n\n"
        "COMPLETE CONVERSATION\n\n"
        + conversation.strip()
    )
    return system_prompt, user_prompt


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        left, right = raw.find("{"), raw.rfind("}")
        if left < 0 or right <= left:
            return {}
        try:
            value = json.loads(raw[left : right + 1])
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def _call_fixture(
    fixture: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    routing_contract: Mapping[str, Any],
    known_model_ids: set[str],
) -> dict[str, Any]:
    fixture_id = str(fixture["fixture_id"])
    path = REPO_ROOT / str(fixture["path"])
    conversation = path.read_text(encoding="utf-8")
    system_prompt, user_prompt = _build_prompts(conversation)
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY"
    )
    if not api_key:
        raise JointProcessInvarianceError("OPENROUTER_API_KEY is required")
    config = contract["call_configuration"]
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": config["temperature"],
        "max_tokens": config["max_output_tokens"],
        "reasoning": {"effort": config["reasoning_effort"]},
    }
    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=float(config["timeout_seconds"])) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        return {"fixture_id": fixture_id, "status": f"http_error_{exc.code}", "call_count": 1}
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "fixture_id": fixture_id,
            "status": "provider_error",
            "error": type(exc).__name__,
            "call_count": 1,
        }
    choices = payload.get("choices", [])
    raw = str(choices[0].get("message", {}).get("content", "")) if choices else ""
    parsed = _extract_json_object(raw)
    try:
        packet = seal_joint_process_response(
            parsed,
            packet_id=fixture_id,
            source_ref=str(fixture["path"]),
            source_sha256=str(fixture["sha256"]),
            valid_turn_numbers=conversation_turn_numbers(conversation),
        )
        routing = route_joint_projection(
            packet,
            routing_contract=routing_contract,
            known_model_ids=known_model_ids,
        )
        status = "ok"
        validation_error = ""
    except JointProcessReasoningShadowError as exc:
        packet = {}
        routing = {}
        status = "invalid_contract"
        validation_error = str(exc)
    usage = payload.get("usage", {})
    return {
        "fixture_id": fixture_id,
        "status": status,
        "packet": packet,
        "routing": routing,
        "validation_error": validation_error,
        "call_count": 1,
        "automatic_retry_count": 0,
        "metadata": {
            "requested_model": config["model"],
            "served_model": payload.get("model", ""),
            "finish_reason": choices[0].get("finish_reason", "") if choices else "",
            "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
            "total_tokens": int(usage.get("total_tokens", 0) or 0),
            "system_prompt_sha256": _hash_text(system_prompt),
            "user_prompt_sha256": _hash_text(user_prompt),
            "raw_response_sha256": _hash_text(raw),
        },
    }


def _status_by_mechanism(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(item["mechanism_id"]): str(item["joint_status"])
        for item in result.get("packet", {}).get("mechanism_reviews", [])
    }


def _candidate_ids(result: Mapping[str, Any], field: str) -> list[str]:
    return [
        str(item["model_id"])
        for item in result.get("routing", {}).get(field, [])
    ]


def evaluate_comparisons(
    results: Mapping[str, Mapping[str, Any]], contract: Mapping[str, Any]
) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for comparison in contract.get("comparisons", []):
        left_id, right_id = comparison["fixture_ids"]
        left, right = results[left_id], results[right_id]
        valid = left.get("status") == "ok" and right.get("status") == "ok"
        signatures_equal = False
        active_equal = False
        edge_equal = False
        if valid:
            signatures_equal = normalized_joint_projection_signature(
                left["packet"]
            ) == normalized_joint_projection_signature(right["packet"])
            active_equal = _candidate_ids(left, "active_seed_candidates") == _candidate_ids(
                right, "active_seed_candidates"
            )
            edge_equal = _candidate_ids(left, "edge_reserve_candidates") == _candidate_ids(
                right, "edge_reserve_candidates"
            )
        left_status = _status_by_mechanism(left)
        right_status = _status_by_mechanism(right)
        required_left = comparison.get("required_left_statuses", {})
        required_right = comparison.get("required_right_statuses", {})
        checks = {
            "both_outputs_valid": valid,
            "projection_expectation_met": signatures_equal
            == bool(comparison["expect_projection_equal"]),
            "active_candidate_expectation_met": active_equal
            == bool(comparison["expect_active_candidates_equal"]),
            "edge_candidate_expectation_met": edge_equal
            == bool(comparison["expect_edge_candidates_equal"]),
            "required_left_statuses_met": all(
                left_status.get(mechanism) == status
                for mechanism, status in required_left.items()
            ),
            "required_right_statuses_met": all(
                right_status.get(mechanism) == status
                for mechanism, status in required_right.items()
            ),
        }
        reviews.append(
            {
                "comparison_id": comparison["comparison_id"],
                "comparison_type": comparison["comparison_type"],
                "left_fixture_id": left_id,
                "right_fixture_id": right_id,
                "left_statuses": left_status,
                "right_statuses": right_status,
                "projection_signatures_equal": signatures_equal,
                "active_seed_candidates_equal": active_equal,
                "edge_reserve_candidates_equal": edge_equal,
                "checks": checks,
                "status": "passed" if all(checks.values()) else "failed",
            }
        )
    return reviews


def run_shadow(contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    routing_contract = _load_object(REPO_ROOT / contract["routing_contract"]["path"])
    affordances = _load_object(REPO_ROOT / contract["affordances_artifact"]["path"])
    known_model_ids = {
        str(item["model_id"])
        for item in affordances.get("model_records", [])
        if isinstance(item, Mapping) and item.get("model_id")
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        fixture_results = list(
            executor.map(
                lambda fixture: _call_fixture(
                    fixture,
                    contract=contract,
                    routing_contract=routing_contract,
                    known_model_ids=known_model_ids,
                ),
                contract["fixtures"],
            )
        )
    fixture_results.sort(key=lambda item: item["fixture_id"])
    by_id = {item["fixture_id"]: item for item in fixture_results}
    comparisons = evaluate_comparisons(by_id, contract)
    prompt_tokens = sum(item.get("metadata", {}).get("prompt_tokens", 0) for item in fixture_results)
    completion_tokens = sum(
        item.get("metadata", {}).get("completion_tokens", 0) for item in fixture_results
    )
    from engine.system_b.pricing import PRICES_LAST_VERIFIED, estimate_chat_cost_usd, lookup_chat_price

    price = lookup_chat_price("openrouter", contract["call_configuration"]["model"])
    estimated_cost = (
        estimate_chat_cost_usd(
            price=price,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        if price is not None
        else None
    )
    all_calls_ok = all(item["status"] == "ok" for item in fixture_results)
    comparisons_pass = all(item["status"] == "passed" for item in comparisons)
    cost_pass = estimated_cost is not None and estimated_cost <= float(
        contract["call_configuration"]["estimated_cost_ceiling_usd"]
    )
    return {
        "schema_version": RESULT_SCHEMA,
        "status": "passed" if all_calls_ok and comparisons_pass and cost_pass else "failed",
        "contract_sha256": "",
        "fixture_results": fixture_results,
        "comparisons": comparisons,
        "gates": {
            "all_three_calls_valid": all_calls_ok,
            "all_comparisons_pass": comparisons_pass,
            "estimated_cost_ceiling_met": cost_pass,
            "no_retry": all(
                item.get("automatic_retry_count", 0) == 0 for item in fixture_results
            ),
            "runtime_unchanged": True,
        },
        "usage": {
            "call_count": len(fixture_results),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost_usd": estimated_cost,
            "pricing_table_version": PRICES_LAST_VERIFIED,
        },
        "runtime_integration_authorized": False,
        "non_claims": contract["non_claims"],
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = _load_object(args.contract)
    validate_contract(contract)
    if args.dry_run:
        prompts = []
        for fixture in contract["fixtures"]:
            conversation = (REPO_ROOT / fixture["path"]).read_text(encoding="utf-8")
            system_prompt, user_prompt = _build_prompts(conversation)
            prompts.append(
                {
                    "fixture_id": fixture["fixture_id"],
                    "system_prompt_sha256": _hash_text(system_prompt),
                    "user_prompt_sha256": _hash_text(user_prompt),
                }
            )
        print(json.dumps({"status": "dry_run_valid", "call_count": 3, "prompts": prompts}, indent=2))
        return 0
    if args.env_file:
        _load_env_file(args.env_file)
    result = run_shadow(contract)
    result["contract_sha256"] = _hash_file(args.contract)
    for fixture in result["fixture_results"]:
        if fixture.get("packet"):
            _write_json(args.out_dir / f"{fixture['fixture_id']}-packet.json", fixture["packet"])
        if fixture.get("routing"):
            _write_json(args.out_dir / f"{fixture['fixture_id']}-routing.json", fixture["routing"])
    _write_json(args.out_dir / "result.json", result)
    print(json.dumps({"status": result["status"], "gates": result["gates"], "usage": result["usage"]}, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

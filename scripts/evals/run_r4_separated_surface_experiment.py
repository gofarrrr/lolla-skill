#!/usr/bin/env python3
"""Run the frozen R4 task-shape experiment only after exact authorization."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request

from engine.system_b.r4_complementary_readers import canonical_json_bytes
from engine.system_b.r4_semantic_distinction import inspect_r4_reasoning_exclusion_v1


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json"
CONTRACT_SCHEMA = "lolla.r4_separated_surface_experiment_contract.v1"
AUTH_SCHEMA = "lolla.r4_separated_surface_experiment_authorization.v1"


class R4SeparatedSurfaceRunError(RuntimeError):
    """Raised when execution, authorization, or deterministic custody drifts."""


class R4ProviderTransportError(RuntimeError):
    """Carry exact terminal provider bytes through an injected transport."""

    def __init__(
        self,
        message: str,
        *,
        raw_response: bytes | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.raw_response = raw_response
        self.http_status = http_status


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SeparatedSurfaceRunError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_render(value))


def validate_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    if path.resolve() != CONTRACT_PATH.resolve():
        raise R4SeparatedSurfaceRunError("only the frozen default contract is runnable")
    contract = _load(path)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA
        or contract.get("status") != "provider_free_design_frozen_no_authorization"
        or contract.get("run_id") != "lolla-r4-separated-surface-experiment-v1"
    ):
        raise R4SeparatedSurfaceRunError("contract identity drifted")
    if contract.get("current_provider_authorization") != {
        "maximum_calls": 0,
        "maximum_cost_usd": 0.0,
        "authorization_artifact_exists": False,
    }:
        raise R4SeparatedSurfaceRunError("provider authorization boundary drifted")
    operator = contract.get("operator", {})
    if operator != {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-3.1-flash-lite",
        "allowed_served_model_ids": [
            "google/gemini-3.1-flash-lite",
            "google/gemini-3.1-flash-lite-20260507",
        ],
        "provider_slug": "google-vertex",
        "allowed_served_provider_names": ["Google"],
        "provider_order": ["google-vertex"],
        "provider_only": ["google-vertex"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
        "maximum_price_usd_per_million_tokens": {"prompt": 0.25, "completion": 1.5},
        "reasoning": {"effort": "minimal", "exclude": True},
        "stream": False,
        "strict_json_schema": True,
    }:
        raise R4SeparatedSurfaceRunError("operator boundary drifted")
    budget = contract.get("budget", {})
    zero_fields = (
        "automatic_retries",
        "semantic_retries",
        "fallback_models",
        "model_substitutions",
        "relationship_calls",
        "evaluator_calls",
        "embedding_calls",
        "graph_calls",
        "pipeline_calls",
        "runtime_calls",
    )
    if (
        budget.get("maximum_provider_calls") != 12
        or budget.get("response_healing") is not False
        or any(budget.get(field) != 0 for field in zero_fields)
        or not isinstance(budget.get("proposed_hard_provider_reported_cost_total_usd"), (int, float))
        or budget["proposed_hard_provider_reported_cost_total_usd"] > 0.50
    ):
        raise R4SeparatedSurfaceRunError("budget boundary drifted")
    plan = contract.get("call_plan")
    if (
        not isinstance(plan, list)
        or len(plan) != 12
        or [row.get("ordinal") for row in plan] != list(range(1, 13))
        or sum(row.get("arm") == "paired_residual" for row in plan) != 4
        or sum(str(row.get("arm", "")).startswith("separated_") for row in plan) != 8
    ):
        raise R4SeparatedSurfaceRunError("call plan drifted")
    manifest_ref = contract.get("execution_manifest", {})
    manifest_path = ROOT / str(manifest_ref.get("path", ""))
    if not manifest_path.is_file() or _sha(manifest_path) != manifest_ref.get("sha256"):
        raise R4SeparatedSurfaceRunError("execution manifest drifted")
    manifest = _load(manifest_path)
    if (
        manifest.get("protected_target_reference_present") is not False
        or manifest.get("human_review_reference_present") is not False
    ):
        raise R4SeparatedSurfaceRunError("protected evaluation evidence leaked")
    for row in manifest.get("files", []):
        artifact = ROOT / row["path"]
        if not artifact.is_file() or _sha(artifact) != row["sha256"] or len(artifact.read_bytes()) != row["utf8_bytes"]:
            raise R4SeparatedSurfaceRunError(f"execution artifact drifted: {row['path']}")
    runner = contract.get("future_runner", {})
    if runner.get("path") != _relative(Path(__file__)) or runner.get("sha256") != _sha(Path(__file__)):
        raise R4SeparatedSurfaceRunError("runner drifted")
    for row in plan:
        preview = _load(ROOT / row["request_preview_path"])
        if preview.get("body_sha256") != row.get("request_body_sha256"):
            raise R4SeparatedSurfaceRunError("request preview identity drifted")
        if hashlib.sha256(canonical_json_bytes(preview["body"])).hexdigest() != row["request_body_sha256"]:
            raise R4SeparatedSurfaceRunError("request body drifted")
    return contract


def expected_authorization(*, contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_founder_review",
        "contract_path": _relative(CONTRACT_PATH),
        "contract_sha256": _sha(CONTRACT_PATH),
        "run_id": contract["run_id"],
        "authorized_call_plan": [
            {
                "ordinal": row["ordinal"],
                "case_id": row["case_id"],
                "arm": row["arm"],
                "requested_surface": row["requested_surface"],
                "request_body_sha256": row["request_body_sha256"],
            }
            for row in contract["call_plan"]
        ],
        "maximum_provider_calls": 12,
        "hard_provider_reported_cost_per_case_usd": contract["budget"]["proposed_hard_provider_reported_cost_per_case_usd"],
        "hard_provider_reported_cost_total_usd": contract["budget"]["proposed_hard_provider_reported_cost_total_usd"],
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "model_substitutions": 0,
        "response_healing": False,
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }


def validate_authorization(path: Path, *, contract: Mapping[str, Any]) -> None:
    if _load(path.resolve()) != expected_authorization(contract=contract):
        raise R4SeparatedSurfaceRunError("authorization drifted")


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise R4SeparatedSurfaceRunError("environment file does not exist")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _openrouter_transport(*, endpoint: str) -> Callable[[dict[str, Any]], bytes]:
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise R4SeparatedSurfaceRunError("OpenRouter API key is absent")

    def send(body: dict[str, Any]) -> bytes:
        req = request.Request(
            endpoint,
            data=canonical_json_bytes(body),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=180) as response:
                return response.read()
        except error.HTTPError as exc:
            raise R4ProviderTransportError(
                f"HTTP {exc.code}", raw_response=exc.read(), http_status=exc.code
            ) from exc

    return send


def _admit_candidate(candidate: Any, *, preview: Mapping[str, Any]) -> None:
    if not isinstance(candidate, dict) or set(candidate) != {"reviews", "global_limitations"}:
        raise R4SeparatedSurfaceRunError("candidate object shape invalid")
    if not isinstance(candidate["global_limitations"], str):
        raise R4SeparatedSurfaceRunError("global limitations invalid")
    reviews = candidate["reviews"]
    expected = preview["requested_provider_surfaces"]
    if not isinstance(reviews, list) or len(reviews) != len(expected):
        raise R4SeparatedSurfaceRunError("review count invalid")
    aliases = set(preview["source_aliases"])
    seen: list[str] = []
    for review in reviews:
        if not isinstance(review, dict) or set(review) != {"surface", "outcome", "records"}:
            raise R4SeparatedSurfaceRunError("review shape invalid")
        surface = review["surface"]
        if surface not in expected or surface in seen:
            raise R4SeparatedSurfaceRunError("surface invalid")
        seen.append(surface)
        outcome = review["outcome"]
        records = review["records"]
        if outcome not in {"records_present", "no_supported_record_observed", "ambiguous_review"}:
            raise R4SeparatedSurfaceRunError("outcome invalid")
        if not isinstance(records, list) or len(records) > 2:
            raise R4SeparatedSurfaceRunError("record bound invalid")
        supports: list[str] = []
        for record in records:
            if not isinstance(record, dict) or set(record) != {"support", "interpretation", "evidence_ids", "limitations"}:
                raise R4SeparatedSurfaceRunError("record shape invalid")
            if record["support"] not in {"supported", "ambiguous"}:
                raise R4SeparatedSurfaceRunError("support invalid")
            if not isinstance(record["interpretation"], str) or not isinstance(record["limitations"], str):
                raise R4SeparatedSurfaceRunError("record prose invalid")
            evidence = record["evidence_ids"]
            if not isinstance(evidence, list) or not 1 <= len(evidence) <= 8 or any(alias not in aliases for alias in evidence):
                raise R4SeparatedSurfaceRunError("evidence aliases invalid")
            supports.append(record["support"])
        if outcome == "no_supported_record_observed" and records:
            raise R4SeparatedSurfaceRunError("zero outcome contains records")
        if outcome == "records_present" and "supported" not in supports:
            raise R4SeparatedSurfaceRunError("present outcome lacks support")
        if outcome == "ambiguous_review" and (not supports or set(supports) != {"ambiguous"}):
            raise R4SeparatedSurfaceRunError("ambiguous outcome invalid")
    if set(seen) != set(expected):
        raise R4SeparatedSurfaceRunError("required surface missing")


def execute(
    *,
    contract: Mapping[str, Any],
    authorization_path: Path,
    output: Path,
    transport: Callable[[dict[str, Any]], bytes],
) -> dict[str, Any]:
    frozen = validate_contract()
    if dict(contract) != frozen:
        raise R4SeparatedSurfaceRunError("in-memory contract drifted")
    validate_authorization(authorization_path, contract=frozen)
    if output.exists():
        raise R4SeparatedSurfaceRunError("execution output path already exists")
    output.mkdir(parents=True)
    calls = 0
    total_cost = 0.0
    case_costs = {row["case_id"]: 0.0 for row in frozen["cases"]}
    results: list[dict[str, Any]] = []
    for plan in frozen["call_plan"]:
        preview = _load(ROOT / plan["request_preview_path"])
        body = preview["body"]
        request_raw = canonical_json_bytes(body)
        request_sha = hashlib.sha256(request_raw).hexdigest()
        if request_sha != plan["request_body_sha256"]:
            raise R4SeparatedSurfaceRunError("request hash changed")
        _write(output / f"call-{plan['ordinal']:02d}-started.json", {
            "ordinal": plan["ordinal"], "case_id": plan["case_id"], "arm": plan["arm"],
            "request_body_sha256": request_sha, "provider_calls_before": calls,
            "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0,
            "response_healing": False,
        })
        try:
            raw_response = transport(body)
            calls += 1
            if not isinstance(raw_response, bytes):
                raise TypeError("transport must return exact response bytes")
        except Exception as exc:
            if not (isinstance(exc, TypeError) and "exact response bytes" in str(exc)):
                calls += 1
            failure = {
                "ordinal": plan["ordinal"], "case_id": plan["case_id"], "arm": plan["arm"],
                "operational_status": "transport_failure", "provider_calls": 1,
                "request_body_sha256": request_sha, "failure_detail": f"{type(exc).__name__}: {exc}"[:1000],
                "terminal": True,
            }
            terminal = getattr(exc, "raw_response", None)
            if isinstance(terminal, bytes):
                raw_path = output / f"call-{plan['ordinal']:02d}-raw-response.bin"
                raw_path.write_bytes(terminal)
                failure.update({
                    "raw_response_path": raw_path.name,
                    "raw_response_sha256": hashlib.sha256(terminal).hexdigest(),
                    "raw_response_utf8_bytes": len(terminal),
                    "first_terminal_provider_result_preserved_exactly": True,
                })
            if isinstance(getattr(exc, "http_status", None), int):
                failure["http_status"] = exc.http_status
            results.append(failure)
            _write(output / f"call-{plan['ordinal']:02d}-result.json", failure)
            break
        raw_path = output / f"call-{plan['ordinal']:02d}-raw-response.bin"
        raw_path.write_bytes(raw_response)
        base = {
            "ordinal": plan["ordinal"], "case_id": plan["case_id"], "arm": plan["arm"],
            "provider_calls": 1, "request_body_sha256": request_sha,
            "raw_response_path": raw_path.name,
            "raw_response_sha256": hashlib.sha256(raw_response).hexdigest(),
            "raw_response_utf8_bytes": len(raw_response),
            "first_terminal_provider_result_preserved_exactly": True,
        }
        status = "completed"
        detail = ""
        payload: dict[str, Any] = {}
        usage: Mapping[str, Any] = {}
        cost: float | None = None
        generation_id = served_model = served_provider = finish_reason = ""
        reasoning: dict[str, Any] = {"exclusion_satisfied": False, "status": "not_inspected"}
        candidate: Any = None
        try:
            payload = json.loads(raw_response.decode("utf-8"))
            choices = payload["choices"]
            choice = choices[0]
            message = choice["message"]
            served_model = str(payload.get("model", ""))
            served_provider = str(payload.get("provider", ""))
            generation_id = str(payload.get("id", ""))
            finish_reason = str(choice.get("finish_reason", ""))
            if served_model not in frozen["operator"]["allowed_served_model_ids"] or served_provider not in frozen["operator"]["allowed_served_provider_names"] or not generation_id:
                raise R4SeparatedSurfaceRunError("operator attribution failure")
            reasoning = inspect_r4_reasoning_exclusion_v1(message)
            if not reasoning["exclusion_satisfied"]:
                raise R4SeparatedSurfaceRunError("reasoning custody failure")
            if finish_reason != "stop":
                raise R4SeparatedSurfaceRunError("terminal status failure")
            usage = payload["usage"]
            if any(not isinstance(usage.get(field), int) or isinstance(usage.get(field), bool) or usage[field] < 0 for field in ("prompt_tokens", "completion_tokens", "total_tokens")):
                raise R4SeparatedSurfaceRunError("usage custody failure")
            if not isinstance(usage.get("cost"), (int, float)) or isinstance(usage.get("cost"), bool) or usage["cost"] < 0:
                raise R4SeparatedSurfaceRunError("cost custody failure")
            cost = float(usage["cost"])
            candidate = json.loads(message["content"])
            _admit_candidate(candidate, preview=preview)
        except Exception as exc:
            status = "terminal_validation_failure"
            detail = f"{type(exc).__name__}: {exc}"[:1000]
        if cost is not None:
            total_cost = round(total_cost + cost, 12)
            case_costs[plan["case_id"]] = round(case_costs[plan["case_id"]] + cost, 12)
            if total_cost > frozen["budget"]["proposed_hard_provider_reported_cost_total_usd"] or case_costs[plan["case_id"]] > frozen["budget"]["proposed_hard_provider_reported_cost_per_case_usd"]:
                status = "provider_reported_budget_failure"
                detail = "provider-reported hard cost ceiling exceeded"
        row = {
            **base, "operational_status": status, "served_model": served_model,
            "served_provider": served_provider, "generation_id": generation_id,
            "finish_reason": finish_reason, "usage": dict(usage),
            "provider_reported_cost_usd": cost, "reasoning_custody": reasoning,
            "reasoning_values_copied_to_result": False,
            "candidate_sha256": hashlib.sha256(canonical_json_bytes(candidate)).hexdigest() if isinstance(candidate, dict) else None,
            "local_admission_status": "passed" if status == "completed" else "failed",
            "failure_detail": detail, "terminal": True,
        }
        results.append(row)
        _write(output / f"call-{plan['ordinal']:02d}-result.json", row)
        if status != "completed":
            break
    complete = len(results) == 12 and all(row["operational_status"] == "completed" for row in results)
    result = {
        "schema_version": "lolla.r4_separated_surface_execution_result.v1",
        "status": "complete" if complete else "stopped_on_first_failure",
        "run_id": frozen["run_id"], "provider_calls": calls,
        "provider_reported_cost_usd": total_cost, "case_costs_usd": case_costs,
        "call_ordinals": [row["ordinal"] for row in results], "call_results": results,
        "maximum_provider_calls": 12, "automatic_retries": 0, "semantic_retries": 0,
        "fallback_models": 0, "model_substitutions": 0, "response_healing": False,
        "relationship_calls": 0, "evaluator_calls": 0, "embedding_calls": 0,
        "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0,
        "first_failure_stopped_further_transport": not complete,
    }
    _write(output / "result.json", result)
    return result


def dry_run() -> dict[str, Any]:
    validate_contract()
    return {"status": "valid_no_transport", "provider_calls": 0, "provider_cost_usd": 0.0}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    if args.dry_run:
        print(json.dumps(dry_run(), indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.output is None:
        raise R4SeparatedSurfaceRunError("execution requires authorization and output")
    if args.env_file is not None:
        _load_env(args.env_file)
    contract = validate_contract()
    validate_authorization(args.authorization, contract=contract)
    transport = _openrouter_transport(endpoint=contract["operator"]["endpoint"])
    print(json.dumps(execute(contract=contract, authorization_path=args.authorization, output=args.output, transport=transport), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

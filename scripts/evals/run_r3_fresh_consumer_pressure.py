#!/usr/bin/env python3
"""Execute the one frozen R3 Case 01 pressure call with exact custody."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.provider_budget import (  # noqa: E402
    finalize_provider_call,
    reserve_provider_call,
)
from engine.system_b.r3_fresh_consumer import (  # noqa: E402
    MAX_PROVIDER_CALLS,
    MAX_PROVIDER_COST_USD,
    MODEL,
    R3FreshConsumerError,
    compile_pressure_response,
    validate_pressure_bundle,
    value_sha256,
)


CONTRACT_SCHEMA = "lolla.r3_fresh_consumer_pressure_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.r3_fresh_consumer_pressure_authorization.v1"
CALL_RESULT_SCHEMA = "lolla.r3_fresh_consumer_pressure_call_result.v1"


class R3RunError(RuntimeError):
    """Raised before network transport when frozen R3 custody fails."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3RunError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_env_file(path: Path | None) -> None:
    if path is None:
        return
    if not path.is_file():
        raise R3RunError(f"env file missing: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def validate_contract(
    *, contract_path: Path, authorization_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = _load_object(contract_path)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA
        or contract.get("status") != "frozen_before_one_pressure_call"
    ):
        raise R3RunError("R3 pressure contract is not frozen")
    if contract.get("case_id") != "v1-case01-flood-infrastructure":
        raise R3RunError("R3 pressure case identity drifted")
    for item in contract.get("frozen_inputs", []):
        path = ROOT / str(item.get("path", ""))
        if not path.is_file() or _file_sha(path) != item.get("sha256"):
            raise R3RunError(f"frozen input drifted: {item.get('path')}")
    bundle_path = ROOT / contract["bundle"]["path"]
    if _file_sha(bundle_path) != contract["bundle"]["file_sha256"]:
        raise R3RunError("R3 pressure bundle file drifted")
    bundle = _load_object(bundle_path)
    validate_pressure_bundle(bundle)
    if bundle.get("bundle_sha256") != contract["bundle"]["bundle_sha256"]:
        raise R3RunError("R3 pressure bundle identity drifted")
    expected_attestation = {
        "authoritative_conversation_sha256": bundle["packet"][
            "authoritative_conversation_sha256"
        ],
        "constitutional_graph_portfolio_sha256": bundle["hashes"][
            "constitutional_graph_portfolio_sha256"
        ],
        "packet_sha256": bundle["packet"]["packet_sha256"],
        "system_prompt_sha256": bundle["hashes"]["system_prompt_sha256"],
        "user_prompt_sha256": bundle["hashes"]["user_prompt_sha256"],
        "response_schema_sha256": bundle["hashes"]["response_schema_sha256"],
        "request_body_sha256": bundle["hashes"]["request_body_sha256"],
    }
    if contract.get("request_attestation") != expected_attestation:
        raise R3RunError("R3 pressure request attestation drifted")
    budget = contract.get("budget", {})
    if budget != {
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "maximum_estimated_call_cost_usd": bundle["request_contract"][
            "maximum_estimated_call_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }:
        raise R3RunError("R3 pressure budget contract drifted")
    operator = contract.get("operator", {})
    if (
        operator.get("model") != MODEL
        or operator.get("provider_order") != ["google-vertex/global"]
        or operator.get("provider_only") != ["google-vertex"]
        or operator.get("allow_fallbacks") is not False
        or operator.get("data_collection") != "deny"
        or operator.get("wire_mode") != "strict_json_schema"
    ):
        raise R3RunError("R3 pressure operator contract drifted")
    authorization = _load_object(authorization_path)
    expected_authorization = {
        "schema_version": AUTHORIZATION_SCHEMA,
        "status": "authorized_once_by_founder_for_r3_pressure_proof",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _file_sha(contract_path),
        "authorized_case_id": contract["case_id"],
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models_authorized": False,
    }
    if authorization != expected_authorization:
        raise R3RunError("R3 pressure authorization drifted")
    return contract, bundle


def _result_with_hash(value: dict[str, Any]) -> dict[str, Any]:
    value["call_result_sha256"] = value_sha256(value)
    return value


def _exact_json_object(content: str) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise R3FreshConsumerError("provider content is not exact JSON") from exc
    if not isinstance(value, dict):
        raise R3FreshConsumerError("provider content is not a JSON object")
    return value


def run_once(
    *,
    contract: Mapping[str, Any],
    bundle: Mapping[str, Any],
    contract_path: Path,
    authorization_path: Path,
    output: Path,
) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise R3RunError("R3 pressure output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv(
        "OPENROUTER_API_KEY"
    )
    base = {
        "schema_version": CALL_RESULT_SCHEMA,
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _file_sha(contract_path),
        "authorization_path": str(authorization_path.relative_to(ROOT)),
        "authorization_sha256": _file_sha(authorization_path),
        "bundle_sha256": bundle["bundle_sha256"],
        "requested_model": MODEL,
        "request_body_sha256": bundle["hashes"]["request_body_sha256"],
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "provider_calls": 0,
    }
    if not api_key:
        result = _result_with_hash(
            {
                **base,
                "status": "missing_api_key_no_call",
                "provider_attempted": False,
                "source_review_required": False,
                "quiet_control_authorized": False,
            }
        )
        _write(output / "pressure-call-result.json", result)
        return result

    budget_path = output / "provider-budget.json"
    os.environ["LOLLA_PROVIDER_BUDGET_STATE"] = str(budget_path)
    maximum_estimated = float(
        bundle["request_contract"]["maximum_estimated_call_cost_usd"]
    )
    reservation_id, _ = reserve_provider_call(
        run_id=contract["run_id"],
        stage="r3_fresh_consumer_pressure",
        requested_model=MODEL,
        maximum_call_cost_usd=maximum_estimated,
        maximum_calls=MAX_PROVIDER_CALLS,
        maximum_run_cost_usd=MAX_PROVIDER_COST_USD,
    )
    started = {
        **base,
        "status": "started_before_network_transport",
        "provider_attempted": True,
        "provider_calls": 1,
        "budget_reservation_id": reservation_id,
        "started_at_unix": time.time(),
        "request_contract": bundle["request_contract"],
    }
    _write(output / "pressure-call-started.json", started)
    body = bundle["request_body"]
    req = request.Request(
        bundle["request_contract"]["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    monotonic_started = time.monotonic()
    try:
        with request.urlopen(req, timeout=90.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            provider_error: Any = json.loads(raw)
        except json.JSONDecodeError:
            provider_error = {"message": raw[:6000]}
        _write(output / "provider-error.json", {"provider_error": provider_error})
        finalize_provider_call(
            run_id=contract["run_id"],
            reservation_id=reservation_id,
            status=f"http_error_{exc.code}",
            response_id="",
            exact_cost_usd=None,
            estimated_cost_usd=None,
            maximum_calls=MAX_PROVIDER_CALLS,
            maximum_run_cost_usd=MAX_PROVIDER_COST_USD,
        )
        result = _result_with_hash(
            {
                **base,
                "status": f"http_error_{exc.code}_preserved",
                "provider_attempted": True,
                "provider_calls": 1,
                "budget_reservation_id": reservation_id,
                "http_status": exc.code,
                "provider_error_sha256": value_sha256(provider_error),
                "duration_seconds": round(time.monotonic() - monotonic_started, 3),
                "source_review_required": False,
                "quiet_control_authorized": False,
            }
        )
        _write(output / "pressure-call-result.json", result)
        return result
    except Exception as exc:  # noqa: BLE001
        finalize_provider_call(
            run_id=contract["run_id"],
            reservation_id=reservation_id,
            status="transport_error",
            response_id="",
            exact_cost_usd=None,
            estimated_cost_usd=None,
            maximum_calls=MAX_PROVIDER_CALLS,
            maximum_run_cost_usd=MAX_PROVIDER_COST_USD,
        )
        result = _result_with_hash(
            {
                **base,
                "status": "transport_error_preserved",
                "provider_attempted": True,
                "provider_calls": 1,
                "budget_reservation_id": reservation_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:1500],
                "duration_seconds": round(time.monotonic() - monotonic_started, 3),
                "source_review_required": False,
                "quiet_control_authorized": False,
            }
        )
        _write(output / "pressure-call-result.json", result)
        return result

    if not isinstance(payload, Mapping):
        payload = {"invalid_provider_payload": payload}
    _write(output / "provider-payload.json", dict(payload))
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    content = str(message.get("content", ""))
    candidate: dict[str, Any] | None = None
    compiled: dict[str, Any] | None = None
    validation_error = ""
    try:
        candidate = _exact_json_object(content)
        compiled = compile_pressure_response(
            response=candidate,
            packet=bundle["packet"],
        )
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    exact_cost_raw = usage.get("cost")
    try:
        exact_cost = float(exact_cost_raw) if exact_cost_raw is not None else None
    except (TypeError, ValueError):
        exact_cost = None
    response_id = str(payload.get("id", ""))
    estimated_cost = None
    if usage:
        try:
            prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
            completion_tokens = int(usage.get("completion_tokens", 0) or 0)
            estimated_cost = round(
                prompt_tokens * 0.25 / 1_000_000
                + completion_tokens * 1.50 / 1_000_000,
                9,
            )
        except (TypeError, ValueError):
            estimated_cost = None
    finalize_provider_call(
        run_id=contract["run_id"],
        reservation_id=reservation_id,
        status="ok" if compiled is not None else "local_validation_failed",
        response_id=response_id,
        exact_cost_usd=exact_cost,
        estimated_cost_usd=estimated_cost,
        maximum_calls=MAX_PROVIDER_CALLS,
        maximum_run_cost_usd=MAX_PROVIDER_COST_USD,
    )
    exact_cost_present = exact_cost is not None
    exact_cost_within_budget = exact_cost_present and exact_cost <= MAX_PROVIDER_COST_USD
    if compiled is None:
        status = "pressure_response_invalid_preserved"
    elif not exact_cost_present:
        status = "pressure_response_valid_exact_cost_missing"
    elif not exact_cost_within_budget:
        status = "pressure_response_valid_cost_contract_breached"
    else:
        status = "pressure_response_mechanically_valid_source_review_required"
    result = _result_with_hash(
        {
            **base,
            "status": status,
            "provider_attempted": True,
            "provider_calls": 1,
            "budget_reservation_id": reservation_id,
            "served_model": str(payload.get("model", "")),
            "served_provider": str(payload.get("provider", "")),
            "generation_id": response_id,
            "finish_reason": str(choice.get("finish_reason", "")),
            "usage": dict(usage),
            "provider_reported_cost_usd": exact_cost,
            "local_estimated_cost_usd": estimated_cost,
            "exact_cost_present": exact_cost_present,
            "exact_cost_within_budget": exact_cost_within_budget,
            "raw_content": content,
            "raw_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "candidate": candidate,
            "compiled": compiled,
            "validation_error": validation_error,
            "provider_payload_sha256": value_sha256(payload),
            "reasoning_content_returned": bool(
                message.get("reasoning") or message.get("reasoning_details")
            ),
            "duration_seconds": round(time.monotonic() - monotonic_started, 3),
            "source_review_required": compiled is not None,
            "quiet_control_authorized": False,
        }
    )
    _write(output / "pressure-call-result.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-pressure", action="store_true")
    args = parser.parse_args(argv)
    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    contract, bundle = validate_contract(
        contract_path=contract_path,
        authorization_path=authorization_path,
    )
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "frozen_pressure_contract_valid",
                    "provider_calls": 0,
                    "bundle_sha256": bundle["bundle_sha256"],
                    "request_body_sha256": bundle["hashes"]["request_body_sha256"],
                    "maximum_estimated_call_cost_usd": bundle["request_contract"][
                        "maximum_estimated_call_cost_usd"
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not args.execute_pressure:
        raise R3RunError("network execution requires --execute-pressure")
    _load_env_file(args.env_file.resolve() if args.env_file else None)
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=contract_path,
        authorization_path=authorization_path,
        output=args.output.resolve(),
    )
    print(
        json.dumps(
            {
                key: result.get(key)
                for key in (
                    "status",
                    "provider_calls",
                    "served_model",
                    "served_provider",
                    "provider_reported_cost_usd",
                    "validation_error",
                    "call_result_sha256",
                )
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "pressure_response_mechanically_valid_source_review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())

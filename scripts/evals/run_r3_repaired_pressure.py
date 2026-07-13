#!/usr/bin/env python3
"""Execute exactly one frozen repaired R3 pressure attempt."""

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
    value_sha256,
)
from engine.system_b.r3_google_schema_projection import (  # noqa: E402
    R3GoogleProjectionError,
    compile_projected_pressure_response,
)
from scripts.evals.build_r3_google_schema_repair import (  # noqa: E402
    validate_contract as validate_repair_contract,
)


EXECUTION_CONTRACT_SCHEMA = "lolla.r3_repaired_pressure_execution_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.r3_repaired_pressure_authorization.v1"
CALL_RESULT_SCHEMA = "lolla.r3_repaired_pressure_call_result.v1"
PRIVATE_KEYS = frozenset(
    {"user_id", "account_id", "organization_id", "api_key", "authorization"}
)


class R3RepairedRunError(RuntimeError):
    """Raised before transport when repaired R3 custody is invalid."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3RepairedRunError(f"expected JSON object: {path}")
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
        raise R3RepairedRunError(f"env file missing: {path}")
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


def _result_with_hash(value: dict[str, Any]) -> dict[str, Any]:
    value["call_result_sha256"] = value_sha256(value)
    return value


def _exact_json_object(content: str) -> dict[str, Any]:
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise R3GoogleProjectionError("provider content is not exact JSON") from exc
    if not isinstance(value, dict):
        raise R3GoogleProjectionError("provider content is not a JSON object")
    return value


def _redact(
    value: Any,
    *,
    path: tuple[str, ...] = (),
    redactions: list[dict[str, str]],
) -> Any:
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            next_path = (*path, str(key))
            if str(key).lower() in PRIVATE_KEYS:
                result[str(key)] = "[redacted-private-identifier]"
                redactions.append(
                    {
                        "json_pointer": "/" + "/".join(next_path),
                        "reason": "private account or credential field",
                    }
                )
            else:
                result[str(key)] = _redact(
                    item,
                    path=next_path,
                    redactions=redactions,
                )
        return result
    if isinstance(value, list):
        return [
            _redact(item, path=(*path, str(index)), redactions=redactions)
            for index, item in enumerate(value)
        ]
    return value


def validate_execution_contract(
    *, contract_path: Path, authorization_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = _load_object(contract_path)
    if (
        contract.get("schema_version") != EXECUTION_CONTRACT_SCHEMA
        or contract.get("status") != "frozen_before_one_repaired_pressure_call"
    ):
        raise R3RepairedRunError("repaired pressure contract is not frozen")
    if contract.get("case_id") != "v1-case01-flood-infrastructure":
        raise R3RepairedRunError("repaired pressure case drifted")
    for item in contract.get("frozen_inputs", []):
        path = ROOT / str(item.get("path", ""))
        if not path.is_file() or _file_sha(path) != item.get("sha256"):
            raise R3RepairedRunError(f"repaired frozen input drifted: {item.get('path')}")
    repair_contract_path = ROOT / contract["repair_contract"]["path"]
    if _file_sha(repair_contract_path) != contract["repair_contract"]["file_sha256"]:
        raise R3RepairedRunError("provider-free repair contract drifted")
    _, bundle = validate_repair_contract(repair_contract_path)
    if (
        bundle["bundle_sha256"] != contract["bundle"]["bundle_sha256"]
        or _file_sha(ROOT / contract["bundle"]["path"])
        != contract["bundle"]["file_sha256"]
    ):
        raise R3RepairedRunError("repaired pressure bundle drifted")
    expected_attestation = {
        **bundle["hashes"],
        "wire_projection": bundle["request_contract"]["wire_projection"],
    }
    if contract.get("request_attestation") != expected_attestation:
        raise R3RepairedRunError("repaired request attestation drifted")
    if contract.get("budget") != {
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "maximum_estimated_call_cost_usd": bundle["request_contract"][
            "maximum_estimated_call_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }:
        raise R3RepairedRunError("repaired pressure budget drifted")
    operator = contract.get("operator", {})
    if (
        operator.get("model") != MODEL
        or operator.get("provider_order") != ["google-vertex/global"]
        or operator.get("provider_only") != ["google-vertex"]
        or operator.get("allow_fallbacks") is not False
        or operator.get("data_collection") != "deny"
        or operator.get("wire_mode") != "strict_json_schema"
    ):
        raise R3RepairedRunError("repaired pressure operator drifted")
    authorization = _load_object(authorization_path)
    expected_authorization = {
        "schema_version": AUTHORIZATION_SCHEMA,
        "status": "authorized_once_by_founder_for_repaired_r3_pressure",
        "authorization_context": (
            "Founder confirmed the available account balance should be used wisely "
            "after being asked to authorize exactly one repaired pressure attempt."
        ),
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _file_sha(contract_path),
        "authorized_case_id": contract["case_id"],
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models_authorized": False,
        "quiet_control_authorized_now": False,
        "quiet_control_condition": "all_pressure_axes_pass_and_separate_contract_frozen",
    }
    if authorization != expected_authorization:
        raise R3RepairedRunError("repaired pressure authorization drifted")
    return contract, bundle


def _preserve_provider_error(
    *,
    private_output: Path,
    public_output: Path,
    provider_error: Any,
) -> dict[str, Any]:
    exact = {"provider_error": provider_error}
    private_path = private_output / "provider-error.json"
    _write(private_path, exact)
    redactions: list[dict[str, str]] = []
    redacted_value = _redact(exact, redactions=redactions)
    redacted = {
        "schema_version": "lolla.r3_repaired_provider_error_redacted.v1",
        "status": "safe_to_commit_redaction_of_privately_preserved_raw_error",
        "raw_provider_error_file_sha256": _file_sha(private_path),
        "raw_provider_error_value_sha256": value_sha256(provider_error),
        "redactions": redactions,
        "provider_error": redacted_value["provider_error"],
        "raw_error_preserved_outside_git": True,
    }
    redacted["redacted_error_sha256"] = value_sha256(redacted)
    _write(public_output / "provider-error-redacted.json", redacted)
    return redacted


def run_once(
    *,
    contract: Mapping[str, Any],
    bundle: Mapping[str, Any],
    contract_path: Path,
    authorization_path: Path,
    output: Path,
    private_output: Path,
) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise R3RepairedRunError("repaired pressure output directory must be empty")
    if private_output.exists() and any(private_output.iterdir()):
        raise R3RepairedRunError("private repaired pressure output must be empty")
    output.mkdir(parents=True, exist_ok=True)
    private_output.mkdir(parents=True, exist_ok=True)
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
        "quiet_control_authorized": False,
    }
    if not api_key:
        result = _result_with_hash(
            {
                **base,
                "status": "missing_api_key_no_call",
                "provider_attempted": False,
                "source_review_required": False,
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
        stage="r3_repaired_fresh_consumer_pressure",
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
    req = request.Request(
        bundle["request_contract"]["endpoint"],
        data=json.dumps(bundle["request_body"], ensure_ascii=False).encode("utf-8"),
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
        redacted = _preserve_provider_error(
            private_output=private_output,
            public_output=output,
            provider_error=provider_error,
        )
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
                "redacted_error_sha256": redacted["redacted_error_sha256"],
                "duration_seconds": round(time.monotonic() - monotonic_started, 3),
                "source_review_required": False,
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
        compiled = compile_projected_pressure_response(
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
    response_id = str(payload.get("id", ""))
    served_model = str(payload.get("model", ""))
    served_provider = str(payload.get("provider", ""))
    operator_identity_valid = served_model.startswith(
        "google/gemini-3.1-flash-lite"
    ) and served_provider == "Google"
    reasoning_returned = bool(message.get("reasoning") or message.get("reasoning_details"))
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
    mechanical_contract_valid = bool(
        compiled is not None
        and operator_identity_valid
        and not reasoning_returned
        and exact_cost_within_budget
        and response_id
    )
    if compiled is None:
        status = "pressure_response_invalid_preserved"
    elif not operator_identity_valid:
        status = "pressure_response_valid_operator_identity_drifted"
    elif reasoning_returned:
        status = "pressure_response_valid_reasoning_exclusion_breached"
    elif not exact_cost_present:
        status = "pressure_response_valid_exact_cost_missing"
    elif not exact_cost_within_budget:
        status = "pressure_response_valid_cost_contract_breached"
    elif not response_id:
        status = "pressure_response_valid_generation_identity_missing"
    else:
        status = "pressure_response_mechanically_valid_source_review_required"
    result = _result_with_hash(
        {
            **base,
            "status": status,
            "provider_attempted": True,
            "provider_calls": 1,
            "budget_reservation_id": reservation_id,
            "served_model": served_model,
            "served_provider": served_provider,
            "operator_identity_valid": operator_identity_valid,
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
            "reasoning_content_returned": reasoning_returned,
            "mechanical_contract_valid": mechanical_contract_valid,
            "duration_seconds": round(time.monotonic() - monotonic_started, 3),
            "source_review_required": mechanical_contract_valid,
        }
    )
    _write(output / "pressure-call-result.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute-pressure", action="store_true")
    args = parser.parse_args(argv)
    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    contract, bundle = validate_execution_contract(
        contract_path=contract_path,
        authorization_path=authorization_path,
    )
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "repaired_pressure_contract_valid",
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
        raise R3RepairedRunError("network execution requires --execute-pressure")
    _load_env_file(args.env_file.resolve() if args.env_file else None)
    result = run_once(
        contract=contract,
        bundle=bundle,
        contract_path=contract_path,
        authorization_path=authorization_path,
        output=args.output.resolve(),
        private_output=args.private_output.resolve(),
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
    return (
        0
        if result["status"]
        == "pressure_response_mechanically_valid_source_review_required"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())

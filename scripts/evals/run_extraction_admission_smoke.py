#!/usr/bin/env python3
"""Run and seal one frozen, non-holdout extraction-admission smoke."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
for candidate in (str(REPO_ROOT), str(SCRIPTS_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import run_extract as extraction_module  # noqa: E402
from engine.system_b.pricing import PRICES_LAST_VERIFIED  # noqa: E402
from engine.system_b.run_state import is_valid_run_id  # noqa: E402
from engine.system_b.usage_summary import build_usage_summary  # noqa: E402


CONTRACT_SCHEMA = "lolla.extraction_admission_smoke_contract.v1"
RESULT_SCHEMA = "lolla.extraction_admission_smoke_result.v1"


class ExtractionAdmissionSmokeError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExtractionAdmissionSmokeError(f"expected JSON object: {path}")
    return value


def _load_array(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ExtractionAdmissionSmokeError(f"expected JSON object array: {path}")
    return value


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _repo_path(raw_path: object, *, label: str) -> Path:
    relative = Path(str(raw_path))
    if relative.is_absolute():
        raise ExtractionAdmissionSmokeError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / relative).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise ExtractionAdmissionSmokeError(
            f"{label} must remain inside the repository"
        ) from exc
    return resolved


def _prompt_hashes(conversation: str) -> dict[str, str]:
    return {
        "system_prompt_sha256": _hash_text(extraction_module.EXTRACTION_SYSTEM_PROMPT),
        "user_prompt_sha256": _hash_text(
            extraction_module.EXTRACTION_USER_PROMPT.format(
                conversation_text=conversation
            )
        ),
        "retry_system_prompt_sha256": _hash_text(
            extraction_module.EXTRACTION_SYSTEM_PROMPT
        ),
        "retry_template_sha256": _hash_text(
            extraction_module.EXTRACTION_USER_PROMPT_RETRY
        ),
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise ExtractionAdmissionSmokeError("unexpected smoke contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise ExtractionAdmissionSmokeError("smoke contract is not frozen")
    run_id = str(contract.get("run_id", ""))
    if not is_valid_run_id(run_id):
        raise ExtractionAdmissionSmokeError("run_id is invalid")
    fixture = contract.get("fixture", {})
    if fixture.get("permanently_excluded_from_downstream_holdout") is not True:
        raise ExtractionAdmissionSmokeError("smoke fixture must be excluded from holdouts")
    fixture_path = _repo_path(fixture.get("path", ""), label="fixture path")
    if not fixture_path.is_file() or _hash_file(fixture_path) != fixture.get("sha256"):
        raise ExtractionAdmissionSmokeError("fixture hash mismatch")
    conversation = fixture_path.read_text(encoding="utf-8")
    if _prompt_hashes(conversation) != contract.get("prompt_hashes"):
        raise ExtractionAdmissionSmokeError("prompt hashes mismatch")

    config = contract.get("call_configuration", {})
    if config.get("provider") != "openrouter":
        raise ExtractionAdmissionSmokeError("provider must be openrouter")
    if config.get("model") != "google/gemini-3.1-flash-lite":
        raise ExtractionAdmissionSmokeError("smoke model drifted")
    if int(config.get("orchestrator_invocations", 0) or 0) != 1:
        raise ExtractionAdmissionSmokeError("exactly one orchestrator invocation is required")
    if int(config.get("initial_extraction_calls", 0) or 0) != 1:
        raise ExtractionAdmissionSmokeError("exactly one initial extraction call is required")
    if int(config.get("maximum_builtin_quote_repair_calls", -1)) != 1:
        raise ExtractionAdmissionSmokeError("quote repair budget drifted")
    if int(config.get("experiment_retries", -1)) != 0:
        raise ExtractionAdmissionSmokeError("experiment retries are forbidden")
    provider_timeout = float(config.get("provider_timeout_seconds", 0.0) or 0.0)
    wall_timeout = float(config.get("wall_clock_timeout_seconds", 0.0) or 0.0)
    if not 1.0 <= provider_timeout <= 120.0:
        raise ExtractionAdmissionSmokeError(
            "provider timeout must be between 1 and 120 seconds"
        )
    if not provider_timeout < wall_timeout <= 300.0:
        raise ExtractionAdmissionSmokeError(
            "outer wall-clock timeout must exceed provider timeout and be at most 300 seconds"
        )

    hash_locks = contract.get("hash_locks", [])
    if not isinstance(hash_locks, list) or not hash_locks:
        raise ExtractionAdmissionSmokeError("hash_locks must be a non-empty array")
    roles: set[str] = set()
    for index, lock in enumerate(hash_locks):
        if not isinstance(lock, Mapping) or set(lock) != {"role", "path", "sha256"}:
            raise ExtractionAdmissionSmokeError(f"hash_locks[{index}] shape is invalid")
        role = str(lock["role"])
        if role in roles:
            raise ExtractionAdmissionSmokeError("hash lock roles must be unique")
        roles.add(role)
        path = _repo_path(lock["path"], label=f"hash lock path for {role}")
        if not path.is_file() or _hash_file(path) != lock["sha256"]:
            raise ExtractionAdmissionSmokeError(f"hash lock mismatch: {role}")
    required_roles = {
        "extractor",
        "audit_mode",
        "quote_matcher",
        "boundary_provider",
        "capture_adequacy",
        "run_state",
        "usage_summary",
        "pricing",
        "smoke_runner",
    }
    if not required_roles <= roles:
        raise ExtractionAdmissionSmokeError("required transitive hash locks are missing")

    artifacts = contract.get("artifacts", {})
    extraction_path = _repo_path(
        artifacts.get("extraction_path", ""), label="extraction artifact path"
    )
    expected_name = f"lolla_{run_id}_extraction.json"
    if extraction_path.name != expected_name:
        raise ExtractionAdmissionSmokeError("extraction artifact name must carry run_id")
    sidecar_path = Path(str(artifacts.get("extraction_call_sidecar_path", "")))
    if sidecar_path != Path(f"/tmp/lolla_{run_id}_extraction_calls.json"):
        raise ExtractionAdmissionSmokeError("extraction sidecar path is invalid")
    if artifacts.get("require_output_parent_absent_before_run") is not True:
        raise ExtractionAdmissionSmokeError("output-parent absence precondition is required")
    if artifacts.get("require_sidecar_absent_before_run") is not True:
        raise ExtractionAdmissionSmokeError("sidecar absence precondition is required")
    gates = contract.get("admission_gates", {})
    if int(gates.get("minimum_reasoning_passages", 0) or 0) < 1:
        raise ExtractionAdmissionSmokeError("reasoning passage floor must be positive")
    if not isinstance(contract.get("non_claims"), list) or not contract["non_claims"]:
        raise ExtractionAdmissionSmokeError("non_claims must be a non-empty array")


def _safe_usage_summary(run_id: str, call_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary = build_usage_summary(
        run_id=run_id,
        pipeline_boundary_calls=(),
        extraction_boundary_calls=call_records,
    )
    return summary


def _call_attempt_state(
    custody: Mapping[str, Any],
    calls: Sequence[Mapping[str, Any]],
) -> str:
    if calls:
        return "attempted_recorded"
    if custody.get("call_attempted") is True:
        return "attempted_record_missing"
    if custody.get("call_attempted") is False:
        return "not_attempted"
    return "not_observed"


def _mark_openrouter_usage_unknown(
    usage_summary: dict[str, Any],
    *,
    reason: str,
) -> dict[str, Any]:
    """Replace misleading zeroes when an attempted call has no call record."""

    openrouter = usage_summary.setdefault("vendors", {}).setdefault("openrouter", {})
    openrouter.update(
        {
            "calls": None,
            "recorded_calls": 0,
            "prompt_tokens": None,
            "completion_tokens": None,
            "cached_tokens": None,
            "total_tokens": None,
            "cache_hit_rate": None,
            "estimated_cost_usd": None,
            "usage_evidence_state": "unknown_missing_call_record",
            "cost_estimate_coverage": {
                "calls_with_known_price": 0,
                "calls_with_unknown_price": None,
                "unknown_price_models": [],
                "state": "unknown_missing_call_record",
            },
        }
    )
    usage_summary["estimated_total_cost_usd"] = None
    usage_summary["cost_estimate_state"] = "unknown_missing_call_record"
    usage_summary["cost_estimate_coverage"] = {
        "state": "unknown_missing_call_record",
        "calls_with_known_price": 0,
        "calls_with_unknown_price": None,
        "unknown_price_models": [],
    }
    usage_summary.setdefault("notes", []).append(
        f"OpenRouter usage is unknown because {reason}; numeric zero is not observed cost."
    )
    return usage_summary


def _timeout_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def seal_result(
    *,
    contract: Mapping[str, Any],
    contract_path: Path,
    extraction_path: Path,
    sidecar_path: Path,
    extractor_exit_code: int,
    orchestrator_invocation_count: int,
    output_parent_existed_before_run: bool,
    sidecar_existed_before_run: bool,
    stdout_sha256: str,
    stderr_sha256: str,
    wall_time_seconds: float,
    outer_timeout_triggered: bool,
) -> dict[str, Any]:
    validate_contract(contract)
    expected_extraction_path = _repo_path(
        contract["artifacts"]["extraction_path"],
        label="extraction artifact path",
    )
    expected_sidecar_path = Path(
        str(contract["artifacts"]["extraction_call_sidecar_path"])
    )
    if extraction_path != expected_extraction_path:
        raise ExtractionAdmissionSmokeError("extraction path differs from contract")
    if sidecar_path != expected_sidecar_path:
        raise ExtractionAdmissionSmokeError("sidecar path differs from contract")
    extraction = _load_object(extraction_path) if extraction_path.is_file() else {}
    calls = _load_array(sidecar_path) if sidecar_path.is_file() else []
    config = contract["call_configuration"]
    fixture = contract["fixture"]
    quote_validation = extraction.get("extraction", {}).get("_quote_validation", {})
    if not isinstance(quote_validation, Mapping):
        quote_validation = {}
    capture = extraction.get("capture_adequacy", {})
    if not isinstance(capture, Mapping):
        capture = {}
    call_custody = extraction.get("provider_call_custody", {})
    if not isinstance(call_custody, Mapping):
        call_custody = {}
    stages = [str(item.get("stage", "")) for item in calls]
    initial_calls = stages.count("extraction")
    repair_calls = stages.count("extraction_retry")
    usage_summary = _safe_usage_summary(str(contract["run_id"]), calls)
    call_attempt_state = _call_attempt_state(call_custody, calls)
    usage_evidence_state = "recorded" if calls else (
        "not_applicable_no_call"
        if call_attempt_state == "not_attempted"
        else "unknown_missing_call_record"
    )
    if not calls and call_attempt_state != "not_attempted":
        usage_summary = _mark_openrouter_usage_unknown(
            usage_summary,
            reason=(
                "the extraction call was attempted but no record was persisted"
                if call_attempt_state == "attempted_record_missing"
                else "the provider-call attempt state was not observable"
            ),
        )
    openrouter = usage_summary.get("vendors", {}).get("openrouter", {})
    statuses = [str(item.get("status", "")) for item in calls]
    providers = {str(item.get("provider_name", "")) for item in calls}
    requested_models = {str(item.get("requested_model", "")) for item in calls}
    attribution_statuses = {
        str(item.get("model_attribution_status", "")) for item in calls
    }
    model_service_compatible = bool(calls) and all(
        (
            str(item.get("requested_model", "")) == str(config["model"])
            and (
                (
                    str(item.get("model_attribution_status", "")) == "matched"
                    and str(item.get("served_model") or item.get("model") or "")
                    == str(config["model"])
                )
                or (
                    str(item.get("model_attribution_status", ""))
                    == "served_version_alias"
                    and str(item.get("served_model") or item.get("model") or "").startswith(
                        f"{config['model']}-"
                    )
                )
            )
        )
        for item in calls
    )
    prompt_tokens = openrouter.get("prompt_tokens")
    completion_tokens = openrouter.get("completion_tokens")
    reasoning_passages = extraction.get("extraction", {}).get(
        "reasoning_passages", []
    )
    if not isinstance(reasoning_passages, list):
        reasoning_passages = []
    verified_quotes = int(quote_validation.get("verified", 0) or 0)
    failed_quotes = int(quote_validation.get("fabricated", -1))
    total_quotes = int(quote_validation.get("total", 0) or 0)
    call_custody_consistent = bool(call_custody) and (
        call_custody.get("call_attempted") is True
        and call_custody.get("sidecar_persisted") is sidecar_path.is_file()
        and call_custody.get("call_record_persisted") is bool(calls)
        and int(call_custody.get("recorded_call_count", -1)) == len(calls)
    )
    estimated_cost = usage_summary.get("estimated_total_cost_usd")
    complete_cost = usage_summary.get("cost_estimate_state") == "complete"
    gates = {
        "contract_and_transitive_hashes_valid": True,
        "single_orchestrator_invocation": orchestrator_invocation_count
        == int(config["orchestrator_invocations"]),
        "output_parent_absent_before_run": not output_parent_existed_before_run,
        "output_parent_exists_after_run": extraction_path.parent.is_dir(),
        "sidecar_absent_before_run": not sidecar_existed_before_run,
        "outer_timeout_not_triggered": not outer_timeout_triggered,
        "wall_clock_ceiling_met": not outer_timeout_triggered
        and wall_time_seconds <= float(config["wall_clock_timeout_seconds"]),
        "extractor_exit_zero": extractor_exit_code == 0,
        "extraction_artifact_persisted": extraction_path.is_file(),
        "sidecar_persisted": sidecar_path.is_file(),
        "provider_call_attempt_recorded": call_attempt_state == "attempted_recorded",
        "provider_call_custody_consistent": call_custody_consistent,
        "admissible_extraction_declared": call_custody.get(
            "admissible_extraction"
        ) is True,
        "extraction_status_ok": extraction.get("status") == "ok",
        "capture_health_good": extraction.get("capture_health") == "good",
        "capture_adequacy_status_good": capture.get("status") == "good",
        "capture_run_id_exact": capture.get("run_id") == contract["run_id"],
        "complete_capture": int(capture.get("captured_turn_count", 0) or 0)
        == int(fixture["required_captured_message_count"]),
        "capture_not_truncated": int(capture.get("omitted_turn_count", 0) or 0) == 0,
        "quote_validation_present": bool(quote_validation),
        "quote_failures_zero": failed_quotes == 0,
        "quote_counts_consistent": total_quotes == verified_quotes + failed_quotes,
        "all_persisted_passages_verified": verified_quotes == len(reasoning_passages),
        "reasoning_passage_floor_met": len(reasoning_passages)
        >= int(contract["admission_gates"]["minimum_reasoning_passages"]),
        "initial_call_count_exact": initial_calls
        == int(config["initial_extraction_calls"]),
        "repair_call_ceiling_met": repair_calls
        <= int(config["maximum_builtin_quote_repair_calls"]),
        "total_call_ceiling_met": len(calls)
        <= int(config["initial_extraction_calls"])
        + int(config["maximum_builtin_quote_repair_calls"]),
        "all_call_statuses_ok": bool(calls)
        and all(status.startswith("ok") for status in statuses),
        "provider_metadata_exact": providers == {str(config["provider"])},
        "requested_model_exact": requested_models == {str(config["model"])},
        "served_model_compatible": model_service_compatible,
        "model_attribution_acceptable": bool(attribution_statuses)
        and attribution_statuses <= {"matched", "served_version_alias"},
        "token_usage_present": isinstance(prompt_tokens, int)
        and prompt_tokens > 0
        and isinstance(completion_tokens, int)
        and completion_tokens > 0,
        "cost_estimate_complete": complete_cost,
        "cost_ceiling_met": complete_cost
        and isinstance(estimated_cost, (int, float))
        and float(estimated_cost) <= float(config["estimated_cost_ceiling_usd"]),
        "experiment_retry_zero": int(config["experiment_retries"]) == 0,
    }
    failed = [name for name, passed in gates.items() if not passed]
    return {
        "schema_version": RESULT_SCHEMA,
        "status": "passed" if not failed else "failed",
        "smoke_id": contract["smoke_id"],
        "run_id": contract["run_id"],
        "fixture_id": fixture["fixture_id"],
        "contract_sha256": _hash_file(contract_path),
        "extraction_sha256": _hash_file(extraction_path) if extraction_path.is_file() else "",
        "sidecar_sha256": _hash_file(sidecar_path) if sidecar_path.is_file() else "",
        "gates": gates,
        "failed_gates": failed,
        "observed": {
            "extractor_exit_code": extractor_exit_code,
            "orchestrator_invocation_count": orchestrator_invocation_count,
            "initial_extraction_calls": initial_calls,
            "builtin_quote_repair_calls": repair_calls,
            "provider_call_attempt_state": call_attempt_state,
            "provider_call_count": (
                len(calls)
                if calls or call_attempt_state == "not_attempted"
                else None
            ),
            "recorded_provider_call_count": len(calls),
            "usage_evidence_state": usage_evidence_state,
            "admissible_extraction": call_custody.get(
                "admissible_extraction", False
            ),
            "wall_time_seconds": round(float(wall_time_seconds), 3),
            "outer_timeout_triggered": outer_timeout_triggered,
            "capture_health": extraction.get("capture_health", ""),
            "captured_message_count": int(capture.get("captured_turn_count", 0) or 0),
            "omitted_message_count": int(capture.get("omitted_turn_count", 0) or 0),
            "verified_reasoning_passage_count": int(quote_validation.get("verified", 0) or 0),
            "remaining_quote_failure_count": int(quote_validation.get("fabricated", 0) or 0),
            "stdout_sha256": stdout_sha256,
            "stderr_sha256": stderr_sha256,
        },
        "usage_summary": usage_summary,
        "raw_provider_content_included": False,
        "fixture_permanently_excluded_from_downstream_holdout": True,
        "next_holdout_authorized": not failed,
        "runtime_integration_authorized": False,
        "pricing_table_version": PRICES_LAST_VERIFIED,
        "non_claims": contract["non_claims"],
    }


def run_smoke(
    contract: Mapping[str, Any],
    *,
    contract_path: Path,
    env_file: Path,
) -> dict[str, Any]:
    validate_contract(contract)
    artifacts = contract["artifacts"]
    extraction_path = _repo_path(
        artifacts["extraction_path"], label="extraction artifact path"
    )
    sidecar_path = Path(str(artifacts["extraction_call_sidecar_path"]))
    parent_existed = extraction_path.parent.exists()
    sidecar_existed = sidecar_path.exists()
    if parent_existed:
        raise ExtractionAdmissionSmokeError(
            "frozen smoke output parent already exists; refusing artifact reuse"
        )
    if sidecar_existed:
        raise ExtractionAdmissionSmokeError(
            "frozen smoke sidecar already exists; refusing artifact reuse"
        )
    environment = dict(os.environ)
    environment["LOLLA_RUN_ID"] = str(contract["run_id"])
    environment["LOLLA_EXPECTED_RUN_ID"] = str(contract["run_id"])
    environment["LOLLA_OPENROUTER_MODEL"] = str(
        contract["call_configuration"]["model"]
    )
    environment["LOLLA_LLM_TIMEOUT"] = str(
        contract["call_configuration"]["provider_timeout_seconds"]
    )
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts/run_extract.py"),
        "--conversation-file",
        str(_repo_path(contract["fixture"]["path"], label="fixture path")),
        "--env-file",
        str(env_file),
        "--output-file",
        str(extraction_path),
    ]
    started = time.monotonic()
    outer_timeout_triggered = False
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=float(
                contract["call_configuration"]["wall_clock_timeout_seconds"]
            ),
        )
        extractor_exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        outer_timeout_triggered = True
        extractor_exit_code = 124
        stdout = _timeout_text(exc.stdout)
        stderr = _timeout_text(exc.stderr)
        timeout_note = "outer wall-clock timeout terminated extraction"
        stderr = f"{stderr}\n{timeout_note}" if stderr else timeout_note
    wall_time_seconds = time.monotonic() - started
    return seal_result(
        contract=contract,
        contract_path=contract_path,
        extraction_path=extraction_path,
        sidecar_path=sidecar_path,
        extractor_exit_code=extractor_exit_code,
        orchestrator_invocation_count=1,
        output_parent_existed_before_run=parent_existed,
        sidecar_existed_before_run=sidecar_existed,
        stdout_sha256=_hash_text(stdout),
        stderr_sha256=_hash_text(stderr),
        wall_time_seconds=wall_time_seconds,
        outer_timeout_triggered=outer_timeout_triggered,
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract = _load_object(args.contract)
    validate_contract(contract)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "run_id": contract["run_id"],
                    "prompt_hashes": contract["prompt_hashes"],
                    "hash_lock_count": len(contract["hash_locks"]),
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise ExtractionAdmissionSmokeError("--env-file is required for execution")
    result = run_smoke(contract, contract_path=args.contract, env_file=args.env_file)
    _write_json(args.result, result)
    print(json.dumps({"status": result["status"], "gates": result["gates"], "usage": result["usage_summary"]}, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

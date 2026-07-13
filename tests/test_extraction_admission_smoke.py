from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals import run_extraction_admission_smoke as smoke


REQUIRED_ROLES = (
    "extractor",
    "audit_mode",
    "quote_matcher",
    "boundary_provider",
    "capture_adequacy",
    "run_state",
    "usage_summary",
    "pricing",
    "smoke_runner",
)


def _write_text(path: Path, value: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> str:
    return _write_text(path, json.dumps(value))


def _fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    run_id: str,
) -> tuple[dict, Path, Path, Path]:
    monkeypatch.setattr(smoke, "REPO_ROOT", tmp_path)
    conversation = (
        "CONVERSATION: 2 turns, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\nWhat should we do?\n\n"
        "[Turn 2] ASSISTANT:\nWe should compare the options before deciding.\n"
    )
    fixture_path = tmp_path / "fixtures" / "conversation.txt"
    fixture_sha = _write_text(fixture_path, conversation)
    hash_locks = []
    for role in REQUIRED_ROLES:
        path = tmp_path / "locked" / f"{role}.py"
        sha = _write_text(path, f"# frozen {role}\n")
        hash_locks.append(
            {"role": role, "path": str(path.relative_to(tmp_path)), "sha256": sha}
        )
    extraction_relative = (
        Path("research")
        / "smoke"
        / "run"
        / f"lolla_{run_id}_extraction.json"
    )
    sidecar_path = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    sidecar_path.unlink(missing_ok=True)
    contract = {
        "schema_version": smoke.CONTRACT_SCHEMA,
        "status": "frozen_before_calls",
        "smoke_id": f"smoke-{run_id}",
        "run_id": run_id,
        "fixture": {
            "fixture_id": "non-holdout-test-fixture",
            "path": str(fixture_path.relative_to(tmp_path)),
            "sha256": fixture_sha,
            "required_captured_message_count": 2,
            "permanently_excluded_from_downstream_holdout": True,
        },
        "prompt_hashes": smoke._prompt_hashes(conversation),
        "call_configuration": {
            "provider": "openrouter",
            "model": "google/gemini-3.1-flash-lite",
            "orchestrator_invocations": 1,
            "initial_extraction_calls": 1,
            "maximum_builtin_quote_repair_calls": 1,
            "experiment_retries": 0,
            "estimated_cost_ceiling_usd": 0.02,
            "provider_timeout_seconds": 5,
            "wall_clock_timeout_seconds": 10,
        },
        "hash_locks": hash_locks,
        "artifacts": {
            "extraction_path": str(extraction_relative),
            "extraction_call_sidecar_path": str(sidecar_path),
            "require_output_parent_absent_before_run": True,
            "require_sidecar_absent_before_run": True,
        },
        "admission_gates": {"minimum_reasoning_passages": 3},
        "non_claims": ["This smoke does not establish reasoning quality."],
    }
    contract_path = tmp_path / "research" / "smoke" / "contract.json"
    _write_json(contract_path, contract)
    extraction_path = tmp_path / extraction_relative
    return contract, contract_path, extraction_path, sidecar_path


def _persist_success(
    *,
    contract: dict,
    extraction_path: Path,
    sidecar_path: Path,
    fabricated: int = 0,
    served_model: str | None = None,
    attribution_status: str = "matched",
) -> None:
    passages = ["quote one", "quote two", "quote three"]
    served_model = served_model or contract["call_configuration"]["model"]
    _write_json(
        extraction_path,
        {
            "status": "ok",
            "capture_health": "good",
            "capture_adequacy": {
                "status": "good",
                "run_id": contract["run_id"],
                "captured_turn_count": 2,
                "omitted_turn_count": 0,
            },
            "provider_call_custody": {
                "schema_version": "lolla.extraction_call_custody.v0",
                "run_id": contract["run_id"],
                "call_attempted": True,
                "sidecar_persisted": True,
                "call_record_persisted": True,
                "recorded_call_count": 1,
                "admissible_extraction": True,
                "terminal_status": "admissible_extraction",
                "usage_evidence_state": "recorded",
                "sidecar_path": str(sidecar_path),
                "failure_reason": "",
            },
            "extraction": {
                "reasoning_passages": passages,
                "_quote_validation": {
                    "total": len(passages) + fabricated,
                    "verified": len(passages),
                    "fabricated": fabricated,
                    "retry_attempted": fabricated > 0,
                },
            },
        },
    )
    _write_json(
        sidecar_path,
        [
            {
                "stage": "extraction",
                "provider_name": "openrouter",
                "requested_model": contract["call_configuration"]["model"],
                "served_model": served_model,
                "model": served_model,
                "model_attribution_status": attribution_status,
                "status": "ok",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "cached_tokens": 0,
                "raw_message_content": "provider output remains in the local sidecar",
            }
        ],
    )


def _seal(
    *,
    contract: dict,
    contract_path: Path,
    extraction_path: Path,
    sidecar_path: Path,
) -> dict:
    return smoke.seal_result(
        contract=contract,
        contract_path=contract_path,
        extraction_path=extraction_path.resolve(),
        sidecar_path=sidecar_path,
        extractor_exit_code=0,
        orchestrator_invocation_count=1,
        output_parent_existed_before_run=False,
        sidecar_existed_before_run=False,
        stdout_sha256="a" * 64,
        stderr_sha256="b" * 64,
        wall_time_seconds=1.25,
        outer_timeout_triggered=False,
    )


def test_sealer_passes_complete_capture_and_sanitizes_provider_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_pass"
    )
    try:
        _persist_success(
            contract=contract,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
        )
        result = _seal(
            contract=contract,
            contract_path=contract_path,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
        )
        assert result["status"] == "passed"
        assert result["failed_gates"] == []
        assert result["next_holdout_authorized"] is True
        assert result["usage_summary"]["vendors"]["openrouter"]["calls"] == 1
        assert result["usage_summary"]["cost_estimate_state"] == "complete"
        assert "raw_message_content" not in json.dumps(result)
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_sealer_fails_when_quote_custody_reports_a_remaining_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_quote"
    )
    try:
        _persist_success(
            contract=contract,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
            fabricated=1,
        )
        result = _seal(
            contract=contract,
            contract_path=contract_path,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
        )
        assert result["status"] == "failed"
        assert result["gates"]["quote_failures_zero"] is False
        assert result["next_holdout_authorized"] is False
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_sealer_accepts_provider_reported_version_alias_of_frozen_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_model_alias"
    )
    try:
        _persist_success(
            contract=contract,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
            served_model="google/gemini-3.1-flash-lite-20260701",
            attribution_status="served_version_alias",
        )
        result = _seal(
            contract=contract,
            contract_path=contract_path,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
        )
        assert result["status"] == "passed"
        assert result["gates"]["served_model_compatible"] is True
        assert result["gates"]["model_attribution_acceptable"] is True
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_contract_rejects_transitive_hash_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, _contract_path, _extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_hash"
    )
    try:
        locked_path = tmp_path / contract["hash_locks"][0]["path"]
        locked_path.write_text("# drifted\n", encoding="utf-8")
        with pytest.raises(smoke.ExtractionAdmissionSmokeError, match="hash lock mismatch"):
            smoke.validate_contract(contract)
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_sealer_rejects_an_artifact_path_not_named_by_the_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_path"
    )
    try:
        _persist_success(
            contract=contract,
            extraction_path=extraction_path,
            sidecar_path=sidecar_path,
        )
        with pytest.raises(
            smoke.ExtractionAdmissionSmokeError,
            match="extraction path differs from contract",
        ):
            smoke.seal_result(
                contract=contract,
                contract_path=contract_path,
                extraction_path=tmp_path / "wrong.json",
                sidecar_path=sidecar_path,
                extractor_exit_code=0,
                orchestrator_invocation_count=1,
                output_parent_existed_before_run=False,
                sidecar_existed_before_run=False,
                stdout_sha256="a" * 64,
                stderr_sha256="b" * 64,
                wall_time_seconds=1.25,
                outer_timeout_triggered=False,
            )
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_sealer_reports_attempted_call_with_missing_record_as_unknown_not_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_unknown_usage"
    )
    _write_json(
        extraction_path,
        {
            "status": "error",
            "error": "Extraction missing required fields",
            "capture_health": "good",
            "capture_adequacy": {
                "status": "good",
                "run_id": contract["run_id"],
                "captured_turn_count": 2,
                "omitted_turn_count": 0,
            },
            "provider_call_custody": {
                "schema_version": "lolla.extraction_call_custody.v0",
                "run_id": contract["run_id"],
                "call_attempted": True,
                "sidecar_persisted": False,
                "call_record_persisted": False,
                "recorded_call_count": 0,
                "admissible_extraction": False,
                "terminal_status": "missing_required_fields",
                "usage_evidence_state": "missing_after_attempt",
                "sidecar_path": str(sidecar_path),
                "failure_reason": "sidecar_write_failed:OSError",
            },
        },
    )

    result = smoke.seal_result(
        contract=contract,
        contract_path=contract_path,
        extraction_path=extraction_path.resolve(),
        sidecar_path=sidecar_path,
        extractor_exit_code=1,
        orchestrator_invocation_count=1,
        output_parent_existed_before_run=False,
        sidecar_existed_before_run=False,
        stdout_sha256="a" * 64,
        stderr_sha256="b" * 64,
        wall_time_seconds=2.0,
        outer_timeout_triggered=False,
    )

    assert result["status"] == "failed"
    assert result["observed"]["provider_call_attempt_state"] == (
        "attempted_record_missing"
    )
    assert result["observed"]["provider_call_count"] is None
    assert result["observed"]["recorded_provider_call_count"] == 0
    assert result["usage_summary"]["estimated_total_cost_usd"] is None
    assert result["usage_summary"]["cost_estimate_state"] == (
        "unknown_missing_call_record"
    )
    assert result["gates"]["cost_ceiling_met"] is False


def test_contract_rejects_outer_timeout_that_does_not_bound_provider_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, _contract_path, _extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_timeout_contract"
    )
    try:
        contract["call_configuration"]["wall_clock_timeout_seconds"] = 5
        with pytest.raises(
            smoke.ExtractionAdmissionSmokeError,
            match="outer wall-clock timeout",
        ):
            smoke.validate_contract(contract)
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_runner_seals_outer_timeout_without_retry_and_marks_usage_unknown(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, _extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_outer_timeout"
    )
    observed: dict[str, object] = {}

    def _timeout(*_args: object, **kwargs: object) -> None:
        observed.update(kwargs)
        raise smoke.subprocess.TimeoutExpired(
            cmd="run_extract",
            timeout=float(kwargs["timeout"]),
            output=b"partial stdout",
            stderr=b"partial stderr",
        )

    monkeypatch.setattr(smoke.subprocess, "run", _timeout)
    try:
        result = smoke.run_smoke(
            contract,
            contract_path=contract_path,
            env_file=tmp_path / "unused.env",
        )
        assert observed["timeout"] == 10.0
        environment = observed["env"]
        assert isinstance(environment, dict)
        assert environment["LOLLA_LLM_TIMEOUT"] == "5"
        assert result["status"] == "failed"
        assert result["observed"]["outer_timeout_triggered"] is True
        assert result["observed"]["provider_call_attempt_state"] == "not_observed"
        assert result["observed"]["provider_call_count"] is None
        assert result["usage_summary"]["estimated_total_cost_usd"] is None
        assert result["gates"]["outer_timeout_not_triggered"] is False
        assert result["gates"]["wall_clock_ceiling_met"] is False
    finally:
        sidecar_path.unlink(missing_ok=True)


def test_runner_refuses_a_preexisting_output_parent_before_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract, contract_path, extraction_path, sidecar_path = _fixture(
        tmp_path, monkeypatch, run_id="admission_smoke_test_reuse"
    )
    extraction_path.parent.mkdir(parents=True)

    def _unexpected_call(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("subprocess must not run")

    monkeypatch.setattr(smoke.subprocess, "run", _unexpected_call)
    try:
        with pytest.raises(
            smoke.ExtractionAdmissionSmokeError,
            match="output parent already exists",
        ):
            smoke.run_smoke(
                contract,
                contract_path=contract_path,
                env_file=tmp_path / "unused.env",
            )
    finally:
        sidecar_path.unlink(missing_ok=True)

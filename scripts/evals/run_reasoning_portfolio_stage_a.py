#!/usr/bin/env python3
"""Run one frozen fresh-extraction-plus-pipeline Stage A contract exactly once."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
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
from engine.system_b.run_state import is_valid_run_id  # noqa: E402
from engine.system_b.stage_a_execution_contract import (  # noqa: E402
    EXTRACTION_EXIT_ZERO_GATE,
    EXTRACTION_TIMEOUT_CLEAR_GATE,
    PIPELINE_EXIT_ZERO_GATE,
    PIPELINE_TIMEOUT_CLEAR_GATE,
    RUN_DIRECTORY_ABSENT_GATE,
    SIDECARS_ABSENT_GATE,
    validate_stage_a_execution_gates,
)
from scripts.evals.seal_reasoning_portfolio_pipeline_result import (  # noqa: E402
    seal_pipeline_result,
)


CONTRACT_SCHEMA = "lolla.reasoning_portfolio_stage_a_contract.v1"
EXECUTION_SCHEMA = "lolla.reasoning_portfolio_stage_a_execution.v1"
PIPELINE_CALL_ENVELOPE_KIND = "theoretical_custody_envelope"
FIXED_CORE_CALL_SHAPE = {
    "pass1_fixed_calls": 6,
    "companion_fixed_calls": 2,
    "frame_fixed_calls": 2,
    "structural_coverage_maximum_calls": 3,
}


class StageAContractError(RuntimeError):
    pass


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StageAContractError(f"expected JSON object: {path}")
    return value


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _repo_path(raw_path: object, *, label: str) -> Path:
    relative = Path(str(raw_path))
    if relative.is_absolute():
        raise StageAContractError(f"{label} must be repo-relative")
    resolved = (REPO_ROOT / relative).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise StageAContractError(f"{label} must remain inside the repository") from exc
    return resolved


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _prompt_hashes(conversation: str) -> dict[str, str]:
    return {
        "extraction_system_prompt_sha256": _hash_text(
            extraction_module.EXTRACTION_SYSTEM_PROMPT
        ),
        "extraction_user_prompt_sha256": _hash_text(
            extraction_module.EXTRACTION_USER_PROMPT.format(
                conversation_text=conversation
            )
        ),
        "extraction_retry_system_prompt_sha256": _hash_text(
            extraction_module.EXTRACTION_SYSTEM_PROMPT
        ),
        "extraction_retry_template_sha256": _hash_text(
            extraction_module.EXTRACTION_USER_PROMPT_RETRY
        ),
    }


def _env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.is_file():
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            if key:
                values[key] = value
    return values


def _validate_pipeline_call_envelope(
    contract: Mapping[str, Any], *, knowledge_graph_path: Path
) -> None:
    """Reject arbitrary call ceilings that are smaller than the frozen pipeline.

    This is a custody/safety envelope, not a quality target. Activation yield is
    reported separately by the sealer so a noisy pipeline cannot defend itself
    merely by staying beneath its theoretical maximum.
    """
    budget = contract.get("pipeline_call_budget", {})
    if not isinstance(budget, Mapping):
        raise StageAContractError("pipeline call budget is missing")
    derivation = budget.get("derivation", {})
    if not isinstance(derivation, Mapping):
        raise StageAContractError("pipeline call envelope derivation is missing")
    if budget.get("budget_kind") != PIPELINE_CALL_ENVELOPE_KIND:
        raise StageAContractError("pipeline call budget must be a theoretical custody envelope")

    graph = _load_object(knowledge_graph_path)
    tendencies = graph.get("tendencies", {})
    if not isinstance(tendencies, Mapping):
        raise StageAContractError("hash-locked knowledge graph tendencies are invalid")
    tendency_count = len(tendencies)
    if int(derivation.get("hash_locked_tendency_count", -1)) != tendency_count:
        raise StageAContractError("call envelope tendency count differs from knowledge graph")
    for key, expected in FIXED_CORE_CALL_SHAPE.items():
        if int(derivation.get(key, -1)) != expected:
            raise StageAContractError(f"call envelope fixed stage drift: {key}")

    expected_core = sum(FIXED_CORE_CALL_SHAPE.values()) + tendency_count
    if int(budget.get("core_pressure_openrouter_call_ceiling", -1)) != expected_core:
        raise StageAContractError("core pressure ceiling is not pipeline-derived")
    expected_total = (
        int(budget.get("extraction_openrouter_call_ceiling", -1))
        + expected_core
        + int(budget.get("bullshit_index_openrouter_call_ceiling", -1))
    )
    if int(budget.get("total_openrouter_call_ceiling", -1)) != expected_total:
        raise StageAContractError("total OpenRouter ceiling is not pipeline-derived")


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise StageAContractError("unexpected Stage A contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise StageAContractError("Stage A contract is not frozen")
    run_id = str(contract.get("run_id", ""))
    if not is_valid_run_id(run_id):
        raise StageAContractError("run_id is invalid")

    runtime = contract.get("execution_runtime", {})
    if not isinstance(runtime, Mapping):
        raise StageAContractError("execution runtime contract is missing")
    minimum_version = runtime.get("minimum_python_version")
    if (
        not isinstance(minimum_version, list)
        or len(minimum_version) != 2
        or not all(isinstance(item, int) for item in minimum_version)
    ):
        raise StageAContractError("minimum Python version must be [major, minor]")
    if sys.version_info[:2] < tuple(minimum_version):
        raise StageAContractError(
            "active Python is older than the frozen minimum runtime"
        )
    if runtime.get("required_python_version") != platform.python_version():
        raise StageAContractError("active Python version differs from frozen runtime")
    executable = Path(sys.executable).resolve()
    if str(executable) != runtime.get("executable_path"):
        raise StageAContractError("active Python executable differs from frozen runtime")
    if not executable.is_file() or _hash_file(executable) != runtime.get(
        "executable_sha256"
    ):
        raise StageAContractError("active Python executable hash mismatch")

    selection = contract.get("selection", {})
    selection_path = _repo_path(selection.get("path", ""), label="selection path")
    if not selection_path.is_file() or _hash_file(selection_path) != selection.get(
        "sha256"
    ):
        raise StageAContractError("selection artifact hash mismatch")
    selection_payload = _load_object(selection_path)
    selected = selection_payload.get("selection_rule", {}).get("selected_case_id")
    if selected != contract.get("case", {}).get("case_id"):
        raise StageAContractError("contract case differs from frozen selection")

    case = contract.get("case", {})
    source_path = _repo_path(case.get("source_path", ""), label="source path")
    if not source_path.is_file() or _hash_file(source_path) != case.get("source_sha256"):
        raise StageAContractError("source hash mismatch")
    conversation = source_path.read_text(encoding="utf-8")
    capture_preflight = extraction_module._validate_conversation_capture(conversation)
    if capture_preflight.get("capture_health") != "good":
        raise StageAContractError(
            "source capture envelope is not mechanically verifiable as good"
        )
    capture_manifest = capture_preflight.get("capture_manifest", {})
    if not isinstance(capture_manifest, Mapping):
        raise StageAContractError("source capture manifest is invalid")
    observed_messages = int(capture_manifest.get("actual_user_turns", 0) or 0) + int(
        capture_manifest.get("actual_assistant_turns", 0) or 0
    )
    required_messages = int(
        contract.get("fresh_extraction", {}).get("required_captured_message_count", 0)
        or 0
    )
    if observed_messages != required_messages:
        raise StageAContractError(
            "source marker count differs from required captured message count"
        )
    if _prompt_hashes(conversation) != contract.get("prompt_hashes"):
        raise StageAContractError("extraction prompt hashes mismatch")

    extraction = contract.get("fresh_extraction", {})
    pipeline = contract.get("pipeline", {})
    if extraction.get("provider") != "openrouter" or pipeline.get("provider") != "openrouter":
        raise StageAContractError("OpenRouter is the only chat provider in this contract")
    if extraction.get("model") != pipeline.get("model"):
        raise StageAContractError("extraction and pipeline models must match")
    if pipeline.get("embedding_policy") != "on_direct_openai_only":
        raise StageAContractError("Stage A requires the frozen direct-OpenAI embedding policy")
    if pipeline.get("skip_revision") is not True:
        raise StageAContractError("Stage A must skip the user-visible revision call")
    if pipeline.get("pre_step6_portfolio") != "step6_private":
        raise StageAContractError("Stage A requires the private pre-Step-6 table")
    if int(contract.get("experiment_retries", -1)) != 0:
        raise StageAContractError("experiment retries are forbidden")
    if int(extraction.get("maximum_builtin_quote_repair_calls", -1)) != 1:
        raise StageAContractError("exactly one built-in quote repair must be allowed")
    for phase in (extraction, pipeline):
        provider_timeout = float(phase.get("provider_timeout_seconds", 0) or 0)
        wall_timeout = float(phase.get("wall_clock_timeout_seconds", 0) or 0)
        if not 1 <= provider_timeout <= 120:
            raise StageAContractError("provider timeout must be between 1 and 120 seconds")
        if not provider_timeout < wall_timeout <= 900:
            raise StageAContractError(
                "outer wall-clock timeout must exceed provider timeout and be at most 900 seconds"
            )

    locks = contract.get("hash_locks", [])
    if not isinstance(locks, list) or not locks:
        raise StageAContractError("hash_locks must be a non-empty array")
    roles: set[str] = set()
    for index, lock in enumerate(locks):
        if not isinstance(lock, Mapping) or set(lock) != {"role", "path", "sha256"}:
            raise StageAContractError(f"hash_locks[{index}] shape is invalid")
        role = str(lock["role"])
        if role in roles:
            raise StageAContractError("hash lock roles must be unique")
        roles.add(role)
        path = _repo_path(lock["path"], label=f"hash lock path for {role}")
        if not path.is_file() or _hash_file(path) != lock["sha256"]:
            raise StageAContractError(f"hash lock mismatch: {role}")
    required_roles = {
        "selection",
        "source",
        "stage_a_runner",
        "stage_a_execution_contract",
        "extractor",
        "pipeline_runner",
        "pipeline_engine",
        "pipeline_prompts",
        "companion_routing",
        "frame_pressure",
        "structural_coverage",
        "bullshit_index",
        "embedding_retriever",
        "v60_enrichment",
        "affordances_v60",
        "knowledge_graph",
        "relationship_graph",
        "compiled_chunks",
        "reasoning_signals",
        "subpattern_catalog",
        "structural_signal_lexicon",
        "quote_matcher",
        "boundary_provider",
        "capture_adequacy",
        "audit_mode",
        "run_state",
        "usage_summary",
        "pricing",
        "pipeline_sealer",
        "two_stage_protocol",
    }
    if not required_roles <= roles:
        missing = sorted(required_roles - roles)
        raise StageAContractError(f"required transitive hash locks missing: {missing}")

    knowledge_graph_lock = next(
        lock for lock in locks if lock.get("role") == "knowledge_graph"
    )
    _validate_pipeline_call_envelope(
        contract,
        knowledge_graph_path=_repo_path(
            knowledge_graph_lock["path"], label="knowledge graph call-envelope path"
        ),
    )

    artifacts = contract.get("artifacts", {})
    run_dir = _repo_path(artifacts.get("run_dir", ""), label="run directory")
    for label in ("extraction_path", "pipeline_result_path", "execution_result_path"):
        path = _repo_path(artifacts.get(label, ""), label=label)
        if path.parent != run_dir:
            raise StageAContractError(f"{label} must be directly inside run_dir")
    expected_extraction_name = f"lolla_{run_id}_extraction.json"
    extraction_path = _repo_path(artifacts["extraction_path"], label="extraction path")
    if extraction_path.name != expected_extraction_name:
        raise StageAContractError("extraction artifact name must carry run_id")
    expected_sidecars = {
        "extraction_call_sidecar_path": f"/tmp/lolla_{run_id}_extraction_calls.json",
        "private_table_json_sidecar_path": f"/tmp/lolla_{run_id}_pre_step6_private_table.json",
        "private_table_markdown_sidecar_path": f"/tmp/lolla_{run_id}_pre_step6_private_table.md",
        "v60_ledger_sidecar_path": f"/tmp/lolla_{run_id}_v60_ledger_skeleton.json",
    }
    for key, expected in expected_sidecars.items():
        if str(artifacts.get(key, "")) != expected:
            raise StageAContractError(f"invalid sidecar path: {key}")


def _run_command(
    command: list[str],
    *,
    environment: Mapping[str, str],
    timeout_seconds: float,
) -> dict[str, Any]:
    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=dict(environment),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
    return {
        "exit_code": exit_code,
        "timed_out": timed_out,
        "wall_time_seconds": round(time.monotonic() - started, 3),
        "stdout_sha256": _hash_text(stdout),
        "stderr_sha256": _hash_text(stderr),
    }


def _extraction_admission_gates(
    contract: Mapping[str, Any], extraction_path: Path, sidecar_path: Path
) -> dict[str, bool]:
    if not extraction_path.is_file():
        return {"extraction_artifact_persisted": False}
    extraction_result = _load_object(extraction_path)
    extraction = extraction_result.get("extraction", {})
    if not isinstance(extraction, Mapping):
        extraction = {}
    capture = extraction_result.get("capture_adequacy", {})
    if not isinstance(capture, Mapping):
        capture = {}
    quote = extraction.get("_quote_validation", {})
    if not isinstance(quote, Mapping):
        quote = {}
    custody = extraction_result.get("provider_call_custody", {})
    if not isinstance(custody, Mapping):
        custody = {}
    records: list[Mapping[str, Any]] = []
    if sidecar_path.is_file():
        raw = json.loads(sidecar_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            records = [item for item in raw if isinstance(item, Mapping)]
    expected_model = str(contract["fresh_extraction"]["model"])
    model_compatible = bool(records) and all(
        str(item.get("requested_model", "")) == expected_model
        and (
            str(item.get("served_model") or item.get("model") or "") == expected_model
            or str(item.get("served_model") or item.get("model") or "").startswith(
                f"{expected_model}-"
            )
        )
        for item in records
    )
    passages = extraction.get("reasoning_passages", [])
    if not isinstance(passages, list):
        passages = []
    required = contract["fresh_extraction"]
    return {
        "extraction_artifact_persisted": True,
        "extraction_sidecar_persisted": sidecar_path.is_file(),
        "extraction_status_ok": extraction_result.get("status") == "ok",
        "capture_health_good": extraction_result.get("capture_health") == "good",
        "capture_complete": int(capture.get("captured_turn_count", 0) or 0)
        == int(required["required_captured_message_count"]),
        "capture_not_truncated": int(capture.get("omitted_turn_count", 0) or 0) == 0,
        "quote_failures_zero": int(quote.get("fabricated", -1)) == 0,
        "reasoning_passage_floor_met": len(passages)
        >= int(required["minimum_reasoning_passages"]),
        "provider_call_custody_admissible": custody.get("admissible_extraction")
        is True,
        "provider_call_count_consistent": int(custody.get("recorded_call_count", -1))
        == len(records),
        "provider_call_ceiling_met": 1 <= len(records) <= 2,
        "provider_call_statuses_ok": bool(records)
        and all(str(item.get("status", "")).startswith("ok") for item in records),
        "provider_model_compatible": model_compatible,
    }


def _sanitized_call_evidence(
    *,
    contract: Mapping[str, Any],
    pipeline_result_path: Path,
    extraction_sidecar_path: Path,
) -> dict[str, Any]:
    result = _load_object(pipeline_result_path)
    raw_records = json.loads(extraction_sidecar_path.read_text(encoding="utf-8"))
    extraction_records = raw_records if isinstance(raw_records, list) else []
    pipeline_records = result.get("audit_summary", {}).get("boundary_calls", [])
    safe_fields = (
        "stage",
        "tendency_id",
        "provider_name",
        "requested_model",
        "served_model",
        "model",
        "model_attribution_status",
        "status",
        "finish_reason",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cached_tokens",
        "reasoning_disabled",
        "reasoning_details_present",
    )

    def clean(records: object) -> list[dict[str, Any]]:
        if not isinstance(records, list):
            return []
        return [
            {key: item.get(key) for key in safe_fields if key in item}
            for item in records
            if isinstance(item, Mapping)
        ]

    return {
        "schema_version": "lolla.reasoning_portfolio_stage_a_call_evidence.v1",
        "run_id": contract["run_id"],
        "pipeline_result_sha256": _hash_file(pipeline_result_path),
        "extraction_sidecar_sha256": _hash_file(extraction_sidecar_path),
        "extraction_calls": clean(extraction_records),
        "pipeline_core_calls": clean(pipeline_records),
        "usage_summary": result.get("usage_summary", {}),
        "raw_provider_content_included": False,
    }


def run_stage_a(
    contract: Mapping[str, Any], *, contract_path: Path, env_file: Path
) -> dict[str, Any]:
    validate_contract(contract)
    artifacts = contract["artifacts"]
    run_dir = _repo_path(artifacts["run_dir"], label="run directory")
    extraction_path = _repo_path(artifacts["extraction_path"], label="extraction path")
    pipeline_path = _repo_path(
        artifacts["pipeline_result_path"], label="pipeline result path"
    )
    execution_path = _repo_path(
        artifacts["execution_result_path"], label="execution result path"
    )
    extraction_sidecar = Path(artifacts["extraction_call_sidecar_path"])
    all_sidecars = [
        extraction_sidecar,
        Path(artifacts["private_table_json_sidecar_path"]),
        Path(artifacts["private_table_markdown_sidecar_path"]),
        Path(artifacts["v60_ledger_sidecar_path"]),
    ]
    if run_dir.exists():
        raise StageAContractError("frozen Stage A run directory already exists")
    if any(path.exists() for path in all_sidecars):
        raise StageAContractError("one or more frozen Stage A sidecars already exist")

    env_values = _env_values(env_file)
    openrouter_present = bool(os.environ.get("OPENROUTER_API_KEY") or env_values.get("OPENROUTER_API_KEY"))
    openai_present = bool(os.environ.get("OPENAI_API_KEY") or env_values.get("OPENAI_API_KEY"))
    if not openrouter_present:
        raise StageAContractError("OPENROUTER_API_KEY is missing")
    if not openai_present:
        raise StageAContractError(
            "OPENAI_API_KEY is missing but this frozen contract requires embeddings on"
        )

    environment = dict(os.environ)
    environment.update(
        {
            "LOLLA_RUN_ID": str(contract["run_id"]),
            "LOLLA_EXPECTED_RUN_ID": str(contract["run_id"]),
            "LOLLA_OPENROUTER_MODEL": str(contract["pipeline"]["model"]),
            "LOLLA_AUDIT_MODE": str(contract["pipeline"]["audit_mode"]),
            "LOLLA_STAKEHOLDER_CHECK": "0",
            "LOLLA_V60_ENRICHMENT": "on",
            "LOLLA_PRE_STEP6_PORTFOLIO": "step6_private",
            "LOLLA_ACTIVATION_TIEBREAKER": "on",
        }
    )
    environment["LOLLA_LLM_TIMEOUT"] = str(
        contract["fresh_extraction"]["provider_timeout_seconds"]
    )
    extraction_command = [
        sys.executable,
        str(REPO_ROOT / "scripts/run_extract.py"),
        "--conversation-file",
        str(_repo_path(contract["case"]["source_path"], label="source path")),
        "--env-file",
        str(env_file),
        "--output-file",
        str(extraction_path),
    ]
    extraction_execution = _run_command(
        extraction_command,
        environment=environment,
        timeout_seconds=float(
            contract["fresh_extraction"]["wall_clock_timeout_seconds"]
        ),
    )
    extraction_gates = _extraction_admission_gates(
        contract, extraction_path, extraction_sidecar
    )
    extraction_gates[EXTRACTION_EXIT_ZERO_GATE] = extraction_execution["exit_code"] == 0
    extraction_gates[EXTRACTION_TIMEOUT_CLEAR_GATE] = not extraction_execution[
        "timed_out"
    ]

    execution: dict[str, Any] = {
        "schema_version": EXECUTION_SCHEMA,
        "status": "stopped_after_extraction",
        "run_id": contract["run_id"],
        "contract_sha256": _hash_file(contract_path),
        "orchestrator_invocations": 1,
        "credential_presence": {
            "openrouter_present": openrouter_present,
            "direct_openai_present": openai_present,
            "secret_values_included": False,
        },
        "extraction": extraction_execution,
        "pipeline": {"not_run": True},
        "gates": {
            RUN_DIRECTORY_ABSENT_GATE: True,
            SIDECARS_ABSENT_GATE: True,
            **extraction_gates,
            PIPELINE_EXIT_ZERO_GATE: False,
            PIPELINE_TIMEOUT_CLEAR_GATE: False,
        },
        "experiment_retry_count": 0,
    }
    validate_stage_a_execution_gates(execution["gates"])
    if not all(extraction_gates.values()):
        _write_json(execution_path, execution)
        return execution

    environment["LOLLA_LLM_TIMEOUT"] = str(
        contract["pipeline"]["provider_timeout_seconds"]
    )
    pipeline_command = [
        sys.executable,
        str(REPO_ROOT / "scripts/run_pipeline.py"),
        "--extraction-file",
        str(extraction_path),
        "--conversation-file",
        str(_repo_path(contract["case"]["source_path"], label="source path")),
        "--env-file",
        str(env_file),
        "--output",
        "full",
        "--output-file",
        str(pipeline_path),
        "--skip-revision",
        "--embeddings",
        "on",
        "--companion-candidate-cap",
        str(contract["pipeline"]["companion_candidate_cap"]),
        "--v60-enrichment",
        "on",
        "--v60-affordances-path",
        str(
            _repo_path(
                contract["pipeline"]["affordances_path"],
                label="V60 affordances path",
            )
        ),
        "--v60-max-cards",
        str(contract["pipeline"]["v60_max_cards"]),
        "--pre-step6-portfolio",
        "step6_private",
    ]
    pipeline_execution = _run_command(
        pipeline_command,
        environment=environment,
        timeout_seconds=float(contract["pipeline"]["wall_clock_timeout_seconds"]),
    )
    execution["pipeline"] = pipeline_execution
    execution["gates"].update(
        {
            PIPELINE_EXIT_ZERO_GATE: pipeline_execution["exit_code"] == 0,
            PIPELINE_TIMEOUT_CLEAR_GATE: not pipeline_execution["timed_out"],
            "pipeline_artifact_persisted": pipeline_path.is_file(),
        }
    )
    validate_stage_a_execution_gates(execution["gates"])
    execution["status"] = (
        "completed"
        if pipeline_execution["exit_code"] == 0
        and not pipeline_execution["timed_out"]
        and pipeline_path.is_file()
        else "stopped_after_pipeline"
    )
    _write_json(execution_path, execution)
    if execution["status"] != "completed":
        return execution

    gate, table, v60 = seal_pipeline_result(
        contract_path=contract_path,
        pipeline_result_path=pipeline_path,
        repo_root=REPO_ROOT,
        fresh_extraction_result_path=extraction_path,
        execution_result_path=execution_path,
        extraction_call_sidecar_path=extraction_sidecar,
        experiment_retry_count=0,
    )
    out_dir = _repo_path(artifacts["sealed_output_dir"], label="sealed output dir")
    _write_json(out_dir / "pipeline-gate-result.json", gate)
    _write_json(out_dir / "private-table-snapshot.json", table)
    _write_json(out_dir / "v60-snapshot.json", v60)
    _write_json(
        out_dir / "call-evidence.json",
        _sanitized_call_evidence(
            contract=contract,
            pipeline_result_path=pipeline_path,
            extraction_sidecar_path=extraction_sidecar,
        ),
    )
    return gate


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
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
                    "selected_case_id": contract["case"]["case_id"],
                    "hash_lock_count": len(contract["hash_locks"]),
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    if args.env_file is None:
        raise StageAContractError("--env-file is required for execution")
    result = run_stage_a(contract, contract_path=args.contract, env_file=args.env_file)
    print(json.dumps({"status": result.get("status"), "run_id": contract["run_id"]}, indent=2))
    return 0 if result.get("status") in {"passed", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

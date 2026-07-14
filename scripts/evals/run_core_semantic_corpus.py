#!/usr/bin/env python3
"""Run the fixed core-semantic contract across a manifest corpus.

The runner is resumable. Existing valid artifacts are kept unless
``--overwrite`` is supplied. It writes only evaluation artifacts and never
touches graph, routing, live archive, or runtime configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_MANIFEST = (
    REPO_ROOT
    / "tests/fixtures/core_semantic_validation/corpus-v0/manifest.json"
)

EXPECTED_SHADOW_READER_ROLES = [
    "live_constraints",
    "assistant_stances",
    "dropped_threads",
    "question_trajectory",
    "user_pressure",
    "option_evidence",
]
REQUIRED_OUTPUT_KEYS_BY_STAGE = {
    "core_semantic_shadow.live_constraints": {"live_constraints"},
    "core_semantic_shadow.assistant_stances": {"stance_events"},
    "core_semantic_shadow.dropped_threads": {"dropped_threads"},
    "core_semantic_shadow.question_trajectory": {"question_events"},
    "core_semantic_shadow.user_pressure": {"user_pressure_events"},
    "core_semantic_shadow.option_evidence": {
        "option_events",
        "evidence_boundary_events",
    },
}
REQUIRED_RAW_COUNT_KEYS_BY_ROLE = {
    "live_constraints": {"live_constraints"},
    "assistant_stances": {"stance_events"},
    "dropped_threads": {"dropped_threads"},
    "question_trajectory": {"question_events"},
    "user_pressure": {"user_pressure_events"},
    "option_evidence": {
        "option_events",
        "evidence_boundary_events",
    },
}


class EvaluationCallWallTimeout(RuntimeError):
    def __init__(self, *, stage: str, timeout_seconds: float) -> None:
        super().__init__(
            f"evaluation call exceeded {timeout_seconds:.1f}s at {stage}"
        )
        self.stage = stage
        self.timeout_seconds = timeout_seconds
        self.status = "wall_clock_timeout"


class EvaluationBoundaryCallFailure(RuntimeError):
    def __init__(self, *, stage: str, provider_status: str) -> None:
        super().__init__(f"boundary call failed at {stage}: {provider_status}")
        self.stage = stage
        self.provider_status = provider_status
        self.status = "provider_call_failed"


def _load_env(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"env file was not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
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
        if key and key not in os.environ:
            os.environ[key] = value


def _default_env_file() -> Path:
    candidates = [
        REPO_ROOT / ".env",
        Path.home() / ".config/lolla/.env",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _evaluation_call_wall_timeout() -> float:
    raw = os.getenv("LOLLA_EVAL_CALL_WALL_TIMEOUT", "180")
    try:
        value = float(raw)
    except ValueError:
        value = 180.0
    return max(5.0, min(value, 600.0))


def _stage_for_prompt(system_prompt: str) -> str:
    if "LIVE CONSTRAINTS" in system_prompt:
        return "core_semantic_shadow.live_constraints"
    if "STANCE EVENT" in system_prompt:
        return "core_semantic_shadow.assistant_stances"
    if "DROPPED THREADS" in system_prompt:
        return "core_semantic_shadow.dropped_threads"
    if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
        return "core_semantic_shadow.question_trajectory"
    if "USER COUNTER-PRESSURE TEMPORAL SEMANTICS" in system_prompt:
        return "core_semantic_shadow.user_pressure"
    if "USER COUNTER-PRESSURE SEMANTICS" in system_prompt:
        return "core_semantic_shadow.user_pressure"
    if "USER PRESSURE SEMANTICS" in system_prompt:
        return "core_semantic_shadow.user_pressure"
    if "OPTION AND EVIDENCE SEMANTICS" in system_prompt:
        return "core_semantic_shadow.option_evidence"
    return "core_semantic_shadow.unknown"


@contextmanager
def _wall_clock_guard(*, seconds: float, stage: str):
    """Interrupt a slow-drip response in the evaluation process only."""

    supported = (
        seconds > 0
        and hasattr(signal, "setitimer")
        and threading.current_thread() is threading.main_thread()
    )
    if not supported:
        yield
        return

    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)
    started = time.monotonic()

    def on_alarm(_signum: int, _frame: object) -> None:
        raise EvaluationCallWallTimeout(
            stage=stage,
            timeout_seconds=seconds,
        )

    signal.signal(signal.SIGALRM, on_alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
        if old_timer[0] > 0:
            remaining = max(0.001, old_timer[0] - (time.monotonic() - started))
            signal.setitimer(signal.ITIMER_REAL, remaining, old_timer[1])


class _StageBoundary:
    def __init__(self, boundary: object, *, wall_timeout: float | None = None) -> None:
        self.boundary = boundary
        self.wall_timeout = (
            _evaluation_call_wall_timeout()
            if wall_timeout is None
            else wall_timeout
        )

    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        stage = _stage_for_prompt(system_prompt)
        with _wall_clock_guard(seconds=self.wall_timeout, stage=stage):
            result = self.boundary.run_json(  # type: ignore[attr-defined]
                system_prompt,
                user_prompt,
                stage=stage,
            )
        call_log = getattr(self.boundary, "call_log", [])
        status = str(getattr(call_log[-1], "status", "")) if call_log else ""
        if status and status != "ok":
            raise EvaluationBoundaryCallFailure(
                stage=stage,
                provider_status=status,
            )
        missing_keys = REQUIRED_OUTPUT_KEYS_BY_STAGE.get(stage, set()) - set(result)
        if missing_keys:
            raise EvaluationBoundaryCallFailure(
                stage=stage,
                provider_status=(
                    "invalid_output_contract_missing_keys:"
                    + ",".join(sorted(missing_keys))
                ),
            )
        return result


def _safe_call(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key != "raw_message_content"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _artifact_is_valid(path: Path, *, kind: str) -> bool:
    if not path.is_file():
        return False
    try:
        payload = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    if kind == "compact":
        return payload.get("status") == "ok" and isinstance(payload.get("extraction"), dict)
    calls = [
        call
        for call in payload.get("semantic_candidate_ledger", {}).get(
            "reader_calls", []
        )
        if isinstance(call, dict)
    ]
    roles = [call.get("reader_role") for call in calls]
    reader_contracts_complete = all(
        REQUIRED_RAW_COUNT_KEYS_BY_ROLE.get(str(call.get("reader_role")), set())
        <= set(call.get("raw_candidate_counts", {}))
        for call in calls
    )
    return (
        payload.get("schema_version") == "lolla.core_semantic_shadow.v0"
        and roles == EXPECTED_SHADOW_READER_ROLES
        and reader_contracts_complete
    )


def _preserve_failed_artifact(path: Path) -> Path | None:
    if not path.is_file():
        return None
    index = 1
    while True:
        candidate = path.with_name(f"{path.stem}-attempt-{index:02d}.error.json")
        if not candidate.exists():
            path.replace(candidate)
            return candidate
        index += 1


def _run_compact(
    *,
    case_id: str,
    repeat: int,
    conversation_path: Path,
    output_path: Path,
    env_file: Path,
    max_attempts: int = 3,
) -> None:
    run_id = f"coresem_{case_id.replace('-', '_')}_r{repeat:02d}"
    child_env = dict(os.environ)
    child_env.update(
        {
            "LOLLA_RUN_ID": run_id,
            "LOLLA_EXPECTED_RUN_ID": run_id,
            "LOLLA_AUDIT_MODE": child_env.get("LOLLA_AUDIT_MODE", "standard"),
        }
    )
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts/run_extract.py"),
        "--conversation-file",
        str(conversation_path),
        "--env-file",
        str(env_file),
        "--output-file",
        str(output_path),
    ]
    prior_failure_count = len(list(output_path.parent.glob(f"{output_path.stem}-attempt-*.error.json")))
    if output_path.exists() and not _artifact_is_valid(output_path, kind="compact"):
        _preserve_failed_artifact(output_path)
        prior_failure_count += 1

    completed: subprocess.CompletedProcess[str] | None = None
    invocation_failures = 0
    for _attempt in range(1, max_attempts + 1):
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=child_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode == 0 and _artifact_is_valid(output_path, kind="compact"):
            break
        invocation_failures += 1
        _preserve_failed_artifact(output_path)
    else:
        assert completed is not None
        raise RuntimeError(
            f"compact extraction failed for {case_id} repeat {repeat} after "
            f"{max_attempts} attempts:\n{completed.stdout[-4000:]}"
        )

    sidecar = Path(f"/tmp/lolla_{run_id}_extraction_calls.json")
    if sidecar.is_file():
        payload = _load_json(output_path)
        calls = json.loads(sidecar.read_text(encoding="utf-8"))
        payload["model_usage"] = {
            "calls": [_safe_call(item) for item in calls if isinstance(item, dict)]
        }
        output_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        sidecar.unlink(missing_ok=True)
    payload = _load_json(output_path)
    payload["evaluation_execution"] = {
        "failed_attempts_before_success": prior_failure_count + invocation_failures,
        "bounded_retry_limit": max_attempts,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _run_shadow(
    *,
    conversation_path: Path,
    context_extraction_path: Path,
    output_path: Path,
    boundary: _StageBoundary,
) -> None:
    from engine.system_b.conversation_loader import load_conversation_context
    from engine.system_b.core_semantic_shadow import (
        build_core_semantic_shadow,
        render_core_semantic_shadow_json,
    )

    context = load_conversation_context(context_extraction_path, conversation_path)
    call_log = boundary.boundary.call_log  # type: ignore[attr-defined]
    start = len(call_log)
    payload = build_core_semantic_shadow(context=context, boundary=boundary)
    payload["model_usage"] = {
        "calls": [_safe_call(record.to_dict()) for record in call_log[start:]]
    }
    output_path.write_text(render_core_semantic_shadow_json(payload), encoding="utf-8")


def _next_shadow_error_path(output_path: Path) -> Path:
    index = 1
    while True:
        candidate = output_path.with_name(
            f"{output_path.stem}-attempt-{index:02d}.error.json"
        )
        if not candidate.exists():
            return candidate
        index += 1


def _write_shadow_attempt_error(
    *,
    output_path: Path,
    case_id: str,
    repeat: int,
    attempt: int,
    failure: EvaluationCallWallTimeout | EvaluationBoundaryCallFailure,
    completed_calls: list[object],
    elapsed_seconds: float,
) -> Path:
    path = _next_shadow_error_path(output_path)
    payload = {
        "schema_version": "lolla.core_semantic_shadow_attempt_error.v0",
        "case_id": case_id,
        "repeat": repeat,
        "attempt": attempt,
        "status": failure.status,
        "failed_stage": failure.stage,
        "provider_status": getattr(failure, "provider_status", "not_recorded"),
        "wall_timeout_seconds": getattr(failure, "timeout_seconds", None),
        "elapsed_seconds": elapsed_seconds,
        "in_flight_call_recorded": False
        if isinstance(failure, EvaluationCallWallTimeout)
        else True,
        "completed_calls_before_failure": [
            _safe_call(call.to_dict())
            for call in completed_calls
            if hasattr(call, "to_dict")
        ],
        "contains_prompt_text": False,
        "contains_provider_message_text": False,
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _run_shadow_with_retries(
    *,
    case_id: str,
    repeat: int,
    conversation_path: Path,
    context_extraction_path: Path,
    output_path: Path,
    boundary: _StageBoundary,
    max_attempts: int = 3,
) -> None:
    call_log = boundary.boundary.call_log  # type: ignore[attr-defined]
    prior_failures = len(
        list(output_path.parent.glob(f"{output_path.stem}-attempt-*.error.json"))
    )
    invocation_failures = 0
    for attempt in range(1, max_attempts + 1):
        start = len(call_log)
        started = time.monotonic()
        try:
            _run_shadow(
                conversation_path=conversation_path,
                context_extraction_path=context_extraction_path,
                output_path=output_path,
                boundary=boundary,
            )
        except (EvaluationCallWallTimeout, EvaluationBoundaryCallFailure) as failure:
            invocation_failures += 1
            if output_path.exists():
                _preserve_failed_artifact(output_path)
            _write_shadow_attempt_error(
                output_path=output_path,
                case_id=case_id,
                repeat=repeat,
                attempt=attempt,
                failure=failure,
                completed_calls=call_log[start:],
                elapsed_seconds=time.monotonic() - started,
            )
            continue
        if not _artifact_is_valid(output_path, kind="shadow"):
            raise RuntimeError(
                f"shadow extraction produced an invalid artifact for "
                f"{case_id} repeat {repeat}"
            )
        payload = _load_json(output_path)
        payload["evaluation_execution"] = {
            "failed_attempts_before_success": prior_failures + invocation_failures,
            "bounded_retry_limit": max_attempts,
            "per_call_wall_timeout_seconds": boundary.wall_timeout,
        }
        output_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return
    raise RuntimeError(
        f"shadow extraction failed for {case_id} repeat {repeat} after "
        f"{max_attempts} attempts"
    )


def _write_case_manifest(
    *,
    case: dict[str, Any],
    case_dir: Path,
    compact_paths: list[Path],
    shadow_paths: list[Path],
    comparison_json: Path,
) -> None:
    artifacts = [
        {"path": path.name, "sha256": _sha256(path), "path_kind": "live_compact_extraction"}
        for path in compact_paths
    ]
    artifacts.extend(
        {"path": path.name, "sha256": _sha256(path), "path_kind": "decision_work_aligned_shadow"}
        for path in shadow_paths
    )
    payload = {
        "schema_version": "lolla.core_semantic_case_run_manifest.v0",
        "case_id": case["case_id"],
        "source_conversation_sha256": case["source_file_sha256"],
        "provider_status": "all_calls_ok",
        "graph_runtime_modified": False,
        "artifacts": artifacts,
        "comparison": {
            "path": comparison_json.name,
            "sha256": _sha256(comparison_json),
        },
    }
    (case_dir / "manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    from engine.system_b.boundary_provider import load_boundary_client_from_env
    from engine.system_b.core_semantic_comparison import (
        build_core_semantic_comparison,
        render_core_semantic_comparison_json,
        render_core_semantic_comparison_markdown,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=_default_env_file())
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--skip-compact", action="store_true")
    parser.add_argument("--skip-shadow", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--real-boundary-approved", action="store_true")
    args = parser.parse_args()

    if not args.real_boundary_approved:
        print("error: real boundary approval flag is required", file=sys.stderr)
        return 2
    manifest_path = args.manifest.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    env_file = args.env_file.expanduser().resolve()
    manifest = _load_json(manifest_path)
    repeats = args.repeats or int(
        manifest["repeat_contract"]["compact_runs_per_case"]
    )
    if repeats < 2:
        print("error: corpus repeatability evaluation requires at least two repeats", file=sys.stderr)
        return 2
    selected = set(args.case_ids or [])
    cases = [
        case for case in manifest["cases"]
        if not selected or case["case_id"] in selected
    ]
    unknown = selected - {case["case_id"] for case in cases}
    if unknown:
        print(f"error: unknown case ids: {sorted(unknown)}", file=sys.stderr)
        return 2

    _load_env(env_file)
    boundary = _StageBoundary(load_boundary_client_from_env(args.provider))
    output_dir.mkdir(parents=True, exist_ok=True)

    for case in cases:
        case_id = case["case_id"]
        source = REPO_ROOT / case["source_path"]
        context_extraction = REPO_ROOT / case["context_extraction_path"]
        gold = REPO_ROOT / case["gold_path"]
        if _sha256(source) != case["source_file_sha256"]:
            raise ValueError(f"source hash mismatch: {case_id}")
        case_dir = output_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        compact_paths = [case_dir / f"compact-{index:02d}.json" for index in range(1, repeats + 1)]
        shadow_paths = [case_dir / f"shadow-{index:02d}.json" for index in range(1, repeats + 1)]

        print(f"[{case_id}] compact path", flush=True)
        if not args.skip_compact:
            for index, path in enumerate(compact_paths, 1):
                if not args.overwrite and _artifact_is_valid(path, kind="compact"):
                    print(f"  compact {index}/{repeats}: reuse", flush=True)
                    continue
                print(f"  compact {index}/{repeats}: run", flush=True)
                _run_compact(
                    case_id=case_id,
                    repeat=index,
                    conversation_path=source,
                    output_path=path,
                    env_file=env_file,
                )

        print(f"[{case_id}] shadow path", flush=True)
        if not args.skip_shadow:
            for index, path in enumerate(shadow_paths, 1):
                if not args.overwrite and _artifact_is_valid(path, kind="shadow"):
                    print(f"  shadow {index}/{repeats}: reuse", flush=True)
                    continue
                print(f"  shadow {index}/{repeats}: run", flush=True)
                _run_shadow_with_retries(
                    case_id=case_id,
                    repeat=index,
                    conversation_path=source,
                    context_extraction_path=context_extraction,
                    output_path=path,
                    boundary=boundary,
                )

        missing = [
            path for path, kind in (
                *[(path, "compact") for path in compact_paths],
                *[(path, "shadow") for path in shadow_paths],
            )
            if not _artifact_is_valid(path, kind=kind)
        ]
        if missing:
            raise RuntimeError(f"case incomplete after run: {case_id}: {missing}")

        comparison = build_core_semantic_comparison(
            compact_paths=compact_paths,
            shadow_paths=shadow_paths,
            conversation_path=source,
            gold_path=gold,
        )
        comparison_json = case_dir / "comparison.json"
        comparison_md = case_dir / "comparison.md"
        comparison_json.write_text(
            render_core_semantic_comparison_json(comparison), encoding="utf-8"
        )
        comparison_md.write_text(
            render_core_semantic_comparison_markdown(comparison), encoding="utf-8"
        )
        _write_case_manifest(
            case=case,
            case_dir=case_dir,
            compact_paths=compact_paths,
            shadow_paths=shadow_paths,
            comparison_json=comparison_json,
        )
        print(f"[{case_id}] complete", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

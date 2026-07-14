#!/usr/bin/env python3
"""Prepare or run the locked one-case user counter-pressure preflight.

Without ``--real-boundary-approved`` this command only writes the contract and
makes no provider call. The paid mode performs one focused reader call per
repeat and never runs or rewrites the other semantic readers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


CASE_ID = "case-08-oncologist-career-family"
REPEATS = 3
MAX_ATTEMPTS = 3
DEFAULT_MANIFEST = (
    REPO_ROOT / "tests/fixtures/core_semantic_validation/corpus-v0/manifest.json"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "research/core-semantic-sk4-counterpressure-v2-preflight-2026-07-10"
)
CONTRACT_SCHEMA_VERSION = "lolla.user_counterpressure_preflight_contract.v0"
RESULT_SCHEMA_VERSION = "lolla.user_counterpressure_preflight_result.v0"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _case_from_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    for item in manifest.get("cases", []):
        if isinstance(item, dict) and item.get("case_id") == CASE_ID:
            return item
    raise ValueError(f"locked preflight case was not found: {CASE_ID}")


def build_contract(
    *,
    manifest_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    from engine.system_b.core_semantic_shadow import (
        USER_COUNTERPRESSURE_KINDS,
        USER_COUNTERPRESSURE_SYSTEM_PROMPT,
    )

    manifest = _load_json(manifest_path)
    case = _case_from_manifest(manifest)
    source = REPO_ROOT / str(case["source_path"])
    gold = REPO_ROOT / str(case["gold_path"])
    context = REPO_ROOT / str(case["context_extraction_path"])
    if _sha256_path(source) != case["source_file_sha256"]:
        raise ValueError("locked source hash does not match the corpus manifest")

    baseline_dir = (
        REPO_ROOT
        / "research/core-semantic-sk3-repair-2026-07-10"
        / CASE_ID
    )
    baseline_artifacts = [
        baseline_dir / f"shadow-{index:02d}.json"
        for index in range(1, REPEATS + 1)
    ]
    missing_baseline = [str(path) for path in baseline_artifacts if not path.is_file()]
    if missing_baseline:
        raise ValueError(f"locked SK3 control artifacts are missing: {missing_baseline}")

    gold_payload = _load_json(gold)
    pressure_gold = [
        observation
        for observation in gold_payload.get("required_observations", [])
        if isinstance(observation, dict)
        and observation.get("dimension") == "user_corrections_and_pressure"
    ]

    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "contract_status": "prepared_no_calls_executed",
        "case_id": CASE_ID,
        "repeat_count": REPEATS,
        "successful_call_budget": REPEATS,
        "bounded_retry_limit_per_repeat": MAX_ATTEMPTS,
        "source": {
            "conversation_path": str(source.relative_to(REPO_ROOT)),
            "conversation_sha256": _sha256_path(source),
            "context_extraction_path": str(context.relative_to(REPO_ROOT)),
            "gold_path": str(gold.relative_to(REPO_ROOT)),
            "gold_sha256": _sha256_path(gold),
        },
        "probabilistic_job": {
            "reader_role": "user_pressure",
            "reader_calls_per_repeat": 1,
            "output_key": "user_pressure_events",
            "allowed_kinds": sorted(USER_COUNTERPRESSURE_KINDS),
            "system_prompt_sha256": _sha256_text(
                USER_COUNTERPRESSURE_SYSTEM_PROMPT
            ),
            "target_definition": (
                "user statements that materially correct a premise or frame, "
                "qualify evidence or feasibility, or object to the reasoning"
            ),
        },
        "deterministic_job": {
            "checks": [
                "required output key",
                "allowed kind",
                "user source turn",
                "exact contiguous source quote",
                "eight-item cap",
                "candidate custody",
                "exact duplicate identity",
            ],
            "must_not_infer_semantic_role": True,
        },
        "control": {
            "baseline": "five-reader SK3 repair",
            "baseline_artifacts": [
                str(path.relative_to(REPO_ROOT)) for path in baseline_artifacts
            ],
            "baseline_artifact_sha256": {
                path.name: _sha256_path(path) for path in baseline_artifacts
            },
            "rerun_other_readers": False,
            "modify_baseline_artifacts": False,
            "families_held_constant": [
                "live_constraints",
                "assistant_stances",
                "dropped_threads",
                "question_trajectory",
                "options",
                "evidence_boundaries",
            ],
        },
        "locked_gold_pressure_observations": pressure_gold,
        "gate": {
            "required_gold_pressure_recall": 1.0,
            "required_stable_gold_pressure_observation_count": len(pressure_gold),
            "required_exact_source_validity": 1.0,
            "required_reader_calls_per_artifact": 1,
            "forbidden_returned_kinds": [
                "concern",
                "correction",
                "evidence_request",
                "timing_pressure",
                "value",
            ],
            "pass_authorizes": "three-case pressure-only ablation",
            "pass_does_not_authorize": [
                "SK4 promotion",
                "full corpus",
                "SK5",
                "graph integration",
                "live integration",
            ],
        },
        "output": {
            "directory": str(output_dir),
            "artifact_pattern": "counterpressure-01.json through counterpressure-03.json",
        },
        "non_claims": [
            "contract_preparation_is_not_semantic_quality_evidence",
            "repeatability_is_not_correctness",
            "exact_source_validity_is_not_reasoning_quality",
        ],
    }


def _artifact_is_valid(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        payload = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    calls = payload.get("semantic_candidate_ledger", {}).get("reader_calls", [])
    events = payload.get("semantic_events", {})
    model_calls = payload.get("model_usage", {}).get("calls", [])
    return (
        payload.get("schema_version") == "lolla.user_counterpressure_shadow.v0"
        and isinstance(calls, list)
        and len(calls) == 1
        and isinstance(calls[0], dict)
        and calls[0].get("reader_role") == "user_pressure"
        and set(calls[0].get("raw_candidate_counts", {}))
        == {"user_pressure_events"}
        and isinstance(events, dict)
        and isinstance(events.get("user_pressure_events"), list)
        and all(
            not items
            for family, items in events.items()
            if family != "user_pressure_events"
        )
        and isinstance(model_calls, list)
        and len(model_calls) == 1
        and isinstance(model_calls[0], dict)
        and model_calls[0].get("status") == "ok"
    )


def _safe_call(record: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in record.items()
        if key != "raw_message_content"
    }


def _run_paid_repeats(
    *,
    case: Mapping[str, Any],
    output_dir: Path,
    env_file: Path,
    provider_name: str,
) -> list[Path]:
    from engine.system_b.boundary_provider import load_boundary_client_from_env
    from engine.system_b.conversation_loader import load_conversation_context
    from engine.system_b.core_semantic_shadow import (
        build_user_counterpressure_shadow,
        render_core_semantic_shadow_json,
    )
    from scripts.evals.run_core_semantic_corpus import (
        EvaluationBoundaryCallFailure,
        EvaluationCallWallTimeout,
        _StageBoundary,
        _load_env,
        _write_shadow_attempt_error,
    )

    _load_env(env_file)
    boundary = _StageBoundary(load_boundary_client_from_env(provider_name))
    source = REPO_ROOT / str(case["source_path"])
    context = load_conversation_context(
        REPO_ROOT / str(case["context_extraction_path"]),
        source,
    )
    outputs: list[Path] = []
    for repeat in range(1, REPEATS + 1):
        output = output_dir / f"counterpressure-{repeat:02d}.json"
        outputs.append(output)
        if _artifact_is_valid(output):
            print(f"counterpressure {repeat}/{REPEATS}: reuse", flush=True)
            continue
        print(f"counterpressure {repeat}/{REPEATS}: run", flush=True)
        prior_failures = len(
            list(output_dir.glob(f"{output.stem}-attempt-*.error.json"))
        )
        for attempt in range(1, MAX_ATTEMPTS + 1):
            call_log = boundary.boundary.call_log  # type: ignore[attr-defined]
            start = len(call_log)
            started = time.monotonic()
            try:
                payload = build_user_counterpressure_shadow(
                    context=context,
                    boundary=boundary,
                )
            except (
                EvaluationCallWallTimeout,
                EvaluationBoundaryCallFailure,
            ) as failure:
                _write_shadow_attempt_error(
                    output_path=output,
                    case_id=CASE_ID,
                    repeat=repeat,
                    attempt=attempt,
                    failure=failure,
                    completed_calls=call_log[start:],
                    elapsed_seconds=time.monotonic() - started,
                )
                continue
            payload["model_usage"] = {
                "calls": [
                    _safe_call(record.to_dict()) for record in call_log[start:]
                ]
            }
            payload["evaluation_execution"] = {
                "failed_attempts_before_success": prior_failures + attempt - 1,
                "bounded_retry_limit": MAX_ATTEMPTS,
                "per_call_wall_timeout_seconds": boundary.wall_timeout,
            }
            output.write_text(
                render_core_semantic_shadow_json(payload),
                encoding="utf-8",
            )
            if not _artifact_is_valid(output):
                raise RuntimeError(f"invalid counter-pressure artifact: {output}")
            break
        else:
            raise RuntimeError(
                f"counter-pressure repeat {repeat} failed after {MAX_ATTEMPTS} attempts"
            )
    return outputs


def _source_event_matches(event: Mapping[str, Any], evidence: Mapping[str, Any]) -> bool:
    from engine.system_b.core_semantic_comparison import _quotes_overlap

    source = event.get("source") if isinstance(event.get("source"), Mapping) else {}
    return (
        int(source.get("turn_index") or 0) == int(evidence.get("turn_index") or -1)
        and str(source.get("speaker") or "") == str(evidence.get("speaker") or "")
        and _quotes_overlap(
            str(source.get("quote") or ""),
            str(evidence.get("quote") or ""),
        )
    )


def build_result(
    *,
    contract: Mapping[str, Any],
    artifact_paths: list[Path],
) -> dict[str, Any]:
    required = contract.get("locked_gold_pressure_observations", [])
    runs = [_load_json(path) for path in artifact_paths]
    per_run: list[dict[str, Any]] = []
    recovered_sets: list[set[str]] = []
    selected_count = 0
    raw_count = 0
    valid_count = 0
    forbidden_kinds: set[str] = set()
    allowed = set(contract["probabilistic_job"]["allowed_kinds"])
    for run in runs:
        events = run.get("semantic_events", {}).get("user_pressure_events", [])
        selected_count += len(events)
        validation = run["validation"]["user_counterpressure"][
            "user_pressure_events"
        ]
        raw_count += int(validation["raw_count"])
        valid_count += int(validation["validated_count"])
        candidates = run.get("semantic_candidate_ledger", {}).get(
            "candidates", []
        )
        forbidden_kinds.update(
            str(candidate.get("raw_proposal", {}).get("kind") or "")
            for candidate in candidates
            if isinstance(candidate, Mapping)
            and isinstance(candidate.get("raw_proposal"), Mapping)
            and str(candidate["raw_proposal"].get("kind") or "") not in allowed
        )
        recovered: set[str] = set()
        for observation in required:
            if any(
                _source_event_matches(event, evidence)
                for event in events
                for evidence in observation.get("evidence", [])
            ):
                recovered.add(str(observation.get("observation_id") or ""))
        recovered_sets.append(recovered)
        per_run.append(
            {
                "recovered_observation_ids": sorted(recovered),
                "recall": len(recovered) / len(required) if required else 0.0,
                "selected_candidate_count": len(events),
            }
        )
    stable = set.intersection(*recovered_sets) if recovered_sets else set()
    mean_recall = (
        sum(item["recall"] for item in per_run) / len(per_run) if per_run else 0.0
    )
    exact_validity = valid_count / raw_count if raw_count else 0.0
    gate = {
        "gold_pressure_recall": mean_recall
        >= float(contract["gate"]["required_gold_pressure_recall"]),
        "stable_gold_pressure": len(stable)
        >= int(contract["gate"]["required_stable_gold_pressure_observation_count"]),
        "exact_source_validity": exact_validity
        >= float(contract["gate"]["required_exact_source_validity"]),
        "one_reader_call_per_artifact": all(
            len(run.get("semantic_candidate_ledger", {}).get("reader_calls", [])) == 1
            for run in runs
        ),
        "no_forbidden_returned_kinds": not forbidden_kinds,
    }
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "case_id": CASE_ID,
        "artifact_paths": [str(path) for path in artifact_paths],
        "per_run": per_run,
        "mean_gold_pressure_recall": mean_recall,
        "stable_gold_pressure_observation_ids": sorted(stable),
        "raw_candidate_count": raw_count,
        "validated_candidate_count": valid_count,
        "selected_candidate_count": selected_count,
        "exact_source_validity": exact_validity,
        "forbidden_returned_kinds": sorted(forbidden_kinds),
        "gate": gate,
        "passed": all(gate.values()),
        "pass_authorizes": contract["gate"]["pass_authorizes"],
        "pass_does_not_authorize": contract["gate"]["pass_does_not_authorize"],
    }


def _render_result_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# User Counter-Pressure One-Case Preflight",
        "",
        f"Case: `{result['case_id']}`",
        "",
        f"Decision: **{'pass' if result['passed'] else 'fail'}**",
        "",
        f"- Mean locked pressure recall: {result['mean_gold_pressure_recall']:.3f}",
        f"- Stable locked pressure observations: {len(result['stable_gold_pressure_observation_ids'])}",
        f"- Exact-source validity: {result['exact_source_validity']:.3f}",
        f"- Selected candidates: {result['selected_candidate_count']}",
        "",
        "## Gate",
        "",
    ]
    lines.extend(
        f"- {name}: {'pass' if passed else 'fail'}"
        for name, passed in result["gate"].items()
    )
    lines.extend(
        [
            "",
            "A pass authorizes only the three-case pressure-only ablation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--real-boundary-approved", action="store_true")
    args = parser.parse_args()

    manifest_path = args.manifest.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    contract = build_contract(
        manifest_path=manifest_path,
        output_dir=output_dir,
    )
    contract_path = output_dir / "preflight-contract.json"
    contract_path.write_text(
        json.dumps(contract, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not args.real_boundary_approved:
        print(f"Preflight contract written to {contract_path}")
        print("No model calls executed.")
        return 0

    from scripts.evals.run_core_semantic_corpus import _default_env_file

    manifest = _load_json(manifest_path)
    case = _case_from_manifest(manifest)
    artifacts = _run_paid_repeats(
        case=case,
        output_dir=output_dir,
        env_file=(args.env_file or _default_env_file()).expanduser().resolve(),
        provider_name=args.provider,
    )
    result = build_result(contract=contract, artifact_paths=artifacts)
    (output_dir / "preflight-result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "preflight-result.md").write_text(
        _render_result_markdown(result),
        encoding="utf-8",
    )
    print(f"Preflight {'passed' if result['passed'] else 'failed'}.")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

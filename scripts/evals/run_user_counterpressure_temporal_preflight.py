#!/usr/bin/env python3
"""Run the locked three-call v2.1 temporal counter-pressure preflight."""
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


OUTPUT_DIR = (
    REPO_ROOT
    / "research/core-semantic-sk4-counterpressure-v21-temporal-preflight-2026-07-10"
)
CONTRACT_PATH = OUTPUT_DIR / "preflight-contract.json"
CASE_ID = "case-08-oncologist-career-family"
REPEATS = 3
MAX_ATTEMPTS = 3
RESULT_SCHEMA_VERSION = "lolla.user_counterpressure_temporal_preflight_result.v0"
MANIFEST_PATH = (
    REPO_ROOT / "tests/fixtures/core_semantic_validation/corpus-v0/manifest.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _case() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    for item in manifest["cases"]:
        if item.get("case_id") == CASE_ID:
            return item
    raise ValueError(f"missing locked case: {CASE_ID}")


def validate_contract(contract_path: Path = CONTRACT_PATH) -> dict[str, Any]:
    from engine.system_b.core_semantic_shadow import (
        USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT,
    )

    contract = _load_json(contract_path)
    if contract.get("case_id") != CASE_ID:
        raise ValueError("temporal preflight case drifted")
    if int(contract.get("repeat_count") or 0) != REPEATS:
        raise ValueError("temporal repeat contract drifted")
    prompt = contract["prompt_contract"]
    if prompt["v21_temporal_prompt_sha256"] != _sha256_text(
        USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    ):
        raise ValueError("temporal system prompt hash drifted")
    if prompt["v21_temporal_prompt_character_count"] != len(
        USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    ):
        raise ValueError("temporal system prompt length drifted")
    source = REPO_ROOT / contract["source"]["conversation_path"]
    if contract["source"]["conversation_sha256"] != _sha256_path(source):
        raise ValueError("temporal source hash drifted")
    scoring = contract["temporal_scoring_contract"]
    if scoring["sha256"] != _sha256_path(REPO_ROOT / scoring["path"]):
        raise ValueError("temporal scoring contract hash drifted")
    for name, expected in contract["control"]["baseline_artifact_sha256"].items():
        path = (
            REPO_ROOT
            / "research/core-semantic-sk3-repair-2026-07-10"
            / CASE_ID
            / name
        )
        if expected != _sha256_path(path):
            raise ValueError(f"baseline artifact hash drifted: {name}")
    return contract


def _artifact_is_valid(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        payload = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    reader_calls = payload.get("semantic_candidate_ledger", {}).get(
        "reader_calls", []
    )
    model_calls = payload.get("model_usage", {}).get("calls", [])
    events = payload.get("semantic_events", {})
    return (
        payload.get("schema_version")
        == "lolla.user_counterpressure_temporal_shadow.v0"
        and isinstance(reader_calls, list)
        and len(reader_calls) == 1
        and isinstance(reader_calls[0], dict)
        and reader_calls[0].get("reader_role") == "user_pressure"
        and set(reader_calls[0].get("raw_candidate_counts", {}))
        == {"user_pressure_events"}
        and isinstance(model_calls, list)
        and len(model_calls) == 1
        and isinstance(model_calls[0], dict)
        and model_calls[0].get("status") == "ok"
        and isinstance(events, dict)
        and isinstance(events.get("user_pressure_events"), list)
        and all(
            not items
            for family, items in events.items()
            if family != "user_pressure_events"
        )
    )


def _safe_call(record: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in record.items()
        if key != "raw_message_content"
    }


def run_paid_repeats(
    *,
    output_dir: Path,
    env_file: Path,
    provider_name: str,
) -> list[Path]:
    from engine.system_b.boundary_provider import load_boundary_client_from_env
    from engine.system_b.conversation_loader import load_conversation_context
    from engine.system_b.core_semantic_shadow import (
        build_user_counterpressure_temporal_shadow,
        render_core_semantic_shadow_json,
    )
    from scripts.evals.run_core_semantic_corpus import (
        EvaluationBoundaryCallFailure,
        EvaluationCallWallTimeout,
        _StageBoundary,
        _load_env,
        _write_shadow_attempt_error,
    )

    case = _case()
    _load_env(env_file)
    boundary = _StageBoundary(load_boundary_client_from_env(provider_name))
    context = load_conversation_context(
        REPO_ROOT / case["context_extraction_path"],
        REPO_ROOT / case["source_path"],
    )
    artifacts: list[Path] = []
    for repeat in range(1, REPEATS + 1):
        output = output_dir / f"counterpressure-temporal-{repeat:02d}.json"
        artifacts.append(output)
        if _artifact_is_valid(output):
            print(f"temporal {repeat}/{REPEATS}: reuse", flush=True)
            continue
        print(f"temporal {repeat}/{REPEATS}: run", flush=True)
        prior_failures = len(
            list(output_dir.glob(f"{output.stem}-attempt-*.error.json"))
        )
        for attempt in range(1, MAX_ATTEMPTS + 1):
            call_log = boundary.boundary.call_log  # type: ignore[attr-defined]
            start = len(call_log)
            started = time.monotonic()
            try:
                payload = build_user_counterpressure_temporal_shadow(
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
                raise RuntimeError(f"invalid temporal artifact: {output}")
            break
        else:
            raise RuntimeError(
                f"temporal repeat {repeat} failed after {MAX_ATTEMPTS} attempts"
            )
    return artifacts


def build_result(
    *,
    contract: Mapping[str, Any],
    artifact_paths: list[Path],
) -> dict[str, Any]:
    from scripts.evals.score_counterpressure_temporal_coverage import (
        build_temporal_coverage_result,
    )

    scoring_path = REPO_ROOT / contract["temporal_scoring_contract"]["path"]
    temporal = build_temporal_coverage_result(
        contract_path=scoring_path,
        case_id=CASE_ID,
        arm_name="counterpressure-v21-temporal",
        artifact_paths=artifact_paths,
    )
    metrics = temporal["metrics"]
    gate = contract["gate"]

    raw_count = 0
    validated_count = 0
    forbidden_kinds: set[str] = set()
    call_count = 0
    retry_count = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    for path in artifact_paths:
        artifact = _load_json(path)
        validation = artifact["validation"]["user_counterpressure"][
            "user_pressure_events"
        ]
        raw_count += int(validation["raw_count"])
        validated_count += int(validation["validated_count"])
        for candidate in artifact["semantic_candidate_ledger"]["candidates"]:
            raw = candidate.get("raw_proposal", {})
            kind = str(raw.get("kind") or "") if isinstance(raw, Mapping) else ""
            if kind in set(gate["mechanical"]["forbidden_returned_kinds"]):
                forbidden_kinds.add(kind)
        calls = artifact["model_usage"]["calls"]
        call_count += len(calls)
        retry_count += int(
            artifact["evaluation_execution"]["failed_attempts_before_success"]
        )
        prompt_tokens += sum(int(call.get("prompt_tokens") or 0) for call in calls)
        completion_tokens += sum(
            int(call.get("completion_tokens") or 0) for call in calls
        )
        total_tokens += sum(int(call.get("total_tokens") or 0) for call in calls)

    concept = metrics["concept_coverage"]
    first = metrics["first_introduction_coverage"]
    later = metrics["later_strengthening_coverage"]
    reasoning_checks = {
        "concept_recall": concept["weighted_recall"]
        >= gate["reasoning_substrate"]["required_concept_weighted_recall"],
        "stable_concept": len(concept["stable_observation_ids"])
        >= gate["reasoning_substrate"][
            "required_stable_concept_observation_count"
        ],
    }
    audit_checks = {
        "first_introduction_recall": first["weighted_recall"]
        >= gate["audit_trail"]["required_first_introduction_weighted_recall"],
        "stable_first_introduction": len(first["stable_observation_ids"])
        >= gate["audit_trail"][
            "required_stable_first_introduction_observation_count"
        ],
        "later_strengthening_recall": later["weighted_recall"]
        >= gate["audit_trail"]["required_later_strengthening_weighted_recall"],
        "stable_later_strengthening": len(later["stable_observation_ids"])
        >= gate["audit_trail"][
            "required_stable_later_strengthening_observation_count"
        ],
    }
    exact_validity = validated_count / raw_count if raw_count else 0.0
    mechanical_checks = {
        "exact_source_validity": exact_validity
        >= gate["mechanical"]["required_exact_source_validity"],
        "one_call_per_artifact": call_count
        == len(artifact_paths)
        * gate["mechanical"]["required_reader_calls_per_artifact"],
        "no_forbidden_returned_kinds": not forbidden_kinds,
    }
    reasoning_passed = all(reasoning_checks.values())
    audit_passed = all(audit_checks.values())
    mechanical_passed = all(mechanical_checks.values())
    passed = reasoning_passed and audit_passed and mechanical_passed
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "case_id": CASE_ID,
        "artifact_paths": [str(path) for path in artifact_paths],
        "temporal_coverage": temporal,
        "checks": {
            "reasoning_substrate": reasoning_checks,
            "audit_trail": audit_checks,
            "mechanical": mechanical_checks,
        },
        "reasoning_substrate_passed": reasoning_passed,
        "audit_trail_passed": audit_passed,
        "mechanical_passed": mechanical_passed,
        "passed": passed,
        "decision": (
            "eligible_for_three_case_discussion"
            if passed
            else "stop_and_review_without_more_paid_calls"
        ),
        "operational": {
            "successful_call_count": call_count,
            "retry_count": retry_count,
            "raw_candidate_count": raw_count,
            "validated_candidate_count": validated_count,
            "exact_source_validity": exact_validity,
            "forbidden_returned_kinds": sorted(forbidden_kinds),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
        "pass_authorizes": gate["pass_authorizes"],
        "pass_does_not_authorize": gate["pass_does_not_authorize"],
    }


def _render_markdown(result: Mapping[str, Any]) -> str:
    temporal = result["temporal_coverage"]["metrics"]
    lines = [
        "# Counter-Pressure v2.1 Temporal Preflight",
        "",
        f"Decision: **{'pass' if result['passed'] else 'fail'}**",
        "",
        "| product read | weighted recall | stable | passed |",
        "| --- | ---: | ---: | --- |",
    ]
    rows = [
        ("concept", "concept_coverage", result["reasoning_substrate_passed"]),
        ("first introduction", "first_introduction_coverage", result["audit_trail_passed"]),
        ("later strengthening", "later_strengthening_coverage", result["audit_trail_passed"]),
    ]
    for label, key, passed in rows:
        metric = temporal[key]
        lines.append(
            f"| {label} | {metric['weighted_recall']:.3f} | "
            f"{len(metric['stable_observation_ids'])} / {metric['observation_count']} | "
            f"{'yes' if passed else 'no'} |"
        )
    operational = result["operational"]
    lines.extend(
        [
            "",
            f"- Exact-source validity: {operational['exact_source_validity']:.3f}",
            f"- Successful calls: {operational['successful_call_count']}",
            f"- Retry calls: {operational['retry_count']}",
            f"- Recorded tokens: {operational['total_tokens']}",
            "",
            f"Decision code: `{result['decision']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    from scripts.evals.run_core_semantic_corpus import _default_env_file

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--real-boundary-approved", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser().resolve()
    contract_path = args.contract.expanduser().resolve()
    contract = validate_contract(contract_path)
    if not args.real_boundary_approved:
        print(f"Temporal preflight contract validated: {contract_path}")
        print("No model calls executed.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = run_paid_repeats(
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
        _render_markdown(result), encoding="utf-8"
    )
    print(f"Temporal preflight {'passed' if result['passed'] else 'failed'}.")
    print(f"Decision: {result['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

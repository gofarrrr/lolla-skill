#!/usr/bin/env python3
"""Run the approved real-boundary specialist extractor probe over archives."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_RUNS = (
    "launch-limited-beta-workflow/20260626T125112Z_b861fd",
    "initiate-pre-sale-coffee/20260626T131939Z_368960",
    "implement-price-increase-three/20260626T132915Z_49172d",
    "five-person-saas-team/20260626T133147Z_99712f",
)

FINDINGS_SCHEMA_VERSION = "lolla.real_specialist_extractor_probe_findings.v0"


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


class InputError(ValueError):
    """Deterministic, sanitized user-facing input error."""


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.boundary_provider import load_boundary_client_from_env
    from engine.system_b.specialist_extractor_probe import SPECIALISTS

    parser = argparse.ArgumentParser(
        description=(
            "Run the local/offline real-boundary specialist extractor probe. "
            "Requires explicit model-call approval and never writes into archives."
        )
    )
    parser.add_argument("archive_root", type=Path, help="Root containing case/run archives.")
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="case_id/run_id archive relpath. Defaults to the four PR29B modern runs.",
    )
    parser.add_argument("--out-dir", required=True, type=Path, help="Per-run JSON output directory.")
    parser.add_argument("--json-out", required=True, type=Path, help="Aggregate JSON findings path.")
    parser.add_argument("--md-out", required=True, type=Path, help="Aggregate Markdown findings path.")
    parser.add_argument(
        "--provider",
        default="openrouter",
        help="Boundary provider to load from environment. PR29B supports openrouter only.",
    )
    parser.add_argument(
        "--specialist",
        action="append",
        choices=SPECIALISTS,
        default=[],
        help="Specialist to run. Repeatable. Defaults to all when omitted.",
    )
    parser.add_argument("--all", action="store_true", help="Run all supported specialists.")
    parser.add_argument(
        "--real-boundary-approved",
        action="store_true",
        help="Required acknowledgement that this script may make real model calls.",
    )
    args = parser.parse_args(argv)

    try:
        if not args.real_boundary_approved:
            raise InputError("real boundary approval flag is required")
        archive_root = args.archive_root.expanduser()
        if not archive_root.is_dir():
            raise InputError("archive_root is not a directory")
        run_relpaths = _normalize_run_relpaths(args.run or list(DEFAULT_RUNS))
        _validate_outputs_outside_archive_root(
            archive_root,
            [args.out_dir, args.json_out, args.md_out],
        )
        provider = _validate_provider(args.provider)
        specialists = list(SPECIALISTS) if args.all or not args.specialist else args.specialist
        boundary = load_boundary_client_from_env(provider)
        report = run_real_specialist_probe(
            archive_root=archive_root,
            run_relpaths=run_relpaths,
            out_dir=args.out_dir,
            boundary=boundary,
            specialists=specialists,
        )
        json_out = _safe_external_output_path(archive_root, args.json_out)
        md_out = _safe_external_output_path(archive_root, args.md_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(render_findings_json(report), encoding="utf-8")
        md_out.write_text(render_findings_markdown(report), encoding="utf-8")
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {type(exc).__name__}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: output could not be written:{type(exc).__name__}", file=sys.stderr)
        return 2
    return 0


def run_real_specialist_probe(
    *,
    archive_root: Path,
    run_relpaths: Sequence[str],
    out_dir: Path,
    boundary: Any,
    specialists: Sequence[str],
) -> dict[str, Any]:
    from engine.system_b.specialist_extractor_probe import (
        write_real_specialist_extractor_probe,
    )

    archive_root_resolved = archive_root.expanduser().resolve(strict=False)
    output_dir = _safe_external_output_path(archive_root_resolved, out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for relpath in run_relpaths:
        run_dir = archive_root_resolved / relpath
        if not run_dir.is_dir():
            raise InputError(f"run archive missing: {relpath}")
        output_path = output_dir / f"{relpath.replace('/', '__')}.json"
        _, probe = write_real_specialist_extractor_probe(
            run_dir,
            output_path,
            boundary=boundary,
            specialists=specialists,
        )
        records.append(_compact_probe_record(probe, output_path=output_path))

    return _build_findings(records)


def render_findings_json(findings: Mapping[str, Any]) -> str:
    return json.dumps(findings, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_findings_markdown(findings: Mapping[str, Any]) -> str:
    lines = [
        "# Real Specialist Extractor Probe Findings",
        "",
        "## Summary",
        "",
        f"- Records inspected: {_int(findings.get('record_count'))}",
        f"- Model calls: {_int(findings.get('model_call_count'))}",
        f"- Estimated cost USD: {_text(findings.get('estimated_cost_usd'))}",
        f"- Cost estimate state: {_text(findings.get('cost_estimate_state'))}",
        f"- Boundary status counts: {_inline_counts(_mapping(findings.get('boundary_status_counts')))}",
        f"- Provider-boundary warning count: {_int(findings.get('provider_boundary_warning_count'))}",
        f"- Improved target elements: {_int(findings.get('improved_target_element_count'))}",
        "",
        "## Per-Run Coverage Delta",
        "",
        "| case | run_id | live constraints | stance lineage | dropped threads | calls | cost |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for record in _records(findings):
        specialists = _mapping(record.get("specialists"))
        lines.append(
            "| "
            + " | ".join(
                [
                    _text(record.get("case_id")),
                    _text(record.get("run_id")),
                    _yes_no(_did_improve(specialists, "live_constraints")),
                    _yes_no(_did_improve(specialists, "stance")),
                    _yes_no(_did_improve(specialists, "dropped_threads")),
                    str(_int(record.get("model_call_count"))),
                    _text(record.get("estimated_cost_usd")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Per-Specialist Validation", ""])
    lines.append("| specialist | attempted | raw candidates | validated | improved runs | grounding | failures |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    for specialist, summary in _mapping(findings.get("per_specialist_totals")).items():
        item = _mapping(summary)
        lines.append(
            "| "
            + " | ".join(
                [
                    str(specialist),
                    str(_int(item.get("attempted_count"))),
                    str(_int(item.get("raw_candidate_count"))),
                    str(_int(item.get("validated_event_count"))),
                    str(_int(item.get("improved_run_count"))),
                    _inline_counts(_mapping(item.get("grounding_counts"))),
                    _inline_counts(_mapping(item.get("validation_failures"))),
                ]
            )
            + " |"
        )
    recommendation = _mapping(findings.get("recommendation"))
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- Decision: {_text(recommendation.get('decision'))}",
            f"- Recommendation: {_text(recommendation.get('recommendation'))}",
            f"- Reason: {_text(recommendation.get('reason'))}",
            f"- User-values gap: {_text(recommendation.get('user_values_gap'))}",
            f"- Provider-boundary note: {_text(recommendation.get('provider_boundary_note'))}",
            "",
            "## Privacy And Custody",
            "",
            "- Raw transcript text exported: false",
            "- Raw memo/revised answer text exported: false",
            "- Raw model messages exported: false",
            "- Absolute archive paths exported: false",
            "- Archive mutation: false",
            "- Runtime behavior changed: false",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_findings(records: list[dict[str, Any]]) -> dict[str, Any]:
    per_specialist = _per_specialist_totals(records)
    boundary_status_counts = Counter()
    model_call_count = 0
    estimated_cost = 0.0
    cost_states: Counter[str] = Counter()
    improved_target_count = 0
    provider_boundary_warning_count = 0
    for record in records:
        boundary_status_counts.update(_mapping(record.get("boundary_status_counts")))
        model_call_count += _int(record.get("model_call_count"))
        estimated_cost += _float(record.get("estimated_cost_usd"))
        provider_boundary_warning_count += _int(record.get("provider_boundary_warning_count"))
        cost_state = _text(record.get("cost_estimate_state"))
        if cost_state:
            cost_states[cost_state] += 1
        for specialist in _mapping(record.get("specialists")).values():
            if bool(_mapping(specialist).get("did_improve_coverage")):
                improved_target_count += 1
    return {
        "schema_version": FINDINGS_SCHEMA_VERSION,
        "source": _source_scope(model_call_count=model_call_count),
        "record_count": len(records),
        "model_call_count": model_call_count,
        "estimated_cost_usd": round(estimated_cost, 6),
        "cost_estimate_state": _aggregate_cost_state(cost_states),
        "boundary_status_counts": _counter_dict(boundary_status_counts),
        "provider_boundary_warning_count": provider_boundary_warning_count,
        "improved_target_element_count": improved_target_count,
        "per_specialist_totals": per_specialist,
        "records": records,
        "recommendation": _recommendation(
            records,
            per_specialist=per_specialist,
            boundary_status_counts=boundary_status_counts,
            provider_boundary_warning_count=provider_boundary_warning_count,
        ),
    }


def _compact_probe_record(probe: Mapping[str, Any], *, output_path: Path) -> dict[str, Any]:
    model_usage = _mapping(probe.get("model_usage"))
    calls = [_mapping(call) for call in _list(probe.get("boundary_calls"))]
    return {
        "case_id": _text(probe.get("case_id")),
        "run_id": _text(probe.get("run_id")),
        "archive_relpath": _text(probe.get("archive_relpath")),
        "output_path": _safe_output_text(output_path),
        "boundary_mode": _text(probe.get("boundary_mode")),
        "model_call_count": _int(probe.get("model_call_count")),
        "estimated_cost_usd": model_usage.get("estimated_total_cost_usd"),
        "cost_estimate_state": _text(model_usage.get("cost_estimate_state")),
        "model_provider": _text(model_usage.get("provider")),
        "models_seen": _string_list(model_usage.get("models_seen")),
        "requested_models_seen": _string_list(model_usage.get("requested_models_seen")),
        "token_usage": {
            "prompt_tokens": _int(model_usage.get("prompt_tokens")),
            "completion_tokens": _int(model_usage.get("completion_tokens")),
            "total_tokens": _int(model_usage.get("total_tokens")),
        },
        "boundary_status_counts": _counter_dict(
            Counter(_text(call.get("status")) for call in calls)
        ),
        "provider_boundary_warning_count": sum(
            1 for call in calls if bool(call.get("reasoning_details_present"))
        ),
        "baseline_semantic_coverage": probe.get("baseline_semantic_coverage", {}),
        "enhanced_semantic_coverage": probe.get("enhanced_semantic_coverage", {}),
        "coverage_delta": _coverage_delta(probe),
        "specialists": probe.get("specialists", {}),
        "source": probe.get("source", {}),
    }


def _coverage_delta(probe: Mapping[str, Any]) -> dict[str, Any]:
    baseline = _mapping(_mapping(probe.get("baseline_semantic_coverage")).get("semantic_elements"))
    enhanced = _mapping(_mapping(probe.get("enhanced_semantic_coverage")).get("semantic_elements"))
    delta: dict[str, Any] = {}
    for element, before in baseline.items():
        after = _mapping(enhanced.get(element))
        before_map = _mapping(before)
        changed = (
            _text(before_map.get("status")) != _text(after.get("status"))
            or _text(before_map.get("grounding")) != _text(after.get("grounding"))
        )
        if changed:
            delta[str(element)] = {
                "before_status": _text(before_map.get("status")),
                "after_status": _text(after.get("status")),
                "before_grounding": _text(before_map.get("grounding")),
                "after_grounding": _text(after.get("grounding")),
            }
    return delta


def _per_specialist_totals(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "attempted_count": 0,
            "raw_candidate_count": 0,
            "validated_event_count": 0,
            "improved_run_count": 0,
            "grounding_counts": Counter(),
            "validation_failures": Counter(),
        }
    )
    for record in records:
        for specialist, payload in _mapping(record.get("specialists")).items():
            item = _mapping(payload)
            total = totals[str(specialist)]
            if bool(item.get("attempted")):
                total["attempted_count"] += 1
            total["raw_candidate_count"] += _int(item.get("raw_candidate_count"))
            total["validated_event_count"] += _int(item.get("validated_event_count"))
            if bool(item.get("did_improve_coverage")):
                total["improved_run_count"] += 1
            total["grounding_counts"].update(_mapping(item.get("grounding_counts")))
            total["validation_failures"].update(_mapping(item.get("validation_failures")))
    return {
        specialist: {
            "attempted_count": _int(item["attempted_count"]),
            "raw_candidate_count": _int(item["raw_candidate_count"]),
            "validated_event_count": _int(item["validated_event_count"]),
            "improved_run_count": _int(item["improved_run_count"]),
            "grounding_counts": _counter_dict(item["grounding_counts"]),
            "validation_failures": _counter_dict(item["validation_failures"]),
        }
        for specialist, item in sorted(totals.items())
    }


def _recommendation(
    records: Sequence[Mapping[str, Any]],
    *,
    per_specialist: Mapping[str, Any],
    boundary_status_counts: Mapping[str, int],
    provider_boundary_warning_count: int = 0,
) -> dict[str, str]:
    non_ok = {
        status: count
        for status, count in boundary_status_counts.items()
        if status and status != "ok" and _int(count) > 0
    }
    if non_ok:
        return {
            "decision": "E",
            "recommendation": "probe_inconclusive_due_model_provider_or_boundary_issue",
            "reason": "One or more specialist boundary calls did not complete cleanly.",
            "user_values_gap": "D: user_values_or_priorities_signal remains unsolved by current specialists.",
            "provider_boundary_note": "Non-ok boundary status is separate from extractor validation quality.",
        }
    attempted_runs = max(1, len(records))
    improved = sum(
        _int(_mapping(item).get("improved_run_count"))
        for item in per_specialist.values()
    )
    validated = sum(
        _int(_mapping(item).get("validated_event_count"))
        for item in per_specialist.values()
    )
    if improved >= attempted_runs * len(per_specialist):
        decision = "A"
        recommendation = "existing_specialists_worth_later_runtime_design"
        reason = "All attempted target elements improved across the sampled runs."
    elif improved > 0 and validated > 0:
        decision = "B"
        recommendation = "existing_specialists_help_partially_keep_offline_until_design"
        reason = "Some target elements improved, but the improvement was not universal."
    elif validated > 0:
        decision = "B"
        recommendation = "existing_specialists_validate_but_do_not_move_coverage_enough"
        reason = "Specialists produced validated events, but coverage deltas were weak."
    else:
        decision = "C"
        recommendation = "existing_specialists_do_not_justify_runtime_integration"
        reason = "No validated specialist events improved semantic coverage in the sample."
    return {
        "decision": decision,
        "recommendation": recommendation,
        "reason": reason,
        "user_values_gap": "D: user_values_or_priorities_signal remains unsolved by current specialists.",
        "provider_boundary_note": (
            f"{provider_boundary_warning_count} call(s) returned provider reasoning metadata despite disabled reasoning; "
            "treat this as a separate provider-boundary issue, not an extractor-validation failure."
            if provider_boundary_warning_count
            else "No provider-boundary reasoning-detail warnings were observed."
        ),
    }


def _normalize_run_relpaths(values: Sequence[str]) -> list[str]:
    relpaths: list[str] = []
    for value in values:
        text = _text(value)
        if not text or text.startswith("/") or ".." in Path(text).parts:
            raise InputError("run relpath must be case_id/run_id")
        parts = Path(text).parts
        if len(parts) != 2:
            raise InputError("run relpath must be case_id/run_id")
        relpaths.append("/".join(parts))
    return relpaths


def _validate_provider(value: str) -> str:
    provider = _text(value).lower() or "openrouter"
    if provider != "openrouter":
        raise InputError("real specialist probe currently supports openrouter cost telemetry only")
    return provider


def _validate_outputs_outside_archive_root(archive_root: Path, paths: Sequence[Path]) -> None:
    for path in paths:
        _safe_external_output_path(archive_root, path)


def _safe_external_output_path(archive_root: Path, path: Path) -> Path:
    archive_root_resolved = archive_root.expanduser().resolve(strict=False)
    output = path.expanduser()
    if not output.name:
        raise InputError("output path is invalid")
    resolved = output.resolve(strict=False)
    if resolved == archive_root_resolved or archive_root_resolved in resolved.parents:
        raise InputError("output path must not be inside archive_root")
    return output


def _source_scope(*, model_call_count: int) -> dict[str, Any]:
    return {
        "local_only": True,
        "shareable_without_review": False,
        "raw_archives_read": True,
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "raw_model_messages_included": False,
        "provider_reasoning_details_included": False,
        "failed_quote_text_included": False,
        "absolute_archive_paths_included": False,
        "control_argument_values_included": False,
        "model_calls": model_call_count,
        "llm_judge_used": False,
        "archive_mutation": False,
        "runtime_behavior_changed": False,
    }


def _aggregate_cost_state(states: Mapping[str, int]) -> str:
    if not states:
        return "not_applicable"
    if set(states) == {"complete"}:
        return "complete"
    if "complete" in states:
        return "partial"
    if "unknown" in states:
        return "unknown"
    return sorted(states)[0]


def _records(findings: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [record for record in _list(findings.get("records")) if isinstance(record, Mapping)]


def _did_improve(specialists: Mapping[str, Any], specialist: str) -> bool:
    return bool(_mapping(specialists.get(specialist)).get("did_improve_coverage"))


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _inline_counts(counts: Mapping[str, Any]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}:{_int(value)}" for key, value in sorted(counts.items()))


def _counter_dict(counter: Mapping[str, Any]) -> dict[str, int]:
    return {
        str(key): _int(value)
        for key, value in sorted(
            ((key, value) for key, value in counter.items() if key),
            key=lambda item: (-_int(item[1]), str(item[0])),
        )
    }


def _safe_output_text(path: Path) -> str:
    text = str(path)
    if text.startswith("/tmp/"):
        return text
    return path.name


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return sorted(_text(item) for item in value if _text(item))


def _text(value: Any) -> str:
    return str(value or "").strip()


def _int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    raise SystemExit(main())

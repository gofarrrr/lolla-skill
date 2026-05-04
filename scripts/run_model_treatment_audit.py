#!/usr/bin/env python3
"""Run the model-treatment audit prototype against archived Lolla runs.

This is Observatory plumbing only. Python assembles packets, calls a narrow
LLM judge, validates exact output quotes, and writes audit artifacts. Python
does not decide whether an affordance was treated.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.boundary_provider import OpenAICompatibleBoundaryClient  # noqa: E402
from system_b.model_treatment_audit import (  # noqa: E402
    TREATMENT_AUDIT_SCHEMA_VERSION,
    build_audited_output_text,
    build_case_context,
    build_model_output_slice,
    build_pressure_baseline_text,
    build_summary_payload,
    compute_evidence_tier,
    item_is_merge_gate_candidate,
    load_compiled_affordances,
    load_do_not_promote_flags,
    load_json,
    normalize_judge_payload,
    selected_models_by_lane,
    sha256_text,
    validate_judge_payload,
    validate_treatment_audit_payload,
    write_json,
)
from system_b.route_trace import build_route_trace_payload  # noqa: E402


DEFAULT_RUN_REFS_SOURCE = REPO_ROOT / "data/treatment_audits/summary.v1.json"

SYSTEM_PROMPT = """You are a conservative model-treatment audit judge.

Your job is narrow: decide whether one selected mental-model affordance was
actually treated in the audited output, or merely named / gestured at.

Return JSON only. Do not include prose outside JSON.

Rules:
- First decide activation_status from the affordance's structural activation_shape and CASE_CONTEXT.
- Do not decide activation by case category labels. Decide whether the structural conditions are present.
- activation_note must name only structural signals or their absence. Avoid domain labels, relationship labels, industry labels, profession labels, organization names, and settings.
- If activation_status is not activated, do not score an untreated gap.
- Be conservative. Prefer not_treated over inferring treatment from vague language.
- activation_quote must be an exact substring of CASE_CONTEXT when activation_status is activated. No paraphrase.
- output_quote must be an exact substring of AUDITED_OUTPUT_SLICE. No paraphrase.
- If treatment_status is treated, partially_treated, set_aside_with_reason, or duplicate_of_existing_pressure, output_quote must be non-empty.
- For not_treated or not_applicable, output_quote may be empty only when there is no relevant passage to quote.
- If you cannot copy a quote exactly, use not_treated or not_applicable with an empty output_quote. Never paraphrase a quote.
- Use activation_status set_aside_as_misfit with treatment_status set_aside_with_reason when the audited output explicitly sets aside the affordance because the structural mechanism does not fit.
- Mark duplicate_of_existing_pressure true when the affordance's required move is already covered in the Pressure Check baseline.
- Do not reward do_not_runtime_promote flags. Audit them normally, but do not treat the flag as evidence.
- Keep treatment_note brief. The status and exact quote are the signal.
"""

OUTPUT_SCHEMA = {
    "activation_status": "activated | not_activated | unclear_activation | set_aside_as_misfit | activation_shape_missing",
    "activation_note": "40+ chars, concrete structural fit rationale; do not classify by case category",
    "activation_quote": "exact substring of CASE_CONTEXT when activated; otherwise may be empty",
    "treatment_status": "treated | partially_treated | set_aside_with_reason | duplicate_of_existing_pressure | not_treated | not_applicable",
    "output_quote": "exact substring of AUDITED_OUTPUT_SLICE, or empty only for not_treated/not_applicable",
    "treatment_note": "40+ chars, concrete note about what was or was not treated",
    "missing_requirements": ["requirement text that was missing; empty list if none"],
    "duplicate_of_existing_pressure": "boolean",
    "baseline_coverage": "new_finding | duplicate_of_existing_pressure | additional_specificity | not_a_finding",
    "confidence": "high | medium | weak",
    "one_line_description": "one short sentence suitable for a PR evidence list",
}


def main() -> int:
    args = _parse_args()
    _load_env_file(REPO_ROOT / ".env")

    compiled = load_compiled_affordances(args.compiled_affordances)
    flags = load_do_not_promote_flags(args.quality_report)
    run_refs = args.run_ref or _default_run_refs(args.output_dir)

    boundary = _make_boundary(args)
    audits: list[dict[str, Any]] = []
    total_calls = 0

    for ref in run_refs:
        run_dir = args.archive_root / ref
        audit = run_single_archive(
            run_dir=run_dir,
            compiled_affordances=compiled,
            do_not_promote_flags=flags,
            boundary=boundary,
            max_attempts=args.max_attempts,
        )
        validate_treatment_audit_payload(audit)
        out_path = args.output_dir / f"{audit['run_id']}.json"
        write_json(out_path, audit)
        audits.append(audit)
        total_calls += int(audit["metadata"]["judge_call_count"])
        print(
            f"wrote {out_path} "
            f"({len(audit['items'])} items, {audit['validation_summary']['judge_rejection_count']} rejected attempts)",
            file=sys.stderr,
        )

    summary = build_summary_payload(audits)
    summary["metadata"] = {
        "schema_version": TREATMENT_AUDIT_SCHEMA_VERSION,
        "judge_provider": boundary.provider_name,
        "judge_model": boundary.model,
        "judge_call_count": total_calls,
        "run_refs": list(run_refs),
    }
    write_json(args.output_dir / "summary.json", summary)
    print(f"wrote {args.output_dir / 'summary.json'}", file=sys.stderr)
    return 0


def run_single_archive(
    *,
    run_dir: Path,
    compiled_affordances: dict[str, list[dict[str, Any]]],
    do_not_promote_flags: dict[str, dict[str, str]],
    boundary: OpenAICompatibleBoundaryClient,
    max_attempts: int = 2,
) -> dict[str, Any]:
    result_path = run_dir / "result.json"
    result = load_json(result_path)
    route_trace = result.get("audit_summary", {}).get("route_trace")
    route_trace_source = "persisted"
    if not isinstance(route_trace, dict):
        route_trace = build_route_trace_payload(result)
        route_trace_source = "computed_fallback"

    selected_by_lane = selected_models_by_lane(route_trace)
    jobs = []
    for model_id, lanes in selected_by_lane.items():
        for affordance in compiled_affordances.get(model_id, []):
            jobs.append((model_id, lanes, affordance))

    case_id = run_dir.parent.name
    stamp = run_dir.name
    run_id = f"{case_id}__{stamp}"
    audited_output = build_audited_output_text(result, run_dir)
    pressure_baseline = build_pressure_baseline_text(result, run_dir)
    case_context = build_case_context(result)
    items: list[dict[str, Any]] = []
    rejection_count = 0
    token_usage: Counter[str] = Counter()
    call_count = 0

    for model_id, lanes, affordance in jobs:
        output_slice = build_model_output_slice(result, model_id=model_id, run_dir=run_dir)
        judge_payload, attempts, item_rejections = _call_judge_with_validation(
            boundary=boundary,
            run_id=run_id,
            model_id=model_id,
            selected_lanes=lanes,
            affordance=affordance,
            do_not_promote_flag=do_not_promote_flags.get(str(affordance["affordance_id"])),
            case_context=case_context,
            pressure_baseline=pressure_baseline,
            audited_output_slice=output_slice,
            max_attempts=max_attempts,
        )
        rejection_count += item_rejections
        call_count += len(attempts)
        for attempt in attempts:
            usage = attempt["metadata"]
            token_usage["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
            token_usage["completion_tokens"] += int(usage.get("completion_tokens") or 0)
            token_usage["total_tokens"] += int(usage.get("total_tokens") or 0)

        normalized = normalize_judge_payload(judge_payload)
        flag = do_not_promote_flags.get(str(affordance["affordance_id"]))
        item = {
            "model_id": model_id,
            "affordance_id": affordance["affordance_id"],
            "selected_lanes": lanes,
            "activation_status": normalized["activation_status"],
            "activation_note": normalized["activation_note"],
            "activation_quote": normalized["activation_quote"],
            "treatment_status": normalized["treatment_status"],
            "output_quote": normalized["output_quote"],
            "treatment_note": normalized["treatment_note"],
            "missing_requirements": normalized["missing_requirements"],
            "duplicate_of_existing_pressure": normalized["duplicate_of_existing_pressure"],
            "baseline_coverage": normalized["baseline_coverage"],
            "confidence": normalized["confidence"],
            "one_line_description": normalized["one_line_description"],
            "audited_output_slice": output_slice,
            "do_not_promote_without_rewrite_review": bool(flag),
            "do_not_promote_reason": flag.get("reason", "") if flag else "",
            "evidence_tier": "excluded",
            "merge_gate_evidence_candidate": False,
            "judge_attempt_count": len(attempts),
            "judge_model": attempts[-1]["metadata"].get("model", boundary.model),
            "judge_provider": attempts[-1]["metadata"].get("provider_name", boundary.provider_name),
        }
        item["evidence_tier"] = compute_evidence_tier(item)
        item["merge_gate_evidence_candidate"] = item_is_merge_gate_candidate(item)
        items.append(item)

    audit = {
        "schema_version": TREATMENT_AUDIT_SCHEMA_VERSION,
        "run_id": run_id,
        "case_id": case_id,
        "source_run_ref": f"{case_id}/{stamp}",
        "metadata": {
            "judge_provider": boundary.provider_name,
            "judge_model": boundary.model,
            "judge_call_count": call_count,
            "route_trace_source": route_trace_source,
            "compiled_affordance_source": "data/compiled/model_affordances/affordances_v1.json",
            "token_usage": dict(sorted(token_usage.items())),
            "audited_output_sha256": sha256_text(audited_output),
        },
        "case_context": case_context,
        "audited_output": audited_output,
        "pressure_check_baseline": pressure_baseline,
        "items": items,
        "validation_summary": {
            "judge_rejection_count": rejection_count,
            "item_count": len(items),
        },
    }
    return audit


def _call_judge_with_validation(
    *,
    boundary: OpenAICompatibleBoundaryClient,
    run_id: str,
    model_id: str,
    selected_lanes: list[str],
    affordance: dict[str, Any],
    do_not_promote_flag: dict[str, str] | None,
    case_context: str,
    pressure_baseline: str,
    audited_output_slice: str,
    max_attempts: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    attempts: list[dict[str, Any]] = []
    rejections = 0
    validation_feedback = ""
    for attempt_index in range(1, max(max_attempts, 1) + 1):
        user_prompt = _judge_user_prompt(
            run_id=run_id,
            model_id=model_id,
            selected_lanes=selected_lanes,
            affordance=affordance,
            do_not_promote_flag=do_not_promote_flag,
            case_context=case_context,
            pressure_baseline=pressure_baseline,
            audited_output_slice=audited_output_slice,
            validation_feedback=validation_feedback,
        )
        payload, metadata = boundary.run_json_with_metadata(
            SYSTEM_PROMPT,
            user_prompt,
            stage="model_treatment_audit",
            tendency_id=str(affordance.get("affordance_id") or ""),
        )
        attempts.append({"payload": payload, "metadata": asdict(metadata)})
        errors = validate_judge_payload(
            payload,
            audited_output=audited_output_slice,
            activation_context=case_context,
        )
        if not errors:
            return payload, attempts, rejections
        rejections += 1
        validation_feedback = (
            "Your previous response failed validation. Fix only these mechanical issues: "
            + "; ".join(errors)
            + " For any non-empty output_quote, copy exactly one complete string from quote_candidates. "
            + "For activation_quote, copy exactly one complete string from case_quote_candidates."
        )
    raise RuntimeError(
        f"judge response failed validation for {run_id} {affordance.get('affordance_id')}: "
        f"{validation_feedback}"
    )


def _judge_user_prompt(
    *,
    run_id: str,
    model_id: str,
    selected_lanes: list[str],
    affordance: dict[str, Any],
    do_not_promote_flag: dict[str, str] | None,
    case_context: str,
    pressure_baseline: str,
    audited_output_slice: str,
    validation_feedback: str,
) -> str:
    packet = {
        "run_id": run_id,
        "case_context": _clip(case_context, 2500),
        "model_id": model_id,
        "selected_lanes": selected_lanes,
        "affordance": {
            "affordance_id": affordance.get("affordance_id", ""),
            "name": affordance.get("name", ""),
            "mechanism": affordance.get("mechanism", ""),
            "activation_shape": affordance.get("activation_shape", {}),
            "treatment_requirements": affordance.get("treatment_requirements", []),
            "diagnostic_questions": affordance.get("diagnostic_questions", []),
            "misuse_guards": affordance.get("misuse_guards", []),
        },
        "do_not_runtime_promote_without_rewrite_review": do_not_promote_flag or {},
        "pressure_check_baseline": _clip(pressure_baseline, 5000),
        "audited_output_slice": _clip(audited_output_slice, 12000),
        "case_quote_candidates": _quote_candidates(case_context),
        "quote_candidates": _quote_candidates(audited_output_slice),
        "required_output_schema": OUTPUT_SCHEMA,
        "validation_feedback": validation_feedback,
    }
    return (
        "Audit this single affordance against the case and audited output slice.\n"
        "Use only the supplied packet. Return exactly one JSON object matching required_output_schema.\n\n"
        "Evaluation order:\n"
        "1. Determine activation_status first from activation_shape and case_context.\n"
        "2. Activation is structural fit, not category matching by domain, relationship type, industry, or setting.\n"
        "3. Write activation_note using structural features only: commitments, reversibility, confidence claims, feedback, leverage, bottlenecks, reference classes, actors, incentives, constraints, delays, and evidence. "
        "Do not name the domain, relationship type, industry, profession, organization, or setting.\n"
        "4. If activation_shape is missing or empty, use activation_shape_missing and treatment_status not_applicable.\n"
        "5. If activation_status is not_activated, unclear_activation, or activation_shape_missing, set treatment_status not_applicable.\n"
        "6. If the audited output explicitly sets aside this affordance as structurally misfit, use activation_status set_aside_as_misfit and treatment_status set_aside_with_reason.\n"
        "7. Only when activation_status is activated may you mark not_treated or partially_treated.\n\n"
        "Activation quote discipline: when activation_status is activated, activation_quote must be copied exactly from case_quote_candidates. "
        "Use an empty activation_quote for not_activated, unclear_activation, set_aside_as_misfit, or activation_shape_missing.\n\n"
        "Quote discipline: copy every non-empty output_quote exactly from quote_candidates. "
        "Do not use ellipses, summaries, or normalized wording unless those exact characters appear in the audited output.\n\n"
        "Important baseline classification rule:\n"
        "- If Pressure Check already covers the same required move, classify duplicate_of_existing_pressure.\n"
        "- If this audit is more operational than Pressure Check in the same territory, classify additional_specificity.\n"
        "- If Pressure Check does not cover the missing or partial treatment, classify new_finding.\n"
        "- If no treatment gap exists, classify not_a_finding unless it is clearly duplicate_of_existing_pressure.\n\n"
        "PACKET:\n"
        f"{json.dumps(packet, indent=2, ensure_ascii=False)}"
    )


def _make_boundary(args: argparse.Namespace) -> OpenAICompatibleBoundaryClient:
    if args.judge_model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = args.judge_model
    return OpenAICompatibleBoundaryClient.openrouter_from_env()


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
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
        os.environ.setdefault(key, value)


def _default_run_refs(output_dir: Path) -> list[str]:
    candidates = [Path(output_dir) / "summary.v1.json", DEFAULT_RUN_REFS_SOURCE]
    for path in candidates:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        refs = payload.get("metadata", {}).get("run_refs")
        if isinstance(refs, list) and all(isinstance(ref, str) and ref for ref in refs):
            return list(refs)
    raise SystemExit(
        "No default archived run refs found. Pass --run-ref or provide "
        "data/treatment_audits/summary.v1.json with metadata.run_refs."
    )


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n[...truncated for token budget...]"


def _quote_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if len(line) < 30 or line in seen:
            continue
        if line.startswith("## "):
            continue
        if len(line) > 260:
            line = line[:260].rstrip()
        seen.add(line)
        candidates.append(line)
        if len(candidates) >= 60:
            break
    return candidates


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=Path.home() / ".local/share/lolla/runs",
    )
    parser.add_argument(
        "--run-ref",
        action="append",
        help="Archived run ref as case-id/run-id. Defaults to the PR5 five-run set.",
    )
    parser.add_argument(
        "--compiled-affordances",
        type=Path,
        default=REPO_ROOT / "data/compiled/model_affordances/affordances_v1.json",
    )
    parser.add_argument(
        "--quality-report",
        type=Path,
        default=REPO_ROOT / "data/compiled/model_affordances/quality_report_v1.md",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "data/treatment_audits",
    )
    parser.add_argument(
        "--judge-model",
        default=os.getenv("LOLLA_TREATMENT_AUDIT_MODEL", ""),
        help="OpenRouter model override. Defaults to the repo's OpenRouter boundary model.",
    )
    parser.add_argument("--max-attempts", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())

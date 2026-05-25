#!/usr/bin/env python3
"""Run a Lane-1-only model/conversation diagnostic.

This intentionally avoids the full pipeline tail (Lane 2/3/4, BI, revision,
V60, and pre-Step-6 rendering). The question is narrow: did Lane 1 go quiet
because of the model, the conversation, Pass 2 rejection, or wiring sensitivity?
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = REPO_ROOT / "engine"
if (ENGINE_DIR / "system_b" / "__init__.py").exists():
    sys.path.insert(0, str(ENGINE_DIR))


from system_b.conversation_loader import load_conversation_context  # noqa: E402
from system_b.embedding_retriever import capture_usage  # noqa: E402
from system_b.pipeline import PipelineConfig, SystemBPipeline  # noqa: E402
from system_b.usage_summary import build_usage_summary  # noqa: E402


DEFAULT_ARCHIVE_ROOT = Path.home() / ".local" / "share" / "lolla" / "runs"
DEFAULT_OLD_RUN = DEFAULT_ARCHIVE_ROOT / "founder-grant-marcus-equity" / "20260429T141920Z"
DEFAULT_NEW_RUN = DEFAULT_ARCHIVE_ROOT / "founder-grant-marcus-equity-1" / "20260522T191424Z"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "research" / "lane1-model-diagnostic-2026-05-25"


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
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _load_default_env() -> None:
    for candidate in [
        REPO_ROOT / ".env",
        Path.home() / ".config" / "lolla" / ".env",
    ]:
        if candidate.exists():
            _load_env_file(candidate)
            return


def _data_root() -> Path:
    skill_data = REPO_ROOT / "data"
    tmp_root = Path(tempfile.mkdtemp(prefix="lolla_lane1_diag_"))
    os.symlink(str(skill_data), str(tmp_root / "build"))
    return tmp_root


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return value


def _boundary_dicts(boundary_calls: Any) -> list[dict[str, Any]]:
    return [_jsonable(call) for call in boundary_calls or ()]


def _run_arm(
    *,
    arm_id: str,
    description: str,
    run_dir: Path,
    requested_model: str,
    pre_step6_mode: str,
    output_dir: Path,
) -> dict[str, Any]:
    extraction_path = run_dir / "extraction.json"
    conversation_path = run_dir / "conversation.txt"
    if not extraction_path.exists() or not conversation_path.exists():
        raise FileNotFoundError(f"Missing extraction/conversation files in {run_dir}")

    previous_model = os.environ.get("LOLLA_OPENROUTER_MODEL")
    os.environ["LOLLA_OPENROUTER_MODEL"] = requested_model
    os.environ["LOLLA_RUN_ID"] = f"lane1diag_{arm_id}"

    started = time.monotonic()
    embedding_records: list[dict[str, Any]] = []
    try:
        pipeline = SystemBPipeline.load_live(
            root=_data_root(),
            provider_name="openrouter",
            config=PipelineConfig(
                enable_companion=False,
                enable_frame_pressure=False,
                enable_structural_coverage=False,
                enable_embeddings=bool(os.environ.get("OPENAI_API_KEY", "")),
                enable_deep_checks=True,
            ),
        )
        context = load_conversation_context(
            extraction_path=extraction_path,
            conversation_path=conversation_path,
        )
        with capture_usage() as captured_embedding_records:
            result = pipeline.run(context)
            embedding_records = list(captured_embedding_records)
    finally:
        if previous_model is None:
            os.environ.pop("LOLLA_OPENROUTER_MODEL", None)
        else:
            os.environ["LOLLA_OPENROUTER_MODEL"] = previous_model

    audit = result.audit
    boundary_calls = _boundary_dicts(audit.boundary_calls)
    usage_summary = build_usage_summary(
        run_id=f"lane1diag_{arm_id}",
        pipeline_boundary_calls=boundary_calls,
        embedding_records=embedding_records,
    )
    boundary_status_counts = dict(Counter(str(call.get("status", "")) for call in boundary_calls))
    deep_results = [_jsonable(item) for item in audit.deep_check_results]
    detected = [item for item in deep_results if item.get("detected") is True]
    rejected = [item for item in deep_results if item.get("detected") is not True]
    triage_scores = [_jsonable(item) for item in audit.triage_scores]
    triggered = [_jsonable(item) for item in audit.triggered_tendencies]
    pass1_nominations = [score for score in triage_scores if int(score.get("score", 0) or 0) >= 4]

    record = {
        "schema_version": "lane1_model_diagnostic.v1",
        "arm_id": arm_id,
        "description": description,
        "run_dir": str(run_dir),
        "requested_model": requested_model,
        "pre_step6_mode_label": pre_step6_mode,
        "pre_step6_note": (
            "Lane-1-only diagnostic: pre-Step-6 table rendering is intentionally "
            "not executed because it happens after Lane 1 in the live pipeline."
        ),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "summary": {
            "pass1_score_count": len(triage_scores),
            "pass1_nomination_count": len(pass1_nominations),
            "triggered_count": len(triggered),
            "triggered_sources": dict(Counter(str(item.get("source", "")) for item in triggered)),
            "pass2_checked_count": len(deep_results),
            "pass2_detected_count": len(detected),
            "pass2_rejected_count": len(rejected),
            "delta_findings_count": len(result.delta_card.findings if result.delta_card else ()),
            "detected_tendencies": list(result.detected_tendencies),
            "selected_model_ids": list(result.delta_card.selected_model_ids if result.delta_card else ()),
            "cost_estimate_state": usage_summary.get("cost_estimate_state"),
            "estimated_total_cost_usd": usage_summary.get("estimated_total_cost_usd"),
            "boundary_status_counts": boundary_status_counts,
            "non_ok_boundary_count": sum(
                count for status, count in boundary_status_counts.items() if status != "ok"
            ),
            "model_attribution": (
                usage_summary.get("vendors", {})
                .get("openrouter", {})
                .get("model_attribution", {})
            ),
            "models_seen": usage_summary.get("vendors", {}).get("openrouter", {}).get("models_seen", []),
            "requested_models_seen": usage_summary.get("vendors", {}).get("openrouter", {}).get("requested_models_seen", []),
        },
        "pass1_nominations": pass1_nominations,
        "triggered_tendencies": triggered,
        "pass2_detected": detected,
        "pass2_rejections": [
            {
                "tendency_id": item.get("tendency_id"),
                "tendency_name": item.get("tendency_name"),
                "reason": item.get("reason"),
                "confidence": item.get("confidence"),
            }
            for item in rejected
        ],
        "triage_scores": triage_scores,
        "deep_check_results": deep_results,
        "boundary_calls": boundary_calls,
        "embedding_records": embedding_records,
        "usage_summary": usage_summary,
    }
    (output_dir / f"{arm_id}.lane1-diagnostic.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return record


def _interpret(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {record["arm_id"]: record for record in records}

    def detected_count(arm_id: str) -> int:
        return int(by_id[arm_id]["summary"]["pass2_detected_count"])

    def triggered_count(arm_id: str) -> int:
        return int(by_id[arm_id]["summary"]["triggered_count"])

    old_detected = detected_count("A_old_deepseek_off")
    new_off_detected = detected_count("B_new_deepseek_off")
    new_private_detected = detected_count("C_new_deepseek_step6_private")
    grok_private_detected = detected_count("D_new_grok43_step6_private")
    invalid_arms = [
        arm_id
        for arm_id, record in by_id.items()
        if int(record["summary"].get("non_ok_boundary_count", 0) or 0) > 0
    ]

    findings: list[str] = []
    if invalid_arms:
        findings.append("boundary_errors_observed:" + ",".join(sorted(invalid_arms)))

    if old_detected > 0:
        findings.append("lane1_working_on_historical_founder_under_deepseek")
    elif triggered_count("A_old_deepseek_off") > 0:
        findings.append("historical_founder_pass1_triggers_but_pass2_rejects_all")
    else:
        findings.append("historical_founder_no_pass1_trigger_under_deepseek")

    if old_detected > 0 and new_off_detected == 0:
        findings.append("current_conversation_effect_plausible")
    elif new_off_detected > 0:
        findings.append("current_conversation_still_fires_under_deepseek")

    if new_off_detected != new_private_detected:
        findings.append("pre_step6_flag_sensitivity_observed")
    else:
        findings.append("no_pre_step6_flag_sensitivity_observed")

    if new_private_detected != grok_private_detected:
        findings.append("model_effect_observed_between_deepseek_and_grok43")
    else:
        findings.append("no_model_effect_observed_between_deepseek_and_grok43")

    if grok_private_detected == 0 and triggered_count("D_new_grok43_step6_private") > 0:
        findings.append("grok43_pass2_rejection_pattern_observed")

    complete_records = [
        record for record in records if int(record["summary"].get("non_ok_boundary_count", 0) or 0) == 0
    ]
    if complete_records and all(
        int(record["summary"]["pass2_detected_count"]) == 0
        and int(record["summary"]["triggered_count"]) > 0
        for record in complete_records
    ):
        findings.append("pass2_rejection_pattern_across_complete_arms")

    return {
        "schema_version": "lane1_model_diagnostic_readout.v1",
        "thresholds": {
            "lane1_working": "pass1 triggers >=1 and pass2 detects >=1 on historical founder",
            "pass2_too_strict": "pass1 triggers >=1 and pass2 detects 0, with rejection reasons preserved",
            "pre_step6_sensitivity": "same conversation/model differs between off and step6_private labels",
            "model_effect": "same conversation/pre-step6 label differs between DeepSeek and Grok 4.3",
        },
        "arm_summaries": {record["arm_id"]: record["summary"] for record in records},
        "findings": findings,
        "decision": (
            "rerun_incomplete_arms"
            if invalid_arms
            else (
                "lane1_pass2_rejection_review_before_process_hardening"
                if "pass2_rejection_pattern_across_complete_arms" in findings
                else "interpret_before_process_hardening"
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-run-dir", type=Path, default=DEFAULT_OLD_RUN)
    parser.add_argument("--new-run-dir", type=Path, default=DEFAULT_NEW_RUN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--deepseek-model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--grok-model", default="x-ai/grok-4.3")
    args = parser.parse_args()

    _load_default_env()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = {
        "schema_version": "lane1_model_diagnostic_contract.v1",
        "purpose": (
            "Attribute Lane 1 zero-findings on the May 22 Marcus live run to "
            "conversation change, model behavior, Pass 2 strictness, or "
            "pre-Step-6 wiring sensitivity."
        ),
        "arms": [
            "A_old_deepseek_off: historical founder conversation, DeepSeek, pre-Step-6 off",
            "B_new_deepseek_off: May 22 founder conversation, DeepSeek, pre-Step-6 off",
            "C_new_deepseek_step6_private: May 22 founder conversation, DeepSeek, pre-Step-6 label on",
            "D_new_grok43_step6_private: May 22 founder conversation, Grok 4.3, pre-Step-6 label on",
        ],
        "non_purpose": (
            "This is not a full product-quality comparison and does not test "
            "cached Bevelin/Polya portfolio cards."
        ),
    }
    (args.output_dir / "lane1-model-diagnostic-contract.v1.json").write_text(
        json.dumps(contract, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    arms = [
        (
            "A_old_deepseek_off",
            "Historical founder run, new production default model, pre-Step-6 off.",
            args.old_run_dir,
            args.deepseek_model,
            "off",
        ),
        (
            "B_new_deepseek_off",
            "May 22 founder run, new production default model, pre-Step-6 off.",
            args.new_run_dir,
            args.deepseek_model,
            "off",
        ),
        (
            "C_new_deepseek_step6_private",
            "May 22 founder run, new production default model, pre-Step-6 private-table label.",
            args.new_run_dir,
            args.deepseek_model,
            "step6_private",
        ),
        (
            "D_new_grok43_step6_private",
            "May 22 founder run, Grok 4.3 comparison arm, pre-Step-6 private-table label.",
            args.new_run_dir,
            args.grok_model,
            "step6_private",
        ),
    ]
    records = []
    for arm_id, description, run_dir, model, mode in arms:
        print(f"running {arm_id} model={model} mode={mode}", flush=True)
        records.append(
            _run_arm(
                arm_id=arm_id,
                description=description,
                run_dir=run_dir,
                requested_model=model,
                pre_step6_mode=mode,
                output_dir=args.output_dir,
            )
        )

    result = _interpret(records)
    (args.output_dir / "lane1-model-diagnostic-result.v1.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result["arm_summaries"], indent=2, ensure_ascii=False))
    print("decision:", result["decision"])
    print("output:", args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

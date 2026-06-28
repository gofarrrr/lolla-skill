from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.agent_result import write_agent_result
from engine.system_b.capture_adequacy import CAPTURE_ADEQUACY_SCHEMA_VERSION
from engine.system_b.evaluation import (
    EVALUATION_SCHEMA_VERSION,
    build_evaluation,
)
from engine.system_b.extraction_adequacy_report import (
    EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION,
    write_extraction_adequacy_report,
)
from engine.system_b.provider_boundary_health import build_provider_boundary_health
from engine.system_b.reasoning_trace import write_reasoning_trace


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _base_health(
    *,
    overall: str = "healthy",
    product_output_health: str = "clean",
    live_output_health: str = "clean",
) -> dict:
    health = {
        "overall": overall,
        "product_output_health": product_output_health,
        "live_output_health": live_output_health,
        "issues": [],
        "issue_details": [],
    }
    health["provider_boundary_health"] = build_provider_boundary_health(health)
    return health


def _provider_boundary_health(*, status: str) -> dict:
    health = {
        "overall": "partial",
        "product_output_health": "clean",
        "live_output_health": "not_checked",
        "issues": ["vendor_boundary_reasoning_leak"],
        "issue_details": [
            {
                "code": "vendor_boundary_reasoning_leak",
                "severity": "partial",
                "axis": "vendor_boundary",
                "leak_count": 1,
                "models": ["google/gemini-3.1-flash-lite-20260507"],
                "stages": ["extraction"],
            }
        ],
        "partial_health_causes": ["vendor_boundary_reasoning_leak"],
        "boundary_reasoning_leak_detected": True,
        "boundary_reasoning_leak_count": 1,
        "boundary_reasoning_leak_models": ["google/gemini-3.1-flash-lite-20260507"],
        "boundary_reasoning_leak_stages": ["extraction"],
    }
    health["provider_boundary_health"] = build_provider_boundary_health(health)
    if status == "warning_unknown_persistence":
        health["product_output_health"] = "unknown"
        health["provider_boundary_health"] = build_provider_boundary_health(health)
    return health


def _seed_run(
    tmp_path: Path,
    *,
    run_id: str = "evalrun",
    case_id: str = "eval-case",
    health: dict | None = None,
    include_optional_graph: bool = True,
    include_extraction_adequacy_report: bool = True,
    risk_mode: str = "standard",
    capture_adequacy: dict | None = None,
) -> Path:
    run_dir = tmp_path / case_id / run_id
    run_dir.mkdir(parents=True)
    health = health or _base_health()
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_health": "good",
            "capture_adequacy": capture_adequacy
            or {
                "schema_version": CAPTURE_ADEQUACY_SCHEMA_VERSION,
                "run_id": run_id,
                "status": "good",
                "capture_strategy": "full",
                "declared_turn_count": 2,
                "captured_turn_count": 2,
                "omitted_turn_count": 0,
                "captured_windows": [
                    {
                        "label": "full",
                        "start_turn": 1,
                        "end_turn": 2,
                        "turn_count": 2,
                    }
                ],
                "omitted_windows": [],
                "risk_flags": [],
                "notes": [],
            },
            "extraction": {
                "decision_situation": "Founder deciding whether to pivot",
                "reasoning_passages": ["Only pivot after a customer evidence gate."],
            },
        },
    )
    (run_dir / "conversation.txt").write_text(
        "CONVERSATION\n\n[Turn 1] USER:\nShould we pivot?\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "risk_mode": risk_mode,
            "run_health": health,
            "revised_answer": "Only pivot after a customer evidence gate.",
            "usage_summary": {"estimated_total_cost_usd": 0.01},
        },
    )
    (run_dir / "revised.txt").write_text(
        "Only pivot after a customer evidence gate.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Memo\n", encoding="utf-8")
    _write_json(
        run_dir / "run_events.json",
        {"schema_version": "lolla.run_events.v0.1", "run_id": run_id, "events": []},
    )
    if include_optional_graph:
        _write_json(
            run_dir / "graph_survival_report.json",
            {"schema_version": "lolla.graph_survival_report.v0.1"},
        )
        (run_dir / "graph_survival_report.md").write_text(
            "# Graph Survival\n",
            encoding="utf-8",
        )

    write_agent_result(run_dir, run_id=run_id, case_id=case_id)
    if include_extraction_adequacy_report:
        write_extraction_adequacy_report(run_dir, run_id=run_id, case_id=case_id)
    files_for_trace = [
        "conversation.txt",
        "extraction.json",
        "result.json",
        "revised.txt",
        "memo.md",
        "run_events.json",
        "agent_result.json",
    ]
    if include_extraction_adequacy_report:
        files_for_trace.append("extraction_adequacy_report.json")
    if include_optional_graph:
        files_for_trace.extend(["graph_survival_report.json", "graph_survival_report.md"])
    write_reasoning_trace(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        fingerprint="founder deciding whether to pivot",
        how_matched="new_case",
        files_copied=files_for_trace,
        files_missing=[],
        manifest={"run_count": 1},
    )
    return run_dir


def _check(evaluation: dict, check_id: str) -> dict:
    for check in evaluation["checks"]:
        if check["id"] == check_id:
            return check
    raise AssertionError(f"missing check {check_id}")


def test_healthy_archive_evaluation_passes(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["schema_version"] == EVALUATION_SCHEMA_VERSION
    assert evaluation["overall"] == "pass"
    assert evaluation["caller_readiness"] == "ready"
    assert _check(evaluation, "reasoning_trace_indexes_agent_result")["status"] == "pass"
    assert _check(evaluation, "extraction_adequacy_report_schema_version")[
        "status"
    ] == "pass"
    assert _check(evaluation, "extraction_adequacy_status")["status"] == "pass"
    assert evaluation["scope"] == {
        "artifact": "run_readiness",
        "advice_quality_scored": False,
        "model_calls": 0,
        "llm_judge_used": False,
    }


def test_contained_provider_boundary_warning_is_not_green(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        health=_provider_boundary_health(status="warning_contained"),
    )

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "warn"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "provider_boundary_policy")["status"] == "warn"
    assert _check(evaluation, "provider_boundary_contained_policy")["status"] == "pass"


def test_contained_provider_boundary_with_other_degraded_cause_stays_conservative(
    tmp_path: Path,
) -> None:
    health = _provider_boundary_health(status="warning_contained")
    health["overall"] = "degraded"
    health["issues"].append("no_fingerprint")
    health["issue_details"].append(
        {
            "code": "no_fingerprint",
            "severity": "degraded",
            "axis": "case_memory",
        }
    )
    health["provider_boundary_health"] = build_provider_boundary_health(health)
    run_dir = _seed_run(tmp_path, health=health)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")
    agent_result = json.loads((run_dir / "agent_result.json").read_text(encoding="utf-8"))

    assert agent_result["status"] == "degraded"
    assert agent_result["status_reason"] == "run_health.overall is degraded"
    assert agent_result["caller_action"] == "do_not_use_run_degraded"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "provider_boundary_policy")["status"] == "warn"
    assert _check(evaluation, "provider_boundary_contained_policy")["status"] == "pass"


def test_product_output_unsafe_is_blocking(tmp_path: Path) -> None:
    health = _base_health(overall="degraded", product_output_health="unsafe")
    run_dir = _seed_run(tmp_path, health=health)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "product_output_health")["severity"] == "blocking"


def test_high_stakes_clean_run_requires_user_first(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path, risk_mode="high_stakes")

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "pass"
    assert evaluation["caller_readiness"] == "inspect_first"
    assert _check(evaluation, "high_stakes_clean_policy")["status"] == "pass"


def test_high_stakes_clean_run_surfaces_reliance_caveat_without_approval(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path, risk_mode="high_stakes")

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")
    caveat = _check(evaluation, "risk_mode_reliance_policy")
    serialized = json.dumps(evaluation).lower()

    assert caveat["status"] == "pass"
    assert caveat["severity"] == "info"
    caveat_message = caveat["message"].lower()
    assert "high-stakes mode keeps reliance conservative" in caveat_message
    assert "ask_user_first" in caveat_message
    assert "authorize action" in caveat_message
    assert evaluation["caller_readiness"] == "inspect_first"
    assert evaluation["scope"]["advice_quality_scored"] is False
    assert evaluation["scope"]["llm_judge_used"] is False
    for forbidden in ("approved", "certified", "cleared", "domain authority"):
        assert forbidden not in serialized


def test_standard_clean_run_has_no_high_stakes_reliance_caveat(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path, risk_mode="standard")

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "pass"
    assert evaluation["caller_readiness"] == "ready"
    assert not any(
        check["id"] == "risk_mode_reliance_policy"
        for check in evaluation["checks"]
    )


def test_degraded_high_stakes_reliance_caveat_preserves_do_not_use(
    tmp_path: Path,
) -> None:
    health = _base_health(overall="degraded")
    run_dir = _seed_run(tmp_path, health=health, risk_mode="high_stakes")

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")
    caveat = _check(evaluation, "risk_mode_reliance_policy")

    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "non_ok_status_conservative")["status"] == "pass"
    assert caveat["status"] == "pass"
    assert "does not override degraded or incomplete run state" in caveat["message"]
    assert "do_not_use_run_degraded" in caveat["message"]


def test_degraded_standard_run_stays_conservative_without_high_stakes_caveat(
    tmp_path: Path,
) -> None:
    health = _base_health(overall="degraded")
    run_dir = _seed_run(tmp_path, health=health, risk_mode="standard")

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "non_ok_status_conservative")["status"] == "pass"
    assert not any(
        check["id"] == "risk_mode_reliance_policy"
        for check in evaluation["checks"]
    )


def test_live_output_unsafe_is_blocking(tmp_path: Path) -> None:
    health = _base_health(overall="degraded", live_output_health="unsafe")
    run_dir = _seed_run(tmp_path, health=health)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "live_output_health")["severity"] == "blocking"


def test_live_output_not_checked_warns(tmp_path: Path) -> None:
    health = _base_health(live_output_health="not_checked")
    run_dir = _seed_run(tmp_path, health=health)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "warn"
    assert evaluation["caller_readiness"] == "inspect_first"
    assert _check(evaluation, "live_output_health")["status"] == "warn"


def test_capture_adequacy_warning_warns_without_blocking(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        capture_adequacy={
            "schema_version": CAPTURE_ADEQUACY_SCHEMA_VERSION,
            "status": "warn",
            "capture_strategy": "first_n_plus_last_n",
            "declared_turn_count": 30,
            "captured_turn_count": 18,
            "omitted_turn_count": 12,
            "captured_windows": [],
            "omitted_windows": [{"start_turn": 4, "end_turn": 15, "turn_count": 12}],
            "risk_flags": ["middle_turns_omitted"],
            "notes": ["Middle turns were omitted."],
        },
    )

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "warn"
    assert evaluation["caller_readiness"] == "inspect_first"
    assert _check(evaluation, "capture_adequacy_status")["status"] == "warn"


def test_capture_adequacy_critical_is_blocking(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        capture_adequacy={
            "schema_version": CAPTURE_ADEQUACY_SCHEMA_VERSION,
            "status": "critical",
            "capture_strategy": "unknown",
            "declared_turn_count": 2,
            "captured_turn_count": 0,
            "omitted_turn_count": 2,
            "captured_windows": [],
            "omitted_windows": [{"start_turn": 1, "end_turn": 2, "turn_count": 2}],
            "risk_flags": ["zero_user_turns_captured"],
            "notes": ["No user turns were captured."],
        },
    )

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "capture_adequacy_status")["severity"] == "blocking"


def test_missing_capture_adequacy_warns_for_older_archives(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction.pop("capture_adequacy")
    _write_json(run_dir / "extraction.json", extraction)
    write_reasoning_trace(
        run_dir,
        run_id="evalrun",
        case_id="eval-case",
        fingerprint="founder deciding whether to pivot",
        how_matched="new_case",
        files_copied=[
            "conversation.txt",
            "extraction.json",
            "result.json",
            "revised.txt",
            "memo.md",
            "run_events.json",
            "agent_result.json",
            "extraction_adequacy_report.json",
            "graph_survival_report.json",
            "graph_survival_report.md",
        ],
        files_missing=[],
        manifest={"run_count": 1},
    )

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "warn"
    assert _check(evaluation, "capture_adequacy_schema_version")["status"] == "warn"
    assert _check(evaluation, "capture_adequacy_status")["status"] == "warn"


def test_missing_extraction_adequacy_report_warns_for_older_archives(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path, include_extraction_adequacy_report=False)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "warn"
    assert _check(evaluation, "extraction_adequacy_report_schema_version")[
        "status"
    ] == "warn"
    assert _check(evaluation, "extraction_adequacy_status")["status"] == "warn"


def test_extraction_adequacy_critical_is_blocking(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    report = json.loads(
        (run_dir / "extraction_adequacy_report.json").read_text(encoding="utf-8")
    )
    report["adequacy_status"] = "critical"
    _write_json(run_dir / "extraction_adequacy_report.json", report)

    write_reasoning_trace(
        run_dir,
        run_id="evalrun",
        case_id="eval-case",
        fingerprint="founder deciding whether to pivot",
        how_matched="new_case",
        files_copied=[
            "conversation.txt",
            "extraction.json",
            "result.json",
            "revised.txt",
            "memo.md",
            "run_events.json",
            "agent_result.json",
            "extraction_adequacy_report.json",
            "graph_survival_report.json",
            "graph_survival_report.md",
        ],
        files_missing=[],
        manifest={"run_count": 1},
    )

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "extraction_adequacy_status")["severity"] == "blocking"


def test_wrong_extraction_adequacy_report_schema_is_blocking(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    report = json.loads(
        (run_dir / "extraction_adequacy_report.json").read_text(encoding="utf-8")
    )
    assert report["schema_version"] == EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION
    report["schema_version"] = "wrong.schema"
    _write_json(run_dir / "extraction_adequacy_report.json", report)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert _check(evaluation, "extraction_adequacy_report_schema_version")[
        "status"
    ] == "fail"


def test_missing_required_artifact_is_blocking(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    (run_dir / "memo.md").unlink()

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert _check(evaluation, "artifact_required_memo_md")["status"] == "fail"
    assert _check(evaluation, "reasoning_trace_records_missing_required_artifacts")[
        "status"
    ] == "fail"


def test_missing_optional_artifact_warns_only(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path, include_optional_graph=False)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "warn"
    assert evaluation["caller_readiness"] == "inspect_first"
    assert _check(evaluation, "artifact_optional_graph_survival_report_json")[
        "status"
    ] == "warn"


def test_wrong_agent_result_schema_is_blocking(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    agent_result = json.loads((run_dir / "agent_result.json").read_text(encoding="utf-8"))
    agent_result["schema_version"] = "wrong.schema"
    _write_json(run_dir / "agent_result.json", agent_result)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert _check(evaluation, "agent_result_schema_version")["status"] == "fail"


def test_warning_unknown_provider_boundary_persistence_is_blocking(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        health=_provider_boundary_health(status="warning_unknown_persistence"),
    )

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")

    assert evaluation["overall"] == "fail"
    assert _check(evaluation, "provider_boundary_policy")["status"] == "fail"


def test_evaluation_does_not_include_raw_model_content_or_reasoning_details(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    raw_message_key = "raw_" + "message_content"
    result["audit_summary"] = {
        "boundary_calls": [
            {
                raw_message_key: "secret raw model content marker",
                "reasoning": "secret raw reasoning details marker",
                "reasoning_details": "another raw reasoning marker",
            }
        ]
    }
    _write_json(run_dir / "result.json", result)

    evaluation = build_evaluation(run_dir, run_id="evalrun", case_id="eval-case")
    serialized = json.dumps(evaluation)

    assert "secret raw model content marker" not in serialized
    assert "secret raw reasoning details marker" not in serialized
    assert "another raw reasoning marker" not in serialized
    assert raw_message_key not in serialized
    assert "reasoning_details\"" not in serialized

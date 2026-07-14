from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.agent_result import build_agent_result, write_agent_result
from engine.system_b.capture_adequacy import CAPTURE_ADEQUACY_SCHEMA_VERSION
from engine.system_b.evaluation import build_evaluation, write_evaluation
from engine.system_b.extraction_adequacy_report import write_extraction_adequacy_report
from engine.system_b.provider_boundary_health import build_provider_boundary_health
from engine.system_b.reasoning_trace import write_reasoning_trace
from engine.system_b.review_corpus import build_review_corpus_records


REPO_ROOT = Path(__file__).resolve().parents[1]
RISK_FIXTURE_MATRIX = REPO_ROOT / "docs" / "evals" / "risk-mode-fixture-matrix-v0.json"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _health(
    *,
    overall: str = "healthy",
    product_output_health: str = "clean",
    live_output_health: str = "clean",
    issues: list[str] | None = None,
    issue_details: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "overall": overall,
        "product_output_health": product_output_health,
        "live_output_health": live_output_health,
        "issues": issues or [],
        "issue_details": issue_details or [],
    }
    payload["provider_boundary_health"] = build_provider_boundary_health(payload)
    return payload


def _capture_adequacy(run_id: str) -> dict[str, Any]:
    return {
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
    }


def _seed_run(
    root: Path,
    *,
    case_id: str = "risk-contract-case",
    run_id: str = "20260628T120000Z_risk40",
    risk_mode: str = "standard",
    health: dict[str, Any] | None = None,
    write_eval: bool = True,
) -> Path:
    run_dir = root / case_id / run_id
    run_dir.mkdir(parents=True)
    health = health or _health()
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_adequacy": _capture_adequacy(run_id),
            "extraction": {
                "decision_situation": "Whether to proceed with a high-impact operating change",
                "reasoning_passages": ["Proceed only after the review gate is complete."],
            },
        },
    )
    (run_dir / "conversation.txt").write_text(
        "[Turn 1] USER:\nShould we proceed?\n\n"
        "[Turn 2] ASSISTANT:\nProceed only after a review gate.\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "risk_mode": risk_mode,
            "run_health": health,
            "revised_answer": "Proceed only after the review gate is complete.",
            "usage_summary": {
                "estimated_total_cost_usd": 0.01,
                "cost_estimate_state": "complete",
                "pricing_table_version": "2026-06-28",
            },
        },
    )
    (run_dir / "revised.txt").write_text(
        "Proceed only after the review gate is complete.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Memo\n\nReview gate first.\n", encoding="utf-8")
    _write_json(
        run_dir / "run_events.json",
        {"schema_version": "lolla.run_events.v0.1", "run_id": run_id, "events": []},
    )
    _write_json(
        run_dir / "graph_survival_report.json",
        {"schema_version": "lolla.graph_survival_report.v0.1"},
    )
    (run_dir / "graph_survival_report.md").write_text("# Graph\n", encoding="utf-8")

    write_agent_result(run_dir, run_id=run_id, case_id=case_id)
    write_extraction_adequacy_report(run_dir, run_id=run_id, case_id=case_id)
    _write_trace(run_dir, run_id=run_id, case_id=case_id, include_evaluation=False)
    if write_eval:
        write_evaluation(run_dir, run_id=run_id, case_id=case_id)
        _write_trace(run_dir, run_id=run_id, case_id=case_id, include_evaluation=True)
    return run_dir


def _write_trace(
    run_dir: Path,
    *,
    run_id: str,
    case_id: str,
    include_evaluation: bool,
) -> None:
    files = [
        "conversation.txt",
        "extraction.json",
        "result.json",
        "revised.txt",
        "memo.md",
        "run_events.json",
        "graph_survival_report.json",
        "graph_survival_report.md",
        "agent_result.json",
        "extraction_adequacy_report.json",
    ]
    if include_evaluation:
        files.append("evaluation.json")
    write_reasoning_trace(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        fingerprint="high impact operating change",
        how_matched="new_case",
        files_copied=files,
        files_missing=[],
        manifest={"run_count": 1},
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _check(evaluation: dict[str, Any], check_id: str) -> dict[str, Any]:
    for check in evaluation["checks"]:
        if check["id"] == check_id:
            return check
    raise AssertionError(f"missing evaluation check {check_id}")


def test_high_stakes_clean_not_checked_stays_conservative(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        risk_mode="high_stakes",
        health=_health(live_output_health="not_checked"),
    )

    agent_result = build_agent_result(
        run_dir,
        run_id="20260628T120000Z_risk40",
        case_id="risk-contract-case",
    )
    evaluation = build_evaluation(
        run_dir,
        run_id="20260628T120000Z_risk40",
        case_id="risk-contract-case",
    )

    assert agent_result["risk_mode"] == "high_stakes"
    assert agent_result["status"] == "ok"
    assert agent_result["caller_action"] == "ask_user_first"
    assert agent_result["caller_action"] != "use_revised_answer"
    assert agent_result["live_output_health"] == "not_checked"
    assert evaluation["overall"] == "warn"
    assert evaluation["caller_readiness"] == "inspect_first"
    assert _check(evaluation, "high_stakes_clean_policy")["status"] == "pass"
    assert _check(evaluation, "live_output_health")["status"] == "warn"
    assert evaluation["scope"]["advice_quality_scored"] is False
    assert evaluation["scope"]["llm_judge_used"] is False


def test_high_stakes_trusted_live_clean_still_asks_user_first(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        risk_mode="high_stakes",
        health=_health(live_output_health="clean"),
    )

    agent_result = _read_json(run_dir / "agent_result.json")
    evaluation = _read_json(run_dir / "evaluation.json")

    assert agent_result["risk_mode"] == "high_stakes"
    assert agent_result["live_output_health"] == "clean"
    assert agent_result["caller_action"] == "ask_user_first"
    assert evaluation["overall"] == "pass"
    assert evaluation["caller_readiness"] == "inspect_first"
    assert _check(evaluation, "high_stakes_clean_policy")["status"] == "pass"
    assert _check(evaluation, "live_output_health")["status"] == "pass"


def test_standard_clean_behavior_remains_ready_to_use_revised_answer(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(
        tmp_path,
        risk_mode="standard",
        health=_health(live_output_health="clean"),
    )

    agent_result = _read_json(run_dir / "agent_result.json")
    evaluation = _read_json(run_dir / "evaluation.json")

    assert agent_result["risk_mode"] == "standard"
    assert agent_result["status"] == "ok"
    assert agent_result["caller_action"] == "review_revised_answer"
    assert evaluation["overall"] == "pass"
    assert evaluation["caller_readiness"] == "ready"
    assert not any(
        check["id"] == "high_stakes_clean_policy"
        for check in evaluation["checks"]
    )


def test_degraded_run_dominates_high_stakes_risk_mode(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        risk_mode="high_stakes",
        health=_health(
            overall="degraded",
            live_output_health="clean",
            issues=["artifact_custody_failure"],
            issue_details=[
                {
                    "code": "artifact_custody_failure",
                    "severity": "degraded",
                    "axis": "artifact_custody",
                }
            ],
        ),
    )

    agent_result = _read_json(run_dir / "agent_result.json")
    evaluation = _read_json(run_dir / "evaluation.json")

    assert agent_result["risk_mode"] == "high_stakes"
    assert agent_result["status"] == "degraded"
    assert agent_result["caller_action"] == "do_not_use_run_degraded"
    assert agent_result["caller_action"] != "ask_user_first"
    assert evaluation["caller_readiness"] == "do_not_use"
    assert _check(evaluation, "non_ok_status_conservative")["status"] == "pass"
    assert not any(
        check["id"] == "high_stakes_clean_policy"
        for check in evaluation["checks"]
    )


def test_high_stakes_contract_wording_stays_approval_neutral(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        risk_mode="high_stakes",
        health=_health(live_output_health="clean"),
    )

    serialized = json.dumps(_read_json(run_dir / "agent_result.json")).lower()

    for forbidden in ("approved", "certified", "cleared", "domain authority"):
        assert forbidden not in serialized


def test_review_corpus_preserves_high_stakes_reliance_metadata(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        risk_mode="high_stakes",
        health=_health(live_output_health="not_checked"),
    )

    records = build_review_corpus_records(archive_root)

    assert len(records) == 1
    record = records[0]
    assert record["risk_mode"] == "high_stakes"
    assert record["agent_result"]["caller_action"] == "ask_user_first"
    assert record["evaluation"]["caller_readiness"] == "inspect_first"
    assert record["run_health"]["live_output_health"] == "not_checked"
    assert record["scope"]["raw_transcript_included"] is False
    assert record["scope"]["raw_memo_included"] is False
    assert record["scope"]["raw_revised_answer_included"] is False
    assert record["scope"]["llm_judge_used"] is False


def test_risk_mode_fixture_matrix_core_expectations_match_locked_contract() -> None:
    matrix = _read_json(RISK_FIXTURE_MATRIX)
    fixtures = {item["fixture_id"]: item for item in matrix["fixtures"]}

    assert matrix["canonical_risk_modes"] == [
        "quick",
        "standard",
        "deep",
        "high_stakes",
        "stability",
    ]
    assert (
        fixtures["risk_high_stakes_clean_not_checked_v0"]["caller_action_expected"]
        == "conservative stance; current contract uses ask_user_first for otherwise clean high_stakes runs"
    )
    assert (
        fixtures["risk_high_stakes_clean_trusted_live_v0"]["caller_action_expected"]
        == "conservative stance remains; current high_stakes behavior is ask_user_first, not automatic use"
    )
    assert (
        fixtures["risk_high_stakes_artifact_degraded_v0"]["caller_action_expected"]
        == "do_not_use_run_degraded or equivalent existing conservative policy"
    )
    assert (
        fixtures["risk_high_stakes_unsupported_claim_v0"]["primary_failure_mode_expected"]
        == "unsupported_new_claim"
    )
    assert (
        fixtures["risk_high_stakes_values_conflict_unresolved_v0"]["safe_for_agent_use_expected"]
        == "with_human_review or no; never automatic yes"
    )
    assert (
        fixtures["risk_standard_clean_not_checked_v0"]["caller_action_expected"]
        == "existing policy only; clean standard run may be use_revised_answer, but that is not human approval"
    )
    assert (
        fixtures["risk_quick_thin_scope_declared_v0"]["invalid_behavior"]
        == "using quick mode to produce broad confident advice or bypass custody expectations"
    )
    assert (
        fixtures["risk_stability_archive_consistency_v0"]["invalid_behavior"]
        == "treating repeated-run agreement as proof that the answer is correct"
    )
    assert (
        fixtures["risk_deep_intent_not_automatic_v0"]["caller_action_expected"]
        == "no automatic rerun_deeper or automatic use from the mode label alone"
    )

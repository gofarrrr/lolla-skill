from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from engine.system_b.product_delta_readiness import (
    PRODUCT_DELTA_READINESS_SCHEMA_VERSION,
    build_product_delta_readiness_report,
    render_product_delta_readiness_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_case(
    *,
    case_id: str = "sample-case",
    run_id: str = "20260629T000000Z_sample",
    summary_status: str = "available",
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": f"{case_id}/{run_id}",
        "vanilla_baseline_status": "actual_strong_model_conversation_in_archive",
        "review_safe_summary_status": summary_status,
        "review_safe_sources": ["docs/evals/human-review-corpus-batch-v0.md"],
    }


def _seed_cases(cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": "lolla.product_delta_seed_cases.v0",
        "source_artifacts": ["docs/evals/human-review-corpus-batch-v0.md"],
        "cases": cases,
    }


def _run_dir(
    archive_root: Path,
    *,
    case_id: str = "sample-case",
    run_id: str = "20260629T000000Z_sample",
    degraded: bool = False,
    omit: set[str] | None = None,
) -> Path:
    omit = omit or set()
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    raw_artifacts = {
        "conversation.txt": "RAW CONVERSATION DO NOT READ",
        "revised.txt": "RAW REVISED ANSWER DO NOT READ",
        "memo.md": "RAW MEMO DO NOT READ",
    }
    for artifact, text in raw_artifacts.items():
        if artifact not in omit:
            (run_dir / artifact).write_text(text, encoding="utf-8")
    if "evaluation.json" not in omit:
        _write_json(
            run_dir / "evaluation.json",
            {
                "schema_version": "lolla.evaluation.v0",
                "overall": "fail" if degraded else "warn",
                "caller_readiness": "do_not_use" if degraded else "inspect_first",
            },
        )
    if "agent_result.json" not in omit:
        _write_json(
            run_dir / "agent_result.json",
            {
                "schema_version": "lolla_agent_result.v1",
                "case_id": case_id,
                "run_id": run_id,
                "caller_action": "do_not_use_run_degraded" if degraded else "use_revised_answer",
                "changed_advice_summary": [
                    "DO NOT COPY SEMANTIC SUMMARY INTO READINESS OUTPUT"
                ],
            },
        )
    if "reasoning_trace.json" not in omit:
        _write_json(
            run_dir / "reasoning_trace.json",
            {
                "schema_version": "lolla.reasoning_trace.v0.2",
                "case": {
                    "case_id": case_id,
                    "run_id": run_id,
                },
            },
        )
    if "extraction_adequacy_report.json" not in omit:
        _write_json(
            run_dir / "extraction_adequacy_report.json",
            {
                "schema_version": "lolla.extraction_adequacy_report.v0",
                "status": "good",
            },
        )
    return run_dir


def test_ready_case_gets_shell_without_semantic_judgment(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root)

    report = build_product_delta_readiness_report(
        seed_cases=_seed_cases([_seed_case()]),
        archive_root=archive_root,
    )

    assert report["schema_version"] == PRODUCT_DELTA_READINESS_SCHEMA_VERSION
    assert report["aggregate"]["ready_for_codex_provisional_review"] == 1
    case = report["cases"][0]
    assert case["readiness_state"] == "ready_for_codex_provisional_review"
    assert case["ready_for_later_human_review"] is True
    assert case["weakening_reasons"] == [
        "evaluation_overall_warn",
        "caller_readiness_inspect_first",
    ]
    shell = report["provisional_review_shells"][0]
    assert shell["schema_version"] == "lolla.vanilla_vs_lolla_provisional_review.v0"
    assert shell["human_validated"] is False
    assert shell["ground_truth"] is False
    assert shell["judge_calibration_eligible"] is False
    assert shell["model_calls"] == 0
    assert shell["archive_mutated"] is False
    assert shell["vanilla_likely_next_action"]["status"] == "not_reviewed"
    assert shell["net_decision_read_provisional"]["label"] == "inconclusive"


def test_degraded_case_is_readiness_blocked(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root, degraded=True)

    report = build_product_delta_readiness_report(
        seed_cases=_seed_cases([_seed_case()]),
        archive_root=archive_root,
    )

    assert report["cases"][0]["readiness_state"] == "degraded_run_health"
    assert report["cases"][0]["blocking_reasons"] == [
        "degraded_or_excluded_run_health"
    ]
    assert report["provisional_review_shells"][0]["first_upstream_failure"]["surface"] == "artifact_custody"


def test_missing_revised_answer_is_reported(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root, omit={"revised.txt"})

    report = build_product_delta_readiness_report(
        seed_cases=_seed_cases([_seed_case()]),
        archive_root=archive_root,
    )

    assert report["cases"][0]["readiness_state"] == "missing_revised_answer"
    assert "revised_answer_missing" in report["cases"][0]["blocking_reasons"]


def test_missing_safe_summary_is_reported(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root)

    report = build_product_delta_readiness_report(
        seed_cases=_seed_cases([_seed_case(summary_status="missing")]),
        archive_root=archive_root,
    )

    assert report["cases"][0]["readiness_state"] == "missing_review_safe_summary"


def test_missing_structured_json_with_raw_artifacts_is_private_content_only(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root, omit={"evaluation.json", "agent_result.json"})

    report = build_product_delta_readiness_report(
        seed_cases=_seed_cases([_seed_case()]),
        archive_root=archive_root,
    )

    assert report["cases"][0]["readiness_state"] == "blocked_private_content_only"
    assert "missing_or_malformed:evaluation.json" in report["cases"][0]["blocking_reasons"]


def test_outputs_do_not_read_or_copy_raw_content_or_paths(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root)

    original_read_text = Path.read_text

    def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path.name in {"conversation.txt", "revised.txt", "memo.md"}:
            raise AssertionError(f"raw artifact was read: {path.name}")
        return original_read_text(path, *args, **kwargs)

    with patch.object(Path, "read_text", guarded_read_text):
        report = build_product_delta_readiness_report(
            seed_cases=_seed_cases(
                [
                    {
                        **_seed_case(),
                        "ignored_private_note": "/Users/example SECRET client_secret api_key password",
                    }
                ]
            ),
            archive_root=archive_root,
        )

    rendered = render_product_delta_readiness_json(report)
    for forbidden in (
        "RAW CONVERSATION",
        "RAW REVISED ANSWER",
        "RAW MEMO",
        "DO NOT COPY SEMANTIC SUMMARY",
        "/Users/",
        "SECRET",
        "client_secret",
        "api_key",
        "password",
    ):
        assert forbidden not in rendered


def test_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _run_dir(archive_root)
    case_list = tmp_path / "cases.json"
    json_out = tmp_path / "review.json"
    md_out = tmp_path / "report.md"
    case_list.write_text(json.dumps(_seed_cases([_seed_case()])), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_provisional_review.py",
            "--case-list",
            str(case_list),
            "--archive-root",
            str(archive_root),
            "--out",
            str(md_out),
            "--json-out",
            str(json_out),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    markdown = md_out.read_text(encoding="utf-8")
    assert payload["aggregate"]["ready_for_codex_provisional_review"] == 1
    assert "ready_for_codex_provisional_review" in markdown


def test_cli_reports_sanitized_invalid_case_list_error(tmp_path: Path) -> None:
    case_list = tmp_path / "bad.json"
    case_list.write_text("{not-json", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_provisional_review.py",
            "--case-list",
            str(case_list),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() == "error: case list is not valid JSON"
    assert str(tmp_path) not in result.stderr

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths
from engine.system_b.product_delta_specialist_packets import (
    PRODUCT_DELTA_SPECIALIST_PACKETS_SCHEMA_VERSION,
    SPECIALIST_ROLES,
    build_product_delta_specialist_packets,
    load_json_object,
    render_product_delta_specialist_packets_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_LIST = REPO_ROOT / "docs/evals/product-delta-seed-cases-v0.json"
PROVISIONAL_REVIEW = (
    REPO_ROOT / "reviews/codex-assisted/product-delta-provisional-run-v0/review.json"
)
CODEX_BATCH = REPO_ROOT / "reviews/codex-assisted/product-delta-batch-v0/review.json"
DOC_PATH = REPO_ROOT / "docs/evals/product-delta-specialist-packet-builder-v0.md"
CONTRACT_DOC = REPO_ROOT / "docs/evals/product-delta-specialist-review-contracts-v0.md"
CONTRACT_SCHEMA = REPO_ROOT / "docs/evals/product-delta-specialist-review-contracts-v0.json"
FIXTURE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/product-delta-specialist-packets-v0/packets.json"
)


def _build_report(*, limit: int | None = 2, case_ids: list[str] | None = None) -> dict[str, Any]:
    return build_product_delta_specialist_packets(
        seed_cases=load_json_object(CASE_LIST),
        provisional_review=load_json_object(PROVISIONAL_REVIEW),
        codex_batch=load_json_object(CODEX_BATCH),
        case_list_relpath="docs/evals/product-delta-seed-cases-v0.json",
        provisional_review_relpath=(
            "reviews/codex-assisted/product-delta-provisional-run-v0/review.json"
        ),
        codex_batch_relpath=(
            "reviews/codex-assisted/product-delta-batch-v0/review.json"
        ),
        limit=limit,
        case_ids=case_ids,
    )


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _walk_paths(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    paths = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            paths.extend(_walk_paths(child, (*path, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_walk_paths(child, (*path, str(index))))
    return paths


def test_packet_builder_generates_checked_in_safe_packets() -> None:
    report = _build_report(limit=2)

    assert report["schema_version"] == PRODUCT_DELTA_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert report["generated_by"] == "product_delta_specialist_packets"
    assert report["mode"] == "checked_in_safe_mode"
    assert report["case_count"] == 2
    assert len(report["cases"]) == 2
    assert report["packet_policy"]["specialist_reads_filled"] is False


def test_boundary_metadata_is_conservative() -> None:
    boundary = _build_report(limit=1)["boundary"]

    assert boundary["human_validated"] is False
    assert boundary["ground_truth"] is False
    assert boundary["judge_calibration_eligible"] is False
    assert boundary["product_proof"] is False
    assert boundary["answer_quality_scored"] is False
    assert boundary["agent_action_authorized"] is False
    assert boundary["model_calls"] == 0
    assert boundary["archive_mutated"] is False
    assert boundary["runtime_invoked"] is False
    assert boundary["skill_invoked"] is False


def test_no_forbidden_authority_field_names_in_packet_output() -> None:
    report = _build_report(limit=2)
    keys = _walk_keys(report)
    forbidden = {
        "safe_for_agent_use",
        "quality_score",
        "answer_quality_score",
        "improvement_score",
        "judge_score",
        "winner",
        "approved",
        "certified",
        "pass_fail",
    }

    assert not (forbidden & keys)
    assert '"safe_for_agent_use"' not in render_product_delta_specialist_packets_json(report)


def test_each_ready_case_gets_all_specialist_role_packets() -> None:
    report = _build_report(limit=4)

    ready_cases = [
        case
        for case in report["cases"]
        if case["readiness_status"] == "ready_for_codex_provisional_review"
    ]
    assert ready_cases
    for case in ready_cases:
        assert set(case["packets"]) == set(SPECIALIST_ROLES)
        for role, packet in case["packets"].items():
            assert packet["specialist_role"] == role
            assert packet["expected_output_contract"]["filled_by_packet_builder"] is False
            assert packet["expected_output_contract"]["must_be_filled_by_future_specialist"] is True


def test_packets_do_not_fill_specialist_result_fields() -> None:
    report = _build_report(limit=2)
    result_like_keys = {
        "net_decision_read_candidate",
        "overall_interpretation_adequacy",
        "action_changed",
    }

    for path, value in _walk_paths(report):
        if not path:
            continue
        if path[-1] not in result_like_keys:
            continue
        assert "expected_output_contract" in path, path
        assert isinstance(value, list) or isinstance(value, str)
    assert "lolla_worse_candidate" not in render_product_delta_specialist_packets_json(report)


def test_packets_preserve_known_limits_for_thin_or_blocked_cases() -> None:
    report = _build_report(limit=None)

    blocked_cases = [
        case
        for case in report["cases"]
        if case["readiness_status"] != "ready_for_codex_provisional_review"
    ]
    assert blocked_cases
    for case in blocked_cases:
        assert any(
            item.startswith("readiness_status:")
            or item.startswith("blocking:")
            or item == "prior_provisional_broad_read_missing"
            for item in case["missing_or_thin_context"]
        )
        for packet in case["packets"].values():
            assert packet["known_limits"]


def test_generated_packet_json_has_no_privacy_markers() -> None:
    rendered = render_product_delta_specialist_packets_json(_build_report(limit=None))

    for marker in (
        "/Users/",
        "SECRET",
        "raw_message_content",
        "fabricated_passages",
        "FULL ASSISTANT REASONING",
        "client_secret",
        "api_key",
        "password",
    ):
        assert marker not in rendered


def test_cli_writes_json_and_supports_limit_and_case_filter(tmp_path: Path) -> None:
    out = tmp_path / "packets.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_specialist_packets.py",
            "--case-list",
            str(CASE_LIST),
            "--provisional-review",
            str(PROVISIONAL_REVIEW),
            "--codex-batch",
            str(CODEX_BATCH),
            "--limit",
            "2",
            "--case-id",
            "ceo-remove-founding-cofounder",
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == PRODUCT_DELTA_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert payload["case_count"] == 1
    assert payload["cases"][0]["case_id"] == "ceo-remove-founding-cofounder"


def test_pr78_lint_passes_generated_packets_and_docs(tmp_path: Path) -> None:
    out = tmp_path / "packets.json"
    out.write_text(
        render_product_delta_specialist_packets_json(_build_report(limit=2)),
        encoding="utf-8",
    )

    report = lint_product_delta_paths([out, DOC_PATH, CONTRACT_DOC, CONTRACT_SCHEMA])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_fixture_is_small_and_safe() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture["schema_version"] == PRODUCT_DELTA_SPECIALIST_PACKETS_SCHEMA_VERSION
    assert fixture["case_count"] == 2
    assert len(fixture["cases"]) == 2
    assert fixture["packet_policy"]["specialist_reads_filled"] is False
    assert set(fixture["cases"][0]["packets"]) == set(SPECIALIST_ROLES)
    rendered = json.dumps(fixture, sort_keys=True)
    assert "/Users/" not in rendered
    assert "raw_message_content" not in rendered
